"""11.9 FKM 准则与工程疲劳评定：WQ-CR5 大臂根部内角（局部应力法），以及焊接法兰的对照（IIW 名义应力法）。

算例 11.9.1  FKM 局部应力法的流程（FKM 指南第 7 版的主要步骤，本例用到的部分；系数取值见各行注释）：
            ① 材料：对称拉压疲劳强度 σ_W,zd = f_W·R_m，变形铝合金 f_W = 0.30；R_m 取 ASTM B221 规定的最低值 260 MPa（设计值，
               材料库的 310 MPa 是典型值）；
            ② 构件：设计系数 K_WK = (1/n_σ)·[1 + (1/K̃_f)(1/K_R − 1)]·1/(K_V·K_S)：支撑系数 n_σ 由相对应力梯度 G ≈ 2/r 按 FKM 公式
               （变形铝合金 a_G = 0.05、b_G = 850 MPa）；K̃_f = 2；K_R 按粗糙度公式（R_z = 6.3 μm）；K_V = 1；阳极氧化 K_S 本书取 0.8；
            ③ 平均应力：M_σ = a_M·10⁻³·R_m + b_M（变形铝合金 a_M = 1.0、b_M = −0.04），按 R 所在的区间求 K_AK；
            ④ 循环次数：本例每个节拍只有一个大循环（11.6 节），按等幅计；铝合金没有疲劳极限，FKM 取拐点 N_D = 10⁶、之后斜率 15
               继续下降（本书按此取；正式评定以规范原文为准），5 年 N 次时 K_BK = (N_D/N)^(1/15)；
            ⑤ 安全系数 j_D = 1.5（FKM：后果严重、不定期检查）；利用度 a = σa / (σ_AK / j_D) ≤ 1。
            应力取 11.6 节临界平面上的最大一个循环；与 11.6 节按数字工厂程序得到的安全系数对照；
算例 11.9.2  对照：如果大臂改成铝管与法兰焊接（角焊缝，焊趾在管上），按 IIW 推荐的名义应力法：铝合金管–板角焊缝取
            FAT 25（2×10⁶ 次的应力变程 MPa，斜率 m = 3，1×10⁷ 次以后 m = 22，IIW 2016；本书按 IIW 的分类取值），
            名义应力 = 根部截面的弯曲 + 轴力（梁理论，一个节拍里圆周上变程最大的那一点；扭转切应力很小，未计），
            γ_M = 1.30（IIW：安全寿命设计、后果严重）；
            与整体机加工的方案比较“载荷还能放大多少倍”；
图 11.9.1。
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
cyc = H.FT.rainflow(sn)
j = int(np.argmax(cyc[:, 0]))
sa, sm = float(cyc[j, 0]), float(cyc[j, 1])
Rr = (sm - sa) / (sm + sa)
_, s_fac = H.damage(sn)

# ① 材料
RM_MIN, F_W = 260.0, 0.30
s_wzd = F_W * RM_MIN
# ② 构件
r = H.FIL
G = 2 / r                                                 # 1/mm
A_G, B_G = 0.05, 850.0
if G <= 0.1:
    n_s = 1 + G * 10 ** -(A_G - 0.5 + RM_MIN / B_G)
elif G <= 1.0:
    n_s = 1 + math.sqrt(G) * 10 ** -(A_G + RM_MIN / B_G)
else:
    n_s = 1 + G ** 0.25 * 10 ** -(A_G + RM_MIN / B_G)
RZ = 6.3
K_R = 1 - 0.22 * math.log10(RZ) * math.log10(2 * RM_MIN / 133)
KF_T, K_V, K_S = 2.0, 1.0, 0.8
K_WK = (1 / n_s) * (1 + (1 / KF_T) * (1 / K_R - 1)) / (K_V * K_S)
s_wk = s_wzd / K_WK
# ③ 平均应力
M_s = 1.0e-3 * RM_MIN - 0.04
if Rr > 1:
    K_AK, region = 1 / (1 - M_s), "I"
elif Rr <= 0:
    K_AK, region = 1 / (1 + M_s * sm / sa), "II"
elif Rr < 0.5:
    K_AK, region = (1 + M_s / 3) / (1 + M_s) / (1 + M_s / 3 * sm / sa), "III"
else:
    K_AK, region = (3 + M_s) / (3 * (1 + M_s) ** 2), "IV"
s_ak = K_AK * s_wk
N_LIFE = H.cycles_per_life(TCYC)
ND_FKM, KD_FKM = 1e6, 15.0
K_BK, J_D = (ND_FKM / N_LIFE) ** (1 / KD_FKM), 1.5
s_bk = K_BK * s_ak
util = sa / (s_bk / J_D)
S_fkm = s_bk / sa

# ---------------------------------------------------------------- 算例 11.9.2 焊接法兰
p = H.SP.params_of("wqcr5_upper", None)
D, d, L = p["D"], p["D"] - 2 * p["t"], p["L"]
Wb = math.pi * (D ** 4 - d ** 4) / (32 * D)
Aa = math.pi * (D ** 2 - d ** 2) / 4
Fv, Mv = L6[:3], L6[3:] * 1e3                              # N、N·mm
Mroot = Mv + np.cross(np.array([0.0, 0.0, L]), Fv.T).T      # 根部截面的弯矩（J3 端的载荷移到根部）
best = (0.0, 0.0)
for th in np.radians(np.arange(0, 360, 5)):
    y, x = math.sin(th) * D / 2, math.cos(th) * D / 2
    I = Wb * D / 2
    sig = (Mroot[0] * y - Mroot[1] * x) / I + Fv[2] / Aa
    if np.ptp(sig) > best[0]:
        best = (float(np.ptp(sig)), math.degrees(th))
dsn = best[0]
FAT, GAM = 25.0, 1.30
ds_L = FAT * (2e6 / 1e7) ** (1 / 3) * (1e7 / N_LIFE) ** (1 / 22)   # 1×10⁷ 次以后斜率 22，到 5 年的次数
lam_weld = ds_L / GAM / dsn
lam_mach = H.lam_for_life(lambda x: x * sn, N_LIFE)


def lam_fkm_of(j_d):
    """FKM 的“允许放大倍数”：σa、σm 一起放大，利用度刚好为 1（R 不变，K_AK 随 σm/σa 不变，所以就是 1/利用度）"""
    return (K_BK * K_AK * s_wk / j_d) / sa


lam_fkm = lam_fkm_of(J_D)
lam_fkm1 = lam_fkm_of(1.0)
lam_weld1 = ds_L / dsn

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.3, 1]})
steps = [(T("σ_W,zd\n= 0.30 R_m", "σ_W,zd\n= 0.30 R_m"), s_wzd), (T("÷ K_WK\n({:.2f})".format(K_WK), "÷ K_WK\n({:.2f})".format(K_WK)), s_wk),
         (T("× K_AK\n({:.2f})".format(K_AK), "× K_AK\n({:.2f})".format(K_AK)), s_ak),
         (T("× K_BK\n({:.2f})".format(K_BK), "× K_BK\n({:.2f})".format(K_BK)), s_bk),
         (T("÷ j_D\n({:.1f})".format(J_D), "÷ j_D\n({:.1f})".format(J_D)), s_bk / J_D), (T("实际 σa", "actual σa"), sa)]
xs = np.arange(len(steps))
a0.bar(xs, [s[1] for s in steps], color=["#1f77b4", "#9ecae1", "#9ecae1", "#9ecae1", "#2ca02c", "#d62728"], width=0.6)
for x, (_, y) in zip(xs, steps):
    a0.text(x, y + 1.0, "{:.1f}".format(y), ha="center", fontsize=6.3)
a0.set_xticks(xs)
a0.set_xticklabels([s[0] for s in steps], fontsize=5.6)
a0.set_ylabel(T("应力幅 / MPa", "Stress amplitude / MPa"), fontsize=7.0)
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) FKM 局部应力法：利用度 a = {:.2f}".format(util), "(a) FKM local approach: utilization a = {:.2f}".format(util)), fontsize=7.0)
labs = [T("整体机加工\n（迈因纳，11.6 节）", "machined\n(Miner, 11.6)"), T("整体机加工\n（FKM）", "machined\n(FKM)"),
        T("焊接法兰\n（IIW FAT 25）", "welded flange\n(IIW FAT 25)")]
vals = [lam_mach, lam_fkm1, lam_weld1]
a1.bar(range(3), vals, color=["#1f77b4", "#2ca02c", "#d62728"], width=0.55)
for x, y in enumerate(vals):
    a1.text(x, y + 0.2, "{:.1f}".format(y), ha="center", fontsize=6.5)
a1.axhline(1.0, color=H.INK, lw=0.8, ls="--")
a1.set_ylim(0, max(vals) * 1.15)
a1.set_xticks(range(3))
a1.set_xticklabels(labs, fontsize=6.0)
a1.set_ylabel(T("载荷还能放大的倍数 λ", "Load factor λ still allowed"), fontsize=7.0)
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 5 年两班，不计安全系数", "(b) 5 years, two shifts, no safety factor"), fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_9_1")

out(sa=sa, sm=sm, R=Rr, Rm_min=RM_MIN, f_w=F_W, s_wzd=s_wzd, G=G, n_s=n_s, Rz=RZ, K_R=K_R, Kf_t=KF_T, K_S=K_S, K_WK=K_WK, s_wk=s_wk,
    M_s=M_s, region=region, K_AK=K_AK, s_ak=s_ak, j_D=J_D, util=util, S_fkm=S_fkm, K_BK=K_BK, N_life=N_LIFE, S_fac=s_fac["S_fat"], S_D_fac=s_fac["S_D"],
    dsn=dsn, th_weld=best[1], FAT=FAT, ds_L=ds_L, gam=GAM, lam_weld=lam_weld, lam_mach=lam_mach, lam_fkm=lam_fkm, lam_fkm1=lam_fkm1, lam_weld1=lam_weld1,
    util_weld=dsn / (ds_L / GAM), s1_lib=H.AL["sigma_1"], f_lib=H.AL["sigma_1"] / H.AL["ultimate_mpa"])
