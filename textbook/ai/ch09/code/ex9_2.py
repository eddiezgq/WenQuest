"""算例 9.2.1、9.2.2：数据并行与 ZeRO。Ψ 个参数，混合精度 + AdamW：BF16 参数 2Ψ、BF16 梯度 2Ψ、优化器状态 KΨ（K = 12：
FP32 主权重 4、两份 AdamW 状态 8），p 块 GPU（拉杰班达里等 2020 年 ZeRO 论文的记法）。
（1）每块 GPU 上“模型状态”的显存：数据并行 (2 + 2 + K)Ψ；ZeRO-1 切分优化器状态 4Ψ + KΨ/p；ZeRO-2 再切分梯度 2Ψ + (2 + K)Ψ/p；
    ZeRO-3（PyTorch 的 FSDP）再切分参数 (2 + 2 + K)Ψ/p。7B 模型、64 块 GPU 时各是多少。
（2）每一步每块 GPU 的通信量（以 BF16 的字节计，按环形算法的带宽项）：数据并行一次全归约 ≈ 2·2Ψ；
    ZeRO-1/2 用归约—散播 + 全收集，同为 2·2Ψ；ZeRO-3 前向、反向各全收集一次参数，加梯度的归约—散播，≈ 3·2Ψ。
    8 块 A100（NVLink 300 GB/s）上各要多久。"""
from _ch9 import BIG, NVLINK, params
from bookout import out

psi = params(BIG)
K, p = 12, 64
GB = 1e9
mem = {"dp": (4 + K) * psi, "z1": 4 * psi + K * psi / p, "z2": 2 * psi + (2 + K) * psi / p, "z3": (4 + K) * psi / p}
p8 = 8
bw = NVLINK["a100"]
ring = (p8 - 1) / p8
comm_dp = 2 * 2 * psi * ring
comm_z3 = 3 * 2 * psi * ring
out(psi_B=psi / 1e9, p=p, **{k + "_GB": v / GB for k, v in mem.items()},
    comm_dp_GB=comm_dp / GB, comm_z3_GB=comm_z3 / GB, t_dp_s=comm_dp / bw, t_z3_s=comm_z3 / bw)
