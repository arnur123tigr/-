#!/bin/bash
# Kazakh version: python3 make_kk.py (free Edge voice kk-KZ-DauletNeural) -> vo_kk_raw.wav + tmap_kk.json, then this script.
# Animation is time-remapped per shot to the Kazakh voice (scene.html?lang=kk loads kk.js + tmap_kk.json).
set -e; cd "$(dirname "$0")"
ffmpeg -v error -y -i vo_kk_raw.wav -ar 48000 -af "highpass=f=60,equalizer=f=3000:t=q:w=1.2:g=1.5" vo_kk.wav
LANG_Q=kk python3 sfx.py
DUR=$(python3 -c "import json;print(json.load(open('tmap_kk.json'))['dur'])")
[ "$SKIP_RECORD" = 1 ] || LANG_Q=kk DUR=$DUR node record.js video_silent_kk.mp4 30
mix(){ # $1 = music volume, $2 = output
  F="[1:a]aresample=48000,apad=whole_dur=$DUR,volume=1.6,asplit=2[v][vk];[2:a]aresample=48000,volume=0.25[s];[3:a]aresample=48000,volume=$1[m];[s][m]amix=inputs=2:normalize=0:duration=first[bed];[bed][vk]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350:makeup=1[duck];[v][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.5:attack=2:release=60:level=false"
  J=$(ffmpeg -hide_banner -i video_silent_kk.mp4 -i vo_kk.wav -i sfx_kk.wav -i music_kk.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -loglevel error -y -i video_silent_kk.mp4 -i vo_kk.wav -i sfx_kk.wav -i music_kk.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ac 2 -t $DUR -movflags +faststart "$2"
  echo "done $2"
}
mix 0.10 jasalash_kk.mp4
mix 0 jasalash_kk_no_music.mp4
