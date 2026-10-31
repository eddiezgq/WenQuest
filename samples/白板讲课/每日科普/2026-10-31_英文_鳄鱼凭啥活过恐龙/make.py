"""Daily science short 2026-10-31 (English): "How Did Crocodiles Outlive T. rex?"
News: UCL-led study, Science Advances 12(43), 2026: "Climatic niche conservatism shapes the macroevolution, extinction, and survivorship of
crocodile-line archosaurs" (Chiarenza, Howard, Varnham, Farnsworth, Valdes, Mannion).
Trending: ScienceDaily "Top Science" Oct 30, 2026 (#5): "The Asteroid Killed the Dinosaurs. Why Did Crocodiles Survive?"
Facts used (https://www.sciencedaily.com/releases/2026/10/261030002922.htm):
- 7,000+ fossils and records, 400+ living and extinct species; climate + geography models over 245 million years.
- Crocodile-line animals tracked warm climates: spread poleward when hot, retreated to tropics when cool; ~50 Myr ago Earth ~10 °C warmer,
  crocodile relatives at high latitudes incl. Antarctica.
- After the impact: simulations with 5% or 10% less sunlight kept equatorial regions suitable; 15% made them unsuitable, judged unlikely.
- Same team's earlier modeling: non-avian dinosaur habitats contracted much more.
- Other likely factors: small body size, partly aquatic, flexible diets, low energy needs as ectotherms.
- Chiarenza: "The asteroid did not make the whole planet equally hostile to every group." Mannion: roads, farms and cities make moving harder.
General knowledge: Chicxulub impact 66 Myr ago, ~10 km asteroid, ~3/4 of species lost (standard textbook figures).
Analogies: "solar-powered robot" for cold-blooded, "favorite blanket" joke, "seat next to the heater" are our analogies.
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig, bubbles, waves)
from popkit import cute_croc, cute_bot  # noqa: E402

S = [
 ("小行星灭了霸王龙。|鳄鱼呢，基本上只是搬了个家。", "The asteroid wiped out T. rex. | The crocodile basically just moved."),
 ("六千六百万年前，一块十公里宽的石头|砸进了墨西哥。", "Sixty six million years ago, a rock ten kilometers wide | slammed into Mexico."),
 ("大约四分之三的物种消失了，|包括所有不会飞的恐龙。", "About three quarters of all species vanished, | including every dinosaur that could not fly."),
 ("可鳄鱼挺过来了。|它们的家族今天还在。", "But crocodiles made it. | Their family is still here today."),
 ("它们当年可野了：|披甲的素食者、陆地猎手、一吨多重的巨兽。", "And their family used to be wild: | armored plant eaters, land hunters, giants over a ton."),
 ("有一种叫帝鳄，|能长到十二米长。", "One called Sarcosuchus | could grow up to twelve meters long."),
 ("今天的烧脑问题：|一只冷血爬行动物，凭什么活过霸王龙？", "Today's brain teaser: | how does a cold blooded reptile outlive T. rex?"),
 ("伦敦大学学院牵头的一项新研究，|专门去找答案。", "A new study led by University College London | went looking for the answer."),
 ("他们翻了七千多条化石和记录，|覆盖四百多个物种。", "They dug through more than seven thousand fossils and records | from over four hundred species."),
 ("再用气候模型，|重建了两亿四千五百万年的气候。", "Then they used climate models | to rebuild two hundred forty five million years of weather."),
 ("结论一句话：|鳄鱼追着热走。", "Their finding, in one sentence: | crocodiles follow the heat."),
 ("把鳄鱼想成一台太阳能机器人：|没太阳，就没电。", "Think of a croc as a solar powered robot. | No sun, no power."),
 ("地球一热，|鳄鱼的亲戚就往两极扩张。", "When Earth got hot, | crocodile relatives spread toward the poles."),
 ("五千万年前，地球比现在热大约十度，|南极洲都有鳄鱼的亲戚。", "Fifty million years ago, Earth was about ten degrees warmer. | Crocodile relatives lived in Antarctica."),
 ("地球一冷，|它们就退回热带。", "When Earth cooled, | they retreated to the tropics."),
 ("反转一：它们多半不是改变自己去适应，|而是换个地址。", "Twist one: mostly, they did not change to fit the climate. | They changed address."),
 ("科学家管这叫气候生态位保守。|我管这叫：永远不离开最爱的那条毯子。", "Scientists call it climatic niche conservatism. | I call it never leaving your favorite blanket."),
 ("现在说小行星。|尘埃和烟灰挡住了阳光。", "Now, the asteroid. | Dust and soot blocked the sunlight."),
 ("地球变暗，|也变冷了。", "The planet got darker | and colder."),
 ("团队做了模拟：|阳光少百分之五，或者少百分之十。", "The team ran simulations | with five or ten percent less sunlight."),
 ("赤道附近，仍然暖和到|鳄鱼能活。", "Near the equator, it stayed warm enough | for crocodiles."),
 ("反转二，最狡猾：|它们本来就站在对的位置。", "Twist two, the sneaky one: | they were already in the right place."),
 ("第一作者说，小行星并没有让整个地球|对每个物种都一样凶。", "As the lead author puts it, the asteroid did not make the whole planet | equally hostile to everyone."),
 ("团队之前的模拟显示，|恐龙的栖息地缩得多得多。", "The team's earlier modeling showed | dinosaur habitats shrank far more."),
 ("只有阳光少到百分之十五，|热带避难所才会失守。", "Only with fifteen percent less sunlight | would the tropical refuge fail."),
 ("研究者认为，|那种极端情况不太可能。", "The researchers think that extreme case | is unlikely."),
 ("鳄鱼还有别的招：|个头小，半泡在水里，什么都吃。", "Crocs had other tricks too: | small bodies, a life half in water, and they eat almost anything."),
 ("冷血也帮了忙：|耗能低，饿得起。", "Being cold blooded helped as well. | Low energy needs, so they can wait out hunger."),
 ("黑暗的世界里，饿肚子的霸王龙麻烦大了。|鳄鱼可以等。", "In a dark world, a hungry T. rex was in big trouble. | A croc could wait."),
 ("反转三，跟今天有关：|鳄鱼应对气候变化，靠的是搬家。", "Twist three, and it is about today: | crocodiles handle climate change by moving."),
 ("可现在，路、农田和城市|挡在路上。", "But now there are roads, farms and cities | in the way."),
 ("团队说，鳄鱼需要|能搬家的空间。", "The team says crocodiles need room | to move."),
 ("它们的祖先能走到南极洲，|今天的鳄鱼却连一条高速都过不去。", "Their ancestors walked all the way to Antarctica. | Today's crocs can barely cross a highway."),
 ("两亿多年的教训：|活下来，有时候就是能搬家。", "The lesson of two hundred million years: | sometimes survival just means being able to move."),
 ("友情提示：这是对远古的模型，|靠化石和模拟拼出来的。", "Fine print: this is a model of the deep past, | pieced together from fossils and simulations."),
 ("个头、食性、水，|也都很重要，不只是气候。", "Body size, diet and water | mattered too, not just climate."),
 ("所以，鳄鱼凭什么活过霸王龙？|它一直坐在离暖气最近的位置。", "So how did crocodiles outlive T. rex? | They always had the seat closest to the heater."),
 ("小行星终结了恐龙时代。|鳄鱼呢，只是没离开暖气。", "The asteroid ended the age of dinosaurs. | The crocodile just never left the heater."),
]
TITLE = {"zh": "鳄鱼凭啥活过霸王龙？", "en": "How Did Crocodiles Outlive T. rex?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += [p] if isinstance(p, dict) else p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    B.append(E)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def croc(a, x, y, k=1.0, d=0.0, mood="happy", walk=0, wd=0.4):
    i = uid("cr")
    E = cute_croc(x, y, k, a, idp=i, mood=mood) + [pop(a, [i + "_b", i + "_t", i + "_j"], d)]
    if walk:
        E.append(sh(a, [i + "_b", i + "_t", i + "_j"], walk, 0, d + wd, 1.4))
    return E


def rock(a, x, y, d=0.0, dx=500, dy=400, r=60):
    """The asteroid: a lumpy rock with a fire trail, flying down-right."""
    i = uid("rk")
    E = [P(a, f"M{x - r},{y} Q{x - r},{y - r} {x},{y - r} Q{x + r * 1.1},{y - r * 0.9} {x + r},{y} Q{x + r * 0.9},{y + r} {x},{y + r} Q{x - r * 1.1},{y + r * 0.8} {x - r},{y} Z",
           c="ink", w=5, fill="muted", idp=i),
         P(a, f"M{x - r * 0.7},{y - r * 0.7} L{x - r * 3},{y - r * 2.6} M{x - r},{y - r * 0.2} L{x - r * 3.2},{y - r * 1.8} M{x - r * 0.2},{y - r} L{x - r * 2.2},{y - r * 3}",
           c="red", w=7, idp=i),
         pop(a, i, d), spin(a, i, (x, y), 30), sh(a, i, dx, dy, d + 0.3, 1.2)]
    return E


def boom(a, x, y, d=0.0, c="gold", r=90):
    import math
    i = uid("bm")
    pts = []
    for q in range(16):
        rr = r if q % 2 == 0 else r * 0.45
        ang = math.pi * q / 8
        pts.append(f"{x + rr * math.cos(ang):.0f},{y + rr * math.sin(ang):.0f}")
    return [P(a, "M" + " L".join(pts) + " Z", c="red", w=5, fill=c, idp=i), pop(a, i, d), pulse(a, i, d + 0.4), spin(a, i, (x, y), 20)]


def dino(a, x, y, s=220, d=0.0, fall=None):
    i = uid("dn")
    E = [{"t": "icon", "at": a, "id": i, "name": "dinosaur", "x": x, "y": y, "size": s, "c": "red"}, pop(a, i, d), wig(a, i, (x, y + s / 2), 5, 1.8)]
    if fall is not None:
        E.append(rot(a, i, 90, (x, y + s / 2), fall, 0.6))
    return E


def sun(a, x, y, s=180, d=0.0, dim=False):
    i = uid("sn")
    E = [{"t": "icon", "at": a, "id": i, "name": "sun", "x": x, "y": y, "size": s, "c": "muted" if dim else "gold"}, pop(a, i, d), spin(a, i, (x, y), 15)]
    return E


def earth(a, x, y, r=200, d=0.0, warm=True, band=None):
    """Globe with a warm equator band (band = 'wide' | 'narrow' | None)."""
    i, j = uid("ea"), uid("eb")
    E = [O(a, x, y, r, c="blue", fill="paper", idp=i, sw=6), P(a, f"M{x - r},{y} L{x + r},{y}", c="muted", w=3, idp=i), pop(a, i, d)]
    if band:
        h = r * (0.8 if band == "wide" else 0.3)
        w = (r * r - (h / 2) ** 2) ** 0.5
        E += [R(a, x - w, y - h / 2, 2 * w, h, c="red", fill="red", idp=j, sw=2),
              {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y], "dur": 0.8, "delay": d + 0.3}, pulse(a, j, d + 1.2)]
    E.append(spin(a, i, (x, y), 8))
    return E


def dust(a, n=6, d=0.0, y=260):
    E = []
    for q in range(n):
        j = uid("du")
        x = 250 + 280 * q
        E += [P(a, f"M{x - 90},{y} Q{x - 60},{y - 70} {x},{y - 50} Q{x + 60},{y - 90} {x + 100},{y - 20} Q{x + 120},{y + 40} {x},{y + 30} Q{x - 100},{y + 50} {x - 90},{y} Z",
                c="ink", w=4, fill="muted", idp=j), pop(a, j, d + 0.08 * q), sh(a, j, 40, 0, d + 0.3, 2.0)]
    return E


def thermo(a, x, y, d=0.0, drop=True):
    i, j = uid("th"), uid("tl")
    E = [R(a, x - 25, y - 250, 50, 250, c="ink", fill="paper", idp=i), O(a, x, y + 20, 45, c="ink", fill="red", idp=i),
         R(a, x - 12, y - 220, 24, 230, c="red", fill="red", idp=j), pop(a, [i, j], d)]
    E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y + 10], "dur": 1.0, "delay": d + 0.4, **({"from": 1.0, "to": 0.3} if drop else {})})
    return E


def snow(a, n=5, d=0.0):
    E = []
    for q in range(n):
        j = uid("sw")
        x, y = 300 + 330 * q, 200 + 40 * (q % 2)
        E += [P(a, f"M{x - 20},{y} L{x + 20},{y} M{x},{y - 20} L{x},{y + 20}", c="blue", w=5, idp=j), pop(a, j, d + 0.1 * q), sh(a, j, 20, 300, d + 0.2, 2.5), spin(a, j, (x, y), 40)]
    return E


def road(a, y=820, d=0.0):
    i = uid("rd")
    return [R(a, 1050, y - 60, 700, 120, c="ink", fill="muted", idp=i), P(a, f"M1080,{y} L1720,{y}", c="paper", w=8, idp=i, strokeDash="dashed"), pop(a, i, d)]


def car_go(a, x, y, d=0.0):
    i = uid("cg")
    return [{"t": "icon", "at": a, "id": i, "name": "car", "x": x, "y": y, "size": 120, "c": "blue"}, pop(a, i, d), sh(a, i, 600, 0, d + 0.2, 2.0)]


def paper(a, x, y, d=0.0, label="Science Advances"):
    i = uid("pa")
    return [R(a, x - 200, y - 250, 400, 500, c="ink", fill="paper", idp=i), pop(a, i, d), wig(a, i, (x, y + 250), 3, 1.2)] + T(a, x, y - 170, 40, label, c="blue", d=d + 0.2) + \
        [P(a, f"M{x - 140},{y - 80 + 60 * q} L{x + 140},{y - 80 + 60 * q}", c="muted", w=5) for q in range(4)]


def bones(a, x, y, n=6, d=0.0):
    E = []
    for q in range(n):
        j = uid("bo")
        bx = x + 110 * q
        E += [P(a, f"M{bx - 35},{y} L{bx + 35},{y} M{bx - 45},{y - 12} L{bx - 35},{y} L{bx - 45},{y + 12} M{bx + 45},{y - 12} L{bx + 35},{y} L{bx + 45},{y + 12}", c="ink", w=6, idp=j),
              pop(a, j, d + 0.06 * q), rot(a, j, 25 * (q % 2 * 2 - 1), (bx, y), d + 0.5, 0.6)]
    return E


def blanket(a, x, y, d=0.0):
    i = uid("bk")
    return [P(a, f"M{x - 220},{y} Q{x - 110},{y - 40} {x},{y} Q{x + 110},{y + 40} {x + 220},{y} L{x + 220},{y + 120} Q{x + 110},{y + 160} {x},{y + 120} Q{x - 110},{y + 80} {x - 220},{y + 120} Z",
              c="ink", w=5, fill="gold", idp=i), pop(a, i, d), wig(a, i, (x, y + 60), 3, 1.0)]


def heater(a, x, y, d=0.0):
    i, w = uid("ht"), uid("hw")
    E = [R(a, x - 90, y - 160, 180, 160, c="ink", fill="red", idp=i)] + [P(a, f"M{x - 60 + 30 * q},{y - 140} L{x - 60 + 30 * q},{y - 20}", c="ink", w=4, idp=i) for q in range(5)]
    E += [P(a, f"M{x - 50},{y - 190} Q{x - 30},{y - 230} {x - 50},{y - 270} M{x},{y - 190} Q{x + 20},{y - 230} {x},{y - 270} M{x + 50},{y - 190} Q{x + 70},{y - 230} {x + 50},{y - 270}",
            c="red", w=5, idp=w), pop(a, i, d), pop(a, w, d + 0.2), wig(a, w, (x, y - 190), 6, 2.5)]
    return E


ROBO = [0]


def robot(a, x, y, k=0.8, d=0.0, mood="happy"):
    i = uid("rb")
    return cute_bot(x, y, k, a, idp=i, mood=mood) + [pop(a, i + "_b", d)]


# ---------- boards ----------
bd(0, rock(0, 400, 200, 0.0, 500, 450), dino(0, 1300, 520, 300, 0.0, fall=1.2), boom(0, 960, 700, 1.4, r=110), BIG(0, 1450, 250, "T. rex: gone", c="red", d=0.3, s=90))
bd(0.5, croc(0.5, 700, 760, 1.2, 0.0, walk=500), BIG(0.5, 1300, 300, "just... moved", c="green", d=0.3, s=100), ic(0.5, "map_pin", 1600, 600, 140, 0.5, mv="bob", c="red"))
bd(1, BIG(1, 1350, 280, "66,000,000", c="red", d=0.0, s=110), T(1, 1350, 420, 56, "years ago", c="ink", d=0.2), rock(1, 300, 200, 0.2, 400, 350), ic(1, "clock", 1350, 650, 150, 0.4, mv="spin"))
bd(1.5, rock(1.5, 500, 150, 0.0, 400, 450), boom(1.5, 960, 650, 1.3, r=130), BIG(1.5, 1450, 300, "10 km", c="red", d=0.2, s=130), T(1.5, 1450, 450, 56, "Mexico", c="ink", d=0.5))
bd(2, BIG(2, 960, 280, "3/4", c="red", d=0.0, s=170), bones(2, 650, 600, 6, 0.3), cross(2, 1500, 450, d=0.6))
bd(2.5, dino(2.5, 500, 500, 260, 0.0, fall=0.9), dino(2.5, 950, 520, 220, 0.1, fall=1.1), ic(2.5, "rocket", 1450, 450, 140, 0.3, mv="bob"),
   T(2.5, 1450, 700, 50, "birds flew on", c="blue", d=0.6))
bd(3, croc(3, 800, 760, 1.3, 0.0), check(3, 1450, 400, d=0.3), BIG(3, 1450, 580, "made it", c="green", d=0.4, s=110))
bd(3.5, croc(3.5, 500, 760, 0.8, 0.0), croc(3.5, 1100, 760, 0.6, 0.2), croc(3.5, 1550, 760, 0.45, 0.4), T(3.5, 960, 280, 64, "still here", c="green", d=0.3))
bd(6, BIG(6, 1150, 360, "Brain teaser", c="red", d=0.0, s=120), ic(6, "question", 450, 450, 260, 0.2, mv="wig", c="red"), ic(6, "gear", 1150, 620, 140, 0.4, mv="spin"),
   ic(6, "flame", 1650, 620, 140, 0.5, mv="wig", c="red"))
bd(6.5, croc(6.5, 550, 760, 0.9, 0.0), T(6.5, 960, 600, 120, "vs", c="ink", d=0.3), dino(6.5, 1300, 420, 300, 0.2), ic(6.5, "question", 960, 300, 140, 0.5, mv="wig", c="red"))
bd(7, ic(7, "building", 600, 480, 260, 0.0, mv="bob"), T(7, 1300, 380, 70, "UCL", c="red", d=0.2), ic(7, "magnifier", 1300, 600, 160, 0.4, mv="wig"), croc(7, 1500, 860, 0.5, 0.5))
bd(7.5, ic(7.5, "magnifier", 500, 450, 220, 0.0, mv="wig"), croc(7.5, 1100, 700, 0.8, 0.2), ic(7.5, "question", 1550, 400, 150, 0.4, mv="wig", c="red"))
bd(8, BIG(8, 960, 280, "7,000+", c="red", d=0.0, s=150), bones(8, 650, 560, 6, 0.2), T(8, 960, 720, 56, "fossils & records", c="ink", d=0.5))
bd(8.5, BIG(8.5, 960, 280, "400+ species", c="blue", d=0.0, s=120), croc(8.5, 500, 760, 0.6, 0.2), dino(8.5, 900, 520, 200, 0.3), croc(8.5, 1450, 760, 0.6, 0.4))
bd(9, ic(9, "computer", 600, 500, 260, 0.0, mv="bob"), ic(9, "cloud", 1250, 350, 180, 0.2, mv="bob"), ic(9, "thermometer", 1500, 600, 160, 0.4, mv="wig", c="red"))
bd(9.5, BIG(9.5, 960, 300, "245 million yrs", c="blue", d=0.0, s=110), arr(9.5, 300, 600, 1600, 600, c="blue", d=0.2, w=10), ic(9.5, "clock", 960, 750, 130, 0.4, mv="spin"),
   earth(9.5, 400, 520, 70, 0.3))
bd(10, T(10, 960, 380, 70, "in one sentence:", c="ink", d=0.0), ic(10, "check", 960, 600, 160, 0.3, mv="bob", c="green"), ic(10, "flame", 400, 600, 150, 0.2, mv="wig", c="red"),
   ic(10, "flame", 1520, 600, 150, 0.4, mv="wig", c="red"))
bd(10.5, croc(10.5, 500, 760, 1.0, 0.0, walk=600), sun(10.5, 1500, 350, 220, 0.2), BIG(10.5, 1100, 300, "follow the heat", c="red", d=0.4, s=90))
bd(11, robot(11, 650, 860, 1.0, 0.0), sun(11, 1300, 330, 200, 0.2), arr(11, 1180, 430, 820, 550, c="gold", d=0.4), T(11, 1400, 650, 56, "solar powered", c="gold", d=0.5))
bd(11.5, robot(11.5, 650, 860, 1.0, 0.0, mood="sad"), sun(11.5, 1300, 330, 200, 0.1, dim=True), cross(11.5, 1300, 330, d=0.3), BIG(11.5, 1400, 650, "no power", c="red", d=0.5, s=90))
bd(12, earth(12, 960, 500, 230, 0.0, band="wide"), croc(12, 960, 360, 0.35, 0.3), arr(12, 960, 300, 960, 170, c="red", d=0.6), arr(12, 960, 700, 960, 830, c="red", d=0.6),
   ic(12, "thermometer", 1500, 500, 160, 0.2, mv="wig", c="red"))
bd(12.5, earth(12.5, 700, 500, 230, 0.0, band="wide"), arr(12.5, 700, 260, 700, 160, c="red", d=0.3), arr(12.5, 700, 740, 700, 840, c="red", d=0.3), croc(12.5, 1400, 700, 0.7, 0.2),
   T(12.5, 1400, 350, 56, "toward the poles", c="red", d=0.5))
bd(13, BIG(13, 960, 260, "50 million yrs ago", c="blue", d=0.0, s=90), BIG(13, 600, 520, "+10°C", c="red", d=0.3, s=140), thermo(13, 1350, 650, 0.2, drop=False))
bd(13.5, ic(13.5, "globe", 500, 500, 240, 0.0, mv="spin"), T(13.5, 1200, 330, 70, "Antarctica", c="blue", d=0.2), croc(13.5, 1200, 700, 0.8, 0.3), snow(13.5, 2, 0.5))
bd(14, thermo(14, 500, 650, 0.0, drop=True), snow(14, 5, 0.2), T(14, 1200, 450, 70, "Earth cooled", c="blue", d=0.3))
bd(14.5, earth(14.5, 700, 500, 230, 0.0, band="narrow"), croc(14.5, 1400, 700, 0.7, 0.2, walk=-200), T(14.5, 1400, 350, 64, "back to the tropics", c="red", d=0.4))
bd(15, BIG(15, 960, 380, "Twist 1", c="red", d=0.0, s=150), ic(15, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), croc(15, 1500, 650, 0.6, 0.4))
bd(15.5, croc(15.5, 450, 760, 0.8, 0.0, walk=800), ic(15.5, "map_pin", 1500, 450, 180, 0.2, mv="bob", c="red"), BIG(15.5, 960, 300, "new address", c="green", d=0.4, s=100))
bd(16, T(16, 960, 330, 64, "climatic niche", c="blue", d=0.0), T(16, 960, 440, 64, "conservatism", c="blue", d=0.2), ic(16, "flask", 500, 650, 150, 0.3, mv="wig"),
   ic(16, "thermometer", 1400, 650, 150, 0.4, mv="wig", c="red"))
bd(16.5, blanket(16.5, 900, 640, 0.0), croc(16.5, 900, 660, 0.7, 0.2), T(16.5, 960, 320, 64, "never leave the blanket", c="red", d=0.4))
bd(17, rock(17, 300, 150, 0.0, 500, 400), boom(17, 850, 600, 1.4, r=100), ic(17, "globe", 1450, 550, 200, 0.2, mv="spin"))
bd(17.5, dust(17.5, 6, 0.0), sun(17.5, 960, 560, 200, 0.2, dim=True), cross(17.5, 1300, 560, d=0.6), T(17.5, 960, 760, 56, "sunlight blocked", c="ink", d=0.5))
bd(18, dust(18, 6, 0.0), ic(18, "globe", 960, 560, 260, 0.2, mv="spin"), BIG(18, 1500, 600, "dark", c="ink", d=0.4, s=110))
bd(18.5, thermo(18.5, 600, 700, 0.0, drop=True), snow(18.5, 5, 0.1), BIG(18.5, 1300, 500, "cold", c="blue", d=0.3, s=130))
bd(19, ic(19, "computer", 500, 500, 240, 0.0, mv="bob"), sun(19, 1200, 400, 200, 0.2), BIG(19, 1250, 680, "-5%", c="red", d=0.4, s=110), ic(19, "gear", 1650, 400, 120, 0.3, mv="spin"))
bd(19.5, sun(19.5, 600, 450, 220, 0.0, dim=True), BIG(19.5, 1250, 450, "-10%", c="red", d=0.3, s=140), thermo(19.5, 1650, 700, 0.3, drop=True))
bd(20, earth(20, 700, 500, 250, 0.0, band="narrow"), croc(20, 700, 540, 0.3, 0.6), T(20, 1450, 400, 60, "equator:", c="ink", d=0.3), T(20, 1450, 500, 60, "still warm", c="red", d=0.5))
bd(20.5, croc(20.5, 800, 760, 1.2, 0.0), check(20.5, 1450, 420, d=0.3), sun(20.5, 1450, 650, 150, 0.4))
bd(21, BIG(21, 960, 380, "Twist 2", c="red", d=0.0, s=150), ic(21, "eye", 450, 450, 150, 0.2, mv="wig"), ic(21, "flame", 1470, 450, 150, 0.4, mv="wig", c="red"))
bd(21.5, earth(21.5, 600, 500, 230, 0.0, band="narrow"), croc(21.5, 600, 530, 0.3, 0.3), arr(21.5, 1100, 500, 860, 500, c="green", d=0.5), BIG(21.5, 1450, 500, "right place", c="green", d=0.4, s=100))
bd(22, ic(22, "globe", 500, 500, 240, 0.0, mv="spin"), T(22, 1250, 380, 56, "not equally hostile", c="red", d=0.2), T(22, 1250, 480, 48, "everywhere", c="ink", d=0.4))
bd(22.5, rock(22.5, 300, 150, 0.0, 300, 250), croc(22.5, 1000, 760, 0.8, 0.2), dino(22.5, 1450, 450, 260, 0.3, fall=1.3), T(22.5, 960, 300, 56, "to everyone", c="red", d=0.5))
bd(23, dino(23, 600, 450, 300, 0.0), earth(23, 1350, 520, 220, 0.2, band="wide"), arr(23, 900, 450, 1100, 450, c="blue", d=0.4))
hs = uid("hs")
bd(23.5, [O(23.5, 700, 520, 260, c="red", fill="red", idp=hs), pop(23.5, hs, 0.0),
          {"t": "move", "at": 21.5, "kind": "grow", "targets": [hs], "axis": "x", "pivot": [700, 520], "dur": 1.0, "delay": 0.3, "from": 1.0, "to": 0.2}],
   dino(23.5, 1350, 420, 260, 0.2, fall=1.2), T(23.5, 1350, 780, 56, "habitat shrank", c="red", d=0.5))
bd(24, sun(24, 600, 450, 220, 0.0, dim=True), BIG(24, 1250, 450, "-15%", c="red", d=0.3, s=150), dust(24, 3, 0.4, 230))
bd(24.5, earth(24.5, 700, 500, 230, 0.0, band="narrow"), cross(24.5, 700, 500, d=0.6), croc(24.5, 1400, 700, 0.7, 0.2, mood="sad"), T(24.5, 1400, 350, 56, "refuge fails", c="red", d=0.4))
bd(25, ic(25, "flask", 500, 500, 200, 0.0, mv="wig"), ic(25, "magnifier", 1400, 500, 200, 0.2, mv="wig"), T(25, 960, 300, 60, "that extreme case", c="ink", d=0.3))
bd(25.5, BIG(25.5, 960, 400, "unlikely", c="green", d=0.0, s=140), check(25.5, 960, 600, d=0.3), croc(25.5, 1500, 800, 0.5, 0.4))
bd(26, croc(26, 700, 760, 1.0, 0.0), BIG(26, 1350, 380, "other tricks", c="blue", d=0.2, s=100), ic(26, "gear", 1350, 620, 140, 0.4, mv="spin"))
bd(26.5, croc(26.5, 450, 700, 0.6, 0.0), waves(26.5, 720, 150, 800), bubbles(26.5, 500, 680, 4, 0.2), ic(26.5, "water", 960, 500, 150, 0.3, mv="bob", c="blue"),
   T(26.5, 1450, 400, 50, "small", c="ink", d=0.3), T(26.5, 1450, 500, 50, "in water", c="blue", d=0.5), T(26.5, 1450, 600, 50, "eats anything", c="red", d=0.7))
bd(27, croc(27, 700, 760, 1.0, 0.0), ic(27, "battery", 1350, 500, 180, 0.2, mv="wig", c="green"), T(27, 1350, 700, 56, "low energy", c="green", d=0.4))
bd(27.5, croc(27.5, 700, 760, 1.0, 0.0), ic(27.5, "clock", 1350, 450, 180, 0.2, mv="spin"), BIG(27.5, 1350, 680, "can wait", c="green", d=0.4, s=100))
bd(28, dust(28, 6, 0.0), dino(28, 900, 450, 320, 0.2), ic(28, "question", 1450, 500, 150, 0.4, mv="wig", c="red"), T(28, 900, 820, 56, "hungry...", c="red", d=0.5))
bd(28.5, croc(28.5, 800, 760, 1.2, 0.0), ic(28.5, "clock", 1450, 450, 160, 0.2, mv="spin"), T(28.5, 1450, 680, 64, "zzz...", c="blue", d=0.4))
bd(29, BIG(29, 960, 380, "Twist 3", c="red", d=0.0, s=150), ic(29, "thermometer", 450, 450, 150, 0.2, mv="wig", c="red"), ic(29, "globe", 1470, 450, 150, 0.4, mv="spin"))
bd(29.5, croc(29.5, 450, 760, 0.8, 0.0, walk=700), thermo(29.5, 1600, 600, 0.3, drop=False), T(29.5, 960, 300, 60, "they move", c="green", d=0.4))
bd(30, road(30, 820, 0.0), car_go(30, 1100, 780, 0.2), ic(30, "building", 1400, 450, 220, 0.3, mv="bob"), croc(30, 500, 840, 0.7, 0.4, walk=300, wd=0.6))
bd(30.5, croc(30.5, 600, 760, 0.9, 0.0, mood="sad"), cross(30.5, 1000, 600, d=0.3), ic(30.5, "building", 1450, 500, 250, 0.2, mv="bob"), T(30.5, 960, 300, 60, "in the way", c="red", d=0.4))
bd(31, croc(31, 600, 760, 1.0, 0.0), arr(31, 950, 600, 1600, 600, c="green", d=0.3, w=10), T(31, 1300, 400, 64, "room", c="green", d=0.4))
bd(31.5, croc(31.5, 400, 760, 0.8, 0.0, walk=900), BIG(31.5, 960, 350, "to move", c="green", d=0.3, s=120))
bd(34, BIG(34, 960, 380, "Fine print", c="blue", d=0.0, s=130), ic(34, "ruler", 500, 620, 150, 0.2, mv="wig"), ic(34, "computer", 1400, 620, 150, 0.4, mv="bob"))
bd(34.5, bones(34.5, 450, 600, 4, 0.0), ic(34.5, "computer", 1350, 500, 220, 0.2, mv="bob"), T(34.5, 960, 300, 56, "fossils + simulations", c="ink", d=0.4))
bd(35, croc(35, 450, 760, 0.6, 0.0), waves(35, 700, 800, 1200), ic(35, "water", 1000, 500, 140, 0.2, mv="bob", c="blue"), ic(35, "thermometer", 1500, 500, 140, 0.4, mv="wig", c="red"))
bd(35.5, BIG(35.5, 960, 400, "not just climate", c="red", d=0.0, s=100), check(35.5, 600, 650, d=0.3), check(35.5, 960, 650, d=0.4), check(35.5, 1320, 650, d=0.5))
bd(36, croc(36, 550, 760, 0.9, 0.0), ic(36, "question", 1100, 400, 160, 0.2, mv="wig", c="red"), dino(36, 1450, 450, 240, 0.3, fall=1.0))
bd(36.5, heater(36.5, 1350, 800, 0.0), croc(36.5, 700, 760, 1.0, 0.2, walk=200), BIG(36.5, 960, 280, "closest seat", c="red", d=0.4, s=100))
bd(37, rock(37, 300, 150, 0.0, 400, 350), dino(37, 1100, 450, 300, 0.2, fall=1.2), BIG(37, 1500, 280, "the end", c="red", d=0.5, s=100))
bd(37.5, heater(37.5, 1300, 800, 0.0), croc(37.5, 700, 760, 1.1, 0.1), blanket(37.5, 700, 800, 0.3), BIG(37.5, 960, 280, "cozy.", c="green", d=0.5, s=120))


bd(4, croc(4, 450, 760, 0.7, 0.0), ic(4, "robot_arm", 960, 450, 160, 0.2, mv="wig"), dino(4, 1450, 450, 220, 0.3), T(4, 960, 250, 60, "wild family", c="red", d=0.4))
bd(4.5, croc(4.5, 500, 760, 0.8, 0.0, walk=200), BIG(4.5, 1350, 400, "1 ton+", c="red", d=0.3, s=130), bar(4.5, 1250, 850, 80, 200, "green", 0.5), bar(4.5, 1400, 850, 80, 320, "green", 0.6))
bd(5, croc(5, 550, 700, 1.5, 0.0), T(5, 1400, 300, 64, "Sarcosuchus", c="blue", d=0.3), ic(5, "ruler", 1400, 500, 150, 0.4, mv="wig"))
bd(5.5, croc(5.5, 700, 760, 1.6, 0.0, walk=100), BIG(5.5, 1450, 380, "12 m", c="red", d=0.3, s=160), arr(5.5, 200, 860, 1250, 860, c="blue", d=0.5, w=8))
bd(32, ic(32, "globe", 500, 500, 220, 0.0, mv="spin"), croc(32, 1200, 700, 0.6, 0.2, walk=400), T(32, 1300, 350, 56, "all the way to Antarctica", c="blue", d=0.4))
bd(32.5, road(32.5, 820, 0.0), car_go(32.5, 1100, 780, 0.2), croc(32.5, 600, 840, 0.6, 0.3, mood="sad"), ic(32.5, "question", 600, 450, 150, 0.4, mv="wig", c="red"))
bd(33, BIG(33, 960, 350, "200,000,000 yrs", c="blue", d=0.0, s=110), ic(33, "clock", 500, 650, 150, 0.2, mv="spin"), croc(33, 1350, 760, 0.6, 0.4))
bd(33.5, croc(33.5, 400, 760, 0.8, 0.0, walk=800), BIG(33.5, 960, 330, "able to move", c="green", d=0.3, s=110), check(33.5, 1600, 500, d=0.6))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"T. rex": "tee rex", "UCL": "U C L", "Sarcosuchus": "sar co sook us"})
