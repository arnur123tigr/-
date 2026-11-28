"""shapes.json for the UK/Britain/England reel (Natural Earth 10m map units, public domain)."""
import json, sys
sys.path.insert(0, '../_shared'); from geo import *
U = units(); C = countries()
S = {}
for k in ['ENG', 'SCT', 'WLS', 'NIR']: S[k] = rings(U[k], .01, .002)
S['IRL'] = rings(C['IRL'], .01, .002)
S['GB'] = rings(unary_union([U['ENG'], U['SCT'], U['WLS']]), .01, .002)
S['UK'] = rings(C['GBR'], .01, .002)
S['IRISL'] = rings(unary_union([C['IRL'], U['NIR']]), .01, .002)
S['ISLES'] = rings(unary_union([C['GBR'], C['IRL'], C.get('IMN', box(0, 0, 0, 0))]), .01, .002)
S['borders'] = []
for k in ['FRA', 'BEL', 'NLD', 'DEU', 'NOR', 'DNK', 'ESP', 'PRT', 'ISL']: S['borders'] += rings(C[k], .03, .01)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
