import json, collections, re
pc, pid = {}, {}
for l in open('../../tmp/fav_pid.txt'):
    p = l.rstrip('\n').split('\t')
    if len(p) == 3: pid[p[2]] = p[0]; pc[p[2]] = int(p[1] or 0)
by = collections.defaultdict(list)
seen_title = set()
for l in open('../../tmp/scale_ht.jsonl'):
    d = json.loads(l); h = d['ht']
    if not h: continue
    keys = {s['key'].replace('Major','major').replace('Minor','minor') for s in h['sections']}
    if len(keys) != 1: continue
    k = keys.pop(); name = f"{d['title']} — {d['artist']}"
    base = re.sub(r"\s*[\(\[].*?[\)\]]", "", d['title']).lower() + d['artist'].lower()
    if base in seen_title: continue
    seen_title.add(base)
    by[k].append((pc.get(name, 0), name, pid.get(name), h['url']))
for k in by: by[k].sort(key=lambda x: -x[0])
FLAT = {'A#':'Bb','D#':'Eb','G#':'Ab','C#':'C#','F#':'F#'}
def nice(k):
    r, m = k.split(' ', 1); r = FLAT.get(r, r).replace('b','♭') if len(r) > 1 else r
    return r, m
PL = {}
def keypl(title, keys, n=20):
    rows = [x + (k,) for k in keys for x in by.get(k, [])]
    rows.sort(key=lambda x: -x[0]); PL[title] = rows[:n]
keypl("🎹 D major", ["D major"])
keypl("🎹 B♭ major", ["Bb major", "A# major"])
keypl("🎹 A major", ["A major"])
keypl("🎹 E♭ major", ["Eb major", "D# major"])
# modes: D-major family first (B Aeolian, E Dorian, A Mixolydian, G Lydian), then Bb family, then the rest by plays
fam = {"minor": ["B minor", "G minor"], "Dorian": ["E Dorian", "C Dorian"], "Mixolydian": ["A Mixolydian", "F Mixolydian"], "Lydian": ["G Lydian", "Eb Lydian"]}
for mode, label in [("minor", "🎹 Aeolian (natural minor)"), ("Mixolydian", "🎹 Mixolydian"), ("Dorian", "🎹 Dorian"), ("Lydian", "🎹 Lydian")]:
    first = [x + (k,) for k in fam[mode] for x in by.get(k, [])][:8]
    rest = sorted([x + (k,) for k in by if k.endswith(' ' + mode) and k not in fam[mode] for x in by[k]], key=lambda x: -x[0])
    PL[label] = (first + rest)[:22]
json.dump({t: [{"name": r[1], "pid": r[2], "key": " ".join(nice(r[4])).replace("minor", "minor (Aeolian)").replace("major", "major (Ionian)"), "url": r[3]} for r in rows] for t, rows in PL.items()}, open('../../tmp/scale_playlists.json', 'w'), indent=1, ensure_ascii=False)
for t, rows in PL.items():
    print(f"\n{t} ({len(rows)})"); [print(f"  {r[4]:14} {r[1]}  [{r[0]}] {'' if r[2] else 'NO-PID'}") for r in rows]
