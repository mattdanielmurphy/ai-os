---
title: "I'm trying to install an extension to Hermes web ui called AutoList, a"
date: "2026-08-10"
conversation_id: "5ecf4aebd34e"
source: "antigravity"
---

# I'm trying to install an extension to Hermes web ui called AutoList, a

## User

I'm trying to install an extension to Hermes web ui called AutoList, and I'm getting error:
Install failed: Unsafe archive member

---

## Assistant

[Proxy Error]: HTTP Error 400: Bad Request

---

## User

I'm trying to install an extension to Hermes web ui called AutoList, and I'm getting error:
Install failed: Unsafe archive member

---

## Assistant

I'll start by searching the Hermes source code and system files for where extension archive extraction happens and what is triggering the "Unsafe archive member" error.

I located where the "Unsafe archive member" check is implemented in the Hermes agent package (`hermes_cli/profiles.py`). Now I will read those lines to see the safety validation logic.

I confirmed the path validation check in `_normalize_profile_archive_parts`. Now searching where plugin or extension installation functions are located in `hermes-agent`.

I'll search for where the "Install failed" error message is produced or where extensions/plugins/archives are handled in the webui and gateway services.

I will now examine the endpoint in `web_server.py` where plugin/profile installation happens that raises `Install failed: {exc}`.

I'm now searching `web_server.py` for extension/plugin or archive import/upload endpoints that call `_normalize_profile_archive_parts` or `_safe_extract_profile_archive`.

I'll search `web_server.py` for endpoints related to plugins, profiles, or extensions.

I'll check around line 13048 in `web_server.py` to see what archive functionality exists there.

I will read lines 13000-13030 of `web_server.py` to see which endpoint receives this file upload.

I'll check lines 12980-13000 of `web_server.py`.

I will now inspect `hermes_cli/profiles.py` to see where `import_profile` or archive reading validates files during `hermes import`.

I will read `hermes_cli/profiles.py` from line 1946 to 2075 to analyze how `_normalize_profile_archive_parts`, `_safe_extract_profile_archive`, and `import_profile` work.

[Proxy Error]: HTTP Error 500: Internal Server Error

---

## User

I'm trying to install an extension to Hermes web ui called AutoList, and I'm getting error:
Install failed: Unsafe archive member

---

## Assistant

I will search for any files or archives related to "AutoList" on your system to see how it was packaged and what archive member might be triggering the safety error.

I will search for any archives or folders with "autolist" in their name across Downloads, Desktop, and temp/staging directories.

I'll look for recent `.zip`, `.tar.gz`, or `.tgz` files in Downloads or `.hermes` staging areas.

I will search the web UI frontend code in `web/src` to see where zip archive uploads or plugin/extension/profile/skill installs occur.

I'll check `ProfilesPage.tsx` and `PluginsPage.tsx` in `web/src/pages/` to see where archives are uploaded and processed.

I'll check `ProfilesPage.tsx` for archive/profile import controls.

I'll check `api.ts` for file import methods.

I will search the whole `hermes-agent` repository for all zip/tar archive extraction routines to ensure we catch all locations where archive safety checks are applied.

I will read `hermes_cli/main.py` around line 6391 to see what zip extraction happens there.

The error **`Install failed: Unsafe archive member`** occurs because Hermes Agent enforces strict security checks on imported archives (`.zip` or `.tar.gz`) to prevent path traversal / Zip-Slip vulnerabilities.

An archive member is flagged as **unsafe** and rejected if it contains:
* **Absolute paths** (e.g. `/Users/...` or `C:\...`).
* **Parent directory references** (`..` or `../`).
* **Leading slashes or backslashes** (e.g. `/AutoList/...`).
* System artifacts like `__MACOSX` metadata or absolute symlinks created during zipping.

---

### How to Fix & Install AutoList

#### Option 1: Clean and Repack the Archive (Recommended for UI Install)

If you have `AutoList.zip` on your machine, re-pack it cleanly using relative paths:

```bash
# 1. Unzip to a temporary folder
unzip /path/to/AutoList.zip -d ./autolist_tmp

# 2. Re-zip from inside the folder (stripping absolute paths and macOS metadata)
cd ./autolist_tmp
zip -r ../AutoList_clean.zip . -x "*.DS_Store" "*__MACOSX*"
cd .. && rm -rf ./autolist_tmp
```

Then upload **`AutoList_clean.zip`** in the Web UI.

---

#### Option 2: Manual Direct Install

Depending on what type of extension AutoList is, you can extract it directly into your Hermes directory:

* **If AutoList is a Hermes Plugin** (contains `plugin.yaml`):
  ```bash
  mkdir -p ~/.hermes/plugins/AutoList
  unzip /path/to/AutoList.zip -d ~/.hermes/plugins/AutoList
  ```

* **If AutoList is a Skill** (contains `SKILL.md`):
  ```bash
  mkdir -p ~/.hermes/skills/AutoList
  unzip /path/to/AutoList.zip -d ~/.hermes/skills/AutoList
  ```

---

If you can tell me where `AutoList.zip` is located on your machine (or pass its path), I can inspect its contents, sanitize the archive, or install it directly for you.

---

## User

[Workspace::v1: /Users/matt/projects/userscript-bundler]
Well I'm trying to install from web's built in page

[Attached files: /Users/matt/.hermes/webui/attachments/5ecf4aebd34e/screenshot-1786320238229.png]
[screenshot]

---

## Assistant

I'll check the screenshot image attached to see what page in the Web UI you were using to install AutoList.

I'll analyze the screenshot directly using native python or tools to see what UI page was open.

I will find where python with PIL / Pillow or vision tools are installed.

---

## User

continue

---

## Assistant

[Proxy Error]: HTTP Error 400: Bad Request

---

## User

continue

---

## Assistant

[Proxy Error]: HTTP Error 400: Bad Request

---

## User

continue

---

## Assistant

I will now inspect the screenshot using Python to extract any text or identify which page and button were used.

I will resize the screenshot so it can be analyzed cleanly by the vision model.

I will now process the resized screenshot using vision tools to read the UI page details.

I will run an OCR script using macOS's built-in Vision framework to extract text from the screenshot.

I will search `web_server.py` and `web/src` for the extension installation API endpoint that handles gallery extension installs.

[Proxy Error]: timed out

---
