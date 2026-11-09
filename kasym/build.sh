#!/bin/bash
# Build kasym_kk.mp4 (light study music with clock tick) and kasym_kk_no_music.mp4:
# synth SFX + music -> record frames (canvas, 1080x1920) -> mix VO + SFX (+ music), voice on top, -14 LUFS.
set -e; cd "$(dirname "$0")"
python3 sfx.py
[ "$SKIP_RECORD" = 1 ] || node record.js video_silent.mp4 30
DUR=36
mix(){ # $1 = music volume, $2 = output
  # SFX + music form a bed that ducks (sidechain) whenever the voice speaks; voice starts at 0.1 s
  F="[1:a]aresample=48000,adelay=100:all=1,apad=whole_dur=$DUR,volume=1.5,asplit=2[v][vk];[2:a]aresample=48000,volume=0.25[s];[3:a]aresample=48000,volume=$1[m];[s][m]amix=inputs=2:normalize=0:duration=first[bed];[bed][vk]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=300:makeup=1[duck];[v][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.5:attack=2:release=60:level=false"
  J=$(ffmpeg -hide_banner -i video_silent.mp4 -i vo_kk.mp3 -i sfx.wav -i music.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -loglevel error -y -i video_silent.mp4 -i vo_kk.mp3 -i sfx.wav -i music.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ac 2 -t $DUR -movflags +faststart "$2"
  echo "done $2"
}
mix 0.07 kasym_kk.mp4
mix 0 kasym_kk_no_music.mp4
