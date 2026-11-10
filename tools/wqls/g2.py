"""第 138 轮 G2：WQ-LS 的动力学、上轴强度与疲劳、轴承寿命、临界转速、平衡、电机与飞轮，以及 MuJoCo 对照。

    python3 tools/wqls/g2.py        # 写到 docs/设计/WQ-LS/G2/（图 + 结果.json）
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "textbook" / "mechdesign" / "conventions"), str(ROOT / "factory" / "digital"),
                str(ROOT / "textbook" / "mechdesign" / "ch33" / "code")]
import dyn  # noqa: E402
import mdstd  # noqa: E402
import spec as S  # noqa: E402

OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G2"
plt.rcParams.update({"font.family": ["Noto Sans CJK JP", "DejaVu Sans"], "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "none"})
INK, MUTE, ACC, GRN, BLU, ORG = "#1d2733", "#7a8794", "#c8102e", "#2e9e6a", "#1f5fa8", "#d98a1f"
RES: dict = {}


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ================================================================ 1 驱动力矩
def torque():
    m = dyn.Machine()
    R = m.run()
    s = dyn.summary(R)
    deg = R["phi"]
    fig, (a, b) = plt.subplots(2, 1, figsize=(8.6, 6.6), sharex=True, gridspec_kw=dict(height_ratios=[1.5, 1], hspace=0.12))
    a.plot(deg, R["T"], color=INK, lw=1.8, label="主轴驱动力矩（合计）")
    a.plot(deg, R["T_bar"] + R["T_rod"], color=BLU, lw=1.1, label="刺布（针杆 + 连杆）惯性")
    a.plot(deg, R["T_tk"], color=GRN, lw=1.1, label="挑线杆惯性")
    a.axhline(s["T_mean"], color=ACC, lw=0.9, ls="--")
    a.text(358, s["T_mean"] + 0.15, f"平均 {s['T_mean']:.3f} N·m（{s['P_mean']:.0f} W）", color=ACC, ha="right", fontsize=8)
    a.set_ylabel("力矩 / N·m")
    a.set_title(f"一转之内主轴需要的力矩（{R['n']:.0f} r/min，主轴匀速）", loc="left", fontsize=10.5)
    a.legend(frameon=False, fontsize=8, ncol=3, loc="upper center")
    b.stackplot(deg, R["T_needle"], R["T_thread"], np.clip(R["T_feed"], 0, None), R["T_fric"],
                colors=["#9fb7d6", "#a8d5bd", "#e7c99a", "#d0d5da"],
                labels=["机针穿布", "挑线收紧", "送布（压脚摩擦）", "轴承、油封、旋梭摩擦"])
    b.set_ylabel("缝纫阻力矩 / N·m")
    b.set_xlabel("主轴转角 φ / °（0° = 针杆上止点）")
    b.set_xticks(range(0, 361, 30))
    b.set_xlim(0, 360)
    b.legend(frameon=False, fontsize=7.5, ncol=4, loc="upper center")
    for x in (a, b):
        x.grid(axis="x", color="#e6e9ec", lw=0.6)
    save(fig, "1_驱动力矩")
    # 敏感性：阻力 0.5、2 倍；转速
    sens = {}
    for f in (0.5, 1.0, 2.0):
        r_ = dyn.Machine(resist={k: v * f for k, v in dyn.RESIST.items()}).run()
        sens[f"阻力×{f:g}"] = dyn.summary(r_)
    speeds = {}
    for n in (3000, 4000, 5000, 5500):
        speeds[n] = dyn.summary(m.run(n=n))
    RES["torque"] = dict(s, sens=sens, speeds={str(k): v for k, v in speeds.items()},
                         parts={k: [float(np.mean(R[k])), float(R[k].min()), float(R[k].max())]
                                for k in ("T_bar", "T_rod", "T_tk", "T_fd", "T_grav", "T_needle", "T_thread", "T_feed", "T_fric")})
    return m, R


# ================================================================ 2 MuJoCo 对照（刺布机构）
def mujoco_dense(m, R):
    """mbd.simulate 的记录频率上限 200 Hz，看不清 83 Hz 的一转；直接用 MuJoCo 逐步算，每 0.5° 取一次，和公式逐点比。"""
    import mujoco
    ms = m.ms
    r, l, g = m.r, m.l, ms["g_rod"]
    w = dyn.omega(5000)
    xml = f"""<mujoco><option timestep="1e-6" gravity="0 0 -9.81" integrator="implicitfast"><flag contact="disable"/></option>
<worldbody>
<body name="crank"><joint name="crank" type="hinge" axis="0 1 0" damping="0"/>
 <inertial pos="0 0 0" mass="1e-4" diaginertia="1e-9 1e-9 1e-9"/>
 <body name="rod" pos="0 0 {r}"><joint name="rod" type="hinge" axis="0 1 0"/>
  <inertial pos="0 0 {-g * l}" mass="{ms['m_rod']}" diaginertia="{ms['I_rod']} {ms['I_rod']} 1e-9"/>
  <site name="rod_end" pos="0 0 {-l}"/></body></body>
<body name="bar" pos="0 0 {r - l}"><joint name="bar" type="slide" axis="0 0 1"/>
 <inertial pos="0 0 0" mass="{ms['m_bar']}" diaginertia="1e-7 1e-7 1e-7"/><site name="pin"/></body>
</worldbody>
<equality><connect site1="rod_end" site2="pin" solref="0.00002 1" solimp="0.999 0.9999 0.0001"/>
<joint name="drive" joint1="crank" polycoef="0 0 0 0 0" solref="0.00002 1" solimp="0.999 0.9999 0.0001"/></equality></mujoco>"""
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    jc = model.joint("crank").id
    eid = model.equality("drive").id
    # 初始：曲柄在上止点、匀速
    data.qvel[model.joint("crank").dofadr[0]] = w
    rod_dof = model.joint("rod").dofadr[0]
    data.qvel[rod_dof] = -w        # 上止点时连杆角速度 = −ω·r/l… 近似给定，前几步约束会收敛
    data.qvel[rod_dof] = -w * r / l
    mujoco.mj_forward(model, data)
    out_phi, out_tau = [], []
    steps = int(round(2 * 2 * math.pi / w / model.opt.timestep))     # 两转，取第二转
    for k in range(steps):
        t = data.time
        model.eq_data[eid][0] = w * (t + model.opt.timestep)
        mujoco.mj_step(model, data)
        if k > steps // 2 and k % 20 == 0:
            # 驱动约束的约束力就是驱动力矩（找对应的 efc 行）
            tau = None
            for i in range(data.nefc):
                if data.efc_type[i] == mujoco.mjtConstraint.mjCNSTR_EQUALITY and data.efc_id[i] == eid:
                    tau = data.efc_force[i]
            out_phi.append(math.degrees(data.qpos[model.joint("crank").qposadr[0]]) % 360)
            out_tau.append(tau)
    phi = np.array(out_phi)
    tau = np.array(out_tau, dtype=float)
    # 公式：针杆 + 连杆惯性 + 重力（与 MuJoCo 模型一致：曲柄质量可忽略）
    ref = R["T_bar"] + R["T_rod"] + 9.81 * 0     # 重力在下面单独加
    mm = dyn.Machine(resist={k: 0.0 for k in dyn.RESIST})
    R0 = mm.run()
    ref = R0["T_bar"] + R0["T_rod"] + R0["T_grav"] - 9.81 * mm.ms["m_tk"] * 0
    # 重力项里含挑线杆，MuJoCo 模型没有挑线杆：重新算只含针杆、连杆的重力
    ref_phi = R0["phi"]
    return phi, tau, ref_phi, ref


# ================================================================ 3 平衡率
def balance():
    ks = np.round(np.arange(0, 1.001, 0.05), 2)
    rows = []
    for k in ks:
        R = dyn.Machine(k=float(k)).run()
        F = R["F_shake"]
        hu, hv = dyn.harmonics(F[:, 0]), dyn.harmonics(F[:, 1])
        rows.append(dict(k=float(k), Fmax=float(np.max(np.hypot(*F.T))), u1=hu[1], v1=hv[1], u2=hu[2], v2=hv[2],
                         Fcrank=float(np.max(np.hypot(*R["F_crank"].T)))))
    best = min(rows, key=lambda r: r["Fmax"])
    fig, a = plt.subplots(figsize=(7.6, 4.2))
    a.plot(ks, [r["Fmax"] for r in rows], color=INK, lw=1.8, label="整机振动力最大值（合力）")
    a.plot(ks, [r["v1"] for r in rows], color=BLU, lw=1.1, label="铅垂一阶")
    a.plot(ks, [r["u1"] for r in rows], color=ORG, lw=1.1, label="水平一阶")
    a.plot(ks, [r["v2"] for r in rows], color=BLU, lw=1.0, ls="--", label="铅垂二阶（平衡块管不了）")
    a.axvline(best["k"], color=ACC, lw=0.9)
    a.text(best["k"] + 0.01, best["Fmax"] + 15, f"最小：平衡率 {best['k']:.2f}，{best['Fmax']:.0f} N", color=ACC, fontsize=8)
    a.axvline(0.3, color=MUTE, lw=0.6, ls=":")
    a.text(0.305, a.get_ylim()[1] * 0.92, "设计软件默认 0.30", color=MUTE, fontsize=7.5)
    a.set_xlabel("平衡率 k（平衡块抵消一阶往复惯性力的比例）")
    a.set_ylabel("力 / N（5000 r/min）")
    a.set_title("平衡率对整机振动力的影响", loc="left", fontsize=10.5)
    a.legend(frameon=False, fontsize=8)
    a.grid(color="#eef0f2", lw=0.6)
    save(fig, "3_平衡率")
    RES["balance"] = dict(rows=rows, best=best)
    return best["k"]


# ================================================================ 4 上轴：梁单元
def shaft_mesh(h=2.0, mid=False):
    pts = {S.UPPER_SEGS[0][0], S.UPPER_SEGS[-1][1], S.X_CRANK, S.X_TAKEUP, S.X_FEED_E, S.X_BELT, S.X_ROTOR, *S.X_BRG}
    if mid:
        pts.add(S.X_MID_BUSH)
    for x0, x1, *_ in S.UPPER_SEGS:
        pts |= {x0, x1}
    pts = sorted(pts)
    x = [pts[0]]
    for a_, b_ in zip(pts, pts[1:]):
        k = max(1, int(math.ceil((b_ - a_) / h)))
        x += list(np.linspace(a_, b_, k + 1)[1:])
    return np.array(x)


def dia(x):
    for x0, x1, d, _ in S.UPPER_SEGS:
        if x0 - 1e-9 <= x <= x1 + 1e-9:
            return d
    return S.UPPER_SEGS[-1][2]


def beam_KM(x, E=206000.0, rho=7.85e-9):
    n = len(x)
    K, Mm = np.zeros((2 * n, 2 * n)), np.zeros((2 * n, 2 * n))
    for e in range(n - 1):
        L = x[e + 1] - x[e]
        d = dia((x[e] + x[e + 1]) / 2)
        I, A = math.pi * d ** 4 / 64, math.pi * d ** 2 / 4
        k = E * I / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                        [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        mm = rho * A * L / 420 * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L * L, 13 * L, -3 * L * L],
                                           [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L * L, -22 * L, 4 * L * L]])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k
        Mm[np.ix_(idx, idx)] += mm
    return K, Mm


def supports(x, mid):
    xs = list(S.X_BRG) + ([S.X_MID_BUSH] if mid else [])
    return [2 * int(np.argmin(abs(x - xb))) for xb in xs], xs


def shaft(R, mid=False):
    """每个转角：两个平面的挠度、弯矩、支反力。载荷：曲柄（连杆力 + 离心力）、挑线曲柄、送布偏心、同步带、电机转子重量。"""
    x = shaft_mesh(mid=mid)
    K, _ = beam_KM(x)
    fixed, xs = supports(x, mid)
    free = [i for i in range(2 * len(x)) if i not in fixed]
    Kff = K[np.ix_(free, free)]
    nd = lambda xx: 2 * int(np.argmin(abs(x - xx)))  # noqa: E731
    N = len(R["phi"])
    reac = np.zeros((N, len(xs), 2))
    Mb = np.zeros((N, len(x), 2))
    defl_crank = np.zeros((N, 2))
    for i in range(N):
        for pl in (0, 1):                                  # 0：水平面（u），1：铅垂面（v）
            F = np.zeros(2 * len(x))
            F[nd(S.X_CRANK)] += R["F_crank"][i, pl]
            F[nd(S.X_TAKEUP)] += R["F_tk"][i, pl]
            if pl == 1:
                F[nd(S.X_FEED_E)] += R["F_fe"][i]
                F[nd(S.X_BELT)] += -S.BELT_N
                F[nd(S.X_ROTOR)] += -0.9 * 9.81
            u = np.zeros(2 * len(x))
            u[free] = np.linalg.solve(Kff, F[free])
            rr = K @ u - F
            reac[i, :, pl] = [rr[j] for j in fixed]
            # 弯矩：从左端积分（M(x) = Σ 外力 × 力臂，含支反力）
            loads = [(x[j // 2], F[j] + (rr[j] if j in fixed else 0)) for j in range(0, 2 * len(x), 2) if abs(F[j]) > 0 or j in fixed]
            Mx = np.zeros(len(x))
            for xp, P in loads:
                Mx += P * np.clip(x - xp, 0, None)
            Mb[i, :, pl] = Mx
            defl_crank[i, pl] = u[nd(S.X_CRANK)]
    return x, xs, reac, Mb, defl_crank


def torque_along(R, x):
    """截面传递的转矩（N·mm）：电机在右端，截面左边所有负载的力矩都要从它通过。"""
    T = np.zeros((len(R["phi"]), len(x)))
    T_left_crank = (R["T_bar"] + R["T_rod"] + R["T_needle"] + R["T_grav"] * 0) * 1000
    T_tk = (R["T_tk"] + R["T_thread"]) * 1000
    T_feed = (R["T_fd"] + R["T_feed"]) * 1000
    T_rest = (R["T"] * 1000) - T_left_crank - T_tk - T_feed           # 摩擦、重力等，算在带轮处（下轴经同步带）
    for j, xx in enumerate(x):
        T[:, j] = (T_left_crank * (xx > S.X_CRANK) + T_tk * (xx > S.X_TAKEUP) + T_feed * (xx > S.X_FEED_E)
                   + T_rest * (xx > S.X_BELT))
    return T


def fatigue(R, x, Mb, T):
    mat = mdstd.material("45-QT")
    out = {}
    import _fea
    for name, xsec, d, D_, r_ in (("截面 I：曲柄座 Ø10→前轴颈 Ø12", 11.0, 10.0, 12.0, 0.5),
                                  ("截面 II：前轴颈 Ø12→轴身 Ø16", 21.0, 12.0, 16.0, 0.5),
                                  ("截面 III：轴身 Ø16→后轴颈 Ø12", 330.0, 12.0, 16.0, 0.5),
                                  ("截面 IV：后轴颈 Ø12→带轮座 Ø10", 340.0, 10.0, 12.0, 0.5)):
        j = int(np.argmin(abs(x - xsec)))
        Mx, My = Mb[:, j, 0], Mb[:, j, 1]
        tau = T[:, j] / (math.pi * d ** 3 / 16)
        W = math.pi * d ** 3 / 32
        th = np.radians(R["phi"])
        kt = _fea.stepped_bar_kt(d, D_, r_, fine=4)
        alpha = (kt["alpha_sigma"], kt["alpha_tau"])
        q_s, q_t = mdstd.notch_sensitivity(r_, mat["sigma_b"]), mdstd.notch_sensitivity(r_, mat["sigma_b"], torsion=True)
        k_s, k_t = 1 + q_s * (alpha[0] - 1), 1 + q_t * (alpha[1] - 1)
        eps, beta = mdstd.size_factor(d), mdstd.surface_factor("ground", mat["sigma_b"])
        K_s, K_t = k_s / eps + 1 / beta - 1, k_t / eps + 1 / beta - 1
        ps, pt = mat["sigma_1"] / mat["sigma_b"], mat["tau_1"] / (mat["sigma_b"] / math.sqrt(3))
        ta, tm = (tau.max() - tau.min()) / 2, (tau.max() + tau.min()) / 2
        S_t = mat["tau_1"] / (K_t * ta + pt * abs(tm))
        worst = None
        for p0 in np.linspace(0, 2 * np.pi, 72, endpoint=False):
            psi = p0 - th
            sig = (Mx * np.cos(psi) + My * np.sin(psi)) / W
            sa, sm = (sig.max() - sig.min()) / 2, (sig.max() + sig.min()) / 2
            S_s = mat["sigma_1"] / (K_s * sa + ps * abs(sm))
            S_ = S_s * S_t / math.sqrt(S_s ** 2 + S_t ** 2)
            if worst is None or S_ < worst["S"]:
                worst = dict(S=S_, S_s=S_s, sa=float(sa), sm=float(sm))
        out[name] = dict(worst, S_t=float(S_t), ta=float(ta), tm=float(tm), alpha=alpha, K_s=K_s, K_t=K_t)
    return out


def critical(mid=False):
    x = shaft_mesh(mid=mid)
    K, Mm = beam_KM(x)
    masses = [(S.X_CRANK, 0.15), (S.X_TAKEUP, 0.05), (S.X_FEED_E, 0.08), (S.X_BELT, 0.06), (S.X_ROTOR, 0.45)]
    for xm, mk in masses:
        i = 2 * int(np.argmin(abs(x - xm)))
        Mm[i, i] += mk / 1000.0
    fixed, _ = supports(x, mid)
    free = [i for i in range(2 * len(x)) if i not in fixed]
    from scipy.linalg import eigh
    w2, V = eigh(K[np.ix_(free, free)], Mm[np.ix_(free, free)])
    w = np.sqrt(np.abs(w2[:2]))
    u = np.zeros(2 * len(x))
    u[free] = V[:, 0]
    y = u[0::2]
    return (w * 60 / (2 * math.pi)).tolist(), x, y / np.max(np.abs(y))


def bearing_life(reac, n):
    out = []
    for b in range(reac.shape[1]):
        F = np.hypot(reac[:, b, 0], reac[:, b, 1])
        Pm = float(np.mean(F ** 3) ** (1 / 3))
        L10 = (S.BRG_6201["C"] / max(Pm, 1e-9)) ** 3 * 1e6
        out.append(dict(P_mean=Pm, F_max=float(F.max()), L10h=float(L10 / (n * 60))))
    return out


def shaft_report(R):
    res = {}
    for mid in (False, True):
        x, xs, reac, Mb, dc = shaft(R, mid)
        T = torque_along(R, x)
        tag = "三支承" if mid else "两支承"
        nc, xm, mode = critical(mid)
        res[tag] = dict(supports=xs, bearings=bearing_life(reac[:, :2, :] if not mid else reac[:, [0, 1], :], R["n"]),
                        reac_max=[float(np.max(np.hypot(reac[:, b, 0], reac[:, b, 1]))) for b in range(reac.shape[1])],
                        defl_crank_um=float(np.max(np.hypot(*dc.T)) * 1000), nc=nc,
                        M_max=float(np.max(np.hypot(Mb[:, :, 0], Mb[:, :, 1]))))
        if not mid:
            res[tag]["fatigue"] = fatigue(R, x, Mb, T)
            two = (x, xs, reac, Mb, dc, T, xm, mode)
    # 图：轴的布置、弯矩包络、一阶振型
    x, xs, reac, Mb, dc, T, xm, mode = two
    fig, (a, b, c) = plt.subplots(3, 1, figsize=(8.8, 7.6), sharex=True, gridspec_kw=dict(height_ratios=[0.9, 1.2, 0.9], hspace=0.12))
    for x0, x1, d, nm in S.UPPER_SEGS:
        a.add_patch(plt.Rectangle((x0, -d / 2), x1 - x0, d, fc="#dfe5ea", ec=INK, lw=0.8))
    for xb in S.X_BRG:
        a.add_patch(plt.Rectangle((xb - 5, -16), 10, 32, fc="none", ec=INK, lw=0.8, hatch="////"))
    for xx, nm, tx, ty in ((S.X_CRANK, "针杆曲柄", -25, 28), (S.X_BRG[0], "6201", S.X_BRG[0] + 6, -30),
                           (S.X_TAKEUP, "挑线曲柄", 48, 28), (S.X_FEED_E, "送布偏心", S.X_FEED_E, 28),
                           (S.X_BRG[1], "6201", S.X_BRG[1] - 10, -30), (S.X_BELT, "同步带轮", S.X_BELT - 6, 28),
                           (S.X_ROTOR, "电机转子", S.X_ROTOR + 10, 28)):
        a.annotate(nm, (xx, 8 if ty > 0 else -16), (tx, ty), ha="center", fontsize=7.5,
                   arrowprops=dict(arrowstyle="-", color=MUTE, lw=0.6))
    a.add_patch(plt.Rectangle((S.X_MID_BUSH - 6, -14), 12, 28, fc="none", ec=MUTE, lw=0.8, ls="--"))
    a.text(S.X_MID_BUSH, -24, "可选中间轴套", ha="center", fontsize=7, color=MUTE)
    a.set_ylim(-36, 36)
    a.set_aspect("auto")
    a.axis("off")
    a.set_title("上轴 LS-101 B 版（单位 mm），两个 6201 支承", loc="left", fontsize=10.5)
    Mm_ = np.hypot(Mb[:, :, 0], Mb[:, :, 1]) / 1000
    b.fill_between(x, Mm_.min(axis=0), Mm_.max(axis=0), color=BLU, alpha=0.18, lw=0)
    b.plot(x, Mm_.max(axis=0), color=BLU, lw=1.2, label="一转之内的最大合成弯矩")
    b.set_ylabel("弯矩 / N·m")
    b.legend(frameon=False, fontsize=8)
    c.plot(xm, mode, color=ACC, lw=1.4)
    c.axhline(0, color=MUTE, lw=0.5)
    nc2 = res["两支承"]["nc"][0]
    c.set_ylabel("一阶振型")
    c.text(x[0] + 5, 0.7, f"一阶临界转速 {nc2:.0f} r/min（最高转速的 {nc2 / 5000:.1f} 倍）", fontsize=8, color=ACC)
    c.set_xlabel("沿轴的位置 x / mm（机针 x = 0）")
    save(fig, "4_上轴")
    RES["shaft"] = res
    return res


# ================================================================ 5 电机与飞轮
def motor(R):
    w = R["w"]
    # 转动惯量（kg·m²）：上轴、下轴、旋梭（转速 2 倍，折算 ×4）、带轮、平衡块；机构的平均当量惯量
    J_shaft = 0.5 * (7850 * math.pi * 0.008 ** 2 * 0.31) * 0.008 ** 2
    J_lower = 1.0e-5
    J_hook = 4 * 1.3e-5
    J_misc = 2.0e-5
    m = dyn.Machine()
    # 机构的当量惯量 J_eq = 2·动能 / ω²
    phi = R["phi"]
    h = 0.5
    Jeq = []
    for f in phi[::4]:
        def pos(ff):
            C, B, Gr, th = m.needle(ff)
            P, M_, E, Q, Gt, tt = m.tk(ff)
            return np.concatenate([B, Gr, [th], Gt, [tt]])
        d = (pos(f + h) - pos(f - h)) / (2 * h * dyn.DEG)
        ms = m.ms
        I_tk = ms["m_tk"] * (m.M.LK0["c"] / 1000) ** 2 / 12
        Jeq.append(ms["m_bar"] * d[1] ** 2 + ms["m_rod"] * (d[2] ** 2 + d[3] ** 2) + ms["I_rod"] * d[4] ** 2
                   + ms["m_tk"] * (d[5] ** 2 + d[6] ** 2) + I_tk * d[7] ** 2)
    J_mech = float(np.mean(Jeq))
    J_load = J_shaft + J_lower + J_hook + J_misc + J_mech
    # 两种做法：(a) 速度环很硬，电机补齐一转里的全部力矩起伏；(b) 速度环带宽低于两倍转频，起伏由惯量吸收
    T = R["T"]
    dt = (2 * math.pi / 720) / w
    rows = []
    for J_rotor in (1.0e-4, 2.0e-4, 4.0e-4, 8.0e-4):
        J = J_load + J_rotor
        dT = T - T.mean()
        domega = np.cumsum(dT) * dt / J
        ripple = float((domega.max() - domega.min()) / w * 100)
        t_acc = 0.10                                           # 0 → 5000 r/min 的目标时间
        T_acc = J * w / t_acc
        rows.append(dict(J_rotor=J_rotor, J_total=J, ripple_pct=ripple, T_acc=T_acc,
                         T_peak_a=float(T.max() + T_acc), T_rms_a=float(np.sqrt(np.mean(T ** 2))),
                         T_peak_b=float(T.mean() + T_acc), T_rms_b=float(abs(T.mean()))))
    RES["motor"] = dict(J_load=J_load, J_mech=J_mech, rows=rows, P_sew=float(T.mean() * w))
    fig, a = plt.subplots(figsize=(7.4, 3.8))
    for row, col in zip(rows, (MUTE, BLU, GRN, ORG)):
        J = row["J_total"]
        dT = T - T.mean()
        domega = np.cumsum(dT) * dt / J
        rpm = (w + domega - domega.mean()) * 60 / (2 * math.pi)
        a.plot(phi, rpm, color=col, lw=1.2, label=f"转子惯量 {row['J_rotor'] * 1e4:.0f}×10⁻⁴ kg·m²：波动 ±{row['ripple_pct'] / 2:.1f}%")
    a.set_xlabel("主轴转角 φ / °")
    a.set_ylabel("转速 / (r/min)")
    a.set_title("电机只给平均力矩、一转里的起伏全由惯量吸收时的转速波动（5000 r/min）", loc="left", fontsize=10)
    a.legend(frameon=False, fontsize=7.5)
    a.set_xticks(range(0, 361, 60))
    a.grid(color="#eef0f2", lw=0.6)
    save(fig, "5_转速波动与转子惯量")


def main():
    m, R = torque()
    k_best = balance()
    try:
        phi, tau, rphi, ref = mujoco_dense(m, R)
        fig, a = plt.subplots(figsize=(7.4, 3.6))
        a.plot(rphi, ref, color=INK, lw=1.6, label="本计算（虚功率，公式）")
        order = np.argsort(phi)
        sgn = 1.0 if np.mean(np.abs(tau - np.interp(phi, rphi, ref, period=360))) < np.mean(np.abs(-tau - np.interp(phi, rphi, ref, period=360))) else -1.0
        a.plot(phi[order], sgn * tau[order], ".", color=ACC, ms=2.2, label="MuJoCo 多体动力学（数字工厂）")
        a.set_xlabel("主轴转角 φ / °")
        a.set_ylabel("刺布机构驱动力矩 / N·m")
        a.set_title("刺布机构：两种方法对照（5000 r/min，不计缝纫阻力）", loc="left", fontsize=10)
        a.legend(frameon=False, fontsize=8)
        a.set_xticks(range(0, 361, 60))
        a.grid(color="#eef0f2", lw=0.6)
        save(fig, "2_MuJoCo对照")
        refi = np.interp(phi, rphi, ref, period=360)
        RES["mujoco"] = dict(points=len(phi), max_abs_ref=float(np.max(np.abs(ref))),
                             max_diff=float(np.max(np.abs(sgn * tau - refi))), rms_diff=float(np.sqrt(np.mean((sgn * tau - refi) ** 2))), sign=sgn)
    except Exception as exc:  # noqa: BLE001
        RES["mujoco"] = dict(error=repr(exc)[:300])
    shaft_report(R)
    motor(R)
    RES["k_best"] = k_best
    (OUT / "结果.json").write_text(json.dumps(RES, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: RES[k] for k in ("torque", "mujoco", "k_best")}, ensure_ascii=False, default=float)[:3000])
    print(json.dumps(RES["shaft"], ensure_ascii=False, default=float)[:3000])
    print(json.dumps(RES["motor"], ensure_ascii=False, default=float)[:1500])


if __name__ == "__main__":
    main()
