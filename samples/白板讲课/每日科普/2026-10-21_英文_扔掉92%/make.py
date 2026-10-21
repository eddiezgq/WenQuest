"""Daily science short 2026-10-21 (English): "Google's Quantum Chip Throws Away 92%"
News (Digg Science front page: ~1.6M views, 20K likes, 14 sources): Google Quantum AI, Science, 2026-10-15,
"Magic state cultivation on a superconducting quantum processor" (Willow chip).
Sources: Quantum Computing Report 2026-10-15 (quantumcomputingreport.com/google-quantum-ai-demonstrates-magic-state-cultivation-on-willow-processor-in-science-milestone/):
first hardware demo of cultivation; 40-fold error reduction vs un-cultivated states; 99.99% logical fidelity for T-states (error ~1e-4);
8% of attempts retained (so ~92% discarded); distance-3 color code grafted into distance-5 surface code; traditional distillation
"projected to consume 90% to 95% of a quantum computer's total physical qubit footprint"; cultivation uses a fraction of that footprint.
TechRepublic "Google Willow Cuts Magic-State Errors 40-Fold"; digg.com/science/f54bt7m8 (Sundar Pichai: first demonstration on physical hardware).
Science (textbook): qubits are fragile (noise -> errors); error correction spreads one logical qubit over many physical qubits;
Clifford gates are "easy" in error-corrected codes, a non-Clifford ingredient (T / magic state) is needed for universal computing.
Analogies (ours): spinning coin, friends remembering a phone number, yeast in bread, tossing burnt cookies, checking parts before building a car.
Character: Qubie, a little qubit (a spinning coin with a face). Running gag: Qubie is scared of the trash can; Qubie survives. No hand.
    python3 make.py <kokoro model dir> | --boards-only   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("谷歌的量子芯片，刚刚把92%的成果扔掉了。|故意的。", "Google's quantum chip just threw away 92 percent of its work. | On purpose."),
 ("而且这是个好消息。|登上了《科学》杂志。", "And that's the good news. | It made the journal Science."),
 ("今天的问题：一台电脑，|怎么靠“扔东西”变强？", "Today's question: how does a computer | get better by throwing things away?"),
 ("认识一下小比特。|它是一个量子比特，非常非常脆弱。", "Meet Qubie. | Qubie is a qubit, and Qubie is very, very fragile."),
 ("普通的比特像电灯开关：|0 或者 1。", "A normal bit is like a light switch: | zero or one."),
 ("量子比特更像一枚旋转的硬币：|看之前，两样都沾一点。", "A qubit is more like a spinning coin: | a bit of both, until you look."),
 ("可一点点热、一点点噪声，|硬币就转歪了。", "But a little heat or a little noise, | and the coin wobbles off course."),
 ("这就是错误。|量子芯片犯的错可多了。", "That's an error. | And quantum chips make lots of them."),
 ("所以谷歌把很多量子比特编成一组，|当一个结实的“逻辑比特”用。", "So Google groups many qubits together | to act like one sturdy logical qubit."),
 ("就像一群朋友，|一起记一个电话号码。", "Like a group of friends | remembering one phone number together."),
 ("反转一：这一组人做简单动作很拿手，|但不是所有动作都行。", "Twist one: the team is great at the easy moves, | but not every move."),
 ("想算任何题目，|还缺一样特殊材料。", "To compute anything at all, | it needs one special ingredient."),
 ("物理学家管它叫“魔法态”。|没错，真叫这个名字。", "Physicists call it a magic state. | Yes, that's the real name."),
 ("就像面包里的酵母：|没有它，面发不起来。", "Think of it as the yeast in bread: | without it, nothing rises."),
 ("麻烦是：魔法态刚做出来，|总是乱糟糟的，全是错。", "The problem: fresh magic states come out messy, | full of errors."),
 ("老办法叫“蒸馏”：做一大堆烂的，|再熬成几个好的。", "The old fix is called distillation: make lots of messy ones, | then boil them down to a few good ones."),
 ("有估算说，它可能要吃掉|一台量子计算机90%到95%的比特。", "Some estimates say it could eat up | 90 to 95 percent of a quantum computer's qubits."),
 ("反转二：谷歌这次试了个新办法，|叫“培育”。", "Twist two: this time Google tried a new trick | called cultivation."),
 ("在一小块地方，种出一个魔法态，|一边长，一边检查。", "Grow one magic state in a small patch, | and keep checking it as it grows."),
 ("只要有一项检查不对劲，|扔掉，重来。", "If any check looks wrong, | toss it and start over."),
 ("就像烤饼干，|稍微有点焦的，统统扔掉。", "Like baking cookies, | and tossing every one that looks even a little burnt."),
 ("最后只留下大约8%，|92%进了垃圾桶。", "Only about 8 percent survive. | 92 percent go in the trash."),
 ("可留下来的特别好：|保真度99.99%。", "But the survivors are excellent: | 99.99 percent fidelity."),
 ("差不多一万次|才错一次。", "That's roughly one error | in ten thousand."),
 ("比不培育的，|错误少了大约40倍。", "Compared with no cultivation, | errors drop about 40 times."),
 ("而且它只占芯片的一个小角落，|不用占掉大半台机器。", "And it fits in a small corner of the chip, | instead of most of the machine."),
 ("反转三，最反直觉：|扔掉很便宜，犯错很贵。", "Twist three, the weird part: | throwing away is cheap. Mistakes are expensive."),
 ("失败一次，只浪费一眨眼。|藏着一个错，能毁掉整道题。", "A failed try wastes a blink. | One hidden error can ruin a whole calculation."),
 ("这就是为什么工厂|先检查零件，再装汽车。", "That's why factories | check the parts before building the car."),
 ("这块芯片叫 Willow。|谷歌说，这是培育第一次在真硬件上跑通。", "The chip is called Willow. | Google says it's the first time cultivation ran on real hardware."),
 ("友情提示：这只是一样材料，|不是一台造好的量子计算机。", "Friendly fine print: this is one ingredient, | not a finished quantum computer."),
 ("真正有用的量子计算机，|还需要多得多、好得多的比特。", "Truly useful quantum computers still need | many more, much better qubits."),
 ("所以不，它明天|破解不了你的密码。", "So no, it won't crack | your password tomorrow."),
 ("小比特通过了检查。|现在它骄傲得不得了。", "Qubie passed every check. | Qubie is now unbearable."),
]
TITLE = {"zh": "谷歌芯片为什么扔掉92%", "en": "Google's Quantum Chip Throws Away 92%"}
import math  # noqa: E402


def qubie(a, x, y, k=1.0, c="blue", scared=False):
    """Qubie: a spinning coin with a face; the arrow on its body spins, the coin wobbles."""
    i = uid("qb") + "_"
    ar = i + "a"
    E = [O(a, x, y, 120 * k, c=c, fill="muted", idp=i), O(a, x, y, 95 * k, c=c, idp=i),
         O(a, x - 35 * k, y - 25 * k, 12 * k, c="ink", fill="ink", idp=i), O(a, x + 35 * k, y - 25 * k, 12 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x - 30 * k},{y + 35 * k} Q{x},{y + (15 if scared else 60) * k} {x + 30 * k},{y + 35 * k}", c="ink", w=4, idp=i),
         P(a, f"M{x},{y - 120 * k} L{x},{y - 200 * k} M{x - 18 * k},{y - 180 * k} L{x},{y - 205 * k} L{x + 18 * k},{y - 180 * k}", c="red", w=6, idp=ar),
         bob(a, i, 7 * k, 1.3), wig(a, i, (x, y + 120 * k), 6, 1.2), wig(a, ar, (x, y - 120 * k), 25, 1.0)]
    return E, i


def coin(a, x, y, r=90, d=0.0, c="gold"):
    i = uid("cn")
    return [O(a, x, y, r, c=c, fill=c, idp=i), P(a, f"M{x},{y - r * .6} L{x},{y + r * .6}", c="ink", w=5, idp=i), pop(a, i, d), spin(a, i, (x, y), 90)]


def friend(a, x, y, k=1.0, c="ink"):
    i = uid("fr")
    return [O(a, x, y - 130 * k, 45 * k, c=c, idp=i), P(a, f"M{x},{y - 85 * k} L{x},{y + 40 * k} M{x - 60 * k},{y - 40 * k} L{x + 60 * k},{y - 40 * k} "
                                                          f"M{x},{y + 40 * k} L{x - 45 * k},{y + 130 * k} M{x},{y + 40 * k} L{x + 45 * k},{y + 130 * k}", c=c, w=6, idp=i),
            bob(a, i, 5, 1.0 + 0.1 * (int(x) % 5)), wig(a, i, (x, y + 130 * k), 4, 1.3)]


def cookie(a, x, y, r=60, d=0.0, burnt=False):
    i = uid("ck")
    c = "ink" if burnt else "gold"
    E = [O(a, x, y, r, c=c, fill="muted" if burnt else "gold", idp=i)]
    for q in range(3):
        E.append(O(a, x - r * .4 + r * .4 * q, y - r * .2 + r * .3 * (q % 2), r * .12, c="ink", fill="ink", idp=i))
    return E + [pop(a, i, d), wig(a, i, (x, y), 6, 1.5)]


def trash(a, x, y, k=1.0, d=None):
    i = uid("bin")
    E = [R(a, x - 130 * k, y - 160 * k, 260 * k, 320 * k, c="ink", fill="muted", idp=i), P(a, f"M{x - 160 * k},{y - 180 * k} L{x + 160 * k},{y - 180 * k}", c="ink", w=8, idp=i),
         wig(a, i, (x, y + 160 * k), 4, 2.0)]
    if d is not None:
        E.append(pop(a, i, d))
    return E, i


def chip(a, x, y, k=1.0, d=0.0):
    i, core = uid("chip"), uid("core")
    E = [R(a, x - 180 * k, y - 180 * k, 360 * k, 360 * k, c="ink", idp=i)]
    for q in range(5):
        o = -140 * k + 70 * k * q
        E.append(P(a, f"M{x + o},{y - 180 * k} L{x + o},{y - 230 * k} M{x + o},{y + 180 * k} L{x + o},{y + 230 * k} M{x - 180 * k},{y + o} L{x - 230 * k},{y + o} "
                      f"M{x + 180 * k},{y + o} L{x + 230 * k},{y + o}", c="ink", w=4, idp=i))
    E += [R(a, x - 90 * k, y - 90 * k, 180 * k, 180 * k, c="blue", fill="blue", idp=core), pop(a, i, d), pulse(a, core, d + 0.5), pulse(a, core, d + 1.3), bob(a, i, 4, 0.8)]
    return E, i


def grid(a, x0, y0, cols, rows, gap=90, r=26, d=0.0, step=0.02, c="blue"):
    E = []
    for r_ in range(rows):
        for q in range(cols):
            i = uid("g")
            E += [O(a, x0 + q * gap, y0 + r_ * gap, r, c=c, fill=c if (r_ + q) % 3 else None, idp=i), pop(a, i, d + step * (r_ * cols + q)),
                  bob(a, i, 4, 1.0 + 0.1 * ((r_ + q) % 4))]
    return E


def noise(a, x, y, n=4, d=0.2, c="red"):
    """Zigzag noise bolts flying in."""
    E = []
    for q in range(n):
        i = uid("nz")
        ang = q * 2 * math.pi / n
        sx, sy = x + 320 * math.cos(ang), y + 320 * math.sin(ang)
        E += [P(a, f"M{sx},{sy} l20,-30 l20,30 l20,-30", c=c, w=5, idp=i), pop(a, i, d + 0.1 * q), sh(a, i, (x - sx) * 0.5, (y - sy) * 0.5, d + 0.15 * q, 0.8)]
    return E


def bread(a, x, y, k=1.0, risen=True, d=0.0):
    i = uid("brd")
    h = (170 if risen else 70) * k
    return [P(a, f"M{x - 200 * k},{y} L{x - 200 * k},{y - h * 0.5} Q{x - 200 * k},{y - h} {x},{y - h} Q{x + 200 * k},{y - h} {x + 200 * k},{y - h * 0.5} L{x + 200 * k},{y} Z",
              c="gold", w=6, fill="gold", idp=i), pop(a, i, d), bob(a, i, 4, 1.0)]


def bubbles_(a, x, y, n=4, d=0.2, c="gold"):
    E = []
    for q in range(n):
        i = uid("bu")
        E += [O(a, x + 50 * (q - n / 2), y, 14 + 4 * (q % 2), c=c, idp=i), sh(a, i, 0, -200, d + 0.25 * q, 1.2)]
    return E


def flask(a, x, y, d=0.0, c="blue"):
    i, liq = uid("fl"), uid("liq")
    return [P(a, f"M{x - 50},{y - 200} L{x - 50},{y - 60} L{x - 160},{y + 140} L{x + 160},{y + 140} L{x + 50},{y - 60} L{x + 50},{y - 200}", c="ink", w=6, idp=i),
            P(a, f"M{x - 120},{y + 70} L{x + 120},{y + 70} L{x + 160},{y + 140} L{x - 160},{y + 140} Z", c=c, w=4, fill=c, idp=liq),
            pop(a, i, d), wig(a, liq, (x, y + 140), 3, 2.0), bob(a, i, 4, 0.9)]


def dot(a, x, y, r, dx, dy, d, c="blue"):
    i = uid("dot")
    return [O(a, x, y, r, c=c, fill=c, idp=i), sh(a, i, dx, dy, d, 0.6)]


def gear(a, x, y, s, d, c="ink", rpm=50):
    i = uid("gear")
    return [{"t": "icon", "at": a, "id": i, "name": "gear", "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), spin(a, i, (x, y), rpm)]


def amb(a, n=2):
    E = star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    if n > 2:
        E += star(a, 1810, 900, 0.5, r=20)
    return E


B = []


def bd(a, *parts, n=2):
    E = []
    for p in parts:
        E += p
    B.append(E + amb(a, n))


Q = lambda a, x, y, s=200, d=0.4: (lambda q: [{"t": "icon", "at": a, "id": q, "name": "question", "x": x, "y": y, "size": s, "c": "red"}, pop(a, q, d),  # noqa: E731
                                              wig(a, q, (x + s / 2, y + s / 2), 8, 1.4)])(uid("q"))


def tossing(a, items, bx, by, d=0.3):
    """Move each (id, x, y) into the bin at (bx, by), one after another, tumbling."""
    E = []
    for q, (i, x, y) in enumerate(items):
        E += [sh(a, i, bx - x, by - y, d + 0.18 * q, 0.5), rot(a, i, 120, (x, y), d + 0.18 * q, 0.5)]
    return E


# 0 threw away 92%
c_, ci = chip(0, 520, 520, 1.1)
b_, bi = trash(0, 1550, 640, 1.0)
E = []
for q in range(5):
    i = uid("bit")
    E += [O(0, 820 + 110 * q, 300, 34, c="blue", fill="blue", idp=i), pop(0, i, 0.05 * q), sh(0, i, 1550 - 820 - 110 * q, 340, 0.4 + 0.15 * q, 0.5)]
bd(0, c_, b_, E, BIG(0, 1100, 820, "92%", c="red", d=0.5, s=160))
# 0.5 on purpose
q_, qi = qubie(0.5, 700, 620, 1.3)
bd(0.5, q_, BIG(0.5, 1350, 450, "on purpose", c="red", d=0.2, s=110), check(0.5, 1350, 650, d=0.7), [sh(0.5, qi + "*", 0, -40, 0.5, 0.3), sh(0.5, qi + "*", 0, 40, 0.8, 0.3)])
# 1 good news
bd(1, [e for q in range(4) for e in star(1, 500 + 300 * q, 400 + 80 * (q % 2), 0.1 + 0.15 * q, r=50)], BIG(1, 960, 700, "good news!", c="green", d=0.4, s=130), n=3)
# 1.5 journal Science
E = []
for q in range(3):
    pg = uid("pg")
    E += [R(1.5, 700 + 30 * q, 260 + 20 * q, 460, 560, c="ink", fill="muted" if q == 2 else None, idp=pg), pop(1.5, pg, 0.1 + 0.2 * q),
          rot(1.5, pg, 4 * (q - 1), (930, 820), 0.5 + 0.2 * q, 0.4)]
bd(1.5, E, BIG(1.5, 990, 520, "Science", c="ink", d=0.6, s=100), T(1.5, 990, 920, 52, "Oct 15, 2026", c="red", d=0.8), n=3)
# 2 how does a computer
cp = uid("pc")
bd(2, [{"t": "icon", "at": 2, "id": cp, "name": "computer", "x": 700, "y": 500, "size": 380, "c": "ink"}, pop(2, cp, 0.0), bob(2, cp, 6, 1.0), wig(2, cp, (700, 690), 3, 1.2)],
   Q(2, 1200, 300, d=0.4), T(2, 1400, 760, 60, "get better?", c="blue", d=0.5))
# 2.5 by throwing away
b_, bi = trash(2.5, 1350, 620, 1.1, d=0.1)
cp = uid("pc")
bd(2.5, [{"t": "icon", "at": 2.5, "id": cp, "name": "computer", "x": 600, "y": 500, "size": 320, "c": "ink"}, pop(2.5, cp, 0.0), bob(2.5, cp, 6, 1.0)], b_,
   arr(2.5, 800, 500, 1150, 560, c="red", d=0.4), T(2.5, 960, 900, 60, "by throwing things away?", c="red", d=0.6))
# 3 meet Qubie
q_, qi = qubie(3, 960, 600, 1.8)
bd(3, q_, [pop(3, qi + "*", 0.0)], BIG(3, 1500, 360, "Qubie", c="blue", d=0.4, s=140), star(3, 500, 300, 0.6, r=40), n=3)
# 3.5 very fragile
q_, qi = qubie(3.5, 960, 620, 1.4, scared=True)
bd(3.5, q_, [wig(3.5, qi + "*", (960, 780), 5, 4.0)], T(3.5, 960, 900, 64, "very, very fragile", c="red", d=0.4),
   [e for q in range(3) for e in dot(3.5, 1180 + 50 * q, 400 + 30 * q, 12, 0, 160, 0.3 + 0.25 * q, c="blue")])
# 4 light switch
sw, kn = uid("sw"), uid("knob")
bd(4, [R(4, 560, 300, 260, 420, c="ink", idp=sw), R(4, 640, 360, 100, 150, c="gold", fill="gold", idp=kn), sh(4, kn, 0, 150, 0.4, 0.3), sh(4, kn, 0, -150, 1.0, 0.3),
       bob(4, sw, 4, 0.9)], [{"t": "icon", "at": 4, "id": (lb := uid("lb")), "name": "sun", "x": 1300, "y": 420, "size": 260, "c": "gold"}, pulse(4, lb, 0.4), pulse(4, lb, 1.1),
                             spin(4, lb, (1300, 420), 20)], T(4, 960, 860, 60, "a normal bit", c="ink", d=0.2))
# 4.5 zero or one
bd(4.5, BIG(4.5, 600, 480, "0", c="blue", d=0.1, s=220), BIG(4.5, 1320, 480, "1", c="red", d=0.5, s=220), T(4.5, 960, 480, 64, "or", c="ink", d=0.3),
   [pulse(4.5, "big0", 0.0)] and coin(4.5, 960, 800, r=60, d=0.6))
# 5 spinning coin
bd(5, coin(5, 700, 500, r=170, d=0.0), qubie(5, 1400, 620, 0.9)[0], T(5, 700, 820, 60, "a spinning coin", c="gold", d=0.3))
# 5.5 bit of both
bd(5.5, BIG(5.5, 500, 480, "0", c="blue", d=0.1, s=180), coin(5.5, 960, 480, r=140, d=0.2), BIG(5.5, 1420, 480, "1", c="red", d=0.3, s=180),
   T(5.5, 960, 800, 60, "a bit of both", c="ink", d=0.5), [{"t": "icon", "at": 5.5, "id": (ey := uid("ey")), "name": "eye", "x": 1500, "y": 820, "size": 140, "c": "ink"},
                                                         pop(5.5, ey, 0.9), wig(5.5, ey, (1500, 820), 6, 1.5)])
# 6 heat noise
bd(6, coin(6, 960, 500, r=140, d=0.0), noise(6, 960, 500, n=5, d=0.2), [{"t": "icon", "at": 6, "id": (fl := uid("fl")), "name": "flame", "x": 400, "y": 800, "size": 160, "c": "red"},
                                                                         pop(6, fl, 0.3), wig(6, fl, (400, 880), 8, 3.0)], T(6, 1450, 820, 56, "heat, noise", c="red", d=0.5))
# 6.5 wobbles off course
cc = coin(6.5, 900, 500, r=140, d=0.0)
bd(6.5, cc, [rot(6.5, cc[0]["id"], 40, (900, 640), 0.2, 0.6), sh(6.5, cc[0]["id"], 300, 120, 0.6, 0.8)], T(6.5, 960, 860, 60, "wobble...", c="red", d=0.4),
   noise(6.5, 900, 500, n=3, d=0.1))
# 7 that's an error
bd(7, coin(7, 600, 500, r=120, d=0.0), cross(7, 600, 500, d=0.4), BIG(7, 1300, 480, "ERROR", c="red", d=0.3, s=150))
# 7.5 lots of them
E = []
for q in range(12):
    E += cross(7.5, 360 + 110 * (q % 6) * 2, 320 + 220 * (q // 6), d=0.05 * q)
bd(7.5, E, [e for q in range(3) for e in coin(7.5, 500 + 460 * q, 850, r=50, d=0.3 + 0.2 * q)], T(7.5, 960, 200, 60, "lots of them", c="red", d=0.2))
# 8 groups many qubits
bd(8, grid(8, 560, 300, 5, 5, gap=100, r=28, d=0.0), [R(8, 500, 240, 520, 520, c="red", idp=(gb := uid("gb"))), pop(8, gb, 0.7), pulse(8, gb, 1.2)],
   T(8, 1450, 500, 60, "many qubits", c="blue", d=0.3))
# 8.5 sturdy logical qubit
E = grid(8.5, 360, 360, 4, 4, gap=80, r=22, d=0.0)
q_, qi = qubie(8.5, 1400, 560, 1.3)
bd(8.5, E, arr(8.5, 720, 480, 1150, 520, c="ink", d=0.3), q_, [pop(8.5, qi + "*", 0.5)], T(8.5, 1400, 880, 56, "one logical qubit", c="green", d=0.7))
# 9 group of friends
E = []
for q in range(5):
    E += friend(9, 400 + 280 * q, 620, 1.0)
bd(9, E, T(9, 960, 220, 64, "a group of friends", c="ink", d=0.3))
# 9.5 phone number
E = []
for q, dg in enumerate(["5", "5", "5", "0", "1"]):
    E += friend(9.5, 400 + 280 * q, 720, 0.8)
    E += BIG(9.5, 400 + 280 * q, 380, dg, c="blue", d=0.1 + 0.15 * q, s=110)
ph = uid("ph")
bd(9.5, E, [{"t": "icon", "at": 9.5, "id": ph, "name": "phone", "x": 1750, "y": 300, "size": 160, "c": "ink"}, pop(9.5, ph, 0.9), wig(9.5, ph, (1750, 380), 8, 3.0)])
# 10 twist one: easy moves
E = []
for q in range(3):
    E += friend(10, 600 + 360 * q, 640, 1.0)
bd(10, BIG(10, 960, 160, "TWIST 1", c="red", d=0.1, s=90), E, [e for q in range(3) for e in check(10, 600 + 360 * q, 360, d=0.4 + 0.2 * q)])
# 10.5 not every move
E = []
fi_ = []
for q in range(3):
    f_ = friend(10.5, 600 + 360 * q, 640, 1.0)
    E += f_
    fi_.append(f_[0]["id"])
bd(10.5, E, [rot(10.5, fi_[1], 60, (960, 770), 0.4, 0.5)], cross(10.5, 960, 340, d=0.6), T(10.5, 1500, 340, 56, "not every move", c="red", d=0.5))
# 11 compute anything
c_, ci = chip(11, 650, 520, 1.0)
bd(11, c_, [e for q, s_ in enumerate(["+", "×", "√"]) for e in BIG(11, 1150 + 220 * q, 450, s_, c="blue", d=0.2 + 0.2 * q, s=120)],
   T(11, 1370, 700, 56, "anything at all", c="ink", d=0.6))
# 11.5 special ingredient
bd(11.5, flask(11.5, 700, 520, d=0.0, c="gold"), bubbles_(11.5, 700, 420, n=4, d=0.3), Q(11.5, 1200, 300, d=0.5), T(11.5, 1400, 760, 56, "one special ingredient", c="gold", d=0.6))
# 12 magic state
bd(12, flask(12, 600, 520, d=0.0, c="red"), [e for q in range(4) for e in star(12, 450 + 100 * q, 260 - 30 * (q % 2), 0.2 + 0.1 * q, r=30)],
   BIG(12, 1300, 480, "magic state", c="red", d=0.4, s=110))
# 12.5 real name
q_, qi = qubie(12.5, 700, 620, 1.3)
bd(12.5, q_, [rot(12.5, qi + "*", -10, (700, 740), 0.3, 0.4), rot(12.5, qi + "*", 0, (700, 740), 0.8, 0.4)], T(12.5, 1350, 450, 64, "yes, really.", c="ink", d=0.3),
   check(12.5, 1350, 650, d=0.7))
# 13 yeast in bread
bd(13, bread(13, 960, 700, 1.4, risen=False, d=0.0), bubbles_(13, 960, 600, n=5, d=0.3), T(13, 960, 260, 64, "yeast", c="gold", d=0.2),
   [{"t": "move", "at": 13, "kind": "grow", "targets": [], "axis": "y", "from": 1.0, "to": 1.0, "pivot": [0, 0], "dur": 0.1}][:0])
# 13.5 nothing rises
b1 = bread(13.5, 600, 700, 1.0, risen=True, d=0.0)
b2 = bread(13.5, 1350, 700, 1.0, risen=False, d=0.2)
bd(13.5, b1, b2, [{"t": "move", "at": 13.5, "kind": "grow", "targets": [b1[0]["id"]], "axis": "y", "from": 0.4, "to": 1.0, "pivot": [600, 700], "dur": 1.0, "delay": 0.2}],
   check(13.5, 600, 360, d=0.8), cross(13.5, 1350, 460, d=0.9), T(13.5, 1350, 860, 52, "no yeast", c="red", d=0.5))
# 14 messy
bd(14, flask(14, 700, 520, d=0.0, c="red"), noise(14, 700, 520, n=5, d=0.2), T(14, 1400, 500, 64, "messy", c="red", d=0.4))
# 14.5 full of errors
E = []
for q in range(8):
    E += cross(14.5, 500 + 130 * q, 400 + 120 * (q % 3), d=0.08 * q)
bd(14.5, E, flask(14.5, 960, 760, d=0.0, c="red"), T(14.5, 1550, 860, 56, "full of errors", c="red", d=0.6))
# 15 distillation lots of messy ones
E = []
for q in range(8):
    E += flask(15, 300 + 190 * q, 560, d=0.06 * q, c="red")
bd(15, E, T(15, 960, 220, 60, "distillation", c="ink", d=0.2), T(15, 960, 860, 52, "make lots of messy ones", c="red", d=0.6))
# 15.5 boil down to a few good
E = []
for q in range(6):
    i = uid("dr")
    E += [O(15.5, 400 + 100 * q, 300, 26, c="red", fill="red", idp=i), pop(15.5, i, 0.05 * q), sh(15.5, i, 960 - 400 - 100 * q, 260, 0.2 + 0.1 * q, 0.6)]
bd(15.5, E, flask(15.5, 960, 600, d=0.0, c="green"), [{"t": "icon", "at": 15.5, "id": (fl := uid("fl")), "name": "flame", "x": 960, "y": 880, "size": 140, "c": "red"},
                                                       pop(15.5, fl, 0.1), wig(15.5, fl, (960, 940), 8, 3.0)], T(15.5, 1500, 600, 56, "a few good ones", c="green", d=0.8))
# 16 estimates say eat up
c_, ci = chip(16, 650, 520, 1.1)
mon = uid("mon")
bd(16, c_, [O(16, 1300, 500, 150, c="red", fill="red", idp=mon), P(16, "M1220,520 L1260,560 L1300,520 L1340,560 L1380,520", c="ink", w=5, idp=mon), pop(16, mon, 0.3),
            wig(16, mon, (1300, 650), 8, 2.5), sh(16, mon, -300, 0, 0.8, 0.8)], T(16, 1300, 820, 52, "some estimates", c="muted", d=0.2))
# 16.5 90-95%
bd(16.5, bar(16.5, 500, 860, 220, 560, "red", d=0.1, dur=1.0), bar(16.5, 760, 860, 220, 50, "blue", d=0.3), T(16.5, 610, 920, 44, "magic factory", c="red"),
   T(16.5, 870, 920, 44, "the rest", c="blue"), BIG(16.5, 1400, 480, "90–95%", c="red", d=0.6, s=130))
# 17 twist two new trick
q_, qi = qubie(17, 700, 640, 1.2)
bd(17, BIG(17, 960, 160, "TWIST 2", c="red", d=0.1, s=90), q_, [{"t": "icon", "at": 17, "id": (lt := uid("lt")), "name": "sun", "x": 1300, "y": 460, "size": 220, "c": "gold"},
                                                              pop(17, lt, 0.4), spin(17, lt, (1300, 460), 40)], T(17, 1350, 760, 56, "new trick", c="ink", d=0.6))
# 17.5 cultivation
sprout, lf = uid("spr"), uid("leaf")
bd(17.5, [P(17.5, "M960,820 L960,520", c="green", w=8, idp=sprout), P(17.5, "M960,600 Q860,520 820,600 Q880,640 960,600 M960,560 Q1060,480 1100,560 Q1040,600 960,560",
                                                                         c="green", w=6, fill="green", idp=lf),
          {"t": "move", "at": 17.5, "kind": "grow", "targets": [sprout], "axis": "y", "from": 0.2, "to": 1.0, "pivot": [960, 820], "dur": 0.8, "delay": 0.1},
          pop(17.5, lf, 0.7), wig(17.5, lf, (960, 600), 8, 1.5)], [R(17.5, 760, 820, 400, 120, c="ink", fill="muted", idp=(pt := uid("pot"))), bob(17.5, pt, 3, 0.8)],
   BIG(17.5, 960, 280, "cultivation", c="green", d=0.4, s=110))
# 18 small patch
E = grid(18, 760, 380, 4, 4, gap=90, r=24, d=0.0, c="muted")
bd(18, E, [R(18, 830, 450, 200, 200, c="green", idp=(pa := uid("pa"))), pop(18, pa, 0.3), pulse(18, pa, 0.8)], flask(18, 1450, 560, d=0.5, c="gold"),
   T(18, 930, 860, 56, "a small patch", c="green", d=0.4))
# 18.5 checking as it grows
q_, qi = qubie(18.5, 700, 620, 1.0)
gq = uid("grw")
bd(18.5, q_, [{"t": "move", "at": 18.5, "kind": "grow", "targets": [qi], "axis": "both", "from": 0.6, "to": 1.2, "pivot": [700, 740], "dur": 1.2, "delay": 0.1}],
   [e for q in range(3) for e in check(18.5, 1150 + 200 * q, 450, d=0.3 + 0.3 * q)], T(18.5, 1350, 700, 56, "check, check, check", c="green", d=0.4))
# 19 any check wrong
bd(19, check(19, 600, 450, d=0.0), check(19, 850, 450, d=0.2), cross(19, 1100, 450, d=0.5), [{"t": "icon", "at": 19, "id": (ey := uid("ey")), "name": "eye", "x": 1450, "y": 450,
                                                                                            "size": 200, "c": "ink"}, pop(19, ey, 0.3), wig(19, ey, (1450, 450), 6, 2.0)],
   T(19, 960, 760, 60, "any check looks wrong?", c="red", d=0.4))
# 19.5 toss and start over
b_, bi = trash(19.5, 1450, 640, 1.0)
q_, qi = qubie(19.5, 600, 600, 0.8, scared=True)
fl_ = flask(19.5, 900, 500, d=0.0, c="red")
bd(19.5, b_, q_, fl_, tossing(19.5, [(fl_[0]["id"], 900, 500)], 1450, 600, d=0.3), T(19.5, 960, 900, 60, "toss it. start over.", c="red", d=0.6))
# 20 baking cookies
E = []
for q in range(6):
    E += cookie(20, 500 + 180 * q, 520 + 60 * (q % 2), r=70, d=0.05 * q, burnt=(q in (1, 4)))
tray = uid("tray")
bd(20, [P(20, "M380,640 L1500,640", c="ink", w=8, idp=tray), bob(20, tray, 3, 0.8)], E, T(20, 960, 260, 64, "baking cookies", c="gold", d=0.3))
# 20.5 toss burnt ones
E, items = [], []
for q in range(6):
    burnt = q != 2
    ck_ = cookie(20.5, 400 + 170 * q, 400, r=60, d=0.0, burnt=burnt)
    E += ck_
    if burnt:
        items.append((ck_[0]["id"], 400 + 170 * q, 400))
b_, bi = trash(20.5, 1600, 700, 0.9)
bd(20.5, E, b_, tossing(20.5, items, 1600, 650, d=0.2), T(20.5, 800, 860, 52, "even a little burnt", c="red", d=0.3))
# 21 only 8% survive
E = []
for q in range(25):
    i = uid("d")
    keep = q in (6, 18)
    E += [O(21, 500 + 110 * (q % 5) * 1.0, 260 + 110 * (q // 5), 32, c="green" if keep else "muted", fill="green" if keep else None, idp=i), pop(21, i, 0.02 * q)]
    if keep:
        E.append(pulse(21, i, 0.9))
    else:
        E.append(sh(21, i, 0, 700, 0.6 + 0.02 * q, 0.6))
bd(21, E, BIG(21, 1450, 480, "8%", c="green", d=0.4, s=170))
# 21.5 92% trash
b_, bi = trash(21.5, 700, 640, 1.4)
bd(21.5, b_, [e for q in range(5) for e in dot(21.5, 450 + 120 * q, 200, 30, 700 - 450 - 120 * q, 380, 0.1 + 0.12 * q, c="muted")],
   BIG(21.5, 1400, 480, "92%", c="red", d=0.3, s=170), [pulse(21.5, bi, 0.9)])
# 22 survivors excellent
q_, qi = qubie(22, 700, 620, 1.3)
bd(22, q_, [e for q in range(3) for e in star(22, 500 + 200 * q, 280, 0.2 + 0.15 * q, r=36)], T(22, 1400, 480, 64, "excellent", c="green", d=0.4), check(22, 1400, 680, d=0.8))
# 22.5 99.99%
bd(22.5, BIG(22.5, 960, 420, "99.99%", c="green", d=0.1, s=170), T(22.5, 960, 640, 60, "fidelity", c="ink", d=0.5), bar(22.5, 860, 900, 200, 180, "green", d=0.6),
   star(22.5, 400, 400, 0.4, r=40))
# 23 roughly one error
bd(23, cross(23, 960, 480, d=0.1), BIG(23, 960, 720, "1 error", c="red", d=0.3, s=120), coin(23, 500, 500, r=70, d=0.5), coin(23, 1420, 500, r=70, d=0.6))
# 23.5 in ten thousand
bd(23.5, grid(23.5, 360, 260, 13, 6, gap=95, r=18, d=0.0, step=0.005, c="green"), BIG(23.5, 960, 880, "in 10,000", c="green", d=0.6, s=110),
   cross(23.5, 360 + 95 * 7, 260 + 95 * 3, d=0.9))
# 24 compared with no cultivation
bd(24, bar(24, 600, 860, 220, 600, "red", d=0.1, dur=1.0), T(24, 710, 920, 44, "no cultivation", c="red"), Q(24, 1200, 300, d=0.4), T(24, 1400, 700, 52, "errors", c="ink", d=0.3))
# 24.5 40 times fewer
bd(24.5, bar(24.5, 500, 860, 220, 600, "red", d=0.0), bar(24.5, 820, 860, 220, 15, "green", d=0.3), T(24.5, 610, 920, 44, "before", c="red"), T(24.5, 930, 920, 44, "after", c="green"),
   BIG(24.5, 1450, 480, "÷40", c="green", d=0.6, s=170))
# 25 small corner
c_, ci = chip(25, 760, 520, 1.3)
bd(25, c_, [R(25, 560, 320, 120, 120, c="green", fill="green", idp=(cr := uid("cr"))), pop(25, cr, 0.4), pulse(25, cr, 0.9), pulse(25, cr, 1.5)],
   T(25, 1450, 500, 60, "a small corner", c="green", d=0.5))
# 25.5 instead of most of the machine
c_, ci = chip(25.5, 760, 520, 1.3)
bd(25.5, c_, [R(25.5, 540, 300, 440, 440, c="red", fill="red", idp=(cr := uid("cr"))), pop(25.5, cr, 0.1),
              {"t": "move", "at": 25.5, "kind": "grow", "targets": [cr], "axis": "both", "from": 1.0, "to": 0.25, "pivot": [600, 360], "dur": 1.0, "delay": 0.4}],
   cross(25.5, 1450, 400, d=0.3), T(25.5, 1450, 600, 52, "most of the machine", c="red", d=0.2))
# 26 twist three
b_, bi = trash(26, 1300, 640, 1.0)
bd(26, BIG(26, 960, 160, "TWIST 3", c="red", d=0.1, s=90), b_, qubie(26, 650, 620, 1.1, scared=True)[0], Q(26, 900, 300, s=140, d=0.5))
# 26.5 cheap vs expensive
coinz = []
for q in range(4):
    coinz += coin(26.5, 1200 + 140 * q, 300 + 40 * (q % 2), r=50, d=0.5 + 0.12 * q)
bd(26.5, coin(26.5, 500, 400, r=40, d=0.1), T(26.5, 500, 560, 56, "toss = cheap", c="green", d=0.2), coinz, T(26.5, 1400, 560, 56, "mistake = $$$", c="red", d=0.6),
   [{"t": "move", "at": 26.5, "kind": "pulse", "targets": [coinz[0]["id"]], "delay": 1.1, "dur": 0.5}])
# 27 failed try wastes a blink
ey = uid("ey")
bd(27, [{"t": "icon", "at": 27, "id": ey, "name": "eye", "x": 700, "y": 480, "size": 300, "c": "ink"}, pop(27, ey, 0.0),
        {"t": "move", "at": 27, "kind": "grow", "targets": [ey], "axis": "y", "from": 1.0, "to": 0.1, "pivot": [700, 480], "dur": 0.3, "delay": 0.5},
        {"t": "move", "at": 27, "kind": "grow", "targets": [ey], "axis": "y", "from": 0.1, "to": 1.0, "pivot": [700, 480], "dur": 0.3, "delay": 0.8}],
   cross(27, 1300, 400, d=0.3), T(27, 1300, 600, 60, "a blink", c="muted", d=0.4))
# 27.5 hidden error ruins
E = []
for q in range(6):
    i = uid("dom")
    E += [R(27.5, 400 + 200 * q, 400, 50, 240, c="ink", fill="muted", idp=i), pop(27.5, i, 0.02 * q), rot(27.5, i, 70, (450 + 200 * q, 640), 0.4 + 0.15 * q, 0.3)]
bd(27.5, E, cross(27.5, 425, 330, d=0.2), T(27.5, 960, 860, 56, "one hidden error ruins it all", c="red", d=0.5))
# 28 factories
gr = uid("gear")
bd(28, [{"t": "icon", "at": 28, "id": gr, "name": "gear", "x": 650, "y": 480, "size": 320, "c": "ink"}, pop(28, gr, 0.0), spin(28, gr, (650, 480), 40)],
   [{"t": "icon", "at": 28, "id": (gr2 := uid("gear")), "name": "gear", "x": 870, "y": 650, "size": 200, "c": "blue"}, pop(28, gr2, 0.2), spin(28, gr2, (870, 650), -60)],
   T(28, 1400, 500, 64, "factories", c="ink", d=0.3))
# 28.5 check parts before car
car = uid("car")
bd(28.5, [e for q in range(3) for e in check(28.5, 450 + 160 * q, 400, d=0.1 + 0.2 * q)], arr(28.5, 900, 450, 1150, 450, c="ink", d=0.6),
   [{"t": "icon", "at": 28.5, "id": car, "name": "car", "x": 1450, "y": 450, "size": 320, "c": "blue"}, pop(28.5, car, 0.8), sh(28.5, car, 150, 0, 1.1, 0.6)],
   T(28.5, 960, 820, 56, "parts first, then the car", c="ink", d=0.4))
# 29 chip called Willow
c_, ci = chip(29, 650, 520, 1.2, d=0.0)
bd(29, c_, BIG(29, 1350, 450, "Willow", c="blue", d=0.3, s=130), T(29, 1350, 650, 52, "Google Quantum AI", c="muted", d=0.6))
# 29.5 first time on real hardware
c_, ci = chip(29.5, 650, 520, 1.0)
bd(29.5, c_, BIG(29.5, 1350, 420, "FIRST", c="red", d=0.2, s=140), T(29.5, 1350, 620, 52, "on real hardware", c="ink", d=0.5),
   [e for q in range(3) for e in star(29.5, 1150 + 200 * q, 780, 0.6 + 0.1 * q, r=30)])
# 30 fine print one ingredient
bd(30, BIG(30, 960, 180, "fine print", c="muted", d=0.1, s=80), flask(30, 700, 560, d=0.2, c="gold"), T(30, 1350, 560, 60, "one ingredient", c="gold", d=0.4))
# 30.5 not a finished quantum computer
cp = uid("pc")
bd(30.5, [{"t": "icon", "at": 30.5, "id": cp, "name": "computer", "x": 800, "y": 500, "size": 380, "c": "muted"}, pop(30.5, cp, 0.0), wig(30.5, cp, (800, 690), 3, 1.0)],
   cross(30.5, 800, 480, d=0.5), T(30.5, 1450, 500, 52, "not finished", c="red", d=0.4), [e for q in range(2) for e in gear(30.5, 1350 + 200 * q, 750, 120, 0.6 + 0.2 * q)])
# 31 truly useful needs
bd(31, qubie(31, 600, 620, 1.0)[0], arr(31, 800, 600, 1100, 600, c="ink", d=0.3), Q(31, 1300, 400, d=0.5), T(31, 960, 200, 56, "truly useful?", c="ink", d=0.2))
# 31.5 many more much better
bd(31.5, grid(31.5, 280, 260, 15, 6, gap=95, r=20, d=0.0, step=0.004), T(31.5, 960, 880, 60, "many more, much better", c="blue", d=0.5), n=3)
# 32 crack password
lk = uid("lock")
bd(32, [R(32, 760, 460, 400, 320, c="gold", fill="gold", idp=lk), P(32, "M840,460 Q840,280 960,280 Q1080,280 1080,460", c="ink", w=12, idp=lk), pop(32, lk, 0.0),
        wig(32, lk, (960, 780), 4, 2.0)], c_ := chip(32, 400, 560, 0.6)[0], arr(32, 560, 560, 740, 600, c="red", d=0.4), T(32, 1450, 560, 56, "crack it?", c="red", d=0.4))
# 32.5 not tomorrow
cal = uid("cal")
bd(32.5, [R(32.5, 560, 280, 400, 420, c="ink", idp=cal), P(32.5, "M560,380 L960,380", c="red", w=10, idp=cal), pop(32.5, cal, 0.0), wig(32.5, cal, (760, 280), 4, 1.0)],
   T(32.5, 760, 540, 60, "tomorrow", c="ink", d=0.2), cross(32.5, 760, 540, d=0.5), BIG(32.5, 1400, 480, "NO", c="red", d=0.6, s=150))
# 33 Qubie passed every check
q_, qi = qubie(33, 760, 620, 1.4)
b_, bi = trash(33, 1500, 660, 0.8)
bd(33, q_, b_, [sh(33, qi + "*", 0, -40, 0.4, 0.3), sh(33, qi + "*", 0, 40, 0.7, 0.3)], [e for q in range(3) for e in check(33, 560 + 200 * q, 260, d=0.3 + 0.2 * q)], n=3)
# 33.5 unbearable
q_, qi = qubie(33.5, 760, 640, 1.5)
crown = uid("crown")
bd(33.5, q_, [P(33.5, "M640,420 L640,320 L700,380 L760,300 L820,380 L880,320 L880,420 Z", c="gold", w=6, fill="gold", idp=crown), sh(33.5, crown, 0, 60, 0.2, 0.5),
              wig(33.5, crown, (760, 420), 8, 1.5)], T(33.5, 1400, 500, 64, "unbearable.", c="red", d=0.5), n=3)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"Qubie": "Cue-bee"})
