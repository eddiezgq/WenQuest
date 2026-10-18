# -*- coding: utf-8 -*-
"""平缝机机构库（第 39 轮）：教材共用库 lockstitch-kit.js（WQLS，第 20 轮）的 Python 版。

公式、常数、判据与 JS 版逐条对应（tests/test_sewcore.py 用 node 跑 JS 版逐项对数）；
不同之处只有一处：刺布机构的曲柄半径 r、连杆长 l、针尖上止点高度等做成参数（Mech(r=..., l=...)），
用默认值时与教材算例完全一致，改了就是“设计一台新机器”。
纯 Python、不依赖 numpy：网关和 FreeCAD 工作台用同一份。
角度单位：度，主轴转角 0° = 针杆上止点。长度 mm。
"""
import math

DEG = math.pi / 180


def _clamp(v, a, b):
    return max(a, min(b, v))


def _mod(a):
    return ((a % 360) + 360) % 360


class LCG:
    """实验 5-1 的随机数（glibc 式 LCG，按双精度运算，与 JS 版逐位一致）"""

    def __init__(self, seed):
        self.seed = float(seed)

    def rnd(self):
        self.seed = math.fmod(self.seed * 1103515245.0 + 12345.0, 2147483648.0)
        return self.seed / 2147483648.0

    def gauss(self):
        u = v = 0.0
        while not u:
            u = self.rnd()
        while not v:
            v = self.rnd()
        return math.sqrt(-2 * math.log(u)) * math.cos(2 * math.pi * v)


def hull_perim(pts):
    p = sorted(([q[0], q[1]] for q in pts), key=lambda q: (q[0], q[1]))
    if len(p) < 2:
        return 0.0

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    h = lo[:-1] + up[:-1]
    s = 0.0
    for i in range(len(h)):
        a, b = h[i], h[(i + 1) % len(h)]
        s += math.hypot(b[0] - a[0], b[1] - a[1])
    return s


def smooth(u):
    u = min(1, max(0, u))
    return u * u * (3 - 2 * u)


# 挑线四杆（算例；坐标 mm，原点 = 上轴中心，z 向右、y 向上）
LK0 = dict(r=20.7, d=-6.8, Qz=21.5, Qy=-45.5, a=43.4, b=40.9, c=65.7, al=2.8)
AC = (122.2, -45.7)
ADIR = (math.cos(285.2 * DEG), math.sin(285.2 * DEG))
B_GUIDE = (66.4, -117.7)

# 第 5 章
HOOK_H0, HOOK_TB, HOOK_DREF, HOOK_RH = 2.2, 0.15, 0.9, 13.5
HOOK_FAB = {"woven": dict(W=0.75, sd=0.10), "knit": dict(W=0.5, sd=0.15)}

# 第 6 章
FEED_A, FEED_H0 = 1.1, 0.8
FEED_FAB = {"lining": dict(t=0.4, mud=0.55, muf=0.15, F0=0.32, K=10, hreq=0.7, hmax=0.85, Pmark=1.4, name="衬里滑料", en="Lining (slippery)"),
            "cotton": dict(t=1.5, mud=0.80, muf=0.25, F0=0.30, K=50, hreq=0.75, hmax=1.1, Pmark=2.0, name="棉布", en="Cotton"),
            "denim": dict(t=4.0, mud=0.85, muf=0.30, F0=0.75, K=40, hreq=0.95, hmax=1.5, Pmark=2.5, name="牛仔布", en="Denim")}
MODEF = {"drop": 1.0, "needle": 0.3, "compound": 0.08}

# 第 7 章
GUIDE = math.exp(0.2 * 1.0)
EYEK = math.exp(-0.35 * math.pi)
KN = GUIDE * EYEK
THREAD = {"t18": dict(name="Tex 18", F=700, el=0.14), "t24": dict(name="Tex 24", F=1000, el=0.15), "t40": dict(name="Tex 40", F=1700, el=0.16)}
TEN_FAB = {"lining": dict(name="衬里两层", t=0.4, Tmin=20, pf=0.30, B=1.8, jam="t24", plim=0.15),
           "cotton": dict(name="衬衫棉布两层", t=1.0, Tmin=35, pf=0.60, B=2.2, jam="t40", plim=0.3),
           "denim": dict(name="牛仔布四层", t=4.0, Tmin=100, pf=4.0, B=3.0, jam="t40", plim=0.3)}
ORDER = ["t18", "t24", "t40"]

# 整机（第 20 轮）
STD = dict(psi=0, dz=0, g=0.08, d=0.9, u=0, stroke=10, fab="cotton", th="t24", Td=100, Tb=40, dT=0, dP=0, h=0.8, P=1.0, s=3,
           n=5000, k=0.3, mode="drop")
FT = {"lining": 0.4, "cotton": 1.5, "denim": 4.0}


class Mech:
    """一台平缝机的机构模型。r、l：刺布曲柄半径与连杆长（mm）；tip0：针尖在上止点时高出针板（mm）；
    eye_tdc：上止点时针眼上沿高出针板；eye：针眼上沿到针尖；mr：针杆组件质量（kg）。"""

    def __init__(self, r=15.5, l=55.0, tip0=18.0, eye_tdc=20.0, eye=2.0, mr=0.12, lk=None):
        self.RN, self.LN, self.LAM = float(r), float(l), float(r) / float(l)
        self.TIP0, self.EYE_TDC, self.EYE, self.mr = tip0, eye_tdc, eye, mr
        self.LK0 = dict(LK0, **(lk or {}))
        # 钩线时刻：机针回升 2 mm 的转角（二分 60 次，同实验 5-1）
        a, b = 181.0, 240.0
        for _ in range(60):
            m = (a + b) / 2
            if self.rise(m) < 2:
                a = m
            else:
                b = m
        self.PHC0 = (a + b) / 2
        self.YP = self.xN(round(self.PHC0)) - 8      # 针板上面高出旋梭中心：206° 钩线时梭尖在针眼上方 1.5 mm
        self.FE = self.cross(-self.EYE)              # 针眼上沿到达针板（114.2°）
        self.HALF0 = math.acos((FEED_A - FEED_H0) / FEED_A) / DEG
        self.PHL0 = self.FE - self.HALF0
        self.EFF0 = (1 - math.cos(2 * self.HALF0 * DEG)) / 2
        self._table = None
        self._sup = {}

    # ---------- 第 3 章 刺布曲柄滑块 ----------
    def xN(self, f):
        a = f * DEG
        return self.RN * (1 - math.cos(a)) - self.LN * (1 - math.sqrt(1 - (self.LAM * math.sin(a)) ** 2))

    def rise(self, f):
        return self.xN(180) - self.xN(f)

    def vel(self, f, n):
        """针杆速度 m/s"""
        w, p, la = n * math.pi / 30, f * DEG, self.LAM
        S = math.sqrt(1 - la * la * math.sin(p) ** 2)
        return w * self.RN * math.sin(p) * (1 - la * math.cos(p) / S) / 1000

    def acc(self, f, n):
        """针杆加速度 m/s²（精确式）"""
        return self.aN(f, n * math.pi / 30)

    def aN(self, f, w):
        a, L = f * DEG, self.LAM
        S = math.sqrt(1 - L * L * math.sin(a) ** 2)
        return self.RN * 1e-3 * w * w * (math.cos(a) - L * (math.cos(2 * a) + L ** 2 * math.sin(a) ** 4) / S ** 3)

    def tip(self, f):
        return self.TIP0 - self.xN(f)

    def cross(self, lv):
        a, b = 0.0, 180.0
        for _ in range(60):
            m = (a + b) / 2
            if self.tip(m) > lv:
                a = m
            else:
                b = m
        return (a + b) / 2

    # ---------- 第 4 章 挑线：供线量与耗线量 ----------
    def loop_pts(self, f, t, phc):
        RH, RC = 13.5, 11.0
        x = self.xN(f)
        e = self.EYE_TDC - t - x
        F = [0, self.YP + t]
        th = (90 - 2 * (f - phc)) * DEG
        H = [RH * math.cos(th), RH * math.sin(th)]
        pts = [F, H]
        sw = 2 * (f - phc)
        a = 0
        while a < sw:
            q = (90 - a) * DEG
            pts.append([RC * math.cos(q), RC * math.sin(q)])
            a += 1
        if e < 0:
            pts.append([0, self.YP + t + e])
        return pts

    def demand_raw(self, f, t, phc):
        x = self.xN(f)
        e = self.EYE_TDC - t - x
        if f < phc:
            return 2 * max(0, -e)
        P = hull_perim(self.loop_pts(f, t, phc))
        tail = P + e if e < 0 else e + P
        return x + tail - (self.EYE_TDC - t)

    def demand(self, f, t, s, phc):
        bot, off, c = phc + 90, phc + 135, s + t
        if f <= bot:
            return self.demand_raw(f, t, phc)
        if f <= off:
            Lb = self.demand_raw(bot, t, phc)
            u = smooth((f - bot) / (off - bot))
            return Lb * (1 - u) + c * u
        return c

    @staticmethod
    def link_pose(f, lk):
        q = (f + lk["d"]) * DEG
        P = [-lk["r"] * math.sin(q), -lk["r"] * math.cos(q)]
        Q = [lk["Qz"], lk["Qy"]]
        dz, dy = Q[0] - P[0], Q[1] - P[1]
        D = math.hypot(dz, dy)
        tt = (lk["a"] ** 2 - lk["b"] ** 2 + D * D) / (2 * D)
        h2 = lk["a"] ** 2 - tt * tt
        if not h2 > 0:
            return None
        h = math.sqrt(h2)
        mz, my = P[0] + tt * dz / D, P[1] + tt * dy / D
        M = [mz - h * dy / D, my + h * dz / D]
        uz, uy = (M[0] - P[0]) / lk["a"], (M[1] - P[1]) / lk["a"]
        ca, sa = math.cos(lk["al"] * DEG), math.sin(lk["al"] * DEG)
        E = [P[0] + lk["c"] * (uz * ca - uy * sa), P[1] + lk["c"] * (uz * sa + uy * ca)]
        w1, w2 = [P[0] - M[0], P[1] - M[1]], [Q[0] - M[0], Q[1] - M[1]]
        mu = math.acos(_clamp((w1[0] * w2[0] + w1[1] * w2[1]) / lk["a"] / lk["b"], -1, 1)) / DEG
        return dict(P=P, M=M, E=E, Q=Q, mu=mu)

    def takeup(self, u=0.0, t=1.5, s=3.0, phc=206, rpm=5000, lk=None):
        """供线量 S、耗线量 D 与判据（实验 4-1 的 compute，连杆式）"""
        lk = lk or self.LK0
        N = 360
        A = (AC[0] + u * ADIR[0], AC[1] + u * ADIR[1])
        S, E, mu, Lp = [0.0] * N, [], [], []
        for i in range(N):
            p = self.link_pose(i, lk)
            if not p:
                return dict(ok=False)
            E.append(p["E"])
            mu.append(p["mu"])
            Lp.append(math.hypot(p["E"][0] - A[0], p["E"][1] - A[1]) + math.hypot(p["E"][0] - B_GUIDE[0], p["E"][1] - B_GUIDE[1]))
        mx = max(Lp)
        S = [mx - v for v in Lp]
        top = min(range(N), key=lambda i: (S[i], i))
        bot = max(range(N), key=lambda i: (S[i], -i))
        c = s + t
        D = [c if i < top else self.demand(i, t, s, phc) for i in range(N)]
        sl = [S[i] - D[i] for i in range(N)]
        fin = 0
        while fin < 180 and self.xN(fin) < self.EYE_TDC - t:
            fin += 1
        margin, at = 1e9, 0
        for i in range(phc, min(359, phc + 135) + 1):
            if sl[i] < margin:
                margin, at = sl[i], i
        waste = max(sl[i] for i in range(phc, min(359, phc + 90) + 1))
        pre = max(sl[i] for i in range(top, fin + 1)) if fin >= top else -1e9
        neg = 0.0
        for i in range(fin, phc):
            neg = max(neg, -sl[i])
        w = rpm * 2 * math.pi / 60
        acc = 0.0
        for i in range(N):
            d2 = (S[(i + 1) % N] - 2 * S[i] + S[(i - 1) % N]) / (DEG * DEG)
            acc = max(acc, abs(d2))
        return dict(ok=True, S=S, D=D, sl=sl, top=top, bot=bot, fin=fin, margin=margin, at=at, waste=waste, pre=pre, neg=neg,
                    entry=sl[fin], c=c, Smax=S[bot], acc=acc * w * w / 1000, mu=[min(mu), max(mu)], E=E, A=list(A))

    # ---------- 第 5 章 旋梭定时、针杆高度与梭尖间隙 ----------
    @staticmethod
    def f_loop(h):
        h = max(h, 0)
        return (h / HOOK_H0) ** 2 * math.exp(2 * (1 - h / HOOK_H0))

    @staticmethod
    def y_top(h):
        return 0.5 + 0.9 * max(h, 0)

    def hook_geom(self, psi=0, dz=0, g=0.08, d=0.9, fab="woven"):
        fc = self.PHC0 + psi / 2
        h = self.rise(fc)
        D = 1.0 - dz - (h - 2.0)
        gg = g - (d - HOOK_DREF) / 2
        W = HOOK_FAB[fab]["W"]
        yt = self.y_top(h)
        y = D + 0.15
        wAt = W * self.f_loop(h) * math.sin(math.pi * y / yt) if 0 < y < yt else 0
        if gg <= 0.02:
            res = "hit"
        elif D < 0.2:
            res = "cut"
        else:
            res = "ok" if wAt - (gg + HOOK_TB) >= 0 else "skip"
        return dict(fc=fc, h=h, D=D, g=gg, W=W, yt=yt, wAt=wAt, margin=wAt - (gg + HOOK_TB), res=res)

    def hook_stitch(self, g0, fab, dz, gauss):
        sd = HOOK_FAB[fab]["sd"]
        dh, dg, kW = 0.08 * gauss(), 0.015 * gauss(), 1 + sd * gauss()
        h = g0["h"] + dh
        D = 1.0 - dz - (h - 2.0)
        g = g0["g"] + dg
        yt = self.y_top(h)
        y = D + 0.15
        w = g0["W"] * kW * self.f_loop(h) * math.sin(math.pi * y / yt) if 0 < y < yt else 0
        return "hit" if g <= 0.02 else "cut" if D < 0.2 else ("ok" if w - (g + HOOK_TB) >= 0 else "skip")

    # ---------- 第 6 章 送布牙轨迹与送布时序 ----------
    def feed_model(self, fab="cotton", mode="drop", s=3, dT=0, dP=0, h=0.8, P=1.0):
        f = FEED_FAB[fab]
        A = FEED_A
        half = math.acos(_clamp((A - h) / A, -1, 1)) / DEG
        if mode == "drop":
            phL, phF = self.PHL0 + dT, self.FE + dT + dP
        else:
            phL, phF = 180.0, 180 + half
        rise, drop, S = phL - half, phL + half, s / self.EFF0

        def X(p):
            return (S / 2) * math.cos((p - phF) * DEG)

        def Y(p):
            return (h - A) + A * math.cos((p - phL) * DEG)
        ain = self.cross(f["t"])
        aout = 360 - ain
        drag = back = 0.0
        n = 720
        sg = 1 if s >= 0 else -1
        for i in range(n):
            p0 = rise + (drop - rise) * i / n
            p1 = rise + (drop - rise) * (i + 1) / n
            dx = X(p1) - X(p0)
            pm = _mod((p0 + p1) / 2)
            if mode == "drop" and ain < pm < aout:
                drag += abs(dx)
            if dx * sg < 0:
                back += abs(dx)
        net = X(drop) - X(rise)
        mud = f["mud"] * min(1, h / f["hreq"])
        Pmin = f["F0"] / mud if mode == "compound" else f["F0"] / max(mud - f["muf"], 1e-6)
        eps = min(1, P / Pmin)
        ply = f["muf"] * P / f["K"] * MODEF[mode] * 400
        marks = []
        if h > f["hmax"] + 1e-9:
            marks.append("dog")
        if P > f["Pmark"] + 1e-9:
            marks.append("foot")
        return dict(half=half, phL=phL, phF=phF, rise=_mod(rise), drop=_mod(drop), riseRaw=rise, dropRaw=drop, S=S, X=X, Y=Y,
                    ain=ain, aout=aout, drag=drag, back=back, net=net, act=eps * net, eps=eps, Pmin=Pmin, ply=ply, marks=marks,
                    eyeAtDrop=self.tip(_mod(drop)) + self.EYE, t=f["t"])

    # ---------- 第 7 章 线张力 ----------
    @staticmethod
    def tension(fab="cotton", th="t24", Td=100, Tb=40, s=3, n=5000):
        f, T = TEN_FAB[fab], THREAD[th]
        Tn = KN * Td
        r = Tn / Tb
        z = 0.5 + 0.5 * _clamp(math.log(r) / math.log(f["B"]), -1, 1)
        EA = T["F"] / T["el"]
        lam = (s + f["t"]) / s
        shrink = 100 * (Tn + Tb) / 2 / EA * lam
        pucker = max(0, shrink - f["pf"])
        peak = Td * GUIDE * (1 + 0.15 * (n / 5000) ** 2)
        sf = 0.5 * T["F"] / peak
        loose = min(Tn, Tb) < f["Tmin"]
        jam = ORDER.index(th) > ORDER.index(f["jam"])
        bal, brk, pk = 0.4 <= z <= 0.6, sf < 1.5, pucker > f["plim"]
        return dict(Tn=Tn, r=r, z=z, shrink=shrink, pucker=pucker, peak=peak, sf=sf, loose=loose, jam=jam, bal=bal, brk=brk, pk=pk,
                    good=bal and not loose and not brk and not pk and not jam, f=f)

    # ---------- 第 8 章 全机时序与整机惯性力 ----------
    def table(self):
        if self._table:
            return self._table
        R = self.takeup(u=0, t=1.5, s=3, phc=206, rpm=5000)
        r3 = lambda v: math.floor(v * 1000 + 0.5) / 1000   # 同 JS Math.round
        fin = 0
        while fin < 180 and self.xN(fin) < self.EYE_TDC - 1.5:
            fin += 1
        self._table = dict(S0=[r3(v) for v in R["S"]], top0=R["top"], FIN=fin, D={}, r3=r3)
        return self._table

    def _Dt(self, phc):
        T = self.table()
        if phc not in T["D"]:
            T["D"][phc] = [T["r3"](self.demand(i, 1.5, 3, phc)) for i in range(360)]
        return T["D"][phc]

    def timing_feed(self, dT):
        A6, H6 = FEED_A, FEED_H0
        HALF = math.acos((A6 - H6) / A6) / DEG
        EFF = (1 - math.cos(2 * HALF * DEG)) / 2
        S6 = 3 / EFF
        phL, phF = self.PHL0 + dT, self.FE + dT
        rise, drop = phL - HALF, phL + HALF
        X = lambda p: (S6 / 2) * math.cos((p - phF) * DEG)
        ain = self.cross(1.5)
        drag = 0.0
        n = 720
        for i in range(n):
            p0 = rise + (drop - rise) * i / n
            p1 = p0 + (drop - rise) / n
            pm = _mod((p0 + p1) / 2)
            if ain < pm < 360 - ain:
                drag += abs(X(p1) - X(p0))
        return dict(rise=_mod(rise), drop=_mod(drop), riseRaw=rise, dropRaw=drop, drag=drag, phL=phL, phF=phF, S6=S6, X=X,
                    Y=lambda p: (H6 - A6) + A6 * math.cos((p - phL) * DEG), ain=ain)

    def timing_core(self, dh=0, dt=0, dT=0):
        """六条判据的数值部分（实验 8-1）"""
        T = self.table()
        FIN = T["FIN"]
        phc = round(self.PHC0) + dh
        top = _mod(T["top0"] + dt)
        Dt = self._Dt(phc)
        S = lambda i: T["S0"][_mod(i - dt)]
        sl = [S(i) - (4.5 if i < top else Dt[i]) for i in range(360)]
        margin = min(sl[i % 360] for i in range(phc, phc + 136))
        pre = max(sl[i] for i in range(top, FIN + 1)) if FIN >= top else -1e9
        neg = max((-sl[i] for i in range(FIN, phc)), default=-1e9)
        rc = self.rise(self.PHC0 + dh)
        F = self.timing_feed(dT)
        ain = F["ain"]
        fr = (F["rise"] - (360 - ain) + 360) % 360
        ok = dict(rise=1.6 <= rc <= 2.5, margin=margin >= 1, pre=pre <= 10, neg=neg <= 1, drag=F["drag"] <= 0.05, feedrise=20 <= fr < 180)
        return dict(phc=phc, top=top, sl=sl, margin=margin, pre=pre, neg=neg, rc=rc, F=F, feedrise=fr, ok=ok)

    def link_com(self, ph):
        LK = self.LK0
        f = (ph + LK["d"]) * DEG
        P = [-LK["r"] * math.sin(f), -LK["r"] * math.cos(f)]
        Q = [LK["Qz"], LK["Qy"]]
        d = [Q[0] - P[0], Q[1] - P[1]]
        D = math.hypot(d[0], d[1])
        t = (LK["a"] ** 2 - LK["b"] ** 2 + D * D) / (2 * D)
        h = math.sqrt(max(0, LK["a"] ** 2 - t * t))
        m = [P[0] + t * d[0] / D, P[1] + t * d[1] / D]
        M = [m[0] - h * d[1] / D, m[1] + h * d[0] / D]
        u = [(M[0] - P[0]) / LK["a"], (M[1] - P[1]) / LK["a"]]
        al = LK["al"] * DEG
        v = [u[0] * math.cos(al) - u[1] * math.sin(al), u[0] * math.sin(al) + u[1] * math.cos(al)]
        E = [P[0] + LK["c"] * v[0], P[1] + LK["c"] * v[1]]
        return [(P[0] + 0.45 * (E[0] - P[0])) * 1e-3, (P[1] + 0.45 * (E[1] - P[1])) * 1e-3]

    def forces(self, n=5000, k=0.3, dt=0, dT=0, mo=0.06, mt=0.025, mf=0.05):
        """整机惯性力（作用在机壳上的合力，N），每 1° 一个"""
        w = 2 * math.pi * n / 60
        Fd = self.timing_feed(dT)
        S6 = Fd["S6"]
        out = []
        RN = self.RN
        for f in range(360):
            an = self.aN(f, w)
            ay = -an
            apin = [-w * w * RN * 1e-3 * math.sin(f * DEG), -w * w * RN * 1e-3 * math.cos(f * DEG)]
            g, d = f - dt, 0.5
            c0, c1, c2 = self.link_com(g - d), self.link_com(g), self.link_com(g + d)
            ddt = d * DEG / w
            atk = [(c2[0] - 2 * c1[0] + c0[0]) / ddt / ddt, (c2[1] - 2 * c1[1] + c0[1]) / ddt / ddt]
            afx = -(S6 / 2) * 1e-3 * w * w * math.cos((f - Fd["phF"]) * DEG)
            afy = -1.1e-3 * w * w * math.cos((f - Fd["phL"]) * DEG)
            mr = self.mr
            cw = mo + k * mr
            sx = mo * apin[0] + cw * (-apin[0]) + mt * atk[0] + mf * afx
            sy = mr * ay + mo * apin[1] + cw * (-apin[1]) + mt * atk[1] + mf * afy
            out.append([-sx, -sy])
        return out

    # ---------- 线环与供线（第 20 轮） ----------
    def supply(self, u=0, t=1.5, s=3, phc=206):
        phc = int(math.floor(phc + 0.5))
        key = (u, t, s, phc)
        if key in self._sup:
            return self._sup[key]
        R = self.takeup(u=u, t=t, s=s, phc=phc, rpm=5000)
        k = _clamp((3 - R["neg"]) / 2, 0, 1) if R["ok"] else 0
        nan = float("nan")
        r = dict(ok=R["ok"], neg=R["neg"] if R["ok"] else nan, margin=R["margin"] if R["ok"] else nan, pre=R["pre"] if R["ok"] else nan,
                 k=k, short=R["ok"] and R["margin"] < 0)
        self._sup[key] = r
        return r

    # ---------- 整机：一套调机参数 → 各机构判定 ----------
    def evaluate(self, cfg=None):
        c = dict(STD, **(cfg or {}))
        out = []

        def add(key, sev, part, lab, zh, en, czh, cen):
            out.append(dict(key=key, sev=sev, part=part, lab=lab, title=dict(zh=zh, en=en), cause=dict(zh=czh, en=cen)))
        g = self.hook_geom(psi=c["psi"], dz=c["dz"], g=c["g"], d=c["d"], fab="woven")
        sup = self.supply(u=c["u"], t=FT[c["fab"]], s=c["s"], phc=g["fc"])
        margin = g["wAt"] * sup["k"] - (g["g"] + HOOK_TB)
        res = g["res"]
        if res == "ok" and margin < 0:
            res = "skip"
        if res == "hit":
            add("hit", "bad", "hook", "5-1", "梭尖碰针", "Hook point hits the needle",
                f"梭尖与机针的间隙只有 {g['g']:.2f} mm：响声、针尖起毛刺、断针。换了粗针（Nm {round(c['d'] * 100)}）没有重调间隙最常见。",
                f"Hook-to-needle clearance only {g['g']:.2f} mm: noise, burred needle, broken needle. Most often a thicker needle (Nm {round(c['d'] * 100)}) without resetting the clearance.")
        elif res == "cut":
            add("cut", "bad", "hook", "5-1", "梭尖划线（劈线、断线）", "Hook point splits the thread",
                f"梭尖比针眼上沿只高 {g['D']:.2f} mm，从针眼附近划过：针杆太高，或钩线太晚。",
                f"The hook point passes only {g['D']:.2f} mm above the eye: needle bar too high, or catching too late.")
        elif res == "skip":
            if sup["k"] < 1 and g["margin"] >= 0:
                w = (f"挑线杆供线不够：针眼入布后欠线 {sup['neg']:.1f} mm，线环张不开。",
                     f"Take-up supply too short: {sup['neg']:.1f} mm short after the eye enters the fabric, so the loop cannot open.")
            elif g["h"] < 2:
                w = (f"钩线太早：梭尖到达时机针只回升了 {g['h']:.2f} mm，线环还没张开。",
                     f"Hook too early: the needle has risen only {g['h']:.2f} mm when the point arrives; the loop is not open yet.")
            elif g["h"] > 2.5:
                w = (f"钩线太晚：机针已回升 {g['h']:.2f} mm，线环已在收缩。",
                     f"Hook too late: the needle has risen {g['h']:.2f} mm; the loop is shrinking.")
            elif g["g"] > 0.1:
                w = (f"梭尖离机针太远（间隙 {g['g']:.2f} mm），从线环外面滑过。",
                     f"Hook point too far from the needle (clearance {g['g']:.2f} mm); it slides past outside the loop.")
            else:
                w = (f"梭尖高度不在线环里（梭尖高于针眼上沿 {g['D']:.2f} mm）：针杆高度不对。",
                     f"The hook point is not at the height of the loop ({g['D']:.2f} mm above the eye): needle-bar height is wrong.")
            add("skip", "bad", "hook", "4-1" if sup["k"] < 1 and g["margin"] >= 0 else "5-1", "跳针", "Skipped stitches", *w)
        if sup["ok"] and sup["margin"] < 0:
            add("short", "bad", "tklever", "4-1", "绕梭时线不够（断线）", "Thread too short round the bobbin case (breaks)",
                f"钩线到脱环之间，旋梭要的线比挑线杆放下的多 {-sup['margin']:.1f} mm：旋梭硬拉面线，容易断线、线迹不匀。",
                f"Between catch and release the hook needs {-sup['margin']:.1f} mm more thread than the take-up lever gives: it drags the upper thread, which breaks or tightens unevenly.")
        if sup["ok"] and sup["pre"] > c["stroke"]:
            add("slack", "warn", "tklever", "4-1", "针眼入布前面线松垮", "Upper thread slack before the eye enters",
                f"挑线杆放下的线多出挑线簧行程 {sup['pre'] - c['stroke']:.1f} mm，面线松垮，可能被机针刺穿或绕住。",
                f"The lever releases {sup['pre'] - c['stroke']:.1f} mm more than the check spring can hold: the thread goes slack and may be pierced or tangled.")
        E = self.tension(fab=c["fab"], th=c["th"], Td=c["Td"], Tb=c["Tb"], s=c["s"], n=c["n"])
        if E["jam"]:
            add("jam", "bad", "tension", "7-1", "线太粗：结构性起皱", "Thread too coarse: structural pucker",
                "这种布织得密，粗线和相应的粗针把纱线挤开、把布撑皱。换细一号的线和针。",
                "This fabric is tightly woven; the coarse thread and needle push the yarns apart. Use a finer thread and needle.")
        if E["brk"]:
            add("tbreak", "bad", "tension", "7-1", "张力太大：断线", "Tension too high: thread breaks",
                f"收紧时峰值张力 {E['peak']:.0f} cN，超过线的名义强力的三分之一。",
                f"Peak tension {E['peak']:.0f} cN exceeds a third of the thread strength.")
        if E["z"] > 0.6:
            add("bobup", "warn", "tension", "7-1", "底线被拉到正面", "Bobbin thread pulled to the top",
                "面线相对太紧或底线太松，交织点被拉向布面。", "Upper thread relatively too tight (or bobbin too loose): the interlock is pulled to the top.")
        elif E["z"] < 0.4:
            add("float", "warn", "tension", "7-1", "面线被拉到反面（浮线）", "Upper thread pulled to the back (loops underneath)",
                "底线相对太紧或面线太松，交织点被拉向布底。", "Bobbin thread relatively too tight (or upper too loose): the interlock is pulled to the underside.")
        if E["loose"]:
            add("loose", "warn", "tension", "7-1", "线迹太松", "Loose stitches",
                f"较小的张力只有 {min(E['Tn'], c['Tb']):.0f} cN，收不紧线迹。", f"The lower of the two tensions is only {min(E['Tn'], c['Tb']):.0f} cN: the stitch is not pulled in.")
        if E["pk"]:
            add("pucker", "bad", "tension", "7-1", "张力起皱", "Tension pucker",
                f"两根线的张力都偏高，缝线被拉长 {E['shrink']:.2f}%，缝好后回缩把布拉皱。",
                f"Both tensions too high: the thread is stretched {E['shrink']:.2f}% and shrinks back, puckering the seam.")
        F = self.feed_model(fab=c["fab"], mode=c["mode"], s=c["s"], dT=c["dT"], dP=c["dP"], h=c["h"], P=c["P"])
        if "dog" in F["marks"]:
            add("dogmark", "warn", "dog", "6-1", "牙痕", "Feed-dog marks", "牙太高，布上留下牙痕。", "Teeth too high: marks on the fabric.")
        if "foot" in F["marks"]:
            add("footmark", "warn", "presser", "6-1", "压痕", "Presser-foot marks", "压脚压力太大，布上留下压痕。", "Foot pressure too high: marks on the fabric.")
        if F["eps"] < 0.999:
            add("slip", "warn", "dog", "6-1", "打滑：针距变短", "Slipping: stitches too short",
                f"压脚压力低于不打滑所需的 {F['Pmin']:.2f}，布只走了牙行程的 {F['eps'] * 100:.0f}%。",
                f"Foot pressure below the {F['Pmin']:.2f} needed; the fabric moves only {F['eps'] * 100:.0f}% of the dog stroke.")
        if F["drag"] > 0.05:
            add("drag", "bad", "dog", "6-1", "机针在布中时布还在动（断针）", "Fabric moves while the needle is in it (needle breaks)",
                f"布在针里被推着走了 {F['drag']:.2f} mm：针被带弯，重则撞上旋梭而断针。送布太晚。",
                f"The fabric is pushed {F['drag']:.2f} mm with the needle in it: the needle bends and may hit the hook. Feed too late.")
        if F["back"] > 0.05:
            add("back", "warn", "dog", "6-1", "回拖", "Back-drag", f"牙把布往回带了 {F['back']:.2f} mm，针距不匀。",
                f"The dog drags the fabric back {F['back']:.2f} mm; uneven stitches.")
        if F["ply"] > 3:
            add("ply", "warn", "presser", "6-1", "上层布越缝越长：缝皱", "Upper ply creeps: seam pucker",
                f"缝 40 cm 上层多出 {F['ply']:.1f} mm，多出的上层布在线迹之间拱起。",
                f"Over 40 cm the upper ply ends {F['ply']:.1f} mm longer and bulges between the stitches.")
        fmax = max(math.hypot(x, y) for x, y in self.forces(n=c["n"], k=c["k"], dt=0, dT=c["dT"]))
        if fmax > 550:
            add("vib", "warn", "upper", "8-1", "振动大", "Strong vibration",
                f"整机惯性力最大 {fmax:.0f} N（{c['n']} r/min，平衡率 {c['k']}）：平衡块与转速不配。",
                f"Peak inertia force {fmax:.0f} N ({c['n']} r/min, balance ratio {c['k']}): counterweight and speed do not match.")
        return dict(cfg=c, faults=out, ok=not any(f["sev"] == "bad" for f in out), hook=g, catch=res, supply=sup, tension=E, feed=F, fmax=fmax)

    def trial(self, cfg=None, n=30, seed=7):
        """试缝 n 针：钩线带随机波动（同实验 5-1），其余机构的判定对每一针相同"""
        ev = self.evaluate(cfg)
        c = ev["cfg"]
        R = LCG(7 if seed is None else seed)
        res = []
        for _ in range(n or 30):
            r = self.hook_stitch(ev["hook"], "woven", c["dz"], R.gauss)
            if r == "ok" and ev["supply"]["k"] < 1 and R.rnd() > ev["supply"]["k"]:
                r = "skip"
            if r == "ok" and any(f["key"] in ("short", "tbreak") for f in ev["faults"]) and R.rnd() < 0.25:
                r = "break"
            res.append(r)
        return dict(ev=ev, res=res)
