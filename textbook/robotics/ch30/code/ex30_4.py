"""30.4 节的计算：机电一体化设计流程与评审；为减速器厂部件装配工位选机器人。

(1) 算例 30.4.1：设计的结果进了 ERP：机器人厂清单里一台 WQ-CR5 的材料费（逐层加起来）、各部分占多少；
    J1 若按自己的需要用中关节模组能省多少；整机与关节模组的工艺路线工时。
(2) 算例 30.4.2：部件装配工位要搬的零件：毛坯质量（上限），加上 1 kg 夹爪，哪些在 5 kg 以内；
    第二级大齿轮 GR-302 的成品质量估算（齿顶圆 Ø216、齿宽 40 mm 的实心盘减去 Ø45 的孔，示例）。
(3) 算例 30.4.3：零件库里的候选：负载 ≥ 5 kg、臂展够得着工位（算例 30.1.2 的最小臂展）且不超过 1.5 m；协作 / 工业。
"""
import math

from _ch30 import COBOTS, GRIPPER_KG, RHO_STEEL, library_arms, robot_plant, station_parts, wqcr5
from bookout import out

W = wqcr5()
P = robot_plant()
# ---------------------------------------------------------------- (1) 清单与成本
from _ch30 import bom_rollup                                    # noqa: E402
parts, mat = bom_rollup("WQ-CR5")
price = {p["item"]: p["price"] for p in P["products"]}["WQ-CR5"]
_, cL = bom_rollup("WQJ-L")
_, cM = bom_rollup("WQJ-M")
_, cS = bom_rollup("WQJ-S")
mods = parts["WQJ-L"] + parts["WQJ-M"] + parts["WQJ-S"]
ctrl = parts["CTRL-CAB"]
rt = {r["name"]: r["steps"] for r in P["routings"]}
t_robot = sum(m for _, m in rt["RT-协作机器人 Cobot"])
t_joint = sum(m for _, m in rt["RT-关节模组 Joint module"])
t_total = t_robot + 6 * t_joint
assert abs(mods + ctrl + sum(v for k, v in parts.items() if k not in ("WQJ-L", "WQJ-M", "WQJ-S", "CTRL-CAB")) - mat) < 1e-6
out(mat=mat, price=price, mat_share=mat / price * 100, cL=cL, cM=cM, cS=cS, mods=mods, mod_share=mods / mat * 100, ctrl=ctrl,
    ctrl_share=ctrl / mat * 100, save_j1=cL - cM, save_share=(cL - cM) / mat * 100, t_robot=t_robot, t_joint=t_joint,
    t_total_h=t_total / 60, t_run=dict(rt["RT-协作机器人 Cobot"])["负载跑合 Load run-in"],
    t_cal=dict(rt["RT-协作机器人 Cobot"])["整机标定 Robot calibration"])

# ---------------------------------------------------------------- (2) 工位的零件
sp = station_parts()
light = [p for p in sp if p["blank_kg"] + GRIPPER_KG <= W.PAYLOAD_KG]
heavy = [p for p in sp if p["blank_kg"] + GRIPPER_KG > W.PAYLOAD_KG]
gr302 = next(p for p in sp if p["item"] == "GR-302")
m302 = RHO_STEEL * math.pi / 4 * (0.216 ** 2 - 0.045 ** 2) * 0.040
assert [p["item"] for p in heavy] == ["SH-101", "GR-202", "GR-302"] and 10 < m302 < gr302["blank_kg"]
out(n_parts=len(sp), n_light=len(light), b101=sp[0]["blank_kg"], b201=sp[1]["blank_kg"], b301=sp[2]["blank_kg"], b202=sp[3]["blank_kg"],
    b203=sp[4]["blank_kg"], b302=gr302["blank_kg"], m302=m302, grip=GRIPPER_KG, need302=m302 + GRIPPER_KG)

# ---------------------------------------------------------------- (3) 零件库里的候选
reach_need = 759                                              # 算例 30.1.2（程序 30.1.1 算出，四舍五入到 mm）
arms = library_arms()
cands = [a for a in arms if (a["payload_kg"] or 0) >= 5 and a["reach_mm"] and reach_need <= a["reach_mm"] <= 1500]
co = [a for a in cands if a["id"] in COBOTS]
ind = [a for a in cands if a["id"] not in COBOTS]
too_short = [a for a in arms if (a["payload_kg"] or 0) >= 5 and a["reach_mm"] and a["reach_mm"] < reach_need and a["reach_mm"] > 600]
can302 = [a for a in cands if a["payload_kg"] >= m302 + GRIPPER_KG]
by = {a["id"]: a for a in arms}
assert "B-ARM-WQCR5" in [a["id"] for a in co] and "B-ARM-IRB1200" in [a["id"] for a in too_short]
out(n_arms=len(arms), n_cand=len(cands), n_co=len(co), n_ind=len(ind), n_short=len(too_short), n_302=len(can302),
    ur10_p=by["B-ARM-UR10E"]["payload_kg"], ur10_r=by["B-ARM-UR10E"]["reach_mm"], ur10_w=by["B-ARM-UR10E"]["weight_kg"],
    m302_margin=(by["B-ARM-UR10E"]["payload_kg"] - (m302 + GRIPPER_KG)) / by["B-ARM-UR10E"]["payload_kg"] * 100,
    irb_r=by["B-ARM-IRB1200"]["reach_mm"], reach_need=reach_need)
