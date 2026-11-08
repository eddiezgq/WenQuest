"""每日科普 2026-11-08（中文）：“一百吨的火箭，只送一吨多上天？”
新闻：2026-11-07 星河动力谷神星二号（遥三）在酒泉发射成功，一箭四星送入约 535 公里太阳同步轨道；今年 1 月 17 日首飞失利，这次是复飞。
热度：新浪微博《2026 年 11 月科技新闻：谷神星二号成功，AI 冲击编程》汇总的头条（11 月 8 日）；新浪科技热点小时报 11-07 收录。
事实（澎湃新闻 2026-01-17 首飞报道）：三级固体串联 + 液体上面级；起飞质量 100 吨；500 km LEO 运力 1.6 吨、500 km SSO 1.3 吨；
  运载效率 1.3%，报道称国际领先；支持海上和陆上发射。
教科书物理：500 公里左右圆轨道速度约 7.6 km/s；火箭方程 Δv = v_e ln(m0/mf)。
我们的估算（片中说明是估算）：入轨连损失约需 9 km/s 多；固体发动机喷气约 2.8 km/s → 质量比约 30（约 97% 是燃料）；
  北京到上海直线约 1070 km → 约两分多钟；步枪子弹约 1 km/s → 七八倍。大火箭运载效率约 4%（土星五号、猎鹰九号一次性）是常见量级。
出处：
- https://sina.cn/weibo/detail/5362898431903683.html
- https://www.thepaper.cn/newsDetail_forward_32408138
- https://k.sina.com.cn/article_7857201856_1d45362c001908u0h6.html
"""
import math
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402,F401
                     star, uid, wig)
from popkit import cute_rocket, stick  # noqa: E402

S = [
 ("一百吨重的火箭，|只把一吨多送上天？", "A one hundred ton rocket | that lifts barely more than one ton to orbit?"),
 ("11 月 7 日，民营火箭谷神星二号，|把 4 颗卫星送上了五百多公里的轨道。", "On November 7, the private rocket Ceres-2 | put four satellites into orbit over 500 km up."),
 ("它今年一月首飞失利，|这次复飞，成了。", "Its first flight failed in January. | This time it worked."),
 ("可公司自己公布的数字是：|起飞一百吨，送上天一点三吨。", "But the company's own numbers: | 100 tons at liftoff, 1.3 tons to orbit."),
 ("一点三除以一百：|百分之一点三。", "1.3 divided by 100: | just 1.3 percent."),
 ("报道说，这个效率|在同类火箭里已经算领先。", "And reports say that efficiency | is world-class for its type."),
 ("今天的烧脑问题：剩下那九十八吨多，|到底干嘛去了？", "Today's brain teaser: the other 98-plus tons, | where did they go?"),
 ("认识主角：小谷，|一百吨重，就为了扔一吨。", "Meet our hero, Gu: | a hundred tons, built to throw one."),
 ("答案一：绝大部分是燃料，|几分钟就烧光了。", "Answer one: most of it is fuel, | burned in a few minutes."),
 ("为啥要烧这么多？|因为它得跑得飞快。", "Why so much? | Because it has to go incredibly fast."),
 ("在五百公里高绕地球转，|速度大约每秒七点六公里。", "To circle Earth 500 km up, | you need about 7.6 km per second."),
 ("这是步枪子弹的七八倍，|北京到上海，两分多钟。", "Seven or eight times a rifle bullet: | Beijing to Shanghai in about two minutes."),
 ("反转一：难的不是“上去”。|五百公里，开车也就半天。", "Twist one: going up is not the hard part. | 500 km is half a day's drive."),
 ("真正难的是横着跑，|快到一边往下掉，一边绕过地球。", "The hard part is going sideways, | so fast that you fall around the Earth."),
 ("就像扔球：扔得越快，落得越远，|快到地面弯下去的速度追上它，就再也落不了地。", "Like throwing a ball: faster means farther, | until the ground curves away as fast as it falls."),
 ("这就是轨道：|一直在掉，永远掉不到。", "That is an orbit: | always falling, never landing."),
 ("反转二：燃料越多，|要推的重量也越多。", "Twist two: more fuel | means more weight to push."),
 ("火箭靠往后喷气往前跑，|就像在冰面上往后扔球，人就往前滑。", "A rocket throws gas backward to go forward, | like throwing balls behind you on ice."),
 ("可燃料本身也有重量：|多带的燃料，得先把自己推起来。", "But fuel has weight: | extra fuel must first lift itself."),
 ("这就是火箭方程：速度每多一截，|燃料要成倍地往上翻。", "That is the rocket equation: each step of speed | multiplies the fuel you need."),
 ("我们按固体火箭粗算：|要跑出每秒九公里多，", "Our rough estimate for a solid rocket: | to reach over 9 km per second,"),
 ("起飞重量得是最后重量的三十倍左右，|九成七都得是燃料。", "liftoff weight must be about 30 times the final weight. | 97 percent fuel."),
 ("可装燃料的壳子加发动机，|就远不止那百分之三。", "But the tanks and engines alone | weigh far more than 3 percent."),
 ("反转三：所以火箭要边飞边扔。|小谷有四节：三级固体，加一级液体。", "Twist three: so rockets drop pieces as they fly. | Gu has four stages: three solid, one liquid."),
 ("烧空一节，扔一节，|后面就不用背着空罐子跑。", "Burn a stage, drop it, | and stop hauling empty tanks."),
 ("就像接力赛：跑累的下场，|新的那棒接着冲。", "Like a relay race: the tired runner steps off, | a fresh one sprints on."),
 ("一棒接一棒，|最后把一点三吨推到每秒七点六公里。", "Leg after leg, | until 1.3 tons hits 7.6 km per second."),
 ("友情提示：大火箭能做到百分之四左右，|小火箭普遍更低。", "Fine print: big rockets reach around 4 percent; | small ones usually less."),
 ("液体燃料喷得更快，|同样的燃料能多跑一截。", "Liquid fuel shoots out faster, | so the same fuel goes farther."),
 ("固体火箭的好处是简单、准备快，|还能在海上发射。", "Solid rockets are simple and quick to prepare, | and can even launch from sea."),
 ("所以那九十八吨去哪了？|大多烧成了气，空壳子掉了回来。", "So where did the 98 tons go? | Mostly burned to gas; the empty shells fell back."),
 ("下次看到“一箭四星”，|记得底下有一百吨在帮忙。", "Next time you hear four satellites, one rocket, | remember the hundred tons underneath."),
 ("小谷说：我一百吨，|就为了把这一吨扔得足够快。", "Gu says: I weigh a hundred tons | just to throw this one ton fast enough."),
]
TITLE = {"zh": "百吨火箭只送一吨上天？", "en": "100-Ton Rocket, 1-Ton Payload?"}

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
    return T(a, x, y, s * 1.5, text, c=c, d=d)


def big(a, x, y, text, c="red", d=0.0, s=140):
    return BIG(a, x, y, text, c=c, d=d, s=s)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def man(a, x, y, k=1.4, d=0.0, arms="down", amp=3):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": amp, "hz": 1.6}]


def gu(a, x, y, k=1.0, d=0.0, mood="happy", dx=0, dy=0, dur=1.2, flame=True):
    i = uid("gu")
    E = cute_rocket(x, y, k, a, idp=i, mood=mood, flame=flame) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if dx or dy:
        E.append(sh(a, i + "*", dx, dy, d + 0.3, dur))
    return E


def ball(a, x, y, dx, dy, d=0.0, c="red", dur=1.0, r=18):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, dur)]


def sat(a, x, y, s=120, d=0.0):
    i = uid("st")
    return [{"t": "icon", "at": a, "id": i, "name": "satellite", "x": x, "y": y, "size": s, "c": "blue"}, pop(a, i, d), wig(a, i, (x, y), 10, 1.5)]


def earth(a, x, y, r=260, d=0.0):
    i = uid("ea")
    return [O(a, x, y, r, c="ink", fill="blue", idp=i), pop(a, i, d), spin(a, i, (x, y), 6),
            P(a, f"M{x - r * .6},{y - r * .2} Q{x - r * .2},{y - r * .5} {x + r * .1},{y - r * .2} Q{x + r * .3},{y + r * .1} {x - r * .1},{y + r * .3}", c="green", w=10, idp=i)]


def orbit(a, x, y, r, d=0.0, n=1, c="red"):
    """A dashed orbit ring with satellites spinning around."""
    i = uid("ob")
    E = [O(a, x, y, r, c=c, idp=i, sw=4), pop(a, i, d), wig(a, i, (x, y), 1, 0.5)]
    for q in range(n):
        j = uid("os")
        ang = 2 * math.pi * q / n
        E += [{"t": "icon", "at": a, "id": j, "name": "satellite", "x": x + r * math.cos(ang), "y": y + r * math.sin(ang), "size": 90, "c": "blue"},
              pop(a, j, d + 0.1 + 0.08 * q), spin(a, j, (x, y), 30)]
    return E


def stage(a, x, base, h, c, d=0.0, w=90):
    """One rocket stage block drawn upward from base."""
    i = uid("sg")
    return [R(a, x - w / 2, base - h, w, h, c="ink", fill=c, idp=i), pop(a, i, d), wig(a, i, (x, base), 1, 2)], i


def stack(a, x, base, d=0.0, drop=(), hs=(220, 150, 100, 60)):
    """Gu's four stages stacked; stages in drop fall away and fade one after another."""
    E = []
    y = base
    cols = ("gold", "gold", "gold", "blue")
    for q, h in enumerate(hs):
        e, i = stage(a, x, y, h, cols[q], d + 0.06 * q)
        E += e
        if q in drop:
            E += [sh(a, i, -60 - 40 * q, 500, d + 0.4 + 0.5 * drop.index(q), 0.8), rot(a, i, -40, (x, y - h / 2), d + 0.4 + 0.5 * drop.index(q), 0.8)]
        y -= h + 6
    j = uid("cap")
    E += [P(a, f"M{x - 45},{y} Q{x},{y - 110} {x + 45},{y} Z", c="ink", w=5, fill="red", idp=j), pop(a, j, d + 0.3), wig(a, j, (x, y), 2, 2)]
    return E


def tank(a, x, base, w, h, level, d=0.0, to=None, c="gold"):
    """A fuel tank; level drains to `to` with a grow."""
    i, j = uid("tk"), uid("fl")
    E = [R(a, x, base - h, w, h, c="ink", idp=i), pop(a, i, d), wig(a, i, (x + w / 2, base), 1, 1),
         R(a, x, base - h * level, w, h * level, c=c, fill=c, idp=j), pop(a, j, d + 0.1), wig(a, j, (x + w / 2, base), 1, 3)]
    if to is not None:
        E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x + w / 2, base], "dur": 1.6, "delay": d + 0.4, "to": to})
    return E


def exhaust(a, x, y, n=4, d=0.0, dy=300, c="muted"):
    return [ball(a, x + 30 * (q % 2 * 2 - 1), y, 40 * (q % 2 * 2 - 1), dy, d + 0.15 * q, c=c, dur=0.8, r=22) for q in range(n)]


def runner(a, x, y, d=0.0, dx=0):
    i = uid("rn")
    E = stick(x, y, 1.0, a, idp=i, arms="up") + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                               {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": 10, "hz": 3}]
    if dx:
        E.append(sh(a, i + "*", dx, 0, d + 0.3, 1.6))
    return E


# ---------- boards ----------
bd(0, gu(0, 600, 600, 1.4, 0.0, dy=-120, dur=2.0), big(0, 1300, 380, "100 吨", c="red", d=0.1, s=150), arr(0, 1300, 520, 1300, 700, c="ink", d=0.3), big(0, 1300, 820, "1 吨", c="blue", d=0.4, s=110))
bd(0.5, gu(0.5, 960, 650, 1.1, 0.0, mood="o"), ic(0.5, "question", 600, 500, 200, 0.2, mv="wig", c="red"), ic(0.5, "question", 1350, 500, 160, 0.3, mv="wig", c="red"), exhaust(0.5, 960, 850, 4, 0.2, 200))
bd(1, gu(1, 600, 700, 1.0, 0.0, dy=-250, dur=2.5), [sat(1, 1100 + 180 * q, 350 + 60 * (q % 2), 120, 0.2 + 0.08 * q) for q in range(4)], t(1, 1350, 700, 50, "11 月 7 日 · 酒泉", c="blue", d=0.2))
bd(1.5, earth(1.5, 960, 1100, 420, 0.0), orbit(1.5, 960, 1100, 620, 0.1, n=4), big(1.5, 1550, 330, "535 公里", c="red", d=0.3, s=100))
bd(2, gu(2, 650, 600, 1.0, 0.0, mood="sad", flame=False), rot(2, "gu", 0, (0, 0), 0, 0.1) if False else [], cross(2, 650, 600, d=0.3), t(2, 1300, 450, 64, "1 月：首飞失利", c="muted", d=0.2), exhaust(2, 650, 450, 3, 0.2, -200, c="muted"))
bd(2.5, gu(2.5, 650, 700, 1.0, 0.0, dy=-300, dur=1.6), check(2.5, 1300, 500, d=0.3), t(2.5, 1300, 750, 70, "复飞成功", c="green", d=0.4), star(2.5, 1550, 350, 0.5, r=40))
bd(3, big(3, 650, 380, "起飞 100 吨", c="red", d=0.0, s=110), tank(3, 450, 950, 400, 400, 1.0, 0.1), gu(3, 1350, 650, 1.0, 0.2))
bd(3.5, bar(3.5, 600, 950, 260, 650, "red", 0.0, 1.0), bar(3.5, 1100, 950, 260, 9, "blue", 0.4), t(3.5, 730, 1010, 40, "起飞"), t(3.5, 1230, 1010, 40, "入轨"), big(3.5, 1230, 780, "1.3 吨", c="blue", d=0.5, s=90), sat(3.5, 1600, 500, 140, 0.3))
bd(4, big(4, 960, 330, "1.3 ÷ 100", c="ink", d=0.0, s=130), [ball(4, 500 + 100 * q, 700, 0, 180, 0.2 + 0.05 * q, c="gold", r=26) for q in range(8)], ball(4, 1400, 700, 0, -250, 0.6, c="blue", r=30))
bd(4.5, big(4.5, 960, 400, "1.3%", c="red", d=0.0, s=200), [O(4.5, 560 + 80 * (q % 10), 720 + 80 * (q // 10), 28, c="ink", fill="blue" if q == 0 else "paper", idp=f"dt{q}") for q in range(20)],
   [pop(4.5, f"dt{q}", 0.1 + 0.02 * q) for q in range(20)], [wig(4.5, f"dt{q}", (560 + 80 * (q % 10), 720 + 80 * (q // 10)), 4, 2) for q in range(0, 20, 4)])
bd(5, gu(5, 600, 600, 1.1, 0.0), t(5, 1300, 450, 60, "国际领先", c="green", d=0.2), [star(5, 1100 + 120 * q, 650, 0.3 + 0.08 * q, r=34) for q in range(4)], man(5, 1300, 1000, 1.0, 0.3, arms="up", amp=8))
bd(5.5, [gu(5.5, 450 + 340 * q, 650, 0.6, 0.06 * q) for q in range(4)], check(5.5, 450, 300, d=0.4), t(5.5, 1100, 950, 50, "同类火箭里", c="blue", d=0.3))
bd(6, big(6, 960, 250, "烧脑问题", c="red", d=0.0, s=120), gu(6, 650, 680, 1.0, 0.1, mood="o"), ic(6, "question", 1300, 650, 240, 0.2, mv="wig", c="red"))
bd(6.5, big(6.5, 960, 330, "98 吨去哪了？", c="red", d=0.0, s=130), [ball(6.5, 600 + 120 * q, 650, 80 * (q - 3), 300, 0.2 + 0.06 * q, c="muted", r=30) for q in range(7)], ic(6.5, "magnifier", 1600, 750, 200, 0.3, mv="wig"))
bd(7, gu(7, 960, 600, 2.0, 0.0), t(7, 1450, 600, 80, "小谷", c="blue", d=0.3), star(7, 500, 380, 0.4, r=40), star(7, 1420, 380, 0.5, r=40))
bd(7.5, gu(7.5, 600, 650, 1.3, 0.0), arr(7.5, 800, 650, 1100, 500, c="red", d=0.3), sat(7.5, 1300, 400, 180, 0.4), big(7.5, 1350, 750, "扔一吨", c="red", d=0.5, s=100))
bd(8, tank(8, 600, 950, 400, 600, 0.95, 0.0, to=0.05), t(8, 1350, 400, 70, "燃料", c="red", d=0.2), ic(8, "flame", 1350, 700, 200, 0.3, mv="wig", c="red"))
bd(8.5, ic(8.5, "clock", 600, 550, 260, 0.0, mv="spin"), big(8.5, 1300, 450, "几分钟", c="red", d=0.2, s=130), exhaust(8.5, 1300, 650, 5, 0.3, 300))
bd(9, ic(9, "question", 600, 550, 240, 0.0, mv="wig", c="red"), tank(9, 1000, 900, 250, 500, 0.9, 0.1), tank(9, 1350, 900, 250, 500, 0.9, 0.2))
bd(9.5, gu(9.5, 400, 600, 0.8, 0.0, dx=1100, dur=1.5), [arr(9.5, 300, 400 + 150 * q, 700, 400 + 150 * q, c="blue", d=0.2 + 0.1 * q) for q in range(3)], t(9.5, 1300, 900, 64, "飞快", c="red", d=0.3))
bd(10, earth(10, 960, 600, 300, 0.0), orbit(10, 960, 600, 420, 0.1, n=2), t(10, 1600, 300, 50, "五百公里高", c="blue", d=0.3))
bd(10.5, big(10.5, 960, 380, "7.6 公里/秒", c="red", d=0.0, s=150), gu(10.5, 400, 800, 0.6, 0.2, dx=1100, dur=1.2), ic(10.5, "clock", 1600, 800, 160, 0.3, mv="spin"))
bd(11, ic(11, "rocket", 500, 450, 200, 0.0, mv="wig", c="red"), ball(11, 450, 750, 300, 0, 0.2, c="ink", r=14), [ball(11, 450, 850, 1100, 0, 0.3, c="red", r=14)], t(11, 1300, 400, 70, "子弹 ×7~8", c="red", d=0.3))
bd(11.5, ic(11.5, "map_pin", 500, 600, 180, 0.0, mv="bob", c="red"), ic(11.5, "map_pin", 1450, 600, 180, 0.1, mv="bob", c="blue"), gu(11.5, 550, 750, 0.4, 0.2, dx=850, dur=1.6),
   t(11.5, 500, 400, 50, "北京", d=0.1), t(11.5, 1450, 400, 50, "上海", d=0.2), big(11.5, 960, 950, "两分多钟", c="red", d=0.5, s=90))
bd(12, big(12, 960, 250, "反转一", c="red", d=0.0, s=140), gu(12, 650, 700, 0.9, 0.1, dy=-150), ic(12, "car", 1300, 750, 220, 0.2, mv="wig", c="blue"))
bd(12.5, ic(12.5, "car", 500, 850, 200, 0.0, mv="wig"), sh(12.5, "x", 0, 0, 0, 0.1) if False else [], arr(12.5, 650, 850, 1400, 850, c="ink", d=0.2), t(12.5, 1000, 500, 70, "500 公里 ≈ 半天", c="blue", d=0.3), ic(12.5, "clock", 1500, 700, 140, 0.3, mv="spin"))
bd(13, earth(13, 960, 700, 300, 0.0), gu(13, 960, 300, 0.5, 0.1, dx=500, dy=150, dur=2.0), arr(13, 960, 300, 1500, 300, c="red", d=0.3), t(13, 400, 250, 60, "横着跑", c="red", d=0.3))
bd(13.5, earth(13.5, 960, 600, 280, 0.0), orbit(13.5, 960, 600, 400, 0.1, n=1), arr(13.5, 960, 200, 960, 300, c="blue", d=0.3), t(13.5, 1600, 300, 50, "一边掉", c="blue", d=0.3), t(13.5, 1600, 900, 50, "一边绕", c="red", d=0.4))
bd(14, man(14, 300, 900, 1.3, 0.0, arms="up"), [ball(14, 400, 600, 300 + 350 * q, 300 - 40 * q, 0.2 + 0.25 * q, c=("blue", "gold", "red")[q], dur=1.0) for q in range(3)],
   P(14, "M100,950 L1800,950", c="green", w=8, idp="gr14"), pop(14, "gr14", 0.0), wig(14, "gr14", (960, 950), 2, 1))
bd(14.5, earth(14.5, 960, 1000, 520, 0.0), man(14.5, 960, 480, 0.8, 0.1, arms="up"), ball(14.5, 1000, 420, 600, 250, 0.3, c="red", dur=2.0), t(14.5, 960, 200, 60, "地面弯下去", c="blue", d=0.4))
bd(15, earth(15, 960, 560, 260, 0.0), orbit(15, 960, 560, 400, 0.1, n=3), big(15, 960, 1010, "一直在掉，永远掉不到", c="red", d=0.4, s=70))
bd(15.5, gu(15.5, 600, 600, 1.0, 0.0, mood="happy"), orbit(15.5, 1300, 550, 250, 0.1, n=2), earth(15.5, 1300, 550, 140, 0.2))
bd(16, big(16, 960, 250, "反转二", c="red", d=0.0, s=140), tank(16, 500, 950, 250, 450, 0.9, 0.1), tank(16, 850, 950, 250, 450, 0.9, 0.2), gu(16, 1450, 650, 0.9, 0.3, mood="o"))
bd(16.5, bar(16.5, 500, 950, 200, 250, "gold", 0.0), bar(16.5, 800, 950, 200, 450, "gold", 0.2), bar(16.5, 1100, 950, 200, 700, "red", 0.4), man(16.5, 1550, 950, 1.2, 0.3, arms="up", amp=8))
bd(17, gu(17, 960, 500, 1.1, 0.0, dy=-150), exhaust(17, 960, 700, 6, 0.1, 300), arr(17, 1250, 700, 1250, 400, c="red", d=0.3), arr(17, 700, 450, 700, 750, c="blue", d=0.3))
bd(17.5, man(17.5, 900, 800, 1.3, 0.0, arms="up"), sh(17.5, "x", 0, 0, 0, 0) if False else [], [ball(17.5, 850, 650, -500, 0, 0.2 + 0.2 * q, c="red", r=20) for q in range(3)],
   P(17.5, "M100,900 L1820,900", c="blue", w=8, idp="ice"), pop(17.5, "ice", 0.0), wig(17.5, "ice", (960, 900), 1, 1), arr(17.5, 1100, 650, 1500, 650, c="green", d=0.4))
bd(18, tank(18, 550, 950, 300, 600, 0.9, 0.0), ic(18, "block_force", 1250, 550, 220, 0.2, mv="wig"), arr(18, 1250, 750, 1250, 950, c="red", d=0.3))
bd(18.5, tank(18.5, 500, 950, 220, 300, 0.9, 0.0), arr(18.5, 610, 600, 610, 450, c="blue", d=0.2), tank(18.5, 900, 950, 220, 500, 0.9, 0.2), arr(18.5, 1010, 400, 1010, 250, c="blue", d=0.4),
   gu(18.5, 1500, 650, 0.8, 0.3, mood="sad"))
bd(19, t(19, 960, 250, 70, "Δv = v · ln(起飞 ÷ 最后)", c="blue", d=0.0), bar(19, 450, 950, 150, 80, "gold", 0.2), bar(19, 700, 950, 150, 180, "gold", 0.4), bar(19, 950, 950, 150, 360, "gold", 0.6),
   bar(19, 1200, 950, 150, 600, "red", 0.8))
bd(19.5, big(19.5, 960, 350, "成倍往上翻", c="red", d=0.0, s=130), [ball(19.5, 500 + 160 * q, 950, 0, -150 * (q + 1) * 0.6, 0.2 + 0.08 * q, c="gold", r=24) for q in range(7)])
bd(20, t(20, 960, 250, 60, "我们的粗算", c="muted", d=0.0), gu(20, 600, 650, 1.0, 0.1), big(20, 1300, 550, "9+ 公里/秒", c="red", d=0.2, s=110), exhaust(20, 600, 850, 4, 0.3, 200))
bd(20.5, ic(20.5, "flame", 600, 550, 240, 0.0, mv="wig", c="red"), t(20.5, 1250, 450, 60, "固体喷气 ≈ 2.8 公里/秒", c="blue", d=0.2), arr(20.5, 800, 600, 1100, 600, c="ink", d=0.3), ic(20.5, "ruler", 1250, 750, 160, 0.4, mv="wig"))
bd(21, big(21, 960, 300, "× 30", c="red", d=0.0, s=200), bar(21, 600, 950, 200, 600, "gold", 0.2), bar(21, 1100, 950, 200, 20, "blue", 0.5), gu(21, 1550, 700, 0.6, 0.3))
bd(21.5, big(21.5, 960, 330, "97% 是燃料", c="red", d=0.0, s=130), tank(21.5, 700, 1000, 500, 500, 0.97, 0.2), ic(21.5, "flame", 1500, 700, 160, 0.4, mv="wig", c="red"))
bd(22, tank(22, 500, 950, 300, 600, 0.0, 0.0), ic(22, "engine", 1100, 650, 220, 0.2, mv="wig"), ic(22, "gear", 1450, 600, 160, 0.3, mv="spin"))
bd(22.5, big(22.5, 960, 330, "3% 装不下", c="red", d=0.0, s=130), cross(22.5, 960, 650, d=0.3), gu(22.5, 600, 700, 0.7, 0.1, mood="sad"), gu(22.5, 1350, 700, 0.7, 0.2, mood="sad"))
bd(23, big(23, 960, 230, "反转三", c="red", d=0.0, s=140), stack(23, 960, 1000, 0.1, drop=(0,)), ic(23, "wind", 1450, 600, 160, 0.3, mv="wig", c="blue"))
bd(23.5, stack(23.5, 700, 1000, 0.0), t(23.5, 1350, 350, 54, "三级固体", c="gold", d=0.2), t(23.5, 1350, 550, 54, "+ 一级液体", c="blue", d=0.3), arr(23.5, 1100, 400, 800, 800, c="red", d=0.4))
bd(24, stack(24, 960, 1000, 0.0, drop=(0, 1)), exhaust(24, 960, 1000, 3, 0.1, 100, c="muted"), t(24, 1450, 400, 64, "烧空就扔", c="red", d=0.3))
bd(24.5, stack(24.5, 700, 1000, 0.0, drop=(0, 1, 2)), cross(24.5, 1400, 650, d=0.3), tank(24.5, 1300, 900, 200, 300, 0.0, 0.2))
bd(25, runner(25, 400, 900, 0.0, dx=500), runner(25, 1000, 900, 0.2, dx=600), P(25, "M100,950 L1820,950", c="red", w=8, idp="tr25"), pop(25, "tr25", 0.0), wig(25, "tr25", (960, 950), 1, 1))
bd(25.5, runner(25.5, 600, 900, 0.0, dx=900), man(25.5, 400, 900, 1.0, 0.1, arms="down"), ic(25.5, "flame", 1500, 450, 160, 0.3, mv="wig", c="red"), t(25.5, 960, 300, 60, "下一棒", c="blue", d=0.3))
bd(26, stack(26, 500, 1000, 0.0, drop=(0, 1, 2)), arr(26, 700, 500, 1100, 350, c="red", d=0.3), sat(26, 1300, 330, 160, 0.4))
bd(26.5, earth(26.5, 960, 650, 260, 0.0), orbit(26.5, 960, 650, 390, 0.1, n=4), big(26.5, 960, 170, "1.3 吨 · 7.6 公里/秒", c="red", d=0.4, s=80))
bd(27, big(27, 960, 250, "友情提示", c="blue", d=0.0, s=120), bar(27, 600, 950, 200, 400, "blue", 0.2), bar(27, 1100, 950, 200, 130, "gold", 0.4), t(27, 700, 1010, 40, "大火箭 ~4%", d=0.2), t(27, 1200, 1010, 40, "小火箭 ~1%", d=0.4))
bd(27.5, gu(27.5, 600, 650, 1.6, 0.0), gu(27.5, 1300, 750, 0.7, 0.2), arr(27.5, 900, 400, 1150, 550, c="ink", d=0.3))
bd(28, ic(28, "water", 600, 550, 220, 0.0, mv="wig", c="blue"), exhaust(28, 600, 750, 5, 0.1, 300, c="blue"), arr(28, 900, 600, 1500, 600, c="blue", d=0.3), ic(28, "flame", 1600, 500, 160, 0.3, mv="wig", c="red"))
bd(28.5, bar(28.5, 600, 950, 200, 650, "blue", 0.0), bar(28.5, 1100, 950, 200, 450, "gold", 0.2), t(28.5, 700, 1010, 40, "液体"), t(28.5, 1200, 1010, 40, "固体"), gu(28.5, 1600, 600, 0.6, 0.3))
bd(29, ic(29, "gear", 600, 550, 220, 0.0, mv="spin"), check(29, 900, 550, d=0.2), ic(29, "clock", 1300, 550, 220, 0.3, mv="spin"), check(29, 1600, 550, d=0.4))
bd(29.5, P(29.5, "M100,800 Q480,740 960,800 Q1440,860 1820,800", c="blue", w=8, idp="sea"), pop(29.5, "sea", 0.0), wig(29.5, "sea", (960, 800), 10, 0.8),
   R(29.5, 760, 800, 400, 80, c="ink", fill="muted", idp="ship"), pop(29.5, "ship", 0.1), bob(29.5, "ship", 10, 0.8), gu(29.5, 960, 600, 0.7, 0.3, dy=-200, dur=1.5), t(29.5, 960, 200, 60, "海上发射", c="blue", d=0.3))
bd(30, big(30, 960, 250, "98 吨？", c="red", d=0.0, s=140), exhaust(30, 700, 950, 6, 0.1, -300, c="muted"), ic(30, "cloud", 1300, 550, 220, 0.3, mv="bob", c="muted"))
bd(30.5, stack(30.5, 700, 900, 0.0, drop=(0, 1, 2)), ic(30.5, "globe", 1400, 800, 200, 0.2, mv="spin", c="blue"), t(30.5, 1400, 400, 60, "空壳掉回来", c="red", d=0.4))
bd(31, gu(31, 600, 650, 1.1, 0.0, dy=-150), [sat(31, 1100 + 170 * q, 400 + 80 * (q % 2), 120, 0.2 + 0.08 * q) for q in range(4)], t(31, 1350, 750, 64, "一箭四星", c="blue", d=0.3))
bd(31.5, stack(31.5, 960, 1000, 0.0), big(31.5, 1450, 450, "100 吨", c="red", d=0.3, s=120), [man(31.5, 450 + 150 * q, 1000, 0.7, 0.2 + 0.06 * q, arms="up", amp=6) for q in range(3)])
bd(32, gu(32, 700, 600, 1.6, 0.0), big(32, 1350, 450, "100 吨", c="red", d=0.2, s=120), arr(32, 1100, 600, 1500, 750, c="ink", d=0.4))
bd(32.5, gu(32.5, 500, 750, 0.9, 0.0, dy=-200, dur=1.5), sat(32.5, 1000, 400, 200, 0.2), arr(32.5, 1150, 400, 1600, 400, c="red", d=0.3), big(32.5, 1300, 800, "够快！", c="red", d=0.5, s=120))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"11 月 7 日": "十一月七日", "4 颗": "四颗", "Ceres-2": "Ceres 2"})
