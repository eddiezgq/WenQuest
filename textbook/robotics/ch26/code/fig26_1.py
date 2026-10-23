"""26.1 节的示意图。

图 26.1.1：(a) 书中 UR5e 的 78 个参数（每个连杆十个惯性参数、转子惯量、库仑摩擦、黏性摩擦）按可辨识性分类：
              基参数（可单独辨识或作为组合的代表）、只以组合出现而被并入基参数的、对力矩毫无影响的；按连杆分开画；
          (b) 算例 26.1.1：广义动量观测器的残差。实线：模型带夹爪和毛坯；虚线：模型里没有负载；点线：真实的外力矩 Jᵀℱ。
              只画受影响最大的关节 3；阴影为碰撞的 0.1 s。
"""
import numpy as np

from _ch26 import collision_demo, full_names, ur_base_set
from bookout import COLORS as C, T, figure, style

plt = style()
W, ind, dep, K, rank = ur_base_set()
names = full_names(6)
zero = {j for j in dep if np.abs(W[:, j]).max() < 1e-9}
depn = set(dep) - zero
groups = [list(range(10 * i, 10 * i + 10)) + [60 + i] for i in range(6)] + [list(range(66, 78))]
labels = [T(f"连杆 {i + 1}", f"link {i + 1}") for i in range(6)] + [T("摩擦", "friction")]
cnt = np.array([[sum(1 for j in g if j in set(ind)), sum(1 for j in g if j in depn), sum(1 for j in g if j in zero)] for g in groups])
fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.1), gridspec_kw=dict(width_ratios=[1, 1.35]))
ax = axs[0]
x = np.arange(len(groups))
cols = [C["z"], "#9ecae1", "#d9d9d9"]
labs = [T(f"基参数（{len(ind)}）", f"base ({len(ind)})"), T(f"并入组合（{len(depn)}）", f"merged ({len(depn)})"),
        T(f"无影响（{len(zero)}）", f"no effect ({len(zero)})")]
bottom = np.zeros(len(groups))
for k in range(3):
    ax.bar(x, cnt[:, k], bottom=bottom, color=cols[k], ec=C["ink"], lw=0.5, label=labs[k])
    bottom += cnt[:, k]
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel(T("参数个数", "number of parameters"))
ax.set_title(T("(a) 78 个参数中能辨识的", "(a) which of the 78 parameters are identifiable"), fontsize=11)
ax.legend(fontsize=9, frameon=False, loc="upper right")
ax.set_ylim(0, 14.5)
ax.grid(alpha=0.25, axis="y")
ax = axs[1]
t, R, Rn, E = collision_demo()
j = 2
ax.axvspan(0.70, 0.80, color="#fde0c5", alpha=0.7, lw=0)
ax.plot(t, E[:, j], ":", color=C["ink"], lw=1.6, label=T("真实的外力矩 (Jᵀℱ)₃", "true external torque (Jᵀℱ)₃"))
ax.plot(t, R[:, j], color=C["x"], lw=1.6, label=T("残差 r₃：模型带负载", "residual r₃: model with payload"))
ax.plot(t, Rn[:, j], "--", color=C["z"], lw=1.3, label=T("残差 r₃：模型没有负载", "residual r₃: model without payload"))
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("力矩 / (N·m)", "torque / (N·m)"))
ax.set_title(T("(b) 用广义动量检测碰撞（关节 3）", "(b) collision detection by generalized momentum (joint 3)"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="lower left")
ax.grid(alpha=0.25)
ax.set_xlim(0, t[-1])
fig.tight_layout()
figure(fig, "fig26_1_1")
