import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["3D 车间。十二个工作单元按真实布局摆放，设备颜色就是实时状态：绿色运行，灰色空闲，红色停机。",
     "两台 AGV 在工位之间搬运工件，三维画面和首页看板用的是同一条数据总线上的消息。",
     "鼠标停在设备上能看到它正在加工的工单和进度，点一下就进入车间终端。"]
s = Shot("f15_3d")
s.prep(L)
from rec import api
tk = s.t["token"]; api("POST", "/api/scenario/reset", {"speed": 1, "scores": False}, tk); time.sleep(10)
api("POST", "/api/mes/cmd", {"unit": "sim", "command": "set_speed", "speed": 20}, tk)
s.go("/3d", 7000)
v0 = s.pg.locator("canvas").first.bounding_box()
s.pg.mouse.move(v0["x"] + v0["width"] / 2, v0["y"] + v0["height"] / 2)
for _ in range(5): s.pg.mouse.wheel(0, -150); s.wait(200)
s.begin()
v = s.pg.locator("canvas").first.bounding_box(); cx, cy = v["x"] + v["width"] / 2, v["y"] + v["height"] / 2
s.say(L[0]); s.to(cx, cy, pause=800); s.pg.mouse.down(); s.to(cx + 260, cy + 10, steps=60, pause=100); s.pg.mouse.up(); s.wait(1500)
s.key()
s.say(L[1]); s.pg.mouse.down(); s.to(cx - 100, cy - 40, steps=60, pause=100); s.pg.mouse.up(); s.wait(800)
for _ in range(6): s.pg.mouse.wheel(0, -120); s.wait(250)
s.wait(1500)
s.say(L[2]); s.to(cx + 60, cy + 30, steps=30, pause=1500); s.to(cx - 80, cy - 20, steps=30, pause=2500)
s.end()
