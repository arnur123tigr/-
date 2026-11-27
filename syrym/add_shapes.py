"""Adds the shapes of the Syrym reel to shapes.json (after prep_map.py vec, or on top of the committed file).
All historical areas are hand-drawn approximations:
  kishi   the Junior Zhuz (western Kazakhstan, Ural to the Aral and the Syr Darya)
  baib    the pastures of the Baibakty between the Zhaiyk (Ural) and the Oiyl
  ural    the Ural river as one line, upstream (Orenburg) -> the Caspian (Natural Earth centre lines)"""
import json
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union
S = json.load(open('shapes.json'))
kz = Polygon(S['kz'][0]).buffer(0)
rnd = lambda cs: [[round(x, 3), round(y, 3)] for x, y in cs]
def rings(g):
    ps = [g] if isinstance(g, Polygon) else list(g.geoms)
    return [rnd(p.exterior.coords) for p in ps if p.area > .05]
kishi = kz.intersection(Polygon([(45, 40), (62.0, 40), (62.0, 45.5), (63.6, 48.5), (62.4, 52.6), (45, 53)]))
S['kishi'] = rings(kishi)
baib = Polygon([(51.5, 50.55), (52.6, 50.75), (53.8, 50.35), (55.2, 49.75), (55.9, 48.9), (55.3, 48.2), (54.0, 47.95), (52.8, 47.95), (51.95, 48.3), (51.45, 49.3)]).intersection(kz)
S['baib'] = rings(baib)
R = S['rivers']
def near(r, p): return min(abs(x - p[0]) + abs(y - p[1]) for x, y in r)
low = min(R, key=lambda r: near(r, (51.37, 51.23)) + near(r, (51.9, 47.1)))
if low[0][0] < low[-1][0]: low = low[::-1]
S['ural'] = low
c = baib.centroid; S['baib_c'] = [round(c.x, 3), round(c.y, 3)]
c = kishi.centroid; S['kishi_c'] = [round(c.x, 3), round(c.y, 3)]
json.dump(S, open('shapes.json', 'w'), separators=(',', ':'))
print('kishi', len(S['kishi']), 'baib', len(S['baib']), S['baib_c'], 'ural', len(low), low[0], low[-1])
