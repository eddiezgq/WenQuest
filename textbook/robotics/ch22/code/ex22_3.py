"""22.3 节的计算：样条与过路径点。

上下料循环的前半段：TCP 从料架里的抓取点 R 竖直提升到 A，越过车床防护罩上方的路径点 M，到卡盘前的 B（示意值）。
四个位形 θ_R、θ_A、θ_M、θ_B 由逆解求出（同一支）。比较四种做法的总时间（限值同算例 22.1.1）：
(a) 在每个路径点停下：每段用五次多项式，各取最短时间（定理 22.1.3）；
(b) 经验速度（相邻两段平均斜率，变号取零）+ 三次埃尔米特，各段时长按 (a) 的比例，整体缩放到不超限的最短；
(c) 三次样条（两端速度为零，中间点速度、加速度连续），时长同样按比例整体缩放；用 scipy 的 CubicSpline 核对；
(d) 抛物线过渡的直线段：各段时长同 (c)，每个路径点的过渡时长取不超过加速度限值的最小值；
    过渡中点偏离路径点 Δv t_b/8（定理 22.3.2），用 TCP 的位置换算成毫米。
另外：(b) 在路径点处加速度的跳变；(c) 第一段（提升）中 TCP 偏离竖直线的距离；时长取得不当（三段等长）时的过冲。
"""
import math

import numpy as np
from scipy.interpolate import CubicSpline

from _traj import (AMAX, VMAX, cell_joints, cubic_spline, heuristic_vel, hermite_segments, lspb_via, s_quintic, segs_eval, t_min_poly,
                   tcp_fk, ur_labels, via_joints, JMAX, LIFT, P_PICK)
from bookout import out, tex

deg = np.degrees
thR, thA, thB, thC = cell_joints()
thM = via_joints()
Q = np.array([thR, thA, thM, thB])
assert all(ur_labels(q) == ("A", "up", False) for q in Q)
names = ["R", "A", "M", "B"]

# ---------------------------------------------------------------- (a) 每个路径点都停
T_seg = np.array([t_min_poly(Q[k + 1] - Q[k], VMAX, AMAX, "quintic", JMAX)[0] for k in range(3)])
T_stop = float(T_seg.sum())


def peaks(segs, n=4001):
    Ttot = sum(T for T, _ in segs)
    t = np.linspace(0, Ttot, n)
    V = segs_eval(segs, t, 1)
    A = segs_eval(segs, t, 2)
    return np.max(np.abs(V) / VMAX), np.max(np.abs(A) / AMAX)


def scaled(make, h0):
    """时长按 h0 的比例整体缩放（λ h0），二分法求不超限的最小 λ（速度、加速度都按 1/λ、1/λ² 变化，单调）。"""
    lo, hi = 0.05, 5.0
    for _ in range(80):
        lam = 0.5 * (lo + hi)
        rv, ra = peaks(make(lam * h0))
        if rv <= 1 and ra <= 1:
            hi = lam
        else:
            lo = lam
    return hi, make(hi * h0)


def make_spline(h):
    ts = np.concatenate([[0.0], np.cumsum(h)])
    return cubic_spline(ts, Q)


def make_heur(h):
    ts = np.concatenate([[0.0], np.cumsum(h)])
    return hermite_segments(ts, Q, heuristic_vel(ts, Q))


lam_s, S = scaled(make_spline, T_seg)
lam_h, H = scaled(make_heur, T_seg)
T_spl = lam_s * T_stop
T_heu = lam_h * T_stop
# 样条：中间路径点处速度、加速度连续；与 scipy 的夹持样条一致
ts = np.concatenate([[0.0], np.cumsum(lam_s * T_seg)])
cs = CubicSpline(ts, Q, bc_type=((1, np.zeros(6)), (1, np.zeros(6))))
tt = np.linspace(0, ts[-1], 3001)
assert np.allclose(segs_eval(S, tt), cs(tt), atol=1e-10) and np.allclose(segs_eval(S, tt, 2), cs(tt, 2), atol=1e-8)
for k in (1, 2):
    for r in (1, 2):
        left = segs_eval(S, ts[k] - 1e-9, r)[0]
        right = segs_eval(S, ts[k] + 1e-9, r)[0]
        assert np.max(np.abs(left - right)) < 1e-5
# 经验速度：路径点处加速度跳变
th_ = np.concatenate([[0.0], np.cumsum(lam_h * T_seg)])
jump = []
for k in (1, 2):
    l = segs_eval(H, th_[k] - 1e-9, 2)[0]
    r = segs_eval(H, th_[k] + 1e-9, 2)[0]
    jump.append(np.abs(l - r))
jump = np.array(jump)
kj = np.unravel_index(np.argmax(jump), jump.shape)
assert jump.max() > 1.0
# 样条第一段（提升）：TCP 偏离抓取点上方竖直线的水平距离
t1 = np.linspace(0, ts[1], 801)
P1 = np.array([tcp_fk(q)[:3, 3] for q in segs_eval(S, t1)])
dev_lift = float(np.max(np.hypot(P1[:, 0] - P_PICK[0], P1[:, 1] - P_PICK[1])))
z_at_dev = float(P1[np.argmax(np.hypot(P1[:, 0] - P_PICK[0], P1[:, 1] - P_PICK[1])), 2])
dip1 = float(deg(thR[0] - segs_eval(S, t1)[:, 0].min()))
assert 0.1 < dip1 < 5
# 时长取得不当：三段等长（总时间与 (c) 相同），关节 6 的过冲
heq = np.full(3, T_spl / 3)
Seq = make_spline(heq)
teq = np.linspace(0, T_spl, 4001)
q6 = deg(segs_eval(Seq, teq)[:, 5])
q6s = deg(segs_eval(S, teq)[:, 5])
rv_eq, ra_eq = peaks(Seq)
lo6, hi6 = deg(Q[:, 5]).min(), deg(Q[:, 5]).max()

# ---------------------------------------------------------------- (d) 抛物线过渡
h = lam_s * T_seg
tsd = np.concatenate([[0.0], np.cumsum(h)])
vseg = np.diff(Q, axis=0) / h[:, None]
assert np.all(np.abs(vseg) <= VMAX[None, :])
vv = np.vstack([np.zeros(6), vseg, np.zeros(6)])
tb = np.array([np.max(np.abs(vv[k + 1] - vv[k]) / AMAX) for k in range(4)])
assert np.all(tb[1:3] < np.minimum(h[:2], h[1:]))                 # 相邻过渡不重叠
f = lspb_via(tsd, Q, tb)
T_lspb = float(tsd[-1] + (tb[0] + tb[3]) / 2)
dev_joint = []
dev_tcp = []
for k in (1, 2):
    qk = f(tsd[k])
    d = qk - Q[k]
    assert np.allclose(d, (vv[k + 1] - vv[k]) * tb[k] / 8, atol=1e-12)      # 定理 22.3.2
    dev_joint.append(deg(np.abs(d)).max())
    dev_tcp.append(np.linalg.norm(tcp_fk(qk)[:3, 3] - tcp_fk(Q[k])[:3, 3]) * 1000)
# 过渡中加速度不超限、过渡的两端与直线段衔接（速度连续）
for k in (1, 2):
    a_bl = (vv[k + 1] - vv[k]) / tb[k]
    assert np.all(np.abs(a_bl) <= AMAX + 1e-9)
    assert np.allclose(f(tsd[k] - tb[k] / 2 - 1e-9, 1), vv[k], atol=1e-6) and np.allclose(f(tsd[k] + tb[k] / 2 + 1e-9, 1), vv[k + 1], atol=1e-6)

out(thM=tex(deg(thM).reshape(1, -1), 2), thR=tex(deg(thR).reshape(1, -1), 2),
    T1=T_seg[0], T2=T_seg[1], T3=T_seg[2], T_stop=T_stop, lam_s=lam_s, lam_h=lam_h, T_spl=T_spl, T_heu=T_heu,
    save_spl=100 * (1 - T_spl / T_stop), h1=h[0], h2=h[1], h3=h[2],
    jump_max=jump.max(), jump_at=names[1 + kj[0]], jump_joint=int(kj[1]) + 1,
    dip1=dip1, tb_all=[float(x) for x in tb], hs=[float(x) for x in h], dev_lift_mm=dev_lift * 1000, z_dev=z_at_dev,
    rise_dev_mm=(z_at_dev - P_PICK[2]) * 1000, rise_frac=100 * (z_at_dev - P_PICK[2]) / LIFT,
    q6_min=q6.min(), q6_max=q6.max(), q6s_min=q6s.min(), q6s_max=q6s.max(), lo6=lo6, hi6=hi6, rv_eq=rv_eq, ra_eq=ra_eq,
    tbA=tb[1], tbM=tb[2], tb0=tb[0], tb3=tb[3], T_lspb=T_lspb, devA_deg=dev_joint[0], devM_deg=dev_joint[1],
    devA_mm=dev_tcp[0], devM_mm=dev_tcp[1])
