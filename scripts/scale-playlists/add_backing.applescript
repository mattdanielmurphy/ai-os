-- Run after adding these albums to the library (music.apple.com/ca/album/<id>):
-- 1268259828 Modal Backing Tracks - D, 1278264129 Modal Backing Tracks - A,
-- 1451738265 Blues Backing Tracks, 1213701636 30 Greatest Scott Joplin Ragtime Piano Pieces
-- Builds "🎹 Blues & Ragtime" and "🎹 Modal backing (D & A)" in the 🎹 Scale Practice folder.
-- Keys: blues by track title; rags from Hooktheory (A strain key, trio key).
on addTo(plName, albumName, trackName, note)
	tell application "Music"
		set r to (every track of library playlist 1 whose album is albumName and name starts with trackName)
		if (count r) = 0 then return 0
		set tr to item 1 of r
		duplicate tr to user playlist plName
		try
			if comment of tr does not contain "Scale:" then set comment of tr to "Scale: " & note
		end try
		return 1
	end tell
end addTo

tell application "Music"
	set f to folder playlist "🎹 Scale Practice"
	repeat with n in {"🎹 Blues & Ragtime", "🎹 Modal backing (D & A)"}
		if exists user playlist n then
			delete tracks of user playlist n
		else
			make new user playlist at f with properties {name:n}
		end if
	end repeat
	set b to user playlist "🎹 Blues & Ragtime"
	set m to user playlist "🎹 Modal backing (D & A)"
	set description of b to "12-bar blues jams in your keys (D, B♭, A, E♭) plus Joplin rags in B♭/E♭. Blues: try the major pentatonic, then the blues scale. Rags change key at the trio (Comment shows both)."
	set description of m to "One chord vamp per mode. D set = the 7 modes of D major's notes; A set = A major's. Play the same white/black keys, hear a new home note."
end tell
set n to 0
set BB to "Blues Backing Tracks"
repeat with x in {{"D - Shuffle", "D blues (12-bar, D7 G7 A7)"}, {"D - Slow", "D blues (12-bar, slow)"}, {"A# (Gb) - Shuffle", "B♭ blues (12-bar, B♭7 E♭7 F7)"}, {"A# (Gb) - Slow", "B♭ blues (12-bar, slow)"}, {"A - Shuffle", "A blues (12-bar, A7 D7 E7)"}, {"A - Sweet Home", "A blues (Chicago shuffle)"}, {"D# (Eb) - Shuffle", "E♭ blues (12-bar, E♭7 A♭7 B♭7)"}, {"D# (Eb) - Slow", "E♭ blues (12-bar, slow)"}}
	set n to n + (addTo("🎹 Blues & Ragtime", BB, item 1 of x, item 2 of x))
end repeat
set JA to "30 Greatest Scott Joplin Ragtime Piano Pieces"
repeat with x in {{"Pineapple Rag", "B♭ major → E♭ major (trio)"}, {"Fig Leaf Rag", "B♭ major → E♭ major (trio)"}, {"Searchlight Rag", "B♭ major → E♭ major (trio)"}, {"Sunflower Slow Drag", "B♭ major → E♭ major (trio)"}, {"Sugar Cane", "B♭ major, E♭ major middle"}, {"Peacherine Rag", "E♭ major → A♭ major (trio)"}, {"The Entertainer", "C major (F major strain)"}, {"Maple Leaf Rag", "A♭ major → D♭ major (trio)"}}
	set n to n + (addTo("🎹 Blues & Ragtime", JA, item 1 of x, item 2 of x))
end repeat
repeat with x in {{"Modal Backing Tracks - D", "D"}, {"Modal Backing Tracks - A", "A"}}
	repeat with md in {{"Ionian", " Ionian (major)"}, {"Aeolian", " Aeolian (natural minor)"}, {"Mixolydian", " Mixolydian"}, {"Dorian", " Dorian"}, {"Lydian", " Lydian"}, {"Phrygian", " Phrygian"}, {"Modal Progression", " all modes"}}
		tell application "Music" to set r to (every track of library playlist 1 whose album is (item 1 of x) and name starts with (item 1 of md))
		if (count r) > 0 then
			-- note names the root from the track title, e.g. "Dorian Backing Track - E min 7 - D"
			tell application "Music" to set t to name of item 1 of r
			set n to n + (addTo("🎹 Modal backing (D & A)", item 1 of x, item 1 of md, t & " → notes of " & item 2 of x & " major"))
		end if
	end repeat
end repeat
return "added " & n & " of 30"
