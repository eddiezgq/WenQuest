import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["零件与机器人库。标准件按国标和 ISO 建模，一千多个规格，每个都有三维模型和工厂物料号。",
     "勾选 WQR-105 用到，就只剩减速器实际用到的零件。打开深沟球轴承 6207，三维模型可以旋转查看，规格表和额定载荷都在。",
     "也可以一句话选型：35 毫米的轴、1450 转每分、以径向载荷为主，系统只从库里挑规格，并说明理由。",
     "机器人库收录了一百五十种机器人。打开 UR5e 协作机器人，拖动关节，模型跟着动；这些模型也直接用于运动与动力分析。"]
s = Shot("f02_library")
s.prep(L)
s.go("/library", 6000)
s.begin()
s.say(L[0]); s.hover("text=A 标准件", pause=1200); s.hover("text=深沟球轴承 >> nth=0", pause=1500)
s.say(L[1]); s.click("label:has-text('WQR-105 用到')", pause=1200); s.click("button.item:has-text('深沟球轴承')", pause=1500)
s.mark("item"); v = s.pg.locator(".detail canvas, canvas").first.bounding_box()
cx, cy = v["x"] + v["width"] / 2, v["y"] + v["height"] / 2
s.to(cx - 80, cy, pause=300); s.pg.mouse.down(); s.to(cx + 120, cy - 40, steps=20, pause=200); s.pg.mouse.up(); s.wait(800)
s.mark("drag"); s.key(); s.mark("key")
s.say(L[2]); s.type("#ask", "35 mm 轴、1450 r/min、径向载荷为主用什么轴承", delay=25); s.click("button:has-text('选型')", pause=300)
s.mark("ask"); s.pg.wait_for_selector("button.chip", timeout=60000); s.wait(1500); s.hover("button.chip >> nth=0", pause=2500)
s.say(L[3]); s.pg.locator("label:has-text('WQR-105 用到') input").uncheck(); s.click("button.tab:has-text('B 机器人')", pause=800); s.type("#q", "UR5e", delay=60); s.wait(800)
s.click("button.item >> nth=0", pause=2500)
s.mark("robot"); r = s.pg.locator("input[type=range]")
for i in range(min(3, r.count())):
    bb = r.nth(i).bounding_box()
    if not bb: continue
    s.to(bb["x"] + bb["width"] * 0.5, bb["y"] + bb["height"] / 2, pause=200); s.pg.mouse.down()
    s.to(bb["x"] + bb["width"] * (0.8 if i % 2 == 0 else 0.25), bb["y"] + bb["height"] / 2, steps=16, pause=200); s.pg.mouse.up(); s.wait(500)
s.mark("sliders"); s.key("f02_library_robot")
s.end()
