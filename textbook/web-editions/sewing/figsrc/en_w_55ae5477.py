import sys; sys.path.insert(0,'figsrc')
from en_wchart_style import *
Wp,Hp=1344,774
fig=plt.figure(figsize=(Wp/100,Hp/100),dpi=150,facecolor=BG)
header(fig,'Larger link ratio: faster needle rise after BDC, earlier loop catching',
       'r = 15.5 mm fixed, only the link length changed; l = 77.5, 55, 38.75 mm give λ = 0.20, 0.282, 0.40',Wp,Hp)
ax=fig.add_axes([255/Wp,1-672/Hp,(1185-255)/Wp,(672-140)/Hp]); clean(ax)
ax.spines['bottom'].set_color('#bdbdb5')
ax.set_xlim(180,220); ax.set_ylim(0,5.2); ax.set_yticks(range(6)); ax.set_xticks(range(180,221,5))
ax.set_xticklabels([f'{d}°' for d in range(180,221,5)]); ax.tick_params(axis='x',pad=10); ax.tick_params(axis='y',pad=14)
ax.yaxis.grid(True,color=GRID,lw=1); ax.set_axisbelow(True)
pf=np.linspace(180,220,401); pp=np.arange(180,221,5)
rise=lambda p,l: 31-x_of(p,l)
for l,c,lw,lab,fw,tc in [(77.5,G2,2,'λ = 0.20','normal','#888'),(38.75,G1,2.2,'λ = 0.40','normal',DARK),(55,BLUE,2.8,'λ = 0.282','bold',BLUE)]:
    ax.plot(pf,rise(pf,l),color=c,lw=lw,zorder=3,clip_on=False); ax.plot(pp,rise(pp,l),'o',color=c,ms=5,zorder=4,clip_on=False)
    ax.annotate(lab,(220,rise(np.array([220.0]),l)[0]),xytext=(14,0),textcoords='offset points',va='center',fontsize=13,fontweight=fw,color=tc,annotation_clip=False)
ax.axhline(2,color='#888',lw=1.4,ls=(0,(5,4)))
ax.text(180.5,2.08,'2 mm rise: hook catches the loop',fontsize=12.5,color='#444',va='bottom')
fig.text(42/Wp,1-347/Hp,'Rise',fontsize=13.5,color=DARK,va='center'); fig.text(42/Wp,1-376/Hp,'mm',fontsize=12,color=MUTED,va='center')
fig.text(42/Wp,1-700/Hp,'Main-shaft angle φ',fontsize=13,color='#333',va='center')
fig.savefig('img/en/w_55ae5477.png',facecolor=BG); print('ok')
