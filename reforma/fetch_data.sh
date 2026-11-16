#!/usr/bin/env bash
# Downloads the public-domain sources that prep_map.py turns into the parchment map (into data/).
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }
for n in ne_50m_land ne_10m_lakes ne_10m_rivers_lake_centerlines ne_10m_admin_1_states_provinces ne_10m_admin_0_countries; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done
# Terrarium elevation tiles (Mapzen / AWS Open Data), zoom 6 over 40..92 E, 34..58 N
for x in $(seq 39 48); do for y in $(seq 19 25); do echo "6 $x $y"; done; done | xargs -P 16 -n 3 sh -c '
  f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png"' _
echo ok
