"""Beat times (voice seconds, read off the whisper words) -> beats.json; captions with per-word times -> caps_<lang>.json.
RAW is filled from words_<lang>.json (python3 beats.py --find prints candidate times for each key's anchor word)."""
import json, sys
KEYS = 'q s3 twist st1 lake4 ltu st2 cotton st3 ships kum aralkum wind ent cat dam kok north fish cta vend'.split()
S = {'ru': ['Куда за полвека исчезло целое море?', 'Это случилось в три шага.', 'А конец истории неожиданный.',
            'Шаг первый: в шестидесятых Арал был четвёртым озером мира.', 'Больше всей Литвы.',
            'Шаг второй: воду Сырдарьи и Амударьи забрали на хлопковые поля.', 'Шаг третий: море стало отступать.', 'Корабли остались прямо в песке.',
            'На дне появилась новая пустыня — Аралкум.', 'Ветер разносит отсюда соль и пыль.', 'Это бывает на ЕНТ:',
            'высыхание Арала — одна из главных экологических катастроф века.', 'Но в 2005 году Казахстан построил плотину Кокарал.',
            'И северная часть моря ожила.', 'Вода поднялась, и вернулась рыба.', None],
     'kk': ['Жарты ғасырда тұтас теңіз қайда жоғалды?', 'Бұл үш қадаммен болды.', 'Ал оқиғаның соңы күтпеген.',
            'Бірінші қадам: алпысыншы жылдары Арал әлемдегі төртінші көл еді.', 'Бүкіл Литвадан үлкен.',
            'Екінші қадам: Сырдария мен Әмудария суын мақта алқаптарына бұрды.', 'Үшінші қадам: теңіз шегіне бастады.', 'Кемелер құмның ортасында қалды.',
            'Түбінде жаңа шөл пайда болды — Аралқұм.', 'Жел бұдан тұз бен шаң таратады.', 'Бұл ҰБТ-да келеді:',
            'Аралдың тартылуы — ғасырдың ең ірі экологиялық апаттарының бірі.', 'Бірақ 2005 жылы Қазақстан Көкарал бөгетін салды.',
            'Теңіздің солтүстік бөлігі қайта тірілді.', 'Су көтеріліп, балық оралды.', None]}
# sentence index -> key whose time is the sentence start
SENT_KEY = ['q', 's3', 'twist', 'st1', 'ltu', 'st2', 'st3', 'ships', 'kum', 'wind', 'ent', 'cat', 'dam', 'north', 'fish', 'cta']
RAW = json.load(open('raw_beats.json'))   # {lang: {key: t}} incl. sentence starts and lake4/cotton/aralkum/kok/vend
out = {}
for L in RAW:
    out[L] = {k: RAW[L][k] for k in KEYS}
    W = json.load(open(f'words_{L}.json')); caps = []
    st = [RAW[L][k] for k in SENT_KEY]
    for s, t0, t1 in zip(S[L], st, st[1:]):
        if s is None: break
        end = max([w[1] for w in W if t0 - .05 <= w[0] < t1 - .05] or [t1 - .3])
        words = s.replace(' —', '').split(' '); tot = sum(len(w) + 2 for w in words); t = t0; tw = []
        for w in words: d = (end - t0) * (len(w) + 2) / tot; tw.append([w, round(t, 2), round(t + d, 2)]); t += d
        cur = []
        for w in tw:
            cur.append(w)
            if len(cur) == 3 or (len(cur) == 2 and len(' '.join(c[0] for c in cur)) > 16) or w[0][-1] in ',.?:':
                caps.append([cur[0][1], cur[-1][2], cur]); cur = []
        if cur: caps.append([cur[0][1], cur[-1][2], cur])
    json.dump(caps, open(f'caps_{L}.json', 'w'), ensure_ascii=False)
    print(L, len(caps), out[L]['vend'])
json.dump(out, open('beats.json', 'w'), indent=0)
