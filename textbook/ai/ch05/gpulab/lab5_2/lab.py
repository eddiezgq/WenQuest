# GPU 实验 5.2 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 5.2　归约的五个版本
# %%
import sys; sys.path.insert(0, "..")
import json
import wqgpu
env = wqgpu.check(("gpu", "nvcc"))
# %% [markdown]
# ## 1. 五个版本与 CUB
# 打开 `reduce.cu`：`v1`～`v5` 是正文 5.2 节的五个版本，最后一个是 CUB 的 `cub::DeviceReduce::Sum`。
# %%
wqgpu.sh("nvcc -O3 -arch=native -o reduce reduce.cu")
r = json.loads(wqgpu.sh("./reduce").splitlines()[-1])
assert r["correct"], "归约结果不对"
print("每个 SM 能同时驻留", r["fit"], "个线程块")
prev = None
for k in ("v1", "v2", "v3", "v4", "v5", "cub"):
    g = r[k + "_GBs"]
    print(f"{k:4s} {r[k + '_us']:8.1f} μs {g:8.1f} GB/s" + (f"  ×{g / prev:.2f}" if prev else ""))
    prev = g
# %% [markdown]
# ## 2. 线程块个数
# 版本 4、5 只启动“SM 数 × 每个 SM 的线程块数”个线程块，默认取能同时驻留的个数（输出中的 fit）。改成 1 和 24 看看。
# %%
x = {m: json.loads(wqgpu.sh(f"./reduce {m}").splitlines()[-1]) for m in (1, 24)}
for m, rr in x.items():
    print(f"每个 SM {m:2d} 个线程块：版本 4 {rr['v4_GBs']:7.1f} GB/s，版本 5 {rr['v5_GBs']:7.1f} GB/s")
# %% [markdown]
# ## 3. 回传结果
# %%
wqgpu.submit(v1_GBs=r["v1_GBs"], v2_GBs=r["v2_GBs"], v3_GBs=r["v3_GBs"], v4_GBs=r["v4_GBs"], v5_GBs=r["v5_GBs"], cub_GBs=r["cub_GBs"],
             v5_x1_GBs=x[1]["v5_GBs"], v5_x24_GBs=x[24]["v5_GBs"])
