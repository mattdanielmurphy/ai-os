# Architectural Decision Record: Selecting Antigravity IDE (With Theia Migration Path)

## 1. Core Requirements & Constraints

- **100% Keyboard & Text Parity:** Must support multi-cursor editing, complex regex transformation pipelines, line cloning, and standard VS Code keyboard shortcuts flawlessly.
- **Rich Extension UI (Webviews):** Must be capable of rendering complex graphical extensions, specifically interactive project-management Kanban boards.
- **AI-Assisted Workflows:** Native, low-friction integration with AI auto-suggestions and inline chat components.
- **Future Decoupled Execution (Optional):** Ability to eventually split the UI footprint away from the file-watching, extension indexing, and heavy CPU compilation cycles, routing them to a remote VPS if project scope demands it.

---

## 2. The Evaluation & Current Selection

While exploring lightweight or completely open-source editors, our immediate operational requirements shifted the selection toward standardizing on **Antigravity IDE (agy-ide)** for local development, with a clear fallback architecture established.

### The Selected Choice: Antigravity IDE (agy-ide)

Antigravity IDE is currently selected as the primary local driver due to high immediate utility and zero initial setup friction:

- **Flawless Editor Parity:** As a direct fork of VS Code, it keeps standard macOS line-navigation string shortcuts (like `Cmd + Right`) completely intact without manual remap profiles.
- **Built-in AI Efficiencies:** Out-of-the-box AI auto-suggestions and native sidebar chat remain highly available and run seamlessly without requiring manual model Orchestration or per-token API routing setups.

### The Runners-Up

- **Lapce / Zed:** Blisteringly fast native performance (Rust/GPU-accelerated), but their native compilation targets do not run a Chromium rendering thread. Because they lack an embedded browser layer, they fundamentally **cannot render webviews**, making standard visual Kanban extensions impossible to run or build.
- **VSCodium / Melty:** Excellent choices for local development with complete open-source `Code - OSS` parity. However, they lack the immediate out-of-the-box AI convenience features provided by the active Antigravity environment without separate extension configuration.
- **Eclipse Theia (Local Deployment):** Evaluated locally but paused due to minor structural friction. Running entirely on a local machine, its boot times, window reloads, and web-context keyboard capturing profiles (e.g., overriding basic text-selection combinations) felt a little rough around the edges compared to a native desktop container layout.

---

## 3. The Long-Term Transition Strategy: Why We Kept Theia

We are choosing to preserve **Eclipse Theia** as our dedicated target migration path for the future.

Because both Antigravity IDE and Eclipse Theia implement the **standardized VS Code Extension API**, any custom tooling we build today (such as a custom project-management Kanban workspace extension) will operate seamlessly across both applications without modifying a single line of backend logic.

If Google modifies its pricing structures or if a massive monorepo setup begins taxing our local machine's local hardware, we can execute a zero-downtime migration to a **VPS-Offloaded Theia Engine**. Theia’s unique decoupled architecture allows us to offload the entire operational footprint (file watchers, LSPs, compilers) onto a remote cloud server, leaving our local machine perfectly cool while streaming the editor frame over an optimized WebSocket connection.

---

## 4. Broad-Strokes Architecture Setup (Future VPS Offload)

When the time comes to execute the cloud offload via Theia, the environment will be stood up using a secure browser container layout on the remote server:

### Step 1: Configure a Secure Web Reverse Proxy (VPS)

Because typing input, terminal updates, and file tree operations stream continuously over WebSockets, the remote proxy must handle protocol upgrades securely. Web browsers require an encrypted context (`HTTPS`) to allow clipboard operations (copy-pasting text) inside web applications.

- Set up **Nginx** or **Traefik** on the server.
- Generate a free TLS certificate via **Let's Encrypt**.
- Explicitly append connection upgrade headers within the proxy definition:

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "Upgrade";

```

### Step 2: Deploy the Decoupled Theia Image via Docker Compose

By using the official `theia-blueprint/theia-ide` image, we fetch a production-ready, extension-compatible workspace, mapping the host server's local development directory straight into the container's volume space.

```yaml
version: "3.8"

services:
  theia-ide:
    image: ghcr.io/eclipse-theia/theia-blueprint/theia-ide:latest
    container_name: theia_cloud_engine
    restart: unless-stopped
    volumes:
      # Map remote development project directories into the container workspace
      - /home/user/development:/home/theia/workspace
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - THEIA_DEFAULT_WORKSPACE=/home/theia/workspace
```

### Step 3: Connect and Mount the 1:1 Local File Mirror (Mac Setup)

With the server engine serving the UI securely at `https://ide.yourvps.com`, the local filesystem is bridged for developer or local agent interaction:

- **The Remote-First Path:** Do all active work straight inside the secure browser session. The VPS handles everything natively. Files stay perfectly synced because they live directly on the server host.
- **The Real-Time Delta Mirror (Mutagen Daemon):** To run local CLI tools or external local scripts directly on the local machine's filesystem while working seamlessly with the VPS, configure a background file-sync daemon using **Mutagen** over SSH. A `.mutagenignore` manifest isolates heavy assets, letting tiny code files instantly mirror bi-directionally between both environments over light text stream deltas.
