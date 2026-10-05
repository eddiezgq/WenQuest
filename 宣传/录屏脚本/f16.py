import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["质量。三坐标测得的每一件尺寸都上总线，控制图实时更新。这是轴承位直径 Ø35 k6，最近几件明显在往上漂。",
     "超出公差的零件，系统自动开不合格品单。质检员在这里评审：返修、报废或者让步接收。",
     "对控制图上的异常，开一张质量异常单，按 8D 的步骤找根本原因、定措施，再用后面的数据验证措施有没有效。",
     "老师还可以注入隐藏的加工问题，比如砂轮修整间隔过长，学生只能从数据里把原因找出来。"]
s = Shot("f16_quality", role="quality", user="演示质检员")
s.prep(L)
s.go("/work/quality", 5000)
s.begin()
s.say(L[0]); s.hover("select >> nth=1", pause=1000); s.hover("svg >> nth=0", pause=2500, dx=0.8); s.hover("text=最近 5 件均值", pause=1500)
s.key()
s.say(L[1]); s.hover(".ncr >> nth=0", pause=2000); s.click("button:has-text('返修') >> nth=0", pause=2500)
s.say(L[2]); s.type("input[placeholder*='现象']", "轴承位直径逐件上移，接近上限", delay=60, clear=False); s.click("button:has-text('为当前特性开单')", pause=300)
s.wait(3000)
s.pg.wait_for_load_state(); s.hover("h1, h2 >> nth=0", pause=2500); s.pg.mouse.wheel(0, 400); s.wait(2500)
s.key("f16_quality_8d")
s.say(L[3]); s.go("/work/quality", 3000); s.hover("text=问题情景（老师）", pause=2500, dy=3)
s.end()
