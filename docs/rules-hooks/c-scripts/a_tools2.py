import pickle,re,collections,json
P=pickle.load(open('ev.pkl','rb'))
C=collections.Counter(); EX=collections.defaultdict(list)
def add(k,r,ts,s):
  C[k]+=1
  if len(EX[k])<14: EX[k].append((ts[:16],r['role'][:5],r['title'][:28],s[:230].replace('\n',' ')))
seen=set(); seenr=set()
QUIZRULE='2026-10-21T01:30'
for r in P['ROWS']:
  ev=r['ev']
  for e in ev:
    if e[0]=='result':
      if e[3] in seenr: continue
      seenr.add(e[3]); t=e[2]
      if 'Blocked by the take-control guard' in t: add('deny_input',r,e[1],t[60:200])
      elif 'Blocked by the hang guard' in t: add('deny_hang',r,e[1],t[25:140])
      elif 'Blocked: local/reel/media pages' in t: add('deny_browser',r,e[1],'')
      continue
    if e[0]!='tool' or e[4] in seen: continue
    seen.add(e[4]); n,inp=e[2],e[3]
    if n=='Bash':
      cmd=inp.get('command','')
      if re.search(r'(?:^|[\s"\'=(:])/tmp/',cmd): add('system_tmp',r,e[1],re.search(r'.{0,60}(?:^|[\s"\'=(:])/tmp/.{0,60}',cmd).group(0))
      if re.search(r'(?:^|[;&|(]\s*|\s)(?:cat|head|tail|less|more|bat|grep|rg|sed -n|awk|source|\.)\s+[^|;&>]*?(?:^|[\s/"\'])\.env(?:\.local|\.production)?(?:["\'\s;|&]|$)',cmd) and 'aios-env' not in cmd:
        add('env_read',r,e[1],cmd[:200])
    if n=='Read' and re.search(r'/\.env(\.[a-z]+)?$',inp.get('file_path','')) and not inp.get('file_path','').endswith(('.example','.sample')): add('env_read_tool',r,e[1],inp.get('file_path',''))
    if n=='AskUserQuestion':
      qs=inp.get('questions',[])
      quiz=any(re.match(r'^(Q\d|\d)',q.get('header','')) or re.match(r'^\d+\.',q.get('question','')) for q in qs) or 'Track' in json.dumps(qs) or 'quiz' in r['title'].lower() or 'study' in r['title'].lower() or 'logic' in r['title'].lower()
      after=e[1]>=QUIZRULE
      if quiz:
        for q in qs:
          C['quiz_q_'+('after' if after else 'before')]+=1
          if not q.get('multiSelect'): C['quiz_single_'+('after' if after else 'before')]+=1
      else: add('menu_nonquiz_'+('after' if after else 'before'),r,e[1],json.dumps([q.get('question','') for q in qs])[:160])
    if n=='mcp__hearthbot__no_reply_needed': C['no_reply_needed']+=1
print(dict(C))
for k,v in EX.items():
  print('\n==',k,C[k])
  for x in v[:14]: print('  ',x)
