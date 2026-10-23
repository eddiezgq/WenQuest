"""Daily science short 2026-10-23 (English): "Don't Jump on This Moon"
News: Japan's MMX (Martian Moons eXploration) launched on an H3 rocket from Tanegashima on Oct 19, 2026 (Live Science top story
"Japan launches world's first round-trip mission to Mars", 22 Oct; Space.com "Japan launches historic MMX sample-return mission to
Mars' moon Phobos"; ESA "Mars moon lander set to launch on 19 October").
Facts (Space.com): arrives Aug 2027 in a quasi-satellite orbit (QSO) around Phobos; ~3 years in the Mars system; two touchdowns;
~10 g of sample; NASA pneumatic sampler (puff of gas); leaves Nov 2030, capsule lands in Australia 2031; Phobos ~22 km across;
origin: captured asteroid vs giant-impact debris; IDEFIX rover (France-Germany).
Textbook (NASA fact sheets): Phobos orbits ~6,000 km above Mars; surface gravity ~0.0057 m/s² (~1/1,700 g); escape speed ~11 m/s
(~25 mph); spirals inward ~2 cm/yr (1.8 m per century); expected to break up or hit Mars in ~30-50 million years; Phobos sits
deep in Mars' gravity, its Hill sphere barely clears its surface, so ordinary orbits around it are not stable -> QSO.
Our estimates (said as estimates): 60 kg on Earth -> ~35 g on Phobos; a 3 m/s jump -> ~1 km up, ~17 min in the air
(t = 2v/g = 6/0.0057 ≈ 1,050 s). "Might hold bits of Mars" is said as a possibility. Character: Pho, a potato moon. Gag: do not jump.
    python3 make.py <kokoro model dir> | --boards-only | --fake   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import math
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("日本刚刚发射了一艘飞船，|要去火星的一颗月亮上挖土。", "Japan just launched a spacecraft | to go dig up dirt on a moon of Mars."),
 ("然后把土带回地球。|史上第一次。", "And bring it back to Earth. | A first, ever."),
 ("可这颗月亮有一条规矩：|千万别跳。", "But this moon has one rule: | do not jump."),
 ("今天的问题：怎么降落在一颗|跳一下就可能飞走的月亮上？", "Today's question: how do you land on a moon | where one hop could send you flying?"),
 ("认识一下小福。|火卫一，福波斯，火星更大的那颗月亮。", "Meet Pho. | Phobos, the bigger moon of Mars."),
 ("它不是圆的，|像一个坑坑洼洼的土豆。", "It's not round. | It's a lumpy, cratered potato."),
 ("宽大约22公里，|开车二十分钟就横穿过去了。", "About 22 kilometers across. | You could drive across it in twenty minutes."),
 ("10月19日，日本的H3火箭|从种子岛升空。", "On October 19th, Japan's H3 rocket | lifted off from Tanegashima."),
 ("任务叫MMX，|火星卫星探测。", "The mission is called MMX, | Martian Moons eXploration."),
 ("明年8月到火星，|在那边待大约三年。", "It reaches Mars next August | and stays about three years."),
 ("反转一：小福太轻了，|引力只有地球的大约一千七百分之一。", "Twist one: Pho is so light, | its gravity is about one seventeen-hundredth of Earth's."),
 ("在地球上60公斤？|在小福上大约只有35克，一片面包那么重。", "Weigh 60 kilos on Earth? | On Pho you'd weigh about 35 grams. A slice of bread."),
 ("逃逸速度大约每秒11米，|也就是时速40公里左右。", "Its escape speed is about 11 meters per second, | roughly 25 miles an hour."),
 ("一个棒球投手，|能把球直接扔出这颗月亮。", "A baseball pitcher | could throw a ball right off this moon."),
 ("那跳一下会怎样？我们粗算一下：|普通人起跳大约每秒3米。", "So what about a jump? Our rough math: | a normal jump launches you at about 3 meters per second."),
 ("你会飘到快一公里高，|十几分钟以后才落回来。", "You'd float almost a kilometer up | and land more than fifteen minutes later."),
 ("够你在半空中|做一个三明治。", "Long enough to make a sandwich | in midair."),
 ("反转二：小福这么轻，|飞船连正常地绕着它转都做不到。", "Twist two: Pho is so light, | a spacecraft can't even orbit it the normal way."),
 ("小福离火星太近了，|火星的引力会把飞船拽走。", "Pho is so close to Mars | that Mars' gravity drags the spacecraft away."),
 ("所以MMX耍了个花招：|准卫星轨道。", "So MMX uses a trick: | a quasi-satellite orbit."),
 ("飞船其实是在绕火星转，|只是一直跟在小福身边。", "The spacecraft actually orbits Mars, | sticking right next to Pho."),
 ("从小福看过去，飞船好像在绕着自己转圈。|就像跑道上两个并排跑、来回交错的人。", "Seen from Pho, it seems to circle around it. | Like two runners on a track, weaving side by side."),
 ("然后它会降落两次，|用一股气把土吹进罐子里。", "Then it touches down twice | and uses a puff of gas to blow dirt into a canister."),
 ("目标：大约10克土。|差不多一勺。", "The goal: about 10 grams of dirt. | Roughly a tablespoon."),
 ("2031年，|这一勺土会落在澳大利亚。", "In 2031, | that tablespoon lands in Australia."),
 ("为什么这么费劲？|因为没人知道小福是从哪来的。", "Why all this trouble? | Because nobody knows where Pho came from."),
 ("一种说法：它是一颗小行星，|被火星抓住了。", "One idea: it's an asteroid | that Mars captured."),
 ("另一种说法：一次大撞击，|从火星身上撞下来一块。", "Another idea: a giant impact | knocked a chunk off Mars itself."),
 ("那一勺土可能会给出答案。|里面也许还有火星本身的碎渣。", "That tablespoon could settle it. | It might even hold bits of Mars."),
 ("反转三，最惨：|小福正在往下掉。", "Twist three, the sad part: | Pho is falling."),
 ("它离火星表面只有大约六千公里，|每年靠近大约两厘米。", "It orbits only about 6,000 kilometers above Mars, | and creeps about 2 centimeters closer every year."),
 ("几千万年以后，|它会被火星撕碎，或者直接撞上去。", "In tens of millions of years, | Mars will tear it apart, or it will crash."),
 ("友情提示：MMX不会跳。|它会用腿，轻轻地落下去。", "Friendly fine print: MMX won't jump. | It sets down gently, on its legs."),
 ("所以我们得趁早，|赶在小福掉下去之前，拿一勺土当纪念。", "So we'd better hurry | and grab a souvenir before Pho falls."),
 ("小福的规矩还是那一条：|千万别跳。", "And Pho's one rule still stands: | do not jump."),
]
TITLE = {"zh": "别在这颗月亮上跳", "en": "Don't Jump on This Moon"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 970, 0.5, r=16)
    B.append(E)


def pho(a, x, y, k=1.0, mood="happy", d=None):
    """Pho: a lumpy potato moon with craters and a face; bobs and wobbles."""
    i = uid("pho") + "_"
    E = [P(a, f"M{x - 150 * k},{y} Q{x - 160 * k},{y - 90 * k} {x - 40 * k},{y - 95 * k} Q{x + 80 * k},{y - 110 * k} {x + 150 * k},{y - 50 * k} "
              f"Q{x + 180 * k},{y + 40 * k} {x + 90 * k},{y + 85 * k} Q{x - 40 * k},{y + 110 * k} {x - 130 * k},{y + 70 * k} Q{x - 165 * k},{y + 40 * k} {x - 150 * k},{y} Z",
           c="ink", w=6, fill="muted", idp=i),
         O(a, x + 100 * k, y + 30 * k, 18 * k, c="ink", idp=i), O(a, x - 110 * k, y + 30 * k, 12 * k, c="ink", idp=i),
         O(a, x - 40 * k, y - 25 * k, 12 * k, c="ink", fill="ink", idp=i), O(a, x + 35 * k, y - 25 * k, 12 * k, c="ink", fill="ink", idp=i)]
    m = {"happy": f"M{x - 30 * k},{y + 20 * k} Q{x},{y + 50 * k} {x + 30 * k},{y + 20 * k}",
         "o": f"M{x - 13 * k},{y + 35 * k} a13,13 0 1,0 26,0 a13,13 0 1,0 -26,0",
         "sad": f"M{x - 30 * k},{y + 45 * k} Q{x},{y + 18 * k} {x + 30 * k},{y + 45 * k}"}[mood]
    E += [P(a, m, c="ink", w=5, idp=i), bob(a, i, 8 * k, 1.3), wig(a, i, (x, y + 90 * k), 4, 1.1)]
    if d is not None:
        E.append(pop(a, i + "*", d))
    return E, i


def mars(a, x, y, r=200, d=0.0):
    i = uid("mars")
    return [O(a, x, y, r, c="red", idp=i), P(a, f"M{x - r * .6},{y - r * .2} q{r * .3},{-r * .15} {r * .6},0 M{x + r * .1},{y + r * .35} q{r * .25},{r * .1} {r * .45},{-r * .05}",
                                            c="red", w=5, idp=i), pop(a, i, d), spin(a, i, (x, y), 8)]


def ship(a, x, y, k=1.0, d=0.0):
    i = uid("sh")
    E = [R(a, x - 50 * k, y - 40 * k, 100 * k, 80 * k, c="ink", fill="gold", idp=i),
         R(a, x - 170 * k, y - 20 * k, 110 * k, 40 * k, c="blue", fill="blue", idp=i), R(a, x + 60 * k, y - 20 * k, 110 * k, 40 * k, c="blue", fill="blue", idp=i),
         P(a, f"M{x - 35 * k},{y + 40 * k} L{x - 55 * k},{y + 80 * k} M{x + 35 * k},{y + 40 * k} L{x + 55 * k},{y + 80 * k}", c="ink", w=5, idp=i),
         pop(a, i, d), bob(a, i, 6 * k, 1.0)]
    return E, i


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def person(a, x, y, k=1.0, c="ink"):
    i = uid("ps")
    return [O(a, x, y - 130 * k, 40 * k, c=c, idp=i), P(a, f"M{x},{y - 90 * k} L{x},{y + 40 * k} M{x - 60 * k},{y - 30 * k} L{x},{y - 60 * k} L{x + 60 * k},{y - 30 * k} "
                                                         f"M{x},{y + 40 * k} L{x - 40 * k},{y + 130 * k} M{x},{y + 40 * k} L{x + 40 * k},{y + 130 * k}", c=c, w=6, idp=i),
            bob(a, i, 5, 1.0), wig(a, i, (x, y + 130 * k), 4, 1.2)], i


def ball(a, x, y, r=30, d=0.0, c="red"):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), spin(a, i, (x, y), 90)], i


def dirt(a, x, y, n=8, spread=200, d=0.0, c="muted"):
    E = []
    for q in range(n):
        i = uid("dt")
        E += [O(a, x + ((q * 137) % spread) - spread / 2, y + ((q * 89) % (spread * .5)) - spread * .25, 8 + q % 3 * 4, c=c, fill=c, idp=i), pop(a, i, d + 0.04 * q),
              bob(a, i, 5, 0.8 + 0.1 * (q % 5))]
    return E


def orbit(a, cx, cy, rx, ry, c="muted", d=0.0, rpm=6):
    i = uid("orb")
    return [P(a, f"M{cx - rx},{cy} A{rx},{ry} 0 1,0 {cx + rx},{cy} A{rx},{ry} 0 1,0 {cx - rx},{cy}", c=c, w=4, idp=i), pop(a, i, d), spin(a, i, (cx, cy), rpm)]


def ground(a, y=880, c="muted"):
    i = uid("gr")
    return [P(a, f"M150,{y} Q560,{y - 40} 960,{y} Q1360,{y + 40} 1770,{y}", c=c, w=6, idp=i), bob(a, i, 2, 0.5)]


def spoon(a, x, y, k=1.0, d=0.0):
    i = uid("sp")
    return [P(a, f"M{x - 120 * k},{y} Q{x - 120 * k},{y + 70 * k} {x - 40 * k},{y + 70 * k} Q{x + 40 * k},{y + 70 * k} {x + 40 * k},{y} Z M{x + 40 * k},{y + 20 * k} L{x + 260 * k},{y - 40 * k}",
              c="ink", w=6, idp=i), pop(a, i, d), wig(a, i, (x + 260 * k, y - 40 * k), 5, 1.0)], i


def puff(a):
    E = []
    for q in range(6):
        gi = uid("g")
        E += [O(a, 760 + 30 * q, 700 - 10 * q, 14, c="muted", fill="muted", idp=gi), sh(a, gi, 480 - 30 * q, -150 + 10 * q, 0.2 + 0.12 * q, 0.6)]
    return E


def redbits(a):
    E = []
    for q in range(4):
        ri = uid("rm")
        E += [O(a, 800 + 70 * q, 520 + 30 * (q % 2), 16, c="red", fill="red", idp=ri), pop(a, ri, 0.3 + 0.1 * q), pulse(a, ri, 0.8)]
    return E


# 0 Japan launched a spacecraft
r_ = icon(0, "rocket", 700, 560, 300, 0.0, c="red", mv="wig")
bd(0, r_, [sh(0, r_[0]["id"], 300, -380, 0.4, 1.4)], mars(0, 1500, 300, 140, 0.2), [e for q in range(4) for e in star(0, 300 + 120 * q, 850 - 40 * q, 0.2 + 0.1 * q, c="red", r=24)])
# 0.5 dig dirt on a moon of Mars
p_, pi = pho(0.5, 1200, 520, 1.6, d=0.0)
s_, si = ship(0.5, 500, 300, 0.8, 0.1)
bd(0.5, p_, s_, [sh(0.5, si, 500, 140, 0.3, 1.0)], dirt(0.5, 1200, 380, 6, 200, 0.8), mars(0.5, 300, 850, 120, 0.2))
# 1 bring it back to Earth
i = uid("ear")
bd(1, icon(1, "globe", 1500, 520, 260, 0.0, c="blue", mv="spin"), mars(1, 380, 520, 150, 0.1), arr(1, 600, 520, 1300, 520, c="green", d=0.2, dur=0.8),
   dirt(1, 950, 440, 6, 160, 0.4, c="ink"), T(1, 960, 820, 60, "bring it home", c="green", d=0.3))
# 1.5 a first ever
bd(1.5, BIG(1.5, 960, 450, "FIRST EVER", c="red", d=0.1, s=160), [e for q in range(5) for e in star(1.5, 400 + 280 * q, 760, 0.2 + 0.1 * q, r=40)], pho(1.5, 960, 860, 0.5)[0])
# 2 one rule
p_, pi = pho(2, 700, 560, 1.8)
bd(2, p_, T(2, 1400, 400, 60, "one rule:", c="ink", d=0.2), icon(2, "question", 1450, 650, 180, 0.4, c="red", mv="wig"))
# 2.5 do not jump
ps, pp = person(2.5, 960, 600, 1.2)
bd(2.5, ps, [sh(2.5, pp, 0, -60, 0.3, 0.3), sh(2.5, pp, 0, 60, 0.7, 0.3)], cross(2.5, 960, 470, d=0.5), BIG(2.5, 960, 940, "DO NOT JUMP", c="red", d=0.2, s=110), ground(2.5, 760))
# 3 how do you land
s_, si = ship(3, 960, 250, 1.2, 0.0)
bd(3, s_, [sh(3, si, 0, 300, 0.3, 1.5)], pho(3, 960, 820, 1.4)[0], icon(3, "question", 1550, 400, 200, 0.4, c="red", mv="wig"))
# 3.5 one hop sends you flying
ps, pp = person(3.5, 700, 760, 0.9)
bd(3.5, ps, [sh(3.5, pp, 700, -500, 0.3, 1.6), rot(3.5, pp, 360, (700, 760), 0.3, 1.6)], ground(3.5, 900), arr(3.5, 760, 600, 1300, 300, c="red", d=0.2),
   T(3.5, 1450, 760, 60, "byeeee!", c="red", d=0.7))
# 4 meet Pho
p_, pi = pho(4, 860, 560, 2.4, d=0.0)
bd(4, p_, BIG(4, 1560, 360, "Pho", c="blue", d=0.4, s=160), [e for q in range(3) for e in star(4, 1450 + 110 * q, 600, 0.6 + 0.1 * q, r=30)])
# 4.5 Phobos bigger moon of Mars
p_, pi = pho(4.5, 1350, 400, 0.8)
bd(4.5, mars(4.5, 650, 560, 260, 0.0), p_, orbit(4.5, 650, 560, 700, 260, d=0.1), [rot(4.5, pi + "*", 25, (650, 560), 0.3, 2.0)],
   T(4.5, 1350, 860, 60, "Phobos", c="red", d=0.4), icon(4.5, "moon", 1700, 760, 90, 0.5, c="gold"))
# 5 not round
c_ = uid("rd")
bd(5, [O(5, 600, 520, 200, c="ink", idp=c_), pop(5, c_, 0.0), bob(5, c_, 6, 1.0)], cross(5, 600, 520, d=0.4), pho(5, 1350, 520, 1.3, mood="o", d=0.6)[0],
   T(5, 600, 860, 52, "round?", c="muted", d=0.2))
# 5.5 lumpy potato
pt = uid("pt")
bd(5.5, pho(5.5, 650, 540, 1.5)[0], [P(5.5, "M1250,540 Q1220,400 1400,390 Q1600,380 1620,520 Q1640,660 1450,680 Q1270,690 1250,540 Z", c="gold", w=6, fill="gold", idp=pt),
                                    pop(5.5, pt, 0.3), wig(5.5, pt, (1430, 680), 6, 1.4)], T(5.5, 1430, 860, 60, "potato", c="gold", d=0.4), BIG(5.5, 1000, 520, "=", c="ink", d=0.5, s=120))
# 6 22 km across
bd(6, pho(6, 960, 600, 2.0)[0], arr(6, 640, 860, 1280, 860, c="blue", d=0.2), arr(6, 1280, 860, 640, 860, c="blue", d=0.2), BIG(6, 960, 240, "22 km", c="blue", d=0.1, s=150))
# 6.5 drive across in twenty minutes
cr = icon(6.5, "car", 400, 560, 220, 0.0, mv="wig")
bd(6.5, cr, [sh(6.5, cr[0]["id"], 1100, 0, 0.2, 2.0)], ground(6.5, 700), icon(6.5, "clock", 960, 300, 180, 0.2, mv="spin"), BIG(6.5, 960, 880, "20 min", c="red", d=0.4, s=110))
# 7 Oct 19 H3
r_ = icon(7, "rocket", 960, 700, 320, 0.0, c="red", mv="wig")
bd(7, r_, [sh(7, r_[0]["id"], 0, -500, 0.6, 1.4)], BIG(7, 450, 400, "Oct 19", c="blue", d=0.1, s=110), BIG(7, 1480, 400, "H3", c="red", d=0.3, s=150),
   dirt(7, 960, 900, 8, 400, 0.5, c="muted"))
# 7.5 Tanegashima
isl = uid("isl")
r_ = icon(7.5, "rocket", 960, 420, 140, 0.2, c="red", mv="wig")
bd(7.5, [P(7.5, "M700,700 Q800,560 980,600 Q1200,640 1250,720 Q1100,800 900,790 Q720,780 700,700 Z", c="green", w=6, fill="green", idp=isl), pop(7.5, isl, 0.0), bob(7.5, isl, 3, 0.7)],
   r_, [sh(7.5, r_[0]["id"], 300, -300, 0.5, 1.2)], T(7.5, 960, 920, 60, "Tanegashima, Japan", c="ink", d=0.3), icon(7.5, "map_pin", 960, 640, 100, 0.4, c="red"))
# 8 MMX
s_, si = ship(8, 960, 600, 1.8, 0.0)
bd(8, s_, [rot(8, si, 15, (960, 600), 0.3, 0.8)], BIG(8, 960, 250, "MMX", c="red", d=0.2, s=170), icon(8, "satellite", 1600, 700, 160, 0.4, mv="spin"))
# 8.5 Martian Moons eXploration
bd(8.5, mars(8.5, 960, 480, 180, 0.0), pho(8.5, 1400, 330, 0.4, d=0.2)[0], icon(8.5, "moon", 550, 650, 90, 0.3, c="muted", mv="spin"),
   T(8.5, 960, 860, 64, "Martian Moons eXploration", c="ink", d=0.3))
# 9 next August
s_, si = ship(9, 300, 300, 0.7, 0.0)
bd(9, s_, [sh(9, si, 1050, 150, 0.2, 1.8)], mars(9, 1500, 520, 200, 0.1), BIG(9, 700, 780, "Aug 2027", c="blue", d=0.3, s=120))
# 9.5 three years
bd(9.5, mars(9.5, 760, 520, 200, 0.0), orbit(9.5, 760, 520, 360, 160, c="blue", d=0.1, rpm=20), ship(9.5, 1120, 520, 0.5, 0.2)[0],
   BIG(9.5, 1500, 400, "~3 years", c="red", d=0.3, s=110), icon(9.5, "clock", 1500, 720, 150, 0.4, mv="spin"))
# 10 twist one so light
p_, pi = pho(10, 700, 600, 1.4, mood="o")
bd(10, BIG(10, 960, 160, "TWIST 1", c="red", d=0.1, s=90), p_, [e for q in range(3) for e in icon(10, "wind", 1250 + 200 * q, 450 + 120 * (q % 2), 120, 0.3 + 0.1 * q, c="blue", mv="wig")],
   T(10, 1400, 820, 60, "featherweight", c="blue", d=0.5))
# 10.5 1/1700 gravity
bd(10.5, BIG(10.5, 960, 420, "1/1,700 g", c="red", d=0.1, s=160), bar(10.5, 500, 900, 140, 260, "blue", d=0.3), T(10.5, 570, 950, 44, "Earth", c="blue"),
   bar(10.5, 1300, 900, 140, 10, "red", d=0.5), T(10.5, 1370, 950, 44, "Pho", c="red"), pho(10.5, 1600, 760, 0.4)[0])
# 11 60 kilos on Earth
ps, pp = person(11, 700, 580, 1.2)
sc = uid("sc")
bd(11, ps, [R(11, 560, 760, 280, 60, c="ink", fill="muted", idp=sc), pop(11, sc, 0.1), wig(11, sc, (700, 820), 3, 2.0)], BIG(11, 1350, 480, "60 kg", c="blue", d=0.3, s=150),
   icon(11, "globe", 1350, 780, 140, 0.4, c="blue", mv="spin"))
# 11.5 35 grams a slice of bread
br = uid("br")
bd(11.5, BIG(11.5, 700, 420, "≈ 35 g", c="red", d=0.1, s=160), [P(11.5, "M1250,700 L1250,480 Q1250,380 1400,380 Q1550,380 1550,480 L1550,700 Z", c="gold", w=7, fill="gold", idp=br),
                                                               pop(11.5, br, 0.3), bob(11.5, br, 10, 1.0), rot(11.5, br, 20, (1400, 540), 0.6, 0.8)],
   T(11.5, 1400, 820, 52, "one slice of bread", c="ink", d=0.5), pho(11.5, 500, 820, 0.5)[0])
# 12 escape 11 m/s
b_, bi = ball(12, 700, 760, 40, 0.2)
bd(12, pho(12, 700, 900, 0.9)[0], b_, [sh(12, bi, 900, -600, 0.4, 1.4)], BIG(12, 1300, 380, "11 m/s", c="red", d=0.1, s=160), T(12, 1300, 560, 48, "escape speed", c="ink", d=0.3))
# 12.5 25 mph
cr = icon(12.5, "car", 500, 560, 220, 0.0, mv="wig")
bd(12.5, cr, [sh(12.5, cr[0]["id"], 300, 0, 0.3, 1.0)], BIG(12.5, 1300, 500, "25 mph", c="red", d=0.2, s=160), T(12.5, 1300, 700, 52, "school-zone speed", c="ink", d=0.5), ground(12.5, 700))
# 13 baseball pitcher
ps, pp = person(13, 500, 600, 1.2)
arm = uid("arm")
bd(13, ps, [P(13, "M500,520 L640,420", c="ink", w=8, idp=arm), rot(13, arm, -120, (500, 520), 0.2, 0.5), rot(13, arm, 120, (500, 520), 0.8, 0.3)],
   ball(13, 640, 420, 26, 0.0)[0], icon(13, "clock", 1400, 450, 150, 0.3, mv="spin"), T(13, 1400, 700, 52, "pro fastball: ~40 m/s", c="blue", d=0.4))
# 13.5 throw a ball off the moon
b_, bi = ball(13.5, 700, 620, 30, 0.0)
bd(13.5, pho(13.5, 600, 820, 1.2, mood="o")[0], b_, [sh(13.5, bi, 1050, -520, 0.2, 1.6)], arr(13.5, 760, 580, 1500, 200, c="red", d=0.2), T(13.5, 1400, 500, 60, "into space!", c="red", d=0.6))
# 14 what about a jump
ps, pp = person(14, 960, 640, 1.2)
bd(14, ps, [sh(14, pp, 0, -40, 0.3, 0.3), sh(14, pp, 0, 40, 0.6, 0.3)], ground(14, 820), icon(14, "question", 1450, 450, 200, 0.2, c="red", mv="wig"), T(14, 500, 400, 52, "our rough math", c="muted", d=0.4))
# 14.5 3 m/s
ps, pp = person(14.5, 600, 640, 1.0)
bd(14.5, ps, [sh(14.5, pp, 0, -200, 0.3, 0.6)], arr(14.5, 760, 700, 760, 350, c="red", d=0.2), BIG(14.5, 1300, 460, "3 m/s", c="red", d=0.3, s=160), ground(14.5, 800))
# 15 almost a kilometer up
ps, pp = person(15, 400, 760, 0.5)
bd(15, ps, [sh(15, pp, 0, -580, 0.2, 2.0)], pho(15, 400, 950, 0.8)[0], arr(15, 900, 900, 900, 160, c="blue", d=0.2, dur=1.0),
   BIG(15, 1350, 450, "~1 km", c="blue", d=0.4, s=160), icon(15, "building", 1350, 780, 160, 0.5, mv="bob"))
# 15.5 fifteen minutes
ps, pp = person(15.5, 500, 300, 0.6)
bd(15.5, ps, [sh(15.5, pp, 0, 450, 0.3, 2.5), rot(15.5, pp, 30, (500, 300), 0.3, 1.0)], icon(15.5, "clock", 1250, 450, 240, 0.0, mv="spin"),
   BIG(15.5, 1250, 800, "15+ min", c="red", d=0.4, s=120), ground(15.5, 900))
# 16 make a sandwich
sw = uid("sw")
bd(16, [P(16, "M700,460 L1000,460 L1000,520 L700,520 Z M700,540 Q850,580 1000,540 M700,560 L1000,560 L1000,620 L700,620 Z", c="gold", w=6, idp=sw), pop(16, sw, 0.1),
        bob(16, sw, 14, 0.9), rot(16, sw, 15, (850, 540), 0.4, 1.0)], person(16, 1350, 560, 0.9)[0], [e for q in range(3) for e in dirt(16, 850 + 0 * q, 300, 2, 200, 0.3 + 0.2 * q, c="green")],
   T(16, 960, 860, 60, "sandwich in midair", c="ink", d=0.5))
# 16.5 in midair
ps, pp = person(16.5, 960, 420, 1.0)
bd(16.5, ps, [rot(16.5, pp, 360, (960, 420), 0.2, 3.0)], ground(16.5, 900), [e for q in range(4) for e in icon(16.5, "cloud", 300 + 440 * q, 200 + 60 * (q % 2), 120, 0.1 * q, c="muted", mv="bob")],
   T(16.5, 960, 760, 56, "still... falling...", c="muted", d=0.5))
# 17 twist two
p_, pi = pho(17, 960, 560, 1.4)
bd(17, BIG(17, 960, 160, "TWIST 2", c="red", d=0.1, s=90), p_, orbit(17, 960, 560, 400, 200, c="blue", d=0.2, rpm=14), ship(17, 1360, 560, 0.4, 0.3)[0])
# 17.5 can't even orbit
s_, si = ship(17.5, 1300, 400, 0.6, 0.0)
bd(17.5, pho(17.5, 800, 560, 1.2, mood="sad")[0], s_, [sh(17.5, si, 450, -200, 0.3, 1.4), rot(17.5, si, 60, (1300, 400), 0.3, 1.4)], cross(17.5, 1100, 560, d=0.5),
   T(17.5, 800, 860, 56, "normal orbit? nope", c="red", d=0.4))
# 18 so close to Mars
bd(18, mars(18, 600, 560, 340, 0.0), pho(18, 1250, 560, 0.7)[0], arr(18, 1180, 760, 960, 760, c="ink", d=0.3), T(18, 1500, 860, 56, "so close", c="red", d=0.4), ship(18, 1550, 450, 0.4, 0.2)[0])
# 18.5 Mars drags spacecraft away
s_, si = ship(18.5, 1350, 400, 0.6, 0.0)
bd(18.5, mars(18.5, 500, 600, 300, 0.0), pho(18.5, 1500, 700, 0.7)[0], s_, [sh(18.5, si, -480, 120, 0.2, 1.4)], [e for q in range(3) for e in arr(18.5, 1200, 330 + 60 * q, 900, 430 + 60 * q, c="red", d=0.1 * q)])
# 19 trick
bd(19, BIG(19, 960, 300, "a trick!", c="blue", d=0.1, s=140), [e for q in range(3) for e in icon(19, "gear", 560 + 400 * q, 680, 160, 0.2 + 0.1 * q, mv="spin")], pho(19, 960, 900, 0.4)[0])
# 19.5 quasi-satellite orbit
p_, pi = pho(19.5, 960, 560, 0.8)
s_, si = ship(19.5, 960, 260, 0.5, 0.2)
bd(19.5, p_, orbit(19.5, 960, 560, 360, 300, c="green", d=0.1, rpm=10), s_, [rot(19.5, si, 360, (960, 560), 0.4, 2.5)], T(19.5, 960, 940, 64, "quasi-satellite orbit", c="green", d=0.3))
# 20 actually orbits Mars
s_, si = ship(20, 1500, 520, 0.4, 0.1)
p_, pi = pho(20, 1500, 680, 0.35)
bd(20, mars(20, 760, 560, 220, 0.0), orbit(20, 760, 560, 740, 320, d=0.1), s_, p_, [rot(20, [si], -40, (760, 560), 0.3, 2.0), rot(20, [pi + "*"], -40, (760, 560), 0.3, 2.0)])
# 20.5 right next to Pho
s_, si = ship(20.5, 1150, 520, 0.6, 0.0)
bd(20.5, pho(20.5, 700, 560, 1.4)[0], s_, [sh(20.5, si, 0, -80, 0.2, 0.6), sh(20.5, si, 0, 160, 0.9, 0.8)], T(20.5, 960, 880, 56, "buddies", c="blue", d=0.4),
   [e for q in range(2) for e in check(20.5, 1500 + 150 * q, 400, d=0.5 + 0.2 * q)])
# 21 seems to circle around it
s_, si = ship(21, 960, 260, 0.5, 0.0)
bd(21, pho(21, 960, 560, 1.0)[0], s_, [rot(21, si, 360, (960, 560), 0.2, 3.0)], orbit(21, 960, 560, 300, 300, c="green", d=0.1, rpm=-12), T(21, 960, 940, 52, "looks like it circles Pho", c="green", d=0.4))
# 21.5 two runners weaving
a_, ai = person(21.5, 400, 560, 0.8, c="blue")
b_, bi = person(21.5, 400, 760, 0.6, c="red")
trk = uid("trk")
bd(21.5, [P(21.5, "M150,460 L1770,460 M150,900 L1770,900", c="muted", w=5, idp=trk), bob(21.5, trk, 2, 0.5)], a_, b_, [sh(21.5, ai, 1100, 0, 0.1, 2.5), sh(21.5, bi, 1100, -200, 0.1, 1.2),
                                                                                                                     sh(21.5, bi, 0, 200, 1.3, 1.2)], T(21.5, 1500, 960, 48, "weaving side by side", c="ink", d=0.3))
# 22 touches down twice
s_, si = ship(22, 700, 250, 0.9, 0.0)
bd(22, s_, [sh(22, si, 0, 420, 0.2, 0.8), sh(22, si, 600, -300, 1.1, 0.6)], ground(22, 780), BIG(22, 1500, 650, "× 2", c="red", d=0.3, s=150), dirt(22, 700, 760, 6, 200, 0.8))
# 22.5 puff of gas into canister
can = uid("can")
bd(22.5, [R(22.5, 1200, 360, 220, 300, c="ink", idp=can), pop(22.5, can, 0.0), wig(22.5, can, (1310, 660), 3, 1.5)], icon(22.5, "wind", 600, 620, 200, 0.1, c="blue", mv="wig"),
   puff(22.5),
   ground(22.5, 780), T(22.5, 960, 900, 52, "pfft! dirt in the can", c="ink", d=0.6))
# 23 10 grams
bd(23, BIG(23, 960, 420, "~10 g", c="blue", d=0.1, s=180), dirt(23, 960, 700, 10, 300, 0.3), pho(23, 400, 800, 0.5)[0])
# 23.5 a tablespoon
sp, spi = spoon(23.5, 860, 520, 1.6, 0.0)
bd(23.5, sp, dirt(23.5, 800, 510, 8, 140, 0.3), T(23.5, 960, 820, 60, "one tablespoon", c="ink", d=0.4), [rot(23.5, spi, -10, (860, 520), 0.6, 0.8)])
# 24 2031
cap = uid("cap")
bd(24, BIG(24, 960, 380, "2031", c="blue", d=0.1, s=170), [O(24, 960, 160, 50, c="ink", fill="gold", idp=cap), pop(24, cap, 0.2), sh(24, cap, 0, 520, 0.4, 1.5)],
   icon(24, "globe", 960, 820, 140, 0.0, c="blue", mv="spin"))
# 24.5 Australia
aus = uid("aus")
cap = uid("cap")
bd(24.5, [P(24.5, "M600,520 Q650,380 860,400 Q1000,330 1120,420 Q1300,460 1300,620 Q1250,780 1060,760 Q900,820 760,740 Q600,700 600,520 Z", c="gold", w=6, fill="gold", idp=aus),
          pop(24.5, aus, 0.0), bob(24.5, aus, 3, 0.7)], [O(24.5, 950, 150, 40, c="ink", fill="muted", idp=cap), pop(24.5, cap, 0.1), sh(24.5, cap, 0, 420, 0.3, 1.2)],
   T(24.5, 960, 900, 60, "Australia", c="ink", d=0.4), check(24.5, 1450, 400, d=0.9))
# 25 why all this trouble
bd(25, icon(25, "rocket", 500, 560, 220, 0.0, c="red", mv="wig"), icon(25, "clock", 960, 560, 200, 0.1, mv="spin"), icon(25, "gear", 1420, 560, 200, 0.2, mv="spin"),
   T(25, 960, 860, 60, "why bother?", c="red", d=0.4))
# 25.5 nobody knows where Pho came from
bd(25.5, pho(25.5, 800, 560, 1.4, mood="o")[0], [e for q in range(3) for e in icon(25.5, "question", 1300 + 150 * q, 380 + 120 * (q % 2), 130, 0.2 + 0.15 * q, c="red", mv="wig")],
   T(25.5, 960, 880, 56, "where did I come from?", c="ink", d=0.5))
# 26 an asteroid
ast = uid("ast")
bd(26, [P(26, "M1400,300 Q1500,220 1600,300 Q1680,380 1580,450 Q1460,480 1400,400 Z", c="ink", w=6, fill="muted", idp=ast), pop(26, ast, 0.0), spin(26, ast, (1500, 360), 30),
        sh(26, ast, -500, 150, 0.3, 1.5)], T(26, 600, 300, 60, "idea 1: asteroid", c="blue", d=0.2), mars(26, 600, 700, 180, 0.1))
# 26.5 Mars captured
hk = uid("hk")
bd(26.5, mars(26.5, 760, 560, 220, 0.0), orbit(26.5, 760, 560, 480, 220, d=0.1), pho(26.5, 1240, 560, 0.5)[0],
   [P(26.5, "M980,560 Q1100,480 1180,540", c="red", w=7, idp=hk), pop(26.5, hk, 0.3), wig(26.5, hk, (980, 560), 6, 2.0)], T(26.5, 1300, 880, 56, "gotcha!", c="red", d=0.5))
# 27 giant impact
ast = uid("ast")
bd(27, mars(27, 960, 600, 260, 0.0), [O(27, 1700, 200, 60, c="ink", fill="muted", idp=ast), pop(27, ast, 0.0), sh(27, ast, -560, 220, 0.2, 0.8)],
   T(27, 500, 250, 60, "idea 2: BOOM", c="red", d=0.3), [e for q in range(4) for e in star(27, 1150 + 60 * q, 420 + 40 * q, 1.0, c="red", r=40)])
# 27.5 chunk off Mars
E = []
for q in range(6):
    i = uid("ch")
    E += [O(27.5, 960, 400, 14 + 4 * (q % 3), c="red", fill="red", idp=i), pop(27.5, i, 0.05 * q), sh(27.5, i, 500 * math.cos(q) , -200 - 60 * (q % 3), 0.1 + 0.05 * q, 1.0)]
bd(27.5, mars(27.5, 960, 650, 250, 0.0), E, pho(27.5, 1550, 300, 0.4, d=0.8)[0], T(27.5, 960, 970, 52, "a chunk of Mars itself", c="red", d=0.5))
# 28 tablespoon settles it
sp, spi = spoon(28, 760, 560, 1.4, 0.0)
bd(28, sp, dirt(28, 700, 550, 6, 120, 0.2), icon(28, "magnifier", 1350, 520, 260, 0.3, mv="wig"), check(28, 1600, 760, d=0.7))
# 28.5 bits of Mars
bd(28.5, dirt(28.5, 900, 520, 8, 300, 0.0), redbits(28.5), T(28.5, 960, 820, 56, "maybe... bits of Mars?", c="red", d=0.4), mars(28.5, 1600, 300, 90, 0.2))
# 29 twist three
bd(29, BIG(29, 960, 160, "TWIST 3", c="red", d=0.1, s=90), pho(29, 960, 560, 1.6, mood="sad")[0], [e for q in range(3) for e in icon(29, "water", 1150 + 60 * q, 450 + 40 * q, 60, 0.4 + 0.1 * q, c="blue")])
# 29.5 Pho is falling
p_, pi = pho(29.5, 1200, 250, 0.7, mood="o")
bd(29.5, mars(29.5, 760, 760, 260, 0.0), p_, [sh(29.5, pi + "*", -250, 220, 0.2, 2.0)], arr(29.5, 1300, 380, 1100, 560, c="red", d=0.3), T(29.5, 1500, 700, 60, "falling...", c="red", d=0.5))
# 30 6,000 km
bd(30, mars(30, 500, 560, 260, 0.0), pho(30, 1500, 560, 0.6)[0], arr(30, 780, 560, 1380, 560, c="blue", d=0.2), BIG(30, 1080, 420, "6,000 km", c="blue", d=0.3, s=110),
   T(30, 1080, 760, 44, "(the Moon: 384,000 km from us)", c="muted", d=0.6))
# 30.5 2 cm a year
p_, pi = pho(30.5, 1300, 500, 0.9)
bd(30.5, mars(30.5, 400, 560, 200, 0.0), p_, [sh(30.5, pi + "*", -60, 0, 0.3, 2.0)], BIG(30.5, 1100, 850, "2 cm / year", c="red", d=0.3, s=110), icon(30.5, "ruler", 800, 260, 160, 0.4, mv="wig"))
# 31 tens of millions of years
bd(31, BIG(31, 960, 420, "~30–50 million yrs", c="blue", d=0.1, s=110), [e for q in range(3) for e in icon(31, "clock", 500 + 460 * q, 760, 140, 0.2 + 0.1 * q, mv="spin")])
# 31.5 tear apart or crash
E = []
for q in range(8):
    i = uid("rg")
    E += [O(31.5, 1300, 400, 14, c="muted", fill="muted", idp=i), pop(31.5, i, 0.1), rot(31.5, i, -40 - 25 * q, (760, 600), 0.3 + 0.05 * q, 1.5)]
p_, pi = pho(31.5, 1300, 400, 0.5, mood="o")
bd(31.5, mars(31.5, 760, 600, 220, 0.0), p_, [{"t": "move", "at": 31.5, "kind": "grow", "targets": [pi + "*"], "axis": "both", "from": 1.0, "to": 0.05, "pivot": [1300, 400], "dur": 0.8, "delay": 0.2}],
   E, orbit(31.5, 760, 600, 560, 220, d=0.1), T(31.5, 960, 940, 52, "a ring... or a crater", c="red", d=0.6))
# 32 friendly fine print
s_, si = ship(32, 960, 560, 1.4, 0.0)
bd(32, T(32, 960, 200, 60, "friendly fine print", c="ink", d=0.1), s_, [sh(32, si, 0, -30, 0.3, 0.3), sh(32, si, 0, 30, 0.6, 0.3)], cross(32, 1450, 560, d=0.5), T(32, 1450, 760, 48, "no jumping", c="red", d=0.6))
# 32.5 gently on its legs
s_, si = ship(32.5, 960, 250, 1.4, 0.0)
bd(32.5, s_, [sh(32.5, si, 0, 400, 0.2, 2.0)], ground(32.5, 820), T(32.5, 960, 960, 56, "gently... gently...", c="blue", d=0.4), dirt(32.5, 960, 800, 6, 400, 1.6))
# 33 better hurry
bd(33, icon(33, "clock", 700, 520, 300, 0.0, mv="spin"), icon(33, "rocket", 1350, 520, 240, 0.2, c="red", mv="wig"), T(33, 960, 860, 64, "hurry!", c="red", d=0.4))
# 33.5 grab a souvenir before Pho falls
sp, spi = spoon(33.5, 600, 560, 1.0, 0.0)
p_, pi = pho(33.5, 1300, 400, 0.9)
bd(33.5, sp, dirt(33.5, 560, 550, 5, 100, 0.2), p_, [sh(33.5, pi + "*", 0, 200, 0.4, 2.0)], BIG(33.5, 960, 880, "souvenir", c="gold", d=0.4, s=110), mars(33.5, 1650, 820, 110, 0.1))
# 34 Pho's rule
bd(34, pho(34, 960, 520, 2.2, d=0.0)[0], [e for q in range(4) for e in star(34, 400 + 370 * q, 880, 0.3 + 0.1 * q, r=34)], T(34, 960, 170, 56, "Pho's one rule", c="ink", d=0.3))
# 34.5 do not jump
ps, pp = person(34.5, 960, 560, 1.2)
bd(34.5, ps, [sh(34.5, pp, 0, -40, 0.3, 0.3), sh(34.5, pp, 0, 40, 0.6, 0.3)], cross(34.5, 960, 430, d=0.5), BIG(34.5, 960, 920, "DO NOT JUMP", c="red", d=0.2, s=120), ground(34.5, 720),
   pho(34.5, 1600, 400, 0.5)[0])

# ---- extra sentences (inserted after an original sentence; boards use at = 100 + j) ----
X = [
 (9, "它还带了一个小机器人：|法国和德国造的漫游车，IDEFIX。", "It also carries a little robot: | a French-German rover called IDEFIX."),
 (9, "在这么弱的引力下开车很难：|轮子一使劲，车就可能飘起来。", "Driving in gravity this weak is tricky: | spin the wheels too hard and the rover could float off."),
 (9, "所以它得像树懒一样，|慢慢地、小心地爬。", "So it has to move like a sloth, | slow and careful."),
 (16, "站在小福上抬头看，|火星占了一大片天。", "Stand on Pho and look up: | Mars fills a huge chunk of the sky."),
 (16, "看起来比我们的满月|宽大约80倍。", "It looks about 80 times wider | than our full Moon."),
 (16, "小福绕火星一圈只要七个多小时，|比火星自转还快。", "Pho circles Mars in about seven and a half hours, | faster than Mars spins."),
 (16, "所以在火星上看，小福西边升起、东边落下，|一天两次。", "So from Mars, Pho rises in the west and sets in the east, | twice a day."),
 (22, "在这么弱的引力下，你推地面，地面也推你。|挖得太猛，就把自己推飞了。", "In gravity this weak, every push pushes back. | Dig too hard, and you shove yourself off."),
 (24, "临走前，它还会顺路看一眼|火星另一颗更小的月亮，火卫二。", "Before heading home, it will also fly past | Mars' other, smaller moon, Deimos."),
 (30, "怪潮汐：火星的引力把小福一点点往里拖，|像一个慢慢收紧的绳套。", "Blame tides: Mars' gravity drags Pho inward, | like a slowly tightening lasso."),
 (31, "到时候，火星也许会有一圈自己的光环。|这是科学家的一种推测。", "Mars might even end up with a ring of its own. | That's one scientific guess."),
]
# 100 IDEFIX
rv = uid("rv")
bd(100, [R(100, 760, 480, 360, 160, c="ink", fill="blue", idp=rv), O(100, 820, 660, 40, c="ink", fill="muted", idp=rv), O(100, 1060, 660, 40, c="ink", fill="muted", idp=rv),
         pop(100, rv, 0.0), bob(100, rv, 5, 1.2), sh(100, rv, 200, 0, 0.4, 1.2)], BIG(100, 960, 260, "IDEFIX", c="blue", d=0.2, s=130), ground(100, 720),
   T(100, 960, 880, 52, "a French-German rover", c="ink", d=0.4))
# 100.5 robot
bd(100.5, icon(100.5, "robot_arm", 600, 520, 260, 0.0, mv="wig"), icon(100.5, "wheel", 1100, 560, 180, 0.2, mv="spin"), icon(100.5, "wheel", 1400, 560, 180, 0.3, mv="spin"),
   T(100.5, 1250, 820, 56, "robot on a potato", c="blue", d=0.4))
# 101 tricky driving
wh = icon(101, "wheel", 960, 600, 260, 0.0, mv="spin")
bd(101, wh, [sh(101, wh[0]["id"], 0, -40, 0.5, 0.4), sh(101, wh[0]["id"], 0, 40, 1.0, 0.4)], ground(101, 760), dirt(101, 960, 720, 8, 300, 0.4), T(101, 960, 220, 60, "driving? tricky", c="ink", d=0.2))
# 101.5 rover floats off
rv = uid("rv")
bd(101.5, [R(101.5, 760, 620, 300, 130, c="ink", fill="blue", idp=rv), O(101.5, 810, 770, 35, c="ink", fill="muted", idp=rv), O(101.5, 1010, 770, 35, c="ink", fill="muted", idp=rv),
           pop(101.5, rv, 0.0), sh(101.5, rv, 300, -400, 0.4, 1.6), rot(101.5, rv, -30, (910, 690), 0.4, 1.6)], ground(101.5, 820), T(101.5, 600, 300, 60, "wheee...", c="red", d=0.6),
   pho(101.5, 1650, 800, 0.4, mood="o")[0])
# 102 sloth
sl = uid("sl")
bd(102, [P(102, "M500,400 L1400,400", c="green", w=10, idp=(br_ := uid("br"))), bob(102, br_, 3, 0.6),
         O(102, 800, 520, 90, c="ink", fill="muted", idp=sl), P(102, "M740,440 L740,400 M860,440 L860,400", c="ink", w=8, idp=sl), O(102, 770, 510, 10, c="ink", fill="ink", idp=sl),
         O(102, 830, 510, 10, c="ink", fill="ink", idp=sl), P(102, "M775,550 Q800,570 825,550", c="ink", w=5, idp=sl), pop(102, sl, 0.0), wig(102, sl, (800, 400), 6, 0.6), sh(102, sl, 150, 0, 0.3, 2.0)],
   T(102, 1350, 620, 64, "sloth mode", c="green", d=0.3))
# 102.5 slow and careful
bd(102.5, BIG(102.5, 960, 420, "slow + careful", c="blue", d=0.1, s=120), icon(102.5, "clock", 500, 760, 150, 0.2, mv="spin"), icon(102.5, "wheel", 1420, 760, 150, 0.3, mv="spin"))
# 103 stand on Pho, look up
ps, pp = person(103, 960, 760, 0.8)
bd(103, ps, pho(103, 960, 1000, 1.2)[0], mars(103, 960, 260, 220, 0.2), arr(103, 1060, 600, 1060, 450, c="ink", d=0.4))
# 103.5 huge chunk of sky
bd(103.5, mars(103.5, 960, 420, 380, 0.0), person(103.5, 500, 900, 0.4)[0], T(103.5, 1550, 900, 52, "huge!", c="red", d=0.4),
   [e for q in range(3) for e in star(103.5, 300 + 120 * q, 250, 0.3 + 0.1 * q, r=24)])
# 104 80 times wider
bd(104, BIG(104, 960, 380, "× 80", c="red", d=0.1, s=180), icon(104, "moon", 500, 780, 60, 0.2, c="gold"), mars(104, 1350, 780, 180, 0.3))
# 104.5 than our full Moon
bd(104.5, icon(104.5, "moon", 700, 500, 260, 0.0, c="gold", mv="bob"), T(104.5, 1300, 500, 64, "our full Moon", c="gold", d=0.2), arr(104.5, 1300, 600, 900, 600, c="ink", d=0.4),
   icon(104.5, "globe", 1550, 800, 120, 0.4, c="blue", mv="spin"))
# 105 7.5 hours
p_, pi = pho(105, 1300, 560, 0.5)
bd(105, mars(105, 760, 560, 200, 0.0), orbit(105, 760, 560, 540, 240, d=0.1), p_, [rot(105, pi + "*", -340, (760, 560), 0.2, 2.5)], BIG(105, 960, 920, "7.5 hours", c="blue", d=0.3, s=100))
# 105.5 faster than Mars spins
bd(105.5, mars(105.5, 700, 560, 220, 0.0), icon(105.5, "clock", 1350, 450, 180, 0.2, mv="spin"), T(105.5, 1350, 700, 56, "faster than a Mars day", c="red", d=0.4),
   pho(105.5, 1350, 900, 0.3)[0])
# 106 rises in the west
p_, pi = pho(106, 1600, 700, 0.4)
bd(106, ground(106, 820, c="red"), p_, [sh(106, pi + "*", -1200, -100, 0.3, 2.0)], T(106, 1600, 920, 44, "west", c="ink", d=0.2), T(106, 300, 920, 44, "east", c="ink", d=0.2),
   arr(106, 1400, 400, 600, 400, c="blue", d=0.4))
# 106.5 twice a day
bd(106.5, BIG(106.5, 960, 420, "2× a day", c="blue", d=0.1, s=150), pho(106.5, 500, 780, 0.4, d=0.2)[0], pho(106.5, 1420, 780, 0.4, d=0.4)[0])
# 107 every push pushes back
ps, pp = person(107, 760, 640, 1.0)
bd(107, ps, ground(107, 800), arr(107, 860, 760, 860, 840, c="red", d=0.2), arr(107, 960, 820, 960, 600, c="blue", d=0.4), T(107, 1400, 500, 56, "push = push back", c="ink", d=0.3))
# 107.5 dig too hard, shove yourself off
s_, si = ship(107.5, 960, 640, 0.9, 0.0)
bd(107.5, s_, [sh(107.5, si, 200, -400, 0.4, 1.2), rot(107.5, si, 30, (960, 640), 0.4, 1.2)], ground(107.5, 760), dirt(107.5, 960, 740, 6, 200, 0.3), T(107.5, 500, 300, 60, "oops", c="red", d=0.6))
# 108 fly past
s_, si = ship(108, 300, 400, 0.5, 0.0)
bd(108, s_, [sh(108, si, 1300, 100, 0.2, 2.0)], mars(108, 500, 800, 150, 0.1), icon(108, "moon", 1400, 600, 120, 0.3, c="muted", mv="spin"))
# 108.5 Deimos
dm = uid("dm")
bd(108.5, [P(108.5, "M800,500 Q820,400 960,410 Q1100,420 1110,520 Q1100,620 960,620 Q820,620 800,500 Z", c="ink", w=6, fill="muted", idp=dm), pop(108.5, dm, 0.0), bob(108.5, dm, 6, 1.0),
           spin(108.5, dm, (960, 515), 6)], BIG(108.5, 960, 820, "Deimos", c="blue", d=0.3, s=110), pho(108.5, 400, 400, 0.6)[0])
# 109 blame tides
p_, pi = pho(109, 1400, 560, 0.6)
bd(109, mars(109, 600, 560, 260, 0.0), p_, [e for q in range(3) for e in arr(109, 1250, 460 + 100 * q, 900, 460 + 100 * q, c="red", d=0.1 * q)], T(109, 960, 900, 60, "tides", c="red", d=0.3))
# 109.5 tightening lasso
ls_ = uid("ls")
p_, pi = pho(109.5, 960, 560, 0.7, mood="o")
bd(109.5, p_, [O(109.5, 960, 560, 300, c="gold", idp=ls_), pop(109.5, ls_, 0.0), spin(109.5, ls_, (960, 560), 20),
               {"t": "move", "at": 109.5, "kind": "grow", "targets": [ls_], "axis": "both", "from": 1.0, "to": 0.6, "pivot": [960, 560], "dur": 2.0, "delay": 0.3}],
   T(109.5, 960, 950, 52, "a slowly tightening lasso", c="gold", d=0.4))
# 110 ring of its own
bd(110, mars(110, 960, 560, 220, 0.0), orbit(110, 960, 560, 450, 110, c="gold", d=0.2, rpm=10), orbit(110, 960, 560, 400, 90, c="muted", d=0.3, rpm=-8), dirt(110, 960, 560, 10, 900, 0.4))
# 110.5 one scientific guess
bd(110.5, icon(110.5, "question", 700, 500, 240, 0.0, c="muted", mv="wig"), T(110.5, 1300, 500, 64, "just a guess", c="muted", d=0.2), icon(110.5, "flask", 1300, 760, 150, 0.3, mv="wig"))

# merge: new sentence order, remap board times
ORDER = []
for k in range(len(S)):
    ORDER.append(k)
    ORDER += [100 + j for j, x in enumerate(X) if x[0] == k]
S = [S[k] if k < 100 else X[k - 100][1:] for k in ORDER]
NEW = {k: n for n, k in enumerate(ORDER)}
for b in B:
    for e in b:
        e["at"] = NEW[int(e["at"])] + (e["at"] - int(e["at"]))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"MMX": "M M X", "H3": "H three", "2031": "twenty thirty-one", "6,000": "six thousand", "IDEFIX": "Idefix", "7.5": "seven and a half"})
