"""12.1 节的示意图（信号与特征同 _ch12.py 与程序 12.1.1）。

图 12.1.1：同一段合成语音的三种看法：（a）波形（时间—幅度）；（b）短时傅里叶变换的幅度谱（时间—频率，对数幅度）；
（c）对数梅尔频谱（时间—梅尔频带）。从左到右，数据量一路压缩，而区分音素要用的结构——共振峰的位置、
摩擦音的高频噪声带——都还在。
"""
import numpy as np

from _ch12 import HOP, N_FFT, SR, frames, log_mel, utterance
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
x = utterance(["a", None, ("f", (3000, 7000)), "i", None, "u"])
t = np.arange(len(x)) / SR
spec = np.abs(np.fft.rfft(frames(x), axis=1)) ** 2
mel = log_mel(x)

fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.7))
axes[0].plot(t, x, lw=0.4, color=C["z"])
axes[0].set_xlabel(T("时间（s）", "time (s)"))
axes[0].set_ylabel(T("幅度", "amplitude"))
axes[0].set_title(T("(a) 波形：每秒 16 000 个数", "(a) Waveform: 16 000 numbers per second"), fontsize=10)
axes[0].set_xlim(0, t[-1])

ext = [0, len(x) / SR, 0, SR / 2 / 1000]
axes[1].imshow(np.log(spec.T + 1e-10), origin="lower", aspect="auto", extent=ext, cmap="magma")
axes[1].set_xlabel(T("时间（s）", "time (s)"))
axes[1].set_ylabel(T("频率（kHz）", "frequency (kHz)"))
axes[1].set_title(T("(b) 幅度谱：每秒 100 帧 × 201 个频点", "(b) Spectrogram: 100 frames × 201 bins"), fontsize=10)

axes[2].imshow(mel.T, origin="lower", aspect="auto", extent=[0, len(x) / SR, 0, mel.shape[1]], cmap="magma")
axes[2].set_xlabel(T("时间（s）", "time (s)"))
axes[2].set_ylabel(T("梅尔频带", "mel band"))
axes[2].set_title(T("(c) 对数梅尔频谱：每秒 100 帧 × 80 维", "(c) Log-mel: 100 frames × 80 bands"), fontsize=10)
fig.tight_layout()
figure(fig, "fig12_1_1")
