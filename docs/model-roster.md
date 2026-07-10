# Active Model List Roster Cheat Sheet

Here is the scannable cheat sheet of your active `model_list` roster, broken down by why each model exists in your configuration and exactly when your orchestrator should deploy them.

---

## Tier 1: The Code Architects & Heavy Reasoners

*Use these when your agent loops hit complex multi-file logic, deep state tracking, or need a massive structural roadmap built from scratch.*

* **`deepseek-v4-pro-high`**
* **When to use:** Deep debugging, raw logic, writing intricate data pipelines, or solving edge cases where small flash models get caught in endless syntax loops.
* **Benefits:** Industry-standard reasoning depth. Maximizes Chain-of-Thought (CoT) tokens to trace backend bugs before outputting code.


* **`glm-5.2-agent`**
* **When to use:** Long-horizon project planning, complex architecture design, and multi-step tool-execution workflows.
* **Benefits:** Currently a top open-weight planning model. It has an exceptional capacity for maintaining complex rule constraints across hundreds of lines of terminal execution without drifting.

---

## Tier 2: The Multi-Modal & Native Search Powerhouses

*Use these when you need to parse visual layout structures (images, UI screenshots), need up-to-the-minute web grounding, or need fallback safety.*

* **`gemini-2.5-pro` (Native) / `gemini-2.5-pro-or` (OpenRouter Fallback)**
* **When to use:** Complex code-to-UI syncing, auditing frontends from design mocks, analyzing large system logs, or hunting down modern breaking changes via the web.
* **Benefits:** High-tier multi-modal image/video reasoning, native **Google Search grounding** for real-time documentation scraping, and a massive context window for massive file payloads.


* **`gemini-2.5-flash` (Native) / `gemini-2.5-flash-or` (OpenRouter Fallback)**
* **When to use:** Rapid UI snapshot checking, fast asset classification, or lightweight web searches during a quick task.
* **Benefits:** Blazing fast execution speeds, cheap token footprint, and excellent visual comprehension for high-frequency agent loops.

---

## Tier 3: The High-Efficiency "Worker Bees" (DeepSeek V4 Flash)

*Your task execution tier. You use different dial settings here to balance speed, cost, and complexity for iterative file writing.*

* **`deepseek-v4-flash-high`**
* **When to use:** Complex inline refactoring, writing algorithms, or filling out a detailed logic block that requires a quick internal reality check.
* **Benefits:** Keeps the high-reasoning budget on to avoid logical fallacies while retaining a fast, cost-effective flash footprint.


* **`deepseek-v4-flash-low`**
* **When to use:** Straightforward multi-line code generation, standard boilerplates, or basic multi-file edits.
* **Benefits:** Limits the internal reasoning loop to save time and token cost while ensuring code structural integrity.


* **`deepseek-v4-flash-off`**
* **When to use:** Repetitive string parsing, JSON structure filling, formatting terminal outputs, or mass file renames.
* **Benefits:** Bypasses the thinking engine completely to deliver pure, snappy, sub-second execution tokens at maximum throughput.

---

## Tier 4: The Budget & Special-Operations Open Weights

*Your optimization roster—ideal for offloading massive workloads, heavy local repo scraping, or leveraging free promotion tiers.*

* **`hy3-free` / `hy3-paid`**
* **When to use:** Highly efficient alternative worker bee for code generation and handling multi-turn constraints.
* **Benefits:** Utilizes a massive underlying 295B MoE framework with speculative decoding for rapid output. It produces compact, precise code structures without the over-generation bloat common in smaller flash variants. (Free tier cascades automatically into the low-cost paid tier fallback).


* **`poolside-laguna-free`**
* **When to use:** Automated test generation, file tree navigation, and repetitive code translation tasks.
* **Benefits:** Free endpoint trained from the ground up exclusively for agentic software development, code-repository interactions, and terminal tooling logic.


* **`nemotron-ultra-free`**
* **When to use:** Feeding entire multi-megabyte project codebases, structural maps, or massive server log outputs directly to a worker.
* **Benefits:** Free 1-million token context window built on a hybrid Transformer-Mamba MoE architecture, making it perfect for massive repository ingestion tasks without hitting walls.
