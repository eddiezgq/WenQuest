"""52.1 节：键槽铣夹具 JJ-301-50 的组成——画夹具总图的示意（俯视图、A–A 剖视、明细栏、技术要求），全部取自夹具数据
factory/digital/std/JJ-301-50_fixture.yaml；统计各类元件。图 52.1.1。"""
import math

import _mfg as M
from bookout import T, figure, out, style

fx = M.fixture_data()
p = M.plan()
o50 = M.op(p, 50)
assert o50.get("fixture_id") == fx["id"], "工序 50 登记的夹具编号与夹具数据不一致"

plt = style()
fig = plt.figure(figsize=(7.6, 6.9))
axp = fig.add_axes([0.02, 0.50, 0.62, 0.48])     # 俯视图
axs = fig.add_axes([0.02, 0.06, 0.40, 0.42])     # A–A 剖视
axt = fig.add_axes([0.45, 0.19, 0.54, 0.30])     # 明细栏
axp.set_title(T("俯视图（工件双点画线）", "Plan view (workpiece in phantom)"), fontsize=8.5, loc="left")
axs.set_title(T("A–A（过 V 形块）", "Section A–A (through the V-block)"), fontsize=8.5, loc="left")

# ---- SH-301 的各段（左端起）：长度与直径取自工序 40 简图的毛坯段
segs = M.op(p, 40)["sketch"]["stock"]
x0 = -sum(L for _, L in segs[:2])                 # 齿轮位左端（左轴肩）放在 x = 0
xs, x = [], x0
for d, L in segs:
    xs.append((x, x + L, d)); x += L
alpha = fx["locating"]["alpha"]
h = math.radians(alpha) / 2
d_g = 40.3
apex = 20.0                                       # V 形块顶点离夹具体顶面的高度
zc = apex + d_g / 2 / math.sin(h)

def rect(ax, x0, y0, w, hh, **k):
    k.setdefault("fc", "none"); k.setdefault("ec", M.INK); k.setdefault("lw", 1.0)
    ax.add_patch(plt.Rectangle((x0, y0), w, hh, **k))

# 俯视图
rect(axp, -75, -62, 245, 124, fc="#f3f1ec")                                         # 1 夹具体
for ex_ in (-75 - 14, 170):                                                          # 两端 U 形耳座（T 形槽螺栓压紧）
    rect(axp, ex_, -14, 14, 28, fc="#f3f1ec")
    axp.add_patch(plt.Rectangle((ex_ + (0 if ex_ < 0 else 4), -4.5), 10, 9, fc="white", ec=M.INK, lw=0.8))
ks = fx["keys"]["spacing"]
for kx in (-40, -40 + ks):
    rect(axp, kx - 12, -9, 24, 18, ec=M.MUTED, ls="--")                             # 2 定位键（在底面，虚线）
rect(axp, 0, -40, 60, 80, fc="#e4ecf5")                                              # 3 V 形块
land = fx["locating"]["v_land"]
for lx in (0, 60 - land):
    rect(axp, lx, -14, land, 28, fc="#c9d9ec", ec=M.ACCENT)
for y0_, h_ in ((-30, 11.5), (18.5, 11.5)):                                           # 4 挡板：U 形缺口宽 37，让开 Ø35.3 轴承位，只碰轴肩
    rect(axp, -6, y0_, 6, h_, fc="#efd9c4", ec=M.WARM)
for (a, b, d) in xs:                                                                 # 工件
    rect(axp, a, -d / 2, b - a, d, ec=M.MUTED, ls=(0, (6, 2, 1, 2)), lw=0.9)
kp = next(dd for dd in o50["sketch"]["dims"] if dd["kind"] == "keyway_pos")
kx0 = float(kp["text"])
rect(axp, kx0, -6, 45, 12, ec=M.RED, lw=1.2)                                         # 键槽
strap_x = (-20, 60 + 20)                                                             # 离 V 形块两端各 20 mm，对称布置
for sx in strap_x:                                                                   # 5 压板、6 后支点、7 螺柱
    rect(axp, sx - 8, -8, 16, 68, fc="#d7dde2")
    axp.add_patch(plt.Circle((sx, 22), 5.5, fc="white", ec=M.INK, lw=0.8))
    rect(axp, sx - 7, 52, 14, 8, fc="#bfc7cd")
sb = fx["setting"]
rect(axp, 135, sb["side_from_v_plane"], 18, 20, fc="#f2d4cf", ec=M.RED)              # 10 对刀块（在工件右端以外）
axp.plot([-80, 150], [0, 0], color=M.MUTED, lw=0.6, ls=(0, (8, 2, 1, 2)))
axp.annotate("", xy=(190, 40), xytext=(165, 40), arrowprops=dict(arrowstyle="-|>", color=M.INK, lw=0.8))
axp.text(160, 46, T("工作台进给", "table feed"), fontsize=6.5)
# 进给方向朝向挡板：铣刀从右向左走，轴向切削力把工件推向挡板
axp.annotate("", xy=(-6, -48), xytext=(30, -48), arrowprops=dict(arrowstyle="-|>", color=M.RED, lw=0.9))
axp.text(32, -51, T("铣刀相对工件（朝向挡板；每层单向切削，抬刀返回）", "cutter relative to work (toward stop; one-way, lift to return)"), fontsize=6.2, color=M.RED, va="center")
labels = {1: (-68, 52), 2: (-40, -16), 3: (30, 34), 4: (-3, 34), 5: (strap_x[1], 66), 6: (strap_x[1] + 10, 55), 10: (144, 33), 13: (177, 20)}
for k, (lx, ly) in labels.items():
    axp.text(lx, ly, str(k), fontsize=7.5, ha="center", va="center",
             bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec=M.INK, lw=0.6))
axp.plot([30, 30], [-62, -70], color=M.INK, lw=0.8); axp.text(31, -72, "A", fontsize=8)
axp.set_xlim(-92, 195); axp.set_ylim(-75, 72); axp.set_aspect("equal"); axp.axis("off")

# A–A 剖视
rect(axs, -62, -30, 124, 30, fc="#f3f1ec", hatch="///")
rect(axs, -9, -38, 18, 8, fc="#dddddd")
vx = [-40, -40, -(50 - apex) * math.tan(h), 0, (50 - apex) * math.tan(h), 40, 40]
vy = [0, 50, 50, apex, 50, 50, 0]
axs.add_patch(plt.Polygon(list(zip(vx, vy)), closed=True, fc="#c9d9ec", ec=M.ACCENT, lw=1.0, hatch="\\\\\\"))
axs.add_patch(plt.Circle((0, zc), d_g / 2, fc="white", ec=M.INK, lw=1.2))
axs.plot([-26, 26], [zc, zc], color=M.MUTED, lw=0.5, ls=(0, (6, 2, 1, 2)))
axs.plot([0, 0], [-40, zc + 26], color=M.MUTED, lw=0.5, ls=(0, (6, 2, 1, 2)))
rect(axs, -6, zc + d_g / 2 - 4.85, 12, 4.85, fc="#f2d4cf", ec=M.RED)                 # 键槽截面（示意）
top = apex + sb["top_from_v_apex"]
sx_ = sb["side_from_v_plane"]                                                       # 直角对刀块（在剖切面之后）：
axs.add_patch(plt.Polygon([(sx_, 0), (sx_ + 20, 0), (sx_ + 20, top), (sx_ + 8, top), (sx_ + 8, top - 10), (sx_, top - 10)], closed=True,
                          fc="none", ec=M.RED, ls="--", lw=1.0))                      # 侧面（低处）对中心，顶面对深度
yy = top + 4
axs.plot([sb["side_from_v_plane"]] * 2, [top, yy + 2], color=M.INK, lw=0.4)
axs.annotate("", xy=(0, yy), xytext=(sb["side_from_v_plane"], yy), arrowprops=dict(arrowstyle="<->", lw=0.7))
axs.text(sb["side_from_v_plane"] + 2, yy + 1.5, f"{sb['side_from_v_plane']:g}±{sb['side_tol']:g}", fontsize=6.5, ha="left")
axs.annotate("", xy=(48, apex), xytext=(48, top), arrowprops=dict(arrowstyle="<->", lw=0.7))
axs.plot([0, 50], [apex, apex], color=M.MUTED, lw=0.4)
axs.text(50, (apex + top) / 2, f"{sb['top_from_v_apex']:.2f}±{sb['top_tol']:g}", fontsize=6.5, va="center")
axs.text(-3, apex - 6, "90°", fontsize=7, ha="right")
axs.set_xlim(-66, 80); axs.set_ylim(-56, zc + 30); axs.set_aspect("equal"); axs.axis("off")

# 明细栏与技术要求
axt.axis("off")
rows = [[str(r[0]), r[1], str(r[2]), r[3]] for r in fx["parts"]]
tb = axt.table(cellText=rows, colLabels=[T("序号", "No."), T("名称", "Name"), T("数量", "Qty"), T("材料", "Material")],
               colWidths=[0.08, 0.52, 0.12, 0.18], loc="upper left", cellLoc="left")
tb.auto_set_font_size(False); tb.set_fontsize(6.6); tb.scale(1, 0.86)
req = "\n".join(f"{i}. {t}" for i, t in enumerate(fx["requirements"][:5], 1))
fig.text(0.45, 0.150, T("技术要求（摘录）", "Technical requirements (extract)") + "\n" + req, fontsize=6.2, va="top")
figure(fig, "fig52_1_1")

kinds = {"定位元件": [3, 4], "夹紧装置": [5, 6, 7, 8, 9], "对刀元件": [10, 12], "连接元件": [2], "夹具体": [1], "其他": [11]}
out(n_parts=len(fx["parts"]), n_req=len(fx["requirements"]), dof=fx["locating"]["dof"], key_spacing=fx["keys"]["spacing"],
    **{f"k_{i}": len(v) for i, v in enumerate(kinds.values())})
