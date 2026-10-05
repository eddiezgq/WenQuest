# GPU 实验 6.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 6.1　三个流的重叠
# %%
import sys; sys.path.insert(0, "..")
import json
import wqgpu
env = wqgpu.check(("gpu", "nvcc"))
# %% [markdown]
# ## 1. 一个流与三个流
# 打开 `streams.cu`：`serial` 只用一个流，`streams` 把第 f 帧放进第 f % 3 个流。
# %%
wqgpu.sh("nvcc -O3 -arch=native -o streams streams.cu")
r = json.loads(wqgpu.sh("./streams").splitlines()[-1])
assert r["correct"], "结果不对"
th, tk, td, F = r["h2d_ms"], r["kern_ms"], r["d2h_ms"], r["frames"]
model = (th + tk + td) + (F - 1) * max(th, tk, td)            # 式 (6.1.1)
print(f"复制引擎 {r['engines']} 个；一帧：上传 {th:.2f}、处理 {tk:.2f}、传回 {td:.2f} ms")
print(f"{F} 帧：一个流 {r['serial_ms']:.1f} ms，三个流 {r['streams_ms']:.1f} ms，式 (6.1.1) 估计 {model:.1f} ms")
# %% [markdown]
# ## 2. 用 Nsight Systems 看时间线
# 下面记录一次运行，再打印每种操作的时间汇总。时间线文件 `timeline.nsys-rep` 可以下载后用图形界面打开。
# %%
if "nsys" in env:
    try:
        wqgpu.sh("nsys profile -o timeline --force-overwrite true --trace=cuda ./streams > /dev/null")
        print(wqgpu.sh("nsys stats --report cuda_gpu_trace --format csv timeline.nsys-rep | head -40"))
    except RuntimeError as e:
        print("这台机器上 Nsight Systems 运行失败：", e)
else:
    print("这台机器上没有 nsys")
# %% [markdown]
# ## 3. 回传结果
# %%
wqgpu.submit(h2d_ms=th, kern_ms=tk, d2h_ms=td, serial_ms=r["serial_ms"], streams_ms=r["streams_ms"], engines=r["engines"], model_ms=model)
