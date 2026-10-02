"""6.7 节的算例。

先验证李括号的性质：so(3) 中 [[ω1],[ω2]] = [ω1 × ω2]；se(3) 中矩阵对易子与 [ad_V1]V2 一致（式 (6.7.4)、(6.7.6)）；
反对称性、雅可比恒等式；伴随矩阵的导数 d[Ad_T]/dt = [Ad_T][ad_Vb]（式 (6.7.10)）。
算例 6.7.1：差速 AGV 的“前进—左转—后退—右转”：净位移 ≈ ε²[V1, V2]（式 (6.7.8)），误差为 ε³ 量级；ε 减半，侧移约为四分之一。
算例 6.7.2：绕 {s} 中两根固定轴（UR5e 零位时关节 1、2 的轴）交替作小转动：净运动 ≈ −ε²[S1, S2]，是绕过肩部、沿 −x 方向的转动；
而 UR5e 的关节 1、2 来回转动时末端精确回到零位。
另：贝克-坎贝尔-豪斯多夫公式的前三项（式 (6.7.9)）：log(e^A e^B) ≈ A + B + ½[A, B]，误差为三阶。
"""
import math

import numpy as np
from scipy.linalg import expm, logm

from _screw import UR_M, UR_S, ad, adjoint, axis_of, bracket, exp6, inv, lie, pose, skew, unbracket, unskew, ur_fk
from bookout import out, vec

rng = np.random.default_rng(67)

# ---------------------------------------------------------------- 性质
for _ in range(30):
    w1, w2 = rng.normal(size=(2, 3))
    assert np.allclose(skew(w1) @ skew(w2) - skew(w2) @ skew(w1), skew(np.cross(w1, w2)))
    V1, V2, V3 = rng.normal(size=(3, 6))
    L = lie(V1, V2)
    assert np.allclose(L, ad(V1) @ V2)
    assert np.allclose(L, np.r_[np.cross(V1[:3], V2[:3]), np.cross(V1[:3], V2[3:]) - np.cross(V2[:3], V1[3:])])
    assert np.allclose(lie(V2, V1), -L)
    jac = lie(V1, lie(V2, V3)) + lie(V2, lie(V3, V1)) + lie(V3, lie(V1, V2))
    assert np.allclose(jac, 0, atol=1e-12)
    # 伴随矩阵的导数：T(t) = T0 e^{[Vb]t}
    T0 = pose(expm(skew(rng.normal(size=3))), rng.normal(size=3))
    h = 1e-6
    dAd = (adjoint(T0 @ expm(bracket(V1) * h)) - adjoint(T0 @ expm(bracket(V1) * -h))) / (2 * h)
    assert np.allclose(dAd, adjoint(T0) @ ad(V1), atol=1e-7)

# ---------------------------------------------------------------- 算例 6.7.1 差速 AGV
Vf = np.array([0, 0, 0, 1.0, 0, 0])      # 前进 1 m/s（物体坐标系）
Vr = np.array([0, 0, 1.0, 0, 0, 0])      # 绕自身中心左转 1 rad/s
Lfr = lie(Vf, Vr)
assert np.allclose(Lfr, [0, 0, 0, 0, -1, 0])


def maneuver(e, A=Vf, B=Vr):
    """物体坐标系中依次执行 A、B、−A、−B，各持续 ε：T = e^{[A]ε} e^{[B]ε} e^{−[A]ε} e^{−[B]ε}（右乘）。"""
    return expm(bracket(A) * e) @ expm(bracket(B) * e) @ expm(-bracket(A) * e) @ expm(-bracket(B) * e)


res = {}
for e in (0.2, 0.1, 0.05):
    T = maneuver(e)
    pred = expm(bracket(Lfr) * e * e)
    res[e] = (T[:3, 3].copy(), float(np.linalg.norm(T - pred)))
y02, y01 = res[0.2][0][1], res[0.1][0][1]
x02 = res[0.2][0][0]
assert abs(math.atan2(maneuver(0.2)[1, 0], maneuver(0.2)[0, 0])) < 1e-12        # 转回原来的朝向
# 闭式：前进 ε、左转 ε、后退 ε、右转 ε 后的位移 (ε(1 − cos ε), −ε sin ε)
assert np.allclose(res[0.2][0][:2], [0.2 * (1 - math.cos(0.2)), -0.2 * math.sin(0.2)])
# 误差为 ε³ 量级
r = res[0.2][1] / res[0.1][1]
assert 6 < r < 10
assert 3.5 < y02 / y01 < 4.5

# ---------------------------------------------------------------- 算例 6.7.2 UR5e 关节 1、2
L12 = lie(UR_S[0], UR_S[1])
s12, q12, h12 = axis_of(L12)
assert np.allclose(s12, [1, 0, 0]) and np.allclose(q12, [0, 0, 0.163]) and abs(h12) < 1e-12
# 两根轴固定在 {s} 中，依次“绕 S1 转 ε、绕 S2 转 ε、绕 S1 转回、绕 S2 转回”，每一步左乘：
# T = e^{−[S2]ε} e^{−[S1]ε} e^{[S2]ε} e^{[S1]ε}，即式 (6.7.8) 中 A = −S2、B = −S1，净效果 ε²[S2, S1] = −ε²[S1, S2]。
def spatial_seq(e, S1=UR_S[0], S2=UR_S[1]):
    return expm(-bracket(S2) * e) @ expm(-bracket(S1) * e) @ expm(bracket(S2) * e) @ expm(bracket(S1) * e)


errs = []
for e in (0.1, 0.05):
    T = spatial_seq(e)
    errs.append(float(np.linalg.norm(T - expm(-bracket(L12) * e * e))))
assert 6 < errs[0] / errs[1] < 10
T01 = spatial_seq(0.1)
S01 = np.real(unbracket(logm(T01)))
rot_deg = math.degrees(np.linalg.norm(S01[:3]))
s_net = S01[:3] / np.linalg.norm(S01[:3])
assert s_net[0] < -0.99                      # 净转动绕 −x̂
s_net_axis, q_net, h_net = axis_of(S01)
assert np.linalg.norm(q_net - [0, 0, 0.163]) < 0.01
# 对照：若让 UR5e 的关节 1、2 按同样次序来回转动，关节角全部归零，末端精确回到 M
th = np.zeros(6)
for j, dth in ((0, 0.1), (1, 0.1), (0, -0.1), (1, -0.1)):
    th[j] += dth
assert np.allclose(ur_fk(th), UR_M)

# ---------------------------------------------------------------- BCH
A, B = bracket(rng.normal(size=6)), bracket(rng.normal(size=6))
bch = []
for e in (0.1, 0.05):
    Lg = np.real(logm(expm(A * e) @ expm(B * e)))
    bch.append(float(np.linalg.norm(Lg - (A + B) * e - 0.5 * (A @ B - B @ A) * e * e)))
assert 6 < bch[0] / bch[1] < 10

out(L12=vec(L12, 3), y02=y02, x02=x02, y01=y01, ratio=y02 / y01, err02=res[0.2][1], err01=res[0.1][1], err_ratio=r,
    rot_deg=rot_deg, S01=vec(S01, 5), s_net=vec(s_net, 3), q_net=vec(q_net, 3), pred_rot_deg=math.degrees(0.01))
