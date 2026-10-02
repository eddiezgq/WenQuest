"""RSSR kinematics ported from src/en/labs/rssr.html (presets LL = lower looper, UL = upper looper)."""
import numpy as np
D2R=np.pi/180; OMEGA=2*np.pi*7000/60; M0=np.array([22.0,1.27606,-51.53467])
PRE={'LL':dict(r=4.3619,b=22.4789,c=22,gam=90,bet=20,dl=-7.133,s=0,dy=0,dz=0,Q=[0,16.6497,-67.772],xc=22,ph0=-2.50136),
     'UL':dict(r=7.3801,b=29.47,c=20,gam=90,bet=-75.97,dl=0,s=0,dy=0,dz=0,Q=[35.3839,-18.6172,-72.7627],xc=15.3839,ph0=0.244346)}
unit=lambda a:a/np.linalg.norm(a)
def rot(v,e,t): return v*np.cos(t)+np.cross(e,v)*np.sin(t)+e*np.dot(e,v)*(1-np.cos(t))
def run(k,br=1):
    P=PRE[k]; ex=np.array([1.,0,0]); g,bt=P['gam']*D2R,P['bet']*D2R
    e=unit(np.array([np.cos(g),np.sin(g)*np.sin(bt),np.sin(g)*np.cos(bt)]))
    ref=unit(ex-e*np.dot(ex,e)); v0=rot(ref,e,P['dl']*D2R); v1=np.cross(e,v0)
    Q=np.array(P['Q'])+e*P['s']+np.array([0,P['dy'],P['dz']]); C=np.array([P['xc'],M0[1],M0[2]])
    rows=[];prev=None
    for kk in range(361):
        ang=kk*D2R+P['ph0']; A=C+P['r']*np.array([0,np.cos(ang),np.sin(ang)])
        Ad=np.cross(ex,A-C)*OMEGA; Add=(A-C)*(-OMEGA**2)
        K=A-Q; Pp=K@v0; Kk=K@v1; Mm=(K@K+P['c']**2-P['b']**2)/(2*P['c']); rho=np.hypot(Pp,Kk)
        th=np.arctan2(Kk,Pp)+br*np.arccos(Mm/rho)
        if prev is not None:
            while th-prev>np.pi: th-=2*np.pi
            while th-prev<-np.pi: th+=2*np.pi
        prev=th
        rr=(v0*np.cos(th)+v1*np.sin(th))*P['c']; B=Q+rr; d=A-B; t=np.cross(e,rr); den=d@t
        thd=d@Ad/den; dd=Ad-t*thd; thdd=(dd@dd+d@Add+thd*thd*(d@rr))/den
        gm=np.arcsin(min(1,abs(den)/(np.linalg.norm(d)*np.linalg.norm(t))))/D2R
        rows.append((kk,th/D2R,thd,thdd,gm))
    return np.array(rows)
if __name__=='__main__':
    for k in PRE:
        r=run(k); print(k,'swing',r[:,1].max()-r[:,1].min(),'gmin',r[:,4].min(),r[r[:,4].argmin(),0],'wmax',abs(r[:,2]).max(),'amax',abs(r[:,3]).max())
        for i in range(0,361,30): print(r[i].round(1))
