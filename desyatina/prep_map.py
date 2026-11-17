"""Map shapes for the reel -> geo.json (units: 1 = 250 km, equal-scale local projection centred on 67E 48N).
Kazakhstan = Natural Earth 10m Kazakhstan + the Baikonur lease (filled, no hole). Kyrgyzstan at the same scale.
Needs data/adm0.geojson = Natural Earth ne_10m_admin_0_countries.geojson (public domain).
Usage: python3 prep_map.py"""
import json, math
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union

LON0, LAT0, KM = 67.0, 48.0, 250.0
def P(lon, lat): return [round((lon - LON0) * math.cos(math.radians(LAT0)) * 111.32 / KM, 4), round((lat - LAT0) * 110.57 / KM, 4)]

F = {f['properties']['ADMIN']: shape(f['geometry']) for f in json.load(open('data/adm0.geojson'))['features']}
kz = unary_union([F['Kazakhstan'], F['Baykonur Cosmodrome']]).buffer(0.01).buffer(-0.01)
kg = F['Kyrgyzstan']
def outer(g, tol):
    g = max(getattr(g, 'geoms', [g]), key=lambda p: p.area).simplify(tol)
    return [P(x, y) for x, y in list(Polygon(g.exterior).exterior.coords)[:-1]]
def area_km2(g):   # rough equal-area check
    from shapely.ops import transform
    return transform(lambda x, y: ((x - LON0) * 111.32 * math.cos(math.radians(y)), (y - LAT0) * 110.57), g).area
print('KZ km2 %.0f  KG km2 %.0f  17M desyatinas = %.0f km2' % (area_km2(kz), area_km2(kg), 17e6 * 1.0925 / 100))
out = {
  'kz': outer(kz, .03), 'kg': outer(kg, .02),
  'rail': [P(*c) for c in ((53.2, 53.2), (56.0, 54.7), (61.40, 55.16), (63.5, 55.3), (65.34, 55.44), (67.5, 55.1), (69.15, 54.87), (71.2, 54.9), (73.37, 54.99), (76.5, 55.2), (79.0, 55.2), (82.92, 55.03))],
  'city': {'petro': P(69.15, 54.87), 'omsk': P(73.37, 54.99), 'chel': P(61.40, 55.16), 'semir': P(77.5, 44.5)},
}
json.dump(out, open('geo.json', 'w'))
print(len(out['kz']), 'kz pts', len(out['kg']), 'kg pts')
