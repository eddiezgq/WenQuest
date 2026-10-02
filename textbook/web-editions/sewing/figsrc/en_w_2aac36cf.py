"""English version of w_2aac36cf: lower-looper RSSR swing angle, angular velocity, acceleration, transmission angle.
Data recomputed from the RSSR model (en_rssr_model.py, ported from labs/rssr.html)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from en_rssr_model import run
plt.rcParams['font.family']=['DejaVu Sans']
BG='#faf9f5'; INK='#1f1f1f'; MUT='#555555'; GRID='#e4e4e4'
LL=run('LL'); UL=run('UL'); phi=LL[:,0]; k=np.arange(0,361,10)
fig=plt.figure(figsize=(13.44,11.1),dpi=150,facecolor=BG)
fig.text(0.021,0.968,'Lower-looper RSSR: swing angle, angular velocity, angular acceleration and transmission angle',fontsize=15.5,fontweight='bold',color=INK,va='top')
fig.text(0.021,0.935,'Worked-example machine, main shaft 7000 r/min; in the bottom panel the dashed line is the transmission angle of the upper-looper RSSR; the red band is below 40°',fontsize=11.2,color=MUT,va='top')
L,R=0.215,0.968
panels=[(LL[:,1],'#2a78d6',[0,20],(-7.5,22.5),'Swing angle θ','°',0.74,0.17),
        (LL[:,2],'#eb6834',[-150,0,150],(-200,170),'Angular velocity ω','rad/s',0.53,0.17),
        (LL[:,3]/1000,'#1baf7a',[-100,0,100],(-150,125),'Angular acceleration α','10³ rad/s²',0.335,0.15),
        (LL[:,4],'#0f3366',[40,80],(34,82),'Transmission angle γ','°; solid: lower looper\ndashed: upper looper',0.105,0.19)]
axs=[]
for y,col,ticks,yl,name,unit,b,h in panels:
    ax=fig.add_axes([L,b,R-L,h],facecolor=BG); axs.append(ax)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xlim(0,360); ax.set_ylim(*yl); ax.set_yticks(ticks); ax.tick_params(axis='y',length=0,labelsize=11,colors=MUT,pad=14)
    ax.set_xticks([]);
    if 0 in ticks: ax.axhline(0,color=GRID,lw=1,zorder=0)
    if name.startswith('Trans'):
        ax.axhspan(yl[0]+1,40,color='#f9e7e7',zorder=0,lw=0)
        ax.plot(phi,UL[:,4],color=col,lw=2,ls=(0,(3,2)))
        ax.plot(k,UL[k,4],'o',color=col,ms=3.2)
    ax.plot(phi,y,color=col,lw=2.4); ax.plot(k,y[k],'o',color=col,ms=3.8)
    mid=np.mean(yl); 
    fig.text(0.021,b+h*0.62,name,fontsize=12.5,fontweight='bold',color=INK,va='bottom')
    fig.text(0.021,b+h*0.62-0.006,unit,fontsize=11,color=MUT,va='top',linespacing=1.6)
ax=axs[-1]; ax.spines['bottom'].set_visible(True); ax.spines['bottom'].set_color('#cfcfcf'); ax.spines['bottom'].set_position(('outward',22))
ax.set_xticks(range(0,361,30)); ax.tick_params(axis='x',labelsize=11,colors=MUT,length=6,color='#cfcfcf')
ax.set_xlabel('Main-shaft angle φ (°)',fontsize=12,color=MUT,labelpad=8)
fig.savefig(sys.argv[1] if len(sys.argv)>1 else 'img/en/w_2aac36cf.png',facecolor=BG)
