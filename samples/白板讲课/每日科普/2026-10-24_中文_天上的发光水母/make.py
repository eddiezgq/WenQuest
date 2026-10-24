"""每日科普 2026-10-24（中文）：《天上为什么飘过一只发光水母？》
新闻：2026-10-23 18:15，长征六号改运载火箭在太原卫星发射中心发射遥感五十号03星，成功；长征系列第672次飞行（澎湃新闻 34325514）。
晋冀鲁豫等地网友拍到“火箭云”“夜光水母”，朋友圈刷屏（澎湃 34323778）；知乎问题“10 月 23 日北方多地出现火箭云，你看到了吗？这是什么原理？”；
新浪财经 2026-10-24“火箭途经大连上空”；新华社/微博“周末抬头，看见火箭云在泰山上空画了个圈”。卫星用途：国土普查、农作物估产、防灾减灾（澎湃）。
教科书：日落后地面进入地球影子，高处仍被阳光照着；太阳落到地平线下 θ 度时，影子顶高约 h ≈ R(1/cosθ − 1)；
高处看得远：能看到 h 高的东西的最远距离约 √(2Rh)；高空近真空，尾焰没有空气约束会向四周猛烈膨胀，水汽冻成冰晶散射阳光。
我们的估算（片中说是估算）：太原 10 月 23 日日落约 17:58，18:15 时太阳在地平线下约 4 度 → 影子顶约 15 公里；
200 公里高 → 约 1,600 公里外可见；太原—大连直线约 800 公里。角色：小箭（会眨眼的火箭）。梗：我这儿太阳还没落。
    python3 make.py <kokoro 模型目录> | --boards-only | --fake   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("10月23日傍晚，北方好几个省的人，|同时看见天上飘过一只发光的大水母。", "On the evening of October 23rd, people across northern China | all saw a glowing jellyfish drift across the sky."),
 ("它不是外星人，|是一枚火箭。", "It wasn't aliens. | It was a rocket."),
 ("今天的问题：太阳都下山了，|火箭的尾巴为什么还会发光？", "Today's question: the sun had already set, | so why was the rocket's trail glowing?"),
 ("认识一下小箭。|一枚刚出门上班的火箭。", "Meet Archie. | A rocket heading off to work."),
 ("18点15分，长征六号改火箭|从山西的太原卫星发射中心起飞。", "At 6:15 p.m., a Long March 6 rocket | lifted off from the Taiyuan launch center in Shanxi."),
 ("它要把遥感五十号03星|送上太空。", "Its job: carry the Yaogan-50 03 satellite | into space."),
 ("这颗卫星的活儿，|是看国土、估产量、帮着防灾减灾。", "The satellite's work: | surveying land, estimating crops, helping with disasters."),
 ("这是长征系列火箭的|第672次飞行。", "It was the Long March family's | 672nd flight."),
 ("那天傍晚，山西、河北、山东、河南，|好多人的朋友圈都被刷屏了。", "That evening, in Shanxi, Hebei, Shandong and Henan, | social feeds were flooded."),
 ("有人说像水母，|有人说像一盏太空灯笼。", "Some said jellyfish. | Some said a space lantern."),
 ("原因一：太阳下山，|只是对你下山。", "Reason one: the sun sets | only for you."),
 ("你站在地上，已经进了地球的影子；|可越往高处，太阳落得越晚。", "On the ground, you're already in Earth's shadow. | But the higher you go, the later the sun sets."),
 ("就像傍晚的高楼：|楼下黑了，楼顶还亮着。", "Like a tall building at dusk: | dark at the bottom, still lit at the top."),
 ("火箭飞到上百公里高，|那里还是大白天。", "A rocket a hundred kilometers up | is still in broad daylight."),
 ("我们粗算一下：那时太阳落到地平线下4度左右，|地球影子的顶，只有十几公里高。", "Our rough math: the sun was about 4 degrees below the horizon, | so Earth's shadow only reached about 15 kilometers up."),
 ("比这高的东西，|全都还被太阳照着。", "Anything higher than that | was still in sunshine."),
 ("所以天是黑的，|火箭的尾巴却被阳光点亮。", "So the sky was dark, | but the rocket's trail was lit by the sun."),
 ("就像黑屋子里，|一束光照亮了飘着的灰尘。", "Like a dark room | where a sunbeam lights up floating dust."),
 ("原因二，最反直觉：|为什么是一只大水母，不是一条细线？", "Reason two, the weird one: | why a giant jellyfish, not a thin line?"),
 ("在地面附近，空气很稠，|尾焰被空气按住，只是细细一条。", "Near the ground, the air is thick. | It holds the exhaust into a narrow trail."),
 ("可到了一百多公里高，|空气稀得差不多是真空。", "But a hundred-plus kilometers up, | the air is so thin it's nearly a vacuum."),
 ("没有空气按着，|喷出来的气就往四面八方猛地散开。", "With nothing holding it back, | the exhaust bursts out in every direction."),
 ("就像拧开一瓶摇过的汽水：|气一下子全冲出来。", "Like opening a shaken soda: | the gas rushes out all at once."),
 ("这一团气，能胀成好几公里宽。|这是估算，要看当时的高度。", "That cloud can swell to several kilometers wide. | That's an estimate; it depends on the altitude."),
 ("气里的水汽一冷，就冻成小冰晶，|把阳光散射出来。", "The water vapor freezes into tiny ice crystals | that scatter the sunlight."),
 ("所以亮的不是火，|是被太阳照亮的冰雾。", "So the glow isn't fire. | It's sunlit ice fog."),
 ("原因三：为什么好几个省都看得到？|因为它太高了。", "Reason three: why could several provinces see it? | Because it was so high."),
 ("站得越高，看得越远，|这是因为地球是圆的。", "The higher something is, the farther it can be seen, | because Earth is round."),
 ("我们粗算一下：两百公里高的东西，|一千多公里外都看得见。", "Our rough math: something 200 kilometers up | can be seen from over 1,000 kilometers away."),
 ("从太原到大连，|直线大约八百公里。", "From Taiyuan to Dalian | is about 800 kilometers in a straight line."),
 ("所以大连的网友，|也拍到了它。", "So people in Dalian | caught it on camera too."),
 ("还得赶上刚刚好的时间：|太早，天太亮，看不出来。", "And the timing has to be just right: | too early, and the sky is too bright."),
 ("太晚，连高空也进了地球的影子。|太原那天日落大约在17点58分。", "Too late, and even the high sky falls into shadow. | Sunset in Taiyuan that day was around 5:58."),
 ("日落后一刻钟起飞，|地上黑了，天上还亮，正好。", "Liftoff a quarter hour after sunset: | dark ground, bright sky. Perfect."),
 ("反转：同样的道理，|你其实天天见。", "Plot twist: you see the same thing | almost every day."),
 ("太阳下山后，|飞机拉的白线还亮一会儿。", "After sunset, | a plane's contrail keeps glowing for a while."),
 ("天黑了，|远处的山顶还被照得金黄。", "After dark, | distant mountaintops still glow gold."),
 ("天黑后一两个小时，|你常能看到一颗亮点慢慢划过，那是卫星。", "An hour or two after dark, | you can often spot a slow moving dot. That's a satellite."),
 ("它们都在高处，|还泡在阳光里。", "They're all up high, | still bathing in sunlight."),
 ("友情提示：火箭云很美，|可过一会儿，就慢慢散开了。", "Friendly fine print: rocket clouds are beautiful, | but they fade before long."),
 ("想看下一只？|留意日落后不久的发射预告。", "Want to see the next one? | Watch for launches scheduled just after sunset."),
 ("然后往发射场的方向看，|离几百公里也没关系。", "Then look toward the launch site, | even from hundreds of kilometers away."),
 ("小箭已经下班了，|卫星送到了。", "Archie has clocked out. | The satellite was delivered."),
 ("下次它再在傍晚出门，|记得抬头。", "Next time it heads out at dusk, | look up."),
 ("那只发光水母，是高空在跟你说：|我这儿，太阳还没落呢。", "That glowing jellyfish is the sky telling you: | up here, the sun hasn't set yet."),
]
TITLE = {"zh": "天上为什么飘过一只发光水母？", "en": "Why Was There a Glowing Jellyfish in the Sky?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 900, 0.5, r=16)
    B.append(E)


def jian(a, x, y, k=1.0, mood="happy", d=None, fire=True):
    """小箭：圆鼻子的火箭，有脸、两片尾翼，尾巴的火苗一直在抖。"""
    i = uid("jn") + "_"
    f = i + "f"
    E = [P(a, f"M{x},{y - 170 * k} Q{x + 70 * k},{y - 110 * k} {x + 60 * k},{y + 90 * k} L{x - 60 * k},{y + 90 * k} Q{x - 70 * k},{y - 110 * k} {x},{y - 170 * k} Z",
           c="ink", w=6, fill="muted", idp=i),
         P(a, f"M{x - 60 * k},{y + 30 * k} L{x - 110 * k},{y + 110 * k} L{x - 60 * k},{y + 90 * k} M{x + 60 * k},{y + 30 * k} L{x + 110 * k},{y + 110 * k} L{x + 60 * k},{y + 90 * k}",
           c="red", w=6, fill="red", idp=i),
         O(a, x - 22 * k, y - 50 * k, 10 * k, c="ink", fill="ink", idp=i), O(a, x + 22 * k, y - 50 * k, 10 * k, c="ink", fill="ink", idp=i)]
    m = {"happy": f"M{x - 25 * k},{y - 15 * k} Q{x},{y + 10 * k} {x + 25 * k},{y - 15 * k}",
         "o": f"M{x - 10 * k},{y - 10 * k} a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0",
         "sad": f"M{x - 25 * k},{y + 5 * k} Q{x},{y - 18 * k} {x + 25 * k},{y + 5 * k}"}[mood]
    E += [P(a, m, c="ink", w=5, idp=i), bob(a, i, 8 * k, 1.3)]
    if fire:
        E += [P(a, f"M{x - 40 * k},{y + 95 * k} Q{x},{y + 260 * k} {x + 40 * k},{y + 95 * k} Z", c="gold", w=5, fill="gold", idp=f),
              wig(a, f, (x, y + 95 * k), 14, 3.0), bob(a, f, 8 * k, 1.3)]
    if d is not None:
        E.append(pop(a, [i, f] if fire else [i], d))
    return E, i


def jelly(a, x, y, k=1.0, d=0.0, c="blue"):
    """发光水母：一个圆顶 + 几根飘带（尾焰云），圆顶慢慢胀大，飘带扭动。"""
    i = uid("jl")
    t = i + "t"
    E = [P(a, f"M{x - 160 * k},{y} Q{x - 160 * k},{y - 180 * k} {x},{y - 180 * k} Q{x + 160 * k},{y - 180 * k} {x + 160 * k},{y} Q{x},{y + 40 * k} {x - 160 * k},{y} Z",
           c=c, w=6, fill=c, idp=i),
         P(a, " ".join(f"M{x + (q - 2) * 60 * k},{y + 10 * k} q{30 * k},{60 * k} 0,{120 * k} q{-30 * k},{60 * k} 0,{120 * k}" for q in range(5)), c=c, w=5, idp=t),
         pop(a, [i, t], d), {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "both", "from": 0.6, "to": 1.0, "pivot": [x, y], "dur": 1.6, "delay": d + 0.2},
         wig(a, t, (x, y), 8, 1.2), bob(a, i, 6 * k, 0.8)]
    return E, i


def sun(a, x, y, s=200, d=0.0):
    i = uid("sun")
    return [{"t": "icon", "at": a, "id": i, "name": "sun", "x": x, "y": y, "size": s, "c": "gold"}, pop(a, i, d), spin(a, i, (x, y), 10)]


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def person(a, x, y, k=1.0, c="ink", look=False):
    i = uid("ps")
    E = [O(a, x, y - 130 * k, 40 * k, c=c, idp=i), P(a, f"M{x},{y - 90 * k} L{x},{y + 40 * k} M{x - 60 * k},{y - 30 * k} L{x},{y - 60 * k} L{x + 60 * k},{y - 30 * k} "
                                                      f"M{x},{y + 40 * k} L{x - 40 * k},{y + 130 * k} M{x},{y + 40 * k} L{x + 40 * k},{y + 130 * k}", c=c, w=6, idp=i),
         bob(a, i, 5, 1.0), wig(a, i, (x, y + 130 * k), 4, 1.2)]
    if look:
        E += [P(a, f"M{x + 20 * k},{y - 70 * k} L{x + 90 * k},{y - 160 * k}", c=c, w=6, idp=(h := uid("hd"))), wig(a, h, (x + 20 * k, y - 70 * k), 8, 1.0)]
    return E, i


def earth(a, y=820, c="blue", night=False):
    i = uid("ea")
    E = [P(a, f"M100,{y + 140} Q960,{y - 120} 1820,{y + 140}", c=c, w=7, idp=i), bob(a, i, 3, 0.4)]
    if night:
        n = uid("nt")
        E += [P(a, f"M100,{y + 150} Q960,{y - 100} 1820,{y + 150} L1820,1000 L100,1000 Z", c="ink", w=2, fill="ink", idp=n), pop(a, n, 0.0), pulse(a, n, 0.6)]
    return E


def town(a, x, y, n=4, d=0.0, lit=0):
    E = []
    for q in range(n):
        h = 80 + 40 * (q % 3)
        i = uid("tw")
        E += [R(a, x + 90 * q, y - h, 70, h, c="ink", fill="gold" if q < lit else "muted", idp=i), pop(a, i, d + 0.06 * q), bob(a, i, 3, 0.6 + 0.1 * q)]
    return E


def ray(a, x0, y0, x1, y1, d=0.0, c="gold"):
    return arr(a, x0, y0, x1, y1, c=c, d=d, dur=0.4)


def trail(a, x0, y0, x1, y1, d=0.0, c="muted", w=10):
    i = uid("tr")
    return [P(a, f"M{x0},{y0} Q{(x0 + x1) / 2 + 80},{(y0 + y1) / 2} {x1},{y1}", c=c, w=w, idp=i),
            {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x0, y0], "dur": 1.0, "delay": d}, pulse(a, i, d + 1.1)]


def phone(a, x, y, s=160, d=0.0):
    return icon(a, "phone", x, y, s, d, mv="wig")


def plane(a, x, y, k=1.0, d=0.0):
    i = uid("pl")
    return [P(a, f"M{x - 80 * k},{y} L{x + 80 * k},{y} M{x - 10 * k},{y} L{x - 40 * k},{y - 60 * k} M{x - 10 * k},{y} L{x - 40 * k},{y + 60 * k} M{x - 80 * k},{y} L{x - 100 * k},{y - 30 * k}",
              c="ink", w=7, idp=i), pop(a, i, d), bob(a, i, 6, 1.0)], i


def mountain(a, x, y, k=1.0, d=0.0, lit=True):
    i, s = uid("mt"), uid("cap")
    E = [P(a, f"M{x - 260 * k},{y} L{x},{y - 300 * k} L{x + 260 * k},{y} Z", c="ink", w=6, fill="muted", idp=i), pop(a, i, d), bob(a, i, 2, 0.5)]
    if lit:
        E += [P(a, f"M{x - 70 * k},{y - 220 * k} L{x},{y - 300 * k} L{x + 70 * k},{y - 220 * k} Z", c="gold", w=6, fill="gold", idp=s), pop(a, s, d + 0.4), pulse(a, s, d + 0.8)]
    return E


def smoke(a):
    E = []
    for q in range(5):
        sm = uid("sm")
        E += [O(a, 800 + 80 * q, 820, 30, c="muted", fill="muted", idp=sm), pop(a, sm, 0.2 + 0.05 * q), sh(a, sm, (q - 2) * 60, -40, 0.4, 1.0)]
    return E


# 0 傍晚北方多省
j_, ji = jelly(0, 960, 380, 1.4, 0.0)
bd(0, j_, earth(0, 820, night=True), [e for q in range(3) for e in person(0, 500 + 450 * q, 820, 0.4, look=True)[0]], BIG(0, 400, 250, "10月23日", c="blue", d=0.3, s=90))
# 0.5 发光的大水母
j_, ji = jelly(0.5, 960, 480, 2.0, 0.0)
bd(0.5, j_, [pulse(0.5, ji, 0.8, 0.8)], T(0.5, 960, 150, 64, "发光的大水母？！", c="blue", d=0.4))
# 1 不是外星人
uf = uid("ufo")
bd(1, [O(1, 960, 480, 160, c="green", fill="green", idp=uf), P(1, "M760,520 L1160,520", c="ink", w=7, idp=uf), pop(1, uf, 0.0), wig(1, uf, (960, 480), 10, 1.5)],
   cross(1, 960, 480, d=0.5), T(1, 960, 800, 64, "外星人？", c="green", d=0.2))
# 1.5 是火箭
j_, ji = jian(1.5, 960, 560, 1.6, d=0.0)
bd(1.5, j_, [sh(1.5, [ji, ji + "f"], 0, -80, 0.4, 0.8)], BIG(1.5, 1450, 400, "火箭！", c="red", d=0.3, s=130))
# 2 今天的问题
s_ = sun(2, 1500, 500, 200, 0.0)
bd(2, s_, [sh(2, s_[0]["id"], 0, 400, 0.2, 1.4)], earth(2, 780), T(2, 700, 300, 64, "太阳下山了……", c="red", d=0.3))
# 2.5 尾巴为什么发光
j_, ji = jian(2.5, 700, 380, 1.0, mood="o")
bd(2.5, j_, trail(2.5, 700, 900, 700, 520, d=0.2, c="blue"), icon(2.5, "question", 1300, 450, 260, 0.3, c="red", mv="wig"), T(2.5, 1300, 760, 56, "尾巴为什么亮？", c="red", d=0.5))
# 3 认识小箭
j_, ji = jian(3, 860, 520, 2.0, d=0.0)
bd(3, j_, BIG(3, 1500, 380, "小箭", c="red", d=0.4, s=150), [e for q in range(3) for e in star(3, 1400 + 110 * q, 600, 0.6 + 0.1 * q, r=30)])
# 3.5 出门上班
j_, ji = jian(3.5, 600, 600, 1.0)
bd(3.5, j_, icon(3.5, "clock", 1300, 450, 200, 0.2, mv="spin"), T(3.5, 1300, 720, 56, "上班去！", c="ink", d=0.4), [sh(3.5, [ji, ji + "f"], 0, -60, 0.6, 0.6)])
# 4 18:15
bd(4, BIG(4, 960, 380, "18:15", c="blue", d=0.1, s=170), icon(4, "clock", 500, 760, 160, 0.2, mv="spin"), jian(4, 1450, 760, 0.6, d=0.3)[0])
# 4.5 太原起飞
j_, ji = jian(4.5, 960, 700, 1.2)
bd(4.5, j_, [sh(4.5, [ji, ji + "f"], 0, -380, 0.3, 1.6)], T(4.5, 960, 940, 60, "长征六号改 · 太原卫星发射中心", c="ink", d=0.2), smoke(4.5))
# 5 遥感五十号03星
st = icon(5, "satellite", 1300, 450, 240, 0.0, mv="spin")
bd(5, st, jian(5, 600, 560, 1.0)[0], arr(5, 720, 420, 1150, 420, c="ink", d=0.3), T(5, 1300, 720, 56, "遥感五十号03星", c="blue", d=0.4))
# 5.5 送上太空
st = icon(5.5, "satellite", 960, 700, 160, 0.0, mv="spin")
bd(5.5, st, [sh(5.5, st[0]["id"], 0, -400, 0.2, 1.4)], earth(5.5, 860), T(5.5, 1450, 400, 60, "送上太空", c="blue", d=0.4))
# 6 卫星的活儿
bd(6, icon(6, "satellite", 960, 260, 160, 0.0, mv="spin"), icon(6, "magnifier", 960, 520, 160, 0.2, mv="wig"), earth(6, 820), T(6, 960, 700, 52, "低头看地", c="ink", d=0.4))
# 6.5 国土 估产 防灾
bd(6.5, icon(6.5, "map_pin", 450, 500, 200, 0.0, c="red"), icon(6.5, "water", 960, 500, 200, 0.2, c="green"), icon(6.5, "cloud", 1470, 500, 200, 0.4, c="blue", mv="wig"),
   T(6.5, 450, 720, 52, "看国土", d=0.1), T(6.5, 960, 720, 52, "估产量", c="green", d=0.3), T(6.5, 1470, 720, 52, "防灾", c="blue", d=0.5))
# 7 长征系列
E = []
for q in range(8):
    E += jian(7, 300 + 190 * q, 560, 0.45, d=0.06 * q)[0]
bd(7, E, T(7, 960, 260, 60, "长征系列", c="red", d=0.3))
# 7.5 第672次
bd(7.5, BIG(7.5, 960, 440, "第 672 次", c="red", d=0.1, s=160), jian(7.5, 400, 760, 0.6)[0], jian(7.5, 1520, 760, 0.6)[0])
# 8 四省
E = []
for q, nm in enumerate(["山西", "河北", "山东", "河南"]):
    E += [O(8, 450 + 340 * q, 500, 120, c="blue", fill="blue", idp=(pv := uid("pv"))), pop(8, pv, 0.1 * q), bob(8, pv, 6, 0.8 + 0.1 * q)] + T(8, 450 + 340 * q, 500, 52, nm, d=0.1 * q + 0.1)
bd(8, E, jelly(8, 960, 240, 0.4, 0.4)[0])
# 8.5 朋友圈刷屏
E = []
for q in range(5):
    p_ = phone(8.5, 400 + 280 * q, 560, 180, 0.08 * q)
    E += p_ + [sh(8.5, p_[0]["id"], 0, -60, 0.3 + 0.1 * q, 0.6)]
bd(8.5, E, T(8.5, 960, 860, 64, "朋友圈刷屏！", c="red", d=0.6))
# 9 像水母
bd(9, jelly(9, 700, 500, 1.2, 0.0)[0], T(9, 1350, 500, 64, "水母？", c="blue", d=0.3), [e for q in range(3) for e in star(9, 1250 + 100 * q, 700, 0.4 + 0.1 * q, r=24)])
# 9.5 灯笼
ln = uid("ln")
bd(9.5, [O(9.5, 960, 480, 180, c="red", fill="red", idp=ln), P(9.5, "M960,300 L960,220 M900,660 L1020,660 M960,660 L960,760", c="ink", w=6, idp=ln), pop(9.5, ln, 0.0),
         wig(9.5, ln, (960, 220), 8, 1.0)], T(9.5, 960, 900, 60, "太空灯笼？", c="red", d=0.3), icon(9.5, "moon", 1500, 300, 120, 0.4, c="gold"))
# 10 原因一
s_ = sun(10, 1450, 500, 200, 0.0)
bd(10, BIG(10, 960, 160, "原因一", c="red", d=0.1, s=90), s_, [sh(10, s_[0]["id"], 0, 300, 0.3, 1.2)], earth(10, 780), person(10, 700, 720, 0.6)[0])
# 10.5 只是对你下山
ps, pp = person(10.5, 960, 640, 1.0)
bd(10.5, ps, sun(10.5, 1500, 760, 150, 0.0), arr(10.5, 1100, 400, 1000, 500, c="red", d=0.3), BIG(10.5, 600, 360, "只对你", c="red", d=0.4, s=110))
# 11 你在影子里
e2 = uid("e")
bd(11, [O(11, 700, 560, 260, c="blue", fill="blue", idp=e2), spin(11, e2, (700, 560), 6),
        P(11, "M700,300 L1800,330 L1800,790 L700,820 Z", c="ink", w=3, fill="ink", idp=(sd := uid("sd"))), pop(11, sd, 0.3), pulse(11, sd, 1.0)],
   sun(11, 200, 200, 120, 0.1), [e for q in range(3) for e in ray(11, 260, 260 + 100 * q, 440, 380 + 100 * q, d=0.2 + 0.1 * q)], T(11, 1300, 940, 52, "地球的影子", c="ink", d=0.5))
# 11.5 越高落得越晚
bd(11.5, earth(11.5, 860, night=True), [e for q in range(4) for e in ray(11.5, 200, 200 + 90 * q, 1700, 200 + 90 * q, d=0.1 * q)],
   arr(11.5, 960, 820, 960, 220, c="red", d=0.3, dur=0.8), T(11.5, 1400, 650, 56, "越高，日落越晚", c="red", d=0.5))
# 12 高楼
bd(12, icon(12, "building", 960, 560, 460, 0.0, mv="bob"), ray(12, 200, 300, 820, 360, d=0.2), sun(12, 160, 240, 100, 0.1), earth(12, 900, night=True))
# 12.5 楼下黑 楼顶亮
tp = uid("tp")
bd(12.5, [R(12.5, 800, 200, 320, 700, c="ink", fill="muted", idp=(bl := uid("bl"))), pop(12.5, bl, 0.0), bob(12.5, bl, 2, 0.5),
          R(12.5, 800, 200, 320, 140, c="gold", fill="gold", idp=tp), pop(12.5, tp, 0.3), pulse(12.5, tp, 0.8)],
   T(12.5, 1450, 260, 56, "楼顶：亮", c="gold", d=0.4), T(12.5, 1450, 820, 56, "楼下：黑", c="ink", d=0.6), sun(12.5, 300, 260, 120, 0.2))
# 13 上百公里高
j_, ji = jian(13, 960, 700, 0.6)
bd(13, j_, [sh(13, [ji, ji + "f"], 0, -460, 0.1, 1.6)], earth(13, 880, night=True), BIG(13, 1450, 380, "100+ 公里", c="blue", d=0.3, s=100))
# 13.5 大白天
j_, ji = jian(13.5, 1100, 380, 0.8)
bd(13.5, j_, sun(13.5, 300, 300, 200, 0.0), [e for q in range(3) for e in ray(13.5, 420, 240 + 60 * q, 960, 300 + 60 * q, d=0.2 + 0.1 * q)],
   T(13.5, 1100, 720, 60, "这儿还是大白天", c="gold", d=0.5), earth(13.5, 900, night=True))
# 14 粗算 4度
s_ = sun(14, 1500, 820, 140, 0.0)
bd(14, earth(14, 760), s_, [sh(14, s_[0]["id"], 0, 120, 0.2, 1.0)], BIG(14, 960, 380, "地平线下 ~4°", c="red", d=0.3, s=100), T(14, 960, 200, 48, "我们粗算", c="muted", d=0.1))
# 14.5 影子顶十几公里
bd(14.5, earth(14.5, 860, night=True), [P(14.5, "M100,700 Q960,560 1820,700", c="ink", w=6, idp=(sl := uid("sl"))), pop(14.5, sl, 0.1), wig(14.5, sl, (960, 600), 2, 0.6)],
   arr(14.5, 1500, 800, 1500, 640, c="red", d=0.3), BIG(14.5, 960, 340, "影子顶 ~15 公里", c="red", d=0.4, s=100))
# 15 比这高的
E = []
for q, (nm, y) in enumerate([("飞机", 620), ("火箭", 360), ("卫星", 200)]):
    E += T(15, 500 + 450 * q, y - 80, 48, nm, c="ink", d=0.1 + 0.2 * q)
E += plane(15, 500, 620, 0.8, 0.1)[0] + jian(15, 950, 360, 0.4, d=0.3)[0] + icon(15, "satellite", 1400, 200, 120, 0.5, mv="spin")
bd(15, E, earth(15, 880, night=True))
# 15.5 全都被照着
bd(15.5, sun(15.5, 260, 300, 200, 0.0), [e for q in range(4) for e in ray(15.5, 380, 220 + 80 * q, 1600, 220 + 80 * q, d=0.1 * q)], check(15.5, 1400, 700, d=0.6),
   T(15.5, 960, 700, 60, "全是阳光", c="gold", d=0.4))
# 16 天是黑的
bd(16, earth(16, 860, night=True), icon(16, "moon", 1500, 300, 160, 0.0, c="gold"), [e for q in range(5) for e in star(16, 300 + 250 * q, 300 + 80 * (q % 2), 0.1 * q, r=20)],
   T(16, 700, 500, 64, "天，黑了", c="ink", d=0.3))
# 16.5 尾巴被点亮
j_, ji = jian(16.5, 1300, 260, 0.5)
bd(16.5, j_, trail(16.5, 600, 900, 1260, 340, d=0.0, c="gold", w=14), sun(16.5, 200, 260, 120, 0.2), ray(16.5, 280, 280, 900, 500, d=0.5), earth(16.5, 900, night=True))
# 17 黑屋子
rm = uid("rm")
bd(17, [R(17, 300, 200, 1320, 700, c="ink", fill="ink", idp=rm), pop(17, rm, 0.0)], [P(17, "M300,300 L1100,800 L1250,700 L300,380 Z", c="gold", w=4, fill="gold", idp=(bmm := uid("b"))),
                                                                             pop(17, bmm, 0.3), pulse(17, bmm, 1.0)], T(17, 1350, 300, 52, "黑屋子", c="muted", d=0.2))
# 17.5 灰尘
E = []
for q in range(10):
    i = uid("ds")
    E += [O(17.5, 600 + 60 * q, 400 + 40 * (q % 4), 10, c="gold", fill="gold", idp=i), pop(17.5, i, 0.05 * q), bob(17.5, i, 12, 0.6 + 0.08 * q)]
bd(17.5, E, T(17.5, 960, 820, 60, "光里飘的灰尘", c="gold", d=0.5), sun(17.5, 260, 300, 120, 0.1))
# 18 原因二
bd(18, BIG(18, 960, 160, "原因二", c="red", d=0.1, s=90), jelly(18, 960, 560, 1.4, 0.2)[0], icon(18, "question", 1550, 450, 180, 0.4, c="red", mv="wig"))
# 18.5 水母 vs 细线
bd(18.5, jelly(18.5, 600, 480, 1.0, 0.0)[0], T(18.5, 960, 480, 80, "vs", c="ink", d=0.2), trail(18.5, 1350, 860, 1350, 260, d=0.3, c="muted", w=8),
   T(18.5, 960, 900, 56, "为什么不是一条线？", c="red", d=0.5))
# 19 空气很稠
E = []
for q in range(18):
    i = uid("air")
    E += [O(19, 300 + 90 * (q % 9), 300 + 120 * (q // 9), 18, c="blue", fill="blue", idp=i), pop(19, i, 0.02 * q), wig(19, i, (300 + 90 * (q % 9), 300), 6, 2.0)]
bd(19, E, T(19, 1500, 400, 56, "空气很稠", c="blue", d=0.3), jian(19, 1500, 700, 0.6)[0])
# 19.5 按住，细细一条
j_, ji = jian(19.5, 960, 300, 0.6)
bd(19.5, j_, [e for q in range(4) for e in arr(19.5, 600 + (q % 2) * 720, 500 + 100 * (q // 2), 900 + (q % 2) * 120, 500 + 100 * (q // 2), c="blue", d=0.1 * q)],
   trail(19.5, 960, 900, 960, 420, d=0.2, c="muted", w=8), T(19.5, 1450, 900, 52, "被按成一条", c="ink", d=0.5))
# 20 一百多公里高
j_, ji = jian(20, 960, 700, 0.6)
bd(20, j_, [sh(20, [ji, ji + "f"], 0, -400, 0.1, 1.4)], BIG(20, 1450, 400, "100+ 公里", c="blue", d=0.3, s=100), earth(20, 900))
# 20.5 差不多真空
E = []
for q in range(4):
    i = uid("air")
    E += [O(20.5, 400 + 380 * q, 400 + 150 * (q % 2), 16, c="blue", fill="blue", idp=i), pop(20.5, i, 0.1 * q), bob(20.5, i, 20, 0.5)]
bd(20.5, E, BIG(20.5, 960, 780, "≈ 真空", c="ink", d=0.3, s=130))
# 21 没有空气按着
j_, ji = jian(21, 960, 400, 0.7)
bd(21, j_, [e for q in range(8) for e in arr(21, 960, 620, 960 + 400 * [1, .7, 0, -.7, -1, -.7, 0, .7][q], 620 + 260 * [0, .7, 1, .7, 0, -.7, -1, -.7][q], c="gold", d=0.2 + 0.05 * q)])
# 21.5 四面八方
j_, ji = jelly(21.5, 960, 560, 1.8, 0.0)
bd(21.5, j_, T(21.5, 960, 130, 60, "砰！四面八方", c="red", d=0.3))
# 22 汽水
bt = uid("bt")
bd(22, [P(22, "M880,800 L880,500 Q880,420 930,380 L930,300 L990,300 L990,380 Q1040,420 1040,500 L1040,800 Z", c="green", w=7, fill="green", idp=bt), pop(22, bt, 0.0), wig(22, bt, (960, 800), 10, 3.0)],
   T(22, 1450, 500, 60, "摇一摇……", c="green", d=0.3), T(22, 450, 500, 60, "汽水", c="ink", d=0.1))
# 22.5 冲出来
E = []
for q in range(10):
    i = uid("fz")
    E += [O(22.5, 960, 320, 16 + 4 * (q % 3), c="blue", idp=i, sw=4), pop(22.5, i, 0.03 * q), sh(22.5, i, 380 * [1, .8, .3, -.3, -.8, -1, -.6, 0, .6, .9][q], -60 - 40 * (q % 4), 0.1 + 0.03 * q, 0.9)]
bd(22.5, [P(22.5, "M880,900 L880,600 Q880,520 930,480 L930,400 L990,400 L990,480 Q1040,520 1040,600 L1040,900 Z", c="green", w=7, fill="green", idp=(bt2 := uid("bt"))),
          pop(22.5, bt2, 0.0), wig(22.5, bt2, (960, 900), 4, 2.0)], E, T(22.5, 1450, 760, 60, "噗——", c="red", d=0.4))
# 23 好几公里宽
j_, ji = jelly(23, 960, 560, 2.2, 0.0)
bd(23, j_, arr(23, 600, 640, 1320, 640, c="red", d=0.3), arr(23, 1320, 640, 600, 640, c="red", d=0.3), BIG(23, 960, 180, "好几公里宽", c="red", d=0.4, s=100))
# 23.5 估算 看高度
bd(23.5, icon(23.5, "ruler", 600, 500, 240, 0.0, mv="wig"), T(23.5, 1250, 450, 64, "估算", c="muted", d=0.2), T(23.5, 1250, 620, 52, "要看高度", c="ink", d=0.4),
   jian(23.5, 1600, 760, 0.4)[0])
# 24 冻成冰晶
E = []
for q in range(8):
    i = uid("ic")
    x, y = 450 + 140 * q, 500 + 60 * (q % 3)
    E += [P(24, f"M{x - 30},{y} L{x + 30},{y} M{x},{y - 30} L{x},{y + 30} M{x - 20},{y - 20} L{x + 20},{y + 20} M{x - 20},{y + 20} L{x + 20},{y - 20}", c="blue", w=5, idp=i),
          pop(24, i, 0.08 * q), spin(24, i, (x, y), 40)]
bd(24, E, icon(24, "thermometer", 300, 760, 160, 0.2, c="blue", mv="wig"), T(24, 1100, 820, 56, "水汽 → 冰晶", c="blue", d=0.4))
# 24.5 散射阳光
bd(24.5, sun(24.5, 300, 300, 160, 0.0), ray(24.5, 400, 340, 860, 500, d=0.2), [e for q in range(5) for e in ray(24.5, 960, 520, 960 + 400 * [1, .7, 0, -.4, .9][q], 520 + 300 * [0, .7, 1, .8, -.6][q], d=0.4 + 0.08 * q)],
   T(24.5, 1400, 880, 52, "散射", c="gold", d=0.6))
# 25 不是火
bd(25, icon(25, "flame", 700, 500, 260, 0.0, c="red", mv="wig"), cross(25, 700, 500, d=0.4), jelly(25, 1350, 520, 0.9, 0.3)[0], T(25, 700, 780, 56, "不是火", c="red", d=0.2))
# 25.5 冰雾
j_, ji = jelly(25.5, 960, 500, 1.6, 0.0, c="gold")
bd(25.5, j_, sun(25.5, 250, 250, 120, 0.1), BIG(25.5, 1350, 140, "被照亮的冰雾", c="blue", d=0.3, s=90))
# 26 原因三
bd(26, BIG(26, 960, 160, "原因三", c="red", d=0.1, s=90), [e for q in range(4) for e in person(26, 450 + 340 * q, 760, 0.5, look=True)[0]], jelly(26, 960, 420, 0.6, 0.3)[0])
# 26.5 太高了
j_, ji = jelly(26.5, 960, 260, 0.6, 0.0)
bd(26.5, j_, [sh(26.5, [ji, ji + "t"], 0, -40, 0.4, 0.8)], earth(26.5, 860), arr(26.5, 1300, 820, 1300, 300, c="blue", d=0.3), BIG(26.5, 1500, 560, "太高了", c="red", d=0.4, s=100))
# 27 站得高看得远
ps, pp = person(27, 960, 640, 1.0, look=True)
bd(27, ps, [sh(27, pp, 0, -200, 0.3, 1.0)], icon(27, "eye", 1450, 400, 160, 0.2, mv="bob"), T(27, 960, 920, 56, "站得越高，看得越远", c="ink", d=0.4))
# 27.5 地球是圆的
bd(27.5, icon(27.5, "globe", 960, 520, 360, 0.0, c="blue", mv="spin"), arr(27.5, 600, 260, 1320, 260, c="red", d=0.3), T(27.5, 960, 900, 56, "因为地球是圆的", c="blue", d=0.4))
# 28 200公里
j_, ji = jelly(28, 960, 220, 0.5, 0.0)
bd(28, j_, earth(28, 860), arr(28, 960, 760, 960, 300, c="blue", d=0.2), BIG(28, 1400, 450, "200 公里", c="blue", d=0.3, s=110), T(28, 400, 300, 48, "我们粗算", c="muted", d=0.1))
# 28.5 一千多公里外
bd(28.5, earth(28.5, 760), jelly(28.5, 960, 260, 0.5, 0.0)[0], arr(28.5, 960, 320, 250, 800, c="gold", d=0.2), arr(28.5, 960, 320, 1670, 800, c="gold", d=0.3),
   BIG(28.5, 960, 940, "1,000+ 公里外", c="red", d=0.4, s=90))
# 29 太原到大连
d1, d2 = uid("c"), uid("c")
bd(29, [O(29, 450, 600, 30, c="red", fill="red", idp=d1), pop(29, d1, 0.0), pulse(29, d1, 0.4), O(29, 1450, 500, 30, c="blue", fill="blue", idp=d2), pop(29, d2, 0.3), pulse(29, d2, 0.7)],
   T(29, 450, 700, 52, "太原", c="red", d=0.1), T(29, 1450, 600, 52, "大连", c="blue", d=0.4), arr(29, 500, 590, 1400, 510, c="ink", d=0.5), jian(29, 450, 380, 0.4)[0])
# 29.5 800公里
bd(29.5, BIG(29.5, 960, 420, "≈ 800 公里", c="red", d=0.1, s=150), icon(29.5, "ruler", 500, 760, 150, 0.2, mv="wig"), icon(29.5, "car", 1400, 760, 180, 0.3, mv="wig"))
# 30 大连网友
ps, pp = person(30, 700, 700, 0.9, look=True)
bd(30, ps, phone(30, 840, 520, 120, 0.2), jelly(30, 1350, 330, 0.6, 0.3)[0], T(30, 1350, 800, 56, "大连", c="blue", d=0.4))
# 30.5 拍到了
p_ = phone(30.5, 960, 520, 340, 0.0)
bd(30.5, p_, jelly(30.5, 960, 520, 0.4, 0.3)[0], check(30.5, 1400, 520, d=0.6), T(30.5, 960, 860, 56, "咔嚓！", c="red", d=0.5))
# 31 刚刚好的时间
bd(31, icon(31, "clock", 960, 480, 300, 0.0, mv="spin"), T(31, 960, 820, 60, "时间要刚刚好", c="ink", d=0.3), sun(31, 400, 300, 120, 0.2))
# 31.5 太早，太亮
bd(31.5, sun(31.5, 700, 400, 260, 0.0), jelly(31.5, 1300, 400, 0.6, 0.3, c="muted")[0], icon(31.5, "eye", 1300, 700, 120, 0.4), T(31.5, 960, 880, 56, "太早：太亮，看不见", c="red", d=0.5))
# 32 太晚 高空也进影子
j_, ji = jelly(32, 960, 300, 0.6, 0.0, c="muted")
bd(32, earth(32, 860, night=True), j_, [P(32, "M100,250 L1820,250 L1820,500 L100,500 Z", c="ink", w=3, fill="ink", idp=(dk := uid("dk"))), pop(32, dk, 0.4), pulse(32, dk, 0.9)],
   T(32, 960, 640, 56, "太晚：高空也黑了", c="ink", d=0.5))
# 32.5 17:58
s_ = sun(32.5, 1400, 500, 180, 0.0)
bd(32.5, s_, [sh(32.5, s_[0]["id"], 0, 300, 0.2, 1.4)], earth(32.5, 780), BIG(32.5, 650, 380, "日落 ~17:58", c="red", d=0.3, s=100))
# 33 一刻钟后起飞
j_, ji = jian(33, 960, 700, 0.8)
bd(33, j_, [sh(33, [ji, ji + "f"], 0, -300, 0.4, 1.2)], icon(33, "clock", 400, 400, 180, 0.0, mv="spin"), BIG(33, 1450, 400, "+15 分钟", c="blue", d=0.3, s=100))
# 33.5 地上黑 天上亮 正好
bd(33.5, earth(33.5, 860, night=True), jelly(33.5, 960, 400, 1.0, 0.0, c="gold")[0], sun(33.5, 220, 300, 120, 0.1), check(33.5, 1550, 400, d=0.6),
   T(33.5, 1500, 600, 56, "正好！", c="green", d=0.5))
# 34 反转
bd(34, BIG(34, 960, 300, "反转", c="red", d=0.1, s=150), [e for q in range(3) for e in icon(34, "question", 560 + 400 * q, 700, 160, 0.2 + 0.1 * q, c="red", mv="wig")])
# 34.5 天天见
bd(34.5, icon(34.5, "eye", 700, 500, 260, 0.0, mv="bob"), T(34.5, 1300, 500, 64, "你天天见", c="ink", d=0.3), icon(34.5, "sunrise", 1300, 760, 160, 0.4, c="gold"))
# 35 太阳下山后
s_ = sun(35, 1500, 600, 160, 0.0)
bd(35, s_, [sh(35, s_[0]["id"], 0, 300, 0.1, 1.2)], earth(35, 800), T(35, 600, 360, 60, "太阳下山后……", c="red", d=0.3))
# 35.5 飞机的白线
pl, pli = plane(35.5, 400, 300, 1.0, 0.0)
bd(35.5, pl, [sh(35.5, pli, 1000, 0, 0.1, 2.0)], trail(35.5, 300, 300, 1300, 300, d=0.2, c="gold", w=12), earth(35.5, 860, night=True), T(35.5, 960, 600, 56, "白线还亮着", c="gold", d=0.5))
# 36 天黑了
bd(36, earth(36, 860, night=True), icon(36, "moon", 1500, 280, 150, 0.0, c="gold"), T(36, 700, 400, 64, "天黑了", c="ink", d=0.2),
   [e for q in range(4) for e in star(36, 400 + 300 * q, 260, 0.1 * q, r=20)])
# 36.5 山顶金黄
bd(36.5, mountain(36.5, 960, 860, 1.6, 0.0), sun(36.5, 200, 300, 120, 0.2), ray(36.5, 280, 320, 880, 400, d=0.5), T(36.5, 1500, 400, 56, "山顶还金黄", c="gold", d=0.6))
# 37 一两个小时后
bd(37, icon(37, "clock", 700, 480, 260, 0.0, mv="spin"), BIG(37, 1300, 480, "+1~2 小时", c="blue", d=0.2, s=100), earth(37, 880, night=True))
# 37.5 卫星划过
st = icon(37.5, "satellite", 300, 300, 120, 0.0, mv="spin")
bd(37.5, st, [sh(37.5, st[0]["id"], 1300, 100, 0.1, 2.5)], earth(37.5, 860, night=True), person(37.5, 960, 760, 0.5, look=True)[0], T(37.5, 960, 560, 56, "是卫星！", c="blue", d=0.5))
# 38 都在高处
E = plane(38, 500, 600, 0.8, 0.0)[0] + jian(38, 960, 420, 0.4, d=0.2)[0] + icon(38, "satellite", 1450, 250, 120, 0.4, mv="spin")
bd(38, E, arr(38, 300, 880, 300, 260, c="ink", d=0.3), earth(38, 880, night=True))
# 38.5 泡在阳光里
bd(38.5, sun(38.5, 300, 300, 220, 0.0), [e for q in range(4) for e in ray(38.5, 440, 220 + 90 * q, 1600, 220 + 90 * q, d=0.1 * q)], T(38.5, 1100, 760, 60, "泡在阳光里", c="gold", d=0.5))
# 39 友情提示 很美
bd(39, T(39, 960, 180, 60, "友情提示", c="ink", d=0.1), jelly(39, 960, 560, 1.4, 0.2)[0], [e for q in range(3) for e in star(39, 1450 + 100 * q, 760, 0.4 + 0.1 * q, r=26)])
# 39.5 慢慢散开
j_, ji = jelly(39.5, 960, 480, 1.4, 0.0, c="muted")
bd(39.5, j_, [{"t": "move", "at": 39.5, "kind": "grow", "targets": [ji, ji + "t"], "axis": "both", "from": 1.0, "to": 1.6, "pivot": [960, 480], "dur": 2.0, "delay": 0.4},
              sh(39.5, [ji, ji + "t"], 200, -80, 0.4, 2.0)], T(39.5, 960, 120, 56, "慢慢散开……", c="muted", d=0.4))
# 40 想看下一只
bd(40, jelly(40, 700, 480, 0.9, 0.0)[0], icon(40, "question", 1300, 450, 220, 0.2, c="red", mv="wig"), T(40, 960, 860, 60, "下一只在哪？", c="ink", d=0.3))
# 40.5 发射预告
cal = uid("cal")
bd(40.5, [R(40.5, 700, 300, 520, 400, c="ink", fill="muted", idp=cal), P(40.5, "M700,400 L1220,400", c="ink", w=6, idp=cal), pop(40.5, cal, 0.0), wig(40.5, cal, (960, 700), 4, 1.2)],
   T(40.5, 960, 560, 56, "日落后不久", c="red", d=0.3), jian(40.5, 1500, 600, 0.5)[0], T(40.5, 960, 860, 52, "看发射预告", c="ink", d=0.5))
# 41 往发射场方向看
ps, pp = person(41, 500, 700, 0.9, look=True)
bd(41, ps, arr(41, 600, 520, 1300, 360, c="red", d=0.2), jian(41, 1450, 360, 0.5)[0], icon(41, "map_pin", 1450, 700, 120, 0.4, c="red"))
# 41.5 几百公里
bd(41.5, earth(41.5, 820), person(41.5, 400, 780, 0.4, look=True)[0], jelly(41.5, 1400, 300, 0.5, 0.1)[0], BIG(41.5, 960, 480, "几百公里也行", c="blue", d=0.3, s=90))
# 42 小箭下班
j_, ji = jian(42, 900, 520, 1.6, fire=False)
bd(42, j_, zz := [e for q in range(3) for e in T(42, 1250 + 50 * q, 400 - 60 * q, 50 + 14 * q, "z", c="muted", d=0.2 * q)], T(42, 900, 900, 56, "下班！", c="ink", d=0.3))
# 42.5 卫星送到
st = icon(42.5, "satellite", 960, 460, 260, 0.0, mv="spin")
bd(42.5, st, check(42.5, 1400, 460, d=0.4), earth(42.5, 880), T(42.5, 960, 760, 56, "送到了", c="green", d=0.3))
# 43 傍晚出门
j_, ji = jian(43, 960, 700, 0.8)
bd(43, j_, [sh(43, [ji, ji + "f"], 0, -300, 0.3, 1.4)], sun(43, 1500, 820, 140, 0.0), T(43, 500, 300, 56, "又在傍晚出门", c="red", d=0.4))
# 43.5 记得抬头
ps, pp = person(43.5, 960, 640, 1.2, look=True)
bd(43.5, ps, BIG(43.5, 960, 200, "抬头！", c="red", d=0.2, s=130), jelly(43.5, 1500, 400, 0.5, 0.4)[0])
# 44 高空在跟你说
j_, ji = jelly(44, 960, 450, 1.6, 0.0, c="gold")
bd(44, j_, earth(44, 880, night=True), T(44, 960, 200, 52, "高空在跟你说：", c="ink", d=0.2))
# 44.5 我这儿太阳还没落
bd(44.5, sun(44.5, 960, 380, 260, 0.0), jian(44.5, 500, 600, 0.7, d=0.2)[0], jelly(44.5, 1450, 560, 0.6, 0.3)[0],
   BIG(44.5, 960, 860, "我这儿，太阳还没落呢", c="gold", d=0.4, s=80))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"18点15分": "十八点十五分", "03星": "零三星", "672": "六百七十二", "17点58分": "十七点五十八分", "4度": "四度"})
