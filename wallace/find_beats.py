"""Find beats in words_<lang>.json by anchor word prefixes (in order). Usage: python3 find_beats.py -> raw_beats.json"""
import json, re
A = {'ru': [('q', None), ('s2', 'их'), ('worlds', 'два'), ('why', 'вот'), ('west0', 'на$'), ('west', 'западе'), ('monk', 'обезьян'), ('tig', 'тигр'), ('ele', 'слон'),
            ('east0', 'на$'), ('east', 'востоке'), ('mars', 'сумчат'), ('cock', 'кокаду|какаду'), ('wal', 'эту'), ('alf', 'альфред'), ('y150', '150|ста'),
            ('ice0', 'в$'), ('ice', 'ледник'), ('lvl', '120|сто'), ('bali', 'бали'), ('deep0', 'а$'), ('deep', 'пролив'), ('never', 'никогда'), ('walk', 'звери'), ('stop', 'стоп'),
            ('wall', 'стена'), ('birds', 'самое'), ('cross', 'пересека'), ('fly', 'летать'), ('cta', 'перейд')],
     'kk': [('q', None), ('s2', 'олардың'), ('worlds', 'екі'), ('why', 'себеб'), ('west', 'батыс'), ('monk', 'маймыл'), ('tig', 'жолбар'), ('ele', 'піл'),
            ('east', 'шығыс'), ('mars', 'қапшық'), ('cock', 'какаду'), ('wal', 'бұл'), ('y150', '150|жүз'), ('alf', 'альфред'),
            ('ice', 'мұз'), ('lvl', '120|жүз'), ('bali', 'бали'), ('deep0', 'ал'), ('deep', 'бали'), ('never', 'ешқашан'), ('walk', 'аңдар'), ('stop', 'тоқта'),
            ('wall', 'қабырға'), ('birds', 'ең'), ('cross', 'кесіп'), ('fly', 'өтбейді|өтпейді'), ('cta', 'профил')]}
out = {}
for L in A:
    W = json.load(open(f'words_{L}.json')); i = 0; r = {}
    for k, pre in A[L]:
        if pre is None: r[k] = 0.0; continue
        while not re.match(pre, W[i][2].lower().strip('.,?:!«»—–-')): i += 1
        r[k] = W[i][0]; i += 1
    for k in ('west0', 'east0', 'ice0'): r.setdefault(k, r[k[:-1]])
    r['vend'] = W[-1][1]; out[L] = r; print(L, r)
json.dump(out, open('raw_beats.json', 'w'))
