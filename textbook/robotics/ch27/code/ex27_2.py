"""27.2 节的计算：库仑摩擦与摩擦锥。

(1) 算例 27.2.2：平口夹爪竖直提起 SH-301 毛坯（2.8 kg），钢对钢 μ = 0.2（示意值）。静止时、以 a = 3 m/s² 加速提起时的最小夹紧力
    F = m(𝔤 + a)/(2μ)；90° V 形夹爪 F = m(𝔤 + a) cos γ/(2μ)。在 MuJoCo 中夹住毛坯提起，二分法找刚好不滑的夹紧力，与公式比较。
(2) 算例 27.2.1：MuJoCo 的棱锥摩擦锥与椭圆摩擦锥。地面上 1 kg 的方块，沿 0° 和 45° 方向推，找开始滑动的推力；
    推力为最大静摩擦的一半时的蠕滑速度（后 1 s 的平均速度；impratio = 1、10）与 noslip 的效果。内接棱锥最窄处的相对误差 1 − cos(π/k)。
(3) 算例 27.2.3：毛坯水平（卡盘前 B）时的平口夹爪：重力绕夹紧方向的力矩靠接触线两端的摩擦力偶承担，
    F = m𝔤(1/2 + d/ℓ)/μ；MuJoCo 中的值；V 形夹爪的值。
"""
import math

import mujoco
import numpy as np

from _ch27 import G0, GRIP_TOP, MU_JAW, PAD_HALF, V_HALF, mj_threshold, sh301_blank
from bookout import out

m_b, r_b, L_b = sh301_blank()
W = m_b * G0
A_LIFT = 3.0

# ---------------------------------------------------------------- (1) 竖直提起
F_flat0 = W / (2 * MU_JAW)
F_flat3 = m_b * (G0 + A_LIFT) / (2 * MU_JAW)
F_v0 = W * math.cos(V_HALF) / (2 * MU_JAW)
F_v3 = m_b * (G0 + A_LIFT) * math.cos(V_HALF) / (2 * MU_JAW)
TOL = 0.25
mj_flat0 = mj_threshold("flat", "v", 0.0, lo=0.7 * F_flat0, hi=1.25 * F_flat0, tol=TOL)
mj_flat3 = mj_threshold("flat", "v", A_LIFT, lo=0.7 * F_flat3, hi=1.25 * F_flat3, tol=TOL)
mj_v0 = mj_threshold("V", "v", 0.0, lo=0.7 * F_v0, hi=1.25 * F_v0, tol=TOL)
mj_v3 = mj_threshold("V", "v", A_LIFT, lo=0.7 * F_v3, hi=1.25 * F_v3, tol=TOL)
for a, b in ((mj_flat0, F_flat0), (mj_flat3, F_flat3), (mj_v0, F_v0), (mj_v3, F_v3)):
    assert abs(a / b - 1) < 0.01
v_gain = 1 / math.cos(V_HALF)                         # V 形夹爪的法向力是平口的 1/cos γ 倍

# ---------------------------------------------------------------- (2) 棱锥与椭圆
def box(cone, impratio=1, ns=0, mu=0.5):
    x = (f'<mujoco><option timestep="0.001" cone="{cone}" impratio="{impratio}" noslip_iterations="{ns}"/>'
         f'<default><geom solref="0.02 1" friction="{mu} 0.005 0.0001"/></default><worldbody><geom type="plane" size="5 5 0.1"/>'
         '<body name="b" pos="0 0 0.05"><freejoint/><geom type="box" size="0.05 0.05 0.05" mass="1"/></body></worldbody></mujoco>')
    m = mujoco.MjModel.from_xml_string(x)
    return m, mujoco.MjData(m)


def push(cone, phi, ratio, T=2.0, rate=False, **kw):
    """静置 0.5 s 后，沿 φ 方向施加 ratio × μm𝔤 的水平推力 T 秒，返回位移（m）；rate = True 时返回最后 1 s 的平均速度（m/s）。"""
    m, d = box(cone, **kw)
    for _ in range(500):
        mujoco.mj_step(m, d)
    x0 = d.qpos[:2].copy()
    F = ratio * 0.5 * G0
    x1 = None
    for k in range(int(T / 0.001)):
        d.xfrc_applied[1, :3] = [F * math.cos(phi), F * math.sin(phi), 0]
        mujoco.mj_step(m, d)
        if k == int((T - 1.0) / 0.001) - 1:
            x1 = d.qpos[:2].copy()
    if rate:
        return float(np.linalg.norm(d.qpos[:2] - x1))
    return float(np.linalg.norm(d.qpos[:2] - x0))


def slip_ratio(cone, phi):
    lo, hi = 0.5, 1.2
    while hi - lo > 0.002:
        mid = (lo + hi) / 2
        if push(cone, phi, mid) > 0.05:               # 2 s 内滑出 5 cm 以上算滑动
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


s_py0, s_py45 = slip_ratio("pyramidal", 0.0), slip_ratio("pyramidal", math.pi / 4)
s_el0, s_el45 = slip_ratio("elliptic", 0.0), slip_ratio("elliptic", math.pi / 4)
assert abs(s_py45 - math.cos(math.pi / 4)) < 0.01 and abs(s_py0 - 1) < 0.01 and abs(s_el45 - 1) < 0.01
creep1 = push("elliptic", 0.0, 0.5, rate=True)                 # 蠕滑速度（后 1 s），m/s
creep10 = push("elliptic", 0.0, 0.5, rate=True, impratio=10)
creep_ns = push("elliptic", 0.0, 0.5, rate=True, impratio=10, ns=10)
el_ns = push("elliptic", 0.0, 0.5, T=1.0, impratio=10, ns=10)     # noslip 时推力加上后 1 s 内的位移（主要是弹性变形）
cone_err = {k: 1 - math.cos(math.pi / k) for k in (4, 8, 64)}  # 内接棱锥最窄处的相对误差

# ---------------------------------------------------------------- (3) 毛坯水平
d_com = L_b / 2 - GRIP_TOP                            # 质心到夹持点的距离（沿毛坯轴线）
ell = 2 * PAD_HALF                                    # 接触线两端的距离
f_plus = W / 4 + W * d_com / (2 * ell)                # 远端一点要承担的摩擦力（每个夹爪）
f_minus = W / 4 - W * d_com / (2 * ell)
F_flat_h = W * (0.5 + d_com / ell) / MU_JAW
mj_flat_h = mj_threshold("flat", "h", 0.0, lo=0.7 * F_flat_h, hi=1.25 * F_flat_h, tol=TOL)
assert abs(mj_flat_h / F_flat_h - 1) < 0.01
mj_v_h = mj_threshold("V", "h", 0.0, lo=10.0, hi=60.0, tol=TOL)
h_over_v = F_flat_h / F_flat0
M_grav = W * d_com                                    # 重力绕夹紧方向的力矩
# 扭转摩擦（软指）：半径 r_p 的圆形指面，均布压力时最大扭矩 (2/3)μNa
R_PAD = 0.01
Mt_pad = 2 / 3 * MU_JAW * 1.0 * R_PAD                 # 单位法向力时
F_soft_h = M_grav / (2 * Mt_pad)                      # 两个圆形指面只靠扭转摩擦平衡重力矩时所需的夹紧力

slope_deg = math.degrees(math.atan(MU_JAW))                                  # 习题 27.2.1
F_v60 = W * math.cos(math.radians(60)) / (2 * MU_JAW)                        # 习题 27.2.2：60° V 形槽
F_l06 = W * (0.5 + d_com / 0.06) / MU_JAW                                    # 习题 27.2.3：指面加长到 0.06 m
F_d25 = W * (0.5 + (d_com - 0.025) / ell) / MU_JAW                           # 夹持点向中间移 25 mm

# 习题 27.2.5：捏起一支笔（20 g，μ = 0.4）；捏在中间、竖直；捏在一端、横着（质心离夹持点 6 cm，指腹接触长 1.5 cm）
F_pen_mid = 0.02 * G0 / (2 * 0.4)
F_pen_end = 0.02 * G0 * (0.5 + 0.06 / 0.015) / 0.4

out(F_pen_mid=F_pen_mid, F_pen_end=F_pen_end, cone4=cone_err[4] * 100, cone8=cone_err[8] * 100, cone64=cone_err[64] * 100,
    el_ns_um=el_ns * 1e6, slope_deg=slope_deg, F_v60=F_v60, F_l06=F_l06, F_d25=F_d25, m_b=m_b, W=W, mu=MU_JAW, a_lift=A_LIFT, F_flat0=F_flat0, F_flat3=F_flat3, F_v0=F_v0, F_v3=F_v3,
    mj_flat0=mj_flat0, mj_flat3=mj_flat3, mj_v0=mj_v0, mj_v3=mj_v3, v_gain=v_gain, gam_deg=math.degrees(V_HALF),
    s_py0=s_py0, s_py45=s_py45, s_el0=s_el0, s_el45=s_el45, creep1_mm=creep1 * 1e3, creep10_mm=creep10 * 1e3, creep_ns_um=creep_ns * 1e6,
    d_com=d_com, ell=ell, f_plus=f_plus, f_minus=f_minus, F_flat_h=F_flat_h, mj_flat_h=mj_flat_h, mj_v_h=mj_v_h, h_over_v=h_over_v,
    M_grav=M_grav, r_pad_mm=R_PAD * 1e3, F_soft_h=F_soft_h)
