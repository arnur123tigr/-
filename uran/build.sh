#!/bin/bash
# ./build.sh ru|kk -> out/uran_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['p1'], B['y09'], B['p2'], B['coal'] - .1, B['ent'], B['p3'], B['steppe'], B['fuel'] + .4, B['cta'], B['vend'] + .4],
     'pop': [1.9, B['u'] + .05] + [B['f3'] + .43 + .18 * i for i in range(3)] + [B['pct'] + .3 + .25 * i for i in range(4)] + [B['most'], B['y09'] + 2.6]
            + [B['sands'], B['sands'] + .4, B['coal'] + .2, B['coal'] + .9, B['ent'] + .5, B['ent'] + .7, B['where'] + .3, B['sol'] + .2, B['rise'] + .2, B['rise'] + 1.2]
            + [B['fuel'] + 1.6 + .2 * i for i in range(5)] + [B['cta'] + .3],
     'boom': [B['most'] + .1], 'drum': [], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['kz'] + .1, B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/uran_$L.mp4
echo built $L
