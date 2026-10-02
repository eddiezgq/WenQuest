# English version of fig_pattern_struct: erase the Chinese callout margins, redraw leader lines and English labels.
from PIL import Image, ImageDraw, ImageFont
import numpy as np
SRC='/home/claude/book/img/fig_pattern_struct.png'; OUT='/home/claude/sm/img/en/fig_pattern_struct.png'
img=Image.open(SRC).convert('RGB'); a=np.array(img).astype(int)
BG=(251,250,247); LINE=np.array([123,135,148])
def isline(x,y): return np.abs(a[y,x]-LINE).sum()<40
def starts(x):
    ys=[y for y in range(130,1720) if isline(x,y)]
    out=[]
    for y in ys:
        if not out or y-out[-1][-1]>2: out.append([y])
        else: out[-1].append(y)
    return [sum(g)/len(g) for g in out]
def trace(x0,y0,xend,step):
    # follow the line from (x0,y0) to xend
    best=None
    for s in np.linspace(-1.2,1.2,1201):      # slope dy/dx
        xs=np.arange(x0+step*20, xend, step*4)
        ys=y0+s*(xs-x0)
        ok=(ys>=0)&(ys<a.shape[0]-1)
        if not ok.all(): continue
        d=np.abs(a[ys.round().astype(int),xs]-LINE).sum(1)
        sc=(d<60).mean()
        if best is None or sc>best[0]: best=(sc,s)
    return best
XL,XR=955,3410
L=[]; R=[]

L=[]; R=[]
for y in starts(84):
    sc,s_=trace(82,y,XL,1)
    if sc>0.5: L.append((y,s_))
for y in starts(3524):
    sc,s_=trace(3522,y,XR,-1)
    if sc>0.5: R.append((y,s_))
assert len(L)==5 and len(R)==6, (L,R)
d=ImageDraw.Draw(img)
d.rectangle([0,0,img.width,128],fill=BG)
d.rectangle([0,128,XL,img.height],fill=BG)
d.rectangle([XR,128,img.width,img.height],fill=BG)
d.rectangle([2180,1588,2290,1630],fill=(238,240,241))
COL=(123,135,148)
FB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34)
FR=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',27)
FT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',32)
TC=(31,42,54); SC=(93,107,122)
d.text((83,70),'Illustration: the head only “sews”; where the fabric goes is decided entirely by the X–Y table carrying the template (structural schematic, not to scale)',font=FT,fill=SC)
def label(x,ytop,title,subs):
    d.text((x,ytop),title,font=FB,fill=TC)
    for i,t in enumerate(subs): d.text((x,ytop+46+i*35),t,font=FR,fill=SC)
# (title top, title, subs, new line-start y or None)
LEFT=[(170,'Machine head',['Needle, take-up and hook mechanisms as on a','lockstitch machine; no feed dog'],None),
      (452,'Needle and intermediate presser foot',['The foot hops with the needle and holds the','fabric down to prevent skipped stitches'],None),
      (742,'Template (upper + lower plates) and slot',['The slot is the sewing path; the fabric is','clamped between the two plates'],None),
      (1160,'X-axis servo motor',['Drives the X carriage','via a timing belt'],None),
      (1414,'Y-axis servo motor',['Moves the beam back and forth','along the linear guides'],None)]
RIGHT=[(198,'Control panel',['Select pattern, set speed and stitch length'],None),
       (438,'Column and arm-shaft drive',['Servo motor drives the arm shaft directly'],None),
       (678,'X carriage and Y beam',['The two axes form the X–Y table'],None),
       (918,'Pneumatic clamp',['Cylinders press the template; lift to change it'],None),
       (1254,'Y linear guide',[],None),
       (1474,'Control box',['Main-shaft servo, X/Y drives, air valves,','main controller board'],None)]
SS=4; mask=Image.new('L',(img.width*SS,img.height*SS),0); md=ImageDraw.Draw(mask)
def centroid(x,yp):
    ys=[y for y in range(int(yp)-5,int(yp)+6) if np.abs(a[y,x]-LINE).sum()<120]
    w=[255*3-np.abs(a[y,x]-np.array(BG)).sum()*0+ (765-np.abs(a[y,x]-LINE).sum()) for y in ys]
    return sum(y*v for y,v in zip(ys,w))/sum(w)+0.5
def seg(p,q): md.line([(p[0]*SS,p[1]*SS),(q[0]*SS,q[1]*SS)],fill=255,width=int(2.6*SS))
for (y0,sl),(top,t,subs,ny) in zip(L,LEFT):
    xe=XL+8; seg((82,y0+0.5),(xe,centroid(xe,y0+sl*(xe-82)))); label(83,top,t,subs)
for (y0,sl),(top,t,subs,ny) in zip(R,RIGHT):
    xe=XR-8; seg((xe,centroid(xe,y0+sl*(xe-3522))),(3523,y0+0.5)); label(3541,top,t,subs)
m=mask.resize(img.size,Image.LANCZOS)
img.paste(Image.new('RGB',img.size,COL),(0,0),m)
d.text((2186,1592),'Under the table',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26),fill=SC)
img.save(OUT); print('saved',OUT)
