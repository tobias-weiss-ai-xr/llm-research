#!/usr/bin/env python3
"""Saturate papers.yaml by searching arXiv comprehensively.

Builds diverse queries by expanding the base arxiv_queries from
config/taxonomy.yaml across cs.AI, cs.CL, cs.LG, cs.RO within a 48-month
window. Auto-classifies, deduplicates, and loops until saturation (<5 new).
Saves after each round to survive timeouts.
"""

import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import yaml

import research_config

ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5})")
ARXIV_SEARCH_API = (
    "https://export.arxiv.org/api/query?search_query={}&start={}&max_results={}"
)
API_DELAY = 3
SATURATION_THRESHOLD = 5
MAX_RESULTS_PER_QUERY = 100
MONTHS_BACK = 48
MAX_ROUNDS = 3

def get_queries(cfg):
    base = cfg.get("arxiv_queries", [])
    cats = ["cs.AI", "cs.CL", "cs.LG", "cs.RO"]
    out = []
    for q in base:
        m = re.match(r'cat:([\w.]+) AND (.+)', q)
        if m:
            clause = m.group(2)
            for c in cats:
                out.append(f'cat:{c} AND {clause}')
        else:
            out.append(q)
    return out or [f'cat:cs.AI AND abs:"{cfg.get("topic", {}).get("short", "research")}"']


def load_existing_papers(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    papers = data.get("papers", [])
    by_id = {}
    titles_lower = []
    for p in papers:
        url = p.get("url", "")
        match = ARXIV_ID_PATTERN.search(url)
        if match:
            by_id[match.group(1)] = p
        titles_lower.append(p.get("title", "").lower().strip())
    return data, papers, by_id, titles_lower


def title_similarity(a, b):
    a_clean = re.sub(r"[^\w\s]", "", a.lower())
    b_clean = re.sub(r"[^\w\s]", "", b.lower())
    return SequenceMatcher(None, a_clean, b_clean).ratio()


def search_arxiv(query, months_back):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff = now - timedelta(days=months_back * 30)
    date_start = cutoff.strftime("%Y%m%d0000")
    date_end = now.strftime("%Y%m%d") + "2359"

    full_query = f"({query}) AND submittedDate:[{date_start} TO {date_end}]"
    try:
        resp = requests.get(
            ARXIV_SEARCH_API.format(
                requests.utils.quote(full_query), 0, MAX_RESULTS_PER_QUERY
            ),
            timeout=30,
        )
        resp.raise_for_status()
        entries = []
        root = resp.text
        for match in re.finditer(r"<entry>(.*?)</entry>", root, re.DOTALL):
            entry_xml = match.group(1)
            entry = {}
            title_m = re.search(r"<title>(.*?)</title>", entry_xml, re.DOTALL)
            if title_m:
                entry["title"] = re.sub(r"\s+", " ", title_m.group(1).strip())
            id_m = re.search(r"<id>(.*?)</id>", entry_xml)
            if id_m:
                entry["url"] = id_m.group(1).strip().replace("http://", "https://")
            published_m = re.search(r"<published>(.*?)</published>", entry_xml)
            if published_m:
                entry["date"] = published_m.group(1).strip()[:7]
            summary_m = re.search(r"<summary>(.*?)</summary>", entry_xml, re.DOTALL)
            if summary_m:
                entry["abstract"] = re.sub(r"\s+", " ", summary_m.group(1).strip())
            if entry.get("title") and entry.get("url"):
                entries.append(entry)
        return entries
    except Exception as e:
        print(f"  WARNING: arXiv search error: {e}", flush=True)
        return []


AGENT_KEYWORDS = [
    "agent",
    "agents",
    "llm",
    "language model",
    "autonomous",
    "embodied",
    "robot",
    "assistant",
    "chatbot",
    "dialogue system",
    "conversational",
]

MEMORY_KEYWORDS_AGENT_MEMORY = [
    "agent memory",
    "llm memory",
    "memory-augmented agent",
    "memory augmented agent",
    "agent memor",
    "long-term memory",
    "episodic memory",
    "semantic memory",
    "working memory",
    "experience replay",
    "memory bank",
    "memory store",
    "memory system",
    "memory architecture",
    "memory management",
    "memory-augmented",
    "memory retrieval",
    "memory update",
    "memory consolidation",
    "memory hierarchy",
    "memory pruning",
    "memory evolution",
    "memory retention",
    "context compression",
    "context management",
    "knowledge retention",
    "reflexion",
    "reflective memory",
    "generative agent",
    "memory module",
    "structured memory",
    "memory write",
    "memory read",
    "latent memory",
    "memory personalization",
    "reflective memory",
    "memory benchmark",
    "conversation memory",
    "chat memory",
    "dialogue memory",
    "cognitive memory",
    "memgpt",
    "mem0",
    "letta",
    "memory wire",
    "memory protocol",
    "memory governance",
    "memory ontology",
    "memory constitution",
    "memory lifecycle",
]

EXPERIENTIAL_KEYWORDS = [
    "episodic",
    "experiential",
    "experience",
    "narrative memory",
    "event-based",
    "interaction history",
    "conversation history",
    "dialogue history",
    "trajectory",
    "reflect",
    "reflection",
    "self-reflection",
    "reflexion",
]

WORKING_KEYWORDS = [
    "working memory",
    "short-term",
    "context management",
    "kv cache",
    "kv-cache",
    "cache memory",
    "attention memory",
    "streaming",
    "prompt caching",
    "inference-time",
]

PARAMETRIC_KEYWORDS = [
    "parametric",
    "parameter",
    "weight update",
    "model update",
    "fine-tun",
    "finetun",
    "gradient",
    "continual learning",
    "lifelong learning",
    "continual pretrain",
]

LATENT_KEYWORDS = [
    "latent",
    "latent memory",
    "latent space",
    "embedding",
    "vector store",
    "vector database",
    "knowledge graph",
    "latent representation",
    "implicit memory",
    "representation learning",
]


def is_relevant(title, abstract):
    text = f"{title} {abstract}".lower()

    has_agent = any(k in text for k in AGENT_KEYWORDS)
    has_specific_memory = any(k in text for k in MEMORY_KEYWORDS_AGENT_MEMORY)

    if has_agent and has_specific_memory:
        return True

    if has_agent:
        memory_generic = any(
            k in text
            for k in [
                "memory",
                "memorization",
                "forgetting",
                "recall",
                "retrieval",
                "retriev",
                "remember",
                "context window",
                "knowledge graph",
                "cache",
            ]
        )
        if memory_generic:
            agent_terms = any(
                k in text
                for k in [
                    "agent",
                    "agents",
                    "llm",
                    "autonomous agent",
                    "language model",
                    "embodied agent",
                    "conversational",
                    "dialogue",
                    "assistant",
                    "multi-agent",
                ]
            )
            if agent_terms:
                return True

    return False


def classify_paper(title, abstract):
    text = f"{title} {abstract}".lower()

    is_exp = any(k in text for k in EXPERIENTIAL_KEYWORDS)
    is_work = any(k in text for k in WORKING_KEYWORDS)

    if is_work and not is_exp:
        category = "working"
    elif is_exp:
        category = "experiential"
    else:
        category = "factual"

    is_param = any(k in text for k in PARAMETRIC_KEYWORDS)
    is_lat = any(k in text for k in LATENT_KEYWORDS)
    is_tok = any(
        k in text
        for k in [
            "token",
            "text retrieval",
            "retrieval",
            "store",
            "database",
            "key-value",
            "symbolic",
            "explicit",
            "rag",
            "retrieve",
            "index",
            "knowledge base",
        ]
    )

    if is_param and not is_lat and not is_tok:
        subcategory = "parametric"
    elif is_lat and not is_tok:
        subcategory = "latent"
    else:
        subcategory = "token-level"

    return category, subcategory


def dedup_title(title, titles_lower, threshold=0.75):
    title_clean = title.lower().strip()
    for existing in titles_lower:
        if title_similarity(title_clean, existing) >= threshold:
            return True
    return False


def save_papers(yaml_path, data, papers):
    data["papers"] = papers
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def run_round(yaml_path, data, papers, by_id, titles_lower, queries, round_num):
    print(f"\n{'=' * 60}", flush=True)
    print(f"ROUND {round_num}", flush=True)
    print(f"{'=' * 60}", flush=True)

    round_new = []
    seen_ids = set()
    seen_titles = set(titles_lower)

    for qi, query in enumerate(queries):
        cat_match = re.search(r"cat:(\S+)", query)
        cat = cat_match.group(1) if cat_match else "?"
        print(
            f"\n  Query {qi + 1}/{len(queries)} [{cat}]...",
            flush=True,
        )

        entries = search_arxiv(query, MONTHS_BACK)
        print(f"    arXiv returned {len(entries)} entries", flush=True)

        for entry in entries:
            arxiv_id_match = ARXIV_ID_PATTERN.search(entry.get("url", ""))
            arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else None

            if arxiv_id and arxiv_id in by_id:
                continue

            if arxiv_id and arxiv_id in seen_ids:
                continue

            title = entry.get("title", "")
            title_lower = title.lower().strip()

            if title_lower in seen_titles:
                continue

            if dedup_title(title, titles_lower):
                continue

            abstract = entry.get("abstract", "")

            if not is_relevant(title, abstract):
                continue

            category, subcategory = classify_paper(title, abstract)

            new_paper = {
                "title": title,
                "date": entry.get("date", ""),
                "url": entry.get("url", ""),
                "category": category,
                "subcategory": subcategory,
                "authors": [],
                "venue": "",
                "code_url": "",
                "project_url": "",
                "abstract": abstract,
                "tags": [f"auto-{category}", f"auto-{subcategory}"],
            }

            if arxiv_id:
                seen_ids.add(arxiv_id)
            seen_titles.add(title_lower)
            titles_lower.append(title_lower)
            round_new.append(new_paper)
            by_id[arxiv_id] = new_paper

            print(
                f"    NEW [{category}/{subcategory}] {title[:70]}",
                flush=True,
            )

        time.sleep(API_DELAY)

        if (qi + 1) % 20 == 0:
            save_papers(yaml_path, data, papers + round_new)
            print(
                f"    [checkpoint] saved {len(papers) + len(round_new)} papers",
                flush=True,
            )

    print(f"\n  Round {round_num} found {len(round_new)} new papers", flush=True)
    return round_new


def main():
    cfg = research_config.load_config()
    queries = get_queries(cfg)

    yaml_path = Path(__file__).resolve().parent.parent.parent / "papers.yaml"
    data, papers, by_id, titles_lower = load_existing_papers(yaml_path)

    print(f"Loaded {len(papers)} existing papers", flush=True)
    print(f"Using {len(queries)} queries (expanded from config/taxonomy.yaml)", flush=True)
    print(f"Search window: {MONTHS_BACK} months", flush=True)

    total_new = 0
    round_num = 1

    while round_num <= MAX_ROUNDS:
        round_new = run_round(
            yaml_path, data, papers, by_id, titles_lower, queries, round_num
        )

        papers.extend(round_new)
        total_new += len(round_new)

        save_papers(yaml_path, data, papers)
        print(f"  Saved {len(papers)} total papers to {yaml_path}", flush=True)

        if len(round_new) < SATURATION_THRESHOLD:
            print(
                f"\nSATURATED: Round {round_num} found only {len(round_new)} "
                f"new papers (< {SATURATION_THRESHOLD} threshold)",
                flush=True,
            )
            break

        print(
            f"\n  Total new so far: {total_new}, starting round {round_num + 1}...",
            flush=True,
        )
        round_num += 1

    if round_num > MAX_ROUNDS:
        print(
            f"\nReached max rounds ({MAX_ROUNDS}). Stopping.",
            flush=True,
        )

    if total_new == 0:
        print("\nNo new papers found. papers.yaml unchanged.", flush=True)

    cat_counter = Counter()
    sub_counter = Counter()
    for p in papers:
        cat_counter[p.get("category", "unknown")] += 1
        sub_counter[p.get("subcategory", "unknown")] += 1

    print(f"\n{'=' * 60}", flush=True)
    print("FINAL DISTRIBUTION", flush=True)
    print(f"{'=' * 60}", flush=True)
    print(f"Total papers: {len(papers)}", flush=True)
    print(f"New papers added: {total_new}", flush=True)
    print(f"Rounds: {round_num}", flush=True)
    print(f"\nBy category:", flush=True)
    for cat in ["factual", "experiential", "working"]:
        print(f"  {cat}: {cat_counter.get(cat, 0)}", flush=True)
    print(f"\nBy subcategory:", flush=True)
    for sub in ["token-level", "parametric", "latent"]:
        print(f"  {sub}: {sub_counter.get(sub, 0)}", flush=True)


if __name__ == "__main__":
    main()
