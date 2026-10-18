"""23.1 节的计算：质量、质心与惯量张量。

(1) 算例 23.1.1：夹爪（1.0 kg，示意值）夹住 SH-301 毛坯后的总质量与总质心（式 (23.1.3)）。
(2) 算例 23.1.2：SH-301 毛坯（数字工厂物料清单：每根耗 Ø50 mm 圆钢 2.8 kg）的长度与对质心的惯量。三种算法互相核对：
    式 (23.1.12) 的闭式；按定义 (23.1.6) 在柱坐标网格上直接求和；MuJoCo 由同样尺寸、质量的圆柱几何体自己算出的惯量。
    再用 MuJoCo 核对长方体公式 (23.1.11)（第 3 章算例 3.4.2 的板）。
(3) 算例 23.1.3：书中 UR5e 模型（MuJoCo Menagerie）各连杆的主惯量，反推“等效均匀实心圆柱”的半径与长度；
    检查每个连杆都满足三角不等式（定理 23.1.4）。
(4) 算例 23.1.4：毛坯在卡盘里夹偏 1°，主轴 1200 r/min（示意值）：惯量张量的非对角元素、L 与 ω 的夹角、
    轴承要提供的力矩 ω²|I_t − I_a| sin α cos α（式 (23.1.16)），与偏心 0.1 mm 的静不平衡力 m e ω² 比较。
    MuJoCo 用同一个夹偏的圆柱自由地绕竖直轴转动，读出铰链的约束力矩，与公式核对（实验 23.1 用同一个模型）。
(5) 习题答案。
"""
import math

import numpy as np

from _ch23 import (D_BAR, GRIP_C, GRIP_M, GRIP_TOP, RHO_STEEL, TCP, box_inertia, cyl_inertia, mj_load, mjcf_text,
                   parse_links, rotx, sh301_blank)
from bookout import out, tex

# ---------------------------------------------------------------- (2) 毛坯（先算，算例 23.1.1 要用它的长度）
m_b, r_b, L_b = sh301_blank()
assert abs(m_b - 2.8) < 1e-12 and abs(2 * r_b - D_BAR) < 1e-12
Ic = cyl_inertia(m_b, r_b, L_b)
I_t, I_a = Ic[0, 0], Ic[2, 2]

# 按定义在柱坐标网格上求和：每个小单元 dm = ρ r dr dφ dz，位于 (r cos φ, r sin φ, z)，取单元中点
nr, nphi, nz = 160, 192, 160
rr = (np.arange(nr) + 0.5) * r_b / nr
ph = (np.arange(nphi) + 0.5) * 2 * math.pi / nphi
zz = (np.arange(nz) + 0.5) * L_b / nz - L_b / 2
R_, P_ = np.meshgrid(rr, ph, indexing="ij")
dA = RHO_STEEL * R_ * (r_b / nr) * (2 * math.pi / nphi)          # 每个 (r, φ) 单元乘 dz 之前的质量
X, Y = R_ * np.cos(P_), R_ * np.sin(P_)
dz = L_b / nz
mass_sum = dA.sum() * dz * nz
Sx2, Sy2, Sxy = (dA * X * X).sum() * dz * nz, (dA * Y * Y).sum() * dz * nz, (dA * X * Y).sum() * dz * nz
Sz2 = dA.sum() * dz * (zz ** 2).sum()
Sxz = (dA * X).sum() * dz * zz.sum()
Syz = (dA * Y).sum() * dz * zz.sum()
I_grid = np.array([[Sy2 + Sz2, -Sxy, -Sxz], [-Sxy, Sx2 + Sz2, -Syz], [-Sxz, -Syz, Sx2 + Sy2]])
err_grid = float(np.abs(I_grid - Ic).max() / Ic.max())
assert abs(mass_sum / m_b - 1) < 1e-3 and err_grid < 1e-3

# MuJoCo：圆柱几何体（size = 半径、半长），质量给定，惯量由 MuJoCo 自己算
mj, mm, dd = mj_load(f'<mujoco><worldbody><body><freejoint/><geom type="cylinder" size="{r_b} {L_b / 2}" mass="{m_b}"/></body>'
                     f'<body pos="1 0 0"><freejoint/><geom type="box" size="0.15 0.10 0.01" mass="2.0"/></body></worldbody></mujoco>')
I_mj = mm.body_inertia[1].copy()
err_mj = float(np.abs(I_mj - np.diag(Ic)).max() / Ic.max())
assert err_mj < 1e-12
plate = box_inertia(2.0, 0.30, 0.20, 0.02)                         # 算例 3.4.2 的板
assert np.allclose(mm.body_inertia[2], np.diag(plate), rtol=1e-12, atol=0)

# ---------------------------------------------------------------- (1) 算例 23.1.1：夹爪 + 毛坯
y_top = TCP - GRIP_TOP                                              # 毛坯靠法兰一端在工具方向上的位置
y_blank = y_top + L_b / 2
m_tot = GRIP_M + m_b
y_c = (GRIP_M * GRIP_C + m_b * y_blank) / m_tot
assert GRIP_C < y_c < y_blank

# ---------------------------------------------------------------- (3) 算例 23.1.3：UR5e 各连杆的主惯量与“等效圆柱”
links = parse_links(mjcf_text())
rows, eq = [], []
tri_min = 9.0
for L in links:
    d = np.sort(L.diag)
    tri_min = min(tri_min, (d[0] + d[1]) / d[2])
    # 两个相等的主惯量是横向的 I_t，另一个是沿轴的 I_a（对圆柱：I_a = m r²/2，I_t = m(3r² + ℓ²)/12）
    vals, cnt = np.unique(np.round(L.diag, 12), return_counts=True)
    I_ax = float(vals[cnt == 1][0])
    I_tr = float(vals[cnt == 2][0])
    r_eq = math.sqrt(2 * I_ax / L.m)
    l_eq = math.sqrt(12 * I_tr / L.m - 3 * r_eq ** 2)
    eq.append((L.name, L.m, r_eq, l_eq))
    rows.append(f"\\text{{{L.name.replace('_', '\\_')}}} & {L.m:g} & {r_eq:.4f} & {l_eq:.4f}")
assert tri_min >= 1.0                                               # 三角不等式（定理 23.1.4）
eqd = {n: (m, r, l) for n, m, r, l in eq}
for n in ("base", "shoulder_link", "upper_arm_link", "forearm_link", "wrist_1_link", "wrist_2_link"):
    assert abs(eqd[n][1] - 0.06) < 1e-6                             # 六个连杆都是半径 0.06 m 的实心圆柱
assert abs(eqd["upper_arm_link"][2] - 0.425) < 1e-5 and abs(eqd["forearm_link"][2] - 0.392) < 1e-5   # 长度 = L₁、L₂（表 12.1.1）
ua = [L for L in links if L.name == "upper_arm_link"][0]
assert abs(ua.ipos[2] - 0.425 / 2) < 1e-12                          # 质心在杆长的中点
# 来源核对：Menagerie 的 UR5e（README：由 ROS-Industrial universal_robot 的 ur_e_description URDF 转换）。
# 那个 URDF（kinetic-devel，ur_e_description/urdf/ur5e.urdf.xacro）用宏 cylinder_inertial 按均匀圆柱算惯量：
#   ixx = iyy = 0.0833333 m (3r² + ℓ²)，izz = 0.5 m r²；半径、长度如下（m）。
URDF_CYL = {"base": (4.0, 0.06, 0.05), "shoulder_link": (3.7, 0.06, 0.15), "upper_arm_link": (8.393, 0.06, 0.425),
            "forearm_link": (2.275, 0.06, 0.392), "wrist_1_link": (1.219, 0.06, 0.12), "wrist_2_link": (1.219, 0.06, 0.12)}
lk = {L.name: L for L in links}
for n, (m_, r_, l_) in URDF_CYL.items():
    t_ = 0.0833333 * m_ * (3 * r_ * r_ + l_ * l_)
    assert abs(lk[n].m - m_) < 1e-12 and np.allclose(np.sort(lk[n].diag), np.sort([t_, t_, 0.5 * m_ * r_ * r_]), rtol=5e-6, atol=0)
# 最后一个连杆：URDF 是 0.1879 kg、r = 0.0375 m、ℓ = 0.0458 m 的圆柱（轴线沿 y，中心在 y = 0.1 − ℓ/2）；MuJoCo 转换时把
# 没有 <inertial> 的 ee_link 并了进来，它的碰撞几何是边长 1 cm 的立方体（中心在 y = 0.09），按默认密度 1000 kg/m³ 得 1 g。
m_c3, r_c3, l_c3, m_ee = 0.1879, 0.0375, 0.0458, 1000 * 0.01 ** 3
c_c3, c_ee = np.array([0, 0.1 - l_c3 / 2, 0]), np.array([0, 0.09, 0])
m_w3 = m_c3 + m_ee
c_w3 = (m_c3 * c_c3 + m_ee * c_ee) / m_w3
t3 = 0.0833333 * m_c3 * (3 * r_c3 ** 2 + l_c3 ** 2)
I_w3 = (np.diag([t3, 0.5 * m_c3 * r_c3 ** 2, t3]) + m_c3 * ((c_c3 - c_w3) @ (c_c3 - c_w3) * np.eye(3) - np.outer(c_c3 - c_w3, c_c3 - c_w3))
        + np.eye(3) * m_ee * 2 * 0.01 ** 2 / 12 + m_ee * ((c_ee - c_w3) @ (c_ee - c_w3) * np.eye(3) - np.outer(c_ee - c_w3, c_ee - c_w3)))
w3 = lk["wrist_3_link"]
assert abs(w3.m - m_w3) < 1e-12 and np.allclose(w3.ipos, c_w3, atol=1e-7)
assert np.allclose(np.sort(w3.diag), np.sort(np.diag(I_w3)), rtol=5e-6, atol=0)
# 毛坯长度与数字工厂工艺规程 GY-SH301 的下料长度（182 ± 1 mm）一致
import yaml                                                          # noqa: E402
from _ch23 import ROOT                                               # noqa: E402
proc = yaml.safe_load((ROOT / "factory" / "digital" / "std" / "SH-301_process.yaml").read_text(encoding="utf-8"))
L_saw = float(proc["blank"]["length_mm"])
assert proc["blank"]["material_item"] == "RM-45-D50" and abs(L_b * 1000 - L_saw) < 1.0
L_fin = float(sum(s[1] for s in proc["part"]["segments"]))          # 成品轴总长（图纸 C12：167 mm）

# ---------------------------------------------------------------- (4) 算例 23.1.4：夹偏的毛坯
alpha = math.radians(1.0)
n_rpm = 1200.0
w = n_rpm * 2 * math.pi / 60
Rx = rotx(alpha)
I_s = Rx @ Ic @ Rx.T                                               # 主轴坐标系 {s}（z 沿主轴）中的惯量，式 (3.4.4)
assert abs(I_s[1, 2] - (I_t - I_a) * math.sin(alpha) * math.cos(alpha)) < 1e-15
Lw = I_s @ np.array([0, 0, w])
beta = math.degrees(math.acos(Lw[2] / np.linalg.norm(Lw)))         # L 与 ω 的夹角
M_dyn = w * w * abs(I_t - I_a) * math.sin(alpha) * math.cos(alpha)
assert abs(M_dyn - np.linalg.norm(np.cross([0, 0, w], Lw))) < 1e-12
e_ecc = 0.1e-3
F_stat = m_b * e_ecc * w * w

# MuJoCo：同一根毛坯夹偏 1° 装在竖直的铰链上自由转动（无摩擦、无驱动），读铰链处的约束力矩（torque 传感器）
q = (math.cos(alpha / 2), math.sin(alpha / 2), 0, 0)
xml = (f'<mujoco><option timestep="0.0002" integrator="RK4" gravity="0 0 -9.81"/><worldbody>'
       f'<body name="spindle" pos="0 0 0.5"><joint name="spin" type="hinge" axis="0 0 1"/><site name="s"/>'
       f'<geom type="sphere" size="0.005" mass="1e-9" contype="0" conaffinity="0"/>'
       f'<body name="blank" quat="{q[0]} {q[1]} {q[2]} {q[3]}"><geom type="cylinder" size="{r_b} {L_b / 2}" mass="{m_b}" contype="0" conaffinity="0"/></body>'
       f'</body></worldbody><sensor><torque site="s"/></sensor></mujoco>')
mj, mm, dd = mj_load(xml)
dd.qvel[0] = w
tq = []
for _ in range(2500):                                               # 0.5 s，主轴转 10 圈
    mj.mj_step(mm, dd)
    tq.append(np.linalg.norm(dd.sensordata[:3]))
tq = np.array(tq)
M_mj = float(tq.mean())
assert abs(tq.max() - tq.min()) < 1e-9 * M_dyn and abs(M_mj / M_dyn - 1) < 1e-9     # 在转动的主轴坐标系中力矩不变
assert abs(dd.qvel[0] / w - 1) < 1e-12                               # 绕主轴的转速不变（主轴方向没有力矩）

# ---------------------------------------------------------------- 实验 23.1 的阈值（lab23_1.js 的同一个模型）
def lab_spindle(alpha_deg, ecc_mm, n):
    a, e = math.radians(alpha_deg), ecc_mm / 1000
    xml = (f'<mujoco><option timestep="0.0002" integrator="RK4"/><worldbody><body name="spindle" pos="0 0 0.5">'
           f'<joint name="spin" type="hinge" axis="0 0 1"/><site name="s"/>'
           f'<geom type="cylinder" size="0.08 0.03" pos="0 0 -0.09" mass="0.000001" contype="0" conaffinity="0"/>'
           f'<geom type="box" size="0.012 0.03 0.02" pos="0.07 0 -0.04" mass="0" contype="0" conaffinity="0"/>'
           f'<body name="blank" pos="{e} 0 0" quat="{math.cos(a / 2)} {math.sin(a / 2)} 0 0">'
           f'<geom type="cylinder" size="0.025 {0.1816597 / 2}" mass="2.8" contype="0" conaffinity="0"/>'
           f'<geom type="box" size="0.003 0.026 0.091" mass="0" contype="0" conaffinity="0"/></body>'
           f'</body></worldbody><sensor><torque site="s"/><force site="s"/></sensor></mujoco>')
    mj, mm, dd = mj_load(xml)
    dd.qvel[0] = n * 2 * math.pi / 60
    for _ in range(1500):
        mj.mj_step(mm, dd)
    q = dd.sensordata
    return math.hypot(q[0], q[1]), math.hypot(q[3], q[4])


assert abs(0.1816597 - L_b) < 1e-7                                   # 实验程序里写的毛坯长度
w12 = 1200 * 2 * math.pi / 60
lab_pred = lambda al: w12 ** 2 * abs(I_t - I_a) * math.sin(math.radians(al)) * math.cos(math.radians(al))
M0, F0 = lab_spindle(0, 0, 1200)
M45, _ = lab_spindle(45, 0, 1200)
M90, _ = lab_spindle(90, 0, 1200)
_, F1 = lab_spindle(0, 1.0, 1200)
assert M0 < 1e-6 and F0 < 1e-6 and M90 < 1e-6                       # 任务 1、3
assert abs(M45 / lab_pred(45) - 1) < 1e-3                            # 任务 2（阈值 0.5%）；标记用的极小质量带来 ~1e-6 的差别
assert abs(F1 / (m_b * 1e-3 * w12 ** 2) - 1) < 1e-3                  # 任务 4（阈值 1%）
xmlw = ('<mujoco><option timestep="0.0002" integrator="RK4"/><worldbody><body name="drum" pos="0 0 0.55">'
        '<joint name="spin" type="hinge" axis="0 0 1"/><site name="s"/>'
        '<geom type="cylinder" size="0.25 0.175" mass="5" contype="0" conaffinity="0"/>'
        '<geom type="box" size="0.25 0.01 0.17" mass="0" contype="0" conaffinity="0"/>'
        '<geom type="sphere" size="0.07" pos="0.2 0 0" mass="0.5" contype="0" conaffinity="0"/>'
        '</body></worldbody><sensor><torque site="s"/><force site="s"/></sensor></mujoco>')
mj, mm, dd = mj_load(xmlw)
dd.qvel[0] = 510 * 2 * math.pi / 60
for _ in range(1500):
    mj.mj_step(mm, dd)
F_wash = math.hypot(dd.sensordata[3], dd.sensordata[4])
assert 270 < F_wash < 300                                            # 任务 5 的演示：510 r/min

# ---------------------------------------------------------------- (5) 习题答案
# 23.1.2：算例 3.4.2 的板；23.1.5：最大力矩在 α = 45°
M45 = w * w * abs(I_t - I_a) * 0.5
al = np.linspace(0, math.pi / 2, 9001)
assert abs(al[np.argmax(np.sin(al) * np.cos(al))] - math.pi / 4) < 1e-3

out(m_b=m_b, r_b=r_b, L_b=L_b, L_b_mm=L_b * 1000, I_t=I_t, I_a=I_a, ratio_ta=I_t / I_a,
    I_t3=I_t * 1e3, I_a3=I_a * 1e3, I_mj=tex(np.array(I_mj) * 1e3, 5), err_grid=err_grid, err_mj=err_mj, n_cells=nr * nphi * nz,
    y_top=y_top, y_blank=y_blank, m_tot=m_tot, y_c=y_c,
    eq_rows=r" \\ ".join(rows), tri_min=tri_min, ua_m=ua.m, ua_c=ua.ipos[2],
    w=w, I_s=tex(I_s * 1e3, 5), Iyz=I_s[1, 2] * 1e6, beta=beta, M_dyn=M_dyn, M_mj=M_mj, F_stat=F_stat, f_hz=n_rpm / 60,
    plate=tex(plate * 1e3, 4), M45=M45, F_wash=F_wash, lab_M45=M45, L_saw=L_saw, L_fin=L_fin, m_fin=float(proc["part"]["mass_kg"]))
