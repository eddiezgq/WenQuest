"""算例 3.2.1～3.2.3：阿姆达尔定律与古斯塔夫森定律。

式 (3.2.1)：S(p) = 1 / (f + (1 − f)/p)，p → ∞ 时 S → 1/f；
式 (3.2.3)：规模扩大的加速比 S'(p) = f + (1 − f) p = p − f (p − 1)（f 为并行运行时串行部分所占的比例）。
"""
from bookout import out
from gpus import GPUS


def amdahl(f, p):
    return 1 / (f + (1 - f) / p)


def gustafson(f, p):
    return f + (1 - f) * p


p_h = GPUS["h100"]["cores"]
rows = {f: (amdahl(f, p_h), 1 / f) for f in (0.05, 0.01, 0.001)}

# 算例 3.2.2：一个训练步原来全在 CPU 上：数据读取与预处理、Python 调度占 5%，其余 95% 是张量运算。
# 张量运算搬到 GPU 上快 50 倍：整体只快多少？要整体快 40 倍，串行部分要压到多少？
f_step, s_gpu = 0.05, 50
S_step = amdahl(f_step, s_gpu)
target = 40
f_need = (1 / target - 1 / s_gpu) / (1 - 1 / s_gpu)             # 由 1/target = f + (1 − f)/s 解出 f
# 换一种做法：把数据预处理也放到 GPU 上，或与 GPU 计算重叠（流水线）——串行部分被“藏”起来，只剩 0.5%
S_overlap = amdahl(0.005, s_gpu)

# 算例 3.2.3：古斯塔夫森：8 块 GPU 上每块 GPU 的工作量不变，串行部分占并行运行时间的 5%
p8 = 8
S_g8 = gustafson(0.05, p8)
S_a8 = amdahl(0.05, p8)

out(p_h=p_h, S05=rows[0.05][0], L05=rows[0.05][1], S01=rows[0.01][0], L01=rows[0.01][1], S001=rows[0.001][0], L001=rows[0.001][1],
    f_step_pct=f_step * 100, s_gpu=s_gpu, S_step=S_step, target=target, f_need_pct=f_need * 100, S_overlap=S_overlap,
    p8=p8, S_g8=S_g8, S_a8=S_a8)
