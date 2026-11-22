#!/bin/bash
# ./build.sh -> out/openai_kk.mp4 (1080x1920, voice + effects + music)
set -e; cd "$(dirname "$0")"; mkdir -p out/kk
node record.js --cues out/kk/cues.json
cp sfx.py mix.py out/kk/; ffmpeg -loglevel error -y -i vo_kk.mp3 -ar 48000 -ac 1 out/kk/vo.wav
(cd out/kk && python3 sfx.py && python3 mix.py kk)
node record.js out/kk/video_silent.mp4 30
ffmpeg -loglevel error -y -i out/kk/video_silent.mp4 -i out/kk/mix_kk.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/openai_kk.mp4
echo built
