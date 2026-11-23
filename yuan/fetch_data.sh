#!/usr/bin/env bash
# Downloads the Natural Earth vectors for shapes.json (into data/). The reel itself runs from the files already in the folder.
# tex/ and dem.bin come unchanged from amangeldi/ (NASA Blue Marble, Eurasia lon 10..146.5, lat 12..78). Then: python3 prep_shapes.py
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data
for n in ne_50m_land ne_50m_admin_0_boundary_lines_land; do
  [ -s "data/$n.geojson" ] || curl -fsSL --retry 4 -o "data/$n.geojson" "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson"
done
echo "data/ is ready"
