"""15.1 节：李群上的牛顿-拉夫森迭代。

(1) 算例 15.1.1：平面 3R 臂（尺寸同 14.2.5 节）在 SE(2) 上的位姿误差 V_b = log(T⁻¹ T_d)：转角与极点；
    牛顿-拉夫森迭代收敛到算例 14.2.2 的一组解。
(2) 物体雅可比 (15.1.4) 与差商核对；J_s = [Ad_T] J_b；一阶近似 (15.1.6) 的误差是二阶小量。
(3) 引理 15.1.1：F(θ) = log(T(θ)⁻¹T_d) 的导数 F′ = −(I − ½[ad_F]) J_b + O(‖F‖²)，用差商核对。
(4) 算例 15.1.2：UR5e 到达算例 14.5.1 的位姿，从“当前关节角”出发；与表 14.5.1 的解析解、与零件库模型核对；
    误差比 e_{k+1}/e_k²（定理 15.1.2）；其他起点；零位处 J_b 奇异；空间形式与物体形式给出同一步。
(5) 另一种常见的误差（位置差 + 姿态误差的指数坐标，都在 {s} 中）：同样收敛，步子不同。
(6) 算例 15.1.3：“标定后的”UR5e 没有现成的公式；以名义尺寸的解析解为初值，几步迭代修正到 10⁻¹² 量级。
"""
import math

import numpy as np

from _nik import (PL, TH_CUR, TH_HOME, TH_STAR, UR_B, UR_S, ad, adjoint, err_twist, exp_twist, fk_space, inv, jacobian_body,
                  jacobian_space, jb_planar, log_se2, log_twist, logR, nr, planar_nr, planar_pose, pole_se2, pose_err, se2,
                  ur_fk, ur_jb, ur_labels, ur_model, ur_screws_perturbed, ur_solution_index, ur_table, ur_target, wrap,
                  body_screws, ik3r)
from bookout import T as tr, out, vec

deg = np.degrees
rng = np.random.default_rng(151)

# ---------------------------------------------------------------- (1) 平面 3R 臂（SE(2)）
Tp = se2(0.6, 0.05, -math.pi / 2)                                # 算例 14.2.2 的目标位姿
p0 = np.radians([30, -40, -20])
V0 = log_se2(np.linalg.inv(planar_pose(p0)) @ Tp)
c_b = pole_se2(V0)                                              # 极点在 {b} 中
Tb = planar_pose(p0)
c_s = Tb[:2, :2] @ c_b + Tb[:2, 2]                              # 极点在 {s} 中
# 检验：{b} 绕极点转 φ 恰好到达 {d}
R = np.array([[math.cos(V0[0]), -math.sin(V0[0])], [math.sin(V0[0]), math.cos(V0[0])]])
Rs = Tb[:2, :2] @ R @ Tb[:2, :2].T
pb_new = c_s + Rs @ (Tb[:2, 2] - c_s)
assert np.linalg.norm(pb_new - Tp[:2, 2]) < 1e-12
pth, pok, phist = planar_nr(Tp, p0)
assert pok
psols = ik3r(0.6, 0.05, -math.pi / 2, *PL)
p_match = [i for i, s in enumerate(psols) if max(abs(wrap(a - b)) for a, b in zip(s, pth)) < 1e-10]
assert len(p_match) == 1
p_norms = [float(np.linalg.norm(V)) for _, V in phist]

# ---------------------------------------------------------------- (2) 物体雅可比
jac_err, ad_err, lin_ratio = 0.0, 0.0, []
for _ in range(200):
    th = rng.uniform(-math.pi, math.pi, 6)
    J = ur_jb(th)
    h = 1e-6
    Jn = np.zeros((6, 6))
    for i in range(6):
        d = np.zeros(6)
        d[i] = h
        Jn[:, i] = log_twist(inv(ur_fk(th - d)) @ ur_fk(th + d)) / (2 * h)
    jac_err = max(jac_err, float(np.abs(J - Jn).max()))
    ad_err = max(ad_err, float(np.abs(jacobian_space(UR_S, th) - adjoint(ur_fk(th)) @ J).max()))
assert jac_err < 1e-8 and ad_err < 1e-12
# 一阶近似 T(θ + Δθ) ≈ T(θ) e^{[J_b Δθ]}：误差随 ‖Δθ‖² 减小
th = np.radians([10, -50, 70, -30, 40, 20])
dirv = rng.normal(size=6)
dirv /= np.linalg.norm(dirv)
lin = []
for s in (1e-1, 1e-2, 1e-3):
    lin.append(float(np.linalg.norm(log_twist(inv(ur_fk(th) @ exp_twist(ur_jb(th) @ (s * dirv))) @ ur_fk(th + s * dirv)))))
lin_r1, lin_r2 = lin[0] / lin[1], lin[1] / lin[2]
assert 80 < lin_r1 < 120 and 80 < lin_r2 < 120                  # 步长缩小 10 倍，误差缩小约 100 倍

# ---------------------------------------------------------------- (3) 引理 15.1.1
Td = ur_target()
lem = []
for th in (TH_CUR, TH_HOME):
    X = err_twist(ur_fk(th), Td)
    h = 1e-6
    Fp = np.zeros((6, 6))
    for i in range(6):
        d = np.zeros(6)
        d[i] = h
        Fp[:, i] = (err_twist(ur_fk(th + d), Td) - err_twist(ur_fk(th - d), Td)) / (2 * h)
    Jb = ur_jb(th)
    lem.append((float(np.linalg.norm(X)), float(np.linalg.norm(Fp + Jb, 2)), float(np.linalg.norm(Fp + (np.eye(6) - 0.5 * ad(X)) @ Jb, 2))))
assert all(c < 0.1 * b for _, b, c in lem)

# ---------------------------------------------------------------- (4) 算例 15.1.2：UR5e
table = ur_table()
def sci(x, d=2):
    """1.23e-05 → 1.23\\times 10^{-5}（印在表中）。"""
    if x == 0:
        return "0"
    m, e = f"{x:.{d}e}".split("e")
    return f"{m}\\times 10^{{{int(e)}}}" if int(e) != 0 else m


ur = ur_model()
th, ok, hist = nr(ur_fk, ur_jb, Td, TH_CUR)
assert ok
k_cur = len(hist) - 1
idx_cur = ur_solution_index(th, table, 1e-12)
assert idx_cur == 3
diff_cur = max(abs(wrap(a - b)) for a, b in zip(th, table[idx_cur - 1]))
ep, eR = pose_err(ur.fk(th), Td)
assert ep < 1e-12 and eR < 1e-12
it_table = "\n".join(f"| {k} | " + ", ".join(f"{x:.3f}" for x in deg(t)) +
                     f" | ${sci(float(np.linalg.norm(V[:3])))}$ | ${sci(float(np.linalg.norm(V[3:])))}$ |"
                     for k, (t, V) in enumerate(hist))
ek = [float(np.linalg.norm(t - TH_STAR)) for t, _ in hist]
ratios = [ek[k + 1] / ek[k] ** 2 for k in range(len(ek) - 2)]
assert max(ratios) < 1.0
first_step = float(np.abs(deg(hist[1][0] - hist[0][0])).max())

# 其他起点
th_h, ok_h, hist_h = nr(ur_fk, ur_jb, Td, TH_HOME)
assert ok_h
idx_home, k_home = ur_solution_index(th_h, table, 1e-10), len(hist_h) - 1
th_b = np.radians([-120, -100, -80, -60, 90, 60])                # 习题 14.5.5 的“当前关节角”
th_bb, ok_b, hist_b = nr(ur_fk, ur_jb, Td, th_b)
assert ok_b
idx_b, k_b = ur_solution_index(th_bb, table, 1e-10), len(hist_b) - 1
lab_b = ur_labels(th_bb)
# 零位：关节 3 伸直、关节 5 为零，J_b 奇异
sv0 = np.linalg.svd(ur_jb(np.zeros(6)), compute_uv=False)
rank0 = int(np.sum(sv0 > 1e-10 * sv0[0]))
_, ok0, hist0 = nr(ur_fk, ur_jb, Td, np.zeros(6))
assert not ok0 and len(hist0) == 1

# 空间形式与物体形式给出同一步
step_diff = 0.0
for _ in range(50):
    t0 = rng.uniform(-math.pi, math.pi, 6)
    T0 = ur_fk(t0)
    Vb = err_twist(T0, Td)
    Vs = adjoint(T0) @ Vb
    db = np.linalg.solve(ur_jb(t0), Vb)
    ds = np.linalg.solve(jacobian_space(UR_S, t0), Vs)
    step_diff = max(step_diff, float(np.abs(db - ds).max() / max(1.0, np.abs(db).max())))
assert step_diff < 1e-9

# ---------------------------------------------------------------- (5) 另一种误差：位置差与姿态误差分开，都在 {s} 中
def nr_split(th, iters=60):
    th = np.array(th, float)
    for k in range(iters):
        T = ur_fk(th)
        e = np.r_[logR(Td[:3, :3] @ T[:3, :3].T), Td[:3, 3] - T[:3, 3]]
        if np.linalg.norm(e) < 1e-12:
            return th, k
        Js = jacobian_space(UR_S, th)
        # 末端原点的线速度 = v_s + ω_s × p（6.3 节），所以把 J_s 的下三行换成 v_s + ω_s × p 对应的行
        Jg = Js.copy()
        Jg[3:] = Js[3:] - np.cross(T[:3, 3], Js[:3].T).T
        th = th + np.linalg.solve(Jg, e)
    return th, None
th_sp, k_sp = nr_split(TH_CUR)
assert k_sp is not None and ur_solution_index(th_sp, table, 1e-10) == 3
th_sp2, k_sp2 = nr_split(TH_HOME)
idx_sp2 = ur_solution_index(th_sp2, table, 1e-9) if k_sp2 is not None else 0
assert idx_sp2 == 3                                              # 正文：两个起点都落在第 3 组

# ---------------------------------------------------------------- (6) 算例 15.1.3：标定后的 UR5e
Sc, Mc = ur_screws_perturbed(dL1=0.4e-3, dL2=-0.3e-3, tilt3=math.radians(0.05))
offs = np.radians([0.03, -0.05, 0.04, 0.06, -0.02, 0.05])       # 编码器零点偏差：实际关节角 = 读数 + δ
fk_c = lambda t: fk_space(Sc, Mc, np.asarray(t) + offs)
Bc = body_screws(Sc, Mc)
jb_c = lambda t: jacobian_body(Bc, np.asarray(t) + offs)
seed = table[2]                                                  # 名义尺寸下的解析解（第 3 组）
e_seed_p, e_seed_R = pose_err(fk_c(seed), Td)
V_seed = err_twist(fk_c(seed), Td)
ang_seed = math.degrees(float(np.linalg.norm(V_seed[:3])))
th_c, ok_c, hist_c = nr(fk_c, jb_c, Td, seed)
assert ok_c
k_c = len(hist_c) - 1
corr = deg(th_c - seed)
e_c_p, e_c_R = pose_err(fk_c(th_c), Td)
assert e_c_p < 1e-12
c_norms = [float(np.linalg.norm(V)) for _, V in hist_c]

out(
    # (1)
    p0_deg=vec(deg(p0), 0), pV=vec(V0, 4), pphi_deg=math.degrees(V0[0]), pc_s=vec(c_s, 4), p_k=len(phist) - 1,
    p_sol=vec(deg(pth), 2), p_norms=", ".join(f"{x:.1e}" for x in p_norms), p_which=p_match[0] + 1,
    pn0=p_norms[0], pn1=p_norms[1], pn2=p_norms[2],
    # (2)
    jac_err=jac_err, ad_err=ad_err, lin_r1=lin_r1, lin_r2=lin_r2,
    # (3)
    lem_X=lem[0][0], lem_a=lem[0][1], lem_b=lem[0][2], lem_X2=lem[1][0], lem_a2=lem[1][1], lem_b2=lem[1][2],
    # (4)
    it_table=it_table, k_cur=k_cur, idx_cur=idx_cur, diff_cur=diff_cur, ep=ep, eR=eR,
    r0=ratios[0], r1=ratios[1], r2=ratios[2], e0=ek[0], e1=ek[1], e2=ek[2], e3=ek[3], first_step=first_step,
    k_home=k_home, idx_home=idx_home, k_b=k_b, idx_b=idx_b, lab_b=f"{lab_b[0]}、" + (tr("肘上", "elbow up") if lab_b[1] == "up" else tr("肘下", "elbow down")) +
    "、" + (tr("腕不翻", "wrist not flipped") if lab_b[2] else tr("腕翻", "wrist flipped")),
    sv0=vec(sv0, 3), rank0=rank0, step_diff=step_diff,
    k_sp=k_sp, k_sp2=k_sp2 if k_sp2 is not None else -1, idx_sp2=idx_sp2,
    # (6)
    e_seed_mm=e_seed_p * 1000, ang_seed=ang_seed, k_c=k_c, corr=vec(corr, 4), e_c_p=e_c_p, e_c_R=e_c_R,
    c_n0=c_norms[0], c_n1=c_norms[1], c_n2=c_norms[2], c_last=c_norms[-1],
)
