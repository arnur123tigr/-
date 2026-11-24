"""shapes.json for the New Year / date line reel (Natural Earth 10m, public domain). Pacific-centred: lon < 0 shifted by +360."""
import json, sys
sys.path.insert(0, '../_shared'); from geo import *
from shapely.geometry import shape, box, LineString
from shapely.ops import unary_union, linemerge
from shapely import affinity
def sh(g):   # shift western hemisphere east by 360
    a = g.intersection(box(-180, -90, 0, 90)); b = g.intersection(box(0, -90, 180, 90))
    return unary_union([affinity.translate(a, 360, 0), b]).buffer(0)
Z = [(f['properties']['zone'], shape(f['geometry']).buffer(0)) for f in feats('ne_10m_time_zones')]
S = {}
# time zones grouped by whole-hour zone (both raw coords; the scene draws them twice, +0 and +360)
G = {}
for z, g in Z: G.setdefault(z, []).append(g)
S['tz'] = [[z, rings(unary_union(gs), .15, .01)] for z, gs in sorted(G.items())]
# date line: shared boundary of zones >= +12 and zones <= -10 (Pacific-centred)
Wz = sh(unary_union([g for z, g in Z if z >= 11.9])); Ez = sh(unary_union([g for z, g in Z if z <= -9.9]))
L = Wz.boundary.intersection(Ez.buffer(.05)).intersection(box(150, -60, 230, 75))
L = linemerge([l for l in polys(L) if l.geom_type == 'LineString']) if L.geom_type != 'LineString' else L
pts = []
lat = 75.0
while lat >= -60:
    seg = Ez.intersection(LineString([(165, lat), (235, lat)]))
    if not seg.is_empty: pts.append((max(165, seg.bounds[0]), lat))
    lat -= .2
dl = [[round(x, 2), round(y, 2)] for x, y in LineString(pts).simplify(.08).coords]
north = [p for p in dl if p[1] >= 48]; south = [p for p in dl if p[1] <= -15.2]
# Kiribati / Samoa section (after 1995 / 2011), hand-placed between the islands
mid_new = [[180, -1.2], [197, -1.2], [197, 6.5], [210, 6.5], [210, -11.7], [189, -11.7], [189, -15], [187.5, -15]]
mid_old = [[180, -1.2], [180, -1.2], [180, -1.2], [180, -1.2], [180, -11.7], [180, -11.7], [180, -15], [187.5, -15]]
S['dl'] = north + mid_new + south; S['dl_old'] = north + mid_old + south
print('dateline pts', len(S['dl']), S['dl'][:3], S['dl'][-3:])
U = units(); C = countries()
for k in ['KIR', 'WSM', 'ASM', 'NZL', 'TON', 'FJI', 'TUV', 'FQI', 'HQI']:
    S[k] = rings(sh(U[k]), .005, 0)
# Kiritimati detailed
S['KIRI'] = rings(sh(C['KIR'].intersection(box(-158, 1.5, -157, 2.2))), .002, 0)
S['TARAWA'] = rings(sh(C['KIR'].intersection(box(172.8, 1.3, 173.3, 1.75))), .002, 0)
S['AUS'] = rings(C['AUS'], .1, .5)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
