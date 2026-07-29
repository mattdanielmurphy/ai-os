# macOS Environment Reference

## macOS Context & Automation
- Refer to [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md) before installing software or scripting automation.
- **TCC Permission Reset:** When rebuilding ad-hoc binaries on macOS, run `tccutil reset Accessibility <bundle-id>` and `tccutil reset ListenEvent <bundle-id>` if permission prompts fail.
- **Hammerspoon Reload:** After modifying files in `qwerty-midi-hammerspoon`, run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.
