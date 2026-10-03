"""算例 3.3.1～3.3.3：CPU 与 GPU 的峰值与带宽；利特尔定律：要用满带宽，路上要有多少数据。

式 (3.3.1)：利特尔定律 并发量 = 吞吐率 × 延迟；用于显存：在途字节数 = 带宽 β × 延迟 τ。
"""
from bookout import out
from gpus import CPU, GPUS, H100_LAT, H100_SM

h = GPUS["h100"]
P_cpu = CPU["cores"] * CPU["clock"] * CPU["flop_per_cycle"]
P_h = h["fp32"]
# 峰值与带宽之比
r_P = P_h / P_cpu
r_bw = h["bw"] / CPU["bw"]

# 算例 3.3.2：CPU：在途字节数与缓存行数
cpu_inflight = CPU["bw"] * CPU["lat"]
cpu_lines = cpu_inflight / CPU["line"]
cpu_lines_core = cpu_lines / CPU["cores"]

# 算例 3.3.3：H100：显存延迟按最高频率折算成周期；在途字节；每个 SM 要多少次“线程束读”（32 个线程各读 4 字节，共 128 字节）
tau = H100_LAT["hbm"]
tau_cyc = tau * h["clock"]
gpu_inflight = h["bw"] * tau
per_sm = gpu_inflight / h["sm"]
warp_loads = per_sm / 128
warps_max = H100_SM["max_warps"]
loads_per_warp = warp_loads / warps_max
# 每个 SM 每周期能从显存得到的字节（平均）
B_per_clk_sm = h["bw"] / h["sm"] / h["clock"]

# 一个线程（CPU 核与 GPU 的一条通道）的峰值，说明“单兵”差距
P_core = CPU["clock"] * CPU["flop_per_cycle"]
P_lane = 2 * h["clock"]

out(P16_T=h["fp16t"] / 1e12, r_P16=h["fp16t"] / P_cpu, tc_total=h["sm"] * H100_SM["tensor_cores"], P_cpu_T=P_cpu / 1e12, cpu_bw_G=CPU["bw"] / 1e9, P_h_T=P_h / 1e12, h_bw_T=h["bw"] / 1e12, r_P=r_P, r_bw=r_bw,
    cpu_lat_ns=CPU["lat"] * 1e9, cpu_inflight_kB=cpu_inflight / 1e3, cpu_lines=cpu_lines, cpu_lines_core=cpu_lines_core,
    tau_ns=tau * 1e9, tau_cyc=tau_cyc, clock_G=h["clock"] / 1e9, gpu_inflight_MB=gpu_inflight / 1e6, per_sm_kB=per_sm / 1e3,
    warp_loads=warp_loads, warps_max=warps_max, loads_per_warp=loads_per_warp, B_per_clk_sm=B_per_clk_sm,
    P_core_G=P_core / 1e9, P_lane_G=P_lane / 1e9, r_core_lane=P_core / P_lane, cores_h=h["cores"], cpu_cores=CPU["cores"])
