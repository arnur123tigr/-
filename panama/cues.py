import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['pan', 'baru', 'how', 'morn', 'clear', 'if', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['rise', 'atl', 'num', 's', 'we', 'pac', 'car', 'both', 'link']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
