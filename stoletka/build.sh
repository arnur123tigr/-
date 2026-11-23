#!/bin/bash
# ./build.sh ru|kk -> out/stoletka_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
W = json.load(open(f'words_{L}.json')); tf = next((w[0] + .3 for w in W if '116' in w[2]), B['trap'] - 1.0)
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [B['why'] + .1, B['lands'], B['throne'], B['truce'], B['lose'], B['y1429'] - .2, B['burn'] - .1, B['turn'], B['roses'] + .2, B['ent'], B['cta'], B['vend'] + .4],
     'pop': [.5, tf + .2, B['rem'] + .3, B['rem'] + 1.6, B['lands'] + 2.2, B['lands'] + 2.9, B['lands'] + 3.6, B['lands'] + 4.3, B['throne'] + .4, B['plague'], B['jac'] + .7, B['tyler'] + .7,
             B['lose'] + .2, B['orl'] + .5, B['girl'] + .2, B['name'], B['y1429'] + .2, B['age19'], B['calais'], B['roses'] + .4, B['q'], B['q'] + .8, B['q'] + 1.3, B['q'] + 1.8, B['cta'] + .4],
     'boom': [tf - .1, B['y1453'] + .2], 'drum': [[0, 1.0], [B['turn'] - .1, B['y1453'] + .15]], 'tick': [B['ans'] - 3.0, B['ans'] - 2.0, B['ans'] - 1.0],
     'clang': [B['trap'] + .1, B['ent'] + .1], 'ding': [B['ans'] + .1, B['burn'], B['cta'] + .4]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -shortest -movflags +faststart out/stoletka_$L.mp4
echo built $L
