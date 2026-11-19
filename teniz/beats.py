"""Beat times from the whisper words -> beats.json; captions with per-word times -> caps_<lang>.json.
Each beat is the start of a sentence fragment (S below); its time = the first whisper word at or after the previous beat
whose text starts like the fragment's first word. Without words_<lang>.json the times are estimated (2.6 words/s)."""
import json, os, re, sys
S = {'ru': [('rec0', 'У Казахстана есть мировой рекорд, о котором почти никто не знает.'), ('f3', 'Три факта, и последний вас удивит.'),
            ('area', 'Казахстан девятый в мире по площади.'), ('eu', 'Сюда влезут пять крупных стран Европы.'),
            ('ocean', 'Но ни одного выхода к мировому океану.'), ('casp', 'Каспий не считается.'),
            ('rec', 'Это рекорд: мы самая большая страна без моря на планете.'),
            ('pole', 'Рядом с нашей границей — точка, самая далёкая от океана на Земле.'),
            ('far', 'До ближайшего моря отсюда около 2500 километров.'), ('alm', 'Это как от Алматы до Атырау,'), ('plus', 'и ещё 500 километров сверху.'),
            ('ent', 'Это бывает на ЕНТ:'), ('pos', 'положение Казахстана — внутриконтинентальное.'),
            ('uzb', 'А наш сосед Узбекистан —'), ('two', 'одна из двух стран мира, окружённых только странами без моря.'),
            ('cta', 'Перейдите по ссылке в шапке профиля.')],
     'kk': [('rec0', 'Қазақстанның әлемдік рекорды бар, оны көпшілік білмейді.'), ('f3', 'Үш дерек, соңғысы таң қалдырады.'),
            ('area', 'Қазақстан аумағы бойынша әлемде тоғызыншы.'), ('eu', 'Еуропаның бес ірі елі осыған сыяды.'),
            ('ocean', 'Бірақ дүниежүзілік мұхитқа бірде-бір шығатын жолы жоқ.'), ('casp', 'Каспий есепке кірмейді.'),
            ('rec', 'Міне, рекорд: біз — планетадағы теңізі жоқ ең үлкен ел.'),
            ('pole', 'Шекарамыздың жанында — Жер бетіндегі мұхиттан ең алыс нүкте.'),
            ('far', 'Бұдан ең жақын теңізге дейін шамамен екі жарым мың шақырым.'), ('alm', 'Бұл — Алматыдан Атырауға дейінгі қашықтық,'), ('plus', 'оған тағы 500 шақырым қосыңыз.'),
            ('ent', 'Бұл ҰБТ-да келеді:'), ('pos', 'Қазақстанның жағдайы — құрлықішілік.'),
            ('uzb', 'Ал көршіміз Өзбекстан —'), ('two', 'тек теңізі жоқ елдермен қоршалған әлемдегі екі елдің бірі.'),
            ('cta', 'Профиль шапкасындағы сілтемеге өтіңіз.')]}
PFX = {('kk', 'eu'): 1}   # whisper writes «Европаның»
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
