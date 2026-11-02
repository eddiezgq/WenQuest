"""Round 64 step 5 part 1: part profiles, volumes, STEP and DXF. With OpenCASCADE installed the STEP files are read
back and checked (valid solids, volumes equal to the analytic ones)."""

import json
import math
from pathlib import Path

import pytest

from bearingkit import parts as PT
from bearingkit import step3d as S
from bearingkit.analyze import geometry_of

EX = Path(__file__).resolve().parents[1] / "examples"


def geo(name):
    return geometry_of(json.loads((EX / f"{name}.json").read_text(encoding="utf-8")))


def test_volumes_closed_forms():
    g = geo("scene-cylindrical")
    pr = PT.parts(g)
    assert S.volume(pr["element"]) == pytest.approx(math.pi * (g["Dw"] / 2) ** 2 * g["Lw"], rel=1e-12)
    assert S.volume(pr["inner"]) == pytest.approx(
        math.pi * ((g["di"] / 2) ** 2 - (g["d"] / 2) ** 2) * g["B"], rel=1e-12
    )
    # a ball bearing ring: the groove takes out of the shoulder band exactly what the arc encloses
    gb = geo("demo-deep-groove")
    v = S.volume(PT.parts(gb)["inner"])
    band = math.pi * ((gb["di"] / 2 + gb["h_i"]) ** 2 - (gb["d"] / 2) ** 2) * gb["B"]
    assert 0 < band - v < band * 0.2


@pytest.mark.parametrize("name", ["demo-deep-groove", "demo-angular", "scene-cylindrical", "scene-tapered"])
def test_step_text_and_dxf(name):
    g = geo(name)
    text, vol = PT.step(g, "bearing")
    assert text.startswith("ISO-10303-21;") and text.count("MANIFOLD_SOLID_BREP") == 2 + g["Z"]
    assert set(vol) == {"inner", "outer", "element"}
    d = PT.dxf(PT.parts(g)["inner"])
    assert d.endswith("EOF\n") and ("ARC" in d) == (g["type"] in ("deep_groove", "angular"))
    dr = PT.drawings(g)
    assert {"inner", "outer", "element"} <= set(dr) and dr["notes"]


def test_missing_shoulder_refused():
    p = json.loads((EX / "demo-deep-groove.json").read_text(encoding="utf-8"))
    del p["inner"]["h_i"]
    with pytest.raises(PT.PartsError, match="shoulder heights"):
        PT.parts(geometry_of(p))


@pytest.mark.parametrize("name", ["demo-deep-groove", "demo-angular", "scene-cylindrical", "scene-tapered"])
def test_step_read_back_by_opencascade(name, tmp_path):
    pytest.importorskip("OCP")
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer

    g = geo(name)
    text, vol = PT.step(g, "bearing")
    f = tmp_path / "b.step"
    f.write_text(text)
    r = STEPControl_Reader()
    r.ReadFile(str(f))
    r.TransferRoots()
    shape = r.OneShape()
    assert BRepCheck_Analyzer(shape).IsValid()
    total, n = 0.0, 0
    e = TopExp_Explorer(shape, TopAbs_SOLID)
    while e.More():
        gp = GProp_GProps()
        BRepGProp.VolumeProperties_s(e.Current(), gp)
        total += gp.Mass()
        n += 1
        e.Next()
    assert n == 2 + g["Z"] and total == pytest.approx(sum(vol.values()), rel=1e-5)
