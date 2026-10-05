"""52.9 节：JJ-301-50 的夹具精度分析与刚度校核。
算例 52.9.1 精度预算：各项误差由本章的公式算出，与夹具数据里登记的预算核对，再按极值法和平方和法合成；
算例 52.9.2 V 形块截面的平面应力有限元（hub/fe2d.py）：夹紧力使工件轴心下沉多少，换成铝合金或 3D 打印尼龙会怎样；图 52.9.2（预算）、图 52.9.3（有限元）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

FX = M.fx()
FE = M.fe()
TL = M.tol()
fx = M.fixture_data()
p = M.plan()
an = FX.analyse(fx)
b_sym = next(b for b in fx["budgets"] if b["what"].startswith("键槽对称度"))
b_H = next(b for b in fx["budgets"] if b["what"].startswith("槽底尺寸"))
# 对称度各项（公差带宽度）：ΔD = 2e_t（第 51 章）；夹具装上机床后用检验棒找正 V 形块对称面，夹具上各元件的常值位置误差
# 由找正和首件试切调整吸收，ΔJ 记 0；ΔA = 找正残差 0.01/100 在 45 mm 键槽上的歪斜（若不找正、只靠定位键单边靠紧，
# 则 ΔA ≈ 0 而 ΔJ = V 形块对称面对定位键侧面的平行度 0.01/100 造成的歪斜，数值相同）
tir_t = next(i for i in M.op(p, 40)["inspect"] if "齿轮位跳动" in i["char"])["tir"]
calc = {"ΔD": TL.offset_to_zone(tir_t / 2), "ΔJ": 0.0, "ΔA": FX.parallelism_skew(0.01, 45)}
for k, v in calc.items():
    assert abs(b_sym["items"][k] - v) < 1e-9, f"对称度预算 {k} 应为 {v}"
fin = next(f for f in M.op(p, 40)["features"] if f["name"] == "齿轮位")
assert abs(b_H["items"]["ΔD"] - round(TL.v_block(fin["es_mm"] - fin["ei_mm"], 90, "bottom"), 4)) < 1e-9
sym_ext = FX.budget(b_sym["items"], b_sym["T"], "extreme")
sym_rss = FX.budget(b_sym["items"], b_sym["T"], "rss")
H_ext = FX.budget(b_H["items"], b_H["T"], "extreme")

# 有限元：一段 V 形块工作面（长 18）承担一半的夹紧力
# 两个压板离 V 形块两段工作面的外端各 20 mm、对称布置（见图 52.1.1），每段工作面各承担一半
W_land = (an["W_have"] + fx["clamping"]["G"]) / 2
N_land = W_land / (2 * math.sin(math.pi / 4))
hz = FX.hertz_line(N_land / fx["locating"]["v_land"], 40.3 / 2)
mats = {"steel": ("20Cr 渗碳淬火钢", 210000.0, 0.3), "Al": ("铝合金 6061", 69000.0, 0.33), "PA12": ("3D 打印尼龙 PA12", 1700.0, 0.4)}
res = {k: FE.vblock_stiffness(W_land, E, nu, t=fx["locating"]["v_land"]) for k, (_, E, nu) in mats.items()}
# 实验 52.9 用网格边长 2 mm、同样的单元和加载方式（JavaScript）；这里用同样的网格算一遍，供核对实验读数
lab_src = (M.REPO / "textbook" / "mfgtech" / "ch52" / "lab" / "lab52_9.js").read_text(encoding="utf-8")
assert "H: 2, NU: 0.3, D: 40.3" in lab_src
lab = {k: FE.vblock_stiffness(W_land, E, 0.3, t=fx["locating"]["v_land"], h=2.0)["drop"] for k, (_, E, nu) in mats.items()}
thin = FE.vblock_stiffness(W_land, 210000.0, 0.3, t=fx["locating"]["v_land"], y_apex=5.0, h=1.0)["drop"]
a120 = FE.vblock_stiffness(W_land, 210000.0, 0.3, t=fx["locating"]["v_land"], alpha=120.0, h=1.0)["drop"]
fine = FE.vblock_stiffness(W_land, 210000.0, 0.3, t=fx["locating"]["v_land"], h=0.5)
# 夹紧力的分散（手动定扭矩，摩擦系数 0.10–0.20，52.5 节）引起的下沉变化
cl = fx["clamping"]
lo = FX.screw_clamp(cl["hand_force"], cl["wrench"], cl["thread_d"], cl["thread_P"], 0.20, 0.20, cl["r_end"])["W"]
hi = FX.screw_clamp(cl["hand_force"], cl["wrench"], cl["thread_d"], cl["thread_P"], 0.10, 0.10, cl["r_end"])["W"]
k_s = res["steel"]["drop"] / W_land
spread = {k: (hi - lo) * an["strap"]["ratio"] * 0.95 * r["drop"] / W_land for k, r in res.items()}

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 3.4))
r = res["steel"]
m = r["mesh"]
u = r["res"]["u"]
mag = 3000.0                                       # 位移放大
xy = m.xy + mag * u
umag = np.hypot(u[:, 0], u[:, 1]) * 1000
tpc = ax.tripcolor(xy[:, 0], xy[:, 1], m.tri, facecolors=umag[m.tri].mean(axis=1), cmap="viridis", edgecolors="none")
ya = 20.0
ax.plot([-40, -40, -30, 0, 30, 40, 40, -40], [0, 50, 50, ya, 50, 50, 0, 0], color=M.MUTED, lw=0.7, ls="--")   # 变形前的轮廓
zc = ya + 40.3 / 2 / math.sin(math.pi / 4)
ax.add_patch(plt.Circle((0, zc), 40.3 / 2, fc="none", ec=M.INK, lw=0.8, ls="--"))
cb = fig.colorbar(tpc, ax=ax, shrink=0.8)
cb.set_label(T("位移 / µm", "displacement / µm"), fontsize=8)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(T(f"V 形块截面（钢），位移放大 {mag:.0f} 倍", f"V-block section (steel), displacement × {mag:.0f}"), fontsize=8.5)
figure(fig, "fig52_9_3")

# 图 52.9.2：精度预算：五项误差按极值法堆叠，与平方和合成、公差比较
fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.5))
cols = ["#4f7fb8", "#9a8f78", "#5a9e6f", "#e0b84f", "#c0504d"]
for ax, b, ttl in ((axs[0], b_sym, T("键槽对称度", "keyway symmetry")), (axs[1], b_H, T("槽底尺寸 H", "keyway depth H"))):
    left = 0.0
    for (kk, vv), c in zip(b["items"].items(), cols):
        ax.barh(1, vv * 1000, left=left * 1000, color=c, height=0.5, label=kk)
        if vv > 0.06 * max(sum(b["items"].values()), b["T"]):
            ax.text((left + vv / 2) * 1000, 1, kk, ha="center", va="center", fontsize=7, color="white")
        left += vv
    rss = FX.budget(b["items"], b["T"], "rss")["total"]
    ax.barh(0, rss * 1000, color=M.MUTED, height=0.5)
    ax.axvline(b["T"] * 1000, color=M.INK, lw=1.2, ls="--")
    ax.text(b["T"] * 1000, 1.45, T(f"公差 {b['T'] * 1000:g} µm", f"tolerance {b['T'] * 1000:g} µm"), ha="center", fontsize=7.5, bbox=dict(fc="white", ec="none", pad=1))
    ax.text(left * 1000, 1, f"  {left * 1000:.1f}", va="center", fontsize=7.5)
    ax.text(rss * 1000, 0, f"  {rss * 1000:.1f}", va="center", fontsize=7.5)
    ax.set_yticks([0, 1], [T("平方和", "RSS"), T("极值相加", "worst case")], fontsize=8)
    ax.set_xlabel("µm", fontsize=8)
    ax.set_xlim(0, max(left, b["T"]) * 1000 * 1.25)
    ax.set_ylim(-0.5, 1.75)
    ax.set_title(ttl, fontsize=9)
fig.tight_layout()
figure(fig, "fig52_9_2")

out(T_sym=b_sym["T"], sym_D=b_sym["items"]["ΔD"], sym_J=b_sym["items"]["ΔJ"], sym_A=b_sym["items"]["ΔA"], sym_T=b_sym["items"]["ΔT"],
    sym_G=b_sym["items"]["ΔG"], sym_ext=sym_ext["total"], sym_rss=sym_rss["total"], sym_ext_ok=sym_ext["ok"],
    H_D=b_H["items"]["ΔD"], H_J=b_H["items"]["ΔJ"], H_A=b_H["items"]["ΔA"], H_T=b_H["items"]["ΔT"], H_G=b_H["items"]["ΔG"],
    H_ext=H_ext["total"], T_H=b_H["T"], W_land=W_land, n_nodes=res["steel"]["n_nodes"], n_el=res["steel"]["n_el"],
    d_steel=res["steel"]["drop"] * 1000, d_Al=res["Al"]["drop"] * 1000, d_PA=res["PA12"]["drop"] * 1000,
    d_fine=fine["drop"] * 1000, vm_steel=res["steel"]["vm_max"], sp_steel=spread["steel"] * 1000, sp_Al=spread["Al"] * 1000,
    sp_PA=spread["PA12"] * 1000, lab_steel=lab["steel"] * 1000, lab_PA=lab["PA12"] * 1000, thin=thin * 1000, a120=a120 * 1000, PA_ratio=res["PA12"]["drop"] / res["steel"]["drop"],
    hz_p0=hz["p0"], hz_b=hz["b"] * 1000, hz_w=2 * hz["b"] * 1000, N_land=N_land)
