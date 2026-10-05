import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["参数配置器。销售按客户要求填参数：WQR-105 两级圆柱齿轮减速器，选传动比、输入功率和工况系数。",
     "系统马上校核。把输入功率加到 5.5 千瓦，计入工况系数后输出转矩超过额定 350 牛米，立即标红。",
     "改回 4 千瓦，校核通过：轴承 6207 的寿命、平键挤压应力都在表里，零件直接引用零件库的规格。",
     "三维模型同步生成，齿轮可以转起来给客户看。",
     "填上数量和交期，自动报价；确认后生成订单提议，经桥接写入 ERPNext。"]
s = Shot("f03_configurator")
s.prep(L)
s.go("/configurator", 6000)
s.click("button:has-text('WQR-105')", pause=2500)
s.begin()
s.say(L[0]); s.hover("text=传动比 >> nth=0", pause=1000); s.hover("select >> nth=1", pause=1200); s.hover("text=工况系数 KA", pause=1000)
inp = s.pg.locator("input[type=number]")
s.say(L[1]); s.click(inp.nth(0), pause=200); s.pg.keyboard.press("Control+A"); s.pg.keyboard.type("5.5", delay=200); s.wait(1200); s.hover("text=超过额定", pause=1800)
s.say(L[2]); s.click(inp.nth(0), pause=200); s.pg.keyboard.press("Control+A"); s.pg.keyboard.type("4", delay=200); s.wait(1200)
s.hover("text=校核通过", pause=800); s.hover("text=轴承 6207 寿命", pause=1200, dx=0.9); s.hover("text=A-BRG-DG/6207", pause=1200)
s.say(L[3]); s.click("button:has-text('转动')", pause=3500)
s.key()
s.say(L[4]); q = s.pg.locator("label.fld:has-text('数量') input"); s.click(q, pause=200); s.pg.keyboard.press("Control+A"); s.pg.keyboard.type("20", delay=250)
s.wait(1200); s.hover("text=合计", pause=1500, dx=3); s.hover("button:has-text('生成订单提议')", pause=2000)
s.end()
