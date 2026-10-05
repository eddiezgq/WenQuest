"""算例 9.9.1—9.9.3：训练集群的故障、检查点与能耗。
（1）Llama 3 的论文报告：在约 16 000 块 H100 上预训练的一个 54 天的时段里，发生了 419 次意外中断。平均几小时一次；
    折算到每块 GPU（连同它所在的机器、网络），平均多少年才出一次故障。
（2）检查点：每隔 τ 秒把模型与优化器状态写到存储上，每次耗时 C；出故障时丢掉上一次检查点以后的工作，平均丢 τ/2。
    损失的时间比例 ≈ C/τ + τ/(2M)（M 为平均故障间隔），在 τ = √(2CM) 时最小（扬—戴利公式）。C = 60 s 时 τ 与损失的比例。
（3）能耗：Llama 2 7B 训练用了 184 320 个 A100 GPU 小时（算例 9.1.2），按每块 400 W（A100 SXM 的热设计功耗）只算 GPU 的电能。"""
import math

from bookout import out

hours, fails, gpus = 54 * 24, 419, 16384
mtbf_h = hours / fails
gpu_years = mtbf_h * gpus / (24 * 365)
C, M = 60.0, mtbf_h * 3600
tau = math.sqrt(2 * C * M)
waste = C / tau + tau / (2 * M)
mwh = 184320 * 400 / 1e6
out(mtbf_h=mtbf_h, gpu_years=gpu_years, tau_min=tau / 60, waste_pct=100 * waste, mwh=mwh)
