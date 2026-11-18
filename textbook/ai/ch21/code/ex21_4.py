"""算例 21.4.1—21.4.2：划分口径第四次露面（21.3 节）。

现场的振动数据是成片的：同一台机床的几次采集共用一个共振频率与一档底噪，
而故障是**慢慢长出来的**——今天的信号与昨天的几乎一样。于是：

* **按采集随机划分**：同一台机床相邻两次采集分到训练与测试两边，分数好得不像话；
* **按机床划分**：回答"换一台没见过的机床还准不准"；
* **按时间划分**：拿过去训、拿未来测——**这才是现场真正的问法**，也是最难的一种。

这是 18.5 节骨架划分、19.5 节区块划分、20.4 节按成分划分之后的第四次。
"""
import numpy as np

from _ch21 import features, logistic_acc, logistic_fit, make_runs, split_runs, standardize
from bookout import out

N_MACH, PER_MACH, SECONDS = 8, 8, 0.5
SEEDS = range(8)
runs = make_runs(N_MACH, PER_MACH, seconds=SECONDS, seed=0)
v = {"n_machines": N_MACH, "per_machine": PER_MACH, "n_runs": len(runs),
     "seconds": SECONDS,
     "fault_share_pct": float(np.mean([r["fault"] for r in runs])) * 100,
     "n_never_fault": len({r["machine"] for r in runs if r["onset"] >= PER_MACH})}
print(f"{v['n_machines']} 台机床 × 每台 {v['per_machine']} 次采集 = {v['n_runs']} 条信号，"
      f"其中 {v['fault_share_pct']:.1f}% 有故障；"
      f"{v['n_never_fault']} 台一直没坏")


def score(how: str) -> dict:
    accs = []
    for sd in SEEDS:
        tr, te = split_runs(runs, how, seed=sd)
        if not te or len({r["fault"] for r in tr}) < 2 or len({r["fault"] for r in te}) < 2:
            continue
        Xtr = np.array([features(r) for r in tr])
        Xte = np.array([features(r) for r in te])
        ytr = np.array([r["fault"] for r in tr], dtype=float)
        yte = np.array([r["fault"] for r in te], dtype=float)
        Xtr, Xte = standardize(Xtr, Xte)          # 用训练集的均值方差去标准化测试集
        accs.append(logistic_acc(logistic_fit(Xtr, ytr), Xte, yte))
    return {"median": float(np.median(accs)), "lo": float(np.min(accs)),
            "hi": float(np.max(accs)), "n": len(accs)}
    # 注：按时间划分不含随机性（训练段永远是前面那一截），所以它的 8 折是同一个数


# ---------- 一、三种划分
for how, tag in (("random", "random"), ("machine", "machine"), ("time", "time")):
    r = score(how)
    v[f"acc_{tag}"] = r["median"] * 100
    v[f"acc_{tag}_lo"] = r["lo"] * 100
    v[f"acc_{tag}_hi"] = r["hi"] * 100
    v[f"folds_{tag}"] = r["n"]
    print(f"{how:>8} 划分：准确率中位 {r['median'] * 100:.1f}%"
          f"（{r['n']} 折，{r['lo'] * 100:.1f}—{r['hi'] * 100:.1f}%）")

v["gap_random_time"] = v["acc_random"] - v["acc_time"]
v["gap_random_machine"] = v["acc_random"] - v["acc_machine"]
assert v["acc_random"] >= v["acc_machine"] >= v["acc_time"], \
    "随机划分应当最乐观，按时间划分最接近现场"
print(f"\n随机划分比按时间划分高 {v['gap_random_time']:.1f} 个百分点，"
      f"比按机床划分高 {v['gap_random_machine']:.1f} 个百分点")
print("**同一个模型、同一批数据，换个划分口径，验收结论就不一样**")
print("这批数据还告诉我们一件更具体的事：**要害不在机床，在时间**——"
      "换一台没见过的机床，这几个特征还认得出故障；而拿过去去预测未来，"
      "分数立刻掉下来，因为未来的故障更重、也更多。"
      "所以“按什么划分最危险”不是一句通则，要在自己的数据上试出来")

# ---------- 二、同一台机床的采集有多像（标准化之后按距离看，不按余弦）
X = np.array([features(r) for r in runs])
Xs = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)
within, across = [], []
for i in range(len(runs)):
    for j in range(i + 1, len(runs)):
        d = float(np.linalg.norm(Xs[i] - Xs[j]))
        same_state = runs[i]["fault"] == runs[j]["fault"]
        if not same_state:
            continue                      # 只比同一种状态，免得把"好件对坏件"的差算进来
        (within if runs[i]["machine"] == runs[j]["machine"] else across).append(d)
v["dist_within"] = float(np.mean(within))
v["dist_across"] = float(np.mean(across))
v["dist_ratio"] = v["dist_across"] / v["dist_within"]
print(f"\n同一种状态下，同一台机床两次采集的特征距离 {v['dist_within']:.3f}，"
      f"不同机床之间 {v['dist_across']:.3f}，后者是前者的 {v['dist_ratio']:.2f} 倍")
assert v["dist_within"] < v["dist_across"], "同一台机床的采集本来就更像"
print("**这就是随机划分虚高的来源**：测试集里的每一条，训练集里都有一条同机床的近亲")

# ---------- 三、按时间划分为什么更难：训练与测试的类别比例本来就不同
tr, te = split_runs(runs, "time", seed=0)
v["train_fault_pct"] = float(np.mean([r["fault"] for r in tr])) * 100
v["test_fault_pct"] = float(np.mean([r["fault"] for r in te])) * 100
print(f"\n按时间划分：训练段里 {v['train_fault_pct']:.1f}% 有故障，"
      f"测试段里 {v['test_fault_pct']:.1f}%")
print("**差别不只是“难一点”**：故障是长出来的，所以未来那一段的故障更重、也更多；"
      "这正是现场要回答的问题，也是随机划分永远答不了的问题")
v["shift_pts"] = v["test_fault_pct"] - v["train_fault_pct"]
assert v["shift_pts"] > 0, "后面的时间段里故障应当更多"

print("\n**本章的默认口径定为按时间划分**：训练用过去、测试用未来；"
      "要回答“换一台机床还准不准”，再单独按机床划分跑一遍。"
      "两个数都要印，而且要写明哪个是哪个")

out(**v)
