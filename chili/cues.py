import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['long', 'cmp', 'narrow', 'how', 'look1', 'mid', 'war', 'exp', 'geo', 'north', 'hey', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['no', 'this2', 'lon', 'bag', 'xv', 'euro', 'live', 'spa', 'por', 'chl', 'like', 'east', 'oy', 'south', 'ocean', 'andes', 'bol', 'per', 'coast', 'ent']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
