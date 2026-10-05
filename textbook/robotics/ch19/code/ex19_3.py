"""19.3 节的计算：瑞典轮的运动学，三轮全向底盘与四轮麦克纳姆底盘。

算例 19.3.1  四轮麦克纳姆 AGV（r = 0.075 m，l = 0.25 m，w = 0.20 m）：由式 (19.3.3) 逐轮写出 H，与常用的展开式核对；
             前进、侧移、斜行、原地转四种运动的轮速。
算例 19.3.2  正运动学：H 的秩、左零空间（相容条件）、伪逆的闭式；一个车轮打滑时的最小二乘估计与残差。
算例 19.3.3  装错辊子方向的两种情形：四个轮子的辊子同向（H 降秩，有一个方向不受控），左右装反（转动一列很小，条件数变大）。
算例 19.3.4  轮速限制下的速度范围：直行、侧移、斜行、原地转的最高速度。
算例 19.3.5  三轮全向底盘（γ = 0，三轮相隔 120°）：H 是方阵，可逆；由轮速求车体运动旋量。
"""
import math

import numpy as np

from _mob import rank, swedish_row
from bookout import T, out

r, l, w = 0.075, 0.25, 0.20
wmax = 20.0
g = math.radians(45)
# 车轮：名称、(x_i, y_i)、γ_i；β_i = 0（四个轮子都朝前装）
wheels = [("FL", l, w, -g), ("FR", l, -w, +g), ("RL", -l, w, +g), ("RR", -l, -w, -g)]
H = np.array([swedish_row(x, y, 0.0, gm, r) for _, x, y, gm in wheels])
k = l + w
H_ref = np.array([[-k, 1, -1], [k, 1, 1], [-k, 1, 1], [k, 1, -1]]) / r          # 式 (19.3.5)
assert np.allclose(H, H_ref, atol=1e-12)

cases = {"fwd": np.array([0.0, 0.5, 0.0]), "side": np.array([0.0, 0.0, 0.3]), "diag": np.array([0.0, 0.3, 0.3]),
         "spin": np.array([1.0, 0.0, 0.0])}
speeds = {kk: H @ V for kk, V in cases.items()}
assert np.allclose(speeds["diag"][[0, 3]], 0)                      # 斜行时 FL、RR 不转

# ---------------------------------------------------------------- 算例 19.3.2：秩、相容条件、伪逆
rk = rank(H)
assert rk == 3
nvec = np.array([1.0, 1.0, -1.0, -1.0])
assert np.allclose(nvec @ H, 0)
Hp = np.linalg.pinv(H)
Hp_ref = (r / 4) * np.array([[-1 / k, 1 / k, -1 / k, 1 / k], [1, 1, 1, 1], [-1, 1, 1, -1]])
assert np.allclose(Hp, Hp_ref, atol=1e-12)
assert np.allclose(Hp @ H, np.eye(3), atol=1e-12)
# 侧移 0.3 m/s 时右前轮打滑，编码器读数比应有的少 5%
cmd = speeds["side"]
meas = cmd.copy()
meas[1] *= 0.95
V_hat = Hp @ meas
resid = float(nvec @ meas / 2)                    # 相容条件的残差（rad/s），不打滑时为零
fit = H @ V_hat
res_vec = meas - fit
assert abs(float(np.linalg.norm(res_vec)) - abs(resid)) < 1e-12          # 残差就在左零空间方向上

# ---------------------------------------------------------------- 算例 19.3.3：装错辊子
H_same = np.array([swedish_row(x, y, 0.0, +g, r) for _, x, y, _ in wheels])          # 四个轮子辊子同向
rk_same = rank(H_same)
assert rk_same == 2
ns = np.linalg.svd(H_same)[2][-1]
ns = ns / ns[np.argmax(np.abs(ns))]
assert abs(ns[0]) < 1e-9 and abs(abs(ns[1]) - 1) < 1e-9 and abs(abs(ns[2]) - 1) < 1e-9 and ns[1] * ns[2] < 0   # 斜向 (v_x, v_y) ∝ (1, −1)
H_swap = np.array([swedish_row(x, y, 0.0, -gm, r) for _, x, y, gm in wheels])        # 左右装反（每个轮的辊子方向反过来）
assert rank(H_swap) == 3
sv_ok = np.linalg.svd(H, compute_uv=False)
sv_sw = np.linalg.svd(H_swap, compute_uv=False)
cond_ok, cond_sw = sv_ok[0] / sv_ok[-1], sv_sw[0] / sv_sw[-1]
spin_sw = H_swap @ np.array([1.0, 0, 0])
# 装反后要原地转 1 rad/s，轮速只需 (l − w)/r；能达到的最高原地转速却是 r ω_max/(l − w)，同时转动几乎“推不动”
spin_need_sw = (l - w) / r

# ---------------------------------------------------------------- 算例 19.3.4：速度范围
v_fwd = r * wmax                                   # |v_x| + |v_y| + k|ω| ≤ r ω_max
v_side = r * wmax
v_diag_comp = r * wmax / 2
v_diag = math.hypot(v_diag_comp, v_diag_comp)
om_max = r * wmax / k
# 用线性规划式的扫描核对：各方向上的最高速度 = r ω_max / (|cos α| + |sin α|)
for a in np.linspace(0, 2 * math.pi, 73):
    d = np.array([0.0, math.cos(a), math.sin(a)])
    vmax_a = wmax / np.abs(H @ d).max()
    assert abs(vmax_a - r * wmax / (abs(math.cos(a)) + abs(math.sin(a)))) < 1e-9

# ---------------------------------------------------------------- 算例 19.3.5：三轮全向
r3, R3 = 0.03, 0.12
alphas = [math.radians(a) for a in (90, 210, 330)]                 # 三个轮子在车体上的方位
H3 = np.array([swedish_row(R3 * math.cos(a), R3 * math.sin(a), a + math.pi / 2, 0.0, r3) for a in alphas])
H3_ref = np.array([[R3, -math.sin(a), math.cos(a)] for a in [a + math.pi / 2 for a in alphas]]) / r3
H3_ref = np.array([[R3, math.cos(a + math.pi / 2), math.sin(a + math.pi / 2)] for a in alphas]) / r3
assert np.allclose(H3, H3_ref, atol=1e-12)
det3 = float(np.linalg.det(H3))
assert abs(det3 - (-3 * math.sqrt(3) / 2 * R3 / r3 ** 3)) < 1e-6 * abs(det3) or abs(abs(det3) - 3 * math.sqrt(3) / 2 * R3 / r3 ** 3) < 1e-6 * abs(det3)
w3 = np.array([10.0, -5.0, -5.0])
V3 = np.linalg.solve(H3, w3)
assert np.allclose(H3 @ V3, w3)

fmt = lambda a: ", ".join(f"{x:.2f}".replace("-", "−") for x in a)
out(r=r, l=l, w=w, k=k, wmax=wmax, kr=k / r, inv_r=1 / r,
    fwd=fmt(speeds["fwd"]), side=fmt(speeds["side"]), diag=fmt(speeds["diag"]), spin=fmt(speeds["spin"]),
    fwd1=speeds["fwd"][0], side1=abs(speeds["side"][0]), diag2=speeds["diag"][1], spin1=abs(speeds["spin"][0]),
    rk=rk, meas=fmt(meas), vx_hat=V_hat[1], vy_hat=V_hat[2], om_hat=V_hat[0], resid=resid,
    err_vy_mm=(0.3 - V_hat[2]) * 1000, err_vx_mm=V_hat[1] * 1000, om_hat_deg=math.degrees(V_hat[0]),
    rk_same=rk_same, cond_ok=cond_ok, cond_sw=cond_sw, spin_sw=fmt(spin_sw), spin_need_sw=spin_need_sw,
    lw_diff=l - w, om_max_sw=r * wmax / (l - w),
    v_fwd=v_fwd, v_side=v_side, v_diag_comp=v_diag_comp, v_diag=v_diag, om_max=om_max,
    r3=r3, R3=R3, det3=det3, vx3=V3[1], vy3=V3[2], om3=V3[0])
