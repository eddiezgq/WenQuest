import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["数字孪生。卖出去的每一台 WQR-105 在平台里都有一个分身：出厂数据，加上现场每天上报的运行数据，再加上寿命模型。",
     "左边是机队，红黄绿一目了然。打开这台报警的减速器：六个轴承各用掉了多少 L10 寿命，输出轴的疲劳损伤，振动按 ISO 10816 分区，油温和热平衡模型对比。",
     "油温比模型高出一截，说明散热变差。AI 结合数据给出原因和处理顺序，一键开维修单，进入 ERPNext 的服务工单。",
     "假如分析：负载降到 80%，再加轴端风扇，散热系数用的就是流体分析算出来的值，平台算出剩余寿命、换油间隔和油温的变化。"]
s = Shot("f18_twin")
s.prep(L)
s.go("/twin", 6000)
s.begin()
s.say(L[0]); s.hover("h1", pause=1500); s.hover("button.unit >> nth=0", pause=1500)
s.say(L[1]); s.click("button.unit:has-text('H2504-06')", pause=2500)
for i in range(3): s.hover(".kpi >> nth=%d" % i, pause=900) if s.pg.locator(".kpi").count() > i else None
s.hover("canvas", pause=2500); s.key()
s.say(L[2]); s.click("button:has-text('请 AI 说说')", pause=300); s.pg.wait_for_selector(".exp", timeout=60000); s.hover(".exp", pause=2500)
s.click(".alert button >> nth=0", pause=2000); s.click("button:has-text('确认开单')", pause=2500)
s.say(L[3]); w = s.pg.locator(".whatif"); w.scroll_into_view_if_needed(); s.wait(500)
rg = s.pg.locator(".whatif input[type=range]").bounding_box()
s.to(rg["x"] + rg["width"] * 0.375, rg["y"] + rg["height"] / 2, pause=200)
s.click(".whatif label.chk", pause=800, dx=0.05); s.click("button:has-text('重算')", pause=3500)
s.key("f18_twin_whatif"); s.hover(".whatif", pause=1500, dy=3)
s.end()
