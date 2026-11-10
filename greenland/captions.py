"""caps.json: short on-screen captions (1-3 words) timed to the voice, text from the script (whisper only gives timing)."""
import json, re, difflib
SCRIPT = """Почему Гренландию назвали «Зелёной землёй», если она на 80% состоит из ледников и почти полностью покрыта льдом? А Исландию, которая славится зелёными пейзажами и горячими источниками, — «Ледяной землёй»? Кажется, будто названия перепутали. На самом деле это хитрость викингов.
В IX веке норвежские викинги первыми доплыли до берегов Исландии. Была зима, и они не увидели ничего, кроме льда и снега. Поэтому и назвали её Исландией — «Ледяной землёй».
Тогда первооткрыватели часто называли новые земли по тому, что видели первым. Например, Флорида получила имя от испанцев — «земля цветов», потому что они приплыли в самый разгар цветения.
Спустя время, когда Исландию уже заселили, одного из викингов — Эрика Рыжего — изгнали с острова за преступления. В поисках новых земель он поплыл на запад и наткнулся на огромный ледяной остров. Эрик понимал, что заманить туда поселенцев будет непросто. И пошёл на хитрость: назвал остров Гренландией — «Зелёной землёй», полной противоположностью тому, чем он был на самом деле. Чтобы название звучало заманчиво для новых жителей."""
toks = [w for w in SCRIPT.replace('—', ' ').split() if w.strip()]
W = json.load(open('words.json'))
key = lambda s: re.sub(r'[^а-яёa-z0-9]', '', s.lower().replace('ё', 'е'))
A = [key(t) for t in toks]; B = [key(w[2]) for w in W]
T = [None] * len(toks)
for a, b, n in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks():
    for i in range(n): T[a + i] = (W[b + i][0], W[b + i][1])
for i in range(len(T)):   # interpolate unmatched words
    if T[i] is None:
        j = i - 1; k = i + 1
        while k < len(T) and T[k] is None: k += 1
        s0 = T[j][1] if j >= 0 and T[j] else 0; s1 = T[k][0] if k < len(T) else s0 + 1
        n = k - i; m = i - j - 1
        d = (s1 - s0) / (n + m + 1) if False else (s1 - s0) / (k - j)
        T[i] = (s0 + d * (i - j - 1), s0 + d * (i - j))
caps = []; cur = []
for i, t in enumerate(toks):
    cur.append(i)
    txt = ' '.join(toks[j] for j in cur)
    endp = re.search(r'[.,:!?]$', t) is not None
    nxt_gap = (T[i + 1][0] - T[i][1]) if i + 1 < len(toks) else 9
    if endp or len(cur) >= 3 or len(txt) > 16 or nxt_gap > .35 or (i + 1 < len(toks) and len(txt + toks[i + 1]) > 20):
        caps.append([round(T[cur[0]][0], 2), round(T[i][1], 2), re.sub(r'[.,:]$', '', txt)]); cur = []
for a, b in zip(caps, caps[1:]): a[1] = round(min(b[0], max(a[1], a[0] + .3)), 2)
json.dump(caps, open('caps.json', 'w'), ensure_ascii=False)
for c in caps: print(c)
