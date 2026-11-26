#!/usr/bin/env bash
# Public-domain sources for the detail textures and the vectors (into data/). Then: python3 prep_map.py
# tex/main.jpg, tex/world.jpg and dem.bin come from tyn/ (<- kulja/ <- semey/ <- kaganat/): NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }
NASA=https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july
get "$NASA/world.topo.bathy.200407.3x21600x21600.C1.jpg" data/C1.jpg
for n in ne_10m_admin_0_boundary_lines_land ne_10m_admin_0_countries ne_10m_rivers_lake_centerlines ne_10m_rivers_europe ne_10m_lakes ne_10m_geography_marine_polys ne_10m_land ne_10m_lakes_historic; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done
# Terrarium elevation tiles, zoom 7: Levant (Dead Sea), Aral, Baltic
{ for x in $(seq 75 77); do for y in $(seq 51 53); do echo "7 $x $y"; done; done
  for x in $(seq 84 86); do for y in $(seq 44 47); do echo "7 $x $y"; done; done
  for x in $(seq 66 75); do for y in $(seq 32 41); do echo "7 $x $y"; done; done; } | xargs -P 16 -n 3 sh -c '
  f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png"' _
echo "data/ is ready"
