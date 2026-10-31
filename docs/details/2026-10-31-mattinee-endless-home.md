# Mattinee endless Home

## 03:05 Endless rows and columns
You asked for every row and the column of rows to feel endless, with as many categories as possible.

- **What shipped:** commit 4d48ba0 on master. About 7,500 rows over about 30,000 titles, on the Mac and VPS servers and the Streamer.
- **How it stays fast:** Home sends 12 rows of 24 titles (about 37 KB compressed, was about 600 KB). Android asks for more only when focus nears the end. Library-free rebuilds take about 2 s, so after the first hour they happen every 6 hours.
- **Catalog growth:** the add-on catalog alone gave only 340 rows and AFI matched 14 of 100. Cinemeta's by-year lists, walked weekly one request at a time and saved as `deep-catalog.json`, raised AFI to 97 of 100 and added director, cast, country and Oscars.
- **Row families:** AFI, Best Picture, Letterboxd, genres, decades, decade + genre, years, year + genre, ratings, hidden gems, cult, famously bad, genre blends, 70 themes, theme + genre or decade, directors, actors, countries, Oscars, title quirks. Fixed top, then the rest reshuffles daily.
- **Rejected:** a live Letterboxd feed. 17 popular public lists were saved once with `bin/letterboxd-bake.ts`; their terms don't favour scraping, so the server never contacts Letterboxd.
- **Tested:** row unit tests; 30 rows down and 40 titles right on the Streamer, no crash, p50 28 ms per frame. iPad's Home is unchanged.
- **Untested or risky:** the feel with a real held remote; older titles may have no good stream, since only known-bad ones are hidden; filters still use the smaller catalog.
- **Undo:** revert 4d48ba0 and redeploy.

## 03:40 Back to the top, and obvious rows first
You wanted a quick way to the top menu from hundreds of rows down, and traditional rows before the wacky ones.

- **What shipped:** commit 648e3ff. Back below the first row focuses Search at the top; Back at the top behaves as before. A quiet "Back: to the top" label shows while you're below the first row.
- **Home button:** it does the same when Mattinee is the TV's home screen, because the app's remote service receives Home only then. Tested by sending the same internal signal, not a physical press.
- **New row order:** the fixed top, then all-time greats, Oscars, AFI, Best Picture, decades newest first, decade movies and shows, genres, best of each genre, gems and cult. 40 more tame rows follow before the wacky families join. Tweak `tv.tameRows`.
- **Undo:** revert 648e3ff, redeploy and publish.
