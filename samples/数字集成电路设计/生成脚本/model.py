"""数字集成电路设计 第 1 章（CMOS 反相器）参考计算。

与浏览器实验的 JS 模型（labs/micro/kit/models/mos.js）共用同一份参数
labs/micro/kit/models/params.json，算法一一对应（第 17 轮 RM2）。
运行：python model.py        → 打印并写出 ref.json
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
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
    out["p14"] = {"Cin": C1, "F": CL / C1, "Nopt4": math.log(CL / C1) / math.log(4),
                  "t": {str(N): chain_delay(N, CL, r) for N in range(1, 9)}}
    # 1.5
    q = pr["p15"]
    out["p15"] = {"P_VDD": dyn_power(q["N"], q["alpha"], q["Cgate"], VDD, q["f"]),
                  "P_low": dyn_power(q["N"], q["alpha"], q["Cgate"], q["Vlow"], q["f"])}
    return out


if __name__ == "__main__":
    ref = reference()
    Path(__file__).with_name("ref.json").write_text(json.dumps(ref, indent=2, ensure_ascii=False), encoding="utf-8")
    p = ref
    print(f"饱和电流 n {p['idsat_n_per_um']*1e6:.0f} μA/μm, p {p['idsat_p_per_um']*1e6:.0f} μA/μm, r = {p['r']:.2f}")
    print(f"1.1 Wn = {p['p11']['Wn']:.2f} μm (W/L = {p['p11']['WnL']:.1f})")
    for k, v in p["p12"].items():
        print(f"1.2 {k}: VM={v['VM']:.3f} VIL={v['VIL']:.3f} VIH={v['VIH']:.3f} NML={v['NML']:.3f} NMH={v['NMH']:.3f}")
    for k, v in p["p13"].items():
        print(f"1.3 {k}: Wp/Wn={v['ratio']:.2f} tPHL={v['tphl']*1e12:.1f} tPLH={v['tplh']*1e12:.1f} tp={v['tp']*1e12:.1f} ps 差 {v['mismatch']*100:.0f}%")
    q = p["p14"]
    print(f"1.4 Cin={q['Cin']*1e15:.2f} fF F={q['F']:.0f} lnF/ln4={q['Nopt4']:.2f}; " +
          ", ".join(f"N={n}:{t*1e9:.3f}ns" for n, t in q["t"].items()))
    print(f"1.5 P(1.8V)={p['p15']['P_VDD']*1e3:.2f} mW, P(1.2V)={p['p15']['P_low']*1e3:.2f} mW")
