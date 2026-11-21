"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('rec0', 'Космодром Байконур находится не в Байконуре.'), ('map', 'Покажу на карте.'), ('tyur', 'Ракеты взлетают вот отсюда:'),
            ('kzo', 'Кызылординская область, станция Тюратам.'), ('real', 'А настоящий посёлок Байконур —'), ('km', 'больше чем в 300 километрах, в сторону Улытау.'),
            ('y55', 'В 1955 году в этой степи начали строить секретный полигон.'), ('noname', 'Тогда у него даже названия не было.'),
            ('y61', 'В 1961 году отсюда в космос полетел Гагарин.'), ('world', 'Весь мир спросил, откуда старт.'), ('hide', 'И чтобы скрыть настоящее место,'),
            ('named', 'назвали посёлок далеко отсюда: Байконур.'), ('len', 'Сам город долго назывался Ленинск,'), ('y95', 'Байконуром он стал только в 1995 году.'),
            ('rent', 'А космодром Россия арендует до 2050 года.'), ('ent', 'Запомни для ЕНТ.'), ('first', 'А первый казахский космонавт стартовал с этого Байконура в 1991 году.'),
            ('q', 'Вопрос с ЕНТ.'), ('who', 'Кто первый казахский космонавт?'), ('opts', 'Мусабаев, Аубакиров или Аимбетов?'),
            ('ans', 'Правильно: Токтар Аубакиров, 1991 год.'), ('often', 'Такие вопросы часто бывают на ЕНТ, мы разбираем их по одному.'),
            ('cta', 'Перейдите по ссылке в шапке профиля.')],
     'kk': [('rec0', 'Байқоңыр ғарыш айлағы Байқоңырда емес.'), ('map', 'Картадан көрсетемін.'), ('tyur', 'Ракеталар мына жерден ұшады:'),
            ('kzo', 'Қызылорда облысы, Төретам бекеті.'), ('real', 'Ал нағыз Байқоңыр кенті —'), ('km', '300 шақырымнан да алыс, Ұлытау жақта.'),
            ('y55', '1955 жылы осы далада құпия полигон сала бастады.'), ('noname', 'Ол кезде оның аты да жоқ еді.'),
            ('y61', '1961 жылы Гагарин осы жерден ғарышқа ұшты.'), ('world', 'Бүкіл әлем айлақтың атын сұрады.'), ('hide', 'Сонда шын орнын жасыру үшін'),
            ('named', 'алыстағы кенттің атын берді: Байқоңыр.'), ('len', 'Қаланың өзі де ұзақ уақыт Ленинск аталды,'), ('y95', 'тек 1995 жылы Байқоңыр болды.'),
            ('rent', 'Ал айлақты Ресей 2050 жылға дейін жалға алған.'), ('ent', 'ҰБТ-ға есте сақта.'), ('first', 'Алғашқы қазақ ғарышкері осы Байқоңырдан 1991 жылы ұшты.'),
            ('q', 'ҰБТ сұрағы.'), ('who', 'Алғашқы қазақ ғарышкері кім?'), ('opts', 'Мұсабаев, Әубәкіров әлде Аймбетов?'),
            ('ans', 'Дұрыс жауап: Тоқтар Әубәкіров, 1991 жыл.'), ('often', 'Мұндай сұрақтар ҰБТ-да жиі келеді, біз оларды бір-бірлеп талдаймыз.'),
            ('cta', 'Профиль шапкасындағы сілтемеге өтіңіз.')]}
ALT = {('kk', 'km'): '(үш|300|3)', ('kk', 'y55'): '(мың|1955|19|бір)', ('kk', 'y61'): '(мың|1961|19|бір)', ('kk', 'y95'): 'тек', ('kk', 'world'): 'б[үө]к',
       ('kk', 'ent'): '(обт|ұбт|өбт)', ('kk', 'q'): '(обт|ұбт|өбт)', ('ru', 'km'): 'бол', ('ru', 'y55'): '1955', ('ru', 'y61'): '1961', ('kk', 'named'): 'ал[ыс]', ('kk', 'ans'): 'д[ұуіи]', ('ru', 'kzo'): '(к[аы]з)', ('kk', 'kzo'): 'қыз', ('kk', 'len'): 'қал', ('kk', 'who'): 'алғ', ('kk', 'first'): 'алғ', ('kk', 'opts'): 'м[ұу]с', ('kk', 'often'): 'м[ұу]н'}
norm = lambda s: re.sub(r'[^\wәғқңөұүһі]', '', s.lower().replace('ё', 'е'))
out = json.load(open('beats.json')) if os.path.exists('beats.json') else {}
for L in sys.argv[1:] or ('ru', 'kk'):
    seq = S[L]; fn = f'words_{L}.json'
    if os.path.exists(fn):
        W = json.load(open(fn)); B = {}; i = 0
        for k, s in seq:
            if k == 'rec0': B[k] = 0.0; continue
            w0 = ALT.get((L, k)) or re.escape(norm(s.split()[0])[:3])
            j = next((j for j in range(i, len(W)) if re.match(w0, norm(W[j][2]))), None)
            if j is None: sys.exit(f'{L}: no word for {k} ({s.split()[0]}) after {W[i][0] if i < len(W) else "end"}')
            B[k] = W[j][0] if k != 'rec0' else 0.0; i = j + 1
        B['vend'] = W[-1][1]; B['_p0'] = max(w[1] for w in W if w[0] < B['ans'] - .05)
    else:
        B = {}; t = 0
        for k, s in seq: B[k] = round(t, 2); t += len(s.split()) / 2.6 + .25
        B['vend'] = round(t - .25, 2); W = None
    out[L] = B
    keys = [k for k, _ in seq] + ['vend']; caps = []
    for n, (k, s) in enumerate(seq):
        t0, t1 = B[k], B[keys[n + 1]]
        end = max([w[1] for w in W if t0 - .05 <= w[0] < t1 - .05] or [t1 - .3]) if W else t1 - .25
        words = s.replace(' —', '').split(' '); wl = lambda w: (26 if any(ch.isdigit() for ch in w) else len(w)) + 2; tot = sum(wl(w) for w in words); t = t0; tw = []
        for w in words: d = (end - t0) * wl(w) / tot; tw.append([w, round(t, 2), round(t + d, 2)]); t += d
        cur = []
        for w in tw:
            cur.append(w)
            if len(cur) == 3 or (len(cur) == 2 and len(' '.join(c[0] for c in cur)) > 16) or w[0][-1] in ',.?:':
                caps.append([cur[0][1], cur[-1][2], cur]); cur = []
        if cur: caps.append([cur[0][1], cur[-1][2], cur])
    json.dump(caps, open(f'caps_{L}.json', 'w'), ensure_ascii=False)
    print(L, B)
json.dump(out, open('beats.json', 'w'), indent=0)
