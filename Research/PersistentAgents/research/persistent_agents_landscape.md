# Persistent AI Research Agents Landscape

*Generated on June 05, 2025.*

## Executive Summary
Persistent “thinking” agents are moving from academic prototypes toward commercial usefulness. These systems maintain **open‑ended reasoning loops**, refine their own thoughts, and update deliverables without waiting for new external events.  
Key enablers are (i) *branch‑and‑evaluate* planning (Tree‑of‑Thoughts¹), (ii) *self‑reflection* loops (Reflexion²), and (iii) scalable long‑term memory (MemGPT³).  
Products such as AlphaSense Smart Summaries⁸ and OpenAI Operator⁷ already expose always‑on agents for market research and web automation, yet gaps remain around cost‑efficient memory, automatic self‑evaluation, and guard‑rails—fertile ground for new ventures.

---

## 1. From Chain of Thought to Towers of Thought

| Primitive | What it Adds | Key Paper |
|-----------|--------------|-----------|
| **Tree‑of‑Thoughts** | Branching & backtracking search over thoughts | Yao *et al.* (2023)¹ |
| **Reflexion** | Verbal self‑critique after each trial | Shinn *et al.* (2023)² |
| **MemGPT** | Hierarchical virtual context for ‘infinite’ memory | Packer *et al.* (2023)³ |

---

## 2. Research Prototypes That Already Run for Days

| Prototype | Domain | Persistence Mechanism | Source |
|-----------|--------|-----------------------|--------|
| **Voyager** | Minecraft | Automatic curriculum + skill library | Wang *et al.* (2023)⁴ |
| **Self‑RAG** | QA / summarization | On‑demand retrieval + self‑reflection | Asai *et al.* (2023)⁵ |
| **AutoGPT** | General workflows | Task decomposition loop | GitHub repo |
| **MultiOn “Agent Q”** | Web automation | Tree search + self‑critique | Company blog |

---

## 3. Commercial Products (2025)

| Category | Product | Continuous Capability | Notes |
|----------|---------|-----------------------|-------|
| Decision agents | OpenAI **Operator**⁷ | Browser actions, scheduled tasks | Early research preview |
|  | Adept **ACT‑1**⁶ | Executes SaaS UIs | Enterprise, closed beta |
| Knowledge filters | **AlphaSense** Smart Summaries⁸ | Streams filings, auto‑rewrites briefs | Finance focus |
|  | **Crayon**⁹ | Competitor monitoring, live battlecards | Sales enablement |
|  | **Laser AI**¹⁰ | Living systematic reviews | Health & policy research |
| Personal memory | **Rewind AI**¹¹ | Records desktop, LLM queries over history | Local‑storage privacy |

---

## 4. Build‑Your‑Own Stack

1. **Planner** – Tree‑of‑Thoughts or Reflexion prompt  
2. **Memory** – Redis / vector DB + MemGPT schema  
3. **Orchestrator** – LangGraph or CrewAI  
4. **Tooling** – Browser drivers, email & job‑site APIs  
5. **Scheduler** – Cron, Airflow, or event triggers

---

## 5. Open Problems & Opportunity Areas

| Gap | Pain Today | Opportunity |
|-----|------------|-------------|
| **Memory compression** | Vector DBs balloon | Summarisation & distillation algorithms |
| **Auto‑evaluation** | No benchmark for “depth of reasoning” | Publish leaderboard, sell eval services |
| **Safety & budget control** | Sparse guard‑rails | Policy DSL + simulator |
| **Domain‑specific living reviews** | Only health/finance covered | Vertical SaaS (law, climate, materials) |

---

## 6. Research Brief (for Assistant)

> **Goal:** Catalogue & compare continuous‑reasoning systems.  
> **Tasks:**  
> 1. Feature matrix of >25 systems (planner, memory, actions, safety, price).  
> 2. Summarise ≥15 papers (ToT, Reflexion, Self‑RAG, etc.).  
> 3. Map unsolved challenges; list top 5 labs/startups per challenge.  
> 4. Rank white‑space opportunities by difficulty & market readiness.  
> 5. Deliver Google Sheet + 3‑page memo. Refresh sources weekly.

---

## References
1. Yao, S. *et al.* “Tree of Thoughts: Deliberate Problem Solving with Large Language Models.” arXiv, 2023.  
2. Shinn, N. *et al.* “Reflexion: Language Agents with Verbal Reinforcement Learning.” arXiv, 2023.  
3. Packer, C. *et al.* “MemGPT: Towards LLMs as Operating Systems.” arXiv, 2023.  
4. Wang, G. *et al.* “Voyager: An Open‑Ended Embodied Agent with LLMs.” arXiv, 2023.  
5. Asai, A. *et al.* “Self‑RAG: Learning to Retrieve, Generate, and Critique through Self‑Reflection.” arXiv, 2023.  
6. Adept. “ACT‑1: Transformer for Actions.” 2023.  
7. OpenAI. “Introducing Operator.” 2025.  
8. AlphaSense. “Smart Summaries.” 2024.  
9. Crayon. “Competitive Intelligence Software.” 2025.  
10. Laser AI. “About Laser AI.” 2025.  
11. Rewind AI. “Product Overview.” 2025.
