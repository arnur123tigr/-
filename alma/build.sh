#!/bin/bash
# ./build.sh ru|kk -> out/alma_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 3, 2),
     'whoosh': [B['alm'] + .3, B['ala'] - .2, B['forest'] + 1.2, B['vav'], B['how'] + .3, B['dna'], B['turn'], B['y1865'], B['red'] + .2, B['q'], B['cta']],
     'pop': [1.0, 2.0, B['alm'] + .1, B['ala'] + .5, B['ala'] + 1.2, B['forest'] + .3, B['siv'], B['vav'] + .1, B['vav'] + .5] + [B['saw'] + .1 + .3 * i for i in range(6)]
            + [B['per'] + .25, B['rim'] + .25, B['evr'] + .45, B['dna'] + .1, B['pred'] + .4, B['aport'] - .1, B['y1865'] + .9, B['y1865'] + 1.8, B['q'], B['oA'] - .1, B['oB'] - .1, B['oC'] - .1, B['cta'] + .3],
     'boom': [B['wrote'] + .6, B['proof'] + .1, B['aport'] + 1.2], 'drum': [], 'clang': [], 'ding': [B['proof'] + .3, B['ans'], B['red'] + .9],
     'tick': [B['oC'] + 1.0 + .5 * i for i in range(int((B['ans'] - B['oC'] - 1.0) / .5))], 'crunch': [.35, B['oC'] + 1.35, B['oC'] + 2.05, B['oC'] + 2.75, B['cta'] + .3],
     'bell': [B['silk'] + .3, B['car'] + .5, B['car'] + 1.6, B['reach']]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/alma_$L.mp4
echo built $L
