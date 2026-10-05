"""15.5 节：收敛与初值。

(1) 算例 15.5.1：UR5e 初值平面（θ₁、θ₃ 各取 91 个值，其余关节取 θ* 的值）上的吸引域：牛顿-拉夫森、限步长的牛顿-拉夫森、
    LM、延拓法四种做法收敛的比例、收敛到“最近的一组解”的比例、保持起点构型（肩、肘、腕三个标签）的比例。
    成批计算与逐个计算核对。延拓法失败的起点，在失败处 J_b 的最小奇异值很小（路径碰到了奇异位形）。
(2) 算例 15.5.2：平面 2R 臂从 (0°, 60°) 出发到达 (−0.45, 0.35) m：直接用牛顿法落到 θ₂ < 0 的一支，关节角大幅跳动；
    延拓法（10 段）留在 θ₂ > 0 的一支。
(3) 定理 15.5.1：固定阻尼的阻尼最小二乘在解附近线性收敛，每步误差缩小为 λ²/(σ_min² + λ²) 倍；UR5e 上实测与预测比较。
    与牛顿-拉夫森（二次）和 LM（阻尼自动减小，超线性）比较。
(4) 实时跟踪：法兰盘沿直线以 0.25 m/s 移动，每 2 ms 以上一周期的解为初值，迭代一次后的误差与达到 10⁻¹⁰ 所需的次数。
(5) 目标够不着：牛顿-拉夫森不收敛、误差乱跳；LM 使误差单调下降后停住，但那里按 J_b 算出的“梯度”不为零：
    误差大时 J_b 不是误差旋量的准确导数（引理 15.1.1）。
(6) 随机重启的成功率（数据取自程序 15.4.1 的 Panda 统计，见 ex15_4.py）在正文中讨论，这里不重复计算。
"""
import math
import time

import numpy as np

import _basin as B
from _nik import (L2R, TH_CUR, TH_STAR, err_twist, fk_planar, newton_planar, nr, ur_err_batch, ur_fk, ur_jb, ur_labels, ur_table,
                  ur_target, wrap)
from bookout import T as tr, out, vec

t_start = time.time()
deg = np.degrees
Td = ur_target()
table = ur_table()
labs = [ur_labels(s) for s in table]

# ---------------------------------------------------------------- (1) 吸引域
n = 91
a, th0 = B.grid(n)
# 成批与逐个核对（随机抽 40 个初值）
rng = np.random.default_rng(155)
pick = rng.choice(len(th0), 40, replace=False)
thb, okb, itb = B.newton(th0[pick], Td, iters=1)                         # 第一步逐个比较（远处的迭代对舍入误差极敏感，不比较终点）
batch_err = 0.0
for i, j in enumerate(pick):
    th1, ok1, h1 = nr(ur_fk, ur_jb, Td, th0[j], tol_w=B.TOL, tol_v=B.TOL, iters=1)
    batch_err = max(batch_err, float(np.abs(th1 - thb[i]).max()))
assert batch_err < 1e-8
_, _, res = B.run_all(n)
L0 = [ur_labels(t) for t in th0]


def nearest(t):
    d = [np.linalg.norm([wrap(x - y) for x, y in zip(t, s)]) for s in table]
    return int(np.argmin(d)) + 1


near = np.array([nearest(t) for t in th0])
stat = {}
for name, (idx, ok, its) in res.items():
    idx, ok = idx.ravel(), ok.ravel()
    same = np.array([idx[i] > 0 and labs[idx[i] - 1] == L0[i] for i in range(len(idx))])
    stat[name] = dict(conv=100 * ok.mean(), near=100 * np.mean(idx == near), same=100 * same.mean(),
                      same_of_conv=100 * same.sum() / max(1, ok.sum()), it=float(np.median(its.ravel()[ok])),
                      sol3=100 * np.mean(idx == 3), nsol=int(len(set(idx[idx > 0]))))
assert stat["step"]["conv"] > stat["nr"]["conv"] and stat["step"]["same"] > stat["nr"]["same"]
assert stat["cont"]["same_of_conv"] > 90
# 延拓法失败的起点：重做一遍，记下失败那一段 J_b 的最小奇异值
fail = np.where(~res["cont"][1].ravel())[0]
sub = fail[np.random.default_rng(3).choice(len(fail), min(200, len(fail)), replace=False)]
smin_fail, retry_ok = [], []
for j in sub:
    t0 = th0[j]
    T0 = ur_fk(t0)
    V0 = err_twist(T0, Td)
    cur = t0.copy()
    from _nik import exp_twist
    smin = np.inf
    for s in np.linspace(0, 1, 101)[1:]:
        Ts = T0 @ exp_twist(s * V0)
        new, ok, _ = nr(ur_fk, ur_jb, Ts, cur, tol_w=1e-8, tol_v=1e-8, iters=8)
        smin = min(smin, float(np.linalg.svd(ur_jb(cur), compute_uv=False)[-1]))
        if not ok:
            break
        cur = new
    smin_fail.append(smin)
    retry_ok.append(bool(ok))
smin_fail = np.array(smin_fail)
frac_sing = 100 * np.mean(smin_fail < 0.02)
n_retry_ok = int(sum(retry_ok))                                             # 分成 100 段后成功：10 段时失败只因每段太长
frac_start_sing = 100 * float(np.mean([np.linalg.svd(ur_jb(th0[j]), compute_uv=False)[-1] < 0.02 for j in sub]))

# LM 失败的初值：停下的地方误差仍大；按 J_b 算出的“梯度” g_J = −J_bᵀW²V_b 与 f = ½‖W V_b‖² 的真实梯度（差商）方向不一致
lm_fail = np.where(~res["lm"][1].ravel())[0]
th_lm_all, ok_lm_all, _ = B.lm(th0[lm_fail], Td)
assert not ok_lm_all.any()
fW = lambda t: 0.5 * float(np.sum((B.WV * err_twist(ur_fk(t), Td)) ** 2))
cos_l, err_l = [], []
for t in th_lm_all[np.random.default_rng(5).choice(len(lm_fail), min(150, len(lm_fail)), replace=False)]:
    V = err_twist(ur_fk(t), Td)
    gJ = -ur_jb(t).T @ (B.WV ** 2 * V)
    gt = np.array([(fW(t + h) - fW(t - h)) / 2e-6 for h in np.eye(6) * 1e-6])
    cos_l.append(float(gt @ gJ / np.linalg.norm(gt) / np.linalg.norm(gJ)))
    err_l.append(float(np.linalg.norm(B.WV * V)))
cos_l, err_l = np.array(cos_l), np.array(err_l)
E0 = np.array([np.linalg.norm(B.WV * err_twist(ur_fk(t), Td)) for t in th0])
lm_init_fail, lm_init_all = float(np.median(E0[lm_fail])), float(np.median(E0))
assert np.median(cos_l) < 0.2 and err_l.min() > 1.0

# ---------------------------------------------------------------- (2) 算例 15.5.2：平面 2R 臂
pd2 = np.array([-0.45, 0.35])
th2_0 = np.radians([0.0, 60.0])
th_n, k_n, E_n, TH_n = newton_planar(pd2, th2_0, tol=1e-12)
jump = float(deg(np.abs(np.diff(np.array(TH_n), axis=0)).max()))
th_nw = np.array([wrap(x) for x in th_n])


def cont2(pd, th0, nseg=10):
    p0 = fk_planar(th0, L2R)[:2]
    th, tot, path = np.array(th0, float), 0, [np.array(th0, float)]
    for j in range(1, nseg + 1):
        pj = p0 + (pd - p0) * j / nseg
        th, k, _, _ = newton_planar(pj, th, tol=1e-12 if j == nseg else 1e-8)
        assert k is not None
        tot += k
        path.append(th.copy())
    return th, tot, np.array(path)


th_c, k_c, path_c = cont2(pd2, th2_0)
assert k_n is not None and math.sin(th_n[1]) < 0 < math.sin(th_c[1])
step_c = float(deg(np.abs(np.diff(path_c, axis=0)).max()))
# 两组解析解（第 14 章）：θ₂ = ±arccos(...)
c2 = (pd2 @ pd2 - L2R[0] ** 2 - L2R[1] ** 2) / (2 * L2R[0] * L2R[1])
t2a = math.acos(c2)
t1a = math.atan2(pd2[1], pd2[0]) - math.atan2(L2R[1] * math.sin(t2a), L2R[0] + L2R[1] * math.cos(t2a))
assert abs(wrap(th_c[0] - t1a)) < 1e-9 and abs(wrap(th_c[1] - t2a)) < 1e-9

# ---------------------------------------------------------------- (3) 定理 15.5.1：收敛速度
Lc, lam = B.LC, 0.4
Wd = np.diag(B.WV)


def dls(th, lam, iters=200):
    th = np.array(th, float)
    E = []
    for k in range(iters + 1):
        V = err_twist(ur_fk(th), Td)
        E.append(float(np.linalg.norm(Wd @ V)))
        if E[-1] < 1e-13:
            break
        J = Wd @ ur_jb(th)
        th = th + J.T @ np.linalg.solve(J @ J.T + lam ** 2 * np.eye(6), Wd @ V)
    return th, np.array(E)


th_d, E_d = dls(TH_CUR, lam)
sv = np.linalg.svd(Wd @ ur_jb(TH_STAR), compute_uv=False)
rho_pred = lam ** 2 / (sv[-1] ** 2 + lam ** 2)
ratios = E_d[1:-1] / E_d[:-2]                                               # 最后一步碰到舍入误差，不计
rho_meas = float(np.median(ratios[len(ratios) // 2:]))
assert abs(rho_meas - rho_pred) / rho_pred < 1e-3
th_nr, ok_nr, h_nr = nr(ur_fk, ur_jb, Td, TH_CUR)
E_nr = np.array([np.linalg.norm(Wd @ V) for _, V in h_nr])
_, ok_lm, it_lm = B.lm(TH_CUR[None, :], Td)
E_lm = []
th = TH_CUR[None, :].copy()
for k in range(1, 40):
    t, o, _ = B.lm(TH_CUR[None, :], Td, iters=k)
    E_lm.append(float(np.linalg.norm(Wd @ err_twist(ur_fk(t[0]), Td))))
    if o[0]:
        break
E_lm = np.r_[np.linalg.norm(Wd @ err_twist(ur_fk(TH_CUR), Td)), E_lm]
k_dls, k_nr, k_lm = len(E_d) - 1, len(E_nr) - 1, len(E_lm) - 1
# 定理 15.5.1 的一般形式：解附近每步误差 ≈ λ²(JJᵀ + λ²I)⁻¹ 作用于原误差
Jw = Wd @ ur_jb(TH_STAR)
Mlin = lam ** 2 * np.linalg.inv(Jw @ Jw.T + lam ** 2 * np.eye(6))
assert abs(np.linalg.norm(Mlin, 2) - rho_pred) < 1e-12

# ---------------------------------------------------------------- (4) 实时跟踪：上一周期的解作初值
dt, v = 0.002, 0.25
dirx = np.array([1.0, 0, 0])
N = 400
th = TH_STAR.copy()
err1, kmax, kall = [], 0, []
for k in range(1, N + 1):
    Tk = Td.copy()
    Tk[:3, 3] += v * k * dt * dirx
    J = ur_jb(th)
    V = err_twist(ur_fk(th), Tk)
    th1 = th + np.linalg.solve(J, V)
    err1.append(float(np.linalg.norm(ur_fk(th1)[:3, 3] - Tk[:3, 3])))
    th, ok, h = nr(ur_fk, ur_jb, Tk, th, tol_w=1e-10, tol_v=1e-10)
    assert ok
    kall.append(len(h) - 1)
step_mm = v * dt * 1000
assert max(kall) <= 3 and labs[2] == ur_labels(th)

# ---------------------------------------------------------------- (5) 够不着的目标
Tfar = Td.copy()
Tfar[:3, 3] = Td[:3, 3] * 1.8                                               # 把目标沿基座到法兰盘中心的方向推远到 1.8 倍
dist_far = float(np.linalg.norm(Tfar[:3, 3]))
_, ok_far_nr, h_far = nr(ur_fk, ur_jb, Tfar, TH_CUR, iters=100)
nr_far = [float(np.linalg.norm(Wd @ V)) for _, V in h_far]
th_far, ok_far_lm, _ = B.lm(TH_CUR[None, :], Tfar, iters=400)
Vf = err_twist(ur_fk(th_far[0]), Tfar)
f0 = float(np.linalg.norm(Wd @ err_twist(ur_fk(TH_CUR), Tfar)))
gap_mm = float(np.linalg.norm(ur_fk(th_far[0])[:3, 3] - Tfar[:3, 3]) * 1000)
grad_rel = float(np.linalg.norm(ur_jb(th_far[0]).T @ Wd @ Wd @ Vf) / np.linalg.norm(Wd @ Vf))
far_t3 = float(deg(wrap(th_far[0][2])))
assert not ok_far_nr and not ok_far_lm[0] and np.linalg.norm(Wd @ Vf) < f0 and max(nr_far) > 2 * nr_far[0]
nr_far_max, nr_far0 = max(nr_far), nr_far[0]

S = stat
out(n=n, grid_deg=360 / n,
    nr_conv=S["nr"]["conv"], nr_near=S["nr"]["near"], nr_same=S["nr"]["same"], nr_it=S["nr"]["it"], nr_sol3=S["nr"]["sol3"], nr_nsol=S["nr"]["nsol"],
    st_conv=S["step"]["conv"], st_near=S["step"]["near"], st_same=S["step"]["same"], st_it=S["step"]["it"], st_sol3=S["step"]["sol3"],
    lm_conv=S["lm"]["conv"], lm_near=S["lm"]["near"], lm_same=S["lm"]["same"], lm_it=S["lm"]["it"], lm_sol3=S["lm"]["sol3"],
    ct_conv=S["cont"]["conv"], ct_near=S["cont"]["near"], ct_same=S["cont"]["same"], ct_it=S["cont"]["it"], ct_sol3=S["cont"]["sol3"],
    ct_same_of_conv=S["cont"]["same_of_conv"], nr_same_of_conv=S["nr"]["same_of_conv"], st_same_of_conv=S["step"]["same_of_conv"],
    lm_same_of_conv=S["lm"]["same_of_conv"], frac_sing=frac_sing, n_retry_ok=n_retry_ok, frac_start_sing=frac_start_sing, lm_cos_med=float(np.median(cos_l)), lm_frac_up=100 * float(np.mean(cos_l < 0)), lm_err_min=float(err_l.min()), lm_err_max=float(err_l.max()), lm_init_fail=lm_init_fail, lm_init_all=lm_init_all, n_lm_fail=len(lm_fail), n_fail_sample=len(sub), step=math.degrees(B.STEP), nc=B.NC,
    p2_k=k_n, p2_jump=jump, p2_sol=vec(deg(th_nw), 1), p2_cont_k=k_c, p2_cont_sol=vec(deg(th_c), 1), p2_cont_step=step_c,
    lam=lam, sv_min=float(sv[-1]), rho_pred=rho_pred, rho_meas=rho_meas, k_dls=k_dls, k_nr=k_nr, k_lm=k_lm,
    trk_step_mm=step_mm, trk_err1=float(max(err1)), trk_kmax=max(kall), trk_kmean=float(np.mean(kall)), trk_N=N,
    far_dist=dist_far, far_gap_mm=gap_mm, far_nr_max=nr_far_max, far_nr0=nr_far0, far_grad_rel=grad_rel, far_t3=far_t3, far_f0=f0, far_f=float(np.linalg.norm(Wd @ Vf)),
    batch_err=batch_err, runtime=time.time() - t_start)

# ================================================================ 示意图（数据就是上面算出的）
from matplotlib.colors import ListedColormap

from _fig15 import C, arm_pts, base_mark, draw_arm, plane
from bookout import figure, style

plt = style()
SOLC = ["#d9d9d9", "#08519c", "#6baed6", "#1f9e89", "#a1d99b", "#b8860b", "#f2c14e", "#d62728", "#fb9a99"]
WR = {True: tr("不翻", "no flip"), False: tr("翻", "flip")}
EL = {"up": tr("上", "up"), "down": tr("下", "down")}

# ---------------------------------------------------------------- 图 15.5.2：吸引域
fig, axs = plt.subplots(2, 2, figsize=(10.4, 10.0))
titles = {"nr": tr("(a) 牛顿-拉夫森", "(a) Newton-Raphson"),
          "step": tr(f"(b) 限步长的牛顿-拉夫森（每步 ≤ {math.degrees(B.STEP):.0f}°）", f"(b) Step-limited Newton-Raphson (≤ {math.degrees(B.STEP):.0f}° per step)"),
          "lm": tr("(c) LM 法（自动调整阻尼）", "(c) Levenberg-Marquardt (adaptive damping)"),
          "cont": tr(f"(d) 延拓法（{B.NC} 段）", f"(d) Continuation ({B.NC} stages)")}
ad = math.degrees(a[1] - a[0])
ext = [-180 - ad / 2, 180 - ad / 2, -180 - ad / 2, 180 - ad / 2]
for ax, name in zip(axs.ravel(), ("nr", "step", "lm", "cont")):
    idx = res[name][0]
    ax.imshow(idx, origin="lower", extent=ext, cmap=ListedColormap(SOLC), vmin=-0.5, vmax=8.5, interpolation="nearest")
    ax.plot(30, 90, "*", color="white", ms=13, mec=C["ink"], mew=0.8)
    ax.set_xticks(range(-180, 181, 90))
    ax.set_yticks(range(-180, 181, 90))
    ax.set_xlabel(tr("起点的 θ₁ / (°)", "start θ₁ / (°)"))
    ax.set_ylabel(tr("起点的 θ₃ / (°)", "start θ₃ / (°)"))
    st = stat[name]
    ax.set_title(titles[name], fontsize=10, loc="left")
    ax.text(-175, 168, tr(f"收敛 {st['conv']:.0f}%，保持构型 {st['same']:.0f}%", f"converged {st['conv']:.0f}%, same posture {st['same']:.0f}%"),
            fontsize=8.5, color="white", va="top", bbox=dict(boxstyle="round,pad=0.2", fc="#00000080", ec="none"))
handles = [plt.Rectangle((0, 0), 1, 1, color=SOLC[0])]
names = [tr("不收敛", "not converged")]
for i, (sh, el, wr) in enumerate(labs, 1):
    handles.append(plt.Rectangle((0, 0), 1, 1, color=SOLC[i]))
    names.append(f"{i}  {sh} · {EL[el]} · {WR[wr]}")
fig.legend(handles, names, loc="lower center", ncol=5, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.005),
           title=tr("终点在表 14.5.1 中的编号（肩 · 肘 · 腕）；白色星号为 θ*（第 3 组）", "solution reached, numbered as in Table 14.5.1 (shoulder · elbow · wrist); white star: θ* (solution 3)"),
           title_fontsize=9)
fig.tight_layout(rect=(0, 0.07, 1, 1))
figure(fig, "fig15_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 15.5.3：平面 2R 臂，直接迭代与延拓
fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.6))
for ax, (mode, ttl) in zip(axs, (("nr", tr(f"(a) 直接用牛顿法：{k_n} 次迭代，落到 θ₂ < 0 的一支", f"(a) Newton directly: {k_n} iterations, ends with θ₂ < 0")),
                                 ("cont", tr(f"(b) 延拓法：目标分 10 段移动，留在 θ₂ > 0 的一支", "(b) Continuation: target moved in 10 stages, stays with θ₂ > 0")))):
    plane(ax, (-0.95, 0.95), (-0.9, 0.95))
    tt = np.linspace(0, 2 * math.pi, 300)
    R = L2R[0] + L2R[1]
    ax.plot(R * np.cos(tt), R * np.sin(tt), color=C["muted"], lw=0.8, ls=":")
    base_mark(ax)
    p0 = fk_planar(th2_0, L2R)[:2]
    if mode == "nr":
        for k, th in enumerate(TH_n[:6]):
            draw_arm(ax, arm_pts(th, L2R), C["accent"], lw=3, alpha=0.25 + 0.12 * k, jr=0.02)
            tip = arm_pts(th, L2R)[-1]
            ax.text(tip[0] + 0.03, tip[1] + 0.02, str(k), fontsize=8.5, color=C["accent"])
        draw_arm(ax, arm_pts(th_n, L2R), C["x"], lw=5)
    else:
        line = np.array([p0 + (pd2 - p0) * s for s in np.linspace(0, 1, 11)])
        ax.plot(*line.T, "o--", color=C["muted"], ms=3, lw=0.8)
        for th in path_c[:-1]:
            draw_arm(ax, arm_pts(th, L2R), C["z"], lw=2.5, alpha=0.3, jr=0.015)
        draw_arm(ax, arm_pts(th_c, L2R), C["z"], lw=5)
    draw_arm(ax, arm_pts(th2_0, L2R), C["ink"], lw=3, alpha=0.6, ls="--", jr=0.02)
    ax.plot(*pd2, "o", color=C["x"], ms=7, zorder=9)
    ax.text(pd2[0] - 0.05, pd2[1] + 0.07, tr("目标", "target"), fontsize=9, color=C["x"], ha="right")
    ax.text(p0[0] + 0.03, p0[1] - 0.08, tr("起点 (0°, 60°)", "start (0°, 60°)"), fontsize=9, color=C["ink"])
    ax.set_title(ttl, fontsize=10, loc="left")
fig.tight_layout()
figure(fig, "fig15_5_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 15.5.1：收敛速度
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.semilogy(range(len(E_nr)), np.maximum(E_nr, 1e-17), "o-", color=C["x"], ms=4, lw=1.4, label=tr("牛顿-拉夫森：二次收敛", "Newton-Raphson: quadratic"))
ax.semilogy(range(len(E_lm)), np.maximum(E_lm, 1e-17), "s-", color=C["accent"], ms=4, lw=1.4, label=tr("LM：阻尼自动减小", "LM: damping shrinks by itself"))
ax.semilogy(range(len(E_d)), np.maximum(E_d, 1e-17), "D-", color=C["z"], ms=3.5, lw=1.4, label=tr(f"固定阻尼 λ = {lam}：线性收敛", f"fixed damping λ = {lam}: linear"))
kk = np.arange(len(E_d))
ax.semilogy(kk, E_d[3] * rho_pred ** (kk - 3), color=C["z"], lw=0.8, ls=":", label=tr(f"定理 15.5.1 的斜率 ρ = {rho_pred:.3f}", f"slope of Theorem 15.5.1, ρ = {rho_pred:.3f}"))
ax.set_ylim(1e-15, 10)
ax.set_xlabel(tr("迭代次数 k", "iteration k"))
ax.set_ylabel(tr(r"加权误差 $\|\mathcal{V}_b\|_W$", r"weighted error $\|\mathcal{V}_b\|_W$"))
from matplotlib.ticker import MaxNLocator
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.legend(fontsize=8.5, frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, which="major", color="#e6e6e6", lw=0.6)
fig.tight_layout()
figure(fig, "fig15_5_1")
plt.close(fig)
