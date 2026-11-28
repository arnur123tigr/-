import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['map', 'put', 'fact', 'but', 'why', 'fin', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['ninth', 'mln', 'irl', 'tur', 'deu', 'fra', 'gbr', 'esp', 'swe', 'nor', 'west', 'east', 'n20', 'rou', 'steppe', 'semi', 'desert', 'ent']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
