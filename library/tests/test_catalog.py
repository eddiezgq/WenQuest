# -*- coding: utf-8 -*-
"""条目格式、许可、规格表：tools/validate.py 的全部检查，加上规格表能从 bd_warehouse 原样重新生成。"""
import os
import subprocess
import sys
from pathlib import Path

import validate
import wqlib

ROOT = Path(__file__).resolve().parents[1]


def test_all_entries_are_valid():
    p = validate.problems()
    assert not p, "\n".join(p)


def test_bd_specs_regenerate_identically(tmp_path):
    """规格表进了仓库；从 bd_warehouse 的数据重新生成必须一字不差（B.4、L6）。"""
    env = dict(os.environ, WQLIB_SPECS_OUT=str(tmp_path))
    subprocess.run([sys.executable, str(ROOT / "tools" / "import_bd.py")], check=True, env=env, capture_output=True)
    made = sorted(tmp_path.glob("*/*/specs.csv"))
    assert made
    for f in made:
        rel = f.relative_to(tmp_path)
        assert (wqlib.CATALOG / rel).read_text(encoding="utf-8") == f.read_text(encoding="utf-8"), rel


def test_wqr105_standard_parts_are_in_the_library():
    """减速器 WQR-105 第一期能从库里生成的外购件（其余在第二期：弹簧垫圈、圆锥销、油封、螺塞）。"""
    mapped = {}
    for e in wqlib.entries():
        for x in (e.get("factory") or {}).get("erp_items") or []:
            mapped[x["item_code"]] = "{}/{}".format(e["id"], x["size"])
    want = {"BRG-6205", "BRG-6206", "BRG-6207", "KEY-6x6x25", "KEY-8x7x36", "KEY-10x8x28", "KEY-12x8x45",
            "BOLT-M12x110", "NUT-M12", "BOLT-M8x25"}
    assert want <= set(mapped), sorted(want - set(mapped))
