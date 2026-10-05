"""Screenshots of a 3D lab page in headless Chromium (three.js r128 is served from a local copy instead of cdnjs).

    python3 tools/shot3d.py out.png page.html 'js to run before the shot' [width height]
"""
import sys, pathlib, os
from playwright.sync_api import sync_playwright

THREE = os.environ.get("WQ_THREE", "/home/claude/sm/node_modules/three/build/three.min.js")


def shot(out, page_path, js="", w=1400, h=900, wait=1500):
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        pg.route("**/three.min.js", lambda r: r.fulfill(path=THREE, content_type="application/javascript"))
        pg.goto("file://" + str(pathlib.Path(page_path).resolve()))
        pg.wait_for_timeout(wait)
        if js:
            pg.evaluate(js)
            pg.wait_for_timeout(wait)
        pg.screenshot(path=out)
        b.close()
        return errs


if __name__ == "__main__":
    a = sys.argv
    print(shot(a[1], a[2], a[3] if len(a) > 3 else "", *(int(x) for x in a[4:6])))
