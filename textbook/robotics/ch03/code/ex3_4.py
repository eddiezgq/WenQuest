"""3.4 节的算例。

算例 3.4.1：在倾斜 20° 的工件表面上抛光。“把速度投影到表面上”是一个投影张量 P：在表面坐标系 {b} 中 P_b = diag(1, 1, 0)，
           在机座坐标系 {a} 中 P_a = R_ab P_b R_abᵀ，应当等于 I − n nᵀ。命令速度 v_cmd 投影后与法线垂直；
           若误把 diag(1, 1, 0) 直接用在 {a} 中，工具会以一定速度扎进表面。比较两套分量的迹、行列式、特征值。
算例 3.4.2：夹爪中倾斜 30° 的矩形板（惯量张量预告）。I_b = m/12 diag(b²+c², a²+c², a²+b²)，I_t = R_tb I_b R_tbᵀ；
           另用“把板划分成小块直接求和”的办法在工具坐标系 {t} 中算一次核对。绕工具 z 轴以 1 r/s 转动时，L = I ω 与 ω 不平行。
另外验证：R[a]Rᵀ = [Ra]（定理 3.4.4）；对称性、迹、行列式、特征值在换坐标系时不变。
"""
import math

import numpy as np

from _vec import d, rot_x, rot_z, skew
from bookout import out, tex, vec

# ---------------------------------------------------------------- 算例 3.4.1 投影张量
R_ab = rot_x(d(20))                                   # 表面坐标系 {b} 相对机座 {a}：绕 x 轴倾斜 20°
P_b = np.diag([1.0, 1.0, 0.0])
P_a = R_ab @ P_b @ R_ab.T                             # 式 (3.4.4)
n_a = R_ab[:, 2]                                      # 表面法线 = {b} 的 z 轴
assert np.allclose(P_a, np.eye(3) - np.outer(n_a, n_a))                 # 式 (3.4.8)：两种算法一致
# 分量形式 (3.4.5)：逐项求和
P_sum = np.array([[sum(R_ab[i, k] * R_ab[j, l] * P_b[k, l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)])
assert np.allclose(P_sum, P_a)
v_cmd = np.array([0.05, 0.10, 0.0])                    # 命令速度（机座坐标系），m/s
v = P_a @ v_cmd
assert abs(v @ n_a) < 1e-15                           # 投影后沿表面
v_wrong = P_b @ v_cmd                                 # 错误：把 {b} 中的分量矩阵用在 {a} 中
dig = float(v_wrong @ n_a)                            # 沿法线的速度（负值 = 扎向表面）
# 在 {b} 中算一遍再换回 {a}
assert np.allclose(R_ab @ (P_b @ (R_ab.T @ v_cmd)), v)
# 不变量
for M in (P_a, P_b):
    assert abs(np.trace(M) - 2) < 1e-12 and abs(np.linalg.det(M)) < 1e-12
assert np.allclose(np.sort(np.linalg.eigvalsh(P_a)), [0, 1, 1])
# 表面坐标系绕法线任意转动，P 的分量不变：P 只取决于法线方向
for t in (0.3, 1.0, 2.5):
    R2 = R_ab @ rot_z(t)
    assert np.allclose(R2 @ P_b @ R2.T, P_a)

# ---------------------------------------------------------------- 算例 3.4.2 惯量张量（预告）
a, b, c, m = 0.30, 0.20, 0.02, 2.0
I_b = m / 12 * np.diag([b * b + c * c, a * a + c * c, a * a + b * b])     # 板自身的主轴坐标系 {b}
R_tb = rot_x(d(30))                                   # 板相对工具坐标系 {t} 绕 x 轴倾斜 30°
I_t = R_tb @ I_b @ R_tb.T
# 第二种算法：把板划分成 N 个小块，在 {t} 中按式 (3.4.9) 直接求和  I = Σ m_k (|r|² I − r rᵀ) = −Σ m_k [r]²
nx, ny, nz = 120, 80, 8
xs = (np.arange(nx) + 0.5) / nx * a - a / 2
ys = (np.arange(ny) + 0.5) / ny * b - b / 2
zs = (np.arange(nz) + 0.5) / nz * c - c / 2
X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
pts_b = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
pts_t = pts_b @ R_tb.T
mk = m / len(pts_t)
r2 = np.einsum("ki,ki->k", pts_t, pts_t)
I_sum = mk * (r2.sum() * np.eye(3) - pts_t.T @ pts_t)
assert np.allclose(I_sum, I_t, rtol=2e-3, atol=1e-7)                       # 中点求和的误差约为千分之一以内
r0 = pts_t[0]
assert np.allclose(-skew(r0) @ skew(r0), (r0 @ r0) * np.eye(3) - np.outer(r0, r0))   # 式 (3.2.16)
w = np.array([0.0, 0.0, 2 * math.pi])                 # 绕工具 z 轴 1 r/s
L = I_t @ w
ang_Lw = math.degrees(math.acos(L @ w / (np.linalg.norm(L) * np.linalg.norm(w))))
assert abs(np.trace(I_t) - np.trace(I_b)) < 1e-15 and abs(np.linalg.det(I_t) - np.linalg.det(I_b)) < 1e-15
assert np.allclose(np.sort(np.linalg.eigvalsh(I_t)), np.sort(np.diag(I_b)))
assert np.allclose(I_t, I_t.T)

# ---------------------------------------------------------------- 定理 3.4.4：R[a]Rᵀ = [Ra]，式 (3.4.6)
rng = np.random.default_rng(11)
for _ in range(100):
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    w0, x0, y0, z0 = q
    R = np.array([[1 - 2 * (y0 * y0 + z0 * z0), 2 * (x0 * y0 - w0 * z0), 2 * (x0 * z0 + w0 * y0)],
                  [2 * (x0 * y0 + w0 * z0), 1 - 2 * (x0 * x0 + z0 * z0), 2 * (y0 * z0 - w0 * x0)],
                  [2 * (x0 * z0 - w0 * y0), 2 * (y0 * z0 + w0 * x0), 1 - 2 * (x0 * x0 + y0 * y0)]])   # 随机旋转矩阵
    av = rng.normal(size=3)
    assert np.allclose(R @ skew(av) @ R.T, skew(R @ av))

out(
    s20=math.sin(d(20)), c20=math.cos(d(20)), R_ab=tex(R_ab, 4), P_a=tex(P_a, 4), n_a=vec(n_a, 4),
    v=vec(v, 4), v1=v[0], v2=v[1], v3=v[2], dig_mm=-dig * 1000, v_speed=float(np.linalg.norm(v)),
    cmd_speed=float(np.linalg.norm(v_cmd)),
    I_b=tex(I_b * 1e3, 3), I_t=tex(I_t * 1e3, 3), Ixx=I_b[0, 0] * 1e3, Iyy=I_b[1, 1] * 1e3, Izz=I_b[2, 2] * 1e3,
    Iyz=I_t[1, 2] * 1e3, trI=np.trace(I_b) * 1e3, L=vec(L * 1e3, 2), ang_Lw=ang_Lw, w=2 * math.pi,
    I_err=float(np.abs(I_sum - I_t).max() / np.abs(I_t).max()),
)
