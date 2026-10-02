import sys; sys.path.insert(0,'figsrc')
from en_wchart_style import *
Wp,Hp=1344,862
fig=plt.figure(figsize=(Wp/100,Hp/100),dpi=150,facecolor=BG)
header(fig,'Acceleration at BDC is 5.45 km/s², about 80% more than the 3.05 km/s² at TDC',
       'r = 15.5 mm, l = 55 mm, n = 5000 r/min; exact formulas, one point every 10° (TDC/BDC: top/bottom dead centre)',Wp,Hp)
ph=np.arange(0,361,10); pf=np.linspace(0,360,721)
def ax_at(y0,y1): return fig.add_axes([255/Wp,1-y1/Hp,(1272-255)/Wp,(y1-y0)/Hp])
specs=[(130,305,x_of,(0,31.5),[0,10,20,30],G1,'Displacement x','mm'),
       (365,535,v_of,(-9.5,9.5),[-8,-4,0,4,8],G1,'Velocity v','m/s'),
       (595,785,a_of,(-7.4,4.6),[-6,-4,-2,0,2,4],BLUE,'Acceleration a','km/s²')]
axes=[]
for y0,y1,fn,yl,yt,c,lab,unit in specs:
    ax=ax_at(y0,y1); clean(ax); axes.append(ax)
    ax.set_xlim(-3,363); ax.set_ylim(*yl); ax.set_yticks(yt); ax.set_xticks(range(0,361,45))
    ax.yaxis.grid(True,color=GRID,lw=1); ax.set_axisbelow(True)
    ax.axhline(0,color='#cfcfc8',lw=1.2)
    ax.plot(pf,fn(pf),color=c,lw=2.3,zorder=3); ax.plot(ph,fn(ph),'o',color=c,ms=4.5,zorder=4)
    ax.spines['bottom'].set_visible(False)
    yc=1-(y0+y1)/2/Hp
    fig.text(42/Wp,yc+0.012,lab,fontsize=13.5,fontweight='bold',color=DARK,va='center')
    fig.text(42/Wp,yc-0.022,unit,fontsize=12,color=MUTED,va='center')
    if ax is not axes[-1] if False else fn is not a_of: ax.set_xticklabels([])
axes[2].set_xticklabels([f'{d}°' for d in range(0,361,45)])
vmax=v_of(np.array([104.7]))[0]
axes[1].annotate(f'{vmax:.1f} m/s',(104.7,vmax),xytext=(0,10),textcoords='offset points',ha='center',fontsize=12.5,color=DARK)
axes[2].annotate(f'TDC {a_of(np.array([0.0]))[0]:.2f}',(0,a_of(np.array([0.0]))[0]),xytext=(6,10),textcoords='offset points',ha='left',fontsize=13,fontweight='bold',color=BLUE)
amin=a_of(np.array([180.0]))[0]
axes[2].annotate(f'BDC {amin:.2f}'.replace('-','−'),(180,amin),xytext=(0,-20),textcoords='offset points',ha='center',fontsize=13,fontweight='bold',color=BLUE)
for ax in axes: ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p: f'{v:g}'.replace('-','−')))
fig.text(42/Wp,1-815/Hp,'Main-shaft angle φ',fontsize=13,color='#333',va='center')
fig.savefig('img/en/w_f0f8ad0a.png',facecolor=BG); print('ok')
