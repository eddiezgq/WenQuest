"""33.8 节：轴的有限元校核与疲劳寿命。

算例 33.8.1  整根 B 版轴（带各处圆角，不含键槽）的有限元：两轴承位限制径向位移（A 兼限轴向），齿轮位受齿轮力和
             转矩，轴端限制转动。表面冯·米塞斯应力沿轴线的分布，与梁理论名义应力对照（图 33.8.1）；
算例 33.8.2  用跑合试验台的转矩记录（数字工厂仿真车间同一个函数生成）做雨流计数，按数字工厂“仿真与分析”的
             同一套疲劳程序（pyLife）算寿命：圆角处用有限元应力；外伸段键槽用名义应力加有效应力集中系数；
算例 33.8.3  45 钢与 40Cr、要求寿命 10 000 h 的结论；起停频率对寿命的影响。
图 33.8.2    转矩记录与雨流计数结果。
"""
import math
import sys
from pathlib import Path

import numpy as np

import _draw as D
import _fea
import _shaft as S
from bookout import T, figure, out, style
import mdstd

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "factory" / "digital"))
from cae import fatigue as FAT, materials as MATS  # noqa: E402

Ft, Fr = S.gear_forces()
# 轴承：只在轴承中心 ±1 mm 的一圈限制径向位移（近似铰支，不约束截面转动）；齿轮力和转矩加在键长范围内（离开两端圆角）
seats = {"A": (S.Z_BRG_A - 1, S.Z_BRG_A + 1), "B": (S.Z_BRG_B - 1, S.Z_BRG_B + 1),
         "gear": (S.Z_GEAR - 22.5, S.Z_GEAR + 22.5), "cpl": (S.LEN_B - 20, S.LEN_B)}
rows, n_el, reac = _fea.shaft_fea(S.LAY_B, S.FILLET_B, seats, (Ft, Fr), S.T_RATED, h=5.0, fine_r=2)
zz, rr, th, vm = rows.T
keep = (zz > 2) & (zz < S.LEN_B - 25)                  # 反向转矩的作用处（轴端 20 mm）不看
outer = keep & (rr > np.array([S.diameter_at(min(max(z, 0), S.LEN_B)) for z in zz]) / 2 - 0.05)

# 梁理论名义应力（冯·米塞斯合成），与 33.4 节相同：转矩在齿轮中点一次传入
zs = np.linspace(0, S.LEN_B, 977)
def nominal(z):
    d = S.diameter_at(z)
    return math.sqrt((S.M_total(z) / S.W_solid(d)) ** 2 + 3 * (S.torque_at(z) / S.WT_solid(d)) ** 2)
vn = np.array([nominal(z) for z in zs])

def peak_near(z0, w=2.5):
    m = keep & (abs(zz - z0) < w)
    return float(vm[m].max())
hot = {k: peak_near(S.SECTIONS[k]["z"]) for k in ("II", "III")}
hot["IV_fillet"] = peak_near(172.0)
# 弯曲的核对：两个轴承环的支反力与 33.4 节的手算（有限元里支反力是作用在轴上的，方向与齿轮力相反）
RA_fe, RB_fe = float(np.hypot(*reac[0][:2])), float(np.hypot(*reac[1][:2]))
RA_hand, RB_hand = math.hypot(*[S.reactions(F)[0] for F in (Ft, Fr)]), math.hypot(*[S.reactions(F)[1] for F in (Ft, Fr)])
err_RA, err_RB = (RA_fe - RA_hand) / RA_hand * 100, (RB_fe - RB_hand) / RB_hand * 100
ext = keep & (zz > 182) & (zz < 210) & outer
vm_ext = float(np.median(vm[ext]))
vm_ext_nom = math.sqrt(3) * S.T_RATED / S.WT_solid(30)
err_ext = (vm_ext - vm_ext_nom) / vm_ext_nom * 100

# ---- 疲劳寿命
series, rate, rated = S.torque_series()
block_s = len(series) / rate
cyc = FAT.rainflow(series)
eps30 = mdstd.size_factor(30)
f4 = S.fatigue_factors(S.SECTIONS["IV"], mdstd.material(S.MAT), "ground")
lives = {}
for mid in ("45-QT", "40Cr-QT"):
    m = MATS.get(mid)
    _, s_fil = FAT.compute(vm[keep & (zz > 60)], rated, series, block_s, m, surface="ground", size_factor=mdstd.size_factor(35), kf=1.0)
    _, s_key = FAT.compute(np.array([vm_ext]), rated, series, block_s, m, surface="ground", size_factor=eps30, kf=f4["k_t"])
    lives[mid] = (s_fil, s_key)
life = lambda s: math.inf if s["infinite"] else s["life_hours"]
# 起停大循环（变程最大的三个）占外伸段键槽每块损伤的比例
sk = lives["45-QT"][1]
big_share = sum(1 / c["N"] for c in sk["hot_cycles"][:3] if c["N"]) / sk["damage_per_block"] * 100
L45_fil, L45_key = life(lives["45-QT"][0]), life(lives["45-QT"][1])
L40_fil, L40_key = life(lives["40Cr-QT"][0]), life(lives["40Cr-QT"][1])
starts_per_h_test = 3 * 3600 / block_s               # 记录里每 25 s 一次起停
# 起停频率的影响：每小时 N 次起停时，损伤只来自起停（运行中的小波动低于疲劳极限的部分很少）——按损伤与起停次数成正比换算
def life_at(starts_per_h, L_test):
    return L_test * starts_per_h_test / starts_per_h
L45_key_10ph = life_at(10, L45_key)
big = cyc[np.argsort(-cyc[:, 0])][:3]

plt = style()
fig, ax = plt.subplots(figsize=(8.0, 3.4))
m = outer
ax.scatter(zz[m], vm[m], s=2, color=D.MOMENT, alpha=0.35, lw=0, label=T("有限元：表面节点", "FEA: surface nodes"))
ax.plot(zs, vn, color=D.INK, lw=1.4, label=T("梁理论名义应力", "beam theory, nominal"))
for k, z0 in (("II", 90.0), ("III", 115.0), ("IV", 172.0)):
    v = hot[k if k != "IV" else "IV_fillet"]
    ax.annotate(f"{k}: {v:.0f}", (z0, v), (z0 + 6, v + 25), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.7))
ax.set_xlabel("z / mm")
ax.set_ylabel(T("冯·米塞斯应力 / MPa", "von Mises stress / MPa"))
ax.set_ylim(0, 240)
ax.legend(fontsize=8.5, frameon=False, loc="upper left", markerscale=4)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_8_1")

fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.0), gridspec_kw={"width_ratios": [2.2, 1]})
t = np.arange(len(series)) / rate
axs[0].plot(t, series, color=D.TORQUE, lw=0.9)
axs[0].axhline(rated, color=D.MUTED, lw=0.8, ls="--")
axs[0].text(74, rated + 12, T("额定 350 N·m", "rated 350 N·m"), ha="right", fontsize=8.5, color=D.MUTED)
axs[0].set_xlabel("t / s"); axs[0].set_ylabel(T("转矩 / N·m", "torque / N·m"))
axs[1].scatter(cyc[:, 1], cyc[:, 0] * 2, s=10, color=D.TORQUE, alpha=0.6)
axs[1].set_xlabel(T("平均值 / N·m", "mean / N·m")); axs[1].set_ylabel(T("变程 / N·m", "range / N·m"))
axs[1].set_title(T(f"雨流计数：每块 {len(cyc)} 个循环", f"rainflow: {len(cyc)} cycles per block"), fontsize=9.5)
for a in axs:
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_8_2")

fmt = lambda x: None if not math.isfinite(x) else x
r3 = lambda x: None if not math.isfinite(x) else float(f"{x:.3g}")   # 寿命只看量级：三位有效数字
out(n_el=n_el, hot_II=hot["II"], hot_III=hot["III"], hot_IV=hot["IV_fillet"], vm_ext=vm_ext, vm_ext_nom=vm_ext_nom,
    err_ext=err_ext, Kfe_II=hot["II"] / nominal(89.99), Kfe_III=hot["III"] / nominal(115.01), Kfe_IV=hot["IV_fillet"] / vm_ext_nom,
    RA_fe=RA_fe, RB_fe=RB_fe, RA_hand=RA_hand, RB_hand=RB_hand, err_RA=err_RA, err_RB=err_RB, big_share=big_share, beta_fac=FAT.SURFACE["ground"][0],
    block_s=block_s, n_cycles=len(cyc), T_max=float(series.max()), T_mean=float(series.mean()),
    big_amp=float(big[0, 0]), big_mean=float(big[0, 1]), kt_IV=f4["k_t"], eps30=eps30,
    L45_fil=fmt(L45_fil), L45_key=fmt(L45_key), L40_fil=fmt(L40_fil), L40_key=fmt(L40_key),
    L45_fil_inf=not math.isfinite(L45_fil), L40_key_ok=L40_key >= S.LIFE_H if math.isfinite(L40_key) else True,
    L45_key_ok=L45_key >= S.LIFE_H, life_req=S.LIFE_H, starts_test=starts_per_h_test, L45_key_10ph=L45_key_10ph,
    SD45=lives["45-QT"][1]["S_D"], SD40=lives["40Cr-QT"][1]["S_D"],
    L45_fil_r=r3(L45_fil), L45_key_r=r3(L45_key), L40_key_r=r3(L40_key), L40_fil_big=(not math.isfinite(L40_fil)) or L40_fil > 1e6,
    L45_key_10ph_w=L45_key_10ph / 1e4)
