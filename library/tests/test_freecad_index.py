# -*- coding: utf-8 -*-
"""FreeCAD-library 索引：只收相关分类的 FCStd，配上同名 STEP/STL 链接（固定提交），缩略图复制进发布目录。"""
import json

import freecad_index


def test_index_from_fake_repo(tmp_path):
    src = tmp_path / "src"
    for f in ["Mechanical Parts/Bearings/6205 bearing.FCStd", "Mechanical Parts/Bearings/6205 bearing.step",
              "Mechanical Parts/Bearings/6205 bearing.stl", "Architectural Parts/Doors/door.FCStd",
              "Robots/Arm/base.fcstd", "thumbnails/abc123.png"]:
        (src / f).parent.mkdir(parents=True, exist_ok=True)
        (src / f).write_bytes(b"x")
    (src / "index.html").write_text(
        '<div class="card"><a title="FCSTD version" href="https://github.com/FreeCAD/FreeCAD-library/blob/master/'
        'Mechanical%20Parts/Bearings/6205%20bearing.FCStd?raw=true"><img class="icon" src="thumbnails/abc123.png"/>',
        encoding="utf-8")
    out = tmp_path / "ver"
    c = freecad_index.build(out, src)
    assert c["count"] == 2 and c["thumbs"] == 1 and c["license"] == "CC-BY-3.0"
    doc = json.loads((out / "freecad-library.json").read_text(encoding="utf-8"))
    pin = freecad_index.pin()["commit"]
    brg = next(i for i in doc["items"] if i["name"] == "6205 bearing")
    assert set(brg["formats"]) == {"fcstd", "step", "stl"}
    assert all(pin in u for u in brg["formats"].values())
    assert (out / brg["thumb"]).exists()
    assert not any("door" in i["name"] for i in doc["items"])      # 建筑类不收
    assert doc["attribution"] and "CC BY" in doc["attribution"]


def test_missing_source_is_skipped(tmp_path):
    assert freecad_index.build(tmp_path / "ver", tmp_path / "nope") is None
