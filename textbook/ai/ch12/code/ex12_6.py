"""算例 12.6.1—12.6.2：说话人识别与语音增强（12.6 节）。

（1）说话人识别：把一段语音映射成一个固定长度的向量（嵌入），同一个人的两段靠得近、不同人的远。
    判定用余弦相似度加一个阈值；阈值越高，冒认通过率（错误接受）越低、本人被拒率（错误拒绝）越高，
    两者相等处称为等错误率（EER）。本程序用合成的嵌入（同一说话人的向量围绕各自的中心散开）算出这条曲线。
（2）语音增强：按不同信噪比叠加车间噪声，看增强（这里用最简单的谱减法）能把信噪比提高多少，
    以及它对后面识别的影响——增强会引入失真，信噪比高的时候反而可能帮倒忙。
"""
import numpy as np

from _ch12 import SPK_N, SPK_UTT, SR, add_noise, speaker_scores, utterance
from bookout import out

v = {}
# ---------- （1）嵌入与等错误率
same, diff = speaker_scores()                                # 嵌入与配对都在 _ch12 里，图 12.6.1 用的是同一组
v["n_spk"], v["n_utt"] = SPK_N, SPK_UTT
v["n_same"], v["n_diff"] = len(same), len(diff)
v["cos_same"], v["cos_diff"] = float(same.mean()), float(diff.mean())
best, gap = (1.0, 0.0, -0.2), 1e9
for t in np.linspace(-0.2, 1.0, 400):
    far = float((diff >= t).mean())                          # 错误接受（冒认通过）
    frr = float((same < t).mean())                           # 错误拒绝（本人被拒）
    if abs(far - frr) < gap:
        best, gap = (far, frr, float(t)), abs(far - frr)
v["t_eer"] = best[2]
v["eer"] = (best[0] + best[1]) / 2 * 100
for t in (0.3, 0.5):
    v[f"far_{int(t * 10)}"] = float((diff >= t).mean()) * 100
    v[f"frr_{int(t * 10)}"] = float((same < t).mean()) * 100

# ---------- （2）谱减法增强（逐帧，重叠相加）
def spectral_subtract(y, n_noise_frames=12, over=1.5, floor=0.08, n_fft=512, hop=128):
    """最简单的增强：用开头几帧（只有噪声）估出噪声的幅度谱，从每帧的幅度里减掉它，相位不动。
    over 是过减因子，floor 是谱底——减过头会留下忽隐忽现的“音乐噪声”，所以要留一个底。"""
    win = np.hanning(n_fft)
    n = 1 + max(0, (len(y) - n_fft) // hop)
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n)[:, None]
    F = np.fft.rfft(y[idx] * win, axis=1)
    mag, pha = np.abs(F), np.angle(F)
    noise = mag[:n_noise_frames].mean(0)
    clean = np.maximum(mag - over * noise, floor * mag)
    G = clean * np.exp(1j * pha)
    g = np.fft.irfft(G, n_fft, axis=1) * win
    out_ = np.zeros(len(y))
    wsum = np.zeros(len(y))
    for i in range(n):
        out_[i * hop:i * hop + n_fft] += g[i]
        wsum[i * hop:i * hop + n_fft] += win ** 2
    return (out_ / np.maximum(wsum, 1e-6)).astype(np.float32)


def snr_of(est, ref):
    """把估计与参考对齐幅度后算信噪比（dB）。"""
    k = float(np.dot(est, ref) / max(np.dot(ref, ref), 1e-12))
    return float(10 * np.log10(np.mean((k * ref) ** 2) / max(np.mean((est - k * ref) ** 2), 1e-12)))


x = np.concatenate([np.zeros(int(0.2 * SR), dtype=np.float32),          # 开头留 0.2 秒静音，供估噪声
                    utterance(["a", None, ("f", (3000, 7000)), "i", None, "u"])])
sil = slice(0, int(0.18 * SR))                                       # 开头的静音段：那里只有噪声
sp = slice(int(0.25 * SR), len(x))                                   # 后面的语音段
for snr in (0, 10, 20):
    y = add_noise(x, snr, seed=3)
    z = spectral_subtract(y)[:len(x)]
    v[f"snr{snr}_sil_db"] = float(10 * np.log10(np.mean(y[sil] ** 2) / max(np.mean(z[sil] ** 2), 1e-12)))
    k = float(np.dot(z[sp], x[sp]) / max(np.dot(x[sp], x[sp]), 1e-12))
    v[f"snr{snr}_dist_db"] = float(10 * np.log10(np.mean((k * x[sp]) ** 2) / max(np.mean((z[sp] - k * x[sp]) ** 2), 1e-12)))
    v[f"snr{snr}_wave_db"] = snr_of(z, x) - snr_of(y[:len(x)], x)    # 波形信噪比的变化（常常是负的）
v["sil_drop_0"], v["dist_0"] = v["snr0_sil_db"], v["snr0_dist_db"]
v["snr0_wave_drop"] = -v["snr0_wave_db"]            # 正数，表示“变差了多少 dB”
assert v["snr0_wave_db"] < 0, "谱减法在 0 dB 下本该让波形信噪比变差；这个结论不能靠手写"
out(**v)
