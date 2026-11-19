#!/bin/bash
# ./build.sh ru|kk -> out/teniz_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['area'], B['ocean'] + .3, B['rec'] + .3, B['pole'] + .3, B['far'] + .5, B['ent'], B['uzb'], B['two'] + 1.42, B['cta'], B['vend'] + .4],
     'pop': [B['f3'] + .43 + .18 * i for i in range(3)] + [B['eu'] + .9 + .32 * i for i in range(5)] + [B['ocean'] + 1.6 + .25 * i for i in range(4)]
            + [B['casp'], B['rec'] + 1.0, B['pole'] + 1.0, B['far'] + 1.0, B['alm'] + .8, B['plus'] + .8, B['uzb'] + .4, B['two'] + 1.6, B['two'] + 2.2, B['cta'] + .3],
     'boom': [B['rec'] + 2.7], 'drum': [], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['area'] + .2, B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/teniz_$L.mp4
echo built $L
