import sys; sys.path.insert(0, 'figsrc')
from en_labelfix import Fixer
D=(31,42,54); G=(91,105,120)
f=Fixer('/home/claude/book/img/fig_needle.png')
B=24; s=18
f.erase(120,78,410,152); f.text(263,92,'Shank',B,True,D,'mm'); f.text(263,113,'Fits into the needle bar;\nheld by the clamp screw',s,False,G,'mm')
f.erase(550,78,900,152); f.text(725,92,'Long groove',B,True,D,'mm'); f.text(725,113,'Needle thread runs down inside,\nsafe from fabric abrasion',s,False,G,'mm')
f.erase(88,333,295,364); f.text(93,348,'Front view (long-groove side)',20,True,G,'lm')
f.erase(1395,108,1460,144); f.text(1427,126,'Scarf',B,True,D,'mm')
f.erase(1750,108,1815,144); f.text(1782,126,'Eye',B,True,D,'mm')
f.erase(760,392,826,428); f.text(793,410,'Blade',B,True,D,'mm')
f.erase(1310,392,1375,428); f.text(1343,410,'Point',B,True,D,'mm')
f.erase(1870,492,1936,528); f.text(1874,496,'Short',B,True,D,'lm'); f.text(1874,526,'groove',B,True,D,'lm')
f.erase(88,610,335,640); f.text(93,625,'Side view (scarf side down)',20,True,G,'lm')
f.erase(995,690,1185,758); f.text(1090,707,'Scarf',B,True,D,'mm'); f.text(1090,744,'The hook point passes close to the blade here',s,False,G,'mm')
f.erase(1446,648,1514,683); f.text(1480,665,'Hook point',B,True,D,'mm')
f.erase(1684,648,1750,683); f.text(1717,665,'Loop',B,True,D,'mm')
f.erase(1485,692,1752,722); f.text(1618,707,'Detail near the eye (side view)',s,False,G,'mm')
f.erase(88,812,1520,892)
L=['Needle thread enters the eye from the long-groove side and leaves on the short-groove side. As the needle rises, the thread on the',
   'short-groove side is held by the fabric and bulges into a loop at the scarf, and the hook point slips in along the scarf. The scarf and',
   'short groove must face the hook point when the needle is fitted; fitted the wrong way round, the hook point cannot reach the loop and stitches are skipped.']
for i,l in enumerate(L): f.text(93,822+i*30,l,19,False,D,'lm')
f.save('img/en/fig_needle.png')
