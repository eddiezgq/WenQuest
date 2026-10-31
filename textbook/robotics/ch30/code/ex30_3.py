"""30.3 节的计算：尺寸综合。

(1) 式 (30.3.1)～(30.3.3)（工具朝下时关节 4 轴上那一点 P4 的位置、够得着的条件）与正运动学核对：工位的 12 个点，两种手腕。
(2) 算例 30.3.1：臂展 0.86 m 不变（a2 + a3 = 0.76 m），大臂、小臂怎样分：各种分法下 J2、J3 的最大重力矩（带 5 kg 负载，
    关节模组按标准 WQ-CR5）和肩部死区 |a2 − a3|；死区小于 J1 模组的半径时落在机器人自己身上。
(3) 算例 30.3.2：关节模组的选择（factory/digital/cae/wqcr5.py 的 design()，与配置器的协作臂模板同一段代码）：
    最大重力矩、最大惯量 → 峰值需求；标准动作的均方根 → 连续需求；能力与利用率；J1、腕部的“通用”规则。
(4) 算例 30.3.3：重量预算：各构件、各类零件的质量。
(5) 算例 30.3.4：刚度初估：手臂水平伸直、带 5 kg 负载时，两根铝管弯曲让 TCP 下沉多少（关节当作刚性）。
"""
import math

import numpy as np

from _ch30 import G0, TOOL, cr_dh, fk, ik_down, reach_margin, station_points, wqcr5, wrist_points
from bookout import out

W = wqcr5()
dh = cr_dh()
# ---------------------------------------------------------------- (1) 公式核对
err = 0.0
for _, _, r, z in station_points():
    for outward in (True, False):
        q = ik_down(r, z, dh, outward=outward)
        if q is None:
            continue
        T, P, tcp = fk(q, dh, TOOL)
        err = max(err, abs(math.hypot(tcp[0], tcp[1]) - r), abs(tcp[2] - z), abs(T[2, 2] + 1))
        p4 = P[3]                                              # 坐标系 {3} 的原点：在 J4 轴上、手臂平面里，就是 P4
        x, y = wrist_points(r, z, dh)[0 if outward else 1]
        err = max(err, abs(math.hypot(p4[0], p4[1]) - x), abs(p4[2] - dh[0]["d"] - y))
assert err < 1e-12
out(err_formula=err)

# ---------------------------------------------------------------- (2) 大臂、小臂怎样分
S = abs(W.DH[1]["a"]) + abs(W.DH[2]["a"])
rows = []
for a2 in np.round(np.arange(0.30, 0.501, 0.02), 3):
    a3 = round(S - a2, 3)
    with W.geometry(a2, a3):
        g, _ = W.worst_case(W.PAYLOAD_KG, step_deg=45.0)
    rows.append((a2, a3, g[1], g[2], abs(a2 - a3)))
rows = np.array(rows)
r_mod = W.MODULES["L"]["r"]
std = rows[np.argmin(np.abs(rows[:, 0] - 0.40))]
lo, hi = rows[0], rows[-1]
assert hi[2] > lo[2] and hi[3] < lo[3] and std[4] < r_mod
out(S=S, g2_lo=lo[2], g2_hi=hi[2], g3_lo=lo[3], g3_hi=hi[3], a2_lo=lo[0], a2_hi=hi[0], g2_std=std[2], g3_std=std[3],
    dz_std=std[4] * 100, r_mod_cm=r_mod * 100, d_g2=(hi[2] - lo[2]) / lo[2] * 100, d_g3=(lo[3] - hi[3]) / lo[3] * 100,
    dead_rule=W.DEAD_ZONE * 100)

# ---------------------------------------------------------------- (3) 模组选择
d = W.design()
J = d["joints"]
assert d["standard"] and J[0]["own"] == "WQJ-M"
cap = {s: W.capacity(s) for s in "SML"}
out(**{f"g{j + 1}": J[j]["g_max"] for j in range(6)}, **{f"M{j + 1}": J[j]["M_max"] for j in range(6)},
    **{f"np{j + 1}": J[j]["need_peak"] for j in range(6)}, **{f"nr{j + 1}": J[j]["need_rms"] for j in range(6)},
    **{f"up{j + 1}": J[j]["use_peak"] * 100 for j in range(6)}, **{f"ur{j + 1}": J[j]["use_rms"] * 100 for j in range(6)},
    capL_p=cap["L"]["peak"], capL_r=cap["L"]["rated"], capM_p=cap["M"]["peak"], capM_r=cap["M"]["rated"],
    capS_p=cap["S"]["peak"], capS_r=cap["S"]["rated"], safety=W.SAFETY, ratio=W.GEAR_RATIO, eta=W.ETA,
    j1_own_use=J[0]["need_rms"] / cap["M"]["rated"] * 100, hold2=J[1]["g_max"] / cap["L"]["rated"] * 100,
    hold3=J[2]["g_max"] / cap["M"]["rated"] * 100)

# ---------------------------------------------------------------- (4) 重量预算
L = W.links()
m_mod = sum(W.MODULES[s]["mass"] for s in W.JOINT_MODULE)
m_base_fixed = W.base_mass() - W.MODULES["L"]["mass"]
m_total = W.total_mass()
m_parts = {}
for i in range(6):
    for name, p, _ in W.link_parts(i):
        key = "模组" if "模组" in name else ("铝管" if "铝管" in name else "壳体、法兰、线缆")
        m_parts[key] = m_parts.get(key, 0.0) + p["mass"]
m_parts["模组"] += W.MODULES["L"]["mass"]                         # J1 的模组在底座里
assert abs(sum(m_parts.values()) + m_base_fixed - m_total) < 1e-9
out(m_total=m_total, m_mod=m_mod, mod_share=m_mod / m_total * 100, m_tube=m_parts["铝管"], m_shell=m_parts["壳体、法兰、线缆"],
    m_base=m_base_fixed, m_moving=sum(l["mass"] for l in L))

# ---------------------------------------------------------------- (5) 铝管的弯曲
E = 69e9
def I_tube(ro, t):
    ri = ro - t
    return math.pi / 4 * (ro ** 4 - ri ** 4)
(ru, tu), (rf, tf) = W.TUBES["upper"], W.TUBES["fore"]
a2, a3, d5 = abs(W.DH[1]["a"]), abs(W.DH[2]["a"]), W.DH[4]["d"]
# 手臂水平伸直：从 J2 起沿 x，点载荷（N）与位置（m）：J3 模组在 a2；腕部三个模组、连接件、法兰、负载近似都在小臂末端 a2 + a3
F_elbow = G0 * W.MODULES["M"]["mass"]
m_tip = 3 * W.MODULES["S"]["mass"] + 0.2 + 0.2 + 0.35 + W.PAYLOAD_KG
F_tip = G0 * m_tip
q_u = G0 * (W.RHO_AL * math.pi * (ru ** 2 - (ru - tu) ** 2) + 0.3 / a2)      # 大臂：铝管 + 罩壳，均布
q_f = G0 * (W.RHO_AL * math.pi * (rf ** 2 - (rf - tf) ** 2) + 0.2 / a3)
xs = np.linspace(0, a2 + a3, 4001)
Mx = np.zeros_like(xs)
Lt = a2 + a3
for k, x in enumerate(xs):                                     # 截面 x 处的弯矩（取 x 以外的部分）
    m = F_tip * (Lt - x)
    if x < a2:
        m += F_elbow * (a2 - x) + q_u * (a2 - x) ** 2 / 2 + q_f * a3 * (a2 + a3 / 2 - x)
    else:
        m += q_f * (Lt - x) ** 2 / 2
    Mx[k] = m
EI = np.where(xs < a2, E * I_tube(ru, tu), E * I_tube(rf, tf))
kappa = Mx / EI
theta = np.concatenate([[0], np.cumsum((kappa[1:] + kappa[:-1]) / 2 * np.diff(xs))])
w = np.concatenate([[0], np.cumsum((theta[1:] + theta[:-1]) / 2 * np.diff(xs))])
defl = w[-1] + theta[-1] * d5                                  # 再到 TCP：小臂末端的转角乘腕部偏距
assert 0.05e-3 < defl < 1e-3
out(E_GPa=E / 1e9, defl_mm=defl * 1000, M_root=Mx[0], m_tip=m_tip, tube_u_mm=2000 * ru, tube_u_t=1000 * tu, tube_f_mm=2000 * rf,
    tube_f_t=1000 * tf, rep_ratio=defl * 1000 / 0.03)
