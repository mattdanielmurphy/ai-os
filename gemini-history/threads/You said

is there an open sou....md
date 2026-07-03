[2026-07-02 21:36] User:
is there an open source coding cli tool as an alternative to the new antigravity build in go?

I have used aider and wasn't impressed. Seems to have a lot of baggage and bloat and it's much slower and worse than antigravity.

Maybe I'm naive but a coding harness doesn't seem like the toughest thing in the world. I'm sure I AM totally ignorant to the complexities of making a tool that's really well suited for the model being used etc. And all the safety and edge cases etc etc.

Anyway I'm making my own coding harness and I feel like there's gotta be some framework out there that is kind of minimalist and customizable etc I can use as a foundation instead of trying to reinvent the wheel from scratch @Pro

---

[2026-07-02 21:36] Assistant:
The transition from the open-source Gemini CLI to the closed-source Antigravity CLI has definitely frustrated a lot of developers, especially with the tighter quotas and the loss of underlying flexibility. It makes sense that you'd want to build something tailored to your own workflow.

You aren't naive for thinking the core of a coding harness shouldn't be overly complicated. The hardest parts are usually context management (filtering which files and functions get sent to the model so you don't blow up the context window) and reliable code patching (ensuring the model's generated diffs apply cleanly to your local files). If you handle those two efficiently, the actual interaction loop is fairly straightforward.

If you want to avoid the overhead and sluggishness of tools like Aider, here are a few minimalist, open-source foundations you can use to build your own CLI harness:

1. Smolagents (Python)

Developed by Hugging Face, this is arguably the best fit if you prioritize a lightweight footprint. It strips away heavy abstractions and relies on a "code-first" approach. Instead of using complex JSON schemas for tool calling, the agents write and execute raw code snippets to solve tasks. It’s highly customizable and has very little internal bloat.

2. PydanticAI (Python)

If you want to write the core execution logic yourself and just need a reliable way to handle the model's inputs and outputs, PydanticAI is extremely lean. It focuses entirely on type-safe, structured responses using standard Pydantic models. It stays out of your way and lets you control the actual terminal workflow.

3. Instructor (Python / TypeScript / Go)

This is even lighter than PydanticAI. It acts as a direct patch over standard API clients to guarantee structured data extraction. If you just need the model to return precise file edits or shell commands without hallucinating the format, Instructor is a fantastic, bare-bones building block.

4. Gollm (Go)

Since you noted Antigravity’s Go implementation is fast, if you want to write your own harness in Go to get that same snappy terminal performance, Gollm is a lightweight Go library. It simplifies LLM interactions without enforcing the heavy, opinionated architecture you'd find in a framework like LangChainGo.

Which programming language are you leaning toward using to write the harness?
