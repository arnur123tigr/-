#!/bin/bash
# run from a reel folder: ../_shared/build.sh NAME  -> out/NAME_ru.mp4 (1080x1920, with music)
set -e; L=ru; N=$1; mkdir -p out/$L
python3 cues.py
cp sfx.py mix.py out/$L/; ffmpeg -loglevel error -y -i vo_$L.mp3 -ar 48000 -ac 1 out/$L/vo.wav
(cd out/$L && python3 sfx.py && python3 mix.py $L)
LANG_Q=$L node record.js out/$L/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/$L/video_silent.mp4 -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/$L/v21.mp4
ffmpeg -loglevel error -y -i out/$L/v21.mp4 -i out/$L/mix_$L.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/${N}_$L.mp4
echo built out/${N}_$L.mp4
