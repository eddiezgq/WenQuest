# -*- coding: utf-8 -*-
"""各机型共用的小工具（第 40 轮）：参数表整理、校核条目、结果条目。

每种机型（平缝 design.py、包缝 overlock.py、绷缝 cover.py）都给出同一套东西：
GROUPS / CHOICES / PARAMS / DEFAULTS / clean() / analyze() / adjust_card()；analyze() 的结果里都有
params、checks、ok、results（主要结果）、charts（曲线）、timing（时序条）、parts（零件尺寸）、card（调机顺序）、view（三维或动画页）。
网页、计算书、FreeCAD 只认这套字段，所以加机型不用改它们。
"""
import math


def make_params(groups, choices):
    params = {p[0]: p for g in groups for p in g[3]}
    defaults = {k: p[4] for k, p in params.items()}

    def clean(p):
        """外来参数整理成合法的一组：未知的键丢掉，数值夹到范围里，选项不在表里用默认。"""
        out = dict(defaults)
        for k, v in (p or {}).items():
            if k not in params:
                continue
            spec = params[k]
            if k in choices:
                if v in [c[0] for c in choices[k]]:
                    out[k] = v
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(v):
                continue
            out[k] = min(spec[6], max(spec[5], v))
        if "n" in out:
            out["n"] = round(out["n"])
        return out
    return params, defaults, clean


def bi(x):
    return dict(zh=x[0], en=x[1]) if isinstance(x, tuple) else dict(zh=x, en=x)


class Checks(list):
    def add(self, key, grp, zh, en, value, limit, state, lec, adv_zh="", adv_en=""):
        """value / limit：纯数字写一个字符串；带文字的写 (中文, English)"""
        self.append(dict(key=key, group=grp, name=dict(zh=zh, en=en), value=bi(value), limit=bi(limit), state=state, lecture=lec,
                         advice=dict(zh=adv_zh, en=adv_en)))


def result(zh, en, value, unit=""):
    return dict(zh=zh, en=en, value=value, unit=unit)


def line_chart(key, zh, en, phi, series, ref=None, zero=False, xr=None, xl=None):
    """series: [(中文, English, 颜色, y 列表)]。横轴缺省是主轴转角 0–360°；xr = [起, 止]、xl = (中文, English) 时是别的量（例如针号）"""
    d = dict(key=key, kind="line", zh=zh, en=en, x=list(phi),
             series=[dict(zh=a, en=b, color=c, y=[round(v, 4) for v in y]) for a, b, c, y in series], ref=ref, zero=zero)
    if xr:
        d["xr"] = [xr[0], xr[1]]
        d["xl"] = dict(zh=xl[0], en=xl[1]) if xl else dict(zh="", en="")
    return d


def xy_chart(key, zh, en, x, y, color="#2e9e6a", ref_zh="", ref_en=""):
    return dict(key=key, kind="xy", zh=zh, en=en, x=[round(v, 4) for v in x],
                series=[dict(zh="", en="", color=color, y=[round(v, 4) for v in y])], ref_zh=ref_zh, ref_en=ref_en)


def mod360(a):
    return ((a % 360) + 360) % 360
