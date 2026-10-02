"""Monte Carlo of the hook-point clearance chain (port of the RNG and model in src/zh/labs/tol.html)."""
import math
M=0xFFFFFFFF
def imul(a,b): return ((a&M)*(b&M))&M
def rng(seed):
    s=[seed&M]
    def r():
        s[0]=(s[0]+0x6D2B79F5)&M; t=s[0]
        t=imul(t^(t>>15),t|1)
        t=(t^((t+imul(t^(t>>7),t|61))&M))&M
        return ((t^(t>>14))&M)/4294967296
    return r
def gauss(r):
    u=0
    while u==0: u=r()
    v=r(); return math.sqrt(-2*math.log(u))*math.cos(2*math.pi*v)
CH=[(0.03,1,0),(0.008,0,0),(0.02,1,0),(0.02,0,1),(0.015,0,1),(0.03,1,0),(0.02,1,0),(0.01,0,0)]
def sim(adj,swap,seed):
    r=rng(seed);gs=[]
    for k in range(4000):
        e=[gauss(r)*c[0]/3 for c in CH]
        if adj:
            g=0.07+gauss(r)*0.01/3
            for i,c in enumerate(CH):
                if not c[1] and not c[2]: g+=e[i]
        else: g=0.07+sum(e)
        if swap:
            for i,c in enumerate(CH):
                if c[2]: g+=gauss(r)*c[0]/3-e[i]
        gs.append(g)
    ok=sum(1 for g in gs if 0.04<=g<=0.10)/4000; m=sum(gs)/4000; sd=math.sqrt(sum((g-m)**2 for g in gs)/4000)
    return gs,ok,sd


# ---- speed-increase case (page B of tol.html) ----
F1, F2, N0, K, L0 = 300, 120, 5000, 1e8, 83.5


def vib(n, fn=190, z=0.03, m=1.0):
    k = K * (fn / 190) ** 2
    o = []
    for order, F0 in ((1, F1), (2, F2)):
        f = order * n / 60; r = f / fn; F = F0 * m * (n / N0) ** 2
        Am = 1 / math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2)
        X = F / k * Am; v = 2 * math.pi * f * X / math.sqrt(2) * 1000
        o.append(dict(f=f, r=r, Am=Am, v=v))
    return o, math.hypot(o[0]['v'], o[1]['v'])


VREF = vib(5000)[1]
noise = lambda n, fn=190, z=0.03, m=1.0: L0 + 20 * math.log10(vib(n, fn, z, m)[1] / VREF)
