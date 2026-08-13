#!/usr/bin/env python3
"""Discover GitHub repositories relevant to your research topic.

Reads GitHub search queries from ``config/taxonomy.yaml`` under the
``github_queries`` key.  Each query can optionally specify a category,
subcategory hint, and a minimum-stars override.  Repos are written to
``repos.yaml`` (sibling to ``papers.yaml``) in the same taxonomy.

GitHub queries use the standard search syntax:
  https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories

Requirements:
  - ``gh`` CLI installed and authenticated (``gh auth status``)
  - ``pip install pyyaml``

Usage:
    # Preview (dry-run)
    python3 scripts/fetch/fetch_github_repos.py --dry-run

    # Full run
    python3 scripts/fetch/fetch_github_repos.py --min-stars 100

    # Subset of queries
    python3 scripts/fetch/fetch_github_repos.py --from 5 --to 10

    # Tune pagination
    python3 scripts/fetch/fetch_github_repos.py --max-pages 2 --sleep 5

Output: repos.yaml in the repo root.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Allow imports from scripts/ (sibling directory)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

import research_config

BASE = Path(__file__).resolve().parent.parent.parent
REPOS_YAML = BASE / "repos.yaml"


# ── Config loading ────────────────────────────────────────────────────────

def load_github_queries(cfg):
    """Load github_queries from taxonomy.yaml.

    Each entry must have at least ``query`` (GitHub search string).
    Optional keys: ``category``, ``subcategory_hint``, ``min_stars``.

    If no ``github_queries`` are defined, returns an empty list with a
    helpful message.
    """
    raw = cfg.get("github_queries", [])
    if not raw:
        return []
    queries = []
    for item in raw:
        q = item.get("query", "")
        if not q:
            continue
        queries.append({
            "query": q,
            "category": item.get("category", ""),
            "subcategory_hint": item.get("subcategory_hint", ""),
            "min_stars": item.get("min_stars"),
        })
    return queries


def load_topic_signals(cfg):
    """Extract relevance signals from the topic config.

    Builds a set of normalized keyword tokens from:
      1. topic.name and topic.short
      2. category/subcategory IDs
      3. Optional ``github_signals`` list in taxonomy.yaml

    These are used to gate out irrelevant repos from broad GitHub searches.
    """
    tokens = set()

    # From topic metadata
    topic = cfg.get("topic", {})
    for key in ("name", "short", "description"):
        val = topic.get(key, "")
        if val:
            tokens.update(_tokenize(val))

    # From taxonomy IDs
    for cat in cfg.get("taxonomy", {}).get("categories", []):
        tokens.add(cat.get("id", "").lower())
    for sub in cfg.get("taxonomy", {}).get("subcategories", []):
        tokens.add(sub.get("id", "").lower())

    # Explicit signal list (optional)
    explicit = cfg.get("github_signals", [])
    for sig in explicit:
        tokens.update(_tokenize(sig))

    # Filter out generic/broad tokens
    skip = {
        "research", "corpus", "study", "review", "analysis", "paper", "approach",
        "system", "method", "model", "based", "using", "data", "framework",
        "novel", "proposed", "new", "survey", "topic", "skeleton",
    }
    return sorted(t for t in tokens if len(t) >= 3 and t not in skip)


# ── Text helpers ─────────────────────────────────────────────────────────

def _norm(text):
    """Lowercase and collapse whitespace/hyphens/slashes."""
    return re.sub(r"[\s\-/]+", " ", text.lower())


def _tokenize(text):
    """Split text into individual normalized tokens."""
    return _norm(text).split()


def _word_re(tokens):
    """Build a regex that matches tokens at word boundaries.

    Multi-word tokens (containing spaces) match with a leading ``\\b`` only,
    following the _word_re fix: ``re.escape`` in Python 3.11+ escapes internal
    spaces, so we escape each word individually and join with a literal space.
    No trailing ``\\b`` for multi-word tokens to allow plural/fuzzy matches
    (e.g. "supply chains" matches "supply chain").
    """
    parts = []
    for t in tokens:
        words = _norm(t).split(" ")
        escaped = [re.escape(w) for w in words]
        if len(escaped) == 1:
            parts.append(r"\b" + escaped[0] + r"\b")
        else:
            parts.append(r"\b" + " ".join(escaped))
    return re.compile(r"|".join(parts), re.I)


# ── Subcategory classification ────────────────────────────────────────────

DEFAULT_SUBCATEGORY_RULES = [
    ("review", ["survey", "benchmark", "comparison", "awesome", "collection",
                "curated", "list", "catalogue", "directory"], True),
    ("theory", ["framework", "specification", "standard", "rfc", "architecture",
                "model", "ontology", "taxonomy"], False),
    ("application", ["cli", "tool", "scanner", "analyzer", "detector", "checker",
                     "linter", "parser", "processor", "converter", "engine"], False),
    ("development", ["sdk", "library", "api", "client", "wrapper", "binding",
                      "plugin", "extension", "module", "package"], False),
    ("method", ["template", "boilerplate", "starter", "example", "demo",
                "playground", "tutorial", "cookbook", "guide", "examples"], False),
    ("systems", ["platform", "orchestrator", "operator", "controller", "runtime",
                 "daemon", "service", "server", "broker", "gateway"], False),
    ("evaluation", ["benchmark", "test-suite", "testbed", "evaluation",
                    "metrics", "dataset", "corpus", "baseline"], False),
]
SUBCATEGORY_FALLBACK = "application"


def classify_subcategory(name, description, topics, cfg):
    """Assign subcategory from repo metadata + taxonomy config.

    First tries to match against config-derived rules, then falls back to
    keyword heuristics from the repo's name/description/topics.
    """
    text = f"{name} {description} {' '.join(topics)}".lower()
    name_lower = name.lower()

    # Try matching subcategory IDs directly in the repo text
    for sub in cfg.get("taxonomy", {}).get("subcategories", []):
        sub_id = sub.get("id", "")
        if sub_id and sub_id in text:
            return sub_id

    # Heuristic rules
    for subcat, keywords, title_only in DEFAULT_SUBCATEGORY_RULES:
        haystack = name_lower if title_only else text
        for kw in keywords:
            if kw in haystack:
                return subcat

    return SUBCATEGORY_FALLBACK


# ── GitHub API helpers ────────────────────────────────────────────────────

def gh_search_repos(query, sort="stars", order="desc", per_page=30, page=1):
    """Search GitHub repos via ``gh api``. Returns (items, total_count)."""
    cmd = [
        "gh", "api", "--method", "GET",
        f"search/repositories?q={query}&sort={sort}&order={order}"
        f"&per_page={per_page}&page={page}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            err = result.stderr.strip()
            if "422" in err or "rate limit" in err.lower():
                return [], 0
            if "could not resolve host" in err.lower():
                print(f"  WARNING: network error — skipping query", flush=True)
                return [], 0
            print(f"  WARNING: gh api error: {err[:120]}", flush=True)
            return [], 0
        data = json.loads(result.stdout)
        return data.get("items", []), data.get("total_count", 0)
    except subprocess.TimeoutExpired:
        print("  WARNING: gh api timeout (30s)", flush=True)
        return [], 0
    except json.JSONDecodeError:
        return [], 0


def to_entry(item, category, subcategory_hint, cfg):
    """Map a GitHub search result to a repos.yaml entry."""
    name = item.get("full_name", "")
    desc = (item.get("description") or "")[:200]
    topics = item.get("topics", [])

    # Determine category: prefer subcategory_hint, fall back to query category
    subcat = subcategory_hint or classify_subcategory(name, desc, topics, cfg)

    return {
        "name": name,
        "url": item.get("html_url", ""),
        "description": desc,
        "category": category or "method",
        "subcategory": subcat,
        "stars": item.get("stargazers_count", 0),
        "forks": item.get("forks_count", 0),
        "language": item.get("language") or "",
        "topics": sorted(topics),
        "pushed_at": item.get("pushed_at", "")[:10],
        "created_at": item.get("created_at", "")[:10],
        "open_issues": item.get("open_issues_count", 0),
        "license": (item.get("license") or {}).get("spdx_id", ""),
    }


# ── Relevance check ───────────────────────────────────────────────────────

def is_relevant_repo(name, description, topics, signal_re):
    """Gate out repos that have nothing to do with the research topic.

    Uses a pre-compiled regex from ``load_topic_signals()`` to require at least
    one topic signal in the repo's name, description, or topics.
    """
    if signal_re.pattern == r"\b\b":  # empty pattern (no signals defined)
        return True  # pass everything when no signals configured
    text = _norm(f"{name} {description} {' '.join(topics)}")
    return bool(signal_re.search(text))


# ── YAML I/O ─────────────────────────────────────────────────────────────

def _yaml_str(s):
    """Escape a string for a double-quoted YAML scalar."""
    if not s:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def format_yaml_entry(entry):
    """Format a single repo entry as YAML lines."""
    lines = [f'  - name: "{_yaml_str(entry["name"])}"']
    lines.append(f'    url: {entry["url"]}')
    if entry.get("description"):
        lines.append(f'    description: "{_yaml_str(entry["description"])}"')
    lines.append(f'    category: {entry["category"]}')
    lines.append(f'    subcategory: {entry["subcategory"]}')
    lines.append(f'    stars: {entry["stars"]}')
    lines.append(f'    forks: {entry["forks"]}')
    if entry.get("language"):
        lines.append(f'    language: {entry["language"]}')
    if entry.get("topics"):
        lines.append(f'    topics:')
        for t in entry["topics"]:
            lines.append(f'      - {_yaml_str(t)}')
    if entry.get("pushed_at"):
        lines.append(f'    pushed_at: "{entry["pushed_at"]}"')
    if entry.get("created_at"):
        lines.append(f'    created_at: "{entry["created_at"]}"')
    if entry.get("open_issues"):
        lines.append(f'    open_issues: {entry["open_issues"]}')
    if entry.get("license") and entry["license"] not in ("NOASSERTION", ""):
        lines.append(f'    license: {entry["license"]}')
    return "\n".join(lines)


def load_existing_repos(path):
    """Load repos.yaml, return (names_set, entries_count)."""
    if not path.exists():
        return set(), 0
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    repos = data.get("repos", [])
    names = {r.get("name", "").lower().strip() for r in repos}
    return names, len(repos)


def append_repos(path, entries, topic_short="research"):
    """Append entries to repos.yaml, creating the file if needed."""
    lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.rstrip("\n").split("\n")
        if lines == ["repos:"]:
            lines = ["repos:"]
        else:
            lines.append("")
    else:
        lines = [
            f"# GitHub repositories relevant to {topic_short} research.",
            "# Generated by scripts/fetch/fetch_github_repos.py",
            f"# Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "",
            "repos:",
        ]

    for entry in entries:
        lines.append(format_yaml_entry(entry))

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Discover GitHub repos relevant to your research topic."
    )
    parser.add_argument("--min-stars", type=int, default=50,
                        help="Default minimum star threshold (default: 50)")
    parser.add_argument("--per-page", type=int, default=30,
                        help="Results per GitHub query page (max 100)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing files")
    parser.add_argument("--sleep", type=float, default=3.0,
                        help="Seconds between queries (default: 3)")
    parser.add_argument("--max-pages", type=int, default=3,
                        help="Max pages per query (default: 3 = 90 repos/query)")
    parser.add_argument("--from", dest="from_idx", type=int, default=0,
                        help="Start at query index (0-based)")
    parser.add_argument("--to", dest="to_idx", type=int, default=None,
                        help="Stop at query index (inclusive)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path (default: repos.yaml in repo root)")
    args = parser.parse_args()

    cfg = research_config.load_config()
    queries = load_github_queries(cfg)

    if not queries:
        topic_name = cfg.get("topic", {}).get("name", "your topic")
        print(f"ERROR: No github_queries defined in config/taxonomy.yaml.", file=sys.stderr)
        print(f"Add a ``github_queries`` section, e.g.:", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"github_queries:", file=sys.stderr)
        print(f'  - query: "topic:{_norm(topic_name).replace(" ", "-")}+stars:>50"', file=sys.stderr)
        print(f'    category: method', file=sys.stderr)
        print(f'  - query: "YOUR KEYWORD+tool+stars:>100"', file=sys.stderr)
        print(f'    category: application', file=sys.stderr)
        print(f'  - query: "YOUR KEYWORD+framework+stars:>200"', file=sys.stderr)
        print(f'    category: method', file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"See: https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories",
              file=sys.stderr)
        sys.exit(1)

    # Build relevance filter
    signals = load_topic_signals(cfg)
    signal_re = _word_re(signals) if signals else re.compile(r"(?!)")
    print(f"Relevance signals: {len(signals)} tokens", flush=True)

    output_path = Path(args.output) if args.output else REPOS_YAML
    topic_short = cfg.get("topic", {}).get("short", "research")

    to_idx = args.to_idx if args.to_idx is not None else len(queries) - 1
    active = queries[args.from_idx:to_idx + 1]

    existing_names, existing_count = load_existing_repos(output_path)
    print(f"Loaded {existing_count} existing repos from {output_path.name}", flush=True)
    print(f"Running {len(active)}/{len(queries)} queries (min-stars {args.min-stars})...", flush=True)

    all_new = []
    total_results = 0
    filtered_out = 0

    for qi, qinfo in enumerate(active, start=args.from_idx):
        query_raw = qinfo["query"]
        cat = qinfo.get("category", "")
        hint = qinfo.get("subcategory_hint", "")
        q_min_stars = qinfo.get("min_stars", args.min_stars)

        # Inject star threshold if the query doesn't already have one
        if "stars:" not in query_raw:
            query = f"{query_raw}+stars:>{q_min_stars}"
        else:
            # Replace existing stars:>N if user's min is higher
            query = re.sub(r'stars:>\d+', f'stars:>{q_min_stars}', query_raw)

        label = f"[{cat}]" if cat else f"[q{qi}]"
        print(f"\nQuery {qi + 1}/{len(queries)} {label} {query[:90]}", flush=True)

        for page in range(1, args.max_pages + 1):
            items, total = gh_search_repos(query, per_page=args.per_page, page=page)
            if qi == args.from_idx and page == 1:
                total_results += total
                print(f"  {total} total results", flush=True)

            if not items:
                break

            page_new = 0
            for item in items:
                name = item.get("full_name", "")
                if name.lower().strip() in existing_names:
                    continue

                desc = item.get("description") or ""
                topics = item.get("topics", [])

                # Relevance gate
                if not is_relevant_repo(name, desc, topics, signal_re):
                    filtered_out += 1
                    continue

                existing_names.add(name.lower().strip())
                entry = to_entry(item, cat, hint, cfg)
                all_new.append(entry)
                page_new += 1

            print(f"  page {page}: {len(items)} results, {page_new} new, "
                  f"{len(items) - page_new} dup/filtered", flush=True)

            if len(items) < args.per_page:
                break

        time.sleep(args.sleep)

    print(f"\n{'='*60}", flush=True)
    print(f"Total search results scanned: {total_results}", flush=True)
    print(f"Filtered out (irrelevant): {filtered_out}", flush=True)
    print(f"New relevant repos: {len(all_new)}", flush=True)

    if not all_new:
        print("No new repos to add.", flush=True)
        return

    if args.dry_run:
        print(f"\n--- Candidate repos (first 20) ---", flush=True)
        for e in sorted(all_new, key=lambda x: x["stars"], reverse=True)[:20]:
            print(f"  [{e['category']}/{e['subcategory']}] "
                  f"⭐{e['stars']:>5} {e['name']}", flush=True)
            if e.get("description"):
                print(f"    {e['description'][:100]}", flush=True)
        remaining = max(0, len(all_new) - 20)
        if remaining:
            print(f"... and {remaining} more", flush=True)
        print("\nDry run complete — no files modified.", flush=True)
        return

    append_repos(output_path, all_new, topic_short)
    print(f"\nAppended {len(all_new)} repos to {output_path.name}", flush=True)

    cats = Counter(e["category"] for e in all_new)
    langs = Counter(e["language"] for e in all_new if e["language"])
    total_stars = sum(e["stars"] for e in all_new)

    print("\nCategory breakdown:", flush=True)
    for c, count in cats.most_common():
        print(f"  {c:20} {count:4}", flush=True)

    print("\nTop languages:", flush=True)
    for lang, count in langs.most_common(5):
        print(f"  {lang:15} {count:4}", flush=True)

    print(f"\nTotal new stars: {total_stars:,}", flush=True)


if __name__ == "__main__":
    main()
