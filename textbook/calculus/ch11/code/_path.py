"""第 10、11 章共用：AGV 换道路径 y(x)（横移 d，纵向长度 L）及其一、二阶导数。以下划线开头，构建时不单独运行。"""
import math

A_LAT = 1.0          # 允许的侧向加速度 m/s²（保证货物不滑、小车不侧翻，取保守值）
B_TRACK = 0.5        # 差速 AGV 的轮距 m（与 8.3 节习题一致）


def lane(kind, d, L):
    """返回 (y, y′, y″) 三个函数。kind：cubic 三次，cos 余弦，quintic 五次。"""
    if kind == "cubic":
        return (lambda x: d * (3 * (x / L) ** 2 - 2 * (x / L) ** 3),
                lambda x: d / L * (6 * (x / L) - 6 * (x / L) ** 2),
                lambda x: d / L ** 2 * (6 - 12 * (x / L)))
    if kind == "cos":
        return (lambda x: d * (1 - math.cos(math.pi * x / L)) / 2,
                lambda x: d * math.pi / (2 * L) * math.sin(math.pi * x / L),
                lambda x: d * math.pi ** 2 / (2 * L * L) * math.cos(math.pi * x / L))
    return (lambda x: d * (10 * (x / L) ** 3 - 15 * (x / L) ** 4 + 6 * (x / L) ** 5),
            lambda x: d / L * (30 * (x / L) ** 2 - 60 * (x / L) ** 3 + 30 * (x / L) ** 4),
            lambda x: d / L ** 2 * (60 * (x / L) - 180 * (x / L) ** 2 + 120 * (x / L) ** 3))


def curvature(yp, ypp, x):
    return abs(ypp(x)) / (1 + yp(x) ** 2) ** 1.5
