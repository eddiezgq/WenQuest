"""本章共用：一只 15 个关节的机器人手（拟人手）的抓取姿态（模拟数据）。以下划线开头，构建时不单独运行。

关节顺序：拇指（腕掌旋转、掌指、指间），食指、中指、无名指、小指（各为掌指、近节指间、远节指间），单位为度。
姿态由三个“协同”（同时变化的关节组合）叠加而成，再加上每个关节约 6° 的随机偏差：
  协同 1：五指一起握紧（强力抓握的开合）；
  协同 2：拇指对掌、食指和中指弯曲，无名指和小指伸直（捏取）；
  协同 3：食指单独伸出，其余手指略弯。
"""
import numpy as np

JOINTS = ["拇指旋转", "拇指掌指", "拇指指间",
          "食指掌指", "食指近节", "食指远节", "中指掌指", "中指近节", "中指远节",
          "无名指掌指", "无名指近节", "无名指远节", "小指掌指", "小指近节", "小指远节"]
JOINTS_EN = ["thumb rot.", "thumb MCP", "thumb IP",
             "index MCP", "index PIP", "index DIP", "middle MCP", "middle PIP", "middle DIP",
             "ring MCP", "ring PIP", "ring DIP", "little MCP", "little PIP", "little DIP"]
OPEN = np.array([20, 10, 10, 15, 20, 10, 15, 20, 10, 15, 20, 10, 15, 20, 10], float)    # 张开的手
SYN = np.array([
    [15, 20, 25, 30, 40, 25, 30, 40, 25, 30, 40, 25, 30, 40, 25],
    [30, 10, -10, 25, 15, -10, 15, 10, 0, -15, -20, -10, -20, -25, -15],
    [5, -5, 0, -20, -15, -5, 5, 5, 5, 15, 10, 5, 15, 10, 5],
], float).T                                                                              # 15×3，每列一个协同（度/单位得分）
SCORE_SD = np.array([0.55, 0.8, 0.9])
NOISE_DEG = 6.0


def postures(n=120, seed=1998):
    rng = np.random.default_rng(seed)
    t = rng.standard_normal((n, 3)) * SCORE_SD
    return OPEN + t @ SYN.T + NOISE_DEG * rng.standard_normal((n, 15))
