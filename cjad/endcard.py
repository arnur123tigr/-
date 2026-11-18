# End card 1080x1920: navy bg, JAS logo, amber CTA "Ссылка в шапке профиля"
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920; NAVY=(19,11,84); AMB=(254,179,0)
im=Image.new('RGB',(W,H),NAVY); d=ImageDraw.Draw(im)
logo=Image.open('/mnt/project-files/references/brand/logo_white_transparent.png').convert('RGBA')
lw=620; logo=logo.resize((lw,int(logo.height*lw/logo.width)))
im.paste(logo,((W-lw)//2,560-logo.height//2),logo)
fB=ImageFont.truetype('fonts/Montserrat-Black.ttf',76); fE=ImageFont.truetype('fonts/Montserrat-ExtraBold.ttf',52)
def ctext(y,t,f,c):
    w=d.textlength(t,font=f); d.text(((W-w)/2,y),t,font=f,fill=c)
ctext(930,'ПРОБНЫЙ УРОК',fB,AMB)
ctext(1030,'подготовка к ЕНТ',fE,(255,255,255))
# pill
pw,ph=920,130; x0=(W-pw)//2; y0=1230
d.rounded_rectangle([x0,y0,x0+pw,y0+ph],radius=65,fill=AMB)
t='ССЫЛКА В ШАПКЕ ПРОФИЛЯ'; f=ImageFont.truetype('fonts/Montserrat-Black.ttf',44)
w=d.textlength(t,font=f); d.text(((W-w)/2,y0+ph/2),t,font=f,fill=NAVY,anchor='lm' if False else None) if False else d.text(((W-w)/2,y0+38),t,font=f,fill=NAVY)
# arrow up
cx=W//2; d.polygon([(cx,1430),(cx-40,1490),(cx+40,1490)],fill=(255,255,255))
im.save('endcard.png')
