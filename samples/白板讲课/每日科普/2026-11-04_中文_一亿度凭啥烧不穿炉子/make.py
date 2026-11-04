"""每日科普 2026-11-04（中文）：《一亿度的火，凭啥烧不穿炉子？》
热点：新浪科学热点小时报 2026-11-04 18 时第 1 条（抖音博主探访“人造太阳”等大国重器）；B 站“超级科学晚”上讲人造太阳（网易 2026-11-02）。
事实：
- EAST（东方超环，合肥）2025 年 1 月实现 1066 秒高约束模等离子体运行，“亿度千秒”（光明网、人民网科普中国、新华网 2025-01-20/21）。
- B 站超级科学晚上说：一瓶海水里的聚变能，够开车约一千公里（网易报道，属晚会上的说法）。
- 教科书：太阳核心约一千五百万度；带电粒子在磁场里绕磁力线打转（洛伦兹力）；托卡马克是环形磁笼；EAST 是全超导装置，超导线圈用液氦冷到约零下 269 度。
估算（片中说是估算）：聚变堆里的等离子体比空气稀几十万倍（典型密度约 10^20 个/立方米，空气约 2.5×10^25）。
推测（片中说是推测）：离商业发电还要很多年。
比喻（我们的）：磁力线 = 过山车轨道；仙女棒火花上千度却不烫手。
出处：
- https://k.sina.com.cn/article_7857201856_1d45362c001908tmtk.html
- https://www.163.com/dy/article/LAMIHQHU051196HN.html
- https://politics.gmw.cn/2025-01/20/content_37809150.htm
- http://kpzg.people.com.cn/n1/2025/0121/c404214-40405783.html
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_plasma, stick  # noqa: E402

S = [
 ("一亿度的火，|就关在合肥的一个“炉子”里。", "A fire at one hundred million degrees | is locked inside a 'furnace' in Hefei."),
 ("一亿度，|是太阳核心的六七倍。", "A hundred million degrees. | Six or seven times the core of the Sun."),
 ("这几天，抖音博主钻进“人造太阳”拍视频，|上了科学热榜第一。", "This week, Douyin creators filmed inside China's 'artificial sun', | topping the science trending list."),
 ("B站的科学晚会上，|人造太阳也是主角。", "At Bilibili's science night, | the artificial sun was a star too."),
 ("它叫东方超环，|2025年1月，跑出了“亿度千秒”。", "It's called EAST. | In January 2025 it held its plasma for over a thousand seconds."),
 ("一千零六十六秒，|将近十八分钟。", "One thousand sixty-six seconds, | almost eighteen minutes."),
 ("今天的烧脑问题：|一亿度，什么墙不化？凭啥烧不穿炉子？", "Today's brain teaser: | at a hundred million degrees, every wall melts. Why doesn't the furnace burn through?"),
 ("先认识主角：|一亿度的小火球，亿亿。", "Meet our hero: | a tiny hundred-million-degree fireball, Yiyi."),
 ("这么热，原子都被扯散了，|电子和原子核各跑各的。", "At that heat, atoms get torn apart: | electrons and nuclei run separately."),
 ("这团带电的“汤”，|叫等离子体。", "This charged soup | is called plasma."),
 ("反转一：|炉子的墙，根本不碰火。", "Twist one: | the wall never touches the fire."),
 ("带电的粒子一进磁场，|就只能绕着磁力线打转。", "Charged particles in a magnetic field | can only spiral around the field lines."),
 ("磁力线就像过山车的轨道，|车只能顺着轨道跑，跳不出去。", "Field lines are like roller-coaster tracks. | The cars follow the track and can't jump off."),
 ("把轨道首尾接成一个圈，|就是个甜甜圈形的磁笼子。", "Join the track into a loop | and you get a doughnut-shaped magnetic cage."),
 ("这种笼子，|叫托卡马克。", "This cage | is called a tokamak."),
 ("火球在中间飘着，|离墙远远的。", "The fireball floats in the middle, | far from the wall."),
 ("太阳靠自己巨大的引力压住火，|我们只能靠磁场。", "The Sun holds its fire with huge gravity. | We only have magnets."),
 ("也正因为没有太阳那么大的压力，|温度只好比太阳高得多。", "And without the Sun's crushing pressure, | we have to go much hotter than the Sun."),
 ("反转二：|一亿度，其实没多少热。", "Twist two: | a hundred million degrees isn't much heat."),
 ("温度是粒子跑得多快，|热量还要看粒子有多少。", "Temperature is how fast particles move. | Heat also depends on how many there are."),
 ("估算一下：炉子里的等离子体，|比空气还稀几十万倍。", "A rough estimate: the plasma is | a few hundred thousand times thinner than air."),
 ("就像过年的仙女棒，|火花上千度，落在手上却不烫。", "Like a sparkler: | sparks over a thousand degrees, yet they don't burn your hand."),
 ("火花太小、太少，|热量还没传过来就没了。", "The sparks are too small and too few. | Their heat is gone before it reaches you."),
 ("所以万一磁笼子失灵，|火球一碰墙，自己先凉了。", "So if the cage ever fails, | the fireball hits the wall and cools itself first."),
 ("人造太阳不会像炸弹那样炸，|它只会“熄火”。", "An artificial sun can't explode like a bomb. | It just goes out."),
 ("当然墙也会受点伤，|所以墙要用耐高温的钨来做。", "The wall does get hurt a little, | so it's armored with tough tungsten."),
 ("反转三，最反直觉：|最热的旁边，就是最冷的。", "Twist three, the weirdest: | right next to the hottest thing is the coldest."),
 ("磁笼子靠超导线圈，|要冷到零下二百六十九度。", "The cage uses superconducting coils | chilled to minus two hundred sixty-nine degrees."),
 ("一边一亿度，一边接近绝对零度，|中间就隔一层真空和几层墙。", "A hundred million degrees on one side, almost absolute zero on the other, | with just a vacuum and a few layers between."),
 ("就像热水瓶，|中间抽成真空，热就传不过去。", "It's like a thermos: | the vacuum in between stops the heat."),
 ("费这么大劲图啥？|燃料就在海水里。", "Why go to all this trouble? | The fuel is in seawater."),
 ("B站晚会上说：一瓶海水里的聚变能，|够开车跑一千公里。", "At Bilibili's science night they said: the fusion energy in one bottle of seawater | could drive a car a thousand kilometers."),
 ("友情提示：现在还发不出能卖的电，|我们推测还要很多年。", "Fine print: it can't sell electricity yet. | Our guess: that's still many years away."),
 ("比稀薄几十万倍，是我们的估算；|一千公里，是晚会上的说法。", "Thinner by hundreds of thousands is our estimate. | The thousand kilometers is what the show said."),
 ("所以，一亿度凭啥烧不穿炉子？|因为火碰不到墙，而且它太稀了。", "So why doesn't a hundred million degrees burn through? | The fire never touches the wall, and it's very thin."),
 ("人造太阳的秘密，|不是更结实的炉子，是一个看不见的笼子。", "The secret of the artificial sun | is not a stronger furnace, but an invisible cage."),
]
TITLE = {"zh": "一亿度的火，凭啥烧不穿炉子？", "en": "Why Doesn't 100 Million Degrees Melt the Furnace?"}

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
    return T(a, x, y, s, text, c=c, d=d)


def big(a, x, y, text, c="red", d=0.0, s=140):
    return BIG(a, x, y, text, c=c, d=d, s=s)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def yy(a, x, y, k=1.0, d=0.0, mood="happy"):
    i = uid("yy")
    return cute_plasma(x, y, k, a, idp=i, mood=mood) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]


def man(a, x, y, k=1.4, d=0.0, arms="down"):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 6, "hz": 1.6}]


def torus(a, x, y, rx=380, ry=200, d=0.0, n=6, c="blue"):
    """甜甜圈磁笼：两圈椭圆 + 一串小点一直绕着跑。"""
    i, j = uid("to"), uid("tp")
    E = [{"t": "ellipse", "at": a, "id": i, "x": x - rx, "y": y - ry, "w": 2 * rx, "h": 2 * ry, "c": c, "sw": 8},
         {"t": "ellipse", "at": a, "id": i, "x": x - rx * 0.45, "y": y - ry * 0.4, "w": 0.9 * rx, "h": 0.8 * ry, "c": c, "sw": 6}, pop(a, i, d)]
    import math
    for q in range(n):
        g = 2 * math.pi * q / n
        E.append(O(a, x + 0.72 * rx * math.cos(g), y + 0.7 * ry * math.sin(g), 16, c="red", fill="red", idp=j))
    E += [pop(a, j, d + 0.2), spin(a, j, (x, y), 30)]
    return E


def spiral(a, x0, y, x1, d=0.0, c="blue"):
    """一根磁力线 + 一个粒子沿着它边绕边走。"""
    i, j = uid("fl"), uid("sp")
    E = [P(a, f"M{x0},{y} L{x1},{y}", c=c, w=6, idp=i), pop(a, i, d)]
    n = int((x1 - x0) / 60)
    p = f"M{x0},{y}" + "".join(f" Q{x0 + 60 * q + 30},{y + (-70 if q % 2 else 70)} {x0 + 60 * q + 60},{y}" for q in range(n))
    E += [P(a, p, c="red", w=4, idp=j), pop(a, j, d + 0.2), wig(a, j, ((x0 + x1) / 2, y), 4, 2.5)]
    k = uid("pt")
    E += [O(a, x0, y, 20, c="red", fill="red", idp=k), pop(a, k, d + 0.3), sh(a, k, x1 - x0, 0, d + 0.4, 2.2)]
    return E


def dots(a, x, y, n=8, d=0.0, c="red", fast=True, w=300):
    E = []
    for q in range(n):
        i = uid("dt")
        px, py = x + (q * 97) % w, y + (q * 61) % (w * 0.7)
        E += [O(a, px, py, 14, c=c, fill=c, idp=i), pop(a, i, d + 0.05 * q), wig(a, i, (px, py), 22 if fast else 5, 5 if fast else 1)]
    return E


def wall(a, x, y, h=500, d=0.0, c="ink"):
    i = uid("wl")
    E = [R(a, x, y - h / 2, 60, h, c=c, fill="muted", idp=i), pop(a, i, d)]
    for q in range(5):
        E.append(P(a, f"M{x},{y - h / 2 + 100 * q + 30} L{x + 60},{y - h / 2 + 100 * q + 80}", c=c, w=3, idp=i))
    return E


def coil(a, x, y, d=0.0, c="blue"):
    i = uid("co")
    E = [R(a, x - 60, y - 200, 120, 400, c=c, idp=i, sw=8), pop(a, i, d)]
    for q in range(6):
        E.append(P(a, f"M{x - 60},{y - 170 + 65 * q} L{x + 60},{y - 140 + 65 * q}", c=c, w=5, idp=i))
    E.append(wig(a, i, (x, y), 2, 3))
    return E


def snow(a, x, y, d=0.0, s=1.0):
    i = uid("sn")
    E = [P(a, f"M{x},{y - 60 * s} L{x},{y + 60 * s} M{x - 52 * s},{y - 30 * s} L{x + 52 * s},{y + 30 * s} M{x - 52 * s},{y + 30 * s} L{x + 52 * s},{y - 30 * s}", c="blue", w=7, idp=i), pop(a, i, d), spin(a, i, (x, y), 30)]
    return E


def thermo(a, x, y, d=0.0, up=True, c="red"):
    i, j = uid("tm"), uid("tl")
    h = 360
    E = [R(a, x - 30, y - h, 60, h, c="ink", idp=i, sw=6), O(a, x, y + 30, 50, c="ink", fill=c, idp=i), pop(a, i, d),
         R(a, x - 18, y - (h - 30 if up else 60), 36, h - 30 if up else 60, c=c, fill=c, idp=j)]
    E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y], "dur": 1.0, "delay": d + 0.2})
    return E


def sparkler(a, x, y, d=0.0):
    i = uid("sk")
    E = [P(a, f"M{x},{y} L{x - 120},{y + 300}", c="ink", w=8, idp=i), pop(a, i, d)]
    for q in range(6):
        j = uid("sp")
        import math
        g = 2 * math.pi * q / 6
        E += [P(a, f"M{x},{y} L{x + 90 * math.cos(g)},{y + 90 * math.sin(g)}", c="gold", w=5, idp=j), pop(a, j, d + 0.1 + 0.05 * q),
              wig(a, j, (x, y), 10, 4)]
    return E


def bottle(a, x, y, d=0.0):
    i, j = uid("bt"), uid("bw")
    E = [R(a, x - 60, y - 220, 120, 220, c="ink", idp=i, sw=6), R(a, x - 25, y - 270, 50, 50, c="ink", idp=i, sw=6), pop(a, i, d),
         R(a, x - 50, y - 150, 100, 145, c="blue", fill="blue", idp=j)]
    E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y], "dur": 0.8, "delay": d + 0.2})
    E.append(wig(a, i, (x, y), 4, 1.5))
    return E


def furnace(a, x, y, d=0.0, k=1.0):
    i = uid("fu")
    E = [R(a, x - 260 * k, y - 300 * k, 520 * k, 330 * k, c="ink", fill="paper", idp=i, sw=8),
         P(a, f"M{x - 200 * k},{y + 30 * k} L{x - 220 * k},{y + 90 * k} M{x + 200 * k},{y + 30 * k} L{x + 220 * k},{y + 90 * k}", c="ink", w=8, idp=i), pop(a, i, d), wig(a, i, (x, y), 2, 2)]
    return E


# ---------- boards ----------
bd(0, yy(0, 960, 600, 1.8, 0.0), big(0, 960, 220, "1亿℃", c="red", d=0.2, s=150), ic(0, "flame", 500, 650, 170, 0.3, mv="wig", c="red"), ic(0, "flame", 1420, 650, 170, 0.4, mv="wig", c="red"))
bd(0.5, furnace(0.5, 960, 750, 0.0, 1.3), yy(0.5, 960, 560, 0.8, 0.2), ic(0.5, "map_pin", 1500, 350, 150, 0.3, mv="bob", c="red"), t(0.5, 1500, 520, 64, "合肥", d=0.4))
bd(1, ic(1, "sun", 520, 550, 280, 0.0, mv="spin", c="gold"), t(1, 520, 850, 56, "太阳核心 1500万℃", d=0.2), big(1, 1350, 450, "1亿℃", c="red", d=0.3, s=140), thermo(1, 1700, 900, 0.4))
bd(1.5, bar(1.5, 650, 950, 160, 90, "gold", 0.0), t(1.5, 730, 1000, 50, "太阳", d=0.0), bar(1.5, 950, 950, 160, 600, "red", 0.3), t(1.5, 1030, 1000, 50, "人造太阳", d=0.3), big(1.5, 1450, 400, "×6~7", c="red", d=0.6, s=140), yy(1.5, 1450, 700, 0.6, 0.5))
bd(2, ic(2, "phone", 600, 550, 300, 0.0, mv="wig"), yy(2, 600, 520, 0.5, 0.2), big(2, 1350, 380, "热榜 No.1", c="red", d=0.3, s=120), ic(2, "signal", 1350, 700, 150, 0.4, mv="bob", c="blue"))
bd(2.5, man(2.5, 500, 900, 1.6, 0.0, arms="up"), ic(2.5, "phone", 750, 500, 140, 0.2, mv="wig"), furnace(2.5, 1350, 800, 0.3, 0.9), t(2.5, 1350, 300, 64, "钻进人造太阳", d=0.4))
bd(3, ic(3, "speaker", 500, 550, 220, 0.0, mv="wig"), t(3, 1250, 350, 80, "B站 科学晚会", c="blue", d=0.2), star(3, 1250, 600, 0.3, r=40), star(3, 1450, 650, 0.5, r=26))
bd(3.5, man(3.5, 450, 900, 1.5, 0.0, arms="up"), yy(3.5, 1100, 550, 1.3, 0.2), t(3.5, 1100, 850, 64, "主角", c="red", d=0.4), ic(3.5, "sun", 1550, 400, 150, 0.4, mv="spin", c="gold"))
bd(4, furnace(4, 700, 800, 0.0, 1.1), t(4, 1450, 350, 90, "东方超环", d=0.2), t(4, 1450, 500, 60, "EAST", c="blue", d=0.3), ic(4, "building", 1450, 750, 150, 0.4, mv="bob"))
bd(4.5, big(4.5, 960, 300, "亿度千秒", c="red", d=0.0, s=140), ic(4.5, "clock", 600, 700, 200, 0.2, mv="spin"), yy(4.5, 1300, 700, 0.9, 0.3), t(4.5, 960, 950, 50, "2025年1月", c="muted", d=0.4))
bd(5, big(5, 960, 380, "1066 秒", c="red", d=0.0, s=150), ic(5, "clock", 500, 750, 170, 0.2, mv="spin"), ic(5, "clock", 1420, 750, 170, 0.3, mv="spin"))
bd(5.5, big(5.5, 1200, 400, "≈ 18 分钟", c="ink", d=0.0, s=130), ic(5.5, "clock", 500, 500, 260, 0.1, mv="spin"), yy(5.5, 1200, 780, 0.8, 0.3))
bd(6, big(6, 1150, 330, "烧脑问题", c="red", d=0.0, s=120), ic(6, "question", 450, 450, 260, 0.2, mv="wig", c="red"), yy(6, 1150, 700, 1.0, 0.3, mood="o"))
bd(6.5, furnace(6.5, 700, 800, 0.0, 1.1), yy(6.5, 700, 620, 0.8, 0.2), ic(6.5, "flame", 1100, 600, 150, 0.4, mv="wig", c="red"), t(6.5, 1450, 400, 70, "烧不穿？", c="red", d=0.5), ic(6.5, "question", 1450, 650, 140, 0.5, mv="wig", c="red"))
bd(7, man(7, 500, 900, 1.6, 0.0, arms="up"), t(7, 1300, 300, 70, "认识主角", d=0.2), star(7, 1600, 500, 0.4, r=40))
bd(7.5, yy(7.5, 800, 560, 2.0, 0.0), t(7.5, 1450, 400, 110, "亿亿", c="red", d=0.3), star(7.5, 1450, 600, 0.5, r=40))
bd(8, O(8, 700, 550, 140, c="ink", idp="at1"), O(8, 700, 550, 40, c="red", fill="red", idp="nu1"), O(8, 840, 550, 18, c="blue", fill="blue", idp="el1"), spin(8, "el1", (700, 550), 90),
   ic(8, "flame", 700, 850, 140, 0.2, mv="wig", c="red"), t(8, 1350, 400, 70, "原子被扯散", c="red", d=0.3), arr(8, 900, 550, 1150, 550, c="red", d=0.4))
bd(8.5, dots(8.5, 450, 400, 7, 0.0, c="red"), dots(8.5, 1150, 400, 7, 0.2, c="blue"), t(8.5, 600, 850, 56, "原子核", c="red", d=0.3), t(8.5, 1300, 850, 56, "电子", c="blue", d=0.4))
bd(9, dots(9, 500, 400, 10, 0.0, c="red"), dots(9, 560, 440, 10, 0.1, c="blue"), big(9, 1350, 400, "带电的汤", c="ink", d=0.3, s=100), ic(9, "water", 1350, 700, 150, 0.4, mv="wig", c="blue"))
bd(9.5, yy(9.5, 700, 580, 1.4, 0.0), big(9.5, 1350, 400, "等离子体", c="red", d=0.2, s=120), dots(9.5, 1150, 650, 6, 0.4))
bd(10, big(10, 960, 300, "反转一", c="red", d=0.0, s=140), wall(10, 1300, 700, 450, 0.2), yy(10, 700, 700, 1.0, 0.3))
bd(10.5, wall(10.5, 1400, 650, 500, 0.0), yy(10.5, 700, 650, 1.1, 0.1), cross(10.5, 1100, 650, d=0.4), t(10.5, 1000, 950, 60, "墙不碰火", c="blue", d=0.5))
bd(11, ic(11, "magnet", 500, 500, 220, 0.0, mv="wig", c="red"), spiral(11, 750, 600, 1700, 0.2), t(11, 1200, 300, 60, "进了磁场", c="blue", d=0.2))
bd(11.5, spiral(11.5, 250, 400, 1650, 0.0), spiral(11.5, 250, 750, 1650, 0.3), t(11.5, 960, 950, 60, "绕着磁力线打转", c="red", d=0.5))
bd(12, P(12, "M200,700 Q600,300 960,600 Q1300,900 1700,500", c="blue", w=10, idp="tk1"), pop(12, "tk1", 0.0), ic(12, "car", 400, 560, 150, 0.2, mv="wig"), sh(12, ["ic%dz" % 0], 0, 0, 0, 0.1) if False else [],
   t(12, 1300, 850, 70, "像过山车轨道", d=0.3), ic(12, "flag" if False else "map_pin", 1650, 420, 120, 0.4, mv="bob", c="red"))
bd(12.5, P(12.5, "M200,600 Q600,250 960,550 Q1300,850 1700,450", c="blue", w=10, idp="tk2"), pop(12.5, "tk2", 0.0), dots(12.5, 500, 420, 4, 0.2), cross(12.5, 960, 300, d=0.4), t(12.5, 960, 900, 64, "跳不出去", c="red", d=0.5))
bd(13, P(13, "M300,600 L1600,600", c="blue", w=10, idp="ln1"), pop(13, "ln1", 0.0), rot(13, "ln1", 30, (960, 600), 0.3, 0.6), arr(13, 1400, 350, 1600, 550, c="red", d=0.5), t(13, 960, 300, 64, "首尾接成圈", d=0.3))
bd(13.5, torus(13.5, 960, 600, 420, 230, 0.0), big(13.5, 960, 200, "甜甜圈磁笼", c="blue", d=0.3, s=100))
bd(14, torus(14, 700, 600, 360, 200, 0.0, c="ink"), big(14, 1450, 450, "托卡马克", c="red", d=0.2, s=110), ic(14, "magnet", 1450, 750, 150, 0.4, mv="wig", c="red"))
bd(14.5, t(14.5, 960, 300, 70, "tokamak", c="blue", d=0.0), torus(14.5, 960, 700, 380, 180, 0.1), yy(14.5, 1600, 650, 0.6, 0.3))
bd(15, torus(15, 960, 600, 450, 260, 0.0), yy(15, 960, 600, 0.6, 0.2), t(15, 960, 950, 60, "飘在中间", d=0.4))
bd(15.5, wall(15.5, 250, 600, 600, 0.0), wall(15.5, 1610, 600, 600, 0.1), yy(15.5, 960, 600, 1.0, 0.2), arr(15.5, 820, 600, 400, 600, c="blue", d=0.4), arr(15.5, 1100, 600, 1520, 600, c="blue", d=0.5))
bd(16, ic(16, "sun", 600, 550, 320, 0.0, mv="spin", c="gold"), arr(16, 600, 200, 600, 380, c="ink", d=0.2), arr(16, 950, 550, 800, 550, c="ink", d=0.3), t(16, 1350, 400, 70, "引力压住", d=0.4))
bd(16.5, ic(16.5, "magnet", 500, 550, 260, 0.0, mv="wig", c="red"), torus(16.5, 1300, 600, 330, 180, 0.2), t(16.5, 1300, 280, 64, "我们只有磁场", c="blue", d=0.4))
bd(17, ic(17, "sun", 600, 550, 260, 0.0, mv="spin", c="gold"), cross(17, 1250, 550, d=0.3), t(17, 1250, 350, 64, "没有那么大的压力", d=0.2), dots(17, 1100, 700, 5, 0.4, fast=False))
bd(17.5, thermo(17.5, 600, 900, 0.0), big(17.5, 1300, 400, "只好更热", c="red", d=0.2, s=120), yy(17.5, 1300, 700, 0.9, 0.3))
bd(18, big(18, 960, 300, "反转二", c="red", d=0.0, s=140), yy(18, 600, 700, 0.9, 0.2), ic(18, "thermometer", 1350, 700, 200, 0.3, mv="wig"))
bd(18.5, big(18.5, 960, 330, "没多少热", c="blue", d=0.0, s=130), yy(18.5, 600, 750, 0.8, 0.2), dots(18.5, 1150, 650, 3, 0.3, fast=True))
bd(19, dots(19, 400, 400, 8, 0.0, fast=True), t(19, 550, 900, 64, "温度 = 跑得快", c="red", d=0.2), ic(19, "wind", 1400, 550, 200, 0.3, mv="wig"))
bd(19.5, dots(19.5, 400, 400, 3, 0.0, fast=True), t(19.5, 500, 850, 56, "少", d=0.1), dots(19.5, 1150, 350, 16, 0.2, fast=True, w=450), t(19.5, 1350, 850, 56, "多", d=0.3), big(19.5, 960, 200, "热量看个数", c="red", d=0.5, s=90))
bd(20, t(20, 960, 230, 56, "估算", c="muted", d=0.0), R(20, 300, 350, 550, 500, c="ink", sw=6), dots(20, 360, 400, 3, 0.1), R(20, 1070, 350, 550, 500, c="ink", sw=6), dots(20, 1100, 400, 18, 0.2, c="blue", fast=False, w=480),
   t(20, 575, 950, 50, "等离子体", d=0.3), t(20, 1345, 950, 50, "空气", d=0.3))
bd(20.5, big(20.5, 960, 400, "稀几十万倍", c="red", d=0.0, s=130), dots(20.5, 500, 650, 2, 0.2), ic(20.5, "wind", 1400, 750, 150, 0.3, mv="wig"))
bd(21, sparkler(21, 700, 450, 0.0), t(21, 1350, 300, 80, "仙女棒", d=0.2), star(21, 1350, 500, 0.3, r=36), star(21, 1550, 550, 0.4, r=24))
bd(21.5, sparkler(21.5, 600, 400, 0.0), man(21.5, 1150, 900, 1.5, 0.1, arms="up"), big(21.5, 1550, 330, "上千度", c="red", d=0.3, s=100), check(21.5, 1550, 600, d=0.6))
bd(22, sparkler(22, 600, 400, 0.0), dots(22, 900, 450, 4, 0.2, c="gold"), t(22, 1350, 700, 64, "太小、太少", d=0.3))
bd(22.5, dots(22.5, 500, 400, 5, 0.0, c="gold"), arr(22.5, 900, 550, 1250, 550, c="red", d=0.2), cross(22.5, 1400, 550, d=0.5), t(22.5, 1350, 850, 56, "热量还没传过来", d=0.3))
bd(23, torus(23, 800, 600, 360, 200, 0.0), cross(23, 800, 600, d=0.3), ic(23, "magnet", 1450, 550, 180, 0.2, mv="wig", c="red"), t(23, 1450, 850, 60, "万一失灵", c="red", d=0.4))
bd(23.5, wall(23.5, 1300, 600, 550, 0.0), yy(23.5, 700, 600, 0.9, 0.1, mood="o"), sh(23.5, [], 0, 0, 0, 0.1) if False else [], thermo(23.5, 1650, 900, 0.3, up=False, c="blue"), t(23.5, 900, 950, 60, "自己先凉了", c="blue", d=0.5))
bd(24, ic(24, "flame", 600, 550, 260, 0.0, mv="wig", c="red"), cross(24, 600, 550, d=0.3), t(24, 1300, 450, 70, "不会爆炸", d=0.2), yy(24, 1300, 750, 0.7, 0.4))
bd(24.5, yy(24.5, 700, 600, 1.3, 0.0, mood="sad"), big(24.5, 1350, 450, "只会熄火", c="blue", d=0.3, s=120), ic(24.5, "moon", 1350, 750, 150, 0.4, mv="bob"))
bd(25, wall(25, 800, 600, 550, 0.0), yy(25, 450, 600, 0.7, 0.1), t(25, 1350, 450, 64, "墙受点伤", d=0.3), ic(25, "magnifier", 1350, 700, 150, 0.4, mv="wig"))
bd(25.5, wall(25.5, 600, 600, 600, 0.0, c="ink"), big(25.5, 1250, 400, "钨", c="ink", d=0.2, s=160), t(25.5, 1250, 600, 56, "耐高温", c="red", d=0.4), ic(25.5, "flame", 350, 600, 140, 0.3, mv="wig", c="red"))
bd(26, big(26, 960, 300, "反转三", c="red", d=0.0, s=140), yy(26, 600, 700, 0.8, 0.2), snow(26, 1350, 700, 0.3, 1.3))
bd(26.5, yy(26.5, 600, 600, 1.0, 0.0), snow(26.5, 1350, 600, 0.2, 1.5), t(26.5, 600, 900, 60, "最热", c="red", d=0.3), t(26.5, 1350, 900, 60, "最冷", c="blue", d=0.4))
bd(27, coil(27, 600, 600, 0.0), coil(27, 900, 600, 0.1), t(27, 1400, 400, 64, "超导线圈", c="blue", d=0.2), ic(27, "magnet", 1400, 650, 150, 0.3, mv="wig", c="red"))
bd(27.5, big(27.5, 1150, 400, "-269℃", c="blue", d=0.0, s=150), thermo(27.5, 500, 900, 0.1, up=False, c="blue"), snow(27.5, 1150, 700, 0.3))
bd(28, yy(28, 500, 600, 0.9, 0.0), wall(28, 900, 600, 500, 0.1), snow(28, 1400, 600, 0.2, 1.2), t(28, 500, 900, 56, "1亿℃", c="red", d=0.3), t(28, 1400, 900, 56, "接近绝对零度", c="blue", d=0.4))
bd(28.5, yy(28.5, 400, 600, 0.7, 0.0), R(28.5, 700, 300, 160, 600, c="muted", sw=4), t(28.5, 780, 950, 50, "真空", c="muted", d=0.2), wall(28.5, 1000, 600, 600, 0.3), coil(28.5, 1400, 600, 0.4))
bd(29, R(29, 700, 300, 300, 600, c="ink", sw=7), R(29, 740, 340, 220, 520, c="blue", sw=5), ic(29, "flame", 850, 600, 140, 0.2, mv="wig", c="red"), t(29, 1400, 400, 70, "像热水瓶", d=0.3), ic(29, "water", 1400, 650, 140, 0.4, mv="wig", c="blue"))
bd(29.5, R(29.5, 600, 300, 300, 600, c="ink", sw=7), R(29.5, 640, 340, 220, 520, c="muted", sw=4), arr(29.5, 400, 600, 600, 600, c="red", d=0.2), cross(29.5, 750, 600, d=0.4), t(29.5, 1350, 450, 64, "真空挡住热", c="blue", d=0.3), dots(29.5, 1200, 650, 4, 0.5, fast=False))
bd(30, man(30, 600, 900, 1.6, 0.0, arms="up"), ic(30, "question", 600, 300, 150, 0.2, mv="wig", c="red"), t(30, 1350, 450, 70, "图啥？", d=0.3), ic(30, "gear", 1350, 700, 150, 0.4, mv="spin"))
bd(30.5, P(30.5, "M200,800 Q500,720 800,800 Q1100,880 1400,800 Q1600,720 1800,800", c="blue", w=8, idp="sea1"), pop(30.5, "sea1", 0.0), wig(30.5, "sea1", (960, 800), 6, 1.2), bottle(30.5, 700, 700, 0.2), big(30.5, 1300, 400, "燃料在海水里", c="blue", d=0.4, s=90))
bd(31, t(31, 960, 230, 56, "B站晚会上的说法", c="muted", d=0.0), bottle(31, 700, 850, 0.1), arr(31, 850, 650, 1150, 650, c="red", d=0.3), yy(31, 1400, 650, 0.8, 0.4))
bd(31.5, ic(31.5, "car", 500, 650, 260, 0.0, mv="wig"), big(31.5, 1300, 400, "1000 公里", c="red", d=0.2, s=130), ic(31.5, "map_pin", 1300, 700, 150, 0.4, mv="bob", c="red"))
bd(32, big(32, 960, 300, "友情提示", c="blue", d=0.0, s=130), ic(32, "building", 600, 700, 200, 0.2, mv="bob"), cross(32, 1300, 650, d=0.4), t(32, 1300, 900, 56, "还不能卖电", d=0.3))
bd(32.5, ic(32.5, "clock", 600, 550, 240, 0.0, mv="spin"), big(32.5, 1350, 400, "还要很多年", c="ink", d=0.2, s=110), t(32.5, 1350, 600, 56, "我们的推测", c="muted", d=0.3), yy(32.5, 1350, 800, 0.5, 0.4))
bd(33, t(33, 960, 330, 70, "几十万倍：我们的估算", d=0.0), ic(33, "magnifier", 600, 650, 200, 0.2, mv="wig"), dots(33, 1150, 600, 4, 0.3, fast=False))
bd(33.5, t(33.5, 960, 330, 70, "一千公里：晚会上的说法", d=0.0), ic(33.5, "speaker", 600, 650, 200, 0.2, mv="wig"), ic(33.5, "car", 1350, 650, 180, 0.3, mv="wig"))
bd(34, furnace(34, 700, 800, 0.0, 1.1), yy(34, 700, 620, 0.8, 0.1), ic(34, "question", 1400, 400, 180, 0.2, mv="wig", c="red"), t(34, 1400, 650, 64, "凭啥烧不穿？", c="red", d=0.4))
bd(34.5, torus(34.5, 700, 600, 360, 200, 0.0), check(34.5, 700, 600, d=0.4), dots(34.5, 1250, 450, 3, 0.2), t(34.5, 1400, 850, 60, "碰不到，太稀", c="blue", d=0.5))
bd(35, furnace(35, 650, 800, 0.0, 1.0), cross(35, 650, 600, d=0.3), t(35, 1350, 450, 64, "不是更结实的炉子", d=0.2), ic(35, "gear", 1350, 700, 140, 0.4, mv="spin"))
bd(35.5, torus(35.5, 960, 600, 450, 250, 0.0), yy(35.5, 960, 600, 0.7, 0.2), big(35.5, 960, 200, "看不见的笼子", c="blue", d=0.4, s=110))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"EAST": "伊斯特", "B站": "B站", "1066": "一千零六十六", "2025年": "二零二五年"})
