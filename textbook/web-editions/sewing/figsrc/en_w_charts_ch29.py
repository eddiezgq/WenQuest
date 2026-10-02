# English versions of the three data charts in Chapter 29 (w_24804990, w_7d16e7c0, w_b27b372e)
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import brentq
plt.rcParams.update({'font.family':['DejaVu Sans'],'font.size':12,'axes.edgecolor':'#cccccc','text.color':'#1b1b1b'})
BG='#faf9f5';GREY='#c3c3b7';BLUE='#2a78d6';INK='#1b1b1b';MUT='#555555'
OUT='/home/claude/sm/img/en/'
def head(fig,t,s):
    fig.text(0.014,0.955,t,fontsize=17,fontweight='bold',va='top')
    fig.text(0.014,0.885,s,fontsize=12.5,color=MUT,va='top')
def clean(ax):
    for k in ['top','right','left']: ax.spines[k].set_visible(False)
    ax.tick_params(length=0,colors=MUT,labelsize=12)
    ax.set_facecolor(BG)

# ---- Fig. 29-4 balance chart ----
smv=[0.230,0.207,0.380,0.287,0.299,0.345,0.287,0.380,0.345,0.253,0.483,0.345,0.655,0.425,0.529,0.391]
ppl=[1,1,2,1,1,2,1,2,2,1,2,2,3,2,2,2]
load=[s*60/p for s,p in zip(smv,ppl)]
grp=[('Overlock\n7 people',1.863,7),('Coverstitch\n5 people',1.506,5),('Lockstitch\n5 people',1.334,5),('Manual\n4 people',1.138,4)]
gl=[s*60/n for _,s,n in grp]
fig=plt.figure(figsize=(13.44,7.2),dpi=150,facecolor=BG)
head(fig,'Grouping operations by machine type: the same 200 pieces/h with 6 fewer people','Bar height = load per person (s/piece); blue = bottleneck; the gap between a bar and the dashed line is waiting time')
ax=fig.add_axes([0.067,0.19,0.915,0.53])
x1=np.arange(16); x2=np.arange(4)*2.35+18.9
ib=int(np.argmax(load))
ax.bar(x1,load,0.78,color=[BLUE if i==ib else GREY for i in range(16)])
ax.bar(x2,gl,1.4,color=[BLUE if i==1 else GREY for i in range(4)])
ax.plot([-0.5,15.5],[18,18],'--',color='#888888',lw=1.6); ax.plot([18.0,27.1],[18,18],'--',color='#888888',lw=1.6)
ax.text(15,18.6,'Takt time 18 s',ha='right',va='bottom',fontsize=12)
ax.set_xlim(-0.8,27.1);ax.set_ylim(0,30);ax.set_yticks([0,10,20,30])
ax.set_xticks(list(x1)+list(x2));ax.set_xticklabels([str(i+1) for i in range(16)]+[g[0] for g in grp])
ax.yaxis.grid(True,color='#e3e3e3');ax.set_axisbelow(True);clean(ax)
ax.text(-1.0,34.5,'One person per operation: 27 people, balance 72%',fontsize=12.5,fontweight='bold',va='center')
ax.text(27.1,34.5,'Grouped by machine type: 21 people, balance 92%',fontsize=12.5,fontweight='bold',va='center',ha='right')
ax.text(-2.5,25.5,'s/piece',fontsize=12,color=INK,ha='left')
ax.text(7.5,-7.3,'Operation No.',ha='center',fontsize=12,color=MUT); ax.text(22.4,-7.3,'Machine group',ha='center',fontsize=12,color=MUT)
fig.savefig(OUT+'w_24804990.png',facecolor=BG);plt.close(fig)

# ---- Fig. 29-5 sweater labour ----
fig=plt.figure(figsize=(13.44,6.5),dpi=150,facecolor=BG)
head(fig,'Whole-garment knitting drops linking: about a third of the labour, but longer machine time','Labour per piece (min) for a 12-gauge plain-knit crew-neck sweater; blue = linking; worked example')
ax=fig.add_axes([0.223,0.17,0.735,0.65])
trad=[(17/8,'#c3c3b7'),(32,BLUE),(10,'#d9d8d2'),(8,'#e4e4de')]
whole=[(30/8,'#c3c3b7'),(5,'#cfcfc8'),(8,'#dcdbd5')]
for y,segs in [(1,trad),(0,whole)]:
    l=0
    for w,c in segs:
        ax.barh(y,w,0.36,left=l,color=c,edgecolor=BG,lw=2); l+=w
    ax.text(l+1,y,f'{l:.0f} min',va='center',fontsize=13,fontweight='bold')
ax.text(2.1+16,1,'Linking',ha='center',va='center',color='white',fontsize=13)
kw=dict(fontsize=12.5,color='#444444',ha='center',va='top')
ax.text(1.1,0.77,'Knitting (tending)',**kw); ax.text(39.1,0.77,'Hand sewing, mending',**kw); ax.text(48.1,0.64,'Washing, pressing, inspection',**kw)
ax.text(1.9,-0.23,'Knitting (tending)',**kw); ax.text(6.25,-0.36,'Trimming yarn ends',**kw); ax.text(9.0,-0.23,'Washing, pressing, inspection',**dict(kw,ha='left'))
ax.set_xlim(0,60);ax.set_ylim(-0.6,1.35);ax.set_yticks([])
ax.xaxis.grid(True,color='#e3e3e3');ax.set_axisbelow(True);clean(ax);ax.spines['bottom'].set_visible(False)
ax.set_xlabel('Labour per piece (minutes)',color=MUT,fontsize=12.5,labelpad=12)
fig.text(0.014,0.705,'Shaped panels + linking',fontsize=13,fontweight='bold'); fig.text(0.014,0.665,'Machine time 17 min/piece',fontsize=12.5,color=MUT)
fig.text(0.014,0.405,'Whole-garment',fontsize=13,fontweight='bold'); fig.text(0.014,0.365,'Machine time 30 min/piece',fontsize=12.5,color=MUT)
fig.savefig(OUT+'w_7d16e7c0.png',facecolor=BG);plt.close(fig)

# ---- Fig. 29-6 batch size vs labour per piece (model of Section 29.5) ----
SAM=12;r0=0.63
def per_piece(Q,N,E,C,tau):
    Y=lambda t:60*N/SAM*E*(t-(1-r0)*tau*(1-np.exp(-t/tau)))-Q
    T=brentq(Y,1e-6,1e5); return 60*N*(C+T)/Q
L=dict(N=30,E=0.70,C=4,tau=12); U=dict(N=8,E=0.58,C=0.5,tau=6)
Qs=np.array([100,150,200,300,500,700,1000,1500,2000,3000,5000,7000,10000])
qq=np.logspace(2,4,400)
fL=lambda q:per_piece(q,**L); fU=lambda q:per_piece(q,**U)
qx=brentq(lambda q:fL(q)-fU(q),1000,10000)
print('150:',fL(150),fU(150),'cross',qx)
fig=plt.figure(figsize=(13.44,6.84),dpi=150,facecolor=BG)
head(fig,f'Below about {round(qx,-2):.0f} pieces per batch, the U-shaped cell needs less labour per piece','Labour per piece = all labour time taken by the batch ÷ pieces, incl. style-change downtime and the learning ramp; SAM = 12 min; worked example')
ax=fig.add_axes([0.105,0.15,0.86,0.63])
ax.plot(qq,[fL(q) for q in qq],color=GREY,lw=3); ax.plot(Qs,[fL(q) for q in Qs],'o',color=GREY,ms=6)
ax.plot(qq,[fU(q) for q in qq],color=BLUE,lw=3); ax.plot(Qs,[fU(q) for q in Qs],'o',color=BLUE,ms=6)
ax.axvline(qx,color='#888888',ls='--',lw=1.4)
ax.text(qx*1.03,98,f'Break-even batch about {round(qx,-2):.0f}',fontsize=12.5,va='top')
ax.text(115,fL(100),'Long line (30 people)',fontsize=12.5,color='#555555',va='center')
ax.text(160,fL(150)+2,f'150 pieces: {fL(150):.0f} min/piece',fontsize=12.5,fontweight='bold',va='bottom')
ax.text(160,fU(150)+2.5,f'{fU(150):.0f} min/piece',fontsize=13,fontweight='bold',color=BLUE,va='bottom')
ax.text(103,fU(100)-9,'U-shaped cell (8 people)',fontsize=12.5,color=BLUE,va='top')
ax.set_xscale('log');ax.set_xlim(100,10000);ax.set_ylim(0,100)
ax.set_xticks([100,200,500,1000,2000,5000,10000]);ax.set_xticklabels(['100','200','500','1000','2000','5000','10000'])
ax.minorticks_off();ax.set_yticks([0,20,40,60,80,100])
ax.yaxis.grid(True,color='#e3e3e3');ax.set_axisbelow(True);clean(ax)
ax.set_xlabel('Order batch size (pieces, log scale)',color=MUT,fontsize=12.5,labelpad=8)
ax.text(100,104,'min/piece',fontsize=12.5,color=MUT,ha='right')
fig.savefig(OUT+'w_b27b372e.png',facecolor=BG);plt.close(fig)
