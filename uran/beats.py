"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('h', 'Почти половину урана планеты добывает одна страна.'), ('kz', 'И это Казахстан.'), ('u', 'Речь об уране.'),
            ('f3', 'Три факта, и последний самый странный.'), ('p1', 'Первый:'), ('pct', 'Казахстан добывает около 40% урана планеты.'),
            ('most', 'Больше всех.'), ('y09', 'И держит первое место уже больше 15 лет.'), ('p2', 'Второй:'),
            ('south', 'почти весь уран — на юге,'), ('sands', 'в песках между Шу и Сырдарьёй.'),
            ('coal', 'Одна тонна урана даёт столько энергии,'), ('coal2', 'сколько 16 тысяч тонн угля.'),
            ('ent', 'Это бывает на ЕНТ:'), ('where', 'где в Казахстане добывают уран.'), ('p3', 'Третий:'),
            ('nomine', 'здесь нет шахт и карьеров.'), ('sol', 'В землю закачивают раствор,'), ('rise', 'и уран поднимается сам.'),
            ('steppe', 'Сверху это выглядит как обычная степь.'), ('fuel', 'А под ней — топливо для атомных станций всего мира.'),
            ('cta', 'Перейдите по ссылке в шапке профиля.')],
     'kk': [('h', 'Планетадағы уранның жартысына жуығын бір ел өндіреді.'), ('kz', 'Ол — Қазақстан.'), ('u', 'Әңгіме уран туралы.'),
            ('f3', 'Үш дерек, соңғысы ең таңғаларлық.'), ('p1', 'Біріншісі:'), ('pct', 'Қазақстан планетадағы уранның шамамен 40% өндіреді.'),
            ('most', 'Бәрінен көп.'), ('y09', 'Бірінші орынды 15 жылдан астам ұстап келеді.'), ('p2', 'Екіншісі:'),
            ('south', 'уранның басым бөлігі оңтүстікте,'), ('sands', 'Шу мен Сырдария арасындағы құмда.'),
            ('coal', 'Бір тонна уран'), ('coal2', '16 мың тонна көмірдей энергия береді.'),
            ('ent', 'Бұл ҰБТ-да келеді:'), ('where', 'Қазақстанда уран қай жерде өндіріледі.'), ('p3', 'Үшіншісі:'),
            ('nomine', 'мұнда шахта да, карьер де жоқ.'), ('sol', 'Жерге ерітінді құяды,'), ('rise', 'уран өзі көтеріледі.'),
            ('steppe', 'Үстінен қарасаң — кәдімгі дала.'), ('fuel', 'Ал астында — бүкіл әлемдегі атом стансаларына отын.'),
            ('cta', 'Профиль шапкасындағы сілтемеге өтіңіз.')]}
ALIAS = {('ru', 'sands'): 'пес', ('kk', 'most'): 'дәр', ('kk', 'south'): 'ұра', ('kk', 'steppe'): 'үс', ('kk', 'coal2'): '16', ('ru', 'coal2'): 'ск', ('kk', 'h'): 'пла'}
norm = lambda s: re.sub(r'[^\wәғқңөұүһі]', '', s.lower().replace('ё', 'е'))
out = json.load(open('beats.json')) if os.path.exists('beats.json') else {}
for L in sys.argv[1:] or ('ru', 'kk'):
    seq = S[L]; fn = f'words_{L}.json'
    if os.path.exists(fn):
        W = json.load(open(fn)); B = {}; i = 0
        for k, s in seq:
            w0 = ALIAS.get((L, k)) or norm(s.split()[0])[:3]
            j = next((j for j in range(i, len(W)) if norm(W[j][2]).startswith(w0)), None)
            if j is None: sys.exit(f'{L}: no word for {k} ({s.split()[0]}) after {W[i][0] if i < len(W) else "end"}')
            B[k] = W[j][0] if k != 'h' else 0.0; i = j + 1
        B['vend'] = W[-1][1]
    else:
        B = {}; t = 0
        for k, s in seq: B[k] = round(t, 2); t += len(s.split()) / 2.6 + .25
        B['vend'] = round(t - .25, 2); W = None
    out[L] = B
    keys = [k for k, _ in seq] + ['vend']; caps = []
    for n, (k, s) in enumerate(seq):
        t0, t1 = B[k], B[keys[n + 1]]
        end = max([w[1] for w in W if t0 - .05 <= w[0] < t1 - .05] or [t1 - .3]) if W else t1 - .25
        words = s.replace(' —', '').split(' '); tot = sum(len(w) + 2 for w in words); t = t0; tw = []
        for w in words: d = (end - t0) * (len(w) + 2) / tot; tw.append([w, round(t, 2), round(t + d, 2)]); t += d
        cur = []
        for w in tw:
            cur.append(w)
            if len(cur) == 3 or (len(cur) == 2 and len(' '.join(c[0] for c in cur)) > 16) or w[0][-1] in ',.?:':
                caps.append([cur[0][1], cur[-1][2], cur]); cur = []
        if cur: caps.append([cur[0][1], cur[-1][2], cur])
    json.dump(caps, open(f'caps_{L}.json', 'w'), ensure_ascii=False)
    print(L, B)
json.dump(out, open('beats.json', 'w'), indent=0)
