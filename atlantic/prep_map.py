"""One-time asset prep (data/ = Natural Earth geojson from github.com/nvkelso/natural-earth-vector).
 dark.jpg  - flight-radar style dark world map (Mercator, lon -170..70, lat -70..84, 12 px/deg): grey sea, near-black land
 globe.json - simplified 110m land rings for the orthographic globe
 sat.jpg is reused from the greenland/ reel (NE2 satellite look, lon -100..40, lat -56..84, 30 px/deg, YT=168.948)."""
import json, math
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape
D = 'data/'
my = lambda lat: math.log(math.tan(math.pi / 4 + lat * math.pi / 360)) * 180 / math.pi
def polys(g): return g.geoms if g.geom_type == 'MultiPolygon' else [g]
L0, L1, B0, B1, S = -170, 70, -70, 84, 12
YT = my(B1); W, H = int((L1 - L0) * S), int((YT - my(B0)) * S); print('dark', W, H, 'YT', YT)
P = lambda lo, la: ((lo - L0) * S, (YT - my(max(-85, min(85, la)))) * S)
img = Image.new('RGB', (W, H), (58, 60, 63)); dr = ImageDraw.Draw(img)
for f in json.load(open(D + 'ne_50m_land.geojson'))['features']:
    for p in polys(shape(f['geometry'])):
        dr.polygon([P(*c) for c in p.exterior.coords], fill=(27, 28, 30))
for f in json.load(open(D + 'ne_50m_admin_0_countries.geojson'))['features']:
    for p in polys(shape(f['geometry'])):
        dr.line([P(*c) for c in p.exterior.coords], fill=(48, 50, 53), width=2)
img.save('dark.jpg', quality=90)
rings = []
for f in json.load(open(D + 'ne_110m_land.geojson'))['features']:
    for p in polys(shape(f['geometry']).simplify(.3)):
        if p.area > 1: rings.append([[round(x, 1), round(y, 1)] for x, y in p.exterior.coords])
json.dump({'land': rings, 'YT': YT}, open('globe.json', 'w')); print(len(rings), 'rings')
