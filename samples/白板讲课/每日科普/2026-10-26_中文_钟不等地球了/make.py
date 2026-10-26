"""每日科普 2026-10-26（中文）：《钟，不等地球了？》
新闻：第28届国际计量大会（2026年10月13—15日，法国凡尔赛）决议，自2027年5月20日起全球停止插入闰秒，UTC 与 UT1 的最大允许偏差
放宽到3600秒（光明网 10/19、10/26；澎湃新闻；新浪科技 10/19；新浪财经 10/26；广州日报 10/25）。新浪科技热点小时报 10/26 13时第4条。
光明网：5G基站、电网相量同步、金融时间戳不再处理正负闰秒；北斗不再需要插闰秒，减少换算出错。
课本/公开资料：1967年起秒用铯-133的9192631770次振荡定义；1972年起实行闰秒，共插入27次，最近一次2016年12月31日；潮汐让地球自转变慢；
冰川融化、地核、大气让日长变几毫秒；近年地球转偏快，曾讨论首次“负闰秒”；2012年闰秒让 Reddit、澳航订票系统等出故障，2017年元旦
Cloudflare 的 DNS 也因闰秒出错。估算：误差攒满一小时要上千年（按近几十年平均每年不到一秒）。
角色：小地（会转的地球）、小铯（铯原子，电子绕着转）。贯穿的梗：小地“等等我”。
    python3 make.py <kokoro 模型目录> | --boards-only | --fake   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("23点59分60秒，|以后再也看不到了。", "23:59:60. | You'll never see it again."),
 ("不是钟坏了，|是全世界刚投票取消了闰秒。", "The clock isn't broken. | The world just voted to scrap the leap second."),
 ("国际计量大会决定：|2027年5月20日起，不再插闰秒。", "The General Conference on Weights and Measures decided: | from May 20, 2027, no more leap seconds."),
 ("今天的问题：钟和地球对不上，|为什么不等地球了？", "Today's question: clocks and Earth disagree. | Why stop waiting for Earth?"),
 ("先认识小地，|它每转一圈，就是一天。", "Meet Little Earth. | One spin is one day."),
 ("再认识小铯，原子钟里的铯原子，|一秒振动九十一亿多次。", "And Little Cesium, the atom inside an atomic clock: | over 9.1 billion wiggles a second."),
 ("1967年起，一秒有多长，|就由小铯说了算。", "Since 1967, the length of a second | has been set by cesium."),
 ("问题来了：小铯从来不偷懒，|小地却时快时慢。", "Here's the problem: cesium never slacks, | but Earth speeds up and slows down."),
 ("月亮的潮汐像刹车片，|一点点拖慢地球。", "The Moon's tides act like brake pads, | slowly dragging Earth down."),
 ("冰川融化，水流向赤道，|就像滑冰的人张开胳膊，转得更慢。", "Melting ice flows toward the equator, | like a skater opening her arms and slowing down."),
 ("地核晃一晃、刮几场大风，|一天的长短也会差几毫秒。", "A wobble in the core, a few big winds, | and a day changes by milliseconds."),
 ("差多了怎么办？|1972年起，人们发明了闰秒。", "So what do you do when they drift apart? | In 1972, people invented the leap second."),
 ("钟跑到地球前面了，|就在午夜多插一秒，等等地球。", "When the clock gets ahead of Earth, | add one second at midnight and let Earth catch up."),
 ("到现在一共插了27次，|最近一次是2016年最后一天。", "It's been done 27 times, | most recently on the last day of 2016."),
 ("反转一：|这一秒，把电脑坑惨了。", "Twist one: | that one second wrecked computers."),
 ("电脑只认到59秒，|突然冒出个60秒，直接懵了。", "Computers count to 59. | Suddenly there's a 60, and they freeze."),
 ("2012年那次闰秒，|好几家大网站和航空公司订票系统都出了故障。", "In the 2012 leap second, | big websites and an airline booking system broke."),
 ("2017年元旦，|一家大型网络公司也因为闰秒短暂出错。", "On New Year's Day 2017, | a major internet company glitched because of one."),
 ("5G基站、电网、金融交易，|时间一秒都不能乱。", "5G towers, power grids, stock trades: | they can't afford a messy second."),
 ("反转二：|地球这几年反而转快了！", "Twist two: | lately, Earth has been spinning faster!"),
 ("人们甚至开始讨论，|要不要第一次“减”一秒。", "People even started talking about | taking a second away for the first time."),
 ("负闰秒就是直接跳过一秒，|从来没人试过，谁也不敢试。", "A negative leap second skips a second entirely. | Nobody has ever tried it, and nobody wants to."),
 ("所以干脆：不插了，|让钟只管自己走。", "So the decision: stop adding them, | and let the clocks just tick."),
 ("钟和地球的误差，|放宽到3600秒，整整一小时。", "The allowed gap between clock and Earth | grows to 3600 seconds. A full hour."),
 ("反转三：那太阳会不会越来越不准？|会，但慢得你察觉不到。", "Twist three: will the Sun drift off schedule? | Yes, too slowly to notice."),
 ("按近几十年的速度估算，|攒满一小时，要上千年。", "At the pace of recent decades, | filling that hour would take over a thousand years."),
 ("一辈子下来，太阳也就晚个把分钟，|你根本感觉不到。", "In a lifetime, the Sun might run a minute or so late. | You'd never feel it."),
 ("北斗导航也松了口气：|不用再处理闰秒，换算少出错。", "Navigation satellites relax too: | no leap seconds means fewer conversion errors."),
 ("说到底，是两种时间在打架：|天文时间和原子时间。", "In the end, it's two kinds of time fighting: | Earth time and atom time."),
 ("以前是钟等地球，|以后是钟先走，地球慢慢跟。", "Before, the clock waited for Earth. | Now the clock walks on, and Earth follows slowly."),
 ("友情提示：天文学家用的世界时还在，|太阳照样东升西落。", "Friendly fine print: astronomers' Earth time still exists, | and the Sun still rises in the east."),
 ("这事也不影响你的闹钟，|手机照样自动对时。", "Your alarm clock won't notice either. | Your phone still syncs itself."),
 ("所以最后一个23点59分60秒，|已经留在了2016年。", "So the last 23:59:60 | stays forever in 2016."),
 ("小地慢慢转，小铯一秒不差，|从此各走各的，相安无事。", "Earth spins at its own pace, cesium never misses, | and from now on, they each go their own way."),
]
TITLE = {"zh": "钟，不等地球了？", "en": "The Clock Stops Waiting for Earth"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 880, 0.5, r=16)
    B.append(E)


def earth(a, x, y, k=1.0, mood="happy", d=None, rpm=30):
    """小地：蓝色圆脸，脸上的“大陆”一直转，自己上下晃。"""
    i = uid("ea") + "_"
    ld = i + "ld"
    r = 90 * k
    E = [O(a, x, y, r, c="ink", fill="blue", idp=i),
         P(a, f"M{x - r * .6},{y - r * .5} Q{x - r * .2},{y - r * .8} {x},{y - r * .4} Q{x - r * .3},{y - r * .2} {x - r * .6},{y - r * .5} Z "
              f"M{x + r * .3},{y + r * .3} Q{x + r * .7},{y + r * .2} {x + r * .6},{y + r * .6} Q{x + r * .3},{y + r * .7} {x + r * .3},{y + r * .3} Z",
           c="green", w=5, fill="green", idp=ld),
         O(a, x - 30 * k, y - 10 * k, 10 * k, c="ink", fill="ink", idp=i), O(a, x + 30 * k, y - 10 * k, 10 * k, c="ink", fill="ink", idp=i)]
    m = {"happy": f"M{x - 24 * k},{y + 20 * k} Q{x},{y + 40 * k} {x + 24 * k},{y + 20 * k}",
         "o": f"M{x - 10 * k},{y + 28 * k} a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0",
         "sad": f"M{x - 24 * k},{y + 36 * k} Q{x},{y + 18 * k} {x + 24 * k},{y + 36 * k}"}[mood]
    E += [P(a, m, c="ink", w=4, idp=i), spin(a, ld, (x, y), rpm), bob(a, i, 8 * k, 1.2), bob(a, ld, 8 * k, 1.2)]
    if d is not None:
        E.append(pop(a, [i, ld], d))
    return E, [i, ld]


def cesium(a, x, y, k=1.0, mood="happy", d=None, rpm=180):
    """小铯：金色小圆脸，外面一圈轨道上一个电子飞快地转。"""
    i = uid("cs") + "_"
    el = i + "el"
    r = 60 * k
    E = [O(a, x, y, r, c="ink", fill="gold", idp=i),
         {"t": "ellipse", "at": a, "x": x - r * 2, "y": y - r * .7, "w": r * 4, "h": r * 1.4, "c": "red", "sw": 3, "id": i},
         O(a, x + r * 2, y, 12 * k, c="ink", fill="red", idp=el),
         O(a, x - 20 * k, y - 8 * k, 7 * k, c="ink", fill="ink", idp=i), O(a, x + 20 * k, y - 8 * k, 7 * k, c="ink", fill="ink", idp=i)]
    m = {"happy": f"M{x - 16 * k},{y + 14 * k} Q{x},{y + 28 * k} {x + 16 * k},{y + 14 * k}",
         "o": f"M{x - 7 * k},{y + 20 * k} a7,7 0 1,0 14,0 a7,7 0 1,0 -14,0",
         "sad": f"M{x - 16 * k},{y + 26 * k} Q{x},{y + 12 * k} {x + 16 * k},{y + 26 * k}"}[mood]
    E += [P(a, m, c="ink", w=4, idp=i), spin(a, el, (x, y), rpm), wig(a, i, (x, y + r), 4, 3.0)]
    if d is not None:
        E.append(pop(a, [i, el], d))
    return E, [i, el]


def clock(a, x, y, r=150, d=0.0, rpm=60, c="ink", face="paper"):
    """钟：表盘 + 一直转的秒针 + 慢一些的分针。"""
    i, s, m = uid("ck"), uid("sec"), uid("min")
    return [O(a, x, y, r, c=c, fill=face, idp=i), P(a, " ".join(f"M{x + r * .85 * dx},{y + r * .85 * dy} L{x + r * dx},{y + r * dy}" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), c=c, w=5, idp=i),
            P(a, f"M{x},{y} L{x},{y - r * .85}", c="red", w=4, idp=s), P(a, f"M{x},{y} L{x + r * .5},{y}", c=c, w=7, idp=m),
            pop(a, [i, s, m], d), spin(a, s, (x, y), rpm), spin(a, m, (x, y), rpm / 12)]


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def flash(a, x, y, d=0.0, c="gold", r=110):
    i = uid("fl")
    return [P(a, " ".join(f"M{x},{y} L{x + r * dx},{y + r * dy}" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, -.7), (.7, -.7), (-.7, .7))), c=c, w=7, idp=i),
            pop(a, i, d), spin(a, i, (x, y), 30), pulse(a, i, d + 0.4)]


def moon(a, x, y, s=160, d=0.0, cx=None, cy=None, rpm=20):
    i = uid("mn")
    E = [{"t": "icon", "at": a, "id": i, "name": "moon", "x": x, "y": y, "size": s, "c": "gold"}, pop(a, i, d)]
    E.append(spin(a, i, (cx, cy), rpm) if cx is not None else bob(a, i, 8, 0.9))
    return E


def digits(a, x, y, text, s=130, c="red", d=0.0, flip=True):
    """大号时间戳：最后一格会翻一下。"""
    E = BIG(a, x, y, text, c=c, d=d, s=s)
    if flip:
        E.append(pulse(a, E[0]["id"], d + 0.5))
    return E


def wave(a, x, y, w=500, n=6, d=0.0, c="red", amp=60):
    i = uid("wv")
    dd = f"M{x - w / 2},{y} " + " ".join(f"Q{x - w / 2 + w / n * (q + .5)},{y + (amp if q % 2 else -amp)} {x - w / 2 + w / n * (q + 1)},{y}" for q in range(n))
    return [P(a, dd, c=c, w=6, idp=i), pop(a, i, d), wig(a, i, (x, y), 2, 3.0)]


def plane(a, x, y, d=0.0):
    i = uid("pln")
    return [P(a, f"M{x - 120},{y} L{x + 120},{y} L{x + 150},{y - 20} M{x - 20},{y} L{x - 70},{y - 90} M{x - 20},{y} L{x - 70},{y + 90} M{x - 110},{y} L{x - 140},{y - 40}", c="ink", w=7, idp=i),
            pop(a, i, d), wig(a, i, (x, y), 6, 1.5)]


# 0 23:59:60
bd(0, digits(0, 960, 420, "23:59:60", s=170, d=0.0), clock(0, 400, 760, 110, 0.2, rpm=120), clock(0, 1520, 760, 110, 0.3, rpm=-120, c="red"), flash(0, 1430, 300, 0.5, r=70))
# 0.5 never see again
bd(0.5, digits(0.5, 960, 380, "23:59:60", s=130, c="muted", d=0.0, flip=False), cross(0.5, 960, 380, d=0.3), earth(0.5, 960, 720, 0.9, mood="o", d=0.4)[0], T(0.5, 1450, 720, 50, "再见！", c="red", d=0.5))
# 1 clock isn't broken
bd(1, clock(1, 650, 500, 220, 0.0, rpm=60), check(1, 650, 820, d=0.3), T(1, 1350, 420, 64, "钟没坏", c="green", d=0.2), icon(1, "gear", 1350, 640, 160, 0.4, mv="spin"))
# 1.5 world voted
hands_ = []
for q in range(5):
    i = uid("vt")
    hands_ += [P(1.5, f"M{450 + 250 * q},800 L{450 + 250 * q},560 M{430 + 250 * q},600 L{450 + 250 * q},540 L{470 + 250 * q},600", c="ink", w=7, idp=i),
               pop(1.5, i, 0.1 * q), sh(1.5, i, 0, -60, 0.3 + 0.1 * q, 0.3)]
bd(1.5, icon(1.5, "globe", 960, 300, 220, 0.0, c="blue", mv="spin"), hands_, T(1.5, 960, 900, 56, "全世界投票：取消闰秒", c="red", d=0.6))
# 2 CGPM
bd(2, icon(2, "building", 500, 500, 300, 0.0), T(2, 1250, 380, 64, "国际计量大会", c="blue", d=0.1), T(2, 1250, 500, 44, "第28届 · 法国凡尔赛", c="muted", d=0.3), icon(2, "ruler", 1100, 720, 140, 0.3, mv="wig"),
   icon(2, "clock", 1400, 720, 140, 0.4, mv="spin"))
# 2.5 from 2027-05-20
bd(2.5, BIG(2.5, 960, 380, "2027.5.20", c="red", d=0.0, s=150), T(2.5, 960, 580, 64, "起，不再插闰秒", c="ink", d=0.2), cross(2.5, 960, 780, d=0.4), clock(2.5, 1550, 780, 90, 0.3, rpm=90))
# 3 today's question
bd(3, earth(3, 600, 520, 1.3, mood="o")[0], clock(3, 1350, 520, 160, 0.1, rpm=90), BIG(3, 960, 520, "≠", c="red", d=0.3, s=150), T(3, 960, 860, 56, "钟和地球对不上", c="ink", d=0.4))
# 3.5 why stop waiting
p_, pi = earth(3.5, 500, 560, 1.0, mood="sad")
bd(3.5, p_, T(3.5, 500, 300, 56, "等等我！", c="blue", d=0.2), clock(3.5, 1300, 520, 140, 0.0, rpm=120), [sh(3.5, [], 0, 0, 0, 0.1)] if False else [],
   icon(3.5, "question", 1650, 300, 160, 0.4, c="red", mv="wig"), T(3.5, 1300, 820, 56, "为什么不等了？", c="red", d=0.5))
# 4 meet Little Earth
bd(4, earth(4, 760, 500, 2.2, d=0.0)[0], BIG(4, 1450, 380, "小地", c="blue", d=0.3, s=150), [e for q in range(3) for e in star(4, 1330 + 120 * q, 600, 0.5 + 0.1 * q, r=30)])
# 4.5 one spin one day
bd(4.5, earth(4.5, 700, 520, 1.4, rpm=60)[0], icon(4.5, "sun", 1400, 350, 200, 0.1, c="gold", mv="spin"), arr(4.5, 900, 300, 1150, 300, c="red", d=0.3), T(4.5, 1300, 700, 64, "转一圈 = 一天", c="ink", d=0.4))
# 5 meet Little Cesium
bd(5, cesium(5, 760, 500, 2.2, d=0.0)[0], BIG(5, 1500, 380, "小铯", c="gold", d=0.3, s=150), icon(5, "atom", 1500, 650, 160, 0.4, mv="spin"))
# 5.5 9.1 billion wiggles
bd(5.5, cesium(5.5, 480, 500, 1.2, rpm=400)[0], BIG(5.5, 1250, 380, "9,192,631,770", c="red", d=0.1, s=100), T(5.5, 1250, 560, 56, "次 / 秒", c="ink", d=0.3), wave(5.5, 1250, 760, 700, 12, 0.4, c="gold", amp=40))
# 6 since 1967
bd(6, BIG(6, 700, 400, "1967", c="blue", d=0.0, s=160), T(6, 700, 600, 56, "一秒有多长", c="ink", d=0.2), icon(6, "ruler", 700, 780, 140, 0.3, mv="wig"), clock(6, 1400, 500, 180, 0.2, rpm=60))
# 6.5 cesium decides
bd(6.5, cesium(6.5, 800, 500, 1.6, d=0.0)[0], T(6.5, 1450, 420, 64, "小铯说了算", c="gold", d=0.2), check(6.5, 1450, 620, d=0.4), [e for q in range(3) for e in star(6.5, 500 + 600 * q, 850, 0.3 + 0.1 * q, r=28)])
# 7 cesium never slacks
bd(7, cesium(7, 600, 500, 1.4, rpm=300)[0], wave(7, 1300, 400, 600, 10, 0.1, c="gold", amp=40), T(7, 1300, 620, 60, "从不偷懒", c="gold", d=0.3), check(7, 1300, 800, d=0.4))
# 7.5 earth fast and slow
p_, pi = earth(7.5, 600, 500, 1.3, rpm=50)
bd(7.5, p_, [rot(7.5, pi, 30, (600, 500), 0.2, 0.4), rot(7.5, pi, -30, (600, 500), 0.8, 0.5)], T(7.5, 1300, 380, 64, "时快", c="red", d=0.2), T(7.5, 1300, 560, 64, "时慢", c="blue", d=0.5),
   arr(7.5, 1100, 760, 1500, 760, c="red", d=0.3), arr(7.5, 1500, 820, 1100, 820, c="blue", d=0.6))
# 8 moon tides
bd(8, earth(8, 800, 520, 1.2)[0], moon(8, 1400, 520, 160, 0.1, cx=800, cy=520, rpm=12), wave(8, 800, 820, 500, 6, 0.3, c="blue", amp=30), T(8, 1450, 860, 56, "潮汐", c="blue", d=0.3))
# 8.5 brake pads
bd(8.5, icon(8.5, "wheel", 700, 500, 300, 0.0, mv="spin"), [R(8.5, 860, 420, 60, 160, c="ink", fill="red", idp=uid("bk"))], arr(8.5, 1050, 500, 930, 500, c="red", d=0.2), T(8.5, 1400, 420, 64, "刹车片", c="red", d=0.3),
   T(8.5, 1400, 600, 48, "一点点拖慢", c="ink", d=0.5))
# 9 ice melts to equator
ic = uid("ice")
bd(9, earth(9, 700, 520, 1.6)[0], [P(9, "M560,300 L840,300 L800,350 L600,350 Z", c="ink", w=5, fill="paper", idp=ic), pop(9, ic, 0.0), sh(9, ic, 0, 220, 0.4, 0.9)],
   T(9, 1400, 420, 60, "冰化成水", c="blue", d=0.2), arr(9, 1400, 520, 1400, 700, c="blue", d=0.4), T(9, 1400, 780, 56, "流向赤道", c="blue", d=0.5))
# 9.5 skater opens arms
sk, ar = uid("sk"), uid("ska")
bd(9.5, [O(9.5, 700, 330, 50, c="ink", fill="paper", idp=sk), P(9.5, "M700,380 L700,620 L640,800 M700,620 L760,800", c="ink", w=7, idp=sk), P(9.5, "M700,450 L720,420 M700,450 L680,420", c="ink", w=7, idp=ar),
           pop(9.5, [sk, ar], 0.0), {"t": "move", "at": 9.5, "kind": "grow", "targets": [ar], "axis": "x", "pivot": [700, 450], "dur": 0.6, "delay": 0.4},
           spin(9.5, sk, (700, 560), 30)], [P(9.5, "M560,450 L840,450", c="red", w=7, idp=ar)],
   T(9.5, 1350, 420, 60, "张开胳膊", c="red", d=0.4), T(9.5, 1350, 600, 60, "转得更慢", c="blue", d=0.6), icon(9.5, "wind", 1350, 780, 120, 0.3, c="blue", mv="wig"))
# 10 core wobble winds
bd(10, earth(10, 600, 520, 1.3)[0], [O(10, 600, 520, 40, c="ink", fill="red", idp=uid("core"))], icon(10, "wind", 1100, 350, 180, 0.2, c="blue", mv="wig"), icon(10, "cloud", 1450, 350, 160, 0.3, mv="bob"),
   T(10, 1300, 650, 56, "地核晃、大风刮", c="ink", d=0.4))
# 10.5 milliseconds
bd(10.5, BIG(10.5, 960, 400, "± 几毫秒", c="red", d=0.0, s=140), clock(10.5, 500, 760, 110, 0.2, rpm=180), clock(10.5, 1420, 760, 110, 0.3, rpm=170), T(10.5, 960, 760, 48, "一天的长短", c="ink", d=0.4))
# 11 drifted apart
p_, pi = earth(11, 900, 520, 1.0, mood="o")
c_ = clock(11, 1100, 520, 100, 0.0, rpm=120)
bd(11, p_, c_, [sh(11, pi, -400, 0, 0.2, 0.8), sh(11, [c_[0]["id"], c_[2]["id"], c_[3]["id"]], 400, 0, 0.2, 0.8)], T(11, 960, 860, 56, "越差越多", c="red", d=0.4))
# 11.5 1972 leap second
bd(11.5, BIG(11.5, 700, 420, "1972", c="blue", d=0.0, s=160), T(11.5, 700, 620, 64, "闰秒诞生", c="red", d=0.2), BIG(11.5, 1350, 450, "+1 s", c="red", d=0.4, s=150), flash(11.5, 1350, 450, 0.5, r=150))
# 12 clock ahead of earth
p_, pi = earth(12, 500, 560, 1.0, mood="sad")
bd(12, p_, clock(12, 1300, 500, 160, 0.0, rpm=120), T(12, 1300, 760, 56, "钟跑前面了", c="red", d=0.2), T(12, 500, 320, 50, "等等我！", c="blue", d=0.4), arr(12, 700, 560, 1100, 560, c="muted", d=0.4))
# 12.5 add a second at midnight
bd(12.5, digits(12.5, 960, 360, "23:59:59", s=120, c="ink", d=0.0, flip=False), arr(12.5, 960, 450, 960, 560, c="red", d=0.2), digits(12.5, 960, 660, "23:59:60", s=120, c="red", d=0.4),
   earth(12.5, 1600, 600, 0.7, d=0.6)[0], icon(12.5, "moon", 350, 400, 140, 0.2, c="gold", mv="bob"))
# 13 27 times
ticks = []
for q in range(27):
    i = uid("tk")
    ticks += [P(13, f"M{380 + 44 * q},700 L{380 + 44 * q},{620 - 30 * (q % 3)}", c="red", w=6, idp=i), pop(13, i, 0.03 * q)]
bd(13, ticks, BIG(13, 960, 360, "27 次", c="red", d=0.2, s=150), T(13, 960, 820, 48, "1972 → 2016", c="muted", d=0.5))
# 13.5 last on 2016-12-31
cal = uid("cal")
bd(13.5, [R(13.5, 600, 300, 400, 400, c="ink", fill="paper", idp=cal), R(13.5, 600, 300, 400, 90, c="ink", fill="red", idp=cal), pop(13.5, cal, 0.0), rot(13.5, cal, -6, (800, 500), 0.4, 0.4)],
   T(13.5, 800, 560, 120, "31", c="ink"), T(13.5, 800, 345, 44, "2016.12", c="paper"), T(13.5, 1400, 450, 60, "最近一次", c="red", d=0.3), clock(13.5, 1400, 700, 100, 0.4, rpm=120))
# 14 twist one
bd(14, BIG(14, 960, 200, "反转一", c="blue", d=0.0, s=100), icon(14, "computer", 960, 560, 320, 0.2, mv="bob"), flash(14, 1300, 400, 0.5, r=70, c="red"))
# 14.5 wrecked computers
bd(14.5, icon(14.5, "computer", 600, 500, 280, 0.0, mv="wig"), BIG(14.5, 600, 820, "+1 s", c="red", d=0.2, s=100), [e for q in range(3) for e in flash(14.5, 1100 + 260 * q, 350 + 150 * (q % 2), 0.2 + 0.15 * q, r=70, c="red")],
   T(14.5, 1350, 780, 60, "坑惨了", c="red", d=0.5))
# 15 computers count to 59
cnt = []
for q, n in enumerate(["57", "58", "59"]):
    cnt += T(15, 500 + 300 * q, 450, 110, n, c="ink", d=0.15 * q)
bd(15, cnt, icon(15, "computer", 1500, 450, 200, 0.2, mv="bob"), check(15, 1500, 700, d=0.5), T(15, 800, 700, 50, "电脑只认到 59", c="muted", d=0.4))
# 15.5 suddenly 60, freeze
p_ = icon(15.5, "computer", 1300, 480, 300, 0.0, mv="wig")
bd(15.5, BIG(15.5, 600, 450, "60 ?!", c="red", d=0.1, s=160), p_, [rot(15.5, p_[0]["id"], 12, (1300, 630), 0.4, 0.3)], T(15.5, 1300, 820, 60, "懵了…", c="red", d=0.5), icon(15.5, "question", 1550, 260, 120, 0.4, c="red", mv="wig"))
# 16 2012 leap second
bd(16, BIG(16, 960, 340, "2012", c="blue", d=0.0, s=150), icon(16, "computer", 600, 700, 200, 0.2, mv="wig"), cross(16, 600, 700, d=0.4), icon(16, "phone", 1320, 700, 180, 0.3, mv="wig"), cross(16, 1320, 700, d=0.5))
# 16.5 websites and airline booking
bd(16.5, plane(16.5, 650, 450, 0.0), cross(16.5, 650, 450, d=0.3), T(16.5, 650, 700, 56, "订票系统", c="red", d=0.2), icon(16.5, "globe", 1350, 450, 220, 0.2, c="blue", mv="spin"), T(16.5, 1350, 700, 56, "大网站", c="red", d=0.4))
# 17 New Year's Day 2017
bd(17, BIG(17, 700, 400, "2017.1.1", c="red", d=0.0, s=130), [e for q in range(3) for e in flash(17, 1250 + 200 * q, 350 + 100 * (q % 2), 0.1 * q, r=60, c=["gold", "red", "blue"][q])],
   icon(17, "cloud", 1450, 650, 200, 0.3, mv="bob"))
# 17.5 major internet company glitched
bd(17.5, icon(17.5, "cloud", 700, 450, 300, 0.0, mv="wig"), cross(17.5, 700, 450, d=0.3), T(17.5, 1350, 400, 60, "网络公司出错", c="red", d=0.2), icon(17.5, "signal", 1350, 650, 160, 0.4, mv="wig"))
# 18 5G grid trades
bd(18, icon(18, "signal", 450, 500, 220, 0.0, mv="wig"), icon(18, "engine", 960, 500, 220, 0.1, mv="wig"), icon(18, "building", 1470, 500, 220, 0.2, mv="bob"),
   T(18, 450, 720, 50, "5G基站", c="ink", d=0.2), T(18, 960, 720, 50, "电网", c="ink", d=0.3), T(18, 1470, 720, 50, "金融交易", c="ink", d=0.4))
# 18.5 can't be messy
bd(18.5, clock(18.5, 700, 500, 200, 0.0, rpm=60), BIG(18.5, 1350, 420, "一秒不能乱", c="red", d=0.2, s=100), check(18.5, 1350, 650, d=0.4), sound(18.5, 920, 500, 0.8, d=0.3))
# 19 twist two
bd(19, BIG(19, 960, 200, "反转二", c="blue", d=0.0, s=100), earth(19, 960, 560, 1.4, mood="o", rpm=90)[0])
# 19.5 earth spinning faster
p_, pi = earth(19.5, 700, 520, 1.4, rpm=160)
bd(19.5, p_, [rot(19.5, pi, 360, (700, 520), 0.2, 0.8)], T(19.5, 1350, 420, 64, "转快了！", c="red", d=0.2), [e for q in range(3) for e in arr(19.5, 1150, 580 + 60 * q, 1550, 580 + 60 * q, c="red", d=0.3 + 0.1 * q)])
# 20 people discussing
bd(20, icon(20, "speaker", 500, 480, 240, 0.0, mv="wig"), sound(20, 640, 480, 1.2, d=0.2), T(20, 1300, 420, 60, "要不要……", c="ink", d=0.2), icon(20, "question", 1300, 650, 180, 0.4, c="red", mv="wig"))
# 20.5 take a second away
bd(20.5, BIG(20.5, 960, 400, "−1 s", c="blue", d=0.0, s=170), T(20.5, 960, 620, 60, "第一次“减”一秒？", c="red", d=0.3), clock(20.5, 450, 750, 100, 0.2, rpm=-120), clock(20.5, 1470, 750, 100, 0.3, rpm=-120))
# 21 skip a second
bd(21, digits(21, 600, 450, "23:59:58", s=110, c="ink", d=0.0, flip=False), arr(21, 900, 450, 1050, 450, c="red", d=0.2), digits(21, 1400, 450, "00:00:00", s=110, c="blue", d=0.3),
   T(21, 960, 660, 56, "直接跳过 59", c="red", d=0.5), cross(21, 960, 820, d=0.6))
# 21.5 nobody tried
bd(21.5, icon(21.5, "computer", 600, 500, 260, 0.0, mv="wig"), T(21.5, 600, 280, 50, "没试过", c="muted", d=0.2), icon(21.5, "question", 1300, 450, 220, 0.2, c="red", mv="wig"), T(21.5, 1300, 700, 60, "谁也不敢试", c="red", d=0.4),
   flash(21.5, 850, 300, 0.5, r=50, c="red"))
# 22 stop adding
bd(22, BIG(22, 600, 450, "+1 s", c="muted", d=0.0, s=140), cross(22, 600, 450, d=0.3), T(22, 1300, 400, 70, "不插了", c="red", d=0.2), check(22, 1300, 600, d=0.5))
# 22.5 let clocks tick
bd(22.5, clock(22.5, 600, 500, 200, 0.0, rpm=60), clock(22.5, 1100, 500, 140, 0.1, rpm=60, c="blue"), clock(22.5, 1500, 500, 110, 0.2, rpm=60, c="red"), T(22.5, 960, 860, 60, "钟只管自己走", c="ink", d=0.4))
# 23 gap between clock and earth
bd(23, earth(23, 500, 520, 1.1)[0], clock(23, 1400, 520, 140, 0.0, rpm=60), arr(23, 650, 520, 1230, 520, c="red", d=0.2), arr(23, 1230, 580, 650, 580, c="red", d=0.4), T(23, 940, 380, 56, "允许的误差", c="ink", d=0.3))
# 23.5 3600 seconds an hour
bd(23.5, BIG(23.5, 960, 360, "3600 秒", c="red", d=0.0, s=150), T(23.5, 960, 560, 70, "= 1 小时", c="blue", d=0.3), bar(23.5, 600, 880, 120, 30, "muted", d=0.3), bar(23.5, 1200, 880, 120, 260, "red", d=0.5),
   T(23.5, 660, 920, 36, "以前 0.9 秒", c="muted", d=0.4))
# 24 will the sun drift
bd(24, BIG(24, 960, 200, "反转三", c="blue", d=0.0, s=100), icon(24, "sun", 960, 540, 280, 0.2, c="gold", mv="spin"), icon(24, "question", 1450, 450, 160, 0.4, c="red", mv="wig"))
# 24.5 yes, too slow to notice
sn = uid("sun")
bd(24.5, [{"t": "icon", "at": 24.5, "id": sn, "name": "sunrise", "x": 700, "y": 520, "size": 340, "c": "gold"}, pop(24.5, sn, 0.0), sh(24.5, sn, 20, 0, 0.3, 1.2)], T(24.5, 1350, 420, 64, "会，但……", c="ink", d=0.2),
   T(24.5, 1350, 600, 60, "慢得察觉不到", c="blue", d=0.4), icon(24.5, "magnifier", 1600, 780, 120, 0.5, mv="wig"))
# 25 at recent pace
bd(25, bar(25, 500, 850, 120, 200, "blue", d=0.0), bar(25, 700, 850, 120, 220, "blue", d=0.15), bar(25, 900, 850, 120, 190, "blue", d=0.3), T(25, 700, 480, 50, "近几十年", c="ink", d=0.2),
   T(25, 1400, 450, 56, "每年不到 1 秒", c="red", d=0.4), clock(25, 1400, 700, 100, 0.3, rpm=30))
# 25.5 over a thousand years
bd(25.5, BIG(25.5, 960, 380, "上千年", c="red", d=0.0, s=160), T(25.5, 960, 580, 56, "攒满一小时（估算）", c="ink", d=0.2), icon(25.5, "dinosaur", 450, 780, 160, 0.3, mv="wig"), icon(25.5, "building", 1500, 780, 160, 0.4, mv="bob"))
# 26 a lifetime a minute or so
bd(26, icon(26, "sun", 600, 450, 220, 0.0, c="gold", mv="spin"), BIG(26, 1300, 400, "≈ 1 分钟", c="blue", d=0.2, s=120), T(26, 1300, 580, 56, "一辈子下来", c="ink", d=0.3), earth(26, 600, 780, 0.6)[0])
# 26.5 never feel it
bd(26.5, earth(26.5, 960, 480, 1.4, mood="happy")[0], [e for q in range(3) for e in T(26.5, 1250 + 50 * q, 300 - 50 * q, 40 + 12 * q, "z", c="muted", d=0.2 + 0.2 * q)], T(26.5, 960, 820, 60, "根本感觉不到", c="blue", d=0.3))
# 27 navigation satellites relax
bd(27, icon(27, "satellite", 700, 420, 280, 0.0, mv="spin"), T(27, 1350, 400, 70, "北斗", c="red", d=0.2), earth(27, 1350, 720, 0.7)[0], sound(27, 850, 560, 0.6, d=0.3))
# 27.5 fewer errors
bd(27.5, icon(27.5, "map_pin", 600, 480, 260, 0.0, c="red"), check(27.5, 900, 400, d=0.3), T(27.5, 1350, 420, 60, "不用处理闰秒", c="ink", d=0.2), T(27.5, 1350, 600, 60, "换算少出错", c="green", d=0.4),
   icon(27.5, "gear", 1350, 800, 120, 0.4, mv="spin"))
# 28 two kinds of time fighting
p_, pi = earth(28, 500, 520, 1.1, mood="o")
c_, ci = cesium(28, 1420, 520, 1.1, mood="o")
bd(28, p_, c_, [sh(28, pi, 200, 0, 0.2, 0.4), sh(28, ci, -200, 0, 0.2, 0.4)], flash(28, 960, 520, 0.6, r=90, c="red"), T(28, 960, 220, 64, "两种时间在打架", c="red", d=0.3))
# 28.5 Earth time vs atom time
bd(28.5, earth(28.5, 550, 480, 1.1)[0], cesium(28.5, 1370, 480, 1.0)[0], T(28.5, 550, 760, 60, "天文时间", c="blue", d=0.2), T(28.5, 1370, 760, 60, "原子时间", c="gold", d=0.4), BIG(28.5, 960, 480, "VS", c="red", d=0.3, s=110))
# 29 before, clock waited
p_, pi = earth(29, 600, 520, 1.0)
bd(29, p_, clock(29, 1300, 520, 130, 0.0, rpm=20), T(29, 960, 220, 60, "以前：钟等地球", c="ink", d=0.2), T(29, 1300, 760, 50, "（插闰秒）", c="muted", d=0.4), sh(29, pi, 200, 0, 0.4, 0.8) and [sh(29, pi, 200, 0, 0.4, 0.8)])
# 29.5 now clock walks on
p_, pi = earth(29.5, 500, 560, 0.9)
c_ = clock(29.5, 900, 560, 110, 0.0, rpm=90)
bd(29.5, p_, c_, [sh(29.5, [c_[0]["id"], c_[2]["id"], c_[3]["id"]], 600, 0, 0.2, 1.2), sh(29.5, pi, 200, 0, 0.6, 1.4)], T(29.5, 960, 220, 60, "以后：钟先走，地球慢慢跟", c="blue", d=0.3))
# 30 fine print
bd(30, T(30, 960, 200, 64, "友情提示", c="red", d=0.0), icon(30, "lens", 600, 520, 240, 0.1, mv="wig"), T(30, 1300, 480, 56, "世界时（UT1）还在", c="ink", d=0.3), check(30, 1300, 650, d=0.5))
# 30.5 sun still rises in the east
sn = uid("sun")
bd(30.5, [{"t": "icon", "at": 30.5, "id": sn, "name": "sunrise", "x": 960, "y": 560, "size": 420, "c": "gold"}, pop(30.5, sn, 0.0), sh(30.5, sn, 0, -60, 0.3, 1.2)], T(30.5, 960, 220, 60, "太阳照样东升西落", c="ink", d=0.3))
# 31 alarm clock won't notice
bd(31, clock(31, 700, 520, 200, 0.0, rpm=60, c="red"), sound(31, 920, 380, 0.7, d=0.2), sound(31, 480, 380, 0.7, d=0.2, dirn=-1), T(31, 1400, 500, 60, "闹钟不受影响", c="ink", d=0.3))
# 31.5 phone syncs
bd(31.5, icon(31.5, "phone", 700, 500, 300, 0.0, mv="bob"), icon(31.5, "satellite", 1300, 320, 160, 0.2, mv="spin"), arr(31.5, 1220, 380, 820, 450, c="blue", d=0.3), T(31.5, 1300, 700, 60, "自动对时", c="green", d=0.4),
   check(31.5, 1550, 700, d=0.6))
# 32 the last 23:59:60
bd(32, digits(32, 960, 420, "23:59:60", s=160, c="red", d=0.0), T(32, 960, 620, 56, "最后一个", c="ink", d=0.2), [e for q in range(4) for e in star(32, 500 + 300 * q, 820, 0.3 + 0.1 * q, r=30)])
# 32.5 stays in 2016
cal = uid("cal")
bd(32.5, [R(32.5, 760, 260, 400, 400, c="ink", fill="paper", idp=cal), R(32.5, 760, 260, 400, 90, c="ink", fill="red", idp=cal), pop(32.5, cal, 0.0), pulse(32.5, cal, 0.6)], T(32.5, 960, 520, 120, "2016", c="ink"),
   T(32.5, 960, 820, 56, "永远留在这一年", c="blue", d=0.3), clock(32.5, 400, 500, 100, 0.2, rpm=60), clock(32.5, 1520, 500, 100, 0.3, rpm=60))
# 33 earth slow cesium exact
bd(33, earth(33, 600, 500, 1.3, rpm=20)[0], cesium(33, 1320, 500, 1.2, rpm=300)[0], T(33, 600, 800, 50, "慢慢转", c="blue", d=0.2), T(33, 1320, 800, 50, "一秒不差", c="gold", d=0.4))
# 33.5 each go their own way
p_, pi = earth(33.5, 860, 520, 1.0)
c_, ci = cesium(33.5, 1060, 520, 0.9)
bd(33.5, p_, c_, [sh(33.5, pi, -380, 0, 0.2, 1.0), sh(33.5, ci, 380, 0, 0.2, 1.0)], T(33.5, 960, 860, 60, "各走各的，相安无事", c="green", d=0.5), [e for q in range(3) for e in star(33.5, 760 + 200 * q, 250, 0.4 + 0.1 * q, r=30)])

# ---- 插入的句子（插在原第 k 句后面；画板 at = 100 + j 和 100 + j + 0.5）----
INS = [
 (5, "最好的铯钟，|三亿年都差不到一秒。", "The best cesium clocks | wouldn't lose a second in 300 million years."),
 (10, "所以“一天”，|其实并不正好是86400秒。", "So a day | isn't exactly 86,400 seconds."),
 (13, "每次都是全世界同一时刻，|一起多等这一秒。", "Each time, the whole world | waits that extra second at the same moment."),
 (17, "有的公司干脆发明了“抹秒”，|把这一秒摊进一整天里。", "Some companies invented the leap smear, | spreading that second across a whole day."),
 (21, "原本估算2026年前后就得减一秒，|冰川融化把它推迟到了2029年前后。", "One estimate said we'd need it around 2026. | Melting ice pushed that back to around 2029."),
 (25, "说白了，这一小时，|留给几百上千年后的人去操心。", "In other words, that hour | is a problem for people centuries from now."),
]
# 100 best cesium clocks
bd(100, cesium(100, 600, 500, 1.4, rpm=300)[0], icon(100, "clock", 1350, 450, 240, 0.2, mv="spin"), T(100, 960, 860, 56, "最好的铯钟", c="gold", d=0.3))
# 100.5 300 million years
bd(100.5, BIG(100.5, 960, 360, "3 亿年", c="red", d=0.0, s=160), T(100.5, 960, 560, 60, "差不到 1 秒", c="blue", d=0.3), icon(100.5, "dinosaur", 500, 780, 180, 0.2, mv="wig"), cesium(100.5, 1450, 780, 0.7, d=0.4)[0])
# 101 so a day
bd(101, earth(101, 650, 520, 1.4, rpm=60)[0], icon(101, "sun", 1350, 350, 200, 0.2, c="gold", mv="spin"), T(101, 1350, 650, 70, "“一天”", c="ink", d=0.3), icon(101, "question", 1600, 650, 120, 0.4, c="red", mv="wig"))
# 101.5 not exactly 86400
bd(101.5, BIG(101.5, 960, 380, "86400 秒", c="blue", d=0.0, s=150), BIG(101.5, 960, 600, "± 几毫秒", c="red", d=0.3, s=90), cross(101.5, 1500, 380, d=0.5), clock(101.5, 400, 750, 100, 0.2, rpm=90))
# 102 whole world same moment
cl_ = []
for q in range(4):
    cl_ += clock(102, 420 + 360 * q, 480, 110, 0.1 * q, rpm=60, c=["red", "blue", "ink", "green"][q])
bd(102, cl_, icon(102, "globe", 960, 800, 160, 0.3, c="blue", mv="spin"))
# 102.5 waits together
p_, pi = earth(102.5, 960, 500, 1.2, mood="happy")
bd(102.5, p_, BIG(102.5, 960, 800, "+1 s", c="red", d=0.3, s=120), T(102.5, 960, 200, 56, "全世界一起等", c="ink", d=0.2), clock(102.5, 400, 500, 100, 0.1, rpm=0.01), clock(102.5, 1520, 500, 100, 0.2, rpm=0.01))
# 103 leap smear
bd(103, T(103, 960, 220, 80, "抹秒", c="blue", d=0.0), icon(103, "computer", 600, 550, 240, 0.1, mv="bob"), [e for q in range(3) for e in star(103, 1150 + 180 * q, 550, 0.2 + 0.1 * q, r=34)], T(103, 1300, 760, 50, "有的公司这么干", c="muted", d=0.4))
# 103.5 spread across a day
sm = uid("sm")
bd(103.5, [R(103.5, 300, 500, 80, 80, c="ink", fill="red", idp=sm), pop(103.5, sm, 0.0), {"t": "move", "at": 103.5, "kind": "grow", "targets": [sm], "axis": "x", "pivot": [300, 540], "dur": 1.0, "delay": 0.3}],
   T(103.5, 340, 420, 50, "1 秒", c="red", d=0.1), arr(103.5, 450, 700, 1600, 700, c="blue", d=0.3, dur=1.0), T(103.5, 1300, 800, 56, "摊进一整天", c="blue", d=0.5), clock(103.5, 1650, 400, 90, 0.2, rpm=200))
# 104 estimate 2026
bd(104, BIG(104, 700, 400, "2026？", c="red", d=0.0, s=150), BIG(104, 1350, 400, "−1 s", c="blue", d=0.2, s=130), T(104, 960, 620, 56, "原本的估算", c="muted", d=0.3), earth(104, 960, 820, 0.6, rpm=120)[0])
# 104.5 melting ice pushes to 2029
ic = uid("ice")
bd(104.5, [P(104.5, "M400,350 L700,350 L660,420 L440,420 Z", c="ink", w=5, fill="paper", idp=ic), pop(104.5, ic, 0.0), sh(104.5, ic, 0, 280, 0.3, 0.9)], wave(104.5, 560, 760, 400, 6, 0.6, c="blue", amp=25),
   arr(104.5, 900, 450, 1150, 450, c="red", d=0.4), BIG(104.5, 1450, 450, "2029", c="red", d=0.5, s=140), T(104.5, 1450, 640, 48, "（估算）", c="muted", d=0.6))
# 105 that hour
bd(105, BIG(105, 960, 380, "1 小时", c="red", d=0.0, s=150), clock(105, 500, 700, 120, 0.2, rpm=60), earth(105, 1420, 700, 0.8)[0], T(105, 960, 620, 50, "这一小时", c="ink", d=0.3))
# 105.5 centuries from now
fut = []
for q in range(4):
    fut += [e for e in [R(105.5, 380 + 300 * q, 640 - 60 * q, 160, 200 + 60 * q, c="ink", fill="muted", idp=uid("tw"))]]
    fut += [pop(105.5, fut[-1]["id"], 0.1 * q)]
bd(105.5, fut, icon(105.5, "rocket", 1600, 300, 180, 0.4, c="red", mv="wig"), T(105.5, 960, 200, 56, "几百上千年后的人去操心", c="blue", d=0.3), [e for q in range(3) for e in star(105.5, 1500 + 100 * q, 800, 0.5 + 0.1 * q, r=24)])

S2, MAP = [], {}
for k, sent in enumerate(S):
    MAP[k], MAP[k + 0.5] = len(S2), len(S2) + 0.5
    S2.append(sent)
    for q, (after, zh, en) in enumerate(INS):
        if after == k:
            MAP[100 + q], MAP[100 + q + 0.5] = len(S2), len(S2) + 0.5
            S2.append((zh, en))
S = S2
for b in B:
    for e in b:
        e["at"] = MAP[e["at"]]
B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"23点59分60秒": "二十三点五十九分六十秒", "2027年": "二零二七年", "1967年": "一九六七年", "1972年": "一九七二年",
                                       "2016年": "二零一六年", "2012年": "二零一二年", "2017年": "二零一七年", "5G": "五G", "3600秒": "三千六百秒", "27次": "二十七次", "59秒": "五十九秒", "60秒": "六十秒", "86400秒": "八万六千四百秒", "2026年": "二零二六年", "2029年": "二零二九年"})
