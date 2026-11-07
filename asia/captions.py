"""words_b.json (whisper word times) -> captions.json: short caption chunks with the script's spelling."""
import json
W = json.load(open('words_b.json'))
fix = {'контимент': 'континент', 'соседином': 'соседи на', 'Атирике': 'материке', 'Оон': 'ООН', 'Шриланка': 'Шри-Ланка',
       'Тяньшанем': 'Тянь-Шанем', 'Стан,': '«стан»:', 'Станы,': '«станы»,', 'разберемся.': 'разберёмся.', 'живет': 'живёт',
       'все,': 'всё,', 'ее': 'её', 'центральную': 'Центральную', 'центральная': 'Центральная', 'названия': 'название', 'дальним': 'Дальним'}
toks = []
for i, (s, e, w) in enumerate(W):
    if w == 'Все' and i > 0 and W[i - 1][2].startswith('Восток'): w = 'Всё'
    elif w == 'Все': w = 'Все'
    if w == 'названия' and W[i - 1][2] == 'что': w = 'название'
    elif w == 'названия': pass
    else: w = fix.get(w, w)
    if w == '%': toks[-1][2] += '%'; toks[-1][1] = e; continue
    if w == '-Восточная': toks[-1][2] += '-Восточная'; toks[-1][1] = e; continue
    if w == '—': toks[-1][2] += ' —'; continue
    toks.append([s, e, w])
caps, cur = [], []
for t in toks:
    cur.append(t)
    L = len(' '.join(x[2] for x in cur))
    if t[2][-1] in '.?!:' or L > 20 or (t[2][-1] in ',—' and L > 12):
        caps.append(cur); cur = []
if cur: caps.append(cur)
out = []
for c in caps:
    out.append({'s': c[0][0], 'e': c[-1][1], 'w': [[x[0], x[2]] for x in c]})
for a, b in zip(out, out[1:]): a['e'] = min(b['s'], a['e'] + 0.5)
json.dump(out, open('captions.json', 'w'), ensure_ascii=False)
print(len(out)); print(' | '.join(' '.join(w for _, w in c['w']) for c in out))
