---
name: apple-reminders
description: "Apple Reminders via apple-reminders CLI: create timed and geofenced location reminders for Matt's personal to-dos."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Reminders, tasks, todo, macOS, Apple, geofence, location, personal-todos]
prerequisites:
  commands: [apple-reminders]
---

# Apple Reminders (`apple-reminders`)

Use `apple-reminders` CLI (`~/.local/bin/apple-reminders`) for **ALL** personal reminders, to-dos, timed alerts, and location-based geofences requested by Matt.

## Trigger Phrases

Whenever Matt says:
- "make a reminder...", "set a reminder...", "remind me..."
- "add a to-do...", "add to my reminders...", "personal to-do..."
- "geofence reminder for...", "when I get to [location]..."

👉 **Route EXCLUSIVELY to Apple Reminders** via `apple-reminders`. Do NOT use cron jobs or project task trackers for Matt's personal to-dos unless explicitly directed otherwise.

## Quick Reference

### 1. Timed Reminders

```bash
apple-reminders add --title "Transfer money" --due "2026-07-27 12:00" --notes "Details..."
```

### 2. Geofenced Location Reminders

```bash
apple-reminders add --title "Present Mounjaro savings card" \
  --location-name "Costco Wholesale Sherwood Park" \
  --lat 53.5466885 --lon -113.3173788 \
  --radius 150 --proximity enter \
  --notes "Card is in Apple Wallet"
```

### 3. List / Complete / Delete

```bash
apple-reminders list
apple-reminders complete --title "<query>"
apple-reminders delete --title "<query>"
```

## How Geofencing Sync Works

- When a geofenced reminder is added via `apple-reminders` on Mac, EventKit saves the structured location (`EKStructuredLocation`) to iCloud.
- iCloud syncs the geofence parameters directly to Matt's iPhone/Apple Watch.
- iOS handles location tracking in the background and fires a native alert when entering the geofence barrier.
