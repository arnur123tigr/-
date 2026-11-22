"""Align the caption script (script_kk.txt) to whisper word times (words_kk.json) -> beats.json
Markup: @name = scene beat at the next word, | = caption chunk end, {spoken=display} = text shown differently from what is said."""
import json, re, difflib
W = json.load(open('words_kk.json'))
norm = lambda s: re.sub(r'[^0-9a-zа-яёәғқңөұүһі]', '', s.lower())
# whisper chars with times
wc, wt = [], []
for w in W:
    n = norm(w['w'])
    for i, ch in enumerate(n): wc.append(ch); wt.append(w['s'] + (w['e'] - w['s']) * i / max(1, len(n)))
src = open('script_kk.txt').read()
toks = re.findall(r'@\w+|\||\{[^}]*\}|[^\s|{}]+', src)
words, beats, chunks, cur = [], {}, [], []
pend = []
for t in toks:
    if t.startswith('@'): pend.append(t[1:]); continue
    if t == '|':
        if cur: chunks.append(cur); cur = []
        continue
    if t.startswith('{'): sp, disp = t[1:-1].split('=')
    else: sp = disp = t
    words.append(dict(sp=sp, d=disp, beats=pend)); pend = []; cur.append(len(words) - 1)
sc = []; owner = []
for i, w in enumerate(words):
    for ch in norm(w['sp']): sc.append(ch); owner.append(i)
sm = difflib.SequenceMatcher(None, sc, wc, autojunk=False)
m = {}
for a, b, n in sm.get_matching_blocks():
    for k in range(n): m[a + k] = b + k
# per word: first/last matched char
for i, w in enumerate(words):
    idx = [k for k, o in enumerate(owner) if o == i]
    hit = [m[k] for k in idx if k in m]
    w['s'] = wt[hit[0]] if hit else None; w['e'] = wt[hit[-1]] + .08 if hit else None
# interpolate missing
for i, w in enumerate(words):
    if w['s'] is None:
        a = next((words[j] for j in range(i - 1, -1, -1) if words[j]['s'] is not None), None)
        b = next((words[j] for j in range(i + 1, len(words)) if words[j]['s'] is not None), None)
        w['s'] = (a['e'] if a else 0) if not b else ((a['e'] + b['s']) / 2 if a else b['s'] - .3); w['e'] = w['s'] + .25
for w in words:
    for b in w['beats']: beats[b] = round(w['s'], 3)
caps = [dict(s=round(words[c[0]]['s'], 3), e=round(words[c[-1]]['e'], 3), w=[dict(t=words[k]['d'], s=round(words[k]['s'], 3)) for k in c]) for c in chunks]
json.dump(dict(beats=beats, caps=caps, vend=round(W[-1]['e'], 3)), open('beats.json', 'w'), ensure_ascii=False, indent=0)
print(len(words), 'words', len(caps), 'chunks', 'unmatched', sum(1 for k in range(len(sc)) if k not in m), '/', len(sc))
print(beats)
