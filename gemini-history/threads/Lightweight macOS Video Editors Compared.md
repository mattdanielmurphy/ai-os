[2026-07-07 16:46] User:
is there a really lightweight super fast free video editor for macos?

---

[2026-07-07 16:46] Assistant:
Depending on what you mean by "lightweight" and "super fast," there are two distinct ways to go.

If you just need to shave down large files, trim clips, or merge footage without bogging down your Mac, you don't need a heavy, traditional non-linear timeline editor.

1. For Instant Trimming & Splicing: **LosslessCut**

If your goal is to rough-cut footage from a camera, drone, or screen recording without waiting hours for rendering, this is the tool.  
MacUpdate

**How it works:** It uses FFmpeg under the hood to directly cut the video stream without re-encoding or transcoding the file.  
Wikipedia

**The Speed:** Because it skips the rendering process entirely and just copies the raw data streams, it exports a 5GB video in **less than a second**.  
LosslessCut

**Specs:** Open-source, under 200 MB in size, completely free, and natively supports Apple Silicon.  
Wikipedia

**Best for:** Trimming, changing container formats (e.g., MKV to MP4), or stripping audio tracks instantly with zero quality loss.  
SourceForge

2. For Snappy Timeline Editing: **VN Video Editor** or **iMovie**

If you need an actual multi-track timeline to layer audio, add text, or apply transitions, a full suite like DaVinci Resolve can feel massive and slow to navigate.

**VN Video Editor:** Originally built as a mobile editor, the desktop macOS native version is incredibly fast, clean, and entirely free with **no watermarks**. It gives you precise frame-accurate timeline editing, keyframe animations, and speed curves without the bloat of a desktop suite.  
Gizmodo
+ 1

**iMovie:** Don't sleep on the default Mac app. Because it's deeply integrated into macOS, it leverages Apple Silicon hardware acceleration better than almost any third-party freeware, making timeline scrubbing and 4K rendering exceptionally smooth.  
XP-Pen

**Quick Tip:** If you are trying to cut highly compressed codecs (like H.264 or H.265) frame-by-frame in LosslessCut, it has to cut at the nearest keyframe to avoid re-rendering. If you need pixel-perfect cuts down to the individual millisecond across multiple overlapping tracks, opt for **VN** or **iMovie** instead.  
Wikipedia

What kind of video project are you putting together?

---

[2026-07-07 16:47] User:
yeah I just want to be able to do extremely simple cuts and splices

---

[2026-07-07 16:47] Assistant:
If it's strictly simple cuts and splices, **LosslessCut** is exactly what you want. It's essentially just a visual interface for slicing up the raw file data directly.

Because it doesn't re-encode the video, cutting a massive file takes the same amount of time as copying a file from one folder to another on your SSD—it is practically instant.

Here is the quickest way to grab it and the basic workflow to get moving:

Getting the App

You can download the official DMG file for free directly from the project's GitHub page (the Mac App Store version is a paid download purely to support the developer, but the GitHub release is identical and 100% free).

How to Use It

**Drop the File:** Drag your video file directly into the player window.

**Mark Your Cuts:** Use the spacebar to play/pause, and use the `<` and `>` keys (or **I** and **O**) to set your **In** and **Out** points for a segment.

**Keep or Discard:**

Press the **+** (plus) button to add the current selection to your export list.

You can create multiple segments from the same video file, and the app will automatically splice them together into a single file when you export.

**Export:** Click the **Export** button in the bottom right corner. A pop-up will ask if you want to merge the segments—keep that checked, hit export, and your edited video will appear in the source folder instantly.

---

[2026-07-07 16:47] User:
tand ideally it's something I can just like instantly spawn from the finder or something, I don

---

[2026-07-07 16:47] Assistant:
You can easily configure this so you can just select a video file in Finder, press a hotkey or right-click, and instantly pass it to LosslessCut without even having the app sitting open in your dock.

The cleanest native way to handle this on macOS is by building a **Quick Action** using the Shortcuts app.

How to set up a Finder Quick Action for LosslessCut

Open the native **Shortcuts** app on your Mac.  
MacRumors

Click the **+** (plus) icon in the top toolbar to create a new shortcut.

In the right-hand panel, click **Shortcut Details** (the info icon) and check the box for **Use as Quick Action**. Under "Provide files to", ensure **Finder** is selected.  
MacRumors

Set the top input line to read: `Receive [Files] input from [Quick Actions]`.

In the action search bar on the right, search for **Open File**. Drag that action into the main window.

Set it to: `Open [Shortcut Input] in [LosslessCut]`.

*(Optional)* Click the Shortcut Details tab again and click **Add Keyboard Shortcut** to map it to something fast, like `Option + C`.

The Result

Whenever you are browsing files in Finder, you can just tap your hotkey (or right-click the video, go to **Quick Actions**, and select your shortcut). The file will instantly launch straight into the LosslessCut interface, ready for you to drop your *In* and *Out* points and export.  
MacRumors

---

[2026-07-07 17:27] User:
lossless cut is incredible.

I just find the design decisions quite strange. Like you see the original clip, and you just make edit points and then you assign an order number to each clip, so that's how you rearrange clips. It'd be so much more sensible to, after slicing the clip, drag them in the order you want.

But it's amazing to just have a video export almost instantly.

---

[2026-07-07 17:27] Assistant:
It is a massive mental shift from standard video editing, for sure. The interface feels completely backwards at first because it's built around **extracting data segments** rather than laying things out on a canvas.

The reason it uses that rigid segment list with ordering numbers instead of a drag-and-drop timeline comes down to how it works under the hood:

**It's a wrapper for a command-line tool:** LosslessCut is essentially a visual skin for **FFmpeg**, a powerful command-line program that processes raw media streams.

**The "Concat" process:** When you hit export, LosslessCut creates a simple text file listing the exact timestamps you want to keep, then tells FFmpeg: *"Extract segment A, extract segment B, then stitch (concatenate) them together."*

**UI limitations:** Because the developer (Michele) is translating raw text timestamps into a visual app using web technologies (Electron), building a smooth, interactive drag-and-drop timeline would require a massive overhaul of how the app tracks and calculates those precise file offsets.

It sacrifices a lot of user experience conventions just to keep the app lightweight and laser-focused on that raw, instantaneous file-copying speed. Once you get used to treating the segment list on the side as your "timeline," it becomes a weirdly fast workflow—but it definitely takes some unlearning!

---

[2026-07-07 17:29] User:
I really don't think it WOULD be difficult to have drag and drop at all.




It's literally just representing the same thing in a different way: instead of showing:




```

[Clip A: order=4] [Clip B: order=2] [Clip C: order=1] [Clip D: order=3]

```




You're doing

```

[ Clip C ] [ Clip B ] [ Clip D ] [ Clip A ]

```




And when you drag the clips around, it changes the order value

---

[2026-07-07 17:29] Assistant:
You are 100% right. From a data-modeling perspective, it is exactly the same logic under the hood: changing the order of a list array when a UI element is moved.

The barrier isn't the data mapping; it's the specific architecture the developer chose. Because LosslessCut is built as a highly utilitarian wrapper, its UI elements are mapped directly to a basic sidebar list of text tracks rather than a canvas or timeline component. While implementing a standard JavaScript drag-and-drop library (like `react-sortable-hoc` or native HTML5 drag-and-drop) to reorder that sidebar array is standard front-end development, the app's focus has always been purely on exposing FFmpeg's functions as simply as possible rather than refining the user experience.

There is actually an open discussion about this exact feature on the LosslessCut GitHub repository. Users have pointed out exactly what you did: dragging segments to reorder them is infinitely more intuitive than manually clicking arrows or typing index numbers.

Until the UI gets that overhaul, you're stuck doing mental math with the track list, but at least the underlying engine still delivers that near-instantaneous export.

---

[2026-07-07 17:30] User:
But can I or has someone made a reasonable UI for the underlying engine or whatever? I mean, it's pretty basic ffmpeg commands under the hood right

---

[2026-07-07 17:30] Assistant:
It really is just a straightforward series of standard `ffmpeg` commands stringing together `-ss` (start time), `-to` (end time), `-c copy` (codec copy), and a final `concat` demuxer text file to merge them back up.

Because the backend math is so straightforward, several developers have attempted to build a prettier wrapper for it. The primary direct open-source alternative that tackled the exact drag-and-drop timeline problem you mentioned is **VidCutter**.

The Alternative: VidCutter

VidCutter is built using Python and Qt5 rather than Electron. Its user interface operates exactly how you described: you make your cuts, and the resulting clips appear as blocks on a visual, horizontal timeline bar at the bottom. You can physically drag those blocks around to reorder your sequence before hitting save.

However, the reality of these community-driven tools highlights why LosslessCut remains the dominant player despite its clunky interface:

**The Maintenance Trap:** Maintaining an app that handles every erratic video container, codec pairing, and changing `ffmpeg` update across macOS, Windows, and Linux is incredibly tedious. While VidCutter has the better timeline layout, its development frequently stalls, and it struggles with stability, bugs, and sluggish file loading compared to LosslessCut.

**The "Good Enough" Plateau:** Because LosslessCut’s UI development model is essentially a one-man show, once the core functionality worked flawlessly, rewriting the entire frontend view architecture to support canvas-style dragging simply wasn't a priority for the developer.

Rolling Your Own

Given how basic the underlying syntax is, it’s a classic example of a project where it's almost easier to build exactly what you want rather than wrestling with someone else's Electron choices.

If you ever get fed up with typing index numbers into LosslessCut, you could easily build a highly tailored developer harness or a small web-based GUI utility for your own machine. A simple local webpage using standard HTML5 drag-and-drop elements to manipulate a list array can pipe the final timestamps over to a lightweight local Node or Python backend that shoots the data straight into native `ffmpeg` commands.

---

[2026-07-07 17:31] User:
yeah electron sucks too, Tauri is where it's at

---

[2026-07-07 17:31] Assistant:
Tauri is exactly the right tool for this architectural pattern. Shifting the heavy multi-process overhead of an Electron shell down to a tiny Rust binary with native WebKit webviews drops the app bundle and idle RAM footprint instantly.

Because this is such a clean stack for media utilities, there are a handful of open-source projects moving this exact direction:

**Katana:** A lightweight video editor built by independent developers using SvelteKit, Tauri, and an FFmpeg backend. It was built for exactly this frustration—to serve as a lightweight alternative to clunky, resource-heavy tools, featuring a fast path that skips re-encoding when performing basic cuts.

**Clypra:** A newer open-source timeline editor built on Tauri v2 and Rust, designed specifically to use hardware-accelerated FFmpeg streams (using `VideoToolbox` natively on macOS) to handle smooth scrubbing without massive Electron lag.  
GitHub

**Tauri Plugin Media Toolkit:** A cross-platform plugin providing simple media processing APIs. Its `trim` operation includes a `preserveQuality: true` flag that acts as a direct abstraction for stream copying (`-c copy`), enabling rapid, loss-free cuts out of the box.  
GitHub
+ 1

Given how straightforward the UI requirements are for a true drag-and-drop cutting tool, piping a quick frontend grid layout into a Tauri IPC command that triggers an asynchronous Rust command-line execution or a `ffmpeg-next` binding is incredibly clean. If you ever decide to spin up a custom utility to escape the Electron constraints, Tauri is the most efficient framework for the job.
