"""1.2 节的计算：

算例 1.2.1  舵机手册写“堵转扭矩 20 kgf·cm”，关节手册写“最大角速度 180 °/s”：换算成国际单位。
算例 1.2.2  火星气候探测者号（1999）：地面软件按 lbf·s 输出推进器冲量，导航软件按 N·s 读入。读数偏小多少倍？
算例 1.2.3  2019 年起千克由普朗克常量定义：铯 133 超精细跃迁的一个光子能量 hΔν_Cs 是多少焦耳、多少电子伏特。
图 1.2.1    七个定义常数与七个基本单位。
"""
import math

from bookout import T, figure, out, style
from constants import c, h, e, k, N_A, dnu_Cs, g_n
import _draw as d

# ---- 算例 1.2.1
tau_kgfcm = 20.0
tau_Nm = tau_kgfcm * g_n * 0.01                 # 1 kgf = 9.806 65 N（标准重力加速度，定义值）
w_deg = 180.0
w_rad = math.radians(w_deg)

# ---- 算例 1.2.2
lbf = 0.453_592_37 * g_n                        # 1 lbf = 0.453 592 37 kg × g_n（定义值）
# ---- 算例 1.2.3
E_Cs = h * dnu_Cs
E_Cs_eV = E_Cs / e
lam_Cs_cm = c / dnu_Cs * 100

def sci(x, digits):
    """把精确常数写成“有效数字三位一组、× 10 的幂”的形式（GB/T 3101 的数字分组）。"""
    m, ex = f"{x:.{digits - 1}e}".split("e")
    ip, fp = m.split(".")
    fp = " ".join(fp[i:i + 3] for i in range(0, len(fp), 3))
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return f"{ip}.{fp} × 10{str(int(ex)).translate(sup)}"


assert c == 299_792_458 and dnu_Cs == 9_192_631_770 and g_n == 9.806_65
out(cal_str="4.184", gn_str="9.806 65", lb_str="0.453 592 37", oz_str="28.349 523 125", c_str="299 792 458", dnu_str="9 192 631 770", h_str=sci(h, 9), e_str=sci(e, 10), k_str=sci(k, 7), NA_str=sci(N_A, 9), Kcd_str="683")
assert sci(h, 9) == "6.626 070 15 × 10⁻³⁴" and sci(e, 10) == "1.602 176 634 × 10⁻¹⁹"
out(tau_kgfcm=tau_kgfcm, tau_Nm=tau_Nm, w_deg=w_deg, w_rad=w_rad, lbf=lbf, E_Cs=E_Cs, E_Cs_eV=E_Cs_eV,
    lam_Cs_cm=lam_Cs_cm, dnu_Cs=dnu_Cs)

plt = style()
fig, ax = plt.subplots(figsize=(6.4, 3.6))
consts = [("$\\Delta\\nu_\\mathrm{Cs}$", "s"), ("$c$", "m"), ("$h$", "kg"), ("$e$", "A"), ("$k$", "K"), ("$N_\\mathrm{A}$", "mol"), ("$K_\\mathrm{cd}$", "cd")]
names = [T("时间", "time"), T("长度", "length"), T("质量", "mass"), T("电流", "current"), T("温度", "temperature"),
         T("物质的量", "amount"), T("发光强度", "luminous intensity")]
for i, ((cs, unit), nm) in enumerate(zip(consts, names)):
    a = math.pi / 2 - 2 * math.pi * i / 7
    xo, yo = 1.45 * math.cos(a), 1.45 * math.sin(a)
    xi, yi = 0.78 * math.cos(a), 0.78 * math.sin(a)
    ax.add_patch(plt.Circle((xo, yo), 0.3, fc="#eaf2fb", ec=d.DATA, lw=1.5))
    ax.text(xo, yo, cs, ha="center", va="center", fontsize=12, color=d.DATA)
    ax.add_patch(plt.Circle((xi, yi), 0.25, fc="#fbeaea", ec=d.FIT, lw=1.5))
    ax.text(xi, yi, unit, ha="center", va="center", fontsize=11, color=d.FIT)
    ax.annotate("", xy=(1.02 * math.cos(a), 1.02 * math.sin(a)), xytext=(1.16 * math.cos(a), 1.16 * math.sin(a)),
                arrowprops=dict(arrowstyle="-|>", color=d.MUTED, lw=1.2, mutation_scale=9))
    cx = math.cos(a)
    ax.text(1.45 * math.cos(a) + (0.38 if cx > 0.3 else -0.38 if cx < -0.3 else 0), 1.45 * math.sin(a) + (0 if abs(cx) > 0.3 else 0.42 * math.copysign(1, math.sin(a))),
            nm, ha="left" if cx > 0.3 else "right" if cx < -0.3 else "center", va="center", fontsize=9, color=d.INK)
ax.text(0, 0, "SI", ha="center", va="center", fontsize=16, color=d.INK, weight="bold")
ax.text(-3.4, 1.9, T("外圈：定义常数（精确值）", "outer ring: defining constants (exact)"), fontsize=9, color=d.DATA)
ax.text(-3.4, 1.6, T("内圈：基本单位", "inner ring: base units"), fontsize=9, color=d.FIT)
ax.set_xlim(-3.5, 3.5); ax.set_ylim(-2.3, 2.3); ax.set_aspect("equal"); d.clean(ax)
figure(fig, "fig1_2_1")
