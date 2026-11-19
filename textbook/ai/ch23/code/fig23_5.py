"""23.5 节的图：端到端与分模块，两列成绩加一列归因。

图 23.4.1：（a）总体与罕见情形两组柱——左边端到端赢，右边分模块赢；
（b）分模块的误差能归到哪一环（感知 / 控制），**端到端这一列是空的**。
"""
import numpy as np

from _ch23 import (CAM, LANE, fit_ls, lane_obs, lane_scene, perceive_lane,
                   poly_features, true_steer)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

LANE_CTRL = dict(LANE)
LANE_CTRL["ratio"] = LANE["ratio"] * 1.04
LANE_CTRL["k_e"] = LANE["k_e"] * 0.94

tr = lane_scene(8000, seed=1)
w_e2e = fit_ls(poly_features(lane_obs(tr, seed=1)),
               true_steer(tr["e"], tr["psi"], tr["kappa"]), lam=1e-3)


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def run(sc, seed):
    U = lane_obs(sc, seed=seed)
    y = true_steer(sc["e"], sc["psi"], sc["kappa"])
    pc = perceive_lane(U, CAM["pitch"], CAM["height"])
    return {
        "e2e": rmse(poly_features(U) @ w_e2e, y),
        "mod": rmse(true_steer(pc["e"], pc["psi"], pc["kappa"], LANE_CTRL), y),
        "perc": rmse(true_steer(pc["e"], pc["psi"], pc["kappa"], LANE), y),
        "ctrl": rmse(true_steer(sc["e"], sc["psi"], sc["kappa"], LANE_CTRL), y),
    }


r_all = run(lane_scene(4000, seed=55), 55)
r_rare = run(lane_scene(2000, seed=77, kappa_max=0.05, e_sigma=2.5), 77)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 两列成绩
xs = np.arange(2)
e2e = [r_all["e2e"], r_rare["e2e"]]
mod = [r_all["mod"], r_rare["mod"]]
a.bar(xs - 0.19, e2e, 0.36, color=C["x"], label=T("端到端", "end-to-end"))
a.bar(xs + 0.19, mod, 0.36, color=C["z"], label=T("分模块", "modular"))
for i in range(2):
    a.annotate(f"{e2e[i]:.3f}°", xy=(i - 0.19, e2e[i]), xytext=(0, 4),
               textcoords="offset points", ha="center", fontsize=8.5, color=C["x"])
    a.annotate(f"{mod[i]:.3f}°", xy=(i + 0.19, mod[i]), xytext=(0, 4),
               textcoords="offset points", ha="center", fontsize=8.5, color=C["z"])
a.set_xticks(xs)
a.set_xticklabels([T("总体（与训练同分布）", "overall (in-distribution)"),
                   T("罕见情形（半径 20 m 急弯）", "rare case (20 m radius turn)")], fontsize=9)
a.set_ylabel(T("方向盘角误差（均方根，°）", "steering-angle RMSE (deg)"))
a.set_ylim(0, max(e2e + mod) * 1.30)
a.set_title(T("(a) 左边端到端赢，右边分模块赢",
              "(a) end-to-end wins on the left, modular on the right"), fontsize=10)
a.legend(fontsize=8.5, loc="upper left", framealpha=0.92)
a.annotate(T(f"端到端好 {(1 - e2e[0] / mod[0]) * 100:.0f}%",
             f"end-to-end {(1 - e2e[0] / mod[0]) * 100:.0f}% better"),
           xy=(0, max(e2e[0], mod[0])), xytext=(0, 26), textcoords="offset points",
           ha="center", fontsize=8.5, color=C["accent"])
a.annotate(T(f"端到端差 {e2e[1] / mod[1]:.1f} 倍",
             f"end-to-end {e2e[1] / mod[1]:.1f}$\\times$ worse"),
           xy=(1, max(e2e[1], mod[1])), xytext=(0, 26), textcoords="offset points",
           ha="center", fontsize=8.5, color=C["accent"])
a.grid(alpha=0.25, lw=0.5, axis="y")

# ---------------- (b) 误差归到哪一环
perc = [r_all["perc"], r_rare["perc"]]
ctrl = [r_all["ctrl"], r_rare["ctrl"]]
b.bar(xs - 0.20, perc, 0.30, color=C["y"],
      label=T("第一环 感知（e、ψ、κ 估错）", "stage 1 perception (e, $\\psi$, $\\kappa$)"))
b.bar(xs + 0.10, ctrl, 0.30, color=C["accent"],
      label=T("第二环 控制（车辆参数不准）", "stage 2 control (vehicle parameters)"))
b.bar(xs + 0.40, mod, 0.30, color=C["z"], alpha=0.55,
      label=T("分模块合计", "modular total"))
for i in range(2):
    for off, val, col in ((-0.20, perc[i], C["y"]), (0.10, ctrl[i], C["accent"]),
                          (0.40, mod[i], C["z"])):
        b.annotate(f"{val:.2f}", xy=(i + off, val), xytext=(0, 3),
                   textcoords="offset points", ha="center", fontsize=8, color=col)
b.set_xticks(xs + 0.10)
b.set_xticklabels([T("总体", "overall"), T("罕见情形", "rare case")], fontsize=9)
b.set_ylabel(T("折成方向盘角误差（°）", "contribution to steering RMSE (deg)"))
b.set_ylim(0, max(perc + ctrl + mod) * 1.42)
b.set_title(T("(b) 分模块能说出错在哪一环", "(b) the modular stack can name the stage at fault"),
            fontsize=10)
b.legend(fontsize=8, loc="upper left", framealpha=0.92)
b.annotate(T("端到端没有这一组柱：\n它只给你一个变大的数",
             "end-to-end has no such bars:\nit only hands you one bigger number"),
           xy=(0.97, 0.97), xycoords="axes fraction", ha="right", va="top",
           fontsize=8.5, color=C["x"])
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig23_4_1")
