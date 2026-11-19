#!/bin/bash
# ./build.sh ru|kk -> out/brazil_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['s2'], B['st1'], B['st2'], B['st3'], B['grow'], B['ent'], B['twist'], B['cta'], B['vend'] + .4],
     'pop': [1.0, 1.7, B['why'], B['s2'] + .2, B['steps'] + .15, B['steps'] + .3, B['steps'] + .45, B['st1'] + .3, B['st1'] + .7, B['st1'] + .9, B['argue'],
             B['st2'] + .3, B['west'], B['east'], B['edge'], B['c1500'] - .4, B['grow'] + .2, B['fifth'], B['ent'] + 2.3, B['ent'] + 2.7, B['ent'] + 3.1,
             B['disc'], B['twist'] + .3, B['ptg'] - .6, B['cta'] + .2],
     'boom': [B['split'] - .2], 'drum': [], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['x20'], B['fifth'] + .3, B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/brazil_$L.mp4
echo built $L
