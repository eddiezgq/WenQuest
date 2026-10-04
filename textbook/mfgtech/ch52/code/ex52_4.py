"""52.4 节：基本夹紧机构。斜楔的增力比与自锁（图 52.4.1 左）、圆偏心转角与夹紧力（图 52.4.1 右）；
算例 52.4.1 JJ-301-50 的螺旋压板：定扭矩 5 N·m 能给出多大夹紧力，够不够；随手用长扳手拧紧会怎样；压板强度。
算例 52.4.2 圆偏心的自锁与夹紧力。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

FX = M.fx()
fx = M.fixture_data()
cl = fx["clamping"]
an = FX.analyse(fx)
need = an["need"]["W"]
sc = an["screw"]
st = an["strap"]
W_have = an["W_have"]
# 随手用 150 mm 扳手、150 N 的力拧（没有定扭矩）
sc_hand = FX.screw_clamp(150, 150, cl["thread_d"], cl["thread_P"], cl["mu_thread"], cl["mu_end"], cl["r_end"])
W_hand = FX.strap_clamp(sc_hand["W"], cl["l_work"], cl["l_heel"])["W"] * cl["count"]
sc_flat = FX.screw_clamp(cl["hand_force"], cl["wrench"], cl["thread_d"], cl["thread_P"], cl["mu_thread"], cl["mu_end"], 1.0)  # 对照：球头螺杆直接顶压块，端面摩擦半径很小（取 1 mm）
S = cl["strap"]
sig = FX.strap_stress(sc_hand["W"], cl["l_work"], cl["l_heel"], S["b"], S["h"], S["slot_w"])
sig5 = FX.strap_stress(sc["W"], cl["l_work"], cl["l_heel"], S["b"], S["h"], S["slot_w"])
# 斜楔：μ = 0.1，φ = arctan 0.1
phi = math.degrees(math.atan(0.1))
w6 = FX.wedge(100, 6, phi, phi)
w15 = FX.wedge(100, 15, phi, phi)
# 圆偏心：D = 40，e = 2，手柄 100 mm，手力 80 N，μ = 0.1
ec = FX.eccentric(80, 100, 40, 2, 0.1, 0.1, 90)
ec3 = FX.eccentric(80, 100, 40, 3, 0.1, 0.1, 90)
hg = FX.hinge(500, 10, 2)

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7))
al = np.linspace(2, 30, 200)
for mu, col in ((0.1, M.ACCENT), (0.15, M.WARM)):
    ph = math.degrees(math.atan(mu))
    axs[0].plot(al, [FX.wedge(1, a, ph, ph)["i"] for a in al], color=col, lw=1.3, label=f"μ = {mu:g}")
    axs[0].axvline(2 * ph, color=col, lw=0.7, ls="--")
axs[0].plot(al, 1 / np.tan(np.radians(al)), color=M.MUTED, lw=1.0, ls=":", label=T("无摩擦 1/tanα", "frictionless 1/tanα"))
axs[0].set_ylim(0, 12)
axs[0].text(2 * phi + 0.5, 10.5, T("← 自锁", "← self-locking"), fontsize=7.5, color=M.ACCENT)
axs[0].set_xlabel(T("楔角 α / °", "wedge angle α / °"), fontsize=8.5)
axs[0].set_ylabel(T("增力比 W/Q", "force ratio W/Q"), fontsize=8.5)
axs[0].legend(fontsize=7.5, frameon=False)
g = np.linspace(10, 170, 200)
for e, col in ((2, M.ACCENT), (3, M.RED)):
    r = [FX.eccentric(80, 100, 40, e, 0.1, 0.1, x) for x in g]
    axs[1].plot(g, [v["W"] / 1000 for v in r], color=col, lw=1.3, label=f"e = {e} mm（D/e = {40 / e:.0f}）")
axs[1].set_xlabel(T("偏心轮转角 γ / °", "eccentric angle γ / °"), fontsize=8.5)
axs[1].set_ylabel(T("夹紧力 W / kN", "clamping force W / kN"), fontsize=8.5)
axs[1].legend(fontsize=7.5, frameon=False)
for ax in axs:
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig52_4_1")

out(need=need, M=sc["M_Nmm"] / 1000, W_screw=sc["W"], i_screw=sc["i"], lead=sc["lead_deg"], phi_e=sc["phi_e_deg"],
    ratio=st["ratio"], W_one=st["W"], W_have=W_have, margin=W_have / need, W_hand=W_hand, M_hand=sc_hand["M_Nmm"] / 1000,
    hand_ratio=W_hand / W_have, W_ball=FX.strap_clamp(sc_flat["W"], cl["l_work"], cl["l_heel"])["W"] * cl["count"],
    end_share=cl["r_end"] * cl["mu_end"] / (sc["M_Nmm"] / sc["W"]), r_end=cl["r_end"], K=an["K"]["K"],
    sig=sig["sigma"], sig5=sig5["sigma"], phi=phi, w6_i=w6["i"], w6_eta=w6["eta"], w6_lock=w6["self_lock"], w15_lock=w15["self_lock"],
    w15_i=w15["i"], lock_limit=2 * phi, ec_W=ec["W"], ec_i=ec["i"], ec_lift=ec["lift_max_deg"], ec_lift_tan=math.degrees(math.atan(2 / 20)), ec_lock=ec["self_lock_safe"],
    ec3_lock=ec3["self_lock_safe"], ec_Dmin=ec["D_over_e_min"], ec_stroke=ec["stroke"], hg_W=hg["W"], hg_i=hg["i"])
