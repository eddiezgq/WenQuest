"""1.7 节：本书用到的机器人数据从问渠零件库读取（模型版本见 textbook/physics/models/来源.md）。

算例 1.7.1  把 UR5e 模型中 7 个连杆（含底座）的质量相加，与厂家技术规格中的整机重量比较。
图 1.7.1    全书的结构：导论与六篇，各篇的章数与主要的机器人问题。
"""
import json
from pathlib import Path

from bookout import T, figure, out, style
import _draw as d

entry = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
links = entry["robot"]["links"]
m_sum = sum(l["mass_kg"] for l in links)
ds = entry["datasheet"]["values"]
diff_pct = 100 * (m_sum - ds["weight_kg"]) / ds["weight_kg"]

out(n_links=len(links), m_sum=m_sum, weight=ds["weight_kg"], diff_pct=diff_pct, payload=ds["payload_kg"],
    reach=ds["reach_mm"], repeat=ds["repeatability_mm"], dof=ds["dof"], version=entry.get("version", ""))

plt = style()
parts = [(T("导论", "Introduction"), 1, 1, T("测量与估算", "measurement, estimates")),
         (T("第一篇 力学", "I Mechanics"), 2, 17, T("AGV、UR5e、Go2、四旋翼的运动与受力", "motion and forces of AGVs, UR5e, Go2, drones")),
         (T("第二篇 振动与波", "II Oscillations and waves"), 18, 21, T("机械臂振动、超声测距", "arm vibration, ultrasonic ranging")),
         (T("第三篇 热学", "III Thermodynamics"), 22, 25, T("电机与电池的发热、散热", "heating and cooling of motors, batteries")),
         (T("第四篇 电磁学", "IV Electromagnetism"), 26, 37, T("电机、传感器、无线充电", "motors, sensors, wireless charging")),
         (T("第五篇 光学", "V Optics"), 38, 41, T("相机、激光雷达", "cameras, LiDAR")),
         (T("第六篇 近代物理", "VI Modern physics"), 42, 49, T("GPS、芯片、激光器、辐射环境", "GPS, chips, lasers, radiation"))]
fig, ax = plt.subplots(figsize=(7.4, 3.3))
cols = ["#7a868d", "#1d6fb8", "#2ca02c", "#e67e22", "#8e44ad", "#c0392b", "#16a085"]
for i, ((name, a, b, robo), col) in enumerate(zip(parts, cols)):
    y = len(parts) - 1 - i
    ax.barh(y, b - a + 1, left=a - 0.5, color=col, alpha=0.8, height=0.6)
    ax.text(0, y, name, ha="right", va="center", fontsize=9)
    ax.text(b + 1, y, (f"{a}" if a == b else f"{a}–{b}") + T(" 章  ", "  ") + robo, va="center", fontsize=8.5, color=d.INK)
ax.set_xlim(-13, 78); ax.set_ylim(-0.6, len(parts) - 0.4); d.clean(ax)
figure(fig, "fig1_7_1")
