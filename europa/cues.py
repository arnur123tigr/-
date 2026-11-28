import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['go', 'eur', 'bound', 'part', 'cold', 'today', 'slav', 'but', 'balt2', 'balk2', 'south', 'north', 'broad', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['west', 'east', 'scand', 'nord', 'balt', 'balk', 'atl', 'urm', 'urr', 'kaz', 'casp', 'cauc', 'bosp', 'tur', 'curt', 'ideo', 'deu', 'aut', 'ita', 'pol', 'cze', 'svk', 'ukr', 'blr', 'rus2', 'est', 'lva', 'ltu', 'prt', 'esp', 'ita2', 'grc', 'nor', 'swe', 'dnk', 'fin', 'isl', 'ent']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
