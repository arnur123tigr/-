#!/bin/bash
# re-record picture only (audio mixes in out/<lang>/ stay) and mux: ./rerec.sh ru|kk
set -e; L=$1; cd "$(dirname "$0")"
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v.mp4
for v in "" _no_music; do ffmpeg -loglevel error -y -i out/$L/v.mp4 -i out/$L/mix_$L$v.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/oguz_$L$v.mp4; done
echo built $L
