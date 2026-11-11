"""WQ-LS 的动力学（第 138 轮 G2）：一转之内各运动构件的惯性、缝纫阻力 → 主轴驱动力矩、上轴受力、整机振动力。

方法：平面机构，主轴匀速 ω。每个构件的质心位置和转角是主轴转角 φ 的函数（几何由 sewcore 给出），对 φ 数值求导，
  速度 = x'·ω，加速度 = x''·ω²。驱动力矩按虚功率：T = Σ (m·x'·x'' + I·θ'·θ'')·ω² + Σ m·g·y' + Σ F_阻·|x'|。
  上轴受力：针杆—连杆、挑线杆两组用牛顿—欧拉方程解出销力（连杆、挑线杆有质量；摇杆按二力杆）。
质量和转动惯量在 G4 有实体零件后用 FreeCAD 算出的值替换（表 MASS 每一项注明来历）。
单位：长度 m、力 N、力矩 N·m（接口处的 mm 都已换算）。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "services" / "gateway"), str(Path(__file__).parent)]
from app.sewcore import design as D  # noqa: E402
from app.sewcore.kit import AC, B_GUIDE  # noqa: E402

import spec as S  # noqa: E402

G = 9.81
_TKJ = ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "挑线机构.json"
TK_LK = __import__("json").loads(_TKJ.read_text())["lk"] if _TKJ.exists() else None
DEG = math.pi / 180

# 质量与转动惯量（估计值，G4 用实体零件替换）。来历：
#   针杆组件 0.12 kg = 设计软件 mr（针杆、针夹、机针、线钩），其中连杆单列，所以针杆本身取 0.09
#   连杆：钢锻件 l = 55，大头套曲柄销；0.040 kg，质心距曲柄销 0.38 l，I_G = 1.3e-5（细杆 m l²/12 = 1.0e-5，加两端头）
#   曲柄销当量 0.06 kg（设计软件 mo）；挑线杆 0.025 kg（设计软件 mt），质心在 P→线眼 0.45 处（设计软件 link_com），
#   I_G = m c²/12；摇杆 8 g 按二力杆不计惯性；送布当量 0.05 kg（设计软件 mf，送布牙、牙架、摆轴折算）
MASS = dict(m_bar=0.09, m_rod=0.040, g_rod=0.38, I_rod=1.3e-5, m_pin=0.06, m_tk=0.025, g_tk=0.45, m_feed=0.05)

# G4.1 起：有了 FreeCAD 实体零件，就用实体算出的质量替换上面的估计（docs/设计/WQ-LS/G4/零件质量.json，由 g4_parts.py 写）
_PM = ROOT / "docs" / "设计" / "WQ-LS" / "G4" / "零件质量.json"
if _PM.exists():
    MASS.update(__import__("json").loads(_PM.read_text())["dyn_mass"])

# 缝纫阻力（示例估计；文献里机针穿刺力为几牛量级，G2 做 0.5–2 倍的敏感性分析）
RESIST = dict(F_pen=4.0,        # 针下行穿布时的穿刺力 N（Nm 90、棉布两层）
              F_out=1.5,        # 针上行出布时的摩擦力 N
              P_foot=50.0,      # 压脚压力 N
              mu_foot=0.25,     # 布与压脚的摩擦系数（设计软件 cotton.muf）
              T_hook=0.02,      # 旋梭摩擦力矩（旋梭轴上）N·m
              T_brg=0.05)       # 轴承、油封、油泵、同步带损耗合计（主轴上）N·m


def omega(n):
    return n * 2 * math.pi / 60


class Machine:
    def __init__(self, p=None, mass=None, resist=None, k=None, textbook_takeup=False):
        self.p = D.clean({**S.SEW, **(p or {})})
        self.M = D.mech_of(self.p)
        if TK_LK and textbook_takeup is False:          # G4.1 起：挑线杆与连杆共用曲柄销（g4_takeup.py 综合的四连杆）
            from g4_takeup import Mech2
            self.M = Mech2(r=self.p["r"], l=self.p["l"], mr=self.p["mr"], lk=TK_LK)
        self.ms = {**MASS, **(mass or {})}
        self.rs = {**RESIST, **(resist or {})}
        self.k = self.p["k"] if k is None else k
        self.r = self.p["r"] / 1000
        self.l = self.p["l"] / 1000
        r_ = self.analyze_once()
        self.fc, self.takeup = r_

    def analyze_once(self):
        res = D.analyze(self.p, trial=False)
        tk = self.M.takeup(u=self.p["u"], t=1.5, s=self.p["s"], phc=round(res["key"]["fc"]), rpm=self.p["n"], lk=self.M.LK0)
        return res["key"]["fc"], tk

    # ---------------- 几何（m），原点在上轴中心，u 水平、v 铅垂向上
    def needle(self, phi):
        q = phi * DEG
        C = np.array([self.r * math.sin(q), self.r * math.cos(q)])
        Bv = C[1] - math.sqrt(self.l ** 2 - C[0] ** 2)
        B = np.array([0.0, Bv])
        Gr = C + self.ms["g_rod"] * (B - C)
        th = math.atan2(B[1] - C[1], B[0] - C[0])
        return C, B, Gr, th

    def tk(self, phi):
        lp = self.M.link_pose(phi % 360, self.M.LK0)
        P, M_, E, Q = (np.array(lp[k]) / 1000 for k in ("P", "M", "E", "Q"))
        Gt = P + self.ms["g_tk"] * (E - P)
        th = math.atan2(M_[1] - P[1], M_[0] - P[0])
        return P, M_, E, Q, Gt, th

    def feed(self, phi):
        F = self._F
        return np.array([F["X"](phi), F["Y"](phi)]) / 1000

    @property
    def _F(self):
        p = self.p
        if not hasattr(self, "_fm"):
            self._fm = self.M.feed_model(fab=p["fab"], mode=p["mode"], s=p["s"], dT=p["dT"], dP=p["dP"], h=p["h"], P=p["P"])
        return self._fm

    # ---------------- 一转
    def run(self, n=None, N=720):
        n = n or self.p["n"]
        w = omega(n)
        h = 360.0 / N
        phi = np.arange(N) * h
        ms, rs = self.ms, self.rs

        def deriv(fun, ang=False):
            x0 = np.array([fun(f) for f in phi])
            xp = np.array([fun(f + h) for f in phi])
            xm = np.array([fun(f - h) for f in phi])
            dp, dm = xp - x0, x0 - xm
            if ang:                                         # 角度：差值折回 (−π, π]，避免 atan2 跳变
                dp, dm = (dp + math.pi) % (2 * math.pi) - math.pi, (dm + math.pi) % (2 * math.pi) - math.pi
            d1 = (dp + dm) / (2 * h * DEG)
            d2 = (dp - dm) / (h * DEG) ** 2
            return x0, d1, d2

        nb = deriv(lambda f: self.needle(f)[1])            # 针杆销 B
        rod = deriv(lambda f: self.needle(f)[2])           # 连杆质心
        rth = deriv(lambda f: np.array([self.needle(f)[3]]), True)
        tkg = deriv(lambda f: self.tk(f)[4])
        tth = deriv(lambda f: np.array([self.tk(f)[5]]), True)
        fd = deriv(self.feed)
        tipz = np.array([self.M.tip(f % 360) for f in phi]) / 1000

        a = lambda d: d[2] * w * w  # noqa: E731
        v = lambda d: d[1] * w      # noqa: E731

        # 惯性 + 重力力矩（虚功率 / ω）
        T_bar = ms["m_bar"] * np.sum(nb[1] * nb[2], axis=1) * w * w
        T_rod = (ms["m_rod"] * np.sum(rod[1] * rod[2], axis=1) + ms["I_rod"] * rth[1][:, 0] * rth[2][:, 0]) * w * w
        I_tk = ms["m_tk"] * (self.M.LK0["c"] / 1000) ** 2 / 12
        T_tk = (ms["m_tk"] * np.sum(tkg[1] * tkg[2], axis=1) + I_tk * tth[1][:, 0] * tth[2][:, 0]) * w * w
        T_fd = ms["m_feed"] * np.sum(fd[1] * fd[2], axis=1) * w * w
        T_grav = G * (ms["m_bar"] * nb[1][:, 1] + ms["m_rod"] * rod[1][:, 1] + ms["m_tk"] * tkg[1][:, 1])

        # 缝纫阻力
        t_fab = 1.5e-3
        in_fab = tipz < t_fab
        down = nb[1][:, 1] < 0
        F_needle = np.where(in_fab & down, rs["F_pen"], np.where(in_fab & ~down, rs["F_out"], 0.0))
        T_needle = F_needle * np.abs(nb[1][:, 1])
        # 挑线：挑线杆收线（供线量减小）时，线张力从夹线器张力升到收紧峰值
        TK = self.takeup
        Sarr = np.array(TK["S"]) / 1000
        dS = np.gradient(np.interp(phi, np.arange(360), Sarr, period=360), h * DEG)
        Td, Tpk = self.p["Td"] / 100, 1.40
        top = TK["top"]
        dist = ((top - phi) % 360)                         # 离挑线杆最高点还差多少度
        T_thr = np.where(dS < 0, Td + (Tpk - Td) * np.clip(1 - dist / 60, 0, 1), 0.0)
        T_thread = T_thr * np.clip(-dS, 0, None)
        # 送布：牙在针板上时推布，压脚摩擦阻碍；牙顶起压脚（弹簧，力矩有正有负）
        above = fd[0][:, 1] > 0
        T_feed = np.where(above, rs["mu_foot"] * rs["P_foot"] * np.abs(fd[1][:, 0]) + rs["P_foot"] * fd[1][:, 1], 0.0)
        T_fric = rs["T_brg"] + 2 * rs["T_hook"] + 0 * phi
        T_sew = T_needle + T_thread + T_feed + T_fric
        T = T_bar + T_rod + T_tk + T_fd + T_grav + T_sew

        # ---------------- 针杆—连杆销力（牛顿—欧拉）
        F_crank = np.zeros((N, 2))
        N_guide = np.zeros(N)
        for i in range(N):
            C, B, Gr, th = self.needle(phi[i])
            ab = a(nb)[i]
            # 布对针的阻力与速度方向相反：针下行时向上
            ag = a(rod)[i]
            alpha = rth[2][i, 0] * w * w
            # 未知：A=(Au, Av)（曲柄销对连杆），Bu（针杆对连杆的水平力）；针杆对连杆的铅垂力 = -（连杆对针杆的铅垂力）
            # 连杆对针杆：(-Bu_r, -Bv_r)；针杆：-Bv_r - m g + R = m a  →  Bv_r = -(m a + m g - R)
            R = F_needle[i] if nb[1][i, 1] < 0 else -F_needle[i]
            Bv_r = -(ms["m_bar"] * ab[1] + ms["m_bar"] * G - R)
            rC, rB = C - Gr, B - Gr
            # Au + Bu = m ag_u ; Av + Bv_r - m g = m ag_v ; rC×A + rB×B = I α
            Amat = np.array([[1, 0, 1], [0, 1, 0], [-rC[1], rC[0], -rB[1]]])
            bvec = np.array([ms["m_rod"] * ag[0], ms["m_rod"] * ag[1] + ms["m_rod"] * G - Bv_r,
                             ms["I_rod"] * alpha - rB[0] * Bv_r])
            Au, Av, Bu = np.linalg.solve(Amat, bvec)
            F_crank[i] = [-Au, -Av]                         # 连杆对曲柄销（即对上轴）
            N_guide[i] = Bu
        # 曲柄销、平衡块离心力（随轴转动）
        m_recip = ms["m_bar"] + ms["m_rod"] * ms["g_rod"]
        m_rot = ms["m_pin"] + ms["m_rod"] * (1 - ms["g_rod"])
        cw = m_rot + self.k * m_recip                      # 平衡块（折算到曲柄半径）
        q = phi * DEG
        er = np.stack([np.sin(q), np.cos(q)], axis=1)       # 曲柄方向
        F_cent = (ms["m_pin"] - cw) * self.r * w * w * er   # 曲柄销当量与平衡块的离心力合力（作用在轴上）
        F_crank_total = F_crank + F_cent

        # ---------------- 挑线杆：P 处销力（摇杆二力杆）
        F_tk = np.zeros((N, 2))
        for i in range(N):
            P, M_, E, Q, Gt, th = self.tk(phi[i])
            ag = a(tkg)[i]
            alpha = tth[2][i, 0] * w * w
            uMQ = (Q - M_) / np.linalg.norm(Q - M_)
            A_ = np.array(AC) / 1000
            B_ = np.array(B_GUIDE) / 1000
            Fe = T_thr[i] * ((A_ - E) / np.linalg.norm(A_ - E) + (B_ - E) / np.linalg.norm(B_ - E))
            rP, rM, rE = P - Gt, M_ - Gt, E - Gt
            cr = lambda r_, f_: r_[0] * f_[1] - r_[1] * f_[0]  # noqa: E731
            Amat = np.array([[1, 0, uMQ[0]], [0, 1, uMQ[1]], [-rP[1], rP[0], cr(rM, uMQ)]])
            bvec = np.array([ms["m_tk"] * ag[0] - Fe[0], ms["m_tk"] * ag[1] + ms["m_tk"] * G - Fe[1],
                             I_tk * alpha - cr(rE, Fe)])
            Pu, Pv, s_ = np.linalg.solve(Amat, bvec)
            F_tk[i] = [-Pu, -Pv]

        # ---------------- 送布偏心：送布连杆的力（铅垂，作用在上轴；折算比 1）
        F_fe = -(ms["m_feed"] * a(fd)[:, 0]) - np.where(above, rs["mu_foot"] * rs["P_foot"] * np.sign(fd[1][:, 0]), 0.0)

        # ---------------- 整机振动力（作用在机壳上的合力 = −Σ m a，加旋转不平衡）
        F_shake = -(ms["m_bar"] * a(nb) + ms["m_rod"] * a(rod) + ms["m_tk"] * a(tkg)) + F_cent
        F_shake[:, 0] += -ms["m_feed"] * a(fd)[:, 0]
        F_shake[:, 1] += -ms["m_feed"] * a(fd)[:, 1]

        return dict(phi=phi, n=n, w=w, T=T, T_bar=T_bar, T_rod=T_rod, T_tk=T_tk, T_fd=T_fd, T_grav=T_grav,
                    T_needle=T_needle, T_thread=T_thread, T_feed=T_feed, T_fric=T_fric, T_sew=T_sew,
                    F_crank=F_crank_total, F_rod=F_crank, F_cent=F_cent, F_tk=F_tk, F_fe=F_fe, N_guide=N_guide, F_shake=F_shake, cw=cw,
                    m_recip=m_recip, m_rot=m_rot)


def summary(R):
    T = R["T"]
    P = float(np.mean(T)) * R["w"]
    return dict(T_mean=float(np.mean(T)), T_rms=float(np.sqrt(np.mean(T ** 2))), T_max=float(T.max()), T_min=float(T.min()),
                T_sew_mean=float(np.mean(R["T_sew"])), P_mean=P,
                F_shake_max=float(np.max(np.hypot(*R["F_shake"].T))), F_crank_max=float(np.max(np.hypot(*R["F_crank"].T))))


def harmonics(x, orders=(1, 2, 3)):
    X = np.fft.rfft(x) / len(x) * 2
    return {k: float(abs(X[k])) for k in orders}
