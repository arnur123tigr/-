#!/usr/bin/env bash
# Downloads the public-domain sources for the map (into data/). Only needed to rebuild tex/detail.jpg and shapes.json:
# the reel itself runs from the files already in the folder. Then: python3 prep_map.py && python3 fix_lakes.py
# (tex/main.jpg, tex/world.jpg and dem.bin come from kaganat/ via shyrak/, the Aral there is already filled to its 1960 shore).
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }
NASA=https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july
get "$NASA/world.topo.bathy.200407.3x21600x21600.C1.jpg" data/C1.jpg          # NASA Blue Marble NG, July, 0..90E, 90N..0
for n in ne_50m_admin_0_boundary_lines_land ne_10m_admin_0_countries ne_10m_rivers_lake_centerlines ne_10m_lakes ne_10m_lakes_historic; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done
# Terrarium elevation tiles, zoom 8, lon 56..84, lat 40..54
for x in $(seq 167 188); do for y in $(seq 82 97); do echo "8 $x $y"; done; done | xargs -P 16 -n 3 sh -c '
  f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png"' _
echo "data/ is ready"
