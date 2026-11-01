"""第 17 轮附三 6f：用 ngspice + SKY130（tt）测第 5 章的功耗参数。

被测器件都取参考尺寸：参考反相器 Wn = 0.42 μm、Wp = r·Wn（与第 1–3 章相同）。
1. 短路功耗：理想斜坡驱动被测反相器，被测反相器驱动 4 个参考反相器（FO4，负载另行供电）。输入上升、下降时间 tin 从 10 ps 扫到 600 ps。
   用器件的沟道电流区分：输出下降时 PMOS、输出上升时 NMOS 的沟道电荷是短路电荷（扣除 tin = 2 ps 时的残值），
   输出上升时 PMOS 的沟道电荷是给电容充电的电荷。结果记为 (tin/FO4, 短路能量/充电能量) 的表。
2. 漏电：参考反相器输入为 0、为 1 时电源的静态电流（取平均），温度 27、85、125 °C；二输入或非门（PMOS 各 2Wp）两个 PMOS 都关
   与只关一个时的漏电之比（叠层效应）。
3. 亚阈值摆幅 S：NMOS（Wn）VDS = 1.8 V，VGS 在 0.25–0.45 V 之间每变一个数量级的电压（mV/dec），27 °C 与 85 °C。
   DIBL：VDS = 0.05 V 与 1.8 V 时，电流等于 100 nA·W/L 的 VGS 之差除以 1.75 V（mV/V）。
4. 电压与速度、漏电：VDD = 0.4～1.8 V 时参考反相器的 FO4 延时（相对 1.8 V 的倍数）和平均漏电（相对 1.8 V 的倍数），27 °C。
结果写 calib/power.json，要点写进 params.json 的 power_sim；--check 只与仓库比较（镜像验收用，相差 > 15 % 报错，漏电放宽到 30 %）。
运行：SKY130_LIB=… 或 SKY130_INCLUDE=… python calib_power.py（约 1 分钟）
"""
import json
import math
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calib  # noqa: E402

OUT = Path(os.environ.get("CALIB_OUT", HERE))
PARAMS = HERE.parents[3] / "labs/micro/kit/models/params.json"
P = json.loads(PARAMS.read_text(encoding="utf-8"))
WN = P["Wmin"]
WP = round(P["kn"] / P["kp"] * WN, 3)
nmos, pmos = calib.nmos, calib.pmos


def inv(name, a, y, k=1.0):
    return nmos(name + "n", y, a, "0", round(k * WN, 3)) + pmos(name + "p", y, a, "vdd", round(k * WP, 3))


def num(out, key):
    m = re.search(rf"\b{key}\s*=\s*([-\d.e+]+)", out)
    return float(m.group(1)) if m else None


# ------------------------------------------------------------------ FO4 延时（相对比较用，同一仿真条件）
def fo4(vdd=1.8, temp=27):
    T = 8e-9 * max(1.0, (1.8 / vdd) ** 5)
    body = f".temp {temp}\nVdd vdd 0 {vdd}\nVin in 0 PULSE(0 {vdd} {T / 10} 20p 20p {T / 2} {T})\n"
    body += inv("S", "in", "a") + inv("D", "a", "y")
    for k in range(4):
        body += inv(f"L{k}", "y", f"z{k}") + inv(f"M{k}", f"z{k}", f"w{k}")
    h = vdd / 2
    ctl = (f"tran {T / 4000} {2 * T}\nmeas tran tf trig v(a) val={h} rise=1 targ v(y) val={h} fall=1\n"
           f"meas tran tr trig v(a) val={h} fall=1 targ v(y) val={h} rise=1")
    out, _ = calib.run(body, ctl)
    return (num(out, "tf") + num(out, "tr")) / 2


# ------------------------------------------------------------------ 1 短路功耗
def energy(tin, period=4e-9):
    """理想斜坡（上升、下降都为 tin）驱动被测反相器，FO4 负载（负载由另一个电源供电，不计入）。
    用器件的沟道电流（不含电容电流）分开两部分：输出下降时 PMOS 的沟道电流、输出上升时 NMOS 的沟道电流都是从电源直通到地的短路电流；
    输出上升时 PMOS 的沟道电荷是给电容充电的电荷。返回 (短路电荷, 充电电荷)（C）。"""
    body = "Vdd vdd 0 1.8\nVdd2 vdd2 0 1.8\n"
    body += f"Vin a 0 PULSE(0 1.8 {0.5e-9} {tin} {tin} {period / 2 - tin} {period})\n"
    body += nmos("Dn", "y", "a", "0", WN) + pmos("Dp", "y", "a", "vdd", WP)
    for k in range(4):
        body += nmos(f"L{k}n", f"z{k}", "y", "0", WN) + f"XL{k}p z{k} y vdd2 vdd2 {calib.PF} W={WP} L={calib.L} nf=1\n"
    ip, i_n = f"@m.xdp.m{calib.PF}[id]", f"@m.xdn.m{calib.NF}[id]"
    t0 = 0.5e-9 + period - 0.05e-9                     # 第二个周期：输入上升（输出下降）的半周期从 t0 开始
    ctl = (f"save {ip} {i_n}\ntran 0.5p {t0 + period + 0.1e-9}\nlet ip = {ip}\nlet inn = {i_n}\n"
           f"meas tran qpf integ ip from={t0} to={t0 + period / 2}\nmeas tran qpr integ ip from={t0 + period / 2} to={t0 + period}\n"
           f"meas tran qnr integ inn from={t0 + period / 2} to={t0 + period}")
    out, _ = calib.run(body, ctl)
    return num(out, "qpf") + num(out, "qnr"), num(out, "qpr")


# ------------------------------------------------------------------ 2 漏电
def leak_inv(temp=27, vdd=1.8, both=False):
    """参考反相器的静态电流：输入为 0（NMOS 关）与输入为 1（PMOS 关）。返回平均值，both=True 时返回两者。"""
    r = []
    for vin in (0, vdd):
        body = f".temp {temp}\nVdd vdd 0 {vdd}\nVin a 0 {vin}\n" + inv("D", "a", "y")
        out, _ = calib.run(body, "op\nlet il = -i(Vdd)\nprint il")
        r.append(num(out, "il"))
    return r if both else sum(r) / 2


def leak_nor(temp=27, both_off=True):
    """二输入或非门（PMOS 各 2·Wp 串联，NMOS 各 Wn）：输入都为 1 时两个 PMOS 都关；只有一个为 1 时只关一个（另一个输入为 0）。
    SKY130 的 PMOS 漏电远大于 NMOS，所以用或非门的 PMOS 叠层看叠层效应。"""
    wp = round(2 * WP, 3)
    va, vb = (1.8, 1.8) if both_off else (1.8, 0)
    body = f".temp {temp}\nVdd vdd 0 1.8\nVa a 0 {va}\nVb b 0 {vb}\n"
    body += pmos("P1", "y", "a", "m", wp) + pmos("P2", "m", "b", "vdd", wp)
    body += nmos("N1", "y", "a", "0", WN) + nmos("N2", "y", "b", "0", WN)
    out, _ = calib.run(body, "op\nlet il = -i(Vdd)\nprint il")
    return num(out, "il")


# ------------------------------------------------------------------ 3 亚阈值摆幅与 DIBL
def idvg(vds, temp=27):
    body = f".temp {temp}\nVd d 0 {vds}\nVg g 0 0\n" + nmos("N", "d", "g", "0", WN)
    out, _ = calib.run(body, "dc Vg 0 0.8 0.005\nprint -i(Vd)")
    pts = [(float(a), float(b)) for a, b in re.findall(r"^\d+\s+([-\d.e+]+)\s+([-\d.e+]+)", out, flags=re.M)]
    return pts


def swing(pts, v0=0.25, v1=0.45):
    a = min(pts, key=lambda p: abs(p[0] - v0)); b = min(pts, key=lambda p: abs(p[0] - v1))
    return (b[0] - a[0]) / math.log10(b[1] / a[1])


def vt_cc(pts, icrit):
    for (v0, i0), (v1, i1) in zip(pts, pts[1:]):
        if i0 < icrit <= i1:
            return v0 + (v1 - v0) * (math.log(icrit) - math.log(i0)) / (math.log(i1) - math.log(i0))
    return None


def main():
    res = {}
    f4 = fo4()
    res["fo4"] = f4
    # 1
    q0, qc = energy(2e-12)
    sc = []
    for tin in (10e-12, 25e-12, 50e-12, 100e-12, 150e-12, 200e-12, 300e-12, 400e-12, 600e-12):
        q, _ = energy(tin)
        sc.append((round(tin / f4, 3), round((q - q0) / qc, 4)))
    e0 = qc * 1.8
    res.update(E_cycle=e0, sc=sc)
    # 2
    res["leak"] = {}
    for T in (27, 85, 125):
        both, one = leak_nor(T, True), leak_nor(T, False)
        i0, i1 = leak_inv(T, both=True)
        res["leak"][str(T)] = {"inv": (i0 + i1) / 2, "in0": i0, "in1": i1, "stack2": both, "stack1": one}
    # 3
    lo, hi = idvg(0.05), idvg(1.8)
    hi85 = idvg(1.8, 85)
    icrit = 100e-9 * WN / calib.L
    res.update(S27=swing(hi) * 1e3, S85=swing(hi85) * 1e3, dibl=(vt_cc(lo, icrit) - vt_cc(hi, icrit)) / 1.75 * 1e3,
               vt_cc=vt_cc(hi, icrit))
    # 4
    vv = []
    l18 = leak_inv(27, 1.8)
    for v in (0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8):
        vv.append((v, round(fo4(v) / f4, 4), round(leak_inv(27, v) / l18, 4)))
    res["vdd"] = vv
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "power.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    keep = {"_note": "SKY130 功耗参数（samples/数字集成电路设计/生成脚本/calib/calib_power.py）：sc 为 [输入转换时间/FO4, 短路能量/电容充电能量]；"
                     "leak_inv 为参考反相器两种输入的平均漏电（A），leak_in0、leak_in1 分别为输入 0（NMOS 关）、输入 1（PMOS 关）；vt_cc 为 100 nA·W/L 定义的 NMOS 阈值（V）；stack 为二输入或非门两个 PMOS 都关与只关一个的漏电之比；"
                     "S 亚阈值摆幅（mV/dec）、dibl（mV/V）；vdd 为 [VDD, FO4 相对 1.8 V 的倍数, 漏电相对 1.8 V 的倍数]",
            "sc": sc, "S27": round(res["S27"], 1), "S85": round(res["S85"], 1), "dibl": round(res["dibl"], 1),
            "leak_inv": {T: float(f"{res['leak'][T]['inv']:.4g}") for T in res["leak"]},
            "leak_in0": {T: float(f"{res['leak'][T]['in0']:.4g}") for T in res["leak"]},
            "leak_in1": {T: float(f"{res['leak'][T]['in1']:.4g}") for T in res["leak"]},
            "vt_cc": round(res["vt_cc"], 3),
            "stack": {T: round(res["leak"][T]["stack2"] / res["leak"][T]["stack1"], 3) for T in res["leak"]},
            "vdd": vv}
    print(f"FO4 {f4 * 1e12:.1f} ps; E/cycle {e0 * 1e15:.1f} fJ")
    print("短路：", sc)
    print("漏电：", {T: {k: f"{v:.3g}" for k, v in d.items()} for T, d in res["leak"].items()})
    print(f"S {res['S27']:.1f}/{res['S85']:.1f} mV/dec; DIBL {res['dibl']:.1f} mV/V; VT(cc) {res['vt_cc']:.3f} V")
    print("电压：", vv)
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "--check" in sys.argv:
        old = params.get("power_sim", {})
        bad = []
        for k in ("S27", "S85", "dibl"):
            if abs(old.get(k, 0) - keep[k]) > 0.15 * abs(keep[k]):
                bad.append(f"{k}: {old.get(k)} → {keep[k]}")
        for T, v in keep["leak_inv"].items():
            o = old.get("leak_inv", {}).get(T, 0)
            if abs(o - v) > 0.3 * v:
                bad.append(f"leak_inv[{T}]: {o} → {v}")
        for (a, b), (c, e) in zip(old.get("sc", []), sc):
            if abs(b - e) > 0.15 * abs(e) + 0.01:
                bad.append(f"sc[{c}]: {b} → {e}")
        for (v, a, b), (_, c, e) in zip(old.get("vdd", []), vv):
            if abs(a - c) > 0.15 * c:
                bad.append(f"vdd[{v}]: {a} → {c}")
        print("功耗参数与仓库一致" if not bad else "功耗参数不一致：" + "；".join(bad))
        if bad:
            sys.exit(1)
    else:
        params["power_sim"] = keep
        PARAMS.write_text(json.dumps(params, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
