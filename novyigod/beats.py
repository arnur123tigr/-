"""beats_spec.txt + words_ru.json -> beats.json. Each spec line: `name word [n]` = start time of the n-th (default 1st) word
beginning with `word` after the previous beat. Adds cta (Такие), ent (ЕНТ), link (Переходи), prep (чтобы) and vend (end of last word)."""
import json, re
W = json.load(open('words_ru.json'))
norm = lambda s: re.sub(r'[^а-яёa-z0-9]', '', s.lower().replace('ё', 'е'))
B = {}; i = 0
lines = [l.split() for l in open('beats_spec.txt') if l.strip() and not l.startswith('#')]
lines += [['cta', 'такие'], ['ent', 'ент'], ['link', 'переходи'], ['prep', 'чтобы']]
for parts in lines:
    name, w = parts[0], norm(parts[1]); n = int(parts[2]) if len(parts) > 2 else 1
    if w == '0': B[name] = 0.0; continue
    j = i
    while j < len(W):
        if norm(W[j][2]).startswith(w):
            n -= 1
            if n == 0: break
        j += 1
    if j >= len(W): raise SystemExit(f'beat {name}: word {w} not found after index {i}')
    B[name] = W[j][0]; i = j + 1
B['vend'] = W[-1][1]
json.dump({'ru': B}, open('beats.json', 'w'), indent=0); print(len(B), 'beats; vend', B['vend'])
