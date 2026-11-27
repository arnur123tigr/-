"""Map assets for the Kipchaks-in-Hungary reel (run once after fetch_data.sh). tex/world.jpg comes unchanged from atacama/ (whole globe, 4096x2048).
This script writes
  tex/main.jpg    the steppe and Europe, lon 4..90, lat 32..62, 60 px/deg (NASA Blue Marble NG C1, relief from Terrarium z6)
  tex/detail.jpg  Hungary,               lon 14..24, lat 44..50, 240 px/deg (relief from Terrarium z8)
  dem.bin         Int16 heights (m) for the main window, 8 samples/deg (terrain displacement of the Carpathians, Caucasus, Alps)
  shapes.json     borders, Kazakhstan, Hungary, rivers (Danube, Tisza, Volga, Don, Ural, Irtysh), Desht-i-Kipchak (approximate, hand-drawn,
                  clipped to land), Kiskunság and Nagykunság (approximate historic outlines, hand-drawn)
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
import mapkit as mk
Image.MAX_IMAGE_PIXELS = None
MAIN = (4.0, 90.0, 32.0, 62.0, 60)
DETAIL = (14.0, 24.0, 44.0, 50.0, 240)
BOX = (0, 95, 28, 66)


def make_tex():
    for (lon0, lon1, lat0, lat1, ppd), z, name in ((MAIN, 6, 'main'), (DETAIL, 8, 'detail')):
        img = np.asarray(mk.bm_region(lon0, lon1, lat0, lat1, ppd)).astype(np.float32) / 255
        rel, hm = mk.relief(lon0, lon1, lat0, lat1, ppd, z, 5.0 if name == 'detail' else 3.0, 6)
        Image.fromarray((mk.grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save(f'tex/{name}.jpg', quality=88, subsampling=0)
        print(name, img.shape, flush=True)
    lon0, lon1, lat0, lat1, _ = MAIN
    hm = mk.dem_grid(lon0, lon1, lat0, lat1, 8, 6)
    np.clip(hm, 0, 9000).astype(np.int16).tofile('dem.bin'); print('dem', hm.shape)


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
def rings(g, step=.05, amin=.05):
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [rnd(thin(list(p.exterior.coords), step)) for p in polys if p.area > amin]
def km2(g):
    c = g.centroid.y; return g.area * 111.32 * 110.57 * np.cos(np.radians(c))


# Desht-i-Kipchak: the steppe belt from the lower Danube to the Irtysh (approximate, as on school maps of the 11th-12th c.)
DK = Polygon([(27.6, 45.0), (28.4, 47.6), (31.0, 49.4), (34.5, 50.6), (39.0, 51.4), (44.0, 52.6), (49.0, 54.0), (54.0, 54.6), (60.0, 55.0),
              (66.0, 55.4), (72.0, 55.4), (77.0, 54.6), (80.6, 53.0), (81.6, 50.6), (80.4, 48.4), (76.6, 46.2), (72.0, 44.4), (67.0, 43.4),
              (62.0, 43.6), (58.0, 45.2), (54.0, 46.0), (50.0, 46.4), (47.0, 45.6), (45.2, 44.6), (43.0, 44.6), (40.0, 45.4), (37.5, 46.0),
              (35.0, 45.3), (33.0, 45.8), (31.0, 46.4), (29.6, 45.2)])
# Kunság: Kiskunság (Little Cumania, between the Danube and the Tisza) and Nagykunság (Greater Cumania, east of the Tisza); approximate
KIS = Polygon([(19.02, 47.18), (19.42, 47.16), (19.78, 47.02), (20.06, 46.78), (20.02, 46.52), (19.82, 46.34), (19.52, 46.28), (19.30, 46.36),
               (19.10, 46.62), (18.98, 46.92)])
NAGY = Polygon([(20.36, 47.46), (20.70, 47.52), (21.10, 47.44), (21.20, 47.22), (21.00, 47.08), (20.62, 47.10), (20.34, 47.22)])
RIVERS = {'Danube': 'danube', 'Donau': 'danube', 'Tisa': 'tisza', 'Volga': 'volga', 'Don': 'don', 'Ural': 'ural', 'Irtysh': 'irtysh'}


def make_vec():
    out = {'borders': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    land = []
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        a = f['properties']['ADMIN']; g = shape(f['geometry']).buffer(0)
        if g.intersects(box(20, 36, 90, 60)): land.append(g.intersection(box(-10, 30, 100, 70)))
        if a == 'Kazakhstan': out['kz'] = rings(g, .04, .05); print('KZ km2', round(km2(g)))
        if a == 'Hungary': out['hu'] = rings(g, .02, .02)
    L = unary_union(land)
    for f in json.load(open('data/ne_10m_lakes.geojson'))['features']:        # the Caspian and Aral seas, Balkhash are not steppe
        g = shape(f['geometry']).buffer(0)
        if g.intersects(DK) and g.area > .3: L = L.difference(g)
    dk = DK.intersection(L).buffer(0)
    out['dk'] = rings(dk, .06, .3); print('Desht-i-Kipchak km2', round(km2(dk)))
    out['kis'] = rings(KIS, .01, 0); out['nagy'] = rings(NAGY, .01, 0); print('Kunság km2', round(km2(KIS) + km2(NAGY)))
    riv = {}
    for f in json.load(open('data/ne_10m_rivers_lake_centerlines.geojson'))['features']:
        k = RIVERS.get(f['properties'].get('name'))
        if k: riv.setdefault(k, []).extend(rnd(thin(r, .03)) for r in lines(f['geometry']) if inbox(r))
    out['rivers'] = riv
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: len(v) for k, v in out.items()}, {k: len(v) for k, v in riv.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
