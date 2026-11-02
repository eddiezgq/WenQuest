"""每日科普 2026-11-02（英文）：《Scientists Set Doomsday for Nov 13, 2026》
新闻：1960 年 Science 论文 “Doomsday: Friday, 13 November, A.D. 2026”（von Foerster, Mora, Amiot）算出世界人口将在 2026-11-13 趋于无穷；
  离那天还有 11 天，The Conversation（10-16，Alan MacEachern）文章被 ScienceDaily、Gizmodo 等转载，正在英文网上流传。
出处：
- ScienceDaily（转载 The Conversation）https://www.sciencedaily.com/releases/2026/10/261016070639.htm ：24 个两千年来的人口估计、
  “Our great-great-grandchildren will not starve. They will be squeezed to death.”、建议出生率减半、约 1993 年起实际人口落后于公式、
  如今全球出生率“略低于 1960 年的一半”、批评者称其 “ridiculous”“manifestly absurd”。
- Gizmodo https://gizmodo.com/scientists-once-calculated-the-date-of-doomsday-and-its-next-month-2000820261
常识/估算：公式大致是 N = 1.79×10¹¹ / (2026.87 − t)^0.99（双曲增长）；人口约 80 多亿（联合国估计）。
“翻倍时间 40、20、10、5 年 → 加起来 80 年撞墙”是我们简化的示意，不是论文原式；“警告帮助打破预言”是作者 MacEachern 的看法 + 我们的推测，
  出生率下降有很多原因。
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import stick  # noqa: E402

S = [
 ("1960年，三位科学家算出了世界末日：|2026年11月13日，星期五。", "In 1960, three scientists calculated the end of the world: | Friday, November thirteenth, 2026."),
 ("那是十一天以后。|对，我也去翻了日历。", "That is eleven days from today. | Yes, I checked my calendar too."),
 ("论文登在《科学》上，|世界顶级的期刊。", "They published it in Science, | one of the top journals on Earth."),
 ("他们说，到那一天，|人口会冲向无穷大。", "Their claim: on that day, | the number of humans shoots to infinity."),
 ("他们写道：我们的玄孙不会饿死，|会被挤死。", "They wrote: our great great grand kids will not starve. | They will be squeezed to death."),
 ("《时代》周刊和《纽约时报》|都报道了它。", "Time magazine and The New York Times | covered it."),
 ("今天的烧脑问题：|数学怎么能算出一个“无穷大”的星期五？", "Today's brain teaser: | how can math put infinity on a specific Friday?"),
 ("先说普通的增长：指数增长，|就像存在银行里的钱。", "Start with normal growth, exponential, | like money in a bank."),
 ("指数增长的翻倍时间是固定的，|比如每四十年翻一倍。", "Exponential growth has a fixed doubling time, | say, double every forty years."),
 ("它会变得很大，|但永远到不了无穷。", "It gets huge, | but it never reaches infinity."),
 ("反转一：他们发现，人类长得|比指数还快。", "Twist one: they found that humans grew | faster than exponential."),
 ("他们查了两千年里|二十四个世界人口估计。", "They checked twenty four estimates | of world population across two thousand years."),
 ("翻倍的时间，|越来越短。", "And the doubling time | kept getting shorter."),
 ("他们的想法：人越多，点子越多，|合作越多，粮食越多。", "Their idea: more people means more ideas, | more teamwork, more food."),
 ("于是增长喂养增长，|越来越快。", "So growth feeds on itself, | faster and faster."),
 ("培养皿里的细菌可不会这样，|它们不交换点子。", "Bacteria in a dish do not do that. | They do not swap ideas."),
 ("数学上这叫双曲增长。|诀窍在这儿。", "Math calls this hyperbolic growth. | Here is the trick."),
 ("想象每次翻倍，只用上次一半的时间：|四十年，二十年，十年，五年。", "Picture each doubling taking half as long as the last: | forty years, then twenty, then ten, then five."),
 ("把它们加起来，|八十年就撞墙。", "Add them up, | and you hit a wall at eighty years."),
 ("无穷多次翻倍，|塞进有限的时间里。", "Infinite doublings, | squeezed into a finite time."),
 ("这有点像芝诺悖论，|只不过倒过来用。", "It is a bit like Zeno's paradox, | run in reverse."),
 ("那堵墙是日历上的一天。|他们管它叫末日。", "That wall is a date on the calendar. | They called it doomsday."),
 ("他们的公式指向|2026年11月。", "Their formula pointed | to November 2026."),
 ("反转二：好几十年里，|这个公式准得吓人。", "Twist two: for decades, | the formula worked scarily well."),
 ("直到大约1993年，|真实人口一直跟着它走。", "Until about 1993, | real numbers kept up with it."),
 ("然后，现实掉队了。|掉得很远。", "Then reality fell behind. | Way behind."),
 ("今天地球上大约八十多亿人。|不是无穷，差得远。", "Today there are about eight billion of us. | Not infinity. Not even close."),
 ("按他们的公式算，|今天地球上该有大约两千亿人。", "Run their formula for today, | and you get about two hundred billion people."),
 ("反转三，最奇妙：|也许是警告本身，打破了预言。", "Twist three, the weirdest: | maybe the warning helped break the prediction."),
 ("他们开的药方是：|把全世界的出生率减半。", "Their cure was to cut | the world birth rate in half."),
 ("今天全球出生率|比1960年的一半还略低一点。", "Today the global birth rate is | slightly less than half its 1960 level."),
 ("当然原因很多：|医疗、上学、进城、计划生育。", "Of course, many things drove that: | medicine, school, cities, family planning."),
 ("物理学家都懂这个信号：|公式一算出无穷，模型就要坏了。", "Physicists know the sign: | when a formula hits infinity, the model is breaking."),
 ("它忽略的东西，|比如粮食、空间、人的选择，会接管一切。", "Something it ignored, | like food, space, or people's choices, takes over."),
 ("真实的增长曲线，|会弯成一个S形。", "Real growth curves | bend into an S shape."),
 ("就像岛上的兔子：|先猛涨，然后吃的不够了。", "Like rabbits on an island: | a boom first, then the food runs out."),
 ("1960年就有批评者说这篇论文|荒唐、明显荒谬。", "Critics in 1960 called the paper | ridiculous and manifestly absurd."),
 ("但它留下一堂好课：|贴合过去的曲线，照样可能算错未来。", "But it left a great lesson: | a curve that fits the past can still fail the future."),
 ("友情提示：那个日期是数学上的警告，|不是真的预言。", "Fine print: the date was a math warning, | not a real prophecy."),
 ("四十、二十、十年的例子是我们的简化示意，|不是他们的原公式。", "The forty, twenty, ten example is our simple picture, | not their exact formula."),
 ("所以，11月13日世界会完蛋吗？|不会。完蛋的是公式，不是我们。", "So, will the world end on November thirteenth? | No. The formula ends, not us."),
 ("不过那天要是地铁特别挤，|你知道该怪谁了。", "But if your subway is extra crowded that day, | you know who to blame."),
]
TITLE = {"en": "Scientists Set Doomsday for Nov 13, 2026", "zh": "科学家把末日定在 2026 年 11 月 13 日"}

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


def t(a, x, y, s, text, c="ink", d=None):
    return T(a, x, y, s, text, c=c, d=d, font="en")


def big(a, x, y, text, c="red", d=0.0, s=140):
    return BIG(a, x, y, text, c=c, d=d, s=s, font="en")


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def man(a, x, y, k=1.0, d=0.0, hop=False):
    i = uid("mn")
    E = stick(x, y, k, a, idp=i) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.3, "delay": d}]
    E.append({"t": "move", "at": a, "kind": "bob" if not hop else "wiggle", "targets": [i + "*"], **({"amp": 6, "hz": 1.6} if not hop else {"pivot": [x, y + 120 * k], "amp": 6, "hz": 3})})
    return E


def crowd(a, x, y, n, k=0.6, gap=70, d=0.0, step=0.05, squeeze=False, cols=None):
    """A row (or grid) of stick people popping in one by one; squeeze = they all jiggle."""
    E = []
    cols = cols or max(1, min(n, int(1500 / gap)))
    for q in range(n):
        E += man(a, x + gap * (q % cols), y + 150 * k * (q // cols), k, d + step * q, hop=squeeze)
    return E


def cal(a, x, y, d=0.0, day="13", c="red"):
    """A calendar page: Fri / 13."""
    i = uid("cl")
    E = [R(a, x - 150, y - 160, 300, 320, c="ink", idp=i, sw=7), R(a, x - 150, y - 160, 300, 80, c="ink", fill=c, idp=i, sw=7),
         pop(a, i, d), {"t": "move", "at": a, "kind": "wiggle", "targets": [i], "pivot": [x, y - 160], "amp": 4, "hz": 1.2}]
    E += t(a, x, y - 120, 44, "FRI", c="paper", d=d + 0.1) + big(a, x, y + 50, day, c=c, d=d + 0.2, s=130)
    return E


def axes(a, x0=400, y0=880, w=1100, h=620):
    return [P(a, f"M{x0},{y0 - h} L{x0},{y0} L{x0 + w},{y0}", c="ink", w=6)]


def curve(a, kind, x0=400, y0=880, w=1100, h=620, d=0.0, c="blue", wall=None):
    """Plot a curve that draws itself (grow along x). kind: exp | hyp | s | real."""
    import math
    pts = []
    for q in range(41):
        u = q / 40
        if kind == "exp":
            v = (math.exp(3.2 * u) - 1) / (math.exp(3.2) - 1) * 0.75
        elif kind == "hyp":
            v = min(1.05, 0.06 / max(1.0 - u * 0.97, 0.03) - 0.06)
        elif kind == "s":
            v = 0.8 / (1 + math.exp(-9 * (u - 0.5)))
        else:  # real: follows hyp then bends over
            hv = 0.06 / max(1.0 - u * 0.97, 0.03) - 0.06
            v = hv if u < 0.62 else 0.06 / (1 - 0.62 * 0.97) - 0.06 + 0.12 * (1 - math.exp(-(u - 0.62) * 3))
        pts.append(f"{x0 + w * u:.0f},{y0 - h * min(v, 1.05):.0f}")
    i = uid("cv")
    E = [P(a, "M" + " L".join(pts), c=c, w=8, idp=i),
         {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "x", "pivot": [x0, y0], "dur": 1.2, "delay": d}]
    if wall:
        j = uid("wl")
        E += [P(a, f"M{x0 + w * wall},{y0 - h - 40} L{x0 + w * wall},{y0}", c="red", w=6, idp=j, strokeStyle="dashed"), pop(a, j, d + 1.2), pulse(a, j, d + 1.6)]
    return E


def dot(a, x, y, d=0.0, c="ink", r=14, dy=0):
    i = uid("dt")
    E = [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d)]
    if dy:
        E.append(sh(a, i, 0, dy, d + 0.4, 0.6))
    return E


def coin(a, x, y, d=0.0, n=3):
    E = []
    for q in range(n):
        i = uid("cn")
        E += [O(a, x, y - 40 * q, 50, c="gold", fill="gold", idp=i), pop(a, i, d + 0.15 * q), bob(a, i, 4, 1.5)]
    return E


def bulb(a, x, y, d=0.0):
    i, j = uid("lb"), uid("lr")
    return [O(a, x, y, 60, c="gold", fill="gold", idp=i), R(a, x - 25, y + 55, 50, 40, c="ink", fill="muted", idp=i), pop(a, i, d),
            P(a, f"M{x - 100},{y} L{x - 140},{y} M{x + 100},{y} L{x + 140},{y} M{x},{y - 100} L{x},{y - 140} M{x - 75},{y - 75} L{x - 100},{y - 100} M{x + 75},{y - 75} L{x + 100},{y - 100}",
              c="gold", w=6, idp=j), pop(a, j, d + 0.2), pulse(a, j, d + 0.6)]


def snowball(a, x, y, d=0.0, dx=900):
    i = uid("sb")
    return [O(a, x, y, 60, c="blue", idp=i, sw=6), pop(a, i, d), {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x, y + 60], "dur": 1.4, "delay": d + 0.2},
            sh(a, i, dx, 0, d + 0.2, 1.4), spin(a, i, (x, y), 80)]


def subway(a, x, y, d=0.0):
    i = uid("sw")
    E = [R(a, x - 500, y - 220, 1000, 300, c="ink", idp=i, sw=7), O(a, x - 350, y + 110, 40, c="ink", fill="ink", idp=i), O(a, x + 350, y + 110, 40, c="ink", fill="ink", idp=i),
         pop(a, i, d), {"t": "move", "at": a, "kind": "wiggle", "targets": [i], "pivot": [x, y], "amp": 1, "hz": 3}]
    E += crowd(a, x - 430, y - 10, 13, 0.55, 70, d + 0.2, 0.04, squeeze=True)
    return E


# ---------- boards ----------
bd(0, big(0, 1300, 330, "1960", c="ink", d=0.0, s=140), man(0, 500, 520, 1.2, 0.1), man(0, 700, 520, 1.2, 0.2), man(0, 900, 520, 1.2, 0.3), ic(0, "flask", 1300, 650, 150, 0.4, mv="wig"))
bd(0.5, cal(0.5, 600, 560, 0.0), big(0.5, 1300, 420, "Nov 13, 2026", c="red", d=0.3, s=110), ic(0.5, "flame", 1300, 680, 140, 0.5, mv="wig", c="red"), ic(0.5, "globe", 1650, 700, 130, 0.6, mv="spin"))
bd(1, big(1, 1250, 420, "11 days", c="red", d=0.0, s=150), ic(1, "clock", 500, 520, 200, 0.2, mv="spin"), arr(1, 700, 520, 950, 450, c="red", d=0.4))
bd(1.5, cal(1.5, 700, 560, 0.0), man(1.5, 1250, 500, 1.4, 0.2, hop=True), ic(1.5, "question", 1550, 380, 120, 0.4, mv="wig", c="red"))
bd(2, big(2, 1250, 380, "Science", c="blue", d=0.1, s=140), R(2, 400, 280, 360, 480, c="ink", sw=7), P(2, "M450,380 L710,380 M450,450 L710,450 M450,520 L650,520", c="muted", w=5),
   ic(2, "atom", 580, 640, 120, 0.3, mv="spin"))
bd(2.5, big(2.5, 1300, 420, "top journal", c="blue", d=0.1, s=100), star(2.5, 600, 400, 0.2, r=50), star(2.5, 800, 600, 0.4, r=40), star(2.5, 450, 700, 0.5, r=36), check(2.5, 1300, 650, d=0.5))
bd(3, cal(3, 550, 560, 0.0), arr(3, 800, 560, 1100, 560, c="ink", d=0.3), crowd(3, 1150, 560, 8, 0.6, 80, 0.4, 0.05))
bd(3.5, big(3.5, 960, 420, "∞", c="red", d=0.0, s=260), crowd(3.5, 300, 760, 18, 0.5, 75, 0.2, 0.03, squeeze=True))
bd(4, ic(4, "flame", 600, 500, 160, 0.0, mv="wig", c="red"), cross(4, 600, 500, d=0.3), t(4, 1250, 400, 64, "will not starve", c="green", d=0.2), check(4, 1250, 600, d=0.5))
bd(4.5, crowd(4.5, 300, 420, 30, 0.5, 65, 0.0, 0.02, squeeze=True), big(4.5, 960, 880, "squeezed to death", c="red", d=0.4, s=90))
bd(6, big(6, 1150, 360, "Brain teaser", c="red", d=0.0, s=110), ic(6, "question", 450, 450, 260, 0.2, mv="wig", c="red"), cal(6, 1150, 700, 0.3))
bd(6.5, big(6.5, 600, 500, "∞", c="red", d=0.0, s=240), t(6.5, 1000, 500, 120, "=", d=0.2), cal(6.5, 1400, 520, 0.3), ic(6.5, "question", 1700, 300, 110, 0.5, mv="wig", c="red"))
bd(7, axes(7), curve(7, "exp", d=0.2, c="blue"), t(7, 960, 230, 70, "exponential", c="blue", d=0.1))
bd(7.5, ic(7.5, "building", 500, 550, 220, 0.0, mv="bob"), coin(7.5, 1000, 650, 0.2, 3), coin(7.5, 1250, 650, 0.5, 5), t(7.5, 960, 260, 64, "money in a bank", c="gold", d=0.2))
bd(8, axes(8), curve(8, "exp", d=0.0, c="blue"), t(8, 960, 230, 64, "fixed doubling time", c="blue", d=0.2), ic(8, "clock", 1650, 400, 130, 0.3, mv="spin"))
bd(8.5, big(8.5, 960, 300, "×2 every 40 years", c="blue", d=0.0, s=90), bar(8.5, 600, 900, 100, 60, "blue", 0.2), bar(8.5, 800, 900, 100, 120, "blue", 0.4), bar(8.5, 1000, 900, 100, 240, "blue", 0.6), bar(8.5, 1200, 900, 100, 480, "blue", 0.8))
bd(9, axes(9), curve(9, "exp", d=0.0, c="blue"), big(9, 900, 330, "huge", c="blue", d=0.3, s=120))
bd(9.5, big(9.5, 700, 450, "∞", c="ink", d=0.0, s=220), cross(9.5, 700, 450, d=0.3), axes(9.5, 1050, 850, 650, 450), curve(9.5, "exp", 1050, 850, 650, 450, d=0.2, c="blue"))
bd(10, big(10, 960, 360, "Twist one", c="red", d=0.0, s=140), crowd(10, 450, 700, 6, 0.7, 120, 0.2, 0.06), ic(10, "flame", 1500, 650, 140, 0.5, mv="wig", c="red"))
bd(10.5, axes(10.5), curve(10.5, "exp", d=0.0, c="blue"), curve(10.5, "hyp", d=0.4, c="red"), t(10.5, 700, 230, 60, "faster than exponential", c="red", d=0.5))
bd(11, big(11, 1300, 380, "24 estimates", c="blue", d=0.1, s=110), axes(11, 300, 850, 700, 450), [dot(11, 330 + 28 * q, 850 - 4 - 0.6 * q * q, 0.05 * q, c="blue") for q in range(24)])
bd(11.5, big(11.5, 960, 280, "2,000 years", c="ink", d=0.0, s=120), ic(11.5, "clock", 600, 650, 180, 0.2, mv="spin"), ic(11.5, "globe", 1300, 650, 180, 0.4, mv="spin"))
bd(12, ic(12, "clock", 960, 380, 220, 0.0, mv="spin"), t(12, 960, 650, 70, "doubling time", c="ink", d=0.2), arr(12, 600, 800, 1300, 800, c="red", d=0.4))
bd(12.5, bar(12.5, 500, 900, 120, 500, "red", 0.0), bar(12.5, 750, 900, 120, 300, "red", 0.2), bar(12.5, 1000, 900, 120, 150, "red", 0.4), bar(12.5, 1250, 900, 120, 70, "red", 0.6), big(12.5, 960, 260, "shorter and shorter", c="red", d=0.3, s=90))
bd(13, crowd(13, 450, 650, 4, 0.9, 150, 0.0, 0.08), bulb(13, 1300, 500, 0.3), bulb(13, 1600, 500, 0.5))
bd(13.5, man(13.5, 500, 600, 1.2, 0.0), man(13.5, 700, 600, 1.2, 0.1), arr(13.5, 560, 500, 640, 500, c="green", d=0.3), ic(13.5, "gear", 1200, 550, 160, 0.3, mv="spin"), ic(13.5, "water", 1500, 550, 150, 0.4, mv="wig", c="blue"), t(13.5, 1350, 300, 60, "teamwork, food", c="green", d=0.4))
bd(14, snowball(14, 400, 600, 0.0, 1000), t(14, 960, 300, 70, "growth feeds on itself", c="blue", d=0.3))
bd(14.5, axes(14.5), curve(14.5, "hyp", d=0.0, c="red"), big(14.5, 900, 300, "faster and faster", c="red", d=0.4, s=80))
bd(16, big(16, 960, 300, "hyperbolic", c="red", d=0.0, s=140), axes(16, 500, 900, 900, 450), curve(16, "hyp", 500, 900, 900, 450, d=0.3, c="red"))
bd(16.5, ic(16.5, "magnifier", 700, 550, 240, 0.0, mv="wig"), big(16.5, 1300, 450, "the trick", c="blue", d=0.2, s=110), star(16.5, 1300, 700, 0.4, r=40))
bd(17, t(17, 960, 230, 64, "each doubling takes half as long", c="ink", d=0.0), bar(17, 300, 900, 120, 120, "red", 0.2), bar(17, 450, 900, 120, 240, "red", 0.4), bar(17, 600, 900, 120, 480, "red", 0.6), crowd(17, 1000, 650, 6, 0.7, 120, 0.3, 0.1))
bd(17.5, [R(17.5, 300, 400, 640, 120, c="ink", fill="blue"), R(17.5, 940, 400, 320, 120, c="ink", fill="blue"), R(17.5, 1260, 400, 160, 120, c="ink", fill="blue"), R(17.5, 1420, 400, 80, 120, c="ink", fill="blue")],
   t(17.5, 620, 600, 64, "40", d=0.0), t(17.5, 1100, 600, 64, "20", d=0.3), t(17.5, 1340, 600, 56, "10", d=0.6), t(17.5, 1460, 600, 48, "5", d=0.9), dot(17.5, 300, 300, 0.0, c="red", r=24))
bd(18, t(18, 960, 230, 70, "40 + 20 + 10 + 5 + ...", c="ink", d=0.0), arr(18, 300, 600, 1400, 600, c="blue", d=0.3, dur=1.0), P(18, "M1500,380 L1500,820", c="red", w=14), big(18, 1500, 900, "80 years", c="red", d=0.6, s=80))
bd(18.5, axes(18.5), curve(18.5, "hyp", d=0.0, c="red", wall=0.97), big(18.5, 800, 330, "WALL", c="red", d=0.8, s=120))
bd(19, big(19, 960, 330, "∞ doublings", c="red", d=0.0, s=130), ic(19, "clock", 600, 700, 180, 0.2, mv="spin"), ic(19, "atom", 1300, 700, 180, 0.4, mv="spin"))
bd(19.5, R(19.5, 500, 400, 920, 400, c="ink", sw=8), crowd(19.5, 560, 480, 24, 0.45, 70, 0.0, 0.03, squeeze=True, cols=12), t(19.5, 960, 300, 64, "finite time", c="blue", d=0.4))
bd(21, axes(21), curve(21, "hyp", d=0.0, c="red", wall=0.97), cal(21, 1700, 420, 0.6))
bd(21.5, big(21.5, 960, 330, "DOOMSDAY", c="red", d=0.0, s=150), ic(21.5, "flame", 500, 700, 160, 0.2, mv="wig", c="red"), ic(21.5, "globe", 960, 700, 170, 0.3, mv="spin"), ic(21.5, "flame", 1420, 700, 160, 0.4, mv="wig", c="red"))
bd(22, t(22, 960, 230, 64, "N = 1.79 × 10¹¹ / (2026.87 − t)^0.99", c="ink", d=0.0), ic(22, "computer", 600, 600, 200, 0.2, mv="bob"), arr(22, 800, 600, 1150, 600, c="red", d=0.4))
bd(22.5, cal(22.5, 960, 560, 0.0), big(22.5, 960, 900, "November 2026", c="red", d=0.3, s=90), star(22.5, 600, 500, 0.4, r=40), star(22.5, 1320, 500, 0.6, r=40))
bd(23, big(23, 960, 360, "Twist two", c="red", d=0.0, s=140), ic(23, "eye", 500, 700, 160, 0.2, mv="wig"), ic(23, "flame", 1420, 700, 150, 0.4, mv="wig", c="red"))
bd(23.5, axes(23.5), curve(23.5, "hyp", d=0.0, c="red"), [dot(23.5, 400 + 1100 * u, 880 - 620 * (0.06 / (1 - u * 0.97) - 0.06), 0.3 + 0.12 * q, c="blue") for q, u in enumerate((0.1, 0.25, 0.4, 0.5, 0.6, 0.66))],
   t(23.5, 800, 250, 64, "scarily good", c="blue", d=0.4))
bd(24, big(24, 960, 300, "until ~1993", c="ink", d=0.0, s=120), axes(24, 500, 900, 900, 450), curve(24, "hyp", 500, 900, 900, 450, d=0.2, c="red"), check(24, 1500, 500, d=0.6))
bd(24.5, axes(24.5), curve(24.5, "hyp", d=0.0, c="red"), curve(24.5, "real", d=0.3, c="blue"), t(24.5, 700, 230, 60, "real numbers", c="blue", d=0.4))
bd(25, axes(25), curve(25, "hyp", d=0.0, c="red", wall=0.97), curve(25, "real", d=0.2, c="blue"), arr(25, 1300, 300, 1300, 580, c="ink", d=0.8), t(25, 700, 230, 64, "reality fell behind", c="blue", d=0.5))
bd(25.5, big(25.5, 960, 300, "WAY behind", c="blue", d=0.0, s=130), man(25.5, 600, 650, 1.4, 0.1, hop=True), arr(25.5, 800, 600, 1400, 600, c="red", d=0.3), ic(25.5, "rocket", 1550, 600, 160, 0.5, mv="bob"))
bd(26, big(26, 1250, 380, "≈ 8 billion", c="blue", d=0.1, s=120), ic(26, "globe", 500, 550, 260, 0.0, mv="spin"), crowd(26, 900, 700, 10, 0.6, 85, 0.3, 0.04))
bd(26.5, big(26.5, 700, 450, "∞", c="red", d=0.0, s=240), cross(26.5, 700, 450, d=0.2), t(26.5, 1350, 450, 70, "not even close", c="blue", d=0.4), ic(26.5, "ruler", 1350, 700, 150, 0.5, mv="wig"))
bd(28, big(28, 960, 360, "Twist three", c="red", d=0.0, s=140), ic(28, "question", 450, 700, 150, 0.2, mv="wig", c="red"), ic(28, "flame", 1470, 700, 150, 0.4, mv="wig", c="red"))
bd(28.5, ic(28.5, "speaker", 500, 500, 200, 0.0, mv="wig"), arr(28.5, 650, 500, 950, 500, c="red", d=0.3), big(28.5, 1300, 400, "warning", c="red", d=0.2, s=100), cross(28.5, 1300, 650, d=0.6))
bd(29, ic(29, "flask", 500, 550, 200, 0.0, mv="wig"), t(29, 1250, 350, 70, "their cure", c="green", d=0.2), ic(29, "check", 1250, 600, 140, 0.4, mv="bob", c="green"))
bd(29.5, big(29.5, 960, 300, "birth rate ÷ 2", c="green", d=0.0, s=110), bar(29.5, 700, 900, 160, 400, "muted", 0.2), bar(29.5, 1060, 900, 160, 200, "green", 0.5), arr(29.5, 900, 550, 1040, 650, c="green", d=0.7))
bd(30, t(30, 960, 230, 64, "global birth rate", c="ink", d=0.0), bar(30, 650, 900, 180, 500, "muted", 0.1), t(30, 740, 960, 48, "1960", d=0.2), bar(30, 1100, 900, 180, 230, "green", 0.4), t(30, 1190, 960, 48, "today", c="green", d=0.5))
bd(30.5, big(30.5, 960, 330, "< half", c="green", d=0.0, s=150), check(30.5, 960, 600, d=0.3), crowd(30.5, 500, 750, 10, 0.5, 100, 0.2, 0.04))
bd(31, t(31, 960, 230, 70, "many causes", c="ink", d=0.0), ic(31, "flask", 400, 550, 150, 0.1, mv="wig"), ic(31, "computer", 800, 550, 150, 0.2, mv="bob"), ic(31, "building", 1200, 550, 150, 0.3, mv="bob"), ic(31, "check", 1550, 550, 130, 0.4, mv="bob", c="green"))
bd(31.5, t(31.5, 400, 800, 48, "medicine", d=0.0), t(31.5, 800, 800, 48, "school", d=0.2), t(31.5, 1200, 800, 48, "cities", d=0.4), t(31.5, 1550, 800, 48, "family planning", d=0.6),
   ic(31.5, "flask", 400, 550, 150, 0.0, mv="wig"), ic(31.5, "computer", 800, 550, 150, 0.0, mv="bob"), ic(31.5, "building", 1200, 550, 150, 0.0, mv="bob"))
bd(32, ic(32, "atom", 600, 500, 220, 0.0, mv="spin"), t(32, 1300, 400, 70, "physicists know", c="blue", d=0.2), ic(32, "eye", 1300, 650, 150, 0.4, mv="wig"))
bd(32.5, big(32.5, 600, 450, "∞", c="red", d=0.0, s=240), arr(32.5, 800, 450, 1100, 450, c="ink", d=0.2), ic(32.5, "gear", 1350, 450, 200, 0.3, mv="spin"), cross(32.5, 1350, 450, d=0.6), t(32.5, 960, 800, 64, "the model is breaking", c="red", d=0.5))
bd(33, t(33, 960, 250, 70, "what it ignored", c="ink", d=0.0), ic(33, "magnifier", 960, 550, 220, 0.2, mv="wig"), ic(33, "question", 1450, 500, 140, 0.4, mv="wig", c="red"))
bd(33.5, ic(33.5, "water", 450, 500, 170, 0.0, mv="wig", c="blue"), ic(33.5, "building", 960, 500, 170, 0.2, mv="bob"), man(33.5, 1450, 420, 1.2, 0.4), t(33.5, 450, 750, 52, "food", d=0.1), t(33.5, 960, 750, 52, "space", d=0.3), t(33.5, 1450, 750, 52, "choices", d=0.5))
bd(34, axes(34), curve(34, "s", d=0.0, c="green"), t(34, 960, 230, 70, "real growth", c="green", d=0.3))
bd(34.5, axes(34.5), curve(34.5, "hyp", d=0.0, c="red"), curve(34.5, "s", d=0.3, c="green"), big(34.5, 1300, 450, "S", c="green", d=0.6, s=200))
bd(36, big(36, 960, 300, "1960 critics", c="ink", d=0.0, s=110), man(36, 500, 600, 1.3, 0.1, hop=True), man(36, 1420, 600, 1.3, 0.2, hop=True), R(36, 800, 500, 320, 400, c="ink", sw=6), P(36, "M850,600 L1070,600 M850,680 L1070,680 M850,760 L1000,760", c="muted", w=5), ic(36, "flame", 960, 820, 80, 0.4, mv="wig", c="red"))
bd(36.5, big(36.5, 960, 350, "ridiculous!", c="red", d=0.0, s=120), t(36.5, 960, 550, 64, "manifestly absurd", c="red", d=0.3), ic(36.5, "speaker", 450, 750, 140, 0.2, mv="wig"), ic(36.5, "speaker", 1470, 750, 140, 0.4, mv="wig"))
bd(37, big(37, 960, 330, "the lesson", c="blue", d=0.0, s=120), bulb(37, 960, 650, 0.3))
bd(37.5, axes(37.5), curve(37.5, "real", d=0.0, c="blue"), P(37.5, "M1060,560 L1500,180", c="red", w=6, strokeStyle="dashed"), cross(37.5, 1450, 250, d=0.8), t(37.5, 700, 230, 56, "fits the past", c="blue", d=0.3))
bd(38, big(38, 960, 330, "Fine print", c="blue", d=0.0, s=130), ic(38, "magnifier", 500, 700, 150, 0.2, mv="wig"), cal(38, 1420, 650, 0.3))
bd(38.5, t(38.5, 960, 300, 70, "math warning", c="green", d=0.0), check(38.5, 960, 450, d=0.2), t(38.5, 960, 650, 70, "not a prophecy", c="red", d=0.4), cross(38.5, 960, 800, d=0.6))
bd(39, t(39, 960, 250, 70, "40, 20, 10 ...", c="ink", d=0.0), bar(39, 600, 800, 100, 320, "blue", 0.2), bar(39, 800, 800, 100, 160, "blue", 0.3), bar(39, 1000, 800, 100, 80, "blue", 0.4), t(39, 1400, 600, 56, "our simple picture", c="blue", d=0.5))
bd(39.5, t(39.5, 960, 300, 56, "N = 1.79 × 10¹¹ / (2026.87 − t)^0.99", c="ink", d=0.0), check(39.5, 960, 480, d=0.2), ic(39.5, "flask", 600, 700, 140, 0.3, mv="wig"), ic(39.5, "computer", 1320, 700, 140, 0.4, mv="bob"))
bd(40, cal(40, 600, 560, 0.0), ic(40, "question", 1300, 450, 200, 0.2, mv="wig", c="red"), t(40, 1300, 700, 60, "the end?", c="red", d=0.4))
bd(40.5, big(40.5, 960, 300, "No.", c="green", d=0.0, s=150), axes(40.5, 400, 880, 600, 400), curve(40.5, "hyp", 400, 880, 600, 400, d=0.2, c="red"), cross(40.5, 700, 650, d=0.6), crowd(40.5, 1150, 700, 6, 0.6, 90, 0.3, 0.05))
bd(41, subway(41, 960, 600, 0.0), t(41, 960, 230, 64, "extra crowded?", c="ink", d=0.4))
bd(41.5, subway(41.5, 960, 650, 0.0), big(41.5, 960, 250, "blame 1960", c="red", d=0.3, s=110), star(41.5, 500, 250, 0.5, r=36))

bd(5, ic(5, "phone", 500, 500, 200, 0.0, mv="wig"), t(5, 1250, 350, 80, "TIME", c="red", d=0.2), t(5, 1250, 550, 64, "The New York Times", c="ink", d=0.4), ic(5, "speaker", 1600, 700, 120, 0.5, mv="wig"))
bd(5.5, R(5.5, 300, 300, 500, 600, c="ink", sw=7), big(5.5, 550, 450, "DOOM", c="red", d=0.1, s=110), crowd(5.5, 1000, 600, 8, 0.7, 100, 0.2, 0.06, squeeze=True))
bd(15, O(15, 600, 600, 220, c="ink", sw=7), [dot(15, 520 + 60 * (q % 4), 520 + 60 * (q // 4), 0.05 * q, c="green", r=16) for q in range(12)], t(15, 1350, 400, 64, "bacteria", c="green", d=0.3), ic(15, "molecule", 1350, 650, 150, 0.4, mv="spin"))
bd(15.5, crowd(15.5, 450, 550, 3, 1.0, 180, 0.0, 0.08), bulb(15.5, 540, 300, 0.2), O(15.5, 1350, 600, 200, c="ink", sw=7), [dot(15.5, 1300 + 50 * (q % 3), 560 + 50 * (q // 3), 0.05 * q, c="green", r=14) for q in range(6)], cross(15.5, 1350, 300, d=0.5))
bd(20, t(20, 960, 250, 80, "Zeno", c="blue", d=0.0), man(20, 400, 600, 1.2, 0.1), [arr(20, 500 + w0, 700, 500 + w1, 700, c="blue", d=0.2 + 0.2 * q, dur=0.3) for q, (w0, w1) in enumerate(((0, 500), (500, 750), (750, 875), (875, 937)))], P(20, "M1500,520 L1500,820", c="red", w=10))
bd(20.5, big(20.5, 960, 330, "in reverse", c="red", d=0.0, s=110), ic(20.5, "clock", 600, 700, 160, 0.2, mv="spin"), arr(20.5, 800, 700, 1200, 700, c="red", d=0.3), big(20.5, 1400, 700, "∞", c="red", d=0.6, s=160))
bd(27, ic(27, "computer", 500, 550, 220, 0.0, mv="bob"), t(27, 1200, 350, 56, "their formula, today", c="ink", d=0.2), axes(27, 900, 900, 700, 400), curve(27, "hyp", 900, 900, 700, 400, d=0.3, c="red"))
bd(27.5, big(27.5, 960, 300, "≈ 200 billion", c="red", d=0.0, s=120), crowd(27.5, 260, 600, 44, 0.45, 64, 0.1, 0.02, squeeze=True, cols=22), t(27.5, 960, 960, 44, "our calculation", c="muted", d=0.5))
bd(35, ic(35, "map_pin", 500, 500, 160, 0.0, mv="bob", c="green"), [dot(35, 700 + 70 * (q % 6), 500 + 60 * (q // 6), 0.05 * q, c="ink", r=18) for q in range(18)], t(35, 1500, 400, 64, "rabbits", c="ink", d=0.3))
bd(35.5, axes(35.5), curve(35.5, "s", d=0.0, c="green"), t(35.5, 700, 260, 56, "boom", c="green", d=0.3), t(35.5, 1300, 260, 56, "food runs out", c="red", d=0.8), ic(35.5, "water", 1650, 350, 110, 0.6, mv="wig", c="blue"))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"Science,": "Science magazine,", "2026": "twenty twenty six", "1960": "nineteen sixty", "1993": "nineteen ninety three"})
