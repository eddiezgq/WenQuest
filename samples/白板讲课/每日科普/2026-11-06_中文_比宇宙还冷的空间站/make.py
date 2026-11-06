"""每日科普 2026-11-06（中文）：《空间站里，比宇宙还冷？》
热点：中国空间站“梦天”超冷原子实验把铷原子云降到 9.7 皮开尔文，造出人类已知最冷的人造物质，论文 2026-11-06 在线发表于《科学》
  （新浪科学热点小时报 2026-11-06 18 时第 9 条；新浪科技、科学网、凤凰网、网易、央视新闻等同日报道）。
事实（科学网 2026-11-06；新浪科技 2026-11-06）：
- 铷原子云等效温度 9.7 pK，比室温低约 14 个数量级；可持续观测 7 秒。
- 2022 年国际空间站冷原子实验室做到 52 pK。
- 地面上重力把原子从束缚“容器”底部拉走，限制了蒸发冷却时容器高度继续降低；微重力下可以降得很低。
- 先用磁光阱、光学黏团（激光冷却）初步冷却；中国方案：全光阱、降低光强蒸发冷却，再用“非绝热扩散”深度冷却，两级交叉光阱。
- 地面系统约 20 立方米、10 吨，集成为约 0.7 立方米、0.5 吨的实验柜；2011 年开始论证，约 15 年；起始材料 5 克金属铷；2022 年随梦天舱上天。
- 用途：更高精度的原子干涉仪、量子传感器、空间时频基准（重力场测量、惯性导航）；极低温量子气体、早期宇宙模拟、超轻暗物质探测。
- 中国科学院空间应用工程与技术中心牵头，北京大学、上海光机所联合完成；DOI 10.1126/science.aea5324。
我们的估算（片中说明是估算）：宇宙背景约 2.7 K，2.7 K / 9.7 pK ≈ 2800 亿倍；铷原子 9.7 pK 时方均根速度 √(3kT/m) ≈ 0.05 毫米/秒，
  蜗牛约 1 毫米/秒；室温约每秒 300 米。
比喻（我们的）：吹热汤、碗边放低、斜坡上的碗、开汽水、扔乒乓球（激光“刹车”）。
出处：
- https://news.sciencenet.cn/htmlnews/2026/11/574304.shtm
- https://finance.sina.com.cn/tech/digi/2026-11-06/doc-inixtxky8306526.shtml
- https://k.sina.com.cn/article_7857201856_1d45362c001908tvg2.html
- https://news.ifeng.com/c/8xovbzIRb3I
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_atom, stick  # noqa: E402

S = [
 ("中国空间站里，|造出了人类已知最冷的人造物质。", "Inside China's space station, | scientists made the coldest man-made stuff we know of."),
 ("九点七皮开尔文，|离绝对零度只差一丁点。", "Nine point seven picokelvin. | A hair above absolute zero."),
 ("比宇宙深空还冷，|我们算了一下，冷了大约两千八百亿倍。", "Colder than deep space, | about two hundred eighty billion times colder, by our math."),
 ("十一月六日，论文登上《科学》，|一下子刷屏了。", "On November sixth the paper came out in Science, | and it was everywhere."),
 ("今天的烧脑问题：|为啥非得跑到太空，才能这么冷？", "Today's brain teaser: | why go all the way to space to get this cold?"),
 ("认识主角：一颗铷原子，|小铷。", "Meet our hero: a rubidium atom, | Little Rubi."),
 ("温度到底是啥？|就是原子乱跑的快慢。", "What is temperature, really? | It's how fast atoms jitter around."),
 ("室温下，小铷每秒跑好几百米，|跟飞机差不多快。", "At room temperature, Rubi zooms hundreds of meters a second, | about as fast as a jet."),
 ("降到九点七皮开尔文，|它每秒只挪大约零点零五毫米。", "At nine point seven picokelvin, | it creeps about five hundredths of a millimeter a second."),
 ("比蜗牛还慢二十来倍，|这是我们按公式估算的。", "Twenty times slower than a snail, | by our own estimate."),
 ("怎么让原子慢下来？|第一步，用激光“刹车”。", "How do you slow atoms down? | Step one: laser brakes."),
 ("好几束激光从四面八方照过来，|像迎面扔来的乒乓球，越跑越慢。", "Lasers shine in from every side, | like ping pong balls hitting you head on."),
 ("第二步，蒸发冷却，|跟你吹热汤一个道理。", "Step two: evaporative cooling, | the same trick as blowing on hot soup."),
 ("汤里最“热”的分子先飞走，|剩下的就凉了。", "The hottest molecules fly off first, | and what's left cools down."),
 ("原子关在光做的“碗”里，|碗边一点点放低，跑得快的就溜了。", "The atoms sit in a bowl made of light. | Lower the rim, and the fast ones escape."),
 ("反转一：碗边越低，剩下的越冷。|可在地面上，碗边放不低。", "Twist one: the lower the rim, the colder the rest. | But on Earth, you can't lower it far."),
 ("因为重力把原子往下拽，|碗一放低，它们从底下漏光了。", "Gravity drags the atoms down. | Lower the bowl, and they spill out the bottom."),
 ("就像斜坡上放一碗汤，|碗边一低，汤先从下面洒了。", "Like a bowl of soup on a slope: | lower the rim, and it spills downhill."),
 ("在空间站里，大家一起自由下落，|原子感觉不到“往下”。", "On the space station, everything falls together, | so the atoms feel no 'down'."),
 ("碗边可以放得很低很低，|原子还乖乖待着。", "The rim can go really, really low, | and the atoms still stay put."),
 ("反转二：还有更狠的一招，|叫“非绝热扩散”。", "Twist two: there's an even sneakier move, | called non-adiabatic expansion."),
 ("简单说，让原子云在更大的碗里散开，|又降了一截温度。", "Basically, let the cloud spread out into a bigger bowl, | and it cools down another notch."),
 ("就像打开一罐汽水，|气一冲出来，罐口凉飕飕。", "Like opening a can of soda: | the gas rushes out, and the can top feels cold."),
 ("二零二二年，国际空间站做到五十二皮开尔文；|这次降到了九点七。", "In twenty twenty two, the International Space Station hit fifty two picokelvin. | This one hit nine point seven."),
 ("低了五倍多，|而且能盯着看七秒钟。", "More than five times lower, | and they could watch it for seven seconds."),
 ("反转三，最难：|这台“冰箱”在地面上有二十立方米、十吨重。", "Twist three, the hardest part: | on the ground this freezer filled twenty cubic meters and weighed ten tons."),
 ("科学家把它塞进零点七立方米、|半吨重的实验柜。", "They squeezed it into a cabinet of point seven cubic meters, | weighing half a ton."),
 ("从二零一一年论证开始，|做了大约十五年。", "From the first plans in twenty eleven, | it took about fifteen years."),
 ("里面只用了五克铷，|比一枚一元硬币还轻。", "It started with just five grams of rubidium, | lighter than a coin."),
 ("这么冷有啥用？|原子越慢，越能当精确的尺子。", "Why so cold? | The slower the atoms, the better they work as rulers."),
 ("能做更准的原子干涉仪和量子传感器，|测地球重力、帮飞船导航。", "Better atom interferometers and quantum sensors, | to map Earth's gravity and help navigation."),
 ("还能研究暗物质，|模拟宇宙刚诞生时的样子。", "They may even help hunt dark matter | and mimic the early universe."),
 ("友情提示：最冷的是这团原子云，|空间站里一点也不冷。", "Fine print: only this tiny atom cloud is that cold. | The station itself is comfy."),
 ("两千八百亿倍、比蜗牛慢，|都是我们自己估算的，算个大概。", "The two hundred eighty billion and the snail | are our own rough estimates."),
 ("所以，为啥非得去太空？|因为在太空，碗边能放很低，原子也不会漏。", "So why space? | Up there, the rim can go low without the atoms spilling out."),
 ("地球上最冷的东西，|原来在天上。", "The coldest thing on Earth | is actually up in the sky."),
]
TITLE = {"zh": "空间站里，比宇宙还冷？", "en": "Colder Than Space, In Space?"}

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
    return T(a, x, y, s * 1.5, text, c=c, d=d)


def big(a, x, y, text, c="red", d=0.0, s=140):
    return BIG(a, x, y, text, c=c, d=d, s=s)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def man(a, x, y, k=1.4, d=0.0, arms="down"):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": 3, "hz": 1.6}]


def rubi(a, x, y, k=1.0, d=0.0, mood="happy", cold=True):
    i = uid("rb")
    return cute_atom(x, y, k, a, idp=i, mood=mood, cold=cold) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]


def cloud(a, cx, cy, n=9, spread=90, d=0.0, c="blue", amp=6, hz=2.0, r=14, ids=None):
    """A little atom cloud: n dots that jitter (hot = big amp/hz)."""
    E = []
    for q in range(n):
        i = uid("dt")
        x = cx + spread * ((q * 53) % 11 - 5) / 5
        y = cy + spread * 0.6 * ((q * 37) % 7 - 3) / 3
        E += [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d + 0.03 * q), wig(a, i, (x - 3, y), amp, hz + 0.3 * (q % 3))]
        if ids is not None:
            ids.append(i)
    return E


def bowl(a, cx, cy, w=500, h=260, d=0.0, c="red", idp=None):
    i = idp or uid("bw")
    return [P(a, f"M{cx - w / 2},{cy - h} Q{cx - w / 2},{cy + h * 0.4} {cx},{cy + h * 0.25} Q{cx + w / 2},{cy + h * 0.4} {cx + w / 2},{cy - h}",
              c=c, w=8, idp=i), pop(a, i, d), wig(a, i, (cx, cy), 1.5, 1.0)]


def laser(a, x0, y0, x1, y1, d=0.0):
    i = uid("lz")
    return [P(a, f"M{x0},{y0} L{x1},{y1}", c="red", w=6, idp=i), pop(a, i, d), wig(a, i, (x0, y0), 1.5, 4)]


def station(a, x, y, s=220, d=0.0):
    return ic(a, "satellite", x, y, s, d, mv="bob", c="blue")


def escape(a, x, y, dx, dy, d=0.0, c="red"):
    """One fast atom zipping out."""
    i = uid("es")
    return [O(a, x, y, 16, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, 1.0)]


def snail(a, x, y, k=1.0, d=0.0):
    i = uid("sn")
    E = [O(a, x, y - 60 * k, 60 * k, c="ink", fill="gold", idp=i),
         P(a, f"M{x - 30 * k},{y - 60 * k} Q{x},{y - 100 * k} {x + 20 * k},{y - 60 * k} Q{x + 10 * k},{y - 40 * k} {x - 5 * k},{y - 55 * k}", c="ink", w=4, idp=i),
         P(a, f"M{x - 110 * k},{y} L{x + 90 * k},{y} Q{x + 120 * k},{y} {x + 110 * k},{y - 50 * k} M{x + 100 * k},{y - 40 * k} L{x + 110 * k},{y - 90 * k} "
              f"M{x + 115 * k},{y - 40 * k} L{x + 140 * k},{y - 85 * k}", c="ink", w=5, idp=i)]
    return E + [pop(a, i, d), sh(a, i, 60 * k, 0, d + 0.3, 2.5)]


def soup(a, x, y, d=0.0):
    i = uid("sp")
    E = [P(a, f"M{x - 160},{y - 60} Q{x - 150},{y + 90} {x},{y + 90} Q{x + 150},{y + 90} {x + 160},{y - 60} Z", c="ink", w=6, idp=i), pop(a, i, d)]
    for q in range(3):
        j = uid("sm")
        E += [P(a, f"M{x - 60 + 60 * q},{y - 90} Q{x - 35 + 60 * q},{y - 130} {x - 60 + 60 * q},{y - 170}", c="muted", w=5, idp=j), pop(a, j, d + 0.1 * q),
              wig(a, j, (x - 60 + 60 * q, y - 90), 10, 2.5)]
    return E


def can(a, x, y, d=0.0):
    i = uid("cn")
    return [R(a, x - 70, y - 120, 140, 240, c="ink", fill="red", idp=i), pop(a, i, d), wig(a, i, (x, y + 120), 3, 2)] + bubbles(a, x, y - 140, 5, d + 0.2, 300, "muted")


def fall(a, x, y, d=0.0, n=3):
    """Things falling together: a station + atoms + arrows all drifting down."""
    E = []
    for q in range(n):
        E += arr(a, x - 300 + 300 * q, y - 120, x - 300 + 300 * q, y + 120, c="muted", d=d + 0.1 * q)
    return E


# ---------- boards ----------
bd(0, station(0, 960, 450, 360), rubi(0, 1500, 750, 0.8, 0.3), big(0, 960, 880, "人类已知最冷", c="blue", d=0.4, s=110))
bd(0.5, rubi(0.5, 650, 560, 1.6, 0.0), cloud(0.5, 1350, 560, 9, 120, 0.2, amp=2, hz=0.6), ic(0.5, "thermometer", 1650, 560, 200, 0.4, mv="wig", c="blue"))
bd(1, big(1, 960, 420, "9.7 pK", c="blue", d=0.0, s=200), rubi(1, 450, 700, 0.8, 0.2), ic(1, "thermometer", 1450, 720, 220, 0.3, mv="wig", c="blue"))
bd(1.5, big(1.5, 960, 330, "−273.15 ℃", c="ink", d=0.0, s=130), arr(1.5, 960, 480, 960, 700, c="blue", d=0.2), rubi(1.5, 960, 820, 0.7, 0.4, mood="o"), cloud(1.5, 400, 700, 7, 90, 0.3, amp=2, hz=0.5))
bd(2, ic(2, "globe", 600, 600, 260, 0.0, mv="spin", c="blue"), ic(2, "moon", 1000, 350, 120, 0.2, mv="bob"), [star(2, 300 + 260 * q, 300 + 90 * (q % 2), 0.1 * q, r=30) for q in range(6)],
   rubi(2, 1450, 650, 0.9, 0.4))
bd(2.5, bar(2.5, 600, 950, 220, 600, "red", 0.0, 1.0), t(2.5, 710, 1010, 44, "宇宙深空 2.7 K", d=0.0), bar(2.5, 1100, 950, 220, 8, "blue", 0.4), t(2.5, 1210, 1010, 44, "9.7 pK", c="blue", d=0.4),
   big(2.5, 1350, 350, "冷约 2800 亿倍", c="blue", d=0.5, s=90), rubi(2.5, 1600, 700, 0.6, 0.6))
bd(3, ic(3, "magnifier", 500, 560, 240, 0.0, mv="wig"), t(3, 1200, 380, 90, "《科学》", c="red", d=0.2), ic(3, "atom", 1200, 650, 200, 0.3, mv="spin", c="blue"), check(3, 1550, 650, d=0.5))
bd(3.5, ic(3.5, "phone", 450, 600, 260, 0.0, mv="wig"), ic(3.5, "phone", 960, 600, 220, 0.1, mv="wig"), ic(3.5, "phone", 1450, 600, 260, 0.2, mv="wig"),
   big(3.5, 960, 280, "刷屏", c="red", d=0.3, s=130), star(3.5, 1700, 400, 0.4, r=40))
bd(4, big(4, 960, 260, "烧脑问题", c="red", d=0.0, s=120), ic(4, "question", 500, 620, 260, 0.1, mv="wig", c="red"), rubi(4, 1050, 650, 1.0, 0.2, mood="o"), station(4, 1550, 600, 200, 0.4))
bd(4.5, ic(4.5, "globe", 500, 750, 260, 0.0, mv="spin", c="blue"), arr(4.5, 650, 650, 1250, 380, c="red", d=0.2), station(4.5, 1450, 330, 200, 0.4), ic(4.5, "question", 1450, 700, 200, 0.5, mv="wig", c="red"))
bd(5, rubi(5, 960, 560, 2.0, 0.0), t(5, 960, 940, 70, "小铷", c="blue", d=0.3), star(5, 600, 400, 0.4, r=40), star(5, 1320, 400, 0.5, r=40))
bd(5.5, rubi(5.5, 700, 600, 1.4, 0.0), big(5.5, 1350, 450, "Rb", c="blue", d=0.2, s=170), t(5.5, 1350, 700, 56, "铷 · 第 37 号元素", d=0.3), ic(5.5, "flask", 1650, 850, 140, 0.4, mv="wig"))
bd(6, ic(6, "thermometer", 500, 580, 300, 0.0, mv="wig", c="red"), ic(6, "question", 960, 400, 160, 0.2, mv="wig", c="red"), cloud(6, 1350, 600, 11, 150, 0.2, c="red", amp=14, hz=4))
bd(6.5, rubi(6.5, 600, 600, 1.2, 0.1, cold=False), cloud(6.5, 1300, 600, 11, 160, 0.0, c="red", amp=18, hz=5), t(6.5, 960, 950, 64, "温度 = 原子乱跑的快慢", c="red", d=0.4))
bd(7, rubi(7, 500, 600, 1.1, 0.0, cold=False), [arr(7, 700, 520 + 60 * q, 1150, 520 + 60 * q, c="red", d=0.2 + 0.1 * q) for q in range(3)], big(7, 1450, 350, "每秒几百米", c="red", d=0.3, s=100),
   ic(7, "wind", 1450, 650, 180, 0.4, mv="wig"))
bd(7.5, ic(7.5, "rocket", 600, 560, 260, 0.0, mv="wig"), sh(7.5, [], 0, 0, 0, 0.1) if False else [], rubi(7.5, 1300, 600, 0.9, 0.2, cold=False), arr(7.5, 1300, 800, 1700, 800, c="red", d=0.3),
   t(7.5, 960, 950, 64, "跟飞机差不多快", d=0.3), escape(7.5, 300, 300, 1400, 0, 0.4))
bd(8, rubi(8, 600, 600, 1.4, 0.0), big(8, 1350, 400, "0.05 毫米/秒", c="blue", d=0.2, s=100), ic(8, "ruler", 1350, 700, 240, 0.3, mv="wig"), cloud(8, 1350, 900, 7, 120, 0.4, amp=1, hz=0.3))
bd(8.5, rubi(8.5, 700, 650, 1.0, 0.0, mood="o"), arr(8.5, 900, 650, 960, 650, c="blue", d=0.3, dur=2.0), ic(8.5, "clock", 1400, 500, 240, 0.1, mv="spin"), t(8.5, 1400, 800, 56, "慢得像没动", c="blue", d=0.4))
bd(9, snail(9, 600, 800, 1.6, 0.0), rubi(9, 1300, 650, 0.8, 0.2), big(9, 1300, 350, "慢 20 倍", c="red", d=0.3, s=120))
bd(9.5, ic(9.5, "calc" if False else "chip", 500, 600, 220, 0.0, mv="wig", c="blue"), t(9.5, 1250, 450, 64, "我们估算的", c="muted", d=0.2), snail(9.5, 1250, 800, 1.0, 0.3), star(9.5, 1650, 500, 0.4, r=40))
bd(10, rubi(10, 960, 600, 1.2, 0.0, cold=False, mood="o"), ic(10, "question", 500, 500, 200, 0.2, mv="wig", c="red"), ic(10, "laser", 1450, 500, 220, 0.3, mv="wig", c="red"))
bd(10.5, ic(10.5, "laser", 450, 600, 240, 0.0, mv="wig", c="red"), laser(10.5, 600, 600, 1150, 600, 0.2), rubi(10.5, 1300, 600, 1.0, 0.3, cold=False), big(10.5, 1300, 300, "激光刹车", c="red", d=0.4, s=100))
bd(11, rubi(11, 960, 560, 1.0, 0.0), [laser(11, x, y, 960 + (x - 960) * 0.35, 560 + (y - 560) * 0.35, 0.1 + 0.08 * q) for q, (x, y) in enumerate([(300, 560), (1620, 560), (960, 150), (960, 970), (450, 200), (1470, 920)])])
bd(11.5, man(11.5, 1100, 950, 1.5, 0.0, arms="up"), [escape(11.5, 300, 450 + 90 * q, 600, 0, 0.1 + 0.2 * q, c="gold") for q in range(4)], arr(11.5, 1300, 600, 1650, 600, c="blue", d=0.3),
   t(11.5, 1500, 400, 56, "越跑越慢", c="blue", d=0.5))
bd(12, soup(12, 700, 700, 0.0), man(12, 1350, 950, 1.4, 0.1), ic(12, "wind", 1050, 500, 180, 0.3, mv="wig"), t(12, 960, 250, 70, "蒸发冷却", c="blue", d=0.3))
bd(12.5, soup(12.5, 600, 700, 0.0), ic(12.5, "thermometer", 1150, 600, 220, 0.2, mv="wig", c="red"), arr(12.5, 1350, 450, 1350, 750, c="blue", d=0.4), big(12.5, 1600, 600, "凉", c="blue", d=0.5, s=150))
bd(13, soup(13, 960, 750, 0.0), [escape(13, 900 + 60 * q, 600, -300 + 300 * q, -350, 0.2 + 0.15 * q) for q in range(3)], cloud(13, 960, 750, 6, 70, 0.1, amp=4, hz=2))
bd(13.5, soup(13.5, 700, 700, 0.0), cloud(13.5, 700, 720, 6, 70, 0.0, amp=2, hz=1), ic(13.5, "thermometer", 1300, 600, 260, 0.2, mv="wig", c="blue"), check(13.5, 1600, 600, d=0.5))
bd(14, bowl(14, 960, 600, 700, 300, 0.0), cloud(14, 960, 600, 11, 120, 0.2, c="red", amp=10, hz=3), ic(14, "laser", 400, 300, 140, 0.3, mv="wig", c="red"), ic(14, "laser", 1520, 300, 140, 0.4, mv="wig", c="red"))
bd(14.5, bowl(14.5, 960, 650, 700, 150, 0.0), cloud(14.5, 960, 640, 9, 110, 0.1, amp=6, hz=2), escape(14.5, 700, 520, -400, -350, 0.3), escape(14.5, 1220, 520, 400, -350, 0.5),
   t(14.5, 960, 250, 64, "碗边放低，快的溜了", c="red", d=0.3))
bd(15, big(15, 960, 260, "反转一", c="red", d=0.0, s=140), bowl(15, 960, 700, 600, 120, 0.2), cloud(15, 960, 700, 7, 90, 0.3, amp=2, hz=0.6), ic(15, "thermometer", 1550, 650, 200, 0.4, mv="wig", c="blue"))
bd(15.5, ic(15.5, "globe", 450, 650, 260, 0.0, mv="spin", c="blue"), bowl(15.5, 1200, 650, 600, 250, 0.2), cloud(15.5, 1200, 700, 7, 90, 0.3, amp=4, hz=1.5), cross(15.5, 1200, 330, d=0.5))
bd(16, bowl(16, 960, 500, 600, 200, 0.0), cloud(16, 960, 520, 7, 90, 0.1, amp=4, hz=2), [arr(16, 760 + 200 * q, 650, 760 + 200 * q, 950, c="ink", d=0.2 + 0.1 * q) for q in range(3)],
   t(16, 1550, 350, 70, "重力", c="red", d=0.3))
bd(16.5, bowl(16.5, 960, 450, 600, 80, 0.0), [escape(16.5, 860 + 100 * q, 520, 0, 480, 0.2 + 0.15 * q, c="blue") for q in range(3)], rubi(16.5, 1550, 600, 0.7, 0.3, mood="sad"), big(16.5, 450, 400, "漏光了", c="red", d=0.4, s=110))
bd(17, P(17, "M300,900 L1600,500", c="ink", w=8, idp="slope"), pop(17, "slope", 0.0), soup(17, 900, 620, 0.1), rot(17, [], 0, (0, 0), 0, 0.1) if False else [],
   man(17, 1550, 520, 1.2, 0.3), ic(17, "question", 400, 400, 160, 0.4, mv="wig", c="red"))
bd(17.5, P(17.5, "M300,900 L1600,500", c="ink", w=8, idp="slope2"), pop(17.5, "slope2", 0.0), soup(17.5, 900, 620, 0.1),
   [escape(17.5, 760, 640, -300, 200, 0.3 + 0.15 * q, c="gold") for q in range(3)], big(17.5, 1350, 300, "洒了！", c="red", d=0.4, s=120))
bd(18, ic(18, "globe", 500, 800, 300, 0.0, mv="spin", c="blue"), station(18, 1100, 380, 240, 0.1), rubi(18, 1500, 450, 0.6, 0.3), arr(18, 1100, 520, 900, 700, c="red", d=0.4),
   P(18, "M500,300 Q1300,250 1500,800", c="muted", w=4, idp="orb"), pop(18, "orb", 0.2))
bd(18.5, station(18.5, 700, 500, 260, 0.0), rubi(18.5, 1200, 500, 0.9, 0.1), man(18.5, 1600, 800, 1.0, 0.2, arms="up"), fall(18.5, 1100, 850, 0.3), t(18.5, 1100, 250, 64, "一起下落 = 没有“下”", c="blue", d=0.4))
bd(19, bowl(19, 960, 650, 700, 60, 0.0, c="blue"), cloud(19, 960, 610, 9, 110, 0.1, amp=2, hz=0.7), check(19, 1500, 400, d=0.4), rubi(19, 450, 400, 0.6, 0.3))
bd(19.5, bowl(19.5, 960, 650, 700, 30, 0.0, c="blue"), cloud(19.5, 960, 620, 9, 100, 0.1, amp=1, hz=0.5), big(19.5, 960, 300, "乖乖待着", c="blue", d=0.3, s=110), rubi(19.5, 1550, 750, 0.6, 0.4))
bd(20, big(20, 960, 260, "反转二", c="red", d=0.0, s=140), rubi(20, 600, 650, 1.0, 0.2, mood="o"), ic(20, "flame", 1300, 650, 200, 0.3, mv="wig", c="red"), star(20, 1600, 450, 0.4, r=40))
bd(20.5, t(20.5, 960, 350, 90, "非绝热扩散", c="blue", d=0.0), cloud(20.5, 960, 700, 9, 80, 0.2, amp=3, hz=1), arr(20.5, 1100, 700, 1500, 700, c="blue", d=0.3), arr(20.5, 820, 700, 420, 700, c="blue", d=0.3))
bd(21, bowl(21, 700, 650, 300, 150, 0.0), cloud(21, 700, 640, 7, 50, 0.1, amp=3, hz=1.5), arr(21, 900, 650, 1100, 650, c="red", d=0.3), bowl(21, 1450, 650, 650, 150, 0.4, c="blue"))
bd(21.5, bowl(21.5, 960, 650, 900, 150, 0.0, c="blue"), cloud(21.5, 960, 640, 9, 200, 0.1, amp=1, hz=0.4), ic(21.5, "thermometer", 1650, 450, 200, 0.2, mv="wig", c="blue"), arr(21.5, 1650, 600, 1650, 800, c="blue", d=0.4))
bd(22, can(22, 700, 650, 0.0), man(22, 1300, 950, 1.4, 0.1, arms="up"), ic(22, "wind", 700, 300, 140, 0.3, mv="wig"), t(22, 1300, 350, 64, "开汽水", d=0.3))
bd(22.5, can(22.5, 700, 650, 0.0), ic(22.5, "thermometer", 1250, 600, 220, 0.2, mv="wig", c="blue"), big(22.5, 1600, 600, "凉", c="blue", d=0.4, s=150))
bd(23, ic(23, "satellite", 600, 450, 220, 0.0, mv="bob"), t(23, 600, 700, 56, "国际空间站 2022", d=0.1), bar(23, 1150, 950, 200, 540, "red", 0.2), big(23, 1250, 330, "52 pK", c="red", d=0.4, s=110))
bd(23.5, bar(23.5, 700, 950, 200, 540, "red", 0.0), t(23.5, 800, 1010, 44, "52 pK", d=0.0), bar(23.5, 1100, 950, 200, 100, "blue", 0.3), t(23.5, 1200, 1010, 44, "9.7 pK", c="blue", d=0.3),
   station(23.5, 1600, 450, 200, 0.4), rubi(23.5, 1200, 700, 0.5, 0.5))
bd(24, big(24, 960, 350, "低 5 倍多", c="red", d=0.0, s=150), [arr(24, 600 + 180 * q, 600, 600 + 180 * q, 800, c="blue", d=0.2 + 0.08 * q) for q in range(5)], rubi(24, 1650, 750, 0.6, 0.4))
bd(24.5, ic(24.5, "clock", 600, 560, 280, 0.0, mv="spin"), big(24.5, 1250, 400, "7 秒", c="blue", d=0.2, s=170), ic(24.5, "eye", 1250, 750, 180, 0.3, mv="wig", c="red"), cloud(24.5, 1650, 750, 5, 60, 0.4, amp=1, hz=0.4))
bd(25, big(25, 960, 260, "反转三", c="red", d=0.0, s=140), ic(25, "building", 600, 680, 300, 0.2, mv="bob"), t(25, 1300, 600, 70, "20 立方米", d=0.3), t(25, 1300, 760, 70, "10 吨", c="red", d=0.4))
bd(25.5, R(25.5, 300, 300, 800, 600, c="ink", fill="paper", idp="lab"), pop(25.5, "lab", 0.0), [ic(25.5, n_, 450 + 250 * (q % 3), 450 + 280 * (q // 3), 140, 0.1 + 0.05 * q, mv="wig", c="red")
   for q, n_ in enumerate(["laser", "lens", "mirror", "magnet", "chip", "gear"])], man(25.5, 1500, 950, 1.5, 0.3, arms="up"))
bd(26, R(26, 750, 400, 300, 400, c="ink", fill="paper", idp="cab"), pop(26, "cab", 0.0), wig(26, "cab", (900, 800), 2, 1.5), t(26, 900, 900, 50, "0.7 立方米", d=0.2), ic(26, "building", 450, 600, 200, 0.1, mv="bob"),
   arr(26, 560, 600, 730, 600, c="red", d=0.3), check(26, 1300, 600, d=0.5))
bd(26.5, R(26.5, 700, 400, 300, 400, c="ink", fill="paper", idp="cab2"), pop(26.5, "cab2", 0.0), ic(26.5, "laser", 850, 520, 120, 0.1, mv="wig", c="red"), ic(26.5, "chip", 850, 700, 100, 0.2, mv="spin", c="blue"),
   big(26.5, 1400, 500, "半吨", c="red", d=0.3, s=150), station(26.5, 1400, 800, 160, 0.4))
bd(27, big(27, 960, 330, "2011", c="ink", d=0.0, s=170), arr(27, 500, 650, 1400, 650, c="blue", d=0.2, dur=1.2), ic(27, "flask", 450, 650, 140, 0.1, mv="wig"), station(27, 1550, 650, 180, 0.5))
bd(27.5, ic(27.5, "clock", 600, 560, 300, 0.0, mv="spin"), big(27.5, 1250, 450, "≈15 年", c="red", d=0.2, s=150), man(27.5, 1250, 950, 1.0, 0.3, arms="up"), star(27.5, 1600, 700, 0.4, r=40))
bd(28, big(28, 1300, 400, "5 克", c="blue", d=0.0, s=170), cloud(28, 600, 550, 11, 140, 0.1, amp=3, hz=1), ic(28, "flask", 600, 800, 160, 0.2, mv="wig"), rubi(28, 1300, 750, 0.6, 0.3))
bd(28.5, O(28.5, 700, 600, 150, c="ink", fill="gold", idp="coin"), pop(28.5, "coin", 0.0), wig(28.5, "coin", (700, 600), 6, 1.5), t(28.5, 700, 600, 70, "1 元", d=0.1),
   big(28.5, 1350, 450, "更轻", c="blue", d=0.3, s=140), cloud(28.5, 1350, 750, 6, 80, 0.4, amp=2, hz=1))
bd(29, ic(29, "question", 600, 560, 260, 0.0, mv="wig", c="red"), rubi(29, 1250, 560, 1.0, 0.2), ic(29, "ruler", 1250, 850, 220, 0.4, mv="wig"))
bd(29.5, ic(29.5, "ruler", 650, 600, 320, 0.0, mv="wig"), cloud(29.5, 1300, 600, 9, 120, 0.1, amp=1, hz=0.4), t(29.5, 1300, 350, 70, "越慢越准", c="blue", d=0.3), check(29.5, 1650, 750, d=0.5))
bd(30, ic(30, "sine", 500, 560, 260, 0.0, mv="wig", c="blue"), ic(30, "globe", 1100, 600, 260, 0.1, mv="spin", c="blue"), arr(30, 1100, 300, 1100, 450, c="red", d=0.3), t(30, 1100, 900, 56, "测重力", d=0.3),
   ic(30, "map_pin", 1600, 600, 160, 0.4, mv="bob", c="red"))
bd(30.5, ic(30.5, "rocket", 600, 600, 260, 0.0, mv="wig"), arr(30.5, 750, 600, 1200, 450, c="blue", d=0.2), ic(30.5, "map_pin", 1350, 420, 160, 0.3, mv="bob", c="red"), t(30.5, 1300, 800, 64, "导航", c="blue", d=0.4))
bd(31, ic(31, "magnifier", 600, 560, 280, 0.0, mv="wig"), cloud(31, 1300, 560, 11, 200, 0.1, c="muted", amp=8, hz=1), t(31, 1300, 900, 64, "暗物质？", c="ink", d=0.3))
bd(31.5, ic(31.5, "sun", 960, 520, 300, 0.0, mv="spin", c="gold"), [arr(31.5, 960 + 220 * dx, 520 + 220 * dy, 960 + 420 * dx, 520 + 420 * dy, c="red", d=0.2 + 0.08 * q)
   for q, (dx, dy) in enumerate([(1, 0), (-1, 0), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7)])], t(31.5, 960, 1000, 56, "模拟宇宙刚诞生", d=0.4))
bd(32, big(32, 960, 280, "友情提示", c="blue", d=0.0, s=120), cloud(32, 700, 650, 7, 70, 0.2, amp=1, hz=0.4), O(32, 700, 650, 150, c="blue", idp="ring"), pop(32, "ring", 0.3), wig(32, "ring", (700, 650), 3, 1),
   t(32, 1300, 650, 60, "只有这团原子云", d=0.3))
bd(32.5, station(32.5, 700, 550, 300, 0.0), man(32.5, 1300, 950, 1.3, 0.2, arms="up"), ic(32.5, "thermometer", 1650, 600, 200, 0.3, mv="wig", c="red"), t(32.5, 1300, 380, 64, "一点也不冷", c="red", d=0.4))
bd(33, snail(33, 600, 800, 1.2, 0.0), t(33, 1300, 400, 70, "2800 亿倍", c="blue", d=0.2), ic(33, "chip", 1300, 700, 180, 0.3, mv="wig", c="blue"))
bd(33.5, ic(33.5, "magnifier", 600, 560, 260, 0.0, mv="wig"), t(33.5, 1250, 450, 64, "估算，算个大概", c="muted", d=0.2), ic(33.5, "question", 1300, 720, 160, 0.3, mv="wig", c="red"), star(33.5, 1700, 700, 0.4, r=40))
bd(34, ic(34, "question", 600, 560, 280, 0.0, mv="wig", c="red"), station(34, 1300, 500, 240, 0.2), rubi(34, 1300, 820, 0.6, 0.3))
bd(34.5, bowl(34.5, 700, 650, 600, 40, 0.0, c="blue"), cloud(34.5, 700, 620, 7, 90, 0.1, amp=1, hz=0.5), check(34.5, 700, 350, d=0.3), bowl(34.5, 1400, 500, 400, 60, 0.2), [escape(34.5, 1350 + 50 * q, 560, 0, 220, 0.3 + 0.1 * q, c="blue") for q in range(2)],
   cross(34.5, 1400, 300, d=0.5), t(34.5, 700, 900, 50, "太空", c="blue", d=0.2), t(34.5, 1650, 650, 50, "地面", d=0.3))
bd(35, ic(35, "globe", 600, 750, 300, 0.0, mv="spin", c="blue"), station(35, 1300, 350, 260, 0.2), rubi(35, 1500, 650, 0.7, 0.3), arr(35, 750, 550, 1150, 400, c="blue", d=0.4))
bd(35.5, station(35.5, 960, 500, 380, 0.0), rubi(35.5, 500, 700, 0.8, 0.2), rubi(35.5, 1420, 700, 0.8, 0.3), big(35.5, 960, 900, "最冷的在天上", c="blue", d=0.4, s=100))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"pK": "皮开尔文", "Rb": "铷"})
