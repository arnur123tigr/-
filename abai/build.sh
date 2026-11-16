#!/bin/bash
# ./build.sh kk|ru  -> abai_<lang>.mp4 (light music) and abai_<lang>_no_music.mp4
# timing.py (voice with 3-second pauses + timeline) -> sfx.py -> record frames -> mix (voice on top, -14 LUFS)
set -e; cd "$(dirname "$0")"; L=${1:-kk}
[ -f vo_$L.wav ] || python3 timing.py $L
python3 sfx.py $L && mv sfx.wav sfx_$L.wav && mv music.wav music_$L.wav
[ "$SKIP_RECORD" = 1 ] || LANG_Q=$L node record.js video_silent_$L.mp4 30
DUR=$(python3 -c "import json;print(json.load(open('timeline_$L.json'))['dur'])")
mix(){ # $1 = music volume, $2 = output
  F="[1:a]aresample=48000,apad=whole_dur=$DUR,volume=1.5,asplit=2[v][vk];[2:a]aresample=48000,volume=0.3[s];[3:a]aresample=48000,volume=$1[m];[s][m]amix=inputs=2:normalize=0:duration=first[bed];[bed][vk]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=300:makeup=1[duck];[v][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.5:attack=2:release=60:level=false"
  J=$(ffmpeg -hide_banner -i video_silent_$L.mp4 -i vo_$L.wav -i sfx_$L.wav -i music_$L.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -loglevel error -y -i video_silent_$L.mp4 -i vo_$L.wav -i sfx_$L.wav -i music_$L.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ac 2 -t $DUR -movflags +faststart "$2"
  echo "done $2"
}
mix 0.08 abai_$L.mp4
mix 0 abai_${L}_no_music.mp4
