"""10.2 塑性材料的强度理论：特雷斯卡与冯·米塞斯。

算例 10.2.1  WQ-CR5 大臂（数字工厂“仿真与分析”的示例零件：6061 铝管 Ø90×3 + 两端法兰，伸直、5 kg 的预设载荷），用 CAE 同一套程序
            算一次（网格 7 mm），从每个节点的应力张量求主应力，分别算冯·米塞斯和特雷斯卡等效应力；比较两种理论的最大值、安全系数，
            以及两者之比在零件上的分布（1 到 2/√3）；
算例 10.2.2  三个点放在同一张 σ–τ 图上：WQ-CR5 大臂的最危险点、SH-301 B 版齿轮位的危险点（第 8 章，40Cr 调质）、
            RJ-201 在谐波减速器瞬时允许最大转矩下花键段（按小径，与第 33 章 33.10 节相同，只计转矩）的表面——纯剪切时两种理论正好差 15.5%；
图 10.2.1。
"""
import math

import numpy as np

import _ch10 as H
import _rj as RJ
import _shaft as SH
from bookout import T, figure, out, style

# ---------------------------------------------------------------- 算例 10.2.1：WQ-CR5 大臂
AL = H.mat("6061-T6")
p, step, faces, loads, ex = H.upper_arm()
H_MESH = 7.0
st, surf, P, STR = H.fe_solve(step, loads, H_MESH, AL)
ids = sorted(STR)
prin = {i: H.principal(STR[i]) for i in ids}
vm = np.array([H.vm_of(prin[i]) for i in ids])
tr = np.array([H.tresca_of(prin[i]) for i in ids])
xyz = np.array([P[int(i)] for i in ids])
# 与 CAE 一样，不计固定面（z = 0）1.5 个网格尺寸以内的点
ok = xyz[:, 2] > 1.5 * H_MESH
iv = int(np.argmax(np.where(ok, vm, -1)))
it = int(np.argmax(np.where(ok, tr, -1)))
vm_max, tr_max = vm[iv], tr[it]
SF_vm, SF_tr = AL["yield_mpa"] / vm_max, AL["yield_mpa"] / tr_max
ratio = tr / np.maximum(vm, 1e-9)
sig_ok = ok & (vm > 0.2 * vm_max)                          # 应力较大的点
r_lo, r_hi = float(ratio[sig_ok].min()), float(ratio[sig_ok].max())
r_at_hot = float(ratio[iv])
p_hot = prin[ids[iv]]
# 根部（J2 端）内角：离固定面 10 mm，落在 CAE 的排除区里（1.5 × 网格尺寸），这里单独看一下
root = [k for k in range(len(ids)) if abs(xyz[k, 2] - p["flange_t"]) < 3.0 and abs(np.hypot(xyz[k, 0], xyz[k, 1]) - (p["D"] / 2 - p["t"])) < 3.0]
vm_root = float(vm[root].max())
# 两者之比接近 2/√3 的节点在哪里
near_ts = sig_ok & (ratio > 1.14)
frac_end = float(np.mean(xyz[near_ts, 2] > p["L"] - 2 * p["flange_t"]))
# 管中段顶部（梁理论可比的地方）
top = ok & (np.abs(xyz[:, 2] - p["L"] / 2) < H_MESH) & (np.hypot(xyz[:, 0], xyz[:, 1]) > p["D"] / 2 - 0.01)
vm_mid = float(vm[top].max())
beam_vm = ex["formula"]["vm_mpa"]

# ---------------------------------------------------------------- 算例 10.2.2：三个点
ST40 = H.mat("40Cr-QT")
d = SH.diameter_at(SH.Z_GEAR)
sh_sig = SH.M_total(SH.Z_GEAR) / SH.W_solid(d)
sh_tau = SH.torque_at(SH.Z_GEAR) / SH.WT_solid(d)
sh_vm, sh_tr = math.sqrt(sh_sig ** 2 + 3 * sh_tau ** 2), math.sqrt(sh_sig ** 2 + 4 * sh_tau ** 2)
hd = RJ.harmonic("25-100")
HUB = RJ.spline(RJ.SEAT)["D_ie"]                                    # 花键段小径：传全部转矩、截面最小（第 33 章 ex33_10）
rj_tau = hd["momentary"] * 1e3 / (2 * RJ.W_hollow(HUB))            # 抗扭截面系数 = 2 × 抗弯截面系数
rj_vm, rj_tr = math.sqrt(3) * rj_tau, 2 * rj_tau
# 大臂热点的 (σ, τ) 表示：平面应力时面内两个主应力 σa、σb = σ/2 ± √(σ²/4 + τ²)，反过来 σ = σa + σb、τ = √(−σa·σb)；
# 热点的三个主应力里 σ3 接近 0，面内那一对是 σ1、σ2，都为正，几乎是单向拉伸，τ 取 0
s1, s2, s3 = p_hot
cr_sig, cr_tau = s1 + s2, math.sqrt(max(-s1 * s2, 0.0))

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={"width_ratios": [1.15, 1.0]})
a0.hist(ratio[sig_ok], bins=40, color="#1f77b4", alpha=0.85)
a0.axvline(1.0, color=H.MUTED, lw=0.7, ls="--")
a0.axvline(2 / math.sqrt(3), color="#d62728", lw=0.9, ls="--")
a0.text(2 / math.sqrt(3) - 0.003, a0.get_ylim()[1] * 0.92, T("2/√3（纯剪切）", "2/√3 (pure shear)"), fontsize=6.2, ha="right", color="#d62728")
a0.text(1.006, a0.get_ylim()[1] * 0.75, T("1（单向拉压）", "1 (uniaxial)"), fontsize=6.2, color=H.MUTED)
a0.set_xlabel(T("特雷斯卡等效应力 / 冯·米塞斯等效应力", "Tresca / von Mises equivalent stress"), fontsize=7.0)
a0.set_ylabel(T("节点数", "Number of nodes"), fontsize=7.0)
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) WQ-CR5 大臂：应力较大的节点上两者之比", "(a) WQ-CR5 upper arm: ratio at highly stressed nodes"), fontsize=7.2)
th = np.linspace(0, 2 * math.pi, 400)
a1.plot(np.cos(th), np.sin(th) / math.sqrt(3), color="#1f77b4", lw=1.4, label=T("冯·米塞斯 σ² + 3τ² = σs²", "von Mises σ² + 3τ² = σs²"))
a1.plot(np.cos(th), np.sin(th) / 2, color="#d62728", lw=1.4, ls="--", label=T("特雷斯卡 σ² + 4τ² = σs²", "Tresca σ² + 4τ² = σs²"))
pts = [(sh_sig, sh_tau, "SH-301", "o"), (0.0, rj_tau, "RJ-201", "s"), (cr_sig, cr_tau, T("WQ-CR5 大臂", "WQ-CR5 arm"), "^")]
for (x, y, n, mk), (dx, dy) in zip(pts, ((0.06, 0.03), (-0.32, 0.03), (-0.42, 0.06))):
    k = 1 / math.sqrt(x * x + 3 * y * y)               # 载荷按比例加大，直到碰到冯·米塞斯线
    kt = 1 / math.sqrt(x * x + 4 * y * y)              # 碰到特雷斯卡线
    a1.plot([0, x * k], [0, y * k], color="k", lw=0.6)
    a1.plot([x * kt], [y * kt], mk, color="#d62728", ms=4)
    a1.plot([x * k], [y * k], mk, color="#1f77b4", ms=4)
    a1.annotate(n, (x * k, y * k), xytext=(x * k + dx, y * k + dy), fontsize=6.3)
a1.set_xlim(-1.1, 1.1)
a1.set_ylim(0, 0.75)
a1.set_xlabel(T("σ / σs（载荷放大到屈服时）", "σ / σs (load scaled up to yield)"), fontsize=7.0)
a1.set_ylabel(T("τ / σs", "τ / σs"), fontsize=7.0)
a1.legend(fontsize=5.9, frameon=False, loc="upper right")
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 载荷按比例加大：先碰到哪条屈服线", "(b) Scaling the load up: which locus is hit first"), fontsize=7.2)
fig.tight_layout()
figure(fig, "fig10_2_1")

out(D=p["D"], t=p["t"], L=p["L"], h=H_MESH, el=st["elements"], vm_cae=st["vm_max_mpa"], vm_max=vm_max, tr_max=tr_max,
    hot_z=float(xyz[iv, 2]), vm_root=vm_root, frac_end=frac_end * 100, hub=HUB, s1h=s1, s2h=s2, s3h=s3, sy_al=AL["yield_mpa"], SF_vm=SF_vm, SF_tr=SF_tr,
    dSF=(SF_vm / SF_tr - 1) * 100, r_lo=r_lo, r_hi=r_hi, r_hot=r_at_hot, vm_mid=vm_mid, beam_vm=beam_vm,
    sh_sig=sh_sig, sh_tau=sh_tau, sh_vm=sh_vm, sh_tr=sh_tr, sh_r=sh_tr / sh_vm, sy40=ST40["yield_mpa"],
    hd_mom=hd["momentary"], rj_tau=rj_tau, rj_vm=rj_vm, rj_tr=rj_tr, rj_r=rj_tr / rj_vm,
    SF_rj_vm=ST40["yield_mpa"] / rj_vm, SF_rj_tr=ST40["yield_mpa"] / rj_tr)
