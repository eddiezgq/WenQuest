"""第 33 章共用：WQR-105 输出轴 SH-301（本书 B 版方案）的几何、载荷与计算。

所有算例程序都从这里取数据，书里的数字前后一致。单位：长度 mm，力 N，力矩 N·mm（对外输出时换成 N·m），
应力 MPa。坐标 z 沿轴线，从左端面（非输出端）算起；铅垂面 y（径向力），水平面 x（圆周力）。

数字工厂里的现行 A 版（factory/digital/freecad/wq_shaft.py 的默认参数）是教学用的简化模型，B 版是本章按
轴的结构设计重新确定的方案（33.2 节），任务单 TS-33-1 让学生完成从 A 版到 B 版的工程更改。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conventions"))
import mdstd  # noqa: E402

# ---------------------------------------------------------------- 已知条件（数字工厂 WQR-105）
N_IN = 1450.0                    # 输入转速 r/min（factory/工厂设计.md）
I_TOTAL = 72 / 24 * 70 / 20      # 传动比 10.5
N_OUT = N_IN / I_TOTAL           # 输出转速 r/min
T_RATED = 350.0e3                # 输出轴额定转矩 N·mm（参数配置器 T_RATED，已含工况系数）
M_GEAR, Z_TEETH, ALPHA = 3.0, 70, math.radians(20.0)     # GR-302：m = 3，z = 70，直齿，α = 20°
D_GEAR = M_GEAR * Z_TEETH         # 分度圆直径 210 mm
BRG = "6207"                     # 两端深沟球轴承（BOM：BRG-6207）
MAT = "45-QT"                    # SH-301 材料：45 钢调质（BOM：RM-45-D50）
LIFE_H = 10000.0                 # 参数配置器默认的要求寿命 h

# ---------------------------------------------------------------- A 版（数字工厂现行）与 B 版（本章方案）
SEG_A = [(30, 40), (35, 12), (40, 60), (35, 25), (30, 30)]          # wq_shaft.py PARAMS["segments"]
KEY_A = {"segment": 2, "b": 12, "t": 5.0, "L": 45.0}
BOM_KEY_EXT_A = (8, 7, 36)        # BOM 外伸段平键 KEY-8x7x36
BLANK_GEAR_A = (225, 45)          # GR-302 锻坯 Ø225 × 45（齿轮毂宽 45）

HUB_GEAR = 55.0                   # B 版：GR-302 改为带毂锻件，毂宽 55
HUB_CPL = 70.0                    # 联轴器轮毂长（外伸段 72）
SLEEVE = 18.0                     # 左轴承与齿轮之间的套筒

# (直径, 长度, 名称, 公差带)
SEG_B = [
    (35, 37, "左轴承位 + 套筒", "k6"),
    (40, 53, "齿轮位", "r6"),
    (48, 10, "轴环", ""),
    (42, 15, "轴肩", ""),
    (35, 17, "右轴承位", "k6"),
    (35, 40, "密封段", "f9"),
    (30, 68, "外伸段（联轴器）", "k6"),
]
FILLET_B = {37: 1.0, 90: 1.6, 100: 1.6, 115: 1.0, 172: 1.0}        # 各台阶处的过渡圆角 r（z 位置 → mm）


def layout(segs):
    """[(z0, z1, d, 名称, 公差带)]，总长。"""
    out, z = [], 0.0
    for s in segs:
        d, L = s[0], s[1]
        out.append((z, z + L, d) + tuple(s[2:]))
        z += L
    return out, z


LAY_B, LEN_B = layout(SEG_B)
_brg = mdstd.bearing(BRG)
Z_BRG_A = _brg["B"] / 2                              # 左轴承中心
Z_BRG_B = LAY_B[4][0] + _brg["B"] / 2                # 右轴承中心
Z_GEAR = LAY_B[1][0] - 2 + HUB_GEAR / 2              # 齿轮毂比轴段长 2 mm（套筒压在毂上）
Z_CPL = LAY_B[6][0] + HUB_CPL / 2                    # 联轴器轮毂中心：轮毂靠在 Ø35 → Ø30 的轴肩上，伸出轴端 2 mm，由轴端挡圈压紧
SPAN = Z_BRG_B - Z_BRG_A


def diameter_at(z: float, lay=LAY_B) -> float:
    for z0, z1, d, *_ in lay:
        if z0 <= z <= z1:
            return d
    raise ValueError(z)


# ---------------------------------------------------------------- 载荷与支反力
def gear_forces(T=T_RATED):
    Ft = 2 * T / D_GEAR
    Fr = Ft * math.tan(ALPHA)
    return Ft, Fr


def reactions(F, z_load=Z_GEAR, zA=Z_BRG_A, zB=Z_BRG_B):
    """简支梁：一个横向力 F 作用在 z_load。返回 (R_A, R_B)。"""
    L = zB - zA
    RB = F * (z_load - zA) / L
    return F - RB, RB


def moment(z, F, z_load=Z_GEAR, zA=Z_BRG_A, zB=Z_BRG_B):
    """简支梁弯矩（N·mm）。外伸段没有横向载荷，弯矩为 0。"""
    RA, RB = reactions(F, z_load, zA, zB)
    if z <= zA or z >= zB:
        return 0.0
    return RA * (z - zA) if z <= z_load else RB * (zB - z)


def M_total(z, T=T_RATED):
    Ft, Fr = gear_forces(T)
    return math.hypot(moment(z, Ft), moment(z, Fr))


def torque_at(z, T=T_RATED):
    """转矩从齿轮（键的中点）传到联轴器。"""
    return T if Z_GEAR <= z <= LEN_B else 0.0


# ---------------------------------------------------------------- 截面
def W_solid(d):
    return math.pi * d ** 3 / 32


def WT_solid(d):
    return math.pi * d ** 3 / 16


def W_key(d, b, t):
    """有一个平键槽的轴截面抗弯截面系数（近似式）。"""
    return math.pi * d ** 3 / 32 - b * t * (d - t) ** 2 / (2 * d)


def WT_key(d, b, t):
    return math.pi * d ** 3 / 16 - b * t * (d - t) ** 2 / (2 * d)


# 校核截面：编号、z、直径、应力集中来源
SECTIONS = {
    "I": {"z": Z_GEAR, "d": 40, "what": ("齿轮中点（键槽、过盈配合）", "mid-gear (keyseat, press fit)"), "notch": "keyseat"},
    "II": {"z": 90.0, "d": 40, "D": 48, "r": FILLET_B[90], "what": ("轴环左侧轴肩", "shoulder at the collar"), "notch": "shoulder"},
    "III": {"z": 115.0, "d": 35, "D": 42, "r": FILLET_B[115], "what": ("右轴承轴肩", "right bearing shoulder"), "notch": "shoulder"},
    "IV": {"z": 172.0, "d": 30, "D": 35, "r": FILLET_B[172], "what": ("外伸段根部（轴肩、键槽）", "root of the extension (shoulder, keyseat)"), "notch": "keyseat"},
}


# ---------------------------------------------------------------- 疲劳：国内的安全系数法（与 Shigley 同一组修正系数）
def fatigue_factors(sec, mat, finish="ground", alpha=None):
    """返回该截面的 kσ、kτ、εσ、ετ、β、Kσ、Kτ。alpha：(ασ, ατ)，轴肩用有限元算出的值；键槽用 [SHI] 首轮估计。"""
    d = sec["d"]
    if sec["notch"] == "keyseat":
        k = mdstd.kt_estimate("keyseat_endmill")
        a_s, a_t, r = k["Kt"], k["Kts"], 0.02 * d
    else:
        a_s, a_t = alpha
        r = sec["r"]
    q_s = mdstd.notch_sensitivity(r, mat["sigma_b"])
    q_t = mdstd.notch_sensitivity(r, mat["sigma_b"], torsion=True)
    k_s, k_t = 1 + q_s * (a_s - 1), 1 + q_t * (a_t - 1)
    eps = mdstd.size_factor(d)
    beta = mdstd.surface_factor(finish, mat["sigma_b"])
    K_s = k_s / eps + 1 / beta - 1
    K_t = k_t / eps + 1 / beta - 1
    return dict(alpha_s=a_s, alpha_t=a_t, r=r, q_s=q_s, q_t=q_t, k_s=k_s, k_t=k_t, eps=eps, beta=beta, K_s=K_s, K_t=K_t)


def psi(mat):
    """平均应力影响系数：按古德曼线 ψσ = σ₋₁/σb，ψτ = τ₋₁/τb，τb 取 σb/√3（畸变能理论）。"""
    return mat["sigma_1"] / mat["sigma_b"], mat["tau_1"] / (mat["sigma_b"] / math.sqrt(3))


def safety(sec, mat, f, M, T):
    """弯曲为对称循环（σm = 0）；转矩按脉动循环（τa = τm = τ/2）。名义应力按实心截面（与 Kt 的定义一致）。"""
    d = sec["d"]
    sa = M / W_solid(d)
    tau = T / WT_solid(d)
    ta = tm = tau / 2
    ps, pt = psi(mat)
    S_s = mat["sigma_1"] / (f["K_s"] * sa) if sa > 0 else math.inf
    S_t = mat["tau_1"] / (f["K_t"] * ta + pt * tm) if tau > 0 else math.inf
    S_ca = S_s * S_t / math.sqrt(S_s ** 2 + S_t ** 2) if math.isfinite(S_s) and math.isfinite(S_t) else min(S_s, S_t)
    return dict(sigma_a=sa, tau=tau, tau_a=ta, psi_s=ps, psi_t=pt, S_s=S_s, S_t=S_t, S_ca=S_ca)


def shigley_goodman(sec, mat, f, M, T):
    """[SHI] 的做法：冯·米塞斯合成幅值与平均值，修正古德曼。Se = σ₋₁·β·ε（与上面同一组系数），Kf、Kfs 即 kσ、kτ。"""
    d = sec["d"]
    Se = mat["sigma_1"] * f["beta"] * f["eps"]
    sa = f["k_s"] * M / W_solid(d)
    ta = tm = f["k_t"] * T / WT_solid(d) / 2
    s_a = math.sqrt(sa ** 2 + 3 * ta ** 2)
    s_m = math.sqrt(3 * tm ** 2)
    n = 1 / (s_a / Se + s_m / mat["sigma_b"])
    return dict(Se=Se, sigma_a_vm=s_a, sigma_m_vm=s_m, n=n)


# ---------------------------------------------------------------- 梁模型：挠度、转角、临界转速
def beam_mesh(lay=LAY_B, h=1.0):
    """把阶梯轴分成长约 h 的梁单元，台阶、轴承、齿轮、联轴器处都设节点。"""
    pts = {0.0, lay[-1][1], Z_BRG_A, Z_BRG_B, Z_GEAR, Z_CPL}
    for z0, z1, *_ in lay:
        pts |= {z0, z1}
    pts = sorted(pts)
    z = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.ceil((b - a) / h)))
        z += list(np.linspace(a, b, n + 1)[1:])
    return np.array(z)


def _beam_matrices(z, lay, E, rho):
    n = len(z)
    K = np.zeros((2 * n, 2 * n))
    Mm = np.zeros((2 * n, 2 * n))
    for e in range(n - 1):
        L = z[e + 1] - z[e]
        d = diameter_at((z[e] + z[e + 1]) / 2, lay)
        I = math.pi * d ** 4 / 64
        A = math.pi * d ** 2 / 4
        k = E * I / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                        [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        m = rho * A * L / 420 * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L * L, 13 * L, -3 * L * L],
                                          [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L * L, -22 * L, 4 * L * L]])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k
        Mm[np.ix_(idx, idx)] += m
    return K, Mm


def deflection(F, z_load=Z_GEAR, lay=LAY_B, E=None):
    """一个平面内的挠度 y(z)（mm）与转角 θ(z)（rad），轴承处简支（只限挠度）。梁单元法，与积分法结果相同。"""
    E = E or mdstd.material(MAT)["E"]
    z = beam_mesh(lay)
    K, _ = _beam_matrices(z, lay, E, 0.0)
    f = np.zeros(2 * len(z))
    f[2 * int(np.argmin(abs(z - z_load)))] += F
    fixed = [2 * int(np.argmin(abs(z - Z_BRG_A))), 2 * int(np.argmin(abs(z - Z_BRG_B)))]
    free = [i for i in range(2 * len(z)) if i not in fixed]
    u = np.zeros(2 * len(z))
    u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    return z, u[0::2], u[1::2]


def critical_speeds(lay=LAY_B, m_gear=None, m_cpl=None, n_modes=3, E=None, rho=7.85e-9):
    """一阶及以上临界转速（r/min）：梁单元 + 齿轮、联轴器集中质量，轴承处简支。rho：t/mm³。"""
    E = E or mdstd.material(MAT)["E"]
    m_gear = gear_mass() if m_gear is None else m_gear
    m_cpl = 0.0 if m_cpl is None else m_cpl
    z = beam_mesh(lay, h=2.0)
    K, M = _beam_matrices(z, lay, E, rho)
    M[2 * int(np.argmin(abs(z - Z_GEAR))), 2 * int(np.argmin(abs(z - Z_GEAR)))] += m_gear / 1000.0     # kg → t
    M[2 * int(np.argmin(abs(z - Z_CPL))), 2 * int(np.argmin(abs(z - Z_CPL)))] += m_cpl / 1000.0
    fixed = [2 * int(np.argmin(abs(z - Z_BRG_A))), 2 * int(np.argmin(abs(z - Z_BRG_B)))]
    free = [i for i in range(2 * len(z)) if i not in fixed]
    from scipy.linalg import eigh
    w2, V = eigh(K[np.ix_(free, free)], M[np.ix_(free, free)])
    w = np.sqrt(np.abs(w2[:n_modes]))                     # rad/s（K 以 N/mm，M 以 t：ω² 单位 1/s²）
    modes = []
    for k in range(n_modes):
        u = np.zeros(2 * len(z))
        u[free] = V[:, k]
        y = u[0::2]
        modes.append(y / np.max(np.abs(y)))
    return w * 60 / (2 * math.pi), z, modes


def gear_mass():
    """GR-302（B 版）：轮缘 Ø216（齿顶圆）× 45、轮毂 Ø64 × 55、孔 Ø40；钢，ρ = 7.85 g/cm³。辐板减重不计（偏保守）。"""
    da = M_GEAR * (Z_TEETH + 2)
    v = math.pi / 4 * (da ** 2 - 64 ** 2) * 45 + math.pi / 4 * (64 ** 2 - 40 ** 2) * HUB_GEAR
    return v * 7.85e-6


# ---------------------------------------------------------------- 键（只做本章需要的挤压校核，详见第 25 章）
SIGMA_P_ALLOW = 135.0      # 钢制轮毂静联接许用挤压应力 120–150 MPa 的中值（与数字工厂参数配置器一致）


def key_torque_limit(d, b, h, L):
    """A 型平键：工作长度 l = L − b，接触高度 k = h/2；T = σp·d·k·l/2（N·mm）。"""
    return SIGMA_P_ALLOW * d * (h / 2) * (L - b) / 2


def torque_series(serial="WQR-105-00001", work_order="WO-TS-33"):
    """跑合试验台“工况模拟”的转矩记录（N·m，10 Hz，75 s）：直接调用数字工厂仿真车间的同一个函数。"""
    root = Path(__file__).resolve().parents[4] / "factory" / "digital"
    sys.path.insert(0, str(root))
    from sim.engine import torque_record
    r = torque_record(serial, work_order, "WQR-105")
    return np.array(r["samples_nm"], float), r["rate_hz"], r["rated_nm"]
