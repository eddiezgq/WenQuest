"""Daily science short 2026-10-20 (English): "Hackers turned freezers into ovens"
News (trending tech story of the week, still developing): night of 2026-10-11, attackers remotely took over refrigeration controllers
(Danfoss AK-SM / AK-SC, mostly old units no longer updated) at hundreds of French supermarkets, forced defrost and heated cases up to 50 C (122 F).
Sources: Al Jazeera 2026-10-13 (aljazeera.com/news/2026/10/13/unprecedented-cyberattack-hits-french-supermarkets-causing-food-losses):
at least 300 Intermarche/Netto stores (AFP), Carrefour 80, losses "tens of millions of euros ... in a single day" (Thierry Cotillard),
BFM TV: forced defrosting; fires at several stores; Sekoia analyst: Spain, Portugal, Poland, Germany, Belgium also affected.
The Hacker News 2026-10 (thehackernews.com/2026/10/attackers-heat-french-supermarket.html): Danfoss controllers, AK-SM 800 end-of-life 2021,
AK-SC 355 phased out 2016, attacker and entry route not established, CERT-FR: disconnect or filter access. CBC, CNBC same story.
Science (textbook): a fridge moves heat, it does not make cold (refrigerant evaporates inside, compressor, hot coils outside);
freezers have defrost heaters; USDA: frozen food safe at -18 C / 0 F, danger zone 4-60 C (40-140 F), bacteria can double in ~20 min,
a full closed freezer holds ~48 h without power, discard perishables left >2 h in the danger zone; melting ice takes 334 J per gram.
Our comparison: 50 C is close to Death Valley's hottest days (record 54.4 C / 130 F), said as "almost".
Character: Scoop, a little ice-cream cone (running gag: Scoop keeps melting; Scoop survives at the end). No hand.
    python3 make.py <kokoro model dir> | --fake | --boards-only   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("10月11日夜里，法国几百家超市的冰柜，|被黑客远程加热到了50度。", "On the night of October 11, freezers in hundreds of French supermarkets | were remotely heated to 50 degrees Celsius."),
 ("那是122华氏度。|冰淇淋表示：我不干了。", "That's 122 Fahrenheit. | The ice cream did not survive."),
 ("今天的问题：冰柜明明是造冷的，|它怎么能变成烤箱？", "Today's question: a freezer makes cold, right? | So how do you turn it into an oven?"),
 ("认识一下小勺。|小勺是一个冰淇淋，今天它很紧张。", "Meet Scoop. | Scoop is an ice cream cone, and Scoop is nervous today."),
 ("据报道，光是英特马歇和奈拓，|就至少有300家店中招。", "According to reports, at least 300 Intermarché and Netto stores | were hit."),
 ("家乐福说80家，还有好几家连锁也中招。|有的设备甚至开始冒火。", "Carrefour said 80 more, plus several other chains. | Some equipment even started to catch fire."),
 ("老板估计：一天之内，|损失几千万欧元。", "One boss estimated the damage: | tens of millions of euros, in a single day."),
 ("先说一个反常识：冰箱根本不会“造冷”。|它只会搬热。", "First, a surprise: a fridge doesn't make cold at all. | It moves heat."),
 ("就像用海绵从船里舀水：|在里面吸饱，到外面拧干。", "Like bailing a boat with a sponge: | soak it up inside, squeeze it out outside."),
 ("冷媒在柜子里蒸发，吸走热量，|压缩机一挤，在外面的管子上把热放掉。", "The refrigerant evaporates inside and soaks up heat. | The compressor squeezes it, and the coils outside dump that heat."),
 ("所以冰箱背后总是热乎乎的。|那是你食物的热。", "That's why the back of a fridge feels warm. | That's your food's heat."),
 ("反转一：每个冰柜里，|本来就装着一个加热器。", "Twist one: every freezer already has a heater | built right in."),
 ("因为冷柜会结霜，霜越厚，|搬热就越慢。", "Freezers grow frost, and the thicker the frost, | the worse they move heat."),
 ("所以它定时开一会儿加热，把霜化掉，|这叫除霜。", "So every so often a heater melts the ice away. | It's called defrost."),
 ("据法国媒体报道，黑客做的就是：|强行除霜，一直不停。", "French media reported that's exactly what the attackers did: | forced defrost, and kept it on."),
 ("控制这一切的，是一个联网的小盒子，|好让维修公司远程管理。", "All of this runs on a small connected controller, | so repair companies can manage it remotely."),
 ("中招的大多是老型号，|厂家早就不再给它们更新。", "Most of the hit units were old models | the maker had stopped updating years ago."),
 ("反转二：其实冰柜停电，|问题并不大。", "Twist two: if a freezer simply loses power, | it's usually fine."),
 ("美国农业部说，装满的冰柜关着门，|能撑大约48小时。", "The US Department of Agriculture says a full freezer, door closed, | holds for about 48 hours."),
 ("因为冰要化，得先吃进一大口热：|每克334焦耳。", "Because melting ice swallows a lot of heat: | 334 joules for every gram."),
 ("冰就是一块热量海绵，|替食物挡时间。", "Ice is a heat sponge. | It buys your food time."),
 ("可加热器是从里面往上烤。|海绵再大，也扛不住。", "But a heater cooks it from the inside. | No sponge can keep up with that."),
 ("50度，差不多是死亡谷|最热那几天的温度。", "50 degrees is almost as hot | as Death Valley on its hottest days."),
 ("反转三：就算东西又冻回去了，|也得全扔。", "Twist three: even if the food freezes again, | it all goes in the trash."),
 ("4到60度是危险区，|细菌大约20分钟就能翻一倍。", "Between 4 and 60 degrees is the danger zone. | Bacteria can double in about 20 minutes."),
 ("一个变两个，两个变四个，|两个小时，翻六次。", "One becomes two, two becomes four. | In two hours, that's six doublings."),
 ("冷冻只能让细菌睡觉，|杀不死它们。", "Freezing only puts bacteria to sleep. | It doesn't kill them."),
 ("所以规矩是：在危险区待过两小时，|就扔掉。", "So the rule is: two hours in the danger zone, | and out it goes."),
 ("这就是为什么一夜之间，|货架全空了。", "That's why overnight, | whole shelves went empty."),
 ("据一位安全分析师说，西班牙、葡萄牙、波兰、德国、比利时|也有超市受影响。", "One security analyst says stores in Spain, Portugal, Poland, Germany and Belgium | were affected too."),
 ("友情提示：到目前为止，是谁干的、|怎么进去的，官方都还没说。", "Friendly fine print: so far, officials haven't said who did it, | or how they got in."),
 ("法国网络安全部门的建议很朴素：|把这些盒子从网上断开，或者把门锁好。", "France's cyber agency gave simple advice: | unplug those boxes from the internet, or lock the door."),
 ("能远程控制的东西，|别人也可能远程控制。", "Anything you can control from far away, | someone else might, too."),
 ("所以，你家的智能设备，|记得更新。", "So, your smart gadgets at home? | Keep them updated."),
 ("小勺没事，它在家里的冰箱里。|你家冰箱，没联网吧？", "Scoop is fine. Scoop lives in a home freezer. | Yours isn't online... is it?"),
]
TITLE = {"zh": "黑客把冰柜变成了烤箱", "en": "Hackers Turned Freezers Into Ovens"}


def scoop(a, x, y, k=1.0, melt=False, c="red"):
    """Scoop: an ice-cream cone with a face; bobs and wobbles. melt=True adds drips that slide down."""
    i = uid("sc")
    E = [P(a, f"M{x - 70 * k},{y - 120 * k} L{x},{y + 90 * k} L{x + 70 * k},{y - 120 * k} Z", c="gold", w=5, fill="gold", idp=i),
         P(a, f"M{x - 40 * k},{y - 80 * k} L{x + 20 * k},{y - 10 * k} M{x + 40 * k},{y - 80 * k} L{x - 20 * k},{y - 10 * k}", c="ink", w=3, idp=i),
         O(a, x, y - 170 * k, 85 * k, c=c, fill=c, idp=i),
         O(a, x - 28 * k, y - 180 * k, 9 * k, c="ink", fill="ink", idp=i), O(a, x + 28 * k, y - 180 * k, 9 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x - 25 * k},{y - 145 * k} Q{x},{y - (160 if melt else 125) * k} {x + 25 * k},{y - 145 * k}", c="ink", w=4, idp=i),
         bob(a, i, 7 * k, 1.3), wig(a, i, (x, y + 90 * k), 4, 1.1)]
    if melt:
        for n in range(3):
            dr = uid("drip")
            E += [O(a, x - 50 * k + 50 * k * n, y - 110 * k, 14 * k, c=c, fill=c, idp=dr), sh(a, dr, 0, 140 * k, 0.2 + 0.3 * n, 1.0)]
    return E, i


def fridge(a, x, y, k=1.0, c="blue", d=None, door=True):
    """A freezer case: box + door that wiggles + spinning snowflake inside."""
    i, dr, sn = uid("fr"), uid("door"), uid("snow")
    E = [R(a, x - 160 * k, y - 220 * k, 320 * k, 440 * k, c="ink", idp=i), P(a, f"M{x - 160 * k},{y - 40 * k} L{x + 160 * k},{y - 40 * k}", c="ink", w=4, idp=i),
         P(a, f"M{x + 120 * k},{y - 140 * k} L{x + 120 * k},{y - 80 * k} M{x + 120 * k},{y + 20 * k} L{x + 120 * k},{y + 100 * k}", c="ink", w=8, idp=dr),
         P(a, f"M{x - 50 * k},{y - 130 * k} L{x + 50 * k},{y - 130 * k} M{x},{y - 180 * k} L{x},{y - 80 * k} M{x - 35 * k},{y - 165 * k} L{x + 35 * k},{y - 95 * k} "
              f"M{x - 35 * k},{y - 95 * k} L{x + 35 * k},{y - 165 * k}", c=c, w=5, idp=sn),
         spin(a, sn, (x, y - 130 * k), 40), bob(a, i, 3, 0.8), wig(a, dr, (x + 120 * k, y), 3, 2.0)]
    if d is not None:
        E.append(pop(a, i, d))
    return E, i


def thermo(a, x, y, k=1.0, frm=0.15, to=0.95, d=0.2, dur=1.0, c="red"):
    """Thermometer whose red column rises (grow from the bulb)."""
    i, col = uid("th"), uid("col")
    h = 360 * k
    return [R(a, x - 22 * k, y - h, 44 * k, h, c="ink", idp=i), O(a, x, y + 30 * k, 40 * k, c=c, fill=c, idp=i),
            R(a, x - 12 * k, y - h * to, 24 * k, h * to, c=c, fill=c, idp=col),
            {"t": "move", "at": a, "kind": "grow", "targets": [col], "axis": "y", "from": frm / to, "pivot": [x, y], "dur": dur, "delay": d},
            bob(a, i, 3, 0.7)]


def flame(a, x, y, k=1.0, d=0.0):
    i = uid("fl")
    return [P(a, f"M{x},{y} C{x - 70 * k},{y - 40 * k} {x - 30 * k},{y - 120 * k} {x},{y - 180 * k} C{x + 30 * k},{y - 120 * k} {x + 70 * k},{y - 40 * k} {x},{y} Z",
              c="red", w=5, fill="gold", idp=i), pop(a, i, d), wig(a, i, (x, y), 7, 3.0)]


def germ(a, x, y, r=26, d=0.0, c="green"):
    i = uid("gm")
    return [O(a, x, y, r, c=c, fill=c, idp=i), P(a, f"M{x - r - 12},{y} L{x - r},{y} M{x + r},{y} L{x + r + 12},{y} M{x},{y - r - 12} L{x},{y - r}", c=c, w=4, idp=i),
            pop(a, i, d), wig(a, i, (x, y), 10, 2.2)]


def box(a, x, y, k=1.0, d=None):
    """The controller: a little box with an antenna and blinking light, sending wifi arcs."""
    i, led = uid("bx"), uid("led")
    E = [R(a, x - 110 * k, y - 70 * k, 220 * k, 140 * k, c="ink", fill="muted", idp=i), P(a, f"M{x + 70 * k},{y - 70 * k} L{x + 90 * k},{y - 150 * k}", c="ink", w=5, idp=i),
         O(a, x - 60 * k, y, 14 * k, c="green", fill="green", idp=led), pulse(a, led, 0.2, 0.5), pulse(a, led, 1.0, 0.5), bob(a, i, 4, 1.0)]
    E += sound(a, x + 100 * k, y - 160 * k, 0.8 * k, c="blue", d=0.3)
    if d is not None:
        E.append(pop(a, i, d))
    return E, i


def store(a, x, y, k=1.0, d=0.0, c="ink"):
    i = uid("st")
    return [R(a, x - 70 * k, y - 50 * k, 140 * k, 100 * k, c=c, idp=i), P(a, f"M{x - 85 * k},{y - 50 * k} L{x},{y - 100 * k} L{x + 85 * k},{y - 50 * k}", c=c, w=4, idp=i),
            pop(a, i, d), bob(a, i, 3, 0.9 + 0.1 * (int(x) % 4))]


def stores(a, x0, y0, cols, rows, gap=170, k=0.8, d=0.1, step=0.04, c="ink"):
    E = []
    for r in range(rows):
        for q in range(cols):
            E += store(a, x0 + q * gap, y0 + r * gap * 0.8, k, d + step * (r * cols + q), c)
    return E


def sponge(a, x, y, k=1.0, d=0.0):
    i = uid("sp")
    return [R(a, x - 90 * k, y - 50 * k, 180 * k, 100 * k, c="gold", fill="gold", idp=i), O(a, x - 40 * k, y - 10 * k, 10 * k, c="ink", idp=i),
            O(a, x + 30 * k, y + 15 * k, 12 * k, c="ink", idp=i), pop(a, i, d), wig(a, i, (x, y), 6, 1.5)]


def drops(a, x, y, n=3, d=0.3, c="blue"):
    E = []
    for q in range(n):
        i = uid("dp")
        E += [O(a, x + 40 * (q - 1), y, 12, c=c, fill=c, idp=i), sh(a, i, 0, 180, d + 0.25 * q, 0.7)]
    return E


def waveheat(a, x, y, n=3, d=0.2, c="red"):
    """Wavy heat lines rising."""
    E = []
    for q in range(n):
        i = uid("hw")
        xx = x + 60 * (q - 1)
        E += [P(a, f"M{xx},{y} Q{xx - 20},{y - 40} {xx},{y - 80} Q{xx + 20},{y - 120} {xx},{y - 160}", c=c, w=5, idp=i), sh(a, i, 0, -80, d + 0.2 * q, 1.2),
              wig(a, i, (xx, y), 6, 2.0)]
    return E


def amb(a, n=2):
    E = star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    if n > 2:
        E += star(a, 1810, 900, 0.5, r=20)
    return E


B = []


def bd(a, *parts, n=2):
    E = []
    for p in parts:
        E += p
    B.append(E + amb(a, n))


Q = lambda a, x, y, s=200, d=0.4: (lambda q: [{"t": "icon", "at": a, "id": q, "name": "question", "x": x, "y": y, "size": s, "c": "red"}, pop(a, q, d),  # noqa: E731
                                              wig(a, q, (x + s / 2, y + s / 2), 8, 1.4)])(uid("q"))

# 0 freezers heated
f, fi = fridge(0, 560, 520, 1.1, c="red")
bd(0, f, thermo(0, 1000, 700, 1.1), flame(0, 560, 900, 0.6, d=0.8), BIG(0, 1450, 480, "50°C", c="red", d=0.5, s=150), stores(0, 1250, 760, 3, 1, k=0.6, d=0.3))
# 0.5 hundreds of stores
bd(0.5, stores(0.5, 260, 260, 9, 3, gap=170, k=0.7, d=0.0, step=0.025, c="red"), BIG(0.5, 960, 860, "hundreds of stores", c="red", d=0.6, s=110), n=3)
# 1 122 F
bd(1, thermo(1, 600, 720, 1.2, frm=0.1, to=1.0), BIG(1, 1200, 420, "122°F", c="red", d=0.3, s=150), waveheat(1, 1200, 800, d=0.4))
# 1.5 ice cream did not survive
s, si = scoop(1.5, 960, 640, 1.4, melt=True)
bd(1.5, s, waveheat(1.5, 600, 600), waveheat(1.5, 1320, 600, d=0.5), T(1.5, 960, 900, 64, "nope.", c="muted", d=0.8))
# 2 freezer makes cold right?
f, fi = fridge(2, 700, 520, 1.1)
bd(2, f, Q(2, 1200, 300), T(2, 1300, 760, 64, "makes cold?", c="blue", d=0.3), drops(2, 700, 820, d=0.6, c="blue"))
# 2.5 how into an oven
f, fi = fridge(2.5, 600, 520, 1.0, c="red")
bd(2.5, f, arr(2.5, 820, 520, 1100, 520, c="ink", d=0.3), flame(2.5, 1400, 640, 1.2, d=0.6), BIG(2.5, 1400, 800, "OVEN?", c="red", d=0.9, s=110))
# 3 meet Scoop
s, si = scoop(3, 960, 620, 1.8)
bd(3, s, [pop(3, si, 0.0)], BIG(3, 1500, 420, "Scoop", c="gold", d=0.4, s=140), star(3, 600, 320, 0.6, r=40), n=3)
# 3.5 nervous
s, si = scoop(3.5, 960, 640, 1.4)
bd(3.5, s, [wig(3.5, si + "*", (960, 760), 5, 4.0)], drops(3.5, 1130, 360, n=2, d=0.4), T(3.5, 960, 900, 64, "...nervous", c="muted", d=0.6))
# 4 300 Intermarche
bd(4, stores(4, 300, 300, 10, 3, gap=150, k=0.6, d=0.0, step=0.02, c="red"), BIG(4, 960, 840, "300+", c="red", d=0.5, s=150), n=3)
# 4.5 hit
bd(4.5, stores(4.5, 500, 420, 6, 1, gap=180, k=0.9, d=0.0, step=0.06), flame(4.5, 680, 350, 0.5, d=0.5), flame(4.5, 1220, 350, 0.5, d=0.8),
   BIG(4.5, 960, 760, "HIT", c="red", d=0.6, s=140))
# 5 Carrefour 80 + others
bd(5, stores(5, 300, 300, 8, 2, gap=160, k=0.6, d=0.0, step=0.03, c="blue"), BIG(5, 700, 760, "+80", c="blue", d=0.4, s=140),
   T(5, 1350, 760, 64, "+ more chains", c="ink", d=0.8))
# 5.5 catch fire
f, fi = fridge(5.5, 760, 520, 1.1, c="red")
bd(5.5, f, flame(5.5, 640, 260, 0.8, d=0.3), flame(5.5, 880, 260, 0.6, d=0.6), BIG(5.5, 1400, 500, "fire!", c="red", d=0.7, s=130), waveheat(5.5, 1400, 800, d=0.4))
# 6 boss estimated
E = []
for k in range(5):
    c = uid("coin")
    E += [O(6, 600 + 180 * k, 140, 50, c="gold", fill="gold", idp=c), sh(6, c, 0, 420, 0.1 + 0.2 * k, 0.6), spin(6, c, (600 + 180 * k, 140), 60)]
bd(6, E, T(6, 960, 760, 64, "damage...", c="ink", d=0.4), bar(6, 860, 700, 200, 120, "gold", d=0.5))
# 6.5 tens of millions of euros
bd(6.5, BIG(6.5, 960, 440, "€ tens of millions", c="gold", d=0.1, s=110), bar(6.5, 400, 860, 160, 250, "gold", d=0.3), bar(6.5, 1360, 860, 160, 300, "gold", d=0.5),
   T(6.5, 960, 700, 64, "in ONE day", c="red", d=0.8))
# 7 fridge doesn't make cold
f, fi = fridge(7, 600, 520, 1.1)
bd(7, f, cross(7, 600, 380, d=0.4), BIG(7, 1300, 400, "makes cold", c="blue", d=0.1, s=100), cross(7, 1300, 400, d=0.7), T(7, 1300, 620, 64, "surprise!", c="red", d=0.9))
# 7.5 it moves heat
f, fi = fridge(7.5, 600, 520, 1.0)
bd(7.5, f, arr(7.5, 700, 420, 1250, 420, c="red", d=0.2, w=10), waveheat(7.5, 1450, 520, d=0.5), BIG(7.5, 1000, 760, "MOVES HEAT", c="red", d=0.6, s=110))
# 8 bailing a boat
boat = uid("boat")
bd(8, [P(8, "M500,600 L1400,600 L1250,780 L650,780 Z", c="ink", w=6, fill="muted", idp=boat), bob(8, boat, 10, 0.8), rot(8, boat, 3, (950, 700), 0.3, 1.2)],
   sponge(8, 950, 520, 1.0, d=0.2), drops(8, 950, 300, d=0.5), T(8, 960, 200, 64, "bailing with a sponge", c="ink", d=0.3))
# 8.5 soak inside squeeze outside
sp_ = sponge(8.5, 600, 500, 1.2, d=0.0)
bd(8.5, sp_, [sh(8.5, sp_[0]["id"], 700, 0, 0.4, 1.0)], drops(8.5, 1300, 600, n=4, d=1.2), T(8.5, 600, 760, 56, "soak inside", c="blue", d=0.2),
   T(8.5, 1300, 760, 56, "squeeze outside", c="red", d=0.9))
# 9 refrigerant evaporates inside
f, fi = fridge(9, 560, 520, 1.1)
E = []
for k in range(4):
    i = uid("ht")
    E += [O(9, 460 + 60 * k, 700, 16, c="red", fill="red", idp=i), sh(9, i, 900 - 60 * k, -300, 0.2 + 0.25 * k, 1.0)]
bd(9, f, E, T(9, 1350, 300, 64, "refrigerant soaks up heat", c="blue", d=0.3), bob(9, fi, 4, 1.0) and [])
# 9.5 compressor squeezes, coils dump heat
cp = uid("cmp")
coil = uid("coil")
bd(9.5, [O(9.5, 600, 560, 120, c="ink", idp=cp), P(9.5, "M600,460 L600,660 M500,560 L700,560", c="ink", w=6, idp=cp), spin(9.5, cp, (600, 560), 150)],
   [P(9.5, "M1100,400 L1500,400 L1100,480 L1500,480 L1100,560 L1500,560 L1100,640 L1500,640", c="red", w=6, idp=coil), pop(9.5, coil, 0.3), pulse(9.5, coil, 0.9)],
   arr(9.5, 760, 560, 1060, 520, c="ink", d=0.2), waveheat(9.5, 1300, 380, d=0.6), T(9.5, 600, 780, 56, "compressor", c="ink", d=0.1), T(9.5, 1300, 780, 56, "hot coils", c="red", d=0.5))
# 10 back of fridge warm
f, fi = fridge(10, 760, 520, 1.1)
bd(10, f, waveheat(10, 1050, 560, d=0.2), waveheat(10, 1050, 360, d=0.6), T(10, 1450, 480, 64, "warm back", c="red", d=0.4), [rot(10, fi + "*", -8, (760, 740), 0.3, 0.8)])
# 10.5 your food's heat
s, si = scoop(10.5, 700, 620, 1.2)
bd(10.5, s, arr(10.5, 860, 500, 1150, 500, c="red", d=0.3), waveheat(10.5, 1350, 620, d=0.5), BIG(10.5, 1350, 300, "your food's heat", c="red", d=0.6, s=80))
# 11 twist one: heater built in
f, fi = fridge(11, 700, 540, 1.1)
bd(11, f, BIG(11, 960, 160, "TWIST 1", c="red", d=0.1, s=90), flame(11, 700, 700, 0.6, d=0.6), Q(11, 1250, 400, d=0.8))
# 11.5 built right in
htr = uid("htr")
f, fi = fridge(11.5, 960, 520, 1.3)
bd(11.5, f, [P(11.5, "M800,640 L840,600 L880,640 L920,600 L960,640 L1000,600 L1040,640 L1080,600 L1120,640", c="red", w=7, idp=htr), pop(11.5, htr, 0.3), pulse(11.5, htr, 0.8),
             pulse(11.5, htr, 1.4)], T(11.5, 1500, 600, 64, "heater!", c="red", d=0.4))
# 12 frost grows
E = []
for k in range(6):
    i = uid("frost")
    E += [P(12, f"M{460 + 80 * k},{300} L{480 + 80 * k},{340 + 25 * k} L{500 + 80 * k},{300}", c="blue", w=5, idp=i), pop(12, i, 0.1 + 0.15 * k),
          {"t": "move", "at": 12, "kind": "grow", "targets": [i], "axis": "y", "pivot": [480 + 80 * k, 300], "dur": 0.6, "delay": 0.2 + 0.15 * k}]
bd(12, [R(12, 400, 280, 560, 500, c="ink", idp=uid("fb"))], E, T(12, 1400, 420, 64, "frost builds up", c="blue", d=0.3), BIG(12, 1400, 620, "-18°C", c="blue", d=0.6, s=110))
# 12.5 thicker frost worse
bd(12.5, bar(12.5, 450, 820, 200, 520, "blue", d=0.1) + bar(12.5, 1250, 820, 200, 200, "red", d=0.4),
   T(12.5, 550, 900, 52, "frost", c="blue"), T(12.5, 1350, 900, 52, "heat moved", c="red"), arr(12.5, 700, 400, 1150, 600, c="ink", d=0.7))
# 13 heater melts ice
ice = uid("ice")
bd(13, [R(13, 600, 300, 400, 160, c="blue", fill="blue", idp=ice),
        {"t": "move", "at": 13, "kind": "grow", "targets": [ice], "axis": "y", "from": 1.0, "to": 0.2, "pivot": [800, 460], "dur": 1.2, "delay": 0.3}],
   flame(13, 800, 700, 0.9, d=0.1), drops(13, 800, 480, d=0.6), T(13, 1450, 480, 64, "every so often", c="ink", d=0.3))
# 13.5 defrost
bd(13.5, BIG(13.5, 960, 380, "DEFROST", c="red", d=0.1, s=150), flame(13.5, 500, 760, 0.7, d=0.4), flame(13.5, 1420, 760, 0.7, d=0.6),
   [e for k in range(3) for e in drops(13.5, 820 + 140 * k, 560, n=1, d=0.5 + 0.2 * k)])
# 14 French media reported
E = []
for k in range(3):
    i = uid("np")
    E += [R(14, 380 + 420 * k, 300, 340, 380, c="ink", idp=i), pop(14, i, 0.1 + 0.25 * k), rot(14, i, 5 * (k - 1), (550 + 420 * k, 680), 0.6 + 0.2 * k, 0.5)]
bd(14, E, T(14, 960, 820, 60, "French media reported...", c="ink", d=0.4))
# 14.5 forced defrost kept on
b_, bi = box(14.5, 500, 500, 1.2)
bd(14.5, b_, arr(14.5, 680, 500, 950, 500, c="red", d=0.3), flame(14.5, 1150, 640, 1.0, d=0.5), BIG(14.5, 1500, 500, "ON", c="red", d=0.7, s=130),
   T(14.5, 1300, 780, 56, "and on and on", c="red", d=1.0))
# 15 connected controller
b_, bi = box(15, 960, 520, 1.6, d=0.0)
bd(15, b_, T(15, 960, 820, 64, "connected controller", c="ink", d=0.4), f_ := fridge(15, 400, 520, 0.7)[0], fridge(15, 1550, 520, 0.7)[0])
# 15.5 repair companies remote
b_, bi = box(15.5, 1300, 500, 1.1)
E = []
for k in range(3):
    i = uid("pkt")
    E += [O(15.5, 650, 500, 14, c="blue", fill="blue", idp=i), sh(15.5, i, 560, 0, 0.2 + 0.35 * k, 0.6)]
bd(15.5, b_, [R(15.5, 380, 400, 260, 180, c="ink", idp=uid("lap"))], E, T(15.5, 960, 780, 56, "remote repair", c="ink", d=0.4))
# 16 old models
b_, bi = box(16, 700, 500, 1.4)
bd(16, b_, [rot(16, bi + "*", -6, (700, 570), 0.2, 0.8)], T(16, 1350, 400, 64, "old models", c="ink", d=0.2), BIG(16, 1350, 600, "2016", c="muted", d=0.5, s=110))
# 16.5 stopped updating
cal_ = uid("upd")
bd(16.5, [R(16.5, 500, 300, 360, 360, c="ink", idp=cal_), wig(16.5, cal_, (680, 300), 4, 1.0)], T(16.5, 680, 470, 64, "update", c="muted", d=0.1),
   cross(16.5, 680, 470, d=0.5), BIG(16.5, 1350, 480, "no more", c="red", d=0.7, s=110), arr(16.5, 1000, 700, 1600, 700, c="ink", d=0.3))
# 17 twist two: power loss
f, fi = fridge(17, 700, 540, 1.1)
plug = uid("plug")
bd(17, f, BIG(17, 960, 160, "TWIST 2", c="red", d=0.1, s=90), [P(17, "M900,700 L1150,700 L1150,640 M1150,760 L1150,700", c="ink", w=7, idp=plug), sh(17, plug, 200, 0, 0.5, 0.6)],
   T(17, 1450, 500, 64, "power off", c="ink", d=0.6))
# 17.5 usually fine
s, si = scoop(17.5, 960, 640, 1.4)
bd(17.5, s, check(17.5, 1400, 400, d=0.4), T(17.5, 960, 900, 64, "usually fine", c="green", d=0.3), [sh(17.5, si + "*", 0, -40, 0.6, 0.3), sh(17.5, si + "*", 0, 40, 0.9, 0.3)])
# 18 USDA says full freezer
f, fi = fridge(18, 700, 540, 1.1)
bd(18, f, T(18, 1350, 380, 64, "USDA:", c="ink", d=0.1), T(18, 1350, 520, 56, "full + door closed", c="blue", d=0.4), check(18, 1350, 680, d=0.8))
# 18.5 48 hours
E = []
for k in range(2):
    i = uid("clk")
    h = uid("hand")
    E += [O(18.5, 500 + 900 * k, 420, 140, c="ink", idp=i), P(18.5, f"M{500 + 900 * k},420 L{500 + 900 * k},310", c="red", w=7, idp=h),
          spin(18.5, h, (500 + 900 * k, 420), 90), pop(18.5, i, 0.2 * k)]
bd(18.5, E, BIG(18.5, 960, 780, "48 hours", c="blue", d=0.3, s=140))
# 19 melting ice swallows heat
ice = uid("ice")
bd(19, [R(19, 760, 380, 300, 300, c="blue", fill="blue", idp=ice), wig(19, ice, (910, 680), 3, 1.2)],
   [e for k in range(4) for e in arr(19, 300 + 0 * k, 300 + 120 * k, 720, 450 + 30 * k, c="red", d=0.2 + 0.2 * k, w=5)], T(19, 1450, 520, 64, "gulp!", c="red", d=0.8))
# 19.5 334 J per gram
bd(19.5, BIG(19.5, 960, 420, "334 J", c="red", d=0.1, s=150), T(19.5, 960, 600, 64, "per gram of ice", c="blue", d=0.4),
   [e for k in range(4) for e in sh(19.5, (lambda i: i)(uid("x")), 0, 0, 0, 0.1) and []], bar(19.5, 860, 860, 200, 160, "blue", d=0.6))
# 20 ice is heat sponge
s2 = sponge(20, 800, 500, 1.6, d=0.0)
bd(20, s2, [{"t": "move", "at": 20, "kind": "grow", "targets": [s2[0]["id"]], "axis": "both", "from": 0.8, "to": 1.2, "pivot": [800, 550], "dur": 1.0, "delay": 0.3}],
   waveheat(20, 1300, 700, d=0.2), BIG(20, 1350, 360, "heat sponge", c="blue", d=0.5, s=90))
# 20.5 buys time
E = []
for k in range(1):
    h = uid("hand")
    E += [O(20.5, 700, 480, 170, c="ink", idp=uid("clk")), P(20.5, "M700,480 L700,340", c="blue", w=8, idp=h), spin(20.5, h, (700, 480), 60)]
s, si = scoop(20.5, 1350, 640, 1.1)
bd(20.5, E, s, T(20.5, 1000, 900, 64, "buys time", c="green", d=0.4))
# 21 heater cooks from inside
f, fi = fridge(21, 700, 520, 1.2, c="red")
bd(21, f, flame(21, 700, 640, 0.9, d=0.2), waveheat(21, 700, 400, d=0.5), T(21, 1400, 500, 64, "from the inside", c="red", d=0.4))
# 21.5 no sponge keeps up
s3 = sponge(21.5, 700, 500, 1.4, d=0.0)
bd(21.5, s3, [{"t": "move", "at": 21.5, "kind": "grow", "targets": [s3[0]["id"]], "axis": "both", "from": 1.0, "to": 0.3, "pivot": [700, 550], "dur": 1.2, "delay": 0.3}],
   flame(21.5, 1200, 700, 1.1, d=0.1), cross(21.5, 700, 500, d=1.2), drops(21.5, 700, 600, n=3, d=0.4))
# 22 50 C almost as hot
bd(22, thermo(22, 500, 720, 1.1), BIG(22, 1100, 380, "50°C", c="red", d=0.2, s=150), arr(22, 1100, 520, 1100, 680, c="ink", d=0.5), sun_ := [])
# 22.5 Death Valley
sun = uid("sun")
bd(22.5, [O(22.5, 1400, 300, 110, c="gold", fill="gold", idp=sun), spin(22.5, sun, (1400, 300), 30), pulse(22.5, sun, 0.6)],
   [P(22.5, "M200,800 Q500,600 800,800 Q1100,620 1400,800 Q1600,700 1750,800", c="gold", w=6, idp=uid("dn"))], waveheat(22.5, 700, 700, d=0.2),
   BIG(22.5, 760, 360, "Death Valley", c="red", d=0.5, s=100))
# 23 twist three: refreeze
f, fi = fridge(23, 700, 540, 1.1)
bd(23, f, BIG(23, 960, 160, "TWIST 3", c="red", d=0.1, s=90), T(23, 1400, 480, 64, "frozen again...", c="blue", d=0.4), Q(23, 1300, 600, s=160, d=0.8))
# 23.5 trash
bin_ = uid("bin")
E = []
for k in range(3):
    i = uid("fd")
    E += [R(23.5, 500 + 120 * k, 200, 90, 90, c="blue", fill="blue", idp=i), sh(23.5, i, 400 - 120 * k, 380, 0.2 + 0.3 * k, 0.6), rot(23.5, i, 90, (545 + 120 * k, 245), 0.2 + 0.3 * k, 0.6)]
bd(23.5, [R(23.5, 820, 560, 300, 320, c="ink", fill="muted", idp=bin_), wig(23.5, bin_, (970, 880), 4, 2.0)], E, BIG(23.5, 1500, 500, "TRASH", c="red", d=1.0, s=120))
# 24 danger zone
bd(24, thermo(24, 500, 760, 1.2, frm=0.3, to=0.7), [R(24, 600, 380, 700, 280, c="red", idp=uid("dz"))], BIG(24, 950, 520, "4–60°C", c="red", d=0.3, s=110),
   T(24, 950, 760, 64, "danger zone", c="red", d=0.6), germ(24, 1500, 500, d=0.8))
# 24.5 bacteria double 20 min
bd(24.5, germ(24.5, 600, 500, 50, d=0.0), germ(24.5, 900, 450, 50, d=0.5), germ(24.5, 900, 580, 50, d=0.6), arr(24.5, 680, 500, 820, 500, c="ink", d=0.3),
   BIG(24.5, 1400, 500, "20 min", c="green", d=0.7, s=120))
# 25 one two four
E = []
for k, n_ in enumerate([1, 2, 4]):
    for q in range(n_):
        E += germ(25, 400 + 500 * k + 60 * (q % 2), 400 + 80 * (q // 2) + 40 * (q % 2), 30, d=0.2 + 0.4 * k + 0.05 * q)
bd(25, E, T(25, 960, 760, 64, "1 → 2 → 4", c="ink", d=0.3))
# 25.5 six doublings in two hours
E = []
for k in range(7):
    E += bar(25.5, 300 + 200 * k, 820, 120, 8 * 2 ** k, "green", d=0.1 + 0.15 * k, dur=0.4)
bd(25.5, E, BIG(25.5, 700, 300, "×64", c="green", d=1.2, s=140), T(25.5, 1300, 300, 64, "2 hours", c="ink", d=0.3))
# 26 freezing puts bacteria to sleep
E = []
for k in range(3):
    E += germ(26, 600 + 200 * k, 500, 40, d=0.1 * k, c="blue")
    zt = T(26, 640 + 200 * k, 420, 50, "z", c="blue")
    E += zt + [sh(26, zt[0]["id"], 30, -120, 0.3 + 0.3 * k, 1.2)]
bd(26, E, T(26, 1450, 500, 64, "just sleeping", c="blue", d=0.5))
# 26.5 doesn't kill
bd(26.5, germ(26.5, 700, 500, 60, d=0.0), germ(26.5, 960, 560, 40, d=0.3), check(26.5, 1400, 400, c="red", d=0.6), T(26.5, 1300, 650, 64, "still alive", c="green", d=0.5))
# 27 rule two hours
E = []
h = uid("hand")
E += [O(27, 700, 480, 170, c="ink", idp=uid("clk")), P(27, "M700,480 L780,380", c="red", w=8, idp=h), spin(27, h, (700, 480), 120)]
bd(27, E, BIG(27, 1300, 480, "2 hours", c="red", d=0.3, s=130), germ(27, 1300, 720, 30, d=0.6), germ(27, 1400, 720, 30, d=0.8))
# 27.5 out it goes
bin_ = uid("bin")
s, si = scoop(27.5, 600, 500, 1.0, melt=True)
bd(27.5, s, [sh(27.5, si + "*", 600, 200, 0.4, 0.8), R(27.5, 1080, 560, 300, 320, c="ink", fill="muted", idp=bin_), wig(27.5, bin_, (1230, 880), 4, 2.0)],
   T(27.5, 1300, 300, 64, "out it goes", c="red", d=0.3))
# 28 overnight
moon = uid("moon")
bd(28, [O(28, 1500, 280, 100, c="gold", fill="gold", idp=moon), sh(28, moon, -900, 0, 0.1, 2.0), pulse(28, moon, 0.5)], stores(28, 500, 700, 5, 1, gap=230, k=1.0, d=0.2),
   T(28, 960, 480, 64, "overnight", c="ink", d=0.3))
# 28.5 shelves empty
E = []
for k in range(3):
    sh_ = uid("shelf")
    E += [P(28.5, f"M400,{350 + 180 * k} L1500,{350 + 180 * k}", c="ink", w=6, idp=sh_)]
    for q in range(5):
        i = uid("it")
        E += [R(28.5, 450 + 200 * q, 270 + 180 * k, 120, 80, c="blue", fill="blue", idp=i), sh(28.5, i, 0, 900, 0.1 + 0.08 * (k * 5 + q), 0.5)]
bd(28.5, E, BIG(28.5, 960, 900, "EMPTY", c="red", d=1.2, s=110))
# 29 analyst says
E = []
for k in range(5):
    E += store(29, 400 + 280 * k, 500, 1.0, 0.1 + 0.15 * k, c="blue")
bd(29, E, T(29, 960, 300, 60, "one analyst says...", c="ink", d=0.2), sound(29, 1700, 500, 1.0, d=0.5, dirn=-1))
# 29.5 affected too
E = []
for k, nm in enumerate(["ES", "PT", "PL", "DE", "BE"]):
    i = uid("fl")
    E += [O(29.5, 360 + 300 * k, 460, 100, c="red", idp=i), pop(29.5, i, 0.1 + 0.15 * k), bob(29.5, i, 6, 1.0 + 0.1 * k)]
    E += T(29.5, 360 + 300 * k, 470, 60, nm, c="red", d=0.15 + 0.15 * k)
bd(29.5, E, T(29.5, 960, 760, 64, "affected too", c="ink", d=0.9))
# 30 fine print: who
pf = uid("pf")
bd(30, BIG(30, 960, 200, "fine print", c="muted", d=0.1, s=80), [O(30, 760, 520, 130, c="ink", fill="ink", idp=pf), bob(30, pf, 8, 1.0), wig(30, pf, (760, 650), 5, 1.2)],
   Q(30, 1150, 380, d=0.4), T(30, 1450, 700, 60, "who?", c="red", d=0.6))
# 30.5 how they got in
dr_ = uid("dr")
bd(30.5, [R(30.5, 700, 280, 300, 500, c="ink", idp=dr_), rot(30.5, dr_, -25, (700, 530), 0.3, 0.8)], Q(30.5, 1150, 380, d=0.5),
   T(30.5, 1450, 700, 60, "how?", c="red", d=0.6), T(30.5, 960, 900, 52, "not yet known", c="muted", d=0.9))
# 31 simple advice
b_, bi = box(31, 700, 500, 1.4)
bd(31, b_, T(31, 1350, 400, 60, "France's cyber agency:", c="ink", d=0.2), BIG(31, 1350, 600, "simple fix", c="green", d=0.6, s=90))
# 31.5 unplug or lock
b_, bi = box(31.5, 600, 500, 1.2)
lk = uid("lock")
bd(31.5, b_, cross(31.5, 760, 340, d=0.4), [R(31.5, 1250, 460, 240, 200, c="gold", fill="gold", idp=lk), P(31.5, "M1300,460 Q1300,330 1370,330 Q1440,330 1440,460", c="ink", w=10, idp=lk),
                                            pop(31.5, lk, 0.7), wig(31.5, lk, (1370, 660), 6, 2.0)], T(31.5, 960, 860, 60, "unplug  or  lock", c="ink", d=0.6))
# 32 control from far away
lap = uid("lap")
f, fi = fridge(32, 1450, 520, 1.0)
bd(32, [R(32, 300, 420, 320, 220, c="ink", idp=lap), bob(32, lap, 5, 1.0)], f, sound(32, 700, 520, 1.0, d=0.2), arr(32, 720, 520, 1250, 520, c="blue", d=0.4),
   T(32, 960, 860, 56, "control from far away", c="ink", d=0.4))
# 32.5 someone else
pf = uid("pf")
f, fi = fridge(32.5, 1450, 520, 1.0, c="red")
bd(32.5, [O(32.5, 450, 480, 110, c="ink", fill="ink", idp=pf), bob(32.5, pf, 8, 1.1), wig(32.5, pf, (450, 590), 6, 1.4)], f, arr(32.5, 600, 520, 1250, 520, c="red", d=0.3),
   T(32.5, 960, 860, 60, "someone else, too", c="red", d=0.6))
# 33 smart gadgets at home
E = []
for k in range(3):
    E += box(33, 500 + 460 * k, 460, 0.9)[0]
bd(33, E, T(33, 960, 800, 64, "smart gadgets at home", c="ink", d=0.4))
# 33.5 keep them updated
ar = uid("upd")
bd(33.5, [O(33.5, 700, 480, 170, c="green", idp=ar), spin(33.5, ar, (700, 480), 90)], arr(33.5, 700, 310, 820, 310, c="green", d=0.1), check(33.5, 700, 480, d=0.6),
   BIG(33.5, 1350, 480, "UPDATE", c="green", d=0.4, s=120))
# 34 Scoop is fine
s, si = scoop(34, 760, 640, 1.4)
f, fi = fridge(34, 1350, 540, 1.0)
bd(34, s, f, [sh(34, si + "*", 0, -40, 0.4, 0.3), sh(34, si + "*", 0, 40, 0.7, 0.3)], check(34, 760, 230, d=0.9), n=3)
# 34.5 yours isn't online?
f, fi = fridge(34.5, 760, 540, 1.1)
bd(34.5, f, sound(34.5, 960, 300, 1.0, d=0.4), Q(34.5, 1250, 360, d=0.7), T(34.5, 1400, 760, 64, "...is it?", c="red", d=0.9), n=3)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"€": "", "Intermarché": "Inter-marshay"})
