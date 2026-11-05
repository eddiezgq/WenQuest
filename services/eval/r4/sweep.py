import numpy as np, itertools
g=9.8
def rng(a,b,s):
    if s==0: return [a]
    return list(np.round(np.arange(a,b+s/2,s),6))
# b1
bad=0;mn=1e9
for h0,x,th in itertools.product(rng(.6,1.2,.1),rng(3,5,.5),rng(45,65,5)):
    t=np.radians(th); d=h0+x*np.tan(t)-2.43
    if d<=0: bad+=1; continue
    v=np.sqrt(g*x*x/(2*np.cos(t)**2*d)); mn=min(mn,v)
print('b1 bad',bad,'minv',mn)
def xh(v,h0,th):
    t=np.radians(th); vy=v*np.sin(t); vx=v*np.cos(t)
    disc=vy*vy-2*g*(2.43-h0)
    return vx*(vy+np.sqrt(disc))/g if disc>=0 else None
def v0(h0,x,th):
    t=np.radians(th); d=h0+x*np.tan(t)-2.43
    return np.sqrt(g*x*x/(2*np.cos(t)**2*d))
mx=0
for h0,x,th,dv in itertools.product([.8],rng(3.5,5,.5),rng(45,65,10),rng(.1,.2,.05)):
    v=v0(h0,x,th); h=1e-5
    lin=(xh(v+h,h0,th)-xh(v-h,h0,th))/(2*h)*dv
    a=xh(v+dv,h0,th);b=xh(v-dv,h0,th)
    if a is None or b is None: print('c1 unreach',h0,x,th,dv);continue
    mx=max(mx,abs(a-x-lin)/lin,abs(x-b-lin)/lin)
    #ascending-branch ambiguity: crossing hoop height on rise?
print('c1 max rel diff finite vs linear',mx)
# c1 up-crossing exists?
t=np.radians(45);
# 1.4 tie
for h,b,mu in itertools.product(rng(.3,.8,.1),rng(.4,.8,.1),rng(.4,.8,.1)):
    if abs(b/(2*h)-mu)<1e-6: print('tie',h,b,mu)
# 1.5 a2
for w,u in itertools.product(rng(.5,2,.5),rng(2,5,.5)):
    if u<=w: print('a2 nosol',w,u)
# 1.5 a1 ok? va>vw
print(min(va-vw for va in rng(8,15,1) for vw in rng(2,6,1)))
# 1.2 b1
Ts=[1.414*s/(v*e) for s in rng(.005,.02,.005) for v in rng(.3,1,.1) for e in rng(.03,.1,.01)]
print(min(Ts),max(Ts))
# c2 allowed dv
r=[]
for h0,x,th,e in itertools.product(rng(.6,1,.2),rng(3.5,5,.5),rng(45,65,10),rng(.05,.15,.05)):
    v=v0(h0,x,th);h=1e-5
    s=(xh(v+h,h0,th)-xh(v-h,h0,th))/(2*h); r.append(e/s)
print('c2 dv',min(r),max(r))
