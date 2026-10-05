import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot, api
L = ["经营与成本，厂长的工作区。每台设备今天的综合效率 OEE，拆成开动率、性能和合格率，数据来自设备状态和完工事件。",
     "工单成本分解：材料、加工、调整和换刀工时，实际和标准成本逐项对比，偏差的原因一眼能看出来。",
     "教学模式下，这里也是教师控制台：调仿真倍速，或者给某台设备制造一次故障。我们让数控车床 B 停机 30 分钟。",
     "回到首页，这台设备立刻变红，AI 简报和订单交期风险也跟着更新，学生要据此重新安排生产。"]
s = Shot("f17_manager")
s.prep(L)
tk = s.t["token"]; api("POST", "/api/scenario/reset", {"speed": 1, "scores": False}, tk); time.sleep(10)
api("POST", "/api/mes/cmd", {"unit": "sim", "command": "set_speed", "speed": 20}, tk)
s.go("/work/manager", 5000)
s.begin()
s.say(L[0]); s.hover("text=设备综合效率（今日）", pause=1200); s.hover("tbody tr >> nth=1", pause=1500); s.hover("tbody tr >> nth=8", pause=1500)
s.say(L[1]); s.pg.locator("text=工单成本分解").scroll_into_view_if_needed(); s.wait(600); s.hover("text=工单成本分解", pause=1500, dy=4); s.key(); s.wait(1500)
s.say(L[2]); s.pg.mouse.wheel(0, -3000); s.wait(600); s.hover("text=教师控制台", pause=800)
sel = s.pg.locator(".ctl select").nth(1); s.hover(sel, pause=400); sel.select_option("cnc-l01-b"); s.wait(600)
r = s.pg.locator("input[aria-label=原因]"); s.click(r, pause=200); s.pg.keyboard.press("Control+A"); s.pg.keyboard.type("主轴报警", delay=150)
s.click("button:has-text('注入')", pause=2000); s.hover("text=已让", pause=1200)
s.say(L[3]); s.go("/", 5000); s.hover("text=CNC-L01-B", pause=2500, dy=3); s.key("f17_manager_home"); s.hover("text=AI 今日简报", pause=2000)
s.end()
