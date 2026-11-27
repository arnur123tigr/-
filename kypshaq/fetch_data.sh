#!/usr/bin/env bash
# Public-domain / open sources for the steppe-to-Danube textures and vectors (into data/). Then: python3 prep_map.py
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p data/dem
get() { [ -s "$2" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$2" "$1"; }
NASA=https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/july
get "$NASA/world.topo.bathy.200407.3x21600x21600.C1.jpg" data/C1.jpg &
for n in ne_10m_admin_0_boundary_lines_land ne_10m_admin_0_countries ne_10m_rivers_lake_centerlines ne_10m_lakes; do
  get "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/$n.geojson" "data/$n.geojson"
done
# Terrarium elevation tiles: z5 for the steppe window, z8 for the Hungary detail window
python3 - <<'PY' | xargs -P 16 -n 3 sh -c 'f="data/dem/$1_$2_$3.png"; [ -s "$f" ] || curl -fsSL --retry 4 --retry-delay 2 -o "$f" "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/$1/$2/$3.png" || true' _
import math
def t(lon, lat, z):
    n = 2 ** z; lat = max(-85, min(85, lat))
    return int((lon + 180) / 360 * n), int((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n)
for z, (l0, l1, a0, a1) in ((6, (4, 90, 32, 62)), (8, (14, 24, 44, 50))):
    x0, y0 = t(l0, a1, z); x1, y1 = t(l1, a0, z)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1): print(z, x, y)
PY
wait
echo "data/ is ready"
