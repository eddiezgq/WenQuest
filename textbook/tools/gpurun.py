"""书中数字的 GPU 实测（《人工智能》第 14 轮附 4.4 节）。

需要在 GPU 上测的程序放在 ``chNN/code/runs/<名>/``：
- ``run.yaml``：显卡（basic / hopper / profile）、命令（默认 ``python3 run.py``）、说明；
- 程序本身（.py、.cu 等）。命令运行结束时在当前文件夹写出 ``out.json``（{名称: 数值}）。

实测记录是 ``chNN/code/runs/<名>.json``：程序指纹（本文件夹全部文件的 SHA-256）、时间、平台、机器型号、环境
（GPU、驱动、CUDA……，由 deploy/gpu-lab/wqgpu.py 的 env() 记下）和测得的数值。正文用 ``{{<名>.<数值名>}}`` 引用。

构建时（build.py）：
- 有记录且指纹相符：数值照常填入；
- 没有记录：显示“〔待实测〕”，给提醒；这一章的状态不能超过“草稿”（否则报错）；
- 指纹不符（程序改过）：报错，要重测。

实测：``python3 textbook/tools/gpurun.py run ai 4 [--name run4_1]``，在 Lambda 上开一台机器，经 SSH 上传、运行、取回，
最后一定关机。需要环境变量 LAMBDA_KEY、LAMBDA_SSH_KEY_NAME（控制台登记的公钥名）、LAMBDA_SSH_KEY_FILE（私钥文件）。
GitHub 上由手动工作流 .github/workflows/gpu-run.yml 触发，密钥放在仓库的加密变量里。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "deploy" / "gpu-lab" / "wqgpu.py"
PENDING = "__pending__"
LAMBDA = os.environ.get("LAMBDA_URL", "https://cloud.lambda.ai/api/v1")
TYPES = {"basic": "gpu_1x_a10", "hopper": "gpu_1x_h100_sxm5", "profile": "gpu_1x_a10"}


def runs(book_root: Path, chapters: set[int]) -> list[tuple[int, str, Path]]:
    out = []
    for ch in sorted(chapters):
        base = book_root / f"ch{ch:02d}" / "code" / "runs"
        for d in sorted(base.glob("*/run.yaml")) if base.exists() else []:
            out.append((ch, d.parent.name, d.parent))
    return out


def fingerprint(folder: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(x for x in folder.rglob("*") if x.is_file() and x.name not in ("out.json", "env.json") and "__pycache__" not in x.parts):
        h.update(str(p.relative_to(folder)).encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def values(book_root: Path, chapters: set[int], status: dict[int, str]) -> tuple[dict[str, dict], list[tuple[str, str, str]]]:
    """({名: 数值或 {__pending__: True}}, [(级别, 位置, 说明)])。"""
    vals, probs = {}, []
    for ch, name, folder in runs(book_root, chapters):
        rec_p = folder.parent / f"{name}.json"
        where = f"第 {ch} 章 code/runs/{name}"
        if not rec_p.exists():
            vals[name] = {PENDING: True}
            level = "warning" if status.get(ch, "draft") == "draft" else "error"
            probs.append((level, where, "还没有实测记录，正文显示“〔待实测〕”" + ("" if level == "warning" else "；这一章的状态不能超过“草稿”")))
            continue
        rec = json.loads(rec_p.read_text(encoding="utf-8"))
        if rec.get("fingerprint") != fingerprint(folder):
            vals[name] = {PENDING: True}
            probs.append(("error", where, "程序在实测之后改过（指纹不符），要重新实测"))
            continue
        vals[name] = dict(rec.get("values") or {}, _gpu=rec.get("env", {}).get("gpu", ""), _driver=rec.get("env", {}).get("driver", ""),
                          _cuda=rec.get("env", {}).get("nvcc", ""), _date=str(rec.get("at", ""))[:10])
    return vals, probs


# ---------------------------------------------------------------- running on Lambda

def _api(method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(LAMBDA + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {os.environ['LAMBDA_KEY']}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode()).get("data") or {}


def _opts() -> list[str]:
    return ["-i", os.environ["LAMBDA_SSH_KEY_FILE"], "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=20"]


def _ssh(ip: str, command: str) -> None:
    subprocess.run(["ssh", *_opts(), f"ubuntu@{ip}", command], check=True)


def _scp(src: str, dst: str) -> None:
    subprocess.run(["scp", "-r", *_opts(), src, dst], check=True)


def execute(folder: Path, region: str = "us-east-1") -> dict:
    cfg = yaml.safe_load((folder / "run.yaml").read_text(encoding="utf-8")) or {}
    kind = TYPES[cfg.get("显卡", "basic")]
    command = cfg.get("命令") or "python3 run.py"
    iid = _api("POST", "/instance-operations/launch", {"region_name": region, "instance_type_name": kind,
                                                       "ssh_key_names": [os.environ["LAMBDA_SSH_KEY_NAME"]], "name": f"wq-run-{folder.name}"})["instance_ids"][0]
    try:
        ip = ""
        for _ in range(120):                                # up to 20 minutes to boot
            inst = _api("GET", f"/instances/{iid}")
            if inst.get("status") == "active" and inst.get("ip"):
                ip = inst["ip"]
                break
            time.sleep(10)
        if not ip:
            raise RuntimeError("the machine did not come up")
        time.sleep(20)
        _ssh(ip, "mkdir -p wqrun")
        _scp(f"{folder}/.", f"ubuntu@{ip}:wqrun/")
        _scp(str(HELPER), f"ubuntu@{ip}:wqrun/wqgpu.py")
        _ssh(ip, f"cd wqrun && python3 -c 'import json, wqgpu; json.dump(wqgpu.env(), open(\"env.json\", \"w\"))' && {command}")
        tmp = folder / ".fetched"
        tmp.mkdir(exist_ok=True)
        for f in ("out.json", "env.json"):
            _scp(f"ubuntu@{ip}:wqrun/{f}", str(tmp / f))
        rec = {"name": folder.name, "fingerprint": fingerprint(folder), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "platform": "lambda", "region": region, "instance_type": kind,
               "env": json.loads((tmp / "env.json").read_text()), "values": json.loads((tmp / "out.json").read_text())}
        for f in tmp.iterdir():
            f.unlink()
        tmp.rmdir()
        (folder.parent / f"{folder.name}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return rec
    finally:
        _api("POST", "/instance-operations/terminate", {"instance_ids": [iid]})       # always stop the machine


def main() -> None:
    ap = argparse.ArgumentParser(description="书中数字的 GPU 实测")
    ap.add_argument("cmd", choices=["list", "run"])
    ap.add_argument("book")
    ap.add_argument("chapter", type=int)
    ap.add_argument("--name", default="")
    ap.add_argument("--stale", action="store_true", help="只测没有记录或指纹不符的")
    a = ap.parse_args()
    root = ROOT / "textbook" / a.book
    for ch, name, folder in runs(root, {a.chapter}):
        if a.name and name != a.name:
            continue
        rec_p = folder.parent / f"{name}.json"
        fresh = rec_p.exists() and json.loads(rec_p.read_text(encoding="utf-8")).get("fingerprint") == fingerprint(folder)
        print(f"{name}: {'有记录' if fresh else '待实测'}")
        if a.cmd == "run" and not (a.stale and fresh):
            rec = execute(folder)
            print("  ✓", rec["env"].get("gpu"), rec["values"])


if __name__ == "__main__":
    sys.exit(main())
