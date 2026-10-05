import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["疲劳寿命。载荷反复变化时零件能用多久？平台用博世开源的 pyLife 做雨流计数、S-N 曲线和 Miner 累积损伤。",
     "载荷谱可以是恒幅，也可以直接用车间跑合试验台记录的真实转矩、机械臂关节的力矩记录，或者上传自己的数据。",
     "疲劳极限按尺寸系数、表面状态和应力集中系数修正，再做 Goodman 平均应力修正，每一步公式都列出来。",
     "寿命云图上红色是寿命最短的地方，就是键槽根部。设计改了以后，重新算一次就能对比。"]
s = Shot("f07_fatigue", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/cae", 6000)
s.click("a:has-text('看结果') >> nth=0", pause=4000)
s.pg.locator("text=疲劳寿命 >> nth=1").scroll_into_view_if_needed(); s.pg.mouse.wheel(0, 250); s.wait(800)
s.begin()
s.say(L[0]); s.hover("h3:has-text('疲劳寿命')", pause=2500)
s.say(L[1])
logbtn = s.pg.locator("button:has-text('跑合试验台转矩记录')")
s.hover(logbtn, pause=900); s.hover("button:has-text('关节力矩记录')", pause=900); s.hover("button:has-text('上传载荷记录')", pause=900)
uselog = False
if logbtn.is_enabled():
    s.click(logbtn, pause=800)
    sel = s.pg.locator("select:has(option:has-text('选择记录'))")
    if sel.count() and sel.locator("option").count() > 1:
        sel.select_option(index=1); uselog = True; s.wait(1200)
if not uselog:
    s.click("button:has-text('恒幅')", pause=800)
print("用跑合记录：", uselog)
s.say(L[2]); s.click("button:has-text('计算疲劳寿命')", pause=300); c0 = s.now() + 3
s.pg.wait_for_selector("text=修正后疲劳极限", timeout=300000); s.cut(max(c0, s._due), s.now() - 1); s.wait(800)
s.hover("text=修正后疲劳极限", pause=2500)
s.say(L[3]); s.pg.mouse.wheel(0, -2000); s.wait(800); s.click("button:has-text('疲劳寿命') >> nth=0", pause=2500)
s.key(); s.hover("canvas", pause=2500)
s.end()
