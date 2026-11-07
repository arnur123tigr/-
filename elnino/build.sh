#!/bin/bash
# Build elnino_ru.mp4 / elnino_ru_no_music.mp4, or with LANG_Q=kk the Kazakh elnino_kk*.mp4:
# synth SFX + music -> record frames (2D canvas) -> mix VO on top (bed ducked under voice), loudness -14 LUFS (two-pass).
set -e; cd "$(dirname "$0")"
L=${LANG_Q:-ru}
if [ "$L" = kk ]; then python3 captions_kk.py >/dev/null; python3 sfx.py kk; VO=vo_kk.mp3; SFX=sfx_kk.wav; MUS=music_kk.wav; DUR=99.2; VS=video_silent_kk.mp4
else python3 captions.py >/dev/null; python3 sfx.py; VO=vo_a.mp3; SFX=sfx.wav; MUS=music.wav; DUR=95.4; VS=video_silent.mp4; fi
[ "$SKIP_RECORD" = 1 ] || node record.js $VS 30
mix(){ # $1 = music volume, $2 = output
  F="[1:a]aresample=48000,adelay=300:all=1,apad=whole_dur=$DUR,volume=1.6,asplit=2[v][vk];[2:a]aresample=48000,volume=0.3[s];[3:a]aresample=48000,volume=$1[m];[s][m]amix=inputs=2:normalize=0:duration=first[bed];[bed][vk]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350:makeup=1[duck];[v][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.5:attack=2:release=60:level=false"
  J=$(ffmpeg -hide_banner -i $VS -i $VO -i $SFX -i $MUS -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -loglevel error -y -i $VS -i $VO -i $SFX -i $MUS -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[a]" \
    -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 22 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -c:a aac -b:a 192k -ac 2 -t $DUR -movflags +faststart "$2"
  echo "done $2"
}
mix 0.12 elnino_$L.mp4
mix 0 elnino_${L}_no_music.mp4
