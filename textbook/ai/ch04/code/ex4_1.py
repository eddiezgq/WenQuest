"""算例 4.1.1：向量加法的数据量与启动配置；在几种 GPU 上按显存带宽估计的耗时下限（实测见 code/runs/run4_1）。

式 (4.1.1)：耗时下限 = 搬运的字节 / 显存带宽；向量加法每个元素读 8 字节、写 4 字节。
"""
from bookout import out
from gpus import GPUS

n = 2 ** 26
block = 256
grid = (n + block - 1) // block
bytes_moved = 3 * 4 * n
flops = n
I = flops / bytes_moved
t = {k: bytes_moved / GPUS[k]["bw"] for k in ("a10", "rtx4090", "h100")}
t_compute_a10 = flops / GPUS["a10"]["fp32"]
out(n=n, n_e="2^{26}", block=block, grid=grid, threads=grid * block, MiB=4 * n / 2 ** 20, MB=bytes_moved / 1e6, I=I,
    t_a10_ms=t["a10"] * 1e3, t_4090_ms=t["rtx4090"] * 1e3, t_h100_ms=t["h100"] * 1e3, bw_a10=GPUS["a10"]["bw"] / 1e9,
    bw_4090=GPUS["rtx4090"]["bw"] / 1e9, bw_h100=GPUS["h100"]["bw"] / 1e9, t_comp_a10_us=t_compute_a10 * 1e6,
    ratio=t["a10"] / t_compute_a10)
