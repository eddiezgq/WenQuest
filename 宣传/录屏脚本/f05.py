import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["设计发布与审批，这是生产模式下的流程。任何 CAD 画的零件，导出 STEP 就能提交，图纸和加工程序也可以一起上传。",
     "工艺员填物料号 SH-301，选好 STEP 文件，写明改动：轴环加粗、键槽改短，提交审批。服务器自动生成网页可看的三维模型。",
     "审批人打开待审列表，在浏览器里看三维模型，可以在模型上点一处写批注，比如键槽端部的标注，提交人修改后标为已处理。",
     "没有未处理的批注，审批人批准生效。新版本才会进入 ERPNext，车间拿到的永远是批准过的版本。"]
s = Shot("f05_release", role="engineer", user="演示工艺员", mode="prod")
s.prep(L)
s.go("/design", 5000)
s.begin()
s.say(L[0]); s.hover("text=提交新版本", pause=1500); s.hover("text=加工程序（G 代码，可选）", pause=1500)
s.say(L[1]); s.type("input[placeholder*='SH-301']", "SH-301", delay=120); s.pg.keyboard.press("Tab"); s.wait(1500)
s.hover("text=三维模型（STEP）", pause=400); s.pg.locator("input[type=file]").first.set_input_files("/var/tmp/footage/SH-301_revB.step"); s.wait(600)
s.type("textarea", "轴环 Ø40 → Ø42，键槽长 → 36", delay=50, clear=False)
s.click("button:has-text('提交审批')", pause=300); c0 = s.now() + 2.5
s.pg.wait_for_selector("text=待审", timeout=120000); s.cut(c0, s.now() - 0.5); s.wait(1500)
s.switch("演示审批人", "approver", "prod")
s.say(L[2]); s.go("/design", 4000)
s.click("a:has-text('看图审阅') >> nth=0", pause=4000)
v = s.pg.locator("canvas").first.bounding_box(); cx, cy = v["x"] + v["width"] / 2, v["y"] + v["height"] / 2
s.click("button:has-text('差异着色')", pause=1500); s.click("button:has-text('本版')", pause=500)
s.type(".add textarea, textarea >> nth=0", "键槽端部请注明圆头 R6，按 GB/T 1095", delay=45, clear=False)
s.click("button:has-text('添加批注')", pause=1500)
s.key()
s.click("button:has-text('标为已处理') >> nth=0", pause=1200)
s.say(L[3]); s.type("textarea[placeholder*='审批意见']", "同意，按 rev B 生效", delay=60, clear=False)
s.click("button:has-text('批准生效')", pause=300); s.pg.wait_for_selector("text=已批准", timeout=60000); s.hover("text=已批准", pause=2500)
s.end()
