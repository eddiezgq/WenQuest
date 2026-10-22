"""Daily science short 2026-10-22 (English): "Halley's Comet Is Hitting Us Tonight"
News: the Orionid meteor shower peaks Oct 21-22, 2026 (Live Science "See pieces of Halley's Comet fall to Earth this week as the Orionid
meteor shower peaks", in its Trending list; Space.com "How to see the Orionid meteor shower 2026 peak this week").
Facts (Space.com): peak around Oct 21-22; up to 15-20 per hour in the dark hours before dawn; dust hits the air at 66 km/s (41 mi/s);
starts burning ~130 km (80 mi) up; about half leave persistent glowing trains; waxing gibbous Moon sets shortly after 2 a.m.;
Halley's period ~75-76 years; particles "tiny and brittle, with the consistency of cigar ash"; Halley returns 2061.
Textbook: Halley orbits retrograde, so Earth meets its dust head-on; meteors glow because air piles up in front (ram compression),
heats, vaporizes the grain, and the hot atoms/air glow (not mainly friction); radiant in Orion; dark adaptation ~20 min.
Our estimates (said as estimates): 66 km/s ≈ 150,000 mph; ~70x a rifle bullet (~1 km/s); 1 mg at 66 km/s ≈ ½·1e-6·66000² ≈ 2,200 J,
more than a typical pistol bullet (~500 J). Character: Dusty, a crumb of Halley's Comet. Running gag: waited forever, famous for one second. No hand.
    python3 make.py <kokoro model dir> | --boards-only   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("今晚，哈雷彗星的碎片正在砸向地球。|速度是每秒66公里。", "Tonight, tiny pieces of Halley's Comet are slamming into Earth. | At 66 kilometers per second."),
 ("差不多每小时24万公里。|而你在自家后院就能看。", "That's about 150,000 miles an hour. | And you can watch it from your backyard."),
 ("这就是猎户座流星雨，|差不多正在极大期。", "It's the Orionid meteor shower, | peaking right about now."),
 ("今天的问题：一粒比沙子还小的灰，|怎么能把整片天空点亮？", "Today's question: how does a speck smaller than a grain of sand | light up the whole sky?"),
 ("认识一下小尘。|小尘是哈雷彗星掉下来的一点渣。", "Meet Dusty. | Dusty is a crumb of Halley's Comet."),
 ("哈雷彗星大约每76年|绕太阳回来一次。", "Halley's Comet swings by the Sun | about every 76 years."),
 ("每次靠近，太阳一烤，|它就掉灰，像狗掉毛。", "Each time, the Sun cooks it, | and it sheds dust like a dog sheds fur."),
 ("绕了几千圈，|这些灰铺成了一条长长的脏带子。", "Over thousands of orbits, | that dust spreads into a long, dirty ring."),
 ("每年十月，地球正好从里面穿过。|年年同一时间。", "Every October, Earth drives right through it. | Same time, every year."),
 ("就像在高速公路上|开进一团飞虫。", "Like driving through a cloud of bugs | on the highway."),
 ("反转一：我们是迎头撞上的。|哈雷彗星绕太阳的方向跟地球相反。", "Twist one: we hit it head-on. | Halley orbits the Sun the opposite way to us."),
 ("所以速度要相加。|迎面相撞，最狠。", "So the speeds add up. | Head-on collisions are the worst kind."),
 ("每秒66公里，|大约是步枪子弹的70倍。", "66 kilometers per second | is roughly 70 times faster than a rifle bullet."),
 ("而能量跟速度的平方走。|速度翻倍，冲击翻四倍。", "And energy grows with speed squared. | Double the speed, four times the punch."),
 ("我们估算一下：1毫克的小灰，这个速度，|带着大约两千焦耳的能量。", "Our rough estimate: a one-milligram speck at that speed | carries about 2,000 joules."),
 ("这比一颗手枪子弹的能量|还要大。", "That's more energy | than a pistol bullet."),
 ("反转二：让它发光的，|不是摩擦。", "Twist two: it's not friction | that makes it glow."),
 ("小尘太快了，空气来不及让开，|在它前面挤成一堆，又烫又密。", "Dusty is so fast, the air can't get out of the way. | It piles up in front, squeezed and scorching hot."),
 ("空气被挤得又狠又快，|就能热到几千度。", "Squeeze air hard enough and fast enough, | and it heats to thousands of degrees."),
 ("就像打气筒会发烫，|只不过开了快进。", "Like a bike pump getting hot, | but on fast-forward."),
 ("小尘一个原子一个原子地蒸发掉，|大约在一百多公里的高空。", "Dusty boils away, atom by atom, | more than 100 kilometers up."),
 ("这些滚烫的原子和周围的空气在发光，|就像霓虹灯。", "Those hot atoms, and the air around them, glow. | Like a neon sign."),
 ("所以你看到的那道光，不是一块烧着的石头，|而是一条几公里长、发光的空气管子。", "So the streak you see is not a rock on fire. | It's a tube of glowing air, kilometers long."),
 ("反转三，最反直觉：|那道光比小尘大太多了。", "Twist three, the weird part: | the streak is way bigger than Dusty."),
 ("放在指尖上都找不到的一点渣，|能划出一百公里外都看得见的线。", "A crumb you could lose on your fingertip | makes a line you can see from 100 kilometers away."),
 ("大约一半的猎户座流星，还会留下发光的尾迹，|在天上停一会儿。", "About half the Orionids even leave glowing trails | that hang in the sky for a moment."),
 ("而且它们一个都落不到地上。|没到半路，小尘就没了。", "And none of them reach the ground. | Dusty is gone long before it gets close."),
 ("怎么看：天亮前那几个小时，|离城市的灯光远一点。", "How to watch: go out in the dark hours before dawn | and get away from city lights."),
 ("月亮大约凌晨两点落下，|之后天更黑。", "The Moon sets around 2 a.m., | so the sky gets darker after that."),
 ("看天上哪里都行。|流星都像是从猎户座里飞出来的。", "Look anywhere in the sky. | The streaks all seem to fly out of Orion."),
 ("给眼睛20分钟适应。|还有，把手机收起来。", "Give your eyes 20 minutes. | And put your phone away."),
 ("友情提示：最好的时候，一小时也就15到20颗，|带上耐心和一条毯子。", "Friendly fine print: maybe 15 to 20 an hour at best, | so bring patience and a blanket."),
 ("错过了？哈雷的灰每年十月都会回来。|哈雷彗星本尊，2061年回来。", "Missed it? Halley's dust comes back every October. | And Halley itself returns in 2061."),
 ("小尘等了几千年，就为这一刻。|只亮了一秒，可是真灿烂。", "Dusty waited thousands of years for this moment. | It lasted one second, and it was glorious."),
]
TITLE = {"zh": "哈雷彗星今晚砸地球", "en": "Halley's Comet Is Hitting Us Tonight"}

B = []


def bd(a, *parts, n=2):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    if n > 2:
        E += star(a, 1810, 900, 0.5, r=20)
    B.append(E)


def dusty(a, x, y, k=1.0, mood="happy", hot=False):
    """Dusty: a lumpy little crumb with a face; bobs and wiggles all the time."""
    i = uid("du") + "_"
    c = "red" if hot else "ink"
    E = [P(a, f"M{x - 90 * k},{y} Q{x - 100 * k},{y - 80 * k} {x - 20 * k},{y - 90 * k} Q{x + 60 * k},{y - 110 * k} {x + 95 * k},{y - 30 * k} "
              f"Q{x + 110 * k},{y + 60 * k} {x + 20 * k},{y + 85 * k} Q{x - 80 * k},{y + 90 * k} {x - 90 * k},{y} Z", c=c, w=6, fill="gold" if hot else "muted", idp=i),
         O(a, x - 30 * k, y - 20 * k, 11 * k, c="ink", fill="ink", idp=i), O(a, x + 30 * k, y - 20 * k, 11 * k, c="ink", fill="ink", idp=i)]
    m = {"happy": f"M{x - 25 * k},{y + 25 * k} Q{x},{y + 50 * k} {x + 25 * k},{y + 25 * k}",
         "o": f"M{x - 12 * k},{y + 35 * k} a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0",
         "sad": f"M{x - 25 * k},{y + 45 * k} Q{x},{y + 20 * k} {x + 25 * k},{y + 45 * k}"}[mood]
    E += [P(a, m, c="ink", w=5, idp=i), bob(a, i, 8 * k, 1.4), wig(a, i, (x, y + 85 * k), 5, 1.2)]
    return E, i


def earth(a, x, y, r=150, d=0.0):
    i = uid("ea")
    return [O(a, x, y, r, c="blue", idp=i), P(a, f"M{x - r * .5},{y - r * .4} q{r * .3},{-r * .2} {r * .5},{r * .1} q{-r * .1},{r * .4} {-r * .4},{r * .3} Z "
                                                 f"M{x + r * .2},{y + r * .2} q{r * .4},0 {r * .4},{r * .4}", c="green", w=5, idp=i),
            pop(a, i, d), spin(a, i, (x, y), 12)]


def sun(a, x, y, s=220, d=0.0):
    i = uid("sun")
    return [{"t": "icon", "at": a, "id": i, "name": "sun", "x": x, "y": y, "size": s, "c": "gold"}, pop(a, i, d), spin(a, i, (x, y), 20)]


def comet(a, x, y, k=1.0, d=0.0, dx=0, dy=0):
    i = uid("cm")
    E = [O(a, x, y, 40 * k, c="ink", fill="muted", idp=i), P(a, f"M{x + 30 * k},{y - 30 * k} Q{x + 200 * k},{y - 120 * k} {x + 380 * k},{y - 90 * k} "
                                                              f"M{x + 40 * k},{y} Q{x + 220 * k},{y - 40 * k} {x + 400 * k},{y - 10 * k} "
                                                              f"M{x + 30 * k},{y + 30 * k} Q{x + 200 * k},{y + 60 * k} {x + 360 * k},{y + 80 * k}", c="blue", w=5, idp=i),
         pop(a, i, d), wig(a, i, (x, y), 3, 1.5)]
    if dx or dy:
        E.append(sh(a, i, dx, dy, d + 0.2, 1.2))
    return E, i


def streak(a, x0, y0, x1, y1, d=0.0, c="gold", w=8):
    i = uid("sk")
    return [P(a, f"M{x0},{y0} L{x1},{y1}", c=c, w=w, idp=i),
            {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "both", "from": 0.05, "to": 1.0, "pivot": [x0, y0], "dur": 0.5, "delay": d}]


def shower(a, n=5, d=0.0, x0=1500, y0=150):
    E = []
    for q in range(n):
        sx, sy = x0 - 250 * q, y0 + 60 * (q % 3)
        E += streak(a, sx, sy, sx - 320, sy + 220, d + 0.18 * q, c="gold" if q % 2 else "blue", w=6)
    return E


def dust_cloud(a, x, y, n=10, spread=300, d=0.0, c="muted"):
    E = []
    for q in range(n):
        i = uid("dc")
        E += [O(a, x + ((q * 137) % spread) - spread / 2, y + ((q * 89) % (spread * .6)) - spread * .3, 8 + q % 3 * 4, c=c, fill=c, idp=i), pop(a, i, d + 0.03 * q),
              bob(a, i, 6, 0.8 + 0.1 * (q % 5))]
    return E


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def bullet(a, x, y, k=1.0, d=0.0, dx=600):
    i = uid("bl")
    return [P(a, f"M{x},{y - 20 * k} L{x + 80 * k},{y - 20 * k} Q{x + 130 * k},{y} {x + 80 * k},{y + 20 * k} L{x},{y + 20 * k} Z", c="ink", w=5, fill="gold", idp=i),
            pop(a, i, d), sh(a, i, dx, 0, d + 0.2, 1.4)]


def air(a, x, y, n=8, d=0.0, tx=None):
    """Air molecules piling up toward (tx, y)."""
    E = []
    tx = x - 250 if tx is None else tx
    for q in range(n):
        i = uid("air")
        ax, ay = x - 500 + 60 * (q % 4), y - 150 + 45 * q
        E += [O(a, ax, ay, 14, c="blue", fill="blue", idp=i), pop(a, i, d + 0.04 * q), sh(a, i, tx - ax + 20 * (q % 3), (y - ay) * 0.6, d + 0.2 + 0.05 * q, 0.6),
              wig(a, i, (ax, ay), 10, 4.0)]
    return E


def heat(a, x, y, d=0.0):
    i = uid("ht")
    return [O(a, x, y, 140, c="red", idp=i), pop(a, i, d), pulse(a, i, d + 0.4), pulse(a, i, d + 1.1), wig(a, i, (x, y), 4, 3.0)]


def person(a, x, y, k=1.0, c="ink"):
    i = uid("ps")
    return [O(a, x, y - 130 * k, 40 * k, c=c, idp=i), P(a, f"M{x},{y - 90 * k} L{x},{y + 40 * k} M{x - 60 * k},{y - 30 * k} L{x},{y - 60 * k} L{x + 60 * k},{y - 30 * k} "
                                                         f"M{x},{y + 40 * k} L{x - 40 * k},{y + 130 * k} M{x},{y + 40 * k} L{x + 40 * k},{y + 130 * k}", c=c, w=6, idp=i),
            bob(a, i, 5, 1.0), wig(a, i, (x, y + 130 * k), 4, 1.2)]


def orion(a, x, y, k=1.0, d=0.0):
    pts = [(-120, -200), (120, -180), (-30, 0), (0, -10), (30, -20), (-140, 200), (130, 210)]
    E = []
    for q, (px, py) in enumerate(pts):
        E += star(a, x + px * k, y + py * k, d + 0.06 * q, r=22 * k)
    return E


# 0 slamming into Earth
d_, di = dusty(0, 500, 300, 0.8, hot=True)
bd(0, earth(0, 1300, 620, 260), d_, [sh(0, di + "*", 600, 250, 0.3, 0.8)], shower(0, 4, 0.2, x0=1100, y0=120))
# 0.5 66 km/s
bd(0.5, BIG(0.5, 960, 470, "66 km/s", c="red", d=0.1, s=190), shower(0.5, 5, 0.2, x0=1700, y0=650), icon(0.5, "clock", 300, 300, 150, 0.3, mv="spin"))
# 1 150,000 mph
bd(1, BIG(1, 960, 450, "150,000 mph", c="red", d=0.1, s=150), [e for q in range(3) for e in icon(1, "car", 400 + 560 * q, 780, 140, 0.2 * q, mv="wig")],
   [sh(1, B[-1][0]["id"], 0, 0, 0, 0.1)][:0])
# 1.5 backyard
hs = uid("hs")
bd(1.5, [P(1.5, "M300,860 L300,600 L450,480 L600,600 L600,860 Z", c="ink", w=6, idp=hs), bob(1.5, hs, 2, 0.6)], person(1.5, 900, 740, 1.0), shower(1.5, 4, 0.3, x0=1700, y0=150),
   T(1.5, 1400, 880, 56, "your backyard", c="green", d=0.4))
# 2 Orionid meteor shower
bd(2, orion(2, 600, 480, 1.0), shower(2, 5, 0.3, x0=1650, y0=200), T(2, 1300, 760, 64, "the Orionids", c="blue", d=0.3))
# 2.5 peaking now
bd(2.5, bar(2.5, 500, 820, 160, 200, "blue", d=0.1), bar(2.5, 700, 820, 160, 420, "blue", d=0.2), bar(2.5, 900, 820, 160, 560, "red", d=0.3, dur=1.0),
   bar(2.5, 1100, 820, 160, 380, "blue", d=0.4), BIG(2.5, 1500, 400, "PEAK", c="red", d=0.6, s=120), T(2.5, 1500, 560, 48, "Oct 21–22", c="ink", d=0.7))
# 3 speck smaller than sand
d_, di = dusty(3, 700, 560, 0.5)
bd(3, d_, dust_cloud(3, 1300, 560, 12, 400, 0.1, c="gold"), T(3, 1300, 820, 52, "grain of sand", c="gold", d=0.3), T(3, 700, 820, 52, "smaller!", c="red", d=0.5))
# 3.5 light up the whole sky
bd(3.5, shower(3.5, 6, 0.0, x0=1750, y0=150), icon(3.5, "question", 860, 560, 240, 0.4, c="red", mv="wig"))
# 4 meet Dusty
d_, di = dusty(4, 900, 560, 2.2)
bd(4, d_, [pop(4, di + "*", 0.0)], BIG(4, 1550, 360, "Dusty", c="blue", d=0.4, s=140), star(4, 400, 300, 0.6, r=40), n=3)
# 4.5 crumb of Halley
c_, ci = comet(4.5, 700, 450, 1.3)
d_, di = dusty(4.5, 1400, 700, 0.8)
bd(4.5, c_, d_, [sh(4.5, di + "*", 0, 60, 0.3, 0.6)], T(4.5, 1300, 900, 52, "a crumb of Halley", c="ink", d=0.4))
# 5 swings by the Sun
orb = uid("orb")
c_, ci = comet(5, 1500, 500, 0.6)
bd(5, sun(5, 600, 500, 220), [P(5, "M500,500 A600,260 0 1,0 1700,500 A600,260 0 1,0 500,500", c="muted", w=4, idp=orb), pop(5, orb, 0.1)], c_,
   [rot(5, ci, -60, (1100, 500), 0.3, 1.5)])
# 5.5 every 76 years
bd(5.5, BIG(5.5, 960, 450, "76 years", c="blue", d=0.1, s=170), icon(5.5, "clock", 400, 750, 160, 0.3, mv="spin"), icon(5.5, "clock", 1520, 750, 160, 0.4, mv="spin"))
# 6 Sun cooks it
c_, ci = comet(6, 1100, 500, 1.2)
bd(6, sun(6, 400, 500, 260), c_, [e for q in range(3) for e in arr(6, 560, 400 + 100 * q, 900, 420 + 80 * q, c="red", d=0.2 + 0.1 * q)],
   T(6, 1200, 820, 56, "the Sun cooks it", c="red", d=0.4))
# 6.5 sheds like a dog
dog = uid("dog")
bd(6.5, [P(6.5, "M400,600 Q400,450 560,450 L820,450 Q900,450 900,380 L960,380 L960,500 L900,560 L900,700 M440,600 L440,720 M820,600 L820,720 M400,600 L900,600",
           c="ink", w=6, idp=dog), pop(6.5, dog, 0.0), wig(6.5, dog, (650, 720), 4, 2.5)], dust_cloud(6.5, 650, 380, 10, 400, 0.2),
   T(6.5, 1400, 500, 60, "shedding!", c="ink", d=0.3), dust_cloud(6.5, 1400, 700, 8, 300, 0.4))
# 7 thousands of orbits
E = []
for q in range(4):
    o = uid("orb")
    E += [P(7, f"M{560 - 30 * q},500 A{560 + 30 * q},{220 + 15 * q} 0 1,0 {1700 + 30 * q},500 A{560 + 30 * q},{220 + 15 * q} 0 1,0 {560 - 30 * q},500", c="muted", w=3, idp=o),
          pop(7, o, 0.1 * q), rot(7, o, 3 * (q - 1.5), (1130, 500), 0.3 + 0.1 * q, 0.6)]
bd(7, sun(7, 700, 500, 160), E, T(7, 960, 880, 56, "thousands of orbits", c="ink", d=0.3))
# 7.5 dirty ring
ring = uid("ring")
bd(7.5, [{"t": "ellipse", "at": 7.5, "id": ring, "x": 360, "y": 260, "w": 1200, "h": 480, "c": "muted"}, pop(7.5, ring, 0.0), spin(7.5, ring, (960, 500), 3)],
   dust_cloud(7.5, 500, 500, 10, 200, 0.1), dust_cloud(7.5, 1420, 500, 10, 200, 0.3), sun(7.5, 960, 500, 150), T(7.5, 960, 880, 56, "a long, dirty ring", c="ink", d=0.4))
# 8 Earth drives through
e_ = earth(8, 400, 500, 140)
bd(8, e_, [sh(8, e_[0]["id"], 1100, 0, 0.2, 1.4)], dust_cloud(8, 1000, 500, 16, 500, 0.0), T(8, 960, 880, 56, "every October", c="blue", d=0.3))
# 8.5 same time every year
cal = uid("cal")
bd(8.5, [R(8.5, 560, 260, 400, 440, c="ink", idp=cal), P(8.5, "M560,360 L960,360", c="red", w=10, idp=cal), pop(8.5, cal, 0.0), wig(8.5, cal, (760, 260), 4, 1.0)],
   T(8.5, 760, 540, 72, "OCT", c="red", d=0.2), [e for q in range(3) for e in check(8.5, 1250 + 180 * q, 480, d=0.3 + 0.2 * q)], T(8.5, 1430, 700, 48, "every year", c="ink", d=0.6))
# 9 cloud of bugs
cr = icon(9, "car", 500, 560, 300, 0.0, mv="wig")
bd(9, cr, [sh(9, cr[0]["id"], 300, 0, 0.2, 1.2)], dust_cloud(9, 1300, 520, 14, 400, 0.1, c="ink"), T(9, 1300, 860, 56, "a cloud of bugs", c="ink", d=0.3))
# 9.5 splat on the windshield
E = []
for q in range(6):
    i = uid("spl")
    E += [P(9.5, f"M{700 + 90 * q},{400 + 50 * (q % 3)} l15,-25 l15,25 l15,-25", c="ink", w=5, idp=i), pop(9.5, i, 0.1 * q), wig(9.5, i, (715 + 90 * q, 400), 10, 3.0)]
ws = uid("ws")
bd(9.5, [R(9.5, 600, 300, 700, 360, c="blue", idp=ws), bob(9.5, ws, 3, 0.9)], E, T(9.5, 960, 860, 56, "splat, splat, splat", c="red", d=0.4))
# 10 twist one head-on
e_ = earth(10, 600, 520, 130)
c_, ci = comet(10, 1400, 520, 0.8)
bd(10, BIG(10, 960, 160, "TWIST 1", c="red", d=0.1, s=90), e_, c_, [sh(10, e_[0]["id"], 200, 0, 0.3, 0.6), sh(10, ci, -300, 0, 0.3, 0.6)], T(10, 960, 820, 60, "head-on", c="red", d=0.4))
# 10.5 opposite way
o1, o2 = uid("o"), uid("o")
bd(10.5, sun(10.5, 960, 520, 160), [P(10.5, "M560,520 A400,300 0 1,1 1360,520", c="blue", w=5, idp=o1), pop(10.5, o1, 0.1), spin(10.5, o1, (960, 520), 15),
                                    P(10.5, "M460,520 A500,360 0 1,0 1460,520", c="red", w=5, idp=o2), pop(10.5, o2, 0.3), spin(10.5, o2, (960, 520), -15)],
   T(10.5, 360, 220, 48, "Earth", c="blue", d=0.2), T(10.5, 1600, 900, 48, "Halley", c="red", d=0.4))
# 11 speeds add up
bd(11, arr(11, 300, 400, 900, 400, c="blue", d=0.1), arr(11, 1620, 600, 1020, 600, c="red", d=0.3), BIG(11, 960, 820, "+", c="ink", d=0.5, s=140),
   earth(11, 220, 400, 70), dusty(11, 1720, 600, 0.6)[0])
# 11.5 worst kind
e_ = earth(11.5, 500, 520, 160)
d_, di = dusty(11.5, 1400, 520, 0.8, mood="o", hot=True)
bd(11.5, e_, d_, [sh(11.5, di + "*", -620, 0, 0.2, 0.5), sh(11.5, e_[0]["id"], 80, 0, 0.2, 0.5)], [e for q in range(4) for e in star(11.5, 800, 360 + 90 * q, 0.7, c="red", r=35)])
# 12 66 km/s
bd(12, BIG(12, 960, 450, "66 km/s", c="red", d=0.1, s=170), (d_ := dusty(12, 300, 760, 0.6, hot=True)[0]), [sh(12, d_[0]["id"], 1300, 0, 0.3, 0.6)])
# 12.5 70x rifle bullet
bd(12.5, bullet(12.5, 300, 400, 1.0, 0.1, dx=200), T(12.5, 700, 400, 44, "rifle bullet", c="muted", d=0.2), bullet(12.5, 300, 650, 1.0, 0.1, dx=1300),
   T(12.5, 960, 780, 44, "Dusty", c="red", d=0.3), BIG(12.5, 1450, 400, "× 70", c="red", d=0.5, s=130))
# 13 energy ~ speed squared
bd(13, BIG(13, 960, 420, "E ~ v²", c="ink", d=0.1, s=170), icon(13, "gear", 400, 760, 150, 0.3, mv="spin"), icon(13, "gear", 1520, 760, 150, 0.4, mv="spin"))
# 13.5 double speed four times punch
E = []
for q in range(4):
    i = uid("sq")
    s_ = 70 + 70 * q
    E += [R(13.5, 450 + 270 * q - s_ / 2, 820 - s_, s_, s_, c="red", fill="red" if q == 3 else None, idp=i), pop(13.5, i, 0.1 + 0.15 * q), bob(13.5, i, 4, 1.0 + 0.1 * q)]
bd(13.5, E, T(13.5, 960, 250, 72, "speed × 2  →  punch × 4", c="red", d=0.2))
# 14 rough estimate 1 mg
d_, di = dusty(14, 600, 540, 0.6)
bd(14, d_, T(14, 1300, 300, 52, "our rough estimate", c="muted", d=0.1), BIG(14, 1300, 520, "1 mg", c="blue", d=0.3, s=140), icon(14, "magnifier", 600, 540, 340, 0.2, mv="wig"))
# 14.5 2,000 joules
bd(14.5, BIG(14.5, 960, 450, "≈ 2,000 J", c="red", d=0.1, s=170), [e for q in range(4) for e in icon(14.5, "flame", 360 + 400 * q, 780, 130, 0.2 + 0.1 * q, c="red", mv="wig")])
# 15 more energy
bd(15, bar(15, 600, 820, 240, 520, "red", d=0.1, dur=1.0), T(15, 720, 880, 44, "Dusty"), bar(15, 1000, 820, 240, 130, "blue", d=0.3), T(15, 1120, 880, 44, "pistol bullet"),
   T(15, 1500, 400, 56, "more energy", c="red", d=0.5))
# 15.5 than a pistol bullet
bd(15.5, bullet(15.5, 300, 500, 1.6, 0.1, dx=900), (d_ := dusty(15.5, 1550, 500, 0.4, hot=True)[0]), [pulse(15.5, d_[0]["id"], 0.6)],
   BIG(15.5, 960, 800, "tiny > bullet", c="red", d=0.5, s=100))
# 16 twist two not friction
hands = uid("hd")
bd(16, BIG(16, 960, 160, "TWIST 2", c="red", d=0.1, s=90), [P(16, "M600,500 L900,500 M600,600 L900,600", c="ink", w=14, idp=hands), wig(16, hands, (750, 550), 6, 5.0)],
   T(16, 750, 760, 52, "friction?", c="muted", d=0.3), cross(16, 1300, 550, d=0.5))
# 16.5 makes it glow
d_, di = dusty(16.5, 960, 560, 1.2, hot=True)
bd(16.5, d_, heat(16.5, 960, 560, 0.2), T(16.5, 960, 860, 60, "so what makes it glow?", c="red", d=0.4))
# 17 air can't get out of the way
d_, di = dusty(17, 1400, 520, 0.9, mood="o")
bd(17, d_, air(17, 1400, 520, 8, 0.1, tx=1220), T(17, 700, 860, 52, "air can't move out of the way", c="blue", d=0.3))
# 17.5 squeezed and scorching
d_, di = dusty(17.5, 1300, 520, 0.9, hot=True)
bd(17.5, d_, heat(17.5, 1110, 520, 0.1), air(17.5, 1300, 520, 8, 0.0, tx=1130), T(17.5, 700, 860, 56, "squeezed + scorching", c="red", d=0.4))
# 18 squeeze hard and fast
pst = uid("pst")
bd(18, [R(18, 500, 360, 600, 300, c="ink", idp=(cy_ := uid("cy"))), bob(18, cy_, 2, 0.8), R(18, 1100, 380, 40, 260, c="ink", fill="ink", idp=pst), sh(18, pst, -420, 0, 0.2, 0.6)],
   air(18, 1180, 510, 6, 0.0, tx=600), T(18, 800, 820, 56, "squeeze hard + fast", c="blue", d=0.3))
# 18.5 thousands of degrees
bd(18.5, BIG(18.5, 1150, 470, "1,000s °C", c="red", d=0.2, s=150), [e for q in range(2) for e in icon(18.5, "flame", 350 + 0 * q, 300 + 350 * q, 150, 0.1 + 0.2 * q, c="red", mv="wig")],
   icon(18.5, "thermometer", 1650, 760, 150, 0.4, c="red", mv="wig"))
# 19 bike pump
pump, hnd = uid("pump"), uid("hnd")
bd(19, [R(19, 860, 360, 120, 440, c="ink", idp=pump), bob(19, pump, 2, 0.8), P(19, "M820,330 L1020,330 M920,330 L920,420", c="ink", w=10, idp=hnd),
        sh(19, hnd, 0, 150, 0.1, 0.3), sh(19, hnd, 0, -150, 0.5, 0.3), sh(19, hnd, 0, 150, 0.9, 0.3)], heat(19, 920, 720, 0.4), T(19, 1450, 500, 60, "bike pump: warm", c="ink", d=0.3))
# 19.5 fast forward
bd(19.5, BIG(19.5, 960, 450, "▶▶ × 1,000,000", c="red", d=0.1, s=120)[:0], BIG(19.5, 960, 450, ">> fast-forward", c="red", d=0.1, s=130),
   [e for q in range(4) for e in icon(19.5, "flame", 360 + 400 * q, 780, 130, 0.2 + 0.1 * q, c="red", mv="wig")])
# 20 boils away atom by atom
d_, di = dusty(20, 700, 520, 1.1, hot=True)
E = []
for q in range(8):
    i = uid("at")
    E += [O(20, 800, 450 + 20 * q, 12, c="red", fill="red", idp=i), pop(20, i, 0.1 * q), sh(20, i, 600 + 30 * q, -200 + 50 * q, 0.15 + 0.1 * q, 0.7)]
bd(20, d_, E, [{"t": "move", "at": 20, "kind": "grow", "targets": [di], "axis": "both", "from": 1.0, "to": 0.5, "pivot": [700, 520], "dur": 1.2, "delay": 0.2}],
   T(20, 960, 880, 52, "atom by atom", c="red", d=0.3))
# 20.5 100 km up
bd(20.5, [P(20.5, "M300,880 Q960,800 1620,880", c="green", w=6, idp=(gr := uid("gr"))), bob(20.5, gr, 2, 0.5)], arr(20.5, 400, 860, 400, 260, c="ink", d=0.1),
   BIG(20.5, 900, 300, "100+ km", c="blue", d=0.3, s=130), streak(20.5, 1600, 200, 1250, 400, 0.4), person(20.5, 1300, 750, 0.6))
# 21 hot atoms glow
E = []
for q in range(10):
    i = uid("gl")
    E += [O(21, 500 + 100 * q, 480 + 60 * ((q * 7) % 3), 26, c="gold", fill="gold" if q % 2 else None, idp=i), pop(21, i, 0.05 * q), pulse(21, i, 0.4 + 0.07 * q)]
bd(21, E, T(21, 960, 820, 60, "hot atoms glow", c="gold", d=0.3))
# 21.5 neon sign
ns = uid("neon")
bd(21.5, [R(21.5, 460, 320, 1000, 380, c="red", idp=ns), pulse(21.5, ns, 0.3), pulse(21.5, ns, 1.0), bob(21.5, ns, 3, 1.0)], BIG(21.5, 960, 560, "OPEN", c="red", d=0.1, s=170),
   icon(21.5, "sun", 1700, 300, 120, 0.4, c="gold", mv="spin"))
# 22 not a rock on fire
rk = uid("rk")
bd(22, [P(22, "M500,560 Q480,420 620,400 Q760,380 780,500 Q800,640 640,660 Q520,660 500,560 Z", c="ink", w=6, fill="muted", idp=rk), bob(22, rk, 5, 1.0)],
   icon(22, "flame", 640, 280, 160, 0.2, c="red", mv="wig"), cross(22, 640, 520, d=0.5), T(22, 1350, 520, 60, "not a rock on fire", c="red", d=0.3))
# 22.5 tube of glowing air
tb = uid("tb")
bd(22.5, [P(22.5, "M300,420 L1600,420 M300,600 L1600,600", c="gold", w=8, idp=tb),
          {"t": "move", "at": 22.5, "kind": "grow", "targets": [tb], "axis": "x", "from": 0.05, "to": 1.0, "pivot": [1600, 510], "dur": 0.8, "delay": 0.1}],
   dusty(22.5, 1650, 510, 0.5, hot=True)[0], T(22.5, 960, 780, 60, "a glowing tube of air", c="gold", d=0.5), BIG(22.5, 960, 920, "kilometers long", c="ink", d=0.7, s=60))
# 23 twist three
d_, di = dusty(23, 700, 560, 1.2, mood="o")
bd(23, BIG(23, 960, 160, "TWIST 3", c="red", d=0.1, s=90), d_, icon(23, "question", 1250, 400, 220, 0.3, c="red", mv="wig"))
# 23.5 streak way bigger
d_, di = dusty(23.5, 400, 700, 0.3, hot=True)
bd(23.5, d_, streak(23.5, 1750, 150, 450, 680, 0.1, w=14), T(23.5, 1250, 700, 60, "way bigger", c="red", d=0.4), T(23.5, 400, 850, 40, "Dusty", c="ink", d=0.5))
# 24 crumb on fingertip
fg = uid("fg")
bd(24, [P(24, "M600,900 L600,500 Q600,380 720,380 Q840,380 840,500 L840,900", c="ink", w=7, idp=fg), bob(24, fg, 4, 0.8)], dusty(24, 720, 360, 0.18)[0],
   icon(24, "magnifier", 1150, 400, 220, 0.3, mv="wig"), T(24, 1350, 760, 52, "lose it on a fingertip", c="ink", d=0.4))
# 24.5 seen 100 km away
bd(24.5, streak(24.5, 1700, 150, 1000, 420, 0.1, w=12), person(24.5, 400, 760, 0.8), arr(24.5, 460, 560, 950, 420, c="muted", d=0.3),
   BIG(24.5, 1250, 750, "100 km", c="blue", d=0.5, s=110))
# 25 half leave trails
E = []
for q in range(4):
    E += streak(25, 1600 - 330 * q, 150 + 40 * q, 1300 - 330 * q, 450 + 40 * q, 0.1 * q, c="gold" if q % 2 else "blue")
bd(25, E, BIG(25, 960, 760, "1 in 2", c="gold", d=0.4, s=130))
# 25.5 trails hang
tr = uid("tr")
bd(25.5, [P(25.5, "M1500,200 Q1200,350 1100,320 Q900,300 700,520", c="gold", w=10, idp=tr), pop(25.5, tr, 0.0), wig(25.5, tr, (1100, 360), 10, 0.8), pulse(25.5, tr, 0.6)],
   T(25.5, 960, 820, 56, "glowing trails linger", c="gold", d=0.3), icon(25.5, "clock", 400, 400, 150, 0.2, mv="spin"))
# 26 none reach the ground
bd(26, [P(26, "M200,880 L1720,880", c="green", w=6, idp=(gr := uid("gr"))), bob(26, gr, 2, 0.5)], shower(26, 5, 0.0, x0=1700, y0=120), BIG(26, 960, 700, "0", c="red", d=0.4, s=150),
   T(26, 960, 820, 48, "reach the ground", c="ink", d=0.5))
# 26.5 Dusty gone
d_, di = dusty(26.5, 960, 400, 1.0, hot=True)
bd(26.5, d_, [{"t": "move", "at": 26.5, "kind": "grow", "targets": [di + "*"], "axis": "both", "from": 1.0, "to": 0.05, "pivot": [960, 400], "dur": 1.0, "delay": 0.3}],
   dust_cloud(26.5, 960, 400, 10, 300, 0.5, c="gold"), T(26.5, 960, 820, 60, "gone. poof.", c="red", d=0.6))
# 27 before dawn
bd(27, icon(27, "moon", 500, 400, 200, 0.0, c="gold", mv="bob"), icon(27, "clock", 1000, 400, 200, 0.2, mv="spin"), T(27, 1450, 400, 56, "before dawn", c="blue", d=0.3),
   person(27, 960, 760, 0.7))
# 27.5 away from city lights
E = []
for q in range(4):
    i = uid("bld")
    E += [R(27.5, 300 + 120 * q, 900 - 150 - 60 * q, 100, 150 + 60 * q, c="ink", idp=i), pop(27.5, i, 0.05 * q), bob(27.5, i, 2, 1.0 + 0.1 * q)]
bd(27.5, E, cross(27.5, 500, 500, d=0.4), person(27.5, 1400, 760, 0.8), shower(27.5, 3, 0.4, x0=1700, y0=200), arr(27.5, 900, 760, 1250, 760, c="green", d=0.3))
# 28 Moon sets 2 am
mn = icon(28, "moon", 800, 300, 200, 0.0, c="gold", mv="bob")
bd(28, mn, [sh(28, mn[0]["id"], 300, 500, 0.3, 1.2)], [P(28, "M200,820 L1720,820", c="green", w=6, idp=(hz := uid("hz"))), bob(28, hz, 2, 0.5)],
   BIG(28, 1450, 400, "2 a.m.", c="blue", d=0.3, s=120))
# 28.5 darker after
bd(28.5, [R(28.5, 400, 250, 1120, 500, c="ink", fill="ink", idp=(sky := uid("sky"))), pop(28.5, sky, 0.0)], shower(28.5, 5, 0.3, x0=1450, y0=290),
   T(28.5, 960, 880, 56, "darker = more streaks", c="ink", d=0.4))
# 29 look anywhere
bd(29, person(29, 960, 760, 1.0), [e for q in range(4) for e in streak(29, 300 + 400 * q, 150, 200 + 400 * q, 400, 0.1 + 0.15 * q, c="gold")],
   T(29, 960, 960, 52, "look anywhere", c="ink", d=0.3))
# 29.5 radiate from Orion
E = []
for q in range(6):
    ang = q * 1.047
    import math
    E += streak(29.5, 960 + 120 * math.cos(ang), 480 + 120 * math.sin(ang), 960 + 420 * math.cos(ang), 480 + 360 * math.sin(ang), 0.2 + 0.1 * q, c="gold" if q % 2 else "blue")
bd(29.5, orion(29.5, 960, 480, 0.6), E, T(29.5, 960, 940, 52, "out of Orion", c="blue", d=0.4))
# 30 20 minutes
ey = icon(30, "eye", 600, 480, 260, 0.0, mv="wig")
bd(30, ey, [pulse(30, ey[0]["id"], 0.6)], BIG(30, 1300, 450, "20 min", c="blue", d=0.3, s=140), icon(30, "clock", 1300, 750, 140, 0.5, mv="spin"))
# 30.5 phone away
ph = icon(30.5, "phone", 700, 500, 260, 0.0, mv="wig")
bd(30.5, ph, [sh(30.5, ph[0]["id"], 0, 600, 0.4, 0.6)], cross(30.5, 700, 480, d=0.3), T(30.5, 1350, 500, 60, "phone away", c="red", d=0.3))
# 31 15-20 an hour
bd(31, T(31, 960, 200, 60, "friendly fine print", c="ink", d=0.1), BIG(31, 960, 480, "15–20 / hour", c="blue", d=0.3, s=130), shower(31, 3, 0.5, x0=1700, y0=650))
# 31.5 patience and blanket
bk = uid("bk")
bd(31.5, [P(31.5, "M500,700 Q700,560 960,640 Q1200,720 1420,600 L1420,820 L500,820 Z", c="blue", w=6, fill="blue", idp=bk), pop(31.5, bk, 0.0), wig(31.5, bk, (960, 820), 3, 1.0)],
   person(31.5, 960, 560, 0.6), icon(31.5, "moon", 1550, 250, 140, 0.2, c="gold"), T(31.5, 700, 300, 56, "patience + blanket", c="blue", d=0.3))
# 32 every October
cal = uid("cal")
bd(32, [R(32, 560, 260, 400, 440, c="ink", idp=cal), P(32, "M560,360 L960,360", c="red", w=10, idp=cal), pop(32, cal, 0.0), wig(32, cal, (760, 260), 4, 1.0)],
   T(32, 760, 540, 72, "OCT", c="red", d=0.2), [P(32, "M1300,500 A160,160 0 1,1 1460,340", c="green", w=7, idp=(lp := uid("lp"))), spin(32, lp, (1300, 340 + 160), 40)],
   T(32, 1300, 860, 52, "every year", c="green", d=0.4))
# 32.5 Halley returns 2061
c_, ci = comet(32.5, 1300, 500, 1.1, dx=-500, dy=0)
bd(32.5, c_, BIG(32.5, 700, 760, "2061", c="blue", d=0.4, s=170), star(32.5, 400, 300, 0.5, r=40), n=3)
# 33 Dusty waited thousands of years
d_, di = dusty(33, 700, 600, 1.4)
bd(33, d_, icon(33, "clock", 1300, 420, 200, 0.1, mv="spin"), T(33, 1350, 720, 56, "thousands of years", c="ink", d=0.3), n=3)
# 33.5 one second, glorious
d_, di = dusty(33.5, 600, 360, 0.7, hot=True)
bd(33.5, d_, [sh(33.5, di + "*", 900, 400, 0.2, 0.8)], streak(33.5, 600, 360, 1500, 760, 0.2, w=14), BIG(33.5, 900, 860, "1 second", c="gold", d=0.5, s=100),
   [e for q in range(4) for e in star(33.5, 1300 + 120 * q, 250 + 50 * (q % 2), 0.6 + 0.1 * q, r=35)], n=3)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"2061": "twenty sixty-one", "2 a.m.": "two A M"})
