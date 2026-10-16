"""知识图样段（约 47 秒）：Eddie 2026-10-16 14:47 看重《物理学导论》的信息量 → 每节一张“知识图”：中英标题、结构化排布、
6～9 个带图标和中英标注的要点，边讲边加、加上去的东西一直在动；配音和快节奏版一样快（同一段讲稿：能飞多久）。
14:50 Eddie：“好”（先做样段）。
    python3 make.py && WB_CRF=17 python3 ../../../tools/whiteboard/wb.py . --mp4
配音直接用 科普_会飞的特斯拉_v2/_tts 里同样句子的录音（按句缓存）。"""
import hashlib, importlib.util, json, sys  # noqa: E401
from pathlib import Path
import numpy as np, soundfile as sf  # noqa: E401
here = Path(__file__).resolve().parent
src = here.parent / "科普_会飞的特斯拉_v2"
spec = importlib.util.spec_from_file_location("v2", src / "make.py")
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
from popkit import car, txt  # noqa: E402
wai, missing_chars = v2.wai, v2.missing_chars
pop, tank, R, P, arr, curve, axes, spin, pulse, uid = v2.pop, v2.tank, v2.R, v2.P, v2.arr, v2.curve, v2.axes, v2.spin, v2.pulse, v2.uid

S = [s for s in v2.S if s[0].startswith(("黑科技三，重头戏", "六百升，就是", "冷空气喷出去", "两百公斤，每秒", "只悬停呢", "还有隐藏减益", "结论：这不是飞"))]
assert len(S) == 7


def L2(at, x, y, zh, en, c="ink", s=40, d=None, align="center"):
    """中文标注 + 下面一行小号英文（物理学导论的板书样式）。"""
    i = uid("lb")
    E = [txt(x, y, s, zh, at, c=c, id=i, align=align), txt(x, y + s * 0.95, int(s * 0.62), en, at, c="muted", font="en", id=i, align=align)]
    if d is not None:
        E.append(pop(at, i, d))
    return E


def link(at, pts, c="muted", d=0.0):
    """连接两节的箭头，上面一直有小点在跑（signal）。"""
    i = uid("ln")
    return [{"t": "arrow", "at": at, "id": i, "pts": [list(p) for p in pts], "c": c, "w": 4},
            {"t": "move", "at": at, "kind": "signal", "targets": [i], "speed": 260}]


def num(at, x, y, text, c="red", s=64, d=0.6):
    i = uid("nm")
    return [txt(x, y, s, text, at, c=c, id=i, font="en" if text.isascii() else "zh"), pop(at, i, d)]


B = []
# ---- 0 · 钩子（快切一张）
a = 0
E = [txt(960, 190, 84, "到底能飞多久？", a, c="red", id="q0"), pop(a, "q0")]
E += car(560, 640, 2.0, a, idp="hk", jets="down")
E += num(a, 1440, 430, "10", c="blue", s=150, d=1.2) + L2(a, 1440, 520, "个喷口", "jets", c="blue", s=52)
E += num(a, 1440, 760, "600 L", c="gold", s=150, d=2.6) + L2(a, 1440, 850, "压缩空气", "compressed air", c="gold", s=52)
B.append({"elements": E})

# ---- 1–6 · 一张知识图，边讲边加
E = L2(1, 1500, 95, "冷气推进", "Cold-gas thrust", c="gold", s=44)
# 第一行：气罐 → 喷气 → 推力 → 全力喷
a = 1   # 气罐：600 L ≈ 3 浴缸；300 bar ≈ 200 kg
E += tank(a, 205, 250, 110, 230, 0.05)
j0 = j = uid("fill")
E += [R(a, 213, 262, 94, 210, c="gold", fill="gold", idp=j, sw=3),
      {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [260, 472], "dur": 1.2, "delay": 2.5}]
for k in range(3):
    t = uid("tub")
    x = 345
    E += [P(a, f"M{x},{300 + k * 60} L{x + 90},{300 + k * 60} Q{x + 86},{338 + k * 60} {x + 70},{338 + k * 60} L{x + 20},{338 + k * 60} Q{x + 4},{338 + k * 60} {x},{300 + k * 60} Z",
            w=3, idp=t), pop(a, t, 0.6 + 0.3 * k)]
E += L2(a, 300, 545, "气罐 600 L ≈ 3 个浴缸", "Tank: 600 L ≈ 3 bathtubs", s=36)
E += num(a, 300, 640, "300 bar ≈ 200 kg", c="gold", s=40, d=2.6) + num(a, 300, 690, "700 bar ≈ 300+ kg", c="red", s=32, d=4.6)
a = 2   # 喷速 → 推力 → 每秒 130 kg
E += link(a, [(470, 370), (580, 370)])
E += [P(a, "M640,300 L760,300 L800,440 L600,440 Z", w=5)]
for k in range(3):
    t = uid("jet")
    E += [P(a, f"M{640 + k * 60},450 L{620 + k * 80},560", c="blue", w=5, idp=t),
          {"t": "move", "at": a, "kind": "flow", "targets": [t], "speed": 160}]
E += L2(a, 700, 620, "喷速 600–700 m/s", "Jet speed", c="blue", s=36, d=0.3)
E += link(a, [(830, 370), (960, 370)], d=1.2)
E += arr(a, 1080, 470, 1080, 250, c="red", w=12, d=1.4, dur=0.6)
E += L2(a, 1080, 545, "推力 80 kN", "Thrust (reported)", c="red", s=36, d=1.6)
E += [R(a, 900, 610, 360, 70, c="ink", sw=3)] + [txt(1080, 655, 30, "推力 = 每秒空气 × 喷速", a, c="ink")]
E += num(a, 1080, 735, "→ 130 kg/s", c="red", s=52, d=3.4)
a = 3   # 全力喷 1.5 秒见底
E += link(a, [(1210, 370), (1330, 370)])
E += axes(a, 1360, 470, 1800, 250)
E += curve(a, "M1360,265 C1420,275 1460,420 1540,455 C1620,468 1720,469 1800,470", c="red", w=6, pivot=(1360, 360), delay=0.6, dur=1.4)
E += L2(a, 1580, 545, "全力喷：1.5 秒见底", "Full blast: empty in 1.5 s", c="red", s=36, d=1.6)
E += num(a, 1580, 650, "1.5 s", c="red", s=72, d=2.0)
# 第二行：只悬停 → 降温 → 结论
a = 4   # 悬停 2 万牛，每秒 30 kg，5–10 秒
E += L2(a, 120, 790, "只悬停？", "Just hover?", c="blue", s=40, align="left")
E += car(560, 870, 0.8, a, idp="hv", jets="down")
E += L2(a, 560, 1015, "托住 2 吨 = 20 kN · 每秒 30+ kg", "Hold 2 t: 20 kN, 30+ kg/s", c="blue", s=32, d=0.8)
E += num(a, 230, 940, "5–10 s", c="red", s=64, d=3.0)
E += link(a, [(760, 880), (840, 880)], d=3.6)
a = 5   # 越喷越冷
E += [{"t": "icon", "at": a, "name": "thermometer", "x": 920, "y": 850, "size": 170, "c": "red", "w": 4, "id": "thm"},
      {"t": "move", "at": a, "kind": "wiggle", "targets": ["thm"], "pivot": [920, 930], "amp": 5, "hz": 3}]
for k, (x, y) in enumerate(((1040, 780), (1110, 860), (1050, 930))):
    t = uid("sn")
    E += [P(a, f"M{x - 22},{y} L{x + 22},{y} M{x},{y - 22} L{x},{y + 22} M{x - 15},{y - 15} L{x + 15},{y + 15} M{x - 15},{y + 15} L{x + 15},{y - 15}",
            c="blue", w=4, idp=t), pop(a, t, 1.4 + 0.4 * k), spin(a, t, [x, y], 30)]
E += L2(a, 1000, 990, "越喷越冷 · 喷口结霜", "Expanding gas cools, nozzles frost", c="blue", s=32, d=0.6)
E += link(a, [(1170, 880), (1290, 880)], d=3.0)
a = 6   # 结论
i = uid("st")
E += [{"t": "ellipse", "at": a, "id": i, "x": 1320, "y": 770, "w": 460, "h": 170, "c": "red", "sw": 7},
      txt(1550, 850, 54, "很贵的一跳", a, c="red", id=i), txt(1550, 905, 30, "An expensive jump", a, c="muted", font="en", id=i),
      pop(a, i, 0.4, 0.45), pulse(a, i, 2.4, 0.8)]
E += L2(a, 1550, 1000, "200 kg 空气 → 1 次跳", "200 kg of air → one jump", c="gold", s=32, d=1.4)
# ---- 加动画：每样新加的东西都动起来（Eddie 13:26：动画至少 3 倍）
idof = {e["text"]: e["id"] for e in E if e.get("t") == "text" and e.get("id")}
tank_fill = j0


def dots(at, x, y, dx, dy, n, d0, gap=0.25, c="blue", r=16, dur=0.9):
    """一串小点依次飞出（每个点一个动作，看起来像气流）。"""
    out = []
    for k in range(n):
        t = uid("dt")
        out += [{"t": "ellipse", "at": at, "id": t, "x": x - r / 2, "y": y - r / 2, "w": r, "h": r, "c": c, "fill": c},
                {"t": "move", "at": at, "kind": "shift", "targets": [t], "dx": dx, "dy": dy, "dur": dur, "delay": d0 + gap * k}]
    return out


def stream(at, pts, speed=260):
    """一条淡淡的线，上面小点一直在跑（气流、物料流），跑完不留痕。"""
    t = uid("st")
    return [{"t": "line", "at": at, "id": t, "pts": [list(p) for p in pts], "c": "muted", "w": 1},
            {"t": "move", "at": at, "kind": "signal", "targets": [t], "speed": speed}]


# 1 气罐：压力表指针 300 → 700；浴缸里的水晃
g = uid("gauge")
E += [{"t": "ellipse", "at": 1, "id": g, "x": 60, "y": 250, "w": 90, "h": 90, "c": "ink", "sw": 4}, pop(1, g, 0.2)]
nd = uid("needle")
E += [P(1, "M105,295 L75,295", c="red", w=5, idp=nd),
      {"t": "move", "at": 1, "kind": "rotate", "targets": [nd], "to": 120, "pivot": [105, 295], "dur": 0.8, "delay": 2.6},
      {"t": "move", "at": 1, "kind": "rotate", "targets": [nd], "to": 40, "pivot": [105, 295], "dur": 0.8, "delay": 4.6}]
E += [txt(105, 375, 26, "bar", 1, c="muted", font="en")]
for k in range(3):
    w = uid("wv")
    E += [P(1, f"M{355},{318 + k * 60} Q{375},{310 + k * 60} {395},{318 + k * 60} Q{415},{326 + k * 60} {430},{318 + k * 60}", c="blue", w=3, idp=w),
          {"t": "move", "at": 1, "kind": "wiggle", "targets": [w], "pivot": [392, 318 + k * 60], "amp": 4, "hz": 2}]
# 2 喷气：气流一串串喷出；推力箭头闪；每秒 130 kg 的空气飞走
for col in (680, 740, 800):
    E += stream(2, [(col, 450), (col + (col - 740) * 0.4, 560)], speed=200)
E += [pulse(2, idof["→ 130 kg/s"], 4.0)]
E += stream(2, [(1230, 725), (1340, 725)], speed=180)
# 3 全力喷：气罐 1.5 秒排空；小点沿曲线滑下；时钟
E += [{"t": "move", "at": 3, "kind": "grow", "targets": [tank_fill], "axis": "y", "from": 1, "to": 0.05, "pivot": [260, 472], "dur": 1.5, "delay": 0.6}]
cv = uid("cvs")
E += [P(3, "M1360,265 C1420,275 1460,420 1540,455 C1620,468 1720,469 1800,470", c="red", w=1, idp=cv),
      {"t": "move", "at": 3, "kind": "signal", "targets": [cv], "speed": 220}]
E += [pulse(3, idof["1.5 s"], 2.8)]
ck, hd = uid("clk"), uid("hand")
E += [{"t": "ellipse", "at": 3, "id": ck, "x": 1720, "y": 610, "w": 80, "h": 80, "c": "ink", "sw": 4}, pop(3, ck, 1.8),
      P(3, "M1760,650 L1760,620", c="red", w=4, idp=hd), {"t": "move", "at": 3, "kind": "spin", "targets": [hd], "pivot": [1760, 650], "rpm": 120}]
# 4 悬停：车升起又落下；车底气流；5–10 s 倒计时条
E += [{"t": "move", "at": 4, "kind": "shift", "targets": ["hv*"], "dx": 0, "dy": -50, "dur": 0.6, "delay": 0.4},
      {"t": "move", "at": 4, "kind": "shift", "targets": ["hv*"], "dx": 0, "dy": 50, "dur": 0.6, "delay": 4.6}]
E += stream(4, [(510, 880), (500, 960)], speed=150) + stream(4, [(610, 880), (620, 960)], speed=150)
bar_ = uid("bar")
E += [R(4, 150, 990, 170, 18, c="red", fill="red", idp=bar_, sw=2),
      {"t": "move", "at": 4, "kind": "grow", "targets": [bar_], "axis": "x", "from": 1, "to": 0, "pivot": [150, 999], "dur": 2.4, "delay": 3.2},
      pulse(4, idof["5–10 s"], 3.0)]
# 5 降温：更多霜花；温度往下的箭头
for k, (x, y) in enumerate(((1180, 790), (1250, 960), (1265, 800), (1215, 955))):
    t = uid("sn2")
    E += [P(5, f"M{x - 14},{y} L{x + 14},{y} M{x},{y - 14} L{x},{y + 14}", c="blue", w=3, idp=t), pop(5, t, 2.4 + 0.3 * k),
          spin(5, t, [x, y], 40)]
E += arr(5, 860, 780, 860, 900, c="blue", w=6, d=1.0)
# 0 钩子：车底两道气流
B[0]["elements"] += stream(0, [(470, 650), (450, 760)], 220) + stream(0, [(650, 650), (670, 760)], 220)
# 1 三个浴缸轻轻晃；推力箭头再闪一次
E += [{"t": "move", "at": 1, "kind": "bob", "targets": [e["id"] for e in E if e.get("id", "").startswith("tub")][:3], "amp": 5, "hz": 1.2}]
E += [{"t": "move", "at": 3, "kind": "wiggle", "targets": [g], "pivot": [105, 295], "amp": 4, "hz": 5}]
E += [{"t": "move", "at": 5, "kind": "wiggle", "targets": [nd], "pivot": [105, 295], "amp": 3, "hz": 4}]
E += [pulse(2, idof["喷速 600–700 m/s"], 0.9), pulse(2, idof["推力 80 kN"], 2.4), pulse(5, idof["越喷越冷 · 喷口结霜"], 3.2)]
# 6 一图看懂：关键数字依次闪一遍，小 R 跳一下
for k, key in enumerate(("300 bar ≈ 200 kg", "→ 130 kg/s", "1.5 s", "5–10 s")):
    E += [pulse(6, idof[key], 1.6 + 0.5 * k, 0.5)]
E += [{"t": "move", "at": 6, "kind": "shift", "targets": ["hv*"], "dx": 0, "dy": -40, "dur": 0.35, "delay": 0.2},
      {"t": "move", "at": 6, "kind": "shift", "targets": ["hv*"], "dx": 0, "dy": 40, "dur": 0.35, "delay": 0.6}]
B.append({"title": {"zh": "能飞多久？", "en": "How long can it fly?"}, "elements": E})

bad = missing_chars("".join(e.get("text", "") for b in B for e in b["elements"]))
if bad:
    sys.exit(f"the fonts lack: {bad}")

t, parts, segs, sr = 0.3, [], [], 24000
for zh, en in S:
    say = zh
    for k, v in v2.SAY.items():
        say = say.replace(k, v)
    x, sr = sf.read(src / "_tts" / (hashlib.md5(say.encode()).hexdigest()[:16] + ".wav"), dtype="float32")
    if not parts:
        parts.append(np.zeros(int(sr * 0.3), np.float32))
    segs.append({"zh": zh, "en": en, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    parts += [x, np.zeros(int(sr * 0.12), np.float32)]
    t += len(x) / sr + 0.12
parts.append(np.zeros(int(sr * 1.5), np.float32))
t += 1.5
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson({"zh": "知识图样段：能飞多久", "en": "Knowledge-map sample"}, segs, B, audio="配音.wav", duration=round(t, 2))
lesson["boards"] = B            # keep the board titles (to_lesson passes boards through)
lesson.update(pace=0.2, hand=False, subs=True, ink=1.5, pan=0.45)
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", round(t, 1), "s")
