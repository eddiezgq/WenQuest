"""快节奏样段（约 40 秒）：Eddie 2026-10-16 11:07“视频不够清晰，动画太少，节奏太慢，我喜欢节奏快，信息量大”。
同一段内容（能飞多久）按新标准重做：线更粗、字更大（数字 110 px 以上）、画得更快（pace 0.32）、镜头 0.45 秒切换、语速 1.22、句间 0.12 秒；
每 2～3 秒有东西在动（弹出、增长、流动、计时、排空）；每句都带一个数字。
    python3 make.py <kokoro 模型目录> [--boards-only] && WB_CRF=17 python3 ../../../tools/whiteboard/wb.py . --mp4"""
import json, sys  # noqa: E401
from pathlib import Path
import numpy as np, soundfile as sf  # noqa: E401
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[2] / "services" / "gateway"))
sys.path.insert(0, str(here.parent))
from app.production.whiteboard import ai as wai  # noqa: E402
from app.production.whiteboard.core import missing_chars  # noqa: E402
from app.production.whiteboard.speech import speakable  # noqa: E402
from popkit import car, txt  # noqa: E402

S = [
 ("重头戏：它到底能飞多久？官方只给了两个数：十个喷口，六百升压缩空气。", "The main event: how long can it fly? Tesla gave two numbers: ten jets, 600 liters of compressed air."),
 ("六百升，就是三个浴缸。压到三百个大气压，大约装两百公斤空气；压到七百，也就三百多公斤。", "600 liters is three bathtubs. At 300 atmospheres that's about 200 kg of air; at 700, just over 300."),
 ("冷空气喷出去，每秒最多六七百米。推力八万牛，除一下：每秒要喷掉一百三十公斤。", "Cold air leaves at 600 to 700 meters per second at most. 80 kN divided by that: 130 kg every second."),
 ("两百公斤，每秒一百三，一秒半见底。而且压力一掉，推力跟着掉。", "200 kg at 130 per second: empty in a second and a half. And as pressure drops, so does thrust."),
 ("只悬停呢？两吨的车要两万牛，每秒三十多公斤：五到十秒，就得落地。", "Just hovering? Two tons needs 20 kN, over 30 kg a second: down again in five to ten seconds."),
 ("还有隐藏减益：气体一膨胀就降温，罐子越喷越冷，压力掉得更快，喷口还会结霜。", "Hidden penalty: expanding gas cools, the tank gets colder, pressure falls faster, and nozzles frost."),
 ("结论：这不是飞，是用两百公斤空气，换来的一次很贵的跳。", "Verdict: it doesn't fly. It trades 200 kg of air for one very expensive jump."),
]
SAY = {"减益": "减益"}

def P(at, d, c="ink", w=4, idp=None):
    e = {"t": "path", "at": at, "c": c, "w": w, "d": d}
    if idp:
        e["id"] = idp
    return e

def pop(at, ids, delay=0.0, dur=0.35):
    return {"t": "move", "at": at, "kind": "pop", "targets": ids if isinstance(ids, list) else [ids], "dur": dur, "delay": delay}

B = []
# 0 · 能飞多久？10 个喷口 + 600 升
els = [txt(960, 190, 84, "到底能飞多久？", 0, c="red", id="q0"), pop(0, "q0")]
els += car(560, 640, 2.0, 0, idp="c0", jets="down")
els += [txt(1440, 430, 150, "10", 0, c="blue", font="en", id="n10"), txt(1440, 520, 52, "个喷口", 0, c="blue"), pop(0, "n10", 1.2),
        txt(1440, 760, 150, "600 L", 0, c="gold", font="en", id="n600"), txt(1440, 850, 52, "压缩空气", 0, c="gold"), pop(0, "n600", 2.6)]
B.append(els)
# 1 · 三个浴缸；300 bar ≈ 200 kg；700 bar ≈ 300+ kg
els = []
for i, x in enumerate((240, 520, 800)):
    els += [P(1, f"M{x},300 L{x + 240},300 Q{x + 230},420 {x + 185},420 L{x + 55},420 Q{x + 10},420 {x},300 Z", w=5, idp=f"tub{i}"),
            pop(1, f"tub{i}", 0.3 * i)]
els += [txt(640, 520, 56, "600 L ≈ 3 个浴缸", 1, c="gold"),
        {"t": "rect", "at": 1, "x": 1180, "y": 260, "w": 140, "h": 600, "c": "ink", "sw": 5},
        {"t": "rect", "at": 1, "id": "g300", "x": 1195, "y": 560, "w": 110, "h": 285, "c": "gold", "fill": "gold"},
        {"t": "move", "at": 1, "kind": "grow", "targets": ["g300"], "axis": "y", "pivot": [1250, 845], "dur": 1.0, "delay": 2.0},
        txt(1250, 940, 52, "300 bar", 1, font="en"), txt(1250, 1010, 44, "≈ 200 kg", 1, c="gold"),
        {"t": "rect", "at": 1, "x": 1520, "y": 260, "w": 140, "h": 600, "c": "ink", "sw": 5},
        {"t": "rect", "at": 1, "id": "g700", "x": 1535, "y": 300, "w": 110, "h": 545, "c": "red", "fill": "red"},
        {"t": "move", "at": 1, "kind": "grow", "targets": ["g700"], "axis": "y", "pivot": [1590, 845], "dur": 1.0, "delay": 4.2},
        txt(1590, 940, 52, "700 bar", 1, font="en"), txt(1590, 1010, 44, "≈ 300+ kg", 1, c="red")]
B.append(els)
# 2 · F = ṁ·v → 80000 ÷ 600 ≈ 133 kg/s
els = [txt(960, 260, 76, "推力 = 每秒喷出的空气 × 喷速", 2, id="f"), pop(2, "f"),
       txt(560, 470, 52, "喷速 v ≈ 600–700 m/s", 2, c="blue"),
       txt(1360, 470, 52, "推力 F ≈ 80,000 N", 2, c="red"),
       txt(960, 720, 140, "≈ 130 kg/s", 2, c="red", id="kgs"), pop(2, "kgs", 3.0),
       txt(960, 830, 48, "每秒喷掉的空气", 2, c="muted")]
for i in range(6):
    els += [{"t": "ellipse", "at": 2, "id": "puff", "x": 300 + i * 40, "y": 900 + (i % 2) * 30, "w": 30, "h": 30, "c": "blue", "fill": "blue"}]
els += [{"t": "move", "at": 2, "kind": "shift", "targets": ["puff"], "dx": 1300, "dy": 0, "dur": 3.5, "delay": 1.0}]
B.append(els)
# 3 · 一秒半见底；推力跟着掉
els = [{"t": "rect", "at": 3, "x": 260, "y": 220, "w": 220, "h": 640, "c": "ink", "sw": 5},
       {"t": "rect", "at": 3, "id": "air", "x": 278, "y": 238, "w": 184, "h": 604, "c": "gold", "fill": "gold"},
       {"t": "move", "at": 3, "kind": "grow", "targets": ["air"], "axis": "y", "from": 1, "to": 0.02, "pivot": [370, 842], "dur": 1.5, "delay": 1.2},
       txt(370, 940, 48, "200 kg", 3, c="gold", font="en"),
       {"t": "line", "at": 3, "pts": [[700, 860], [1780, 860]], "c": "ink", "w": 4},
       {"t": "line", "at": 3, "pts": [[700, 860], [700, 260]], "c": "ink", "w": 4},
       P(3, "M700,300 C820,320 900,700 1100,820 C1300,850 1600,855 1780,856", c="red", w=6, idp="curve"),
       {"t": "move", "at": 3, "kind": "grow", "targets": ["curve"], "pivot": [700, 560], "dur": 1.5, "delay": 1.2},
       txt(1240, 330, 64, "1.5 秒见底", 3, c="red", id="t15"), pop(3, "t15", 2.8),
       txt(1500, 940, 44, "推力 vs 时间", 3, c="muted")]
B.append(els)
# 4 · 悬停：2 万牛，30 kg/s，5–10 秒
els = car(620, 820, 1.7, 4, idp="c4", jets="down")
els += [{"t": "move", "at": 4, "kind": "shift", "targets": ["c4*"], "dx": 0, "dy": -330, "dur": 1.2, "delay": 0.4},
        {"t": "move", "at": 4, "kind": "shift", "targets": ["c4*"], "dx": 0, "dy": 330, "dur": 1.2, "delay": 6.0},
        txt(1400, 300, 64, "托住 2 吨 = 20,000 N", 4, c="blue"),
        txt(1400, 470, 64, "每秒 30+ kg", 4, c="red", id="k30"), pop(4, "k30", 1.6),
        txt(1400, 720, 150, "5–10 s", 4, c="red", font="en", id="s510"), pop(4, "s510", 3.2)]
B.append(els)
# 5 · 降温、结霜
els = [txt(960, 200, 80, "隐藏减益：冷", 5, c="blue", id="cold"), pop(5, "cold")]
els += [{"t": "rect", "at": 5, "x": 300, "y": 320, "w": 60, "h": 520, "c": "ink", "sw": 5},
        {"t": "ellipse", "at": 5, "x": 270, "y": 820, "w": 120, "h": 120, "c": "ink", "sw": 5},
        {"t": "rect", "at": 5, "id": "merc", "x": 315, "y": 340, "w": 30, "h": 500, "c": "red", "fill": "red"},
        {"t": "move", "at": 5, "kind": "grow", "targets": ["merc"], "axis": "y", "from": 1, "to": 0.25, "pivot": [330, 840], "dur": 3.0, "delay": 0.6},
        txt(520, 600, 52, "越喷越冷", 5, c="blue", align="left")]
for i, (x, y) in enumerate([(1100, 420), (1360, 360), (1600, 470), (1250, 620), (1500, 700)]):
    els += [P(5, f"M{x - 40},{y} L{x + 40},{y} M{x},{y - 40} L{x},{y + 40} M{x - 28},{y - 28} L{x + 28},{y + 28} M{x - 28},{y + 28} L{x + 28},{y - 28}",
              c="blue", w=5, idp=f"sn{i}"),
            pop(5, f"sn{i}", 2.0 + 0.4 * i),
            {"t": "move", "at": 5, "kind": "spin", "targets": [f"sn{i}"], "pivot": [x, y], "rpm": 20}]
els += [txt(1360, 880, 56, "压力掉得更快 · 喷口结霜", 5, c="red")]
B.append(els)
# 6 · 结论：很贵的跳
els = car(960, 880, 2.0, 6, idp="c6", mood="o", jets="down")
els += [{"t": "move", "at": 6, "kind": "shift", "targets": ["c6*"], "dx": 0, "dy": -300, "dur": 0.5, "delay": 0.3},
        {"t": "move", "at": 6, "kind": "shift", "targets": ["c6*"], "dx": 0, "dy": 300, "dur": 0.5, "delay": 1.3},
        txt(960, 220, 96, "不是飞，是很贵的跳", 6, c="red", id="v"), pop(6, "v", 1.8),
        txt(960, 360, 52, "200 kg 空气 → 1 次跳", 6, c="gold")]
B.append(els)
boards = [{"elements": b} for b in B]

bad = missing_chars("".join(e.get("text", "") for b in B for e in b))
if bad:
    sys.exit(f"the fonts lack: {bad}")
if "--boards-only" in sys.argv:
    lesson = json.load(open(here / "lesson.json"))
    lesson["boards"] = boards
    json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
    sys.exit(print(len(boards), "boards"))

import sherpa_onnx as so  # noqa: E402
d = sys.argv[1].rstrip("/") + "/"
tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
    model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
    lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=2),
    rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1))
t, parts, segs, sr = 0.3, [], [], 24000
for i, (zh, en) in enumerate(S):
    a = tts.generate(speakable(zh), sid=49, speed=1.22); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.3), np.float32))
    segs.append({"zh": zh, "en": en, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    parts += [x, np.zeros(int(sr * 0.12), np.float32)]; t += len(x) / sr + 0.12
parts.append(np.zeros(int(sr * 1.0), np.float32)); t += 1.0
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson({"zh": "快节奏样段", "en": "Fast-paced sample"}, segs, boards, audio="配音.wav", duration=round(t, 2))
lesson.update(pace=0.32, hand=False, subs=True, ink=1.7, pan=0.45)
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", round(t, 1), "s")
