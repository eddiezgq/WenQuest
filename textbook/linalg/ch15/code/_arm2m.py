"""本章共用：平面两连杆机械臂（均匀细杆）的雅可比矩阵、质量矩阵与重力势能。以下划线开头，构建时不单独运行。

连杆长 l1 = 0.40 m、l2 = 0.30 m（与第 14 章 _arm2.py 相同），质量 m1 = 2 kg、m2 = 1 kg，质心在中点，
绕质心的转动惯量 I_i = m_i l_i² / 12。q2 为相对角。网页实验 15.6、15.8 用同样的参数与公式（lab15_6.js、lab15_8.js）。
    动能 = ½ q̇ᵀ M(q) q̇，
    M11 = I1 + I2 + m1 c1² + m2 (l1² + c2² + 2 l1 c2 cos q2)，M12 = I2 + m2 (c2² + l1 c2 cos q2)，M22 = I2 + m2 c2²，
其中 c_i = l_i / 2。末端负载 mp（质点）相当于在末端加一个质量。
"""
import numpy as np

L1, L2 = 0.40, 0.30
M1, M2 = 2.0, 1.0
G = 9.81


def jac(q1, q2, l1=L1, l2=L2):
    a1, a2 = q1, q1 + q2
    return np.array([[-l1 * np.sin(a1) - l2 * np.sin(a2), -l2 * np.sin(a2)],
                     [l1 * np.cos(a1) + l2 * np.cos(a2), l2 * np.cos(a2)]])


def jac_c(q1, q2, link):
    """连杆 link（1 或 2）质心的 2×2 位置雅可比。"""
    a1, a2 = q1, q1 + q2
    if link == 1:
        c = L1 / 2
        return np.array([[-c * np.sin(a1), 0.0], [c * np.cos(a1), 0.0]])
    c = L2 / 2
    return np.array([[-L1 * np.sin(a1) - c * np.sin(a2), -c * np.sin(a2)],
                     [L1 * np.cos(a1) + c * np.cos(a2), c * np.cos(a2)]])


def mass(q2, mp=0.0, m1=M1, m2=M2, l1=L1, l2=L2):
    """质量矩阵（与 q1 无关）。mp：末端负载（质点）。"""
    c1, c2 = l1 / 2, l2 / 2
    I1, I2 = m1 * l1 ** 2 / 12, m2 * l2 ** 2 / 12
    cq = np.cos(q2)
    m11 = I1 + I2 + m1 * c1 ** 2 + m2 * (l1 ** 2 + c2 ** 2 + 2 * l1 * c2 * cq) + mp * (l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * cq)
    m12 = I2 + m2 * (c2 ** 2 + l1 * c2 * cq) + mp * (l2 ** 2 + l1 * l2 * cq)
    m22 = I2 + m2 * c2 ** 2 + mp * l2 ** 2
    return np.array([[m11, m12], [m12, m22]])


def mass_from_jac(q1, q2):
    """同一个质量矩阵，按 M = Σ (m_i J_ciᵀ J_ci + I_i j_i j_iᵀ) 拼出来（15.8 节的证明）。"""
    I1, I2 = M1 * L1 ** 2 / 12, M2 * L2 ** 2 / 12
    J1, J2 = jac_c(q1, q2, 1), jac_c(q1, q2, 2)
    j1, j2 = np.array([[1.0, 0.0]]), np.array([[1.0, 1.0]])
    return M1 * J1.T @ J1 + I1 * j1.T @ j1 + M2 * J2.T @ J2 + I2 * j2.T @ j2


def gravity_hessian(m1=M1, m2=M2, l1=L1, l2=L2, g=G):
    """直立（角度从竖直向上量起）时重力势能在 θ = 0 处的黑塞矩阵的相反数 G（重力的“负刚度”）。
    V_g = g[(m1 c1 + m2 l1) cos θ1 + m2 c2 cos(θ1 + θ2)]，∂²V_g/∂θ² |₀ = −G。"""
    c1, c2 = l1 / 2, l2 / 2
    a = (m1 * c1 + m2 * l1 + m2 * c2) * g
    b = m2 * c2 * g
    return np.array([[a, b], [b, b]])


def potential(th1, th2, k1, k2, m1=M1, m2=M2, l1=L1, l2=L2, g=G):
    """直立双连杆的总势能：关节弹簧 + 重力（以 θ = 0 为零点）。"""
    c1, c2 = l1 / 2, l2 / 2
    vg = g * ((m1 * c1 + m2 * l1) * (np.cos(th1) - 1) + m2 * c2 * (np.cos(th1 + th2) - 1))
    return 0.5 * k1 * th1 ** 2 + 0.5 * k2 * th2 ** 2 + vg


def points(q1, q2, l1=L1, l2=L2):
    p1 = np.array([l1 * np.cos(q1), l1 * np.sin(q1)])
    return np.array([[0.0, 0.0], p1, p1 + l2 * np.array([np.cos(q1 + q2), np.sin(q1 + q2)])])
