import json,re
R=json.load(open('corpus2.json'))
M=[r for r in R if r['kind']=='matt']
LEX=re.compile(r"""\b(again|still|I told you|I said|I asked|as I said|should have|should've|shouldn't|why did you|why didn't you|why are you|why do you|why would you|why is it|why wait|you didn't|you did not|you forgot|you never|you missed|you keep|keep (doing|asking|getting)|never|always|rule|from now on|didn't I|how many times|ffs|wtf|fuck|not what I|I meant|that's not|wrong|confus|doesn't make sense|don't understand|I shouldn't have to|just do it|you can do|do it yourself|yourself|clickable|link|too long|wall of|concise|shorter|ugh|seriously|come on|instead of asking|without asking|stop asking|don't ask|didn't ask|unasked|who told you|broke|broken|lost|forgot|where is|where's|you were supposed|supposed to)\b""",re.I)
C=[r for r in M if LEX.search(r['text']) and len(r['text'])<4000]
json.dump(C,open('cands.json','w'))
print(len(M),len(C))
