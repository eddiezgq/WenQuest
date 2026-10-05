"""算例 6.3.1：GPU 之间与机器之间的互联带宽，以及传 1 GB 要多久。每个 GPU 每个方向的理论带宽（conventions/gpus.py）。
数据并行训练要交换的梯度：第 2 章小型 Transformer（单精度）与 70 亿参数一级的模型（半精度）。"""
from bookout import out
from gpus import IB, NVLINK, PCIE

links = {"pcie4": PCIE[4], "pcie5": PCIE[5], "nvl_v100": NVLINK["v100"], "nvl_a100": NVLINK["a100"], "nvl_h100": NVLINK["h100"],
         "nvl_b200": NVLINK["b200"], "ib_hdr": IB["hdr"], "ib_ndr": IB["ndr"]}
small_MB = 11_532_288 * 4 / 1e6                 # 小型 Transformer 的参数个数（2.9 节），单精度梯度
big_GB = 7e9 * 2 / 1e9                          # 70 亿参数，半精度梯度
out(**{f"{k}_GBs": v / 1e9 for k, v in links.items()}, **{f"{k}_ms": 1e9 / v * 1e3 for k, v in links.items()},
    small_MB=small_MB, big_GB=big_GB, big_nvl_a100_ms=big_GB * 1e9 / NVLINK["a100"] * 1e3, big_pcie4_ms=big_GB * 1e9 / PCIE[4] * 1e3,
    big_ndr_ms=big_GB * 1e9 / IB["ndr"] * 1e3, ratio_nvl_pcie=NVLINK["a100"] / PCIE[4])
