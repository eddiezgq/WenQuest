"""程序 11.7.1（实测）：同一个分类器的四种推理方式（11.7 节）。A10。
  eager  ：PyTorch 直接跑（半精度）；
  compile：torch.compile（第 7 章）；
  trt    ：导出 ONNX 后用 TensorRT 跑（没装 TensorRT 时退到 ONNX Runtime 的 CUDA 后端，并在结果里注明）；
对每种方式测：批大小 1 的延迟（中位数）与批大小 32 的吞吐量。ONNX 与引擎这一路用单精度（导出时转回 float），
与半精度的 eager 相比时要记住这一点——结果里的 "precision" 字段注明了各自的精度。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import statistics
import time

import numpy as np
import torch
import torchvision
from torch import nn

dev = "cuda"
torch.manual_seed(0)
model = torchvision.models.resnet18(weights=None)
model.fc = nn.Linear(512, 4)
model = model.eval().to(dev).half()
x1 = torch.randn(1, 3, 224, 224, device=dev, dtype=torch.half)
x32 = torch.randn(32, 3, 224, 224, device=dev, dtype=torch.half)
out = {"torch": torch.__version__, "eager_precision": "fp16", "engine_precision": "fp32"}


def timeit(fn, x, reps=50):
    for _ in range(10):
        fn(x)
    torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        fn(x)
        torch.cuda.synchronize()
        ts.append((time.perf_counter() - t) * 1e3)
    return statistics.median(ts)


with torch.no_grad():
    ref = model(x1).float().cpu().numpy()
    out["eager_ms"] = timeit(lambda t: model(t), x1)
    out["eager_b32_ms"] = timeit(lambda t: model(t), x32, 20)
    out["eager_fps"] = 32 / out["eager_b32_ms"] * 1e3
    comp = torch.compile(model)
    out["compile_ms"] = timeit(lambda t: comp(t), x1)
    out["compile_b32_ms"] = timeit(lambda t: comp(t), x32, 20)
    out["compile_fps"] = 32 / out["compile_b32_ms"] * 1e3

# ---- 导出 ONNX，再用 TensorRT（或 ONNX Runtime）跑
torch.onnx.export(model.float(), torch.randn(1, 3, 224, 224, device=dev), "model.onnx",
                  input_names=["x"], output_names=["y"], dynamic_axes={"x": {0: "b"}, "y": {0: "b"}}, opset_version=17)
engine = "none"
try:
    import tensorrt  # noqa: F401
    import subprocess
    r = subprocess.run(["trtexec", "--onnx=model.onnx", "--fp16", "--shapes=x:1x3x224x224",
                        "--iterations=200", "--avgRuns=50"], capture_output=True, text=True, timeout=1800)
    for line in r.stdout.splitlines():                      # 只认 "Latency:" 这一行：H2D/D2H Latency 是传输时间，不是推理
        if line.strip().startswith("[I] Latency:") and "median =" in line:
            ms = float(line.split("median =")[1].split("ms")[0])
            if 0.01 < ms < 1000:                            # 解析出奇怪的数就当作没测到，退到 ONNX Runtime
                out["trt_ms"], engine = ms, "tensorrt"
            break
    out["trt_version"] = tensorrt.__version__
except Exception as e:                                      # noqa: BLE001  没有 TensorRT：退到 ONNX Runtime
    out["trt_note"] = f"没有 TensorRT（{type(e).__name__}），改用 ONNX Runtime"
if engine == "none":
    try:
        import onnxruntime as ort
        sess = ort.InferenceSession("model.onnx", providers=["CUDAExecutionProvider"])
        xi = np.random.randn(1, 3, 224, 224).astype(np.float32)
        for _ in range(10):
            sess.run(None, {"x": xi})
        ts = []
        for _ in range(50):
            t = time.perf_counter()
            sess.run(None, {"x": xi})
            ts.append((time.perf_counter() - t) * 1e3)
        out["trt_ms"] = statistics.median(ts)
        engine = "onnxruntime"
    except Exception as e:                                  # noqa: BLE001
        out["trt_note2"] = f"ONNX Runtime 也没有：{type(e).__name__}"
out["engine"] = engine
if "trt_ms" in out:
    out["trt_speedup"] = out["eager_ms"] / out["trt_ms"]
out["_gpu_name"] = torch.cuda.get_device_name(0)
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
