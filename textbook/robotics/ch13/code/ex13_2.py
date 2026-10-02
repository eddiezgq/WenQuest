"""算例 13.2.1、13.2.2：按步骤建立连杆坐标系。

13.2.1 SCARA（零件库模型，关节轴见表 12.3.2）：两张都合乎规则的标准 DH 表——
       表 A 按“平行轴取 d = 0”的默认规则（由程序按 13.2.2 节的步骤自动生成）；
       表 B 按工程习惯（{1} 放在大臂高度，{3} 放在工具安装面，丝杠变量带偏置）。
       两张表在算例 12.3.2 的关节变量下都给出与指数积相同的末端位姿，并与模型在一万组随机关节变量下核对。
13.2.2 UR5e（表 12.1.1 的六根轴）：按同样的步骤建立 {0}…{6}，读出各坐标系的原点；
       DH 正运动学与指数积、与零件库模型在一万组随机关节角下核对。
定理 13.2.1 的数值例证：中间坐标系取法不同，T_0n 相同。
"""
import math

import numpy as np

from _dh import Model, clean, fk_sdh, fk_space, inv, lines_to_sdh, screw_prismatic, screw_revolute, ur_poe
from bookout import out, tex, vec

rng = np.random.default_rng(132)
N = 10000

# ---------------------------------------------------------------- SCARA
sc = Model("B-SCA-WQ4", "base", "tool")
axes_sc = sc.axes()                                   # [(类型, 方向, 轴上一点)]
Ss = [screw_prismatic(w) if k == "P" else screw_revolute(w, q) for k, w, q in axes_sc]
Ms = sc.fk(np.zeros(4))
kinds = ["R", "R", "P", "R"]
tabA, FA = lines_to_sdh(axes_sc, Ms[:3, 3])           # 表 A：默认规则
offA = [0.0] * 4
pi = math.pi
tabB = [(0.35, 0.0, 0.4, 0.0), (0.25, pi, 0.0, 0.0), (0.0, pi, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)]   # 表 B
offB = [0.0, 0.0, 0.158, 0.0]                          # 丝杠：d_3 = θ_3 + 0.158 m
q_ex = np.array([math.radians(40), math.radians(-70), 0.12, math.radians(90)])     # 算例 12.3.2
T_poe = fk_space(Ss, Ms, q_ex)
TA = fk_sdh(tabA, q_ex, kinds, offA)
TB = fk_sdh(tabB, q_ex, kinds, offB)
assert np.allclose(TA, T_poe, atol=1e-12) and np.allclose(TB, T_poe, atol=1e-12)
errA = errB = 0.0
for _ in range(N):
    q = np.r_[rng.uniform(-pi, pi, 2), rng.uniform(0, 0.15), rng.uniform(-pi, pi)]
    Tm = sc.fk(q)
    errA = max(errA, float(np.abs(fk_sdh(tabA, q, kinds, offA) - Tm).max()))
    errB = max(errB, float(np.abs(fk_sdh(tabB, q, kinds, offB) - Tm).max()))
assert errA < 1e-9 and errB < 1e-9
# 表 B 各坐标系原点（零位）
FB = fk_sdh(tabB, np.zeros(4), kinds, offB, frames=True)
FA0 = fk_sdh(tabA, np.zeros(4), kinds, offA, frames=True)
assert all(np.allclose(F1, F2, atol=1e-12) for F1, F2 in zip(FA, FA0))   # 自动建系得到的坐标系 = 按表 A 算出的坐标系


def rows_tex(tab, off, kinds):
    """DH 表的 LaTeX 行：(a, α, d, θ)；关节变量写成 θ_i 或 d_i = θ_i + 偏置。"""
    out_rows = []
    for i, ((a, al, d, th), k, o) in enumerate(zip(tab, kinds, off), 1):
        al_s = {0: "0", 1: r"\pi", -1: r"-\pi", 0.5: r"\pi/2", -0.5: r"-\pi/2"}[round(al / pi * 2) / 2]
        if k == "R":
            th_s = rf"\theta_{i}" + ("" if abs(th) < 1e-12 else f"{th:+.4f}")
            d_s = f"{d:.3f}".rstrip("0").rstrip(".") if abs(d) > 1e-12 else "0"
        else:
            th_s = "0"
            d_s = rf"\theta_{i}" + (f" + {o + d:.3f}" if abs(o + d) > 1e-12 else "")
        a_s = f"{a:.3f}".rstrip("0").rstrip(".") if abs(a) > 1e-12 else "0"
        out_rows.append(f"{i} & {a_s} & {al_s} & {d_s} & {th_s}")
    return r" \\ ".join(out_rows)


# ---------------------------------------------------------------- UR5e
tab, S_ur, M_ur = ur_poe()
axes_ur = [("R", np.asarray(w, float), np.asarray(q, float)) for w, q in tab]
tab_ur, F_ur = lines_to_sdh(axes_ur, M_ur[:3, 3])
ur = Model("B-ARM-UR5E", "base", "wrist_3_link", (0, 0.1, 0))
T6b = inv(F_ur[-1]) @ M_ur                               # {6} 到第 12 章 {b} 的固定变换
err_ur_poe = err_ur_model = 0.0
for _ in range(N):
    q = rng.uniform(-pi, pi, 6)
    A = fk_sdh(tab_ur, q) @ T6b
    err_ur_poe = max(err_ur_poe, float(np.abs(A - fk_space(S_ur, M_ur, q)).max()))
    err_ur_model = max(err_ur_model, float(np.abs(A - ur.fk(q)).max()))
assert err_ur_poe < 1e-9 and err_ur_model < 1e-9
origins = [clean(F[:3, 3]) for F in F_ur]

# 定理 13.2.1：中间坐标系换一种取法（把 {2} 的原点沿 z_2 平移 0.05 m，并把 x_2 反向），T_06 不变
alt = [list(r) for r in tab_ur]
# {2} 沿 z_2 平移 c：第 2 行 d 增加 c、第 3 行 d 减少 c；x_2 反向：第 2 行 θ 偏置 +π、a 变号，第 3 行 θ 偏置 +π
c = 0.05
alt[1][2] += c
alt[2][2] -= c
alt[1][3] += pi
alt[1][0] = -alt[1][0]
alt[2][3] += pi
for _ in range(100):
    q = rng.uniform(-pi, pi, 6)
    assert np.allclose(fk_sdh(alt, q), fk_sdh(tab_ur, q), atol=1e-12)

out(scA=rows_tex(tabA, offA, kinds), scB=rows_tex(tabB, offB, kinds), T_sc=tex(clean(TB, 1e-12), 4),
    errA=errA, errB=errB, N=N, oB1=vec(FB[1][:3, 3], 3), oB3=vec(FB[3][:3, 3], 3), oA1=vec(clean(FA0[1][:3, 3]), 3),
    oA3=vec(clean(FA0[3][:3, 3]), 3),
    **{f"o{i}": vec(o, 3) for i, o in enumerate(origins)},
    T6b=tex(clean(T6b), 0), err_ur_poe=err_ur_poe, err_ur_model=err_ur_model)
