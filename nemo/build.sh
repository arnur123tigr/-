#!/bin/bash
# ./build.sh ru|kk -> out/nemo_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['s1'], B['s2'], B['ent'] + .1, B['s3'], B['cta']] + [B['vend'] + .4],
     'pop': [2.0, 2.3, B['f3'] + .43, B['f3'] + .61, B['f3'] + .79] + [B[k] + d for k, d in [('s1', 1.4), ('s1', 1.75), ('s1', 2.1), ('km', 0), ('almaty', .5), ('water', 0), ('iss400', 0), ('closer', 0), ('pac', 0), ('iss2', .2), ('cta', .3)]],
     'boom': [B['grave'], B['mir2001'] + 1.2], 'drum': [[B['drop'], B['grave']]],
     'tick': [], 'clang': [B['ent'] + .1], 'ding': [B['iss400'], B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/nemo_$L.mp4
echo built $L
