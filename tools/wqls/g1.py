"""第 138 轮 G1：WQ-LS 的时序图、机构运动简图、总体布置图，以及全针距范围的校核表。

    python3 tools/wqls/g1.py        # 写到 docs/设计/WQ-LS/G1/
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "services" / "gateway"), str(Path(__file__).parent)]
from app.sewcore import design as D  # noqa: E402
from app.sewcore.kit import AC, B_GUIDE, Mech  # noqa: E402

import spec as S  # noqa: E402

OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G1"
plt.rcParams.update({"font.family": ["Noto Sans CJK JP", "DejaVu Sans"], "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none"})
INK, MUTE, ACC, RED, GRN, BLU = "#1d2733", "#7a8794", "#c8102e", "#d7263d", "#2e9e6a", "#1f5fa8"
GROUPS_MECH = {"needle", "hook", "takeup", "feed", "frame", "manuf"}


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- 校核：1–5 mm 针距
def checks():
    rows, allok = {}, True
    for s in S.STITCH_RANGE:
        r = D.analyze({**S.SEW, "s": s}, trial=(s == 3.0))
        for c in r["checks"]:
            mech = c["group"] in GROUPS_MECH
            row = rows.setdefault(c["key"], dict(name=c["name"]["zh"], en=c["name"]["en"], limit=c["limit"]["zh"],
                                                 group=c["group"], mech=mech, vals={}, states={}))
            row["vals"][s], row["states"][s] = c["value"]["zh"], c["state"]
            if mech and c["state"] != "ok":
                allok = False
    return rows, allok


# ---------------------------------------------------------------- 时序图
def timing():
    p = {**S.SEW}
    r = D.analyze(p, trial=False)
    M = D.mech_of(D.clean(p))
    F = M.feed_model(fab=p.get("fab", "cotton"), mode=p["mode"], s=p["s"], dT=p["dT"], dP=p["dP"], h=p["h"], P=p["P"])
    TK = M.takeup(u=0, t=1.5, s=p["s"], phc=round(r["key"]["fc"]), rpm=p["n"], lk=M.LK0)
    phi = list(range(361))
    tip = [M.tip(f % 360) for f in phi]
    eye = [t + M.EYE for t in tip]
    fy = [F["Y"](f) for f in phi]
    fx = [F["X"](f) for f in phi]
    sup = [TK["S"][f % 360] for f in phi]
    dem = [TK["D"][f % 360] for f in phi]
    fc = r["key"]["fc"]

    fig, ax = plt.subplots(4, 1, figsize=(8.6, 9.2), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1.6, 1.6, 1.3], hspace=0.14))
    a = ax[0]
    a.axhspan(0, 1.5, color="#e9dfcf", lw=0, label="面料（棉布两层 1.5 mm）")
    a.axhline(0, color=INK, lw=0.8)
    a.plot(phi, tip, color=INK, lw=1.6, label="针尖高度")
    a.plot(phi, eye, color=BLU, lw=1.0, ls="--", label="针眼上沿")
    a.axvline(fc, color=ACC, lw=1)
    a.annotate(f"钩线 {fc:.1f}°\n针回升 2.0 mm", (fc, M.tip(round(fc)) + 2), (fc - 6, 7), color=ACC, fontsize=8, ha="right",
               arrowprops=dict(arrowstyle="-", color=ACC, lw=0.7))
    a.set_ylabel("相对针板 / mm")
    a.set_title("WQ-LS 机构时序图（主轴 5000 r/min，针距 3 mm，送布定时提前 6°）", loc="left", fontsize=10.5, color=INK)
    a.legend(loc="lower left", fontsize=7.5, frameon=False)

    a = ax[1]
    a.plot(phi, sup, color=GRN, lw=1.5, label="挑线杆供线量 S")
    a.plot(phi, dem, color=INK, lw=1.0, ls="--", label="需线量 D")
    a.fill_between(phi, sup, dem, where=[s_ >= d_ for s_, d_ in zip(sup, dem)], color=GRN, alpha=0.08, lw=0)
    a.set_ylabel("线量 / mm")
    a.legend(loc="upper right", fontsize=7.5, frameon=False)

    a = ax[2]
    a.plot(phi, fy, color=INK, lw=1.4, label="送布牙齿尖高度")
    a.axhline(0, color=MUTE, lw=0.6)
    a.fill_between(phi, 0, fy, where=[y > 0 for y in fy], color=BLU, alpha=0.12, lw=0, label="牙在针板上")
    a2 = a.twinx()
    a2.plot(phi, fx, color=BLU, lw=1.0, ls="--")
    a2.set_ylabel("水平位置 / mm", color=BLU)
    a2.spines["top"].set_visible(False)
    a.set_ylabel("高度 / mm")
    a.legend(loc="lower left", fontsize=7.5, frameon=False)

    a = ax[3]
    tl = r["timing"]
    names = []
    for i, w in enumerate(tl):
        lo, hi = w["a"], w["b"]
        segs = [(lo, hi)] if hi >= lo else [(lo, 360), (0, hi)]
        if w["key"] == "dog_up":
            lo, hi = F["rise"], F["drop"]
            segs = [(lo, hi)] if hi >= lo else [(lo, 360), (0, hi)]
        for s0, s1 in segs:
            a.barh(i, max(s1 - s0, 1.5), left=s0, height=0.55, color=[INK, BLU, ACC, GRN, MUTE][i % 5], alpha=0.85)
        names.append(w["zh"])
    a.set_yticks(range(len(names)), names, fontsize=7.5)
    a.invert_yaxis()
    a.set_xlim(0, 360)
    a.set_xticks(range(0, 361, 30))
    a.set_xlabel("主轴转角 φ / °（0° = 针杆上止点）")
    for x in ax:
        x.grid(axis="x", color="#e6e9ec", lw=0.6)
    save(fig, "时序图")
    return dict(fc=fc, drop=F["drop"], rise=F["rise"], takeup_top=TK["top"], fin=TK["fin"])


# ---------------------------------------------------------------- 机构运动简图
def ground(ax, x, y, w=10, ang=0):
    ax.plot([x - w / 2, x + w / 2], [y, y], color=INK, lw=1)
    for i in range(5):
        xx = x - w / 2 + i * w / 4
        ax.plot([xx, xx - 2.2], [y, y - 2.2], color=INK, lw=0.6)


def pivot(ax, x, y, r=1.8, fill="white"):
    ax.add_patch(Circle((x, y), r, fc=fill, ec=INK, lw=1, zorder=5))


def label(ax, xy, text, xytext, color=None, ha="left"):
    color = color or INK
    ax.annotate(text, xy, xytext, fontsize=8, color=color, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=color, lw=0.6, shrinkA=2, shrinkB=1))


def bushing(ax, x, z, w, h, vertical=True):
    """机架上的导轨 / 轴承：两侧各一条带剖面线的块。"""
    if vertical:
        for dx in (-w / 2 - 2.6, w / 2):
            ax.add_patch(Rectangle((x + dx, z - h / 2), 2.6, h, fc="white", ec=INK, lw=0.8, hatch="//////"))
    else:
        for dz in (-w / 2 - 2.6, w / 2):
            ax.add_patch(Rectangle((x - h / 2, z + dz), h, 2.6, fc="white", ec=INK, lw=0.8, hatch="//////"))


def kinematic():
    lk = dict(r=S.SEW["lk_r"], a=S.SEW["lk_a"], b=S.SEW["lk_b"], c=S.SEW["lk_c"], al=S.SEW["lk_al"], d=S.SEW["lk_d"])
    M = Mech(r=S.SEW["r"], l=S.SEW["l"], lk=lk)
    r, l, ZU = S.SEW["r"], S.SEW["l"], S.ZU
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12, 6.4), gridspec_kw=dict(width_ratios=[1, 1.45], wspace=0.04))

    # ---- 左：端视（从机头一侧看，Y–Z 平面；横向是 sewcore 的 z，向右为机器前方）
    phi = 60.0
    q = math.radians(phi)
    C = (r * math.sin(q), ZU + r * math.cos(q))                          # 曲柄销
    pin_z = C[1] - math.sqrt(l * l - C[0] ** 2)                           # 针杆连接销（在针杆中心线 y = 0 上）
    tip = M.tip(phi)                                                      # 针尖高出针板
    nb_bot = tip + S.NEEDLE_DB1 - 6                                       # 针夹下端（机针插入 6 mm）
    nb_top = pin_z + 26
    ax.add_patch(Rectangle((-3.2, nb_bot), 6.4, nb_top - nb_bot, fc="#dfe5ea", ec=INK, lw=1, zorder=3))
    ax.plot([0, 0], [nb_bot, tip], color=INK, lw=1.4, zorder=3)
    bushing(ax, 0, ZU - 70, 6.4, 16)
    bushing(ax, 0, 46, 6.4, 16)
    ax.plot([0, C[0]], [ZU, C[1]], color=INK, lw=3, solid_capstyle="round", zorder=4)
    ax.plot([C[0], 0], [C[1], pin_z], color=INK, lw=2.2, solid_capstyle="round", zorder=4)
    lp = M.link_pose(phi, M.LK0)
    T = lambda p_: (p_[0], ZU + p_[1])  # noqa: E731
    P_, M_, E_, Q_ = (T(lp[k]) for k in ("P", "M", "E", "Q"))
    ax.plot([0, P_[0]], [ZU, P_[1]], color=GRN, lw=3, solid_capstyle="round", zorder=4)
    ax.plot([P_[0], E_[0]], [P_[1], E_[1]], color=GRN, lw=2.4, solid_capstyle="round", zorder=4)
    ax.plot([M_[0], Q_[0]], [M_[1], Q_[1]], color=GRN, lw=1.8, zorder=4)
    for p_ in (C, (0, pin_z), P_, M_, Q_):
        pivot(ax, *p_)
    pivot(ax, 0, ZU, 4.2, "#cfd8df")
    ground(ax, Q_[0], Q_[1] - 1.8, 12)
    ax.add_patch(Circle(E_, 2.6, fc=GRN, ec=INK, lw=0.8, zorder=6))
    A, B = T(AC), T(B_GUIDE)
    ax.plot([A[0], E_[0], B[0], 0], [A[1], E_[1], B[1], tip + 2], color=ACC, lw=0.9, ls=(0, (3, 2)), zorder=2)
    for g_ in (A, B):
        ax.add_patch(Circle(g_, 1.8, fc=ACC, ec="none", zorder=5))
    ax.axhline(0, color=INK, lw=1.4)
    ax.add_patch(Rectangle((-30, -1.6), 60, 1.6, fc="#e9dfcf", ec="none"))
    hook = (0, S.ZH)
    ax.add_patch(Circle(hook, 17.5, fc="#eef3fa", ec=BLU, lw=1.3))
    ax.add_patch(Circle(hook, 2.6, fc=BLU, ec="none"))
    lbl = [((0, ZU), "上轴（主轴）", (-70, ZU + 22), INK), (C, f"刺布曲柄 r = {r:g}", (-70, ZU + 6), INK),
           (((C[0] + 0) / 2, (C[1] + pin_z) / 2), f"连杆 l = {l:g}", (-70, ZU - 30), INK),
           ((0, ZU - 70), "针杆导套（机架）", (-70, ZU - 70), INK), ((-3.2, 90), "针杆", (-70, 92), INK),
           ((0, tip + 4), "机针 DB×1", (-70, 30), INK), ((-20, 0), "针板", (-70, 6), INK),
           (hook, "旋梭（转速为主轴 2 倍）", (34, -38), BLU),
           (E_, "挑线眼", (E_[0] + 22, E_[1] + 16), GRN), (P_, "挑线曲柄 20.7", (P_[0] + 34, P_[1] + 38), GRN),
           (M_, "挑线杆", (M_[0] + 40, M_[1] + 6), GRN), (Q_, "摇杆支点（机架）", (Q_[0] + 34, Q_[1] - 14), GRN),
           (A, "夹线器侧线钩", (A[0] + 4, A[1] - 22), ACC), (B, "机针侧线钩", (B[0] + 18, B[1] - 6), ACC)]
    for xy, t_, xt, col in lbl:
        label(ax, xy, t_, xt, col)
    ax.text(-70, ZU + 48, f"端视（从机头一侧看），主轴 φ = {phi:.0f}°，按比例", fontsize=9.5, color=INK)
    ax.set_aspect("equal")
    ax.set_xlim(-75, 175)
    ax.set_ylim(-48, ZU + 56)
    ax.axis("off")

    # ---- 右：前视传动示意（X–Z）
    b = bx
    xe, xb = 150.0, 232.0                                                  # 送布偏心、同步带
    b.plot([-22, S.X_HAND], [ZU, ZU], color=INK, lw=3.4, solid_capstyle="butt", zorder=3)
    b.plot([-8, 330], [S.ZL, S.ZL], color=INK, lw=3.4, solid_capstyle="butt", zorder=3)
    b.plot([-30, 18], [S.ZH, S.ZH], color=BLU, lw=3.4, solid_capstyle="butt", zorder=3)
    for x in (12, 120, 300):
        bushing(b, x, ZU, 3.4, 14, vertical=False)
    for x in (44, 200, 312):
        bushing(b, x, S.ZL, 3.4, 14, vertical=False)
    bushing(b, 8, S.ZH, 3.4, 12, vertical=False)
    # 刺布：曲柄在上轴左端，针杆在 x = 0
    b.add_patch(Rectangle((-22, ZU - r - 4), 8, 2 * r + 8, fc="#cfd8df", ec=INK, lw=0.9, zorder=4))
    b.plot([-18, 0], [ZU - r, ZU - r - l + 8], color=INK, lw=2.2, zorder=4)
    b.add_patch(Rectangle((-3, 20), 6, ZU - r - l + 8 - 20, fc="#dfe5ea", ec=INK, lw=0.9, zorder=4))
    b.plot([0, 0], [20, 3], color=INK, lw=1.4)
    # 挑线曲柄（同在左端，挑线杆向前伸出）
    b.add_patch(Circle((-10, ZU), 6, fc="white", ec=GRN, lw=1.4, zorder=5))
    # 同步带 1:1
    for z in (ZU, S.ZL):
        b.add_patch(Rectangle((xb - 5, z - 15), 10, 30, fc="#cfd8df", ec=INK, lw=0.9, zorder=4))
    b.plot([xb - 5, xb - 5], [ZU - 15, S.ZL + 15], color=INK, lw=0.9)
    b.plot([xb + 5, xb + 5], [ZU - 15, S.ZL + 15], color=INK, lw=0.9)
    # 齿轮 1:2（下轴大齿轮带动旋梭轴小齿轮）
    b.add_patch(Rectangle((22, S.ZL - 12), 7, 24, fc="#e7d9b8", ec=INK, lw=0.9, zorder=4))
    b.add_patch(Rectangle((22, S.ZH - 6), 7, 12, fc="#e7d9b8", ec=INK, lw=0.9, zorder=4))
    b.add_patch(Circle((-36, S.ZH), 11, fc="#eef3fa", ec=BLU, lw=1.3, zorder=4))
    # 送布：上轴上的送布偏心 + 针距调节器 → 连杆 → 送布摆轴；下轴上的抬牙偏心 → 抬牙摆轴
    b.add_patch(Circle((xe, ZU), 11, fc="white", ec=INK, lw=1.2, zorder=4))
    b.plot([xe, xe + 6], [ZU - 11, S.ZL - 26], color=INK, lw=1.8, zorder=3)
    b.add_patch(Circle((90, S.ZL), 7, fc="white", ec=INK, lw=1.2, zorder=4))
    b.plot([-14, 170], [S.ZL - 26, S.ZL - 26], color=MUTE, lw=2.6)
    b.plot([-14, 120], [S.ZL - 40, S.ZL - 40], color=MUTE, lw=2.6)
    b.plot([-8, -8], [S.ZL - 40, -3], color=MUTE, lw=1.6)
    b.add_patch(Polygon([(-14, -3.5), (12, -3.5), (10, 1.2), (-12, 1.2)], fc="#9aa5ae", ec=INK, lw=0.8, zorder=4))
    # 电机
    b.add_patch(FancyBboxPatch((S.X_HAND - 34, ZU - 40), 44, 80, boxstyle="round,pad=2", fc="#2b3440", ec=INK, zorder=4))
    b.axhline(0, color=INK, lw=1.4)
    lbl = [((-18, ZU + r + 4), "刺布曲柄", (-60, ZU + 46), INK), ((-10, ZU + 6), "挑线曲柄", (-14, ZU + 62), GRN),
           ((60, ZU), "上轴", (60, ZU + 30), INK), ((xe, ZU + 11), "送布偏心 + 针距调节器", (110, ZU + 46), INK),
           ((xb, (ZU + S.ZL) / 2), "同步带 1 : 1", (xb + 34, (ZU + S.ZL) / 2), INK),
           ((S.X_HAND - 12, ZU + 40), "直驱伺服电机（手轮内）", (S.X_HAND - 60, ZU + 62), INK),
           ((0, 60), "针杆", (40, 70), INK), ((-1, -1), "送布牙", (-62, 22), INK),
           ((-36, S.ZH - 11), "旋梭", (-70, S.ZH - 32), BLU), ((25, S.ZL - 12), "齿轮 1 : 2", (20, S.ZL - 62), INK),
           ((90, S.ZL + 7), "抬牙偏心（下轴）", (112, -15), INK), ((250, S.ZL), "下轴", (262, S.ZL + 18), INK),
           ((160, S.ZL - 26), "送布摆轴", (190, S.ZL - 40), MUTE), ((100, S.ZL - 40), "抬牙摆轴", (130, S.ZL - 58), MUTE),
           ((380, 0), "台面", (395, 12), INK)]
    for xy, t_, xt, col in lbl:
        label(b, xy, t_, xt, col)
    b.text(-70, ZU + 84, "前视传动示意（X–Z），上下轴位置按总体布置", fontsize=9.5, color=INK)
    b.set_aspect("equal")
    b.set_xlim(-75, 480)
    b.set_ylim(-110, ZU + 92)
    b.axis("off")
    fig.suptitle("WQ-LS 机构运动简图", x=0.05, y=0.97, ha="left", fontsize=12.5, color=INK)
    save(fig, "机构运动简图")



# ---------------------------------------------------------------- 总体布置
def dim(ax, p0, p1, off, text, vert=False):
    if vert:
        x = p0[0] + off
        ax.annotate("", (x, p0[1]), (x, p1[1]), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.7))
        ax.plot([p0[0], x], [p0[1], p0[1]], color=MUTE, lw=0.5)
        ax.plot([p1[0], x], [p1[1], p1[1]], color=MUTE, lw=0.5)
        ax.text(x + 3, (p0[1] + p1[1]) / 2, text, fontsize=7.5, rotation=90, va="center")
    else:
        y = p0[1] + off
        ax.annotate("", (p0[0], y), (p1[0], y), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.7))
        ax.plot([p0[0], p0[0]], [p0[1], y], color=MUTE, lw=0.5)
        ax.plot([p1[0], p1[0]], [p1[1], y], color=MUTE, lw=0.5)
        ax.text((p0[0] + p1[0]) / 2, y + 3, text, fontsize=7.5, ha="center")


def layout():
    B = S.BED
    fig, (a, b) = plt.subplots(2, 1, figsize=(9, 10), gridspec_kw=dict(height_ratios=[1.45, 1], hspace=0.1))
    # 前视外轮廓（示意线框，外观待 G3）
    a.add_patch(Rectangle((B["x0"], -B["depth"]), B["x1"] - B["x0"], B["depth"], fc="#eef1f4", ec=INK, lw=1))
    top = S.ZU + 42
    arm_bot = S.ARM["space_z"]
    head = Polygon([(-62, 34), (52, 34), (52, arm_bot), (S.X_PILLAR, arm_bot), (S.X_PILLAR, 0), (S.X_PILLAR + 78, 0),
                    (S.X_PILLAR + 78, top), (-62, top)], fc="#f6f7f8", ec=INK, lw=1)
    a.add_patch(head)
    a.plot([-110, S.X_HAND + 30], [S.ZU, S.ZU], color=ACC, lw=0.8, ls=(0, (8, 3, 2, 3)))
    a.plot([-110, 360], [S.ZL, S.ZL], color=ACC, lw=0.8, ls=(0, (8, 3, 2, 3)))
    a.plot([0, 0], [-B["depth"] - 10, top + 15], color=ACC, lw=0.8, ls=(0, (8, 3, 2, 3)))
    a.add_patch(Rectangle((S.X_HAND - 22, S.ZU - 62), 44, 124, fc="#2b3440", ec=INK, lw=1))
    a.text(S.X_HAND, S.ZU + 70, "手轮 / 直驱电机", ha="center", fontsize=8)
    a.text(4, top + 8, "机针中心线", fontsize=7.5, color=ACC)
    a.text(-128, S.ZU + 4, "上轴", fontsize=7.5, color=ACC)
    a.text(-128, S.ZL - 3, "下轴", fontsize=7.5, color=ACC)
    dim(a, (0, arm_bot), (S.X_PILLAR, arm_bot), 18, f"机臂空间 {S.ARM['space_x']:.0f}")
    dim(a, (S.X_PILLAR - 40, 0), (S.X_PILLAR - 40, arm_bot), 0, f"{S.ARM['space_z']:.0f}", vert=True)
    dim(a, (B["x0"], -B["depth"]), (B["x1"], -B["depth"]), -22, f"机座 {B['x1'] - B['x0']:.0f}")
    dim(a, (-80, 0), (-80, S.ZU), 0, f"{S.ZU:.0f}", vert=True)
    dim(a, (380, S.ZL), (380, 0), 0, f"{-S.ZL:.0f}", vert=True)
    a.set_title("前视（外形待 G3 定，这里只表示空间和轴线）", loc="left", fontsize=9.5)
    a.set_aspect("equal")
    a.set_xlim(-135, 470)
    a.set_ylim(-100, top + 40)
    a.axis("off")
    # 俯视
    b.add_patch(Rectangle((B["x0"], B["y0"]), B["x1"] - B["x0"], B["y1"] - B["y0"], fc="#eef1f4", ec=INK, lw=1))
    b.add_patch(Rectangle((-62, -40), 140, 80, fc="#f6f7f8", ec=INK, lw=0.8, ls="--"))
    b.add_patch(Rectangle((S.X_PILLAR, -30), 78, 110, fc="#f6f7f8", ec=INK, lw=0.8, ls="--"))
    b.add_patch(Rectangle((-32, -22), 64, 44, fc="#dfe5ea", ec=INK, lw=0.8))
    b.text(0, -30, "针板 / 滑板", ha="center", fontsize=7.5)
    b.text(-58, 30, "机头投影", fontsize=7.5, color=MUTE)
    b.text(S.X_PILLAR + 39, 25, "立柱投影", ha="center", fontsize=7.5, color=MUTE)
    b.plot([0], [0], marker="+", ms=12, color=ACC)
    dim(b, (B["x0"], B["y1"]), (B["x1"], B["y1"]), 14, f"{B['x1'] - B['x0']:.0f}")
    dim(b, (B["x1"], B["y0"]), (B["x1"], B["y1"]), 14, f"{B['y1'] - B['y0']:.0f}", vert=True)
    dim(b, (B["x0"], B["y0"]), (0, B["y0"]), -16, f"{-B['x0']:.0f}")
    dim(b, (B["x0"], B["y0"]), (B["x0"], 0), -16, f"{-B['y0']:.0f}", vert=True)
    b.set_title("俯视（机座 517 × 178，机针位置）", loc="left", fontsize=9.5)
    b.set_aspect("equal")
    b.set_xlim(-140, 470)
    b.set_ylim(-100, 150)
    b.axis("off")
    fig.suptitle("WQ-LS 总体布置图（单位 mm）", x=0.06, ha="left", fontsize=12, color=INK)
    save(fig, "总体布置图")


def main():
    rows, ok = checks()
    t = timing()
    kinematic()
    layout()
    (OUT / "校核.json").write_text(json.dumps(dict(ok=ok, timing=t, rows=rows), ensure_ascii=False, indent=1, default=str),
                                  encoding="utf-8")
    print("mechanism checks all green over 1–5 mm:", ok)
    for k, v in rows.items():
        print(f"{v['name']:<22} {v['limit']:<16}", " | ".join(f"{s:g}:{v['vals'][s]}({v['states'][s]})" for s in S.STITCH_RANGE))


if __name__ == "__main__":
    main()
