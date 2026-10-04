"""图 6.3.1：致密性定理——有界数列 sin n 不收敛；二分法一次次保留“含无穷多项”的一半，挑出收敛的子数列。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

N = 3000
n = np.arange(1, N + 1)
s = np.sin(n.astype(float))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.4, 1]})
a1.plot(n, s, ".", color=MUTED, ms=1.5)
target = 0.5
last, ks, vs = 0, [], []
for k in range(1, 6):
    idx = np.nonzero((n > last) & (np.abs(s - target) < 10.0 ** (-k / 1.6)))[0]
    if len(idx) == 0:
        break
    last = int(n[idx[0]])
    ks.append(last)
    vs.append(s[idx[0]])
a1.plot(ks, vs, "o-", color=RED, ms=6, lw=1)
a1.axhline(target, color=RED, lw=0.8, ls="--")
a1.set_xlabel("n")
a1.set_ylabel("sin n")
a1.set_title(T("sin n 不收敛，但有子数列趋于 0.5（红点）", "sin n diverges, but a subsequence tends to 0.5 (red)"), fontsize=10)
clean(a1)
a, b = -1.0, 1.0
for k in range(7):
    a2.plot([a, b], [k, k], color=BLUE, lw=4)
    m = (a + b) / 2
    left = np.count_nonzero((s >= a) & (s <= m))
    right = np.count_nonzero((s >= m) & (s <= b))
    a2.text(b + 0.03, k, f"{max(left, right)}", va="center", fontsize=8, color=MUTED)
    a, b = (a, m) if left >= right else (m, b)
a2.invert_yaxis()
a2.set_yticks(range(7))
a2.set_yticklabels([str(k) for k in range(7)])
a2.set_xlim(-1.05, 1.25)
a2.set_ylabel(T("二分的次数", "halvings"))
a2.set_title(T("每次保留项数多的一半（数字：前 3000 项中落在其中的个数）", "Keep the half with more terms (count among the first 3000)"), fontsize=9)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig6_3_1")
