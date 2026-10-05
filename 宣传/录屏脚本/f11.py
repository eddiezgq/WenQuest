import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["设计优化。目标是让输出轴更轻，要求是安全系数和无限疲劳寿命都要满足。平台用开源的 Optuna 自动改尺寸。",
     "勾选可以改的直径和长度，设定范围，点开始优化。每一组尺寸都先过设计台的校核，再跑一次有限元。",
     "每一次的结果都列出来，绿色是满足要求的。现行设计的安全系数不够，平台找到满足全部要求、又尽量轻的方案，一键送回设计台。",
     "另一种是拓扑优化：给定支承和载荷，让算法决定材料该放在哪里，可以回放材料生长的过程，结果拉伸成板件再做有限元校核。"]
s = Shot("f11_opt", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/opt", 5000)
s.begin()
s.say(L[0]); s.hover("select[aria-label=优化问题]", pause=1200); s.hover("text=安全系数 ≥", pause=1500); s.hover("text=疲劳寿命（0", pause=1200)
s.say(L[1])
cb = s.pg.locator(".vrow input[type=checkbox]")
for i in range(cb.count()):
    if not cb.nth(i).is_checked() and i < 3:
        s.click(cb.nth(i), pause=500)
n = s.pg.locator("label:has-text('分析次数') input"); s.click(n, pause=200); s.pg.keyboard.press("Control+A"); s.pg.keyboard.type("16", delay=150)
s.click("button:has-text('开始优化')", pause=300)
s.pg.wait_for_selector(".card-head .pill:has-text('完成')", timeout=1200000); s.wait(1500)
s.say(L[2]); s.hover("button:has-text('送到设计台')", pause=1500)
s.key(); s.pg.mouse.wheel(0, 500); s.wait(1500); s.hover("svg >> nth=0", pause=2000)
s.say(L[3]); s.pg.mouse.wheel(0, -2000); s.click("button:has-text('拓扑优化')", pause=1500)
s.click("button:has-text('开始拓扑优化')", pause=300); s.pg.wait_for_selector("button:has-text('播放生长过程')", timeout=600000); s.wait(1000)
s.click("button:has-text('播放生长过程')", pause=4000); s.key("f11_opt_topo"); s.hover("button:has-text('拉伸成板件')", pause=2000)
s.end()
