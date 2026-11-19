"""23.6 节的图之一：两种加数据策略的学习曲线。

图 23.5.1：（a）同一个误差预算，随机加数据与按不确定性挑数据各要标多少条；
（b）挑出来的到底是什么——标注集里难例的占比，以及最后易例、难例两列的误差。
"""
import numpy as np

from _ch23 import fit_ls, lane_obs, lane_scene, leverage, poly_features, pool_scene, true_steer
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_POOL, N_SEED, BATCH, N_ROUND, EASY = 9000, 60, 60, 24, 0.93

pool = pool_scene(N_POOL, seed=2, easy_frac=EASY)
X_pool = poly_features(lane_obs(pool, seed=2))
y_pool = true_steer(pool["e"], pool["psi"], pool["kappa"])

sets = {}
for tag, sc, sd in (("easy", lane_scene(3000, seed=61, kappa_max=0.0004, e_sigma=0.10), 61),
                    ("hard", lane_scene(3000, seed=62, kappa_max=0.009, e_sigma=1.10), 62)):
    U = lane_obs(sc, seed=sd)
    sets[tag] = (poly_features(U), true_steer(sc["e"], sc["psi"], sc["kappa"]))


def rmse(X, y, w):
    return float(np.sqrt(np.mean((X @ w - y) ** 2)))


def balanced(w):
    return float(np.sqrt(0.5 * rmse(*sets["easy"], w) ** 2 + 0.5 * rmse(*sets["hard"], w) ** 2))


def run(strategy):
    g = np.random.default_rng(404)
    idx = list(g.choice(N_POOL, N_SEED, replace=False))
    rest = np.setdiff1d(np.arange(N_POOL), idx)
    n, err, share = [], [], []
    for _ in range(N_ROUND + 1):
        w = fit_ls(X_pool[idx], y_pool[idx], lam=1e-3)
        n.append(len(idx))
        err.append(balanced(w))
        share.append(float(pool["is_hard"][idx].mean()) * 100)
        if len(rest) < BATCH:
            break
        pick = (g.choice(len(rest), BATCH, replace=False) if strategy == "random"
                else np.argsort(leverage(X_pool[rest], X_pool[idx]))[-BATCH:])
        idx = idx + list(rest[pick])
        rest = np.delete(rest, pick)
    return np.array(n), np.array(err), np.array(share), w


n_r, e_r, s_r, w_r = run("random")
n_a, e_a, s_a, w_a = run("active")

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 学习曲线
TARGET = max(e_r[-1], e_a[-1]) * 1.15
a.plot(n_r, e_r, "o-", color=C["muted"], lw=2.2, ms=5, label=T("随机加数据", "random sampling"))
a.plot(n_a, e_a, "s-", color=C["x"], lw=2.2, ms=5,
       label=T("按不确定性挑数据", "uncertainty sampling"))
a.axhline(TARGET, color=C["accent"], lw=1.6, ls="--",
          label=T(f"误差预算 {TARGET:.3f}°", f"error budget {TARGET:.3f}°"))
nr = int(n_r[np.where(e_r <= TARGET)[0][0]])
na = int(n_a[np.where(e_a <= TARGET)[0][0]])
for x, col, tag in ((nr, C["muted"], T("随机", "random")), (na, C["x"], T("挑数据", "picked"))):
    a.axvline(x, color=col, lw=1.3, ls=":")
    a.annotate(T(f"{tag} {x} 条", f"{tag}: {x}"), xy=(x, TARGET), xytext=(5, 26),
               textcoords="offset points", fontsize=8.5, color=col)
a.set_xlabel(T("已标注的样本数", "labelled samples"))
a.set_ylabel(T("方向盘角误差（易例、难例等权重，°）",
               "steering RMSE (easy and hard weighted equally, deg)"))
a.set_title(T("(a) 同一个误差预算，挑数据省多少标注量",
              "(a) labels needed to reach the same error budget"), fontsize=10)
a.legend(fontsize=8.5, loc="upper right", framealpha=0.92)
a.annotate(T(f"省 {(1 - na / nr) * 100:.0f}%（{nr / na:.1f} 倍）",
             f"{(1 - na / nr) * 100:.0f}% fewer ({nr / na:.1f}$\\times$)"),
           xy=(0.97, 0.45), xycoords="axes fraction", xytext=(0, 0),
           textcoords="offset points", ha="right", fontsize=9, color=C["accent"])
a.set_ylim(min(e_r.min(), e_a.min()) * 0.85, float(e_r[1]) * 1.9)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 挑出来的是什么
b.plot(n_r, s_r, "o-", color=C["muted"], lw=2.2, ms=5, label=T("随机加数据", "random"))
b.plot(n_a, s_a, "s-", color=C["x"], lw=2.2, ms=5,
       label=T("按不确定性挑数据", "uncertainty sampling"))
b.axhline(float(pool["is_hard"].mean()) * 100, color=C["z"], lw=1.6, ls="--",
          label=T(f"候选池里难例只占 {pool['is_hard'].mean() * 100:.0f}%",
                  f"hard cases are only {pool['is_hard'].mean() * 100:.0f}% of the pool"))
b.set_xlabel(T("已标注的样本数", "labelled samples"))
b.set_ylabel(T("标注集里难例的占比（%）", "share of hard cases among the labels (%)"))
b.set_title(T("(b) 它自己把弯道那一片挑了出来",
              "(b) it finds the curves on its own"), fontsize=10)
b.legend(fontsize=8.5, loc="upper right", framealpha=0.92)
b.set_ylim(0, 132)

ins = b.inset_axes((0.07, 0.555, 0.42, 0.335))
vals_e = [rmse(*sets["easy"], w_r), rmse(*sets["easy"], w_a)]
vals_h = [rmse(*sets["hard"], w_r), rmse(*sets["hard"], w_a)]
xs = np.arange(2)
ins.bar(xs - 0.19, vals_e, 0.36, color=C["muted"], label=T("易例", "easy"))
ins.bar(xs + 0.19, vals_h, 0.36, color=C["x"], label=T("难例", "hard"))
ins.set_xticks(xs)
ins.set_xticklabels([T("随机", "random"), T("挑数据", "picked")], fontsize=7.5)
ins.tick_params(axis="y", labelsize=7)
ins.set_title(T("标满之后的两列", "the two columns, once full"), fontsize=8)
ins.legend(fontsize=6.5, loc="upper right", framealpha=0.9)
ins.set_ylim(0, max(vals_h) * 1.45)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig23_5_1")
