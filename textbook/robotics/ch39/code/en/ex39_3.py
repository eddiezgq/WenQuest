"""Examples 39.3.1–39.3.3: quantization and aliasing.

39.3.1 12-bit ADC, reference voltage 2.5 V: least significant bit, quantization noise, ideal signal-to-noise ratio,
       and the corresponding force resolution at the end of the measurement chain.
39.3.2 Computing the alias frequency f_a = |f − k·f_s|: motor vibration at 950 Hz sampled at 1 kHz; 50 Hz mains sampled
       at 60 Hz.
39.3.3 Numerical check: a 950 Hz sine sampled at 1 kHz gives, point by point, the same samples as a 50 Hz sine (inverted).
"""
import math

import numpy as np

from _meas import ADC_BITS, F_FS, GAIN, RO, V_EX, V_REF, adc
from bookout import out


def alias(f, fs):
    """Apparent frequency, folded into [0, fs/2]."""
    r = f % fs
    return min(r, fs - r)


lsb = V_REF / 2 ** ADC_BITS
q_rms = lsb / math.sqrt(12)
snr = 6.02 * ADC_BITS + 1.76
# measure the quantization SNR with a full-scale sine, as a check of 6.02N + 1.76 dB
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
