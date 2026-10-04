"""第 17 轮附 4a：确认网页远程桌面能用——打开 noVNC，截图；在桌面里启动 Xschem（反相器原理图）和 KLayout（反相器版图）后再截图。
用法：python vnc_shot.py <容器名> <端口> <输出目录>"""
import subprocess, sys, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

name, port, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
url = f"http://localhost:{port}/?password=abc123&autoconnect=true&resize=remote"
for _ in range(120):
    try:
        urllib.request.urlopen(f"http://localhost:{port}/", timeout=2); break
    except Exception:
        time.sleep(2)
else:
    sys.exit("web desktop did not come up")


def ex(cmd):
    subprocess.run(["docker", "exec", "-d", name, "bash", "-lc", cmd], check=True)


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(url); time.sleep(15)
    pg.screenshot(path=str(out / "desktop.png"))
    ex("cd /foss/designs && DISPLAY=:1 xschem --rcfile $PDKPATH/libs.tech/xschem/xschemrc $WQ_HOME/ch1/inv.sch")
    time.sleep(20)
    pg.screenshot(path=str(out / "xschem.png"))
    ex("cd /foss/designs && DISPLAY=:1 klayout -nn $PDKPATH/libs.tech/klayout/tech/sky130.lyt /foss/designs/inv.gds || DISPLAY=:1 klayout /foss/designs/inv.gds")
    time.sleep(20)
    pg.screenshot(path=str(out / "klayout.png"))
    b.close()
print("screenshots in", out)
