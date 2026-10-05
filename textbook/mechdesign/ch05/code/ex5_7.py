"""5.7 选材方法：阿什比选材图（E–ρ）与性能指数；协作机器人小臂的轻量化选材（算例 5.7.1，图 5.7.1、5.7.2）。

小臂按悬臂梁算：长度取零件库 UR5e 模型（MJCF：肘关节到腕关节 1 的距离），末端载荷 = 三个腕部连杆的质量（同一模型）+ 负载
（第 33.10 节的 4 kg），并计入管子自重。外径受关节尺寸限制（本书设定 75 mm），壁厚自由，加各材料的最小壁厚约束（本书设定）；
末端由小臂弯曲引起的挠度分配 0.10 mm（本书设定）。"""
import math
import os
import re
from pathlib import Path

import numpy as np

import _cfrp
import _ch5 as H
from bookout import T, figure, out, style

G = 9.81
MJCF = Path(os.environ.get("WQ_MENAGERIE", "/opt/menagerie")) / "universal_robots_ur5e" / "ur5e.xml"
xml = MJCF.read_text(encoding="utf-8")


def body_block(name):
    i = xml.index(f'<body name="{name}"')
    return xml[i:i + 400]


L = float(re.search(r'pos="0 0 ([0-9.]+)"', body_block("wrist_1_link")).group(1))          # 小臂长 m
m_wrist = sum(float(re.search(r'mass="([0-9.]+)"', body_block(b)).group(1)) for b in ("wrist_1_link", "wrist_2_link", "wrist_3_link"))
import _rj                                                                                   # noqa: E402  第 33.10 节的负载
PAYLOAD = _rj.PAYLOAD_KG
F = (m_wrist + PAYLOAD) * G
D = 0.075                     # 外径 m（本书设定）
DELTA = 0.10e-3               # 允许挠度 m（本书设定）
T_MIN = {"steel": 1.0, "al6061": 1.5, "al7075": 1.5, "mg": 2.0, "ti": 1.0, "cfrp": 1.0, "gfrp": 1.0}   # 最小壁厚 mm（本书设定）；塑料的模量太低，薄壁管的公式不再适用，不列入
E_cf, rho_cf = _cfrp.qi_modulus()


def mats():
    out_ = []
    for m in H.materials():
        if m["id"] not in T_MIN:
            continue
        m = dict(m)
        if m["id"] == "cfrp":
            m["E"], m["rho"] = E_cf, rho_cf                    # 由程序 5.5.1 的经典层合理论算出
        out_.append(m)
    return out_


def tube(m):
    """薄壁管（I = πD³t/8，A = πDt）：末端力 F + 自重，挠度 = DELTA 所需的壁厚 t，以及质量"""
    E, rho = m["E"] * 1e9, m["rho"] * 1000
    t_req = (F * L ** 3 / 3) / (math.pi * D / 8 * (DELTA * D * D * E - rho * G * L ** 4))
    t = max(t_req, T_MIN[m["id"]] / 1000)
    mass = rho * math.pi * D * t * L
    I = math.pi * D ** 3 * t / 8
    M = F * L + rho * math.pi * D * t * G * L * L / 2
    s = M * (D / 2) / I / 1e6
    return {"t_req": t_req * 1000, "t": t * 1000, "mass": mass, "mass_free": rho * math.pi * D * t_req * L, "S": m["sy"] / s,
            "idx": m["E"] / m["rho"]}


rows = [(m, tube(m)) for m in mats()]
rows_free = sorted(rows, key=lambda r: r[1]["mass_free"])
rows_min = sorted(rows, key=lambda r: r[1]["mass"])
R = {m["id"]: r for m, r in rows}

# ---------------------------------------------------------------- 图 5.7.1：选材图
plt = style()
fig, ax = plt.subplots(figsize=(6.2, 4.2))
allm = H.materials()
SHORT = {"steel": T("45 钢", "1045"), "ss304": "304", "ci": "HT200", "al6061": "6061", "al7075": "7075", "mg": "AZ31B", "ti": "TC4",
         "cfrp": "CFRP", "gfrp": "GFRP", "pa66": "PA66", "abs": "ABS", "peek": "PEEK", "pa12": "PA12", "wood": T("云杉", "spruce"),
         "alumina": T("氧化铝", "alumina")}
OFFS = {"steel": (-26, 3), "ss304": (5, -9), "al6061": (-26, -8), "al7075": (6, 2), "ci": (6, -6), "abs": (-24, -2), "pa12": (6, -6)}
for m in allm:
    if m["id"] == "cfrp":
        m = dict(m, E=E_cf, rho=rho_cf)
    ax.loglog(m["rho"], m["E"], "o", ms=5, color=H.CLS_COLOR[m["cls"]])
    dx, dy = OFFS.get(m["id"], (5, -2))
    ax.annotate(SHORT[m["id"]], (m["rho"], m["E"]), xytext=(dx, dy), textcoords="offset points", fontsize=6.4, color=H.CLS_COLOR[m["cls"]])
al = H.by_id("al6061")
rr = np.logspace(-0.6, 1.0, 50)
for p, lab in ((1, r"$E/\rho$"), (2, r"$E^{1/2}/\rho$"), (3, r"$E^{1/3}/\rho$")):
    E = al["E"] * (rr / al["rho"]) ** p
    keep = (E > 0.5) & (E < 600)
    ax.loglog(rr[keep], E[keep], color=H.MUTED, lw=0.7, ls="--")
    r0 = {1: 0.42, 2: 0.6, 3: 0.66}[p]                                     # 标注的位置（左下方，避开数据点）
    ax.text(r0, al["E"] * (r0 / al["rho"]) ** p * 1.15, lab, fontsize=7, color=H.MUTED, va="bottom", ha="right")
for c, n in H.CLS_NAME.items():
    ax.plot([], [], "o", color=H.CLS_COLOR[c], label=n)
ax.legend(fontsize=6.4, frameon=False, loc="lower right")
ax.set_xlabel(T("密度 ρ / (g/cm³)", "Density ρ / (g/cm³)"), fontsize=7.5)
ax.set_ylabel(T("弹性模量 E / GPa", "Young's modulus E / GPa"), fontsize=7.5)
ax.set_xlim(0.3, 12)
ax.set_ylim(0.5, 600)
ax.tick_params(labelsize=6.5)
ax.set_title(T("弹性模量–密度选材图（虚线过 6061 铝合金：线上材料性能指数相同）", "Modulus–density chart (dashed lines through 6061: equal index)"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig5_7_1")

# ---------------------------------------------------------------- 图 5.7.2：小臂的质量
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 2.9), sharey=False)
names = [m["name"] for m, _ in rows_min]
y = range(len(rows_min))
a0.barh(list(y), [r["mass_free"] for _, r in rows_min], color="#9ecae1", label=T("只按刚度", "stiffness only"))
a0.barh(list(y), [r["mass"] - r["mass_free"] for _, r in rows_min], left=[r["mass_free"] for _, r in rows_min], color="#d62728",
        label=T("最小壁厚多出的", "added by minimum wall"))
a0.set_yticks(list(y))
a0.set_yticklabels(names, fontsize=6.3)
a0.invert_yaxis()
a0.set_xlabel(T("小臂管身质量 / kg", "Forearm tube mass / kg"), fontsize=7.5)
a0.legend(fontsize=6.2, frameon=False, loc="center right")
a0.set_xlim(0, 0.95)
a0.tick_params(labelsize=6.5)
a0.set_title(T("(a) 外径 75 mm、挠度 0.10 mm", "(a) OD 75 mm, deflection 0.10 mm"), fontsize=7.8)
a1.barh(list(y), [r["idx"] for _, r in rows_min], color="#2ca02c")
a1.set_yticks(list(y))
a1.set_yticklabels([])
a1.invert_yaxis()
a1.set_xlabel(T("E/ρ / (GPa·cm³/g)", "E/ρ / (GPa·cm³/g)"), fontsize=7.5)
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 性能指数 E/ρ（外径固定、壁厚自由）", "(b) Index E/ρ (fixed OD, free wall)"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig5_7_2")

out(L_mm=L * 1000, m_wrist=m_wrist, payload=PAYLOAD, F=F, D_mm=D * 1000, delta_mm=DELTA * 1000, E_cf=E_cf,
    best_free=rows_free[0][0]["name"], best_min=rows_min[0][0]["name"], second_min=rows_min[1][0]["name"],
    **{f"t_{k}": R[k]["t_req"] for k in R}, **{f"m_{k}": R[k]["mass"] for k in R}, **{f"mf_{k}": R[k]["mass_free"] for k in R},
    **{f"S_{k}": R[k]["S"] for k in R}, **{f"i_{k}": R[k]["idx"] for k in R}, **{f"tmin_{k}": T_MIN[k] for k in R},
    **{f"E_{m['id']}": m["E"] for m in mats()}, **{f"rho_{m['id']}": m["rho"] for m in mats()}, **{f"sy_{m['id']}": m["sy"] for m in mats()},
    ratio_steel_al=R["steel"]["mass"] / R["al6061"]["mass"])
