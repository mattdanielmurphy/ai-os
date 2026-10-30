import json,re,html,collections
R=[json.loads(l) for l in open('corpus.jsonl')]
S={s['sid']:s for s in map(json.loads,open('sessions.jsonl'))}
def role(title):
  t=(title or '').strip()
  if re.match(r'^Coordinator(\s+\d|\s*$)',t): return 'coordinator'
  if re.search(r'\bCoordinator$',t): return 'project-coordinator'
  return 'worker'
out=[]
for r in R:
  t=html.unescape(r['text']); t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t).strip()
  k=r['kind']
  if k in('matt','wake'):
    if '<relay from=' in t or t.startswith('<project_claude_message'): k='relay'
    elif 'Voice task from voice chat' in t[:80]: k='voice-task'
    elif t.startswith('From ') and '<pasted_content' in t[:200]: k='paste'
    elif re.match(r'^(Another Claude session|<cross-session)',t): k='agent'
    else: k='matt'
  r['kind']=k; r['text']=t; r['role']=role(r['title'])
  if r['role']=='worker' and S.get(r['sid'],{}).get('first','').startswith('Background (from'): r['role']='side-worker'
  out.append(r)
json.dump(out,open('corpus2.json','w'))
M=[r for r in out if r['kind']=='matt']
print(collections.Counter(r['kind'] for r in out))
print(collections.Counter(r['role'] for r in M))
print('days',collections.Counter(r['ts'][:10] for r in M).most_common())
