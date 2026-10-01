"""Round 4 §7: the digital factory in lessons — client, design book case, factory figures, workshop animation,
live workshop entry. Fixtures: real answers of the factory's course interface (factory/digital tests' scenario)."""
import asyncio
import html
import json
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

from app import main
from app.factory import Factory, FactoryError, source_record
from app.production import factory_figs as FF
from app.production import figures as F

from tests.test_materials import login
from tests.test_studio import _write_first_lesson, client, settle  # noqa: F401 - the fixture

DATA = Path(__file__).parent / "data" / "factory"
KEY = "read-key"


def handler(request: httpx.Request) -> httpx.Response:
    if request.headers.get("authorization") != f"Bearer {KEY}":
        return httpx.Response(401, json={"detail": "no"})
    p = request.url.path
    q = parse_qs(request.url.query.decode())
    name = {"/api/course/layout": "layout", "/api/course/products": "products", "/api/course/products/WQR-105": "product_WQR-105",
            "/api/course/cases": "cases", "/api/course/embed-token": "embed"}.get(p)
    if p == "/api/course/data":
        name = f"data_{q['kind'][0]}"
    if not name or not (DATA / f"{name}.json").exists():
        return httpx.Response(404, json={"detail": "not found"})
    return httpx.Response(200, content=(DATA / f"{name}.json").read_bytes(), headers={"content-type": "application/json"})


def factory(key=KEY):
    return Factory("https://factory.test", key, httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_client_summary_and_source():
    fac = factory()
    s = asyncio.run(fac.summary())
    assert s["case"] == "lab7" and s["products"] == ["WQR-105"] and "cnc-l01-a" in s["text"] and "no robot arms" in s["text"]
    rec = source_record(s)
    assert rec["id"] == "factory:lab7" and rec["version"].startswith("截至 2026") and "不含个人信息" in rec["attribution"]
    with pytest.raises(FactoryError):
        asyncio.run(factory("wrong").layout())
    assert not Factory("", "").available


def test_factory_figures(tmp_path):
    fac = factory()
    out = asyncio.run(FF.make(fac, "layout", tmp_path / "fig-1.png", "both", ["cnc-l01-a"]))
    assert F.png_ok(tmp_path / out["png"]) and "数控车床" in (tmp_path / out["svg"]).read_text()
    out = asyncio.run(FF.make(fac, "bom:WQR-105", tmp_path / "fig-2.png", "both"))
    svg = html.unescape((tmp_path / out["svg"]).read_text())
    assert "WQR-105" in svg and "SA-300" in svg and "输出轴组件" in svg
    out = asyncio.run(FF.make(fac, "routing:SH-301", tmp_path / "fig-3.png", "both"))
    assert "saw-01" in html.unescape((tmp_path / out["svg"]).read_text())
    rows = json.loads((DATA / "data_measurement.json").read_text())["rows"]
    char = rows[0]["characteristic"]
    spec = FF.control_chart(rows, char)
    assert spec["series"][0]["y"] == [r["value_mm"] for r in rows if r["characteristic"] == char]   # the factory's numbers
    out = asyncio.run(FF.make(fac, f"control:{char}", tmp_path / "fig-4.png", "both"))
    assert F.png_ok(tmp_path / out["png"])
    with pytest.raises(F.FigureError):
        asyncio.run(FF.make(fac, "routing:NOPE", tmp_path / "fig-5.png", "both"))


def test_workshop_script_follows_the_data():
    from app.production import scene3d as S
    L = lambda n: json.loads((DATA / f"{n}.json").read_text())  # noqa: E731
    agv = L("data_agv")["rows"]
    data = {"layout": L("layout"), "agv": agv, "event": L("data_event")["rows"],
            "from": min(r["ts"] for r in agv), "to": max(r["ts"] for r in agv)}
    sc = S.build({"template": "workshop", "follow": "agv-01", "highlight": ["cnc-l01-a"]}, {}, factory_data=data, source="src")
    w = sc["workshop"]
    assert {u["id"] for u in w["units"]} == {u["unit"] for u in L("layout")["units"]}
    assert next(u for u in w["units"] if u["id"] == "cnc-l01-a")["highlight"]
    keys = next(a for a in w["agvs"] if a["id"] == "agv-01")["keys"]
    assert all(keys[i][0] <= keys[i + 1][0] for i in range(len(keys) - 1)) and keys[-1][0] <= sc["duration"]
    # every AGV point between docks lies on an aisle (y = 9 or 18.5, or the cross aisle x = 7) or at a recorded dock
    docks = {(r["x_m"], r["y_m"]) for r in agv if r["unit"] == "agv-01"}
    assert all((k[1], k[2]) in docks or k[2] in (9.0, 18.5) or k[1] == 7.0 for k in keys)
    assert any(u["states"] for u in w["units"]) and sc["source"] == "src"
    assert sc["camera"]["keys"][2][4] == "agv-01"


def test_a_lesson_with_the_factory(client, monkeypatch, tmp_path):
    """Design book names the factory case; the 3D clip replays the workshop then a robot shot (an illustration);
    the notes link the live workshop and list the factory data with its date."""
    from app.production import labs, scene3d as S
    pages = []

    import io
    from PIL import Image
    jpg = io.BytesIO()
    Image.new("RGB", (64, 36), "#202830").save(jpg, "JPEG")

    async def render3d(url, page_html, duration, **kw):
        pages.append(page_html)
        return b"\x00\x00\x00\x18ftypmp42", jpg.getvalue(), float(duration), [jpg.getvalue()]

    async def trial_run(url, page_html, lab, timeout=150.0):
        return {"ok": True, "problems": [], "tasks": {}, "screenshot": b"", "seconds": 1.0}
    monkeypatch.setattr(S, "render", render3d)
    monkeypatch.setattr(labs, "trial_run", trial_run)
    monkeypatch.setattr(main.state.settings, "labcheck_url", "http://labcheck.test")
    monkeypatch.setattr(main.state.settings, "factory_url", "https://factory.test")
    monkeypatch.setattr(main.state.settings, "factory_read_key", KEY)
    st = main._studio()
    st.factory.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    concat = []
    monkeypatch.setattr(type(st), "_concat_clips", staticmethod(lambda parts, out: (concat.append(len(parts)), out.write_bytes(b"x"))))
    h = login(client)
    pid, p = _write_first_lesson(client, h)
    p = settle(client, h, pid, 60)
    assert p["design_book"]["factory"]["case"] == "lab7"
    les = p["outline"]["chapters"][0]["lessons"][0]
    esc = lambda x: json.dumps(x)[1:-1]  # noqa: E731 - the page carries the script as JSON
    assert '"workshop": {"floor"' in pages[0] and esc("数据来自问渠数字工厂") in pages[0]
    assert concat == [2] and esc("上下料示意（非工厂数据）") in pages[1]          # the robot shot is marked
    assert any(f["kind"] == "animation" for f in les["files"])           # the 3D clip is the lesson's animation
    zh = les["content"]["zh"]
    assert 'class="wq-factory"' in zh and "https://factory.test/embed/workshop" in zh
    assert "问渠数字工厂" in zh and "截至 2026" in zh                       # sources with the data's date
