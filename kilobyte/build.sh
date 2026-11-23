#!/bin/bash
# ./build.sh ru|kk -> out/kilobyte_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
l0, l1 = B['list'], B['tenth']; d = max(.35, (l1 - l0) / 7)
st = [l0 + i * d if i < 4 else l0 + 4 * d + (l1 - l0 - 4 * d) * (i - 3) / 6 for i in range(10)]
c = {'dur': round(B['vend'] + 2.6, 2),
     'err': [1.2, B['round'] + .2], 'zap': [B[k] for k in ('ent', 'comp', 'byte', 'main', 'kb', 'check', 'q', 'cta')],
     'coin': [B['ent'] + .2, B['bit'] + .2, B['letter'] + .5, B['kb'] + .1],
     'click': [B['off'] + .1, B['on'], B['on'] + .1, B['on'] + .2] + [B['byte'] + i * .07 for i in range(8)] + [B['mult'] + .1],
     'blip': [B['min'], B['small'], B['opts'], B['opts'] + .55, B['opts'] + 1.1, B['check'] + .1, B['qq']],
     'blop': [B['kb'] + .1, B['mb'] + .1, B['gb'] + .1], 'rise': st,
     'ding': [B['tenth'] + .1, B['mult'] + 1.3, 1.5],
     'tick': [B['_p0'] + i * .5 for i in range(int((B['ans'] - B['_p0']) / .5))],
     'clear': [B['ans']], 'fan': [B['cta'] + .1]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/kilobyte_$L.mp4
echo built $L
