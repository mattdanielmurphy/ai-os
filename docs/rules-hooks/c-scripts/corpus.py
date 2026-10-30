"""Build a corpus of Matt-authored messages + the agent turn just before each one.
Output: corpus.jsonl rows {ts, sid, title, role, kind, text, prev_reply, prev_tools}"""
import json,glob,os,re,time,sys
cut=time.time()-11*86400
OUT=open(os.path.expanduser('~/projects/ai-os/tmp/rules-c/corpus.jsonl'),'w')
SESS=open(os.path.expanduser('~/projects/ai-os/tmp/rules-c/sessions.jsonl'),'w')
def text_of(m):
  c=m.get('content')
  if isinstance(c,str): return c
  if isinstance(c,list): return '\n'.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
  return ''
def is_tool_result(m):
  c=m.get('content'); return isinstance(c,list) and any(isinstance(x,dict) and x.get('type')=='tool_result' for x in c)
WAKE=re.compile(r'<wake[^>]*>([\s\S]*)',re.I)
def classify(t):
  s=t.lstrip()
  if s.startswith('Another Claude session sent a message') or '<cross-session-message' in s[:300] or '<agent-message' in s[:300]: return 'agent'
  if s.startswith('<side-sessions-event') or s.startswith('<task-notification') or s.startswith('<ci-monitor') or s.startswith('<system-reminder'): return 'system'
  if s.startswith('Background (from the session'): return 'brief'
  if s.startswith('<command-name>') or s.startswith('<local-command'): return 'command'
  if s.startswith('Caveat:'): return 'system'
  if '<wake' in s[:600]: return 'wake'
  return 'matt'
def wake_body(t):
  # project-thread wake envelope: Matt's text usually inside <message ...>...</message> or after the envelope
  m=re.findall(r'<message[^>]*author="(?:user|matt)[^"]*"[^>]*>([\s\S]*?)</message>',t)
  if m: return m[-1]
  m=re.findall(r'<text>([\s\S]*?)</text>',t)
  if m: return m[-1]
  return re.sub(r'<[^>]+>',' ',t)
n=0
for f in glob.glob('*/*.jsonl'):
  if os.path.getmtime(f)<cut: continue
  sid=os.path.basename(f)[:-6]; title=''; agent=''; first=''; prev_reply=''; prev_tools=[]; nturns=0; cwd=os.path.dirname(f)
  rows=[]
  for line in open(f,errors='ignore'):
    try: d=json.loads(line)
    except: continue
    ty=d.get('type')
    if ty=='custom-title': title=d.get('customTitle') or title
    elif ty=='agent-name': agent=d.get('agentName') or agent
    elif ty=='assistant':
      for c in d.get('message',{}).get('content',[]) or []:
        if not isinstance(c,dict): continue
        if c.get('type')=='text' and c['text'].strip(): prev_reply=c['text']
        if c.get('type')=='tool_use':
          inp=c.get('input',{})
          s=inp.get('command') or inp.get('description') or inp.get('to') or inp.get('file_path') or ''
          prev_tools.append(c['name']+': '+str(s)[:120])
    elif ty=='user' and not d.get('isSidechain'):
      m=d.get('message',{})
      if is_tool_result(m) or d.get('isMeta'): continue
      t=text_of(m)
      if not t.strip(): continue
      k=classify(t)
      if not first: first=t[:300]
      body=wake_body(t) if k=='wake' else t
      rows.append(dict(ts=d.get('timestamp','')[:16],sid=sid,kind=k,text=body[:3000],prev_reply=prev_reply[:2500],prev_tools=prev_tools[-12:],ent=d.get('entrypoint','')))
      prev_reply=''; prev_tools=[]; nturns+=1
  role='worker'
  tl=(title+' '+agent).lower()
  if 'coordinator' in tl and not any(w in tl for w in ('glass','slub','project','tv')) : role='coordinator'
  elif 'coordinator' in tl: role='project-coordinator'
  if first.startswith('Background (from the session'): role=role if role!='worker' else 'side-worker'
  for r in rows:
    r['title']=title or agent; r['role']=role; r['dir']=cwd[-40:]
    OUT.write(json.dumps(r)+'\n'); n+=1
  SESS.write(json.dumps(dict(sid=sid,title=title,agent=agent,role=role,dir=cwd,turns=nturns,first=first[:200]))+'\n')
print(n)
