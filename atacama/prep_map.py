"""Map assets for the Atacama reel (run once after fetch_data.sh). tex/world.jpg comes unchanged from tyn/ (whole globe, 4096x2048).
This script writes
  tex/main.jpg    South America, lon -90..-30, lat -50..10, 60 px/deg (NASA Blue Marble NG B1+B2, relief from Terrarium z6)
  tex/detail.jpg  Atacama,       lon -76..-64, lat -28..-16, 240 px/deg (relief from Terrarium z8)
  dem.bin         Int16 heights (m) for the main window, 8 samples/deg (terrain displacement of the Andes)
  shapes.json     borders, Chile outline, the Atacama desert (approximate hand-drawn strip, clipped to land), Pavlodar oblast
Usage: python3 prep_map.py [tex] [vec]"""
import json, sys
import numpy as np
from PIL import Image
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
import mapkit as mk
Image.MAX_IMAGE_PIXELS = None
MAIN = (-90.0, -30.0, -50.0, 10.0, 60)
DETAIL = (-76.0, -64.0, -28.0, -16.0, 240)
BOX = (-100, -20, -60, 15)


def bm_region(lon0, lon1, lat0, lat1, ppd):
    """Blue Marble 500 m tiles B1 (90W..0, 90N..0) and B2 (90W..0, 0..90S) resampled to an equirect window."""
    w, h = int(round((lon1 - lon0) * ppd)), int(round((lat1 - lat0) * ppd))
    out = Image.new('RGB', (w, h))
    for name, top in (('B1.jpg', 90.0), ('B2.jpg', 0.0)):
        a0, a1 = max(lat0, top - 90), min(lat1, top)
        if a1 <= a0: continue
        im = Image.open('data/' + name)
        box = (int(round((lon0 + 90) * 240)), int(round((top - a1) * 240)), int(round((lon1 + 90) * 240)), int(round((top - a0) * 240)))
        y0 = int(round((lat1 - a1) * ppd)); th = int(round((lat1 - a0) * ppd)) - y0
        part = im.crop(box).resize((w, th), Image.LANCZOS); out.paste(part, (0, y0)); print('  ', name, box, '->', part.size, flush=True)
    return out


def make_tex():
    for (lon0, lon1, lat0, lat1, ppd), z, name in ((MAIN, 6, 'main'), (DETAIL, 8, 'detail')):
        img = np.asarray(bm_region(lon0, lon1, lat0, lat1, ppd)).astype(np.float32) / 255
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
    return o
def rings(g, step=.05, amin=.05):
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [rnd(thin(list(p.exterior.coords), step)) for p in polys if p.area > amin]
def km2(g):
    c = g.centroid.y; return g.area * 111.32 * 110.57 * np.cos(np.radians(c))


# the hyper-arid core of the Atacama: coast (extended into the sea, then cut to land) to the Andean foothills, Arica .. Huasco
ATA_E = [(-69.6, -18.0), (-69.4, -19.0), (-69.15, -20.5), (-68.9, -21.8), (-68.3, -22.6), (-68.0, -23.6), (-68.3, -24.6), (-68.9, -25.6),
         (-69.4, -26.6), (-69.9, -27.6), (-70.4, -28.6), (-70.9, -29.4)]
ATA = Polygon([(-72.5, -29.4), (-72.5, -18.0)] + [(x - .62, y) for x, y in ATA_E])


def make_vec():
    out = {'borders': [], 'chile': [], 'peru': []}
    for f in json.load(open('data/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
        for r in lines(f['geometry']):
            if inbox(r): out['borders'].append(rnd(thin(r, .03)))
    land = []
    for f in json.load(open('data/ne_10m_admin_0_countries.geojson'))['features']:
        a = f['properties']['ADMIN']; g = shape(f['geometry']).buffer(0)
        if a in ('Chile', 'Peru', 'Bolivia', 'Argentina'): land.append(g)
        if a == 'Chile': out['chile'] = rings(g, .03, .02)
    ata = ATA.intersection(unary_union(land))
    out['atacama'] = rings(ata, .03, .02)
    sea = Polygon([(-73.6, -21.2), (-73.6, -16.6), (-70.0, -16.6), (-70.0, -21.2)]).difference(unary_union(land).buffer(.01))
    out['sea'] = rings(sea, .02, .05); print('Atacama km2', round(km2(ata)))
    for f in json.load(open('data/ne_10m_admin_1_states_provinces.geojson'))['features']:
        p = f['properties']
        if p.get('admin') == 'Kazakhstan' and p['name_en'] == 'Pavlodar':
            g = shape(f['geometry']).buffer(0); out['pav'] = rings(g, .03); out['pavC'] = [round(g.centroid.x, 3), round(g.centroid.y, 3)]; print('Pavlodar km2', round(km2(g)))
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: len(v) for k, v in out.items()})


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
