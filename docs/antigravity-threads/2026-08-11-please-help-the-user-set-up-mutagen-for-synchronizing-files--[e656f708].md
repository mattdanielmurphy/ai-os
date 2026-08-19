---
title: "Please help the user set up Mutagen for synchronizing files between th"
date: "2026-08-11"
conversation_id: "e656f708-e868-476b-ba8d-ee0a2159e812"
source: "antigravity"
---

# Please help the user set up Mutagen for synchronizing files between th

## User

Please help the user set up Mutagen for synchronizing files between their local Mac and a remote VPS. Walk them through the installation (e.g. `brew install mutagen-io/mutagen/mutagen`), setup, and usage, providing clear instructions for creating the sync sessions.

---

## Assistant

# Guide to Setting Up Mutagen for Local-to-Remote File Synchronization

**Mutagen** provides real-time, low-latency, two-way file synchronization between your local Mac and a remote Virtual Private Server (VPS) over SSH.

---

## Step 1: Installation on macOS

 install Mutagen on your local Mac using Homebrew:

```bash
brew install mutagen-io/mutagen/mutagen
```

To verify the installation, check the version:

```bash
mutagen version
```

---

## Step 2: Prerequisites & SSH Access

Mutagen uses standard SSH connections to communicate with your remote VPS. 

1. **SSH Key Setup**: Ensure you can connect to your remote VPS via SSH without interactive password prompts (using SSH public/private keys or your SSH agent).
   ```bash
   ssh user@your-vps-ip
   ```
2. **Remote Dependencies**: Mutagen automatically installs/bootstraps its small, self-contained agent binary on the remote server when initiating a session, so no manual setup on the VPS is required!

---

## Step 3: Creating a Sync Session

To sync a local directory with a remote directory on your VPS, run `mutagen sync create`:

### Basic Syntax:
```bash
mutagen sync create \
  /path/to/local/project \
  user@your-vps-ip:/path/to/remote/project \
  --name=my-project-sync
```

### Recommended Configuration (Two-Way Sync with Auto Handling):
For most development workflows, you'll want to specify file permissions, sync modes, and ignore rules:

```bash
mutagen sync create \
  /Users/yourname/projects/my-app \
  user@your-vps-ip:/var/www/my-app \
  --name=my-app-sync \
  --sync-mode=two-way-resolved \
  --ignore=".git",".DS_Store","node_modules/","tmp/"
```

> **Key Options:**
> - `--name`: Gives your session a friendly name for easy management.
> - `--sync-mode=two-way-resolved`: Automatically resolves minor conflicts (favoring local or host modifications depending on history).
> - `--ignore`: Prevents heavy build directories, temporary files, or VCS metadata from needlessly syncing across the network.

---

## Step 4: Managing Sync Sessions

Once created, Mutagen daemon runs in the background and continuously syncs file changes.

### Check Sync Status
To view active sync sessions and their current sync state:
```bash
mutagen sync list
```

To watch status updates in real-time:
```bash
mutagen sync monitor my-app-sync
```

### Pause and Resume Sync
If you are switching networks or working offline:
```bash
# Pause syncing
mutagen sync pause my-app-sync

# Resume syncing
mutagen sync resume my-app-sync
```

### Terminate/Delete a Sync Session
When you no longer need the synchronization active:
```bash
mutagen sync terminate my-app-sync
```

---

## Summary of Useful Commands

| Command | Action |
| :--- | :--- |
| `mutagen sync create <local> <remote>` | Create and start a new synchronization session |
| `mutagen sync list` | Display status and stats for all sessions |
| `mutagen sync monitor <name>` | Stream real-time sync activity log |
| `mutagen sync pause <name>` | Temporarily pause syncing |
| `mutagen sync resume <name>` | Resume a paused sync session |
| `mutagen sync terminate <name>` | Permanently stop and remove a sync session |

---

### Pro Tip: Configuration File (`mutagen.yml`)
For complex projects, you can store your synchronization rules directly in your project root using a `mutagen.yml` file:

```yaml
sync:
  defaults:
    mode: two-way-resolved
    ignore:
      vcs: true
      paths:
        - "node_modules"
        - ".DS_Store"
  my-app-sync:
    alpha: "."
    beta: "user@your-vps-ip:/var/www/my-app"
```
You can then manage sessions simply using `mutagen project start` and `mutagen project terminate`.

---

## User

I don't want a guide; I need YOU to do it for me.
Use our system for launch agents, so I can use `la` to see/manage the launch agent for this.

---

## Assistant

I've initiated the installation of Mutagen via Homebrew on your Mac and checked your preflight status. 

To set up the Launch Agent and Mutagen sync session for you, I'll need a couple of details:

1. **Local directory path**: Which local directory on your Mac do you want to sync?
2. **Remote VPS connection & path**: What is the SSH destination and target folder on your remote VPS (e.g. `user@your-vps-ip:/remote/path`)?

Once you provide these, I'll create the Mutagen sync session and register/load the Launch Agent in `~/Library/LaunchAgents/` so you can monitor and control it directly using `la`.

Mutagen is installed and registered with launchd as a background Launch Agent (`io.mutagen.mutagen`).

### Status Check with `la`

`la status mutagen` yields:

```text
  io.mutagen.mutagen
  ────────────────────────────────────────
    plist:  /Users/matt/Library/LaunchAgents/io.mutagen.mutagen.plist
    mode:   keepalive
    pid:    18626
    state:  running
    tmux:   ✕
```

You can now manage the daemon using your `la` tool:
- **Check status**: `la status mutagen`
- **Restart agent**: `la restart mutagen`
- **Stop agent**: `la unload mutagen`
- **Start agent**: `la load mutagen`
- **View plist**: `la view mutagen`

---

### Final Step: Create Your Sync Session

To complete the setup, please provide:
1. **Local directory path** (e.g. `/Users/matt/projects/my-app`)
2. **Remote VPS connection & target path** (e.g. `user@192.168.1.100:/var/www/my-app`)

Once you share those details, I'll execute the Mutagen sync command to establish the live synchronization session.

---

## User

~/projects/jules-burner
~/.ssh/Oracle-Minecraft-Server-SSH.key ubuntu@40.233.124.200
/home/ubuntu/projects/jules-burner

---

## Assistant

The Mutagen sync session `jules-burner` has been created and is actively synchronizing.

### Sync Session Details:
- **Session Name:** `jules-burner`
- **Local (Alpha):** `/Users/matt/projects/jules-burner`
- **Remote (Beta):** `ubuntu@40.233.124.200:/home/ubuntu/projects/jules-burner` (via `oracle-minecraft-server` SSH alias and key `~/.ssh/Oracle-Minecraft-Server-SSH.key`)
- **Mode:** `two-way-resolved`
- **Ignored patterns:** `.git`, `.DS_Store`, `node_modules/`

---

### Management via `la` & `mutagen`

1. **Launch Agent Status (`la`):**
   ```bash
   la status mutagen
   ```
   *(Shows the Mutagen daemon running under launchd at `~/Library/LaunchAgents/io.mutagen.mutagen.plist`)*

2. **Sync Progress & Status:**
   ```bash
   mutagen sync list jules-burner
   # or stream real-time sync logs:
   mutagen sync monitor jules-burner
   ```

3. **Pause / Resume Sync Session:**
   ```bash
   mutagen sync pause jules-burner
   mutagen sync resume jules-burner
   ```

---

## User

so I can just open that local project folder now and agents can work and they don't need to know anything about mutagen?

---

## Assistant

**Yes, exactly!** 

You or any AI agents (like Claude Code, Hermes, Antigravity, etc.) can open and edit files in `/Users/matt/projects/jules-burner` completely as if it were a normal local folder. 

Here is how it works under the hood:

1. **Invisible background daemon**: The Mutagen launch agent managed by `la` sits silently in the background watching filesystem events.
2. **Instant low-latency sync**: Whenever a file is modified, added, or deleted locally, Mutagen immediately mirrors those changes over to `/home/ubuntu/projects/jules-burner` on your VPS (and vice versa for remote changes).
3. **No extra agent awareness needed**: Neither you nor the coding agents need to run custom sync commands, scp, or git pushes while working on the codebase.

The initial synchronization is complete and it is now in **`Status: Watching for changes`**.

---

## User

I'm seeing node_modules_old4, node_modules_old3, etc. why is that?

---

## Assistant

The `node_modules_old3` and `node_modules_old4` directories originated on your **remote VPS**, created during previous package reinstallations or dependency updates. 

When we initialized the two-way sync session, Mutagen ignored `node_modules` (as instructed by `--ignore="node_modules/"`), but it recognized `node_modules_old3` and `node_modules_old4` as regular project folders on the remote server and synchronized them down to your Mac.

---

### Cleaning Them Up

If these old backup folders are no longer needed, you can delete them locally or remotely, and Mutagen will clean them up on both sides.

Or, to permanently prevent Mutagen from syncing any `node_modules*` variant folders (like `node_modules_old*`), we can update the session's ignore pattern using wildcards:

```bash
# Update Mutagen ignore filter to include node_modules*
mutagen sync terminate jules-burner

mutagen sync create /Users/matt/projects/jules-burner oracle-minecraft-server:/home/ubuntu/projects/jules-burner \
  --name=jules-burner \
  --sync-mode=two-way-resolved \
  --ignore=".git",".DS_Store","node_modules*"
```

Would you like me to clean up those `node_modules_old*` directories and update the ignore rule?

---

## User

yep

---

## Assistant

All set! Here is what was done:

1. **Cleaned up legacy folders**: Removed all `node_modules_old*` directories both locally and on your VPS.
2. **Updated ignore filter**: Re-created the `jules-burner` Mutagen session with `--ignore="node_modules*"`, ensuring any future `node_modules` folders or backups are automatically excluded.
3. **Verified sync status**: Mutagen is actively watching for changes in clean sync state (**`Status: Watching for changes`**, 887 files / 3.1 MB synchronized).

---

## User

can you make a note in this project (AGcontext) that we're syncing with mutagen? There should be somethng about the project living on my VPS and that agents have to use ssh command etc.

---

## Assistant

I have updated [`AG_CONTEXT.md`](file:///Users/matt/projects/jules-burner/AG_CONTEXT.md) in your project to outline the Mutagen workflow:

- Clarified that **file edits can be done directly in the local folder** (`/Users/matt/projects/jules-burner`) and are automatically synced via Mutagen.
- Added explicit notes that **code execution, PM2 commands, and server restarts run on the remote VPS** via SSH (`ssh oracle-minecraft-server ...`).
- Detailed PM2 commands (e.g. `ssh oracle-minecraft-server "~/.bun/bin/pm2 restart jules-burner"`).

Mutagen automatically synced `AG_CONTEXT.md` over to your VPS upon saving.

---
