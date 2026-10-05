import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot, api
L = ["AI 工厂助手。它读的是历史库和统一数据总线上的真实数据，回答都附上数据来源。",
     "问它：外圆磨床停机会影响哪张订单？演示环境没接大模型，它先按规则用实时数据作答；接上 DeepSeek 这类大模型后，会把设备、工单和订单串起来分析。",
     "教学模式下，助手只提示方向、不代做；生产模式下，它可以起草订单、请购这类提议，人确认之后才写入 ERPNext。"]
s = Shot("f20_assistant")
s.prep(L)
tk = s.t["token"]; api("POST", "/api/scenario/reset", {"speed": 1, "scores": False}, tk); time.sleep(10)
s.go("/", 5000)
s.begin()
s.say(L[0]); s.click("a.nav:has-text('AI 工厂助手')", pause=2000); s.hover(".chip >> nth=0", pause=1500)
s.say(L[1]); s.type("input[aria-label='问 AI 工厂助手']", "外圆磨床 GRD-01 停机会影响哪张订单？", delay=60, clear=False)
s.pg.keyboard.press("Enter"); s.wait(7000); s.key(); s.wait(3000)
s.say(L[2]); s.pg.mouse.wheel(0, 300); s.wait(4000)
s.end()
