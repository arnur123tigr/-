#!/bin/bash
# ./build.sh ru|kk -> out/aral_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['st1'], B['st2'], B['st3'], B['dam'], B['cta'], B['vend'] + .4],
     'pop': [B['q'] + 1.9, B['s3'] + .5, B['s3'] + .7, B['s3'] + .9, B['twist']] + [B[k] + d for k, d in [('st1', .5), ('lake4', 0), ('ltu', 0), ('cotton', 0), ('ships', 0), ('ships', .2), ('aralkum', 0), ('kok', 0), ('fish', -.2), ('cta', .2)]],
     'boom': [B['st3'] + 1.6], 'drum': [[B['st3'] + .6, B['kum'] - .2]], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['north'], B['fish'], B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/aral_$L.mp4
echo built $L
