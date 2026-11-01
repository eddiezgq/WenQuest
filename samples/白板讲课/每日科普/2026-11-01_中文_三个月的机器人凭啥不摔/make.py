"""每日科普 2026-11-01（中文）：《三个月造的机器人，凭啥不摔？》
新闻：据 The Information 10-31 报道，Meta 与上海傅利叶合作，约三个月造出人形机器人原型 Max；Max 2 九月已开工。
热榜：新浪科技热点小时报 2026-11-01 09 时第 2 条（“Meta与傅利叶合作研发人形机器人原型”）。
出处：
- 新浪科技热点小时报 https://k.sina.com.cn/article_7857201856_1d45362c001908t7vo.html ：三个月、约 1.5 米、英伟达 Thor、Muse 的“物理化身”、Max 2 九月启动。
- TNW https://thenextweb.com/news/meta-humanoid-robot-fourier-max ：约 48 公斤、Jetson Thor、屏幕做表情、扬声器、五指手；
  Max 2：新躯干、更好的手、投影仪、帮助上楼梯的额外传感器；Meta 称原型只做内部研究、不卖；TNW 未独立核实。
常识/估算：两条腿站立 ≈ 倒立摆（“一直在往下倒”）；倒的快慢 ∝ √(重心高度)，重心约 0.75 米时特征时间约 0.28 秒（估算）；
  机器人姿态控制通常每秒几百到上千次（一般情况，不是 Max 的公开参数）；网络来回几十到上百毫秒（估计）。
比喻（手心立扫把、内耳 = 陀螺仪、走路 = 一路接住自己）是我们的。
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_bot, cute_chip, stick  # noqa: E402

S = [
 ("三个月，|造出一台一米五的人形机器人。", "Three months | to build a humanoid robot one and a half meters tall."),
 ("造它的是扎克伯格的Meta，|还有上海的傅利叶。", "The builders: Zuckerberg's Meta | and Shanghai's Fourier."),
 ("据报道，它叫Max，|大约四十八公斤。", "Reportedly it is called Max | and weighs about forty eight kilograms."),
 ("脸是一块屏幕，会做表情，|还有五根手指的手。", "Its face is a screen that makes expressions, | and it has five fingered hands."),
 ("Meta的团队专门飞到中国，|一位副总裁在傅利叶的工厂待了快两个月。", "Meta's team flew to China, | and a vice president spent almost two months at Fourier's factory."),
 ("今天的烧脑问题：|一个两条腿的铁家伙，凭什么站着不摔？", "Today's brain teaser: | how does a two legged machine stand without falling?"),
 ("答案可能吓你一跳：|它其实一直在摔。", "The answer may surprise you: | it is falling all the time."),
 ("先玩个游戏：|把一把扫把立在手心上。", "Try a game: | balance a broom on your palm."),
 ("手不动，|扫把马上就倒。", "Keep your hand still, | and the broom topples right away."),
 ("你得一直挪手，|追着它倒的方向。", "You have to keep moving your hand, | chasing the way it falls."),
 ("物理学家管这叫倒立摆：|重心在上，支点在下。", "Physicists call it an inverted pendulum: | weight on top, pivot at the bottom."),
 ("两条腿站着的机器人，|就是一把会自己挪手的扫把。", "A robot standing on two legs | is a broom that moves its own hand."),
 ("规矩只有一条：|重心要落在脚底板围成的那块地方里。", "There is one rule: | the center of mass must stay over the area under its feet."),
 ("重心一出界，|就开始倒。", "Once the center of mass leaves that area, | it starts to fall."),
 ("反转一：高一点，反而好平衡。|长扫把比铅笔好立多了。", "Twist one: taller is easier. | A long broom is easier to balance than a pencil."),
 ("因为越高，倒得越慢，|你有更多时间去接。", "Because taller things fall slower, | you get more time to catch them."),
 ("估算一下：一米五的个子，重心大约在腰，|不管它的话，一秒左右就躺地上了。", "A rough estimate: for a one and a half meter body, the center of mass is near the waist. | Left alone, it hits the floor in about a second."),
 ("所以机器人得飞快地|检查自己歪没歪。", "So a robot must check very fast | whether it is tilting."),
 ("它肚子里有个陀螺仪，|就像你耳朵里管平衡的那个小器官。", "It has a gyroscope inside, | like the balance organ in your inner ear."),
 ("脚底还有传感器，|感觉力压在哪儿。", "Sensors in the feet | feel where the weight presses."),
 ("一般的人形机器人，|每秒要这样调几百次甚至上千次。", "A typical humanoid robot | adjusts like this hundreds or even thousands of times a second."),
 ("反转二：所以大脑必须|装在机器人自己身上。", "Twist two: so the brain must ride | inside the robot itself."),
 ("要是靠网络问云端，|来回一趟可能就要几十到上百毫秒。", "If it had to ask the cloud, | one round trip could take tens to hundreds of milliseconds."),
 ("等答案回来，|人已经躺下了。", "By the time the answer came back, | the robot would be lying down."),
 ("Max用的是英伟达的Thor芯片，|直接装在身上。", "Max uses Nvidia's Thor chip, | built right into its body."),
 ("走路就更刺激了：|每一步都是先往前倒。", "Walking is even wilder: | every step starts with falling forward."),
 ("然后伸出一只脚，|把自己接住。", "Then a foot swings out | and catches it."),
 ("走路，就是一路摔、|一路接住自己。", "Walking is falling | and catching yourself, again and again."),
 ("你每天也是这么走的，|只是你早就忘了。", "You walk this way every day too. | You just forgot."),
 ("反转三：最难的不是站，|是楼梯。", "Twist three: the hardest part is not standing. | It is stairs."),
 ("脚下的地面突然变了高度，|它得提前看见。", "The ground suddenly changes height, | and it has to see that coming."),
 ("据报道，Max 2九月就开工了，|加了帮它上楼梯的传感器。", "Reportedly, Max 2 started in September, | with extra sensors to help it on stairs."),
 ("还换了新躯干、更好的手，|甚至加了投影仪。", "Plus a new torso, better hands, | and even a projector."),
 ("Meta想让它当自家AI Muse的身体，|将来帮忙做家务。", "Meta wants it to be a body for its AI, Muse, | and someday help with chores."),
 ("想想那个画面：|AI终于有了腿。", "Picture it: | AI finally gets legs."),
 ("然后它第一件事，|是学会别摔跤。", "And the first thing it has to learn | is not to fall."),
 ("三个月能造这么快，|也说明中国的机器人供应链多成熟。", "Building it in three months | also shows how mature China's robot supply chain is."),
 ("傅利叶自己也做人形机器人，|比如一米六五高的陪护机器人GR-3。", "Fourier makes its own humanoids too, | like GR-3, a one hundred sixty five centimeter care robot."),
 ("友情提示：这些都来自媒体报道，|Meta说原型只做内部研究，不卖。", "Fine print: all of this comes from media reports. | Meta says the prototypes are for research, not for sale."),
 ("一秒倒地、每秒几百次，|是一般情况的估算，不是Max的官方参数。", "One second to fall, hundreds of checks a second: | these are general estimates, not Max's official specs."),
 ("所以，三个月造的机器人，凭啥不摔？|它一刻不停地在摔，又一刻不停地接住自己。", "So how does a robot built in three months not fall? | It never stops falling, and never stops catching itself."),
 ("跟你一样。|只不过它还在学，你已经会了。", "Just like you. | It is still learning. You already know how."),
]
TITLE = {"zh": "三个月造的机器人，凭啥不摔？", "en": "Built in 3 Months: Why Doesn't It Fall?"}

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


def bot(a, x, y, k=1.0, d=0.0, mood="happy", tilt=0, fall=None, walk=0):
    """Max: cute_bot. tilt = wobble back and forth; fall = delay to fall flat; walk = dx."""
    i = uid("rb")
    E = cute_bot(x, y, k, a, idp=i, mood=mood) + [pop(a, i + "_b", d)]
    if tilt:
        E.append({"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": tilt, "hz": 1.4})
    if fall is not None:
        E.append(rot(a, i + "*", 85, (x, y), fall, 0.7))
    if walk:
        E.append(sh(a, i + "*", walk, 0, d + 0.3, 1.6))
    return E


def broom(a, x, y, L=420, d=0.0, fall=None, wob=True):
    """A broom standing on a palm at (x, y): stick + bristles; wobbles, or falls."""
    i, h = uid("br"), uid("pm")
    E = [P(a, f"M{x},{y} L{x},{y - L}", c="ink", w=10, idp=i),
         P(a, f"M{x - 60},{y - L} L{x + 60},{y - L} L{x + 40},{y - L - 110} L{x - 40},{y - L - 110} Z", c="ink", w=5, fill="gold", idp=i),
         P(a, f"M{x - 110},{y + 10} Q{x},{y + 60} {x + 110},{y + 10} L{x + 110},{y + 50} Q{x},{y + 100} {x - 110},{y + 50} Z", c="ink", w=5, fill="paper", idp=h),
         pop(a, [i, h], d)]
    if wob:
        E.append({"t": "move", "at": a, "kind": "wiggle", "targets": [i], "pivot": [x, y], "amp": 8, "hz": 1.3})
        E.append({"t": "move", "at": a, "kind": "wiggle", "targets": [h], "pivot": [x, y], "amp": 2, "hz": 1.3})
    if fall is not None:
        E.append(rot(a, i, 80, (x, y), fall, 0.8))
    return E


def pencil(a, x, y, d=0.0, fall=None):
    i = uid("pc")
    E = [R(a, x - 12, y - 160, 24, 160, c="ink", fill="gold", idp=i), P(a, f"M{x - 12},{y - 160} L{x},{y - 195} L{x + 12},{y - 160}", c="ink", w=4, idp=i), pop(a, i, d)]
    if fall is not None:
        E.append(rot(a, i, 85, (x, y), fall, 0.3))
    return E


def feet(a, x, y, d=0.0, out=False):
    """The support area: two foot prints and the dashed region between; a red COM dot drops onto it (or outside)."""
    f, c = uid("ft"), uid("cm")
    E = [R(a, x - 220, y - 40, 160, 80, c="ink", fill="muted", idp=f), R(a, x + 60, y - 40, 160, 80, c="ink", fill="muted", idp=f),
         R(a, x - 220, y - 40, 440, 80, c="green", idp=f, sw=4), pop(a, f, d),
         O(a, x + (380 if out else 0), y - 400, 30, c="red", fill="red", idp=c), pop(a, c, d + 0.2), sh(a, c, 0, 400, d + 0.5, 0.8)]
    return E


def gyro(a, x, y, s=130, d=0.0):
    i, j = uid("gy"), uid("gr")
    return [O(a, x, y, s, c="blue", idp=i, sw=6), pop(a, i, d), P(a, f"M{x - s},{y} Q{x},{y - s * 0.5} {x + s},{y} Q{x},{y + s * 0.5} {x - s},{y}", c="red", w=5, idp=j),
            pop(a, j, d + 0.1), spin(a, j, (x, y), 90), O(a, x, y, 18, c="ink", fill="ink")]


def ear(a, x, y, d=0.0):
    i, j = uid("er"), uid("ec")
    return [P(a, f"M{x},{y - 160} Q{x + 140},{y - 170} {x + 130},{y - 20} Q{x + 120},{y + 80} {x + 40},{y + 120} Q{x},{y + 150} {x - 20},{y + 110}", c="ink", w=7, idp=i),
            pop(a, i, d), P(a, f"M{x + 40},{y - 60} Q{x + 80},{y - 100} {x + 70},{y - 30} Q{x + 60},{y + 10} {x + 40},{y}", c="blue", w=6, idp=j), pop(a, j, d + 0.3), wig(a, j, (x + 50, y - 30), 10, 2.5)]


def cloud_trip(a, x0, y0, x1, y1, d=0.0):
    """A message dot flying to the cloud and back (slow)."""
    i = uid("ms")
    return [{"t": "icon", "at": a, "id": uid("cl"), "name": "cloud", "x": x1, "y": y1, "size": 200, "c": "blue"},
            O(a, x0, y0, 22, c="red", fill="red", idp=i), pop(a, i, d), sh(a, i, x1 - x0, y1 - y0, d + 0.2, 0.9), sh(a, i, x0 - x1, y0 - y1, d + 1.2, 0.9)]


def chip(a, x, y, k=1.0, d=0.0, label=None):
    i = uid("cp")
    return cute_chip(x, y, k, a, idp=i, label=label) + [pop(a, i + "_b", d)]


def stairs(a, x, y, n=4, d=0.0):
    i = uid("sr")
    pts = f"M{x},{y}" + "".join(f" L{x + 120 * q},{y - 90 * q} L{x + 120 * (q + 1)},{y - 90 * q}" for q in range(n))
    return [P(a, pts, c="ink", w=7, idp=i), pop(a, i, d), pulse(a, i, d + 0.6)]


def scan(a, x, y, d=0.0):
    """Sensor beams fanning out from (x, y) toward the lower right."""
    E = []
    for q in range(3):
        j = uid("sc")
        E += [{"t": "arrow", "at": a, "id": j, "pts": [[x, y], [x + 260, y + 60 + 70 * q]], "c": "red", "w": 5}, pop(a, j, d + 0.12 * q), pulse(a, j, d + 0.6 + 0.12 * q)]
    return E


def man(a, x, y, k=1.4, d=0.0, walk=0):
    i = uid("mn")
    E = [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    E = stick(x, y, k, a, idp=i) + E
    if walk:
        E.append(sh(a, i + "*", walk, 0, d + 0.3, 1.6))
    E.append({"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 6, "hz": 1.6})
    return E


def clock(a, x, y, s=140, d=0.0):
    return ic(a, "clock", x, y, s, d, mv="spin")


# ---------- boards ----------
bd(0, BIG(0, 1350, 300, "3 个月", c="red", d=0.0, s=150), bot(0, 600, 920, 1.5, 0.0, tilt=4), clock(0, 1350, 600, 160, 0.3))
bd(0.5, bot(0.5, 600, 920, 1.5, 0.0, tilt=4), ic(0.5, "ruler", 1000, 560, 200, 0.2, mv="wig"), BIG(0.5, 1450, 450, "1.5 米", c="blue", d=0.4, s=140))
bd(1, T(1, 960, 280, 80, "Meta", c="blue", d=0.0), ic(1, "building", 600, 600, 220, 0.2, mv="bob"), arr(1, 800, 600, 1100, 600, c="ink", d=0.4), bot(1, 1350, 900, 0.9, 0.3, tilt=4))
bd(1.5, T(1.5, 960, 280, 80, "傅利叶 · 上海", c="red", d=0.0), ic(1.5, "gear", 600, 600, 200, 0.2, mv="spin"), ic(1.5, "robot_arm", 1350, 600, 200, 0.4, mv="wig"))
bd(2, bot(2, 600, 920, 1.4, 0.0, tilt=4), BIG(2, 1350, 350, "Max", c="blue", d=0.2, s=160), ic(2, "question", 1650, 600, 120, 0.4, mv="wig", c="red"))
bd(2.5, bot(2.5, 600, 920, 1.4, 0.0, tilt=4), BIG(2.5, 1350, 400, "48 公斤", c="red", d=0.2, s=140), bar(2.5, 1250, 850, 80, 200, "red", 0.4), bar(2.5, 1400, 850, 80, 300, "red", 0.5))
bd(3, bot(3, 700, 920, 1.5, 0.0), ic(3, "phone", 1350, 450, 200, 0.2, mv="wig"), T(3, 1350, 700, 60, "屏幕脸 · 会做表情", c="blue", d=0.4))
bd(3.5, bot(3.5, 600, 920, 1.3, 0.0, tilt=4), T(3.5, 1350, 300, 70, "五根手指", c="red", d=0.2), ic(3.5, "robot_arm", 1350, 600, 200, 0.3, mv="wig"))
bd(4, ic(4, "rocket", 500, 500, 200, 0.0, mv="bob"), arr(4, 650, 500, 1200, 500, c="blue", d=0.2, w=8), ic(4, "map_pin", 1400, 500, 200, 0.4, mv="bob", c="red"), T(4, 1400, 750, 60, "中国", c="red", d=0.5))
bd(4.5, ic(4.5, "building", 600, 550, 240, 0.0, mv="bob"), BIG(4.5, 1350, 380, "快两个月", c="red", d=0.2, s=110), clock(4.5, 1350, 650, 140, 0.4))
bd(5, BIG(5, 1150, 360, "烧脑问题", c="red", d=0.0, s=130), ic(5, "question", 450, 450, 260, 0.2, mv="wig", c="red"), bot(5, 1300, 950, 0.7, 0.3, tilt=6))
bd(5.5, bot(5.5, 700, 920, 1.4, 0.0, tilt=8, mood="sad"), ic(5.5, "question", 1300, 400, 200, 0.2, mv="wig", c="red"), T(5.5, 1350, 700, 70, "凭啥不摔？", c="red", d=0.4))
bd(6, ic(6, "eye", 960, 400, 200, 0.0, mv="wig"), T(6, 960, 700, 70, "吓你一跳", c="ink", d=0.2), ic(6, "flame", 450, 500, 150, 0.3, mv="wig", c="red"), ic(6, "flame", 1470, 500, 150, 0.4, mv="wig", c="red"))
bd(6.5, bot(6.5, 700, 920, 1.4, 0.0, tilt=12), BIG(6.5, 1350, 450, "一直在摔", c="red", d=0.3, s=120))
bd(7, broom(7, 800, 850, 420, 0.0), T(7, 1400, 350, 64, "小游戏", c="blue", d=0.2), ic(7, "question", 1400, 600, 140, 0.4, mv="wig", c="red"))
bd(7.5, broom(7.5, 700, 850, 450, 0.0), T(7.5, 1350, 450, 64, "立在手心", c="ink", d=0.3), check(7.5, 1350, 650, d=0.6))
bd(8, broom(8, 700, 850, 450, 0.0, fall=0.4, wob=False), cross(8, 1350, 450, d=0.2), T(8, 1350, 650, 64, "手不动", c="red", d=0.3))
bd(8.5, broom(8.5, 600, 850, 450, 0.0, fall=0.1, wob=False), BIG(8.5, 1350, 450, "马上倒", c="red", d=0.3, s=120))
bd(9, broom(9, 600, 850, 450, 0.0), arr(9, 600, 960, 1000, 960, c="blue", d=0.3), T(9, 1350, 450, 64, "一直挪手", c="blue", d=0.3))
bd(9.5, broom(9.5, 500, 850, 450, 0.0), arr(9.5, 500, 960, 900, 960, c="blue", d=0.2), arr(9.5, 900, 960, 500, 960, c="blue", d=1.0), T(9.5, 1350, 450, 64, "追着倒的方向", c="blue", d=0.4))
bd(10, T(10, 960, 260, 80, "倒立摆", c="blue", d=0.0), O(10, 960, 450, 70, c="red", fill="red"), P(10, "M960,520 L960,850", c="ink", w=10), O(10, 960, 860, 20, c="ink", fill="ink"),
   arr(10, 1100, 450, 1350, 450, c="red", d=0.3), T(10, 1550, 450, 50, "重心在上", c="red", d=0.4), T(10, 1550, 860, 50, "支点在下", c="ink", d=0.6), broom(10, 450, 850, 350, 0.5))
bd(10.5, broom(10.5, 600, 850, 420, 0.0), T(10.5, 1300, 420, 120, "=", c="ink", d=0.2), bot(10.5, 1450, 920, 1.0, 0.3, tilt=6))
bd(11, bot(11, 700, 920, 1.4, 0.0, tilt=8), BIG(11, 1350, 400, "会挪手的扫把", c="blue", d=0.3, s=90), arr(11, 500, 960, 900, 960, c="blue", d=0.5))
bd(11.5, bot(11.5, 600, 920, 1.3, 0.0, tilt=6), broom(11.5, 1350, 850, 400, 0.2))
bd(12, T(12, 960, 230, 70, "只有一条规矩", c="red", d=0.0), feet(12, 960, 850, 0.2), T(12, 960, 600, 56, "重心", c="red", d=0.6))
bd(12.5, feet(12.5, 960, 850, 0.0), check(12.5, 1450, 600, d=1.2), T(12.5, 960, 300, 56, "落在脚底板围成的地方里", c="green", d=0.3))
bd(13, feet(13, 800, 850, 0.0, out=True), cross(13, 1180, 600, d=1.2), T(13, 960, 250, 70, "出界！", c="red", d=0.3))
bd(13.5, bot(13.5, 800, 920, 1.3, 0.0, fall=0.4, mood="sad"), BIG(13.5, 1450, 400, "开始倒", c="red", d=0.3, s=110))
bd(14, BIG(14, 960, 360, "反转一", c="red", d=0.0, s=150), ic(14, "ruler", 450, 550, 160, 0.2, mv="wig"), ic(14, "flame", 1470, 550, 150, 0.4, mv="wig", c="red"))
bd(14.5, broom(14.5, 600, 850, 500, 0.0), check(14.5, 600, 200, d=0.4), pencil(14.5, 1350, 850, 0.2, fall=0.8), cross(14.5, 1350, 550, d=1.0))
bd(15, broom(15, 500, 850, 500, 0.0, fall=0.3, wob=False), pencil(15, 1300, 850, 0.0, fall=0.1), T(15, 960, 250, 60, "越高，倒得越慢", c="blue", d=0.4))
bd(15.5, broom(15.5, 600, 850, 450, 0.0), clock(15.5, 1350, 400, 160, 0.2), T(15.5, 1350, 650, 60, "更多时间去接", c="green", d=0.4))
bd(16, bot(16, 600, 920, 1.4, 0.0, tilt=4), O(16, 600, 920 - 210 * 1.4, 26, c="red", fill="red"), arr(16, 1000, 650, 680, 640, c="red", d=0.3), T(16, 1350, 600, 56, "重心约在腰", c="red", d=0.3), T(16, 1350, 300, 56, "估算", c="muted", d=0.1))
bd(16.5, bot(16.5, 700, 920, 1.3, 0.0, fall=0.5, mood="sad"), BIG(16.5, 1400, 400, "≈ 1 秒", c="red", d=0.3, s=140), clock(16.5, 1400, 680, 130, 0.4))
bd(17, bot(17, 700, 920, 1.3, 0.0, tilt=10), ic(17, "eye", 1350, 400, 180, 0.2, mv="wig"), T(17, 1350, 650, 60, "歪没歪？", c="red", d=0.4))
bd(17.5, bot(17.5, 600, 920, 1.3, 0.0, tilt=10), ic(17.5, "clock", 1200, 450, 150, 0.2, mv="spin"), ic(17.5, "clock", 1500, 450, 150, 0.3, mv="spin"), BIG(17.5, 1350, 700, "飞快", c="red", d=0.4, s=110))
bd(18, bot(18, 600, 920, 1.3, 0.0, tilt=5), gyro(18, 1350, 450, 150, 0.2), T(18, 1350, 750, 60, "陀螺仪", c="blue", d=0.4))
bd(18.5, ear(18.5, 600, 500, 0.0), T(18.5, 960, 900, 60, "内耳管平衡", c="blue", d=0.3), gyro(18.5, 1400, 500, 130, 0.3))
bd(19, feet(19, 700, 850, 0.0), ic(19, "signal", 1400, 450, 180, 0.2, mv="bob"), T(19, 1400, 700, 60, "脚底传感器", c="blue", d=0.4))
bd(19.5, feet(19.5, 900, 850, 0.0), arr(19.5, 700, 400, 700, 750, c="red", d=0.3), arr(19.5, 1100, 400, 1100, 750, c="red", d=0.4), T(19.5, 900, 250, 60, "力压在哪儿", c="red", d=0.5))
bd(20, bot(20, 600, 920, 1.3, 0.0, tilt=6), BIG(20, 1350, 380, "每秒几百次", c="red", d=0.2, s=100), clock(20, 1350, 650, 140, 0.3))
bd(20.5, BIG(20.5, 960, 380, "甚至上千次", c="red", d=0.0, s=120), bot(20.5, 450, 920, 0.8, 0.2, tilt=10), bot(20.5, 1500, 920, 0.8, 0.3, tilt=10))
bd(21, BIG(21, 960, 360, "反转二", c="red", d=0.0, s=150), chip(21, 450, 600, 1.0, 0.2), ic(21, "flame", 1470, 550, 150, 0.4, mv="wig", c="red"))
bd(21.5, bot(21.5, 700, 920, 1.4, 0.0, tilt=4), chip(21.5, 700, 920 - 250 * 1.4, 0.5, 0.3), T(21.5, 1350, 400, 64, "大脑装在身上", c="blue", d=0.4))
bd(22, bot(22, 500, 920, 1.0, 0.0, tilt=6), cloud_trip(22, 550, 450, 1400, 300, 0.2), T(22, 1400, 600, 56, "问云端？", c="blue", d=0.3))
bd(22.5, cloud_trip(22.5, 500, 600, 1400, 300, 0.0), BIG(22.5, 960, 800, "几十～上百毫秒", c="red", d=0.3, s=90), T(22.5, 500, 300, 50, "估计", c="muted", d=0.2))
bd(23, cloud_trip(23, 500, 500, 1400, 300, 0.0), bot(23, 800, 920, 1.0, 0.1, fall=0.6, mood="sad"), T(23, 1350, 650, 60, "等答案…", c="ink", d=0.3))
bd(23.5, bot(23.5, 700, 920, 1.2, 0.0, fall=0.1, mood="sad"), BIG(23.5, 1350, 400, "已经躺下", c="red", d=0.3, s=110), star(23.5, 900, 750, 0.5, r=30))
bd(24, chip(24, 700, 550, 1.6, 0.0, label="Thor"), T(24, 1350, 400, 64, "英伟达 Thor", c="green", d=0.2), ic(24, "gear", 1350, 650, 140, 0.4, mv="spin"))
bd(24.5, bot(24.5, 700, 920, 1.4, 0.0, tilt=4), chip(24.5, 700, 920 - 250 * 1.4, 0.45, 0.2), check(24.5, 1350, 450, d=0.4), T(24.5, 1350, 650, 60, "装在身上", c="green", d=0.5))
bd(25, man(25, 600, 650, 1.6, 0.0, walk=300), T(25, 1350, 350, 70, "走路更刺激", c="red", d=0.2), ic(25, "flame", 1350, 600, 140, 0.4, mv="wig", c="red"))
bd(25.5, bot(25.5, 600, 920, 1.3, 0.0, walk=400), arr(25.5, 1100, 500, 1500, 600, c="red", d=0.3), T(25.5, 1350, 350, 64, "先往前倒", c="red", d=0.3))
bd(26, bot(26, 500, 920, 1.3, 0.0, walk=500), feet(26, 1300, 900, 0.3), T(26, 1300, 350, 64, "伸出一只脚", c="blue", d=0.4))
bd(26.5, bot(26.5, 700, 920, 1.3, 0.0, tilt=4), check(26.5, 1350, 450, d=0.3), BIG(26.5, 1350, 650, "接住！", c="green", d=0.4, s=110))
bd(27, bot(27, 400, 920, 1.0, 0.0, walk=900), T(27, 960, 300, 70, "一路摔", c="red", d=0.3))
bd(27.5, bot(27.5, 400, 920, 1.0, 0.0, walk=900), T(27.5, 960, 300, 70, "一路接住自己", c="green", d=0.3), check(27.5, 1650, 500, d=1.2))
bd(28, man(28, 500, 650, 1.6, 0.0, walk=700), T(28, 1350, 300, 64, "你也是", c="blue", d=0.3))
bd(28.5, man(28.5, 700, 650, 1.6, 0.0), ic(28.5, "question", 1300, 400, 160, 0.2, mv="wig", c="red"), T(28.5, 1300, 650, 64, "早就忘了", c="ink", d=0.4))
bd(29, BIG(29, 960, 360, "反转三", c="red", d=0.0, s=150), stairs(29, 450, 850, 3, 0.2), ic(29, "flame", 1470, 550, 150, 0.4, mv="wig", c="red"))
bd(29.5, stairs(29.5, 900, 900, 5, 0.0), bot(29.5, 650, 920, 1.0, 0.2, tilt=8, mood="sad"), BIG(29.5, 1350, 300, "楼梯", c="red", d=0.4, s=130))
bd(30, stairs(30, 1000, 900, 4, 0.0), bot(30, 650, 920, 1.0, 0.1, tilt=6), scan(30, 700, 600, 0.3), ic(30, "eye", 400, 350, 130, 0.4, mv="wig"))
bd(30.5, stairs(30.5, 1000, 900, 4, 0.0), bot(30.5, 700, 920, 1.0, 0.1), scan(30.5, 760, 600, 0.2), T(30.5, 960, 200, 64, "提前看见", c="red", d=0.4))
bd(31, BIG(31, 960, 300, "Max 2", c="blue", d=0.0, s=150), T(31, 960, 450, 60, "九月开工", c="ink", d=0.2), ic(31, "gear", 600, 700, 150, 0.3, mv="spin"), ic(31, "gear", 1300, 700, 150, 0.4, mv="spin"))
bd(31.5, stairs(31.5, 1000, 900, 4, 0.0), bot(31.5, 650, 920, 1.0, 0.1, walk=200), scan(31.5, 700, 600, 0.3), T(31.5, 1300, 200, 56, "上楼梯的传感器", c="red", d=0.5))
bd(32, bot(32, 600, 920, 1.3, 0.0, tilt=4), T(32, 1350, 300, 60, "新躯干", c="blue", d=0.2), T(32, 1350, 420, 60, "更好的手", c="blue", d=0.4), ic(32, "robot_arm", 1350, 650, 150, 0.5, mv="wig"))
bd(32.5, ic(32.5, "lens", 600, 500, 200, 0.0, mv="wig"), arr(32.5, 720, 500, 1200, 400, c="gold", d=0.2), arr(32.5, 720, 500, 1200, 600, c="gold", d=0.3), BIG(32.5, 1450, 500, "投影仪", c="gold", d=0.4, s=100))
bd(33, chip(33, 500, 550, 1.2, 0.0, label="Muse"), arr(33, 700, 550, 1100, 550, c="blue", d=0.3), bot(33, 1350, 920, 1.1, 0.4, tilt=4), T(33, 960, 250, 60, "AI 的身体", c="blue", d=0.4))
bd(33.5, bot(33.5, 600, 920, 1.2, 0.0, walk=200), ic(33.5, "building", 1350, 450, 200, 0.2, mv="bob"), T(33.5, 1350, 700, 60, "做家务", c="green", d=0.4))
bd(34, chip(34, 960, 500, 1.4, 0.0), T(34, 960, 250, 60, "想想那个画面", c="ink", d=0.2), ic(34, "eye", 450, 550, 140, 0.3, mv="wig"))
bd(34.5, chip(34.5, 960, 420, 1.1, 0.0), P(34.5, "M920,520 L880,750 L930,850 M1000,520 L1040,750 L990,850", c="ink", w=10), BIG(34.5, 1450, 400, "有腿了", c="red", d=0.4, s=110))
bd(35, bot(35, 700, 920, 1.3, 0.0, tilt=8), T(35, 1350, 350, 64, "第一件事", c="ink", d=0.3), ic(35, "question", 1350, 600, 140, 0.4, mv="wig", c="red"))
bd(35.5, bot(35.5, 700, 920, 1.3, 0.0, tilt=12, mood="sad"), BIG(35.5, 1350, 450, "别摔跤", c="red", d=0.3, s=120))
bd(36, BIG(36, 960, 330, "3 个月", c="red", d=0.0, s=140), ic(36, "gear", 500, 650, 150, 0.2, mv="spin"), ic(36, "gear", 700, 780, 110, 0.3, mv="spin"), ic(36, "robot_arm", 1400, 650, 160, 0.4, mv="wig"))
bd(36.5, ic(36.5, "building", 500, 550, 220, 0.0, mv="bob"), arr(36.5, 700, 550, 1100, 550, c="green", d=0.2), T(36.5, 1400, 450, 60, "供应链成熟", c="green", d=0.4), check(36.5, 1400, 650, d=0.6))
bd(37, ic(37, "building", 600, 550, 220, 0.0, mv="bob"), bot(37, 1350, 920, 1.0, 0.3, tilt=4), T(37, 960, 250, 60, "傅利叶自己也做", c="red", d=0.3))
bd(37.5, bot(37.5, 700, 920, 1.5, 0.0, tilt=3), BIG(37.5, 1400, 350, "GR-3", c="blue", d=0.2, s=130), T(37.5, 1400, 520, 56, "1.65 米 · 陪护", c="ink", d=0.4))
bd(38, BIG(38, 960, 360, "友情提示", c="blue", d=0.0, s=130), ic(38, "phone", 500, 650, 150, 0.2, mv="wig"), ic(38, "magnifier", 1400, 650, 150, 0.4, mv="wig"))
bd(38.5, bot(38.5, 600, 920, 1.2, 0.0, tilt=4), T(38.5, 1350, 350, 56, "只做内部研究", c="ink", d=0.2), BIG(38.5, 1350, 550, "不卖", c="red", d=0.4, s=110))
bd(39, T(39, 960, 300, 70, "1 秒 · 每秒几百次", c="red", d=0.0), clock(39, 600, 600, 150, 0.2), ic(39, "ruler", 1300, 600, 150, 0.3, mv="wig"))
bd(39.5, BIG(39.5, 960, 380, "估算", c="blue", d=0.0, s=140), cross(39.5, 960, 600, d=0.3), T(39.5, 960, 750, 56, "不是官方参数", c="ink", d=0.4))
bd(40, bot(40, 700, 920, 1.3, 0.0, tilt=10), ic(40, "question", 1350, 400, 180, 0.2, mv="wig", c="red"), T(40, 1350, 650, 60, "凭啥不摔？", c="red", d=0.3))
bd(40.5, bot(40.5, 400, 920, 1.0, 0.0, walk=900), T(40.5, 960, 260, 60, "一直在摔，一直在接", c="green", d=0.3), check(40.5, 1650, 500, d=1.2))
bd(41, man(41, 600, 650, 1.6, 0.0), T(41, 960, 400, 120, "=", c="ink", d=0.2), bot(41, 1350, 920, 1.2, 0.3, tilt=6))
bd(41.5, man(41.5, 500, 650, 1.6, 0.0, walk=200), bot(41.5, 1350, 920, 1.2, 0.1, tilt=10), BIG(41.5, 960, 250, "你已经会了", c="green", d=0.4, s=100))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"Meta": "梅塔", "Max": "麦克斯", "Thor": "索尔", "Muse": "缪斯", "GR-3": "G R 三", "AI": "A I"})
