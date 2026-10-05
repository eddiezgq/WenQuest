"""2.6 节：图 2.6.1（上料输送线控制柜的布置），控制柜的温升估算。

温升按柜体表面散热估算：ΔT = P / (k·A)，钢板柜 k ≈ 5.5 W/(m²·K)（IEC/TR 60890 一类方法的简化）；
靠墙安装的柜子背面不算散热面：A = W·H + 2·D·H + W·D。需要的风扇风量用厂商手册常见的经验式 V = 3.1·P/ΔT（m³/h，海平面）。"""
from bookout import figure, out, T, style
from _draw02 import _box, _l, frame, INK, MUTED, ACCENT, SOFT, LINE, WARM, GREEN

W, H, D = 0.6, 0.8, 0.3          # m
K = 5.5
A = W * H + 2 * D * H + W * D
loss = {"24 V 电源（5 A，效率 90 %）": 24 * 5 * 0.6 * (1 / 0.9 - 1), "PLC（第 3 章）": 8.0, "接触器线圈 ×3": 3 * 2.4,
        "主触点与热继电器 ×3": 3 * 2.0, "断路器与熔断器": 4.0, "端子与导线": 3.0}
P = sum(loss.values())
dT = P / (K * A)
T_amb = 35
P_vfd = 4000 * 0.03            # a 4 kW frequency converter loses about 3 % (Ch. 22)
dT2 = (P + P_vfd) / (K * A)
fan = 3.1 * (P + P_vfd) / 10    # m³/h to keep the rise at 10 K


def draw():
    plt = style()
    fig, ax = plt.subplots(figsize=(7.2, 8.2))
    _box(ax, 0, 0, 6.0, 8.0, "", fc="#f6f8fa", ec=INK, lw=1.6, r=0.05)
    ax.text(3.0, 8.15, T("安装板 600 × 800（柜深 300）", "mounting plate 600 × 800 (depth 300)"), ha="center", va="bottom", fontsize=9)
    for y in (7.2, 4.95, 2.7, 0.35):                                  # wiring ducts
        _box(ax, 0.25, y, 5.5, 0.45, "", fc="#d9dee2", ec=MUTED, lw=0.8, r=0.02)
    ax.text(5.9, 7.42, T("线槽", "duct"), ha="right", va="center", fontsize=7.6, color=MUTED)
    # row 1: incoming supply and protection
    row1 = [("Q0", T("总开关", "main switch"), 0.9), ("Q1", T("电动机\n断路器", "motor\nCB"), 0.6), ("Q2", T("备用", "spare"), 0.6), ("Q3", T("备用", "spare"), 0.6),
            ("F3", T("控制\n电路", "control"), 0.45), ("G1", T("24 V\n电源", "24 V\nPSU"), 1.0)]
    x = 0.35
    for name, sub, w in row1:
        _box(ax, x, 5.65, w, 1.3, "", fc="white", ec=INK)
        ax.text(x + w / 2, 6.62, name, ha="center", fontsize=8.6, family="monospace")
        if sub:
            ax.text(x + w / 2, 6.05, sub, ha="center", va="center", fontsize=7.2, color=MUTED, linespacing=1.0)
        x += w + 0.18
    # row 2: PLC and motor starters
    _box(ax, 0.35, 3.4, 1.9, 1.3, "", fc="white", ec=INK)
    ax.text(1.3, 4.35, "A1", ha="center", fontsize=8.6, family="monospace")
    ax.text(1.3, 3.85, T("PLC（第 3 章起）", "PLC (from Ch. 3)"), ha="center", fontsize=7.4, color=MUTED)
    # the conveyor's reversing starter (KM1 forward, KM2 reverse, one overload relay F1) and a spare starter
    for k, (name, x0) in enumerate((("KM1", 2.45), ("KM2", 3.2))):
        _box(ax, x0, 3.95, 0.55, 0.75, name, fc="white", ec=INK, fs=7.8)
    _box(ax, 2.45, 3.4, 1.3, 0.45, "F1", fc="white", ec=INK, fs=7.4)
    _box(ax, 4.2, 3.4, 1.3, 1.3, T("备用", "spare"), fc="white", ec=MUTED, fs=7.6, color=MUTED)
    ax.text(3.1, 3.24, T("输送线正反转：KM1、KM2、F1", "conveyor reversing: KM1, KM2, F1"), ha="center", fontsize=7.0, color=MUTED)
    # row 3: terminals and PE bar
    _box(ax, 0.35, 1.0, 4.2, 0.9, "", fc="white", ec=INK)
    for k in range(18):
        _l(ax, [0.5 + k * 0.22] * 2, [1.05, 1.85], color=LINE, lw=0.8)
    ax.text(2.45, 2.05, T("端子排 X1（现场电缆从这里进出）", "terminal strip X1 (field cables)"), ha="center", fontsize=7.6, color=MUTED)
    _box(ax, 4.75, 1.0, 0.95, 0.9, "PE", fc="#e7f3e9", ec=GREEN, fs=8.6, color=GREEN)
    ax.text(5.22, 2.05, T("保护接地排", "PE bar"), ha="center", fontsize=7.6, color=MUTED)
    for x0 in (0.8, 2.0, 3.2, 4.4):
        _box(ax, x0, -0.35, 0.5, 0.3, "", fc="#c9d2d8", ec=MUTED, r=0.1)
    ax.text(3.0, -0.5, T("底部电缆入口（格兰头）", "cable glands at the bottom"), ha="center", va="top", fontsize=7.6, color=MUTED)
    ax.annotate(T("发热大的器件放上面，\n热往上走", "hot devices at the top;\nheat rises"), xy=(5.4, 6.3), xytext=(6.3, 7.0), fontsize=7.8, color=WARM,
                arrowprops=dict(arrowstyle="-", color=WARM, lw=0.8))
    ax.annotate(T("主电路和控制电路\n分开走线", "power and control\nwiring kept apart"), xy=(5.6, 5.15), xytext=(6.3, 5.2), fontsize=7.8, color=ACCENT,
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    frame(ax, (-0.3, 8.4), (-1.0, 8.6))
    return fig


figure(draw(), "fig2_6_1")
out(A=round(A, 2), P=round(P), dT=round(dT, 1), T_in=round(T_amb + dT), P_vfd=round(P_vfd), dT2=round(dT2), T_in2=round(T_amb + dT2), fan=round(fan),
    loss_psu=round(loss["24 V 电源（5 A，效率 90 %）"], 1))
