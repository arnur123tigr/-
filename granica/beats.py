"""raw_beats.json -> beats.json; captions (2-3 words, per-word times) -> caps_<lang>.json.
Caption text is the script text; a token 'X|n' stands for n spoken words (years written as digits)."""
import json
S = {'ru': ['Самая длинная сухопутная граница в мире — наша?', 'Есть подвох. Три факта, чтобы разобраться.',
            'Первый: граница Казахстана с Россией — около 7,5 тысяч километров.', 'Это длиннее, чем от Алматы до Лондона.',
            'Второй: у США и Канады граница ещё длиннее — почти 9 тысяч километров.', 'Но она разорвана на две части. Аляска отделена от остальных США.',
            'Третий: а наша идёт одним куском. Это самая длинная непрерывная сухопутная граница на Земле.',
            'Это бывает на ЕНТ: у Казахстана 5 соседей, и самая длинная граница — с Россией.',
            'И эту гигантскую линию до сих пор отмечают на местности пограничными столбами.', None],
     'kk': ['Әлемдегі ең ұзын құрлық шекарасы — біздікі ме?', 'Мұнда бір құпия бар. Анықтау үшін үш|2 дерек.',
            'Біріншісі: Қазақстан мен Ресей шекарасы — шамамен 7,5|2 мың шақырым.', 'Бұл Алматыдан Лондонға дейінгі қашықтықтан да ұзақ.',
            'Екіншісі: Америка мен|1 Канаданың шекарасы одан да ұзын — 9 мыңға жуық шақырым.', 'Бірақ ол екіге бөлінген. Аляска Американың қалған бөлігінен бөлек.',
            'Үшіншісі: ал біздікі тұтас бір сызық. Бұл — Жердегі ең ұзын үзіліссіз құрлық шекарасы.',
            'Бұл ҰБТ-да|2 келеді: Қазақстанның бес көршісі бар, ең ұзын шекара — Ресеймен.',
            'Осы алып сызықты әлі күнге|1 дейін жергілікті жерде шекара бағандарымен белгілеп жатыр.', None]}
SENT_KEY = ['q', 's2', 'f1', 'lon', 'f2', 'split', 'f3', 'ent', 'dem', 'cta']
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
