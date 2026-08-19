---
title: "Warp CLI Auto-Completion Setup"
date: "2026-08-07"
conversation_id: "dbc5d095c859689a"
source: "antigravity"
---

# Warp CLI Auto-Completion Setup

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-06 19:54 MDT-6] [context to this point is 0] How do I get robust, um, CLI tool auto completion for like every CLI tool that I have installed? I use a Warp terminal and I'm on a Mac.

---

## Assistant

Warp handles auto-completion differently than standard terminal emulators because it uses its own IDE-style input editor rather than a traditional shell line editor.

To get robust completions for practically everything you have installed, you'll want to combine Warp's native engine with a blanket `zsh` completion fallback. Here is how to set it up.

1. Tweak Warp's Native Engine

Out of the box, Warp ships with built-in, natively maintained completion specs for over 400 popular CLI tools.  
Warp

To make this feel more seamless:

Open Warp and press `Cmd + ,` to open **Settings**.

Go to **Features** > **Terminal Input**.

Toggle on **Open completions menu as you type**. This saves you from having to repeatedly hit the `TAB` key to see available flags.  
Warp docs

Customize the **Tab key behavior** to your preference (e.g., accepting the current autosuggestion vs. cycling through the menu options).  
Warp docs

2. Catch the Rest with `zsh-completions`

For tools that Warp doesn't support natively, it parses and falls back to whatever is loaded into your underlying shell (which is `zsh` by default on macOS). You can grab community-maintained completions for thousands of niche tools via Homebrew.

Run this command:

Bash

```
brew install zsh-completions

```


Then, open your `~/.zshrc` file and add this block *before* any `compinit` calls (if you already have them):

Bash

```
if type brew &>/dev/null; then
  FPATH=$(brew --prefix)/share/zsh-completions:$FPATH
  autoload -Uz compinit
  compinit
fi

```


Restart Warp (or run `source ~/.zshrc`). Warp will now intercept these standard `zsh` completions and render them in its native popup menu.

3. Tool-Specific Generated Completions

Many modern CLIs generate their own completion scripts on the fly. Because Warp acts as a wrapper over standard `zsh` completions, you just need to follow the standard `zsh` instructions for those specific tools to get them showing up in Warp's UI.

For example, you can add completion generation for specific tools directly at the bottom of your `~/.zshrc`:

Bash

```
# Example for Bun
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

# Example for Kubernetes
source <(kubectl completion zsh)

```


Once a tool registers its standard completion with the shell, Warp handles the visual rendering automatically.

---

## User

[2026-08-06 20:03 MDT-6] [context to this point is 881] fuck I totally forgot I actually need this for my linux VPS

---

## Assistant

If you are SSHing into that Linux VPS *using Warp* on your Mac, you actually might not need to configure anything on the server. Warp has a built-in SSH wrapper that injects its own shell environment into the remote machine.

As long as Warp's SSH wrapper is enabled (it usually is by default, but you can check via **Settings > Features > Network > Enable Warp SSH Wrapper**), you will get the exact same native IDE-style autocomplete and block features on the VPS as you do locally.

If you are using a different terminal to connect, or if you just want the native shell on the VPS to be fully equipped regardless of the client, here is how to set up robust completions natively on Linux.

1. The Standard Foundation

Depending on which shell your VPS defaults to (usually `bash`, sometimes `zsh`), you need the base completion packages. Assuming a Debian/Ubuntu-based VPS:

**For Bash:**

Bash

```
sudo apt update
sudo apt install bash-completion

```


Then ensure this is in your `~/.bashrc`:

Bash

```
if [ -f /etc/bash_completion ]; then
  . /etc/bash_completion
fi

```


**For Zsh:**

Bash

```
sudo apt update
sudo apt install zsh-autosuggestions zsh-completions zsh-syntax-highlighting

```


Then add this to your `~/.zshrc`:

Bash

```
autoload -Uz compinit
compinit
source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

```

2. The Heavy Hitter: Carapace

If you want something closer to the "Warp experience" natively inside a standard Linux shell, install **Carapace**. It is a multi-shell argument completer that provides robust, context-aware completions for over 1,000 CLI tools.

Install it on the VPS:

Bash

```
curl -sL https://carapace.sh/install.sh | bash

```


Then hook it into your shell.
For `bash` (add to `~/.bashrc`):

Bash

```
export CARAPACE_BRIDGES='zsh,fish,bash,inshellisense'
source <(carapace _carapace)

```


For `zsh` (add to `~/.zshrc`):

Bash

```
export CARAPACE_BRIDGES='zsh,fish,bash,inshellisense'
zstyle ':completion:*' format $'\e[2;37mCompleting %d\e[m'
source <(carapace _carapace)

```

3. Tool-Specific Generators

Just like on macOS, many modern tools handle their own completion generation. If you are running tools like Bun or Docker on the VPS, you still need to append their specific completion generation commands to your shell config file so your base shell (or Carapace) knows they exist.

For example, at the bottom of your `~/.bashrc` or `~/.zshrc`:

Bash

```
# Bun
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

# Docker
source <(docker completion $(basename $SHELL))

```

---

## User

[2026-08-06 20:10 MDT-6] [context to this point is 1715] I just realized... Warp is definitely a step in the right direction for enhancing the terminal experience, but there's no reason why I shouldn't be able to get like full on GUI popups to understand quickly what a command does, the essential commands, etc.

Does that exist by any chance?

---

## Assistant

Sorry, something went wrong. Please try your request again.

---
