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

- [2026] **Practical Online KV Cache Compaction for LLM Agents: An Empirical Study** [[paper](https://arxiv.org/abs/2608.00902)]
- [2026] **Learning how to Forget: Fine-tuning for Long-Context Sparse Attention** [[paper](https://arxiv.org/abs/2608.19920)] [[code](https://github.com/awslabs/keys_values)]
- [2026] **Bole: Efficient Tree Speculation for Hybrid-Attention Language Models** [[paper](https://arxiv.org/abs/2608.01651)]
- [2026] **KV Cache Compression Through the Lens of Transform Coding** [[paper](https://arxiv.org/abs/2608.14191)]
- [2026] **WhiteMatter: All-to-All Cross-Layer Connections via KV Mixing** [[paper](https://arxiv.org/abs/2608.18486)]
- [2026] **CoinRAG: Contextualized Information Nugget KV Cache Reuse for Long-Context RAG** [[paper](https://arxiv.org/abs/2608.07458)]
- [2026] **S4R: Selective Sampling, Subspaces, and Sparse Reconstruction for Compressed Long-Context KV Caching** [[paper](https://arxiv.org/abs/2608.00528)]
- [2026] **WnW: Waxing-and-Waning KV Cache for Long-Form Speech LLMs** *EMNLP 2026 Main Conference. 8 pages* [[paper](https://arxiv.org/abs/2608.22704)]
- [2026] **Autonomy-of-Heads: Data-Free Sparse Attention from Frozen Query-Key Geometry** [[paper](https://arxiv.org/abs/2608.06849)]
- [2026] **TreeWY: Speculative Verification for Gated DeltaNet Hybrids** [[paper](https://arxiv.org/abs/2608.20961)]
- [2026] **RestoreKV: Recovering Full-Cache Behavior Under Aggressive Query-Agnostic KV Cache Eviction** [[paper](https://arxiv.org/abs/2608.01247)]
- [2026] **QEvict: Recoverable Quantized KV Eviction for Attention-Drift-Robust Long-Context Decoding** [[paper](https://arxiv.org/abs/2608.05326)]
- [2026] **Archer: Adaptive Reuse of Cached Hidden States for Efficient Rollback in Diffusion Language Models** [[paper](https://arxiv.org/abs/2608.08086)] [[code](https://github.com/Hxnng/Archer)]
- [2026] **AnchorKV: Anchor-Residual KV Cache Compression** [[paper](https://arxiv.org/abs/2608.02901)]
- [2026] **VoiceChat-TTS: A Low-Latency Continuous Speech Synthesis Model for Interactive Agents** [[paper](https://arxiv.org/abs/2608.13831)]
- [2026] **Beyond Sparse Weights: When Is Attention Compressible?** [[paper](https://arxiv.org/abs/2608.21541)]
- [2026] **RT-SEMamba: Real-Time Speech Enhancement Mamba via Progressive Knowledge Distillation** [[paper](https://arxiv.org/abs/2608.12099)]
- [2026] **Beyond Factual Knowledge: Benchmarking and Learning Step-Level Procedural Rule Reasoning in Large Language Models** [[paper](https://arxiv.org/abs/2608.22753)] [[code](https://github.com/SharkSpicy-NLP/Beyond-Factual-Knowledge)]
- [2026] **Does Accuracy Equal Evidence? Reasoning Faithfulness under KV Cache Compression** [[paper](https://arxiv.org/abs/2608.01631)] [[code](https://github.com/famous-blue-raincoat/Safe_KV_Compress)]
- [2026] **MentorPulse: Refreshing Cross-Model Latent Guidance for Long-Form Generation** [[paper](https://arxiv.org/abs/2608.20927)]
- [2026] **Opt.Gear Technical Report** [[paper](https://arxiv.org/abs/2608.01034)]
- [2026] **FlashPrefill V2: Block-Sparse Prefill Attention for Long-Context LLM Serving** [[paper](https://arxiv.org/abs/2608.19758)]
- [2026] **Accelerating Diffusion Language Models via Structured Suffix Modeling** [[paper](https://arxiv.org/abs/2608.23167)] [[code](https://github.com/zifengcheng/SSM)]
- [2026] **KV-Rescue: Recovering Reasoning Language Model KV Eviction Loss via Stepwise Interleaving** [[paper](https://arxiv.org/abs/2608.15797)]
- [2026] **Understanding Sparse Attention Selectivity in Long-Context Foundation Models via Counterfactual Evaluation** [[paper](https://arxiv.org/abs/2608.01676)]
- [2026] **Ripple-Pivot Search: Active Parallel Decoding for Diffusion Large Language Models** [[paper](https://arxiv.org/abs/2608.11742)]
- [2026] **Position Encoding in Transformers: From Absolute and Relative Methods to Rotary Position Embeddings and Long-Context Scaling** [[paper](https://arxiv.org/abs/2608.10021)]
- [2026] **Training-Free Hashing-Based Attention via Binary Principal Components** [[paper](https://arxiv.org/abs/2608.04405)] [[code](https://github.com/yudaohai666/BPC)]
- [2026] **From Retrieved Context to Runtime Control: Adaptive Compression for Edge-based RAG** [[paper](https://arxiv.org/abs/2608.19535)]
- [2026] **LLM Serving in the Wild: An Empirical Study of Frameworks, Methods, and System Designs** [[paper](https://arxiv.org/abs/2608.03036)]
- [2026] **HYDRA: A Heterogeneous Chiplet DSE Framework for Serving Dynamic Hybrid LLM Workloads** [[paper](https://arxiv.org/abs/2608.19395)]
- [2026] **Cascade: Exploiting SLO-Aware latency budget for fair and high goodput LLM inference serving** [[paper](https://arxiv.org/abs/2608.06557)]
- [2026] **TokenPowerSandbox: Evidence-Gated CPU-First Screening for Energy-Aware LLM Serving** [[paper](https://arxiv.org/abs/2608.18149)]
- [2026] **FleetSieve: Decision-Critical Profiling for SLO-Aware LLM Fleet Configuration** [[paper](https://arxiv.org/abs/2608.19659)]
- [2026] **Beyond Binary Priorities: Multi-Tier SLA Scheduling for Large Language Model Serving** [[paper](https://arxiv.org/abs/2608.16336)]
- [2026] **ST2U: Stateful Test-Time Unlearning via Restricted Knowledge Boundary Control** [[paper](https://arxiv.org/abs/2608.23034)]
- [2026] **Global Simulation-Guided Dynamic Operator Scheduling for Efficient Multi-Tenant Model Serving** [[paper](https://arxiv.org/abs/2608.15762)]
- [2026] **Pallas: A Proactive KV Cache Migration Framework for LLM Inference in AI-RAN** [[paper](https://arxiv.org/abs/2608.16477)]
- [2026] **Llama-Mobile: Efficient 2.7-Bit Quantization of VLMs** [[paper](https://arxiv.org/abs/2608.21134)]
- [2026] **DIVE: Dynamic Iterative Visual Evidence Construction for Efficient Vision-Language Models** [[paper](https://arxiv.org/abs/2608.04496)] [[code](https://github.com/Zhong-Chenchen/DIVE.git)]
- [2026] **FrugalSOT - Frugal Search Over the Models** [[paper](https://arxiv.org/abs/2608.21621)]
- [2026] **From Digital to Physical Reservoir Computing: Co-Optimizing Soft Robotic Reservoirs via Dynamics Matching** [[paper](https://arxiv.org/abs/2608.00484)]
- [2026] **CascadeLUT: Information-Ordered Streaming Inference for Bandwidth-Constrained FPGAs** [[paper](https://arxiv.org/abs/2608.00720)]
- [2026] **Flow Matching Meets 3D Curvilinear Structure Segmentation in Medical Imaging** [[paper](https://arxiv.org/abs/2608.19965)]
- [2026] **CookVoice: Unified Framework for Style Controllable Multi-Modal Human Voice Generation** [[paper](https://arxiv.org/abs/2608.11590)] [[project](https://haoweilou.github.io/CookVoice/)]
- [2026] **Depth-adaptive Inference of Looped Language Models via Continuous Depth Batching** [[paper](https://arxiv.org/abs/2608.09444)]
- [2026] **C2KV: Compressed and Composable KV Cache Reuse for Efficient LLM Inference** [[paper](https://arxiv.org/abs/2607.17715)]
- [2026] **Towards Efficient Large Language Model Serving: A Survey on System-Aware KV Cache Optimization** [[paper](https://arxiv.org/abs/2607.08057)]
- [2026] **Mixture-of-Translators: Translating KV Caches Across Heterogeneous Large Language Models** [[paper](https://arxiv.org/abs/2607.28979)]
- [2026] **A Sparse Glimpse of the Whole: Train-Free Self-Speculative Decoding** [[paper](https://arxiv.org/abs/2607.27735)]
- [2026] **SpecLA: Efficient Speculative Decoding for Linear-Attention Models** [[paper](https://arxiv.org/abs/2607.16673)]
- [2026] **Kalypso: Relational LLM Serving** [[paper](https://arxiv.org/abs/2607.23815)]
- [2026] **PARTREP: Learning What to Repeat for Decoder-only LLMs** [[paper](https://arxiv.org/abs/2607.01792)]
- [2026] **Recall Before You Rank: Similarity-Guided Top-K Reuse for Efficient Long-Context Attention** [[paper](https://arxiv.org/abs/2607.27692)]
- [2026] **DIRECT: Direct Decoding for Efficient and Aligned Sequence Labeling with Large Language Models** [[paper](https://arxiv.org/abs/2607.26891)]
- [2026] **PReM: Learning What to Preserve and When to Refresh for Context Compression** [[paper](https://arxiv.org/abs/2607.14327)]
- [2026] **Error Certificates for KV-Cache Eviction via Randomized Design** [[paper](https://arxiv.org/abs/2607.21475)]
- [2026] **Reading Between the Dots: Decoding Hidden Computation across Filler Tokens** [[paper](https://arxiv.org/abs/2607.03502)]
- [2026] **ResKV: Reconstructing Omitted Attention Contributions for Fixed-Budget KV Cache Compression** [[paper](https://arxiv.org/abs/2607.29591)]
- [2026] **Adaptive Filtering of the KV Cache: Diagnosing and Correcting Structural-Role Bias in LLM Inference** [[paper](https://arxiv.org/abs/2607.13205)]
- [2026] **SeDeM: Selective Decompression of Hidden-State Memories for Long-Context Question Answering** [[paper](https://arxiv.org/abs/2608.00311)]
- [2026] **VarRate: Training-Free Variable-Rate KV Cache Compression for Long-Context LLMs** [[paper](https://arxiv.org/abs/2607.15498)]
- [2026] **Through the Bottleneck: How Multi-head Latent Attention Separates Content from Position in Language Models** [[paper](https://arxiv.org/abs/2607.23054)]
- [2026] **WAR: Workload-Aware Rollouts for Synchronous Agentic Reinforcement Learning** [[paper](https://arxiv.org/abs/2607.17299)]
- [2026] **Faster but Different: Diagnosing and Controlling Content Drift in Accelerated Multimodal Diffusion Language Models** [[paper](https://arxiv.org/abs/2607.29079)]
- [2026] **Training Hybrid Block Diffusion Language Models with Partial Bidirectionality** [[paper](https://arxiv.org/abs/2607.02805)]
- [2026] **When Words Predict Workload** [[paper](https://arxiv.org/abs/2607.04951)]
- [2026] **Distill to Detect: Exposing Stealth Biases in LLMs through Cartridge Distillation** [[paper](https://arxiv.org/abs/2607.01208)]
- [2026] **LLMET: Enabling Cross-Layer Evaluation of Emerging M3D Memories for Energy-Efficient LLM Serving** [[paper](https://arxiv.org/abs/2607.26491)]
- [2026] **KAP: Bridging the Knowledge Selection-Runtime Consumption Gap in LLM Systems** [[paper](https://arxiv.org/abs/2607.24260)]
- [2026] **PagedWeight: Efficient MoE LLM Serving with Dynamic Quality-Aware Weight Quantization** [[paper](https://arxiv.org/abs/2607.16184)]
- [2026] **DeltaServe: Host-Agnostic Co-Serving of Inference and Fine-Tuning for LLMs** [[paper](https://arxiv.org/abs/2607.28848)]
- [2026] **Agentic Coding in the Wild: Characterizing GitHub Copilot Traces at Production Scale** [[paper](https://arxiv.org/abs/2608.00101)]
- [2026] **Supervised Fine-Tuning vs. In-Context Learning: An Equilibrium Analysis of LLM Personalization under Congestion** [[paper](https://arxiv.org/abs/2607.14371)]
- [2026] **Unified Static-Dynamic Pruning for Efficient LLM Inference** [[paper](https://arxiv.org/abs/2607.21985)]
- [2026] **Cache-Aware Prompt Compression:A Two-Tier Cost Model for LLM API Caching** [[paper](https://arxiv.org/abs/2607.15516)]
- [2026] **Lynx: Progressive Speculative Quantization for accelerating KV Transfer in Long-Context Inference** [[paper](https://arxiv.org/abs/2607.01831)]
- [2026] **FedLSG: LLM-Enhanced Semantic Calibration for Federated Graph Backdoor Defense** [[paper](https://arxiv.org/abs/2607.19674)]
- [2026] **Deformable State Estimation for Autonomous Surgical Tissue Retraction Under Partial Observability** [[paper](https://arxiv.org/abs/2607.13475)]
- [2026] **FUSE: FK-Steered Multi-Modal Flow Matching for Efficient Simulation-Based Posterior Estimation** [[paper](https://arxiv.org/abs/2607.05252)]
- [2026] **Transforming LLMs into Efficient Cross-Encoders via Knowledge Distillation for RAG Reranking** [[paper](https://arxiv.org/abs/2607.11933)]
- [2026] **A Lightweight Foundation Model for Collider Physics with Multi-Domain Adaptation** [[paper](https://arxiv.org/abs/2607.27501)]
- [2026] **Transformers with Physics-Informed Encodings and Simulation-Based Inference for Robust Detection of Eccentric Binary Black Holes in Pulsar Timing Array Data** [[paper](https://arxiv.org/abs/2607.03904)]
- [2026] **Sparse Inter-Layer Dependencies of Transformer FFN Neurons** [[paper](https://arxiv.org/abs/2607.11990)]
- [2026] **MXAttention: Data-Free Optimal Scaling and Pre-Normalization Quantization for MXFP4 Attention** [[paper](https://arxiv.org/abs/2607.24377)]
- [2026] **Sensitivity-Aware Thresholding and Token Routing for Activation Sparsification in Large Language Models** [[paper](https://arxiv.org/abs/2607.08991)]
- [2026] **Constrained Decoding for Diffusion Language Models via Efficient Inference over Finite Automata** [[paper](https://arxiv.org/abs/2607.07026)]
- [2026] **Efficient Learning of Truncated Boolean Product Distributions: Influence to the Rescue** [[paper](https://arxiv.org/abs/2607.22889)]
- [2026] **Self-Gating Attention for Efficient Time Series Forecasting** [[paper](https://arxiv.org/abs/2607.02344)]
- [2026] **Driving up Inference Energy on SNNs: Per-Sample and Universal Sponge Attacks** [[paper](https://arxiv.org/abs/2607.27990)]
- [2026] **Value-Aware Stochastic KV Cache Eviction for Reasoning Models** [[paper](https://arxiv.org/abs/2606.03928)]
- [2026] **Multi-Segment Attention: Enabling Efficient KV-Cache Management for Faster Large Language Model Serving** [[paper](https://arxiv.org/abs/2606.02964)]
- [2026] **Keyless Attention: Value-Space Routing and Value-Only Caching for Efficient Transformers** [[paper](https://arxiv.org/abs/2606.21848)]
- [2026] **SeKV: Resolution-Adaptive KV Cache with Hierarchical Semantic Memory for Long-Context LLM Inference** [[paper](https://arxiv.org/abs/2606.31145)] [[code](https://github.com/AmirAbaskohi/SeKV)]
- [2026] **Information-Aware KV Cache Compression for Long Reasoning** [[paper](https://arxiv.org/abs/2606.26875)]
- [2026] **YouZhi: Towards High-Concurrency Financial LLMs via Adaptive GQA-to-MLA Transition** [[paper](https://arxiv.org/abs/2606.05868)]
- [2026] **End-to-End Context Compression at Scale** [[paper](https://arxiv.org/abs/2606.09659)]
- [2026] **Unlimited OCR Works** [[paper](https://arxiv.org/abs/2606.23050)] [[code](http://github.com/baidu/Unlimited-OCR)]
- [2026] **Coverage-Driven KV Cache Eviction for Efficient and Improved Inference of LLM** [[paper](https://arxiv.org/abs/2606.29563)]
- [2026] **MiniPIC: Flexible Position-Independent Caching in <100LOC** [[paper](https://arxiv.org/abs/2606.13126)]
- [2026] **Last But Not Least: Boundary Attention CalibratiON for Multimodal KV Cache Compression** [[paper](https://arxiv.org/abs/2606.14782)]
- [2026] **From Rigid to Dynamic: Entropy-Guided Adaptive Inference for Long-Context LLMs** [[paper](https://arxiv.org/abs/2606.09508)] [[code](https://github.com/SHA-4096/EntropyInfer)]
- [2026] **GLIDE: Guided Layerwise Hybrid Attention for Efficient LLM Inference** [[paper](https://arxiv.org/abs/2607.24788)]
- [2026] **Rethinking LoRA Memory Through the Lens of KV Cache Compression** [[paper](https://arxiv.org/abs/2606.05698)]
- [2026] **RKSC: Reasoning-Aware KV Cache Sharing and Confident Early Exit for Multi-Step LLM Inference** [[paper](https://arxiv.org/abs/2606.09937)] [[code](https://github.com/AnirudhSekar/RKSC)]
- [2026] **LazyAttention: Efficient Retrieval-Augmented Generation with Deferred Positional Encoding** [[paper](https://arxiv.org/abs/2606.04302)]
- [2026] **AGENTSERVESIM: A Hardware-aware Simulator for Multi-Turn LLM Agent Serving** [[paper](https://arxiv.org/abs/2606.09613)]
- [2026] **Dual Dimensionality for Local and Global Attention** [[paper](https://arxiv.org/abs/2606.18587)]
- [2026] **Latent Reasoning with Normalizing Flows** [[paper](https://arxiv.org/abs/2606.06447)]
- [2026] **You Only Index Once: Cross-Layer Sparse Attention with Shared Routing** [[paper](https://arxiv.org/abs/2606.06467)]
- [2026] **Fractional Decay KV-Cache: Ownership-Aware Memory Management for Improved Inference Relevancy in Dialog Systems** [[paper](https://arxiv.org/abs/2608.18098)]
- [2026] **MM-ShiftKV: Decode-Aware Prefill-Stage KV Selection for Multimodal Large Language Models** [[paper](https://arxiv.org/abs/2607.22586)] [[code](https://github.com/zjuDBxAI/MM-ShiftKV)]
- [2026] **KVEraser: Learning to Steer KV Cache for Efficient Localized Context Erasing** [[paper](https://arxiv.org/abs/2606.17034)]
- [2026] **RoPE-Aware Bit Allocation for KV-Cache Quantization** [[paper](https://arxiv.org/abs/2606.24033)] [[code](https://github.com/JIA-Lab-research/blockgtq)]
- [2026] **Beyond tokens: a unified framework for latent communication in LLM-based multi-agent systems** [[paper](https://arxiv.org/abs/2606.05711)]
- [2026] **Depth-Attention: Cross-Layer Value Mixing for Language Models** [[paper](https://arxiv.org/abs/2606.05014)]
- [2026] **RaBitQCache: Rotated Binary Quantization for KVCache in Long Context LLM Inference** [[paper](https://arxiv.org/abs/2606.31519)] [[code](https://github.com/Sakuraaa0/RaBitQCache.git)]
- [2026] **Thought-Aware KV Cache Compaction for Reasoning via Adaptive Attention Matching** [[paper](https://arxiv.org/abs/2608.12331)]
- [2026] **Latent Personal Memory: Represent personal memory as dynamic soft prompts** [[paper](https://arxiv.org/abs/2606.20911)]
- [2026] **Decoupled Mixture-of-Experts for Parametric Knowledge Injection** [[paper](https://arxiv.org/abs/2606.14243)]
- [2026] **Dustin: Draft-Augmented Sparse Verification for Efficient Long-Context Generation with Speculative Decoding** [[paper](https://arxiv.org/abs/2606.24957)]
- [2026] **Variable-Width Transformers** [[paper](https://arxiv.org/abs/2606.18246)]
- [2026] **Epiphany-Aware KV Cache Eviction Without the Attention Matrix** [[paper](https://arxiv.org/abs/2606.26472)]
- [2026] **Cartridges at Scale: Training Modular KV Caches over Large Document Collections** [[paper](https://arxiv.org/abs/2606.04557)]
- [2026] **Taylor-Calibrate: Principled Initialization for Hybrid Linear Attention Distillation** [[paper](https://arxiv.org/abs/2606.16429)]
- [2026] **From Layers to Submodules: Rethinking Granularity in Replacement-Based LLM Compression** [[paper](https://arxiv.org/abs/2606.02559)] [[code](https://github.com/eliacunegatti/SubFit)]
- [2026] **SparDA: Sparse Decoupled Attention for Efficient Long-Context LLM Inference** [[paper](https://arxiv.org/abs/2606.04511)] [[code](https://github.com/NVlabs/SparDA)]
- [2026] **TRADE: Transducer-Augmented Decoder for Speech LLM** [[paper](https://arxiv.org/abs/2606.08486)]
- [2026] **Towards Direct Latent-Space Synthesis for Parallel Branches in LLM-Agent Workflows** [[paper](https://arxiv.org/abs/2606.14672)]
- [2026] **MedLatentDx: Latent Multi-Agent Communication for Cross-Hospital Rare-Disease Diagnosis** [[paper](https://arxiv.org/abs/2606.13945)]
- [2026] **SimSD: Simple Speculative Decoding in Diffusion Language Models** [[paper](https://arxiv.org/abs/2606.02544)]
- [2026] **Do Transformers Need Three Projections? Systematic Study of QKV Variants** *ICML 2026* [[paper](https://arxiv.org/abs/2606.04032)] [[code](https://github.com/Brainchip-Inc/Do-Transformers-Need-3-Projections)]
- [2026] **Fast-dLLM++: Fréchet Profile Decoding for Faster Diffusion LLM Inference** [[paper](https://arxiv.org/abs/2606.02955)] [[code](https://github.com/Ringo-Star/FastdLLM_plusplus)]
- [2026] **When Does Learning to Stop Help? A Cost-Aware Study of Early Exits in Reasoning Models** [[paper](https://arxiv.org/abs/2606.30852)]
- [2026] **Beyond Prediction: Tail-Aware Scheduling for LLM Inference** [[paper](https://arxiv.org/abs/2606.18431)]
- [2026] **From Tensor Buffer to Distributed Memory Hierarchy: A Survey of KV Cache Management for LLM Serving** [[paper](https://arxiv.org/abs/2607.02574)]
- [2026] **Communication-Efficient Verifiable Attention for LLM Inference** [[paper](https://arxiv.org/abs/2606.16352)]
- [2026] **TokenPilot: Cache-Efficient Context Management for LLM Agents** [[paper](https://arxiv.org/abs/2606.17016)] [[code](https://github.com/zjunlp/LightMem2)]
- [2026] **CrossPool: Efficient Multi-LLM Serving for Cold MoE Models through KV-Cache and Weight Disaggregation** [[paper](https://arxiv.org/abs/2606.24506)]
- [2026] **Service-Induced Congestion in Memory-Constrained LLM Serving** [[paper](https://arxiv.org/abs/2606.15555)]
- [2026] **Tangram: Unlocking Non-Uniform KV Cache Compression for Efficient Multi-turn LLM Serving** [[paper](https://arxiv.org/abs/2606.06302)] [[code](https://github.com/aiha-lab/TANGRAM)]
- [2026] **PersistentKV: Page-Aware Decode Scheduling for Long-Context LLM Serving on Commodity GPUs** [[paper](https://arxiv.org/abs/2606.26666)]
- [2026] **Execution-State Capsules: Graph-Bound Execution-State Checkpoint and Restore for Low-Latency, Small-Batch, On-Device Physical-AI Serving** [[paper](https://arxiv.org/abs/2606.20537)]
- [2026] **HERALD: High-Throughput Block Diffusion LLM Serving via CPU-GPU Cooperative KV Cache Retrieval** [[paper](https://arxiv.org/abs/2606.21633)]
- [2026] **Mitigating the Contractivity Trap in Diffusion ODEs via Stein Stabilization** [[paper](https://arxiv.org/abs/2606.07835)]
- [2026] **Toward Multi-Domain and Long-Tailed Quantization via Feature Alignment and Scaling** [[paper](https://arxiv.org/abs/2606.04920)]
- [2026] **Efficient Network Inference via Hardware-Aware Architecture Search, Model Pruning & Quantization** [[paper](https://arxiv.org/abs/2606.23210)]
- [2026] **Efficient Analytic Uncertainty Quantification for Multi-Modal Regression** [[paper](https://arxiv.org/abs/2606.25188)]
- [2026] **LRMIL: Efficient Low-Resolution Multiple Instance Learning via High-Resolution Knowledge Distillation for Whole Slide Image Classification** [[paper](https://arxiv.org/abs/2606.06864)]
- [2026] **FLARE: Diffusion for Hybrid Language Model** [[paper](https://arxiv.org/abs/2606.01774)]
- [2026] **Streaming Knowledge Compilation: Proactive Materiality-Scored Pinning for Time-Evolving LLM Wikis** [[paper](https://arxiv.org/abs/2606.09877)]
- [2026] **Distill on a Diet: Efficient Knowledge Distillation via Learnable Data Pruning** [[paper](https://arxiv.org/abs/2606.25488)]
- [2026] **KVBoost: Chunk-Level Key-Value Cache Reuse with Deviation-Guided Recomputation for Efficient Large Language Model Inference** [[paper](https://arxiv.org/abs/2608.21362)]
- [2026] **Probing the Prompt KV Cache: Where It Becomes Dispensable** [[paper](https://arxiv.org/abs/2605.30574)]
- [2026] **GRKV: Global Regression for Training-Free KV Cache Compression in Long-Context LLMs** [[paper](https://arxiv.org/abs/2605.31105)]
- [2026] **WaveFilter: Enhancing the Long-Context Capability of Diffusion LLMs via Wavelet-Guided KV Cache Filtering** [[paper](https://arxiv.org/abs/2606.00724)]
- [2026] **PrunePath: Towards Highly Structured Sparse Language Models** [[paper](https://arxiv.org/abs/2605.28283)]
- [2026] **Efficient Diffusion LLMs via Temporal-Spatial Parallel Decoding and Confidence Extrapolation** [[paper](https://arxiv.org/abs/2605.30753)]
- [2026] **CacheProbe: Auditing Prompt Cache Isolation in Gateway APIs** [[paper](https://arxiv.org/abs/2605.30613)]
- [2026] **RW-TTT: Batched Serving for Request-Owned Test-Time Training State** [[paper](https://arxiv.org/abs/2605.28053)]
- [2026] **ViBE: Co-Optimizing Workload Skew and Hardware Variability for MoE Serving** [[paper](https://arxiv.org/abs/2606.00735)]
- [2026] **Augmenting Attention with Exponentially Decaying Memory Improves Query-Aware KV Sparsity** [[paper](https://arxiv.org/abs/2605.28640)]

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

##### 2026

- [2026] **Beyond Teacher Likelihood: Group-Calibrated On-Policy Distillation for Long-Context Reasoning** [[paper](https://arxiv.org/abs/2608.19181)] [[code](https://github.com/SolereZhang/GC-OPD)]
- [2026] **LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing** [[paper](https://arxiv.org/abs/2608.01662)]
- [2026] **SEER: Long-Context Reasoning via Selective Visual-Text Compression** [[paper](https://arxiv.org/abs/2608.15962)] [[code](https://github.com/jiaweixu98/SEER)]
- [2026] **Can Agent Memory Systems Track Evolving State?** [[paper](https://arxiv.org/abs/2608.19652)]
- [2026] **ContractScrub: A benchmark for final review of legal contracts** [[paper](https://arxiv.org/abs/2608.20204)]
- [2026] **PI-Mem: Pushing Long-Context Reasoning to 3.6M Tokens with Parallel-Iterative Memory** [[paper](https://arxiv.org/abs/2608.03048)]
- [2026] **OmniAlign: A Unified Multilingual Aligner for Word and Sentence Alignment** [[paper](https://arxiv.org/abs/2608.18474)] [[code](https://github.com/MilkDargon/OmniAlign)] [[project](https://huggingface.co/WPS-Qingqiu/OmniAlign})]
- [2026] **SimpleOPD: Simple Tokenizer-Agnostic On-Policy Distillation for Long-Context Reasoning** [[paper](https://arxiv.org/abs/2608.14277)]
- [2026] **Beyond LLM-Based Reasoning: Lightweight GNNs for Agent Failure Attribution** [[paper](https://arxiv.org/abs/2608.18575)]
- [2026] **ArborMem: Navigating Interaction States with Memory Forests** [[paper](https://arxiv.org/abs/2608.17534)]
- [2026] **MoNe: Modular Neural Memory for Efficient Long Context Inference** [[paper](https://arxiv.org/abs/2608.17616)]
- [2026] **EpiBench: Can LLMs Understand Epitopes for Antibody Drug Discovery?** [[paper](https://arxiv.org/abs/2608.06022)]
- [2026] **Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents** [[paper](https://arxiv.org/abs/2608.15008)]
- [2026] **Reduced Matrix Multiplication: Input-Adaptive Matrix-Product Reduction for LLM Inference** [[paper](https://arxiv.org/abs/2608.13426)]
- [2026] **Distractor-Aware Truncation: Disentangling Context-Length Effects from Signal Loss in Long-Context LLM Benchmarks** [[paper](https://arxiv.org/abs/2608.03297)]
- [2026] **Quantization-Aware Healing: A Practical Recipe for Recovering Compressed, 4-Bit LLMs** [[paper](https://arxiv.org/abs/2608.20953)]
- [2026] **EvoWiki: Incremental State Overwriting and Traceable Question Answering for Cross-Meeting Knowledge Evolution** [[paper](https://arxiv.org/abs/2608.23265)]
- [2026] **Macaron-V1: Towards Open Continual Learning with Self-Improvement and Mixture-of-LoRA** [[paper](https://arxiv.org/abs/2608.09819)]
- [2026] **ATFlash: Per-RoPE-Wavelength Attention Windows for Compute/Memory-Efficient LLM Inference** [[paper](https://arxiv.org/abs/2608.02947)]
- [2026] **Self-Guided Test-Time Training for Long-Context LLMs** [[paper](https://arxiv.org/abs/2607.09415)]
- [2026] **INS-ActBench: A Comprehensive Benchmark for Assessing Professional Actuarial Capability of Large Language Models** [[paper](https://arxiv.org/abs/2607.24273)] [[code](https://github.com/FDU-INS/INS-ActBench)]
- [2026] **Gemma 4 Technical Report** [[paper](https://arxiv.org/abs/2607.02770)]
- [2026] **MemOps: Benchmarking Lifecycle Memory Operations in Long-Horizon Conversations** [[paper](https://arxiv.org/abs/2607.12893)]
- [2026] **RUMBA: Russian User Memory Benchmark** [[paper](https://arxiv.org/abs/2607.21447)]
- [2026] **Beyond Multilingual Averages: MTEB-PT, a Benchmark for Portuguese Sentence Encoders** [[paper](https://arxiv.org/abs/2607.04071)]
- [2026] **SWE-Pruner Pro: The Coder LLM Already Knows What to Prune** [[paper](https://arxiv.org/abs/2607.18213)]
- [2026] **XL-DocBench: Benchmarking Evidence-Grounded Extra-Long Document Understanding** [[paper](https://arxiv.org/abs/2608.00036)]
- [2026] **Copy Less, Ground More: Overcoming Repetitive Copying in Long-Context Reasoning via Evidence-Aware Reinforcement Learning** [[paper](https://arxiv.org/abs/2607.19345)]
- [2026] **Multi-Head Recurrent Memory Agents** [[paper](https://arxiv.org/abs/2607.01523)]
- [2026] **DeLS-Spec: Decoupled Long-Short Contexts for Parallel Speculative Drafting** [[paper](https://arxiv.org/abs/2607.07409)]
- [2026] **Enjoy Your Talk: A Human-Centered Benchmark for Multi-Turn Dialogue with Decoupled User Simulation, Target Modeling, and Judging** [[paper](https://arxiv.org/abs/2607.10428)]
- [2026] **Global Merger-Arbitrage Forecasting with Language Models** [[paper](https://arxiv.org/abs/2607.09921)]
- [2026] **Logit-Contribution Scoring Identifies Non-Literal Retrieval Heads** [[paper](https://arxiv.org/abs/2607.01002)]
- [2026] **CoSA: Accelerating Long-Context Inference via Proxy-Kernel Co-Designed Sparse Attention** [[paper](https://arxiv.org/abs/2607.25291)] [[code](https://github.com/Tencent/AngelSlim)]
- [2026] **Studying quantization trade-offs for efficient inference deployment in machine translation** [[paper](https://arxiv.org/abs/2607.29397)]
- [2026] **UniClawBench: A Universal Benchmark for Proactive Agents on Real-World Tasks** [[paper](https://arxiv.org/abs/2607.08768)] [[code](https://github.com/HKU-MMLab/UniClawBench)]
- [2026] **MemDefrag: Latent Memory Defragmentation for Large Language Models** [[paper](https://arxiv.org/abs/2607.05969)]
- [2026] **Inject or Navigate? Token-Efficient Retrieval for LLM Analysis of Transactional Legal Documents** [[paper](https://arxiv.org/abs/2607.05764)]
- [2026] **WildTrace: Benchmarking Natural Evidence Trails in Long-Context Reasoning** [[paper](https://arxiv.org/abs/2607.09328)]
- [2026] **A Sovereign, Open-Source Foundation Model for German and English** [[paper](https://arxiv.org/abs/2607.09424)]
- [2026] **Are the Financial Reasoning from LLMs Credible? A Real World Test over Long-Horizon Statements** [[paper](https://arxiv.org/abs/2607.28661)]
- [2026] **Zero-Mem: Zero-Token Memory Operations for LLM Agents** [[paper](https://arxiv.org/abs/2607.29377)] [[code](https://github.com/TheMoon0815/Zero-mem)]
- [2026] **Agentic Routing: The Harness-Native Data Flywheel** [[paper](https://arxiv.org/abs/2607.11399)]
- [2026] **DominoTree: Conditional Tree-Structured Drafting with Domino for Speculative Decoding** [[paper](https://arxiv.org/abs/2607.08642)]
- [2026] **LongNovel: A Multi-Scale Benchmark for Hallucination Detection in Long-Context Novel Summarization** [[paper](https://arxiv.org/abs/2608.18082)] [[code](https://github.com/BDML-lab/LongNovel)]
- [2026] **moBERTo: A Modern Encoder for Portuguese via Continued Pretraining of ModernBERT** [[paper](https://arxiv.org/abs/2606.22722)] [[project](https://huggingface.co/Tropic-AI/moBERTo)]
- [2026] **Morphing into Hybrid Attention Models** [[paper](https://arxiv.org/abs/2606.30562)]
- [2026] **Beyond Reward Engineering: A Data Recipe for Long-Context Reinforcement Learning** [[paper](https://arxiv.org/abs/2606.18831)]
- [2026] **The Token Tax of Epistemic Accuracy: Comparing RAG and Long-Context Architectures for Document-Grounded Generative AI Applications** [[paper](https://arxiv.org/abs/2606.20898)]
- [2026] **Storyline Trees: Hierarchical Representations for Long-Form Narratives** [[paper](https://arxiv.org/abs/2606.20900)]
- [2026] **Customer-Agent: Overcoming Context Limitations in Ultra-Long Shopping Trajectories via Tool-Augmented Agents and RLVR** [[paper](https://arxiv.org/abs/2606.07995)]
- [2026] **Attention Expansion: Enhancing Keyphrase Extraction from Long Documents with Attention-Augmented Contextualized Embeddings** [[paper](https://arxiv.org/abs/2606.10716)]
- [2026] **QO-Bench: Diagnosing Query-Operator-Preserving Retrieval over Typed Event Tuples** [[paper](https://arxiv.org/abs/2606.04646)]
- [2026] **Randomized YaRN Improves Length Generalization for Long-Context Reasoning** [[paper](https://arxiv.org/abs/2606.23687)]
- [2026] **Mitigating Position Bias in Transformers via Layer-Specific Positional Embedding Scaling** [[paper](https://arxiv.org/abs/2606.27705)]
- [2026] **Dense Contexts Are Hard Contexts: Lexical Density Limits Effective Context in LLMs** [[paper](https://arxiv.org/abs/2606.06203)]
- [2026] **EntSQL: A Benchmark for Grounding Text-to-SQL in Long-Context Enterprise Knowledge** [[paper](https://arxiv.org/abs/2606.03363)]
- [2026] **LEDGER: A Long-Context Benchmark of Corporate Annual Reports for Grounded Financial Retrieval and Extraction** [[paper](https://arxiv.org/abs/2606.13100)]
- [2026] **Memory Retrieval for Changing Preferences** [[paper](https://arxiv.org/abs/2606.02976)]
- [2026] **Scalable Hierarchical Attention Transformers for Multi-Turn Jailbreak Detection in Long Conversations** [[paper](https://arxiv.org/abs/2606.21082)]
- [2026] **EvoEmbedding: Evolvable Representations for Long-Context Retrieval and Agentic Memory** [[paper](https://arxiv.org/abs/2606.21649)] [[project](https://clare-nie.github.io/EvoEmbedding/)]
- [2026] **MemoryDocDataSet: A Benchmark for Joint Conversational Memory and Long Document Reasoning** [[paper](https://arxiv.org/abs/2606.04442)]
- [2026] **GateMem: Benchmarking Memory Governance in Multi-Principal Shared-Memory Agents** [[paper](https://arxiv.org/abs/2606.18829)]
- [2026] **Continual LLM Upcycling: A Predictor-Gated Bank-Wise Sparsity Training Recipe for Dense-to-Sparse LLMs** [[paper](https://arxiv.org/abs/2606.10722)]
- [2026] **Does AI Reviewer See the Full Picture? Attacking and Defending Multimodal Peer Review** [[paper](https://arxiv.org/abs/2606.12716)]
- [2026] **G-Long: Graph-Enhanced Memory Management for Efficient Long-Term Dialogue Agents** [[paper](https://arxiv.org/abs/2606.13115)]
- [2026] **AgentCL: Toward Rigorous Evaluation of Continual Learning in Language Agents** [[paper](https://arxiv.org/abs/2606.02461)]
- [2026] **Modality-Driven Search with Holistic Trace Judging for ARC-AGI-2** [[paper](https://arxiv.org/abs/2606.31543)]
- [2026] **Uncertainty-Aware Hybrid Retrieval for Long-Document RAG** [[paper](https://arxiv.org/abs/2606.13550)]
- [2026] **Transformer-Based Language Models Across Domain Verticals: Architectures, Applications and Critical Assessment** [[paper](https://arxiv.org/abs/2606.24331)]
- [2026] **Lost at the End: Primacy Bias in Multimodal Retrieval-Augmented Question Answering** [[paper](https://arxiv.org/abs/2606.16494)]
- [2026] **Magnifying What Matters: Attention-Guided Adaptive Rendering for Visual Text Comprehension** [[paper](https://arxiv.org/abs/2606.12898)]
- [2026] **Test-Time Training with Next-Token Prediction** [[paper](https://arxiv.org/abs/2606.21803)]
- [2026] **VISTA Architect: A graph database-oriented health AI system demonstrated in multidisciplinary tumor boards** [[paper](https://arxiv.org/abs/2606.22692)]
- [2026] **ATLAS: All-round Testing of Long-context Abilities across Scales** [[paper](https://arxiv.org/abs/2605.28079)]
- [2026] **VibeSearchBench: Benchmarking Long-horizon Proactive Search in the Wild** [[paper](https://arxiv.org/abs/2605.27882)]
- [2026] **ChildEval: When large language models meet children's personalities** [[paper](https://arxiv.org/abs/2605.27805)] [[code](https://github.com/ziyanluo/ChildEval)]
- [2026] **LongTraceRL: Learning Long-Context Reasoning from Search Agent Trajectories with Rubric Rewards** [[paper](https://arxiv.org/abs/2605.31584)] [[code](https://github.com/THU-KEG/LongTraceRL)]
- [2026] **Connecting the Dots: Benchmarking Reflective Memory in Long-Horizon Dialogue** [[paper](https://arxiv.org/abs/2606.01223)]
- [2026] **MemTrace: Tracing and Attributing Errors in Large Language Model Memory Systems** [[paper](https://arxiv.org/abs/2605.28732)] [[code](https://github.com/zjunlp/MemTrace)]
- [2026] **Give it Space! Explicit Disentangling of Positional and Semantic Representations in Encoders** [[paper](https://arxiv.org/abs/2605.30022)]
- [2026] **WorldMemArena: Evaluating Multimodal Agent Memory Through Action-World Interaction** [[paper](https://arxiv.org/abs/2605.29341)]

##### 2024

- [2024] **RULER: What's the Real Context Size of Your Long-Context Language Models?** [[paper](https://arxiv.org/abs/2404.06654)]

##### 2023

- [2023] **LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding** [[paper](https://arxiv.org/abs/2308.14508)]

[⬆ Back to top](#paper-list)

### Surveys & Taxonomies

#### Non-Agentic

##### 2026

- [2026] **Beyond Tokens: A Survey on Decoding Methods for Large Language and Vision-Language Models** [[paper](https://arxiv.org/abs/2608.14797)] [[code](https://github.com/wang2226/Awesome-LLM-Decoding)]
- [2026] **The conditional superiority of fast silicon sampling** [[paper](https://arxiv.org/abs/2608.14079)]
- [2026] **Large Language Models for Low-Resource Languages: A Conceptual Framework for an Electronic Explanatory Dictionary of the Tajik Language** [[paper](https://arxiv.org/abs/2608.04186)]
- [2026] **Memory for Large Language Models** [[paper](https://arxiv.org/abs/2607.25380)]
- [2026] **Multimodal Unlearning Across Vision, Language, Video, and Audio: Survey of Methods, Datasets, and Benchmarks** [[paper](https://arxiv.org/abs/2607.07907)] [[project](https://smsnobin77.github.io/Awesome-Multimodal-Unlearning/)]
- [2026] **Autonomous Information Seeking: A Roadmap for Agentic Recommender Systems** [[paper](https://arxiv.org/abs/2607.04433)]
- [2026] **Accelerating Masked Diffusion Large Language Models: A Survey of Efficient Inference Techniques** *IJCAI-ECAI 2026* [[paper](https://arxiv.org/abs/2607.12829)]
- [2026] **From Question Answering to Task Completion: A Survey on Agent System and Harness Design** [[paper](https://arxiv.org/abs/2606.20683)] [[code](https://github.com/ggjy/Awesome-Agent-Engineering)]
- [2026] **Agent Skill Evaluation and Evolution: Frameworks and Benchmarks** [[paper](https://arxiv.org/abs/2606.11435)] [[code](https://github.com/Cassie07/AgentSkill_Survey)]
- [2026] **Evaluating LLM Usage for Efficient and Explainable Numerical and Classified Implicit Sentiment Analysis of Product Desirability** [[paper](https://arxiv.org/abs/2606.23701)]
- [2026] **Artificial Intelligence for Mathematical Reasoning: An Integrated Survey of Language Models, Neuro-symbolic Systems, and Verified Discovery** [[paper](https://arxiv.org/abs/2606.08728)] [[code](https://github.com/Starscream-11813/awesome-AI4Math)]

##### 2024

- [2024] **A Survey on Efficient Inference for Large Language Models** [[paper](https://arxiv.org/abs/2404.14294)]

[⬆ Back to top](#paper-list)

<!-- END PAPER LIST -->

<!-- BEGIN CORPUS STATISTICS -->

## 📊 Corpus Statistics

**790 papers** across **4 categories**.  
Sources: **arXiv** 435 (55%).  

### Top categories

| Category | Papers | Recent | |
|----------|--------|--------|-|
| application | **393** | 239 | ████████████ |
| method | **260** | 214 | ████████░░░░ |
| evaluation | **113** | 93 | ███░░░░░░░░░ |
| survey | **24** | 14 | █░░░░░░░░░░░ |

### By year

| Year | Papers | |
|------|--------|-|
| 1998 | 1 | █░░░░░░░░░░░ |
| 2000 | 1 | █░░░░░░░░░░░ |
| 2001 | 1 | █░░░░░░░░░░░ |
| 2004 | 1 | █░░░░░░░░░░░ |
| 2008 | 1 | █░░░░░░░░░░░ |
| 2012 | 6 | █░░░░░░░░░░░ |
| 2013 | 1 | █░░░░░░░░░░░ |
| 2014 | 1 | █░░░░░░░░░░░ |
| 2015 | 1 | █░░░░░░░░░░░ |
| 2016 | 2 | █░░░░░░░░░░░ |
| 2017 | 2 | █░░░░░░░░░░░ |
| 2018 | 3 | █░░░░░░░░░░░ |
| 2019 | 4 | █░░░░░░░░░░░ |
| 2020 | 2 | █░░░░░░░░░░░ |
| 2021 | 1 | █░░░░░░░░░░░ |
| 2023 | 11 | █░░░░░░░░░░░ |
| 2024 | 81 | ██░░░░░░░░░░ |
| 2025 | 205 | █████░░░░░░░ |
| 2026 | 464 | ████████████ |

### Momentum (hottest categories)

| Category | Total | Rate | Recent | Score |
|----------|-------|------|--------|-------|
| Evaluation | 113 | 7.8/mo | 82% | 2307 |
| Method | 260 | 17.8/mo | 82% | 1409 |
| Survey | 24 | 1.2/mo | 58% | 1358 |
| Application | 393 | 19.9/mo | 61% | 167 |

### Trending keywords

| Keyword | Papers | Burst |
|---------|--------|-------|
| autonomous | 47 | 1.12 |
| framework | 218 | 1.11 |
| method | 212 | 1.08 |
| analysis | 97 | 1.08 |
| benchmark | 252 | 1.07 |
| system | 232 | 1.06 |
| tool | 65 | 1.04 |
| model | 498 | 1.02 |

### Top venues

| Venue | Papers |
|-------|--------|
| arXiv (Cornell University) | 143 |
| Zenodo (CERN European Organization for Nuclear Research) | 41 |
| Lecture notes in computer science | 14 |
| Proceedings of the AAAI Conference on Artificial Intelligence | 10 |
| MED | 10 |
| Underline Science Inc. | 8 |
| Preprints.org | 8 |
| SSRN Electronic Journal | 7 |
| Open MIND | 5 |
| Information | 4 |

### Research gaps (thinnest cells)

| Cell | Papers |
|------|--------|
| `survey/` | 3 |
| `survey/hybrid` | 9 |
| `application/non-agentic` | 10 |
| `survey/non-agentic` | 12 |
| `evaluation/hybrid` | 12 |

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
