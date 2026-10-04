"""云端 GPU 实验（《人工智能》第 14 轮附 4.3 节）：教材里的 ``::: GPU实验 4.1`` 与它的文件。

每个 GPU 实验是 ``chNN/gpulab/<src>/`` 下的一个文件夹：

- ``lab.yaml``：标题、目的（中英）、显卡档次（basic / hopper / profile）、结果（名、说明、单位）、要一起上传的文件、
  实际问题（标题、内容，中英；可选），
  以及与浏览器实验相同的指导书内容（原理、步骤、数据表、注意、思考题）。数据表中写 ``{{结果名}}`` 的格子，
  学生回传结果后由问渠填好。
- ``lab.py``：实验笔记本，用“百分号格式”写（``# %%`` 开始一个代码格，``# %% [markdown]`` 开始一个说明格，
  说明格的每行以 ``# `` 开头），便于审阅和比较；构建时转成 JupyterLab 的 .ipynb。
  第一个代码格调用 ``wqgpu.check(...)``，最后要有 ``wqgpu.submit(...)``，回传 lab.yaml 中登记的全部结果。
- 其余文件（如 ``vadd.cu``）在 lab.yaml 的“文件”中列出。

构建把它们放进 ``build/<书>/gpulab/``：index.json、lab<章>_<节>.ipynb、文件、wqgpu.py、指导书与报告模板（Word）。
网关（services/gateway/app/gpulab.py）读这个文件夹。
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "deploy" / "gpu-lab" / "wqgpu.py"
TIERS = ("basic", "hopper", "profile")
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,40}$")
PLACE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]{0,40})\s*\}\}")
GUIDE_KEYS = ("原理", "步骤", "数据表", "注意")


def _pair(x) -> bool:
    return isinstance(x, list) and len(x) == 2 and all(isinstance(s, str) and s.strip() for s in x)


def cells(text: str) -> list[dict]:
    """百分号格式 → [{"type": "code" | "markdown", "source": str}]。第一个 # %% 之前的内容（文件说明）不进笔记本。"""
    out, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^# %%(.*)$", line)
        if m:
            cur = {"type": "markdown" if "[markdown]" in m.group(1) else "code", "lines": []}
            out.append(cur)
            continue
        if cur is None:
            continue
        if cur["type"] == "markdown":
            cur["lines"].append(line[2:] if line.startswith("# ") else line.lstrip("#"))
        else:
            cur["lines"].append(line)
    res = []
    for c in out:
        src = "\n".join(c["lines"]).strip("\n")
        if src.strip():
            res.append({"type": c["type"], "source": src})
    return res


def notebook(cs: list[dict]) -> dict:
    nb_cells = []
    for c in cs:
        lines = c["source"].splitlines(keepends=True)
        if c["type"] == "markdown":
            nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": lines})
        else:
            nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": lines})
    return {"cells": nb_cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                            "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}


def _python(src: str) -> str:
    """把笔记本的命令行（!cmd）和魔法命令（%cmd、%%cmd）换成占位语句，好让 Python 检查语法。"""
    out = []
    for line in src.splitlines():
        s = line.lstrip()
        out.append(line[: len(line) - len(s)] + "pass" if s.startswith(("!", "%")) else line)
    return "\n".join(out)


def load(folder: Path) -> tuple[dict | None, list[dict], list[str]]:
    """(lab.yaml 的内容, 笔记本的格, 问题清单)。"""
    bad: list[str] = []
    y = folder / "lab.yaml"
    if not folder.is_dir() or not y.exists():
        return None, [], [f"没有 GPU 实验文件夹 {folder.name}/（要有 lab.yaml 和 lab.py）"]
    try:
        g = yaml.safe_load(y.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return None, [], [f"lab.yaml 格式错误：{str(e).splitlines()[0]}"]
    for k in ("标题", "目的"):
        if not _pair(g.get(k)):
            bad.append(f"lab.yaml 的“{k}”应为 [中文, English]")
    if g.get("显卡") not in TIERS:
        bad.append(f"lab.yaml 的“显卡”应为 {' / '.join(TIERS)} 之一")
    results = g.get("结果") or []
    names = []
    for r in results:
        if not (isinstance(r, dict) and NAME.match(str(r.get("名", ""))) and _pair(r.get("说明"))):
            bad.append("lab.yaml 的“结果”每项要有 名（英文字母、数字、下划线）和 说明（中英）")
        else:
            names.append(r["名"])
    if not names:
        bad.append("lab.yaml 没有登记“结果”（学生回传的数）")
    if len(set(names)) != len(names):
        bad.append("lab.yaml 的“结果”有重名")
    for k in GUIDE_KEYS:
        if not g.get(k):
            bad.append(f"lab.yaml 缺少“{k}”（用来生成实验指导书和报告模板）")
    for t in g.get("数据表") or []:
        for row in t.get("行") or []:
            for cell in row:
                for m in PLACE.finditer(str(cell)):
                    if m.group(1) not in names:
                        bad.append(f"数据表“{t.get('标题', ['?'])[0]}”引用了没有登记的结果 {m.group(1)}")
    for f in g.get("文件") or []:
        if not (folder / str(f)).is_file() or "/" in str(f) or str(f).startswith("."):
            bad.append(f"lab.yaml 的“文件”中 {f} 不存在（只能是本文件夹里的文件）")
    nbp = folder / "lab.py"
    if not nbp.exists():
        return g, [], bad + ["没有实验笔记本 lab.py"]
    cs = cells(nbp.read_text(encoding="utf-8"))
    code = [c for c in cs if c["type"] == "code"]
    if not code:
        bad.append("lab.py 没有代码格（用 # %% 分格）")
    else:
        if "wqgpu.check(" not in code[0]["source"]:
            bad.append("lab.py 的第一个代码格要调用 wqgpu.check(...) 检查环境")
        sub = [c["source"] for c in code if "wqgpu.submit(" in c["source"]]
        if not sub:
            bad.append("lab.py 没有 wqgpu.submit(...)：测得的数回传不了")
        else:
            missing = [n for n in names if not re.search(rf"\b{n}\s*=", sub[-1])]
            if missing:
                bad.append(f"lab.py 的 wqgpu.submit(...) 没有回传 {', '.join(missing)}")
        for i, c in enumerate(code, 1):
            try:
                ast.parse(_python(c["source"]))
            except SyntaxError as e:
                bad.append(f"lab.py 第 {i} 个代码格有语法错误：{e.msg}（第 {e.lineno} 行）")
    return g, cs, sorted(set(bad), key=bad.index)


def meta(g: dict) -> dict:
    """给 labdocs.guide / report 用的实验定义（GPU 实验没有场景、滑块和网页任务）。"""
    p = g.get("实际问题") or {}
    scenes = ([{"id": "real", "name": p["标题"], "robot": True, "problem": {"title": p["标题"], "text": p["内容"]}}]
              if _pair(p.get("标题")) and _pair(p.get("内容")) else [])
    return {"title": g["标题"], "goal": g["目的"], "scenes": scenes, "params": [], "tasks": [], "think": g.get("思考"),
            "gpu": {"tier": g["显卡"], "results": [(r["名"], r["说明"], r.get("单位", "")) for r in g["结果"]]}}


def pack(out: Path, labs: list[tuple[str, Path, dict, list[dict]]]) -> dict:
    """写出 build/<书>/gpulab/：index.json、笔记本、文件、wqgpu.py。返回 index。"""
    out.mkdir(parents=True, exist_ok=True)
    index = {"labs": {}}
    for no, folder, g, cs in labs:
        stem = f"lab{no.replace('.', '_')}"
        nb = f"{stem}.ipynb"
        (out / nb).write_text(json.dumps(notebook(cs), ensure_ascii=False, indent=1), encoding="utf-8")
        files = []
        for f in g.get("文件") or []:          # each lab's files in its own folder: two labs may both have a vadd.cu
            (out / stem).mkdir(exist_ok=True)
            (out / stem / str(f)).write_bytes((folder / str(f)).read_bytes())
            files.append(f"{stem}/{f}")
        index["labs"][no] = {"title": g["标题"], "tier": g["显卡"], "notebook": nb, "files": files,
                             "results": [r["名"] for r in g["结果"]]}
    (out / "wqgpu.py").write_text(HELPER.read_text(encoding="utf-8"), encoding="utf-8")
    (out / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return index
