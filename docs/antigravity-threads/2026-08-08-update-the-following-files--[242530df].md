---
title: "Update the following files:"
date: "2026-08-08"
conversation_id: "242530df-641f-4037-8696-8816c15ec133"
source: "antigravity"
---

# Update the following files:

## User

Update the following files:

1. TargetFile: `/Users/matt/projects/jules-burner/src/staging/auto_pr.ts`
Overwrite: true
CodeContent:
```ts
import { JulesCLI } from "../daemon/jules_cli";
import { StagingValidator, SimulatedDiff } from "./validator";
import { UpstreamPRGate } from "./upstream_pr";
import { KanbanBoard } from "../kanban/board";
import { AuditDatabase } from "../audit/db";
import { execSync } from "child_process";

export interface AutoPRTriggerResult {
  sessionId: string;
  taskTitle: string;
  prUrl?: string;
  status: "PR_CREATED" | "PR_MERGED" | "SKIPPED_DUPLICATE" | "NO_DIFF" | "VALIDATION_FAILED" | "ERROR";
  reason?: string;
}

export class AutoPRTriggerPipeline {
  private julesCLI: JulesCLI;
  private validator: StagingValidator;
  private prGate: UpstreamPRGate;
  private kanban: KanbanBoard;
  private db: AuditDatabase;

  constructor(db: AuditDatabase = new AuditDatabase()) {
    this.db = db;
    this.julesCLI = new JulesCLI();
    this.validator = new StagingValidator();
    this.prGate = new UpstreamPRGate();
    this.kanban = new KanbanBoard(db);
  }

  parseRawDiff(diffStr: string): SimulatedDiff {
    const lines = diffStr.split("\n");
    const filesChanged: string[] = [];
    const deletedFiles: string[] = [];
    const addedContent: string[] = [];

    for (const line of lines) {
      if (line.startsWith("--- a/")) {
        const file = line.replace("--- a/", "").trim();
        if (diffStr.includes(`+++ /dev/null`)) {
          deletedFiles.push(file);
        }
      } else if (line.startsWith("+++ b/")) {
        const file = line.replace("+++ b/", "").trim();
        if (!filesChanged.includes(file)) {
          filesChanged.push(file);
        }
      } else if (line.startsWith("+") && !line.startsWith("+++")) {
        addedContent.push(line.substring(1));
      }
    }

    return {
      filesChanged,
      deletedFiles,
      hasBinaryBlobs: diffStr.includes("Binary files differ"),
      addedContent,
    };
  }

  async processUniqueCompletedSessions()
<truncated 3820 bytes>
onId: session.id,
            taskTitle: title,
            prUrl,
            status: "PR_MERGED",
          });
        } catch (gitErr: any) {
          console.error(`[AutoPRPipeline] Error creating PR for session ${session.id}:`, gitErr.message);
          results.push({
            sessionId: session.id,
            taskTitle: title,
            status: "ERROR",
            reason: gitErr.message,
          });
        } finally {
          execSync(`git checkout main`, { stdio: "pipe" });
        }
      } catch (err: any) {
        results.push({
          sessionId: session.id,
          taskTitle: title,
          status: "ERROR",
          reason: err.message,
        });
      }
    }

    this.kanban.saveMarkdownBoardFile();
    return results;
  }
}
```

2. TargetFile: `/Users/matt/projects/jules-burner/src/index.ts`
Overwrite: true
CodeContent:
```ts
import { Dispatcher } from "./daemon/dispatcher";
import { fetchNextBountyCandidate } from "./discovery/miner";
import { AutoPRTriggerPipeline } from "./staging/auto_pr";

const dispatcher = new Dispatcher({ taskProvider: fetchNextBountyCandidate });
const autoPR = new AutoPRTriggerPipeline();

let isRunning = true;

async function autoPRLoop() {
  while (isRunning) {
    try {
      await autoPR.processUniqueCompletedSessions();
    } catch (err) {
      console.error("[AutoPRLoop] Error processing completed sessions:", err);
    }
    await new Promise((r) => setTimeout(r, 60000));
  }
}

async function shutdown() {
  console.log("Shutting down...");
  isRunning = false;
  dispatcher.stopLoop();
  process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

console.log("Starting Jules Burner with Auto-PR & Merge Loop...");
dispatcher.startLoop().catch((err) => {
  console.error("Dispatcher loop error:", err);
  process.exit(1);
});

autoPRLoop().catch((err) => {
  console.error("AutoPR loop error:", err);
});
```

---
