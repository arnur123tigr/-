#!/bin/bash
# ./build.sh -> out/uae_ru.mp4 and out/uae_ru_no_music.mp4 (1080x1920)
set -e; L=ru; cd "$(dirname "$0")"; mkdir -p out/$L
python3 - <<'PY'
import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.0, 2),
     'whoosh': [B[k] for k in ['me', 'area', 'seven', 'usa', 'emname', 'family', 'council', 'trad', 'adcity', 'dubai', 'sky', 'mall', 'palm', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['uae', 'ad', 'du', 'country', 'official', 'prt', 'aut', 'name', 'sheikh', 'president', 'adsheikh', 'pct', 'capital', 'ducity', 'burj', 'vatican']]
            + [B['seven'] + .4 + i * .18 for i in range(7)],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v21.mp4
for v in "" _no_music; do
  ffmpeg -loglevel error -y -i out/$L/v21.mp4 -i out/$L/mix_$L$v.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/uae_$L$v.mp4
done
echo built
