"""第 8 章 运动协调与整机动力学 —— 课程包数值题的计算。
惯性力按转速平方缩放（教材 8.4 节：k = 0.45、5000 r/min 时最大合力约 368 N；针杆下止点约 654 N）；
时序数据取第 3–6 章算例。相位窗口与合力的教材数值已用虚拟实验 8-1 的模型（node 运行实验页脚本）复核。"""
from math import sqrt, cos, sin, radians, degrees

R, L = 15.5, 55.0; LAM = R / L


def xN(f):
    a = radians(f)
    return R * (1 - cos(a)) - L * (1 - sqrt(1 - (LAM * sin(a)) ** 2))


def rise(f):
    return xN(180) - xN(f)


def angle_for_rise(h):
    a, b = 180.0, 260.0
    for _ in range(80):
        m = (a + b) / 2
        a, b = (m, b) if rise(m) < h else (a, m)
    return (a + b) / 2


def ms_per_deg(n):
    return 1000 / (n * 6)


F5000, NB5000 = 368.0, 654.0      # 教材 8.4 节、第 3 章
scale = lambda n: (n / 5000) ** 2

out = {}
out["重叠 114.2-101.7"] = 114.18 - 101.67
out["重叠时间 @5000 ms"] = 12.5 * ms_per_deg(5000)
out["4000→5000 倍数"] = (5000 / 4000) ** 2
out["回升 1.6/2.5 对应转角"] = (angle_for_rise(1.6), angle_for_rise(2.5))
out["回升 @210°"] = rise(210)
out["5500 合力 / 针杆"] = (F5000 * scale(5500), NB5000 * scale(5500))
out["6000 合力 / 4000 合力"] = (F5000 * scale(6000), F5000 * scale(4000))
# 导入问题：5000 → 6000 r/min
out["问题 6000 合力"] = F5000 * scale(6000); out["问题 6000 针杆"] = NB5000 * scale(6000)
out["问题 重叠时间 @6000 ms"] = 12.5 * ms_per_deg(6000)
out["问题 5500 合力"] = F5000 * scale(5500)
# 测验 / 考试
out["Q 重叠时间 @4000 ms"] = 12.5 * ms_per_deg(4000)
out["Q 合力 @4500"] = F5000 * scale(4500)
out["Q 回升 @208°"] = rise(208)
out["Q 合力≤450 的最高转速"] = 5000 * sqrt(450 / F5000)
out["Q 针杆 @4000"] = NB5000 * scale(4000)
out["E 针杆 @6000"] = NB5000 * scale(6000)
out["E 3000→4500 倍数"] = (4500 / 3000) ** 2
out["E 推迟 3° 主轴转角 回升"] = rise(206.07 + 3)
# 机器人联系：压力机节拍 15 → 18 次/分，加速度倍数
out["机器人 18/15 加速度倍数"] = (18 / 15) ** 2
for k, v in out.items():
    print(k, ":", v)
