"""算例 55.7.1–55.7.2：表面强化（hub/surface.py）。
55.7.1：喷丸覆盖率 C = 1 − e^(−kt)（Avrami 型）：单位时间的覆盖常数 k 由“t₁ 时覆盖 90%”定出，求 98%（工程上的“全覆盖”）
        所需时间与 200% 覆盖率（全覆盖时间的 2 倍）；
55.7.2：强化前后的残余应力分布与 SH-101 轴承位的疲劳极限：正常磨削、喷丸、深滚压（压应力层深度、最大压应力）。
画图 55.7.5（几种强化的残余应力分布）、55.7.6（疲劳极限的提高）、55.7.4（喷丸覆盖率与时间）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
m20 = S.STEELS["20CrMnTi-CQ"]
t1 = 10.0                                   # 示意：试片 10 s 覆盖 90%
k = -math.log(1 - 0.90) / t1
t98 = -math.log(1 - 0.98) / k
t200 = 2 * t98
# 强化后的表面状态：Rz（喷丸使表面变粗，滚压使表面变光——示意倍数）与表层残余应力
x, z = S.turned_profile(0.05, 0.8, vc_m_min=200, noise_um=0.5)
rr = S.roughness(x, z)
rz_g = 0.8 * rr["Rz"] / rr["Ra"]
states = {"ground": (rz_g, T("正常磨削", "ground")), "shot_peened": (rz_g * 2.5, T("喷丸", "shot peened")),
          "rolled": (rz_g * 0.5, T("深滚压", "deep rolled"))}
fd = {k_: S.fatigue_limit(m20, rz, float(S.residual_stress(k_, np.array([0.0]))[0]))["sigma_D"] for k_, (rz, _) in states.items()}
gain_peen = (fd["shot_peened"] / fd["ground"] - 1) * 100
gain_roll = (fd["rolled"] / fd["ground"] - 1) * 100
def zero_cross(kind):
    """压应力层深度：残余应力由压变为零的深度（插值曲线上找）。"""
    zz_ = np.linspace(0, S.RESIDUAL[kind][-1][0], 4000)
    s_ = S.residual_stress(kind, zz_)
    i = int(np.argmax(s_ >= 0))
    return float(zz_[i])


depth = {k_: zero_cross(k_) for k_ in ("shot_peened", "rolled")}
peak = {k_: min(v for _, v in S.RESIDUAL[k_]) for k_ in ("shot_peened", "rolled")}

plt = style()
# ---- 图 55.7.5：强化前后的残余应力分布
fig, ax = plt.subplots(figsize=(6.0, 3.0))
zz = np.linspace(0, 1.6, 400)
for k_, c in (("ground", M.GREEN), ("shot_peened", M.ACCENT), ("rolled", "#6a4fa0")):
    zk = zz[zz <= S.RESIDUAL[k_][-1][0]]
    ax.plot(zk, S.residual_stress(k_, zk), color=c, lw=1.5, label=states[k_][1])
for k_, c in (("shot_peened", M.ACCENT), ("rolled", "#6a4fa0")):
    ax.annotate(T(f"压应力层约 {depth[k_]:.2f} mm", f"compressive layer ≈ {depth[k_]:.2f} mm"), (depth[k_], 0), (depth[k_] + 0.05, 180), fontsize=7, color=c,
                arrowprops={"arrowstyle": "->", "lw": 0.6, "color": c})
ax.axhline(0, color=M.INK, lw=0.6)
ax.set_xlabel(T("离表面的深度 / mm", "depth below the surface / mm")); ax.set_ylabel(T("轴向残余应力 / MPa", "axial residual stress / MPa"))
ax.set_ylim(-900, 350); ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="lower right")
figure(fig, "fig55_7_5")

# ---- 图 55.7.6：疲劳极限
fig, ax = plt.subplots(figsize=(5.4, 2.8))
keys = ["ground", "shot_peened", "rolled"]
ax.bar(range(3), [fd[k_] for k_ in keys], color=[M.GREEN, M.ACCENT, "#6a4fa0"], width=0.55)
for i, k_ in enumerate(keys):
    ax.text(i, fd[k_] + 8, f"{fd[k_]:.0f}", ha="center", fontsize=8)
ax.set_xticks(range(3)); ax.set_xticklabels([states[k_][1] for k_ in keys])
ax.set_ylabel(T("弯曲疲劳极限 σD / MPa", "bending fatigue limit σD / MPa")); ax.set_ylim(0, 750); ax.grid(lw=0.3, alpha=0.5, axis="y")
ax.set_title(T("SH-101 轴承位（20CrMnTi）：表面压应力抵消一部分外载", "SH-101 journal: surface compression offsets part of the load"), fontsize=8.5)
figure(fig, "fig55_7_6")

# ---- 图 55.7.4：喷丸覆盖率
fig, ax = plt.subplots(figsize=(5.6, 2.8))
ts = np.linspace(0, 50, 200)
ax.plot(ts, (1 - np.exp(-k * ts)) * 100, color=M.ACCENT, lw=1.5)
for t_, lab in ((t1, "90%"), (t98, T("98%（全覆盖）", "98% (full)"))):
    ax.plot(t_, (1 - math.exp(-k * t_)) * 100, "o", color=M.RED, ms=4)
    ax.text(t_ + 1, (1 - math.exp(-k * t_)) * 100 - 9, f"t = {t_:.0f} s：{lab}", fontsize=7.5, color=M.RED)
ax.axvline(t200, color=M.MUTED, ls="--", lw=0.8); ax.text(t200 + 0.6, 40, T(f"200% 覆盖率\n= {t200:.0f} s", f"200% coverage\n= {t200:.0f} s"), fontsize=7.5, color=M.MUTED)
ax.set_xlabel(T("喷丸时间 / s（示意）", "peening time / s (illustrative)")); ax.set_ylabel(T("覆盖率 / %", "coverage / %"))
ax.set_ylim(0, 105); ax.grid(lw=0.3, alpha=0.5)
ax.set_title(T("C = 1 − e^(−kt)：越接近 100% 越慢", "C = 1 − e^(−kt): the last few per cent are slow"), fontsize=8.5)
figure(fig, "fig55_7_4")

out(t1=t1, k=k, t98=t98, t200=t200, fd_g=fd["ground"], fd_p=fd["shot_peened"], fd_r=fd["rolled"], gain_peen=gain_peen, gain_roll=gain_roll,
    depth_p=depth["shot_peened"], depth_r=depth["rolled"], peak_p=peak["shot_peened"], peak_r=peak["rolled"])
