"""English version of w_d90f8ced: overlock timing diagram (one main-shaft revolution).
Curves recomputed from the chapter's calculation table embedded in labs/model-overlock.html (en_ol_model.py);
layout reproduces the original (coordinates below are in the original 1344-px-wide frame)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from en_ol_model import table
plt.rcParams['font.family']=['DejaVu Sans']
BG='#faf9f5'; INK='#1f1f1f'; MUT='#555555'; GRID='#e2e2e2'
T=table(); phi=T[:,0]
OFF=26; W,H=1344,1144+OFF
fig=plt.figure(figsize=(W/100,H/100),dpi=150,facecolor=BG); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis('off')
X=lambda p:265+np.asarray(p)/360*(1301-265)
def Y(v,y0,sc): return y0+OFF-np.asarray(v)*sc
ax.text(28,32,'Motion of each mechanism within one stitch (one main-shaft revolution)',fontsize=13,fontweight='bold',color=INK,va='center')
ax.text(28,70,'Worked-example values: needle-bar stroke 24.5 mm, lower-looper swing 25.7°, upper-looper rocker swing 50.5°, stitch length 2.5 mm',fontsize=9.6,color=MUT,va='center')
# events
EV=[(22,'Upper looper reaches upper left',0),(57.5,'Needle passes through upper-looper thread',1),(80.8,'Needle enters fabric',2),
    (213.6,'Lower looper catches needle thread',1),(270.8,'Upper looper picks up lower-looper thread',0),(279.2,'Needle leaves fabric',2)]
for p,t,r in EV:
    ax.plot([X(p)]*2,[96+OFF+r*24-8,1052+OFF],color='#cfcfcf',lw=1,ls=(0,(4,3)),zorder=0)
    ax.text(X(p),96+r*24,t,fontsize=9.4,color=MUT,ha='center',va='center',bbox=dict(fc=BG,ec='none',pad=1.2))
# panels: (values, y of zero, px per mm, colour, style)
ax.fill_between([X(0),X(360)],Y(0,236.4,6.777),Y(1.5,236.4,6.777),color='#ededec',lw=0,zorder=0)
for y0 in (523,678,970): ax.plot([X(0),X(360)],[y0+OFF]*2,color=GRID,lw=1,zorder=0)
for col,y0,sc,c,ls in [(1,236.4,6.777,'#2978d6','-'),(2,523,9.61,'#eb6834','-'),(3,678,8.23,'#1baf7a','-'),(5,970,20.3,'#d55181',(0,(4,2.5))),(4,970,20.3,'#0d366b','-')]:
    ax.plot(X(phi),Y(T[:,col],y0,sc),color=c,lw=2.2,ls=ls)
    if ls=='-': ax.plot(X(phi[::3]),Y(T[::3,col],y0,sc),'o',color=c,ms=1.6)
for y,name,unit,ucol in [(222,'Needle-point height','mm; shading = fabric layer',MUT),(455,'Lower-looper point','lateral position, mm; 0 = needle centre',MUT),
                          (685,'Upper-looper point height','mm; 0 = throat-plate surface',MUT)]:
    ax.text(28,y+OFF,name.replace('lateral ','lateral\n') if False else name,fontsize=10.6,fontweight='bold',color=INK,va='center')
    ax.text(28,y+30+OFF,unit,fontsize=9.6,color=ucol,va='center')
ax.text(28,904+OFF,'Feed dog and upper knife',fontsize=10.6,fontweight='bold',color=INK,va='center')
ax.text(28,934+OFF,'Solid: feed-dog tooth tips',fontsize=9.6,color='#0d366b',va='center')
ax.text(28,962+OFF,'Dashed: upper-knife edge',fontsize=9.6,color='#d55181',va='center')
ax.plot([X(0),X(360)],[1052+OFF]*2,color='#cfcfcf',lw=1)
for t in range(0,361,30):
    ax.plot([X(t)]*2,[1052+OFF,1060+OFF],color='#cfcfcf',lw=1); ax.text(X(t),1080+OFF,str(t),fontsize=9.6,color=MUT,ha='center',va='center')
ax.text(X(180),1112+OFF,'Main-shaft angle φ (°); 0° = needle point highest',fontsize=10,color=MUT,ha='center',va='center')
fig.savefig(sys.argv[1] if len(sys.argv)>1 else 'img/en/w_d90f8ced.png',facecolor=BG)
