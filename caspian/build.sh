#!/bin/bash
# ./build.sh -> out/caspian_ru.mp4 and out/caspian_ru_no_music.mp4 (1080x1920)
set -e; L=ru; cd "$(dirname "$0")"; mkdir -p out/$L
python3 - <<'PY'
import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.0, 2),
     'whoosh': [B[k] for k in ['largest', 'len', 'storm', 'depth', 'confuse', 'black', 'landlocked', 'why', 'once', 'salt', 'ancient', 'name', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['lake', 'num', 'wave', 'd1000', 'burj', 'salty', 'ocean', 'bosp', 'med', 'gib', 'atl', 'lakeclass', 'para', 'split', 'rivers', 'giant']]
            + [B['five'] + .2 + i * .18 for i in range(5)] + [B['seems'] + .3 + i * .4 for i in range(3)],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v21.mp4
for v in "" _no_music; do
  ffmpeg -loglevel error -y -i out/$L/v21.mp4 -i out/$L/mix_$L$v.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/caspian_$L$v.mp4
done
echo built
