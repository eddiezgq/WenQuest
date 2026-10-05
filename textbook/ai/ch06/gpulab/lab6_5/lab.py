# GPU 实验 6.5 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 6.5　读 Nsight Compute 报告
# %%
import sys; sys.path.insert(0, "..")
import csv
import io
import json
import wqgpu
env = wqgpu.check(("gpu", "nvcc", "ncu"))
# %% [markdown]
# ## 1. 正常运行一次
# `gemm.cu` 就是第 5 章的程序 5.7.1。
# %%
wqgpu.sh("nvcc -O3 -arch=native -o gemm gemm.cu -lcublas")
r = json.loads(wqgpu.sh("./gemm 4096").splitlines()[-1])
for k in ("naive", "tiled", "regtile", "vec", "dbuf", "wmma", "cublas"):
    print(f"{k:8s} {r[k + '_GFs']:9.0f} GFLOP/s")
# %% [markdown]
# ## 2. 用 ncu 分析三个版本
# 读不了计数器的机器会报 ERR_NVGPUCTRPERM，这时请改用书中表 6.5.1 的实测记录。
# %%
M = {"sm": "sm__throughput.avg.pct_of_peak_sustained_elapsed", "mem": "gpu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed",
     "dram_rd": "dram__bytes_read.sum", "dram_wr": "dram__bytes_write.sum", "wf": "l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum",
     "conf": "l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_ld.sum",
     "long": "smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct", "mio": "smsp__warp_issue_stalled_mio_throttle_per_warp_active.pct"}


import subprocess
# 能用 sudo 就用（虚拟机上一般可以），否则直接运行 ncu
SUDO = "sudo -n " if subprocess.run("sudo -n true", shell=True, capture_output=True).returncode == 0 else ""


def profile(kernel):
    out = wqgpu.sh(f"{SUDO}ncu --clock-control none --kernel-name {kernel} --launch-count 1 --csv --print-units base "
                   f"--metrics {','.join(M.values())} ./gemm 4096")
    rows = csv.DictReader(io.StringIO(out[out.index('"ID"'):]))
    v = {row["Metric Name"]: float(row["Metric Value"].replace(",", "")) for row in rows}
    r = {k: v.get(m, -1.0) for k, m in M.items()}
    r["dram"] = r["dram_rd"] + r["dram_wr"] if min(r["dram_rd"], r["dram_wr"]) >= 0 else -1.0
    return r


prof, can = {}, 1
for k in ("tiled", "regtile", "vec"):
    try:
        prof[k] = profile(k)
        p = prof[k]
        print(f"{k:8s} SM {p['sm']:5.1f}%  内存 {p['mem']:5.1f}%  显存读写 {p['dram'] / 1e9:6.2f} GB  共享内存访问 {p['wf'] / 1e6:7.1f} M"
              f"  冲突 {p['conf'] / 1e6:7.1f} M  long {p['long']:5.1f}%  MIO {p['mio']:5.1f}%")
    except (RuntimeError, ValueError) as e:
        print("读不了性能计数器：", str(e)[:200])
        can = 0
        break
# %% [markdown]
# ## 3. 改一处再测
# 把 `gemm.cu` 中 `constexpr int T = 32;` 改成 16，重新运行第 1、2 格，比较 tiled 的变化。
# %% [markdown]
# ## 4. 回传结果
# %%
nan = -1.0                                                   # 没测到的记为 −1
wqgpu.submit(can_profile=can, tiled_GFs=r["tiled_GFs"], vec_GFs=r["vec_GFs"],
             tiled_sm_pct=prof.get("tiled", {}).get("sm", nan), vec_sm_pct=prof.get("vec", {}).get("sm", nan),
             tiled_mio=prof.get("tiled", {}).get("mio", nan), vec_mio=prof.get("vec", {}).get("mio", nan),
             tiled_dram_GB=prof["tiled"]["dram"] / 1e9 if "tiled" in prof and prof["tiled"]["dram"] >= 0 else nan)
