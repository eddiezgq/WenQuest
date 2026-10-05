"""第 6 章共用：XM540 舵机的 L 形安装支架（铣削、钣金、3D 打印三种做法）的几何、展开与成本模型；数字工厂的工艺数据。

- 舵机外形取零件库 D-ACT-ROBOTIS-X（XM540-W270：宽 33.5、高 58.5、深 44 mm）；
- 铣削工位费率取数字工厂（factory/factory/data.py：立式加工中心 VMC-01 的折旧 + 人工 + 能耗，美元/小时）；
- 激光切割、折弯、3D 打印的费率，铝块、铝板、PA12 粉末的单价，切削参数和各工序的辅助时间都是本书设定的教学值（与数字工厂一样用美元示意）。
长度 mm，质量 kg，时间 min，金额美元。
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / "factory", ROOT / "factory" / "digital", HERE.parents[1] / "conventions"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mdstd                            # noqa: E402
from bookout import COLORS, T           # noqa: E402
from factory import data as F           # noqa: E402

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]
C_MILL, C_SHEET, C_AM, C_IM = "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"     # 全章统一：铣削/数控 蓝、钣金 绿、3D 打印 橙、注塑 紫
LIB = ROOT / "library" / "catalog"


def lib_specs(pid):
    with (next(LIB.glob(f"*/{pid}")) / "specs.csv").open(encoding="utf-8") as f:
        return {r["size"]: r for r in csv.DictReader(f)}


SERVO_SIZE = "XM540-W270"
_s = lib_specs("D-ACT-ROBOTIS-X")[SERVO_SIZE]
SERVO = {"size": SERVO_SIZE, "W": float(_s["width_mm"]), "H": float(_s["height_mm"]), "D": float(_s["depth_mm"]),
         "mass_g": float(_s["weight_g"]), "torque": float(_s["stall_torque_Nm"])}


def rate(ws):
    """数字工厂工位的小时费率（美元/小时）"""
    return sum(F.WORKSTATIONS[ws][1])


R_VMC = rate("立式加工中心 VMC-01")
RHO_AL = 2.70e-6           # kg/mm³

# ---------------------------------------------------------------- 支架的几何（本书的设计规则）
MARGIN = 6.0               # 舵机侧面两边各留 6 mm
BASE_L = 50.0              # 底板伸出长度
B_WIDTH = SERVO["D"] + 2 * MARGIN      # 支架宽 = 舵机深 + 两边余量
UP_H = math.floor(SERVO["H"])          # 立板高与舵机高齐平（取整）
N_HOLE_UP, D_HOLE_UP = 4, 2.7          # 立板：4 个 M2.5 通孔（舵机侧面的安装孔）
N_HOLE_BASE, D_HOLE_BASE = 4, 4.5      # 底板：4 个 M4 通孔（固定到连杆上）


def milled(t=4.0, r_in=4.0):
    """铣削：从 6061 方块铣出 L 形，两板厚 t，内角圆角 r_in。返回体积、毛坯体积、加工面积等"""
    blank = (BASE_L + 2) * (B_WIDTH + 2) * (UP_H + 2)                  # 毛坯：每边留 1 mm
    vol = (BASE_L * t + (UP_H - t) * t + (1 - math.pi / 4) * r_in ** 2) * B_WIDTH
    holes = N_HOLE_UP * math.pi * D_HOLE_UP ** 2 / 4 * t + N_HOLE_BASE * math.pi * D_HOLE_BASE ** 2 / 4 * t
    vol -= holes
    area_fin = 2 * (BASE_L + UP_H) * B_WIDTH                             # 精加工面积（两板内外两面，近似）
    return {"t": t, "r_in": r_in, "vol": vol, "blank": blank, "removed": blank - vol, "area_fin": area_fin,
            "n_holes": N_HOLE_UP + N_HOLE_BASE, "mass": vol * RHO_AL, "blank_mass": blank * RHO_AL, "setups": 2}


K_FACTOR = 0.33            # 折弯的中性层系数 K（软铝、空气折弯、r/t ≈ 1 时的常用值）


def bend_allowance(t, r, angle_deg=90.0, k=K_FACTOR):
    """折弯余量 BA = θ (r + K t)（θ 为弧度）"""
    return math.radians(angle_deg) * (r + k * t)


def sheet(t=2.0, r=2.0):
    """钣金：5052 铝板一次 90° 折弯。外形尺寸按外侧计；展开长 = 两直边（扣除到折弯起点）+ 折弯余量"""
    flat_base = BASE_L - (t + r)
    flat_up = UP_H - (t + r)
    ba = bend_allowance(t, r)
    L_flat = flat_base + flat_up + ba
    vol = L_flat * B_WIDTH * t - (N_HOLE_UP * math.pi * D_HOLE_UP ** 2 / 4 + N_HOLE_BASE * math.pi * D_HOLE_BASE ** 2 / 4) * t
    cut_len = 2 * (L_flat + B_WIDTH) + N_HOLE_UP * math.pi * D_HOLE_UP + N_HOLE_BASE * math.pi * D_HOLE_BASE
    return {"t": t, "r": r, "BA": ba, "L_flat": L_flat, "vol": vol, "mass": vol * RHO_AL, "cut_len": cut_len,
            "pierces": 1 + N_HOLE_UP + N_HOLE_BASE, "bends": 1, "flat_base": flat_base, "flat_up": flat_up}


RHO_PA12 = 1.01e-6


def printed(t=3.0, r_in=4.0):
    """3D 打印（PA12 激光烧结）：同样的 L 形，壁厚 3 mm、内角圆角 4 mm（塑料刚度低，壁做厚）"""
    vol = (BASE_L * t + (UP_H - t) * t + (1 - math.pi / 4) * r_in ** 2) * B_WIDTH
    vol -= (N_HOLE_UP * math.pi * D_HOLE_UP ** 2 / 4 + N_HOLE_BASE * math.pi * D_HOLE_BASE ** 2 / 4) * t
    return {"t": t, "vol": vol, "mass": vol * RHO_PA12, "height": UP_H}


# ---------------------------------------------------------------- 成本模型（本书设定的教学值）
P = {
    "al_block": 6.0, "al_sheet": 5.0, "pa12": 80.0,              # 美元/kg：6061 铝块、5052 铝板、PA12 粉末（含回收料的损耗）
    "mrr": 40.0,                # 粗铣材料去除率 cm³/min（Ø10 立铣刀铣铝）
    "fin_rate": 2500.0,         # 精铣 mm²/min
    "t_hole": 0.3, "t_load": 2.0,  # 每个孔（钻、攻或铰）min；每次装夹、卸件 min
    "mill_setup": 60.0, "mill_prog": 90.0,   # 每批：对刀、夹具调整 min；一次性：编程 min
    "R_laser": 80.0, "R_brake": 50.0, "R_print": 30.0, "R_labour": 30.0,    # 美元/小时
    "v_cut": 3000.0, "t_pierce": 0.02, "t_bend": 0.4, "t_part_sheet": 0.5,   # 激光切割 mm/min，穿孔 min，每个折弯 min，每件上下料 min
    "laser_setup": 15.0, "brake_setup": 20.0, "sheet_prog": 30.0,         # 每批 min；一次性编程 min
    "scrap_sheet": 0.30,        # 板料利用率损失（排样后的余料）
    "print_rate": 60.0,         # 激光烧结：每台每小时烧结的零件体积 cm³（满腔排满时折算到每件）
    "print_job": 60.0, "t_post": 6.0,   # 每次打印作业的准备、冷却（摊到批）min；每件清粉、喷砂 min
}


def cost_mill(q, m=None, p=P):
    m = m or milled()
    mat = m["blank_mass"] * p["al_block"]
    run = m["removed"] / 1000 / p["mrr"] + m["area_fin"] / p["fin_rate"] + m["n_holes"] * p["t_hole"] + m["setups"] * p["t_load"]
    batch = p["mill_setup"] * m["setups"]
    once = p["mill_prog"]
    unit = mat + run / 60 * R_VMC + (batch + once) / 60 * R_VMC / q
    hours = (batch + once + run * q) / 60
    return {"unit": unit, "mat": mat, "run_min": run, "batch_min": batch + once, "hours": hours}


def cost_sheet(q, s=None, p=P):
    s = s or sheet()
    mat = s["mass"] / (1 - p["scrap_sheet"]) * p["al_sheet"]
    laser = s["cut_len"] / p["v_cut"] + s["pierces"] * p["t_pierce"]
    brake = s["bends"] * p["t_bend"] + p["t_part_sheet"]
    unit = mat + laser / 60 * p["R_laser"] + brake / 60 * p["R_brake"] + \
        (p["laser_setup"] / 60 * p["R_laser"] + p["brake_setup"] / 60 * p["R_brake"] + p["sheet_prog"] / 60 * p["R_laser"]) / q
    hours = (p["laser_setup"] + p["brake_setup"] + p["sheet_prog"] + (laser + brake) * q) / 60
    return {"unit": unit, "mat": mat, "run_min": laser + brake, "hours": hours}


def cost_print(q, a=None, p=P):
    a = a or printed()
    mat = a["mass"] * p["pa12"]
    build_h = a["vol"] / 1000 / p["print_rate"]
    unit = mat + build_h * p["R_print"] + p["t_post"] / 60 * p["R_labour"] + p["print_job"] / 60 * p["R_labour"] / q
    hours = p["print_job"] / 60 + build_h * q + p["t_post"] * q / 60
    return {"unit": unit, "mat": mat, "build_h": build_h, "hours": hours}


def breakeven(f, g):
    """两种做法的单件成本都是 C(q) = v + F/q 的形式：返回 f 开始比 g 便宜的最小整数批量（解析求交点，不靠网格）"""
    big = 1e12
    vf, vg = f(big), g(big)
    Ff, Fg = f(1) - vf, g(1) - vg
    if vf >= vg:
        return None
    qx = (Ff - Fg) / (vg - vf)
    return max(1, math.floor(qx) + 1)
