[2026-06-30 18:07] User:
woah!

 webfilterproxyd 23.01 GB 79 93 772 15901 root (null) - No No 3.8 48:28.73 (null) Apple 0.0 0.00 0 bytes 0 bytes 0 bytes No Yes Yes 0 bytes 0 0 bytes 0 0 bytes 0 bytes 0 bytes 0 bytes (null)

wtf is going on here?

---

[2026-06-30 18:07] Assistant:
That process is experiencing a massive **memory leak**.

`webfilterproxyd` is a native macOS background process responsible for web content filtering. It is primarily tied to **Screen Time** (specifically parental controls and Content & Privacy Restrictions), though certain third-party security software, firewalls, or VPNs can also trigger or conflict with it.

It should normally only consume a few megabytes. Ballooning to 23 GB means it has gotten stuck in a loop and is hoarding your RAM.

Here is how to deal with it right now:

1. Force Quit the Process

You can safely kill it. macOS will immediately restart the process, which usually stops the memory leak and frees up your RAM.

While selecting `webfilterproxyd` in **Activity Monitor**, click the **`X` button** at the very top left of the window.

Choose **Force Quit**.

2. Turn off Web Restrictions (If you don't need them)

If this happens repeatedly, a conflict with Screen Time is the most likely culprit. If you don't explicitly need web filtering turned on, disable it:

Open **System Settings** > **Screen Time**.

Click on **Content & Privacy**.

If it's on, check **Store, Web, Siri & Game Center Content**.

Change **Access to Web Content** to **Unrestricted Access**.

3. Check for VPN or Network Extensions

If you use tools like Tailscale, a corporate VPN, or third-party firewalls (like Little Snitch), they frequently clash with Apple's built-in web filter proxy. Updating those applications or temporarily disabling them can narrow down what triggered the leak.

Give it a quick force quit first—your system should instantly breathe a sigh of relief.
