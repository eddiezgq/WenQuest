"""Daily science short 2026-10-26 (English): "Why Is This Chip the Size of a Dinner Plate?"
News: Cerebras blog "How we deploy trillion-parameter frontier models on Cerebras" (Oct 2026): a ~3-trillion-parameter model
(Kimi K3, used as the worked example) mapped across 59 WSE-3T wafers; Hacker News 25 Oct 2026 digest #3, 343 points
("Cerebras runs a 3-trillion-parameter model across 59 wafers at 2,000 tokens per second"); also daily.dev, neoteo, techplanet.
Facts used (Cerebras blog): 44 GB on-chip memory per wafer; 4-bit weights -> ~1.5 TB, ~16 GB per layer; 93 layers = 69 linear-attention
+ 24 dense; dense layers one per wafer (24 wafers), linear-attention two per wafer (35 wafers) = 59; pipeline: only activations move,
wafers linked by RDMA over Ethernet ~2 microseconds per hop; target "1000-2000+ tokens per second"; the blog calls its example illustrative.
Textbook: wafer-scale chip ~21.5 cm on a side (WSE-3); LLM token generation is memory-bandwidth bound; Cerebras routes around
defects with spare cores. Analogy: chef + fridge down the hall. Character: Chippy, a little chip. Gag: "the hallway".
    python3 make.py <kokoro model dir> | --boards-only | --fake   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("这块AI芯片，|为什么有餐盘那么大？", "Why is this AI chip | the size of a dinner plate?"),
 ("排上59块，|就能跑一个三万亿参数的AI。", "Line up fifty nine of them, | and they run a three trillion parameter AI."),
 ("Cerebras说，一秒能吐上千到两千个词元，|差不多每秒好几页字。", "Cerebras says it can write up to two thousand tokens a second. | That's pages of text, every second."),
 ("今天的问题：|芯片做大，AI为什么就变快？", "Today's question: | why does a bigger chip make AI faster?"),
 ("认识一下小芯，|一块普通芯片，跟邮票差不多大。", "Meet Chippy. | A normal chip, about as big as a postage stamp."),
 ("小芯算数快得吓人，|一秒几万亿次乘法。", "Chippy does math insanely fast. | Trillions of multiplications a second."),
 ("可问题是：|小芯大部分时间在等。", "But here's the catch: | most of the time, Chippy is waiting."),
 ("等什么？|等内存把数字送过来。", "Waiting for what? | For numbers to arrive from memory."),
 ("想象一个厨师，一秒就能炒好菜，|可冰箱在走廊尽头。", "Picture a chef who cooks in one second, | but the fridge is down the hall."),
 ("AI每写一个词，|都要把一大堆参数从内存读一遍。", "To write each word, an AI must read | a huge pile of its numbers from memory."),
 ("就像每做一道菜，|每样食材都得跑一趟冰箱。", "It's like running to the fridge | for every ingredient of every dish."),
 ("所以限速的不是炒菜，|是走路。", "So the speed limit isn't the cooking. | It's the walking."),
 ("反转一：|要是冰箱就在灶台边呢？", "Twist one: | what if the fridge sat right on the counter?"),
 ("这就是Cerebras的思路：|硅晶圆不切成小芯片。", "That's the Cerebras idea: | don't cut the silicon wafer into little chips."),
 ("整片留着，|一块巨大的芯片，边长二十多厘米。", "Keep the whole wafer: | one giant chip, about twenty centimeters on a side."),
 ("内存就贴在每个小核旁边，|一片晶圆上有44个G。", "Memory sits right beside every tiny core. | Forty four gigabytes on one wafer."),
 ("食材就在手边，|不用走廊了。", "The ingredients are within arm's reach. | No more hallway."),
 ("反转二：|44个G还是不够。", "Twist two: | forty four gigabytes still isn't enough."),
 ("每个参数用4个比特存，|整个模型也有大约1.5个T。", "Even at four bits per number, | the model weighs about one and a half terabytes."),
 ("一层大约16个G，|一共93层。", "That's about sixteen gigabytes per layer, | and there are ninety three layers."),
 ("那就搭一条流水线：|每片晶圆管一两层。", "So build an assembly line: | each wafer holds one or two layers."),
 ("第一片算完自己的层，|把结果交给第二片。", "Wafer one runs its layers, | then hands the result to wafer two."),
 ("晶圆之间只传小小的中间结果，|沉重的参数一动不动。", "Only small results travel between wafers. | The heavy numbers never move."),
 ("每传一次大约两微秒，|眨一下眼，够传几万次。", "Each hop takes about two microseconds. | One blink fits tens of thousands of hops."),
 ("反转三，最鸡贼的一个：|第二片在忙，第一片已经开始下一单。", "Twist three, the sneaky one: | while wafer two works, wafer one starts the next request."),
 ("就像汽车厂，|流水线上同时好多辆车。", "Like a car factory: | lots of cars on the line at once."),
 ("算一下：24片放大层，|35片放小层，正好59。", "Count them: twenty four wafers for the big layers, | thirty five for the light ones. Fifty nine."),
 ("小层只记一个固定大小的小本子，|所以两层能挤一片。", "The light layers keep a small fixed notebook, | so two of them can share one wafer."),
 ("结果：这么大的模型，|目标一秒一千到两千个词元。", "The result: for a model this huge, | the target is one to two thousand tokens a second."),
 ("友情提示：这是公司自己的博客，|例子是一份部署方案，还没有第三方实测。", "Friendly fine print: this is the company's own blog. | It's a deployment plan, not an independent test."),
 ("而且整片晶圆很难造，|它得留备用的核，绕开坏点。", "And a whole wafer is hard to make. | It carries spare cores to route around defects."),
 ("所以秘诀不是越大越好，|是别再跑冰箱。", "So the secret isn't just bigger. | It's stop running to the fridge."),
 ("在电脑里，搬数据|常常比算数还贵。", "Inside computers, moving data | often costs more than doing the math."),
 ("下次AI秒回你的时候，|谢谢那个从不出厨房的厨师。", "So next time your AI answers instantly, | thank the chef who never leaves the kitchen."),
]
TITLE = {"zh": "这块芯片为什么有餐盘大？", "en": "Why Is This Chip the Size of a Dinner Plate?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 880, 0.5, r=16)
    B.append(E)


def chippy(a, x, y, k=1.0, mood="happy", d=None, c="blue"):
    """Chippy: a square chip with pins all round (pins wiggle), two eyes, a mouth, and it bobs."""
    i = uid("ch") + "_"
    pn = i + "pn"
    s = 80 * k
    E = [R(a, x - s, y - s, 2 * s, 2 * s, c="ink", fill=c, idp=i),
         R(a, x - s * .55, y - s * .55, 1.1 * s, 1.1 * s, c="paper", idp=i, sw=3),
         O(a, x - 28 * k, y - 15 * k, 10 * k, c="ink", fill="ink", idp=i), O(a, x + 28 * k, y - 15 * k, 10 * k, c="ink", fill="ink", idp=i)]
    pins = " ".join(f"M{x - s + q * s / 2},{y - s} L{x - s + q * s / 2},{y - s - 22 * k} M{x - s + q * s / 2},{y + s} L{x - s + q * s / 2},{y + s + 22 * k}"
                    for q in range(1, 4))
    pins += " " + " ".join(f"M{x - s},{y - s + q * s / 2} L{x - s - 22 * k},{y - s + q * s / 2} M{x + s},{y - s + q * s / 2} L{x + s + 22 * k},{y - s + q * s / 2}"
                           for q in range(1, 4))
    m = {"happy": f"M{x - 22 * k},{y + 18 * k} Q{x},{y + 36 * k} {x + 22 * k},{y + 18 * k}",
         "o": f"M{x - 9 * k},{y + 24 * k} a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0",
         "sad": f"M{x - 22 * k},{y + 32 * k} Q{x},{y + 16 * k} {x + 22 * k},{y + 32 * k}"}[mood]
    E += [P(a, pins, c="ink", w=5, idp=pn), P(a, m, c="ink", w=4, idp=i),
          wig(a, pn, (x, y), 4, 2.5), bob(a, i, 8 * k, 1.4), bob(a, pn, 8 * k, 1.4)]
    if d is not None:
        E.append(pop(a, [i, pn], d))
    return E, [i, pn]


def wafer(a, x, y, r=260, d=0.0, c="blue", rpm=12):
    """A round wafer with a grid of little dies; it slowly turns."""
    i = uid("wf")
    g = " ".join(f"M{x - r * .8},{y + q * r / 4} L{x + r * .8},{y + q * r / 4} M{x + q * r / 4},{y - r * .8} L{x + q * r / 4},{y + r * .8}" for q in range(-3, 4))
    return [O(a, x, y, r, c="ink", fill=c, idp=i), P(a, g, c="paper", w=3, idp=i), pop(a, i, d), spin(a, i, (x, y), rpm)]


def chef(a, x, y, k=1.0, d=0.0):
    """Stick chef with a tall hat; the spatula arm wiggles."""
    i, ar = uid("cf"), uid("cfa")
    E = [O(a, x, y - 120 * k, 40 * k, c="ink", fill="paper", idp=i),
         P(a, f"M{x - 35 * k},{y - 160 * k} L{x - 35 * k},{y - 220 * k} Q{x},{y - 260 * k} {x + 35 * k},{y - 220 * k} L{x + 35 * k},{y - 160 * k} Z", c="ink", w=5, fill="paper", idp=i),
         P(a, f"M{x},{y - 80 * k} L{x},{y + 60 * k} M{x},{y + 60 * k} L{x - 40 * k},{y + 150 * k} M{x},{y + 60 * k} L{x + 40 * k},{y + 150 * k} M{x},{y - 40 * k} L{x - 60 * k},{y + 10 * k}", c="ink", w=6, idp=i),
         P(a, f"M{x},{y - 40 * k} L{x + 80 * k},{y - 10 * k} L{x + 130 * k},{y - 40 * k}", c="ink", w=6, idp=ar),
         pop(a, [i, ar], d), wig(a, ar, (x, y - 40 * k), 18, 3.0), bob(a, i, 5, 1.0)]
    return E, [i, ar]


def fridge(a, x, y, s=1.0, d=0.0):
    i = uid("fr")
    return [R(a, x - 70 * s, y - 150 * s, 140 * s, 300 * s, c="ink", fill="paper", idp=i), P(a, f"M{x - 70 * s},{y - 40 * s} L{x + 70 * s},{y - 40 * s} M{x + 45 * s},{y - 120 * s} L{x + 45 * s},{y - 70 * s}", c="ink", w=5, idp=i),
            pop(a, i, d), wig(a, i, (x, y + 150 * s), 2, 1.0)]


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def runner(a, x0, y, x1, d=0.0, dur=0.8, c="red"):
    """A little dot that dashes from x0 to x1 (a trip down the hall)."""
    i = uid("rn")
    return [O(a, x0, y, 18, c="ink", fill=c, idp=i), pop(a, i, d), sh(a, i, x1 - x0, 0, d + 0.1, dur)]


def flash(a, x, y, d=0.0, c="gold", r=110):
    i = uid("fl")
    return [P(a, " ".join(f"M{x},{y} L{x + r * dx},{y + r * dy}" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, -.7), (.7, -.7), (-.7, .7))), c=c, w=7, idp=i),
            pop(a, i, d), spin(a, i, (x, y), 30), pulse(a, i, d + 0.4)]


def gear(a, x, y, s=140, d=0.0, rpm=60, c="ink"):
    i = uid("gr")
    return [{"t": "icon", "at": a, "id": i, "name": "gear", "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), spin(a, i, (x, y), rpm)]


def line(a, n, x0, y, gap, k=0.35, d=0.0, step=0.1, c="blue"):
    """A row of n little wafers popping in one after another."""
    E = []
    for q in range(n):
        E += wafer(a, x0 + gap * q, y, 120 * k * 2, d + step * q, c=c, rpm=20)
    return E


def packet(a, x0, y, dx, d=0.0, dur=0.6, c="gold"):
    i = uid("pk")
    return [R(a, x0 - 20, y - 20, 40, 40, c="ink", fill=c, idp=i), pop(a, i, d), sh(a, i, dx, 0, d + 0.1, dur)]


# 0 dinner plate chip
bd(0, wafer(0, 700, 500, 300, 0.0), chippy(0, 1450, 520, 0.5, mood="o", d=0.3)[0], BIG(0, 1450, 260, "?!", c="red", d=0.2, s=150), T(0, 700, 900, 56, "a chip the size of a plate", c="ink", d=0.4))
# 0.5 dinner plate
pl = uid("pl")
bd(0.5, [O(0.5, 960, 500, 340, c="ink", fill="paper", idp=pl), pop(0.5, pl, 0.0), pulse(0.5, pl, 0.6)], wafer(0.5, 960, 500, 270, 0.2), icon(0.5, "ruler", 960, 900, 160, 0.4, mv="wig"),
   icon(0.5, "check", 1550, 300, 140, 0.5, c="green"))
# 1 line up 59
bd(1, line(1, 8, 260, 480, 200, d=0.0, step=0.08), BIG(1, 960, 800, "x 59", c="red", d=0.6, s=130))
# 1.5 three trillion parameters
bd(1.5, BIG(1.5, 960, 340, "3,000,000,000,000", c="blue", d=0.0, s=110), T(1.5, 960, 520, 60, "parameters", c="ink", d=0.2), icon(1.5, "robot_arm", 600, 760, 200, 0.3, mv="wig"),
   icon(1.5, "chip", 1320, 760, 180, 0.4, mv="spin"))
# 2 two thousand tokens a second
bd(2, BIG(2, 960, 380, "2,000 / s", c="red", d=0.0, s=150), icon(2, "clock", 450, 700, 180, 0.2, mv="spin"), [e for q in range(5) for e in packet(2, 700, 700 + 0 * q, 900, d=0.2 + 0.25 * q, dur=0.5)],
   T(2, 960, 900, 50, "tokens (word pieces)", c="muted", d=0.3))
# 2.5 pages every second
pg = []
for q in range(4):
    i = uid("pg")
    pg += [R(2.5, 500 + 260 * q, 360, 200, 270, c="ink", fill="paper", idp=i), P(2.5, " ".join(f"M{530 + 260 * q},{400 + 40 * j} L{670 + 260 * q},{400 + 40 * j}" for j in range(5)), c="muted", w=3, idp=i),
           pop(2.5, i, 0.15 * q), sh(2.5, i, 0, -40, 0.3 + 0.15 * q, 0.4)]
bd(2.5, pg, T(2.5, 960, 800, 64, "pages. every. second.", c="red", d=0.5))
# 3 today's question
bd(3, chippy(3, 600, 520, 1.2, mood="o")[0], icon(3, "question", 1300, 450, 280, 0.2, c="red", mv="wig"), T(3, 1300, 760, 60, "today's question", c="ink", d=0.3))
# 3.5 bigger = faster?
bd(3.5, chippy(3.5, 500, 560, 0.5)[0], arr(3.5, 650, 560, 1000, 560, c="ink", d=0.2), wafer(3.5, 1350, 520, 240, 0.3), icon(3.5, "rocket", 1350, 180, 140, 0.5, c="red", mv="wig"),
   T(3.5, 960, 880, 60, "bigger = faster?", c="red", d=0.4))
# 4 meet Chippy
p_, pi = chippy(4, 760, 500, 2.0, d=0.0)
bd(4, p_, BIG(4, 1450, 380, "Chippy", c="blue", d=0.3, s=140), [e for q in range(3) for e in star(4, 1330 + 120 * q, 600, 0.5 + 0.1 * q, r=30)])
# 4.5 postage stamp
st = uid("stp")
bd(4.5, chippy(4.5, 700, 500, 0.7)[0], [R(4.5, 1150, 330, 300, 360, c="red", idp=st, sw=6), P(4.5, "M1190,380 L1410,380 L1410,640 L1190,640 Z", c="red", w=3, idp=st), pop(4.5, st, 0.2), rot(4.5, st, -8, (1300, 510), 0.5, 0.4)],
   T(4.5, 960, 860, 60, "about stamp-size", c="ink", d=0.4))
# 5 math insanely fast
bd(5, chippy(5, 500, 520, 1.1)[0], gear(5, 1100, 400, 200, 0.1, 160), gear(5, 1300, 600, 160, 0.2, -200, c="blue"), gear(5, 1500, 400, 140, 0.3, 220, c="red"), T(5, 1250, 860, 56, "math: super fast", c="ink", d=0.4))
# 5.5 trillions of multiplications
bd(5.5, BIG(5.5, 960, 380, "× × × ×", c="red", d=0.0, s=150), BIG(5.5, 960, 640, "trillions / s", c="blue", d=0.3, s=100), [e for q in range(4) for e in flash(5.5, 400 + 370 * q, 840, 0.2 + 0.1 * q, r=50)])
# 6 the catch
bd(6, chippy(6, 960, 500, 1.4, mood="o")[0], T(6, 960, 160, 70, "the catch...", c="red", d=0.2), icon(6, "magnifier", 1550, 600, 180, 0.4, mv="wig"))
# 6.5 most of the time waiting
p_, pi = chippy(6.5, 700, 520, 1.1, mood="sad")
bd(6.5, p_, icon(6.5, "clock", 1350, 450, 260, 0.1, mv="spin"), [e for q in range(3) for e in T(6.5, 950 + 60 * q, 300 - 50 * q, 40 + 12 * q, "z", c="muted", d=0.2 + 0.2 * q)],
   T(6.5, 1350, 760, 60, "waiting...", c="muted", d=0.3), bar(6.5, 1250, 900, 200, 80, "muted", d=0.4))
# 7 waiting for what
bd(7, chippy(7, 600, 520, 1.1, mood="o")[0], icon(7, "question", 1300, 500, 260, 0.1, c="red", mv="wig"), T(7, 1300, 800, 56, "waiting for what?", c="ink", d=0.3))
# 7.5 numbers from memory
mem = uid("mem")
bd(7.5, [R(7.5, 1250, 300, 380, 420, c="ink", fill="muted", idp=mem), pop(7.5, mem, 0.0), wig(7.5, mem, (1440, 720), 2, 1.0)], T(7.5, 1440, 510, 64, "MEMORY", c="paper"),
   chippy(7.5, 400, 520, 0.8, mood="o")[0], [e for q in range(4) for e in packet(7.5, 1200, 420 + 70 * q, -650, d=0.2 + 0.2 * q, dur=0.9, c="gold")])
# 8 chef cooks in one second
bd(8, chef(8, 600, 600, 1.4)[0], icon(8, "flame", 1000, 720, 180, 0.2, c="red", mv="wig"), BIG(8, 1400, 400, "1 s", c="red", d=0.3, s=150), T(8, 1400, 620, 56, "to cook", c="ink", d=0.4))
# 8.5 fridge down the hall
hl = uid("hl")
bd(8.5, chef(8.5, 300, 600, 0.9)[0], [P(8.5, "M450,780 L1450,780", c="muted", w=6, idp=hl), pop(8.5, hl, 0.0), {"t": "move", "at": 8.5, "kind": "grow", "targets": [hl], "axis": "x", "pivot": [450, 780], "dur": 0.6, "delay": 0.0}],
   fridge(8.5, 1600, 620, 1.0, 0.3), T(8.5, 950, 860, 56, "the hallway", c="red", d=0.4), runner(8.5, 450, 740, 1450, d=0.5, dur=1.0))
# 9 each word reads memory
bd(9, T(9, 600, 300, 70, "each word...", c="ink", d=0.0), chippy(9, 600, 620, 0.9)[0], icon(9, "chip", 1350, 500, 260, 0.2, mv="spin"), arr(9, 1200, 500, 800, 600, c="gold", d=0.4))
# 9.5 huge pile of numbers
pile = []
for q in range(12):
    pile += T(9.5, 700 + 90 * (q % 6), 760 - 90 * (q // 6), 60, str((q * 7) % 10), c="blue", d=0.05 * q)
bd(9.5, pile, arr(9.5, 1300, 600, 1600, 400, c="red", d=0.6), T(9.5, 960, 260, 64, "a huge pile of numbers", c="ink", d=0.2), chippy(9.5, 1650, 330, 0.4, mood="o")[0])
# 10 running to the fridge
bd(10, chef(10, 300, 600, 0.8)[0], fridge(10, 1600, 600, 0.9, 0.0), [e for q in range(3) for e in runner(10, 450, 520 + 80 * q, 1450, d=0.1 + 0.3 * q, dur=0.6)],
   T(10, 960, 880, 56, "run... run... run...", c="red", d=0.3))
# 10.5 every ingredient every dish
ing = []
for q, n in enumerate(["sun", "water", "flame", "wind"]):
    ing += icon(10.5, n, 450 + 330 * q, 500, 160, 0.1 * q, c=["gold", "blue", "red", "blue"][q], mv="bob")
bd(10.5, ing, [e for q in range(4) for e in arr(10.5, 450 + 330 * q, 640, 450 + 330 * q, 760, c="red", d=0.3 + 0.1 * q)], T(10.5, 960, 880, 56, "a trip for EVERY ingredient", c="ink", d=0.4))
# 11 not the cooking
bd(11, chef(11, 600, 600, 1.2)[0], icon(11, "flame", 900, 720, 150, 0.1, c="red", mv="wig"), check(11, 1300, 450, d=0.3), T(11, 1350, 700, 60, "cooking: fast", c="green", d=0.4))
# 11.5 it's the walking
bd(11.5, [e for q in range(4) for e in runner(11.5, 300, 400 + 100 * q, 1600, d=0.1 * q, dur=1.4, c="red")], BIG(11.5, 960, 860, "the WALKING", c="red", d=0.4, s=110),
   icon(11.5, "clock", 960, 220, 140, 0.2, mv="spin"))
# 12 twist one
bd(12, BIG(12, 960, 200, "Twist 1", c="blue", d=0.0, s=100), chef(12, 600, 650, 1.0)[0], fridge(12, 1300, 600, 0.9, 0.3), arr(12, 1500, 400, 1380, 400, c="red", d=0.5))
# 12.5 fridge on the counter
ct = uid("ct")
bd(12.5, [R(12.5, 400, 700, 1100, 40, c="ink", fill="muted", idp=ct), pop(12.5, ct, 0.0)], chef(12.5, 600, 560, 0.9)[0], fridge(12.5, 1100, 560, 0.8, 0.2), icon(12.5, "flame", 850, 640, 90, 0.3, c="red", mv="wig"),
   T(12.5, 960, 880, 56, "fridge on the counter!", c="green", d=0.4))
# 13 the Cerebras idea
bd(13, T(13, 960, 200, 80, "Cerebras", c="blue", d=0.0), wafer(13, 960, 560, 260, 0.2), icon(13, "lens", 1550, 560, 180, 0.4, mv="wig"))
# 13.5 don't cut the wafer
kn = uid("kn")
bd(13.5, wafer(13.5, 800, 520, 300, 0.0), [P(13.5, "M1300,250 L1500,250 L1550,300 L1300,300 Z M1500,250 L1700,200", c="ink", w=6, idp=kn, fill="muted"), pop(13.5, kn, 0.2), rot(13.5, kn, -20, (1500, 275), 0.4, 0.5)],
   cross(13.5, 1500, 500, d=0.5), T(13.5, 960, 900, 56, "don't cut it up", c="red", d=0.5))
# 14 keep whole wafer
bd(14, wafer(14, 960, 500, 330, 0.0, rpm=20), BIG(14, 960, 920, "ONE chip", c="blue", d=0.3, s=100), [e for q in range(4) for e in flash(14, 960 + 420 * (q % 2 * 2 - 1), 250 + 500 * (q // 2), 0.2 + 0.1 * q, r=50)])
# 14.5 twenty centimeters
bd(14.5, wafer(14.5, 700, 500, 280, 0.0), arr(14.5, 420, 860, 980, 860, c="red", d=0.2), BIG(14.5, 1400, 420, "~21 cm", c="red", d=0.3, s=130), chippy(14.5, 1400, 700, 0.3, d=0.5)[0],
   T(14.5, 1550, 700, 44, "vs", c="muted", d=0.5))
# 15 memory beside every core
cells = []
for q in range(16):
    i, j = uid("cr"), uid("mm")
    x, y = 560 + 200 * (q % 4), 260 + 180 * (q // 4)
    cells += [R(15, x, y, 70, 70, c="ink", fill="blue", idp=i), R(15, x + 80, y, 50, 70, c="ink", fill="gold", idp=j), pop(15, [i, j], 0.04 * q)]
cells += [pulse(15, cells[0]["id"], 0.8)]
bd(15, cells, T(15, 1600, 400, 50, "core", c="blue", d=0.3), T(15, 1600, 500, 50, "memory", c="gold", d=0.5), sound(15, 1600, 650, 0.6, d=0.6))
# 15.5 44 GB
bd(15.5, wafer(15.5, 600, 500, 260, 0.0), BIG(15.5, 1350, 450, "44 GB", c="gold", d=0.2, s=160), T(15.5, 1350, 650, 56, "on one wafer", c="ink", d=0.4), bar(15.5, 1250, 900, 200, 120, "gold", d=0.5))
# 16 within arm's reach
bd(16, chef(16, 800, 620, 1.2)[0], fridge(16, 1100, 600, 0.7, 0.1), icon(16, "flame", 600, 700, 140, 0.2, c="red", mv="wig"), [e for q in range(3) for e in star(16, 1300 + 120 * q, 300, 0.3 + 0.1 * q, r=30)])
# 16.5 no more hallway
bd(16.5, [P(16.5, "M400,600 L1500,600", c="muted", w=8, idp=uid("hw"))], cross(16.5, 960, 600, d=0.1), BIG(16.5, 960, 860, "no hallway", c="green", d=0.3, s=110), chippy(16.5, 960, 320, 0.8, d=0.4)[0])
# 17 twist two
bd(17, BIG(17, 960, 200, "Twist 2", c="blue", d=0.0, s=100), chippy(17, 960, 550, 1.2, mood="o")[0], icon(17, "question", 1500, 500, 200, 0.3, c="red", mv="wig"))
# 17.5 not enough
bd(17.5, bar(17.5, 600, 850, 200, 150, "gold", d=0.0), bar(17.5, 1100, 850, 200, 600, "red", d=0.3), T(17.5, 700, 650, 50, "44 GB", c="gold", d=0.1), T(17.5, 1200, 200, 50, "needed", c="red", d=0.5),
   cross(17.5, 700, 500, d=0.6))
# 18 four bits
bits = []
for q in range(4):
    i = uid("bt")
    bits += [R(18, 650 + 160 * q, 380, 120, 120, c="ink", fill="blue" if q % 2 else "paper", idp=i), pop(18, i, 0.1 * q), rot(18, i, 180, (710 + 160 * q, 440), 0.5 + 0.1 * q, 0.4)]
bd(18, bits, T(18, 960, 640, 64, "4 bits per number", c="ink", d=0.3), icon(18, "magnifier", 1550, 440, 160, 0.4, mv="wig"))
# 18.5 1.5 TB
bd(18.5, BIG(18.5, 960, 380, "1.5 TB", c="red", d=0.0, s=160), bar(18.5, 600, 880, 120, 60, "gold", d=0.2), bar(18.5, 1100, 880, 120, 300, "red", d=0.3), T(18.5, 660, 900 - 20, 40, "44 GB", c="gold", d=0.3),
   icon(18.5, "building", 1500, 700, 200, 0.5, mv="bob"))
# 19 16 GB per layer
lay = []
for q in range(6):
    i = uid("ly")
    lay += [R(19, 500, 780 - 90 * q, 500, 70, c="ink", fill="blue", idp=i), pop(19, i, 0.07 * q), sh(19, i, 20 * (q % 2 * 2 - 1), 0, 0.5, 0.4)]
bd(19, lay, BIG(19, 1400, 450, "16 GB", c="blue", d=0.3, s=130), T(19, 1400, 640, 50, "per layer", c="ink", d=0.4))
# 19.5 93 layers
lay = []
for q in range(10):
    i = uid("ly")
    lay += [R(19.5, 400, 860 - 66 * q, 420, 50, c="ink", fill="blue" if q % 3 else "red", idp=i), pop(19.5, i, 0.05 * q)]
bd(19.5, lay, BIG(19.5, 1350, 450, "93 layers", c="red", d=0.3, s=130), icon(19.5, "lattice", 1350, 720, 160, 0.5, mv="spin"))
# 20 assembly line
bt_ = uid("belt")
bd(20, [P(20, "M200,700 L1720,700", c="ink", w=10, idp=bt_), pop(20, bt_, 0.0)], gear(20, 300, 760, 100, 0.1, 120), gear(20, 1620, 760, 100, 0.1, 120),
   [e for q in range(4) for e in packet(20, 300, 650, 1200, d=0.2 + 0.25 * q, dur=1.4)], T(20, 960, 300, 72, "an assembly line", c="ink", d=0.2))
# 20.5 each wafer holds one or two layers
bd(20.5, line(20.5, 5, 400, 500, 280, 0.45, d=0.0, step=0.1), T(20.5, 400, 760, 56, "1-2", c="red", d=0.3), T(20.5, 680, 760, 56, "1-2", c="red", d=0.4), T(20.5, 960, 760, 56, "1-2", c="red", d=0.5),
   T(20.5, 960, 880, 50, "layers per wafer", c="ink", d=0.6))
# 21 wafer one runs its layers
bd(21, wafer(21, 600, 500, 220, 0.0, rpm=40), T(21, 600, 800, 60, "wafer 1", c="blue", d=0.1), gear(21, 600, 500, 140, 0.2, 200, c="paper"), wafer(21, 1320, 500, 220, 0.3, c="muted"),
   T(21, 1320, 800, 60, "wafer 2", c="muted", d=0.4))
# 21.5 hands result to wafer two
bd(21.5, wafer(21.5, 500, 500, 200, 0.0), wafer(21.5, 1400, 500, 200, 0.0, rpm=40), packet(21.5, 700, 500, 500, d=0.2, dur=0.8), arr(21.5, 700, 380, 1200, 380, c="red", d=0.1),
   T(21.5, 960, 820, 56, "pass it on!", c="red", d=0.4))
# 22 only small results travel
bd(22, wafer(22, 450, 520, 200, 0.0), wafer(22, 1470, 520, 200, 0.0), [e for q in range(3) for e in packet(22, 650, 460 + 60 * q, 620, d=0.1 + 0.3 * q, dur=0.7)], T(22, 960, 220, 60, "tiny results travel", c="gold", d=0.2))
# 22.5 heavy numbers never move
an = uid("anc")
bd(22.5, wafer(22.5, 700, 480, 260, 0.0, rpm=5), [{"t": "icon", "at": 22.5, "id": an, "name": "block_force", "x": 700, "y": 480, "size": 160, "c": "paper"}, pop(22.5, an, 0.2), pulse(22.5, an, 0.6)],
   T(22.5, 1350, 450, 64, "weights stay put", c="blue", d=0.3), icon(22.5, "magnet", 1350, 680, 160, 0.4, c="red", mv="wig"))
# 23 two microseconds
bd(23, BIG(23, 960, 380, "2 µs", c="red", d=0.0, s=160), T(23, 960, 580, 56, "per hop", c="ink", d=0.2), packet(23, 400, 780, 1100, d=0.2, dur=0.3), packet(23, 400, 850, 1100, d=0.5, dur=0.3),
   icon(23, "fiber", 1600, 700, 160, 0.3, mv="wig"))
# 23.5 blink tens of thousands
ey = uid("eye")
bd(23.5, [{"t": "icon", "at": 23.5, "id": ey, "name": "eye", "x": 550, "y": 500, "size": 300, "c": "ink"}, pop(23.5, ey, 0.0), {"t": "move", "at": 23.5, "kind": "grow", "targets": [ey], "axis": "y", "pivot": [550, 500], "dur": 0.4, "delay": 0.4}],
   BIG(23.5, 1300, 420, "~50,000", c="blue", d=0.3, s=120), T(23.5, 1300, 600, 50, "hops in one blink", c="ink", d=0.5), [e for q in range(3) for e in packet(23.5, 1000, 760, 600, d=0.3 + 0.15 * q, dur=0.3)])
# 24 twist three
bd(24, BIG(24, 960, 200, "Twist 3", c="blue", d=0.0, s=100), chippy(24, 960, 560, 1.1)[0], T(24, 960, 860, 56, "the sneaky one", c="red", d=0.3), icon(24, "eye", 1500, 560, 140, 0.4, mv="wig"))
# 24.5 wafer one starts next request
bd(24.5, wafer(24.5, 500, 500, 200, 0.0, rpm=40), wafer(24.5, 1400, 500, 200, 0.0, rpm=40), packet(24.5, 700, 500, 500, d=0.0, dur=0.6, c="gold"), packet(24.5, 300, 500, 200, d=0.4, dur=0.4, c="red"),
   T(24.5, 500, 800, 50, "next request!", c="red", d=0.4), T(24.5, 1400, 800, 50, "busy", c="blue", d=0.2))
# 25 like a car factory
bd(25, icon(25, "building", 500, 480, 300, 0.0), gear(25, 900, 400, 120, 0.1, 120), gear(25, 1000, 500, 90, 0.2, -160), icon(25, "car", 1400, 520, 220, 0.3, c="red", mv="bob"), T(25, 960, 860, 60, "a car factory", c="ink", d=0.3))
# 25.5 lots of cars at once
cars = []
for q in range(4):
    i = uid("car")
    cars += [{"t": "icon", "at": 25.5, "id": i, "name": "car", "x": 300 + 300 * q, "y": 560, "size": 180, "c": ["red", "blue", "gold", "green"][q]}, pop(25.5, i, 0.1 * q), sh(25.5, i, 300, 0, 0.4, 1.2)]
bd(25.5, [P(25.5, "M150,660 L1770,660", c="ink", w=8, idp=uid("rd"))], cars, T(25.5, 960, 860, 60, "many at once", c="ink", d=0.4))
# 26 24 wafers big layers
bd(26, BIG(26, 600, 400, "24", c="red", d=0.0, s=160), T(26, 600, 600, 50, "big layers", c="red", d=0.1), line(26, 4, 1050, 450, 180, 0.35, d=0.2, c="red"), T(26, 1320, 650, 44, "1 layer each", c="muted", d=0.5))
# 26.5 35 light + 59
bd(26.5, BIG(26.5, 500, 380, "24 + 35", c="ink", d=0.0, s=130), BIG(26.5, 1350, 380, "= 59", c="red", d=0.4, s=150), line(26.5, 7, 380, 700, 190, 0.3, d=0.2, step=0.07), check(26.5, 1700, 380, d=0.6))
# 27 light layers small notebook
nb = uid("nb")
bd(27, [R(27, 700, 350, 260, 320, c="ink", fill="gold", idp=nb), P(27, "M740,420 L920,420 M740,480 L920,480 M740,540 L920,540", c="ink", w=4, idp=nb), pop(27, nb, 0.0), rot(27, nb, 8, (830, 510), 0.4, 0.5)],
   T(27, 1300, 450, 60, "fixed-size notes", c="ink", d=0.3), icon(27, "ruler", 1300, 650, 150, 0.4, mv="wig"))
# 27.5 two share one wafer
lw = uid("lw")
bd(27.5, wafer(27.5, 960, 500, 280, 0.0, rpm=10), [R(27.5, 820, 400, 120, 200, c="ink", fill="gold", idp=lw), R(27.5, 980, 400, 120, 200, c="ink", fill="gold", idp=lw), pop(27.5, lw, 0.3), pulse(27.5, lw, 0.7)],
   T(27.5, 960, 880, 56, "2 layers, 1 wafer", c="ink", d=0.5))
# 28 result: model this huge
bd(28, BIG(28, 960, 300, "3 T", c="blue", d=0.0, s=150), line(28, 6, 460, 600, 200, 0.3, d=0.2, step=0.07), T(28, 960, 860, 56, "a model this huge", c="ink", d=0.4))
# 28.5 1000-2000 tokens/s
bd(28.5, BIG(28.5, 960, 380, "1,000-2,000", c="red", d=0.0, s=130), T(28.5, 960, 560, 56, "tokens per second (target)", c="ink", d=0.2), bar(28.5, 700, 880, 160, 140, "muted", d=0.3), bar(28.5, 1060, 880, 160, 260, "red", d=0.5),
   icon(28.5, "rocket", 1500, 760, 140, 0.4, c="red", mv="wig"))
# 29 fine print company blog
bd(29, T(29, 960, 200, 64, "Friendly fine print", c="red", d=0.0), icon(29, "computer", 600, 520, 240, 0.1, mv="bob"), T(29, 1300, 500, 56, "the company's own blog", c="ink", d=0.3), icon(29, "magnifier", 1300, 700, 140, 0.4, mv="wig"))
# 29.5 plan, not independent test
bd(29.5, icon(29.5, "map_pin", 600, 480, 240, 0.0, c="red"), T(29.5, 600, 720, 56, "a plan", c="ink", d=0.1), icon(29.5, "flask", 1300, 480, 220, 0.2, mv="wig"), cross(29.5, 1300, 480, d=0.4),
   T(29.5, 1300, 720, 50, "independent test: not yet", c="red", d=0.5))
# 30 whole wafer hard to make
bd(30, wafer(30, 800, 500, 280, 0.0), [e for q in range(3) for e in cross(30, 700 + 100 * q, 400 + 90 * q, d=0.2 + 0.15 * q)], T(30, 1450, 450, 60, "defects!", c="red", d=0.3), icon(30, "lens", 1450, 650, 140, 0.4, mv="wig"))
# 30.5 spare cores route around
sp = []
for q in range(9):
    i = uid("sc")
    sp += [R(30.5, 650 + 120 * (q % 3), 300 + 120 * (q // 3), 90, 90, c="ink", fill="red" if q == 4 else "blue", idp=i), pop(30.5, i, 0.04 * q)]
rt = uid("rt")
bd(30.5, sp, [P(30.5, "M695,525 Q815,650 935,525", c="gold", w=8, idp=rt), pop(30.5, rt, 0.5), pulse(30.5, rt, 0.9)], T(30.5, 1450, 450, 56, "spare cores", c="blue", d=0.4), check(30.5, 1450, 620, d=0.7))
# 31 the secret isn't just bigger
bd(31, wafer(31, 600, 500, 220, 0.0), BIG(31, 1300, 400, "bigger?", c="muted", d=0.2, s=110), cross(31, 1300, 400, d=0.5), icon(31, "question", 1300, 680, 140, 0.3, c="red", mv="wig"))
# 31.5 stop running to the fridge
bd(31.5, fridge(31.5, 960, 500, 1.2, 0.0), cross(31.5, 960, 500, d=0.3), T(31.5, 960, 860, 64, "stop running to the fridge", c="red", d=0.4), runner(31.5, 300, 300, 800, d=0.1, dur=0.6))
# 32 moving data
bd(32, [e for q in range(4) for e in packet(32, 300, 380 + 80 * q, 1300, d=0.1 * q, dur=1.6)], T(32, 960, 220, 64, "moving data", c="gold", d=0.2), icon(32, "computer", 1650, 500, 200, 0.3, mv="bob"))
# 32.5 costs more than math
bd(32.5, bar(32.5, 600, 850, 200, 500, "gold", d=0.0), bar(32.5, 1100, 850, 200, 150, "blue", d=0.3), T(32.5, 700, 280, 50, "moving", c="gold", d=0.1), T(32.5, 1200, 620, 50, "math", c="blue", d=0.4),
   BIG(32.5, 1500, 400, ">", c="red", d=0.5, s=150))
# 33 next time AI answers instantly
bd(33, icon(33, "phone", 700, 500, 300, 0.0, mv="bob"), sound(33, 860, 500, 1.0, d=0.2), chippy(33, 1350, 500, 0.9, d=0.3)[0], T(33, 960, 860, 56, "instant answer", c="ink", d=0.4))
# 33.5 thank the chef
bd(33.5, chef(33.5, 700, 620, 1.3)[0], fridge(33.5, 1000, 600, 0.7, 0.2), [e for q in range(4) for e in star(33.5, 1250 + 130 * q, 350, 0.3 + 0.1 * q, r=30)], T(33.5, 1450, 700, 60, "thank you, chef", c="green", d=0.5))

# ---- extra sentences (inserted after old sentence k; their boards use at = 100 + j and 100 + j + 0.5) ----
INS = [
 (11, "这个问题有个名字：|内存墙。", "Engineers have a name for this: | the memory wall."),
 (11, "这些年芯片算得越来越快，|内存送货却跟不上。", "For years, chips got faster at math | much faster than memory got at delivering."),
 (23, "要是参数也得搬来搬去，|那就又回到走廊了。", "If the heavy numbers had to travel too, | we'd be right back in the hallway."),
 (25, "一条59站的流水线，|同时处理好多人的问题。", "A fifty nine station line | serves lots of people's questions at the same time."),
 (28, "对比一下：你读书，|一秒大约读四五个词。", "For comparison: when you read, | you manage maybe four or five words a second."),
 (28, "它一秒写的，|够你读好几分钟。", "What it writes in one second | would take you several minutes to read."),
]
# 100 the memory wall
wl_ = []
for q in range(12):
    i = uid("brk")
    wl_ += [R(100, 900 + 110 * (q % 3) + 55 * ((q // 3) % 2), 250 + 110 * (q // 3), 100, 100, c="ink", fill="red", idp=i), pop(100, i, 0.05 * q)]
bd(100, chippy(100, 450, 520, 1.0, mood="o")[0], wl_, T(100, 960, 900, 56, "engineers have a name", c="ink", d=0.3), icon(100, "magnifier", 1600, 500, 140, 0.4, mv="wig"))
wl_ = []
for q in range(12):
    i = uid("brk")
    wl_ += [R(100.5, 800 + 110 * (q % 3) + 55 * ((q // 3) % 2), 250 + 110 * (q // 3), 100, 100, c="ink", fill="red", idp=i), pop(100.5, i, 0.04 * q)]
p_, pi = chippy(100.5, 400, 520, 0.8, mood="sad")
bd(100.5, wl_, p_, [sh(100.5, pi, 220, 0, 0.3, 0.4), sh(100.5, pi, -120, 0, 0.8, 0.3)], BIG(100.5, 1450, 520, "the MEMORY WALL", c="red", d=0.4, s=80))
# 101 chips faster at math
bd(101, bar(101, 450, 850, 100, 120, "blue", d=0.0), bar(101, 600, 850, 100, 280, "blue", d=0.15), bar(101, 750, 850, 100, 500, "blue", d=0.3), T(101, 600, 250, 56, "math speed", c="blue", d=0.2),
   arr(101, 450, 700, 850, 300, c="blue", d=0.4), gear(101, 1350, 500, 220, 0.2, 200), T(101, 1350, 780, 50, "faster every year", c="ink", d=0.5))
# 101.5 memory can't keep up
bd(101.5, bar(101.5, 450, 850, 100, 120, "blue", d=0.0), bar(101.5, 600, 850, 100, 280, "blue", d=0.0), bar(101.5, 750, 850, 100, 500, "blue", d=0.0),
   bar(101.5, 1100, 850, 100, 100, "gold", d=0.2), bar(101.5, 1250, 850, 100, 140, "gold", d=0.35), bar(101.5, 1400, 850, 100, 180, "gold", d=0.5), T(101.5, 1250, 550, 56, "memory delivery", c="gold", d=0.3),
   T(101.5, 960, 200, 60, "the gap keeps growing", c="red", d=0.6))
# 102 if weights traveled
bd(102, wafer(102, 450, 520, 200, 0.0), wafer(102, 1470, 520, 200, 0.0), [e for q in range(3) for e in packet(102, 650, 400 + 100 * q, 620, d=0.1 + 0.2 * q, dur=0.7, c="red")],
   T(102, 960, 220, 56, "heavy numbers on the move?", c="red", d=0.3))
# 102.5 back in the hallway
bd(102.5, chef(102.5, 350, 600, 0.9, 0.0)[0], fridge(102.5, 1550, 600, 0.9, 0.1), runner(102.5, 480, 700, 1420, d=0.2, dur=1.0), runner(102.5, 480, 620, 1420, d=0.6, dur=1.0),
   T(102.5, 960, 880, 60, "the hallway is back!", c="red", d=0.4))
# 103 a 59-station line
bd(103, line(103, 7, 300, 500, 220, 0.35, d=0.0, step=0.08), [e for q in range(3) for e in packet(103, 300, 650, 1300, d=0.3 + 0.3 * q, dur=1.4)], BIG(103, 960, 850, "59 stations", c="blue", d=0.3, s=100))
# 103.5 lots of people
ppl = []
for q in range(5):
    i = uid("pp")
    x = 400 + 280 * q
    ppl += [O(103.5, x, 420, 45, c="ink", fill="paper", idp=i), P(103.5, f"M{x},465 L{x},600 L{x - 40},700 M{x},600 L{x + 40},700 M{x},500 L{x - 50},560 M{x},500 L{x + 50},560", c="ink", w=6, idp=i),
            pop(103.5, i, 0.1 * q), bob(103.5, i, 8, 1.0 + 0.2 * q)]
bd(103.5, ppl, [e for q in range(5) for e in icon(103.5, "question", 400 + 280 * q, 270, 90, 0.3 + 0.08 * q, c="red", mv="wig")], T(103.5, 960, 860, 56, "many questions at once", c="ink", d=0.6))
# 104 you read 4-5 words a second
bk = uid("bk")
bd(104, [R(104, 450, 350, 360, 280, c="ink", fill="paper", idp=bk), P(104, "M630,350 L630,630", c="ink", w=5, idp=bk), pop(104, bk, 0.0), rot(104, bk, -6, (630, 490), 0.4, 0.5)],
   [O(104, 630, 250, 60, c="ink", fill="paper")], BIG(104, 1350, 420, "4-5 words / s", c="blue", d=0.3, s=100), T(104, 1350, 600, 50, "you, reading", c="ink", d=0.4), icon(104, "eye", 1350, 760, 140, 0.5, mv="wig"))
# 104.5 four or five words a second
wd = []
for q, w_ in enumerate(["the", "cat", "sat", "on", "a"]):
    wd += T(104.5, 450 + 220 * q, 450, 70, w_, c="ink", d=0.2 * q)
bd(104.5, wd, icon(104.5, "eye", 960, 700, 200, 0.0, mv="wig"), arr(104.5, 400, 560, 1500, 560, c="blue", d=0.1, dur=1.2), icon(104.5, "clock", 1650, 300, 140, 0.2, mv="spin"))
# 105 what it writes in one second
bd(105, chippy(105, 500, 520, 1.1)[0], [e for q in range(5) for e in packet(105, 650, 380 + 70 * q, 900, d=0.1 * q, dur=0.6)], BIG(105, 1400, 250, "1 s", c="red", d=0.3, s=120))
# 105.5 minutes to read
pg = []
for q in range(6):
    i = uid("pg")
    pg += [R(105.5, 350 + 200 * q, 330 + 20 * (q % 2), 160, 220, c="ink", fill="paper", idp=i), pop(105.5, i, 0.1 * q), sh(105.5, i, 0, 40, 0.6 + 0.05 * q, 0.4)]
bd(105.5, pg, BIG(105.5, 960, 750, "1 s  =  minutes", c="red", d=0.4, s=100), icon(105.5, "clock", 1700, 400, 140, 0.3, mv="spin"))

S2, MAP, j = [], {}, 0
for k, sent in enumerate(S):
    MAP[k], MAP[k + 0.5] = len(S2), len(S2) + 0.5
    S2.append(sent)
    for q, (after, zh, en) in enumerate(INS):
        if after == k:
            MAP[100 + q], MAP[100 + q + 0.5] = len(S2), len(S2) + 0.5
            S2.append((zh, en))
S = S2
for b in B:
    for e in b:
        e["at"] = MAP[e["at"]]
B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"Cerebras": "Sir rebus", "Chippy": "Chippie", "two microseconds": "two micro seconds"})
