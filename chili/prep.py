"""shapes.json for the Chile reel (Natural Earth 10m, public domain). Historical shapes are simplified approximations."""
import json, sys
from math import cos, sin, radians, atan2, degrees, hypot
sys.path.insert(0, '../_shared'); from geo import *
from shapely import transform as stransform
import numpy as np
C = countries()
SAc = 'CHL PER BOL ARG BRA PRY URY COL VEN ECU GUY SUR PAN'.split()
S = {}
for k in SAc: S[k] = rings(C[k], .03, .003)
SA = unary_union([C[k] for k in SAc[:-1]] + [C['FRA'].intersection(box(-55, 1, -51, 6.5))])
S['SA'] = rings(SA.buffer(.02), .05, .02)
band = lambda g, a, b: g.intersection(box(-90, a, -30, b))
CHL = C['CHL'].intersection(box(-80, -60, -60, -15))           # mainland + nearby islands, no Easter Island
S['CHL'] = rings(CHL, .02, .002)
S['CHL_EARLY'] = rings(band(CHL, -37.6, -24.0), .02, .003)
S['ARAUC'] = rings(band(CHL, -41.2, -37.6), .03, .01)
S['COAST'] = rings(band(CHL, -24.0, -17.4), .02, .003)
S['BOL_OLD'] = rings(C['BOL'].union(band(CHL, -24.0, -21.4)).buffer(.01), .02, .003)
S['PER_OLD'] = rings(C['PER'].union(band(CHL, -21.4, -17.4)).buffer(.01), .02, .003)
POR = C['BRA'].intersection(box(-50.5, -35, -30, 6))
SOUTH = SA.intersection(box(-90, -60, -30, -38.0))
S['POR'] = rings(POR, .05, .05); S['SPA'] = rings(SA.difference(POR).difference(SOUTH).buffer(.01), .05, .05); S['SOUTH'] = rings(SOUTH, .05, .05)
S['GRAN'] = rings(unary_union([C[k] for k in ['COL', 'VEN', 'ECU', 'PAN']]).buffer(.01), .04, .02)
S['PLATA'] = rings(unary_union([C['ARG'], C['URY'], C['PRY']]).intersection(box(-90, -38, -30, 0)).buffer(.01), .04, .02)
S['ANDES'] = rings(region('ANDES'), .05, .05)
# Chile laid over Europe at true size, from London to Baghdad
lon0, lat0 = -71.0, -37.0
ext = list(CHL.intersection(box(-80, -56.2, -60, -17.4)).geoms if hasattr(CHL, 'geoms') else [CHL])
def tokm(x, y): return ((x - lon0) * cos(radians(y)) * 111.32, (y - lat0) * 110.57)
L, Bg = (-0.13, 51.51), (44.37, 33.31)
mlon, mlat = (L[0] + Bg[0]) / 2, (L[1] + Bg[1]) / 2
dx, dy = (Bg[0] - L[0]) * cos(radians(mlat)) * 111.32, (Bg[1] - L[1]) * 110.57
ang = atan2(dy, dx)                       # direction London->Baghdad
north, south = tokm(-70.3, -17.5), tokm(-68.6, -55.9)
ca = atan2(south[1] - north[1], south[0] - north[0])   # Chile north->south direction
rot = ang - ca; cx_, cy_ = (north[0] + south[0]) / 2, (north[1] + south[1]) / 2
print('Chile length km', round(hypot(south[0] - north[0], south[1] - north[1])), 'London-Baghdad km', round(hypot(dx, dy)))
def f(arr):
    out = []
    for x, y in arr:
        a, b = tokm(x, y); a -= cx_; b -= cy_
        u, v = a * cos(rot) - b * sin(rot), a * sin(rot) + b * cos(rot)
        la = mlat + v / 110.57; lo = mlon + u / (111.32 * cos(radians(la)))
        out.append((lo, la))
    return np.array(out)
CEU = stransform(CHL.intersection(box(-80, -56.2, -60, -17.4)), f)
S['CHL_EU'] = rings(CEU, .02, .003)
S['borders'] = []
for k, g in C.items():
    b = g.bounds
    if (b[2] > -95 and b[0] < -30 and b[1] < 15) or (b[2] > -12 and b[0] < 60 and b[3] > 25 and b[1] < 62): S['borders'] += rings(g, .04, .02)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
