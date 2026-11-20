"""Find beats in words_<lang>.json by anchor word prefixes (in order). Usage: python3 find_beats.py dir -> dir/raw_beats.json"""
import json, sys, re
D = sys.argv[1] if len(sys.argv) > 1 else '.'
A = {'ru': [('q', None), ('s2', 'есть'), ('f1', 'первый'), ('km', 'около'), ('lon', 'это'), ('f2', 'второй'), ('nine', 'почти'), ('split', 'но$'),
            ('alaska', 'аляска'), ('f3', 'третий'), ('one', 'одним'), ('rec', 'это'), ('ent', 'это'), ('five', '5|пять'), ('rus', 'росси'),
            ('dem', 'и$'), ('posts', 'столб'), ('cta', 'перейд')],
     'kk': [('q', None), ('s2', 'мұнда'), ('f1', 'біріншіс'), ('km', 'шамамен'), ('lon', 'бұл'), ('f2', 'екінші'), ('nine', '9|тоғыз'), ('split', 'бірақ'),
            ('alaska', 'аляска'), ('f3', 'үшінші'), ('one', 'тұтас'), ('rec', 'бұл'), ('ent', 'бұл'), ('five', 'без|бес|5'), ('rus', 'ресей'),
            ('dem', 'осы'), ('posts', 'баған'), ('cta', 'профил')]}
out = {}
for L in A:
    W = json.load(open(f'{D}/words_{L}.json')); i = 0; r = {}
    for k, pre in A[L]:
        if pre is None: r[k] = 0.0; continue
        while not re.match(pre, W[i][2].lower().strip('.,?:!«»—-')): i += 1
        r[k] = W[i][0]; i += 1
    r['vend'] = W[-1][1]; out[L] = r; print(L, r)
json.dump(out, open(f'{D}/raw_beats.json', 'w'))
