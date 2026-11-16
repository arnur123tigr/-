#!/usr/bin/env bash
# Builds one language:  ./build.sh ru|kk  ->  reforma_<lang>.mp4 and reforma_<lang>_no_music.mp4 (1080x1920, 30 fps).
# SKIP_RECORD=1 reuses video_silent_<lang>.mp4.
set -euo pipefail
cd "$(dirname "$0")"
L=${1:-ru}
[ -f "vo_$L.wav" ] || ffmpeg -loglevel error -y -i "vo_${L}_take.mp3" -ar 48000 -ac 1 "vo_$L.wav"
python3 sfx.py "$L"
[ "${SKIP_RECORD:-0}" = 1 ] || LANG_Q=$L node record.js "video_silent_$L.mp4" 30
python3 mix.py "$L"
ffmpeg -hide_banner -loglevel error -y -i "video_silent_$L.mp4" -i "mix_$L.wav" -map 0:v -map 1:a \
  -vf "scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=tv:out_range=tv:flags=accurate_rnd+full_chroma_int+bitexact" \
  -c:v libx264 -preset slow -crf 18 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -g 60 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 192k -ac 2 -movflags +faststart "reforma_$L.mp4"
ffmpeg -hide_banner -loglevel error -y -i "reforma_$L.mp4" -i "mix_${L}_no_music.wav" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -ac 2 -movflags +faststart "reforma_${L}_no_music.mp4"
ls -la "reforma_$L.mp4" "reforma_${L}_no_music.mp4"
