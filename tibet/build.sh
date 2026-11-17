#!/bin/bash
# ./build.sh ru|kk  -> tibet_<lang>.mp4 and tibet_<lang>_no_music.mp4 (1080x1920)
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
python3 - $L <<'PY'
import json, sys
L = sys.argv[1]; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
end = B['vend'] + 3.0
c = {'dur': round(end, 2),
     'whoosh': [B[k] for k in ['radar', 'name', 'r1', 'plane', 'r2', 'r3', 'cta']] + [B['vend'] + .5],
     'pop': [B['zone']] + [B['five'] + i * .22 for i in range(5)] + [B['empty'], B['name']] + [B['three'] + .25 + i * .3 for i in range(3)]
            + [B['avgnum'], B['everest'], B['plane10'], B['emerg'], B['d3000'], B['imposs'], B['noair'] + .6] + [B['airports'] + .15 + i * .2 for i in range(5)],
     'ding': [B['kw']]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
for v in "" _no_music; do
  ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L$v.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/tibet_$L$v.mp4
done
echo built $L
