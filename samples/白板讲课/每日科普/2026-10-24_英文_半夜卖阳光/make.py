"""Daily science short 2026-10-24 (English): "Selling Sunlight at Night?"
News: Reflect Orbital (space mirrors that beam sunlight down after dark) is on Live Science's "Trending" bar (homepage, 24 Oct 2026);
Oct 15 2026 press release: two dedicated launches booked with India's Skyroot Aerospace (reflectorbital.com/press, SpaceWatch.GLOBAL,
evertiq 19 Oct). Space.com 13 Jul 2026: FCC licensed the first demo craft Earendil-1, mirror ~18 m (60 ft) on a side; 50,000+
mirrors planned by 2035; astronomer John Barentine: beam "four times brighter than the full moon"; concerns: astronomy, wildlife.
Wikipedia (Reflect Orbital): 600-650 km sun-synchronous orbit, 18 m x 18 m, 16 kg, spot ~5 km wide, ~0.1 lux (like a full moon).
Textbook: the Sun is ~0.53 deg wide (distance / diameter ~ 108) -> a reflected spot is at least distance/108 wide (625 km -> ~5.8 km);
illuminance on the spot ~ E_sun x A_mirror / A_spot -> to equal full sunlight the mirror must be as big as the spot.
Our estimates (said as estimates): 324 m^2 mirror vs ~20 million m^2 spot -> diluted ~60,000x -> at most a lux or two straight overhead;
50,000 x 324 m^2 ~ 16 km^2 < one 5-km spot (~20 km^2); at midnight (mid-latitudes) Earth's shadow reaches far above 600 km.
Character: Glint, a little mirror satellite. Gag: "not at midnight".
    python3 make.py <kokoro model dir> | --boards-only | --fake   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("一家创业公司想卖给你阳光，|在晚上。", "A startup wants to sell you sunlight | at night."),
 ("不是台灯，不是灯泡，|是太空里的一面镜子。", "Not a lamp. Not a light bulb. | A mirror in space."),
 ("今天的问题：轨道上的一面镜子，|能把黑夜变成白天吗？", "Today's question: can a mirror in orbit | turn night into day?"),
 ("认识一下小闪。|一面有大梦想的太空镜子。", "Meet Glint. | A space mirror with big dreams."),
 ("这家公司叫Reflect Orbital，|第一面镜子叫Earendil-1。", "The company is called Reflect Orbital. | Its first mirror is Earendil-1."),
 ("今年7月，美国的FCC|批准它发射。", "In July, the FCC, America's airwaves regulator, | gave it permission to launch."),
 ("这个月，它又跟印度的Skyroot|订了两枚火箭。", "This month, it booked two more rockets | from India's Skyroot."),
 ("计划：到2035年，|五万多面镜子。", "The plan: more than fifty thousand mirrors | by 2035."),
 ("原理？|其实是个老把戏。", "How does it work? | It's an old trick."),
 ("还记得用手表反光，|在教室天花板上晃光斑吗？", "Remember bouncing sunlight off a watch | onto the classroom ceiling?"),
 ("一模一样，|只不过手表在六百公里高。", "Same idea, | except the watch is 600 kilometers up."),
 ("秘密是：太阳下山以后，|你在地球的影子里。", "Here's the secret: after sunset, | you're in Earth's shadow."),
 ("可在你头顶很高的地方，|太阳还照着。", "But high above you, | the sun is still shining."),
 ("小闪接住这束阳光，|一歪，就打到你身上。", "Glint catches that sunlight | and tilts it down to you."),
 ("它的镜子每边大约18米，|比网球场还宽。", "Its mirror is about 18 meters on a side, | wider than a tennis court."),
 ("可它只有16公斤，|跟一台微波炉差不多重。", "Yet it weighs only 16 kilos, | about as much as a microwave."),
 ("反转一：光斑没法做小。|太阳挡了道。", "Twist one: you can't make a tiny spotlight. | The sun gets in the way."),
 ("太阳不是一个点，|是一个大约半度宽的圆盘。", "The sun isn't a dot. | It's a disk, about half a degree wide."),
 ("所以每一束反射光都会散开，|像一个圆锥。", "So every reflected beam spreads out, | like a cone."),
 ("规律是：光斑至少有|距离除以108那么宽。", "The rule: the spot is at least | the distance divided by 108."),
 ("从六百公里高照下来，|光斑大约五六公里宽。", "From 600 kilometers up, | that's a spot about five or six kilometers wide."),
 ("公司自己说大约5公里。|算的对得上。", "The company says about 5 kilometers. | The math checks out."),
 ("照亮的是一整片街区，|不是你家后院。", "It lights a whole neighborhood, | not one backyard."),
 ("反转二：有多亮？|我们把光摊开看看。", "Twist two: how bright is it? | Let's spread the light out."),
 ("小闪的镜子大约300平方米，|光斑大约两千万平方米。", "Glint's mirror is about 300 square meters. | The spot is about 20 million."),
 ("所以阳光被摊薄了|好几万倍。", "So the sunlight gets thinned out | tens of thousands of times."),
 ("我们粗算一下：就算正对头顶，|最多也就一两勒克斯。", "Our rough math: even straight overhead, | it's a lux or two at most."),
 ("实际上它斜着从更远处照过来，|还要更暗。", "In practice it shines from farther away, at a slant, | so it's even dimmer."),
 ("报道里说，大约像满月。|有位天文学家说，最多能到满月的四倍。", "Reports compare it to a full moon. | One astronomer says up to four times brighter."),
 ("够你看清地图，|不够你晒黑。", "Bright enough to read a map. | Not bright enough to get a tan."),
 ("反转三，最大的一个：真要变成白天，|得要多大的镜子？", "Twist three, the big one: to make real daylight, | how much mirror would you need?"),
 ("白天大约十万勒克斯，|是几十万个满月。", "Daylight is about 100,000 lux. | That's hundreds of thousands of full moons."),
 ("答案很漂亮：|镜子得跟光斑一样大。", "The answer is beautiful: | the mirror has to be as big as the spot."),
 ("想把一个5公里的小镇照成正午，|就得有一面5公里的镜子。", "To light a five-kilometer town like noon, | you'd need a five-kilometer mirror."),
 ("就算五万面镜子全加起来，|也只有大约16平方公里。", "Even all fifty thousand mirrors combined | add up to only about 16 square kilometers."),
 ("连一个小镇的正午，|都凑不出来。", "Not enough to give | even one town a noon."),
 ("那它干嘛用？公司说：|日落后给太阳能电站补光、救援、夜间施工。", "So what's it for? The company says: | solar farms after sunset, rescue work, night construction."),
 ("天文学家很担心：|一道反光就能毁掉一张望远镜照片。", "Astronomers are worried. | One flash of reflected sunlight can ruin a telescope image."),
 ("动物也靠黑夜，|知道什么时候睡、觅食、迁徙。", "And animals rely on the dark | to know when to sleep, hunt, and migrate."),
 ("友情提示：它只在傍晚和清晨好用，|那时镜子还在阳光里。", "Friendly fine print: it works best around dusk and dawn, | while the mirror is still in sunlight."),
 ("我们粗算：到了半夜，|小闪自己也掉进了地球的影子。", "Our rough math: by midnight, | Glint itself is inside Earth's shadow."),
 ("而且它每秒飞七八公里，|一面镜子只能照你几分钟。", "And it zooms by at seven or eight kilometers a second, | so one mirror can only aim at you for minutes."),
 ("所以第一面镜子只是个试验。|夜空能不能分出去，还没有答案。", "So the first mirror is just a test. | Whether we should share the night sky is still an open question."),
 ("小闪的梦想还在：|随叫随到的阳光。", "Glint's dream lives on: | sunlight on demand."),
 ("只是别在半夜，|也永远比不上正午。", "Just not at midnight, | and never as bright as noon."),
]
TITLE = {"zh": "夜里卖阳光？", "en": "Selling Sunlight at Night?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 900, 0.5, r=16)
    B.append(E)


def glint(a, x, y, k=1.0, mood="happy", d=None, tilt=0):
    """Glint: a square silver mirror with a face and two little solar-panel wings that flap."""
    i = uid("gl") + "_"
    wl, wr = i + "wl", i + "wr"
    E = [R(a, x - 90 * k, y - 90 * k, 180 * k, 180 * k, c="ink", fill="blue", idp=i),
         P(a, f"M{x - 60 * k},{y - 70 * k} L{x - 20 * k},{y - 70 * k} M{x - 70 * k},{y - 50 * k} L{x - 50 * k},{y - 50 * k}", c="ink", w=4, idp=i),
         O(a, x - 35 * k, y - 10 * k, 12 * k, c="ink", fill="ink", idp=i), O(a, x + 35 * k, y - 10 * k, 12 * k, c="ink", fill="ink", idp=i),
         R(a, x - 190 * k, y - 25 * k, 90 * k, 50 * k, c="ink", fill="gold", idp=wl), R(a, x + 100 * k, y - 25 * k, 90 * k, 50 * k, c="ink", fill="gold", idp=wr)]
    m = {"happy": f"M{x - 30 * k},{y + 30 * k} Q{x},{y + 60 * k} {x + 30 * k},{y + 30 * k}",
         "o": f"M{x - 13 * k},{y + 45 * k} a13,13 0 1,0 26,0 a13,13 0 1,0 -26,0",
         "sad": f"M{x - 30 * k},{y + 55 * k} Q{x},{y + 28 * k} {x + 30 * k},{y + 55 * k}"}[mood]
    E += [P(a, m, c="ink", w=5, idp=i), wig(a, wl, (x - 100 * k, y), 12, 1.6), wig(a, wr, (x + 100 * k, y), 12, 1.6),
          bob(a, i, 8 * k, 1.2)]
    if tilt:
        E.append(rot(a, [i], tilt, (x, y), 0.3, 0.8))
    if d is not None:
        E.append(pop(a, [i, wl, wr], d))
    return E, i


def sun(a, x, y, s=200, d=0.0):
    i = uid("sun")
    return [{"t": "icon", "at": a, "id": i, "name": "sun", "x": x, "y": y, "size": s, "c": "gold"}, pop(a, i, d), spin(a, i, (x, y), 10)]


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def person(a, x, y, k=1.0, c="ink"):
    i = uid("ps")
    return [O(a, x, y - 130 * k, 40 * k, c=c, idp=i), P(a, f"M{x},{y - 90 * k} L{x},{y + 40 * k} M{x - 60 * k},{y - 30 * k} L{x},{y - 60 * k} L{x + 60 * k},{y - 30 * k} "
                                                         f"M{x},{y + 40 * k} L{x - 40 * k},{y + 130 * k} M{x},{y + 40 * k} L{x + 40 * k},{y + 130 * k}", c=c, w=6, idp=i),
            bob(a, i, 5, 1.0), wig(a, i, (x, y + 130 * k), 4, 1.2)], i


def earth(a, y=820, c="blue", night=False):
    """Curved Earth surface; night side shaded."""
    i = uid("ea")
    E = [P(a, f"M100,{y + 140} Q960,{y - 120} 1820,{y + 140}", c=c, w=7, idp=i), bob(a, i, 3, 0.4)]
    if night:
        n = uid("nt")
        E += [P(a, f"M100,{y + 150} Q960,{y - 100} 1820,{y + 150} L1820,1000 L100,1000 Z", c="ink", w=2, fill="ink", idp=n), pop(a, n, 0.0), pulse(a, n, 0.6)]
    return E


def town(a, x, y, n=4, d=0.0):
    E = []
    for q in range(n):
        h = 80 + 40 * (q % 3)
        i = uid("tw")
        E += [R(a, x + 90 * q, y - h, 70, h, c="ink", fill="muted", idp=i), pop(a, i, d + 0.06 * q), bob(a, i, 3, 0.6 + 0.1 * q)]
    return E


def beam(a, x0, y0, x1, y1, w1=80, c="gold", d=0.0):
    """A light cone from a point to a spot of half-width w1; grows in."""
    i = uid("bm")
    return [P(a, f"M{x0},{y0} L{x1 - w1},{y1} L{x1 + w1},{y1} Z", c=c, w=3, fill=c, idp=i, opacity=45),
            {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x0, y0], "dur": 0.6, "delay": d}, pulse(a, i, d + 0.8)]


def ray(a, x0, y0, x1, y1, d=0.0, c="gold"):
    return arr(a, x0, y0, x1, y1, c=c, d=d, dur=0.4)


def spot(a, x, y, rx, d=0.0, c="gold"):
    i = uid("sp")
    return [{"t": "ellipse", "at": a, "x": x - rx, "y": y - rx * 0.25, "w": 2 * rx, "h": rx * 0.5, "c": c, "sw": 5, "fill": c, "id": i}, pop(a, i, d), pulse(a, i, d + 0.5)]


def moonish(a, x, y, s=120, d=0.0):
    return icon(a, "moon", x, y, s, d, c="gold", mv="bob")


def zz(a, x, y, d=0.0):
    E = []
    for q in range(3):
        E += T(a, x + 40 * q, y - 50 * q, 40 + 12 * q, "z", c="muted", d=d + 0.2 * q)
    return E


# 0 sell sunlight
g_, gi = glint(0, 960, 420, 1.2, d=0.0)
bd(0, g_, sun(0, 300, 260, 180, 0.1), BIG(0, 960, 800, "SUNLIGHT FOR SALE", c="gold", d=0.2, s=110), [sh(0, gi, 0, -40, 0.6, 0.6)])
# 0.5 at night
bd(0.5, earth(0.5, 780, night=True), moonish(0.5, 1500, 250, 140, 0.0), beam(0.5, 960, 200, 960, 760, 140, d=0.2), glint(0.5, 960, 200, 0.6)[0],
   BIG(0.5, 450, 400, "at NIGHT", c="blue", d=0.4, s=110))
# 1 not a lamp
bd(1, icon(1, "headlight", 560, 500, 220, 0.0, mv="wig"), cross(1, 560, 500, d=0.4), icon(1, "laser", 1360, 500, 220, 0.2, mv="wig"), cross(1, 1360, 500, d=0.6),
   T(1, 960, 820, 64, "no lamps. no bulbs.", c="muted", d=0.3))
# 1.5 a mirror in space
bd(1.5, icon(1.5, "mirror", 960, 480, 300, 0.0, c="blue", mv="spin"), icon(1.5, "satellite", 1500, 300, 160, 0.2, mv="spin"), icon(1.5, "globe", 420, 760, 180, 0.3, c="blue", mv="spin"),
   T(1.5, 960, 860, 60, "a mirror... in space", c="blue", d=0.4))
# 2 today's question
g_, gi = glint(2, 600, 450, 1.0, mood="o")
bd(2, g_, icon(2, "question", 1300, 420, 260, 0.2, c="red", mv="wig"), earth(2, 860), T(2, 1300, 720, 56, "night -> day?", c="red", d=0.5))
# 2.5 turn night into day
m_ = moonish(2.5, 600, 450, 220, 0.0)
s_ = sun(2.5, 1350, 450, 220, 0.3)
bd(2.5, m_, s_, arr(2.5, 800, 450, 1150, 450, c="ink", d=0.2), [sh(2.5, m_[0]["id"], 0, 200, 0.6, 0.8), sh(2.5, s_[0]["id"], 0, -100, 0.6, 0.8)],
   T(2.5, 960, 860, 60, "can we flip it?", c="ink", d=0.5))
# 3 meet Glint
g_, gi = glint(3, 860, 500, 2.0, d=0.0)
bd(3, g_, BIG(3, 1560, 380, "Glint", c="blue", d=0.4, s=150), [e for q in range(3) for e in star(3, 1450 + 110 * q, 600, 0.6 + 0.1 * q, r=30)])
# 3.5 big dreams
g_, gi = glint(3.5, 600, 600, 1.0)
bd(3.5, g_, [e for q in range(4) for e in icon(3.5, "cloud", 1100 + 180 * (q % 2), 300 + 140 * q // 2, 140, 0.1 + 0.15 * q, c="muted", mv="bob")],
   sun(3.5, 1450, 380, 140, 0.3), T(3.5, 1300, 860, 56, "big dreams", c="gold", d=0.4))
# 4 Reflect Orbital
bd(4, icon(4, "building", 600, 520, 300, 0.0, mv="bob"), T(4, 1250, 420, 80, "Reflect Orbital", c="blue", d=0.2), icon(4, "rocket", 1250, 650, 160, 0.4, c="red", mv="wig"),
   icon(4, "map_pin", 600, 280, 100, 0.3, c="red"))
# 4.5 Earendil-1
g_, gi = glint(4.5, 960, 480, 1.4)
bd(4.5, g_, [rot(4.5, gi, 15, (960, 480), 0.3, 0.6)], BIG(4.5, 960, 860, "Earendil-1", c="blue", d=0.2, s=120), T(4.5, 1550, 300, 44, "demo", c="muted", d=0.5))
# 5 July FCC
bd(5, BIG(5, 600, 400, "July", c="blue", d=0.1, s=130), BIG(5, 1300, 400, "FCC", c="red", d=0.2, s=150), icon(5, "signal", 960, 700, 180, 0.3, mv="wig"),
   icon(5, "satellite", 1500, 750, 140, 0.4, mv="spin"))
# 5.5 permission
r_ = icon(5.5, "rocket", 700, 640, 260, 0.0, c="red", mv="wig")
bd(5.5, r_, [sh(5.5, r_[0]["id"], 0, -360, 0.6, 1.2)], check(5.5, 1300, 500, d=0.3), T(5.5, 1300, 700, 60, "cleared to launch", c="green", d=0.4))
# 6 this month two rockets
r1 = icon(6, "rocket", 700, 640, 240, 0.1, c="red", mv="wig")
r2 = icon(6, "rocket", 1200, 640, 240, 0.3, c="red", mv="wig")
bd(6, r1, r2, [sh(6, r1[0]["id"], 0, -300, 0.7, 1.0), sh(6, r2[0]["id"], 0, -300, 0.9, 1.0)], BIG(6, 960, 220, "x 2", c="red", d=0.2, s=120))
# 6.5 Skyroot India
bd(6.5, BIG(6.5, 960, 380, "Skyroot", c="blue", d=0.1, s=140), icon(6.5, "map_pin", 960, 650, 160, 0.2, c="red"), T(6.5, 960, 830, 60, "India", c="ink", d=0.3),
   icon(6.5, "rocket", 1550, 600, 160, 0.4, c="red", mv="wig"))
# 7 the plan
E = []
for q in range(12):
    i = uid("mm")
    E += [R(7, 300 + 120 * q, 300 + 80 * (q % 3), 70, 70, c="ink", fill="blue", idp=i), pop(7, i, 0.1 + 0.05 * q), bob(7, i, 6, 0.8 + 0.07 * q)]
bd(7, E, BIG(7, 960, 760, "50,000+", c="red", d=0.4, s=150))
# 7.5 by 2035
bd(7.5, BIG(7.5, 960, 420, "by 2035", c="blue", d=0.1, s=150), icon(7.5, "clock", 500, 760, 160, 0.2, mv="spin"), earth(7.5, 820),
   [e for q in range(5) for e in glint(7.5, 800 + 160 * q, 680 - 30 * q, 0.25)[0]])
# 8 how does it work
g_, gi = glint(8, 960, 500, 1.3, mood="o")
bd(8, g_, [e for q in range(3) for e in icon(8, "gear", 450 + 1000 * (q % 2), 380 + 250 * q // 2, 150, 0.2 + 0.1 * q, mv="spin")], T(8, 960, 880, 60, "how?", c="red", d=0.3))
# 8.5 old trick
bd(8.5, icon(8.5, "mirror", 700, 500, 260, 0.0, mv="wig"), sun(8.5, 300, 250, 140, 0.1), ray(8.5, 380, 300, 640, 460, d=0.3), ray(8.5, 760, 460, 1300, 260, d=0.5),
   T(8.5, 1300, 700, 60, "an old trick", c="ink", d=0.4))
# 9 watch reflection
w_ = uid("wa")
bd(9, [O(9, 700, 600, 110, c="ink", fill="muted", idp=w_), P(9, "M700,600 L700,520 M700,600 L760,640", c="ink", w=6, idp=w_), pop(9, w_, 0.0), wig(9, w_, (700, 600), 10, 1.8)],
   sun(9, 300, 250, 140, 0.1), ray(9, 380, 300, 650, 520, d=0.3), ray(9, 760, 520, 1250, 260, d=0.5), T(9, 1300, 800, 52, "tick... flash!", c="gold", d=0.6))
# 9.5 classroom ceiling
sp = spot(9.5, 900, 220, 70, 0.1)
bd(9.5, [P(9.5, "M200,200 L1720,200", c="ink", w=7)], sp, [sh(9.5, sp[0]["id"], 500, 0, 0.4, 1.0), sh(9.5, sp[0]["id"], -700, 0, 1.4, 1.0)],
   person(9.5, 700, 760, 0.8)[0], person(9.5, 1200, 760, 0.8)[0], T(9.5, 960, 960, 48, "classroom chaos", c="muted", d=0.6))
# 10 same idea
bd(10, icon(10, "mirror", 600, 500, 240, 0.0, mv="wig"), BIG(10, 960, 500, "=", c="ink", d=0.2, s=150), glint(10, 1350, 500, 1.0, d=0.3)[0],
   T(10, 960, 820, 56, "same idea", c="blue", d=0.4))
# 10.5 600 km up
g_, gi = glint(10.5, 960, 260, 0.6)
bd(10.5, g_, earth(10.5, 800), arr(10.5, 1300, 780, 1300, 280, c="blue", d=0.2, dur=0.8), BIG(10.5, 1550, 520, "600 km", c="blue", d=0.3, s=110),
   person(10.5, 700, 760, 0.4)[0])
# 11 after sunset
s_ = sun(11, 1500, 500, 200, 0.0)
bd(11, s_, [sh(11, s_[0]["id"], 0, 400, 0.2, 1.5)], earth(11, 760), person(11, 700, 700, 0.6)[0], T(11, 700, 300, 60, "sunset...", c="red", d=0.4))
# 11.5 Earth's shadow
sh_ = uid("shd")
bd(11.5, [O(11.5, 700, 560, 260, c="blue", fill="blue", idp=(e_ := uid("e"))), spin(11.5, e_, (700, 560), 6),
          P(11.5, "M700,300 L1800,330 L1800,790 L700,820 Z", c="ink", w=3, fill="ink", idp=sh_, opacity=60), pop(11.5, sh_, 0.3), pulse(11.5, sh_, 1.0)],
   sun(11.5, 200, 200, 120, 0.1), [e for q in range(3) for e in ray(11.5, 260, 260 + 100 * q, 440, 380 + 100 * q, d=0.2 + 0.1 * q)],
   T(11.5, 1300, 940, 52, "Earth's shadow", c="ink", d=0.5))
# 12 high above
g_, gi = glint(12, 1300, 260, 0.6)
bd(12, earth(12, 820, night=True), g_, person(12, 700, 760, 0.4)[0], arr(12, 700, 600, 700, 300, c="ink", d=0.2), T(12, 700, 230, 52, "up there?", c="ink", d=0.3))
# 12.5 sun still shining
g_, gi = glint(12.5, 1100, 400, 0.9)
bd(12.5, g_, sun(12.5, 300, 300, 200, 0.0), [e for q in range(3) for e in ray(12.5, 420, 260 + 60 * q, 900, 340 + 60 * q, d=0.2 + 0.15 * q)],
   T(12.5, 1100, 720, 60, "still sunny!", c="gold", d=0.5), earth(12.5, 880, night=True))
# 13 Glint catches sunlight
g_, gi = glint(13, 960, 380, 1.0)
bd(13, g_, sun(13, 260, 240, 160, 0.0), ray(13, 360, 260, 760, 360, d=0.2), [wig(13, gi, (960, 380), 6, 1.0)], T(13, 960, 700, 60, "catch!", c="gold", d=0.3),
   earth(13, 880, night=True))
# 13.5 tilts down to you
g_, gi = glint(13.5, 960, 260, 0.8, tilt=25)
bd(13.5, g_, beam(13.5, 960, 340, 960, 790, 160, d=0.4), earth(13.5, 820, night=True), person(13.5, 960, 760, 0.4)[0], T(13.5, 1500, 500, 56, "tilt... ding!", c="ink", d=0.6))
# 14 18 m
g_, gi = glint(14, 760, 520, 1.6)
bd(14, g_, arr(14, 600, 780, 920, 780, c="blue", d=0.2), arr(14, 920, 780, 600, 780, c="blue", d=0.2), BIG(14, 1450, 420, "18 m", c="blue", d=0.3, s=160))
# 14.5 wider than tennis court
ct = uid("ct")
bd(14.5, [R(14.5, 1100, 380, 330, 520, c="green", fill="green", idp=ct), P(14.5, "M1100,640 L1430,640", c="ink", w=6, idp=ct), pop(14.5, ct, 0.0), bob(14.5, ct, 3, 0.6)],
   glint(14.5, 600, 600, 1.4, d=0.2)[0], T(14.5, 1265, 960, 48, "tennis court", c="green", d=0.3), T(14.5, 600, 340, 52, "wider!", c="blue", d=0.5))
# 15 16 kilos
bd(15, BIG(15, 960, 380, "16 kg", c="red", d=0.1, s=170), glint(15, 600, 780, 0.6)[0], icon(15, "block_force", 1350, 760, 160, 0.3, mv="wig"))
# 15.5 microwave
mw = uid("mw")
bd(15.5, [R(15.5, 1100, 420, 420, 260, c="ink", fill="muted", idp=mw), R(15.5, 1140, 460, 260, 180, c="ink", fill="blue", idp=mw), pop(15.5, mw, 0.0), wig(15.5, mw, (1310, 680), 3, 3.0)],
   glint(15.5, 600, 560, 1.0, d=0.2)[0], BIG(15.5, 870, 560, "=", c="ink", d=0.3, s=120), T(15.5, 1310, 800, 52, "ding!", c="red", d=0.6))
# 16 twist one
bd(16, BIG(16, 960, 160, "TWIST 1", c="red", d=0.1, s=90), beam(16, 960, 300, 960, 760, 40, d=0.2), glint(16, 960, 300, 0.6)[0], cross(16, 1300, 700, d=0.6),
   T(16, 1400, 560, 52, "tiny spotlight?", c="ink", d=0.4))
# 16.5 the sun gets in the way
s_ = sun(16.5, 960, 480, 320, 0.0)
bd(16.5, s_, [pulse(16.5, s_[0]["id"], 0.4, 0.8)], glint(16.5, 400, 800, 0.5, mood="sad")[0], T(16.5, 1450, 800, 56, "blame the sun", c="red", d=0.4))
# 17 not a dot
dt = uid("dt")
bd(17, [O(17, 600, 500, 10, c="gold", fill="gold", idp=dt), pop(17, dt, 0.0), pulse(17, dt, 0.3)], cross(17, 600, 500, d=0.4), sun(17, 1350, 500, 300, 0.6),
   T(17, 600, 760, 56, "a dot?", c="muted", d=0.2))
# 17.5 half a degree
s_ = sun(17.5, 1500, 320, 160, 0.0)
eye = icon(17.5, "eye", 400, 640, 160, 0.1, mv="bob")
bd(17.5, s_, eye, arr(17.5, 480, 620, 1420, 280, c="gold", d=0.2), arr(17.5, 480, 660, 1420, 380, c="gold", d=0.3), BIG(17.5, 1000, 760, "0.5°", c="red", d=0.4, s=150))
# 18 spreads out
g_, gi = glint(18, 960, 260, 0.6)
bd(18, g_, beam(18, 960, 330, 960, 780, 260, d=0.2), sun(18, 300, 200, 120, 0.1), earth(18, 840, night=True))
# 18.5 like a cone
bd(18.5, beam(18.5, 960, 200, 960, 760, 300, c="gold", d=0.0), icon(18.5, "laser", 450, 400, 140, 0.2, mv="wig"), T(18.5, 960, 860, 64, "a cone of light", c="gold", d=0.4),
   [e for q in range(3) for e in star(18.5, 760 + 200 * q, 600, 0.5 + 0.1 * q, r=24)])
# 19 the rule
bd(19, T(19, 960, 300, 70, "spot width ≥", c="ink", d=0.1), BIG(19, 960, 520, "distance ÷ 108", c="red", d=0.3, s=120), sun(19, 1650, 760, 140, 0.4), glint(19, 300, 760, 0.5)[0])
# 19.5 108
bd(19.5, sun(19.5, 1300, 500, 260, 0.0), arr(19.5, 400, 500, 1150, 500, c="ink", d=0.2), T(19.5, 780, 420, 52, "sun's distance", c="ink", d=0.3),
   T(19.5, 1300, 820, 52, "= 108 sun-widths", c="red", d=0.5), icon(19.5, "ruler", 400, 720, 140, 0.4, mv="wig"))
# 20 from 600 km
g_, gi = glint(20, 960, 200, 0.5)
bd(20, g_, beam(20, 960, 260, 960, 780, 360, d=0.2), earth(20, 820, night=True), T(20, 1500, 400, 56, "600 km", c="blue", d=0.3))
# 20.5 5-6 km wide
bd(20.5, spot(20.5, 960, 640, 400, 0.0), town(20.5, 700, 640, 6, 0.2), arr(20.5, 560, 800, 1360, 800, c="red", d=0.3), arr(20.5, 1360, 800, 560, 800, c="red", d=0.3),
   BIG(20.5, 960, 320, "5–6 km", c="red", d=0.4, s=150))
# 21 company says 5 km
bd(21, icon(21, "building", 600, 560, 260, 0.0, mv="bob"), T(21, 1300, 420, 64, "company: ~5 km", c="blue", d=0.2), T(21, 1300, 620, 64, "our math: ~5.8 km", c="red", d=0.4),
   check(21, 1300, 800, d=0.6))
# 21.5 checks out
bd(21.5, BIG(21.5, 960, 440, "it checks out", c="green", d=0.1, s=110), [e for q in range(3) for e in check(21.5, 600 + 360 * q, 720, d=0.3 + 0.15 * q)], glint(21.5, 1600, 760, 0.5)[0])
# 22 whole neighborhood
bd(22, spot(22, 960, 700, 600, 0.0), town(22, 500, 700, 10, 0.1), glint(22, 960, 220, 0.5)[0], beam(22, 960, 280, 960, 650, 560, d=0.2))
# 22.5 not one backyard
hs = icon(22.5, "building", 960, 560, 200, 0.0, mv="bob")
bd(22.5, hs, spot(22.5, 960, 700, 140, 0.2), cross(22.5, 960, 420, d=0.5), T(22.5, 960, 880, 56, "not just your backyard", c="ink", d=0.4))
# 23 twist two
bd(23, BIG(23, 960, 160, "TWIST 2", c="red", d=0.1, s=90), icon(23, "lens", 700, 520, 240, 0.2, mv="spin"), icon(23, "eye", 1250, 520, 200, 0.3, mv="bob"),
   T(23, 960, 820, 64, "how bright?", c="gold", d=0.4))
# 23.5 spread the light
jm = uid("jm")
bd(23.5, [P(23.5, "M500,600 Q700,500 900,600 Q1100,700 1300,600 Q1400,550 1450,600", c="gold", w=26, idp=jm), pop(23.5, jm, 0.0),
          {"t": "move", "at": 23.5, "kind": "grow", "targets": [jm], "axis": "x", "from": 0.3, "to": 1.0, "pivot": [960, 600], "dur": 1.2, "delay": 0.2}],
   T(23.5, 960, 820, 60, "spread it thin", c="ink", d=0.3), sun(23.5, 300, 250, 130, 0.1))
# 24 300 m2 mirror
bd(24, glint(24, 600, 520, 1.2)[0], BIG(24, 1300, 450, "~300 m²", c="blue", d=0.2, s=140), T(24, 1300, 650, 52, "18 m × 18 m", c="muted", d=0.4))
# 24.5 20 million
sp = spot(24.5, 960, 640, 600, 0.0)
bd(24.5, sp, BIG(24.5, 960, 340, "~20,000,000 m²", c="red", d=0.2, s=110), glint(24.5, 960, 640, 0.15, d=0.5)[0], T(24.5, 960, 900, 48, "(Glint is the speck)", c="muted", d=0.6))
# 25 thinned out
bd(25, bar(25, 500, 860, 160, 500, "gold", d=0.1), T(25, 580, 940, 44, "sunlight"), bar(25, 1200, 860, 160, 10, "gold", d=0.4), T(25, 1280, 940, 44, "in the spot"),
   arr(25, 720, 400, 1150, 800, c="red", d=0.3), sun(25, 1600, 300, 120, 0.2))
# 25.5 tens of thousands
bd(25.5, BIG(25.5, 960, 420, "÷ 60,000", c="red", d=0.1, s=160), T(25.5, 960, 640, 52, "(our estimate)", c="muted", d=0.3), glint(25.5, 960, 820, 0.5, mood="sad")[0])
# 26 our rough math overhead
g_, gi = glint(26, 960, 220, 0.5)
bd(26, g_, beam(26, 960, 270, 960, 760, 200, d=0.2), person(26, 960, 760, 0.5)[0], earth(26, 830, night=True), T(26, 1450, 400, 52, "straight overhead", c="ink", d=0.4))
# 26.5 a lux or two
bd(26.5, BIG(26.5, 960, 420, "≈ 1–2 lux", c="gold", d=0.1, s=160), icon(26.5, "lens", 500, 760, 140, 0.2, mv="spin"), T(26.5, 1300, 760, 52, "at most", c="red", d=0.4))
# 27 farther at a slant
g_, gi = glint(27, 1600, 220, 0.5)
bd(27, g_, beam(27, 1600, 270, 600, 780, 300, d=0.2), earth(27, 840, night=True), person(27, 600, 760, 0.4)[0], arr(27, 1500, 400, 800, 700, c="ink", d=0.4))
# 27.5 even dimmer
bd(27.5, bar(27.5, 600, 860, 160, 400, "gold", d=0.0), bar(27.5, 1100, 860, 160, 160, "gold", d=0.3), arr(27.5, 800, 500, 1080, 700, c="red", d=0.4),
   T(27.5, 960, 260, 64, "dimmer still", c="muted", d=0.5))
# 28 like a full moon
bd(28, moonish(28, 600, 480, 300, 0.0), BIG(28, 1000, 480, "≈", c="ink", d=0.2, s=150), glint(28, 1400, 480, 1.0, d=0.3)[0], T(28, 960, 860, 52, "reports: like a full moon", c="ink", d=0.4))
# 28.5 up to 4x
E = []
for q in range(4):
    E += moonish(28.5, 500 + 300 * q, 500, 180, 0.1 + 0.12 * q)
bd(28.5, E, T(28.5, 960, 820, 56, "one astronomer: up to 4×", c="red", d=0.4))
# 29 read a map
mp = uid("mp")
bd(29, [R(29, 760, 400, 400, 300, c="ink", fill="muted", idp=mp), P(29, "M800,450 Q900,550 1000,480 Q1060,700 1120,600", c="red", w=6, idp=mp), pop(29, mp, 0.0), wig(29, mp, (960, 700), 5, 1.2)],
   check(29, 1350, 500, d=0.4), moonish(29, 400, 300, 120, 0.2), T(29, 960, 850, 56, "map: readable", c="green", d=0.3))
# 29.5 not a tan
ps, pp = person(29.5, 960, 600, 1.0)
bd(29.5, ps, icon(29.5, "sun", 1450, 300, 120, 0.2, c="muted", mv="spin"), cross(29.5, 1450, 300, d=0.5), T(29.5, 960, 900, 56, "tan: no", c="red", d=0.4), zz(29.5, 1100, 400, 0.3))
# 30 twist three
bd(30, BIG(30, 960, 160, "TWIST 3", c="red", d=0.1, s=90), sun(30, 960, 520, 300, 0.2), T(30, 960, 860, 60, "the big one", c="red", d=0.4))
# 30.5 how much mirror
bd(30.5, glint(30.5, 600, 500, 1.0, mood="o")[0], icon(30.5, "question", 1300, 450, 240, 0.2, c="red", mv="wig"), T(30.5, 960, 860, 60, "how much mirror for daylight?", c="ink", d=0.4))
# 31 100,000 lux
bd(31, BIG(31, 960, 400, "100,000 lux", c="gold", d=0.1, s=150), sun(31, 1600, 760, 160, 0.2), bar(31, 400, 900, 120, 300, "gold", d=0.3))
# 31.5 hundreds of thousands of full moons
E = []
for q in range(14):
    E += moonish(31.5, 260 + 115 * q, 360 + 120 * (q % 4), 90, 0.05 * q)
bd(31.5, E, T(31.5, 960, 900, 56, "hundreds of thousands of full moons", c="ink", d=0.5))
# 32 beautiful answer
bd(32, T(32, 960, 300, 64, "brightness in the spot =", c="ink", d=0.1), BIG(32, 960, 520, "sun × mirror ÷ spot", c="red", d=0.3, s=100), glint(32, 960, 800, 0.5)[0])
# 32.5 as big as the spot
bd(32.5, spot(32.5, 960, 740, 500, 0.0), [P(32.5, "M460,300 L1460,300 L1460,420 L460,420 Z", c="ink", w=6, fill="blue", idp=(bm_ := uid("bm"))), pop(32.5, bm_, 0.3), bob(32.5, bm_, 6, 1.0)],
   T(32.5, 960, 560, 60, "mirror = spot", c="red", d=0.5), sun(32.5, 200, 200, 120, 0.1))
# 33 5-km town like noon
s_ = sun(33, 960, 200, 180, 0.0)
bd(33, s_, spot(33, 960, 700, 500, 0.2), town(33, 600, 700, 8, 0.3), T(33, 960, 940, 52, "a 5-km town at noon", c="ink", d=0.4))
# 33.5 5-km mirror
bm = uid("bm")
bd(33.5, [R(33.5, 300, 250, 1320, 160, c="ink", fill="blue", idp=bm), pop(33.5, bm, 0.0), wig(33.5, bm, (960, 330), 2, 0.8)], BIG(33.5, 960, 580, "5-km mirror", c="red", d=0.3, s=130),
   glint(33.5, 1600, 760, 0.4, mood="o")[0], town(33.5, 300, 860, 4, 0.4))
# 34 all 50,000 combined
E = []
for q in range(16):
    i = uid("mm")
    E += [R(34, 300 + 80 * q, 320, 60, 60, c="ink", fill="blue", idp=i), pop(34, i, 0.04 * q), sh(34, i, 680 - 80 * q, 120, 0.8, 0.8)]
bd(34, E, T(34, 960, 260, 56, "all 50,000 together", c="ink", d=0.2), BIG(34, 960, 760, "~16 km²", c="blue", d=0.9, s=130))
# 34.5 not even one town
bd(34.5, spot(34.5, 960, 700, 500, 0.0), [R(34.5, 760, 600, 400, 200, c="ink", fill="blue", idp=(sq := uid("sq"))), pop(34.5, sq, 0.3), pulse(34.5, sq, 0.8)],
   T(34.5, 960, 340, 56, "one 5-km spot: ~20 km²", c="red", d=0.5), cross(34.5, 1500, 700, d=0.7))
# 35 not enough
bd(35, BIG(35, 960, 440, "not even ONE noon", c="red", d=0.1, s=110), glint(35, 960, 780, 0.7, mood="sad")[0], town(35, 1350, 860, 3, 0.4))
# 35.5 town at noon nope
bd(35.5, sun(35.5, 600, 400, 200, 0.0), cross(35.5, 600, 400, d=0.4), moonish(35.5, 1300, 400, 200, 0.2), check(35.5, 1300, 640, d=0.6), T(35.5, 960, 860, 56, "moonlight, not noon", c="ink", d=0.5))
# 36 what's it for
bd(36, glint(36, 960, 480, 1.2)[0], icon(36, "question", 1500, 400, 200, 0.2, c="red", mv="wig"), T(36, 960, 860, 60, "so what's it for?", c="ink", d=0.3))
# 36.5 solar farms rescue construction
bd(36.5, icon(36.5, "battery", 400, 500, 200, 0.0, c="green", mv="wig"), icon(36.5, "map_pin", 960, 500, 200, 0.2, c="red", mv="bob"), icon(36.5, "building", 1500, 500, 200, 0.4, mv="bob"),
   T(36.5, 400, 720, 44, "solar farms", c="green", d=0.1), T(36.5, 960, 720, 44, "rescue", c="red", d=0.3), T(36.5, 1500, 720, 44, "construction", c="ink", d=0.5))
# 37 astronomers worried
bd(37, icon(37, "lens", 700, 500, 260, 0.0, mv="wig"), person(37, 1200, 600, 1.0)[0], T(37, 960, 860, 60, "astronomers: uh-oh", c="red", d=0.3),
   [e for q in range(3) for e in star(37, 1450 + 100 * q, 300, 0.2 + 0.1 * q, r=24)])
# 37.5 ruin a telescope image
ph = uid("ph")
bd(37.5, [R(37.5, 560, 300, 800, 500, c="ink", fill="ink", idp=ph), pop(37.5, ph, 0.0), wig(37.5, ph, (960, 800), 2, 1.0)],
   [e for q in range(6) for e in star(37.5, 640 + 120 * q, 380 + 70 * (q % 3), 0.1, c="gold", r=16)],
   [P(37.5, "M520,700 L1400,340", c="gold", w=24, idp=(st_ := uid("st"))), pop(37.5, st_, 0.6), pulse(37.5, st_, 0.9)], T(37.5, 960, 900, 52, "streak!", c="red", d=0.7))
# 38 animals rely on the dark
ow = uid("ow")
bd(38, [O(38, 700, 520, 120, c="ink", fill="muted", idp=ow), O(38, 650, 490, 30, c="ink", fill="gold", idp=ow), O(38, 750, 490, 30, c="ink", fill="gold", idp=ow),
        P(38, "M690,540 L710,540 L700,560 Z", c="ink", w=4, fill="gold", idp=ow), pop(38, ow, 0.0), bob(38, ow, 6, 1.0), wig(38, ow, (700, 640), 8, 1.4)],
   moonish(38, 1350, 300, 160, 0.2), T(38, 1200, 700, 56, "animals need the dark", c="ink", d=0.4))
# 38.5 sleep hunt migrate
E = []
for q in range(5):
    i = uid("bd")
    E += [P(38.5, f"M{300 + 120 * q},{600 - 40 * q} q30,-30 60,0 q30,-30 60,0", c="ink", w=5, idp=i), pop(38.5, i, 0.1 * q), sh(38.5, i, 700, -200, 0.3 + 0.1 * q, 2.0)]
bd(38.5, E, zz(38.5, 1400, 700, 0.2), T(38.5, 960, 900, 52, "sleep · hunt · migrate", c="ink", d=0.4))
# 39 fine print dusk and dawn
bd(39, T(39, 960, 180, 60, "friendly fine print", c="ink", d=0.1), icon(39, "sunrise", 600, 520, 260, 0.2, c="gold", mv="bob"), icon(39, "sunrise", 1320, 520, 260, 0.3, c="red", mv="bob"),
   T(39, 600, 780, 48, "dawn", c="gold", d=0.4), T(39, 1320, 780, 48, "dusk", c="red", d=0.5))
# 39.5 mirror still in sunlight
g_, gi = glint(39.5, 1200, 300, 0.6)
bd(39.5, g_, sun(39.5, 300, 300, 140, 0.0), ray(39.5, 400, 300, 1050, 300, d=0.2), earth(39.5, 860, night=True), check(39.5, 1500, 300, d=0.6))
# 40 our rough math by midnight
bd(40, icon(40, "clock", 960, 480, 300, 0.0, mv="spin"), BIG(40, 960, 820, "midnight", c="blue", d=0.2, s=110), T(40, 960, 200, 52, "our rough math", c="muted", d=0.3))
# 40.5 Glint in Earth's shadow
g_, gi = glint(40.5, 1500, 300, 0.5, mood="sad")
e2 = uid("e")
bd(40.5, [O(40.5, 760, 560, 240, c="blue", fill="blue", idp=e2), spin(40.5, e2, (760, 560), 6),
          P(40.5, "M760,320 L1850,280 L1850,840 L760,800 Z", c="ink", w=3, fill="ink", idp=(s2 := uid("sd")), opacity=60), pop(40.5, s2, 0.0)],
   g_, [sh(40.5, gi, 0, 200, 0.3, 1.0)], sun(40.5, 200, 560, 120, 0.1), T(40.5, 1500, 940, 48, "lights out", c="ink", d=0.6))
# 41 7-8 km per second
g_, gi = glint(41, 300, 300, 0.5)
bd(41, g_, [sh(41, gi, 1300, 0, 0.1, 1.2)], BIG(41, 960, 600, "~7.5 km/s", c="red", d=0.2, s=150), earth(41, 860),
   [e for q in range(3) for e in icon(41, "wind", 500 + 300 * q, 300, 100, 0.3 + 0.1 * q, c="blue", mv="wig")])
# 41.5 minutes
g_, gi = glint(41.5, 500, 260, 0.5)
bd(41.5, g_, [sh(41.5, gi, 900, 0, 0.2, 2.2), rot(41.5, gi, -40, (500, 260), 0.2, 2.2)], icon(41.5, "clock", 960, 640, 200, 0.1, mv="spin"),
   BIG(41.5, 1500, 640, "minutes", c="red", d=0.4, s=100), earth(41.5, 900))
# 42 just a test
bd(42, icon(42, "flask", 700, 500, 260, 0.0, mv="wig"), glint(42, 1300, 480, 1.0, d=0.2)[0], T(42, 960, 860, 60, "first mirror = a test", c="blue", d=0.4))
# 42.5 share the night sky
bd(42.5, earth(42.5, 860, night=True), [e for q in range(6) for e in star(42.5, 300 + 260 * q, 300 + 90 * (q % 3), 0.1 * q, r=24)],
   icon(42.5, "question", 960, 500, 180, 0.3, c="red", mv="wig"), T(42.5, 960, 700, 56, "share the night?", c="ink", d=0.5))
# 43 dream lives on
g_, gi = glint(43, 960, 480, 1.6)
bd(43, g_, [e for q in range(4) for e in star(43, 400 + 370 * q, 860, 0.3 + 0.1 * q, r=34)], T(43, 960, 150, 56, "Glint's dream", c="ink", d=0.3))
# 43.5 sunlight on demand
bd(43.5, BIG(43.5, 960, 380, "sunlight on demand", c="gold", d=0.1, s=110), icon(43.5, "phone", 600, 700, 200, 0.2, mv="wig"), sun(43.5, 1300, 700, 180, 0.4))
# 44 just not at midnight
bd(44, icon(44, "clock", 600, 480, 260, 0.0, mv="spin"), cross(44, 600, 480, d=0.4), glint(44, 1300, 480, 1.0, mood="sad")[0], BIG(44, 960, 850, "not at midnight", c="blue", d=0.3, s=100))
# 44.5 never as bright as noon
bd(44.5, sun(44.5, 600, 420, 260, 0.0), BIG(44.5, 1000, 420, ">", c="red", d=0.2, s=160), moonish(44.5, 1350, 420, 200, 0.3), glint(44.5, 1650, 780, 0.5, d=0.5)[0],
   T(44.5, 960, 860, 56, "noon still wins", c="gold", d=0.6))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"FCC": "F C C", "Earendil-1": "Air in deal one", "2035": "twenty thirty five", "Skyroot": "Sky-root"})
