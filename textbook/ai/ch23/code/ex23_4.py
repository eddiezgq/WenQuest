"""算例 23.4.1：规划权重的取舍——调快一点点就不安全了（23.4 节）。

规划器的代价函数里有三项：跟车距离、车速跟随、舒适。本算例只扫**跟车距离那一项的权重**，
把三个指标并排报出来：平均车距、通行效率、急刹次数，再加一列**最小安全间距被侵犯的次数**。

要讲的两件事：
（1）**这三个指标不可能同时最好。** 权重往“跟紧”调，通行效率上去了，侵犯次数也上来了；
    往“跟远”调，侵犯次数清零了，但急刹反而回升（离太远 → 前车一刹就要大幅修正）。
（2）**存在一个窄的安全区间**，而它不在任何一个单指标的最优点上。只报一个指标的
    调参结论，一定是错的。

通行效率用交通流的标准口径：流量 q = 3600·v /（车距 + 车长），单位 辆/小时。
它正是“跟得紧就通得多”这件事的量化——也正是跟车距离权重真正在交易的东西。
"""
import numpy as np

from _ch23 import SCENE, cost_planner, follow_sim
from bookout import out

N = 2400                   # 120 s
SEED = 5
DELAY = 2                  # 感知到执行的时延：2 拍 = 100 ms
v = {"n_steps": N, "seed": SEED, "delay_steps": DELAY,
     "t_safe": SCENE["t_safe"], "d_safe0": SCENE["d_safe0"],
     "a_hard": SCENE["a_hard"], "v_set": SCENE["v_set"]}
print(f"跟车场景 {N * 0.05:.0f} s，时延 {DELAY} 拍（{DELAY * 50} ms）")
print(f"最小安全间距 = {SCENE['d_safe0']:.1f} m + {SCENE['t_safe']:.1f} s × 车速；"
      f"减速度低于 {SCENE['a_hard']:.1f} m/s² 记一次急刹")


def flow_vph(r: dict) -> float:
    """交通流量（辆/小时）：跟得越紧，同一条车道一小时过的车越多。"""
    return 3600.0 * r["v_mean"] / (r["gap_mean"] + SCENE["veh_len"])


WS = np.array([0.02, 0.035, 0.05, 0.07, 0.10, 0.14, 0.20, 0.28, 0.40,
               0.57, 0.80, 1.13, 1.60, 2.26, 3.20])
rows = []
print("\n权重 w_gap   平均车距(m)  最小车距(m)  流量(辆/h)  急刹次数  侵犯次数")
for w in WS:
    r = follow_sim(cost_planner(float(w)), n=N, seed=SEED, delay_steps=DELAY)
    rows.append({"w": float(w), "gap": r["gap_mean"], "gap_min": r["gap_min"],
                 "flow": flow_vph(r), "hard": r["hard"], "viol": r["viol"],
                 "jerk": r["jerk_rms"], "crash": r["crash"]})
    print(f"{w:10.3f}{r['gap_mean']:13.2f}{r['gap_min']:13.2f}"
          f"{flow_vph(r):12.0f}{r['hard']:10d}{r['viol']:10d}")

assert all(x["crash"] == 0 for x in rows), "任何权重都不许真撞上，否则这组扫描没有意义"

for k in ("w", "gap", "flow", "hard", "viol"):
    v[f"sweep_{k}"] = [x[k] for x in rows]

# ---------- 一、安全区间在哪里
safe = [x for x in rows if x["viol"] == 0]
unsafe = [x for x in rows if x["viol"] > 0]
assert safe and unsafe, "这组权重必须既扫到安全的也扫到不安全的，否则区间无从谈起"
v["w_safe_lo"], v["w_safe_hi"] = min(x["w"] for x in safe), max(x["w"] for x in safe)
v["n_safe"], v["n_unsafe"] = len(safe), len(unsafe)
print(f"\n侵犯次数为 0 的权重：{v['w_safe_lo']:.2f}—{v['w_safe_hi']:.2f}"
      f"（扫的 {len(rows)} 档里有 {v['n_safe']} 档）")

# 再加一条：既不侵犯、也不急刹
clean = [x for x in safe if x["hard"] == 0]
assert clean, "应当存在既不侵犯最小间距、也不急刹的权重"
v["w_clean_lo"], v["w_clean_hi"] = min(x["w"] for x in clean), max(x["w"] for x in clean)
v["n_clean"] = len(clean)
v["clean_span_ratio"] = v["w_clean_hi"] / v["w_clean_lo"]
print(f"既不侵犯、也不急刹的权重：{v['w_clean_lo']:.2f}—{v['w_clean_hi']:.2f}"
      f"（{v['n_clean']} 档，宽度只有 {v['clean_span_ratio']:.1f} 倍）")
print(f"**可用区间两头都是悬崖**：往小调就侵犯最小间距，往大调急刹回升——"
      f"而权重可以连续调，这个区间却只有 {v['clean_span_ratio']:.1f} 倍宽")

# ---------- 二、“调快一点就不安全了”，差多少
best_safe = max(safe, key=lambda x: x["flow"])
best_any = max(rows, key=lambda x: x["flow"])
v["flow_best_safe"] = best_safe["flow"]
v["w_best_safe"] = best_safe["w"]
v["flow_best_any"] = best_any["flow"]
v["w_best_any"] = best_any["w"]
v["viol_best_any"] = best_any["viol"]
v["flow_gain_pct"] = (v["flow_best_any"] / v["flow_best_safe"] - 1) * 100
assert v["viol_best_any"] > 0, \
    "流量最高的那一档必须是侵犯了最小间距的那一档——这就是“调快一点就不安全了”"
assert v["flow_best_any"] > v["flow_best_safe"], "不安全那一档的流量确实更高"
print(f"\n流量最高的一档是 w={v['w_best_any']:.3f}：{v['flow_best_any']:.0f} 辆/h，"
      f"但它侵犯最小间距 {v['viol_best_any']} 次")
print(f"安全区间内流量最高的一档是 w={v['w_best_safe']:.2f}：{v['flow_best_safe']:.0f} 辆/h")
print(f"**那 {v['flow_gain_pct']:.1f}% 的流量，是用 {v['viol_best_any']} 次"
      f"侵犯最小安全间距换来的**——报表上只写流量，这笔交易就看不见了")

# 把侵犯次数折成时间：一次侵犯就是一个控制周期
v["viol_seconds_best_any"] = v["viol_best_any"] * 0.05
v["viol_pct_best_any"] = v["viol_best_any"] / N * 100
print(f"折成时间：{v['viol_seconds_best_any']:.1f} s 处于最小安全间距以内，"
      f"占全程 {v['viol_pct_best_any']:.1f}%")

# ---------- 三、三个指标各自的最优点在不同的地方
i_flow = int(np.argmax([x["flow"] for x in rows]))
i_hard = int(np.argmin([x["hard"] for x in rows]))
i_jerk = int(np.argmin([x["jerk"] for x in rows]))
v["w_opt_flow"], v["w_opt_hard"], v["w_opt_jerk"] = (rows[i_flow]["w"], rows[i_hard]["w"],
                                                     rows[i_jerk]["w"])
print(f"\n三个指标各自的最优权重：流量 {v['w_opt_flow']:.3f}、"
      f"急刹 {v['w_opt_hard']:.2f}、舒适 {v['w_opt_jerk']:.2f}")
assert v["w_opt_flow"] != v["w_opt_hard"], "流量最优与急刹最优不在同一个权重上"
print("**三个最优点不在同一处**：所以“调参调到最好”这句话，不说清是按哪个指标，就没有意义")

# ---------- 四、时延一加，安全区间会不会缩
print("\n时延(ms)  安全区间(w_gap)  既不侵犯也不急刹的区间  最高安全流量(辆/h)")
for d in (0, 2, 4, 8):
    rs = [follow_sim(cost_planner(float(w)), n=N, seed=SEED, delay_steps=d) for w in WS]
    sf = [(float(w), flow_vph(r), r["hard"]) for w, r in zip(WS, rs) if r["viol"] == 0]
    cl = [t for t in sf if t[2] == 0]
    tag = f"d{d}"
    v[f"safe_lo_{tag}"] = min(t[0] for t in sf) if sf else None
    v[f"clean_n_{tag}"] = len(cl)
    v[f"flow_best_safe_{tag}"] = max(t[1] for t in sf) if sf else None
    lo = f"{v[f'safe_lo_{tag}']:.2f}" if sf else "无"
    print(f"{d * 50:8d}  ≥{lo:<15}{len(cl)} 档{'':<18}"
          f"{v[f'flow_best_safe_{tag}'] if sf else 0:.0f}")
v["clean_shrink_0_to_8"] = v["clean_n_d0"] - v["clean_n_d8"]
print(f"时延从 0 加到 400 ms，“既不侵犯也不急刹”的权重档数从 {v['clean_n_d0']} 降到 "
      f"{v['clean_n_d8']}（少 {v['clean_shrink_0_to_8']} 档）")
assert v["clean_n_d8"] <= v["clean_n_d0"], "时延越大，可用的权重区间不该变宽"
print("这一列要照实读：在本场景这个时延范围里，**可用区间只窄了一档，变化不大**——"
      "因为安全区间里车距本来就留得宽（20 m 以上），几百毫秒的时延还吃得下。"
      "时延真正咬人的地方是跟得紧的时候，那要到算例 23.7 才算得清。")

print("\n这个算例回答不了什么：本算例只有一辆前车、一条直道、一个权重，"
      "真规划器有十几个权重且互相耦合，调参要在成千条场景上做；"
      "“最小安全间距”这里取的是固定时距公式，真正的安全间距要按路面、能见度、"
      "制动能力来定，而且**这个公式本身就是一条假设**，不是物理定律。")

# ---------- 正文那张表要印的六档（第 174 轮：正文里不许有手打的数）
for _w in (0.02, 0.10, 0.20, 0.57, 0.80, 3.20):
    _r = min(rows, key=lambda x: abs(x["w"] - _w))
    _tag = f"r{str(_w).replace('.', 'p')}"
    v[f"{_tag}_gap"] = _r["gap"]
    v[f"{_tag}_flow"] = _r["flow"]
    v[f"{_tag}_hard"] = _r["hard"]
    v[f"{_tag}_viol"] = _r["viol"]

out(**v)
