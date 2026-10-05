"""在 8 块 A100 的机器上依次启动 train.py：小型 Transformer 与约 8 亿参数的模型，各在 1 块 GPU（不包装）、8 块 GPU 的 DDP、
8 块 GPU 的 FSDP 下训练，汇总每步耗时、每块 GPU 的显存峰值、每秒词元数，写进 out.json（第 14 轮附 4.4 节）。"""
import json
import subprocess
import sys

import torch

P = torch.cuda.device_count()
assert P >= 8, f"需要 8 块 GPU，这台机器只有 {P} 块"
out = {"gpus": P, "torch": torch.__version__}
for size in ("small", "mid"):
    for mode, n in (("single", 1), ("ddp", P), ("fsdp", P)):
        subprocess.run([sys.executable, "-m", "torch.distributed.run", "--standalone", f"--nproc_per_node={n}",
                        "train.py", mode, size], check=True)
        r = json.load(open(f"result_{mode}_{size}_{n}.json"))
        for k, v in r.items():
            out[f"{size}_{mode}_{k}"] = v
    out[f"{size}_mem_ratio"] = out[f"{size}_ddp_peak_MB"] / out[f"{size}_fsdp_peak_MB"]
    out[f"{size}_scale_ddp"] = out[f"{size}_ddp_tok_s"] / out[f"{size}_single_tok_s"]
    out[f"{size}_scale_fsdp"] = out[f"{size}_fsdp_tok_s"] / out[f"{size}_single_tok_s"]
json.dump(out, open("out.json", "w"))
print(out)
