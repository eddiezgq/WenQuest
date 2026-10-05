import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["运动与动力分析，相当于在线版的 ADAMS，求解器是开源的 MuJoCo。模型直接取自零件库：这里选 UR5e 协作机器人。",
     "设定工况：末端带 3 公斤负载，肩关节和肘关节在 1.3 秒内各转一个角度，重力打开。也可以一句话让 AI 填。",
     "计算完成，三维动画回放整个动作，下面是每个关节的角度、速度、驱动力矩和功率曲线。",
     "按这次算出的峰值力矩和转速，平台自动给每个关节选电机和减速器；杆件受力还可以送到有限元和疲劳分析。"]
s = Shot("f10_mbd", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/mbd", 5000)
s.begin()
s.say(L[0]); s.click(".seg button:has-text('机械臂')", pause=800)
sel = s.pg.locator("select[aria-label=机械臂]"); s.hover(sel, pause=500)
opt = sel.locator("option", has_text="UR5e").first.get_attribute("value"); sel.select_option(opt); s.wait(800)
s.click("button:has-text('读入')", pause=300); s.pg.wait_for_selector("text=可驱动关节", timeout=120000); s.wait(1500)
s.say(L[1]); s.hover("text=末端负载 >> nth=0", pause=1200); s.hover("text=驱动 >> nth=0", pause=1200); s.hover("canvas", pause=1500)
s.click("button:has-text('开始计算')", pause=300); c0 = s.now() + 3
s.pg.wait_for_selector("button:has-text('导出曲线')", timeout=600000); s.cut(max(c0, s._due), s.now() - 1); s.wait(1500)
s.say(L[2]); s.pg.mouse.wheel(0, -3000); s.wait(500); s.click("button:has-text('播放')", pause=2500); s.key(); s.hover(".charts", pause=2500)
s.say(L[3]); b = s.pg.locator("button:has-text('按这次的力矩')"); b.scroll_into_view_if_needed(); s.click(b, pause=300)
s.pg.wait_for_selector("text=够用", timeout=60000); s.wait(800); s.hover("th:has-text('推荐')", pause=1500, dy=3); s.key("f10_mbd_motor"); s.hover("text=够用 >> nth=0", pause=2500)
s.end()
