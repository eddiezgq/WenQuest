"""50.5 节：粗车（工序 20）和铣键槽（工序 50）的工序卡片（图 50.5.1、50.5.2）；卡片上的转速、机动时间由切削用量算出。
同时核对实验 50.5 里写死的常数（刀尖圆弧半径、单位切削力、机床功率）与数据表、工厂数据一致。"""
import math
import re
from pathlib import Path

import _mfg as M
from bookout import out

p = M.plan()
ops = M.cards.machining_ops(p)
pages = 1 + len(ops) + 3
idx = {o["seq"]: i for i, o in enumerate(ops)}
r, k = M.op(p, 20), M.op(p, 50)
M.card_figure(M.cards.op_card(p, r, idx[20] + 2, pages), "fig50_5_1")
M.card_figure(M.cards.op_card(p, k, idx[50] + 2, pages), "fig50_5_2")
M.card_figure(M.cards.op_card(p, M.op(p, 40), idx[40] + 2, pages), "fig50_5_3")
M.card_figure(M.cards.op_card(p, M.op(p, 60), idx[60] + 2, pages), "fig50_5_4")
v = [M.cards.step_values(s) for s in r["steps"]]
face, drill, turn = v[0], v[1], v[2]
assert abs(face["n"] - 1000 * 120 / (math.pi * 50)) < 1e-9
kv = M.cards.step_values(k["steps"][2])
tb20 = M.cards.op_basic_time(r)
# 实验 50.5 的常数与数据表、工厂数据核对
lab = (Path(__file__).resolve().parents[1] / "lab" / "lab50_5.js").read_text(encoding="utf-8")
sys_path = M.REPO / "factory" / "digital" / "std"
import sys  # noqa: E402
sys.path.insert(0, str(sys_path))
import stdtab  # noqa: E402
kz = stdtab.table("kienzle").row("C45E")
assert f"KC11: {kz['kc11_MPa']}" in lab and f"MC: {kz['mc']}" in lab, "实验 50.5 的单位切削力常数与 kienzle 表不一致"
from hub import process  # noqa: E402
pw = process.WORKCENTER_POWER["数控车床 CNC-L01"]
assert f"P_MOTOR: {pw[0]}" in lab and f"ETA: {pw[1]}" in lab, "实验 50.5 的机床功率与工厂数据不一致"
# 实验场景“粗车”“精车”的 ta = 单件定额 − 场景那一段的机动时间
pd = r["steps"][2]["passes_detail"]
tb2 = sum(L / (1000 * 120 / (math.pi * d) * 0.3) for d, _, L in pd[:2])
fin = M.op(p, 40)["steps"][1]
tbf = fin["passes_detail"][0][2] / (1000 * fin["vc"] / (math.pi * fin["passes_detail"][0][0]) * fin["f"])
assert f"ta: {r['minutes'] - tb2:.1f}" in lab and f"ta: {M.op(p, 40)['minutes'] - tbf:.1f}" in lab, "实验 50.5 的 ta 与工序卡不一致"
kc = kz["kc11_MPa"] * 0.3 ** (-kz["mc"])
Fc = kc * 2.125 * 0.3
Pc = Fc * 120 / 60000
ra_f = 0.0321 * 0.15 ** 2 / 0.4 * 1000
# 键槽深度的工艺尺寸链（第 53 章）：d − t = H − d精车/2 + d磨/2，极值法
from hub import tolerance as TL  # noqa: E402
ch = p["chains"][0]
res = TL.extreme([TL.Link(l["name"], l["nominal"], l.get("es", 0), l.get("ei", 0), l.get("sense", 1)) for l in ch["links"]])
H = ch["links"][0]
out(H=H["nominal"], H_es=H["es"], H_ei=H["ei"], dt_nom=res.nominal, dt_es=res.es, dt_ei=res.ei,
    tb2=tb2, kc=kc, Fc=Fc, Pc=Pc, Pm=Pc / pw[1], ra_f=ra_f, rz_f=0.15 ** 2 / (8 * 0.4) * 1000,
    n_face=face["n"], tb_face=face["tb"], n_drill=drill["n"], tb_drill=drill["tb"], n_turn_lo=turn["n"][0], n_turn_hi=turn["n"][1],
    tb_turn=turn["tb"], passes_turn=turn["passes"], tb20=tb20, min20=r["minutes"], share20=100 * tb20 / r["minutes"],
    n_key=kv["n"], vf_key=kv["vf"], tb_key=kv["tb"], min50=k["minutes"], kc11=kz["kc11_MPa"], mc=kz["mc"], p_motor=pw[0], eta=pw[1])
