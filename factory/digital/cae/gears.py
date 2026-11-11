# -*- coding: utf-8 -*-
"""渐开线圆柱齿轮（直齿、斜齿，外啮合）的几何计算与强度校核（第 138 轮 G4.5）。

方法：GB/T 3480（等同 ISO 6336）的简化计算，按国内《机械设计》教材的通行写法：
  齿面接触  σH = ZH·ZE·Zε·Zβ·√( 2·K·T1·(u+1) / (b·d1²·u) )
  齿根弯曲  σF = 2·K·T1·YFa·YSa·Yε·Yβ / (b·mn·d1)
  K = KA·Kv·Kα·Kβ；许用应力 [σH] = σHlim·ZN / SHmin，[σF] = σFlim·YST·YN / SFmin（YST = 2）。
YFa、YSa 按当量齿数 zv = z/cos³β 查国内教材通用的表（标准齿形 α 20°、ha* 1、c* 0.25、不变位）并线性插值。
寿命系数 ZN、YN：应力循环次数 N 超过拐点（接触 5×10⁷，弯曲 3×10⁶）后，按 ISO 6336 的“允许少量点蚀以外”的
下降线在对数坐标里线性降到 10¹⁰ 时的 0.85；循环次数少于拐点取 1（这里只算高速长寿命的情况，不外推静强度段）。
单位：mm、N、N·m、MPa。
"""
from __future__ import annotations

import math

# 当量齿数 zv → (YFa, YSa)
_Y_TABLE = [(17, 2.97, 1.52), (18, 2.91, 1.53), (19, 2.85, 1.54), (20, 2.80, 1.55), (21, 2.76, 1.56), (22, 2.72, 1.57),
            (23, 2.69, 1.575), (24, 2.65, 1.58), (25, 2.62, 1.59), (26, 2.60, 1.595), (27, 2.57, 1.60), (28, 2.55, 1.61),
            (29, 2.53, 1.62), (30, 2.52, 1.625), (35, 2.45, 1.65), (40, 2.40, 1.67), (45, 2.35, 1.68), (50, 2.32, 1.70),
            (60, 2.28, 1.73), (70, 2.24, 1.75), (80, 2.22, 1.77), (90, 2.20, 1.78), (100, 2.18, 1.79), (150, 2.14, 1.83),
            (200, 2.12, 1.865)]

# 材料与热处理 → 试验齿轮的极限应力（ISO 6336-5 MQ 级的量级）
MATERIALS = {
    "20CrMnTi-carburized": dict(E=206e3, nu=0.3, sHlim=1500.0, sFlim=500.0, hard="58–62 HRC 渗碳淬火"),
    "40Cr-QT": dict(E=206e3, nu=0.3, sHlim=700.0, sFlim=290.0, hard="250–280 HBW 调质"),
    "45-QT": dict(E=206e3, nu=0.3, sHlim=600.0, sFlim=230.0, hard="220–250 HBW 调质"),
}


def y_fa_sa(zv: float) -> tuple[float, float]:
    t = _Y_TABLE
    if zv <= t[0][0]:
        return t[0][1], t[0][2]
    if zv >= t[-1][0]:
        return t[-1][1], t[-1][2]
    for (z0, f0, s0), (z1, f1, s1) in zip(t, t[1:]):
        if z0 <= zv <= z1:
            k = (zv - z0) / (z1 - z0)
            return f0 + k * (f1 - f0), s0 + k * (s1 - s0)
    raise ValueError(zv)


def z_e(E1=206e3, nu1=0.3, E2=206e3, nu2=0.3) -> float:
    """弹性系数 √MPa"""
    return math.sqrt(1.0 / (math.pi * ((1 - nu1 ** 2) / E1 + (1 - nu2 ** 2) / E2)))


def geometry(mn: float, z1: int, z2: int, beta_deg: float = 0.0, alpha_n_deg: float = 20.0, b: float | None = None,
             ha=1.0, c=0.25) -> dict:
    """标准中心距（不变位）的几何参数"""
    be, an = math.radians(beta_deg), math.radians(alpha_n_deg)
    at = math.atan(math.tan(an) / math.cos(be))
    d1, d2 = mn * z1 / math.cos(be), mn * z2 / math.cos(be)
    da1, da2 = d1 + 2 * ha * mn, d2 + 2 * ha * mn
    df1, df2 = d1 - 2 * (ha + c) * mn, d2 - 2 * (ha + c) * mn
    db1, db2 = d1 * math.cos(at), d2 * math.cos(at)
    a = (d1 + d2) / 2
    pt = math.pi * mn / math.cos(be)
    pbt = pt * math.cos(at)
    g_alpha = (math.sqrt(da1 ** 2 - db1 ** 2) + math.sqrt(da2 ** 2 - db2 ** 2)) / 2 - a * math.sin(at)
    eps_a = g_alpha / pbt
    eps_b = (b * math.sin(be) / (math.pi * mn)) if b else 0.0
    beta_b = math.atan(math.tan(be) * math.cos(at))
    return dict(mn=mn, z1=z1, z2=z2, u=z2 / z1, beta=beta_deg, alpha_t=math.degrees(at), d1=d1, d2=d2, da1=da1, da2=da2,
                df1=df1, df2=df2, db1=db1, db2=db2, a=a, b=b, eps_a=eps_a, eps_b=eps_b, beta_b=math.degrees(beta_b),
                zv1=z1 / math.cos(be) ** 3, zv2=z2 / math.cos(be) ** 3)


def z_h(beta_deg=0.0, alpha_n_deg=20.0) -> float:
    """节点区域系数"""
    be, an = math.radians(beta_deg), math.radians(alpha_n_deg)
    at = math.atan(math.tan(an) / math.cos(be))
    bb = math.atan(math.tan(be) * math.cos(at))
    return math.sqrt(2 * math.cos(bb) / (math.cos(at) ** 2 * math.tan(at)))


def life_factor(N: float, knee: float) -> float:
    if N <= knee:
        return 1.0
    return max(0.85, 1.0 - 0.15 * math.log10(N / knee) / math.log10(1e10 / knee))


def check(T1: float, n1: float, g: dict, mat1: str, mat2: str | None = None, KA=1.25, Kv=1.1, Ka=1.1, Kb=1.1,
          hours=20000.0, SHmin=1.0, SFmin=1.25) -> dict:
    """T1 小齿轮力矩 N·m，n1 小齿轮转速 r/min；g 由 geometry() 给出（要带齿宽 b）。返回应力、许用应力和安全系数。"""
    m1, m2 = MATERIALS[mat1], MATERIALS[mat2 or mat1]
    b, d1, u, mn = g["b"], g["d1"], g["u"], g["mn"]
    K = KA * Kv * Ka * Kb
    T = T1 * 1000.0                                                     # N·mm
    ZE = z_e(m1["E"], m1["nu"], m2["E"], m2["nu"])
    ZH = z_h(g["beta"])
    ea, eb = g["eps_a"], g["eps_b"]
    Zeps = math.sqrt((4 - ea) / 3 * (1 - eb) + eb / ea) if eb < 1 else math.sqrt(1 / ea)
    Zbeta = math.sqrt(math.cos(math.radians(g["beta"])))
    sH = ZH * ZE * Zeps * Zbeta * math.sqrt(2 * K * T * (u + 1) / (b * d1 ** 2 * u))
    ean = ea / math.cos(math.radians(g["beta_b"])) ** 2
    Yeps = 0.25 + 0.75 / ean
    Ybeta = max(1 - min(eb, 1.0) * g["beta"] / 120.0, 0.75)
    N1 = 60 * n1 * hours
    N2 = N1 / u
    out = dict(K=K, ZE=ZE, ZH=ZH, Zeps=Zeps, Zbeta=Zbeta, Yeps=Yeps, Ybeta=Ybeta, Ft=2 * T / d1, v=math.pi * d1 * n1 / 60000.0,
               N1=N1, N2=N2, sigma_H=sH)
    for i, (z_v, m, N) in enumerate(((g["zv1"], m1, N1), (g["zv2"], m2, N2)), 1):
        YFa, YSa = y_fa_sa(z_v)
        sF = 2 * K * T * YFa * YSa * Yeps * Ybeta / (b * mn * d1)
        ZN, YN = life_factor(N, 5e7), life_factor(N, 3e6)
        out[f"YFa{i}"], out[f"YSa{i}"] = YFa, YSa
        out[f"sigma_F{i}"] = sF
        out[f"SF{i}"] = m["sFlim"] * 2.0 * YN / sF
        out[f"SH{i}"] = m["sHlim"] * ZN / sH
        out[f"ZN{i}"], out[f"YN{i}"] = ZN, YN
    out["SH"] = min(out["SH1"], out["SH2"])
    out["SF"] = min(out["SF1"], out["SF2"])
    out["ok"] = out["SH"] >= SHmin and out["SF"] >= SFmin
    return out
