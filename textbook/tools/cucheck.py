"""CUDA 程序的编译检查（《人工智能》第 4 章起）：没有 GPU、没有 nvcc 的机器上，用 clang 的 CUDA 前端检查书中的 .cu 程序。

clang 分两步检查：设备端（编译成指定架构的机器码，经 ptxas）与主机端。只编译、不链接、不运行——运行与计时在云端 GPU 上做
（gpurun.py、GPU 实验）。所需的 CUDA 头文件与 ptxas 来自 NVIDIA 在 PyPI 上发布的软件包
（nvidia-cuda-runtime-cu12、nvidia-cuda-nvcc-cu12、nvidia-cuda-cccl-cu12、nvidia-curand-cu12；cuBLAS 的软件包有 580 MB，
只需从中解出头文件 nvidia/cublas/include，见 .github/workflows/deploy.yml），本工具把它们拼成 clang 认得的 CUDA 目录。也可以用环境变量 WQ_CUDA_ROOT 指向一个完整的 CUDA 工具包。

    python3 textbook/tools/cucheck.py file.cu ...        # 逐个检查，打印问题
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ARCHS = ("sm_89", "sm_90")          # Ada（RTX 4090）与 Hopper（H100）：书中实验所用的两档显卡
_ROOT: Path | None = None


def cuda_root() -> Path | None:
    """clang 用的 CUDA 目录；找不到时返回 None。"""
    global _ROOT
    if _ROOT is not None:
        return _ROOT
    env = os.environ.get("WQ_CUDA_ROOT")
    if env and (Path(env) / "include" / "cuda_runtime.h").exists():
        _ROOT = Path(env)
        return _ROOT
    try:
        import nvidia  # noqa: PLC0415  (the PyPI wheels install into the "nvidia" namespace package)
    except ImportError:
        return None
    parts = [Path(p) for p in nvidia.__path__]
    find = lambda rel: next((p / rel for p in parts if (p / rel).exists()), None)  # noqa: E731
    rt, cc, nvcc = find("cuda_runtime/include"), find("cuda_cccl/include"), find("cuda_nvcc")
    if not (rt and cc and nvcc and (nvcc / "bin" / "ptxas").exists()):
        return None
    root = Path(tempfile.gettempdir()) / "wq-cuda-root"
    blas = find("cublas/include")
    stale = blas is not None and not (root / "include" / "cublas_v2.h").exists()   # 后来才装上 cuBLAS 头文件：重拼
    if stale or not (root / "include" / "cuda_runtime.h").exists():
        shutil.rmtree(root, ignore_errors=True)
        (root / "bin").mkdir(parents=True)
        inc = root / "include"
        inc.mkdir()
        for src in (rt, cc, nvcc / "include", find("curand/include"), blas):
            if src:
                for f in src.rglob("*"):
                    if f.is_file():
                        dst = inc / f.relative_to(src)
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        if not dst.exists():
                            dst.symlink_to(f)
        (root / "bin" / "ptxas").symlink_to(nvcc / "bin" / "ptxas")
        (root / "nvvm").symlink_to(nvcc / "nvvm")
        (root / "lib64").mkdir()
    _ROOT = root
    return _ROOT


def gcc_dir() -> list[str]:
    """clang 18 与 GCC 14 的 C++ 头文件一起编译 CUDA 设备代码时会报 “__float128 is not supported”（GCC 14 的 <limits>
    在设备端也声明 __float128）。机器上装了多个 GCC 时，选 13 及以下中最新的一个。"""
    base = Path("/usr/lib/gcc/x86_64-linux-gnu")
    if not base.is_dir():
        return []
    vers = sorted((int(p.name), p) for p in base.iterdir() if p.name.isdigit())
    if not vers or vers[-1][0] <= 13:
        return []
    old = [p for v, p in vers if v <= 13 and (p / "crtbegin.o").exists()]
    return [f"--gcc-install-dir={old[-1]}"] if old else []


def available() -> bool:
    return shutil.which("clang++") is not None and cuda_root() is not None


def check(path: Path, archs: tuple[str, ...] = ARCHS) -> list[str]:
    """问题清单（空 = 编译通过）。"""
    root = cuda_root()
    if root is None or not shutil.which("clang++"):
        return ["无法检查：缺少 clang++ 或 CUDA 头文件"]
    env = dict(os.environ, PATH=f"{root / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}")
    base = ["clang++", "-std=c++17", "-O1", "-Wno-unknown-cuda-version", f"--cuda-path={root}", "-I", str(path.parent), *gcc_dir()]
    out = []
    runs = [[f"--cuda-gpu-arch={a}", "--cuda-device-only"] for a in archs] + [["--cuda-host-only"]]
    for extra in runs:
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([*base, *extra, "-c", str(path), "-o", str(Path(tmp) / "x.o")], capture_output=True, text=True, env=env,
                               timeout=180)
            if r.returncode != 0 and "__float128" in r.stderr:      # 没有旧版 GCC 可选时：不让 <limits> 声明 __float128 再试一次
                r = subprocess.run([*base, "-U__SIZEOF_FLOAT128__", "-U__FLOAT128__", *extra, "-c", str(path), "-o", str(Path(tmp) / "x.o")],
                                   capture_output=True, text=True, env=env, timeout=180)
        if r.returncode != 0:
            msg = [ln for ln in r.stderr.splitlines() if "error" in ln][:3] or r.stderr.splitlines()[-3:]
            where = "主机端" if "--cuda-host-only" in extra else extra[0].split("=")[1]
            out.append(f"编译不通过（{where}）：" + " / ".join(m.replace(str(path.parent) + "/", "") for m in msg))
            break
    return out


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        probs = check(Path(f))
        print(("✗ " if probs else "✓ ") + f + ("：" + "；".join(probs) if probs else ""))
        bad += bool(probs)
    sys.exit(1 if bad else 0)
