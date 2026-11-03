"""每日科普 2026-11-03（中文）：《机器狗背70公斤爬泰山，累不累？》
新闻：11 月 2 日开赛的首届总台世界机器人泰山登山（简称泰山机器人登山赛），足式机器人负重赛冠军是灵锶智能“灵狮队”的机器狗；
  最难的第二段连筐约 70 公斤，超过额定负重 50 公斤（据报道）；人形机器人竞速赛的台阶高低宽窄不一。
热榜：新浪机器人热点小时报 2026-11-03 13 时第 3 条（负重赛冠军）、第 2 条（登山助力机器人）、第 8 条（人形竞速）。
出处：
- 新浪机器人热点小时报 https://k.sina.com.cn/article_7857201856_1d45362c001908th14.html
- 挑山工一趟约 30–40 公斤（央视新闻 2025-04-05，人民日报客户端转载）：https://www.peopleapp.com/column/30048712880-500006185178
常识/估算：泰山海拔约 1545 米；功 = 重量 × 高度（mgh），70 公斤抬高 1 米约 700 焦（g 取 10，估算）；一级台阶约 15–20 厘米（估算）；
  电机“举着不动”时机械功为零但电流照样发热（焦耳热，物理常识）；三点支撑 = 静态稳定（常识）。
  一路背到山顶抬高一千多米（山顶 1545 米减山脚，估算）→ 70×10×1300 ≈ 90 万焦，说“将近一百万焦”；大号充电宝 20000 mAh×3.7 V ≈ 74 Wh ≈ 27 万焦，约 4 块（估算）；
  实际耗电多好几倍是推测；人形竞速（新浪第 8 条）、助力外骨骼约 1 小时上中天门（新浪第 2 条）据报道。
比喻（台阶 = 一级级把箱子搬上货架；四条腿 = 三条腿的凳子最稳）是我们的。
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_bot, cute_dogbot, stick, txt  # noqa: E402

S = [
 ("一只机器狗，背着七十公斤，|爬上了泰山。", "A robot dog carried seventy kilograms | up Mount Tai."),
 ("七十公斤是什么概念？|差不多背着一个成年人。", "How heavy is seventy kilograms? | About one grown-up on its back."),
 ("这是11月2日开赛的泰山机器人登山赛，|它拿了负重赛冠军。", "This was the Mount Tai robot climbing contest that opened November second, | and it won the load race."),
 ("据报道，它的额定负重只有五十公斤，|比赛这段直接超载。", "Reportedly its rated load is only fifty kilograms. | On this stretch it was overloaded."),
 ("今天的烧脑问题：|机器狗背七十公斤爬泰山，到底累不累？", "Today's brain teaser: | does a robot dog get tired hauling seventy kilos up Mount Tai?"),
 ("先认识主角：小灵，|一只四条腿的机器狗。", "Meet our hero, Lingling, | a four-legged robot dog."),
 ("它没有肌肉，|每条腿上是几个电机。", "It has no muscles. | Each leg has a few motors."),
 ("爬山，说白了就是|把东西往高处搬。", "Climbing is really just | lifting stuff higher."),
 ("每一级台阶，就像把箱子|搬上一层货架。", "Every step is like lifting a box | onto the next shelf."),
 ("物理课的公式：|做的功 = 重量 × 高度。", "The physics rule: | work equals weight times height."),
 ("估算一下：七十公斤抬高一米，|大约七百焦。", "Rough estimate: lifting seventy kilos one meter | takes about seven hundred joules."),
 ("一级台阶十几厘米，|一级就要一百多焦。", "One step is fifteen centimeters or so. | That is over one hundred joules per step."),
 ('要是一路背到泰山顶，|估算要抬高一千多米。', 'If it hauled all the way to the summit, | that is over a thousand meters up, roughly.'),
 ('七十公斤抬一千多米，|算下来将近一百万焦。', 'Seventy kilos up a thousand meters | works out to nearly a million joules.'),
 ('一百万焦是多少？|大约四块大号充电宝的电。', 'How much is a million joules? | About four big power banks.'),
 ('可电机会发热，腿还要找平衡，|实际耗的电得多好几倍，这是推测。', "But motors heat up and legs keep balancing, | so the real bill is several times more. That's our guess."),
 ("反转一：走快走慢，|这份功一分都不少。", "Twist one: fast or slow, | the work stays exactly the same."),
 ("一口气冲上去，|和歇十次再上去，一样多。", "Rush up in one go, | or rest ten times, it is the same amount."),
 ("走得快，只是每秒花得多，|这叫功率。", "Going fast only spends more per second. | That is called power."),
 ("就像花钱：|总价一样，只是一次付还是分期付。", "Like paying for something: | same price, all at once or in installments."),
 ("那为啥是四条腿，|不是两条腿？", "So why four legs | and not two?"),
 ("想想凳子：|三条腿的凳子，怎么放都不晃。", "Think of a stool: | a three-legged stool never wobbles."),
 ("机器狗抬一条腿，|还剩三条腿撑着。", "When the robot dog lifts one leg, | three are still holding it up."),
 ("两条腿的人形机器人抬一条腿，|只剩一个点，得一直找平衡。", "When a two-legged humanoid lifts one leg, | only one point is left, so it must keep balancing."),
 ("所以背重物，|四条腿天生占便宜。", "So for heavy loads, | four legs have a built-in edge."),
 ('那人形机器人呢？|据报道，它们也在乱台阶上比了竞速。', 'What about humanoids? | Reportedly they raced on the messy steps too.'),
 ('两条腿虽然难，|可人走的路，全是给两条腿修的。', 'Two legs are harder, | but every path people walk was built for two legs.'),
 ("反转二，最反直觉：|站着不动，也在耗电。", "Twist two, the strangest: | standing still also burns power."),
 ("按物理课的定义，|举着不动，做的功是零。", "By the physics definition, | holding still does zero work."),
 ("可电机要使劲撑住，|电流一直在流，全变成了热。", "But the motors push to hold on. | Current keeps flowing, and it all turns into heat."),
 ("你端着一桶水站着不动，|胳膊照样会酸。", "Hold a bucket of water without moving, | and your arm still gets sore."),
 ("所以机器狗不会“累”，|但电机会热，电池会掉。", "So the robot dog does not get tired, | but its motors heat up and its battery drains."),
 ("反转三：泰山的台阶，|最难的不是高，是乱。", "Twist three: on Mount Tai, | the hard part is not the height, it is the mess."),
 ("据报道，台阶高低宽窄都不一样，|每一步都得重新算。", "Reportedly the steps vary in height and width, | so every step needs a new calculation."),
 ("机器狗靠眼睛和腿上的感觉，|一步一步“摸”着走。", "The dog uses cameras and the feel in its legs | to feel its way, step by step."),
 ("再说咱们的挑山工：|据央视报道，一趟挑三四十公斤。", "Now the human porters of Mount Tai: | according to CCTV, about thirty to forty kilos a trip."),
 ("机器狗背七十公斤，|力气上已经赢了一倍。", "The robot dog carried seventy, | about double on pure strength."),
 ("可挑山工能挑一整天，|机器狗得找地方充电。", "But porters can go all day. | The robot dog needs to find a charger."),
 ('据报道，登山赛上还有人穿着助力外骨骼，|大约一小时就上了中天门。', 'Reportedly, one climber wore an assist exoskeleton | and reached the halfway gate in about an hour.'),
 ('机器不一定要替人爬山，|也可以帮人爬山。', "Machines don't have to climb for us. | They can help us climb."),
 ("友情提示：七十公斤、五十公斤额定是据报道，|七百焦、一百多焦是估算。", "Fine print: seventy kilos and the fifty kilo rating are as reported. | Seven hundred joules and over one hundred per step are estimates."),
 ("比赛是一天的成绩，|离天天上山干活还有距离。", "A contest is one day's result, | still far from hauling up the mountain every day."),
 ("所以，机器狗累不累？|它不会累，只会热、只会没电。", "So does the robot dog get tired? | It never gets tired. It only gets hot and runs out of battery."),
 ("泰山不是一口气爬上去的，|是一级一级“抬”上去的。", "Nobody climbs Mount Tai in one go. | It gets lifted, one step at a time."),
]
TITLE = {"zh": "机器狗背70公斤爬泰山，累不累？", "en": "A Robot Dog Hauled 70 kg Up Mount Tai. Is It Tired?"}

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


def dog(a, x, y, k=1.0, d=0.0, load=None, mood="happy", walk=0, hot=False):
    """小灵 = 机器狗；walk = 往右走多少像素；hot = 头顶冒火（电机热）。"""
    i = uid("dg")
    E = cute_dogbot(x, y, k, a, idp=i, mood=mood, load=load) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if walk:
        E.append(sh(a, [i + "*"], walk, -walk * 0.45, d + 0.4, 2.2))
    if hot:
        for q, dx in enumerate((-70, 30)):
            E += ic(a, "flame", x + dx * k, y - 420 * k, 70 * k, d + 0.2 + 0.1 * q, mv="wig", c="red")
    return E


def stairs(a, x, y, n=6, w=150, h=70, d=0.0, c="ink", messy=False):
    """一段台阶（从左下往右上）；messy = 高低宽窄不一。"""
    i = uid("st")
    hs = [h, h * 1.5, h * 0.7, h * 1.3, h * 0.9, h * 1.6, h * 0.8, h * 1.2] if messy else [h] * n
    ws = [w, w * 0.7, w * 1.3, w * 0.8, w * 1.2, w * 0.6, w, w * 0.9] if messy else [w] * n
    p, cx, cy = f"M{x},{y}", x, y
    for q in range(n):
        cy -= hs[q]
        p += f" L{cx},{cy}"
        cx += ws[q]
        p += f" L{cx},{cy}"
    return [P(a, p, c=c, w=8, idp=i), {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "x", "pivot": [x, y], "dur": 0.6, "delay": d}]


def mountain(a, x, y, s=1.0, d=0.0):
    i, j = uid("mt"), uid("mf")
    E = [P(a, f"M{x - 380 * s},{y} L{x - 120 * s},{y - 330 * s} L{x - 30 * s},{y - 250 * s} L{x + 90 * s},{y - 430 * s} L{x + 400 * s},{y}", c="green", w=8, idp=i),
         {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x, y], "dur": 0.6, "delay": d},
         P(a, f"M{x + 90 * s},{y - 430 * s} L{x + 90 * s},{y - 530 * s} L{x + 170 * s},{y - 500 * s} L{x + 90 * s},{y - 470 * s}", c="red", w=6, idp=j),
         pop(a, j, d + 0.5), wig(a, j, (x + 90 * s, y - 430 * s), 6, 2.0)]
    return E


def box(a, x, y, s=120, d=0.0, c="red", lift=0, label=None):
    i = uid("bx")
    E = [R(a, x - s / 2, y - s, s, s, c="ink", fill=c, idp=i), pop(a, i, d)]
    if label:
        E.append(txt(x, y - s / 2 + 15, s * 0.35, label, a, c="paper", id=i, font="en"))
    if lift:
        E.append(sh(a, i, lift * 0.8, -lift, d + 0.3, 0.9))
    return E


def shelf(a, x, y, n=4, w=300, h=120, d=0.0):
    i = uid("sf")
    p = " ".join(f"M{x},{y - h * q} L{x + w},{y - h * q}" for q in range(n + 1)) + f" M{x},{y} L{x},{y - h * n} M{x + w},{y} L{x + w},{y - h * n}"
    return [P(a, p, c="ink", w=6, idp=i), pop(a, i, d)]


def stool(a, x, y, legs=3, d=0.0, wobble=False):
    i = uid("so")
    xs = [-90, 0, 90] if legs == 3 else ([-60, 60] if legs == 2 else [0])
    p = f"M{x - 130},{y - 200} L{x + 130},{y - 200} " + " ".join(f"M{x + v * 0.6},{y - 200} L{x + v * 1.3},{y}" for v in xs)
    E = [P(a, p, c="ink", w=10, idp=i), pop(a, i, d)]
    E.append(wig(a, i, (x, y), 14 if wobble else 1, 2.5 if wobble else 0.5))
    return E


def man(a, x, y, k=1.4, d=0.0, arms="down"):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "bob", "targets": [i + "*"], "amp": 6, "hz": 1.6}]


def porter(a, x, y, k=1.3, d=0.0):
    """挑山工：小人 + 扁担 + 两个担子，扁担一颤一颤。"""
    i, j = uid("pt"), uid("pb")
    E = man(a, x, y, k, d)
    E += [P(a, f"M{x - 160 * k},{y - 150 * k} L{x + 160 * k},{y - 150 * k}", c="gold", w=9, idp=j),
          R(a, x - 200 * k, y - 120 * k, 80 * k, 70 * k, c="ink", fill="red", idp=j), R(a, x + 120 * k, y - 120 * k, 80 * k, 70 * k, c="ink", fill="red", idp=j),
          pop(a, j, d + 0.2), wig(a, j, (x, y - 150 * k), 5, 2.4)]
    return E


def bot(a, x, y, k=1.0, d=0.0, shake=False):
    i = uid("hb")
    E = cute_bot(x, y, k, a, idp=i) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if shake:
        E.append({"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": 7, "hz": 2.5})
    return E


def motor(a, x, y, r=70, d=0.0, rpm=120, c="blue"):
    i, j = uid("mo"), uid("mr")
    return [O(a, x, y, r, c="ink", fill=c, idp=j), pop(a, j, d),
            P(a, f"M{x - r * 0.7},{y} L{x + r * 0.7},{y} M{x},{y - r * 0.7} L{x},{y + r * 0.7}", c="paper", w=8, idp=i), pop(a, i, d + 0.1), spin(a, i, (x, y), rpm)]


def battery(a, x, y, d=0.0, drain=True):
    i, j = uid("bt"), uid("bl")
    E = [R(a, x - 70, y - 200, 140, 260, c="ink", idp=i, sw=7), R(a, x - 25, y - 225, 50, 25, c="ink", fill="ink", idp=i), pop(a, i, d),
         R(a, x - 55, y - (60 if drain else 180), 100, 60 if drain else 180, c="green" if not drain else "red", fill="green" if not drain else "red", idp=j)]
    E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y + 45], "dur": 1.0, "delay": d + 0.2})
    return E


def spark(a, x, y, n=4, d=0.0, c="red"):
    """电流小点沿导线跑。"""
    E = []
    for q in range(n):
        i = uid("sp")
        E += [O(a, x, y, 12, c=c, fill=c, idp=i), pop(a, i, d + 0.15 * q), sh(a, i, 360, 0, d + 0.2 + 0.25 * q, 1.0)]
    return E


def coins(a, x, y, n=4, d=0.0, step=0.25):
    E = []
    for q in range(n):
        i = uid("cn")
        E += [O(a, x + 70 * q, y, 34, c="ink", fill="gold", idp=i), pop(a, i, d + step * q), bob(a, i, 6, 1.5)]
    return E


# ---------- boards ----------
bd(0, mountain(0, 960, 950, 1.3, 0.0), dog(0, 560, 900, 0.8, 0.2, load="70kg", walk=420), BIG(0, 1450, 300, "70 公斤", c="red", d=0.3, s=130))
bd(0.5, mountain(0.5, 1200, 950, 1.1, 0.0), dog(0.5, 500, 900, 0.9, 0.1, load="70kg", walk=300), BIG(0.5, 600, 250, "泰山", c="green", d=0.3, s=130))
bd(1, BIG(1, 960, 280, "70 公斤 = ?", c="ink", d=0.0, s=120), dog(1, 700, 850, 1.0, 0.2, load="70kg"), ic(1, "question", 1400, 600, 180, 0.3, mv="wig", c="red"))
bd(1.5, dog(1.5, 650, 900, 1.1, 0.0, mood="sad"), man(1.5, 640, 470, 0.9, 0.2), BIG(1.5, 1400, 450, "一个大人", c="red", d=0.3, s=110))
bd(2, ic(2, "clock", 450, 450, 180, 0.0, mv="spin"), BIG(2, 1150, 350, "11 月 2 日", c="ink", d=0.1, s=110), mountain(2, 1150, 950, 0.8, 0.2))
bd(2.5, dog(2.5, 650, 850, 1.0, 0.0, load="70kg"), BIG(2.5, 1350, 400, "负重赛冠军", c="red", d=0.2, s=100), star(2.5, 1350, 620, 0.4, r=50), star(2.5, 1150, 700, 0.6, r=30))
bd(3, T(3, 960, 230, 60, "据报道", c="muted", d=0.0), bar(3, 700, 900, 160, 300, "green", 0.2), T(3, 780, 950, 50, "额定 50", d=0.2), bar(3, 1050, 900, 160, 420, "red", 0.4),
   T(3, 1130, 950, 50, "比赛 70", c="red", d=0.4), dog(3, 1550, 850, 0.6, 0.5))
bd(3.5, dog(3.5, 800, 880, 1.2, 0.0, load="70kg", mood="sad"), BIG(3.5, 1450, 400, "超载！", c="red", d=0.3, s=130), ic(3.5, "flame", 1450, 650, 140, 0.4, mv="wig", c="red"))
bd(4, BIG(4, 1150, 360, "烧脑问题", c="red", d=0.0, s=130), ic(4, "question", 450, 450, 260, 0.2, mv="wig", c="red"), dog(4, 1250, 900, 0.8, 0.3))
bd(4.5, mountain(4.5, 700, 950, 1.0, 0.0), dog(4.5, 500, 900, 0.6, 0.1, load="70", walk=250), BIG(4.5, 1450, 450, "累不累？", c="red", d=0.4, s=120))
bd(5, dog(5, 750, 820, 1.5, 0.0), T(5, 1450, 350, 90, "小灵", c="blue", d=0.2), star(5, 1450, 550, 0.4, r=40))
bd(5.5, dog(5.5, 650, 850, 1.2, 0.0), BIG(5.5, 1400, 400, "四条腿", c="blue", d=0.2, s=120), check(5.5, 1400, 650, d=0.5))
bd(6, man(6, 500, 800, 1.6, 0.0, arms="up"), cross(6, 500, 500, d=0.3), T(6, 500, 900, 56, "肌肉", c="red", d=0.2), dog(6, 1250, 850, 1.0, 0.2))
bd(6.5, dog(6.5, 550, 850, 1.0, 0.0), motor(6.5, 1150, 500, 80, 0.2), motor(6.5, 1400, 500, 80, 0.3, c="gold"), motor(6.5, 1275, 720, 80, 0.4, c="green"), T(6.5, 1275, 900, 60, "电机", c="blue", d=0.5))
bd(7, mountain(7, 960, 950, 1.0, 0.0), ic(7, "question", 1550, 400, 160, 0.3, mv="wig", c="red"), T(7, 400, 350, 64, "爬山 = ?", d=0.2))
bd(7.5, box(7.5, 600, 850, 160, 0.0, lift=300), arr(7.5, 950, 850, 950, 400, c="red", d=0.3), BIG(7.5, 1400, 450, "往高处搬", c="red", d=0.4, s=110))
bd(8, stairs(8, 300, 950, 5, 200, 120, 0.0), box(8, 400, 830, 110, 0.3, lift=150), T(8, 1300, 300, 64, "每一级台阶", d=0.2))
bd(8.5, shelf(8.5, 700, 950, 4, 400, 150, 0.0), box(8.5, 900, 950, 120, 0.2, lift=150), box(8.5, 1500, 800, 120, 0.4, c="blue", lift=150), T(8.5, 1500, 300, 60, "上一层货架", c="blue", d=0.3))
bd(9, BIG(9, 960, 330, "物理课", c="ink", d=0.0, s=110), ic(9, "atom", 500, 700, 180, 0.2, mv="spin"), ic(9, "ruler", 1400, 700, 180, 0.3, mv="wig"))
bd(9.5, BIG(9.5, 960, 330, "功 = 重量 × 高度", c="red", d=0.0, s=100), box(9.5, 600, 850, 140, 0.3, lift=200), arr(9.5, 1300, 900, 1300, 550, c="blue", d=0.5))
bd(10, T(10, 960, 230, 60, "估算", c="muted", d=0.0), box(10, 600, 900, 160, 0.1, label="70kg", lift=250), arr(10, 1000, 900, 1000, 500, c="blue", d=0.3), T(10, 1200, 700, 64, "1 米", c="blue", d=0.4))
bd(10.5, BIG(10.5, 960, 400, "≈ 700 焦", c="red", d=0.0, s=150), ic(10.5, "battery", 500, 750, 150, 0.2, mv="wig"), ic(10.5, "flame", 1420, 750, 150, 0.3, mv="wig", c="red"))
bd(11, stairs(11, 400, 900, 4, 260, 100, 0.0), T(11, 1350, 300, 60, "一级十几厘米", d=0.2), dog(11, 500, 800, 0.5, 0.3, walk=250))
bd(11.5, BIG(11.5, 1300, 400, "一级 100 多焦", c="red", d=0.1, s=100), stairs(11.5, 300, 950, 5, 160, 90, 0.0), coins(11.5, 1150, 700, 5, 0.3))
bd(16, BIG(16, 960, 360, "反转一", c="red", d=0.0, s=150), dog(16, 500, 900, 0.6, 0.2, walk=150), ic(16, "clock", 1450, 650, 160, 0.3, mv="spin"))
bd(16.5, dog(16.5, 450, 850, 0.7, 0.0, walk=200), ic(16.5, "clock", 1250, 500, 160, 0.2, mv="spin"), BIG(16.5, 1250, 800, "一分不少", c="red", d=0.4, s=100))
bd(17, stairs(17, 300, 950, 6, 160, 100, 0.0), dog(17, 400, 850, 0.5, 0.2, walk=700), T(17, 1450, 280, 64, "一口气冲", c="red", d=0.2))
bd(17.5, stairs(17.5, 300, 950, 6, 160, 100, 0.0), [ic(17.5, "clock", 400 + 170 * q, 850 - 100 * q, 70, 0.2 + 0.12 * q, mv="spin") for q in range(5)],
   BIG(17.5, 1450, 350, "一样多", c="green", d=0.6, s=110))
bd(18, bar(18, 600, 900, 140, 450, "red", 0.1), T(18, 670, 950, 50, "快", c="red", d=0.1), bar(18, 900, 900, 140, 150, "blue", 0.3), T(18, 970, 950, 50, "慢", c="blue", d=0.3),
   ic(18, "clock", 1450, 500, 160, 0.4, mv="spin"))
bd(18.5, BIG(18.5, 960, 380, "功率", c="red", d=0.0, s=150), T(18.5, 960, 560, 60, "每秒花多少", d=0.2), motor(18.5, 500, 780, 80, 0.3, rpm=300), motor(18.5, 1420, 780, 80, 0.4, rpm=60, c="green"))
bd(19, T(19, 960, 250, 70, "就像花钱", c="ink", d=0.0), coins(19, 600, 550, 6, 0.2, 0.15), ic(19, "phone", 1450, 600, 150, 0.4, mv="wig"))
bd(19.5, coins(19.5, 450, 500, 6, 0.0, 0.05), T(19.5, 620, 650, 56, "一次付", c="red", d=0.2), coins(19.5, 1150, 500, 6, 0.3, 0.3), T(19.5, 1320, 650, 56, "分期付", c="blue", d=0.4),
   BIG(19.5, 960, 880, "总价一样", c="green", d=0.6, s=90))
bd(20, dog(20, 600, 850, 1.0, 0.0), bot(20, 1350, 900, 1.2, 0.1), T(20, 960, 230, 64, "四条腿？两条腿？", d=0.2))
bd(20.5, BIG(20.5, 600, 400, "4", c="blue", d=0.0, s=160), BIG(20.5, 1300, 400, "2", c="red", d=0.2, s=160), ic(20.5, "question", 960, 700, 160, 0.3, mv="wig", c="red"))
bd(21, stool(21, 960, 850, 3, 0.0), T(21, 960, 300, 64, "想想凳子", d=0.2), ic(21, "question", 1450, 550, 140, 0.3, mv="wig", c="red"))
bd(21.5, stool(21.5, 600, 850, 3, 0.0), T(21.5, 600, 950, 56, "三条腿", c="green", d=0.1), check(21.5, 600, 450, d=0.3), stool(21.5, 1350, 850, 1, 0.2, wobble=True),
   T(21.5, 1350, 950, 56, "一条腿", c="red", d=0.3), cross(21.5, 1350, 450, d=0.5))
bd(22, dog(22, 700, 850, 1.3, 0.0), T(22, 1450, 350, 64, "抬一条腿", d=0.2), BIG(22, 1450, 600, "还剩 3", c="green", d=0.4, s=110))
bd(22.5, dog(22.5, 700, 850, 1.3, 0.0), P(22.5, "M520,850 L780,850 L640,850", c="green", w=10), T(22.5, 1450, 400, 64, "三角形撑着", c="green", d=0.2), check(22.5, 1450, 620, d=0.4))
bd(23, bot(23, 700, 900, 1.4, 0.0, shake=True), T(23, 1350, 350, 64, "两条腿抬一条", d=0.2), ic(23, "question", 1350, 600, 140, 0.3, mv="wig", c="red"))
bd(23.5, bot(23.5, 600, 900, 1.3, 0.0, shake=True), BIG(23.5, 1350, 400, "只剩一个点", c="red", d=0.2, s=100), stool(23.5, 1350, 900, 1, 0.4, wobble=True))
bd(24, dog(24, 650, 850, 1.1, 0.0, load="70kg"), BIG(24, 1400, 400, "四条腿占便宜", c="green", d=0.2, s=90), star(24, 1400, 620, 0.4, r=40), star(24, 1200, 700, 0.6, r=26))
bd(24.5, dog(24.5, 550, 850, 1.0, 0.0, load="70kg"), bot(24.5, 1350, 900, 1.0, 0.1, shake=True), check(24.5, 550, 350, d=0.3), ic(24.5, "flame", 1350, 400, 120, 0.4, mv="wig", c="red"))
bd(27, BIG(27, 960, 360, "反转二", c="red", d=0.0, s=150), dog(27, 500, 900, 0.7, 0.2), ic(27, "battery", 1450, 650, 160, 0.3, mv="wig"))
bd(27.5, dog(27.5, 600, 850, 1.1, 0.0, load="70kg"), BIG(27.5, 1400, 400, "站着也耗电", c="red", d=0.2, s=100), battery(27.5, 1400, 850, 0.3))
bd(28, BIG(28, 960, 300, "物理课的定义", c="ink", d=0.0, s=100), box(28, 960, 800, 180, 0.2), arr(28, 960, 600, 960, 400, c="muted", d=0.4), cross(28, 1250, 500, d=0.5))
bd(28.5, BIG(28.5, 960, 380, "功 = 0", c="blue", d=0.0, s=160), box(28.5, 500, 850, 140, 0.2), ic(28.5, "atom", 1420, 750, 150, 0.3, mv="spin"))
bd(29, motor(29, 600, 550, 120, 0.0, rpm=0), spark(29, 800, 550, 5, 0.2), ic(29, "flame", 1400, 550, 160, 0.4, mv="wig", c="red"), T(29, 960, 300, 64, "使劲撑住", d=0.2))
bd(29.5, spark(29.5, 400, 500, 5, 0.0), BIG(29.5, 1300, 450, "全变成热", c="red", d=0.2, s=110), ic(29.5, "thermometer", 1300, 750, 160, 0.3, mv="wig", c="red"))
bd(30, man(30, 650, 850, 1.7, 0.0, arms="up"), R(30, 560, 330, 180, 130, c="ink", fill="blue"), ic(30, "water", 650, 290, 100, 0.2, mv="wig", c="blue"), T(30, 1350, 400, 64, "端着一桶水", d=0.2))
bd(30.5, man(30.5, 650, 850, 1.7, 0.0, arms="up"), R(30.5, 560, 330, 180, 130, c="ink", fill="blue"), BIG(30.5, 1350, 450, "胳膊酸", c="red", d=0.2, s=120),
   ic(30.5, "flame", 900, 550, 110, 0.4, mv="wig", c="red"))
bd(31, dog(31, 650, 850, 1.1, 0.0), T(31, 1350, 400, 70, "不会“累”", c="green", d=0.2), check(31, 1350, 620, d=0.4))
bd(31.5, dog(31.5, 550, 850, 1.0, 0.0, hot=True, mood="sad"), battery(31.5, 1300, 850, 0.2), T(31.5, 1300, 350, 64, "电机热 电池掉", c="red", d=0.3))
bd(32, BIG(32, 960, 360, "反转三", c="red", d=0.0, s=150), stairs(32, 400, 950, 6, 190, 50, 0.2, messy=True), dog(32, 450, 900, 0.4, 0.3))
bd(32.5, stairs(32.5, 250, 950, 7, 200, 70, 0.0, messy=True), BIG(32.5, 1350, 300, "不是高，是乱", c="red", d=0.3, s=90), ic(32.5, "question", 600, 350, 130, 0.4, mv="wig", c="red"))
bd(33, T(33, 960, 230, 60, "据报道", c="muted", d=0.0), stairs(33, 250, 950, 7, 210, 80, 0.1, messy=True), bot(33, 450, 950, 0.6, 0.3, shake=True))
bd(33.5, stairs(33.5, 250, 950, 6, 200, 80, 0.0, messy=True), ic(33.5, "computer", 1450, 450, 170, 0.2, mv="bob"), T(33.5, 1450, 700, 60, "每步重新算", c="blue", d=0.3),
   ic(33.5, "gear", 1650, 300, 110, 0.4, mv="spin"))
bd(34, dog(34, 650, 850, 1.1, 0.0), ic(34, "eye", 1300, 450, 160, 0.2, mv="wig"), ic(34, "signal", 1550, 650, 150, 0.3, mv="bob", c="blue"), T(34, 1400, 300, 56, "眼睛 + 腿的感觉", d=0.2))
bd(34.5, stairs(34.5, 250, 950, 6, 200, 80, 0.0, messy=True), dog(34.5, 400, 870, 0.55, 0.2, walk=500), T(34.5, 1400, 280, 64, "一步一步“摸”", c="blue", d=0.4))
bd(35, porter(35, 700, 850, 1.5, 0.0), mountain(35, 1450, 950, 0.6, 0.2), T(35, 1400, 280, 64, "挑山工", c="green", d=0.3))
bd(35.5, porter(35.5, 650, 850, 1.4, 0.0), T(35.5, 1350, 250, 56, "据央视报道", c="muted", d=0.1), BIG(35.5, 1350, 450, "30–40 公斤", c="red", d=0.2, s=110))
bd(36, dog(36, 600, 850, 1.0, 0.0, load="70kg"), bar(36, 1150, 900, 120, 200, "green", 0.2), bar(36, 1350, 900, 120, 400, "red", 0.4), T(36, 1210, 950, 44, "人 35", d=0.2), T(36, 1410, 950, 44, "狗 70", c="red", d=0.4))
bd(36.5, BIG(36.5, 960, 400, "力气 ×2", c="red", d=0.0, s=150), dog(36.5, 550, 900, 0.7, 0.2, load="70"), porter(36.5, 1400, 900, 1.0, 0.3))
bd(37, porter(37, 600, 850, 1.3, 0.0), ic(37, "sun", 600, 300, 140, 0.2, mv="spin", c="gold"), ic(37, "moon", 900, 300, 120, 0.4, mv="bob"), T(37, 1400, 450, 64, "挑一整天", c="green", d=0.3))
bd(37.5, dog(37.5, 600, 850, 1.0, 0.0, mood="sad"), battery(37.5, 1150, 850, 0.2), ic(37.5, "battery", 1500, 600, 160, 0.4, mv="wig"), T(37.5, 1350, 300, 64, "得找地方充电", c="red", d=0.4))
bd(40, BIG(40, 960, 330, "友情提示", c="blue", d=0.0, s=130), T(40, 960, 520, 56, "70 公斤、额定 50：据报道", c="ink", d=0.2), ic(40, "magnifier", 500, 780, 150, 0.3, mv="wig"), dog(40, 1450, 900, 0.5, 0.4))
bd(40.5, BIG(40.5, 960, 350, "700 焦 / 100 多焦", c="ink", d=0.0, s=100), T(40.5, 960, 550, 60, "估算", c="muted", d=0.2), ic(40.5, "ruler", 500, 780, 150, 0.3, mv="wig"), ic(40.5, "atom", 1420, 780, 150, 0.4, mv="spin"))
bd(41, ic(41, "clock", 600, 550, 200, 0.0, mv="spin"), T(41, 1300, 450, 64, "一天的成绩", d=0.2), star(41, 1300, 650, 0.4, r=40))
bd(41.5, mountain(41.5, 960, 950, 1.0, 0.0), dog(41.5, 450, 900, 0.5, 0.2, walk=200), T(41.5, 1450, 300, 56, "天天干活还远", c="red", d=0.4))
bd(42, dog(42, 650, 850, 1.1, 0.0, load="70kg"), ic(42, "question", 1350, 400, 180, 0.2, mv="wig", c="red"), T(42, 1350, 650, 64, "累不累？", c="red", d=0.3))
bd(42.5, dog(42.5, 550, 850, 1.0, 0.0, hot=True), check(42.5, 550, 300, d=0.2), battery(42.5, 1150, 850, 0.3), T(42.5, 1400, 350, 56, "只会热、只会没电", c="red", d=0.4))
bd(43, mountain(43, 960, 950, 1.2, 0.0), stairs(43, 400, 950, 6, 120, 60, 0.2), dog(43, 450, 900, 0.4, 0.3, walk=500))
bd(43.5, stairs(43.5, 250, 950, 6, 200, 100, 0.0), [box(43.5, 330 + 200 * q, 950 - 100 * (q + 1), 70, 0.2 + 0.1 * q) for q in range(6)],
   BIG(43.5, 600, 300, "一级一级“抬”", c="red", d=0.6, s=100), star(43.5, 1500, 300, 0.8, r=44))

bd(12, mountain(12, 960, 950, 1.3, 0.0), dog(12, 500, 900, 0.5, 0.2, load="70", walk=500), BIG(12, 1500, 300, "山顶", c="red", d=0.3, s=110))
bd(12.5, BIG(12.5, 960, 330, "1000 多米", c="red", d=0.0, s=140), T(12.5, 960, 520, 60, "估算", c="muted", d=0.2), arr(12.5, 500, 950, 500, 450, c="blue", d=0.3), mountain(12.5, 1350, 950, 0.7, 0.4))
bd(13, box(13, 550, 900, 160, 0.0, label="70kg", lift=300), arr(13, 900, 900, 900, 400, c="blue", d=0.2), T(13, 1350, 300, 60, "抬 1000 多米", d=0.3), coins(13, 1150, 700, 4, 0.4))
bd(13.5, BIG(13.5, 960, 380, "≈ 100 万焦", c="red", d=0.0, s=150), ic(13.5, "flame", 500, 750, 150, 0.2, mv="wig", c="red"), ic(13.5, "battery", 1420, 750, 150, 0.3, mv="wig"))
bd(14, BIG(14, 960, 300, "100 万焦 = ?", c="ink", d=0.0, s=110), ic(14, "question", 500, 650, 160, 0.2, mv="wig", c="red"), dog(14, 1350, 900, 0.7, 0.3))
bd(14.5, [battery(14.5, 500 + 300 * q, 850, 0.1 * q, drain=False) for q in range(4)], BIG(14.5, 960, 300, "≈ 4 块充电宝", c="green", d=0.5, s=110))
bd(15, dog(15, 600, 850, 1.1, 0.0, hot=True), motor(15, 1250, 500, 90, 0.2, rpm=300), spark(15, 1100, 750, 4, 0.3), T(15, 1350, 300, 60, "发热 + 找平衡", c="red", d=0.3))
bd(15.5, bar(15.5, 650, 900, 150, 120, "green", 0.0), T(15.5, 725, 950, 48, "理论", d=0.0), bar(15.5, 950, 900, 150, 450, "red", 0.3), T(15.5, 1025, 950, 48, "实际", c="red", d=0.3), BIG(15.5, 1450, 400, "推测", c="blue", d=0.5, s=110))
bd(25, bot(25, 700, 900, 1.4, 0.0, shake=True), ic(25, "question", 1350, 450, 170, 0.2, mv="wig", c="red"), T(25, 1350, 700, 64, "人形机器人呢？", d=0.3))
bd(25.5, T(25.5, 960, 230, 56, "据报道", c="muted", d=0.0), stairs(25.5, 250, 950, 6, 210, 80, 0.1, messy=True), bot(25.5, 400, 950, 0.55, 0.2), ic(25.5, "clock", 1600, 400, 140, 0.3, mv="spin"))
bd(26, bot(26, 600, 900, 1.3, 0.0, shake=True), BIG(26, 1350, 400, "两条腿难", c="red", d=0.2, s=110), stool(26, 1350, 900, 1, 0.3, wobble=True))
bd(26.5, stairs(26.5, 250, 950, 5, 200, 100, 0.0), man(26.5, 400, 850, 1.0, 0.2), bot(26.5, 900, 750, 0.6, 0.3), T(26.5, 1450, 300, 56, "路是给两条腿修的", c="blue", d=0.4), check(26.5, 1450, 500, d=0.6))
bd(38, man(38, 650, 850, 1.7, 0.0), P(38, "M600,850 L620,700 L600,560 M700,850 L680,700 L700,560", c="gold", w=12), motor(38, 650, 700, 40, 0.2, rpm=200), T(38, 1350, 400, 64, "助力外骨骼", c="gold", d=0.3))
bd(38.5, ic(38.5, "clock", 550, 500, 200, 0.0, mv="spin"), BIG(38.5, 1300, 400, "约 1 小时", c="red", d=0.2, s=120), mountain(38.5, 1300, 950, 0.5, 0.3))
bd(39, dog(39, 600, 850, 1.0, 0.0, load="70kg"), cross(39, 600, 300, d=0.3), T(39, 1350, 450, 64, "不一定替人爬", d=0.2), man(39, 1350, 900, 1.0, 0.3))
bd(39.5, man(39.5, 700, 900, 1.6, 0.0), motor(39.5, 700, 720, 40, 0.1, rpm=200), dog(39.5, 1150, 900, 0.6, 0.2), BIG(39.5, 1400, 330, "帮人爬", c="green", d=0.3, s=120), star(39.5, 1600, 550, 0.5, r=40))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"70kg": "七十公斤", "11月2日": "十一月二日"})
