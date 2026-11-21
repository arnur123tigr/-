"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('rec0', 'Султан Египта, остановивший монголов, родился в нашей степи.'), ('show', 'Покажу его путь на карте.'), ('y1223', 'Примерно 1223 год.'),
            ('born', 'Бейбарс родился в Дешт-и-Кыпчаке, в кыпчакской семье.'), ('mong', 'Но пришли монголы.'), ('capt', 'Мальчика Бейбарса взяли в плен и продали в рабство.'),
            ('eye', 'Говорят, из-за бельма на глазу его продали дёшево.'), ('egypt', 'Его привезли в Египет и сделали мамлюком, то есть воином-рабом.'),
            ('bow', 'Степной мальчик владел конём и луком лучше всех.'), ('gen', 'Вскоре он стал полководцем.'), ('mong2', 'Те же монголы шли теперь на Египет.'),
            ('ain', 'В 1260 году при Айн-Джалуте мамлюки их разгромили.'), ('lead', 'Бейбарс был одним из главных полководцев этой битвы.'),
            ('first', 'Это первое крупное поражение монголов.'), ('sultan', 'В тот же год Бейбарс стал султаном Египта.'), ('rule', 'Вчерашний раб 17 лет правил Египтом и Сирией.'),
            ('kin', 'В Казахстане его считают земляком.'), ('ent', 'Вопрос с ЕНТ.'), ('q', 'В каком году мамлюки разбили монголов при Айн-Джалуте?'),
            ('opts', '1219, 1260 или 1380?'), ('ans', 'Правильно: 1260 год.'), ('path', 'От раба до султана — путь одного степного мальчика.'),
            ('often', 'Такие вопросы часто бывают на ЕНТ.'), ('cta', 'Перейдите по ссылке в шапке профиля.')],
     'kk': [('rec0', 'Моңғолдарды тоқтатқан Мысыр сұлтаны біздің далада туған.'), ('show', 'Жолын картадан көрсетемін.'), ('y1223', 'Шамамен 1223 жыл.'),
            ('born', 'Бейбарс Дешті Қыпшақта, қыпшақ отбасында туды.'), ('mong', 'Бірақ моңғолдар келді.'), ('capt', 'Бала Бейбарс тұтқынға түсіп, құлдыққа сатылды.'),
            ('eye', 'Көзінде ақ дағы болғандықтан, оны арзанға сатқан деседі.'), ('egypt', 'Оны Мысырға әкеліп, мәмлүк, яғни құл-жауынгер етті.'),
            ('bow', 'Дала баласы ат пен садақты бәрінен жақсы меңгерді.'), ('gen', 'Көп ұзамай ол қолбасшы болды.'), ('mong2', 'Сол моңғолдар енді Мысырға келе жатты.'),
            ('ain', '1260 жылы Айн-Джалутта мәмлүктер оларды талқандады.'), ('lead', 'Бейбарс сол шайқастың басты қолбасшыларының бірі болды.'),
            ('first', 'Моңғолдардың алғашқы ірі жеңілісі.'), ('sultan', 'Сол жылы Бейбарс Мысыр сұлтаны болды.'), ('rule', 'Кешегі құл 17 жыл бойы Мысыр мен Сирияны биледі.'),
            ('kin', 'Қазақстан оны жерлесіміз деп санайды.'), ('ent', 'ҰБТ сұрағы.'), ('q', 'Мәмлүктер моңғолдарды Айн-Джалутта қай жылы жеңді?'),
            ('opts', '1219, 1260 әлде 1380?'), ('ans', 'Дұрыс жауап: 1260 жыл.'), ('path', 'Құлдан сұлтанға дейін — бір дала баласының жолы.'),
            ('often', 'Мұндай сұрақтар ҰБТ-да жиі келеді.'), ('cta', 'Профиль шапкасындағы сілтемеге өтіңіз.')]}
ALT = {('kk', 'gen'): 'к[өе][пб]', ('kk', 'first'): 'м[оұ][нң]', ('kk', 'kin'): '[кқ]аз', ('kk', 'mong'): 'бір', ('kk', 'egypt'): '[оа]н[ыа]',
       ('ru', 'ain'): 'в$|1260', ('ru', 'sultan'): 'в$', ('ru', 'kin'): 'в$', ('ru', 'q'): 'в$', ('kk', 'rec0'): 'м'}
ALT2 = {('kk', 'egypt'): 'м[ыұ]с', ('ru', 'ain'): '', ('kk', 'gen'): '', ('kk', 'first'): ''}
GAP = {('kk', 'ent'): 'мәм'}   # whisper drops «ҰБТ сұрағы»: put the beat 1.7 s before the next sentence's first word
norm = lambda s: re.sub(r'[^\wәғқңөұүһі]', '', s.lower().replace('ё', 'е'))
out = json.load(open('beats.json')) if os.path.exists('beats.json') else {}
for L in sys.argv[1:] or ('ru', 'kk'):
    seq = S[L]; fn = f'words_{L}.json'
    if os.path.exists(fn):
        W = json.load(open(fn)); B = {}; i = 0
        for k, s in seq:
            if k == 'rec0': B[k] = 0.0; continue
            if (L, k) in GAP:
                j = next(j for j in range(i, len(W)) if re.match(GAP[(L, k)], norm(W[j][2]))); B[k] = round(W[j][0] - 1.7, 2); continue
            w0 = ALT.get((L, k)) or re.escape(norm(s.split()[0])[:3])
            sw = s.split(); w1 = ALT2.get((L, k)) or re.escape(norm(sw[1])[:3]) if len(sw) > 1 and norm(sw[1]) else ''
            j = next((j for j in range(i, len(W) - 1) if re.match(w0, norm(W[j][2])) and re.match(w1, norm(W[j + 1][2]))), None)
            if j is None: j = next((j for j in range(i, len(W)) if re.match(w0, norm(W[j][2]))), None)
            if j is None: sys.exit(f'{L}: no word for {k} ({s.split()[0]}) after {W[i][0] if i < len(W) else "end"}')
            B[k] = W[j][0] if k != 'rec0' else 0.0; i = j + 1
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
