"""31.5 节的计算：振动与模态。

(1) 算例 31.5.1：单自由度估算：TCP 竖直方向的刚度 k_z（31.2 节，只计关节）和 TCP 处竖直方向的等效质量 Λ_zz（操作空间惯量
    Λ = (J M⁻¹ Jᵀ)⁻¹ 的对角元），f ≈ √(k/m)/2π。
(2) 算例 31.5.2：关节柔性模型：六个关节各是一根扭簧（谐波减速器的 K1 或 K3），连杆是刚体；K v = ω² M v 求全部固有频率和振型。
    M 不含电机转子（转子在弹簧的另一侧，由伺服锁住）。再按 31.2 节负载引起的下沉中铝管所占的比例修正第一阶（串联弹簧）。
(3) 第一阶频率随负载、随手臂伸出的远近怎样变（图 31.5.1）。
(4) 与伺服的关系：第 29 章出厂位置环（控制器 A）J2 的闭环自然频率 √(kp/M22)（刚性模型，含转子）与结构第一阶之比。
"""
import math

import numpy as np

from _ch31 import G0, Q_OUT, W, deflection, jacobian_v, joint_K, joint_compliance_x, load_points, mass_matrix, modes, tcp_point
from bookout import COLORS as C, T, figure, out, style

q = Q_OUT
K1, K3 = joint_K(0), joint_K(2)
# ---------------------------------------------------------------- (1) 单自由度
M = mass_matrix(q)
J = jacobian_v(q, tcp_point(q))
Lam = np.linalg.inv(J @ np.linalg.inv(M) @ J.T)
kz = 1 / joint_compliance_x(q, K1)[2, 2]
f_sdof = math.sqrt(kz / Lam[2, 2]) / (2 * math.pi)
out(kz=kz / 1e3, Lzz=Lam[2, 2], f_sdof=f_sdof, Lzz_arm=Lam[2, 2] - W.PAYLOAD_KG)

# ---------------------------------------------------------------- (2) 关节柔性模型
f1, V1 = modes(q, K1)
f3, _ = modes(q, K3)
v = V1[:, 0] / np.max(np.abs(V1[:, 0]))
v2 = V1[:, 1] / np.max(np.abs(V1[:, 1]))
assert np.argmax(np.abs(v[1:4])) in (0, 1, 2) and abs(v[0]) < 0.2            # 第一阶：J2、J3、J4 在竖直面里一起点头
assert abs(v2[0]) > 0.5 and max(abs(v2[1]), abs(v2[2])) < 0.2                 # 第二阶：J1 带着整条手臂水平摆
out(**{f"fk1_{i + 1}": f1[i] for i in range(6)}, **{f"fk3_{i + 1}": f3[i] for i in range(6)},
    **{f"v1_{i + 1}": v[i] for i in range(6)}, **{f"v2_{i + 1}": v2[i] for i in range(6)})
# 铝管的柔性：串联弹簧，第一阶频率乘 √(关节下沉 / 总下沉)
d = deflection(q, load_points(q, self_weight=False), K=K1, n_sec=100)
dz = {k: -x[2] for k, x in d.items()}
dj = sum(dz[j] for j in W.JOINTS)
ratio = math.sqrt(dj / sum(dz.values()))
d3 = deflection(q, load_points(q, self_weight=False), K=K3, n_sec=100)
dz3 = {k: -x[2] for k, x in d3.items()}
ratio3 = math.sqrt(sum(dz3[j] for j in W.JOINTS) / sum(dz3.values()))
out(f1c=f1[0] * ratio, f1c3=f3[0] * ratio3, corr=(1 - ratio) * 100)

# ---------------------------------------------------------------- (3) 随负载、随伸出远近
pays = np.arange(0.0, 5.01, 0.5)
fp = np.array([[modes(q, K, m)[0][0] for m in pays] for K in (K1, K3)])
rows = []
for al in np.radians(np.arange(0.0, 70.1, 5.0)):
    qq = np.array([0, -al, 2 * al, 0, -math.pi / 2, 0.0])
    qq[3] = -(qq[1] + qq[2]) - math.pi / 2
    rows.append((float(np.hypot(*tcp_point(qq)[:2])), modes(qq, K1)[0][0], modes(qq, K3)[0][0]))
rows = np.array(rows)
assert np.all(np.diff(fp[0]) < 0) and rows[-1, 1] > rows[0, 1]
out(f_empty=fp[0, 0], f_full=fp[0, -1], f_near=rows[-1, 1], r_near=rows[-1, 0], r_far=rows[0, 0])

# ---------------------------------------------------------------- (4) 与伺服的关系
M_rigid = M + np.diag(W.armature())
w_servo = math.sqrt(W.SERVO_KP[1] / M_rigid[1, 1])
zeta = W.SERVO_KV[1] / (2 * math.sqrt(W.SERVO_KP[1] * M_rigid[1, 1]))
out(kp2=W.SERVO_KP[1], kv2=W.SERVO_KV[1], M22=M_rigid[1, 1], arm2=W.armature()[1], f_servo=w_servo / (2 * math.pi), zeta=zeta,
    sep=f1[0] * ratio / (w_servo / (2 * math.pi)))

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(11.6, 3.9))
ax = axs[0]
ax.plot(pays, fp[0], color=C["x"], lw=1.6, marker="o", ms=3, label=T("K1（小负载区，最软）", "K1 (low-load region, softest)"))
ax.plot(pays, fp[1], color=C["z"], lw=1.6, marker="o", ms=3, label=T("K3（大负载区，最硬）", "K3 (high-load region, stiffest)"))
ax.set_xlabel(T("负载 / kg（手臂水平伸直）", "payload / kg (arm horizontal, outstretched)"))
ax.set_ylabel(T("第一阶固有频率 / Hz", "first natural frequency / Hz"))
ax.set_ylim(0, None)
ax.legend(fontsize=8, frameon=False)
ax.set_title(T("(a) 负载越重，频率越低", "(a) heavier payload, lower frequency"), fontsize=11)
ax = axs[1]
ax.plot(rows[:, 0], rows[:, 1], color=C["x"], lw=1.6, marker="o", ms=3, label="K1")
ax.plot(rows[:, 0], rows[:, 2], color=C["z"], lw=1.6, marker="o", ms=3, label="K3")
ax.set_xlabel(T("TCP 离 J1 轴的水平距离 / m（带 5 kg，工具朝下）", "horizontal distance of the TCP from J1 / m (5 kg, tool down)"))
ax.set_ylabel(T("第一阶固有频率 / Hz", "first natural frequency / Hz"))
ax.set_ylim(0, None)
ax.legend(fontsize=8, frameon=False)
ax.set_title(T("(b) 伸得越远，频率越低", "(b) farther out, lower frequency"), fontsize=11)
fig.tight_layout()
figure(fig, "fig31_5_1")
