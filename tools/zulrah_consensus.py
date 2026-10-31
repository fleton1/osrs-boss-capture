#!/usr/bin/env python3
# Reads RuneLite Boss Capture files (osrs-boss-capture plugin, JSONL, optionally gzipped).
# Usage: tools/zulrah_consensus.py data/captures/zulrah
import gzip,os
def opn(f): return gzip.open(f,'rt') if f.endswith('.gz') else open(f)
import sys,glob,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from phases import fights,fmt
CH={1:'GM RM BM GS RM BW GS BS GW RM GM',2:'GM RM BM GW BS RM GE BS GW RM GM',
    3:'GM GE RM BW GS BE GM GW BM GE BM GM',4:'GM BE GS BW RM GE GS BW GM BM GE BM GM'}
CH={k:v.split() for k,v in CH.items()}
obs=collections.defaultdict(list)
for f in sorted(glob.glob(sys.argv[1]+'/*.jsonl*')):
    ph=[p for p in fights(f) if p['acts'] or 'dead' in p]
    keys=[''.join(p['k']) for p in ph]
    i=0; rot=None; pos=0
    while i<len(ph):
        k=keys[i]
        if rot is None:
            cands=[r for r,c in CH.items() if all(pos+j>=len(c) or i+j>=len(keys) or keys[i+j]==c[pos+j] for j in range(4))]
            if len(cands)!=1:  # new fight boundary? restart at opening
                if k=='GM': pos=0
                cands=[r for r,c in CH.items() if all(pos+j>=len(c) or i+j>=len(keys) or keys[i+j]==c[pos+j] for j in range(5))]
            if len(cands)!=1: print('??',f,i,keys[i:i+5],cands); i+=1; continue
            rot=cands[0]
        if keys[i]!=CH[rot][pos]:
            # a new fight in the same file
            if keys[i]=='GM': rot=None; pos=0; continue
            print('mismatch',f,i,rot,pos,keys[i]); rot=None; pos=0; i+=1; continue
        s=fmt(ph[i]); full='dead' not in ph[i] and not (i+1<len(ph) and ph[i+1]['start']-ph[i]['start']>60)
        obs[(rot,pos)].append((s, 'full' if 'dead' not in ph[i] else 'DEAD', os.path.basename(f)))
        if 'dead' in ph[i]: rot=None; pos=0; i+=1; continue
        pos+=1; i+=1
        if pos==len(CH[rot]): rot=None; pos=1
for (r,p),v in sorted(obs.items()):
    print('R%d.%d %s'%(r,p+1,CH[r][p]))
    for s,c in collections.Counter((a,b) for a,b,_ in v).most_common(): print('     %dx %s %s'%(c, b if (b:=s[1])=='DEAD' else '', s[0]))
