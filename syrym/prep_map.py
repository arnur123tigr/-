"""Map assets for the «first capital of the Kazakhs is in Russia» reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from kulja/ (<- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  Orenburg and the Ural valley, lon 53..57.5, lat 50.5..53, 240 px/deg, relief from Terrarium z9
  shapes.json     modern borders, Kazakhstan / Uzbekistan outlines, the KZ-RU border line (west -> east), the regions of the reel
                  (Orenburg, Omsk, Astrakhan oblasts, Karakalpakstan, Zhambyl oblast; Natural Earth admin-1), the Ural, Volga, Irtysh,
                  Aral, and hand-drawn approximations: the Bukey Horde, the old Akmola oblast (1868-1917, governed from Omsk),
                  the Kazakh ASSR of the 1920s (= today's Kazakhstan + Orenburg + Karakalpakstan + the Bukey part at the Volga).
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union, linemerge
import mapkit as mk
DETAIL = (53.0, 57.5, 50.5, 53.0, 240)
BOX = (10, 150, 10, 78)


def make_tex():
    lon0, lon1, lat0, lat1, ppd = DETAIL
    img = np.asarray(mk.bm_region(*DETAIL)).astype(np.float32) / 255
    rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 9, 3.0, 12)
    Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/detail.jpg', quality=88, subsampling=0)
    print('detail.jpg', img.shape)


def lines(geom):
    t = geom['type']; c = geom['coordinates']
    return {'LineString': [c], 'MultiLineString': c, 'Polygon': [c[0]], 'MultiPolygon': [p[0] for p in c]}.get(t, [])
def inbox(r, b=BOX): return any(b[0] <= x <= b[1] and b[2] <= y <= b[3] for x, y in r)
def rnd(r, k=3): return [[round(x, k), round(y, k)] for x, y in r]
def thin(r, step=.04):
    o = [r[0]]
    for p in r[1:]:
        if abs(p[0] - o[-1][0]) + abs(p[1] - o[-1][1]) >= step: o.append(p)
    if o[-1] != r[-1]: o.append(r[-1])
    return o
def rings(g, step=.05, minA=.05):
    ps = [g] if isinstance(g, Polygon) else list(getattr(g, 'geoms', []))
    return [rnd(thin(list(p.exterior.coords), step)) for p in ps if isinstance(p, Polygon) and p.area >= minA]


def make_vec():
    out = {'borders': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    C = {}
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        a = f['properties']['ADMIN']
        if a in ('Kazakhstan', 'Russia', 'Uzbekistan', 'Baikonur'): C[a] = shape(f['geometry']).buffer(0)
    kz = C['Kazakhstan']
    if 'Baikonur' in C: kz = unary_union([kz, C['Baikonur']])          # Baikonur is Kazakhstan territory (no hole)
    kz = Polygon(max(kz.geoms, key=lambda p: p.area).exterior) if isinstance(kz, MultiPolygon) else Polygon(kz.exterior)
    ru = C['Russia']; uz = C['Uzbekistan']
    out['kz'] = rings(kz, .04); out['uz'] = rings(uz, .05, .5)
    # the KZ-RU border as one line, west -> east
    b = kz.exterior.intersection(ru.buffer(.03))
    b = linemerge(b) if not isinstance(b, LineString) else b
    seg = max(b.geoms, key=lambda l: l.length) if isinstance(b, MultiLineString) else b
    pts = list(seg.coords)
    if pts[0][0] > pts[-1][0]: pts.reverse()
    out['rukz'] = rnd(thin(pts, .04))
    A = {}
    for f in json.load(open('data/ne_10m_admin_1_states_provinces.geojson'))['features']:
        p = f['properties']; k = {('Russia', 'Orenburg'): 'oren', ('Russia', 'Omsk'): 'omsk', ('Russia', "Astrakhan'"): 'astr',
                                  ('Uzbekistan', 'Karakalpakstan'): 'kara', ('Kazakhstan', 'Zhambyl'): 'zham'}.get((p['admin'], p['name']))
        if k: A[k] = shape(f['geometry']).buffer(0)
    for k, g in A.items(): out[k] = rings(g, .04, .3)
    land = unary_union([kz, ru.intersection(Polygon([(40, 40), (95, 40), (95, 60), (40, 60)]))])
    bukey = Polygon([(46.45, 48.7), (46.7, 49.4), (47.2, 50.0), (48.2, 50.55), (49.4, 51.0), (50.6, 51.2), (51.3, 51.05), (51.6, 50.55), (51.7, 49.7),
                     (51.5, 48.6), (51.0, 47.6), (50.1, 46.95), (49.0, 46.6), (48.1, 46.55), (47.5, 46.9), (47.0, 47.6)]).intersection(land)
    out['bukey'] = rings(bukey, .04); out['bukey_ru'] = rings(bukey.intersection(ru), .04, .02)
    akm = Polygon([(64.6, 53.4), (65.6, 54.7), (67.5, 55.2), (70.0, 55.45), (72.6, 55.5), (74.3, 55.3), (75.8, 54.5), (76.6, 53.0), (77.0, 51.3),
                   (76.6, 49.4), (75.6, 47.7), (74.4, 46.6), (72.0, 46.3), (69.5, 46.9), (67.3, 47.8), (65.7, 49.2), (64.9, 51.0)]).intersection(land)
    out['akm'] = rings(akm, .04)
    kassr = unary_union([kz, A['oren'].buffer(.02), A['kara'].buffer(.02), bukey.buffer(.02)]).buffer(-.02)
    out['kassr'] = rings(kassr, .05, .5)
    out['rivers'] = []
    for f in json.load(open('data/ne_10m_rivers_lake_centerlines.geojson'))['features']:
        if (f['properties'].get('name') or '') in ('Ural', 'Volga', 'Irtysh', 'Syr Darya', 'Ishim', 'Tobol'):
            out['rivers'] += [rnd(thin(r, .03)) for r in lines(f['geometry']) if inbox(r, (40, 90, 38, 60))]
    out['aral'] = []
    for f in json.load(open('data/ne_10m_lakes.geojson'))['features']:
        if 'Aral' in (f['properties'].get('name') or ''): out['aral'] += [rnd(thin(r, .02)) for r in lines(f['geometry'])]
    for k in ('oren', 'kara', 'zham', 'bukey', 'kassr'):
        g = {'oren': A['oren'], 'kara': A['kara'], 'zham': A['zham'], 'bukey': bukey, 'kassr': kassr}[k]
        c = g.centroid; out[k + '_c'] = [round(c.x, 3), round(c.y, 3)]
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: (len(v), sum(len(r) for r in v) if v and isinstance(v[0], list) and isinstance(v[0][0], list) else v) for k, v in out.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
