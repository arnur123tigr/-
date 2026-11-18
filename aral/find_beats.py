"""Find raw beats from words_<lang>.json by anchor word prefixes (in order). Usage: python3 find_beats.py dir -> dir/raw_beats.json"""
import json, sys, re
D = sys.argv[1]
A = {'ru': [('q', None), ('s3', 'это'), ('twist', 'а'), ('st1', 'шаг'), ('lake4', 'четв'), ('ltu', 'больше'), ('st2', 'шаг'), ('cotton', 'хлоп'),
            ('st3', 'шаг'), ('ships', 'корабл'), ('kum', 'на'), ('aralkum', 'ор|ар'), ('wind', 'ветер'), ('ent', 'это'), ('cat', 'высых'),
            ('dam', 'но'), ('kok', 'плотин'), ('north', 'и'), ('fish', 'вернул'), ('cta', 'перейд')],
     'kk': [('q', None), ('s3', 'бұл'), ('twist', 'ал'), ('st1', 'бірінші'), ('lake4', 'төрт'), ('ltu', 'бү'), ('st2', 'екінші'), ('cotton', 'мақта'),
            ('st3', 'үшінші'), ('ships', 'кеме'), ('kum', 'т'), ('aralkum', 'арал'), ('wind', 'жел'), ('ent', 'бұл'), ('cat', 'аралдың'),
            ('dam', 'бірақ'), ('kok', 'көк|бөг|бұғ'), ('north', 'тең|тен'), ('fish', 'ба'), ('cta', 'профил')]}
out = {}
for L in A:
    W = json.load(open(f'{D}/words_{L}.json')); i = 0; r = {}
    for k, pre in A[L]:
        if pre is None: r[k] = 0.0; continue
        while not re.match(pre, W[i][2].lower().strip('.,?:!«»—-')): i += 1
        r[k] = W[i][0]; i += 1
    r['vend'] = W[-1][1]; out[L] = r; print(L, r)
json.dump(out, open(f'{D}/raw_beats.json', 'w'))
