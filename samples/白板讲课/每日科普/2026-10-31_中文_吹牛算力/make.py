"""每日科普 2026-10-31（中文）：《芯片算力能吹到7倍？》
新闻：地平线创始人余凯 2026-10-30 晚在微博吐槽智驾芯片“PPT 算力”：英伟达按稠密算力 ×2 标称，业界已吹到 6–7 倍、叫“等效算力”；
他提议地平线以后两个数一起标：“NV 算力”（稠密 ×2）和“等效算力”（戏称“吹牛算力”）。
热榜：新浪科技热点小时报 2026-10-30 22 时第 8 条；微博相关话题（新浪新闻微博频道多条）。
出处：
- IT之家 https://www.ithome.com/1/020/358.htm ：Orin X 稠密 127 TOPS、标称 254 TOPS；6–7 倍；“吹牛算力”；“建议采纳”。
- 新浪科技 https://finance.sina.com.cn/tech/roll/2026-10-31/doc-inixakva1817339.shtml ：征程 6P NV 算力 560、等效算力 1960；
  真实效果还看架构、利用率、编译器、软件栈、模型适配、内存带宽。
- 新浪科技 https://finance.sina.com.cn/tech/roll/2026-10-30/doc-iniwziiq2246595.shtml
推算：280（=560÷2）与“正好七倍”（1960÷280）是按报道数字推算的。
常识：TOPS = 每秒万亿次运算；英伟达标称数含结构化稀疏（2:4，一半权重为零可跳过）——这是行业常识，报道未写明，片中说“一般认为”。
推测：等效算力怎么折算各家没公开统一公式；“更短的数字、更省事的架构”是常见说法，片中说成“大致思路”。比喻（搬砖工人、发动机马力、吹牛气球）是我们的。
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_chip, balloon_cow, car, car_drive, stick  # noqa: E402

S = [
 ("智驾芯片的算力，|有人能吹到真实的七倍。", "Self-driving chips: | some makers inflate compute to seven times the real number."),
 ("这话不是我说的，|是地平线创始人余凯昨晚在微博上说的。", "Not my words. | Horizon Robotics founder Yu Kai said it on Weibo last night."),
 ("他还给这种数字起了个名字：|吹牛算力。", "He even gave that number a name: | bragging compute."),
 ("今天的烧脑问题：|同一块芯片，算力怎么能有好几个数？", "Today's brain teaser: | how can one chip have several compute numbers?"),
 ("先说算力是啥。|单位叫TOPS，每秒一万亿次运算。", "First, what is compute? | The unit is TOPS: a trillion operations per second."),
 ("车上的AI看路，靠的是神经网络，|而神经网络几乎全是乘法和加法。", "Car AI sees the road with neural networks, | and those are almost all multiply and add."),
 ("想象芯片里有一大群搬砖工人，|每人每次搬一块砖。", "Picture a crowd of brick carriers inside the chip, | each carrying one brick at a time."),
 ("工人数乘以每秒搬几趟，|就是稠密算力，实打实的。", "Workers times trips per second | is dense compute. The honest number."),
 ("反转一：英伟达自己就先乘了二。|Orin X稠密算力一百二十七，标称二百五十四。", "Twist one: Nvidia already doubles it. | Orin X: 127 dense, 254 on the label."),
 ("为啥能乘二？|一般认为，是因为神经网络里很多数是零。", "Why double? | Generally, because many numbers in a neural network are zero."),
 ("零乘什么都是零，|这块砖不用搬，直接跳过。", "Zero times anything is zero, | so that brick can be skipped."),
 ("要是一半的数是零，|搬一半，就算搬了全部。", "If half the numbers are zero, | carrying half counts as carrying all."),
 ("这叫稀疏算力。|前提是，砖真的有一半是空的。", "That's sparse compute. | It only works if half the bricks really are empty."),
 ("反转二：有人乘了六七倍。|余凯说，这就叫等效算力。", "Twist two: some multiply by six or seven. | Yu calls that equivalent compute."),
 ("比如地平线自家的征程6P，|等效算力一千九百六十。", "Take Horizon's own Journey 6P: | 1960 equivalent TOPS."),
 ("按英伟达的算法，|它是五百六十。", "By Nvidia's method, | it is 560."),
 ("再除以二，稠密算力大约二百八十，|一千九百六十正好是它的七倍。", "Halve that: about 280 dense. | 1960 is exactly seven times that."),
 ("多出来的倍数从哪来？|各家没公开统一的算法。", "Where do the extra multiples come from? | There's no public, shared formula."),
 ("大致的思路是：|我的工人更聪明，一个顶好几个。", "Roughly, the idea is: | my workers are smarter, one does the job of several."),
 ("比如用更短的数字来算，|或者架构更省事，就说相当于多少倍。", "Say, computing with shorter numbers, | or a leaner design, then claiming it equals more."),
 ("就像一台发动机说：|我特别省油，所以等效一千马力。", "Like an engine saying: | I'm so fuel efficient, call me a thousand horsepower."),
 ("听着好像有点道理，|可马力表上不能这么写。", "Sounds almost reasonable, | but you can't print that on a spec sheet."),
 ("反转三，最反直觉：|就算是稠密算力，也常常用不满。", "Twist three, the most surprising: | even dense compute often goes unused."),
 ("工人再多，|砖送不过来，也只能干等。", "However many workers you have, | if bricks don't arrive, they just wait."),
 ("这个送砖的速度，|叫内存带宽。", "That brick delivery speed | is called memory bandwidth."),
 ("报道里说，真实效果还要看芯片利用率、|编译器和软件。", "Reports note real performance also depends on utilization, | compilers and software."),
 ("所以，纸面算力|不等于能用的算力。", "So, paper compute | is not usable compute."),
 ("余凯的办法很直接：|以后地平线两个数一起标。", "Yu's fix is simple: | Horizon will print both numbers."),
 ("一个叫NV算力，|就是稠密乘二。", "One is Nvidia-style compute: | dense times two."),
 ("另一个叫等效算力，|他自己管它叫吹牛算力。", "The other is equivalent compute, | which he himself calls bragging compute."),
 ("友情提示：等效算力怎么折算，|今天讲的是大致思路，不是官方公式。", "Fine print: how equivalent compute is calculated, | today is the rough idea, not an official formula."),
 ("芯片好不好，|最后还得看车开得好不好。", "Is a chip good? | In the end, ask how well the car drives."),
 ("同一块芯片，为啥有好几个算力？|因为数砖的方法不一样。", "Why does one chip have several numbers? | Because people count bricks differently."),
 ("下次看到几千TOPS，|先问一句：这是搬的砖，还是吹的牛？", "Next time you see thousands of TOPS, | ask: bricks carried, or bull blown?"),
]
TITLE = {"zh": "芯片算力能吹到7倍？", "en": "Can Chip Compute Be Inflated 7x?"}

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


def chip(a, x, y, k=1.0, d=0.0, mood="happy", label=None):
    i = uid("cp")
    return cute_chip(x, y, k, a, idp=i, mood=mood, label=label) + [pop(a, [i + "_b", i + "_p"], d)]


def cow(a, x, y, k=1.0, d=0.0, inflate=None):
    """吹牛气球；inflate = 放大倍数（蹦出后吹大）。"""
    i = uid("cw")
    E = balloon_cow(x, y, k, a, idp=i) + [pop(a, [i + "_b", i + "_s"], d)]
    if inflate:
        E.append({"t": "move", "at": a, "kind": "grow", "targets": [i + "_b"], "axis": "x", "pivot": [x, y], "dur": 1.0, "delay": d + 0.4,
                  "from": 1.0 / inflate, "to": 1.0})
    return E


def worker(a, x, y, k=1.0, d=0.0, brick=True, empty=False, walk=0, idle=False):
    """搬砖工人：小人举着一块砖（empty = 空心砖）。"""
    i, b = uid("wk"), uid("br")
    E = stick(x, y, k, a, idp=i, arms="up") + [pop(a, i, d)]
    if brick:
        E += [R(a, x - 50 * k, y - 330 * k, 100 * k, 50 * k, c="red", fill=None if empty else "red", idp=b, sw=5), pop(a, b, d + 0.1)]
    if walk:
        E.append(sh(a, [i, b], walk, 0, d + 0.3, 1.4))
    else:
        E.append(bob(a, i, 4 if idle else 10 * k, 0.6 if idle else 2.0))
        if brick:
            E.append(bob(a, b, 4 if idle else 10 * k, 0.6 if idle else 2.0))
    return E


def crew(a, x, y, n=4, gap=180, k=0.8, d=0.0, empty_every=0, walk=0):
    E = []
    for q in range(n):
        E += worker(a, x + gap * q, y, k, d + 0.08 * q, empty=bool(empty_every and q % empty_every == 1), walk=walk)
    return E


def bricks(a, x, y, n=6, d=0.0, zeros=False, fly=True):
    E = []
    for q in range(n):
        j = uid("bk")
        zero = zeros and q % 2 == 1
        bx, by = x + 110 * (q % 3), y - 60 * (q // 3)
        E += [R(a, bx, by, 100, 50, c="red", fill=None if zero else "red", idp=j, sw=5), pop(a, j, d + 0.06 * q)]
        if zero:
            E += T(a, bx + 50, by + 25, 34, "0", c="muted")
        if fly and not zero:
            E.append(sh(a, j, 0, -30, d + 0.5 + 0.1 * q, 0.4))
    return E


def counter(a, x, y, frm, to, d=0.0, c="red", s=150):
    """数字从 frm 蹦成 to：先出 frm，再被 to 顶掉。"""
    i, j = uid("cn"), uid("cn")
    E = [{**T(a, x, y, s, frm, c="ink")[0], "id": i}, pop(a, i, d), sh(a, i, 0, -1200, d + 0.9, 0.3)]
    E += [{**T(a, x, y, s, to, c=c)[0], "id": j}, pop(a, j, d + 1.0), pulse(a, j, d + 1.4)]
    return E


def drive(a, x, y, k=0.9, d=0.0, go=0, mood="happy"):
    i = uid("car")
    E = car(x, y, k, a, idp=i, mood=mood) + car_drive(x, y, k, a, idp=i) + [pop(a, [i + "_b", i + "_w0", i + "_w1"], d)]
    if go:
        E.append(sh(a, [i + "_b", i + "_w0", i + "_w1"], go, 0, d + 0.3, 1.6))
    return E


def phone(a, x, y, d=0.0):
    i = uid("ph")
    return [{"t": "icon", "at": a, "id": i, "name": "phone", "x": x, "y": y, "size": 220, "c": "ink"}, pop(a, i, d), wig(a, i, (x, y + 110), 6, 2.0)]


def net(a, x, y, d=0.0):
    """小神经网络：三层点，信号沿线跑。"""
    E = []
    cols = [[y - 120, y, y + 120], [y - 180, y - 60, y + 60, y + 180], [y - 60, y + 60]]
    ids = []
    for ci, col in enumerate(cols):
        for yy in col:
            j = uid("nn")
            ids.append(j)
            E += [O(a, x + 200 * ci, yy, 26, c="blue", fill="paper", idp=j), pop(a, j, d + 0.05 * len(ids))]
    ln = uid("nl")
    path = " ".join(f"M{x + 200 * ci + 26},{y0} L{x + 200 * (ci + 1) - 26},{y1}" for ci in range(2) for y0 in cols[ci] for y1 in cols[ci + 1])
    E = [P(a, path, c="muted", w=2, idp=ln), pop(a, ln, d)] + E
    E += [pulse(a, ids[q], d + 0.5 + 0.12 * q) for q in range(len(ids))]
    return E


def gauge(a, x, y, d=0.0, to=60):
    """利用率表盘：指针转到 to 度。"""
    i, n = uid("gg"), uid("gn")
    return [P(a, f"M{x - 160},{y} A160,160 0 0,1 {x + 160},{y}", c="ink", w=8, idp=i), pop(a, i, d),
            P(a, f"M{x},{y} L{x - 130},{y}", c="red", w=8, idp=n), pop(a, n, d + 0.1), rot(a, n, to, (x, y), d + 0.4, 1.0),
            O(a, x, y, 14, c="ink", fill="ink")]


def pipe(a, x0, x1, y, d=0.0):
    """窄管子：砖一块块慢慢送过去。"""
    i = uid("pp")
    E = [R(a, x0, y - 30, x1 - x0, 60, c="ink", idp=i, sw=5), pop(a, i, d)]
    for q in range(3):
        j = uid("pb")
        E += [R(a, x0 + 10, y - 18, 60, 36, c="red", fill="red", idp=j, sw=3), pop(a, j, d + 0.2 + 0.4 * q), sh(a, j, x1 - x0 - 80, 0, d + 0.3 + 0.4 * q, 1.8)]
    return E


def label(a, x, y, w, h, top, mid, d=0.0, c="blue"):
    i = uid("lb")
    return [R(a, x - w / 2, y - h / 2, w, h, c=c, idp=i, sw=6), pop(a, i, d), wig(a, i, (x, y + h / 2), 2, 1.0)] + T(a, x, y - h / 4, 46, top, c="ink", d=d + 0.1) + \
        BIG(a, x, y + h / 6, mid, c=c, d=d + 0.2, s=90)


# ---------- 画板 ----------
bd(0, chip(0, 550, 480, 1.3, 0.0), cow(0, 1350, 420, 1.4, 0.2, inflate=3), BIG(0, 1350, 800, "×7 ?", c="red", d=0.6, s=130))
bd(0.5, chip(0.5, 500, 480, 1.0, 0.0, mood="o"), counter(0.5, 1300, 500, "280", "1960", d=0.2), arr(0.5, 750, 480, 1050, 480, c="red", d=0.3))
bd(1, ic(1, "question", 500, 450, 200, 0.0, mv="wig", c="red"), cross(1, 500, 750, d=0.3), phone(1, 1300, 450, 0.2), T(1, 1300, 760, 56, "余凯 · 微博", c="blue", d=0.5))
bd(1.5, phone(1.5, 550, 420, 0.0), T(1.5, 1300, 380, 64, "地平线创始人", c="ink", d=0.2), BIG(1.5, 1300, 540, "余凯", c="blue", d=0.3, s=120), chip(1.5, 1600, 760, 0.5, 0.5))
bd(2, chip(2, 550, 500, 1.0, 0.0), arr(2, 780, 500, 1000, 500, c="red", d=0.3), cow(2, 1350, 450, 1.0, 0.4, inflate=2))
bd(2.5, cow(2.5, 600, 450, 1.3, 0.0, inflate=2.5), BIG(2.5, 1350, 420, "吹牛算力", c="red", d=0.3, s=130), star(2.5, 1350, 650, 0.6, r=50))
bd(3, BIG(3, 1150, 360, "烧脑问题", c="red", d=0.0, s=130), ic(3, "question", 450, 450, 260, 0.2, mv="wig", c="red"), ic(3, "gear", 1150, 620, 140, 0.4, mv="spin"),
   ic(3, "flame", 1650, 620, 140, 0.5, mv="wig", c="red"))
bd(3.5, chip(3.5, 500, 500, 1.1, 0.0, mood="o"), BIG(3.5, 1150, 350, "127", c="ink", d=0.2, s=110), BIG(3.5, 1500, 500, "254", c="blue", d=0.4, s=110), BIG(3.5, 1200, 700, "1960?", c="red", d=0.6, s=110))
bd(4, chip(4, 600, 480, 1.1, 0.0), ic(4, "question", 1300, 450, 200, 0.2, mv="wig", c="red"), T(4, 1300, 720, 60, "算力是啥？", c="ink", d=0.4))
bd(4.5, BIG(4.5, 960, 300, "TOPS", c="blue", d=0.0, s=140), T(4.5, 960, 480, 64, "每秒 1,000,000,000,000 次", c="red", d=0.3), ic(4.5, "clock", 500, 650, 150, 0.4, mv="spin"),
   ic(4.5, "gear", 1420, 650, 150, 0.5, mv="spin"))
bd(5, drive(5, 500, 760, 1.0, 0.0, go=300), ic(5, "eye", 1300, 400, 160, 0.2, mv="wig"), net(5, 1150, 600, 0.4))
bd(5.5, net(5.5, 400, 500, 0.0), BIG(5.5, 1350, 380, "× +", c="red", d=0.3, s=160), T(5.5, 1350, 600, 56, "乘法和加法", c="ink", d=0.5))
bd(6, chip(6, 400, 450, 0.8, 0.0), crew(6, 900, 820, 4, 230, 0.9, 0.2))
bd(6.5, worker(6.5, 600, 820, 1.4, 0.0), BIG(6.5, 1300, 400, "1 次 1 块", c="red", d=0.3, s=110), bricks(6.5, 1150, 700, 6, 0.4))
bd(7, crew(7, 300, 820, 4, 170, 0.8, 0.0), BIG(7, 1350, 400, "人数 × 趟数", c="blue", d=0.3, s=90), ic(7, "clock", 1350, 650, 150, 0.5, mv="spin"))
bd(7.5, label(7.5, 700, 480, 500, 300, "稠密算力", "实打实", d=0.0, c="green"), check(7.5, 1300, 450, d=0.4), crew(7.5, 1150, 840, 3, 180, 0.6, 0.3))
bd(8, BIG(8, 960, 360, "反转一", c="red", d=0.0, s=150), ic(8, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), chip(8, 1500, 560, 0.7, 0.4))
bd(8.5, chip(8.5, 450, 500, 1.0, 0.0, label="Orin X"), counter(8.5, 1200, 450, "127", "254", d=0.2, c="blue"), BIG(8.5, 1650, 450, "×2", c="red", d=1.3, s=120),
   T(8.5, 1200, 700, 50, "稠密 → 标称", c="ink", d=0.5))
bd(9, ic(9, "question", 600, 480, 240, 0.0, mv="wig", c="red"), BIG(9, 1300, 450, "×2 ?", c="red", d=0.2, s=150), chip(9, 1300, 760, 0.5, 0.4))
bd(9.5, net(9.5, 300, 500, 0.0), bricks(9.5, 1050, 600, 6, 0.3, zeros=True), T(9.5, 1250, 330, 60, "很多数是 0", c="red", d=0.5))
bd(10, BIG(10, 700, 450, "0 × 任何 = 0", c="ink", d=0.0, s=100), ic(10, "check", 1450, 450, 150, 0.4, mv="bob", c="green"), bricks(10, 600, 750, 3, 0.3, zeros=True))
sk = uid("sk")
bd(10.5, worker(10.5, 500, 820, 1.2, 0.0), [R(10.5, 1100, 560, 140, 70, c="red", idp=sk, sw=5), pop(10.5, sk, 0.2), sh(10.5, sk, 400, -200, 0.6, 0.8), rot(10.5, sk, 180, (1170, 595), 0.6, 0.8)],
   BIG(10.5, 1250, 300, "跳过！", c="green", d=0.4, s=110))
bd(11, bricks(11, 400, 700, 6, 0.0, zeros=True), BIG(11, 1300, 400, "一半是 0", c="red", d=0.3, s=110), crew(11, 1150, 850, 2, 200, 0.6, 0.5))
bd(11.5, crew(11.5, 300, 820, 2, 200, 0.9, 0.0, walk=200), arr(11.5, 900, 500, 1200, 500, c="red", d=0.4), BIG(11.5, 1500, 450, "= 全部", c="blue", d=0.5, s=120))
bd(12, label(12, 700, 480, 500, 300, "稀疏算力", "×2", d=0.0, c="blue"), bricks(12, 1200, 700, 6, 0.3, zeros=True))
bd(12.5, bricks(12.5, 400, 650, 6, 0.0, zeros=False), cross(12.5, 560, 500, d=0.4), T(12.5, 1300, 400, 60, "前提：", c="ink", d=0.2), T(12.5, 1300, 520, 60, "砖真的一半是空的", c="red", d=0.4))
bd(13, BIG(13, 960, 360, "反转二", c="red", d=0.0, s=150), cow(13, 450, 480, 0.8, 0.2, inflate=2), ic(13, "flame", 1500, 480, 150, 0.4, mv="wig", c="red"))
bd(13.5, cow(13.5, 550, 450, 1.3, 0.0, inflate=3.5), BIG(13.5, 1300, 380, "×6～7", c="red", d=0.3, s=140), T(13.5, 1300, 580, 64, "等效算力", c="blue", d=0.5))
bd(14, chip(14, 500, 500, 1.1, 0.0, label="J6P"), T(14, 1300, 360, 60, "征程6P", c="ink", d=0.2), BIG(14, 1300, 520, "1960", c="red", d=0.4, s=150), T(14, 1300, 680, 48, "等效算力", c="muted", d=0.5))
bd(14.5, chip(14.5, 500, 500, 1.1, 0.0, label="J6P"), counter(14.5, 1300, 480, "1960", "560", d=0.2, c="blue"), T(14.5, 1300, 680, 48, "NV 算力", c="muted", d=1.2))
bd(15, ic(15, "ruler", 500, 450, 200, 0.0, mv="wig"), T(15, 1250, 380, 60, "按英伟达的算法", c="ink", d=0.2), chip(15, 1250, 650, 0.6, 0.4))
bd(15.5, BIG(15.5, 960, 420, "560", c="blue", d=0.0, s=180), bar(15.5, 500, 850, 120, 280, "blue", 0.3), bar(15.5, 1300, 850, 120, 280, "blue", 0.4))
bd(16, BIG(16, 700, 400, "560 ÷ 2", c="ink", d=0.0, s=110), BIG(16, 1350, 400, "≈ 280", c="green", d=0.4, s=120), crew(16, 600, 840, 4, 200, 0.6, 0.5))
bd(16.5, bar(16.5, 450, 880, 160, 90, "green", 0.0), bar(16.5, 800, 880, 160, 630, "red", 0.3, 1.2), T(16.5, 530, 750, 50, "280", c="green", d=0.2),
   T(16.5, 880, 200, 50, "1960", c="red", d=1.2), BIG(16.5, 1450, 450, "×7", c="red", d=0.8, s=170))
bd(17, cow(17, 600, 450, 1.1, 0.0, inflate=2), ic(17, "question", 1300, 450, 220, 0.2, mv="wig", c="red"), T(17, 1300, 720, 56, "多的从哪来？", c="ink", d=0.4))
bd(17.5, ic(17.5, "magnifier", 500, 480, 220, 0.0, mv="wig"), cross(17.5, 1200, 450, d=0.3), T(17.5, 1200, 650, 60, "没有公开统一的公式", c="red", d=0.4))
bd(18, worker(18, 500, 820, 1.2, 0.0), ic(18, "gear", 500, 300, 120, 0.2, mv="spin"), T(18, 1300, 400, 60, "大致思路", c="muted", d=0.2), T(18, 1300, 520, 60, "我的工人更聪明", c="blue", d=0.4))
bd(18.5, worker(18.5, 500, 820, 1.0, 0.0), BIG(18.5, 850, 450, "=", c="ink", d=0.3, s=120), crew(18.5, 1100, 820, 4, 170, 0.7, 0.5))
bd(19, BIG(19, 600, 400, "3.14159", c="ink", d=0.0, s=110), arr(19, 900, 400, 1150, 400, c="red", d=0.3), BIG(19, 1400, 400, "3.1", c="red", d=0.5, s=110),
   ic(19, "ruler", 960, 680, 150, 0.4, mv="wig"))
bd(19.5, chip(19.5, 500, 500, 1.0, 0.0), arr(19.5, 750, 500, 1000, 500, c="red", d=0.3), cow(19.5, 1350, 450, 1.0, 0.4, inflate=2), T(19.5, 960, 830, 50, "（大致思路，非官方）", c="muted", d=0.6))
bd(20, ic(20, "engine", 550, 480, 260, 0.0, mv="wig"), T(20, 1300, 400, 60, "我特别省油……", c="blue", d=0.3), ic(20, "flame", 1300, 620, 120, 0.4, mv="wig", c="red"))
bd(20.5, ic(20.5, "engine", 500, 480, 220, 0.0, mv="wig"), BIG(20.5, 1300, 420, "等效 1000 马力", c="red", d=0.3, s=90), cow(20.5, 1300, 700, 0.6, 0.5, inflate=2))
bd(21, ic(21, "engine", 600, 480, 220, 0.0, mv="wig"), ic(21, "question", 1300, 450, 180, 0.2, mv="wig", c="red"), T(21, 1300, 700, 56, "有点道理？", c="ink", d=0.4))
bd(21.5, label(21.5, 700, 480, 520, 300, "马力表", "1000?", d=0.0, c="ink"), cross(21.5, 700, 520, d=0.4), cross(21.5, 1350, 450, d=0.5), T(21.5, 1350, 650, 56, "不能这么写", c="red", d=0.6))
bd(22, BIG(22, 960, 360, "反转三", c="red", d=0.0, s=150), gauge(22, 500, 650, 0.2, 60), ic(22, "flame", 1500, 520, 150, 0.4, mv="wig", c="red"))
bd(22.5, gauge(22.5, 600, 600, 0.0, 70), BIG(22.5, 1350, 400, "用不满", c="red", d=0.4, s=130), chip(22.5, 1350, 700, 0.5, 0.5, mood="sad"))
bd(23, crew(23, 300, 820, 5, 200, 0.8, 0.0), ic(23, "question", 1500, 400, 150, 0.4, mv="wig", c="red"))
bd(23.5, worker(23.5, 400, 820, 0.9, 0.0, brick=False, idle=True), worker(23.5, 650, 820, 0.9, 0.1, brick=False, idle=True), pipe(23.5, 900, 1700, 500, 0.2),
   T(23.5, 1300, 700, 56, "砖送不过来，干等", c="red", d=0.5))
bd(24, pipe(24, 300, 1300, 500, 0.0), ic(24, "clock", 1550, 500, 160, 0.3, mv="spin"))
bd(24.5, BIG(24.5, 960, 350, "内存带宽", c="blue", d=0.0, s=130), pipe(24.5, 400, 1500, 650, 0.2))
bd(25, gauge(25, 450, 600, 0.0, 90), ic(25, "computer", 960, 500, 170, 0.2, mv="bob"), ic(25, "gear", 1450, 500, 170, 0.3, mv="spin"), T(25, 960, 280, 56, "利用率", c="blue", d=0.4))
bd(25.5, ic(25.5, "computer", 500, 480, 220, 0.0, mv="bob"), T(25.5, 1300, 400, 60, "编译器", c="blue", d=0.2), T(25.5, 1300, 520, 60, "软件", c="green", d=0.4), ic(25.5, "gear", 1600, 700, 120, 0.4, mv="spin"))
bd(26, label(26, 600, 480, 460, 280, "纸面算力", "1960", d=0.0, c="red"), cow(26, 1350, 450, 0.9, 0.3, inflate=2))
bd(26.5, BIG(26.5, 960, 300, "≠", c="red", d=0.0, s=200), T(26.5, 500, 600, 60, "纸面算力", c="red", d=0.2), T(26.5, 1400, 600, 60, "能用的算力", c="green", d=0.3),
   crew(26.5, 1250, 860, 2, 200, 0.5, 0.5))
bd(27, phone(27, 550, 450, 0.0), T(27, 1300, 400, 60, "余凯的办法：", c="ink", d=0.2), check(27, 1300, 600, d=0.4))
bd(27.5, label(27.5, 600, 480, 460, 280, "NV 算力", "560", d=0.0, c="blue"), label(27.5, 1300, 480, 460, 280, "等效算力", "1960", d=0.3, c="red"), chip(27.5, 960, 800, 0.4, 0.5))
bd(28, label(28, 600, 480, 500, 300, "NV 算力", "稠密 ×2", d=0.0, c="blue"), chip(28, 1350, 500, 0.9, 0.3, label="J6P"))
bd(28.5, bar(28.5, 500, 850, 150, 200, "green", 0.0), bar(28.5, 800, 850, 150, 400, "blue", 0.4), BIG(28.5, 1400, 450, "×2", c="blue", d=0.6, s=150))
bd(29, label(29, 600, 480, 500, 300, "等效算力", "×7", d=0.0, c="red"), cow(29, 1350, 450, 1.0, 0.3, inflate=3))
bd(29.5, cow(29.5, 600, 450, 1.4, 0.0, inflate=3), BIG(29.5, 1350, 420, "= 吹牛算力", c="red", d=0.3, s=110), star(29.5, 1350, 650, 0.6, r=50))
bd(30, BIG(30, 960, 360, "友情提示", c="blue", d=0.0, s=130), ic(30, "ruler", 500, 620, 150, 0.2, mv="wig"), cow(30, 1450, 620, 0.6, 0.4))
bd(30.5, T(30.5, 960, 380, 64, "今天讲的是大致思路", c="ink", d=0.0), cross(30.5, 600, 600, d=0.3), T(30.5, 1100, 600, 60, "不是官方公式", c="red", d=0.4), ic(30.5, "magnifier", 1600, 650, 120, 0.4, mv="wig"))
bd(31, chip(31, 600, 480, 1.1, 0.0), ic(31, "question", 1300, 450, 200, 0.2, mv="wig", c="red"), T(31, 1300, 720, 56, "好不好？", c="ink", d=0.4))
bd(31.5, drive(31.5, 400, 760, 1.2, 0.0, go=700), check(31.5, 1500, 400, d=0.6), T(31.5, 960, 300, 60, "看车开得好不好", c="green", d=0.4))
bd(32, chip(32, 500, 480, 1.0, 0.0), BIG(32, 1150, 350, "127", c="ink", d=0.2, s=90), BIG(32, 1450, 500, "254", c="blue", d=0.3, s=90), BIG(32, 1200, 700, "1960", c="red", d=0.4, s=90))
bd(32.5, crew(32.5, 300, 820, 3, 200, 0.8, 0.0, empty_every=2), bricks(32.5, 1150, 650, 6, 0.3, zeros=True), T(32.5, 1300, 330, 60, "数砖的方法不一样", c="blue", d=0.5))
bd(33, BIG(33, 960, 380, "几千 TOPS ?", c="red", d=0.0, s=130), chip(33, 450, 650, 0.6, 0.3, mood="o"), cow(33, 1500, 600, 0.7, 0.4, inflate=2))
bd(33.5, worker(33.5, 450, 820, 1.1, 0.0), T(33.5, 960, 500, 80, "还是", c="ink", d=0.3), cow(33.5, 1450, 420, 1.2, 0.4, inflate=3), BIG(33.5, 960, 260, "搬砖？吹牛？", c="red", d=0.6, s=100))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"TOPS": "托普斯", "Orin X": "奥林 X", "NV": "N V", "AI": "A I", "征程6P": "征程六P"})
