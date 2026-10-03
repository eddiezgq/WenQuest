"""习题 50.4.4 的图 50.4.2：一张故意埋了 10 处错误的工艺过程卡片（答案在教师用书里，不在程序输出中）。"""
import _mfg as M
from bookout import out

p = M.plan()
ops = {o["seq"]: o for o in p["operations"]}
p["material"] = "Q235"
p["blank"]["spec"] = "Ø40"
p["doc"]["per_unit"] = 2
ops[20]["content"] = "夹一端车端面，调头车另一端面至总长 168；一夹一顶粗车各外圆，单边留余量"
ops[30]["workstation"] = "外圆磨床 GRD-01"
ops[40]["content"] = "三爪卡盘夹左端外圆，精车各外圆、轴肩与倒角，轴承位和齿轮位留磨量"
ops[50]["seq"], ops[40]["seq"] = 40, 50
p["operations"].sort(key=lambda o: o["seq"])
ops[60]["minutes"] = 0.2
ops[60]["fixture"] = "键槽铣夹具 JJ-301-50"
p["operations"] = [o for o in p["operations"] if o["seq"] != 70]
M.card_figure(M.cards.process_card(p, 1, 1), "fig50_4_2")
out(n_errors=10)
