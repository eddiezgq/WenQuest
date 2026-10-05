"""第 10 章共用的数据：各家人工智能加速器的规格，以及达芬奇架构（昇腾）的结构参数。

**写法的三条纪律**（与资料卡 `docs/教材/人工智能/参考/第10章_加速器资料_2026-10.md` 一致）：
1. 峰值算力一律取**稠密**值（不计 2:4 稀疏）并注明精度。厂商材料常印稀疏值，是稠密值的 2 倍
   （如 H100 的“FP16 1979 TFLOP/s”是稀疏值，稠密为 989.4）。
2. 厂商没有公布的数写 None，正文据此写“厂商未公布”，不填第三方估算。国产加速器多只公布显存容量与
   一个不带精度的算力数字，这一列的 None 本身就是本章要读者看见的事实。
3. 路线图上的型号（2027 年及以后）不进这张表：它们是发布会公布的目标，不是可以买到、可以实测的产品。

每条的出处写在它上面的注释里，日期为查阅日期。截至 2026 年 10 月。
"""

# 字段：名称、英文名（英文版用）、厂商、年份、BF16/FP16 稠密峰值（FLOP/s）、FP8 或 INT8 稠密峰值（FLOP/s 或 OP/s，注明在注释里）、
#       显存容量（B）、显存带宽（B/s）、单卡对外互联带宽（B/s，双向合计）、功耗（W）、片上并行单元数与名称
ACC = {
    # NVIDIA A100 SXM 80 GB、H100 SXM：见 conventions/gpus.py（本章只重复互联与功耗，便于与各家对照）
    # NVIDIA A100 数据手册（2020）：FP16 张量核心 312 TFLOP/s 稠密，HBM2e 2039 GB/s，NVLink 3 600 GB/s，400 W
    "a100": dict(name="NVIDIA A100 SXM", en="NVIDIA A100 SXM", vendor="NVIDIA", year=2020, bf16=312e12, low=624e12, mem=80e9,
                 bw=2039e9, link=600e9, tdp=400, units=108, unit_name="SM"),
    # NVIDIA H100 架构白皮书与数据手册（2022）：FP16 989.4、FP8 1979 TFLOP/s（均稠密），HBM3 3.35 TB/s，
    # NVLink 4 900 GB/s，700 W，132 个 SM
    "h100": dict(name="NVIDIA H100 SXM", en="NVIDIA H100 SXM", vendor="NVIDIA", year=2022, bf16=989.4e12, low=1979e12, mem=80e9,
                 bw=3.35e12, link=900e9, tdp=700, units=132, unit_name="SM"),
    # AMD Instinct MI300X：ROCm 微架构文档（docs-6.3.1，conceptual/gpu-arch/mi300）：每个计算单元每周期 2048 次
    # 半精度运算 → FP16 1307.4 TFLOP/s 稠密，FP8 2614.9；HBM3 192 GB、5.3 TB/s；Infinity Fabric 7×128 GB/s；
    # 750 W；304 个计算单元（8 个 XCD × 38 个启用）
    "mi300x": dict(name="AMD MI300X", en="AMD MI300X", vendor="AMD", year=2023, bf16=1307.4e12, low=2614.9e12, mem=192e9,
                   bw=5.3e12, link=7 * 128e9, tdp=750, units=304, unit_name="CU"),
    # AMD Instinct MI355X：ROCm 微架构文档（reference/gpu-arch/mi350）：FP16 2.5、FP8 5.0、MXFP6/MXFP4 10.0 PFLOP/s
    # （均稠密；AMD 产品页印的 5.0/10.1 PF 是稀疏值）；HBM3E 288 GB、8 TB/s；1400 W 液冷；256 个计算单元
    # （8 个 XCD × 36 个，其中 32 个启用）。互联带宽 AMD 未在文档中单列 → None
    "mi355x": dict(name="AMD MI355X", en="AMD MI355X", vendor="AMD", year=2025, bf16=2.5e15, low=5.0e15, mem=288e9,
                   bw=8e12, link=None, tdp=1400, units=256, unit_name="CU"),
    # Google TPU v5p：Google Cloud 文档 tpu/docs/v5p：BF16 459 TFLOP/s、FP8 459 TFLOP/s，95 GiB HBM、2765 GB/s，
    # 芯片间互联 1200 GB/s，Pod 上限 8960 个芯片。功耗 Google 未公布 → None。每个芯片 2 个 TensorCore
    "tpuv5p": dict(name="Google TPU v5p", en="Google TPU v5p", vendor="Google", year=2023, bf16=459e12, low=459e12, mem=95 * 2 ** 30,
                   bw=2765e9, link=1200e9, tdp=None, units=2, unit_name="TensorCore"),
    # Google TPU v7（Ironwood）：Google Cloud 文档 tpu/docs/tpu7x：BF16 2307 TFLOP/s、FP8 4614 TFLOP/s，
    # 192 GB HBM、7380 GB/s，芯片间互联 1200 GB/s，Pod 上限 9216 个芯片（三维环面）。功耗未公布。
    # 每个芯片 2 个 TensorCore + 4 个 SparseCore
    "tpuv7": dict(name="Google TPU v7", en="Google TPU v7", vendor="Google", year=2025, bf16=2307e12, low=4614e12, mem=192e9,
                  bw=7380e9, link=1200e9, tdp=None, units=2, unit_name="TensorCore"),
    # 华为昇腾 910C：华为 2025 年全联接大会主题演讲与路线图整理：128 GB、3.2 TB/s、互联 784 GB/s。
    # 算力华为没有在公开材料中给出统一的稠密峰值（不同子型号不同）→ bf16、low 写 None。功耗未公布
    "ascend910c": dict(name="华为昇腾 910C", en="Huawei Ascend 910C", vendor="华为", year=2025, bf16=None, low=None, mem=128e9,
                       bw=3.2e12, link=784e9, tdp=None, units=None, unit_name="AI Core"),
    # 华为昇腾 950PR：华为 2025 年全联接大会主题演讲（2026 年第一季度）：FP8 1 PFLOP/s、FP4 2 PFLOP/s，
    # 自研高带宽存储 HiBL 1.0 128 GB、1.6 TB/s，互联 2.0 TB/s。BF16 峰值未公布
    "ascend950pr": dict(name="华为昇腾 950PR", en="Huawei Ascend 950PR", vendor="华为", year=2026, bf16=None, low=1e15, mem=128e9,
                        bw=1.6e12, link=2.0e12, tdp=None, units=None, unit_name="AI Core"),
    # 壁仞 BR100：Hot Chips 34（2022）论文：BF16 1024 TFLOP/s、INT8 2048 TOP/s，64 GB HBM2E，
    # 对外 I/O 合计 2.3 TB/s（含 8 条 BLink），550 W，7 nm、1074 mm²。显存带宽论文未单列 → None
    # 互联：论文只给出 die 间 896 GB/s 与对外 I/O 合计 2.3 TB/s（含 PCIe 等），没有单列 8 条 BLink 的聚合带宽 → None
    "br100": dict(name="壁仞 BR100", en="Biren BR100", vendor="壁仞", year=2022, bf16=1024e12, low=2048e12, mem=64e9,
                  bw=None, link=None, tdp=550, units=None, unit_name="SPC"),
    # 天数智芯 天垓 150（BI-V150）：FP16 192 TFLOP/s、INT8 384 TOP/s，64 GB HBM2e、1.2 TB/s，350 W；
    # 没有专用的卡间互联（PCIe 4.0 ×16，双向 64 GB/s）
    # 没有专用的卡间互联（只有 PCIe 4.0 ×16，双向 64 GB/s）：这一项不与 NVLink、Infinity Fabric 放在一起比，写 None
    "biv150": dict(name="天数智芯 天垓 150", en="Iluvatar BI-V150", vendor="天数智芯", year=2023, bf16=192e12, low=384e12, mem=64e9,
                   bw=1.2e12, link=None, tdp=350, units=None, unit_name="—"),
    # 寒武纪 MLU370-X8（官网规格）：FP16 96 TFLOP/s、INT8 256 TOP/s，48 GB LPDDR5、614.4 GB/s，
    # MLU-Link 200 GB/s 双向，250 W，7 nm
    "mlu370x8": dict(name="寒武纪 MLU370-X8", en="Cambricon MLU370-X8", vendor="寒武纪", year=2022, bf16=96e12, low=256e12, mem=48e9,
                     bw=614.4e9, link=200e9, tdp=250, units=None, unit_name="IPU"),
    # 摩尔线程 MTT S4000（官网规格页）：48 GB、768 GB/s、MTLink 240 GB/s、450 W。
    # 官网列出支持 FP32/TF32/FP16/INT8 张量运算，但没有给峰值数字 → bf16、low 写 None
    "mtts4000": dict(name="摩尔线程 MTT S4000", en="Moore Threads MTT S4000", vendor="摩尔线程", year=2023, bf16=None, low=None, mem=48e9,
                     bw=768e9, link=240e9, tdp=450, units=None, unit_name="MUSA Core"),
}

# AMD 自己公布的“可达算力”（max achievable FLOPS，rocm.blogs.amd.com，矩阵乘法实测，不是峰值）：
# MI300X：FP16 654、BF16 708、FP8 1273 TFLOP/s；MI325X：FP16 794、BF16 843、FP8 1519 TFLOP/s
MAF = {"mi300x": dict(fp16=654e12, bf16=708e12, fp8=1273e12, peak_fp16=1307.4e12),
       "mi325x": dict(fp16=794e12, bf16=843e12, fp8=1519e12, peak_fp16=1307.4e12)}

# 两种线程束宽度（NVIDIA 固定 32；AMD CDNA 固定 64，RDNA 可 32 可 64。ROCm 文档 reference/gpu-specs）
WARP = {"NVIDIA": 32, "AMD CDNA": 64}

# 达芬奇架构（昇腾）AI Core 的结构（CANN 社区版文档《Ascend C 算子开发》）：
# - 立方单元（Cube）：官方表述“每次执行可以完成两个 16×16 的 float16 矩阵相乘”，即一次 16×16×16 的矩阵乘累加；
# - 向量单元（Vector）：类 SIMD，支持按间隔取数；标量单元（Scalar）：一个小 CPU，管循环、分支，并调度其他单元的流水线；
# - 片上缓冲：L0A、L0B（立方单元的两个输入）、L0C（立方单元的输出，单精度累加）、
#   统一缓冲区 UB（向量与标量计算的输入输出）、L1（通用数据缓冲）。
# CANN 文档明确写“存储单元大小随型号不同”，没有给出具体的 KB 数 → 本书不写具体容量，只讲各级的用途与数据流。
CUBE = dict(m=16, n=16, k=16, acc="fp32")


def roofline(acc: dict, use_low: bool = False) -> float | None:
    """屋脊点（FLOP/B）：峰值算力 ÷ 显存带宽（3.8 节）。缺任一个数时返回 None。"""
    peak = acc["low"] if use_low else acc["bf16"]
    if peak is None or acc["bw"] is None:
        return None
    return peak / acc["bw"]


def missing(acc: dict) -> int:
    """这一条里厂商没有公布的项数（峰值、低精度峰值、带宽、互联、功耗、并行单元数共 6 项）。"""
    return sum(acc[k] is None for k in ("bf16", "low", "bw", "link", "tdp", "units"))
