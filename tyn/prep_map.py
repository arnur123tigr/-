"""Map assets for the Virgin Lands reel (run once after fetch_data.sh).
tex/world.jpg, tex/main.jpg and dem.bin come unchanged from kulja/ (<- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
This script adds
  tex/detail.jpg  northern Kazakhstan, lon 58..82, lat 47..56.5, 120 px/deg, relief from Terrarium z7
  shapes.json     borders, Kazakhstan outline (with Baikonur), the five Virgin Lands oblasts of 1960 (approximate: modern Natural Earth provinces,
                  Kokchetav oblast hand-drawn and cut out of North Kazakhstan and Akmola), Great Britain + Northern Ireland outline
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, Polygon, mapping
from shapely.ops import unary_union
import mapkit as mk
DETAIL = (58.0, 82.0, 47.0, 56.5, 120)
BOX = (10, 150, 10, 78)


def make_tex():
    lon0, lon1, lat0, lat1, ppd = DETAIL
    img = np.asarray(mk.bm_region(*DETAIL)).astype(np.float32) / 255
    rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, 7, 5.0, 6)
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
    return o
def rings(g, step=.05):
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [rnd(thin(list(p.exterior.coords), step)) for p in polys if p.area > .05]


KOK = Polygon([(66.3, 53.55), (67.6, 53.95), (69.0, 54.15), (70.6, 54.05), (71.9, 53.75), (72.7, 53.3), (72.55, 52.75), (71.6, 52.45),
               (70.3, 52.25), (68.9, 52.3), (67.6, 52.55), (66.6, 52.95)])


def make_vec():
    out = {'borders': [], 'kz': [], 'obl': {}, 'uk': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        a = f['properties']['ADMIN']
        if a == 'Kazakhstan': out['kz'] += [rnd(thin(r, .05)) for r in lines(f['geometry']) if len(r) > 30]
        if a == 'United Kingdom': out['uk'] += [rnd(thin(r, .03)) for r in lines(f['geometry']) if len(r) > 40]
    P = {}
    for f in json.load(open('data/ne_10m_admin_1_states_provinces.geojson'))['features']:
        p = f['properties']
        if p.get('admin') == 'Kazakhstan': P[p['name_en']] = shape(f['geometry']).buffer(0)
    akm = unary_union([P['Akmola'], P['Nur-Sultan']]).buffer(.01).buffer(-.01)
    kok = KOK.intersection(unary_union([P['North Kazakhstan'], akm]))
    obl = {'kus': P['Kostanay'], 'sko': P['North Kazakhstan'].difference(kok), 'kok': kok, 'akm': akm.difference(kok), 'pav': P['Pavlodar']}
    for k, g in obl.items(): out['obl'][k] = rings(g)
    out['tyn'] = rings(unary_union(list(obl.values())).buffer(.02).buffer(-.02), .05)
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: (len(v) if isinstance(v, list) else {a: len(b) for a, b in v.items()}) for k, v in out.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
