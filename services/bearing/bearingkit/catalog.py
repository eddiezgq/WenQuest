"""Checking a maker's tapered roller bearing catalogue (round 64, plan section 十七).

A catalogue read into rows (one dict per printed row, values as printed) is checked by fixed rules. Every finding is
"suspected" or "please confirm": only the maker can say what the right value is. Nothing here changes a value.

Rules
1. dup     the same bearing printed twice: with the same data (please confirm, a repeat) or different data (suspected).
2. part    inch bearings are a cone (inner ring with rollers) and a cup (outer ring) with their own numbers: one cone
           number has one bore d and one cone width B, one cup number one outside diameter D and one cup width C.
3. shape   d < D; C < T; B and C at least half of T; metric series also B ≤ T; mounting dimensions (shaft
           shoulder da max, cone back face db min, housing shoulder Da min / Da max, cup back face Db min):
           d < da max, d < db min, da max < Da min ≤ Da max < D and Db min < D. (The inch tables have no mounting
           dimensions; inch cones are often wider than T, so B ≤ T is not a rule there.)
4. speed   the oil limiting speed is above the grease one.
5. outlier within a group (a metric series, the heavy truck series, the inch table): the static rating equal to the
           dynamic rating; the ratio C0r/Cr, the dynamic rating against the size (Cr against (D − d)·T, a power fit)
           and the mass against the ring volume π/4 (D² − d²) T, each more than a factor `spread` (1.5) from the
           group's typical value (median of the ratio, or of the fit residual). The inch table mixes many series, so
           its size trend uses the wider `spread_mixed` (2.5). In a metric series D also grows with d (not in a
           series the maker marks non-standard, row key "nonstandard").
6. inch    an inch dimension printed in mm is a whole number of 0.0001 in, rounded or cut off to the decimals printed;
           a value no such number gives (e.g. 28.576 where 1.1250 in = 28.575) is listed (please confirm: makers round
           differently). Whole and half millimetres are metric sizes some inch bearings have and are not checked.
7. std     the boundary dimensions against the national standard (GB/T 297): unknown until the standard's text is
           entered (bought, not copied from elsewhere).
Blank cells are listed (please confirm), never filled.

Plain code: no AI, no network. mm, kN, rpm, kg as printed.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from statistics import median

DIMS = ("d", "D", "T", "B", "C")
MOUNT = ("da_max", "db_min", "Da_min", "Da_max", "Db_min")
NUMERIC = DIMS + ("R", "r", "Cr", "Cor", "n_grease", "n_oil") + MOUNT + ("mass",)
LABEL = {
    "d": "d",
    "D": "D",
    "T": "T",
    "B": "B",
    "C": "C",
    "R": "R min",
    "r": "r min",
    "Cr": "Cr",
    "Cor": "C0r",
    "n_grease": "极限转速（脂）",
    "n_oil": "极限转速（油）",
    "da_max": "da max",
    "db_min": "db min",
    "Da_min": "Da min",
    "Da_max": "Da max",
    "Db_min": "Db min",
    "mass": "质量",
    "model": "型号",
    "cup": "外圈",
    "old": "旧型号",
}
SUSPECT, CONFIRM, UNKNOWN = "疑似", "请确认", "未知"


def num(v):
    """A printed value as a number: None for a blank, '(Sp*)' and the like; a trailing '*' is dropped."""
    if v is None:
        return None
    s = str(v).strip().rstrip("*")
    try:
        return float(s)
    except ValueError:
        return None


def key(r: dict) -> str:
    return f"{r['model']} / {r['cup']}" if r.get("cup") else str(r["model"])


def group(r: dict) -> str:
    if r["table"] == "inch":
        return "英制"
    m = re.fullmatch(r"(\d{3})\d\d", str(r["model"]))
    return (m.group(1) if m else str(r["model"])[:3]) + "00"


def standard(r: dict) -> bool:
    """A plain metric number (five digits) or any inch row: the rows a series trend is made of."""
    return r["table"] == "inch" or bool(re.fullmatch(r"\d{5}", str(r["model"])))


def finding(r, fields, rule, level, why):
    return {
        "page": r.get("page"),
        "model": key(r),
        "fields": [LABEL.get(f, f) for f in fields],
        "values": [r.get(f) for f in fields],
        "rule": rule,
        "level": level,
        "why": why,
    }


def inch_ok(raw) -> bool:
    """The printed mm value is some whole number of 0.0001 in, rounded or cut off to the decimals printed."""
    s = str(raw).strip().rstrip("*")
    v = float(s)
    dec = len(s.split(".")[1]) if "." in s else 0
    q = 10**dec
    for n in range(round(v / 2.54e-3) - 2, round(v / 2.54e-3) + 3):
        x = n * 2.54e-3 * q
        if any(abs(c / q - v) < 1e-9 * max(1, v) for c in (math.floor(x + 1e-9), math.floor(x + 0.5 + 1e-9))):
            return True
    return False


def check(rows: list[dict], spread: float = 1.5, spread_mixed: float = 2.5) -> list[dict]:
    out: list[dict] = []
    V = [{f: num(r.get(f)) for f in NUMERIC} for r in rows]

    # 1. the same bearing twice
    seen = defaultdict(list)
    repeats = defaultdict(list)
    for i, r in enumerate(rows):
        seen[(r["table"], key(r))].append(i)
    for (_t, _k), idx in seen.items():
        if len(idx) < 2:
            continue
        first = rows[idx[0]]
        for j in idx[1:]:
            diff = [f for f in NUMERIC if V[j][f] != V[idx[0]][f]]
            pages = f"第 {first.get('page')} 页与第 {rows[j].get('page')} 页"
            if diff:
                why = f"同一型号印了两行（{pages}），{', '.join(LABEL[f] for f in diff)} 不同：" + "；".join(
                    f"{LABEL[f]} {first.get(f)} / {rows[j].get(f)}" for f in diff
                )
                out.append(finding(rows[j], diff, "dup", SUSPECT, why))
            else:
                repeats[(first.get("page"), rows[j].get("page"))].append(key(rows[j]))
    for (p1, p2), models in repeats.items():
        where = f"第 {p1} 页" if p1 == p2 else f"第 {p1} 页与第 {p2} 页"
        out.append(
            {
                "page": p2,
                "model": "、".join(models),
                "fields": [],
                "values": [],
                "rule": "dup",
                "level": CONFIRM,
                "why": f"{len(models)} 个型号在{where}各印了一次，数据相同（版面重复？）",
            }
        )

    # 2. one cone number, one d and B; one cup number, one D and C
    for part, fields in (("model", ("d", "B")), ("cup", ("D", "C"))):
        by = defaultdict(list)
        for i, r in enumerate(rows):
            if r["table"] == "inch" and r.get(part):
                by[r[part]].append(i)
        for code, idx in by.items():
            for f in fields:
                vals = defaultdict(list)
                for i in idx:
                    if V[i][f] is not None:
                        vals[V[i][f]].append(i)
                if len(vals) < 2:
                    continue
                counts = sorted((len(ii) for ii in vals.values()), reverse=True)
                common = max(vals, key=lambda v: len(vals[v])) if counts[0] > counts[1] else None
                for v, ii in vals.items():
                    if v == common:  # the value most rows share stands; with a tie every row is listed
                        continue
                    for i in ii:
                        others = sorted({rows[k].get(f) for k in idx if V[k][f] != v and V[k][f] is not None})
                        what = "内圈" if part == "model" else "外圈"
                        out.append(
                            finding(
                                rows[i],
                                [f],
                                "part",
                                SUSPECT,
                                f"{what} {code} 在别的行里 {LABEL[f]} 是 {'、'.join(others)}，"
                                f"这一行是 {rows[i].get(f)}",
                            )
                        )

    # 3. shape
    for i, r in enumerate(rows):
        v = V[i]

        def lt(a, b, strict=True, v=v):
            x, y = v[a], v[b]
            return x is None or y is None or (x < y if strict else x <= y)

        for f in ("B", "C"):  # a ring narrower than half the total width: a misplaced decimal point or digit
            if v[f] is not None and v["T"] and v[f] < 0.5 * v["T"]:
                out.append(
                    finding(r, [f, "T"], "shape", SUSPECT, f"{LABEL[f]} = {r.get(f)} 不到总宽 T = {r.get('T')} 的一半")
                )
        pairs = [("d", "D", True), ("C", "T", True)]
        if r["table"] != "inch":
            pairs += [
                ("B", "T", False),
                ("d", "da_max", True),
                ("d", "db_min", True),
                ("da_max", "Da_min", True),
                ("Da_min", "Da_max", False),
                ("Da_max", "D", True),
                ("Db_min", "D", True),
            ]
        for a, b, strict in pairs:
            if not lt(a, b, strict):
                out.append(
                    finding(
                        r,
                        [a, b],
                        "shape",
                        SUSPECT,
                        f"{LABEL[a]} = {r.get(a)} 应{'小于' if strict else '不大于'} {LABEL[b]} = {r.get(b)}",
                    )
                )
        # 4. speed
        if v["n_grease"] is not None and v["n_oil"] is not None and not v["n_oil"] > v["n_grease"]:
            out.append(
                finding(
                    r,
                    ["n_grease", "n_oil"],
                    "speed",
                    SUSPECT,
                    f"油润滑极限转速 {r.get('n_oil')} 应高于脂润滑 {r.get('n_grease')}",
                )
            )
        # 6. inch
        if r["table"] == "inch" and not str(r["model"]).startswith("J"):
            for f in DIMS:
                if v[f] is not None and (v[f] * 2) % 1 and not inch_ok(r.get(f)):
                    n = round(v[f] / 2.54e-3) * 1e-4
                    out.append(
                        finding(
                            r,
                            [f],
                            "inch",
                            CONFIRM,
                            f"{LABEL[f]} = {r.get(f)} mm 不是英制尺寸换算来的数（最接近的 {n:.4f} in = "
                            f"{n * 25.4:.3f} mm）",
                        )
                    )
        # blanks
        blank = [
            f
            for f in NUMERIC
            if f in r and r.get(f) in (None, "") and not (r["table"] == "inch" and f in MOUNT + ("mass",))
        ]
        if blank:
            out.append(finding(r, blank, "blank", CONFIRM, f"空着：{', '.join(LABEL[f] for f in blank)}"))
        marked = [f for f in NUMERIC if r.get(f) not in (None, "") and num(r.get(f)) is None]
        if marked:
            out.append(
                finding(
                    r,
                    marked,
                    "blank",
                    CONFIRM,
                    "不是数：" + "；".join(f"{LABEL[f]} {r.get(f)}" for f in marked) + "（目录未说明含义）",
                )
            )
        stars = [f for f in NUMERIC if str(r.get(f) or "").strip().endswith("*") and num(r.get(f)) is not None]
        if stars:
            out.append(
                finding(
                    r,
                    stars,
                    "blank",
                    CONFIRM,
                    "带星号：" + "；".join(f"{LABEL[f]} {r.get(f)}" for f in stars) + "（目录未说明含义）",
                )
            )

    # 5. outliers within a group
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        groups[group(r)].append(i)
    for _g, idx in groups.items():
        for i in idx:
            if V[i]["Cr"] is not None and V[i]["Cr"] == V[i]["Cor"]:
                out.append(
                    finding(
                        rows[i], ["Cr", "Cor"], "outlier", CONFIRM, f"额定动载荷与静载荷完全相同（{rows[i].get('Cr')}）"
                    )
                )
        base = [i for i in idx if standard(rows[i])]
        out += _ratio(
            rows,
            V,
            base,
            idx,
            lambda v: v["Cor"] / v["Cr"] if v["Cr"] and v["Cor"] else None,
            ["Cr", "Cor"],
            "C0r/Cr",
            spread,
        )
        out += _fit(
            rows,
            V,
            base,
            idx,
            "Cr",
            lambda v: (v["D"] - v["d"]) * v["T"] if None not in (v["D"], v["d"], v["T"]) else None,
            "额定动载荷 Cr",
            "(D − d)·T",
            spread if rows[idx[0]]["table"] != "inch" else spread_mixed,
        )
        out += _ratio(
            rows,
            V,
            base,
            idx,
            lambda v: (
                v["mass"] / (math.pi / 4 * (v["D"] ** 2 - v["d"] ** 2) * v["T"] * 1e-6)
                if None not in (v["mass"], v["D"], v["d"], v["T"]) and v["D"] > v["d"]
                else None
            ),
            ["mass"],
            "质量 / 外形体积（kg/dm³）",
            spread,
        )
        if rows[idx[0]]["table"] != "inch" and not rows[idx[0]].get("nonstandard"):
            std = sorted((i for i in base), key=lambda i: V[i]["d"] or 0)
            for a, b in zip(std, std[1:], strict=False):
                if (
                    None not in (V[a]["D"], V[b]["D"], V[a]["d"], V[b]["d"])
                    and V[b]["d"] > V[a]["d"]
                    and not V[b]["D"] > V[a]["D"]
                ):
                    out.append(
                        finding(
                            rows[b],
                            ["d", "D"],
                            "outlier",
                            SUSPECT,
                            f"同一系列内径更大（{rows[a]['model']} d {rows[a].get('d')} → {rows[b]['model']} d "
                            f"{rows[b].get('d')}），外径却没有变大（D {rows[a].get('D')} → {rows[b].get('D')}）",
                        )
                    )

    # 7. the standard
    if any(r["table"] != "inch" for r in rows):
        out.append(
            {
                "page": None,
                "model": "全部公制型号",
                "fields": ["d", "D", "T", "B", "C"],
                "values": [],
                "rule": "std",
                "level": UNKNOWN,
                "why": "与国标外形尺寸（GB/T 297）对比：标准正文录入前为“未知”",
            }
        )
    return out


def _ratio(rows, V, base, idx, f, fields, name, spread):
    vals = {i: f(V[i]) for i in idx}
    ref = [vals[i] for i in base if vals[i]]
    if len(ref) < 5:
        return []
    m = median(ref)
    out = []
    for i in idx:
        x = vals[i]
        if x and not (m / spread <= x <= m * spread):
            out.append(
                finding(
                    rows[i],
                    fields,
                    "outlier",
                    SUSPECT,
                    f"{name} = {x:.3g}，同组典型值 {m:.3g}，相差 {max(x / m, m / x):.2f} 倍",
                )
            )
    return out


def _fit(rows, V, base, idx, field, size, name, sname, spread):
    """log y = a + b log size over the group's plain numbers; a point off the line by more than `spread`."""
    pts = [(math.log(size(V[i])), math.log(V[i][field])) for i in base if V[i][field] and size(V[i]) and size(V[i]) > 0]
    for _ in range(3):  # refit without the points far off the line, so a gross error does not bend the trend
        if len(pts) < 5:
            return []
        n = len(pts)
        mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
        sxx = sum((p[0] - mx) ** 2 for p in pts)
        if sxx == 0:
            return []
        b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
        c = median(p[1] - (my + b * (p[0] - mx)) for p in pts)
        keep = [p for p in pts if abs(p[1] - (my + b * (p[0] - mx)) - c) <= math.log(spread)]
        if len(keep) == len(pts):
            break
        pts = keep
    out = []
    for i in idx:
        s, y = size(V[i]), V[i][field]
        if not (s and y and s > 0):
            continue
        e = math.log(y) - (my + b * (math.log(s) - mx)) - c
        if abs(e) > math.log(spread):
            out.append(
                finding(
                    rows[i],
                    [field],
                    "outlier",
                    SUSPECT,
                    f"{name} = {rows[i].get(field)}，按同组 {name} 与 {sname} 的趋势应在 "
                    f"{y / math.exp(e):.3g} 左右，相差 {math.exp(abs(e)):.2f} 倍",
                )
            )
    return out


# ---- the catalogue as an Excel workbook (plan section 十七 K3): one sheet per table, the first row the headers ----
# The company keeps its catalogue in this form (the template, or the checked table it was given) and loads it into its
# own cloud space; nothing of it is in the code.
SHEETS = {
    "公制圆锥": (
        "metric",
        {
            "页码": "page",
            "系列": "series",
            "新型号": "model",
            "旧型号": "old",
            "d": "d",
            "D": "D",
            "T": "T",
            "B": "B",
            "C": "C",
            "R min": "R",
            "r min": "r",
            "Cr (kN)": "Cr",
            "C0r (kN)": "Cor",
            "极限转速 脂": "n_grease",
            "极限转速 油": "n_oil",
            "da max": "da_max",
            "db min": "db_min",
            "Da min": "Da_min",
            "Da max": "Da_max",
            "Db min": "Db_min",
            "质量 (kg)": "mass",
        },
    ),
    "英制圆锥": (
        "inch",
        {
            "页码": "page",
            "内圈": "model",
            "外圈": "cup",
            "d": "d",
            "D": "D",
            "T": "T",
            "B": "B",
            "C": "C",
            "R min": "R",
            "r min": "r",
            "Cr (kN)": "Cr",
            "C0r (kN)": "Cor",
            "极限转速 脂": "n_grease",
            "极限转速 油": "n_oil",
        },
    ),
    "双列圆锥": (
        "double",
        {
            "页码": "page",
            "型号": "model",
            "d": "d",
            "D": "D",
            "T": "T",
            "Cr (kN)": "Cr",
            "C0r (kN)": "Cor",
            "轴向游隙 (mm)": "axial_clearance",
        },
    ),
    "NU短圆柱": ("nu", {"页码": "page", "型号": "model", "d": "d", "D": "D", "B": "B"}),
}
# which design type a table's rows open as (the others are listed for reference: not a type the software computes yet)
OPENS_AS = {"metric": "tapered", "inch": "tapered", "nu": "cylindrical"}
MAX_ROWS = 5000


class CatalogError(ValueError):
    pass


def _cell(v):
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    return s or None


def read_xlsx(data: bytes) -> list[dict]:
    """The rows of a catalogue workbook, values kept as written (text). Sheets and columns not known are skipped; a
    known sheet must have a model column."""
    import io

    from openpyxl import load_workbook

    try:
        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception as e:  # noqa: BLE001  (any unreadable file)
        raise CatalogError("not an Excel workbook (.xlsx)") from e
    rows: list[dict] = []
    found = False
    for ws in wb.worksheets:
        if ws.title not in SHEETS:
            continue
        found = True
        table, cols = SHEETS[ws.title]
        it = ws.iter_rows(values_only=True)
        head = [_cell(h) for h in next(it, ())]
        keys = [cols.get(h) if h else None for h in head]
        if "model" not in keys:
            raise CatalogError(f"sheet {ws.title}: no model column")
        for vals in it:
            r = {k: _cell(v) for k, v in zip(keys, vals, strict=False) if k}
            if not r.get("model"):
                continue
            r["table"] = table
            if r.get("series") == "重卡非标":
                r["nonstandard"] = True
            rows.append(r)
            if len(rows) > MAX_ROWS:
                raise CatalogError(f"at most {MAX_ROWS} rows")
    if not found:
        raise CatalogError("no sheet named " + " / ".join(SHEETS))
    return rows


def template_xlsx() -> bytes:
    """An empty workbook with the sheets and headers read_xlsx knows."""
    import io

    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    wb.remove(wb.active)
    for name, (_t, cols) in SHEETS.items():
        ws = wb.create_sheet(name)
        ws.append(list(cols))
        for c in ws[1]:
            c.font = Font(bold=True)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
