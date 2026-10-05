"""本章共用：平面两连杆机械臂的雅可比矩阵与末端刚度（与网页实验 14.2 相同）。以下划线开头，构建时不单独运行。
关节刚度 K_q = diag(k₁, k₂)（伺服或减速器的扭转刚度，N·m/rad），末端柔度 C = J K_q⁻¹ Jᵀ（m/N），末端刚度 K_x = C⁻¹（N/m）。"""
import numpy as np

L1, L2 = 0.40, 0.30


def jac(q1, q2, l1=L1, l2=L2):
    a1, a2 = q1, q1 + q2
    return np.array([[-l1 * np.sin(a1) - l2 * np.sin(a2), -l2 * np.sin(a2)], [l1 * np.cos(a1) + l2 * np.cos(a2), l2 * np.cos(a2)]])


def compliance(q1, q2, k1, k2):
    J = jac(q1, q2)
    return J @ np.diag([1 / k1, 1 / k2]) @ J.T


def points(q1, q2, l1=L1, l2=L2):
    p1 = np.array([l1 * np.cos(q1), l1 * np.sin(q1)])
    return np.array([[0.0, 0.0], p1, p1 + l2 * np.array([np.cos(q1 + q2), np.sin(q1 + q2)])])
