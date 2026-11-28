"""shapes.json for the oldest-countries reel (Natural Earth 10m, public domain)."""
import json, sys
sys.path.insert(0, '../_shared'); from geo import *
C = countries(); U = units()
S = {}
for k in ['SDS', 'SAU', 'AUS', 'KAZ', 'ITA', 'EGY', 'IRN']: S[k] = rings(C[k], .02, .01)
S['USA'] = rings(C['USA'].intersection(box(-130, 20, -60, 52)), .03, .05)
S['ENG'] = rings(U['ENG'], .01, .005)
S['KOR'] = rings(unary_union([C['KOR'], C['PRK']]), .01, .005)
S['borders'] = []
for k, g in C.items(): S['borders'] += rings(g, .05, .05)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
