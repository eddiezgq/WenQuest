"""31.4 节的计算：材料与轻量化。

(1) 算例 31.4.1：材料比较。问渠 CAE 材料表（factory/digital/cae/materials.py）里的 6061-T6、7075-T6、Q345、304，加一种碳纤维管
    （Easy Composites 50 mm 卷制碳纤维管的产品页：轴向弹性模量 90 GPa、面内剪切模量 4.6 GPa、密度 1.60 g/cm³、轴向抗拉 750 MPa，
    铺层 [0, 90, 0, 90, 0]）：比刚度 E/ρ、比强度 σ/ρ；外径 90 mm 不变、弯曲刚度与铝管 Ø90×3 相同时要多厚的壁、每米多重、抗扭刚度是多少。
(2) 算例 31.4.2：改截面（铝合金）：Ø90×3（标准）、Ø90×5、Ø100×3、Ø100×2、Ø110×2——大臂的质量、弯曲刚度、负载引起的下沉中大臂弯曲的部分、J2 的重力矩。
(3) 算例 31.4.3：两根管都换成同样弯曲刚度的碳纤维管，整机轻多少、J2 的重力矩小多少：对照关节模组的质量。
(4) 算例 31.4.4：拓扑优化（问渠 CAE 的平面 SIMP，topo.py 的 run_plate）：如果大臂用一块板做，材料用量 30%，左端 J2 的毂固定、
    右端 J3 的毂受向下的力，材料长在哪里。图 31.4.1。
"""
import math

import numpy as np

from _ch31 import G0, Q_OUT, W, deflection, load_points, materials, robot_plant_prices, tube_props
from bookout import COLORS as C, T, figure, out, style

MT = materials()
CF = {"id": "CFRP", "name": "碳纤维管（卷制，0/90 铺层）", "E": 90e9, "G": 4.6e9, "rho": 1600.0, "sig": 750e6}
mats = []
for mid in ("6061-T6", "7075-T6", "Q345", "304"):
    m = MT.get(mid)
    E = m["E_mpa"] * 1e6
    mats.append({"id": mid, "E": E, "G": E / (2 * (1 + m["nu"])), "rho": m["density"] * 1000, "sig": m["yield_mpa"] * 1e6})
mats.append(CF)
# ---------------------------------------------------------------- (1) 材料比较：外径 90 不变、EI 与铝管 Ø90×3 相同
ro = W.TUBES["upper"][0]
al = mats[0]
EI0 = al["E"] * tube_props(*W.TUBES["upper"])["I"]
rows = {}
for m in mats:
    I_need = EI0 / m["E"]
    ri = (ro ** 4 - 4 * I_need / math.pi) ** 0.25           # I = π/4 (ro⁴ − ri⁴)
    t = ro - ri
    A = math.pi * (ro ** 2 - ri ** 2)
    GJ = m["G"] * 2 * math.pi / 4 * (ro ** 4 - ri ** 4)
    rows[m["id"]] = {"E_GPa": m["E"] / 1e9, "rho": m["rho"] / 1000, "spec_E": m["E"] / m["rho"] / 1e6, "spec_s": m["sig"] / m["rho"] / 1e3,
                     "t_mm": t * 1000, "kg_m": A * m["rho"], "GJ_ratio": GJ / (al["G"] * 2 * tube_props(*W.TUBES["upper"])["I"]),
                     "sig_MPa": m["sig"] / 1e6}
for k, v in rows.items():
    tag = k.replace("-", "").replace("6061T6", "al").replace("7075T6", "al7").replace("Q345", "st").replace("304", "ss").replace("CFRP", "cf")
    out(**{f"{tag}_{kk}": vv for kk, vv in v.items()})
assert abs(rows["6061-T6"]["t_mm"] - 3.0) < 1e-9
assert abs(rows["Q345"]["kg_m"] / rows["6061-T6"]["kg_m"] - 1) < 0.1          # 钢和铝的比刚度几乎一样：同样刚度，一样重
assert rows["CFRP"]["kg_m"] < 0.5 * rows["6061-T6"]["kg_m"] and rows["CFRP"]["GJ_ratio"] < 0.3   # 碳纤维轻一半多，但这种铺层抗扭差
out(cf_save=(1 - rows["CFRP"]["kg_m"] / rows["6061-T6"]["kg_m"]) * 100)

# ---------------------------------------------------------------- (2) 改截面（铝）
q = Q_OUT
a2 = abs(W.DH[1]["a"])
pay = load_points(q, self_weight=False)
base = deflection(q, pay, n_sec=100)["upper_bend"][2]
secs = [(90, 3), (90, 5), (100, 3), (100, 2), (110, 2)]
tab = []
for D, t in secs:
    pr = tube_props(D / 2000, t / 1000)
    m_tube = pr["A"] * a2 * W.RHO_AL
    EI = {"upper": W.E_AL * pr["I"], "fore": W.E_AL * tube_props(*W.TUBES["fore"])["I"]}
    dz = -deflection(q, pay, EI=EI, n_sec=100)["upper_bend"][2]
    m0 = tube_props(*W.TUBES["upper"])["A"] * a2 * W.RHO_AL
    dtau = (m_tube - m0) * G0 * a2 / 2                      # 大臂质心在管长一半
    tab.append((D, t, m_tube, pr["I"] / tube_props(*W.TUBES["upper"])["I"], dz * 1e3, dtau))
tab = np.array(tab)
assert abs(tab[0, 4] + base * 1e3) < 1e-9
for k, (D, t, m_t, Ir, dz, dtau) in enumerate(tab):
    out(**{f"s{k}_m": m_t, f"s{k}_I": Ir, f"s{k}_dz": dz, f"s{k}_dtau": dtau})
# Ø110×2 比 Ø90×3 更硬又更轻：直径大、壁薄，材料放在离中性轴远的地方
assert tab[4, 3] > 1.2 and tab[4, 2] < tab[0, 2]

# ---------------------------------------------------------------- (3) 两根管都换碳纤维
m_tubes = sum(tube_props(r, t)["A"] * abs(W.DH[i]["a"]) * W.RHO_AL for i, _, r, t in ((1, 0, *W.TUBES["upper"]), (2, 0, *W.TUBES["fore"])))
out_ratio = 1 - rows["CFRP"]["kg_m"] / rows["6061-T6"]["kg_m"]           # 同样弯曲刚度，碳纤维管轻的比例
save = m_tubes * out_ratio
a3 = abs(W.DH[2]["a"])
m_u = tube_props(*W.TUBES["upper"])["A"] * a2 * W.RHO_AL
m_f = tube_props(*W.TUBES["fore"])["A"] * a3 * W.RHO_AL
dtau2 = out_ratio * G0 * (m_u * a2 / 2 + m_f * (a2 + a3 / 2))
tau2 = abs(W.joint_loads(q, 1)["tau"])
m_mod = sum(W.MODULES[s]["mass"] for s in W.JOINT_MODULE)
out(m_tubes=m_tubes, cf_kg=save, dtau2=dtau2, dtau2_pct=dtau2 / tau2 * 100, m_total=W.total_mass(), m_mod=m_mod,
    save_pct=save / W.total_mass() * 100)
assert save / W.total_mass() < 0.1                         # 整机轻不到一成：大头是关节模组
# 价格的量级：碳纤维管取同一产品页的零售价（Ø50.3×1.4，每米 63.08 英镑），铝管取机器人厂清单的示例价（每千克）
cf_kg_per_m = CF["rho"] * math.pi * ((50.3e-3 / 2) ** 2 - (47.5e-3 / 2) ** 2)
P = robot_plant_prices()
out(cf_gbp_kg=63.08 / cf_kg_per_m, al_usd_kg=P["RM-AL-TUBE-D90"])

# ---------------------------------------------------------------- (4) 拓扑优化
from _ch31 import CAE  # noqa: E402
import sys  # noqa: E402
sys.path.insert(0, str(CAE.parent))
from cae import topo as TO  # noqa: E402
L = a2 * 1000
spec = {"domain": [[-40, -50], [L + 40, -50], [L + 40, 50], [-40, 50]], "support": [0, 0, 28], "load": {"at": [L, 0, 24], "f": [0, -120]},
        "cell_mm": 5}
r = TO.run_plate(spec, volfrac=0.3)
dens = np.asarray(r["density"])
assert r["converged"]
# 材料长在上下两边：两毂之间（x = 100–300 mm），离中线最远的上下各四分之一高度里的材料占了一半以上
ny = dens.shape[0]
c, (x0, y0) = r["plate"]["cell_mm"], r["plate"]["origin"]
mid = dens[:, int((100 - x0) / c): int((300 - x0) / c)]
edge = np.r_[mid[: ny // 4], mid[-(ny // 4):]].sum() / mid.sum()
assert edge > 0.5
out(topo_vol=30, topo_iter=r["iterations"], topo_edge=edge * 100, topo_nx=dens.shape[1], topo_ny=ny)

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(12.0, 3.9), gridspec_kw={"width_ratios": [1.0, 1.25]})
ax = axs[0]
names = {"6061-T6": T("6061-T6 铝", "6061-T6 Al"), "7075-T6": T("7075-T6 铝", "7075-T6 Al"), "Q345": T("Q345 钢", "Q345 steel"),
         "304": T("304 不锈钢", "304 stainless"), "CFRP": T("碳纤维管", "CFRP tube")}
for k, v in rows.items():
    ax.scatter(v["spec_E"], v["spec_s"], s=60, color=C["z"] if k != "CFRP" else C["x"], zorder=3)
    ax.annotate(names[k], (v["spec_E"], v["spec_s"]), xytext=(6, -12 if k == "304" else 4), textcoords="offset points", fontsize=8)
ax.set_xlabel(T("比刚度 E/ρ / (MJ/kg)", "specific stiffness E/ρ / (MJ/kg)"))
ax.set_ylabel(T("比强度 σ/ρ / (kJ/kg)", "specific strength σ/ρ / (kJ/kg)"))
ax.set_xlim(0, 65)
ax.set_ylim(0, 520)
ax.set_title(T("(a) 比刚度与比强度", "(a) specific stiffness and strength"), fontsize=11)
ax = axs[1]
ax.imshow(dens, cmap="Greys", vmin=0, vmax=1, extent=[x0, x0 + dens.shape[1] * c, y0, y0 + dens.shape[0] * c], origin="upper")
ax.add_patch(plt.Circle((0, 0), 28, fill=False, color=C["z"], lw=1.5))
ax.add_patch(plt.Circle((L, 0), 24, fill=False, color=C["x"], lw=1.5))
ax.annotate("", xy=(L, -45), xytext=(L, 5), arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.6))
ax.text(0, 58, T("J2 毂（固定）", "J2 hub (fixed)"), ha="center", fontsize=8, color=C["z"])
ax.text(L, 58, T("J3 毂（受力）", "J3 hub (loaded)"), ha="center", fontsize=8, color=C["x"])
ax.set_ylim(-60, 72)
ax.set_aspect("equal")
ax.set_xlabel("mm")
ax.set_title(T("(b) 大臂做成一块板：材料用量 30% 的拓扑优化", "(b) the upper arm as a plate: topology optimisation, 30 % material"), fontsize=11)
fig.tight_layout()
figure(fig, "fig31_4_1")
