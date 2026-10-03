"""51.6–51.7 节：定位误差的计算。
算例 51.7.1 SH-301 铣键槽 V 形块定位；算例 51.7.2 GR-302 齿坯套在心轴上；算例 51.7.3 箱座一面两销；算例 51.7.4 两顶尖的轴向定位误差；
算例 51.6.1 基准不重合误差。图 51.7.1 V 形块定位误差的几何关系。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
p = M.plan()
fin = next(f for f in M.op(p, 40)["features"] if f["name"] == "齿轮位")            # 精车 Ø40.3（0/−0.039）
Td = fin["es_mm"] - fin["ei_mm"]
H = p["chains"][0]["links"][0]
TH = H["es"] - H["ei"]
vc, vt, vb = (TL.v_block(Td, 90, m) for m in ("center", "top", "bottom"))
v120 = TL.v_block(Td, 120, "bottom")
v60 = TL.v_block(Td, 60, "bottom")
# 心轴：GR-302 齿坯孔 Ø35 H7（+0.025/0），心轴 Ø35 g6（−0.009/−0.025）（GB/T 1800.1 的 IT7 = 25 µm、IT6 = 16 µm，g 的基本偏差 −9 µm）
hole, pin = (35, 0.025, 0.0), (35, -0.009, -0.025)
X_any = TL.pin_clearance(hole, pin, "any")
X_one = TL.pin_clearance(hole, pin, "one")
# 一面两销：箱座底面 + 两个 Ø8 H7 销孔，孔距 220 ± 0.03 mm（教学示意值）；圆柱销 Ø8 g6。
# 先设计削边销（51.7.4 节）：夹具两销中心距 ±0.01，b = 3 mm（Ø8 削边销的圆柱部分宽度，按 JB/T 8014.3 取，写作时核对），销的直径公差取 IT6 = 0.009
h8, p8 = (8, 0.015, 0.0), (8, -0.005, -0.014)
L2, dLK, dLJ, b_dp = 220.0, 0.03, 0.01, 3.0
dp = TL.diamond_pin(h8, b_dp, dLK, dLJ, 0.009)
X2 = dp["X2max"]
tp = TL.two_pins(L2, h8, p8, h8, X2)
bore_dist = 150.0                                    # 被镗的轴承孔在两销连线上、离圆柱销 150 mm
pt = TL.two_pins_point(bore_dist, L2, tp["X1max"], X2)
shift_perp, shift_along = pt["perp"], pt["along"]   # 垂直于连线、沿连线两个方向的变动范围
shift_zone = math.hypot(shift_perp, shift_along)    # 占用的位置度公差带直径（两个方向合成）
# 若误把“圆柱销处的移动 + 转角 × 距离”相加，会重复计算圆柱销的间隙
shift_naive = tp["X1max"] + bore_dist * math.tan(math.radians(tp["rot_deg"]))
# 两顶尖：中心孔锥口直径变动 0.2 mm → 轴向位移
dz = TL.center_hole_axial(0.2)
# 基准不重合（算例 51.6.1）：以右端面为定位基准、加工以左端面为设计基准的尺寸时，两个基准之间的联系尺寸是总长 167（C12，±0.5），它的公差全部成为 ΔB
L_total = next(c for c in p["characteristics"] if c["id"] == "C12")
dB = L_total["es"] - L_total["ei"]
from pathlib import Path  # noqa: E402
lab = (Path(__file__).resolve().parents[1] / "lab" / "lab51_7.js").read_text(encoding="utf-8")
assert f"TH: {TH:g}" in lab and f"TD_FIN: {Td:g}" in lab, "实验 51.7 的常数与工艺规程不一致"
out(Td=Td, TH=TH, vc=vc, vt=vt, vb=vb, v120=v120, v60=v60, vb_ratio=vb / TH, X_any=X_any, X_one=X_one,
    L2=L2, X1=tp["X1max"], rot=tp["rot_deg"], rot100=tp["rot_mm_per_100"], bore_dist=bore_dist,
    shift_perp=shift_perp, shift_along=shift_along, shift_zone=shift_zone, shift_naive=shift_naive,
    dLK=dLK, dLJ=dLJ, b_dp=b_dp, dp_X2min=dp["X2min"], dp_d2max=dp["d2max"], dp_d2min=dp["d2min"], dp_X2max=dp["X2max"],
    dz=dz, dB=dB, H=H["nominal"])

# ---- 图 51.7.1：V 形块上工件直径变化时轴心与母线的位移
plt = style()
fig, ax = plt.subplots(figsize=(5.4, 4.0))
a = math.radians(45)
apex = np.array([0, 0])
ax.plot([-3.2, 0, 3.2], [3.2, 0, 3.2], color=M.INK, lw=1.4)
for R, col, nm in ((1.6, M.ACCENT, r"$d_{\max}$"), (1.25, M.WARM, r"$d_{\min}$")):
    c = R / math.sin(a)
    ax.add_patch(plt.Circle((0, c), R, fill=False, ec=col, lw=1.4))
    ax.plot(0, c, "o", color=col, ms=4)
    ax.plot([-1.9, 1.9], [c + R, c + R], color=col, lw=0.6, ls="--")
    ax.plot([-1.9, 1.9], [c - R, c - R], color=col, lw=0.6, ls="--")
    ax.text(R * 0.75, c + R * 0.75 + 0.05, nm, color=col, fontsize=9)
c1, c2 = 1.6 / math.sin(a), 1.25 / math.sin(a)
ax.annotate("", xy=(2.3, c1), xytext=(2.3, c2), arrowprops=dict(arrowstyle="<->", color=M.RED))
ax.text(2.4, (c1 + c2) / 2, T(r"轴心位移 $\Delta_Y = T_d/(2\sin(\alpha/2))$", r"axis shift $\Delta_Y = T_d/(2\sin(\alpha/2))$"), fontsize=8.5, color=M.RED, va="center")
ax.annotate("", xy=(-2.3, c1 - 1.6), xytext=(-2.3, c2 - 1.25), arrowprops=dict(arrowstyle="<->", color=M.RED))
ax.text(-2.4, (c1 - 1.6 + c2 - 1.25) / 2, T(r"下母线 $\Delta_Y - T_d/2$", r"bottom $\Delta_Y - T_d/2$"), fontsize=8.5, color=M.RED, va="center", ha="right")
ax.annotate("", xy=(-2.3, c1 + 1.6), xytext=(-2.3, c2 + 1.25), arrowprops=dict(arrowstyle="<->", color=M.RED))
ax.text(-2.4, (c1 + 1.6 + c2 + 1.25) / 2, T(r"上母线 $\Delta_Y + T_d/2$", r"top $\Delta_Y + T_d/2$"), fontsize=8.5, color=M.RED, va="center", ha="right")
ax.text(0.15, 0.25, r"$\alpha$", fontsize=11)
ax.set_xlim(-5.6, 6.4); ax.set_ylim(-0.3, 4.4); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig51_7_1")
