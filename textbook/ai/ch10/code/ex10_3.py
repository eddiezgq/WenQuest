"""算例 10.3.1—10.3.2：立方单元上的矩阵乘法与三段流水（10.3 节）。

昇腾的 AI Core 里，矩阵乘法由立方单元完成：一次 16×16×16 的半精度矩阵乘累加（CANN 文档：“每次执行可以完成两个
16×16 的 float16 矩阵相乘”），结果在 L0C 中按单精度累加。数据要先从显存（Global Memory）搬进片上缓冲，再算，再搬出去——
Ascend C 的程序写成 CopyIn → Compute → CopyOut 三段，各段用队列串起来，不同数据块的三段重叠进行。

（1）一个 256×256×256 的半精度矩阵乘法：要多少次立方指令；按 16×16 分块时，每块输出要读多少数据，
    整个计算的片上读写与显存读写各多少——与第 5 章分块矩阵乘法的账（算例 5.8.1）形式完全相同，
    只是“一次乘加”换成了“一次 16×16×16 的矩阵乘加”。
（2）三段流水：n 个数据块、每段耗时相同时，总时间是 (n + 2) 段而不是 3n 段；
    与流水线并行的气泡公式 (9.4.1) 是同一回事（这里的“段”是搬入、计算、搬出）。
"""
from _ch10 import CUBE
from bookout import out

M = N = K = 256
m, n, k = CUBE["m"], CUBE["n"], CUBE["k"]
v = {"M": M, "m": m, "k": k}

# ---------- （1）立方指令的次数与数据量
v["cube_insts"] = (M // m) * (N // n) * (K // k)          # 每条做 m·n·k 次乘加
v["flop"] = 2 * M * N * K
v["flop_M"] = v["flop"] / 1e6
v["flop_per_inst"] = 2 * m * n * k
assert v["cube_insts"] * v["flop_per_inst"] == v["flop"]

# 按 16×16 的输出块算：每块要读 A 的 16×K 与 B 的 K×16（半精度 2 字节）
v["per_out_B"] = (m * K + K * n) * 2
v["out_tiles"] = (M // m) * (N // n)
v["read_naive_MB"] = v["out_tiles"] * v["per_out_B"] / 1e6        # 每个输出块各自去显存读
# 把 A、B 整个放进片上缓冲（L1）再算：显存只读一遍，写一遍结果
v["read_once_MB"] = (M * K + K * N) * 2 / 1e6
v["write_MB"] = M * N * 4 / 1e6                                    # L0C 是单精度累加，搬出时按 4 字节算
v["c_KB_note"] = "L0C 里一个 16×16 的输出块只占 1 KB"
v["save"] = v["read_naive_MB"] / v["read_once_MB"]
v["ai_once"] = v["flop"] / ((M * K + K * N) * 2 + M * N * 4)       # 计算强度（FLOP/B）
v["ab_KB"] = (M * K + K * N) * 2 / 1024                            # A、B 两块一起占多少片上空间
v["c_KB"] = m * n * 4 / 1024                                       # 一个输出块在 L0C 里占多少

# ---------- （2）三段流水：CopyIn → Compute → CopyOut
def pipeline(n_tiles: int, dur: tuple = (1, 1, 1)) -> int:
    """各段耗时为 dur、不同块的各段可重叠时，n 个块流完要多少时间：sum(dur) + (n − 1)·max(dur)。
    各段耗时相同时就是 n + 2（与式 (9.4.1) 同源）；最慢的一段决定节拍（9.4.3 节）。"""
    return sum(dur) + (n_tiles - 1) * max(dur)


for n_tiles in (1, 4, 16, 64):
    v[f"pipe_{n_tiles}"] = pipeline(n_tiles)
    v[f"serial_{n_tiles}"] = 3 * n_tiles
    v[f"speed_{n_tiles}"] = 3 * n_tiles / pipeline(n_tiles)
v["pipe_limit"] = 3.0                                              # 块数很多时趋于 3 倍
v["bubble_16"] = (3 - 1) / pipeline(16) * 100                      # 气泡占比（%），与式 (9.4.1) 一致

# 逐个时刻模拟一遍，核对公式（搬入、计算、搬出各一个单元，同一块的三段必须依次进行）
def simulate(n_tiles: int, dur: tuple = (1, 1, 1)) -> int:
    """逐个时刻排一遍：三个单元各自串行，同一块的三段依次进行，能早就早地开始。返回最后一块搬完的时刻。"""
    free = [0, 0, 0]                                               # 三个单元各自下一次空闲的时刻
    done = 0
    for _ in range(n_tiles):
        t = 0
        for s in range(3):
            t = max(t, free[s])                                    # 等这个单元空出来
            free[s] = t + dur[s]
            t += dur[s]
        done = max(done, t)
    return done


assert all(simulate(n) == pipeline(n) for n in (1, 4, 16, 64)), "模拟与公式不符"
assert all(simulate(n, (1, 2, 1)) == 2 * n + 2 for n in (1, 4, 16, 64)), "计算段慢一倍时应为 2n + 2（习题 10.3.3）"
v["slow_16"] = simulate(16, (1, 2, 1))                             # 计算段慢一倍：16 块要多少段
v["sim_ok"] = True

out(**v)
