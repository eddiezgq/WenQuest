import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["订单与计划，计划员的工作区。客户订购 20 台 WQR-105 减速器，填好交期，先点算料。",
     "MRP 算料表一行一行列清楚：毛需求、其他订单占用、库存、在途和安全库存，净需求为正的物料要请购，还给出 SH-301 的标准成本。",
     "提交后生成一条待确认的提议。AI 起草的也一样，人确认之后，才经桥接写入 ERPNext：销售订单、工单和请购单。",
     "工单出现在下面，点下达车间，系统按工艺路线把每道工序派给对应的设备，操作工在车间终端就能开工。"]
s = Shot("f13_mrp", role="planner", user="演示计划员")
s.prep(L)
s.go("/work/planner", 5000)
s.begin()
s.say(L[0]); s.hover("text=新建订单", pause=800); s.hover("select >> nth=1", pause=1000)
q = s.pg.locator("input[type=number]").first; s.click(q, pause=200); s.pg.keyboard.press("Control+A"); s.pg.keyboard.type("20", delay=250)
d = s.pg.locator("input[type=date]").first; s.click(d, pause=300); d.fill("2026-11-10"); s.wait(600)
s.click("button:has-text('算料')", pause=300); s.pg.wait_for_selector("text=算料结果", timeout=60000); s.wait(1200)
s.say(L[1]); s.hover("tr.need >> nth=0", pause=1500); s.hover("tr.need >> nth=1", pause=1500); s.hover("text=标准成本", pause=1500)
s.key()
s.say(L[2]); s.click("button:has-text('提交（生成待确认的提议）')", pause=2000)
s.hover("text=待确认 >> nth=0", pause=1500)
cb = s.pg.locator("button:has-text('确认执行')"); cb.scroll_into_view_if_needed(); s.wait(600); s.click(cb, pause=300)
s.pg.wait_for_selector("text=已执行", timeout=120000); s.wait(2500)
cl = s.pg.locator(".modal-mask button:has-text('关闭')"); cl.scroll_into_view_if_needed(); s.click(cl, pause=800)
s.say(L[3]); s.click("button:has-text('刷新')", pause=1200)
b = s.pg.locator("button:has-text('下达车间')").first; s.click(b, pause=300); s.pg.wait_for_selector("text=已下达", timeout=60000); s.wait(1500)
s.key("f13_mrp_release"); s.hover("text=已下达 >> nth=0", pause=2500)
s.end()
