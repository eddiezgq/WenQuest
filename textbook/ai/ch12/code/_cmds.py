"""程序 12.7.1 与图 12.7.1 共用的部分：指令集、模板匹配器，以及两条曲线（准确率随信噪比、阈值随代价之比）。
放在这里是为了让算例与图用同一套数，不各算各的。"""
import numpy as np

from _ch12 import add_noise, log_mel, utterance

CMDS = {
    "前进": ["i", "a", None, "i"], "后退": ["u", "e", None, "u"], "左转": ["u", "a", None, "a"],
    "右转": ["i", "u", None, "a"], "停止": ["i", None, ("f", (3000, 7000)), "i"],
    "暂停": [("f", (2500, 6000)), "a", None, "i"], "继续": ["i", None, ("f", (4000, 8000)), "u"],
    "去一号工位": ["u", "i", None, "a", "u"], "去三号工位": ["u", ("f", (3500, 7500)), "a", None, "u"],
    "回充电桩": ["u", ("f", (3000, 7000)), "e", None, "a"],
}
NAMES = list(CMDS)
N_T = 24                                                     # 时间上重采样到 24 帧，保留先后顺序
SNRS = (20, 10, 5, 0, -5, -10, -15)
REPS = 24                                                    # 每条指令说 24 遍：前 12 遍定阈值，后 12 遍评估


def feat(x):
    """对数梅尔频谱 → 逐频带减去全句均值（倒谱均值归一，去掉稳态噪声与通道的影响）
    → 时间轴重采样到固定长度 → 拉直。保留先后顺序，比只取均值强得多。"""
    m = log_mel(x)
    m = m - m.mean(0, keepdims=True)
    idx = np.linspace(0, m.shape[0] - 1, N_T)
    lo, hi = np.floor(idx).astype(int), np.ceil(idx).astype(int)
    w = (idx - lo)[:, None]
    f = ((1 - w) * m[lo] + w * m[hi]).ravel()
    return f / (np.linalg.norm(f) + 1e-9)


TEMPLATES = {k: feat(utterance(v, seed=0)) for k, v in CMDS.items()}        # 每条指令"录"一次当模板（不变异）


def recognize(x):
    f = feat(x)
    sims = {k: float(f @ t) for k, t in TEMPLATES.items()}
    best = max(sims, key=sims.get)
    return best, sims[best]


def trials(snr, half=None):
    """在给定信噪比下跑一轮：返回 [(相似度, 是否认对)]。
    half="fit" 取前一半（用来定阈值），half="eval" 取后一半（用来评估）——阈值不能在评估它的那批数据上选。
    每遍的时长、基频与幅度都随种子变化（utterance 的 vary=True）：真人说同一句话不会两遍一模一样。"""
    reps = range(REPS) if half is None else (range(REPS // 2) if half == "fit" else range(REPS // 2, REPS))
    out = []
    for i, k in enumerate(NAMES):
        for rep in reps:
            x = utterance(CMDS[k], seed=100 + 7 * rep, vary=True)
            y = add_noise(x, snr, seed=200 + rep + 11 * i)
            pred, sim = recognize(y)
            out.append((sim, pred == k))
    return out


def acc_curve():
    """准确率随信噪比的曲线。"""
    accs = [100 * np.mean([ok for _, ok in trials(s)]) for s in SNRS]
    return list(SNRS), accs


def best_threshold(sims, ratio):
    """给定代价之比（误执行 ÷ 拒识），求使总代价最小的拒识阈值。返回 (阈值, 误执行数, 拒识数)。"""
    lo, hi = min(s for s, _ in sims), max(s for s, _ in sims)
    best = (lo, 1e18, 0, 0)
    for t in np.linspace(lo, hi, 200):
        w = sum(1 for s, ok in sims if s >= t and not ok)
        r = sum(1 for s, _ in sims if s < t)
        c = w * ratio + r
        if c < best[1]:
            best = (float(t), c, w, r)
    return best[0], best[2], best[3]


def threshold_curve(snr=-10, ratios=(1, 2, 3, 5, 10, 20, 50, 100)):
    """最优阈值与被拒识的比例随代价之比的变化（阈值在"定阈值"的那一半上选）。"""
    sims = trials(snr, "fit")
    ts, rejs = [], []
    for r in ratios:
        t, _, rej = best_threshold(sims, r)
        ts.append(t)
        rejs.append(rej / len(sims) * 100)
    return list(ratios), ts, rejs
