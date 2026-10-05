"""把第 2 章动画用到的数值写进各动画文件的“数值”块（动画在服务器上渲染，只能 import manim、numpy、math，
不能读模型文件）。参数（labs/micro/kit/models/params.json）变化后运行：python3 textbook/dic/ch02/anim/_sync.py"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "conventions"))
import mos as M  # noqa: E402

r = M.r_ratio()
q = M.P["problems"]["p23"]
gn = M.le_g("nand", q["n_addr"])
VALUES = {
    "R_SYM": r, "GAMMA": M.gamma_self(), "TAU_PS": M.tau() * 1e12,
    "R_N_K": M.req_n(M.Wmin) / 1e3, "C_FO4_FF": (4 * M.cin(M.Wmin, r * M.Wmin) + (1 + r) * M.Wmin * M.Cd) * 1e15,
    "CINV_FF": M.cin(M.Wmin, r * M.Wmin) * 1e15,
    "G_NAND3": gn, "P_NAND3": M.le_p("nand", q["n_addr"]), "B_DEC": q["branch"], "H_DEC": q["Cout_units"] / q["Cin_units"],
}


def block():
    lines = ["# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改"]
    lines += [f"{k} = {repr(float(v))}" for k, v in VALUES.items()]
    return "\n".join(lines + ["# </数值>"])


changed = []
for f in sorted(HERE.glob("a2_*.py")):
    s = f.read_text(encoding="utf-8")
    new = re.sub(r"# <数值>.*?# </数值>", block(), s, flags=re.S)
    if new != s:
        f.write_text(new, encoding="utf-8")
        changed.append(f.name)
print("已更新：" + "、".join(changed) if changed else "数值块已是最新")
