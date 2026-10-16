"""科普短片样片（MinutePhysics 式，第 36 轮讨论用）：果蝇大脑仿真，让虚拟果蝇自己动起来。
讲稿和画板手写（模拟“科普短片”风格的 AI 输出）；配音用平台同一套 Kokoro 声音，语速稍快；画得快（pace 0.55）、没有板书标题。
    python3 make.py <kokoro 模型目录> && python3 ../../../tools/whiteboard/wb.py . [--mp4]"""
import json, math, sys  # noqa: E401
from pathlib import Path
import numpy as np, soundfile as sf
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "services" / "gateway"))
from app.production.whiteboard import ai as wai
from app.production.whiteboard.speech import speakable
here = Path(__file__).resolve().parent

SEG = [
 "这是一只果蝇。对，就是总在你家香蕉上开派对的那位。",
 "它的大脑比一粒芝麻还小，却装着将近十四万个神经元。",
 "2024 年，科学家把这些神经元之间的连线，一根一根全画了出来：五千多万个连接。",
 "这张图叫“连接组”，相当于果蝇大脑的全套电路图。",
 "于是有人想：电路图都有了，能不能在电脑里，给它通上电？",
 "伯克利的团队真这么干了：用最简化的神经元，在一台笔记本电脑上跑整颗果蝇大脑。",
 "戳一下“尝到甜味”的神经元，模拟大脑就下令：伸嘴，开吃！",
 "戳一下“被碰到”的神经元，它就开始……整理仪容。",
 "2026 年，又有公司把这颗模拟大脑，接上了一个物理仿真的果蝇身体。",
 "结果，虚拟果蝇自己伸腿、搓脚、低头喝水。",
 "注意：没有人写过“请搓脚”这行代码。动作是从接线里冒出来的。",
 "不过，先别急着把自己上传。",
 "参数是调出来的；电路图里没有激素，也不会学习；这次演示当时还没有正式论文。",
 "而且，人脑的神经元，大约是果蝇的六十万倍。",
 "所以今天的结论是：电路图很重要，但它还不是灵魂。嗯……也许吧。",
]
EN = ["This is a fruit fly — yes, the one partying on your bananas.", "Its brain is smaller than a sesame seed, yet holds almost 140,000 neurons.",
 "In 2024 scientists mapped every wire between them: over 50 million connections.", "That map is the connectome — the fly brain's full circuit diagram.",
 "So someone asked: with the circuit diagram, can we switch it on in a computer?", "A Berkeley team did it: the simplest neurons, the whole fly brain, on a laptop.",
 "Poke the 'sweet taste' neurons and the model orders: tongue out, eat!", "Poke the 'touch' neurons and it starts… grooming.",
 "In 2026 a company connected this model brain to a physics-simulated fly body.", "And the virtual fly stretched its legs, rubbed its feet and drank.",
 "Note: nobody wrote a line of code saying 'rub feet'. It came out of the wiring.", "But don't upload yourself just yet.",
 "Parameters were tuned; no hormones, no learning in the map; no paper yet at the time.", "And a human brain has about 600,000 times as many neurons.",
 "So today's conclusion: the circuit diagram matters — but it is not a soul. Probably."]

# ---------------------------------------------------------------- drawing helpers (board coordinates 1920×1080)
def fly(cx, cy, k, at, idp="fly", legs_id=None):
    """A cartoon fly facing left: red eyes, two wings, six legs."""
    E = []
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx - 40 * k, "y": cy - 32 * k, "w": 80 * k, "h": 64 * k, "c": "ink"})        # thorax
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx + 30 * k, "y": cy - 30 * k, "w": 120 * k, "h": 62 * k, "c": "ink", "fill": "gold"})  # abdomen
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx - 82 * k, "y": cy - 26 * k, "w": 50 * k, "h": 48 * k, "c": "ink"})       # head
    E.append({"t": "ellipse", "at": at, "id": idp, "x": cx - 86 * k, "y": cy - 24 * k, "w": 24 * k, "h": 28 * k, "c": "red", "fill": "red"})  # eye
    for side in (-1, 1):                                                                                                       # wings
        E.append({"t": "path", "at": at, "id": idp + "_wings", "c": "blue", "w": 3,
                  "d": f"M{cx},{cy - 26 * k} Q{cx + 40 * k},{cy - (150 if side < 0 else 120) * k} {cx + (150 if side < 0 else 120) * k},{cy - (110 if side < 0 else 70) * k} "
                       f"Q{cx + 70 * k},{cy - 30 * k} {cx},{cy - 26 * k}"})
    for i, dx in enumerate((-30, 0, 30)):                                                                                      # legs
        x0 = cx + dx * k
        pts = [[x0, cy + 26 * k], [x0 + (-40 + 30 * i) * k, cy + 70 * k], [x0 + (-60 + 40 * i) * k, cy + 110 * k]]
        E.append({"t": "line", "at": at, "id": (legs_id if (legs_id and i == 0) else idp), "pts": pts, "c": "ink", "w": 3})
    return E

def stick(cx, cy, k, at, idp=None, arms="down"):
    """A stick person standing at (cx, cy) = feet level."""
    h = 200 * k
    E = [{"t": "ellipse", "at": at, "x": cx - 26 * k, "y": cy - h - 52 * k, "w": 52 * k, "h": 52 * k, "c": "ink"},
         {"t": "line", "at": at, "pts": [[cx, cy - h], [cx, cy - 80 * k]], "c": "ink", "w": 3.4},
         {"t": "line", "at": at, "pts": [[cx, cy - 80 * k], [cx - 40 * k, cy]], "c": "ink", "w": 3.4},
         {"t": "line", "at": at, "pts": [[cx, cy - 80 * k], [cx + 40 * k, cy]], "c": "ink", "w": 3.4}]
    if arms == "up":
        E.append({"t": "line", "at": at, "pts": [[cx - 60 * k, cy - h - 40 * k], [cx, cy - h + 30 * k], [cx + 60 * k, cy - h - 40 * k]], "c": "ink", "w": 3.4})
    else:
        E.append({"t": "line", "at": at, "pts": [[cx - 55 * k, cy - h + 90 * k], [cx, cy - h + 30 * k], [cx + 55 * k, cy - h + 90 * k]], "c": "ink", "w": 3.4})
    if idp:
        for e in E:
            e["id"] = idp
    return E

def network(cx, cy, r, at, n=13, seed=3, idp="net", c="ink"):
    """A tangle of neurons: dots joined by wires (the wires can carry a flow)."""
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(n):
        a, d = rng.uniform(0, 2 * math.pi), r * math.sqrt(rng.uniform(0.05, 1))
        pts.append((cx + d * math.cos(a), cy + 0.7 * d * math.sin(a)))
    E = []
    for i, (x, y) in enumerate(pts):
        near = sorted(range(n), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:4]
        for j in near:
            if j > i or i not in [k for k in sorted(range(n), key=lambda q: (pts[q][0] - pts[j][0]) ** 2 + (pts[q][1] - pts[j][1]) ** 2)[1:4]]:
                E.append({"t": "line", "at": at, "id": idp + "_w", "pts": [[x, y], list(pts[j])], "c": "blue", "w": 2.4})
    for x, y in pts:
        E.append({"t": "ellipse", "at": at, "id": idp, "x": x - 11, "y": y - 11, "w": 22, "h": 22, "c": c, "fill": "gold"})
    return E

def txt(x, y, s, text, at, c="ink", align="center", font="zh", **kw):
    return {"t": "text", "at": at, "x": x, "y": y, "s": s, "text": text, "c": c, "align": align, "font": font, **kw}

def bubble(x, y, w, h, at, text, s=44, c="ink"):
    return [{"t": "path", "at": at, "c": c, "w": 3,
             "d": f"M{x + 30},{y} L{x + w - 30},{y} Q{x + w},{y} {x + w},{y + 30} L{x + w},{y + h - 30} Q{x + w},{y + h} {x + w - 30},{y + h} "
                  f"L{x + 90},{y + h} L{x + 40},{y + h + 50} L{x + 55},{y + h} L{x + 30},{y + h} Q{x},{y + h} {x},{y + h - 30} L{x},{y + 30} Q{x},{y} {x + 30},{y}"},
            txt(x + w / 2, y + h / 2 + s * 0.36, s, text, at, c=c)]

banana = "M290,760 Q360,880 560,850 Q640,830 660,770 L680,760 L668,790 Q620,800 560,805 Q420,820 340,750 Z"
B = []
# 1 · 这是一只果蝇
els = fly(960, 470, 2.2, 0)
els += [{"t": "path", "at": 0, "c": "gold", "w": 4, "d": banana},
        {"t": "path", "at": 0, "c": "red", "w": 4, "fill": None, "d": "M770,420 L800,300 L850,410 Z"},           # party hat
        txt(450, 980, 40, "派对现场", 0, c="muted")]
els += [{"t": "move", "at": 0, "kind": "pulse", "targets": ["fly_wings"]}]
B.append(els)
# 2 · 芝麻大的脑，14 万个神经元
els = fly(360, 520, 1.1, 1, idp="fly2")
els += [{"t": "ellipse", "at": 1, "x": 268, "y": 486, "w": 40, "h": 36, "c": "red", "fill": "red"},
        {"t": "arrow", "at": 1, "pts": [[300, 470], [560, 330]], "c": "muted", "w": 3},
        {"t": "ellipse", "at": 1, "x": 600, "y": 270, "w": 60, "h": 42, "c": "gold", "fill": "gold"},
        txt(630, 380, 34, "芝麻", 1, c="muted"),
        txt(780, 310, 64, "大脑 < 芝麻", 1, align="left"),
        txt(1300, 620, 120, "≈ 140,000", 1, c="red"),
        txt(1300, 710, 44, "个神经元", 1)]
B.append(els)
# 3 · 连接组
els = network(800, 540, 440, 2, n=24, idp="net")
els += [txt(1500, 360, 80, "5000 万", 2, c="red"), txt(1500, 430, 40, "个连接", 2),
        txt(1500, 640, 56, "连接组", 3, c="blue"), txt(1500, 700, 30, "connectome", 3, c="muted", font="en"),
        txt(1500, 790, 40, "= 全套电路图", 3),
        {"t": "move", "at": 3, "kind": "flow", "targets": ["net_w"], "speed": 1.2}]
B.append(els)
# 4 · 通上电？笔记本电脑
els = network(560, 470, 230, 4, n=10, seed=5, idp="net2")
els += [{"t": "path", "at": 4, "c": "ink", "w": 4, "d": "M800,470 L900,470 M900,440 L960,440 L960,500 L900,500 Z M960,452 L1000,452 M960,488 L1000,488"},   # plug
        txt(560, 820, 60, "通上电？", 4, c="red"),
        {"t": "icon", "at": 5, "name": "computer", "x": 1380, "y": 470, "size": 380, "c": "ink"},
        txt(1380, 470, 36, "整颗果蝇大脑", 5, c="blue"),
        txt(1380, 760, 40, "伯克利 2024 · 最简化的神经元", 5),
        txt(1380, 820, 34, "（一台笔记本就够了）", 5, c="muted"),
        {"t": "move", "at": 4, "kind": "pulse", "targets": ["net2"]}]
B.append(els)
# 5 · 戳一下：甜 → 开吃；触 → 整理仪容
els = [txt(480, 300, 48, "戳“甜味”神经元", 6, c="gold")]
els += fly(480, 600, 1.2, 6, idp="fly3")
els += bubble(560, 330, 360, 120, 6, "伸嘴，开吃！", s=46, c="red")
els += [txt(1440, 300, 48, "戳“触觉”神经元", 7, c="blue")]
els += fly(1440, 600, 1.2, 7, idp="fly4", legs_id="fly4_legs")
els += [txt(1440, 860, 44, "……整理仪容", 7, c="muted"),
        {"t": "move", "at": 7, "kind": "rotate", "targets": ["fly4_legs"], "pivot": [1404, 631], "to": 25, "dur": 0.6},
        {"t": "move", "at": 7, "kind": "pulse", "targets": ["fly3"]}]
B.append(els)
# 6 · 大脑接上身体，自己动起来
els = network(340, 500, 200, 8, n=9, seed=8, idp="net3")
els += [txt(340, 760, 40, "模拟大脑", 8, c="blue"),
        {"t": "arrow", "at": 8, "pts": [[600, 500], [860, 500]], "c": "red", "w": 4},
        txt(730, 470, 30, "接上", 8, c="red")]
els += fly(1260, 500, 2.0, 8, idp="fly5", legs_id="fly5_legs")
els += [txt(1260, 800, 40, "物理仿真的身体", 8),
        txt(1260, 860, 30, "NeuroMechFly · 2026", 8, c="muted", font="en"),
        {"t": "move", "at": 9, "kind": "rotate", "targets": ["fly5_legs"], "pivot": [1200, 552], "to": 30, "dur": 0.5},
        {"t": "move", "at": 9, "kind": "pulse", "targets": ["fly5_wings"]},
        {"t": "move", "at": 8, "kind": "flow", "targets": ["net3_w"]},
        txt(560, 980, 34, "伸腿 · 搓脚 · 喝水", 9, c="green")]
B.append(els)
# 7 · 没人写过“请搓脚”
els = [txt(960, 420, 64, "rub_feet()", 10, c="ink", font="en"),
       {"t": "line", "at": 10, "pts": [[760, 400], [1170, 400]], "c": "red", "w": 6},
       txt(960, 600, 52, "没有这行代码", 10, c="red"),
       txt(960, 720, 52, "动作是从“接线”里冒出来的", 10, c="green")]
B.append(els)
# 8 · 先别急着上传
els = stick(420, 760, 1.4, 11, idp="me", arms="up")
els += [{"t": "rect", "at": 11, "x": 640, "y": 300, "w": 260, "h": 360, "c": "muted"}, txt(770, 520, 44, "上传", 11, c="muted"),
        {"t": "line", "at": 11, "pts": [[640, 300], [900, 660]], "c": "red", "w": 6}, {"t": "line", "at": 11, "pts": [[900, 300], [640, 660]], "c": "red", "w": 6}, txt(1150, 280, 56, "先别急！", 11, c="red", align="left"),
        txt(1150, 440, 40, "· 参数是调出来的", 12, align="left"),
        txt(1150, 540, 40, "· 没有激素，也不会学习", 12, align="left"),
        txt(1150, 640, 40, "· 当时还没有正式论文", 12, align="left"),
        {"t": "move", "at": 11, "kind": "shift", "targets": ["me"], "dx": -80, "dy": 0, "dur": 0.6}]
B.append(els)
# 9 · 人脑 = 果蝇 × 60 万
els = [{"t": "ellipse", "at": 13, "x": 300, "y": 600, "w": 22, "h": 22, "c": "gold", "fill": "gold"},
       txt(311, 680, 34, "果蝇", 13, c="muted"),
       {"t": "ellipse", "at": 13, "x": 520, "y": 200, "w": 760, "h": 700, "c": "blue"},
       txt(900, 560, 60, "人脑", 13, c="blue"),
       txt(1560, 500, 64, "× 600,000", 13, c="red")]
B.append(els)
# 10 · 结论
els = [txt(960, 460, 72, "电路图 ≠ 灵魂", 14),
       txt(960, 620, 52, "……也许吧", 14, c="muted"),
       {"t": "icon", "at": 14, "name": "question", "id": "q", "x": 1400, "y": 600, "size": 140, "c": "gold"},
       {"t": "move", "at": 14, "kind": "pulse", "targets": ["q"]}]
B.append(els)
boards = [{"elements": e} for e in B]

if "--boards-only" in sys.argv:          # keep the voice, lay the boards out again
    lesson = json.load(open(here / "lesson.json"))
    lesson["boards"] = boards
    json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
    sys.exit(print(len(boards), "boards"))
# ---------------------------------------------------------------- voice (the platform's Kokoro voice, a little faster)
import sherpa_onnx as so
d = sys.argv[1].rstrip("/") + "/"
tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
    model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
    lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=2),
    rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1))
t, parts, segs, sr = 0.4, [], [], 24000
for zh, en in zip(SEG, EN):
    spoken = speakable(zh).replace("2024", "二零二四").replace("2026", "二零二六")
    a = tts.generate(spoken, sid=49, speed=1.12); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.4), np.float32))
    segs.append({"zh": zh, "en": en, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    parts += [x, np.zeros(int(sr * 0.25), np.float32)]; t += len(x) / sr + 0.25
parts.append(np.zeros(int(sr * 1.2), np.float32)); t += 1.2
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson({"zh": "果蝇大脑，自己动起来", "en": "A fly brain that moves on its own"}, segs, boards, audio="配音.wav", duration=round(t, 2))
lesson["pace"] = 0.55
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
