# Build dots.json: hex grid of land dots for the dot-matrix map (Australia + East Asia), from Natural Earth 50m countries.
import json
from shapely.geometry import shape, Point
from shapely.prepared import prep
G = json.load(open('data/countries.geojson'))
polys = [(f['properties']['ADM0_A3'], prep(shape(f['geometry']))) for f in G['features']]
S = 0.9; out = []
lat = -46.0; row = 0
while lat <= 56:
    lon = 88.0 + (S / 2 if row % 2 else 0)
    while lon <= 162:
        p = Point(lon, lat)
        for k, pg in polys:
            if pg.contains(p): out.append([round(lon, 2), round(lat, 2), 1 if k == 'AUS' else 0]); break
        lon += S
    lat += S * 0.866; row += 1
json.dump(out, open('dots.json', 'w'))
print(len(out), sum(d[2] for d in out))
