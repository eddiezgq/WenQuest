"""每日科普 2026-10-21（中文）：《老鼠戴上1克“脑相机”》
新闻（新浪科学热点小时报 2026-10-21 02时 第4条“1克！中国造微型‘脑探测器’如何‘读懂大脑’”；新华网 2026-10-19）：
清华大学戴琼海团队与解放军总医院戴朴团队研制 Airscope，世界最轻无线介观显微镜，约1克（常规头戴式微型显微镜通常超过3克），
《自然》2026-10-19 在线发表；视野6毫米，单细胞分辨率约4–6微米，单只小鼠同时记录8500多个神经元，是同类设备的25倍；
无线，200万像素传感器在设备端压缩图像；仅用4片非球面镜片；在5平方米自然栖息地同时记录多只小鼠皮层活动，在32个末端的迷宫追踪自主探索；
未来可能拓展到免疫、肿瘤等领域。出处：news.cn/tech/20261019/b9491857c35341c9a0c5ae5505f1a0a2/c.html；news.bjd.com.cn/2026/10/19/12001296.shtml
科学（常识）：钙成像——让神经元带上会发光的蛋白，放电时亮一下；小鼠体重约二三十克。
我们的估算：3克 ÷ 30克 ≈ 十分之一体重，换成60公斤的人≈6公斤；1克≈三十分之一，≈2公斤（一大瓶水）。对机器人的启发是我们的推测。
角色：米米，一只小鼠（贯穿的梗：米米的帽子会闪）。没有手。
    python3 make.py <kokoro 模型目录> | --fake | --boards-only   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("一只老鼠，头顶戴着一台显微镜，|只有1克重。", "A mouse wears a microscope on its head | that weighs just 1 gram."),
 ("它一边跑，|科学家一边同时看它8500多个神经元在闪。", "While it runs around, | scientists watch more than 8,500 of its neurons flash at once."),
 ("今天的问题：看老鼠的大脑，|为什么非得让它自己背着显微镜跑？", "Today's question: to look inside a mouse's brain, | why make the mouse carry the microscope?"),
 ("认识一下米米。|米米是一只小鼠，今天它当主角。", "Meet Mimi. | Mimi is a mouse, and today Mimi is the star."),
 ("这台显微镜叫 Airscope，|是清华大学和解放军总医院的团队做的。", "The microscope is called Airscope, | built by teams at Tsinghua University and the PLA General Hospital."),
 ("10月19日，|它登上了《自然》杂志。", "On October 19, | it was published in Nature."),
 ("先说神经元怎么“看”：|它们平时根本看不见。", "First, how do you even see neurons? | Normally you can't."),
 ("科学家常用的办法是，|让神经元带上一种会发光的蛋白。", "A common trick is to give neurons | a protein that glows."),
 ("神经元一放电，就亮一下，|像一栋楼的灯一盏盏开关。", "When a neuron fires, it lights up, | like windows in a building switching on and off."),
 ("拍下这些闪光，|就等于偷看大脑在说什么。", "Film those flashes, | and you're eavesdropping on the brain."),
 ("可老办法常常是：把老鼠的头固定住，|放在大显微镜底下。", "But the old way often means holding the mouse's head still | under a big microscope."),
 ("就像让你一动不动躺着，|还要求你“自然地”逛街。", "It's like lying perfectly still | and being told to go shopping naturally."),
 ("反转一：重量。|一只小鼠，大约只有二三十克。", "Twist one: weight. | A mouse weighs only about 20 to 30 grams."),
 ("常见的头戴显微镜超过3克，|差不多是体重的十分之一。", "Typical head-mounted microscopes weigh over 3 grams, | about a tenth of its body weight."),
 ("我们估算一下：换成60公斤的人，|等于头顶扛着6公斤的西瓜。", "Our rough estimate: for a 60-kilogram person, | that's a 6-kilogram watermelon on your head."),
 ("现在只有1克，|大约相当于人顶一大瓶水。", "Now it's 1 gram, | more like balancing a big bottle of water."),
 ("反转二：线。|很多老设备要拖着一根线。", "Twist two: wires. | Many older devices trail a cable."),
 ("线会缠，会绊，|几只老鼠一起玩，就打成一团毛线。", "Cables tangle and trip. | Put a few mice together and you get a ball of yarn."),
 ("Airscope 是无线的，|在头上先把图压缩，再发出去。", "Airscope is wireless. | It compresses images on its head, then sends them out."),
 ("200万像素的传感器，|只用了4片镜片。", "A 2-megapixel sensor, | with just 4 lenses."),
 ("视野6毫米，|能看清一个一个细胞。", "A 6-millimeter field of view, | sharp enough to see single cells."),
 ("一只老鼠同时记下8500多个神经元，|是同类设备的25倍。", "Over 8,500 neurons recorded in one mouse at once, | 25 times more than similar devices."),
 ("反转三，最烧脑：|看到更多，为什么这么重要？", "Twist three, the brain-bender: | why does seeing more matter so much?"),
 ("因为行为不是一个神经元干的，|是成千上万个一起合唱。", "Because behavior isn't done by one neuron. | It's thousands singing together."),
 ("只听一个人唱，|你听不出是哪首歌。", "Listen to just one singer, | and you can't tell the song."),
 ("团队在5平方米的“小区”里，|同时记录好几只老鼠的大脑。", "In a 5-square-meter habitat, | the team recorded several mice at the same time."),
 ("还让它们在有32个出口的大迷宫里，|自己随便逛。", "They also let mice roam freely | in a big maze with 32 dead ends."),
 ("老鼠自由社交、自由探索，|大脑才说真话。", "When mice can socialize and explore freely, | their brains tell the truth."),
 ("我们猜：看懂动物怎么找路，|也许能帮机器人学会探索。", "Our guess: understanding how animals find their way | might help robots learn to explore."),
 ("友情提示：这是动物实验，|看的是大脑表层，不是读心术。", "Friendly fine print: this is animal research. | It sees the brain's surface layer, not your thoughts."),
 ("离用在人身上，|还很远。", "Using it on people | is still a long way off."),
 ("团队说，以后还想用它|研究免疫和肿瘤。", "The team says they hope to use it | for immunity and cancer research, too."),
 ("米米表示：帽子很轻，|就是脑子一直在闪。", "Mimi says: the hat is light. | It's just that the brain keeps flashing."),
]
TITLE = {"zh": "老鼠戴上1克“脑相机”", "en": "A Mouse Wearing a 1-Gram Brain Camera"}


def mouse(a, x, y, k=1.0, cap=True, c="ink"):
    """米米：圆身子、大耳朵、尾巴会摆、眼睛；cap=True 头顶戴着小显微镜，镜头一闪一闪。"""
    i = uid("ms") + "_"
    tl, ear, lp = i + "t", i + "e", i + "l"
    E = [O(a, x, y, 110 * k, c=c, fill="muted", idp=i),
         O(a, x - 70 * k, y - 110 * k, 45 * k, c=c, fill="muted", idp=ear), O(a, x + 70 * k, y - 110 * k, 45 * k, c=c, fill="muted", idp=ear),
         O(a, x - 35 * k, y - 20 * k, 10 * k, c="ink", fill="ink", idp=i), O(a, x + 35 * k, y - 20 * k, 10 * k, c="ink", fill="ink", idp=i),
         O(a, x, y + 15 * k, 12 * k, c="red", fill="red", idp=i),
         P(a, f"M{x - 20 * k},{y + 40 * k} Q{x},{y + 55 * k} {x + 20 * k},{y + 40 * k} M{x - 50 * k},{y + 15 * k} L{x - 110 * k},{y + 5 * k} "
              f"M{x + 50 * k},{y + 15 * k} L{x + 110 * k},{y + 5 * k}", c="ink", w=3, idp=i),
         P(a, f"M{x + 100 * k},{y + 50 * k} Q{x + 200 * k},{y + 20 * k} {x + 190 * k},{y + 110 * k} Q{x + 180 * k},{y + 170 * k} {x + 250 * k},{y + 150 * k}",
           c=c, w=5, idp=tl),
         bob(a, i, 6 * k, 1.4), wig(a, tl, (x + 100 * k, y + 50 * k), 12, 2.2), wig(a, ear, (x, y - 100 * k), 4, 1.6)]
    if cap:
        E += [R(a, x - 30 * k, y - 190 * k, 60 * k, 80 * k, c="blue", fill="blue", idp=i), O(a, x, y - 200 * k, 18 * k, c="gold", fill="gold", idp=lp),
              pulse(a, lp, 0.2, 0.5), pulse(a, lp, 1.0, 0.5), pulse(a, lp, 1.8, 0.5)]
    return E, i


def neuron(a, x, y, k=1.0, d=0.0, c="green", fire=(0.3,)):
    """一个神经元：细胞体 + 几根突起；fire 的时刻亮一下。"""
    i = uid("nr")
    E = [O(a, x, y, 26 * k, c=c, fill=c, idp=i),
         P(a, f"M{x - 26 * k},{y} L{x - 70 * k},{y - 30 * k} M{x + 26 * k},{y} L{x + 75 * k},{y + 20 * k} M{x},{y + 26 * k} L{x - 10 * k},{y + 75 * k} "
              f"M{x},{y - 26 * k} L{x + 20 * k},{y - 70 * k}", c=c, w=4, idp=i), pop(a, i, d), wig(a, i, (x, y), 6, 1.3)]
    E += [pulse(a, i, f, 0.4) for f in fire]
    return E


def neurons(a, x0, y0, cols, rows, gap=150, k=0.7, d=0.0, step=0.03):
    E = []
    for r in range(rows):
        for q in range(cols):
            n = r * cols + q
            E += neuron(a, x0 + q * gap + (r % 2) * gap / 2, y0 + r * gap * 0.8, k, d + step * n, c=["green", "gold", "blue"][n % 3],
                        fire=(0.4 + 0.13 * (n % 7), 1.2 + 0.11 * (n % 5)))
    return E


def scope(a, x, y, k=1.0, d=None, c="blue"):
    """小显微镜：镜筒 + 镜头 + 闪光。"""
    i, lp = uid("sc"), uid("lamp")
    E = [R(a, x - 60 * k, y - 160 * k, 120 * k, 220 * k, c="ink", fill=c, idp=i), R(a, x - 90 * k, y + 60 * k, 180 * k, 50 * k, c="ink", idp=i),
         O(a, x, y - 190 * k, 30 * k, c="gold", fill="gold", idp=lp), pulse(a, lp, 0.3, 0.5), pulse(a, lp, 1.1, 0.5), bob(a, i, 5 * k, 1.1)]
    if d is not None:
        E.append(pop(a, i, d))
    return E, i


def building(a, x, y, d=0.0):
    """一栋楼，窗户的灯一盏盏亮。"""
    E = [R(a, x - 220, y - 300, 440, 600, c="ink", idp=uid("bd"))]
    for r in range(4):
        for q in range(3):
            w = uid("win")
            E += [R(a, x - 170 + 120 * q, y - 250 + 140 * r, 90, 90, c="gold", fill="gold", idp=w), pop(a, w, d + 0.1 * ((r * 3 + q) * 7 % 12)),
                  pulse(a, w, d + 0.6 + 0.08 * ((r * 3 + q) * 5 % 12), 0.4)]
    return E


def melon(a, x, y, k=1.0, d=0.0):
    i = uid("ml")
    return [O(a, x, y, 110 * k, c="green", fill="green", idp=i), P(a, f"M{x - 60 * k},{y - 90 * k} Q{x},{y} {x - 60 * k},{y + 90 * k} M{x + 40 * k},{y - 100 * k} Q{x + 100 * k},{y} {x + 40 * k},{y + 100 * k}",
                                                                    c="ink", w=4, idp=i), pop(a, i, d), wig(a, i, (x, y + 110 * k), 6, 1.5)]


def bottle(a, x, y, k=1.0, d=0.0):
    i = uid("bt")
    return [R(a, x - 45 * k, y - 120 * k, 90 * k, 220 * k, c="blue", idp=i), R(a, x - 20 * k, y - 160 * k, 40 * k, 40 * k, c="blue", fill="blue", idp=i),
            pop(a, i, d), wig(a, i, (x, y + 100 * k), 5, 1.4)]


def person(a, x, y, k=1.0):
    i = uid("pp")
    return [O(a, x, y - 160 * k, 50 * k, c="ink", idp=i), P(a, f"M{x},{y - 110 * k} L{x},{y + 40 * k} M{x - 70 * k},{y - 60 * k} L{x + 70 * k},{y - 60 * k} "
                                                              f"M{x},{y + 40 * k} L{x - 50 * k},{y + 150 * k} M{x},{y + 40 * k} L{x + 50 * k},{y + 150 * k}", c="ink", w=6, idp=i),
            bob(a, i, 5, 1.0), wig(a, i, (x, y + 150 * k), 4, 1.2)], i


def wire(a, x0, y0, x1, y1, d=0.0, c="ink"):
    i = uid("wr")
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [P(a, f"M{x0},{y0} Q{mx - 200},{my - 250} {mx},{my} Q{mx + 200},{my + 250} {x1},{y1}", c=c, w=5, idp=i), pop(a, i, d),
            wig(a, i, (mx, my), 5, 1.8)]


def yarn(a, x, y, d=0.0):
    i = uid("yn")
    return [O(a, x, y, 120, c="red", idp=i), P(a, f"M{x - 100},{y - 40} Q{x},{y - 160} {x + 100},{y + 40} M{x - 110},{y + 30} Q{x},{y + 160} {x + 90},{y - 70} "
                                                  f"M{x - 60},{y - 90} Q{x + 60},{y} {x - 30},{y + 110}", c="red", w=4, idp=i), pop(a, i, d), spin(a, i, (x, y), 40)]


def maze(a, x, y, s=500, d=0.0):
    i = uid("mz")
    h = s / 2
    path = (f"M{x - h},{y - h} L{x + h},{y - h} L{x + h},{y + h} L{x - h},{y + h} Z M{x - h + s * .2},{y - h} L{x - h + s * .2},{y + h * .4} "
            f"M{x - h + s * .4},{y + h} L{x - h + s * .4},{y - h * .4} M{x - h + s * .6},{y - h} L{x - h + s * .6},{y + h * .2} M{x - h + s * .8},{y + h} L{x - h + s * .8},{y - h * .5}")
    return [P(a, path, c="ink", w=6, idp=i), pop(a, i, d), bob(a, i, 3, 0.7)]


def packets(a, x0, y0, x1, y1, n=3, d=0.2, c="blue"):
    E = []
    for q in range(n):
        i = uid("pk")
        E += [O(a, x0, y0, 14, c=c, fill=c, idp=i), sh(a, i, x1 - x0, y1 - y0, d + 0.3 * q, 0.6)]
    return E


def notes(a, x, y, n=3, d=0.2, c="blue"):
    """音符往上飘。"""
    E = []
    for q in range(n):
        i = uid("nt")
        xx = x + 70 * q
        E += [O(a, xx, y, 16, c=c, fill=c, idp=i), P(a, f"M{xx + 16},{y} L{xx + 16},{y - 60} L{xx + 40},{y - 45}", c=c, w=4, idp=i),
              sh(a, i, 20, -160, d + 0.3 * q, 1.2)]
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

# 0 老鼠头顶显微镜
m, mi = mouse(0, 700, 600, 1.5)
bd(0, m, [pop(0, mi, 0.0)], arr(0, 1100, 300, 780, 330, c="red", d=0.4), T(0, 1350, 300, 64, "显微镜？！", c="red", d=0.5), n=3)
# 0.5 1克
m, mi = mouse(0.5, 600, 620, 1.3)
bd(0.5, m, BIG(0.5, 1300, 420, "1 克", c="red", d=0.2, s=160), bar(0.5, 1240, 860, 120, 160, "blue", d=0.5), T(0.5, 1300, 920, 52, "比一枚一元硬币轻得多", c="muted", d=0.8))
# 1 一边跑
m, mi = mouse(1, 500, 620, 1.1)
bd(1, m, [sh(1, mi + "*", 800, 0, 0.2, 2.5)], [e for q in range(4) for e in packets(1, 300 + 300 * q, 860, 400 + 300 * q, 860, n=1, d=0.2 * q, c="muted")],
   T(1, 960, 200, 64, "它在跑……", c="ink", d=0.3))
# 1.5 8500 神经元在闪
bd(1.5, neurons(1.5, 260, 260, 9, 3, gap=170, k=0.55, d=0.0, step=0.015), BIG(1.5, 960, 860, "8500+", c="green", d=0.5, s=150), n=3)
# 2 看老鼠的大脑
m, mi = mouse(2, 650, 620, 1.3)
bd(2, m, neurons(2, 1250, 400, 3, 2, gap=180, k=0.7, d=0.3), T(2, 1350, 800, 60, "看它的大脑", c="ink", d=0.4))
# 2.5 为什么自己背着
m, mi = mouse(2.5, 650, 620, 1.3)
bd(2.5, m, [rot(2.5, mi + "*", -8, (650, 730), 0.3, 0.6)], Q(2.5, 1150, 300), T(2.5, 1350, 780, 60, "自己背着跑？", c="red", d=0.6))
# 3 认识米米
m, mi = mouse(3, 960, 620, 1.8, cap=False)
bd(3, m, [pop(3, mi + "*", 0.0)], BIG(3, 1500, 360, "米米", c="gold", d=0.4, s=150), star(3, 500, 300, 0.6, r=40), n=3)
# 3.5 今天当主角
m, mi = mouse(3.5, 960, 640, 1.5, cap=False)
sp = uid("spot")
bd(3.5, [P(3.5, "M760,100 L560,900 L1360,900 L1160,100", c="gold", w=5, idp=sp), pulse(3.5, sp, 0.3), pulse(3.5, sp, 1.1)], m,
   [sh(3.5, mi + "*", 0, -50, 0.5, 0.3), sh(3.5, mi + "*", 0, 50, 0.8, 0.3)], T(3.5, 1550, 760, 60, "主角！", c="red", d=0.6))
# 4 Airscope
s, si = scope(4, 700, 560, 1.4, d=0.0)
bd(4, s, BIG(4, 1300, 420, "Airscope", c="blue", d=0.3, s=120), star(4, 1300, 640, 0.6, r=36), T(4, 1300, 780, 56, "世界最轻的无线介观显微镜", c="ink", d=0.7))
# 4.5 清华 + 解放军总医院
E = []
for q, nm in enumerate(["清华大学", "解放军总医院"]):
    hb = uid("hq")
    E += [R(4.5, 330 + 760 * q, 300, 500, 360, c="ink", idp=hb), P(4.5, f"M{300 + 760 * q},300 L{580 + 760 * q},150 L{860 + 760 * q},300", c="ink", w=5, idp=hb),
          pop(4.5, hb, 0.1 + 0.3 * q), bob(4.5, hb, 4, 0.9 + 0.2 * q)]
    E += T(4.5, 580 + 760 * q, 480, 60, nm, c="blue", d=0.2 + 0.3 * q)
bd(4.5, E, arr(4.5, 840, 480, 1080, 480, c="red", d=0.6), arr(4.5, 1080, 520, 840, 520, c="red", d=0.8))
# 5 10月19日
cal = uid("cal")
bd(5, [R(5, 640, 260, 400, 420, c="ink", idp=cal), P(5, "M640,360 L1040,360", c="red", w=10, idp=cal), pop(5, cal, 0.0), wig(5, cal, (840, 260), 4, 1.0)],
   BIG(5, 840, 540, "10.19", c="red", d=0.3, s=110), star(5, 1350, 300, 0.5, r=40), T(5, 1400, 600, 60, "发表", c="ink", d=0.6))
# 5.5 Nature
E = []
for q in range(3):
    pg = uid("pg")
    E += [R(5.5, 700 + 30 * q, 260 + 20 * q, 460, 560, c="ink", fill="muted" if q == 2 else None, idp=pg), pop(5.5, pg, 0.1 + 0.2 * q),
          rot(5.5, pg, 4 * (q - 1), (930, 820), 0.5 + 0.2 * q, 0.4)]
bd(5.5, E, BIG(5.5, 990, 520, "Nature", c="ink", d=0.6, s=100), T(5.5, 990, 920, 56, "《自然》", c="red", d=0.8), n=3)
# 6 神经元怎么看
bd(6, neuron(6, 700, 500, 2.2, d=0.0, fire=(0.5, 1.2)), Q(6, 1150, 300, d=0.4), T(6, 1300, 760, 60, "怎么“看”？", c="ink", d=0.3))
# 6.5 平时看不见
nn = neuron(6.5, 700, 500, 2.2, d=0.0, c="muted", fire=())
bd(6.5, nn, [{"t": "move", "at": 6.5, "kind": "grow", "targets": [nn[0]["id"]], "axis": "both", "from": 1.0, "to": 0.4, "pivot": [700, 500], "dur": 1.0, "delay": 0.3}],
   cross(6.5, 700, 500, d=1.0), T(6.5, 1350, 500, 64, "看不见", c="muted", d=0.4))
# 7 常用的办法
nn = neuron(7, 600, 520, 1.8, d=0.0, c="muted", fire=())
bd(7, nn, arr(7, 900, 520, 1150, 520, c="ink", d=0.3), neuron(7, 1400, 520, 1.8, d=0.6, c="green", fire=(1.0, 1.5)), T(7, 960, 200, 60, "常用的办法", c="ink", d=0.2))
# 7.5 会发光的蛋白
E = []
for q in range(5):
    g = uid("gl")
    E += [O(7.5, 960 + 260 * __import__("math").cos(q * 1.256), 500 + 260 * __import__("math").sin(q * 1.256), 30, c="green", fill="green", idp=g),
          pop(7.5, g, 0.1 + 0.12 * q), pulse(7.5, g, 0.8 + 0.1 * q)]
bd(7.5, neuron(7.5, 960, 500, 1.6, d=0.0, fire=(0.5, 1.3)), E, T(7.5, 960, 880, 60, "会发光的蛋白", c="green", d=0.4))
# 8 放电就亮
bd(8, neuron(8, 600, 500, 2.0, d=0.0, c="gold", fire=(0.3, 0.8, 1.3)), [e for q in range(3) for e in sound(8, 820, 500, 0.8 + 0.2 * q, c="gold", d=0.3 + 0.4 * q)][:6],
   BIG(8, 1400, 480, "亮！", c="gold", d=0.4, s=150))
# 8.5 楼的灯
bd(8.5, building(8.5, 600, 540), T(8.5, 1350, 400, 64, "一盏盏开关", c="gold", d=0.4), neuron(8.5, 1350, 650, 1.0, d=0.6, fire=(1.0, 1.4)))
# 9 拍下闪光
s, si = scope(9, 600, 560, 1.2)
bd(9, s, neurons(9, 1050, 380, 4, 2, gap=170, k=0.6, d=0.2), arr(9, 1000, 500, 720, 400, c="red", d=0.5))
# 9.5 偷看大脑在说什么
m, mi = mouse(9.5, 700, 620, 1.3)
bd(9.5, m, [{"t": "icon", "at": 9.5, "id": (ey := uid("ey")), "name": "eye", "x": 1200, "y": 300, "size": 220, "c": "blue"}, pop(9.5, ey, 0.3),
            wig(9.5, ey, (1310, 410), 6, 1.5)], sound(9.5, 900, 300, 1.0, d=0.4), T(9.5, 1350, 760, 60, "偷看大脑", c="blue", d=0.6))
# 10 老办法：头固定
m, mi = mouse(10, 700, 640, 1.3, cap=False)
clamp = uid("clp")
bd(10, m, [R(10, 560, 330, 280, 60, c="red", fill="red", idp=clamp), sh(10, clamp, 0, 80, 0.3, 0.5), pulse(10, clamp, 0.9)], T(10, 1350, 400, 64, "老办法", c="ink", d=0.1),
   T(10, 1350, 560, 56, "头固定住", c="red", d=0.5))
# 10.5 大显微镜底下
s, si = scope(10.5, 960, 380, 2.0)
m, mi = mouse(10.5, 960, 800, 0.8, cap=False)
bd(10.5, s, m, arr(10.5, 960, 640, 960, 700, c="red", d=0.4), T(10.5, 1500, 500, 56, "大显微镜", c="ink", d=0.6))
# 11 一动不动躺着
pp, pi = person(11, 700, 560, 1.4)
bd(11, pp, [rot(11, pi, 90, (700, 560), 0.2, 0.6)], T(11, 1350, 400, 64, "一动不动", c="ink", d=0.4), [e for q in range(3) for e in T(11, 1150 + 60 * q, 600, 44, "z", c="blue", d=0.6 + 0.2 * q)])
# 11.5 自然地逛街
pp, pi = person(11.5, 700, 560, 1.4)
bd(11.5, pp, [rot(11.5, pi, 90, (700, 560), 0.0, 0.1)], stores_ := [R(11.5, 1150 + 220 * q, 400, 160, 200, c="blue", idp=uid("st")) for q in range(3)],
   [pop(11.5, e["id"], 0.2 + 0.15 * q) for q, e in enumerate(stores_)], [bob(11.5, e["id"], 4, 1.0 + 0.1 * q) for q, e in enumerate(stores_)],
   T(11.5, 1370, 760, 60, "“自然地”逛街？", c="red", d=0.6))
# 12 反转一：重量
bd(12, BIG(12, 960, 200, "反转一", c="red", d=0.1, s=100), [P(12, "M960,360 L960,760 M760,760 L1160,760 M700,420 L1220,420 M700,420 L640,580 L760,580 Z M1220,420 L1160,580 L1280,580 Z", c="ink", w=6, idp=(sc_ := uid("sc"))),
                                                         pop(12, sc_, 0.3), rot(12, sc_, 6, (960, 760), 0.6, 0.6)], T(12, 1500, 560, 64, "重量", c="ink", d=0.5))
# 12.5 二三十克
m, mi = mouse(12.5, 650, 620, 1.3, cap=False)
bd(12.5, m, BIG(12.5, 1350, 420, "20–30 克", c="blue", d=0.3, s=130), bar(12.5, 1300, 860, 120, 260, "blue", d=0.5))
# 13 超过3克
m, mi = mouse(13, 650, 640, 1.3, cap=False)
hv = uid("hv")
bd(13, m, [R(13, 560, 260, 180, 180, c="red", fill="red", idp=hv), sh(13, hv, 0, 100, 0.2, 0.5), {"t": "move", "at": 13, "kind": "grow", "targets": [mi], "axis": "y",
                                                                                                  "from": 1.0, "to": 0.85, "pivot": [650, 750], "dur": 0.5, "delay": 0.6}],
   BIG(13, 1350, 450, "3 克+", c="red", d=0.3, s=140))
# 13.5 十分之一
bd(13.5, bar(13.5, 500, 860, 180, 500, "blue", d=0.1), bar(13.5, 800, 860, 180, 50, "red", d=0.4), T(13.5, 590, 920, 48, "体重", c="blue"),
   T(13.5, 890, 920, 48, "显微镜", c="red"), BIG(13.5, 1400, 480, "1/10", c="red", d=0.6, s=150))
# 14 我们估算 60公斤
pp, pi = person(14, 650, 600, 1.5)
bd(14, pp, BIG(14, 1350, 380, "60 公斤", c="ink", d=0.3, s=120), T(14, 1350, 600, 56, "（估算）", c="muted", d=0.5), arr(14, 1100, 450, 820, 450, c="ink", d=0.6))
# 14.5 6公斤西瓜
pp, pi = person(14.5, 650, 640, 1.5)
bd(14.5, pp, melon(14.5, 650, 290, 0.9, d=0.2), [sh(14.5, pi, 0, 20, 0.5, 0.3), rot(14.5, pi, -5, (650, 860), 0.8, 0.4)], BIG(14.5, 1350, 450, "6 公斤", c="green", d=0.5, s=140))
# 15 现在1克
m, mi = mouse(15, 650, 620, 1.3)
bd(15, m, [sh(15, mi + "*", 0, -60, 0.4, 0.3), sh(15, mi + "*", 0, 60, 0.7, 0.3)], BIG(15, 1350, 450, "1 克", c="green", d=0.2, s=160), check(15, 1350, 700, d=0.8))
# 15.5 一大瓶水
pp, pi = person(15.5, 650, 640, 1.5)
bd(15.5, pp, bottle(15.5, 650, 330, 0.9, d=0.2), T(15.5, 1350, 450, 64, "一大瓶水", c="blue", d=0.4), check(15.5, 1350, 650, d=0.7))
# 16 反转二：线
bd(16, BIG(16, 960, 200, "反转二", c="red", d=0.1, s=100), wire(16, 400, 600, 1500, 600, d=0.3), T(16, 960, 860, 64, "线", c="ink", d=0.5))
# 16.5 拖着线
m, mi = mouse(16.5, 1300, 620, 1.1)
bd(16.5, m, wire(16.5, 300, 300, 1300, 420, d=0.1), [R(16.5, 200, 220, 200, 160, c="ink", fill="muted", idp=(bx := uid("bx"))), bob(16.5, bx, 4, 1.0)],
   T(16.5, 700, 860, 60, "拖着一根线", c="ink", d=0.5))
# 17 缠，绊
m, mi = mouse(17, 900, 620, 1.1)
bd(17, m, wire(17, 300, 300, 900, 450, d=0.1), wire(17, 900, 450, 1600, 800, d=0.3), [rot(17, mi + "*", 30, (900, 730), 0.6, 0.5)], T(17, 1450, 300, 64, "绊！", c="red", d=0.6))
# 17.5 一团毛线
E = []
for q in range(3):
    E += mouse(17.5, 400 + 560 * q, 820, 0.6)[0]
bd(17.5, E, yarn(17.5, 960, 380, d=0.3), T(17.5, 1500, 380, 60, "一团毛线", c="red", d=0.7))
# 18 无线
m, mi = mouse(18, 650, 640, 1.3)
bd(18, m, sound(18, 760, 340, 1.0, d=0.2), cross(18, 1150, 500, d=0.5), BIG(18, 1450, 450, "无线", c="green", d=0.4, s=140))
# 18.5 压缩再发出去
big_ = uid("img")
bd(18.5, [R(18.5, 300, 300, 400, 400, c="blue", fill="blue", idp=big_),
          {"t": "move", "at": 18.5, "kind": "grow", "targets": [big_], "axis": "both", "from": 1.0, "to": 0.4, "pivot": [500, 500], "dur": 0.8, "delay": 0.2}],
   packets(18.5, 600, 500, 1300, 500, n=4, d=0.8), [R(18.5, 1300, 380, 320, 240, c="ink", idp=(lp := uid("lap"))), bob(18.5, lp, 4, 1.0)],
   T(18.5, 500, 820, 56, "压缩", c="blue", d=0.3), T(18.5, 1460, 820, 56, "发出去", c="ink", d=0.9))
# 19 200万像素
E = []
for r in range(4):
    for q in range(6):
        px = uid("px")
        E += [R(19, 400 + 90 * q, 300 + 90 * r, 80, 80, c="blue", fill="blue" if (r + q) % 2 else None, idp=px), pop(19, px, 0.03 * (r * 6 + q))]
bd(19, E, BIG(19, 1350, 450, "200万", c="blue", d=0.5, s=140), T(19, 1350, 640, 56, "像素", c="ink", d=0.7), [pulse(19, E[0]["id"], 1.0)])
# 19.5 4片镜片
E = []
for q in range(4):
    ln = uid("ln")
    E += [P(19.5, f"M{500 + 180 * q},300 Q{570 + 180 * q},500 {500 + 180 * q},700 Q{430 + 180 * q},500 {500 + 180 * q},300", c="blue", w=6, fill="muted", idp=ln),
          pop(19.5, ln, 0.1 + 0.2 * q), bob(19.5, ln, 6, 1.0 + 0.15 * q)]
ray = uid("ray")
bd(19.5, E, [P(19.5, "M300,500 L1250,500", c="gold", w=5, idp=ray), pop(19.5, ray, 0.9), pulse(19.5, ray, 1.2)], BIG(19.5, 1500, 480, "4 片", c="red", d=0.6, s=140))
# 20 视野6毫米
cir = uid("cir")
bd(20, [O(20, 700, 500, 260, c="blue", idp=cir), pop(20, cir, 0.0), spin(20, cir, (700, 500), 20)], neurons(20, 560, 400, 3, 2, gap=130, k=0.45, d=0.3),
   BIG(20, 1400, 480, "6 毫米", c="blue", d=0.4, s=130))
# 20.5 单个细胞
lens = uid("mag")
bd(20.5, neurons(20.5, 400, 350, 5, 3, gap=160, k=0.45, d=0.0, step=0.02), [O(20.5, 700, 500, 120, c="red", idp=lens), sh(20.5, lens, 300, 0, 0.3, 1.0)],
   T(20.5, 1500, 500, 60, "一个一个细胞", c="red", d=0.5))
# 21 8500
bd(21, neurons(21, 260, 240, 10, 3, gap=150, k=0.5, d=0.0, step=0.01), BIG(21, 960, 860, "8500+", c="green", d=0.4, s=150), n=3)
# 21.5 25倍
bd(21.5, bar(21.5, 500, 860, 180, 24, "muted", d=0.1), bar(21.5, 900, 860, 180, 600, "green", d=0.3, dur=1.0), T(21.5, 590, 920, 48, "同类", c="muted"),
   T(21.5, 990, 920, 48, "Airscope", c="green"), BIG(21.5, 1450, 450, "×25", c="red", d=0.9, s=150))
# 22 反转三 最烧脑
bd(22, BIG(22, 960, 200, "反转三", c="red", d=0.1, s=100), neuron(22, 700, 560, 1.8, d=0.2, fire=(0.7, 1.2)), Q(22, 1150, 420, d=0.5))
# 22.5 看到更多为什么重要
bd(22.5, neurons(22.5, 300, 300, 6, 3, gap=170, k=0.5, d=0.0, step=0.02), Q(22.5, 1350, 360, d=0.5), T(22.5, 1460, 760, 56, "为什么重要？", c="red", d=0.6))
# 23 不是一个神经元
bd(23, neuron(23, 700, 500, 2.0, d=0.0, fire=(0.4,)), cross(23, 700, 500, d=0.6), T(23, 1350, 500, 60, "不是一个", c="ink", d=0.3))
# 23.5 一起合唱
E = []
for q in range(6):
    E += neuron(23.5, 360 + 240 * q, 560, 0.8, d=0.05 * q, c=["green", "gold", "blue"][q % 3], fire=(0.4 + 0.1 * q, 1.1 + 0.1 * q))
bd(23.5, E, notes(23.5, 600, 380, n=3, d=0.3), notes(23.5, 1200, 380, n=3, d=0.5, c="red"), T(23.5, 960, 860, 60, "成千上万个一起合唱", c="ink", d=0.4))
# 24 只听一个人唱
pp, pi = person(24, 650, 600, 1.3)
bd(24, pp, notes(24, 780, 350, n=2, d=0.2), T(24, 1350, 450, 64, "只听一个", c="ink", d=0.3), [wig(24, pi, (650, 760), 8, 2.0)])
# 24.5 听不出哪首歌
E = []
for q in range(5):
    E += person(24.5, 350 + 300 * q, 600, 0.9)[0]
bd(24.5, E, notes(24.5, 600, 280, n=4, d=0.2), Q(24.5, 1400, 120, s=160, d=0.6), T(24.5, 960, 900, 56, "合起来才是歌", c="blue", d=0.7))
# 25 5平方米小区
hab = uid("hab")
bd(25, [R(25, 360, 260, 1200, 600, c="green", idp=hab), pop(25, hab, 0.0), pulse(25, hab, 0.9)], BIG(25, 960, 420, "5 平方米", c="green", d=0.3, s=120),
   mouse(25, 700, 720, 0.6)[0], mouse(25, 1250, 720, 0.6)[0])
# 25.5 同时好几只
E = []
for q in range(4):
    mm, mmi = mouse(25.5, 360 + 400 * q, 560 + 100 * (q % 2), 0.7)
    E += mm + [sh(25.5, mmi + "*", 80 * (1 - 2 * (q % 2)), 0, 0.3 + 0.2 * q, 1.0)]
bd(25.5, E, T(25.5, 960, 200, 60, "同时记录好几只", c="ink", d=0.3))
# 26 32个出口迷宫
bd(26, maze(26, 700, 500, 560, d=0.0), BIG(26, 1450, 450, "32", c="red", d=0.3, s=160), T(26, 1450, 650, 56, "个末端", c="ink", d=0.5),
   [e for q in range(4) for e in check(26, 480 + 140 * q, 880, c="red", d=0.6 + 0.1 * q)][:8])
# 26.5 随便逛
m, mi = mouse(26.5, 520, 720, 0.45)
bd(26.5, maze(26.5, 800, 500, 600, d=0.0), m, [sh(26.5, mi + "*", 0, -380, 0.2, 0.8), sh(26.5, mi + "*", 300, 0, 1.0, 0.8)], T(26.5, 1500, 500, 60, "随便逛", c="green", d=0.4))
# 27 自由社交
m1, a1 = mouse(27, 650, 620, 1.0)
m2, a2 = mouse(27, 1250, 620, 1.0)
hrt = uid("hrt")
bd(27, m1, m2, [rot(27, a2 + "*", 0, (1250, 620), 0, 0.1), P(27, "M960,380 C860,300 860,200 960,240 C1060,200 1060,300 960,380 Z", c="red", w=6, fill="red", idp=hrt),
                pop(27, hrt, 0.4), pulse(27, hrt, 0.9)], T(27, 960, 900, 56, "自由社交、自由探索", c="ink", d=0.5))
# 27.5 大脑才说真话
bd(27.5, neurons(27.5, 450, 300, 5, 2, gap=200, k=0.7, d=0.0), BIG(27.5, 960, 760, "说真话", c="green", d=0.4, s=130), check(27.5, 1500, 760, d=0.8))
# 28 我们猜：动物怎么找路
m, mi = mouse(28, 600, 640, 1.1)
pth = uid("pth")
bd(28, m, [P(28, "M800,700 Q1000,400 1200,600 Q1400,800 1600,400", c="red", w=6, idp=pth), pop(28, pth, 0.3), pulse(28, pth, 0.9)], T(28, 1300, 250, 60, "我们猜", c="muted", d=0.1),
   T(28, 1300, 820, 56, "怎么找路", c="red", d=0.5))
# 28.5 帮机器人探索
rb = uid("rb")
ant = uid("ant")
bd(28.5, [R(28.5, 520, 380, 300, 300, c="blue", fill="muted", idp=rb), O(28.5, 610, 500, 25, c="ink", fill="ink", idp=rb), O(28.5, 730, 500, 25, c="ink", fill="ink", idp=rb),
          P(28.5, "M670,380 L670,290", c="blue", w=6, idp=ant), O(28.5, 670, 280, 18, c="red", fill="red", idp=ant), pop(28.5, rb, 0.0), bob(28.5, rb, 6, 1.2),
          wig(28.5, ant, (670, 380), 10, 2.0), sh(28.5, rb + "*", 300, 0, 0.6, 1.0)], Q(28.5, 1350, 300, s=160, d=0.4), T(28.5, 1350, 760, 56, "也许能帮机器人", c="blue", d=0.5))
# 29 友情提示：动物实验
m, mi = mouse(29, 650, 640, 1.2)
bd(29, m, BIG(29, 1350, 260, "友情提示", c="muted", d=0.1, s=90), T(29, 1350, 560, 64, "动物实验", c="ink", d=0.4))
# 29.5 不是读心术
br = uid("br")
bd(29.5, [P(29.5, "M500,600 Q480,320 760,330 Q960,250 1100,400 Q1260,500 1150,650 Q1000,720 800,690 Q600,720 500,600 Z", c="ink", w=6, idp=br), pop(29.5, br, 0.0),
          bob(29.5, br, 4, 0.9)], [P(29.5, "M520,520 Q800,420 1120,500", c="green", w=8, idp=(sf := uid("sf"))), pop(29.5, sf, 0.3), pulse(29.5, sf, 0.8)],
   T(29.5, 1500, 380, 52, "表层", c="green", d=0.4), cross(29.5, 1500, 620, d=0.8), T(29.5, 1500, 760, 52, "读心术", c="red", d=0.6))
# 30 离用在人身上
pp, pi = person(30, 1500, 600, 1.2)
m, mi = mouse(30, 400, 640, 0.9)
bd(30, pp, m, arr(30, 620, 600, 1300, 600, c="ink", d=0.3), T(30, 960, 400, 56, "用在人身上", c="ink", d=0.5))
# 30.5 还很远
rd = uid("rd")
bd(30.5, [P(30.5, "M300,800 Q960,500 1600,300", c="ink", w=8, idp=rd), pop(30.5, rd, 0.0), pulse(30.5, rd, 0.8)], mouse(30.5, 400, 700, 0.6)[0],
   BIG(30.5, 1250, 700, "还很远", c="red", d=0.4, s=130))
# 31 以后还想
s, si = scope(31, 700, 560, 1.3)
bd(31, s, arr(31, 900, 500, 1200, 500, c="ink", d=0.3), T(31, 1450, 500, 64, "以后", c="ink", d=0.4), [rot(31, si + "*", 8, (700, 670), 0.6, 0.5)])
# 31.5 免疫和肿瘤
E = []
for q in range(5):
    E += [e for e in neuron(31.5, 400 + 120 * q, 500 + 60 * (q % 2), 0.5, d=0.1 * q, c="blue", fire=(0.8,))]
bd(31.5, E, T(31.5, 600, 760, 60, "免疫", c="blue", d=0.3), BIG(31.5, 1350, 480, "肿瘤", c="red", d=0.5, s=120), Q(31.5, 1250, 640, s=140, d=0.8))
# 32 米米表示 帽子很轻
m, mi = mouse(32, 800, 640, 1.5)
bd(32, m, [sh(32, mi + "*", 0, -40, 0.4, 0.3), sh(32, mi + "*", 0, 40, 0.7, 0.3)], T(32, 1450, 450, 64, "帽子很轻", c="green", d=0.3), check(32, 1450, 650, d=0.7), n=3)
# 32.5 脑子一直在闪
m, mi = mouse(32.5, 700, 660, 1.4)
E = []
for q in range(6):
    sp = uid("spk")
    E += [O(32.5, 500 + 80 * q, 300 - 40 * (q % 2), 18, c="gold", fill="gold", idp=sp), pop(32.5, sp, 0.1 * q), pulse(32.5, sp, 0.5 + 0.1 * q)]
bd(32.5, m, E, T(32.5, 1400, 500, 60, "一直在闪", c="gold", d=0.4), T(32.5, 1400, 700, 52, "（米米很满意）", c="muted", d=0.8), n=3)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"Airscope": "Air scope", "8500": "八千五百", "10月19日": "十月十九日", "200万": "两百万", "60公斤": "六十公斤",
                                       "6公斤": "六公斤", "1克": "一克", "3克": "三克", "32个": "三十二个", "5平方米": "五平方米", "25倍": "二十五倍",
                                       "6毫米": "六毫米", "4片": "四片"})
