"""3.8 用代码建模：参数化轴承座（build123d）。输入一个轴承型号，按设计规则推出全部尺寸，生成三维实体、导出 STEP；
同一个程序生成 6205、6207、6209 三个规格（程序 3.8.1，图 3.8.1）。"""
import math
import os
import tempfile

import build123d as bd

import _ch3 as H
import mdstd
from bookout import T, figure, out, style

R20 = [10, 11.2, 12.5, 14, 16, 18, 20, 22.4, 25, 28, 31.5, 35.5, 40, 45, 50, 56, 63, 71, 80, 90, 100]   # 优先数系 R20（第 2.6 节）


def params(brg):
    """设计规则：轴承型号 → 全部尺寸。改规则只改这里，模型和图纸一起变。"""
    b = mdstd.bearing(brg)                         # 轴承 d、D、B（GB/T 276，本书标准表）
    D, B = b["D"], b["B"]
    wall = math.floor(0.12 * D + 3 + 0.5)                     # 轴承孔壁厚随外径增大
    Ro = D / 2 + wall                              # 上部圆弧半径
    H = next(v for v in R20 if v >= Ro + 2)        # 中心高：取 R20 优先数
    bolt, dh = ("M8", 9.0) if D <= 52 else ("M10", 11.0) if D <= 72 else ("M12", 13.5)   # 地脚螺栓与通孔（GB/T 5277）
    W = B + 14                                     # 座宽 = 轴承宽 + 端盖止口 4 + 挡肩 10
    Lh = 2 * (Ro + dh + 2)                         # 地脚孔中心距：孔中心离立板 dh + 2，孔边离立板 dh/2 + 2（放得下垫圈）
    return dict(brg=brg, D=D, B=B, wall=wall, Ro=Ro, H=H, bolt=bolt, dh=dh, W=W, Wb=W + 12, tb=math.floor(0.25 * H + 0.5),
                Lh=Lh, L=math.ceil(Lh + 3 * dh), D2=D - 8, seat=B + 4, Lr=Lh - 2 * dh - 10, hr=2.0, dg=6.0)


def model(p):
    """特征的顺序就是加工和设计的顺序：底板 → 立板与圆弧 → 台阶孔 → 地脚孔 → 底面挖空 → 注油孔"""
    L, W, Wb, H, Ro, tb = p["L"], p["W"], p["Wb"], p["H"], p["Ro"], p["tb"]
    s = bd.Pos(0, 0, tb / 2) * bd.Box(L, Wb, tb)                                              # 底板
    s += bd.Pos(0, 0, H / 2) * bd.Box(2 * Ro, W, H)                                            # 立板
    s += bd.Pos(0, 0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(Ro, W)                               # 上部圆弧
    s -= bd.Pos(0, 0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(p["D2"] / 2, W + 2)                 # 挡肩孔（贯通）
    y0 = -W / 2 + p["seat"] / 2 - 0.5
    s -= bd.Pos(0, y0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(p["D"] / 2, p["seat"] + 1)          # 轴承孔（从前端面开）
    for x in (-p["Lh"] / 2, p["Lh"] / 2):
        s -= bd.Pos(x, 0, tb / 2) * bd.Cylinder(p["dh"] / 2, tb + 2)                           # 地脚孔
    s -= bd.Pos(0, 0, p["hr"] / 2 - 0.5) * bd.Box(p["Lr"], Wb + 2, p["hr"] + 1)                # 底面中间挖空，两端着地
    hg = Ro - p["D"] / 2 + 2
    s -= bd.Pos(0, 0, H + p["D"] / 2 - 1 + hg / 2) * bd.Cylinder(p["dg"] / 2, hg)              # 注油孔
    return s.clean()


rows, solids = [], {}
tmp = tempfile.mkdtemp()
for brg in ("6205", "6207", "6209"):
    p = params(brg)
    s = model(p)
    assert abs(s.volume - H.pillow_block(H.pillow_params(brg)).volume) < 1e-6 * s.volume   # 与本章其他程序用的模型相同
    path = os.path.join(tmp, f"pillow_{brg}.step")
    bd.export_step(s, path)                                                                   # 交给 CAE、CAM、PLM 的格式
    rho = 7.2                                                                                 # 灰铸铁 HT200，g/cm³
    rows.append({**p, "mass": s.volume * rho / 1e6, "step_kb": os.path.getsize(path) / 1024, "faces": len(s.faces())})
    solids[brg] = s

plt = style()
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.7), gridspec_kw={"width_ratios": [r["L"] for r in rows]})
for ax, r in zip(axs, rows):
    sh = H.Sheet(ax)
    sh.polys(H.project(solids[r["brg"]], "iso")[0], "thick")
    ax.set_title(T(f"{r['brg']}：D = {r['D']}，H = {r['H']:g}，L = {r['L']:g}\n{r['bolt']} 地脚螺栓，{r['mass']:.1f} kg",
                   f"{r['brg']}: D = {r['D']}, H = {r['H']:g}, L = {r['L']:g}\n{r['bolt']} bolts, {r['mass']:.1f} kg"), fontsize=7.5)
    ax.set_xlim(-rows[-1]["L"] * 0.62, rows[-1]["L"] * 0.62)
    ax.set_ylim(-rows[-1]["L"] * 0.32, rows[-1]["L"] * 0.62)
fig.tight_layout()
figure(fig, "fig3_8_1")

r5, r7, r9 = rows
out(n_lines=sum(1 for ln in open(__file__, encoding="utf-8") if ln.strip() and not ln.strip().startswith("#")),
    L5=r5["L"], L7=r7["L"], L9=r9["L"], H5=r5["H"], H7=r7["H"], H9=r9["H"], m5=r5["mass"], m7=r7["mass"], m9=r9["mass"],
    bolt5=r5["bolt"], bolt9=r9["bolt"], faces7=r7["faces"], step7=r7["step_kb"], wall7=r7["wall"], Ro7=r7["Ro"])
