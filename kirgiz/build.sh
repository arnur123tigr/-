#!/bin/bash
# Build kirgiz_ru.mp4: synth SFX -> record frames -> mix VO + SFX, loudness -14 LUFS (two-pass).
set -e; cd "$(dirname "$0")"
python3 sfx.py
node record.js video_silent.mp4 30
F="[1:a]aresample=48000,apad=whole_dur=32[v];[2:a]aresample=48000,volume=0.9[s];[v][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.45:attack=2:release=60:level=false"
J=$(ffmpeg -hide_banner -i video_silent.mp4 -i vo_ru.mp3 -i sfx.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -loglevel error -y -i video_silent.mp4 -i vo_ru.mp3 -i sfx.wav -filter_complex "$F,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ac 2 -t 32 -movflags +faststart kirgiz_ru.mp4
echo done kirgiz_ru.mp4
