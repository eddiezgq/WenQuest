# -*- coding: utf-8 -*-
"""教材算例程序的书外依赖记录（第 60 轮 D-1）：build.py 运行程序时把本目录放在 PYTHONPATH 最前，并设 WQ_BOOK_DEPS=<文件>。
程序打开（含 import 读到的 .py / .pyc）的仓库内文件都记下来，程序结束时写进那个文件，一行一个绝对路径。
build.py 用它检查：书外文件都在 meta.yaml 的 program_deps 里登记了；缓存命中时还核对这些文件没变。"""
import os
import sys

_OUT = os.environ.get("WQ_BOOK_DEPS")
_ROOT = os.environ.get("WQ_REPO_ROOT")
if _OUT and _ROOT:
    import atexit

    _seen = set()
    _root = os.path.realpath(_ROOT) + os.sep

    def _src(p):
        if "__pycache__" in p and p.endswith(".pyc"):                 # 读的是编译缓存：记它的源文件
            d, f = os.path.split(p)
            return os.path.join(os.path.dirname(d), f.split(".")[0] + ".py")
        return p

    def _hook(event, args):
        if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
            if any(c in mode for c in "wax+"):
                return
            try:
                p = os.fsdecode(args[0])
            except Exception:  # noqa: BLE001
                return
            if not os.path.isabs(p):
                p = os.path.join(os.getcwd(), p)
            p = os.path.realpath(_src(p))
            if p.startswith(_root):
                _seen.add(p)

    def _dump():
        try:
            with open(_OUT, "a", encoding="utf-8") as f:              # 程序再起的子进程也写这里：追加
                f.write("".join(p + "\n" for p in sorted(_seen)))
        except OSError:
            pass

    sys.addaudithook(_hook)
    atexit.register(_dump)
