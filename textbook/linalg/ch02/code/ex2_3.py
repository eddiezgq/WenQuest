"""2.3 节：点积、长度、夹角；功；两连杆臂的肘关节角由点积求出；随机检验柯西–施瓦茨不等式与三角不等式。"""
import math

import numpy as np

from bookout import out, vec
from _arm import ur5e_links

# 拖车：AGV 通过斜向上的牵引绳用力 F 拉料车沿地面走 d，力做的功 W = F·d
F = np.array([40.0, 0.0, 30.0])
d = np.array([5.0, 0.0, 0.0])
out(F=vec(F, 0), d=vec(d, 0), W=float(F @ d), Fn=float(np.linalg.norm(F)),
    angFd=math.degrees(math.acos(F @ d / (np.linalg.norm(F) * np.linalg.norm(d)))))
# 两连杆臂（2.2 节的姿态）：上臂向量与前臂向量的夹角就是肘关节转过的角
l1, l2 = ur5e_links()
t1, t2 = math.radians(30), math.radians(45)
r1 = l1 * np.array([math.cos(t1), math.sin(t1)])
r2 = l2 * np.array([math.cos(t1 + t2), math.sin(t1 + t2)])
cosang = r1 @ r2 / (np.linalg.norm(r1) * np.linalg.norm(r2))
out(dot12=float(r1 @ r2), cos12=float(cosang), ang12=math.degrees(math.acos(cosang)))
# 手算的例子
u, v = np.array([1.0, 2.0, 2.0]), np.array([2.0, -2.0, 1.0])
out(uv=float(u @ v), un=float(np.linalg.norm(u)), vn=float(np.linalg.norm(v)), uv_unit=vec(u / np.linalg.norm(u), 4))
a, b = np.array([3.0, 4.0]), np.array([4.0, 3.0])
out(ab=float(a @ b), cosab=float(a @ b / 25), angab=math.degrees(math.acos(a @ b / 25)))
# 四维的例子：x = (1, 1, 1, 1), y = (1, 0, 0, 0)，夹角 60°
x, y = np.ones(4), np.array([1.0, 0, 0, 0])
out(ang4=math.degrees(math.acos(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))))
# 随机检验：100000 对 5 维向量，|u·v| ≤ ‖u‖‖v‖、‖u + v‖ ≤ ‖u‖ + ‖v‖ 从未被违反；比值的最大值
rng = np.random.default_rng(23)
U, V = rng.standard_normal((100000, 5)), rng.standard_normal((100000, 5))
ratio = np.abs((U * V).sum(1)) / (np.linalg.norm(U, axis=1) * np.linalg.norm(V, axis=1))
tri = np.linalg.norm(U + V, axis=1) - np.linalg.norm(U, axis=1) - np.linalg.norm(V, axis=1)
out(cs_max=float(ratio.max()), cs_ok=bool((ratio <= 1 + 1e-12).all()), tri_ok=bool((tri <= 1e-12).all()), trials=100000)
