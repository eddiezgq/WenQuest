"""算例 6.6.1：A10 的分层屋顶线。三个屋顶（单精度、TF32、半精度张量核心）与两层斜坡：显存（600 GB/s）与共享内存
（每个 SM 每周期 128 字节 × SM 数 × 计算单精度峰值所用的频率）。各层的屋脊 = 峰值 ÷ 该层带宽。"""
from _ch6 import A10
from bookout import out

smem_bw = 128 * A10["sm"] * A10["clock"]
# 第 5 章各版本读共享内存的计算强度（模型，按每次访问 128 字节；见算例 5.8.2、5.9.1、5.9.3）：
# 一个线程束每做一条乘加指令（32 次乘加，64 FLOP）读共享内存几次
acc = {"tiled": 2.0, "regtile": 40 / 64, "vec": 16 / 64}
I_smem = {k: 64 / (v * 128) for k, v in acc.items()}
bound = {k: min(A10["fp32"], smem_bw * I) / A10["fp32"] for k, I in I_smem.items()}
out(**{f"Is_{k}": v for k, v in I_smem.items()}, **{f"bound_{k}": 100 * v for k, v in bound.items()},
    fp32_TF=A10["fp32"] / 1e12, fp16_TF=A10["fp16t"] / 1e12, dram_GBs=A10["bw"] / 1e9, smem_TBs=smem_bw / 1e12,
    ridge_dram32=A10["fp32"] / A10["bw"], ridge_smem32=A10["fp32"] / smem_bw, ridge_dram16=A10["fp16t"] / A10["bw"],
    ridge_smem16=A10["fp16t"] / smem_bw, clock_GHz=A10["clock"] / 1e9)
