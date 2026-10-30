import json,re,collections
T=json.load(open('turns.json'))
# dedupe (duplicate transcripts after compaction)
seen=set(); U=[]
for t in T:
  k=(t['ts'][:16],t['matt'][:80])
  if k in seen: continue
  seen.add(k); U.append(t)
T=U
def words(s): return len(re.findall(r"\S+",re.sub(r'\]\([^)]*\)',']',s)))   # link targets don't count as words
ASK=re.compile(r"(want me to|should I\b|shall I\b|do you want me|reply 👍|react 👍|👍 (=|to|and I|here|if)|say the word|let me know if you(?:'d)? (?:want|like)|if you(?:'d)? like,? I can|okay to |ok to |your (?:ok|go|go-ahead|approval)|once you (?:confirm|approve|say)|waiting (?:on|for) your|nothing (?:is )?built yet|before I build)",re.I)
APPROVE=re.compile(r"^\s*(👍+|yes+|yep|yeah|ya|y|ok(?:ay)?|sure|go|go ahead|do it|please do|yes,? please|build it|make it|sounds good|perfect|great|do both|both|all of (?:these|them)|all|ship it|proceed|yes do it|yes to all|go for it)[\s.!👍]*$",re.I)
ACT=re.compile(r"\*\*Actions:\*\*(.+)$",re.M)
PATH=re.compile(r"(?<![\(\[/\w])(?:~|/Users/matt)/[\w.@%+~-]+(?:/[\w.@%+~ -]*[\w.@%+~-])*")
stats=collections.Counter(); ex=collections.defaultdict(list)
def add(k,t,s=None):
  stats[k]+=1
  if len(ex[k])<12: ex[k].append((t['ts'][:16],t['role'][:5],t['title'][:28],(s or t['vis'])[:260].replace('\n',' ')))
words_by=collections.defaultdict(list)
for t in T:
  v=t['vis']
  if not v.strip(): stats['no_visible_reply']+=1; continue
  stats['replies']+=1
  w=words(v); words_by[(t['role'],t['surface'])].append(w)
  if w>150: add('over150',t)
  if w>250: stats['over250']+=1
  tail=v[-700:]
  asked=bool(ASK.search(tail)) 
  acts=ACT.findall(v)
  if asked: add('ask',t,tail)
  if acts: stats['actions_line']+=1
  if w>40 and 'Details:' not in v: stats['no_details_gt40']+=1
  if w>40: stats['gt40']+=1
  bare=[p for p in PATH.findall(v) if not re.search(r'\]\('+re.escape(p),v) and '`'+p not in v]
  bare_bt=[p for p in re.findall(r'`((?:~|/Users/matt)/[^`]+)`',v)]
  if bare or bare_bt: add('unlinked_path',t,' | '.join((bare+bare_bt)[:3]))
  if re.search(r'\bopen\s+https?://',v): add('open_url_cmd',t)
  if re.search(r'(?m)^\s*[-*]?\s*\**\s*(You|Me):\**\s',v): add('you_me_prefix',t)
  if re.search(r'terracotta',v,re.I): add('terracotta_word',t)
  nx=t['nxt']
  if asked or acts:
    stats['offers']+=1
    if nx is None: stats['offer_no_next']+=1
    else:
      sents=[]
      for a in acts:
        for part in re.split(r'\s[·|]\s',a):
          if '→' in part: sents.append(part.split('→',1)[1].strip().strip('*').strip())
      clicked=[i for i,s in enumerate(sents) if s and nx.strip().rstrip('.').lower()==s.rstrip('.').lower()]
      if clicked:
        stats['action_click']+=1; stats['action_click_first' if clicked[0]==0 else 'action_click_other']+=1
        add('action_click',t,nx)
      elif APPROVE.match(nx) or re.match(r'^\s*(yes|👍)\b.{0,40}$',nx,re.I):
        stats['bare_approval']+=1; add('bare_approval',t,tail[-200:]+'  ==> '+nx[:60])
      elif re.match(r'^\s*(no|❌|don\'t|nope|skip)\b',nx,re.I): stats['declined']+=1
      else: stats['other_reply']+=1
print(dict(stats))
for k,v in words_by.items():
  v=sorted(v); print(k,'n=',len(v),'median',v[len(v)//2],'p75',v[3*len(v)//4],'>150:',sum(x>150 for x in v))
for k in ('bare_approval','action_click','unlinked_path','open_url_cmd','you_me_prefix','over150'):
  print('\n==',k)
  for e in ex[k][:8]: print('  ',e)
json.dump(T,open('turns_d.json','w'))
