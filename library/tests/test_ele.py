# -*- coding: utf-8 -*-
"""电子元件第一批（第 88 轮）：条目由 tools/import_kicad_ele.py 生成且逐字一致；每个规格的 STEP 在仓库里；默认规格造得出来。"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

import wqlib

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def test_entries_regenerate_identically(tmp_path):
    env = dict(os.environ, WQLIB_SPECS_OUT=str(tmp_path))
    subprocess.run([sys.executable, str(ROOT / "tools" / "import_kicad_ele.py")], check=True, env=env, capture_output=True)
    made = sorted(tmp_path.glob("A/A-ELE-*/*"))
    assert len(made) == 28
    for f in made:
        assert (wqlib.CATALOG / f.relative_to(tmp_path)).read_text(encoding="utf-8") == f.read_text(encoding="utf-8"), f


def test_every_step_file_is_vendored_with_license():
    es = [e for e in wqlib.entries() if e["id"].startswith("A-ELE-")]
    assert len(es) == 14
    base = REPO / "factory" / "designs" / "3dmodels"
    assert (base / "LICENSE.md").exists()
    for e in es:
        assert e["source"]["license"] == "CC-BY-SA-4.0" and e["source"]["origin"] == "kicad"
        for r in wqlib.specs(e):
            assert (base / r["step"]).exists(), (e["id"], r["step"])


def test_drive_board_parts_are_in_the_library():
    """驱动板 BOM 上每种外购元件都能在库里找到对应条目"""
    have = {e["id"] for e in wqlib.entries()}
    for eid in ("A-ELE-R0402", "A-ELE-C0402", "A-ELE-C1206", "A-ELE-CPEL", "A-ELE-SHUNT", "A-ELE-LPWR", "A-ELE-DSCH",
                "A-ELE-MOSTDSON", "A-ELE-SOIC8", "A-ELE-LQFP48", "A-ELE-SOT", "A-ELE-XTAL", "A-ELE-TB", "A-ELE-XH"):
        assert eid in have


def test_default_models_build():
    build123d = pytest.importorskip("build123d")
    from generators import get_builder
    for e in [e for e in wqlib.entries() if e["id"].startswith("A-ELE-")]:
        row = next(r for r in wqlib.specs(e) if str(r["size"]) == str(e["default"]))
        nodes = get_builder(e)(e, row)
        size = nodes[0][1].bounding_box().size
        assert 0.3 < max(size.X, size.Y, size.Z) < 40, (e["id"], size)
        assert isinstance(nodes[0][1], build123d.Shape) or hasattr(nodes[0][1], "bounding_box")
