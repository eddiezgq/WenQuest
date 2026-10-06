"""算例 12.1.1—12.1.2：语音信号的三笔账（12.1 节）。

（1）原始波形的数据量与帧率：16 kHz、16 位的单声道语音，一秒多少字节；分帧（25 ms 帧长、10 ms 帧移）后每秒多少帧，
    每帧多少个采样点、帧之间重叠多少。
（2）特征把数据压掉多少：一秒的波形 → 每秒 100 帧 × 80 维对数梅尔频谱 → 13 维 MFCC，三者的数据量之比。
    这就是"声学特征"的意义：对数梅尔频谱把数据量减半，MFCC 再压一个数量级，而识别需要的信息基本没丢。
（3）梅尔刻度在做什么：把 0—8000 Hz 按梅尔等分成 80 份后，低频处每赫兹对应的梅尔数远大于高频处，
    80 个滤波器里有相当一部分中心频率落在 1 kHz 以下——低频分得细、高频分得粗，与人耳一致。
"""
import numpy as np

from _ch12 import FRAME_MS, HOP, HOP_MS, N_FFT, N_MEL, SR, hz_to_mel, log_mel, mel_bank, mel_to_hz, mfcc, utterance
from bookout import out

v = {"sr": SR, "frame_ms": FRAME_MS, "hop_ms": HOP_MS, "n_fft": N_FFT, "n_mel": N_MEL, "hop": HOP}
# ---------- （1）波形与分帧
v["bytes_s"] = SR * 2                                        # 16 位
v["kB_s"] = SR * 2 / 1000
v["fps"] = 1000 / HOP_MS                                     # 每秒多少帧
v["overlap_ms"] = FRAME_MS - HOP_MS
v["overlap_pct"] = (FRAME_MS - HOP_MS) / FRAME_MS * 100
v["samples_per_frame"] = N_FFT
v["bins"] = N_FFT // 2 + 1                                   # 实数傅里叶变换的频点数
v["df"] = SR / N_FFT                                         # 频率分辨率（Hz）

# ---------- （2）三种表示的数据量（每秒，单精度）
x = utterance(["a", None, ("f", (3000, 7000)), "i", "u"])
m = log_mel(x)
c = mfcc(x)
v["dur_s"] = len(x) / SR
v["n_frames"] = m.shape[0]
v["wave_floats"] = SR                                        # 每秒的采样点数
v["mel_floats"] = v["fps"] * N_MEL
v["mfcc_floats"] = v["fps"] * c.shape[1]
v["n_mfcc"] = c.shape[1]
v["mel_ratio"] = v["wave_floats"] / v["mel_floats"]
v["mfcc_ratio"] = v["wave_floats"] / v["mfcc_floats"]

# ---------- （3）梅尔滤波器的宽度与密度
fb = mel_bank()
assert not (fb.sum(1) == 0).any(), "有全零的滤波器：三角窗太窄，被频率分辨率吃掉了"
pts = mel_to_hz(np.linspace(hz_to_mel(20.0), hz_to_mel(SR / 2), N_MEL + 2))
width = pts[2:] - pts[:-2]                                   # 每个三角窗的底宽（Hz）
centers = pts[1:-1]
v["mel_lo_hz"] = width[0]
v["mel_hi_hz"] = width[-1]
v["mel_ratio_hz"] = width[-1] / width[0]
v["mel_1000"] = float(hz_to_mel(1000.0))                     # 1000 Hz 对应多少梅尔
v["mel_2000"] = float(hz_to_mel(2000.0))
v["n_below_1k"] = int((centers < 1000).sum())                # 80 个滤波器里有多少个在 1 kHz 以下
v["pct_below_1k"] = v["n_below_1k"] / N_MEL * 100
v["band_below_1k"] = 1000 / (SR / 2) * 100                   # 1 kHz 只占 0—8 kHz 带宽的百分之几
v["dmel_100"] = float(hz_to_mel(101.0) - hz_to_mel(100.0))   # 100 Hz 附近，1 Hz 对应多少梅尔
v["dmel_6000"] = float(hz_to_mel(6001.0) - hz_to_mel(6000.0))
v["dmel_ratio"] = v["dmel_100"] / v["dmel_6000"]
out(**v)
