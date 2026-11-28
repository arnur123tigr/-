# ../_shared/sheet.sh t1 t2 ... -> sheet.jpg (contact sheet of preview frames)
rm -rf snaps; node record.js --snap snaps "$@" 2>&1 | grep ERR
python3 -c "
from PIL import Image; import glob
fs=sorted(glob.glob('snaps/f_*.jpg'),key=lambda f: float(f.split('_')[-1][:-4])); ims=[Image.open(f).resize((216,384)) for f in fs]
n=len(ims); c=10; r=(n+c-1)//c; S=Image.new('RGB',(216*c,384*r))
for i,im in enumerate(ims): S.paste(im,((i%c)*216,(i//c)*384))
S.save('sheet.jpg')"
