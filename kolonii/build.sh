#!/bin/bash
# ./build.sh -> out/velikie_ru.mp4 (1080x1920, with music)
set -e; L=ru; N=kolonii; cd "$(dirname "$0")"; mkdir -p out/$L
python3 - <<'PY'
import json
B = {k: v + .3 for k, v in json.load(open('beats.json'))['ru'].items()}
c = {'dur': round(B['vend'] + 3.0, 2),
     'whoosh': [B[k] for k in ['war', 'debt', 'look', 'sugar', 'stamp', 'congr', 'boston', 'tea', 'fury', 'cc1', 'lex', 'wash', 'july', 'usa', 'cta']] + [B['vend'] + .5],
     'pop': [B[k] for k in ['y250', 'crown', 'beat', 'lands', 'prot', 'pay', 'molasses', 'sugarI', 'coffee', 'cloth', 'angry', 'news', 'contr', 'lic', 'court', 'cards', 'parl', 'taxes', 'dead', 'cancel', 'teatax', 'n300', 'party', 'port', 'self', 'troops', 'shot', 'washn', 'refuse', 'decl', 'equal']],
     'ding': [B['link'] + .5]}
json.dump(c, open('out/ru/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v21.mp4
ffmpeg -loglevel error -y -i out/$L/v21.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/${N}_$L.mp4
echo built
