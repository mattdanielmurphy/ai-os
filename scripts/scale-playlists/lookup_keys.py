import json, re, sys, importlib.machinery, importlib.util
from concurrent.futures import ThreadPoolExecutor
loader = importlib.machinery.SourceFileLoader("sk", sys.argv[3])
spec = importlib.util.spec_from_loader("sk", loader); sk = importlib.util.module_from_spec(spec); loader.exec_module(sk)
done = set()
try:
    for l in open(sys.argv[2]): d = json.loads(l); done.add(d["title"] + "|" + d["artist"])
except FileNotFoundError: pass
items = []
for line in open(sys.argv[1]):
    line = line.strip()
    if " — " not in line: continue
    t, a = line.rsplit(" — ", 1)
    if t + "|" + a not in done: items.append((t, a)); done.add(t + "|" + a)
def work(ta):
    t, a = ta
    lt = re.sub(r"\s*[\(\[].*?[\)\]]", "", t).strip() or t
    try: r = sk.hooktheory(a.split(" & ")[0].split(", ")[0], lt)
    except Exception as e: r = {"error": str(e)}
    return {"title": t, "artist": a, "ht": r}
out = open(sys.argv[2], "a")
with ThreadPoolExecutor(6) as ex:
    for d in ex.map(work, items):
        out.write(json.dumps(d) + "\n"); out.flush()
