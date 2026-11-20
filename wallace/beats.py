"""raw_beats.json -> beats.json; captions (2-3 words, per-word times) -> caps_<lang>.json.
Caption text is the script text; a token 'X|n' stands for n spoken (whisper) words."""
import json, re
S = {'ru': ['Между этими островами есть стена, которую никто не видит.', 'Их разделяет около 35|1 километров. Но это два разных мира. Вот почему.',
            'На западе азиатские звери: обезьяны, тигры, слоны.', 'На востоке родня австралийских: сумчатые и какаду.',
            'Эту границу заметил учёный Альфред Уоллес больше 150|1 лет назад.', 'В ледниковый период море было ниже метров на 120.|1 Бали стал частью Азии.',
            'А пролив между Бали и Ломбоком слишком глубокий. Он не высох никогда.', 'Звери пешком дошли до Бали, а дальше стоп. Стена сделана из воды.',
            'Самое странное: многие птицы тоже не пересекают эту линию, хотя умеют летать.', None],
     'kk': ['Осы аралдардың арасында ешкім көрмейтін қабырға бар.', 'Олардың арасы шамамен 35 шақырым. Бірақ бұл екі бөлек әлем. Себебі мынада.',
            'Батыста азиялық аңдар: маймыл, жолбарыс, піл.', 'Шығыста австралиялықтардың туыстары: қапшықтылар мен какаду.',
            'Бұл шекараны 150 жылдан астам бұрын ғалым Альфред Уоллес байқаған.', 'Мұз басу кезеңінде теңіз деңгейі 120 метрдей төмен болды. Бали Азияның бір бөлігіне айналды.',
            'Ал Бали мен Ломбок арасындағы бұғаз тым терең. Ол ешқашан құрғамаған.', 'Аңдар Балиге жаяу жетті, ал әрі қарай тоқта. Қабырға судан жасалған.',
            'Ең қызығы: көптеген құстар ұша алса да, бұл сызықты кесіп өтпейді.', None]}
SENT_KEY = ['q', 's2', 'west0', 'east0', 'wal', 'ice0', 'deep0', 'walk', 'birds', 'cta']
RAW = json.load(open('raw_beats.json')); out = {}
for L in RAW:
    out[L] = RAW[L]; W = [w for w in json.load(open(f'words_{L}.json')) if re.search(r'\w', w[2])]; caps = []
    st = [RAW[L][k] for k in SENT_KEY]
    for s, t0, t1 in zip(S[L], st, st[1:]):
        if s is None: break
        sw = [w for w in W if t0 - .05 <= w[0] < t1 - .05]
        toks = [w for w in s.split(' ') if w != '—']; toks = [(w.split('|')[0], int(w.split('|')[1]) if '|' in w else 1) for w in toks]
        tw = []
        if sum(n for _, n in toks) == len(sw):
            i = 0
            for w, n in toks: tw.append([w, sw[i][0], sw[i + n - 1][1]]); i += n
        else:   # spread over the sentence's spoken span by word length
            beg = sw[0][0] if sw else t0; end = max([w[1] for w in sw] or [t1 - .3]); tot = sum(len(w) + 2 for w, _ in toks); t = beg
            for w, _ in toks: d = (end - beg) * (len(w) + 2) / tot; tw.append([w, round(t, 2), round(t + d, 2)]); t += d
            print('spread', L, s[:30])
        cur = []
        for w in tw:
            cur.append(w)
            if len(cur) == 3 or (len(cur) == 2 and len(' '.join(c[0] for c in cur)) > 16) or w[0][-1] in ',.?:':
                caps.append([cur[0][1], cur[-1][2], cur]); cur = []
        if cur: caps.append([cur[0][1], cur[-1][2], cur])
    json.dump(caps, open(f'caps_{L}.json', 'w'), ensure_ascii=False); print(L, len(caps), out[L]['vend'])
json.dump(out, open('beats.json', 'w'), indent=0)
