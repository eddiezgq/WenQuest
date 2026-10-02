"""第 1 章共用的数据表。以下划线开头，构建时不单独运行。

每个数后面写明出处。书中凡用到这些数的地方，都由程序读这里的值算出，不在正文里手写。
"""

# ---------------------------------------------------------------- 硬件规格（稠密峰值，厂商公开资料）
# P_*: 峰值算力，FLOP/s；bw: 显存（内存）带宽，B/s；mem: 容量，B
HW = {
    # NVIDIA GeForce GTX 580（2010 年 11 月）：512 个 CUDA 核心，着色器频率 1544 MHz，每核每周期一次乘加（2 FLOP），
    # 显存带宽 192.4 GB/s；AlexNet 用的是 3 GB 版本（Krizhevsky 等 2012）
    "gtx580": {"year": 2010, "cores": 512, "clock": 1544e6, "bw": 192.4e9, "mem": 3e9},
    # NVIDIA A100 SXM 80 GB（2020）：A100 架构白皮书。FP32 19.5 TFLOP/s；TF32 张量核心 156；FP16/BF16 张量核心 312（稠密）；
    # HBM2e 2039 GB/s
    "a100": {"year": 2020, "P_fp32": 19.5e12, "P_tf32": 156e12, "P_fp16": 312e12, "bw": 2039e9, "mem": 80e9},
    # NVIDIA H100 SXM5 80 GB（2022）：H100 架构白皮书 / 产品资料。FP32 67 TFLOP/s；FP16/BF16 张量核心 989.4（稠密，
    # 计入稀疏为 1979）；HBM3 3.35 TB/s
    "h100": {"year": 2022, "P_fp32": 67e12, "P_fp16": 989.4e12, "bw": 3.35e12, "mem": 80e9},
}
# 代表性的服务器 CPU（教学用的假设值，不对应某一型号）：64 核，主频 3.0 GHz，每核两个 512 位 FMA 单元，
# FP32 每核每周期 2 × 16 × 2 = 64 FLOP；8 通道 DDR5-4800 内存，每通道 4800 MT/s × 8 B = 38.4 GB/s
CPU = {"cores": 64, "clock": 3.0e9, "flop_per_cycle": 2 * 16 * 2, "channels": 8, "mts": 4800e6, "bytes_per_transfer": 8}

# ---------------------------------------------------------------- 模型与训练（原始论文）
# AlexNet（Krizhevsky、Sutskever、Hinton 2012）：两块 GTX 580 3 GB，训练约 90 个周期，用时五到六天；
# ILSVRC-2012 训练集 1 281 167 张图像（Russakovsky 等 2015，表 2）
ALEXNET = {"epochs": 90, "days": (5, 6), "gpus": 2, "train_images": 1281167, "params_paper": 60e6}
# AlexNet 的层（论文第 3 节与图 2）。卷积层：(名称, 输出高, 输出宽, 输出通道, 卷积核高, 宽, 每个核的输入通道)；
# 第 2、4、5 层的卷积核只连接同一块 GPU 上的一半通道（分组卷积），所以每个核的输入通道是 48、192、192。
ALEX_CONV = [
    ("conv1", 55, 55, 96, 11, 11, 3),
    ("conv2", 27, 27, 256, 5, 5, 48),
    ("conv3", 13, 13, 384, 3, 3, 256),
    ("conv4", 13, 13, 384, 3, 3, 192),
    ("conv5", 13, 13, 256, 3, 3, 192),
]
ALEX_FC = [("fc6", 6 * 6 * 256, 4096), ("fc7", 4096, 4096), ("fc8", 4096, 1000)]

# GPT-3（Brown 等 2020）：175B 参数，训练 300B 词元；论文表 D.1 给出训练算力 3.14E+23 FLOP
GPT3 = {"N": 175e9, "D": 300e9, "C_paper": 3.14e23, "year": 2020}
# Llama 3 405B（Llama Team 2024）：405B 参数，15.6T 词元，训练算力 3.8 × 10^25 FLOP；最多 16 384 块 H100
LLAMA3 = {"N": 405e9, "D": 15.6e12, "C_paper": 3.8e25, "gpus": 16384, "year": 2024}

# ---------------------------------------------------------------- 算力增长（文献）
# Moore 定律：晶体管数约每两年翻一番（Moore 1975 的修订说法）；
# Sevilla 等 2022：深度学习之前训练算力约 20 个月翻一番，深度学习时代约 6 个月；
# Amodei、Hernandez 2018：2012—2018 年最大训练算力约 3.4 个月翻一番；
# Epoch AI 2024：前沿模型的训练算力每年增长 4～5 倍
DOUBLING_MONTHS = {"moore": 24, "pre_dl": 20, "dl": 6, "openai2018": 3.4}
EPOCH_PER_YEAR = (4, 5)

# ---------------------------------------------------------------- ImageNet 竞赛（ILSVRC）分类任务冠军的前五错误率
# Russakovsky 等 2015 表 4 与各年官方结果；2012 年为 SuperVision（AlexNet）使用额外数据的提交，第二名 26.2%；
# 人类：Russakovsky 等 2015 第 6.4 节，经过训练的标注者约 5.1%
ILSVRC = [(2010, 28.2, "NEC-UIUC"), (2011, 25.8, "XRCE"), (2012, 15.3, "SuperVision"), (2013, 11.7, "Clarifai"),
          (2014, 6.66, "GoogLeNet"), (2015, 3.57, "MSRA ResNet")]
ILSVRC_2012_SECOND = 26.2
HUMAN_TOP5 = 5.1

# ---------------------------------------------------------------- 年表（1.3 节）
# (年份, 中文, 英文, 线索)；线索：sym 符号主义，con 连接主义，beh 行为主义与控制，gen 综合与里程碑，win 低谷
TIMELINE = [
    (1943, "麦卡洛克、皮茨提出神经元的逻辑模型", "McCulloch–Pitts neuron", "con"),
    (1950, "图灵《计算机器与智能》", "Turing, Computing Machinery and Intelligence", "gen"),
    (1956, "达特茅斯研讨会；逻辑理论家程序", "Dartmouth workshop; Logic Theorist", "sym"),
    (1958, "罗森布拉特提出感知机", "Rosenblatt's perceptron", "con"),
    (1966, "ELIZA 对话程序", "ELIZA", "sym"),
    (1969, "《感知机》一书指出单层网络的局限", "Minsky–Papert, Perceptrons", "con"),
    (1973, "莱特希尔报告，第一次低谷", "Lighthill report; first winter", "win"),
    (1977, "吴文俊提出几何定理机器证明方法", "Wu Wenjun's method for geometry proving", "sym"),
    (1980, "专家系统进入企业", "Expert systems in industry", "sym"),
    (1986, "反向传播算法广为人知", "Backpropagation popularized", "con"),
    (1987, "专用硬件市场崩溃，第二次低谷", "Lisp-machine collapse; second winter", "win"),
    (1991, "布鲁克斯《没有表示的智能》", "Brooks, Intelligence without Representation", "beh"),
    (1997, "深蓝战胜卡斯帕罗夫", "Deep Blue beats Kasparov", "gen"),
    (2006, "深度信念网络；CUDA 发布", "Deep belief nets; CUDA announced", "con"),
    (2012, "AlexNet 在 ImageNet 竞赛中大幅领先", "AlexNet wins ImageNet", "con"),
    (2016, "AlphaGo 战胜李世石", "AlphaGo beats Lee Sedol", "beh"),
    (2017, "Transformer；《新一代人工智能发展规划》", "Transformer; China's AI development plan", "con"),
    (2020, "GPT-3；AlphaFold 2", "GPT-3; AlphaFold 2", "con"),
    (2022, "ChatGPT 发布", "ChatGPT released", "gen"),
    (2024, "诺贝尔物理学奖、化学奖授予人工智能相关工作", "Nobel Prizes in physics and chemistry for AI work", "gen"),
]
WINTERS = [(1974, 1980), (1987, 1993)]      # 两次低谷的大致年代（文献说法不一，取 Russell–Norvig 与 Nilsson 的通常划分）


def gtx580_peak():
    """GTX 580 的 FP32 峰值：核心数 × 频率 × 2 FLOP（每核每周期一次乘加）。"""
    h = HW["gtx580"]
    return h["cores"] * h["clock"] * 2


def cpu_peak(cores=None):
    c = CPU
    return (cores or c["cores"]) * c["clock"] * c["flop_per_cycle"]


def cpu_bw():
    c = CPU
    return c["channels"] * c["mts"] * c["bytes_per_transfer"]


def alexnet_layers():
    """AlexNet 每层的乘加次数（MAC）与参数量（含偏置），按论文的双 GPU 分组结构。"""
    rows = []
    for name, ho, wo, co, kh, kw, ci in ALEX_CONV:
        macs = ho * wo * co * kh * kw * ci
        params = co * kh * kw * ci + co
        rows.append((name, macs, params))
    for name, fin, fout in ALEX_FC:
        rows.append((name, fin * fout, fin * fout + fout))
    return rows
