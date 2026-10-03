"""算例 3.5.1～3.5.2：H100 的资源清点；存储层次各层的带宽估计。

寄存器堆的带宽按“每条 FP32 通道每周期做一次乘加、读 3 个 4 字节操作数”估计；共享内存按每个 SM 每周期 32 个存储体 × 4 字节估计；
都按最高加速频率，是理想的上限。
"""
from bookout import out
from gpus import GPUS, H100_SM

h, s = GPUS["h100"], H100_SM
n_sm, f = h["sm"], h["clock"]
lanes = n_sm * s["fp32_lanes"]
assert lanes == h["cores"]
reg_total = n_sm * s["regs"] * 4
smem_total = n_sm * s["smem_max"]
threads = n_sm * s["max_threads"]
warps = n_sm * s["max_warps"]
regs_per_thread_full = s["regs"] // s["max_threads"]           # 满员时每个线程能分到的寄存器

bw_reg = n_sm * s["fp32_lanes"] * 3 * 4 * f
bw_smem = n_sm * s["banks"] * 4 * f
bw_hbm = h["bw"]

out(n_sm=n_sm, lanes=lanes, part=s["partitions"], lanes_part=s["fp32_lanes"] // s["partitions"], clock_G=f / 1e9,
    reg_kB=s["regs"] * 4 / 1024, reg_total_MB=reg_total / 2 ** 20, smem_kB=s["smem_max"] / 1024, smem_total_MB=smem_total / 2 ** 20,
    l2_MB=h["l2"] / 2 ** 20, mem_GB=h["mem"] / 1e9, threads=threads, warps=warps, max_warps=s["max_warps"], max_threads=s["max_threads"],
    max_blocks=s["max_blocks"], regs_full=regs_per_thread_full, max_regs=s["max_regs_thread"],
    bw_reg_T=bw_reg / 1e12, bw_smem_T=bw_smem / 1e12, bw_hbm_T=bw_hbm / 1e12, r_reg=bw_reg / bw_hbm, r_smem=bw_smem / bw_hbm)
