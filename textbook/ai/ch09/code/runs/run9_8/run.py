"""在单独的 Python 虚拟环境里装 vLLM（它自带匹配的 PyTorch，不动机器上原有的），运行 serve.py（第 14 轮附 4.4 节）。"""
import json
import os
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
subprocess.run([py, "serve.py"], check=True)
out = json.load(open("out.json"))
out["vllm"] = subprocess.run([py, "-c", "import vllm; print(vllm.__version__)"], capture_output=True, text=True).stdout.strip()
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
