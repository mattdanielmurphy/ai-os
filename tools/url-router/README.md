# AI-OS Invisible HTTP URL Router (`AIOSURLRouter.app`)

An invisible macOS URL Router app that acts as a system HTTP/HTTPS router to intercept action clicks from Antigravity artifacts without opening Chrome or stealing window focus.

## Built Components

1. **`AIOSURLRouter.app`** (`tools/url-router/AIOSURLRouter.app`):
   - AppleScript application bundle configured with `LSUIElement = true` (headless background UI element).
   - Listens for `http://127.0.0.1:8643/*` and `http://localhost:8643/*`.
   - Intercepts trigger URLs silently using background `curl`.
   - Delegates all non-matching URLs directly to Google Chrome.

2. **Action Listener Service** (`services/url_action_listener/server.py`):
   - Lightweight Python HTTP listener running on `127.0.0.1:8643`.
   - Processes actions such as `open_zed` (spawns `zed <path>`), `set_delegation`, context switching, etc.

## Setup & Switching Default Browser

To set `AIOSURLRouter` as your system default browser:
1. Open **System Settings -> Desktop & Dock -> Default web browser**.
2. Select **AIOSURLRouter**.

*(To revert anytime, switch Default web browser back to **Google Chrome**).*
