"""每日科普 2026-11-07（中文）：《北京上空的绿火球，是啥？》
热点：2026-11-06 晚约 18:30，北京、河北、山西多地网友目击并拍到“火流星”（新浪科学热点小时报 2026-11-07 01 时第 10 条“多省现火流星”、
  第 7 条“北京上空绿尾流星”；阅读榜同期；澎湃、腾讯新闻、楚天都市报、新华社等报道）。
事实：
- 澎湃（红星新闻）2026-11-06：约 18:30，北京四元桥、海淀万安东路、丰台等地网友在西南方向看到，约 30 度角快速下落；
  张家口网友称持续四五秒，有绿、黄、红光；北京天文馆原馆长朱进：多半是火流星，属偶发流星，可能留有陨石。
- 腾讯新闻 2026-11-07：北京天文馆科普部主任李昕：从视频看北京、山西、河北看到的是同一颗；新华社：山西阳泉多个监测点记录到明亮火流星；
  朱进：估计“比较大个儿”；比金星还亮的流星叫火流星；可能空中解体，有的伴随声响。
- 教科书：流星体进入大气速度约 11–72 km/s；发光高度多在约 70–120 km；发光主要来自前方空气被猛烈压缩加热（冲压），不是主要靠摩擦；
  流星光谱：绿色常归因于镁、镍等金属和氧原子的谱线，黄色常来自钠，红色常来自大气氮、氧；每天落入大气的太空物质常见估计为几十吨，绝大多数是尘粒；
  陨石最后一段“暗飞”，减速到几百公里每小时以下，落地时通常不发光。
我们的估算/说法（片中说明）：北京到阳泉直线约三百来公里（地图估算）；“比步枪子弹快几十倍”（子弹约 1 km/s）；比喻：打气筒、烟花、高楼看远。
推测：是否有陨石落地尚无报道；颜色成因是常见解释，具体成分要看光谱。
出处：
- https://k.sina.com.cn/article_7857201856_1d45362c001908twri.html
- https://www.thepaper.cn/newsDetail_forward_34423257
- https://news.qq.com/rain/a/20261107A0414Z00
- https://www.ctdsb.net/c1476_202611/2898276.html
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402,F401
                     star, uid, wig)
from popkit import cute_meteor, stick  # noqa: E402

S = [
 ("昨晚六点半，北京上空|一个大火球拖着绿光往下砸。", "Last night at 6:30, over Beijing, | a huge fireball fell trailing green light."),
 ("河北、山西的网友也拍到了，|天文馆专家说：多半是同一颗。", "People in Hebei and Shanxi filmed it too; | planetarium experts say it was probably the same one."),
 ("一颗流星，|照亮了三个省。", "One meteor, | lighting up three provinces."),
 ("今天的烧脑问题：一块太空石头，|凭什么亮成这样，还带绿光？", "Today's brain teaser: how can a space rock | glow this bright, and green?"),
 ("认识主角：小火，|一块在太空飘了很久的石头。", "Meet our hero, Blaze, | a rock that drifted in space for ages."),
 ("它绕着太阳跑，|正好撞上了地球。", "It circled the Sun, | and ran right into Earth."),
 ("撞进来有多快？|流星一般每秒十几到七十多公里。", "How fast? | Meteors hit at roughly 11 to 72 km per second."),
 ("每秒几十公里，|比步枪子弹快几十倍。", "Tens of km per second: | dozens of times faster than a rifle bullet."),
 ("反转一：它发光，|主要不是因为摩擦。", "Twist one: | it does not glow mainly from friction."),
 ("它太快了，前面的空气来不及让开，|被挤得越来越紧。", "It is so fast the air ahead cannot get out of the way, | and gets squeezed tighter and tighter."),
 ("就像打气筒，|压得越狠，筒越烫。", "Like a bike pump: | the harder you squeeze, the hotter it gets."),
 ("被压缩的空气烫到几千度，|把石头表面烤化、烤成气。", "The squeezed air reaches thousands of degrees, | melting and vaporizing the rock's skin."),
 ("这团热气和空气一起发光，|这就是流星。", "That hot gas glows along with the air. | That is a meteor."),
 ("反转二：为啥是绿的？|颜色是原子的“指纹”。", "Twist two: why green? | Color is an atom's fingerprint."),
 ("每种原子被烤“兴奋”了，|只放出自己那几种颜色的光。", "Each kind of atom, when heated up, | gives off only its own few colors."),
 ("就像烟花：钠是黄的，|锶是红的。", "Like fireworks: sodium is yellow, | strontium is red."),
 ("流星里的镁、镍，还有空气里的氧，|常被认为是绿光的来源。", "Magnesium and nickel in the rock, plus oxygen in the air, | are the usual suspects for green."),
 ("黄色常来自钠，|红色常来自空气里的氮和氧。", "Yellow often comes from sodium, | red from nitrogen and oxygen in the air."),
 ("所以网友看到的绿、黄、红，|其实是一张化学成分表。", "So the green, yellow and red people saw | is really a chemistry report."),
 ("反转三：为啥北京、河北、山西|都能看到同一颗？", "Twist three: how could Beijing, Hebei and Shanxi | all see the same one?"),
 ("因为流星多半在七八十公里以上发光，|比飞机高差不多十倍。", "Meteors usually glow 70 km up or higher, | about ten times higher than airliners."),
 ("站得越高，看得越远；|反过来，越高的东西，越多地方能看到它。", "The higher you stand, the farther you see; | and the higher a thing is, the more places can see it."),
 ("新华社报道，山西阳泉的监测点也拍到了，|我们估算离北京三百来公里。", "Xinhua says monitors in Yangquan, Shanxi caught it too, | about 300 km from Beijing by our estimate."),
 ("天文学上，比金星还亮的流星，|就叫火流星。", "In astronomy, a meteor brighter than Venus | is called a fireball."),
 ("专家估计这颗“比较大个儿”，|可能留下了陨石。", "Experts think this one was fairly big, | and may have dropped meteorites."),
 ("大部分石头在半空就烧光了，|撑到地面的那一点才叫陨石。", "Most of the rock burns up high in the sky. | The bits that reach the ground are meteorites."),
 ("最后那一段它不亮了：|空气把它刹得很慢，像普通石头一样掉。", "The last stretch is dark: | the air brakes it until it just drops like a stone."),
 ("地球每天要挨多少太空石头？|常见估计：几十吨。", "How much space stuff hits Earth each day? | A common estimate: tens of tons."),
 ("绝大多数比沙粒还小，|你根本看不见。", "Almost all of it is smaller than sand grains, | far too small to see."),
 ("友情提示：目前还没有找到陨石的报道，|“可能”只是可能。", "Fine print: no meteorite has been reported found yet. | Maybe means maybe."),
 ("真捡到可疑的石头，|先拍照、记位置，再联系天文馆。", "If you find a suspicious rock, | photograph it, note the spot, and call a planetarium."),
 ("想看流星？|找个远离灯光的地方，抬头多等一会儿。", "Want to see one? | Find a dark spot, look up, and be patient."),
 ("所以小火凭什么亮成这样？|速度太快，把空气压烫了。", "So why did Blaze glow so bright? | It was so fast it crushed the air red hot."),
 ("为啥带绿光？|原子在报自己的名字。", "Why green? | The atoms were calling out their names."),
 ("一块石头在太空飘了几十亿年，|最后五秒，给三个省放了场烟花。", "A rock that drifted for billions of years | spent its last five seconds as fireworks for three provinces."),
]
TITLE = {"zh": "北京上空的绿火球，是啥？", "en": "What Was the Green Fireball over Beijing?"}

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


def man(a, x, y, k=1.4, d=0.0, arms="down", amp=3):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": amp, "hz": 1.6}]


def blaze(a, x, y, k=1.0, d=0.0, mood="happy", tail=True, dx=0, dy=0, dur=1.2):
    i = uid("bz")
    E = cute_meteor(x, y, k, a, idp=i, mood=mood, tail=tail) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if dx or dy:
        E.append(sh(a, i + "*", dx, dy, d + 0.3, dur))
    return E


def ball(a, x, y, dx, dy, d=0.0, c="red", dur=1.0, r=18):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, dur)]


def streak(a, x0, y0, x1, y1, c="green", d=0.0, w=8):
    i = uid("sk")
    return [P(a, f"M{x0},{y0} L{x1},{y1}", c=c, w=w, idp=i), pop(a, i, d), wig(a, i, (x1, y1), 2, 4)]


def flame(a, x, y, s=120, d=0.0, c="red"):
    return ic(a, "flame", x, y, s, d, mv="wig", c=c)


def sky(a, d=0.0):
    i = uid("sky")
    return [P(a, "M120,980 L700,960 L760,900 L820,960 L1100,950 L1150,880 L1200,950 L1800,970", c="ink", w=6, idp=i), pop(a, i, d)]


def earth(a, x, y, s=300, d=0.0):
    return ic(a, "globe", x, y, s, d, mv="spin", c="blue")


def pump(a, x, y, d=0.0):
    i, j = uid("pm"), uid("pp")
    return [R(a, x - 60, y - 150, 120, 300, c="ink", fill="paper", idp=i), pop(a, i, d), wig(a, i, (x, y + 150), 1, 1),
            P(a, f"M{x},{y - 150} L{x},{y - 300} M{x - 80},{y - 300} L{x + 80},{y - 300}", c="ink", w=10, idp=j), pop(a, j, d + 0.1),
            {"t": "move", "at": a, "kind": "shift", "targets": [j], "dx": 0, "dy": 120, "dur": 0.5, "delay": d + 0.3},
            {"t": "move", "at": a, "kind": "bob", "targets": [j], "amp": 30, "hz": 1.5}]


def dots(a, x, y, n=8, c="blue", d=0.0, squeeze=0):
    E = []
    for q in range(n):
        i = uid("dt")
        E += [O(a, x + (q % 4) * 60, y + (q // 4) * 60, 14, c=c, fill=c, idp=i), pop(a, i, d + 0.04 * q), wig(a, i, (x, y), 6, 3)]
        if squeeze:
            E.append(sh(a, i, squeeze - (q % 4) * 15, 0, d + 0.5, 0.8))
    return E


def firework(a, x, y, c="gold", d=0.0, r=120):
    E = []
    for q in range(8):
        import math
        ang = q * math.pi / 4
        E += arr(a, x + 30 * math.cos(ang), y + 30 * math.sin(ang), x + r * math.cos(ang), y + r * math.sin(ang), c=c, d=d + 0.03 * q)
    i = uid("fw")
    return E + [O(a, x, y, 20, c=c, fill=c, idp=i), pop(a, i, d), spin(a, i, (x, y), 90)]


def bars(a, x, y, cols, d=0.0):
    E = []
    for q, c in enumerate(cols):
        i = uid("ln")
        E += [R(a, x + q * 70, y, 30, 260, c=c, fill=c, idp=i), pop(a, i, d + 0.08 * q), wig(a, i, (x + q * 70 + 15, y + 260), 2, 2)]
    return E


# ---------- boards ----------
bd(0, sky(0), blaze(0, 1500, 250, 1.4, 0.0, mood="o", dx=-700, dy=450, dur=2.5), big(0, 600, 300, "18:30", c="red", d=0.3, s=140), man(0, 400, 960, 1.0, 0.2, arms="up", amp=8))
bd(0.5, sky(0.5), streak(0.5, 1600, 150, 900, 650, "green", 0.0, 14), blaze(0.5, 900, 650, 1.0, 0.1, mood="o"), big(0.5, 500, 300, "绿光！", c="green", d=0.3, s=150), [ic(0.5, "building", 1300 + 150 * q, 860, 140, 0.2 + 0.05 * q, mv="bob") for q in range(3)])
bd(1, [ic(1, "phone", 450 + 500 * q, 600, 220, 0.1 * q, mv="wig") for q in range(3)], [t(1, 450 + 500 * q, 850, 56, n, c="blue", d=0.2 + 0.1 * q) for q, n in enumerate(["北京", "河北", "山西"])], streak(1, 1700, 150, 1300, 400, "green", 0.3))
bd(1.5, ic(1.5, "telescope" if False else "eye", 500, 550, 260, 0.0, mv="wig"), big(1.5, 1250, 450, "同一颗", c="red", d=0.2, s=150), blaze(1.5, 1250, 800, 0.8, 0.3))
bd(2, blaze(2, 960, 300, 1.2, 0.0, dx=0, dy=60, dur=2), [O(2, 500 + 460 * q, 800, 120, c=["blue", "green", "gold"][q], idp=f"pv{q}") for q in range(3)], [pop(2, f"pv{q}", 0.2 + 0.1 * q) for q in range(3)], [wig(2, f"pv{q}", (960, 800), 3, 1.5) for q in range(3)])
bd(2.5, big(2.5, 960, 350, "3 个省", c="red", d=0.0, s=180), [ic(2.5, "sun", 500 + 460 * q, 750, 160, 0.2 + 0.1 * q, mv="spin", c="gold") for q in range(3)])
bd(3, big(3, 960, 230, "烧脑问题", c="red", d=0.0, s=120), blaze(3, 650, 650, 1.3, 0.1, mood="o"), ic(3, "question", 1350, 600, 260, 0.2, mv="wig", c="red"))
bd(3.5, ic(3.5, "sun", 600, 550, 260, 0.0, mv="spin", c="gold"), ic(3.5, "question", 1000, 550, 180, 0.2, mv="wig", c="green"), blaze(3.5, 1400, 600, 1.0, 0.3), t(3.5, 960, 900, 64, "这么亮？还是绿的？", d=0.3))
bd(4, blaze(4, 960, 560, 2.2, 0.0, tail=False), t(4, 960, 920, 70, "小火", c="red", d=0.3), star(4, 450, 380, 0.4, r=40), star(4, 1470, 380, 0.5, r=40))
bd(4.5, [star(4.5, 300 + 220 * q, 250 + 140 * (q % 3), 0.05 * q, r=25) for q in range(7)], blaze(4.5, 960, 650, 1.2, 0.1, tail=False, dx=200, dy=-60, dur=3), ic(4.5, "clock", 1550, 750, 160, 0.3, mv="spin"))
bd(5, ic(5, "sun", 960, 550, 220, 0.0, mv="spin", c="gold"), O(5, 960, 550, 330, c="muted", idp="orb5", sw=4), pop(5, "orb5", 0.1), blaze(5, 1290, 550, 0.5, 0.2, tail=False, dx=-80, dy=-250, dur=2.5), earth(5, 630, 550, 120, 0.3))
bd(5.5, earth(5.5, 1300, 650, 360, 0.0), blaze(5.5, 400, 250, 0.9, 0.1, mood="o", dx=650, dy=250, dur=1.5), big(5.5, 600, 850, "砰！", c="red", d=0.5, s=140))
bd(6, ic(6, "clock", 500, 550, 260, 0.0, mv="spin"), blaze(6, 1300, 450, 1.0, 0.1, dx=-200, dy=150, dur=1.5), ic(6, "question", 1300, 850, 140, 0.2, mv="wig", c="red"))
bd(6.5, big(6.5, 960, 380, "11–72", c="red", d=0.0, s=180), t(6.5, 960, 600, 70, "公里 / 秒", c="ink", d=0.2), ball(6.5, 300, 850, 1300, 0, 0.2, c="red", dur=0.8), blaze(6.5, 1600, 850, 0.6, 0.4))
bd(7, ball(7, 300, 500, 300, 0, 0.0, c="muted", dur=2.0, r=14), t(7, 450, 400, 56, "子弹", d=0.1), blaze(7, 300, 800, 0.8, 0.2, dx=1200, dy=0, dur=0.8), t(7, 1300, 650, 56, "小火", c="red", d=0.4))
bd(7.5, big(7.5, 960, 380, "× 几十倍", c="red", d=0.0, s=160), ic(7.5, "wind", 600, 750, 200, 0.2, mv="wig", c="blue"), ic(7.5, "rocket", 1350, 750, 200, 0.3, mv="wig"))
bd(8, big(8, 960, 250, "反转一", c="red", d=0.0, s=140), ic(8, "fire" if False else "flame", 650, 650, 240, 0.1, mv="wig", c="red"), cross(8, 650, 650, d=0.4), t(8, 1300, 650, 80, "摩擦？", c="ink", d=0.2))
bd(8.5, [ic(8.5, "hand" if False else "gear", 600 + 180 * q, 600, 140, 0.1 * q, mv="spin") for q in range(2)], cross(8.5, 690, 600, d=0.3), check(8.5, 1350, 600, d=0.4), t(8.5, 1350, 850, 64, "另有原因", c="blue", d=0.3))
bd(9, blaze(9, 1350, 550, 1.2, 0.0, tail=False, dx=-60, dy=0, dur=2.5), dots(9, 500, 450, 12, "blue", 0.1, squeeze=200), arr(9, 1150, 550, 950, 550, c="red", d=0.3))
bd(9.5, blaze(9.5, 1400, 550, 1.2, 0.0, tail=False), dots(9.5, 900, 470, 8, "red", 0.1), t(9.5, 700, 300, 70, "越挤越紧", c="red", d=0.3), arr(9.5, 650, 550, 850, 550, c="ink", d=0.4))
bd(10, pump(10, 700, 700, 0.0), man(10, 1200, 960, 1.3, 0.1, arms="up", amp=6), t(10, 1450, 400, 70, "打气筒", c="blue", d=0.2))
bd(10.5, pump(10.5, 700, 700, 0.0), ic(10.5, "thermometer", 1150, 600, 260, 0.2, mv="wig", c="red"), bar(10.5, 1500, 900, 100, 500, "red", 0.3, 1.2), big(10.5, 1500, 300, "烫", c="red", d=0.5, s=130))
bd(11, big(11, 960, 300, "几千度", c="red", d=0.0, s=170), dots(11, 450, 650, 8, "red", 0.2), ic(11, "thermometer", 1450, 650, 240, 0.3, mv="wig", c="red"))
bd(11.5, blaze(11.5, 960, 600, 1.6, 0.0, mood="o", tail=False), [flame(11.5, 650 + 150 * q, 430, 100, 0.1 + 0.06 * q, c="gold") for q in range(5)], bubbles(11.5, 960, 500, 5, 0.3, 300, "red"))
bd(12, blaze(12, 1100, 550, 1.4, 0.0), [O(12, 700 + 60 * q, 450 + 50 * (q % 3), 25, c="gold", fill="gold", idp=f"gl{q}") for q in range(6)], [pop(12, f"gl{q}", 0.2 + 0.05 * q) for q in range(6)], [wig(12, f"gl{q}", (850, 500), 8, 3) for q in range(6)])
bd(12.5, sky(12.5), streak(12.5, 1600, 150, 800, 700, "gold", 0.0, 12), blaze(12.5, 800, 700, 0.8, 0.1), big(12.5, 600, 280, "流星", c="red", d=0.3, s=150))
bd(13, big(13, 960, 250, "反转二", c="red", d=0.0, s=140), blaze(13, 700, 650, 1.2, 0.1), ic(13, "question", 1300, 650, 220, 0.2, mv="wig", c="green"))
bd(13.5, ic(13.5, "atom", 600, 550, 260, 0.0, mv="spin", c="blue"), ic(13.5, "magnifier", 1300, 550, 240, 0.2, mv="wig"), t(13.5, 960, 880, 80, "原子的指纹", c="green", d=0.3))
bd(14, ic(14, "atom", 500, 550, 220, 0.0, mv="spin", c="red"), flame(14, 500, 830, 120, 0.1), arr(14, 700, 550, 1000, 550, c="ink", d=0.3), bars(14, 1100, 420, ["green", "green", "blue"], 0.4))
bd(14.5, [ic(14.5, "atom", 450 + 500 * q, 450, 170, 0.1 * q, mv="spin", c=c) for q, c in enumerate(["gold", "red", "green"])],
   [bars(14.5, 380 + 500 * q, 650, [c, c], 0.3 + 0.1 * q) for q, c in enumerate(["gold", "red", "green"])])
bd(15, firework(15, 600, 500, "gold", 0.0), firework(15, 1300, 450, "red", 0.3), man(15, 960, 980, 1.0, 0.2, arms="up", amp=8))
bd(15.5, firework(15.5, 600, 450, "gold", 0.0), t(15.5, 600, 750, 70, "钠 = 黄", c="gold", d=0.2), firework(15.5, 1350, 450, "red", 0.3), t(15.5, 1350, 750, 70, "锶 = 红", c="red", d=0.4))
bd(16, blaze(16, 600, 600, 1.4, 0.0), t(16, 1300, 400, 80, "镁 · 镍", c="green", d=0.2), ic(16, "atom", 1300, 700, 200, 0.3, mv="spin", c="green"))
bd(16.5, t(16.5, 600, 400, 80, "氧", c="green", d=0.0), dots(16.5, 450, 550, 8, "green", 0.1), streak(16.5, 1700, 200, 1100, 800, "green", 0.3, 16), t(16.5, 1300, 950, 56, "常见解释", c="muted", d=0.4))
bd(17, ic(17, "atom", 600, 500, 220, 0.0, mv="spin", c="gold"), t(17, 600, 800, 70, "钠 → 黄", c="gold", d=0.2), ic(17, "wind", 1300, 500, 220, 0.2, mv="wig", c="red"), t(17, 1300, 800, 70, "氮 · 氧 → 红", c="red", d=0.4))
bd(17.5, sky(17.5), streak(17.5, 1500, 150, 900, 700, "red", 0.0, 20), streak(17.5, 1530, 170, 930, 720, "gold", 0.1, 12), streak(17.5, 1560, 190, 960, 740, "green", 0.2, 8), t(17.5, 500, 300, 70, "三种颜色", c="blue", d=0.3))
bd(18, bars(18, 500, 400, ["green", "gold", "red", "green", "red"], 0.0), ic(18, "flask", 1350, 550, 240, 0.2, mv="wig", c="blue"))
bd(18.5, R(18.5, 600, 300, 700, 500, c="ink", fill="paper", idp="tab18"), pop(18.5, "tab18", 0.0), wig(18.5, "tab18", (950, 800), 1, 1), t(18.5, 950, 400, 64, "成分表", c="blue", d=0.1),
   [t(18.5, 800 + 150 * q, 600, 56, n, c=c, d=0.2 + 0.1 * q) for q, (n, c) in enumerate([("镁", "green"), ("钠", "gold"), ("氧", "red")])], blaze(18.5, 1600, 700, 0.7, 0.4))
bd(19, big(19, 960, 250, "反转三", c="red", d=0.0, s=140), [ic(19, "map_pin", 500 + 460 * q, 650, 180, 0.1 + 0.1 * q, mv="bob", c=["blue", "green", "gold"][q]) for q in range(3)])
bd(19.5, [man(19.5, 450 + 500 * q, 960, 1.0, 0.1 * q, arms="up", amp=6) for q in range(3)], blaze(19.5, 960, 300, 1.0, 0.2), [arr(19.5, 450 + 500 * q, 650, 900 + 60 * q, 380, c="muted", d=0.3 + 0.08 * q) for q in range(3)])
bd(20, P(20, "M200,950 L1700,950", c="ink", w=6, idp="gd20"), pop(20, "gd20", 0.0), ic(20, "rocket" if False else "satellite", 400, 820, 120, 0.1, mv="bob"), t(20, 600, 820, 50, "飞机 10 公里", d=0.2),
   blaze(20, 1300, 250, 1.0, 0.2), big(20, 1300, 550, "70+ 公里", c="red", d=0.3, s=110), arr(20, 1000, 900, 1000, 300, c="red", d=0.4))
bd(20.5, bar(20.5, 600, 950, 160, 70, "blue", 0.0), t(20.5, 680, 1010, 40, "飞机", d=0.0), bar(20.5, 1000, 950, 160, 700, "red", 0.2, 1.2), t(20.5, 1080, 1010, 40, "流星", d=0.2), big(20.5, 1500, 400, "× 10", c="red", d=0.4, s=140))
bd(21, ic(21, "building", 700, 650, 360, 0.0, mv="bob"), man(21, 700, 450, 0.7, 0.1, arms="up", amp=6), [arr(21, 800, 400, 1300 + 100 * q, 500 + 150 * q, c="blue", d=0.2 + 0.08 * q) for q in range(3)])
bd(21.5, earth(21.5, 960, 900, 600, 0.0), blaze(21.5, 960, 280, 0.8, 0.1), [arr(21.5, 960, 340, 600 + 200 * q, 700, c="gold", d=0.2 + 0.06 * q) for q in range(5)])
bd(22, ic(22, "map_pin", 600, 450, 200, 0.0, mv="bob", c="blue"), t(22, 600, 650, 64, "北京", d=0.1), ic(22, "map_pin", 1350, 650, 200, 0.2, mv="bob", c="red"), t(22, 1350, 850, 64, "阳泉", d=0.3),
   ic(22, "satellite", 1600, 350, 140, 0.3, mv="bob"))
bd(22.5, ic(22.5, "map_pin", 450, 600, 160, 0.0, mv="bob", c="blue"), ic(22.5, "map_pin", 1450, 600, 160, 0.1, mv="bob", c="red"), arr(22.5, 550, 650, 1350, 650, c="ink", d=0.2, dur=1.0),
   big(22.5, 960, 400, "≈ 300 公里", c="red", d=0.4, s=120), t(22.5, 960, 850, 50, "我们的估算", c="muted", d=0.5))
bd(23, ic(23, "star" if False else "moon", 500, 500, 200, 0.0, mv="bob", c="gold"), t(23, 500, 750, 64, "金星", c="gold", d=0.1), blaze(23, 1300, 500, 1.2, 0.2), t(23, 960, 500, 90, "<", c="red", d=0.3))
bd(23.5, big(23.5, 960, 350, "火流星", c="red", d=0.0, s=170), [flame(23.5, 650 + 200 * q, 750, 120, 0.2 + 0.06 * q, c=["red", "gold", "green", "red"][q]) for q in range(4)])
bd(24, blaze(24, 700, 550, 2.0, 0.0), t(24, 1400, 450, 64, "“比较大个儿”", c="blue", d=0.2), man(24, 1400, 950, 1.2, 0.3))
bd(24.5, ic(24.5, "question", 600, 500, 200, 0.0, mv="wig", c="red"), [O(24.5, 1100 + 120 * q, 700 + 30 * (q % 2), 30 + 6 * q, c="ink", fill="muted", idp=f"rk{q}") for q in range(4)],
   [pop(24.5, f"rk{q}", 0.2 + 0.07 * q) for q in range(4)], [wig(24.5, f"rk{q}", (1300, 720), 3, 2) for q in range(4)], t(24.5, 1300, 450, 70, "陨石？", c="red", d=0.3))
bd(25, blaze(25, 960, 450, 1.6, 0.0, mood="sad"), [flame(25, 700 + 130 * q, 650, 90, 0.1 + 0.06 * q) for q in range(5)], t(25, 960, 900, 64, "大部分烧光", c="red", d=0.4))
bd(25.5, P(25.5, "M200,900 L1700,900", c="ink", w=6, idp="gd25"), pop(25.5, "gd25", 0.0), ball(25.5, 960, 200, 0, 680, 0.1, c="muted", dur=1.4, r=30), t(25.5, 960, 1000, 64, "陨石", c="blue", d=0.4), check(25.5, 1300, 850, d=0.6))
bd(26, blaze(26, 1500, 200, 0.8, 0.0, dx=-500, dy=250, dur=1.5), ball(26, 960, 500, 0, 380, 0.6, c="muted", dur=1.5, r=26), t(26, 500, 400, 70, "不亮了", c="ink", d=0.3), arr(26, 1300, 300, 1300, 800, c="blue", d=0.4))
bd(26.5, ic(26.5, "wind", 600, 500, 220, 0.0, mv="wig", c="blue"), ball(26.5, 1200, 300, 0, 500, 0.1, c="muted", dur=2.5, r=30), t(26.5, 600, 800, 64, "空气刹车", c="blue", d=0.3), ic(26.5, "clock", 1550, 700, 140, 0.3, mv="spin"))
bd(27, earth(27, 960, 650, 400, 0.0), [ball(27, 400 + 280 * q, 200, 120, 200, 0.1 + 0.08 * q, c="gold", dur=1.2, r=10) for q in range(5)], ic(27, "question", 1600, 400, 160, 0.3, mv="wig", c="red"))
bd(27.5, big(27.5, 960, 330, "几十吨 / 天", c="red", d=0.0, s=150), [R(27.5, 600 + 150 * q, 650, 120, 120, c="ink", fill="muted", idp=f"tn{q}") for q in range(5)],
   [pop(27.5, f"tn{q}", 0.2 + 0.07 * q) for q in range(5)], [wig(27.5, f"tn{q}", (900, 760), 2, 1.5) for q in range(5)], t(27.5, 960, 900, 50, "常见估计", c="muted", d=0.5))
bd(28, [O(28, 400 + 100 * q, 500 + 80 * (q % 3), 6, c="ink", fill="ink", idp=f"sd{q}") for q in range(12)], [pop(28, f"sd{q}", 0.03 * q) for q in range(12)],
   [wig(28, f"sd{q}", (900, 600), 10, 2) for q in range(12)], t(28, 960, 850, 70, "比沙粒还小", d=0.3))
bd(28.5, ic(28.5, "eye", 700, 550, 260, 0.0, mv="wig"), cross(28.5, 700, 550, d=0.3), ic(28.5, "magnifier", 1300, 550, 220, 0.2, mv="wig"), t(28.5, 960, 880, 64, "根本看不见", c="red", d=0.4))
bd(29, big(29, 960, 250, "友情提示", c="blue", d=0.0, s=130), ic(29, "magnifier", 650, 650, 220, 0.1, mv="wig"), ic(29, "question", 1300, 650, 220, 0.2, mv="wig", c="red"))
bd(29.5, big(29.5, 960, 350, "可能 ≠ 一定", c="red", d=0.0, s=150), blaze(29.5, 960, 750, 0.8, 0.2, mood="o"), man(29.5, 450, 950, 1.1, 0.3), man(29.5, 1470, 950, 1.1, 0.4))
bd(30, O(30, 960, 600, 100, c="ink", fill="muted", idp="rk30"), pop(30, "rk30", 0.0), wig(30, "rk30", (960, 650), 4, 2), man(30, 600, 950, 1.3, 0.1, arms="up", amp=6), ic(30, "question", 1350, 500, 200, 0.2, mv="wig", c="red"))
bd(30.5, ic(30.5, "phone", 500, 550, 220, 0.0, mv="wig"), ic(30.5, "map_pin", 960, 550, 200, 0.2, mv="bob", c="red"), ic(30.5, "building", 1450, 550, 220, 0.3, mv="bob"),
   arr(30.5, 650, 550, 830, 550, c="ink", d=0.3), arr(30.5, 1100, 550, 1300, 550, c="ink", d=0.4), t(30.5, 1450, 850, 56, "天文馆", c="blue", d=0.5))
bd(31, ic(31, "building", 500, 700, 300, 0.0, mv="bob"), cross(31, 500, 700, d=0.3), ic(31, "moon", 1300, 400, 180, 0.2, mv="bob", c="gold"), t(31, 1300, 700, 64, "远离灯光", c="blue", d=0.3))
bd(31.5, sky(31.5), man(31.5, 700, 960, 1.4, 0.0, arms="up", amp=4), [star(31.5, 500 + 220 * q, 250 + 80 * (q % 2), 0.1 * q, r=25) for q in range(6)], streak(31.5, 1600, 200, 1300, 450, "green", 0.6), ic(31.5, "clock", 1450, 750, 140, 0.3, mv="spin"))
bd(32, blaze(32, 960, 550, 1.8, 0.0), ic(32, "question", 1500, 400, 180, 0.2, mv="wig", c="red"), t(32, 960, 920, 64, "凭什么这么亮？", d=0.3))
bd(32.5, blaze(32.5, 1350, 550, 1.2, 0.0, tail=False), dots(32.5, 800, 470, 8, "red", 0.1, squeeze=120), ic(32.5, "thermometer", 450, 550, 220, 0.3, mv="wig", c="red"), check(32.5, 960, 850, d=0.5))
bd(33, streak(33, 1500, 200, 900, 700, "green", 0.0, 16), ic(33, "question", 500, 500, 200, 0.1, mv="wig", c="green"), blaze(33, 900, 700, 0.8, 0.2))
bd(33.5, [ic(33.5, "atom", 450 + 340 * q, 550, 170, 0.08 * q, mv="spin", c=c) for q, c in enumerate(["green", "gold", "red", "green"])], ic(33.5, "speaker", 1600, 850, 140, 0.4, mv="wig"),
   t(33.5, 960, 850, 64, "报名字", c="green", d=0.4))
bd(34, blaze(34, 960, 550, 1.6, 0.0, tail=False, dx=0, dy=-30, dur=2.5), [star(34, 400 + 230 * q, 250 + 120 * (q % 3), 0.05 * q, r=25) for q in range(6)], big(34, 960, 880, "几十亿年", c="blue", d=0.3, s=110))
bd(34.5, sky(34.5), firework(34.5, 500, 400, "green", 0.0), firework(34.5, 960, 300, "gold", 0.2), firework(34.5, 1420, 400, "red", 0.4), big(34.5, 960, 700, "最后 5 秒", c="red", d=0.5, s=110))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"18:30": "六点半"})
