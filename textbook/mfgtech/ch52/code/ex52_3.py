"""52.3 节：算例 52.3.1——SH-301 铣键槽的切削力与需要的夹紧力。
切削力按每齿逐角积分（Kienzle 单位切削力，数据表 std/kienzle.yaml），安全系数按分项选取；四个平衡条件取最大。图 52.3.1。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

FX = M.fx()
fx = M.fixture_data()
p = M.plan()
st = next(s for s in M.op(p, 50)["steps"] if s.get("op") == "keyway")
c = fx["cutting"]
for k_plan, k_fx in (("d", "D"), ("z", "z"), ("fz", "fz"), ("ap_layer", "ap"), ("vc", "vc")):
    assert abs(st[k_plan] - c[k_fx]) < 1e-9, f"夹具数据的切削用量 {k_fx} 与工艺规程工序 50 不一致"

f = FX.slot_forces(c["D"], c["z"], c["fz"], c["ap"], c["material"])
P = FX.slot_power(f, c["D"], c["vc"])
n = 1000 * c["vc"] / (math.pi * c["D"])
vf = c["fz"] * c["z"] * n
hm = 2 * c["fz"] / math.pi
kc_hm = f["kc11"] * hm ** (-f["mc"])
P_vol = c["ap"] * c["D"] * vf * kc_hm / 60e6                      # 体积法核对（第 50 章用的方法）
Ks = FX.safety_factor(**fx["safety"])
cl = fx["clamping"]
# 进给朝向挡板：朝向挡板的轴向分力由挡板承受，但一转中有一段轴向分力背离挡板（Fx 为负），这一段要靠摩擦
Fx_back = FX.axial_to_resist(f, True)
rr = (cl["r_f"], cl["r_c"], cl["r_v"])          # 横向力的力臂、压板处和 V 形块处摩擦力的作用半径
need = FX.vblock_clamp_required(Fx_back, f["Fy_peak"], f["Fz_peak"], Ks["K"], cl["mu1"], cl["mu2"], fx["locating"]["alpha"], cl["G"], False, *rr)
need_away = FX.vblock_clamp_required(f["Fx_peak"], f["Fy_peak"], f["Fz_peak"], Ks["K"], cl["mu1"], cl["mu2"], fx["locating"]["alpha"], cl["G"], False, *rr)
need_same_r = FX.vblock_clamp_required(Fx_back, f["Fy_peak"], f["Fz_peak"], Ks["K"], cl["mu1"], cl["mu2"], fx["locating"]["alpha"], cl["G"], False)
an = FX.analyse(fx)
assert abs(an["need"]["W"] - need["W"]) < 1e-9
need_flat = FX.friction_clamp_required(f["Fy_peak"], Ks["K"], cl["mu1"], cl["mu2"])  # 若误用“平面摩擦”公式
N1, N2 = FX.vblock_normal_forces(need["W"] + cl["G"], f["Fy_peak"], fx["locating"]["alpha"])

# 图 52.3.1：一转之内作用在工件上的三个分力（重新逐角算一遍，画曲线）
kc11, mc, D, z, fz, ap = f["kc11"], f["mc"], c["D"], c["z"], c["fz"], c["ap"]
th = np.linspace(0, 2 * math.pi, 721)
FXs, FYs, FZs = [], [], []
for a in th:
    Fx = Fy = Fz = 0.0
    for j in range(z):
        phi = (a + 2 * math.pi * j / z) % (2 * math.pi)
        if 0 < phi < math.pi:
            Ft = kc11 * ap * (fz * math.sin(phi)) ** (1 - mc)
            Fr = 0.35 * Ft
            Fx += Ft * math.cos(phi) + Fr * math.sin(phi)
            Fy += -Ft * math.sin(phi) + Fr * math.cos(phi)
            Fz += 0.25 * Ft
    FXs.append(Fx); FYs.append(Fy); FZs.append(Fz)
assert abs(max(abs(v) for v in FYs) - f["Fy_peak"]) / f["Fy_peak"] < 0.02
plt = style()
fig, ax = plt.subplots(figsize=(6.0, 2.6))
deg = np.degrees(th)
ax.plot(deg, FXs, color=M.ACCENT, lw=1.3, label=T("沿进给方向 $F_x$（推向挡板）", "along feed $F_x$ (toward the stop)"))
ax.plot(deg, FYs, color=M.RED, lw=1.3, label=T("横向 $F_y$", "lateral $F_y$"))
ax.plot(deg, FZs, color=M.WARM, lw=1.3, label=T("向上 $F_z$（把工件往上拔）", "upward $F_z$ (lifting the work)"))
ax.axhline(0, color=M.MUTED, lw=0.5)
ax.set_xlim(0, 360); ax.set_xticks([0, 90, 180, 270, 360])
ax.set_xlabel(T("铣刀转角 / °", "cutter rotation / °"), fontsize=8.5); ax.set_ylabel("N", fontsize=8.5)
ax.legend(fontsize=7.5, frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.22))
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig52_3_1")

out(kc11=f["kc11"], mc=f["mc"], n=n, vf=vf, Fx_mean=f["Fx_mean"], Fy_mean=abs(f["Fy_mean"]), Fz_mean=f["Fz_mean"],
    Fx_peak=f["Fx_peak"], Fy_peak=f["Fy_peak"], Fz_peak=f["Fz_peak"], Fc=f["Fc_mean"], P=P * 1000, P_vol=P_vol * 1000,
    P_err=abs(P - P_vol) / P_vol, K=Ks["K"], K_items="×".join(f"{v:g}" for *_, v in Ks["items"]),
    W_lift=need["req"]["lift"], W_slide=need["req"]["slide_out"], W_rot=need["req"]["rotate"], W=need["W"],
    gov=FX.GOV_ZH[need["governing"]], W_axial=need["req"]["axial"], Fx_back=Fx_back, W_axial_away=need_away["req"]["axial"], W_flat=need_flat, N1=N1, N2=N2,
    mu1=cl["mu1"], mu2=cl["mu2"], G=cl["G"], fr=need["fr"], r_f=cl["r_f"], r_c=cl["r_c"], r_v=cl["r_v"],
    W_same_r=need_same_r["W"], r_effect=need["W"] / need_same_r["W"] - 1)

# 实验 52.3 的常数与本程序、夹具数据一致
from pathlib import Path  # noqa: E402
lab = (Path(__file__).resolve().parents[1] / "lab" / "lab52_3.js").read_text(encoding="utf-8")
S = cl["strap"]
th = FX.thread(cl["thread_d"], cl["thread_P"])
for key, val in (("RF", f"{cl['r_f']:g}"), ("RC", f"{cl['r_c']:g}"), ("RV", f"{cl['r_v']:g}"), ("FY0", f"{f['Fy_peak']:.1f}"), ("FZL0", f"{f['Fz_peak']:.1f}"), ("FXB0", f"{Fx_back:.1f}"), ("MC", f"{f['mc']:g}"),
                 ("RATIO", f"{cl['l_heel'] / (cl['l_work'] + cl['l_heel']) * 0.95:.3f}"), ("D2", f"{th['d2']:.3f}"),
                 ("Z_STRAP", f"{(S['b'] - S['slot_w']) * S['h'] ** 2 / 6:.0f}"), ("G", f"{cl['G']:g}"), ("R_END", f"{cl['r_end']:g}")):
    assert f"{key}: {val}" in lab, f"实验 52.3 的常数 {key} 应为 {val}"
