"""算例 24.1：行为克隆对“带纠正的”（DAgger 玩具版）。

三件事：

（1）**纯克隆只在专家走过的那条管子里有数据**。一旦被摩擦、噪声、延迟推出那条管子，
    它看到的就是训练时没见过的状态，动作开始胡来，机器人越偏越远；
（2）**带纠正的做法是在学生自己走出的状态上再要专家标注**。同样的专家标注预算
    （本算例两边都是 120 回合），成功率差一个数量级；
（3）**误差随步数怎么累积，要把曲线画出来看**。这一条本算例算出来的结果与
    “全程超线性增长”的说法不符——见文件末尾那段，数照实报。

两边的“演示条数”口径一样：纯克隆用 120 条专家演示；带纠正的用 30 条专家演示
+ 3 轮 × 30 回合“学生自己走、专家来标”。专家标注的回合数都是 120。
"""
import numpy as np

from _ch24 import (DEGREE, SIM, collect, deviation_curve, evaluate, expert, fit_ls,
                   make_policy, poly_features, sample_starts, sample_targets)
from bookout import out

N_EPISODES = 120                  # 两种做法的专家标注预算（回合数），**完全相同**
ROUNDS = 4                        # 带纠正的分 4 轮：第 1 轮演示，后 3 轮纠正
SPREAD_DEMO = 0.05                # 演示的起始位姿：集中在收工位姿附近（人示教就是这样）
SPREAD_TEST = 0.30                # 验收的起始位姿：散得开（现场本来就不会每次一样）
N_TEST = 80
STEPS_CURVE = 60

v = {"n_episodes": N_EPISODES, "rounds": ROUNDS, "degree": DEGREE,
     "spread_demo": SPREAD_DEMO, "spread_test": SPREAD_TEST}

test_poses = sample_targets(N_TEST, seed=11)
test_starts = sample_starts(N_TEST, seed=11, spread=SPREAD_TEST)

# ---------- 一、纯克隆：120 条专家演示，只在专家轨迹附近有数据
demo_poses = sample_targets(N_EPISODES, seed=2)
demo_starts = sample_starts(N_EPISODES, seed=2, spread=SPREAD_DEMO)
O_bc, A_bc = collect(lambda p, w: expert(p, w), demo_poses, demo_starts, SIM, seed=0)
W_bc = fit_ls(poly_features(O_bc, DEGREE), A_bc)
v["n_samples_bc"] = len(O_bc)

res_bc = evaluate(lambda p, w: make_policy(W_bc, DEGREE), test_poses, test_starts, SIM, seed=7)
v["succ_bc"], v["n_trials"] = res_bc["success_pct"], res_bc["n_trials"]
v["pos_err_bc"], v["rot_err_bc"] = res_bc["pos_err"], res_bc["rot_err"]
print(f"纯克隆（{N_EPISODES} 条专家演示）：成功率 {v['succ_bc']:.1f}%"
      f"（试了 {v['n_trials']} 次），平均位置误差 {v['pos_err_bc'] * 100:.2f} cm")

# ---------- 二、带纠正的：同样 120 回合的专家标注，但后三轮标在学生自己走出的状态上
per = N_EPISODES // ROUNDS
Os, As = [], []
O0, A0 = collect(lambda p, w: expert(p, w), demo_poses[:per], demo_starts[:per], SIM, seed=0)
Os.append(O0)
As.append(A0)
W_dg = fit_ls(poly_features(O0, DEGREE), A0)
curve_rounds = []
for rnd in range(ROUNDS - 1):
    pp = sample_targets(per, seed=30 + rnd)
    ss = sample_starts(per, seed=30 + rnd, spread=SPREAD_TEST)
    cur = W_dg.copy()
    O2, A2 = collect(lambda p, w, Wc=cur: make_policy(Wc, DEGREE), pp, ss, SIM, seed=rnd)
    Os.append(O2)
    As.append(A2)
    W_dg = fit_ls(poly_features(np.vstack(Os), DEGREE), np.vstack(As))
    s = evaluate(lambda p, w: make_policy(W_dg, DEGREE), test_poses, test_starts, SIM,
                 seed=7)["success_pct"]
    curve_rounds.append(s)
    print(f"  第 {rnd + 2} 轮纠正后：成功率 {s:.1f}%")
v["succ_rounds"] = curve_rounds
v["n_samples_dagger"] = int(sum(len(o) for o in Os))

res_dg = evaluate(lambda p, w: make_policy(W_dg, DEGREE), test_poses, test_starts, SIM, seed=7)
v["succ_dagger"] = res_dg["success_pct"]
v["pos_err_dagger"], v["rot_err_dagger"] = res_dg["pos_err"], res_dg["rot_err"]
print(f"带纠正的（{per} 条演示 + {ROUNDS - 1} × {per} 回合纠正）：成功率 "
      f"{v['succ_dagger']:.1f}%（试了 {v['n_trials']} 次），"
      f"平均位置误差 {v['pos_err_dagger'] * 100:.2f} cm")
v["succ_gap"] = v["succ_dagger"] - v["succ_bc"]
v["err_ratio"] = v["pos_err_bc"] / v["pos_err_dagger"]
assert v["succ_dagger"] > v["succ_bc"] + 20.0, \
    "同样的专家标注预算，带纠正的成功率要明显更高——这是本节的主结论"
print(f"**同样 {N_EPISODES} 回合的专家标注，成功率差 {v['succ_gap']:.1f} 个百分点**"
      f"（位置误差差 {v['err_ratio']:.1f} 倍）。差别不在算法，只在**数据采在谁走出来的状态上**")

# ---------- 三、误差随步数怎么累积
dev_bc = deviation_curve(lambda p, w: make_policy(W_bc, DEGREE), test_poses[:40],
                         test_starts[:40], SIM, seed=7, steps=STEPS_CURVE)
dev_dg = deviation_curve(lambda p, w: make_policy(W_dg, DEGREE), test_poses[:40],
                         test_starts[:40], SIM, seed=7, steps=STEPS_CURVE)
v["dev_bc_step5"], v["dev_bc_step20"] = float(dev_bc[5]), float(dev_bc[20])
v["dev_bc_plateau"] = float(dev_bc[-1])
v["dev_dg_step5"], v["dev_dg_step20"] = float(dev_dg[5]), float(dev_dg[20])
v["dev_dg_plateau"] = float(dev_dg[-1])
v["dev_plateau_ratio"] = v["dev_bc_plateau"] / v["dev_dg_plateau"]
v["dev_step_a"], v["dev_step_b"] = 5, 20        # 正文表头那两步（第 175 轮补）
print(f"\n离专家轨迹的偏差（m）：第 5 步 {v['dev_bc_step5']:.4f} 对 {v['dev_dg_step5']:.4f}，"
      f"第 20 步 {v['dev_bc_step20']:.4f} 对 {v['dev_dg_step20']:.4f}，"
      f"到末尾 {v['dev_bc_plateau']:.4f} 对 {v['dev_dg_plateau']:.4f}")


def slope(curve, lo, hi):
    """这一段的对数—对数斜率：> 1 是超线性增长，≈ 1 是线性，< 1 是在饱和。"""
    t = np.arange(lo, hi + 1)
    return float(np.polyfit(np.log(t), np.log(np.asarray(curve)[lo:hi + 1]), 1)[0])


v["slope_early_bc"] = slope(dev_bc, 1, 6)
v["slope_late_bc"] = slope(dev_bc, 10, 40)
v["slope_early_dg"] = slope(dev_dg, 1, 6)
v["slope_late_dg"] = slope(dev_dg, 10, 40)
v["slope_early_to"] = 6                          # 两段斜率各量哪几步（第 175 轮补）
v["slope_late_from"], v["slope_late_to"] = 10, 40
print(f"对数—对数斜率：纯克隆前 6 步 {v['slope_early_bc']:.2f}、第 10—40 步 "
      f"{v['slope_late_bc']:.2f}；带纠正的 {v['slope_early_dg']:.2f} / {v['slope_late_dg']:.2f}")

# **这一条要照实报，而且它推翻了一个流传很广的说法。**
# 常说“纯克隆的误差随步数超线性累积”。本算例的输出**不支持**这个说法：
# 两条偏差曲线从头到尾都是**次线性**的（前 6 步的对数—对数斜率都小于 1），
# 十几步之后干脆饱和在一个平台上（斜率接近 0 甚至为负）。
# 原因是物理的，不是统计的：工作空间有界、关节有限位、策略带反馈，
# 跟踪误差不可能一路涨上去。**所以正文不要写“误差超线性累积”，要写下面这句。**
v["superlinear_claim_holds"] = bool(v["slope_early_bc"] > 1.0)
assert not v["superlinear_claim_holds"], \
    "本玩具里偏差不是超线性增长的——这条断言就是用来钉住“结论被推翻”这件事的"
assert v["slope_late_bc"] < 0.3, "十几步之后曲线在饱和，不在增长"
assert v["dev_bc_plateau"] > 1.3 * v["dev_dg_plateau"] and v["dev_bc_plateau"] > 0.02, \
    "纯克隆饱和在比 2 cm 判据更远的地方，这才是它抓不着的原因"
print(f"**这一条照实报**：偏差**不是**超线性累积的（前 6 步斜率 "
      f"{v['slope_early_bc']:.2f} < 1，之后 {v['slope_late_bc']:.2f} ≈ 0 已经饱和）——"
      f"工作空间有界、关节有限位，带反馈的策略偏不到天上去。"
      f"要紧的不是涨得多快，而是**它饱和在哪里**：纯克隆停在 "
      f"{v['dev_bc_plateau'] * 100:.1f} cm，是 2 cm 判据的 {v['dev_bc_plateau'] / 0.02:.1f} 倍，"
      f"所以几乎每次都抓空；带纠正的停在 {v['dev_dg_plateau'] * 100:.1f} cm，刚好在判据里面。"
      f"**判据是硬的，差一点就是 0 分**——这比“误差涨得多快”更值得记住")

# ---------- 四、把“演示条数”这一列写进报表
v["labels_bc"] = N_EPISODES
v["labels_dagger"] = N_EPISODES
# 正文表格要用的几个设定值（第 175 轮补：原来正文里是手打的）
v["demos_dagger"] = per                 # 带纠正的那一支先采多少条演示
v["rounds_correct"] = ROUNDS - 1        # 之后做几轮纠正
v["one_trial_pct"] = 100.0 / N_TEST     # 验收 N_TEST 次时，成败一次值几个百分点
print(f"\n报表要这么写（本章口径 a）：")
print(f"  纯克隆　　：演示 {v['labels_bc']} 条（专家采，起始位姿集中），"
      f"样本 {v['n_samples_bc']} 步，成功率 {v['succ_bc']:.1f}%（{v['n_trials']} 次）")
print(f"  带纠正的　：专家标注 {v['labels_dagger']} 回合（{per} 条演示 + "
      f"{ROUNDS - 1} 轮纠正），样本 {v['n_samples_dagger']} 步，"
      f"成功率 {v['succ_dagger']:.1f}%（{v['n_trials']} 次）")
print("**只报成功率不报演示条数与采集方式的模仿学习结果，没法复现，也没法比**")

out(**v)
