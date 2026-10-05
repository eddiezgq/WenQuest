"""HIP 程序的编译与运行检查（《人工智能》第 10 章）：没有 AMD 显卡的机器上，用 AMD 开源的 HIP-CPU
把 HIP 程序编译成普通的 CPU 程序并运行，核对正确性。

HIP-CPU（https://github.com/ROCm/HIP-CPU，MIT 许可）是一组头文件：把 HIP 的核函数当作 C++ 的并行循环在 CPU 上跑。
它不是 GPU 的仿真，跑出来的时间没有意义——本工具只用它检查三件事：程序能编译、能跑完、结果与主机算出的参照一致
（每个程序自己核对，不对就返回非零）。速度与显存要在真正的 AMD 卡上测（10.6 节）。

要求：g++（C++17）、oneTBB（HIP-CPU 用它做并行）、HIP-CPU 的头文件。头文件由环境变量 WQ_HIP_CPU 指定，
或者放在 ~/.cache/wq/HIP-CPU。构建本身不联网：取头文件要显式调用 fetch()（命令行用法会自动调一次），
取的是写死的那个提交（COMMIT），因为这些头文件会被编进构建机上真正运行的程序。

    python3 textbook/tools/hipcheck.py file.hip.cpp ...
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CACHE = Path.home() / ".cache" / "wq" / "HIP-CPU"

REPO = "https://github.com/ROCm/HIP-CPU.git"
COMMIT = "e112c935057434897bb12d9ab3910380a8bd5f58"      # 固定到一个提交：这些头文件会被编进构建机上真正运行的程序
_INC: Path | None = None
_LIB: list[str] | None = None


def _tbb() -> list[str] | None:
    """链接 oneTBB 要用的参数；找不到时返回 None。pip 的 tbb 软件包把库装在 sys.prefix/lib 下。"""
    global _LIB
    if _LIB is not None:
        return _LIB or None
    for d in (Path(sys.prefix) / "lib", Path("/usr/local/lib"), Path("/usr/lib/x86_64-linux-gnu")):
        if list(d.glob("libtbb.so*")):
            _LIB = [f"-L{d}", "-Wl,-rpath," + str(d), "-ltbb", "-lpthread"]
            return _LIB
    _LIB = []
    return None


def include_dir() -> Path | None:
    """已经在本机上的 HIP-CPU 的 include 目录；没有就返回 None（本函数不联网，下载由 fetch() 做）。"""
    global _INC
    if _INC is not None:
        return _INC if str(_INC) else None
    env = os.environ.get("WQ_HIP_CPU")
    for c in (Path(env) if env else None, CACHE):
        if c and (c / "include" / "hip" / "hip_runtime.h").exists():
            _INC = c / "include"
            return _INC
    return None


def fetch() -> Path | None:
    """没有就取一次，取到固定的提交；先克隆到临时目录、成功后再整体改名，中断不会留下半份缓存。"""
    inc = include_dir()
    if inc or not shutil.which("git"):
        return inc
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="wq-hipcpu-", dir=str(CACHE.parent)))
    try:
        subprocess.run(["git", "clone", "-q", REPO, str(tmp / "src")], capture_output=True, timeout=600, check=True)
        subprocess.run(["git", "-C", str(tmp / "src"), "checkout", "-q", COMMIT], capture_output=True, timeout=120, check=True)
        if not (tmp / "src" / "include" / "hip" / "hip_runtime.h").exists():
            return None
        shutil.rmtree(tmp / "src" / ".git", ignore_errors=True)
        if not CACHE.exists():
            (tmp / "src").rename(CACHE)
    except (subprocess.SubprocessError, OSError):
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    global _INC
    _INC = None
    return include_dir()


def version() -> str:
    """参与缓存键：HIP-CPU 的提交与编译器的版本变了，检查就要重做。"""
    gxx = subprocess.run(["g++", "--version"], capture_output=True, text=True).stdout.splitlines()[:1]
    return COMMIT[:12] + "|" + (gxx[0] if gxx else "?")


def available() -> bool:
    return bool(shutil.which("g++")) and _tbb() is not None and include_dir() is not None


def _errors(text: str, n: int = 6) -> str:
    """编译器输出里真正有用的那几行（含 error: 的优先，否则取前几行）。"""
    lines = [l for l in text.splitlines() if l.strip()]
    hit = [l for l in lines if "error:" in l] or lines
    return " / ".join(hit[:n]) if hit else "(没有输出)"


def check(path: Path) -> list[str]:
    """编译并运行一个 HIP 程序；返回问题的说明（空表示通过）。缺少工具时也返回一条说明，不冒充通过。"""
    inc, lib = include_dir(), _tbb()
    if inc is None or lib is None:
        return ["没有检查：缺少 HIP-CPU 头文件或 oneTBB"]
    with tempfile.TemporaryDirectory(prefix="wq-hip-") as d:
        exe = Path(d) / "a.out"
        cmd = ["g++", "-std=c++17", "-O2", "-Wall", f"-I{inc}", f"-I{path.parent}", str(path), "-o", str(exe), *lib]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            return ["在 HIP-CPU 上编译超时（15 分钟）"]
        if r.returncode != 0:
            return ["HIP-CPU 上编译不通过：" + _errors(r.stderr)]
        try:
            r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            return ["在 HIP-CPU 上运行超时（10 分钟）"]
    if r.returncode != 0:
        tail = (r.stderr.strip() or r.stdout.strip() or "(没有输出)").splitlines()[-1]
        return [f"在 HIP-CPU 上运行不通过（返回 {r.returncode}）：{tail}"]
    if '"correct": true' not in r.stdout:
        return ["程序没有报告 correct: true：" + (r.stdout.strip().splitlines() or ["(没有输出)"])[-1]]
    return []


def main() -> int:
    fetch()
    if not available():
        print("跳过：缺少 g++、oneTBB 或 HIP-CPU 头文件")
        return 0
    bad = 0
    for a in sys.argv[1:]:
        probs = check(Path(a))
        print(("✗ " if probs else "✓ ") + a + ("：" + "；".join(probs) if probs else ""))
        bad += bool(probs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
