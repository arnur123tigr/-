#!/bin/bash
# ./build.sh ru|kk -> out/oguz_<lang>.mp4 (with music) and out/oguz_<lang>_no_music.mp4, 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 3.0, 2),
     'whoosh': [1.0] + [B[k] for k in ['c8', 'syr', 'state', 'selj', 'y1040', 'anc', 'quiz', 'cta']] + [B['vend'] + .6],
     'pop': [.25, .7, 1.7] + [B[k] + d for k, d in [('karluk', 0), ('cap', .2), ('kazaly', 0), ('ent', .2), ('seljname', 0), ('desc', .9), ('iran', 0), ('turk', .1), ('tkm', .1), ('aze', .1),
                                                ('lang', 0), ('opts', -.1), ('o2', -.1), ('o3', -.1), ('quiz', .1), ('jank', .3)]],
     'boom': [1.25, B['anat']], 'clang': [B['manz'], B['manz'] + .25], 'drum': [[B['seljname'], B['y1040']]],
     'tick': [B['pause'] + .15 + i * .5 for i in range(6)], 'ding': [B['ans'], B['link'] + .2]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; cp vo_${L}_p.wav out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
for v in "" _no_music; do
  ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L$v.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/oguz_$L$v.mp4
done
echo built $L
