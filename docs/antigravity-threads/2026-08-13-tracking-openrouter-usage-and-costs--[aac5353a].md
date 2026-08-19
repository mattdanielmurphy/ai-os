---
title: "Tracking OpenRouter Usage and Costs"
date: "2026-08-13"
conversation_id: "aac5353a-d4a5-578a-945b-9d3f8e3a700d"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

youre SURE I can't do anything in Warp? Be creative. Can I hack Warp at all?

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-11 20:15" -->

</span>



<span title="Responded at 7:13pm" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

If you want to modify how Warp displays this data, you cannot do so via a straightforward settings toggle or theme tweak. Warp's core UI is written in Rust using a custom UI framework (Pixi/GPUI), meaning that the gray summary card component and its logic are baked directly into the compiled binary.
However, since you want to look at creative options, you can bypass the native UI constraint entirely. Since the OpenRouter API key sits right in your environment variables, you can intercept, track, and proxy the calls.
Here are three ways to get creative:
1. The MITM Proxy Trick (Inject Custom Logic)
If you want to automatically log your spend every single time the Warp agent runs, you can route Warp's custom OpenRouter base URL through a local proxy script or tool like **mitmproxy**.
Instead of pointing Warp directly to `[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)`, you can point it to a local endpoint (e.g., `http://localhost:8080/v1`). You then write a lightweight local script that:
Receives the agent payload from Warp.
Forwards it to OpenRouter.
Intercepts the completion JSON or the streaming chunks.
Parases the `usage` or header metadata (`x-openrouter-tokens-prompt`, etc.).
Appends the exact run cost ($0.00x) into a rolling local log file or triggers a local macOS desktop notification using `osascript`.
2. Hack Your Prompt/Statusline to Live-Stream Costs
Instead of staring at Warp's native card, you can inject your OpenRouter usage directly into your terminal prompt (`PS1`/`RPROMPT`) or use a tool that updates dynamically.
There is an open-source terminal utility called **`vibeusage`** designed exactly for this. It explicitly tracks unified model gateways like OpenRouter (calculating dollars spent vs. total credits) and feeds that data directly into terminal environments. You can call it manually or script a custom hook in your `.zshrc` to spit out your precise OpenRouter burn rate on every new terminal line.
3. Build a Live Floating Dynamic Overlay
If you want to see the cost in real-time right over your terminal window without opening a browser tab, you can use a menu bar controller like **SwiftBar** or **xbar**.
You can configure a 5-line bash/python script that hits the OpenRouter Key Stats endpoint every 10 seconds and outputs the remaining balance or recent spend right in your macOS menu bar:
Bash
```
#!/bin/bash

### <bitbar.title>OpenRouter Tracker</bitbar.title>

### <bitbar.refresh>10s</bitbar.refresh>
BALANCE=$(curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/auth/key | jq -r '.data.limit - .data.usage')
printf "OR: $%.4f\n" "$BALANCE"
```
This forces the financial footprint of your custom models into plain sight, floating right above your Warp workspace at all times.
<!-- /gemini-message -->

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

any way to make Warp better at showing token usage (and ideally cost!) of using openrouter models?

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-11 20:14" -->

</span>



<span title="Responded at 7:13pm" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Because you are routing a custom model via **OpenRouter** (`DS V4 Flash Fast`), Warp's native agent UI defaults to showing `0 credits spent`. Warp's built-in tracker is designed to calculate consumption for its own native tier rather than parsing upstream token metadata or pricing tiers from third-party providers like OpenRouter.
While you can't force Warp's gray status block to natively display the dollar cost or exact token count for external endpoints, you can gain tight visibility into your OpenRouter usage and costs right inside your terminal or workflow using the methods below.
1. Track Live via OpenRouter's Key Stats Endpoint
OpenRouter provides an API endpoint to check your remaining balance, which you can query directly from your command line.
You can add an alias to your shell configuration (`.zshrc`) to quickly check your current wallet balance:
Bash
```
alias or-balance="curl -s -H 'Authorization: Bearer \$OPENROUTER_API_KEY' https://openrouter.ai/api/v1/auth/key | jq '.data.limit - .data.usage | \"Remaining Balance: $\" + tostring'"
```
2. Monitor Real-Time via the OpenRouter Dashboard
The most accurate breakdown of cost per model, prompt tokens, and completion tokens is found on the official dashboard:
**Activity & Costs:** Go to openrouter.ai/activity to view a live-updating stream of every generation, including the exact token breakdown and fractional cent costs for your `DS V4 Flash Fast` runs.
**Key-Specific Limits:** If you want to make sure your agent doesn't run wild on costs, you can create a dedicated API key for Warp at openrouter.ai/keys and set a strict **credit limit** on that specific key.
3. Check Response Headers (If Custom Scripted)
If you ever wrap your calls or use tools that expose raw HTTP response headers, OpenRouter includes specific tracking headers in every completion response:
`x-openrouter-tokens-prompt`
`x-openrouter-tokens-completion`
For now, keeping the OpenRouter Activity tab open on a side screen or utilizing a quick shell alias to query your key's status are the most effective ways to keep tabs on your agent's spending.
<!-- /gemini-message -->
---
<!-- gemini-message index=3 role=user timestamp="2026-07-11 20:15" -->

</span>



</span>

</span>