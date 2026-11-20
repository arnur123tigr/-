"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('rec0', 'Тридцать три километра воды'), ('hold', 'держат в руках всю мировую экономику.'), ('horm', 'Это Ормузский пролив.'),
            ('kz', 'И он связан даже с Казахстаном.'), ('narrow', 'В самом узком месте пролив —'), ('talg', 'как от Алматы до Талгара и чуть дальше.'),
            ('oil', 'Через него идёт около пятой части'), ('all', 'всей нефти, которую потребляет мир.'), ('iran', 'С одной стороны Иран.'),
            ('close', 'Если пролив закроют,'), ('price', 'цены на бензин взлетят везде.'), ('kzq', 'А как продаёт нефть Казахстан?'),
            ('nosea', 'У нас ведь нет моря.'), ('pipe', 'По трубе длиной около полутора тысяч километров'), ('black', 'до Чёрного моря.'),
            ('pct', 'Так уходит около восьмидесяти процентов нашего экспорта нефти.'), ('ent', 'Это бывает на ЕНТ:'),
            ('west', 'главные месторождения нефти — на западе Казахстана.'), ('bos', 'Но танкеры с нашей нефтью идут через Босфор.'),
            ('width', 'Его ширина местами меньше километра.'), ('cta', 'Перейдите по ссылке в шапке профиля.')],
     'kk': [('rec0', 'Отыз үш шақырым су'), ('hold', 'бүкіл әлем экономикасын ұстап тұр.'), ('horm', 'Бұл — Ормуз бұғазы.'),
            ('kz', 'Ол тіпті Қазақстанмен де байланысты.'), ('narrow', 'Ең тар жерінде бұғаз'), ('talg', 'Алматыдан Талғарға дейінгідей, одан сәл ұзақ.'),
            ('oil', 'Әлем тұтынатын мұнайдың шамамен бестен бірі'), ('all', 'осы арқылы өтеді.'), ('iran', 'Бір жағында — Иран.'),
            ('close', 'Бұғаз жабылса,'), ('price', 'жанармай бағасы барлық жерде шарықтайды.'), ('kzq', 'Ал Қазақстан мұнайды қалай сатады?'),
            ('nosea', 'Бізде теңіз жоқ қой.'), ('pipe', 'Ұзындығы шамамен бір жарым мың шақырым құбырмен'), ('black', 'Қара теңізге дейін.'),
            ('pct', 'Мұнай экспортымыздың шамамен сексен пайызы осылай кетеді.'), ('ent', 'Бұл ҰБТ-да келеді:'),
            ('west', 'негізгі мұнай кен орындары Қазақстанның батысында.'), ('bos', 'Бірақ мұнайымыз тиелген танкерлер Босфор арқылы өтеді.'),
            ('width', 'Оның ені кей жерде бір шақырымға да жетпейді.'), ('cta', 'Профиль шапкасындағы сілтемеге өтіңіз.')]}
ALT = {('ru', 'hold'): 'держ', ('kk', 'hold'): 'б[үө]к', ('kk', 'all'): 'ос[аы]', ('kk', 'pipe'): '[оұ]зу|[оұ]зы', ('kk', 'nosea'): 'бізд'}
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
