"""shapes.json for the Kazakhstan-size reel (Natural Earth 10m, public domain)."""
import json, sys
from math import cos, radians
sys.path.insert(0, '../_shared'); from geo import *
C = countries(); K = C['KAZ']
S = {}
for k in ['KAZ', 'DEU', 'FRA', 'GBR', 'ESP', 'SWE', 'NOR', 'ROU', 'IRL', 'TUR']: S[k] = rings(C[k] if k != 'FRA' else C[k].intersection(box(-6, 41, 10, 52)), .02, .003)
S['NOR'] = rings(C['NOR'].intersection(box(0, 55, 35, 72)), .02, .003)
def move(g, dlon, dlat):   # move keeping true size: x in km-ish preserved
    lon0, lat0 = g.centroid.x, g.centroid.y
    def f(x, y, z=None):
        return (lon0 + dlon + (x - lon0) * cos(radians(y)) / cos(radians(y + dlat)), y + dlat)
    from shapely.ops import transform
    return transform(lambda x, y, z=None: tuple(zip(*[f(a, b) for a, b in zip(x, y)])) if hasattr(x, '__len__') else f(x, y), g)
KE = move(K, -55.2, -2.6); S['KAZ_EU'] = rings(KE, .02, .003); print('KZ over Europe bounds', [round(v, 1) for v in KE.bounds])
S['DLON'] = [-55.2, -2.6]
S['borders'] = []
for k, g in C.items():
    b = g.bounds
    if b[2] > -25 and b[0] < 100 and b[3] > 30 and b[1] < 72 and k != 'KAZ': S['borders'] += rings(g, .04, .02)
R = lambda n: region(n).intersection(K)
S['steppe'] = rings(R('KAZAKH STEPPE').union(R('KAZAKH UPLAND')), .05, .05)
S['semi'] = rings(R('CASPIAN DEPRESSION').union(R('TURAN LOWLAND').difference(region('QIZILQUM DESERT'))), .05, .05)
S['desert'] = rings(R('BETPAQDALA DESERT').union(R('QIZILQUM DESERT')).union(R('Ustyurt Plateau')), .05, .05)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
