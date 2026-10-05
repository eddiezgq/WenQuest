import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["工程任务单。老师在课程里下达，比如机械设计第 3 章：画 SH-301 B 版零件图并提交审批。背景、输入、交付物、评分标准都写清楚。",
     "学生按任务单交付：上传三维模型和零件图，一起进入设计发布。",
     "点 AI 预检。AI 设计评审员先按国标查图面：图号、比例、公差带代号、粗糙度写法、过时的符号，还拿图上的直径和三维模型逐一对照。",
     "每条意见都标明依据的标准。学生逐条答复、改图后提交，老师审核批准，零件进车间加工、三坐标检验，最后按评分标准给分。"]
s = Shot("f19_tasks", role="engineer", user="演示学生")
s.prep(L)
import base64, hmac, hashlib, json
u = {"name": "演示学生", "role": "engineer", "mode": "teach", "teacher": False, "uid": "stu-demo-1"}
raw = base64.urlsafe_b64encode(json.dumps(u, ensure_ascii=False).encode()).decode()
tok = raw + "." + hmac.new(b"dev", raw.encode(), hashlib.sha256).hexdigest()[:32]
s.go("/tasks", 1500)
s.pg.evaluate("t => { localStorage.setItem('wq-rec-sw', '1'); localStorage.setItem('wq-df-session', t); }", json.dumps({"token": tok, "user": u}))
s.go("/tasks", 4000)
s.begin()
s.say(L[0]); s.hover("text=用 FreeCAD 画 SH-301 B 版零件图", pause=1000); s.click("a:has-text('用 FreeCAD 画 SH-301 B 版零件图')", pause=2500)
s.hover("text=交付物", pause=1200); s.pg.mouse.wheel(0, 300); s.wait(1500)
s.say(L[1]); s.click("button:has-text('提交模型') >> nth=0", pause=1000)
s.pg.locator("label:has-text('STEP 模型') input").set_input_files("/var/tmp/footage/SH-301_revB.step"); s.wait(400)
s.pg.locator("label:has-text('图纸') input").set_input_files("/var/tmp/footage/SH-301_revB_drawing.pdf"); s.wait(400)
s.click("button.btn.primary:has-text('提交') >> nth=0", pause=300); s.pg.wait_for_selector("text=✓ 设计发布", timeout=120000); s.wait(1200)
s.say(L[2]); s.click("button:has-text('AI 预检')", pause=300); s.wait(6000)
s.pg.mouse.wheel(0, 500); s.wait(1500); s.key(); s.wait(2500)
s.say(L[3]); s.pg.mouse.wheel(0, 500); s.wait(2500); s.hover("text=评审要点", pause=2000)
s.end()
