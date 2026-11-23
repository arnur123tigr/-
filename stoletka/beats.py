"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('rec0', 'Столетняя война длилась не сто лет. Она длилась сто шестнадцать.'), ('trap', 'На ЕНТ путаются именно здесь.'), ('rem', 'Запомни: 1337 и 1453.'),
            ('why', 'А теперь посмотрим, почему.'), ('lands', 'Англия и Франция воевали за земли: Нормандию, Анжу, Аквитанию, Фландрию.'),
            ('throne', 'К тому же английский король претендовал и на французский трон.'), ('truce', 'Но воевали они не без перерыва. Были перемирия.'),
            ('plague', 'А ещё пришла чума, «Чёрная смерть».'), ('jac', 'В 1358 году во Франции началась Жакерия,'), ('tyler', 'в 1381-м в Англии — восстание Уота Тайлера.'),
            ('lose', 'К концу эпохи Франция была на грани поражения.'), ('orl', 'Север у англичан, Орлеан в осаде.'), ('girl', 'И тогда появилась семнадцатилетняя крестьянка.'),
            ('name', 'Её звали Жанна.'), ('y1429', 'В 1429 году она освободила Орлеан.'), ('burn', 'Но через два года англичане сожгли её на костре.'),
            ('age19', 'Ей было всего девятнадцать.'), ('turn', 'Но перелом, начатый Жанной, было уже не остановить.'),
            ('y1453', 'В 1453 году война закончилась, Франция вернула свои земли.'), ('calais', 'У англичан остался только Кале.'),
            ('roses', 'А в Англии вскоре началась война Алой и Белой розы.'), ('ent', 'Вопрос ЕНТ.'), ('q', 'Где и когда было восстание Жакерия?'),
            ('ans', 'Правильно: во Франции, в 1358 году.'), ('cta', 'Чтобы разбирать такие ловушки вместе, перейдите по ссылке в шапке профиля.')],
     'kk': [('rec0', 'Жүз жылдық соғыс жүз жыл болған жоқ. Ол жүз он алты жылға созылды.'), ('trap', 'ҰБТ-да дәл осы жерде шатасады.'), ('rem', 'Есте сақта: 1337 бен 1453.'),
            ('why', 'Енді неге екенін көрейік.'), ('lands', 'Англия мен Франция жер үшін соғысты: Нормандия, Анжу, Аквитания, Фландрия.'),
            ('throne', 'Оның үстіне ағылшын королі Франция тағына да таласты.'), ('truce', 'Бірақ олар үздіксіз соғысқан жоқ. Арада бітімдер болды.'),
            ('plague', 'Оның үстіне «Қара өлім» обасы келді.'), ('jac', '1358 жылы Францияда Жакерия,'), ('tyler', '1381 жылы Англияда Уот Тайлер көтерілісі басталды.'),
            ('lose', 'Ғасыр аяғында Франция жеңілуге жақын қалды.'), ('orl', 'Солтүстігі ағылшындардың қолында, Орлеан қоршауда.'), ('girl', 'Сол кезде он жеті жасар шаруа қызы шықты.'),
            ('name', 'Аты — Жанна.'), ('y1429', '1429 жылы ол Орлеанды азат етті.'), ('burn', 'Бірақ екі жылдан кейін ағылшындар оны отқа өртеді.'),
            ('age19', 'Ол бар болғаны он тоғызда еді.'), ('turn', 'Бірақ Жанна бастаған бетбұрысты ешкім тоқтата алмады.'),
            ('y1453', '1453 жылы соғыс аяқталды, Франция жерлерін қайтарды.'), ('calais', 'Ағылшындарда тек Кале қаласы қалды.'),
            ('roses', 'Ал Англияда іле-шала Ақ және Қызыл раушандар соғысы басталды.'), ('ent', 'ҰБТ сұрағы.'), ('q', 'Жакерия көтерілісі қай елде, қай жылы болды?'),
            ('ans', 'Дұрыс: Францияда, 1358 жылы.'), ('cta', 'Осындай тұзақтарды бірге талдау үшін профиль шапкасындағы сілтемеге өтіңіз.')]}
ALT = {('kk', 'trap'): 'өбе|ұбт|ұ', ('kk', 'ent'): 'өбе|ұбт|ұ', ('kk', 'jac'): '1\\d\\d\\d', ('kk', 'y1453'): '14\\d\\d', ('kk', 'ans'): 'д[ұіу]р', ('kk', 'y1429'): '14\\d\\d', ('kk', 'tyler'): '13\\d\\d'}
ALT2 = {('kk', 'trap'): '', ('kk', 'ent'): '', ('kk', 'ans'): ''}
GAP = {}
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
