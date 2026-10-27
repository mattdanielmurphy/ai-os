# Glass TV on iPad: how hard?

## 17:35 Estimate

Matt asked how hard it would be to get Glass TV on his iPad. Question only; nothing was built or changed. The estimate comes from reading the code, not from trying anything.

---

### How Glass TV is built today

- The Mac app (`app/main.swift`, 276 lines) is just a window around a web page. The page (`web/`) is served by a Bun server on the Mac (`src/server.ts`), which holds your files, keys, TMDB, Real-Debrid, rules and X-Ray matching.
- The server listens on `127.0.0.1` only, so nothing else on your network or tailnet can reach it yet.
- Glass Player (`app/player/main.swift`, ~1000 lines) is AppKit + libmpv. It plays MKV/HEVC/anything because mpv does.
- The Android TV port already treats the Mac as the backend behind a `MediaRepository` interface.

---

### The plan: Mac stays the brain, iPad is a client

The server cannot run on iPadOS (Bun, your files, `.env` keys), so the iPad talks to the Mac over Tailscale (already installed). This also means files never need copying to the iPad.

**Step 1 (an afternoon): the web app on the iPad.** Let the server also listen on the Tailscale address, check the page on the iPad screen (its layout is close to the Mac window already, so little resizing), add it to the Home Screen. The commit flow, library and rules work as-is. Weak spot: Safari can't play MKV or many HEVC files, so playback would need the Mac to remux to HLS with ffmpeg on the fly (another half day to a day), or wait for step 2.

**Step 2 (about 3 to 5 days of agent work): a real iPad app.** A small SwiftUI app that shows the same web page, plus a native player built on libmpv through MPVKit (a Swift package that ships mpv for iOS). It plays everything the Mac plays, no transcoding. Glass Player's controls are AppKit and mouse-driven, so they get rewritten for touch (tap, swipe to seek, pinch for full screen); the mpv control logic and progress/credits timing carry over.

**X-Ray on the iPad (about a day more).** On pause, the app grabs the frame and sends it to the Mac, which already does the face matching. Simpler than porting the model to iOS.

---

### Paths I rejected

- **Mac Catalyst:** goes the wrong way (iPad app running on Mac). Your Mac app is AppKit, so it gives nothing here.
- **AVPlayer instead of mpv:** no MKV support, so it would force transcoding on the Mac for most files.
- **Running everything on the iPad:** would need the files on the iPad and a rewrite of the server in Swift. Far more work for a worse result.

---

### Installing without the App Store

You have a paid Apple developer account: your existing iOS provisioning profiles (Mindful Browser) last a full year, which free accounts can't do (they expire after 7 days). So installing is easy: build from Xcode straight to the iPad, or use TestFlight for easy updates. No App Store review needed.

---

### Untested / risks

- Nothing was built or run. Day estimates are guesses from code size.
- MPVKit on iPadOS was not tried on your machine; it is the main unknown.
- Opening the server to the tailnet needs a check that only your devices can reach it (Tailscale does this by default).
- Other threads are editing glass-tv right now; any build should start after they land.

## 17:50 Correction: iPad, not iPhone

Matt asked about iPad; the first reply said iPhone throughout. The plan is the same. The iPad is a bit easier: its screen is close to the Mac window, so the web layout needs little change, and touch controls have more room. Estimates stay: quick version an afternoon, full app 3 to 5 days, X-Ray about a day more. The same app can also run on iPhone later at little extra cost.
