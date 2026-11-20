#!/bin/bash
# ./build.sh ru|kk -> out/saiga_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['reg'], B['nose'], B['e1'], B['e2'], B['ent'], B['e3'], B['iucn'], B['cta'], B['vend'] + .4],
     'pop': [B['st3'] + .43 + .18 * i for i in range(3)] + [B['reg2'] + .55 * i for i in range(3)] + [B['nose2'] + .1, B['nose2'] + .6, B['nose2'] + 1.0,
             B['e1b'], B['e1b'] + 1.2, B['e2b'], B['e2b'] + 1.2, B['ent2'] + .5, B['ent2'] + .8, B['ent2'] + 1.1, B['ent2'] + 1.4, B['e3b'], B['cnt'],
             B['alm'] + .1, B['alm'] + .4, B['iucn'] + 1.3, B['all'] + .4, B['cta'] + .3, 1.0],
     'boom': [B['e2n'] - .2], 'drum': [[B['cnt'] + .3, B['cnt'] + 2.3]], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['cnt'] + 2.3, B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/saiga_$L.mp4
echo built $L
