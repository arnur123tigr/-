#!/bin/bash
# ./build.sh ru|kk -> out/granica_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['f1'], B['lon'], B['f2'] + .4, B['split'], B['f3'] + .4, B['ent'], B['dem'] + .3, B['cta'], B['vend'] + .4],
     'pop': [1.4, B['s2'] + .1, B['s2'] + 1.15, B['s2'] + 1.3, B['s2'] + 1.45, B['f1'] + .2, B['km'], B['lon'] + .8, B['lon'] + 1.2, B['lon'] + 1.6,
             B['f2'] + 1.3, B['split'] + .3, B['split'] + .45, B['alaska'], B['rec'], B['five'] - .2, B['five'], B['five'] + .2, B['five'] + .4, B['five'] + .6,
             B['dem'] + 1.0, B['posts'] - .2, B['cta'] + .2],
     'boom': [B['split'] + .3], 'drum': [], 'tick': [], 'clang': [B['ent'] + .3], 'ding': [B['lon'] + 2.3, B['nine'] + .8, B['rec'], B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/granica_$L.mp4
echo built $L
