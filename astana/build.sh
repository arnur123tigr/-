#!/bin/bash
# ./build.sh ru|kk -> out/astana_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['n2'], B['jan'], B['c1'] + .3, B['c2'] + .3, B['c3'] + .3, B['ent'], B['but'] + .2, B['cta'], B['vend'] + .4],
     'pop': [1.9, B['how'], B['n2'] + .6, B['n2'] + .85, B['n2'] + 1.1, B['n2'] + 1.35] + [B['r3'] + .2 + .18 * n for n in (1, 2, 3)]
            + [B['c1'] + 1.4, B['c1'] + 1.6, B['warm'] + 1.6, B['c2'] + .9, B['c2'] + 1.6, B['c3'] + 1.6, B['frost'], B['sum'] + .2, B['win'] + .2, B['kip'] + .1, B['kip'] + .7, B['cta'] + .3],
     'boom': [B['jan'] + 1.0, B['diff'] + .1], 'drum': [], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['n2'] + .2, B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/astana_$L.mp4
echo built $L
