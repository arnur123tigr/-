"""Natural Earth 10m geojson (/home/user/data/ne) -> shapes.json: the Roman Empire c. 450 (schematic, from modern countries
clipped to the old frontiers), Mongolia (Xiongnu homeland), coast-free rivers of Europe (Volga, Danube, Rhine...)."""
import json
from shapely.geometry import shape, box, Polygon
from shapely.ops import unary_union
D = '/home/user/data/ne/'
G = {}
for f in json.load(open(D + 'ne_10m_admin_0_countries.geojson'))['features']:
    G[f['properties']['ADM0_A3']] = shape(f['geometry'])
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.03, min_area=.05):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        for r in polys(p.simplify(tol)): out.append([[round(x, 3), round(y, 3)] for x, y in r.exterior.coords])
    return out
U = lambda isos: unary_union([G[i] for i in isos if i in G])
# West Rome c.450: Italy, Gaul up to the Rhine, Hispania, Africa coast (Vandals took it in 439, but schematic), Raetia/Noricum
west = U(['ITA', 'FRA', 'ESP', 'PRT', 'CHE', 'AUT', 'SVN', 'HRV', 'BEL', 'LUX', 'SMR', 'VAT', 'MCO', 'AND', 'BIH', 'MNE'])
west = west.intersection(Polygon([(-10, 35), (-10, 44), (-2, 49), (2, 51.2), (6.2, 51.6), (7.5, 49.5), (8.4, 47.6), (13, 48.5), (16.9, 48.1), (16.6, 46.2), (19.2, 45.2), (19.5, 42), (19.4, 40), (14, 36), (-10, 35)]))
# the Danube between Austria and the sea = the frontier; Pannonia (west Hungary) was already Hunnic by 433
east = U(['GRC', 'BGR', 'MKD', 'ALB', 'SRB', 'XKX', 'KOS', 'TUR', 'CYP', 'SYR', 'LBN', 'ISR', 'PSE', 'JOR', 'EGY', 'ROU', 'MDA'])
east = east.intersection(Polygon([(19.4, 42.5), (19.5, 45), (22.5, 44.6), (28, 43.9), (29.7, 45.2), (29.7, 44), (41, 41.5), (44, 39), (42, 36.5), (39, 32), (36.5, 29.5), (34.5, 28), (33, 22.5), (24.5, 30.5), (24.5, 33), (19.4, 39.5)]))
africa = U(['DZA', 'TUN', 'MAR', 'LBY']).intersection(box(-10, 33.6, 12, 38))
west = unary_union([west, africa])
S = {'west': rings(west), 'east': rings(east), 'mng': rings(G['MNG'], .05, .5), 'rivers': []}
KEEP = {'Volga', 'Don', 'Dnipro', 'Dnepre', 'Danube', 'Rhine', 'Dniester', 'Ural', 'Po', 'Tisza', 'Rhône', 'Seine', 'Marne', 'Loire', 'Elbe', 'Vistula', 'Kama'}
for f in json.load(open(D + 'ne_10m_rivers_lake_centerlines.geojson'))['features']:
    if f['properties'].get('name') not in KEEP: continue
    g = shape(f['geometry']).intersection(box(-12, 28, 78, 62))
    for l in polys(g):
        if l.geom_type == 'LineString' and l.length > .2: S['rivers'].append([[round(x, 3), round(y, 3)] for x, y in l.simplify(.03).coords])
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
