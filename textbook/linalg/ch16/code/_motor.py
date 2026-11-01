"""本章共用：伺服电机的两节点热模型（16.1、16.2 节）。以下划线开头，构建时不单独运行。
状态 x = (绕组温升, 外壳温升)（K，相对环境温度）。绕组热容 C_w = 50 J/K，外壳热容 C_h = 500 J/K，
绕组到外壳的热阻 R_wh = 0.5 K/W，外壳到环境的热阻 R_ha = 1.0 K/W，铜损功率 P（W）加在绕组上：
    C_w ẋ_w = −(x_w − x_h)/R_wh + P,   C_h ẋ_h = (x_w − x_h)/R_wh − x_h/R_ha。
写成 ẋ = A x + b P。"""
import numpy as np

CW, CH, RWH, RHA = 50.0, 500.0, 0.5, 1.0
A = np.array([[-1 / (CW * RWH), 1 / (CW * RWH)],
              [1 / (CH * RWH), -1 / (CH * RWH) - 1 / (CH * RHA)]])
B = np.array([1 / CW, 0.0])
