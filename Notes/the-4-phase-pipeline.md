# The 4-Phase Pipeline

Adding a dedicated brainstorming phase makes perfect sense. Jumping straight into a structured product map can stifle the initial creative exploration.

Here is the revised, four-step prompt framework. It creates a funnel that starts wide and conversational, then progressively locks down the details until you have a machine-ready payload.

### Phase 0: Brainstorming & Ideation

This prompt establishes the LLM as a sounding board. It sets the expectation for a back-and-forth dialogue focused entirely on exploring the concept, identifying use cases, and asking clarifying questions without rushing to a solution.

```text
Act as a technical sounding board. I have an idea for a new feature/project, and we need to brainstorm. 

Do not try to build it, write code, or structure a final plan yet. Your goal is to help me explore the edges of this idea. Ask me clarifying questions about the core problem, the ideal user experience, and potential pitfalls. Let's keep the conversation fluid and conceptual until I tell you we are ready to lock in a plan.

Here is my initial thought: [Insert Idea]
```

### Phase 1: High-Level Plan (UX & Workflow)

Once the brainstorming yields a solid concept, use this prompt to synthesize the conversation into a rigid, non-technical product map.

```text
Act as a Product Manager. We are closing the brainstorming phase. Synthesize our agreed-upon concept into a strict High-Level Plan outlining what this feature DOES and the exact user experience. 

Strictly avoid discussing how it is built under the hood. Structure your response using this exact framework:
1. The Trigger: How the user or system initiates the action.
2. The Staging Area: The intermediate UI, choices, or routing that happens before execution.
3. Task Configuration: The rules, modes, or constraints applied to the task.
4. Execution & Feedback: What happens during the process and how the user knows it finished.
```

### Phase 2: Lower-Level Plan (Architecture & Plumbing)

This bridges the gap between the UX and the terminal. It defines the systems, state management, and communication layers, allowing for highly specific code snippets only if they are critical to the architecture (like an uncommon API endpoint or a specific IPC binding).

```text
Act as a Systems Architect. Translate our approved High-Level Plan into a Lower-Level Technical Plan. 

Focus on the plumbing and architecture. You may include hyper-specific, uncommon code snippets if they are necessary to illustrate an architectural choice (e.g., a specific Rust/Tauri bridge implementation or complex API endpoint), but do not write the standard implementation logic.

Break down the architecture into:
1. Tech Stack & CLI Tools: Required packages or background processes.
2. Component Bridge: How the layers communicate (e.g., file watchers, HTTP, standard I/O).
3. State & Context Management: Where temporary data or files live during execution.
4. Technical Bottlenecks: Highlight 2-3 edge cases or potential fail states to watch out for.
```

### Phase 3: The Execution Payload (Worker Bee)

The final step. This generates the clean, delimiter-wrapped prompt that your userscript can extract and send to your local CLI tool or Worker Bee agent.

```text
Act as a Prompt Engineer. We are ready to execute. Take the High-Level Plan and the Lower-Level Technical Plan and generate a strict, optimized instruction set for a local autonomous AI agent.

Output the final instructions inside a single code block formatted like this:
```claude-instruction
[Instructions here]
```

The instructions must include:
- The target context or directory behavior.
- Strict constraints for the task (e.g., required logging formats, restricted commands).
- A definitive, step-by-step implementation checklist.

Do not include any conversational filler before or after the code block.
```
