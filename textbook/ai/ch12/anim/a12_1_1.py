"""动画 12.1.1（配图 12.1.1）：从波形到梅尔频谱。
一段语音先被切成 25 毫秒一帧、每 10 毫秒移一次；每帧加窗后做傅里叶变换，得到这一帧的频谱；
频谱按梅尔刻度的三角滤波器归并成 80 个频带，取对数。一秒一万六千个数就变成 100 帧 × 80 个数，
而音素的结构——元音的共振峰、摩擦音的高频噪声带——都还在。

画面里的波形、频谱、梅尔频带都是真算出来的，不是示意图：元音按共振峰加权叠加谐波、摩擦音是带通噪声，
梅尔归并用的是真正的三角滤波器（按频点的实际频率算权重、每行归一化成单位面积），
所以“低频分得细、高频分得粗”在图上看得见。
渲染服务只允许 manim、wq_anim、numpy、math、random，所以这里按 code/_ch12.py 里的同一套公式
（VOWELS 共振峰表、F0、mel(f) = 2595 lg(1 + f/700)）就地重写一遍，参数与那边保持一致。"""
import numpy as np
from manim import *
from wq_anim import *

SR, N_FFT, HOP, N_MEL, F0 = 16000, 400, 160, 80, 120.0
VOWELS = {"a": (730, 1090, 2440), "i": (270, 2290, 3010), "u": (300, 870, 2240)}
FRAME_AT = 0.12                       # 画频谱用的那一帧（秒）：落在第一个元音 a 的中间


def vowel(name, dur=0.25, seed=0):
    rng = np.random.default_rng(1200 + seed)
    t = np.arange(int(dur * SR)) / SR
    f1, f2, f3 = VOWELS[name]
    x = np.zeros_like(t)
    for k in range(1, 40):
        f = F0 * k * (1 + 0.002 * np.sin(2 * np.pi * 4.5 * t))
        gain = sum(1.0 / (1 + ((F0 * k - fc) / 90.0) ** 2) for fc in (f1, f2, f3))
        x += gain / k * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    env = np.minimum(1.0, np.minimum(t / 0.02, (dur - t) / 0.03))
    return x / np.abs(x).max() * env


def fricative(dur=0.12, band=(3000, 7000), seed=77):
    rng = np.random.default_rng(1200 + seed)
    n = int(dur * SR)
    X = np.fft.rfft(rng.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < band[0]) | (f > band[1])] = 0
    y = np.fft.irfft(X, n)
    env = np.minimum(1.0, np.minimum(np.arange(n) / (0.01 * SR), (n - np.arange(n)) / (0.01 * SR)))
    return y / (np.abs(y).max() + 1e-9) * env


def mel_bank(n_mel=N_MEL, n_fft=N_FFT, fmin=20.0):
    def hz2mel(f):
        return 2595 * np.log10(1 + f / 700)

    def mel2hz(m):
        return 700 * (10 ** (m / 2595) - 1)

    pts = mel2hz(np.linspace(hz2mel(fmin), hz2mel(SR / 2), n_mel + 2))
    freqs = np.fft.rfftfreq(n_fft, 1 / SR)
    fb = np.zeros((n_mel, len(freqs)))
    for i in range(n_mel):
        lo, mid, hi = pts[i], pts[i + 1], pts[i + 2]
        fb[i] = np.clip(np.minimum((freqs - lo) / max(mid - lo, 1e-9),
                                   (hi - freqs) / max(hi - mid, 1e-9)), 0, None)
        if fb[i].sum() > 0:
            fb[i] /= fb[i].sum()                  # 单位面积：归并即加权平均
    return fb


X = np.concatenate([vowel("a", seed=0), np.zeros(int(0.08 * SR)),
                    fricative(), vowel("i", seed=3), vowel("u", seed=4)])
BANK = mel_bank()


class Lesson(Base):
    def construct(self):
        self.title("12.1", "从波形到梅尔频谱", "From waveform to the mel spectrogram")

        # 波形：真信号（元音 a—静音—摩擦音—元音 i—元音 u），抽稀后画出来
        step = max(1, len(X) // 1200)
        y = X[::step]
        y = y / (np.abs(y).max() + 1e-9)
        xs = np.linspace(-6, 6, len(y))
        pts = [[float(a), 1.6 + 0.5 * float(v), 0] for a, v in zip(xs, y)]
        wave = VMobject(stroke_width=1.6, color=BLUE).set_points_as_corners(pts)
        self.play(Create(wave), run_time=1.2)
        self.caption(f"语音是每秒一万六千个数的波形（这段 {len(X) / SR:.2f} 秒）",
                     f"Speech is a waveform: 16 000 numbers per second ({len(X) / SR:.2f} s here)")

        # 分帧：窗口的宽度就是 25 ms 在画面上占的比例
        wwid = 12.0 * (N_FFT / SR) / (len(X) / SR)
        x0 = -6 + wwid / 2
        win = Rectangle(width=wwid, height=1.3, color=YELLOW, stroke_width=2).move_to([x0, 1.6, 0])
        self.play(Create(win))
        self.caption("切成 25 毫秒一帧，每 10 毫秒移一次——相邻帧重叠 60%",
                     "Cut into 25 ms frames every 10 ms — 60% overlap")
        for k in (6, 14, 24):
            self.play(win.animate.move_to([x0 + 12.0 * k * HOP / len(X), 1.6, 0]), run_time=0.4)
        self.play(win.animate.move_to([x0 + 12.0 * (FRAME_AT * SR) / len(X), 1.6, 0]), run_time=0.5)

        # 这一帧的真频谱：201 个频点，为了看得清每 4 个点取其中最大的画一根
        i0 = int(FRAME_AT * SR) // HOP * HOP
        seg = X[i0:i0 + N_FFT]
        w = 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(len(seg)) / (len(seg) - 1))   # 汉明窗
        sp = np.abs(np.fft.rfft(seg * w, n=N_FFT)) ** 2 / N_FFT
        g = 10 * np.log10(sp + 1e-10)
        g = (g - g.min()) / (g.max() - g.min() + 1e-9)
        gs = g[: len(g) // 4 * 4].reshape(-1, 4).max(axis=1)
        bars = VGroup()
        for i, v in enumerate(gs):
            bars.add(Rectangle(width=0.16, height=max(0.05, float(v) * 1.4), fill_color=RED,
                               fill_opacity=0.65, stroke_width=0).move_to([-3.4 + i * 0.18, -1.3 + float(v) * 0.7, 0]))
        self.play(FadeIn(bars))
        self.caption(f"每帧做一次傅里叶变换：得到 {len(sp)} 个频点上的能量",
                     f"One Fourier transform per frame: energy at {len(sp)} bins")

        # 真的梅尔归并：低频的滤波器窄、高频的宽，所以每根柱子覆盖的频宽差得很远
        lg = np.log(BANK @ sp + 1e-10)
        lg = (lg - lg.min()) / (lg.max() - lg.min() + 1e-9)
        mel = VGroup()
        for i, j in enumerate(np.linspace(0, N_MEL - 1, 12).astype(int)):
            v = float(lg[j])
            mel.add(Rectangle(width=0.42, height=max(0.08, v * 1.4), fill_color=GREEN,
                              fill_opacity=0.7, stroke_width=0).move_to([2.0 + i * 0.46, -1.3 + v * 0.7, 0]))
        self.play(TransformFromCopy(bars, mel), run_time=1.0)
        self.caption("按梅尔刻度归并成 80 个频带：低频分得细、高频分得粗，与人耳一致",
                     "Pool into 80 mel bands: fine at low frequencies, coarse at high — like the ear")
        self.card([["声学特征", "Acoustic features"],
                   MathTex(r"\mathrm{mel}(f) = 2595\,\lg\!\left(1 + \frac{f}{700}\right)", font_size=40),
                   ["一秒：16 000 个采样点 → 100 帧 × 80 维", "One second: 16 000 samples → 100 frames × 80 bands"],
                   ["再做一次离散余弦变换，取前 13 个，就是 MFCC", "A DCT of that, first 13 coefficients, gives MFCCs"]])
