#!/bin/bash
# Higgsfield clips -> 60 fps frame folders the scene reads (clips/s<n>/NNNN.jpg, 1-based, + clips/clips.json). The four clips run in parallel.
cd "$(dirname "$0")"
mkdir -p clips
for n in 1 3 5 7; do
  f=hf/video/s$n.mp4; [ -f "$f" ] || continue
  rm -rf clips/s$n; mkdir -p clips/s$n
  ffmpeg -v error -y -threads 1 -i "$f" -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920" -q:v 3 -start_number 1 clips/s$n/%04d.jpg &
done
wait
J='{'
for n in 1 3 5 7; do c=$(ls clips/s$n 2>/dev/null | wc -l); [ "$c" -gt 0 ] && J="$J\"s$n\":{\"n\":$c,\"fps\":60},"; done
echo "${J%,}}" > clips/clips.json; cat clips/clips.json
