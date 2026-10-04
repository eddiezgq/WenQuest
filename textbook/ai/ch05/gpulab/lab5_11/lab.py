# GPU 实验 5.11 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 5.11　矩阵乘法：从朴素版到张量核心
# %%
import sys; sys.path.insert(0, "..")
import json
import re
import wqgpu
env = wqgpu.check(("gpu", "nvcc"))
# %% [markdown]
# ## 1. 各个版本（n = 4096）
# 打开 `gemm.cu`：从 `naive` 到 `wmma_gemm` 对应正文 5.7—5.10 节，最后与 cuBLAS 比较。朴素版较慢，约需一分钟。
# %%
wqgpu.sh("nvcc -O3 -arch=native -o gemm gemm.cu -lcublas")
r = json.loads(wqgpu.sh("./gemm 4096").splitlines()[-1])
assert r["correct"], "结果与 cuBLAS 不同"
names = ["naive_rowx", "naive", "tiled", "regtile", "vec", "dbuf", "cublas", "wmma", "cublas_tf32", "cublas_h"]
for k in names:
    print(f"{k:12s} {r[k + '_GFs']:10.0f} GFLOP/s")
# %% [markdown]
# ## 2. 画到屋顶线上
# 峰值按显卡型号查表（TFLOP/s：单精度、TF32 张量核心、半精度张量核心，稠密；显存带宽 GB/s）。表中没有的显卡请自己填。
# %%
SPEC = [(r"A10\b", 31.2, 62.5, 125, 600), (r"A100", 19.5, 156, 312, 2039), (r"H100", 67, 494.7, 989.4, 3350), (r"RTX 4090", 82.6, 82.6, 165.2, 1008),
        (r"L4\b", 30.3, 60, 121, 300), (r"T4\b", 8.1, 8.1, 65, 320)]
gpu = env.get("gpu", "")
spec = next((s[1:] for s in SPEC if re.search(s[0], gpu)), None)
print(gpu, spec)
# 计算强度（不计缓存，程序 5.11.1）：朴素 0.25，分块 32×32 约 8，128×128 约 31.5（单精度）、约 62（半精度输入）
I = {"naive_rowx": 0.25, "naive": 0.25, "tiled": 7.97, "regtile": 31.5, "vec": 31.5, "dbuf": 31.5, "wmma": 62.1}
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    if spec:
        p32, ptf, p16, bw = spec
        x = np.logspace(-1, 3.2, 200)
        fig, ax = plt.subplots(figsize=(7, 4.5))
        for peak, lab in ((p32, "FP32"), (ptf, "TF32"), (p16, "FP16 tensor")):
            ax.plot(x, np.minimum(peak, bw * x / 1000), label=f"{lab} {peak} TFLOP/s")
        for k, v in I.items():
            ax.plot(v, r[k + "_GFs"] / 1000, "o")
            ax.annotate(k, (v, r[k + "_GFs"] / 1000), fontsize=8, xytext=(4, 4), textcoords="offset points")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("FLOP/B"); ax.set_ylabel("TFLOP/s"); ax.legend(fontsize=8)
        fig.savefig("roofline.png", dpi=120, bbox_inches="tight")
        print("已存为 roofline.png")
except ImportError:
    print("没有 matplotlib：请把上面的数字手工画到屋顶线上")
# %% [markdown]
# ## 3. 矩阵大小与波次量化
# %%
small = {m: json.loads(wqgpu.sh(f"./gemm {m}").splitlines()[-1]) for m in (1024, 2048)}
for m, rr in small.items():
    print(f"n = {m}: 双缓冲版 {rr['dbuf_GFs']:8.0f} GFLOP/s，cuBLAS 半精度 {rr['cublas_h_GFs']:8.0f} GFLOP/s")
print("寄存器（每个线程）：", {k: r[k + "_regs"] for k in ("regtile", "vec", "dbuf", "wmma")}, "溢出（字节）：", {k: r[k + "_spill"] for k in ("regtile", "vec", "dbuf")})
# %% [markdown]
# ## 4. 回传结果
# %%
wqgpu.submit(naive_GFs=r["naive_GFs"], tiled_GFs=r["tiled_GFs"], regtile_GFs=r["regtile_GFs"], vec_GFs=r["vec_GFs"], dbuf_GFs=r["dbuf_GFs"],
             cublas_GFs=r["cublas_GFs"], wmma_GFs=r["wmma_GFs"], cublas_h_GFs=r["cublas_h_GFs"],
             h1024_GFs=small[1024]["cublas_h_GFs"], h2048_GFs=small[2048]["cublas_h_GFs"],
             d1024_GFs=small[1024]["dbuf_GFs"], d2048_GFs=small[2048]["dbuf_GFs"])
