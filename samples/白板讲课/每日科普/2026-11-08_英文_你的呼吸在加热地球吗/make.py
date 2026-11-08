"""Daily science 2026-11-08 (English): "Is Your Breath Heating the Planet?"
News: a global study in The Lancet Planetary Health (University of Bath, lead author Prof. Javier Gonzalez; release 2026-10-28) estimates
  human metabolism produced 2.05 billion tonnes of CO2 in 2015, up from 1.18 billion tonnes in 1985 (+74%); more than 60% of the rise is
  population growth; built from thousands of real-world measurements plus population and body-weight data.
  The researchers: "We're not saying that breathing is driving climate change" -- breath carbon comes from food that plants recently took
  from the air, unlike fossil carbon stored underground for millions of years; the point is better carbon accounting.
Trending: ScienceDaily "Human bodies produce 2 billion metric tons of CO2 a year just by staying alive" (listed in Daily Kos Science Saturday
  digest 2026-11-07); also SciTechDaily, Lifeboat, Canberra Times, notre-planete.
Other facts: exhaled air is about 4% CO2 vs about 0.04% in inhaled air (textbook physiology); Meerman & Brown, BMJ 2014: of fat lost,
  about 84% leaves as CO2 through the lungs and 16% as water; fossil CO2 emissions are roughly 37-38 billion tonnes a year (Global Carbon Project).
Ours (said as estimates in the film): ~0.75 kg of CO2 per person per day averaged over everyone (2.05e9 t / ~7.4e9 people / 365);
  fossil emissions ~18x all breathing; pen-borrowing metaphor.
Sources:
- https://www.bath.ac.uk/announcements/human-metabolism-produces-two-billion-tonnes-of-co2-a-year-global-study-finds/
- https://www.dailykos.com/stories/2026/11/7/800120986/community/overnight-news-digest-science-saturday-10-3-26/
- https://scitechdaily.com/?p=536415
- https://www.bmj.com/content/349/bmj.g7257 (Meerman & Brown 2014)
"""
import math
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402,F401
                     star, uid, wig)
from popkit import cute_puff, stick  # noqa: E402

S = [
 ("全人类每年呼出|二十亿吨二氧化碳。", "Humanity breathes out | two billion tons of carbon dioxide a year."),
 ("这是《柳叶刀·星球健康》|刚发表的一项全球估算。", "That's a new global estimate | in The Lancet Planetary Health."),
 ("1985 年大约十二亿吨，|三十年涨了百分之七十四。", "In nineteen eighty five it was about one point two billion tons. | Up seventy four percent in thirty years."),
 ("涨的六成多，|是因为人变多了。", "Most of that rise | is simply because there are more of us."),
 ("今天的烧脑问题：你每呼一口气，|是不是都在给地球加热？", "So today's brain teaser: every time you exhale, | are you heating the planet?"),
 ("认识主角：小呼，|你刚呼出的那一口气。", "Meet our hero, Puff: | the breath you just let out."),
 ("小呼里大约百分之四是二氧化碳，|是吸进来的空气的一百倍。", "Puff is about four percent carbon dioxide, | a hundred times more than the air you breathed in."),
 ("这些碳从哪来？|你的午饭。", "Where does that carbon come from? | Your lunch."),
 ("细胞用氧气“烧”食物，|像一堆很慢、很温柔的火。", "Your cells burn food with oxygen, | like a very slow, very gentle fire."),
 ("烧出来的是能量、水，|和二氧化碳。", "Out come energy, water, | and carbon dioxide."),
 ("反转一：你减掉的脂肪，|去哪了？", "Twist one: when you lose fat, | where does it go?"),
 ("大部分从嘴里呼出去了。|一项研究算出约百分之八十四变成了二氧化碳。", "Mostly out of your mouth. | One study found about eighty four percent leaves as carbon dioxide."),
 ("剩下的变成水。|所以减肥，真的是“呼”掉的。", "The rest leaves as water. | So yes, you breathe weight away."),
 ("我们粗算一下：平均每人每天|呼出大约四分之三公斤。", "Our rough math: averaged over everyone, | that's about three quarters of a kilo per person per day."),
 ("反转二：这些碳，|几个月前还在天上。", "Twist two: that carbon | was up in the sky just months ago."),
 ("植物从空气里抓住它，|变成米饭、面条，或者牛吃的草。", "A plant grabbed it from the air | and turned it into rice, bread, or grass for a cow."),
 ("你吃下去，|又把它还给了天空。", "You ate it, | and gave it back to the sky."),
 ("这是一个圈，|就像借了支笔，马上又还回去。", "It's a loop, | like borrowing a pen and handing it right back."),
 ("化石燃料不一样：|那些碳在地下锁了几百万年。", "Fossil fuels are different: | that carbon was locked underground for millions of years."),
 ("烧了就是单程票：|天上凭空多出新的碳。", "Burning it is a one way trip: | brand new carbon, added to the sky."),
 ("比一比：化石燃料每年排放|大约三百八十亿吨。", "For scale: fossil fuels emit | about thirty eight billion tons a year."),
 ("差不多是全人类呼吸的|十八倍。", "That's roughly eighteen times | all of humanity's breathing."),
 ("反转三：研究者说，|呼吸还是值得算一算。", "Twist three: the researchers say | breath is still worth counting."),
 ("不是因为呼吸在推动气候变化，|他们明说：不是。", "Not because breathing drives climate change. | They say plainly that it doesn't."),
 ("而是因为碳的账本，|每一笔进出都该记清楚。", "But because a carbon ledger | should track every flow in and out."),
 ("我们自己多想一步：|种粮、运粮、做饭，可是要烧不少化石燃料。", "Our own extra thought: | growing, shipping and cooking food burns plenty of fossil fuel."),
 ("还有：一屋子人开会，|二氧化碳读数就一路往上爬。", "And here's one you can see: | pack a room with people, and the carbon dioxide meter climbs."),
 ("呼吸其实是光合作用倒着放：|植物用阳光把碳装进糖里，你把它拆开取能量。", "Breathing is photosynthesis in reverse: | plants pack carbon into sugar with sunlight, and you unpack it for energy."),
 ("所以你身上的每一分力气，|说到底都是借来的阳光。", "So every bit of energy you have | is really borrowed sunlight."),
 ("牛、狗、猫也都在呼气，|同一个圈，同样是借来的碳。", "Cows, dogs and cats breathe out too. | Same loop, same borrowed carbon."),
 ("真正让账本失衡的，|是从地下挖出来的那部分。", "What tips the ledger | is the carbon we dig up from underground."),
 ("天上的二氧化碳越来越多，|主要就是这笔单程账。", "The rising carbon dioxide in the sky | comes mainly from that one way trip."),
 ("友情提示：二十亿吨是估算，|靠的是几千次实测加上人口和体重数据。", "Fine print: two billion tons is an estimate, | built from thousands of measurements plus population data."),
 ("而且，人多了在呼吸，|可不是什么要“解决”的问题。", "And more people breathing | is not a problem to fix."),
 ("所以，你的呼吸在加热地球吗？|基本不会。那是在转圈的碳。", "So, is your breath heating the planet? | Not really. It's carbon on a round trip."),
 ("小呼说：我是循环再用的。|排气管可不是。", "Puff says: I'm recycled. | The tailpipe isn't."),
]
TITLE = {"zh": "你的呼吸在加热地球吗？", "en": "Is Your Breath Heating the Planet?"}

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
    return T(a, x, y, s * 1.5, text, c=c, d=d, font="en")


def big(a, x, y, text, c="red", d=0.0, s=140):
    return BIG(a, x, y, text, c=c, d=d, s=s, font="en")


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def man(a, x, y, k=1.4, d=0.0, arms="down", amp=3):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": amp, "hz": 1.6}]


def puff(a, x, y, k=1.0, d=0.0, mood="happy", dx=0, dy=0, dur=1.2):
    i = uid("pf")
    E = cute_puff(x, y, k, a, idp=i, mood=mood) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if dx or dy:
        E.append(sh(a, i + "*", dx, dy, d + 0.3, dur))
    return E


def ball(a, x, y, dx, dy, d=0.0, c="red", dur=1.0, r=18):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, dur)]


def co2(a, x, y, d=0.0, dx=0, dy=-250, dur=1.4, k=1.0):
    """A CO2 molecule (O=C=O) drifting."""
    i = uid("co")
    E = [O(a, x, y, 26 * k, c="ink", fill="muted", idp=i), O(a, x - 46 * k, y, 20 * k, c="ink", fill="red", idp=i), O(a, x + 46 * k, y, 20 * k, c="ink", fill="red", idp=i),
         pop(a, i, d), wig(a, i, (x, y), 12, 2.5)]
    if dx or dy:
        E.append(sh(a, i, dx, dy, d + 0.2, dur))
    return E


def breath(a, x, y, n=4, d=0.0, dx=300, dy=-120):
    return [co2(a, x, y + 40 * (q % 2), d + 0.18 * q, dx=dx, dy=dy - 30 * q, dur=1.2, k=0.8) for q in range(n)]


def head(a, x, y, d=0.0, mood="happy"):
    """A profile head facing right with an open mouth (for breathing out)."""
    i = uid("hd")
    m = f"M{x + 60},{y + 30} Q{x + 85},{y + 40} {x + 60},{y + 50}" if mood == "o" else f"M{x + 40},{y + 40} Q{x + 65},{y + 55} {x + 85},{y + 35}"
    return [O(a, x, y, 110, c="ink", fill="paper", idp=i), O(a, x + 40, y - 30, 12, c="ink", fill="ink", idp=i), P(a, m, c="ink", w=5, idp=i),
            pop(a, i, d), wig(a, i, (x, y + 110), 3, 1.2)]


def plant(a, x, y, d=0.0, k=1.0):
    i = uid("pl")
    return [P(a, f"M{x},{y} L{x},{y - 220 * k} M{x},{y - 90 * k} Q{x - 90 * k},{y - 150 * k} {x - 110 * k},{y - 90 * k} Q{x - 50 * k},{y - 70 * k} {x},{y - 90 * k} "
                 f"M{x},{y - 160 * k} Q{x + 90 * k},{y - 220 * k} {x + 110 * k},{y - 160 * k} Q{x + 50 * k},{y - 140 * k} {x},{y - 160 * k}", c="green", w=7, idp=i),
            pop(a, i, d), wig(a, i, (x, y), 6, 1.2)]


def loop(a, x, y, r, d=0.0, c="green", n=3):
    """A circular cycle arrow with dots running round it."""
    i = uid("lp")
    E = [O(a, x, y, r, c=c, idp=i, sw=6), pop(a, i, d), wig(a, i, (x, y), 1, 0.6)]
    for q in range(n):
        j = uid("ld")
        ang = 2 * math.pi * q / n
        E += [O(a, x + r * math.cos(ang), y + r * math.sin(ang), 20, c="ink", fill=c, idp=j), pop(a, j, d + 0.1 + 0.08 * q), spin(a, j, (x, y), 30)]
    return E


def chimney(a, x, y=950, d=0.0):
    i = uid("ch")
    return [R(a, x - 60, y - 340, 120, 340, c="ink", fill="muted", idp=i), pop(a, i, d), wig(a, i, (x, y), 1, 1),
            bubbles(a, x, y - 360, 4, d + 0.2, 300, "muted")]


def meter(a, x, y, d=0.0, to=0.9):
    i, j = uid("mt"), uid("nd")
    return [R(a, x - 150, y - 100, 300, 160, c="ink", fill="paper", idp=i), pop(a, i, d), wig(a, i, (x, y), 1, 1),
            P(a, f"M{x},{y + 40} L{x - 100},{y - 40}", c="red", w=8, idp=j), pop(a, j, d + 0.1), rot(a, j, 120 * to, (x, y + 40), d + 0.4, 1.8)]


# ---------- boards ----------
bd(0, head(0, 450, 600, 0.0, mood="o"), breath(0, 590, 610, 5, 0.2, dx=700, dy=150), big(0, 1150, 330, "2,000,000,000 t", c="red", d=0.4, s=95))
bd(0.5, ic(0.5, "globe", 960, 550, 360, 0.0, mv="spin", c="blue"), [co2(0.5, 600 + 180 * q, 900, 0.1 + 0.07 * q, dy=-300) for q in range(5)], t(0.5, 960, 200, 64, "CO2 every year", c="red", d=0.3))
bd(1, R(1, 650, 350, 600, 450, c="ink", fill="paper", idp="mag"), pop(1, "mag", 0.0), wig(1, "mag", (950, 800), 2, 1), t(1, 950, 450, 54, "The Lancet", c="red", d=0.2),
   t(1, 950, 560, 40, "Planetary Health", c="blue", d=0.3), ic(1, "magnifier", 1450, 650, 200, 0.3, mv="wig"))
bd(1.5, ic(1.5, "globe", 600, 550, 280, 0.0, mv="spin", c="blue"), [man(1.5, 1100 + 150 * q, 950, 0.7, 0.1 + 0.05 * q, amp=6) for q in range(5)], t(1.5, 1400, 400, 60, "global estimate", c="blue", d=0.3))
bd(2, bar(2, 600, 950, 260, 300, "blue", 0.0), t(2, 730, 1010, 40, "1985"), big(2, 730, 560, "1.2 bn t", c="blue", d=0.2, s=70), bar(2, 1100, 950, 260, 520, "red", 0.4), t(2, 1230, 1010, 40, "2015"),
   big(2, 1230, 350, "2.05 bn t", c="red", d=0.6, s=70))
bd(2.5, big(2.5, 960, 350, "+74%", c="red", d=0.0, s=200), arr(2.5, 500, 900, 1400, 600, c="red", d=0.2), [ball(2.5, 600 + 200 * q, 950, 0, -120 * q - 60, 0.3 + 0.06 * q, c="gold") for q in range(5)])
bd(3, [man(3, 400 + 180 * q, 950, 0.8, 0.05 * q, amp=6) for q in range(4)], arr(3, 1150, 700, 1350, 700, c="ink", d=0.3), [man(3, 1450 + 110 * q, 950, 0.6, 0.4 + 0.04 * q, amp=6) for q in range(4)])
bd(3.5, big(3.5, 960, 330, "60%+", c="red", d=0.0, s=180), t(3.5, 960, 600, 60, "more people", c="blue", d=0.2), [man(3.5, 500 + 230 * q, 1000, 0.7, 0.3 + 0.05 * q, arms="up", amp=6) for q in range(5)])
bd(4, big(4, 960, 230, "Brain teaser", c="red", d=0.0, s=120), head(4, 600, 650, 0.1, mood="o"), breath(4, 740, 660, 3, 0.2, dx=300, dy=-100), ic(4, "thermometer", 1400, 650, 260, 0.3, mv="wig", c="red"))
bd(4.5, ic(4.5, "globe", 700, 600, 300, 0.0, mv="spin", c="blue"), ic(4.5, "flame", 1300, 600, 220, 0.2, mv="wig", c="red"), ic(4.5, "question", 1000, 300, 160, 0.3, mv="wig", c="red"))
bd(5, puff(5, 960, 550, 2.0, 0.0), t(5, 960, 930, 70, "Puff", c="blue", d=0.3), star(5, 450, 380, 0.4, r=40), star(5, 1470, 380, 0.5, r=40))
bd(5.5, head(5.5, 500, 600, 0.0, mood="o"), puff(5.5, 700, 600, 0.7, 0.2, dx=700, dy=-100, dur=1.8), ic(5.5, "wind", 1500, 350, 140, 0.3, mv="wig", c="blue"))
bd(6, puff(6, 600, 550, 1.4, 0.0), big(6, 1300, 400, "~4% CO2", c="red", d=0.2, s=120), [co2(6, 1100 + 150 * q, 750, 0.3 + 0.08 * q, dy=0, k=0.8) for q in range(4)])
bd(6.5, bar(6.5, 600, 950, 220, 8, "blue", 0.0), t(6.5, 710, 1010, 40, "air in"), bar(6.5, 1100, 950, 220, 600, "red", 0.2), t(6.5, 1210, 1010, 40, "air out"), big(6.5, 960, 250, "x100", c="red", d=0.5, s=150))
bd(7, puff(7, 600, 550, 1.2, 0.0, mood="o"), ic(7, "question", 1300, 550, 240, 0.2, mv="wig", c="red"), co2(7, 1000, 800, 0.3, dy=-150))
bd(7.5, R(7.5, 700, 650, 520, 60, c="ink", fill="paper", idp="plate"), pop(7.5, "plate", 0.0), wig(7.5, "plate", (960, 680), 2, 1), O(7.5, 960, 560, 130, c="ink", fill="gold", idp="rice"), pop(7.5, "rice", 0.1),
   bob(7.5, "rice", 8, 1.2), big(7.5, 960, 280, "Your lunch", c="red", d=0.3, s=120), ic(7.5, "flame", 1450, 600, 140, 0.4, mv="wig", c="red"))
bd(8, O(8, 600, 600, 200, c="ink", fill="paper", idp="cell"), pop(8, "cell", 0.0), wig(8, "cell", (600, 600), 4, 1), ic(8, "flame", 600, 600, 160, 0.1, mv="wig", c="red"),
   co2(8, 1300, 500, 0.2, dx=-500, dy=0), ball(8, 1300, 750, -550, -100, 0.3, c="gold", r=30))
bd(8.5, ic(8.5, "flame", 600, 600, 260, 0.0, mv="wig", c="red"), t(8.5, 600, 900, 50, "slow, gentle fire", c="blue", d=0.2), ic(8.5, "clock", 1300, 550, 220, 0.3, mv="spin"))
bd(9, ic(9, "battery", 500, 550, 200, 0.0, mv="wig", c="green"), ic(9, "water", 960, 550, 200, 0.1, mv="bob", c="blue"), co2(9, 1450, 550, 0.2, dy=-200, k=1.4),
   t(9, 500, 850, 50, "energy", d=0.1), t(9, 960, 850, 50, "water", d=0.2), t(9, 1450, 850, 50, "CO2", d=0.3))
bd(9.5, head(9.5, 500, 600, 0.0, mood="o"), breath(9.5, 640, 600, 6, 0.1, dx=1000, dy=-200), t(9.5, 1300, 900, 60, "carbon out", c="red", d=0.4))
bd(10, big(10, 960, 230, "Twist one", c="red", d=0.0, s=140), man(10, 700, 950, 1.6, 0.1, arms="up"), ic(10, "question", 1300, 600, 240, 0.2, mv="wig", c="red"))
bd(10.5, O(10.5, 700, 600, 180, c="ink", fill="gold", idp="fat"), pop(10.5, "fat", 0.0), {"t": "move", "at": 10.5, "kind": "grow", "targets": ["fat"], "axis": "x", "pivot": [700, 600], "dur": 1.6, "delay": 0.4, "from": 1, "to": 0.4},
   wig(10.5, "fat", (700, 600), 4, 2), t(10.5, 700, 900, 50, "fat", d=0.1), ic(10.5, "question", 1300, 600, 240, 0.2, mv="wig", c="red"))
bd(11, head(11, 500, 600, 0.0, mood="o"), breath(11, 640, 600, 5, 0.1, dx=900, dy=-150), big(11, 1300, 850, "out the mouth", c="red", d=0.3, s=80))
bd(11.5, big(11.5, 960, 350, "84%", c="red", d=0.0, s=220), co2(11.5, 600, 800, 0.2, dy=-200, k=1.3), co2(11.5, 1300, 800, 0.3, dy=-200, k=1.3), t(11.5, 960, 960, 44, "BMJ, 2014", c="muted", d=0.4))
bd(12, bar(12, 600, 950, 260, 600, "muted", 0.0), t(12, 730, 1010, 40, "CO2 84%"), bar(12, 1100, 950, 260, 115, "blue", 0.3), t(12, 1230, 1010, 40, "water 16%"), ic(12, "water", 1230, 650, 160, 0.4, mv="bob", c="blue"))
bd(12.5, man(12.5, 600, 950, 1.6, 0.0, arms="up", amp=8), breath(12.5, 650, 520, 4, 0.2, dx=800, dy=-150), big(12.5, 1300, 850, "breathe it away", c="blue", d=0.4, s=80))
bd(13, t(13, 960, 230, 60, "our rough math", c="muted", d=0.0), man(13, 600, 950, 1.4, 0.1), ic(13, "clock", 1300, 600, 260, 0.2, mv="spin"))
bd(13.5, big(13.5, 960, 330, "~0.75 kg / day", c="red", d=0.0, s=140), [co2(13.5, 500 + 230 * q, 800, 0.2 + 0.08 * q, dy=-150, k=1.0) for q in range(5)])
bd(14, big(14, 960, 230, "Twist two", c="red", d=0.0, s=140), co2(14, 960, 900, 0.1, dy=-450, dur=2.0, k=1.5), ic(14, "cloud", 600, 450, 200, 0.2, mv="bob", c="blue"), ic(14, "sun", 1350, 450, 200, 0.3, mv="spin", c="gold"))
bd(14.5, ic(14.5, "clock", 600, 550, 260, 0.0, mv="spin"), big(14.5, 1300, 450, "months ago", c="blue", d=0.2, s=110), ic(14.5, "cloud", 1300, 750, 180, 0.3, mv="bob", c="blue"))
bd(15, plant(15, 700, 950, 0.0, 1.5), [co2(15, 1100 + 120 * q, 300 + 80 * q, 0.2 + 0.15 * q, dx=-450, dy=200) for q in range(3)], ic(15, "sun", 1500, 250, 160, 0.2, mv="spin", c="gold"))
bd(15.5, O(15.5, 500, 600, 120, c="ink", fill="paper", idp="bowl"), pop(15.5, "bowl", 0.0), bob(15.5, "bowl", 8, 1.2), ic(15.5, "flask" if False else "water", 960, 600, 1, 0.0) if False else [],
   plant(15.5, 960, 800, 0.1, 1.0), plant(15.5, 1450, 800, 0.2, 1.2), t(15.5, 500, 850, 44, "rice", d=0.1), t(15.5, 960, 900, 44, "bread", d=0.2), t(15.5, 1450, 900, 44, "grass", d=0.3))
bd(16, man(16, 600, 950, 1.4, 0.0), O(16, 1300, 600, 100, c="ink", fill="gold", idp="fd16"), pop(16, "fd16", 0.1), sh(16, "fd16", -650, 50, 0.4, 1.0), bob(16, "fd16", 8, 1.5))
bd(16.5, head(16.5, 500, 600, 0.0, mood="o"), breath(16.5, 640, 600, 4, 0.1, dx=700, dy=-300), ic(16.5, "cloud", 1450, 300, 200, 0.3, mv="bob", c="blue"))
bd(17, loop(17, 960, 580, 300, 0.0, n=4), plant(17, 960, 300, 0.1, 0.6), man(17, 960, 1000, 0.7, 0.2), co2(17, 660, 580, 0.3, dy=0), ic(17, "cloud", 1260, 580, 120, 0.3, mv="bob", c="blue"))
bd(17.5, man(17.5, 600, 950, 1.3, 0.0, arms="up"), man(17.5, 1300, 950, 1.3, 0.1, arms="up"), P(17.5, "M800,600 L900,560", c="blue", w=10, idp="pen"), pop(17.5, "pen", 0.2),
   sh(17.5, "pen", 300, 0, 0.4, 0.8), sh(17.5, "pen", -300, 0, 1.4, 0.8), arr(17.5, 800, 450, 1100, 450, c="green", d=0.3), arr(17.5, 1100, 380, 800, 380, c="green", d=0.6))
bd(18, chimney(18, 600, 950, 0.0), R(18, 1000, 750, 600, 200, c="ink", fill="muted", idp="gnd"), pop(18, "gnd", 0.1), wig(18, "gnd", (1300, 850), 1, 1),
   O(18, 1300, 850, 60, c="ink", fill="ink", idp="oil"), pop(18, "oil", 0.2), bob(18, "oil", 6, 1), t(18, 1300, 600, 50, "millions of years", c="blue", d=0.3))
bd(18.5, O(18.5, 700, 850, 80, c="ink", fill="ink", idp="oil2"), pop(18.5, "oil2", 0.0), sh(18.5, "oil2", 0, -300, 0.3, 1.0), wig(18.5, "oil2", (700, 850), 4, 2),
   ic(18.5, "magnet" if False else "gear", 1300, 600, 180, 0.2, mv="spin"), t(18.5, 1300, 900, 50, "locked away", c="muted", d=0.3))
bd(19, chimney(19, 600, 950, 0.0), [co2(19, 700 + 150 * q, 500, 0.2 + 0.1 * q, dx=200, dy=-300) for q in range(4)], arr(19, 1100, 900, 1600, 900, c="red", d=0.3), t(19, 1350, 800, 50, "one way", c="red", d=0.3))
bd(19.5, ic(19.5, "cloud", 960, 400, 300, 0.0, mv="bob", c="muted"), [co2(19.5, 600 + 180 * q, 950, 0.1 + 0.06 * q, dy=-400, dur=1.8) for q in range(5)], big(19.5, 960, 750, "new carbon", c="red", d=0.4, s=90))
bd(20, chimney(20, 500, 950, 0.0), chimney(20, 750, 950, 0.1), ic(20, "car", 1100, 850, 200, 0.2, mv="wig"), big(20, 1350, 400, "~38 bn t", c="red", d=0.3, s=130))
bd(20.5, bar(20.5, 600, 950, 220, 700, "red", 0.0, 1.2), t(20.5, 710, 1010, 40, "fossil"), bar(20.5, 1100, 950, 220, 38, "blue", 0.4), t(20.5, 1210, 1010, 40, "breath"), head(20.5, 1550, 750, 0.3, mood="o"))
bd(21, big(21, 960, 330, "~18x", c="red", d=0.0, s=220), [man(21, 450 + 200 * q, 1000, 0.6, 0.2 + 0.04 * q, amp=6) for q in range(6)], t(21, 960, 600, 50, "our math", c="muted", d=0.3))
bd(21.5, puff(21.5, 600, 600, 1.0, 0.0), chimney(21.5, 1300, 950, 0.1), bubbles(21.5, 1300, 500, 5, 0.3, 300, "muted"), t(21.5, 960, 250, 60, "puff vs chimney", c="blue", d=0.2))
bd(22, big(22, 960, 230, "Twist three", c="red", d=0.0, s=140), man(22, 600, 950, 1.3, 0.1), ic(22, "flask", 1000, 650, 180, 0.2, mv="wig", c="blue"), ic(22, "magnifier", 1400, 650, 180, 0.3, mv="wig"))
bd(22.5, R(22.5, 600, 400, 700, 500, c="ink", fill="paper", idp="led"), pop(22.5, "led", 0.0), wig(22.5, "led", (950, 900), 1, 1), [check(22.5, 700 + 160 * q, 650, d=0.2 + 0.1 * q) for q in range(4)],
   puff(22.5, 1550, 600, 0.6, 0.3))
bd(23, puff(23, 600, 600, 1.0, 0.0), cross(23, 960, 600, d=0.2), ic(23, "thermometer", 1350, 600, 240, 0.2, mv="wig", c="red"))
bd(23.5, man(23.5, 700, 950, 1.5, 0.0, arms="up", amp=6), big(23.5, 1300, 450, "\"it doesn't\"", c="blue", d=0.2, s=110), ic(23.5, "speaker", 1300, 750, 160, 0.3, mv="wig"))
bd(24, R(24, 550, 350, 800, 550, c="ink", fill="paper", idp="bk"), pop(24, "bk", 0.0), wig(24, "bk", (950, 900), 1, 1), arr(24, 650, 500, 1250, 500, c="green", d=0.2), arr(24, 1250, 700, 650, 700, c="red", d=0.4),
   co2(24, 950, 600, 0.3, dy=0))
bd(24.5, [check(24.5, 600 + 180 * q, 600, d=0.1 * q) for q in range(5)], t(24.5, 960, 350, 64, "every flow", c="blue", d=0.2), ic(24.5, "ruler", 960, 850, 160, 0.4, mv="wig"))
bd(25, t(25, 960, 230, 60, "our own thought", c="muted", d=0.0), plant(25, 500, 950, 0.1, 1.2), ic(25, "car", 960, 750, 200, 0.2, mv="wig"), ic(25, "flame", 1400, 750, 200, 0.3, mv="wig", c="red"))
bd(25.5, ic(25.5, "engine", 600, 600, 220, 0.0, mv="wig"), chimney(25.5, 1000, 950, 0.1), [co2(25.5, 1300 + 100 * q, 700, 0.2 + 0.1 * q, dy=-300) for q in range(3)])
bd(26, [man(26, 450 + 170 * q, 950, 0.8, 0.04 * q, amp=6) for q in range(6)], R(26, 300, 300, 1400, 750, c="ink", idp="room"), pop(26, "room", 0.0), wig(26, "room", (1000, 1050), 1, 1))
bd(26.5, meter(26.5, 960, 600, 0.0), t(26.5, 960, 800, 60, "CO2 ppm", c="blue", d=0.2), [co2(26.5, 500 + 900 * q, 900, 0.3 + 0.2 * q, dy=-300) for q in range(2)])
bd(32, big(32, 960, 230, "Fine print", c="blue", d=0.0, s=130), big(32, 960, 480, "estimate", c="red", d=0.2, s=120), [ic(32, "ruler", 600 + 240 * q, 800, 140, 0.3 + 0.08 * q, mv="wig") for q in range(4)])
bd(32.5, [check(32.5, 450 + 150 * q, 500, d=0.05 * q) for q in range(8)], ic(32.5, "globe", 960, 800, 220, 0.3, mv="spin", c="blue"), t(32.5, 960, 280, 54, "thousands of measurements", c="blue", d=0.2))
bd(33, [man(33, 400 + 160 * q, 950, 0.8, 0.04 * q, amp=6) for q in range(8)], breath(33, 700, 500, 4, 0.3, dx=500, dy=-150))
bd(33.5, [man(33.5, 500 + 230 * q, 950, 1.0, 0.05 * q, arms="up", amp=8) for q in range(5)], cross(33.5, 960, 400, d=0.3), t(33.5, 960, 200, 60, "not a problem to fix", c="blue", d=0.4))
bd(34, head(34, 600, 600, 0.0, mood="o"), breath(34, 740, 600, 3, 0.1, dx=300, dy=-100), ic(34, "thermometer", 1400, 600, 240, 0.2, mv="wig", c="red"), ic(34, "question", 1050, 300, 140, 0.3, mv="wig", c="red"))
bd(34.5, loop(34.5, 960, 600, 300, 0.0, n=5), puff(34.5, 960, 600, 0.8, 0.2), big(34.5, 960, 1000, "round trip", c="green", d=0.4, s=80))
bd(35, puff(35, 650, 550, 1.4, 0.0), loop(35, 650, 550, 260, 0.1, n=3), check(35, 1300, 450, d=0.3), t(35, 1300, 700, 64, "recycled", c="green", d=0.4))
bd(35.5, ic(35.5, "car", 650, 650, 300, 0.0, mv="wig"), [co2(35.5, 850 + 150 * q, 700, 0.1 + 0.12 * q, dx=200, dy=-300) for q in range(4)], cross(35.5, 650, 400, d=0.4), puff(35.5, 1500, 400, 0.6, 0.3))

bd(27, ic(27, "sun", 500, 400, 220, 0.0, mv="spin", c="gold"), plant(27, 900, 950, 0.1, 1.3), arr(27, 650, 450, 850, 650, c="gold", d=0.2), O(27, 1350, 600, 90, c="ink", fill="gold", idp="sug"), pop(27, "sug", 0.3), bob(27, "sug", 8, 1.2),
   t(27, 1350, 800, 50, "sugar", c="gold", d=0.3))
bd(27.5, O(27.5, 600, 600, 100, c="ink", fill="gold", idp="sug2"), pop(27.5, "sug2", 0.0), {"t": "move", "at": 27.5, "kind": "grow", "targets": ["sug2"], "axis": "x", "pivot": [600, 600], "dur": 1.4, "delay": 0.4, "from": 1, "to": 0.2},
   man(27.5, 960, 950, 1.3, 0.1, arms="up", amp=8), ic(27.5, "battery", 1400, 550, 200, 0.2, mv="wig", c="green"), co2(27.5, 700, 600, 0.4, dx=300, dy=-300))
bd(28, ic(28, "sun", 600, 450, 260, 0.0, mv="spin", c="gold"), arr(28, 800, 500, 1100, 700, c="gold", d=0.2), man(28, 1300, 950, 1.4, 0.3, arms="up", amp=8))
bd(28.5, big(28.5, 960, 330, "borrowed sunlight", c="gold", d=0.0, s=110), [ic(28.5, "sun", 500 + 230 * q, 750, 120, 0.2 + 0.07 * q, mv="spin", c="gold") for q in range(5)])
bd(29, [O(29, 450 + 340 * q, 650, 110, c="ink", fill="paper", idp=f"an{q}") for q in range(4)], [pop(29, f"an{q}", 0.06 * q) for q in range(4)], [bob(29, f"an{q}", 10, 1.0 + 0.2 * q) for q in range(4)],
   [co2(29, 560 + 340 * q, 600, 0.3 + 0.08 * q, dx=80, dy=-250, k=0.7) for q in range(4)], t(29, 960, 250, 60, "cows, dogs, cats", c="blue", d=0.2))
bd(29.5, loop(29.5, 960, 580, 320, 0.0, n=5), plant(29.5, 960, 700, 0.2, 0.9), t(29.5, 960, 1000, 54, "same loop", c="green", d=0.4))
bd(30, R(30, 500, 500, 920, 30, c="ink", fill="muted", idp="beam"), pop(30, "beam", 0.0), rot(30, "beam", -12, (960, 515), 0.4, 1.2), puff(30, 650, 400, 0.5, 0.2), chimney(30, 1300, 480, 0.3))
bd(30.5, R(30.5, 300, 750, 1320, 250, c="ink", fill="muted", idp="und"), pop(30.5, "und", 0.0), wig(30.5, "und", (960, 875), 1, 1),
   [ball(30.5, 600 + 250 * q, 900, 0, -500, 0.2 + 0.12 * q, c="ink", r=30) for q in range(4)], t(30.5, 960, 300, 60, "dug up", c="red", d=0.3))
bd(31, ic(31, "cloud", 960, 350, 280, 0.0, mv="bob", c="muted"), bar(31, 500, 950, 120, 150, "muted", 0.1), bar(31, 700, 950, 120, 250, "muted", 0.2), bar(31, 900, 950, 120, 350, "red", 0.3), bar(31, 1100, 950, 120, 450, "red", 0.4))
bd(31.5, chimney(31.5, 600, 950, 0.0), arr(31.5, 800, 600, 1400, 600, c="red", d=0.2), big(31.5, 1300, 400, "one way", c="red", d=0.3, s=110), ic(31.5, "thermometer", 1500, 800, 180, 0.4, mv="wig", c="red"))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"CO2": "C O 2"})
