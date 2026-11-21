#!/bin/bash
# ./build.sh ru|kk -> out/ozbek_<lang>.mp4 (with music) and out/ozbek_<lang>_no_music.mp4, 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 3.0, 2),
     'whoosh': [1.0] + [B[k] for k in ['show', 'cap', 'go', 'y1468', 'shai', 'quiz', 'two']] + [B['vend'] + .6],
     'pop': [.25, .7, 1.3] + [B[k] + d for k, d in [('c15', 0), ('abul', 0), ('ulus', 0), ('nomad', 0), ('kj', 0), ('kj', .3), ('orys', 0), ('mog', 0), ('shu', 0),
                                                ('esen', 0), ('y1500', 0), ('name', 0), ('today', 0), ('opts', -.1), ('o2', -.1), ('o3', -.1), ('quiz', .1), ('ulus', -.3)]],
     'boom': [1.25, B['kh'], B['sam']], 'clang': [], 'drum': [[B['decide'], B['go'] + .3], [B['y1500'], B['sam']]],
     'ding': [B['cap'] + .3, B['ans'], B['link'] + .2],
     'tick': [B['pause'] + .15 + i * .5 for i in range(6)]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; cp vo_${L}_p.wav out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
for v in "" _no_music; do
  ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L$v.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/ozbek_$L$v.mp4
done
echo built $L
