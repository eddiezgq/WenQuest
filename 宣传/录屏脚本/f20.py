# 镜头 20：厂情中枢——追因 → 推演 → 建议 → 动作 → 复盘（第 17 轮 D 期补拍）
import json, sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot, api
L = ["厂情中枢。规则每 20 秒检查一次全厂。外圆磨床一停机，异常就出现在清单里，首页顶部也有提醒。",
     "中间是因果链：停机连到排在它上面的工单、工单所属的订单和客户。每条连线都能点开，看它的依据。",
     "右边是推演：用仿真车间同一套代码，从当前快照快进。几个处理方案并排比较交期和多花的钱，推荐一个，并说明理由。",
     "也可以让 AI 代理来分析。它自己追因、推演、比较方案。每个结论后面的小方块点开就是依据，数字都经过核对。",
     "采纳方案就生成动作。厂长在动作收件箱批准后，指令真的发到车间。",
     "处理完以后自动复盘：推演说的和实际发生的并排对比，还会重算，如果当时选了别的方案会怎样。"]
s = Shot("f20_assistant")
s.prep(L)
tk = s.t["token"]
api("POST", "/api/scenario/reset", {"speed": 60, "scores": False}, tk); time.sleep(20)
api("POST", "/api/ont/shifts", {"mode": "shift"}, tk)
api("POST", "/api/mes/cmd", {"unit": "grd-01", "command": "inject_fault", "minutes": 2400, "reason": "主轴轴承损坏，等备件"}, tk)
aid = None
for _ in range(60):
    xs = [x for x in api("GET", "/api/ont/anomalies", tok=tk)["anomalies"] if x["rule"] == "P1" and (x["subject"] or {}).get("key") == "grd-01" and "备件" in x["title"]]
    if xs:
        aid = xs[0]["id"]; break
    time.sleep(2)
api("GET", "/api/ont/anomalies/%d" % aid, tok=tk)                 # 先把因果链算好
s.go("/", 5000)
s.begin()
s.say(L[0]); s.hover(".ont-banner:has-text('GRD-01')", pause=2500); s.click(".ont-banner:has-text('GRD-01')", pause=4000)
s.say(L[1]); s.hover(".cg .canvas", pause=2500); s.wait(2500)
s.say(L[2]); s.hover(".op .opt >> nth=0", pause=1500); s.scroll(500, pause=1200); s.hover(".op .reason", pause=2500); s.key(); s.wait(2500)
s.say(L[3]); s.scroll(-2000, pause=600)
a0 = s.now(); s.click("button:has-text('让 AI 分析')", pause=1000)
s.pg.wait_for_selector(".drawer .msg.assistant .ref", timeout=60000); s.cut(a0 + 1.5, s.now() - 0.5)
s.wait(2500); s.hover(".drawer .msg.assistant .ref >> nth=2", pause=2500); s.key("f20_assistant_ai"); s.wait(2500)
s.click(".drawer .x", pause=800)
s.say(L[4]); s.scroll(500, pause=600)
s.click(".op .opt.rec button:has-text('采纳')", pause=2000)
s.go("/ont/actions?box=all", 3000)
s.click("button:has-text('批准并执行') >> nth=0", pause=3500)
s.hover(".act >> nth=0", pause=2000)
# 车间快进到工单做完，等自动复盘（这段剪掉）
a0 = s.now()
api("POST", "/api/mes/cmd", {"unit": "sim", "command": "set_speed", "speed": 600}, tk)
for _ in range(80):
    if api("GET", "/api/ont/anomalies/%d/retro" % aid, tok=tk)["retro"]:
        break
    time.sleep(8)
api("POST", "/api/mes/cmd", {"unit": "sim", "command": "set_speed", "speed": 60}, tk)
s.go("/ont?view=anomalies&a=%d" % aid, 5000)
s.cut(a0 + 0.5, s.now() - 0.5)
s.say(L[5]); s.hover(".rp table >> nth=0", pause=2500); s.scroll(500, pause=800); s.hover(".rp tr.chosen", pause=2500); s.key("f20_assistant_retro"); s.wait(2000)
s.end()
print("errors:", s.errs)
