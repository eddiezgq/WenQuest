import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["数控编程。从工艺规程出发：SH-301 的每道工序列在这里，能编程的工序可以直接选，这里选粗车。",
     "平台根据现行三维模型识别台阶和直径，排出编程单：刀具、切深、进给和转速，都可以改，也可以一句话让 AI 改。",
     "生成程序并仿真：刀路一层层去除材料，同时检查超程、超转速、功率和撞刀，算出加工时间。",
     "程序是标准的 FANUC G 代码，AI 可以逐段讲解；挂到工艺规程审批后，随工单下发到车间的数控车床。"]
s = Shot("f12_cam", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/cam", 5000)
s.begin()
s.say(L[0]); sel = s.pg.locator("select[aria-label=零件]"); s.hover(sel, pause=600); sel.select_option("SH-301"); s.wait(1500)
s.hover(".ops", pause=1200); s.click("label.op:has-text('粗车')", pause=1200)
s.say(L[1]); s.click("button:has-text('按这道工序排编程单')", pause=300); s.pg.wait_for_selector("button:has-text('生成程序并仿真')", timeout=120000); s.wait(1500)
s.hover("text=刀具 >> nth=0", pause=1500); s.hover("button:has-text('生成程序并仿真')", pause=800)
s.say(L[2]); s.click("button:has-text('生成程序并仿真')", pause=300); s.pg.wait_for_selector("button:has-text('下载程序')", timeout=300000); s.wait(1000)
s.click("button:has-text('播放')", pause=300); s.pg.locator("select:has(option[value='60'])").select_option("60"); s.wait(5000)
s.key(); s.hover(".player", pause=1000, dy=-8); s.hover(".kpi >> nth=0", pause=2000)
s.say(L[3]); s.pg.mouse.wheel(0, 600); s.wait(800); s.hover("button:has-text('请 AI 逐段讲解')", pause=1500); s.hover("button:has-text('挂到工艺规程')", pause=2000)
s.end()
