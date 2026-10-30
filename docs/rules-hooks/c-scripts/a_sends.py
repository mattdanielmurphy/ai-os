import pickle,bisect,collections,re
P=pickle.load(open('ev.pkl','rb')); SIZES=P['SIZES']; META=P['META']; L2C=P['LOCAL2CLI']
def size_at(cli,ts):
  if cli not in SIZES: return None
  a,b=SIZES[cli]; i=bisect.bisect_right(a,ts)-1
  return b[i] if i>=0 else 0
out=[]
for r in P['ROWS']:
  for e in r['ev']:
    if e[0]!='tool' or e[2] not in ('SendMessage','mcp__ccd_session_mgmt__send_message'): continue
    to=e[3].get('to') or e[3].get('session_id') or ''
    if not str(to).startswith('local_'): continue
    cli=L2C.get(to)
    s=size_at(cli,e[1]) if cli else None
    out.append((e[1],r['title'][:30],r['role'],to[:14],(META.get(cli,{}).get('title','?'))[:34],s))
print('sends to local threads:',len(out),' resolvable:',sum(1 for o in out if o[5] is not None))
B=collections.Counter()
for o in out:
  s=o[5]
  if s is None: B['unknown']+=1
  elif s>=250000: B['>=250k']+=1
  elif s>=200000: B['200-250k']+=1
  elif s>=150000: B['150-200k']+=1
  else: B['<150k']+=1
print(B)
print('\n>=200k sends:')
for o in sorted(out):
  if o[5] and o[5]>=200000: print(o[0][:16],'|',o[1],'(',o[2],') ->',o[4],'|',o[5]//1000,'k')
byrole=collections.Counter((o[2]) for o in out if o[5] and o[5]>=250000); print(byrole)
print('by day >=250k:',sorted(collections.Counter(o[0][:10] for o in out if o[5] and o[5]>=250000).items()))
print('by day all:',sorted(collections.Counter(o[0][:10] for o in out).items()))
