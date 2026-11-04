"""在单独的 Python 虚拟环境里装 vLLM（它自带匹配的 PyTorch，不动机器上原有的），运行 serve.py（第 14 轮附 4.4 节）。"""
import json
import os
import re
import subprocess
import sys

venv = os.path.expanduser("~/wq-vllm")
py = os.path.join(venv, "bin", "python")
if not os.path.exists(py):
    if subprocess.run([sys.executable, "-m", "venv", venv]).returncode != 0:   # Ubuntu 上可能缺 pythonX.Y-venv
        v = f"python{sys.version_info.major}.{sys.version_info.minor}-venv"
        subprocess.run(["sudo", "-n", "apt-get", "-o", "DPkg::Lock::Timeout=300", "update", "-q"])
        subprocess.run(["sudo", "-n", "apt-get", "-o", "DPkg::Lock::Timeout=300", "install", "-y", "-q", v], check=True)
        subprocess.run([sys.executable, "-m", "venv", "--clear", venv], check=True)
    subprocess.run([py, "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
    subprocess.run([py, "-m", "pip", "install", "-q", "vllm"], check=True)


def driver_cuda() -> str:
    """驱动支持到哪个 CUDA 版本，写成 cu128 这种写法；问不出来就空着。"""
    out = subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout
    m = re.search(r"CUDA Version:\s*(\d+)\.(\d+)", out)
    return f"cu{m.group(1)}{m.group(2)}" if m else ""


r = subprocess.run([py, "serve.py"], capture_output=True, text=True)
print(r.stdout[-4000:], r.stderr[-4000:])
if r.returncode != 0 and "driver on your system is too old" in (r.stdout + r.stderr):
    # 最新的 vLLM 自带的 PyTorch 要比这台机器的驱动更新的 CUDA（2026-11-04 实测时驱动是 12.8）。
    # 照驱动的版本换一份 PyTorch 的轮子再装一遍，只试这一次。
    tag = driver_cuda()
    print(f"自带的 PyTorch 对这台机器的驱动太新，改用 {tag or '默认'} 的轮子重装 vLLM")
    cmd = [py, "-m", "pip", "install", "-q", "--force-reinstall", "vllm"]
    if tag:
        cmd += ["--extra-index-url", f"https://download.pytorch.org/whl/{tag}"]
    subprocess.run(cmd, check=True)
    r = subprocess.run([py, "serve.py"], capture_output=True, text=True)
    print(r.stdout[-4000:], r.stderr[-4000:])
if r.returncode != 0:
    raise SystemExit(f"serve.py 没跑成（返回 {r.returncode}）")
out = json.load(open("out.json"))
out["vllm"] = subprocess.run([py, "-c", "import vllm; print(vllm.__version__)"], capture_output=True, text=True).stdout.strip()
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
