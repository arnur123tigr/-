"""Prepare map assets for the Turkic Khaganate reel (run once, needs data/, see README.md).

Sources (fetch_data.sh downloads them; credits and licence notes are in README.md):
  data/C1.jpg, D1.jpg, world.jpg  NASA Blue Marble Next Generation, July, topography + bathymetry (public domain)
                                  (assets.science.nasa.gov/.../bmng-topography-bathymetry/july/)
  data/dem/<z>_<x>_<y>.png        Mapzen Terrain Tiles, Terrarium encoding (s3.amazonaws.com/elevation-tiles-prod/terrarium; open data, attribution)
  data/ne_*.geojson               Natural Earth vectors (public domain)

Outputs:
  tex/world.jpg  whole globe, equirectangular 4096x2048
  tex/main.jpg   Eurasia  lon 10..146.5, lat 12..78, 60 px/deg
  tex/altai.jpg  Altai    lon 80..97,   lat 43..54, 240 px/deg
  dem.bin        Int16 heights (m) for the main window, 8 samples/deg (terrain displacement)
  shapes.json    borders, Huang He, historic territories (clipped to land), shards, Silk Road
Usage: python3 prep_map.py [tex] [vec]   (no args = both)
"""
import json, math, os, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
D = 'data/'
MAIN = (10.0, 146.5, 12.0, 78.0, 60)      # lon0, lon1, lat0, lat1, px/deg
ALTAI = (80.0, 97.0, 43.0, 54.0, 240)
DEM_PPD = 8


# ---------------------------------------------------------------- elevation
def merc_xy(lon, lat, z):
    n = 256 * 2 ** z
    lat = np.clip(lat, -85.0, 85.0)
    return (lon + 180) / 360 * n, (1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / math.pi) / 2 * n


def dem_grid(lon0, lon1, lat0, lat1, ppd, z):
    """Heights (m, float32) on an equirect grid of pixel centres; row 0 = north."""
    w, h = int(round((lon1 - lon0) * ppd)), int(round((lat1 - lat0) * ppd))
    lons = lon0 + (np.arange(w) + .5) / ppd
    lats = lat1 - (np.arange(h) + .5) / ppd
    X, _ = merc_xy(lons, np.zeros(1), z); _, Y = merc_xy(np.zeros(1), lats, z)
    tx0, tx1 = int(X.min() // 256), int(X.max() // 256) + 1
    ty0, ty1 = int(Y.min() // 256), int(Y.max() // 256) + 1
    n = 2 ** z; tx1 = min(tx1, n - 1); ty1 = min(ty1, n - 1)
    mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            p = f'{D}dem/{z}_{tx}_{ty}.png'
            if not os.path.exists(p): continue
            a = np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
            mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    xs = np.clip(X - tx0 * 256 - .5, 0, mos.shape[1] - 1.001); ys = np.clip(Y - ty0 * 256 - .5, 0, mos.shape[0] - 1.001)
    x0 = xs.astype(int); fx = (xs - x0).astype(np.float32); y0 = ys.astype(int); fy = (ys - y0).astype(np.float32)[:, None]
    top = mos[y0][:, x0] * (1 - fx) + mos[y0][:, x0 + 1] * fx
    bot = mos[y0 + 1][:, x0] * (1 - fx) + mos[y0 + 1][:, x0 + 1] * fx
    return top * (1 - fy) + bot * fy


def blur(a, s):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(a, s, mode='nearest')


def hillshade(hm, lat0, lat1, ppd, zf, az=315.0, alt=42.0):
    """Relative illumination (1 = flat ground) of heights hm on an equirect grid."""
    h = hm.shape[0]
    lats = lat1 - (np.arange(h) + .5) / ppd
    dx = (111320.0 * np.cos(np.radians(lats)) / ppd)[:, None].astype(np.float32); dy = 110574.0 / ppd
    gx = np.empty_like(hm); gy = np.empty_like(hm)
    gx[:, 1:-1] = (hm[:, 2:] - hm[:, :-2]) / 2; gx[:, 0] = hm[:, 1] - hm[:, 0]; gx[:, -1] = hm[:, -1] - hm[:, -2]
    gy[1:-1] = (hm[:-2] - hm[2:]) / 2; gy[0] = hm[0] - hm[1]; gy[-1] = hm[-2] - hm[-1]
    gx = gx / dx * zf; gy = gy / dy * zf
    a, e = math.radians(az), math.radians(alt)
    L = (math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e))
    return np.maximum(0, (-gx * L[0] - gy * L[1] + L[2]) / np.sqrt(gx * gx + gy * gy + 1)) / L[2]


# ---------------------------------------------------------------- imagery
def grade(rgb, rel, hm):
    """rgb float 0..1 (Blue Marble), rel = relief illumination, hm = heights. Returns graded float 0..1."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = (0.30 * r + 0.59 * g + 0.11 * b)[..., None]
    # deep blue water (sea, big lakes) -> dark navy, keeps a hint of depth; turquoise shallow lakes stay natural
    sm = lambda x, a, c: np.clip((x - a) / (c - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (c - a), 0, 1))
    water = (sm(b - r, .10, .26) * sm(b - g, .03, .14))[..., None]
    # land: richer, warmer, more contrast (like graded satellite footage)
    land = np.clip(lum + (rgb - lum) * 1.42, 0, 1)
    land = land * np.array([1.10, 1.00, 0.80], np.float32)
    land = np.clip(land, 0, 1) ** 1.12
    land = land * land * (3 - 2 * land) * .55 + land * .45                 # soft S curve
    # snow / very bright stays neutral white
    snow = sm(np.minimum(np.minimum(r, g), b), .62, .82)[..., None]
    land = land * (1 - snow) + np.clip(rgb * 1.02, 0, 1) * snow
    # relief
    f = np.where(rel < 1, .30 + .70 * rel ** 1.25, 1 + .55 * (rel - 1))[..., None]
    land = np.clip(land * f, 0, 1)
    deep = np.array([.012, .040, .075], np.float32); shallow = np.array([.035, .16, .21], np.float32)
    sea = deep + (shallow - deep) * np.clip((lum - .16) / .30, 0, 1) ** 1.3
    return np.clip(land * (1 - water) + sea * water, 0, 1)


def relief(lon0, lon1, lat0, lat1, ppd, z, zf, coarse):
    hm = dem_grid(lon0, lon1, lat0, lat1, ppd, z)
    land = np.maximum(hm, -30)
    fine = hillshade(land, lat0, lat1, ppd, zf)
    big = hillshade(blur(land, coarse), lat0, lat1, ppd, zf * 2.2)
    return .62 * fine + .38 * big, hm


def bm_region(lon0, lon1, lat0, lat1, ppd):
    """Blue Marble 500 m tiles (C1: 0..90E, D1: 90..180E; both 90N..0) resampled to an equirect window."""
    w, h = int(round((lon1 - lon0) * ppd)), int(round((lat1 - lat0) * ppd))
    out = Image.new('RGB', (w, h))
    for name, a0 in (('C1.jpg', 0.0), ('D1.jpg', 90.0)):
        l0, l1 = max(lon0, a0), min(lon1, a0 + 90)
        if l1 <= l0: continue
        im = Image.open(D + name)
        box = (int(round((l0 - a0) * 240)), int(round((90 - lat1) * 240)), int(round((l1 - a0) * 240)), int(round((90 - lat0) * 240)))
        tw = int(round((l1 - lon0) * ppd)) - int(round((l0 - lon0) * ppd))
        part = im.crop(box).resize((tw, h), Image.LANCZOS)
        out.paste(part, (int(round((l0 - lon0) * ppd)), 0)); print('  ', name, box, '->', part.size, flush=True)
    return out


def make_tex():
    os.makedirs('tex', exist_ok=True)
    # --- main window
    lon0, lon1, lat0, lat1, ppd = MAIN
    print('main imagery', flush=True); img = np.asarray(bm_region(*MAIN)).astype(np.float32) / 255
    print('main relief', flush=True); rel, hm = relief(lon0, lon1, lat0, lat1, ppd, 7, 5.0, 5)
    Image.fromarray((grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/main.jpg', quality=88, subsampling=0)
    print('main.jpg', img.shape, flush=True)
    # heights for displacement: block-average to DEM_PPD
    k = ppd // DEM_PPD; hh = np.maximum(hm, 0)[:hm.shape[0] // k * k, :hm.shape[1] // k * k]
    dm = hh.reshape(hh.shape[0] // k, k, hh.shape[1] // k, k).mean((1, 3))
    np.clip(dm, 0, 9000).astype('<i2').tofile('dem.bin'); print('dem.bin', dm.shape, dm.max(), flush=True)
    del img, rel, hm
    # --- altai window
    lon0, lon1, lat0, lat1, ppd = ALTAI
    print('altai', flush=True); img = np.asarray(bm_region(*ALTAI)).astype(np.float32) / 255
    rel, hm = relief(lon0, lon1, lat0, lat1, ppd, 9, 2.4, 14)
    Image.fromarray((grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/altai.jpg', quality=88, subsampling=0)
    print('altai.jpg', img.shape, flush=True); del img, rel, hm
    # --- whole world
    print('world', flush=True)
    img = np.asarray(Image.open(D + 'world.jpg').resize((4096, 2048), Image.LANCZOS)).astype(np.float32) / 255
    ppd = 4096 / 360; rel, hm = relief(-180, 180, -90, 90, ppd, 4, 9.0, 2)
    Image.fromarray((grade(img, rel, hm) * 255 + .5).astype(np.uint8)).save('tex/world.jpg', quality=88, subsampling=0)
    print('world.jpg', flush=True)


# ---------------------------------------------------------------- vectors
ALTAI_PT = (88.4, 48.0)
# First Turkic Khaganate at its height (570s), clockwise from the Sea of Azov. Schematic, after school-atlas maps.
TURK_MAX = [(39.0, 47.2), (40.5, 47.9), (43.0, 49.0), (46.5, 50.3), (50.0, 51.3), (54.0, 51.9), (58.5, 52.4), (62.0, 53.5),
            (68.0, 54.6), (74.0, 55.0), (80.0, 55.3), (86.0, 55.8), (92.0, 56.0), (98.0, 55.5), (104.0, 54.9), (108.0, 54.6),
            (113.0, 53.9), (119.5, 52.9), (122.2, 52.0), (124.2, 50.6), (125.3, 48.8), (124.9, 46.5), (124.0, 44.5), (122.8, 42.9),
            (121.5, 42.4), (119.5, 42.3), (117.5, 41.9), (115.8, 41.4), (114.0, 41.0), (112.5, 40.6), (111.25, 40.35), (110.3, 40.55),
            (109.5, 40.8), (108.5, 41.1), (107.6, 40.95), (107.0, 40.6), (105.5, 40.9), (103.0, 41.2), (100.0, 41.9), (97.5, 41.6),
            (95.0, 41.3), (93.3, 41.0), (91.5, 39.6), (89.0, 38.4), (86.0, 37.0), (83.0, 36.2), (80.0, 36.6), (77.5, 37.4),
            (75.5, 38.6), (73.5, 39.2), (71.5, 38.6), (70.2, 37.6), (68.8, 37.2), (67.0, 37.3), (65.2, 38.0), (63.6, 39.1),
            (60.0, 39.6), (56.5, 39.7), (53.6, 39.8), (51.0, 41.0), (48.2, 42.0), (46.8, 42.3), (45.5, 42.6), (44.0, 42.9),
            (42.5, 43.3), (41.0, 43.5), (39.9, 43.45), (39.0, 43.9), (38.0, 44.4), (37.0, 44.9), (36.3, 45.0), (36.3, 45.5),
            (37.6, 46.0), (38.2, 46.6)]
# 603: the border between the Eastern and the Western khaganates ran along the Altai (north -> south)
SPLIT = [(87.4, 57.0), (87.6, 54.2), (88.2, 52.2), (88.9, 50.2), (90.4, 48.6), (92.4, 46.9), (94.3, 45.2), (95.4, 43.6), (96.0, 40.5)]
ROURAN = [(84.0, 46.6), (85.6, 49.4), (88.6, 51.4), (93.0, 52.3), (98.0, 52.5), (103.0, 52.8), (107.0, 53.3), (111.0, 53.0),
          (115.0, 51.8), (119.0, 50.5), (121.4, 48.5), (121.9, 46.0), (121.0, 44.0), (119.0, 42.7), (116.0, 41.9), (113.0, 41.4),
          (110.0, 41.5), (107.0, 41.6), (104.0, 41.7), (100.0, 42.0), (96.5, 42.4), (93.0, 43.2), (90.0, 43.7), (87.0, 44.3), (85.0, 45.1)]
HOME = [(86.4, 48.6), (87.2, 49.4), (88.6, 49.7), (90.0, 49.2), (91.0, 48.2), (91.3, 47.0), (90.2, 46.2), (88.6, 45.9), (87.2, 46.4), (86.4, 47.4)]
STRIKE = (104.5, 47.3)       # where the arrow hits (Rouran heartland on the Orkhon)
# Silk Road: Chang'an -> Hexi corridor -> Turfan -> Zhetysu -> Sogdia, then the northern way the 568 embassy took around Persia
SILK = [(108.94, 34.27), (105.7, 34.6), (103.8, 36.06), (102.64, 37.93), (100.45, 38.93), (98.5, 39.74), (95.8, 40.5), (94.66, 40.14),
        (93.5, 42.83), (89.18, 42.95), (87.6, 43.8), (86.2, 44.3), (82.9, 44.6), (81.2, 44.4), (80.4, 44.0), (78.5, 43.6), (76.9, 43.25),
        (75.2, 42.8), (73.3, 42.85), (71.37, 42.9), (69.77, 42.3), (69.28, 41.31), (67.85, 40.12), (66.97, 39.65), (64.42, 39.77),
        (62.2, 40.9), (60.6, 41.9), (59.15, 42.33), (56.6, 44.4), (54.4, 46.5), (51.7, 47.4), (47.9, 46.6), (45.6, 45.3),
        (43.6, 44.0), (42.0, 43.25), (41.2, 42.75), (40.6, 41.6), (39.72, 41.0), (37.4, 41.2), (35.15, 42.02), (33.0, 42.0), (31.4, 41.4), (28.98, 41.01)]
SILK_CITIES = {'changan': 0, 'dunhuang': 7, 'turfan': 9, 'suyab': 17, 'taraz': 19, 'samarkand': 23, 'volga': 31, 'const': len(SILK) - 1}


def chaikin(pts, n=2, closed=True):
    for _ in range(n):
        q = []
        m = len(pts)
        for i in range(m if closed else m - 1):
            a, b = pts[i], pts[(i + 1) % m]
            q += [(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)]
        pts = ([pts[0]] + q + [pts[-1]]) if not closed else q
    return pts


def make_vec():
    from shapely.geometry import shape, Polygon, MultiPolygon, LineString, box, Point
    from shapely.ops import unary_union, split, linemerge
    from shapely import voronoi_polygons, MultiPoint
    G = lambda f: json.load(open(D + f))['features']
    bbox = box(8, 8, 150, 80)
    land = unary_union([shape(f['geometry']).buffer(0) for f in G('ne_50m_land.geojson')]).intersection(bbox)
    lakes = unary_union([shape(f['geometry']).buffer(0) for f in G('ne_50m_lakes.geojson')
                         if shape(f['geometry']).area > 0.25]).intersection(bbox)
    dry = land.difference(lakes)
    rd = lambda c: [round(c[0], 3), round(c[1], 3)]

    def rings(g, tol=.03, amin=.02):
        g = g.simplify(tol, preserve_topology=True)
        ps = list(g.geoms) if g.geom_type in ('MultiPolygon', 'GeometryCollection') else [g]
        return [[rd(c) for c in p.exterior.coords] for p in ps if p.geom_type == 'Polygon' and p.area > amin]

    out = {'altai': list(ALTAI_PT), 'strike': list(STRIKE)}
    tmax = Polygon(chaikin(TURK_MAX, 2)).buffer(0)
    line = LineString(chaikin(SPLIT, 2, closed=False))
    parts = list(split(tmax, line).geoms)
    west = unary_union([p for p in parts if p.representative_point().x < 88 or p.centroid.x < 88])
    east = tmax.difference(west)
    out['split'] = [rd(c) for c in line.intersection(tmax.buffer(.3)).coords]
    out['west'] = rings(west.intersection(dry)); out['east'] = rings(east.intersection(dry))
    out['turk'] = rings(tmax.intersection(dry))
    out['turk_outline'] = rings(tmax, .02)
    rou = Polygon(chaikin(ROURAN, 2)).buffer(0); home = Polygon(chaikin(HOME, 3)).buffer(0)
    out['home'] = rings(home.intersection(dry), .01, .001)
    out['rouran'] = rings(rou.difference(home.buffer(.25)).intersection(dry))
    # shards of the Rouran realm (it cracks and fades in 552): Voronoi cells, denser near the strike point
    rng = np.random.default_rng(11)
    minx, miny, maxx, maxy = rou.bounds; seeds = []
    while len(seeds) < 34:
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        d = math.hypot((x - STRIKE[0]) * .68, y - STRIKE[1])
        if rou.contains(Point(x, y)) and rng.uniform() < .35 + .65 * math.exp(-d / 7) and all(math.hypot((x - a) * .68, y - b) > 1.9 for a, b in seeds):
            seeds.append((x, y))
    vor = voronoi_polygons(MultiPoint(seeds), extend_to=rou.buffer(3))
    shards = []
    rou_clip = rou.difference(home.buffer(.25)).intersection(dry)
    for cell in vor.geoms:
        g = cell.intersection(rou_clip)
        if g.is_empty: continue
        c = cell.intersection(rou).centroid
        for r in rings(g, .04, .05): shards.append({'c': rd((c.x, c.y)), 'ring': r})
    out['shards'] = shards
    # cracks = shared edges of the Voronoi cells inside the realm
    edges = unary_union([c.boundary for c in vor.geoms]).intersection(rou.buffer(-.15))
    edges = linemerge(edges) if edges.geom_type != 'LineString' else edges
    out['cracks'] = [[rd(c) for c in l.coords] for l in (edges.geoms if hasattr(edges, 'geoms') else [edges]) if l.length > .3]
    # modern borders (thin grey lines, as in the reference). The Baikonur lease line is skipped: Baikonur is Kazakhstan.
    bl = []
    for f in G('ne_50m_admin_0_boundary_lines_land.geojson'):
        p = f['properties']
        if 'ease' in str(p.get('FEATURECLA', '')) or 'Baikonur' in json.dumps(p): continue
        g = shape(f['geometry']).intersection(box(12, 14, 148, 76)).simplify(.03)
        for l in (g.geoms if hasattr(g, 'geoms') else [g]):
            if l.geom_type == 'LineString' and l.length > .15: bl.append([rd(c) for c in l.coords])
    out['borders'] = bl
    # Huang He (Yellow River)
    hh = [shape(f['geometry']) for f in G('ne_10m_rivers_lake_centerlines.geojson')
          if str(f['properties'].get('name', '')).startswith('Huang') or str(f['properties'].get('name_en', '')).startswith('Yellow')]
    m = linemerge(unary_union(hh)); m = max(m.geoms, key=lambda l: l.length) if hasattr(m, 'geoms') else m
    out['huanghe'] = [rd(c) for c in m.simplify(.02).coords]
    out['silk'] = [list(p) for p in SILK]; out['silk_cities'] = SILK_CITIES
    json.dump(out, open('shapes.json', 'w'), separators=(',', ':'))
    print({k: (len(v) if hasattr(v, '__len__') else v) for k, v in out.items()})
    print('pts', sum(len(r) for k in ('turk', 'west', 'east', 'rouran', 'home') for r in out[k]), 'border pts', sum(len(l) for l in bl),
          'huanghe', len(out['huanghe']), 'shards', len(shards), 'cracks', len(out['cracks']))


if __name__ == '__main__':
    a = sys.argv[1:] or ['tex', 'vec']
    if 'vec' in a: make_vec()
    if 'tex' in a: make_tex()
