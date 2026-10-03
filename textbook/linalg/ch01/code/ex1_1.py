"""1.1 节：UR5e 手臂水平伸出时，负载在肩关节产生的力矩——对负载是线性的（比例与叠加），对关节角不是。"""
import json
import math
from pathlib import Path

from bookout import out

MODELS = Path(__file__).resolve().parents[2] / "models"
js = {j["name"]: j for j in json.loads((MODELS / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))["robot"]["joints"]}
l1 = js["elbow_joint"]["origin"]["xyz"][2]          # 上臂 0.425 m
l2 = js["wrist_1_joint"]["origin"]["xyz"][2]        # 前臂 0.392 m
L = l1 + l2
g = 9.80665                                         # 标准重力加速度，m/s²


def tau(m, theta_deg=0.0):
    """质量 m（kg）的负载挂在腕心处，手臂与水平面成 θ 角时，负载在肩关节产生的力矩（N·m）。"""
    return m * g * L * math.cos(math.radians(theta_deg))


t1, t2, t3 = tau(1.0), tau(2.0), tau(3.0)
assert abs(t3 - (t1 + t2)) < 1e-12 and abs(t2 - 2 * t1) < 1e-12
out(l1=l1, l2=l2, L=L, g=g, t1=t1, t2=t2, t3=t3, t1p2=t1 + t2,
    t30=tau(2.0, 30), t60=tau(2.0, 60), t30x2=2 * tau(2.0, 30))
# y = 2x + 1 不满足叠加
f = lambda x: 2 * x + 1
out(f1=f(1), f2=f(2), f3=f(3), f1pf2=f(1) + f(2))

# 习题 1.1.2：腕心 0.8 kg + 前臂中点 0.5 kg，叠加
out(drop30=tau(2.0, 0) - tau(2.0, 30), drop60=tau(2.0, 0) - tau(2.0, 60), drop30x2=2 * (tau(2.0, 0) - tau(2.0, 30)))
out(ans112=0.8 * g * L + 0.5 * g * (l1 + l2 / 2))
