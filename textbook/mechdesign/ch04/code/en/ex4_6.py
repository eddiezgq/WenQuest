"""Section 4.6 Tolerancing principles: position of the two anchor-bolt holes of the palletizing-conveyor pillow block (PB-6207, Chapter 3), judged by the independency principle (RFS) and by the maximum material requirement (MMR, Ⓜ);
bonus tolerance, virtual condition boundary, functional gauge; Monte Carlo assembly of a batch of parts confirms that every part accepted under MMR can be assembled (Example 4.6.1, Figure 4.6.1)."""
import math
import random
import sys
from pathlib import Path

import _ch4 as H
from bookout import T, figure, out, style

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ch03" / "code"))
import _ch3 as C3                       # noqa: E402  Design rules of the pillow block (Section 3.8)

p = C3.pillow_params("6207")
F = 10.0                                # Major diameter of the M10 screw (maximum material)
DH = p["dh"]                            # Anchor-bolt hole Ø11 (GB/T 5277, medium fit); maximum material size of the hole MMC = 11.0
IT13 = H.mdstd.it(13, DH) / 1000        # Size tolerance of the hole H13
LMC = DH + IT13
# Fixed fastener (screw threaded into a tapped hole in the frame): position tolerance shared by the two parts, t = (H - F)/2, Ø0.5 each (the formula in the appendix of ASME Y14.5)
TPOS = (DH - F) / 2
VC = DH - TPOS                          # Virtual condition size of the hole (maximum material virtual condition boundary) = diameter of the gauge pins of the functional gauge
TPOS_FRAME = TPOS                       # Position tolerance of the tapped holes in the frame Ø0.5 (on the pitch-diameter axis, RFS)

# ---------------------------------------------------------------- A batch of parts: size and position errors of the drilled holes (process capability set by this book)
N = 5000
rng = random.Random(46)
SD_POS = 0.10                           # Standard deviation of position error in each coordinate direction, mm (holes drilled on a machining center, fixture location and machine errors combined)
MU_D, SD_D = DH + 0.11, 0.045           # Hole size: twist drills cut slightly oversize


def hole():
    d = rng.gauss(MU_D, SD_D)
    while not DH <= d <= LMC:                         # Holes outside the size tolerance are first rejected by the size check; only position is considered here
        d = rng.gauss(MU_D, SD_D)
    ex, ey = rng.gauss(0, SD_POS), rng.gauss(0, SD_POS)
    return d, ex, ey


parts = [[hole(), hole()] for _ in range(N)]
frames = [[(rng.gauss(0, SD_POS * 0.8), rng.gauss(0, SD_POS * 0.8)) for _ in range(2)] for _ in range(N)]


def pos_dia(h):
    return 2 * math.hypot(h[1], h[2])     # Position error value (diameter)


def ok_rfs(part):
    return all(pos_dia(h) <= TPOS for h in part)


def ok_mmr(part):
    return all(pos_dia(h) <= TPOS + (h[0] - DH) for h in part)


def gauge(part):
    """Functional gauge: two gauge pins of Ø VC fixed at the theoretical positions; the part is accepted if it fits over them"""
    return all(math.hypot(h[1], h[2]) + VC / 2 <= h[0] / 2 + 1e-12 for h in part)


def frame_ok(fr):
    return all(2 * math.hypot(*q) <= TPOS_FRAME for q in fr)


def assembles(part, fr):
    """Assembly: the axis of each screw is the axis of the tapped hole in the frame; the screw (Ø10) must pass through the hole of the pillow block"""
    return all(math.hypot(h[1] - q[0], h[2] - q[1]) + F / 2 <= h[0] / 2 for h, q in zip(part, fr))


rfs = [ok_rfs(x) for x in parts]
mmr = [ok_mmr(x) for x in parts]
gau = [gauge(x) for x in parts]
assert mmr == gau                       # The gauge is the physical form of the MMR criterion: both are the same inequality (this only checks that the program has no mistake)
good_frames = [fr for fr in frames if frame_ok(fr)]
asm = [assembles(x, good_frames[i % len(good_frames)]) for i, x in enumerate(parts)]
n_rfs, n_mmr = sum(rfs), sum(mmr)
extra = [i for i in range(N) if mmr[i] and not rfs[i]]
asm_extra = sum(asm[i] for i in extra)
asm_mmr = sum(asm[i] for i, m in enumerate(mmr) if m)
rej = [i for i in range(N) if not mmr[i]]
asm_rej = sum(asm[i] for i in rej)
# Worst case: frame hole displaced to the limit of its position tolerance, directly towards the deviation of the pillow-block hole; the limiting part accepted under MMR (on the virtual condition boundary) just fits
worst_gap = (VC - F) / 2 - TPOS_FRAME / 2

# ---------------------------------------------------------------- Figure
plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={"width_ratios": [1.35, 1.0]})
xs = [h[0] for x in parts[:800] for h in x]
ys = [pos_dia(h) for x in parts[:800] for h in x]
cols = []
for x in parts[:800]:
    for h in x:
        cols.append("#2ca02c" if pos_dia(h) <= TPOS else "#ff7f0e" if pos_dia(h) <= TPOS + h[0] - DH else "#d62728")
a0.scatter(xs, ys, s=3, c=cols, lw=0)
a0.plot([DH, LMC], [TPOS, TPOS], color=H.INK, lw=0.9, ls="--")
a0.plot([DH, LMC], [TPOS, TPOS + IT13], color=H.INK, lw=1.0)
a0.text(LMC - 0.005, TPOS + IT13 + 0.02, T("MMR 合格线：Ø0.5 + 补偿", "MMR limit: Ø0.5 + bonus"), ha="right", fontsize=6.8)
a0.text(LMC - 0.005, TPOS - 0.07, T("RFS 合格线：Ø0.5", "RFS limit: Ø0.5"), ha="right", fontsize=6.8)
a0.set_xlabel(T("孔的实际直径 / mm", "Actual hole diameter / mm"), fontsize=7.5)
a0.set_ylabel(T("位置度误差（直径）/ mm", "Position error (dia.) / mm"), fontsize=7.5)
a0.tick_params(labelsize=6.8)
a0.set_xlim(DH - 0.01, LMC + 0.01)
a0.set_ylim(0, 1.0)
a0.set_title(T("(a) 动态公差图（每点一个孔）", "(a) Dynamic tolerance diagram (one dot per hole)"), fontsize=8)
# (b) Functional gauge: gauge pins Ø VC, maximum and least material of the hole
from matplotlib.patches import Circle, Rectangle  # noqa: E402
for cx in (-1, 1):
    a1.add_patch(Circle((cx * 1.6, -0.2), DH / 2 / 8, fc="none", ec="#1f77b4", lw=0.9, ls="--"))
    a1.add_patch(Circle((cx * 1.6, -0.2), VC / 2 / 8, fc="#ddd", ec=H.INK, lw=0.9))
a1.add_patch(Rectangle((-2.7, -1.35), 5.4, 2.1, fc="#f2f2f2", ec=H.INK, lw=0.7, zorder=0))
a1.text(0, -1.3, T("量规底板（贴基准 A，俯视）", "gauge base (on datum A, top view)"), ha="center", va="bottom", fontsize=6.4)
a1.add_patch(Rectangle((-2.7, 0.75), 5.4, 0.12, fc="#666", ec=H.INK, lw=0.5))      # Locating stop: datum B (one side of the part rests against it)
a1.add_patch(Rectangle((-2.82, -1.35), 0.12, 2.22, fc="#666", ec=H.INK, lw=0.5))   # Locating stop: datum C
a1.text(2.75, 0.81, "B", fontsize=7, va="center")
a1.text(-2.95, -0.25, "C", fontsize=7, va="center", ha="right")
a1.text(-1.6, -0.2, f"Ø{VC:.1f}", ha="center", va="center", fontsize=7)
a1.text(1.6, -0.2, f"Ø{VC:.1f}", ha="center", va="center", fontsize=7)
a1.text(0, 1.3, T("测销 Ø = 实效尺寸 11 − 0.5", "pins Ø = virtual condition 11 − 0.5"), ha="center", fontsize=6.8)
a1.text(0, 1.02, T("虚线：孔的最大实体 Ø11", "dashed: hole at MMC Ø11"), ha="center", fontsize=6.6, color="#1f77b4")
a1.annotate("", xy=(-1.6, -1.0), xytext=(1.6, -1.0), arrowprops=dict(arrowstyle="<->", lw=0.6))
a1.text(0, -0.95, f"{p['Lh']:.0f}", ha="center", va="bottom", fontsize=7)
for cx in (-1.6, 1.6):
    a1.plot([cx, cx], [-0.6, -1.05], color=H.INK, lw=0.4)
a1.set_xlim(-3.1, 3.0)
a1.set_ylim(-1.6, 1.5)
a1.set_aspect("equal")
a1.axis("off")
a1.set_title(T("(b) 功能量规", "(b) Functional gauge"), fontsize=8)
fig.tight_layout()
figure(fig, "fig4_6_1")

out(Lh=p["Lh"], dh=DH, F=F, it13=IT13, LMC=LMC, tpos=TPOS, vc=VC, t_lmc=TPOS + IT13, N=N, sd_pos=SD_POS, mu_d=MU_D,
    p_rfs=100 * n_rfs / N, p_mmr=100 * n_mmr / N, n_extra=len(extra), asm_extra=100 * asm_extra / max(1, len(extra)),
    asm_mmr=100 * asm_mmr / max(1, n_mmr), n_rej=len(rej), asm_rej=100 * asm_rej / max(1, len(rej)),
    worst_gap=worst_gap, scrap_saved=n_mmr - n_rfs)
