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


def test_sfc_and_fbd_editors_in_a_browser(tmp_path):
    """Chapter 11–12 tools: the SFC chart follows the active steps; FBD networks are drawn as blocks."""
    import json
    from app.production import labs
    io = [{"name": "start", "addr": "%IX0.0", "dir": "in"}, {"name": "stopNC", "addr": "%IX0.1", "dir": "in"},
          {"name": "lift", "addr": "%QX0.0", "dir": "out"}, {"name": "grip", "addr": "%QX0.3", "dir": "out"}]
    sfc = ("PROGRAM Main\n INITIAL_STEP S0: END_STEP\n STEP S1: lift(N); END_STEP\n STEP S2: grip(N); END_STEP\n"
           " TRANSITION FROM S0 TO S1 := start; END_TRANSITION\n TRANSITION FROM S1 TO S2 := S1.T >= T#200ms; END_TRANSITION\n"
           " TRANSITION FROM S2 TO S0 := NOT start; END_TRANSITION\nEND_PROGRAM")
    def lab(lang, prog):
        return (f'WQ.lab({{ title: ["{lang}", "{lang}"], goal: ["x", "x"], view: "plc", scenes: [{{id: "a", name: ["a", "a"]}}], params: [], '
                f'plc: {{ io: {json.dumps(io)}, lang: "{lang}", program: {json.dumps(prog)}, tests: [] }}, '
                f'plant: {{ panel: [{{name: "start", kind: "switch", label: ["启动", "Start"]}}], reset(s) {{}}, inputs(s) {{ return {{}}; }}, step() {{}} }}, '
                f'tasks: [{{id: "a", text: ["a", "a"]}}, {{id: "b", text: ["b", "b"]}}], draw(api, s) {{}} }});')
    page = labs.page([("1.1", lab("SFC", {"sfc": sfc})),
                      ("1.2", lab("FBD", {"decls": "VAR t1 : TON; END_VAR", "fbd": [{"text": "lift := (start OR lift) AND stopNC AND NOT t1.Q"}, {"text": "t1(IN := lift, PT := T#3s)"}]}))],
                     course=["x", "x"], chapter=["x", "x"])
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("needs Playwright")
    f = tmp_path / "sfc.html"
    f.write_text(page, encoding="utf-8")
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # noqa: BLE001
            pytest.skip(f"no Chromium: {e}")
        pg = b.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f.as_uri())
        pg.wait_for_timeout(400)
        pg.click("#lab-1-1 [data-action=run]")
        pg.click("#lab-1-1 .opbtn")
        pg.wait_for_timeout(900)
        on = pg.locator("#lab-1-1 .sfcdiag rect.st.on").count()
        names = pg.locator("#lab-1-1 .sfcdiag text.sn").all_text_contents()
        assert on == 1 and any(t.startswith("S2") for t in names), names
        pg.click("#tab-1-2")
        assert pg.locator("#lab-1-2 .fbdpic svg rect.fb").count() >= 3
        assert errors == [] and pg.evaluate("WQ.status()")["errors"] == []
        b.close()
