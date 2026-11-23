"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('h1', 'Рим — самая сильная империя мира.'), ('h2', 'Но он платил золотом всадникам из степи.'),
            ('hun', 'Многие учёные связывают гуннов с хунну, которые тревожили Китай.'), ('hyp', 'Это гипотеза.'),
            ('but', 'Но их поход в Европу — точная история и вопрос ЕНТ.'), ('y370', 'В 370 году гунны разгромили Боспорское царство.'),
            ('y375', 'В 375-м перешли Волгу и подчинили остготов.'), ('mig', 'С этого началось Великое переселение народов.'),
            ('pann', 'Гунны осели в Паннонии.'), ('att', 'А в 434 году власть получил сын Мундзука Аттила.'), ('bich', 'Современники называли его «Бичом Божьим».'),
            ('const', 'Константинополь был вынужден каждый год платить золотом за мир.'), ('gold', 'Сначала 700 фунтов золота в год, потом 2100.'),
            ('malo', 'Но Аттиле этого было мало.'), ('gaul', 'В 451 году он вошёл в Галлию.'), ('cat', 'На Каталаунских полях римляне и вестготы едва его остановили.'),
            ('ital', 'На следующий год он пришёл в Италию, подошёл к Риму.'), ('died', 'А в 453 году внезапно умер.'), ('fall', 'Без Аттилы империя гуннов быстро распалась.'),
            ('ent', 'Запомни для ЕНТ.'), ('e1', '375 — гунны перешли Волгу.'), ('e2', '434 — Аттила пришёл к власти.'), ('e3', '«Бич Божий» — Аттила.'),
            ('jord', 'Историк Иордан писал, что он пришёл «потрясти народы».'), ('cta', 'Чтобы учить всемирную историю вот так, перейдите по ссылке в шапке профиля.')],
     'kk': [('h1', 'Рим — әлемдегі ең күшті империя.'), ('h2', 'Бірақ ол даладан келген салт аттыларға алтын төледі.'),
            ('hun', 'Көп ғалым ғұндарды Қытайды мазалаған хуннулармен байланыстырады.'), ('hyp', 'Бұл — болжам.'),
            ('but', 'Бірақ олардың Еуропаға жорығы — нақты тарих және ҰБТ сұрағы.'), ('y370', '370 жылы ғұндар Босфор патшалығын талқандады.'),
            ('y375', '375 жылы Еділден өтіп, остготтарды бағындырды.'), ('mig', 'Осыдан «Халықтардың ұлы қоныс аударуы» басталды.'),
            ('pann', 'Ғұндар Паннонияға қоныстанды.'), ('att', 'Ал 434 жылы билікке Мундзуктың ұлы Аттила келді.'), ('bich', 'Замандастары оны «Құдайдың қамшысы» деп атады.'),
            ('const', 'Константинополь бейбітшілік үшін жыл сайын алтын төлеуге мәжбүр болды.'), ('gold', 'Алдымен жылына 700 фунт алтын, кейін — 2100 фунт.'),
            ('malo', 'Бірақ Аттилаға бұл аз болды.'), ('gaul', '451 жылы ол Галлияға кірді.'), ('cat', 'Каталаун алқабында римдіктер мен вестготтар оны әрең тоқтатты.'),
            ('ital', 'Келесі жылы ол Италияға келді, Рим қақпасына жақындады.'), ('died', 'Ал 453 жылы кенеттен қайтыс болды.'), ('fall', 'Аттиласыз ғұн империясы тез ыдырады.'),
            ('ent', 'ҰБТ-ға есте сақта.'), ('e1', '375 — ғұндар Еділден өтті.'), ('e2', '434 — Аттила билікке келді.'), ('e3', '«Құдайдың қамшысы» — Аттила.'),
            ('jord', 'Иордан оны «халықтарды күйзелтуге келген адам» деп жазды.'), ('cta', 'Дүниежүзі тарихын осылай оқу үшін профиль шапкасындағы сілтемеге өтіңіз.')]}
ALT = {('kk', 'y370'): '37', ('kk', 'y375'): '37', ('kk', 'gaul'): '4', ('kk', 'ent'): 'ұбы', ('kk', 'fall'): 'атт', ('kk', 'e1'): '375', ('kk', 'e2'): '434', ('kk', 'jord'): '[йи]ор', ('kk', 'cta'): 'дүн', ('kk', 'h2'): 'бір', ('kk', 'but'): 'бір'}
ALT2 = {}
GAP = {}
norm = lambda s: re.sub(r'[^\wәғқңөұүһі]', '', s.lower().replace('ё', 'е'))
out = json.load(open('beats.json')) if os.path.exists('beats.json') else {}
for L in sys.argv[1:] or ('ru', 'kk'):
    seq = S[L]; fn = f'words_{L}.json'
    if os.path.exists(fn):
        W = json.load(open(fn)); B = {}; i = 0
        for k, s in seq:
            if k == 'h1': B[k] = 0.0; continue
            if (L, k) in GAP:
                j = next(j for j in range(i, len(W)) if re.match(GAP[(L, k)], norm(W[j][2]))); B[k] = round(W[j][0] - 1.7, 2); continue
            w0 = ALT.get((L, k)) or re.escape(norm(s.split()[0])[:3])
            sw = s.split(); w1 = ALT2.get((L, k)) or re.escape(norm(sw[1])[:3]) if len(sw) > 1 and norm(sw[1]) else ''
            j = next((j for j in range(i, len(W) - 1) if re.match(w0, norm(W[j][2])) and re.match(w1, norm(W[j + 1][2]))), None)
            if j is None: j = next((j for j in range(i, len(W)) if re.match(w0, norm(W[j][2]))), None)
            if j is None: sys.exit(f'{L}: no word for {k} ({s.split()[0]}) after {W[i][0] if i < len(W) else "end"}')
            B[k] = W[j][0] ; i = j + 1
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
