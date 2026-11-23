#!/bin/bash
# audio only (to check the mix before recording)
set -e; L=$1; cd "$(dirname "$0")"; sed -n '/^L=\$L python3/,/^PY$/p' build.sh > /tmp/cues_$L.sh; mkdir -p out/$L; L=$L bash /tmp/cues_$L.sh
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav; (cd out/$L && python3 sfx.py && python3 mix.py $L)
