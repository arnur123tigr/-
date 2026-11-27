import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['seems', 'smaller', 'merc', 'north', 'kz', 'real', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['why', 'oslo', 'afr1', 'no', 'km1', 'second', 'grl1', 'n14', 'shapes', 'sizes', 'x2', 'link']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
