"""每日科普 2026-10-16（中文）《一只眼的无人机，凭什么赢了世界冠军？》
新闻：荷兰代尔夫特理工大学 MonoRace 自主竞速无人机，时速约 100 公里，2025 年阿布扎比自主无人机竞速赛击败其他自主队伍和
3 名曾获世界冠军的人类飞手；只用一个前置摄像头 + IMU + 无人机模型估计状态，小神经网络直接出电机指令（每秒 500 次），强化学习训练；
论文刊于《科学·机器人》（科技日报 2026-10-15、澎湃新闻、新浪财经转载）。
推测/常识（片中已说明）：人的反应约 0.2 秒（一般数值）；“门越大越近”是举例说明单目怎么看远近；训练“一般在模拟器里”。
固定角色“小飞”（popkit.cute_drone，一只眼的无人机）。没有手。
    python3 make.py <kokoro 模型目录> | --fake | --boards-only   然后  python3 ../../../../tools/whiteboard/wb.py . [--mp4]"""
import json, sys  # noqa: E401
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[3] / "services" / "gateway"))
sys.path.insert(0, str(here.parents[1]))
from app.production.whiteboard import ai as wai  # noqa: E402
from app.production.whiteboard.core import missing_chars  # noqa: E402
from app.production.whiteboard.speech import speakable  # noqa: E402
from popkit import bubble, cute_drone, network, stick, txt  # noqa: E402

SEG = [
 "一架无人机，以每小时一百公里的速度穿过一道道门，把三位人类世界冠军甩在了身后。",
 "开它的不是人，是机身上一块小小的芯片。",
 "它叫 MonoRace，来自荷兰代尔夫特理工大学，论文刚登上《科学·机器人》。比赛是 2025 年在阿布扎比打的。",
 "问题来了：人类冠军练了很多年，反应快得吓人，为什么会输给一块芯片？",
 "更气人的是，它只有一只眼睛。",
 "先算一笔账。每小时一百公里，就是每秒差不多二十八米。",
 "人看到东西再动手，一般要零点二秒左右。这零点二秒里，无人机已经冲出去五米多。",
 "相当于闭着眼，飞过一辆多小汽车那么长。",
 "芯片呢？每秒发五百次指令。两次指令之间，它只飞了五厘米多。",
 "人像一个隔一会儿看一眼路的司机；芯片是一直盯着路、方向盘一直在微调的司机。这是原因一。",
 "原因二：它不玩传话游戏。传统飞控一层一层往下传：一个负责看，一个负责规划路线，一个负责算电机怎么转。",
 "传话的人越多，越慢，也越容易走样。",
 "MonoRace 把中间人全裁了：一个小小的神经网络，看完直接告诉四个电机，各转多快。",
 "它是怎么学会的？强化学习：飞得又快又稳加分，撞了扣分。这类训练一般在电脑里的模拟赛道上进行。",
 "撞多少次都不心疼，反正撞的是电脑里的那架。",
 "原因三，最反直觉：只有一只眼，反而够用。",
 "一只眼看不出远近？其实能。比如门的大小是定的，看起来越大，就离得越近。",
 "再加上一个惯性测量单元，就像你的内耳，闭上眼也知道自己在加速、在转弯。",
 "眼睛偶尔没看清，内耳先顶上；眼睛再看到门，就把误差拉回来。",
 "再烧一点：人类飞手戴着眼镜，看的其实也是无人机上一个摄像头的画面。",
 "所以这场比赛，是一只眼对一只眼。差别在于，人和电机之间隔着眼睛、大脑、手指和遥控器；芯片和电机之间，什么都没隔。",
 "这有什么用？团队说，同样的思路，以后能让扫地机器人走得更稳、更省电，甚至用在码头的大吊车上。",
 "友情提示：比赛的赛道和门都是定好的。换到一片乱糟糟的树林里，它还能不能赢，还不知道。",
 "所以人类飞手先别急着退休。不过下次比赛前，建议多练一项：别眨眼。",
]
SAY = {"MonoRace": "Mono Race", "2025": "二零二五"}


def gate(x, y, s, at, c="gold", idp=None):
    e = {"t": "rect", "at": at, "x": x - s / 2, "y": y - s / 2, "w": s, "h": s, "c": c}
    if idp:
        e["id"] = idp
    return [e, {"t": "rect", "at": at, "x": x - s / 2 + 10, "y": y - s / 2 + 10, "w": s - 20, "h": s - 20, "c": c}]


def pilot(cx, cy, k, at, idp=None):
    """A stick-figure pilot wearing FPV goggles."""
    E = stick(cx, cy, k, at, idp=idp, arms="down")
    E.append({"t": "rect", "at": at, "x": cx - 36 * k, "y": cy - 240 * k, "w": 72 * k, "h": 26 * k, "c": "ink", "fill": "ink", **({"id": idp} if idp else {})})
    return E


B = []
# 0-1 · 一道道门，100 km/h，三位世界冠军；开它的是芯片
els = [txt(960, 150, 72, "100 km/h", 0, c="red", font="en")]
for i, (x, s) in enumerate(((420, 300), (820, 240), (1180, 190), (1500, 150))):
    els += gate(x, 420, s, 0)
els += cute_drone(220, 420, 0.6, 0, idp="d0")
els += [{"t": "move", "at": 0, "kind": "shift", "targets": ["d0*"], "dx": 1450, "dy": 0, "dur": 4, "delay": 1}]
for i in range(3):
    els += pilot(300 + i * 150, 960, 0.7, 0)
els += [txt(450, 1040, 36, "3 位人类世界冠军", 0, c="muted"),
        {"t": "icon", "at": 1, "id": "chip1", "name": "chip", "x": 1420, "y": 800, "size": 200, "c": "blue"},
        txt(1420, 1000, 44, "开它的：一块小芯片", 1, c="blue"), {"t": "move", "at": 1, "kind": "pulse", "targets": ["chip1"]}]
B.append(els)
# 2-4 · MonoRace；为什么会输？只有一只眼
els = [txt(960, 190, 96, "MonoRace", 2, c="blue", font="en"),
       txt(960, 280, 38, "荷兰代尔夫特理工大学 · 《科学·机器人》", 2, c="muted"),
       txt(960, 340, 34, "2025 · 阿布扎比 · 自主无人机竞速赛", 2, c="muted")]
els += pilot(460, 900, 1.2, 3)
els += [{"t": "icon", "at": 3, "id": "q3", "name": "question", "x": 960, "y": 640, "size": 240, "c": "red"},
        {"t": "move", "at": 3, "kind": "pulse", "targets": ["q3"]}, txt(960, 860, 48, "为什么会输？", 3, c="red")]
els += cute_drone(1450, 640, 1.2, 3, idp="d3")
els += [txt(1450, 880, 48, "而且……只有一只眼", 4, c="gold"), {"t": "move", "at": 4, "kind": "pulse", "targets": ["d3_eye"]}]
B.append(els)
# 5-7 · 28 米/秒；0.2 秒冲出 5 米多；闭眼飞过一辆多小汽车
els = [txt(960, 200, 64, "100 km/h ≈ 每秒 28 米", 5, c="blue")]
els += cute_drone(300, 480, 0.5, 6, idp="d6")
els += [{"t": "move", "at": 6, "kind": "shift", "targets": ["d6*"], "dx": 1300, "dy": 0, "dur": 2.5, "delay": 1.5},
        {"t": "line", "at": 6, "pts": [[300, 620], [1600, 620]], "c": "red", "w": 4},
        {"t": "line", "at": 6, "pts": [[300, 595], [300, 645]], "c": "red", "w": 4},
        {"t": "line", "at": 6, "pts": [[1600, 595], [1600, 645]], "c": "red", "w": 4},
        txt(950, 700, 48, "人反应约 0.2 秒 → 冲出 5 米多", 6, c="red"),
        {"t": "icon", "at": 7, "name": "car", "x": 950, "y": 860, "size": 340, "c": "muted"},
        txt(1480, 900, 40, "（闭着眼）", 7, c="muted")]
B.append(els)
# 8-9 · 500 次/秒，5 厘米；两种司机
els = [txt(960, 190, 80, "每秒 500 次", 8, c="green"), txt(960, 270, 40, "两次之间只飞 5 厘米多", 8, c="muted"),
       {"t": "line", "at": 8, "pts": [[300, 360], [1620, 360]], "c": "ink", "w": 2}]
els += [{"t": "line", "at": 8, "pts": [[300 + i * 33, 340], [300 + i * 33, 380]], "c": "green", "w": 2} for i in range(41)]
els += [{"t": "icon", "at": 9, "name": "eye", "x": 520, "y": 620, "size": 200, "c": "muted"},
        txt(520, 800, 40, "人：隔一会儿看一眼", 9), txt(520, 860, 34, "看……　　　　看……", 9, c="muted"),
        {"t": "icon", "at": 9, "id": "eye9", "name": "eye", "x": 1400, "y": 620, "size": 200, "c": "green"},
        {"t": "move", "at": 9, "kind": "pulse", "targets": ["eye9"]},
        txt(1400, 800, 40, "芯片：一直盯，一直调", 9, c="green"), txt(960, 990, 44, "原因一：快", 9, c="blue")]
B.append(els)
# 10-11 · 原因二：传话游戏
els = [txt(960, 180, 64, "原因二：不玩传话游戏", 10, c="red")]
for i, lab in enumerate(("看", "规划路线", "算电机")):
    x = 330 + i * 460
    els += stick(x, 760, 0.9, 10)
    els += bubble(x - 110, 380, 220, 90, 10, lab, s=36)
els += [{"t": "line", "at": 10, "id": "chain", "pts": [[400, 640], [790, 640], [860, 640], [1250, 640], [1320, 640], [1560, 640]], "c": "muted", "w": 3},
        {"t": "move", "at": 10, "kind": "signal", "targets": ["chain"], "speed": 160},
        {"t": "icon", "at": 10, "name": "engine", "x": 1680, "y": 640, "size": 180, "c": "ink"},
        txt(1680, 780, 34, "电机", 10, c="muted"),
        txt(960, 920, 52, "越传越慢，越传越走样", 11, c="red"), txt(1680, 500, 60, "？？", 11, c="red", font="en")]
B.append(els)
# 12 · 中间人全裁了：小神经网络 → 四个电机
els = [txt(960, 180, 56, "中间人，全裁了", 12, c="green")]
els += network(640, 560, 230, 12, n=12, seed=5, idp="nn")
els += [txt(640, 820, 40, "一个小神经网络", 12, c="blue"),
        {"t": "line", "at": 12, "id": "nn_out", "pts": [[900, 560], [1160, 560]], "c": "green", "w": 4},
        {"t": "move", "at": 12, "kind": "signal", "targets": ["nn_out"], "speed": 400},
        {"t": "move", "at": 12, "kind": "pulse", "targets": ["nn"]}]
els += cute_drone(1480, 560, 1.1, 12, idp="d12")
els += [txt(1480, 800, 40, "直接告诉 4 个电机：各转多快", 12)]
B.append(els)
# 13-14 · 强化学习；撞了不心疼
els = [{"t": "icon", "at": 13, "name": "computer", "x": 620, "y": 520, "size": 560, "c": "ink"},
       txt(620, 460, 44, "模拟赛道", 13, c="muted"),
       txt(530, 580, 46, "快 +1", 13, c="green"), txt(720, 580, 46, "撞 −1", 13, c="red"),
       txt(620, 880, 44, "强化学习", 13, c="blue")]
els += cute_drone(1400, 520, 1.0, 14, idp="d14", mood="o", moves=False)
els += [{"t": "move", "at": 14, "kind": "spin", "targets": ["d14*"], "pivot": [1400, 520], "rpm": 45},
        txt(1400, 880, 44, "撞多少次都不心疼", 14, c="muted")]
B.append(els)
# 15-16 · 原因三：一只眼反而够用；门越大越近
els = [txt(960, 180, 60, "原因三：一只眼，反而够用", 15, c="red")]
els += cute_drone(300, 600, 0.9, 16, idp="d16")
els += gate(900, 600, 380, 16) + gate(1550, 600, 140, 16)
els += [txt(900, 870, 40, "看起来大 → 近", 16, c="gold"), txt(1550, 870, 40, "看起来小 → 远", 16, c="muted"),
        txt(960, 980, 34, "（举个例子：门的大小是定的）", 16, c="muted")]
B.append(els)
# 17-18 · 内耳 = IMU；误差拉回来
els = stick(400, 760, 1.4, 17, idp="ear")
els += [{"t": "path", "at": 17, "c": "ink", "w": 3, "d": "M360,425 L390,425 M410,425 L440,425"},   # closed eyes
        {"t": "path", "at": 17, "id": "ear17", "c": "red", "w": 4, "d": "M445,395 Q470,400 465,425 Q460,445 445,445"},
        {"t": "move", "at": 17, "kind": "pulse", "targets": ["ear17"]},
        txt(400, 870, 40, "内耳：闭眼也知道在转弯", 17), txt(400, 940, 40, "IMU", 17, c="blue", font="en"),
        {"t": "line", "at": 18, "pts": [[800, 700], [1700, 700]], "c": "green", "w": 3},
        txt(1250, 760, 32, "真实路线", 18, c="green"),
        {"t": "path", "at": 18, "c": "blue", "w": 3, "d": "M800,700 Q1000,690 1150,620 Q1250,580 1300,560"},
        txt(1000, 520, 32, "只靠内耳：越飘越远", 18, c="blue")]
els += gate(1300, 560, 90, 18)
els += [{"t": "arrow", "at": 18, "pts": [[1320, 590], [1420, 690]], "c": "gold", "w": 4},
        txt(1500, 520, 36, "看到门！拉回来", 18, c="gold")]
B.append(els)
# 19-20 · 人类飞手看的也是一个摄像头；一只眼对一只眼；中间隔了什么
els = pilot(330, 720, 1.3, 19)
els += [{"t": "line", "at": 19, "id": "fpv", "pts": [[420, 410], [1000, 410]], "c": "muted", "w": 3},
        {"t": "move", "at": 19, "kind": "signal", "targets": ["fpv"], "speed": 300}]
els += cute_drone(1150, 420, 0.8, 19, idp="d19")
els += [txt(720, 360, 34, "飞手眼镜里：也是一个摄像头", 19, c="muted"),
        txt(1600, 430, 56, "一只眼 vs 一只眼", 20, c="blue"),
        txt(1000, 780, 38, "人：眼睛 → 大脑 → 手指 → 遥控器 → 电机", 20, c="muted"),
        txt(1000, 880, 44, "芯片 → 电机", 20, c="green"),
        txt(1000, 960, 34, "（什么都没隔）", 20, c="green")]
B.append(els)
# 21 · 用途：扫地机器人、码头吊车
els = [txt(960, 180, 56, "这有什么用？", 21, c="blue"),
       {"t": "ellipse", "at": 21, "id": "vac", "x": 300, "y": 560, "w": 420, "h": 200, "c": "ink", "fill": "gold"},
       {"t": "ellipse", "at": 21, "id": "vac", "x": 440, "y": 600, "w": 30, "h": 36, "c": "ink", "fill": "ink"},
       {"t": "ellipse", "at": 21, "id": "vac", "x": 550, "y": 600, "w": 30, "h": 36, "c": "ink", "fill": "ink"},
       {"t": "path", "at": 21, "id": "vac", "c": "ink", "w": 3, "d": "M470,680 Q510,705 550,680"},
       {"t": "move", "at": 21, "kind": "shift", "targets": ["vac"], "dx": 120, "dy": 0, "dur": 3, "delay": 1},
       txt(560, 860, 40, "扫地机器人：更稳、更省电", 21),
       {"t": "path", "at": 21, "c": "ink", "w": 4, "d": "M1300,900 L1300,340 L1720,340 M1300,420 L1400,340 M1180,340 L1300,340 M1560,340 L1560,560"},
       {"t": "rect", "at": 21, "x": 1500, "y": 560, "w": 120, "h": 80, "c": "red"},
       txt(1500, 960, 40, "码头大吊车", 21)]
B.append(els)
# 22 · 友情提示：定好的赛道 vs 乱糟糟的树林
els = [txt(960, 180, 56, "友情提示", 22, c="red")]
els += gate(480, 560, 260, 22)
els += [txt(480, 800, 40, "定好的赛道：赢了", 22, c="green")]
for i, (x, y, s) in enumerate(((1250, 700, 1.0), (1420, 660, 1.3), (1600, 720, 0.9), (1340, 760, 0.8))):
    els.append({"t": "path", "at": 22, "c": "green", "w": 3.4, "d": f"M{x},{y - 260 * s} L{x - 90 * s},{y} L{x + 90 * s},{y} Z M{x},{y} L{x},{y + 50 * s}"})
els += [{"t": "icon", "at": 22, "id": "q22", "name": "question", "x": 1430, "y": 420, "size": 160, "c": "red"},
        {"t": "move", "at": 22, "kind": "pulse", "targets": ["q22"]},
        txt(1430, 900, 40, "乱糟糟的树林：还不知道", 22, c="red")]
B.append(els)
# 23 · 别急着退休；别眨眼
els = pilot(560, 860, 1.6, 23)
els += [txt(560, 980, 40, "人类飞手：先别急着退休", 23, c="muted")]
els += cute_drone(1350, 500, 1.4, 23, idp="d23")
els += [txt(1350, 860, 72, "别眨眼", 23, c="red"), {"t": "move", "at": 23, "kind": "pulse", "targets": ["d23_eye"]}]
B.append(els)
boards = [{"elements": e} for e in B]

bad = missing_chars("".join(e.get("text", "") for b in B for e in b) + "".join(SEG))
if bad:
    sys.exit(f"the fonts lack: {bad}")
TITLE = {"zh": "一只眼的无人机，凭什么赢了世界冠军？", "en": "How did a one-eyed drone beat the world champions?"}
if "--fake" in sys.argv:       # 7 s per segment, no audio: for checking the boards
    segs = [{"zh": s, "t0": 7 * i, "t1": 7 * i + 6.5} for i, s in enumerate(SEG)]
    import numpy as np, soundfile as sf  # noqa: E401
    sf.write(here / "配音.wav", np.zeros(24000 * 7 * len(SEG), np.float32), 24000)
    lesson = wai.to_lesson(TITLE, segs, boards, audio="配音.wav", duration=7 * len(SEG))
    lesson["pace"], lesson["hand"] = 0.5, False
    json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
    sys.exit(print(len(boards), "boards (fake timing)"))
if "--boards-only" in sys.argv:
    lesson = json.load(open(here / "lesson.json"))
    lesson["boards"] = boards
    json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
    sys.exit(print(len(boards), "boards"))

import numpy as np, soundfile as sf, sherpa_onnx as so  # noqa: E401,E402
d = sys.argv[1].rstrip("/") + "/"
tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
    model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
    lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=2),
    rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1))
t, parts, segs, sr = 0.4, [], [], 24000
PAUSE = {0: 0.6, 1: 0.6, 4: 0.6, 7: 0.5, 9: 0.5, 14: 0.5, 18: 0.4, 20: 0.5, 22: 0.4}
for i, zh in enumerate(SEG):
    spoken = zh
    for a_, b_ in SAY.items():
        spoken = spoken.replace(a_, b_)
    a = tts.generate(speakable(spoken), sid=49, speed=1.12); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.4), np.float32))
    segs.append({"zh": zh, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    gap = PAUSE.get(i, 0.25)
    parts += [x, np.zeros(int(sr * gap), np.float32)]; t += len(x) / sr + gap
parts.append(np.zeros(int(sr * 1.2), np.float32)); t += 1.2
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson(TITLE, segs, boards, audio="配音.wav", duration=round(t, 2))
lesson["pace"], lesson["hand"] = 0.5, False
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
