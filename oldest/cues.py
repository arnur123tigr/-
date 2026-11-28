import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['start', 'sau', 'aus', 'usa', 'kaz', 'eng', 'old', 'rome', 'kor', 'egy', 'iran', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['y15', 'y94', 'y125', 'y250', 'y561', 'y1100', 'y2800', 'y4300', 'y5100', 'y5200', 'link']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
