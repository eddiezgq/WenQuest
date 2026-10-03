"""算例 3.7.1～3.7.3：延迟隐藏（GPU 执行模拟器的 Python 参考版 _gpusim.py，部分 ①）与占用率的计算。

式 (3.7.1)：一个调度器带 n 个线程束、每次读显存后做 k 条算术指令、延迟 L 个周期时，发射利用率
  U ≈ min(1, n (k+1) / (L + k))；要用满需要 n ≥ (L + k)/(k + 1) 个线程束。
式 (3.7.2)：带宽的限制：每个调度器平均每 g 个周期才能读一次（一次 128 字节），U ≤ (k + 1)/g。
式 (3.7.3)：占用率 = 每个 SM 常驻的线程束数 / 64，常驻的线程块数受线程数、寄存器、共享内存、线程块数四项限制，取最小。
"""
import math

from _gpusim import little, schedule
from bookout import out
from gpus import GPUS, H100_LAT, H100_SM

h, s = GPUS["h100"], H100_SM
L_meas = H100_LAT["hbm"] * h["clock"]                         # 实测延迟折算的周期数（约 699）
L = 700                                                        # 取整为 700，与实验 3.6 一致
assert abs(L - L_meas) < 2
per_sched = s["max_warps"] // s["partitions"]                 # 每个调度器最多 16 个线程束
g = 128 / (h["bw"] / (h["sm"] * s["partitions"] * h["clock"]))  # 每个调度器平均多少个周期能分到 128 字节
gap = round(g)

# 算例 3.7.1：k = 4，n = 1 … 16（不计带宽限制）
CY = 200000                                                    # 统计窗口取长，减小量化误差
sim4 = {n: schedule(warps=n, latency=L, k=4, cycles=CY)["util"] for n in (1, 4, 16)}
est4 = {n: little(n, 4, L) for n in (1, 4, 16)}
need4 = math.ceil((L + 4) / 5)
# k 要多大，16 个线程束才够
k_need = next(k for k in range(1, 200) if per_sched * (k + 1) >= L + k)
sim_kneed = schedule(warps=per_sched, latency=L, k=k_need, cycles=CY)["util"]
lrr_kneed = schedule(warps=per_sched, latency=L, k=k_need, policy="lrr", cycles=CY)["util"]

# 算例 3.7.2：加上带宽限制
sim_bw4 = schedule(warps=per_sched, latency=L, k=4, gap=gap, cycles=CY)["util"]
est_bw4 = little(per_sched, 4, L, gap)
sim_bwk = schedule(warps=per_sched, latency=L, k=k_need, gap=gap, cycles=CY)["util"]
# 每次读 4 字节 × 32 个线程，后面 k 条 FP32 乘加：计算强度 = 32 × 2k / 128 = k/2 FLOP/B；平衡点 P/β
I_k4 = 32 * 2 * 4 / 128
I_kneed = 32 * 2 * k_need / 128
bal32 = h["fp32"] / h["bw"]


# 算例 3.7.3：占用率
def occupancy(threads, regs, smem):
    wpb = math.ceil(threads / s["warp"])
    lim_threads = s["max_threads"] // threads
    regs_warp = math.ceil(regs * s["warp"] / s["reg_unit"]) * s["reg_unit"]
    per_part = s["regs"] // s["partitions"]                   # 寄存器堆分属 4 个处理块，每块 16 384 个，分别取整
    lim_regs = (per_part // regs_warp) * s["partitions"] // wpb
    lim_smem = s["smem_max"] // (smem + s["smem_reserved"]) if smem else s["max_blocks"]
    blocks = min(lim_threads, lim_regs, lim_smem, s["max_blocks"])
    return dict(t=lim_threads, r=lim_regs, m=lim_smem, blocks=blocks, warps=blocks * wpb, occ=blocks * wpb / s["max_warps"])


A = occupancy(256, 32, 0)
B = occupancy(256, 64, 0)
C = occupancy(128, 40, 48 * 1024)
assert A["occ"] == 1 and B["occ"] == 0.5 and C["occ"] == 0.25

out(L_meas=L_meas, L=L, per_sched=per_sched, g=g, gap=gap, s1=sim4[1] * 100, e1=est4[1] * 100, s4=sim4[4] * 100, e4=est4[4] * 100,
    s16=sim4[16] * 100, e16=est4[16] * 100, need4=need4, k_need=k_need, sim_kneed=sim_kneed * 100, lrr_kneed=lrr_kneed * 100,
    sim_bw4=sim_bw4 * 100, est_bw4=est_bw4 * 100, sim_bwk=sim_bwk * 100, I_k4=I_k4, I_kneed=I_kneed, bal32=bal32,
    A_t=A["t"], A_r=A["r"], A_w=A["warps"], A_occ=A["occ"] * 100, B_r=B["r"], B_w=B["warps"], B_occ=B["occ"] * 100,
    C_t=C["t"], C_r=C["r"], C_m=C["m"], C_w=C["warps"], C_occ=C["occ"] * 100)
