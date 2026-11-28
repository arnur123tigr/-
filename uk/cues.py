import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['think', 'look', 'int', 'what', 'rem', 'isl', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['uk', 'brit', 'eng', 'irl', 'nir', 'e1', 's1', 'w1', 'gbsay', 'uksay', 'plus', 'lon', 'pop', 'r1', 'r2', 'r3', 'bi', 'ent']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
