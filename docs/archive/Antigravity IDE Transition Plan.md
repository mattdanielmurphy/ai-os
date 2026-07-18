# Product Requirements Document: AI-OS Context Controller (Phase 1 Focus)

This high-level plan outlines the core mechanics and user experience for **Phase 1**, optimizing your workflow within a unified VSCode environment using the existing file-based Kanban plugin and a highly restricted execution protocol.

---

## 1. The Trigger

The workflow is initiated by the user through a combination of manual task curation and a specialized IDE chat macro.

- **Task Selection:** The user moves a specific markdown task file to the `in progress` column using the existing Kanban plugin interface.
- **The AI Call:** The user opens the built-in IDE chat pane and inputs a single, highly standardized slash command (e.g., `/run-task`).
- **The Initialization:** This slash command serves as the singular ignition point. The user does not write custom prompts directly into the chat window; the command itself signals the system to begin.

---

## 2. The Staging Area

Before any generation or modification occurs, a lightweight, predictable context gathering stage executes instantly in the background.

- **Task Retrieval:** The system runs a local bash utility that automatically scans the Kanban data directory, looks for the file marked `status: "in-progress"`, and reads its contents.
- **Context Isolation:** The staging utility pulls the frontmatter metadata (ID, priority, labels) and the raw markdown task description, packaging it as the singular source of truth for the upcoming work.
- **Workspace Filtering:** The system establishes a strict execution perimeter based on the project folder relevant to that card, conceptually masking out the rest of the massive monolith workspace to keep searches clean and focused.

---

## 3. Task Configuration

To maximize the value of the built-in chat quota, strict guardrails and constraints are applied to the agent's behavior prior to execution.

- **Token-Preservation Protocol (`GEMINI.md`):** A robust set of structural rules is injected to dictate exactly _how_ the agent is permitted to think.
- **The Reading Ban:** The agent is explicitly barred from performing default, unprompted workspace scans or reading entire files on its own.
- **Sub-Agent Delegation:** The primary chat agent is configured to act strictly as a high-level manager. It must coordinate complex tasks by spinning out smaller, specialized sub-agents or calling specific, cheap, third-party API functions rather than consuming large context windows directly.

---

## 4. Execution & Feedback

Once configured, the task enters the active execution phase, providing clear runtime visibility to the user.

- **Targeted Execution:** The agent executes the task strictly within the boundaries of the extracted Kanban markdown file, requesting specific code blocks or line ranges only as absolutely necessary.
- **Real-Time Progress:** The user watches the step-by-step progress directly inside the native IDE chat window as the agent coordinates its sub-tasks and echoes its actions.
- **Completion Signpost:** The process finishes when the agent completes the work described in the card, reports its changes, and awaits human verification. The user can then manually shift the card to `completed` on the board.

---

# Product Requirements Document: AI-OS Context Controller (Phase 1 Focus)

This high-level plan outlines the core mechanics and user experience for **Phase 1**, optimizing your workflow within a unified VSCode environment using the existing file-based Kanban plugin and a highly restricted execution protocol.

---

## 1. The Trigger

The workflow is initiated by the user through a combination of manual task curation and a specialized IDE chat macro.

- **Task Selection:** The user moves a specific markdown task file to the `in progress` column using the existing Kanban plugin interface.
- **The AI Call:** The user opens the built-in IDE chat pane and inputs a single, highly standardized slash command (e.g., `/run-task`).
- **The Initialization:** This slash command serves as the singular ignition point. The user does not write custom prompts directly into the chat window; the command itself signals the system to begin.

---

## 2. The Staging Area

Before any generation or modification occurs, a lightweight, predictable context gathering stage executes instantly in the background.

- **Task Retrieval:** The system runs a local bash utility that automatically scans the Kanban data directory, looks for the file marked `status: "in-progress"`, and reads its contents.
- **Context Isolation:** The staging utility pulls the frontmatter metadata (ID, priority, labels) and the raw markdown task description, packaging it as the singular source of truth for the upcoming work.
- **Workspace Filtering:** The system establishes a strict execution perimeter based on the project folder relevant to that card, conceptually masking out the rest of the massive monolith workspace to keep searches clean and focused.

---

## 3. Task Configuration

To maximize the value of the built-in chat quota, strict guardrails and constraints are applied to the agent's behavior prior to execution.

- **Token-Preservation Protocol (`GEMINI.md`):** A robust set of structural rules is injected to dictate exactly _how_ the agent is permitted to think.
- **The Reading Ban:** The agent is explicitly barred from performing default, unprompted workspace scans or reading entire files on its own.
- **Sub-Agent Delegation:** The primary chat agent is configured to act strictly as a high-level manager. It must coordinate complex tasks by spinning out smaller, specialized sub-agents or calling specific, cheap, third-party API functions rather than consuming large context windows directly.

---

## 4. Execution & Feedback

Once configured, the task enters the active execution phase, providing clear runtime visibility to the user.

- **Targeted Execution:** The agent executes the task strictly within the boundaries of the extracted Kanban markdown file, requesting specific code blocks or line ranges only as absolutely necessary.
- **Real-Time Progress:** The user watches the step-by-step progress directly inside the native IDE chat window as the agent coordinates its sub-tasks and echoes its actions.
- **Completion Signpost:** The process finishes when the agent completes the work described in the card, reports its changes, and awaits human verification. The user can then manually shift the card to `completed` on the board.

---

## Phase 2 Outlook: Custom Native Editor Kanban

Phase 2 will completely bypass standard webviews and HTML rendering. Instead, it will use VSCode's native text surfaces (like custom text decorators, virtual documents, or a native Tree View panel) to represent the Kanban structure.

Your files are your interface. Moving a card means modifying its text state, and the entire board runs at the speed of your native editor shortcuts, multi-cursors, and vim bindings—giving you a 100% text-driven workflow with zero web rendering overhead.
