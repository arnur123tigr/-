#!/bin/bash
# ./build.sh ru|kk -> out/balkhash_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [B['bal'] + .1, B['len'] + .1, B['mid'] + .2, B['ans'] + .3, B['west'], B['east'] + .1, B['mix'], B['threat'] + .1, B['quiz'], B['cta'], B['vend'] + .4],
     'pop': [B['fr'], B['sa'], B['bal'] + .5, B['len'] + 1.0, B['narrow'], B['uzy'] + .3, B['uzyw'], B['salt'], B['src'] + .5, B['p80'] - .1, B['sun'] + .3, B['saltst'], B['mix'] + .7,
             B['salty'] + .4, B['fields'], B['fields'] + .25, B['fields'] + .5, B['fields'] + .75, B['fields'] + 1.0, B['aral'] - .1, B['o1'] - .1, B['o2'] - .1, B['o3'] - .1, B['cta'] + .2],
     'boom': [B['s1b'] - .4], 'drum': [], 'clang': [B['ent'] + .1, B['threat']],
     'tick': [B['o3'] + .7 + i * (B['right'] - B['o3'] - .7) / 3 for i in range(3)], 'ding': [B['right'], B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; cp vo_${L}_x.wav out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/balkhash_$L.mp4
echo built $L
