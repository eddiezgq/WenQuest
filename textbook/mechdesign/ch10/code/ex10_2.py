"""10.3 脆性材料的强度理论：最大正应力、库仑–莫尔，与冯·米塞斯的比较。

算例 10.3.1  WQR-105 箱体输出轴的轴承座（HT200 灰铸铁）。数字工厂的箱体示例零件只做热分析、没有轴承孔，这里从箱体上“切下”一段轴承座
            做简化模型（本书设定的尺寸：底座 220 × 20、座体宽 130、轴承孔 Ø72（6207 外径）、孔中心高 130、厚 40），底面固定，
            孔正下方 ±60° 的受载区受轴承力，径向压力按余弦分布。轴承力取第 33 章 SH-301 B 版在额定转矩下较大的那个支反力，再乘第 7 章矿山现场的起动峰值系数
            （本书取 2.5，见程序）。用数字工厂 CAE 同一套程序求解，从节点应力张量求主应力，分别按冯·米塞斯（CAE 网页给的）、
            最大正应力、库仑–莫尔求安全系数，看最危险的点在哪里、安全系数差多少；
算例 10.3.2  纯扭转的铸铁轴：σ1 = τ、σ3 = −τ，库仑–莫尔给出的扭转强度与拉伸强度之比；断面为什么是 45° 螺旋面；
图 10.3.1。
"""
import math
import os
import tempfile

import numpy as np

import _ch10 as H
import _shaft as SH
from bookout import T, figure, out, style
from cae.geometry import _LOCK, _gmsh

CI = H.mat("HT200")
ST_T = CI["ultimate_mpa"]                     # 抗拉强度（材料库）
SC_RATIO = 3.5                                # 灰铸铁抗压强度约为抗拉的 3–4 倍（手册典型值，材料库没有），本书取 3.5
ST_C = SC_RATIO * ST_T
KS = 2.5                                      # 起动峰值 / 额定（本书取值，第 7 章矿山现场的量级）

BW, BH, UW, HC, RB, RO, TH = 220.0, 20.0, 130.0, 130.0, 36.0, 65.0, 40.0
ZONE, NSEC = 60.0, 12                        # 受载区 ±60°，分成 12 段（每段 10°）；深沟球轴承受纯径向力、游隙为零时受载区约 ±90°，
                                              # 有游隙时变窄，本书取 ±60°，径向压力按 p = p0·cos θ 分布（本书取值）


def seat_step():
    """二维截面（x–y）拉伸 TH：底座 + 座体 + 顶部半圆，轴承孔分成多段圆弧，拉伸后受载区的每一段是单独一个面"""
    with _LOCK, tempfile.TemporaryDirectory() as tmp:
        g = _gmsh()
        g.clear()
        g.model.add("seat")
        occ = g.model.occ
        base = occ.addRectangle(-BW / 2, 0, 0, BW, BH)
        up = occ.addRectangle(-UW / 2, BH, 0, UW, HC - BH)
        top = occ.addDisk(0, HC, 0, RO, RO)
        body, _ = occ.fuse([(2, base)], [(2, up), (2, top)])
        c = occ.addPoint(0, HC, 0)
        # 孔分成多段圆弧：正下方 ±ZONE 内每 10° 一段（受载区，每段单独加力），其余部分两段
        ang = [-90 - ZONE + k * 2 * ZONE / NSEC for k in range(NSEC + 1)] + [90]
        pts = [occ.addPoint(RB * math.cos(math.radians(a)), HC + RB * math.sin(math.radians(a)), 0) for a in ang]
        arcs = [occ.addCircleArc(pts[k], c, pts[k + 1]) for k in range(len(pts) - 1)] + [occ.addCircleArc(pts[-1], c, pts[0])]
        hole = occ.addPlaneSurface([occ.addCurveLoop(arcs)])
        cut, _ = occ.cut(body, [(2, hole)])
        occ.extrude(cut, 0, 0, TH)
        occ.synchronize()
        f = os.path.join(tmp, "seat.step")
        g.write(f)
        g.clear()
        return open(f, "rb").read()


step = seat_step()
fcs = H.faces_of(step)
bottom = [f["id"] for f in fcs if f["kind"] == "plane" and abs(f["center"][1]) < 1e-6]
A_SEC = 2 * math.pi * RB * TH * (2 * ZONE / NSEC) / 360                 # 一段的面积；圆柱面拟合的半径对小面不准，按面积认
bore = [f for f in fcs if f["kind"] == "cylinder" and abs(f["area_mm2"] / A_SEC - 1) < 0.01]
sect = []                                                            # 受载区的各段：(面编号, 段中点离正下方的角度)
for f in bore:
    th = math.degrees(math.atan2(f["center"][0], -(f["center"][1] - HC)))
    if abs(th) < ZONE:
        sect.append((f["id"], th))
Ft, Fr = SH.gear_forces()
RA = [abs(x) for x in SH.reactions(Ft)]
RR = [abs(x) for x in SH.reactions(Fr)]
F_brg = max(math.hypot(a, b) for a, b in zip(RA, RR)) * KS              # N，较大的那个轴承
# p = p0 cos θ：每段的径向力 ∝ cos θ_i，竖直分量合起来等于轴承力
w = [math.cos(math.radians(th)) for _, th in sect]
k0 = F_brg / sum(wi * math.cos(math.radians(th)) for wi, (_, th) in zip(w, sect))
loads = [{"type": "fixed", "faces": bottom}] + [
    {"type": "force", "faces": [fid], "vector_n": [k0 * wi * math.sin(math.radians(th)), -k0 * wi * math.cos(math.radians(th)), 0.0]}
    for wi, (fid, th) in zip(w, sect)]
H_MESH = 6.0
st, surf, P, STR = H.fe_solve(step, loads, H_MESH, CI)
ids = sorted(STR)
xyz = np.array([P[int(i)] for i in ids])
pr = [H.principal(STR[i]) for i in ids]
ok = xyz[:, 1] > 1.5 * H_MESH                                       # 与 CAE 一样，不计固定面附近
vm = np.array([H.vm_of(p) for p in pr])
s1 = np.array([p[0] for p in pr])
s3 = np.array([p[2] for p in pr])
sf_cm = np.array([H.cm_factor(p, ST_T, ST_C) for p in pr])
sf_rk = np.array([H.rankine_factor(p, ST_T, ST_C) for p in pr])
iv = int(np.argmax(np.where(ok, vm, -1)))
icm = int(np.argmin(np.where(ok, sf_cm, np.inf)))
irk = int(np.argmin(np.where(ok, sf_rk, np.inf)))
big = ok & (1 / sf_cm > 0.3 / sf_cm[icm])                               # 按库仑–莫尔利用率不低于最大值 30% 的点
rr = np.where(big, (ST_T / np.maximum(vm, 1e-9)) / sf_cm, 0.0)        # 冯·米塞斯安全系数 / 库仑–莫尔安全系数：> 1 表示冯·米塞斯不保守
iu = int(np.argmax(rr))
ic = int(np.argmin(np.where(ok, s3, np.inf)))                       # 压得最厉害的点（受载区中间的孔壁）
SF_vm = ST_T / vm[iv]                                               # CAE 网页的做法：强度 ÷ 最大冯·米塞斯（铸铁取抗拉强度）
SF_cm, SF_rk = sf_cm[icm], sf_rk[irk]
ang = lambda k: math.degrees(math.atan2(xyz[k, 0], -(xyz[k, 1] - HC)))   # noqa: E731  从孔的正下方量起的角度
# 纯扭转：σ1 = τ、σ3 = −τ → 库仑–莫尔 τ_b = 1/(1/σt + 1/σc)
tau_cm = 1 / (1 / ST_T + 1 / ST_C)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.1))
front = ok & (np.abs(xyz[:, 2] - TH) < 1e-6)                        # 前端面上的节点
util_vm = vm / ST_T
util_cm = 1 / np.maximum(sf_cm, 1e-9)
vmax = float(max(util_vm[front].max(), util_cm[front].max()))
for ax, val, ttl in ((a0, util_vm, T("(a) 按冯·米塞斯：σ_vM / σt（CAE 网页的做法）", "(a) von Mises: σ_vM / σt (as on the CAE page)")),
                     (a1, util_cm, T("(b) 按库仑–莫尔：σ1/σt − σ3/σc", "(b) Coulomb–Mohr: σ1/σt − σ3/σc"))):
    sc = ax.scatter(xyz[front, 0], xyz[front, 1], c=val[front], s=2.0, cmap="viridis", vmin=0, vmax=vmax, linewidths=0, rasterized=True)
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
    cb.ax.tick_params(labelsize=5.8)
    ax.set_aspect("equal")
    ax.set_xlim(-BW / 2 - 5, BW / 2 + 5)
    ax.set_ylim(-5, HC + RO + 5)
    ax.tick_params(labelsize=6.0)
    ax.set_xlabel("x / mm", fontsize=6.6)
    ax.set_ylabel("y / mm", fontsize=6.6)
    ax.set_title(ttl, fontsize=7.0)
a0.plot([xyz[iv, 0]], [xyz[iv, 1]], "x", color="#d62728", ms=6)
a1.plot([xyz[icm, 0]], [xyz[icm, 1]], "x", color="#d62728", ms=6)
for ax in (a0, a1):
    ax.plot([xyz[ic, 0]], [xyz[ic, 1]], "o", mfc="none", color="#ff7f0e", ms=6)
a0.annotate("", xy=(0, HC - RB - 2), xytext=(0, HC - RB + 30), arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.0))
fig.tight_layout()
figure(fig, "fig10_3_1")

out(zone=ZONE, nsec=len(sect), BW=BW, UW=UW, HC=HC, D=2 * RB, TH=TH, h=H_MESH, el=st["elements"], st=ST_T, sc=ST_C, sc_ratio=SC_RATIO, ks=KS,
    F_brg=F_brg, F_rated=F_brg / KS, E=CI["E_mpa"],
    vm_max=vm[iv], vm_ang=ang(iv), vm_s1=s1[iv], vm_s3=s3[iv], SF_vm=SF_vm,
    SF_cm=SF_cm, cm_ang=ang(icm), cm_s1=s1[icm], cm_s3=s3[icm], cm_vm=vm[icm],
    SF_rk=SF_rk, rk_ang=ang(irk), c_ang=ang(ic), c_s1=s1[ic], c_s3=s3[ic], c_vm=vm[ic], c_SFvm=ST_T / vm[ic], c_SFcm=sf_cm[ic],
    c_ratio=sf_cm[ic] / (ST_T / vm[ic]), unc=float(rr[iu]), unc_ang=abs(ang(iu)), unc_s1=s1[iu], unc_s3=s3[iu], unc_s2=float(H.principal(STR[ids[iu]])[1]), ratio_vm_cm=SF_vm / SF_cm, tau_cm=tau_cm, tau_ratio=tau_cm / ST_T)
