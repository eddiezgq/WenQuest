# -*- coding: utf-8 -*-
"""AI 助手的程序把关（第 49 轮）：AI 写的话里每个数，都要在这组设计的参数、结果、校核值里找得到。

网关（sewing_ai.py）和计算书（report.py）都用它：AI 起草的设计说明，找不到出处的数所在的句子删掉。
允许四舍五入：原数 941.3，句子写 941 或 941.3 都算找得到；写 942 不算。
"""
import re

_SEP = re.compile(r"(?<=\d)[,   ](?=\d{3}\b)")      # 6,000 / 6 000（千位分隔）
_NUM = re.compile(r"(?<![\d第–—~])-?\d+(?:\.\d+)?|(?<=[\d第–—~])\d+(?:\.\d+)?")   # “第 3-10 讲”里的 -10 不当负数


def numbers_in(text):
    """句子里的数（去掉千位分隔）。返回 [(数值, 小数位数), …]"""
    t = _SEP.sub("", str(text or ""))
    out = []
    for m in _NUM.finditer(t):
        s = m.group(0)
        out.append((float(s), len(s.split(".")[1]) if "." in s else 0))
    return out


def _collect(x, bag):
    if isinstance(x, bool) or x is None:
        return
    if isinstance(x, (int, float)):
        bag.add(float(x))
    elif isinstance(x, str):
        for v, _ in numbers_in(x):
            bag.add(v)
    elif isinstance(x, dict):
        for v in x.values():
            _collect(v, bag)
    elif isinstance(x, (list, tuple)):
        for v in x:
            _collect(v, bag)


def allowed_numbers(R, machine_name=""):
    """一次 analyze() 的结果里能引用的数：参数、主要结果、校核（数值、判据、讲次）、零件尺寸、试缝计数、各种计数。"""
    bag = set()
    _collect(R.get("params") or {}, bag)
    for r in R.get("results") or []:
        _collect(r.get("value"), bag)
    for c in R.get("checks") or []:
        _collect(c.get("value"), bag)
        _collect(c.get("limit"), bag)
        _collect(c.get("lecture"), bag)
    for p in R.get("parts") or []:
        for d in p.get("dims") or []:
            _collect(d[2], bag)
    if R.get("trial"):
        _collect(R["trial"].get("counts"), bag)
    checks = R.get("checks") or []
    bag.update({float(len(checks)), float(sum(c["state"] == "bad" for c in checks)),
                float(sum(c["state"] == "warn" for c in checks)), float(sum(c["state"] == "ok" for c in checks))})
    _collect(machine_name, bag)
    return bag


def found(v, dec, bag):
    if dec == 0 and abs(v) <= 3:                         # 0、1、2、3 这样的小整数要原样出现，不能靠四舍五入凑
        return any(abs(b - v) < 1e-9 for b in bag)
    for b in bag:
        if abs(b - v) < 1e-9 or abs(round(b, dec) - v) < 1e-9:
            return True
        if dec == 0 and abs(b) >= 1 and abs(b - v) < 1e-9 * max(1.0, abs(b)):
            return True
    return False


def verify(sentences, R, machine_name=""):
    """返回 (留下的句子, 删掉的句子及找不到的数)"""
    bag = allowed_numbers(R, machine_name)
    keep, drop = [], []
    for s in sentences or []:
        s = str(s).strip()
        if not s:
            continue
        miss = [v for v, dec in numbers_in(s) if not found(v, dec, bag)]
        if miss:
            drop.append({"sentence": s, "missing": [int(v) if v == int(v) else v for v in miss]})
        else:
            keep.append(s)
    return keep, drop
