"""words_a.json (whisper word times of the RU voice) -> captions.json: 2-3 word chunks like the original reel, with the script's spelling."""
import json
W = json.load(open('words_a.json'))
fix = {'тихого': 'Тихого', 'тихий': 'Тихий', 'нынешние': 'нынешний', 'теплую': 'тёплую', 'теплая': 'тёплая', 'теплые': 'тёплые', 'Северной': 'северной',
       'Южного': 'южного', 'реквадора': 'Эквадора', 'остается': 'остаётся', 'Югу': 'югу', 'в': 'в', 'унес': 'унёс', 'ученые': 'учёные',
       'теплого': 'тепло в', 'ENT': 'ЕНТ', 'ENT.': 'ЕНТ.', '«Гео».': '«гео».', 'два,': '2–7', 'семь': None, 'лет,': 'лет',
       'климатно': 'климат на', '-побережье': 'побережье', 'Ниньо': 'Ниньо'}
toks = []
for i, (s, e, w) in enumerate(W):
    if w == 'в' and W[i + 1][2] == 'части' and W[i - 1][2] == 'дожди,': continue
    if w == '-побережье': toks.append([s, e, 'побережье']); continue
    if w.startswith('-'):   # whisper split: "Эль" "-миньо," / "1" "-2" / "1870" "-х"
        p = toks[-1]; w2 = w.replace('-миньо', '-Ниньо')
        p[2] = ('супер Эль' if p[2] == 'суперэль' else p[2]) + ('–' + w2[1:] if w2[1:2].isdigit() else w2); p[1] = e; continue
    if w == '—': continue
    if w == '%': toks[-1][2] += '%'; toks[-1][1] = e; continue
    if w == 'Ниньо' or (w.startswith('Ниньо') and toks and toks[-1][2] == 'Эль'): toks[-1][2] = 'Эль-' + w; toks[-1][1] = e; continue
    w = fix.get(w, w)
    if w is None: toks[-1][1] = e; continue
    toks.append([s, e, w])
caps, cur = [], []
for t in toks:
    cur.append(t)
    L = len(' '.join(x[2] for x in cur))
    if t[2][-1] in '.?!:,—' and L > 2 or L > 15 or len(cur) == 3:
        caps.append(cur); cur = []
if cur: caps.append(cur)
out = [{'s': c[0][0], 'e': c[-1][1], 't': ' '.join(x[2] for x in c).rstrip(',.:') .replace(' —', '').replace('— ', '')} for c in caps]
for a, b in zip(out, out[1:]): a['e'] = min(b['s'], a['e'] + 0.4)
json.dump(out, open('captions.json', 'w'), ensure_ascii=False)
print(len(out)); print(' | '.join(c['t'] for c in out))
