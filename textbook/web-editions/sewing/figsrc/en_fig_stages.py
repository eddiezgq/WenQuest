import sys; sys.path.insert(0, 'figsrc')
from en_labelfix import Fixer, BG
from PIL import Image, ImageDraw
import numpy as np
D=(31,42,54); G=(91,105,120)
SRC='/home/claude/book/img/fig_stages.png'
f=Fixer(SRC); s=f.s
orig=np.asarray(Image.open(SRC).convert('RGB')).copy()
step=392.4
titles=['Piercing','Loop forms','Catching','Round hook','Tighten, feed']
phi_x=[295,688,1080,1472,1877]
caps=[['The needle carries the needle','thread down through the fabric','and the throat-plate hole'],
      ['Past bottom dead centre the','needle rises; a loop bulges out','on the scarf side'],
      ['After about 2 mm of rise, the','hook point enters between the','loop and the needle'],
      ['The hook enlarges the loop and','carries it round the bobbin case','and the bobbin thread'],
      ['The take-up lever tightens the','stitch; the feed dog advances','the fabric one stitch length']]
lines=[((174.9,282),(190.4,312)),((546.2,282),(554.5,312)),((940.8,282),(949.6,312)),((1349.6,282),(1364.3,312)),((1722.8,282),(1730.8,312))]
for i in range(5):
    x0=80+i*step
    # "局部放大" -> "Detail", keep the leader line that crosses the label
    bx=(x0+12,286,x0+88,308)
    f.erase(*bx,color=(255,255,255))
    (xa,ya),(xb,yb)=lines[i]
    k=lambda y: xa+(y-ya)/(yb-ya)*(xb-xa)
    f.line([(k(285.5),285.5),(k(308.5),308.5)],(96,108,124),1.1)
    f.text(x0+15,297,'Detail',17,False,G,'lm')
    # title (keep the circled number)
    tx=85+i*step
    f.erase(tx-2,32,phi_x[i]-6,70)
    f.text(tx+2,51,titles[i],23,True,D,'lm')
    # caption
    cx=40+i*step
    f.erase(cx-5,724,cx+372,796)
    for k,l in enumerate(caps[i]): f.text(cx,735+k*23,l,18,False,D,'lm')
# legend + note: rebuild on a taller canvas
sw={'blue':(26,806,82,826),'orange':(153,806,209,826),'dash':(283,806,339,826),'dot':(630,800,662,832)}
patches={k:f.im.crop(tuple(f.S(*v))) for k,v in sw.items()}
f.erase(20,798,1990,836)
H=f.im.height; ext=int(round(40*s))
new=Image.new('RGB',(f.im.width,H+ext),BG); new.paste(f.im,(0,0)); f.im=new; f.d=ImageDraw.Draw(new)
x=28
for k,lab in [('blue','Needle thread'),('orange','Bobbin thread'),('dash','Part of the loop passing behind the bobbin case'),('dot','Hook-point position')]:
    p=patches[k]; X,Y=f.S(x,816); f.im.paste(p,(X,Y-p.height//2)); x+=p.width/s+8
    f.text(x,816,lab,19,False,D,'lm'); x+=f.d.textlength(lab,font=__import__('PIL.ImageFont',fromlist=['x']).truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',int(round(19*s))))/s+30
f.text(1970,852,'Viewed along the hook axis; φ is the main-shaft angle, 0° at the needle bar’s top position; needle-bar motion as in the Chapter 3 worked example',16,False,G,'rm')
f.save('img/en/fig_stages.png')
