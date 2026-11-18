"""算例 22.3.1—22.3.3：划分口径第五次露面——时间序列（22.1 节）。

时间序列的泄漏有**两种**，机理不同，要分开防：

（1）**特征里藏着答案**（因果性）：滑动平均取了"居中窗口"，窗口里包含当前点甚至未来点。
    这种特征上线时根本拿不到，而且**换哪种划分都看不出来**——两边分数一起变好看；
（2）**划分把相邻样本分到两边**（独立性）：相邻两个点几乎一样，随机划分时测试集里每一条
    在训练集里都有近亲。**这一种要靠按时间划分才看得出来**，而且模型越能记，差得越多。

这是 18.5、19.5、20.4、21.3 之后的第五次，也是最容易被"我按时间划分了"这句话糊弄过去的一次。
"""
import numpy as np

from _ch22 import (STEPS_PER_DAY, cloud_factor, design_matrix, fit_ls, pv_series,
                   split_random, split_time)
from bookout import out

N_DAYS = 60
WIN = 8                       # 滑动窗口：8 个点 = 2 小时
v = {"n_days": N_DAYS, "window": WIN}

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
g = np.random.default_rng(5)
X0 = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))
n = len(pv)
day = pv > 1.0


def causal_roll(x, k):
    """只用**过去**的点：先整体后移一位，再取滑动平均。"""
    past = np.concatenate([np.zeros(1), x[:-1]])
    return np.convolve(past, np.ones(k) / k, mode="full")[:len(x)]


X_causal = np.column_stack([X0, causal_roll(pv, WIN), causal_roll(pv, WIN * 3)])
X_center = np.column_stack([X0,
                            np.convolve(pv, np.ones(WIN) / WIN, mode="same"),
                            np.convolve(pv, np.ones(WIN * 3) / (WIN * 3), mode="same")])


def rmse_ls(X, tr, te):
    w = fit_ls(X[tr], pv[tr])
    p = np.maximum(X[te] @ w, 0.0)
    m = day[te]
    return float(np.sqrt(np.mean((p[m] - pv[te][m]) ** 2)))


# ---------- 一、第一种泄漏：特征里藏着答案
tr_t, te_t = split_time(n, 0.25, gap=0)
rs = [rmse_ls(X_causal, *split_random(n, 0.25, seed=s)) for s in range(5)]
v["causal_random"] = float(np.median(rs))
v["causal_time"] = rmse_ls(X_causal, tr_t, te_t)
rs = [rmse_ls(X_center, *split_random(n, 0.25, seed=s)) for s in range(5)]
v["center_random"] = float(np.median(rs))
v["center_time"] = rmse_ls(X_center, tr_t, te_t)
print("滑动特征只用过去（因果）：随机划分 "
      f"{v['causal_random']:.2f} kW，按时间划分 {v['causal_time']:.2f} kW")
print("滑动特征取居中窗口（含当前点）：随机划分 "
      f"{v['center_random']:.2f} kW，按时间划分 {v['center_time']:.2f} kW")
v["center_gain"] = v["causal_time"] / v["center_time"]
assert v["center_time"] < v["causal_time"], "居中窗口把答案带进了特征，分数一定更好看"
print(f"**居中窗口让分数好看了 {v['center_gain']:.1f} 倍，而且两种划分一起变好看**——"
      f"所以这一种泄漏，换划分口径是查不出来的")
print("查它只有一条标准：**做预测的那一刻，这个特征到底有没有**")

# ---------- 二、第二种泄漏：随机划分把近亲分到两边
# 用一个"能记"的模型（最近邻）把这件事放大：它只会找最像的那条训练样本照抄
def rmse_nn(X, tr, te):
    Xt = X[tr]
    mu, sd = Xt.mean(0), Xt.std(0) + 1e-9
    A = (Xt - mu) / sd
    B = (X[te] - mu) / sd
    pred = np.empty(len(te))
    for i in range(len(te)):
        j = int(np.argmin(((A - B[i]) ** 2).sum(axis=1)))
        pred[i] = pv[tr][j]
    m = day[te]
    return float(np.sqrt(np.mean((pred[m] - pv[te][m]) ** 2)))


rs = [rmse_nn(X_causal, *split_random(n, 0.25, seed=s)) for s in range(3)]
v["nn_random"] = float(np.median(rs))
v["nn_time"] = rmse_nn(X_causal, tr_t, te_t)
v["nn_ratio"] = v["nn_time"] / v["nn_random"]
print(f"\n最近邻模型（只会照抄最像的那条）：随机划分 {v['nn_random']:.2f} kW，"
      f"按时间划分 {v['nn_time']:.2f} kW，差 {v['nn_ratio']:.1f} 倍")
assert v["nn_time"] > v["nn_random"], "随机划分时，测试集里每一条都有近亲在训练集里"


# 泄漏本身有没有发生，看的不是误差，而是“最像的那条离测试点多远”
def twin_share(X, tr, te, within_h=0.5):
    Xt = X[tr]
    mu, sd = Xt.mean(0), Xt.std(0) + 1e-9
    A, B = (Xt - mu) / sd, (X[te] - mu) / sd
    close = tot = 0
    for k, bvec in enumerate(B):
        if not day[te][k]:
            continue
        j = int(np.argmin(((A - bvec) ** 2).sum(axis=1)))
        tot += 1
        close += abs(int(tr[j]) - int(te[k])) / STEPS_PER_DAY * 24.0 <= within_h
    return close / tot * 100


v["twin_random"] = twin_share(X_causal, *split_random(n, 0.25, seed=0))
v["twin_time"] = twin_share(X_causal, tr_t, te_t)
print(f"随机划分：{v['twin_random']:.0f}% 的白天测试点，最像的那条训练样本就在半小时之内；"
      f"按时间划分：{v['twin_time']:.0f}%")
assert v["twin_random"] > v["twin_time"], "随机划分确实把隔壁的样本摆到了训练集里"
print(f"**泄漏确实发生了，可误差只差 {v['nn_ratio']:.1f} 倍**——因为日变化天天重复，"
      "昨天的同一时刻本来就是个像样的替身，照抄隔壁并没有多赚多少")
print("所以这一条要分开说：**泄漏有没有发生**，看近亲的距离；**泄漏坑不坑人**，"
      "看这条序列有没有天天重复的形状。慢漂移、工况切换那类序列没有替身，同样的泄漏会要命")

# ---------- 三、留间隔
for gap, tag in ((0, "0"), (WIN, "w"), (WIN * 3, "w3"), (STEPS_PER_DAY, "day")):
    tr_g, te_g = split_time(n, 0.25, gap=gap)
    v[f"gap_{tag}"] = rmse_nn(X_causal, tr_g, te_g)
    print(f"按时间划分、训练段与测试段之间留 {gap:>3d} 个点：{v[f'gap_{tag}']:.2f} kW")
v["gap_effect"] = v["gap_day"] / v["gap_0"]
print(f"留一天的间隔，误差变成不留的 {v['gap_effect']:.2f} 倍")
print("本例看不出差别，因为特征窗口只有 2 小时、模型又记不住。"
      "**窗口越长、模型越能记，差别越大**；而留间隔的成本只是少用几十个样本，"
      "不留的风险是紧挨分界的样本在两边都出现过。所以规矩是：**间隔至少等于特征窗口的长度**")

out(**v)
