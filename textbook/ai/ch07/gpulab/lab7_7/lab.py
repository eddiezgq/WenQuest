# GPU 实验 7.7 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 7.7　为 PyTorch 写一个自定义 CUDA 算子
# %%
import sys; sys.path.insert(0, "..")
import os
import subprocess
import sysconfig
import torch
from torch.nn import functional as F
import wqgpu
env = wqgpu.check(("gpu", "nvcc", "torch"))
try:
    import ninja
except ImportError:                                  # 编译扩展要用 ninja
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ninja"], check=True)
    import ninja
os.environ["PATH"] = ninja.BIN_DIR + os.pathsep + os.environ["PATH"]
if not os.path.exists(os.path.join(sysconfig.get_paths()["include"], "Python.h")):
    print("缺少 Python.h：先在终端运行  apt-get install -y python3-dev（普通用户加 sudo）")
# %% [markdown]
# ## 1. 编译并检查（任务 1）
# 打开 `bias_gelu.py`：上半部分是 CUDA 源程序（前向、反向两个核函数），下半部分把它接进自动微分。
# 第一次导入时调用 nvcc 编译，约一分钟。
# %%
from bias_gelu import bias_gelu

x = torch.randn(8192, 1536, device="cuda", requires_grad=True)
b = torch.randn(1536, device="cuda", requires_grad=True)
dy = torch.randn_like(x)
native = lambda x, b: F.gelu(x + b, approximate="tanh")
fwd_err = (bias_gelu(x, b) - native(x, b)).abs().max().item()
xd = torch.randn(4, 3, 8, dtype=torch.double, device="cuda", requires_grad=True)
bd = torch.randn(8, dtype=torch.double, device="cuda", requires_grad=True)
grad_ok = torch.autograd.gradcheck(bias_gelu, (xd, bd))
print(f"前向与原生写法的最大差 {fwd_err:.1e}；梯度检查 {'通过' if grad_ok else '不通过'}")
# %% [markdown]
# ## 2. 比一比速度（任务 2）
# 形状是前馈网络第一层的输出（8192 × 1536，单精度）。前向一次、前向加反向一次，各取 50 次的中位数。
# %%
def t_us(fn):
    return wqgpu.bench(fn, repeat=50, sync=torch.cuda.synchronize) * 1e6


with torch.no_grad():
    nf, ff = t_us(lambda: native(x, b)), t_us(lambda: bias_gelu(x, b))
nb = t_us(lambda: torch.autograd.grad(native(x, b), (x, b), dy))
fb = t_us(lambda: torch.autograd.grad(bias_gelu(x, b), (x, b), dy))
N = x.numel() * 4
print(f"前向：原生 {nf:.0f} μs，融合 {ff:.0f} μs（{2 * N / ff / 1e3:.0f} GB/s）")
print(f"前向加反向：原生 {nb:.0f} μs，融合 {fb:.0f} μs")
# %% [markdown]
# ## 3. 改成精确的 GELU（任务 3）
# 把 `gelu_parts` 改成精确定义 GELU(t) = t·Φ(t)（用 `erf`），导数为 Φ(t) + t·φ(t)；保存后运行下一格：
# `importlib.reload` 重新执行 `bias_gelu.py`，PyTorch 发现源程序变了会自动重新编译。
# 再与 `F.gelu(x + b)`（不加 approximate）比较，并重做梯度检查。
# %%
import importlib
import bias_gelu as bg
bg = importlib.reload(bg)
print("与精确 GELU 的最大差：", (bg.bias_gelu(x, b) - F.gelu(x + b)).abs().max().item())
print("梯度检查：", torch.autograd.gradcheck(bg.bias_gelu, (xd, bd)))
# %% [markdown]
# ## 4. 回传结果
# %%
wqgpu.submit(fwd_err=fwd_err, gradcheck=int(grad_ok), native_f_us=nf, fused_f_us=ff, native_fb_us=nb, fused_fb_us=fb, fused_GBs=2 * N / ff / 1e3)
