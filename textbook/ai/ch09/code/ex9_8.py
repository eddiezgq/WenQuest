"""算例 9.8.1、9.8.2：连续批处理与投机解码。
（1）1000 个请求，各要生成 10—500 个词元（均匀分布），最多 32 条同时解码，每一步每条序列生成一个词元。
    静态批处理：32 个请求一批，等这批里最长的生成完再换下一批；连续批处理（于等 2022 年的 Orca）：每一步结束时，
    生成完的序列立即离开，空位马上由排队的请求补上。两者各要多少步，批中“有效”位置的比例。
（2）投机解码（列维坦等 2023；陈等 2023）：小的草稿模型先猜 k 个词元，大模型一次前向验证全部 k 个；
    设每个猜测被接受的概率为 α（彼此独立），一次验证平均产出 (1 − α^(k+1)) / (1 − α) 个词元（含验证时多给的一个）。
    用蒙特卡罗模拟核对这个公式；草稿模型每猜一个词元的耗时是大模型一步的 c 倍时，加速比为平均产出 ÷ (k·c + 1)。"""
import numpy as np

from bookout import out

rng = np.random.default_rng(98)
lens = rng.integers(10, 501, 1000)
slots = 32
static = sum(lens[i:i + slots].max() for i in range(0, len(lens), slots))
queue, active, steps = list(lens), [], 0
while queue or active:
    while queue and len(active) < slots:
        active.append(queue.pop(0))
    active = [x - 1 for x in active if x > 1]
    steps += 1
useful = lens.sum()


def expected(a, k):
    return (1 - a ** (k + 1)) / (1 - a)


def simulate(a, k, trials=200000):
    acc = rng.random((trials, k)) < a
    first_reject = np.where(acc.all(1), k, acc.argmin(1))
    return float(np.mean(first_reject + 1))             # 接受的个数 + 验证时多得的一个


a, k, c = 0.8, 4, 0.05
out(static=int(static), cont=steps, eff_static=100 * useful / (static * slots), eff_cont=100 * useful / (steps * slots),
    speed_cb=static / steps, E_formula=expected(a, k), E_sim=simulate(a, k), spec_speedup=expected(a, k) / (k * c + 1), a=a, k=k, c=c)
