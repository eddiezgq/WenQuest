"""程序 7.7.2：检验并测量自定义算子（7.7 节）。
（1）正确性：单精度下与 F.gelu(x + b, approximate="tanh") 比较；双精度的小张量上用 torch.autograd.gradcheck 核对反向
    （它用数值差分检查我们写的导数）。
（2）速度：前馈网络第一层输出的形状 8192 × 1536（单精度），前向、前向加反向各要多久——PyTorch 原生写法（两个核函数）、
    自定义的融合算子、以及把原生写法交给 torch.compile（7.8 节）。按算例 7.7.1 的流量算出实际达到的显存带宽。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import time

import torch
from torch.nn import functional as F

import prep

prep.ninja_on_path()                                        # load_inline 要用 ninja
prep.python_headers()

t0 = time.time()
from bias_gelu import bias_gelu   # noqa: E402  第一次导入时编译
build_s = time.time() - t0

dev = "cuda"
torch.manual_seed(0)
n, f = 32 * 256, 1536
x = torch.randn(n, f, device=dev, requires_grad=True)
b = torch.randn(f, device=dev, requires_grad=True)
dy = torch.randn(n, f, device=dev)


def native(x, b):
    return F.gelu(x + b, approximate="tanh")


fwd_err = (bias_gelu(x, b) - native(x, b)).abs().max().item()
xd = torch.randn(4, 3, 8, dtype=torch.double, device=dev, requires_grad=True)
bd = torch.randn(8, dtype=torch.double, device=dev, requires_grad=True)
grad_ok = torch.autograd.gradcheck(bias_gelu, (xd, bd))
ga = torch.autograd.grad(bias_gelu(x, b), (x, b), dy)
gb = torch.autograd.grad(native(x, b), (x, b), dy)
dx_err = (ga[0] - gb[0]).abs().max().item()
db_rel = ((ga[1] - gb[1]).abs().max() / gb[1].abs().max()).item()


def timeit(fn, reps=50):
    for _ in range(5):
        fn()
    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    ts = []
    for _ in range(reps):
        e0.record()
        fn()
        e1.record()
        e1.synchronize()
        ts.append(e0.elapsed_time(e1) * 1e3)
    ts.sort()
    return ts[len(ts) // 2]


def both(op):
    with torch.no_grad():
        tf = timeit(lambda: op(x, b))
    tb = timeit(lambda: torch.autograd.grad(op(x, b), (x, b), dy))
    return tf, tb


res = {"native": both(native), "fused": both(bias_gelu)}
try:
    comp = torch.compile(native)
    res["compiled"] = both(comp)
except Exception as e:                                      # 没有 Triton 等情况：记下原因，其余照常；表中这一格显示“—”
    print("torch.compile 失败：", e)
    res["compiled"] = ("—", "—")
N = n * f * 4
out = dict(build_s=build_s, fwd_err=fwd_err, dx_err=dx_err, db_rel=db_rel, gradcheck=bool(grad_ok), torch=torch.__version__)
for k, (tf, tb) in res.items():
    out[k + "_f_us"], out[k + "_fb_us"] = tf, tb
out["fused_f_GBs"] = 2 * N / out["fused_f_us"] / 1e3
out["native_f_GBs"] = 4 * N / out["native_f_us"] / 1e3
out["speed_f"] = out["native_f_us"] / out["fused_f_us"]
out["speed_fb"] = out["native_fb_us"] / out["fused_fb_us"]
out["correct"] = bool(grad_ok and fwd_err < 1e-5 and dx_err < 1e-4 and db_rel < 1e-4)
assert out["correct"], f"结果不对：{out}"
json.dump(out, open("out.json", "w"))
print(out)
