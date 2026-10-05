import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["流体分析。把减速器箱体放进虚拟风洞，模拟轴端风扇以每秒 5 米顺着长边吹，求解器是开源的 OpenFOAM。",
     "读入示例后，风速、风向、摆放和表面温度自动填好；网格选粗，几分钟就能算完。",
     "结果出来了：零件表面按压力着色，迎风面是正压；流线绕过箱体，在后面形成尾流。",
     "换成散热系数 h，每个面散热好坏一目了然。平均 h 约 20，和教材平板公式的范围对得上，阻力也同时算出来了。",
     "最后一键把算出的散热系数送到温度场，代替查表的经验值，算出更可信的油温。"]
s = Shot("f09_cfd", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/cfd", 5000)
s.begin()
s.say(L[0]); s.hover("h1", pause=800); s.pg.locator("select[aria-label=零件]").select_option(value="ex:housing"); s.hover("select[aria-label=零件]", pause=1500)
s.click("button:has-text('读入')", pause=300); s.pg.wait_for_selector(".okline", timeout=60000); s.wait(1000)
s.say(L[1]); s.hover("text=风速 >> nth=0", pause=1200); s.hover("text=放在地面", pause=1000); s.hover("text=表面温度", pause=1000)
s.click(".seg button:has-text('粗')", pause=800); s.click("button:has-text('开始计算')", pause=300); c0 = s.now() + 5
s.pg.wait_for_selector(".kpi", timeout=1500000); s.cut(max(c0, s._due), s.now() - 1); s.wait(2500)
s.say(L[2]); s.hover(".stage", pause=2500)
v = s.pg.locator(".stage").bounding_box(); cx, cy = v["x"] + v["width"] / 2, v["y"] + v["height"] / 2
s.to(cx - 120, cy + 40, pause=200); s.pg.mouse.down(); s.to(cx + 60, cy, steps=16, pause=200); s.pg.mouse.up(); s.wait(1500)
s.say(L[3]); s.pg.locator(".tools select").select_option("h"); s.hover(".tools select", pause=600); s.hover(".stage", pause=2000, dx=0.45, dy=0.5)
s.key(); s.hover(".kpi >> nth=1", pause=1500); s.hover(".kpi >> nth=0", pause=1200)
s.say(L[4]); s.click("button:has-text('把散热系数送到温度场')", pause=300); s.pg.wait_for_selector("text=来自流体分析", timeout=60000); s.wait(1500)
s.hover("text=来自流体分析", pause=2000); s.hover("text=对流散热 >> nth=0", pause=1500)
s.end()
