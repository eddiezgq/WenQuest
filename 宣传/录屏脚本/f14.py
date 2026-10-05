import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot, api
L = ["车间终端，给操作工用，平板上就能打开。上面一排是十二台设备，选外圆磨床 GRD-01：它正停机换砂轮。",
     "换好砂轮，点处理完毕、复位，这台设备接着加工排队的工件；下面是派到本工位的工序，可以开工或暂停。",
     "仿真车间开始加工：本件进度、刀具也就是砂轮的剩余寿命实时变化，数据都走统一数据总线。",
     "右边的最近事件按时间滚动：开工、完工、指令和回执，全部记入历史库，首页、质量和成本分析都从这里取数。"]
s = Shot("f14_mes", role="operator", user="演示操作工")
s.prep(L)
from rec import login; tok = login()["token"]
api("POST", "/api/scenario/reset", {"speed": 1, "scores": False}, tok); time.sleep(10)
api("POST", "/api/mes/cmd", {"unit": "sim", "command": "set_speed", "speed": 60}, tok)
s.go("/work/operator", 5000)
s.begin()
s.say(L[0]); s.hover(".tabs", pause=1200); s.click(".tabs button:has-text('GRD-01')", pause=2500)
s.say(L[1]); s.click("button:has-text('处理完毕，复位')", pause=2500); s.wait(1500)
b = s.pg.locator("button:has-text('开工')")
if b.count(): s.click(b.first, pause=1500)
else: s.hover("text=派到本工位的工序", pause=1500, dy=3)
s.say(L[2]); s.hover(".progress >> nth=0", pause=3000); s.hover("text=剩余寿命", pause=3000); s.key()
s.say(L[3]); s.hover("text=最近事件", pause=2500, dy=4); s.wait(3000)
s.end()
