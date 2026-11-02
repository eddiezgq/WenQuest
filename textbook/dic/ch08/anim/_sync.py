"""把第 8 章动画用到的数值写进各动画文件的“数值”块（动画在服务器上渲染，只能 import manim、numpy、math，
不能读模型文件）。参数（labs/micro/kit/models/params.json）变化后运行：python3 textbook/dic/ch08/anim/_sync.py"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "conventions"))
sys.path.insert(0, str(HERE.parent / "code"))
import mos as M  # noqa: E402
import _pi  # noqa: E402

b = _pi.blocks("cheap")
ff = M.ff_timing()
VALUES = {"D_SUB": b["sub"][0] * 1e9, "D_MUL": b["mul"][0] * 1e9, "D_ADD": b["add1"][0] * 1e9, "D_SAT": b["sat"][0] * 1e9,
          "OH_NS": (ff["tcq"] + ff["tsu"]) * 1e9, "T_NS": 1e3 / M.P["problems"]["p81"]["f_MHz"]}


def block():
    lines = ["# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改"]
    lines += [f"{k} = {repr(float(v))}" for k, v in VALUES.items()]
    return "\n".join(lines + ["# </数值>"])


changed = []
for f in sorted(HERE.glob("a8_*.py")):
    s = f.read_text(encoding="utf-8")
    new = re.sub(r"# <数值>.*?# </数值>", block(), s, flags=re.S)
    if new != s:
        f.write_text(new, encoding="utf-8")
        changed.append(f.name)
print("已更新：" + "、".join(changed) if changed else "数值块已是最新")
