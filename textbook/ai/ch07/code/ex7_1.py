"""算例 7.1.1：小型 Transformer 训练批（B = 32，T = 256）的一次前向（含损失），在 A10 上时间花在哪里。
按 _ch7.layer_ops 与 head_ops 的运算清单（PyTorch 急切执行、单精度）：矩阵乘法交给 cuBLAS，按单精度峰值算最短时间；
其余的逐元素运算、归约与复制按“读写一遍显存”算最短时间。两类各占运算量与时间的多少。
PyTorch 默认不让单精度矩阵乘法用 TF32（torch.backends.cuda.matmul.allow_tf32 默认为 False），所以按单精度峰值算。
另给出不计损失（只算到输出层的得分）时的核函数个数，供与程序 7.8.2 的实测对照。"""
from _ch7 import A10, L, gemm_flop, head_ops, layer_ops
from bookout import out

ops = layer_ops()
hops, hflop = head_ops()
hops_model, _ = head_ops(loss=False)
gf = sum(gemm_flop().values()) * L + hflop
other = [o for o in ops if o[1] != "gemm"]
hother = [o for o in hops if o[1] != "gemm"]
other_bytes = (sum(r + w for _, _, r, w in other) * L + sum(r + w for _, _, r, w in hother)) * 4
other_flop = (sum(r for _, _, r, _ in other) * L + sum(r for _, _, r, _ in hother)) * 5   # 每读一个数约做几次运算：宽松地取 5
n_gemm = sum(1 for o in ops if o[1] == "gemm") * L + sum(1 for o in hops if o[1] == "gemm")
n_other = len(other) * L + len(hother)
t_gemm = gf / A10["fp32"] * 1e6
t_other = other_bytes / A10["bw"] * 1e6
out(GFLOP=gf / 1e9, n_gemm=n_gemm, n_other=n_other, n_other_layer=len(other), kernels=n_gemm + n_other,
    kernels_model=(len(ops)) * L + len(hops_model),
    other_pct_flop=100 * other_flop / (gf + other_flop), other_GB=other_bytes / 1e9,
    t_gemm_us=t_gemm, t_other_us=t_other, other_pct_time=100 * t_other / (t_gemm + t_other),
    t_gemm_tf32_us=gf / A10["tf32t"] * 1e6)
