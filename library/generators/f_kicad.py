# -*- coding: utf-8 -*-
"""电子元件（第 88 轮）：外形原样读 KiCad 官方三维模型库的 STEP（仓库 factory/designs/3dmodels，CC-BY-SA 4.0 附例外）。
engine 写 kicad:<目录（相对仓库根）>，规格表的 step 列是该目录下的文件。"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def build(entry, row):
    from build123d import import_step
    base = REPO / entry["model"]["engine"].split(":", 1)[1]
    shape = import_step(str(base / row["step"]))
    return [(entry["id"] + "-" + str(row["size"]), shape)]
