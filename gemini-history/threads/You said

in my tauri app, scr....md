[2026-06-30 00:02] User:
in my tauri app, scrollbars are shown always on the web views and it's a Mac, I want auto scrollbars and for them to be more discrete and dark mode friendly

---

[2026-06-30 00:02] Assistant:
This is a common issue with WebKit-based apps on macOS. By default, WebKit (which Tauri uses via `wkwebview`) can sometimes force scrollbars to remain visible regardless of system preferences, and standard scrollbar styling doesn't automatically inherit app dark mode changes seamlessly unless explicitly configured.

You can fix this entirely using CSS.

1. The CSS Solution

Add the following styles to your global CSS file (e.g., `index.css` or `style.css`). This targets WebKit's scrollbar pseudo-elements to force the "overlay" behavior and apply discrete, dark-mode-friendly colors.

CSS

```
/* Ensure the body and containers handle overflow correctly */
html, body {
  overflow: auto;
}

/* 1. Force the scrollbar to be discrete and use custom dimensions */
::-webkit-scrollbar {
  width: 8px;  /* Width of vertical scrollbar */
  height: 8px; /* Height of horizontal scrollbar */
  background: transparent; /* Makes the track invisible until hovered */
}

/* 2. The Scrollbar Track (the background) */
::-webkit-scrollbar-track {
  background: transparent;
}

/* 3. The Scrollbar Thumb (the draggable handle) */
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2); /* Semi-transparent white for dark mode */
  border-radius: 4px; /* Fully rounded edges */
  border: 2px solid transparent; /* Acts as padding inside the track */
  background-clip: padding-box; /* Ensures the border doesn't overlap the background */
}

/* 4. Hover effect to make it slightly more visible when interacting */
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.4);
  border: 2px solid transparent;
  background-clip: padding-box;
}

/* 5. Optional: Light mode overrides if your app supports both */
@media (prefers-color-scheme: light) {
  ::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.4);
  }
}

```

2. Why This Works

**`background-clip: padding-box`**: This is the trick to getting that slim, native macOS look. It creates an invisible padding boundary around the thumb so it looks discrete and floating, rather than filling the entire 8px width.

**`rgba` Colors**: By using transparent alpha channels (`rgba(255, 255, 255, 0.2)`), the scrollbar naturally blends into whatever background color your webview is currently rendering.

3. Check macOS System Settings

If the scrollbars *still* persist after applying the CSS, check your macOS system-wide setting under **System Settings > Appearance > Show scroll bars**.

If it is set to **Always**, macOS overrides webview behaviors and forces them to stay visible. Setting it to **Automatically based on mouse or trackpad** or **When scrolling** will let your new CSS auto-hide properly when idle.
