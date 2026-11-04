"""Daily science 2026-11-04 (English): "A Phone Call That Takes a Day"
News: Voyager 1 reaches one light-day from Earth on 2026-11-18 (12:16 a.m. CST), about 25.9 billion km / 16.1 billion miles, 173 AU;
  launched 1977-09-05; left the heliosphere in 2012; NASA switched off the LECP instrument in April 2026 to save power;
  Voyager 2 reaches one light-day around November 2035 (EarthSky; IFLScience).
Trending: Hacker News front page 2026-11-01, #23 "What is a light-day? The milestone Voyager 1 is closing in on" (91 points).
Sources:
- https://earthsky.org/space/voyager-1-1-light-day-from-earth-november-17-18-2026/
- https://iflscience.com/its-official-voyager-1-will-cross-the-1-light-day-threshold-on-november-18-2026-82733
- https://github.com/meixger/hackernews-daily/issues/1511 (HN daily top 30, 2026-11-01)
Background (NASA/JPL, widely published): speed about 17 km/s; transmitter about 20 W (NASA compares it to a fridge light bulb);
  Deep Space Network 70 m dishes in California, Spain and Australia; light 300,000 km/s; Proxima Centauri about 4.24 light-years.
Our estimates, said as such: ~75,000 years to cover the distance to the nearest star at Voyager's speed (4.24 ly / (17/300,000 c)).
Metaphor (spray paint spreading over a bigger and bigger ball = inverse square law; dish = bowl catching rain) is ours.
"""
import math
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_probe, stick  # noqa: E402

S = [
 ("再过两周，跟旅行者一号说声“你好”，|要等整整一天才到。", "In two weeks, saying hello to Voyager 1 | takes a full day to arrive."),
 ("它回一句？|再等一天。一声你好，来回两天。", "Its reply? | Another day. Two days for one hello."),
 ("十一月十八日，|旅行者一号离地球一光日。", "On November eighteenth, | Voyager 1 reaches one light day from Earth."),
 ("大约二百六十亿公里，|也就是一百六十亿英里。", "That is about twenty six billion kilometers, | or sixteen billion miles."),
 ("这周它上了 Hacker News 首页，|网友都在算这道题。", "It made the Hacker News front page this week, | and everyone is doing the math."),
 ("今天的烧脑问题：|打个电话凭啥要等一天？我们又是怎么听见的？", "Today's brain teaser: | why does a call take a day, and how do we even hear it?"),
 ("认识主角：旅行者一号，|一九七七年出发。", "Meet our hero, Voyager 1, | launched in nineteen seventy seven."),
 ("在路上四十九年，|还在说话。", "Forty nine years on the road. | Still talking."),
 ("反转一：慢的不是旅行者，|是光。", "Twist one: the slow part is not Voyager. | It is light."),
 ("光是最快的东西：|每秒三十万公里。", "Light is the fastest thing there is: | three hundred thousand kilometers a second."),
 ("太阳光到地球要八分钟，|月光只要一秒多。", "Sunlight takes eight minutes to reach us. | Moonlight takes about one second."),
 ("无线电也是光，|一样被这个限速卡住。", "A radio wave is light too, | so it obeys the same speed limit."),
 ("换手机、换套餐，|都没用。", "A new phone will not help. | Neither will a better plan."),
 ("旅行者自己每秒飞十七公里，|一小时六万公里。", "Voyager itself flies about seventeen kilometers a second. | That is sixty thousand kilometers an hour."),
 ("快吗？|光还是比它快一万七千多倍。", "Fast? | Light is still about seventeen thousand times faster."),
 ("所以它飞了四十九年，|才走出一光日。", "So it took forty nine years | to get one light day away."),
 ("反转二：旅行者说话像耳语，|电台功率大约二十瓦。", "Twist two: Voyager whispers. | Its radio uses about twenty watts."),
 ("NASA 说，差不多一个冰箱灯泡，|却要喊过整个太阳系。", "NASA compares that to a fridge light bulb, | shouting across the solar system."),
 ("而且越远，|声音弱得越快。", "And the farther it goes, | the fainter it gets, fast."),
 ("想象一罐喷漆往外喷，|漆铺在一个越来越大的球面上。", "Picture a can of spray paint. | The paint spreads over a bigger and bigger ball."),
 ("远一倍，|就弱四倍。", "Twice as far, | four times fainter."),
 ("那怎么听见？|靠巨大的耳朵。", "So how do we hear it? | With giant ears."),
 ("NASA 的深空网，|天线锅七十米宽。", "NASA's Deep Space Network | uses dishes seventy meters wide."),
 ("加州、西班牙、澳大利亚各一处，|地球怎么转，总有一个朝着深空。", "One in California, one in Spain, one in Australia, | so as Earth spins, one always faces deep space."),
 ("大锅收集那一丝耳语，|就像大碗接雨。", "The dish gathers that whisper | like a bowl catching rain."),
 ("反转三，最烧脑：一光日听着很远，|其实就在家门口。", "Twist three, the most mind bending: one light day sounds far, | but it is next door."),
 ("最近的恒星在四光年开外，|也就是一千五百多光日。", "The nearest star is over four light years away. | That is more than fifteen hundred light days."),
 ("按旅行者的速度飞过去，|我们算了算，要七万五千年。", "At Voyager's speed, going that far | would take about seventy five thousand years, by our math."),
 ("而且它根本不是朝那颗星飞的，|只是在黑暗里漂。", "And Voyager is not even aimed at that star. | It is just drifting through the dark."),
 ("二零一二年，它飞出了太阳的“泡泡”，|是第一个做到的飞船。", "In twenty twelve it left the Sun's bubble, | the first spacecraft ever to do it."),
 ("它的电越来越少，|NASA 只能一台台关掉仪器。", "Its power keeps fading, | so NASA keeps switching instruments off."),
 ("二零二六年四月，又关掉一台，|为了省电。", "In April twenty twenty six, one more went quiet, | to save energy."),
 ("友情提示：日期和距离来自 EarthSky 根据 NASA 的数据；|七万五千年是我们在纸上算的。", "Fine print: the date and distance come from EarthSky, using NASA data. | Seventy five thousand years is our own math on paper."),
 ("旅行者二号在后面追，|大约二零三五年到一光日。", "Voyager 2 is behind it. | It reaches one light day around twenty thirty five."),
 ("所以电话凭啥要等一天？|因为连光都要走一天。", "So why does the call take a day? | Because even light needs a day to get there."),
 ("我们怎么听见？|靠大耳朵，还有耐心。", "And how do we hear it? | With giant ears, and a lot of patience."),
 ("下次嫌消息回得慢，|想想旅行者：等一天，还在说你好。", "Next time a text feels slow, | think of Voyager. It waits a whole day, and still says hello."),
]
TITLE = {"zh": "打个电话要等一天", "en": "A Phone Call That Takes a Day"}

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


def voy(a, x, y, k=1.0, d=0.0, mood="happy"):
    i = uid("vg")
    return cute_probe(x, y, k, a, idp=i, mood=mood) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]


def man(a, x, y, k=1.4, d=0.0, arms="down"):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 6, "hz": 1.6}]


def earth(a, x, y, r=110, d=0.0):
    i, j = uid("ea"), uid("ec")
    E = [O(a, x, y, r, c="blue", fill="paper", idp=i, sw=7), pop(a, i, d),
         P(a, f"M{x - r * 0.6},{y - r * 0.2} Q{x - r * 0.2},{y - r * 0.6} {x + r * 0.1},{y - r * 0.2} Q{x + r * 0.35},{y + r * 0.1} {x + r * 0.6},{y + r * 0.3}", c="green", w=7, idp=j), pop(a, j, d + 0.1),
         spin(a, j, (x, y), 20)]
    return E


def beam(a, x0, y0, x1, y1, d=0.0, dur=1.6, c="red", n=3):
    """无线电小点一个接一个沿直线飞过去。"""
    E = [P(a, f"M{x0},{y0} L{x1},{y1}", c="muted", w=3, idp=uid("bl"))]
    for q in range(n):
        i = uid("bm")
        E += [O(a, x0, y0, 16, c=c, fill=c, idp=i), pop(a, i, d + 0.15 * q), sh(a, i, x1 - x0, y1 - y0, d + 0.2 + 0.25 * q, dur)]
    return E


def dish(a, x, y, k=1.0, d=0.0):
    i = uid("ds")
    E = [P(a, f"M{x - 200 * k},{y - 150 * k} Q{x},{y + 120 * k} {x + 200 * k},{y - 150 * k}", c="ink", w=10, idp=i),
         P(a, f"M{x},{y - 20 * k} L{x},{y + 200 * k} M{x - 90 * k},{y + 200 * k} L{x + 90 * k},{y + 200 * k}", c="ink", w=8, idp=i), pop(a, i, d),
         rot(a, i, -12, (x, y + 200 * k), d + 0.4, 0.8)]
    return E


def rings(a, x, y, n=4, d=0.0, c="red"):
    """喷漆球面一圈圈变大（越来越淡）。"""
    E = []
    for q in range(n):
        i = uid("rg")
        r = 70 + 90 * q
        E += [O(a, x, y, r, c=c, idp=i, sw=max(2, 10 - 3 * q)), pop(a, i, d + 0.25 * q)]
    j = uid("rc")
    E += [O(a, x, y, 26, c=c, fill=c, idp=j), pop(a, j, d), wig(a, j, (x, y), 6, 3)]
    return E


def clock(a, x, y, s=200, d=0.0):
    return ic(a, "clock", x, y, s, d, mv="spin")


def dotsky(a, n=10, d=0.0, seed=1):
    E = []
    for q in range(n):
        i = uid("sk")
        x, y = 200 + (q * 397 + seed * 131) % 1500, 200 + (q * 263 + seed * 71) % 700
        E += [O(a, x, y, 6, c="gold", fill="gold", idp=i), pop(a, i, d + 0.04 * q), wig(a, i, (x, y), 4, 1 + q % 3)]
    return E


def ruler(a, x0, x1, y, d=0.0, ticks=6, c="ink"):
    i = uid("ru")
    E = [P(a, f"M{x0},{y} L{x1},{y}" + "".join(f" M{x0 + (x1 - x0) * q / ticks},{y - 20} L{x0 + (x1 - x0) * q / ticks},{y + 20}" for q in range(ticks + 1)), c=c, w=6, idp=i), pop(a, i, d)]
    return E


def bubble_sun(a, x, y, r=330, d=0.0):
    i = uid("hb")
    return [O(a, x, y, r, c="gold", idp=i, sw=6), pop(a, i, d), wig(a, i, (x, y), 3, 1)] + ic(a, "sun", x, y, 130, d + 0.1, mv="spin", c="gold")


# ---------- boards ----------
bd(0, earth(0, 300, 600, 110, 0.0), voy(0, 1550, 550, 0.9, 0.1), beam(0, 420, 600, 1400, 560, 0.3, 2.5), t(0, 900, 300, 70, "Hello?", c="blue", d=0.2))
bd(0.5, clock(0.5, 600, 550, 300, 0.0), big(0.5, 1300, 400, "1 day", c="red", d=0.2, s=160), voy(0.5, 1300, 750, 0.6, 0.3))
bd(1, voy(1, 1500, 550, 0.9, 0.0), earth(1, 350, 600, 100, 0.1), beam(1, 1380, 560, 460, 600, 0.2, 2.5, c="blue"), t(1, 950, 300, 70, "...hello!", c="red", d=0.4))
bd(1.5, big(1.5, 960, 380, "2 days", c="red", d=0.0, s=170), clock(1.5, 500, 750, 180, 0.2), clock(1.5, 1420, 750, 180, 0.3))
bd(2, t(2, 960, 230, 56, "November 18", c="blue", d=0.0), earth(2, 300, 650, 100, 0.1), ruler(2, 450, 1400, 650, 0.2), voy(2, 1600, 600, 0.7, 0.3), big(2, 960, 450, "1 light day", c="red", d=0.4, s=110))
bd(2.5, voy(2.5, 600, 600, 1.4, 0.0), ic(2.5, "earth_arc", 1400, 800, 300, 0.2, mv="bob", c="blue"), arr(2.5, 800, 500, 1250, 700, c="red", d=0.4))
bd(3, big(3, 960, 380, "26 billion km", c="red", d=0.0, s=130), ruler(3, 300, 1620, 650, 0.2, ticks=10), voy(3, 1620, 850, 0.5, 0.4))
bd(3.5, big(3.5, 960, 380, "16 billion miles", c="ink", d=0.0, s=120), earth(3.5, 400, 750, 90, 0.2), voy(3.5, 1500, 750, 0.6, 0.3))
bd(4, ic(4, "computer", 600, 550, 300, 0.0, mv="wig"), t(4, 1350, 380, 80, "Hacker News", c="red", d=0.2), t(4, 1350, 540, 60, "front page", d=0.3), star(4, 1350, 720, 0.4, r=40))
bd(4.5, man(4.5, 450, 900, 1.5, 0.0, arms="up"), man(4.5, 750, 900, 1.3, 0.1, arms="up"), big(4.5, 1350, 400, "1 + 1 = ?", c="blue", d=0.3, s=120), ic(4.5, "ruler", 1350, 700, 180, 0.4, mv="wig"))
bd(5, big(5, 1150, 330, "Brain teaser", c="red", d=0.0, s=120), ic(5, "question", 450, 450, 260, 0.2, mv="wig", c="red"), voy(5, 1150, 720, 0.8, 0.3, mood="o"))
bd(5.5, ic(5.5, "phone", 500, 550, 260, 0.0, mv="wig"), clock(5.5, 950, 550, 180, 0.2), ic(5.5, "speaker", 1400, 550, 220, 0.3, mv="wig"), ic(5.5, "question", 1700, 350, 120, 0.4, mv="wig", c="red"))
bd(6, voy(6, 800, 560, 1.8, 0.0), t(6, 1500, 350, 80, "Voyager 1", c="blue", d=0.2), star(6, 1500, 550, 0.4, r=40))
bd(6.5, ic(6.5, "rocket", 600, 600, 320, 0.0, mv="wig"), big(6.5, 1300, 400, "1977", c="red", d=0.2, s=160), dotsky(6.5, 8, 0.3))
bd(7, big(7, 960, 380, "49 years", c="red", d=0.0, s=150), voy(7, 500, 750, 0.6, 0.2), clock(7, 1420, 750, 180, 0.3))
bd(7.5, voy(7.5, 700, 560, 1.3, 0.0), ic(7.5, "signal", 1300, 500, 200, 0.2, mv="bob", c="blue"), t(7.5, 1300, 800, 64, "still talking", c="blue", d=0.3))
bd(8, big(8, 960, 300, "Twist one", c="red", d=0.0, s=140), voy(8, 600, 750, 0.7, 0.2), cross(8, 600, 750, d=0.5), ic(8, "sun", 1350, 700, 200, 0.3, mv="spin", c="gold"))
bd(8.5, ic(8.5, "headlight", 500, 550, 260, 0.0, mv="wig", c="gold"), beam(8.5, 650, 550, 1700, 550, 0.1, 2.5, c="gold"), big(8.5, 1200, 330, "light", c="gold", d=0.3, s=140))
bd(9, t(9, 960, 250, 64, "fastest thing there is", d=0.0), big(9, 960, 450, "300,000 km/s", c="red", d=0.2, s=120), beam(9, 300, 700, 1600, 700, 0.3, 1.5, c="gold"))
bd(9.5, earth(9.5, 400, 600, 110, 0.0), beam(9.5, 520, 600, 1500, 600, 0.1, 0.8, c="gold", n=4), ic(9.5, "check", 1600, 600, 140, 0.5, mv="bob", c="green"), t(9.5, 1000, 400, 64, "7.5 times around Earth", d=0.2))
bd(10, ic(10, "sun", 450, 550, 260, 0.0, mv="spin", c="gold"), beam(10, 620, 550, 1300, 550, 0.2, 2.5, c="gold"), earth(10, 1450, 550, 100, 0.2), big(10, 960, 300, "8 min", c="red", d=0.3, s=120))
bd(10.5, ic(10.5, "moon", 500, 550, 220, 0.0, mv="bob"), beam(10.5, 640, 550, 1300, 550, 0.1, 0.6, c="gold"), earth(10.5, 1450, 550, 100, 0.2), big(10.5, 960, 300, "~1 s", c="blue", d=0.3, s=120))
bd(11, ic(11, "satellite", 500, 550, 240, 0.0, mv="wig"), ic(11, "sine", 960, 550, 220, 0.2, mv="wig", c="red"), t(11, 960, 800, 64, "radio = light", c="red", d=0.3), ic(11, "headlight", 1450, 550, 200, 0.4, mv="wig", c="gold"))
bd(11.5, R(11.5, 760, 300, 400, 400, c="red", fill="paper", sw=10), big(11.5, 960, 500, "c", c="ink", d=0.1, s=200), t(11.5, 960, 800, 64, "speed limit", c="red", d=0.3), ic(11.5, "car", 450, 600, 180, 0.3, mv="wig"), ic(11.5, "rocket", 1500, 600, 180, 0.4, mv="wig"))
bd(12, ic(12, "phone", 600, 550, 280, 0.0, mv="wig"), cross(12, 600, 550, d=0.4), t(12, 1300, 450, 64, "new phone?", d=0.2), voy(12, 1350, 750, 0.5, 0.3, mood="sad"))
bd(12.5, ic(12.5, "signal", 600, 550, 260, 0.0, mv="bob", c="blue"), cross(12.5, 600, 550, d=0.4), t(12.5, 1300, 450, 64, "better plan?", d=0.2), man(12.5, 1350, 900, 1.3, 0.3))
bd(13, voy(13, 500, 600, 1.0, 0.0), sh(13, [], 0, 0, 0, 0.1) if False else [], big(13, 1300, 380, "17 km/s", c="red", d=0.2, s=130), ic(13, "wind", 1300, 650, 180, 0.3, mv="wig"))
bd(13.5, big(13.5, 1100, 380, "60,000 km/h", c="ink", d=0.0, s=110), ic(13.5, "rocket", 450, 650, 260, 0.1, mv="wig"), beam(13.5, 650, 700, 1600, 700, 0.3, 1.2, c="red", n=2))
bd(14, voy(14, 600, 600, 1.0, 0.0, mood="o"), ic(14, "question", 1300, 450, 200, 0.2, mv="wig", c="red"), t(14, 1300, 750, 70, "Fast?", d=0.3))
bd(14.5, bar(14.5, 650, 950, 160, 12, "red", 0.0), t(14.5, 730, 1000, 50, "Voyager", d=0.0), bar(14.5, 1000, 950, 160, 650, "gold", 0.2), t(14.5, 1080, 1000, 50, "light", d=0.2), big(14.5, 1500, 380, "x17,000", c="red", d=0.5, s=110), voy(14.5, 400, 600, 0.5, 0.3))
bd(15, clock(15, 500, 550, 260, 0.0), big(15, 1300, 400, "49 years", c="red", d=0.2, s=130), ruler(15, 900, 1700, 750, 0.3))
bd(15.5, earth(15.5, 350, 600, 100, 0.0), ruler(15.5, 480, 1450, 600, 0.1), voy(15.5, 1600, 560, 0.6, 0.3), big(15.5, 960, 330, "1 light day", c="blue", d=0.4, s=110))
bd(16, big(16, 960, 300, "Twist two", c="red", d=0.0, s=140), voy(16, 600, 700, 0.8, 0.2), t(16, 1350, 650, 90, "psst...", c="blue", d=0.4), ic(16, "speaker", 1350, 850, 120, 0.4, mv="wig"))
bd(16.5, big(16.5, 1200, 400, "~20 W", c="red", d=0.0, s=160), ic(16.5, "battery", 500, 550, 240, 0.1, mv="wig", c="green"), voy(16.5, 1200, 750, 0.5, 0.3))
bd(17, R(17, 400, 300, 400, 600, c="ink", fill="paper", sw=8), ic(17, "headlight", 600, 450, 160, 0.1, mv="wig", c="gold"), t(17, 1300, 350, 64, "a fridge light bulb", d=0.2), ic(17, "speaker", 1300, 650, 200, 0.3, mv="wig"))
bd(17.5, voy(17.5, 1550, 450, 0.7, 0.0), ic(17.5, "sun", 300, 600, 160, 0.1, mv="spin", c="gold"), beam(17.5, 1450, 470, 450, 600, 0.2, 2.0, c="blue"), t(17.5, 960, 850, 64, "across the solar system", d=0.4))
bd(18, voy(18, 400, 600, 0.8, 0.0), ic(18, "sine", 900, 600, 220, 0.1, mv="wig", c="red"), ic(18, "sine", 1300, 600, 140, 0.2, mv="wig", c="red"), ic(18, "sine", 1600, 600, 70, 0.3, mv="wig", c="red"))
bd(18.5, bar(18.5, 500, 950, 140, 600, "red", 0.0), bar(18.5, 750, 950, 140, 300, "red", 0.2), bar(18.5, 1000, 950, 140, 120, "red", 0.4), bar(18.5, 1250, 950, 140, 40, "red", 0.6), big(18.5, 1500, 330, "fainter", c="blue", d=0.5, s=110))
bd(19, ic(19, "flask", 450, 600, 260, 0.0, mv="wig", c="red"), rings(19, 1200, 550, 4, 0.2), t(19, 450, 900, 56, "spray paint", d=0.2))
bd(19.5, rings(19.5, 960, 560, 5, 0.0), t(19.5, 960, 1000, 60, "bigger and bigger ball", c="red", d=0.6))
bd(20, rings(20, 600, 560, 2, 0.0), big(20, 1350, 400, "2x far", c="ink", d=0.3, s=130), arr(20, 900, 560, 1150, 560, c="ink", d=0.5))
bd(20.5, big(20.5, 1150, 400, "1/4", c="red", d=0.0, s=180), rings(20.5, 500, 560, 3, 0.1, c="blue"), t(20.5, 1150, 650, 64, "four times fainter", c="red", d=0.3))
bd(21, man(21, 500, 900, 1.6, 0.0, arms="up"), ic(21, "question", 500, 320, 150, 0.2, mv="wig", c="red"), ic(21, "speaker", 1300, 550, 200, 0.3, mv="wig"), t(21, 1300, 800, 64, "how do we hear?", d=0.3))
bd(21.5, dish(21.5, 900, 600, 1.4, 0.0), big(21.5, 1550, 400, "giant ears", c="blue", d=0.3, s=100), ic(21.5, "eye", 1550, 650, 150, 0.4, mv="wig"))
bd(22, t(22, 960, 230, 56, "Deep Space Network", c="blue", d=0.0), dish(22, 650, 650, 1.2, 0.1), man(22, 1050, 950, 0.6, 0.3), big(22, 1450, 500, "70 m", c="red", d=0.4, s=150))
bd(22.5, dish(22.5, 600, 650, 1.3, 0.0), ruler(22.5, 1050, 1750, 550, 0.2, ticks=7), t(22.5, 1400, 700, 64, "seventy meters wide", c="red", d=0.4))
bd(23, earth(23, 960, 600, 260, 0.0), ic(23, "map_pin", 760, 450, 110, 0.2, mv="bob", c="red"), ic(23, "map_pin", 1080, 420, 110, 0.3, mv="bob", c="red"), ic(23, "map_pin", 1180, 760, 110, 0.4, mv="bob", c="red"),
   t(23, 400, 300, 56, "California", d=0.2), t(23, 1550, 300, 56, "Spain", d=0.3), t(23, 1550, 900, 56, "Australia", d=0.4))
bd(23.5, earth(23.5, 700, 600, 220, 0.0), spin(23.5, "ec%dz" % 0, (700, 600), 1) if False else [], dish(23.5, 700, 280, 0.4, 0.2), beam(23.5, 1700, 300, 800, 300, 0.3, 1.6, c="red"), t(23.5, 1400, 850, 60, "always facing deep space", c="blue", d=0.4))
bd(24, dish(24, 700, 600, 1.3, 0.0), beam(24, 1700, 200, 800, 450, 0.2, 1.4, c="red", n=4), t(24, 1450, 800, 64, "gathers the whisper", d=0.3))
bd(24.5, P(24.5, "M500,500 Q750,850 1000,500", c="ink", w=12, idp="bw1"), pop(24.5, "bw1", 0.0), ic(24.5, "water", 750, 300, 140, 0.2, mv="bob", c="blue"), ic(24.5, "cloud", 750, 150, 180, 0.1, mv="bob", c="muted"),
   ic(24.5, "water", 600, 330, 90, 0.3, mv="bob", c="blue"), t(24.5, 1400, 550, 64, "a bowl catching rain", c="blue", d=0.4))
bd(25, big(25, 960, 300, "Twist three", c="red", d=0.0, s=140), voy(25, 600, 700, 0.7, 0.2, mood="o"), ic(25, "building", 1350, 700, 200, 0.3, mv="bob"))
bd(25.5, earth(25.5, 450, 600, 90, 0.0), voy(25.5, 650, 560, 0.35, 0.1), t(25.5, 1300, 400, 70, "next door!", c="red", d=0.3), dotsky(25.5, 8, 0.4, seed=2))
bd(26, ic(26, "sun", 1650, 500, 160, 0.0, mv="spin", c="red"), ruler(26, 300, 1500, 650, 0.1, ticks=4), big(26, 900, 380, "4+ light years", c="red", d=0.3, s=110), earth(26, 300, 650, 60, 0.2))
bd(26.5, big(26.5, 960, 380, "1,500+ light days", c="ink", d=0.0, s=110), [ruler(26.5, 200 + 300 * q, 450 + 300 * q, 700, 0.1 + 0.1 * q, ticks=2) for q in range(5)], voy(26.5, 270, 850, 0.3, 0.6))
bd(27, voy(27, 450, 600, 0.9, 0.0), arr(27, 700, 600, 1350, 600, c="red", d=0.2), ic(27, "sun", 1550, 600, 160, 0.3, mv="spin", c="red"), t(27, 960, 330, 64, "at Voyager speed", d=0.3))
bd(27.5, big(27.5, 960, 380, "75,000 years", c="red", d=0.0, s=130), t(27.5, 960, 560, 56, "by our math", c="muted", d=0.2), clock(27.5, 500, 800, 160, 0.3), clock(27.5, 1420, 800, 160, 0.4))
bd(28, ic(28, "sun", 1500, 400, 160, 0.0, mv="spin", c="red"), voy(28, 600, 650, 0.9, 0.1), cross(28, 1100, 500, d=0.4), t(28, 1300, 800, 60, "not aimed at it", d=0.3))
bd(28.5, dotsky(28.5, 14, 0.0, seed=3), voy(28.5, 960, 560, 1.0, 0.2), t(28.5, 960, 950, 60, "drifting through the dark", c="blue", d=0.4))
bd(29, bubble_sun(29, 750, 560, 330, 0.0), voy(29, 1400, 560, 0.6, 0.3), arr(29, 1100, 560, 1250, 560, c="red", d=0.5), big(29, 1500, 250, "2012", c="red", d=0.3, s=110))
bd(29.5, voy(29.5, 700, 560, 1.2, 0.0), star(29.5, 700, 250, 0.2, r=50), big(29.5, 1400, 450, "first ever", c="red", d=0.3, s=110), ic(29.5, "check", 1400, 700, 140, 0.4, mv="bob", c="green"))
bd(30, ic(30, "battery", 600, 550, 300, 0.0, mv="wig", c="red"), bar(30, 1100, 900, 120, 500, "green", 0.1), bar(30, 1300, 900, 120, 300, "gold", 0.3), bar(30, 1500, 900, 120, 120, "red", 0.5), t(30, 1300, 250, 60, "power fading", c="red", d=0.4))
bd(30.5, voy(30.5, 600, 560, 1.0, 0.0, mood="sad"), ic(30.5, "gear", 1200, 450, 150, 0.2, mv="spin"), ic(30.5, "gear", 1450, 600, 120, 0.3, mv="spin"), cross(30.5, 1300, 500, d=0.5), t(30.5, 1300, 850, 60, "switching off", d=0.4))
bd(31, big(31, 960, 330, "April 2026", c="red", d=0.0, s=120), ic(31, "magnifier", 600, 700, 180, 0.2, mv="wig"), cross(31, 600, 700, d=0.5), voy(31, 1350, 750, 0.5, 0.3))
bd(31.5, ic(31.5, "battery", 600, 600, 260, 0.0, mv="wig", c="green"), check(31.5, 600, 300, d=0.3), t(31.5, 1350, 500, 70, "save energy", c="green", d=0.2), ic(31.5, "moon", 1350, 750, 140, 0.4, mv="bob"))
bd(32, big(32, 960, 300, "Fine print", c="blue", d=0.0, s=130), t(32, 960, 500, 56, "date and distance: EarthSky, NASA data", d=0.2), ic(32, "satellite", 600, 780, 150, 0.3, mv="wig"), ic(32, "computer", 1350, 780, 150, 0.4, mv="wig"))
bd(32.5, big(32.5, 960, 350, "75,000 years", c="ink", d=0.0, s=110), t(32.5, 960, 540, 56, "our own math", c="muted", d=0.2), ic(32.5, "ruler", 600, 780, 150, 0.3, mv="wig"), ic(32.5, "magnifier", 1350, 780, 150, 0.4, mv="wig"))
bd(33, voy(33, 1400, 560, 0.9, 0.0), voy(33, 600, 600, 0.6, 0.2), t(33, 600, 900, 56, "Voyager 2", c="blue", d=0.3), arr(33, 800, 600, 1150, 580, c="blue", d=0.4))
bd(33.5, big(33.5, 960, 380, "~2035", c="blue", d=0.0, s=150), clock(33.5, 500, 750, 160, 0.2), voy(33.5, 1420, 750, 0.5, 0.3))
bd(34, ic(34, "phone", 600, 550, 260, 0.0, mv="wig"), clock(34, 1000, 550, 180, 0.2), ic(34, "question", 1450, 500, 180, 0.3, mv="wig", c="red"), t(34, 960, 850, 64, "why a day?", d=0.4))
bd(34.5, earth(34.5, 300, 600, 100, 0.0), beam(34.5, 420, 600, 1450, 600, 0.1, 2.5, c="gold", n=4), voy(34.5, 1600, 560, 0.6, 0.2), big(34.5, 960, 330, "even light", c="gold", d=0.3, s=110))
bd(35, dish(35, 700, 600, 1.2, 0.0), ic(35, "speaker", 1350, 450, 160, 0.2, mv="wig"), t(35, 1350, 700, 64, "how do we hear?", d=0.3))
bd(35.5, dish(35.5, 600, 600, 1.1, 0.0), clock(35.5, 1350, 500, 200, 0.2), big(35.5, 1350, 800, "patience", c="blue", d=0.4, s=100))
bd(36, ic(36, "phone", 600, 550, 280, 0.0, mv="wig"), clock(36, 600, 250, 120, 0.2), t(36, 1300, 450, 64, "a text feels slow?", d=0.3), man(36, 1350, 950, 1.2, 0.3))
bd(36.5, earth(36.5, 350, 600, 100, 0.0), voy(36.5, 1500, 550, 1.0, 0.1), beam(36.5, 1380, 560, 470, 600, 0.2, 2.5, c="blue"), t(36.5, 950, 300, 70, "hello!", c="red", d=0.4))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"NASA's": "Nasa's", "NASA": "Nasa", "EarthSky": "Earth Sky", "Voyager 1": "Voyager one", "Voyager 2": "Voyager two",
                                       "Voyager's": "Voyager", "Sun's": "Sun", "mind bending": "mind bending"})
