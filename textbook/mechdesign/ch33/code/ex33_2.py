"""33.2 节：轴的结构设计。

图 33.2.1  SH-301 B 版的结构：轴承、套筒、齿轮、轴环、轴承盖与密封、联轴器，以及各段长度；
图 33.2.2  A 版（数字工厂现行的教学模型）与 B 版的外形对比，A 版的问题处标号；
图 33.2.3  轴肩的三条规则：定位高度、圆角小于轴承倒角、齿轮毂比轴段长；
算例 33.2.1  B 版逐条核对结构设计规则；算例 33.2.2  A 版的设计评审。
"""
import math

import numpy as np

import _draw as D
import _shaft as S
from bookout import T, figure, out, style
import mdstd

brg = mdstd.bearing(S.BRG)
lay = S.LAY_B
seg = {i + 1: s for i, s in enumerate(lay)}
key_gear = mdstd.key_for(40)
key_ext = mdstd.key_for(30)
L_key_gear = mdstd.key_length(S.HUB_GEAR - 10)          # 键比轮毂短 5–10 mm，取标准长度
L_key_ext = mdstd.key_length(S.HUB_CPL - 7)

# ---- 算例 33.2.1：B 版的规则核对
checks = []
def chk(name_zh, name_en, ok, detail):
    checks.append((T(name_zh, name_en), bool(ok), detail))

h_collar = (seg[3][2] - seg[2][2]) / 2
chk("轴环定位高度 h ≥ 0.07d", "collar height h ≥ 0.07d", h_collar >= 0.07 * seg[2][2], f"{h_collar:.1f} ≥ {0.07 * seg[2][2]:.1f}")
chk("右轴承轴肩直径 ≥ 安装尺寸 da,min", "bearing shoulder ≥ da,min", seg[4][2] >= brg["da_min"], f"{seg[4][2]} ≥ {brg['da_min']}")
r_brg = S.FILLET_B[115]
chk("轴承处圆角 r < 轴承内圈倒角 r_s,min", "fillet r < bearing chamfer r_s,min", r_brg < brg["r_smin"], f"{r_brg} < {brg['r_smin']}")
chk("齿轮位比轮毂短 2–3 mm", "gear seat 2–3 mm shorter than the hub", 2 <= S.HUB_GEAR - (seg[2][1] - seg[2][0]) <= 3,
    f"{S.HUB_GEAR:.0f} − {seg[2][1] - seg[2][0]:.0f} = {S.HUB_GEAR - (seg[2][1] - seg[2][0]):.0f}")
chk("左轴承位 ≥ 轴承宽 + 套筒", "left seat ≥ bearing + sleeve", seg[1][1] - seg[1][0] >= brg["B"] + S.SLEEVE,
    f"{seg[1][1] - seg[1][0]:.0f} ≥ {brg['B']} + {S.SLEEVE:.0f}")
chk("右轴承位 = 轴承宽", "right seat = bearing width", seg[5][1] - seg[5][0] == brg["B"], f"{seg[5][1] - seg[5][0]:.0f} = {brg['B']}")
chk("键长比轮毂短（齿轮）", "key shorter than the hub (gear)", L_key_gear <= S.HUB_GEAR - 5, f"{L_key_gear} ≤ {S.HUB_GEAR:.0f} − 5")
chk("键长比轮毂短（联轴器）", "key shorter than the hub (coupling)", L_key_ext <= S.HUB_CPL - 5, f"{L_key_ext} ≤ {S.HUB_CPL:.0f} − 5")
chk("联轴器位比轮毂短 2 mm（轴端挡圈压紧）", "coupling seat 2 mm shorter than the hub (end plate)", S.HUB_CPL - (seg[7][1] - seg[7][0]) == 2,
    f"{S.HUB_CPL:.0f} − {seg[7][1] - seg[7][0]:.0f} = {S.HUB_CPL - (seg[7][1] - seg[7][0]):.0f}")
T_key_gear = S.key_torque_limit(40, key_gear["b"], key_gear["h"], L_key_gear) / 1e3
# 按轮毂一侧的实际接触高度 h − t（键伸出轴面的高度）核算：比常规的 k = h/2 小
T_key_gear_exact = S.key_torque_limit(40, key_gear["b"], 2 * (key_gear["h"] - key_gear["t"]), L_key_gear) / 1e3
T_key_ext = S.key_torque_limit(30, key_ext["b"], key_ext["h"], L_key_ext) / 1e3
T_key_ext_exact = S.key_torque_limit(30, key_ext["b"], 2 * (key_ext["h"] - key_ext["t"]), L_key_ext) / 1e3
chk("齿轮键的挤压承载 ≥ 额定转矩", "gear key capacity ≥ rated torque", T_key_gear >= S.T_RATED / 1e3, f"{T_key_gear:.0f} ≥ {S.T_RATED / 1e3:.0f}")
chk("联轴器键的挤压承载 ≥ 额定转矩", "coupling key capacity ≥ rated torque", T_key_ext >= S.T_RATED / 1e3, f"{T_key_ext:.0f} ≥ {S.T_RATED / 1e3:.0f}")
n_ok_B = sum(ok for _, ok, _ in checks)

# ---- 算例 33.2.2：A 版评审
layA, LA = S.layout(S.SEG_A)
seatA = [s for s in layA if s[2] == 35]
A_seat_short = min(s[1] - s[0] for s in seatA)
T_key_ext_A = S.key_torque_limit(30, *S.BOM_KEY_EXT_A) / 1e3
key_vs_blank = S.KEY_A["L"] >= S.BLANK_GEAR_A[1]
T_key_gear_hub45 = S.key_torque_limit(40, 12, 8, mdstd.key_length(S.BLANK_GEAR_A[1] - 5)) / 1e3

# ---- 图 33.2.1：B 版结构
plt = style()
fig, ax = plt.subplots(figsize=(9.6, 4.4))
keys = [(S.Z_GEAR - L_key_gear / 2, S.Z_GEAR + L_key_gear / 2, key_gear["t"]),
        (S.Z_CPL - L_key_ext / 2, S.Z_CPL + L_key_ext / 2, key_ext["t"])]
D.shaft(ax, lay, keys=keys)
D.bearing(ax, S.Z_BRG_A, brg["d"], brg["D"], brg["B"])
D.bearing(ax, S.Z_BRG_B, brg["d"], brg["D"], brg["B"])
D.ring(ax, brg["B"], brg["B"] + S.SLEEVE, 35, 46, D.SLEEVE)                       # 套筒
z0g = S.Z_GEAR - S.HUB_GEAR / 2
CUT = 150                                                                          # 齿轮只画到 Ø150，上下用折断线
D.gear(ax, z0g, S.HUB_GEAR, 40, 64, 45, CUT, CUT)
for sgn in (1, -1):
    zz = np.linspace(S.Z_GEAR - 24, S.Z_GEAR + 24, 9)
    ax.plot(zz, sgn * (CUT / 2 + np.array([0, 2, -2, 2, -2, 2, -2, 2, 0])), color=D.INK, lw=1.0, zorder=6)
D.ring(ax, lay[5][0] + 4, lay[5][0] + 14, 35.6, 56, "#e5e8eb")                     # 密封（示意）
D.ring(ax, S.Z_CPL - S.HUB_CPL / 2, S.Z_CPL + S.HUB_CPL / 2, 30, 62, D.CPL)        # 联轴器轮毂
ax.add_patch(plt.Rectangle((S.LEN_B + 2, -20), 4, 40, fc="#e5e8eb", ec=D.INK, lw=1.0, zorder=5))   # 轴端挡圈
for zc in (S.Z_BRG_A, S.Z_BRG_B, S.Z_GEAR, S.Z_CPL):
    ax.plot([zc, zc], [-80, 82], color=D.MUTED, lw=0.5, ls=":")
for k, (z0, z1, d, name, tol) in enumerate(lay):
    ax.text((z0 + z1) / 2, -84 - 9 * (k % 2), f"Ø{d}{(' ' + tol) if tol else ''}", ha="center", fontsize=8, color=D.INK)
    D.dim(ax, z0, z1, -112 - 12 * (k % 2), f"{z1 - z0:.0f}", size=8)
D.dim(ax, 0, S.LEN_B, -140, f"{S.LEN_B:.0f}", size=8)
labels = [(S.Z_BRG_A, 46, T("轴承 6207", "bearing 6207")), (brg["B"] + S.SLEEVE / 2, -31, T("套筒", "sleeve")),
          (S.Z_GEAR, 84, T("齿轮 GR-302（毂宽 55）", "gear GR-302 (hub 55)")), ((lay[2][0] + lay[2][1]) / 2, 33, T("轴环", "collar")),
          (S.Z_BRG_B, 46, T("轴承 6207", "bearing 6207")), (lay[5][0] + 9, 36, T("密封", "seal")),
          (S.Z_CPL, 38, T("联轴器", "coupling")), (S.LEN_B + 4, 26, T("挡圈", "end plate"))]
for z, y, t in labels:
    ax.text(z, y, t, ha="center", fontsize=9, color=D.INK, zorder=9, bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
ax.text(S.Z_BRG_A, -70, "A", ha="center", fontsize=10, weight="bold")
ax.text(S.Z_BRG_B, -70, "B", ha="center", fontsize=10, weight="bold")
ax.set_xlim(-10, S.LEN_B + 16)
ax.set_ylim(-148, 94)
ax.set_aspect("equal")
ax.axis("off")
fig.tight_layout()
figure(fig, "fig33_2_1")

# ---- 图 33.2.2：A 版与 B 版
fig, axs = plt.subplots(2, 1, figsize=(9.0, 3.8))
for ax, L, title in ((axs[0], layA, T("A 版（数字工厂现行教学模型）", "Rev. A (the factory's current teaching model)")),
                     (axs[1], lay, T("B 版（本章方案）", "Rev. B (this chapter's design)"))):
    D.shaft(ax, L)
    ax.set_title(title, fontsize=10, loc="left")
    ax.set_xlim(-10, 260)
    ax.set_ylim(-34, 34)
    ax.set_aspect("equal")
    ax.axis("off")
marks = [((layA[1][0] + layA[1][1]) / 2, 22, "①"), ((layA[2][0] + layA[2][1]) / 2, 27, "②"), (layA[4][0] + 15, 22, "③"),
         (layA[2][0], -26, "④")]
for z, y, t in marks:
    axs[0].text(z, y, t, ha="center", fontsize=12, color=D.FORCE)
fig.tight_layout()
figure(fig, "fig33_2_2")

# ---- 图 33.2.3：轴肩细部
fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.4))
ax = axs[0]
# 轴承靠轴肩（放大）：轴肩圆角 r 必须小于轴承内圈的倒角，内圈才能贴紧轴肩端面
from matplotlib.patches import Polygon, Arc
r, c = 1.0, 1.1
ax.add_patch(Polygon([[20, 10], [30 - r, 10], *[(30 - r + r * np.sin(t), 10 + r - r * np.cos(t)) for t in np.linspace(0, np.pi / 2, 12)],
                      [30, 13.5], [36, 13.5], [36, 6], [20, 6]], closed=True, fc=D.STEEL, ec=D.INK, lw=1.2))
ax.add_patch(Polygon([[22, 10], [30 - c, 10], [30, 10 + c], [30, 17], [22, 17]], closed=True, fc=D.BEARING, ec=D.INK, lw=1.2))
ax.annotate(T("轴肩圆角 r = 1.0", "shaft fillet r = 1.0"), (29.4, 10.25), (21, 7.2), fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.annotate(T("内圈倒角 r_s,min = 1.1", "inner-ring chamfer r_s,min = 1.1"), (29.6, 10.7), (31, 16), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.text(33, 8.5, T("轴肩 Ø42", "shoulder Ø42"), fontsize=9, ha="center")
ax.text(25.5, 14, T("轴承内圈", "inner ring"), fontsize=9, ha="center", color="white")
ax.text(24, 8.2, T("轴承位 Ø35", "seat Ø35"), fontsize=9, ha="center")
ax.set_xlim(20, 37); ax.set_ylim(6, 18); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(T("(a) 轴承靠在轴肩上（局部放大）", "(a) bearing against a shoulder (enlarged)"), fontsize=10)
ax = axs[1]
ax.add_patch(plt.Rectangle((0, 0), 40, 20, fc=D.STEEL, ec=D.INK))
ax.add_patch(plt.Rectangle((40, 0), 10, 24, fc=D.STEEL, ec=D.INK))
ax.add_patch(plt.Rectangle((-6, 20), 12, 6, fc=D.SLEEVE, ec=D.INK))
ax.add_patch(plt.Rectangle((6, 20), 34, 12, fc=D.GEAR, ec=D.INK))
ax.annotate("", (6, 34.5), (40, 34.5), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(23, 35.5, T("毂宽 55", "hub 55"), ha="center", fontsize=9)
ax.annotate("", (8, -3), (40, -3), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(24, -7, T("轴段 53", "seat 53"), ha="center", fontsize=9)
ax.annotate(T("2 mm：套筒压在毂上，\n而不是顶在轴肩上", "2 mm: the sleeve presses the hub,\nnot the shaft step"), (7, 21), (8, 8),
            fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.text(0, 27.5, T("套筒", "sleeve"), fontsize=8.5)
ax.text(45, 26, T("轴环", "collar"), fontsize=8.5, ha="center")
ax.set_xlim(-8, 52); ax.set_ylim(-10, 40); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(T("(b) 齿轮的轴向定位", "(b) axial location of the gear"), fontsize=10)
fig.tight_layout()
figure(fig, "fig33_2_3")

out(L1=seg[1][1] - seg[1][0], L2=seg[2][1] - seg[2][0], L3=seg[3][1] - seg[3][0], L4=seg[4][1] - seg[4][0],
    L5=seg[5][1] - seg[5][0], L6=seg[6][1] - seg[6][0], L7=seg[7][1] - seg[7][0], L_total=S.LEN_B,
    z_A=S.Z_BRG_A, z_B=S.Z_BRG_B, z_gear=S.Z_GEAR, z_cpl=S.Z_CPL, span=S.SPAN, a_gear=S.Z_GEAR - S.Z_BRG_A,
    b_gear=S.Z_BRG_B - S.Z_GEAR, c_cpl=S.Z_CPL - S.Z_BRG_B, B_brg=brg["B"], da_min=brg["da_min"], r_smin=brg["r_smin"],
    h_collar=h_collar, h_min=0.07 * 40, key_gear=f"{key_gear['b']}×{key_gear['h']}×{L_key_gear}",
    key_ext=f"{key_ext['b']}×{key_ext['h']}×{L_key_ext}", t_gear=key_gear["t"], t_ext=key_ext["t"],
    T_key_gear=T_key_gear, T_key_ext=T_key_ext, T_key_gear_exact=T_key_gear_exact, T_key_ext_exact=T_key_ext_exact,
    k_gear_exact=key_gear["h"] - key_gear["t"], k_ext_exact=key_ext["h"] - key_ext["t"], n_checks=len(checks), n_ok_B=n_ok_B,
    checks=[[c[0], c[1], c[2]] for c in checks],
    A_seat_short=A_seat_short, T_key_ext_A=T_key_ext_A, key_vs_blank=key_vs_blank, T_key_gear_hub45=T_key_gear_hub45,
    blank_w=S.BLANK_GEAR_A[1], hub=S.HUB_GEAR, sigma_p=S.SIGMA_P_ALLOW,
    k6_35=" – ".join(f"{x:.3f}" for x in mdstd.fit_limits(35, "k6")), r6_40=" – ".join(f"{x:.3f}" for x in mdstd.fit_limits(40, "r6")),
    H7_40=" – ".join(f"{x:.3f}" for x in mdstd.fit_limits(40, "H7")), f9_35=" – ".join(f"{x:.3f}" for x in mdstd.fit_limits(35, "f9")))
