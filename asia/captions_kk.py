"""Kazakh captions: script text aligned to faster-whisper word times by character matching (difflib)."""
import json, re, difflib
MAIN = """Азияда 48 ел бар. Бірақ Таяу Шығыс қай жерде екенін білесің бе? Орталық Азияға қандай елдер кіреді? Ал Оңтүстік, Шығыс және Оңтүстік-Шығыс Азияның айырмашылығы неде? Кәне, түсініп көрейік!
Азия — Жердегі ең үлкен құрлық. Бұл планетадағы бүкіл құрлықтың үштен біріне жуық. Мұнда 5 миллиардқа жуық адам тұрады, ал олардың жартысына жуығы дәл осы жерде — Оңтүстік Азияда.
Оған Үндістан, Пәкістан, Ауғанстан, Бангладеш, Гималайдағы шағын елдер және Шри-Ланка мен Мальдив сияқты арал мемлекеттері кіреді.
Оңтүстік Азияның солтүстігінде атауы «стан» деп аяқталатын елдер орналасқан: Қазақстан, Өзбекстан және басқалары. Ауғанстан мен Пәкістаннан басқа барлық «стандар» — Орталық Азия.
Ал алып таулардың — Гималай мен Тянь-Шаньның арғы жағында Шығыс Азия жатыр: Қытай, Моңғолия, Солтүстік және Оңтүстік Корея, Жапония және Тайвань.
Ал мына жердің бәрі — Оңтүстік-Шығыс Азия: Вьетнам, Тайланд, олардың құрлықтағы көршілері және Индонезия, Филиппин сияқты арал елдері.
Ал алыс солтүстікте — Ресей. Біріккен Ұлттар Ұйымы бүкіл елді Еуропаға жатқызады, бірақ оның аумағының шамамен 77% Азияда жатыр. Сондықтан бұл бөлікті жиі Солтүстік Азия деп атайды.
Ақырында — Таяу Шығыс. Қызық: Азияның ең батыс бөлігін «Шығыс» деп атайды! Өйткені бұл атауды еуропалықтар ойлап тапқан. Олар үшін Қытай мен Жапония — Қиыр Шығыс, ал бұл аймақ — Таяу Шығыс болды.
Оған Иран, Ирак, Сауд Арабиясы, Израиль, Палестина және басқа елдер кіреді. Географиялық тұрғыдан бұл — Батыс Азия. Бірақ «Таяу Шығыс» дегенде, көбіне Мысырды да қосады, ал ол толығымен дерлік Африкада орналасқан.
Енді сен білесің."""
SPOKEN = {'48': 'қырықсегіз', '5': 'бес', '77%': 'жетпісжетіпайызы'}   # how numbers sound, for matching only
norm = lambda s: re.sub(r'[^а-яәіңғүұқөһё]', '', s.lower())
W = json.load(open('words_kk.json'))
# whisper char stream with times
hs, ht = '', []
for s, e, w in W:
    n = norm(w)
    for i, ch in enumerate(n): hs += ch; ht.append(s + (e - s) * i / max(1, len(n)))
words = [w for w in MAIN.split() if w != '—']
ss, owner = '', []
for i, w in enumerate(words):
    n = norm(SPOKEN.get(w, w))
    for ch in n: ss += ch; owner.append(i)
sm = difflib.SequenceMatcher(None, ss, hs, autojunk=False)
ct = [None] * len(ss)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): ct[a + k] = ht[b + k]
# word start = first matched char; interpolate gaps
wt = [None] * len(words)
for ci, t in enumerate(ct):
    if t is not None and wt[owner[ci]] is None: wt[owner[ci]] = t
known = [(i, t) for i, t in enumerate(wt) if t is not None]
for i in range(len(words)):
    if wt[i] is None:
        lo = max([k for k in known if k[0] < i], default=(0, 0.0)); hi = min([k for k in known if k[0] > i], default=(len(words), 110.1))
        wt[i] = lo[1] + (hi[1] - lo[1]) * (i - lo[0]) / (hi[0] - lo[0])
for i in range(1, len(wt)): wt[i] = max(wt[i], wt[i - 1] + 0.05)
# re-attach dashes to the previous word for display
disp = []; j = 0
for w in MAIN.split():
    if w == '—': disp[-1][1] += ' —'; continue
    disp.append([wt[j], w]); j += 1
caps, cur = [], []
for t, w in disp:
    cur.append([round(t, 2), w]); L = len(' '.join(x[1] for x in cur))
    if w[-1] in '.?!:' or L > 20 or (w[-1] in ',—' and L > 12): caps.append(cur); cur = []
if cur: caps.append(cur)
out = [{'s': c[0][0], 'e': c[-1][0] + 0.6, 'w': c} for c in caps]
for a, b in zip(out, out[1:]): a['e'] = min(b['s'], a['e'])
out[-1]['e'] = 110.5
json.dump(out, open('captions_kk.json', 'w'), ensure_ascii=False)
for c in out[:200]: print(f"{c['s']:6.2f} {' '.join(x[1] for x in c['w'])}")
