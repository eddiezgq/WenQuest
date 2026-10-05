"""用 Nsight Compute 测第 5 章矩阵乘法（程序 5.7.1，这里是它的一份拷贝）各版本的性能计数器（6.5、6.6 节）。
每个核函数只分析第一次启动，n = 4096。需要读 GPU 性能计数器的权限：Lambda 的虚拟机上用 sudo 运行 ncu。
ncu 默认把 GPU 锁在基础频率（--clock-control base），这里改为不锁（none），使耗时与正常运行可比；它仍在每遍重放前清空缓存
（--cache-control all 是默认值），所以第一次读 A、B 一定来自显存。
把每个核函数的耗时、显存与 L2 流量、SM 与内存的利用率、占用率、共享内存的访问与存储体冲突、几种停顿原因写进 out.json，
并算出按实际流量的计算强度（2n³ ÷ 字节数；共享内存按每次访问 128 字节计，只计读）。机器上的 ncu 不认识的计数器先剔除，对应的值记为 −1。"""
import csv
import glob
import io
import json
import os
import shutil
import subprocess

N = 4096
KERNELS = {"naive": "naive", "tiled": "tiled", "regtile": "regtile", "vec": "vec", "dbuf": "dbuf", "wmma": "wmma_gemm",
           "cublas": "regex:(sgemm|gemm.*f32f32.*ffma|simt.*gemm)"}   # cuBLAS 单精度核函数的名字随版本而变
METRICS = {
    "ms": "gpu__time_duration.sum",
    "dram_rd": "dram__bytes_read.sum",
    "dram_wr": "dram__bytes_write.sum",
    "l2": "lts__t_bytes.sum",
    "sm_pct": "sm__throughput.avg.pct_of_peak_sustained_elapsed",
    "mem_pct": "gpu__compute_memory_throughput.avg.pct_of_peak_sustained_elapsed",
    "occ_pct": "sm__warps_active.avg.pct_of_peak_sustained_active",
    "issue_pct": "smsp__issue_active.avg.pct_of_peak_sustained_active",
    "conf": "l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_ld.sum",
    "wf": "l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum",
    "regs": "launch__registers_per_thread",
    "lds": "smsp__inst_executed_op_shared_ld.sum",
    "stall_long": "smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct",
    "stall_mio": "smsp__warp_issue_stalled_mio_throttle_per_warp_active.pct",
    "stall_short": "smsp__warp_issue_stalled_short_scoreboard_per_warp_active.pct",
    "stall_bar": "smsp__warp_issue_stalled_barrier_per_warp_active.pct",
}


def find_ncu():
    for c in [shutil.which("ncu"), *sorted(glob.glob("/usr/local/cuda*/bin/ncu")), *sorted(glob.glob("/opt/nvidia/nsight-compute/*/ncu"))]:
        if c and os.path.exists(c):
            return c
    raise SystemExit("找不到 ncu")


ncu = find_ncu()
subprocess.run(["nvcc", "-O3", "-arch=native", "-o", "gemm", "gemm.cu", "-lcublas"], check=True)
known = subprocess.run(["sudo", ncu, "--query-metrics"], capture_output=True, text=True).stdout
metrics = {k: m for k, m in METRICS.items() if m.split(".")[0] in known}
missing = [k for k in METRICS if k not in metrics]
print("这台机器的 ncu 没有这些计数器：", missing)
REQUIRED = {"ms", "dram_rd", "dram_wr", "l2", "sm_pct", "mem_pct", "occ_pct", "wf", "conf", "regs",
            "stall_long", "stall_mio", "stall_short", "stall_bar"}       # 书中表格用到的，缺了就停下，不让表里出现 −1
assert not REQUIRED & set(missing), f"缺少书中要用的计数器：{sorted(REQUIRED & set(missing))}"
out = {"n": N, "missing": len(missing)}
failed = []
for name, filt in KERNELS.items():
    cmd = ["sudo", ncu, "--clock-control", "none", "--kernel-name-base", "demangled" if name == "cublas" else "function",
           "--kernel-name", filt, "--launch-count", "1", "--csv", "--print-units", "base",
           "--metrics", ",".join(metrics.values()), "./gemm", str(N)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or '"ID"' not in r.stdout:                     # 没匹配到核函数，或 ncu 出错：记下，接着测别的
        print(f"{name}：ncu 没有结果", r.stderr[-500:])
        failed.append(name)
        continue
    rows = [row for row in csv.DictReader(io.StringIO(r.stdout[r.stdout.index('"ID"'):]))]
    print(name, "→", rows[0].get("Kernel Name", "")[:120])
    val = {row["Metric Name"]: float(row["Metric Value"].replace(",", "")) for row in rows}
    for k in METRICS:
        out[f"{name}_{k}"] = val.get(METRICS[k], -1.0)
    out[f"{name}_ms"] = out[f"{name}_ms"] / 1e6 if out[f"{name}_ms"] > 0 else -1.0          # 纳秒 → 毫秒
    lds = out[f"{name}_lds"]
    out[f"{name}_conf2"] = (out[f"{name}_wf"] - lds) / 1e6 if lds >= 0 and out[f"{name}_wf"] >= 0 else -1.0   # 交叉核对：访问次数 − 读指令数（只对 32 位的读有意义；128 位的读本来就要分 4 次）
    for k in ("conf", "wf", "lds"):
        out[f"{name}_{k}"] = out[f"{name}_{k}"] / 1e6 if out[f"{name}_{k}"] >= 0 else -1.0   # 百万次
    dram = max(out[f"{name}_dram_rd"], 0) + max(out[f"{name}_dram_wr"], 0)
    out[f"{name}_dram_GB"] = dram / 1e9
    out[f"{name}_l2_GB"] = out[f"{name}_l2"] / 1e9 if out[f"{name}_l2"] > 0 else -1.0
    out[f"{name}_I_dram"] = 2 * N ** 3 / dram if dram > 0 else -1.0
    out[f"{name}_I_l2"] = 2 * N ** 3 / out[f"{name}_l2"] if out[f"{name}_l2"] > 0 else -1.0
    wf = out[f"{name}_wf"] * 1e6                                                # 共享内存的读：每次访问 32 个存储体 × 4 字节
    out[f"{name}_I_smem"] = 2 * N ** 3 / (wf * 128) if wf > 0 else -1.0
    out[f"{name}_TFs"] = 2 * N ** 3 / (out[f"{name}_ms"] * 1e-3) / 1e12 if out[f"{name}_ms"] > 0 else -1.0
assert not failed, f"这些核函数没有测到：{failed}"
json.dump(out, open("out.json", "w"))
print(out)
