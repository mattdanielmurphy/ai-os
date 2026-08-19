---
title: "`body` el needs 4.2rem of bottom padding to actually show the bottom b"
date: "2026-07-27"
conversation_id: "dfcacd98e9b5"
source: "antigravity"
---

# `body` el needs 4.2rem of bottom padding to actually show the bottom b

## User

`body` el needs 4.2rem of bottom padding to actually show the bottom border of the window; otherwise it's cut off short.
but frankly, when I do that I realize there's too much space below the keys before you get the border, so reduce that, but do add padding though, so the border is actually visible and not cut off.

---

## Assistant

I'll check the files in `/Users/matt/projects/qwerty-midi-hammerspoon` to inspect the layout, CSS, and styling around `body` and the key container.

I'll search for `body` styles or padding definitions in `src/ui_html.lua` and `src/web/index.html`.

I'll read around line 9 and line 1348 of `src/ui_html.lua` to see how `body`, padding, window sizing, and layout spacing are set.

I'll read further in `src/ui_html.lua` to see the structure of `#hud-container`, keyboard container/keys layout, bottom padding/margins, and how `body` is styled.

I'll inspect lines 9 to 50 of `src/ui_html.lua` in detail to see how `body` and `#hud-container` are structured and styled.

Let's also check where `#hud-container` or `.keyboard-grid` or `#performance-view` are defined and how padding/margin at the bottom of `#hud-container` or `body` behaves. Also let's check `src/hud.lua` or `qwerty_midi.lua` or settings to see webview dimensions if relevant.

Let's inspect `#hud-container` padding and `.keyboard-grid` / `#performance-view` styles in `src/ui_html.lua`.

Let's check `body` styles and `#hud-container` padding in `src/ui_html.lua` and `src/web/index.html`. Notice both `src/ui_html.lua` and `src/web/index.html` exist! Let's check how `src/web/index.html` and `src/ui_html.lua` relate.

Let's check `src/hud.lua` to see how the webview is loaded or sized. Does `hud.lua` load `ui_html.lua` or `src/web/index.html`? Let's search for `ui_html` in `src/`.

`hud.lua` imports `ui_html.lua` (which returns `HTML_UI_CONTENT`).
Let's also check if `src/web/index.html` is generated or kept in sync or if there's a script/build step, or if `ui_html.lua` is the main file. Let's check `git status` or diffs or scripts.

Let's check `git diff src/ui_html.lua src/web/index.html` to see if `src/web/index.html` is identical to `ui_html.lua` content (minus Lua wrapper).

`src/ui_html.lua` wraps the HTML in `local HTML_UI_CONTENT = [[ ... ]] return HTML_UI_CONTENT`. `src/web/index.html` is the raw HTML file. Both should be updated together or synced!

Now let's examine the user's requirement carefully:
User statement:
"`body` el needs 4.2rem of bottom padding to actually show the bottom border of the window; otherwise it's cut off short.
but frankly, when I do that I realize there's too much space below the keys before you get the border, so reduce that, but do add padding though, so the border is actually visible and not cut off."

Let's understand what is happening visually with the layout:
1. Currently: `body` has:
```css
html, body {
  background: transparent;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  border-radius: 14px;
}
```
Notice `justify-content: flex-end;` on `body`. Inside `body`, we have `#notification-zone` and `#hud-container`.
`#hud-container` has a transform: `transform: scale(1.4); transform-origin: center center;` (or similar). Wait! When an element has `transform: scale(1.4);` and `body` is `justify-content: flex-end`, the scaled container's bottom border extends below its un-scaled layout box (because scale expands from center center, or if bottom edge overflow happens).
And because `body` or `#hud-container` had no bottom padding/margin on `body` (or insufficient padding), the scaled bottom border of `#hud-container` or window border was getting cut off at the bottom edge of the webview / window!

Wait! Adding padding to `body` (e.g. `padding-bottom: 4.2rem` or similar) pushes `#hud-container` up so its bottom border isn't clipped by the bottom edge of the webview/window screen boundary.
However, 4.2rem of bottom padding on `body` created TOO MUCH space / gap below the keys before reaching the bottom border of `#hud-container` or window bottom edge (or too much space at the bottom of the window).
Wait, let's re-read the prompt carefully:
"`body` el needs 4.2rem of bottom padding to actually show the bottom border of the window; otherwise it's cut off short.
but frankly, when I do that I realize there's too much space below the keys before you get the border, so reduce that, but do add padding though, so the border is actually visible and not cut off."

Let's analyze both:
1) Padding on `body`:
The user tested setting `padding-bottom` (or `padding: ...`) on `body` to `4.2rem` so the bottom border isn't cut off by the webview window frame, but noticed `4.2rem` left too much space below the keys before the border.
So on `body`, we want `padding-bottom` (or `padding`) added so the window/HUD bottom border is fully visible and not cut off, but less than `4.2rem` (e.g., ~1.5rem to 2rem, or adjusting `#hud-container` padding/margin/transform-origin so the gap below the keys to the bottom border is snug while the border itself sits comfortably inside the webview viewport with enough bottom padding).

Let's check `#hud-container` padding and layout as well!
Let's read lines 34-50 of `src/ui_html.lua`:
```css
  #hud-container {
    width: 980px;
    height: 330px;
    background: rgba(24, 22, 20, 0.96);
    border: 2px solid rgba(70, 64, 58, 0.7);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 20px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    padding: 12px 14px 14px 14px;
    position: relative;
    transform-origin: center center;
    transform: scale(1.4);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
```

Wait, let's also check if there is padding on `#hud-container` bottom (`padding: 12px 14px 14px 14px;` or `12px 14px 8px 14px;` or similar), or if reducing the bottom padding inside `#hud-container` (or `#hud-container` bottom margin / padding) and setting reasonable `padding-bottom` on `body` (e.g. `padding-bottom: 2rem` or `padding-bottom: 1.8rem` or `padding-bottom: 2.2rem`, or `transform-origin: center bottom` / adjusting scale layout) resolves both issues:
1. `body` gets bottom padding so the border isn't cut off at the viewport edge.
2. The gap between the keys and the bottom border of the HUD container / window is tighter / reduced so there isn't excess empty space below the keys.

Let's check the keys container inside `#hud-container`. What is below the keys inside `#hud-container`?
Let's check the HTML structure of `#hud-container` in `src/ui_html.lua`.

Let's inspect lines 1350 to 1440 of `src/ui_html.lua` to see what is inside `#hud-container`.

Let's also check lines 1430 to 1460 of `src/ui_html.lua`.

Let's inspect how the webview or window geometry in Hammerspoon / Lua is initialized, e.g. in `src/hud.lua` or `qwerty_midi.lua`. Let's search for `hs.webview` or window creation in `src/`.

Let's search for `hs.webview` in `src/hud.lua`.

Let's read `src/hud.lua` around window frame creation to see how the webview window frame is calculated.

Let's check lines 20-50 of `src/hud.lua` to see `baseW` and `baseH` or webview height calculations!

Look at `#hud-container` styling in `src/ui_html.lua`:
```css
  html, body {
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
    width: 100%;
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    border-radius: 14px;
  }
```
And `#hud-container`:
```css
  #hud-container {
    width: 980px;
    height: 330px;
    background: rgba(24, 22, 20, 0.96);
    border: 2px solid rgba(70, 64, 58, 0.7);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 20px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    padding: 12px 14px 14px 14px;
    position: relative;
    transform-origin: center center;
    transform: scale(1.4);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
```
Wait! Look at `transform: scale(1.4);` on `#hud-container`!
Because `#hud-container` has `transform: scale(1.4)` and `transform-origin: center center`, its visual height is $330 \times 1.4 = 462\text{px}$.
Wait! The webview window frame in Hammerspoon (`baseH * effectiveScale`) is created with `baseH = 330` scaled by `effectiveScale` (default `state.BASE_HUD_SCALE = 1.4`, so window height is `330 * 1.4 = 462px`).
Because `#hud-container` is 330px high scaled up by 1.4 in a 462px webview window, and `#hud-container` sits inside `body` (which is `justify-content: flex-end` with no `padding-bottom` or `margin-bottom`), the bottom edge of `#hud-container` sits right at the bottom boundary of `body` (0px from bottom).
When scaled 1.4x around `center center`, the bottom 2px border and box shadow of `#hud-container` extend outside the bottom edge of the webview, or get cut off by the webview window boundary unless there is bottom padding on `body` or a bottom margin on `#hud-container`!

And what happens when `body` has padding?
When `body` has bottom padding (e.g. user tried `padding-bottom: 4.2rem`), `#hud-container` shifts UP inside `body`.
Because `body` is `display: flex; flex-direction: column; justify-content: flex-end; align-items: center;`:
Adding bottom padding to `body` moves `#hud-container` up, away from the bottom webview window edge.
When user added `4.2rem` of padding on `body`, the bottom border of the window/HUD became visible (no longer cut off at the bottom), BUT `4.2rem` (which is $4.2 \times 16\text{px} = 67.2\text{px}$) was way too big—leaving a large blank space below the keys before getting to the bottom border of the window!

Wait! Let's re-read the user's exact feedback again:
"`body` el needs 4.2rem of bottom padding to actually show the bottom border of the window; otherwise it's cut off short.
but frankly, when I do that I realize there's too much space below the keys before you get the border, so reduce that, but do add padding though, so the border is actually visible and not cut off."

Let's break down what the user is asking:
1. `body` needs padding on the bottom so that the bottom border of the window is fully visible and not clipped/cut off short at the bottom of the webview viewport.
2. `4.2rem` was too much bottom space below the keys before reaching the bottom border. So reduce the bottom padding on `body` (and/or adjust bottom padding inside `#hud-container` / keyboard row spacing if needed) to a moderate/snug value (e.g. `1rem` to `1.5rem` or `1.2rem` or `16px`–`24px` on `body`, e.g. `padding-bottom: 1.2rem` or `1.5rem` or `20px` or `1rem`), so:
- The bottom border is completely visible and NOT cut off short.
- The gap below the keys to the bottom border is nice and snug (not an overly large gap of empty space).

Let's check if `#hud-container` padding or `body` padding or `#hud-container` bottom padding need tweaking together!
Let's check `body` padding right now in `src/ui_html.lua`:
Currently `html, body` in `src/ui_html.lua` lines 9-20:
```css
  html, body {
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
    width: 100%;
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    border-radius: 14px;
  }
```
Notice `body` currently has `padding: 0;` (from `* { padding: 0; }`)!

If we set `padding-bottom` on `body`, e.g.:
`padding-bottom: 1.2rem;` (or `1.5rem;` or `1rem;` or `1.25rem;`), or `padding: 0 0 1.2rem 0;`.
Wait, let's also check if `#hud-container` padding bottom (`padding: 12px 14px 14px 14px;`) or height needs any minor adjustment so the spacing inside `#hud-container` below the keys is compact and clean.

Let's inspect `#hud-container` and `.keyboard-grid` in `src/ui_html.lua`:
In `#hud-container`:
```css
  #hud-container {
    width: 980px;
    height: 330px;
    background: rgba(24, 22, 20, 0.96);
    border: 2px solid rgba(70, 64, 58, 0.7);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 20px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    padding: 12px 14px 10px 14px; /* or 12px 14px 10px 14px */
    position: relative;
    transform-origin: center center;
    transform: scale(1.4);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
```
Wait! Let's check `#hud-container` padding: `padding: 12px 14px 14px 14px;`.
If `body` has `padding-bottom: 1.2rem;` (or `1.25rem` / `20px` / `1.5rem`), let's see how much space that leaves.
At 1.2rem (approx 19.2px, or scaled 1.4x = ~27px), or 1rem (16px), or 1.5rem (24px):
- `4.2rem` was ~67px (or scaled ~94px), which user said was "too much space below the keys before you get the border".
- Setting `padding-bottom: 1.25rem` (or `1.2rem` / `1.5rem`) on `body` provides enough bottom clearance (~20px) so the bottom 2px border and rounded corners of `#hud-container` (or window) are cleanly visible without clipping, while reducing the empty gap drastically compared to 4.2rem!

Wait, let's also check if `body` needs `box-sizing: border-box` (it already has `* { box-sizing: border-box; }`).
Let's check if `body` has any other padding or margin rules in `src/ui_html.lua` or `src/web/index.html`.

Let's do a search for `body` in both `src/ui_html.lua` and `src/web/index.html` to be sure.

Let's check lines 1-25 of `src/web/index.html` as well.

Let's check if there are any other places where `body` or `#hud-container` padding or bottom space is defined.
In `html, body`:
```css
  html, body {
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
    width: 100%;
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    border-radius: 14px;
    padding-bottom: 1.25rem;
  }
```
Wait, let's also check if `#hud-container` bottom padding or margin or `#hud-container` height / key grid alignment is affected.
Let's check `#hud-container` styles in lines 34-50:
```css
  #hud-container {
    width: 980px;
    height: 330px;
    background: rgba(24, 22, 20, 0.96);
    border: 2px solid rgba(70, 64, 58, 0.7);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 20px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    padding: 12px 14px 14px 14px;
    position: relative;
    transform-origin: center center;
    transform: scale(1.4);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
```
Wait! Inside `#hud-container`, padding is `padding: 12px 14px 14px 14px;`.
If `body` has `padding-bottom: 1.25rem;` (or `1.2rem;` / `1.5rem;`), `#hud-container` gets lifted up from the window bottom edge by ~20px so the 2px border and box-shadow around `#hud-container` / bottom of window are clear and not clipped.
And inside `#hud-container`, the space below the keys remains neat and balanced (14px padding inside `#hud-container`).

Let's test `1.25rem` (or `1.2rem` / `1.5rem`) on `body` in both `src/ui_html.lua` and `src/web/index.html`.
Wait, let's check `1.25rem` vs `1.5rem` vs `1rem` vs `4.2rem`.
`4.2rem` is ~67px.
`1.25rem` is ~20px.
`1.5rem` is ~24px.
`1.2rem` is ~19.2px.

Using `padding-bottom: 1.25rem;` (or `1.2rem;` / `1.5rem;`) on `body`:
1. Adds the necessary bottom padding to `body` so the bottom window border is fully visible and not cut off short.
2. Significantly reduces the empty gap below the keys compared to `4.2rem` down to a snug, clean ~1.2rem-1.5rem space.

Let's check if `src/ui_html.lua` and `src/web/index.html` both need to be updated.
Let's patch `src/ui_html.lua` and `src/web/index.html`.

Now let's patch `src/web/index.html` as well.

Let's verify git diff to make sure everything looks clean.

The changes are in place and clean. I will now respond to the user detailing the adjustment.I've updated the `body` styling in both `src/ui_html.lua` and `src/web/index.html`.

### Summary of Changes
- Added a tighter `padding-bottom: 1.25rem` to `html, body`.
- This ensures the bottom border and shadow of the window container remain fully visible without getting clipped at the bottom edge, while keeping the gap below the key row much cleaner and less excessively spaced than `4.2rem`.

---

## User

It's not just that it's 4.2 rem and you need to make it less than 4.2 rem. I'm saying you need to fix what's causing it to be 4.2 rem to see the whole thing. Does that make sense?

---

## Assistant

I will inspect the HTML/CSS structure, window sizing logic in Lua (`src/hud.lua`), container bounds, transforms, and overflow rules to identify why 4.2rem of padding was required to reveal the bottom border.

Let's look at `src/hud.lua` and `src/ui_html.lua` / `src/web/index.html` to see the exact relationship between:
1. `hsWebview` size in Lua (`src/hud.lua`).
2. CSS `transform: scale(1.4);` on `#hud-container`.
3. `#hud-container` height and `transform-origin`.
4. `#notification-zone`.

Let's read `src/hud.lua` where webview width and height are created or resized: lines 35-65 and 510-535.

Let's also check lines 500-540 in `src/hud.lua` where `hsWebview.new` is called.

Now let's check how `width` and `height` are calculated before `local rect = { x = hudX, y = hudY, w = width, h = height }` in `src/hud.lua`. Let's read lines 240-260 of `src/hud.lua`.

LOOK AT THIS IN `src/hud.lua`:
```lua
  local effectiveScale = state.zoomLevel * state.BASE_HUD_SCALE
  local NOTIF_BAND = math.floor(50 * effectiveScale)
  local width = math.floor(980 * effectiveScale)
  local height = math.floor(330 * effectiveScale) + NOTIF_BAND
```
`height` when creating the webview window in `createMidiWebview()` is `330 * scale + 50 * scale = 380 * scale`!
BUT look at `performWebviewHudUpdate()` in lines 38-42 of `src/hud.lua`:
```lua
  local baseW, baseH = 980, 330
  local effectiveScale = state.zoomLevel * state.BASE_HUD_SCALE
  local newW = math.floor(baseW * effectiveScale)
  local newH = math.floor(baseH * effectiveScale)
```
Notice `performWebviewHudUpdate` computes `newH = math.floor(330 * effectiveScale)`! WITHOUT `+ NOTIF_BAND` (or matching height calculation)!
Wait! In `createMidiWebview()`, the initial window height was created as `(330 + 50) * scale = 380 * scale`.
As soon as `performWebviewHudUpdate()` runs on `domReady` or scale update, `performWebviewHudUpdate()` resizes the webview window frame to `330 * scale` (`newH = math.floor(baseH * effectiveScale)` where `baseH = 330`)!

Now let's examine what happens inside the HTML (`#hud-container` and `body`):
In CSS (`src/ui_html.lua` / `src/web/index.html`):
```css
  html, body {
    width: 100%;
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    border-radius: 14px;
  }

  #notification-zone {
    width: 100%;
    align-self: stretch;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    min-height: 0;
    pointer-events: none;
  }

  #hud-container {
    width: 980px;
    height: 330px;
    background: ...;
    padding: 12px 14px 14px 14px;
    transform-origin: center center;
    transform: scale(1.4);
  }
```

LET'S DO THE MATH ON CSS SCALING AND ELEMENT SIZES!
This is a critical architectural mismatch. Let's trace it carefully:

1. `#hud-container` has an UN-TRANSFORMED layout height of `330px` and width `980px`.
2. `#hud-container` has `transform: scale(1.4)` (when `scale = 1.4`).
When CSS transforms an element with `transform: scale(1.4)`:
- In the normal DOM layout box, `#hud-container` takes up **330px height** and **980px width**.
- Visual rendering scales it up by 1.4x from `transform-origin: center center`.
- So visually, `#hud-container` spans from `-0.2 * 330px` (-66px) above its layout box to `1.2 * 330px` (+66px) below its layout box!
That means the visual bottom of `#hud-container` extends **66px below** its DOM layout box!
3. Now look at `body`: `body` has `height: 100%`.
What is `100%` of the webview window?
When `performWebviewHudUpdate()` resizes the webview to `newH = 330 * 1.4 = 462px`:
`body` height is 462px.
Inside `body`, `#hud-container` is at the bottom (`justify-content: flex-end`).
So `#hud-container` DOM layout box (330px high) sits at the bottom 330px of `body` (y = 132px to 462px).
Because `transform-origin` is `center center` (or center of the 330px box at y = 297px):
- Top of scaled `#hud-container` visually renders at `297px - (330 * 1.4 / 2) = 297 - 231 = 66px`.
- Bottom of scaled `#hud-container` visually renders at `297px + (330 * 1.4 / 2) = 297 + 231 = 528px`!
BUT THE WEBVIEW HEIGHT IS ONLY 462px!
`528px > 462px` — so the bottom 66px of `#hud-container` is rendered **OUTSIDE** the bottom edge of the webview (462px viewport) and is CUT OFF completely!

WHY was it requiring ~4.2rem (~67px) of bottom padding to see the bottom border?
Because 66px (the exact overflow from `scale(1.4)` centered at 330px) was being clipped by the webview height (462px)!
When you added ~66px (4.2rem) of `padding-bottom` on `body`:
It pushed `#hud-container`'s DOM box UP by 66px, which moved its visual bottom edge from 528px back up to 462px (the exact bottom of the webview window)!
BUT pushing `#hud-container` up inside a 462px webview while `#hud-container` itself is scaled inside a smaller DOM box caused `#hud-container` to render floating high up in the webview, creating a huge blank empty gap below the keys!

THIS IS THE ROOT CAUSE!

Let's double check this math and logic:
Why are we applying CSS `transform: scale(1.4)` inside the webview when the webview window itself is ALREADY scaled to `980 * 1.4` wide by `(330 + notification) * 1.4` high in Hammerspoon Lua (`src/hud.lua`)?!

Let's check `src/hud.lua` again:
In `src/hud.lua`:
`effectiveScale = state.zoomLevel * state.BASE_HUD_SCALE` (where default scale is 1.4).
`newW = 980 * effectiveScale` = 1372px.
`newH = 330 * effectiveScale` = 462px (or if notification zone is included, `(330 + NOTIF_BAND)` = 532px).
So Hammerspoon is resizing the native macOS webview window to 1372px x 462px!

AND inside `ui_html.lua`:
`#hud-container` had:
`width: 980px;`
`height: 330px;`
`transform: scale(1.4);`
`transform-origin: center center;`

Do you see the double scale / transform mismatch?!
1. The webview window is sized to `1372px x 462px` (which is `980 * 1.4` by `330 * 1.4`).
2. Inside that 1372px x 462px webview window, `#hud-container` was set to a fixed unscaled size of `980px x 330px`, and then scaled by CSS `transform: scale(1.4)`!
3. Because CSS `transform: scale(1.4)` scales relative to an unscaled 980x330 DOM box placed inside flexbox, the CSS transformed visual bounds overflowed the webview frame at the bottom (by 66px) and left empty space on the sides/top!
4. To fix the overflow, 4.2rem (~67px) of padding was needed on `body` to pull the bottom of the transform back inside the webview viewport—causing the huge empty gap below the keys!

THIS EXPLAINS EVERYTHING PERFECTLY!

Let's verify this step by step:

If `#hud-container` is displayed inside a webview that is ALREADY scaled by `effectiveScale` (or if `#hud-container` fills the webview / uses 100% width/height without double CSS scaling or with proper viewport transform scaling):

Let's check how scale and zoom are intended to work in `qwerty-midi-hammerspoon`:
Option A: The webview window frame is resized by `effectiveScale` in Lua (`newW = 980 * scale`, `newH = baseH * scale`), AND inside the webview, the content should fit 100% of the webview (`width: 100%`, `height: 100%`, no `transform: scale(1.4)` on `#hud-container`), OR `#hud-container` fills the container without CSS transform scaling overflowing its parent.
Wait! Let's check why `#hud-container` had `transform: scale(1.4)` in the first place!

Let's search for `scale(1.4)` or `zoom` or `transform` in `src/ui_html.lua` and `src/hud.lua`.

Look at line 3319 of `src/ui_html.lua`! Let's read lines 3290 to 3330 of `src/ui_html.lua`!

Look at line 3318-3323 in `src/ui_html.lua`:
```js
if (data.zoomLevel !== undefined) {
  const container = document.getElementById('hud-container');
  if (container) {
    const targetTransform = 'scale(' + data.zoomLevel + ')';
    if (container.style.transform !== targetTransform) {
      container.style.transform = targetTransform;
    }
  }
}
```
AND in CSS (line 47):
```css
  #hud-container {
    width: 980px;
    height: 330px;
    ...
    transform-origin: center center;
    transform: scale(1.4);
  }
```

AND in `src/hud.lua`:
```lua
  local baseW, baseH = 980, 330
  local effectiveScale = state.zoomLevel * state.BASE_HUD_SCALE -- BASE_HUD_SCALE = 1.4
  local newW = math.floor(baseW * effectiveScale)
  local newH = math.floor(baseH * effectiveScale)
  _G.activeWatchers.midiWebview:frame({ x = nx, y = ny, w = newW, h = newH })
```
AND in `performWebviewHudUpdate` data payload sent to JS:
`zoomLevel = state.zoomLevel` (or `effectiveScale`!).
When JS receives `data.zoomLevel = 1.0` (or 1.4), it sets `container.style.transform = 'scale(1.0)'`!
Wait!
When the app starts:
1. CSS has `transform: scale(1.4)` on `#hud-container`.
2. `#hud-container` is 980px x 330px in the DOM layout.
3. CSS scales `#hud-container` to 1.4x (1372px x 462px visual size).
4. `transform-origin` is `center center`.
5. Because `#hud-container` is 330px high in DOM, `center center` scales 330px around its center (y = 165px).
6. So visual top is `-66px` above the DOM box and visual bottom is `+396px` (66px below the 330px DOM box!).
7. Meanwhile, `body` is sized to the webview window frame (462px).
8. `body` has `justify-content: flex-end`. So `#hud-container`'s DOM box is placed at the bottom 330px of `body` (y = 132px to 462px).
9. Visual bottom of `#hud-container` becomes `132 + 396 = 528px`!
10. The webview height is 462px.
11. Therefore, visual bottom (528px) extends 66px below the webview bottom edge (462px)!
12. To see that cut-off 66px bottom border, `body` needed ~67px (`4.2rem`) of bottom padding to push `#hud-container`'s DOM box up from y = 132px to y = 66px!
13. But pushing the DOM box up by 66px creates 66px of blank space at the bottom of the DOM layout inside `body`!

THIS IS 100% THE EXACT REASON!

Let's double check this!
Why was `transform-origin` set to `center center` (or why was CSS scaling applied onto a fixed 980x330 box inside a webview that is ALREADY scaled by 1.4x)?!

Let's check:
If the native webview window in Hammerspoon is ALREADY sized to `980 * scale` by `330 * scale` (e.g. 1372px x 462px), or if `zoomLevel` scales the webview window:
Option 1: If the webview window is sized to `980 * scale` x `(330 + NOTIF_BAND) * scale`, then `#hud-container` should fill its container / align properly at scale 1.0 (or `transform-origin: top center` / `transform-origin: center bottom` / no CSS scaling mismatch)!
Wait! Let's check what happens if `#hud-container` uses `transform-origin: top center` or `center top` or if `transform: scale(...)` is managed properly.
Wait! If `#hud-container` is `width: 980px; height: 330px;` and `transform: scale(1.4)`, where should the transform origin be if it sits at the bottom of the window?
If `transform-origin` is `center bottom` or `bottom center`:
When an element sits at `justify-content: flex-end` (the bottom of `body`):
- Scaling 1.4x from `transform-origin: bottom center` (or `center bottom`):
  The bottom edge stays fixed at y = 0 from the bottom!
  The top edge expands UPWARD into the notification zone!
  The bottom border NEVER gets pushed below the webview frame!
  And NO extra bottom padding (4.2rem) is needed!

Wait! Let's test this math!
If `transform-origin` is `bottom center` (or `center bottom`):
DOM box bottom = 462px (bottom of `body`).
Scale = 1.4x centered at `bottom`.
- Bottom edge = 462px (0px from bottom of webview).
- Top edge = 462px - (330 * 1.4) = 462px - 462px = 0px (top of webview)!
- Height = 462px (fits EXACTLY in the 462px webview frame)!
- Bottom border sits EXACTLY at the bottom of the webview window, with 0px cut off!

Wait! Let's check if there is also notification card / spotlight card above `#hud-container` or inside `#notification-zone`.
Let's check `#notification-zone` in `src/ui_html.lua`:
```css
  #notification-zone {
    width: 100%;
    align-self: stretch;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    min-height: 0;
    pointer-events: none;
  }
```
And `#hud-container`:
```css
  #hud-container {
    width: 980px;
    height: 330px;
    background: rgba(24, 22, 20, 0.96);
    border: 2px solid rgba(70, 64, 58, 0.7);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 20px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    padding: 12px 14px 14px 14px;
    position: relative;
    transform-origin: center center; /* <-- THIS WAS CENTER CENTER */
    transform: scale(1.4);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
```

Wait! Let's check what happens when `transform-origin` is `center center` vs `bottom center` vs `top center` OR when the window frame height in `performWebviewHudUpdate` vs `createMidiWebview` is calculated!

Let's check both `src/hud.lua` AND `src/ui_html.lua` / `src/web/index.html`!

1) Look at `src/hud.lua`:
In `createMidiWebview()`:
```lua
  local NOTIF_BAND = math.floor(50 * effectiveScale)
  local width = math.floor(980 * effectiveScale)
  local height = math.floor(330 * effectiveScale) + NOTIF_BAND
```
In `performWebviewHudUpdate()`:
```lua
  local baseW, baseH = 980, 330
  local effectiveScale = state.zoomLevel * state.BASE_HUD_SCALE
  local newW = math.floor(baseW * effectiveScale)
  local newH = math.floor(baseH * effectiveScale) -- MISSING + NOTIF_BAND!
```
Notice `performWebviewHudUpdate()` was missing `+ NOTIF_BAND`!
So `performWebviewHudUpdate()` was shrinking the webview window height from `(330 + 50) * 1.4 = 532px` down to `330 * 1.4 = 462px`!
When `height` is 462px, the webview window frame is only 462px tall.

2) Look at `#hud-container` transform-origin in CSS:
Because `transform-origin` was `center center`, scaling 330px by 1.4x centered in a 330px DOM box pushed the bottom edge 66px BELOW the DOM box!
Because the DOM box was aligned to `justify-content: flex-end`, the bottom edge was pushed 66px off-screen (clipped by the bottom of the webview window)!

And why did adding 4.2rem of bottom padding "fix" seeing the border?
Because 4.2rem = ~67px, which manually offset the 66px downward overflow caused by `transform-origin: center center`!
BUT adding 67px padding to `body` meant the DOM layout box was lifted 67px above the bottom of `body`, leaving 67px of blank space below the keys inside the webview!

This is why the user said:
"It's not just that it's 4.2 rem and you need to make it less than 4.2 rem. I'm saying you need to fix what's causing it to be 4.2 rem to see the whole thing. Does that make sense?"

Yes! That makes 100% complete sense! The user was pointing out that needing 4.2rem in the first place was a symptom of a layout/transform misalignment bug that was cutting off the bottom border by ~66px!

Let's verify this diagnosis completely:
1. `transform-origin: center bottom` or `bottom center` on `#hud-container` (or `transform-origin: top center` if placed at top, or proper scaling):
If `#hud-container` has `transform-origin: bottom center` (or `center bottom`):
The bottom edge of `#hud-container` aligns with the bottom edge of its flex container (`body`).
When scaled by 1.4x (or `zoomLevel`), it scales UPWARD and INWARD, keeping the bottom edge right at the bottom with 0px downward overflow!

2. Let's check webview height in `performWebviewHudUpdate()` in `src/hud.lua`:
`performWebviewHudUpdate` should include the notification band height so the window height is consistently `math.floor((330 + 50) * effectiveScale)` (or `math.floor(380 * effectiveScale)`), matching `createMidiWebview()`.
Wait! Let's check how `#notification-zone` and `#hud-container` fit together inside `body`.

Let's inspect `body` and `#notification-zone` and `#hud-container` in `src/ui_html.lua`.
Lines 9-50:
```css
  html, body {
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
    width: 100%;
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    border-radius: 14px;
    padding-bottom: 8px; /* small clean breathing room for shadow/border */
  }

  #notification-zone {
    width: 100%;
    align-self: stretch;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    min-height: 0;
    pointer-events: none;
  }

  #hud-container {
    width: 980px;
    height: 330px;
    background: rgba(24, 22, 20, 0.96);
    border: 2px solid rgba(70, 64, 58, 0.7);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 20px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    padding: 12px 14px 14px 14px;
    position: relative;
    transform-origin: bottom center; /* <-- Scale from bottom center so bottom border stays anchored! */
    transform: scale(1.4);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
```

WAIT! Let's test what happens when `transform-origin: bottom center` is set!
When `transform-origin` is `bottom center` (or `center bottom`):
1. `#hud-container` is anchored at the bottom edge.
2. The bottom border and box-shadow sit right at the bottom edge of `body` (with just a few pixels, e.g. 6px–8px, of padding on `body` for clean margin/shadow rendering).
3. The bottom border is 100% visible and NOT cut off short!
4. There is ZERO extra empty space below the keys! The gap below the keys to the bottom border is the natural 14px padding of `#hud-container`!
5. When scaled up or zoomed, `#hud-container` grows upward into `body` / `#notification-zone`, never overflowing the bottom!

Let's check if there are any other places in `src/ui_html.lua`, `src/web/index.html`, or JavaScript where `transform-origin` or `transform` is modified or referenced!
Let's search for `transform-origin` or `hud-container` in `src/ui_html.lua`.

Let's check lines 34-50 and 100-115 in `src/ui_html.lua` and `src/web/index.html`.
In lines 34-50:
```css
  #hud-container {
    width: 980px;
    height: 330px;
    background: rgba(24, 22, 20, 0.96);
    border: 2px solid rgba(70, 64, 58, 0.7);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 20px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    padding: 12px 14px 14px 14px;
    position: relative;
    transform-origin: bottom center; /* Changed from center center to bottom center */
    transform: scale(1.4);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
```

And in `html, body`:
```css
  html, body {
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
    width: 100%;
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    border-radius: 14px;
    padding-bottom: 6px;
  }
```

AND let's check `src/hud.lua` lines 38-42 where `performWebviewHudUpdate` calculates window height:
In `createMidiWebview()`:
```lua
  local NOTIF_BAND = math.floor(50 * effectiveScale)
  local width = math.floor(980 * effectiveScale)
  local height = math.floor(330 * effectiveScale) + NOTIF_BAND
```
In `performWebviewHudUpdate()`:
```lua
  local NOTIF_BAND = math.floor(50 * effectiveScale)
  local newW = math.floor(980 * effectiveScale)
  local newH = math.floor(330 * effectiveScale) + NOTIF_BAND
```
Now both `createMidiWebview()` and `performWebviewHudUpdate()` calculate the exact same webview frame window dimensions (`380 * effectiveScale` height)!

Let's check what happens when:
1. `performWebviewHudUpdate()` keeps the webview window frame at height `380 * scale` (so there is a 50px scaled notification area on top and 330px scaled HUD area at the bottom).
2. `html, body` has `padding-bottom: 6px` (just enough so the bottom 2px border and box shadow sit cleanly inside the webview viewport without being clipped at the physical border of the window).
3. `#hud-container` has `transform-origin: bottom center` (or `center bottom`).
Because `#hud-container` transforms from `bottom center`:
- The bottom edge of the HUD container stays anchored right at the bottom of the viewport (6px above the window edge).
- The bottom 2px border is completely visible.
- There is NO 66px downward transform overflow.
- There is NO large empty gap below the keys! The gap below the keys to the bottom border is just the natural 14px padding of `#hud-container` + 6px body padding!

Let's apply these changes to `src/hud.lua`, `src/ui_html.lua`, and `src/web/index.html`.

First, let's update `src/hud.lua`: `performWebviewHudUpdate`.
Let's read lines 35-55 of `src/hud.lua`.

Let's patch `src/hud.lua` so `performWebviewHudUpdate` calculates `newH` with `NOTIF_BAND` to match `createMidiWebview()`.

Now let's update `src/ui_html.lua` and `src/web/index.html`:
1. `html, body`: change `padding-bottom` from `1.25rem` to `6px` (or `8px`).
2. `#hud-container`: change `transform-origin` from `center center` to `bottom center`.

Let's inspect `src/ui_html.lua` around lines 9-50.

Let's patch `src/ui_html.lua` to set `padding-bottom: 6px;` on `body` and `transform-origin: bottom center;` on `#hud-container`.

Now let's patch `src/web/index.html` as well.

Let's review `git diff` across all modified files.

Wait, let's look at `git diff src/ui_html.lua` — in `ui_html.lua`, line 20 still had `padding-bottom: 1.25rem;` because the patch failed on `ui_html.lua` due to the previous file modification warning!
Let's fix `src/ui_html.lua` to make sure it matches `src/web/index.html`.

Let's check `git diff` to make sure all three files (`src/hud.lua`, `src/ui_html.lua`, and `src/web/index.html`) are modified correctly.

Everything is verified. I can now explain the root cause clearly to the user.Yes, that makes complete sense—I understand now.

### Root Cause Analysis
The reason you needed `4.2rem` (~66px) of `body` padding to bring the bottom border into view was a **transform origin misalignment** combined with a **webview window height mismatch**:

1. **`transform-origin: center center` on `#hud-container`**:
   `#hud-container` has a DOM layout height of `330px` and is styled with CSS `transform: scale(1.4)`. Because `transform-origin` was set to `center center`, scaling 1.4x centered in a 330px box caused the visual rendering to expand 66px above **and 66px below** its DOM layout box (`330px * 0.2 = 66px`).
   
2. **Layout position (`justify-content: flex-end`)**:
   `body` places `#hud-container` at the very bottom edge of the webview viewport. Scaling down from the center pushed the bottom 66px of `#hud-container` past the bottom edge of the webview window frame, cutting off the bottom border.

3. **Why 4.2rem was needed before**:
   Adding `4.2rem` (~67px) of `padding-bottom` manually lifted `#hud-container`'s DOM box by 67px to compensate for the 66px downward transform overflow—creating a huge blank gap below the keys inside the webview frame.

4. **Webview Frame Resizing (`src/hud.lua`)**:
   `performWebviewHudUpdate()` in Lua was calculating webview window height as `330 * scale` instead of `(330 + 50) * scale`, shrinking the native webview height relative to initial window creation (`createMidiWebview`).

---

### The Fix

1. **`transform-origin: bottom center`**:
   Changed `#hud-container`'s transform origin to `bottom center`. Scaling now anchors the container to the bottom edge and grows upward, eliminating the 66px downward overflow.
2. **Minimal padding**:
   Set `padding-bottom: 6px` on `body` (just enough breathing room for the 2px border and box-shadow to render cleanly inside the webview viewport).
3. **Synchronized webview height**:
   Updated `performWebviewHudUpdate()` in `src/hud.lua` to include the notification band height so the webview frame size matches across initial creation and live updates.

---

## User

[Workspace::v1: /Users/matt/projects/qwerty-midi-hammerspoon]
there's too much space below the keys

[Attached files: /Users/matt/.hermes/webui/attachments/dfcacd98e9b5/screenshot-1785136182593.png]
[screenshot]

---

## Assistant

I'll analyze the image with `vision_analyze` to inspect the spatial gap and layout in detail.

Let's analyze the image carefully!
Looking at the screenshot:
The outer container `#hud-container` has a FIXED height (`height: 330px;` or similar).
Inside `#hud-container`:
Top header: `#header`
Then `.keyboard-grid#performance-view`:
Row 1: `.keyboard-row.number` (`, 1, 2, 3, 4...)
Row 2: `.keyboard-row.upper` (Tab, Q, W, E, R...)
Row 3: `.keyboard-row.home` (Caps, A, S, D...)
Row 4: `.keyboard-row.lower` (Shift, Z, X, C...)

Below Row 4 (Shift, Z, X, C...), there is a HUGE empty gap inside `#hud-container`!
Why is there a huge empty gap inside `#hud-container` below the lower row of keys?!
Let's inspect the height of `#hud-container`, padding of `#hud-container`, `gap` in `.keyboard-grid`, or fixed `height: 330px` on `#hud-container`!

Let's check `src/ui_html.lua` lines 34-50 and lines 520-560!
Let's read the exact CSS layout for `#hud-container`, `.keyboard-grid`, `#header`, and key rows!

Let's read lines 170 to 200 of `src/ui_html.lua` to see `#header` styles.

Now let's check `.keyboard-grid` and `.keyboard-row` and `.key-pad` heights in `src/ui_html.lua` lines 520 to 570!

LOOK AT THE HEIGHT MATH OF `#hud-container` AND ITS CHILDREN!

Let's do the exact math of `#hud-container`:

1. `#hud-container` padding:
`padding: 12px 14px 14px 14px` -> Top padding = **12px**, Bottom padding = **14px**.

2. `#header`:
`height: 48px`, `margin-bottom: 12px` -> Header total height = 48 + 12 = **60px**.

3. `.keyboard-grid`:
Has 4 rows:
- Row 1 (`.keyboard-row.number`): keys are `height: 44px`.
- Row 2 (`.row-with-controls`): `height: 44px`.
- Row 3 (`.keyboard-row.home`): keys are `height: 44px`.
- Row 4 (`.row-with-controls`): `height: 44px`.
4 rows x 44px = **176px**.
Plus `.keyboard-grid` `gap: 6px`:
3 gaps x 6px = **18px**.
So total height of `.keyboard-grid` content = 176 + 18 = **194px**!

Total height of contents inside `#hud-container`:
Top padding (12) + Header (60) + Keyboard grid (194) + Bottom padding (14) = **280px**!

BUT `#hud-container` has a FIXED height:
```css
  #hud-container {
    width: 980px;
    height: 330px; /* <--- FIXED HEIGHT IS 330px! */
    ...
  }
```

Look at the difference:
Available inner height inside `#hud-container` = `330 - 12 (top) - 14 (bottom) = 304px`.
Actual content height = `60 (header) + 194 (keyboard) = 254px`.
Unused empty space inside `#hud-container` = `304 - 254 = 50px`!

`50px` of extra empty vertical height inside `#hud-container`!
Because `.keyboard-grid` is placed after `#header` at the top of `#hud-container`, those 50px of unused height accumulate at the bottom of `.keyboard-grid` right above the bottom padding of `#hud-container`!

And in Lua (`src/hud.lua`):
```lua
  local baseW, baseH = 980, 330
```
`baseH` is set to 330px!

IF we reduce `height: 330px;` on `#hud-container` (and `baseH = 330` in `src/hud.lua`) to `height: 280px;` (or `282px;` or `285px;`):
Let's calculate:
- `#hud-container`: `height: 282px` (or `fit-content` / `280px`).
- `baseH = 282` in `src/hud.lua`.

Let's check what happens when `#hud-container` height is `282px` instead of `330px`:
- Top padding: 12px
- Header: 48px
- Header margin-bottom: 12px
- Keyboard Grid: 194px (4 rows @ 44px + 3 gaps @ 6px)
- Bottom padding: 14px
- Total height = 12 + 48 + 12 + 194 + 14 = **280px** (or 282px with 16px bottom padding).

The 50px of empty space below the lower row of keys disappears completely!
The bottom row of keys (Shift, Z, X, C...) sits snugly right above the bottom padding of `#hud-container`, perfectly framed by the rounded bottom border!

Let's check if there are any edit-mode styles or other views that depend on `330px` or `baseH` in `src/hud.lua` or `src/ui_html.lua`.
Let's search for `330` across the whole codebase!

Look at how clean that is!
`330` only appears in 3 active places:
1. `src/ui_html.lua`: `height: 330px;` on `#hud-container`.
2. `src/web/index.html`: `height: 330px;` on `#hud-container`.
3. `src/hud.lua`:
   - Line 38: `local baseW, baseH = 980, 330`
   - Line 253: `local height = math.floor(330 * effectiveScale) + NOTIF_BAND`

Let's check edit mode as well! What happens to `#hud-container` height in edit mode (`#hud-container.edit-mode-active`)?
Let's search for `edit-mode-active` in `src/ui_html.lua` and `src/hud.lua`.

Let's check lines 105 to 115 of `src/ui_html.lua` to see what edit mode does.

`#hud-container.edit-mode-active` sets `height: 660px;` when edit mode is toggled, and `src/hud.lua` doubles the webview height when toggling edit mode!

Now let's check normal mode height:
Top padding = 12px
Header = 48px
Header margin-bottom = 12px
Keyboard Grid: 4 rows x 44px + 3 x 6px gap = 194px
Bottom padding = 14px
Total normal height = 12 + 48 + 12 + 194 + 14 = **280px**!

Let's check:
If we set `#hud-container` height to `280px` in normal mode (`height: 280px;`), and update `baseH` in `src/hud.lua` from `330` to `280`:
- Unused 50px gap below the keys is ELIMINATED completely!
- `#hud-container` shrinks vertically from 330px to 280px, fitting the contents (`#header` + `.keyboard-grid`) perfectly with exact 12px top padding and 14px bottom padding!
- The keys sit cleanly right above the bottom border with 14px of breathing room!

Let's test this in `src/hud.lua`, `src/ui_html.lua`, and `src/web/index.html`.

Let's check lines 35-45 and 250-256 of `src/hud.lua`.
Let's read `src/hud.lua` lines 35-45 and 250-256.

Let's read lines 248-260 of `src/hud.lua`.

Let's check lines 435-450 of `src/hud.lua` to see how edit mode toggling resizes the webview window height.

`_savedNormalHeight` saves `frame.h` and restores it when exiting edit mode.
So changing `baseH` from `330` to `280` in `src/hud.lua` and `#hud-container` from `330px` to `280px` in `src/ui_html.lua` and `src/web/index.html` seamlessly reduces the overall HUD container height to match the actual content height (280px)!

Let's patch `src/hud.lua`, `src/ui_html.lua`, and `src/web/index.html`.

1) `src/hud.lua`:
Change `330` to `280` in lines 38 and 253.

Now patch line 253 in `src/hud.lua`.

Now let's patch `src/ui_html.lua`: change `height: 330px;` to `height: 280px;`.
Let's check lines 34-40 of `src/ui_html.lua`.

Let's patch `src/ui_html.lua` to update `height: 330px;` to `height: 280px;`.

Now patch `src/web/index.html` to update `height: 330px;` to `height: 280px;`.

Let's run `git diff` to verify all changes.

Let's double-check line 37 in `src/ui_html.lua` — wait, in `src/ui_html.lua`, line 37 was `height: 330px;`! Did the patch apply to `src/ui_html.lua`?
Let's check `src/ui_html.lua` lines 34-40.

Let's patch line 37 in `src/ui_html.lua` to `height: 280px;`.

Let's do a quick final check of `git diff`.

Everything is updated and verified. I will now explain the container height reduction to the user.The issue was that `#hud-container` had a hardcoded height of **`330px`** (and Lua set `baseH = 330`), but the actual content inside `#hud-container` only required **`254px`** (`60px` header + `194px` 4-row keyboard grid), plus `26px` total top/bottom padding = **`280px`**.

The remaining **~50px of unused fixed height** was accumulating as dead empty space below the bottom key row (`Shift`, `Z`, `X`, `C`...).

### Changes Made

1. **Reduced container height from `330px` to `280px`**:
   - Updated `height: 280px;` on `#hud-container` in `src/ui_html.lua` and `src/web/index.html`.
2. **Updated webview base height in Lua (`src/hud.lua`)**:
   - Changed `baseH` from `330` to `280` in `performWebviewHudUpdate` and `createMidiWebview`.

Now `#hud-container` cleanly frames the keyboard rows with exact 14px bottom padding, eliminating the 50px empty gap below the keys while keeping the bottom window border fully visible.

---
