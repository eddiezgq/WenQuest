"""19.4 节的示意图：降尺度能把统计做对，不能保证某一点上是对的。

图 19.4.1：（a）同一个粗场配两个同样合法的真实细场；（b）降尺度只看粗场，
所以给出同一个答案——它补的是统计，不是这一次的实况。
"""
import numpy as np

from _ch19 import (coarse_grain, downscale_learned, downscale_naive, fine_field,
                   same_coarse_variant, sharpness)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N, F, SLOPE = 512, 8, 1.0
SHOW = 160                                   # 只画前一段，细节才看得清

truth = fine_field(N, seed=0, slope=SLOPE)
coarse = coarse_grain(truth, F)
alt = same_coarse_variant(truth, F, seed=11, slope=SLOPE)
amp = float(np.std(truth - downscale_naive(coarse, F)))
d1 = downscale_learned(coarse, F, amp * 0.9, seed=3, slope=SLOPE)
d2 = downscale_learned(coarse_grain(alt, F), F, amp * 0.9, seed=3, slope=SLOPE)
step = np.repeat(coarse, F)
x = np.arange(N)

fig, (a, b) = plt.subplots(2, 1, figsize=(10.6, 6.6), sharex=True)

# ---------------- (a) 一个粗场，两个真实细场
a.step(x[:SHOW], step[:SHOW], where="mid", color=C["ink"], lw=2.6,
       label=T("全球模式看到的粗场（两者完全相同）",
               "the coarse field the global model sees (identical for both)"))
a.plot(x[:SHOW], truth[:SHOW], "-", color=C["x"], lw=1.6,
       label=T("真实细场 甲", "true fine field A"))
a.plot(x[:SHOW], alt[:SHOW], "-", color=C["y"], lw=1.6,
       label=T("真实细场 乙", "true fine field B"))
for e in range(0, SHOW + 1, F):
    a.axvline(e, color=C["muted"], lw=0.5, alpha=0.4)
a.text(0.012, 0.045, T(f"两者在粗网格上相关 {np.corrcoef(coarse_grain(alt, F), coarse)[0, 1]:.3f}，"
             f"在细网格上只有 {np.corrcoef(alt, truth)[0, 1]:.3f}",
             f"correlation {np.corrcoef(coarse_grain(alt, F), coarse)[0, 1]:.3f} on the coarse "
             f"grid, only {np.corrcoef(alt, truth)[0, 1]:.3f} on the fine grid"),
       transform=a.transAxes, fontsize=9, color=C["ink"],
       bbox=dict(fc="white", ec="none", alpha=0.85, pad=2.0))
a.set_ylabel(T("场的数值", "field value"))
a.set_title(T("(a) 粗场一模一样，细节却可以完全不同",
              "(a) The same coarse field, with completely different detail"), fontsize=10)
a.legend(fontsize=8, loc="upper right", ncol=1)
a.grid(alpha=0.2, lw=0.5)

# ---------------- (b) 降尺度只有一个答案
b.plot(x[:SHOW], truth[:SHOW], "-", color=C["x"], lw=1.3, alpha=0.55,
       label=T("真实细场 甲", "true fine field A"))
b.plot(x[:SHOW], alt[:SHOW], "-", color=C["y"], lw=1.3, alpha=0.55,
       label=T("真实细场 乙", "true fine field B"))
b.plot(x[:SHOW], d1[:SHOW], "-", color=C["z"], lw=2.6,
       label=T("学出来的降尺度（对甲、对乙给出同一条线）",
               "learned downscaling (one and the same curve for A and B)"))
b.plot(x[:SHOW], d2[:SHOW], "--", color="white", lw=1.1, zorder=6)
b.text(0.012, 0.045, T(f"两条降尺度结果相关 {np.corrcoef(d1, d2)[0, 1]:.3f}——"
             f"它看的只是粗场；锐度 {sharpness(d1):.3f} 对上了真实的 {sharpness(truth):.3f}，"
             f"可逐点误差 {np.sqrt(np.mean((d1 - truth) ** 2)):.2f} 并不比直接复制的 "
             f"{np.sqrt(np.mean((downscale_naive(coarse, F) - truth) ** 2)):.2f} 小",
             f"the two downscaled curves correlate {np.corrcoef(d1, d2)[0, 1]:.3f} — it only "
             f"sees the coarse field"),
       transform=b.transAxes, fontsize=9, color=C["z"],
       bbox=dict(fc="white", ec="none", alpha=0.85, pad=2.0))
b.set_xlabel(T("细网格格点", "fine-grid point"))
b.set_ylabel(T("场的数值", "field value"))
b.set_title(T("(b) 它补的是统计上像样的细节，不是这一次的实况",
              "(b) It adds statistically plausible detail, not this particular truth"),
            fontsize=10)
b.legend(fontsize=8, loc="upper right")
b.grid(alpha=0.2, lw=0.5)
for ax in (a, b):
    ax.margins(y=0.30)

fig.tight_layout()
figure(fig, "fig19_4_1")
