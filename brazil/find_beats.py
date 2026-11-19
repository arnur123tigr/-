"""Find beats in words_<lang>.json by anchor word prefixes (in order). Usage: python3 find_beats.py dir -> dir/raw_beats.json"""
import json, sys, re
D = sys.argv[1] if len(sys.argv) > 1 else '.'
A = {'ru': [('q', None), ('why', 'почему'), ('s2', 'всё|все'), ('steps', 'три|3'), ('st1', 'шаг$'), ('argue', 'спорил'), ('st2', 'шаг$'), ('split', 'раздел'),
            ('west', 'запад'), ('east', 'восток'), ('st3', 'шаг$'), ('edge', 'оказ'), ('c1500', 'в$|1500'), ('grow', 'а$'), ('far', 'далеко'), ('fifth', 'так'),
            ('ent', 'это'), ('disc', 'велик'), ('twist', 'сегодня'), ('x20', 'двадцат|20'), ('ptg', 'португалии'), ('cta', 'перейд')],
     'kk': [('q', None), ('why', 'неге'), ('s2', 'бәрін'), ('steps', 'үш|3'), ('st1', 'бірінші|1'), ('argue', 'талас'), ('st2', 'екінші|2'), ('split', 'әлемді'),
            ('west', 'батыс|батс'), ('east', 'шығыс'), ('st3', 'үшінші|3'), ('edge', 'шеті'), ('c1500', 'мың|1500'), ('grow', 'кейін|кеин'), ('far', 'батыс|батс'), ('fifth', 'бразилия'),
            ('ent', 'бұл'), ('disc', 'ұлы|олы'), ('twist', 'бүгін|бұгің|бүгің'), ('ptg', 'португалия|партугалия'), ('x20', 'жиырма|жірма|20'), ('cta', 'профил')]}
out = {}
for L in A:
    W = json.load(open(f'{D}/words_{L}.json')); i = 0; r = {}
    for k, pre in A[L]:
        if pre is None: r[k] = 0.0; continue
        while not re.match(pre, W[i][2].lower().strip('.,?:!«»—-')): i += 1
        r[k] = W[i][0]; i += 1
    r['vend'] = W[-1][1]; out[L] = r; print(L, r)
json.dump(out, open(f'{D}/raw_beats.json', 'w'))
