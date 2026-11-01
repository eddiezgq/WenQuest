# -*- coding: utf-8 -*-
"""横机意匠图（第 70 轮）：读文件、编译成逐趟的机头动作。

意匠图（教材 17.6 节）：每格是一枚针在一个意匠行里的动作。符号和虚拟实验 17-2“横机操作与制版”同一套：
  K 前编、P 后编、T 集圈、> 右移（绞花 / 放针）、< 左移（绞花 / 收针）、. 不织；符号后面可跟颜色（纱嘴）号 1–6，不写就是 1。
两种文件：
  文字表（CSV / TXT）：一行一个意匠行，**第一行先织（起口）**；格子之间用逗号、分号、制表符或空格分开，也可以一个字符一格（只用一种颜色时）。
  提花色码图（PNG）：一个像素 = 一枚针 × 一个意匠行，**最下面一行先织**（和织物的样子一样）；每种颜色一个纱嘴，全部前编；
  透明像素 = 不织。最多 6 种颜色。
编译（compile）照搬虚拟实验 17-2 的编译器：每个意匠行先插翻针横列（前 → 后、摇床、后 → 前），再按颜色分编织横列；
纱嘴只能从它上次停的那一端出发，方向不对就插空行；查“空针翻针”“摇床超过 ±4 针”“移到针床外”。
"""
import base64
import binascii
import io
import re

MAX_NEEDLES = 1200
MAX_ROWS = 4000
MAX_CELLS = 600_000           # 一片衣片常见几百针 × 几百行；再大请拆开（每次计算要逐趟算）
MAX_PASSES = 30_000
MAX_TEXT = 3_000_000
MAX_COLORS = 6
SYMS = set("KPT<>.")
RACK_MAX = 4


class KnitFileError(ValueError):
    def __init__(self, zh, en):
        super().__init__(en)
        self.zh, self.en = zh, en


_TOK = re.compile(r"^([KPT<>.·])([1-6]?)$", re.I)


def parse_text(text):
    """文字表 → 意匠图（行列表，第一行先织；每格 (符号, 颜色)）"""
    if len(text) > MAX_TEXT:
        raise KnitFileError("意匠图太大，请拆开或缩小。", "The design is too large; split or reduce it.")
    rows = []
    for ln, line in enumerate(text.splitlines(), 1):
        line = line.strip().lstrip("﻿")
        if not line or line.startswith("#"):
            continue
        if re.search(r"[,;\t]", line):            # 有分隔符：逐个切，空格子当“不织”（表格软件里空白格常见）
            toks = [t.strip() or "." for t in re.split(r"[,;\t]", line)]
        else:
            toks = [t for t in line.split() if t]
            if len(toks) == 1 and len(toks[0]) > 1 and not _TOK.match(toks[0]):
                toks = list(toks[0])                  # 一个字符一格
        row = []
        for t in toks:
            m = _TOK.match(t)
            if not m:
                raise KnitFileError(f"第 {ln} 行有认不出的格子“{t[:12]}”：只能用 K P T > < . 加颜色号 1–6。",
                                    f"Line {ln} has an unknown cell '{t[:12]}': use K P T > < . with colour 1–6.")
            s = m.group(1).upper().replace("·", ".")
            row.append(_cell(s, int(m.group(2) or 1)))
        rows.append(row)
    return _check(rows)


def parse_png(data):
    """提花色码图 → 意匠图：最下面一行先织；不透明的每种颜色一个纱嘴（按用得多少排 1、2、3……），全部前编"""
    try:
        from PIL import Image
    except ImportError:                                # FreeCAD 自带的 Python 可能没有 Pillow
        raise KnitFileError("这里读不了 PNG，请用意匠图文字表（CSV / TXT）。", "PNG cannot be read here; use a text table (CSV / TXT).")
    try:
        im = Image.open(io.BytesIO(data))
        w, h = im.size                                 # 先看尺寸再解码：小文件也可能是很大的图
    except Exception:
        raise KnitFileError("图片读不出来，请存成 PNG。", "The image cannot be read; save it as PNG.")
    if w > MAX_NEEDLES or h > MAX_ROWS or w * h > MAX_CELLS:
        raise KnitFileError(f"图太大：{w} × {h} 像素（最多 {MAX_NEEDLES} 针、{MAX_ROWS} 行、共 {MAX_CELLS // 10000} 万格）。",
                            f"The image is too large: {w} × {h} (at most {MAX_NEEDLES} needles, {MAX_ROWS} rows, {MAX_CELLS} cells).")
    try:
        im.load()
    except Exception:
        raise KnitFileError("图片读不出来，请存成 PNG。", "The image cannot be read; save it as PNG.")
    im = im.convert("RGBA")
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    count = {}
    for r, g, b, a in px:
        if a >= 128:
            count[(r, g, b)] = count.get((r, g, b), 0) + 1
    if len(count) > MAX_COLORS:
        raise KnitFileError(f"图里有 {len(count)} 种颜色，最多 {MAX_COLORS} 种（一种颜色一个纱嘴）；先在制版软件里减色。",
                            f"The image has {len(count)} colours, at most {MAX_COLORS} (one per yarn carrier); reduce colours first.")
    order = {c: i + 1 for i, (c, _) in enumerate(sorted(count.items(), key=lambda kv: -kv[1]))}
    rows = []
    for y in range(h - 1, -1, -1):
        row = []
        for x in range(w):
            r, g, b, a = px[y * w + x]
            row.append(_cell("K", order[(r, g, b)]) if a >= 128 else _cell(".", 1))
        rows.append(row)
    return _check(rows)


_CELLS = {}


def _cell(s, c):
    """格子共用同一个元组（最多 6 × 6 种），大图省内存"""
    k = (s, c)
    return _CELLS.setdefault(k, k)


def _check(rows):
    rows = [r for r in rows if r]
    if not rows:
        raise KnitFileError("意匠图是空的。", "The design is empty.")
    W = max(len(r) for r in rows)
    if W > MAX_NEEDLES or len(rows) > MAX_ROWS or W * len(rows) > MAX_CELLS:
        raise KnitFileError(f"意匠图太大：{W} 针 × {len(rows)} 行（最多 {MAX_NEEDLES} 针、{MAX_ROWS} 行、共 {MAX_CELLS // 10000} 万格）。",
                            f"The design is too large: {W} needles × {len(rows)} rows (at most {MAX_NEEDLES} needles, {MAX_ROWS} rows, {MAX_CELLS} cells).")
    rows = [r + [_cell(".", 1)] * (W - len(r)) for r in rows]     # 短的行右边补“不织”
    if all(s == "." for r in rows for s, _ in r):
        raise KnitFileError("意匠图里没有要织的格子。", "The design has nothing to knit.")
    return rows


def load(text=None, png_b64=None):
    if png_b64:
        if len(png_b64) > MAX_TEXT:
            raise KnitFileError("图片太大，请缩小。", "The image is too large.")
        try:
            data = base64.b64decode(png_b64, validate=False)
        except (binascii.Error, ValueError):
            raise KnitFileError("文件内容传输出错，请重新选择文件。", "The file did not arrive intact; choose it again.")
        return parse_png(data)
    if text:
        if not isinstance(text, str):
            raise KnitFileError("意匠图格式不对。", "The design is malformed.")
        return parse_text(text)
    return None


def to_text(rows):
    """意匠图 → 文字表（第一行先织）；虚拟实验 17-2 的“导出意匠图”写的就是这个格式"""
    return "\n".join(",".join(s + (str(c) if c != 1 else "") for s, c in r) for r in rows) + "\n"


def compile(rows):
    """照搬虚拟实验 17-2 的编译器。返回 courses（每趟：row 意匠行号（从 1 起）、type knit / xfer / empty、dir、carrier、
    lo / hi 这一趟用到的针（最左、最右，含）、rack）、msgs（err / warn）、err_cells"""
    W = len(rows[0])
    front = [[] for _ in range(W)]
    back = [[] for _ in range(W)]
    carrier_side = {c: "L" for c in range(1, MAX_COLORS + 1)}
    state = {"side": "L", "loop": 0}
    courses, msgs, err = [], [], set()

    def span(idx, row):
        idx = list(idx)
        if idx:
            return min(idx), max(idx)
        live = [i for i, (s, _) in enumerate(row) if s != "."]
        return (min(live), max(live)) if live else (0, W - 1)

    def push(o):
        o["dir"] = "→" if state["side"] == "L" else "←"
        state["side"] = "R" if state["side"] == "L" else "L"
        courses.append(o)

    for r, row in enumerate(rows):
        if all(s == "." for s, _ in row):
            continue
        disp = [0] * W
        i = 0
        while i < W:
            if row[i][0] == ">":
                j = i
                while j < W and row[j][0] == ">":
                    j += 1
                k = j
                while k < W and row[k][0] == "<":
                    k += 1
                if k > j:                                 # 一段 > 紧跟一段 < 是绞花：两段对调
                    for a in range(i, j):
                        disp[a] = k - j
                    for a in range(j, k):
                        disp[a] = -(j - i)
                    i = k
                else:
                    for a in range(i, j):
                        disp[a] = 1
                    i = j
            elif row[i][0] == "<":
                j = i
                while j < W and row[j][0] == "<":
                    j += 1
                for a in range(i, j):
                    disp[a] = -1
                i = j
            else:
                i += 1
        movers = [i for i in range(W) if disp[i]]
        if movers:
            for i in movers:
                if not front[i]:
                    msgs.append(dict(t="err", zh=f"第 {r + 1} 行第 {i + 1} 针：前床针上没有线圈却要翻针（空针翻针）",
                                     en=f"Row {r + 1}, needle {i + 1}: transfer from an empty needle"))
                    err.add((r, i))
            lo, hi = span(movers, row)
            push(dict(row=r + 1, type="xfer", rack=0, carrier=0, lo=lo, hi=hi))
            for i in movers:
                back[i].extend(front[i])
                front[i] = []
            for d in sorted({disp[i] for i in movers}, reverse=True):
                if abs(d) > RACK_MAX:
                    msgs.append(dict(t="err", zh=f"第 {r + 1} 行：需要摇床 {d} 针，超过 ±{RACK_MAX} 针的行程",
                                     en=f"Row {r + 1}: racking {d} needles exceeds ±{RACK_MAX}"))
                grp = [i for i in movers if disp[i] == d]
                lo, hi = span(grp, row)
                push(dict(row=r + 1, type="xfer", rack=d, carrier=0, lo=lo, hi=hi))
                for i in grp:
                    t = i + d
                    if t < 0 or t >= W:
                        msgs.append(dict(t="err", zh=f"第 {r + 1} 行第 {i + 1} 针：移到针床外", en=f"Row {r + 1}, needle {i + 1}: moved off the bed"))
                        err.add((r, i))
                        back[i] = []
                        continue
                    front[t].extend(back[i])
                    back[i] = []

        def knit_sym(i):
            s = row[i][0]
            return s if s in "KPT<>" else None
        colors = []
        for i in range(W):
            if knit_sym(i) and row[i][1] not in colors:
                colors.append(row[i][1])
        left = colors[:]
        guard = 0
        while left:
            k = next((n for n, c in enumerate(left) if carrier_side[c] == state["side"]), -1)
            if k < 0:
                lo, hi = span([], row)
                push(dict(row=r + 1, type="empty", rack=0, carrier=0, lo=lo, hi=hi))
                guard += 1                             # 插一个空行机头就换一边，下一趟必定接得上；保险起见限次数
                if guard > len(colors) + 1:
                    break
                continue
            c = left.pop(k)
            sel = []
            for i in range(W):
                if row[i][1] != c:
                    continue
                s = knit_sym(i)
                if not s:
                    continue
                if s in "<>" and not front[i]:
                    continue
                sel.append(i)
            lo, hi = span(sel, row)
            push(dict(row=r + 1, type="knit", rack=0, carrier=c, lo=lo, hi=hi))
            carrier_side[c] = state["side"]
            for i in sel:
                s = row[i][0]
                state["loop"] += 1
                if s == "P":
                    back[i] = [state["loop"]]
                elif s == "T":
                    front[i].append(state["loop"])
                else:
                    front[i] = [state["loop"]]
    # 连续集圈太多：同一枚针连着 4 个意匠行以上集圈，线圈挂不住（教材 17.6 节“连续集圈太多”）
    for i in range(len(rows[0])):
        run = 0
        for r, row in enumerate(rows):
            run = run + 1 if row[i][0] == "T" else 0
            if run == 5:
                msgs.append(dict(t="warn", zh=f"第 {i + 1} 针从第 {r - 3} 行起连续集圈超过 4 行", en=f"Needle {i + 1}: more than 4 tucks in a row from row {r - 3}"))
                err.add((r, i))
    if len(courses) > MAX_PASSES:
        raise KnitFileError(f"编译出 {len(courses)} 趟，超过 {MAX_PASSES // 10000} 万趟（翻针太多或图太大），请拆开。",
                            f"The design compiles into {len(courses)} passes, over {MAX_PASSES}; split it.")
    return dict(courses=courses, msgs=msgs, err_cells=sorted(err), W=len(rows[0]), H=len(rows))


def stats(rows, C):
    cs = C["courses"]
    used = set(c for r in rows for s, c in r if s != ".")
    return dict(W=len(rows[0]), H=len(rows), colors=len(used), passes=len(cs), knit=sum(c["type"] == "knit" for c in cs),
                xfer=sum(c["type"] == "xfer" for c in cs), empty=sum(c["type"] == "empty" for c in cs),
                errors=sum(m["t"] == "err" for m in C["msgs"]), warns=sum(m["t"] == "warn" for m in C["msgs"]))
