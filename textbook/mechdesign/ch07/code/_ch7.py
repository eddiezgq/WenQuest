"""第 7 章共用：数字工厂的载荷数据与雨流计数。

- 跑合试验台的转矩记录：sim/engine.torque_record（与数字工厂仿真车间同一个函数，同一件每次一样）；
- 客户现场（数字孪生）：twin/field.day_summary —— 矿山皮带机、港口输送、食品包装线三类客户每天的运行摘要
  （运行小时、起动次数、平均/最大转矩、雨流计数、载荷直方图）；
- WQR-105 的齿轮、轴、轴承：twin/models（三根轴的转矩、六个轴承的径向力；输出轴按数字孪生的简化布置，即 A 版轴段，与第 33 章 B 版不同）；
- UR5e：零件库 B-ARM-UR5E 的 MuJoCo 模型（MJCF）里的连杆长度、质量和质心。
转矩 N·m，长度 m，时间 s。
"""
from __future__ import annotations

import datetime as dt
import math
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / "factory", ROOT / "factory" / "digital", HERE.parents[1] / "conventions"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from bookout import COLORS, T           # noqa: E402
from sim.engine import torque_record     # noqa: E402
from twin import field as FIELD          # noqa: E402
from twin import models as TM            # noqa: E402

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]
SITE_COLOR = {"mine": "#d62728", "port": "#1f77b4", "food": "#2ca02c"}
SITE_NAME = {"mine": T("矿山皮带机", "mine belt conveyor"), "port": T("港口输送", "port conveyor"), "food": T("食品包装线", "food packaging line")}
RATED = TM.RATED_T_NM


def bench(serial="WQR-105-00001", wo="WO-TS-1"):
    """跑合试验台“工况模拟”段的转矩记录：返回 (t, T) 与原始记录"""
    r = torque_record(serial, wo, "WQR-105")
    dtp = 1.0 / r["rate_hz"]
    y = r["samples_nm"]
    return [i * dtp for i in range(len(y))], y, r


def site_year(site, serial="WQR-105-00001", start=dt.date(2025, 1, 1), days=365):
    """一台减速器在某类客户现场一年的每日运行摘要（数字孪生的客户现场模拟器）"""
    return [FIELD.day_summary(serial, site, start + dt.timedelta(days=k)) for k in range(days)]


# ---------------------------------------------------------------- 雨流计数（ASTM E1049-85 的四点法 / 三点法）
def reversals(x):
    """取出转折点（峰谷），去掉相等的相邻点"""
    out = []
    for v in x:
        if out and v == out[-1]:
            continue
        if len(out) >= 2 and (out[-1] - out[-2]) * (v - out[-1]) > 0:
            out[-1] = v                     # 同方向继续，替换
        else:
            out.append(v)
    return out


def rainflow(x):
    """ASTM E1049-85 5.4.4 的雨流计数。返回 [(范围, 平均值, 次数)]，次数 1 为全循环、0.5 为半循环"""
    stack, out = [], []
    for v in reversals(x):
        stack.append(v)
        while len(stack) >= 3:
            X = abs(stack[-1] - stack[-2])
            Y = abs(stack[-2] - stack[-3])
            if X < Y:
                break
            if len(stack) == 3:             # Y 含起点：记半循环，去掉起点
                out.append((Y, (stack[-2] + stack[-3]) / 2, 0.5))
                stack.pop(0)
            else:
                out.append((Y, (stack[-2] + stack[-3]) / 2, 1.0))
                last = stack.pop()
                stack.pop()
                stack.pop()
                stack.append(last)
    for a, b in zip(stack[:-1], stack[1:]):
        out.append((abs(b - a), (a + b) / 2, 0.5))
    return out


def eq_value(pairs, m):
    """当量值 (Σ nᵢ Sᵢ^m / Σ nᵢ)^(1/m)"""
    n = sum(c for _, c in pairs)
    return (sum(c * s ** m for s, c in pairs) / n) ** (1 / m)


# ---------------------------------------------------------------- UR5e（零件库的 MJCF）
MJCF = Path(os.environ.get("WQ_MENAGERIE", "/opt/menagerie")) / "universal_robots_ur5e" / "ur5e.xml"


def ur5e():
    """肩—肘—腕在一条直线上时的连杆参数：上臂、小臂长度与质心、质量；腕部三个连杆的质量；关节的力矩限值"""
    xml = MJCF.read_text(encoding="utf-8")

    def blk(name):
        i = xml.index(f'<body name="{name}"')
        return xml[i:i + 400]

    def num(pat, s):
        return float(re.search(pat, s).group(1))

    ua, fa = blk("upper_arm_link"), blk("forearm_link")
    d = {"m_ua": num(r'mass="([0-9.]+)"', ua), "c_ua": num(r'inertial mass="[0-9.]+" pos="0 0 ([0-9.]+)"', ua),
         "L_ua": num(r'pos="0 -?[0-9.]+ ([0-9.]+)"', fa),
         "m_fa": num(r'mass="([0-9.]+)"', fa), "c_fa": num(r'inertial mass="[0-9.]+" pos="0 0 ([0-9.]+)"', fa),
         "L_fa": num(r'pos="0 0 ([0-9.]+)"', blk("wrist_1_link")),
         "m_w": sum(num(r'mass="([0-9.]+)"', blk(b)) for b in ("wrist_1_link", "wrist_2_link", "wrist_3_link")),
         "L_w": num(r'pos="0 0 ([0-9.]+)"', blk("wrist_3_link"))}
    i = xml.index('<default class="size3">')
    d["tau_big"] = num(r'forcerange="-?[0-9.]+ ([0-9.]+)"', xml[xml.index("<general"):i])
    d["tau_small"] = num(r'forcerange="-?[0-9.]+ ([0-9.]+)"', xml[xml.index('<default class="size1">'):])
    return d


G = 9.81


def ur5e_arm(payload=5.0):
    """手臂伸直时肩关节以外的集中质量 [(名称, 质量 kg, 到肩关节的距离 m)]（腕部集中在小臂末端，负载在其外 L_w 处）"""
    U = ur5e()
    L1, L2, LW = U["L_ua"], U["L_fa"], U["L_w"]
    return [(T("上臂", "upper arm"), U["m_ua"], U["c_ua"]), (T("小臂", "forearm"), U["m_fa"], L1 + U["c_fa"]),
            (T("腕部", "wrist"), U["m_w"], L1 + L2), (T("负载", "payload"), payload, L1 + L2 + LW)]


def shaft_out_gear_seat(t_out=None):
    """WQR-105 输出轴齿轮位（Ø40）的弯矩与扭矩：支反力取数字孪生的轴承力模型（A 版的轴段，与第 33 章 B 版不同），返回 (M N·m, T N·m, d mm)"""
    t_out = RATED if t_out is None else t_out
    seg = [(30, 40), (35, 12), (40, 60), (35, 25), (30, 30)]
    x = [0.0]
    for _, l in seg:
        x.append(x[-1] + l)
    xa, xg = (x[1] + x[2]) / 2, (x[2] + x[3]) / 2
    RA = TM.bearing_loads(t_out)["out-A"]
    return RA * (xg - xa) / 1000, t_out, 40.0
