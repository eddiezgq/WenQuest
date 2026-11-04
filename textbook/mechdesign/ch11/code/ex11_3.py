"""11.4 平均应力的影响：古德曼、格伯、SWT、索德伯格；海格图。

算例 11.4.1  同一组 (σa, σm) 换算成对称循环的等效应力幅 σa,eq，四种修正比较：
            古德曼 σa/(1 − σm/R_m)；格伯 σa/(1 − (σm/R_m)²)；索德伯格 σa/(1 − σm/σs)；SWT √(σmax·σa)。
            (1) WQ-CR5 大臂 J2 端（根部）法兰内角：标准动作一个节拍里最大主应力最大的那个点（重力使它一直受拉），
                雨流计数（数字工厂 fatigue.rainflow）得到最大一个循环的 σa、σm——平均应力是应力幅的几倍；
            (2) RJ-201 输出轴花键段（第 33 章，40Cr 调质）：谐波减速器启停允许峰值转矩 T_repeat 的起停循环 0 → T → 0（R = 0），
                冯·米塞斯当量应力 √3·τ，σa = σm = σmax/2。
            (3) 平均应力很大的情形（第 17 章螺栓的预告）：40Cr 调质，σm = 0.6 σs（预紧），σa = 40 MPa（本书取值）。
            都画在各自材料的海格图上；数字工厂的疲劳程序用的是古德曼（且取 |σm|，受压的平均应力也当作有害）；
图 11.4.1。
"""
import math

import numpy as np

import _ch11 as H
import _rj as RJ
from bookout import T, figure, out, style


def allow(sm, m):
    """平均应力不变时允许的应力幅（海格图上该 σm 处各条线的高度）"""
    s1, Rm, sy = m["sigma_1"], m["ultimate_mpa"], m["yield_mpa"]
    return {"goodman": s1 * (1 - sm / Rm), "gerber": s1 * (1 - (sm / Rm) ** 2), "soderberg": s1 * (1 - sm / sy),
            "swt": (-sm + math.sqrt(sm * sm + 4 * s1 * s1)) / 2}


def corr(sa, sm, m):
    Rm, sy = m["ultimate_mpa"], m["yield_mpa"]
    return {"goodman": sa / (1 - sm / Rm), "gerber": sa / (1 - (sm / Rm) ** 2), "soderberg": sa / (1 - sm / sy),
            "swt": math.sqrt(max(sm + sa, 0.0) * sa)}


# (1) 大臂根部
R = H.heavy()
F = H.field(R["U"]["J2"], R["L6"], R["L0"])
i = int(np.argmax(F["s1"].mean(axis=1)))
cyc = H.FT.rainflow(F["s1"][i])
j = int(np.argmax(cyc[:, 0]))
sa1, sm1 = float(cyc[j, 0]), float(cyc[j, 1])
al = H.AL
c1 = corr(sa1, sm1, al)

# (2) RJ-201 花键段
st = H.mat("40Cr-QT")
hd = RJ.harmonic("25-100")
D_ie = RJ.spline(RJ.SEAT)["D_ie"]
tau = hd["repeat"] * 1e3 / (2 * RJ.W_hollow(D_ie))
smax2 = math.sqrt(3) * tau
sa2 = sm2 = smax2 / 2
c2 = corr(sa2, sm2, st)

# (3) 高平均应力
sm3, sa3 = 0.6 * st["yield_mpa"], 40.0
c3 = corr(sa3, sm3, st)

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.1))
for ax, m, pts, ttl in ((axs[0], al, [((sm1, sa1), T("大臂根部内角", "arm root corner"))],
                         T("(a) 6061-T6", "(a) 6061-T6")),
                        (axs[1], st, [((sm2, sa2), T("RJ-201 花键（R = 0）", "RJ-201 spline (R = 0)")),
                                      ((sm3, sa3), T("高预紧（σm = 0.6σs）", "high preload (σm = 0.6σs)"))],
                         T("(b) 40Cr 调质", "(b) 40Cr Q&T"))):
    s1, Rm, sy = m["sigma_1"], m["ultimate_mpa"], m["yield_mpa"]
    x = np.linspace(0, Rm, 300)
    ax.plot(x, s1 * (1 - x / Rm), color="#d62728", lw=1.2, label=T("古德曼", "Goodman"))
    ax.plot(x, s1 * (1 - (x / Rm) ** 2), color="#2ca02c", lw=1.2, label=T("格伯", "Gerber"))
    xs = np.linspace(0, sy, 200)
    ax.plot(xs, s1 * (1 - xs / sy), color="#1f77b4", lw=1.0, ls="--", label=T("索德伯格", "Soderberg"))
    xl = np.linspace(0, sy, 50)
    ax.plot(xl, sy - xl, color=H.MUTED, lw=0.8, ls=":", label=T("屈服 σa + σm = σs", "yield σa + σm = σs"))
    xx = np.linspace(1, Rm, 300)
    sw = []
    for xm in xx:                                    # SWT：√((σm + σa)·σa) = σ₋₁ 的曲线
        sw.append((-xm + math.sqrt(xm * xm + 4 * s1 * s1)) / 2)
    ax.plot(xx, sw, color="#9467bd", lw=1.0, label="SWT")
    for pt, lab in pts:
        ax.plot([pt[0]], [pt[1]], "o", color=H.INK, ms=4)
        ax.annotate(lab, pt, textcoords="offset points", xytext=(5, 5), fontsize=6.0)
    ax.set_xlim(0, Rm * 1.02)
    ax.set_ylim(0, s1 * 1.15)
    ax.set_xlabel(T("平均应力 σm / MPa", "Mean stress σm / MPa"), fontsize=7.0)
    ax.set_ylabel(T("应力幅 σa / MPa", "Stress amplitude σa / MPa"), fontsize=7.0)
    ax.tick_params(labelsize=6.2)
    ax.legend(fontsize=5.6, frameon=False, loc="upper right")
    ax.set_title(ttl, fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_4_1")

v = dict(sa1=sa1, sm1=sm1, r1=(sm1 - sa1) / (sm1 + sa1), ratio1=sm1 / sa1, th1=math.degrees(F["theta"][i]), ph1=F["phi"][i],
         T_rep=hd["repeat"], D_ie=D_ie, tau=tau, smax2=smax2, sa2=sa2, s1_al=al["sigma_1"], Rm_al=al["ultimate_mpa"],
         s1_st=st["sigma_1"], Rm_st=st["ultimate_mpa"], sy_st=st["yield_mpa"], sy_al=al["yield_mpa"])
v.update(sm3=sm3, sa3=sa3)
for tag, c, sa in (("1", c1, sa1), ("2", c2, sa2), ("3", c3, sa3)):
    for k, x in c.items():
        v[f"{k}{tag}"] = x
        v[f"{k}{tag}_pct"] = (x / sa - 1) * 100
for tag, sm, sa, m in (("2", sm2, sa2, st), ("3", sm3, sa3, st)):
    for k, x in allow(sm, m).items():
        v[f"Sm_{k}{tag}"] = x / sa                    # 平均应力不变、应力幅放大到海格图上那条线的倍数
out(**v)
