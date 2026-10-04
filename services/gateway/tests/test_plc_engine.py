"""The PLC engine of the lab kit (第 18 轮): its own Node tests, and the PLCopen XML it exports is well formed."""
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

HERE = Path(__file__).parent


@pytest.mark.skipif(not shutil.which("node"), reason="needs Node.js")
def test_plc_engine(tmp_path):
    out = tmp_path / "export.xml"
    r = subprocess.run(["node", "--test", str(HERE / "plc" / "plc.test.mjs"), str(HERE / "plc" / "plants.test.mjs"), str(HERE / "plc" / "wrong.test.mjs")], capture_output=True, text=True,
                       env={**os.environ, "PLC_XML_OUT": str(out)}, timeout=120)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-2000:]
    root = ET.fromstring(out.read_text(encoding="utf-8"))
    ns = {"p": "http://www.plcopen.org/xml/tc6_0201"}
    assert root.tag == "{http://www.plcopen.org/xml/tc6_0201}project"
    pous = {p.get("name"): p.get("pouType") for p in root.findall(".//p:pou", ns)}
    assert pous == {"FB_X": "functionBlock", "Main": "program"}
    assert root.find(".//p:task/p:pouInstance", ns).get("typeName") == "Main"


def test_plc_labs_carry_the_engine_and_run_in_a_browser(tmp_path):
    """A lab with view: "plc" gets the engine and the editor; the example lab's own tests all pass in Chromium."""
    from app.production import labs
    code = (Path(labs.KIT) / "demo_plc.js").read_text(encoding="utf-8")
    assert labs.static_problems(code) == []
    page = labs.page([("8.1", code)], course=["PLC 原理及实践", "PLC"], chapter=["第8章", "Chapter 8"])
    assert "WQPLCUI" in page and "class Runtime" in page
    plain = labs.page([("2.1", labs.physics_example())], course=["x", "x"], chapter=["x", "x"])
    assert "window.WQPLCUI = { setup }" not in plain and "window.WQPLCUI = { setup }" in page
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("needs Playwright")
    f = tmp_path / "plc.html"
    f.write_text(page, encoding="utf-8")
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # noqa: BLE001 - no browser on this machine
            pytest.skip(f"no Chromium: {e}")
        pg = b.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f.as_uri())
        pg.wait_for_timeout(500)
        st = pg.evaluate("WQ.status()")
        assert st["errors"] == [] and st["labs"]["8-1"]["view"] == "plc" and not st["labs"]["8-1"]["broken"]
        pg.click("button.chip[data-k=tests]")
        pg.click(".plcview:not([hidden]) .btn.primary")
        marks = pg.locator(".plctests > li .mark").all_inner_texts()
        assert marks == ["✓"] * 4, pg.inner_text(".plctests")
        st = pg.evaluate("WQ.status()")
        assert [k for k, v in st["labs"]["8-1"]["tasks"].items() if v] == ["run", "stop", "jam"]
        # run it by hand: press start, the part travels and stops at the end sensor
        pg.click("[data-action=run]")
        btn = pg.locator(".opbtn.push")
        btn.dispatch_event("pointerdown"); pg.wait_for_timeout(200); btn.dispatch_event("pointerup")
        pg.wait_for_timeout(4500)
        assert pg.evaluate("WQ.status()")["labs"]["8-1"]["tasks"]["hand"]
        assert errors == []
        b.close()


def test_plc_labs_on_3d_machines(tmp_path):
    """The four first virtual machines (WQPLANTS) load in a 3D PLC lab; the 3D engine comes with them, not otherwise."""
    from app.production import labs
    progs = {"traffic": "PROGRAM Main NS_G := TRUE; EW_R := TRUE; END_PROGRAM", "elevator": "PROGRAM Main Y_DoorOpen := TRUE; END_PROGRAM",
             "sorter": "PROGRAM Main M_Belt := S_Stop; END_PROGRAM", "press": "PROGRAM Main Y_Clamp := B_Part; END_PROGRAM"}
    items = []
    for k, (name, prog) in enumerate(progs.items()):
        code = (f'const plant = WQPLANTS.{name}();\nWQ.lab({{ title: ["{name}", "{name}"], goal: ["x", "x"], view: "plc", scenes: [{{id: "a", name: ["a", "a"]}}], '
                f'params: [], plc: {{ io: plant.io, lang: "ST", program: {{ st: "{prog}" }}, tests: [] }}, plant, '
                f'tasks: [{{id: "a", text: ["a", "a"]}}, {{id: "b", text: ["b", "b"]}}] }});')
        assert labs.static_problems(code) == []
        items.append((f"1.{k + 1}", code))
    page = labs.page(items, course=["PLC", "PLC"], chapter=["x", "x"])
    assert "WQ3D=" in page and "function sorter" in page
    plain = labs.page([("8.1", (Path(labs.KIT) / "demo_plc.js").read_text(encoding="utf-8"))], course=["x", "x"], chapter=["x", "x"])
    assert "WQ3D=" not in plain and "function sorter" not in plain
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("needs Playwright")
    f = tmp_path / "plants.html"
    f.write_text(page, encoding="utf-8")
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        except Exception as e:  # noqa: BLE001
            pytest.skip(f"no Chromium: {e}")
        pg = b.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f.as_uri())
        pg.wait_for_timeout(500)
        for lab in ("1-1", "1-2", "1-3", "1-4"):
            pg.click(f"#tab-{lab}")
            pg.click(f"#lab-{lab} [data-action=run]")
            pg.wait_for_timeout(400)
        st = pg.evaluate("WQ.status()")
        assert st["errors"] == [] and all(v["view"] == "plc" and not v["broken"] for v in st["labs"].values()), st
        assert pg.evaluate("document.querySelector('#lab-1-3 canvas').dataset.engine || ''").startswith("three.js")
        assert errors == []
        b.close()
