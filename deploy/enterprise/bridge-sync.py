#!/usr/bin/env python3
"""企业服务器与教育服务器网关之间的交接桥（第 146 轮）。deploy 用户的 crontab 每分钟跑一次。

开通程序（wenquest-ops 的 pilot-runner.sh）和网关原来共用一台机器上的文件夹 /opt/wenquest/pilot-queue；
质量 ERP 搬到企业服务器以后，这个脚本在两边之间搬文件：
  取回来：req-*（开通申请）、cmd-*（停用 / 恢复）、trial-*（体验账号），写进本机文件夹后告诉网关删掉；
  送回去：state-*（进度）、res-*、res-trial-*（账号，送到就删）、host.json（内存）；
  名单：开通了的企业网址，写成 allow/<网址> 空文件，Caddy 只给这些网址办证书。
设置在 /opt/wenquest/edge/.env：WQ_PILOT_BRIDGE_KEY（空 = 桥关着，什么都不做）、WQ_BRIDGE_URL（默认 https://learn.<SITE_DOMAIN>）。
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q = Path(os.environ.get("WQO_PILOT_QUEUE", "/opt/wenquest/pilot-queue"))
ALLOW = HERE / "allow"
UP = re.compile(r"^((state|res|res-trial)-[a-z0-9-]{1,40}|host)\.json$")
DOWN = re.compile(r"^(req|cmd|trial)-[a-z0-9-]{1,40}\.json$")
DOMAIN = re.compile(r"^[a-z0-9.-]{3,200}$")


def env() -> dict:
    out = {}
    f = HERE / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def call(base: str, key: str, method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"x-bridge-key": key, "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"{}")


def put(path: Path, text: str) -> None:
    tmp = path.parent / f".{path.name}.tmp"
    tmp.write_text(text, encoding="utf-8")
    tmp.chmod(0o644)
    tmp.replace(path)


def main() -> int:
    e = env()
    key = e.get("WQ_PILOT_BRIDGE_KEY", "")
    if not key:
        return 0
    base = (e.get("WQ_BRIDGE_URL") or f"https://learn.{e.get('SITE_DOMAIN', '')}").rstrip("/") + "/api/v1/pilot-bridge"
    Q.mkdir(parents=True, exist_ok=True)
    ALLOW.mkdir(parents=True, exist_ok=True)

    got = [f for f in call(base, key, "GET", "/outbox").get("files", []) if DOWN.match(f.get("name", ""))]
    for f in got:
        put(Q / f["name"], f["text"])
    if got:
        call(base, key, "POST", "/ack", {"names": [f["name"] for f in got]})
        print("took", ", ".join(f["name"] for f in got))

    ups = [p for p in sorted(Q.glob("*.json")) if UP.match(p.name)]
    if ups:
        call(base, key, "POST", "/inbox", {"files": [{"name": p.name, "text": p.read_text(encoding="utf-8")} for p in ups]})
        for p in ups:
            if p.name.startswith("res-"):           # 账号和初始密码：网关发完邮件就删，这边送到也删
                p.unlink(missing_ok=True)
                print("sent", p.name)

    want = {d for d in call(base, key, "GET", "/tenants").get("domains", []) if DOMAIN.match(d)}
    have = {p.name for p in ALLOW.iterdir() if not p.name.startswith(".")}
    for d in want - have:
        (ALLOW / d).touch()
    for d in have - want:
        (ALLOW / d).unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                         # noqa: BLE001  下一分钟再试；写进日志
        print("bridge-sync:", type(exc).__name__, exc, file=sys.stderr)
        sys.exit(1)
