"""科普短片样片第 2 版《电脑里的那只果蝇，痒吗？》（Eddie 22:06–22:11：“不够烧脑，也不幽默”“可以把手拿掉”
“果蝇动起来，可爱点”“通电的比喻不恰当、到处短路”“三分钟够了”）。
一个问题贯穿全片、三次反转、一个贯穿的梗（馋嘴的果蝇）；神经元的计算用“传纸条”比喻（攒够了就往下传）；
没有手，画面自己出来；果蝇会扇翅膀、悬停。
    python3 make.py <kokoro 模型目录> [--boards-only] && python3 ../../../tools/whiteboard/wb.py . [--mp4]"""
import json, sys  # noqa: E401
from pathlib import Path
import numpy as np, soundfile as sf  # noqa: E401
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[2] / "services" / "gateway"))
sys.path.insert(0, str(here.parent))
from app.production.whiteboard import ai as wai  # noqa: E402
from app.production.whiteboard.core import missing_chars  # noqa: E402
from app.production.whiteboard.speech import speakable  # noqa: E402
from popkit import bubble, cute_fly, network, stick, txt  # noqa: E402

SEG = [
 "假设我把你大脑里的每一根线，原样抄进电脑。电脑里那个，是你吗？",
 "先别回答。这个问题太贵了，我们先拿一个便宜点的大脑试试。",
 "果蝇。十四万个神经元。比你朋友圈的点赞还少。",
 "但它们之间有五千万个连接。科学家花了好几年，一根一根画了出来。",
 "相当于把一碗面里每根面条的走向都记下来，还要记清哪根和哪根粘在一起。",
 "这张图叫“连接组”。2024 年，一整只成年果蝇的大脑，第一次画全了。",
 "接下来最大胆的一步：不去猜它在想什么，只让电脑照着这张图，算一算消息怎么传。",
 "每个神经元的规矩只有一条：收到的消息攒够了，就往下家传一条。",
 "想象十四万个同学，照着座位表传纸条。谁收到的纸条够多，谁就往下传。",
 "规矩就这么简单，简单得有点像在偷懒。",
 "结果呢？戳一下“尝到甜味”的那几个同学，纸条一路传到管伸嘴的同学。电脑里的果蝇，馋了。",
 "更神的是：电脑先猜哪些神经元管“吃”，科学家再去真果蝇身上验证。猜中了一大片。",
 "一个连“想”都不会的模拟，开始给生物学家出题了。",
 "后来，有人把这颗模拟大脑接上一个虚拟身体。它开始自己搓脚。",
 "没有人写过“搓脚”这行代码。搓脚，就藏在那碗面条里。",
 "好，烧脑的来了：它搓脚的时候……痒吗？",
 "线路图能告诉你它会搓脚，却说不清它痒不痒。哲学家吵了几百年的问题，被一只果蝇摆到了程序员的桌上。",
 "再烧一点：把这只数字果蝇复制一份。同一份线路，同一秒开机。",
 "它们会一直一模一样，直到你多戳了其中一只一下。",
 "从那一刻起，它们就是两只果蝇了。那“我”，到底是线路，还是线路上跑过的那些经历？",
 "最后一个：把一只真果蝇的神经元，一个一个换成芯片。",
 "换一个，它还是果蝇。换一半呢？换到最后一个呢？它是从哪一个开始，不再是它自己的？",
 "友情提示：这个模型的参数是调出来的，线路图里也没有激素和学习；人脑的神经元还是它的六十万倍。上传你，还早。",
 "回到开头：电脑里那个你，是你吗？我不知道。但我可以保证一件事：它也会半夜想吃宵夜。",
]

def tag(x, y, at, top, bottom, c):
    """A price tag with a hole."""
    return [{"t": "path", "at": at, "c": c, "w": 4, "d": f"M{x},{y} L{x + 320},{y} L{x + 400},{y + 110} L{x + 320},{y + 220} L{x},{y + 220} Z"},
            {"t": "ellipse", "at": at, "x": x + 330, "y": y + 96, "w": 28, "h": 28, "c": c},
            txt(x + 160, y + 90, 52, top, at, c=c), txt(x + 160, y + 170, 40, bottom, at, c="muted")]

def bowl(cx, cy, at, k=1.0, idp="bowl"):
    E = [{"t": "path", "at": at, "id": idp, "c": "ink", "w": 4, "d": f"M{cx - 260 * k},{cy} Q{cx},{cy + 300 * k} {cx + 260 * k},{cy} Z"}]
    for i in range(7):
        x0 = cx - 210 * k + i * 70 * k
        d = f"M{x0},{cy + 20 * k}"
        for j in range(5):
            d += f" Q{x0 + (30 if j % 2 else -30) * k},{cy - 40 * k - j * 45 * k} {x0 + (8 * (i - 3)) * k},{cy - 70 * k - j * 45 * k}"
        E.append({"t": "path", "at": at, "id": idp, "c": "gold", "w": 3.4, "d": d})
    return E

def computer(cx, cy, at, size=420, idp=None):
    e = {"t": "icon", "at": at, "name": "computer", "x": cx, "y": cy, "size": size, "c": "ink"}
    if idp:
        e["id"] = idp
    return [e]

def classroom(x0, y0, cols, rows, gap, at, chain, idp="cls", label_first="", label_last=""):
    """Little heads in seats; a note runs from head to head along `chain` (seat indices)."""
    E, pos = [], []
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * gap, y0 + r * gap * 0.8
            pos.append((x, y))
    # a row of heads is one quick stroke (a classroom appears in a moment, not seat by seat)
    for r in range(rows):
        d = ""
        for c in range(cols):
            x, y = pos[r * cols + c]
            d += (f"M{x - 28},{y} a28,28 0 1,0 56,0 a28,28 0 1,0 -56,0 "
                  f"M{x - 12},{y - 4} a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 M{x + 6},{y - 4} a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 ")
        E.append({"t": "path", "at": at, "c": "ink", "w": 3, "d": d.strip()})
    for a, b in zip(chain, chain[1:]):
        (xa, ya), (xb, yb) = pos[a], pos[b]
        E.append({"t": "line", "at": at, "id": idp + "_note", "pts": [[xa, ya + 30], [xb, yb + 30]], "c": "muted", "w": 2})
    if label_first:
        E.append(txt(pos[chain[0]][0], pos[chain[0]][1] - 48, 32, label_first, at, c="gold"))
    if label_last:
        E.append(txt(pos[chain[-1]][0], pos[chain[-1]][1] + 92, 32, label_last, at, c="red"))
    E.append({"t": "move", "at": at, "kind": "signal", "targets": [idp + "_note"], "speed": 380})
    return E

def keyboard(x, y, at):
    E = [{"t": "rect", "at": at, "x": x, "y": y, "w": 520, "h": 160, "c": "ink"}]
    E += [{"t": "rect", "at": at, "x": x + 22 + 62 * (i % 8), "y": y + 20 + 48 * (i // 8), "w": 46, "h": 34, "c": "muted"} for i in range(24)]
    return E

B = []
# 0 · 抄进电脑，是你吗？
els = stick(380, 820, 1.6, 0, idp="you")
els += network(380, 340, 80, 0, n=8, seed=2, idp="head")
els += [{"t": "arrow", "at": 0, "pts": [[640, 540], [940, 540]], "c": "red", "w": 5}, txt(790, 500, 36, "原样抄", 0, c="red")]
els += computer(1380, 520, 0, 560)
els += stick(1380, 640, 0.75, 0, idp="you2", arms="up")
els += [txt(1380, 900, 64, "是你吗？", 0, c="blue"), {"t": "move", "at": 0, "kind": "bob", "targets": ["you2"], "amp": 10, "hz": 1.6}]
B.append(els)
# 1 · 太贵了，先拿便宜的
els = tag(260, 380, 1, "人脑", "非卖品", "blue") + tag(1160, 380, 1, "果蝇脑", "特价", "red")
els += [txt(960, 820, 44, "先拿便宜的试试", 1, c="muted")]
B.append(els)
# 2 · 十四万，比点赞还少
els = cute_fly(640, 560, 1.8, 2, idp="f1")
els += [{"t": "line", "at": 2, "pts": [[1010, 760], [1010, 330]], "c": "ink", "w": 4},
        {"t": "rect", "at": 2, "x": 900, "y": 220, "w": 400, "h": 130, "c": "ink"},
        txt(1100, 305, 52, "我尽力了", 2),
        txt(1560, 600, 96, "140,000", 2, c="red"), txt(1560, 680, 40, "个神经元", 2),
        txt(1560, 790, 32, "（比你朋友圈的点赞还少）", 2, c="muted")]
B.append(els)
# 3-4 · 五千万个连接 = 一碗面
els = bowl(700, 620, 3)
els += [txt(1420, 420, 90, "5000 万", 3, c="red"), txt(1420, 500, 40, "个连接", 3), txt(1420, 640, 40, "一根一根画出来", 3, c="muted")]
for i, (x, y) in enumerate([(520, 500), (640, 420), (780, 380), (880, 470)]):
    els += [{"t": "ellipse", "at": 4, "x": x - 26, "y": y - 26, "w": 52, "h": 52, "c": "blue"}, txt(x, y + 14, 34, str(i + 1), 4, c="blue", font="en")]
els += [{"t": "arrow", "at": 4, "pts": [[1100, 300], [930, 360]], "c": "blue", "w": 3}, txt(1120, 290, 36, "这两根粘一起", 4, c="blue", align="left")]
B.append(els)
# 5 · 连接组，第一次画全
els = network(760, 540, 440, 5, n=26, seed=4, idp="map")
els += [txt(1500, 440, 80, "连接组", 5, c="blue"), txt(1500, 510, 34, "connectome", 5, c="muted", font="en"),
        txt(1500, 640, 40, "2024 · 第一次画全", 5)]
els += cute_fly(1560, 880, 0.7, 5, idp="f2", mood="o")
B.append(els)
# 6-7 · 照着图算消息怎么传；规矩只有一条
els = computer(560, 480, 6, 640)
els += network(560, 440, 160, 6, n=9, seed=9, idp="m2")
els += [txt(560, 860, 40, "不猜它在想什么，只算消息怎么传", 6, c="muted"),
        {"t": "rect", "at": 7, "x": 1120, "y": 330, "w": 640, "h": 300, "c": "gold"},
        txt(1440, 420, 44, "每个神经元的规矩", 7, c="gold"),
        txt(1440, 520, 48, "攒够了，就往下传", 7, c="ink"),
        {"t": "arrow", "at": 7, "pts": [[1300, 580], [1580, 580]], "c": "red", "w": 4}]
B.append(els)
# 8-9 · 十四万个同学传纸条
els = classroom(480, 360, 5, 3, 240, 8, [10, 11, 6, 7, 2, 3, 4], idp="c1")
els += [txt(960, 200, 52, "照着座位表传纸条", 8, c="blue"),
        txt(1660, 960, 36, "（规矩简单得像偷懒）", 9, c="muted")]
B.append(els)
# 10 · 甜 → 伸嘴，馋了
els = classroom(260, 400, 5, 3, 190, 10, [10, 11, 6, 7, 2, 3, 4], idp="c2", label_first="尝到甜", label_last="")
els += [{"t": "arrow", "at": 10, "pts": [[1060, 400], [1230, 470]], "c": "red", "w": 4}, txt(1100, 360, 34, "伸嘴！", 10, c="red", align="left")]
els += cute_fly(1500, 620, 1.6, 10, idp="f3", mood="drool")
els += bubble(1600, 170, 220, 120, 10, "馋！", s=60, c="red")
B.append(els)
# 11-12 · 电脑先猜，真果蝇验证
els = computer(420, 460, 11, 460)
els += [txt(420, 470, 48, "我猜：", 11, c="blue"), txt(420, 780, 40, "这几个管“吃”", 11, c="blue"),
        {"t": "arrow", "at": 11, "pts": [[720, 460], [1000, 460]], "c": "ink", "w": 4}]
els += cute_fly(1300, 520, 1.3, 11, idp="f4")
els += [{"t": "icon", "at": 11, "name": "magnifier", "x": 1180, "y": 380, "size": 220, "c": "ink"},
        {"t": "icon", "at": 11, "name": "check", "id": "ok", "x": 1600, "y": 360, "size": 200, "c": "green"},
        txt(1460, 820, 40, "真果蝇：猜中一大片", 11, c="green"),
        txt(960, 980, 44, "模拟开始给生物学家出题了", 12, c="red"),
        {"t": "move", "at": 11, "kind": "pulse", "targets": ["ok"]}]
B.append(els)
# 13-14 · 虚拟身体，自己搓脚；没人写这行代码
els = cute_fly(560, 520, 2.2, 13, idp="f5")
els += [txt(560, 920, 44, "虚拟身体 · 自己搓脚", 13, c="blue"),
        {"t": "move", "at": 13, "kind": "wiggle", "targets": ["f5_legs"], "pivot": [560, 620], "amp": 8, "hz": 3},
        txt(1400, 330, 64, "rub_feet()", 14, font="en"),
        {"t": "line", "at": 14, "pts": [[1200, 310], [1610, 310]], "c": "red", "w": 6},
        txt(1400, 450, 44, "没有这行代码", 14, c="red")]
els += bowl(1400, 700, 14, k=0.55, idp="bowl2")
els += [txt(1400, 920, 40, "它藏在面条里", 14, c="green")]
B.append(els)
# 15 · 痒吗？
els = cute_fly(680, 580, 2.4, 15, idp="f6", mood="o")
els += [{"t": "move", "at": 15, "kind": "wiggle", "targets": ["f6_legs"], "pivot": [680, 700], "amp": 8, "hz": 3},
        {"t": "icon", "at": 15, "id": "q", "name": "question", "x": 1400, "y": 460, "size": 420, "c": "red"},
        txt(1400, 860, 80, "它痒吗？", 15, c="red"),
        {"t": "move", "at": 15, "kind": "pulse", "targets": ["q"]}]
B.append(els)
# 16 · 哲学家吵了几百年 → 程序员的桌上
els = []
for i, (x, said) in enumerate([(260, "会！"), (560, "不会！"), (860, "先定义“痒”")]):
    els += stick(x, 760, 1.0, 16, arms="up" if i == 1 else "down")
    els += bubble(x - 60, 300 - (i % 2) * 40, 120 + 46 * len(said), 100, 16, said, s=34)
els += [txt(560, 900, 36, "哲学家 · 几百年", 16, c="muted")]
els += keyboard(1240, 640, 16)
els += cute_fly(1500, 480, 0.9, 16, idp="f7")
els += [txt(1500, 900, 36, "程序员的桌上", 16, c="muted")]
B.append(els)
# 17-19 · 复制一份；多戳一下；两条路
els = cute_fly(420, 400, 1.2, 17, idp="fa") + cute_fly(1000, 400, 1.2, 17, idp="fb")
els += [txt(710, 640, 44, "同一份线路 · 同一秒开机", 17, c="blue"),
        {"t": "arrow", "at": 18, "pts": [[1300, 180], [1110, 330]], "c": "red", "w": 5}, txt(1320, 170, 40, "戳！", 18, c="red", align="left"),
        {"t": "move", "at": 18, "kind": "shift", "targets": ["fb*"], "dx": 60, "dy": -30, "dur": 0.3},
        {"t": "path", "at": 19, "c": "ink", "w": 4, "d": "M700,1040 L700,880 Q700,820 600,780 L380,700"},
        {"t": "path", "at": 19, "c": "ink", "w": 4, "d": "M760,1040 L760,880 Q760,820 860,780 L1080,700"},
        txt(1460, 800, 60, "“我”是线路？", 19, c="blue"), txt(1460, 920, 60, "还是经历？", 19, c="gold")]
B.append(els)
# 20-21 · 一个一个换成芯片
els = cute_fly(520, 560, 2.0, 20, idp="f8")
els += [{"t": "icon", "at": 20, "name": "chip", "x": 1000, "y": 300, "size": 160, "c": "blue"},
        {"t": "arrow", "at": 20, "pts": [[920, 340], [640, 420]], "c": "blue", "w": 4}]
for i, (lab, x) in enumerate((("换一个", 1100), ("换一半", 1380), ("换完", 1660))):
    els += [{"t": "icon", "at": 21, "name": "chip", "x": x, "y": 620, "size": 90 + 50 * i, "c": "blue"}, txt(x, 780, 40, lab, 21)]
els += [txt(1380, 920, 52, "从哪一个开始，它不再是它？", 21, c="red")]
B.append(els)
# 22 · 友情提示
els = [{"t": "ellipse", "at": 22, "x": 300, "y": 640, "w": 20, "h": 20, "c": "gold", "fill": "gold"}, txt(310, 720, 32, "果蝇", 22, c="muted"),
       {"t": "ellipse", "at": 22, "x": 420, "y": 240, "w": 640, "h": 600, "c": "blue"}, txt(740, 560, 56, "人脑 ×60 万", 22, c="blue"),
       txt(1180, 300, 48, "友情提示", 22, c="red", align="left"),
       txt(1180, 420, 38, "· 参数是调出来的", 22, align="left"),
       txt(1180, 500, 38, "· 没有激素，也不会学习", 22, align="left"),
       txt(1180, 640, 56, "上传你，还早。", 22, c="green", align="left")]
B.append(els)
# 23 · 它也会半夜想吃宵夜
els = computer(560, 520, 23, 620)
els += stick(560, 640, 0.75, 23, idp="you3")
els += [{"t": "rect", "at": 23, "x": 1180, "y": 260, "w": 360, "h": 620, "c": "ink"},
        {"t": "line", "at": 23, "pts": [[1180, 520], [1540, 520]], "c": "ink", "w": 3},
        {"t": "path", "at": 23, "c": "ink", "w": 4, "d": "M1540,260 L1700,320 L1700,820 L1540,880"}]
els += cute_fly(1360, 440, 0.7, 23, idp="f9", mood="drool")
els += bubble(1300, 100, 300, 110, 23, "宵夜！", s=48, c="red")
els += [txt(960, 1010, 40, "（凌晨 2:00）", 23, c="muted")]
B.append(els)
boards = [{"elements": e} for e in B]

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
t, parts, segs, sr = 0.4, [], [], 24000
PAUSE = {0: 0.9, 2: 0.5, 9: 0.5, 12: 0.6, 14: 0.6, 15: 0.9, 18: 0.5, 21: 0.9, 22: 0.6}      # a beat after the punchlines
for i, zh in enumerate(SEG):
    a = tts.generate(speakable(zh), sid=49, speed=1.12); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.4), np.float32))
    segs.append({"zh": zh, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    gap = PAUSE.get(i, 0.25)
    parts += [x, np.zeros(int(sr * gap), np.float32)]; t += len(x) / sr + gap
parts.append(np.zeros(int(sr * 1.2), np.float32)); t += 1.2
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson({"zh": "电脑里的那只果蝇，痒吗？", "en": "Does the fly in the computer itch?"}, segs, boards, audio="配音.wav", duration=round(t, 2))
lesson["pace"], lesson["hand"] = 0.5, False
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
