"""第 31 章 人工智能与制衣业 —— 课程包数值题计算（模型与虚拟实验 31-1 相同）"""
import math
from statistics import NormalDist
N = NormalDist()
Phi = N.cdf

def inspect(prev, dp, t, cm=20, cf=0.5, n=1000):
    tpr = 1-Phi(t-dp); fpr = 1-Phi(t)
    tp, fp, fn = prev*tpr, (1-prev)*fpr, prev*(1-tpr)
    return dict(tpr=tpr, fpr=fpr, prec=tp/(tp+fp), alarms=(tp+fp)*n, tp=tp*n, fp=fp*n, fn=fn*n, cost=n*(fn*cm+fp*cf))
def best_t(prev, dp, cm=20, cf=0.5):
    return min((i/100 for i in range(-100,601)), key=lambda t: inspect(prev,dp,t,cm,cf)['cost'])
def t_star(prev, dp, cm=20, cf=0.5):
    return dp/2 + math.log((1-prev)*cf/(prev*cm))/dp

r = inspect(0.02,3.53,1.88); print("默认", {k:round(v,4) for k,v in r.items()})
for p in (0.10,0.01,0.05): print("次品率",p,"精确率",round(inspect(p,3.53,1.88)['prec'],4))
for p in (0.02,0.10,0.01):
    bt=best_t(p,3.53); print("最省阈值",p,bt,"公式",round(t_star(p,3.53),4),"成本",round(inspect(p,3.53,bt)['cost'],2))
print("t=1.88 成本", inspect(0.02,3.53,1.88)['cost'])
# 精确率 80%、召回率 90% 所需 d′（π=2%）
fpr_max = 0.02*0.9*(1-0.8)/0.8/0.98; t = N.inv_cdf(1-fpr_max); print("所需 fpr≤",fpr_max,"t",t,"d′",t+N.inv_cdf(0.9))
# 习题 1、2
pi=0.03; print("习题1 报警", 1000*(pi*0.9+(1-pi)*0.05), "精确率", pi*0.9/(pi*0.9+(1-pi)*0.05))
print("习题2", 1000*(pi*0.1*30+(1-pi)*0.05*1), 1000*(pi*0.2*30+(1-pi)*0.02*1))
# 测验：召回 95% 误报 3%，次品率 5%：报警件数、精确率
pi=0.05; tp=pi*0.95; fp=(1-pi)*0.03; print("5%: 报警", 1000*(tp+fp), "精确率", tp/(tp+fp))
# 考试：次品率 4%，召回 92%，误报 4%，Cm=25，Cf=0.8：成本
pi=0.04; print("考试成本", 1000*(pi*0.08*25+(1-pi)*0.04*0.8), "精确率", pi*0.92/(pi*0.92+(1-pi)*0.04))
# 永远说合格 的准确率
print("全放行准确率 2%:", 0.98)
# t* for Cf=1 (π=2%) 测验
print("t* Cf=1:", t_star(0.02,3.53,20,1.0), " Cm=40:", t_star(0.02,3.53,40,0.5))

# ---- 预测性维护（移植实验页 fleet/alarms，mulberry32 随机数）----
def rng(seed):
    s=[seed & 0xffffffff]
    def imul(a,b): return ((a & 0xffffffff)*(b & 0xffffffff)) & 0xffffffff
    def f():
        s[0]=(s[0]+0x6D2B79F5)&0xffffffff; t=s[0]
        t=imul(t^(t>>15), t|1)
        t^=(t+imul(t^(t>>7), t|61)) & 0xffffffff
        return ((t^(t>>14)) & 0xffffffff)/4294967296
    return f
def gauss(r):
    u=r()
    while u==0: u=r()
    v=r(); return math.sqrt(-2*math.log(u))*math.cos(2*math.pi*v)
def fleet(sigma,n=200,days=180,frac=0.5,T=30,k=0.1,seed=11):
    r=rng(seed); M=[]
    for i in range(n):
        deg=r()<frac; t0=30+math.floor(r()*121) if deg else None; sig=[]
        for d in range(days):
            x=1+sigma*gauss(r)
            if deg and d>=t0: x+=(math.exp(k*(d-t0))-1)/(math.exp(k*T)-1)
            sig.append(x)
        M.append((deg,t0,t0+T if deg else None,sig))
    return M
def alarms(M,thr,w,days=180):
    det=lead=fal=ndeg=hd=0
    for deg,t0,fail,s in M:
        armed=True; caught=False; sm=0; end=fail if deg and fail<days else days; ndeg+=deg
        for d in range(end):
            sm+=s[d]
            if d>=w: sm-=s[d-w]
            if d<w-1: continue
            ma=sm/w; healthy=(not deg) or d<t0
            if healthy: hd+=1
            if ma>thr and armed:
                armed=False
                if healthy: fal+=1
                elif not caught: caught=True; det+=1; lead+=fail-d
            elif ma<=thr: armed=True
    return dict(det=det/max(ndeg,1), lead=lead/max(det,1), fpm=fal/max(hd,1)*30, ndeg=ndeg)
M=fleet(0.08)
for thr,w in ((1.15,1),(1.12,3),(1.10,3),(1.14,3)):
    print("PdM", thr, w, {k:round(v,3) for k,v in alarms(M,thr,w).items()})
best={}
for w in (1,2,3,4,5,7,10):
    c=[(round(1.02+0.01*i,2),alarms(M,1.02+0.01*i,w)) for i in range(70)]
    ok=[(t,a) for t,a in c if a['fpm']<=0.1 and a['det']>=0.95]
    if ok: t,a=max(ok,key=lambda x:x[1]['lead']); print("窗口",w,"最佳阈值",t,round(a['lead'],2),round(a['fpm'],3))
print("单点误报 0.85×200 =", 0.85*200)
