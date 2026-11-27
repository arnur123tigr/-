import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['mk', 'stars', 'r1', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['yes', 'no', 'km10', 'd9', 'km2', 'r1', 'r2', 'r3', 'three', 'link']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
