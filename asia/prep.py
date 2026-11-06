"""Natural Earth 50m countries -> data.js (simplified lon/lat rings for Afro-Eurasia + Australia)."""
import json
G = json.load(open('data/countries50.geojson'))
def dp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1; L = (dx * dx + dy * dy) ** .5 or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [pts[0], pts[-1]]
out = {}
for f in G['features']:
    p = f['properties']; code = p['ADM0_A3']
    g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    rings = []
    for poly in polys:
        r = poly[0]
        if code == 'RUS': r = [[x + 360 if x < -100 else x, y] for x, y in r]
        xs = [x for x, _ in r]; ys = [y for _, y in r]
        if max(xs) < -25 or min(xs) > 192 or max(ys) < -50: continue
        h = len(r) // 2
        s = dp(r[:h + 1], 0.06)[:-1] + dp(r[h:], 0.06)
        if len(s) < 4: continue
        rings.append([[round(x, 2), round(y, 2)] for x, y in s])
    if not rings: continue
    if code == 'RUS':   # split Russia at the Urals (~59E): European part RUE, Asian part RUS
        from shapely.geometry import Polygon, box
        from shapely.validation import make_valid
        parts = {'RUE': box(-30, -90, 59, 90), 'RUS': box(59, -90, 200, 90)}
        for name, bx in parts.items():
            rr = []
            for r in rings:
                g = make_valid(Polygon(r)).intersection(bx)
                for p in getattr(g, 'geoms', [g]):
                    if p.geom_type == 'Polygon' and p.area > 0.01: rr.append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords])
            out[name] = rr
        continue
    out[code] = rings
open('data.js', 'w').write('window.GEO=' + json.dumps(out, separators=(',', ':')) + ';')
print(len(out), sum(len(r) for v in out.values() for r in v), 'pts')
