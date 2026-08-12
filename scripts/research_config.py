#!/usr/bin/env python3
"""Shared config loader for the *-research skeleton.

Reads config/taxonomy.yaml and exposes:
  - topic metadata (name, short, description)
  - categories / subcategories with display names
  - arxiv_queries, other_sources_queries, openalex_queries

All scripts use this module, so the taxonomy lives in ONE place.
"""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent


def load_config(path=None):
    path = path or (REPO / "config" / "taxonomy.yaml")
    if not path.exists():
        # Fallback: minimal default taxonomy (keeps scripts runnable out-of-the-box)
        return {
            "topic": {"name": "Research Corpus", "short": "research"},
            "taxonomy": {
                "categories": [{"id": "method", "display": "Methods"}],
                "subcategories": [{"id": "core", "display": "Core"}],
            },
            "arxiv_queries": [],
            "other_sources_queries": [],
            "openalex_queries": [],
        }
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_topic(cfg):
    return cfg.get("topic", {})


def get_categories(cfg):
    """Return ordered list of category dicts {id, display}."""
    return cfg.get("taxonomy", {}).get("categories", [])


def get_subcategories(cfg):
    return cfg.get("taxonomy", {}).get("subcategories", [])


def category_display(cfg, cat_id):
    for c in get_categories(cfg):
        if c.get("id") == cat_id:
            return c.get("display", cat_id)
    return cat_id


def subcategory_display(cfg, sub_id):
    for s in get_subcategories(cfg):
        if s.get("id") == sub_id:
            return s.get("display", sub_id)
    return sub_id


def load_papers(path=None):
    path = path or (REPO / "papers.yaml")
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("papers", [])


if __name__ == "__main__":
    cfg = load_config()
    print("Topic:", get_topic(cfg).get("name"))
    print("Categories:", [c["id"] for c in get_categories(cfg)])
    print("Subcategories:", [s["id"] for s in get_subcategories(cfg)])
    print("arXiv queries:", len(cfg.get("arxiv_queries", [])))
