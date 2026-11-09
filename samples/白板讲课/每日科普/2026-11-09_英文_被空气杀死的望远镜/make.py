"""Daily science 2026-11-09 (English): "Killed by Almost-Empty Air?"  (NASA's Swift observatory re-entered on 2026-11-04)
News: NASA's Neil Gehrels Swift Observatory re-entered at 7:39 a.m. EST on Wednesday 2026-11-04 over North Sumatra, Indonesia (U.S. Space Force);
  launched 2004 (Nov 20) for a planned 2-year mission, worked nearly 22 years; three telescopes; studied gamma-ray bursts (ScienceDaily 2026-11-06).
  Mass about 3,200 lb (~1,450 kg); last observation 2026-10-20 at about 275 km (171 miles); NASA risk to anyone on Earth about 1 in 2,100; 11-hour
  re-entry window (Tech Insider, relaying NASA/CNN).
  Initial orbit about 585 x 604 km; decay "natural, made worse by increased solar activity" (NASA via Wikipedia); 1,000th burst GRB 151027B (2015).
  Rescue: NASA's ~$30M contract (Sept 2025) with Katalyst Space; robotic spacecraft LINK launched July 2026 on an air-dropped Pegasus XL;
  the reboost did not happen in time and NASA ended its part on 2026-09-03; the exact reasons are not public (Shattered, Tech Insider).
Trending: ScienceDaily top science news ("NASA's Swift telescope falls to Earth after nearly 22 years in space"), CNN / Space.com coverage.
Textbook physics (said plainly): orbit ~7.6 km/s, ~96-minute period; drag lowers the orbit and the satellite speeds up (the "drag paradox");
  re-entry heating comes mostly from compressing the air in front (shock heating), not rubbing friction; a busy Sun heats and swells the thermosphere.
Sources:
- https://sciencedaily.com/releases/2026/11/261105224545.htm
- https://tech-insider.org/nasa-swift-observatory-re-entry-1-in-2100-risk-2026/
- https://shattered.io/swift-failed-rescue-katalyst-link-three-reentry-forecasts-2026/
- https://en.wikipedia.org/wiki/Neil_Gehrels_Swift_Observatory
- https://orbitalradar.com/swift-tracker
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402,F401
                     star, uid, wig)
from popkit import cute_battery, cute_claw, cute_meteor, cute_probe, cute_rocket, stick  # noqa: E402

S = [
 ("一台 NASA 望远镜刚刚从天上掉下来，|十一月四日在印度尼西亚上空烧掉了。", "A NASA telescope just fell out of the sky. | It burned up over Indonesia on November fourth."),
 ("它叫 Swift（雨燕），|重约一千四百五十公斤。", "Its name was Swift. | It weighed about fourteen hundred and fifty kilos."),
 ("是什么杀死了它？|空气。几乎什么都没有的空气。", "What killed it? | Air. Almost nothing but air."),
 ("今天的烧脑问题：|几乎空荡荡的太空，怎么能把望远镜拽下来？", "Today's brain teaser: | how does nearly empty space pull down a telescope?"),
 ("认识 Swift：2004 年发射，|在大约六百公里高的地方。", "Meet Swift: launched in two thousand four, | about six hundred kilometers up."),
 ("它的任务：抓伽马射线暴，|宇宙里最猛烈的爆炸。", "Its job: catch gamma ray bursts, | the biggest explosions in the universe."),
 ("它能在大约一分钟里转身对准目标，|所以叫“雨燕”。", "It could swing around and point | in about a minute. Hence the name."),
 ("原计划只工作两年，|结果干了将近二十二年。", "Planned life: two years. | It worked for almost twenty two."),
 ("它抓到了一千多次伽马暴，|对一个两年的计划来说，相当不错。", "It caught more than a thousand of those bursts. | Not bad for a two year plan."),
 ("现在讲物理：在轨道上，|Swift 其实一直在往下掉。", "Now the physics. | In orbit, Swift is falling all the time."),
 ("只是它横着飞得太快，|总是掉不到地面上。", "It just moves sideways so fast | that it keeps missing the ground."),
 ("每秒大约七点六公里，|九十六分钟绕地球一圈。", "About seven point six kilometers per second. | Around the whole world in ninety six minutes."),
 ("可那么高的地方，还有一丁点空气，|就像一阵极轻的逆风。", "But up there, there's still a tiny bit of air. | Like a whisper of a headwind."),
 ("每绕一圈，这阵逆风|就偷走它一点点能量。", "Every orbit, that whisper steals | a tiny bit of energy."),
 ("能量少了，就降低一点；|越低空气越浓，偷得越多。", "Lose energy, drop a little lower. | Lower air is thicker, so it steals more."),
 ("像滚雪球：|一开始很慢，后来非常快。", "It's a snowball. | Slow at first, then very fast."),
 ("反转一：往下掉的时候，|Swift 反而越飞越快。", "Twist one: as it drops, | Swift actually speeds up."),
 ("轨道越低，绕得越快。|空气阻力让卫星加速，怪，但是真的。", "A lower orbit is a faster orbit. | Drag makes satellites go faster. Weird, but true."),
 ("反转二：是太阳|把空气变浓了。", "Twist two: the Sun | made the air thicker."),
 ("太阳活跃时，会把高层大气加热，|空气就像面包发酵一样鼓起来。", "When the Sun is very active, it heats the upper air, | and the air puffs up, like bread rising."),
 ("于是 Swift 那个高度，突然多了空气。|空气越多，阻力越大。", "Suddenly there's more air at Swift's height. | More air, more drag."),
 ("太阳正处在十一年周期里很忙的一段。|NASA 说，这让下降更快了。", "The Sun has been in a busy stretch of its eleven year cycle. | NASA says that made the decay worse."),
 ("到十月下旬，|Swift 只剩大约二百七十五公里高。", "By late October, | Swift was down to about two hundred seventy five kilometers."),
 ("于是 NASA 试了个新办法：|派机器人去救它。", "So NASA tried something new: | a robot rescue."),
 ("一家叫 Katalyst 的公司造了救援飞船 LINK，|要抓住 Swift，把它推高。", "A company called Catalyst built a robot spacecraft named Link, | to grab Swift and push it higher."),
 ("它七月发射，|用的是从飞机上扔下去的火箭。", "It launched in July, | on a rocket dropped from an airplane."),
 ("可救援没能及时成功，|具体原因还没有完全公开。", "But the rescue did not work out in time. | The exact reasons haven't been made fully public."),
 ("反转三：那团火球，|不是摩擦出来的。", "Twist three: the fireball | does not come from friction."),
 ("Swift 以每小时两万七千公里冲进浓空气，|前面的空气根本来不及让开。", "Swift hit thick air at about twenty seven thousand kilometers an hour. | The air in front couldn't get out of the way."),
 ("空气被猛压，就变得超级烫，|像打气筒会发热，只是猛烈得多。", "Squeezed air gets super hot, | like a bike pump getting warm, but far more extreme."),
 ("被压缩的空气发光，|飞船熔化、解体。", "That squeezed air glows, | and the spacecraft melts and breaks apart."),
 ("Swift 大部分都烧掉了。|NASA 估计，伤到地面任何人的概率约二千一百分之一。", "Most of Swift burned up. | NASA put the risk to anyone on the ground at about one in twenty one hundred."),
 ("友情提示：救援为什么失败，|目前公开的信息还不多。", "Fine print: why the rescue failed | is still mostly unexplained in public."),
 ("而且阻力跟着太阳变，|所以坠落时间总有十几个小时的误差。", "And drag changes with the Sun, | so reentry times always come with hours of uncertainty."),
 ("几乎没有的空气，怎么拽下望远镜？|每圈推一下，推了二十二年。", "So how does almost nothing pull down a telescope? | A tiny push, every orbit, for twenty two years."),
 ("Swift 因速度得名，|最后也是速度把它烧掉了。", "Swift was named for speed. | In the end, speed is what burned it."),
]
TITLE = {"zh": "被几乎没有的空气杀死的望远镜", "en": "Killed by Almost-Empty Air"}

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


def man(a, x, y, k=1.4, d=0.0, arms="down", amp=3):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": amp, "hz": 1.6}]


def char(fn, a, x, y, k=1.0, d=0.0, dx=0, dy=0, dur=1.2, dd=0.3, **kw):
    i = uid("ch")
    E = fn(x, y, k, a, idp=i, **kw) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if dx or dy:
        E.append(sh(a, i + "*", dx, dy, d + dd, dur))
    return E


def swift(a, x, y, k=1.0, d=0.0, mood="happy", **kw):
    return char(cute_probe, a, x, y, k, d, mood=mood, **kw)


def blaze(a, x, y, k=1.0, d=0.0, mood="o", **kw):
    return char(cute_meteor, a, x, y, k, d, mood=mood, **kw)


def link(a, x, y, k=1.0, d=0.0, mood="happy", **kw):
    return char(cute_claw, a, x, y, k, d, mood=mood, **kw)


def ball(a, x, y, dx, dy, d=0.0, c="red", dur=1.0, r=18):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, dur)]


def earth(a, x, y, r=200, d=0.0):
    """Earth with a green continent, slowly spinning."""
    i = uid("ea")
    return [O(a, x, y, r, c="ink", fill="blue", idp=i),
            P(a, f"M{x - r * .5},{y - r * .3} q{r * .3},{-r * .3} {r * .55},{-r * .05} q{r * .1},{r * .3} {-r * .15},{r * .45} q{-r * .35},{r * .1} {-r * .4},{-r * .4} Z",
              c="green", w=6, idp=i, fill="green"), pop(a, i, d), spin(a, i, (x, y), 12)]


def orbiter(a, cx, cy, r, d=0.0, rpm=30, c="red", n=1):
    """An orbit ring with dot(s) going round."""
    i = uid("or")
    E = [O(a, cx, cy, r, c="muted", idp=i, sw=3), pop(a, i, d)]
    for q in range(n):
        j = uid("od")
        E += [O(a, cx, cy - r, 18, c="ink", fill=c, idp=j), pop(a, j, d + 0.1), spin(a, j, (cx, cy), rpm + 6 * q)]
    return E


def air(a, x0, x1, y0, y1, n=8, d=0.0, c="muted", drift=0):
    """Wiggling air molecules scattered in a box."""
    E = []
    for q in range(n):
        j = uid("air")
        x = x0 + (x1 - x0) * ((q * 37) % 100) / 100
        y = y0 + (y1 - y0) * ((q * 61) % 100) / 100
        E += [O(a, x, y, 12, c=c, fill=c, idp=j), pop(a, j, d + 0.04 * q), wig(a, j, (x, y), 14, 2 + 0.3 * (q % 3))]
        if drift:
            E.append(sh(a, j, drift, 0, d + 0.3, 1.4))
    return E


def wind(a, x, y, n=3, d=0.0, dx=-260, c="blue"):
    E = []
    for q in range(n):
        j = uid("wd")
        E += [P(a, f"M{x},{y + 60 * q} q60,-30 120,0 q60,30 120,0", c=c, w=6, idp=j), pop(a, j, d + 0.1 * q), sh(a, j, dx, 0, d + 0.2 + 0.1 * q, 1.0),
              wig(a, j, (x + 120, y + 60 * q), 6, 2.5)]
    return E


def burst(a, x, y, r=90, d=0.0, c="gold"):
    """A spiky gamma-ray burst that pulses."""
    i = uid("gb")
    pts = []
    for q in range(16):
        import math
        rr = r if q % 2 == 0 else r * 0.45
        ang = q * math.pi / 8
        pts.append(f"{x + rr * math.cos(ang):.0f},{y + rr * math.sin(ang):.0f}")
    return [P(a, "M" + " L".join(pts) + " Z", c="red", w=5, idp=i, fill=c), pop(a, i, d), spin(a, i, (x, y), 30),
            {"t": "move", "at": a, "kind": "pulse", "targets": [i], "dur": 0.6, "delay": d + 0.4}]


def fall_curve(a, x0, y0, x1, y1, d=0.0, c="red"):
    i = uid("fc")
    return [P(a, f"M{x0},{y0} Q{x1 - 100},{y0} {x1},{y1}", c=c, w=6, idp=i, dash=True), pop(a, i, d)]


# ---------- boards ----------
bd(0, blaze(0, 900, 650, 1.2, 0.0, dx=-350, dy=250, dur=2.0), ic(0, "globe", 1500, 820, 220, 0.2, mv="spin", c="blue"), big(0, 1450, 520, "FELL!", c="red", d=0.3, s=150))
bd(0.5, earth(0.5, 960, 1050, 520, 0.0), blaze(0.5, 1300, 450, 0.7, 0.1, dx=-300, dy=250), ic(0.5, "map_pin", 700, 450, 160, 0.3, mv="bob", c="red"),
   t(0.5, 700, 260, 54, "Indonesia, Nov 4", c="red", d=0.4))
bd(1, swift(1, 700, 560, 1.6, 0.0), big(1, 1350, 380, "Swift", c="blue", d=0.2, s=160), [star(1, 1150 + 120 * q, 650, 0.3 + 0.1 * q, r=30) for q in range(4)])
bd(1.5, swift(1.5, 600, 600, 1.2, 0.0), big(1.5, 1300, 400, "~1,450 kg", c="red", d=0.2, s=130), R(1.5, 1100, 700, 400, 60, c="ink", fill="muted", idp="sc1"), pop(1.5, "sc1", 0.3),
   rot(1.5, "sc1", 8, (1300, 730), 0.5, 0.8), ic(1.5, "ruler", 1300, 870, 140, 0.4, mv="wig"))
bd(2, swift(2, 600, 550, 1.2, 0.0, mood="sad"), ic(2, "question", 1200, 450, 260, 0.2, mv="wig", c="red"), air(2, 1000, 1700, 700, 950, 8, 0.3))
bd(2.5, air(2.5, 300, 1600, 350, 900, 12, 0.0), big(2.5, 960, 500, "AIR", c="red", d=0.4, s=220))
bd(3, big(3, 960, 230, "Brain teaser", c="red", d=0.0, s=120), swift(3, 600, 650, 1.0, 0.1, mood="o"), air(3, 1000, 1600, 500, 900, 6, 0.2), ic(3, "question", 1350, 650, 200, 0.3, mv="wig", c="red"))
bd(3.5, earth(3.5, 960, 1100, 450, 0.0), swift(3.5, 960, 350, 0.8, 0.1, dy=200, dur=2.0, dd=0.4), wind(3.5, 1300, 300, 3, 0.3), t(3.5, 500, 300, 50, "nearly empty", c="muted", d=0.3))
bd(4, swift(4, 1300, 450, 1.0, 0.0), char(cute_rocket, 4, 500, 750, 0.8, 0.1, dy=-300, dur=1.4), big(4, 1300, 850, "2004", c="blue", d=0.3, s=130))
bd(4.5, earth(4.5, 960, 1150, 500, 0.0), swift(4.5, 960, 300, 0.7, 0.1), arr(4.5, 1300, 640, 1300, 380, c="red", d=0.3), big(4.5, 1550, 500, "~600 km", c="red", d=0.4, s=110))
bd(5, swift(5, 500, 600, 1.1, 0.0), burst(5, 1350, 450, 150, 0.2), arr(5, 1200, 520, 700, 580, c="gold", d=0.4), t(5, 1350, 800, 54, "gamma ray burst", c="red", d=0.4))
bd(5.5, burst(5.5, 600, 500, 180, 0.0), burst(5.5, 1300, 400, 110, 0.2, c="red"), burst(5.5, 1100, 750, 80, 0.3), big(5.5, 960, 920, "biggest booms", c="red", d=0.4, s=100))
bd(6, swift(6, 800, 560, 1.4, 0.0), rot(6, "ch*", 0, (800, 560), 0, 0) if False else [], ic(6, "clock", 1450, 500, 220, 0.2, mv="spin"), burst(6, 300, 300, 70, 0.4),
   arr(6, 600, 350, 380, 320, c="gold", d=0.5))
bd(6.5, big(6.5, 960, 300, "~1 minute", c="blue", d=0.0, s=150), [ball(6.5, 500 + 220 * q, 650, 0, -100 - 60 * q, 0.2 + 0.08 * q, c="blue") for q in range(5)], ic(6.5, "wind", 1500, 750, 160, 0.3, mv="wig", c="blue"))
bd(7, bar(7, 600, 950, 240, 120, "blue", 0.0), t(7, 720, 1010, 40, "plan: 2 yr"), bar(7, 1100, 950, 240, 640, "red", 0.4, 1.4), t(7, 1220, 1010, 40, "actual"), swift(7, 1600, 450, 0.6, 0.3))
bd(7.5, big(7.5, 960, 330, "~22 years", c="red", d=0.0, s=170), ic(7.5, "clock", 600, 750, 180, 0.2, mv="spin"), ic(7.5, "clock", 1320, 750, 180, 0.3, mv="spin"), star(7.5, 960, 750, 0.4, r=50))
bd(8, [burst(8, 400 + 280 * q, 450 + 120 * (q % 2), 70, 0.08 * q) for q in range(5)], big(8, 960, 800, "1,000+", c="red", d=0.4, s=150))
bd(8.5, swift(8.5, 700, 580, 1.3, 0.0, mood="happy"), [check(8.5, 1200 + 150 * q, 500, d=0.2 + 0.1 * q) for q in range(3)], star(8.5, 1350, 750, 0.5, r=50))
bd(9, t(9, 960, 220, 64, "physics time", c="blue", d=0.0), earth(9, 960, 1100, 450, 0.1), swift(9, 960, 380, 0.7, 0.2, dy=120, dur=1.6), arr(9, 1200, 380, 1200, 560, c="red", d=0.4))
bd(9.5, ball(9.5, 400, 300, 0, 600, 0.0, c="red", dur=1.2, r=30), ball(9.5, 700, 300, 0, 600, 0.2, c="red", dur=1.2, r=30), earth(9.5, 1300, 650, 250, 0.1),
   orbiter(9.5, 1300, 650, 380, 0.3, rpm=40), big(9.5, 550, 1000, "falling", c="red", d=0.4, s=90))
bd(10, earth(10, 960, 600, 250, 0.0), fall_curve(10, 960, 220, 1330, 600, 0.2), swift(10, 960, 220, 0.4, 0.1), arr(10, 1000, 220, 1300, 220, c="blue", d=0.3), orbiter(10, 960, 600, 380, 0.4, rpm=50))
bd(10.5, ic(10.5, "earth_arc", 960, 850, 500, 0.0, mv="bob", c="blue"), [ball(10.5, 300, 400 + 30 * q, 700 + 200 * q, 150 + 100 * q, 0.1 + 0.15 * q, c=("muted", "gold", "red")[q], dur=1.2) for q in range(3)],
   t(10.5, 1300, 250, 54, "keeps missing", c="blue", d=0.4))
bd(11, big(11, 960, 300, "7.6 km/s", c="red", d=0.0, s=170), [ball(11, 300, 650 + 60 * q, 1300, 0, 0.1 + 0.1 * q, c="red", dur=0.6) for q in range(3)], ic(11, "wind", 400, 850, 140, 0.3, mv="wig", c="blue"))
bd(11.5, earth(11.5, 960, 600, 250, 0.0), orbiter(11.5, 960, 600, 350, 0.1, rpm=60, n=2), ic(11.5, "clock", 1550, 400, 180, 0.2, mv="spin"), big(11.5, 1550, 750, "96 min", c="blue", d=0.3, s=110))
bd(12, swift(12, 1300, 550, 1.0, 0.0), air(12, 300, 900, 300, 900, 7, 0.2, drift=200), ic(12, "magnifier", 600, 600, 220, 0.3, mv="wig"))
bd(12.5, swift(12.5, 1300, 550, 1.0, 0.0, mood="o"), wind(12.5, 500, 450, 4, 0.1, dx=350), t(12.5, 700, 280, 54, "a whisper of wind", c="blue", d=0.3))
bd(13, earth(13, 960, 600, 230, 0.0), orbiter(13, 960, 600, 360, 0.1, rpm=60), char(cute_battery, 13, 1550, 550, 0.8, 0.2, level=0.8),
   arr(13, 1400, 300, 1550, 380, c="red", d=0.4))
bd(13.5, char(cute_battery, 13.5, 700, 560, 1.3, 0.0, level=0.3, mood="tired"), [ball(13.5, 820, 500 + 40 * q, 500, -80 + 60 * q, 0.2 + 0.12 * q, c="gold", r=14) for q in range(4)],
   t(13.5, 1350, 300, 54, "a tiny bit", c="red", d=0.4))
bd(14, swift(14, 960, 300, 0.7, 0.0, dy=350, dur=2.0, dd=0.2), bar(14, 1500, 950, 120, 500, "red", 0.3, 1.4), ic(14, "earth_arc", 960, 950, 600, 0.1, mv="bob", c="blue"), arr(14, 400, 300, 400, 700, c="red", d=0.4))
bd(14.5, air(14.5, 300, 1600, 300, 450, 4, 0.0), air(14.5, 300, 1600, 550, 750, 9, 0.1), air(14.5, 300, 1600, 800, 980, 16, 0.2, c="blue"), t(14.5, 1700, 350, 40, "thin", c="muted", d=0.3),
   t(14.5, 1700, 900, 40, "thick", c="blue", d=0.4))
bd(15, O(15, 500, 750, 60, c="ink", fill="paper", idp="sb1"), pop(15, "sb1", 0.0), sh(15, "sb1", 800, 0, 0.3, 2.0),
   {"t": "move", "at": 15, "kind": "grow", "targets": ["sb1"], "axis": "both", "pivot": [500, 750], "dur": 2.0, "delay": 0.3, "from": 1, "to": 3},
   big(15, 960, 300, "snowball", c="blue", d=0.2, s=130), ic(15, "earth_arc", 960, 1000, 1200, 0.1, mv="bob", c="muted"))
bd(15.5, P(15.5, "M300,350 C900,370 1300,450 1600,950", c="red", w=10, idp="crv"), pop(15.5, "crv", 0.0), swift(15.5, 300, 350, 0.4, 0.1, dx=1000, dy=300, dur=1.8),
   t(15.5, 600, 600, 50, "slow...", c="muted", d=0.2), big(15.5, 1300, 500, "FAST", c="red", d=0.6, s=120))
bd(16, big(16, 960, 230, "Twist one", c="red", d=0.0, s=140), swift(16, 700, 650, 1.0, 0.1, mood="o"), arr(16, 1000, 650, 1500, 650, c="red", d=0.3), [ball(16, 1000, 800, 500, 0, 0.3 + 0.1 * q, c="gold") for q in range(3)])
bd(16.5, earth(16.5, 960, 600, 200, 0.0), orbiter(16.5, 960, 600, 420, 0.1, rpm=25, c="blue"), orbiter(16.5, 960, 600, 300, 0.2, rpm=55, c="red"), big(16.5, 1650, 300, "faster!", c="red", d=0.4, s=90))
bd(17, earth(17, 700, 600, 200, 0.0), orbiter(17, 700, 600, 330, 0.1, rpm=60), bar(17, 1250, 950, 140, 250, "blue", 0.2), t(17, 1320, 1010, 36, "high"), bar(17, 1500, 950, 140, 500, "red", 0.4),
   t(17, 1570, 1010, 36, "low"), t(17, 1420, 350, 44, "speed", c="red", d=0.3))
bd(17.5, big(17.5, 960, 300, "Drag = faster?!", c="red", d=0.0, s=130), swift(17.5, 600, 700, 0.9, 0.2, mood="o"), ic(17.5, "question", 1300, 700, 220, 0.3, mv="wig", c="red"))
bd(18, big(18, 960, 230, "Twist two", c="red", d=0.0, s=140), ic(18, "sun", 700, 650, 300, 0.1, mv="spin", c="gold"), air(18, 1100, 1700, 500, 900, 10, 0.3))
bd(18.5, ic(18.5, "sun", 500, 500, 280, 0.0, mv="spin", c="gold"), [arr(18.5, 700, 400 + 100 * q, 1100, 400 + 100 * q, c="gold", d=0.2 + 0.1 * q) for q in range(3)],
   air(18.5, 1200, 1700, 350, 800, 9, 0.3, c="red"))
bd(19, ic(19, "sun", 450, 450, 260, 0.0, mv="spin", c="gold"), ic(19, "thermometer", 1000, 550, 240, 0.2, mv="wig", c="red"), ic(19, "earth_arc", 1400, 900, 600, 0.1, mv="bob", c="blue"),
   R(19, 1150, 650, 500, 100, c="red", fill="red", idp="atm"), pop(19, "atm", 0.3),
   {"t": "move", "at": 19, "kind": "grow", "targets": ["atm"], "axis": "y", "pivot": [1400, 750], "dur": 1.4, "delay": 0.5, "from": 1, "to": 2.5})
bd(19.5, R(19.5, 700, 650, 520, 220, c="ink", fill="gold", idp="brd"), pop(19.5, "brd", 0.0),
   {"t": "move", "at": 19.5, "kind": "grow", "targets": ["brd"], "axis": "y", "pivot": [960, 870], "dur": 1.6, "delay": 0.3, "from": 1, "to": 2.0}, wig(19.5, "brd", (960, 870), 2, 1.5),
   t(19.5, 960, 300, 60, "air rising like bread", c="red", d=0.2), ic(19.5, "flame", 1500, 800, 160, 0.3, mv="wig", c="red"))
bd(20, swift(20, 1300, 500, 1.0, 0.0, mood="sad"), air(20, 300, 1000, 300, 900, 16, 0.1, drift=150), arr(20, 1000, 300, 1100, 380, c="red", d=0.4))
bd(20.5, bar(20.5, 600, 950, 240, 250, "blue", 0.0), t(20.5, 720, 1010, 40, "quiet Sun"), bar(20.5, 1100, 950, 240, 600, "red", 0.3, 1.2), t(20.5, 1220, 1010, 40, "busy Sun"),
   t(20.5, 960, 230, 60, "drag", c="red", d=0.2), ic(20.5, "sun", 1600, 400, 180, 0.4, mv="spin", c="gold"))
bd(21, ic(21, "sun", 960, 550, 300, 0.0, mv="spin", c="gold"), orbiter(21, 960, 550, 380, 0.1, rpm=20, c="gold"), big(21, 960, 1000, "11-year cycle", c="blue", d=0.3, s=80),
   [ic(21, "flame", 500 + 920 * q, 450, 140, 0.2 + 0.1 * q, mv="wig", c="red") for q in range(2)])
bd(21.5, R(21.5, 600, 350, 720, 500, c="ink", fill="paper", idp="nas"), pop(21.5, "nas", 0.0), wig(21.5, "nas", (960, 850), 1, 1), t(21.5, 960, 450, 60, "NASA:", c="blue", d=0.1),
   t(21.5, 960, 600, 44, "decay made worse", c="red", d=0.3), P(21.5, "M700,800 L900,780 L1100,820 L1250,900", c="red", w=8, idp="dcl"), pop(21.5, "dcl", 0.4), ic(21.5, "sun", 1550, 350, 140, 0.3, mv="spin", c="gold"))
bd(22, P(22, "M300,300 C800,320 1200,500 1500,800", c="red", w=8, idp="alt"), pop(22, "alt", 0.0), swift(22, 300, 300, 0.4, 0.1, dx=1200, dy=480, dur=2.0, mood="sad"),
   t(22, 400, 220, 40, "600 km", c="blue", d=0.1), ic(22, "clock", 1650, 350, 140, 0.3, mv="spin"))
bd(22.5, big(22.5, 960, 330, "~275 km", c="red", d=0.0, s=180), earth(22.5, 960, 1250, 500, 0.1), swift(22.5, 1400, 650, 0.6, 0.2, mood="sad"), arr(22.5, 1600, 500, 1550, 650, c="red", d=0.4))
bd(23, man(23, 600, 950, 1.5, 0.0, arms="up", amp=6), ic(23, "question", 600, 330, 140, 0.2, mv="wig", c="red"), ic(23, "rocket", 1300, 600, 260, 0.3, mv="bob", c="red"))
bd(23.5, link(23.5, 960, 550, 1.8, 0.0), big(23.5, 960, 230, "Robot rescue!", c="green", d=0.2, s=120), star(23.5, 600, 700, 0.3, r=50), star(23.5, 1320, 700, 0.4, r=50))
bd(24, link(24, 600, 550, 1.3, 0.0), t(24, 600, 850, 54, "LINK", c="green", d=0.2), t(24, 1300, 300, 54, "Katalyst Space", c="blue", d=0.3), ic(24, "robot_arm", 1300, 650, 240, 0.3, mv="wig"))
bd(24.5, link(24.5, 400, 600, 1.0, 0.0, dx=550, dur=1.4), swift(24.5, 1300, 600, 0.9, 0.2, dy=-250, dur=1.2, dd=1.5), arr(24.5, 1550, 750, 1550, 350, c="green", d=0.6))
bd(25, ic(25, "satellite", 600, 300, 160, 0.0, mv="bob", c="ink"), R(25, 400, 300, 400, 80, c="ink", fill="muted", idp="plane"), pop(25, "plane", 0.0), sh(25, "plane", 900, 0, 0.2, 2.0),
   char(cute_rocket, 25, 700, 600, 0.6, 0.3, dx=500, dy=-300, dur=1.4), big(25, 1450, 800, "July", c="blue", d=0.3, s=110))
bd(25.5, R(25.5, 600, 300, 600, 100, c="ink", fill="muted", idp="pl2"), pop(25.5, "pl2", 0.0), wig(25.5, "pl2", (900, 350), 3, 1.5),
   char(cute_rocket, 25.5, 900, 500, 0.5, 0.1, dy=300, dur=0.8, dd=0.2), arr(25.5, 1200, 800, 1600, 300, c="red", d=0.9), t(25.5, 1500, 850, 50, "drop, then fire", c="red", d=0.6))
bd(26, link(26, 700, 550, 1.2, 0.0, mood="sad"), swift(26, 1300, 550, 1.0, 0.1, mood="sad", dy=250, dur=2.0), cross(26, 1000, 300, d=0.4))
bd(26.5, ic(26.5, "question", 600, 550, 260, 0.0, mv="wig", c="red"), R(26.5, 1000, 350, 500, 400, c="ink", fill="paper", idp="sec"), pop(26.5, "sec", 0.1), wig(26.5, "sec", (1250, 750), 2, 1),
   t(26.5, 1250, 550, 54, "not public", c="muted", d=0.3), link(26.5, 1250, 900, 0.5, 0.4, mood="o"))
bd(27, big(27, 960, 230, "Twist three", c="red", d=0.0, s=140), blaze(27, 900, 750, 1.1, 0.1), ic(27, "question", 1500, 600, 200, 0.3, mv="wig", c="red"))
bd(27.5, [P(27.5, f"M{500 + 60 * q},500 l40,80 l-40,80", c="muted", w=8, idp=f"rb{q}") for q in range(1)], wig(27.5, "rb0", (520, 580), 20, 4), pop(27.5, "rb0", 0.0),
   t(27.5, 600, 800, 54, "rubbing?", c="muted", d=0.1), cross(27.5, 600, 400, d=0.3), blaze(27.5, 1250, 700, 1.0, 0.2))
bd(28, swift(28, 1500, 300, 0.6, 0.0, dx=-900, dy=400, dur=1.6, mood="o"), big(28, 960, 900, "27,000 km/h", c="red", d=0.2, s=120), air(28, 300, 800, 550, 800, 10, 0.1))
bd(28.5, swift(28.5, 1300, 550, 0.9, 0.0, mood="o"), air(28.5, 700, 1000, 350, 750, 14, 0.1, drift=-120), arr(28.5, 1050, 550, 800, 550, c="red", d=0.3), t(28.5, 600, 250, 54, "no time to move", c="red", d=0.4))
bd(29, R(29, 600, 400, 160, 500, c="ink", fill="paper", idp="pmp"), pop(29, "pmp", 0.0), P(29, "M680,250 L680,420 M600,250 L760,250", c="ink", w=10, idp="pmh"), pop(29, "pmh", 0.1),
   sh(29, "pmh", 0, 120, 0.3, 0.4), sh(29, "pmh", 0, -120, 0.8, 0.4), sh(29, "pmh", 0, 120, 1.3, 0.4), air(29, 620, 740, 700, 880, 8, 0.2, c="red"), ic(29, "thermometer", 1200, 600, 260, 0.3, mv="wig", c="red"))
bd(29.5, big(29.5, 960, 300, "SQUEEZE = HOT", c="red", d=0.0, s=130), air(29.5, 600, 1300, 550, 850, 18, 0.1, c="red"), ic(29.5, "flame", 1550, 700, 200, 0.4, mv="wig", c="red"))
bd(30, blaze(30, 900, 650, 1.4, 0.0), [ic(30, "flame", 500 + 900 * q, 450, 160, 0.2 + 0.1 * q, mv="wig", c="red") for q in range(2)], t(30, 960, 900, 54, "glowing air", c="red", d=0.3))
bd(30.5, [ball(30.5, 900, 500, 400 - 160 * q, 300 + 60 * (q % 3), 0.1 + 0.05 * q, c=("red", "gold", "muted")[q % 3]) for q in range(6)], swift(30.5, 900, 500, 0.8, 0.0, mood="o"),
   ic(30.5, "flame", 1500, 550, 200, 0.3, mv="wig", c="red"))
bd(31, blaze(31, 900, 550, 0.9, 0.0, dx=-300, dy=300), [ic(31, "flame", 1100 + 180 * q, 650, 120, 0.2 + 0.08 * q, mv="wig", c="red") for q in range(3)], t(31, 1300, 300, 54, "mostly burned up", c="red", d=0.3))
bd(31.5, big(31.5, 960, 330, "1 in 2,100", c="red", d=0.0, s=170), [man(31.5, 450 + 200 * q, 950, 0.6, 0.2 + 0.04 * q, amp=6) for q in range(6)], t(31.5, 960, 560, 44, "NASA's estimate", c="muted", d=0.3))
bd(32, big(32, 960, 230, "Fine print", c="blue", d=0.0, s=130), link(32, 700, 650, 1.0, 0.1, mood="o"), ic(32, "question", 1300, 650, 220, 0.3, mv="wig", c="red"))
bd(32.5, R(32.5, 600, 350, 720, 500, c="ink", fill="paper", idp="fp1"), pop(32.5, "fp1", 0.0), wig(32.5, "fp1", (960, 850), 1, 1), [P(32.5, f"M700,{480 + 90 * q} L1200,{480 + 90 * q}", c="ink", w=12, idp=f"rd{q}") for q in range(4)],
   [pop(32.5, f"rd{q}", 0.2 + 0.1 * q) for q in range(4)], ic(32.5, "magnifier", 1450, 700, 200, 0.4, mv="wig"))
bd(33, ic(33, "sun", 600, 500, 260, 0.0, mv="spin", c="gold"), air(33, 900, 1600, 400, 800, 10, 0.2, c="red"), arr(33, 800, 500, 950, 550, c="gold", d=0.3))
bd(33.5, ic(33.5, "clock", 700, 550, 300, 0.0, mv="spin"), big(33.5, 1300, 450, "± 11 h", c="red", d=0.2, s=150), blaze(33.5, 1350, 800, 0.6, 0.3, dx=-200, dy=100))
bd(34, swift(34, 700, 550, 1.2, 0.0, mood="o"), air(34, 1100, 1600, 400, 800, 7, 0.2), ic(34, "question", 1100, 250, 140, 0.3, mv="wig", c="red"))
bd(34.5, earth(34.5, 960, 600, 200, 0.0), orbiter(34.5, 960, 600, 300, 0.1, rpm=60), orbiter(34.5, 960, 600, 380, 0.2, rpm=45, c="blue"), big(34.5, 1600, 300, "x 22 yr", c="red", d=0.3, s=100),
   wind(34.5, 200, 850, 2, 0.4, dx=200))
bd(35, swift(35, 700, 550, 1.3, 0.0), ic(35, "wind", 1300, 500, 200, 0.2, mv="wig", c="blue"), t(35, 1300, 800, 64, "Swift = speed", c="blue", d=0.3))
bd(35.5, blaze(35.5, 1300, 550, 1.0, 0.0, dx=-500, dy=350, dur=1.8), [star(35.5, 400 + 200 * q, 300, 0.3 + 0.1 * q, r=30) for q in range(3)], big(35.5, 600, 850, "speed burned it", c="red", d=0.4, s=90))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"NASA": "Nasa", "Katalyst": "Catalyst", "LINK": "Link"})
