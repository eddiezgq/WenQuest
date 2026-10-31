"""15.8 节的示意图。

图 15.8.1：（a）三种调度下，每一单等了多久的分布（横轴是等待时间，注意尾巴）；
（b）奖励里"已等时间"的权重一调，平均等待与尾部等待怎样此消彼长——学出来的就是这个权重。
"""
import numpy as np

from _ch15 import AGVShop, nearest_policy, oldest_policy, weighted_policy
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

N_AGV, RATE, HOURS = 3, 1 / 24, 3.0
shop = AGVShop(n_agv=N_AGV, rate=RATE, horizon=HOURS * 3600, seed=1)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0))


def waits(pol):
    """跑一遍，把每一单的等待时间取出来（run 只返回统计量，这里重跑一次取分布）。"""
    out, orders = [], shop._orders()
    free_at = np.zeros(N_AGV)
    where = np.zeros(N_AGV, dtype=int)
    from _ch15 import LOAD_S, SPEED, dist
    pending, i, t = [], 0, 0.0
    while i < len(orders) or pending:
        k = int(np.argmin(free_at))
        t = max(free_at[k], t)
        while i < len(orders) and orders[i]["t"] <= t:
            pending.append(orders[i])
            i += 1
        if not pending:
            if i < len(orders):
                t = orders[i]["t"]
                continue
            break
        j = pol(where[k], pending, t)
        o = pending.pop(j)
        go = dist(where[k], o["from"]) / SPEED
        out.append(t - o["t"] + go)
        free_at[k] = t + go + LOAD_S + dist(o["from"], o["to"]) / SPEED + LOAD_S
        where[k] = o["to"]
    return np.array(out)


for name, pol, col in ((T("最近任务优先", "nearest first"), nearest_policy, C["z"]),
                       (T("最久等待优先", "oldest first"), oldest_policy, C["x"]),
                       (T("学出来的权重", "learned weights"), weighted_policy(1.0, 0.05), C["y"])):
    w = np.sort(waits(pol))
    a.plot(w, 1 - np.arange(len(w)) / len(w), color=col, lw=1.8, label=name)
a.set_yscale("log")
a.set_xlabel(T("这一单等了多久（秒）", "waiting time of an order (s)"))
a.set_ylabel(T("等得比它久的比例", "share of orders waiting longer"))
a.set_title(T("(a) 平均数看不出的那条尾巴", "(a) The tail the average hides"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5, which="both")

ws = [0.0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8]
mean, p95, mx = [], [], []
for w_wait in ws:
    r = shop.run(weighted_policy(1.0, w_wait))
    mean.append(r["wait_mean"])
    p95.append(r["wait_p95"])
    mx.append(r["wait_max"])
b.plot(ws, mean, "o-", color=C["z"], lw=1.8, label=T("平均等待", "mean wait"))
b.plot(ws, p95, "s-", color=C["y"], lw=1.8, label=T("95 分位", "95th percentile"))
b.plot(ws, mx, "^-", color=C["x"], lw=1.8, label=T("最久的那一单", "worst case"))
b.axvline(0.05, color=C["muted"], ls="--", lw=1.0)
b.text(0.055, max(mx) * 0.8, T("选出来的权重", "the weight we picked"), fontsize=8, color=C["muted"])
b.set_xlabel(T("奖励里“已等时间”的权重", "weight on waiting time in the reward"))
b.set_ylabel(T("等待时间（秒）", "waiting time (s)"))
b.set_title(T("(b) 这头好一点，那头就差一点", "(b) Gain on one end, lose on the other"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig15_8_1")
