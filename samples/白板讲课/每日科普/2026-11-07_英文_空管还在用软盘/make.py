"""Daily science 2026-11-07 (English): "Air Traffic Control Runs on Floppy Disks?"
News: the FAA says it will phase floppy disks out of US air traffic control by the end of 2028 (Reuters, 2026-11-05).
Trending: Hacker News front page 2026-11-06, #12 "FAA plans to retire floppy disks from air traffic control by 2028" (258 points when checked);
  carried by Reuters, US News, Yahoo, The Star, GV Wire, Investing.com.
Facts (Reuters via GV Wire / US News, 2026-11-05):
- floppy disks are used for weather and other critical information at more than 400 air traffic control facilities; replacement due by end of 2028;
- the new Enterprise Information Display System replaces four systems dating to the 1980s;
- floppies largely stopped being used more than 25 years ago and have not been produced in large numbers since 2011;
- the FAA relies on decades-old Compaq computers and replacement parts bought on eBay; Administrator Bryan Bedford: "Every facility is a silo.";
- Congress approved $12.5 billion last year; Transportation Secretary Sean Duffy wants $30 billion more;
- paper flight strips: shift began 2022; 27 major airports have already eliminated them; 49 major airports take until at least 2028.
- Tom's Hardware (2025-06-07): some systems can never be shut down, so parts cannot simply be swapped.
Textbook physics: a 3.5-inch HD floppy holds 1.44 "MB" (1,474,560 bytes, about 11.8 million bits) on a disk coated with iron-oxide (rust-like)
  magnetic particles; writing = a head's coil flips the magnetization of tiny regions; reading = moving magnetized regions induce a current in the coil;
  magnetization is stable (rocks keep their ancient magnetism for millions of years: paleomagnetism); strong magnets can erase disks;
  data centers still archive on magnetic tape (LTO).
Ours (said as estimates in the film): one HD floppy is roughly one phone photo; 256 GB / 1.47 MB is about 170,000 floppies;
  reading a full disk takes roughly a minute (about 60 KB/s); stadium-card metaphor; "changing the engine mid-flight" metaphor.
Sources:
- https://zeli.app/digest/2026-11-06 (Hacker News digest, #12)
- https://gvwire.com/2026/11/05/faa-says-it-will-phase-out-floppy-disks-from-air-traffic-control-by-2028/
- https://www.usnews.com/news/top-news/articles/2026-11-05/us-faa-says-it-will-phase-out-floppy-disks-from-air-traffic-control-by-2028
- https://tomshardware.com/pc-components/storage/the-faa-seeks-to-eliminate-floppy-disk-usage-in-air-traffic-control-systems
"""
import math
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, rot, sh, spin,  # noqa: E402,F401
                     star, uid, wig)
from popkit import cute_floppy, stick  # noqa: E402

S = [
 ("美国的空中交通管制，|有一部分还在用软盘。", "America's air traffic control | still runs partly on floppy disks."),
 ("美国联邦航空局说，四百多个空管设施|靠软盘传天气等关键信息。", "The FAA says floppies carry weather and other key information | at more than four hundred facilities."),
 ("这周它承诺：|2028 年底前全部淘汰。", "This week it promised | to phase them out by the end of twenty twenty eight."),
 ("软盘早在二十五年前就基本没人用了，|2011 年后也不再大量生产。", "Floppies mostly vanished more than twenty five years ago, | and have not been mass produced since twenty eleven."),
 ("路透社报道，有些替换零件，|是从 eBay 上买的。", "Reuters reports that some replacement parts | were bought on eBay."),
 ("今天的烧脑问题：一片薄薄的塑料，|凭什么能记住东西？", "Today's brain teaser: how does a thin piece of plastic | remember anything at all?"),
 ("认识主角：小软，|一点四四兆字节的倔脾气。", "Meet our hero, Floppy: | one point four four megabytes of pure attitude."),
 ("一点四四兆字节，|大约就是一张手机照片。", "One point four four megabytes | is roughly one phone photo."),
 ("你的手机也许有二百五十六 G，|我们算了下，相当于十七万张软盘。", "Your phone might hold two hundred fifty six gigabytes. | By our math, that is about one hundred seventy thousand Floppies."),
 ("反转一：里面没有纸，也没有墨，|只有一张涂着“铁锈”的薄圆片。", "Twist one: inside, there is no paper and no ink. | Just a thin disk coated with a kind of rust."),
 ("这层铁锈里全是小磁铁，|小到看不见。", "That rust is packed with tiny magnets, | far too small to see."),
 ("每一小块，磁铁要么朝这边，要么朝那边：|一边是一，一边是零。", "Each tiny patch points one way or the other. | One way means one, the other way means zero."),
 ("就像体育场里的观众，|举牌子朝上或朝下，拼出一幅画。", "Like a stadium crowd | flipping cards up or down to make a picture."),
 ("圆片一转，一个小磁头|就把经过的小磁铁一块块翻过来，这就是写。", "Spin the disk, and a little head | flips the magnets as they pass. That is writing."),
 ("读正好反过来：小磁铁经过线圈，|推出一点点电流。", "Reading is the reverse: | passing magnets nudge a tiny current through a coil."),
 ("反转二：磁铁很倔，|你不碰它，它就一直这么指着。", "Twist two: magnets are stubborn. | Leave them alone, and they stay put."),
 ("有些岩石里的磁性，|保存了几百万年。", "Some rocks have kept their magnetism | for millions of years."),
 ("那为啥要换掉软盘？|反转三：盘没坏，是它周围的世界变了。", "So why replace floppies? | Twist three: the disk is fine; the world around it is not."),
 ("驱动器会磨损，磁头会脏，|而且没人再造新的了。", "Drives wear out. Heads get dirty. | And nobody makes new ones."),
 ("一块强磁铁靠近，|天气数据就可能乱掉。", "Bring a strong magnet close, | and the weather data can get scrambled."),
 ("放久了，塑料会老，|那层“铁锈”也可能脱落。", "Plastic ages, | and that rusty coating can flake off."),
 ("还有速度：我们估算，|读完一整张大约要一分钟。", "And speed: by our estimate, | reading a whole disk takes about a minute."),
 ("航空局局长说：|“每个设施都是一座孤岛。”", "The FAA's chief put it this way: | every facility is a silo."),
 ("数据没法在网上流动，|就得有人拿着它走。", "When data cannot flow over a network, | someone has to carry it."),
 ("新计划：一套新的显示系统，|一口气替换四套八十年代的老系统。", "The plan: one new display system | replaces four systems from the nineteen eighties."),
 ("国会去年批了一百二十五亿美元，|交通部长还想再要三百亿。", "Congress approved twelve and a half billion dollars last year, | and the transportation secretary wants thirty billion more."),
 ("纸质的飞行进程单也要退休：|二十七个大机场已经不用了。", "Paper flight strips are retiring too: | twenty seven big airports have already dropped them."),
 ("为啥这么慢？|天空没法关机升级。", "Why so slow? | You cannot switch off the sky to upgrade it."),
 ("就像飞机还在天上飞，|你得给它换发动机。", "It is like swapping a plane's engine | while it is still flying."),
 ("友情提示：老，不等于不安全。|这些机器跑了几十年。", "Fine print: old does not mean unsafe. | These machines have run for decades."),
 ("但从 eBay 上淘零件，|可不是长久之计。", "But hunting for spare parts on eBay | is not a long term plan."),
 ("还有个讽刺的事：|大型数据中心今天还在用磁带存档。", "And here is the irony: | big data centers still archive on magnetic tape."),
 ("跟小软一个道理：|小磁铁，朝上或朝下。", "Same trick as Floppy: | tiny magnets, pointing one way or the other."),
 ("所以塑料凭什么能记住东西？|它记不住，是上千万个小磁铁在记。", "So how does plastic remember? | It does not. Millions of tiny magnets do."),
 ("小软退休，不是因为它忘了。|是因为大家都忘了怎么跟它说话。", "Floppy is not retiring because it forgot. | It is retiring because everyone forgot how to talk to it."),
]
TITLE = {"zh": "空管还在用软盘？", "en": "Air Traffic Control Runs on Floppies?"}

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


def flop(a, x, y, k=1.0, d=0.0, mood="happy", dx=0, dy=0, dur=1.2):
    i = uid("fp")
    E = cute_floppy(x, y, k, a, idp=i, mood=mood) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]
    if dx or dy:
        E.append(sh(a, i + "*", dx, dy, d + 0.3, dur))
    return E


def ball(a, x, y, dx, dy, d=0.0, c="red", dur=1.0, r=18):
    i = uid("bl")
    return [O(a, x, y, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, dx, dy, d + 0.2, dur)]


def plane(a, x, y, s=200, d=0.0, dx=0):
    i = uid("pl")
    E = [{"t": "icon", "at": a, "id": i, "name": "rocket", "x": x, "y": y, "size": s, "c": "blue"}, pop(a, i, d), wig(a, i, (x, y), 5, 1.2)]
    if dx:
        E.append(sh(a, i, dx, 0, d + 0.3, 2.5))
    return E


def tower(a, x, y=980, d=0.0):
    i, j = uid("tw"), uid("tc")
    return [R(a, x - 40, y - 420, 80, 420, c="ink", fill="paper", idp=i), pop(a, i, d), wig(a, i, (x, y), 1, 1),
            R(a, x - 110, y - 540, 220, 120, c="ink", fill="blue", idp=j), pop(a, j, d + 0.1), wig(a, j, (x, y - 480), 3, 1.5)]


def disk(a, x, y, r=220, d=0.0, n=10, flip=False):
    """The magnetic disk seen from above, spinning, with little arrow-magnets on it."""
    i = uid("dk")
    E = [O(a, x, y, r, c="ink", fill="gold", idp=i), pop(a, i, d), spin(a, i, (x, y), 60), O(a, x, y, 40, c="ink", fill="paper", idp=i)]
    for q in range(n):
        ang = 2 * math.pi * q / n
        cx, cy = x + 0.7 * r * math.cos(ang), y + 0.7 * r * math.sin(ang)
        up = (q % 3 != 0) if not flip else (q % 2 == 0)
        j = uid("mg")
        E += [P(a, f"M{cx},{cy + 22} L{cx},{cy - 22} M{cx - 10},{cy - 10 if up else cy + 10} L{cx},{cy - 22 if up else cy + 22} L{cx + 10},{cy - 10 if up else cy + 10}",
                c="red" if up else "blue", w=6, idp=j), pop(a, j, d + 0.03 * q), spin(a, j, (x, y), 60)]
    return E


def magnets(a, x, y, n=8, d=0.0, flipq=(), gap=110):
    """A row of tiny bar magnets (arrows up = 1, down = 0); those in flipq rotate 180° one after another."""
    E = []
    for q in range(n):
        up = q % 3 != 1
        j = uid("bm")
        cx = x + q * gap
        E += [R(a, cx - 25, y - 60, 50, 120, c="ink", fill="red" if up else "blue", idp=j), pop(a, j, d + 0.04 * q), wig(a, j, (cx, y), 3, 1.5)]
        if q in flipq:
            E.append(rot(a, j, 180, (cx, y), d + 0.4 + 0.12 * q, 0.3))
        E.append(T(a, cx, y + 110, 60, "1" if up else "0", c="ink", d=d + 0.04 * q, font="en"))
    return E


def head(a, x, y, d=0.0, dx=0):
    i = uid("hd")
    E = [R(a, x - 40, y - 160, 80, 140, c="ink", fill="muted", idp=i), P(a, f"M{x - 30},{y - 20} Q{x},{y + 20} {x + 30},{y - 20}", c="red", w=6, idp=i),
         pop(a, i, d), wig(a, i, (x, y - 100), 2, 3)]
    if dx:
        E.append(sh(a, i, dx, 0, d + 0.3, 2.0))
    return E


def coil(a, x, y, d=0.0):
    i = uid("cl")
    return [P(a, " ".join(f"M{x - 80 + 32 * q},{y - 50} Q{x - 64 + 32 * q},{y + 60} {x - 48 + 32 * q},{y - 50}" for q in range(5)), c="gold", w=7, idp=i),
            pop(a, i, d), wig(a, i, (x, y), 4, 3)]


def crowd(a, x, y, n=8, d=0.0):
    E = []
    for q in range(n):
        j = uid("cd")
        cx = x + q * 120
        E += [R(a, cx - 40, y - 60, 80, 60, c="ink", fill="red" if q % 2 else "gold", idp=j), pop(a, j, d + 0.04 * q),
              rot(a, j, 180, (cx, y - 30), d + 0.4 + 0.08 * q, 0.3), O(a, cx, y + 40, 26, c="ink", fill="paper", idp=j)]
        E.append(bob(a, j, 10, 1.4))
    return E


def strip(a, x, y, d=0.0, c="paper"):
    i = uid("st")
    return [R(a, x - 200, y - 35, 400, 70, c="ink", fill=c, idp=i), pop(a, i, d), wig(a, i, (x, y), 3, 1.5)]


# ---------- boards ----------
bd(0, tower(0, 500), flop(0, 1200, 550, 1.6, 0.1, mood="o"), plane(0, 1500, 250, 160, 0.2, dx=-300))
bd(0.5, flop(0.5, 700, 550, 1.4, 0.0), big(0.5, 1350, 400, "floppy disks", c="red", d=0.2, s=110), ic(0.5, "computer", 1350, 750, 220, 0.3, mv="wig"))
bd(1, big(1, 960, 330, "400+", c="red", d=0.0, s=200), [tower(1, 400 + 280 * q, 1000, 0.2 + 0.08 * q) for q in range(5)])
bd(1.5, ic(1.5, "cloud", 500, 450, 220, 0.0, mv="bob", c="blue"), arr(1.5, 650, 500, 850, 550, c="ink", d=0.2), flop(1.5, 1050, 600, 0.9, 0.2, dx=350, dy=0, dur=1.5), tower(1.5, 1600, 980, 0.3))
bd(2, ic(2, "clock", 600, 550, 260, 0.0, mv="spin"), big(2, 1300, 400, "2028", c="red", d=0.2, s=180), flop(2, 1300, 760, 0.7, 0.3, mood="sad"))
bd(2.5, flop(2.5, 700, 550, 1.2, 0.0, mood="sad", dx=-500, dy=0, dur=2.5), t(2.5, 1350, 450, 64, "phase out", c="red", d=0.2), arr(2.5, 1100, 600, 700, 600, c="red", d=0.3), ic(2.5, "check", 1450, 750, 160, 0.4, mv="wig", c="green"))
bd(3, big(3, 960, 330, "25+ years", c="blue", d=0.0, s=150), [ic(3, "computer", 500 + 300 * q, 750, 180, 0.2 + 0.08 * q, mv="wig") for q in range(4)])
bd(3.5, bar(3.5, 500, 950, 150, 600, "blue", 0.0), bar(3.5, 750, 950, 150, 400, "blue", 0.1), bar(3.5, 1000, 950, 150, 150, "blue", 0.2), bar(3.5, 1250, 950, 150, 30, "red", 0.3),
   big(3.5, 1500, 400, "2011", c="red", d=0.4, s=130))
bd(4, ic(4, "computer", 600, 550, 300, 0.0, mv="wig"), t(4, 600, 850, 64, "eBay", c="red", d=0.2), ic(4, "gear", 1300, 500, 200, 0.2, mv="spin"), ic(4, "gear", 1500, 650, 160, 0.3, mv="spin", c="blue"))
bd(4.5, flop(4.5, 700, 550, 1.2, 0.0, mood="o"), big(4.5, 1350, 450, "eBay!", c="red", d=0.2, s=140), man(4.5, 1350, 950, 1.1, 0.3, arms="up", amp=8))
bd(5, big(5, 960, 250, "Brain teaser", c="red", d=0.0, s=120), flop(5, 650, 650, 1.3, 0.1), ic(5, "question", 1300, 650, 240, 0.2, mv="wig", c="red"))
bd(5.5, R(5.5, 600, 450, 400, 30, c="ink", fill="blue", idp="pl55"), pop(5.5, "pl55", 0.0), wig(5.5, "pl55", (800, 465), 4, 1.5), ic(5.5, "eye" , 1300, 500, 200, 0.2, mv="wig"),
   ic(5.5, "question", 1300, 800, 160, 0.3, mv="wig", c="red"), t(5.5, 800, 650, 60, "remember?", c="blue", d=0.3))
bd(6, flop(6, 960, 550, 2.2, 0.0), t(6, 960, 930, 70, "Floppy", c="blue", d=0.3), star(6, 450, 380, 0.4, r=40), star(6, 1470, 380, 0.5, r=40))
bd(6.5, flop(6.5, 600, 600, 1.3, 0.0), big(6.5, 1300, 450, "1.44 MB", c="red", d=0.2, s=140), ic(6.5, "flame", 1300, 750, 140, 0.3, mv="wig", c="red"))
bd(7, big(7, 600, 450, "1.44 MB", c="red", d=0.0, s=120), t(7, 960, 450, 100, "≈", d=0.2), ic(7, "phone", 1350, 500, 280, 0.3, mv="wig"), flop(7, 600, 800, 0.6, 0.1))
bd(7.5, ic(7.5, "phone", 600, 550, 300, 0.0, mv="wig"), ic(7.5, "sun", 600, 520, 100, 0.2, mv="spin", c="gold"), flop(7.5, 1300, 550, 1.0, 0.2, dx=-150, dy=0, dur=1.5), t(7.5, 1000, 900, 60, "1 photo", d=0.4))
bd(8, ic(8, "phone", 600, 550, 320, 0.0, mv="wig"), big(8, 1300, 450, "256 GB", c="blue", d=0.2, s=150), arr(8, 800, 550, 1050, 550, c="ink", d=0.3))
bd(8.5, big(8.5, 960, 280, "~170,000", c="red", d=0.0, s=150), [flop(8.5, 350 + 205 * q, 700 + 90 * (q % 2), 0.45, 0.1 + 0.05 * q) for q in range(7)], t(8.5, 960, 1000, 44, "our math", c="muted", d=0.5))
bd(9, big(9, 960, 250, "Twist one", c="red", d=0.0, s=140), flop(9, 650, 650, 1.2, 0.1, mood="o"), ic(9, "magnifier", 1300, 650, 240, 0.2, mv="wig"))
bd(9.5, disk(9.5, 750, 600, 280, 0.0), t(9.5, 1400, 450, 70, "rust", c="red", d=0.3), arr(9.5, 1250, 500, 1000, 600, c="red", d=0.4), ic(9.5, "atom", 1450, 750, 160, 0.4, mv="spin", c="gold"))
bd(10, disk(10, 600, 600, 260, 0.0), ic(10, "magnifier", 1000, 500, 220, 0.2, mv="wig"), magnets(10, 1250, 600, 5, 0.3, gap=110))
bd(10.5, magnets(10.5, 450, 550, 9, 0.0, gap=130), t(10.5, 960, 900, 64, "tiny magnets", c="blue", d=0.4))
bd(11, magnets(11, 450, 500, 9, 0.0, flipq=(2, 5), gap=130), arr(11, 300, 750, 300, 600, c="red", d=0.3))
bd(11.5, big(11.5, 650, 400, "1", c="red", d=0.0, s=200), big(11.5, 1250, 400, "0", c="blue", d=0.2, s=200), magnets(11.5, 600, 780, 2, 0.1, flipq=(1,), gap=650))
bd(12, crowd(12, 420, 650, 9, 0.0), t(12, 960, 300, 70, "stadium crowd", c="blue", d=0.2))
bd(12.5, crowd(12.5, 420, 550, 9, 0.0), crowd(12.5, 480, 800, 8, 0.2), t(12.5, 960, 250, 64, "a picture!", c="red", d=0.4))
bd(13, disk(13, 750, 600, 300, 0.0), head(13, 1100, 500, 0.2), t(13, 1450, 400, 70, "head", c="red", d=0.3))
bd(13.5, magnets(13.5, 450, 650, 9, 0.0, flipq=(0, 1, 2, 3, 4, 5, 6, 7, 8), gap=130), head(13.5, 450, 520, 0.1, dx=1040), t(13.5, 960, 250, 80, "writing", c="red", d=0.3))
bd(14, magnets(14, 450, 700, 7, 0.0, gap=130), coil(14, 960, 380, 0.2), arr(14, 960, 470, 960, 600, c="ink", d=0.3), t(14, 1450, 350, 70, "reading", c="blue", d=0.3))
bd(14.5, coil(14.5, 700, 550, 0.0), [ball(14.5, 850, 550 + 40 * q, 600, 0, 0.2 + 0.15 * q, c="gold", dur=1.0, r=14) for q in range(3)], ic(14.5, "battery", 1550, 550, 200, 0.4, mv="wig", c="green"))
bd(15, big(15, 960, 250, "Twist two", c="red", d=0.0, s=140), magnets(15, 650, 650, 5, 0.1, gap=150), flop(15, 1600, 650, 0.6, 0.3, mood="happy"))
bd(15.5, ic(15.5, "magnet", 650, 550, 280, 0.0, mv="wig", c="red"), t(15.5, 1300, 450, 70, "stays put", c="blue", d=0.2), ic(15.5, "clock", 1300, 750, 180, 0.3, mv="spin"))
bd(16, [O(16, 500 + 220 * q, 750 - 40 * (q % 2), 90, c="ink", fill="muted", idp=f"rk16_{q}") for q in range(5)], [pop(16, f"rk16_{q}", 0.05 * q) for q in range(5)],
   [wig(16, f"rk16_{q}", (960, 750), 2, 1) for q in range(5)], ic(16, "magnet", 960, 400, 200, 0.3, mv="spin", c="red"))
bd(16.5, big(16.5, 960, 380, "millions of years", c="blue", d=0.0, s=110), [O(16.5, 600 + 240 * q, 750, 70, c="ink", fill="muted", idp=f"rr{q}") for q in range(4)],
   [pop(16.5, f"rr{q}", 0.2 + 0.06 * q) for q in range(4)], [rot(16.5, f"rr{q}", 20, (600 + 240 * q, 750), 0.3, 0.5) for q in range(4)], [wig(16.5, f"rr{q}", (600 + 240 * q, 750), 4, 1) for q in range(4)])
bd(17, flop(17, 700, 550, 1.2, 0.0, mood="o"), ic(17, "question", 1300, 550, 240, 0.2, mv="wig", c="red"), cross(17, 1300, 850, d=0.4))
bd(17.5, big(17.5, 960, 250, "Twist three", c="red", d=0.0, s=140), flop(17.5, 960, 650, 0.9, 0.1), ic(17.5, "globe", 500, 650, 200, 0.2, mv="spin", c="blue"), ic(17.5, "phone", 1450, 650, 200, 0.3, mv="wig"))
bd(18, ic(18, "gear", 600, 550, 240, 0.0, mv="spin"), ic(18, "gear", 800, 700, 160, 0.1, mv="spin", c="red"), head(18, 1300, 600, 0.2), bubbles(18, 1300, 500, 4, 0.3, 200, "muted"))
bd(18.5, [ic(18.5, "building", 500 + 300 * q, 600, 200, 0.06 * q, mv="bob") for q in range(4)], [cross(18.5, 500 + 300 * q, 600, d=0.3 + 0.08 * q) for q in range(4)], t(18.5, 960, 900, 60, "no new ones", c="red", d=0.5))
bd(19, ic(19, "magnet", 500, 550, 260, 0.0, mv="wig", c="red"), flop(19, 1200, 550, 1.2, 0.1, mood="o", dx=200, dy=0, dur=1.0), [arr(19, 650, 450 + 100 * q, 950, 450 + 100 * q, c="red", d=0.2 + 0.08 * q) for q in range(3)])
bd(19.5, magnets(19.5, 450, 550, 9, 0.0, flipq=(0, 2, 3, 6, 7), gap=130), ic(19.5, "cloud", 960, 850, 160, 0.3, mv="wig", c="blue"), t(19.5, 1450, 850, 60, "scrambled", c="red", d=0.4))
bd(20, flop(20, 700, 550, 1.3, 0.0, mood="sad"), ic(20, "clock", 1300, 500, 220, 0.2, mv="spin"), t(20, 1300, 800, 64, "aging", c="muted", d=0.3))
bd(20.5, disk(20.5, 750, 600, 260, 0.0), [ball(20.5, 900 + 40 * q, 500 + 60 * q, 250, 300, 0.2 + 0.1 * q, c="red", dur=1.2, r=12) for q in range(4)], t(20.5, 1450, 400, 60, "flakes off", c="red", d=0.3))
bd(21, ic(21, "clock", 650, 550, 300, 0.0, mv="spin"), flop(21, 1300, 550, 1.0, 0.1), t(21, 960, 900, 50, "our estimate", c="muted", d=0.3))
bd(21.5, big(21.5, 960, 350, "~1 minute", c="red", d=0.0, s=150), bar(21.5, 500, 900, 900, 60, "blue", 0.2, 3.0), disk(21.5, 1600, 750, 120, 0.1, n=6))
bd(22, man(22, 600, 950, 1.5, 0.0), ic(22, "speaker", 900, 500, 180, 0.2, mv="wig"), t(22, 1350, 450, 64, "FAA chief", c="blue", d=0.3))
bd(22.5, [ic(22.5, "building", 450 + 340 * q, 600, 200, 0.07 * q, mv="bob") for q in range(4)], [O(22.5, 450 + 340 * q, 600, 160, c="blue", idp=f"silo{q}") for q in range(4)],
   [pop(22.5, f"silo{q}", 0.2 + 0.07 * q) for q in range(4)], [wig(22.5, f"silo{q}", (450 + 340 * q, 600), 3, 1) for q in range(4)], big(22.5, 960, 900, "every facility is a silo", c="red", d=0.4, s=70))
bd(23, ic(23, "computer", 500, 550, 220, 0.0, mv="wig"), ic(23, "computer", 1400, 550, 220, 0.1, mv="wig"), cross(23, 960, 550, d=0.2), ic(23, "signal", 960, 350, 140, 0.2, mv="wig", c="blue"))
bd(23.5, man(23.5, 500, 950, 1.3, 0.0), flop(23.5, 600, 600, 0.5, 0.1, dx=800, dy=0, dur=2.5), {"t": "move", "at": 23.5, "kind": "shift", "targets": [], "dx": 0, "dy": 0, "dur": 0.1, "delay": 0} if False else [],
   ic(23.5, "computer", 1500, 650, 200, 0.2, mv="wig"), t(23.5, 960, 300, 64, "carry it", c="red", d=0.3))
bd(24, ic(24, "computer", 960, 550, 320, 0.0, mv="wig"), t(24, 960, 850, 64, "new display system", c="blue", d=0.2), star(24, 600, 400, 0.3, r=40), star(24, 1320, 400, 0.4, r=40))
bd(24.5, [ic(24.5, "computer", 450 + 340 * q, 550, 180, 0.06 * q, mv="wig", c="muted") for q in range(4)], [cross(24.5, 450 + 340 * q, 550, d=0.3 + 0.08 * q) for q in range(4)], big(24.5, 960, 850, "1980s", c="red", d=0.4, s=120))
bd(25, big(25, 960, 350, "$12.5 billion", c="green", d=0.0, s=130), ic(25, "building", 960, 750, 220, 0.2, mv="bob"), [ball(25, 600 + 180 * q, 950, 0, -80, 0.3 + 0.06 * q, c="gold") for q in range(5)])
bd(25.5, bar(25.5, 600, 950, 200, 220, "green", 0.0), t(25.5, 700, 1010, 40, "approved", d=0.0), bar(25.5, 1000, 950, 200, 600, "gold", 0.2, 1.2), t(25.5, 1100, 1010, 40, "+$30 billion?", d=0.2),
   man(25.5, 1500, 950, 1.3, 0.3, arms="up", amp=6))
bd(26, [strip(26, 700, 380 + 110 * q, 0.07 * q) for q in range(5)], t(26, 1400, 400, 64, "paper strips", c="blue", d=0.3), ic(26, "rocket", 1400, 700, 180, 0.3, mv="wig", c="blue"))
bd(26.5, big(26.5, 960, 330, "27 airports", c="red", d=0.0, s=140), [check(26.5, 450 + 170 * q, 750, d=0.2 + 0.05 * q) for q in range(7)])
bd(27, ic(27, "question", 650, 550, 260, 0.0, mv="wig", c="red"), ic(27, "clock", 1250, 550, 220, 0.2, mv="spin"), t(27, 960, 900, 64, "why so slow?", d=0.3))
bd(27.5, ic(27.5, "sun", 500, 350, 180, 0.0, mv="spin", c="gold"), [plane(27.5, 900 + 250 * q, 300 + 120 * q, 140, 0.1 * q, dx=-200) for q in range(3)], ic(27.5, "button" if False else "battery", 600, 800, 160, 0.3, mv="wig", c="red"), cross(27.5, 600, 800, d=0.5))
bd(28, plane(28, 960, 450, 320, 0.0, dx=200), ic(28, "gear", 800, 800, 160, 0.2, mv="spin"), ic(28, "engine", 1150, 800, 180, 0.3, mv="wig", c="red"))
bd(28.5, ic(28.5, "engine", 960, 450, 260, 0.0, mv="wig", c="red"), man(28.5, 700, 950, 1.2, 0.1, arms="up", amp=8), man(28.5, 1220, 950, 1.2, 0.2, arms="up", amp=8), ic(28.5, "wind", 1600, 450, 160, 0.3, mv="wig", c="blue"))
bd(29, big(29, 960, 250, "Fine print", c="blue", d=0.0, s=130), tower(29, 650, 980, 0.1), check(29, 650, 300, d=0.4), flop(29, 1300, 650, 1.0, 0.2))
bd(29.5, big(29.5, 960, 330, "decades", c="green", d=0.0, s=150), [ic(29.5, "computer", 550 + 270 * q, 750, 160, 0.2 + 0.06 * q, mv="wig") for q in range(4)], [check(29.5, 550 + 270 * q, 900, d=0.4 + 0.05 * q) for q in range(4)])
bd(30, ic(30, "computer", 600, 550, 260, 0.0, mv="wig"), t(30, 600, 850, 64, "eBay", c="red", d=0.2), ic(30, "gear", 1200, 550, 160, 0.2, mv="spin"), ic(30, "gear", 1400, 650, 120, 0.3, mv="spin", c="red"))
bd(30.5, ic(30.5, "clock", 700, 550, 260, 0.0, mv="spin"), cross(30.5, 700, 550, d=0.3), flop(30.5, 1300, 550, 1.0, 0.1, mood="sad"), t(30.5, 960, 900, 64, "not a long-term plan", c="red", d=0.4))
bd(31, man(31, 600, 950, 1.4, 0.0, arms="up", amp=6), ic(31, "question", 600, 300, 140, 0.2, mv="wig", c="red"), big(31, 1250, 450, "irony", c="red", d=0.2, s=150))
bd(31.5, [ic(31.5, "building", 500 + 300 * q, 450, 180, 0.06 * q, mv="bob") for q in range(3)], [O(31.5, 600 + 300 * q, 780, 90, c="ink", fill="muted", idp=f"tp{q}") for q in range(3)],
   [pop(31.5, f"tp{q}", 0.2 + 0.08 * q) for q in range(3)], [spin(31.5, f"tp{q}", (600 + 300 * q, 780), 90) for q in range(3)], t(31.5, 1600, 600, 60, "tape", c="blue", d=0.4))
bd(32, flop(32, 600, 550, 1.1, 0.0), t(32, 960, 550, 100, "=", d=0.2), O(32, 1350, 550, 150, c="ink", fill="muted", idp="tp32"), pop(32, "tp32", 0.2), spin(32, "tp32", (1350, 550), 90))
bd(32.5, magnets(32.5, 450, 600, 9, 0.0, flipq=(1, 4, 7), gap=130), t(32.5, 960, 280, 64, "same trick", c="blue", d=0.3))
bd(33, flop(33, 700, 550, 1.4, 0.0), ic(33, "question", 1350, 550, 240, 0.2, mv="wig", c="red"), t(33, 960, 920, 64, "how does it remember?", d=0.3))
bd(33.5, magnets(33.5, 450, 500, 9, 0.0, flipq=(0, 3, 6), gap=130), big(33.5, 960, 850, "millions of magnets", c="red", d=0.4, s=90))
bd(34, flop(34, 700, 550, 1.4, 0.0, mood="sad"), t(34, 1350, 450, 64, "forgot?", c="muted", d=0.2), cross(34, 1350, 650, d=0.4), ic(34, "check", 1550, 800, 140, 0.3, mv="wig", c="green"))
bd(34.5, flop(34.5, 960, 450, 1.0, 0.0, mood="happy"), [man(34.5, 450 + 340 * q, 950, 1.0, 0.1 * q, arms="up", amp=6) for q in range(4)],
   [ic(34.5, "question", 450 + 340 * q, 650, 100, 0.2 + 0.06 * q, mv="wig", c="red") for q in range(4)], big(34.5, 960, 200, "talk to me!", c="blue", d=0.4, s=90))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"FAA's": "F A A's", "FAA": "F A A", "eBay": "e Bay", "megabytes": "mega bytes", "gigabytes": "giga bytes", "Floppies": "floppies"})
