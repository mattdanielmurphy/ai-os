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

---

[2026-07-02 21:44] User:
Tell me more about smolagents. It seems like a pretty smart thing to do, because agents are better at writing code than specific json objects, right?

---

[2026-07-02 21:44] Assistant:
You have the right intuition. The shift from JSON-based tool calling to code-based agents is one of the most significant architectural changes in agent design right now, and it is the core premise behind Smolagents.  
Hugging Face

Historically, most agent frameworks relied on JSON schemas. When the agent wanted to take an action, it had to output a rigidly formatted JSON object. The framework would parse it, run the tool, and feed the result back to the model.  
Morph

Here is why having the model write raw Python code instead of JSON is highly advantageous:

1. Drastic Reduction in LLM API Calls

If a JSON agent needs to search for five different things, it usually has to output five separate JSON tool calls, wait for the harness to execute each one, and ingest the results across multiple API roundtrips.
A code agent simply writes a `for` loop. It generates a single block of Python that iterates over the queries, executes the search function locally, and aggregates the results in one go. Hugging Face found that this reduces the number of required steps by roughly 30%.  
Morph
+ 1

2. Native Composability and State Management

JSON has no native way to store intermediate variables or pass the output of one tool directly into another. A code agent can assign a variable `data = fetch_api()`, filter it with a list comprehension, and immediately pass the filtered data into `write_file(data)`. The logic happens inside the execution sandbox rather than filling up the LLM's context window.  
Morph

3. Control Flow and Error Handling

Instead of the LLM hallucinating a JSON format that breaks your parser, code agents can write `try/except` blocks. If an API call fails or a file isn't found, the generated Python script can handle the exception locally, perhaps retrying the action, before giving control back to the LLM.  
Morph

4. Leveraging Native Training Data

LLMs are heavily trained on GitHub and massive repositories of Python code. They are inherently better at reasoning through algorithms, logic, and standard libraries in Python than they are at adhering to complex, custom-defined JSON schemas.

The Smolagents Philosophy

Hugging Face built Smolagents around this exact realization. By treating the agent's output as an executable Python script rather than a complex graph of JSON tool calls, they stripped away the bloated abstractions found in older frameworks. The core library is around 1,000 lines of code. It just asks the LLM what to do, executes the Python snippet in a secure sandbox, and feeds the output back into the loop.  
Morph
+ 1
