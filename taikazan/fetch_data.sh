#!/usr/bin/env bash
# Public-domain sources for the Turkestan detail texture and the vectors (into data/). Then: python3 prep_map.py
# tex/main.jpg, tex/world.jpg and dem.bin come from semey/ (<- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }
NASA=https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july
get "$NASA/world.topo.bathy.200407.3x21600x21600.C1.jpg" data/C1.jpg
for n in; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done
# Terrarium elevation tiles, zoom 9, lon 67..69.5, lat 42.6..44 (Turkestan)
for x in $(seq 351 354); do for y in $(seq 186 189); do echo "9 $x $y"; done; done | xargs -P 16 -n 3 sh -c '
  f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png"' _
echo "data/ is ready"
