import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.2, 2),
     'whoosh': [B[k] for k in ['earth', 'line', 'hide', 'vil', 'why', 'after', 'lastp', 'some', 'bh', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['first', 'n24', 'idl', 'kir', 'n130', 'banana', 'london', 'paris', 'poland', 'cap', 'ban2', 'moved', 'nz', 'aus', 'asia', 'eur', 'afr', 'amer', 'asm', 'k70', 'wsm', 'diff', 'sut2', 'baker', 'how', 'hour', 'ent']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
