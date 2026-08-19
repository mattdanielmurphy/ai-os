---
title: "Tauri Slow Initial Startup Optimization"
date: "2026-08-13"
conversation_id: "f2e070f5-983f-5743-ae36-6c53960854d4"
source: "antigravity"
---

# Tauri Slow Initial Startup Optimization

## USER_EXPLICIT (2026-08-13T18:54:09.241940)

[2026-07-07 20:03 MDT-6] the one thing I don't love about tauri is how long it takes to start the app at first

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-07 20:07" -->

---
## MODEL (2026-08-13T18:54:09.241945)

The initial build and first cold boot times in Tauri can definitely feel like a massive drag. When you run `tauri dev` or `tauri build` for the very first time, cargo is compiling the entire Rust backend—including heavy dependencies like `tokio`, `serde`, and the underlying webview bindings—directly from source.

While subsequent builds use cached artifacts and are much faster, that initial spin-up or clean build can easily take several minutes.

If you want to shave down that first-run compile time and optimize your development loop, a few specific tweaks can help:

1. Optimize the Cargo Linker

The default linker on many systems is notoriously slow. Switching to a modern, concurrent linker like **Mold** (Linux) or **Zld** (macOS) makes a massive difference in linking times, which is a huge chunk of the initial compilation phase.

To switch linkers globally or per-project, you can configure your `.cargo/config.toml`:

Ini, TOML

```
# For macOS (using zld)
[target.x86_64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=zld"]

[target.aarch64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=zld"]

```

2. Split Your Front-End and Back-End Dev Servers

If you are waiting for the Tauri window to open just to test basic UI changes, you can bypass the Rust layer entirely during early development.

Run your front-end framework's dev server solo (e.g., `vite` or `next`).

Build your UI components directly in the browser.

Only spin up `tauri dev` when you need to test actual native API features (like file system access or window manipulation).

3. Check for Anti-Virus Interference

If you're on Windows, Windows Defender loves to deeply scan the hundreds of tiny build artifacts generated in the `src-tauri/target` folder during a fresh compilation. Adding your project directory to the Defender exclusion list can sometimes cut compilation times in half.

4. Cache Dependencies in CI/CD

If the long initial boot times are killing your automated builds or deployment pipelines, ensure you are caching the Cargo home and target directories.

YAML

```
- name: Cache Cargo data
  uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      src-tauri/target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

```


It doesn't completely eliminate the heavy lifting Rust has to do out of the gate, but minimizing the linking bottleneck and using the browser for pure UI work keeps you from staring at a blank compilation screen quite as often.

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="2026-07-07 20:07" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.241947)

[2026-07-07 20:03 MDT-6] is there a new tauri competitor that would beat it in this regard?

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-07 20:07" -->

---
## MODEL (2026-08-13T18:54:09.241949)

If your main goal is to bypass the heavy initial Rust compilation time while still getting a lightweight desktop app, there are a few newer and emerging players in the webview space that take entirely different architectural approaches.

Here are the most notable alternatives tackling that specific problem:

1. Electrobun (TypeScript + Bun)  
TeamDev

If you want to keep the system webview model (lightweight binaries like Tauri) but completely eliminate Rust from the equation, **Electrobun** is a fascinating new competitor.

**How it works:** It uses **Bun** as the backend runtime instead of Rust/Node and drives the OS system webviews (`WKWebView`, `WebView2`).

**The Boot/Build Advantage:** Because it’s pure TypeScript/JS running on Bun, there is **no heavy compilation step**. Your initial start time is essentially instantaneous, matching the rapid development loop of the web ecosystem.

2. Neutralinojs (Pure JS/C++ Wrapper)

Neutralino is an older project, but it has gained significant traction as a "lightweight webview framework without the Rust baggage."

**How it works:** Neutralino runs a single, lightweight portable C++ binary that spins up a local web server and opens the system webview. You write your backend logic directly in JavaScript using their built-in native API.

**The Boot/Build Advantage:** Zero compilation. You don't have a massive `target/` directory to build out of the gate. You clone a template, run `neu run`, and it opens immediately.

3. Perry (TypeScript to Native Widgets)  
Perry

If you are open to moving away from HTML rendering entirely to avoid both webview overhead and Rust compile times, **Perry** is a newer framework gaining attention in the cross-platform space.  
Perry

**How it works:** It compiles TypeScript directly into native machine code via LLVM and drives real platform widgets (AppKit, UIKit, GTK4, Win32) using a declarative SwiftUI-style API.

**The Boot/Build Advantage:** While it does compile, it skips the massive dependency tree of the Rust/Cargo ecosystem and drops the entire webview layer, resulting in incredibly rapid execution and sub-megabyte binaries.

Summary Comparison
Framework	Backend Stack	UI Layer	First-Run Setup Speed
**Tauri**	Rust (Cargo)	System WebView	**Slow** (Heavy Rust compilation)
**Electrobun**	TS / Bun	System WebView	**Near Instant** (Interpreted/JIT)
**Neutralinojs**	JS / C++ Core	System WebView	**Instant** (No backend compilation)
**Perry**	TS (AOT Native)	Native Widgets	**Fast** (Direct LLVM compilation)

If the initial `cargo` compilation bottleneck is what drives you crazy about Tauri, looking into a Bun-backed runtime like **Electrobun** or sticking to a thin wrapper like **Neutralino** gives you that rapid web-developer feedback loop right from the first launch.

<!-- /gemini-message -->

---

<!-- gemini-message index=5 role=user timestamp="2026-07-07 20:07" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.241951)

[2026-07-07 20:04 MDT-6] electrobun sounds like it's the newest option? Is it like super alpha stages or is it decently stable?

And does it offer less features or like OS integration than Tauri?

<!-- /gemini-message -->

---

<!-- gemini-message index=6 role=assistant timestamp="2026-07-07 20:07" -->

---
## MODEL (2026-08-13T18:54:09.241952)

Electrobun is very much in its early stages, and its features are currently quite limited compared to Tauri.  
InfoWorld

Stability Status: Deep Alpha / Highly Experimental

While Electrobun recently hit a milestone called "v1", it is still in its **early alpha/experimental stages**.  
YouTube

**The Looming Architecture Shift:** The project is undergoing massive structural evolution. Electrobun initially relied completely on Bun for its main backend process. However, the framework is moving toward a core rewrite in Rust for its internal architecture (to decouple its strict dependency on Bun's runtime for native bindings).  
Better Stack

**Ecosystem Readiness:** The documentation frequently slips out of sync with the codebase, the community is small, and it hasn't faced serious production hardening yet. It is a fantastic project to watch or use for local developer utilities, but it isn't ready to anchor a stable, commercial production application.  
InfoWorld
+ 1

Feature & OS Integration Tradeoffs: Electrobun vs. Tauri

Electrobun offers **significantly fewer built-in features and lighter OS integration** than Tauri right now. Because Tauri has a massive head start and an entire ecosystem of official plugins, Electrobun is still playing catch-up on the native layer.  
Better Stack

Where Electrobun is Missing Ground

**Native API Surface:** Tauri provides out-of-the-box, fine-grained APIs for the filesystem, path resolution, shell execution, system notifications, global shortcuts, and system tray management. Electrobun has basic window management, custom context menus, and application menus, but its deeper OS integration hooks are still sparse.  
RaftLabs - Medium
+ 1

**Security Model:** Tauri uses a strict, granular "deny-by-default" capability isolation model where you explicitly whitelist what commands and APIs your frontend can invoke. Electrobun uses a more traditional, unrestricted RPC bridge between the webview and the Bun main process.  
RaftLabs - Medium

**Cross-Platform Nuance:** Tauri handles deep platform-specific edge cases gracefully across Windows, macOS, Linux, and mobile (iOS/Android). Electrobun's underlying native layer is stitched together with a mix of C++, Objective-C++, and Zig. While it runs on macOS and Windows, Linux support and complex window behaviors are less mature.  
Better Stack
+ 1

Where Electrobun Actually Competes (or Wins)

**Differential Updates:** Electrobun features an incredibly clever, built-in BSDIFF-based patch updater. Instead of downloading a brand-new 15MB binary for a small JS fix, it can generate and ship update patches as tiny as **14 KB**.  
Better Stack

**WebGPU / Direct Canvas:** It provides specialized abstractions (`<electrobun-wgpu>`) that allow you to pipe TypeScript code directly into native GPU surfaces using WGPU without a webview middleman—which is unique and powerful for high-performance canvas rendering.  
GitHub

The Bottom Line

If you are frustrated by Tauri's initial compile times, Electrobun proves that a fast-booting, pure-TypeScript alternative is architecturally possible. However, you would be trading Tauri's massive plugin ecosystem, stability, and cross-platform maturity for an experimental toolchain that is still finding its feet.  
RaftLabs - Medium

<!-- /gemini-message -->

---

<!-- gemini-message index=7 role=user timestamp="2026-07-07 20:07" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.241954)

[2026-07-07 20:05 MDT-6] what else is there? you mentioned Perry?

<!-- /gemini-message -->

---

<!-- gemini-message index=8 role=assistant timestamp="2026-07-07 20:07" -->

---
## MODEL (2026-08-13T18:54:09.241956)

Yes, **Perry** is a fascinating new player that takes an entirely unique approach.

While Electron, Tauri, and Electrobun all rely on a web browser engine to show you a UI, Perry tosses the browser out of the window completely.  
GitHub

How Perry Works (Under the Hood)

Perry is a **native TypeScript compiler** written in Rust. Instead of transpiling your TypeScript down to JavaScript so a browser or Node/Bun can read it, Perry uses SWC to parse your code and **LLVM/Cranelift to compile a subset of TypeScript directly into a native machine binary**.  
GitHub
+ 1

When it comes to the UI, it doesn't render HTML elements. It maps your UI code directly to **real, native platform widgets** (AppKit on macOS, Win32 on Windows, GTK4 on Linux, and UIKit on iOS). There's even a `perry-react` library in development that lets you use a JSX-like syntax that compiles directly into native layouts.  
GitHub
+ 1

How it Beats Tauri on Initial Setup & Boot

**No Massive Rust Dependency Tree for You:** Even though Perry itself is built in Rust, *you* aren't compiling Rust. You write pure TypeScript. The Perry compiler takes your `.ts` files and compiles them immediately.  
GitHub
+ 1

**Ultra-Light Binaries:** Because there's no Chromium layer (Electron) and no system webview bindings/window routing wrappers (Tauri), the output binaries are typically only **2 to 7 MB**.  
Perry

**Instant Cold Starts:** App launch takes less than a second because it’s just executing raw compiled machine code natively, pulling less than 100 MB of RAM.  
GitHub

What's the Catch?

Like Electrobun, Perry is incredibly young and has massive architectural constraints you need to look out for:

**It's a Subset of TypeScript:** Because it compiles to native code without a full browser engine by default, you can't just drop any arbitrary, highly dynamic JavaScript npm package into it. It has native, optimized implementations of Node APIs (like `fs`, `path`, and `crypto`), but complex, runtime-heavy JS code will fail unless you explicitly opt to embed their optional V8 runtime package (which balloons the binary size and defeats the "pure native" speed purpose).  
GitHub
+ 1

**No CSS Engine:** There is no HTML DOM and no CSS parser. If you use `perry-react`, styling is handled strictly via a small subset of inline `style={{}}` layout props that map directly to native widget setters. You can forget about Tailwind, CSS modules, or global classes.  
GitHub
+ 1

**Maturity:** It’s an ambitious engineering feat, but it's very much in the early adoption/showcase phase. The ecosystem of third-party libraries is basically nonexistent right now.  
GitHub

If you want to keep an eye on projects proving that TypeScript can exist as a compiled, ultra-fast native language without the weight of an entire browser engine or hours of initial Cargo compilation, Perry is exactly what you want to watch.

<!-- /gemini-message -->

---

<!-- gemini-message index=9 role=user timestamp="2026-07-07 20:07" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.241957)

[2026-07-07 20:06 MDT-6] ok, so what's a realistic competitor to Tauri?

<!-- /gemini-message -->

---

<!-- gemini-message index=10 role=assistant timestamp="2026-07-07 20:07" -->

---
## MODEL (2026-08-13T18:54:09.241958)

If you want a framework that is actually stable, production-tested, and shares Tauri's exact design philosophy but completely removes the painful Rust compilation times, the most realistic competitor is **Wails**.

The Direct Equivalent: Wails (Go + System Webview)

Wails is built on the exact same architecture as Tauri: it strips away the bundled Chromium browser and uses the operating system's native webview component to render your HTML/CSS/JS frontend.  
Digital Applied

The critical difference is the backend: **Wails uses Go instead of Rust**.  
Digital Applied

**The Boot/Compile Advantage:** Go is famous for its compilation speed. Unlike Rust, which spends immense amounts of time doing deep LLVM optimization and handling complex macro expansions during an initial `cargo build`, Go compiles almost instantly. Your very first run of a Wails project takes seconds, completely resolving the cold-start bottleneck you face with Tauri.

**Maturity:** It is highly stable and production-ready. Wails v2 has been stable for years, and Wails v3 is incredibly robust, introducing advanced features like native multi-window orchestration and rich system tray attachments.  
Digital Applied
+ 1

**Developer Experience:** Like Tauri, it automatically generates TypeScript types for your backend structs and methods, so calling backend code from your frontend feels seamless.  
Wails

**The Tradeoff:** Your binaries will be slightly larger than Tauri’s (think ~15MB instead of ~5MB) because the Go runtime is bundled into the executable, but it is still a fraction of Electron's size.  
Digital Applied

Other Realistic Options (Depending on your priorities)

If Go isn't your thing, the other mature paths each require a compromise on something else:

Framework	Architecture	The Compile/Boot Speed	The Tradeoff
**Electron**	Node.js + Bundled Chromium	**Instant** (No backend compilation)	Bloated binaries (100MB+) and heavy idle RAM usage.
**Neutralinojs**	C++ Web Server Wrapper	**Instant** (You only edit JS/TS)	Great for small utilities, but lacks the polished native plugin ecosystem and robust auto-updater pipelines of Tauri or Wails.
**Flutter (Desktop)**	Dart + Custom Canvas Renderer	**Fast** (Incremental compilation)	You have to write the UI in Dart instead of the web stack (React/Vite/Svelte), and it doesn't use webviews.
Summary

If you love the webview model of Tauri but absolutely dread staring at `cargo` compile logs on a clean build, **Wails** is the most mature, drop-in alternative available. It gives you the same lightweight distribution benefits, but the Go compiler keeps your momentum alive from the very first run.

<!-- /gemini-message -->

---

<!-- gemini-message index=11 role=user timestamp="2026-07-07 20:07" -->

---
## USER_EXPLICIT (2026-08-13T18:54:09.241960)

[2026-07-07 20:07 MDT-6] Wails sounds pretty great!

I mean, what makes Tauri better than Wails?

<!-- /gemini-message -->

---

<!-- gemini-message index=12 role=assistant timestamp="2026-07-07 20:07" -->

---
## MODEL (2026-08-13T18:54:09.241961)

Wails is an incredibly compelling option because it avoids that painful Rust compilation barrier completely. If you are looking for a rapid feedback loop and straightforward backend development, Go delivers exactly that.  
DEV Community

However, Tauri remains a highly polished framework because it makes several fundamental architectural choices that provide a distinct edge for complex or highly distributed applications:  
daily.dev

1. The Mobile Frontier (Tauri v2)

The absolute biggest separator is platform reach.

**Tauri v2** brings mobile support out of beta. You can use the exact same Rust backend logic and web frontend to target **iOS and Android** alongside macOS, Windows, and Linux.  
Rust Bootcamp

**Wails** is structurally constrained to desktop execution (Windows, macOS, Linux). If you ever want to transition your app to a mobile app store, Wails requires a complete rewrite of your native layer.

2. Deep Security and Isolation

Tauri was engineered from day one with a strict security-first mindset.

**Tauri's Capability System:** It uses a rigorous, granular allowlist system. You explicitly define exactly which native commands or filesystem paths your frontend is permitted to access. If an NPM dependency gets compromised, it cannot arbitrarily read files or execute shell commands unless you explicitly whitelisted that exact capability.  
PkgPulse

**Production Asset Serving:** Tauri uses custom protocol handlers (like `tauri://`) to securely load assets directly through native OS webview APIs. Wails historically relied on running a local HTTP web server bound to a local port in the background, which introduces potential surface area for local network attacks or port conflicts.

3. Maximum Resource Control and Zero Garbage Collection

While Go is remarkably fast and efficient compared to Node/Electron, it is still a garbage-collected language.

**Memory Posture:** The Go runtime features a background garbage collector (GC) that manages memory allocation on a cycle. This means a Wails app requires a slightly larger memory footprint baseline and carries a bundled runtime overhead.

**Raw Rust Performance:** Rust gives you complete deterministic control over memory allocation with zero GC pauses. If you are processing large data streams, reading huge directories, or dealing with thousands of concurrent operations, Rust's memory utilization profile scales flatly and predictably.

4. Binary Footprint Optimization

Because Go bundles its runtime, scheduler, and garbage collector directly into every compiled executable, the starting size for a bare-bones Wails application is typically around **12 to 15 MB**. Rust's compilation model allows Tauri to trim away everything down to the absolute bare metal, producing initial distribution binaries as small as **2 to 5 MB**.

Summary Tradeoff

Choosing between them comes down to a clear structural question:

Choose **Wails** if you are building an exclusively desktop application, want to maximize your development velocity, and hate long compile pauses.  
DEV Community

Choose **Tauri** if you need cross-platform mobile parity, require strict sandboxed security, or need to eke out absolute maximum memory performance from host machines.  
PkgPulse

<!-- /gemini-message -->

---
