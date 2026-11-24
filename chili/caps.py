"""script_ru.txt + words_ru.json (whisper word times) -> caps_ru.json: 2-3-word captions timed to the real words.
Script words are aligned to whisper words with difflib (whisper misspells some), unmatched ones are interpolated.
Captions stop at the CTA sentence ('Хочешь больше')."""
import json, re, difflib
import re as _re
S = _re.sub(r'\[[^\]]*\]', '', open('script_ru.txt').read()).replace('\n', ' ')
S = S.split('Такие вопросы')[0]
SW = S.split()
W = json.load(open('words_ru.json'))
norm = lambda w: re.sub(r'[^а-яёa-z0-9]', '', w.lower().replace('ё', 'е'))
a = [norm(w) for w in SW]; b = [norm(w[2]) for w in W]
T = [None] * len(SW); E = [None] * len(SW)
for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
    for k in range(blk.size): T[blk.a + k] = W[blk.b + k][0]; E[blk.a + k] = W[blk.b + k][1]
# interpolate gaps
known = [i for i, x in enumerate(T) if x is not None]
for i in range(len(T)):
    if T[i] is None:
        p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
        if p is None: T[i] = T[n]; E[i] = T[n]
        elif n is None: T[i] = E[p]; E[i] = E[p] + .3
        else: f = (i - p) / (n - p); T[i] = E[p] + (T[n] - E[p]) * f; E[i] = T[i] + .2
chunks = []; cur = []
for i, w in enumerate(SW):
    if w in ('—', '–'): continue
    cur.append(i)
    txt = ' '.join(SW[j] for j in cur)
    if len(cur) == 3 or (len(cur) == 2 and len(txt) > 16) or w[-1] in ',.?:!;»' or len(txt) > 20:
        if len(cur) > 1 and len(norm(SW[cur[-1]])) <= 2 and w[-1].isalnum(): chunks.append(cur[:-1]); cur = cur[-1:]
        else: chunks.append(cur); cur = []
if cur: chunks.append(cur)
caps = []
for k, c in enumerate(chunks):
    t0 = T[c[0]]; t1 = E[c[-1]] + .25
    if k + 1 < len(chunks): t1 = min(max(t1, T[chunks[k + 1][0]] - .02), T[chunks[k + 1][0]] - .02) if T[chunks[k + 1][0]] - E[c[-1]] < .6 else t1
    s = ' '.join(SW[j] for j in c).strip(',.:;—–').replace('«', '').replace('»', '')
    caps.append([round(t0, 2), round(t1, 2), s.rstrip(',.:;')])
json.dump(caps, open('caps_ru.json', 'w'), ensure_ascii=False)
print(len(caps), 'captions; unmatched words:', sum(1 for i in range(len(SW)) if i not in known))
