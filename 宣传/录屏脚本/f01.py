import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot, api
L = ["这是问渠数字工厂的运营总览。所有设备、软件和人，都通过一条统一数据总线交换数据。",
     "AI 每天读总线上的数据，写出今日简报：哪台设备停了，哪种物料不够，哪张订单有风险。",
     "六个关键指标：准时交付、在制品、设备综合效率、一次合格率、完工数和成本偏差，每五秒刷新。",
     "车间实况里，十二个工作单元的状态实时更新，正在加工哪一件、做到第几件，一目了然。",
     "右边是订单与交期，有延期风险的订单会被标出来。"]
s = Shot("f01_home")
s.prep(L)
tok = s.t["token"]
api("POST", "/api/scenario/reset", {"speed": 1, "scores": False}, tok); time.sleep(10)
api("POST", "/api/mes/cmd", {"unit": "sim", "command": "set_speed", "speed": 30}, tok)
s.go("/", 5000)
s.begin()
s.say(L[0]); s.to(900, 330, pause=2500)
s.say(L[1]); s.hover("text=外圆磨床（GRD-01）停机了", pause=2500); s.hover("text=有几种物料的库存不够了", pause=1500)
s.say(L[2])
for k in ["准时交付率", "在制品", "设备综合效率", "一次合格率", "本周完工", "实际成本偏差"]:
    s.hover(f"text={k}", pause=700, dy=2.2)
s.say(L[3]); s.hover("text=CNC-L01-B", pause=1500, dy=3); s.key(); s.hover("text=KEY-01", pause=1200, dy=3); s.hover("text=GRD-01 >> nth=0", pause=1200, dy=3)
s.say(L[4]); s.hover(".card >> text=SAL-ORD-2026-00019", pause=1500); s.hover("text=SAL-ORD-2026-00020", pause=1000)
s.end()
