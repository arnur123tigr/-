"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('h', 'Астана холоднее Москвы и даже Оттавы.'), ('how', 'Как так?'), ('n2', 'Это вторая самая холодная столица мира.'), ('r3', 'И есть три причины.'),
            ('jan', 'Средняя температура января — около минус четырнадцати.'),
            ('c1', 'Причина первая: океан очень далеко.'), ('warm', 'Тёплый морской воздух сюда не доходит.'),
            ('c2', 'Причина вторая: с севера нет гор.'), ('arc', 'Арктический воздух летит прямо по степи.'),
            ('c3', 'Причина третья: зимой над Сибирью стоит огромный антициклон.'), ('frost', 'Он и приносит морозы.'),
            ('ent', 'Это бывает на ЕНТ:'), ('kl', 'климат Казахстана — резко континентальный.'),
            ('but', 'Но самое удивительное:'), ('sum', 'летом здесь бывало плюс сорок один,'), ('win', 'а зимой минус пятьдесят один.'),
            ('diff', 'Разница больше девяноста градусов.'), ('kip', 'Почти как между кипятком и льдом.'),
            ('cta', 'Перейдите по ссылке в шапке профиля.')],
     'kk': [('h', 'Астана Мәскеуден де, Оттавадан да суық.'), ('how', 'Қалай?'), ('n2', 'Бұл әлемдегі екінші ең суық астана.'), ('r3', 'Оның үш себебі бар.'),
            ('jan', 'Қаңтардың орташа температурасы — шамамен минус он төрт.'),
            ('c1', 'Бірінші себеп: мұхит өте алыс.'), ('warm', 'Жылы теңіз ауасы бұл жерге жетпейді.'),
            ('c2', 'Екінші себеп: солтүстікте тау жоқ.'), ('arc', 'Арктика ауасы далаға тура соғады.'),
            ('c3', 'Үшінші себеп: қыста Сібір үстінде орасан зор антициклон тұрады.'), ('frost', 'Аязды сол әкеледі.'),
            ('ent', 'Бұл ҰБТ-да келеді:'), ('kl', 'Қазақстанның климаты — шұғыл континенттік.'),
            ('but', 'Ең таңғаларлығы:'), ('sum', 'мұнда жазда қырық бір градус ыстық,'), ('win', 'қыста минус елу бір градус аяз болған.'),
            ('diff', 'Айырмашылығы тоқсан градустан асады.'), ('kip', 'Қайнаған су мен мұздың арасындай.'),
            ('cta', 'Профиль шапкасындағы сілтемеге өтіңіз.')]}
PFX = {}
norm = lambda s: re.sub(r'[^\wәғқңөұүһі]', '', s.lower().replace('ё', 'е'))
out = json.load(open('beats.json')) if os.path.exists('beats.json') else {}
for L in sys.argv[1:] or ('ru', 'kk'):
    seq = S[L]; fn = f'words_{L}.json'
    if os.path.exists(fn):
        W = json.load(open(fn)); B = {}; i = 0
        for k, s in seq:
            w0 = norm(s.split()[0])[:PFX.get((L, k), 3)]
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
