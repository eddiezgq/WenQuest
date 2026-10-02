"""6.7 节的计算：牛顿力学在什么情况下不够准。

算例 6.7.1  速度多大时，相对论修正 γ − 1 达到 1%；机器人、卫星、电子各是多少（图 6.7.1）；
算例 6.7.2  物质波的波长：搬运中的零件与原子中的电子。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import c, h, m_e
import _draw as d


def gamma_minus_1(v):
    b2 = (np.asarray(v, dtype=float) / c) ** 2
    return b2 / (np.sqrt(1 - b2) * (1 + np.sqrt(1 - b2)))     # = 1/√(1−β²) − 1，小速度时不损失精度


beta_1pct = math.sqrt(1 - 1 / 1.01 ** 2)
v_1pct = beta_1pct * c
v_tcp = 1.0                 # UR5e 末端的典型速度，m/s（厂家技术规格 “typical TCP speed 1 m/s”）
cases = {"tcp": v_tcp, "bullet": 900.0, "gps": 3874.0, "electron": 2.188e6}    # 弹头、GPS 卫星轨道速度、氢原子中电子（αc）
gm = {k: float(gamma_minus_1(v)) for k, v in cases.items()}
assert abs(gm["tcp"] - v_tcp ** 2 / (2 * c ** 2)) / gm["tcp"] < 1e-6

m_part, v_part = 2.0, 1.0
lam_part = h / (m_part * v_part)
lam_e = h / (m_e * cases["electron"])
day = 86400.0
dt_sr_us = gm["gps"] * day * 1e6        # 卫星钟因运动每天慢的微秒数（狭义相对论）

out(m_part=m_part, beta_1pct=beta_1pct, v_1pct=v_1pct, v_1pct_frac=v_1pct / c, v_tcp=v_tcp,
    gm_tcp=gm["tcp"], gm_bullet=gm["bullet"], gm_gps=gm["gps"], gm_e=gm["electron"],
    lam_part=lam_part, dt_sr_us=dt_sr_us, lam_e=lam_e, lam_e_nm=lam_e * 1e9)

plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.3))
v = np.logspace(0, math.log10(0.999 * c), 400)
ax.loglog(v, gamma_minus_1(v), color="#1d6fb8", lw=2)
ax.axhline(0.01, color=d.MUTED, ls="--", lw=1)
ax.text(1.5, 0.02, T("修正达 1%", "1 % correction"), fontsize=9, color=d.MUTED)
labels = {"tcp": T("UR5e 末端（典型）", "UR5e tool (typical)"), "bullet": T("步枪弹头", "rifle bullet"), "gps": T("GPS 卫星", "GPS satellite"),
          "electron": T("氢原子中的电子", "electron in hydrogen")}
for k, val in cases.items():
    ax.plot([val], [gm[k]], "o", color=d.FORCE, ms=5)
    ax.annotate(labels[k], (val, gm[k]), xytext=(6, 4), textcoords="offset points", fontsize=9, color=d.INK)
ax.set_xlabel(T("速度 $v$ / (m/s)", "speed $v$ / (m/s)")); ax.set_ylabel(r"$\gamma - 1$")
ax.set_xlim(1, c)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig6_7_1")
