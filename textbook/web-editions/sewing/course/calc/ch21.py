"""第 21 章 电子花样机与电脑横机电控原型 —— 课程包数值题计算（数据取自教材 21.3、21.6、21.7 节）"""
import math

# ---------- 花样机原型 WQ-SC/PS ----------
C_S = 5.333            # S 形峰值加速度系数
WU = 183.4             # 实用窗口（布厚 1.5 mm），度
Ph = 0.010             # 丝杠导程 m
Jm, Jp2 = 0.30e-4, 0.01e-4
rho, L, d = 7850, 0.5, 0.016
J_screw = math.pi * rho * L * d**4 / 32


def J_total(m):
    return Jm + Jp2 + J_screw + m * (Ph / 2 / math.pi) ** 2


def torque(m, a, mu=0.1, eta=0.9):
    return J_total(m) * 2 * math.pi * a / Ph + mu * m * 9.81 * Ph / (2 * math.pi * eta)


def dt_window(wu, n):
    return wu / (6 * n)


def n_cap(s_mm, a, wu=WU, nhead=2500):
    dt = math.sqrt(C_S * s_mm * 1e-3 / a)
    return min(wu / (6 * dt), nhead)


print("J_screw", J_screw, "J_X", J_total(4))
dt = dt_window(WU, 1600)
a = C_S * 0.003 / dt**2
print("引子/算例: dt ms", round(dt * 1e3, 2), " a", round(a, 1), " vpk", round(2 * 0.003 / dt, 3),
      " motor rpm", round(2 * 0.003 / dt / Ph * 60), " T_X", round(torque(4, a), 2), " T_Y", round(torque(12, a), 2))
print("rms 系数", round(0.816 * math.sqrt(WU / 360), 3), " T_pk 上限", round(1.27 / (0.816 * math.sqrt(WU / 360)), 2))
for s in range(1, 7):
    print("s", s, "X", round(n_cap(s, 50)), "Y", round(n_cap(s, 40)), "45°", round(n_cap(s / math.sqrt(2), 40)))
# 测验：2000 r/min 时实用窗口时间
print("Q dt@2000", round(dt_window(WU, 2000) * 1e3, 2), "ms")
# 测验：沿 Y 2 mm
print("Q Y 2mm cap", round(n_cap(2, 40)))
# 考试：布厚 3 mm（几何窗口 192.6°），沿 X 3 mm，a=50
print("E X 3mm, 3mm cloth:", round(n_cap(3, 50, wu=192.6 - 20)))
# 习题 1 复核
print("习题1 Y 4mm 3mm cloth:", round(n_cap(4, 40, wu=172.6)))
# 2500 r/min 忘记延迟补偿：滞后角
print("E lag@2500", 2500 * 6 * 1.5e-3, "deg")
# 前瞻算例
caps = [2092, 2092, 2092, 2092, 1080, 2092, 2092, 2092]
n = caps[:]
for i in range(len(n) - 2, -1, -1):
    n[i] = min(n[i], n[i + 1] + 300)
prev = 400
for i in range(len(n)):
    n[i] = min(n[i], prev + 300); prev = n[i]
print("前瞻(从 400 起步)", n)
n = caps[:]
for i in range(len(n) - 2, -1, -1):
    n[i] = min(n[i], n[i + 1] + 300)
print("前瞻(仅反向)", n)

# ---------- 缩比横机原型 WQ-SC/FK ----------
p5 = 25.4 / 5
p6 = 25.4 / 6
p7 = 25.4 / 7
Tr, J = 1.5e-3, 0.3e-3


def vmax_mcu(p_mm, Tc, J=J):
    return 0.1 * p_mm * 1e-3 / (Tc / 2 + J)


def vmax_fpga(p_mm, J=J, res=0.01):
    return (0.1 * p_mm - res / 2) * 1e-3 / J


v = 0.6
print("每针时间 ms", round(p5 / v, 2), " 同段间隔 ms", round(8 * p5 / v, 1))
print("提前量 mm", round(v * (Tr + 0.5e-3) * 1e3, 2), "=", round(v * (Tr + 0.5e-3) * 1e3 / p5, 3), "p")
print("最坏误差 mm", round(v * (0.5e-3 + J) * 1e3, 3), "=", round(v * (0.5e-3 + J) * 1e3 / p5, 3), "p")
print("vmax MCU 1ms", round(vmax_mcu(p5, 1e-3), 3), " 0.5ms", round(vmax_mcu(p5, 0.5e-3), 3),
      " 0.25ms", round(vmax_mcu(p5, 0.25e-3), 3), " FPGA", round(vmax_fpga(p5), 3))
print("E6 MCU 1ms", round(vmax_mcu(p6, 1e-3), 3), " E7 MCU 1ms", round(vmax_mcu(p7, 1e-3), 3),
      " E7 FPGA", round(vmax_fpga(p7), 3))
# 一行用时（梯形速度，a=10，c=40，Lk=80，换向 0.1 s）


def row_time(v, a=10, c=40, Lk=80, p=p5, N=60, trev=0.1):
    D = (2 * c + N * p + Lk) / 1000
    if D <= v * v / a:
        vp = math.sqrt(a * D); T = 2 * vp / a
    else:
        T = 2 * v / a + (D - v * v / a) / v
    return D, T + trev


D, t = row_time(0.6)
print("D mm", D * 1e3, " 一行 s", round(t, 3), " 行/h", round(3600 / t))
for vv in (0.635, 1.66):
    D, t = row_time(vv)
    print(" v", vv, "一行", round(t, 3), "行/h", round(3600 / t))
print("产量比 1.66/0.6:", round(row_time(0.6)[1] / row_time(1.66)[1], 3), " 速度比", round(1.66 / 0.6, 2))
print("20 行样片 s", round(20 * row_time(0.6)[1], 1))
# 制动距离
for vv in (1.66, 0.635, 1.0):
    print("制动 v", vv, "mm", round(vv**2 / (2 * 20) * 1e3, 1))
# 两速扫描标定
slope = (0.26 - 0.09) / (0.9 - 0.3)       # mm/(m/s) = ms
print("标定斜率 ms", round(slope, 3), " Tr_new", round(1.2 + slope, 3))
# 考试：标定变式 0.4 m/s 中点 0.05 mm，1.0 m/s 中点 0.29 mm，初值 1.2 ms
slope2 = (0.29 - 0.05) / (1.0 - 0.4)
print("E 标定斜率", round(slope2, 3), " Tr_new", round(1.2 + slope2, 3), " 截距(几何偏移) mm", round(0.05 - slope2 * 0.4, 3))
# 单段选针器约束 p/v >= 2Tr
print("单段 E5 vmax", round(p5 / 3, 3), "E7", round(p7 / 3, 3))
# 选针目标位置（计数）
C_UM, P_UM = 40000, 5080
print("target0", (C_UM + P_UM // 2) // 10, "target1", (C_UM + 3 * P_UM // 2) // 10)
# 机头推力与转矩（示意）
F = 2.5 * 10 + 2.5 + 15
r = 0.03183 / 2
print("推力 N", F, " 峰值转矩", round(F * r, 3), " 匀速", round(17.5 * r, 3), " 2 m/s rpm", round(2 / 0.1 * 60))

# ---------- 作业 ----------
print("作业1 布厚3mm（Wu=172.6）:")
for s in (2, 3, 4):
    print("  s", s, "X", round(n_cap(s, 50, wu=172.6)), "Y", round(n_cap(s, 40, wu=172.6)))
JY = 0.820e-4
Tpk = JY * 2 * math.pi * 50 / 0.01
print("作业2 Tpk", round(Tpk, 2), " Trms", round(Tpk * 0.816 * math.sqrt(WU / 360), 2))
print("作业3 E6: MCU1", round(vmax_mcu(p6, 1e-3), 3), " MCU0.5", round(vmax_mcu(p6, 0.5e-3), 3), " FPGA", round(vmax_fpga(p6), 3))
for vv in (0.6, 1.0, 1.66):
    print("作业4 制动", vv, round(vv**2 / 40 * 1e3, 1), "mm")
