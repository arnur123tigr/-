"""shapes.json for the Yuan reel: land (to clip the empire fills to the coast), faint modern borders, the empire outlines (approximate, hand drawn).
Usage: python3 prep_shapes.py   (needs data/ne_50m_*.geojson, see fetch_data.sh)"""
import json
BOX = (5, 150, 8, 68)
def rnd(r): return [[round(x, 3), round(y, 3)] for x, y in r]
def inbox(r): return any(BOX[0] <= x <= BOX[1] and BOX[2] <= y <= BOX[3] for x, y in r)
def lines(g):
    t, c = g['type'], g['coordinates']
    if t == 'LineString': return [c]
    if t == 'MultiLineString': return c
    if t == 'Polygon': return c
    if t == 'MultiPolygon': return [r for p in c for r in p]
    return []
out = {'land': [], 'borders': []}
for f in json.load(open('data/ne_50m_land.geojson'))['features']:
    for r in lines(f['geometry']):
        if inbox(r) and len(r) > 12: out['land'].append(rnd(r))
for f in json.load(open('data/ne_50m_admin_0_boundary_lines_land.geojson'))['features']:
    out['borders'] += [rnd(r) for r in lines(f['geometry']) if inbox(r)]
# the Mongol Empire about 1279 (all four uluses) and the Yuan; the Southern Song conquered 1235-1279 (approximate, generous to the sea: the land clips the coast)
out['mongol'] = [[[27, 46], [29, 50], [33, 54], [39, 57], [47, 58.5], [55, 60], [63, 58.5], [72, 57], [82, 56], [92, 54], [100, 53], [108, 54], [116, 53.5], [124, 52.5], [131, 48.5], [133, 44], [128, 41], [126, 39], [124, 38.5], [122, 35], [123, 30], [121, 26], [117, 22], [110, 18], [107, 21], [104, 22], [100, 21.5], [98, 25], [97, 28], [92, 28], [86, 28], [80, 30], [75, 33.5], [70, 33], [65, 29], [60, 25], [55, 26], [50, 28], [47, 30], [43, 33], [40, 36], [37, 37.5], [36, 39.5], [39, 41], [36, 42.5], [32, 44.5], [27, 46]]]
out['yuan'] = [[[87, 48.5], [92, 51], [98, 51.5], [106, 52], [116, 53.5], [124, 52.5], [131, 48.5], [133, 44], [128, 41], [126, 39], [124, 38.5], [122, 35], [123, 30], [121, 26], [117, 22], [110, 18], [107, 21], [104, 22], [100, 21.5], [98, 25], [97, 28], [92, 28], [86, 28], [80.5, 31], [79, 35], [83, 37], [89, 40], [92, 44], [87, 48.5]]]
out['song'] = [[[117, 22], [121, 26], [123, 30], [121.5, 33], [116, 32.8], [112, 32.4], [108, 33], [105, 32.5], [103, 30], [102, 27], [104, 24.5], [104, 22], [107, 21], [110, 18], [117, 22]]]
json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in out.items()})
