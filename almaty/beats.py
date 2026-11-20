"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('h1', 'Почему землетрясения бывают в Алматы, а в Астане почти нет?'), ('cul', 'Виновник находится очень далеко.'),
            ('steps', 'Разберём по шагам.'), ('s1', 'Шаг первый: город стоит у подножия Тянь-Шаня.'), ('grow', 'Эти горы до сих пор растут.'),
            ('s2', 'Шаг второй: Индия каждый год врезается в Азию.'), ('cm', 'Примерно на 4–5 сантиметров в год.'), ('nail', 'Так растут ногти.'),
            ('s3', 'Шаг третий: этот удар доходит почти на 2000 километров.'), ('alm', 'Прямо до Алматы.'),
            ('hist', 'Город уже дважды почти разрушали:'), ('y1', 'в 1887-м'), ('y2', 'и в 1911-м.'),
            ('ent', 'Это бывает на ЕНТ:'), ('zone', 'сейсмоопасны юг и восток,'), ('plate', 'а центр стоит на древней плите.'),
            ('turn', 'Получается, Алматы трясёт из-за страны, с которой у нас даже нет границы.'),
            ('cta', 'Перейдите по ссылке в шапке профиля.')],
     'kk': [('h1', 'Неге жер сілкінісі Алматыда болады, ал Астанада жоқтың қасы?'), ('cul', 'Кінәлі өте алыста.'),
            ('steps', 'Қадам бойынша талдайық.'), ('s1', 'Бірінші қадам: қала Тянь-Шань етегінде тұр.'), ('grow', 'Бұл таулар әлі де өсіп жатыр.'),
            ('s2', 'Екінші қадам: Үндістан жыл сайын Азияға соғылып жатыр.'), ('cm', 'Жылына шамамен 4–5 сантиметр.'), ('nail', 'Тырнақ осылай өседі.'),
            ('s3', 'Үшінші қадам: бұл соққы шамамен 2000 шақырымға жетеді.'), ('alm', 'Тура Алматыға дейін.'),
            ('hist', 'Қаланы екі рет қирата жаздады:'), ('y1', '1887'), ('y2', 'және 1911 жылдары.'),
            ('ent', 'Бұл ҰБТ-да келеді:'), ('zone', 'оңтүстік пен шығыс сейсмикалық қауіпті,'), ('plate', 'ал орталық ежелгі тақтада тұр.'),
            ('turn', 'Сонда Алматыны бізбен шекарасы да жоқ ел сілкіндіріп тұр.'),
            ('cta', 'Профиль шапкасындағы сілтемеге өтіңіз.')]}
PFX = {('kk', 'cm'): 6}
ALT = {('kk', 's1'): '1', ('kk', 's2'): '2', ('kk', 's3'): '3', ('kk', 'zone'): 'ұң', ('kk', 'cul'): 'кін', ('kk', 'alm'): 'тұр'}
EX = {('ru', 's1'), ('ru', 's2'), ('ru', 's3')}   # whole-word match («Шаг», not «шагам»)   # how whisper wrote the first word
norm = lambda s: re.sub(r'[^\wәғқңөұүһі]', '', s.lower().replace('ё', 'е'))
out = json.load(open('beats.json')) if os.path.exists('beats.json') else {}
for L in sys.argv[1:] or ('ru', 'kk'):
    seq = S[L]; fn = f'words_{L}.json'
    if os.path.exists(fn):
        W = json.load(open(fn)); B = {}; i = 0
        for k, s in seq:
            w0 = ALT.get((L, k)) or norm(s.split()[0])[:PFX.get((L, k), 3)]
            j = next((j for j in range(i, len(W)) if (norm(W[j][2]) == w0 if (L, k) in EX else norm(W[j][2]).startswith(w0))), None)
            if j is None: sys.exit(f'{L}: no word for {k} ({s.split()[0]}) after {W[i][0] if i < len(W) else "end"}')
            B[k] = W[j][0] if k != 'h1' else 0.0; i = j + 1
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
