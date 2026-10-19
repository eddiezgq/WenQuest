"""Daily science short 2026-10-19 (English): "Science said the world ends Nov 13, 2026?"
News (trending this week): Popular Science 2026-10-13 "In 1960, scientists predicted the world would end on November 13, 2026"
(popsci.com/science/world-end-overpopulation-doomsday-november-2026); ScienceDaily 2026-10-16 reprint of The Conversation piece by
historian Alan MacEachern (sciencedaily.com/releases/2026/10/261016070639.htm) "Scientists predicted doomsday for November 13, 2026.
Should we be worried?"; also WION, Jang, Futura.
Paper: von Foerster, Mora & Amiot, "Doomsday: Friday, 13 November, A.D. 2026", Science, 4 Nov 1960. Formula N = 1.79e11/(2026.87 - t)^0.99;
fitted on 24 population estimates over 2,000 years; proposed halving the birth rate; letters called it "ridiculous"; Time & NYT covered it;
von Foerster was once a stage magician; MacEachern: "a magic trick". Real population ~8.3 billion (UN via PopSci); growth rate peaked early
1960s (Joel Cohen via PopSci); birth rate today slightly less than half the 1960 rate (Our World in Data via MacEachern).
Our own arithmetic (said as "plug in"): formula gives ~0.83 bn (1800), ~1.9 bn (1927), ~3.5 bn (1974), ~2.5 trillion today (2026-10-19),
~300 x real. "The world took their advice" is MacEachern's playful framing, said as "in a way".
Character: Mo, a little stick person (running gag: Mo's relatives keep arriving; Mo is fine at the end). No hand.
    python3 make.py <kokoro model dir> | --fake | --boards-only   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("1960年，三位科学家算了一笔账，|把世界末日定在了2026年11月13日。", "In 1960, three scientists did the math, | and set the end of the world for November 13, 2026."),
 ("离今天不到四个星期。|当然，还是个黑色星期五。", "That's less than four weeks from today. | Friday the 13th, of course."),
 ("论文发在《科学》杂志上，|地球上最受尊敬的期刊之一。", "It was published in Science, | one of the most respected journals on Earth."),
 ("今天的问题：一个正经公式，为什么说我们会被挤死？|我们又为什么还在？", "Today's question: why did a serious formula say we'd be squeezed to death? | And why are we still here?"),
 ("认识一下小莫。小莫只是一个人。|可小莫的亲戚，特别多。", "Meet Mo. Mo is just one person. | But Mo has a lot of relatives."),
 ("1800年前后，地球上大约十亿人。|到1927年，二十亿。", "Around 1800, there were about one billion people. | By 1927, two billion."),
 ("1974年，四十亿。|每翻一倍，都比上一次更快。", "By 1974, four billion. | Each doubling came faster than the last."),
 ("普通的快速增长叫指数增长：|按固定的节奏，翻倍，翻倍，再翻倍。", "Normal fast growth is exponential: | double, double, double, at a steady pace."),
 ("就像利率固定的存款。|会很大，但永远不会无穷大。", "Like a bank account with a fixed interest rate. | It gets huge, but never infinite."),
 ("反转一：他们认为，人类比指数增长还快。", "Twist one: the team thought humans grow even faster than exponential."),
 ("人越多，点子越多，合作越多，|点子越多，增长就越快。", "More people means more ideas and more teamwork, | and more ideas mean even faster growth."),
 ("增长的速度本身也在增长。|数学家管这叫双曲增长。", "So the growth rate itself keeps growing. | Mathematicians call this hyperbolic growth."),
 ("他们的公式：人口等于一个大数，|除以离2026年还剩多少年。", "Their formula: population equals a big number, | divided by the years left until 2026."),
 ("除数越来越小，|答案就冲向无穷大。", "Divide by a smaller and smaller number, | and the answer rockets toward infinity."),
 ("这叫奇点：一个确定的日子，一个无穷大的答案。", "That's a singularity: a definite date with an infinite answer."),
 ("吓人的是：它拟合了两千年的数据，|一共24个世界人口估计值。", "The scary part? It fit two thousand years of data, | 24 estimates of world population."),
 ("1800年，1927年，1974年，|它都算得八九不离十。", "1800, 1927, 1974: | it came surprisingly close every time."),
 ("专家写信说它荒唐。|作者照样据理力争。", "Experts wrote in calling it ridiculous. | The authors fought back."),
 ("反转二：把今天的日期代进公式，|地球上应该有大约两万五千亿人。", "Twist two: plug today's date into the formula, | and Earth should hold about 2.5 trillion people."),
 ("相当于每个真人身边，|再挤上三百个。", "That's three hundred people | for every person actually alive."),
 ("真实的数字呢？大约八十三亿。", "The real number? About 8.3 billion."),
 ("是什么把曲线掰弯了？|不是饥荒，也不是战争。", "So what bent the curve? | Not famine. Not war."),
 ("就在1960年代初，人口增长率到顶，|然后开始往下走。", "Right around the early 1960s, the growth rate peaked, | and then started falling."),
 ("孩子不再早早夭折。|大多数孩子能长大，家庭就选择少生。", "Kids stopped dying young. | And when most kids survive, families choose to have fewer."),
 ("今天全球的出生率，|还不到1960年的一半。", "Today the global birth rate | is less than half of what it was in 1960."),
 ("反转三：作者当年开过一个药方：|把出生率砍掉一半。", "Twist three: the authors had a prescription: | cut the birth rate in half."),
 ("世界差不多真做到了。|某种意义上，预言把自己给破了。", "The world roughly did it. | In a way, the prophecy cancelled itself."),
 ("公式里一出现无穷大，|通常说明模型已经不再描述现实。", "When a formula hits infinity, | it usually means the model has stopped describing reality."),
 ("就像一直吹的气球：|数学说能无限大，橡皮说不行。", "Like a balloon you keep blowing up: | the math says forever, the rubber says no."),
 ("冷知识：第一作者冯·福斯特，|还当过舞台魔术师。", "Fun fact: the lead author, von Foerster, | was once a stage magician."),
 ("一位历史学家说，这篇论文就是个魔术：|普通的内容，惊人的标题。", "One historian called the paper a magic trick: | ordinary math, extraordinary title."),
 ("魔术成功了：《时代》周刊和《纽约时报》都报道了它。", "And the trick worked: Time magazine and the New York Times covered it."),
 ("友情提示：这个公式从来不是真预言，|它是一个关于曲线的警告。", "Friendly fine print: the formula was never a real forecast. | It was a warning about a curve."),
 ("如今人口增长在放慢，|不少国家反倒发愁孩子太少。", "Today population growth is slowing, | and many countries now worry about too few babies."),
 ("所以11月13号，放轻松，小莫没事。|不过那天，重要的事还是别排了。", "So on November 13, relax. Mo is fine. | Maybe just don't schedule anything important."),
]
TITLE = {"zh": "《科学》说2026年11月13日是末日？", "en": "Science said the world ends Nov 13, 2026?"}


def person(a, x, y, k=1.0, c="ink", d=None, hz=1.2):
    """A tiny round person (head + body); pops in at d and bobs."""
    i = uid("pp")
    E = [O(a, x, y - 70 * k, 18 * k, c=c, fill=c, idp=i),
         P(a, f"M{x},{y - 52 * k} L{x},{y - 18 * k} M{x - 20 * k},{y} L{x},{y - 18 * k} L{x + 20 * k},{y} M{x - 22 * k},{y - 42 * k} L{x + 22 * k},{y - 42 * k}",
           c=c, w=4, idp=i), bob(a, i, 4 * k, hz)]
    if d is not None:
        E.append(pop(a, i, d))
    return E


def crowd(a, x, y, cols, rows, gap=60, k=0.8, d=0.2, step=0.06, c="ink"):
    E = []
    n = 0
    for r in range(rows):
        for q in range(cols):
            E += person(a, x + q * gap + (r % 2) * gap / 2, y + r * gap * 1.1, k, c=c, d=d + step * n, hz=0.9 + 0.1 * (n % 5))
            n += 1
    return E


def mo(a, x, y, k=1.0, mood="happy"):
    """Mo: a round-headed stick person with a smile; waves an arm."""
    i, arm = uid("mo"), uid("arm")
    E = [O(a, x, y - 260 * k, 50 * k, c="ink", fill=None, idp=i), O(a, x - 17 * k, y - 270 * k, 6 * k, c="ink", fill="ink", idp=i),
         O(a, x + 17 * k, y - 270 * k, 6 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x - 20 * k},{y - 245 * k} Q{x},{y - 228 * k if mood == 'happy' else y - 255 * k} {x + 20 * k},{y - 245 * k}", c="ink", w=4, idp=i),
         P(a, f"M{x},{y - 210 * k} L{x},{y - 90 * k} M{x - 45 * k},{y} L{x},{y - 90 * k} L{x + 45 * k},{y} M{x},{y - 180 * k} L{x - 60 * k},{y - 120 * k}",
           c="ink", w=5, idp=i),
         P(a, f"M{x},{y - 180 * k} L{x + 70 * k},{y - 240 * k}", c="ink", w=5, idp=arm),
         wig(a, arm, (x, y - 180 * k), 18, 2.2), bob(a, i, 6 * k, 1.3), bob(a, arm, 6 * k, 1.3)]
    return E, i


def axes(a, x0=300, y0=820, w=1300, h=560):
    i = uid("ax")
    return [P(a, f"M{x0},{y0 - h} L{x0},{y0} L{x0 + w},{y0}", c="ink", w=5, idp=i)]


def curve(a, pts, c="red", d=0.2, dur=1.4, w=7):
    """A curve that draws itself left to right (grow along x from its first point)."""
    i = uid("cv")
    return [P(a, "M" + " L".join(f"{p:.0f},{q:.0f}" for p, q in pts), c=c, w=w, idp=i),
            {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "x", "pivot": [pts[0][0], pts[0][1]], "dur": dur, "delay": d}]


def hyper(x0=300, y0=820, w=1200, h=540, n=40, cap=1.0):
    pts = []
    for k in range(n + 1):
        t = k / n * 0.97
        v = min(cap, 0.03 / (1.0 - t))
        pts.append((x0 + w * t, y0 - h * v))
    return pts


def expo(x0=300, y0=820, w=1200, h=540, n=30):
    return [(x0 + w * k / n, y0 - h * (2 ** (5 * k / n) - 1) / 31) for k in range(n + 1)]


def dot(a, x, y, c="red", d=0.0, r=14):
    i = uid("dt")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), pulse(a, i, d + 0.4, 0.8)]


def cal(a, x, y, top, big, d=0.0, k=1.0, c="red"):
    """A calendar page that pops in, then swings."""
    i = uid("cal")
    E = [R(a, x - 150 * k, y - 160 * k, 300 * k, 320 * k, c="ink", idp=i), R(a, x - 150 * k, y - 160 * k, 300 * k, 80 * k, c=c, fill=c, idp=i),
         pop(a, i, d), wig(a, i, (x, y - 160 * k), 4, 1.0)]
    E += T(a, x, y - 125 * k, int(40 * k), top, c="ink", d=d + 0.1) + T(a, x, y + 40 * k, int(130 * k), big, c="ink", d=d + 0.2)
    return E


def book(a, x, y, d=0.0, k=1.0):
    i = uid("bk")
    E = [R(a, x - 170 * k, y - 220 * k, 340 * k, 440 * k, c="ink", fill="muted", idp=i), pop(a, i, d), rot(a, i, -6, (x, y + 220 * k), d + 0.4, 0.6),
         bob(a, i, 6, 0.9)]
    E += T(a, x, y - 140 * k, int(70 * k), "SCIENCE", c="red", d=d + 0.2) + T(a, x, y + 160 * k, int(40 * k), "1960", c="ink", d=d + 0.3)
    return E


def balloon(a, x, y, r, d=0.0, c="red", to=1.6):
    i, s = uid("bl"), uid("str")
    return [O(a, x, y, r, c=c, idp=i), P(a, f"M{x},{y + r} Q{x - 20},{y + r + 80} {x},{y + r + 160}", c="ink", w=3, idp=s),
            {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "both", "from": 0.4, "to": to, "pivot": [x, y + r], "dur": 1.6, "delay": d},
            bob(a, s, 6, 1.0), wig(a, i, (x, y + r), 3, 1.4)]


def amb(a, n=2):
    E = star(a, 110, 110, 0.1, r=20) + star(a, 1810, 990, 0.3, r=20)
    if n > 2:
        E += star(a, 1810, 110, 0.5, r=20)
    return E


B = []


def bd(a, *parts, n=2):
    E = []
    for p in parts:
        E += p
    B.append(E + amb(a, n))


# 0 doomsday date
m, mi = mo(0, 1500, 900, 0.9)
bd(0, cal(0, 700, 470, "NOVEMBER", "13", d=0.2, k=1.3), m, [sh(0, mi + "*", -60, 0, 1.0, 0.6)],
   BIG(0, 700, 900, "2026", c="red", d=0.8, s=130), crowd(0, 1250, 280, 5, 2, k=0.7, d=0.3))
# 0.5 end of the world
bd(0.5, crowd(0.5, 360, 300, 12, 6, gap=100, k=0.9, d=0.0, step=0.03), BIG(0.5, 960, 960, "THE END?", c="red", d=0.6, s=130), n=3)
# 1 four weeks
E = []
for k in range(4):
    i = uid("wk")
    E += [R(1, 330 + 330 * k, 380, 260, 220, c="ink", idp=i), pop(1, i, 0.2 + 0.25 * k), bob(1, i, 5, 1.0 + 0.2 * k)]
bd(1, E, cross(1, 1490, 490, d=1.4), BIG(1, 960, 820, "< 4 weeks", c="red", d=0.6, s=130))
# 1.5 Friday 13th
q = uid("q")
bd(1.5, cal(1.5, 760, 480, "FRIDAY", "13", d=0.1, k=1.2, c="ink"),
   [{"t": "icon", "at": 1.5, "id": q, "name": "question", "x": 1350, "y": 300, "size": 220, "c": "red"}, pop(1.5, q, 0.5), wig(1.5, q, (1460, 410), 8, 1.6)],
   T(1.5, 1400, 820, 70, "of course", c="muted", d=0.8), n=3)
# 2 Science journal
bd(2, book(2, 760, 500, 0.1), arr(2, 1050, 500, 1300, 500, c="ink", d=0.6), T(2, 1560, 500, 64, "a real paper", c="ink", d=0.8),
   dot(2, 1560, 620, d=1.0))
# 2.5 respected
bd(2.5, book(2.5, 960, 470, 0.0, 1.1), star(2.5, 620, 380, 0.4, r=40), star(2.5, 1300, 380, 0.7, r=40), star(2.5, 1300, 620, 1.0, r=40),
   T(2.5, 960, 900, 64, "top journal", c="gold", d=0.6))
# 3 the question: squeezed
E = []
for k in range(2):
    w = uid("wl")
    E += [R(3, 260 + 1300 * k, 240, 100, 600, c="ink", fill="muted", idp=w), sh(3, w, 300 if k == 0 else -300, 0, 0.4, 2.0)]
bd(3, E, crowd(3, 560, 360, 9, 4, gap=95, k=0.9, d=0.1, step=0.02), BIG(3, 960, 940, "squeezed?!", c="red", d=0.6, s=110))
# 3.5 still here
m, mi = mo(3.5, 960, 860, 1.1)
q = uid("q")
bd(3.5, m, [{"t": "icon", "at": 3.5, "id": q, "name": "question", "x": 1250, "y": 260, "size": 220, "c": "red"}, pop(3.5, q, 0.4), pulse(3.5, q, 1.0)],
   [sh(3.5, mi + "*", 0, -40, 0.6, 0.4), sh(3.5, mi + "*", 0, 40, 1.0, 0.4)], T(3.5, 500, 500, 70, "still here", c="green", d=0.6), n=3)
# 4 meet Mo
m, mi = mo(4, 960, 880, 1.6)
bd(4, m, [pop(4, mi, 0.0)], BIG(4, 1500, 500, "Mo", c="gold", d=0.4, s=150), star(4, 620, 400, 0.6, r=40), n=3)
# 4.5 relatives
m, mi = mo(4.5, 960, 860, 1.0)
bd(4.5, m, crowd(4.5, 300, 300, 4, 3, gap=110, d=0.2), crowd(4.5, 1300, 300, 4, 3, gap=110, d=0.4, c="blue"),
   T(4.5, 960, 1000, 60, "...lots of relatives", c="muted", d=0.6))
# 5 1800: one billion
bd(5, crowd(5, 760, 380, 1, 1, k=2.5, d=0.1), BIG(5, 760, 760, "1800", c="ink", d=0.0, s=110), BIG(5, 1300, 500, "1 billion", c="blue", d=0.6, s=110),
   arr(5, 900, 380, 1060, 470, c="ink", d=0.4))
# 5.5 1927: two billion
bd(5.5, crowd(5.5, 600, 380, 2, 1, gap=200, k=2.5, d=0.1), BIG(5.5, 700, 760, "1927", c="ink", s=110), BIG(5.5, 1360, 500, "2 billion", c="blue", d=0.5, s=110))
# 6 1974: four billion
bd(6, crowd(6, 480, 340, 4, 1, gap=170, k=2.2, d=0.1, step=0.15), BIG(6, 740, 760, "1974", c="ink", s=110), BIG(6, 1450, 520, "4 billion", c="blue", d=0.7, s=100))
# 6.5 doublings faster
E = []
for k, (x, w) in enumerate([(300, 640), (940, 360), (1300, 200), (1500, 110)]):
    i = uid("gap")
    E += [R(6.5, x, 440, w - 20, 120, c="blue", fill="blue", idp=i),
          {"t": "move", "at": 6.5, "kind": "grow", "targets": [i], "axis": "x", "pivot": [x, 500], "dur": 0.5, "delay": 0.2 + 0.35 * k}]
bd(6.5, E, T(6.5, 610, 400, 48, "127 yrs", c="ink", d=0.3), T(6.5, 1110, 400, 48, "47 yrs", c="ink", d=0.6), arr(6.5, 300, 700, 1600, 700, c="red", d=1.0, dur=0.6),
   T(6.5, 960, 820, 64, "faster and faster", c="red", d=1.2))
# 7 exponential
bd(7, axes(7), curve(7, expo(), c="blue", d=0.2), T(7, 960, 160, 80, "exponential", c="blue", d=0.3), dot(7, 1500, 280, c="blue", d=1.4))
# 7.5 double double double
E = []
for k in range(4):
    i = uid("sq")
    s = 40 * 2 ** (k / 2)
    E += [R(7.5, 400 + 340 * k - s, 560 - s, 2 * s, 2 * s, c="blue", fill="blue", idp=i), pop(7.5, i, 0.1 + 0.3 * k), bob(7.5, i, 6, 1.0)]
bd(7.5, E, T(7.5, 960, 860, 64, "×2   ×2   ×2", c="ink", d=0.3))
# 8 bank account
i = uid("pig")
E = [O(8, 760, 520, 200, c="gold", fill="gold", idp=i), O(8, 640, 470, 12, c="ink", fill="ink", idp=i), bob(8, i, 8, 1.1)]
coins = []
for k in range(4):
    c = uid("coin")
    coins += [O(8, 760, 120 - 60 * k, 34, c="gold", idp=c), sh(8, c, 0, 300 + 60 * k, 0.2 + 0.3 * k, 0.5)]
bd(8, E, coins, T(8, 1400, 450, 64, "fixed interest", c="ink", d=0.4), BIG(8, 1400, 620, "+5%", c="green", d=0.6, s=110))
# 8.5 huge, never infinite
bd(8.5, axes(8.5), curve(8.5, expo(), c="blue", d=0.1), BIG(8.5, 1260, 380, "∞ ?", c="red", d=0.8, s=110), cross(8.5, 1480, 380, d=1.2))
# 9 twist one: faster than exponential
bd(9, axes(9), curve(9, expo(), c="blue", d=0.0, dur=0.8), curve(9, hyper(), c="red", d=0.6, dur=1.4), BIG(9, 960, 160, "TWIST 1", c="red", d=0.2, s=90),
   T(9, 1350, 640, 52, "exponential", c="blue", d=0.5))
# 10 more people more ideas
E = []
for k, x in enumerate([500, 960, 1420]):
    b = uid("bulb")
    E += [O(10, x, 380, 70, c="gold", fill="gold", idp=b), pop(10, b, 0.2 + 0.3 * k), pulse(10, b, 1.0 + 0.2 * k)]
bd(10, E, crowd(10, 380, 680, 10, 2, gap=125, k=0.9, d=0.1, step=0.03), T(10, 960, 1000, 56, "people → ideas", c="ink", d=0.4))
# 10.5 ideas -> faster growth (loop)
L = uid("loop")
bd(10.5, [O(10.5, 960, 520, 260, c="green", idp=L), spin(10.5, L, (960, 520), 40)], arr(10.5, 1220, 520, 1220, 380, c="green", d=0.2),
   arr(10.5, 700, 520, 700, 660, c="green", d=0.4), T(10.5, 960, 420, 60, "more ideas", c="gold", d=0.2), T(10.5, 960, 620, 60, "more people", c="ink", d=0.5),
   BIG(10.5, 960, 940, "faster!", c="red", d=0.9, s=100))
# 11 growth rate grows
E = []
for k in range(5):
    E += bar(11, 400 + 250 * k, 820, 150, 60 * (k + 1) ** 1.6, "red", d=0.15 + 0.2 * k, dur=0.5)
bd(11, E, T(11, 960, 200, 64, "growth rate ↑", c="red", d=0.3))
# 11.5 hyperbolic
bd(11.5, axes(11.5), curve(11.5, hyper(), c="red", d=0.1), BIG(11.5, 900, 200, "hyperbolic", c="red", d=0.4, s=100), dot(11.5, 1460, 300, d=1.4))
# 12 formula
bd(12, BIG(12, 960, 380, "N = big number", c="ink", d=0.1, s=100), arr(12, 600, 560, 1320, 560, c="ink", d=0.4, w=8),
   T(12, 960, 680, 80, "years left until 2026", c="red", d=0.8), crowd(12, 1550, 820, 4, 2, gap=70, k=0.7, d=0.5), n=3)
# 12.5 the real formula
bd(12.5, BIG(12.5, 960, 420, "1.79 × 10¹¹", c="ink", d=0.0, s=110), arr(12.5, 560, 560, 1360, 560, c="ink", d=0.3, w=8),
   BIG(12.5, 960, 700, "(2026.87 − t)", c="red", d=0.6, s=100), cal(12.5, 1650, 400, "NOV", "13", d=0.9, k=0.6))
# 13 divide by smaller
E = []
for k, s in enumerate([160, 110, 70, 40]):
    i = uid("dv")
    E += [R(13, 300 + 380 * k, 700 - s, 2 * s, s, c="blue", fill="blue", idp=i), pop(13, i, 0.2 + 0.3 * k), wig(13, i, (300 + 380 * k + s, 700), 3, 1.4)]
bd(13, E, T(13, 960, 300, 64, "divide by less and less", c="ink", d=0.2))
# 13.5 rockets to infinity
rk = uid("rk")
bd(13.5, axes(13.5), curve(13.5, hyper(cap=1.15), c="red", d=0.0, dur=1.0),
   [P(13.5, "M1480,520 L1520,420 L1560,520 Z", c="red", w=5, fill="red", idp=rk), sh(13.5, rk, 0, -380, 0.8, 1.0), wig(13.5, rk, (1520, 520), 6, 3)],
   BIG(13.5, 900, 300, "→ ∞", c="red", d=0.9, s=130))
# 14 singularity
wall = uid("wall")
bd(14, axes(14), curve(14, hyper(), c="red", d=0.1), [P(14, "M1500,220 L1500,840", c="ink", w=4, idp=wall), pop(14, wall, 0.6), pulse(14, wall, 1.2)],
   T(14, 1500, 900, 52, "Nov 13, 2026", c="red", d=0.8), BIG(14, 820, 200, "singularity", c="ink", d=0.4, s=90))
# 15 scary: fit 2000 years
bd(15, axes(15), curve(15, hyper(), c="red", d=0.1), [e for k in range(6) for e in dot(15, 300 + 200 * k, 820 - 540 * min(1, 0.03 / (1 - k / 6 * 0.9)), c="blue", d=0.4 + 0.15 * k)],
   BIG(15, 800, 200, "2000 years", c="blue", d=0.6, s=100))
# 15.5 24 estimates
E = []
for k in range(24):
    E += dot(15.5, 300 + 55 * k, 820 - 540 * min(1, 0.03 / (1 - k / 24 * 0.92)), c="blue", d=0.05 * k, r=10)
bd(15.5, axes(15.5), E, BIG(15.5, 800, 220, "24 data points", c="blue", d=0.5, s=90))
# 16 1800, 1927, 1974
E = []
for k, (yr, a1, a2) in enumerate([("1800", 0.83, 1), ("1927", 1.9, 2), ("1974", 3.5, 4)]):
    E += bar(16, 380 + 480 * k, 760, 110, 100 * a1, "red", d=0.2 + 0.3 * k) + bar(16, 510 + 480 * k, 760, 110, 100 * a2, "blue", d=0.35 + 0.3 * k)
    E += T(16, 490 + 480 * k, 830, 56, yr, c="ink")
bd(16, E, T(16, 700, 200, 52, "formula", c="red", d=0.2), T(16, 1200, 200, 52, "real", c="blue", d=0.4))
# 16.5 came close
bd(16.5, check(16.5, 500, 500, d=0.1), check(16.5, 960, 500, d=0.4), check(16.5, 1420, 500, d=0.7), BIG(16.5, 960, 820, "close!", c="green", d=0.6, s=120))
# 17 ridiculous letters
E = []
for k in range(5):
    i = uid("let")
    E += [R(17, 200 + 70 * k, 220 + 30 * k, 260, 170, c="ink", fill="muted", idp=i), sh(17, i, 600 + 50 * k, 160, 0.2 + 0.2 * k, 0.6), rot(17, i, 10 * (k % 2 * 2 - 1), (330 + 70 * k, 300), 0.3 + 0.2 * k, 0.5)]
bd(17, E, BIG(17, 1300, 860, "\"ridiculous!\"", c="red", d=0.8, s=100))
# 17.5 fought back
m, mi = mo(17.5, 960, 880, 1.1)
bd(17.5, m, book(17.5, 500, 500, 0.0, 0.7), [sh(17.5, mi + "*", 0, -30, 0.4, 0.3), sh(17.5, mi + "*", 0, 30, 0.8, 0.3)],
   T(17.5, 1450, 450, 64, "\"we stand by it\"", c="ink", d=0.4))
# 18 twist two: plug in today
bd(18, BIG(18, 960, 200, "TWIST 2", c="red", d=0.1, s=90), cal(18, 600, 560, "OCT", "19", d=0.3, k=1.0),
   arr(18, 820, 560, 1080, 560, c="ink", d=0.7), BIG(18, 1400, 560, "N = ?", c="ink", d=0.9, s=110))
# 18.5 2.5 trillion
bd(18.5, crowd(18.5, 220, 200, 16, 5, gap=100, k=0.7, d=0.0, step=0.012, c="muted"), BIG(18.5, 960, 860, "2.5 TRILLION", c="red", d=0.4, s=140))
# 19 300 people
bd(19, crowd(19, 300, 260, 15, 5, gap=90, k=0.7, d=0.0, step=0.012, c="muted"), BIG(19, 960, 880, "×300", c="red", d=0.5, s=140))
# 19.5 for every real person
m, mi = mo(19.5, 960, 860, 1.0)
bd(19.5, m, crowd(19.5, 260, 260, 5, 6, gap=70, k=0.6, d=0.1, step=0.02, c="muted"), crowd(19.5, 1320, 260, 5, 6, gap=70, k=0.6, d=0.3, step=0.02, c="muted"),
   [wig(19.5, mi + "*", (960, 860), 4, 3.0)], T(19.5, 960, 1000, 56, "for every one of us", c="ink", d=0.6))
# 20 real: 8.3 billion
E = bar(20, 500, 820, 200, 600, "red", d=0.1) + bar(20, 1200, 820, 200, 4, "blue", d=0.6)
bd(20, E, T(20, 600, 900, 52, "formula", c="red"), T(20, 1300, 900, 52, "real", c="blue"), BIG(20, 1300, 500, "8.3 billion", c="blue", d=0.8, s=100))
# 21 what bent the curve
bd(21, axes(21), curve(21, [(300 + 1200 * k / 30, 820 - 540 * (1 / (1 + 2.7 ** (-(k - 12) / 3)))) for k in range(31)], c="green", d=0.1),
   BIG(21, 900, 200, "what bent it?", c="ink", d=0.5, s=90), dot(21, 1500, 290, c="green", d=1.3))
# 21.5 not famine not war
bd(21.5, cross(21.5, 600, 480, d=0.2), cross(21.5, 1300, 480, d=0.7), T(21.5, 600, 650, 70, "famine", c="ink", d=0.1), T(21.5, 1300, 650, 70, "war", c="ink", d=0.5),
   crowd(21.5, 700, 800, 8, 1, gap=80, k=0.8, d=0.3))
# 22 growth rate peaked
bd(22, axes(22), curve(22, [(300 + 1200 * k / 30, 820 - 520 * (1 - ((k - 12) / 18) ** 2 if k >= 12 else 1 - ((12 - k) / 12) ** 2)) for k in range(31)], c="red", d=0.1),
   dot(22, 780, 300, d=0.9), T(22, 780, 230, 56, "early 1960s", c="red", d=1.0))
# 22.5 falling
dn = uid("dn")
bd(22.5, axes(22.5), curve(22.5, [(300 + 1200 * k / 20, 300 + 480 * k / 20) for k in range(21)], c="red", d=0.0, dur=1.0),
   [P(22.5, "M1400,600 L1460,700 L1520,600", c="red", w=8, idp=dn), sh(22.5, dn, 0, 100, 0.6, 0.8), pulse(22.5, dn, 1.2)],
   BIG(22.5, 900, 200, "growth rate ↓", c="red", d=0.4, s=90))
# 23 kids stopped dying young
E = []
for k in range(5):
    E += person(23, 500 + 230 * k, 700, 1.4, c="green", d=0.15 * k)
bd(23, E, check(23, 1600, 500, d=1.0), T(23, 960, 860, 64, "most kids grow up", c="green", d=0.6))
# 23.5 families choose fewer
E = person(23.5, 600, 700, 1.8, d=0.0) + person(23.5, 800, 700, 1.8, d=0.1) + person(23.5, 700, 760, 1.1, c="green", d=0.4) + person(23.5, 900, 760, 1.1, c="green", d=0.6)
bd(23.5, E, arr(23.5, 1100, 600, 1300, 600, c="ink", d=0.6), BIG(23.5, 1550, 600, "fewer", c="blue", d=0.9, s=110))
# 24 birth rate today
E = bar(24, 500, 820, 260, 560, "muted", d=0.1) + bar(24, 1150, 820, 260, 260, "blue", d=0.5)
bd(24, E, T(24, 630, 900, 56, "1960", c="ink"), T(24, 1280, 900, 56, "today", c="ink"), T(24, 960, 160, 56, "birth rate", c="ink", d=0.2))
# 24.5 less than half
bd(24.5, BIG(24.5, 960, 480, "< ½", c="blue", d=0.1, s=150), crowd(24.5, 600, 720, 10, 1, gap=80, k=0.8, d=0.3), T(24.5, 960, 920, 56, "of 1960", c="muted", d=0.5))
# 25 twist three: prescription
pill = uid("pill")
bd(25, BIG(25, 960, 200, "TWIST 3", c="red", d=0.1, s=90),
   [R(25, 760, 440, 400, 160, c="red", fill="red", idp=pill), pop(25, pill, 0.4), rot(25, pill, 20, (960, 520), 0.8, 0.8), bob(25, pill, 8, 1.2)],
   T(25, 960, 800, 64, "the authors' fix", c="ink", d=0.6))
# 25.5 cut birth rate in half
cut = uid("cut")
E = bar(25.5, 760, 820, 400, 560, "muted", d=0.0) + [P(25.5, "M640,540 L1280,540", c="red", w=8, idp=cut), pop(25.5, cut, 0.6),
                                                       {"t": "move", "at": 25.5, "kind": "grow", "targets": [cut], "axis": "x", "pivot": [640, 540], "dur": 0.6, "delay": 0.6}]
bd(25.5, E, BIG(25.5, 1550, 540, "÷ 2", c="red", d=0.9, s=130))
# 26 the world roughly did it
bd(26, axes(26), curve(26, hyper(), c="red", d=0.0, dur=0.8), curve(26, [(300 + 1200 * k / 30, 820 - 540 * (1 / (1 + 2.7 ** (-(k - 14) / 3)))) for k in range(31)], c="green", d=0.6),
   check(26, 1600, 280, d=1.4), T(26, 1350, 700, 52, "the real curve", c="green", d=1.0))
# 26.5 prophecy cancelled itself
bd(26.5, cal(26.5, 960, 480, "DOOMSDAY", "13", d=0.0, k=1.2), cross(26.5, 960, 500, d=0.6), BIG(26.5, 960, 900, "cancelled", c="green", d=0.8, s=110), n=3)
# 27 formula hits infinity
bd(27, BIG(27, 700, 480, "∞", c="red", d=0.1, s=150), arr(27, 900, 480, 1150, 480, c="ink", d=0.4), T(27, 1450, 480, 64, "model broken", c="red", d=0.7),
   [e for k in range(3) for e in dot(27, 1300 + 120 * k, 620, c="red", d=0.9 + 0.15 * k)])
# 27.5 stopped describing reality
m, mi = mo(27.5, 1500, 880, 1.0)
bd(27.5, m, BIG(27.5, 700, 420, "math ≠ reality", c="ink", d=0.1, s=90), cross(27.5, 700, 650, d=0.7))
# 28 balloon
bd(28, balloon(28, 760, 480, 120, d=0.1), T(28, 1400, 480, 64, "keep blowing...", c="ink", d=0.4), crowd(28, 1250, 700, 3, 1, gap=120, k=1.0, d=0.6))
# 28.5 rubber says no
pf = uid("pf")
bd(28.5, balloon(28.5, 760, 480, 160, d=0.0, to=1.3), [P(28.5, "M660,300 L620,240 M860,300 L900,240 M760,280 L760,200", c="red", w=6, idp=pf), pop(28.5, pf, 0.9), pulse(28.5, pf, 1.3)],
   BIG(28.5, 1400, 400, "POP!", c="red", d=1.0, s=130), T(28.5, 1400, 650, 56, "rubber says no", c="ink", d=0.6))
# 29 fun fact: magician
hat = uid("hat")
rab = uid("rab")
bd(29, [R(29, 660, 400, 300, 260, c="ink", fill="ink", idp=hat), R(29, 600, 640, 420, 40, c="ink", fill="ink", idp=hat), bob(29, hat, 5, 1.0),
        O(29, 810, 330, 60, c="muted", fill="muted", idp=rab), sh(29, rab, 0, -160, 0.5, 0.8), wig(29, rab, (810, 390), 8, 2.5)],
   star(29, 1050, 260, 0.9, r=40), T(29, 1450, 460, 64, "fun fact", c="gold", d=0.2), T(29, 1450, 580, 52, "von Foerster", c="ink", d=0.4))
# 29.5 stage magician
wand = uid("wand")
bd(29.5, [P(29.5, "M600,700 L960,360", c="ink", w=12, idp=wand), rot(29.5, wand, -25, (600, 700), 0.2, 0.6), wig(29.5, wand, (600, 700), 6, 1.8)],
   star(29.5, 980, 340, 0.6, r=50), star(29.5, 1100, 460, 0.9, r=30), BIG(29.5, 1400, 760, "magician", c="gold", d=0.6, s=110))
# 30 historian: magic trick
bd(30, book(30, 700, 520, 0.1), [e for k in range(3) for e in star(30, 1000 + 150 * k, 300 + 80 * k, 0.4 + 0.2 * k, r=34)],
   T(30, 1400, 700, 64, "a magic trick", c="gold", d=0.6))
# 30.5 ordinary math, extraordinary title
bd(30.5, T(30.5, 500, 420, 60, "ordinary math", c="muted", d=0.1), BIG(30.5, 1300, 420, "DOOMSDAY!", c="red", d=0.5, s=110),
   arr(30.5, 760, 420, 950, 420, c="ink", d=0.3), crowd(30.5, 700, 700, 9, 2, gap=70, k=0.7, d=0.6))
# 31 Time and NYT
E = []
for k, nm in enumerate(["TIME", "NY TIMES"]):
    i = uid("np")
    E += [R(31, 400 + 620 * k, 300, 480, 420, c="ink", idp=i), pop(31, i, 0.2 + 0.4 * k), rot(31, i, 6 * (1 - 2 * k), (640 + 620 * k, 720), 0.6 + 0.4 * k, 0.5)]
    E += T(31, 640 + 620 * k, 380, 64, nm, c="red", d=0.3 + 0.4 * k)
bd(31, E, T(31, 960, 900, 56, "front-page famous", c="ink", d=1.0))
# 32 fine print
bd(32, BIG(32, 960, 220, "fine print", c="muted", d=0.1, s=80), cross(32, 600, 520, d=0.4), T(32, 1050, 520, 64, "not a forecast", c="ink", d=0.3),
   crowd(32, 700, 760, 6, 1, gap=100, k=0.8, d=0.5))
# 32.5 warning about a curve
bd(32.5, axes(32.5), curve(32.5, hyper(), c="red", d=0.1), BIG(32.5, 860, 200, "⚠ warning", c="gold", d=0.6, s=100), dot(32.5, 1460, 300, d=1.2))
# 33 growth slowing
bd(33, axes(33), curve(33, [(300 + 1200 * k / 30, 820 - 540 * (1 / (1 + 2.7 ** (-(k - 12) / 3)))) for k in range(31)], c="green", d=0.1),
   T(33, 900, 200, 64, "slowing down", c="green", d=0.6), dot(33, 1500, 290, c="green", d=1.4))
# 33.5 too few babies
E = []
for k in range(3):
    E += person(33.5, 700 + 260 * k, 720, 0.8, c="blue", d=0.3 + 0.2 * k)
q = uid("q")
bd(33.5, E, crowd(33.5, 500, 400, 8, 1, gap=130, k=1.4, d=0.0, step=0.04),
   [{"t": "icon", "at": 33.5, "id": q, "name": "question", "x": 1450, "y": 600, "size": 200, "c": "red"}, pop(33.5, q, 0.8), wig(33.5, q, (1550, 700), 8, 1.4)],
   T(33.5, 960, 960, 56, "too few babies?", c="ink", d=0.8))
# 34 relax, Mo is fine
m, mi = mo(34, 960, 880, 1.5)
bd(34, m, cal(34, 400, 420, "NOV", "13", d=0.1, k=0.8), check(34, 1500, 400, d=0.8), BIG(34, 1500, 700, "relax", c="green", d=0.5, s=110), n=3)
# 34.5 don't schedule anything important
m, mi = mo(34.5, 1450, 880, 1.0)
bd(34.5, m, cal(34.5, 650, 480, "FRI", "13", d=0.0, k=1.1), cross(34.5, 650, 520, c="red", d=0.6), T(34.5, 650, 860, 56, "no big meetings", c="ink", d=0.4),
   [sh(34.5, mi + "*", 0, -40, 0.9, 0.3), sh(34.5, mi + "*", 0, 40, 1.2, 0.3)], n=3)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en")
