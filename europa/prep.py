"""shapes.json for the Europe-regions reel (Natural Earth 10m, public domain)."""
import json, sys
sys.path.insert(0, '../_shared'); from geo import *
from shapely.geometry import LineString, Polygon
C = countries()
EU = 'ALB AND AUT BEL BGR BIH BLR CHE CZE DEU DNK ESP EST FIN FRA GBR GRC HRV HUN IRL ISL ITA KOS LIE LTU LUX LVA MCO MDA MKD MLT MNE NLD NOR POL PRT ROU SMR SRB SVK SVN SWE UKR VAT'.split()
ural = [f for f in feats('ne_10m_rivers_lake_centerlines') if f['properties'].get('name') == 'Ural']
ural = max((shape(f['geometry']) for f in ural), key=lambda g: g.length)
m = linemerge(ural) if ural.geom_type == 'MultiLineString' else ural
m = max(polys(m), key=lambda g: g.length); uc = list(m.coords)
if uc[0][1] < uc[-1][1]: uc = uc[::-1]          # north -> south (to the Caspian)
URM = [(66.5, 69.2), (64.5, 67.6), (60.3, 65.2), (59.4, 62.5), (59.6, 60.0), (59.2, 57.5), (59.0, 55.5), (59.3, 54.6)]
UR = [list(p) for p in URM] + [[x, y] for x, y in uc if y < 54.6]
# Europe's east boundary polygon (west side): Ural mts + Ural river + Caspian + Caucasus + Bosporus
CAU = [(46.5, 42.2), (44.5, 42.7), (42.5, 43.2), (40.0, 43.5), (38.5, 44.4), (37.0, 45.1)]
bound = UR + [[51.5, 45.5], [49.5, 44.0], [48.3, 41.9]] + [list(p) for p in CAU] + [[33, 44], [29.1, 41.3], [26.0, 40.0], [20, 34]]
euro_poly = Polygon([(70, 80), (-30, 80), (-30, 34), (20, 34)] + [(a, b) for a, b in bound[::-1]]).buffer(0)
S = {'URAL_MTS': [list(p) for p in URM], 'URAL_RIV': [[round(x, 2), round(y, 2)] for x, y in uc if y < 54.6], 'CAUC': [list(p) for p in CAU]}
for k in EU + ['RUS', 'KAZ', 'TUR']: S[k] = rings(C[k] if k not in ('RUS', 'NOR') else C[k].intersection(box(-30, 34, 70, 72)), .03, .004)
S['RUS_EU'] = rings(C['RUS'].intersection(euro_poly), .04, .01); S['KAZ_EU'] = rings(C['KAZ'].intersection(euro_poly), .03, .01); S['TUR_EU'] = rings(C['TUR'].intersection(euro_poly), .02, .005)
S['EUROPE'] = rings(unary_union([C[k] for k in EU] + [C['RUS'].intersection(euro_poly), C['KAZ'].intersection(euro_poly), C['TUR'].intersection(euro_poly)]).buffer(.03), .05, .05)
S['EURASIA'] = rings(unary_union([f for f in [shape(x['geometry']).buffer(0) for x in feats('ne_10m_land')] if f.intersects(box(60, 40, 61, 41)) or f.intersects(box(10, 50, 11, 51))]).intersection(box(-30, -15, 180, 82)), .15, .5)
S['BALKAN'] = rings(region('BALKAN PEN.'), .05, .1)
S['SCAND'] = rings(region('SCANDINAVIA'), .05, .1)
S['borders'] = []
for k, g in C.items():
    b = g.bounds
    if b[2] > -30 and b[0] < 80 and b[3] > 30 and b[1] < 80: S['borders'] += rings(g, .04, .02)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
