#!/usr/bin/env python3
# Reads the RuneLite Boss Capture files of Vorkath (osrs-boss-capture plugin, JSONL, gzipped) and prints the facts the
# Vorkath fight is checked against: the ordered attacks, the gaps, the specials (rapid fire and the zombified spawn), the
# spawn's walk and lifetime, the wake-up and the kill.  Stdlib only; run with python3 -I.
# Usage: python3 -I tools/vorkath_measure.py data/captures/vorkath/*.jsonl.gz
import collections
import gzip
import json
import sys

VORKATH_IDS = (8059, 8061)
SPAWN_ID = 8063
ACID = 32000
ANIM_RAPID = 7957
ANIM_BREATH = 7960          # the deadly fireball (1481) and the icy breath (1484)
ANIM_MELEE = 7948
ANIM_STANDARD = 7952        # ranged (1477), magic (1479) and the three dragonfires (1470, 393, 395, 1471)
PROJ_RANGED, PROJ_MAGIC, PROJ_DEADLY, PROJ_ICE = 1477, 1479, 1481, 1484
PROJ_BARRAGE, PROJ_BURST = 1482, 1483
DRAGONFIRE = (1470, 393, 395, 1471)
KNOWN = (1477, 1479, 1481, 1484, 1470, 393, 395, 1471)
LABEL = {ANIM_MELEE: 'M', PROJ_RANGED: 'r', PROJ_MAGIC: 'm', PROJ_DEADLY: 'D'}


def load(path):
    with gzip.open(path, 'rt') as fh:
        return [json.loads(line) for line in fh]


def chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def fight(path):
    recs = load(path)
    out = collections.OrderedDict()
    vork = next(d['index'] for d in recs if d['type'] == 'npc_spawn' and d.get('name') == 'Vorkath' and d['id'] == 8061)
    me = {}
    for d in recs:
        if d['type'] == 'tick':
            me[d['tick']] = (d['player']['x'], d['player']['y'])
    chats = [d for d in recs if d['type'] == 'chat']
    hits_me = [d for d in recs if d['type'] == 'hitsplat' and d['actor'] == 'me']
    hits_v = [d for d in recs if d['type'] == 'hitsplat' and d['actor'] == 'npc' and d.get('index') == vork]
    projs = [d for d in recs if d['type'] == 'projectile' and d['from']['x'] in range(2262, 2285)
             and d['from']['y'] in range(4050, 4080)]
    vanim = [d for d in recs if d['type'] == 'anim' and d.get('actor') == 'npc' and d.get('index') == vork and d['anim'] != -1]
    acid_on = [d['tick'] for d in recs if d['type'] == 'object_spawn' and d['id'] == ACID]
    acid_off = [d['tick'] for d in recs if d['type'] == 'object_despawn' and d['id'] == ACID]
    spawns = [d for d in recs if d['type'] == 'npc_spawn' and d['id'] == SPAWN_ID]
    spawn_end = {d['index']: d for d in recs if d['type'] in ('death', 'npc_despawn') and d.get('npcId', d.get('id')) == SPAWN_ID}
    spawn_pos = collections.defaultdict(list)
    for d in recs:
        if d['type'] == 'npc_spawn' and d['id'] == SPAWN_ID or d['type'] == 'npc_despawn' and d['id'] == SPAWN_ID:
            pass
    for d in recs:
        if d['type'] == 'tick':
            for n in d['npcs']:
                if n['id'] == SPAWN_ID:
                    spawn_pos[n['index']].append((d['tick'], n['x'], n['y']))

    def chat_after(t, lo=0, hi=6, needle=()):
        return [c['text'] for c in chats if t + lo <= c['tick'] <= t + hi and any(s in c['text'] for s in needle)]

    # 1. attacks: each anim start of Vorkath, with its projectile and a label from the chat that follows
    attacks = []
    for a in vanim:
        t = a['tick']
        pj = [p for p in projs if p['tick'] in (t, t + 1, t + 2) and p['id'] in KNOWN]
        pid = pj[0]['id'] if pj else None
        if a['anim'] == ANIM_RAPID:
            kind = 'RAPID'
        elif a['anim'] == ANIM_BREATH and pid == PROJ_ICE:
            kind = 'SPAWN'
        elif a['anim'] == ANIM_BREATH and pid == PROJ_DEADLY:
            kind = 'D'
        elif a['anim'] == ANIM_MELEE:
            kind = 'M'
        elif a['anim'] == ANIM_STANDARD and pid in (PROJ_RANGED, PROJ_MAGIC):
            kind = LABEL[pid]
        elif a['anim'] == ANIM_STANDARD and pid in DRAGONFIRE:
            if chat_after(t, needle=('venomous',)):
                kind = 'V'
            elif chat_after(t, needle=('prayers have been disabled',)):
                kind = 'C'
            elif chat_after(t, needle=('fiery',)):
                kind = 'F'
            else:
                kind = 'F?%d' % pid
        else:
            kind = 'A%d/%s' % (a['anim'], pid)
        attacks.append((t, a['anim'], pid, kind))
    out['attacks'] = attacks
    specials = [x for x in attacks if x[3] in ('RAPID', 'SPAWN')]
    standards = [x for x in attacks if x[3] not in ('RAPID', 'SPAWN')]

    # 2. the sequence of swings, standards as letters and specials in brackets
    seq = []
    for x in attacks:
        seq.append('[%s]' % x[3] if x[3] in ('RAPID', 'SPAWN') else x[3])
    out['sequence'] = ' '.join('%d:%s' % (x[0], x[3]) for x in attacks)

    # 3. gaps between consecutive standards (both inside a block and across a special)
    gaps = collections.Counter()
    for (t0, *_, k0), (t1, *_, k1) in zip(standards, standards[1:]):
        gaps[t1 - t0] += 1
    out['standard_gaps'] = dict(sorted(gaps.items()))
    blocks = []
    run = 0
    for x in attacks:
        if x[3] in ('RAPID', 'SPAWN'):
            blocks.append((run, x[3], x[0]))
            run = 0
        else:
            run += 1
    out['standards_before_special'] = blocks

    # 4. rapid fire: start, acid on and off, pools, barrage shots and the player's hits
    rapid = []
    for t, *_ , k in attacks:
        if k != 'RAPID':
            continue
        ons = [u for u in acid_on if t <= u <= t + 6]
        offs = [u for u in acid_off if u > (ons[0] if ons else t)]
        barrage = [p['tick'] for p in projs if p['id'] == PROJ_BARRAGE and p['tick'] >= t]
        burst = [p for p in projs if p['id'] == PROJ_BURST and p['tick'] in range(t, t + 4)]
        end = offs[0] if offs else None
        shots = [p for p in barrage if end is None or p <= end]
        hit_here = [h['amount'] for h in hits_me if ons and ons[0] <= h['tick'] <= (end or 10**9) + 2 and h['amount'] > 0]
        rapid.append(dict(start=t, acid_on=ons[0] if ons else None, acid_off=end, length=(end - ons[0]) if ons and end else None,
                          pools=len(ons), burst_projectiles=len(burst),
                          barrage_first=shots[0] if shots else None, barrage_last=shots[-1] if shots else None,
                          player_hits=hit_here))
    out['rapid'] = rapid
    # the barrage's shots: did the player stand on the aimed tile, and was there a hit in the next three ticks?
    shots = []
    for p in projs:
        if p['id'] != PROJ_BARRAGE:
            continue
        t = p['tick']
        tgt = (p['to']['x'], p['to']['y'])
        here = me.get(t)
        nxt = me.get(t + 1)
        hit = sorted(h['amount'] for h in hits_me if t <= h['tick'] <= t + 3 and h['amount'] > 0)
        shots.append((t, tgt, here == tgt if here else None, nxt == tgt if nxt else None, hit))
    out['barrage'] = shots

    # 5. the zombified spawn: breath, spawn tile, walk, end, explosion damage and freeze messages
    spawn_rows = []
    for t, *_, k in attacks:
        if k != 'SPAWN':
            continue
        freeze = [c['tick'] for c in chats if t <= c['tick'] <= t + 4 and 'frozen' in c['text']]
        s = [d for d in spawns if t <= d['tick'] <= t + 6]
        if not s:
            spawn_rows.append(dict(breath=t, freeze=freeze, note='no spawn'))
            continue
        s = s[0]
        idx = s['index']
        pos = spawn_pos.get(idx, [])
        land = (s['tick'], s['x'], s['y'])
        at_land = me.get(s['tick'], None)
        dist = chebyshev((s['x'], s['y']), at_land) if at_land else None
        end_ev = spawn_end.get(idx)
        ended = None
        if end_ev:
            ended = dict(tick=end_ev['tick'], how='killed' if end_ev['type'] == 'death' or end_ev.get('dead') else 'burst')
        booms = [h['amount'] for h in hits_me if ended and ended['tick'] <= h['tick'] <= ended['tick'] + 2 and h['amount'] > 0]
        unfreeze = [c['tick'] for c in chats if t <= c['tick'] <= t + 300 and ('unfreezing' in c['text'] or 'unfrozen' in c['text'])][:1]
        walk = [(p[0], chebyshev((p[1], p[2]), me.get(p[0], (p[1], p[2])))) for p in pos]
        spawn_rows.append(dict(breath=t, freeze=freeze[:1], land=s['tick'], land_tile=(s['x'], s['y']),
                               land_dist=dist, end=ended, damage=booms, unfreeze=unfreeze,
                               life=(ended['tick'] - s['tick']) if ended else None,
                               walk_dist=walk[:12]))
    out['spawn'] = spawn_rows

    # 6. wake-up and kill
    poke = next((d['tick'] for d in recs if d['type'] == 'interact' and d.get('target', {}).get('index') == vork), None)
    death = next((d['tick'] for d in recs if d['type'] == 'death' and d.get('index') == vork), None)
    kill_msg = next((c['tick'] for c in chats if 'kill count' in c['text']), None)
    loot = [c['text'] for c in chats if 'Valuable drop' in c['text'] or 'received a drop' in c['text']]
    sleep = [d['tick'] for d in recs if d['type'] == 'npc_spawn' and d['id'] == 8059]
    change = [(d['tick'], d['to']) for d in recs if d['type'] == 'npc_change' and d['index'] == vork or d['type'] == 'npc_change' and d['from'] in VORKATH_IDS]
    out['wake'] = dict(poke=poke, first_attack=attacks[0][0] if attacks else None)
    out['kill'] = dict(death=death, kill_message=kill_msg, loot_lines=len(loot), sleeper=sleep[:1], changes=change[:2],
                       duration=next((c['text'] for c in chats if 'Fight duration' in c['text']), None))
    out['messages'] = collections.Counter(c['text'] for c in chats if c['chatType'] != 'SPAM' and 'Vorkath' not in c['text'] and 'frozen' not in c['text'])
    out['spam'] = collections.Counter(c['text'] for c in chats if c['chatType'] == 'SPAM' and 'dragon' in c['text'])
    return out


def show(path, o):
    print('==', path.rsplit('/', 1)[-1])
    print('wake: poke %s, first attack %s' % (o['wake']['poke'], o['wake']['first_attack']))
    print('standard gaps (ticks: count):', o['standard_gaps'])
    print('standards before each special (count, special, tick):', o['standards_before_special'])
    print('sequence:', o['sequence'])
    for r in o['rapid']:
        print('rapid:', r)
    print('barrage shots: tick, target, player on target at tick, at tick+1, hits in tick..tick+3')
    print('   on-tile at tick=%s; on-tile at tick+1=%s; hit=%s' % tuple(collections.Counter(
        (x[2], x[3], bool(x[4])) for x in o['barrage']).most_common(0) or ('', '', '')))
    print('   ', sorted(collections.Counter((x[2], x[3], bool(x[4])) for x in o['barrage']).items(), key=str))
    for s in o['spawn']:
        print('spawn:', s)
    print('kill:', o['kill'])
    print('messages:')
    for k, v in o['messages'].items():
        print('   %dx %s' % (v, k[:110]))
    print('spam (dragon):')
    for k, v in o['spam'].items():
        print('   %dx %s' % (v, k[:110]))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        show(p, fight(p))
