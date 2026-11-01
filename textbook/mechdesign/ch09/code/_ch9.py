"""第 9 章共用：材料常数、梁单元、谐波减速器的扭转刚度、UR5e 手臂的刚度模型、压杆与板的稳定。

- 材料：数字工厂材料库（经 _ch8.mat）；
- UR5e：连杆长度与质量取零件库 MJCF（第 7 章 _ch7.ur5e、ur5e_arm）；连杆管的截面是本书设定；
- 谐波减速器 CSF：零件库 D-RDC-HD-CSF 的 K1–K3（10⁴ N·m/rad）；分段点 T1、T2 零件库里没有，取样本值（见 CSF_T12）；
- 滚珠丝杠：零件库 A-BSC-SFU。
长度 mm，力 N，力矩 N·mm（对外输出时多换成 N·m），应力 MPa。
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
ROOT = HERE.parents[3]
for p in (BOOK / "ch08" / "code", BOOK / "ch07" / "code", BOOK / "ch33" / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import _ch7 as C7                       # noqa: E402
import _ch8 as H8                       # noqa: E402
import _rj as RJ                        # noqa: E402
from bookout import COLORS, T           # noqa: E402

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]
mat = H8.mat
G = C7.G
LIB = ROOT / "library" / "catalog"


def lib_rows(pid):
    with (next(LIB.glob(f"*/{pid}")) / "specs.csv").open(encoding="utf-8") as f:
        return {r["size"]: r for r in csv.DictReader(f)}


# ---------------------------------------------------------------- 截面
def I_tube(D, t):
    return math.pi / 64 * (D ** 4 - (D - 2 * t) ** 4)


def A_tube(D, t):
    return math.pi / 4 * (D ** 2 - (D - 2 * t) ** 2)


# ---------------------------------------------------------------- 谐波减速器的扭转刚度（三段折线）
# 样本 csf-csg-catalog 的扭转刚度一节：减速比 80 以上时的分段转矩 T1、T2（N·m）。零件库只登记了 K1–K3，本书补这两列（待补入零件库）。
CSF_T12 = {"17": (3.9, 12.0), "25": (14.0, 48.0), "32": (29.0, 108.0)}


def csf(size="25-100"):
    r = lib_rows("D-RDC-HD-CSF")[size]
    T1, T2 = CSF_T12[size.split("-")[0]]
    return {"size": size, "K1": float(r["K1_1e4_Nm_rad"]) * 1e4, "K2": float(r["K2_1e4_Nm_rad"]) * 1e4,
            "K3": float(r["K3_1e4_Nm_rad"]) * 1e4, "T1": T1, "T2": T2, "rated": float(r["T_rated_Nm"]),
            "repeat": float(r["T_repeat_Nm"]), "avg": float(r["T_avg_Nm"]), "momentary": float(r["T_momentary_Nm"]), "mass": float(r["mass_kg"]), "OD": float(r["OD_mm"])}


def windup(Tq, k):
    """转矩 Tq（N·m，取绝对值）下的扭转角 rad（从零转矩算起）"""
    Tq = abs(Tq)
    if Tq <= k["T1"]:
        return Tq / k["K1"]
    if Tq <= k["T2"]:
        return k["T1"] / k["K1"] + (Tq - k["T1"]) / k["K2"]
    return k["T1"] / k["K1"] + (k["T2"] - k["T1"]) / k["K2"] + (Tq - k["T2"]) / k["K3"]


# ---------------------------------------------------------------- UR5e 手臂：水平伸直时末端的下垂
# 连杆管的截面（本书设定，6061-T6）：上臂 Ø85×2.5，小臂 Ø75×2（与第 5、8 章相同）。关节壳体看作刚体，连杆管长度取关节间距。
TUBE_UA, TUBE_FA = (85.0, 2.5), (75.0, 2.0)
# 底座关节 J1 的轴承（交叉滚子轴承）抵抗倾覆力矩的刚度 N·m/rad（本书设定，同尺寸交叉滚子轴承样本的量级）
K_TILT_J1 = 2.0e5


def cantilever(L, EI, w=0.0, P=0.0, M=0.0):
    """悬臂梁自由端的挠度和转角（向下为正）：均布 w（N/mm）、端部力 P（N）、端部力矩 M（N·mm，使梁向下弯为正）"""
    y = w * L ** 4 / (8 * EI) + P * L ** 3 / (3 * EI) + M * L ** 2 / (2 * EI)
    th = w * L ** 3 / (6 * EI) + P * L ** 2 / (2 * EI) + M * L / EI
    return y, th


def k_rj201():
    """肩关节输出轴 RJ-201（第 33 章：Ø50/Ø30，40Cr 调质）的扭转刚度 N·m/rad，按第 33 章的分段公式（线性）"""
    m = mat("40Cr-QT")
    return 1e3 / RJ.twist(1e3 * 1e3, RJ.segments(RJ.SEAT), m["G"])


def arm_sag(payload=5.0, size="25-100", tube_ua=TUBE_UA, tube_fa=TUBE_FA, k_tilt=K_TILT_J1, material="6061-T6"):
    """返回各环对末端下垂的贡献（mm）和中间量。手臂水平伸直，重力向下；小变形，各环叠加。
    改管子截面或减速器规格时，自重随之改变：管子多出（或少）的质量按管长均布（铝 2.7 g/cm³），肘关节减速器部件的质量差加在肘关节处
    （肩关节的减速器在转轴上，不产生重力矩）。"""
    U = C7.ur5e()
    L1, L2, LW = U["L_ua"] * 1e3, U["L_fa"] * 1e3, U["L_w"] * 1e3
    x_tip = L1 + L2 + LW
    m_ua = U["m_ua"] + (A_tube(*tube_ua) - A_tube(*TUBE_UA)) * L1 * 2.7e-6
    m_fa = U["m_fa"] + (A_tube(*tube_fa) - A_tube(*TUBE_FA)) * L2 * 2.7e-6
    k = csf(size)
    m_el = k["mass"] - csf("25-100")["mass"]
    m_w = U["m_w"]
    E = mat(material)["E"]
    EI1, EI2 = E * I_tube(*tube_ua), E * I_tube(*tube_fa)
    Wp, Ww, Wfa, Wua, Wel = payload * G, m_w * G, m_fa * G, m_ua * G, m_el * G
    # 肘关节（J3）处：小臂及以外的力和力矩
    T3 = (Wfa * L2 / 2 + Ww * L2 + Wp * (L2 + LW)) / 1e3                      # N·m（小臂质量按沿管均布）
    T2 = (Wua * L1 / 2 + Wel * L1 + Wfa * (L1 + L2 / 2) + Ww * (L1 + L2) + Wp * x_tip) / 1e3
    # 小臂管：根部固定在肘关节壳体上，自重均布，末端受腕部重量和负载（负载在其外 LW 处，折成力和力矩）
    y_fa, th_fa = cantilever(L2, EI2, w=Wfa / L2, P=Ww + Wp, M=Wp * LW)
    # 上臂管：自重均布，末端（肘）受肘关节及以外的全部重量和力矩
    y_ua, th_ua = cantilever(L1, EI1, w=Wua / L1, P=Wel + Wfa + Ww + Wp, M=T3 * 1e3)
    th2, th3, th1 = windup(T2, k), windup(T3, k), T2 / k_tilt
    th_rj = T2 / k_rj201()
    parts = {"tilt": th1 * x_tip, "j2": th2 * x_tip, "rj": th_rj * x_tip, "ua": y_ua + th_ua * (L2 + LW),
             "j3": th3 * (L2 + LW), "fa": y_fa + th_fa * LW}
    return {"parts": parts, "total": sum(parts.values()), "T2": T2, "T3": T3, "th1": th1, "th2": th2, "th3": th3, "th_rj": th_rj,
            "x_tip": x_tip, "L1": L1, "L2": L2, "LW": LW, "EI1": EI1, "EI2": EI2, "k": k, "y_ua": y_ua, "th_ua": th_ua,
            "y_fa": y_fa, "th_fa": th_fa, "m_ua": m_ua, "m_fa": m_fa, "m_el": m_el}


PART_NAMES = {"tilt": T("底座轴承倾斜（J1）", "base bearing tilt (J1)"), "j2": T("肩关节减速器扭转（J2）", "shoulder reducer windup (J2)"),
              "rj": T("肩关节输出轴 RJ-201 扭转", "shoulder output shaft RJ-201 twist"),
              "ua": T("上臂管弯曲", "upper-arm tube bending"), "j3": T("肘关节减速器扭转（J3）", "elbow reducer windup (J3)"),
              "fa": T("小臂管弯曲", "forearm tube bending")}
PART_COLORS = {"tilt": "#9467bd", "j2": "#d62728", "rj": "#8c564b", "ua": "#1f77b4", "j3": "#ff7f0e", "fa": "#2ca02c"}


# ---------------------------------------------------------------- 梁单元（平面弯曲，欧拉–伯努利）
def beam_fe(z, EI, supports, loads, h=2.0):
    """z：关键点（mm，含两端、支座、载荷点）；EI(zm) → N·mm²；supports：{z: 指定挠度 mm}；loads：{z: 力 N（向下为正）}。
    返回 (节点 z, 挠度, 转角, {支座 z: 支反力 N（向上为正）})"""
    pts = sorted(set(z) | set(supports) | set(loads))
    zz = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.ceil((b - a) / h)))
        zz += list(np.linspace(a, b, n + 1)[1:])
    zz = np.array(zz)
    n = len(zz)
    K = np.zeros((2 * n, 2 * n))
    for e in range(n - 1):
        L = zz[e + 1] - zz[e]
        k = EI((zz[e] + zz[e + 1]) / 2) / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                                            [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k
    f = np.zeros(2 * n)
    node = lambda zq: int(np.argmin(abs(zz - zq)))
    for zq, F in loads.items():
        f[2 * node(zq)] += F
    u = np.zeros(2 * n)
    fixed = {2 * node(zq): v for zq, v in supports.items()}
    for i, v in fixed.items():
        u[i] = v
    free = [i for i in range(2 * n) if i not in fixed]
    fx = list(fixed)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free] - K[np.ix_(free, fx)] @ u[fx])
    r = K @ u - f
    return zz, u[0::2], u[1::2], {zq: -r[2 * node(zq)] for zq in supports}


# ---------------------------------------------------------------- 压杆
def euler(E, I, L, mu):
    return math.pi ** 2 * E * I / (mu * L) ** 2


def column_cr(E, sy, A, I, L, mu):
    """欧拉与约翰逊抛物线：返回 (临界力 N, 柔度 λ, 分界柔度 λc, 用的公式)"""
    i = math.sqrt(I / A)
    lam = mu * L / i
    lam_c = math.pi * math.sqrt(2 * E / sy)
    if lam >= lam_c:
        return math.pi ** 2 * E / lam ** 2 * A, lam, lam_c, "euler"
    return A * (sy - (sy * lam / (2 * math.pi)) ** 2 / E), lam, lam_c, "johnson"


# ---------------------------------------------------------------- 薄壁
def plate_k(alpha, m_max=12):
    """四边简支矩形板单向均匀受压的屈曲系数 k = min_m (m/α + α/m)²，α = a/b（a 沿受压方向）"""
    return min((m / alpha + alpha / m) ** 2 for m in range(1, m_max + 1))


def plate_cr(E, nu, t, b, k):
    return k * math.pi ** 2 * E / (12 * (1 - nu ** 2)) * (t / b) ** 2


def tube_local_cr(E, nu, t, R, knock=True):
    """薄壁圆管受弯的局部屈曲应力：经典值 E t /(R √(3(1 − ν²)))（ν = 0.3 时约 0.605 E t/R），
    乘 NASA SP-8007 的折减系数 γ = 1 − 0.731(1 − e^(−φ))，φ = √(R/t)/16（受弯）"""
    cl = E * t / (R * math.sqrt(3 * (1 - nu ** 2)))
    if not knock:
        return cl, 1.0
    g = 1 - 0.731 * (1 - math.exp(-math.sqrt(R / t) / 16))
    return cl * g, g
