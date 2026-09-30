# -*- coding: utf-8 -*-
"""FreeCAD-library 索引（附录 B.6 第 5 条、L13 第一期）：只收索引和缩略图，模型点击时从原仓库固定提交下载。

源：vendor/freecad_library.yaml 固定的提交，克隆到 WQ_FCLIB（默认 library/vendor_src/FreeCAD-library）。
    只需要文件清单（git ls-tree，部分克隆即可）、index.html（原仓库生成的缩略图对照）和 thumbnails/。
输出：<版本目录>/freecad-library.json 与 <版本目录>/freecad-library/thumbs/*.png
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wqlib  # noqa: E402

SRC = Path(os.environ.get("WQ_FCLIB", wqlib.ROOT / "vendor_src" / "FreeCAD-library"))
PIN = wqlib.ROOT / "vendor" / "freecad_library.yaml"


def pin():
    return yaml.safe_load(PIN.read_text(encoding="utf-8"))


def _files(src):
    if (src / ".git").exists():
        out = subprocess.run(["git", "-C", str(src), "-c", "core.quotepath=off", "ls-tree", "-r", "--name-only", "HEAD"],
                             check=True, capture_output=True, text=True).stdout
        return [x for x in out.split("\n") if x]
    return [str(p.relative_to(src)).replace(os.sep, "/") for p in src.rglob("*") if p.is_file()]


def _thumb_map(src):
    """原仓库 index.html 里每张卡片：FCStd 路径 → thumbnails/<md5>.png"""
    html = src / "index.html"
    if not html.exists():
        return {}
    s = html.read_text(encoding="utf-8", errors="replace")
    pat = r'href="https://github.com/FreeCAD/FreeCAD-library/blob/master/([^"?]+)\?raw=true"><img class="icon" src="(thumbnails/[0-9a-f]+\.png)"'
    return {urllib.parse.unquote(p): t for p, t in re.findall(pat, s)}


def build(ver_dir, src=SRC):
    """生成索引；源不存在时返回 None（本地没克隆就跳过）。"""
    src = Path(src)
    if not src.exists():
        return None
    cfg = pin()
    cats = cfg["categories"]
    files = _files(src)
    have = set(files)
    thumbs = _thumb_map(src)
    raw = "{}/raw/{}/".format(cfg["repo"], cfg["commit"])
    blob = "{}/blob/{}/".format(cfg["repo"], cfg["commit"])
    out_dir = Path(ver_dir) / "freecad-library" / "thumbs"
    out_dir.mkdir(parents=True, exist_ok=True)
    items, copied = [], 0
    for f in sorted(files):
        parts = f.split("/")
        if parts[0] not in cats or not f.lower().endswith(".fcstd"):
            continue
        stem = f[: -len(".fcstd")]
        formats = {"fcstd": raw + urllib.parse.quote(f)}
        for ext in ("step", "stp", "stl", "brep"):
            for cand in (stem + "." + ext, stem + "." + ext.upper()):
                if cand in have:
                    formats.setdefault("step" if ext == "stp" else ext, raw + urllib.parse.quote(cand))
        iid = "F-" + hashlib.md5(f.encode("utf-8")).hexdigest()[:10]
        thumb = None
        t = thumbs.get(f)
        if t and (src / t).exists():
            shutil.copyfile(src / t, out_dir / (iid + ".png"))
            thumb = "freecad-library/thumbs/{}.png".format(iid)
            copied += 1
        name = parts[-1].rsplit(".", 1)[0].replace("_", " ")
        items.append({"id": iid, "name": name, "path": parts[:-1],
                      "top": cats[parts[0]], "formats": formats, "thumb": thumb,
                      "source_url": blob + urllib.parse.quote(f)})
    doc = {"schema": 1, "collection": "freecad-library", "name": {"zh": "FreeCAD 零件库", "en": "FreeCAD Parts Library"},
           "repo": cfg["repo"], "commit": cfg["commit"], "license": cfg["license"], "attribution": cfg["attribution"],
           "note": {"zh": "只提供索引与缩略图；模型从原仓库下载，使用时须按 CC BY 3.0 署名（作者见原仓库）",
                    "en": "Index and thumbnails only; models download from the original repository. Attribution required (CC BY 3.0)."},
           "count": len(items), "items": items}
    (Path(ver_dir) / "freecad-library.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return {"id": "freecad-library", "name": doc["name"], "url": "freecad-library.json", "count": len(items),
            "thumbs": copied, "license": cfg["license"]}


if __name__ == "__main__":
    r = build(sys.argv[1] if len(sys.argv) > 1 else wqlib.ROOT / "build" / "library" / "dev")
    print(r or "没有 FreeCAD-library 源文件（WQ_FCLIB）")
