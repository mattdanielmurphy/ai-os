---
title: "Configure SSH Multiplexing Settings"
date: "2026-08-05"
conversation_id: "b1253652-48b2-4c6e-a091-2208c16eb702"
source: "antigravity"
---

# Configure SSH Multiplexing Settings

## User

Add `Host *` configuration with `ControlPath /tmp/ssh-%r@%h:%p.sock` and `ControlMaster auto` / `ControlPersist 10m` to `~/.ssh/config`. Ensure existing hosts remain intact.

Target file: /Users/matt/.ssh/config

Existing content:
Host oracle-minecraft-server
  HostName 40.233.124.200
  User ubuntu
  IdentityFile ~/.ssh/Oracle-Minecraft-Server-SSH.key

Write updated content using write_to_file or replace_file_content. Ensure permissions/format remain valid.

---

## Assistant

Created At: 2026-08-05T16:02:56-06:00
Completed At: 2026-08-05T16:02:56-06:00
Created file file:///Users/matt/.ssh/config with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

---
