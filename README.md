<h1 align="center">
  <strong>Research Corpus Skeleton</strong>
</h1>
<h3 align="center">Agentic literature review, jump-started — fork me for your own topic</h3>

### 🔗 Links

- **License**: https://github.com/tobias-weiss-ai-xr/skeleton-research/blob/main/LICENSE
- **CI**: https://github.com/<YOUR_ORG>/<YOUR_REPO>/actions/workflows/validate.yml
- **GitHub Pages**: https://<YOUR_ORG>.github.io/<YOUR_REPO>/


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
| 🐙 **GitHub repos discovery** | `scripts/fetch/fetch_github_repos.py` (optional, config-driven via `github_queries` in taxonomy.yaml) |
| 🦊 **GitLab projects discovery** | `scripts/fetch/fetch_gitlab_repos.py` (optional, config-driven via `gitlab_queries` in taxonomy.yaml) |
| 🏠 **Codeberg repos discovery** | `scripts/fetch/fetch_codeberg_repos.py` (optional, config-driven via `codeberg_queries` in taxonomy.yaml) |
| 🖥️ **GitHub Pages site** | `docs/index.html` — searchable, filterable paper browser |
| 🤖 **Agentic workflow** | `AGENTS.md` + `config/taxonomy.yaml` make this repo agent-friendly by design |

## 🚀 Jump-start (5 steps)

```bash
# 1. Clone and rename
git clone https://github.com/tobias-weiss-ai-xr/skeleton-research.git my-topic-research
cd my-topic-research
git remote set-url origin https://github.com/<YOUR_ORG>/my-topic-research.git  # repoint to your fork
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
                   generate_readme.py ──► README.md paper list (auto)
                          │
                          ▼
                  standard_stats.py ──► statistics.json, docs/papers.json,
                                        README.md corpus statistics (auto)
                          │
                          ▼
              analysis/generate_reports.py ──► docs/research/*.md
```

The generated README sections (paper list + corpus statistics) are
**marker-delimited** (`<!-- BEGIN … -->` … `<!-- END … -->`) and are owned by
the pipeline: `generate_readme.py` and `standard_stats.py` regenerate exactly
their section on every run. Everything else in the README is user-owned prose
and is left untouched. If a repo drops a section entirely (e.g. the paper list
lives on the GitHub Pages site), the owning script skips it gracefully instead
of erroring.

- **Never edit the generated README sections by hand** — run the pipeline.
- The **taxonomy lives in one place** (`config/taxonomy.yaml`); every script reads it via `scripts/research_config.py`, which now validates the config up front so mistakes fail loudly.
- **CI (validate.yml)** runs on every push/PR and weekly to discover new papers. The `validate` job re-checks that all generated outputs are fresh (README, statistics, reports), and a `test` job runs the pytest suite.

## 🧪 Local pipeline (all in one)

```bash
make all          # validate → check freshness → generate → test
# …or run the raw steps:
python3 scripts/validate_papers.py && \
python3 scripts/generate_readme.py && \
python3 scripts/standard_stats.py && \
python3 scripts/analysis/generate_reports.py

# Freshness checks (non-destructive; exit 1 if stale) — used by CI
python3 scripts/generate_readme.py --check
python3 scripts/standard_stats.py --check
python3 scripts/analysis/generate_reports.py --check

# Unit tests
python3 -m pytest
```

## 🔎 Discovery & utility scripts

Beyond the core pipeline, several scripts remain available for manual / scheduled use:

| Script | What it does |
|---|---|
| `scripts/fetch/fetch_new_papers.py` | arXiv discovery; `--create-pr` opens a weekly PR (used by CI) |
| `scripts/fetch/fetch_openalex_bulk.py` | OpenAlex bulk discovery per category (`--months`, `--local`) |
| `scripts/fetch/fetch_other_sources.py` | dblp / crossref / Europe PMC / Semantic Scholar discovery |
| `scripts/fetch/fetch_metadata.py` | backfill authors/abstracts/venues for existing arXiv papers |
| `scripts/fetch/saturate_papers.py` | expand queries & loop arXiv until corpus saturates |
| `scripts/fetch/fetch_github_repos.py` / `fetch_gitlab_repos.py` / `fetch_codeberg_repos.py` | discover topic-relevant code repos → `repos.yaml` |
| `scripts/fetch/search_arxiv_html.py` / `search_arxiv_offline.py` | alternate/ad-hoc arXiv search helpers |
| `scripts/export_bibtex.py` | write `paper/references.bib` from `papers.yaml` |
| `scripts/visualize_statistics.py` | visualise `statistics.json` |

The repo-discovery fetchers share rate-limit/backoff + relevance logic in `scripts/fetch/repos_common.py`.

## 🤖 Agentic workflow (AGENTS.md)

This repo is designed to be driven by coding agents (OpenCode, Claude Code, …):

- **Spec-style guardrails** in `AGENTS.md` — agents know the pipeline, never edit README, always re-validate.
- **One config file** to change → one re-run to verify (low context cost for agents).
- **Auto-validation** gives agents an objective pass/fail signal.
- **Weekly discovery** keeps the corpus fresh without human babysitting.

<!-- BEGIN PAPER LIST -->

## 📚 Paper list

- [📚 Methods & Architectures](#methods-&-architectures)
  - [Non-Agentic](#non-agentic)
- [📚 Applications](#applications)
- [📚 Evaluation & Benchmarks](#evaluation-&-benchmarks)
  - [Non-Agentic](#non-agentic)
- [📚 Surveys & Taxonomies](#surveys-&-taxonomies)
  - [Non-Agentic](#non-agentic)

### Methods & Architectures

#### Non-Agentic

##### 2026

- [2026] **KVBoost: Chunk-Level Key-Value Cache Reuse with Deviation-Guided Recomputation for Efficient Large Language Model Inference** [[paper](https://arxiv.org/abs/2608.21362)]

##### 2024

- [2024] **PyramidKV: Dynamic KV Cache Compression based on Pyramidal Information Funneling** [[paper](https://arxiv.org/abs/2406.02069)]
- [2024] **Quest: Query-Aware Sparsity for Efficient Long-Context LLM Inference** [[paper](https://arxiv.org/abs/2406.10774)]
- [2024] **CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion** [[paper](https://arxiv.org/abs/2405.16444)]
- [2024] **MiniCache: KV Cache Compression in Depth Dimension for Large Language Models** [[paper](https://arxiv.org/abs/2405.14366)]
- [2024] **SnapKV: LLM Knows What You are Looking for Before Generation** [[paper](https://arxiv.org/abs/2404.14469)]
- [2024] **TriForce: Lossless Acceleration of Long Sequence Generation with Hierarchical Speculative Decoding** [[paper](https://arxiv.org/abs/2404.11912)]
- [2024] **GEAR: An Efficient KV Cache Compression Recipe for Near-Lossless Generative Inference of LLM** [[paper](https://arxiv.org/abs/2403.05527)]
- [2024] **KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache** [[paper](https://arxiv.org/abs/2402.02750)]
- [2024] **ChunkAttention: Efficient Self-Attention with Prefix-Aware KV Cache and Two-Phase Partition** [[paper](https://arxiv.org/abs/2402.15220)]

##### 2023

- [2023] **Prompt Cache: Modular Attention Reuse for Low-Latency Inference** [[paper](https://arxiv.org/abs/2311.04934)]
- [2023] **Efficient Memory Management for Large Language Model Serving with PagedAttention** [[paper](https://arxiv.org/abs/2309.06180)]
- [2023] **H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models** [[paper](https://arxiv.org/abs/2306.14048)]
- [2023] **Scissorhands: Exploiting the Persistence of Importance Hypothesis for LLM KV Cache Compression at Test Time** [[paper](https://arxiv.org/abs/2305.17118)]

[⬆ Back to top](#paper-list)

### Applications

### Evaluation & Benchmarks

#### Non-Agentic

##### 2024

- [2024] **RULER: What's the Real Context Size of Your Long-Context Language Models?** [[paper](https://arxiv.org/abs/2404.06654)]

##### 2023

- [2023] **LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding** [[paper](https://arxiv.org/abs/2308.14508)]

[⬆ Back to top](#paper-list)

### Surveys & Taxonomies

#### Non-Agentic

##### 2024

- [2024] **A Survey on Efficient Inference for Large Language Models** [[paper](https://arxiv.org/abs/2404.14294)]

[⬆ Back to top](#paper-list)

<!-- END PAPER LIST -->

<!-- BEGIN CORPUS STATISTICS -->

## 📊 Corpus Statistics

**17 papers** across **3 categories**.  
Sources: **arXiv** 17 (100%).  

### Top categories

| Category | Papers | Recent | |
|----------|--------|--------|-|
| method | **14** | 1 | ████████████ |
| evaluation | **2** | 0 | ██░░░░░░░░░░ |
| survey | **1** | 0 | █░░░░░░░░░░░ |

### By year

| Year | Papers | |
|------|--------|-|
| 2023 | 5 | █████░░░░░░░ |
| 2024 | 11 | ████████████ |
| 2026 | 1 | █░░░░░░░░░░░ |

### Momentum (hottest categories)

| Category | Total | Rate | Recent | Score |
|----------|-------|------|--------|-------|
| Method | 14 | 0.1/mo | 7% | 7 |
| Evaluation | 2 | 0.0/mo | 0% | 0 |
| Survey | 1 | 0.0/mo | 0% | 0 |

### Trending keywords

| Keyword | Papers | Burst |
|---------|--------|-------|
| system | 1 | 1.89 |
| model | 1 | 1.0 |

### Research gaps (thinnest cells)

| Cell | Papers |
|------|--------|
| `survey/non-agentic` | 1 |
| `evaluation/non-agentic` | 2 |
| `method/non-agentic` | 14 |

*Generated 2026-08 by `scripts/standard_stats.py`.*

<!-- END CORPUS STATISTICS -->

## 📖 Citation

If you use this skeleton for a project, please cite:

```bibtex
@misc{skeleton-research,
  author = {Weiß, Tobias},
  title = {Research Corpus Skeleton: Data-Driven Agentic Literature Review},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/tobias-weiss-ai-xr/skeleton-research}
}
```

## 📄 License

MIT — see [LICENSE](LICENSE).
