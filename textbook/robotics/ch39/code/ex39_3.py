"""算例 39.3.1–39.3.3：量化与混叠。

39.3.1 12 位 ADC、参考电压 2.5 V：最低有效位、量化噪声、理想信噪比，以及接在测量链后面对应的力分辨率。
39.3.2 混叠频率 f_a = |f − k·f_s| 的计算：电机振动 950 Hz 用 1 kHz 采样；50 Hz 工频用 60 Hz 采样。
39.3.3 数值验证：对 950 Hz 正弦以 1 kHz 采样，所得样本与 50 Hz 正弦（相位反向）的样本逐点相同。
"""
import math

import numpy as np

from _meas import ADC_BITS, F_FS, GAIN, RO, V_EX, V_REF, adc
from bookout import out


def alias(f, fs):
    """折叠到 [0, fs/2] 的表观频率。"""
    r = f % fs
    return min(r, fs - r)


lsb = V_REF / 2 ** ADC_BITS
q_rms = lsb / math.sqrt(12)
snr = 6.02 * ADC_BITS + 1.76
# 用满幅正弦实测量化信噪比，核对 6.02N + 1.76 dB
t = np.arange(200000)
v = V_REF / 2 * (1 + 0.999999 * np.sin(2 * math.pi * 0.0123457 * t))
qerr = (adc(v) + 0.5) * lsb - v
snr_sim = 20 * math.log10((V_REF / 2 / math.sqrt(2)) / qerr.std())
assert abs(snr_sim - snr) < 0.3
f_res = lsb / (GAIN * RO * V_EX / F_FS)

a1 = alias(950, 1000)
a2 = alias(50, 60)
a3 = alias(1950, 1000)
fs, f = 1000.0, 950.0
n = np.arange(40)
s_hi = np.sin(2 * math.pi * f * n / fs)
s_lo = -np.sin(2 * math.pi * a1 * n / fs)
assert np.allclose(s_hi, s_lo, atol=1e-9)

out(lsb_mV=lsb * 1e3, q_uV=q_rms * 1e6, snr=snr, snr_sim=snr_sim, f_res=f_res, codes=2 ** ADC_BITS,
    a1=a1, a2=a2, a3=a3)
