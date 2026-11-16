#!/usr/bin/env bash
# Downloads the public-domain sources that prep_map.py turns into tex/, dem.bin and shapes.json (about 380 MB into data/).
# Only needed to rebuild the map; the reel itself runs from the files that are already in the folder.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }

# NASA Blue Marble Next Generation, July, topography + bathymetry: two 500 m tiles (0..90E and 90..180E, 90N..0) and the whole globe
NASA=https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july
get "$NASA/world.topo.bathy.200407.3x21600x21600.C1.jpg" data/C1.jpg
get "$NASA/world.topo.bathy.200407.3x21600x21600.D1.jpg" data/D1.jpg
get "$NASA/world.topo.bathy.200407.3x21600x10800.jpg" data/world.jpg

# Natural Earth vectors: coastline, lakes, country borders, rivers (the Huang He)
for n in ne_50m_land ne_50m_lakes ne_50m_admin_0_boundary_lines_land ne_10m_rivers_lake_centerlines; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done

# Terrarium elevation tiles: the whole world at zoom 4, Eurasia at zoom 7, the Altai at zoom 9
tiles() { local z=$1 x y; for ((x = $2; x <= $3; x++)); do for ((y = $4; y <= $5; y++)); do echo "$z $x $y"; done; done; }
{ tiles 4 0 15 0 15; tiles 7 67 116 18 59; tiles 9 369 393 164 188; } | xargs -P 16 -n 3 sh -c '
  f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png"' _
echo "data/ is ready: $(ls data/dem | wc -l) elevation tiles"
