# Feat: Multi-Phase Gemini Web to Local Execution Planning (high level plan)

Here is the updated high-level workflow, integrating the multi-phase planning pipeline directly into the browser interface alongside the local routing system.

### 1. The Strategy Loop (Browser UI)

The web interface acts as a structured project management and ideation environment, guided by predefined skills and a clear progression path.

- **Slash Command Autocomplete:** Typing `/` within the prompt input box opens a dropdown menu of predefined skills, allowing for the rapid insertion of structured system prompts without manual copying.
- **Phase Selection:** A dedicated UI element allows you to explicitly set the current context of the conversation to one of four distinct stages.
- **Phase Progression Button:** Alongside the standard Submit button, a distinct green "Advance to Next Phase" button pushes the LLM to transition its context and output to the subsequent stage of the workflow.
- **[[The 4-Phase Pipeline]]:**
- **Phase 0: Brainstorming & Ideation:** Exploring concepts, viability, and core objectives.
- **Phase 1: High-Level Plan:** Defining the user experience, workflow, and broad mechanics.
- **Phase 2: Lower-Level Plan:** Mapping out the architecture, plumbing, and specific technical requirements.
- **Phase 3: The Execution Payload:** Generating the strict, formatted instruction set destined for the local worker agent.



### 2. The Trigger (Browser UI to Local Handoff)

Once the LLM completes Phase 3 and outputs the formatted execution payload, the bridge layer takes over.

- **The Action:** An "Execute Locally" button is injected directly adjacent to the Phase 3 code block.
- **The UX:** Clicking the button captures the payload, flashes green to confirm capture, and transmits the payload to your local machine. The browser's responsibility ends here.

### 3. The Staging Area (Local App UI)

The payload reaches your macOS environment but is paused to prevent blind execution. It enters a staging area managed by your AI OS.

- **The Intercept:** A lightweight, Spotlight-style native window appears, displaying a summary of the incoming payload.
- **The Context Router:** The interface prompts you to assign the execution environment by selecting:
- **Recent Workspaces:** A quick-select list of active project directories.
- **Bootstrap New:** An option to scaffold a completely new directory.
- **Scratchpad:** A temporary directory (e.g., `./tmp`) for isolated testing.





### 4. Task Configuration and Execution

Before the payload is handed to the local engine, you define the operational parameters for the task.

- **Mode Selection:** You toggle how the local agent should handle the payload, choosing between Triage Mode to act as an architectural supervisor, or Worker Bee Mode for direct coding contributions.


- **Execution:** Upon confirming the setup, the native popup dismisses, and the local CLI engine spins up in the designated directory.
- **Completion:** The agent performs the task and generates a standardized `.agent-logs/` file to map out the goal, changes, and architectural discoveries.