---
title: "Antigravity Slash Command Troubleshooting"
date: "2026-07-31"
conversation_id: "3fb1ad9d-7bc3-437e-808e-eba8398d5bc7"
source: "antigravity"
---

# Antigravity Slash Command Troubleshooting

## User

Investigate why slash commands like /planner are not recognized or executed directly by Antigravity.app (the GUI client app).
Check:
1. System/app configuration files in ~/.gemini/antigravity or app bundles.
2. How Antigravity GUI parses input lines starting with `/` (e.g. built-in slash commands vs skills vs workflows).
3. Search ~/.gemini/config and ~/.gemini/antigravity for workflow registration, slash command definitions, or MCP server configs.
4. Report your findings clearly.

---

## Assistant

Created At: 2026-07-31T15:30:24-06:00
Completed At: 2026-07-31T15:30:29-06:00
{"File":"/Users/matt/.gemini/antigravity/brain/e273c39d-658b-4eec-8cda-f5db8288f3ad/.system_generated/logs/transcript.jsonl","LineNumber":2,"LineContent":"{\"step_index\":2,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:44Z\"}"}
{"File":"/Users/matt/.gemini/antigravity/brain/e273c39d-658b-4eec-8cda-f5db8288f3ad/.system_generated/logs/transcript_full.jsonl","LineNumber":2,"LineContent":"{\"step_index\":2,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:44Z\"}"}
{"File":"/Users/matt/.gemini/antigravity/brain/f11fc49b-dfa0-43f1-a645-1e1ce214d6aa/.system_generated/logs/transcript.jsonl","LineNumber":3,"LineContent":"{\"step_index\":2,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:12Z\",\"tool_calls\":[{\"name\":\"invoke_subagent\",\"args\":{\"Subagents\":\"[{\\\"Model\\\":\\\"flash_lite\\\",\\\"Prompt\\\":\\\"Modify `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/10-tool-calls.js` to change the auto-execute logic at lines 289-292.\\\\n\\\\nCurrent code:\\\\n```javascript\\\\n289: \\\\t\\\\t\\\\t// Auto-execute if requested\\\\n290: \\\\t\\\\t\\\\tif (parsed.run_automatically === true) {\\\\n291: \\\\t\\\\t\\\\t\\\\twindow.executeToolCall(parsed.tool, parsed.args)\\\\n292: \\\\t\\\\t\\\\t}\\\\n```\\\\n\\\\nNew code:\\\\n```javascript\\\\n\\\\t\\\\t\\\\tif (!isInitialScan \u0026\u0026 parsed.run_automatically === true) {\\\\n\\\\t\\\\t\\\\t\\\\twindow.executeToolCall(parsed.tool, parsed.args)\\\\n\\\\t\\\\t\\\\t}\\\\n```\\\\n\\\",\\\"Role\\\":\\\"Code Editor\\\",\\\"TypeName\\\":\\\"self\\\"}]\",\"toolAction\":\"\\\"Editing tool execution logic\\\"\",\"toolSummary\":\"\\\"File modification\\\"\"}}]}"}
{"File":"/Users/matt/.gemini/antigravity/brain/f11fc49b-dfa0-43f1-a645-1e1ce214d6aa/.system_generated/logs/transcript.jsonl","LineNumber":6,"LineConte
<truncated 25922 bytes>
Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/\\\"\",\"WaitMsBeforeAsync\":\"0\",\"toolAction\":\"\\\"Verifying changes\\\"\",\"toolSummary\":\"\\\"Diffing changes\\\"\"}}]}"}
{"File":"/Users/matt/.gemini/antigravity/brain/969ce7a3-82c8-4686-aa4e-463a2f9c8967/.system_generated/logs/transcript.jsonl","LineNumber":12,"LineContent":"{\"step_index\":11,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:14Z\"}"}
{"File":"/Users/matt/.gemini/antigravity/brain/969ce7a3-82c8-4686-aa4e-463a2f9c8967/.system_generated/logs/transcript.jsonl","LineNumber":14,"LineContent":"{\"step_index\":13,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:15Z\"}"}
{"File":"/Users/matt/.gemini/antigravity/brain/969ce7a3-82c8-4686-aa4e-463a2f9c8967/.system_generated/logs/transcript.jsonl","LineNumber":16,"LineContent":"{\"step_index\":15,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:17Z\",\"tool_calls\":[{\"name\":\"run_command\",\"args\":{\"CommandLine\":\"\\\"bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh\\\"\",\"Cwd\":\"\\\"/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/\\\"\",\"WaitMsBeforeAsync\":\"0\",\"toolAction\":\"\\\"Reloading bundle\\\"\",\"toolSummary\":\"\\\"Bundle and reload\\\"\"}}]}"}
{"File":"/Users/matt/.gemini/antigravity/brain/969ce7a3-82c8-4686-aa4e-463a2f9c8967/.system_generated/logs/transcript.jsonl","LineNumber":18,"LineContent":"{\"step_index\":17,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:21Z\"}"}
{"File":"/Users/matt/.gemini/antigravity/brain/969ce7a3-82c8-4686-aa4e-463a2f9c8967/.system_generated/logs/transcript.jsonl","LineNumber":20,"LineContent":"{\"step_index\":19,\"source\":\"MODEL\",\"type\":\"PLANNER_RESPONSE\",\"status\":\"DONE\",\"created_at\":\"2026-07-28T21:00:22Z\"}"}
(...12929 more results not shown)

Created At: 2026-07-31T15:30:30-06:00
Completed At: 2026-07-31T15:30:30-06:00
{"name":".DS_Store","sizeBytes":"10244"}
{"name":"GEMINI.md","sizeBytes":"44"}
{"name":"agyhub_summaries_proto.pb","sizeBytes":"1646090"}
{"name":"annotations","isDir":true}
{"name":"antigravity_state.pbtxt","sizeBytes":"774"}
{"name":"bin","isDir":true}
{"name":"brain","isDir":true}
{"name":"builtin","isDir":true}
{"name":"context_state","isDir":true}
{"name":"conversations","isDir":true}
{"name":"crashes","isDir":true}
{"name":"html_artifacts","isDir":true}
{"name":"implicit","isDir":true}
{"name":"installation_id","sizeBytes":"36"}
{"name":"knowledge","isDir":true}
{"name":"mcp","isDir":true}
{"name":"mcp_config.json","sizeBytes":"51"}
{"name":"scratch","isDir":true}
{"name":"skills","isDir":true}

Summary: This directory contains 13 subdirectories and 6 files.

Created At: 2026-07-31T15:30:31-06:00
Completed At: 2026-07-31T15:30:31-06:00
{"name":".DS_Store","sizeBytes":"6148"}
{"name":".migrated"}
{"name":"config.json","sizeBytes":"2871"}
{"name":"global_workflows","isDir":true}
{"name":"mcp_config.json","sizeBytes":"302"}
{"name":"plugins","isDir":true}
{"name":"projects","isDir":true}
{"name":"settings.json","sizeBytes":"206"}
{"name":"sidecars","isDir":true}
{"name":"skills","isDir":true}

Summary: This directory contains 5 subdirectories and 5 files.

Created At: 2026-07-31T15:30:31-06:00
Completed At: 2026-07-31T15:30:31-06:00
{"name":".DS_Store","sizeBytes":"6148"}
{"name":"audit.md","sizeBytes":"34"}
{"name":"fast.md","sizeBytes":"33"}
{"name":"planner.md","sizeBytes":"599"}
{"name":"start.md","sizeBytes":"34"}
{"name":"strict-delegation.md","sizeBytes":"46"}

Summary: This directory contains 0 subdirectories and 6 files.

Created At: 2026-07-31T15:30:32-06:00
Completed At: 2026-07-31T15:30:32-06:00
File Path: `file:///Users/matt/.gemini/config/global_workflows/planner.md`
Total Lines: 12
Total Bytes: 599
Showing lines 1 to 12
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: description: MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks.
3: name: planner
4: ---
5: 
6: Run high-reasoning planning using the `planner` skill instructions in `/Users/matt/.gemini/config/skills/planner/SKILL.md`.
7: 
8: 1. Do NOT inspect codebase files directly in the main thread.
9: 2. Delegate context pre-fetching to a Flash subagent.
10: 3. Call `agymcp:agy` with model `gemini-3.1-pro-low` (or specified model profile) to author `implementation_plan.md`.
11: 4. Store the returned `SESSION_ID` for Stage 4 QA audit resumption (`agymcp:agy_continue`).
12: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:32-06:00
Completed At: 2026-07-31T15:30:33-06:00
File Path: `file:///Users/matt/.gemini/config/global_workflows/audit.md`
Total Lines: 14
Total Bytes: 1203
Showing lines 1 to 14
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: name: audit
3: description: Perform a token waste audit on the previous conversation transcript.
4: ---
5: 
6: Perform a token waste audit on the previous conversation transcript using the following steps:
7: 
8: 1. **Locate the Transcript**: Identify the previous conversation ID from the agent log directory (`agent-logs/`) by looking at the most recent log file's transcript pointer, or find the second most recent directory in `~/.gemini/antigravity-ide/brain/` or `~/.gemini/antigravity-cli/brain/`. Locate the `transcript_full.jsonl` in that directory.
9: 2. **Run Audit Script**: Execute `python3 scripts/audit_transcripts.py <path-to-transcript_full.jsonl>` to analyze the tool calls and calculate cumulative token waste.
10: 3. **Analyze Findings**:
11:    - Identify the files that were read or edited directly by the orchestrator.
12:    - Describe which steps contributed most to cumulative token waste (e.g., files read early in a long thread).
13: 4. **Propose Optimizations**: Identify specific ways we can modify the system of rules (e.g., in `.agents/AGENTS.md`) and helper functions (like `subagent.py` or shell wrappers) to minimize direct file reads/writes and enforce cheaper delegation to Deepseek or Claude Code.
14: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:33-06:00
Completed At: 2026-07-31T15:30:33-06:00
File Path: `file:///Users/matt/.gemini/config/config.json`
Total Lines: 62
Total Bytes: 2871
Showing lines 1 to 62
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: {
2:   "userSettings": {
3:     "artifactReviewMode": "ARTIFACT_REVIEW_MODE_ALWAYS",
4:     "autoExecutionPolicy": "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER",
5:     "conversationWidth": "CONVERSATION_WIDTH_DEFAULT",
6:     "customThemeSeedsDark": {
7:       "background": "#24273A",
8:       "foregroundOverride": "#CAD3F5",
9:       "primary": "#C6A0F6"
10:     },
11:     "customThemeSeedsLight": {
12:       "background": "#E9E9EB",
13:       "foregroundOverride": "#160C5C",
14:       "primary": "#624DEB"
15:     },
16:     "enableTerminalSandbox": false,
17:     "gcpRegion": "global",
18:     "globalPermissionGrants": {
19:       "allow": [
20:         "command(git commit)",
21:         "command(git add)",
22:         "command(git status)",
23:         "command(git diff)",
24:         "read_file(/Users/matt/Library/LaunchAgents)",
25:         "read_file(/Users/matt/Documents/Scripts/macOS/energy_monitor.sh)",
26:         "write_file(/Users/matt/Documents/Scripts/macOS/energy_monitor.sh)",
27:         "mcp(chrome-devtools/list_pages)",
28:         "mcp(chrome-devtools/evaluate_script)",
29:         "mcp(chrome-devtools/new_page)",
30:         "execute_url(localhost)",
31:         "read_url(github.com)",
32:         "command(ps)",
33:         "command(head)",
34:         "command(killall chronod)",
35:         "command(pkill)",
36:         "command(grep)",
37:         "command(log)",
38:         "command(tail)",
39:         "command(/usr/bin/log)",
40:         "unsandboxed(git -C /Users/matt/projects/hermes-agent diff origin/main --name-only)",
41:         "unsandboxed(git -C /Users/matt/projects/hermes-agent log --oneline origin/main..HEAD)",
42:         "unsandboxed(git -C /Users/matt/projects/hermes-agent show --stat b21785647 9c68ef28a fec526907 d34c7eb16 d229e43f9 d10b45cdb c642d845b 767768399 c9825bcb2 cf6bfdac6 e183a0b47 de98e0f9c 2\u003e\u00261)",
43:         "unsandboxed(head)",
44:         "unsandboxed(git -C /Users/matt/projects/hermes-agent show --stat cf6bfdac6 e183a0b47 de98e0f9c 2\u003e\u00261)",
45:         "unsandboxed(git -C /Users/matt/projects/hermes-agent diff origin/main -- agent/conversation_loop.py agent/auxiliary_client.py hermes_cli/auth.py hermes_cli/providers.py hermes_cli/model_switch.py hermes_cli/runtime_provider.py 2\u003e\u00261)",
46:         "unsandboxed(git -C /Users/matt/projects/hermes-agent diff origin/main -- agent/auxiliary_client.py hermes_cli/web_server.py 2\u003e\u00261)",
47:         "unsandboxed(ls)",
48:         "mcp(chrome-devtools/navigate_page)",
49:         "execute_url(gemini.google.com)",
50:         "mcp(chrome-devtools/list_console_messages)",
51:         "mcp(chrome-devtools/wait_for)",
52:         "mcp(chrome-devtools/take_screenshot)",
53:         "read_url(developer.spotify.com)"
54:       ]
55:     },
56:     "nonWorkspaceFileAccessPolicy": "AGENT_SETTING_POLICY_ALLOW",
57:     "queuedMessageDeliveryStrategy": "MESSAGE_DELIVERY_STRATEGY_NEXT_INVOCATION",
58:     "remoteControlHostname": "matt-local-silent-dust",
59:     "themeMode": "THEME_MODE_INHERIT",
60:     "useAiCredits": true
61:   }
62: }
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:34-06:00
Completed At: 2026-07-31T15:30:34-06:00
File Path: `file:///Users/matt/.gemini/config/settings.json`
Total Lines: 11
Total Bytes: 206
Showing lines 1 to 11
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: {
2:   "permissions": {
3:     "deny": [
4:       "invoke_subagent",
5:       "custom(invoke_subagent)"
6:     ]
7:   },
8:   "autoExecutionPolicy": "CASCADE_COMMANDS_AUTO_EXECUTION_STRICT",
9:   "toolExecutionPolicy": "strict"
10: }
11: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:34-06:00
Completed At: 2026-07-31T15:30:34-06:00
File Path: `file:///Users/matt/.gemini/antigravity/antigravity_state.pbtxt`
Total Lines: 29
Total Bytes: 774
Showing lines 1 to 29
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: post_onboarding: {
2:   completed_steps: POST_ONBOARDING_STEP_TYPE_MANAGER_WELCOME
3:   completed_steps: POST_ONBOARDING_STEP_TYPE_USAGE_MODE
4:   completed_steps: POST_ONBOARDING_STEP_TYPE_AGENT_CONFIGURATION
5:   completed_steps: POST_ONBOARDING_STEP_TYPE_ADD_WORKSPACE
6: }
7: seen_nuxs: {
8:   uids: 24
9:   uids: 26
10:   uids: 27
11:   uids: 23
12:   uids: 25
13:   uids: 29
14:   uids: 31
15: }
16: agent_onboarding_completed: AGENT_ONBOARDING_STATE_COMPLETED
17: last_selected_agent_model: MODEL_PLACEHOLDER_M73
18: migrate_convos_into_projects: MIGRATION_STATUS_COMPLETED
19: installation_uuid: "8580cfac-9264-418c-bd2f-56bf047bcf32"
20: migrate_retroactive_projects: RETROACTIVE_MIGRATION_STATUS_COMPLETED_RAN
21: migrations: {
22:   key: 2
23:   value: MIGRATION_STATUS_COMPLETED
24: }
25: migrations: {
26:   key: 3
27:   value: MIGRATION_STATUS_COMPLETED
28: }
29: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:35-06:00
Completed At: 2026-07-31T15:30:35-06:00
{"name":"Contents","isDir":true}

Summary: This directory contains 1 subdirectories and 0 files.

Created At: 2026-07-31T15:30:36-06:00
Completed At: 2026-07-31T15:30:36-06:00
{"name":"CodeResources","sizeBytes":"1989"}
{"name":"Frameworks","isDir":true}
{"name":"Info.plist","sizeBytes":"3335"}
{"name":"MacOS","isDir":true}
{"name":"PkgInfo","sizeBytes":"8"}
{"name":"Resources","isDir":true}
{"name":"_CodeSignature","isDir":true}

Summary: This directory contains 4 subdirectories and 3 files.

Created At: 2026-07-31T15:30:37-06:00
Completed At: 2026-07-31T15:30:37-06:00
{"name":"af.lproj","isDir":true}
{"name":"am.lproj","isDir":true}
{"name":"app-update.yml","sizeBytes":"147"}
{"name":"app.asar","sizeBytes":"2114856"}
{"name":"app.asar.unpacked","isDir":true}
{"name":"ar.lproj","isDir":true}
{"name":"bg.lproj","isDir":true}
{"name":"bin","isDir":true}
{"name":"bn.lproj","isDir":true}
{"name":"ca.lproj","isDir":true}
{"name":"cs.lproj","isDir":true}
{"name":"da.lproj","isDir":true}
{"name":"de.lproj","isDir":true}
{"name":"el.lproj","isDir":true}
{"name":"en.lproj","isDir":true}
{"name":"en_GB.lproj","isDir":true}
{"name":"es.lproj","isDir":true}
{"name":"es_419.lproj","isDir":true}
{"name":"et.lproj","isDir":true}
{"name":"fa.lproj","isDir":true}
{"name":"fi.lproj","isDir":true}
{"name":"fil.lproj","isDir":true}
{"name":"fr.lproj","isDir":true}
{"name":"gu.lproj","isDir":true}
{"name":"he.lproj","isDir":true}
{"name":"hi.lproj","isDir":true}
{"name":"hr.lproj","isDir":true}
{"name":"hu.lproj","isDir":true}
{"name":"icon.icns","sizeBytes":"149929"}
{"name":"id.lproj","isDir":true}
{"name":"it.lproj","isDir":true}
{"name":"ja.lproj","isDir":true}
{"name":"kn.lproj","isDir":true}
{"name":"ko.lproj","isDir":true}
{"name":"lt.lproj","isDir":true}
{"name":"lv.lproj","isDir":true}
{"name":"ml.lproj","isDir":true}
{"name":"mr.lproj","isDir":true}
{"name":"ms.lproj","isDir":true}
{"name":"nb.lproj","isDir":true}
{"name":"nl.lproj","isDir":true}
{"name":"pl.lproj","isDir":true}
{"name":"pt_BR.lproj","isDir":true}
{"name":"pt_PT.lproj","isDir":true}
{"name":"ro.lproj","isDir":true}
{"name":"ru.lproj","isDir":true}
{"name":"sk.lproj","isDir":true}
{"name":"sl.lproj","isDir":true}
{"name":"sr.lproj","isDir":true}
{"name":"sv.lproj","isDir":true}
{"name":"sw.lproj","isDir":true}
{"name":"ta.lproj","isDir":true}
{"name":"te.lproj","isDir":true}
{"name":"th.lproj","isDir":true}
{"name":"tr.lproj","isDir":true}
{"name":"uk.lproj","isDir":true}
{"name":"ur.lproj","isDir":true}
{"name":"vi.lproj","isDir":true}
{"name":"zh_CN.lproj","isDir":true}
{"name":"zh_TW.lproj","isDir":true}

Summary: This directory contains 57 subdirectories and 3 files.

Created At: 2026-07-31T15:30:37-06:00
Completed At: 2026-07-31T15:30:37-06:00
{"name":"node_modules","isDir":true}

Summary: This directory contains 1 subdirectories and 0 files.

Created At: 2026-07-31T15:30:38-06:00
Completed At: 2026-07-31T15:30:38-06:00
{"name":"language_server","sizeBytes":"138112640"}
{"name":"webm_encoder","sizeBytes":"13584144"}

Summary: This directory contains 0 subdirectories and 2 files.

Created At: 2026-07-31T15:30:39-06:00
Completed At: 2026-07-31T15:30:39-06:00
{"name":"agy-customizations","isDir":true}
{"name":"antigravity_guide","isDir":true}
{"name":"permissioned-github","isDir":true}

Summary: This directory contains 3 subdirectories and 0 files.

Created At: 2026-07-31T15:30:39-06:00
Completed At: 2026-07-31T15:30:39-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/SKILL.md`
Total Lines: 55
Total Bytes: 2955
Showing lines 1 to 55
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: name: antigravity-guide
3: description: Provides a comprehensive guide, quick reference, and sitemap for Google Antigravity (AGY), including the Antigravity CLI (agy), Antigravity 2.0, Antigravity IDE, Python SDK, slash commands, keybindings, and customizations (skills, rules, MCP, sidecars). Activate this skill when the user asks questions about how to use, configure, or customize Antigravity, AGY, the agy CLI, the Antigravity IDE, or Antigravity 2.0.
4: ---
5: 
6: # Google Antigravity (AGY) Guide & Sitemap
7: 
8: Google Antigravity is an AI-first development platform. Depending on which
9: surface the user is asking about, you **MUST** read the corresponding
10: subdocumentation in the `references/` directory of this skill:
11: 
12: ## 1. Surfaces Sitemap (Offline Subdocs)
13: 
14: -   **Antigravity CLI (`agy`)**: [references/cli.md](references/cli.md)
15:     -   Pointers to the authoritative public CLI docs for slash commands,
16:         features, settings, and best practices.
17: -   **Antigravity IDE**: [references/ide.md](references/ide.md)
18:     -   Covers the standalone AI-first IDE, sidebar chat panels, and inline code
19:         lenses.
20: -   **Antigravity 2.0**: [references/app.md](references/app.md)
21:     -   Covers the parallel desktop application, left-hand sidebar, chat canvas,
22:         and the HTML Auxiliary Pane (Subagents, Background Tasks, Artifacts,
23:         Files Changed, Terminals).
24: -   **Antigravity SDK**: [references/sdk.md](references/sdk.md)
25:     -   Covers the public Python SDK
26:         (https://github.com/google-antigravity/antigravity-sdk-python) for
27:         programmatic agent leasing, orchestration APIs, and custom tool
28:         exposing.
29: 
30: --------------------------------------------------------------------------------
31: 
32: ## 2. Smart Hybrid Retrieval: When to Fetch Live Docs
33: 
34: The offline subdocs provide excellent quick references. However, if the user
35: asks for the latest updates, advanced Vertex AI integrations, or complex setups
36: not covered here, you **MUST** dynamically fetch the live page from the official
37: sitemap:
38: 
39: <!-- LINT.IfChange(sitemap) -->
40: 
41: -   **Main Documentation Home**: `https://antigravity.google/docs`
42: -   **Skills**: `https://antigravity.google/docs/skills`
43: -   **Rules**: `https://antigravity.google/docs/rules-workflows`
44: -   **Hooks**: `https://antigravity.google/docs/hooks`
45: -   **Plugins**: `https://antigravity.google/docs/plugins`
46: -   **Sidecars**: `https://antigravity.google/docs/sidecars`
47: -   **Model Context Protocol (MCP)**: `https://antigravity.google/docs/mcp`
48: -   **Browser Automation & Testing**:
49:     `https://antigravity.google/docs/ide/browser`
50: -   **Agent Permissions & Security**:
51:     `https://antigravity.google/docs/permissions`
52: -   **Changelog & Release Notes**: `https://antigravity.google/changelog`
53: -   **Troubleshooting & Support**: `https://antigravity.google/support`
54:     <!-- LINT.ThenChange(//depot/google3/third_party/gemini_coder/agent_ui_toolkit/dev/appVariant/externalAppVariant.ts:custom_links) -->
55: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:40-06:00
Completed At: 2026-07-31T15:30:40-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/references/cli.md`
Total Lines: 42
Total Bytes: 1686
Showing lines 1 to 42
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Antigravity CLI (`agy`) Reference
2: 
3: The Antigravity CLI (`agy`) is a lightweight, terminal-based interface for fast
4: agent interaction. For full details, always consult the live public
5: documentation:
6: 
7: -   **CLI Features & Subagents**: `https://antigravity.google/docs/cli/features`
8: -   **CLI Best Practices**: `https://antigravity.google/docs/cli/best-practices`
9: -   **CLI Reference**: `https://antigravity.google/docs/cli/reference`
10: 
11: When the user asks about CLI specifics, **fetch the relevant page above** for
12: authoritative, up-to-date information.
13: 
14: --------------------------------------------------------------------------------
15: 
16: ## 1. Getting Started
17: 
18: -   **Launch**: Run `agy` to start the CLI.
19: -   **Authentication**: On first run, follow the on-screen prompts to
20:     authenticate. See `https://antigravity.google/docs/cli/reference` for
21:     details.
22: -   **Exit**: `Ctrl+D Ctrl+D` (or `/exit` or `/quit`).
23: 
24: --------------------------------------------------------------------------------
25: 
26: ## 2. CLI Slash Commands
27: 
28: -   **CLI flags & subcommands**: Run `agy --help` to see all command-line flags
29:     and subcommands.
30: -   **Slash commands** (inside the TUI): Launch `agy` and run `/help` to see all
31:     available slash commands.
32: -   **Full reference**: Fetch `https://antigravity.google/docs/cli/reference`
33:     for the authoritative list of all slash commands and CLI options.
34: 
35: --------------------------------------------------------------------------------
36: 
37: ## 3. Configuration
38: 
39: The CLI is configured via **`~/.gemini/antigravity-cli/settings.json`**. For the
40: full list of settings keys, types, and defaults, fetch the live docs:
41: `https://antigravity.google/docs/cli/reference`
42: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:40-06:00
Completed At: 2026-07-31T15:30:40-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/references/app.md`
Total Lines: 88
Total Bytes: 3852
Showing lines 1 to 88
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Antigravity 2.0 Reference
2: 
3: Antigravity 2.0 is a desktop Electron application that can launch and monitor
4: agents on your machine. It provides a unified platform to orchestrate agent
5: activities independently of an IDE.
6: 
7: ## 1. Unified Interface Surfaces
8: 
9: ### Left-hand Sidebar
10: 
11: -   **New Conversation**: Start a new chat session with the agent.
12: -   **Projects**: Manage and switch between different workspaces or
13:     repositories.
14: -   **Scheduled Tasks**: Define, monitor, and run recurring background tasks
15:     (cron) and one-time delayed timers.
16: -   **Skills & Customizations**: View and manage active skills, rules, plugins,
17:     and MCP servers.
18: -   **Settings**: Configure application preferences, model selection, and
19:     permissions.
20: 
21: ### Chat Canvas
22: 
23: The main panel for direct agent interaction, planning, and task execution.
24: 
25: -   **Slash Commands**: Type `/` to invoke built-in workflows. Slash commands
26:     trigger specialized agent behaviors or launch dedicated subagents. Each
27:     slash command has a description in the menu.
28: -   **@ Mentions**: Type `@` to open the mention menu and attach context
29:     directly to your message. Supported categories include files and folders,
30:     previous conversations, terminal sessions, rules, and MCP servers/tools.
31: -   **Media Uploads**: Drag-and-drop or paste images and files into the chat
32:     canvas to share them with the agent. Uploaded media is included as context
33:     for the current messag
<truncated 661 bytes>
     environment for added security.
51: -   **Non-Workspace File Access**: Controls whether the agent can read or write
52:     files outside the current workspace root (`allow`, `ask`, `deny`).
53: -   **Internet Access Policy**: Controls whether the agent can make network
54:     requests (`allow`, `ask`, `deny`).
55: -   **Permission Grants**: Define global allow/deny rules for specific files,
56:     commands, and URLs.
57: -   **Command Allowlist / Denylist**: Specify terminal commands that are always
58:     permitted or always blocked.
59: -   **Browser Allowlist**: Restrict which domains the agent's browser tools can
60:     navigate to.
61: -   **Artifact Review Mode**: Controls when the agent asks for artifact review
62:     (`always-proceed`, `agent-decides`, `asks-for-review`).
63: -   **Notifications**: Enable system notifications on task completion.
64: -   **Appearance**: Theme mode and conversation width.
65: -   **App Settings**: Keep computer awake, run in background, and auto-check
66:     for updates.
67: 
68: ### Project-Level Settings
69: 
70: Each project can override a subset of global settings. Project-level settings
71: take priority over their global counterparts when a project is active:
72: 
73: -   **File Access Policy**: Override the non-workspace file access policy for
74:     this project.
75: -   **Internet Access Policy**: Override the internet access policy for this
76:     project.
77: -   **Sandbox Mode**: Enable or disable terminal sandboxing per project.
78: -   **Auto-Execution Policy**: Override the tool execution policy for this
79:     project.
80: -   **Artifact Review Mode**: Override artifact review behavior per project.
81: -   **Permission Grants**: Define project-scoped permission grants that apply
82:     only within the project's workspace.
83: 
84: ## 3. Further Reading
85: 
86: For all other questions, search the live documentation at
87: `https://antigravity.google/docs`.
88: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:41-06:00
Completed At: 2026-07-31T15:30:41-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/references/ide.md`
Total Lines: 77
Total Bytes: 3399
Showing lines 1 to 77
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Antigravity IDE Reference
2: 
3: Antigravity IDE is a standalone, AI-first integrated development environment
4: (built on VS Code) that integrates agentic workflows directly into your coding
5: environment.
6: 
7: > [!NOTE] Antigravity IDE coexists with **Antigravity 2.0**. While the IDE
8: > provides an in-editor integrated experience, Antigravity 2.0 offers a parallel
9: > desktop application. Both are fully supported and share the same underlying
10: > agentic capabilities. See [references/app.md](references/app.md) for details
11: > on Antigravity 2.0.
12: 
13: ## 1. Core AI Modalities
14: 
15: Antigravity IDE offers three distinct ways to interact with AI, depending on the
16: task:
17: 
18: ### A. Passive: Antigravity Tab (Autocomplete)
19: 
20: A next-intent prediction experience routed to a single keystroke.
21: 
22: -   **Context-Aware Suggestions**: Proposes insertions, deletions, edits,
23:     imports, and cursor movements based on surrounding code, open tabs, terminal
24:     output, and clipboard (optional).
25: -   **Autocomplete & Supercomplete**: Autocomplete suggests code at the cursor.
26:     Supercomplete suggests larger diffs (including deletions) in floating
27:     windows.
28: -   **Tab to Jump**: Anticipates your next navigation point and lets you jump
29:     there by pressing <kbd>tab</kbd>.
30: -   **Tab to Import**: Automatically adds necessary imports at the top of the
31:     file when a new dependency is used.
32: -   **Controls**: Accept with <kbd>tab</kbd>, cancel with <kbd>esc</kbd>, or
33:     accept 
<truncated 164 bytes>
>+<kbd>I</kbd> / <kbd>Ctrl</kbd>+<kbd>I</kbd>)
37: 
38: An instructive inline modality for localized edits.
39: 
40: -   **Targeted Edits**: Highlight a block of code and press the shortcut to
41:     refactor, explain, or modify it. The AI will only edit the highlighted
42:     block.
43: -   **Code Generation**: Invoke without a selection to generate net-new code at
44:     the cursor.
45: -   **Localized Docs**: Highly effective for quickly adding comments,
46:     docstrings, or localized documentation.
47: 
48: ### C. Collaborative: Sidebar Chat & Agent
49: 
50: The most powerful modality for complex, multi-step tasks.
51: 
52: -   **Sidebar Chat**: The primary panel to ask questions, plan features, or
53:     discuss code.
54: -   **Agent Mode**: Launches a collaborative, multi-step pair programmer that
55:     can read/write files, run terminal commands (e.g., build/test), search the
56:     web, and use MCP tools.
57: -   **Planning Mode**: Review and refine the agent's step-by-step plan before
58:     execution.
59: 
60: ## 2. Editor UI Integrations
61: 
62: -   **Inline Code Lenses**: Action buttons appearing directly above code symbols
63:     (classes, functions) allowing you to trigger targeted agent commands (e.g.,
64:     "Refactor", "Write Tests", "Explain Code") on specific lines.
65: -   **Visual Diff Overlays**: Inline red/green diff indicators inside your
66:     editor canvas showing proposed edits, allowing you to review and
67:     accept/reject changes in-context.
68: -   **Diagnostic Auto-Fix**: Trigger the agent directly from inline compiler
69:     errors, lint warnings, or the Problems pane to automatically generate and
70:     apply fixes.
71: 
72: ## 3. Workspace Integration
73: 
74: -   **Workspace-Scoped Customizations**: The IDE automatically discovers and
75:     respects configurations in the `<project-root>/.agents/` folder, loading
76:     project-specific rules, custom skills, and plugins.
77: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:30:42-06:00
Completed At: 2026-07-31T15:30:42-06:00
{"name":"agy","isDir":true}
{"name":"agy-extreme-delegation","isDir":true}
{"name":"ai-os-audit","isDir":true}
{"name":"ai-os-auto-commit","isDir":true}
{"name":"ai-os-quiet-run","isDir":true}
{"name":"airtable","isDir":true}
{"name":"apikey-image-gen","isDir":true}
{"name":"apple-notes","isDir":true}
{"name":"apple-reminders","isDir":true}
{"name":"architecture-diagram","isDir":true}
{"name":"arxiv","isDir":true}
{"name":"ascii-art","isDir":true}
{"name":"ascii-video","isDir":true}
{"name":"audiocraft","isDir":true}
{"name":"audit","isDir":true}
{"name":"background-gui","isDir":true}
{"name":"baoyu-infographic","isDir":true}
{"name":"blogwatcher","isDir":true}
{"name":"build","isDir":true}
{"name":"claude-code","isDir":true}
{"name":"claude-design","isDir":true}
{"name":"codebase-inspection","isDir":true}
{"name":"codex","isDir":true}
{"name":"comfyui","isDir":true}
{"name":"computer-use","isDir":true}
{"name":"design-md","isDir":true}
{"name":"docx","isDir":true}
{"name":"dogfood","isDir":true}
{"name":"evaluating-llms-harness","isDir":true}
{"name":"excalidraw","isDir":true}
{"name":"fast","isDir":true}
{"name":"findmy","isDir":true}
{"name":"gif-search","isDir":true}
{"name":"github-auth","isDir":true}
{"name":"github-code-review","isDir":true}
{"name":"github-issues","isDir":true}
{"name":"github-pr-workflow","isDir":true}
{"name":"github-repo-management","isDir":true}
{"name":"google-workspace","isDir":true}
{"name":"grok-image-to-video","isDir":true}
{"name":"hammerspoon-webview","isDir":true}
{"name":"hammerspoon-webview-layout-presets","isDir":true}
{"name":"heartmula","isDir":true}
{"name":"hermes-agent","isDir":true}
{"name":"hermes-agent-skill-authoring","isDir":true}
{"name":"hermes-database-internals","isDir":true}
{"name":"hermes-desktop-plugins","isDir":true}
{"name":"hermes-gateway-api","isDir":true}
{"name":"hermes-to-agy","isDir":true}
{"name":"himalaya","isDir":true}
{"name":"huggingface-hub","isDir":true}
{"name":"h
<truncated 111 bytes>
message","isDir":true}
{"name":"jupyter-live-kernel","isDir":true}
{"name":"la-launch-agent-manager","isDir":true}
{"name":"llama-cpp","isDir":true}
{"name":"llm-wiki","isDir":true}
{"name":"macos-background-gui","isDir":true}
{"name":"macos-computer-use","isDir":true}
{"name":"macos-keyboard-shortcuts","isDir":true}
{"name":"macos-service-migration","isDir":true}
{"name":"manim-video","isDir":true}
{"name":"maps","isDir":true}
{"name":"markdown-viewer","isDir":true}
{"name":"nano-pdf","isDir":true}
{"name":"node-inspect-debugger","isDir":true}
{"name":"notion","isDir":true}
{"name":"obsidian","isDir":true}
{"name":"obsidian-notes","isDir":true}
{"name":"ocr-and-documents","isDir":true}
{"name":"opencode","isDir":true}
{"name":"openhue","isDir":true}
{"name":"p5js","isDir":true}
{"name":"pdf","isDir":true}
{"name":"petdex","isDir":true}
{"name":"plan","isDir":true}
{"name":"plan-multi-step","isDir":true}
{"name":"planner","isDir":true}
{"name":"polymarket","isDir":true}
{"name":"popular-web-designs","isDir":true}
{"name":"powerpoint","isDir":true}
{"name":"pretext","isDir":true}
{"name":"python-debugpy","isDir":true}
{"name":"remotion","isDir":true}
{"name":"requesting-code-review","isDir":true}
{"name":"research-paper-writing","isDir":true}
{"name":"resume","isDir":true}
{"name":"segment-anything","isDir":true}
{"name":"serving-llms-vllm","isDir":true}
{"name":"simplify-code","isDir":true}
{"name":"sketch","isDir":true}
{"name":"songsee","isDir":true}
{"name":"songwriting-and-ai-music","isDir":true}
{"name":"spike","isDir":true}
{"name":"start","isDir":true}
{"name":"strict-delegation","isDir":true}
{"name":"systematic-debugging","isDir":true}
{"name":"teams-meeting-pipeline","isDir":true}
{"name":"test-driven-development","isDir":true}
{"name":"touchdesigner-mcp","isDir":true}
{"name":"weights-and-biases","isDir":true}
{"name":"xlsx","isDir":true}
{"name":"xurl","isDir":true}
{"name":"youtube-content","isDir":true}
{"name":"yuanbao","isDir":true}

Summary: This directory contains 107 subdirectories and 0 files.

Created At: 2026-07-31T15:30:42-06:00
Completed At: 2026-07-31T15:30:43-06:00
File Path: `file:///Users/matt/.gemini/config/skills/planner/SKILL.md`
Total Lines: 46
Total Bytes: 2460
Showing lines 1 to 46
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: name: planner
3: description: MANDATORY: Use when initiating high-reasoning planning with a specific model profile before executing non-trivial tasks.
4: version: 1.3.0
5: author: AGY Systems
6: license: MIT
7: metadata:
8:   hermes:
9:     tags: [planner, triage, agymcp, reasoning, planning, multi-stage]
10:     related_skills: [plan, plan-multi-step, agy]
11: ---
12: 
13: # AGY Planner Skill (`/planner`)
14: 
15: ## STRICT TRIAGE & DELEGATION MANDATE
16: 
17: **CRITICAL RULE FOR ORCHESTRATOR**: When the user passes `/planner` or any model arguments (e.g. `/planner 3.1 pro high`), the Orchestrator MUST NEVER do codebase research, file reads (`view_file`), code searches (`grep_search`), or plan authoring directly in the main thread. 
18: 
19: Doing reads or planning directly in the main thread upon receiving `/planner` is a **STRICT SYSTEM VIOLATION**.
20: 
21: ## Usage & Model Profiles
22: 
23: Call the skill directly with optional model parameters:
24: - `/planner` (defaults to Gemini Pro 3.1 Low)
25: - `/planner 3.1 pro high`
26: - `/planner pro`
27: - `/planner claude-3-5-sonnet`
28: 
29: ## Mandatory Execution Workflow
30: 
31: 1. **Step 1: Immediate Subagent Research Delegation (Flash/Subagent)**
32:    - The main orchestrator thread MUST NOT call `list_dir`, `view_file`, or `grep_search` on codebase files.
33:    - The main orchestrator MUST immediately spawn a research subagent (`invoke_subagent` with `TypeName: "research"` or `Model: "flash"`) to inspect the project structure and gather necessary file context into a summary report.
34: 
35: 2. **Step 2: External Planner Pass via `agymcp`**
36:    - The orchestrator passes the subagent's research report to the requested model profile (e.g., `gemini-3.1-pro-high` or `pro`) using the `agymcp` tool or specialized planner subagent (`invoke_subagent` with `Model: "pro"`).
37:    - The external planner generates the `implementation_plan.md` artifact at `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.
38: 
39: 3. **Step 3: Plan Execution (Main Orchestrator -> Flash Subagent -> Flash-Lite Edits)**
40:    - Once user approves plan, Main Orchestrator (M) spawns an execution orchestrator subagent (Model: 'flash').
41:    - The Flash execution subagent coordinates the sub-tasks and delegates individual file creation/edit operations to leaf 'flash_lite' subagents (E).
42: 
43: ## Core Directives
44: - **Zero Direct Codebase Inspection in Main Thread**: Let research subagents collect context.
45: - **Zero Direct Plan Drafts by Orchestrator**: High-reasoning plans MUST originate from the designated Pro/Planner model.
46: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:31:04-06:00
Completed At: 2026-07-31T15:31:05-06:00
No results found

Created At: 2026-07-31T15:31:05-06:00
Completed At: 2026-07-31T15:31:05-06:00
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/docs/skills.md","LineNumber":4,"LineContent":"capabilities. They serve as \"cheatsheets\" or runbooks for specific workflows,"}
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/docs/skills.md","LineNumber":70,"LineContent":"    workflow."}
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md","LineNumber":12,"LineContent":"teach it new workflows, enforce guidelines, and integrate it with external"}
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md","LineNumber":26,"LineContent":"**Skills**      | `skills/\u003cname\u003e/SKILL.md`     | On-Demand (Progressive)   | Teaching the agent multi-step procedures, runbooks, and tool workflows.                 | [Skills Guide](./docs/skills.md)"}
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/references/app.md","LineNumber":25,"LineContent":"-   **Slash Commands**: Type `/` to invoke built-in workflows. Slash commands"}
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/references/ide.md","LineNumber":4,"LineContent":"(built on VS Code) that integrates agentic workflows directly into your coding"}
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/references/sdk.md","LineNumber":70,"LineContent":"For complex agentic workflows, you can monitor the agent's internal reasoning or"}
{"File":"/Users/matt/.gemini/antigravity/builtin/skills/antigravity_guide/SKILL.md","LineNumber":43,"LineContent":"-   **Rules**: `https://antigravity.google/docs/rules-workflows`"}

Created At: 2026-07-31T15:31:06-06:00
Completed At: 2026-07-31T15:31:06-06:00
{"name":"SKILL.md","sizeBytes":"5321"}
{"name":"docs","isDir":true}

Summary: This directory contains 1 subdirectories and 1 files.

Created At: 2026-07-31T15:31:07-06:00
Completed At: 2026-07-31T15:31:07-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md`
Total Lines: 105
Total Bytes: 5321
Showing lines 1 to 105
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: name: agy-customizations
3: description: >-
4:   Comprehensive guide and reference for the Antigravity Customization System.
5:   Use to explain how customizations work, their loading priority, discovery mechanisms,
6:   and to guide the creation of skills, rules, plugins, hooks, and MCP servers.
7: ---
8: 
9: # Antigravity Customization System Guide
10: 
11: The Antigravity Customization System allows you to tailor the agent's behavior,
12: teach it new workflows, enforce guidelines, and integrate it with external
13: tools. By customizing the agent, you can transition it from a general-purpose
14: assistant to an expert pair programmer specialized in your project's codebase
15: and processes.
16: 
17: --------------------------------------------------------------------------------
18: 
19: ## Customization Types: Quick Reference
20: 
21: Choose the right customization type based on your goal:
22: 
23: Type            | Config File/Folder           | Scope                     | Best For                                                                                | Learn More
24: :-------------- | :--------------------------- | :------------------------ | :-------------------------------------------------------------------------------------- | :---------
25: **Rules**       | `GEMINI.md`, `AGENTS.md`     | Contextual / Hierarchical | Enforcing coding styles, API restrictions, and local guidelines.                        | [Rules Guide](./docs/rules.md)
26: **Skills**      | `skills/<name>/SKILL.md`     | On-Demand (Progressive)   | Teach
<truncated 2198 bytes>
, the higher-priority customization overrides the lower-priority one.
62: 
63: The priority order (from highest to lowest) is:
64: 
65: 1.  **Workspace Project**: Hierarchical discovery walking up from the CWD to the
66:     repository root.
67: 2.  **Declared Configurations**: Customizations explicitly listed in
68:     `skills.json` or `plugins.json` in your workspace.
69: 3.  **Global Discovery**: `~/.gemini/config/`
70: 4.  **Built-in Customizations**: Default skills bundled with the application.
71: 5.  **Global Declared Configurations**: Explicitly listed in global JSON
72:     configs.
73: 
74: --------------------------------------------------------------------------------
75: 
76: ## How Customizations are Applied
77: 
78: ### Progressive Disclosure (Skills and Rules)
79: 
80: To prevent overwhelming the model's context window, Antigravity uses
81: **progressive disclosure**:
82: 
83: *   **Skills** are not loaded into the context window by default. Only their
84:     names and descriptions are injected. The full content of a skill is only
85:     loaded if the model (or the user) explicitly decides to activate it.
86: *   **Rules** with `trigger: model_decision` behave similarly. Only `always_on`
87:     rules are loaded unconditionally.
88: 
89: ### Deduplication
90: 
91: All customizations (especially rules) are deduplicated by their resolved file
92: paths. A rule file will never be injected more than once in a single
93: conversation turn, even if it matches multiple trigger conditions.
94: 
95: --------------------------------------------------------------------------------
96: 
97: ## Advanced Management: JSON Configs
98: 
99: For customizations stored in non-standard locations, you can use `skills.json`
100: and `plugins.json` to explicitly register them and inherit from shared
101: configurations.
102: 
103: *   Learn how to configure these in the
104:     [JSON Configurations Guide](./docs/json_configs.md).
105: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:31:07-06:00
Completed At: 2026-07-31T15:31:07-06:00
{"name":"hooks.md","sizeBytes":"10421"}
{"name":"json_configs.md","sizeBytes":"3983"}
{"name":"mcp_servers.md","sizeBytes":"2966"}
{"name":"plugins.md","sizeBytes":"2453"}
{"name":"rules.md","sizeBytes":"1063"}
{"name":"skills.md","sizeBytes":"2650"}

Summary: This directory contains 0 subdirectories and 6 files.

Created At: 2026-07-31T15:31:08-06:00
Completed At: 2026-07-31T15:31:08-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/docs/skills.md`
Total Lines: 71
Total Bytes: 2650
Showing lines 1 to 71
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Workspace Skills
2: 
3: Skills are modular packages of knowledge and procedures that extend the agent's
4: capabilities. They serve as "cheatsheets" or runbooks for specific workflows,
5: enabling the agent to perform complex tasks reliably.
6: 
7: ## Directory Structure
8: 
9: A skill must be structured as a directory within a `skills/` folder inside a
10: customization root (e.g., `.agents/skills/`).
11: 
12: ```text
13: skills/<skill_name>/
14: ├── SKILL.md          # Required: Main instruction file with frontmatter
15: ├── scripts/          # Optional: Helper scripts and utilities
16: ├── examples/         # Optional: Reference implementations
17: ├── resources/        # Optional: Additional assets or templates
18: └── references/       # Optional: Detailed documentation or manuals
19: ```
20: 
21: ## Main Instruction File (`SKILL.md`)
22: 
23: The `SKILL.md` file must start with a YAML frontmatter block containing the
24: `name` and `description` fields.
25: 
26: ```markdown
27: ---
28: name: my-specialized-skill
29: description: >-
30:   Describe when the agent should use this skill. Use third-person.
31:   Example: "Use this skill when the user asks to run integration tests for the XYZ service."
32: ---
33: 
34: # My Specialized Skill
35: 
36: Provide clear, step-by-step instructions for the agent here.
37: 
38: ## Steps
39: 
40: 1.  Run the preparation script:
41:     [prepare.sh](./scripts/prepare.sh)
42: 2.  Execute the test command:
43:     `npm test`
44: 3.  Analyze the results in the log file.
45: ```
46: 
47: ### Frontmatter Fields
48: 
49: *   **`name`** (string, required): A unique identifier for the skill. It should
50:     be lowercase and hyphenated.
51: *   **`description`** (string, required): This is the most critical field. The
52:     primary agent reads this description to decide whether to activate the skill
53:     for a given user prompt. It should clearly state **what** the skill does and
54:     **when** it should be used.
55: 
56: ## Best Practices for Writing Skills
57: 
58: 1.  **Progressive Disclosure**: Keep the main `SKILL.md` concise. Use the
59:     `references/` subdirectory for bulky documentation and link to it from
60:     `SKILL.md`. The agent will only read those reference files if it needs them,
61:     saving token context.
62: 2.  **Executable Helpers**: Encapsulate complex command sequences in scripts
63:     within the `scripts/` directory. Link to them using relative links so the
64:     agent can easily find and run them.
65: 3.  **Validation Steps**: Always include instructions on how the agent can
66:     verify that a step was successful (e.g., checking a log file, running a
67:     dry-run command).
68: 4.  **No Duplication**: Do not instruct the agent on general coding practices or
69:     things it already knows. Focus strictly on the unique procedures of your
70:     workflow.
71: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:31:08-06:00
Completed At: 2026-07-31T15:31:08-06:00
{"name":".DS_Store","sizeBytes":"30724"}
{"name":".agents","isDir":true}
{"name":".clinerules","isDir":true}
{"name":".cursor","isDir":true}
{"name":".github","isDir":true}
{"name":".opencode","isDir":true}
{"name":".windsurf","isDir":true}
{"name":"Inboxer","isDir":true}
{"name":"TypedRecall","isDir":true}
{"name":"ai-migration-staging","isDir":true}
{"name":"ai-os","isDir":true}
{"name":"ai-os-archive","isDir":true}
{"name":"any-markdown-main","isDir":true}
{"name":"apple-music-companion","isDir":true}
{"name":"apple-pencil-safari-api-test","isDir":true}
{"name":"apple-podcast-transcript-extractor","isDir":true}
{"name":"archive","sizeBytes":"76"}
{"name":"atlas-calculator","isDir":true}
{"name":"atlas-educational-society-website","isDir":true}
{"name":"blockdoku","isDir":true}
{"name":"break-reminder","isDir":true}
{"name":"cm-pinner","isDir":true}
{"name":"cock-band","isDir":true}
{"name":"console-compactifier","isDir":true}
{"name":"deal-or-no-deal","isDir":true}
{"name":"edmonton-fire-rescue-site-scraper-action","isDir":true}
{"name":"external","isDir":true}
{"name":"generative-animation","isDir":true}
{"name":"hermes-agent","isDir":true}
{"name":"hermes-extension","isDir":true}
{"name":"hermes-todo.md","sizeBytes":"332"}
{"name":"jay-art-portfolio","isDir":true}
{"name":"local-automation-server","isDir":true}
{"name":"lost-fuzz-website","isDir":true}
{"name":"mattmurphy.ca","isDir":true}
{"name":"music-companion","isDir":true}
{"name":"music-cross-linker","isDir":true}
{"name":"pencil-notes","isDir":true}
{"name":"prune.md","sizeBytes":"4120"}
{"name":"purge_node_modules.sh","sizeBytes":"724"}
{"name":"qbit-manage","isDir":true}
{"name":"qwerty-midi-hammerspoon","isDir":true}
{"name":"ride-weather-pwa","isDir":true}
{"name":"rym-apple-music-player","isDir":true}
{"name":"school","sizeBytes":"75"}
{"name":"smart-c2p","isDir":true}
{"name":"spotiflac-cli","isDir":true}
{"name":"structural-constraint-art","isDir":true}
{"name":"synthesia-clone","isDir":true}
{"name":"taboo","isDir":true}
{"name":"tauri-monorepo","isDir":true}
{"name":"timelock-vault","isDir":true}
{"name":"typery","isDir":true}
{"name":"user-migration-bridge","isDir":true}
{"name":"userscript-bundler","isDir":true}
{"name":"vector-art-generator","isDir":true}
{"name":"vercel-openrouter-proxy","isDir":true}
{"name":"video-chat","isDir":true}
{"name":"video-context-agent","isDir":true}
{"name":"waking-up-code","isDir":true}
{"name":"webpage-compressor","isDir":true}
{"name":"yt-dlp-dev","isDir":true}

Summary: This directory contains 56 subdirectories and 6 files.

Created At: 2026-07-31T15:31:09-06:00
Completed At: 2026-07-31T15:31:09-06:00
{"name":".DS_Store","sizeBytes":"10244"}
{"name":".agents","isDir":true}
{"name":".agy-mcp","isDir":true}
{"name":".devtool","isDir":true}
{"name":".gemini","isDir":true}
{"name":".git","isDir":true}
{"name":".github","isDir":true}
{"name":".gitignore","sizeBytes":"249"}
{"name":".gitignore.bak","sizeBytes":"156"}
{"name":".hermes","isDir":true}
{"name":".prettierignore","sizeBytes":"27"}
{"name":".rules","isDir":true}
{"name":".vscode","isDir":true}
{"name":".zshrc","sizeBytes":"457"}
{"name":".zshrc_aios","sizeBytes":"3485"}
{"name":"2026-07-20-125858-local-command-caveatcaveat-the-messages-below.txt","sizeBytes":"352789"}
{"name":"AGENTS.md","sizeBytes":"29"}
{"name":"AG_CONTEXT.md","sizeBytes":"3489"}
{"name":"CLAUDE.md","sizeBytes":"5458"}
{"name":"DEVELOPMENT_JOURNAL.md","sizeBytes":"14115"}
{"name":"FEATURES.md","sizeBytes":"7182"}
{"name":"HERMES.md","sizeBytes":"5001"}
{"name":"README.md","sizeBytes":"5366"}
{"name":"agent-logs","isDir":true}
{"name":"bin","isDir":true}
{"name":"bun.lock","sizeBytes":"26965"}
{"name":"conduit","isDir":true}
{"name":"context","isDir":true}
{"name":"dist","isDir":true}
{"name":"docs","isDir":true}
{"name":"litellm","isDir":true}
{"name":"litellm_config.yaml","sizeBytes":"4979"}
{"name":"node_modules","isDir":true}
{"name":"package.json","sizeBytes":"566"}
{"name":"plans","isDir":true}
{"name":"pnpm-lock.yaml","sizeBytes":"479"}
{"name":"scripts","isDir":true}
{"name":"services","isDir":true}
{"name":"skills","isDir":true}
{"name":"tauri-gui","isDir":true}
{"name":"test.db"}
{"name":"thread-browser","isDir":true}
{"name":"tmp","isDir":true}
{"name":"todo.md","sizeBytes":"6146"}
{"name":"userscripts","isDir":true}
{"name":"webui-patches","isDir":true}

Summary: This directory contains 26 subdirectories and 20 files.

Created At: 2026-07-31T15:31:10-06:00
Completed At: 2026-07-31T15:31:10-06:00
{"name":".last_usage","sizeBytes":"11"}
{"name":"__pycache__","isDir":true}
{"name":"aios_hermes_wrapper.py","sizeBytes":"6325"}
{"name":"append_system_rule.py","sizeBytes":"2556"}
{"name":"audit_transcripts.py","sizeBytes":"16549"}
{"name":"auto_commit.py","sizeBytes":"5081"}
{"name":"background_review.py","sizeBytes":"4489"}
{"name":"build_rules.py","sizeBytes":"3044"}
{"name":"check_thread_bloat.py","sizeBytes":"7609"}
{"name":"clip_search.py","sizeBytes":"5774"}
{"name":"compile_dynamic_prompt.py","sizeBytes":"2496"}
{"name":"context_handoff.py","sizeBytes":"7064"}
{"name":"curate_knowledge.py","sizeBytes":"4779"}
{"name":"gemini-ingest-watch.sh","sizeBytes":"1805"}
{"name":"gen_conversation_md.py","sizeBytes":"8582"}
{"name":"generate_repo_map.py","sizeBytes":"6786"}
{"name":"generate_title.py","sizeBytes":"6014"}
{"name":"get-active-task.sh","sizeBytes":"514"}
{"name":"get_last_cost.py","sizeBytes":"3732"}
{"name":"habit_tracker.py","sizeBytes":"7384"}
{"name":"handover.py","sizeBytes":"6727"}
{"name":"housekeep.py","sizeBytes":"4258"}
{"name":"ingest_codebase","sizeBytes":"10048"}
{"name":"ingest_gemini_archives.py","sizeBytes":"15361"}
{"name":"jules-agent.sh","sizeBytes":"1155"}
{"name":"jules_delegate.py","sizeBytes":"5375"}
{"name":"jules_provisioner.py","sizeBytes":"4638"}
{"name":"jules_quota.py","sizeBytes":"3504"}
{"name":"mcp_server.py","sizeBytes":"8066"}
{"name":"memory_diff","sizeBytes":"213"}
{"name":"memory_diff.sh","sizeBytes":"487"}
{"name":"memory_search","sizeBytes":"420"}
{"name":"memory_search.sh","sizeBytes":"717"}
{"name":"parse_litellm_models.py","sizeBytes":"4440"}
{"name":"precision_edit.py","sizeBytes":"1550"}
{"name":"preflight.py","sizeBytes":"5442"}
{"name":"research_agent.py","sizeBytes":"3249"}
{"name":"runaway-watchdog.sh","sizeBytes":"3725"}
{"name":"search_all_agent_logs.py","sizeBytes":"2813"}
{"name":"start-triage-proxy.sh","sizeBytes":"808"}
{"name":"subagent.py","sizeBytes":"20691"}
{"name":"swap_turn.py","sizeBytes":"6959"}
{"name":"sync_rules.sh","sizeBytes":"1341"}
{"name":"sync_skills.py","sizeBytes":"2607"}
{"name":"sync_threads.py","sizeBytes":"8280"}
{"name":"telemetry_db.py","sizeBytes":"2721"}
{"name":"test_triage.py","sizeBytes":"2183"}
{"name":"triage_proxy.py","sizeBytes":"7838"}
{"name":"triage_router.py","sizeBytes":"24348"}
{"name":"triage_task.py","sizeBytes":"5453"}
{"name":"trigger_thread_reset.py","sizeBytes":"1966"}
{"name":"view_thread.py","sizeBytes":"3625"}
{"name":"yt-channel-videos.py","sizeBytes":"3766"}

Summary: This directory contains 1 subdirectories and 52 files.

Created At: 2026-07-31T15:31:11-06:00
Completed At: 2026-07-31T15:31:11-06:00
{"name":"gemini.js","sizeBytes":"76"}
{"name":"livebench-frontier.js","sizeBytes":"5487"}

Summary: This directory contains 0 subdirectories and 2 files.

Created At: 2026-07-31T15:31:11-06:00
Completed At: 2026-07-31T15:31:12-06:00
{"name":".DS_Store","sizeBytes":"6148"}
{"name":"1337x.js","sizeBytes":"754"}
{"name":"Perplexity.ai Improvements.user.js","sizeBytes":"62064"}
{"name":"amazon filter.js","sizeBytes":"7516"}
{"name":"apple-music-embedded-player.user.js","sizeBytes":"1272"}
{"name":"auto-redirect-paywalls.user.js","sizeBytes":"344"}
{"name":"compat.js","sizeBytes":"6499"}
{"name":"contentconnections.js","sizeBytes":"97624"}
{"name":"control-center.js","sizeBytes":"24272"}
{"name":"custom-youtube-iframe-fullscreen.js","sizeBytes":"13099"}
{"name":"d2l-content-tools.user.js","sizeBytes":"122597"}
{"name":"fix-aistudio-lag-1.0.user.js","sizeBytes":"3165"}
{"name":"forbes.js","sizeBytes":"321"}
{"name":"gemini-enhancements","isDir":true}
{"name":"livebench-frontier.user.js","sizeBytes":"4451"}
{"name":"m3u8-capture.user.js","sizeBytes":"29415"}
{"name":"open-apple-music-links-in-music-app.js","sizeBytes":"1617"}
{"name":"openrouter-credit-reminder.user.js","sizeBytes":"1562"}
{"name":"perplexity.js","sizeBytes":"15335"}
{"name":"rate-your-music-hide-competing-media.js","sizeBytes":"1524"}
{"name":"rym.user.js","sizeBytes":"10967"}
{"name":"studyforge-frame-downloader.user.js","sizeBytes":"55374"}
{"name":"torrentgalaxy-modal-fix.js","sizeBytes":"3683"}
{"name":"torrentmac.js","sizeBytes":"2842"}
{"name":"xkcd-explain.user.js","sizeBytes":"1383"}
{"name":"youtube-master.user.js","sizeBytes":"51429"}

Summary: This directory contains 1 subdirectories and 25 files.

Created At: 2026-07-31T15:31:12-06:00
Completed At: 2026-07-31T15:31:12-06:00
{"name":"00-bootstrap.js","sizeBytes":"888"}
{"name":"01-shared.js","sizeBytes":"3538"}
{"name":"02-token-usage.js","sizeBytes":"13125"}
{"name":"03-timestamps.js","sizeBytes":"7190"}
{"name":"04-sidebar-dates.js","sizeBytes":"8434"}
{"name":"05-prompt-tools.js","sizeBytes":"42972"}
{"name":"06-archive.js","sizeBytes":"6438"}
{"name":"07-terminal.js","sizeBytes":"18774"}
{"name":"08-model-optimizer.js","sizeBytes":"9936"}
{"name":"09-page-observer.js","sizeBytes":"5117"}
{"name":"10-tool-calls.js","sizeBytes":"9788"}

Summary: This directory contains 0 subdirectories and 11 files.

Created At: 2026-07-31T15:31:14-06:00
Completed At: 2026-07-31T15:31:14-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/docs/rules.md`
Total Lines: 28
Total Bytes: 1063
Showing lines 1 to 28
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Workspace Rules
2: 
3: Rules are guidelines and constraints that the agent must follow when operating
4: within specific directories. They are useful for enforcing coding styles, API
5: usage restrictions, or safety protocols.
6: 
7: ## Rule Locations
8: 
9: The system automatically discovers and applies rules from the following
10: locations:
11: 
12: *   **Directory-Based Rules (`GEMINI.md` / `AGENTS.md`)**: Placed directly in
13:     any directory. The system walks up from the current working directory to the
14:     repository root and loads these files. They apply to the directory they
15:     reside in and all its subdirectories.
16: 
17: ## Rule Format
18: 
19: Rules are written in Markdown. Standalone `GEMINI.md` / `AGENTS.md` files do not
20: support frontmatter and are always active for their directory scope.
21: 
22: ## Rule Merging and Deduplication
23: 
24: *   Rules are automatically deduplicated. Even if a rule is discovered via
25:     multiple paths (e.g., inherited from parent directories), it is only applied
26:     once per conversation.
27: *   If a rule is defined in a plugin, it is loaded when the plugin is enabled.
28: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:31:15-06:00
Completed At: 2026-07-31T15:31:15-06:00
File Path: `file:///Users/matt/.gemini/antigravity/builtin/skills/agy-customizations/docs/json_configs.md`
Total Lines: 103
Total Bytes: 3983
Showing lines 1 to 103
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # JSON Configuration Files
2: 
3: JSON configuration files allow you to explicitly register and manage
4: customizations that are stored outside the default discovery locations (such as
5: project-specific folders or shared team directories).
6: 
7: Each customization type has its own configuration file, placed in your
8: customization root directory (e.g., `.agents/` in your project, or
9: `~/.gemini/config/` globally):
10: 
11: *   **Skills**: `skills.json`
12: *   **Plugins**: `plugins.json`
13: 
14: ## Configuration Schema
15: 
16: Both configuration files share the same schema, allowing you to declare path
17: entries and inherit from other configurations.
18: 
19: ```json
20: {
21:   "inherits": [
22:     {
23:       "path": "/path/to/shared/skills.json",
24:       "include_only": ["linter-skill"],
25:       "exclude": ["deprecated-skill"]
26:     }
27:   ],
28:   "entries": [
29:     {
30:       "path": "path/to/my/project/skills",
31:       "exclude": ["experimental-.*"]
32:     },
33:     {
34:       "path": "~/personal-skills"
35:     }
36:   ]
37: }
38: ```
39: 
40: ### Top-Level Fields
41: 
42: *   **`entries`** (array of objects, optional): A list of path entries to scan
43:     for customizations of this type.
44: *   **`inherits`** (array of objects, optional): A list of other configuration
45:     files to inherit from. The entries from inherited files are merged with your
46:     local entries. Inherited files are processed in the order they are listed.
47: 
48: ### Path Entry Fields
49: 
50: Each object in the `entri
<truncated 862 bytes>
   :          : directory names match at      :
62: :                :                  :          : least one of these patterns   :
63: :                :                  :          : will be loaded.               :
64: | `exclude`      | array of strings | No       | A list of regex patterns.     |
65: :                :                  :          : Customizations whose          :
66: :                :                  :          : directory names match any of  :
67: :                :                  :          : these patterns will be        :
68: :                :                  :          : skipped.                      :
69: 
70: ## Path Resolution Rules
71: 
72: The `path` field is resolved based on the following rules:
73: 
74: 1.  **Absolute Paths**: Paths starting with `/` are treated as absolute local
75:     filesystem paths.
76: 2.  **Home-Relative Paths**: Paths starting with `~/` are resolved relative to
77:     the user's home directory.
78: 3.  **Workspace-Relative Paths**: Paths not starting with `/` or `~/` are
79:     resolved relative to the repository root (the folder containing `.git` or
80:     the root of the workspace).
81: 
82: ### Pro-Tip: Team Sharing via VCS
83: 
84: To share customizations across a team:
85: 
86: 1.  **Commit the Customizations**: Commit your team's skills to a shared
87:     directory in your repository (e.g., `tools/agents/skills/`).
88: 2.  **Commit the Config**: Create and commit a `skills.json` at the root of your
89:     repository (in `.agents/skills.json`) that points to the shared directory
90:     using a workspace-relative path:
91: 
92:     ```json
93:     {
94:       "entries": [
95:         { "path": "tools/agents/skills" }
96:       ]
97:     }
98:     ```
99: 
100: 3.  **Automatic Activation**: When other team members clone the repository and
101:     open it, the agent will automatically discover `.agents/skills.json` and
102:     load the shared skills.
103: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:31:21-06:00
Completed At: 2026-07-31T15:31:21-06:00
Message sent to "26a75289-bec3-4737-b152-c0ccc4fb0fc7".

I have completed the investigation and sent the detailed findings report to the parent agent.

---
