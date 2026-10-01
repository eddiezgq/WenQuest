# -*- coding: utf-8 -*-
"""把零件库用到的第三方仓库按固定提交取到 library/vendor_src/（不进仓库）。本地和 library.yml 都用它。

    python3 tools/fetch_sources.py              # 全部：Menagerie、FreeCAD-library、robot_descriptions 及其各模型仓库
    python3 tools/fetch_sources.py rd           # 只取 robot_descriptions 的模型仓库（按 vendor/rd_repos.yaml）
已经取过且提交一致的跳过。
"""
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wqlib import ROOT  # noqa: E402

SRC = ROOT / "vendor_src"


def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fetch(dest, url, commit, sparse=None):
    dest = Path(dest)
    if (dest / ".git").exists():
        try:
            if git("rev-parse", "HEAD", cwd=dest) == commit:
                if sparse:
                    git("sparse-checkout", "set", "--no-cone", *sparse, cwd=dest)
                return "已有"
        except subprocess.CalledProcessError:
            pass
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        git("init", "-q", cwd=dest)
        git("remote", "add", "origin", url, cwd=dest)
    args = ["fetch", "-q", "--depth", "1"]
    if sparse:
        git("sparse-checkout", "set", "--no-cone", *sparse, cwd=dest)
        args.append("--filter=blob:none")
    git(*args, "origin", commit, cwd=dest)
    git("checkout", "-q", "FETCH_HEAD", cwd=dest)
    return "取到"


def pin(name):
    return yaml.safe_load((ROOT / "vendor" / name).read_text(encoding="utf-8"))


def main(which=("menagerie", "fclib", "rd"), strict=False):
    if "menagerie" in which:
        p = pin("menagerie.yaml")
        print("Menagerie:", fetch(SRC / "mujoco_menagerie", p["repo"] + ".git", p["commit"]))
    if "fclib" in which:
        p = pin("freecad_library.yaml")
        print("FreeCAD-library:", fetch(SRC / "FreeCAD-library", p["repo"] + ".git", p["commit"],
                                        sparse=["/index.html", "/thumbnails/", "/LICENSE-Assets"]))
    if "rd" in which:
        p = pin("robot_descriptions.yaml")
        print("robot_descriptions:", fetch(SRC / "robot_descriptions", p["repo"] + ".git", p["commit"]))
        repos = ROOT / "vendor" / "rd_repos.yaml"
        if repos.exists():
            for key, r in (yaml.safe_load(repos.read_text(encoding="utf-8")) or {}).items():
                try:
                    print("  {}: {}".format(key, fetch(SRC / "rd" / key, r["url"], r["commit"], sparse=r.get("sparse"))))
                except subprocess.CalledProcessError as e:      # 取不到的跳过（import_rd 不会为它建条目）
                    print("  {}: 取不到（{}）".format(key, (e.stderr or "")[-160:].strip()))
                    if strict:
                        raise


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--strict"]
    main(tuple(args) or ("menagerie", "fclib", "rd"), strict="--strict" in sys.argv)
