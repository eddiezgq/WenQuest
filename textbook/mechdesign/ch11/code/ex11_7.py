"""11.8 疲劳裂纹扩展：WQ-CR5 大臂根部内角的表面裂纹。

算例 11.8.1  应力取 11.6 节的最危险点、最危险的面（J2 端法兰内角，标准动作一个节拍里最大的一个循环）：Δσ = σmax − σmin，R = σmin/σmax。
            表面浅裂纹 ΔK = Y·Δσ·√(πa)，Y = 1.12（第 10 章 10.5 节）。帕里斯公式 da/dN = C·ΔK^m，取铝合金的代表值
            C = 1.42 × 10⁻¹¹ m/循环（ΔK 以 MPa·√m 计）、m = 3.59（[DOW] 中 2024-T3 的值，6061-T6 同一量级；本书取值），
            门槛值 ΔK_th = 1.0 MPa·√m（铝合金在 R ≈ 0.1–0.5 时约 1–3 MPa·√m，本书偏安全取下限）。
            (1) 实际载荷：0.5 mm 深的裂纹（目视、渗透检测大致能发现的尺寸）的 ΔK 与门槛值比较；裂纹要多深才会扩展；
            (2) 载荷放大 λ 倍（λ 取 11.6 节“5 年刚好用完”的值）：裂纹从 0.5 mm 长到穿透壁厚（3 mm）要多少个节拍、多少年
            （Y 按浅裂纹不变，深裂纹时实际偏大，结果偏乐观）；与“萌生寿命”5 年比较；穿透前会不会先断（K_max 与 K_IC = 29 MPa·√m）；
            检修周期按扩展寿命的一半；
图 11.8.1。
"""
import math

import numpy as np

import _ch11 as H
from bookout import T, figure, out, style

R = H.heavy()
t, L6, L0 = R["t"], R["L6"], R["L0"]
TCYC = float(t[-1])
U = R["U"]["J2"]
F = H.field(U, L6, L0)
_, _, _, sn = H.critical_plane(U, F, "J2")
N_LIFE = H.cycles_per_life(TCYC)
lam = H.lam_for_life(lambda x: x * sn, N_LIFE)

smax, smin = float(sn.max()), float(sn.min())
dsig = smax - smin
Rr = smin / smax
Y, C, M_, DKTH, KIC = 1.12, 1.42e-11, 3.59, 1.0, 29.0
A0, WALL = 0.5e-3, 3.0e-3
dk = lambda ds, a: Y * ds * math.sqrt(math.pi * a)          # noqa: E731
dk0 = dk(dsig, A0)
a_th = (DKTH / (Y * dsig)) ** 2 / math.pi


def grow(ds, a0, a1, n=4000):
    """从 a0 长到 a1 的循环数（低于门槛值的那一段不扩展：返回 inf）"""
    a = np.geomspace(a0, a1, n)
    k = Y * ds * np.sqrt(np.pi * a)
    if k[0] < DKTH:
        return math.inf
    rate = C * k ** M_
    return float(np.trapezoid(1 / rate, a))


N_grow_lam = grow(lam * dsig, A0, WALL)
yrs_grow = N_grow_lam * TCYC / 3600 / (H.SHIFT_H * H.DAYS)
a_th_lam = (DKTH / (Y * lam * dsig)) ** 2 / math.pi
Kmax_wall = Y * lam * smax * math.sqrt(math.pi * WALL)
a_c = (KIC / (Y * lam * smax)) ** 2 / math.pi
N_grow1 = grow(dsig, max(a_th, A0) * 1.0001, WALL) if a_th < WALL else math.inf

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
aa = np.geomspace(0.05e-3, 3e-3, 200)
a0.loglog(aa * 1e3, Y * dsig * np.sqrt(np.pi * aa), color="#1f77b4", lw=1.3, label=T("实际载荷", "actual load"))
a0.loglog(aa * 1e3, Y * lam * dsig * np.sqrt(np.pi * aa), color="#d62728", lw=1.3, label=T("载荷 × {:.1f}".format(lam), "load × {:.1f}".format(lam)))
a0.axhline(DKTH, color=H.INK, lw=0.9, ls="--")
a0.text(0.06, DKTH * 1.12, T("门槛值 ΔK_th", "threshold ΔK_th"), fontsize=6.3)
a0.axvline(A0 * 1e3, color=H.MUTED, lw=0.8, ls=":")
a0.text(A0 * 1e3 * 1.06, 0.12, T("可检出 0.5 mm", "detectable 0.5 mm"), fontsize=6.0, color=H.MUTED, rotation=90, va="bottom")
a0.axvline(WALL * 1e3, color=H.MUTED, lw=0.8, ls=":")
a0.text(WALL * 1e3 * 0.88, 0.12, T("壁厚", "wall"), fontsize=6.0, color=H.MUTED, rotation=90, va="bottom")
a0.set_ylim(0.08, 40)
a0.set_xlabel(T("裂纹深度 a / mm", "Crack depth a / mm"), fontsize=7.0)
a0.set_ylabel(T("ΔK / MPa·√m", "ΔK / MPa·√m"), fontsize=7.0)
a0.legend(fontsize=6.0, frameon=False, loc="upper left")
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 应力强度因子变程", "(a) Stress-intensity range"), fontsize=7.0)
# 载荷放大后的裂纹长大曲线
a = np.geomspace(A0, WALL, 400)
k = Y * lam * dsig * np.sqrt(np.pi * a)
N_a = np.concatenate([[0.0], np.cumsum(np.diff(a) / (C * (0.5 * (k[1:] + k[:-1])) ** M_))])
a1.plot(N_a * TCYC / 3600 / (H.SHIFT_H * H.DAYS), a * 1e3, color="#d62728", lw=1.3)
a1.axhline(WALL * 1e3, color=H.MUTED, lw=0.8, ls=":")
a1.set_xlabel(T("时间 / 年（两班，每年 250 天）", "Time / years (two shifts, 250 days)"), fontsize=7.0)
a1.set_ylabel(T("裂纹深度 a / mm", "Crack depth a / mm"), fontsize=7.0)
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 载荷 × {:.1f}：从 0.5 mm 到穿透壁厚".format(lam), "(b) Load × {:.1f}: from 0.5 mm to through-wall".format(lam)), fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_8_1")

out(smax=smax, smin=smin, dsig=dsig, R=Rr, Y=Y, C=C * 1e11, m=M_, dkth=DKTH, KIC=KIC, a0=A0 * 1e3, wall=WALL * 1e3,
    dk0=dk0, a_th=a_th * 1e3, lam=lam, N_grow=N_grow_lam, yrs_grow=yrs_grow, yrs_insp=yrs_grow / 2,
    a_th_lam=a_th_lam * 1e3, dk0_lam=dk(lam * dsig, A0), Kmax_wall=Kmax_wall, a_c=a_c * 1e3,
    grow_wall_finite=math.isfinite(N_grow1), N_grow1=N_grow1 if math.isfinite(N_grow1) else 0.0,
    yrs_grow1=(N_grow1 * TCYC / 3600 / (H.SHIFT_H * H.DAYS)) if math.isfinite(N_grow1) else 0.0, share=yrs_grow / H.YEARS * 100)
