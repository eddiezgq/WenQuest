"""算例 10.2.1：移植的代价清单（10.2、10.6 节）。

HIPIFY 把 CUDA 的接口名机械地换成 HIP 的名字（`cudaMalloc` → `hipMalloc`），换不了的是**语义**：线程束宽度、
线程束级指令的掩码、张量核心的接口、厂商自己的库。本程序扫描本书第 4—7 章的全部 .cu 源文件，按几类模式数一数
各自出现多少次，给出“哪些能自动换、哪些要人改”的清单。这份清单在没有 AMD 卡的机器上就能得到，
是估计移植工作量的第一步。

分三类：
- 原样不动：内建变量与限定符（threadIdx、__shared__、__global__ 等）——HIP 里是同一个名字，一个字都不用改；
- 自动替换：运行时与驱动接口（cuda* → hip*）、头文件、原子操作；
- 要人看一眼：线程束级指令（__shfl_*_sync、__ballot_sync、__syncwarp）与写死的 32、0xffffffff 掩码；
- 要重写：张量核心（wmma、mma）、厂商库（cuBLAS、cuDNN、CUB、NCCL、Thrust）、内联汇编（PTX）。
"""
import hashlib
import re
from pathlib import Path

from bookout import out

AI = Path(__file__).resolve().parents[2]                 # textbook/ai
_ALL = sorted(p for ch in ("ch04", "ch05", "ch06", "ch07") for p in (AI / ch).rglob("*.cu"))
# 同一个程序在 code/runs 与 gpulab 下各有一份（GPU 实验要带着源码上机，见第 14 轮附），内容相同的只数一遍；
# 各实测文件夹里的 check.cuh、bench.cuh 也是同一份头文件的副本，不计入（只数 .cu）
_seen: set = set()
FILES = []
for _p in _ALL:
    _h = hashlib.sha256(_p.read_bytes()).hexdigest()
    if _h not in _seen:
        _seen.add(_h)
        FILES.append(_p)

PATS = {
    # 原样不动：HIP 里是同一个名字
    "builtin": (r"\b(?:threadIdx|blockIdx|blockDim|gridDim|__syncthreads|__shared__|__global__|__device__)\b", "same"),
    # 自动替换（HIPIFY 能做）
    "api": (r"\b(?:cuda[A-Z]\w+|cuda_runtime\.h|cuda_fp16\.h)", "auto"),      # cudaMalloc、cudaMemcpy、头文件……
    "atomic": (r"\batomic(?:Add|Max|Min|CAS|Exch)\b", "auto"),
    "launch": (r"<<<", "auto"),                          # 核函数的启动语法
    # 要人看一眼（与 32 道的线程束绑在一起）
    "shuffle": (r"\b__(?:shfl|ballot|activemask|any|all)\w*_sync\b", "hand"),
    "mask": (r"_sync\s*\(\s*0x[fF]{8}[uU]?\s*,", "hand"),   # 作为线程束掩码用的 32 位全 1（不是别处的哨兵值）
    "warpconst": (r"\b(?:16|32)\s*;\s*\w+\s*>\s*0", "hand"),   # 写死起点的线程束内归约循环
    # 要重写
    "wmma": (r"\b(?:wmma::|nvcuda|mma_sync)\w*", "rewrite"),
    "match": (r"\b__match_(?:any|all)\w*_sync\b", "rewrite"),     # HIP 没有对应物
    "lib": (r"\b(?:cublas\w+|cudnn\w+|cub::|ncclu?\w+|thrust::)", "rewrite"),
    "asm": (r"(?:\b__?asm__?\b\s*(?:volatile)?\s*\()", "rewrite"),
}

counts = {k: 0 for k in PATS}
per_file = {}
for p in FILES:
    src = p.read_text(encoding="utf-8")
    src = re.sub(r"//[^\n]*|/\*.*?\*/", "", src, flags=re.S)         # 注释里的名字不算
    hit = {k: len(re.findall(r, src)) for k, (r, _) in PATS.items() if r}
    for k, n in hit.items():
        counts[k] += n
    per_file[str(p.relative_to(AI))] = hit

v = {"n_files": len(FILES), "n_lines": sum(len(p.read_text(encoding="utf-8").splitlines()) for p in FILES)}
for k, n in counts.items():
    v["n_" + k] = n
for kind in ("same", "auto", "hand", "rewrite"):
    v["n_" + kind] = sum(n for k, n in counts.items() if PATS[k][1] == kind)
v["n_change"] = v["n_auto"] + v["n_hand"] + v["n_rewrite"]           # 真正要改的处数（不含原样不动的）
v["pct_auto"] = v["n_auto"] / v["n_change"] * 100

# 哪些文件一处要人改的地方都没有（纯算术的核函数，HIPIFY 之后直接能编译）
v["n_clean"] = sum(1 for f, h in per_file.items()
                   if all(h[k] == 0 for k, (_, kind) in PATS.items() if kind in ("hand", "rewrite")))
# 最难移植的一个文件：要重写的处数最多
worst = max(per_file, key=lambda f: (sum(per_file[f][k] for k, (_, kd) in PATS.items() if kd == "rewrite"),
                                     sum(per_file[f][k] for k, (_, kd) in PATS.items() if kd == "hand")))
v["worst"] = worst
v["worst_rewrite"] = sum(per_file[worst][k] for k, (_, kd) in PATS.items() if kd == "rewrite")

out(**v)
