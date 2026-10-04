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
    r = subprocess.run(["node", "--test", str(HERE / "plc" / "plc.test.mjs")], capture_output=True, text=True,
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
