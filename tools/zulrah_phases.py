#!/usr/bin/env python3
# Reads RuneLite Boss Capture files (osrs-boss-capture plugin, JSONL, optionally gzipped).
# Usage: tools/zulrah_phases.py data/captures/zulrah
import gzip,os
def opn(f): return gzip.open(f,'rt') if f.endswith('.gz') else open(f)
import json,sys,glob,collections
FORM={2042:'G',2043:'R',2044:'B'}
SPOT={(2268,3075):'M',(2278,3073):'E',(2258,3073):'W',(2268,3064):'S'}
def fights(f):
    ev=[json.loads(l) for l in opn(f)]
    zid=None; phases=[]; cur=None; deaths=[]
    for d in ev:
        t=d['type']; tk=d['tick']
        if t=='npc_spawn' and d['name']=='Zulrah':
            zid=d['index']
        if t=='tick':
            for n in d['npcs']:
                if n['index']==zid:
                    k=(FORM.get(n['id'],n['id']),SPOT.get((n['x'],n['y']),(n['x'],n['y'])))
                    if cur is None or (k!=cur['k']):
                        cur={'k':k,'start':tk,'acts':[],'snk':[]}; phases.append(cur)
        if cur is None: continue
        if t=='projectile' and d['from'] and d['to'].get('actor')!='npc':
            p=d['id']; to=(d['to']['x'],d['to']['y'])
            if p==1044: cur['acts'].append(('r',tk))
            elif p==1046: cur['acts'].append(('m',tk))
            elif p==1045: cur['acts'].append(('c',tk,(to[0]+1,to[1]+1),d['endCycle']-d['startCycle']))
            elif p==1047: cur['acts'].append(('e',tk,to))
        if t=='anim' and d.get('index')==zid and d['anim'] in (5806,5807):
            cur['acts'].append(('t',tk))
        if t=='npc_spawn' and d['name']=='Snakeling': cur['snk'].append(d['id'])
        if t=='death' and d.get('index')==zid: cur['dead']=tk
    return phases
def fmt(ph):
    out=[]; acts=ph['acts']; i=0
    while i<len(acts):
        a=acts[i]
        if a[0]=='c':
            if i+1<len(acts) and acts[i+1][0]=='c' and acts[i+1][1]==a[1]:
                b=acts[i+1]; x,y=(a,b) if a[3]<=b[3] else (b,a)
                out.append('C%d,%d+%d,%d'%(x[2]+y[2])); i+=2; continue
            out.append('c%d,%d'%a[2])
        elif a[0]=='e': out.append('E%d,%d'%a[2])
        else: out.append(a[0])
        i+=1
    # compress runs of r/m/t
    s=[]; 
    for o in out:
        if s and len(o)==1 and s[-1][0]==o: s[-1][1]+=1
        else: s.append([o,1])
    return ' '.join(o if n==1 else '%s%d'%(o,n) for o,n in s)
if __name__=='__main__':
    for f in sorted(glob.glob(sys.argv[1]+'/*.jsonl*')):
        print('==',os.path.basename(f))
        for ph in fights(f):
            if not ph['acts'] and 'dead' not in ph: continue
            print('  %3d %s%s %s %s %s'%(ph['start'],*ph['k'],fmt(ph),'snk'+''.join(str(s-2044) for s in ph['snk']) if ph['snk'] else '', 'DEAD@%d'%ph['dead'] if 'dead' in ph else ''))
