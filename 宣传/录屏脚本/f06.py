import sys, time; sys.path.insert(0, "/var/tmp/footage")
from rec import Shot
L = ["仿真与分析：有限元强度校核。读入输出轴 SH-301 的现行三维模型，材料选 45 钢调质，每个数值都标明出处。",
     "填入示范工况：两处轴承支承，输出端限制转动，键槽一侧加额定扭矩 350 牛米。也可以一句话让 AI 填表。",
     "点开始计算。服务器用 Gmsh 划网格、CalculiX 求解，几十秒出结果。",
     "Von Mises 应力云图上，最大应力在键槽根部，平台标出最大应力、安全系数，并和材料许用值比较。",
     "切到位移云图，变形可以放大显示；计算报告可以一键导出 Word。"]
s = Shot("f06_cae", role="engineer", user="演示工艺员")
s.prep(L)
s.go("/cae", 6000)
s.begin()
s.say(L[0]); s.hover("select >> nth=0", pause=600); s.click("button:has-text('读入') >> nth=0", pause=3000)
s.hover("text=材料 >> nth=0", pause=800)
s.say(L[1]); s.click("button:has-text('填入示范题：SH-301')", pause=2500); s.hover("canvas", pause=1500)
s.say(L[2]); s.click("button:has-text('开始计算')", pause=300); c0 = s.now() + 4
s.pg.wait_for_selector("button:has-text('Von Mises 应力')", timeout=400000); s.cut(max(c0, s._due), s.now() - 1); s.wait(2500)
s.say(L[3]); s.hover("canvas", pause=1500)
v = s.pg.locator("canvas").first.bounding_box(); cx, cy = v["x"] + v["width"] / 2, v["y"] + v["height"] / 2
s.to(cx - 150, cy + 30, pause=200); s.pg.mouse.down(); s.to(cx + 50, cy - 20, steps=16, pause=200); s.pg.mouse.up(); s.wait(1200)
s.key()
s.hover("text=安全系数 >> nth=0", pause=2000)
s.say(L[4]); s.click("button:has-text('位移')", pause=1800); s.hover("text=变形放大", pause=1200)
s.click("button:has-text('Von Mises 应力')", pause=1000); s.hover("button:has-text('下载计算报告')", pause=1500)
s.end()
