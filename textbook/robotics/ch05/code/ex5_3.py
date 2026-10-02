"""算例 5.3.1–5.3.3：齐次变换的复合与求逆。

UR5e 在关节角 (0°, −90°, 90°, −70°, −90°, 0°) 时，控制器给出法兰坐标系 {b} 的位姿 T_sb
（这里用第 12 章的指数积公式算出，并与零件库三维模型逐个核对）。夹爪的工具坐标系 {t} 相对 {b} 为 T_bt。
5.3.1 复合：T_st = T_sb T_bt，与“先把 {t} 的原点和三根轴换到 {b}、再换到 {s}”的逐点做法比较。
5.3.2 求逆：T_ts 按定理 5.3.2 计算，与通用矩阵求逆比较；验证 T_st T_ts = I。
5.3.3 左乘与右乘：沿工具自身 z 轴前进 20 mm 与沿基座 z 轴下降 20 mm；绕工具 z 轴转 90° 与绕基座 z 轴转 90°。
"""
import math

import numpy as np

from _frames import DEG, T, T_bt, clean, hom, inv, is_se3, rot_z, texm, trans, ur_fk_glb, ur_fk_poe, vecm
from bookout import out

theta = np.array([0, -90, 90, -70, -90, 0]) * DEG
Tsb = ur_fk_poe(theta)
assert np.allclose(Tsb, ur_fk_glb(theta), atol=1e-12)      # 与网页三维模型的算法一致
Tbt = T_bt()

# ---------------------------------------------------------------- 算例 5.3.1 复合
Tst = Tsb @ Tbt
# 逐点做法：{t} 的原点和三根轴先在 {b} 中写出，再用 T_sb 换到 {s}（原点按点、轴按自由矢量）
o_s = (Tsb @ hom(Tbt[:3, 3]))[:3]
axes_s = Tsb[:3, :3] @ Tbt[:3, :3]
assert np.allclose(o_s, Tst[:3, 3]) and np.allclose(axes_s, Tst[:3, :3])
assert is_se3(Tst)
# 次序不能交换
assert not np.allclose(Tbt @ Tsb, Tst)
wrong = Tbt @ Tsb

# ---------------------------------------------------------------- 算例 5.3.2 求逆
Tts = inv(Tst)
Tts_num = np.linalg.inv(Tst)
assert np.allclose(Tts, Tts_num, atol=1e-14)
assert np.allclose(Tst @ Tts, np.eye(4), atol=1e-15) and np.allclose(Tts @ Tst, np.eye(4), atol=1e-15)
neg_p = -Tst[:3, 3]                                     # 常见错误：只把 p 取负
assert np.linalg.norm(neg_p - Tts[:3, 3]) > 0.1
# 把一个点从 {s} 换到 {t} 再换回来
q_s = np.array([-0.45, -0.10, 0.02])                    # 台面上一个零件特征点（{s} 中）
q_t = (Tts @ hom(q_s))[:3]
assert np.allclose((Tst @ hom(q_t))[:3], q_s)

# ---------------------------------------------------------------- 算例 5.3.3 左乘与右乘
step = 0.02
Tst_A = Tst @ trans(0, 0, step)          # 沿 {t} 自身的 z 轴前进 20 mm（右乘）
Tst_B = trans(0, 0, -step) @ Tst         # 沿 {s} 的 z 轴下降 20 mm（左乘）
dA = Tst_A[:3, 3] - Tst[:3, 3]
dB = Tst_B[:3, 3] - Tst[:3, 3]
assert np.allclose(dA, step * Tst[:3, 2]) and np.allclose(dB, [0, 0, -step])
tilt = math.degrees(math.acos(-Tst[2, 2]))                # 工具 z 轴偏离竖直向下的角度
gap = np.linalg.norm(dA - dB)

Rz90 = T(rot_z(math.pi / 2))
Tst_C = Tst @ Rz90                        # 绕工具自身 z 轴转 90°（右乘）：TCP 不动
Tst_D = Rz90 @ Tst                        # 绕基座 z 轴转 90°（左乘）：TCP 绕基座竖直轴甩过 90°
assert np.allclose(Tst_C[:3, 3], Tst[:3, 3])
swing = np.linalg.norm(Tst_D[:3, 3] - Tst[:3, 3])
r_axis = math.hypot(Tst[0, 3], Tst[1, 3])
assert abs(swing - math.sqrt(2) * r_axis) < 1e-12        # 弦长 = √2 × 到 z_s 轴的距离
# 两种转动后的姿态相同吗？只有当工具 z 轴与 z_s 平行时才相同；这里不平行
assert not np.allclose(Tst_C[:3, :3], Tst_D[:3, :3])

out(
    Tsb=texm(clean(Tsb), 4), Tbt=texm(clean(Tbt), 2), Tst=texm(clean(Tst), 4), wrong=texm(clean(wrong), 4),
    Tts=texm(clean(Tts), 4), pst=vecm(Tst[:3, 3], 4), pts=vecm(Tts[:3, 3], 4), negp=vecm(neg_p, 4),
    pst_norm=np.linalg.norm(Tst[:3, 3]), pts_norm=np.linalg.norm(Tts[:3, 3]),
    qt=vecm(q_t, 4), dA=vecm(dA, 4), dB=vecm(dB, 4), tilt=tilt, gap_mm=gap * 1000,
    pD=vecm(Tst_D[:3, 3], 4), swing=swing, r_axis=r_axis,
    zt=vecm(clean(Tst[:3, 2]), 4),
)
