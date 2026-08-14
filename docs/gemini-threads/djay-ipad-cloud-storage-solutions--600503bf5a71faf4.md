---
title: "Djay iPad Cloud Storage Solutions"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "f9efd5aa-1373-5281-b5b3-88e003c78ff4"
url: ""
---

# Djay iPad Cloud Storage Solutions

> [!NOTE]
> Archived Gemini Thread: [Djay iPad Cloud Storage Solutions]() | Date: 2026-08-13

## User
[2026-07-15 21:46 MDT-6] [context to this point is 0] i've been having fun with djay, but I realized I ought to be mixing in flac and more importantly, I want to get more organized with like, having a specific list of songs and having them categorized like: here's a great drums-only part of a song, or even a song that's entirely just drums only; same for bass, etc.

Although that brings up another fantastic feature of djay I can only take advantage of by actually downloading files rather than using apple music, convenient as it is: Neural mixing. With that, I can basically use any song for anything. Remains to be seen how good it actually sounds with flac. Sometimes it sounds a little weird, but then again, not fair to not assess it with actual flac files.




But still, even with Neural mixing, I think it'd still be smart to extract some great mixing songs from my library and broadly categorize them into drums, lead, bass, etc.

And I'm definitely down to download other stuff that is fantastic for mixing. I want to get better at it.

I'm wondering if I can mix fine with the music hosted on my OneDrive?

I mean on my Mac I know it's possible because I have CloudMounter; the songs would just download on demand. But I'm wondering about the situation on my iPad.

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-15 21:46" -->

---

## Gemini
Using FLAC is a massive upgrade for Neural Mix. When you feed the AI-separation engine heavily compressed files (like AAC or MP3), the algorithm has to work much harder to guess what's what, which is what causes those weird "underwater" phase-y artifacts or tinny high-end sizzles. Feeding it lossless FLAC gives it a completely clean frequency spectrum to slice up, and the difference in stem quality is night and day.

Regarding your iPad and OneDrive setup, here is how the land lies and what your best path forward is.

The OneDrive iPad Situation: The Catch

Can you do it? **Technically yes, but practically, it’s going to be a headache.** Unlike macOS, where CloudMounter or OneDrive’s native Finder integration handles on-demand downloads transparently behind the scenes, iPadOS is much more restrictive.

**No Direct Folder Indexing:** Algoriddim's engineering team has confirmed that third-party cloud providers (like OneDrive and Google Drive) do not allow iOS apps to index or access entire directories recursively through the document picker.

**The "Fully Downloaded" Requirement:** For djay to load and analyze a track, calculate its transient transient beatgrid, and initialize the Neural Mix stems, the file **must** be fully stored locally. If you try to stream a track directly from OneDrive inside djay via the Files tab, the app will frequently hang or fail to load the deck if the file is still sitting in the cloud.  
Algoriddim Support

If you add a folder from OneDrive to djay's **Files** tab, you will have to manually open the iOS Files app, navigate to OneDrive, and tap the cloud download icon on those files to force them onto the iPad's physical storage before you open djay.

The Better Approaches

If you want a seamless transition between your Mac and your iPad without constantly manually downloading files on the tablet, you have three great options:

1. The "Local Syncing" Route (Highly Recommended)

Keep your master FLAC library on your Mac. Since you want to be highly organized with specific folders (drums, bass, leads), you can sync those specific folders directly to the iPad's internal storage:

Connect your iPad to your Mac.

Open Finder, select your iPad in the sidebar, and use the **Files** tab to drag your organized music folders directly into djay's local app sandbox.

Inside djay on the iPad, tap the **Files** tab, hit the `+` icon, select **On My iPad**, and point it to that local folder. This completely avoids cloud lag and ensures flawless offline playback.

2. The OneLibrary Route (Algoriddim's New Standard)

In djay, Algoriddim introduced **OneLibrary**. If you keep your organized FLAC library on a fast, tiny USB-C flash drive or external SSD (formatted as exFAT):  
YouTube

You can plug it into your Mac, build your playlists, set your cue points, and categorize your drum/bass loops.

Safely eject it, plug it directly into the iPad's USB-C port, and load the **USB Library** source.  
Algoriddim Support

Your exact cue points, beatgrids, and organized folders will instantly match, using zero internal iPad storage.

3. The iCloud Drive Alternative

If it *has* to be cloud-based, iCloud Drive plays significantly better with iPadOS background downloading than OneDrive. If you store your curated mixing library in iCloud Drive, you can select "Keep Downloaded" on those folders on your iPad, and iOS will generally keep them locally cached far more reliably than OneDrive's file provider extension.

<!-- /gemini-message -->

---

