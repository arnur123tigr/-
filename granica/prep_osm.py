"""OpenStreetMap extract (api.openstreetmap.org /api/0.6/map, 6 tiles over lon 68.55-69.45, lat 54.95-55.62, north of Petropavlovsk) -> osm.json:
roads, rivers, fields/forests, villages, buildings and the state border (admin_level 2) for the 'down to the streets' shot. Data © OSM contributors, ODbL."""
import json, xml.etree.ElementTree as ET
from collections import Counter
import glob
FILES = sorted(glob.glob('/home/user/data/osm_*.xml'))   # 6 tiles covering lon 68.55-69.45, lat 54.95-55.62
ROOT = ET.Element('osm'); seen = set()
for f in FILES:
    for e in ET.parse(f).getroot():
        k = (e.tag, e.get('id'))
        if e.tag in ('node', 'way', 'relation') and k not in seen: seen.add(k); ROOT.append(e)
T = ROOT
N = {n.get('id'): (round(float(n.get('lon')), 5), round(float(n.get('lat')), 5)) for n in T.iter('node')}
out = {'road': [], 'track': [], 'water': [], 'field': [], 'forest': [], 'res': [], 'bld': [], 'border': [], 'place': []}
tags = Counter()
for w in T.iter('way'):
    tg = {t.get('k'): t.get('v') for t in w.iter('tag')}; pts = [N[n.get('ref')] for n in w.iter('nd') if n.get('ref') in N]
    if len(pts) < 2: continue
    h = tg.get('highway')
    if h in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential'): out['road'].append([h[:3]] + pts)
    elif h in ('track', 'service'): out['track'].append(pts)
    elif 'waterway' in tg or tg.get('natural') == 'water': out['water'].append([tg.get('natural', 'line')] + pts)
    elif tg.get('landuse') in ('farmland', 'meadow', 'grass'): out['field'].append(pts)
    elif tg.get('landuse') == 'forest' or tg.get('natural') in ('wood', 'scrub'): out['forest'].append(pts)
    elif tg.get('landuse') in ('residential',): out['res'].append(pts)
    elif 'building' in tg: out['bld'].append(pts)
    for k in tg: tags[k] += 1
for r in T.iter('relation'):
    tg = {t.get('k'): t.get('v') for t in r.iter('tag')}
    if tg.get('admin_level') == '2' and tg.get('boundary') == 'administrative': print('border relation', tg.get('name'))
for n in T.iter('node'):
    tg = {t.get('k'): t.get('v') for t in n.iter('tag')}
    if tg.get('place') in ('village', 'town', 'hamlet', 'city'): out['place'].append([tg.get('name:ru') or tg.get('name'), float(n.get('lon')), float(n.get('lat')), tg['place']])
# border: ways that belong to admin_level=2 relations
WAYS = {w.get('id'): w for w in T.iter('way')}
for r in T.iter('relation'):
    tg = {t.get('k'): t.get('v') for t in r.iter('tag')}
    if tg.get('admin_level') == '2':
        for m in r.iter('member'):
            if m.get('type') == 'way' and m.get('ref') in WAYS:
                pts = [N[n.get('ref')] for n in WAYS[m.get('ref')].iter('nd') if n.get('ref') in N]
                if len(pts) > 1 and pts not in out['border']: out['border'].append(pts)
json.dump(out, open('osm.json', 'w'), separators=(',', ':'))
import os; print({k: len(v) for k, v in out.items()}, os.path.getsize('osm.json') // 1024, 'KB'); print(out['place']); print(tags.most_common(25))
