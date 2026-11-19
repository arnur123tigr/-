"""raw_beats.json -> beats.json; captions (2-3 words, per-word times) -> caps_<lang>.json.
Caption text is the script text; a token 'X|n' stands for n spoken words (years written as digits)."""
import json
S = {'ru': ['Вся Южная Америка говорит по-испански. Почему Бразилия — нет?', 'Всё решила одна линия на карте. Три шага.',
            'Шаг первый: в пятнадцатом веке две страны спорили, кому достанутся новые земли.',
            'Шаг второй: в 1494-м|4 мир разделили линией. Запад — Испании, восток — Португалии.',
            'Шаг третий: край будущей Бразилии оказался на португальской стороне. В 1500-м|2 сюда приплыли португальцы.',
            'А потом португальцы ушли далеко на запад, за линию. Так Бразилия стала пятой страной мира по площади.',
            'Это бывает на ЕНТ: Великие географические открытия и кто открыл какие земли.',
            'Сегодня по-португальски в Бразилии говорят в двадцать раз больше людей, чем в самой Португалии.', None],
     'kk': ['Бүкіл Оңтүстік Америка испанша сөйлейді. Неге Бразилия олай емес?', 'Бәрін картадағы бір сызық шешті. Үш қадам.',
            'Бірінші қадам: он бесінші ғасырда екі ел жаңа жерлер кімге тиетінін таласты.',
            'Екінші қадам: 1494|5 жылы әлемді бір сызықпен бөлді. Батысы — Испанияға, шығысы — Португалияға.',
            'Үшінші қадам: болашақ Бразилияның шеті португал жағында қалды. 1500|3 жылы мұнда португалдар жүзіп келді.',
            'Кейін португалдар сызықтан әрі батысқа қарай кетті. Бразилия осылай аумағы бойынша әлемдегі бесінші ел болды.',
            'Бұл ҰБТ-да келеді: Ұлы географиялық ашулар және кім қай жерді ашқаны.',
            'Бүгін Бразилияда португалша сөйлейтіндер Португалияның өзінен жиырма есе көп.', None]}
SENT_KEY = ['q', 's2', 'st1', 'st2', 'st3', 'grow', 'ent', 'twist', 'cta']
RAW = json.load(open('raw_beats.json')); out = {}
for L in RAW:
    out[L] = RAW[L]; W = json.load(open(f'words_{L}.json')); caps = []
    st = [RAW[L][k] for k in SENT_KEY]
    for s, t0, t1 in zip(S[L], st, st[1:]):
        if s is None: break
        sw = [w for w in W if t0 - .05 <= w[0] < t1 - .05]
        toks = [w for w in s.split(' ') if w != '—']; toks = [(w.split('|')[0], int(w.split('|')[1]) if '|' in w else 1) for w in toks]
        tw = []
        if sum(n for _, n in toks) == len(sw):     # exact word times
            i = 0
            for w, n in toks: tw.append([w, sw[i][0], sw[i + n - 1][1]]); i += n
        else:                                       # fall back: spread over the sentence by length
            end = max([w[1] for w in sw] or [t1 - .3]); tot = sum(len(w) + 2 for w, _ in toks); t = t0
            for w, _ in toks: d = (end - t0) * (len(w) + 2) / tot; tw.append([w, round(t, 2), round(t + d, 2)]); t += d
            print('spread', L, s[:30])
        cur = []
        for w in tw:
            cur.append(w)
            if len(cur) == 3 or (len(cur) == 2 and len(' '.join(c[0] for c in cur)) > 16) or w[0][-1] in ',.?:':
                caps.append([cur[0][1], cur[-1][2], cur]); cur = []
        if cur: caps.append([cur[0][1], cur[-1][2], cur])
    json.dump(caps, open(f'caps_{L}.json', 'w'), ensure_ascii=False); print(L, len(caps), out[L]['vend'])
json.dump(out, open('beats.json', 'w'), indent=0)
