#!/bin/bash
# Build africa_ru.mp4 / africa_ru_no_music.mp4 (1080x1920):
# synth SFX + music -> record frames (2D canvas) -> mix VO on top (bed ducked under voice), loudness -14 LUFS (two-pass).
# One-time asset prep: put Natural Earth files in data/ (NE2_HR_LC_SR_W.tif, ne_10m/50m admin_0 geojson, ne_50m admin_1 geojson) and run prep_map.py.
set -e; cd "$(dirname "$0")"
L=${LANG_Q:-ru}
if [ "$L" = kk ]; then python3 sfx.py kk; VO=vo_kk.mp3; SFX=sfx_kk.wav; MUS=music_kk.wav; VS=video_silent_kk.mp4; TL=timeline_kk.json
else python3 sfx.py; VO=vo_a.mp3; SFX=sfx.wav; MUS=music.wav; VS=video_silent.mp4; TL=timeline.json; fi
DUR=$(python3 -c "import json;print(json.load(open('$TL'))['scenes'][-1]['end'])")
[ "$SKIP_RECORD" = 1 ] || node record.js $VS 30
mix(){ # $1 = music volume, $2 = output
  F="[1:a]aresample=48000,adelay=300:all=1,apad=whole_dur=$DUR,volume=1.6,asplit=2[v][vk];[2:a]aresample=48000,volume=0.3[s];[3:a]aresample=48000,volume=$1[m];[s][m]amix=inputs=2:normalize=0:duration=first[bed];[bed][vk]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350:makeup=1[duck];[v][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.5:attack=2:release=60:level=false"
  J=$(ffmpeg -hide_banner -i $VS -i $VO -i $SFX -i $MUS -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -loglevel error -y -i $VS -i $VO -i $SFX -i $MUS -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[a]" \
    -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 20 -maxrate 10M -bufsize 20M -pix_fmt yuv420p -c:a aac -b:a 192k -ac 2 -t $DUR -movflags +faststart "$2"
  echo "done $2"
}
mix 0.12 africa_$L.mp4
mix 0 africa_${L}_no_music.mp4
