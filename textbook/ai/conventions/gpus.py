"""《人工智能》跨章共用的硬件规格表（第 3 章起使用；第 1、2 章的规格在各自的 _ch1.py、ex2_10.py 中，数值与此一致）。

每个数都写明出处。峰值算力按 NVIDIA 公布的数，张量核心一律取稠密（不计 2:4 稀疏）的数。
GPU 的 FP32 峰值 = FP32 核心数 × 2（一次乘加）× 频率，表中的 clock 是厂商计算这一峰值所用的频率（多数为最高加速频率；
GTX 580 为着色器频率，K40 为基础频率），可以用它核对峰值（程序 3.4.1）。H100 的张量核心峰值所用的频率更低（见下）。
"""

# 名称、年份、架构、SM 数、FP32 核心数、计算 FP32 峰值所用的频率（Hz）、FP32 峰值、FP16/BF16 张量核心峰值（稠密，没有张量核心的写 None）、
# 显存带宽（B/s）、显存容量（B）、L2 缓存（B）
GPUS = {
    # GeForce GTX 580（Fermi GF110，2010 年 11 月）：512 个 CUDA 核心，着色器频率 1544 MHz，显存带宽 192.4 GB/s，
    # L2 768 KB；公版显存 1.5 GB，AlexNet 用的是 3 GB 版本，表中取 3 GB（NVIDIA Fermi 架构白皮书 2009；GTX 580 产品资料；
    # Krizhevsky 等 2012）
    "gtx580": dict(name="GTX 580", year=2010, arch="Fermi", sm=16, cores=512, clock=1544e6, fp32=1.581e12, fp16t=None,
                   bw=192.4e9, mem=3e9, l2=768 * 1024),
    # Tesla K40（Kepler GK110B，2013）：15 个 SMX、2880 个核心；单精度 4.29 TFLOP/s 按基础频率 745 MHz 计，288 GB/s，12 GB，
    # L2 1.5 MB（NVIDIA Tesla K40 数据手册；Kepler GK110 白皮书）
    "k40": dict(name="Tesla K40", year=2013, arch="Kepler", sm=15, cores=2880, clock=745e6, fp32=4.29e12, fp16t=None,
                bw=288e9, mem=12e9, l2=1.5 * 2 ** 20),
    # Tesla P100 SXM2（Pascal，2016）：56 个 SM、3584 个核心、1480 MHz；FP32 10.6、FP16 21.2 TFLOP/s（非张量核心），
    # HBM2 732 GB/s，16 GB，L2 4 MB（NVIDIA Tesla P100 白皮书 2016）
    "p100": dict(name="P100", year=2016, arch="Pascal", sm=56, cores=3584, clock=1480e6, fp32=10.6e12, fp16t=None,
                 bw=732e9, mem=16e9, l2=4 * 2 ** 20),
    # Tesla V100 SXM2（Volta，2017）：80 个 SM、5120 个核心、1530 MHz；FP32 15.7、张量核心 125 TFLOP/s，HBM2 900 GB/s，
    # 2017 年发布时 16 GB（32 GB 版 2018 年推出），L2 6 MB（NVIDIA Tesla V100 GPU 架构白皮书 2017）
    "v100": dict(name="V100", year=2017, arch="Volta", sm=80, cores=5120, clock=1530e6, fp32=15.7e12, fp16t=125e12,
                 bw=900e9, mem=16e9, l2=6 * 2 ** 20),
    # A100 SXM 80 GB（Ampere，2020）：108 个 SM、6912 个核心、1410 MHz；FP32 19.5、FP16 张量核心 312 TFLOP/s（稠密），
    # HBM2e 2039 GB/s，L2 40 MB（NVIDIA A100 架构白皮书 2020；A100 数据手册）
    "a100": dict(name="A100", year=2020, arch="Ampere", sm=108, cores=6912, clock=1410e6, fp32=19.5e12, fp16t=312e12,
                 bw=2039e9, mem=80e9, l2=40 * 2 ** 20),
    # H100 SXM5 80 GB（Hopper，2022）：132 个 SM、16 896 个核心、最高加速频率 1980 MHz；FP32 67、FP16 张量核心 989.4 TFLOP/s
    # （稠密，计入稀疏为 1979；按每个 SM 每周期 4096 次稠密半精度运算反推，所用频率约 1.83 GHz，低于 FP32 峰值所用的 1.98 GHz），
    # HBM3 3.35 TB/s，L2 50 MB（NVIDIA H100 架构白皮书 2022；H100 数据手册）
    "h100": dict(name="H100", year=2022, arch="Hopper", sm=132, cores=16896, clock=1980e6, fp32=67e12, fp16t=989.4e12,
                 bw=3.35e12, mem=80e9, l2=50 * 2 ** 20),
    # GeForce RTX 4090（Ada Lovelace，2022）：128 个 SM、16 384 个核心、2520 MHz；FP32 82.6 TFLOP/s；FP16 张量核心
    # （FP32 累加）165.2 TFLOP/s（稠密），GDDR6X 1008 GB/s，24 GB，L2 72 MB（NVIDIA Ada GPU 架构白皮书 2022）
    "rtx4090": dict(name="RTX 4090", year=2022, arch="Ada", sm=128, cores=16384, clock=2520e6, fp32=82.6e12, fp16t=165.2e12,
                    bw=1008e9, mem=24e9, l2=72 * 2 ** 20),
    # B200（Blackwell，HGX B200，2024 年发布）：FP32 75 TFLOP/s；FP16/BF16 张量核心 4.5 PFLOP/s 为计入稀疏的数，稠密为一半
    # 2.25 PFLOP/s；HBM3e 180 GB、7.7 TB/s（NVIDIA HGX B200 数据手册，截至 2026 年 10 月）。SM 数、频率未在数据手册中给出。
    "b200": dict(name="B200", year=2024, arch="Blackwell", sm=None, cores=None, clock=None, fp32=75e12, fp16t=2.25e15,
                 bw=7.7e12, mem=180e9, l2=None),
}

# H100（计算能力 9.0）每个 SM 的资源（H100 架构白皮书表 3；CUDA C++ Programming Guide，“Compute Capabilities”）
H100_SM = dict(
    partitions=4,                 # 4 个处理块，各有 1 个线程束调度器、32 条 FP32 通道、1 个张量核心、16 384 个 32 位寄存器
    fp32_lanes=128,
    tensor_cores=4,
    regs=65536,                   # 32 位寄存器，共 256 KB
    max_regs_thread=255,
    reg_unit=256,                 # 寄存器按线程束分配，单位 256 个
    l1_smem=256 * 1024,           # L1 与共享内存合计
    smem_max=228 * 1024,          # 每个 SM 共享内存最多配置为 228 KB
    smem_block_max=227 * 1024,    # 每个线程块最多 227 KB
    smem_reserved=1024,           # 每个线程块由系统保留 1 KB
    max_warps=64, max_threads=2048, max_blocks=32, warp=32, banks=32,
)

# 访问延迟（实测，无负载的指针追逐；带宽用满时延迟会更高）：H100 上 L2 命中约 145 ns，显存（HBM3）约 353 ns
# （S. Manjunath、R. Ramachandra，Concurrency Response of Plain Global Loads on the NVIDIA H100，arXiv:2608.15764，2026）
H100_LAT = dict(l2=145e-9, hbm=353e-9)

# 代表性的服务器 CPU（与第 1 章 _ch1.py 中 CPU 相同的教学假设，不对应某一型号）：64 核，3.0 GHz，每核每周期 64 FLOP（FP32），
# 8 通道 DDR5-4800（307.2 GB/s）；访问内存的延迟取 100 ns（服务器 CPU 的常见量级，作估算用）
CPU = dict(cores=64, clock=3.0e9, flop_per_cycle=64, bw=8 * 4800e6 * 8, lat=100e-9, line=64)
