"""13.4 节的示意图（数值同程序 13.4.1）。

图 13.4.1：（a）在对数坐标上，损失随规模是一条直线（幂律）：七个点拟出的指数与真值相差很小；
只用最小的三个点外推到一万倍，误差就明显放大——规模定律的用处在外推，风险也在外推。
（b）给定算力时参数与数据怎样分配：Kaplan 的联合式偏向把算力花在参数上，
而 Chinchilla 按它自己的配置折算约为每个参数 20 个词元；GPT-3 的实际配置不到 2 个。
"""
import numpy as np

from bookout import COLORS, T, figure, style
from llm_facts import CHINCHILLA, GOPHER, GPT3_PARAMS, GPT3_TOKENS, KAPLAN

plt = style()
C = COLORS
A_N, N_C = KAPLAN["alpha_N"], KAPLAN["N_c"]
rng = np.random.default_rng(134)
NS = np.array([1e6, 3e6, 1e7, 3e7, 1e8, 3e8, 1e9])
LS = (N_C / NS) ** A_N * (1 + rng.normal(0, 0.01, len(NS)))

fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.2))
grid = np.logspace(6, 11, 100)
a.loglog(grid, (N_C / grid) ** A_N, color=C["muted"], lw=1.2, ls="--",
         label=T("真实幂律", "true power law"))
a.loglog(NS, LS, "o", ms=6, color=C["z"], label=T("七个“训练过的模型”", "seven trained models"))
p_all = np.polyfit(np.log(NS), np.log(LS), 1)
a.loglog(grid, np.exp(np.polyval(p_all, np.log(grid))), color=C["z"], lw=1.6,
         label=T("用全部点拟合", "fit on all points"))
small = NS <= 1e7
p_small = np.polyfit(np.log(NS[small]), np.log(LS[small]), 1)
a.loglog(grid, np.exp(np.polyval(p_small, np.log(grid))), color=C["x"], lw=1.6,
         label=T("只用最小的三个点", "fit on the three smallest"))
a.axvspan(1e7, 1e11, color=C["x"], alpha=0.06)
a.set_xlabel(T("非嵌入参数个数", "non-embedding parameters"))
a.set_ylabel(T("损失", "loss"))
a.set_title(T("(a) 幂律的拟合与外推", "(a) Fitting and extrapolating the power law"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5, which="both")


def joint(n, d):
    return ((N_C / n) ** (A_N / KAPLAN["alpha_D"]) + KAPLAN["D_c"] / d) ** KAPLAN["alpha_D"]


Cs = np.logspace(19, 26, 40)
ratios = []
for Cv in Cs:
    ns = np.logspace(7, 13, 400)
    ds = Cv / (6 * ns)
    i = int(np.argmin(joint(ns, ds)))
    ratios.append(ds[i] / ns[i])
b.semilogx(Cs, ratios, color=C["z"], lw=1.8, label=T("Kaplan 联合式的最优分配", "Kaplan joint law"))
b.axhline(CHINCHILLA["tokens"] / CHINCHILLA["params"], color=C["y"], lw=1.6, ls="--",
          label=T("Chinchilla 的配置（约 1∶20）", "Chinchilla's configuration (≈1:20)"))
b.plot([6 * GPT3_PARAMS[-1] * GPT3_TOKENS], [GPT3_TOKENS / GPT3_PARAMS[-1]], "o", ms=8, color=C["x"])
b.annotate(T("GPT-3", "GPT-3"), (6 * GPT3_PARAMS[-1] * GPT3_TOKENS, GPT3_TOKENS / GPT3_PARAMS[-1]),
           textcoords="offset points", xytext=(8, 6), fontsize=9, color=C["x"])
b.plot([6 * GOPHER["params"] * GOPHER["tokens"]], [GOPHER["tokens"] / GOPHER["params"]], "s", ms=7, color=C["accent"])
b.annotate(T("Gopher", "Gopher"), (6 * GOPHER["params"] * GOPHER["tokens"], GOPHER["tokens"] / GOPHER["params"]),
           textcoords="offset points", xytext=(8, -12), fontsize=9, color=C["accent"])
b.set_xlabel(T("训练算力（FLOP，按 6ND 折算）", "training compute (FLOP, as 6ND)"))
b.set_ylabel(T("每个参数配几个词元", "tokens per parameter"))
b.set_yscale("log")
b.set_title(T("(b) 算力怎样分配", "(b) How to split the compute"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5, which="both")
fig.tight_layout()
figure(fig, "fig13_4_1")
