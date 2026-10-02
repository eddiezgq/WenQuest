"""Overlock timing kinematics, ported from src/en/labs/model-overlock.html (K table = the chapter's calculation)."""
import re, json, numpy as np, os
_s=open(os.path.join(os.path.dirname(__file__),'..','src','en','labs','model-overlock.html')).read()
K=json.loads(re.search(r'const K=(\{.*?\});\n',_s).group(1))
UP=np.array(K['UP']); EWB=np.array(K['EWB']); EV=np.array(K['EV']); EU=np.array([1.,0,0]); PIV=np.array(K['PIVOT_LL'])
def rotUp(v,t): return v*np.cos(t)+np.cross(UP,v)*np.sin(t)+UP*np.dot(UP,v)*(1-np.cos(t))
def llTip(th): return PIV+rotUp(-EWB,th)*K['R_LL']
def ulTip(psi):
    U=K['UL']; Q=np.array(K['O_UL'])+EU*U['cr']*np.cos(psi)+EV*U['cr']*np.sin(psi); d=np.array(K['G_UL'])-Q; u=d/np.linalg.norm(d)
    n=EU*(-np.dot(u,EV))+EV*np.dot(u,EU); return Q+u*U['L']+n*U['h']
def table():
    out=[]
    for i,r in enumerate(K['rows']):
        pr=np.radians(i)
        out.append((i, r['a_tip']*np.cos(K['INC']), llTip(r['th'])[0], ulTip(r['psi'])[2],
                    (K['FEED_LIFT_TOP']+0.6)*np.cos(pr)-0.6, -K['KNIFE_OVERLAP']+K['KNIFE_STROKE']*(1-np.cos(pr-K['KNIFE_LOW_PHI']))/2, ulTip(r['psi'])[0]))
    out.append((360,)+out[0][1:]); return np.array(out)
if __name__=='__main__':
    T=table()
    for i in range(0,361,30): print(T[i].round(2))
    print('needle max/min',T[:,1].max(),T[:,1].min(),'ll x at 125',T[125,2],'ul z min at',T[:,3].argmin(),'ul x min at',T[:,6].argmin(),T[:,6].min())
