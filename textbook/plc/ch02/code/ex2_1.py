"""2.1 节：上料输送线电动机的额定电流与主电路器件的选择；图 2.1.1（主电路与控制电路）、图 2.1.2（开关量与模拟量）。

电动机：IE2 级 0.75 kW 四极三相异步电动机，380 V，效率约 80 %，功率因数约 0.75（数值以铭牌和样本为准）。
启动电流倍数取 6.5（与虚拟设备的电动机模型相同，程序 2.3.1 的测试里实测启动电流也由它而来）。"""
import math
from bookout import figure, out, T, style
from _draw02 import (control, frame, group, motor, phase_lines, rails3, _l, _lab, dot, P, MUTED, INK, ACCENT, GREEN, WARM)

P_KW, U, ETA, PF, KI = 0.75, 380.0, 0.80, 0.75, 6.5
In = P_KW * 1000 / (math.sqrt(3) * U * ETA * PF)
Ist = KI * In
# Q1: a 4 A miniature circuit breaker, characteristic D (instantaneous trip 10–20 × In)
q1_in = 4
q1_lo, q1_hi = 10 * q1_in, 20 * q1_in
peak = 2.0 * Ist          # r.m.s. of the first half-cycle: with the decaying d.c. component up to about twice the steady starting current
# F1: overload relay with a 1.6–2.5 A range, set to the rated current
f1_set = round(In, 1)
# KM1: the smallest AC-3 contactor, 9 A at 400 V
km1 = 9
# control circuit: the coil of a DC 24 V contactor of this size takes about 2–3 W
p_coil = 2.4
i_coil = p_coil / 24

PB = {"act": "push"}
TH = {"act": "thermal"}
ES = {"act": "estop"}


def circuits():
    plt = style()
    fig, (am, ac) = plt.subplots(1, 2, figsize=(10.4, 6.6), gridspec_kw={"width_ratios": [3.2, 6.0]})
    x = 0.6
    rails3(am, x, 0)
    phase_lines(am, x, 0, -0.3)
    group(am, x, -0.3, "CB", "Q1")
    phase_lines(am, x, -1.3, -1.7)
    group(am, x, -1.7, "KM", "KM1")
    phase_lines(am, x, -2.7, -3.1)
    group(am, x, -3.1, "OL", "F1")
    phase_lines(am, x, -4.1, -4.4)
    yb = motor(am, x, -4.4, "M1")
    am.text(x + P, yb - 0.15, T("0.75 kW  380 V\n" + f"{In:.1f} A", "0.75 kW  380 V\n" + f"{In:.1f} A"), ha="center", va="top", fontsize=8, color=MUTED)
    frame(am, (-0.9, 2.2), (-6.6, 0.5))
    am.set_title(T("主电路（AC 380 V）", "Main circuit (AC 380 V)"), fontsize=10.5)

    run = [("NC", "S0", ES), ("NC", "S2", PB), ("NC", "F1", TH), ("PAR", [[("NO", "S1", PB)], [("NO", "KM1")]], 1.25), ("COIL", "KM1")]
    h1 = [("NO", "KM1"), ("LAMP", "H1")]
    h2 = [("NO", "F1", TH), ("LAMP", "H2")]
    xs, bot = control(ac, [run, h1, h2], top=0, x0=0.0, xs=[1.5, 4.0, 5.6],
                      notes=[T("电动机", "motor"), T("运行灯（绿）", "running (green)"), T("过载灯（红）", "overload (red)")])
    frame(ac, (-0.7, 6.4), (bot - 1.1, 0.5))
    ac.set_title(T("控制电路（DC 24 V）", "Control circuit (DC 24 V)"), fontsize=10.5)
    return fig


def signals():
    """左：开关量（按钮按下与松开，24 V / 0 V）；右：模拟量（4–20 mA 温度变送器）。"""
    import numpy as np
    plt = style()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.0))
    t = np.linspace(0, 4, 800)
    v = np.where((t > 0.8) & (t < 2.6), 24.0, 0.0)
    a1.plot(t, v, color=GREEN, lw=1.6)
    a1.set_ylim(-3, 30)
    a1.set_yticks([0, 24])
    a1.set_ylabel(T("电压 / V", "voltage / V"), fontsize=9)
    a1.set_xlabel(T("时间 / s", "time / s"), fontsize=9)
    a1.text(1.7, 26, T("按下：1", "pressed: 1"), ha="center", fontsize=8.6, color=GREEN)
    a1.text(3.3, 2, T("松开：0", "released: 0"), ha="center", fontsize=8.6, color=MUTED)
    a1.set_title(T("（a）开关量：只有两个状态", "(a) discrete: two states only"), fontsize=10)
    temp = 20 + 55 * (1 - np.exp(-t / 1.2))
    ma = 4 + 16 * temp / 150
    a2.plot(t, ma, color=ACCENT, lw=1.6)
    a2.set_ylim(0, 22)
    a2.set_yticks([4, 8, 12, 16, 20])
    a2.set_ylabel(T("电流 / mA", "current / mA"), fontsize=9)
    a2.set_xlabel(T("时间 / min", "time / min"), fontsize=9)
    a2.text(2.0, 5.2, T("0–150 °C ↔ 4–20 mA", "0–150 °C ↔ 4–20 mA"), fontsize=8.6, color=MUTED)
    a2.set_title(T("（b）模拟量：连续变化", "(b) analog: varies continuously"), fontsize=10)
    for ax in (a1, a2):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


figure(circuits(), "fig2_1_1")
figure(signals(), "fig2_1_2")
out(In=round(In, 2), In1=round(In, 1), Ist=round(Ist, 1), q1_in=q1_in, q1_lo=q1_lo, q1_hi=q1_hi, peak=round(peak), f1_set=f1_set, km1=km1,
    p_coil=p_coil, i_coil_ma=round(i_coil * 1000))
