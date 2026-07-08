[2026-07-07 23:38] User:
with agy you can do ctrl-g to open the prompt in an external editor. I have it set to open in agy-ide. It opens, I save the file, I close the file, I return to the agy-cli terminal, and nothing's happened. it's just a blank prompt.

---

[2026-07-07 23:38] Assistant:
The issue you are experiencing is a classic behavior with terminal applications spawning external GUI editors.

When you press `Ctrl+G`, `agy-cli` creates a temporary text file, fires up a background process to open your configured editor, and **waits for that specific process to terminate** before reading the text back into your terminal prompt.

Because `agy-ide` is a full GUI application, launching it from the CLI usually just passes the file path to an already running background instance of the IDE and immediately exits the terminal command. Since the spawned process exits instantly, `agy-cli` assumes you closed the file right away without typing anything—leaving you with a blank prompt.

To fix this, you have two main options:

Option 1: Add a "Wait" flag to your editor configuration

If `agy-ide` supports a command-line interface flag that forces the terminal to block and wait until the specific file tab is closed (similar to `code --wait` for VS Code), you need to include that flag in your configuration.

Check your `agy-cli` settings by running:

Bash

```
/settings

```


(Or by opening `~/.gemini/antigravity-cli/settings.json` directly). Look for the external editor execution string and ensure it looks something like this:

JSON

```
"external_editor": "agy-ide --wait"

```


*(Note: Replace `--wait` with the specific blocking flag native to the `agy-ide` CLI utility if it uses a different syntax).*

Option 2: Use a terminal-based editor for prompts (Recommended)

An entire IDE can be heavy just for tweaking a quick CLI prompt. Most developers prefer mapping `Ctrl+G` to a lightweight, terminal-native editor like `nano` or `vim`, which inherently blocks the terminal until closed.

You can set this globally in your shell profile (e.g., `~/.zshrc` or `~/.bashrc`):

Bash

```
export EDITOR="nano"

```


Or explicitly bind it inside your `agy-cli` configuration so it doesn't conflict with your global system settings.

---

[2026-07-07 23:39] User:
sick it worked w/ --wait.

seems to be as soon as I close the file, then it shows up in the prompt box, but then I still have to hit enter to send it

---

[2026-07-07 23:39] Assistant:
That is actually the intentional design. Passing it back to the prompt box gives you a final chance to review it, add any quick terminal-specific flags, or cancel out before sending it off into the void.

If you want it to automatically execute the moment you close your editor, you can check if `agy-cli` has a specific configuration option for it.

Open your configuration file (`~/.gemini/antigravity-cli/settings.json`) and look for a boolean key related to immediate execution. Depending on your version, it usually looks like this:

JSON

```
"auto_submit_external_editor": true

```


If that key doesn't exist, the CLI doesn't currently support auto-submission out of the box, meaning hitting `Enter` remains a manual safety buffer.
