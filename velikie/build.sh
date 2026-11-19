#!/bin/bash
# ./build.sh -> out/velikie_ru.mp4 (1080x1920, with music)
set -e; L=ru; N=velikie; cd "$(dirname "$0")"; mkdir -p out/$L
python3 - <<'PY'
import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.0, 2),
     'whoosh': [B[k] for k in ['five', 'pct', 'spread', 'cm', 'big', 'oth', 'sea', 'storm', 'ships', 'conn', 'ppl', 'great', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['usa', 'can', 'gl', 'sup', 'mic', 'hur', 'eri', 'ont', 'n20', 'n23', 'am', 'af', 'eu', 'au', 'an', 'n15', 'aut', 'cze', 'irl', 'pan', 'wave', 'n350', 'ef', 'law', 'atl', 'n40', 'n4000', 'grt2']]
            + [B['bal'] + .4 + i * .32 for i in range(5)],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v21.mp4
ffmpeg -loglevel error -y -i out/$L/v21.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/${N}_$L.mp4
echo built
