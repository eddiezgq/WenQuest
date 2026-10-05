"""第 5 章共用：碳纤维/环氧层合板（混合律、Halpin–Tsai 式、经典层合理论）。程序 5.5.1、5.7.1 都用它，数字一致。
纤维与树脂的性能是常见的典型值（T700 级碳纤维、通用环氧树脂，厂商数据表的量级），本书设定，待核对。"""
import math

import numpy as np

EF1, EF2, GF12, NUF, RHOF = 230.0, 15.0, 24.0, 0.20, 1.80     # 碳纤维：轴向模量、横向模量、剪切模量 GPa，泊松比，密度
EM, NUM, RHOM = 3.5, 0.35, 1.20                               # 环氧树脂
VF = 0.60                                                     # 纤维体积分数
GM = EM / (2 * (1 + NUM))


def halpin_tsai(Pf, Pm, xi, vf):
    eta = (Pf / Pm - 1) / (Pf / Pm + xi)
    return Pm * (1 + xi * eta * vf) / (1 - eta * vf)


E1 = VF * EF1 + (1 - VF) * EM                     # 纵向：混合律
E2 = halpin_tsai(EF2, EM, 2.0, VF)                # 横向：Halpin–Tsai，ξ = 2
E2_inv = 1 / (VF / EF2 + (1 - VF) / EM)           # 横向：反混合律（偏低，对照）
G12 = halpin_tsai(GF12, GM, 1.0, VF)
NU12 = VF * NUF + (1 - VF) * NUM
RHO = VF * RHOF + (1 - VF) * RHOM


def Q_ply():
    nu21 = NU12 * E2 / E1
    d = 1 - NU12 * nu21
    return np.array([[E1 / d, NU12 * E2 / d, 0], [NU12 * E2 / d, E2 / d, 0], [0, 0, G12]])


def Qbar(theta_deg):
    t = math.radians(theta_deg)
    c, s = math.cos(t), math.sin(t)
    Tm = np.array([[c * c, s * s, 2 * c * s], [s * s, c * c, -2 * c * s], [-c * s, c * s, c * c - s * s]])
    R = np.diag([1, 1, 2])
    return np.linalg.inv(Tm) @ Q_ply() @ R @ Tm @ np.linalg.inv(R)


def A_matrix(layup):
    return sum(Qbar(a) for a in layup) / len(layup)       # 各层等厚：平均刚度 A/h（单位厚度）


def Ex_at(Aavg, phi):
    """层合板在面内 φ 方向的弹性模量（把坐标转 φ 后取 x 方向的柔度）"""
    t = math.radians(phi)
    c, s = math.cos(t), math.sin(t)
    Tm = np.array([[c * c, s * s, 2 * c * s], [s * s, c * c, -2 * c * s], [-c * s, c * s, c * c - s * s]])
    R = np.diag([1, 1, 2])
    Arot = np.linalg.inv(Tm) @ Aavg @ R @ Tm @ np.linalg.inv(R)
    return 1 / np.linalg.inv(Arot)[0, 0]


QI = [0, 45, -45, 90, 90, -45, 45, 0]


def qi_modulus():
    """[0/45/−45/90]s 准各向同性层合板的面内弹性模量 GPa 与密度 g/cm³"""
    return float(Ex_at(A_matrix(QI), 0.0)), RHO
