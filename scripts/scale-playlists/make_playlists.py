import json, subprocess
P = json.load(open('../../tmp/scale_playlists.json'))
for t in P:
    for x in P[t]: x["key"] = x["key"].replace("A♭ minor", "G♯ minor")
DESC = {
 "🎹 D major": "D major (Ionian): D E F♯ G A B C♯. Your favourites, keys from Hooktheory transcriptions. Each song's Comment shows its scale.",
 "🎹 B♭ major": "B♭ major (Ionian): B♭ C D E♭ F G A. Your favourites, keys from Hooktheory transcriptions.",
 "🎹 A major": "A major (Ionian): A B C♯ D E F♯ G♯. Next pair after D/B♭. Keys from Hooktheory.",
 "🎹 E♭ major": "E♭ major (Ionian): E♭ F G A♭ B♭ C D. Next pair after D/B♭. Keys from Hooktheory.",
 "🎹 Aeolian (natural minor)": "Natural minor: 1 2 ♭3 4 5 ♭6 ♭7. B minor songs first (same notes as D major). Root in each song's Comment.",
 "🎹 Mixolydian": "Major with a ♭7: 1 2 3 4 5 6 ♭7. A Mixolydian first (same notes as D major). Root in each song's Comment.",
 "🎹 Dorian": "Minor with a natural 6: 1 2 ♭3 4 5 6 ♭7. Classics first, then E Dorian (same notes as D major). Root in each song's Comment.",
 "🎹 Lydian": "Major with a ♯4: 1 2 3 ♯4 5 6 7. G Lydian first (same notes as D major). Root in each song's Comment.",
}
ORDER = ["🎹 D major", "🎹 B♭ major", "🎹 Aeolian (natural minor)", "🎹 Mixolydian", "🎹 Dorian", "🎹 Lydian", "🎹 A major", "🎹 E♭ major"]
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
lines = ['tell application "Music"',
 'if not (exists folder playlist "🎹 Scale Practice") then make new folder playlist with properties {name:"🎹 Scale Practice"}',
 'set f to folder playlist "🎹 Scale Practice"']
for t in ORDER:
    lines += [f'if exists user playlist {q(t)} then delete tracks of user playlist {q(t)}',
              f'if not (exists user playlist {q(t)}) then make new user playlist at f with properties {{name:{q(t)}}}',
              f'set p to user playlist {q(t)}',
              f'set description of p to {q(DESC[t])}']
    for s in P[t]:
        note = "Scale: " + s["key"]
        lines += ['try', f'set tr to (first track of library playlist 1 whose persistent ID is {q(s["pid"])})',
                  f'duplicate tr to p',
                  'try',
                  f'set c to comment of tr',
                  f'if c does not contain "Scale:" then',
                  f'if c is "" then', f'set comment of tr to {q(note)}', 'else', f'set comment of tr to c & " · " & {q(note)}', 'end if',
                  'end if',
                  'end try', 'end try']
lines += ['end tell']
open('../../tmp/scale_make.applescript', 'w').write("\n".join(lines))
json.dump(P, open('../../tmp/scale_playlists.json', 'w'), indent=1, ensure_ascii=False)
print(sum(len(P[t]) for t in ORDER))
