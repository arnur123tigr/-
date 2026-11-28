"""shapes.json for the snowiest-country reel (Natural Earth 10m, public domain)."""
import json, sys
sys.path.insert(0, '../_shared'); from geo import *
from shapely.geometry import shape
C = countries()
A1 = {f['properties']['name']: shape(f['geometry']).buffer(0) for f in feats('ne_10m_admin_1_states_provinces') if f['properties']['adm0_a3'] in ('JPN', 'CAN')}
S = {}
for k in ['NOR', 'SWE', 'FIN', 'ISL', 'DNK']: S[k] = rings(C[k], .03, .01)
S['GRL'] = rings(C['GRL'], .05, .05); S['JPN'] = rings(C['JPN'], .01, .003); S['CAN'] = rings(C['CAN'], .08, .3)
S['CANN'] = sum((rings(A1[n], .08, .3) for n in ['Yukon', 'Northwest Territories', 'Nunavut']), [])
for n in ['Niigata', 'Yamagata', 'Aomori', 'Shiga', 'Gifu']: S[n] = rings(A1[n], .005, .002)
S['borders'] = []
for k in ['RUS', 'CHN', 'KOR', 'PRK', 'MNG', 'EST', 'LVA', 'DEU', 'POL', 'USA']: S['borders'] += rings(C[k], .05, .05)
S['jpref'] = []
for n, g in A1.items():
    if any(abs(c[0]) > 0 and c[0] > 125 for c in g.representative_point().coords): S['jpref'] += rings(g, .01, .003)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
