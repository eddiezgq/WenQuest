import sys; sys.path.insert(0, 'figsrc')
from en_labelfix import Fixer, SANS
from PIL import ImageFont
D=(31,42,54); G=(75,88,104)
f=Fixer('/home/claude/book/img/fig_section.png'); s=f.s
f.erase(30,70,800,106); f.text(35,88,'Section cut along the seam (schematic). Top is the face of the fabric, bottom is the back.',20,False,G,'lm')
W=(255,255,255)
for cx,title,cap in [(345,'Balanced tension','Interlock in mid-fabric; straight lines on both faces'),
                     (1008,'Needle thread too tight','Bobbin thread pulled to the face; dots show on top'),
                     (1672,'Bobbin thread too tight','Needle thread pulled to the back; dots show beneath')]:
    f.erase(cx-150,165,cx+150,205,color=W); f.text(cx,185,title,27,True,D,'mm')
    f.erase(cx-300,470,cx+300,506,color=W); f.text(cx,488,cap,19.5,False,G,'mm')
sw=[(24,588,104,616),(191,588,270,616),(378,586,417,618)]
P=[f.im.crop(tuple(f.S(*b))) for b in sw]
f.erase(20,582,800,622)
font=ImageFont.truetype(SANS,int(round(22*s)))
x=26
for p,lab in zip(P,['Needle thread','Bobbin thread','Fabric yarn cross-section']):
    X,Y=f.S(x,602); f.im.paste(p,(X,Y-p.height//2)); x+=p.width/s+8
    f.text(x,602,lab,22,False,D,'lm'); x+=f.d.textlength(lab,font=font)/s+36
f.save('img/en/fig_section.png')
