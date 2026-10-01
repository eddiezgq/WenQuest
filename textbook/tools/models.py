"""教材用到的零件库模型：从零件库发布版复制到 textbook/<book>/models/<id>/（entry.json、default.glb）。

    python3 tools/models.py robotics 2026.10.9 B-ARM-UR5E B-ARM-PANDA B-SCA-WQ4

从 GitHub 发布 library-v<版本> 下载网页包（需要 GH_TOKEN 或 GITHUB_TOKEN），取出这几个模型，写入 models/来源.md。
构建时只读这个文件夹，不联网，结果可以复现。
"""
from __future__ import annotations

import io
import json
import os
import sys
import tarfile
import urllib.request
from pathlib import Path

REPO = "eddiezgq/WenQuest"
ROOT = Path(__file__).resolve().parents[1]


def _get(url: str, accept: str = "application/vnd.github+json") -> bytes:
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    req = urllib.request.Request(url, headers={"Accept": accept, **({"Authorization": f"Bearer {tok}"} if tok else {})})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def fetch(book: str, version: str, ids: list[str]) -> None:
    rel = json.loads(_get(f"https://api.github.com/repos/{REPO}/releases/tags/library-v{version}"))
    asset = next(a for a in rel["assets"] if a["name"].startswith("library-web-"))
    data = _get(asset["url"], "application/octet-stream")
    out = ROOT / book / "models"
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for eid in ids:
            d = out / eid
            d.mkdir(parents=True, exist_ok=True)
            for name in ("entry.json", "default.glb"):
                f = tar.extractfile(f"./{version}/{eid}/{name}")
                (d / name).write_bytes(f.read())
    write_sources(out)


def write_sources(out: Path) -> None:
    lines = ["# 教材用到的零件库模型", "", "由 `textbook/tools/models.py` 从问渠零件库发布版复制，不要手改。", "",
             "| 模型 | 零件库版本 | 来源 | 许可证 |", "|---|---|---|---|"]
    for d in sorted(p for p in out.iterdir() if (p / "entry.json").exists()):
        e = json.loads((d / "entry.json").read_text(encoding="utf-8"))
        src = e.get("source") or {}
        lines.append(f"| {d.name} {e['name']['zh']} | {e.get('version', '')} | {src.get('attribution', '')} | {src.get('license', '')} |")
    (out / "来源.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    fetch(sys.argv[1], sys.argv[2], sys.argv[3:])
