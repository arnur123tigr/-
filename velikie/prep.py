"""Data for the Great Lakes reel. Textures: NASA Blue Marble (public domain) via prep_tex.py; vectors: Natural Earth 10m (public domain) -> shapes.json."""
import json, subprocess
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union, linemerge
D = '/home/user/data/'
subprocess.run(['python3', 'prep_tex.py', 'tex', 'na', '-140', '-48', '12', '66', '30', 'gl', '-93.5', '-73', '40', '50', '120'], check=True)
subprocess.run(['python3', 'grade.py', 'tex/na.jpg', 'tex/gl.jpg'], check=True)
from PIL import Image
im = Image.open(D + 'world.jpg'); im.save('tex/world.jpg', quality=90); subprocess.run(['python3', 'grade.py', 'tex/world.jpg'], check=True)
L = lambda n: json.load(open(D + n + '.geojson'))['features']
def polys(g): return list(g.geoms) if hasattr(g, 'geoms') else [g]
def rings(g, tol=.02, min_area=0):
    out = []
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.area < min_area: continue
        q = p.simplify(tol)
        for r in polys(q): out.append([[round(x, 4), round(y, 4)] for x, y in r.exterior.coords])
    return out
S = {}
lakes = {f['properties']['name']: shape(f['geometry']) for f in L('ne_10m_lakes') if f['properties'].get('name')}
for k, n in [('sup', 'Lake Superior'), ('mic', 'Lake Michigan'), ('hur', 'Lake Huron'), ('eri', 'Lake Erie'), ('ont', 'Lake Ontario')]:
    S[k] = rings(lakes[n], .01, .01)
C = {f['properties']['ADM0_A3']: shape(f['geometry']) for f in L('ne_10m_admin_0_countries')}
S['usa'] = rings(C['USA'].intersection(box(-130, 24, -60, 50)), .03, .5)
S['can'] = rings(C['CAN'], .05, 1)
# USA-Canada border line (shared boundary, 49th parallel and lakes part)
bd = C['USA'].intersection(box(-130, 40, -60, 50)).boundary.intersection(C['CAN'].buffer(.02))
ln = linemerge(bd) if bd.geom_type == 'MultiLineString' else bd
S['border'] = [[[round(x, 3), round(y, 3)] for x, y in l.simplify(.02).coords] for l in (ln.geoms if hasattr(ln, 'geoms') else [ln]) if l.length > .3]
# rel shapes for size compare: centred lon/lat offsets
def rel(g, lat0=None):
    c = g.centroid; return {'lat': round(c.y, 3), 'r': [[[round(x - c.x, 4), round(y - c.y, 4)] for x, y in r] for r in rings(g, .01, .002)]}
for k, a in [('aut', 'AUT'), ('cze', 'CZE'), ('irl', 'IRL'), ('pan', 'PAN')]: S['rel_' + k] = rel(C[a])
S['rel_bal'] = rel(lakes['Lake Balkhash']); S['rel_sup'] = rel(lakes['Lake Superior'])
# continents for the "spread the water over all land" scene
cont = {}
for f in L('ne_10m_admin_0_countries'):
    c = f['properties']['CONTINENT']; cont.setdefault(c, []).append(shape(f['geometry']).buffer(0))
grp = {'am': ['North America', 'South America'], 'af': ['Africa'], 'eu': ['Europe', 'Asia'], 'au': ['Oceania'], 'an': ['Antarctica']}
for k, cs in grp.items():
    g = unary_union([p for c in cs for p in cont.get(c, [])]).intersection(box(-179.9, -85, 179.9, 84))
    S['c_' + k] = rings(g, .25, 2)
# water route: lakes -> St Lawrence -> Atlantic
S['route'] = [[-89.5, 47.6], [-87.0, 47.4], [-84.6, 46.6], [-84.2, 46.4], [-83.6, 45.8], [-82.6, 44.6], [-82.4, 43.0], [-82.9, 42.5], [-81.5, 42.25], [-80.0, 42.6],
              [-79.06, 43.1], [-78.0, 43.6], [-76.4, 44.1], [-75.0, 45.0], [-73.6, 45.5], [-71.2, 46.8], [-69.0, 48.2], [-65.5, 49.5], [-61.5, 48.5], [-58.5, 47.2], [-55, 46.5]]
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
