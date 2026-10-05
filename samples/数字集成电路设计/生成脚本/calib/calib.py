"""第 17 轮附 3.4：用 ngspice + SKY130（tt，27 °C）校准第 1 章的有效参数。

测量（W = 0.42 μm、L = 0.15 μm 的 sky130_fd_pr__nfet_01v8 / pfet_01v8）：
  1. 饱和电流 IDSAT（|VGS| = |VDS| = 1.8 V），换算为 μA/μm；
  2. 阈值电压 VT：线性区（|VDS| = 50 mV）最大跨导外推；
  3. 反相器传输特性（Wp/Wn = 1、1.5、2.25、3）：VM、VIL、VIH、NML、NMH；
  4. 反相器延时：前级反相器整形输入，被测反相器驱动 n 个相同反相器（n = 1、2、4、8），
     tPHL、tPLH 取 50% 点；对 n 线性拟合，截距/斜率 = 自载与输入电容之比 γ；
  5. 输入电容：理想斜坡驱动反相器输入，积分输入电流得 Cin = Q / VDD。
拟合（与 labs/micro/kit/models 的长沟道模型一致）：
  VT 取“有效值”：在 0.40–0.80 V 间扫描，使四个尺寸比的 VM、NML、NMH 与仿真最接近（短沟道器件用平方律时，
  外推得到的 VT 会让噪声容限偏大约 20%；有效 VT 只影响传输特性，不影响延时）；外推值另行记录；
  k′ = 2·IDSAT·L / [W·(VDD − VT)²]（保证饱和电流与仿真一致）；Cg = Cin /(Wn + Wp)，Cd = γ·Cg；
  再按 FO4 延时的比值修正 Cg、Cd（同一比例），使 Wp/Wn = 2.25 时模型 FO4 与仿真一致。
输出 calib/result.json 与 calib/params.sky130.json（可直接替换 params.json 的器件部分）。

模型来源：环境变量 SKY130_LIB（如 $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice，用 .lib … tt），
或 SKY130_INCLUDE（一个可直接 .include 的模型文件）。运行：python calib.py
"""
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("CALIB_OUT", HERE))          # CI 在镜像里运行时写到别处（仓库只读挂载）
ROOT = HERE.parents[3]
PARAMS = json.loads((ROOT / "labs/micro/kit/models/params.json").read_text(encoding="utf-8"))
VDD, L, WMIN = 1.8, 0.15, 0.42
NF, PF = "sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"


def models() -> str:
    lib, inc = os.environ.get("SKY130_LIB"), os.environ.get("SKY130_INCLUDE")
    if lib:
        return f".param mc_mm_switch=0\n.param mc_pr_switch=0\n.lib {lib} tt\n"
    if inc:
        return f".include {inc}\n"
    sys.exit("set SKY130_LIB or SKY130_INCLUDE")


def run(body: str, control: str) -> str:
    with tempfile.TemporaryDirectory() as d:
        Path(d, ".spiceinit").write_text("set ngbehavior=hsa\nset skywaterpdk\nset ng_nomodcheck\n")
        Path(d, "c.sp").write_text(f"* WenQuest calibration\n{models()}{body}\n.control\n{control}\n.endc\n.end\n")
        p = subprocess.run(["ngspice", "-b", "c.sp"], cwd=d, capture_output=True, text=True, timeout=600)
        out = p.stdout + p.stderr
        if p.returncode != 0 or "rror" in out and "fatal" in out.lower():
            raise RuntimeError(out[-3000:])
        files = {f.name: f.read_text() for f in Path(d).glob("*.dat")}
        return out, files


def table(text: str) -> list[list[float]]:
    rows = []
    for ln in text.splitlines():
        try:
            rows.append([float(x) for x in ln.split()])
        except ValueError:
            pass
    return rows


def nmos(name, d, g, s, w): return f"X{name} {d} {g} {s} 0 {NF} W={w} L={L} nf=1\n"
def pmos(name, d, g, s, w): return f"X{name} {d} {g} {s} vdd {PF} W={w} L={L} nf=1\n"
def inv(name, a, y, wn, wp): return nmos(name + "n", y, a, "0", wn) + pmos(name + "p", y, a, "vdd", wp)


# ------------------------------------------------------------------ 1–2 IDSAT, VT
def device():
    w = WMIN
    body = ("Vdd vdd 0 1.8\nVdn dn 0 1.8\nVgn gn 0 1.8\n" + nmos("N", "dn", "gn", "0", w) +
            "Vdp dp 0 0\nVgp gp 0 0\n" + pmos("P", "dp", "gp", "vdd", w))
    out, _ = run(body, "op\nprint -i(Vdn) i(Vdd)")
    idn = float(re.search(r"-i\(vdn\) = ([-\d.e+]+)", out).group(1))
    # PMOS current: the supply also feeds nothing else, i(Vdd) is negative of current out of supply
    idp = -float(re.search(r"i\(vdd\) = ([-\d.e+]+)", out).group(1))
    # VT by max-gm extrapolation at |VDS| = 50 mV
    vt = {}
    for kind in ("n", "p"):
        if kind == "n":
            body = "Vd d 0 0.05\nVg g 0 0\n" + nmos("N", "d", "g", "0", w)
            ctl = "dc Vg 0 1.8 0.005\nwrdata id.dat -i(Vd)"
        else:
            body = "Vdd vdd 0 1.8\nVd d 0 1.75\nVg g 0 1.8\n" + pmos("P", "d", "g", "vdd", w)
            ctl = "dc Vg 1.8 0 -0.005\nwrdata id.dat i(Vd)"
        _, f = run(body, ctl)
        rows = table(f["id.dat"])
        vg = [r[0] for r in rows]; i = [abs(r[1]) for r in rows]
        vgs = [v if kind == "n" else 1.8 - v for v in vg]
        gm = [(i[k + 1] - i[k - 1]) / (vgs[k + 1] - vgs[k - 1]) for k in range(1, len(i) - 1)]
        k = max(range(len(gm)), key=lambda j: gm[j]) + 1
        vt[kind] = vgs[k] - i[k] / gm[k - 1] - 0.05 / 2
    return {"idsat_n": idn, "idsat_p": idp, "idsat_n_per_um": idn / w, "idsat_p_per_um": idp / w, "vtn": vt["n"], "vtp": vt["p"]}


# ------------------------------------------------------------------ 3 VTC
def vtc(ratio):
    body = "Vdd vdd 0 1.8\nVin a 0 0\n" + inv("I", "a", "y", WMIN, round(WMIN * ratio, 4))
    _, f = run(body, "dc Vin 0 1.8 0.001\nwrdata vtc.dat v(y)")
    rows = table(f["vtc.dat"])
    vs = [r[0] for r in rows]; vo = [r[1] for r in rows]
    vm = next(vs[k - 1] + (vs[k] - vs[k - 1]) * (vo[k - 1] - vs[k - 1]) / ((vo[k - 1] - vs[k - 1]) - (vo[k] - vs[k]))
              for k in range(1, len(vs)) if (vo[k - 1] - vs[k - 1]) * (vo[k] - vs[k]) <= 0)
    g = [(vo[k + 1] - vo[k - 1]) / (vs[k + 1] - vs[k - 1]) for k in range(1, len(vs) - 1)]
    idx = [k + 1 for k, s in enumerate(g) if s < -1]
    vil, vih = vs[idx[0]], vs[idx[-1]]
    voh, vol = vo[idx[0]], vo[idx[-1]]
    return {"ratio": ratio, "VM": vm, "VIL": vil, "VIH": vih, "NML": vil - vol, "NMH": voh - vih}


# ------------------------------------------------------------------ 4 delay vs fan-out
def delay(ratio, fanout):
    wn, wp = WMIN, round(WMIN * ratio, 4)
    body = "Vdd vdd 0 1.8\nVin in 0 PULSE(0 1.8 100p 20p 20p 1n 2n)\n"
    body += inv("S", "in", "a", wn, wp)                         # shaping stage: realistic input edge
    body += inv("D", "a", "y", wn, wp)                          # device under test
    for k in range(fanout):
        body += inv(f"L{k}", "y", f"z{k}", wn, wp)              # n identical loads
        body += inv(f"M{k}", f"z{k}", f"w{k}", wn, wp)          # each load sees one inverter (keeps its edge real)
    ctl = ("tran 1p 4n\n"
           "meas tran tphl trig v(a) val=0.9 rise=2 targ v(y) val=0.9 fall=2\n"
           "meas tran tplh trig v(a) val=0.9 fall=2 targ v(y) val=0.9 rise=2")
    out, _ = run(body, ctl)
    tphl = float(re.search(r"tphl\s*=\s*([-\d.e+]+)", out).group(1))
    tplh = float(re.search(r"tplh\s*=\s*([-\d.e+]+)", out).group(1))
    return tphl, tplh


# ------------------------------------------------------------------ 5 input capacitance
def cin(ratio):
    wn, wp = WMIN, round(WMIN * ratio, 4)
    body = "Vdd vdd 0 1.8\nVin in 0 PULSE(0 1.8 100p 200p 200p 1n 2n)\n" + inv("D", "in", "y", wn, wp)
    body += inv("L", "y", "z", wn, wp)
    out, _ = run(body, "tran 0.5p 1.5n\nmeas tran q integ i(Vin) from=90p to=400p")
    q = abs(float(re.search(r"q\s*=\s*([-\d.e+]+)", out).group(1)))
    return q / VDD


def effective_vt(res):
    """Effective VTn, VTp (square law) that best reproduce VM, NML, NMH of the simulated transfer curves."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("wqmodel", HERE.parents[3] / "textbook" / "dic" / "conventions" / "mos.py")   # 一个独立副本：拟合时要改它的参数
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    d = res["device"]
    best = None
    for vtn in [x / 100 for x in range(40, 81, 1)]:
        for dv in (0.0,):                      # |VTn| = |VTp|：第 1 章用“两管等强时 VM = VDD/2”的教学结论
            vtp = vtn + dv
            M.VTn, M.VTp = vtn, vtp
            M.kn = 2 * d["idsat_n"] * L / (WMIN * (VDD - vtn) ** 2)
            M.kp = 2 * d["idsat_p"] * L / (WMIN * (VDD - vtp) ** 2)
            err = 0.0
            for v in res["vtc"]:
                nm = M.noise_margins(WMIN, v["ratio"] * WMIN, step=0.002)
                for m, s in ((M.vm(WMIN, v["ratio"] * WMIN), v["VM"]), (nm["NML"], v["NML"]), (nm["NMH"], v["NMH"])):
                    err += ((m - s) / s) ** 2
            if best is None or err < best[0]:
                best = (err, vtn, vtp)
    return best[1], best[2]


def main():
    if "--fit-only" in sys.argv and (OUT / "result.json").exists():
        res = json.loads((OUT / "result.json").read_text(encoding="utf-8"))
        res.pop("fit", None)
    else:
        res = {"device": device()}
        res["vtc"] = [vtc(r) for r in (1.0, 1.5, 2.25, 3.0)]
        res["delay"] = {}
        for ratio in (1.0, 1.5, 2.25):
            res["delay"][str(ratio)] = {str(n): delay(ratio, n) for n in (1, 2, 4, 8)}
        res["cin"] = {str(r): cin(r) for r in (1.0, 2.25)}
    d = res["device"]

    # ---- fit
    vtn, vtp = effective_vt(res)
    kn = 2 * d["idsat_n"] * L / (WMIN * (VDD - vtn) ** 2)
    kp = 2 * d["idsat_p"] * L / (WMIN * (VDD - vtp) ** 2)
    r_ = 2.25
    tp = {n: sum(res["delay"]["2.25"][str(n)]) / 2 for n in (1, 2, 4, 8)}
    ns = [1, 2, 4, 8]; mx = sum(ns) / 4; my = sum(tp[n] for n in ns) / 4
    slope = sum((n - mx) * (tp[n] - my) for n in ns) / sum((n - mx) ** 2 for n in ns)
    inter = my - slope * mx
    gamma = inter / slope
    cg = res["cin"]["2.25"] / (WMIN * (1 + r_))
    # long-channel delay for the fitted k', VT, Cg, γ; then scale C so FO4 at Wp/Wn = 2.25 matches the simulation
    def model_fo4(Cg, Cd, ratio=2.25):
        wn, wp = WMIN, WMIN * ratio
        req_n = 0.75 * VDD / (kn / 2 * wn / L * (VDD - vtn) ** 2)
        req_p = 0.75 * VDD / (kp / 2 * wp / L * (VDD - vtp) ** 2)
        c = (wn + wp) * Cd + 4 * (wn + wp) * Cg
        return 0.69 * req_n * c, 0.69 * req_p * c
    a, b = model_fo4(cg, gamma * cg)
    scale = tp[4] / ((a + b) / 2)
    cg_eff, cd_eff = cg * scale, gamma * cg * scale
    fit = {"VTn": round(vtn, 3), "VTp": round(vtp, 3), "kn": float(f"{kn:.3g}"), "kp": float(f"{kp:.3g}"),
           "Cg": float(f"{cg_eff:.3g}"), "Cd": float(f"{cd_eff:.3g}")}
    res["fit"] = {**fit, "vt_extracted": [d["vtn"], abs(d["vtp"])], "gamma": gamma, "cg_from_charge": cg, "delay_scale": scale,
                  "fo4_sim_ps": {k: [x * 1e12 for x in res["delay"][k]["4"]] for k in res["delay"]}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    newp = dict(PARAMS)
    newp.update(fit)
    newp["_note"] = ("SKY130 tt 27 °C 校准值（第 17 轮附 3.4，samples/数字集成电路设计/生成脚本/calib/calib.py）："
                     "VT 为使传输特性最接近仿真的有效值（线性区外推值见 calib/result.json），k′ 由 IDSAT 反推，Cg、Cd 由输入电容与扇出拟合后按 FO4 延时修正")
    (OUT / "params.sky130.json").write_text(json.dumps(newp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"IDSAT n {d['idsat_n_per_um']*1e6:.0f} μA/μm, p {d['idsat_p_per_um']*1e6:.0f} μA/μm; VT extracted {d['vtn']:.3f}/{abs(d['vtp']):.3f} V, effective {vtn:.2f}/{vtp:.2f} V")
    print(f"k'n {kn*1e6:.1f} μA/V², k'p {kp*1e6:.1f} μA/V², r = {kn/kp:.2f}")
    for v in res["vtc"]:
        print(f"VTC Wp/Wn={v['ratio']}: VM {v['VM']:.3f}  NML {v['NML']:.3f}  NMH {v['NMH']:.3f}")
    for k, v in res["delay"].items():
        print(f"delay Wp/Wn={k}: " + "  ".join(f"FO{n} {a*1e12:.1f}/{b*1e12:.1f}" for n, (a, b) in v.items()))
    print(f"gamma {gamma:.2f}; Cin(2.25) {res['cin']['2.25']*1e15:.2f} fF → Cg {cg*1e15:.2f} fF/μm; delay scale {scale:.2f} → Cg_eff {cg_eff*1e15:.2f}, Cd_eff {cd_eff*1e15:.2f} fF/μm")


if __name__ == "__main__":
    main()
