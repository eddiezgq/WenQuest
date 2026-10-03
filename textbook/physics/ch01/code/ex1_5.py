"""1.5 节的计算：

算例 1.5.1  用游标卡尺（分度值 0.02 mm，最大允许误差 ±0.03 mm）在 10 个不同位置测铝合金转接盘的外径：
            平均值、实验标准差、A 类与 B 类标准不确定度、合成与扩展不确定度（k = 2）。读数由程序按固定种子生成。
算例 1.5.2  用螺旋测微器（分度值 0.01 mm，估读到 0.001 mm，最大允许误差 ±0.004 mm）测厚度 5 次，同样处理。
算例 1.5.3  再测中心孔、4 个通孔的直径与质量，算出转接盘的密度及其不确定度（不确定度传递，灵敏系数用数值偏导），
            判断材料；用蒙特卡罗法核对（各分量按各自的分布抽样：A 类取正态，最大允许误差与舍入取均匀分布）。
图 1.5.1    准确度与精密度；图 1.5.2  外径的 10 次读数。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

rng = np.random.default_rng(15)


def rnd(x, step):
    return np.round(np.asarray(x) / step) * step


# ---- 算例 1.5.1：外径（卡尺）
D_true, n_D = 62.96, 10
D = rnd(D_true + 0.012 * rng.standard_normal(n_D), 0.02)       # 转接盘略不圆，各位置略有不同
D_mean, s_D = D.mean(), D.std(ddof=1)
uA_D = s_D / math.sqrt(n_D)
uB_D = 0.03 / math.sqrt(3)                                      # 均匀分布
uc_D = math.hypot(uA_D, uB_D)

# ---- 算例 1.5.2：厚度（螺旋测微器）
h_true, n_h = 8.012, 5
h = rnd(h_true + 0.002 * rng.standard_normal(n_h), 0.001)
h_mean, s_h = h.mean(), h.std(ddof=1)
uA_h = s_h / math.sqrt(n_h)
uB_h = 0.004 / math.sqrt(3)
uc_h = math.hypot(uA_h, uB_h)

# ---- 算例 1.5.3：中心孔（卡尺内量爪，单次）、4 个通孔（各量一次取平均）、质量（天平）
# 单次读数的重复性借用算例 1.5.1 的实验标准差 s_D（同一把卡尺、同一个人，JJF 1059.1 允许这样做）
d_in = 31.52
u_din = math.sqrt(s_D ** 2 + 0.02 ** 2 / 12 + 0.03 ** 2 / 3)      # 重复性 + 读数舍入 + 最大允许误差
d_h, n_holes = 6.62, 4
u_dh = math.sqrt((s_D ** 2 + 0.02 ** 2 / 12) / n_holes + 0.03 ** 2 / 3)   # 4 次的平均；卡尺的误差对 4 次相同，不因平均而减小
m = 47.55                                                      # g
u_m = 0.02 / math.sqrt(3)                                      # 天平最大允许误差 ±0.02 g


def rho(Dm, dm, hm, mm, dhm=d_h):
    V = math.pi / 4 * (Dm ** 2 - dm ** 2 - n_holes * dhm ** 2) * hm / 1000    # cm³
    return mm / V


rho0 = rho(D_mean, d_in, h_mean, m)
# 不确定度传递：各输入量的灵敏系数用数值偏导
parts, sens = {}, {}
for name, (x, u) in {"D": (D_mean, uc_D), "d": (d_in, u_din), "h": (h_mean, uc_h), "m": (m, u_m), "dh": (d_h, u_dh)}.items():
    args = {"Dm": D_mean, "dm": d_in, "hm": h_mean, "mm": m, "dhm": d_h}
    key = {"D": "Dm", "d": "dm", "h": "hm", "m": "mm", "dh": "dhm"}[name]
    dx = 1e-6 * x
    args[key] = x + dx
    cs = (rho(**args) - rho0) / dx                                 # 灵敏系数 ∂ρ/∂x
    sens[name] = cs
    parts[name] = cs * u
uc_rho = math.sqrt(sum(v * v for v in parts.values()))
U_rho = 2 * uc_rho
# 蒙特卡罗核对（10⁵ 次抽样）
N = 100_000
U_ = lambda a: rng.uniform(-a, a, N)
Dmc = D_mean + rng.normal(0, uA_D, N) + U_(0.03)
dmc = d_in + rng.normal(0, s_D, N) + U_(0.01) + U_(0.03)
hmc = h_mean + rng.normal(0, uA_h, N) + U_(0.004)
mmc = m + U_(0.02)
dhmc = d_h + rng.normal(0, math.sqrt((s_D ** 2 + 0.02 ** 2 / 12) / n_holes), N) + U_(0.03)
mc = rho(Dmc, dmc, hmc, mmc, dhmc)
assert abs(mc.std() - uc_rho) < 0.05 * uc_rho
share = {k: 100 * v * v / uc_rho ** 2 for k, v in parts.items()}
sens_ratio = abs(sens["D"] / sens["d"])                        # 外径与中心孔的灵敏系数之比（≈ D/d）

out(D_list=", ".join(f"{x:.2f}" for x in D), D_mean=D_mean, s_D=s_D, uA_D=uA_D, uB_D=uB_D, uc_D=uc_D, U_D=2 * uc_D,
    h_list=", ".join(f"{x:.3f}" for x in h), h_mean=h_mean, s_h=s_h, uA_h=uA_h, uB_h=uB_h, uc_h=uc_h, U_h=2 * uc_h,
    d_in=d_in, u_din=u_din, m=m, u_m=u_m, rho=rho0, uc_rho=uc_rho, U_rho=U_rho, mc_std=float(mc.std()),
    sh_D=share["D"], sh_d=share["d"], sh_h=share["h"], sh_m=share["m"], sh_dh=share["dh"], rel_rho=100 * uc_rho / rho0,
    d_h=d_h, u_dh=u_dh, sens_ratio=sens_ratio)

# 正文与习题中给定的数据（程序给出，保证与上面的计算一致）
D_nom, D_lo = 63.00, 62.95                                   # 图样：外径 63.00 mm，公差 −0.05～0
D_r, U_r = round(D_mean, 2), round(2 * uc_D, 2)              # 修约后的结果 (62.96 ± 0.04) mm
lo, hi = D_r - U_r, D_r + U_r
assert lo < D_lo < hi                                        # 测得区间与公差带下限重叠
t20_ex = [39.38, 39.45, 39.30, 39.41, 39.36]                 # 习题 1.5.3
out(D_nom=f"{D_nom:.2f}", D_lo=f"{D_lo:.2f}", first3="、".join(f"{x:.2f} mm" for x in (D[0], D[1], D[7])),
    lo=f"{lo:.2f}", hi=f"{hi:.2f}", rd1=f"{D[2]:.2f}", rd1x=f"{D[2]:.3f}", gex="9.7893", t20_ex="、".join(f"{x:.2f} s" for x in t20_ex),
    Dex=f"{D_nom:.2f}", dex="62.00")

# GB/T 8170 修约：四舍六入五成双（用十进制精确运算，避免二进制浮点的 2.675 问题）
from decimal import Decimal, ROUND_HALF_EVEN
def gb8170(x, q):
    return str(Decimal(x).quantize(Decimal(q), rounding=ROUND_HALF_EVEN))
rd_cases = ["2.7036", "2.7051", "2.6950"]
assert [gb8170(x, "0.01") for x in rd_cases] == ["2.70", "2.71", "2.70"]
out(rd_ex="，".join(f"{x} 修约为 {gb8170(x, '0.01')}" for x in rd_cases),
    rd_hw="、".join(["2.345", "2.355", "2.3451"]), g_std="9.789", ug_std="0.018")

plt = style()
# ---- 图 1.5.1：准确度与精密度
fig, axs = plt.subplots(1, 4, figsize=(7.6, 2.2))
cases = [(0, 0, 0.12, T("准确且精密", "accurate, precise")), (0.55, 0.35, 0.12, T("精密但不准确", "precise, not accurate")),
         (0, 0, 0.33, T("准确但不精密", "accurate, not precise")), (0.4, -0.3, 0.3, T("都不好", "neither"))]
r2 = np.random.default_rng(3)
for ax, (bx, by, s, lab) in zip(axs, cases):
    for r, col in ((1.0, "#f2f2f2"), (0.66, "#e3e9e7"), (0.33, "#d0d8d5")):
        ax.add_patch(plt.Circle((0, 0), r, fc=col, ec=d.MUTED, lw=0.6))
    p = r2.normal(0, s, (12, 2)) + [bx, by]
    ax.plot(p[:, 0], p[:, 1], "o", color=d.DATA, ms=4)
    ax.set_title(lab, fontsize=9); ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1); ax.set_aspect("equal"); d.clean(ax)
figure(fig, "fig1_5_1")

# ---- 图 1.5.2：外径读数
fig, ax = plt.subplots(figsize=(5.0, 2.6))
ax.plot(np.arange(1, n_D + 1), D, "o", color=d.DATA)
ax.axhline(D_mean, color=d.FIT, lw=1.5)
ax.axhspan(D_mean - s_D, D_mean + s_D, color=d.FIT, alpha=0.12)
ax.text(10.3, D_mean, T("平均值", "mean"), va="center", fontsize=9, color=d.FIT)
ax.text(10.3, D_mean + s_D, "$+s$", va="center", fontsize=9, color=d.FIT)
ax.set_xlabel(T("测量序号", "reading no."), fontsize=10); ax.set_ylabel(T("外径读数 / mm", "diameter reading / mm"))
ax.set_xticks(range(1, 11)); ax.set_xlim(0.5, 11.5); d.spines(ax)
figure(fig, "fig1_5_2")
