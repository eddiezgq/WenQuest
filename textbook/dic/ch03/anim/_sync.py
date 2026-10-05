"""把第 3 章动画用到的数值写进各动画文件的“数值”块（动画在服务器上渲染，只能 import manim、numpy、math，
不能读模型文件）。参数（labs/micro/kit/models/params.json）变化后运行：python3 textbook/dic/ch03/anim/_sync.py"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "conventions"))
import mos as M  # noqa: E402

r = M.r_ratio()
ff = M.ff_timing()
VALUES = {"VDD": M.VDD, "VM": M.vm(M.Wmin, r * M.Wmin), "TAU_M_PS": ff["tau_m"] * 1e12, "T0_PS": ff["T0"] * 1e12,
          "TAU_EST_PS": M.tau_m_est() * 1e12}


def block():
    lines = ["# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改"]
    lines += [f"{k} = {repr(float(v))}" for k, v in VALUES.items()]
    return "\n".join(lines + ["# </数值>"])


changed = []
for f in sorted(HERE.glob("a3_*.py")):
    s = f.read_text(encoding="utf-8")
    new = re.sub(r"# <数值>.*?# </数值>", block(), s, flags=re.S)
    if new != s:
        f.write_text(new, encoding="utf-8")
        changed.append(f.name)
print("已更新：" + "、".join(changed) if changed else "数值块已是最新")
