"""算例 9.4.1：流水线并行的气泡。模型按层切成 p 段，放在 p 块 GPU 上；一个批切成 m 个微批依次流过。
（1）GPipe（黄等 2019）：先让 m 个微批都做完前向，再都做反向。设每段一个微批的前向用时 1、反向用时 2，
    一步的总时间是 (m + p − 1)·3，其中有效计算 m·3，空闲（气泡）占 (p − 1)/(m + p − 1)。逐个时刻模拟调度，与公式核对。
（2）1F1B（PipeDream-Flush 的做法）：一个前向、一个反向交替。气泡比例相同，但每块 GPU 同时保存激活值的微批最多 p 个（GPipe 要存 m 个）。
p = 8 时，m = 8、32、128 的气泡比例。"""
from bookout import out


def gpipe(p, m, f=1, b=2):
    """逐段模拟：第 s 段第 i 个微批的前向在 s−1 段完成它之后、且本段前一个微批的前向完成之后开始；反向从最后一段倒着来。"""
    F = [[0.0] * m for _ in range(p)]
    for s in range(p):
        for i in range(m):
            start = max(F[s - 1][i] if s else 0.0, F[s][i - 1] if i else 0.0)
            F[s][i] = start + f
    B = [[0.0] * m for _ in range(p)]
    t0 = max(F[s][m - 1] for s in range(p))           # 全部前向结束后再开始反向（同步的流水线）
    for s in reversed(range(p)):
        for i in range(m):
            start = max(B[s + 1][i] if s < p - 1 else t0, B[s][i - 1] if i else 0.0, F[s][m - 1])
            B[s][i] = start + b
    total = max(B[0])
    return total, 1 - m * (f + b) / total


r = {}
for m in (8, 32, 128):
    total, bub = gpipe(8, m)
    r[f"bub{m}"] = 100 * bub
    r[f"formula{m}"] = 100 * 7 / (m + 7)
    assert abs(bub - 7 / (m + 7)) < 1e-9
out(**r, p=8)
