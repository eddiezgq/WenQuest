"""2.7 节与实验 2.7 共用的数据：数字工厂减速器车间出厂检测的六个项目、过程的均值与标准差、
三种典型故障的“特征方向”、八份检测记录。数据按车间检测项目编制（模拟数据），只用于教学。"""
import numpy as np

ITEMS = ["输出轴直径偏差", "齿圈径向跳动", "空载噪声", "温升", "振动速度", "回差"]
ITEMS_EN = ["shaft diameter deviation", "gear runout", "no-load noise", "temperature rise", "vibration velocity", "backlash"]
UNITS = ["μm", "μm", "dB(A)", "K", "mm/s", "arcmin"]
MU = np.array([0.0, 12.0, 60.0, 15.0, 1.2, 3.0])        # 过程均值
SIGMA = np.array([3.0, 3.0, 1.5, 2.0, 0.25, 0.4])       # 过程标准差
# 故障的特征方向（标准化后各项偏离的相对大小）
FAULTS = {"轴承磨损": np.array([0.0, 0.2, 1.0, 0.8, 1.0, 0.1]),
          "齿轮偏心": np.array([0.0, 1.0, 0.6, 0.1, 0.7, 0.5]),
          "装配过紧": np.array([0.0, 0.0, 0.5, 1.0, 0.2, -0.8])}
FAULTS_EN = {"轴承磨损": "bearing wear", "齿轮偏心": "gear eccentricity", "装配过紧": "over-tight assembly"}
# 八份检测记录（原始单位）
RECORDS = np.array([
    [1.0, 13.0, 60.5, 15.5, 1.25, 3.1],     # 1 正常
    [-2.0, 12.5, 63.6, 18.6, 1.95, 3.1],    # 2
    [0.5, 19.5, 62.0, 15.6, 1.75, 3.9],     # 3
    [3.5, 11.5, 61.2, 19.8, 1.35, 2.3],     # 4
    [-1.0, 11.0, 59.4, 14.2, 1.10, 2.9],    # 5 正常
    [0.0, 13.5, 64.4, 19.0, 2.10, 3.3],     # 6
    [-0.5, 18.0, 61.8, 15.0, 1.60, 3.6],    # 7
    [2.5, 12.0, 60.9, 17.4, 1.30, 2.6],     # 8
])


def z(x):
    return (np.asarray(x) - MU) / SIGMA


def cos(u, v):
    u, v = np.asarray(u, float), np.asarray(v, float)
    return float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)))


if __name__ == "__main__":
    from bookout import out
    out(check=cos(z(RECORDS[1]), FAULTS["轴承磨损"]))
