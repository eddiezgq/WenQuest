# -*- coding: utf-8 -*-
"""SH-301 输出轴零件图（A3，1:1）与毛坯图（A4，1:1）：由三维模型 models3d/workpiece.py 投影；尺寸、公差、形位公差、粗糙度和技术要求
取自工艺规程 std/SH-301_process.yaml 的 part、characteristics。书中图 50.1.2、50.1.3 与数字工厂 PLM 里的图出自这里。"""
from __future__ import annotations

import math

from models3d import workpiece as W
from models3d import shapes as S
from .sheet import Sheet


def _chars():
    p = W.plan()
    return p, {c["id"]: c for c in p["characteristics"]}


def part_sheet() -> Sheet:
    p, ch = _chars()
    segs = p["part"]["segments"]
    k = p["part"]["keyway"]
    xs = [0.0]
    for _, L, _n in segs:
        xs.append(xs[-1] + L)
    Ltot = xs[-1]
    xk0 = xs[2] + float(k["offset_mm"])
    xk1 = xk0 + float(k["L"])
    xkm = (xk0 + xk1) / 2
    shaft = W.sh301("op60").shape
    sh = Sheet("A3", title="输出轴", code="SH-301", material="45", scale_text="1:1", mass=f"{p['part']['mass_kg']:g} kg", qty="1",
               designer="", date="")
    fv = sh.view([(shaft, 1)], "front", 1.0, ref3=(0, 0, 0), at=(70, 120), hidden=False)
    sv = sh.view([(shaft, 1)], d=(1, 0, 0), up=(0, 0, 1), scale=1.0, ref3=(xkm, 0, 0), at=(330, 120), hidden=False,
                 section=((xkm, 0, 0), (-1, 0, 0)), name="A–A")
    sh.centerline(fv, (0, 0, 0), (Ltot, 0, 0), extend=5)
    sh.center_mark(sv, (xkm, 0, 0), 20)
    sh.section_label(fv, (xkm, 0, -26), (xkm, 0, 26), "A")
    # 直径（上方一排）
    dia = {0: ("Ø30 h8（0/−0.033）", 15), 1: ("Ø35 k6（+0.018/+0.002）", 17.5), 2: ("Ø40 k6（+0.018/+0.002）", 20),
           3: ("Ø35 k6（+0.018/+0.002）", 17.5), 4: ("Ø30 h8（0/−0.033）", 15)}
    for i, (txt, r) in dia.items():
        xm = (xs[i] + xs[i + 1]) / 2 + (20 if i == 2 else 0)
        sh.dia_dim(fv, (xm, 0, 0), 2 * r, txt, offset=0)
    # 长度（下方两排）
    y1, y2 = -38.0, -52.0
    for i in range(5):
        sh.dim(fv, (xs[i], 0, -dia[i][1]), (xs[i + 1], 0, -dia[i][1]), f"{segs[i][1]:g}", offset=-(abs(y1) - dia[i][1]))
    sh.dim(fv, (0, 0, -15), (Ltot, 0, -15), f"{Ltot:g}", offset=-(abs(y2) - 15))
    # 键槽：俯视的长度与位置标在主视图上方
    sh.dim(fv, (xk0, 0, 20), (xk1, 0, 20), f"{k['L']:g}", offset=26)
    sh.dim(fv, (xs[2], 0, 20), (xk0, 0, 20), f"{k['offset_mm']:g}", offset=26)
    # 断面图：键槽宽、d − t₁
    sh.dim(sv, (xkm, -6, 15), (xkm, 6, 15), "12 N9（0/−0.043）", offset=30)
    sh.dim(sv, (xkm, 24, -20), (xkm, 24, 15), "35（0/−0.2）", orient="v", offset=-52)
    # 基准与形位公差
    pa = fv.at(((xs[1] + xs[2]) / 2, 0, -17.5))
    pb = fv.at(((xs[3] + xs[4]) / 2, 0, -17.5))
    sh.datum(pa, "A", direction=(0, 1))
    sh.datum(pb, "B", direction=(0, 1))
    t1 = fv.at(((xs[1] + xs[2]) / 2, 0, 17.5))
    sh.gdt(t1, (t1[0] - 46, t1[1] - 30), "↗", "0.012", "A–B")
    t3 = fv.at(((xs[3] + xs[4]) / 2, 0, 17.5))
    sh.gdt(t3, (t3[0] + 8, t3[1] - 30), "↗", "0.012", "A–B")
    t2 = fv.at((xs[2] + 50, 0, 20))
    sh.gdt(t2, (t2[0] + 4, t2[1] - 42), "↗", "0.015", "A–B")
    tf = fv.at((xs[2], 0, 19))
    sh.gdt(tf, (tf[0] - 40, tf[1] - 52), "↗", "0.02", "A–B")
    ts = sv.at((xkm, 6, 18))
    sh.gdt(ts, (ts[0] + 34, ts[1] - 4), "⌯", "0.02", "C")
    xm2 = (xs[2] + xs[3]) / 2 + 20                   # 基准 C：齿轮位轴线（基准符号与 Ø40 的尺寸线对齐）
    sh.datum(fv.at((xm2, 0, -20)), "C", direction=(0, 1))
    # 粗糙度
    for i in (1, 2, 3):
        q = fv.at((xs[i] + 3 if i != 2 else xs[i] + 52, 0, dia[i][1]))
        sh.roughness(q, "Ra 0.8")
    q32 = sv.at((xkm, 6, 18))
    q32 = sv.at((xkm, -6, 17))
    sh.leader_note(q32, (q32[0] - 20, q32[1] - 22), "两侧 Ra 3.2")
    sh.note((330, 26), "其余", 3.5)
    sh.roughness((346, 30), "Ra 6.3")
    req = ["调质 217–255 HB", "未注倒角 C1.5", "未注尺寸公差按 GB/T 1804-m", "两端中心孔 A3.15/6.7（GB/T 145），保留",
           "轴端、键槽侧面 Ra 3.2", "齿轮定位轴肩为齿轮位左端面"]
    sh.requirements(req, (32, 230))
    return sh


def blank_sheet() -> Sheet:
    p, _ = _chars()
    segs, x0 = W.segments("blank")
    D, L = segs[0]
    shaft = W.sh301("op60").shape
    blank = W.sh301("blank").shape
    mass = math.pi * (D / 2) ** 2 * L * 7.85e-6
    sh = Sheet("A4", title="输出轴毛坯", code="SH-301-M", material="45 热轧圆钢", scale_text="1:1", qty="1", mass=f"{mass:.2f} kg")
    fv = sh.view([(blank, 1)], "front", 1.0, ref3=(0, 0, 0), at=(60, 90), hidden=False, phantom=[shaft])
    sh.centerline(fv, (x0, 0, 0), (x0 + L, 0, 0), extend=5)
    sh.dia_dim(fv, (x0 + L - 12, 0, 0), D, f"Ø{D:g}", offset=0)
    sh.dim(fv, (x0, 0, -D / 2), (x0 + L, 0, -D / 2), f"{L:g}", offset=-12)
    sh.note((60, 140), "双点画线为成品轮廓；两端各留端面余量，外圆按热轧圆钢规格", 3.5)
    sh.requirements([f"材料 45 热轧圆钢 Ø{D:g}（GB/T 702），物料编码 {p['blank']['material_item']}", "锯床下料，端面垂直度 1 mm", "下料后打钢号与炉批号"], (32, 160))
    return sh
