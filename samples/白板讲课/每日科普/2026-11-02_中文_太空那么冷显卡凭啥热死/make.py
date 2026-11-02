"""每日科普 2026-11-02（中文）：《太空那么冷，显卡凭啥热死？》
新闻：马斯克称轨道（太空）AI 算力的月度新增规模可能在 2028 年底左右超过地面，2029 年大幅领先。
热榜：新浪互联网热点小时报 2026-11-02 17 时第 1 条（“马斯克：2029年轨道算力将碾压地面”）、第 3 条。
出处：
- 新浪互联网热点小时报 https://k.sina.com.cn/article_7857201856_1d45362c001908tdcs.html
- 国际空间站外部主动热控系统最多散热约 70 kW：https://www.wikiwand.com/en/articles/External_Active_Thermal_Control_System （据 NASA 资料）
常识/估算：太空背景约 -270 ℃；真空不导热不对流，只能热辐射；辐射功率 ∝ 绝对温度的四次方（斯特藩-玻尔兹曼定律）；
  一块高端 AI 显卡约 700 瓦（估算，H100 级别），70 kW ≈ 100 块（估算）；向阳面一百多度（常见资料）。
比喻（太空 = 保温瓶，显卡泡成热茶）是我们的；2029 时间表是马斯克的预测。
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_chip, stick  # noqa: E402

S = [
 ("马斯克说：|到2029年，天上的AI算力要碾压地面。", "Elon Musk says: | by 2029, AI computing in orbit will crush computing on the ground."),
 ("据报道，他预计2028年底左右，|太空每月新增的算力就会超过地面。", "Reportedly, he expects that around the end of 2028, | new computing added in space each month will pass the ground."),
 ("听起来很美：太空零下两百七十度，|一台天然的大冰箱！", "Sounds great: space is minus two hundred seventy degrees, | a giant free fridge!"),
 ("今天的烧脑问题：|太空那么冷，显卡凭啥会热死？", "Today's brain teaser: | space is so cold, so how can a GPU overheat?"),
 ("先认识主角：小芯，|一块AI显卡。", "Meet our hero, Chip, | an AI graphics card."),
 ("它一干活，|一块就要吃掉大约七百瓦。", "When it works, | one card eats about seven hundred watts."),
 ("吃进去的电，|几乎全都变成了热。", "Almost all that electricity | turns into heat."),
 ("在地上，热是怎么走的？|靠空气。", "On the ground, how does heat leave? | Through the air."),
 ("风扇一吹，热空气被赶走，|冷空气补进来。", "A fan blows the hot air away, | and cool air rushes in."),
 ("机房再加上水冷，|热就被一路搬到室外。", "Add water cooling, | and the heat is carried all the way outside."),
 ("反转一：太空里，|没有空气。", "Twist one: in space, | there is no air."),
 ("没有空气，风扇转得再快，|也是白转。", "With no air, however fast the fan spins, | it moves nothing."),
 ("太空不是冰箱，|是一个保温瓶。", "Space is not a fridge. | It is a thermos."),
 ("保温瓶为啥保温？|夹层里抽成了真空。", "Why does a thermos keep things hot? | The gap in its wall is a vacuum."),
 ("热没法靠碰传出去，|也没法靠吹。", "Heat cannot leave by touching, | or by blowing."),
 ("冷是真冷，|可那份冷根本碰不到你。", "The cold is real, | but it never touches you."),
 ("那热还剩哪条路？|发光。", "So what way out is left for heat? | Glowing."),
 ("所有东西都在发看不见的红外光，|你我也在发。", "Everything gives off invisible infrared light, | including you and me."),
 ("其实你在黑夜里也在发光，|热成像相机拍到的就是它。", "You glow in the dark too. | A thermal camera sees exactly that."),
 ("这叫热辐射，|是太空里唯一的出路。", "This is thermal radiation, | the only exit in space."),
 ("反转二：这条路，|窄得吓人。", "Twist two: this exit | is shockingly narrow."),
 ("国际空间站有好几大片散热板，|据NASA资料，最多也就散掉约七十千瓦。", "The space station has several big radiator panels. | According to NASA, they shed at most about seventy kilowatts."),
 ("七十千瓦是多少？|估算一下：大约一百块显卡。", "How much is seventy kilowatts? | A rough estimate: about one hundred GPUs."),
 ("而一个大型AI机房，|动不动就是几十万块。", "And a big AI data center | can hold hundreds of thousands."),
 ("怎么办？|让散热板更烫一点。", "What to do? | Make the radiators hotter."),
 ("发光散热有个规律：|绝对温度翻一倍，散热变十六倍。", "Glowing follows a rule: | double the absolute temperature, and the heat shed goes up sixteen times."),
 ("这叫四次方定律：|温度自己乘四遍。", "It is the fourth power law: | temperature multiplied by itself four times."),
 ("可显卡怕烫，|它热不起来。", "But GPUs hate heat. | They cannot run that hot."),
 ("小芯表示：|我只想要一台风扇。", "Chip says: | all I want is a fan."),
 ("所以散热板只能做得巨大，|大得像一对对翅膀。", "So the radiators must be huge, | like giant pairs of wings."),
 ("空间站上那些白色的大板子就是散热板，|不是太阳能板。", "On the space station, the big white panels are radiators, | not solar panels."),
 ("反转三，最反直觉：|太阳还在帮倒忙。", "Twist three, the strangest: | the Sun makes it worse."),
 ("太空里没有云挡着，|向阳的一面能晒到一百多度。", "In space no clouds block the Sun. | The sunny side can bake above one hundred degrees."),
 ("所以散热板得侧着身子，|躲着太阳。", "So the radiators turn edge on, | dodging the Sun."),
 ("那马斯克图什么？|图的恰恰就是太阳。", "Then why does Musk want it? | Exactly for the Sun."),
 ("合适的轨道上几乎一直有太阳，|没有黑夜，没有阴天。", "In the right orbit, sunlight is almost nonstop: | no night, no cloudy days."),
 ("电几乎白来，|也不用抢地、抢水。", "Nearly free power, | and no fight over land or water."),
 ("地上的大机房，|有的要用大量的水来降温。", "Some big data centers on the ground | use lots of water for cooling."),
 ("说白了是一笔账：|省下的电，能不能抵掉散热的麻烦。", "It comes down to a trade: | can the power saved pay for the cooling trouble?"),
 ("友情提示：2029的时间表是马斯克的预测，|还没有人在太空建成大型AI机房。", "Fine print: the 2029 timeline is Musk's prediction. | Nobody has built a large AI data center in space yet."),
 ("一百块显卡是估算，|十六倍是物理规律，都不是哪家公司的方案。", "One hundred GPUs is an estimate, | sixteen times is physics. Neither is any company's design."),
 ("所以，太空那么冷，显卡凭啥会热死？|因为冷碰不到它，热也甩不出去。", "So why can a GPU overheat in freezing space? | Because the cold can't touch it, and the heat can't get out."),
 ("太空是全宇宙最大的保温瓶。|显卡上去，可别被泡成一杯热茶。", "Space is the biggest thermos in the universe. | Send a GPU up there, and don't let it steep like hot tea."),
]
TITLE = {"zh": "太空那么冷，显卡凭啥热死？", "en": "Space Is Freezing. Why Do GPUs Overheat?"}

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


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def gpu(a, x, y, k=1.0, d=0.0, mood="happy", hot=False, shake=False):
    """小芯 = AI 显卡（cute_chip, label GPU）；hot = 头顶冒火；shake = 热得发抖。"""
    i = uid("gp")
    E = cute_chip(x, y, k, a, idp=i, mood=mood, label="GPU") + [pop(a, i + "_b", d)]
    if shake:
        E.append({"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y + 120 * k], "amp": 5, "hz": 4})
    if hot:
        for q, dx in enumerate((-60, 0, 60)):
            E += ic(a, "flame", x + dx * k, y - 210 * k, 70 * k, d + 0.2 + 0.1 * q, mv="wig", c="red")
    return E


def fan(a, x, y, r=110, d=0.0, rpm=200, c="blue"):
    i, j = uid("fn"), uid("fr")
    blades = " ".join(f"M{x},{y} Q{x + r * 0.9 * ((q % 2) * 2 - 1) * 0.2 + (r if q == 0 else -r if q == 2 else 0)},{y + (r if q == 1 else -r if q == 3 else 0) * 1.0} "
                      f"{x + (r * 0.8 if q == 0 else -r * 0.8 if q == 2 else 0)},{y + (r * 0.8 if q == 1 else -r * 0.8 if q == 3 else 0)}" for q in range(4))
    return [O(a, x, y, r + 20, c="ink", idp=j, sw=6), pop(a, j, d), P(a, blades, c=c, w=12, idp=i), pop(a, i, d + 0.1), spin(a, i, (x, y), rpm)]


def air(a, x, y, n=5, dx=420, d=0.0, c="red"):
    """热空气小点被吹走（一个点一个动作，错开）。"""
    E = []
    for q in range(n):
        i = uid("ai")
        E += [O(a, x + 20 * (q % 2), y - 90 + 45 * q, 16, c=c, fill=c, idp=i), pop(a, i, d + 0.08 * q), sh(a, i, dx, -20 + 10 * q, d + 0.3 + 0.18 * q, 1.4)]
    return E


def cool(a, x, y, n=4, dx=-300, d=0.0):
    return air(a, x, y, n, dx, d, c="blue")


def pipe(a, x0, y0, x1, d=0.0):
    """水冷管，水点沿管子跑。"""
    i = uid("pp")
    E = [P(a, f"M{x0},{y0} L{x1},{y0}", c="blue", w=14, idp=i), pop(a, i, d)]
    for q in range(3):
        j = uid("dp")
        E += [O(a, x0 + 30, y0, 12, c="paper", fill="paper", idp=j), sh(a, j, x1 - x0 - 60, 0, d + 0.3 + 0.4 * q, 1.2)]
    return E


def thermos(a, x, y, d=0.0, inner="red"):
    """保温瓶：外壳 + 真空夹层（虚线）+ 里面的热水，瓶口冒热气。"""
    o, v, w, s = uid("th"), uid("tv"), uid("tw"), uid("ts")
    E = [R(a, x - 150, y - 260, 300, 520, c="ink", idp=o, sw=7), pop(a, o, d),
         R(a, x - 110, y - 220, 220, 440, c="muted", idp=v, sw=4), pop(a, v, d + 0.15),
         R(a, x - 95, y - 120, 190, 325, c=inner, fill=inner, idp=w), {"t": "move", "at": a, "kind": "grow", "targets": [w], "axis": "y", "pivot": [x, y + 205], "dur": 0.7, "delay": d + 0.3},
         P(a, f"M{x - 30},{y - 290} Q{x - 60},{y - 340} {x - 30},{y - 390} M{x + 30},{y - 290} Q{x},{y - 340} {x + 30},{y - 390}", c="muted", w=5, idp=s),
         pop(a, s, d + 0.6), wig(a, s, (x, y - 290), 8, 1.5)]
    return E


def rays(a, x, y, r=170, n=6, d=0.0, c="red"):
    """往外发光（红外）：一圈箭头依次长出来、再闪。"""
    import math
    E = []
    for q in range(n):
        ang = 2 * math.pi * q / n
        x0, y0 = x + r * math.cos(ang), y + r * math.sin(ang)
        x1, y1 = x + (r + 130) * math.cos(ang), y + (r + 130) * math.sin(ang)
        E += arr(a, x0, y0, x1, y1, c=c, w=6, d=d + 0.07 * q, dur=0.35)
    return E


def panel(a, x, y, w=420, h=140, d=0.0, c="blue", tilt=False):
    i = uid("pn")
    lines = " ".join(f"M{x + w * q / 6},{y} L{x + w * q / 6},{y + h}" for q in range(1, 6))
    E = [R(a, x, y, w, h, c="ink", fill=c, idp=i, sw=5), P(a, lines, c="paper", w=3, idp=i),
         {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "x", "pivot": [x if x > 900 else x + w, y + h / 2], "dur": 0.6, "delay": d}]
    if tilt:
        E.append(rot(a, i, 70, (x + w / 2, y + h / 2), d + 0.8, 0.8))
    return E


def sat(a, x, y, s=200, d=0.0, wings=True):
    E = ic(a, "satellite", x, y, s, d, mv="bob")
    if wings:
        E += panel(a, x - s / 2 - 360, y - 60, 340, 120, d + 0.3) + panel(a, x + s / 2 + 20, y - 60, 340, 120, d + 0.4)
    return E


def sun(a, x, y, s=200, d=0.0):
    return ic(a, "sun", x, y, s, d, mv="spin", c="gold")


def thermo(a, x, y, d=0.0, up=True):
    """温度计：红柱升（up）或降。"""
    i, j = uid("tm"), uid("tl")
    h = 360
    E = [R(a, x - 30, y - h, 60, h, c="ink", idp=i, sw=6), O(a, x, y + 30, 50, c="ink", fill="red", idp=i), pop(a, i, d),
         R(a, x - 18, y - (h - 30 if up else 60), 36, h - 30 if up else 60, c="red", fill="red", idp=j)]
    E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y], "dur": 1.0, "delay": d + 0.2})
    return E


def calc(a, x, y, d=0.0):
    """一杆秤：左电、右热，来回晃。"""
    i = uid("sc")
    E = [P(a, f"M{x - 360},{y} L{x + 360},{y} M{x},{y} L{x},{y + 260} M{x - 120},{y + 260} L{x + 120},{y + 260}", c="ink", w=8, idp=i), pop(a, i, d),
         {"t": "move", "at": a, "kind": "wiggle", "targets": [i], "pivot": [x, y], "amp": 6, "hz": 0.8}]
    return E


def man(a, x, y, k=1.4, d=0.0):
    i = uid("mn")
    return stick(x, y, k, a, idp=i) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                       {"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 6, "hz": 1.6}]


# ---------- boards ----------
bd(0, ic(0, "rocket", 450, 600, 220, 0.0, mv="bob"), BIG(0, 1250, 330, "马斯克", c="ink", d=0.1, s=110), sat(0, 1250, 650, 160, 0.3, wings=False), star(0, 1600, 500, 0.5, r=30))
bd(0.5, BIG(0.5, 960, 280, "2029", c="red", d=0.0, s=150), sat(0.5, 960, 560, 150, 0.2), ic(0.5, "globe", 960, 850, 160, 0.4, mv="spin"))
bd(1, T(1, 960, 250, 70, "据报道", c="muted", d=0.0), BIG(1, 960, 420, "2028 年底", c="red", d=0.2, s=120), ic(1, "clock", 600, 700, 160, 0.3, mv="spin"), ic(1, "chip", 1300, 700, 160, 0.4, mv="bob"))
bd(1.5, bar(1.5, 600, 900, 160, 250, "muted", 0.2), bar(1.5, 900, 900, 160, 500, "blue", 0.4), T(1.5, 680, 950, 50, "地面", d=0.1), T(1.5, 980, 950, 50, "太空", c="blue", d=0.3),
   sat(1.5, 1500, 450, 150, 0.5, wings=False), arr(1.5, 1150, 700, 1350, 500, c="red", d=0.7))
bd(2, BIG(2, 1250, 380, "-270 ℃", c="blue", d=0.1, s=140), thermo(2, 600, 750, 0.2, up=False), ic(2, "moon", 1250, 700, 160, 0.4, mv="bob"))
bd(2.5, R(2.5, 750, 300, 420, 600, c="blue", sw=7), P(2.5, "M750,520 L1170,520", c="blue", w=6), T(2.5, 960, 420, 60, "大冰箱", c="blue", d=0.2),
   gpu(2.5, 960, 720, 0.7, 0.3), star(2.5, 1400, 400, 0.4, r=36), star(2.5, 500, 700, 0.6, r=30))
bd(3, BIG(3, 1150, 360, "烧脑问题", c="red", d=0.0, s=130), ic(3, "question", 450, 450, 260, 0.2, mv="wig", c="red"), gpu(3, 1300, 750, 0.7, 0.3, mood="o"))
bd(3.5, ic(3.5, "moon", 450, 400, 150, 0.0, mv="bob"), gpu(3.5, 960, 650, 1.0, 0.1, mood="sad", hot=True, shake=True), T(3.5, 1450, 450, 70, "凭啥热死？", c="red", d=0.4))
bd(4, gpu(4, 700, 600, 1.4, 0.0), T(4, 1350, 400, 80, "小芯", c="blue", d=0.2), star(4, 1350, 600, 0.4, r=40))
bd(4.5, gpu(4.5, 600, 600, 1.2, 0.0), BIG(4.5, 1350, 450, "AI 显卡", c="blue", d=0.2, s=110), ic(4.5, "computer", 1350, 720, 150, 0.4, mv="bob"))
bd(5, gpu(5, 600, 600, 1.1, 0.0, shake=True), ic(5, "battery", 1100, 600, 150, 0.2, mv="wig"), arr(5, 1000, 600, 780, 600, c="gold", d=0.3))
bd(5.5, gpu(5.5, 550, 620, 1.1, 0.0, shake=True), BIG(5.5, 1300, 450, "≈ 700 瓦", c="red", d=0.2, s=130), bar(5.5, 1150, 900, 80, 150, "gold", 0.4), bar(5.5, 1300, 900, 80, 260, "gold", 0.5))
bd(6, ic(6, "battery", 450, 550, 160, 0.0, mv="wig"), arr(6, 580, 550, 800, 550, c="gold", d=0.2), gpu(6, 1050, 600, 0.9, 0.1), arr(6, 1250, 550, 1450, 550, c="red", d=0.5), ic(6, "flame", 1600, 550, 150, 0.6, mv="wig", c="red"))
bd(6.5, gpu(6.5, 700, 620, 1.1, 0.0, mood="o", hot=True), BIG(6.5, 1400, 450, "几乎全变成热", c="red", d=0.3, s=90), thermo(6.5, 1400, 850, 0.4))
bd(7, ic(7, "globe", 500, 500, 200, 0.0, mv="spin"), T(7, 1150, 400, 70, "在地上", c="ink", d=0.2), ic(7, "question", 1150, 650, 140, 0.3, mv="wig", c="red"))
bd(7.5, gpu(7.5, 600, 620, 1.0, 0.0), air(7.5, 800, 620, 5, 600, 0.2), BIG(7.5, 1350, 300, "靠空气", c="blue", d=0.3, s=110), ic(7.5, "wind", 1500, 650, 150, 0.4, mv="wig"))
bd(8, fan(8, 500, 600, 120, 0.0), gpu(8, 900, 620, 0.8, 0.1), air(8, 1050, 620, 5, 500, 0.3), T(8, 1350, 280, 60, "热空气赶走", c="red", d=0.3))
bd(8.5, fan(8.5, 500, 600, 120, 0.0), gpu(8.5, 900, 620, 0.8, 0.0), cool(8.5, 1500, 620, 4, -400, 0.2), T(8.5, 1350, 280, 60, "冷空气补进来", c="blue", d=0.3))
bd(9, ic(9, "building", 500, 600, 240, 0.0, mv="bob"), pipe(9, 650, 650, 1300, 0.2), ic(9, "water", 1450, 600, 160, 0.4, mv="wig", c="blue"), T(9, 960, 300, 64, "水冷", c="blue", d=0.3))
bd(9.5, ic(9.5, "building", 450, 600, 220, 0.0, mv="bob"), arr(9.5, 650, 600, 1150, 600, c="red", d=0.2), ic(9.5, "wind", 1400, 550, 180, 0.4, mv="wig"), T(9.5, 960, 300, 64, "一路搬到室外", c="red", d=0.4))
bd(10, BIG(10, 960, 360, "反转一", c="red", d=0.0, s=150), sat(10, 960, 700, 150, 0.2), ic(10, "flame", 1600, 450, 140, 0.4, mv="wig", c="red"))
bd(10.5, BIG(10.5, 1300, 450, "没有空气", c="red", d=0.2, s=120), ic(10.5, "wind", 550, 450, 200, 0.0, mv="wig"), cross(10.5, 550, 450, d=0.4), ic(10.5, "moon", 550, 800, 120, 0.3, mv="bob"))
bd(11, fan(11, 600, 600, 140, 0.0, rpm=400), gpu(11, 1150, 620, 0.9, 0.1, mood="sad", hot=True), T(11, 960, 230, 60, "转得再快", c="ink", d=0.2))
bd(11.5, fan(11.5, 600, 600, 140, 0.0, rpm=400), BIG(11.5, 1300, 450, "白转", c="red", d=0.2, s=150), cross(11.5, 1300, 700, d=0.5))
bd(12, R(12, 300, 300, 380, 560, c="blue", sw=7), cross(12, 490, 580, d=0.3), T(12, 490, 950, 50, "冰箱", c="blue", d=0.2), thermos(12, 1300, 600, 0.5))
bd(12.5, thermos(12.5, 700, 600, 0.0), BIG(12.5, 1400, 450, "保温瓶", c="red", d=0.3, s=120), check(12.5, 1400, 650, d=0.6))
bd(13, thermos(13, 600, 600, 0.0), ic(13, "question", 1300, 450, 180, 0.2, mv="wig", c="red"), T(13, 1300, 700, 60, "为啥保温？", c="ink", d=0.4))
bd(13.5, thermos(13.5, 600, 600, 0.0), arr(13.5, 1050, 450, 730, 450, c="ink", d=0.4), BIG(13.5, 1350, 450, "真空", c="muted", d=0.3, s=130), T(13.5, 1350, 650, 56, "夹层", c="ink", d=0.6))
bd(14, gpu(14, 600, 620, 1.0, 0.0, hot=True), arr(14, 800, 620, 1100, 620, c="red", d=0.2), cross(14, 1250, 620, d=0.5), T(14, 1250, 350, 64, "靠碰", c="ink", d=0.3))
bd(14.5, fan(14.5, 500, 600, 120, 0.0), air(14.5, 700, 600, 4, 120, 0.2), cross(14.5, 1100, 600, d=0.6), T(14.5, 1350, 350, 64, "靠吹", c="ink", d=0.3))
bd(15, BIG(15, 960, 330, "-270 ℃", c="blue", d=0.0, s=130), thermo(15, 500, 800, 0.1, up=False), gpu(15, 1400, 700, 0.8, 0.3, hot=True))
bd(15.5, thermos(15.5, 960, 600, 0.0), T(15.5, 400, 400, 60, "冷", c="blue", d=0.2), arr(15.5, 450, 500, 760, 550, c="blue", d=0.3), cross(15.5, 700, 650, d=0.7), T(15.5, 1450, 400, 60, "碰不到", c="red", d=0.6))
bd(16, gpu(16, 700, 620, 1.1, 0.0, mood="o", hot=True), ic(16, "question", 1350, 450, 180, 0.2, mv="wig", c="red"), T(16, 1350, 700, 60, "还剩哪条路？", c="ink", d=0.4))
bd(16.5, gpu(16.5, 960, 560, 0.9, 0.0), rays(16.5, 960, 560, 170, 8, 0.2), BIG(16.5, 960, 960, "发光", c="red", d=0.5, s=90))
bd(17, ic(17, "eye", 500, 450, 180, 0.0, mv="wig"), cross(17, 500, 450, d=0.3), rays(17, 1250, 550, 120, 6, 0.2), ic(17, "flame", 1250, 550, 130, 0.1, mv="wig", c="red"), T(17, 960, 900, 56, "看不见的红外光", c="red", d=0.4))
bd(17.5, man(17.5, 700, 600, 1.6, 0.0), rays(17.5, 700, 520, 200, 6, 0.2), man(17.5, 1300, 600, 1.6, 0.1), rays(17.5, 1300, 520, 200, 6, 0.4))
bd(19, gpu(19, 600, 600, 0.9, 0.0), rays(19, 600, 600, 170, 6, 0.1), BIG(19, 1350, 450, "热辐射", c="red", d=0.3, s=120))
bd(19.5, sat(19.5, 960, 450, 150, 0.0), rays(19.5, 960, 450, 120, 6, 0.3), T(19.5, 960, 800, 64, "唯一的出路", c="red", d=0.5), check(19.5, 1350, 800, d=0.7))
bd(20, BIG(20, 960, 360, "反转二", c="red", d=0.0, s=150), gpu(20, 450, 700, 0.7, 0.2, mood="sad"), ic(20, "flame", 1470, 650, 140, 0.4, mv="wig", c="red"))
bd(20.5, P(20.5, "M300,400 L1620,400 M300,800 L1620,800", c="ink", w=8), R(20.5, 900, 400, 120, 170, c="ink", fill="muted"), R(20.5, 900, 630, 120, 170, c="ink", fill="muted"), air(20.5, 600, 600, 5, 300, 0.2), BIG(20.5, 960, 250, "窄得吓人", c="red", d=0.3, s=100))
bd(21, sat(21, 960, 500, 180, 0.0), T(21, 960, 250, 64, "国际空间站", c="ink", d=0.2), T(21, 960, 800, 56, "好几大片散热板", c="blue", d=0.5))
bd(21.5, BIG(21.5, 960, 350, "≈ 70 千瓦", c="red", d=0.0, s=140), T(21.5, 960, 520, 50, "据 NASA 资料", c="muted", d=0.2), panel(21.5, 300, 700, 500, 140, 0.3), panel(21.5, 1120, 700, 500, 140, 0.4))
bd(22, BIG(22, 960, 300, "70 千瓦 = ?", c="ink", d=0.0, s=110), gpu(22, 600, 700, 0.6, 0.2), gpu(22, 960, 700, 0.6, 0.3), gpu(22, 1320, 700, 0.6, 0.4))
bd(22.5, BIG(22.5, 1300, 400, "≈ 100 块", c="red", d=0.1, s=140), T(22.5, 1300, 600, 50, "估算", c="muted", d=0.2),
   [gpu(22.5, 300 + 160 * (q % 4), 400 + 230 * (q // 4), 0.4, 0.1 * q) for q in range(8)])
bd(23, ic(23, "building", 500, 600, 260, 0.0, mv="bob"), BIG(23, 1300, 400, "几十万块", c="red", d=0.2, s=130), bar(23, 1150, 900, 80, 100, "muted", 0.4), bar(23, 1300, 900, 80, 380, "red", 0.5))
bd(23.5, [gpu(23.5, 260 + 200 * (q % 8), 330 + 260 * (q // 8), 0.4, 0.05 * q, mood="sad") for q in range(16)], T(23.5, 960, 920, 56, "散不掉！", c="red", d=0.6))
bd(24, gpu(24, 700, 620, 1.0, 0.0, mood="o", shake=True), ic(24, "question", 1350, 450, 180, 0.2, mv="wig", c="red"), T(24, 1350, 700, 64, "怎么办？", c="ink", d=0.3))
bd(24.5, panel(24.5, 300, 500, 600, 160, 0.0, c="red"), thermo(24.5, 1200, 800, 0.2), BIG(24.5, 1500, 400, "更烫", c="red", d=0.3, s=120), ic(24.5, "flame", 600, 400, 120, 0.4, mv="wig", c="red"))
bd(25, T(25, 960, 260, 70, "发光散热的规律", c="ink", d=0.0), rays(25, 600, 600, 90, 6, 0.2), rays(25, 1300, 600, 120, 8, 0.4), ic(25, "flame", 1300, 600, 120, 0.3, mv="wig", c="red"))
bd(25.5, BIG(25.5, 700, 380, "温度 ×2", c="blue", d=0.0, s=110), arr(25.5, 1000, 380, 1200, 380, c="ink", d=0.2), BIG(25.5, 1450, 380, "×16", c="red", d=0.4, s=150),
   bar(25.5, 600, 900, 100, 30, "blue", 0.5), bar(25.5, 1400, 900, 100, 400, "red", 0.7))
bd(26, BIG(26, 960, 360, "T⁴", c="red", d=0.0, s=160), T(26, 960, 560, 60, "四次方定律", c="ink", d=0.2), ic(26, "sun", 500, 750, 140, 0.3, mv="spin", c="gold"), ic(26, "thermometer", 1400, 750, 150, 0.4, mv="wig", c="red"))
bd(26.5, BIG(26.5, 960, 380, "T×T×T×T", c="red", d=0.0, s=120), bar(26.5, 500, 900, 80, 40, "red", 0.2), bar(26.5, 750, 900, 80, 90, "red", 0.4), bar(26.5, 1000, 900, 80, 200, "red", 0.6), bar(26.5, 1250, 900, 80, 380, "red", 0.8))
bd(27, gpu(27, 700, 620, 1.1, 0.0, mood="sad", hot=True, shake=True), T(27, 1350, 450, 70, "显卡怕烫", c="red", d=0.3), thermo(27, 1350, 900, 0.4))
bd(27.5, gpu(27.5, 600, 620, 1.0, 0.0, mood="sad", shake=True), BIG(27.5, 1350, 450, "热不起来", c="red", d=0.2, s=110), cross(27.5, 1350, 650, d=0.5))
bd(29, sat(29, 960, 500, 160, 0.0), BIG(29, 960, 250, "巨大", c="blue", d=0.3, s=110), T(29, 960, 800, 56, "散热板", c="blue", d=0.5))
bd(29.5, sat(29.5, 960, 450, 140, 0.0), panel(29.5, 150, 650, 600, 140, 0.4), panel(29.5, 1170, 650, 600, 140, 0.5), T(29.5, 960, 900, 60, "一对对翅膀", c="blue", d=0.6))
bd(31, BIG(31, 960, 360, "反转三", c="red", d=0.0, s=150), sun(31, 450, 650, 200, 0.2), ic(31, "flame", 1470, 650, 140, 0.4, mv="wig", c="red"))
bd(31.5, sun(31.5, 500, 500, 240, 0.0), BIG(31.5, 1300, 450, "帮倒忙", c="red", d=0.3, s=120), arr(31.5, 700, 500, 1000, 600, c="gold", d=0.4))
bd(32, sun(32, 400, 400, 200, 0.0), ic(32, "cloud", 900, 400, 160, 0.2, mv="bob", c="blue"), cross(32, 900, 400, d=0.4), sat(32, 1400, 700, 130, 0.3, wings=False))
bd(32.5, sun(32.5, 400, 450, 200, 0.0), arr(32.5, 550, 450, 900, 550, c="gold", d=0.2), thermo(32.5, 1050, 850, 0.3), BIG(32.5, 1500, 450, "100多度", c="red", d=0.4, s=110))
bd(33, sun(33, 350, 450, 200, 0.0), panel(33, 900, 450, 500, 150, 0.2, tilt=True), T(33, 1150, 250, 60, "侧着身子", c="blue", d=0.3))
bd(33.5, sun(33.5, 350, 450, 200, 0.0), sat(33.5, 1300, 500, 130, 0.1), T(33.5, 1300, 850, 64, "躲着太阳", c="blue", d=0.4))
bd(34, ic(34, "rocket", 500, 550, 200, 0.0, mv="bob"), T(34, 1300, 350, 70, "那马斯克图什么？", c="ink", d=0.2), ic(34, "question", 1300, 620, 150, 0.4, mv="wig", c="red"))
bd(34.5, sun(34.5, 960, 480, 300, 0.0), BIG(34.5, 960, 850, "图的就是太阳", c="gold", d=0.3, s=100), star(34.5, 500, 400, 0.4, r=40), star(34.5, 1420, 400, 0.6, r=40))
bd(35, ic(35, "globe", 960, 600, 260, 0.0, mv="spin"), sat(35, 960, 300, 110, 0.2, wings=False), sun(35, 1600, 400, 160, 0.3),
   T(35, 400, 300, 56, "合适的轨道", c="blue", d=0.3))
bd(35.5, ic(35.5, "moon", 500, 450, 160, 0.0, mv="bob"), cross(35.5, 500, 450, d=0.2), ic(35.5, "cloud", 1000, 450, 160, 0.1, mv="bob", c="blue"), cross(35.5, 1000, 450, d=0.4),
   sun(35.5, 1500, 450, 180, 0.3), check(35.5, 1500, 700, d=0.6))
bd(36, sun(36, 450, 450, 200, 0.0), panel(36, 650, 400, 500, 150, 0.2, c="blue"), arr(36, 1200, 480, 1450, 480, c="gold", d=0.5), ic(36, "battery", 1600, 480, 140, 0.6, mv="wig"))
bd(36.5, ic(36.5, "map_pin", 500, 500, 180, 0.0, mv="bob", c="red"), cross(36.5, 500, 750, d=0.3), ic(36.5, "water", 1400, 500, 180, 0.1, mv="wig", c="blue"), cross(36.5, 1400, 750, d=0.5),
   T(36.5, 960, 280, 64, "不抢地、不抢水", c="green", d=0.4))
bd(38, calc(38, 960, 500, 0.0), ic(38, "battery", 600, 380, 150, 0.2, mv="bob"), ic(38, "flame", 1320, 380, 150, 0.3, mv="wig", c="red"), T(38, 960, 250, 64, "一笔账", c="ink", d=0.1))
bd(38.5, calc(38.5, 960, 500, 0.0), T(38.5, 600, 360, 56, "省下的电", c="green", d=0.2), T(38.5, 1320, 360, 56, "散热的麻烦", c="red", d=0.4), ic(38.5, "question", 960, 880, 110, 0.5, mv="wig", c="red"))
bd(39, BIG(39, 960, 330, "友情提示", c="blue", d=0.0, s=130), T(39, 960, 520, 60, "2029：马斯克的预测", c="ink", d=0.2), ic(39, "rocket", 500, 750, 150, 0.3, mv="bob"), ic(39, "magnifier", 1400, 750, 150, 0.4, mv="wig"))
bd(39.5, sat(39.5, 960, 450, 140, 0.0), T(39.5, 960, 780, 60, "还没人建成大型机房", c="red", d=0.3), cross(39.5, 1500, 450, d=0.5))
bd(40, BIG(40, 960, 350, "≈ 100 块", c="ink", d=0.0, s=120), T(40, 960, 550, 60, "估算", c="muted", d=0.2), gpu(40, 500, 750, 0.6, 0.3), gpu(40, 1420, 750, 0.6, 0.4))
bd(40.5, BIG(40.5, 960, 350, "×16", c="red", d=0.0, s=130), T(40.5, 960, 550, 60, "物理规律，不是公司方案", c="ink", d=0.2), ic(40.5, "atom", 500, 750, 150, 0.3, mv="spin"), ic(40.5, "building", 1420, 750, 150, 0.4, mv="bob"), cross(40.5, 1420, 750, d=0.6))
bd(41, gpu(41, 700, 620, 1.0, 0.0, mood="o", hot=True), ic(41, "question", 1350, 400, 180, 0.2, mv="wig", c="red"), T(41, 1350, 650, 60, "凭啥会热死？", c="red", d=0.3))
bd(41.5, thermos(41.5, 960, 600, 0.0), T(41.5, 450, 400, 56, "冷碰不到", c="blue", d=0.3), T(41.5, 1480, 400, 56, "热甩不出", c="red", d=0.5), rays(41.5, 960, 600, 300, 6, 0.6, c="red"))
bd(42, thermos(42, 700, 600, 0.0), BIG(42, 1400, 400, "最大的保温瓶", c="blue", d=0.2, s=90), ic(42, "globe", 1400, 700, 160, 0.3, mv="spin"))
bd(42.5, thermos(42.5, 650, 600, 0.0, inner="gold"), gpu(42.5, 650, 600, 0.45, 0.4, mood="o"), BIG(42.5, 1400, 450, "一杯热茶", c="red", d=0.5, s=110), star(42.5, 1400, 700, 0.6, r=40))

bd(18, man(18, 600, 600, 1.6, 0.0), ic(18, "moon", 1400, 300, 120, 0.1, mv="bob"), rays(18, 600, 520, 200, 6, 0.2), T(18, 1300, 600, 64, "黑夜里也在发光", c="red", d=0.3))
bd(18.5, ic(18.5, "lens", 500, 500, 200, 0.0, mv="wig"), arr(18.5, 650, 500, 950, 500, c="red", d=0.2), man(18.5, 1300, 550, 1.4, 0.3), R(18.5, 1180, 380, 240, 400, c="red", sw=6), T(18.5, 960, 900, 56, "热成像", c="red", d=0.4))
bd(28, gpu(28, 700, 620, 1.1, 0.0, mood="sad", shake=True), T(28, 1350, 400, 70, "小芯表示：", c="blue", d=0.2), ic(28, "question", 1350, 650, 140, 0.3, mv="wig", c="red"))
bd(28.5, gpu(28.5, 600, 620, 1.0, 0.0, mood="o"), fan(28.5, 1250, 550, 130, 0.2, rpm=300), T(28.5, 1250, 850, 60, "只想要一台风扇", c="blue", d=0.4), star(28.5, 1600, 350, 0.5, r=36))
bd(30, sat(30, 960, 450, 150, 0.0), T(30, 960, 800, 64, "白色大板子 = 散热板", c="blue", d=0.3))
bd(30.5, sun(30.5, 450, 450, 180, 0.0), panel(30.5, 700, 600, 400, 140, 0.2, c="gold"), T(30.5, 900, 850, 56, "这是太阳能板", c="gold", d=0.3), panel(30.5, 1250, 600, 400, 140, 0.4, c="paper"), T(30.5, 1450, 850, 56, "这才是散热板", c="blue", d=0.5))
bd(37, ic(37, "building", 600, 550, 240, 0.0, mv="bob"), pipe(37, 750, 600, 1250, 0.2), ic(37, "water", 1400, 550, 180, 0.3, mv="wig", c="blue"))
bd(37.5, ic(37.5, "water", 600, 550, 200, 0.0, mv="wig", c="blue"), bar(37.5, 1150, 900, 80, 150, "blue", 0.4), bar(37.5, 1300, 900, 80, 260, "blue", 0.5), BIG(37.5, 1300, 450, "大量的水", c="blue", d=0.3, s=110))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"2029": "二零二九", "2028": "二零二八", "AI": "A I", "NASA": "纳萨"})
