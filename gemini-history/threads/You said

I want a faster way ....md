[2026-06-30 18:05] User:
I want a faster way to swap accounts in `agy`. It seems to require me opening a browser, signing in, copying the code, pasting it back in.

I assume that's the only way to log out of one account and into another?

To automate it I'd have to use puppeteer or something?

---

[2026-06-30 18:05] Assistant:
Your assumption is spot on regarding the current limitation: `agy` doesn't have a native `--profile` or `account switch` flag built into the CLI yet. Because it is a Go binary that relies directly on your operating system's native secure keyring (like Apple Keychain on macOS) to store its OAuth tokens, running `/logout` completely purges the active token, forcing you back into the browser-based OAuth loop.

You *could* build a Puppeteer script to handle the browser interaction, but there are much cleaner ways to bypass or automate this without simulating UI clicks.

Here are the most efficient ways to handle fast account swapping:

1. The Keychain Swapping Hack (No Browser Required)

Since `agy` pulls directly from the OS Keychain, you can bypass the browser entirely by backing up and swapping the tokens directly via the command line. On macOS, `agy` stores its tokens as a Base64-encoded JSON payload.

Instead of calling `/logout`, you can let your shell swap the specific keychain item.

You can write a lightweight bash/zsh function using the macOS native `security` utility.

When you authenticate with Account A, export that specific keychain entry to a local encrypted file or separate variable.

Do the same for Account B.

Create a toggle alias in your `.zshrc` that uses `security add-generic-password` to overwrite the `agy` token entry with the target account's token on the fly.

Next time you launch `agy`, it will silently read the injected token from the keychain without opening a window.

2. Leverage Community Tools (`Antigravity-Manager`)

The developer ecosystem has already run into this bottleneck. There is an open-source project called **Antigravity-Manager** specifically designed to fix this exact issue.

It acts as a single-dashboard account switcher that handles:

**Silent Keychain Injection:** It manages multiple OAuth tokens and uses native macOS `security` CLI scripts to silently swap them in your Keychain behind the scenes.

**Path Isolation:** It separates runtime databases (`state.vscdb`) and configurations to prevent session invalidation or machine ID fingerprint conflicts.

3. Isolated Environment Routing

If you only need to swap accounts because certain projects belong to a different Google account (e.g., personal vs. work), you can isolate the environment by tweaking your execution context.

If you are running the `agy` daemon or automation via custom scripts, you can containerize or run the instances under distinct local user profiles, meaning they will inherently look at separate, isolated OS Keychains.

Would you prefer a quick zsh function template to handle the `security` keychain exports, or are you leaning toward dropping an ecosystem manager into your toolchain?
