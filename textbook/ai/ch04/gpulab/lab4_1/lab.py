# GPU 实验 4.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 4.1　第一个核函数：向量加法与图像灰度化
# 按顺序运行各格。第一格检查环境；最后一格把你测得的数回传问渠，填进你的实验报告。
# %%
import sys; sys.path.insert(0, "..")
import json
import wqgpu
env = wqgpu.check(("gpu", "nvcc"))
# %% [markdown]
# ## 1. 向量加法
# 打开左边的 `vadd.cu` 看一看：核函数 `vadd` 每个线程算一个元素。下面编译并运行，输出一行 JSON。
# %%
wqgpu.sh("nvcc -O3 -arch=native -o vadd vadd.cu")
r = json.loads(wqgpu.sh("./vadd").splitlines()[-1])
vadd_ms, vadd_GBs = r["vadd_ms"], r["vadd_GBs"]
print(f"耗时 {vadd_ms:.3f} ms，有效带宽 {vadd_GBs:.0f} GB/s，误差 {r['vadd_err']}")
assert r["vadd_err"] == 0, "向量加法结果不对，检查程序"
# %% [markdown]
# 这块 GPU 规格上的显存带宽是多少？下面按型号查一张小表（按整词匹配，先查最具体的写法）；
# 查不到时，请在网上查它的数据手册，把数填进 `peak_GBs`。
# %%
import re
SPEC = [(r"H100.*NVL", 3900), (r"H100.*PCIe", 2000), (r"H100|H800", 3350), (r"A100.*80GB", 2039), (r"A100", 1555),
        (r"L40S", 864), (r"\bL4\b", 300), (r"\bA10\b", 600), (r"4090", 1008), (r"5090", 1792)]
name = env.get("gpu", "")
peak_GBs = next((v for k, v in SPEC if re.search(k, name)), None)
if peak_GBs is None:
    print("没有查到", name, "的显存带宽：请查数据手册，写成 peak_GBs = …")
else:
    print(f"{name} 的显存带宽（规格）：{peak_GBs} GB/s；向量加法达到了 {100 * vadd_GBs / peak_GBs:.0f}%")
# %% [markdown]
# ## 2. 图像灰度化
# `gray.cu` 用 16×16 的二维线程块，每个线程处理一个像素。暗斑像素数应为 11277（与书中程序 4.2.2 在 CPU 上算的一样）。
# %%
wqgpu.sh("nvcc -O3 -arch=native -o gray gray.cu")
g = json.loads(wqgpu.sh("./gray").splitlines()[-1])
gray_ms, gray_GBs = g["gray_ms"], g["gray_GBs"]
assert g["gray_diff"] == 0, "有像素的灰度与 CPU 上算的不同，检查程序"
assert g["gray_dark"] == 11277, "暗斑像素数不对，检查程序"
print(f"每帧 {gray_ms:.3f} ms，占 1/60 秒的 {100 * gray_ms / (1000 / 60):.2f}%")
# %% [markdown]
# ## 3. 每块线程数
# %%
times = {}
for b in (32, 64, 128, 256, 512, 1024):
    times[b] = json.loads(wqgpu.sh(f"./vadd {1 << 26} {b}").splitlines()[-1])["vadd_ms"]
best_block = min(times, key=times.get)
print(times, "最快：", best_block)
# %% [markdown]
# ## 4. 回传结果
# %%
wqgpu.submit(vadd_ms=vadd_ms, vadd_GBs=vadd_GBs, gray_ms=gray_ms, gray_GBs=gray_GBs, peak_GBs=peak_GBs or 0,
             best_block=best_block, t32_ms=times[32], t64_ms=times[64], t128_ms=times[128], t256_ms=times[256],
             t512_ms=times[512], t1024_ms=times[1024])
