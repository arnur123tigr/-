import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['parts', 'c70', 'col', 'sec', 'field', 'west', 'north', 'south', 'east', 'who', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['rain', 'fog', 'sun', 'hail', 'wind', 'd250', 'no', 'mm', 'gulf', 'arc', 'dry', 'link']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
