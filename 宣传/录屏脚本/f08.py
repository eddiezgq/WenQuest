import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["温度场与热平衡。示例是 WQR-105 减速器的简化箱体，齿轮和轴承的损耗按传动效率算出来，变成箱体内壁的发热。",
     "读入后，热边界自动填好：内壁发热，外表面按教材的散热系数对流散热，底面装在机座上不散热。",
     "算完看温度云图：箱体外表面平均温度和教材的热平衡公式几乎一致，有限元还看出底部角落更热。",
     "这个箱体还可以加散热筋、加风扇，或者把流体分析算出的散热系数送进来，比较油温能降多少。"]
s = Shot("f08_thermal", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/cae", 6000)
s.begin()
s.say(L[0]); sel = s.pg.locator("select[aria-label=零件]"); s.hover(sel, pause=500); sel.select_option(value="ex:housing"); s.wait(800)
s.click("button:has-text('读入') >> nth=0", pause=300); s.pg.wait_for_selector("text=面发热", timeout=120000); s.wait(1500)
s.say(L[1]); s.hover("text=面发热 >> nth=0", pause=1500); s.hover("text=对流散热 >> nth=0", pause=1500); s.hover("canvas", pause=1500)
s.click("button:has-text('开始计算')", pause=300); c0 = s.now() + 3
s.pg.wait_for_selector(".formula", timeout=600000); s.cut(max(c0, s._due), s.now() - 1); s.wait(2000)
s.say(L[2]); s.hover("canvas", pause=1200)
v = s.pg.locator("canvas").first.bounding_box(); cx, cy = v["x"] + v["width"] / 2, v["y"] + v["height"] / 2
s.to(cx - 150, cy + 60, pause=200); s.pg.mouse.down(); s.to(cx + 40, cy - 30, steps=16, pause=200); s.pg.mouse.up(); s.wait(1000)
s.key(); s.pg.locator(".formula").scroll_into_view_if_needed(); s.hover(".formula", pause=3000)
s.say(L[3]); s.pg.mouse.wheel(0, -1500); s.wait(800); s.hover("canvas", pause=2500)
s.end()
