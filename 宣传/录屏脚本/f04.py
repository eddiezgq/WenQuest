import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["设计台。工艺员在浏览器里直接改输出轴 SH-301 的参数，不用装任何 CAD 软件。",
     "把键槽长度从 45 改成 42，三维模型马上更新，系统同时做尺寸校核，算出总长和下料重量。",
     "写上改动说明，点发布新版本。服务器用 build123d 生成 STEP 模型、零件图和键槽的数控 G 代码。",
     "新版本出现在版本表里，STEP、零件图一应俱全；ERPNext 里的设计版本和 BOM 也同步更新。",
     "键槽 G 代码会随工单下达，派给键槽铣床 KEY-01。"]
s = Shot("f04_cad", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/work/engineer", 6000)
n0 = s.pg.locator("td.mono.b").count()
s.begin()
s.say(L[0]); s.hover("text=在线设计 · 输出轴 SH-301", pause=1200); s.hover(".view", pause=1500)
s.say(L[1]); s.type("label:has-text('槽长 L') input", "42", delay=300); s.wait(1200); s.hover(".view", pause=1500); s.hover("text=校核通过", pause=1500)
s.say(L[2]); s.type("input.note", "键槽长 45 → 42（配合新键）", delay=60, clear=False); s.click("button:has-text('发布新版本')", pause=300)
t = time.time(); c0 = s.now() + 2
s.pg.wait_for_function("n => document.querySelectorAll('td.mono.b').length > n", arg=n0, timeout=120000)
print("发布用时", round(time.time() - t, 1)); s.cut(max(c0, s._due), s.now() - 1)
s.say(L[3]); s.scroll(450, pause=600); s.hover("td.mono.b >> nth=0", pause=1000); s.hover("a.flink:has-text('STEP') >> nth=0", pause=1000); s.hover("a.flink:has-text('零件图') >> nth=0", pause=1000); s.key()
s.say(L[4]); s.scroll(450, pause=600); s.hover("text=键槽 G 代码", pause=2000)
s.end()
