"""第 12 章共用的工具：按公式合成的语音信号、声学特征（梅尔频谱与 MFCC）、维特比解码、CTC 的前向算法、
编辑距离与字错率。

**为什么是合成的信号**：仓库里不放录音（与第 11 章不放图片同理）。语音的道理——分帧、频谱、共振峰、对齐——
用程序合成的信号讲得一样清楚，而且每个数都能复算。合成的"元音"是几个共振峰的叠加，"辅音"是一段带通噪声，
再叠上车间的背景噪声；它不像真人说话，但频谱上该有的结构都有。真实录音上的识别率要在云端实测（12.4 节）。

约定：采样率 16 kHz（语音识别的常用值），帧长 25 ms、帧移 10 ms（即每秒 100 帧），梅尔滤波器 80 个。
"""
from __future__ import annotations

import numpy as np

SR = 16000                       # 采样率（Hz）
FRAME_MS, HOP_MS = 25.0, 10.0    # 帧长与帧移（ms）
N_MEL = 80                       # 梅尔滤波器的个数
N_FFT = 400                      # 25 ms × 16 kHz = 400 个采样点
HOP = int(SR * HOP_MS / 1000)    # 160 个采样点

# 几个元音的前三个共振峰（Hz）：彼得森与巴尼 1952 年测得的成年男声均值（英语元音；"e" 这一组对应英语的 /ɛ/，
# 与汉语的 e 不同）。真实值因人、因语言而异，这里只用来合成一个频谱结构像样的信号。
VOWELS = {"a": (730, 1090, 2440), "i": (270, 2290, 3010), "u": (300, 870, 2240), "e": (530, 1840, 2480)}
F0 = 120.0                       # 基频（Hz）


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(1200 + seed)


def vowel(name: str, dur: float = 0.25, seed: int = 0, sr: int = SR, f0: float | None = None) -> np.ndarray:
    """一个元音：基频的谐波按共振峰加权叠加，加一点轻微的抖动与包络。f0 不给时用默认基频。"""
    rng = _rng(seed)
    t = np.arange(int(dur * sr)) / sr
    f0 = f0 or F0
    f1, f2, f3 = VOWELS[name]
    x = np.zeros_like(t)
    for k in range(1, 40):                                   # 基频的前 40 个谐波
        f = f0 * k * (1 + 0.002 * np.sin(2 * np.pi * 4.5 * t))   # 轻微的颤动
        gain = sum(1.0 / (1 + ((f0 * k - fc) / 90.0) ** 2) for fc in (f1, f2, f3))
        x += gain / k * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    env = np.minimum(1.0, np.minimum(t / 0.02, (dur - t) / 0.03))   # 起落包络
    return (x / np.abs(x).max() * env).astype(np.float32)


def fricative(dur: float = 0.12, band=(3000, 7000), seed: int = 0, sr: int = SR) -> np.ndarray:
    """一个摩擦音：带通噪声（如 s、sh）。"""
    rng = _rng(seed + 77)
    n = int(dur * sr)
    x = rng.normal(0, 1, n)
    f = np.fft.rfftfreq(n, 1 / sr)
    X = np.fft.rfft(x)
    X[(f < band[0]) | (f > band[1])] = 0
    y = np.fft.irfft(X, n)
    env = np.minimum(1.0, np.minimum(np.arange(n) / (0.01 * sr), (n - np.arange(n)) / (0.01 * sr)))
    return (y / (np.abs(y).max() + 1e-9) * env).astype(np.float32)


def silence(dur: float = 0.08, sr: int = SR) -> np.ndarray:
    return np.zeros(int(dur * sr), dtype=np.float32)


def workshop_noise(n: int, seed: int = 0, sr: int = SR) -> np.ndarray:
    """车间背景噪声：低频为主的风机与机床声（粉红噪声一类）加上偶尔的金属撞击。"""
    rng = _rng(seed + 301)
    white = rng.normal(0, 1, n)
    f = np.fft.rfftfreq(n, 1 / sr)
    X = np.fft.rfft(white) / np.sqrt(np.maximum(f, 1.0))     # 1/f 谱：低频强
    y = np.fft.irfft(X, n)
    for _ in range(max(1, n // sr)):                          # 每秒一次撞击
        i = int(rng.integers(0, max(n - 1600, 1)))
        y[i:i + 1600] += rng.uniform(0.5, 1.5) * np.exp(-np.arange(1600) / 200) * rng.normal(0, 1, 1600)
    return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)


def utterance(phones: list, seed: int = 0, vary: bool = False) -> np.ndarray:
    """把若干个音素接起来：元音名、('f', (低, 高)) 表示摩擦音、None 表示静音。
    vary=True 时，同一串音素每遍的时长（±30%）、基频（±15%）与幅度（±20%）都随种子变化——
    真人说同一句话不会两遍一模一样，没有这点变异，模板匹配会轻松得不真实（12.7 节）。"""
    rng = _rng(seed + 999)
    kd = rng.uniform(0.7, 1.3) if vary else 1.0
    kf = rng.uniform(0.85, 1.15) if vary else 1.0
    ka = rng.uniform(0.8, 1.2) if vary else 1.0
    out = []
    for i, p in enumerate(phones):
        if p is None:
            out.append(silence(0.08 * kd))
        elif isinstance(p, tuple):
            out.append(fricative(0.12 * kd, band=p[1], seed=seed + i))
        else:
            out.append(vowel(p, 0.25 * kd, seed=seed + i, f0=F0 * kf))
    return (np.concatenate(out) * ka).astype(np.float32)


def add_noise(x: np.ndarray, snr_db: float, seed: int = 0) -> np.ndarray:
    """按给定的信噪比叠加车间噪声。信噪比 = 10 lg(信号功率 / 噪声功率)，功率按**整句**平均
    （含静音段）——语音段的实际信噪比会比标称略高，句中静音越多差得越多。"""
    noise = workshop_noise(len(x), seed)
    ps, pn = float(np.mean(x ** 2)), float(np.mean(noise ** 2))
    k = np.sqrt(ps / (pn * 10 ** (snr_db / 10)))
    return (x + k * noise).astype(np.float32)


# ---------------------------------------------------------------- 声学特征

def frames(x: np.ndarray, n_fft: int = N_FFT, hop: int = HOP) -> np.ndarray:
    """分帧并加汉明窗：返回 (帧数, n_fft)。"""
    n = 1 + max(0, (len(x) - n_fft) // hop)
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n)[:, None]
    return x[idx] * np.hamming(n_fft)[None, :]


def hz_to_mel(f):
    """梅尔刻度（O'Shaughnessy 的常用式）：人耳对低频的分辨率高，对高频低。"""
    return 2595.0 * np.log10(1.0 + np.asarray(f, dtype=float) / 700.0)


def mel_to_hz(m):
    return 700.0 * (10.0 ** (np.asarray(m, dtype=float) / 2595.0) - 1.0)


def mel_bank(n_mel: int = N_MEL, n_fft: int = N_FFT, sr: int = SR, fmin: float = 20.0, fmax: float | None = None):
    """三角形的梅尔滤波器组：在梅尔刻度上等间隔取 n_mel + 2 个点，相邻三点构成一个三角窗。返回 (n_mel, n_fft//2+1)。

    权重直接按频点的**实际频率**算，不先把三角窗的顶点取整到频点——取整会让低频那几个窄窗（底宽只有几十赫兹，
    而 400 点的傅里叶变换频率分辨率是 40 赫兹）塌成全零行，那些频带就成了永远不变的常数。
    每行再归一化成单位面积，使"归并"真的是加权平均。"""
    fmax = fmax or sr / 2
    pts = mel_to_hz(np.linspace(hz_to_mel(fmin), hz_to_mel(fmax), n_mel + 2))
    freqs = np.fft.rfftfreq(n_fft, 1 / sr)
    fb = np.zeros((n_mel, len(freqs)))
    for i in range(n_mel):
        lo, mid, hi = pts[i], pts[i + 1], pts[i + 2]
        left = (freqs - lo) / max(mid - lo, 1e-9)
        right = (hi - freqs) / max(hi - mid, 1e-9)
        fb[i] = np.clip(np.minimum(left, right), 0, None)
        area = fb[i].sum()
        if area > 0:
            fb[i] /= area                                     # 单位面积：归并即加权平均
    return fb


def log_mel(x: np.ndarray, n_mel: int = N_MEL) -> np.ndarray:
    """对数梅尔频谱：分帧 → 幅度谱的平方 → 梅尔滤波（单位面积的三角窗）→ 取对数。返回 (帧数, n_mel)。"""
    spec = np.abs(np.fft.rfft(frames(x), axis=1)) ** 2
    return np.log(spec @ mel_bank(n_mel).T + 1e-10)


def mfcc(x: np.ndarray, n_mfcc: int = 13, n_mel: int = N_MEL) -> np.ndarray:
    """MFCC：对数梅尔频谱再做一次离散余弦变换，取前几个系数（去掉相关性，压缩维度）。"""
    m = log_mel(x, n_mel)
    k = np.arange(n_mel)
    dct = np.cos(np.pi / n_mel * (k[None, :] + 0.5) * np.arange(n_mfcc)[:, None])
    return m @ dct.T


# ---------------------------------------------------------------- 解码与评价

def viterbi(obs_logp: np.ndarray, trans_logp: np.ndarray, init_logp: np.ndarray) -> tuple:
    """维特比解码：给定每帧在各状态上的对数似然、状态转移与初始概率，求最可能的状态序列。
    返回 (最优路径, 它的对数概率)。"""
    T, S = obs_logp.shape
    dp = np.full((T, S), -np.inf)
    bk = np.zeros((T, S), int)
    dp[0] = init_logp + obs_logp[0]
    for t in range(1, T):
        for s in range(S):
            cand = dp[t - 1] + trans_logp[:, s]
            bk[t, s] = int(np.argmax(cand))
            dp[t, s] = cand[bk[t, s]] + obs_logp[t, s]
    path = [int(np.argmax(dp[-1]))]
    for t in range(T - 1, 0, -1):
        path.append(bk[t, path[-1]])
    return list(reversed(path)), float(dp[-1].max())


def ctc_forward(logp: np.ndarray, target: list, blank: int = 0) -> float:
    """CTC 的前向算法：给定每帧各符号的对数概率与目标序列，求所有能折叠成目标的路径的概率之和（取对数）。
    折叠规则：先去掉相邻的重复，再去掉空白符。标准做法是在目标的每个符号之间插入空白符。"""
    ext = [blank]
    for c in target:
        ext += [c, blank]                                    # 目标扩展成 空白 c 空白 c … 空白
    T, S = logp.shape[0], len(ext)
    a = np.full((T, S), -np.inf)
    a[0, 0] = logp[0, ext[0]]
    if S > 1:
        a[0, 1] = logp[0, ext[1]]
    for t in range(1, T):
        for s in range(S):
            best = a[t - 1, s]
            if s > 0:
                best = np.logaddexp(best, a[t - 1, s - 1])
            if s > 1 and ext[s] != blank and ext[s] != ext[s - 2]:
                best = np.logaddexp(best, a[t - 1, s - 2])
            a[t, s] = best + logp[t, ext[s]]
    return float(np.logaddexp(a[-1, -1], a[-1, -2])) if S > 1 else float(a[-1, -1])


def ctc_greedy(logp: np.ndarray, blank: int = 0) -> list:
    """贪心解码：每帧取概率最大的符号，再按折叠规则去重、去空白。"""
    best = logp.argmax(1)
    out, prev = [], -1
    for b in best:
        if b != prev and b != blank:
            out.append(int(b))
        prev = int(b)
    return out


def edit_distance(a: list, b: list) -> int:
    """编辑距离（插入、删除、替换各算一次）。"""
    dp = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, y in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (x != y))
    return dp[-1]


def error_rate(ref: list, hyp: list) -> float:
    """字错率（或词错率）：编辑距离除以参考的长度。可能大于 1（插入很多时）。"""
    return edit_distance(ref, hyp) / max(len(ref), 1)


# ---------- 说话人嵌入（12.6 节；程序 12.6.1 与图 12.6.1 共用，保证两处数字一致）
SPK_N, SPK_UTT, SPK_DIM, SPK_SPREAD = 40, 8, 32, 1.25


def speaker_embeddings(seed: int = 126, n_spk: int = SPK_N, n_utt: int = SPK_UTT,
                       dim: int = SPK_DIM, spread: float = SPK_SPREAD) -> np.ndarray:
    """合成的说话人嵌入：每个说话人一个中心方向，他的每段语音在中心附近散开，最后都归一化到单位球面。
    spread 越大，两类分数越重叠、等错误率越高。"""
    rng = np.random.default_rng(seed)
    centers = rng.normal(0, 1, (n_spk, dim))
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)
    emb = centers[:, None, :] + spread * rng.normal(0, 1, (n_spk, n_utt, dim)) / np.sqrt(dim)
    emb /= np.linalg.norm(emb, axis=2, keepdims=True)
    return emb


def speaker_scores(emb: np.ndarray | None = None, **kw) -> tuple:
    """算出两堆余弦相似度：同一人的两段（目标试验）与不同人的两段（冒认试验）。
    不同人的那一堆要把两边的所有段都配上（不只配相同序号的那一段），否则只用到了可用对的 1/n_utt。"""
    e = speaker_embeddings(**kw) if emb is None else emb
    n_spk, n_utt = e.shape[0], e.shape[1]
    same = np.array([float(e[i, a] @ e[i, b])
                     for i in range(n_spk) for a in range(n_utt) for b in range(a + 1, n_utt)])
    diff = np.array([float(e[i, a] @ e[j, b])
                     for i in range(n_spk) for j in range(i + 1, n_spk)
                     for a in range(n_utt) for b in range(n_utt)])
    return same, diff
