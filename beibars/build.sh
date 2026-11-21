#!/bin/bash
# ./build.sh ru|kk -> out/beibars_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [B['show'] + .1, B['capt'] + 1.0, B['egypt'] + .4, B['egypt'] + 3.0, B['mong2'] + .2, B['ain'] + .8, B['sultan'], B['rule'] + .4, B['ent'], B['path'], B['vend'] + .4],
     'pop': [.6, 1.2, B['y1223'] + .3, B['born'] + 1.0, B['mong'] + .6, B['capt'] + 2.3, B['eye'], B['egypt'] + 3.7, B['bow'] + .2, B['gen'] + .2, B['mong2'] + .6, B['mong2'] + 1.1,
             B['mong2'] + 1.5, B['ain'] + .8, B['lead'] + .2, B['first'], B['sultan'] + .8, B['kin'], B['q'], B['opts'], B['opts'] + .9, B['opts'] + 1.8, B['cta']],
     'boom': [B['ain'] + 1.05], 'drum': [[0, 1.0], [B['path'] - 1.2, B['path'] + .05]], 'tick': [B['ans'] - 3.0, B['ans'] - 2.0, B['ans'] - 1.0], 'clang': [B['ent'] + .1],
     'ding': [B['ans'] + .1, B['sultan'] + .5]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/beibars_$L.mp4
echo built $L
