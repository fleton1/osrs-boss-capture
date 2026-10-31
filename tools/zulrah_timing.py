#!/usr/bin/env python3
# Reads RuneLite Boss Capture files (osrs-boss-capture plugin, JSONL, optionally gzipped).
# Usage: tools/zulrah_timing.py data/captures/zulrah
import gzip,os
def opn(f): return gzip.open(f,'rt') if f.endswith('.gz') else open(f)
import json,glob,sys,collections
C=collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(sys.argv[1]+'/*.jsonl*')):
    zid=None; seq=[]  # (tick, kind)
    pending=None
    for l in opn(f):
        d=json.loads(l); t=d['type']; tk=d['tick']
        if t=='npc_spawn' and d['name']=='Zulrah': zid=d['index']
        if t=='anim' and d.get('index')==zid and d['anim']!=-1: seq.append([tk,d['anim'],None])
        if t=='projectile' and d['to'].get('actor')!='npc' and d['id'] in (1044,1045,1046,1047):
            for s in reversed(seq):
                if s[1]==5069: 
                    if s[2] is None: s[2]=d['id']; C['spit->proj'][tk-s[0]]+=1; C['flight%d'%d['id']][d['endCycle']-d['startCycle']]+=1
                    break
        if t=='hitsplat' and d['actor']=='me' and seq and seq[-1][1] in (5806,5807): C['tail->hit'][tk-seq[-1][0]]+=1
        if t=='death' and d.get('index')==zid: seq.append([tk,'DEATH',None])
    for a,b in zip(seq,seq[1:]):
        ka=a[1] if a[1]!=5069 else 'spit%s'%a[2]; kb=b[1] if b[1]!=5069 else 'spit'
        C['%s->%s'%(ka,kb)][b[0]-a[0]]+=1
for k,v in sorted(C.items(),key=lambda x:str(x[0])): print(k,dict(sorted(v.items())))
