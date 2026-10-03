"""问渠 GPU 实验助手（《人工智能》第 14 轮附：云端 GPU 实验环境）。

调度服务开机后把本文件、本次实验的笔记本和 session.json 放进 JupyterLab 的 wq/ 文件夹。实验笔记本这样用：

    import sys; sys.path.insert(0, "..")
    import wqgpu
    wqgpu.check()                         # 第一格：看环境（GPU、驱动、CUDA、nvcc、PyTorch、Nsight），缺什么提示怎么补
    out = wqgpu.sh("nvcc -O3 -o vadd vadd.cu && ./vadd")
    t = wqgpu.bench(lambda: f(x), sync=torch.cuda.synchronize)
    wqgpu.submit(t_ms=t * 1e3, bw_GBs=...)   # 最后一格：把测得的数回传问渠，填进你的实验报告

只用 Python 标准库；回传的内容用本次会话的密钥签名（HMAC-SHA256，与问渠网关 app/gpulab.py 的 sign() 相同）。
"""
from __future__ import annotations

import hashlib
import hmac
import json
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def session(path: Path | None = None) -> dict:
    p = path or HERE / "session.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def env() -> dict:
    """GPU 型号、驱动、CUDA、编译器与框架的版本——实验结果连同它一起保存，才知道是在什么环境里测的。"""
    e: dict[str, str] = {"python": platform.python_version(), "os": platform.platform(terse=True)}
    q = _run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,clocks.max.sm", "--format=csv,noheader"])
    if q:
        name, drv, mem, clk = [x.strip() for x in q.splitlines()[0].split(",")][:4]
        e.update(gpu=name, driver=drv, gpu_memory=mem, sm_clock_max=clk, gpus=str(len(q.splitlines())))
    v = _run(["nvcc", "--version"])
    m = re.search(r"release ([\d.]+)", v)
    if m:
        e["nvcc"] = m.group(1)
    if shutil.which("ncu"):
        m = re.search(r"([\d.]{4,})", _run(["ncu", "--version"]))
        e["ncu"] = m.group(1) if m else "yes"
    try:
        import torch  # noqa: PLC0415
        e["torch"] = torch.__version__
        e["torch_cuda"] = str(torch.version.cuda)
        if torch.cuda.is_available():
            e["capability"] = "%d.%d" % torch.cuda.get_device_capability(0)
    except Exception:  # noqa: BLE001
        pass
    try:
        import triton  # noqa: PLC0415
        e["triton"] = triton.__version__
    except Exception:  # noqa: BLE001
        pass
    return e


def check(need: tuple[str, ...] = ("gpu", "nvcc", "torch")) -> dict:
    """打印环境；缺少本实验需要的部件时给出补装的办法。返回 env()。"""
    e = env()
    width = max(len(k) for k in e) if e else 4
    for k, v in e.items():
        print(f"  {k:<{width}}  {v}")
    hints = {"gpu": "没有检测到 GPU：请确认开的是 GPU 机器（不是无卡模式）。",
             "nvcc": "没有 nvcc：运行  conda install -y -c nvidia cuda-nvcc  或换带 CUDA 开发工具的镜像。",
             "torch": "没有 PyTorch：运行  pip install torch。",
             "triton": "没有 Triton：运行  pip install triton。",
             "ncu": "没有 Nsight Compute 命令行（ncu）：本实验需要能读性能计数器的机器（第 7 章用虚拟机）。"}
    missing = [n for n in need if n not in e]
    for n in missing:
        print("  ✗", hints.get(n, n))
    if not missing:
        print("  ✓ 环境齐全")
    return e


def sh(cmd: str, timeout: int = 600) -> str:
    """运行一条命令（编译、运行 CUDA 程序），打印并返回输出；失败时抛出带输出的异常。"""
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout + r.stderr).strip()
    print(out)
    if r.returncode != 0:
        raise RuntimeError(f"命令失败（返回 {r.returncode}）：{cmd}")
    return out


def bench(fn, repeat: int = 20, warmup: int = 3, sync=None) -> float:
    """多次运行取中位数（秒）。GPU 上的运算是异步的，计时前后要同步：sync=torch.cuda.synchronize。"""
    for _ in range(warmup):
        fn()
    if sync:
        sync()
    ts = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        if sync:
            sync()
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts)


def payload(values: dict, environment: dict | None = None, sess: dict | None = None) -> tuple[bytes, str]:
    """回传的正文与签名。"""
    s = sess if sess is not None else session()
    body = json.dumps({"sid": s.get("sid", ""), "values": values, "env": environment if environment is not None else env()},
                      ensure_ascii=False, sort_keys=True).encode()
    return body, hmac.new(str(s.get("key", "")).encode(), body, hashlib.sha256).hexdigest()


def submit(**values) -> dict:
    """把测得的数回传问渠。只保留本实验登记过的结果名（见 session.json 的 results）。"""
    s = session()
    if not s:
        print("没有找到 session.json：这台机器不是从问渠打开的，结果不会回传。")
        return {}
    known = set(s.get("results") or [])
    extra = [k for k in values if known and k not in known]
    if extra:
        print("这些结果名本实验没有登记，不会保存：", ", ".join(extra))
    body, sig = payload(values, sess=s)
    req = urllib.request.Request(s["callback"], data=body, method="POST",
                                 headers={"Content-Type": "application/json", "X-WQ-Signature": sig})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print("回传失败：", e.code, e.read().decode(errors="ignore")[:200])
        return {}
    except OSError as e:
        print("回传失败（网络）：", e)
        return {}
    print("✓ 已回传：", ", ".join(res.get("kept", [])), "——在问渠的实验页可以下载填好数据的实验报告。")
    return res


if __name__ == "__main__":
    check(tuple(sys.argv[1:]) or ("gpu", "nvcc", "torch"))
