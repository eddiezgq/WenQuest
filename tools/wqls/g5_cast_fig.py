"""第 138 轮 G5.1：铸造工艺图和凝固仿真图（给工艺文件、给 Eddie 看）。

    python3 tools/wqls/g5_cast_fig.py <仿真目录> <输出目录> upper:3 lower:2

每一件出三张：
  铸造工艺布置（两个投影：铸件灰、浇注系统和冒口橙、冷铁蓝灰）；
  凝固时间剖面（单一色相由浅到深 = 越晚凝固；圈出热模数 > 0.35 cm 的孤立液相区）；
  凝固过程（同一剖面在几个时刻的固相分数）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap, PowerNorm  # noqa: E402

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
INK, MUTED, GRID = "#1f2328", "#59636e", "#d0d7de"
CAST, FEED, CHILL = "#9aa4ae", "#c2410c", "#2b5c8a"
SEQ = "Oranges"                      # 单一色相：越晚凝固越深
M_SHOW = 0.35                        # 圈出来的孤立区：热模数 > 0.35 cm（相当于 7 mm 平板以上）

NAME = {"upper": "上件 HSG-LS-U（机头、机臂、立柱）", "lower": "下件 HSG-LS-L（机座）"}
# 剖面：(轴, 位置 mm, 标题)
SECTIONS = {"upper": [("y", 0.0, "y = 0 正面剖（分型面）"), ("x", 380.0, "x = 380 立柱与电机座"), ("x", 0.0, "x = 0 机头（针杆）")],
            "lower": [("y", 0.0, "y = 0 正面剖"), ("x", 348.0, "x = 348 立柱脚下"), ("z", -55.0, "z = −55 底边法兰")]}
VIEWS = {"upper": [("y", "前视（x–z）"), ("z", "俯视（x–y，+y 是浇注时的上方）")],
         "lower": [("y", "前视（x–z，+z 是浇注时的上方）"), ("z", "俯视（x–y）")]}


def axes2(axis):
    return [a for a in "xyz" if a != axis]


def extent(o, dx, shape, axis):
    i = "xyz".index(axis)
    js = [j for j in range(3) if j != i]
    return [o[js[0]], o[js[0]] + shape[js[0]] * dx, o[js[1]], o[js[1]] + shape[js[1]] * dx]


def style(ax, axis):
    a, b = axes2(axis)
    ax.set_xlabel(f"{a}（mm）", color=MUTED, fontsize=9)
    ax.set_ylabel(f"{b}（mm）", color=MUTED, fontsize=9)
    ax.tick_params(colors=MUTED, labelsize=8)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.set_aspect("equal")


def crop(ax, mask, o, dx, axis, pad=25):
    i = "xyz".index(axis)
    m = mask.any(axis=i)
    js = [j for j in range(3) if j != i]
    ii, jj = np.nonzero(m)
    ax.set_xlim(o[js[0]] + ii.min() * dx - pad, o[js[0]] + (ii.max() + 1) * dx + pad)
    ax.set_ylim(o[js[1]] + jj.min() * dx - pad, o[js[1]] + (jj.max() + 1) * dx + pad)


def layout_fig(d, res, part, out):
    mat, cast, feeder = d["mat"], d["cast"], d["feeder"]
    o, dx = d["o"], float(d["dx"])
    chill = mat == 3
    fig, axs = plt.subplots(1, 2, figsize=(14, 5.6))
    for ax, (axis, title) in zip(axs, VIEWS[part]):
        i = "xyz".index(axis)
        lab = np.zeros([s for j, s in enumerate(mat.shape) if j != i], np.int8)
        lab[chill.any(i)] = 3
        lab[feeder.any(i)] = 2
        lab[cast.any(i)] = 1
        img = np.where(lab == 0, np.nan, lab).T
        ax.imshow(img, origin="lower", extent=extent(o, dx, mat.shape, axis), interpolation="nearest",
                  cmap=ListedColormap([CAST, FEED, CHILL]), vmin=0.5, vmax=3.5)
        crop(ax, cast | feeder | chill, o, dx, axis)
        style(ax, axis)
        ax.set_title(title, color=INK, fontsize=11, loc="left")
    g = res["gating"]
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (CAST, FEED, CHILL)]
    fig.legend(handles, ["铸件（含加工余量）", "浇注系统、冒口", "外冷铁 / 冷铁芯"], loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.suptitle(f"{NAME[part]}：铸造工艺布置　铸件 {res['mass_casting_kg']} kg，浇注 {res['mass_poured_kg']} kg，"
                 f"工艺出品率 {res['yield_pct']} %；浇注时间 {g['tau_s']} s，内浇道总截面 {g['A_ingate_cm2']} cm²",
                 color=INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    fig.savefig(out, dpi=110)
    plt.close(fig)


def section_fig(d, res, part, out):
    mat, cast = d["mat"], d["cast"]
    o, dx = d["o"], float(d["dx"])
    ts = d["t_sol"].astype(float)
    tmax = float(np.nanmax(np.where(cast & ~d["feeder"], ts, np.nan)))     # 色标按铸件本身（冒口凝固得晚，超出色标的显示为最深色）
    secs = SECTIONS[part]
    fig, axs = plt.subplots(1, len(secs), figsize=(6.2 * len(secs), 5.8))
    for ax, (axis, pos, title) in zip(axs, secs):
        i = "xyz".index(axis)
        k = int(round((pos - o[i]) / dx))
        M = np.take(mat, k, axis=i)
        T = np.take(ts, k, axis=i)
        ext = extent(o, dx, mat.shape, axis)
        ax.imshow(np.where(M == 3, 1.0, np.nan).T, origin="lower", extent=ext, cmap=ListedColormap([CHILL]), interpolation="nearest")
        im = ax.imshow(np.where(M == 1, T, np.nan).T, origin="lower", extent=ext, cmap=SEQ, norm=PowerNorm(0.5, vmin=0, vmax=tmax), interpolation="nearest")   # 平方根色标：薄壁几十秒的差别也看得出
        crop(ax, (mat == 1) | (mat == 3), o, dx, axis, pad=15)
        style(ax, axis)
        ax.set_title(title, color=INK, fontsize=11, loc="left")
        a, b = ["xyz".index(c) for c in axes2(axis)]
        for p in res["pockets"]:
            if not p["in_casting"] or (p["modulus_cm"] or 0) <= M_SHOW or p["volume_cm3"] < 2:
                continue
            bx = p["box_mm"]
            if not (bx[i][0] - dx <= pos <= bx[i][1] + dx):
                continue
            ax.add_patch(plt.Rectangle((bx[a][0], bx[b][0]), bx[a][1] - bx[a][0], bx[b][1] - bx[b][0], fill=False,
                                       ec=INK, lw=1.2, ls="--"))
            ax.annotate(f"孤立区 {p['volume_cm3']:.0f} cm³\nM {p['modulus_cm']} cm", (bx[a][1], bx[b][1]), fontsize=8, color=INK,
                        xytext=(4, 4), textcoords="offset points")
    cb = fig.colorbar(im, ax=axs, shrink=0.8, pad=0.01)
    cb.set_label("凝固完的时间（s）", color=MUTED)
    cb.ax.tick_params(colors=MUTED, labelsize=8)
    fig.suptitle(f"{NAME[part]}：凝固时间（浇注 {res['t_pour_c']:.0f} ℃，全部凝固 {res['t_solid_total_s']:.0f} s；"
                 f"虚线框为共晶开始前被切断、热模数 > {M_SHOW} cm 的孤立液相区）", color=INK, fontsize=11, x=0.01, ha="left")
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)


def process_fig(d, res, part, out, times=(10, 30, 60, 120)):
    mat = d["mat"]
    o, dx = d["o"], float(d["dx"])
    met = mat == 1
    snap_t, snaps = d["snap_t"], d["snaps"]
    axis, pos, title = SECTIONS[part][0]
    i = "xyz".index(axis)
    k = int(round((pos - o[i]) / dx))
    fig, axs = plt.subplots(1, len(times), figsize=(4.6 * len(times), 3.6))
    for ax, tt in zip(axs, times):
        j = int(np.argmin(np.abs(snap_t - tt)))
        fs = np.full(mat.shape, np.nan, np.float32)
        fs[met] = snaps[j].astype(np.float32)
        F = np.take(fs, k, axis=i)
        ax.imshow((1 - F).T, origin="lower", extent=extent(o, dx, mat.shape, axis), cmap=SEQ, vmin=0, vmax=1, interpolation="nearest")
        crop(ax, met, o, dx, axis, pad=10)
        style(ax, axis)
        ax.set_title(f"t = {snap_t[j]:.0f} s", color=INK, fontsize=10, loc="left")
    fig.suptitle(f"{NAME[part]}：凝固过程（{title}；颜色越深液相越多）", color=INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(out, dpi=110)
    plt.close(fig)


def main():
    sim, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for spec in sys.argv[3:]:
        part, var = spec.split(":")
        d = np.load(sim / f"cast_{part}_v{var}.npz")
        res = json.loads((sim / f"cast_{part}_v{var}.json").read_text())
        cn = {"upper": "上件", "lower": "下件"}[part]
        layout_fig(d, res, part, out / f"铸造工艺_{cn}.png")
        section_fig(d, res, part, out / f"凝固时间_{cn}.png")
        process_fig(d, res, part, out / f"凝固过程_{cn}.png")
        print(part, "ok")


if __name__ == "__main__":
    main()
