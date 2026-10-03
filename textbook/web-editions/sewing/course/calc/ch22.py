"""第 22 章 自动化测试与持续迭代 —— 课程包数值题计算（数据取自教材 22.1、22.6、22.7、22.9 节）"""
from math import ceil, log
from scipy.stats import beta


def n_zero(R, C):
    return ceil(log(1 - C) / log(R))


def r_lower(n, x, C=0.95):
    return 0.0 if x >= n else 1 - beta.ppf(C, x + 1, n - x)


def n_with(R, C, x):
    n = x + 1
    while r_lower(n, x, C) < R:
        n += 1
    return n


def max_fail(n, R=0.995, C=0.95):
    x = -1
    while r_lower(n, x + 1, C) >= R:
        x += 1
    return x


def p_detect(p, n):
    return 1 - (1 - p) ** n


# 22.6.1 表 22-5
print("n_zero 99.5/95", n_zero(0.995, 0.95), " 99/95", n_zero(0.99, 0.95), " 99.5/90", n_zero(0.995, 0.90),
      " 99.9/90", n_zero(0.999, 0.90), " 99.9/95", n_zero(0.999, 0.95))
print("allow x=1,2,3 @99.5/95:", [n_with(0.995, 0.95, x) for x in (1, 2, 3)])
# 22.6.2
print("r_lower 1000, x=0..3:", [round(r_lower(1000, x), 4) for x in range(4)])
print("max_fail 1000:", max_fail(1000), " 1500:", max_fail(1500))
# 22.6.3 检出概率
print("detect p=0.012 n=250:", round(p_detect(0.012, 250), 3), " p=0.005 n=598:", round(p_detect(0.005, 598), 3),
      " p=0.17 n=10:", round(p_detect(0.17, 10), 3))
print("22.1: 4750 50次一次都看不到", round((1 - 0.012) ** 50, 3), " 0.012% 50次", round(p_detect(0.00012, 50), 4))
# 22.6.4 Cpk
print("Cpk Kp=200:", round((1 - 0.17) / (3 * 0.026), 1), " Kp=300:", round((1 - 0.92) / (3 * 0.079), 2))
# 习题复核
print("习题1 99/90 零失效", n_zero(0.99, 0.90), " 允许1次", n_with(0.99, 0.90, 1))
print("习题2 1500/3: 点估计", round(1 - 3 / 1500, 4), " 下限", round(r_lower(1500, 3), 4))
n = ceil(log(0.01) / log(0.99))
print("习题3 n", n, " 分钟", round(n * 3 / 60, 1))
print("习题4 Cpk", round((1 - 0.62) / (3 * 0.09), 2), " mu_max", round(1 - 4 * 0.09, 2))
print("习题5 轮数", ceil(log(40, 2)), " 分钟", ceil(log(40, 2)) * 16)
# 二分 23 个提交
print("二分 23 提交 轮数", ceil(log(23, 2)), " 每轮 16 min ->", ceil(log(23, 2)) * 16, "min")
# 剪线进刀角
for nn, t in ((850, 0.008), (300, 0.008), (667, 0.010), (514, 0.008), (1150, 0.008)):
    print(" 进刀角 n", nn, "t", t, "->", round(290 + 6 * nn * t, 1))
print("临界转速 t=10ms 进刀 330°:", round((330 - 290) / (6 * 0.010), 1))
# 每晚 HIL 预算
default = {"HIL-TRM-4000": 55, "HIL-POS-1": 2, "HIL-SOL": 10, "HIL-BT": 20, "HIL-FLT": 35, "HIL-XY": 45, "HIL-KN": 40}
print("默认 HIL", sum(default.values()))
new = dict(default); new.pop("HIL-TRM-4000"); new["HIL-TRM-SW"] = 80; new["HIL-POS-50"] = 6
print("调整后 HIL", sum(new.values()))
t226 = [80, 35, 45, 40, 20, 10, 6, 4]
print("表 22-6 合计", sum(t226))

# ---------- 课程题 ----------
# 测验：99%/95% 零失效
print("Q n_zero 99/95", n_zero(0.99, 0.95))
# 测验：1000 次 1 次失败下限
print("Q r_lower 1000,1", round(r_lower(1000, 1) * 100, 2))
# 测验：每晚 95% 把握抓住 p = 2% 的回归
print("Q 检出 p=2% 95%", ceil(log(0.05) / log(0.98)))
# 测验：Cpk
print("Q Cpk mu 0.40 sd 0.12", round((1 - 0.40) / (3 * 0.12), 2))
# 考试：99.9%/95% 允许 1 次
print("E 99.9/95 允许1", n_with(0.999, 0.95, 1))
# 考试：2000 次 x 次的最大允许
print("E max_fail 2000", max_fail(2000), " 3000", max_fail(3000))
# 考试：二分 60 个提交、每轮 3+13 min
print("E 二分 60", ceil(log(60, 2)), ceil(log(60, 2)) * 16)
# 作业：剪线 99.8%/90% 零失效 与 允许 1 次；4750 r/min p 1.2% 检出 99%
print("A n_zero 99.8/90", n_zero(0.998, 0.90), " 允许1", n_with(0.998, 0.90, 1))
print("A 99% 把握 p=1.2%", ceil(log(0.01) / log(1 - 0.012)), " 剪 3 s/次 分钟", round(ceil(log(0.01) / log(1 - 0.012)) * 3 / 60, 1))
print("A Cpk mu 0.55 sd 0.11", round((1 - 0.55) / 0.33, 2), " 0.30 sd 0.05", round((1 - 0.30) / 0.15, 2))
print("A r_lower 1200,1", round(r_lower(1200, 1), 4), " 1200,2", round(r_lower(1200, 2), 4), " max_fail 1200", max_fail(1200))
