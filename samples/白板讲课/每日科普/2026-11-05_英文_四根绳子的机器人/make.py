"""Daily science 2026-11-05 (English): "Four Strings Beat a Robot Arm?"
News: Stringman, an open-source cable robot by Neufangled Robotics (Nathaniel Nifong, North Carolina), $795 (HN title says $800).
  Four motorized anchors near the ceiling corners reel lines attached to a hanging gripper.
Trending: Hacker News front page 2026-11-04, #1 "Stringman, an $800 open-source room scale gripper robot" (810 points when checked).
Maker's figures (via DEV Community write-up and RuntimeWire): per-line tension capped at 28 N for safety; payload up to 2.2 kg near the floor,
  about 1.9 kg average; ~0.4 m/s; controller adjusts tension dozens of times per second; two anchors carry cameras tracking a marker on the gripper;
  heavy compute runs on the user's own PC, local-only, no data leaves the home (maker's claim); 50 demonstrations can be enough for some
  behaviours (maker's claim). Comparison research arm: 0.75 m reach, 0.88 m^3 workspace, $2,500, 7 actuators vs Stringman ~147 m^3, 4 motors;
  ~500x more workspace per dollar. Lines can only pull; vertical balance 2*T*cos(theta) = W, so capacity drops near walls and corners.
Sources:
- https://news.ycombinator.com/front (2026-11-04)
- https://neufangled.com/
- https://runtimewire.com/article/stringman-neufangled-795-ceiling-cable-robot-nathaniel-nifong
- https://dev.to/lu1tr0n/robots-de-cable-como-stringman-carga-mas-con-menos-motores-2p39
Ours: puppet / claw machine / two friends carrying a bag (metaphors); "an arm carries its own elbow" is our plain-language explanation;
  the stadium flying camera is general knowledge, mentioned as a well-known example of the same idea.
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_claw, stick  # noqa: E402

S = [
 ("一个住在天花板上的机器人，|冲上了 Hacker News 第一名。", "A robot that lives on your ceiling | just hit number one on Hacker News."),
 ("它大约八百美元，|几乎够得着房间里每个角落。", "It costs about eight hundred dollars, | and it can reach almost every spot in a room."),
 ("没有手臂，没有轮子，|只有四根绳子。", "No arm. No wheels. | Just four strings."),
 ("它叫 Stringman（绳子侠），|来自北卡罗来纳的小公司 Neufangled。", "It is called Stringman, | from a tiny company in North Carolina called Neufangled."),
 ("Hacker News 上它拿了八百多票，|网友吵翻了。", "On Hacker News it pulled in over eight hundred points, | and the comments exploded."),
 ("今天的烧脑问题：|绳子只能拉，凭啥把机器人送到任何地方？", "Today's brain teaser: | strings can only pull. So how do they put a robot anywhere?"),
 ("认识主角：小抓，|吊在房间正中间的抓手。", "Meet our hero, Grabby, | a little gripper hanging in the middle of the room."),
 ("天花板四个角各有一台电机，|每台收绳或者放绳。", "Four motors sit near the ceiling corners. | Each one reels a string in or out."),
 ("像提线木偶，|只不过拉线的是四台电机。", "Think of a puppet, | but the puppeteer is four motors."),
 ("或者像一台巨型抓娃娃机，|整间屋子就是那个箱子。", "Or a giant claw machine, | where the whole room is the box."),
 ("反转一：绳子推不动东西。|不信你试试，一推就软了。", "Twist one: you cannot push with a string. | Try it. It just goes floppy."),
 ("所以每根绳子都得绷紧，|一刻都不能松。", "So every string has to stay tight, | all the time."),
 ("想往左走，|左边收绳，右边放绳。", "To move left, | the left strings reel in, and the right strings let out."),
 ("想往下走，|四根一起放。", "To go down, | all four let out together."),
 ("控制器每秒调好几十次|每根绳子的拉力。", "The controller adjusts every string's pull | dozens of times a second."),
 ("角上的两台摄像头|盯着抓手上的标记，像裁判一样。", "Two cameras on the corners | watch a marker on the gripper, like a referee."),
 ("球场上空飞来飞去的摄像机，|也是这样吊在缆绳上的。", "That flying camera over a football field? | It hangs on cables the same way."),
 ("反转二：比够得着，绳子完胜。|厂家拿来对比的研究用机械臂，只能伸七十五厘米。", "Twist two: strings win on reach. | The research arm the maker compares it with reaches seventy five centimeters."),
 ("那条手臂能扫的空间，不到一立方米；|绳子侠大约一百四十七立方米。", "That arm sweeps less than one cubic meter. | Stringman covers about one hundred forty seven."),
 ("那条手臂大约两千五百美元，|要七台电机。", "That arm costs about twenty five hundred dollars, | with seven motors."),
 ("绳子侠：四台电机，|八百美元左右。", "Stringman: four motors, | about eight hundred dollars."),
 ("厂家算了一下：每花一块钱，|能管的空间多了大约五百倍。", "Per dollar, the maker says, | that is about five hundred times more room."),
 ("而且它能提大约两公斤，|像一大瓶水。", "It can lift about two kilograms, | like a big bottle of water."),
 ("为啥？手臂得扛着自己沉重的胳膊肘，|绳子几乎没有重量。", "Why? An arm has to carry its own heavy elbow. | A string weighs almost nothing."),
 ("反转三，最狡猾：|它在中间最有劲，在角落最没劲。", "Twist three, the sneakiest: | it is strongest in the middle and weakest in the corners."),
 ("在中间，绳子几乎竖直往下，|力气全用来拎东西。", "In the middle, the strings hang almost straight down, | so all their pull holds up the load."),
 ("靠近墙边，绳子快躺平了，|大部分力气都往旁边白费了。", "Near a wall, the strings lie almost flat, | and most of the pull goes sideways, wasted."),
 ("就像两个人一人拎一个提手提袋子：|挨着走，轻松；离远了，手疼。", "It is like two friends carrying a bag by its handles. | Walk close, easy. Walk far apart, ouch."),
 ("为了安全，每根绳子最多拉二十八牛，|差不多三公斤东西的重量。", "For safety, each string is capped at twenty eight newtons, | about the weight of a three kilogram bag."),
 ("所以房间的角落，|就是它最吃力的地方。", "So the corners of the room | are where it struggles most."),
 ("大脑跑在你自己的电脑上，|厂家说，数据不出家门。", "Its brain runs on your own computer, | and the maker says no data leaves your home."),
 ("你做几遍给它看，它就能学；|厂家说有些活五十次示范就够。", "You teach it a chore by showing it. | The maker says fifty demos can be enough for some tasks."),
 ("友情提示：这些数字都来自厂家，|还没人在你家乱糟糟的客厅里测过。", "Fine print: these numbers come from the maker, | and nobody has tested them in your messy living room."),
 ("还有，客厅里拉四根绳子，|你家的猫可能有意见。", "Also, four strings across your living room? | Your cat may have opinions."),
 ("所以，只能拉的绳子，|凭啥把机器人送到任何地方？", "So how do strings that only pull | put a robot anywhere?"),
 ("四根绳子互相拔河，|机器人就停在力量平衡的那一点。", "Four of them play tug of war, | and the robot sits right where the pulls balance."),
 ("有时候最聪明的机械臂，|就是根本没有手臂。", "Sometimes the best robot arm | is no arm at all."),
]
TITLE = {"zh": "四根绳子打败机械臂？", "en": "Four Strings Beat a Robot Arm?"}

B = []


def bd(a, *parts):
    E = []

    def flat(p):
        if isinstance(p, dict):
            E.append(p)
        else:
            for q in p:
                flat(q)
    flat(parts)
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    B.append(E)


def t(a, x, y, s, text, c="ink", d=0.0):
    return T(a, x, y, s * 1.5, text, c=c, d=d, font="en")


def big(a, x, y, text, c="red", d=0.0, s=140):
    return BIG(a, x, y, text, c=c, d=d, s=s, font="en")


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def man(a, x, y, k=1.4, d=0.0, arms="down"):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 6, "hz": 1.6}]


def claw(a, x, y, k=1.0, d=0.0, mood="happy"):
    i = uid("cl")
    return cute_claw(x, y, k, a, idp=i, mood=mood) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]


def motor(a, x, y, s=70, d=0.0, rpm=60):
    i = uid("mo")
    return [{"t": "icon", "at": a, "id": i, "name": "gear", "x": x, "y": y, "size": s, "c": "ink"}, pop(a, i, d), spin(a, i, (x, y), rpm)]


ANCH = [(330, 260), (1590, 260), (560, 340), (1360, 340)]   # 前两个角 + 后两个角（透视）


def room(a, cx=960, cy=680, k=1.0, d=0.0, mood="happy", anchors=ANCH, floor=True, rpm=60):
    """Room outline, four spinning motors in the ceiling corners, four taut strings to Grabby."""
    E = []
    if floor:
        i = uid("rm")
        E += [P(a, "M330,260 L330,980 L1590,980 L1590,260 M560,340 L560,860 L1360,860 L1360,340 M330,980 L560,860 M1590,980 L1360,860",
                c="muted", w=3, idp=i), pop(a, i, d)]
    for q, (x, y) in enumerate(anchors):
        j = uid("rp")
        E += [P(a, f"M{x},{y} L{cx},{cy - 70 * k}", c="blue", w=4, idp=j), pop(a, j, d + 0.1 + 0.05 * q)]
        E += motor(a, x, y, 60, d + 0.05 * q, rpm if q % 2 else -rpm)
    E += claw(a, cx, cy, k, d + 0.3, mood)
    return E


def ropes2(a, cx, cy, spread, d=0.0, c="blue", top=260):
    """Two strings from the ceiling to a bag at (cx, cy); spread = half distance between the anchors."""
    E = []
    for s_ in (-1, 1):
        j = uid("r2")
        E += [P(a, f"M{cx + s_ * spread},{top} L{cx},{cy - 60}", c=c, w=6, idp=j), pop(a, j, d)]
        E += motor(a, cx + s_ * spread, top, 60, d, 60 * s_)
    return E


def weight(a, x, y, d=0.0, s=120):
    i = uid("wt")
    return [R(a, x - s / 2, y - 60, s, s * 0.8, c="ink", fill="gold", idp=i, sw=6), pop(a, i, d), bob(a, i, 5, 1.0)]


def tug(a, x, y, dx, dy, d=0.0, c="red"):
    """A pulling arrow that pulses out along the string."""
    i = uid("tg")
    return [P(a, f"M{x},{y} L{x + dx},{y + dy}", c=c, w=8, idp=i), pop(a, i, d), wig(a, i, (x, y), 3, 3)]


# ---------- boards ----------
bd(0, room(0, 960, 640, 1.0, 0.0), big(0, 960, 1020, "#1 on Hacker News", c="red", d=0.4, s=80))
bd(0.5, ic(0.5, "computer", 520, 560, 300, 0.0, mv="wig"), big(0.5, 1300, 420, "#1", c="red", d=0.2, s=200), star(0.5, 1300, 700, 0.3, r=50), claw(0.5, 1600, 750, 0.7, 0.4))
bd(1, big(1, 1250, 400, "~$800", c="red", d=0.0, s=170), claw(1, 550, 600, 1.2, 0.1), ic(1, "check", 1250, 720, 140, 0.4, mv="bob", c="green"))
bd(1.5, room(1.5, 600, 820, 0.6, 0.0), [O(1.5, x, y, 18, c="red", fill="red", idp=f"dot{q}") for q, (x, y) in enumerate([(800, 600), (1100, 700), (1300, 800), (700, 900), (1000, 500)])],
   [pop(1.5, f"dot{q}", 0.3 + 0.15 * q) for q in range(5)], [wig(1.5, f"dot{q}", (800, 600), 4, 2) for q in range(5)])
bd(2, ic(2, "robot_arm", 500, 560, 260, 0.0, mv="wig"), cross(2, 500, 560, d=0.3), ic(2, "wheel", 1100, 560, 220, 0.2, mv="spin"), cross(2, 1100, 560, d=0.5), t(2, 800, 850, 60, "no arm, no wheels", d=0.4))
bd(2.5, big(2.5, 960, 260, "4 strings", c="blue", d=0.0, s=140), room(2.5, 960, 720, 0.8, 0.2, floor=False))
bd(3, t(3, 1300, 330, 90, "Stringman", c="blue", d=0.0), claw(3, 600, 600, 1.5, 0.1), [tug(3, 600, 470, q * 120 - 180, -200, 0.3 + 0.05 * q, c="blue") for q in range(4)], star(3, 1300, 550, 0.4, r=40))
bd(3.5, ic(3.5, "map_pin", 600, 550, 260, 0.0, mv="bob", c="red"), t(3.5, 1250, 450, 64, "North Carolina", d=0.2), t(3.5, 1250, 600, 56, "Neufangled Robotics", c="blue", d=0.3), ic(3.5, "building", 1250, 800, 160, 0.4, mv="bob"))
bd(4, big(4, 1150, 380, "800+ points", c="red", d=0.0, s=130), ic(4, "computer", 450, 650, 240, 0.1, mv="wig"), bar(4, 1000, 900, 120, 200, "gold", 0.3), bar(4, 1200, 900, 120, 320, "gold", 0.4), bar(4, 1400, 900, 120, 450, "red", 0.5))
bd(4.5, man(4.5, 450, 900, 1.4, 0.0, arms="up"), man(4.5, 800, 900, 1.3, 0.1, arms="up"), man(4.5, 1150, 900, 1.4, 0.2, arms="up"),
   ic(4.5, "speaker", 1550, 500, 200, 0.3, mv="wig"), t(4.5, 960, 280, 70, "the comments exploded", c="red", d=0.3))
bd(5, big(5, 1150, 300, "Brain teaser", c="red", d=0.0, s=120), ic(5, "question", 450, 450, 260, 0.2, mv="wig", c="red"), claw(5, 1150, 700, 1.0, 0.3, mood="o"))
bd(5.5, ropes2(5.5, 600, 750, 200, 0.0), weight(5.5, 600, 800, 0.2), tug(5.5, 600, 660, 0, -250, 0.4), t(5.5, 1350, 450, 70, "pull only", c="red", d=0.3), ic(5.5, "question", 1350, 700, 180, 0.5, mv="wig", c="red"))
bd(6, room(6, 960, 650, 1.3, 0.0), t(6, 960, 1010, 64, "Grabby", c="blue", d=0.4))
bd(6.5, claw(6.5, 960, 600, 2.0, 0.0), star(6.5, 600, 400, 0.3, r=40), star(6.5, 1320, 400, 0.4, r=40), t(6.5, 960, 950, 56, "hanging in the middle", d=0.4))
bd(7, [motor(7, 400 + 370 * q, 450, 200, 0.15 * q, 90 if q % 2 else -90) for q in range(4)], big(7, 960, 800, "4 motors", c="red", d=0.5, s=120))
bd(7.5, motor(7.5, 600, 350, 220, 0.0, 120), P(7.5, "M600,460 L600,780", c="blue", w=6, idp="lin1"), pop(7.5, "lin1", 0.2), claw(7.5, 600, 850, 0.8, 0.2),
   sh(7.5, ["lin1", ], 0, 0, 0, 0.1) if False else [], t(7.5, 1350, 450, 70, "reel in", c="red", d=0.3), t(7.5, 1350, 650, 70, "let out", c="blue", d=0.5), arr(7.5, 1050, 650, 1050, 420, c="red", d=0.4))
bd(8, stick(500, 950, 1.4, 8, idp="pp", arms="up"), pop(8, "pp*", 0.0), wig(8, "pp*", (500, 700), 8, 1.5),
   [P(8, f"M{420 + 60 * q},250 L{430 + 50 * q},{620 + (q % 2) * 120}", c="blue", w=3, idp=f"pps{q}") for q in range(4)], [pop(8, f"pps{q}", 0.2 + 0.05 * q) for q in range(4)],
   [motor(8, 1150 + 170 * q, 400, 110, 0.3 + 0.1 * q, 90) for q in range(4)], t(8, 1400, 650, 64, "puppeteer = 4 motors", c="red", d=0.6))
bd(8.5, room(8.5, 760, 680, 0.9, 0.0), t(8.5, 1650, 500, 60, "puppet", c="blue", d=0.4), ic(8.5, "question", 1650, 700, 120, 0.5, mv="wig", c="red"))
bd(9, R(9, 500, 250, 920, 700, c="red", sw=10, idp="box9"), pop(9, "box9", 0.0), claw(9, 960, 450, 1.0, 0.1), P(9, "M960,250 L960,380", c="ink", w=5, idp="cl9r"), pop(9, "cl9r", 0.1),
   ic(9, "molecule", 700, 830, 120, 0.3, mv="wig", c="gold"), ic(9, "atom", 1220, 830, 120, 0.4, mv="spin", c="blue"), sh(9, [], 0, 0, 0, 0.1) if False else [])
bd(9.5, room(9.5, 960, 660, 1.0, 0.0), big(9.5, 960, 170, "the room is the box", c="red", d=0.4, s=80))
bd(10, big(10, 960, 280, "Twist one", c="red", d=0.0, s=140), man(10, 500, 950, 1.4, 0.1, arms="up"), P(10, "M620,700 Q800,780 900,720 Q1000,640 1050,760", c="blue", w=7, idp="flop"), pop(10, "flop", 0.3),
   wig(10, "flop", (620, 700), 10, 2), arr(10, 1100, 600, 1450, 600, c="ink", d=0.4), cross(10, 1550, 600, d=0.6))
bd(10.5, P(10.5, "M600,500 Q700,700 800,560 Q900,450 1000,700 Q1100,850 1300,650", c="blue", w=8, idp="flop2"), pop(10.5, "flop2", 0.0), wig(10.5, "flop2", (600, 500), 14, 2.5),
   big(10.5, 960, 300, "floppy!", c="red", d=0.2, s=130), claw(10.5, 1600, 750, 0.7, 0.3, mood="sad"), man(10.5, 400, 950, 1.2, 0.3))
bd(11, room(11, 960, 640, 1.0, 0.0), [tug(11, 960, 570, (x - 960) * 0.3, (y - 570) * 0.3, 0.4 + 0.05 * q) for q, (x, y) in enumerate(ANCH)], t(11, 960, 1020, 60, "always tight", c="red", d=0.5))
bd(11.5, ic(11.5, "clock", 600, 560, 260, 0.0, mv="spin"), big(11.5, 1300, 450, "100%", c="red", d=0.2, s=150), claw(11.5, 1300, 780, 0.6, 0.3), ic(11.5, "check", 1600, 780, 120, 0.5, mv="bob", c="green"))
bd(12, room(12, 1200, 660, 0.9, 0.0), claw(12, 680, 660, 0.9, 0.6), arr(12, 1060, 660, 820, 660, c="red", d=0.5), t(12, 960, 1030, 60, "move left / right", d=0.3))
bd(12.5, ropes2(12.5, 960, 750, 420, 0.0), weight(12.5, 960, 800, 0.1), sh(12.5, [], 0, 0, 0, 0.1) if False else [], tug(12.5, 900, 690, -250, -250, 0.3, c="red"),
   tug(12.5, 1020, 690, 150, -150, 0.5, c="blue"), t(12.5, 400, 900, 56, "reel in", c="red", d=0.3), t(12.5, 1520, 900, 56, "let out", c="blue", d=0.5))
bd(13, room(13, 960, 520, 0.9, 0.0), arr(13, 1150, 520, 1150, 850, c="red", d=0.4), claw(13, 960, 860, 0.6, 0.6))
bd(13.5, [motor(13.5, 400 + 370 * q, 400, 160, 0.1 * q, 120) for q in range(4)], big(13.5, 960, 700, "all 4 let out", c="blue", d=0.4, s=100), arr(13.5, 960, 800, 960, 1000, c="blue", d=0.6))
bd(14, ic(14, "chip", 550, 560, 260, 0.0, mv="wig", c="blue"), big(14, 1250, 420, "dozens / s", c="red", d=0.2, s=120), ic(14, "sine", 1250, 700, 220, 0.3, mv="wig", c="red"))
bd(14.5, room(14.5, 960, 660, 1.0, 0.0, rpm=150), [ic(14.5, "sine", x, y + 80, 80, 0.4 + 0.05 * q, mv="wig", c="red") for q, (x, y) in enumerate(ANCH)])
bd(15, room(15, 960, 680, 0.9, 0.0), ic(15, "eye", 330, 380, 110, 0.4, mv="wig", c="red"), ic(15, "eye", 1590, 380, 110, 0.5, mv="wig", c="red"), t(15, 960, 1020, 60, "two cameras", d=0.4))
bd(15.5, ic(15.5, "eye", 450, 500, 220, 0.0, mv="wig", c="red"), claw(15.5, 1000, 620, 1.2, 0.1), O(15.5, 1000, 600, 30, c="red", fill="red", idp="mk"), pop(15.5, "mk", 0.3), wig(15.5, "mk", (1000, 600), 5, 3),
   man(15.5, 1550, 950, 1.3, 0.3, arms="up"), t(15.5, 1550, 400, 64, "referee", c="blue", d=0.4))
bd(16, P(16, "M200,900 L1720,900 M960,900 L960,980", c="green", w=8, idp="fld"), pop(16, "fld", 0.0), ic(16, "satellite", 960, 500, 180, 0.1, mv="bob"),
   [P(16, f"M{x},{y} L960,500", c="blue", w=4, idp=f"st{q}") for q, (x, y) in enumerate([(200, 250), (1720, 250)])], [pop(16, f"st{q}", 0.2) for q in range(2)],
   man(16, 500, 880, 0.9, 0.3, arms="up"), man(16, 1400, 880, 0.9, 0.4, arms="up"), ic(16, "wheel", 750, 850, 80, 0.5, mv="spin"))
bd(16.5, ic(16.5, "satellite", 600, 550, 240, 0.0, mv="bob"), t(16.5, 1300, 400, 64, "flying camera", d=0.2), t(16.5, 1300, 560, 64, "same trick", c="red", d=0.3), ropes2(16.5, 1300, 900, 200, 0.4, top=700), claw(16.5, 1300, 960, 0.35, 0.5))
bd(17, big(17, 960, 280, "Twist two", c="red", d=0.0, s=140), claw(17, 600, 700, 1.0, 0.2), ic(17, "robot_arm", 1350, 700, 260, 0.3, mv="wig"), t(17, 960, 950, 60, "reach", c="blue", d=0.4))
bd(17.5, ic(17.5, "robot_arm", 550, 650, 320, 0.0, mv="wig"), big(17.5, 1300, 400, "75 cm", c="red", d=0.2, s=150), ic(17.5, "ruler", 1300, 700, 220, 0.3, mv="wig"))
bd(18, R(18, 500, 550, 200, 200, c="red", fill="paper", sw=8, idp="cube1"), pop(18, "cube1", 0.0), wig(18, "cube1", (600, 650), 3, 2), t(18, 600, 880, 56, "< 1 m³", c="red", d=0.1),
   ic(18, "robot_arm", 600, 400, 160, 0.2, mv="wig"), ic(18, "question", 1350, 600, 180, 0.4, mv="wig", c="blue"))
bd(18.5, R(18.5, 300, 800, 70, 70, c="red", fill="paper", sw=6, idp="cube2"), pop(18.5, "cube2", 0.0), room(18.5, 1100, 650, 0.8, 0.1), big(18.5, 1100, 160, "147 m³", c="blue", d=0.3, s=120), t(18.5, 335, 950, 50, "arm", c="red", d=0.0))
bd(19, big(19, 1250, 380, "$2,500", c="red", d=0.0, s=150), ic(19, "robot_arm", 500, 600, 280, 0.1, mv="wig"), [motor(19, 950 + 120 * q, 700, 90, 0.3 + 0.05 * q, 90) for q in range(7)], t(19, 1300, 850, 60, "7 motors", d=0.5))
bd(19.5, bar(19.5, 600, 950, 200, 600, "red", 0.0), t(19.5, 700, 1010, 50, "arm", d=0.0), bar(19.5, 1000, 950, 200, 190, "blue", 0.3), t(19.5, 1100, 1010, 50, "strings", d=0.3), claw(19.5, 1550, 600, 0.9, 0.4))
bd(20, big(20, 1250, 380, "~$800", c="blue", d=0.0, s=150), claw(20, 500, 600, 1.2, 0.1), [motor(20, 1000 + 160 * q, 700, 110, 0.3 + 0.08 * q, 90) for q in range(4)], t(20, 1250, 870, 60, "4 motors", d=0.5))
bd(20.5, room(20.5, 960, 640, 1.0, 0.0), ic(20.5, "check", 1700, 500, 150, 0.5, mv="bob", c="green"), t(20.5, 960, 1020, 56, "fewer motors, cheaper", c="blue", d=0.4))
bd(21, ic(21, "battery", 450, 560, 200, 0.0, mv="wig", c="gold"), t(21, 450, 780, 56, "per dollar", d=0.1), bar(21, 900, 950, 140, 20, "red", 0.2), bar(21, 1150, 950, 140, 650, "blue", 0.4), claw(21, 1550, 500, 0.7, 0.5))
bd(21.5, big(21.5, 960, 420, "×500", c="red", d=0.0, s=220), claw(21.5, 450, 780, 0.6, 0.2), ic(21.5, "robot_arm", 1500, 780, 160, 0.3, mv="wig"), star(21.5, 960, 750, 0.5, r=50))
bd(22, room(22, 960, 600, 1.0, 0.0), ic(22, "water", 960, 820, 170, 0.4, mv="bob", c="blue"), big(22, 1650, 900, "2 kg", c="red", d=0.5, s=100))
bd(22.5, ic(22.5, "water", 600, 560, 300, 0.0, mv="bob", c="blue"), t(22.5, 1250, 450, 64, "a big bottle of water", d=0.2), claw(22.5, 1300, 750, 0.8, 0.3), ic(22.5, "check", 1600, 750, 120, 0.5, mv="bob", c="green"))
bd(23, ic(23, "robot_arm", 600, 600, 360, 0.0, mv="wig"), weight(23, 600, 420, 0.2, 80), claw(23, 1350, 600, 0.6, 0.4, mood="o"), t(23, 960, 950, 60, "carries its own elbow", c="red", d=0.3), man(23, 1600, 950, 0.8, 0.5))
bd(23.5, P(23.5, "M960,250 L960,700", c="blue", w=4, idp="thin"), pop(23.5, "thin", 0.0), wig(23.5, "thin", (960, 250), 3, 1.5), claw(23.5, 960, 780, 1.0, 0.1),
   t(23.5, 1450, 450, 64, "weighs ~nothing", c="blue", d=0.2), ic(23.5, "wind", 450, 500, 180, 0.3, mv="wig"))
bd(24, big(24, 960, 260, "Twist three", c="red", d=0.0, s=140), room(24, 960, 720, 0.6, 0.2, floor=False), t(24, 500, 950, 56, "strongest", c="green", d=0.4), t(24, 1420, 950, 56, "weakest", c="red", d=0.5))
bd(24.5, room(24.5, 960, 650, 0.8, 0.0), claw(24.5, 1480, 900, 0.5, 0.4, mood="sad"), check(24.5, 960, 420, d=0.5), cross(24.5, 1600, 750, d=0.6))
bd(25, ropes2(25, 700, 800, 90, 0.0), weight(25, 700, 850, 0.1), tug(25, 700, 700, 0, -300, 0.3, c="green"), big(25, 1350, 400, "straight down", c="green", d=0.3, s=90), ic(25, "check", 1350, 700, 180, 0.5, mv="bob", c="green"))
bd(25.5, ropes2(25.5, 960, 800, 100, 0.0), weight(25.5, 960, 850, 0.1), [tug(25.5, 960 + s_ * 40, 700, s_ * 30, -320, 0.3, c="green") for s_ in (-1, 1)], big(25.5, 1500, 500, "100%", c="green", d=0.4, s=120), man(25.5, 400, 950, 1.1, 0.4))
bd(26, ropes2(26, 960, 820, 700, 0.0, top=650), weight(26, 960, 870, 0.1), tug(26, 900, 760, -350, -60, 0.3, c="red"), tug(26, 1020, 760, 350, -60, 0.4, c="red"), big(26, 960, 330, "almost flat", c="red", d=0.4, s=100))
bd(26.5, ropes2(26.5, 960, 820, 700, 0.0, top=650), weight(26.5, 960, 870, 0.1), arr(26.5, 700, 500, 300, 500, c="red", d=0.3), arr(26.5, 1220, 500, 1620, 500, c="red", d=0.4),
   big(26.5, 960, 300, "wasted", c="red", d=0.5, s=110), claw(26.5, 960, 1000, 0.0001, 0.0) if False else [], ic(26.5, "flame", 960, 520, 100, 0.6, mv="wig", c="red"))
bd(27, man(27, 750, 950, 1.4, 0.0, arms="up"), man(27, 1170, 950, 1.4, 0.1, arms="up"), weight(27, 960, 700, 0.2, 140), P(27, "M800,580 L920,640 M1120,580 L1000,640", c="ink", w=6, idp="hd1"), pop(27, "hd1", 0.3),
   t(27, 960, 300, 64, "two friends, one bag", d=0.3), ic(27, "check", 1550, 500, 140, 0.5, mv="bob", c="green"))
bd(27.5, man(27.5, 400, 950, 1.4, 0.0, arms="up"), man(27.5, 1520, 950, 1.4, 0.1, arms="up"), weight(27.5, 960, 800, 0.2, 140),
   P(27.5, "M450,580 L900,740 M1470,580 L1020,740", c="red", w=6, idp="hd2"), pop(27.5, "hd2", 0.3), wig(27.5, "hd2", (960, 740), 4, 3), big(27.5, 960, 330, "ouch!", c="red", d=0.4, s=150))
bd(28, ic(28, "magnet", 500, 560, 240, 0.0, mv="wig", c="red"), big(28, 1250, 400, "28 N max", c="red", d=0.2, s=130), ropes2(28, 1250, 900, 200, 0.3, top=600), weight(28, 1250, 950, 0.4, 80))
bd(28.5, weight(28.5, 600, 650, 0.0, 220), big(28.5, 600, 650, "3 kg", c="ink", d=0.2, s=80), t(28.5, 1300, 450, 64, "about the weight of", d=0.2), ic(28.5, "check", 1300, 700, 160, 0.4, mv="bob", c="green"), t(28.5, 1300, 900, 56, "for safety", c="blue", d=0.5))
bd(29, room(29, 1450, 880, 0.6, 0.0, mood="sad"), [ic(29, "flame", x, y, 90, 0.3 + 0.1 * q, mv="wig", c="red") for q, (x, y) in enumerate([(420, 900), (1500, 900), (560, 780)])])
bd(29.5, claw(29.5, 700, 650, 1.4, 0.0, mood="sad"), ic(29.5, "thermometer", 1300, 550, 220, 0.2, mv="wig", c="red"), t(29.5, 1300, 850, 64, "struggles most", c="red", d=0.4), bubbles(29.5, 900, 450, 3, 0.3, 200) if False else [])
bd(30, ic(30, "computer", 600, 560, 300, 0.0, mv="wig"), ic(30, "chip", 600, 300, 120, 0.2, mv="spin", c="blue"), claw(30, 1350, 600, 1.0, 0.3), arr(30, 800, 560, 1150, 580, c="blue", d=0.4))
bd(30.5, ic(30.5, "building", 600, 560, 300, 0.0, mv="bob"), ic(30.5, "signal", 600, 260, 120, 0.2, mv="wig", c="blue"), cross(30.5, 1000, 560, d=0.5), t(30.5, 1400, 500, 60, "no data leaves", d=0.3), t(30.5, 1400, 650, 60, "(maker says)", c="muted", d=0.4))
bd(31, man(31, 500, 950, 1.5, 0.0, arms="up"), claw(31, 1100, 600, 1.0, 0.2), arr(31, 650, 600, 950, 600, c="blue", d=0.3), ic(31, "eye", 1100, 300, 120, 0.4, mv="wig", c="red"), ic(31, "molecule", 1500, 800, 140, 0.5, mv="wig", c="gold"))
bd(31.5, big(31.5, 960, 380, "50 demos", c="red", d=0.0, s=150), t(31.5, 960, 560, 56, "for some tasks, maker says", c="muted", d=0.2), [check(31.5, 600 + 180 * q, 800, d=0.3 + 0.1 * q) for q in range(5)])
bd(32, big(32, 960, 300, "Fine print", c="blue", d=0.0, s=130), t(32, 960, 480, 56, "numbers from the maker", d=0.2), ic(32, "magnifier", 600, 750, 180, 0.3, mv="wig"), claw(32, 1350, 760, 0.6, 0.4, mood="o"))
bd(32.5, room(32.5, 960, 640, 0.8, 0.0), [ic(32.5, n_, x, 900, 110, 0.3 + 0.1 * q, mv="wig", c="gold") for q, (n_, x) in enumerate([("molecule", 600), ("wheel", 900), ("flask", 1200), ("phone", 1450)])],
   t(32.5, 960, 170, 60, "your messy living room", c="red", d=0.4))
bd(33, room(33, 960, 620, 0.8, 0.0, mood="o"), man(33, 1500, 980, 1.0, 0.4), t(33, 960, 1030, 56, "strings everywhere?", d=0.4))
bd(33.5, O(33.5, 700, 700, 150, c="ink", fill="paper", idp="cat"), P(33.5, "M590,600 L610,470 L680,560 M810,600 L790,470 L720,560", c="ink", w=6, idp="cat"),
   O(33.5, 650, 680, 14, c="ink", fill="ink", idp="cat"), O(33.5, 750, 680, 14, c="ink", fill="ink", idp="cat"), P(33.5, "M560,720 L470,700 M560,740 L470,760 M840,720 L930,700 M840,740 L930,760", c="ink", w=3, idp="cat"),
   pop(33.5, "cat", 0.0), wig(33.5, "cat", (700, 850), 6, 1.5), P(33.5, "M850,800 Q1000,700 1100,850", c="ink", w=8, idp="tail"), pop(33.5, "tail", 0.1), wig(33.5, "tail", (850, 800), 15, 3),
   P(33.5, "M1200,250 L1300,900", c="blue", w=4, idp="cstr"), pop(33.5, "cstr", 0.2), wig(33.5, "cstr", (1200, 250), 6, 2.5), big(33.5, 1500, 450, "opinions", c="red", d=0.4, s=100))
bd(34, ic(34, "question", 500, 500, 260, 0.0, mv="wig", c="red"), tug(34, 1000, 600, -200, -250, 0.2), tug(34, 1000, 600, 200, -250, 0.3), weight(34, 1000, 700, 0.1), t(34, 1450, 500, 64, "only pull...", d=0.3))
bd(34.5, room(34.5, 700, 640, 0.8, 0.0), claw(34.5, 1250, 800, 0.6, 0.4), ic(34.5, "map_pin", 1250, 560, 100, 0.5, mv="bob", c="red"), t(34.5, 960, 1030, 60, "...anywhere?", d=0.3))
bd(35, man(35, 450, 950, 1.3, 0.0, arms="up"), man(35, 1470, 950, 1.3, 0.1, arms="up"), P(35, "M550,620 L1370,620", c="blue", w=8, idp="tugr"), pop(35, "tugr", 0.2), wig(35, "tugr", (960, 620), 4, 3),
   claw(35, 960, 700, 0.7, 0.3), t(35, 960, 300, 70, "tug of war", c="red", d=0.4))
bd(35.5, room(35.5, 960, 640, 1.0, 0.0), [tug(35.5, 960, 570, (x - 960) * 0.25, (y - 570) * 0.25, 0.3 + 0.05 * q, c="red") for q, (x, y) in enumerate(ANCH)], O(35.5, 960, 640, 120, c="green", idp="bal", sw=6), pop(35.5, "bal", 0.5), t(35.5, 960, 1020, 60, "the pulls balance", c="green", d=0.5))
bd(36, ic(36, "robot_arm", 600, 560, 300, 0.0, mv="wig"), ic(36, "question", 600, 260, 120, 0.2, mv="wig", c="red"), t(36, 1300, 500, 70, "the best arm", d=0.3), claw(36, 1300, 760, 0.6, 0.4))
bd(36.5, room(36.5, 960, 640, 1.1, 0.0), big(36.5, 960, 1010, "no arm at all", c="red", d=0.4, s=90))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"Stringman": "String man", "Neufangled": "New fangled", "Grabby": "Grab bee", "m³": " cubic meters"})
