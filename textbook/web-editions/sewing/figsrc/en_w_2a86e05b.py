import sys; sys.path.insert(0,'figsrc')
from en_wchart_style import *
from matplotlib.patches import FancyBboxPatch
Wp,Hp=1344,632
fig=plt.figure(figsize=(Wp/100,Hp/100),dpi=150,facecolor=BG)
header(fig,'The hook catches the loop after the needle has risen about 2 mm past its lowest point',
       'Needle-bar displacement from the Chapter 3 worked example; hook and feed bands are illustrative, to be checked against a real machine',Wp,Hp)
# one axes in pixel-like data coords: x = angle, y = pixel row (downwards)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,Wp); ax.set_ylim(Hp,0); ax.axis('off')
X=lambda d: 226+d*(1259-226)/360
Y=lambda mm: 134+mm*(332-134)/31
for d in range(0,361,45):
    ax.plot([X(d)]*2,[120,552],color=GRID,lw=1,zorder=0)
    ax.text(X(d),578,f'{d}°',ha='center',va='center',fontsize=12.5,color='#444')
pf=np.linspace(0,360,721); ax.plot(X(pf),Y(x_of(pf)),color=DARK,lw=2.2,zorder=3)
pp=np.arange(0,361,15); ax.plot(X(pp),Y(x_of(pp)),'o',color=DARK,ms=4,zorder=4)
yf=Y(x_of(np.array([102.0]))[0])
ax.plot([X(0),X(360)],[yf,yf],color='#bbb',lw=1.2,ls=(0,(4,4)),zorder=1)
ax.text(X(0)+10,yf-8,'Needle point at fabric',fontsize=12,color='#666',va='bottom')
ax.plot([X(180)]*2,[120,552],color='#aaa',lw=1.2,ls=(0,(3,3)),zorder=1)
ax.text(X(180)-10,360,'Lowest point',ha='right',va='center',fontsize=12.5,color='#555')
ax.text(X(180)-10,385,'180°',ha='right',va='center',fontsize=12.5,color='#555')
ax.plot([X(206)]*2,[120,552],color=BLUE,lw=2,zorder=2)
ax.text(X(206)+10,360,'Hook catches loop',ha='left',va='center',fontsize=12.5,fontweight='bold',color=BLUE)
ax.text(X(206)+10,385,'206°',ha='left',va='center',fontsize=12.5,color=BLUE)
ax.text(198,134,'0 mm',ha='right',va='center',fontsize=12.5,color='#555')
ax.text(198,332,'31 mm',ha='right',va='center',fontsize=12.5,color='#555')
ax.text(42,218,'Needle-bar',fontsize=13,color=DARK,va='center'); ax.text(42,243,'displacement x',fontsize=13,color=DARK,va='center')
ax.text(42,268,'(downward +)',fontsize=12,color='#555',va='center')
def band(a,b,y,c,lab):
    ax.add_patch(FancyBboxPatch((X(a)+2,y-15),X(b)-X(a)-4,30,boxstyle='round,pad=0,rounding_size=5',fc=c,ec='none',zorder=1.5))
    ax.text((X(a)+X(b))/2,y,lab,ha='center',va='center',fontsize=12.5,color=DARK,zorder=3)
band(102,258,423,'#e3e2dd','102°–258°'); band(206,341,477,'#c2d7f1','206°–341°')
band(0,60,530,'#e3e2dd','0°–60°'); band(290,360,530,'#e3e2dd','290°–360°')
for y,t in [(423,'Needle in fabric'),(477,'Hook carries loop'),(530,'Feed')]:
    ax.text(42,y,t,fontsize=13,color=DARK,va='center')
ax.text(42,578,'Main-shaft angle φ',fontsize=12.5,color='#333',va='center')
fig.savefig('img/en/w_2a86e05b.png',facecolor=BG); print('ok')
