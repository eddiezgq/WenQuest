# -*- coding: utf-8 -*-
"""第 24 章 机针与旋梭的制造 —— 共用模型（与虚拟实验 labs/hookfit.html 完全一致）。

随机数：mulberry32 + Box–Muller，和实验页里的 JS 逐位相同，所以同一组参数、同一个种子，
书中算例和实验页面给出同样的数。所有数值都是示意/算例值。
"""
import math

# ------------------------------------------------------------ 随机数（与 JS 相同）
M32 = 0xFFFFFFFF


def _imul(a, b):
    return (a * b) & M32


def rng(seed):
    s = [seed & M32]

    def r():
        s[0] = (s[0] + 0x6D2B79F5) & M32
        t = s[0]
        t = _imul(t ^ (t >> 15), t | 1)
        t ^= (t + _imul(t ^ (t >> 7), t | 61)) & M32
        return ((t ^ (t >> 14)) & M32) / 4294967296
    return r


def gauss(r):
    u = 0.0
    while u == 0.0:
        u = r()
    v = r()
    return math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)


# ------------------------------------------------------------ 旋梭选配模型（24.7 节）
# 偏差一律以 μm 计，相对各自的名义尺寸。间隙 c = C0 + x − y（x：梭道直径偏差，y：梭床导轨外径偏差）
C0, CMIN, CMAX = 20.0, 10.0, 30.0      # 名义直径间隙与允许范围（μm，示意）
TOL = 15.0                              # 两零件图纸公差 ±15 μm；超出的零件判废
N = 2000                                # 一批 2000 套
COST_REF_SIGMA = 5.0                    # σ = 5 μm 时每件加工成本 10 元；σ 减半成本加倍
COST_REF = 10.0
COST_MEAS = 0.5                         # 每件测量 0.5 元（两种方案都 100% 测量）
COST_GROUP = 0.4                        # 每多分一组，每套增加 0.4 元的分组、存放与管理费用
STD = dict(muD=0.0, sD=5.0, mud=0.0, sd=5.0, k=1, sm=1.0, seed=24)


def part_cost(sig):
    return COST_REF * COST_REF_SIGMA / sig


def simulate(muD=0.0, sD=5.0, mud=0.0, sd=5.0, k=1, sm=1.0, seed=24, n=N, keep=False):
    r = rng(seed)
    xs = [muD + sD * gauss(r) for _ in range(n)]          # 梭道直径偏差（真值）
    ys = [mud + sd * gauss(r) for _ in range(n)]          # 梭床外径偏差（真值）
    mx = [x + sm * gauss(r) for x in xs]                  # 测得值（含测量误差）
    my = [y + sm * gauss(r) for y in ys]
    w = 2 * TOL / k

    def grp(m):
        if m < -TOL or m > TOL:
            return -1                                     # 按测得值判废
        return min(k - 1, int((m + TOL) // w))
    gD = [[] for _ in range(k)]
    gd = [[] for _ in range(k)]
    scrapD = scrapd = 0
    for i in range(n):
        a = grp(mx[i])
        if a < 0:
            scrapD += 1
        else:
            gD[a].append(xs[i])
        b = grp(my[i])
        if b < 0:
            scrapd += 1
        else:
            gd[b].append(ys[i])
    cs = []
    left = 0
    per = []
    for j in range(k):
        m = min(len(gD[j]), len(gd[j]))
        per.append((len(gD[j]), len(gd[j])))
        for i in range(m):                                # 组内按入组顺序配对（相当于随机配对）
            cs.append(C0 + gD[j][i] - gd[j][i])
        left += abs(len(gD[j]) - len(gd[j]))
    sets = len(cs)
    good = sum(1 for c in cs if CMIN <= c <= CMAX)
    total = n * (part_cost(sD) + part_cost(sd) + 2 * COST_MEAS) + sets * COST_GROUP * (k - 1)
    res = dict(sets=sets, good=good, pass_rate=good / max(sets, 1), left=left, left_rate=left / (2 * n),
               scrap=scrapD + scrapd, cost=total / max(good, 1), per=per,
               mean=sum(cs) / max(sets, 1),
               sd=(sum((c - sum(cs) / sets) ** 2 for c in cs) / sets) ** 0.5 if sets else 0)
    if keep:
        res['cs'] = cs
    return res


# ------------------------------------------------------------ 针孔宽度的工序能力与控制图（24.4 节）
LSL, USL = 0.340, 0.380                 # 针孔宽度规格（mm，Nm 90，示意）
A2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}
D2 = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}
D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}
NBASE, NTOT = 25, 50                    # 前 25 组定控制限，第 26 组起可注入漂移，共 50 组
STD2 = dict(mu=0.362, sig=0.004, n=5, drift=0.0, seed=7)


def Phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def spc(mu=0.362, sig=0.004, n=5, drift=0.0, seed=7):
    """drift 以 σ 为单位，从第 26 组起加到均值上。返回子组均值、极差、控制限、Cpk 与报警组号。"""
    r = rng(seed)
    xb, rg, raw = [], [], []
    for g in range(NTOT):
        m = mu + (drift * sig if g >= NBASE else 0.0)
        s = [m + sig * gauss(r) for _ in range(n)]
        raw.append(s)
        xb.append(sum(s) / n)
        rg.append(max(s) - min(s))
    xbb = sum(xb[:NBASE]) / NBASE
    rb = sum(rg[:NBASE]) / NBASE
    ucl, lcl = xbb + A2[n] * rb, xbb - A2[n] * rb
    sig_hat = rb / D2[n]
    cp = (USL - LSL) / (6 * sig_hat)
    cpk = min(USL - xbb, xbb - LSL) / (3 * sig_hat)
    alarm = None
    for g in range(NBASE, NTOT):
        if xb[g] > ucl or xb[g] < lcl or rg[g] > D4[n] * rb:
            alarm = g + 1
            break
    # 理论值（用真 μ、σ）
    cpk_true = min(USL - mu, mu - LSL) / (3 * sig)
    ppm = (Phi((LSL - mu) / sig) + 1 - Phi((USL - mu) / sig)) * 1e6
    p1 = Phi(-3 + drift * math.sqrt(n)) + Phi(-3 - drift * math.sqrt(n))
    arl1 = 1 / p1
    return dict(xb=xb, rg=rg, raw=raw, xbb=xbb, rb=rb, ucl=ucl, lcl=lcl, uclr=D4[n] * rb, sig_hat=sig_hat,
                cp=cp, cpk=cpk, alarm=alarm, cpk_true=cpk_true, ppm=ppm, arl1=arl1)


def arl(delta, n):
    p = Phi(-3 + delta * math.sqrt(n)) + Phi(-3 - delta * math.sqrt(n))
    return 1 / p
