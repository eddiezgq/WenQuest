"""白板讲课的 AI 部分（第 35 轮，AI 原生）：写讲稿、校对录音讲稿、排画板，再由程序检查修正。

    script  = await write_script(ai, topic, notes=…, minutes=6, course=…)   # 只有题目时：AI 写分段讲稿
    script  = await proofread(ai, asr_segments)                              # 有录音时：只纠识别错字、加标点
    boards  = await lay_out(ai, title, segments)                             # AI 按讲稿排画板（已检查修正）

画板格式与 core.compile_lesson 相同：[{title: {zh, en}, elements: [{t, at, …}]}]；at = 在第几段讲稿时画。
"""
import json
import logging
import math
import re

from .icons import ANCHORS, ICONS

log = logging.getLogger("wenquest.whiteboard")
W, H = 1920, 1080
AREA = (70, 205, 1850, 1050)          # x0, y0, x1, y1 under the board title
COLORS = ("ink", "muted", "gold", "red", "blue", "green")
ICON_HELP = {
    "sun": "太阳", "sunrise": "日出（地平线上的半个太阳）", "moon": "弯月", "wind": "风", "water": "水波", "eye": "眼睛（观察）",
    "flask": "烧瓶（实验）", "ruler": "尺子（测量）", "magnifier": "放大镜", "robot_arm": "机器人手臂（基座、两节连杆、夹爪）",
    "atom": "原子", "molecule": "分子", "dinosaur": "恐龙", "globe": "地球", "cloud": "云", "phone": "手机", "rocket": "火箭",
    "gear": "齿轮", "building": "大楼", "computer": "电脑显示器", "mousetrap": "捕鼠器", "car": "小轿车（侧面，车头朝右）",
    "engine": "发动机", "headlight": "车灯（带光线）", "mirror": "后视镜", "battery": "电池", "spring": "弹簧/减震器",
    "speaker": "扬声器", "wheel": "车轮", "satellite": "卫星", "clock": "时钟", "map_pin": "地图定位针", "chip": "芯片",
    "lattice": "晶格", "laser": "激光器", "lens": "透镜", "fiber": "光纤", "magnet": "U 形磁铁", "flame": "火焰",
    "thermometer": "温度计", "prism": "三棱镜", "sine": "正弦波", "block_force": "受力的木块", "check": "对勾",
    "question": "问号", "earth_arc": "地平线弧", "signal": "无线信号",
}

# ---------------------------------------------------------------- 讲稿
SCRIPT_SYSTEM = """你是问渠机器人学院的主讲老师，要录一段白板讲解（像 VideoScribe：老师边讲，手边在白板上画）。
写分段讲稿，口语、亲切、清楚，中文为主，术语第一次出现时附英文（如“力矩（torque）”）。

课程标准（理工科）：先给一个实际问题（以机器人为主），再讲概念，接着建模和求解（有数就算出来），最后小结；
全课再用一个生活中的例子帮助理解。数字、公式必须正确，单位写全。

分段规则：每段 1～2 句话、约 15～45 个字，是画面上“画一样东西”的节奏；整节约 {minutes} 分钟（每分钟约 230 字）。
每段另写 en：这一段的英文翻译（简洁）。标题给中英文。只输出 JSON。"""

SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "object", "properties": {"zh": {"type": "string"}, "en": {"type": "string"}}, "required": ["zh", "en"]},
        "segments": {"type": "array", "items": {"type": "object", "properties": {"zh": {"type": "string"}, "en": {"type": "string"}},
                                                "required": ["zh"]}},
    },
    "required": ["title", "segments"],
}

PROOF_SYSTEM = """下面是老师讲课录音的语音识别结果，按段给出（编号、时间、文字）。请逐段校对：
只改识别错的字（同音字、漏掉的开头字等）、加上标点，术语写对；不要改老师的说法，不要合并或拆分段落，不要增删内容。
另给这节课一个中英文标题。只输出 JSON：{title: {zh, en}, segments: [{i, zh}]}，i 与输入编号一致。"""

PROOF_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "object", "properties": {"zh": {"type": "string"}, "en": {"type": "string"}}, "required": ["zh", "en"]},
        "segments": {"type": "array", "items": {"type": "object", "properties": {"i": {"type": "integer"}, "zh": {"type": "string"}},
                                                "required": ["i", "zh"]}},
    },
    "required": ["segments"],
}

# ---------------------------------------------------------------- 画板
BOARD_SYSTEM = """你是白板讲解的画板设计师。老师按讲稿一段一段讲，一只手在白板上跟着画。你决定每张画板上画什么、画在哪、在第几段画。

画板：1920×1080（x 向右，y 向下）。每张画板左上角自动写标题（中英），你不要再写标题；内容只放在 x 70～1850、y 205～1050。
需要几张画板就用几张：一个小主题一张，约每 40～70 秒讲稿一张；一张画板 5～14 样东西，宁可多开一张也不要挤。

元素（每个都要写 at = 在第几段讲稿时画，从 0 开始；同一段里按列出的先后画）：
- box：带框的标签。x, y 是中心；w, h；zh 中文（≤10 字），en 英文小字（可省）；s 中文字号（32～48）。
- text：一行字。x, y 是这行字的基线位置；align: left | center | right；s 字号（26～64）；font: zh（中文楷体）或 en（英文手写体）。
  公式、数值写成一行字，如 "τ = F × r = 20 N × 0.3 m = 6 N·m"。一行不超过 20 个汉字或 40 个字母，长句拆成几行。
- arrow / line：pts = [[x, y], [x, y], …]（2～4 个点），箭头画在最后一点；用来连接方框、指向部位、画受力。
- rect / ellipse：x, y 是左上角，w, h；fill 可填颜色（斜线阴影），用来画简单形状或高亮。
- icon：简笔画，name 只能从图标表里选；x, y 是中心；size 是边长（80～420）。表里没有的东西，用 box/text 写出来，或用 line/rect/ellipse 简单画。
  图标表里列了一些图标的“部位”（在 200×200 图标里的坐标）。要用箭头指向或圈出某个部位时，它在画板上的位置是
  (x + (部位x − 100) × size / 200, y + (部位y − 100) × size / 200)；箭头末端放在部位附近，程序会把它对准。
- media：插入本课程已有的虚拟实验、动画或数字工厂视频（只能用“可插入的素材”清单里的 src）。x, y 是框的左上角，w, h 是框的大小
  （约 16:9，宽 640～1200）。先画框，讲到这段时框里开始播放/打开实验；play 可写播放秒数。讲到动态过程、或“动手试试”时用。
- move：让已经画好的东西动起来（画的东西活起来）。先给要动的元素写 id（任意短名，一组东西可以用同一个 id），
  再写 {t: "move", at, kind, targets: [id…]}：
  · rotate：绕 pivot [x, y] 转到 to 度（顺时针为正），如机械臂从水平抬到 60° 写 to: -60；dur 秒数（默认约 2 秒）；
  · shift：平移 dx, dy；· spin：绕 pivot（不写则绕自身中心）持续转，rpm 每分钟转数，如车轮、齿轮、螺母；
  · flow：线条上流动（电流、力的传递、光线、物料流），speed 快慢；· pulse：强调时闪一下。
  讲到“转起来”“抬起来”“流过去”这类动作时就加 move，让画面活起来；一张画板 1～3 个动作即可。
颜色 c：ink（黑，默认）、muted（灰，次要）、gold（金，重点）、red（红，问题/警示/力）、blue（蓝，概念/示意）、green（绿，结论/正确）。

讲究：
- 画的东西要跟这段讲的话对得上：讲到什么画什么，讲完一个点画一个结论。
- 版面整齐：同类东西对齐成行或列，留白均匀；方框之间至少 40 像素；文字不要压在图标或线上；不要出界。
- 实际问题（机器人）配简笔画和受力/尺寸标注；概念用方框和箭头串起来；计算一行一行写出来；小结用 2～4 个要点。
- 中文为主，重要术语配英文小字。
只输出 JSON。"""

ELEMENT = {
    "type": "object",
    "properties": {
        "t": {"type": "string", "enum": ["box", "text", "arrow", "line", "rect", "ellipse", "icon", "media", "move"]},
        "id": {"type": "string"}, "src": {"type": "string"}, "play": {"type": "number"},
        "kind": {"type": "string", "enum": ["rotate", "shift", "spin", "flow", "pulse", "wiggle", "bob", "signal", "pop", "grow"]},
        "targets": {"type": "array", "items": {"type": "string"}}, "pivot": {"type": "array", "items": {"type": "number"}},
        "to": {"type": "number"}, "dx": {"type": "number"}, "dy": {"type": "number"}, "rpm": {"type": "number"},
        "speed": {"type": "number"}, "dur": {"type": "number"}, "delay": {"type": "number"},
        "at": {"type": "integer"},
        "x": {"type": "number"}, "y": {"type": "number"}, "w": {"type": "number"}, "h": {"type": "number"},
        "s": {"type": "number"}, "size": {"type": "number"},
        "zh": {"type": "string"}, "en": {"type": "string"}, "text": {"type": "string"},
        "font": {"type": "string", "enum": ["zh", "en"]}, "align": {"type": "string", "enum": ["left", "center", "right"]},
        "c": {"type": "string"}, "fill": {"type": "string"}, "name": {"type": "string"},
        "pts": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
    },
    "required": ["t", "at"],
}
BOARD_SCHEMA = {
    "type": "object",
    "properties": {"boards": {"type": "array", "items": {
        "type": "object",
        "properties": {"title": {"type": "object", "properties": {"zh": {"type": "string"}, "en": {"type": "string"}}, "required": ["zh"]},
                       "elements": {"type": "array", "items": ELEMENT}},
        "required": ["title", "elements"]}}},
    "required": ["boards"],
}


def icon_table() -> str:
    rows = []
    for k in ICONS:
        parts = ANCHORS.get(k)
        extra = ("；部位 " + "、".join(f"{n}({x},{y})" for n, (x, y) in parts.items())) if parts else ""
        rows.append(f"- {k}：{ICON_HELP.get(k, k)}{extra}")
    return "\n".join(rows)


def anchor_xy(icon: dict, part: str):
    ax, ay = ANCHORS[icon["name"]][part]
    k = icon["size"] / 200
    return (icon["x"] + (ax - 100) * k, icon["y"] + (ay - 100) * k)


def _fmt(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


# ---------------------------------------------------------------- layout check and repair
def media_table(available: list[dict]) -> str:
    """available: [{src, title, kind}] — the course's own labs, animations and factory videos."""
    return "\n".join(f"- {m['src']}：{m.get('title', '')}（{m.get('kind', '')}）" for m in available) or "（这一课没有可插入的素材）"


def text_width(text: str, s: float, font: str = "zh") -> float:
    w = 0.0
    for ch in text:
        w += s * (1.0 if ord(ch) > 0x2e80 else (0.52 if font == "en" else 0.56))
    return w


def bbox(e: dict):
    t = e["t"]
    if t == "box":
        return (e["x"] - e["w"] / 2, e["y"] - e["h"] / 2, e["x"] + e["w"] / 2, e["y"] + e["h"] / 2)
    if t == "text":
        w = text_width(e["text"], e["s"], e.get("font", "zh"))
        x0 = e["x"] - (w / 2 if e.get("align") == "center" else w if e.get("align") == "right" else 0)
        return (x0, e["y"] - e["s"] * 0.88, x0 + w, e["y"] + e["s"] * 0.22)
    if t in ("rect", "ellipse", "media"):
        return (e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"])
    if t == "icon":
        r = e["size"] / 2
        return (e["x"] - r, e["y"] - r, e["x"] + r, e["y"] + r)
    xs, ys = [p[0] for p in e["pts"]], [p[1] for p in e["pts"]]
    return (min(xs), min(ys), max(xs), max(ys))


def _overlap(a, b, pad=8):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])


def _num(v, d, lo, hi):
    try:
        v = float(v)
        if math.isnan(v):
            raise ValueError
    except (TypeError, ValueError):
        v = d
    return max(lo, min(hi, v))


def clean_element(e: dict, nseg: int, allowed: frozenset = frozenset()) -> dict | None:
    """One element made safe: known type, numbers in range, texts short enough to fit; None if it cannot be used."""
    t = e.get("t")
    x0, y0, x1, y1 = AREA
    out = {"t": t, "at": int(_num(e.get("at"), 0, 0, max(0, nseg - 1)))}
    c = e.get("c") if e.get("c") in COLORS else "ink"
    out["c"] = c
    if isinstance(e.get("id"), (str, int)) and str(e["id"]).strip():
        out["id"] = str(e["id"]).strip()[:24]
    if t == "move":
        kind = e.get("kind") if e.get("kind") in ("rotate", "shift", "spin", "flow", "pulse", "wiggle", "bob", "signal", "pop", "grow") else None
        targets = [str(x)[:24] for x in e.get("targets") or [] if str(x).strip()]
        if not kind or not targets:
            return None
        out.update(kind=kind, targets=targets)
        piv = e.get("pivot")
        if isinstance(piv, (list, tuple)) and len(piv) >= 2:
            out["pivot"] = [_num(piv[0], 960, -200, W + 200), _num(piv[1], 540, -200, H + 200)]
        if kind == "rotate":
            out["to"] = _num(e.get("to"), 30, -360, 360)
        if kind == "shift":
            out["dx"], out["dy"] = _num(e.get("dx"), 0, -1600, 1600), _num(e.get("dy"), 0, -900, 900)
        if kind == "spin":
            out["rpm"] = _num(e.get("rpm"), 20, 1, 120)
        if kind in ("wiggle", "bob"):
            out["amp"] = _num(e.get("amp"), 14 if kind == "wiggle" else 12, 1, 60)
            out["hz"] = _num(e.get("hz"), 4 if kind == "wiggle" else 1.5, 0.2, 12)
        if kind == "flow":
            out["speed"] = _num(e.get("speed"), 70, 10, 400)
        if e.get("dur") is not None:
            out["dur"] = _num(e.get("dur"), 2, 0.3, 12)
        if e.get("delay") is not None:
            out["delay"] = _num(e.get("delay"), 0, 0, 10)
        return out
    if t == "media":
        src = str(e.get("src") or "").strip()
        if src not in allowed:
            return None
        w = _num(e.get("w"), 960, 320, x1 - x0)
        h = _num(e.get("h"), w * 9 / 16, 180, y1 - y0)
        out.update(src=src, w=w, h=h, x=_num(e.get("x"), x0, x0, x1 - w), y=_num(e.get("y"), y0, y0, y1 - h))
        if e.get("play") is not None:
            out["play"] = _num(e.get("play"), 10, 1, 600)
        return out
    if t == "icon" and e.get("name") not in ICONS:
        label = (e.get("zh") or e.get("text") or e.get("name") or "").strip()
        if not label or not re.search(r"[一-鿿]", label):
            return None
        t = "box"
        e = dict(e, t="box", zh=label[:10], w=max(160, text_width(label[:10], 36) + 50), h=90)
        out["t"] = "box"
    if t == "box":
        zh = str(e.get("zh") or e.get("text") or "").strip()[:14]
        if not zh:
            return None
        s = _num(e.get("s"), 40, 26, 56)
        en = str(e.get("en") or "").strip()[:40]
        need = max(text_width(zh, s), text_width(en, max(22, s * 0.62), "en")) + 44
        w = _num(e.get("w"), need, 110, 900)
        if w < need:                         # the words would stick out: widen, or shrink the words
            w = min(900, need)
            if need > 900:
                s = max(26, s * 900 / need)
        h = _num(e.get("h"), 100 if en else 80, 60, 320)
        out.update(x=_num(e.get("x"), 960, x0 + w / 2, x1 - w / 2), y=_num(e.get("y"), 600, y0 + h / 2, y1 - h / 2), w=w, h=h,
                   zh=zh, s=s, **({"en": en} if en else {}))
    elif t == "text":
        text = str(e.get("text") or e.get("zh") or "").strip()
        if not text:
            return None
        font = e.get("font") if e.get("font") in ("zh", "en") else ("zh" if re.search(r"[一-鿿]", text) else "en")
        s = _num(e.get("s"), 36, 22, 90)
        width = text_width(text, s, font)
        if width > x1 - x0:
            s = max(22, s * (x1 - x0) / width)
            width = text_width(text, s, font)
        align = e.get("align") if e.get("align") in ("left", "center", "right") else "left"
        lo = x0 + (width / 2 if align == "center" else width if align == "right" else 0)
        hi = x1 - (width / 2 if align == "center" else 0 if align == "right" else width)
        out.update(text=text, s=s, font=font, align=align, x=_num(e.get("x"), lo, lo, max(lo, hi)), y=_num(e.get("y"), 600, y0 + s, y1))
    elif t in ("rect", "ellipse"):
        w, h = _num(e.get("w"), 200, 16, x1 - x0), _num(e.get("h"), 120, 16, y1 - y0)
        out.update(x=_num(e.get("x"), 900, x0, x1 - w), y=_num(e.get("y"), 500, y0, y1 - h), w=w, h=h)
        if e.get("fill") in COLORS:
            out["fill"] = e["fill"]
    elif t in ("arrow", "line"):
        pts = [[_num(p[0], 900, x0 - 20, x1 + 20), _num(p[1], 600, y0 - 20, y1 + 20)] for p in (e.get("pts") or [])
               if isinstance(p, (list, tuple)) and len(p) >= 2][:6]
        if len(pts) < 2 or all(abs(p[0] - pts[0][0]) + abs(p[1] - pts[0][1]) < 6 for p in pts):
            return None
        out.update(pts=pts, w=_num(e.get("w"), 3.2, 2, 7))
    elif t == "icon":
        size = _num(e.get("size"), 180, 70, 460)
        out.update(name=e["name"], size=size, x=_num(e.get("x"), 960, x0 + size / 2, x1 - size / 2),
                   y=_num(e.get("y"), 600, y0 + size / 2, y1 - size / 2))
    else:
        return None
    return out


def _drawable(text: str) -> str:
    from .core import missing_chars
    bad = missing_chars(text)
    return "".join(ch for ch in text if ch not in bad) if bad else text


def snap_to_parts(els: list[dict], reach: float = 110) -> int:
    """Arrow and line ends, and small marking circles, near a named icon part are put exactly on it."""
    parts = [anchor_xy(e, p) for e in els if e["t"] == "icon" and e["name"] in ANCHORS for p in ANCHORS[e["name"]]]
    n = 0
    for e in els:
        if e["t"] in ("arrow", "line"):
            for k in (0, -1):
                p = e["pts"][k]
                best = min(parts, key=lambda q: math.dist(q, p), default=None)
                if best and 0 < math.dist(best, p) <= reach:
                    e["pts"][k] = [round(best[0], 1), round(best[1], 1)]
                    n += 1
        elif e["t"] == "ellipse" and max(e["w"], e["h"]) <= 140 and not e.get("id"):
            c = (e["x"] + e["w"] / 2, e["y"] + e["h"] / 2)
            best = min(parts, key=lambda q: math.dist(q, c), default=None)
            if best and 0 < math.dist(best, c) <= reach + 40:
                e["x"], e["y"] = best[0] - e["w"] / 2, best[1] - e["h"] / 2
                n += 1
    return n


def fix_board(elements: list[dict], nseg: int, allowed: frozenset = frozenset()) -> tuple[list[dict], list[str]]:
    """Clean every element, then move solid things (boxes, words, icons, shapes) apart where they overlap."""
    notes = []
    els = [c for c in (clean_element(e, nseg, allowed) for e in elements if isinstance(e, dict)) if c]
    for e in els:
        for key in ("text", "zh", "en"):
            if e.get(key):
                e[key] = _drawable(e[key])

    if len(els) < len([e for e in elements if isinstance(e, dict)]):
        notes.append(f"dropped {len(elements) - len(els)} unusable element(s)")
    x0, y0, x1, y1 = AREA
    placed = []
    for e in els:
        if e["t"] in ("arrow", "line", "move") or (e["t"] in ("ellipse", "rect") and max(e["w"], e["h"]) <= 140):
            continue   # lines and small marks are meant to sit on other things
        for _ in range(12):
            b = bbox(e)
            hit = next((p for p in placed if _overlap(b, p)), None)
            if not hit:
                break
            # move down below the obstacle when there is room, else to its right, else give up
            dy = hit[3] + 14 - b[1]
            dx = hit[2] + 14 - b[0]
            if b[3] + dy <= y1:
                e["y"] += dy
            elif b[2] + dx <= x1:
                e["x"] += dx
            else:
                notes.append(f"could not clear an overlap for {e.get('zh') or e.get('text') or e.get('name')}")
                break
        placed.append(bbox(e))
    if snap_to_parts(els):
        notes.append("arrows snapped to icon parts")
    return els, notes


def fix_boards(boards: list[dict], nseg: int, allowed=()) -> tuple[list[dict], list[str]]:
    """Every board cleaned; boards follow the lecture (a later board never draws during an earlier segment)."""
    out, notes, floor = [], [], 0
    for i, b in enumerate(boards or []):
        if not isinstance(b, dict):
            continue
        els, n = fix_board(b.get("elements") or [], nseg, frozenset(allowed))
        if not els:
            continue
        for e in els:
            e["at"] = max(e["at"], floor)
        floor = max(e["at"] for e in els)
        title = b.get("title") if isinstance(b.get("title"), dict) else {}
        out.append({"title": {"zh": str(title.get("zh") or f"第 {len(out) + 1} 张")[:20], "en": str(title.get("en") or "")[:48]},
                    "elements": els})
        notes += [f"board {i + 1}: {x}" for x in n]
    return out, notes


# ---------------------------------------------------------------- AI calls
async def write_script(ai, topic: str, notes: str = "", minutes: float = 6, course: str = "") -> dict:
    prompt = (f"课程：{course or '（未指定）'}\n题目：{topic}\n" + (f"老师的要求和资料：\n{notes[:20000]}\n" if notes else "")
              + f"时长：约 {minutes:g} 分钟。")
    data = await ai.json(system=SCRIPT_SYSTEM.replace("{minutes}", f"{minutes:g}"), prompt=prompt, schema=SCRIPT_SCHEMA,
                         max_tokens=12000, fake=lambda: fake_script(topic))
    segs = [{"zh": str(s.get("zh") or "").strip(), "en": str(s.get("en") or "").strip()} for s in data.get("segments") or []]
    segs = [s for s in segs if s["zh"]]
    if not segs:
        raise ValueError("the script came back empty")
    t = data.get("title") or {}
    return {"title": {"zh": str(t.get("zh") or topic)[:40], "en": str(t.get("en") or "")[:80]}, "segments": segs}


async def proofread(ai, segments: list[dict]) -> dict:
    lines = "\n".join(f"{i}\t{_fmt(s['t0'])}\t{s['zh']}" for i, s in enumerate(segments))
    data = await ai.json(system=PROOF_SYSTEM, prompt=lines[:60000], schema=PROOF_SCHEMA, max_tokens=16000,
                         fake=lambda: {"title": {"zh": "白板讲解", "en": "Whiteboard lecture"},
                                       "segments": [{"i": i, "zh": s["zh"]} for i, s in enumerate(segments)]})
    fixed = {int(x["i"]): str(x["zh"]).strip() for x in data.get("segments") or [] if isinstance(x.get("i"), int) and x.get("zh")}
    out = [dict(s, zh=fixed.get(i, s["zh"]) or s["zh"]) for i, s in enumerate(segments)]
    t = data.get("title") or {}
    return {"title": {"zh": str(t.get("zh") or "白板讲解")[:40], "en": str(t.get("en") or "")[:80]}, "segments": out}


async def lay_out(ai, title: dict, segments: list[dict], note: str = "", available: list[dict] | None = None) -> tuple[list[dict], list[str]]:
    """The AI lays the boards out; the program checks and repairs them. available = the course's labs, animations, videos."""
    lines = "\n".join(f"{i}\t{_fmt(s.get('t0', 0))}–{_fmt(s.get('t1', 0))}\t{s['zh']}" for i, s in enumerate(segments))
    prompt = (f"课题：{title.get('zh')} / {title.get('en', '')}\n\n图标表（icon 的 name 只能用这些）：\n{icon_table()}\n\n"
              f"可插入的素材（media 的 src 只能用这些）：\n{media_table(available or [])}\n\n"
              f"讲稿（编号、时间、话）：\n{lines[:50000]}" + (f"\n\n老师的意见：{note}" if note else ""))
    data = await ai.json(system=BOARD_SYSTEM, prompt=prompt, schema=BOARD_SCHEMA, max_tokens=32000,
                         fake=lambda: fake_boards(segments))
    boards, notes = fix_boards(data.get("boards") or [], len(segments), [m["src"] for m in available or []])
    if not boards:
        boards, notes = fix_boards(fake_boards(segments)["boards"], len(segments))
        notes.append("the AI gave no usable board: a plain board of the key sentences was made")
    return boards, notes


# ---------------------------------------------------------------- stand-ins (tests, and when the AI fails)
def fake_script(topic: str) -> dict:
    return {"title": {"zh": topic[:30], "en": "Whiteboard lecture"},
            "segments": [{"zh": f"我们来看{topic}。", "en": f"Let us look at {topic}."},
                         {"zh": "先看一个机器人的实际问题。", "en": "First, a real robot problem."},
                         {"zh": "再把它抽象成一个模型。", "en": "Then we turn it into a model."},
                         {"zh": "最后算出结果并小结。", "en": "Finally we solve it and sum up."}]}


def fake_boards(segments: list[dict]) -> dict:
    """A plain board per six segments: each segment's words as a line of text."""
    boards = []
    for k in range(0, len(segments), 6):
        els = []
        for j, s in enumerate(segments[k:k + 6]):
            line = s["zh"][:20]
            els.append({"t": "text", "at": k + j, "x": 120, "y": 300 + j * 120, "text": line, "s": 40, "align": "left"})
        boards.append({"title": {"zh": f"第 {len(boards) + 1} 部分", "en": f"Part {len(boards) + 1}"}, "elements": els})
    return {"boards": boards}


def to_lesson(title: dict, segments: list[dict], boards: list[dict], audio: str = "", duration: float = 0) -> dict:
    """The lesson file core.compile_lesson reads."""
    return {"title": title.get("zh", ""), "title_en": title.get("en", ""), "audio": audio, "duration": duration,
            "segments": [{"t0": s.get("t0", 0), "t1": s.get("t1", 0), "zh": s["zh"], **({"en": s["en"]} if s.get("en") else {})}
                         for s in segments], "boards": boards}


def describe(boards: list[dict]) -> str:
    return json.dumps([{"title": b["title"]["zh"], "n": len(b["elements"])} for b in boards], ensure_ascii=False)
