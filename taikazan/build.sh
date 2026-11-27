#!/usr/bin/env bash
# Builds the «Тайқазан» reel:  ./build.sh kk|ru  ->  taikazan_<lang>.mp4 (1080x1920, 30 fps, with music).
# Voice: python3 prep_vo.py <lang> && python3 words.py vo_<lang>_raw.wav w_<lang>.json <lang> medium && python3 timing.py  (already done, results in the folder)
# SKIP_RECORD=1 reuses video_silent_kk.mp4.
set -euo pipefail
cd "$(dirname "$0")"
L=${1:-kk}
[ -s "vo_${L}.wav" ] || python3 timing.py
python3 sfx.py "$L"
[ "${SKIP_RECORD:-0}" = 1 ] || LANG_Q=$L node record.js "video_silent_$L.mp4" 30
python3 mix.py "$L"
ffmpeg -hide_banner -loglevel error -y -i "video_silent_$L.mp4" -i "mix_$L.wav" -map 0:v -map 1:a \
  -vf "scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=tv:out_range=tv:flags=accurate_rnd+full_chroma_int+bitexact" \
  -c:v libx264 -preset slow -crf 20 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -g 60 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 192k -ac 2 -movflags +faststart "taikazan_$L.mp4"
ls -la "taikazan_$L.mp4"
