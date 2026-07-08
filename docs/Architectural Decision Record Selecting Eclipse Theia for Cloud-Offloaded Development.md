# Architectural Decision Record: Selecting Eclipse Theia for Cloud-Offloaded Development

## 1. Core Requirements & Constraints
- **Open Source Framework:** Strict requirement for a completely transparent, vendor-neutral development engine with zero proprietary telemetry or paywalled features.
- **100% Keyboard & Text Parity:** Must support multi-cursor editing, complex regex transformation pipelines, line cloning, and standard VS Code keyboard shortcuts flawlessly.
- **Rich Extension UI (Webviews):** Must be capable of rendering complex graphical extensions, specifically interactive project-management Kanban boards.
- **Decoupled Client/Server Execution:** Ability to split the UI footprint away from the file-watching, extension indexing, and heavy CPU compilation cycles, routing them to a remote VPS.

---

## 2. The Evaluation & Runners-Up
While exploring lightweight, high-performance editors, alternative options hit major architectural roadblocks regarding these specific requirements:

- **Lapce / Zed:** Blisteringly fast native performance (Rust/GPU-accelerated), but their native compilation targets do not run a Chromium rendering thread. Because they lack an embedded browser layer, they fundamentally **cannot render webviews**, making standard visual Kanban extensions impossible to run or build.
- **Cursor / Proprietary Tools:** Provide excellent agentic multi-file workflows, but gate advanced developer capabilities behind closed-source binaries and a recurring monthly SaaS subscription fence.
- **VSCodium / Melty:** Excellent choices for local development with complete open-source `Code - OSS` parity. However, they are fundamentally designed as unified desktop packages; they do not natively separate the core UI from the heavy node extension host cleanly enough to completely offload processing over an optimized network socket.

---

## 3. Why We Arrived at Eclipse Theia
Eclipse Theia provides the exact structural solution by utilizing a **Decoupled RPC (Remote Procedure Call) Architecture over WebSockets**:

- **Text Rendering Engine:** Uses standard Monaco (the text layer powering VS Code), preserving perfect text-gymnastics and layout shortcuts.
- **Webview Support:** Built entirely on modern web technologies, providing native compliance with the Open VSX extension ecosystem and complete sandboxed webview layout compatibility for Kanban structures.
- **Hardware Offloading:** The frontend (the UI shell you interact with on your Mac) is completely isolated from the backend process (which handles file management, Language Server Protocols, terminals, and compilers). This allows you to offload the entire operational footprint to a VPS, leaving your local Mac perfectly cool and resource-light.

---

## 4. Broad-Strokes Architecture Setup (VPS Offload)

The goal is to serve a secure, high-performance instance of the Theia IDE out of a Docker environment on your VPS, enabling you to treat your VPS as the raw execution block while viewing it securely in a desktop browser container.

### Step 1: Configure a Secure Web Reverse Proxy (VPS)
Because typing input, terminal updates, and file tree operations stream continuously over WebSockets, your reverse proxy must handle protocol upgrades securely. Web browsers require an encrypted context (`HTTPS`) to allow clipboard operations (copy-pasting text) inside web applications.

- Set up **Nginx** or **Traefik** on your server.
- Generate a free TLS certificate via **Let's Encrypt**.
- Crucially, explicitly append connection upgrade headers within your proxy definition:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "Upgrade";

```

### Step 2: Deploy the Decoupled Theia Image via Docker Compose

By using the official `theia-blueprint/theia-ide` image, you fetch a production-ready, extension-compatible workspace. You map your host server's local development directory straight into the container's volume space.

```yaml
version: '3.8'

services:
  theia-ide:
    image: ghcr.io/eclipse-theia/theia-blueprint/theia-ide:latest
    container_name: theia_cloud_engine
    restart: unless-stopped
    volumes:
      # Map your remote development project directories into the container workspace
      - /home/user/development:/home/theia/workspace
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - THEIA_DEFAULT_WORKSPACE=/home/theia/workspace

```

### Step 3: Connect and Mount the 1:1 Local File Mirror (Mac Setup)

With your server engine serving the UI securely at `https://ide.yourvps.com`, you decide how your Mac interacts with the files for local agent access:

- **The Remote-First Path:** Do all active work straight inside the secure browser session. The VPS handles everything natively. Your files stay perfectly synced because they live on the server.
- **The Real-Time Delta Mirror (Mutagen Daemon):** If you want to run local CLI agents (like *Claude Code*) directly on your Mac's filesystem while working seamlessly with your VPS, configure a background file-sync daemon using **Mutagen** over SSH. Configure a `.mutagenignore` manifest to skip media assets, letting tiny code files instantly mirror bi-directionally between both machines over light text stream deltas.
