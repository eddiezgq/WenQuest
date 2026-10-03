"""第 7 章 线张力与线迹质量 —— 课程包数值题的计算（示意模型与教材 7.2–7.7 节、虚拟实验 7-1 一致）。"""
from math import exp, pi, log, radians

GUIDE = exp(0.2 * 1.0)            # 过线件放大 1.22
EYEK = exp(-0.35 * pi)            # 针眼削减到约 1/3
KN = GUIDE * EYEK                 # 交织点面线张力 / 夹线器设定 ≈ 0.41
THREAD = {"Tex18": (700, 0.14), "Tex24": (1000, 0.15), "Tex40": (1700, 0.16)}   # 强力 cN、断裂伸长
FAB = {"lining": dict(t=0.4, B=1.8, pf=0.30), "cotton": dict(t=1.0, B=2.2, pf=0.60), "denim": dict(t=4.0, B=3.0, pf=4.0)}


def capstan(mu, theta_deg):
    return exp(mu * radians(theta_deg))


def z_pos(r, B):
    c = max(-1, min(1, log(r) / log(B)))
    return 0.5 + 0.5 * c


def td_range(Tb, B):
    """交织点位置 0.4–0.6 对应 r ∈ [B^-0.2, B^0.2]。"""
    return B ** -0.2 * Tb / KN, B ** 0.2 * Tb / KN


def pucker(Td, Tb, fab="cotton", thread="Tex24", s=3.0, seam=400):
    F, el = THREAD[thread]; f = FAB[fab]
    EA = F / el; lam = (s + f["t"]) / s
    mean = (KN * Td + Tb) / 2
    shrink = mean / EA * lam                     # 比例
    puck = max(0.0, shrink - f["pf"] / 100)
    return dict(mean=mean, shrink_pct=100 * shrink, pucker_pct=100 * puck, shrink_mm=shrink * seam, pucker_mm=puck * seam)


def peak(Td, n):
    return Td * GUIDE * (1 + 0.15 * (n / 5000) ** 2)


out = {}
out["KN"] = KN; out["GUIDE"] = GUIDE; out["EYEK"] = EYEK
out["习题1 出夹线器"] = 10 + 2 * 0.2 * 200; out["习题1 过线件后"] = (10 + 2 * 0.2 * 200) * GUIDE
out["习题2 3×90°"] = capstan(0.25, 270); out["习题2 改一个 45°"] = capstan(0.25, 225)
out["μ0.35 180°"] = capstan(0.35, 180)
out["r=1 Tb40 所需 Td"] = 40 / KN
out["棉布 Td 范围(Tb40)"] = td_range(40, 2.2); out["Tn≥35 下限"] = 35 / KN
out["起皱 100/40"] = pucker(100, 40); out["起皱 220/90"] = pucker(220, 90)
out["r 220/90"] = KN * 220 / 90
# 习题 4：平均张力 40、80 cN
for T in (40, 80):
    EA = 1000 / 0.15; lam = (3 + 1) / 3; sh = T / EA * lam
    out[f"习题4 平均{T}"] = (sh * 400, max(0, sh - 0.006) * 400)
out["牛仔 Td"] = 100 / KN; out["牛仔 峰值"] = peak(100 / KN, 5000)
out["峰值/Tex24"] = peak(100 / KN, 5000) / 1000; out["峰值/Tex40"] = peak(100 / KN, 5000) / 1700
# ---- 导入问题（衬衫棉布缝皱）----
out["问题 220/90 交织点面线张力"] = KN * 220
out["问题 z 220/90"] = z_pos(KN * 220 / 90, 2.2); out["问题 z 100/40"] = z_pos(KN * 100 / 40, 2.2)
# ---- 测验 / 考试 ----
out["Q 出夹线器 5+2*0.25*150"] = 5 + 2 * 0.25 * 150
out["Q 单过线件 120° μ0.2"] = capstan(0.2, 120)
out["Q r=1 Tb30 Td"] = 30 / KN
out["Q 衬里 Tb30 Td 上限"] = td_range(30, 1.8)[1]
out["E Tex40 平均60 起皱 40cm"] = (lambda T: (T / (1700 / 0.16) * 4 / 3 * 400, max(0, T / (1700 / 0.16) * 4 / 3 - 0.006) * 400))(60)
out["E 峰值 Td200 @4000"] = peak(200, 4000); out["E 峰值占 Tex24"] = peak(200, 4000) / 1000
# 机器人联系：腱绳总包角 270°、μ = 0.1
out["机器人 腱绳放大"] = capstan(0.1, 270)
for k, v in out.items():
    print(k, ":", v)

# 题目中按“0.41 倍”给出时的答案（容差覆盖 0.4067 的精确值）
print("Q r=1 Tb30 Td (0.41):", 30 / 0.41)
print("Q 衬里 Tb30 Td 上限 (0.41):", 1.8 ** 0.2 * 30 / 0.41)
