import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['nordic', 'grl', 'can', 'but', 'jap', 'pref', 'aom', 'rec', 'wall', 'lat', 'geo', 'sib', 'mtn', 'snowfall', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['norw', 'm13', 'temp', 'north', 'yam', 'm58', 'aom2', 'm8', 'ibuki', 'm12', 'floors', 'lat2', 'nosnow', 'sea', 'rise', 'link']],
     'ding': [B['jap'] + .2, B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
