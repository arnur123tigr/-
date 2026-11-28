"""shapes.json for the Panama reel (Natural Earth 10m, public domain)."""
import json, sys
sys.path.insert(0, '../_shared'); from geo import *
C = countries()
S = {'PAN': rings(C['PAN'], .005, .0005), 'borders': []}
for k in ['CRI', 'COL', 'NIC', 'HND', 'SLV', 'GTM', 'MEX', 'VEN', 'ECU', 'BLZ', 'CUB', 'JAM', 'HTI', 'DOM']: S['borders'] += rings(C[k], .02, .005)
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
