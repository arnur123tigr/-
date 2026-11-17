#!/bin/bash
# Final MP4s: silent video + mix -> desyatina_<lang>.mp4 and desyatina_<lang>_no_music.mp4 (1080x1920, BT.709)
# Full pipeline: python3 prep_map.py; python3 prep_tex.py; python3 timing.py;
#   LANG_Q=ru node record.js video_silent_ru.mp4 30  (same for kk); python3 sfx.py ru; python3 mix.py ru; ./build.sh ru
set -e
for L in ${@:-ru kk}; do
  for V in "" _no_music; do
    ffmpeg -y -loglevel error -i video_silent_$L.mp4 -i mix_$L$V.wav -map 0:v -map 1:a \
      -vf "scale=1080:1920:out_color_matrix=bt709,format=yuv420p" -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
      -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -movflags +faststart -shortest desyatina_$L$V.mp4
    echo desyatina_$L$V.mp4
  done
done
