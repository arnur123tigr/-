"""shapes.json for the British weather reel (Natural Earth 10m, public domain)."""
import json, sys
sys.path.insert(0, '../_shared'); from geo import *
C = countries()
WET = ['COL','PNG','SLB','PAN','CRI','MYS','BRN','IDN','PHL','SLE','LBR','BRA','PER','ECU','VEN','GUY','SUR','NIC','HND','GTM','JPN','NZL','VNM','THA','LKA','BGD','MMR','KHM','LAO','GAB','CMR','COD','COG','CIV','GIN','GNB','MDG','BTN','FJI','VUT','GNQ','GHA','TGO','BEN','NGA','CAF','BLZ','SLV','DOM','HTI','JAM','CUB','BOL','PRY','URY','NPL','KOR','PRK','TWN','CHE','AUT','SVN','NOR','ISL','HRV','MNE','BIH','ALB','GEO','UGA','RWA','BDI']
S = {'GBR': rings(C['GBR'], .01, .002), 'IRL': rings(C['IRL'], .01, .002), 'COL': rings(C['COL'], .02, .005), 'WET': [], 'borders': []}
for k in WET:
    if k in C: S['WET'] += rings(C[k], .05, .02)
for k in ['FRA','BEL','NLD','DEU','NOR','DNK','ESP','PRT','ISL','SWE','POL','ITA','CHE','AUT','CZE']: S['borders'] += rings(C[k], .03, .01)
print(len([k for k in WET if k in C]), 'wet countries')
json.dump(S, open('shapes.json', 'w')); print({k: len(v) for k, v in S.items()})
