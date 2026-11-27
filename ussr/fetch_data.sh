#!/usr/bin/env bash
# Public-domain sources for the Karagiye reel (into data/). Then: python3 prep_map.py
# tex/main.jpg, tex/world.jpg and dem.bin come from tyn/ (<- kulja/ <- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }
NASA=https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july
get "$NASA/world.topo.bathy.200407.3x21600x21600.C1.jpg" data/C1.jpg
for n in ne_10m_admin_0_boundary_lines_land ne_10m_admin_0_countries ne_10m_lakes; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done
# Terrarium elevation tiles: z9 Mangystau + Atyrau (lon 48..56, lat 41..48.5) and Khan Tengri (lon 78.5..81.5, lat 41.5..43.3); z7 lon 44..82, lat 40..50.5
{ for x in $(seq 324 335); do for y in $(seq 176 191); do echo "9 $x $y"; done; done
  for x in $(seq 367 371); do for y in $(seq 187 191); do echo "9 $x $y"; done; done
  for x in $(seq 79 93); do for y in $(seq 43 48); do echo "7 $x $y"; done; done; } | xargs -P 16 -n 3 sh -c '
  f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png"' _
echo "data/ is ready"
