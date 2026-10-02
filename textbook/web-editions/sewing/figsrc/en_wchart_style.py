# shared look for the English redraws of the ch02/ch03 web charts
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.family':['DejaVu Sans'],'axes.edgecolor':'#cfcfc8','axes.linewidth':1.0,
  'xtick.color':'#555','ytick.color':'#555','xtick.labelsize':13,'ytick.labelsize':13,'axes.labelcolor':'#333'})
BG='#faf9f5'; BLUE='#2b77d6'; G1='#c3c3b8'; G2='#dcdcd5'; GRID='#e6e6e2'; DARK='#111111'; MUTED='#555555'
r=15.5; L0=55.0; W=5000*2*np.pi/60
def x_of(phi_deg,l=L0):
    p=np.radians(phi_deg); lam=r/l; b=np.arcsin(lam*np.sin(p)); return r*(1-np.cos(p))-l*(1-np.cos(b))
def v_of(phi_deg,l=L0):  # m/s
    p=np.radians(phi_deg); lam=r/l; b=np.arcsin(lam*np.sin(p))
    return W*r*np.sin(p)*(1-lam*np.cos(p)/np.cos(b))/1000
def a_of(phi_deg,l=L0,h=1e-3):  # km/s^2, central difference in angle
    return (v_of(phi_deg+h,l)-v_of(phi_deg-h,l))/np.radians(2*h)*W/1000
def header(fig,title,sub,W_px,H_px):
    fig.text(42/W_px,1-40/H_px,title,fontsize=17.5,fontweight='bold',color=DARK,va='center')
    fig.text(42/W_px,1-77/H_px,sub,fontsize=12.5,color=MUTED,va='center')
def clean(ax):
    for s in ['top','right','left']: ax.spines[s].set_visible(False)
    ax.tick_params(length=0); ax.set_facecolor(BG)
