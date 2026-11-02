"""《数字集成电路设计》全书的手算模型：长沟道平方律 MOSFET 与 CMOS 反相器（参数按 SKY130 tt、27 °C 校准）。

书中程序 `from mos import *` 使用；与浏览器实验的 JS 模型（labs/micro/kit/models/mos.js）共用同一份参数
labs/micro/kit/models/params.json，算法一一对应，构建时比对（第 17 轮 RM2）。
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # 仓库根目录（textbook/dic/conventions/ 向上三级）
P = json.loads((ROOT / "labs/micro/kit/models/params.json").read_text(encoding="utf-8"))
VDD, VTn, VTp, kn, kp = P["VDD"], P["VTn"], P["VTp"], P["kn"], P["kp"]
L, Wmin, Cg, Cd = P["L"], P["Wmin"], P["Cg"], P["Cd"]


def idn(vgs, vds, W, L=L, vdd=None):
    """NMOS 漏极电流（A），长沟道平方律，忽略沟道长度调制。"""
    vov = vgs - VTn
    if vov <= 0 or vds <= 0:
        return 0.0
    k = kn * W / L
    return k * (vov * vds - vds * vds / 2) if vds < vov else k / 2 * vov * vov


def idp(vsg, vsd, W, L=L):
    vov = vsg - VTp
    if vov <= 0 or vsd <= 0:
        return 0.0
    k = kp * W / L
    return k * (vov * vsd - vsd * vsd / 2) if vsd < vov else k / 2 * vov * vov


def vout(vin, Wn, Wp, vdd=VDD):
    """反相器输出电压：二分法解 In = Ip，固定 60 次，与 JS 一致。"""
    lo, hi = 0.0, vdd
    for _ in range(60):
        mid = (lo + hi) / 2
        f = idn(vin, mid, Wn) - idp(vdd - vin, vdd - mid, Wp)
        if f > 0:      # 下拉更强，输出应更低
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def vm(Wn, Wp, vdd=VDD):
    r = math.sqrt(kp * Wp / (kn * Wn))
    return (VTn + r * (vdd - VTp)) / (1 + r)


def noise_margins(Wn, Wp, vdd=VDD, step=0.0005):
    """在 0..VDD 网格上找斜率 = -1 的两点（中心差分），与 JS 一致。"""
    n = int(round(vdd / step))
    vs = [i * step for i in range(n + 1)]
    vo = [vout(v, Wn, Wp, vdd) for v in vs]
    g = [(vo[i + 1] - vo[i - 1]) / (2 * step) for i in range(1, n)]
    idx = [i + 1 for i, s in enumerate(g) if s < -1]
    vil, vih = vs[idx[0]], vs[idx[-1]]
    voh, vol = vout(vil, Wn, Wp, vdd), vout(vih, Wn, Wp, vdd)
    return dict(VIL=vil, VIH=vih, VOH=voh, VOL=vol, NML=vil - vol, NMH=voh - vih)


def idsat_n(W, vdd=VDD):
    return kn / 2 * W / L * (vdd - VTn) ** 2


def idsat_p(W, vdd=VDD):
    return kp / 2 * W / L * (vdd - VTp) ** 2


def req_n(W, vdd=VDD):
    return 0.75 * vdd / idsat_n(W, vdd)


def req_p(W, vdd=VDD):
    return 0.75 * vdd / idsat_p(W, vdd)


def delays(Wn, Wp, CL, vdd=VDD):
    """tPHL、tPLH（s）：0.69·Req·(自载 + CL)。"""
    Cself = (Wn + Wp) * Cd
    return 0.69 * req_n(Wn, vdd) * (Cself + CL), 0.69 * req_p(Wp, vdd) * (Cself + CL)


def cin(Wn, Wp):
    return (Wn + Wp) * Cg


def fo4(Wn, Wp, vdd=VDD):
    return delays(Wn, Wp, 4 * cin(Wn, Wp), vdd)


def chain_delay(N, CL, ratio, vdd=VDD):
    """N 级等比反相器链，第一级为最小对称反相器，返回总延时（s）。"""
    Wn, Wp = Wmin, ratio * Wmin
    C1 = cin(Wn, Wp)
    F = CL / C1
    f = F ** (1 / N)
    R = (req_n(Wn, vdd) + req_p(Wp, vdd)) / 2
    gamma = Cd / Cg
    return N * 0.69 * R * C1 * (gamma + f)


def wn_for_vol(I, VOLmax, vdd=VDD):
    """线性区：吸收电流 I 时输出低电平不超过 VOLmax 所需的 Wn（μm）。"""
    return I / (kn / L * ((vdd - VTn) * VOLmax - VOLmax ** 2 / 2))


def dyn_power(N, alpha, C, V, f):
    return alpha * C * V * V * f * N


def fopt(gamma):
    """Optimum fan-out per stage: f (ln f − 1) = γ, by bisection on [e, 10]."""
    lo, hi = math.e, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if mid * (math.log(mid) - 1) < gamma:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fo4_tp(ratio, vdd=VDD):
    a, b = fo4(Wmin, ratio * Wmin, vdd)
    return (a + b) / 2


def vdd_for_fo4(limit, ratio, lo=0.9, hi=VDD):
    """Lowest supply whose FO4 delay (average of the two edges) is at most `limit`."""
    for _ in range(80):
        mid = (lo + hi) / 2
        if fo4_tp(ratio, mid) > limit:
            lo = mid
        else:
            hi = mid
    return hi


# ======================================================================= 第 2 章：门与逻辑努力
# 参考反相器：Wn = Wmin、Wp = r·Wmin（两管等强）。门按“等效反相器”定尺寸，最坏情况下的上拉、下拉与参考反相器一样强。

def r_ratio():
    return kn / kp


def tau():
    """逻辑努力的时间单位 τ = 0.69·R·Cinv（s）：R 为参考反相器的等效电阻（两管相等），Cinv 为它的输入电容。
    第 1 章反相器链每级延时 0.69RC1(γ + f) = τ(γ + f)，所以以 τ 为单位，反相器的寄生延时 p_inv = γ。"""
    r = r_ratio()
    R = (req_n(Wmin) + req_p(r * Wmin)) / 2
    return 0.69 * R * cin(Wmin, r * Wmin)


def gamma_self():
    return Cd / Cg


def le_g(kind, n):
    """手算模型的逻辑努力：n 输入与非门 (n + r)/(1 + r)，或非门 (1 + n·r)/(1 + r)，反相器 1。"""
    r = r_ratio()
    if kind == "inv":
        return 1.0
    if kind == "nand":
        return (n + r) / (1 + r)
    if kind == "nor":
        return (1 + n * r) / (1 + r)
    raise ValueError(kind)


def le_p(kind, n):
    """手算模型的寄生延时（以 τ 为单位）：输出节点上的漏极宽度是参考反相器的 n 倍，p = n·γ（反相器 γ）。"""
    return (1 if kind == "inv" else n) * gamma_self()


def gate_widths(kind, n):
    """等效反相器尺寸（μm）：返回 (每个 NMOS 宽, 每个 PMOS 宽)。"""
    r = r_ratio()
    if kind == "inv":
        return Wmin, r * Wmin
    if kind == "nand":
        return n * Wmin, r * Wmin
    if kind == "nor":
        return Wmin, n * r * Wmin
    raise ValueError(kind)


def path_delay(gs, ps, B, H, N=None):
    """路径的最小延时（以 τ 为单位）：D = N·F^(1/N) + ΣP，F = G·B·H。gs、ps 为各级的 g、p 列表。"""
    G = 1.0
    for g in gs:
        G *= g
    N = N or len(gs)
    F = G * B * H
    return N * F ** (1 / N) + sum(ps), F


def stage_sizes(gs, bs, Cin, Cout):
    """按每级努力相等，从输出往回求各级输入电容：Cin_i = g_i·b_i·Cout_i / f。返回 [Cin_1, …, Cin_N]，Cin_1 = Cin。"""
    G, B = 1.0, 1.0
    for g, b in zip(gs, bs):
        G *= g
        B *= b
    N = len(gs)
    f = (G * B * Cout / Cin) ** (1 / N)
    caps, c = [], Cout
    for g, b in reversed(list(zip(gs, bs))):
        c = g * b * c / f
        caps.append(c)
    return list(reversed(caps)), f


# ======================================================================= 第 4 章：导线
WIRES = P["wires"]["layers"]


def wire_r(layer, w):
    """每微米电阻（Ω/μm）：方块电阻 / 线宽。"""
    return WIRES[layer]["Rsq"] / w


def wire_c(layer, w, s=None):
    """每微米电容（F/μm）：对衬底的面积电容 + 两条边的边缘电容；给出间距 s 时再加两侧同层导线的耦合电容（邻线视为交流地）。"""
    q = WIRES[layer]
    c = q["Carea"] * w + 2 * q["Cfringe"]
    if s is not None:
        c += 2 * q["Kside"] / (s + q["s0"])
    return c * 1e-18


def wire_cc(layer, s):
    """同层相邻两条导线之间每微米的耦合电容（F/μm）。"""
    q = WIRES[layer]
    return q["Kside"] / (s + q["s0"]) * 1e-18


def wire_delay(Rd, Cself, Rw, Cw, CL):
    """驱动器（电阻 Rd、自身漏极电容 Cself）经分布式 RC 线（总电阻 Rw、总电容 Cw）驱动 CL 的 50 % 延时（s）：
    0.69·Rd·(Cself + Cw + CL) + 0.38·Rw·Cw + 0.69·Rw·CL。"""
    return 0.69 * Rd * (Cself + Cw + CL) + 0.38 * Rw * Cw + 0.69 * Rw * CL


def repeater_delay(Lw, layer, w, k, size, CL=None, s=None):
    """长度 Lw（μm）的导线分成 k 段，每段前放一个 size 倍参考反相器的中继器，最后驱动 CL（默认一个同样的中继器的输入）。返回总延时（s）。"""
    r = r_ratio()
    R0 = (req_n(Wmin) + req_p(r * Wmin)) / 2
    C0 = cin(Wmin, r * Wmin)
    Rd, Cself, Cin_rep = R0 / size, gamma_self() * C0 * size, C0 * size
    seg = Lw / k
    Rw, Cw = wire_r(layer, w) * seg, wire_c(layer, w, s) * seg
    CL = Cin_rep if CL is None else CL
    t = 0.0
    for i in range(k):
        load = Cin_rep if i < k - 1 else CL
        t += wire_delay(Rd, Cself, Rw, Cw, load)
    return t


def repeater_opt(Lw, layer, w, s=None):
    """中继器的最优段数与尺寸（闭式解，连续变量）：k = Lw·√(0.38·r·c / (0.69·R0·C0·(1 + γ)))，size = √(R0·c / (r·C0))。"""
    rr = r_ratio()
    R0 = (req_n(Wmin) + req_p(rr * Wmin)) / 2
    C0 = cin(Wmin, rr * Wmin)
    rw, cw = wire_r(layer, w), wire_c(layer, w, s)
    k = Lw * math.sqrt(0.38 * rw * cw / (0.69 * R0 * C0 * (1 + gamma_self())))
    size = math.sqrt(R0 * cw / (rw * C0))
    return k, size


def xtalk(layer, w, s, Lw, size, tr):
    """串扰（4.4 节）：受害线（线宽 w、长 Lw μm，接收端 1 个参考反相器，由 size 倍反相器保持）与干扰线以间距 s 平行，
    干扰线以上升时间 tr 跳变 VDD。返回 (Cc, Cg, 悬空时的跳动, 有驱动时的峰值, τ)。Cg 为面积 + 两侧边缘电容（邻线对边缘的遮挡不计）。"""
    q = WIRES[layer]
    r = r_ratio()
    Cc = wire_cc(layer, s) * Lw
    Cg = (q["Carea"] * w + 2 * q["Cfringe"]) * 1e-18 * Lw + cin(Wmin, r * Wmin)
    k = Cc / (Cc + Cg)
    tau_ = req_n(size * Wmin) * (Cc + Cg)
    return Cc, Cg, VDD * k, VDD * k * tau_ / tr * (1 - math.exp(-tr / tau_)), tau_


# ======================================================================= 第 3 章：时序元件
# 触发器的时序参数来自 SKY130 仿真（calib/calib_ff.py），以同一仿真中的 FO4 为单位存在 params.json 的 ff_sim；
# 书中换算成 ps 时乘手算模型的 FO4（参考反相器、两个边沿的平均），与第 2 章门参数的做法一致。

def ff_timing():
    """传输门主从触发器的时序参数（s）：tcq 时钟到输出、tsu 建立时间、th 保持时间、tau_m 亚稳态时间常数、T0 亚稳态窗口。"""
    f4 = fo4_tp(r_ratio())
    return {k: P["ff_sim"][k] * f4 for k in ("tcq", "tsu", "th", "tau_m", "T0")}


def setup_slack(T, t_logic, skew=0.0):
    """建立时间余量（s）：T + skew − (tcq + t_logic + tsu)。skew = 接收触发器的时钟比发送触发器晚到的时间。"""
    t = ff_timing()
    return T + skew - (t["tcq"] + t_logic + t["tsu"])


def hold_slack(t_logic_min, skew=0.0):
    """保持时间余量（s）：tcq + t_logic_min − (th + skew)。"""
    t = ff_timing()
    return t["tcq"] + t_logic_min - (t["th"] + skew)


def sync_tr(n, fclk, slack):
    """n 级同步器留给亚稳态的决断时间（s）：最后一级之后的逻辑留下的余量 slack，加上前 n − 1 级各一个 T − tcq − tsu。"""
    t = ff_timing()
    return slack + (n - 1) * (1 / fclk - t["tcq"] - t["tsu"])


def mtbf(tr, fclk, fdata):
    """平均故障间隔（s）：MTBF = e^(tr/τm) / (T0·fclk·fdata)。"""
    t = ff_timing()
    return math.exp(tr / t["tau_m"]) / (t["T0"] * fclk * fdata)


def ff_tcq_le():
    """tcq 的手算估计（以 τ 为单位）：两级本地时钟反相器（反相时钟驱动 3 个、同相时钟驱动 2 个参考输入），
    从锁存器的传输门（按一个与参考反相器等强的电阻）与主锁存器反相器串联给从节点充电，最后一级反相器驱动 FO4 + 反馈反相器。"""
    g = gamma_self()
    return [g + 3, g + 2, 2 * (1 + 2 * g), g + 5]


def inc_delay(bits):
    """n 位行波进位加 1 电路的关键路径（以 τ 为单位），各门取等效反相器的单位尺寸（每个输入 g 个参考输入电容）：
    每一位的进位 = 二输入与非门（带一个反相器）+ 反相器（驱动下一位的与非门和本位求和的异或门，异或门 g = 4、p = 4γ）；
    最高位的异或门驱动触发器的数据输入（一个参考输入）。"""
    g = gamma_self()
    per_bit = (1 + 2 * g) + (le_g("nand", 2) + 4 + g)
    return (bits - 1) * per_bit + (1 + 4 * g)


def tau_m_est():
    """亚稳态时间常数的手算估计（s）：τm ≈ C/gm。C 为交叉耦合反相器一个节点的电容（另一个反相器的输入 + 自身漏极），
    gm 为参考反相器在 VM 处 NMOS 与 PMOS 跨导之和（两管都在饱和区）。"""
    r = r_ratio()
    v = vm(Wmin, r * Wmin)
    gm = kn * Wmin / L * (v - VTn) + kp * r * Wmin / L * (VDD - v - VTp)
    return cin(Wmin, r * Wmin) * (1 + gamma_self()) / gm


# ======================================================================= 第 5 章：功耗
# 短路能量、漏电、电压—速度关系来自 SKY130 仿真（calib/calib_power.py），存在 params.json 的 power_sim；
# 表中间按线性（短路比）或对数（漏电、延时倍数）插值，表外取端点值。

def _interp(xs, ys, x, log=False):
    import math as _m
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            if log:
                return _m.exp(_m.log(ys[i]) + t * (_m.log(ys[i + 1]) - _m.log(ys[i])))
            return ys[i] + t * (ys[i + 1] - ys[i])


def sc_ratio(tin_fo4):
    """短路能量与充电能量之比（仿真表）：输入转换时间以 FO4 为单位。"""
    t = P["power_sim"]["sc"]
    return max(0.0, _interp([a for a, _ in t], [b for _, b in t], tin_fo4))


def leak_inv(temp=27.0, vdd=VDD):
    """参考反相器两种输入的平均漏电（A）：温度之间按对数插值，电压按仿真的漏电倍数表。"""
    q = P["power_sim"]
    ts = sorted(float(k) for k in q["leak_inv"])
    i = _interp(ts, [q["leak_inv"][str(int(k))] for k in ts], temp, log=True)
    v = q["vdd"]
    return i * _interp([a for a, _, _ in v], [c for _, _, c in v], vdd, log=True)


def fo4_scale(vdd):
    """FO4 延时相对 1.8 V 的倍数（仿真表，对数插值）。"""
    v = P["power_sim"]["vdd"]
    return _interp([a for a, _, _ in v], [b for _, b, _ in v], vdd, log=True)


def energy_per_op(vdd, n_gates, alpha, c_gate, depth_fo4, temp=27.0):
    """一个运算周期的能量（J）：动态 α·N·C·V² 加漏电 N·I_leak(T, V)·V·T_cycle，T_cycle = depth_fo4 个 FO4（按仿真倍数随电压变化）。
    返回 (动态, 漏电, 周期)。"""
    t_cyc = depth_fo4 * fo4_tp(r_ratio()) * fo4_scale(vdd)
    e_dyn = alpha * n_gates * c_gate * vdd ** 2
    e_leak = n_gates * leak_inv(temp, vdd) * vdd * t_cyc
    return e_dyn, e_leak, t_cyc


def sleep_ron(w_um, vdd=VDD):
    """PMOS 休眠管（header）导通时的线性区电阻（Ω）：1 / (k′p·W/L·(VDD − |VTp|))。"""
    return 1.0 / (kp * w_um / L * (vdd - VTp))


# ======================================================================= 第 7 章：存储器
# 6 管 SRAM 单元的手算模型（平方律，与第 1 章反相器同一套参数）：存取管 Wpg = Wmin，下拉管 Wpd = cr·Wpg，上拉管 Wpu = pr·Wpg。
# 仿真值（calib/calib_sram.py）存在 params.json 的 sram_sim。

def sram_half(vin, cr, pr, mode="read", vdd=VDD):
    """半边单元的输出电压：反相器（下拉 cr·Wmin、上拉 pr·Wmin）输入 vin；读出时存取管（栅、位线都接 VDD）从位线往输出端灌电流。
    二分法解 I下拉 = I上拉 + I存取，固定 60 次，与 JS 一致。"""
    lo, hi = 0.0, vdd
    for _ in range(60):
        mid = (lo + hi) / 2
        f = idn(vin, mid, cr * Wmin) - idp(vdd - vin, vdd - mid, pr * Wmin)
        if mode == "read":
            f -= idn(vdd - mid, vdd - mid, Wmin)
        if f > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def sram_curve(cr, pr, mode="read", step=0.002, vdd=VDD):
    n = int(round(vdd / step))
    xs = [i * step for i in range(n + 1)]
    return xs, [sram_half(x, cr, pr, mode, vdd) for x in xs]


def snm_seevinck(xs, ys, vdd=VDD):
    """Seevinck 法求静态噪声容限（V）：曲线 A 为 (x, f(x))、B 为镜像 (f(y), y)，转 45°（u = (x − y)/√2，v = (x + y)/√2），
    在同一 u 上两曲线 v 之差的正、负最大值各除以 √2，取较小的一瓣。u 取 2000 等分。与 calib_sram.py、JS 同一算法。"""
    s2 = math.sqrt(2)
    a = sorted(((x - y) / s2, (x + y) / s2) for x, y in zip(xs, ys))
    b = sorted(((y - x) / s2, (y + x) / s2) for x, y in zip(xs, ys))

    def at(c, u):
        if u <= c[0][0] or u >= c[-1][0]:
            return None
        lo, hi = 0, len(c) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if c[m][0] <= u:
                lo = m
            else:
                hi = m
        t = (u - c[lo][0]) / (c[hi][0] - c[lo][0]) if c[hi][0] > c[lo][0] else 0.0
        return c[lo][1] + t * (c[hi][1] - c[lo][1])
    pos = neg = 0.0
    n, umax = 2000, vdd / s2
    for i in range(1, n):
        u = -umax + 2 * umax * i / n
        va, vb = at(a, u), at(b, u)
        if va is None or vb is None:
            continue
        pos, neg = max(pos, va - vb), max(neg, vb - va)
    return min(pos, neg) / s2


def sram_snm(cr, pr=1.0, mode="read", vdd=VDD):
    xs, ys = sram_curve(cr, pr, mode, 0.002, vdd)
    return snm_seevinck(xs, ys, vdd)


def sram_write_q(qb, vbl, cr, pr, vdd=VDD):
    """写入时存 1 一侧的节点电压 Q：反相器（输入 QB）加存取管把 Q 往位线电压 vbl 拉（栅接 VDD）。二分法 60 次。"""
    lo, hi = 0.0, vdd
    for _ in range(60):
        mid = (lo + hi) / 2
        f = idn(qb, mid, cr * Wmin) - idp(vdd - qb, vdd - mid, pr * Wmin)
        if mid > vbl:
            f += idn(vdd - vbl, mid - vbl, Wmin)
        else:
            f -= idn(vdd - mid, vbl - mid, Wmin)
        if f > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def sram_write_trip(cr, pr, vdd=VDD, iters=120):
    """写入裕量（V）：BL 降到多低时存 1 的单元翻转。另一侧是读出状态的半边单元（BLB = VDD），QB = sram_half(Q)；
    从 Q = VDD 出发反复迭代 Q ← sram_write_q(sram_half(Q))（iters 次），仍高于 VDD/2 说明还保持原状态。
    对 BL 二分 40 次，返回翻转时的 BL 电压。与 JS 一致。"""
    def holds(vbl):
        q = vdd
        for _ in range(iters):
            q = sram_write_q(sram_half(q, cr, pr, "read", vdd), vbl, cr, pr, vdd)
        return q > vdd / 2
    lo, hi = 0.0, vdd
    for _ in range(40):
        mid = (lo + hi) / 2
        if holds(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def sram_sim_snm(cr, mode="read"):
    """仿真的 SNM（V），按单元比线性插值。"""
    t = P["sram_sim"]["snm_" + mode]
    return _interp([a for a, _ in t], [b for _, b in t], cr)


def sram_sim_write(pr):
    t = P["sram_sim"]["write"]
    return _interp([a for a, _ in t], [b for _, b in t], pr)


def sa_time(dv):
    """锁存型灵敏放大器的分辨时间（s），按输入差（V）对数插值仿真表。"""
    t = P["sram_sim"]["sa"]
    return _interp([a for a, _ in t], [b for _, b in t], dv, log=True)


def sram_access(rows, cols, word, dv=0.1, q=None):
    """存储阵列的存取时间估计（s）与面积（μm²）。rows 行 × cols 列，每次读 word 位（列选比 M = cols/word）。
    各段：
      译码：n 位行地址分成两组预译码（⌈n/2⌉ 输入与非门，取反得到预译码线），每条字线一个二输入与非门，再接反相器驱动字线；
            逻辑努力 gs = [g与非(⌈n/2⌉), 1, g与非(2), 1, …]，总级数取偶数（字线高电平有效），在 4～12 级里取延时最小者；
            总分支努力 B = rows/2，H = 字线总电容 / 地址输入电容（cin_units 个参考反相器）；
      字线：met1 导线与沿线的存取管栅电容都是分布的，取 0.38·Rw·C字线（驱动器部分已算进译码）；
      位线：t_bl0 + rows·(c_cell + 位线导线电容)·dv / i_read（c_cell、t_bl0、i_read 为仿真值；导线为 met2，每单元一个单元高，按第 4 章）；
      灵敏放大：sa_time(dv)；
      列选与输出：FO4 ×（2 + 0.5·log2 M），经验估计。
    面积：单元 + 行译码（每行 dec_w μm 宽）+ 列外围（每列 col_h μm 高）。参数在 problems.p71。返回 dict。"""
    q = q or P["problems"]["p71"]
    S = P["sram_sim"]
    rr = r_ratio()
    n = max(2, int(round(math.log2(rows))))
    n1 = (n + 1) // 2
    cw = cols * q["cell_w"]
    c_wl = cols * 2 * Wmin * Cg + wire_c("met1", WIRES["met1"]["wmin"]) * cw
    c_in = q["cin_units"] * cin(Wmin, rr * Wmin)
    B, H = rows / 2, c_wl / c_in
    best = None
    for N in range(4, 13, 2):
        gs = [le_g("nand", n1), 1.0, le_g("nand", 2)] + [1.0] * (N - 3)
        ps = [le_p("nand", n1), le_p("inv", 1), le_p("nand", 2)] + [le_p("inv", 1)] * (N - 3)
        d, _ = path_delay(gs, ps, B, H)
        if best is None or d < best[0]:
            best = (d, N)
    t_dec = best[0] * tau()
    rw = wire_r("met1", WIRES["met1"]["wmin"]) * cw
    t_wl = 0.38 * rw * c_wl
    c_bl = rows * (S["c_cell"] + wire_c("met2", WIRES["met2"]["wmin"]) * q["cell_h"])
    t_bl = S["t_bl0"] + c_bl * dv / S["i_read"]
    t_sa = sa_time(dv)
    M = max(1, cols // word)
    t_out = fo4_tp(rr) * (2 + 0.5 * math.log2(M))
    area = rows * cols * q["cell_w"] * q["cell_h"] + rows * q["cell_h"] * q["dec_w"] + cols * q["cell_w"] * q["col_h"]
    return {"dec": t_dec, "dec_N": best[1], "wl": t_wl, "bl": t_bl, "sa": t_sa, "out": t_out,
            "total": t_dec + t_wl + t_bl + t_sa + t_out, "area": area, "c_bl": c_bl, "c_wl": c_wl, "mux": M,
            "w_um": cw + q["dec_w"], "h_um": rows * q["cell_h"] + q["col_h"],
            "c_bl_dev": rows * S["c_cell"], "c_bl_wire": rows * wire_c("met2", WIRES["met2"]["wmin"]) * q["cell_h"]}


def reference():
    r = kn / kp
    pr = P["problems"]
    out = {"r": r,
           "idsat_n_per_um": idsat_n(1.0), "idsat_p_per_um": idsat_p(1.0)}
    # 1.1
    p = pr["p11"]
    w = wn_for_vol(p["Iload"], p["VOLmax"])
    out["p11"] = {"Wn": w, "WnL": w / L, "Ron": p["VOLmax"] / p["Iload"]}
    # 1.2
    out["p12"] = {}
    for key, ratio in (("ratio1", 1.0), ("ratio_r", r)):
        nm = noise_margins(Wmin, ratio * Wmin)
        nm["VM"] = vm(Wmin, ratio * Wmin)
        out["p12"][key] = nm
    # 1.3
    out["p13"] = {}
    for key, ratio in (("ratio1", 1.0), ("ratio_sqrt", math.sqrt(r)), ("ratio_r", r)):
        a, b = fo4(Wmin, ratio * Wmin)
        out["p13"][key] = {"ratio": ratio, "tphl": a, "tplh": b, "tp": (a + b) / 2,
                           "mismatch": (b - a) / ((a + b) / 2)}
    # 1.4
    CL = pr["p14"]["CL"]
    C1 = cin(Wmin, r * Wmin)
    t = {str(N): chain_delay(N, CL, r) for N in range(1, 11)}
    nbest = min(range(1, 11), key=lambda N: t[str(N)])
    nfew = next((N for N in range(1, 11) if t[str(N)] < pr["p14"]["tmax"]), 0)
    gamma = Cd / Cg
    out["p14"] = {"Cin": C1, "F": CL / C1, "Nopt4": math.log(CL / C1) / math.log(4), "t": t,
                  "gamma": gamma, "fopt": fopt(gamma), "Nbest": nbest, "Nfew": nfew}
    # 1.5
    q = pr["p15"]
    out["p15"] = {"P_VDD": dyn_power(q["N"], q["alpha"], q["Cgate"], VDD, q["f"]),
                  "P_low": dyn_power(q["N"], q["alpha"], q["Cgate"], q["Vlow"], q["f"]),
                  "Vlim": vdd_for_fo4(q["fo4max"], r), "fo4_low": fo4_tp(r, q["Vlow"])}
    out["r_lab"] = round(r * 20) / 20          # the symmetric ratio on the lab's 0.05-step slider
    # 第 2 章
    q23 = pr["p23"]
    gn = le_g("nand", q23["n_addr"])
    H23 = q23["Cout_units"] / q23["Cin_units"]
    out["ch2"] = {"tau": tau(), "g": {}, "p": {}, "dec": {}}
    for k, n in (("nand", 2), ("nand", 3), ("nor", 2), ("nor", 3)):
        out["ch2"]["g"][f"{k}{n}"] = le_g(k, n)
        out["ch2"]["p"][f"{k}{n}"] = le_p(k, n)
    for N in (2, 3, 4):
        gs = [gn] + [1.0] * (N - 1)
        ps = [le_p("nand", q23["n_addr"])] + [le_p("inv", 1)] * (N - 1)
        out["ch2"]["dec"][str(N)] = path_delay(gs, ps, q23["branch"], H23)[0]
    # 第 4 章
    out["ch4"] = {"r": {}, "c": {}, "cn": {}, "rep": {}}
    for l, q in WIRES.items():
        out["ch4"]["r"][l] = wire_r(l, q["wmin"])
        out["ch4"]["c"][l] = wire_c(l, q["wmin"])
        out["ch4"]["cn"][l] = wire_c(l, q["wmin"], q["smin"])
    q43 = pr["p43"]
    CL43 = q43["load_units"] * cin(Wmin, r * Wmin)
    for k in range(1, 6):
        out["ch4"]["rep"][str(k)] = repeater_delay(q43["L_um"], q43["layer"], q43["w_um"], k, 20, CL43)
    k_opt, s_opt = repeater_opt(q43["L_um"], q43["layer"], q43["w_um"])
    out["ch4"]["opt"] = {"k": k_opt, "size": s_opt}
    # 第 3 章
    q33 = pr["p33"]
    f33, fd = q33["f_MHz"] * 1e6, q33["rpm"] / 60 * q33["lines"] * 2
    out["ch3"] = {"ff": ff_timing(), "tcq_le": sum(ff_tcq_le()), "tau_m_est": tau_m_est(),
                  "setup": setup_slack(1 / f33, 1e-9, 50e-12), "hold": hold_slack(0.0, 150e-12),
                  "inc16": inc_delay(16), "xtalk": list(xtalk("met2", 0.14, 0.14, 500, 1, 100e-12)),
                  "sc": sc_ratio(2.0), "leak85": leak_inv(85), "leak_v": leak_inv(27, 1.2), "fo4s": fo4_scale(0.9),
                  "eop": list(energy_per_op(0.8, 1e4, 0.1, 5e-15, 30, 85)), "ron": sleep_ron(100),
                  "mtbf": {str(n): mtbf(sync_tr(n, f33, q33["slack_ps"] * 1e-12), f33, fd) for n in (1, 2)}}
    # 第 7 章
    out["ch7"] = {"snm_read": {str(c): sram_snm(c, 1, "read") for c in (1, 2, 3)},
                  "snm_hold": {str(c): sram_snm(c, 1, "hold") for c in (1, 2, 3)},
                  "write": {str(p_): sram_write_trip(2, p_) for p_ in (1, 2, 3)}, "access": {},
                  "sa": sa_time(0.07), "sim": sram_sim_snm(1.75)}
    for R in (64, 256, 1024):
        a = sram_access(R, 32768 // R, 32)
        out["ch7"]["access"][str(R)] = {k: a[k] for k in ("total", "dec", "bl", "area")}
    return out
