"""每日热点科普 2026-10-22（中文）：《一个小插头，凭什么烧掉显卡？》
热榜：新浪数码热点小时报 2026-10-22 18时 第 1 条“两天收到 7 张烧毁的 NVIDIA 显卡（5090/4090），12+4 针供电口烧毁”
（k.sina.com.cn/article_7857201856_1d45362c001908s0p2.html）；同类事件持续上热搜（快科技、什么值得买、电子工程专辑）。
事实：腾讯新闻 2026-09-03（news.qq.com/rain/a/20260903A05NXW00）：Hardware Unboxed 的 RTX 5090 16 针接口超过 150℃、满载 175℃（热成像），
各线电流严重不均，有的几乎为 0，有的高达 22A，超过规范最大 9.2A 两倍多；电源侧线与接口熔在一起要用钳子取。
RTX 5090 整卡功耗 575 W（英伟达规格）；12V-2x6 接口 6 根 12 V 针。575/12 ≈ 48 A，平均每针约 8 A；6×9.2 = 55 A，余量约 15%（估算）。
老式 PCIe 8 针（150 W）余量常被估算为接近一倍（估算，片中说“据估算”）。物理：发热 P = I²R；并联支路电流往电阻小的挤；热—接触变差—更热（正反馈）。
华硕 ROG Astral（夜神）等高端卡有逐针电流监测（厂商宣传）。根本原因未定论，片中说清。角色：小卡（显卡，胃口大，怕上火）。没有手。
    python3 make.py <kokoro 模型目录> | --boards-only   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("两天，七张显卡送进维修店，|供电插头全烧了。", "Two days, seven graphics cards at one repair shop, | every power plug burned."),
 ("每一张都是上万块的高端卡，|烧的却是一个小小的插头。", "Each one a top-end card worth thousands, | and what burned was a tiny plug."),
 ("今天的问题：一个小插头，|凭什么烧掉一张显卡？", "Today's question: how does one little plug | take down a whole graphics card?"),
 ("认识一下小卡。|小卡是一张显卡，胃口特别大。", "Meet Xiaoka. | Xiaoka is a graphics card with a huge appetite."),
 ("RTX 5090 满载的时候，|一张卡要吃掉575瓦。", "At full load, an RTX 5090 | eats 575 watts."),
 ("可显卡只吃12伏的低压电。|电压低，电流就得大。", "But it only eats 12-volt power. | Low voltage means high current."),
 ("575除以12，|差不多就是48安。", "575 divided by 12 | is about 48 amps."),
 ("家里两千瓦的电水壶，也就九安左右。|小卡要它的五倍多。", "A 2,000-watt kettle at home draws about 9 amps. | Xiaoka wants over five times that."),
 ("这48安，全从一个插头过去，|插头里只有六根细细的针。", "All 48 amps squeeze through one plug, | through just six thin pins."),
 ("平均下来，|一根针扛8安。", "On average, | each pin carries 8 amps."),
 ("规范说，一根针最多|能扛9.2安左右。", "The spec says each pin can handle | about 9.2 amps at most."),
 ("反转一：算一算，|余量只有一成多。", "Twist one: do the math, | the safety margin is only about 15 percent."),
 ("据估算，老式8针插头的余量|接近一倍。", "By common estimates, the old 8-pin plug | had nearly double."),
 ("可平均8安不到上限啊，|怎么还会烧？", "But 8 amps is under the limit. | So why does it burn?"),
 ("想象六个人，|一起抬一架钢琴。", "Picture six people | carrying one piano."),
 ("要是有两个人手一松，|重量就全压到别人身上。", "If two of them loosen their grip, | the weight lands on everyone else."),
 ("电流也一样：六根针并排走，|哪根接触好，电就往哪根挤。", "Current is the same: six pins side by side, | and it crowds into whichever pin touches best."),
 ("插头没插到底、针脚松一点，|接触就变差。", "A plug not pushed all the way in, a loose pin, | and the contact gets worse."),
 ("反转二：硬件媒体实测，|有的线几乎没有电流。", "Twist two: when reviewers measured it, | some wires carried almost nothing."),
 ("而有一根，|高达22安！", "And one wire | carried 22 amps!"),
 ("比规范的上限，|高出两倍多。", "That's more than double | the spec limit."),
 ("反转三，最反直觉：电流翻一倍，|发热翻四倍。", "Twist three, the weird part: double the current, | and you get four times the heat."),
 ("因为发热等于电流的平方|再乘电阻。", "Because heat equals current squared | times resistance."),
 ("22安只是8安的不到三倍，|发热却是七倍多。", "22 amps is less than three times 8, | but the heat is over seven times."),
 ("更糟的是：热了，接触更差；|接触差了，又更热。", "Worse: heat makes the contact worse, | and worse contact makes more heat."),
 ("一圈一圈往上滚，|就像滚雪球。", "Round and round it climbs, | like a snowball rolling downhill."),
 ("热像仪一拍，|插头烫到175度。", "The thermal camera says | the plug hit 175 degrees Celsius."),
 ("塑料外壳就这样化了，|线和插头熔成一坨。", "The plastic melts, | and cable and plug fuse into one lump."),
 ("怎么防？第一，插到底，|听见咔哒一声。", "How to prevent it? First, push it all the way in | until it clicks."),
 ("第二，线别贴着插头|硬弯。", "Second, don't bend the cable sharply | right at the plug."),
 ("第三，有的高端卡会逐根测电流，|不均就报警。", "Third, some high-end cards measure each wire | and warn you when they're uneven."),
 ("友情提示：每张卡到底为什么烧，|厂商还没有定论。", "Friendly fine print: why each card burned | hasn't been settled by the makers."),
 ("我们讲的只是物理：余量小、电流不均，|发热按平方往上涨。", "This is just the physics: thin margins, uneven current, | and heat that grows with the square."),
 ("小卡的新年愿望：|少吃一点，别上火。", "Xiaoka's new year's wish: | eat a little less, and keep cool."),
]
TITLE = {"zh": "一个小插头，凭什么烧掉显卡？", "en": "How Does One Little Plug Burn a Graphics Card?"}

B = []


def bd(a, *parts, n=2):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    if n > 2:
        E += star(a, 1810, 900, 0.5, r=20)
    B.append(E)


def xiaoka(a, x, y, k=1.0, mood="happy", sweat=False):
    """小卡：一张有脸的显卡，两个风扇是眼睛（风扇一直转），整只一直上下飘。"""
    i = uid("ka") + "_"
    E = [R(a, x - 150 * k, y - 95 * k, 300 * k, 190 * k, c="ink", fill="muted", idp=i)]
    for q, fx in enumerate((x - 75 * k, x + 75 * k)):
        fan = i + "f" + str(q)
        E += [O(a, fx, y - 20 * k, 52 * k, c="blue", idp=i), P(a, f"M{fx - 45 * k},{y - 20 * k} L{fx + 45 * k},{y - 20 * k} M{fx},{y - 65 * k} L{fx},{y + 25 * k}",
                                                             c="blue", w=4, idp=fan), spin(a, fan, (fx, y - 20 * k), 160),
              O(a, fx, y - 20 * k, 13 * k, c="ink", fill="ink", idp=i)]
    for q in range(6):
        E.append(R(a, x - 110 * k + q * 38 * k, y + 95 * k, 22 * k, 26 * k, c="gold", fill="gold", idp=i))
    m = {"happy": f"M{x - 30 * k},{y + 45 * k} Q{x},{y + 72 * k} {x + 30 * k},{y + 45 * k}",
         "sad": f"M{x - 30 * k},{y + 65 * k} Q{x},{y + 40 * k} {x + 30 * k},{y + 65 * k}",
         "o": f"M{x - 14 * k},{y + 55 * k} a14,14 0 1,0 28,0 a14,14 0 1,0 -28,0"}[mood]
    E.append(P(a, m, c="ink", w=5, idp=i))
    if sweat:
        sw = uid("sw")
        E += [P(a, f"M{x + 165 * k},{y - 90 * k} Q{x + 190 * k},{y - 45 * k} {x + 165 * k},{y - 35 * k} Q{x + 140 * k},{y - 45 * k} {x + 165 * k},{y - 90 * k}",
                c="blue", w=4, fill="blue", idp=sw), sh(a, sw, 0, 60, 0.3, 0.8)]
    E += [bob(a, i, 8 * k, 1.3), wig(a, i, (x, y + 95 * k), 4, 1.1)]
    return E, i


def plug(a, x, y, k=1.0, hot=(), d=0.0, c="ink"):
    """供电插头：外壳 + 六根针（hot 里的针画成红色并一直抖）。"""
    i = uid("pl")
    E = [R(a, x - 160 * k, y - 80 * k, 320 * k, 160 * k, c=c, idp=i), pop(a, i, d)]
    for q in range(6):
        pi = uid("pin")
        h = q in hot
        E += [R(a, x - 135 * k + q * 48 * k, y - 45 * k, 30 * k, 90 * k, c="red" if h else "gold", fill="red" if h else "gold", idp=pi), pop(a, pi, d + 0.05 * q)]
        E.append(wig(a, pi, (x - 120 * k + q * 48 * k, y + 45 * k), 6 if h else 2, 3.0 if h else 1.0))
    E.append(bob(a, i, 4, 0.9))
    return E


def wires(a, x0, x1, y0, gap=55, amps=(8, 8, 8, 8, 8, 8), d=0.0):
    """六根并排的线，线上的小点按电流大小跑（点越多越快 = 电流越大）。"""
    E = []
    for q, A in enumerate(amps):
        y = y0 + q * gap
        w = uid("w")
        E += [P(a, f"M{x0},{y} L{x1},{y}", c="red" if A > 12 else ("muted" if A < 2 else "ink"), w=4 + A / 4, idp=w), wig(a, w, (x0, y), 1, 1.5)]
        for j in range(min(4, int(A / 5) + (1 if A >= 2 else 0))):
            dt = uid("e")
            E += [O(a, x0 + 20, y, 9, c="blue", fill="blue", idp=dt), sh(a, dt, x1 - x0 - 40, 0, d + 0.25 * j, max(0.4, 3.0 - A / 10))]
    return E


def thermo(a, x, y, frm=0.2, to=0.9, d=0.2, c="red"):
    i, liq = uid("th"), uid("liq")
    return [R(a, x - 35, y - 300, 70, 330, c="ink", idp=i), O(a, x, y + 60, 55, c=c, fill=c, idp=i),
            R(a, x - 18, y - 270, 36, 300, c=c, fill=c, idp=liq),
            {"t": "move", "at": a, "kind": "grow", "targets": [liq], "axis": "y", "from": frm, "to": to, "pivot": [x, y + 30], "dur": 1.0, "delay": d},
            bob(a, i, 3, 0.8), pop(a, i, 0.0)]


def flame(a, x, y, s=160, d=0.0, c="red"):
    i = uid("fl")
    return [{"t": "icon", "at": a, "id": i, "name": "flame", "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), wig(a, i, (x, y + s / 2), 8, 3.0)]


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def person(a, x, y, k=1.0, c="ink", slack=False):
    i = uid("ps")
    arm = f"M{x - 60 * k},{y - 100 * k} L{x},{y - 40 * k} L{x + 60 * k},{y - 100 * k}" if not slack else f"M{x - 50 * k},{y + 20 * k} L{x},{y - 40 * k} L{x + 50 * k},{y + 20 * k}"
    return [O(a, x, y - 130 * k, 40 * k, c=c, idp=i), P(a, f"M{x},{y - 90 * k} L{x},{y + 40 * k} {arm.replace('M', 'M', 1)} M{x},{y + 40 * k} L{x - 40 * k},{y + 130 * k} "
                                                         f"M{x},{y + 40 * k} L{x + 40 * k},{y + 130 * k}", c=c, w=6, idp=i),
            bob(a, i, 5, 1.0 + 0.07 * (int(x) % 7)), wig(a, i, (x, y + 130 * k), 4, 1.2)]


def piano(a, x, y, w=600, d=0.0, tilt=0):
    i = uid("pn")
    E = [R(a, x - w / 2, y - 90, w, 90, c="ink", fill="ink", idp=i)]
    for q in range(9):
        E.append(R(a, x - w / 2 + 20 + q * (w - 40) / 9, y - 60, (w - 40) / 9 - 8, 50, c="ink", fill="muted", idp=i))
    E += [pop(a, i, d), bob(a, i, 4, 0.8)]
    if tilt:
        E.append(rot(a, i, tilt, (x, y), d + 0.5, 0.5))
    return E, i


def kettle(a, x, y, d=0.0):
    i = uid("kt")
    st = uid("st")
    return [P(a, f"M{x - 110},{y + 120} L{x - 90},{y - 80} Q{x},{y - 130} {x + 90},{y - 80} L{x + 110},{y + 120} Z M{x + 90},{y - 40} L{x + 170},{y - 100}", c="ink", w=6,
              fill="muted", idp=i), pop(a, i, d), wig(a, i, (x, y + 120), 3, 2.0),
            P(a, f"M{x + 170},{y - 120} q20,-30 0,-60 q-20,-30 0,-60", c="blue", w=5, idp=st), pop(a, st, d + 0.3), sh(a, st, 0, -60, d + 0.4, 1.0)]


def snowball(a, x, y, d=0.0):
    i = uid("sb")
    return [O(a, x, y, 50, c="blue", idp=i), pop(a, i, d), sh(a, i, 700, 260, d + 0.2, 1.4), rot(a, i, 540, (x, y), d + 0.2, 1.4),
            {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "both", "from": 0.6, "to": 2.4, "pivot": [x, y], "dur": 1.4, "delay": d + 0.2}]


def loop_arrows(a, x, y, r=170, d=0.0):
    i = uid("lp")
    return [P(a, f"M{x + r},{y} A{r},{r} 0 1,1 {x},{y - r} M{x - 25},{y - r - 25} L{x},{y - r} L{x - 25},{y - r + 25}", c="red", w=7, idp=i), pop(a, i, d),
            spin(a, i, (x, y), 45)]


# 0 两天七张显卡
E = []
for q in range(7):
    k_, ki = xiaoka(0, 300 + 220 * (q % 7), 560 + 70 * (q % 2), 0.55, mood="o")
    E += k_ + [pop(0, ki + "*", 0.08 * q)]
bd(0, E, BIG(0, 960, 250, "2 天 · 7 张", c="red", d=0.4, s=130))
# 0.5 插头全烧了
bd(0.5, plug(0.5, 700, 540, 1.4, hot=range(6)), flame(0.5, 640, 260, 200, 0.2), flame(0.5, 860, 300, 140, 0.4), BIG(0.5, 1450, 560, "全烧了", c="red", d=0.4, s=140))
# 1 上万块高端卡
k_, ki = xiaoka(1, 650, 560, 1.6)
bd(1, k_, BIG(1, 1400, 480, "¥10000+", c="gold", d=0.3, s=130), [e for q in range(3) for e in star(1, 1200 + 180 * q, 700, 0.5 + 0.15 * q, r=40)])
# 1.5 烧的却是小插头
bd(1.5, plug(1.5, 960, 560, 0.7, hot=(2, 3)), [e for q in range(2) for e in arr(1.5, 600 + 720 * q, 300, 820 + 280 * q, 480, c="red", d=0.2 + 0.2 * q)],
   flame(1.5, 960, 330, 120, 0.5), T(1.5, 960, 840, 64, "一个小小的插头", c="red", d=0.4))
# 2 问题
bd(2, plug(2, 600, 540, 1.0, hot=(1,)), icon(2, "question", 1150, 320, 260, 0.3, c="red", mv="wig"), T(2, 1300, 760, 60, "一个小插头……", c="ink", d=0.2))
# 2.5 凭什么烧掉显卡
k_, ki = xiaoka(2.5, 1350, 560, 1.2, mood="o", sweat=True)
bd(2.5, plug(2.5, 500, 560, 0.8, hot=(0, 5)), arr(2.5, 700, 560, 1100, 560, c="red", d=0.3), k_, flame(2.5, 1350, 260, 140, 0.6),
   T(2.5, 960, 880, 60, "凭什么烧掉显卡？", c="red", d=0.5))
# 3 认识小卡
k_, ki = xiaoka(3, 900, 560, 2.0)
bd(3, k_, [pop(3, ki + "*", 0.0)], BIG(3, 1550, 360, "小卡", c="blue", d=0.4, s=140), star(3, 400, 300, 0.6, r=40), n=3)
# 3.5 胃口特别大
k_, ki = xiaoka(3.5, 700, 560, 1.5, mood="o")
E = []
for q in range(5):
    i = uid("bolt")
    E += [P(3.5, f"M{1600},{300 + 90 * q} l-40,40 l30,0 l-40,50", c="gold", w=7, idp=i), pop(3.5, i, 0.05 * q), sh(3.5, i, -720, 260 - 90 * q, 0.3 + 0.15 * q, 0.5)]
bd(3.5, k_, E, T(3.5, 1300, 880, 64, "胃口特别大", c="red", d=0.3))
# 4 RTX 5090 满载
k_, ki = xiaoka(4, 650, 560, 1.4)
bd(4, k_, T(4, 1350, 380, 80, "RTX 5090", c="ink", d=0.1), [wig(4, ki + "*", (650, 720), 6, 4.0)], bar(4, 1250, 820, 200, 300, "red", d=0.3, dur=0.8),
   T(4, 1350, 880, 48, "满载", c="red", d=0.4))
# 4.5 575 瓦
bd(4.5, BIG(4.5, 960, 480, "575 瓦", c="red", d=0.1, s=170), [e for q in range(4) for e in icon(4.5, "sun", 360 + 400 * q, 820, 120, 0.2 * q, c="gold", mv="spin")])
# 5 12 伏
bd(5, icon(5, "battery", 600, 520, 300, 0.0, c="green"), BIG(5, 1300, 480, "12 伏", c="green", d=0.3, s=150), T(5, 1300, 700, 52, "低压电", c="muted", d=0.5))
# 5.5 电压低 电流大
bd(5.5, bar(5.5, 560, 820, 200, 160, "green", d=0.1), T(5.5, 660, 880, 48, "电压", c="green"), bar(5.5, 1160, 820, 200, 520, "red", d=0.4, dur=1.0),
   T(5.5, 1260, 880, 48, "电流", c="red"), arr(5.5, 820, 600, 1100, 450, c="ink", d=0.3))
# 6 575 / 12
bd(6, BIG(6, 700, 480, "575 ÷ 12", c="ink", d=0.1, s=140), [e for q in range(3) for e in icon(6, "gear", 1350 + 170 * q, 480, 130, 0.2 + 0.1 * q, mv="spin")])
# 6.5 48 安
bd(6.5, BIG(6.5, 960, 470, "≈ 48 安", c="red", d=0.1, s=180), wires(6.5, 300, 1620, 720, gap=40, amps=(8,) * 6, d=0.2))
# 7 电水壶 9 安
bd(7, kettle(7, 600, 560), BIG(7, 1300, 450, "≈ 9 安", c="blue", d=0.3, s=140), T(7, 1300, 650, 48, "2000 瓦电水壶", c="muted", d=0.4))
# 7.5 五倍多
E = []
for q in range(5):
    E += kettle(7.5, 300 + 230 * q, 560, d=0.1 * q)
k_, ki = xiaoka(7.5, 1550, 560, 0.9, mood="happy")
bd(7.5, E, k_, BIG(7.5, 960, 880, "× 5 还多", c="red", d=0.5, s=110))
# 8 48 安过一个插头
bd(8, wires(8, 200, 900, 380, gap=60, amps=(8,) * 6, d=0.1), plug(8, 1200, 530, 1.2), arr(8, 920, 530, 1020, 530, c="red", d=0.3),
   BIG(8, 1200, 820, "48 安", c="red", d=0.3, s=100))
# 8.5 六根针
bd(8.5, plug(8.5, 960, 520, 2.2), T(8.5, 960, 860, 64, "只有六根细针", c="ink", d=0.4))
# 9 平均
bd(9, wires(9, 300, 1500, 300, gap=80, amps=(8,) * 6, d=0.0), T(9, 960, 860, 56, "平均分", c="ink", d=0.3), check(9, 1650, 500, d=0.6))
# 9.5 一根 8 安
bd(9.5, plug(9.5, 600, 540, 1.2), arr(9.5, 820, 500, 1100, 480, c="ink", d=0.3), BIG(9.5, 1400, 500, "8 安/根", c="blue", d=0.3, s=130))
# 10 规范
pg = uid("pg")
bd(10, [R(10, 600, 260, 420, 540, c="ink", idp=pg), P(10, "M660,380 L960,380 M660,460 L960,460 M660,540 L900,540", c="muted", w=6, idp=pg), pop(10, pg, 0.0),
        rot(10, pg, -5, (810, 800), 0.4, 0.4), bob(10, pg, 4, 0.9)], icon(10, "magnifier", 1300, 420, 220, 0.3, mv="wig"), T(10, 1350, 760, 56, "规范", c="ink", d=0.2))
# 10.5 9.2 安
bd(10.5, bar(10.5, 600, 820, 220, 480, "green", d=0.1), T(10.5, 710, 880, 44, "上限"), bar(10.5, 900, 820, 220, 420, "blue", d=0.3), T(10.5, 1010, 880, 44, "平均"),
   BIG(10.5, 1450, 420, "9.2 安", c="green", d=0.4, s=130), T(10.5, 1450, 600, 48, "8 安", c="blue", d=0.6))
# 11 反转一
bd(11, BIG(11, 960, 160, "反转一", c="red", d=0.1, s=90), BIG(11, 960, 450, "6 × 9.2 = 55", c="ink", d=0.3, s=110), BIG(11, 960, 650, "需要 48", c="red", d=0.6, s=90),
   icon(11, "gear", 300, 800, 140, 0.2, mv="spin"), icon(11, "gear", 1620, 800, 140, 0.3, mv="spin"))
# 11.5 余量一成多
bd(11.5, bar(11.5, 700, 820, 240, 500, "red", d=0.1), bar(11.5, 700, 320, 240, 70, "green", d=0.6, dur=0.4), T(11.5, 820, 880, 44, "能扛的"),
   BIG(11.5, 1400, 480, "余量 ≈ 15%", c="red", d=0.6, s=110), [pulse(11.5, uid("x"), 0.0)][:0], icon(11.5, "thermometer", 1400, 760, 140, 0.8, c="red", mv="wig"))
# 12 据估算 老式8针
bd(12, plug(12, 650, 520, 1.0), T(12, 650, 800, 52, "老式 8 针", c="muted", d=0.2), T(12, 1350, 360, 52, "据估算", c="muted", d=0.3),
   icon(12, "clock", 1350, 560, 180, 0.4, mv="spin"))
# 12.5 接近一倍
bd(12.5, bar(12.5, 500, 820, 200, 300, "blue", d=0.1), bar(12.5, 500, 520, 200, 260, "green", d=0.5), T(12.5, 600, 880, 44, "老式"),
   bar(12.5, 1000, 820, 200, 300, "blue", d=0.1), bar(12.5, 1000, 520, 200, 45, "red", d=0.5), T(12.5, 1100, 880, 44, "新式"),
   BIG(12.5, 1500, 480, "≈ ×2", c="green", d=0.6, s=110))
# 13 平均8安不到上限
bd(13, bar(13, 600, 820, 220, 420, "blue", d=0.1), [P(13, "M520,330 L900,330", c="green", w=6, idp=(ln := uid("ln"))), pop(13, ln, 0.3), pulse(13, ln, 0.8)],
   check(13, 1300, 450, d=0.5), T(13, 1350, 700, 56, "没超上限啊", c="ink", d=0.4))
# 13.5 怎么还会烧
k_, ki = xiaoka(13.5, 700, 560, 1.3, mood="o")
bd(13.5, k_, icon(13.5, "question", 1250, 300, 220, 0.2, c="red", mv="wig"), flame(13.5, 1350, 650, 180, 0.5))
# 14 六个人
E = []
for q in range(6):
    E += person(14, 360 + 240 * q, 620, 1.0)
bd(14, E, T(14, 960, 220, 64, "六个人", c="ink", d=0.2))
# 14.5 抬钢琴
p_, pi = piano(14.5, 960, 470, 1300)
E = []
for q in range(6):
    E += person(14.5, 420 + 216 * q, 680, 0.9)
bd(14.5, p_, E, [sh(14.5, pi, 0, -30, 0.3, 0.4), sh(14.5, pi, 0, 30, 0.8, 0.4)], T(14.5, 960, 940, 56, "一起抬一架钢琴", c="ink", d=0.4))
# 15 两个人手一松
p_, pi = piano(15, 960, 470, 1300)
E = []
for q in range(6):
    E += person(15, 420 + 216 * q, 680, 0.9, slack=q in (1, 4), c="muted" if q in (1, 4) else "ink")
bd(15, p_, E, [rot(15, pi, 4, (960, 470), 0.3, 0.4)], T(15, 960, 940, 56, "两个人手一松", c="red", d=0.3))
# 15.5 压到别人身上
p_, pi = piano(15.5, 960, 470, 1300)
E = []
for q in range(6):
    E += person(15.5, 420 + 216 * q, 680, 0.9, c="red" if q in (2, 3) else "ink", slack=q in (1, 4))
bd(15.5, p_, E, [sh(15.5, pi, 0, 40, 0.2, 0.4)], [e for q in (2, 3) for e in arr(15.5, 420 + 216 * q, 280, 420 + 216 * q, 400, c="red", d=0.3 + 0.1 * q)],
   T(15.5, 960, 940, 56, "重量全压过来", c="red", d=0.5))
# 16 电流也一样
bd(16, wires(16, 300, 1600, 300, gap=80, amps=(8,) * 6, d=0.0), T(16, 960, 860, 56, "六根针并排走", c="ink", d=0.2), plug(16, 1700, 500, 0.5))
# 16.5 往接触好的挤
bd(16.5, wires(16.5, 300, 1600, 280, gap=80, amps=(2, 20, 14, 1, 6, 2), d=0.0), T(16.5, 960, 860, 56, "哪根接触好，电就往哪挤", c="red", d=0.3))
# 17 没插到底
pl = plug(17, 700, 540, 1.2)
bd(17, pl, [sh(17, pl[0]["id"], -80, 0, 0.3, 0.5)], R(17, 920, 420, 300, 240, c="ink", fill="muted", idp=(sk := uid("sk"))) and [R(17, 920, 420, 300, 240, c="ink", idp=sk),
                                                                                                                                       bob(17, sk, 3, 1.0)],
   T(17, 1450, 540, 56, "没插到底", c="red", d=0.4), arr(17, 1250, 760, 920, 760, c="red", d=0.6))
# 17.5 接触变差
E = []
for q in range(4):
    i = uid("sp")
    E += [P(17.5, f"M{900 + 40 * q},{500} l20,-40 l20,40 l20,-40", c="red", w=5, idp=i), pop(17.5, i, 0.1 * q), wig(17.5, i, (920 + 40 * q, 480), 15, 4.0)]
bd(17.5, plug(17.5, 700, 540, 1.0, hot=(1, 4)), E, T(17.5, 1400, 540, 64, "接触变差", c="red", d=0.4))
# 18 反转二 实测
bd(18, BIG(18, 960, 160, "反转二", c="red", d=0.1, s=90), icon(18, "magnifier", 600, 500, 260, 0.2, mv="wig"), wires(18, 900, 1600, 380, gap=60, amps=(8,) * 6, d=0.3),
   T(18, 1250, 820, 52, "硬件媒体实测", c="ink", d=0.4))
# 18.5 有的线几乎没电流
bd(18.5, wires(18.5, 300, 1500, 280, gap=80, amps=(0, 0, 1, 0, 14, 22), d=0.0), BIG(18.5, 1700, 400, "≈ 0", c="muted", d=0.3, s=110), T(18.5, 900, 860, 56, "几乎没电流", c="muted", d=0.3))
# 19 有一根
bd(19, wires(19, 300, 1500, 450, gap=0.01, amps=(22,), d=0.0), arr(19, 900, 250, 900, 400, c="red", d=0.3), T(19, 900, 700, 60, "有一根……", c="ink", d=0.2),
   flame(19, 1650, 380, 140, 0.5))
# 19.5 22 安
bd(19.5, BIG(19.5, 960, 470, "22 安！", c="red", d=0.1, s=190), flame(19.5, 400, 700, 200, 0.2), flame(19.5, 1520, 700, 200, 0.4), wires(19.5, 300, 1620, 860, gap=1, amps=(22,), d=0.3))
# 20 比上限
bd(20, bar(20, 600, 860, 220, 230, "green", d=0.1), T(20, 710, 920, 44, "上限 9.2"), bar(20, 1000, 860, 220, 560, "red", d=0.4, dur=1.0), T(20, 1110, 920, 44, "22"),
   P(20, "M520,630 L1300,630", c="green", w=4, idp=(ln := uid("ln"))) and [P(20, "M520,630 L1300,630", c="green", w=4, idp=ln), pulse(20, ln, 0.5)])
# 20.5 两倍多
bd(20.5, BIG(20.5, 960, 450, "× 2 还多", c="red", d=0.1, s=170), [e for q in range(3) for e in flame(20.5, 560 + 400 * q, 780, 140, 0.2 + 0.15 * q)])
# 21 反转三
k_, ki = xiaoka(21, 600, 600, 1.2, mood="o")
bd(21, BIG(21, 960, 160, "反转三", c="red", d=0.1, s=90), k_, T(21, 1300, 450, 64, "电流 × 2", c="blue", d=0.3), arr(21, 1150, 560, 1450, 560, c="blue", d=0.5))
# 21.5 发热 × 4
E = []
for q in range(4):
    E += flame(21.5, 500 + 300 * q, 640, 180, 0.1 + 0.15 * q)
bd(21.5, BIG(21.5, 960, 300, "发热 × 4", c="red", d=0.1, s=150), E)
# 22 公式
bd(22, BIG(22, 960, 420, "发热 = I² × R", c="ink", d=0.1, s=130), [e for q in range(2) for e in icon(22, "gear", 400 + 1120 * q, 760, 150, 0.3 + 0.1 * q, mv="spin")],
   T(22, 960, 640, 56, "电流的平方", c="red", d=0.4))
# 22.5 乘电阻
E = []
for q in range(4):
    i = uid("sq")
    s_ = 70 + 70 * q
    E += [R(22.5, 400 + 250 * q - s_ / 2, 760 - s_, s_, s_, c="red", fill="red" if q == 3 else None, idp=i), pop(22.5, i, 0.1 + 0.15 * q), bob(22.5, i, 4, 1.0 + 0.1 * q)]
bd(22.5, E, T(22.5, 960, 280, 64, "1² · 2² · 3² · 4²", c="red", d=0.2), T(22.5, 1550, 600, 52, "× 电阻", c="ink", d=0.6))
# 23 22 是 8 的不到三倍
bd(23, bar(23, 500, 820, 180, 180, "blue", d=0.1), T(23, 590, 880, 44, "8 安"), bar(23, 800, 820, 180, 495, "red", d=0.3, dur=0.8), T(23, 890, 880, 44, "22 安"),
   BIG(23, 1450, 480, "< × 3", c="blue", d=0.5, s=130))
# 23.5 发热七倍多
bd(23.5, bar(23.5, 400, 860, 160, 80, "blue", d=0.1), bar(23.5, 650, 860, 160, 600, "red", d=0.3, dur=1.2), T(23.5, 480, 920, 40, "8 安"), T(23.5, 730, 920, 40, "22 安"),
   BIG(23.5, 1350, 450, "发热 × 7.5", c="red", d=0.6, s=120), flame(23.5, 1350, 700, 160, 0.9))
# 24 热了接触差
bd(24, thermo(24, 600, 560, 0.3, 0.7, 0.1), arr(24, 760, 500, 1100, 500, c="red", d=0.4), plug(24, 1400, 520, 0.9, hot=(2,), d=0.5), T(24, 960, 880, 52, "热了 → 接触更差", c="red", d=0.4))
# 24.5 接触差又更热
bd(24.5, plug(24.5, 600, 520, 0.9, hot=(2, 3)), arr(24.5, 800, 500, 1150, 500, c="red", d=0.3), thermo(24.5, 1400, 560, 0.6, 1.0, 0.4), T(24.5, 960, 880, 52, "接触差 → 更热", c="red", d=0.4))
# 25 一圈一圈
bd(25, loop_arrows(25, 960, 520, 230), T(25, 960, 380, 52, "热", c="red", d=0.2), T(25, 960, 700, 52, "接触差", c="red", d=0.4), flame(25, 960, 470, 100, 0.5),
   [e for q in range(2) for e in flame(25, 400 + 1120 * q, 700, 130, 0.3 + 0.2 * q)])
# 25.5 滚雪球
hill = uid("hill")
bd(25.5, [P(25.5, "M200,380 L1700,880", c="ink", w=6, idp=hill), bob(25.5, hill, 2, 0.5)], snowball(25.5, 400, 360, 0.1), T(25.5, 1300, 340, 64, "滚雪球", c="blue", d=0.3),
   icon(25.5, "sun", 1700, 250, 140, 0.2, c="gold", mv="spin"))
# 26 热像仪
bd(26, icon(26, "camera", 600, 520, 280, 0.0, mv="wig") if False else icon(26, "eye", 600, 520, 260, 0.0, mv="wig"), plug(26, 1300, 520, 1.0, hot=(0, 1, 2, 3, 4, 5)),
   [e for q in range(3) for e in arr(26, 780, 420 + 100 * q, 1100, 420 + 100 * q, c="red", d=0.2 + 0.1 * q)], T(26, 960, 860, 56, "热像仪一拍", c="ink", d=0.3))
# 26.5 175 度
bd(26.5, thermo(26.5, 500, 560, 0.2, 1.0, 0.1), BIG(26.5, 1200, 480, "175 °C", c="red", d=0.3, s=180), flame(26.5, 1200, 700, 180, 0.6))
# 27 塑料化了
pl = plug(27, 960, 500, 1.6, hot=range(6))
bd(27, pl, [{"t": "move", "at": 27, "kind": "grow", "targets": [pl[0]["id"]], "axis": "y", "from": 1.0, "to": 0.6, "pivot": [960, 630], "dur": 1.0, "delay": 0.3}],
   flame(27, 700, 760, 140, 0.2), flame(27, 1220, 760, 140, 0.4), T(27, 960, 220, 60, "塑料外壳化了", c="red", d=0.3))
# 27.5 熔成一坨
lump = uid("lump")
bd(27.5, [P(27.5, "M700,620 Q760,420 900,480 Q1000,380 1120,500 Q1260,520 1220,640 Q1000,700 700,620 Z", c="ink", w=6, fill="muted", idp=lump), pop(27.5, lump, 0.1),
          wig(27.5, lump, (960, 640), 4, 1.5)], wires(27.5, 200, 700, 520, gap=30, amps=(0,) * 4, d=0), cross(27.5, 1500, 520, d=0.5),
   T(27.5, 960, 880, 56, "熔成一坨", c="red", d=0.3))
# 28 怎么防 插到底
pl = plug(28, 500, 540, 1.0)
bd(28, BIG(28, 960, 160, "怎么防？", c="green", d=0.1, s=90), pl, [sh(28, pl[0]["id"], 300, 0, 0.3, 0.5)], [R(28, 900, 420, 300, 240, c="ink", idp=(sk := uid("sk"))), bob(28, sk, 3, 1)],
   T(28, 1500, 540, 60, "① 插到底", c="green", d=0.4))
# 28.5 咔哒
bd(28.5, BIG(28.5, 960, 480, "咔哒！", c="green", d=0.2, s=170), check(28.5, 1500, 500, d=0.5), icon(28.5, "speaker", 450, 480, 200, 0.0, mv="wig"))
# 29 线别硬弯
cb = uid("cb")
bd(29, [P(29, "M300,500 L800,500 Q880,500 880,580 L880,860", c="ink", w=14, idp=cb), pop(29, cb, 0.0), wig(29, cb, (300, 500), 3, 1.0)], plug(29, 220, 500, 0.5),
   cross(29, 920, 520, d=0.4), T(29, 1450, 500, 60, "② 线别硬弯", c="green", d=0.3))
# 29.5 贴着插头
cb2 = uid("cb")
bd(29.5, [P(29.5, "M300,500 L1100,500 Q1500,500 1500,860", c="ink", w=14, idp=cb2), pop(29.5, cb2, 0.0), wig(29.5, cb2, (300, 500), 3, 1.0)], plug(29.5, 220, 500, 0.5),
   check(29.5, 1300, 380, d=0.4), T(29.5, 800, 780, 52, "留一段直的", c="green", d=0.4))
# 30 逐根测电流
bd(30, wires(30, 300, 1300, 300, gap=80, amps=(8,) * 6, d=0.0), [e for q in range(6) for e in icon(30, "magnifier", 1400, 260 + 80 * q, 60, 0.1 * q, mv="wig")],
   T(30, 960, 860, 56, "③ 逐根测电流", c="green", d=0.3))
# 30.5 不均就报警
bd(30.5, wires(30.5, 300, 1100, 300, gap=80, amps=(2, 20, 8, 8, 1, 8), d=0.0), icon(30.5, "speaker", 1400, 450, 220, 0.3, c="red", mv="wig"),
   BIG(30.5, 1450, 760, "报警！", c="red", d=0.5, s=110))
# 31 友情提示
k_, ki = xiaoka(31, 700, 600, 1.2)
bd(31, k_, T(31, 960, 200, 64, "友情提示", c="ink", d=0.1), icon(31, "question", 1350, 400, 220, 0.3, c="muted", mv="wig"))
# 31.5 还没定论
bd(31.5, icon(31.5, "magnifier", 600, 500, 260, 0.0, mv="wig"), BIG(31.5, 1300, 480, "还没定论", c="muted", d=0.3, s=120), icon(31.5, "clock", 1300, 760, 140, 0.5, mv="spin"))
# 32 只是物理
bd(32, bar(32, 400, 820, 160, 60, "red", d=0.1), T(32, 480, 880, 40, "余量小"), wires(32, 700, 1200, 400, gap=60, amps=(1, 20, 8, 0, 14), d=0.2), T(32, 950, 880, 40, "电流不均"),
   icon(32, "gear", 1550, 560, 200, 0.3, mv="spin"))
# 32.5 平方往上涨
crv = uid("crv")
bd(32.5, [P(32.5, "M400,860 Q1100,840 1500,260", c="red", w=8, idp=crv),
          {"t": "move", "at": 32.5, "kind": "grow", "targets": [crv], "axis": "both", "from": 0.2, "to": 1.0, "pivot": [400, 860], "dur": 1.0, "delay": 0.1}],
   arr(32.5, 400, 900, 1600, 900, c="ink", d=0), flame(32.5, 1500, 200, 120, 0.8), T(32.5, 900, 300, 64, "按平方涨", c="red", d=0.4))
# 33 新年愿望
k_, ki = xiaoka(33, 760, 600, 1.5)
bd(33, k_, [e for q in range(3) for e in star(33, 500 + 400 * q, 250, 0.2 + 0.2 * q, r=40)], T(33, 1450, 550, 60, "新年愿望", c="gold", d=0.3), n=3)
# 33.5 少吃一点 别上火
k_, ki = xiaoka(33.5, 700, 600, 1.5)
bd(33.5, k_, [sh(33.5, ki + "*", 0, -40, 0.3, 0.3), sh(33.5, ki + "*", 0, 40, 0.6, 0.3)], T(33.5, 1400, 420, 64, "少吃一点", c="blue", d=0.2),
   BIG(33.5, 1400, 640, "别上火", c="red", d=0.5, s=120), icon(33.5, "snowflake", 1400, 860, 90, 0.8, c="blue", mv="spin") if False else star(33.5, 1700, 860, 0.8, c="blue", r=40), n=3)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"RTX 5090": "R T X 五零九零"})
