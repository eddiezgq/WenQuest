"""Daily science short 2026-10-27 (English): "A Robot Tried to Save This Telescope"
News: NASA ends the Swift observatory mission (announced Oct 23, 2026) after the robotic rescue by Katalyst's LINK failed.
Space.com "Latest news" Oct 26 ("NASA ends Swift space telescope mission after failed rescue attempt"); Scientific American; Tech Times Oct 27.
Facts used:
- Scientific American https://www.scientificamerican.com/article/nasa-calls-off-rescue-mission-for-its-falling-swift-space-telescope/ :
  Swift launched 2004 to study gamma-ray bursts; orbit decaying faster than expected; NASA paid about $30 million for LINK, built and run
  by Katalyst Space Technologies in roughly nine months; LINK was to grab Swift with robotic arms and raise its orbit; weeks after its
  early-July launch hardware faults set it spinning, communication sporadic, thrusters failed to stop the spin; Swift will burn up.
- Tech Times 2026-10-27 https://www.techtimes.com/articles/329543/20261027/swift-space-telescope-retires-after-20-years-nasas-rescue-mission-fails.htm :
  final data Oct 20 at ~275 km (safe mode); LINK launched July 3, 2026, three robotic arms, reaction-wheel failures, spin ~3 weeks after
  launch, came within ~12-15 km; boost abandoned Aug 2026; LINK reentered Sep 25; >2,000 gamma-ray bursts; designed for 2 years;
  drag + solar activity; Swift has no thrusters.
- Textbook: Swift's launch orbit ~600 km; orbital speed ~7.6 km/s; drag lowers the orbit and the satellite speeds up (lower orbit is faster);
  solar maximum heats and puffs up the thermosphere; reaction wheels turn a spacecraft by conservation of angular momentum.
Analogy: office chair + spinning wheel. Gag: "a whisper of air". Speculation: none; "the world is still learning" is opinion, said as such.
    python3 make.py <kokoro model dir> | --boards-only | --fake   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("一台机器人飞上太空去救一台望远镜，|结果它自己先转晕了。", "A robot flew into space to rescue a telescope. | Then the robot started spinning out of control."),
 ("现在NASA宣布：|望远镜救不回来了。", "Now NASA says: | the telescope can't be saved."),
 ("它叫Swift，|在太空里干了将近22年。", "It's called Swift. | It worked in space for almost twenty two years."),
 ("原本只设计用两年，|它抓到了两千多次伽马射线暴。", "It was built to last two years, | and it caught more than two thousand gamma ray bursts."),
 ("今天的问题：太空几乎是空的，|卫星为什么还会掉下来？", "Today's question: space is nearly empty, | so why do satellites fall down?"),
 ("先说个秘密：|在轨道上，本来就一直在往下掉。", "First, a secret: | being in orbit means falling all the time."),
 ("只是它横着飞得太快，每秒七公里半，|地面一直弯下去，它永远掉不到。", "It just flies sideways so fast, seven and a half kilometers a second, | that the ground keeps curving away beneath it."),
 ("一直在掉，一直落不了地，|这就叫轨道。", "Always falling, never landing. | That's an orbit."),
 ("可是几百公里高的地方，|还剩一丁点空气。", "But a few hundred kilometers up, | there's still a whisper of air."),
 ("每秒七公里多迎面撞上去，|这一丁点空气就成了刹车。", "Slam into it at seven kilometers a second, | and that whisper becomes a brake."),
 ("反转一，最反直觉：|刹车反而让卫星变快了。", "Twist one, the weird one: | the brake makes the satellite faster."),
 ("被拖慢一点，它就掉低一点，|而低轨道跑得更快。", "Lose a little energy, and it drops a little lower. | And lower orbits are faster."),
 ("越掉越低，空气越来越密，|刹得越来越狠。", "Lower means thicker air, | which means harder braking."),
 ("反转二：|太阳也来插了一脚。", "Twist two: | the Sun joined in."),
 ("太阳活跃的年份，把高空大气晒得膨胀，|空气一直涨到卫星的高度。", "When the Sun is active, it heats the upper air, | and the air puffs up to where satellites fly."),
 ("Swift一开始在大约600公里高，|10月20号只剩大约275公里。", "Swift started about six hundred kilometers up. | By October twentieth, it was down to about two hundred seventy five."),
 ("它自己没有推进器，|只能眼看着往下沉。", "And Swift has no thrusters. | It could only watch itself sink."),
 ("于是NASA花了大约3000万美元，|请人造一个救援机器人。", "So NASA paid about thirty million dollars | for a rescue robot."),
 ("公司叫Katalyst，飞船叫LINK，|大约九个月就造好了。", "The company is Katalyst. The ship is LINK. | It was built in about nine months."),
 ("计划：用三只机械臂抓住Swift，|再把它推回高处。", "The plan: grab Swift with three robot arms, | and push it back up."),
 ("7月3号发射，|可三周后，它就开始乱转。", "It launched on July third. | Three weeks later, it began to tumble."),
 ("反转三：|坑它的，是它自己的轮子。", "Twist three: | its own wheels let it down."),
 ("太空里转身没有墙可以扶，|靠的是飞船里的反作用轮。", "In space, there's no wall to push on. | Spacecraft turn using reaction wheels."),
 ("坐在转椅上，把手里的轮子往一边转，|你自己就往另一边转。", "Sit on an office chair, spin a wheel one way, | and you turn the other way."),
 ("轮子一坏，|你就是那把停不下来的转椅。", "When the wheels fail, | you're the chair that won't stop spinning."),
 ("它用推进器想刹住，没刹住，|通信也断断续续。", "It fired its thrusters to stop the spin. No luck, | and the radio link kept dropping out."),
 ("它离Swift最近只有十几公里，|8月份，救援放弃。", "It got within about twelve to fifteen kilometers. | In August, the rescue was called off."),
 ("9月25号，LINK自己先掉回大气层，|烧掉了。", "On September twenty fifth, LINK itself fell back into the air | and burned up."),
 ("Swift预计几周之内跟着落下，|在大气里烧毁。", "Swift is expected to follow within weeks, | burning up in the atmosphere."),
 ("友情提示：去抓一个没设计让人抓的航天器，|在我们看来，全世界都还在学。", "Friendly fine print: grabbing a spacecraft never built to be grabbed | is, we think, something the whole world is still learning."),
 ("Katalyst说，|这次的数据会留给下一次救援。", "Katalyst says | the data will help the next rescue."),
 ("所以卫星往下掉，不是因为太空不空，|而是那一丁点空气，再加上太阳。", "So satellites fall not because space is crowded, | but because of a whisper of air, plus the Sun."),
 ("再见，Swift。|设计用两年，干了二十二年。", "Goodbye, Swift. | Built for two years. Worked for twenty two."),
]
TITLE = {"zh": "机器人为什么没救回这台望远镜？", "en": "A Robot Tried to Save This Telescope"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 820, 0.5, r=16)
    B.append(E)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def swift(a, x, y, k=1.0, d=0.0, mood="happy", tumble=0):
    """Swift: a gold box with two blue solar panels (panels wiggle), a telescope tube, and a face; it bobs."""
    i, pn = uid("sw"), uid("swp")
    m = {"happy": f"M{x - 25 * k},{y + 20 * k} Q{x},{y + 42 * k} {x + 25 * k},{y + 20 * k}",
         "o": f"M{x - 10 * k},{y + 30 * k} a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0",
         "sad": f"M{x - 25 * k},{y + 38 * k} Q{x},{y + 18 * k} {x + 25 * k},{y + 38 * k}"}[mood]
    E = [R(a, x - 70 * k, y - 70 * k, 140 * k, 140 * k, c="ink", fill="gold", idp=i),
         R(a, x - 40 * k, y - 130 * k, 80 * k, 60 * k, c="ink", fill="paper", idp=i, sw=4),
         O(a, x - 25 * k, y - 15 * k, 9 * k, c="ink", fill="ink", idp=i), O(a, x + 25 * k, y - 15 * k, 9 * k, c="ink", fill="ink", idp=i),
         P(a, m, c="ink", w=4, idp=i),
         R(a, x - 230 * k, y - 40 * k, 150 * k, 80 * k, c="ink", fill="blue", idp=pn, sw=4), R(a, x + 80 * k, y - 40 * k, 150 * k, 80 * k, c="ink", fill="blue", idp=pn, sw=4),
         pop(a, [i, pn], d), bob(a, i, 8 * k, 1.0), bob(a, pn, 8 * k, 1.0), wig(a, pn, (x, y), 3, 1.5)]
    if tumble:
        E += [spin(a, i, (x, y), tumble), spin(a, pn, (x, y), tumble)]
    return E, [i, pn]


def link(a, x, y, k=1.0, d=0.0, mood="happy", rpm=0):
    """LINK: a round-ish blue robot with three arms that wave."""
    i, ar = uid("lk"), uid("lka")
    m = {"happy": f"M{x - 22 * k},{y + 18 * k} Q{x},{y + 38 * k} {x + 22 * k},{y + 18 * k}",
         "o": f"M{x - 10 * k},{y + 28 * k} a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0",
         "dizzy": f"M{x - 22 * k},{y + 28 * k} Q{x - 11 * k},{y + 14 * k} {x},{y + 28 * k} Q{x + 11 * k},{y + 42 * k} {x + 22 * k},{y + 28 * k}"}[mood]
    E = [O(a, x, y, 80 * k, c="ink", fill="blue", idp=i),
         O(a, x - 25 * k, y - 15 * k, 9 * k, c="ink", fill="ink", idp=i), O(a, x + 25 * k, y - 15 * k, 9 * k, c="ink", fill="ink", idp=i), P(a, m, c="ink", w=4, idp=i),
         P(a, f"M{x + 75 * k},{y - 20 * k} L{x + 150 * k},{y - 80 * k} L{x + 190 * k},{y - 50 * k} "
              f"M{x + 75 * k},{y + 25 * k} L{x + 160 * k},{y + 60 * k} L{x + 200 * k},{y + 30 * k} "
              f"M{x - 75 * k},{y + 10 * k} L{x - 160 * k},{y - 30 * k} L{x - 200 * k},{y + 5 * k}", c="ink", w=6, idp=ar),
         pop(a, [i, ar], d), wig(a, ar, (x, y), 10, 2.0), bob(a, i, 6 * k, 1.3), bob(a, ar, 6 * k, 1.3)]
    if rpm:
        E += [spin(a, i, (x, y), rpm), spin(a, ar, (x, y), rpm)]
    return E, [i, ar]


def earth(a, y=1000, d=0.0, c="blue"):
    """A big curve of Earth along the bottom that slowly turns."""
    i = uid("ea")
    return [P(a, f"M60,{y} Q960,{y - 330} 1860,{y}", c=c, w=8, idp=i), pop(a, i, d), wig(a, i, (960, y + 400), 0.6, 0.3)]


def air(a, y0, n=6, d=0.0, c="muted", drift=-80):
    """Little air dots drifting past."""
    E = []
    for q in range(n):
        i = uid("air")
        x = 300 + 260 * q
        E += [O(a, x, y0 + 40 * (q % 3), 9, c=c, fill=c, idp=i), pop(a, i, d + 0.06 * q), sh(a, i, drift, 0, d + 0.3, 1.5)]
    return E


def chair(a, x, y, d=0.0, rpm=0, turn=0):
    """A stick person on an office chair holding a wheel."""
    i, wh = uid("ch"), uid("chw")
    E = [P(a, f"M{x},{y + 150} L{x},{y + 250} M{x - 80},{y + 260} L{x + 80},{y + 260} M{x - 90},{y + 150} L{x + 90},{y + 150} "
              f"M{x},{y - 60} L{x},{y + 120} M{x},{y + 120} L{x + 70},{y + 150} M{x},{y - 10} L{x + 90},{y + 20}", c="ink", w=7, idp=i),
         O(a, x, y - 110, 50, c="ink", fill="paper", idp=i), pop(a, i, d),
         O(a, x + 130, y + 20, 55, c="red", idp=wh, sw=7), P(a, f"M{x + 75},{y + 20} L{x + 185},{y + 20}", c="red", w=5, idp=wh), pop(a, wh, d + 0.1),
         spin(a, wh, (x + 130, y + 20), 120)]
    if rpm:
        E.append(spin(a, i, (x, y + 150), rpm))
    if turn:
        E.append(rot(a, i, turn, (x, y + 150), d + 0.4, 0.8))
    return E


def flash_(a, x, y, d=0.0, c="gold", r=140):
    i = uid("fl")
    return [P(a, " ".join(f"M{x},{y} L{x + r * dx},{y + r * dy}" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, -.7), (.7, -.7), (-.7, .7))), c=c, w=8, idp=i),
            pop(a, i, d), spin(a, i, (x, y), 30), pulse(a, i, d + 0.4)]


# 0 robot rescues / spins
s, sid = swift(0, 1350, 450, 1.0)
l, lid = link(0, 450, 450, 1.0)
bd(0, s, l, [sh(0, lid, 350, 0, 0.3, 1.0)], arr(0, 700, 600, 1050, 600, c="green", d=0.3))
l, lid = link(0.5, 960, 470, 1.3, mood="dizzy", rpm=60)
bd(0.5, l, ic(0.5, "question", 500, 300, 140, 0.3, mv="wig", c="red"), ic(0.5, "question", 1450, 300, 140, 0.5, mv="wig", c="red"), BIG(0.5, 960, 800, "spinning!", c="red", d=0.6, s=90))
# 1 NASA says
bd(1, ic(1, "building", 500, 450, 240, 0.0, mv="bob"), ic(1, "speaker", 900, 420, 160, 0.2, mv="wig"), ic(1, "satellite", 1450, 420, 200, 0.4, mv="spin", c="gold"))
s, sid = swift(1.5, 960, 420, 1.1, mood="sad")
bd(1.5, s, [sh(1.5, sid, 0, 200, 0.4, 1.2)], cross(1.5, 1500, 400, d=0.6), BIG(1.5, 960, 820, "can't be saved", c="red", d=0.3, s=80))
# 2 Swift, 22 years
s, sid = swift(2, 800, 450, 1.2)
bd(2, s, BIG(2, 1450, 450, "SWIFT", c="blue", d=0.3, s=130), earth(2, 1080, 0.1))
bd(2.5, BIG(2.5, 800, 450, "22", c="red", d=0.1, s=240), T(2.5, 800, 640, 60, "years", c="ink", d=0.3), ic(2.5, "clock", 1400, 450, 220, 0.2, mv="spin"), arr(2.5, 300, 780, 1600, 780, c="blue", d=0.4, dur=1.0))
# 3 2 years -> 2000 GRBs
bd(3, bar(3, 600, 750, 160, 70, "blue", d=0.1), bar(3, 900, 750, 160, 480, "red", d=0.4), T(3, 680, 820, 52, "planned: 2", c="blue", d=0.2), T(3, 980, 820, 52, "actual: 22", c="red", d=0.5), ic(3, "satellite", 1450, 400, 200, 0.3, mv="spin", c="gold"))
bd(3.5, BIG(3.5, 960, 420, "2,000+", c="red", d=0.1, s=200), T(3.5, 960, 620, 60, "gamma-ray bursts", c="ink", d=0.3),
   [e for q in range(4) for e in ic(3.5, "sun", 350 + 400 * q, 230 + 40 * (q % 2), 90, 0.3 + 0.1 * q, mv="spin", c="gold")])
# 4 question
bd(4, BIG(4, 960, 250, "space is", c="ink", d=0.0, s=90), BIG(4, 960, 420, "nearly EMPTY", c="blue", d=0.3, s=120), ic(4, "moon", 450, 650, 160, 0.3, mv="bob"), ic(4, "globe", 1450, 650, 180, 0.5, mv="spin"))
s, sid = swift(4.5, 960, 380, 1.0, mood="o")
bd(4.5, s, [sh(4.5, sid, 0, 250, 0.3, 1.2)], earth(4.5, 1080, 0.0), ic(4.5, "question", 1550, 400, 180, 0.4, mv="wig", c="red"), BIG(4.5, 400, 400, "why?", c="red", d=0.5, s=110))
# 5 secret: falling
bd(5, ic(5, "magnifier", 600, 450, 220, 0.0, mv="wig"), BIG(5, 1250, 450, "a secret", c="red", d=0.3, s=120), ic(5, "eye", 1650, 300, 120, 0.4, mv="wig"))
s, sid = swift(5.5, 960, 300, 0.9)
bd(5.5, s, earth(5.5, 1080), arr(5.5, 960, 420, 960, 700, c="red", d=0.3), T(5.5, 1300, 560, 64, "falling... always", c="red", d=0.5))
# 6 sideways fast
s, sid = swift(6, 400, 350, 0.8)
bd(6, s, [sh(6, sid, 900, 0, 0.3, 1.2)], earth(6, 1080), arr(6, 500, 550, 1500, 550, c="blue", d=0.2, dur=0.8), BIG(6, 960, 720, "7.5 km/s", c="red", d=0.4, s=110))
e6 = uid("cv")
bd(6.5, [P(6.5, "M300,300 Q900,220 1500,500 Q1700,700 1650,900", c="blue", w=6, idp=e6), pop(6.5, e6, 0.1), wig(6.5, e6, (960, 600), 1, 0.5)],
   swift(6.5, 300, 300, 0.6)[0], earth(6.5, 1080), [sh(6.5, [], 0, 0, 0, 0.1)][:0], ic(6.5, "globe", 1100, 820, 160, 0.3, mv="spin"))
# 7 always falling never landing
orb = uid("orb")
s, sid = swift(7, 960, 220, 0.6)
bd(7, [O(7, 960, 540, 300, c="blue", idp=orb, sw=4), pop(7, orb, 0.0)], ic(7, "globe", 960, 540, 260, 0.0, mv="spin"), s, [spin(7, sid[0], (960, 540), 30), spin(7, sid[1], (960, 540), 30)], T(7, 1550, 300, 60, "never lands", c="red", d=0.5))
bd(7.5, BIG(7.5, 960, 420, "ORBIT", c="blue", d=0.1, s=200), check(7.5, 1450, 420, d=0.5), ic(7.5, "satellite", 450, 450, 180, 0.2, mv="spin", c="gold"), arr(7.5, 300, 700, 1600, 700, c="blue", d=0.3, dur=1.0))
# 8 whisper of air
bd(8, earth(8, 1080), BIG(8, 960, 300, "a few hundred km", c="ink", d=0.1, s=90), arr(8, 300, 900, 300, 400, c="blue", d=0.3), ic(8, "ruler", 1550, 550, 200, 0.4, mv="wig"))
s, sid = swift(8.5, 960, 450, 0.9)
bd(8.5, s, air(8.5, 250, 6, 0.2), air(8.5, 700, 6, 0.4), T(8.5, 960, 860, 56, "a whisper of air", c="muted", d=0.5))
# 9 brake
s, sid = swift(9, 1400, 450, 0.8)
bd(9, s, air(9, 350, 5, 0.1, drift=200), air(9, 600, 5, 0.2, drift=200), arr(9, 500, 450, 1150, 450, c="red", d=0.3), BIG(9, 700, 750, "7+ km/s", c="red", d=0.4, s=100))
s, sid = swift(9.5, 960, 450, 1.0, mood="o")
bd(9.5, s, ic(9.5, "wind", 450, 450, 200, 0.1, mv="wig", c="muted"), BIG(9.5, 1500, 450, "BRAKE", c="red", d=0.3, s=120), ic(9.5, "flame", 1500, 700, 120, 0.5, mv="wig", c="red"))
# 10 twist one
bd(10, BIG(10, 960, 220, "Twist one", c="red", d=0.0, s=120), ic(10, "question", 600, 550, 200, 0.2, mv="wig", c="red"), ic(10, "question", 1300, 550, 200, 0.4, mv="wig", c="red"))
s, sid = swift(10.5, 600, 450, 0.9)
bd(10.5, s, [sh(10.5, sid, 600, 100, 0.3, 0.8)], BIG(10.5, 1300, 250, "brake = FASTER?!", c="red", d=0.2, s=90), arr(10.5, 700, 750, 1500, 750, c="blue", d=0.5))
# 11 lower, faster
o1, o2 = uid("o1"), uid("o2")
bd(11, [O(11, 960, 600, 380, c="blue", idp=o1, sw=4), pop(11, o1, 0.0), O(11, 960, 600, 300, c="red", idp=o2, sw=4), pop(11, o2, 0.4)],
   ic(11, "globe", 960, 600, 240, 0.0, mv="spin"), swift(11, 960, 220, 0.5)[0], [sh(11, [], 0, 0, 0, 0.1)][:0], arr(11, 1450, 250, 1350, 350, c="red", d=0.5))
bd(11.5, bar(11.5, 600, 750, 160, 250, "blue", d=0.1), bar(11.5, 900, 750, 160, 420, "red", d=0.4), T(11.5, 680, 820, 52, "higher", c="blue", d=0.2), T(11.5, 980, 820, 52, "lower", c="red", d=0.5),
   T(11.5, 1450, 400, 64, "speed", c="ink", d=0.3), ic(11.5, "wheel", 1450, 600, 150, 0.4, mv="spin"))
# 12 thicker air
s, sid = swift(12, 960, 300, 0.7)
bd(12, s, [sh(12, sid, 0, 300, 0.3, 1.2)], air(12, 500, 6, 0.0), air(12, 650, 6, 0.2), air(12, 780, 6, 0.4))
bd(12.5, bar(12.5, 500, 750, 140, 120, "muted", d=0.0), bar(12.5, 750, 750, 140, 260, "muted", d=0.3), bar(12.5, 1000, 750, 140, 450, "red", d=0.6), T(12.5, 1400, 400, 64, "harder braking", c="red", d=0.5), ic(12.5, "flame", 1550, 600, 140, 0.6, mv="wig", c="red"))
# 13 twist two: the Sun
bd(13, BIG(13, 960, 220, "Twist two", c="red", d=0.0, s=120), ic(13, "sun", 960, 580, 300, 0.2, mv="spin", c="gold"))
bd(13.5, ic(13.5, "sun", 500, 450, 280, 0.0, mv="spin", c="gold"), swift(13.5, 1350, 450, 0.9, mood="o")[0], arr(13.5, 700, 450, 1100, 450, c="gold", d=0.3), T(13.5, 960, 800, 60, "the Sun joins in", c="ink", d=0.5))
# 14 air puffs up
lay = uid("lay")
bd(14, ic(14, "sun", 300, 250, 200, 0.0, mv="spin", c="gold"), earth(14, 1080),
   [P(14, "M200,800 Q960,560 1720,800", c="red", w=6, idp=lay), pop(14, lay, 0.2), sh(14, lay, 0, -150, 0.5, 1.0)], ic(14, "thermometer", 1600, 400, 180, 0.4, mv="wig", c="red"))
lay = uid("lay")
s, sid = swift(14.5, 960, 280, 0.6, mood="o")
bd(14.5, s, earth(14.5, 1080), [P(14.5, "M200,850 Q960,600 1720,850", c="red", w=6, idp=lay), pop(14.5, lay, 0.0), sh(14.5, lay, 0, -320, 0.2, 1.0)], air(14.5, 450, 6, 0.6))
# 15 600 -> 275
s, sid = swift(15, 1400, 250, 0.6)
bd(15, s, earth(15, 1080), BIG(15, 600, 350, "600 km", c="blue", d=0.2, s=130), ic(15, "rocket", 600, 650, 160, 0.3, mv="bob"))
s, sid = swift(15.5, 1400, 250, 0.6, mood="sad")
bd(15.5, s, [sh(15.5, sid, 0, 400, 0.2, 1.2)], earth(15.5, 1080), BIG(15.5, 600, 350, "275 km", c="red", d=0.3, s=130), T(15.5, 600, 520, 56, "Oct 20", c="ink", d=0.4))
# 16 no thrusters
s, sid = swift(16, 700, 450, 1.1)
bd(16, s, ic(16, "flame", 1300, 450, 200, 0.2, mv="wig", c="red"), cross(16, 1300, 450, d=0.5), T(16, 1300, 650, 60, "no thrusters", c="red", d=0.4))
s, sid = swift(16.5, 960, 300, 1.0, mood="sad")
bd(16.5, s, [sh(16.5, sid, 0, 350, 0.2, 1.4)], earth(16.5, 1080), ic(16.5, "eye", 1500, 300, 140, 0.3, mv="wig"))
# 17 30 million
bd(17, BIG(17, 960, 420, "$30 million", c="green", d=0.1, s=150), ic(17, "building", 400, 450, 200, 0.2, mv="bob"), arr(17, 1400, 450, 1650, 450, c="green", d=0.4))
l, lid = link(17.5, 960, 450, 1.3)
bd(17.5, l, ic(17.5, "gear", 400, 450, 180, 0.2, mv="spin"), ic(17.5, "check", 1550, 450, 160, 0.5, mv="bob", c="green"))
# 18 Katalyst / LINK / nine months
l, lid = link(18, 600, 450, 1.2)
bd(18, l, BIG(18, 1350, 350, "LINK", c="blue", d=0.2, s=150), T(18, 1350, 550, 60, "by Katalyst", c="ink", d=0.4))
bd(18.5, BIG(18.5, 960, 420, "~9 months", c="red", d=0.1, s=150), ic(18.5, "clock", 400, 450, 200, 0.2, mv="spin"), ic(18.5, "gear", 1550, 450, 180, 0.3, mv="spin"), ic(18.5, "robot_arm", 960, 700, 160, 0.4, mv="wig"))
# 19 plan: three arms, push up
l, lid = link(19, 600, 450, 1.1)
s, sid = swift(19, 1400, 450, 0.8)
bd(19, l, s, [sh(19, lid, 350, 0, 0.3, 0.8)], BIG(19, 960, 800, "3 robot arms", c="blue", d=0.4, s=90))
l, lid = link(19.5, 760, 650, 0.9)
s, sid = swift(19.5, 1150, 650, 0.7)
bd(19.5, l, s, [sh(19.5, lid + sid, 0, -300, 0.4, 1.0)], arr(19.5, 1600, 700, 1600, 300, c="green", d=0.3), earth(19.5, 1100))
# 20 launch / tumble
bd(20, ic(20, "rocket", 700, 600, 260, 0.0, mv="bob"), [sh(20, [], 0, 0, 0, 0.1)][:0], BIG(20, 1300, 400, "July 3", c="blue", d=0.3, s=130), arr(20, 700, 400, 700, 150, c="red", d=0.4))
l, lid = link(20.5, 960, 450, 1.3, mood="dizzy", rpm=90)
bd(20.5, l, BIG(20.5, 400, 300, "+3 weeks", c="red", d=0.2, s=90), ic(20.5, "question", 1550, 350, 140, 0.4, mv="wig", c="red"))
# 21 twist three: wheels
bd(21, BIG(21, 960, 220, "Twist three", c="red", d=0.0, s=120), ic(21, "wheel", 700, 580, 220, 0.2, mv="spin"), ic(21, "wheel", 1250, 580, 220, 0.4, mv="spin"))
l, lid = link(21.5, 600, 450, 1.1, mood="o")
bd(21.5, l, ic(21.5, "wheel", 1300, 450, 220, 0.2, mv="spin", c="red"), cross(21.5, 1300, 450, d=0.6))
# 22 no wall, reaction wheels
wl = uid("wl")
bd(22, [P(22, "M300,200 L300,800", c="ink", w=10, idp=wl), pop(22, wl, 0.0), wig(22, wl, (300, 800), 2, 1.0)], cross(22, 300, 500, d=0.4), link(22, 1000, 450, 1.0, mood="o")[0], T(22, 1500, 700, 56, "nothing to push", c="red", d=0.5))
bd(22.5, ic(22.5, "wheel", 700, 450, 260, 0.0, mv="spin", c="red"), BIG(22.5, 1300, 380, "reaction", c="blue", d=0.3, s=100), BIG(22.5, 1300, 530, "wheels", c="blue", d=0.5, s=100))
# 23 office chair
bd(23, chair(23, 900, 380, 0.0), T(23, 1400, 300, 64, "office chair", c="ink", d=0.3), arr(23, 1050, 650, 1250, 650, c="red", d=0.5))
bd(23.5, chair(23.5, 900, 380, 0.0, turn=-30), arr(23.5, 1300, 400, 1150, 300, c="red", d=0.2), arr(23.5, 600, 300, 450, 400, c="blue", d=0.5), T(23.5, 450, 250, 56, "you turn", c="blue", d=0.6))
# 24 chair won't stop
bd(24, ic(24, "wheel", 960, 450, 240, 0.0, mv="spin", c="red"), cross(24, 960, 450, d=0.4), T(24, 960, 720, 60, "wheels fail", c="red", d=0.4), ic(24, "gear", 400, 450, 160, 0.2, mv="spin"))
bd(24.5, chair(24.5, 960, 380, 0.0, rpm=60), ic(24.5, "question", 1500, 300, 140, 0.4, mv="wig", c="red"), T(24.5, 1500, 700, 56, "won't stop!", c="red", d=0.5))
# 25 thrusters, radio
l, lid = link(25, 900, 450, 1.1, mood="dizzy", rpm=60)
bd(25, l, ic(25, "flame", 1350, 450, 160, 0.2, mv="wig", c="red"), ic(25, "flame", 450, 450, 160, 0.4, mv="wig", c="red"), cross(25, 1600, 300, d=0.7))
bd(25.5, ic(25.5, "signal", 600, 450, 220, 0.0, mv="wig"), ic(25.5, "satellite", 1300, 450, 200, 0.2, mv="spin", c="blue"), arr(25.5, 750, 450, 1150, 450, c="muted", d=0.3), cross(25.5, 950, 450, d=0.6))
# 26 within 12-15 km / August
l, lid = link(26, 500, 450, 0.8, mood="dizzy", rpm=60)
s, sid = swift(26, 1450, 450, 0.7)
bd(26, l, s, arr(26, 700, 650, 1250, 650, c="red", d=0.3), BIG(26, 960, 800, "12-15 km", c="red", d=0.4, s=90))
bd(26.5, BIG(26.5, 960, 380, "August", c="ink", d=0.1, s=130), T(26.5, 960, 560, 64, "rescue called off", c="red", d=0.3), cross(26.5, 1500, 400, d=0.5), ic(26.5, "robot_arm", 400, 500, 180, 0.2, mv="wig"))
# 27 LINK burns up Sep 25
l, lid = link(27, 960, 250, 0.8, mood="o")
bd(27, l, [sh(27, lid, 0, 450, 0.3, 1.2)], earth(27, 1080), BIG(27, 400, 300, "Sep 25", c="blue", d=0.2, s=100))
bd(27.5, ic(27.5, "flame", 960, 450, 280, 0.0, mv="wig", c="red"), ic(27.5, "flame", 650, 550, 160, 0.2, mv="wig", c="gold"), ic(27.5, "flame", 1270, 550, 160, 0.3, mv="wig", c="gold"))
# 28 Swift follows
s, sid = swift(28, 960, 250, 0.8, mood="sad")
bd(28, s, [sh(28, sid, 0, 400, 0.3, 1.4)], earth(28, 1080), T(28, 1500, 300, 60, "within weeks", c="red", d=0.4))
bd(28.5, ic(28.5, "flame", 960, 450, 300, 0.0, mv="wig", c="red"), ic(28.5, "satellite", 960, 250, 140, 0.2, mv="spin", c="gold"), arr(28.5, 1400, 250, 1400, 650, c="red", d=0.4))
# 29 fine print
bd(29, BIG(29, 960, 200, "Fine print", c="ink", d=0.0, s=100), ic(29, "robot_arm", 600, 550, 220, 0.2, mv="wig"), swift(29, 1300, 550, 0.7, mood="o")[0])
bd(29.5, ic(29.5, "globe", 700, 450, 260, 0.0, mv="spin"), T(29.5, 1300, 380, 60, "still learning", c="blue", d=0.3), T(29.5, 1300, 500, 50, "(our opinion)", c="muted", d=0.5), ic(29.5, "flask", 1600, 650, 140, 0.4, mv="wig"))
# 30 data for next rescue
bd(30, ic(30, "building", 600, 450, 240, 0.0, mv="bob"), ic(30, "speaker", 1000, 420, 160, 0.2, mv="wig"), T(30, 1450, 420, 64, "Katalyst", c="blue", d=0.3))
l, lid = link(30.5, 700, 450, 1.1)
bd(30.5, l, ic(30.5, "computer", 1350, 450, 200, 0.2, mv="bob"), arr(30.5, 950, 450, 1200, 450, c="green", d=0.3), T(30.5, 1350, 680, 56, "next rescue", c="green", d=0.5))
# 31 not crowded, whisper + Sun
bd(31, ic(31, "moon", 600, 450, 200, 0.0, mv="bob"), BIG(31, 1250, 450, "not crowded", c="blue", d=0.3, s=110), check(31, 1250, 650, d=0.5))
s, sid = swift(31.5, 1000, 450, 0.8)
bd(31.5, s, air(31.5, 250, 6, 0.0), ic(31.5, "sun", 300, 300, 200, 0.2, mv="spin", c="gold"), T(31.5, 1300, 800, 56, "air + Sun", c="red", d=0.5))
# 32 goodbye Swift
s, sid = swift(32, 960, 420, 1.3)
bd(32, s, [rot(32, sid[1:], 15, (960, 420), 0.3, 0.4), rot(32, sid[1:], -15, (960, 420), 0.8, 0.4)], T(32, 960, 780, 70, "Goodbye, Swift", c="blue", d=0.3))
bd(32.5, bar(32.5, 600, 750, 160, 70, "blue", d=0.1), bar(32.5, 900, 750, 160, 480, "gold", d=0.4), T(32.5, 680, 820, 52, "2 yrs", c="blue", d=0.2), T(32.5, 980, 820, 52, "22 yrs", c="gold", d=0.5),
   ic(32.5, "satellite", 1450, 400, 220, 0.3, mv="spin", c="gold"), star(32.5, 1450, 650, 0.6, r=40))

INS = [
 (1, "这是一次真实的太空救援，|也是一次真实的失败。", "This was a real space rescue, | and a real failure."),
 (3, "伽马射线暴是宇宙里最猛的爆炸，|Swift发现后，大约一分钟就能扭头去看。", "Gamma ray bursts are the biggest blasts in the universe, | and Swift could swing around to look in about a minute."),
 (7, "就像把一个球扔得飞快，|它就绕着地球一直掉下去。", "Like throwing a ball so hard | that it falls all the way around the Earth."),
 (12, "这像一个越滚越大的雪球，|最后几个月掉得最快。", "It's a snowball effect: | the final months go fastest."),
 (16, "只能靠外援：|有人来推它一把。", "It needed outside help: | someone to give it a push."),
 (19, "这就像在每秒七公里多的车流里，|伸手去抓另一辆车。", "That's like reaching out to grab another car | in traffic moving seven kilometers a second."),
 (23, "这就是角动量守恒：|总的转动，不会凭空消失。", "That's conservation of angular momentum: | the total spin never just disappears."),
 (28, "它留下的数据，|撑起了大约七千篇论文。", "Its data | fed about seven thousand scientific papers."),
]
l, lid = link(100, 700, 450, 1.1)
bd(100, l, ic(100, "rocket", 1350, 450, 200, 0.2, mv="bob"), check(100, 1600, 300, d=0.4))
l, lid = link(100.5, 960, 450, 1.2, mood="dizzy", rpm=45)
bd(100.5, l, cross(100.5, 1500, 400, d=0.4), T(100.5, 1500, 600, 60, "real failure", c="red", d=0.5))
bd(101, flash_(101, 700, 450), BIG(101, 1350, 400, "BOOM", c="red", d=0.2, s=140), ic(101, "sun", 1350, 650, 140, 0.4, mv="spin", c="gold"))
s, sid = swift(101.5, 700, 450, 1.0)
bd(101.5, s, [rot(101.5, sid, 40, (700, 450), 0.3, 0.8)], BIG(101.5, 1400, 450, "~1 min", c="blue", d=0.4, s=110), ic(101.5, "clock", 1400, 700, 120, 0.5, mv="spin"))
bl = uid("bl")
bd(102, [O(102, 400, 500, 40, c="ink", fill="red", idp=bl), pop(102, bl, 0.0), sh(102, bl, 1100, 200, 0.3, 1.0)], ic(102, "globe", 960, 850, 260, 0.1, mv="spin"), chair(102, 300, 450, 0.0)[:0], arr(102, 450, 400, 900, 400, c="red", d=0.2))
orb = uid("orb")
bl = uid("bl")
bd(102.5, [O(102.5, 960, 540, 300, c="blue", idp=orb, sw=4), pop(102.5, orb, 0.0), O(102.5, 960, 240, 30, c="ink", fill="red", idp=bl), pop(102.5, bl, 0.1), spin(102.5, bl, (960, 540), 40)],
    ic(102.5, "globe", 960, 540, 260, 0.0, mv="spin"), T(102.5, 1550, 300, 56, "Newton's ball", c="ink", d=0.4))
sb = uid("sb")
bd(103, [O(103, 500, 450, 60, c="ink", fill="paper", idp=sb), pop(103, sb, 0.0), sh(103, sb, 900, 0, 0.3, 1.2), spin(103, sb, (500, 450), 60)], arr(103, 400, 650, 1500, 650, c="blue", d=0.2, dur=1.0), BIG(103, 960, 250, "snowball", c="blue", d=0.4, s=110))
crv = uid("crv")
bd(103.5, [P(103.5, "M300,250 Q1000,280 1300,500 Q1450,650 1500,850", c="red", w=8, idp=crv), pop(103.5, crv, 0.1), wig(103.5, crv, (900, 550), 1, 0.6)], T(103.5, 600, 800, 56, "altitude", c="ink", d=0.3), T(103.5, 1550, 300, 56, "final months", c="red", d=0.5), ic(103.5, "clock", 1650, 550, 120, 0.4, mv="spin"))
s, sid = swift(104, 960, 450, 1.1, mood="o")
bd(104, s, ic(104, "question", 400, 400, 160, 0.3, mv="wig", c="red"), ic(104, "question", 1550, 400, 160, 0.5, mv="wig", c="red"))
s, sid = swift(104.5, 1200, 450, 0.9)
l, lid = link(104.5, 450, 450, 0.9)
bd(104.5, s, l, [sh(104.5, lid, 300, 0, 0.3, 0.6), sh(104.5, sid, 0, -100, 0.9, 0.5)])
bd(105, ic(105, "car", 500, 450, 220, 0.0, mv="wig", c="blue"), ic(105, "car", 1300, 450, 220, 0.2, mv="wig", c="red"), arr(105, 300, 650, 1600, 650, c="ink", d=0.3, dur=1.0))
l, lid = link(105.5, 700, 450, 1.0)
s, sid = swift(105.5, 1300, 450, 0.8)
bd(105.5, l, s, BIG(105.5, 960, 800, "7+ km/s, both", c="red", d=0.4, s=90))
bd(106, chair(106, 700, 380, 0.0, turn=-25), BIG(106, 1350, 380, "angular", c="blue", d=0.3, s=100), BIG(106, 1350, 520, "momentum", c="blue", d=0.5, s=100))
bd(106.5, ic(106.5, "wheel", 600, 450, 220, 0.0, mv="spin", c="red"), BIG(106.5, 960, 450, "+", c="ink", d=0.2, s=120), ic(106.5, "satellite", 1300, 450, 220, 0.3, mv="spin", c="blue"), T(106.5, 960, 750, 60, "total spin stays", c="ink", d=0.5))
bd(107, ic(107, "satellite", 600, 450, 220, 0.0, mv="spin", c="gold"), arr(107, 800, 450, 1100, 450, c="green", d=0.3), ic(107, "computer", 1350, 450, 200, 0.4, mv="bob"))
pg = []
for q in range(6):
    i = uid("pg")
    pg += [R(107.5, 350 + 200 * q, 330 + 20 * (q % 2), 160, 220, c="ink", fill="paper", idp=i), pop(107.5, i, 0.08 * q), sh(107.5, i, 0, 40, 0.6 + 0.05 * q, 0.4)]
bd(107.5, pg, BIG(107.5, 960, 750, "~7,000 papers", c="red", d=0.4, s=100))

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
    main(here, S, B, TITLE, "en", say={"Katalyst": "Catalyst", "NASA": "Nasa", "LINK": "Link"})
