"""第 5 章 钩线机构 —— 课程包数值题的计算（与教材算例一致）。"""
from math import pi, sqrt, cos, sin, radians, degrees, acos

R, L = 15.5, 55.0            # 第 3 章算例：曲柄半径、连杆长 (mm)
LAM = R / L                  # 连杆比 ≈ 0.282


def x_needle(phi):
    """针杆自上止点下行的位移 (mm)，phi 为主轴转角 (deg)。"""
    a = radians(phi)
    return R * (1 - cos(a)) - L * (1 - sqrt(1 - (LAM * sin(a)) ** 2))


def rise_exact(phi):
    return x_needle(180) - x_needle(phi)


def angle_for_rise_exact(h):
    a, b = 180.0, 260.0
    for _ in range(80):
        m = (a + b) / 2
        a, b = (m, b) if rise_exact(m) < h else (a, m)
    return (a + b) / 2


def angle_for_rise_approx(h, r=R, lam=0.282):
    """h ≈ r/2 (1+λ) δ²  →  主轴转角 = 180° + δ。"""
    return 180 + degrees(sqrt(h / (r / 2 * (1 + lam))))


def hook_speed(n_main, Rh=13.5e-3):
    """梭尖线速度 (m/s)，旋梭转速 = 2 × 主轴转速。"""
    return 2 * pi * Rh * 2 * n_main / 60


out = {}
# 教材数字复核
out["钩线 2 mm 精确转角"] = angle_for_rise_exact(2.0)                 # 206.1
out["回升 1.6 mm 近似转角"] = angle_for_rise_approx(1.6)              # 203.0
out["回升 2.5 mm 近似转角"] = angle_for_rise_approx(2.5)              # 208.7
out["2.0→2.5 旋梭转角"] = 2 * (angle_for_rise_approx(2.5) - angle_for_rise_approx(2.0))   # ≈6
out["201° 回升"] = rise_exact(201); out["211° 回升"] = rise_exact(211)  # 1.3 / 2.8
out["5000 r/min 梭尖速度"] = hook_speed(5000)                          # ≈14
out["8° 窗口时间 ms @5000"] = 8 / (5000 * 360 / 60) * 1000            # 0.27
out["8° 窗口梭尖行程 mm"] = 14 * out["8° 窗口时间 ms @5000"]           # 3.7
out["1:1 脱环角"] = 206 + 270                                          # 476 = 116 of next
out["Nm90→110 间隙"] = 0.08 - (1.1 - 0.9) / 2                          # -0.02
out["Nm90→70 间隙(0.06)"] = 0.06 + (0.9 - 0.7) / 2                     # 0.16

# 导入问题（车间）：衬衫线换牛仔线
out["问题 Nm90→110 间隙(0.06)"] = 0.06 - (1.1 - 0.9) / 2              # -0.04
out["问题 轴向移出量使间隙回到 0.06"] = 0.06 - out["问题 Nm90→110 间隙(0.06)"]  # 0.10

# 测验
out["Q 梭尖速度 @4000"] = hook_speed(4000)
out["Q 回升 1.6 转角"] = angle_for_rise_approx(1.6)
out["Q Nm80→100 间隙(0.09)"] = 0.09 - (1.0 - 0.8) / 2
# 考试
out["E 1.6→2.2 旋梭转角"] = 2 * (angle_for_rise_approx(2.2) - angle_for_rise_approx(1.6))
out["E 10° 窗口 @4500 ms"] = 10 / (4500 * 6) * 1000
# 机器人联系：传送带抓取窗口（同样的 0.27 ms 量级对比）
for k, v in out.items():
    print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
