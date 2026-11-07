"""words_b.json (whisper word times of the RU voice) + the script's own spelling -> captions.json.
Chunks of 1-3 words like the original reel; words appear one by one; [..] = yellow highlight box."""
import json, re, difflib
SCRIPT = """Что, если сжать [всю историю] Земли в [один год?] | Поехали! | 1 января, полночь. | Земля [родилась!] | Светящийся шар [из лавы!] |
Через несколько дней... | [Бум!] | Гигантское столкновение — | и рождается [Луна.] | В марте в океанах | появляются первые | [крошечные живые] существа. |
А потом ждём... | и [ждём...] | и [ждём!] | Апрель, май, июнь, | сентябрь, октябрь... | До сих пор | [ни одного животного] | и ни одного [дерева!] |
И вот, [18 ноября...] | [Бабах!] | [Кембрийский взрыв!] | Моря вдруг наполняются | [странными и удивительными] существами! |
В начале декабря | рыба делает | свой [первый шаг] | на сушу. | 11 декабря — | [Великое вымирание!] | Исчезают [9 видов] из 10. |
Но 13 декабря | появляются [динозавры!] | 26 декабря | падает [гигантский астероид] | и динозавров больше нет. | Ну... | не всех. |
Птицы — их | [пра-пра-правнуки!] | Так когда же | появились [мы?] | 31 декабря, | за [35 минут] | до полуночи! |
Осталась [минута 20 секунд] — | первые фермы. | [36 секунд] — | изобретена письменность. | Начинается вся | записанная история. |
Меньше [2 секунд] — | рождается Америка. | В этом календаре | 1 секунда — | это [144 года.] | Значит, вся твоя жизнь — | примерно [полсекунды!] |
[Только представь:] | динозавры правили | этим календарём | целых [13 дней.] | А вся записанная история — | всего [36 секунд!] |
Кстати, такие вопросы | часто попадаются | на [ЕНТ по географии.] | Мы подготовили | [гайд по географии.] | Напиши в комментариях | слово [«гео»,] | чтобы его получить!"""
def norm(w): return re.sub(r'[^0-9а-яё]', '', w.lower().replace('ё', 'е'))
W = json.load(open('words_b.json'))
# expand whisper tokens that the script splits differently
wt = []
for s, e, w in W:
    if w == '—': continue
    if norm(w) == 'прапраправнуки': wt.append([s, e, 'прапраправнуки']); continue
    wt.append([s, e, w])
chunks = []
for ch in SCRIPT.replace('\n', ' ').split('|'):
    toks, hl = [], False
    for w in ch.split():
        if w == '—': toks[-1][0] += ' —'; continue
        a = w.startswith('['); b = w.endswith(']'); w = w.strip('[]')
        if a: hl = True
        toks.append([w, hl]); 
        if b: hl = False
    chunks.append(toks)
flat = [t for c in chunks for t in c]
A = [norm(t[0]) for t in flat]; B = [norm(w[2]) for w in wt]
alias = {'1': 'один', 'ждем': 'ждем'}
B = [{'злавы': 'излавы', 'шары': 'шар', 'светящейся': 'светящийся', 'бобах': 'бабах', 'юнь': 'июнь', 'осталось': 'осталась', 'ent': 'ент', 'двух': '2', 'одна': '1', 'гео': 'гео', 'прапраправнуки': 'прапраправнуки', 'календарем': 'календарем'}.get(b, b) for b in B]
A2 = [{'изобретена': 'изобретена', 'из': 'из', 'лавы': 'излавы', 'прапраправнуки': 'прапраправнуки'}.get(a, a) for a in A]
times = [None] * len(flat)
sm = difflib.SequenceMatcher(None, A2, B, autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size): times[blk.a + k] = (wt[blk.b + k][0], wt[blk.b + k][1])
# 'из'+'лавы' both map to one whisper word 'злавы'
for i in range(len(flat)):
    if times[i] is None:
        p = next((times[j] for j in range(i - 1, -1, -1) if times[j]), (0, 0)); n = next((times[j] for j in range(i + 1, len(flat)) if times[j]), (p[1] + .3, p[1] + .6))
        times[i] = (p[1], max(p[1] + .05, n[0]))
        print('interp', flat[i][0], times[i])
out, k = [], 0
for c in chunks:
    ws = []
    for w, h in c: ws.append({'w': w, 'h': h, 's': round(times[k][0], 2)}); k += 1
    out.append({'s': ws[0]['s'], 'e': round(times[k - 1][1], 2), 'ws': ws})
for a, b in zip(out, out[1:]): a['e'] = round(min(b['s'], a['e'] + 0.5), 2)
json.dump(out, open('captions.json', 'w'), ensure_ascii=False)
print(len(out)); print('\n'.join(f"{c['s']:6.2f}-{c['e']:6.2f} " + ' '.join(('[' + w['w'] + ']') if w['h'] else w['w'] for w in c['ws']) for c in out))
