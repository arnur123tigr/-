#!/bin/bash
# ./build.sh ru|kk -> out/baikonur_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [B['date'], B['y91'], B['so'], B['print'], B['day'], B['q'], B['cta'], B['vend'] + .6],
     'pop': [.2, B['date'] + 1.4, B['ent'] + .1, B['y91'] + .1, B['y91'] + .8, B['rub'], B['rub'] + .6, B['y93'] + .2, B['y93'] + .7, B['price'],
             B['art'], B['a1'], B['a2'], B['a3'], B['a4'], B['print'] + .8, B['print'] + 1.4, B['print'] + 1.9, B['fly'] + .2, B['ppl'] + .3,
             B['d15'] + .1, B['d15'] + 1.0, B['rate'], B['rate'] + .5, B['own'] + 1.2, B['day'], B['day'] + .2, B['word'] + 1.2, B['word'] + 2.0,
             B['when'] + .8, B['when'] + 1.25, B['when'] + 1.7, B['ans'] + .8, B['cta'] + .6, B['cta'] + .9],
     'boom': [B['nobody'] + .2, B['op'] + .4, B['so'] + .5, B['d15'] - .55, B['cta'] + .2], 'drum': [[B['flood'], B['price'] + .3]], 'clang': [B['rate'] + 1.3],
     'tick': [B['_p0'] + i * .5 for i in range(int((B['ans'] - B['_p0']) / .5))] + [B['date'] + i * .09 for i in range(14)], 'ding': [B['ans'], B['word']]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/tenge_$L.mp4
echo built $L
