#!/bin/bash
# ./build.sh ru|kk -> out/hormuz_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['horm'], B['narrow'], B['oil'], B['kzq'] + .2, B['pipe'] + .3, B['ent'], B['bos'] + .2, B['bos'] + 1.6, B['width'] + .2, B['cta'], B['vend'] + .4],
     'pop': [B['hold'] + 1.3, B['horm'] + .6, B['kz'], B['narrow'] + 1.1, B['talg'] + 1.1, B['talg'] + 1.4, B['oil'] + .3, B['iran'] + .1, B['iran'] + .5, B['price'],
             B['kzq'] + 1.5, B['nosea'], B['pipe'] + 1.4, B['black'] + .1, B['pct'] + .3, B['west'], B['west'] + .25, B['west'] + .5, B['bos'] + 1.9, B['width'] + 1.1, B['width'] + 1.4, B['cta'] + .3],
     'boom': [B['close'] + .5], 'drum': [], 'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['hold'] + .8, B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/hormuz_$L.mp4
echo built $L
