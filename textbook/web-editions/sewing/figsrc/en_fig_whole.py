import sys; sys.path.insert(0, 'figsrc')
from en_labelfix import Fixer
D=(29,40,52); G=(75,88,104)
f=Fixer('/home/claude/book/img/fig_whole.png')
B=24; s=17
# (erase box), then text
f.erase(1350,88,1412,122); f.text(1352,105,'Thread stand',B,True,D,'lm')
f.erase(70,200,335,260); f.text(332,214,'Main shaft, needle bar, take-up',s,False,G,'rm'); f.text(332,243,'Head',B,True,D,'rm')
f.erase(960,288,1022,322); f.text(990,305,'Arm',B,True,D,'mm')
f.erase(1518,253,1632,313); f.text(1522,268,'Turns main shaft by hand',s,False,G,'lm'); f.text(1522,297,'Handwheel',B,True,D,'lm')
f.erase(296,443,410,503); f.text(408,457,'Sets needle-thread tension',s,False,G,'rm'); f.text(408,487,'Tension assembly',B,True,D,'rm')
f.erase(350,640,438,673); f.text(436,657,'Take-up lever',B,True,D,'rm')
f.erase(1455,623,1598,658); f.text(1458,641,'Stitch-length regulator',B,True,D,'lm')
f.erase(368,784,428,816,'hinterp'); f.text(428,800,'Needle bar',B,True,D,'rm')
f.erase(1464,788,1578,822); f.text(1466,790,'Reverse',B,True,D,'lm'); f.text(1466,820,'lever',B,True,D,'lm')
f.erase(1776,868,1834,900); f.text(1778,884,'Table',B,True,D,'lm')
f.erase(416,980,477,1014,'hinterp'); f.text(476,997,'Presser foot',B,True,D,'rm')
f.erase(1025,998,1085,1032,'hinterp'); f.text(1028,1015,'Throat plate',B,True,D,'lm')
f.save('img/en/fig_whole.png')
