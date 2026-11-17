#!/usr/bin/env bash
# LANG_Q=ru ./sheet.sh t1 t2 ...  -> /tmp/claude-0/sheet.jpg (contact sheet of preview frames)
cd "$(dirname "$0")"; rm -rf /tmp/claude-0/snap; node snap.js /tmp/claude-0/snap "$@" | grep -v ' ms$'
python3 -c "
import glob
from PIL import Image
fs=sorted(glob.glob('/tmp/claude-0/snap/f_*.jpg'),key=lambda f:float(f.split('f_')[1][:-4]))
ims=[Image.open(f).resize((270,480)) for f in fs]
sh=Image.new('RGB',(270*4,480*((len(ims)+3)//4)))
for i,im in enumerate(ims): sh.paste(im,((i%4)*270,(i//4)*480))
sh.save('/tmp/claude-0/sheet.jpg')"
