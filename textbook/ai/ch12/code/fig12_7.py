"""12.7 节的示意图（数值同程序 12.7.1）。

图 12.7.1：（a）识别准确率随信噪比下降：车间噪声大到一定程度，再好的模型也要靠拒识兜底；
（b）误执行与拒识的代价之比越悬殊，拒识阈值就要定得越高——宁可多问一遍，也别执行错的指令。
"""
import numpy as np
import runpy
from pathlib import Path

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
import sys
sys.path.insert(0, str(Path(__file__).parent))
from _ch12 import add_noise, utterance                                      # noqa: E402
import _cmds as D                                                      # noqa: E402

fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.0))
snrs, accs = D.acc_curve()
a.plot(snrs, accs, "-o", ms=4, lw=1.8, color=C["z"])
a.axhline(100, ls=":", lw=0.8, color=C["muted"])
a.set_xlabel(T("信噪比（dB）", "SNR (dB)"))
a.set_ylabel(T("指令识别准确率（%）", "command accuracy (%)"))
a.set_title(T("(a) 噪声越大，识别越差", "(a) Accuracy falls with noise"), fontsize=10)
a.grid(alpha=0.25, lw=0.5)
a.invert_xaxis()

ratios, ts, rejs = D.threshold_curve()
b.plot(ratios, ts, "-o", ms=4, lw=1.8, color=C["x"], label=T("最优拒识阈值", "best reject threshold"))
b2 = b.twinx()
b2.plot(ratios, rejs, "-s", ms=4, lw=1.4, color=C["z"], label=T("被拒识的比例（%）", "rejected (%)"))
b.set_xscale("log")
b.set_xlabel(T("误执行代价 ÷ 拒识代价", "cost of a wrong action ÷ cost of rejecting"))
b.set_ylabel(T("阈值", "threshold"), color=C["x"])
b2.set_ylabel(T("被拒识的比例（%）", "rejected (%)"), color=C["z"])
b.set_title(T("(b) 代价之比决定阈值", "(b) The cost ratio sets the threshold"), fontsize=10)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig12_7_1")
