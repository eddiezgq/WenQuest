"""Daily science 2026-11-06 (English): "SpaceX Is Selling Weightlessness?"
News: SpaceX's Starfall, a disk-shaped return capsule for microgravity research and manufacturing.
Trending: Hacker News front page 2026-11-05, #16 "Starfall – Affordable, routine access to microgravity" (spacex.com, 273 points, 210 comments when checked).
Facts:
- Space.com (2026-10-20): disk-shaped, about 0.75 m tall and 3.1 m wide, about 2,100 kg (FAA environmental assessment); can return about 1,000 kg of payload;
  first flight 2026-06-23 (Falcon 9, demonstration of controlled flight and surviving the descent), second flight 2026-10-20 on Bandwagon-5.
- TeslaNorth (2026-11-02), quoting SpaceX's Starfall page: up to 1,000 kg payload, 1 kW payload power, Ethernet, online via Starlink for the whole flight;
  "weeks of continuous microgravity" vs seconds for drop towers and parabolic flights; protein and small-molecule drug crystals form
  "smaller and more uniform shapes" without gravity-driven convection; organoids / stem-cell tissue; semiconductors and materials;
  three commercial Starfall missions signed (SpaceX Q3 results, 2026-10-20); no price listed; named for Starship as its vehicle.
Textbook physics: gravity at ~400 km altitude is ~90% of surface gravity; low-orbit speed ~7.7 km/s (~28,000 km/h); orbit = free fall that keeps missing
  (Newton's cannon); parabolic flights give ~20 s of float per arc; drop towers a few seconds; convection needs gravity (buoyancy).
Ours: "flying saucer" nickname, soup-pot metaphor, "crosses the US in about ten minutes" (4,500 km / 7.7 km/s, our arithmetic),
  the wide flat shape acting as a brake and shield is our guess (SpaceX has not described the heat shield).
Sources:
- https://news.ycombinator.com/front (2026-11-05)
- https://www.space.com/space-exploration/launches-spacecraft/spacex-starfall-return-capsule-launch-bandwagon-5-rideshare-mission
- https://teslanorth.com/2026/11/02/spacex-starfall-1000kg-drug-chip/
- https://x.com/SpaceX/status/2112498759854661751
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_saucer, stick  # noqa: E402

S = [
 ("SpaceX 开始卖失重了，|按吨卖。", "SpaceX is now selling weightlessness, | by the ton."),
 ("认识 Starfall：一个飞碟，|大约三米宽。", "Meet Starfall: a flying saucer, | about three meters wide."),
 ("它能带最多一千公斤的货|上太空，再带回家。", "It carries up to a thousand kilograms of cargo | up to orbit and back home."),
 ("它刚上了 Hacker News 首页，|评论区吵个不停。", "It just hit the Hacker News front page, | and people cannot stop arguing about it."),
 ("今天的烧脑问题：在轨道上，重力还有地面的九成。|那东西凭啥飘起来？", "Today's brain teaser: up there, gravity is still about ninety percent as strong. | So why does everything float?"),
 ("认识主角：小碟，|扁扁的小舱，干大活。", "Meet our hero, Saucy, | a flat little capsule with a big job."),
 ("老办法一：|从高塔上往下扔。", "The old way to get weightless: | drop something down a tall tower."),
 ("能飘几秒钟，|然后，咣。", "You get a few seconds of float. | Then, crunch."),
 ("老办法二：坐飞机像过山车一样俯冲，|飘大约二十秒，然后又变沉。", "Or ride a plane that dives like a roller coaster. | About twenty seconds of float, then everyone feels heavy again."),
 ("SpaceX 说，Starfall 能给你好几周。|不是几秒，是几周。", "SpaceX says Starfall gives you weeks of it. | Not seconds. Weeks."),
 ("反转一：轨道上有重力。|空间站那儿，重力还有地面的九成左右。", "Twist one: there is gravity in orbit. | At the space station, it is about ninety percent of what you feel here."),
 ("宇航员飘着，是因为他们在往下掉，|一直在掉。", "Astronauts float because they are falling. | All the time."),
 ("想象山顶上有门牛顿大炮，|打一发，球划个弧落地。", "Picture Newton's cannon on a mountain. | Fire a ball, and it curves down to the ground."),
 ("打得更快，落得更远；|快到一定程度，地面弯下去的速度跟球掉的一样快。", "Fire faster, it lands farther. | Fire fast enough, and the ground curves away as fast as the ball falls."),
 ("这就是轨道：|永远在掉，永远掉不到地上。", "That is an orbit: | falling forever, and always missing."),
 ("低轨道大约每小时两万八千公里，|我们算了下，十分钟左右横穿美国。", "In low orbit, that is about twenty eight thousand kilometers an hour. | Fast enough to cross America in about ten minutes."),
 ("你和实验室一起掉，|谁也压不着谁，这就是失重。", "When you and your lab fall together, | nothing presses on anything. That is weightless."),
 ("那花钱买“掉”图啥？|反转二：重力会把小晶体搅乱。", "So why pay for falling? | Twist two: gravity messes up tiny crystals."),
 ("药厂要把蛋白质长成晶体，|看清它的形状，才好做药。", "Drug makers grow crystals of proteins | to see their shape and design medicine."),
 ("在地面上，热的液体往上走，冷的往下沉，|这种翻滚叫对流。", "On Earth, warm liquid rises and cool liquid sinks. | That churning is called convection."),
 ("就像一锅一直在翻滚的汤，|晶体长得歪歪扭扭。", "It is like a pot of soup that never stops churning. | The crystals come out lumpy."),
 ("一起自由下落时，热液体没有“上”可去，|汤就安静了。", "In free fall, warm liquid has no up to rise toward. | The soup goes calm."),
 ("SpaceX 说，这样晶体长得更小、|更整齐。", "SpaceX says the crystals then grow smaller | and more uniform."),
 ("干细胞长的组织、|做芯片的新材料，也是这个道理。", "Same idea for tissue grown from stem cells, | and new materials for chips."),
 ("小碟让实验一直通着电：一千瓦，|还能通过星链实时联网。", "Saucy keeps the experiments plugged in: one kilowatt of power, | and a live link through Starlink."),
 ("反转三，最难的部分：|回家。", "Twist three, the hardest part: | coming home."),
 ("小碟用轨道速度一头扎进大气，|前面的空气被压得滚烫。", "Saucy slams into the air at orbital speed, | and the air in front gets crushed and blazing hot."),
 ("我们猜：它又宽又扁的肚皮，|既当刹车，又当盾牌。", "Our guess: its wide, flat belly | works as a brake and a shield."),
 ("它已经飞了两次，|六月一次，十月一次。", "It has flown twice, | once in June and again in October."),
 ("据报道，已经签了三单商业任务；|名字里的 Star，来自要拉它们的星舰。", "Reports say three paying missions are already signed. | The name comes from Starship, which would carry them."),
 ("友情提示：还没有标价，|“便宜”到底多便宜，没人知道。", "Fine print: there is no price yet, | so nobody knows how cheap affordable really is."),
 ("太空里长的药值不值，|也还是个没揭晓的赌局。", "And whether space-grown medicine pays off | is still an open bet."),
 ("还有，想搭便车的：|它只有七十五厘米高，装不下你。", "Also, if you are hoping to ride along: | it is about seventy five centimeters tall. You will not fit."),
 ("所以，轨道上的东西凭啥飘？|不是因为没重力。", "So why does everything float in orbit? | Not because gravity is gone."),
 ("而是大家一起在掉，|而且永远掉不到地上。", "Because everything is falling together, | and always missing the ground."),
 ("SpaceX 卖的不是零重力，|是一次非常、非常长的坠落。", "SpaceX is not selling zero gravity. | It is selling a very, very long fall."),
]
TITLE = {"zh": "SpaceX 开始卖失重了？", "en": "SpaceX Is Selling Weightlessness?"}

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


def floater(a, x, y, k=1.0, d=0.0):
    """A floating astronaut: stick figure that bobs and slowly rolls."""
    i = uid("fl")
    return stick(x, y, k, a, idp=i, arms="up") + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 14, "hz": 0.8},
                                                {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y - 100 * k], "amp": 12, "hz": 0.5}]


def saucy(a, x, y, k=1.0, d=0.0, mood="happy"):
    i = uid("sc")
    return cute_saucer(x, y, k, a, idp=i, mood=mood) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]


def earth(a, x, y, s=300, d=0.0):
    return ic(a, "globe", x, y, s, d, mv="spin", c="blue")


def ball(a, x, y, dx, dy, d=0.0, c="red", dur=1.0, r=18):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, dur)]


def crystal(a, x, y, s=40, d=0.0, c="blue", neat=True):
    i = uid("cy")
    if neat:
        dpath = f"M{x},{y - s} L{x + s * .8},{y} L{x},{y + s} L{x - s * .8},{y} Z"
    else:
        dpath = f"M{x},{y - s} L{x + s * 1.1},{y - s * .2} L{x + s * .4},{y + s * .9} L{x - s},{y + s * .5} L{x - s * .6},{y - s * .6} Z"
    return [P(a, dpath, c=c, w=5, idp=i), pop(a, i, d), wig(a, i, (x, y), 4 if neat else 12, 1.0 if neat else 3.0)]


def pot(a, x, y, d=0.0, churn=True):
    i = uid("pt")
    E = [P(a, f"M{x - 220},{y - 150} L{x - 200},{y + 130} L{x + 200},{y + 130} L{x + 220},{y - 150}", c="ink", w=7, idp=i), pop(a, i, d)]
    for s_ in (-1, 1):
        j = uid("cv")
        E += [P(a, f"M{x + s_ * 30},{y + 80} Q{x + s_ * 170},{y + 60} {x + s_ * 150},{y - 40} Q{x + s_ * 120},{y - 110} {x + s_ * 40},{y - 60}", c="red", w=6, idp=j),
              pop(a, j, d + 0.2), (spin(a, j, (x + s_ * 95, y), 50 * s_) if churn else wig(a, j, (x, y), 1, 0.5))]
    return E


def tower(a, x, d=0.0):
    i = uid("tw")
    return [R(a, x - 60, 200, 120, 780, c="ink", fill="paper", idp=i), pop(a, i, d), wig(a, i, (x, 980), 1, 1.0)]


def flame(a, x, y, s=120, d=0.0):
    return ic(a, "flame", x, y, s, d, mv="wig", c="red")


# ---------- boards ----------
bd(0, saucy(0, 960, 520, 1.6, 0.0), floater(0, 500, 700, 1.0, 0.2), floater(0, 1450, 650, 0.9, 0.3), big(0, 960, 900, "weightlessness for sale", c="red", d=0.4, s=80))
bd(0.5, big(0.5, 960, 330, "1,000 kg", c="red", d=0.0, s=180), saucy(0.5, 960, 700, 1.0, 0.2), [ball(0.5, 600 + 180 * q, 900, 0, -60, 0.3 + 0.1 * q, c="gold") for q in range(5)])
bd(1, saucy(1, 960, 560, 2.0, 0.0), t(1, 960, 900, 70, "Starfall", c="blue", d=0.3), star(1, 500, 400, 0.4, r=40), star(1, 1420, 400, 0.5, r=40))
bd(1.5, saucy(1.5, 960, 500, 1.6, 0.0), arr(1.5, 640, 750, 1280, 750, c="red", d=0.2), arr(1.5, 1280, 750, 640, 750, c="red", d=0.3), big(1.5, 960, 880, "about 3 m", c="red", d=0.4, s=100))
bd(2, saucy(2, 600, 600, 1.0, 0.0), [R(2, 1150 + 130 * (q % 3), 750 - 130 * (q // 3), 110, 110, c="ink", fill="gold", idp=f"bx2_{q}") for q in range(6)],
   [pop(2, f"bx2_{q}", 0.1 + 0.07 * q) for q in range(6)], [wig(2, f"bx2_{q}", (1300, 800), 2, 1.5) for q in range(6)], t(2, 1350, 300, 64, "cargo", d=0.3))
bd(2.5, earth(2.5, 500, 750, 320, 0.0), saucy(2.5, 1350, 350, 0.8, 0.1), arr(2.5, 650, 600, 1150, 380, c="blue", d=0.2), arr(2.5, 1250, 480, 750, 700, c="red", d=0.5), t(2.5, 1400, 800, 56, "up and back", d=0.4))
bd(3, ic(3, "computer", 550, 560, 300, 0.0, mv="wig"), big(3, 1300, 380, "front page", c="red", d=0.2, s=110), saucy(3, 1300, 700, 0.8, 0.3))
bd(3.5, man(3.5, 450, 950, 1.4, 0.0, arms="up", amp=8), man(3.5, 850, 950, 1.3, 0.1, arms="up", amp=8), man(3.5, 1250, 950, 1.4, 0.2, arms="up", amp=8),
   ic(3.5, "speaker", 1620, 500, 200, 0.3, mv="wig"), t(3.5, 960, 280, 70, "arguing!", c="red", d=0.3))
bd(4, big(4, 960, 260, "Brain teaser", c="red", d=0.0, s=120), earth(4, 600, 700, 300, 0.1), ic(4, "satellite", 1150, 450, 160, 0.2, mv="bob"), big(4, 1450, 700, "90%", c="blue", d=0.3, s=150))
bd(4.5, floater(4.5, 700, 750, 1.4, 0.0), ic(4.5, "question", 1300, 500, 260, 0.2, mv="wig", c="red"), ball(4.5, 1000, 400, 0, -60, 0.3, c="gold"), ball(4.5, 1100, 750, 40, -40, 0.4, c="blue"))
bd(5, saucy(5, 960, 540, 2.2, 0.0), t(5, 960, 920, 70, "Saucy", c="blue", d=0.3), star(5, 450, 380, 0.4, r=40), star(5, 1470, 380, 0.5, r=40))
bd(5.5, saucy(5.5, 650, 600, 1.2, 0.0), ic(5.5, "flask", 1250, 550, 180, 0.2, mv="wig", c="blue"), ic(5.5, "chip", 1550, 550, 160, 0.3, mv="spin", c="gold"), t(5.5, 1400, 850, 60, "big job", c="red", d=0.4))
bd(6, tower(6, 600, 0.0), ball(6, 600, 230, 0, 700, 0.3, c="red", dur=1.5), man(6, 1100, 980, 1.3, 0.1), t(6, 1400, 400, 70, "drop tower", d=0.2), ic(6, "clock", 1450, 650, 160, 0.4, mv="spin"))
bd(6.5, tower(6.5, 960, 0.0), floater(6.5, 960, 500, 0.6, 0.1), sh(6.5, [], 0, 0, 0, 0.1) if False else [], arr(6.5, 1150, 300, 1150, 800, c="red", d=0.3), t(6.5, 1500, 500, 60, "falling = floating", c="blue", d=0.4))
bd(7, big(7, 1300, 400, "a few seconds", c="blue", d=0.0, s=100), ic(7, "clock", 500, 560, 280, 0.1, mv="spin"), floater(7, 1300, 800, 0.7, 0.3))
bd(7.5, P(7.5, "M300,900 L1620,900", c="ink", w=8, idp="gnd7"), pop(7.5, "gnd7", 0.0), ball(7.5, 960, 300, 0, 560, 0.0, c="red", dur=0.5, r=40),
   big(7.5, 960, 400, "CRUNCH", c="red", d=0.4, s=150), [ic(7.5, "flame", 800 + 160 * q, 830, 90, 0.5 + 0.05 * q, mv="wig", c="gold") for q in range(3)])
bd(8, ic(8, "rocket", 400, 700, 200, 0.0, mv="wig"), P(8, "M300,850 Q700,200 960,300 Q1250,400 1650,850", c="blue", w=6, idp="para"), pop(8, "para", 0.1),
   ball(8, 300, 850, 660, -500, 0.3, c="red", dur=1.5), t(8, 1300, 300, 60, "roller coaster plane", d=0.3))
bd(8.5, big(8.5, 700, 400, "~20 s", c="blue", d=0.0, s=170), floater(8.5, 700, 800, 0.8, 0.1), man(8.5, 1350, 950, 1.4, 0.3), arr(8.5, 1350, 450, 1350, 650, c="red", d=0.4), t(8.5, 1650, 450, 56, "heavy!", c="red", d=0.5))
bd(9, saucy(9, 600, 550, 1.2, 0.0), big(9, 1350, 400, "weeks", c="red", d=0.2, s=180), [ic(9, "clock", 1100 + 180 * q, 750, 120, 0.3 + 0.07 * q, mv="spin") for q in range(4)])
bd(9.5, bar(9.5, 450, 950, 160, 30, "muted", 0.0), t(9.5, 530, 1010, 40, "tower", d=0.0), bar(9.5, 800, 950, 160, 90, "blue", 0.2), t(9.5, 880, 1010, 40, "plane", d=0.2),
   bar(9.5, 1150, 950, 160, 650, "red", 0.4, 1.2), t(9.5, 1230, 1010, 40, "Starfall", d=0.4), saucy(9.5, 1600, 400, 0.6, 0.5))
bd(10, big(10, 960, 260, "Twist one", c="red", d=0.0, s=140), earth(10, 650, 700, 320, 0.1), ic(10, "satellite", 1250, 520, 160, 0.2, mv="bob"),
   arr(10, 1250, 620, 900, 680, c="red", d=0.4), t(10, 1450, 800, 56, "gravity is here", c="red", d=0.5))
bd(10.5, earth(10.5, 960, 650, 360, 0.0), ic(10.5, "satellite", 960, 300, 140, 0.1, mv="bob"), big(10.5, 1500, 400, "~90%", c="blue", d=0.3, s=140), [arr(10.5, 960 + 300 * dx, 650 + 300 * dy, 960 + 220 * dx, 650 + 220 * dy, c="red", d=0.3 + 0.06 * q)
   for q, (dx, dy) in enumerate([(1, 0), (-1, 0), (0, 1), (0.7, -0.7), (-0.7, -0.7), (0.7, 0.7), (-0.7, 0.7)])])
bd(11, floater(11, 700, 650, 1.4, 0.0), arr(11, 1050, 300, 1050, 800, c="red", d=0.2), t(11, 1450, 450, 70, "falling", c="red", d=0.3), ic(11, "satellite", 1450, 750, 160, 0.4, mv="bob"))
bd(11.5, earth(11.5, 960, 600, 300, 0.0), O(11.5, 960, 600, 330, c="muted", idp="orb11", sw=4), pop(11.5, "orb11", 0.1), ic(11.5, "satellite", 1290, 600, 120, 0.2, mv="bob"),
   rot(11.5, [], 0, (0, 0), 0, 0.1) if False else [], ball(11.5, 960, 270, 330, 330, 0.3, c="blue", dur=1.5), t(11.5, 960, 1000, 56, "all the time", d=0.4))
bd(12, P(12, "M200,950 Q960,700 1720,950", c="green", w=8, idp="hill"), pop(12, "hill", 0.0), R(12, 900, 640, 160, 70, c="ink", fill="ink", idp="cannon"), pop(12, "cannon", 0.1),
   wig(12, "cannon", (980, 700), 3, 2), man(12, 800, 720, 0.8, 0.2), t(12, 960, 300, 64, "Newton's cannon", c="blue", d=0.3))
bd(12.5, P(12.5, "M200,950 Q960,700 1720,950", c="green", w=8, idp="hill2"), pop(12.5, "hill2", 0.0), R(12.5, 900, 640, 160, 70, c="ink", fill="ink", idp="can2"), pop(12.5, "can2", 0.0),
   P(12.5, "M1060,660 Q1250,600 1350,850", c="red", w=5, idp="arc1"), pop(12.5, "arc1", 0.2), ball(12.5, 1060, 660, 290, 190, 0.3, c="red", dur=0.8), flame(12.5, 1360, 880, 90, 0.6))
bd(13, earth(13, 960, 700, 420, 0.0), [P(13, f"M960,450 Q{1150 + 150 * q},{430 - 20 * q} {1100 + 160 * q},{650 + 40 * q}", c=["red", "gold", "blue"][q], w=5, idp=f"arc13_{q}") for q in range(3)],
   [pop(13, f"arc13_{q}", 0.1 + 0.2 * q) for q in range(3)], ball(13, 960, 450, 300, 250, 0.5, c="red"))
bd(13.5, earth(13.5, 960, 600, 360, 0.0), O(13.5, 960, 600, 300, c="blue", idp="orb13", sw=5), pop(13.5, "orb13", 0.2), ic(13.5, "satellite", 960, 300, 110, 0.0, mv="bob"),
   arr(13.5, 1300, 300, 1300, 450, c="red", d=0.3), arr(13.5, 1260, 600, 1100, 600, c="blue", d=0.4), t(13.5, 1600, 900, 50, "ground curves away", c="blue", d=0.4))
bd(14, earth(14, 960, 600, 360, 0.0), O(14, 960, 600, 300, c="blue", idp="orb14", sw=5), pop(14, "orb14", 0.1), saucy(14, 960, 300, 0.5, 0.2), t(14, 960, 1000, 64, "an orbit", c="blue", d=0.3))
bd(14.5, earth(14.5, 700, 600, 300, 0.0), ic(14.5, "satellite", 700, 300, 120, 0.1, mv="bob"), big(14.5, 1400, 450, "always", c="red", d=0.2, s=130), big(14.5, 1400, 650, "missing", c="blue", d=0.4, s=130))
bd(15, big(15, 960, 330, "28,000 km/h", c="red", d=0.0, s=150), ic(15, "rocket", 500, 700, 200, 0.2, mv="wig"), ball(15, 700, 700, 900, 0, 0.3, c="red", dur=0.8), ic(15, "wind", 1500, 700, 180, 0.4, mv="wig"))
bd(15.5, R(15.5, 400, 450, 1100, 400, c="ink", fill="paper", idp="usa"), pop(15.5, "usa", 0.0), wig(15.5, "usa", (950, 650), 1, 1), t(15.5, 950, 650, 60, "USA", c="muted", d=0.1),
   ic(15.5, "satellite", 400, 450, 120, 0.2, mv="bob"), arr(15.5, 450, 400, 1450, 400, c="red", d=0.3, dur=1.2), big(15.5, 1650, 850, "~10 min", c="red", d=0.4, s=90))
bd(16, floater(16, 700, 700, 1.1, 0.0), R(16, 450, 300, 600, 600, c="blue", idp="lab16"), pop(16, "lab16", 0.1), bob(16, "lab16", 14, 0.8), ball(16, 900, 450, 0, -30, 0.2, c="gold"),
   arr(16, 1300, 300, 1300, 700, c="red", d=0.3), t(16, 1550, 500, 56, "fall together", d=0.4))
bd(16.5, floater(16.5, 600, 700, 1.2, 0.0), floater(16.5, 1000, 600, 1.0, 0.1), ball(16.5, 1300, 400, 30, -30, 0.2, c="gold"), crystal(16.5, 1500, 700, 50, 0.3), big(16.5, 960, 250, "weightless", c="blue", d=0.4, s=110))
bd(17, ic(17, "question", 600, 560, 260, 0.0, mv="wig", c="red"), saucy(17, 1300, 450, 0.9, 0.2), big(17, 1300, 800, "$ ?", c="red", d=0.3, s=130))
bd(17.5, big(17.5, 960, 260, "Twist two", c="red", d=0.0, s=140), crystal(17.5, 700, 650, 90, 0.2, neat=False), crystal(17.5, 1000, 700, 70, 0.3, neat=False), crystal(17.5, 1300, 640, 80, 0.4, neat=False),
   arr(17.5, 1000, 950, 1000, 800, c="ink", d=0.4))
bd(18, ic(18, "flask", 500, 600, 280, 0.0, mv="wig", c="blue"), ic(18, "molecule", 960, 600, 220, 0.2, mv="spin", c="gold"), arr(18, 1100, 600, 1300, 600, c="ink", d=0.3), crystal(18, 1500, 600, 90, 0.4))
bd(18.5, ic(18.5, "magnifier", 600, 560, 280, 0.0, mv="wig"), crystal(18.5, 600, 520, 50, 0.1), ic(18.5, "flask", 1300, 560, 220, 0.3, mv="wig", c="red"), t(18.5, 1300, 850, 60, "design medicine", d=0.4))
bd(19, pot(19, 960, 650, 0.0), ic(19, "flame", 960, 880, 120, 0.1, mv="wig", c="red"), arr(19, 1350, 750, 1350, 450, c="red", d=0.3), arr(19, 570, 450, 570, 750, c="blue", d=0.4))
bd(19.5, pot(19.5, 800, 650, 0.0), t(19.5, 1450, 450, 80, "convection", c="red", d=0.2), ic(19.5, "sine", 1450, 700, 200, 0.3, mv="wig", c="red"))
bd(20, pot(20, 700, 650, 0.0), man(20, 1300, 950, 1.3, 0.2), ic(20, "flame", 700, 880, 120, 0.1, mv="wig", c="red"), bubbles(20, 700, 600, 4, 0.3, 300, "red"))
bd(20.5, crystal(20.5, 600, 600, 120, 0.0, neat=False), crystal(20.5, 960, 650, 90, 0.1, neat=False), crystal(20.5, 1300, 600, 110, 0.2, neat=False), big(20.5, 960, 300, "lumpy", c="red", d=0.3, s=140))
bd(21, pot(21, 700, 650, 0.0, churn=False), floater(21, 1300, 700, 1.0, 0.1), ic(21, "question", 700, 300, 140, 0.3, mv="wig", c="red"), t(21, 1300, 300, 60, "no up", c="blue", d=0.3))
bd(21.5, pot(21.5, 960, 650, 0.0, churn=False), big(21.5, 960, 280, "calm", c="blue", d=0.2, s=150), saucy(21.5, 1600, 450, 0.6, 0.3), check(21.5, 1600, 750, d=0.4))
bd(22, [crystal(22, 500 + 150 * q, 600, 40, 0.1 * q) for q in range(8)], t(22, 960, 350, 70, "smaller", c="blue", d=0.3), saucy(22, 960, 850, 0.6, 0.4))
bd(22.5, [crystal(22.5, 500 + 150 * q, 500 + 150 * (q % 2), 55, 0.05 * q) for q in range(8)], big(22.5, 960, 280, "uniform", c="green", d=0.3, s=130), check(22.5, 1650, 850, d=0.5))
bd(23, ic(23, "molecule", 600, 560, 260, 0.0, mv="spin", c="red"), [O(23, 1150 + 80 * (q % 4), 450 + 80 * (q // 4), 34, c="red", fill="paper", idp=f"cel{q}") for q in range(8)],
   [pop(23, f"cel{q}", 0.2 + 0.05 * q) for q in range(8)], [wig(23, f"cel{q}", (1270, 490), 3, 1.5) for q in range(8)], t(23, 1270, 800, 56, "stem cell tissue", d=0.4))
bd(23.5, ic(23.5, "chip", 650, 560, 280, 0.0, mv="spin", c="blue"), ic(23.5, "lattice", 1300, 560, 260, 0.2, mv="wig", c="gold"), t(23.5, 960, 900, 60, "new materials for chips", d=0.4))
bd(24, saucy(24, 600, 600, 1.2, 0.0), ic(24, "battery", 1250, 500, 200, 0.2, mv="wig", c="green"), big(24, 1250, 800, "1 kW", c="red", d=0.3, s=120))
bd(24.5, ic(24.5, "satellite", 500, 350, 180, 0.0, mv="bob"), saucy(24.5, 1100, 650, 1.0, 0.1), ic(24.5, "signal", 800, 480, 140, 0.2, mv="wig", c="blue"), t(24.5, 1500, 350, 60, "Starlink", c="blue", d=0.3),
   ic(24.5, "computer", 1600, 750, 160, 0.4, mv="wig"))
bd(25, big(25, 960, 260, "Twist three", c="red", d=0.0, s=140), saucy(25, 700, 650, 1.0, 0.2, mood="o"), flame(25, 1250, 650, 200, 0.3), ic(25, "thermometer", 1600, 650, 180, 0.4, mv="wig", c="red"))
bd(25.5, earth(25.5, 960, 750, 360, 0.0), saucy(25.5, 1400, 300, 0.7, 0.1), arr(25.5, 1300, 380, 1100, 560, c="red", d=0.3), t(25.5, 600, 300, 70, "coming home", c="blue", d=0.3))
bd(26, saucy(26, 960, 600, 1.4, 0.0, mood="o"), [arr(26, 400 + 0 * q, 300 + 150 * q, 650, 450 + 75 * q, c="muted", d=0.1 + 0.08 * q) for q in range(4)], flame(26, 1400, 400, 140, 0.4))
bd(26.5, saucy(26.5, 960, 700, 1.2, 0.0, mood="o"), [flame(26.5, 700 + 130 * q, 520, 110, 0.1 + 0.06 * q) for q in range(5)], big(26.5, 960, 250, "blazing hot", c="red", d=0.4, s=110))
bd(27, saucy(27, 960, 600, 1.8, 0.0), t(27, 960, 250, 64, "our guess", c="muted", d=0.2), [arr(27, 600 + 180 * q, 950, 600 + 180 * q, 760, c="red", d=0.2 + 0.06 * q) for q in range(5)])
bd(27.5, saucy(27.5, 960, 500, 1.4, 0.0), R(27.5, 660, 600, 600, 50, c="red", fill="red", idp="shld"), pop(27.5, "shld", 0.2), wig(27.5, "shld", (960, 625), 2, 3),
   t(27.5, 500, 850, 60, "brake", c="blue", d=0.3), t(27.5, 1420, 850, 60, "shield", c="red", d=0.4))
bd(28, saucy(28, 600, 550, 1.0, 0.0), ic(28, "rocket", 1150, 600, 220, 0.2, mv="wig"), ic(28, "rocket", 1450, 600, 220, 0.3, mv="wig"), big(28, 1300, 900, "2 flights", c="red", d=0.4, s=90))
bd(28.5, t(28.5, 650, 400, 90, "June", c="blue", d=0.0), t(28.5, 1250, 400, 90, "October", c="red", d=0.2), check(28.5, 650, 600, d=0.2), check(28.5, 1250, 600, d=0.4),
   saucy(28.5, 960, 850, 0.6, 0.3))
bd(29, [ic(29, "check", 600 + 350 * q, 500, 180, 0.1 + 0.15 * q, mv="bob", c="green") for q in range(3)], big(29, 960, 800, "3 missions signed", c="red", d=0.4, s=90))
bd(29.5, ic(29.5, "rocket", 600, 560, 320, 0.0, mv="wig"), t(29.5, 1300, 400, 70, "Starship", c="blue", d=0.2), [saucy(29.5, 1100 + 250 * q, 750, 0.4, 0.3 + 0.1 * q) for q in range(3)])
bd(30, big(30, 960, 280, "Fine print", c="blue", d=0.0, s=130), ic(30, "question", 600, 650, 220, 0.2, mv="wig", c="red"), big(30, 1300, 650, "$ ???", c="red", d=0.3, s=130))
bd(30.5, ic(30.5, "magnifier", 650, 560, 260, 0.0, mv="wig"), t(30.5, 1300, 450, 64, "how cheap?", c="red", d=0.2), man(30.5, 1300, 950, 1.0, 0.3), saucy(30.5, 1650, 600, 0.5, 0.4))
bd(31, ic(31, "flask", 600, 600, 260, 0.0, mv="wig", c="blue"), crystal(31, 600, 330, 50, 0.1), ic(31, "question", 1300, 560, 240, 0.2, mv="wig", c="red"), bar(31, 1550, 900, 80, 200, "gold", 0.3))
bd(31.5, O(31.5, 960, 600, 200, c="ink", fill="gold", idp="coin31"), pop(31.5, "coin31", 0.0), spin(31.5, "coin31", (960, 600), 60), t(31.5, 960, 600, 80, "?", d=0.1),
   t(31.5, 960, 920, 64, "an open bet", c="red", d=0.3), man(31.5, 450, 950, 1.2, 0.2), man(31.5, 1470, 950, 1.2, 0.3))
bd(32, man(32, 600, 950, 1.5, 0.0, arms="up", amp=8), saucy(32, 1250, 600, 1.2, 0.1, mood="o"), arr(32, 800, 600, 1000, 600, c="blue", d=0.3), ic(32, "question", 600, 300, 140, 0.4, mv="wig", c="red"))
bd(32.5, saucy(32.5, 900, 750, 1.0, 0.0), man(32.5, 1450, 950, 1.6, 0.1), big(32.5, 900, 350, "75 cm", c="red", d=0.2, s=150), cross(32.5, 1450, 400, d=0.5))
bd(33, floater(33, 700, 700, 1.3, 0.0), ic(33, "question", 1300, 500, 260, 0.2, mv="wig", c="red"), ball(33, 1100, 800, 30, -40, 0.3, c="gold"))
bd(33.5, earth(33.5, 700, 650, 300, 0.0), [arr(33.5, 700 + 250 * dx, 650 + 250 * dy, 700 + 170 * dx, 650 + 170 * dy, c="red", d=0.2 + 0.06 * q)
   for q, (dx, dy) in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1)])], t(33.5, 1350, 500, 60, "gravity is not gone", c="red", d=0.4), check(33.5, 1350, 700, d=0.5))
bd(34, floater(34, 600, 700, 1.0, 0.0), R(34, 400, 350, 450, 500, c="blue", idp="lab34"), pop(34, "lab34", 0.1), bob(34, "lab34", 14, 0.8), saucy(34, 1300, 500, 0.8, 0.2),
   arr(34, 1100, 700, 1100, 950, c="red", d=0.3), arr(34, 1550, 700, 1550, 950, c="red", d=0.4))
bd(34.5, earth(34.5, 960, 600, 360, 0.0), O(34.5, 960, 600, 300, c="blue", idp="orb34", sw=5), pop(34.5, "orb34", 0.1), saucy(34.5, 1260, 600, 0.4, 0.2),
   ball(34.5, 960, 300, 300, 300, 0.3, c="red", dur=1.5), t(34.5, 960, 1000, 56, "always missing", c="blue", d=0.4))
bd(35, big(35, 960, 300, "zero gravity", c="ink", d=0.0, s=120), cross(35, 960, 300, d=0.3), saucy(35, 960, 700, 1.0, 0.3), floater(35, 1550, 700, 0.8, 0.4))
bd(35.5, saucy(35.5, 960, 450, 1.5, 0.0), earth(35.5, 960, 820, 200, 0.1), arr(35.5, 1400, 400, 1400, 800, c="red", d=0.2, dur=1.2), big(35.5, 960, 200, "a very long fall", c="red", d=0.4, s=100))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"SpaceX": "Space X", "Starfall": "Star fall", "Starlink": "Star link", "Starship": "Star ship", "Saucy": "Saw see"})
