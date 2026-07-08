[2026-07-07 19:41] User:
In my tauri webview, the scroll bars on stuff look hideous. how to get a nice macos disappearing minimalist scroll bar?

---

[2026-07-07 19:41] Assistant:
Since Tauri uses the system's native webview (WebKit on macOS, WebView2 on Windows), standard scrollbars default to whatever the operating system dictates. If you want a uniform, minimalist, macOS-style disappearing scrollbar across all platforms, you can achieve this entirely using custom CSS.

The cleanest approach uses CSS custom scrollbar properties alongside pseudo-elements to handle older webview engines.

The Universal CSS Solution

Add this snippet to your global CSS file (e.g., `index.css` or `App.css`):

CSS

```
/* 1. Hide the standard scrollbar track by default */
::-webkit-scrollbar {
  width: 8px;  /* Vertical scrollbar width */
  height: 8px; /* Horizontal scrollbar height */
  background: transparent;
}

/* 2. Style the draggable handle (the thumb) */
::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2); /* Subtle gray */
  border-radius: 10px;            /* Fully rounded edges */
  border: 2px solid transparent;  /* Creates padding around the thumb */
  background-clip: padding-box;   /* Keeps background inside borders */
}

/* 3. Make the thumb slightly darker on hover */
::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.4);
  background-clip: padding-box;
}

/* 4. For modern standards compliance (Firefox/Linux compatibility) */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

```

Making It "Disappearing" (Fade on Hover)

True macOS scrollbars stay hidden until the container is actively scrolled or hovered. Pure CSS cannot easily detect "on scroll" activity without JavaScript, but you can fake the macOS "fade in on container hover" effect like this:

CSS

```
/* Container defaults to hiding the scrollbar thumb */
.scroll-container::-webkit-scrollbar-thumb {
  background: transparent;
}

/* Thumb reveals itself when the container is hovered */
.scroll-container:hover::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border: 2px solid transparent;
  background-clip: padding-box;
}

.scroll-container:hover::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.4);
  background-clip: padding-box;
}

```

A Dark Mode Adjustment

If your application has a dark interface, the dark gray thumb won't show up well. Swap the color values to a light, translucent white instead:
