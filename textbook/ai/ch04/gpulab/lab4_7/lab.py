# GPU 实验 4.7 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 4.7　矩阵转置：合并访问与共享内存
# %%
import sys; sys.path.insert(0, "..")
import json
import wqgpu
env = wqgpu.check(("gpu", "nvcc"))
# %% [markdown]
# ## 1. 四个版本
# 打开 `transpose.cu`：`copy` 是参照，`naive` 按列写，`tiled` 先进共享内存，`tiled<1>` 每行多留一个字。
# %%
wqgpu.sh("nvcc -O3 -arch=native -o transpose transpose.cu")
r = json.loads(wqgpu.sh("./transpose").splitlines()[-1])
assert r["correct"], "转置结果不对"
for k in ("copy", "naive", "tiled", "padded"):
    print(f"{k:7s} {r[k + '_GBs']:8.1f} GB/s  {100 * r[k + '_GBs'] / r['copy_GBs']:5.1f}%")
# %% [markdown]
# ## 2.（可选）用 Nsight Compute 看扇区与存储体冲突
# 只有能读 GPU 性能计数器的机器才能运行；读不了会报 ERR_NVGPUCTRPERM，跳过即可。
# %%
if "ncu" in env:
    try:
        # 每个核函数只分析第一次启动（--launch-count 1）；两个 tiled 版本分开看：模板参数 0 是无填充，1 是有填充
        wqgpu.sh("ncu --kernel-name regex:naive --launch-count 1 --metrics l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum ./transpose | tail -5")
        for pad in (0, 1):
            wqgpu.sh(f"ncu --kernel-name-base demangled --kernel-name 'regex:tiled<{pad}>' --launch-count 1 "
                     "--metrics l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_ld.sum ./transpose | tail -5")
    except RuntimeError as e:
        print("这台机器读不了性能计数器：", e)
# %% [markdown]
# ## 3. 回传结果
# %%
wqgpu.submit(copy_GBs=r["copy_GBs"], naive_GBs=r["naive_GBs"], tiled_GBs=r["tiled_GBs"], padded_GBs=r["padded_GBs"])
