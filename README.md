<h1 align="center">
  <strong>Research Corpus Skeleton</strong>
</h1>
<h3 align="center">Agentic literature review, jump-started — fork me for your own topic</h3>

<div align="center">

[![License](https://img.shields.io/badge/License-MIT-yellow.svg?)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/<YOUR_ORG>/<YOUR_REPO>/validate.yml?label=CI&logo=github)](https://github.com/<YOUR_ORG>/<YOUR_REPO>/actions/workflows/validate.yml)
[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-brightgreen.svg?logo=github)](https://<YOUR_ORG>.github.io/<YOUR_REPO>/)

</div>

> 🎓 **Workshop-ready:** This repository is the *skeleton* for a data-driven,
> auto-validated, agentic literature review — the same architecture used by the
> `*-research` corpus repos (agent-memory, agent-skill, agent-learning, …).

## What you get

| Capability | How |
|------------|-----|
| 📄 **Curated corpus** | `papers.yaml` is the source of truth — one structured entry per paper |
| ✅ **Auto-validation** | `scripts/validate_papers.py` checks schema, duplicates, URL normalization, LaTeX artifacts |
| 🧾 **Auto-generated README** | `scripts/generate_readme.py` renders the paper list grouped by your taxonomy |
| 📊 **Statistics & trends** | `scripts/standard_stats.py` → `statistics.json` (momentum, gaps, bursts, venues, authors) |
| 🔍 **Literature review report** | `scripts/analysis/generate_reports.py` → `docs/research/literature_review.md` + `trends.md` |
| 🧭 **Topic planning** | `tools/topic_planner.py`, `tools/trend_scanner.py`, `tools/landscape_analyzer.py`, `tools/brief_generator.py` |
| 🔎 **New paper discovery** | `scripts/fetch/fetch_new_papers.py` (arXiv), `fetch_other_sources.py` (dblp/crossref/europepmc), `fetch_openalex_bulk.py` |
| 🖥️ **GitHub Pages site** | `docs/index.html` — searchable, filterable paper browser |
| 🤖 **Agentic workflow** | `AGENTS.md` + `config/taxonomy.yaml` make this repo agent-friendly by design |

## 🚀 Jump-start (5 steps)

```bash
# 1. Clone and rename
git clone https://github.com/<YOUR_ORG>/skeleton-research.git my-topic-research
cd my-topic-research

# 2. Define your topic & taxonomy
#    Edit config/taxonomy.yaml: topic name, categories, subcategories, queries
vim config/taxonomy.yaml

# 3. Seed your corpus (start small — 5-10 papers is fine)
#    Either hand-curate papers.yaml, or auto-discover:
python3 scripts/fetch/fetch_new_papers.py --months 12 --dry-run   # preview arXiv hits
python3 scripts/fetch/fetch_new_papers.py --local                 # append to papers.yaml

# 4. Validate + generate
python3 scripts/validate_papers.py
python3 scripts/generate_readme.py
python3 scripts/standard_stats.py
python3 scripts/analysis/generate_reports.py

# 5. Commit & let CI keep it healthy
git add -A && git commit -m "bootstrap corpus for <YOUR TOPIC>"
git push
```

## 📖 How it works

```
config/taxonomy.yaml ──► papers.yaml ──► validate_papers.py
                          │   ▲              │
                          ▼   └── fetch_* ───┘
                   generate_readme.py ──► README.md (auto)
                          │
                          ▼
                  standard_stats.py ──► statistics.json, docs/papers.json
                          │
                          ▼
              analysis/generate_reports.py ──► docs/research/*.md
```

- **Never edit README.md directly** — it is generated from `papers.yaml`.
- The **taxonomy lives in one place** (`config/taxonomy.yaml`); every script reads it via `scripts/research_config.py`.
- **CI (validate.yml)** runs on every push/PR and weekly to discover new papers.

## 🧪 Local pipeline (all in one)

```bash
# Full pipeline (validate → README → stats → reports)
python3 scripts/validate_papers.py && \
python3 scripts/generate_readme.py && \
python3 scripts/standard_stats.py && \
python3 scripts/analysis/generate_reports.py
```

## 🤖 Agentic workflow (AGENTS.md)

This repo is designed to be driven by coding agents (OpenCode, Claude Code, …):

- **Spec-style guardrails** in `AGENTS.md` — agents know the pipeline, never edit README, always re-validate.
- **One config file** to change → one re-run to verify (low context cost for agents).
- **Auto-validation** gives agents an objective pass/fail signal.
- **Weekly discovery** keeps the corpus fresh without human babysitting.

## 📚 Paper list

- [📚 Methods & Architectures](#methods-&-architectures)
  - [Agentic](#agentic)
- [📚 Applications](#applications)
  - [Non-Agentic](#non-agentic)
- [📚 Evaluation & Benchmarks](#evaluation-&-benchmarks)
- [📚 Surveys & Taxonomies](#surveys-&-taxonomies)
  - [Hybrid](#hybrid)

### Methods & Architectures

#### Agentic

##### 2026

- [2026] **Example Paper 2: An Agentic Method for Your Topic** [[paper](https://arxiv.org/abs/2603.00002)]

[⬆ Back to top](#paper-list)

### Applications

#### Non-Agentic

##### 2025

- [2025] **Example Paper 3: Application Study in Your Domain** [[paper](https://arxiv.org/abs/2511.00003)]

[⬆ Back to top](#paper-list)

### Evaluation & Benchmarks

### Surveys & Taxonomies

#### Hybrid

##### 2026

- [2026] **Example Paper 1: A Foundational Survey of Your Topic** [[paper](https://arxiv.org/abs/2601.00001)]

[⬆ Back to top](#paper-list)

## 📖 Citation

If you use this skeleton for a project, please cite:

```bibtex
@misc{skeleton-research,
  author = {Weiß, Tobias},
  title = {Research Corpus Skeleton: Data-Driven Agentic Literature Review},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/<YOUR_ORG>/skeleton-research}
}
```

## 📄 License

MIT — see [LICENSE](LICENSE).
