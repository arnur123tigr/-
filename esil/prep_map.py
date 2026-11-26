"""Map assets for the Esil -> Irtysh -> Ob reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from tyn/ (<- kulja/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  the whole river route, lon 60..90, lat 45..74, 100 px/deg, relief from Terrarium z7
  tex/city.jpg    Astana close-up, lon 69..74, lat 50..52.5, 240 px/deg (Blue Marble native), relief z9
  shapes.json     borders, Kazakhstan outline, rivers (Esil, Irtysh, Ob + Ob Gulf, Tobol) as ordered source -> mouth lines, Lake Zaysan
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, Point
from shapely.ops import linemerge, unary_union
import mapkit as mk
DETAIL = (60.0, 90.0, 45.0, 74.0, 100, 7)
CITY = (69.0, 74.0, 50.0, 52.5, 240, 9)
BOX = (10, 150, 10, 78)
# Natural Earth stops the Ob at Salekhard; the line goes on down the middle of the Ob Gulf into the Kara Sea (approximate)
OB_GULF = [(69.6, 66.6), (70.6, 66.45), (71.7, 66.4), (72.4, 67.3), (72.9, 68.6), (73.25, 70.1), (73.15, 71.5), (72.9, 72.9), (72.7, 74.0)]


def make_tex():
    for name, (lon0, lon1, lat0, lat1, ppd, z) in (('detail', DETAIL), ('city', CITY)):
        img = np.asarray(mk.bm_region(lon0, lon1, lat0, lat1, ppd)).astype(np.float32) / 255
        rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, z, 5.0 if z == 7 else 3.0, 6)
        Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save(f'tex/{name}.jpg', quality=88, subsampling=0)
        print(name, img.shape)


def lines(geom):
    t = geom['type']; c = geom['coordinates']
    return {'LineString': [c], 'MultiLineString': c, 'Polygon': [c[0]], 'MultiPolygon': [p[0] for p in c]}.get(t, [])
def inbox(r, b=BOX): return any(b[0] <= x <= b[1] and b[2] <= y <= b[3] for x, y in r)
def rnd(r, k=3): return [[round(x, k), round(y, k)] for x, y in r]
def thin(r, step=.04):
    o = [r[0]]
    for p in r[1:]:
        if abs(p[0] - o[-1][0]) + abs(p[1] - o[-1][1]) >= step: o.append(p)
    return o


def river(G, names, src):
    """One ordered line from the source end: merge the pieces, walk from the piece end nearest to src, always to the nearest next piece."""
    ls = []
    for n in names:
        for g in G[n]: ls += list(g.geoms) if g.geom_type.startswith('Multi') else [g]
    ls = [l for l in ls if 45 < l.bounds[0] and l.bounds[2] < 92]
    u = unary_union(ls); m = linemerge(u) if u.geom_type == 'MultiLineString' else u; parts = [list(p.coords) for p in (m.geoms if m.geom_type == 'MultiLineString' else [m]) if p.length > .05]
    d = lambda a, b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
    out, cur = [], src
    while parts:
        i, rev = min(((i, r) for i in range(len(parts)) for r in (0, 1)), key=lambda ir: d(parts[ir[0]][-1 if ir[1] else 0], cur))
        if out and d(parts[i][-1 if rev else 0], cur) > 1.0: break
        p = parts.pop(i); p = p[::-1] if rev else p; out += p; cur = p[-1]
    return out


def make_vec():
    out = {'borders': [], 'kz': [], 'riv': {}}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        if f['properties']['ADMIN'] == 'Kazakhstan': out['kz'] += [rnd(thin(r, .05)) for r in lines(f['geometry']) if len(r) > 30]
    G = {}
    for f in json.load(open('data/ne_10m_rivers_lake_centerlines.geojson'))['features']:
        G.setdefault(f['properties'].get('name') or '', []).append(shape(f['geometry']))
    R = {'esil': river(G, ['Esil', 'Ishim'], (73.1, 50.6)), 'irt': river(G, ['Ertix', 'Ertis', 'Irtysh'], (90.4, 47.6)),
         'ob': river(G, ['Ob'], (85.1, 52.4)) + OB_GULF, 'tob': river(G, ['Tobol'], (60.9, 51.7))}
    for k, (names, src) in {'syr': (['Syr  Darya'], (69.8, 41.0)), 'ural': (['Ural'], (59.4, 54.7)), 'ile': (['Ile'], (81.8, 43.8))}.items():
        R[k] = river(G, names, src)
    for k, r in R.items(): out['riv'][k] = rnd(thin(r, .02)); print(k, len(r), r[0], r[-1])
    for f in json.load(open('data/ne_10m_lakes.geojson'))['features']:
        if (f['properties'].get('name') or '') == 'Lake Zaysan': out['zaysan'] = [rnd(thin(r, .01)) for r in lines(f['geometry'])]
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
