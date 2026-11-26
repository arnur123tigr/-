#!/usr/bin/env bash
# Public-domain / open sources for the Africa rift reel (into data/). Then: python3 prep_map.py
# tex/world.jpg comes from tyn/ (<- kaganat/): NASA Blue Marble whole globe.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }
NASA=https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july
for t in B1 B2 C1 C2; do get "$NASA/world.topo.bathy.200407.3x21600x21600.$t.jpg" data/$t.jpg & done; wait
for n in ne_10m_admin_0_boundary_lines_land ne_10m_admin_0_countries ne_10m_lakes ne_10m_roads; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done
# tectonic plates: Peter Bird PB2002 (ODC-By), GeoJSON by fraxen/tectonicplates
get https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json data/pb_boundaries.json
get https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_plates.json data/pb_plates.json
# Terrarium elevation tiles: zoom 6 for Africa lon -20..60 lat -36..40, zoom 8 for the rift lon 28..50 lat -12..18
tiles() { python3 -c "
import math,sys
z,l0,l1,a0,a1=map(float,sys.argv[1:]);z=int(z);n=2**z
X=lambda l:int((l+180)/360*n);Y=lambda a:int((1-math.log(math.tan(math.radians(a))+1/math.cos(math.radians(a)))/math.pi)/2*n)
[print(z,x,y) for x in range(X(l0),X(l1)+1) for y in range(Y(a1),Y(a0)+1)]" "$@"; }
{ tiles 6 -20 60 -36 40; tiles 8 28 50 -12 18; } | xargs -P 24 -n 3 sh -c '
  f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png"' _
echo "data/ is ready"
