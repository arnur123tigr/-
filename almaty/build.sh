#!/bin/bash
# ./build.sh ru|kk -> out/almaty_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['cul'] - .3, B['s1'] + .2, B['s2'] + .4, B['cm'] + .2, B['s3'] + .3, B['hist'] + .3, B['ent'], B['turn'], B['turn'] + .8, B['cta'], B['vend'] + .4],
     'pop': [B['h1'] + .8, B['h1'] + 1.5, B['h1'] + 1.9] + [B['steps'] + .2 + .15 * n for n in (1, 2, 3)] + [B['s1'] + 1.2, B['grow'], B['s2'] + 1.8, B['cm'] + .2, B['nail'],
            B['s3'] + 2.2, B['alm'], B['y1'], B['y2'] + .2, B['zone'], B['plate'], B['turn'] + 1.8, B['turn'] + 2.6, B['cta'] + .3],
     'boom': [B['h1'] + .5, B['y1'], B['y2'] + .2], 'drum': [[B['s2'] + .6, B['s2'] + 1.6]], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['turn'] + 1.8, B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/almaty_$L.mp4
echo built $L
