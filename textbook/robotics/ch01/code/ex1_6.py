"""1.6 节的计算：全书的结构；五台贯穿机器人的主要数据（全部由零件库条目读出或算出）。

算例 1.6.1  UR5e：零位时法兰中心到基座轴线的水平距离（按关节表的正运动学，与按尺寸手算核对），与手册的工作半径比较；
            额定负载在最远处对肩关节产生的力矩。
算例 1.6.3  差速小车：由轮半径、轮距和轮子最高转速求最高车速和原地转动的最大角速度。
算例 1.6.4  四旋翼 X2：悬停时每个旋翼的推力（与模型的悬停关键帧核对）、推重比。
算例 1.6.2  Go2 站立时机身离地高度。
另：Panda、Go2 的连杆质量之和与厂家重量对照。
"""
import math
import re

import numpy as np
import yaml

from _ch1 import FIVE, G, MJCF, ROOT, dof_summary, entry, fk_point
from bookout import T, out

# ---------------------------------------------------------------- 全书结构（book.yaml，由提纲生成）
book = yaml.safe_load((ROOT / "textbook" / "robotics" / "book.yaml").read_text(encoding="utf-8"))
chs = book["chapters"]
n_ch = len(chs)
n_sec = sum(len(c["sections"]) for c in chs)
parts = []
for c in chs:
    if not parts or parts[-1][0] != c["part"]:
        parts.append([c["part"], 0])
    parts[-1][1] += 1
lv = {}
for c in chs:
    lv[c["level"]] = lv.get(c["level"], 0) + 1
assert n_ch == 61 and sum(n for _, n in parts) == n_ch
part_counts = {p: n for p, n in parts}

# 提纲中每章的文字里提到哪台机器人（含配套实验）
outline = (ROOT / "docs" / "教材" / "机器人学" / "00_提纲.md").read_text(encoding="utf-8")
body = outline[outline.index("## 三、提纲"):outline.index("### 附录")]
blocks = re.split(r"\n\*\*第 (\d+) 章", body)[1:]
text_of = {int(blocks[i]): blocks[i + 1] for i in range(0, len(blocks), 2)}
assert sorted(text_of) == list(range(1, 62))
KEYS = {"B-ARM-UR5E": r"UR5e", "B-ARM-PANDA": r"Panda|七轴", "B-LEG-GO2": r"Go2|四足|足式",
        "B-EDU-DIFF": r"AGV|差速|移动机器人", "B-UAV-X2": r"四旋翼|无人机|空中机器人"}
uses = {k: sorted(n for n, t in text_of.items() if re.search(p, t)) for k, p in KEYS.items()}
n_any = len(set().union(*uses.values()))

# ---------------------------------------------------------------- UR5e
ur = entry("B-ARM-UR5E")
sheet = ur["datasheet"]["values"]
p0 = fk_point(ur, {}, "wrist_3_link", (0, 0.1, 0))                 # 零位时的法兰中心（根连杆坐标系）
r0 = math.hypot(p0[0], p0[1])
L1, L2 = 0.425, 0.392
off = 0.138 - 0.131 + 0.127 + 0.1                                    # 侧向偏距之和 W1 − W2 + W3 + W4
r0_hand = math.hypot(L1 + L2, off)
assert abs(r0 - r0_hand) < 1e-6           # 模型里的 π/2 写成 1.570796，有 10⁻⁷ m 级的舍入
reach_sheet = sheet["reach_mm"] / 1000
tau_payload = sheet["payload_kg"] * G * (L1 + L2)                    # 负载 5 kg 在 0.817 m 处，对肩关节轴的力矩
m_ur_model = dof_summary("B-ARM-UR5E")["mass_model"]
v_joint = ur["dh"]["speed_deg_s"][0]
ur_area = math.pi * reach_sheet ** 2

# ---------------------------------------------------------------- Panda、Go2
pa = dof_summary("B-ARM-PANDA")
pa_sheet = pa["datasheet"]
go = dof_summary("B-LEG-GO2")
go_e = entry("B-LEG-GO2")
rest = go_e["robot"]["rest"]
foot = fk_point(go_e, rest, "FL_calf", (0, 0, -0.213))                # 站立姿态下左前足在机身坐标系中的位置
hip = fk_point(go_e, rest, "FL_thigh")
h_stand = -foot[2]
th_t, th_c = rest["FL_thigh_joint"], rest["FL_calf_joint"]
h_hand = 0.213 * math.cos(th_t) + 0.213 * math.cos(th_t + th_c)      # 大腿、小腿在竖直方向的投影之和
assert abs(h_stand - h_hand) < 1e-9
leg = 0.213 * 2

# ---------------------------------------------------------------- 差速小车
df = entry("B-EDU-DIFF")
r_w = df["robot"]["kinematics"]["wheel_radius_m"]
b_w = df["robot"]["kinematics"]["track_m"]
w_max = df["defaults"]["wheel_speed_rad_s"]
v_max = r_w * (w_max + w_max) / 2                                     # 式 (1.6.3)：两轮同速
om_max = r_w * (w_max - (-w_max)) / b_w                               # 式 (1.6.4)：两轮反向
t_turn = 2 * math.pi / om_max
assert abs(v_max - 1.0) < 1e-12                                       # 与数字工厂 AGV 的车速 1.0 m/s 相同

# ---------------------------------------------------------------- 四旋翼 X2
x2 = dof_summary("B-UAV-X2")
m_x2 = x2["mass_model"]
info = MJCF["B-UAV-X2"]
W_x2 = m_x2 * G
f_hover = W_x2 / 4
assert abs(f_hover - info["hover_N"]) < 1e-6                          # 与模型的悬停关键帧一致
tw = 4 * info["thrust_max_N"] / W_x2
arm = math.hypot(*info["rotor_xyz"][0][:2])
a_up = (4 * info["thrust_max_N"] - W_x2) / m_x2                       # 全推力竖直上升时的加速度

# ---------------------------------------------------------------- 五台的总表
rows5 = [dof_summary(e) for e in FIVE]

out(n_ch=n_ch, n_sec=n_sec, n_parts=len(parts) - 1, lv_basic=lv.get("基础", 0), lv_adv=lv.get("进阶", 0),
    lv_topic=lv.get("专题", 0), lv_mixed=n_ch - lv.get("基础", 0) - lv.get("进阶", 0) - lv.get("专题", 0),
    pc_math=part_counts["第一篇 数学基础篇"], pc_kin=part_counts["第二篇 运动学篇"], pc_dyn=part_counts["第三篇 动力学篇"],
    pc_mech=part_counts["第四篇 结构与机电设计篇"], pc_ctrl=part_counts["第五篇 控制篇"], pc_ai=part_counts["第六篇 编程与 AI 篇"],
    use_ur=len(uses["B-ARM-UR5E"]), use_pa=len(uses["B-ARM-PANDA"]), use_go=len(uses["B-LEG-GO2"]),
    use_df=len(uses["B-EDU-DIFF"]), use_x2=len(uses["B-UAV-X2"]), n_any=n_any,
    p0x=p0[0], p0y=p0[1], p0z=p0[2], r0=r0, off=off, L12=L1 + L2, reach_sheet=reach_sheet, payload=sheet["payload_kg"],
    tau_payload=tau_payload, m_ur_model=m_ur_model, m_ur_sheet=sheet["weight_kg"], rep=sheet["repeatability_mm"],
    v_joint=v_joint, ur_area=ur_area,
    pa_mass=pa["mass_model"], pa_payload=pa_sheet["payload_kg"], pa_reach=pa_sheet["reach_mm"], pa_rep=pa_sheet["repeatability_mm"],
    go_mass=go["mass_model"], go_sheet=go["datasheet"]["weight_kg"], go_payload=go["datasheet"]["payload_kg"],
    go_speed=go["datasheet"]["max_speed_m_s"], h_stand=h_stand, leg=leg, th_t=th_t, th_c=th_c,
    hip_z=hip[2],
    r_w=r_w, b_w=b_w, w_max=w_max, v_max=v_max, om_max=om_max, t_turn=t_turn,
    m_x2=m_x2, W_x2=W_x2, f_hover=f_hover, f_max=info["thrust_max_N"], tw=tw, arm=arm, a_up=a_up,
    hover_key=info["hover_N"])
