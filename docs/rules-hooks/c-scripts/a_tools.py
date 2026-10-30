import pickle,re,collections,json
P=pickle.load(open('ev.pkl','rb'))
C=collections.Counter(); EX=collections.defaultdict(list)
def add(k,r,e,s):
  C[k]+=1
  if len(EX[k])<15: EX[k].append((e[1][:16],r['role'][:5],r['title'][:26],s[:200].replace('\n',' ')))
seen=set()
for r in P['ROWS']:
  ev=r['ev']; res={e[3]:e[2] for e in ev if e[0]=='result'}
  last_cc=None
  for i,e in enumerate(ev):
    if e[0]=='result':
      t=e[2]
      for k,pat in (('deny_input_guard','take-control guard'),('deny_timeout_guard','hang'),('deny_browser_guard','browser pane'),('deny_thread_size','250k')):
        if pat in t and ('Blocked' in t or 'denied' in t.lower() or 'deny' in t.lower()): add(k,r,e,t)
      continue
    if e[0]!='tool': continue
    if e[4] in seen: continue
    seen.add(e[4])
    n,inp=e[2],e[3]
    if n=='Bash':
      cmd=inp.get('command','')
      if 'claude-control ask' in cmd or 'claude-control lock' in cmd: last_cc=e[1]
      for seg in re.split(r'&&|;|\|\||\n|\|',cmd):
        s=seg.strip()
        m=re.match(r'(?:sudo\s+)?rm\s+(.*)',s)
        if m and not re.search(r'(tmp|cache|Cache|node_modules|scratch|worktrees|\.Trash|/private/tmp|__pycache__|\.pyc|DerivedData|\.build|dist|build/|out/)',m.group(1)): add('rm_outside_scratch',r,e,s)
      if re.search(r'(^|[\s;&|(])(npm|npx|pnpm|yarn)\s',cmd) : add('npm_family',r,e,cmd)
      if re.search(r'(?<![\w/])/tmp/',cmd) and '/private/tmp/claude' not in cmd: add('system_tmp',r,e,cmd)
      if re.search(r'gh repo create',cmd) and '--private' not in cmd: add('gh_public',r,e,cmd)
      if re.search(r'(cat|head|tail|less|grep|sed -n|awk)\b[^|;&]*\.env\b',cmd) and not re.search(r'\.env\.(example|sample)',cmd): add('env_read',r,e,cmd)
      if re.search(r'git push[^;&|]*\bmain\b',cmd) and 'crossword' in (cmd+r['dir']).lower(): add('crossword_main_push',r,e,cmd)
    if n in ('Read',) and re.search(r'/\.env(\.|$)',inp.get('file_path','')) and 'example' not in inp.get('file_path',''): add('env_read_tool',r,e,inp.get('file_path',''))
    if n in ('Edit','Write','NotebookEdit','MultiEdit'):
      fp=inp.get('file_path','')
      if re.search(r'/Documents/School/|CMPUT|/labs?/|PHIL|assignment',fp,re.I): add('school_file_edit',r,e,fp)
    if n=='Bash' and re.search(r'(Documents/School|CMPUT[ _]174)',inp.get('command','')) and re.search(r'(cp |mv |>|sed -i|python3 - <<|tee )',inp.get('command','')): add('school_bash_write',r,e,inp.get('command',''))
    if n=='AskUserQuestion':
      qs=inp.get('questions',[])
      quiz=any(re.match(r'^(Q\d|\d)',q.get('header','')) or re.match(r'^\d+\.',q.get('question','')) for q in qs)
      add('ask_menu_quiz' if quiz else 'ask_menu_nonquiz',r,e,json.dumps([q.get('question','') for q in qs])[:150])
      if quiz:
        for q in qs:
          C['quiz_q']+=1
          if not q.get('multiSelect'): C['quiz_q_single']+=1; 
        if any(o.get('description','').strip() for q in qs for o in q.get('options',[])): add('quiz_option_desc',r,e,str([o.get('description') for o in qs[0].get('options',[])])[:120])
    if n.startswith('mcp__computer-use__') and n.split('__')[-1] in ('left_click','type','key','computer_batch','scroll','app_click','app_type','app_key','open_application','left_click_drag','app_batch','double_click','right_click','app_drag','app_scroll','app_focus'):
      C['cu_input']+=1
      if last_cc is None or e[1][:13]>last_cc[:13]: add('cu_input_no_recent_cc',r,e,n)
print(dict(C))
for k,v in EX.items():
  print('\n==',k,C[k])
  for x in v[:10]: print('  ',x)
