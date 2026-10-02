import sys; sys.path.insert(0, 'figsrc')
from en_labelfix import Fixer
D=(31,42,54); G=(91,105,120)
f=Fixer('/home/claude/book/img/fig_needlebar_mech.png')
B=25; s=19
f.erase(25,30,870,64); f.text(32,47,'Viewed along the main shaft, face plate removed; shown at main-shaft angle φ = 60° (structural schematic)',s,False,G,'lm')
# right column, left-aligned at 1493
R=1493
f.erase(1488,92,1720,162); f.text(R,112,'Main shaft',B,True,D,'lm'); f.text(R,146,'Section; one revolution = one stitch',s,False,G,'lm')
f.erase(1488,220,1860,290); f.text(R,240,'Needle-bar crank',B,True,D,'lm'); f.text(R,273,'Counterweight (dark part) opposite the crank pin',s,False,G,'lm')
f.erase(1488,430,1595,466); f.text(R,448,'Crank pin',B,True,D,'lm')
f.erase(1488,555,1705,630); f.text(R,575,'Needle-bar link',B,True,D,'lm'); f.text(R,614,'Length l, pin holes at both ends',s,False,G,'lm')
f.erase(1488,683,1690,757); f.text(R,702,'Guide block and slot',B,True,D,'lm'); f.text(R,741,'Stops the needle bar rotating',s,False,G,'lm')
f.erase(1488,882,1715,957); f.text(R,901,'Needle bar',B,True,D,'lm'); f.text(R,940,'Hollow steel tube; the lighter the better',s,False,G,'lm')
f.erase(1488,1092,1715,1128); f.text(R,1110,'Needle clamp and clamp screw',B,True,D,'lm')
f.erase(1488,1222,1560,1258); f.text(R,1240,'Needle',B,True,D,'lm')
f.erase(1488,1387,1560,1423); f.text(R,1405,'Throat plate',B,True,D,'lm')
# left column, right-aligned at 478
L=478
f.erase(100,250,481,290); f.text(L,252,'Upper needle-bar bushing',B,True,D,'rm'); f.text(L-6,281,'(behind the crank)',s,False,G,'rm')
f.erase(190,393,481,462); f.text(L,412,'Needle-bar connecting stud',B,True,D,'rm'); f.text(L,445,'Loosen its screw to set needle-bar height',s,False,G,'rm')
f.erase(318,732,481,768); f.text(L,750,'Lower needle-bar bushing',B,True,D,'rm')
f.erase(865,855,1092,887,color=(238,240,241)); f.line([(864,847.85),(1093,857.55)],(133,142,153),1.4); f.text(978,872,'Head (face plate removed)',s,False,G,'mm')
f.erase(565,1022,628,1053); f.text(618,1037,'Reciprocates',s,False,G,'rm')
f.erase(160,1400,481,1435); f.text(L,1418,'Presser bar (behind the needle bar)',22,True,D,'rm')
f.save('img/en/fig_needlebar_mech.png')
