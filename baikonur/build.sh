#!/bin/bash
# ./build.sh ru|kk -> out/baikonur_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [B['map'], B['y55'], B['y61'], B['hide'], B['len'], B['rent'], B['ent'], B['q'], B['often'], B['cta'], B['vend'] + .6],
     'pop': [.35, .7, 1.05, 1.2, B['tyur'], B['kzo'], B['kzo'] + .6, B['real'], B['real'] + .3, B['km'] + .5, B['km'] + 1.6, B['y55'] + .3, B['y55'] + 1.3,
             B['noname'], B['noname'] + .5, B['y61'] + .2, B['y61'] + .6, B['y61'] + .8, B['world'] + .3, B['world'] + .6, B['named'] - .2, B['named'] + 1.1,
             B['len'], B['y95'] + .9, B['rent'] + .5, B['rent'] + .9, B['ent'] + .5, B['ent'] + 1.0, B['first'] + 1.0, B['first'] + 1.4, B['first'] + 1.9,
             B['opts'], B['opts'] + .55, B['opts'] + 1.1, B['ans'] + .8, B['often'] + .2, B['often'] + .55, B['often'] + .9, B['cta'] + .4],
     'boom': [B['map'] - 1.0, B['y61'] + .5, B['cta'] + .2], 'drum': [], 'clang': [B['rent'] + 1.6],
     'tick': [B['_p0'] + i * .5 for i in range(int((B['ans'] - B['_p0']) / .5))], 'ding': [B['ans']]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/baikonur_$L.mp4
echo built $L
