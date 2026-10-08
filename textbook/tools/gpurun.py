"""书中数字的 GPU 实测（《人工智能》第 14 轮附 4.4 节）。

需要在 GPU 上测的程序放在 ``chNN/code/runs/<名>/``：
- ``run.yaml``：显卡（basic / hopper / profile / multi，multi 为 8 块 A100）、命令（默认 ``python3 run.py``）、说明；
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
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "deploy" / "gpu-lab" / "wqgpu.py"
PENDING = "__pending__"
LAMBDA = os.environ.get("LAMBDA_URL", "https://cloud.lambda.ai/api/v1")
TYPES = {"basic": "gpu_1x_a10", "hopper": "gpu_1x_h100_sxm5", "profile": "gpu_1x_a10",
         "multi": "gpu_8x_a100"}          # multi：8 块 A100 SXM（NVSwitch），第 6 章多 GPU 与集合通信


def _chdir(no) -> str:
    """章的目录名：普通章 ch07，数学篇 chM1（第 26 轮）。"""
    s = str(no)
    return f"ch{int(s):02d}" if s.isdigit() else f"ch{s}"


def _chkey(no):
    s = str(no)
    return int(s) if s.isdigit() else int(s[1:]) - 1000


def runs(book_root: Path, chapters: set[str]) -> list[tuple[str, str, Path]]:
    out = []
    for ch in sorted(chapters, key=_chkey):
        base = book_root / _chdir(ch) / "code" / "runs"
        for d in sorted(base.glob("*/run.yaml")) if base.exists() else []:
            out.append((ch, d.parent.name, d.parent))
    return out


def fingerprint(folder: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(x for x in folder.rglob("*") if x.is_file() and x.name not in ("out.json", "env.json") and "__pycache__" not in x.parts):
        h.update(str(p.relative_to(folder)).encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def values(book_root: Path, chapters: set[str], status: dict[str, str]) -> tuple[dict[str, dict], list[tuple[str, str, str]]]:
    """({名: 数值或 {__pending__: True}}, [(级别, 位置, 说明)])。"""
    status = {str(k): v for k, v in (status or {}).items()}     # 章号可能是数字也可能是 "M1"（第 26 轮）
    vals, probs = {}, []
    for ch, name, folder in runs(book_root, chapters):
        rec_p = folder.parent / f"{name}.json"
        where = f"第 {ch} 章 code/runs/{name}"
        if not rec_p.exists():
            vals[name] = {PENDING: True}
            level = "warning" if status.get(str(ch), "draft") == "draft" else "error"
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
    # Lambda 的接口在 Cloudflare 后面，Python 默认的 User-Agent 会被拒（403），所以显式带一个
    req = urllib.request.Request(LAMBDA + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {os.environ['LAMBDA_KEY'].strip()}", "Content-Type": "application/json",
                                          "Accept": "application/json", "User-Agent": "wenquest-gpu/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode() or "{}").get("data") or {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Lambda {method} {path}: HTTP {e.code} {e.read().decode(errors='replace')[:500]}") from None


def _opts() -> list[str]:
    return ["-i", os.environ["LAMBDA_SSH_KEY_FILE"], "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=20"]


def _ssh(ip: str, command: str) -> None:
    subprocess.run(["ssh", *_opts(), f"ubuntu@{ip}", command], check=True)


def _scp(src: str, dst: str) -> None:
    subprocess.run(["scp", "-r", *_opts(), src, dst], check=True)


def pick_region(kind: str, prefer: str = "us-east-1") -> str:
    """有空闲机器的区域（多卡机器常常某个区域没有）；优先 prefer。都没有时报错，说明哪种机器没货。"""
    info = _api("GET", "/instance-types").get(kind) or {}
    regions = [r.get("name") for r in info.get("regions_with_capacity_available") or [] if r.get("name")]
    if not regions:
        raise RuntimeError(f"Lambda 上 {kind} 现在没有空闲的机器，稍后再试")
    return prefer if prefer in regions else regions[0]


def execute(folder: Path, region: str = "") -> dict:
    cfg = yaml.safe_load((folder / "run.yaml").read_text(encoding="utf-8")) or {}
    kind = TYPES[cfg.get("显卡", "basic")]
    region = region or pick_region(kind)
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


def main() -> int:
    ap = argparse.ArgumentParser(description="书中数字的 GPU 实测")
    ap.add_argument("cmd", choices=["list", "run"])
    ap.add_argument("book")
    ap.add_argument("chapter", type=int)
    ap.add_argument("--name", default="")
    ap.add_argument("--stale", action="store_true", help="只测没有记录或指纹不符的")
    a = ap.parse_args()
    root = ROOT / "textbook" / a.book
    failed = []
    for ch, name, folder in runs(root, {a.chapter}):
        if a.name and name != a.name:
            continue
        rec_p = folder.parent / f"{name}.json"
        fresh = rec_p.exists() and json.loads(rec_p.read_text(encoding="utf-8")).get("fingerprint") == fingerprint(folder)
        print(f"{name}: {'有记录' if fresh else '待实测'}")
        if a.cmd == "run" and not (a.stale and fresh):
            try:                                            # 一个失败不影响其余的；最后统一报告
                rec = execute(folder)
                print("  ✓", rec["env"].get("gpu"), rec["values"])
            except Exception as e:                          # noqa: BLE001
                print(f"  ✗ {name}：{e}")
                failed.append(name)
    if failed:
        print("没有测成：" + "、".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
