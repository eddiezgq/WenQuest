"""Daily science short 2026-10-16 (English): "Why can't your phone charge in nine minutes?"
News: Agility Robotics picked Nyobolt (Cambridge, UK, founded 2019) for Digit 5's battery: 9-minute charge, 90 minutes of work,
run-to-charge 10:1 (Digit 4: 2:1), "more than 20 hours of productive work in a 24-hour day"; Nyobolt cites "proprietary anode
materials"; early access 1H 2027 (The Robot Report 2026-10-14, Drives & Controls 2026-10-15, Supply Chain 24/7 2026-09-16).
Science: lithium ions parking in a graphite anode (intercalation), lithium plating and dendrites when charged too fast, Joule heat ∝ I²,
phones fast-charge to ~half then taper, the energy-vs-power trade-off. Said as a guess in the film: how Nyobolt's anode works.
Characters: popkit.cute_bot (the robot), popkit.cute_battery (the narrator's phone battery, the running gag). No hand.
    python3 make.py <kokoro model dir> | --fake | --boards-only   then  python3 ../../../../tools/whiteboard/wb.py . [--mp4]"""
import json, sys  # noqa: E401
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[3] / "services" / "gateway"))
sys.path.insert(0, str(here.parents[1]))
from app.production.whiteboard import ai as wai  # noqa: E402
from app.production.whiteboard.core import missing_chars  # noqa: E402
from popkit import cute_battery, cute_bot, stick, txt  # noqa: E402

SEG = [
 "This week, a humanoid robot learned a trick your phone would kill for: nine minutes of charging, ninety minutes of work.",
 "My phone, meanwhile, is at three percent. It's watching this video with me. Nervously.",
 "The robot is Digit 5, from Agility Robotics. Its new batteries come from Nyobolt, a battery company in Cambridge, England.",
 "So here's the question: if a robot can charge in nine minutes, why can't everything? And why do people say fast charging hurts batteries?",
 "First, the math. The old Digit worked two minutes for every minute it charged. That's about sixteen hours of work a day.",
 "Digit 5 claims ten to one. Run that around the clock and you get almost twenty-two hours. The companies say more than twenty. Close enough.",
 "Now, what is charging, really? Inside the battery, lithium ions travel from one side to the other, and have to find a place to park.",
 "On the other side, the parking garage is usually graphite: stacked sheets of carbon, like the floors of a garage.",
 "Charge slowly, and the ions drive in, find a floor, and slide into a spot. Lovely.",
 "Charge fast, and it's a stadium letting out. Everyone hits the entrance at once.",
 "The ones that can't get in? They park on the sidewalk. They turn into plain lithium metal, stuck on the surface. That's called lithium plating.",
 "Those ions are gone for good. Your battery just got a little smaller. Forever.",
 "Worse, the sidewalk parking can grow into tiny spikes. If one pokes all the way through to the other side: short circuit.",
 "Reason two: heat. The heat from a current grows with the current squared. Twice the current, four times the heat.",
 "So a nine-minute charge isn't just a bigger hose. It's a hose that wants to boil.",
 "Here's the twist: your phone already fast charges. Ever notice it races to about half, then slows to a crawl?",
 "That's on purpose. An empty garage fills fast. A nearly full one has to slow down, or cars end up on the sidewalk.",
 "So how does Nyobolt do it? The company only says: proprietary anode materials.",
 "My guess, and it's only a guess: a garage with wider ramps and bigger doors, so the ions can rush in without piling up.",
 "Twist number two: there's a price. Every battery trades between how much it holds and how fast it fills.",
 "Digit 5 runs only ninety minutes per charge. Agility didn't build a marathon runner. They built a sprinter who naps a lot.",
 "For a warehouse robot, that's perfect. It works, steps onto its charger for nine minutes, and goes back to lifting boxes.",
 "Your phone would rather last all day. So it gets the big, slow garage.",
 "Friendly fine print: these numbers are the companies' claims. Early customers get the robot in 2027, and nobody outside has tested it yet.",
 "As for my phone: one percent. If you need me, I'll be in the charging dock. Nine minutes, tops.",
]


def T(x, y, s, text, at, c="ink", **kw):
    return txt(x, y, s, text, at, c=c, font="en", **kw)


def ion(x, y, at, idp=None, c="gold"):
    e = {"t": "ellipse", "at": at, "x": x - 16, "y": y - 16, "w": 32, "h": 32, "c": c, "fill": c}
    if idp:
        e["id"] = idp
    return e


def cell(at, x0=260, y0=300, w=1400, h=480):
    """Battery cross-section: cathode (left), separator (dashed middle), graphite anode (right, stacked sheets)."""
    E = [{"t": "rect", "at": at, "x": x0, "y": y0, "w": w, "h": h, "c": "ink"},
         {"t": "rect", "at": at, "x": x0 + 20, "y": y0 + 20, "w": 260, "h": h - 40, "c": "red"},
         T(x0 + 150, y0 + h + 60, 40, "cathode", at, c="red")]
    E += [{"t": "line", "at": at, "pts": [[x0 + w / 2 - 60, y0 + 20 + 40 * i], [x0 + w / 2 - 60, y0 + 40 + 40 * i]], "c": "muted", "w": 3} for i in range(11)]
    gx = x0 + w - 520
    E += [{"t": "line", "at": at, "pts": [[gx, y0 + 50 + 60 * i], [x0 + w - 30, y0 + 50 + 60 * i]], "c": "blue", "w": 4} for i in range(7)]
    E += [T(gx + 240, y0 + h + 60, 40, "anode: graphite", at, c="blue")]
    return E


B = []
# 0-1 · 9 min charge, 90 min work; my phone at 3%
els = cute_bot(480, 980, 1.3, 0)
els += [T(480, 190, 64, "charge 9 min", 0, c="green"), T(480, 290, 64, "work 90 min", 0, c="blue"),
        {"t": "icon", "at": 1, "name": "phone", "x": 1400, "y": 560, "size": 640, "c": "ink"}]
els += cute_battery(1400, 560, 0.9, 1, idp="b1", level=0.04, mood="tired", sweat=True)
els += [T(1400, 900, 60, "3%", 1, c="red"), T(1400, 980, 36, "(nervous)", 1, c="muted")]
B.append(els)
# 2-3 · Digit 5 + Nyobolt; the question
els = cute_bot(330, 900, 1.2, 2, idp="bot2")
els += [T(960, 200, 80, "Digit 5", 2, c="blue"), T(960, 280, 40, "Agility Robotics", 2, c="muted"),
        T(960, 340, 40, "batteries: Nyobolt (Cambridge, England)", 2, c="muted"),
        {"t": "icon", "at": 3, "id": "q3", "name": "question", "x": 1060, "y": 590, "size": 240, "c": "red"},
        {"t": "move", "at": 3, "kind": "pulse", "targets": ["q3"]},
        T(1160, 820, 52, "Why can't everything charge in 9 min?", 3, c="red"),
        T(1160, 900, 44, "Does fast charging hurt?", 3, c="muted")]
els += cute_battery(1600, 580, 0.8, 3, idp="b3", level=0.5)
B.append(els)
# 4-5 · the math: 2:1 → 16 h, 10:1 → ~22 h
els = [T(960, 170, 64, "a 24-hour day", 4, c="muted"), T(220, 450, 44, "old", 4, align="right")]
x0, L = 300, 1320
for i in range(8):
    p = x0 + i * L / 8
    els += [{"t": "rect", "at": 4, "x": p, "y": 400, "w": L / 8 * 2 / 3, "h": 70, "c": "blue", "fill": "blue"},
            {"t": "rect", "at": 4, "x": p + L / 8 * 2 / 3, "y": 400, "w": L / 8 / 3, "h": 70, "c": "gold", "fill": "gold"}]
els += [T(1700, 450, 52, "16 h", 4, c="blue", align="left"), T(500, 550, 36, "blue = work, gold = charging", 4, c="muted"),
        T(220, 750, 44, "new", 5, align="right")]
n = 1440 / 99
for i in range(14):
    p = x0 + i * L / n
    els += [{"t": "rect", "at": 5, "x": p, "y": 700, "w": L / n * 10 / 11, "h": 70, "c": "blue", "fill": "blue"},
            {"t": "rect", "at": 5, "x": p + L / n * 10 / 11, "y": 700, "w": L / n / 11, "h": 70, "c": "gold", "fill": "gold"}]
els += [{"t": "rect", "at": 5, "x": x0 + 14 * L / n, "y": 700, "w": L - 14 * L / n, "h": 70, "c": "blue", "fill": "blue"},
        T(1700, 750, 52, "≈ 22 h", 5, c="green", align="left"), T(960, 900, 40, "(they say \"more than 20\". Close enough.)", 5, c="muted")]
B.append(els)
# 6-8 · ions travel and park; graphite = garage floors; slow = lovely
els = cell(6)
for i in range(4):
    els.append(ion(420 + (i % 2) * 70, 420 + i * 80, 6, idp="ion6"))
els += [{"t": "move", "at": 6, "kind": "shift", "targets": ["ion6"], "dx": 1000, "dy": -30, "dur": 3, "delay": 2},
        T(960, 220, 44, "lithium ions: find a place to park", 6, c="gold"),
        T(1400, 270, 40, "= floors of a parking garage", 7, c="blue")]
els += [ion(1250 + 90 * i, 410 + 120 * (i % 3), 8, c="gold") for i in range(4)]
els += [T(960, 960, 52, "charge slowly: ions slide in. Lovely.", 8, c="green")]
B.append(els)
# 9-11 · stadium letting out; plating on the sidewalk; smaller forever
els = cell(9)
for i in range(12):
    els.append(ion(1060 + (i % 3) * 36, 360 + i * 34, 9, idp="ion9"))
els += [{"t": "move", "at": 9, "kind": "pulse", "targets": ["ion9"], "dur": 2},
        T(960, 220, 44, "charge fast: everyone hits the entrance at once", 9, c="red")]
els += [{"t": "rect", "at": 10, "x": 1120, "y": 330 + 70 * i, "w": 30, "h": 50, "c": "muted", "fill": "muted"} for i in range(6)]
els += [T(1260, 950, 48, "lithium plating", 10, c="muted"), T(1260, 1010, 32, "(parked on the sidewalk)", 10, c="muted")]
els += cute_battery(180, 940, 0.4, 11, idp="b11", level=0.55, mood="tired", moves=False)
els += [T(480, 1000, 40, "smaller. forever.", 11, c="red")]
B.append(els)
# 12 · spikes → short circuit
els = cell(12)
els += [{"t": "path", "at": 12, "c": "muted", "w": 4, "d": "M1140,560 L1080,540 L1040,575 L980,550 L940,585 L880,560 L840,590"},
        {"t": "path", "at": 12, "c": "muted", "w": 3, "d": "M1080,540 L1060,500 M980,550 L960,610 M880,560 L860,520"},
        {"t": "path", "at": 12, "id": "spark", "c": "red", "w": 6, "d": "M820,520 L780,600 L830,600 L790,680"},
        {"t": "move", "at": 12, "kind": "pulse", "targets": ["spark"]},
        T(960, 220, 44, "tiny spikes grow across...", 12, c="muted"),
        T(960, 960, 64, "short circuit!", 12, c="red")]
B.append(els)
# 13-14 · heat ∝ current²; a hose that wants to boil
els = [T(960, 200, 64, "heat grows with current²", 13, c="red"),
       T(480, 400, 48, "1× current", 13), {"t": "icon", "at": 13, "name": "flame", "x": 480, "y": 560, "size": 150, "c": "gold"},
       T(1300, 400, 48, "2× current", 13)]
els += [{"t": "icon", "at": 13, "id": "fl13", "name": "flame", "x": 1060 + 160 * i, "y": 560, "size": 150, "c": "red"} for i in range(4)]
els += [{"t": "move", "at": 13, "kind": "pulse", "targets": ["fl13"]},
        T(1300, 700, 44, "= 4× heat", 13, c="red"),
        {"t": "icon", "at": 14, "id": "th14", "name": "thermometer", "x": 420, "y": 860, "size": 200, "c": "red"},
        {"t": "move", "at": 14, "kind": "pulse", "targets": ["th14"]},
        T(1060, 880, 52, "not a bigger hose: a hose that wants to boil", 14, c="muted")]
B.append(els)
# 15-16 · phone races to half then crawls; empty vs full garage
els = [{"t": "arrow", "at": 15, "pts": [[300, 820], [300, 260]], "c": "ink", "w": 3},
       {"t": "arrow", "at": 15, "pts": [[300, 820], [1100, 820]], "c": "ink", "w": 3},
       T(250, 300, 36, "100%", 15, c="muted", align="right"), T(1100, 880, 36, "time", 15, c="muted"),
       {"t": "path", "at": 15, "c": "green", "w": 5, "d": "M300,820 L520,540 Q620,440 760,380 Q920,320 1080,300"},
       T(560, 500, 40, "races to ~half", 15, c="green", align="right"), T(900, 270, 40, "then crawls", 15, c="muted")]
els += cute_battery(1550, 560, 1.1, 16, idp="b16", level=0.92)
els += [T(1550, 860, 40, "nearly full: slow down,", 16, c="blue"), T(1550, 920, 40, "or ions hit the sidewalk", 16, c="blue")]
B.append(els)
# 17-18 · "proprietary anode materials"; my guess: wider ramps
els = [T(960, 200, 56, "\"proprietary anode materials\"", 17, c="muted"),
       {"t": "path", "at": 18, "c": "ink", "w": 3.4, "d": "M300,560 L300,400 L800,400 L800,780 L300,780 L300,620"},
       T(550, 860, 40, "graphite: narrow door", 18, c="blue")]
els += [ion(260 - 40 * (i % 2), 520 + 40 * i, 18, c="gold") for i in range(5)]
els += [{"t": "path", "at": 18, "c": "ink", "w": 3.4, "d": "M1120,450 L1120,400 L1620,400 L1620,780 L1120,780 L1120,730"}]
els += [ion(1060, 470 + 60 * i, 18, idp="ion18") for i in range(5)]
els += [{"t": "move", "at": 18, "kind": "shift", "targets": ["ion18"], "dx": 300, "dy": 0, "dur": 2, "delay": 3},
        T(1370, 860, 40, "wider ramps, bigger doors?", 18, c="green"),
        T(1370, 930, 34, "(my guess)", 18, c="gold")]
B.append(els)
# 19-20 · trade-off seesaw; sprinter who naps
els = [{"t": "path", "at": 19, "c": "ink", "w": 4, "d": "M520,700 L460,800 L580,800 Z"},
       {"t": "line", "at": 19, "id": "plank", "pts": [[220, 700], [820, 700]], "c": "ink", "w": 6},
       {"t": "move", "at": 19, "kind": "wiggle", "targets": ["plank"], "pivot": [520, 700], "amp": 8, "hz": 0.6},
       T(260, 640, 36, "holds a lot", 19, c="blue"), T(780, 640, 36, "fills fast", 19, c="green"),
       T(520, 900, 40, "pick one (mostly)", 19, c="muted")]
els += stick(1150, 820, 1.0, 20, arms="up")
els += [T(1150, 900, 36, "marathon runner", 20, c="muted"),
        {"t": "line", "at": 20, "pts": [[1060, 560], [1240, 760]], "c": "red", "w": 5}, {"t": "line", "at": 20, "pts": [[1240, 560], [1060, 760]], "c": "red", "w": 5}]
els += cute_bot(1600, 820, 0.8, 20, idp="bot20", moves=False)
els += [T(1720, 470, 48, "z z z", 20, c="blue"), T(1600, 900, 36, "sprinter who naps a lot", 20, c="green")]
B.append(els)
# 21-22 · warehouse loop; phone gets the big slow garage
els = cute_bot(380, 800, 1.0, 21, idp="bot21")
els += [{"t": "rect", "at": 21, "x": 620, "y": 640, "w": 120, "h": 100, "c": "gold"}, {"t": "rect", "at": 21, "x": 660, "y": 540, "w": 120, "h": 100, "c": "gold"},
        T(700, 820, 36, "boxes", 21, c="muted"),
        {"t": "icon", "at": 21, "id": "bat21", "name": "battery", "x": 400, "y": 200, "size": 160, "c": "green"},
        T(500, 215, 36, "9 min", 21, c="green", align="left"),
        {"t": "arrow", "at": 21, "pts": [[520, 260], [700, 500]], "c": "muted", "w": 3},
        {"t": "arrow", "at": 21, "pts": [[250, 560], [320, 270]], "c": "muted", "w": 3},
        {"t": "move", "at": 21, "kind": "pulse", "targets": ["bat21"]},
        T(500, 980, 40, "work · charge · repeat", 21, c="blue"),
        {"t": "icon", "at": 22, "name": "phone", "x": 1450, "y": 540, "size": 560, "c": "ink"}]
els += cute_battery(1450, 540, 0.8, 22, idp="b22", level=0.85)
els += [T(1450, 900, 40, "lasts all day:", 22, c="blue"), T(1450, 960, 40, "big, slow garage", 22, c="blue")]
B.append(els)
# 23 · fine print
els = [T(960, 220, 64, "friendly fine print", 23, c="red"),
       T(960, 400, 48, "company claims, not independent tests", 23),
       T(960, 500, 48, "early customers: 2027", 23),
       T(960, 600, 48, "real-world wear: unknown (for now)", 23, c="muted")]
els += cute_bot(960, 1020, 0.8, 23, idp="bot23")
B.append(els)
# 24 · my phone at 1%; charging dock, nine minutes tops
els = [{"t": "icon", "at": 24, "name": "phone", "x": 520, "y": 520, "size": 600, "c": "ink"}]
els += cute_battery(520, 520, 0.85, 24, idp="b24", level=0.02, mood="tired", sweat=True)
els += [T(520, 860, 64, "1%", 24, c="red"),
        {"t": "rect", "at": 24, "x": 1180, "y": 880, "w": 400, "h": 40, "c": "green", "fill": "green"},
        T(1380, 980, 40, "charging dock", 24, c="green")]
els += stick(1380, 880, 1.2, 24, idp="me")
els += [{"t": "move", "at": 24, "kind": "bob", "targets": ["me"], "amp": 10, "hz": 0.8},
        T(1380, 330, 64, "Nine minutes, tops.", 24, c="blue")]
B.append(els)
boards = [{"elements": e} for e in B]

bad = missing_chars("".join(e.get("text", "") for b in B for e in b))
if bad:
    sys.exit(f"the fonts lack: {bad}")
TITLE = {"zh": "Why can't your phone charge in nine minutes?", "en": "Why can't your phone charge in nine minutes?"}
if "--fake" in sys.argv:       # 7 s per segment, silent audio: for checking the boards
    import numpy as np, soundfile as sf  # noqa: E401
    sf.write(here / "配音.wav", np.zeros(24000 * 7 * len(SEG), np.float32), 24000)
    segs = [{"zh": s, "t0": 7 * i, "t1": 7 * i + 6.5} for i, s in enumerate(SEG)]
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
    lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=2), max_num_sentences=1))
t, parts, segs, sr = 0.4, [], [], 24000
PAUSE = {0: 0.5, 1: 0.6, 3: 0.5, 5: 0.4, 8: 0.4, 11: 0.6, 12: 0.5, 14: 0.5, 18: 0.5, 20: 0.4, 22: 0.4, 23: 0.5}
for i, en in enumerate(SEG):
    a = tts.generate(en, sid=16, speed=1.12); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.4), np.float32))
    segs.append({"zh": en, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    gap = PAUSE.get(i, 0.25)
    parts += [x, np.zeros(int(sr * gap), np.float32)]; t += len(x) / sr + gap
parts.append(np.zeros(int(sr * 1.2), np.float32)); t += 1.2
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson(TITLE, segs, boards, audio="配音.wav", duration=round(t, 2))
lesson["pace"], lesson["hand"] = 0.5, False
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
