"""把第 1 章动画用到的数值写进各动画文件的“数值”块（动画在服务器上渲染，只能 import manim、numpy、math，
不能读模型文件，所以数值要写在文件里）。参数（labs/micro/kit/models/params.json）变化后运行：
    python3 textbook/dic/ch01/anim/_sync.py
regen_ch1.sh 会自动运行它。"""
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "conventions"))
import mos as M  # noqa: E402

R = M.reference()
q = M.P["problems"]["p15"]
VALUES = {
    "VDD": M.VDD, "VT": M.VTn, "KN": M.kn, "KP": M.kp, "WMIN": M.Wmin, "LCH": M.L, "CG": M.Cg, "CD": M.Cd,
    "R_SYM": R["r"], "NB": R["p14"]["Nbest"], "GAMMA": R["p14"]["gamma"], "FOPT": R["p14"]["fopt"],
    "F_TOT": R["p14"]["F"], "NOPT4": R["p14"]["Nopt4"], "T1_NS": R["p14"]["t"]["1"] * 1e9,
    "TN_PS": R["p14"]["t"][str(R["p14"]["Nbest"])] * 1e12,
    "P_HI_MW": R["p15"]["P_VDD"] * 1e3, "P_LO_MW": R["p15"]["P_low"] * 1e3, "V_LOW": q["Vlow"],
    "N_GATES": q["N"], "ALPHA": q["alpha"], "C_GATE_FF": q["Cgate"] * 1e15, "F_MHZ": q["f"] / 1e6,
}


def block():
    lines = ["# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改"]
    for k, v in VALUES.items():
        lines.append(f"{k} = {int(v) if float(v).is_integer() and k in ('NB',) else repr(float(v))}")
    lines.append("# </数值>")
    return "\n".join(lines)


changed = []
for f in sorted(HERE.glob("a1_*.py")):
    s = f.read_text(encoding="utf-8")
    new = re.sub(r"# <数值>.*?# </数值>", block(), s, flags=re.S)
    if new != s:
        f.write_text(new, encoding="utf-8")
        changed.append(f.name)
print("updated:", ", ".join(changed) or "none")
