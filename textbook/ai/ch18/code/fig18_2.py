"""18.2 节的示意图。

图 18.2.1：（a）每多一条正确的接触，能走的折法就少一个量级——而**混进一条错的**，基态直接
被排除在外；（b）接触是从比对里来的，比对太浅就什么都看不出来。
"""
import numpy as np

from _ch18 import (coevolution_scores, contact_precision, contacts,
                   enumerate_folds, fold_energy, information_curve,
                   one_wrong_contact, simulate_msa)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

SEQ = "HPHPHPHHHPHPPHPH"
N = len(SEQ)
folds = enumerate_folds(N)
energies = np.fromiter((fold_energy(f, SEQ) for f in folds), int, len(folds))
fc = [contacts(f) for f in folds]
native = fc[int(np.argmin(energies))]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 接触信息值多少
KS = (0, 1, 2, 3, 4, 5, 6)
rows = information_curve(fc, energies, native, KS, seed=0)
ks = [r[0] for r in rows]
left = [r[1] for r in rows]
frac = [r[3] for r in rows]

a.semilogy(ks, left, "o-", color=C["z"], lw=2.0, ms=6,
           label=T("还剩多少种折法", "folds still allowed"))
wrong_left, wrong_ok = one_wrong_contact(fc, energies, native, N, 4, seed=1)
a.semilogy([4], [wrong_left], "X", color=C["x"], ms=13,
           label=T("四条里错一条", "four restraints, one of them wrong"))
a.annotate(T(f"剩下的里一个基态都没有\n（找回基态 {wrong_ok:.0f}%）",
             f"none of them is the ground state\n({wrong_ok:.0f}% recovered)"),
           xy=(4, wrong_left), xytext=(0.15, 22.0), fontsize=8, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.set_xlabel(T("给了几条正确的接触", "number of correct contacts given"))
a.set_ylabel(T("还剩多少种折法（对数）", "folds still allowed (log)"))
a.set_title(T("(a) 一条接触，少一个量级", "(a) Each contact removes an order of magnitude"),
            fontsize=10)
a.grid(alpha=0.25, lw=0.5, which="both")
a.legend(fontsize=8, loc="center left")

a2 = a.twinx()
a2.plot(ks, frac, "s--", color=C["y"], lw=1.6, ms=5)
a2.set_ylabel(T("剩下的里基态占几成（%）", "share of survivors that are native (%)"), color=C["y"])
a2.tick_params(axis="y", colors=C["y"])

# ---------------- (b) 比对深度
NAT = sorted(native)
DEPTHS = (10, 20, 30, 50, 100, 200, 300, 600, 1000)
ys, lo, hi = [], [], []
for d in DEPTHS:
    ps = [contact_precision(coevolution_scores(simulate_msa(N, NAT, d, seed=sd, coupling=0.9)),
                            NAT, top=len(NAT)) for sd in range(10)]
    ys.append(float(np.mean(ps))); lo.append(float(np.min(ps))); hi.append(float(np.max(ps)))
b.fill_between(DEPTHS, lo, hi, color=C["z"], alpha=0.15)
b.semilogx(DEPTHS, ys, "o-", color=C["z"], lw=2.0, ms=5)
b.axvline(30, color=C["x"], ls=":", lw=1.4)
b.annotate(T("论文说中位深度低于约 30 条时\n精度明显下降", "below a median depth of ~30\nthe paper reports a clear drop"),
           xy=(30, 0.35), xytext=(45, 0.18), fontsize=8, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
b.set_xlabel(T("比对里有多少条同源序列", "number of homologous sequences in the alignment"))
b.set_ylabel(T("前 L 对接触的命中率", "precision of the top-L contacts"))
b.set_ylim(0, 1.05)
b.set_title(T("(b) 接触是从比对里来的", "(b) Contacts come from the alignment"), fontsize=10)
b.grid(alpha=0.25, lw=0.5, which="both")

fig.tight_layout()
figure(fig, "fig18_2_1")
