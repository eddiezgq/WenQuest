"""算例 9.7.1—9.7.3：推理的两个阶段、键值缓存与分页注意力。7B 模型（半精度），A100 80 GB（312 TFLOP/s，2039 GB/s）。
（1）预填充：一次处理 1000 个词元的提示词，运算量约 2N·1000，按峰值的一半算要多久；解码：每生成一个词元读一遍权重（2N 字节），
    受带宽限制要多久。把 b 条序列一起解码，权重只读一遍、运算量乘 b：计算强度约为 b FLOP/B，b 达到屋脊（峰值 ÷ 带宽）以前，
    批越大，每个词元越便宜。
（2）键值缓存：每个词元 2·L·h·d_h 个数；批 16 条、每条 4096 个词元共多少 GB，与权重相比。
（3）分页注意力：若每条序列按最大长度 4096 预先分配连续的缓存，实际长度在 100—2000 之间均匀分布时浪费多少；
    按每块 16 个词元分页分配（vLLM 的做法），浪费的只是每条最后一块没用满的部分。"""
import numpy as np

from _ch9 import A100, BIG, kv_bytes_per_token, params
from bookout import out

N = params(BIG)
prompt = 1000
t_prefill = 2 * N * prompt / (A100["fp16t"] * 0.5)
t_decode = 2 * N / A100["bw"]
ridge = A100["fp16t"] / A100["bw"]
kv = kv_bytes_per_token(BIG)
kv_batch = kv * 16 * 4096
rng = np.random.default_rng(97)
lens = rng.integers(100, 2001, 10000)
waste_contig = 1 - lens.sum() / (len(lens) * 4096)
blocks = np.ceil(lens / 16) * 16
waste_paged = 1 - lens.sum() / blocks.sum()
out(t_prefill_ms=t_prefill * 1e3, t_decode_ms=t_decode * 1e3, ridge=ridge, kv_KB=kv / 1e3, kv_batch_GB=kv_batch / 1e9,
    weights_GB=2 * N / 1e9, waste_contig_pct=100 * waste_contig, waste_paged_pct=100 * waste_paged)
