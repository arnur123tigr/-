#!/bin/bash
# hf/video/s<k>.mp4 (Kling, 5 s) -> clips/s<k>/NNNN.jpg: stretched to the scene length with motion interpolation, 30 fps, 1080x1920
set -e; cd "$(dirname "$0")"; mkdir -p clips
one() { k=$1; len=$2; rm -rf clips/s$k; mkdir -p clips/s$k
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 hf/video/s$k.mp4); f=$(python3 -c "print($len/$d)")
  ffmpeg -loglevel error -y -i hf/video/s$k.mp4 -vf "setpts=$f*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -q:v 3 clips/s$k/%04d.jpg; }
one 1 8.4 & one 5 7.0 & wait
python3 -c "import json,os;json.dump({d:len(os.listdir('clips/'+d)) for d in sorted(os.listdir('clips')) if d.startswith('s')},open('clips/clips.json','w'));print(open('clips/clips.json').read())"
