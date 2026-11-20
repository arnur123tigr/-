#!/bin/bash
# ./build.sh ru|kk -> out/wallace_<lang>.mp4 (with music), 1080x1920
set -e; L=$1; cd "$(dirname "$0")"; mkdir -p out/$L
L=$L python3 - <<'PY'
import json, os
L = os.environ['L']; B = {k: v + .3 for k, v in json.load(open('beats.json'))[L].items()}
c = {'dur': round(B['vend'] + 2.6, 2),
     'whoosh': [.6, B['why'], B['east0'], B['wal'], B['ice0'], B['bali'], B['deep0'] - .2, B['walk'] - .2, B['birds'], B['cta'], B['vend'] + .4],
     'pop': [.8, 2.5, 2.75, B['s2'] + 1.2, B['worlds'], B['worlds'] + .15, B['west'] + .1, B['monk'] - .15, B['tig'] - .15, B['ele'] - .15, B['east'] + .3,
             B['mars'] - .15, B['mars'] + .1, B['cock'] - .15, B['wal'] + .4, B['alf'] - .2, B['y150'], B['ice0'] + .2, B['bali'], B['deep0'] + .1, B['deep'] + .3,
             B['never'], B['wall'], B['birds'] + .1, B['cta'] + .2],
     'boom': [B['stop'] - .05], 'drum': [], 'tick': [], 'clang': [], 'ding': [B['s2'] + 1.2, B['lvl'], B['cta'] + .3]}
json.dump(c, open(f'out/{L}/cues.json', 'w'))
PY
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -shortest -movflags +faststart out/wallace_$L.mp4
echo built $L
