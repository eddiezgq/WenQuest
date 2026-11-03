"""Daily science 2026-11-03 (English): "Hackers Turned Fridges Into Ovens"
News: a cyberattack on supermarket refrigeration controls hit about 700 of France's ~10,000 supermarkets in October (AP);
  fridge temperatures were forced up to 50 °C overnight (Irish Examiner headline); fires reported, being investigated (AP / Reuters);
  the control software came from Danfoss, which said most affected systems were older, no longer updated, and advised updating firmware and using a firewall (AP);
  a new wave hit European chains in late October (PBS / AP, 2026-10-29); Nov 2 roundups: >100 more locations incl. Carrefour Belgium, SuperValu (reportedly).
Trending: TechStartups "Top Tech News Today, November 2, 2026", item 5 (European supermarket cyberattacks).
Sources:
- https://techstartups.com/2026/11/02/top-tech-news-today-november-2-2026-the-biggest-stories-in-ai-startups-and-big-tech/
- https://www.pbs.org/newshour/world/cyberattacks-disrupt-refrigeration-systems-at-european-supermarkets
- https://www.irishexaminer.com/world/arid-41923315.html
Physics (textbook): a fridge does not make cold, it pumps heat out (refrigerant evaporates inside, condenses at the coils outside);
  the back of a fridge is warm; USDA "danger zone" 40–140 °F (about 4–60 °C), bacteria can double in about 20 minutes.
Speculation, said as such: how the boxes reached 50 °C (we guess heaters, e.g. defrost heaters, left on — not confirmed).
Metaphor (the fridge = a bouncer throwing heat out the back door) is ours.
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_fridge, stick  # noqa: E402

S = [
 ("黑客一夜之间，|把超市冰箱烧到了五十度。", "Overnight, hackers pushed supermarket fridges | to fifty degrees Celsius."),
 ("五十度，|比三伏天的车里还热。", "Fifty degrees. | Hotter than a car in the summer sun."),
 ("据美联社，十月份法国约七百家超市中招，|一共才一万家左右。", "According to AP, about seven hundred French supermarkets were hit in October, | out of roughly ten thousand."),
 ("十月底，欧洲又来一波，|据报道比利时、爱尔兰的连锁店也遭殃。", "Late October, a new wave hit Europe. | Reportedly chains in Belgium and Ireland too."),
 ("今天的烧脑问题：|冰箱是制冷的，凭啥能变成烤箱？", "Today's brain teaser: | a fridge makes cold, so how can it turn into an oven?"),
 ("先认识主角：小冰，|一台超市冰柜。", "Meet our hero, Frosty, | a supermarket fridge."),
 ("反转一：冰箱根本不“造冷”。", "Twist one: a fridge does not make cold at all."),
 ("世上没有“冷”这种东西，|只有热多热少。", "There is no such stuff as cold. | There is only more heat or less heat."),
 ('冷，不过是分子晃得慢；|热，是同样的分子晃得快。', 'Cold is just molecules jiggling slowly. | Heat is the same molecules jiggling fast.'),
 ("冰箱干的活，|是把热从里面赶到外面。", "A fridge's job | is to throw heat from inside to outside."),
 ("它像夜店门口的保安，|把热一个个请出后门。", "It is like a bouncer, | showing heat out the back door, one by one."),
 ("不信摸摸冰箱背后：|是热的。", "Don't believe it? Touch the back of your fridge. | It's warm."),
 ('其实冰箱一直在给厨房加热，|吐出的是食物的热，加上电机自己的热。', "In fact, a fridge heats your kitchen. | It dumps the food's heat, plus its own motor's heat."),
 ("怎么赶？|靠一种会“跑”的液体，叫制冷剂。", "How? | With a fluid that keeps moving, called refrigerant."),
 ("它在里面蒸发，|把热吸走。", "Inside, it boils off | and soaks up heat."),
 ("就像你出汗，|汗一蒸发，身上就凉了。", "Like sweat: | when it evaporates, you cool down."),
 ("压缩机再把它压紧，|在背后的管子里把热吐出去。", "Then the compressor squeezes it, | and the coils out back dump the heat."),
 ("一圈又一圈，|保安一直在加班。", "Round and round. | The bouncer never clocks out."),
 ('所以开着冰箱门给厨房降温？|只会越开越热。', 'So, open the fridge to cool your kitchen? | The room only gets warmer.'),
 ("反转二：保安是听电脑指挥的。", "Twist two: the bouncer takes orders from a computer."),
 ("超市的冰柜连着一套控制系统，|远程就能调温度。", "Supermarket fridges are linked to a control system. | You can set the temperature remotely."),
 ("据美联社，系统来自丹麦的丹佛斯公司，|中招的多是老设备，早就不再更新。", "According to AP, the software was from Danfoss, a Danish company. | Most hit systems were old, no longer updated."),
 ("门锁坏了没人修，|黑客就从网上溜了进来。", "The lock was broken and never fixed, | so hackers slipped in over the internet."),
 ('像把家门钥匙压在门垫下，|再把地址贴到网上。', 'Like leaving your key under the doormat, | then posting your address online.'),
 ('冰柜为啥要上网？|好让一个人在一块屏幕上，盯住几百家店。', 'Why put a fridge online at all? | So one person can watch hundreds of stores from one screen.'),
 ("那怎么烧到五十度？|这一步，我们只能推测。", "So how did they reach fifty degrees? | This part is our guess."),
 ("冰柜里本来就有加热丝，|用来化霜。", "Fridges actually contain heaters, | for melting frost."),
 ("要是保安被关掉、加热丝一直开着，|冰柜就成了一个小烤箱。", "Turn the bouncer off and leave the heaters on, | and the fridge becomes a small oven."),
 ("据报道，有的店还冒了火，|起因还在调查。", "Reportedly some stores even had fires. | The cause is still being investigated."),
 ("反转三，最吓人的不是热，|是细菌。", "Twist three, the scariest part is not the heat. | It is the bacteria."),
 ("美国农业部说，四度到六十度是“危险区”。", "The USDA calls four to sixty degrees Celsius the danger zone."),
 ("在这个区间，细菌最快|大约二十分钟翻一倍。", "In that zone, bacteria can double | in about twenty minutes."),
 ("一个变两个，两个变四个，|一夜就是天文数字。", "One becomes two, two become four. | Overnight, that is an astronomical number."),
 ('二十分钟翻一倍，|一天就是七十二次翻倍，这是纸上算的。', 'A doubling every twenty minutes | is seventy-two doublings a day, on paper.'),
 ("所以热过一夜的肉和奶，|只能扔掉。", "So meat and milk that sat warm overnight | have to be thrown out."),
 ("冷其实不杀细菌，|只是让它们“冬眠”。", "Cold doesn't kill bacteria. | It just puts them to sleep."),
 ('所以冻肉一化开，|细菌就醒过来接着长。', "That's why frozen meat, once thawed, | lets the bacteria wake up and grow again."),
 ("保安一下班，|细菌就开派对。", "When the bouncer clocks out, | the bacteria throw a party."),
 ("友情提示：七百家、五十度来自新闻报道；|加热丝怎么被打开，是我们的推测。", "Fine print: seven hundred stores and fifty degrees come from news reports. | How the heaters were switched on is our guess."),
 ("法国财长说，食品供应没有风险。", "France's finance minister said food supply was never at risk."),
 ('据美联社，丹佛斯的建议很朴素：|及时更新，再加一道防火墙。', "According to AP, the advice from Danfoss is boring: | keep it updated, and put it behind a firewall."),
 ("所以，冰箱凭啥变烤箱？|因为它从来不造冷，只会搬热。", "So how does a fridge become an oven? | It never made cold. It only moves heat."),
 ("冷，从来不在冰箱里。|它只是热，被请出了门。", "The cold was never in the fridge. | It was just heat, shown the door."),
]
TITLE = {"zh": "黑客把冰箱变成烤箱", "en": "Hackers Turned Fridges Into Ovens"}

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


def fridge(a, x, y, k=1.0, d=0.0, mood="happy", hot=False):
    i = uid("fz")
    E = cute_fridge(x, y, k, a, idp=i, mood=mood, hot=hot) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if hot:
        for q, dx in enumerate((-70, 70)):
            E += ic(a, "flame", x + dx * k, y + 20, 70 * k, d + 0.2 + 0.1 * q, mv="wig", c="red")
    return E


def heat(a, x, y, n=5, dx=400, dy=0, d=0.0, c="red"):
    """热的小红点被赶走（一个点一个动作，错开）。"""
    E = []
    for q in range(n):
        i = uid("ht")
        E += [O(a, x + 20 * (q % 2), y - 100 + 50 * q, 18, c=c, fill=c, idp=i), pop(a, i, d + 0.07 * q), sh(a, i, dx, dy - 20 + 10 * q, d + 0.3 + 0.18 * q, 1.2)]
    return E


def bouncer(a, x, y, k=1.5, d=0.0):
    i, j = uid("bn"), uid("bg")
    E = stick(x, y, k, a, idp=i, arms="up") + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                               {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": 6, "hz": 2.0}]
    E += [R(a, x - 60 * k, y - 330 * k, 120 * k, 26 * k, c="ink", fill="ink", idp=j), pop(a, j, d + 0.2)]
    return E


def door(a, x, y, d=0.0, open_=True):
    i = uid("dr")
    E = [R(a, x - 90, y - 300, 180, 300, c="ink", fill="gold", idp=i), pop(a, i, d)]
    if open_:
        E.append(rot(a, i, -35, (x - 90, y - 150), d + 0.4, 0.6))
    return E


def coils(a, x, y, d=0.0, c="red"):
    i = uid("cl")
    p = f"M{x},{y}" + "".join(f" Q{x + 60},{y + 40 * q + 20} {x},{y + 40 * q + 40}" if q % 2 == 0 else f" Q{x - 60},{y + 40 * q + 20} {x},{y + 40 * q + 40}" for q in range(8))
    return [P(a, p, c=c, w=8, idp=i), pop(a, i, d), wig(a, i, (x, y + 160), 3, 3.0)]


def loop(a, x, y, r=260, d=0.0, n=6):
    """制冷剂循环：一圈管子 + 小点一直沿着跑（spin 一组点）。"""
    i, j = uid("lp"), uid("ld")
    E = [O(a, x, y, r, c="blue", idp=i, sw=8), pop(a, i, d)]
    import math
    for q in range(n):
        ang = 2 * math.pi * q / n
        E.append(O(a, x + r * math.cos(ang), y + r * math.sin(ang), 18, c="blue" if q % 2 else "red", fill="blue" if q % 2 else "red", idp=j))
    E += [pop(a, j, d + 0.2), spin(a, j, (x, y), 30)]
    return E


def thermo(a, x, y, d=0.0, up=True):
    i, j = uid("tm"), uid("tl")
    h = 360
    E = [R(a, x - 30, y - h, 60, h, c="ink", idp=i, sw=6), O(a, x, y + 30, 50, c="ink", fill="red", idp=i), pop(a, i, d),
         R(a, x - 18, y - (h - 30 if up else 60), 36, h - 30 if up else 60, c="red", fill="red", idp=j)]
    E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y], "dur": 1.0, "delay": d + 0.2})
    return E


def germs(a, x, y, n=8, d=0.0, step=0.12, c="green", party=False):
    """细菌：一个个冒出来（翻倍），一直在扭。"""
    E = []
    for q in range(n):
        i = uid("gm")
        gx, gy = x + 110 * (q % 4), y + 110 * (q // 4)
        E += [O(a, gx, gy, 38, c="ink", fill=c, idp=i), P(a, f"M{gx - 12},{gy - 8} L{gx - 12},{gy} M{gx + 12},{gy - 8} L{gx + 12},{gy}", c="ink", w=5, idp=i),
              pop(a, i, d + step * q), wig(a, i, (gx, gy), 14 if party else 6, 3.0 if party else 1.5)]
    return E


def drops(a, x, y, n=3, d=0.0, c="blue"):
    E = []
    for q in range(n):
        i = uid("dp")
        E += [O(a, x + 50 * q, y, 16, c=c, fill=c, idp=i), pop(a, i, d + 0.1 * q), sh(a, i, 0, -200, d + 0.3 + 0.2 * q, 1.2)]
    return E


def man(a, x, y, k=1.4, d=0.0, arms="down"):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 6, "hz": 1.6}]


def lock(a, x, y, d=0.0, broken=True):
    i, j = uid("lk"), uid("ls")
    E = [R(a, x - 80, y - 60, 160, 130, c="ink", fill="gold", idp=i), pop(a, i, d),
         P(a, f"M{x - 50},{y - 60} L{x - 50},{y - 130} Q{x},{y - 190} {x + 50},{y - 130} L{x + 50},{y - 90}", c="ink", w=10, idp=j), pop(a, j, d + 0.1)]
    if broken:
        E.append(rot(a, j, 40, (x - 50, y - 60), d + 0.5, 0.5))
    return E


def shop(a, x, y, k=1.0, d=0.0, c="ink"):
    i = uid("sh")
    E = [R(a, x - 120 * k, y - 160 * k, 240 * k, 160 * k, c=c, fill="paper", idp=i),
         P(a, f"M{x - 140 * k},{y - 160 * k} L{x},{y - 240 * k} L{x + 140 * k},{y - 160 * k}", c=c, w=6, idp=i),
         R(a, x - 30 * k, y - 80 * k, 60 * k, 80 * k, c=c, fill="blue", idp=i), pop(a, i, d), bob(a, i, 4, 1.0)]
    return E


# ---------- boards ----------
bd(0, fridge(0, 650, 900, 1.2, 0.0, mood="o", hot=True), big(0, 1350, 400, "50 °C", c="red", d=0.2, s=160), thermo(0, 1350, 900, 0.3))
bd(0.5, [shop(0.5, 350 + 400 * q, 900, 1.0, 0.1 * q) for q in range(4)], t(0.5, 960, 300, 70, "HACKED", c="red", d=0.4), ic(0.5, "computer", 960, 520, 140, 0.5, mv="wig"))
bd(1, big(1, 960, 350, "50 °C", c="red", d=0.0, s=150), ic(1, "sun", 450, 700, 180, 0.2, mv="spin", c="gold"), ic(1, "car", 1400, 750, 220, 0.3, mv="wig"))
bd(1.5, ic(1.5, "car", 700, 650, 300, 0.0, mv="wig"), ic(1.5, "sun", 700, 300, 150, 0.1, mv="spin", c="gold"), fridge(1.5, 1350, 900, 0.9, 0.3, hot=True), t(1.5, 1050, 950, 60, "even hotter", c="red", d=0.5))
bd(2, t(2, 960, 230, 56, "According to AP", c="muted", d=0.0), big(2, 960, 420, "~700", c="red", d=0.1, s=160), [shop(2, 500 + 300 * q, 900, 0.7, 0.2 + 0.1 * q, c="red") for q in range(4)])
bd(2.5, bar(2.5, 700, 900, 160, 30, "red", 0.1), t(2.5, 780, 950, 50, "700 hit", c="red", d=0.1), bar(2.5, 1050, 900, 160, 430, "muted", 0.3), t(2.5, 1130, 950, 50, "10,000", d=0.3),
   ic(2.5, "map_pin", 400, 500, 160, 0.4, mv="bob", c="blue"))
bd(3, ic(3, "clock", 450, 500, 180, 0.0, mv="spin"), big(3, 1150, 400, "New wave", c="red", d=0.2, s=120), ic(3, "globe", 1150, 750, 180, 0.3, mv="spin"))
bd(3.5, t(3.5, 960, 230, 56, "Reportedly", c="muted", d=0.0), shop(3.5, 600, 800, 1.2, 0.1, c="red"), t(3.5, 600, 900, 56, "Belgium", d=0.2), shop(3.5, 1300, 800, 1.2, 0.3, c="red"),
   t(3.5, 1300, 900, 56, "Ireland", d=0.4), cross(3.5, 960, 600, d=0.6))
bd(4, big(4, 1150, 360, "Brain teaser", c="red", d=0.0, s=120), ic(4, "question", 450, 450, 260, 0.2, mv="wig", c="red"), fridge(4, 1300, 950, 0.7, 0.3, mood="o"))
bd(4.5, fridge(4.5, 500, 900, 0.9, 0.0), arr(4.5, 750, 650, 1100, 650, c="red", d=0.3), fridge(4.5, 1400, 900, 0.9, 0.4, hot=True, mood="o"), t(4.5, 960, 250, 70, "fridge to oven?", c="red", d=0.5))
bd(5, fridge(5, 700, 950, 1.5, 0.0), t(5, 1400, 400, 90, "Frosty", c="blue", d=0.2), star(5, 1400, 600, 0.4, r=40))
bd(5.5, fridge(5.5, 600, 950, 1.2, 0.0), shop(5.5, 1350, 850, 1.3, 0.2), t(5.5, 1350, 400, 64, "supermarket fridge", c="blue", d=0.3), heat(5.5, 650, 600, 3, 300, 0, 0.4, c="blue"))
bd(6, big(6, 960, 330, "Twist one", c="red", d=0.0, s=140), fridge(6, 500, 950, 0.8, 0.2), cross(6, 1400, 650, d=0.5), t(6, 1400, 850, 60, "no cold made", d=0.4))
bd(7, ic(7, "magnifier", 500, 500, 200, 0.0, mv="wig"), t(7, 1200, 400, 80, "\"cold\" stuff?", d=0.2), cross(7, 1200, 650, d=0.5))
bd(7.5, thermo(7.5, 600, 800, 0.0, up=True), thermo(7.5, 900, 800, 0.2, up=False), big(7.5, 1400, 400, "only heat", c="red", d=0.3, s=110), heat(7.5, 1300, 700, 4, 0, -80, 0.4))
bd(9, fridge(9, 700, 950, 1.1, 0.0), heat(9, 700, 650, 5, 600, 0, 0.2), t(9, 1450, 300, 64, "inside to outside", c="red", d=0.3))
bd(9.5, R(9.5, 400, 300, 500, 600, c="blue", sw=7), heat(9.5, 650, 600, 5, 800, 0, 0.0), arr(9.5, 950, 600, 1400, 600, c="red", d=0.3), ic(9.5, "wind", 1550, 600, 150, 0.5, mv="wig"))
bd(10, bouncer(10, 700, 900, 1.8, 0.0), t(10, 1400, 350, 80, "the bouncer", c="blue", d=0.2), star(10, 1400, 550, 0.4, r=36))
bd(10.5, bouncer(10.5, 650, 900, 1.6, 0.0), door(10.5, 1300, 900, 0.1), heat(10.5, 800, 600, 5, 550, 50, 0.3), t(10.5, 1300, 450, 56, "back door", c="red", d=0.5))
bd(11, man(11, 500, 900, 1.7, 0.0, arms="up"), fridge(11, 1050, 950, 1.1, 0.1), ic(11, "question", 1550, 450, 150, 0.3, mv="wig", c="red"))
bd(11.5, coils(11.5, 960, 300, 0.0), heat(11.5, 1000, 600, 4, 450, -100, 0.2), big(11.5, 1450, 300, "warm!", c="red", d=0.3, s=120), man(11.5, 450, 900, 1.5, 0.1, arms="up"))
bd(13, fridge(13, 600, 950, 1.0, 0.0, mood="o"), t(13, 1350, 400, 70, "How?", d=0.2), ic(13, "question", 1350, 650, 140, 0.3, mv="wig", c="red"))
bd(13.5, loop(13.5, 700, 600, 260, 0.0), big(13.5, 1450, 450, "refrigerant", c="blue", d=0.3, s=90), ic(13.5, "water", 1450, 700, 150, 0.4, mv="wig", c="blue"))
bd(14, R(14, 400, 300, 500, 600, c="blue", sw=7), drops(14, 600, 750, 4, 0.1), heat(14, 1300, 600, 4, -500, 0, 0.2), t(14, 1450, 300, 60, "boils off", c="blue", d=0.3))
bd(14.5, R(14.5, 400, 300, 500, 600, c="blue", sw=7), heat(14.5, 1250, 600, 5, -550, 0, 0.0), big(14.5, 1450, 400, "soaks heat", c="blue", d=0.3, s=90), thermo(14.5, 650, 800, 0.4, up=False))
bd(15, man(15, 700, 900, 1.8, 0.0), drops(15, 600, 500, 4, 0.2), t(15, 1350, 350, 70, "Like sweat", d=0.2))
bd(15.5, man(15.5, 650, 900, 1.8, 0.0), drops(15.5, 550, 500, 4, 0.0, c="blue"), big(15.5, 1350, 450, "cool down", c="blue", d=0.3, s=110), ic(15.5, "wind", 1350, 750, 140, 0.4, mv="wig"))
bd(16, ic(16, "engine", 600, 550, 240, 0.0, mv="wig"), t(16, 600, 850, 60, "compressor", d=0.2), arr(16, 800, 550, 1150, 550, c="red", d=0.3), coils(16, 1400, 350, 0.4))
bd(16.5, coils(16.5, 700, 300, 0.0), heat(16.5, 750, 500, 5, 700, 0, 0.2), t(16.5, 1400, 300, 64, "dump the heat", c="red", d=0.3))
bd(17, loop(17, 960, 580, 300, 0.0, n=8), t(17, 960, 580, 70, "round and round", c="ink", d=0.3))
bd(17.5, bouncer(17.5, 700, 900, 1.7, 0.0), ic(17.5, "clock", 1350, 450, 180, 0.2, mv="spin"), t(17.5, 1350, 750, 60, "never clocks out", c="blue", d=0.4))
bd(19, big(19, 960, 330, "Twist two", c="red", d=0.0, s=140), bouncer(19, 500, 950, 1.2, 0.2), ic(19, "computer", 1400, 650, 200, 0.3, mv="wig"))
bd(20, [fridge(20, 350 + 280 * q, 950, 0.6, 0.1 * q) for q in range(4)], ic(20, "signal", 1600, 450, 170, 0.4, mv="bob", c="blue"), ic(20, "computer", 1600, 750, 150, 0.5, mv="wig"))
bd(20.5, ic(20.5, "phone", 500, 600, 220, 0.0, mv="wig"), arr(20.5, 650, 600, 1000, 600, c="blue", d=0.2), thermo(20.5, 1200, 850, 0.3), t(20.5, 1450, 400, 60, "remote control", c="blue", d=0.4))
bd(21, t(21, 960, 230, 56, "According to AP", c="muted", d=0.0), big(21, 960, 420, "Danfoss", c="ink", d=0.1, s=130), ic(21, "map_pin", 600, 750, 150, 0.3, mv="bob", c="red"), ic(21, "computer", 1320, 750, 150, 0.4, mv="wig"))
bd(21.5, ic(21.5, "computer", 600, 550, 220, 0.0, mv="wig"), ic(21.5, "clock", 600, 850, 120, 0.2, mv="spin"), big(21.5, 1350, 400, "old, no updates", c="red", d=0.3, s=90), cross(21.5, 1350, 650, d=0.5))
bd(22, lock(22, 700, 650, 0.0), t(22, 1350, 400, 64, "broken lock", c="red", d=0.3), ic(22, "gear", 1350, 700, 130, 0.4, mv="spin"))
bd(22.5, lock(22.5, 600, 650, 0.0), ic(22.5, "globe", 1100, 500, 150, 0.2, mv="spin"), arr(22.5, 1000, 600, 750, 650, c="red", d=0.4), t(22.5, 1350, 850, 60, "slipped in", c="red", d=0.5))
bd(25, fridge(25, 600, 950, 1.0, 0.0, hot=True, mood="o"), big(25, 1350, 400, "50 °C ?", c="red", d=0.2, s=120), ic(25, "question", 1350, 700, 140, 0.3, mv="wig", c="red"))
bd(25.5, big(25.5, 960, 380, "our guess", c="blue", d=0.0, s=140), ic(25.5, "magnifier", 500, 750, 160, 0.2, mv="wig"), ic(25.5, "question", 1420, 750, 160, 0.3, mv="wig", c="red"))
bd(26, fridge(26, 600, 950, 1.1, 0.0), coils(26, 1300, 300, 0.2), t(26, 1300, 750, 64, "heaters inside", c="red", d=0.3))
bd(26.5, ic(26.5, "water", 600, 600, 200, 0.0, mv="wig", c="blue"), drops(26.5, 550, 800, 4, 0.2), big(26.5, 1350, 450, "melt frost", c="blue", d=0.3, s=110))
bd(27, bouncer(27, 550, 900, 1.5, 0.0), cross(27, 550, 500, d=0.3), coils(27, 1200, 300, 0.2), ic(27, "flame", 1200, 750, 150, 0.4, mv="wig", c="red"))
bd(27.5, fridge(27.5, 700, 950, 1.3, 0.0, hot=True, mood="sad"), big(27.5, 1450, 400, "a small oven", c="red", d=0.3, s=100), thermo(27.5, 1450, 900, 0.4))
bd(28, t(28, 960, 230, 56, "Reportedly", c="muted", d=0.0), shop(28, 700, 800, 1.5, 0.1, c="red"), ic(28, "flame", 700, 450, 160, 0.3, mv="wig", c="red"), ic(28, "flame", 900, 500, 120, 0.4, mv="wig", c="red"))
bd(28.5, ic(28.5, "magnifier", 700, 550, 240, 0.0, mv="wig"), t(28.5, 1350, 450, 64, "under investigation", d=0.2), ic(28.5, "question", 1350, 700, 140, 0.3, mv="wig", c="red"))
bd(29, big(29, 960, 330, "Twist three", c="red", d=0.0, s=140), fridge(29, 500, 950, 0.7, 0.2, hot=True), germs(29, 1250, 650, 4, 0.3))
bd(29.5, germs(29.5, 500, 450, 8, 0.0), big(29.5, 1450, 500, "bacteria", c="green", d=0.3, s=120))
bd(30, t(30, 960, 230, 56, "USDA", c="muted", d=0.0), thermo(30, 500, 850, 0.1), big(30, 1200, 450, "4–60 °C", c="red", d=0.2, s=130), t(30, 1200, 650, 70, "danger zone", c="red", d=0.4),
   germs(30, 1000, 850, 4, 0.5, party=True))
bd(31, ic(31, "clock", 600, 550, 220, 0.0, mv="spin"), big(31, 1350, 400, "20 min", c="red", d=0.2, s=130), germs(31, 1150, 700, 2, 0.4))
bd(31.5, germs(31.5, 400, 500, 1, 0.0), arr(31.5, 520, 500, 700, 500, c="ink", d=0.2), germs(31.5, 800, 500, 2, 0.3), big(31.5, 1450, 450, "x2", c="red", d=0.5, s=160))
bd(32, germs(32, 400, 400, 1, 0.0), germs(32, 650, 400, 2, 0.2), germs(32, 1000, 400, 4, 0.4), germs(32, 500, 700, 8, 0.6, step=0.05))
bd(32.5, bar(32.5, 400, 950, 100, 20, "green", 0.0), bar(32.5, 600, 950, 100, 60, "green", 0.2), bar(32.5, 800, 950, 100, 160, "green", 0.4), bar(32.5, 1000, 950, 100, 450, "red", 0.6),
   big(32.5, 1450, 400, "astronomical", c="red", d=0.7, s=90))
bd(34, fridge(34, 600, 950, 1.0, 0.0, hot=True, mood="sad"), germs(34, 1100, 450, 8, 0.2, step=0.06, party=True), t(34, 1250, 850, 60, "meat, milk", d=0.4))
bd(34.5, R(34.5, 800, 450, 320, 400, c="ink", sw=7), germs(34.5, 820, 550, 4, 0.0), arr(34.5, 600, 300, 900, 500, c="red", d=0.3), big(34.5, 1450, 450, "thrown out", c="red", d=0.4, s=100), cross(34.5, 960, 650, d=0.6))
bd(35, fridge(35, 600, 950, 1.1, 0.0), germs(35, 1150, 500, 4, 0.2), cross(35, 1300, 750, d=0.4), t(35, 1300, 300, 64, "cold doesn't kill", d=0.3))
bd(35.5, germs(35.5, 500, 500, 4, 0.0, step=0.2), t(35.5, 1350, 450, 90, "Zzz", c="blue", d=0.3), ic(35.5, "moon", 1350, 700, 160, 0.4, mv="bob"))
bd(37, bouncer(37, 600, 900, 1.6, 0.0), ic(37, "clock", 1350, 500, 180, 0.2, mv="spin"), t(37, 1350, 800, 60, "off duty", c="red", d=0.4))
bd(37.5, germs(37.5, 450, 400, 8, 0.0, step=0.06, party=True), big(37.5, 1450, 450, "PARTY", c="green", d=0.3, s=130), star(37.5, 1450, 700, 0.5, r=40), star(37.5, 1250, 750, 0.7, r=26))
bd(38, big(38, 960, 330, "Fine print", c="blue", d=0.0, s=130), t(38, 960, 520, 56, "700 stores, 50 °C: news reports", d=0.2), ic(38, "magnifier", 500, 780, 150, 0.3, mv="wig"), shop(38, 1420, 850, 0.8, 0.4))
bd(38.5, big(38.5, 960, 350, "heaters on?", c="ink", d=0.0, s=110), t(38.5, 960, 550, 64, "our guess", c="muted", d=0.2), coils(38.5, 450, 600, 0.3), ic(38.5, "question", 1420, 750, 150, 0.4, mv="wig", c="red"))
bd(39, ic(39, "building", 500, 600, 240, 0.0, mv="bob"), t(39, 1250, 400, 64, "food supply", d=0.2), check(39, 1250, 620, d=0.4), t(39, 1250, 850, 56, "never at risk", c="green", d=0.5))
bd(41, fridge(41, 600, 950, 1.0, 0.0, hot=True, mood="o"), ic(41, "question", 1350, 400, 180, 0.2, mv="wig", c="red"), t(41, 1350, 650, 64, "fridge to oven?", c="red", d=0.3))
bd(41.5, fridge(41.5, 600, 950, 1.0, 0.0), heat(41.5, 650, 650, 5, 650, 0, 0.2), big(41.5, 1450, 300, "moves heat", c="red", d=0.4, s=100))
bd(42, fridge(42, 600, 950, 1.1, 0.0), cross(42, 600, 600, d=0.3), t(42, 1350, 450, 70, "cold was never here", c="blue", d=0.4))
bd(42.5, bouncer(42.5, 600, 900, 1.6, 0.0), door(42.5, 1250, 900, 0.1), heat(42.5, 750, 600, 5, 500, 50, 0.3), big(42.5, 1250, 330, "shown the door", c="red", d=0.6, s=90))

bd(12, fridge(12, 600, 950, 1.1, 0.0), heat(12, 650, 650, 5, 650, 0, 0.2), t(12, 1400, 300, 64, "heats your kitchen", c="red", d=0.3))
bd(12.5, bar(12.5, 650, 900, 150, 200, "blue", 0.0), t(12.5, 725, 950, 48, "food heat", d=0.0), bar(12.5, 850, 900, 150, 120, "gold", 0.3), t(12.5, 925, 950, 48, "motor", d=0.3), big(12.5, 1350, 400, "= more heat out", c="red", d=0.5, s=80), ic(12.5, "engine", 1350, 700, 150, 0.6, mv="wig"))
bd(18, door(18, 700, 900, 0.0), man(18, 1250, 900, 1.6, 0.2, arms="up"), drops(18, 850, 600, 3, 0.3), t(18, 1300, 300, 64, "cool the kitchen?", d=0.3))
bd(18.5, fridge(18.5, 550, 950, 1.0, 0.0, mood="sad"), thermo(18.5, 1100, 900, 0.2), big(18.5, 1450, 400, "warmer!", c="red", d=0.4, s=120), heat(18.5, 650, 650, 4, 350, -80, 0.3))
bd(24, fridge(24, 600, 950, 1.0, 0.0, mood="o"), ic(24, "globe", 1100, 450, 160, 0.2, mv="spin"), ic(24, "question", 1450, 650, 150, 0.3, mv="wig", c="red"), t(24, 1300, 250, 60, "online?", d=0.2))
bd(24.5, ic(24.5, "computer", 500, 550, 240, 0.0, mv="wig"), [shop(24.5, 1000 + 250 * (q % 3), 550 + 300 * (q // 3), 0.6, 0.1 + 0.08 * q) for q in range(6)], arr(24.5, 700, 550, 880, 550, c="blue", d=0.4), t(24.5, 1250, 250, 60, "hundreds of stores", c="blue", d=0.5))
bd(33, ic(33, "clock", 550, 550, 220, 0.0, mv="spin"), big(33, 1300, 400, "20 min = x2", c="red", d=0.2, s=110), germs(33, 1100, 700, 4, 0.4, step=0.08))
bd(33.5, big(33.5, 960, 380, "72 doublings", c="red", d=0.0, s=130), t(33.5, 960, 560, 60, "on paper", c="muted", d=0.2), germs(33.5, 650, 750, 8, 0.3, step=0.05, party=True))
bd(36, R(36, 500, 400, 360, 300, c="blue", sw=7), germs(36, 530, 500, 4, 0.0, step=0.15), thermo(36, 1150, 850, 0.2), t(36, 1450, 350, 64, "thawed", c="red", d=0.4))
bd(36.5, germs(36.5, 450, 450, 8, 0.0, step=0.06, party=True), big(36.5, 1450, 400, "awake!", c="green", d=0.3, s=130), ic(36.5, "sun", 1450, 700, 150, 0.4, mv="spin", c="gold"))

bd(8, [O(8, 450 + 120 * (q % 3), 450 + 120 * (q // 3), 30, c="blue", fill="blue", idp="mc%d" % q) for q in range(6)], [wig(8, "mc%d" % q, (450 + 120 * (q % 3), 480 + 120 * (q // 3)), 3, 0.8) for q in range(6)], t(8, 570, 850, 60, "cold = slow", c="blue", d=0.2), ic(8, "molecule", 1400, 550, 200, 0.3, mv="spin"))
bd(8.5, [O(8.5, 1150 + 120 * (q % 3), 450 + 120 * (q // 3), 30, c="red", fill="red", idp="mh%d" % q) for q in range(6)], [wig(8.5, "mh%d" % q, (1150 + 120 * (q % 3), 480 + 120 * (q // 3)), 25, 5.0) for q in range(6)], t(8.5, 1270, 850, 60, "heat = fast", c="red", d=0.2), thermo(8.5, 550, 850, 0.3))
bd(23, door(23, 700, 900, 0.0, open_=False), R(23, 560, 900, 280, 40, c="ink", fill="gold"), ic(23, "magnet", 1300, 500, 170, 0.2, mv="wig"), t(23, 1300, 800, 60, "key under the mat", d=0.3))
bd(23.5, ic(23.5, "globe", 600, 550, 240, 0.0, mv="spin"), ic(23.5, "map_pin", 1300, 500, 200, 0.2, mv="bob", c="red"), arr(23.5, 800, 550, 1150, 520, c="red", d=0.3), t(23.5, 1300, 800, 60, "address online", c="red", d=0.4))
bd(40, t(40, 960, 230, 56, "According to AP", c="muted", d=0.0), ic(40, "computer", 600, 600, 220, 0.1, mv="wig"), ic(40, "gear", 1300, 550, 200, 0.2, mv="spin"), t(40, 1300, 850, 60, "update it", c="green", d=0.3))
bd(40.5, R(40.5, 900, 300, 120, 600, c="red", fill="red"), ic(40.5, "flame", 960, 250, 120, 0.1, mv="wig", c="red"), fridge(40.5, 1400, 950, 0.9, 0.2), heat(40.5, 450, 600, 4, 380, 0, 0.3, c="ink"), check(40.5, 1400, 300, d=0.8), t(40.5, 500, 950, 56, "firewall", c="red", d=0.4))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"USDA": "U S D A", "AP": "A P", "Danfoss": "Dan fosse"})
