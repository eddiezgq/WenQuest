# GPU 实验 11.7 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 11.7　把检测模型导出到推理引擎并测速
# %%
import sys; sys.path.insert(0, "..")
import statistics, time
import torch, torchvision
from torch import nn
import wqgpu
env = wqgpu.check(("gpu", "torch"))
dev = "cuda"
print(torch.cuda.get_device_name(0))
# %% [markdown]
# ## 1. 基准：PyTorch 直接跑（任务 1）
# 半精度、批大小 1 测延迟（中位数），批大小 32 测吞吐量。延迟决定“一个零件多久出结果”，吞吐量决定“每秒能检多少件”。
# %%
model = torchvision.models.resnet18(weights=None); model.fc = nn.Linear(512, 4)
model = model.eval().to(dev).half()
x1 = torch.randn(1, 3, 224, 224, device=dev, dtype=torch.half)
x32 = torch.randn(32, 3, 224, 224, device=dev, dtype=torch.half)

def timeit(fn, x, reps=50):
    for _ in range(10): fn(x)
    torch.cuda.synchronize(); ts = []
    for _ in range(reps):
        t = time.perf_counter(); fn(x); torch.cuda.synchronize(); ts.append((time.perf_counter() - t) * 1e3)
    return statistics.median(ts)

with torch.no_grad():
    eager_ms = timeit(lambda t: model(t), x1)
    eager_b32 = timeit(lambda t: model(t), x32, 20)
print(f"PyTorch：批 1 延迟 {eager_ms:.2f} ms，批 32 吞吐 {32/eager_b32*1e3:.0f} 张/秒")
# %% [markdown]
# ## 2. torch.compile 与推理引擎（任务 2）
# 先试 `torch.compile`（第 7 章），再导出 ONNX 交给 TensorRT；机器上没有 TensorRT 时退到 ONNX Runtime，
# 结论照样成立——引擎做的是同一类事：算子融合、常量折叠、为这张卡挑核函数。
# %%
with torch.no_grad():
    comp = torch.compile(model)
    comp_ms = timeit(lambda t: comp(t), x1)
print(f"torch.compile：批 1 延迟 {comp_ms:.2f} ms（加速 {eager_ms/comp_ms:.2f} 倍）")
torch.onnx.export(model.float(), torch.randn(1, 3, 224, 224, device=dev), "model.onnx",
                  input_names=["x"], output_names=["y"], dynamic_axes={"x": {0: "b"}, "y": {0: "b"}}, opset_version=17)
engine_ms, engine = None, "none"
try:
    import tensorrt, subprocess
    r = subprocess.run(["trtexec", "--onnx=model.onnx", "--fp16", "--shapes=x:1x3x224x224",
                        "--iterations=200", "--avgRuns=50"], capture_output=True, text=True, timeout=1800)
    for line in r.stdout.splitlines():                 # 只认 "Latency:" 这一行（H2D/D2H 是传输时间）
        if line.strip().startswith("[I] Latency:") and "median =" in line:
            ms = float(line.split("median =")[1].split("ms")[0])
            if 0.01 < ms < 1000:
                engine_ms, engine = ms, "tensorrt"
            break
except Exception as e:
    print("没有 TensorRT：", type(e).__name__)
if engine == "none":
    import numpy as np, onnxruntime as ort
    sess = ort.InferenceSession("model.onnx", providers=["CUDAExecutionProvider"])
    xi = np.random.randn(1, 3, 224, 224).astype("float32")
    for _ in range(10): sess.run(None, {"x": xi})
    ts = []
    for _ in range(50):
        t = time.perf_counter(); sess.run(None, {"x": xi}); ts.append((time.perf_counter() - t) * 1e3)
    engine_ms, engine = statistics.median(ts), "onnxruntime"
print(f"{engine}：批 1 延迟 {engine_ms:.2f} ms（相对 PyTorch {eager_ms/engine_ms:.2f} 倍）")
# %% [markdown]
# ## 3. 够不够快（任务 3）
# 相机每秒 60 帧：一帧的预算是 16.7 ms。按上面的延迟与吞吐，一块 GPU 能顶几条产线（每条线一路相机）？
# 批大小加大时延迟怎样变（9.7 节的解码也是同一回事）？
# %%
budget = 1000 / 60
print(f"一帧预算 {budget:.1f} ms；按批 1 的延迟，一块 GPU 约可服务 {budget/engine_ms:.1f} 路相机（不计采集与传输）")
# %% [markdown]
# ## 4. 回传结果
# %%
wqgpu.submit(eager_ms=eager_ms, compile_ms=comp_ms, engine_ms=engine_ms,
             eager_fps=32 / eager_b32 * 1e3, engine=engine)
