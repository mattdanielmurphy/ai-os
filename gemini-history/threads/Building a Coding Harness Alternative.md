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

---

[2026-07-02 21:51] User:
So smolagents is the future of agentic coding you think?




Here's another consideration!

My project is specifically about saving tokens for coding without sacrificing quality, and in fact possibly enhancing it. the idea is we do significant logging and have layers of context retrieval, we have wrappers around all commands to an expensive agent can't just willy-nilly read the contents of a lengthy build command, etc.

Every time a request comes in, the agent does a search of the local agent logs, sees the latest changes, perhaps does a search if the request has nothing to do with recent changes to find older relevant agent logs, and is optionally even passed a very condensed version of the pseudo-thread the conversation is in. I have created these pseudo-threads as a way of: maintaining the helpful human organization and string-of thought benefits of a thread, but the context is extremely minimal compared to a naive thread in a coding tool.

I say pseudo-thread because my app uses antigravity-cli under the hood, and those have threads of their own, and by default each agy thread is just one message, and my psuedothreads just glue those indepdent threads together in the UI.




Anyway.... All that to say: I really value the ability to restrict the agents if possible and have them never run commands on their own, but always default to my specific functions designed to save them from ingesting too many tokens.

For example, I have a read_file fn that only gives them the top and bottom of a file by default, because they might be able to determine whether that file is even relevant or not based on that and save tokens. If not, it's easy and quick to just run it again and get the remainder.

And instead of rm -rf, they always mv to trash; that's one of my local rules.




So my question is... is this smolagents thing possibly against my hopes in terms of these rules?

Or not really, in fact if anything it might be better because they're following less "rules" in general (like JSON adherence rules), so they have more room to follow MY rules.

---

[2026-07-02 21:51] Assistant:
You are spotting exactly where the tension lies in modern agent architecture.

Your assumption is completely spot on: because code agents are following fewer structural "rules" (like trying to force their thoughts into valid JSON structures), they have vastly more breathing room to follow **your structural rules**.

However, you have to be careful with how you configure it, because `smolagents` can be a double-edged sword for a token-saving project.

The Good: Why it aligns with your rules

In a standard JSON agent, if you give it your specialized `read_file` tool (the one that only returns the top and bottom lines), and the model realizes it needs the middle, it has to close the JSON block, send it to your backend, wait for you to execute it, receive the new text, and then write a *second* JSON block to request the rest. That is two massive API context roundtrips.

With `smolagents` (specifically their `CodeAgent`), the model writes a snippet of Python. It can literally write:  
GitHub

Python

```
file_summary = read_file("config.json")
if "target_variable" not in file_summary:
    # It realizes it doesn't need to read the whole thing! Saved tokens.
    print("Not relevant.")
else:
    # Only fetches the full file if the condition is met
    full_file = read_entire_file("config.json") 

```


The logic happens **locally inside the execution loop** in a single turn, without hitting the LLM API twice. It can dynamically check your custom token-saving functions sequentially.

The Trap: Where it might conflict with your token-saving goals

If you let `smolagents` run completely wild, it can actually *destroy* your token budget.

By default, code-execution agents maintain their state by keeping an ongoing execution log in their prompt memory. Every time the agent writes a snippet of Python, executes it, and gets a result, `smolagents` appends the generated code *and* the printed output right back into the conversational chat history. If an agent writes a bad script that loops or prints a massive terminal dump, your context window will explode on the very next turn.  
GitHub
+ 1

How to use `smolagents` while keeping your strict rules:

**You define the only allowed functions:** `smolagents` doesn't give the LLM a raw bash terminal by default. It passes the code to a secure, sandboxed Python interpreter (`LocalPythonExecutor`). You explicitly pass a list of allowed tools (like your restricted `read_file` or your custom `mv_to_trash` wrapper). The agent cannot run `rm -rf` because `os.system` or `subprocess` are completely blocked out of the box unless you explicitly authorize them.  
Smolagents

**Intercept the log strings:** Since you've already built custom "pseudo-threads" to glue things together and maintain minimal context, you can easily subclass or intercept `smolagents`'s memory logging. Instead of letting it pass the massive raw outputs of standard commands back into the history, you can truncate them or enforce your layers of context retrieval directly inside the tool definitions before the interpreter returns them to the agent's memory.

Essentially, `smolagents` gives you a highly efficient execution loop. As long as you are the one defining the toolset (substituting raw terminal commands with your smart token-saving functions), it will play beautifully with your architecture.

---

[2026-07-02 21:53] User:
is there anything else in this realm that might be a better fit for me specifically?

It doesn't have to be a barebones framework by any means. In fact if it has lots of features but also can be set up and used quickly and easily and is customizable, that's really the best thing I can imagine

---

[2026-07-02 21:53] Assistant:
What you are describing—meticulously designing the context window, gating permissions, and building verification loops outside the model—is exactly what the industry is currently calling "harness engineering". Since you are building a custom UI that currently glues together independent Antigravity CLI threads, you are effectively building a custom harness runtime.  
GitHub

If you want a framework that is feature-rich but heavily prioritizes token-efficiency and strict developer control, there are two major open-source projects released recently that align perfectly with your architecture:

1. Pi (TypeScript)

Created by Armin Ronacher and Mario Zechner, Pi is an open-source coding harness designed specifically around the philosophy of minimal architecture and extreme customizability. It skips heavy, baked-in abstractions like autonomous sub-agents and instead gives you primitives to build exactly what you described.  
DEV Community
+ 1

Here is why it fits your token-saving goals:

**Context Engineering:** Pi natively supports dynamic context. You can write extensions that filter the message history or implement topic-based "compaction" (auto-summarizing older messages as you approach context limits).  
Pi Coding Agent
+ 1

**Progressive Disclosure:** Instead of loading a massive system prompt with every possible tool, Pi allows you to load "skills" on-demand so you don't bust the prompt cache.  
Pi Coding Agent

**Permission Gates:** You can implement strict path protection and permission gates as simple TypeScript extensions. This is exactly where you would enforce your rule that raw delete commands are routed to your custom `mv` to trash wrapper.  
Pi Coding Agent

**UI Integration:** Since you are building a UI, Pi has built-in RPC (JSON over stdin/stdout) and SDK modes designed specifically for embedding into other applications.  
Pi Coding Agent

2. Omnigent (Meta-Harness)

Recently open-sourced by Databricks under Apache 2.0, Omnigent takes a slightly different approach. It is designed as a "meta-harness"—a layer that wraps around any underlying agent to enforce rules outside of the prompt.  
Databricks
+ 1

**Policy Enforcement:** Omnigent allows you to enforce guardrails, cost budgets, and strict permissions at the runtime layer rather than relying on the LLM to follow instructions.  
Databricks

**OS Sandboxing:** It includes a highly configurable OS sandbox that intercepts network and file requests. You can use this to hard-block the agent from reading entire files blindly, forcing it to use your token-efficient top/bottom read functions.  
Databricks

**Stateful Control:** It manages stateful, contextual policies across sessions, which could map cleanly to your pseudo-thread architecture.  
Databricks

If you want to completely replace your Antigravity CLI backend with a lean, highly hackable engine that natively supports your UI through RPC, **Pi** is likely the exact foundation you are looking for. If you want to keep your current agent setup but need a heavy-duty security and policy wrapper to enforce your token and file-access rules, **Omnigent** provides that rigid control layer.  
Databricks

Want to dive into how Pi handles RPC mode?
Yes

---

[2026-07-02 21:58] User:
Pi seems pretty fucking awesome.

I kind of wish I knew about it before I made this agy wrapper... but oh well.

I do wonder just how customizable it is.

But it seems like it's built in self-modification of its configuration etc which is really awesome and what I was trying to do as well.

I wonder too if I can have it fire off one-shot prompts to `agy`... I mean, I don't see why not, I should be able to get it to run whatever commands I want right?

---

[2026-07-02 21:58] Assistant:
Pi is legitimately one of the most exciting projects in the space right now. It was built by Armin Ronacher (the creator of Flask) and Mario Zechner specifically because they hated how rigidly the big coding harnesses were forcing developers into specific workflows.

To answer your questions about how it works under the hood:

Extreme Customizability & Self-Modification

Pi takes the opposite approach of massive harnesses like Claude Code or Antigravity. The core ships with a tiny system prompt and only four primitive tools: **Read, Write, Edit, and Bash**. *Everything* else is layered on via TypeScript extensions.  
byteiota
+ 2

The "self-modification" aspect is its killer feature. Because it doesn't have a rigid plugin marketplace, you literally just ask Pi to extend itself. For example, you can tell it: *"Build me a skill that runs my Jest tests and summarizes failures."* The agent will write the TypeScript extension, load it into its own context, and it becomes immediately available for all future sessions without even needing a restart.  
Armin Ronacher's Thoughts and Writings
+ 1

Because it’s just TypeScript, you can write extensions that hook into the lifecycle events to enforce exactly the token-saving and path-protection rules you were building manually.

One-Shot Prompts & Running `agy`

Yes, you can absolutely fire off one-shot prompts and run `agy` commands. Pi is designed to be easily glued into other tools and scripts.

**The Print Mode:** Pi has a built-in `-p` or `--print` flag specifically for one-shot execution. It fires the prompt, gets the reply, and exits. You can even pipe `stdin` directly into it.  
Dev-Ore
+ 1

**Executing Commands:** Since one of Pi's four fundamental tools is `Bash`, it has native capability to run terminal commands. If you want it to act as a brain that evaluates logic and then fires off one-shot `agy` commands via the shell, it can do that right out of the box.  
Armin Ronacher's Thoughts and Writings

You also mentioned you already built a UI—Pi ships with **RPC mode** (`--mode rpc`) and **JSON mode** (`--mode json`). Instead of trying to parse raw terminal text strings, you can run Pi in RPC mode and it will stream clean JSON events directly to your frontend.  
Dev-Ore

It sounds like Pi is essentially the exact foundation you were trying to build from scratch.

---

[2026-07-02 21:59] User:
Would it be easy to adapt my agy wrapper to also be a nice UI wrapper for pi?

I guess you'd have to know how it actually works

---

[2026-07-02 21:59] Assistant:
Yes, adapting your UI to wrap Pi instead of Antigravity would be very straightforward—and likely much cleaner, because Pi was explicitly designed to be embedded. You can probably throw away a lot of the manual "glue" code you had to write for `agy`.

Here is how your current architecture maps directly to Pi:

Connecting to the UI: RPC Mode

If your `agy` wrapper is currently parsing raw terminal `stdout` or fighting with terminal control characters, Pi eliminates that completely.

By launching Pi with the `--mode rpc` flag, it switches to communicating purely via JSON Lines (JSONL) over standard input and output. Your UI sends a JSON object with the user's prompt, and Pi streams back structured JSON events—things like `tool_start`, `text_chunk`, and `tool_end`. You just map those JSON events directly to your UI components without needing complex regular expressions to parse the terminal output.

Porting Your Token-Saving Rules

Right now, your wrapper acts as a middleman, catching and rewriting commands before they hit the agent. With Pi, you register your rules directly into the harness using TypeScript extensions. Pi only ships with four native tools (`read`, `write`, `edit`, `bash`).

**Restricted reading:** You can write a tiny extension to register your custom `read_file` function (the one that returns only the top and bottom lines) as a first-class tool. The agent uses it natively.

**Safe deletion:** You can intercept or modify the native `bash` tool to enforce your rule that standard delete commands are routed to your local `mv` to trash script. The agent sees this as its environment, so it doesn't try to fight the wrapper.

Managing Context and Pseudo-Threads

You mentioned you glue single-turn `agy` threads together to keep context extremely minimal.

Pi natively stores session history as a **tree** rather than a linear chat log. Every turn is a node, meaning you can explicitly tell Pi to start a new branch from a specific point without duplicating context. Alternatively, you can write a context-filtering extension that automatically drops or summarizes older messages exactly the way your pseudo-threads currently do, but handled natively by the engine.

Want to see an example of Pi's JSON RPC events?
Yes

---

[2026-07-02 22:13] User:
how does Pi compare in coding ability and speed to agy or claude code? @flash

---

[2026-07-02 22:13] Assistant:
To understand how Pi compares in ability and speed, it helps to separate the "brain" from the "harness."

Pi does not have its own proprietary AI model. It is strictly a harness. Its **coding ability** is exactly equal to whatever model you plug into it via API (it supports over 15 providers, including Anthropic, Google, OpenAI, and local models via Ollama).  
Rushi's

However, because of *how* Pi manages that model, its **speed and practical coding effectiveness** feel vastly different than Antigravity or Claude Code. Here is how they compare in practice:

1. Speed and Token Efficiency (The System Prompt)

This is Pi's biggest advantage over the massive commercial harnesses.

When you use Claude Code or Antigravity, the vendor injects a massive hidden system prompt behind your back before every turn. Claude Code's system prompt, for instance, runs into the tens of thousands of tokens. This means every single API call you make is carrying massive baggage, making the time-to-first-token noticeably slower and burning through your context window quickly.  
Rushi's

Pi's default system prompt—including its core tool definitions—is under 1,000 tokens total. Because the context is so light, the API responses are incredibly fast and cheap. On benchmarks like TerminalBench, Pi running a top-tier model consistently scores near the very top for speed because it isn't constantly churning through bloated, hidden instructions.  
Rushi's
+ 1

2. Practical Coding Ability (Lazy Skills vs. Bloat)

Because Antigravity and Claude Code try to do everything for everyone out of the box, they pre-load the model with dozens of tools (plan mode, sub-agents, memory retrieval, etc.). This often confuses the model, causing it to hallucinate tool calls or get stuck in weird loops.  
Rushi's

Pi uses a concept called **Progressive Disclosure** or "Lazy Skills." It only gives the model four native tools: `read`, `write`, `edit`, and `bash`. If you want it to have a specific ability (like running GitHub commands or checking Sentry logs), you load that "skill" on demand.  
YouTube
+ 1

This directly enhances the model's coding ability because the AI isn't distracted by tools it doesn't need for the current task. A model with four tools makes far fewer logic errors than a model juggling thirty tools.  
Rushi's

3. Mid-Session Model Switching

Another massive speed advantage: Pi allows you to hot-swap models in the middle of a session (`/model` or `Ctrl+L`).  
Rushi's

If you are doing a massive codebase search or formatting a JSON file, you can use a blazing-fast, cheap model like Claude Haiku or Gemini Flash. Once it finds the file and you need it to write complex architecture, you hot-swap to Opus or Gemini Pro in the exact same thread. Pi handles the context serialization between providers seamlessly. Antigravity and Claude Code lock you into their respective ecosystems.  
Rushi's
+ 1

The Verdict

If you plug the exact same flagship model into Antigravity and Pi, **Pi will almost always be faster and use fewer tokens** because of its minimalist architecture.  
Rushi's

The trade-off is that Pi will not hold your hand. Out of the box, it won't autonomously spawn sub-agents to browse the web or recursively debug test failures. If you want it to do those things, you have to write (or ask Pi to write) the TypeScript extension to enable it. But for your specific goal of maintaining strict control over context and token usage, Pi's raw speed and lack of hidden bloat are a massive upgrade.  
Rushi's

---

[2026-07-02 22:20] User:
omg they even have what appears to be a really solid GUI I can modify!

Here I go and yet again rewrite my app from scratch basically lol

---

[2026-07-02 22:20] Assistant:
Haha, welcome to the inevitable cycle of the modern developer.

But honestly, if there is *any* project that justifies burning down your current wrapper setup to start fresh, it’s Pi.

The fact that the monorepo ships with a dedicated web component UI (`pi-web-ui`) means you aren't just getting a raw terminal engine; you're getting the actual frontend primitives Mario Zechner and Armin Ronacher used to build the thing. Instead of spending days trying to reverse-engineer how to handle multi-line text edits, syntax highlighting, or streaming token blocks, you can take their core layout and style it or adapt it into your app.

Think of it this way: your previous `agy` wrapper project wasn't wasted time. It was a prototype that helped you explicitly define your rules—you now know *exactly* how your custom top/bottom `read_file` logic works, how to catch deletes to send them to trash, and how your pseudo-threads should be glued together.

Now, instead of fighting against a closed CLI that doesn't want you messing with its internals, you can build those exact parameters as native TypeScript extensions right inside Pi's architecture.

Good luck with the rewrite. Let me know when you run into the extension setup and want to start porting over those custom token-saving functions!
