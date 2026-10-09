#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""比对两边数字工厂的共有代码（第 30 轮 H-9）：本仓库 factory/ 与 freecad-ai-parts 的 factory/。

哪些路径只在一边、哪些两边各自实现，写在 factory/SYNC.md 的 sync-a-only、sync-b-only、sync-own 代码块里；
其余都是共有，应当逐字一致。报告：共有文件内容不同、只在这边、只在那边。有差异退出码 1，没有 0。

用法：python3 tools/factory_sync.py [那边仓库的路径] [--diff [文件 ...]]
只用标准库。
"""
import argparse
import difflib
import fnmatch
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A_ROOT = os.path.dirname(HERE)
DEFAULT_B = "/home/claude/freecad-ai-parts"
SKIP_DIRS = {"node_modules", "dist", "__pycache__", ".pytest_cache", ".git", ".node-red"}
SKIP_FILES = ("*.pyc", ".DS_Store")


def read_rules(sync_md):
    """SYNC.md 里三个代码块 → {类别: [模式]}"""
    text = open(sync_md, encoding="utf-8").read()
    rules = {}
    for kind, body in re.findall(r"```(sync-a-only|sync-b-only|sync-own)\n(.*?)```", text, re.S):
        pats = []
        for line in body.splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                pats.append(line)
        rules[kind] = pats
    return rules


def matches(path, pats):
    for p in pats:
        if p.endswith("/"):                      # 整个目录：路径的前几级与模式相符
            parts = path.split("/")
            k = p.count("/")
            if len(parts) > k and fnmatch.fnmatch("/".join(parts[:k]) + "/", p):
                return True
        elif fnmatch.fnmatch(path, p):
            return True
    return False


def list_files(repo):
    """repo/factory 下的文件（相对 factory/）。是 git 仓库时：入了 git 的 + 没被 .gitignore 挡住的新文件，减去已删的。"""
    base = os.path.join(repo, "factory")
    if not os.path.isdir(base):
        sys.exit("找不到 {}".format(base))
    try:
        out = subprocess.run(["git", "-C", repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "factory"],
                             capture_output=True, check=True).stdout.decode("utf-8")
        files = {f[len("factory/"):] for f in out.split("\0") if f}
        files = {f for f in files if os.path.isfile(os.path.join(base, f))}        # 已删、还没提交的不算
    except (OSError, subprocess.CalledProcessError):
        files = set()
        for d, dirs, names in os.walk(base):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for n in names:
                files.add(os.path.relpath(os.path.join(d, n), base).replace(os.sep, "/"))
    return {f for f in files if not any(part in SKIP_DIRS for part in f.split("/"))
            and not any(fnmatch.fnmatch(os.path.basename(f), p) for p in SKIP_FILES)}


def same(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def show_diff(a, b, rel):
    try:
        la = open(a, encoding="utf-8").read().splitlines(True)
        lb = open(b, encoding="utf-8").read().splitlines(True)
    except UnicodeDecodeError:
        print("    （二进制文件，不打印差异）")
        return
    sys.stdout.writelines(difflib.unified_diff(la, lb, "这边/factory/" + rel, "那边/factory/" + rel))


def main(argv=None):
    ap = argparse.ArgumentParser(description="比对两边数字工厂的共有代码（清单见 factory/SYNC.md）")
    ap.add_argument("other", nargs="?", default=DEFAULT_B, help="那边仓库（freecad-ai-parts）的路径，缺省 " + DEFAULT_B)
    ap.add_argument("--diff", nargs="*", metavar="文件", help="打印逐行差异；不跟文件名时打印全部不同的文件")
    a = ap.parse_args(argv)
    rules = read_rules(os.path.join(A_ROOT, "factory", "SYNC.md"))
    skip = [p for k in ("sync-a-only", "sync-b-only", "sync-own") for p in rules.get(k, [])]
    fa, fb = list_files(A_ROOT), list_files(os.path.abspath(a.other))
    fa = {f for f in fa if not matches(f, skip)}
    fb = {f for f in fb if not matches(f, skip)}
    base_a, base_b = os.path.join(A_ROOT, "factory"), os.path.join(os.path.abspath(a.other), "factory")
    differ = sorted(f for f in fa & fb if not same(os.path.join(base_a, f), os.path.join(base_b, f)))
    only_a, only_b = sorted(fa - fb), sorted(fb - fa)

    print("比对：{} ↔ {}（共有 {} 个文件；不比对的清单见 factory/SYNC.md）".format(base_a, base_b, len(fa & fb)))
    for title, rows in (("共有文件内容不同", differ), ("只在这边（问渠）", only_a), ("只在那边（freecad-ai-parts）", only_b)):
        print("\n{}：{} 个".format(title, len(rows)))
        for r in rows:
            print("  " + r)
    if a.diff is not None:
        want = set(a.diff) if a.diff else set(differ)
        for f in differ:
            if f in want:
                print("\n==== " + f)
                show_diff(os.path.join(base_a, f), os.path.join(base_b, f), f)
    n = len(differ) + len(only_a) + len(only_b)
    print("\n" + ("两边共有部分一致（0 差异）" if not n else "共 {} 处差异".format(n)))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
