"""算例 12.7.1—12.7.3：车间语音指令控制 AGV（12.7 节）。

指令集只有十条（"前进""后退""左转""右转""停止""暂停""继续""去一号工位""去三号工位""回充电桩"）。
这件事比开放域识别容易——词表小、句式固定；但它多了一个开放域没有的要求：**听错比听不清危险**。
把"停止"听成"前进"会撞人，把"前进"听成"听不清"只是要再说一遍。

（1）噪声下的识别：用程序合成的指令信号在不同信噪比下加噪，用一个简单的模板匹配器（梅尔频谱的余弦相似度）
    识别，算字错率与句准确率——这不是真实识别率，而是说明"信噪比掉下来，识别就掉下来"的量级关系。
（2）拒识阈值：相似度低于阈值就拒识（回答"没听清，请再说一遍"）。给定误执行与拒识的代价，
    算出使总代价最小的阈值——与 11.8 节的做法一样，只是代价之比更悬殊。
（3）端到端延迟：说完 → 端点检测 → 识别 → 解析 → 下发，各段的时间预算；人对"说完到动作"的容忍约 1 秒。
"""
import numpy as np

from _ch12 import SR, add_noise, log_mel, utterance
from bookout import out

from _cmds import CMDS, NAMES, REPS, SNRS, best_threshold, trials

v = {"n_cmd": len(CMDS)}
# ---------- （1）噪声下的识别
rows = {}
for snr in SNRS:
    sims_all = trials(snr)
    acc = 100 * sum(ok for _, ok in sims_all) / len(sims_all)
    rows[snr] = (acc, sims_all)
    v[f"acc_{snr}".replace("-", "m")] = acc
v["acc_drop"] = rows[20][0] - rows[-10][0]
v["n_trial"] = len(NAMES) * REPS

# ---------- （2）拒识阈值
C_WRONG, C_REJECT = 100.0, 1.0                               # 误执行 100、拒识 1（再说一遍的代价）
v["c_wrong"], v["c_reject"] = C_WRONG, C_REJECT
SNR_T = -10                                                  # 取车间里最糟的那一档（信噪比 −10 dB）来定阈值
v["snr_t"] = SNR_T
fit = trials(SNR_T, "fit")                                   # 定阈值用的一半
sims_all = trials(SNR_T, "eval")                             # 评估用的另一半：阈值不能在评估它的数据上选
t_best, _, _ = best_threshold(fit, C_WRONG / C_REJECT)
wrong_best = sum(1 for s_, ok in sims_all if s_ >= t_best and not ok)
rej_best = sum(1 for s_, _ in sims_all if s_ < t_best)
v["t_best"], v["wrong_best"], v["rej_best"] = t_best, wrong_best, rej_best
v["n_fit"], v["n_eval"] = len(fit), len(sims_all)
v["cost_best"] = wrong_best * C_WRONG + rej_best * C_REJECT
no_rej_wrong = sum(1 for s_, ok in sims_all if not ok)
v["wrong_norej"] = no_rej_wrong
v["cost_norej"] = no_rej_wrong * C_WRONG
v["saved"] = v["cost_norej"] - v["cost_best"]
v["rej_pct"] = rej_best / len(sims_all) * 100
# 代价之比不同时的最优阈值：比值越悬殊，越应该多拒识
for ratio in (1, 2, 5, 100):
    t_, _, _ = best_threshold(fit, ratio)
    w_ = sum(1 for s_, ok in sims_all if s_ >= t_ and not ok)
    r_ = sum(1 for s_, _ in sims_all if s_ < t_)
    v[f"t_r{ratio}"], v[f"rej_r{ratio}"], v[f"wrong_r{ratio}"] = t_, r_, w_

# ---------- （3）端到端延迟
ASR_MS = 90.0                                                # 一条 1 秒指令过一遍小模型的量级（算例 12.4.2 的办法，按 1 秒音频折算）
STAGES = [("端点检测（说完后再等）", 200.0), ("特征提取", 5.0), ("识别", ASR_MS), ("解析与校验", 5.0), ("下发到 AGV", 30.0)]
v["total_ms"] = sum(t for _, t in STAGES)
v["budget_ms"] = 1000.0
v["slack_ms"] = v["budget_ms"] - v["total_ms"]
for name, t in STAGES:
    key = {"端点检测（说完后再等）": "vad", "特征提取": "feat", "识别": "asr", "解析与校验": "parse", "下发到 AGV": "send"}[name]
    v[key + "_ms"] = t
v["asr_share"] = ASR_MS / v["total_ms"] * 100
out(**v)
