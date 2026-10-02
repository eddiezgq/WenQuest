"""English version of w_c094b35b: edge strain vs differential ratio for five fabrics.
Data recomputed from the simplified model of Section 9.10 (labs/difffeed.html, function model)."""
import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family']=['DejaVu Sans']
BG='#faf9f5'; INK='#1f1f1f'; MUT='#555555'; GRID='#e4e4e4'
FAB=[('Single jersey',0.18,0.85,0.35,0.6,'#2a78d6'),('Rib knit',0.30,0.80,0.30,0.8,'#eb6834'),('Sweatshirt fleece',0.10,0.90,0.25,0.4,'#1baf7a'),
     ('Chiffon',-0.06,0.95,0.55,0.08,'#0d366b'),('Twill',0.01,0.90,0.12,0.02,'#d55181')]
def eps(f,D):
    _,e0,eta,gmax,emax,_c=f; De=1+eta*(D-1); De=min(De,1/(1-gmax)); De=max(De,1/(1+emax)); return (1+e0)/De-1
D=np.round(np.arange(0.6,2.0001,0.1),2)
fig=plt.figure(figsize=(13.44,8.62),dpi=150,facecolor=BG)
fig.text(0.021,0.965,'Every fabric has its own “flat differential ratio”: above 1 for knits, below 1 for light wovens',fontsize=15,fontweight='bold',color=INK,va='top')
fig.text(0.021,0.925,'Computed with the simplified model of Section 9.10; where a curve levels off, the feed dogs start to slip',fontsize=11.2,color=MUT,va='top')
ax=fig.add_axes([0.093,0.12,0.645,0.735],facecolor=BG)
for s in ax.spines.values(): s.set_visible(False)
ax.spines['bottom'].set_visible(True); ax.spines['bottom'].set_color('#cfcfcf')
ax.set_xlim(0.6,2.0); ax.set_ylim(-0.62,1.0)
ax.set_yticks(np.arange(-0.6,1.01,0.2)); ax.set_yticklabels(['-60%','-40%','-20%','0%','+20%','+40%','+60%','+80%','+100%'])
ax.set_xticks(np.arange(0.6,2.01,0.2)); ax.set_xticklabels([f'{v:.1f}' for v in np.arange(0.6,2.01,0.2)])
ax.tick_params(labelsize=11,colors=MUT,length=0,pad=8); ax.grid(axis='y',color=GRID,lw=1); ax.set_axisbelow(True)
ax.axhspan(-0.02,0.02,color='#e6e6e3',lw=0,zorder=0); ax.text(1.97,0.035,'Flat zone ±2%',ha='right',va='bottom',fontsize=11,color=MUT)
for f in FAB:
    y=[eps(f,d) for d in D]; ax.plot(D,y,color=f[5],lw=2.4,marker='o',ms=4.2,label=f[0],clip_on=False)
ax.set_xlabel('Differential ratio D',fontsize=12,color=MUT,labelpad=10)
fig.text(0.093,0.873,'Edge strain ε',fontsize=11.5,color=MUT,va='bottom',ha='center')
lg=ax.legend(loc='upper left',bbox_to_anchor=(1.055,0.93),frameon=False,fontsize=12.5,handlelength=2.2,labelspacing=1.45,handletextpad=0.8)
for h in lg.legend_handles: h.set_marker(''); h.set_linewidth(3.2)
fig.text(0.776,0.47,'Where a curve passes through\nthe grey band is the right\ndifferential ratio for that fabric',fontsize=11.5,color=MUT,va='top',linespacing=1.7)
fig.savefig(sys.argv[1] if len(sys.argv)>1 else 'img/en/w_c094b35b.png',facecolor=BG)
