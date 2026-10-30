import json,glob,os,re,time,collections,bisect,html
cut=time.time()-11*86400
H=os.path.expanduser
# --- session metadata: cli id -> title/local id
META={}
for p in glob.glob(H('~/Library/Application Support/Claude/claude-code-sessions/*/*/local_*.json')):
  try: d=json.load(open(p))
  except: continue
  META[d.get('cliSessionId')]=dict(local=d.get('sessionId'),title=d.get('title') or '',spawn=bool(d.get('spawnedBy') or d.get('parentSessionId')))
LOCAL2CLI={v['local']:k for k,v in META.items()}
def role(t):
  t=t or ''
  if re.match(r'^Coordinator(\s+\d|\s*$)',t): return 'coordinator'
  if re.search(r'\bCoordinator$',t): return 'project-coordinator'
  return 'worker'
def text_of(m):
  c=m.get('content')
  if isinstance(c,str): return c
  if isinstance(c,list): return '\n'.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
  return ''
def is_matt(t):
  s=t.lstrip()
  if not s: return False
  bad=('Another Claude session','<cross-session','<agent-message','<side-sessions-event','<task-notification','<ci-monitor','<system-reminder','Background (from the session','<command-name>','<local-command','Caveat:','This session is being continued','The context-alert plugin','<scheduled-task','<project_claude_message','<bash-input>','<bash-stdout>')
  if s.startswith(bad): return False
  if 'Voice task from voice chat' in s[:120]: return False
  return True
def wake_text(t):
  if '<wake' not in t[:800]: return t
  t=html.unescape(re.sub(r'<[^>]+>',' ',t)); return re.sub(r'\s+',' ',t).strip()
SIZES={}   # cli -> (ts list, tokens list)
ROWS=[]    # per transcript event rows
files=[f for f in glob.glob(H('~/.claude/projects/*/*.jsonl')) if os.path.getmtime(f)>cut]
for f in files:
  sid=os.path.basename(f)[:-6]; ts_l=[];tk_l=[]
  title=META.get(sid,{}).get('title',''); ct=''
  ev=[]
  for line in open(f,errors='ignore'):
    try: d=json.loads(line)
    except: continue
    ty=d.get('type'); ts=d.get('timestamp','')
    if ty=='custom-title': ct=d.get('customTitle') or ct
    if ty=='assistant':
      u=d.get('message',{}).get('usage')
      if u and ts:
        tok=u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)
        if tok>0: ts_l.append(ts); tk_l.append(tok)
      for c in d.get('message',{}).get('content',[]) or []:
        if not isinstance(c,dict): continue
        if c.get('type')=='text' and c['text'].strip(): ev.append(('text',ts,c['text']))
        elif c.get('type')=='tool_use': ev.append(('tool',ts,c['name'],c.get('input',{}),c.get('id')))
    elif ty=='user' and not d.get('isSidechain'):
      m=d.get('message',{}); c=m.get('content')
      if isinstance(c,list) and any(isinstance(x,dict) and x.get('type')=='tool_result' for x in c):
        for x in c:
          if isinstance(x,dict) and x.get('type')=='tool_result':
            r=x.get('content'); r=r if isinstance(r,str) else ' '.join(y.get('text','') for y in (r or []) if isinstance(y,dict))
            ev.append(('result',ts,r[:600],x.get('tool_use_id')))
        continue
      if d.get('isMeta'): continue
      t=text_of(m)
      if t.strip(): ev.append(('user',ts,t))
  SIZES[sid]=(ts_l,tk_l)
  ROWS.append(dict(sid=sid,title=title or ct,role=role(title or ct),ev=ev,dir=os.path.basename(os.path.dirname(f))))
def size_at(cli,ts):
  if cli not in SIZES: return None
  a,b=SIZES[cli]; i=bisect.bisect_right(a,ts)-1
  return b[i] if i>=0 else 0
import pickle
pickle.dump(dict(ROWS=ROWS,SIZES=SIZES,META=META,LOCAL2CLI=LOCAL2CLI),open(H('~/projects/ai-os/tmp/rules-c/ev.pkl'),'wb'))
print(len(ROWS),'transcripts', sum(len(r['ev']) for r in ROWS),'events')
