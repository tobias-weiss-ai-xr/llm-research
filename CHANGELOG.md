# Changelog

## [Unreleased]
- **Bug fix:** All arXiv API calls now use `https://` instead of `http://`
  (`fetch_new_papers.py`, `fetch_metadata.py`, `saturate_papers.py`).  Many
  networks block plain HTTP; HTTPS is required for arXiv's API.
- **Bug fix:** `fetch_new_papers.py` — fixed `NameError` (`QUERIES` → `queries`) that
  crashed multi-query arXiv discovery runs.
- **Bug fix:** `fetch_openalex_bulk.py` — `reconstruct_abstract()` and
  `sanitize_date()` no longer return the literal string `"papers"` on empty/bad
  input; they return `""` as intended.
- **Config-driven trend keywords:** `standard_stats.py`, `trend_scanner.py`, and
  `landscape_analyzer.py` now read `trend_keywords` from `config/taxonomy.yaml`
  (via `research_config.get_trend_keywords()`), falling back to the built-in list.
  Each repo can now define topic-specific burst keywords.
- **Config-driven subcategory classification:** `fetch_new_papers.py` now exports
  `classify_subcategory(title, abstract, cfg)` that reads `subcategory_keywords`
  from `taxonomy.yaml` first, then falls back to heuristics. `fetch_other_sources.py`
  picks this up automatically via its existing import.
- **Config-driven display names:** `topic_planner.py`, `trend_scanner.py`,
  `landscape_analyzer.py`, `brief_generator.py`, and `standard_stats.py` now use
  `research_config.category_display()` / `subcategory_display()` for proper
  display names instead of raw title-casing of kebab IDs.
- **Config-driven OpenAlex mailto:** `fetch_openalex_bulk.py` reads
  `topic.openalex_mailto` from `taxonomy.yaml` (with env `OPENALEX_MAILTO` override)
  instead of a hardcoded address.
- **`research_config.py`** added `get_trend_keywords()`, `get_subcategory_keywords()`,
  and `get_openalex_mailto()` helpers.

## [0.1.0] — 2026-08-06
- Initial skeleton: config-driven taxonomy, validation, README generation, statistics, reports, discovery, GitHub Pages, CI, AGENTS.md.
