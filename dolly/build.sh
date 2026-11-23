#!/usr/bin/env bash
# Builds the «Dolly» reel for one language:  ./build.sh ru|kk  ->  dolly_<lang>.mp4 (with music only) (1080x1920, 30 fps).
# SKIP_RECORD=1 reuses video_silent_<lang>.mp4 (about 2 minutes per language).
set -euo pipefail
cd "$(dirname "$0")"
L=${1:-ru}

[ "${SKIP_SFX:-0}" = 1 ] || python3 sfx.py "$L"
[ "${SKIP_RECORD:-0}" = 1 ] || LANG_Q=$L node record.js "video_silent_$L.mp4" 30
python3 mix.py "$L"                                                        # voice + effects (+ music), -14 LUFS

# The recording is encoded from JPEG frames, so its colours are stored the BT.601 way. Phones expect BT.709 from HD video and
# would show the brand navy and amber slightly off, so the picture is converted once here and tagged.
ffmpeg -hide_banner -loglevel error -y -i "video_silent_$L.mp4" -i "mix_$L.wav" -map 0:v -map 1:a \
  -vf "scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=tv:out_range=tv:flags=accurate_rnd+full_chroma_int+bitexact" \
  -c:v libx264 -preset slow -crf 18 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -g 60 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 192k -ac 2 -movflags +faststart "dolly_$L.mp4"
ls -la "dolly_$L.mp4"
