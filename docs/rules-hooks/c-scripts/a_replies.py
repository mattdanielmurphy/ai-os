import pickle,re,json,collections,html
P=pickle.load(open('ev.pkl','rb'))
BAD=('Another Claude session','<cross-session','<agent-message','<side-sessions-event','<task-notification','<ci-monitor','<system-reminder','Background (from the session','<command-name>','<local-command','Caveat:','This session is being continued','The context-alert plugin','<scheduled-task','<project_claude_message','<bash-input>','<bash-stdout>','<bash-stderr>')
def matt_text(t):
  s=t.lstrip()
  if s.startswith(BAD) or 'Voice task from voice chat' in s[:150]: return None
  if '<wake' in s[:800]:
    if '<relay from=' in s: return None
    s=html.unescape(re.sub(r'<[^>]+>',' ',s)); s=re.sub(r'\s+',' ',s).strip()
    if 'Voice task' in s[:60]: return None
  return s
turns=[]
for r in P['ROWS']:
  ev=r['ev']; i=0
  # find Matt-triggered turns
  idx=[k for k,e in enumerate(ev) if e[0]=='user']
  for n,k in enumerate(idx):
    mt=matt_text(ev[k][2])
    if mt is None: continue
    end=idx[n+1] if n+1<len(idx) else len(ev)
    seg=ev[k+1:end]
    texts=[e[2] for e in seg if e[0]=='text']
    thread=[e[3].get('text','') for e in seg if e[0]=='tool' and e[2] in ('mcp__hearthbot__reply','mcp__hearthbot__post_message')]
    tools=[e[2] for e in seg if e[0]=='tool']
    vis=thread if thread else (texts[-1:] if texts else [])
    nxt=None
    if n+1<len(idx): nxt=matt_text(ev[idx[n+1]][2])
    turns.append(dict(sid=r['sid'],title=r['title'],role=r['role'],ts=ev[k][1],matt=mt,vis='\n\n'.join(vis),surface='thread' if thread else 'code',nxt=nxt,tools=tools,interrupted=False))
json.dump(turns,open('turns.json','w'))
print('Matt-triggered turns',len(turns),collections.Counter(t['surface'] for t in turns),collections.Counter(t['role'] for t in turns))
