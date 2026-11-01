"""31.2 节的计算：刚度与变形。

(1) 与第 30 章算例 30.3.4 核对：按 30.3.4 的集中载荷（肘部 J3 模组、末端的腕部 + 负载、两根管和罩壳均布），本节“小转角 × 力臂”的方法
    算出的铝管弯曲下沉与 30.3.4 沿梁积分两次的结果一致；再按各零件的真实位置算一遍。
(2) 算例 31.2.1：加上 5 kg 负载，TCP 又下沉多少：六个关节（谐波减速器的扭转刚度，零件库 D-RDC-HD-CSF：K1 最软、K3 最硬）、
    两根管的弯曲和扭转，各占多少；关节部分与 C_x = J C_θ Jᵀ 核对。
(3) 整机自重 + 负载的总下沉（标定要处理的量）。
(4) 算例 31.2.2：手臂伸到不同远处（工具朝下），TCP 竖直方向的刚度 k_z = 1 / C_zz 怎样变。
"""
import math

import numpy as np

from _ch31 import G0, Q_OUT, W, deflection, harmonic_stiffness, joint_K, joint_compliance_x, load_points, tcp_point, tube_props
from bookout import out

q = Q_OUT
E = W.E_AL
# ---------------------------------------------------------------- (1) 与 30.3.4 核对
(ru, tu), (rf, tf) = W.TUBES["upper"], W.TUBES["fore"]
a2, a3, d5 = abs(W.DH[1]["a"]), abs(W.DH[2]["a"]), W.DH[4]["d"]
F_elbow = W.MODULES["M"]["mass"]
m_tip = 3 * W.MODULES["S"]["mass"] + 0.2 + 0.2 + 0.35 + W.PAYLOAD_KG
mq_u = W.RHO_AL * math.pi * (ru ** 2 - (ru - tu) ** 2) + 0.3 / a2       # kg/m
mq_f = W.RHO_AL * math.pi * (rf ** 2 - (rf - tf) ** 2) + 0.2 / a3
Tw = W.link_world(q)
o2 = Tw[1][:3, 3]
ax = -np.array([1.0, 0, 0])                                     # 伸直：沿底座 −x
n = 400
pts = [(1, F_elbow, o2 + a2 * ax, False), (5, m_tip, o2 + (a2 + a3) * ax, False)]
pts += [(1, mq_u * a2 / n, o2 + (k + 0.5) / n * a2 * ax, True) for k in range(n)]
pts += [(2, mq_f * a3 / n, o2 + (a2 + (k + 0.5) / n * a3) * ax, True) for k in range(n)]
EI = {"upper": E * tube_props(ru, tu)["I"], "fore": E * tube_props(rf, tf)["I"]}
EI30 = {"upper": 69e9 * tube_props(ru, tu)["I"], "fore": 69e9 * tube_props(rf, tf)["I"]}   # 30.3.4 取 E = 69 GPa
d30 = deflection(q, pts, EI=EI30, n_sec=400, target=o2 + (a2 + a3 + d5) * ax)
sag30 = -(d30["upper_bend"] + d30["fore_bend"])[2]
# 30.3.4 的做法：弯矩 M(x)，两次积分曲率 M/EI，再加末端转角 × d5（逐行照抄程序 30.3.1）
xs = np.linspace(0, a2 + a3, 4001)
Lt = a2 + a3
Mx = np.array([G0 * m_tip * (Lt - x) + (G0 * F_elbow * (a2 - x) + G0 * mq_u * (a2 - x) ** 2 / 2 + G0 * mq_f * a3 * (a2 + a3 / 2 - x)
                                        if x < a2 else G0 * mq_f * (Lt - x) ** 2 / 2) for x in xs])
EIx = np.where(xs < a2, EI30["upper"], EI30["fore"])
kap = Mx / EIx
th = np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(xs))])
w = np.concatenate([[0], np.cumsum((th[1:] + th[:-1]) / 2 * np.diff(xs))])
sag_int = w[-1] + th[-1] * d5
assert abs(sag30 / sag_int - 1) < 2e-3, (sag30, sag_int)
dfull = deflection(q, load_points(q), n_sec=200)
sag_real = -(dfull["upper_bend"] + dfull["fore_bend"])[2]
out(sag30=sag30 * 1e3, sag_int=sag_int * 1e3, sag_real=sag_real * 1e3, sag_up=(sag_real / sag30 - 1) * 100)

# ---------------------------------------------------------------- (2) 只加负载
Kh = harmonic_stiffness()
res = {}
for tag, which in (("k1", 0), ("k3", 2)):
    d = deflection(q, load_points(q, self_weight=False), K=joint_K(which), n_sec=200)
    res[tag] = d
    z = {k: -v[2] * 1e3 for k, v in d.items()}
    tot = sum(z.values())
    joints = sum(z[j] for j in W.JOINTS)
    out(**{f"{tag}_{k}": v for k, v in z.items()}, **{f"{tag}_tot": tot, f"{tag}_joint": joints, f"{tag}_joint_pct": joints / tot * 100,
                                                       f"{tag}_tube": tot - joints, f"{tag}_j2_pct": z["J2"] / tot * 100,
                                                       f"{tag}_x": sum(v[0] for v in d.values()) * 1e3})
# 关节部分 = J_v C_θ J_vᵀ F
F = np.array([0, 0, -W.PAYLOAD_KG * G0])
dj = sum(res["k1"][j] for j in W.JOINTS)
assert np.allclose(joint_compliance_x(q, joint_K(0)) @ F, dj, atol=1e-12)
K = joint_K(0)
p_t = tcp_point(q)
r2 = abs(p_t[0] - Tw[1][0, 3])                                  # J2 的轴沿 y：力臂是 x 方向的距离
out(K32_1=Kh[32][0] / 1e4, K25_1=Kh[25][0] / 1e4, K17_1=Kh[17][0] / 1e4, K32_3=Kh[32][2] / 1e4, K25_3=Kh[25][2] / 1e4, K17_3=Kh[17][2] / 1e4,
    r2=r2, tau2_pay=W.PAYLOAD_KG * G0 * r2, phi2_amin=math.degrees(W.PAYLOAD_KG * G0 * r2 / K[1]) * 60,
    d2_hand=W.PAYLOAD_KG * G0 * r2 ** 2 / K[1] * 1e3, rep_ratio=res["k1"]["J2"][2] * -1e3 / 0.03)
assert abs(-res["k1"]["J2"][2] - W.PAYLOAD_KG * G0 * r2 ** 2 / K[1]) < 1e-9

# ---------------------------------------------------------------- (3) 自重 + 负载
dz = {k: -v[2] * 1e3 for k, v in dfull.items()}
out(full_tot=sum(dz.values()), full_joint=sum(dz[j] for j in W.JOINTS))

# ---------------------------------------------------------------- (4) 伸到不同远处的竖直刚度（工具朝下）
# 大臂抬起 α、小臂折回 2α（肘部朝上），J4 把手腕转回到工具朝下；α = 0 就是伸直
rows = []
for al in np.radians(np.arange(0.0, 70.1, 5.0)):
    qq = np.array([0, -al, 2 * al, 0, -math.pi / 2, 0.0])
    qq[3] = -(qq[1] + qq[2]) - math.pi / 2
    assert W.link_world(qq)[5][2, 2] < -0.999
    Cx = joint_compliance_x(qq, joint_K(0))
    rows.append((float(np.hypot(*tcp_point(qq)[:2])), 1 / Cx[2, 2]))
rows = np.array(rows)
assert np.all(np.diff(rows[:, 0]) < 0) and np.all(np.diff(rows[:, 1]) > 0)          # 越往回收越硬
k_out = 1 / joint_compliance_x(q, joint_K(0))[2, 2]
out(kz_far=rows[0, 1] / 1e3, kz_near=rows[-1, 1] / 1e3, kz_ratio=rows[-1, 1] / rows[0, 1], r_near=rows[-1, 0], r_far=rows[0, 0],
    k_out=k_out / 1e3)
