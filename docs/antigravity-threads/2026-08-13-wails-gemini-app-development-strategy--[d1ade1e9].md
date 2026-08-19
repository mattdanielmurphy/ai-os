---
title: "Wails Gemini App Development Strategy"
date: "2026-08-13"
conversation_id: "d1ade1e9-1919-5c5b-b417-c97d975c7340"
source: "antigravity"
---

# Wails Gemini App Development Strategy

## USER_EXPLICIT (2026-08-13T18:54:11.224660)

I want to make an app that spawns a little floating input text area.

When the user types into that text area, the app has a hidden but real webview with google.gemini.com loaded whose text area GETS EVERY KEYSTROKE in real time.

When we hit submit on the input textarea, we should see that floating window expand a bit to show the response from gemini, which is simply extracted from the background webview.

An expand button opens that full webview (no longer seeing a custom interface, it's just a regular webview window of that thread).

A quick-search function lets you search with fuzzy search through ALL gemini threads (all downloaded through injected javascript) and load them into the webview via a URL with their UUIDs.




Now. I DO NOT want to make this from scratch. The question is only how minimal of an existing project do we want to make sure we can customize it to our liking.

But we should aim to find an existing project that is:

- a wrapper for gemini.google.com

- ideally also a wrapper for perplexity.com

- ideally has a floating text input thing

- ideally not using Electron, and ideally IS using Wails




If you find an implementation that does most but not all of these (VERY likely), just consider how hard it'd be to change/add onto the code to MAKE those possible.




I don't want any old abandoned projects ideally. I mean, especially since they're web wrappers, they really have to be quite new to be useful I think.




Please find a LOT of projects to audit and determine the best picks for me.

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-09 21:49" -->

---
## MODEL (2026-08-13T18:54:11.224662)

Audit of the current open-source space reveals that finding a pre-built, highly active **Wails** app specifically designed to wrap `gemini.google.com` and `perplexity.com` *while matching your exact floating spotlight UI* does not exist as an off-the-shelf project. Most AI wrappers in the wild rely on Tauri (like *Pake*) or Electron (like *Lencx/ChatGPT*).

However, because you are aiming for low-level UI control (hidden background webviews, key injection, and precise frame expansions), a bloated existing project would likely work against you. **The best strategy is to start with a minimal Wails v3 scaffolding or a lightweight, multi-window utility.**

Here is an audit of the closest matches, followed by how difficult it will be to implement your custom architecture on top of them.

1. Candidate Projects to Audit & Strip Down
Option A: Wails v3 Beta/Alpha Core Examples (Recommended Start)

**Repository:** wailsapp/wails/v3

**Why it fits:** Wails v3 natively introduces robust multi-window support, frameless overlays, and easy hidden-state window toggling out of the box (which was notoriously clunky in v2). The repo contains minimal example configurations for multi-window apps and transparent/frameless shells.

**Customization Effort:** **Low.** You get a zero-bloat foundation with pristine Go structures, letting you instantiate your background webview and custom floating UI without ripping out someone else’s broken CSS or outdated state management.

Option B: Pwh-Pwh / ai-gui

**Repository:** `pwh-pwh/ai-gui` (Go + Wails)

**Why it fits:** One of the few dedicated multi-provider AI desktop desktop wrappers explicitly utilizing Go and Wails.

**Customization Effort:** **Medium-High.** It is designed around hitting direct API endpoints (OpenAI, Gemini via API keys) using standard frontend components rather than wrapping and parsing the live web applications via injected JavaScript. You would have to rip out the API request pipelines and replace them with Webview loaders.

Option C: Minimal Frameless/Overlay Blueprints (e.g., Spirit or GlanceHUD)

**Repository:** Check the Awesome Wails compilation for lightweight UI shells like *Spirit* (a floating image/clipboard manager) or *GlanceHUD* (a floating system monitor).

**Why it fits:** These projects already solve the OS-level quirks of anchoring a frameless, always-on-top, transparent floating input widget.

**Customization Effort:** **Medium.** You get the floating text input UI setup immediately, but you will need to add the secondary background Webview logic manually in the Go layer.

2. Technical Feasibility & Implementation Blueprint

If you start with a minimal Wails v3 structure, here is exactly how your requested features translate to code modifications:

A. Hidden Webview with Real-Time Keystroke Injection

**Feasibility:** Highly Feasible.

**How to implement:** You will declare two windows in your Go main loop. One is your transparent, small floating frame (the input area). The second is a standard window initialized with `StartHidden: true` loading `https://gemini.google.com`.

To pipe keystrokes in real time, bind an `onInput` or `onKeyDown` listener in your custom input HTML. Every time a character is typed, fire a Wails runtime event or Go binding call:

JavaScript

```
// Frontend floating window
window.go.main.App.InjectKey(char);

```


On the Go side, you receive the character and evaluate a short JavaScript snippet directly inside the hidden Gemini webview instance using Wails' window execution runtime:

Go

```
// Go Backend
// Target the specific selector for Gemini's prompt area
jsSnippet := fmt.Sprintf(`
    var el = document.querySelector('div[contenteditable="true"]');
    if (el) {
        el.focus();
        document.execCommand('insertText', false, '%s');
    }
`, escapedChar)
backgroundWindow.ExecJS(jsSnippet)

```

B. Dynamic Window Expansion & Full Webview Toggle

**Feasibility:** Easy (with a crucial OS caveat).

**How to implement:** When the submit button is triggered, the frontend calculates the space needed for the response and calls the Go runtime window management API to update bounds:

Go

```
// Wails v3 Window resizing
floatingWindow.SetSize(width, expandedHeight)

```


**The Button:** Clicking the "Expand Full Webview" button simply hides or closes the custom floating UI window and triggers `.Show()` on the previously hidden `backgroundWindow`.

C. Fuzzy Searching Downloaded Thread Histories

**Feasibility:** Moderate.

**How to implement:** You can inject a content script into the background webview that scrapes the thread sidebar (`/app/` URLs containing the thread UUIDs) and writes them back to your Go layer via a bound method: `window.go.main.App.SaveThreads(jsonPayload)`.

Store this payload locally in a small JSON file or SQLite database. Your custom input window can run a simple fuzzy matching utility (like `fuse.js` in the frontend or a Go-based fuzzy matching library on the backend) to instantly query your downloaded list and call `backgroundWindow.LoadURL("https://gemini.google.com/app/" + selectedUUID)`.

Final Recommendation

Do not attempt to modify a heavy existing chatbot app. Instead, clone a raw **Wails v3 vanilla template** (using Vite + Svelte or React for fast fuzzy search rendering).

Wails provides an ideal footprint here: the single binary overhead will sit around **15–40MB**, and because it reuses WebKit (macOS) or WebView2 (Windows) instead of shipping an entire Chromium instance like Electron, running a background instance alongside your input layer won't destroy your machine's memory layout.

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="2026-07-09 21:49" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224665)

ok, I'd really like to use lots of components and stuff though to make this easier on us. Why re-invent the wheel right?

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-09 21:49" -->

---
## MODEL (2026-08-13T18:54:11.224666)

You're 100% right. Ripping out business logic from a massive, bloated client is a nightmare, but writing custom components for basic UI elements (like a fuzzy-search dropdown, a clean textarea, or layout shells) is equally a waste of time.

The compromise here is to use a **component-heavy starter template** rather than a fully-fledged app. This gives you a blank canvas for your application's architecture (multi-window setup, key injection, hidden webviews) while letting you assemble the UI instantly with pre-made components.

A premier boilerplate for this strategy is `AlexSKuznetsov/wails-template-react`. It saves you from configuring the asset pipelines and packs exactly what you need.

The Component Stack Checklist

By initializing your project with a modern React + Tailwind configuration, you can install specialized headless primitives to assemble your floating window in a few minutes:

1. The Floating Input & Dropdown Component (`shadcn/ui` + `Radix Primitives`)

Instead of styling inputs and state arrays from scratch, use `shadcn/ui` commands to drop pre-styled components right into your frontend:

**The Command Palette:** Run `npx shadcn-ui@latest add command`. This installs a wrapper around **`cmdk`**, which is the exact component used by applications like Linear and Vercel for their search bars. It has built-in, lightning-fast fuzzy filtering for your scraped Gemini thread list.

**The Input Frame:** Run `npx shadcn-ui@latest add textarea` and `npx shadcn-ui@latest add card`.

2. The Fuzzy Search Engine (`fuse.js`)

If you don't want to pipe the thread querying back to the Go layer, pull **Fuse.js** into your frontend:

Bash

```
npm install fuse.js

```


When your injected script scrapes the Gemini thread list (extracting title and UUID), you feed it to Fuse. It handles approximate matching (e.g., matching "phys lab" to "Physics 12 Lab Report Discussion") natively in the UI layer with zero lag.

Assembling the Layout

Using standard utility classes, you can assemble your floating interface without getting stuck in CSS configurations:

TypeScript

```
// Example setup inside your Wails frontend frame
import { Command, CommandInput, CommandList, CommandItem } from "@/components/ui/command"
import { Textarea } from "@/components/ui/textarea"

export default function FloatingSearchLauncher() {
  return (
    <div className="w-[600px] bg-background/80 backdrop-blur-md rounded-xl border p-4 shadow-2xl space-y-3">
      {/* Real-time streaming text input area */}
      <Textarea 
        placeholder="Ask Gemini..." 
        className="resize-none border-none focus-visible:ring-0 text-lg"
        onChange={(e) => window.go.main.App.InjectKey(e.target.value)}
      />

      {/* Fuzzy search thread interface beneath it */}
      <Command className="rounded-lg border shadow-md">
        <CommandInput placeholder="Search archived threads..." />
        <CommandList>
          {threads.map((thread) => (
            <CommandItem 
              key={thread.uuid} 
              onSelect={() => window.go.main.App.LoadThread(thread.uuid)}
            >
              {thread.title}
            </CommandItem>
          ))}
        </CommandList>
      </Command>
    </div>
  )
}

```

Why This Workflow Beats Using an Existing App

**Clean Main Loop:** You don't have to spend days stripping away someone else's authentication, local database setup, or arbitrary API clients. You start with standard `main.go` initialization.

**Design Velocity:** With standard layout engines, achieving the transparent, vibrant "Spotlight-style" look over the desktop background takes only 3 lines of configuration in Wails (`WindowIsTranslucent: true`) matched with Tailwind’s `backdrop-blur` utilities.

**Dependency Control:** Web wrappers break the moment Google changes a DOM selector. When you write the tiny injection snippets yourself, fixing a broken selector takes 10 seconds in a single string variable, rather than tracking down a deeply nested module inside a legacy codebase.

<!-- /gemini-message -->

---

<!-- gemini-message index=5 role=user timestamp="2026-07-09 21:49" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224668)

So I've been curious about shadcdn but I've basically decided Mantine is the way to go because, this is a "requirement" of what I want in my apps:




```

Human-Centric UI Architecture Rules




### 1. Styling Constraints

- DO NOT use Tailwind CSS, utility-class frameworks, or inline styles.

- Use standard, vanilla CSS via CSS Modules (`*.module.css`).

- Keep presentation layout separate from logic. A human must be able to open the `.css` file and tweak margins, colors, and padding using standard web specifications.




### 2. File Organization & Discoverability

- Every UI component must live in its own dedicated directory named after the component (PascalCase).

- Absolute ban on multi-component files. If a component requires a sub-item (like a list row), spin it out into its own folder.

- File structure must mirror visual hierarchy where practical.




### 3. DOM Tagging for Human Maintenance

- The top-level element of every component must include a descriptive `data-ui` attribute matching the component or feature name (e.g., `data-ui="midi-track-row"`).

- This is a strict requirement to allow human operators to use browser developer tools to inspect an element and instantly map it back to the source file via global search.

```




And that leads into another thing: LOTS of exposed variables.

The structure of the app should basically be: a user-facing config that's extremely powerful, as well as SCSS that's well organized so I can easily edit the UI if I so choose; and then the code which I will almost never touch myself.

<!-- /gemini-message -->

---

<!-- gemini-message index=6 role=assistant timestamp="2026-07-09 21:49" -->

---
## MODEL (2026-08-13T18:54:11.224669)

This is a rigorously disciplined approach to UI architecture. While utility classes like Tailwind offer speed in the short term, the constraints you have outlined prioritize long-term maintainability, debugging, and a strict separation of concerns.

Choosing Mantine over `shadcn/ui` for this specific philosophy is the right call, specifically because of the architectural shift Mantine made in its v7 release. They completely stripped out their CSS-in-JS engine (Emotion) and rebuilt the entire library natively around **Vanilla CSS, CSS Modules, and standard CSS variables**.

Here is how your structural rules map directly to Mantine's current capabilities, and how you can implement that powerful variable-driven configuration.

1. Styling Constraints (CSS Modules)

Mantine v7 is built for CSS Modules out of the box. Instead of inline styles or utility strings, every complex component exposes a `classNames` prop (plural) that allows you to target its internal DOM structure using your own isolated `.module.css` files. Your React code remains entirely structural.

TypeScript

```
// FloatingSearch.tsx
import { TextInput } from '@mantine/core';
import classes from './FloatingSearch.module.css';

export function FloatingSearch() {
  return (
    <TextInput
      classNames={{
        root: classes.searchRoot,
        input: classes.searchField,
      }}
    />
  );
}

```

2. File Organization

By strictly enforcing PascalCase directories (e.g., `FloatingSearch/FloatingSearch.tsx` and `FloatingSearch/FloatingSearch.module.css`), you ensure that anyone auditing the code can immediately locate the visual logic. Mantine's modular import system makes it easy to isolate sub-components into their own directories without tangling the root application flow.

3. DOM Tagging & Discoverability

Your requirement for a `data-ui` attribute is fully supported without any messy workarounds. Mantine natively forwards standard HTML attributes and custom `data-*` attributes directly to the underlying DOM node. When you inspect the element in the browser tools, your tracking tags will be immediately visible and cleanly formatted.

TypeScript

```
<TextInput
  data-ui="floating-search-input"
  placeholder="Ask anything..."
/>

```

The "Exposed Variables" Architecture

This is where Mantine will heavily support your goal of rarely touching the React source code.

Mantine dynamically generates hundreds of CSS variables at the `:root` level (e.g., `--mantine-color-blue-filled`, `--mantine-spacing-md`, `--mantine-radius-sm`). To build your powerful configuration engine, you handle styling entirely through variable overrides:

**The SCSS Layer:** You can write highly organized SCSS files that override Mantine's default CSS variables globally or introduce your own custom component variables (e.g., `--app-floating-bg-opacity`).

**The User Config Layer:** You can map user inputs from your config file directly to the `MantineProvider` theme object on application initialization. Mantine automatically parses that theme object and injects the corresponding CSS variables directly into the DOM tree.

The React components simply consume these variables, remaining entirely isolated from the actual styling values.

How are you planning to manage the state of this user-facing config—will it read from a static configuration file stored locally on the OS, or will it be a dynamic settings menu within the UI itself that updates state on the fly?

<!-- /gemini-message -->

---

<!-- gemini-message index=7 role=user timestamp="2026-07-09 21:49" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224671)

Are there any other smart early decisions I can make to make my life easier in the long run?

<!-- /gemini-message -->

---

<!-- gemini-message index=8 role=assistant timestamp="2026-07-09 21:49" -->

---
## MODEL (2026-08-13T18:54:11.224672)

Because you are building a wrapper around live web apps inside a native OS shell, you are going to run into "unknown unknowns" involving authentication, OS window managers, and Google's frontend updates.

Based on your exact stack (Wails v3 + Mantine v7 + background webview), here are the smartest architectural decisions you can make on day one so you don't have to rewrite the core logic in a month.

1. Externalize the DOM Selectors (The Anti-Breakage Config)

Google and Perplexity update their UI constantly. If you hardcode `document.querySelector('div[contenteditable="true"]')` inside your Go codebase or injected JS files, the app will break the moment Google changes a class name, and you will have to recompile the entire binary to fix it.

**The Decision:** Make `selectors.json` a core part of your user-facing configuration file. Go should read this file on boot and pass it into the webview execution scripts. When Gemini changes their input class to `.g-input-v2`, you (or your users) just update the JSON text file and restart the app. Zero recompiling.

2. The "Debug/Auth" Hotkey (Crucial for Web Wrappers)

Your background webview is hidden. What happens when Google logs you out? What happens when Perplexity throws a Cloudflare Turnstile CAPTCHA? If the window is hidden, the app just silently breaks and you won't know why.

**The Decision:** Build a developer toggle immediately. Map a global shortcut (e.g., `Cmd+Option+Shift+D`) that triggers `backgroundWindow.Show()`, drops the transparency, and makes it a standard OS window. You need to be able to instantly surface the hidden browser to log in, clear CAPTCHAs, or open the developer console to inspect DOM changes.

3. The "Max-Bounds" Frameless Window Trick

When working with frameless, transparent, dynamic-height windows, OS window managers (especially on Windows) have a notorious quirk: if you initialize a transparent window at 400x100 pixels, and then dynamically resize the window to 400x800 to show a long Gemini response, the OS often fails to update the "hit-test" region [1]. The newly expanded area will be visible, but your mouse clicks will pass right through it into the desktop behind it.

**The Decision:** Do not dynamically resize the Wails window on the fly. Instead, initialize the floating Wails window at the *maximum* expected size (e.g., 800x1000) but set the Wails window background to 100% transparent. Inside React, your Mantine container will be the only thing with a visible background. When the Gemini response comes in, you are just animating the Mantine `div` to grow taller inside the already-large, invisible Wails bounding box.

4. The Config-to-Mantine Pipeline

You want an extremely powerful user-facing config that dictates the UI without touching the code.

**The Decision:** Funnel your configuration file directly into Mantine's `theme` object. When your React app boots, fetch the config payload from Go, map the user's styling choices into a Mantine theme override, and pass it to `<MantineProvider theme="{dynamicTheme}">`. Mantine will automatically parse that JSON and inject the corresponding `--mantine-*` CSS variables into the `:root` DOM level. Your CSS Modules just consume those variables, keeping your logic perfectly separated from presentation.

5. Centralized Event Dictionary

Wails v3 uses an event emitter system (`Emit`, `On`) to allow multiple windows to talk to each other [1]. If your floating window starts throwing raw string events at the hidden Gemini window, it will become an unmaintainable mess.

**The Decision:** Create a single `events.ts` (or `.js`) file that acts as your dictionary. Never type a raw string like `window.go.main.App.SendKey()`. Use constants (e.g., `EVENTS.INJECT_KEYSTROKE`, `EVENTS.THREAD_LIST_SYNCED`). This guarantees that if you ever need to track down how data moves between the floating UI and the hidden webview, you just global-search the event constant.

<!-- /gemini-message -->

---

<!-- gemini-message index=9 role=user timestamp="2026-07-09 21:49" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224673)

1. YES absolutely, and this leads me into a big idea: I'm getting into the idea of self-improving apps. Basically, a way for the app to reliably be able to conduct an audit of itself and have an agent do a fix.

I mean, first of all, yes, while working on this stuff, agents must ALWAYS try to use as robust and clever of selectors as possible, ideally with a few fallbacks. That means, never relying on class names, using clever selectors like based on internal text content. But in the end, nothing is safe and things WILL break. Your idea is a great step in the right direction, but I think we want to think about this more. Even if it just gives me a nice prompt for me to paste somewhere to fix the issue when it arises, that's better than nothing.




I like everything else you wrote.

<!-- /gemini-message -->

---

<!-- gemini-message index=10 role=assistant timestamp="2026-07-09 21:49" -->

---
## MODEL (2026-08-13T18:54:11.224674)

This "Self-Improving App" architecture moves you from merely *wrapping* a web app to *maintaining* a living integration. Since you want to move beyond simple manual config updates, here is how you build a **Self-Healing Observer Pattern** into your Wails+Mantine stack.

1. The "Observer-Reporter" Agent Loop

Instead of waiting for you to notice the UI is broken, you build a lightweight Go-side "Health Monitor" that runs alongside your background webview.

**The Diagnostic Hook:** Create a Go-side function that periodically injects a "Stability Check" script into the hidden Gemini webview. This script doesn't look for data; it looks for the presence of the UI nodes your app relies on (the `contenteditable` prompt, the thread sidebar).

**The Failure Report:** If the query `document.querySelector(...)` returns `null` for a core element, the observer triggers a **Diagnostic Snapshot**. This snapshot grabs the current DOM hierarchy (the full tree, or at least the relevant slice), packages it into a JSON blob, and sends it to your LLM agent of choice.

**The Auto-Fix Pipeline:** The LLM receives the broken DOM structure, the failed selector, and your `selectors.json`. It generates a new, robust selector (e.g., using `aria-label` or `xpath` traversal based on text proximity) and sends back a JSON patch for your `selectors.json`.

2. Implementation: The "Prompt-Generator" Workflow

You mentioned that even a prompt to paste is better than nothing. You can automate the generation of this "Fix Prompt" so the agent doesn't just tell you it's broken—it hands you the solution.

When the "Observer" detects a selector failure:

**State Capture:** The Go layer triggers a `CaptureDOMState()` function.

**Context Assembly:** It packages:

The current `selectors.json`.

The specific DOM structure of the broken container.

The error log from the browser console.

**Agent Prompt Generation:** Your app automatically writes to your clipboard (or a local log file) a pre-formatted prompt:

"The following selector for the Gemini webview has failed: `[FAILED_SELECTOR]`. Based on the attached DOM snapshot, identify the new attribute or text-based path that uniquely targets this element. Return only the corrected JSON entry for `selectors.json`."

3. Making Selectors "Clever" (Beyond Class Names)

To make your selectors harder to break, your Go logic should force the injected JS to use **Functional Selectors**. Do not let your agent generate CSS class-based paths. Force it to generate:

**Aria-Label pathing:** `//div[@aria-label='Prompt textarea']`

**Text-content traversal:** `//div[contains(text(), 'Type your message')]`

**Data-attribute anchoring:** If Google adds a new `data-test-id` or similar, anchor to those.

4. Smart Early Decisions for Self-Healing

To support this "Self-Improving" vision, start with these two code-level decisions:

**Registry Pattern for Selectors:** In your Go code, never call `document.querySelector` directly in your business logic. Create a central `SelectorRegistry` service. All your UI interactions must call `Registry.Get("gemini-input")`. This abstraction layer is what allows you to hot-swap selectors from your `selectors.json` without touching a single line of React or Go code.

**Event-Driven DOM Heartbeat:** Create a `heartbeat.ts` script that runs in the background. If it fails to find a selector, it emits a `DOM_FAILURE` event via the Wails runtime. Your main Go process listens for this event and instantly halts all interaction, preventing the "blind" keystroke injection that happens when the selector points to the wrong element.

How do you want to handle the "Fix" itself? Should the app automatically overwrite the `selectors.json` file once you approve the agent's fix, or do you want to maintain a manual "Review & Apply" gate for every patch?

<!-- /gemini-message -->

---

<!-- gemini-message index=11 role=user timestamp="2026-07-10 00:07" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224676)

Cancel
Update

<!-- /gemini-message -->

---

<!-- gemini-message index=12 role=assistant timestamp="2026-07-10 00:07" -->

---
## MODEL (2026-08-13T18:54:11.224677)

You stopped this response

<!-- /gemini-message -->

---

<!-- gemini-message index=13 role=user timestamp="2026-07-10 00:08" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224678)

Act as a Product Manager. We are closing the brainstorming phase. Synthesize our agreed-upon concept into a strict High-Level Plan outlining what this feature DOES and the exact user experience.




Strictly avoid discussing how it is built under the hood. Structure your response using this exact framework:

1. The Trigger: How the user or system initiates the action.

2. The Staging Area: The intermediate UI, choices, or routing that happens before execution.

3. Task Configuration: The rules, modes, or constraints applied to the task.

4. Execution & Feedback: What happens during the process and how the user knows it finished.




</end system instruction>

ok I want you to simply collect everything we've talked about in this thread but obviously clean it up a bit; when we discuss different strategies and pick one of them, we just need to know what we picked in the end.

But I want everything we talked about, just a bit more concisely.

<!-- /gemini-message -->

---

<!-- gemini-message index=14 role=assistant timestamp="2026-07-10 00:08" -->

---
## MODEL (2026-08-13T18:54:11.224679)

This synthesis closes the brainstorming phase and establishes the baseline product requirements for the "AI Spotlight" project.

Decisions Summary

We have locked in the following core architecture based on our discussions:

**Platform:** Wails v3 (utilizing native multi-windowing).

**UI Architecture:** Mantine v7 + CSS Modules (strict file separation, human-readable styling, `data-ui` tagging).

**Core Functionality:** Multi-provider (Gemini/Perplexity) wrapper with real-time keystroke injection into a hidden webview.

**Maintenance Strategy:** Centralized "Selector Registry" with an agentic self-healing loop for automated DOM updates.

High-Level Product Plan
1. The Trigger

The user initiates the interface via a global system hotkey. This summons a transparent, always-on-top, frameless floating input window regardless of the currently active application.

2. The Staging Area

Upon invocation, the floating window provides:

**Immediate Input:** A focused, minimalist text field ready for direct interaction.

**Fuzzy Thread Search:** A command-palette interface allows the user to perform fuzzy searches through indexed historical threads. Selecting a thread immediately loads it into the background view.

**Session Context:** The UI displays the current active provider (e.g., Gemini or Perplexity) and indicates the connectivity status of the background session.

3. Task Configuration

Users manage the behavior of the interaction via a local configuration layer:

**Provider Selection:** Toggle between supported web services.

**Self-Healing Mode:** Users define the automation level for the selector registry (e.g., "Manual Review" requires the user to approve LLM-generated selector patches; "Auto-Apply" silently updates the registry).

**Selector Robustness:** Configuration of fallback logic, allowing the system to attempt multiple retrieval methods (text-based, aria-label, etc.) before flagging a failure.

4. Execution & Feedback

**Interaction:** As the user types, keystrokes are mirrored instantly to the background service. The floating interface remains compact during initial input.

**Expansion:** Upon submission, the interface dynamically expands to present the response stream, transitioning from the compact input shell to a reader view.

**Completion & Stability:** Once the streaming completes, the window remains open for further interaction. If the system detects a DOM mismatch (UI change), the interface provides an "Integrity Warning" and, if enabled, presents the agent-suggested fix for the user to review or the system to apply.

**Full Context Switch:** A dedicated button allows the user to surface the background webview as a standard OS window for deep session management (e.g., handling logins, persistent authentication, or browsing history).

<!-- /gemini-message -->

---

<!-- gemini-message index=15 role=user timestamp="2026-07-10 00:09" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224680)

Act as a Systems Architect. Translate our approved High-Level Plan into a Lower-Level Technical Plan.




Focus on the plumbing and architecture. You may include hyper-specific, uncommon code snippets if they are necessary to illustrate an architectural choice (e.g., a specific Rust/Tauri bridge implementation or complex API endpoint), but do not write the standard implementation logic.




Break down the architecture into:

1. Tech Stack & CLI Tools: Required packages or background processes.

2. Component Bridge: How the layers communicate (e.g., file watchers, HTTP, standard I/O).

3. State & Context Management: Where temporary data or files live during execution.

4. Technical Bottlenecks: Highlight 2-3 edge cases or potential fail states to watch out for.

<!-- /gemini-message -->

---

<!-- gemini-message index=16 role=assistant timestamp="2026-07-10 00:09" -->

---
## MODEL (2026-08-13T18:54:11.224681)

1. Tech Stack & CLI Tools
Backend Core

**Go 1.26+ & Wails v3:** Multi-window desktop runtime leveraging native WebKit (macOS) or WebView2 (Windows) engine layers without an embedded Chromium overhead.

**Wails v3 CLI (`wails`):** Used for code generation, binding generation, and cross-platform compilation pipelines.

Frontend Shell

**React 19 & Vite:** Core application frame optimized for HMR and rapid rendering performance.

**Mantine v7:** Core UI component library compiled entirely using Vanilla CSS and CSS Modules.

**PostCSS & Sass/SCSS:** Handles scoping, nesting, and variable propagation through standard `.module.css` and global configuration files.

2. Component Bridge

The application utilizes a two-tier IPC bridge managed by the Wails v3 engine to communicate across three distinct execution spaces: the Floating UI Window, the Main Go Process, and the Hidden Webview Instance.


```
+-------------------+                    +-------------------+
|  Floating UI      | --- Wails Bind --->|  Main Go Process  |
|  (Mantine v7)     |                    |  (Application)    |
+-------------------+                    +-------------------+
                                                   |
                                            Window.ExecJS()
                                                   v
                                         +-------------------+
                                         |  Hidden Webview   |
                                         |  (Gemini Live)    |
                                         +-------------------+

```

Floating UI → Go Layer

Events (such as real-time keystroke sequences or thread selection IDs) hook into auto-generated Javascript bindings generated at compile time.

Go Layer → Hidden Webview

The Go runtime acts as the structural orchestrator. It receives raw telemetry from the floating UI, coordinates with a local registry, and safely executes synthetic script execution within the unmapped window frame.

Go

```
package main

import (
	"encoding/json"
	"fmt"
	"github.com/wailsapp/wails/v3/pkg/application"
)

type BridgeService struct {
	app           *application.App
	hiddenWindow  *application.WebviewWindow
	selectorsFile []byte
}

type SelectorRegistry struct {
	InputArea string `json:"input_area"`
}

// InjectKeystroke channels raw string payloads into the unmapped target frame
func (b *BridgeService) InjectKeystroke(inputString string) {
	var registry SelectorRegistry
	if err := json.Unmarshal(b.selectorsFile, &registry); err != nil {
		return
	}

	// Escaping payload to prevent injection vulnerabilities inside the target webview execution context
	escapedPayload, _ := json.Marshal(inputString)

	jsPayload := fmt.Sprintf(`(() => {
		const target = document.querySelector('%s');
		if (!target) {
			window.runtime.EventsEmit("DOM_FAILURE", "input_area");
			return;
		}
		target.focus();
		// Direct DOM value mutation with synthetic input dispatching to satisfy framework event loops
		if (target.isContentEditable) {
			target.innerText = %s;
		} else {
			target.value = %s;
		}
		target.dispatchEvent(new Event('input', { bubbles: true }));
	})();`, registry.InputArea, escapedPayload, escapedPayload)

	// Execute execution loop within the context of the hidden window
	b.hiddenWindow.ExecJS(jsPayload)
}

```

Hidden Webview → Floating UI (Via Go)

A headless monitoring script injected into the background window binds to Wails' runtime event engine. When mutations are noticed inside the DOM response container, it calls `window.runtime.EventsEmit("STREAM_CHUNK", payload)`, which the Floating UI swallows and renders natively.

3. State & Context Management
Ephemeral App State

Application state is centralized inside the Go architecture rather than trusting the volatile frontend JS state engine.

**The Global Window Router:** Tracks layout vectors, window visibility states, and active provider routes (`gemini` vs `perplexity`).

Storage & Configuration Paths

Persistent files reside strictly within the user’s standard OS sandbox (`~/.config/ai-spotlight/` on macOS).

**`selectors.json`:** The decoupled object mapping logical interaction tokens to target DOM paths.

**`config.json`:** Holds structural theme parameters. On app initialization, Go processes this file and converts keys into a flat map of layout variables. These map directly into Mantine’s dynamic component provider at the root level, updating design layers without recompiling.

**`threads_cache.json`:** A flat index containing scraped thread data (`uuid`, `title`, `timestamp`, `provider`). The frontend pulls this localized file directly into memory during boot to power the fuzzy searching component, preventing network bottlenecks when invoking the search bar.

4. Technical Bottlenecks
IPC Saturation & Frame Dropping

**The Fail State:** Direct key-by-key execution across an asynchronous IPC bridge during high-speed typing (100+ WPM) creates a race condition. Wails event handling loops can become choked, causing synthetic script execution to append characters out of order in the target webview.

**Mitigation:** Replace the direct raw keystroke transmission model with a lightweight frame-based synchronization loop. The frontend debounces short blocks (e.g., 16ms intervals matching standard frame refresh rates) and transmits the complete incremental text diff, rather than relying on individual key-down event processing.

DOM Sandbox Interaction Constraints

**The Fail State:** Modern web applications running complex single-page apps (like Google Gemini) explicitly prevent programmatic text updates to `contenteditable` wrappers if standard keyboard interaction objects are missing (`isTrusted` property checks). Mutating `.innerText` or `.value` directly will update the visual element, but internal React/Angular state engines will ignore the update, resulting in empty query submittals.

**Mitigation:** The injected logic must simulate a sequential event chain. The bridge focuses the target node, utilizes native text insertion directives (`document.execCommand('insertText', false, text)`), or sequentially fires a sequence of `CompositionEvent` primitives to safely simulate standard typing input loops.

<!-- /gemini-message -->

---

<!-- gemini-message index=17 role=user timestamp="2026-07-10 00:10" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224683)

Assess the high- and low-level plans and improve them.

Then provide me with the improved versions.

<!-- /gemini-message -->

---

<!-- gemini-message index=18 role=assistant timestamp="2026-07-10 00:10" -->

---
## MODEL (2026-08-13T18:54:11.224684)

An assessment of the initial specifications reveals three critical structural blind spots that would cause failures during implementation:

**Window Focus & Dismissal Lifecycle:** The high-level plan details invocation but fails to define the dismissal behavior (e.g., blur events, loss of focus, or explicit escape sequences) required for a true Spotlight-style utility.

**Cookie & Session Persistence:** The low-level plan overlooks webview session persistence. By default, headless webviews can reset state on application restart, requiring you to re-authenticate with Google/Perplexity every time the app boots.

**Text Cursor Desynchronization:** Real-time keystroke or diff injection into a `contenteditable` container natively forces the text cursor (caret) to jump back to the beginning or end of the field on mutation, breaking the fluid typing experience.

The improved versions below resolve these bottlenecks while maintaining your exact structural constraints and architectural principles.

Improved High-Level Plan
1. The Trigger

**Activation:** The user invokes a global system hotkey combination to summon the frameless, transparent input shell instantly over any active application.

**Dismissal:** Pressing `Escape` or clicking anywhere outside the bounds of the floating application immediately dismisses the window, returning focus cleanly to the underlying OS layer without terminating active background processes.

2. The Staging Area

**Contextual Focus:** Upon invocation, the system places explicit focus on the custom text input area.

**Fuzzy Thread Command Palette:** Typing a specific control prefix (e.g., `/`) transforms the input field into a local historical database query tool. It filters downloaded thread histories by title, keyword, or provider instantly.

**Instantiation Routing:** Selecting an existing thread via the search index updates the hidden view to that URL state. Typing directly into the clean canvas defaults to preparing a brand new thread.

3. Task Configuration

**Provider Swapping:** A fast hotkey (e.g., `Cmd+P`) toggles the underlying target engine between Google Gemini and Perplexity.

**Self-Healing Thresholds:** Users can dictate the validation rules for selector adjustments via a configuration file, choosing between an automated background overwrite or a manual dashboard review step before modifications are applied to live files.

4. Execution & Feedback

**Fluid Expansion:** Submitting a prompt expands the vertical profile of the visible Mantine container to present incoming text streams parsed directly from the background application webview.

**Stateful Context Transition:** Clicking the "Expand to Full Window" control unhides the native background browser window instantly, preserving the exact scroll position, entered text, and thread history without reloading the page.

**Integrity Monitoring:** A background watcher tracks selector validity. If Google changes their DOM properties, an indicator changes state, and a formatted fix prompt containing the layout error is copied directly to the clipboard.

Improved Low-Level Technical Plan
1. Tech Stack & CLI Tools

**Backend Runtime:** Go 1.26+ utilizing the Wails v3 engine for low-overhead multi-window orchestration.

**Frontend Framework:** React 19 + Vite initialized via a clean asset pipeline using PostCSS and Sass/SCSS.

**Styling Engine:** Mantine v7 combined with standard CSS Modules (`*.module.css`) to enforce strict isolation between presentation styling variables and application logic.

2. Component Bridge

Communication uses asynchronous message loops over the Wails IPC channel to prevent frame rendering bottlenecks.

Go

```
package main

import (
	"encoding/json"
	"fmt"
	"github.com/wailsapp/wails/v3/pkg/application"
)

type TokenDiff struct {
	Text string `json:"text"`
}

type BridgeService struct {
	app          *application.App
	hiddenWindow *application.WebviewWindow
}

// SyncInput Buffer handles incremental updates to secure cursor layout position
func (b *BridgeService) SyncInput(payloadJSON string) {
	var diff TokenDiff
	if err := json.Unmarshal([]byte(payloadJSON), &diff); err != nil {
		return
	}

	escapedText, _ := json.Marshal(diff.Text)

	// Employs modern selection ranges instead of basic value mutation to avoid resetting caret placement
	jsPayload := fmt.Sprintf(`(() => {
		const target = document.querySelector('div[contenteditable="true"]');
		if (!target) return;
		
		target.focus();
		// Utilize Selection and Text Insertion API to maintain text caret placement transparently
		const selection = window.getSelection();
		if (selection.rangeCount > 0) {
			document.execCommand('selectAll', false, null);
			document.execCommand('insertText', false, %s);
		}
	})();`, escapedText)

	b.hiddenWindow.ExecJS(jsPayload)
}

```

3. State & Context Management

**Persistent User Sandboxing:** To resolve authentication loss, the Go application configuration explicitly mounts a static directory path to the native window instance:

Go

```
// In main.go window configuration loop
wailsApp.NewWebviewWindowWithOptions(application.WebviewWindowOptions{
    Name: "background_session",
    StartHidden: true,
    MacOptions: application.MacWebviewWindowOptions{
        UserDataFolder: "~/.config/ai-spotlight/browser_profile",
    },
})

```


This setup ensures cookies, authentication tokens, and session databases persist natively across application reboots.

**Theme Processing:** Local configurations read directly from `~/.config/ai-spotlight/config.json`. These properties map straight to Mantine's dynamic theme provider at runtime, populating global CSS variables without hardcoded style paths.

4. Technical Bottlenecks
Bottleneck	Risk	Mitigation
**Caret Position Reset**	Writing text directly to `.innerText` or `.value` via `ExecJS` moves the target input cursor to position 0 on every update, scrambling real-time typing.	Use `document.execCommand('insertText')` or execute programmatic text updates inside the webview using native clipboard simulation events instead of string reassignment.
**Authentication Expiry**	Headless windows logging out or hitting CAPTCHA checks results in total failure of data scraping streams.	Implement a global fallback macro (`Cmd+Option+Shift+D`) that changes window parameters instantly to make the hidden window visible, allowing for manual session resolution.
**Fuzzy Index Latency**	Querying a massive JSON thread index inside a standard Go loop for every keystroke adds processing lag to the input window.	Offload the thread cache file entirely to the frontend memory space on application initialization. Use `fuse.js` or `cmdk` to run calculations completely inside the user's view layer.

<!-- /gemini-message -->

---

<!-- gemini-message index=19 role=user timestamp="2026-07-10 00:27" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224685)

I suppose while we're doing this...

I also plan on implementing these things:




1. I have gemini threads saved locally.




'/Users/matt/Library/Mobile Documents/com~apple~CloudDocs/Gemini Archive/threads/mounjaro-hunger-and-nausea-management--c624ff4c2acdf08a.md':

```

<!-- /gemini-message -->
---

source: "gemini.google.com"

conversation_id: "c624ff4c2acdf08a"

title: "Mounjaro Hunger and Nausea Management"

source_url: "https://gemini.google.com/app/c624ff4c2acdf08a"

archived_at: "2026-07-10T05:30:57.137Z"

message_count: 8

---

# Mounjaro Hunger and Nausea Management




<!-- gemini-message index=1 role=user timestamp="2026-07-09 18:06" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224686)

[2026-07-09 18:02 MDT-6] on mounjaro, I legitimately forget to eat. Suddenly I get hit with a kind of intense hunger, and it's weird because I'm hungry and I'm reminded that I kind of "have to" eat something, and if I've waited too long, I'm a kind of hungry where I don't really have an appetite, and I almost feel sick about the notion of eating.




<!-- /gemini-message -->




---




<!-- gemini-message index=2 role=assistant timestamp="2026-07-09 18:06" -->

---
## MODEL (2026-08-13T18:54:11.224688)

This is for informational purposes only. For medical advice or diagnosis, consult a professional.

Gemini said




That "hungry but completely turned off by the idea of food" paradox is a classic GLP-1 side effect. When Mounjaro delays gastric emptying and alters central appetite signals, the normal transition from full to empty gets muted. By the time your body finally overrides the medication to scream "we need fuel," your blood sugar has often dipped, and an empty stomach under those conditions frequently triggers nausea instead of a healthy appetite.




When you hit that wall where you know you need to eat but the thought of a full meal makes you sick, forcing down a heavy plate usually backfires. Shifting the strategy often helps get past that specific block:




**Liquid or semi-liquid first:** A small protein shake, a cup of bone broth, or even a bit of yogurt is usually much easier to tolerate than solid food when you feel nauseous. It coats the stomach and gets some quick nutrients in to stabilize your blood sugar.




**Bland, calorie-dense bites:** A few crackers, a spoonful of peanut butter, or a piece of toast can break the fasting cycle without triggering a gag reflex. Once your blood sugar starts to stabilize, the nausea often subsides enough for a real meal.




**Mechanical eating:** Because the natural "bues" are gone, relying on a loose schedule or a simple reminder to eat small, regular snacks *before* the intense hunger hits can prevent getting stuck in that nausea loop entirely.




<!-- /gemini-message -->




---




<!-- gemini-message index=3 role=user timestamp="2026-07-09 18:06" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224689)

[2026-07-09 18:04 MDT-6] I'm trying to kind of make the most of the mounjaro, especially when it's working fabulously in the early stages.




Meaning, I should make a concerted effort to eat healthfully, and just go through the motions and eat something light at certain times even though I'm not hungry, just to basically build the habit that: "at noon I eat a thing of yogurt and some cheerios"




<!-- /gemini-message -->

...

```




I want my app to be able to do a lightning fast fuzzy search of all user and model text, and to display the matching threads in a list that is ordered based on several factors, but a heavy weighting is: most recently edited thread is at the top.

When I click on a thread it should open in the webview by just going to `https://gemini.google.com/app/<uuid>`




---




2.

We are implementing an incremental, context-driven Screen Capture Engine into the application framework. The roadmap scales from instant single-frame captures to complex, chronological multi-frame state tracking.




Architecturally, this requires setting up a decoupled, flexible Context Assembly Pipeline right now:




What we are doing: Designing a system that captures bounded screen regions, pairs those visual states with user intent (text queries), and structures them into sequential payloads for multimodal LLM consumption.

The phased progression: It begins as an immediate, hotkey-driven single screenshot utility (Phase 1), expands into a manual sequential multi-image storyboarding tray (Phase 2), and eventually integrates a background perceptual frame-differencing loop to automate sequence tracking based on active UI state changes (Phase 3).

Architectural requirements: To prevent major refactors down the line, the app’s internal prompt-building layer must treat visual context as a chronologically ordered array of images from day one, rather than a single static file. The capture module must also decouple coordinates and sampling logic from the output delivery system so we can easily swap a manual trigger for a background polling daemon when moving to later phases.

<!-- /gemini-message -->

---

<!-- gemini-message index=20 role=assistant timestamp="2026-07-10 00:27" -->

---
## MODEL (2026-08-13T18:54:11.224691)

Integrating full-text local search and a chronologically aware screen capture pipeline requires significant structural additions to the Go backend. Relying on frontend Javascript to parse thousands of multi-kilobyte Markdown files will crash the Wails memory boundary, and retrofitting an array of images into a single-string prompt injection will fail.

Here is the architectural expansion to accommodate these two major systems.

Expanded Low-Level Technical Plan
5. Local Full-Text Search Engine (Markdown Archival)

To achieve "lightning-fast" queries across both user and model text while prioritizing recency, the fuzzy search cannot live in the frontend `fuse.js` implementation. It must be offloaded to a Go-native database utilizing a Full-Text Search extension.

**The Indexing Daemon:** On application boot, a Go routine scans the `~/.../Gemini Archive/threads/` directory. It uses a Markdown parser to separate the YAML frontmatter (extracting `conversation_id` and `archived_at`) from the raw body text.

**The Storage Layer (SQLite + FTS5):** Go writes the parsed data into a local SQLite database configured with a virtual `FTS5` table. SQLite FTS5 natively supports extremely fast text indexing.

**Weighting & Execution:** When the user types in the Mantine command palette, Wails fires the query to Go. The Go layer executes a SQL query combining the FTS5 `rank` (BM25 relevance algorithm) with a chronological sort:

SQL

```
SELECT conversation_id, title, archived_at 
FROM threads_fts 
WHERE threads_fts MATCH ? 
ORDER BY rank, archived_at DESC LIMIT 20;

```


**Routing:** The resulting array is sent back to the UI. Upon selection, Go executes `b.hiddenWindow.LoadURL("[https://gemini.google.com/app/](https://gemini.google.com/app/)" + selectedUUID)`.

6. Multimodal Context Assembly Pipeline

To support the phased rollout (single capture → storyboard tray → automated diffing), the prompt data structure must be decoupled from the raw string input on day one.

**Phase 1 Architecture (Data Structures):**
The prompt is no longer a string; it is a Chronological Context Object.

Go

```
type VisualContext struct {
    Timestamp int64  `json:"timestamp"`
    MimeType  string `json:"mime_type"`
    Base64    string `json:"base64_data"`
}

type ContextPayload struct {
    Text   string          `json:"text"`
    Images []VisualContext `json:"images"` // Ordered array from day one
}

```


**Phase 1 Architecture (Capture & Injection Bridge):**

**The Capture Trigger:** A Go-side global hotkey listener triggers a native OS capture (e.g., via macOS `ScreenCaptureKit` bindings or standard `screencapture` CLI execution mapped to the clipboard/temp file).

**The Staging Tray:** The Mantine UI maintains a local state array of these captured frames rendered as thumbnails below the text input.

**The Injection Bottleneck:** You cannot inject images into Gemini by changing `.value` or `document.execCommand`. Web apps require real file uploads. The Go layer must package the `[]VisualContext` array, encode it to Base64, and pass it to the hidden webview. The injected script then reconstructs these into JavaScript `File` objects and simulates a native drag-and-drop `DataTransfer` event directly onto Gemini's input dropzone.

JavaScript

```
// Conceptual JS Injection for Image Payload
function simulateImageDrop(base64Image, mimeType) {
    const byteString = atob(base64Image);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    const file = new File([ab], "context_frame.png", { type: mimeType });
    
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    
    // Dispatch onto Gemini's specific dropzone selector
    const dropEvent = new DragEvent("drop", {
        dataTransfer: dataTransfer,
        bubbles: true,
        cancelable: true,
    });
    document.querySelector('div[data-drop-target="true"]').dispatchEvent(dropEvent);
}

```


By structuring the payload as a chronologically sorted `[]VisualContext` array and injecting via a synthetic drop event, Phase 2 (manual sequencing) and Phase 3 (background frame diffing) will not require rewriting the injection bridge or the LLM prompt structure. The background daemon will simply push new `VisualContext` objects into the Mantine UI state array as they are generated.

<!-- /gemini-message -->

---

<!-- gemini-message index=21 role=user timestamp="2026-07-10 00:29" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224692)

Ok, I want you to give me the COMPLETE updated high level plan. Try not to miss anything we discussed.

<!-- /gemini-message -->

---

<!-- gemini-message index=22 role=assistant timestamp="2026-07-10 00:29" -->

---
## MODEL (2026-08-13T18:54:11.224693)

High-Level Product Plan
1. The Trigger

**Activation:** The user invokes a global system hotkey combination to instantly summon a frameless, transparent, always-on-top floating input shell over any active application.

**Dismissal:** Pressing `Escape` or clicking anywhere outside the bounds of the floating interface immediately dismisses the window, returning focus cleanly to the underlying OS layer without terminating active background processing loops or clearing input state.

2. The Staging Area

Upon invocation, the floating frame drops focus directly into a minimalist layout composed of three primary user experience zones:

**Primary Input:** A clean, focused text area designed for real-time prompt drafting.

**Contextual Command Palette:** Typing a specific control prefix (such as `/`) transforms the text area into an instantaneous search bar. This queries a localized archive of all historical Gemini threads, evaluating full text across both user prompts and model responses. Matching threads appear in a list heavily weighted by the most recent modification date. Selecting a historical thread immediately loads it into the background workspace via its unique identifier.

**Visual Storyboard Tray:** An integrated component tray located directly beneath the text input area. It displays a chronologically ordered horizontal sequence of thumbnail previews representing bounded screen region captures queued for multimodal analysis.

3. Task Configuration

Users manage execution behavior and background automation rules via intuitive shortcuts and persistent environment configurations:

**Provider Toggle:** A rapid keyboard macro (e.g., `Cmd+P`) swaps the active background target application instantly between Google Gemini and Perplexity.

**Screen Capture Modes:** A dedicated hotkey sequence takes localized screen captures, adapting seamlessly across three phases of scaling capability:

*Single-Frame Capture:* Captures an immediate, manual bounding box snippet and drops it into the staging tray.

*Manual Storyboarding:* Allows users to build sequential multi-image workflows by triggering successive captures before submitting the task.

*Automated Perceptual Polling:* Monitors active desktop UI changes in the background, automatically queuing relevant frames into the timeline tray based on visual deltas.

**Self-Healing Thresholds:** Configurable policy parameters that dictate how the application responds to target website design changes. The user can choose to have selector updates applied automatically in the background or routed through a manual review step.

4. Execution & Feedback

**Real-Time Synchronization:** As the user types into the custom floating interface, characters or structural text deltas sync instantaneously to the hidden webview application. The interface remains locked to its compact layout while input is actively happening.

**Dynamic Response Expansion:** Triggering the submission control commands the visible floating frame to expand its vertical footprint smoothly. The custom interface transitions into a structured reading layout that streams the live response text parsed directly from the background browser instance.

**Full Canvas Escalation:** A dedicated workspace button allows the user to cleanly unhide the background webview window at any time. This action instantly surfaces the native interface of the chosen provider (Gemini or Perplexity) as a standard OS window, preserving the exact scroll depth, conversation history, and authenticated session state.

**Integrity Alerts & Prompt Diagnostics:** If a background structural change or selector failure prevents the app from locating web inputs or reading a response stream, the interface changes state to show an "Integrity Warning." The application simultaneously assembles a diagnostic payload—combining the failed path, the broken DOM tree snippet, and fix instructions—and copies a pre-formatted improvement prompt directly to the system clipboard for immediate agent resolution.

<!-- /gemini-message -->

---

<!-- gemini-message index=23 role=user timestamp="2026-07-10 00:34" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.224695)

ok great, now the low level plan.

Remember our decisions!

<!-- /gemini-message -->

---

<!-- gemini-message index=24 role=assistant timestamp="2026-07-10 00:34" -->

---
## MODEL (2026-08-13T18:54:11.224696)

1. Tech Stack & CLI Tools
Backend Architecture

**Go 1.26+ & Wails v3:** Native cross-platform application wrapper leveraging lightweight, multi-window system webview runtimes (WebKit/WebView2).

**SQLite (with FTS5 compilation flag):** Local database embedded inside the Go layer to handle high-performance, full-text fuzzy index scoring across local text archives.

Frontend Presentation Layer

**React 19 & Vite:** Frontend UI development environment optimized for rapid asset compilation.

**Mantine v7:** Core UI framework built on standard web specifications, utilizing native CSS variables.

**PostCSS & Sass/SCSS:** Handles component isolation and token variables mapping.

2. Component Bridge & IPC Layout

The application utilizes a multi-process asynchronous IPC loop mediated by the Wails runtime. Communication is isolated across three distinct memory environments:


```
+------------------------------------+
|            Floating UI             |
|   (Mantine v7 + CSS Modules)       |
+------------------------------------+
                 ^
                 | Wails Bindings / IPC events
                 v
+------------------------------------+
|          Main Go Process           |
|  (SQLite FTS5, ScreenCaptureKit)   |
+------------------------------------+
                 ^
                 | WebviewWindow.ExecJS()
                 v
+------------------------------------+
|       Hidden Webview Window        |
|     (Gemini / Perplexity Live)     |
+------------------------------------+

```

Text Synchronization Bridge

To prevent input latency and UI stuttering, input deltas stream over the Wails event bus. The Go runtime continuously shifts focus and processes caret adjustments to ensure the hidden browser state matches the local shell layout:

Go

```
package bridge

import (
	"encoding/json"
	"fmt"
	"github.com/wailsapp/wails/v3/pkg/application"
)

type InputPacket struct {
	Content string `json:"content"`
}

type WebBridge struct {
	hiddenWindow *application.WebviewWindow
}

func (wb *WebBridge) SyncInputCanvas(payload string) {
	var packet InputPacket
	if err := json.Unmarshal([]byte(payload), &packet); err != nil {
		return
	}

	escapedText, _ := json.Marshal(packet.Content)

	// Injected execution loop targeting contenteditable elements without resetting selection offsets
	jsInjectedLoop := fmt.Sprintf(`(() => {
		const target = document.querySelector('div[contenteditable="true"]');
		if (!target) return;
		
		target.focus();
		const selection = window.getSelection();
		if (selection.rangeCount > 0) {
			document.execCommand('selectAll', false, null);
			document.execCommand('insertText', false, %s);
		}
	})();`, escapedText)

	wb.hiddenWindow.ExecJS(jsInjectedLoop)
}

```

Multimodal Upload Bridge

Because traditional file picker dialogs break inside headless window execution, images are uploaded into the target DOM using a programmatic drag-and-drop simulation engine:

Go

```
func (wb *WebBridge) InjectVisualContextArray(base64Payloads []string, mimeType string) {
	for _, b64 := range base64Payloads {
		jsPayload := fmt.Sprintf(`(() => {
			const rawData = atob("%s");
			const arrayBuffer = new ArrayBuffer(rawData.length);
			const uintArray = new Uint8Array(arrayBuffer);
			for (let i = 0; i < rawData.length; i++) {
				uintArray[i] = rawData.charCodeAt(i);
			}
			const file = new File([arrayBuffer], "capture.png", { type: "%s" });
			const dataTransfer = new DataTransfer();
			dataTransfer.items.add(file);
			
			const dropEvent = new DragEvent("drop", {
				dataTransfer: dataTransfer,
				bubbles: true,
				cancelable: true
			});
			
			const dropZone = document.querySelector('div[data-drop-target="true"]') || document.querySelector('input[type="file"]');
			if (dropZone) {
				dropZone.dispatchEvent(dropEvent);
			}
		})();`, b64, mimeType)
		
		wb.hiddenWindow.ExecJS(jsPayload)
	}
}

```

3. Human-Centric UI Architecture (Frontend Setup)

The presentation layer enforces isolated styling, strict component hierarchies, and visual tagging to ensure independent maintenance.

File Structure & Directory Blueprint

```
src/
├── components/
│   ├── FloatingSearch/
│   │   ├── FloatingSearch.tsx
│   │   ├── FloatingSearch.module.css
│   │   └── FloatingSearchRow.tsx
│   ├── StoryboardTray/
│   │   ├── StoryboardTray.tsx
│   │   └── StoryboardTray.module.css
└── styles/
    ├── variables.scss
    └── global.css

```

Code Implementation Rules

Every structural file exports exactly one component, isolates styling metadata within dedicated CSS Modules, and injects `data-ui` attributes into top-level DOM boundaries:

TypeScript

```
// src/components/FloatingSearch/FloatingSearch.tsx
import React from 'react';
import { TextInput } from '@mantine/core';
import classes from './FloatingSearch.module.css';

interface FloatingSearchProps {
  onInputChange: (val: string) => void;
}

export const FloatingSearch: React.FC<FloatingSearchProps> = ({ onInputChange }) => {
  return (
    <div className={classes.searchContainer} data-ui="floating-search-frame">
      <TextInput
        classNames={{
          root: classes.inputRoot,
          input: classes.inputField,
        }}
        data-ui="floating-search-input"
        placeholder="Ask anything..."
        onChange={(e) => onInputChange(e.target.value)}
      />
    </div>
  );
};

```

CSS Modules & Token Inheritance
CSS

```
/* src/components/FloatingSearch/FloatingSearch.module.css */
.searchContainer {
  background: var(--app-window-bg);
  backdrop-filter: blur(var(--app-window-blur));
  border-radius: var(--mantine-radius-md);
  padding: var(--mantine-spacing-md);
  box-shadow: var(--mantine-shadow-xl);
}

.inputField {
  background: transparent;
  border: none;
  font-size: var(--app-font-size-lg);
  color: var(--mantine-color-text);
}

```

4. Local Full-Text Search Engine

The fuzzy search system indexes and queries local markdown archives via an embedded database running asynchronously inside the Go execution space.

Target Parsing Sandbox

**Location:** `/Users/matt/Library/Mobile Documents/com~apple~CloudDocs/Gemini Archive/threads/`

**Workflow:** A file-watcher routine reads new files, strips YAML frontmatter structures, parses internal message boundaries (`<!-- gemini-message ... -->`), and streams normalized indices into SQLite.

Database Indexing Schema & Search Rank Query
SQL

```
-- Virtual FTS5 optimization table configuration
CREATE VIRTUAL TABLE IF NOT EXISTS threads_fts USING fts5(
    conversation_id UNINDEXED,
    title,
    content,
    archived_at UNINDEXED,
    tokenize="porter unicode61"
);

-- Compound recency and relevance scoring execution
SELECT conversation_id, title, archived_at, bm25(threads_fts, 2.0, 1.0) AS score
FROM threads_fts 
WHERE threads_fts MATCH ? 
ORDER BY score ASC, archived_at DESC 
LIMIT 25;

```

5. Multimodal Context Assembly Pipeline

Visual data inputs are modeled as chronological arrays, abstracting screen telemetry entirely away from the underlying prompt execution loops.

Data Schemas
Go

```
package pipeline

type VisualStateFrame struct {
	CaptureID string `json:"capture_id"`
	Timestamp int64  `json:"timestamp"`
	MimeType  string `json:"mime_type"`
	B64Data   string `json:"base64_data"`
}

type ChronologicalContextPipeline struct {
	UserPrompt   string             `json:"user_prompt"`
	TargetEngine string             `json:"target_engine"`
	VisualAssets []VisualStateFrame `json:"visual_assets"`
}

```

Phase Transition Blueprint

**Phase 1 (Immediate Build):** Global Hotkey records active coordinate layouts via a native shell execution utility, encodes the capture, and appends a `VisualStateFrame` to the current state payload array.

**Phase 2 (Storyboard Tray Extension):** The frontend receives individual frame objects, appending them as clickable components inside the `StoryboardTray` array to support manual frame rearrangement.

**Phase 3 (Perceptual Loop Automation):** An asynchronous background Go thread periodically samples target displays, computes perceptual hashes, and evaluates visual changes. If structural deltas cross a predefined variability threshold, the engine builds a new `VisualStateFrame` and pipes it straight to the active array without manual interaction.

6. Technical Bottlenecks & Protective Architecture
1. Webview Profile Invalidation & Persistent State Losses

**Risk:** Headless web instances occasionally clear transient cache directories on system reboots, killing active Google/Perplexity cookies and locking users out behind login walls.

**Mitigation:** The application enforces a static, dedicated `UserDataFolder` partition path in the platform setup. If an unexpected authentication drop happens, hitting `Cmd+Option+Shift+D` mutates window flags instantly, surfacing the background layer to let users complete standard web authentication directly.

2. State Dropping via Selection Layer Truncation

**Risk:** Forcing text updates using basic `.value` string concatenation causes single-page frameworks (React/Angular) running inside Gemini to drop underlying execution states. The input box updates visually, but submitting the prompt triggers an empty query error.

**Mitigation:** The Go injection engine completely avoids direct variable mutation. Instead, it interacts via native browser document mutation APIs (`document.execCommand('insertText')`), forcing target web application framework observers to process text injections as legitimate human inputs.

3. IPC Saturation During High-Speed Input Logs

**Risk:** Rapid key event generation over an asynchronous bridge can cause inputs to reach the hidden browser frame out of order.

**Mitigation:** The application utilizes an atomic text buffering engine. The React application captures input strings locally and transmits structural text deltas at set intervals matching display update frequencies (16ms frames) to safely decouple layout loops from network transmission logic.

<!-- /gemini-message -->
<!-- /gemini-message -->

---
