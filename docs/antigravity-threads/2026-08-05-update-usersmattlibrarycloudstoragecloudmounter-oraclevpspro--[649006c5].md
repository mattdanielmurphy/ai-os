---
title: "Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/daemon/prompter.ts` using `write_to_file`:"
date: "2026-08-05"
conversation_id: "649006c5-165a-4898-a570-3d11ef33243d"
source: "antigravity"
---

# Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/daemon/prompter.ts` using `write_to_file`:

## User

Update `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/daemon/prompter.ts` using `write_to_file`:

Add multi-stage prompt generation support based on task stage:
- **Stage 1 (Research & Plan)**: "DO NOT MODIFY SOURCE CODE FILES. Inspect the repository, locate the bug, write a reproduction script, and produce a detailed step-by-step `IMPLEMENTATION_PLAN.md` with file-by-file diffs."
- **Stage 2 (Staging Fix)**: "Execute the approved `IMPLEMENTATION_PLAN.md`. Write the code fixes, update unit tests, and verify tests pass in the staging environment."
- **Stage 3 (Adversarial Audit)**: "Perform a strict code audit on the changes. Verify no unrelated files were touched, check for subtle regressions, ensure edge case test coverage, and output `AUDIT_REPORT.md` with PASS or REJECT status."
- **Stage 4 (Staging Gate & Pre-Flight)**: "Run full CI test suites, verify lints, build production bundle, and confirm readiness for upstream PR submission."

```typescript
import * as fs from "node:fs";
import * as path from "node:path";
import type { TaskCandidate } from "../discovery/types";

export interface PromptContext {
  task: TaskCandidate | { id: string; title: string; description: string; url?: string; stage?: number; executionStrategy?: string };
  targetRepo?: string;
  auditTag?: string;
  codingStandards?: string[];
  safetyConstraints?: string[];
  requiredTestCoverage?: number;
}

export class PromptPackager {
  private outputDir: string;

  constructor(outputDir = "./tmp/prompts") {
    this.outputDir = outputDir;
  }

  public packagePrompt(ctx: PromptContext): string {
    const auditTag = ctx.auditTag ?? `audit_${Date.now()}_${ctx.task.id}`;
    const stage = ctx.task.stage ?? 1;
    const strategy = ctx.task.executionStrategy ?? "single_pass";

    let stageInstructions = "";
    if (strategy === "staged_4pass" || strategy === "staged_2pass") {
      if (stage === 1) {
        stageInstructions = `
### ⚠️ STAGE 1 MANDATE: RESEARCH & REPRODUCTION ONLY
- **STR
<truncated 1608 bytes>
dy.
`;
      }
    }

    const standards = ctx.codingStandards ?? [
      "Strict TypeScript / Bun runtime compatibility",
      "Comprehensive unit test coverage for new functionality",
      "No breaking changes to public interfaces",
      "Clean git commit message history",
    ];
    const constraints = ctx.safetyConstraints ?? [
      "No raw shell execution with external unverified scripts (curl | bash)",
      "Strict compliance with licensing and safety policies",
      "Isolate modifications strictly to target repository scope",
    ];
    const coverage = ctx.requiredTestCoverage ?? 80;

    return `
# Task Specification: ${ctx.task.title} (Stage ${stage}/${strategy === 'staged_4pass' ? 4 : strategy === 'staged_2pass' ? 2 : 1})
- **Task ID**: ${ctx.task.id}
- **Audit Tag**: ${auditTag}
- **Execution Strategy**: ${strategy}
- **Current Stage**: ${stage}
- **Target Repository**: ${ctx.targetRepo ?? "staging-repo"}

## Objective & Description
${ctx.task.description}

${ctx.task.url ? `**Reference URL**: ${ctx.task.url}\n` : ""}
${stageInstructions}

## Quality Standards & Guidelines
${standards.map(s => `- ${s}`).join("\n")}

## Safety & Compliance Constraints
${constraints.map(c => `- ${c}`).join("\n")}

## Testing Requirements
- Required test coverage: >= ${coverage}%
- All unit and integration tests must pass prior to submission.
`.trim();
  }

  public packageAndSavePrompt(ctx: PromptContext, filename?: string): { promptContent: string; promptFilePath: string } {
    const promptContent = this.packagePrompt(ctx);
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
    const name = filename ?? `prompt_${ctx.task.id}_stage${ctx.task.stage ?? 1}_${Date.now()}.md`;
    const promptFilePath = path.join(this.outputDir, name);
    fs.writeFileSync(promptFilePath, promptContent, "utf-8");
    return { promptContent, promptFilePath };
  }
}
```

---
