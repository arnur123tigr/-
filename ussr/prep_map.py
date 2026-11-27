"""Map shapes for the USSR reel (run once after fetch_data.sh): shapes.json
  borders   Natural Earth land borders inside the frame box (thin lines)
  rep       the 15 Soviet republics (Natural Earth 10m countries, today's borders = the SSR borders of 1991), rings per republic
  ussr      the outline of the whole union (union of the 15)
  land      area check: USSR share of the world's land (printed)
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from karagie/ (<- tyn/ <- kulja/ <- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
Usage: python3 prep_map.py"""
import json
from shapely.geometry import shape
from shapely.ops import unary_union

REP = {'lt': 'Lithuania', 'lv': 'Latvia', 'ee': 'Estonia', 'ua': 'Ukraine', 'by': 'Belarus', 'md': 'Moldova', 'ge': 'Georgia',
       'kg': 'Kyrgyzstan', 'uz': 'Uzbekistan', 'tj': 'Tajikistan', 'tm': 'Turkmenistan', 'am': 'Armenia', 'az': 'Azerbaijan',
       'kz': 'Kazakhstan', 'ru': 'Russia'}
BOX = (5, 180, 30, 82)


def lines(geom):
    t = geom['type']; c = geom['coordinates']
    return {'LineString': [c], 'MultiLineString': c, 'Polygon': [c[0]], 'MultiPolygon': [p[0] for p in c]}.get(t, [])
def inbox(r, b=BOX): return any(b[0] <= x <= b[1] and b[2] <= y <= b[3] for x, y in r)
def rnd(r, k=3): return [[round(x, k), round(y, k)] for x, y in r]
def rings(g, tol, amin):
    g = g.simplify(tol, preserve_topology=True)
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [rnd(list(p.exterior.coords)) for p in polys if p.area > amin]


out = {'borders': [], 'rep': {}, 'cen': {}}
for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
    for r in lines(f['geometry']):
        if inbox(r): out['borders'].append(rnd(r[::2] + [r[-1]] if len(r) > 6 else r))
geo = {}
for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
    a = f['properties']['ADMIN']
    for k, n in REP.items():
        if a == n: geo[k] = shape(f['geometry']).buffer(0)
for k, g in geo.items():
    big = k in ('ru', 'kz', 'ua')
    out['rep'][k] = rings(g, .06 if k == 'ru' else .025 if big else .012, .4 if k == 'ru' else .01)
    p = g.representative_point(); out['cen'][k] = [round(p.x, 2), round(p.y, 2)]
u = unary_union(list(geo.values())).buffer(.05).buffer(-.05)
out['ussr'] = rings(u, .06, .4)
json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
print({k: sum(len(r) for r in v) for k, v in out['rep'].items()}, 'borders', len(out['borders']), 'cen', out['cen'])
