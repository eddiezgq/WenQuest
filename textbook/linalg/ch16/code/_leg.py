"""本章共用：Go2 一条腿的竖直方向质量–弹簧–阻尼链（16.4 节、实验 16.4）。以下划线开头，构建时不单独运行。
质量取自 Unitree Go2 的 MuJoCo 模型（MuJoCo Menagerie，零件库 B-LEG-GO2）：躯干 6.921 kg 的四分之一加髋部 0.678 kg、
大腿 1.152 kg、小腿（含足）0.2414 kg。刚度、阻尼是示意值：k₁ 为髋–大腿间（髋关节伺服的等效竖直刚度），k₂ 为膝关节，
k₃ 为足底橡胶与地面的接触刚度；c 同理。坐标 q 为三个质量相对静平衡位置的竖直位移（向上为正）。
链的顺序（自上而下）：躯干+髋 —k₁— 大腿 —k₂— 小腿+足 —k₃— 地面。"""
import numpy as np

MASS = np.array([6.921 / 4 + 0.678, 1.152, 0.2414])
K3 = np.array([3000.0, 2000.0, 2.0e4])      # N/m
C3 = np.array([30.0, 20.0, 50.0])           # N·s/m


def chain(k):
    """上端自由、下端接地的三质量链的刚度（或阻尼）矩阵。"""
    k1, k2, k3 = k
    return np.array([[k1, -k1, 0.0], [-k1, k1 + k2, -k2], [0.0, -k2, k2 + k3]])


def state_matrix(M, K, C):
    n = len(M)
    Mi = np.linalg.inv(M)
    return np.block([[np.zeros((n, n)), np.eye(n)], [-Mi @ K, -Mi @ C]])
