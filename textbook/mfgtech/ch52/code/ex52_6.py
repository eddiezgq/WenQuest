"""52.6 节：对刀、导向与安装。算例 52.6.1 JJ-301-50 对刀块的位置（侧面、顶面）；
算例 52.6.2 定位键在 T 形槽里的间隙引起的键槽歪斜；算例 52.6.3 箱座端面螺孔钻模的孔位误差（钻套引导，图 52.6.1）。"""
import math

import _mfg as M
from bookout import T, figure, out, style

FX = M.fx()
TL = M.tol()
fx = M.fixture_data()
p = M.plan()
o50 = M.op(p, 50)
H = p["chains"][0]["links"][0]                       # H 35.15（−0.03/−0.20）
H_mid = H["nominal"] + (H["es"] + H["ei"]) / 2
fin = next(f for f in M.op(p, 40)["features"] if f["name"] == "齿轮位")
d_mid = fin["size_mm"] + (fin["es_mm"] + fin["ei_mm"]) / 2
a = math.radians(fx["locating"]["alpha"]) / 2
zc = d_mid / 2 / math.sin(a)                        # 轴心到 V 形块理论顶点的高度
z_bottom = zc - d_mid / 2                           # 下母线高度
z_slot = z_bottom + H_mid                           # 槽底高度
s = fx["setting"]
top = z_slot - s["feeler"]                          # 对刀块顶面 = 槽底 − 塞尺
side = fx["cutting"]["D"] / 2 + s["feeler"]
assert abs(round(top, 2) - s["top_from_v_apex"]) < 1e-9, f"夹具数据的对刀块高度应为 {top:.2f}"
assert abs(side - s["side_from_v_plane"]) < 1e-9
# 对刀误差：对刀块位置公差 ±0.005（侧面）与塞尺判断（手感，约 ±0.005，教学取值）
dT_side = 2 * s["side_tol"] + 2 * 0.005
k = fx["keys"]
L_slot = 45.0
ka = FX.key_alignment(tuple(k["slot"]), tuple(k["key"]), k["spacing"], L_slot, one_side=False)
kb = FX.key_alignment(tuple(k["slot"]), tuple(k["key"]), k["spacing"], L_slot, one_side=True)
skew_J = FX.parallelism_skew(0.01, L_slot)

# 算例 52.6.3：箱体组件 SA-000（箱座、箱盖合箱后）端面 4×M8 螺孔（底孔 Ø6.8，钻深 16），盖板式钻模以 Ø72 H7 轴承孔（短销 g6）和端面定位，
# 钻模上两个支承钉靠箱座底面（已加工）防转；孔的位置度 Ø0.3（教学示意值）
hole, pin = (72, 0.030, 0.0), (72, -0.010, -0.029)
X_loc = TL.pin_clearance(hole, pin, "any")          # 孔心可偏向任意方向，占用位置度公差带 X_max
bush, drill = (6.8, 0.028, 0.013), (6.8, 0.0, -0.022)   # 固定钻套孔 F7，钻头 h8
bush_g6 = (6.8, 0.014, 0.005)                           # 改用 G6
Hb, sb, Bh = 12.0, 4.0, 16.0
g = FX.bushing_drill_error(bush, drill, Hb, sb, Bh)
g_far = FX.bushing_drill_error(bush, drill, Hb, Hb, Bh)  # 钻套离工件远到等于导向长度
g6 = FX.bushing_drill_error(bush_g6, drill, Hb, sb, Bh)
J = 0.03                                             # 钻套孔对定位销的位置度（钻模制造，取工件的 1/10）
G = 0.05                                             # 钻头出钻套后的引偏（教学估计）
items = {"ΔD": X_loc, "ΔJ": J, "ΔT": g["zone"], "ΔG": G}
ext = FX.budget(items, 0.3, "extreme")
rss = FX.budget(items, 0.3, "rss")
ext6 = FX.budget(items | {"ΔT": g6["zone"]}, 0.3, "extreme")
# 分度误差（52.6.6 节）：对定销与分度盘孔间隙 0.01，分度孔在半径 60 处、孔距误差 ±0.005（取 0.01），回转轴间隙 0.005，工件上半径 45 处
ix = FX.indexing_error(45, 0.01, 60, 0.01, 0.005)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 3.4))
bw, bh = 3.0, 6.0                                     # 示意尺寸（放大画）
ax.add_patch(plt.Rectangle((-6, 6), 12, 2.2, fc="#e4ecf5", ec=M.INK, lw=1.0))           # 钻模板
ax.add_patch(plt.Rectangle((-bw, 6 - 2.4), 2 * bw - 0.0, bh + 0.4, fc="#c9d9ec", ec=M.ACCENT, lw=1.0))  # 钻套
ax.add_patch(plt.Rectangle((-1.6, 3.6), 3.2, 6.4, fc="white", ec=M.ACCENT, lw=0.8))      # 钻套孔
ax.add_patch(plt.Rectangle((-8, -2), 16, 2.0, fc="#f3f1ec", ec=M.INK, lw=1.0, hatch="//"))  # 工件
x_top, x_bot = -0.4, 0.4                              # 钻头轴线：上端偏左、下端偏右（钻头碰到钻套孔的两侧）
k_ = (x_bot - x_top) / (10.0 - 3.6)
x_w = x_bot + k_ * 3.6                                 # 延长到工件表面
xa, xb = x_top - k_ * 1.0, x_w                          # 钻头轴线在 y = 11 和 y = 0 处的 x
ax.add_patch(plt.Polygon([(xa - 1.2, 11.0), (xa + 1.2, 11.0), (xb + 1.2, 0.0), (xb - 1.2, 0.0)], closed=True,
                         fc=M.RED, alpha=0.25, ec=M.RED, lw=0.8))
ax.plot([xa, xb], [11.0, 0.0], color=M.RED, lw=0.6, ls=(0, (6, 2, 1, 2)))
ax.plot([0, 0], [-2.6, 11], color=M.MUTED, lw=0.6, ls=(0, (6, 2, 1, 2)))
ax.annotate("", xy=(x_w, -0.4), xytext=(0, -0.4), arrowprops=dict(arrowstyle="<->", lw=0.7, color=M.RED))
ax.text(0.9, -1.2, T("孔位偏移", "hole offset"), fontsize=7.5, color=M.RED)
ax.annotate("", xy=(-4.2, 3.6), xytext=(-4.2, 10.0), arrowprops=dict(arrowstyle="<->", lw=0.7))
ax.text(-4.4, 6.8, "H", fontsize=8, ha="right")
ax.annotate("", xy=(4.2, 0.0), xytext=(4.2, 3.6), arrowprops=dict(arrowstyle="<->", lw=0.7))
ax.text(4.4, 1.8, "s", fontsize=8)
ax.text(6.2, 7.0, T("钻模板", "jig plate"), fontsize=7.5)
ax.text(3.2, 4.4, T("钻套", "bushing"), fontsize=7.5, color=M.ACCENT)
ax.text(6.2, -1.0, T("工件", "workpiece"), fontsize=7.5)
ax.text(-8.8, 11.4, T("钻头上端靠一侧、下端靠另一侧：\n偏移 X/2 + s·X/H（间隙放大画）", "drill touches opposite sides top and bottom:\noffset X/2 + s·X/H (clearance exaggerated)"),
        fontsize=7, va="bottom")
ax.set_xlim(-9, 9); ax.set_ylim(-3, 13.2); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig52_6_1")

out(H_nom=H["nominal"], H_mid=H_mid, d_mid=d_mid, zc=zc, z_bottom=z_bottom, z_slot=z_slot, top=top, side=side, feeler=s["feeler"], dT_side=dT_side,
    key_X=ka["X"], key_th100=ka["theta"] * 100, key_skew=ka["skew"], key_skew_one=kb["skew"], skew_J=skew_J,
    X_loc=X_loc, bushX=g["X"], bush_zone=g["zone"], bush_zone_surf=2 * g["offset_surface"], bush_zone_far=g_far["zone"], Hb=Hb, sb=sb,
    Bh=Bh, J=J, G=G, ext=ext["total"], rss=rss["total"], bushX6=g6["X"], bush_zone6=g6["zone"], ext6=ext6["total"],
    ix_sec=ix["angle_sec"], ix_R=ix["at_R"])
