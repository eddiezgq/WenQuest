# Fig. 15-9 (English): three drive and freewheeling schemes for the trimming solenoid.
import numpy as np
from en_ch15_style import *

R, Lh, tau = 6.0, 0.030, 5.0       # ohm, H, ms
toff, Ipull, Ihold, Uz = 8.0, 3.0, 1.2, 48.0
t = np.arange(0, 14.001, 0.5)
# 24 V direct drive, diode freewheeling
i24 = np.where(t <= toff, 4 * (1 - np.exp(-t / tau)), 4 * (1 - np.exp(-toff / tau)) * np.exp(-(t - toff) / tau))
# 75 V boost until 3 A, then 24 V PWM hold (average heads to 1.2 A)
tp = -tau * np.log(1 - Ipull / 12.5)               # 1.37 ms
def boost(tt):
    return np.where(tt <= tp, 12.5 * (1 - np.exp(-tt / tau)), Ihold + (Ipull - Ihold) * np.exp(-(tt - tp) / tau))
i_off = float(boost(np.array(toff)))               # about 1.68 A at switch-off
ion = boost(t)
i_tvs = np.where(t <= toff, ion, np.maximum(i_off - Uz / Lh / 1000 * (t - toff), 0))
i_dio = i_off * np.exp(-(t - toff) / tau)
ma = t >= toff

fig = figure(792 / 1344)
header(fig, 'Overvoltage drive cuts pull-in from 6.9 ms to 1.4 ms; a TVS cuts release from about 5 ms to 1 ms',
       'Coil R = 6 Ω, L = 30 mH (τ = 5 ms); pulls in at 3 A, releases below 0.6 A; switched off at 8 ms (example values)')
ax = fig.add_axes([0.132, 0.197, 0.815, 0.649])
clean(ax)
ax.set_xlim(0, 14); ax.set_ylim(0, 4.15)
ax.set_yticks([0, 1, 2, 3, 4]); ax.set_xticks(range(0, 15, 2))
ax.axhline(3, color=INK, lw=1.2, ls=(0, (1.5, 2.5)))
ax.axhline(0.6, color=INK, lw=1.2, ls=(0, (1.5, 2.5)))
ax.axvline(8, color=GREY, lw=1.4, ls=(0, (4, 3)))
ax.text(8.15, 4.1, 'Switch-off', color=MUTED, va='top')
ax.plot(t, i24, '--o', color=GREY, lw=2.2, ms=3.5, clip_on=False)
ax.plot(t[ma], i_dio[ma], '-o', color=ORANGE, lw=2.2, ms=3.5, clip_on=False)
ax.plot(t, i_tvs, '-o', color=BLUE, lw=2.6, ms=3.5, clip_on=False)
ax.text(13.95, 3.07, 'Pull-in current 3 A', color=INK, ha='right', va='bottom')
ax.text(5.5, 0.67, 'Release current 0.6 A', color=INK, ha='center', va='bottom')
ax.text(1.65, 3.1, '75 V boost → PWM hold', color=INK, ha='left', va='bottom')
ax.text(5.4, 3.12, '24 V direct drive', color=GREY, ha='center', va='bottom', fontsize=11)
ax.text(9.9, 1.17, 'Diode freewheeling: slow decay', color=ORANGE, ha='left', va='bottom')
ax.text(9.3, 0.25, 'TVS freewheeling: fast release', color=BLUE, ha='left', va='bottom')
ax.set_xlabel('Time (ms)', color=MUTED, labelpad=12, fontsize=10.5)
ylabel(fig, ax, 'Coil current', 'A', yfrac=0.6)
foot(fig, ['Hold current falls from 3 A towards 1.2 A (PWM duty about 30%); heating goes as I²R, only about one-tenth to one-sixth of 24 V continuous drive (4 A steady)'], 0.075)
print('tp', tp, 'ioff', i_off)
save(fig, 'w_830708e2')
