"""每日科普 2026-11-09（中文）：“问 AI 一个问题，它要喝几口水？”
新闻：钛媒体《AI 会撞上的下一堵墙可能是水》（网易 2026-11-09 转载），第十三届“石如对话”（桂林，10 月 29–31 日）水资源分论坛。
热度：新浪科技热点小时报 2026-11-09 11 时第 4 条；同一周新浪财经还有《全球 AI 狂飙，算力中心“喊渴”》（11-03）、
  《选民因资源顾虑否决 AI 数据中心项目》（11-05）、《环保组织陷入 AI 两难》（11-08）。
事实（钛媒体原文，引 WEF、Rystad Energy、北京理工大学团队等）：
  芯片用的电几乎全变成热；AI 机柜功率密度从 3–10 kW 升到 30–100 kW；蒸发冷却是目前最便宜的办法，水蒸发后离开本地流域；
  1 升水蒸发约带走 0.6 kWh 的热（汽化热约 2260 kJ/L）；中型数据中心每天约 100 万升；
  全球冷却用水 2025 年约 2220 亿升 → 2030 年最多 6440 亿升（Rystad）；中国 2030 年约 2628.8 亿升 ≈ 19 个西湖（北理工团队估算）；
  约 45% 的数据中心在高缺水地区（WEF）；挑冷却方案时 87% 考虑节能、只有 35% 考虑节水（WEF 调查）；
  智利圣地亚哥谷歌项目原计划每年约 70 亿升 ≈ 8 万居民一年用水，法院部分撤销许可后改风冷；
  乌兰察布：禁止用地下水冷却，只能用再生水（中水）；单位用水效率（WUE）逐年改善，但总量还在涨。
“几十个问题一瓶 500 毫升水”：Li, Yang, Islam, Ren《Making AI Less "Thirsty"》（arXiv 2304.03271，2023）对 GPT-3 的估算（片中说明是估算）。
我们的比喻/估算（片中说清）：出汗；几十台电暖气塞进衣柜（30–100 kW ÷ 约 2 kW）；100 万升 ≈ 小半个奥运标准泳池（约 250 万升）；省油车越开越远。
出处：
- https://www.163.com/dy/article/LB9J1QK805118O92.html
- https://www.tmtpost.com/8197774.html
- https://k.sina.com.cn/article_7857201856_1d45362c001908u6ak.html
- https://finance.sina.com.cn/jjxw/2026-11-03/doc-inixmhhh2361085.shtml
- https://arxiv.org/abs/2304.03271
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402,F401
                     star, uid, wig)
from popkit import cute_chip, cute_drop, stick  # noqa: E402

S = [
 ("你每问 AI 一个问题，|它可能都在偷偷“喝水”。", "Every question you ask an AI | may come with a secret sip of water."),
 ("一项估算说：聊几十个问题，|就要喝掉一瓶五百毫升的水。", "One estimate: a few dozen questions | can cost a 500 ml bottle of water."),
 ("AI 又没有嘴，|水到底喝到哪去了？", "AI has no mouth. | So where does the water go?"),
 ("今天的烧脑问题：电脑算题，|为什么要用水？", "Today's brain teaser: computers do math. | Why do they need water?"),
 ("认识小芯，一块 AI 芯片。|它吃进去的电，几乎全变成了热。", "Meet Chip, an AI chip. | Almost all the power it eats turns into heat."),
 ("以前一个机柜大约三到十千瓦，|AI 机柜到了三十到一百千瓦。", "An old server rack used about 3 to 10 kilowatts. | An AI rack: 30 to 100."),
 ("相当于把十几到几十台电暖气，|塞进一个衣柜。", "That's like stuffing dozens of space heaters | into one wardrobe."),
 ("不赶紧散热，|芯片就会热到降速，甚至宕机。", "Without cooling, | the chip slows down, or even crashes."),
 ("最省钱的办法：|让小芯“出汗”。", "The cheapest fix: | make Chip sweat."),
 ("人出汗，汗水蒸发，|把身上的热带走。", "When you sweat, the sweat evaporates | and carries heat away."),
 ("数据中心的冷却塔也一样：|让水蒸发，带走热。", "Data center cooling towers do the same: | evaporate water, dump the heat."),
 ("一升水蒸发，|能带走大约零点六度电的热。", "One liter of water evaporating | carries off about 0.6 kilowatt hours of heat."),
 ("反转一：这水不是“用了”，|是“飞走”了。", "Twist one: the water isn't used up. | It flies away."),
 ("它变成水汽飘到天上，|不回本地的河里。", "It becomes vapor in the sky, | not water back in the local river."),
 ("一个中型数据中心，|每天要蒸发大约一百万升水。", "A medium data center | evaporates about a million liters a day."),
 ("我们粗算一下：|差不多是小半个奥运标准泳池。", "Our rough math: | that's close to half an Olympic pool."),
 ("全世界算下来，二零二五年|数据中心冷却用水约二千二百亿升。", "Worldwide in 2025, | data center cooling used about 222 billion liters."),
 ("到二零三零年，|可能涨到六千四百亿升，差不多三倍。", "By 2030 it could hit 644 billion. | Nearly three times as much."),
 ("中国这边，有团队估算二零三零年，|一年要用掉大约十九个西湖的水。", "In China, one team estimates that by 2030, | it's about 19 West Lakes of water a year."),
 ("反转二：越省电，|有时候越费水。", "Twist two: saving power | can cost more water."),
 ("蒸发降温很省电，|所以大家爱用。", "Evaporative cooling saves electricity, | so everyone loves it."),
 ("改用风扇吹、空调冷，|水省了，电就多了。", "Switch to fans and air conditioning: | less water, more power."),
 ("一项调查：八成多的运营商挑冷却方案时考虑省电，|考虑省水的只有三成多。", "One survey: 87 percent of operators think about power, | only 35 percent about water."),
 ("反转三：数据中心爱建在哪？|电便宜、天气凉的地方。", "Twist three: where do data centers go? | Cheap power, cool weather."),
 ("可全球大约百分之四十五的数据中心，|在缺水的地区。", "Yet about 45 percent of them | sit in water-stressed places."),
 ("在智利，谷歌一个项目原计划每年用七十亿升水，|相当于八万人一年的用水。", "In Chile, a Google project planned 7 billion liters a year, | as much as 80,000 people use."),
 ("居民反对、法院介入，|最后改成了风冷。", "Residents objected, a court stepped in, | and it switched to air cooling."),
 ("内蒙古乌兰察布规定：|不准用地下水冷却，只能用再生水。", "Ulanqab in Inner Mongolia now says: | no groundwater for cooling, recycled water only."),
 ("好消息是，每度电用的水|在一年年变少。", "Good news: water per kilowatt hour | keeps dropping."),
 ("坏消息是，AI 长得更快，|总用水量还在涨。", "Bad news: AI grows even faster, | so total water keeps rising."),
 ("这就像你换了辆省油的车，|却越开越远。", "It's like buying a fuel-saving car | and then driving much farther."),
 ("友情提示：一个问题喝多少水是估算，|不同模型、不同地方差很多。", "Fine print: water per question is an estimate. | It varies a lot by model and place."),
 ("用风冷、在冷地方的数据中心，|几乎不怎么喝水。", "Air-cooled data centers in cold places | drink very little."),
 ("所以电脑算题为什么要用水？|因为算力就是热，水是最便宜的“汗”。", "So why does computing need water? | Because compute is heat, and water is the cheapest sweat."),
 ("下次 AI 回答得又快又好，|别忘了它可能出了一身汗。", "Next time AI answers fast, | remember it may have broken a sweat."),
 ("小芯说：多问好问题，|我的汗才没白流。", "Chip says: ask good questions, | so my sweat isn't wasted."),
]
TITLE = {"zh": "问 AI 一个问题，它要喝几口水？", "en": "How Much Water Does Your AI Drink?"}

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


def char(fn, a, x, y, k=1.0, d=0.0, dx=0, dy=0, dur=1.2, dd=0.3, **kw):
    i = uid("ch")
    E = fn(x, y, k, a, idp=i, **kw) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if dx or dy:
        E.append(sh(a, i + "*", dx, dy, d + dd, dur))
    return E


def chip(a, x, y, k=1.0, d=0.0, mood="happy", sweat=0, **kw):
    E = char(cute_chip, a, x, y, k, d, mood=mood, **kw)
    for q in range(sweat):   # sweat drops sliding off
        j = uid("sw")
        sx = x + (1 if q % 2 else -1) * (120 * k + 20)
        E += [P(a, f"M{sx},{y - 40 * k + 50 * q} q-14,26 0,34 q14,-8 0,-34 Z", c="blue", w=4, fill="blue", idp=j), pop(a, j, d + 0.3 + 0.15 * q), sh(a, j, 0, 120, d + 0.5 + 0.15 * q, 1.2)]
    return E


def drop(a, x, y, k=1.0, d=0.0, mood="happy", warm=False, **kw):
    return char(cute_drop, a, x, y, k, d, mood=mood, warm=warm, **kw)


def steam(a, x, y, n=3, d=0.0, rise=300, c="muted"):
    E = []
    for q in range(n):
        j = uid("st")
        xx = x + 60 * (q - (n - 1) / 2)
        E += [P(a, f"M{xx},{y} q25,-30 0,-60 q-25,-30 0,-60", c=c, w=6, idp=j), pop(a, j, d + 0.12 * q), sh(a, j, 0, -rise, d + 0.2 + 0.12 * q, 1.4),
              wig(a, j, (xx, y), 8, 2.5)]
    return E


def ball(a, x, y, dx, dy, d=0.0, c="red", dur=1.0, r=18):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, dur)]


def heat(a, x, y, n=4, d=0.0, c="red"):
    """Wavy heat lines rising."""
    E = []
    for q in range(n):
        j = uid("ht")
        xx = x + 50 * (q - (n - 1) / 2)
        E += [P(a, f"M{xx},{y} q15,-20 0,-40 q-15,-20 0,-40", c=c, w=5, idp=j), pop(a, j, d + 0.08 * q), wig(a, j, (xx, y), 10, 3), sh(a, j, 0, -120, d + 0.3, 1.2)]
    return E


def tower(a, x, y=950, d=0.0):
    """A cooling tower (hourglass) with steam."""
    i = uid("tw")
    return [P(a, f"M{x - 130},{y} Q{x - 60},{y - 200} {x - 100},{y - 380} L{x + 100},{y - 380} Q{x + 60},{y - 200} {x + 130},{y} Z", c="ink", w=6, fill="paper", idp=i),
            pop(a, i, d), wig(a, i, (x, y), 1, 1), steam(a, x, y - 400, 3, d + 0.2, 280)]


def rack(a, x, y, d=0.0, hot=True):
    """A server rack with blinking lights."""
    i = uid("rk")
    E = [R(a, x - 90, y - 300, 180, 300, c="ink", fill="muted", idp=i), pop(a, i, d), wig(a, i, (x, y), 1, 1)]
    for q in range(4):
        j = uid("lt")
        E += [O(a, x - 40, y - 250 + 65 * q, 12, c="green", fill="green", idp=j), pop(a, j, d + 0.1), {"t": "move", "at": a, "kind": "pulse", "targets": [j], "dur": 0.5, "delay": d + 0.3 + 0.2 * q}]
    if hot:
        E += heat(a, x, y - 320, 3, d + 0.3)
    return E


def pool(a, x, y, w, h, d=0.0, frm=1, to=1, c="blue"):
    """Water level in a box; grows/shrinks between from/to."""
    i, j = uid("pb"), uid("pw")
    E = [R(a, x, y - h, w, h, c="ink", idp=i), pop(a, i, d), wig(a, i, (x + w / 2, y), 1, 1),
         R(a, x + 8, y - h * 0.9, w - 16, h * 0.9 - 8, c=c, fill=c, idp=j), pop(a, j, d + 0.1), bob(a, j, 4, 1.3)]
    if frm != to:
        E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x + w / 2, y - 8], "dur": 1.6, "delay": d + 0.3, "from": frm, "to": to})
    return E


def bottle(a, x, y, d=0.0, to=0.2):
    i, j = uid("bt"), uid("bw")
    return [P(a, f"M{x - 50},{y} L{x - 50},{y - 220} Q{x - 50},{y - 260} {x - 20},{y - 280} L{x - 20},{y - 330} L{x + 20},{y - 330} L{x + 20},{y - 280} Q{x + 50},{y - 260} {x + 50},{y - 220} L{x + 50},{y} Z",
              c="ink", w=6, idp=i), pop(a, i, d), wig(a, i, (x, y), 2, 1),
            R(a, x - 42, y - 210, 84, 202, c="blue", fill="blue", idp=j), pop(a, j, d + 0.1),
            {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [x, y - 8], "dur": 1.6, "delay": d + 0.4, "from": 1, "to": to}]


def wardrobe(a, x, y, d=0.0):
    i = uid("wr")
    E = [R(a, x - 200, y - 500, 400, 500, c="ink", fill="paper", idp=i), pop(a, i, d), wig(a, i, (x, y), 2, 3),
         P(a, f"M{x},{y - 500} L{x},{y}", c="ink", w=5, idp=i)]
    for q in range(6):
        j = uid("hr")
        cx, cy = x - 120 + 120 * (q % 3), y - 380 + 200 * (q // 3)
        E += [R(a, cx - 40, cy - 60, 80, 120, c="red", fill="red", idp=j), pop(a, j, d + 0.15 + 0.06 * q), wig(a, j, (cx, cy), 4, 3)]
    return E + heat(a, x, y - 520, 4, d + 0.4)


def car(a, x, y, d=0.0, dx=0):
    i = uid("cr")
    E = [R(a, x - 130, y - 90, 260, 90, c="ink", fill="green", idp=i), P(a, f"M{x - 80},{y - 90} L{x - 50},{y - 150} L{x + 50},{y - 150} L{x + 80},{y - 90}", c="ink", w=5, idp=i),
         O(a, x - 70, y, 32, c="ink", fill="ink", idp=i), O(a, x + 70, y, 32, c="ink", fill="ink", idp=i), pop(a, i, d), wig(a, i, (x, y), 2, 3)]
    if dx:
        E.append(sh(a, i, dx, 0, d + 0.3, 1.8))
    return E


# ---------- boards ----------
bd(0, chip(0, 700, 550, 1.4, 0.0, sweat=3), drop(0, 1300, 500, 0.9, 0.2, dx=-450, dy=0, dur=1.0, dd=0.6), big(0, 1350, 850, "AI 在喝水？", c="blue", d=0.3, s=110))
bd(0.5, man(0.5, 500, 950, 1.4, 0.0, arms="up"), ic(0.5, "computer", 1000, 600, 260, 0.1, mv="bob"), drop(0.5, 1450, 450, 0.6, 0.3, dx=-350, dy=150, dur=1.0), steam(0.5, 1000, 400, 3, 0.4))
bd(1, t(1, 960, 230, 54, "一项估算", c="muted", d=0.0), [ic(1, "question", 450 + 170 * q, 550, 120, 0.05 * q, mv="wig", c="red") for q in range(4)], bottle(1, 1450, 900, 0.2, to=0.1))
bd(1.5, bottle(1.5, 650, 950, 0.0, to=0.05), big(1.5, 1250, 400, "500 ml", c="blue", d=0.2, s=150), big(1.5, 1250, 650, "≈ 几十个问题", c="red", d=0.4, s=80))
bd(2, chip(2, 700, 550, 1.3, 0.0, mood="o"), ic(2, "question", 1300, 450, 240, 0.2, mv="wig", c="red"), cross(2, 700, 820, d=0.3))
bd(2.5, drop(2.5, 700, 650, 1.2, 0.0, mood="o", dy=-80, dur=1.4), ic(2.5, "question", 1300, 550, 260, 0.2, mv="wig", c="red"), steam(2.5, 700, 330, 3, 0.4))
bd(3, big(3, 960, 230, "烧脑问题", c="red", d=0.0, s=130), ic(3, "computer", 650, 650, 260, 0.1), ic(3, "water", 1300, 650, 240, 0.2, mv="bob", c="blue"), arr(3, 850, 650, 1150, 650, c="red", d=0.3))
bd(3.5, chip(3.5, 600, 600, 1.1, 0.0), t(3.5, 1250, 450, 80, "1 + 1 = ?", c="blue", d=0.2), drop(3.5, 1300, 750, 0.7, 0.3, mood="o"), ic(3.5, "question", 1600, 450, 140, 0.4, mv="wig", c="red"))
bd(4, chip(4, 960, 580, 2.0, 0.0), big(4, 960, 230, "小芯", c="blue", d=0.2, s=120), star(4, 500, 600, 0.3, r=40), star(4, 1420, 600, 0.4, r=40))
bd(4.5, ic(4.5, "battery", 400, 600, 200, 0.0, mv="wig", c="green"), arr(4.5, 550, 600, 750, 600, c="gold", d=0.2), chip(4.5, 960, 600, 1.0, 0.1, mood="o"), heat(4.5, 960, 400, 4, 0.3),
   ic(4.5, "thermometer", 1450, 600, 240, 0.4, mv="wig", c="red"))
bd(5, rack(5, 600, 900, 0.0, hot=False), big(5, 600, 300, "3–10 kW", c="blue", d=0.2, s=90), rack(5, 1300, 900, 0.3), big(5, 1300, 300, "30–100 kW", c="red", d=0.5, s=90))
bd(5.5, bar(5.5, 600, 950, 240, 120, "blue", 0.0), t(5.5, 720, 1010, 40, "以前"), bar(5.5, 1100, 950, 240, 650, "red", 0.3, 1.4), t(5.5, 1220, 1010, 40, "AI 机柜"), heat(5.5, 1220, 280, 4, 0.8))
bd(6, [ic(6, "flame", 400 + 140 * q, 600, 110, 0.06 * q, mv="wig", c="red") for q in range(5)], arr(6, 1100, 600, 1300, 600, c="ink", d=0.3), wardrobe(6, 1550, 900, 0.4))
bd(6.5, wardrobe(6.5, 700, 950, 0.0), ic(6.5, "thermometer", 1300, 600, 280, 0.2, mv="wig", c="red"), big(6.5, 1350, 250, "热！", c="red", d=0.4, s=150))
bd(7, chip(7, 700, 550, 1.4, 0.0, mood="sad", sweat=4), ic(7, "thermometer", 1300, 550, 300, 0.2, mv="wig", c="red"), heat(7, 700, 300, 4, 0.3))
bd(7.5, P(7.5, "M400,350 L800,350 L1100,700 L1500,900", c="red", w=10, idp="slw"), pop(7.5, "slw", 0.0), chip(7.5, 400, 300, 0.4, 0.1, mood="sad", dx=1100, dy=550, dur=1.8),
   t(7.5, 1300, 400, 60, "降速", c="red", d=0.3), cross(7.5, 1550, 750, d=0.8))
bd(8, t(8, 960, 230, 60, "最省钱的办法", c="muted", d=0.0), chip(8, 960, 600, 1.4, 0.1, mood="o", sweat=4), ic(8, "check", 1450, 550, 160, 0.4, mv="wig", c="green"))
bd(8.5, chip(8.5, 700, 600, 1.5, 0.0, sweat=6), big(8.5, 1350, 450, "出汗", c="blue", d=0.2, s=170), drop(8.5, 1350, 800, 0.5, 0.4))
bd(9, man(9, 700, 950, 1.8, 0.0, arms="up", amp=6), [ball(9, 640 + 40 * q, 500, 0, 300, 0.3 + 0.12 * q, c="blue", r=14) for q in range(4)], steam(9, 700, 380, 3, 0.4), ic(9, "sun", 1400, 400, 220, 0.2, mv="spin", c="gold"))
bd(9.5, drop(9.5, 700, 650, 1.2, 0.0, warm=True), steam(9.5, 700, 380, 3, 0.2, rise=250), heat(9.5, 1200, 700, 4, 0.3), arr(9.5, 900, 450, 1100, 300, c="red", d=0.4))
bd(10, tower(10, 960, 950, 0.0), rack(10, 450, 950, 0.1), arr(10, 560, 700, 820, 700, c="red", d=0.3), drop(10, 1450, 700, 0.6, 0.3))
bd(10.5, tower(10.5, 700, 950, 0.0), tower(10.5, 1250, 950, 0.2), [ball(10.5, 960, 400, -200 + 100 * q, -250, 0.3 + 0.1 * q, c="muted", r=16) for q in range(4)])
bd(11, drop(11, 600, 600, 1.4, 0.0, dy=-250, dur=1.6, dd=0.6), steam(11, 600, 350, 3, 0.4, rise=200), big(11, 1250, 400, "1 升", c="blue", d=0.2, s=150))
bd(11.5, big(11.5, 960, 330, "≈ 0.6 度电的热", c="red", d=0.0, s=120), ic(11.5, "flame", 600, 750, 200, 0.2, mv="wig", c="red"), arr(11.5, 750, 750, 1150, 750, c="blue", d=0.3),
   drop(11.5, 1350, 750, 0.6, 0.4))
bd(12, big(12, 960, 230, "反转一", c="red", d=0.0, s=140), drop(12, 960, 650, 1.3, 0.1, mood="o", dy=-150, dur=1.4, dd=0.8), [ic(12, "wind", 600 + 720 * q, 600, 140, 0.2 + 0.1 * q, mv="wig", c="blue") for q in range(2)])
bd(12.5, pool(12.5, 500, 950, 400, 300, 0.0, 1, 0.3), steam(12.5, 700, 600, 4, 0.3, rise=350), big(12.5, 1350, 450, "飞走了", c="blue", d=0.4, s=140))
bd(13, ic(13, "cloud", 1300, 300, 260, 0.0, mv="bob", c="muted"), steam(13, 700, 750, 4, 0.1, rise=400), drop(13, 700, 850, 0.5, 0.2, dx=500, dy=-500, dur=1.6))
bd(13.5, P(13.5, "M200,850 Q600,780 960,860 Q1320,940 1720,850", c="blue", w=14, idp="rvr"), pop(13.5, "rvr", 0.0), wig(13.5, "rvr", (960, 850), 4, 1.5), cross(13.5, 960, 650, d=0.3),
   drop(13.5, 960, 300, 0.6, 0.2, mood="sad", dx=300, dy=-100), ic(13.5, "cloud", 1450, 250, 180, 0.3, mv="bob", c="muted"))
bd(14, rack(14, 500, 950, 0.0), rack(14, 750, 950, 0.1), tower(14, 1300, 950, 0.2))
bd(14.5, big(14.5, 960, 300, "100 万升 / 天", c="red", d=0.0, s=130), [drop(14.5, 450 + 200 * q, 750, 0.45, 0.2 + 0.06 * q, dy=-200, dur=1.2) for q in range(6)])
bd(15, t(15, 960, 230, 60, "我们粗算", c="muted", d=0.0), pool(15, 400, 900, 1100, 350, 0.1, 0.1, 0.45), man(15, 1650, 900, 1.0, 0.2, arms="up"))
bd(15.5, big(15.5, 960, 300, "≈ 小半个奥运泳池", c="blue", d=0.0, s=100), pool(15.5, 400, 950, 1100, 320, 0.1, 1, 0.4), [ball(15.5, 600 + 200 * q, 700, 0, -40, 0.3 + 0.08 * q, c="paper", r=20) for q in range(4)])
bd(16, ic(16, "globe", 600, 600, 320, 0.0, mv="spin", c="blue"), [tower(16, 1150 + 260 * q, 950, 0.15 * q) for q in range(3)])
bd(16.5, big(16.5, 960, 330, "2220 亿升", c="blue", d=0.0, s=150), t(16.5, 960, 560, 44, "2025 年 · 全球", c="muted", d=0.2), [drop(16.5, 500 + 230 * q, 830, 0.4, 0.3 + 0.06 * q) for q in range(5)])
bd(17, bar(17, 600, 950, 240, 200, "blue", 0.0), t(17, 720, 1010, 40, "2025"), bar(17, 1100, 950, 240, 580, "red", 0.3, 1.4), t(17, 1220, 1010, 40, "2030"), big(17, 1220, 280, "6440 亿", c="red", d=0.7, s=80))
bd(17.5, big(17.5, 960, 330, "× 3", c="red", d=0.0, s=240), arr(17.5, 500, 900, 1400, 550, c="red", d=0.2), [ball(17.5, 600 + 200 * q, 950, 0, -100 * q - 80, 0.3 + 0.06 * q, c="blue") for q in range(5)])
bd(18, ic(18, "map_pin", 600, 550, 240, 0.0, mv="bob", c="red"), t(18, 600, 820, 54, "中国 · 2030", c="red", d=0.1), [rack(18, 1050 + 220 * q, 900, 0.1 + 0.1 * q) for q in range(3)])
bd(18.5, [pool(18.5, 300 + 270 * (q % 5), 600 + 300 * (q // 5), 220, 140, 0.05 * q) for q in range(5)], big(18.5, 960, 900, "≈ 19 个西湖", c="blue", d=0.4, s=110), t(18.5, 960, 260, 44, "团队估算", c="muted", d=0.3))
bd(19, big(19, 960, 230, "反转二", c="red", d=0.0, s=140), ic(19, "battery", 650, 650, 220, 0.1, mv="wig", c="green"), ic(19, "water", 1300, 650, 220, 0.2, mv="bob", c="blue"),
   R(19, 760, 850, 400, 24, c="ink", fill="muted", idp="sw19"), pop(19, "sw19", 0.3), rot(19, "sw19", 15, (960, 862), 0.5, 1.0))
bd(19.5, R(19.5, 560, 600, 800, 30, c="ink", fill="muted", idp="bm"), pop(19.5, "bm", 0.0), rot(19.5, "bm", -15, (960, 615), 0.3, 1.2), ic(19.5, "battery", 650, 470, 160, 0.1, mv="wig", c="green"),
   drop(19.5, 1270, 470, 0.7, 0.2), P(19.5, "M900,900 L960,620 L1020,900 Z", c="ink", w=6, idp="ful"), pop(19.5, "ful", 0.0))
bd(20, tower(20, 700, 950, 0.0), ic(20, "battery", 1300, 600, 220, 0.2, mv="wig", c="green"), check(20, 1300, 850, d=0.4))
bd(20.5, [man(20.5, 450 + 250 * q, 950, 1.0, 0.06 * q, arms="up", amp=6) for q in range(5)], tower(20.5, 1650, 950, 0.3), t(20.5, 900, 300, 60, "大家都爱", c="blue", d=0.2))
bd(21, ic(21, "gear", 600, 600, 240, 0.0, mv="spin"), ic(21, "wind", 1000, 600, 200, 0.1, mv="wig", c="blue"), rack(21, 1450, 900, 0.2, hot=False))
bd(21.5, bar(21.5, 600, 950, 240, 160, "blue", 0.0), t(21.5, 720, 1010, 40, "水 ↓"), bar(21.5, 1100, 950, 240, 520, "gold", 0.3, 1.2), t(21.5, 1220, 1010, 40, "电 ↑"),
   ic(21.5, "battery", 1220, 300, 140, 0.5, mv="wig", c="red"))
bd(22, big(22, 700, 350, "87%", c="green", d=0.0, s=180), ic(22, "battery", 700, 700, 220, 0.2, mv="wig", c="green"), [man(22, 1150 + 120 * q, 950, 0.6, 0.2 + 0.04 * q, amp=6) for q in range(5)])
bd(22.5, big(22.5, 700, 350, "35%", c="blue", d=0.0, s=180), drop(22.5, 700, 700, 0.8, 0.2, mood="sad"), bar(22.5, 1200, 950, 160, 520, "green", 0.2), bar(22.5, 1450, 950, 160, 210, "blue", 0.4),
   t(22.5, 1280, 1010, 36, "省电"), t(22.5, 1530, 1010, 36, "省水"))
bd(23, big(23, 960, 230, "反转三", c="red", d=0.0, s=140), ic(23, "map_pin", 960, 650, 260, 0.1, mv="bob", c="red"), ic(23, "question", 1400, 600, 180, 0.3, mv="wig", c="red"), rack(23, 550, 950, 0.2))
bd(23.5, ic(23.5, "battery", 600, 500, 200, 0.0, mv="wig", c="green"), t(23.5, 600, 750, 54, "电便宜", c="green", d=0.1), ic(23.5, "thermometer", 1300, 500, 220, 0.2, mv="wig", c="blue"),
   t(23.5, 1300, 750, 54, "天气凉", c="blue", d=0.3), check(23.5, 960, 500, d=0.4))
bd(24, ic(24, "globe", 700, 600, 340, 0.0, mv="spin", c="blue"), big(24, 1350, 450, "45%", c="red", d=0.2, s=180), ic(24, "sun", 1350, 800, 180, 0.4, mv="spin", c="gold"))
bd(24.5, P(24.5, "M300,900 L500,850 L620,920 L800,870 L1000,930 L1200,860 L1400,920 L1620,870", c="gold", w=8, idp="crk"), pop(24.5, "crk", 0.0), wig(24.5, "crk", (960, 900), 2, 1),
   drop(24.5, 960, 550, 1.0, 0.1, mood="sad"), ic(24.5, "sun", 1500, 350, 220, 0.2, mv="spin", c="gold"), t(24.5, 500, 400, 60, "缺水", c="red", d=0.3))
bd(25, ic(25, "map_pin", 450, 500, 200, 0.0, mv="bob", c="red"), t(25, 450, 750, 54, "智利", c="red", d=0.1), big(25, 1200, 400, "70 亿升 / 年", c="blue", d=0.2, s=110), tower(25, 1200, 1000, 0.3))
bd(25.5, [man(25.5, 350 + 150 * q, 950, 0.7, 0.04 * q, amp=6) for q in range(9)], big(25.5, 960, 330, "≈ 8 万人", c="red", d=0.4, s=150))
bd(26, [man(26, 450 + 200 * q, 950, 1.0, 0.05 * q, arms="up", amp=8) for q in range(4)], cross(26, 1350, 500, d=0.3), ic(26, "building", 1500, 750, 240, 0.2, mv="bob"))
bd(26.5, ic(26.5, "wind", 600, 600, 260, 0.0, mv="wig", c="blue"), rack(26.5, 1100, 900, 0.1, hot=False), [ball(26.5, 300, 500 + 70 * q, 700, 0, 0.2 + 0.1 * q, c="blue", r=14) for q in range(4)],
   t(26.5, 1500, 400, 60, "改风冷", c="blue", d=0.4))
bd(27, ic(27, "map_pin", 600, 500, 220, 0.0, mv="bob", c="red"), t(27, 600, 780, 54, "乌兰察布", c="red", d=0.1), rack(27, 1150, 950, 0.2), rack(27, 1400, 950, 0.3))
bd(27.5, pool(27.5, 400, 950, 400, 250, 0.0), cross(27.5, 600, 550, d=0.2), t(27.5, 600, 1010, 40, "地下水"), pool(27.5, 1100, 950, 400, 250, 0.2, c="green"), check(27.5, 1300, 550, d=0.4),
   t(27.5, 1300, 1010, 40, "再生水"))
bd(28, big(28, 960, 230, "好消息", c="green", d=0.0, s=130), bar(28, 500, 950, 180, 500, "blue", 0.1), bar(28, 800, 950, 180, 380, "blue", 0.2), bar(28, 1100, 950, 180, 260, "blue", 0.3),
   bar(28, 1400, 950, 180, 150, "green", 0.4))
bd(28.5, drop(28.5, 700, 600, 1.2, 0.0), arr(28.5, 1100, 400, 1300, 800, c="green", d=0.2), t(28.5, 1400, 300, 54, "每度电的水 ↓", c="green", d=0.3))
bd(29, big(29, 960, 230, "坏消息", c="red", d=0.0, s=130), chip(29, 600, 650, 0.6, 0.1, dx=0), chip(29, 960, 650, 0.9, 0.2), chip(29, 1400, 650, 1.3, 0.3))
bd(29.5, P(29.5, "M300,900 C700,880 1100,700 1600,300", c="red", w=10, idp="tot"), pop(29.5, "tot", 0.0), drop(29.5, 300, 850, 0.4, 0.1, dx=1250, dy=-500, dur=1.8), big(29.5, 800, 350, "总量 ↑", c="red", d=0.3, s=120))
bd(30, car(30, 500, 800, 0.0, dx=900), ic(30, "check", 500, 450, 160, 0.2, mv="wig", c="green"), t(30, 960, 250, 60, "省油车", c="green", d=0.2))
bd(30.5, car(30.5, 300, 850, 0.0, dx=1300), P(30.5, "M200,920 L1750,920", c="ink", w=6, idp="rd"), pop(30.5, "rd", 0.0), [ic(30.5, "map_pin", 600 + 400 * q, 600, 120, 0.3 + 0.2 * q, mv="bob", c="red") for q in range(3)],
   t(30.5, 960, 300, 60, "越开越远", c="red", d=0.4))
bd(31, big(31, 960, 230, "友情提示", c="blue", d=0.0, s=130), big(31, 960, 480, "估算", c="red", d=0.2, s=150), [ic(31, "question", 600 + 240 * q, 800, 120, 0.3 + 0.08 * q, mv="wig", c="red") for q in range(4)])
bd(31.5, [chip(31.5, 450 + 340 * q, 600, 0.6, 0.06 * q, mood=("happy", "o", "sad", "happy")[q], sweat=q) for q in range(4)], ic(31.5, "globe", 1650, 900, 140, 0.3, mv="spin", c="blue"))
bd(32, ic(32, "wind", 600, 550, 260, 0.0, mv="wig", c="blue"), ic(32, "thermometer", 1000, 550, 220, 0.1, mv="wig", c="blue"), chip(32, 1450, 550, 0.9, 0.2), [ball(32, 300, 400 + 60 * q, 1000, 0, 0.3 + 0.1 * q, c="blue", r=12) for q in range(3)])
bd(32.5, bottle(32.5, 700, 950, 0.0, to=0.9), chip(32.5, 1300, 600, 1.0, 0.1), check(32.5, 1300, 300, d=0.4), t(32.5, 700, 330, 54, "几乎不喝", c="blue", d=0.3))
bd(33, chip(33, 700, 600, 1.3, 0.0, mood="o"), ic(33, "water", 1300, 600, 240, 0.2, mv="bob", c="blue"), ic(33, "question", 1000, 300, 160, 0.3, mv="wig", c="red"))
bd(33.5, chip(33.5, 600, 600, 1.2, 0.0, sweat=6), big(33.5, 1300, 380, "算力 = 热", c="red", d=0.2, s=120), big(33.5, 1300, 650, "水 = 汗", c="blue", d=0.5, s=120))
bd(34, man(34, 600, 950, 1.5, 0.0, arms="up", amp=6), ic(34, "computer", 1200, 600, 260, 0.2), [check(34, 1100 + 120 * q, 350, d=0.3 + 0.1 * q) for q in range(3)])
bd(34.5, chip(34.5, 960, 600, 1.6, 0.0, sweat=8), heat(34.5, 960, 330, 4, 0.2), star(34.5, 500, 500, 0.3, r=40), star(34.5, 1420, 500, 0.4, r=40))
bd(35, chip(35, 700, 600, 1.4, 0.0), ic(35, "question", 1300, 400, 200, 0.2, mv="wig", c="blue"), check(35, 1300, 700, d=0.4))
bd(35.5, chip(35.5, 600, 600, 1.2, 0.0, sweat=4), drop(35.5, 1300, 600, 1.0, 0.2), star(35.5, 960, 350, 0.3, r=50), t(35.5, 960, 950, 60, "汗没白流", c="blue", d=0.4))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"AI": "A I", "kW": "千瓦"})
