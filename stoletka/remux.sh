#!/bin/bash
# ./remux.sh ru|kk -> re-record the picture only (e.g. after clips/ changed) and join it with the existing mix
set -e; L=$1; cd "$(dirname "$0")"
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -i out/$L/mix_$L.wav -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -shortest -movflags +faststart out/stoletka_$L.mp4
echo built $L
