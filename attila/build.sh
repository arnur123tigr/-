#!/bin/bash
# ./build.sh ru|kk -> out/attila_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [B['hun'] + .1, B['y370'], B['mig'] + .6, B['pann'] + .9, B['const'] - .25, B['gold'] + 1.8, B['bich'] + .8, B['gaul'] + .2, B['ital'] + .3, B['fall'] + .4, B['ent'], B['cta'], B['vend'] + .4],
     'pop': [.5, B['hun'] + .6, B['hyp'], B['but'] + .9, B['y370'] + 1.2, B['y375'] + .6, B['pann'] + .4, B['att'] + .3, B['gold'] + .3, B['gaul'] + .5, B['cat'] + 1.0, B['ital'] + .6, B['jord'], B['cta'] + .5],
     'boom': [B['y375'] + 1.5, B['cat'] + .6, B['died'] + 1.0], 'drum': [[0, 1.2], [B['vend'] - 1.4, B['vend'] + .05]], 'clang': [B['cat'] + .6],
     'tick': [B['gold'] + 1.4 + i * .17 for i in range(10)], 'ding': [B['e1'] + .3, B['e2'] + .3, B['e3'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/attila_$L.mp4
echo built $L
