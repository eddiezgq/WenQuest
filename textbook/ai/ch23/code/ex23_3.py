"""算例 23.3.2：轨迹预测的平均误差与最坏情形（23.3 节）。

一件事：**同一个预测模型，平均误差与最坏情形差一个量级，而规划吃的是最坏那一档。**

报告上写“平均位移误差 0.4 m”，听起来够用了；可规划要留的安全间距，是按“最坏能差多少”
留的。本算例把同一条轨迹上的平均、95 分位、99 分位、最大值四个数并排报出来，
再把它们各自折成“要留多宽的缓冲”——差出来的那几米，就是只看平均值会漏掉的东西。
"""
import numpy as np

from _ch23 import DT, fit_ls, lead_track, pred_features, predict_const_vel
from bookout import out

N = 24000                  # 20 分钟
HOR_S = 3.0                # 预测时域 3 s（规划器往前看的长度）
HOR = int(HOR_S / DT)
v = {"n_steps": N, "dt_s": DT, "minutes": N * DT / 60, "horizon_s": HOR_S}

s, v_lead = lead_track(N, DT, seed=9)
truth = s[HOR:]                            # HOR 步之后的真实位置
a_lead = np.gradient(v_lead, DT)
v["brake_frac_pct"] = float(np.mean(a_lead < -1.5)) * 100
print(f"{v['minutes']:.0f} 分钟的前车轨迹，预测时域 {HOR_S:.0f} s（{HOR} 拍）")
print(f"其中减速度超过 1.5 m/s² 的时刻占 {v['brake_frac_pct']:.1f}%——"
      f"**最坏情形就藏在这一小撮里**")

# ---------- 一、两个预测模型
pred_cv = predict_const_vel(s, v_lead, HOR)[:len(truth)]

X = pred_features(s, v_lead)[:len(truth)]
y = truth - s[:len(truth)]                 # 学“这 3 s 会走多远”
cut = int(len(y) * 0.6)
w = fit_ls(X[:cut], y[:cut])
pred_lin = s[:len(truth)] + X @ w
v["n_train"], v["n_test"] = cut, len(y) - cut

te = np.arange(cut, len(y))
models = {"cv": pred_cv[te], "lin": pred_lin[te]}
tr_truth = truth[te]

print("\n模型             平均(m)  中位(m)  95分位(m)  99分位(m)  最大(m)  最坏/平均")
for tag, p in models.items():
    e = np.abs(p - tr_truth)
    v[f"ade_{tag}"] = float(e.mean())
    v[f"med_{tag}"] = float(np.median(e))
    v[f"p95_{tag}"] = float(np.quantile(e, 0.95))
    v[f"p99_{tag}"] = float(np.quantile(e, 0.99))
    v[f"max_{tag}"] = float(e.max())
    v[f"ratio_{tag}"] = v[f"max_{tag}"] / v[f"ade_{tag}"]
    v[f"ratio99_{tag}"] = v[f"p99_{tag}"] / v[f"ade_{tag}"]
    name = {"cv": "常速（基线）", "lin": "可学的线性模型"}[tag]
    print(f"{name:<14}{v[f'ade_{tag}']:8.3f}{v[f'med_{tag}']:9.3f}"
          f"{v[f'p95_{tag}']:11.3f}{v[f'p99_{tag}']:11.3f}{v[f'max_{tag}']:9.3f}"
          f"{v[f'ratio_{tag}']:11.1f}")

assert v["ade_lin"] < v["ade_cv"], "可学模型要先打赢常速基线，否则不值得做"
v["lin_gain_pct"] = (1 - v["ade_lin"] / v["ade_cv"]) * 100
print(f"可学模型的平均误差比常速基线低 {v['lin_gain_pct']:.0f}%")

assert v["ratio_lin"] >= 3.0, \
    "最坏情形至少是平均的 3 倍——这是本算例要钉住的结论"
assert v["ratio_cv"] >= 3.0, "常速基线同理"
print(f"**但最坏情形是平均的 {v['ratio_lin']:.0f} 倍**"
      f"（99 分位也已经是 {v['ratio99_lin']:.1f} 倍）")

# ---------- 二、最坏的那几帧在干什么
e_lin = np.abs(models["lin"] - tr_truth)
k_worst = te[np.argsort(e_lin)[-200:]]
# 预测误差是“这 3 s 里发生了什么”造成的，所以要看**未来窗口内**的最小加速度
fut_min_a = np.array([a_lead[k:k + HOR].min() for k in range(len(truth))])
v["worst_window_decel"] = float(np.mean(fut_min_a[k_worst]))
v["all_window_decel"] = float(np.mean(fut_min_a[te]))
v["worst_brake_frac_pct"] = float(np.mean(fut_min_a[k_worst] < -1.5)) * 100
v["all_brake_frac_pct"] = float(np.mean(fut_min_a[te] < -1.5)) * 100
print(f"\n误差最大的 200 帧：未来 {HOR_S:.0f} s 内的最小加速度平均 "
      f"{v['worst_window_decel']:.2f} m/s²（全体 {v['all_window_decel']:.2f} m/s²），"
      f"其中 {v['worst_brake_frac_pct']:.0f}% 的窗口里前车刹到 1.5 m/s² 以上"
      f"（全体 {v['all_brake_frac_pct']:.0f}%）")
assert v["worst_window_decel"] < v["all_window_decel"] - 0.5, \
    "最坏的那几帧应当集中在前车刹车的那几个窗口里"
assert v["worst_brake_frac_pct"] > v["all_brake_frac_pct"], "同上"
print("**最坏情形不是随机散落的，它集中在前车刹车那几秒**——"
      "也就是规划最需要预测准的那几秒")

# ---------- 三、同样的误差，折成要留多宽的缓冲
v["buf_mean_m"] = v["ade_lin"]
v["buf_p99_m"] = v["p99_lin"]
v["buf_max_m"] = v["max_lin"]
v["buf_gap_m"] = v["buf_max_m"] - v["buf_mean_m"]
v["buf_gap_in_cars"] = v["buf_gap_m"] / 4.8
print(f"\n按平均误差留缓冲：{v['buf_mean_m']:.2f} m；按 99 分位：{v['buf_p99_m']:.2f} m；"
      f"按最大值：{v['buf_max_m']:.2f} m")
print(f"**只看平均值会少留 {v['buf_gap_m']:.2f} m = {v['buf_gap_in_cars']:.1f} 个车身**")

# 按平均误差留缓冲，实际会有多少比例的时刻不够用
for tag in ("mean", "p99"):
    budget = v[f"buf_{tag}_m"]
    v[f"exceed_pct_{tag}"] = float(np.mean(e_lin > budget)) * 100
    print(f"把缓冲定成{'平均误差' if tag == 'mean' else '99 分位'}"
          f"（{budget:.2f} m）：有 {v[f'exceed_pct_{tag}']:.1f}% 的时刻不够用")
assert v["exceed_pct_mean"] > 10 * max(v["exceed_pct_p99"], 1e-9) or \
    v["exceed_pct_mean"] > 20.0, "按平均值留缓冲，不够用的时刻比例要高得多"

# ---------- 四、把预测时域拉长，差距怎么长
print("\n预测时域(s)   平均(m)   99分位(m)   最大(m)   最坏/平均")
for hs in (1.0, 2.0, 3.0, 4.0, 5.0):
    h = int(hs / DT)
    t2 = s[h:]
    X2 = pred_features(s, v_lead)[:len(t2)]
    y2 = t2 - s[:len(t2)]
    c2 = int(len(y2) * 0.6)
    w2 = fit_ls(X2[:c2], y2[:c2])
    e2 = np.abs(s[c2:len(t2)] + X2[c2:] @ w2 - t2[c2:])
    tag = f"{hs:.0f}s"
    v[f"ade_h{tag}"] = float(e2.mean())
    v[f"p99_h{tag}"] = float(np.quantile(e2, 0.99))
    v[f"max_h{tag}"] = float(e2.max())
    v[f"ratio_h{tag}"] = v[f"max_h{tag}"] / v[f"ade_h{tag}"]
    print(f"{hs:9.0f}{v[f'ade_h{tag}']:11.3f}{v[f'p99_h{tag}']:12.3f}"
          f"{v[f'max_h{tag}']:10.3f}{v[f'ratio_h{tag}']:11.1f}")
v["ade_growth_1_to_5"] = v["ade_h5s"] / v["ade_h1s"]
v["max_growth_1_to_5"] = v["max_h5s"] / v["max_h1s"]
v["ratio_h1s_over_h5s"] = v["ratio_h1s"] / v["ratio_h5s"]
print(f"时域从 1 s 拉到 5 s：平均误差长 {v['ade_growth_1_to_5']:.1f} 倍，"
      f"最大误差只长 {v['max_growth_1_to_5']:.1f} 倍")
# **一条被自己的输出推翻的猜想**：我们原以为“时域越长，尾巴长得比平均值更快”。不是。
assert v["max_growth_1_to_5"] < v["ade_growth_1_to_5"], \
    "在这套场景里，拉长时域时平均误差长得比尾巴快——与直觉相反，照实报"
assert v["ratio_h1s"] > v["ratio_h5s"], "最坏/平均的比值在短时域上最大"
print(f"**这一条与直觉相反，照实报**：尾巴并没有长得比平均值快。原因是本场景里前车的"
      f"刹车深度有上限（最深约 8.5 m/s²、最长约 3.5 s），3 s 以后最坏情形基本见底，"
      f"而平均误差还在一路长。于是“最坏/平均”的比值是**在短时域上最大**："
      f"1 s 时域 {v['ratio_h1s']:.0f} 倍，5 s 时域只有 {v['ratio_h5s']:.0f} 倍"
      f"（差 {v['ratio_h1s_over_h5s']:.1f} 倍）。")
print("**所以“只看平均误差”在短时域上错得最厉害**——偏偏短时域正是紧急制动要用的那一档。"
      "这条结论比我们原来想的那条更要紧：不能用长时域的平均误差去给短时域的安全间距背书。")

print("\n这个算例回答不了什么：真路上的最坏情形不止前车急刹（切入、抛洒物、行人横穿），"
      "而且它们在数据里更稀少，靠 20 分钟的样本量根本估不出 99.9 分位；"
      "本算例只预测一辆前车的纵向位置，真预测要同时出多条可能轨迹及其概率，"
      "那时“误差”该怎么定义本身就是一个课题。")

out(**v)
