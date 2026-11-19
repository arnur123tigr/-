#!/bin/bash
# ./build.sh ru|kk -> out/nemo_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.2, 1.0, B['s3'], B['s4'], B['s5'], B['s6'], B['s8'], B['cta'], B['vend'] + .4],
     'pop': [2.1, 2.4, 2.7, B['two'] + .4, B['two'] + .9, B['second'] + .6, B['s3'] + 1.2, B['s3'] + 1.5, B['s3'] + 1.7, B['chim'] - .1, B['near'] + .6,
             B['s6'], B['s6'] + .9, B['farther'], B['geoid'] - .2, B['poles'] - .1, B['s8'] + .5, B['stars'] + .5, B['volc'] - .2, B['cta'] + .3],
     'boom': [B['km2'] - .1], 'drum': [[B['s3'] + .3, B['s3'] + 1.7]],
     'tick': [], 'clang': [B['ent'] + .05], 'ding': [B['q'], B['nocomp'], B['km2'], B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/chimborazo_$L.mp4
echo built $L
