"""数字集成电路设计 第 1 章（CMOS 反相器）参考计算。

模型本身在教材里：textbook/dic/conventions/mos.py（书中程序、本目录的生成脚本、浏览器实验共用同一份参数）。
本文件保留原来的接口（import model as M），并在直接运行时写出 ref.json。
运行：python model.py        → 打印并写出 ref.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "textbook" / "dic" / "conventions"))
from mos import *  # noqa: E402,F401,F403
from mos import P, reference  # noqa: E402,F401

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
