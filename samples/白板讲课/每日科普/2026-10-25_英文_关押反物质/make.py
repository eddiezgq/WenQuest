"""Daily science short 2026-10-25 (English): "How Do You Jail Antimatter?"
News: Northwestern University physicists (Gerald Gabrielse's group; T. G. Myers et al., Physical Review Letters 137, 173001, Oct 2026)
held a single positron in a Penning trap for a month and more, cooled to its quantum ground state, and drove cyclotron and spin
jumps with microwaves (Sci.News 22 Oct 2026; Scientific American "Physicists trap a single antimatter particle for a month";
phys.org; Slashdot 23 Oct). Hacker News 24 Oct 2026 digest: #11, 280 points.
Facts used: trap ~0.3 K above absolute zero; positrons from radioactive sodium-22; loading one took 8-11 hours with their weak source;
jumps tracked by tiny frequency shifts (which also prove it's just one); future: test CPT symmetry 30+ times more precisely than before
for leptons; Gabrielse: a mismatch "would be the biggest discovery in physics in the last century".
Textbook: e+ e- annihilate into two 511 keV gamma rays (E = mc^2), total ~1.6e-13 J; Penning trap = strong magnetic field (circles)
+ electric end caps (up/down); matter-antimatter asymmetry ~1 extra per billion pairs; bananas emit positrons (potassium-40, rarely);
the same lab measured the electron's magnetic moment to ~0.13 parts per trillion (2023) -> "about twelve digits".
Character: Posi, a little positron. Gag: "don't touch anything".
    python3 make.py <kokoro model dir> | --boards-only | --fake   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("这一小粒反物质，|已经被关了一个月。", "This tiny speck of antimatter | has been in jail for a month."),
 ("只要碰到任何东西，|噗，就没了。", "If it touches anything, | poof. It's gone."),
 ("美国西北大学的物理学家，|把一个正电子关了一个多月。", "Physicists at Northwestern University | kept a single positron trapped for over a month."),
 ("今天的问题：一个碰什么毁什么的东西，|用什么笼子关？", "Today's question: how do you cage something | that destroys any cage it touches?"),
 ("认识一下小正，|一个正电子，电子的镜像双胞胎。", "Meet Posi. | A positron: the electron's mirror twin."),
 ("质量跟电子一样，|电荷相反：正的。", "Same mass as an electron. | Opposite charge: plus instead of minus."),
 ("它俩一碰面，|就同归于尽。", "When the two meet, | they annihilate."),
 ("全部质量变成能量，|两道伽马射线。", "All their mass turns into energy: | two flashes of gamma rays."),
 ("这就是爱因斯坦的E等于mc平方，|一次小小的爆炸。", "That's Einstein's E equals m c squared, | in one tiny bang."),
 ("冷知识：香蕉也会放正电子，|是里面的钾，偶尔放一个。", "Fun fact: bananas make positrons too. | Their potassium does, once in a while."),
 ("那实验室的正电子哪来的？|放射性的钠，会往外吐。", "So where do you get one? | From radioactive sodium, which spits them out."),
 ("他们的源很弱，|抓一个要8到11个小时。", "Their source is gentle, | so catching just one took 8 to 11 hours."),
 ("反转一：这个笼子没有墙，|是用场做的。", "Twist one: the cage has no walls. | It's made of fields."),
 ("强磁场让小正绕小圈跑，|像用绳子甩一个球。", "A strong magnet makes Posi run in tiny circles, | like a ball whirled on a string."),
 ("上下两头的电场往回推，|它就上不去、下不来。", "Electric fields push back from the top and the bottom, | so it can't escape up or down."),
 ("小正就飘在正中间，|什么都不碰。", "Posi floats right in the middle, | touching nothing."),
 ("反转二：空气才是敌人。|每个气体分子里都有电子在等它。", "Twist two: the air is the enemy. | Every gas molecule has electrons waiting for it."),
 ("所以笼子抽成几乎完美的真空，|冷到绝对零度以上0.3度。", "So the trap is an almost perfect vacuum, | chilled to 0.3 degrees above absolute zero."),
 ("这么冷，残留的气体都冻住了，|小正也安静下来。", "That cold freezes out stray gas | and calms Posi down."),
 ("它掉到量子基态：|能安静到的最安静。", "It drops into its quantum ground state: | the calmest it can possibly be."),
 ("然后用微波轻轻一点，|像弹一下陀螺。", "Then the team taps it with microwaves, | like flicking a spinning top."),
 ("小正跳到更高的一圈，|或者把自旋翻个面。", "Posi jumps to a higher circle, | or flips its spin."),
 ("每跳一次，振动频率就变一点点，|每一下都数得清。", "Each jump nudges its wobble frequency a tiny bit, | so they can count every change."),
 ("反转三，最大的一个：费这么大劲干嘛？|为了一个和宇宙一样大的谜。", "Twist three, the big one: why bother? | Because of a mystery as big as the universe."),
 ("大爆炸本该造出一样多的物质和反物质，|然后互相抵消干净。", "The Big Bang should have made equal matter and antimatter, | and they should have wiped each other out."),
 ("可我们还在，|而且是物质做的。", "Yet here we are, | made of matter."),
 ("大约每十亿对里，|多剩下了一个物质。", "For about every billion pairs, | one extra bit of matter survived."),
 ("如果小正的磁性跟电子有一丁点不一样，|那可能就是线索。", "If Posi's magnet is even slightly different from an electron's, | that could be the clue."),
 ("这个实验室测电子的磁性，|已经测到大约十二位数。", "This lab has measured the electron's magnet | to about twelve digits."),
 ("团队说正电子也能做到，|检验会比以前精确三十多倍。", "The team says the positron can get there too, | a test more than thirty times sharper than before."),
 ("领头的教授说，要是不一样，|那是一百年来物理最大的发现。", "The lead professor says a mismatch would be | the biggest discovery in physics in a century."),
 ("友情提示：还没测到那么准，|目前是一个笼子加一个计划。", "Friendly fine print: they haven't measured it that precisely yet. | For now, it's a cage and a plan."),
 ("还有，这不是燃料：一个正电子的能量，|不到一万亿分之一焦耳。", "And no, this isn't fuel. One positron's energy | is less than a trillionth of a joule."),
 ("小正就这样待在笼子里，|转着圈，等着，什么都不碰。", "So Posi sits in its cage, | spinning, waiting, touching nothing."),
 ("地球上最孤单的粒子，|也许握着万物为什么存在的钥匙。", "The loneliest particle on Earth, | and maybe the key to why anything exists at all."),
]
TITLE = {"zh": "怎么关住反物质？", "en": "How Do You Jail Antimatter?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 880, 0.5, r=16)
    B.append(E)


def posi(a, x, y, k=1.0, mood="happy", d=None, c="red", sign="+"):
    """Posi: a round little positron with a plus sign on its tummy and two antennae that wiggle."""
    i = uid("po") + "_"
    an = i + "an"
    E = [O(a, x, y, 80 * k, c="ink", fill=c, idp=i),
         O(a, x - 28 * k, y - 18 * k, 10 * k, c="ink", fill="ink", idp=i), O(a, x + 28 * k, y - 18 * k, 10 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x - 30 * k},{y - 70 * k} L{x - 50 * k},{y - 120 * k} M{x + 30 * k},{y - 70 * k} L{x + 50 * k},{y - 120 * k}", c="ink", w=5, idp=an),
         O(a, x - 50 * k, y - 125 * k, 8 * k, c="ink", fill="gold", idp=an), O(a, x + 50 * k, y - 125 * k, 8 * k, c="ink", fill="gold", idp=an)]
    pl = f"M{x - 18 * k},{y + 42 * k} L{x + 18 * k},{y + 42 * k}" + (f" M{x},{y + 24 * k} L{x},{y + 60 * k}" if sign == "+" else "")
    m = {"happy": f"M{x - 22 * k},{y + 5 * k} Q{x},{y + 22 * k} {x + 22 * k},{y + 5 * k}",
         "o": f"M{x - 9 * k},{y + 10 * k} a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0",
         "sad": f"M{x - 22 * k},{y + 18 * k} Q{x},{y + 2 * k} {x + 22 * k},{y + 18 * k}"}[mood]
    E += [P(a, pl, c="paper", w=6, idp=i), P(a, m, c="ink", w=4, idp=i), wig(a, an, (x, y - 70 * k), 14, 2.2), bob(a, i, 8 * k, 1.4), bob(a, an, 8 * k, 1.4)]
    if d is not None:
        E.append(pop(a, [i, an], d))
    return E, [i, an]


def elle(a, x, y, k=1.0, mood="happy", d=None):
    return posi(a, x, y, k, mood, d, c="blue", sign="-")


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def trap(a, x=960, y=520, w=700, d=0.0):
    """Penning trap: two end caps (pulsing) and a ring of field lines (spinning)."""
    t, b, rg = uid("tp"), uid("tp"), uid("rg")
    E = [R(a, x - w / 2, y - 280, w, 40, c="ink", fill="red", idp=t), R(a, x - w / 2, y + 240, w, 40, c="ink", fill="red", idp=b),
         pop(a, [t, b], d), pulse(a, t, d + 0.5), pulse(a, b, d + 0.7),
         {"t": "ellipse", "at": a, "x": x - w / 2 + 60, "y": y - 60, "w": w - 120, "h": 120, "c": "blue", "sw": 4, "id": rg},
         pop(a, rg, d + 0.1), wig(a, rg, (x, y), 3, 1.0)]
    return E


def orbit(a, x, y, r=160, d=0.0, rpm=90, c="red"):
    """A little dot whirling around (x, y)."""
    i = uid("ob")
    return [O(a, x + r, y, 22, c="ink", fill=c, idp=i), P(a, f"M{x + r},{y} L{x},{y}", c="muted", w=3, idp=i), pop(a, i, d), spin(a, i, (x, y), rpm)]


def flash(a, x, y, d=0.0, c="gold", r=110):
    i = uid("fl")
    return [P(a, " ".join(f"M{x},{y} L{x + r * dx},{y + r * dy}" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, -.7), (.7, -.7), (-.7, .7))), c=c, w=7, idp=i),
            pop(a, i, d), spin(a, i, (x, y), 30), pulse(a, i, d + 0.4)]


def gamma(a, x, y, dirn=1, d=0.0):
    i = uid("gm")
    pts = " ".join(f"L{x + dirn * 40 * q},{y + (20 if q % 2 else -20)}" for q in range(1, 9))
    return [P(a, f"M{x},{y} {pts}", c="gold", w=6, idp=i), pop(a, i, d), sh(a, i, dirn * 300, 0, d + 0.1, 0.8)]


def molecule(a, x, y, d=0.0):
    i = uid("mo")
    return [{"t": "icon", "at": a, "id": i, "name": "molecule", "x": x, "y": y, "size": 140, "c": "ink"}, pop(a, i, d), spin(a, i, (x, y), 20), bob(a, i, 10, 0.9)]


def top(a, x, y, s=160, d=0.0, rpm=200):
    i = uid("tpn")
    return [P(a, f"M{x - s / 2},{y - s / 4} L{x + s / 2},{y - s / 4} L{x},{y + s / 2} Z M{x},{y - s / 4} L{x},{y - s / 2}", c="ink", w=6, idp=i, fill="gold"),
            pop(a, i, d), wig(a, i, (x, y + s / 2), 8, 3.0)]


# 0 speck of antimatter
p_, pi = posi(0, 960, 470, 1.6, d=0.0)
bd(0, p_, trap(0, 960, 500, 760, 0.1), BIG(0, 960, 860, "ANTIMATTER", c="red", d=0.3, s=110))
# 0.5 in jail for a month
p_, pi = posi(0.5, 960, 500, 1.0, mood="sad")
bars = uid("jb")
bd(0.5, p_, [P(0.5, " ".join(f"M{700 + 75 * q},250 L{700 + 75 * q},760" for q in range(8)), c="ink", w=8, idp=bars), pop(0.5, bars, 0.0), sh(0.5, bars, 0, 20, 0.2, 0.3)],
   BIG(0.5, 1500, 400, "1 month", c="blue", d=0.3, s=110), icon(0.5, "clock", 1500, 650, 160, 0.2, mv="spin"))
# 1 touches anything
p_, pi = posi(1, 700, 500, 1.2, mood="o")
wl = uid("wl")
bd(1, p_, [sh(1, pi, 450, 0, 0.3, 0.9), R(1, 1300, 250, 60, 550, c="ink", fill="muted", idp=wl), pop(1, wl, 0.0)], T(1, 960, 860, 60, "don't touch anything!", c="red", d=0.2))
# 1.5 poof
bd(1.5, flash(1.5, 960, 480, 0.0, r=200), flash(1.5, 960, 480, 0.3, c="red", r=120), BIG(1.5, 960, 820, "POOF.", c="red", d=0.2, s=150), gamma(1.5, 1100, 300, 1, 0.3), gamma(1.5, 820, 660, -1, 0.3))
# 2 Northwestern physicists
bd(2, icon(2, "building", 500, 500, 300, 0.0), T(2, 1250, 320, 72, "Northwestern University", c="blue", d=0.1), icon(2, "flask", 1100, 600, 160, 0.3, mv="wig"),
   icon(2, "magnet", 1400, 600, 160, 0.4, c="red", mv="wig"))
# 2.5 single positron over a month
p_, pi = posi(2.5, 600, 500, 1.2)
bd(2.5, p_, orbit(2.5, 600, 500, 200, d=0.0), BIG(2.5, 1350, 380, "1 positron", c="red", d=0.2, s=110), BIG(2.5, 1350, 600, "30+ days", c="blue", d=0.4, s=110))
# 3 today's question
p_, pi = posi(3, 600, 500, 1.2, mood="o")
bd(3, p_, icon(3, "question", 1300, 450, 280, 0.2, c="red", mv="wig"), T(3, 1300, 760, 60, "how do you cage it?", c="ink", d=0.4))
# 3.5 destroys any cage
cg = uid("cg")
bd(3.5, [R(3.5, 650, 300, 620, 420, c="ink", idp=cg), pop(3.5, cg, 0.0), pulse(3.5, cg, 0.5), rot(3.5, cg, 12, (960, 510), 0.6, 0.5)], posi(3.5, 960, 520, 0.9, mood="o")[0],
   flash(3.5, 650, 300, 0.4, r=80), flash(3.5, 1270, 720, 0.6, r=80), T(3.5, 960, 860, 56, "cage touches it -> boom", c="red", d=0.5))
# 4 meet Posi
p_, pi = posi(4, 760, 500, 2.0, d=0.0)
bd(4, p_, BIG(4, 1450, 380, "Posi", c="red", d=0.3, s=150), [e for q in range(3) for e in star(4, 1330 + 120 * q, 600, 0.5 + 0.1 * q, r=30)])
# 4.5 mirror twin
bd(4.5, posi(4.5, 600, 500, 1.3, d=0.0)[0], elle(4.5, 1320, 500, 1.3, d=0.2)[0], icon(4.5, "mirror", 960, 500, 220, 0.1, c="blue", mv="wig"), T(4.5, 960, 820, 64, "mirror twins", c="blue", d=0.4))
# 5 same mass
bd(5, posi(5, 600, 420, 1.0)[0], elle(5, 1320, 420, 1.0)[0], bar(5, 520, 820, 160, 220, "red", d=0.2), bar(5, 1240, 820, 160, 220, "blue", d=0.3), BIG(5, 960, 650, "=", c="ink", d=0.4, s=150),
   T(5, 960, 200, 60, "same mass", c="ink", d=0.1))
# 5.5 opposite charge
bd(5.5, posi(5.5, 600, 500, 1.4)[0], elle(5.5, 1320, 500, 1.4)[0], BIG(5.5, 600, 820, "+", c="red", d=0.2, s=150), BIG(5.5, 1320, 820, "-", c="blue", d=0.3, s=150),
   arr(5.5, 800, 300, 1120, 300, c="ink", d=0.3), arr(5.5, 1120, 340, 800, 340, c="ink", d=0.5))
# 6 when the two meet
p_, pi = posi(6, 400, 500, 1.0, mood="o")
e_, ei = elle(6, 1520, 500, 1.0, mood="o")
bd(6, p_, e_, [sh(6, pi, 480, 0, 0.1, 1.2), sh(6, ei, -480, 0, 0.1, 1.2)], T(6, 960, 220, 64, "uh oh...", c="red", d=0.3))
# 6.5 annihilate
bd(6.5, flash(6.5, 960, 480, 0.0, r=220), flash(6.5, 960, 480, 0.2, c="red", r=140), BIG(6.5, 960, 820, "ANNIHILATE", c="red", d=0.2, s=110), gamma(6.5, 1150, 380, 1, 0.2), gamma(6.5, 770, 580, -1, 0.2))
# 7 mass to energy
bd(7, bar(7, 500, 760, 140, 400, "red", d=0.0), arr(7, 700, 560, 1100, 560, c="ink", d=0.3), icon(7, "flame", 1350, 520, 260, 0.5, c="gold", mv="wig"),
   T(7, 570, 840, 50, "mass", c="red", d=0.1), T(7, 1350, 840, 50, "energy", c="gold", d=0.6))
# 7.5 two gamma flashes
bd(7.5, flash(7.5, 960, 500, 0.0, r=120), gamma(7.5, 1080, 500, 1, 0.2), gamma(7.5, 840, 500, -1, 0.2), T(7.5, 960, 260, 70, "2 gamma rays", c="gold", d=0.3), T(7.5, 960, 780, 50, "511 keV each", c="muted", d=0.5))
# 8 E = mc^2
bd(8, BIG(8, 960, 400, "E = mc²", c="blue", d=0.0, s=160), icon(8, "atom", 450, 650, 200, 0.2, mv="spin"), icon(8, "lens", 1480, 650, 180, 0.3, mv="wig"))
# 8.5 one tiny bang
bd(8.5, flash(8.5, 960, 460, 0.0, r=70), flash(8.5, 960, 460, 0.3, r=40, c="red"), T(8.5, 960, 700, 70, "one tiny bang", c="red", d=0.2), posi(8.5, 400, 700, 0.6, mood="o")[0], elle(8.5, 1520, 700, 0.6, mood="o")[0])
# 9 bananas
bn = uid("bn")
bd(9, [P(9, "M500,600 Q620,780 860,700 Q700,720 560,560 Z", c="ink", w=6, fill="gold", idp=bn), pop(9, bn, 0.0), wig(9, bn, (680, 650), 8, 1.2)],
   T(9, 1350, 400, 70, "bananas too!", c="gold", d=0.2), posi(9, 1350, 650, 0.6, d=0.4)[0])
# 9.5 potassium once in a while
p_, pi = posi(9.5, 700, 600, 0.5)
bd(9.5, [P(9.5, "M400,600 Q520,780 760,700 Q600,720 460,560 Z", c="ink", w=6, fill="gold", idp=uid("bn"))], p_, [sh(9.5, pi, 600, -300, 0.3, 1.2)],
   T(9.5, 1350, 700, 64, "potassium-40", c="blue", d=0.2), icon(9.5, "clock", 1500, 350, 140, 0.1, mv="spin"))
# 10 where do you get one
bd(10, posi(10, 600, 500, 1.2, mood="o")[0], icon(10, "question", 1300, 450, 240, 0.1, c="red", mv="wig"), icon(10, "magnifier", 1550, 700, 140, 0.3, mv="wig"))
# 10.5 radioactive sodium spits
sd = uid("na")
pp = []
for q in range(3):
    p_, pi = posi(10.5, 680, 500, 0.4)
    pp += p_ + [sh(10.5, pi, 600 + 100 * q, -250 + 250 * q, 0.2 + 0.3 * q, 0.8)]
bd(10.5, [O(10.5, 500, 500, 140, c="ink", fill="muted", idp=sd), pop(10.5, sd, 0.0), wig(10.5, sd, (500, 500), 5, 3.0)], T(10.5, 500, 500, 64, "Na-22", c="ink"), pp,
   T(10.5, 1300, 860, 56, "radioactive sodium", c="blue", d=0.3))
# 11 gentle source
bd(11, [O(11, 600, 500, 140, c="ink", fill="muted", idp=uid("na"))], T(11, 600, 500, 64, "Na-22", c="ink"), bubbles(11, 800, 500, 3, 0.2, rise=200, c="red"),
   T(11, 1350, 450, 72, "a gentle source", c="blue", d=0.2), icon(11, "battery", 1350, 680, 150, 0.4, mv="wig"))
# 11.5 8 to 11 hours
bd(11.5, icon(11.5, "clock", 550, 480, 300, 0.0, mv="spin"), BIG(11.5, 1300, 420, "8-11 hours", c="red", d=0.2, s=120), posi(11.5, 1300, 700, 0.6, d=0.5)[0],
   T(11.5, 1300, 860 - 20, 50, "to catch ONE", c="ink", d=0.6))
# 12 cage has no walls
bd(12, BIG(12, 960, 200, "Twist 1", c="blue", d=0.0, s=100), posi(12, 960, 520, 1.0)[0], cross(12, 600, 520, d=0.3), cross(12, 1320, 520, d=0.4), T(12, 960, 820, 60, "no walls", c="red", d=0.4))
# 12.5 made of fields
bd(12.5, trap(12.5, 960, 520, 760, 0.0), posi(12.5, 960, 520, 0.7)[0], icon(12.5, "magnet", 400, 520, 180, 0.2, c="red", mv="wig"), T(12.5, 1550, 520, 64, "fields!", c="blue", d=0.3))
# 13 magnet makes tiny circles
bd(13, icon(13, "magnet", 450, 500, 260, 0.0, c="red", mv="wig"), orbit(13, 1150, 500, 200, d=0.1, rpm=160), orbit(13, 1150, 500, 120, d=0.3, rpm=-120, c="red"),
   T(13, 1150, 820, 56, "tiny circles", c="red", d=0.4))
# 13.5 ball on a string
bd(13.5, orbit(13.5, 960, 480, 260, d=0.0, rpm=100, c="gold"), [e for e in posi(13.5, 960, 480, 0.6)[0]], T(13.5, 960, 840, 60, "a ball whirled on a string", c="ink", d=0.3),
   icon(13.5, "wind", 1500, 400, 120, 0.3, c="blue", mv="wig"))
# 14 electric fields push back
p_, pi = posi(14, 960, 520, 0.8)
bd(14, trap(14, 960, 520, 700, 0.0), p_, [sh(14, pi, 0, -120, 0.2, 0.4), sh(14, pi, 0, 240, 0.7, 0.6)], arr(14, 1400, 260, 1400, 420, c="red", d=0.3), arr(14, 1400, 780, 1400, 620, c="red", d=0.5))
# 14.5 can't escape up or down
bd(14.5, trap(14.5, 960, 520, 700, 0.0), posi(14.5, 960, 520, 0.8, mood="o")[0], cross(14.5, 960, 170, d=0.3), cross(14.5, 960, 880 - 20, d=0.4), T(14.5, 1550, 520, 56, "stuck!", c="red", d=0.5))
# 15 floats in the middle
bd(15, trap(15, 960, 520, 760, 0.0), posi(15, 960, 520, 1.0)[0], orbit(15, 960, 520, 220, d=0.1, rpm=60, c="gold"))
# 15.5 touching nothing
bd(15.5, posi(15.5, 960, 480, 1.4)[0], [e for q in range(6) for e in star(15.5, 400 + 220 * q, 820, 0.1 * q, r=24)], T(15.5, 960, 180, 64, "touching nothing", c="blue", d=0.3))
# 16 air is the enemy
bd(16, BIG(16, 960, 200, "Twist 2", c="blue", d=0.0, s=100), icon(16, "wind", 600, 520, 260, 0.1, c="blue", mv="wig"), posi(16, 1300, 520, 1.0, mood="o")[0], T(16, 960, 820, 60, "air = the enemy", c="red", d=0.3))
# 16.5 gas molecules with electrons waiting
p_, pi = posi(16.5, 960, 520, 0.9, mood="o")
mm = []
for q, (mx, my) in enumerate([(450, 320), (1450, 320), (450, 760), (1450, 760)]):
    mm += molecule(16.5, mx, my, 0.1 * q)
bd(16.5, p_, mm, [e for q in range(3) for e in elle(16.5, 600 + 360 * q, 180, 0.35, d=0.3 + 0.1 * q)[0]])
# 17 near-perfect vacuum
vc = uid("vc")
mol = molecule(17, 800, 520, 0.0)
bd(17, [R(17, 500, 250, 900, 560, c="ink", idp=vc), pop(17, vc, 0.0)], mol, [sh(17, mol[0]["id"], 900, -300, 0.3, 0.8)], T(17, 960, 860, 56, "an almost perfect vacuum", c="blue", d=0.3),
   icon(17, "wind", 1600, 500, 120, 0.1, c="blue", mv="wig"))
# 17.5 0.3 degrees above absolute zero
th = uid("th")
bd(17.5, [{"t": "icon", "at": 17.5, "id": th, "name": "thermometer", "x": 500, "y": 500, "size": 360, "c": "blue"}, pop(17.5, th, 0.0), sh(17.5, th, 0, 60, 0.3, 0.8)],
   BIG(17.5, 1250, 400, "0.3 K", c="blue", d=0.2, s=150), T(17.5, 1250, 620, 56, "above absolute zero", c="ink", d=0.4), [e for q in range(3) for e in star(17.5, 1050 + 200 * q, 780, 0.4 + 0.1 * q, c="blue", r=28)])
# 18 freezes out stray gas
mol = molecule(18, 960, 300, 0.0)
bd(18, mol, [sh(18, mol[0]["id"], 0, 450, 0.2, 0.8)], [R(18, 400, 820, 1120, 30, c="blue", fill="blue")], T(18, 1500, 400, 56, "frozen stuck", c="blue", d=0.4), icon(18, "thermometer", 400, 400, 200, 0.2, c="blue", mv="wig"))
# 18.5 calms Posi down
bd(18.5, posi(18.5, 960, 480, 1.4, mood="happy")[0], T(18.5, 960, 820, 60, "ahh... calm", c="blue", d=0.3), [e for q in range(3) for e in T(18.5, 1250 + 50 * q, 300 - 50 * q, 40 + 12 * q, "z", c="muted", d=0.2 + 0.2 * q)],
   orbit(18.5, 960, 480, 220, d=0.0, rpm=15, c="blue"))
# 19 quantum ground state
lv = []
for q in range(4):
    li = uid("lv")
    lv += [P(19, f"M1100,{760 - 140 * q} L1600,{760 - 140 * q}", c="ink", w=5, idp=li), pop(19, li, 0.1 * q)]
p_, pi = posi(19, 1350, 260, 0.4)
bd(19, lv, p_, [sh(19, pi, 0, 420, 0.4, 0.8)], T(19, 550, 450, 72, "ground state", c="blue", d=0.2), icon(19, "atom", 550, 680, 160, 0.3, mv="spin"))
# 19.5 calmest possible
bd(19.5, posi(19.5, 700, 520, 1.3)[0], BIG(19.5, 1400, 420, "calmest", c="blue", d=0.2, s=120), T(19.5, 1400, 600, 50, "it can possibly be", c="ink", d=0.4), bar(19.5, 1350, 820, 100, 60, "blue", d=0.5))
# 20 taps with microwaves
p_, pi = posi(20, 1350, 520, 1.0)
bd(20, icon(20, "signal", 450, 520, 240, 0.0, c="ink", mv="wig"), sound(20, 620, 520, 1.6, c="blue", d=0.2), p_, T(20, 960, 860, 56, "microwave tap", c="blue", d=0.3))
# 20.5 flicking a spinning top
bd(20.5, top(20.5, 700, 480, 260, 0.0), arr(20.5, 1200, 480, 880, 480, c="red", d=0.3), T(20.5, 1350, 300, 60, "flick!", c="red", d=0.4), orbit(20.5, 700, 480, 200, d=0.1, rpm=200, c="gold"))
# 21 jumps to a higher circle
lv = []
for q in range(3):
    li = uid("lv")
    lv += [P(21, f"M600,{760 - 200 * q} L1300,{760 - 200 * q}", c="ink", w=5, idp=li), pop(21, li, 0.1 * q)]
p_, pi = posi(21, 950, 700, 0.4)
bd(21, lv, p_, [sh(21, pi, 0, -200, 0.4, 0.4)], arr(21, 1400, 760, 1400, 560, c="red", d=0.3), T(21, 1600, 500, 56, "jump!", c="red", d=0.4))
# 21.5 flips its spin
p_, pi = posi(21.5, 960, 480, 1.3)
bd(21.5, p_, [rot(21.5, pi, 180, (960, 480), 0.3, 0.8)], arr(21.5, 1300, 650, 1300, 300, c="blue", d=0.0), arr(21.5, 1450, 300, 1450, 650, c="red", d=0.6),
   T(21.5, 960, 860, 56, "spin flip", c="blue", d=0.5))
# 22 frequency nudges
sw = uid("sw")
bd(22, [{"t": "icon", "at": 22, "id": sw, "name": "sine", "x": 700, "y": 480, "size": 400, "c": "blue"}, pop(22, sw, 0.0), wig(22, sw, (700, 480), 4, 2.0)],
   arr(22, 1050, 480, 1300, 480, c="red", d=0.3), BIG(22, 1550, 480, "shift!", c="red", d=0.4, s=100), T(22, 960, 820, 56, "a tiny wobble change", c="ink", d=0.5))
# 22.5 count every change
bd(22.5, [e for q in range(5) for e in check(22.5, 600 + 180 * q, 450, d=0.1 + 0.15 * q)], posi(22.5, 1550, 450, 0.6)[0], T(22.5, 960, 700, 60, "count every jump", c="green", d=0.3),
   T(22.5, 960, 820, 44, "(and prove it's just one)", c="muted", d=0.6))
# 23 why bother
bd(23, BIG(23, 960, 200, "Twist 3", c="blue", d=0.0, s=100), posi(23, 700, 560, 1.0, mood="o")[0], icon(23, "question", 1300, 560, 260, 0.2, c="red", mv="wig"))
# 23.5 mystery as big as the universe
bd(23.5, icon(23.5, "globe", 960, 480, 320, 0.0, c="blue", mv="spin"), [e for q in range(6) for e in star(23.5, 300 + 260 * q, 220 + 520 * (q % 2), 0.1 * q, r=26)],
   T(23.5, 960, 820, 60, "a universe-size mystery", c="ink", d=0.3))
# 24 equal matter and antimatter
bd(24, flash(24, 960, 450, 0.0, r=200), [e for q in range(3) for e in posi(24, 400 + 180 * q, 700, 0.4, d=0.2 + 0.1 * q)[0]], [e for q in range(3) for e in elle(24, 1150 + 180 * q, 700, 0.4, d=0.3 + 0.1 * q)[0]],
   T(24, 960, 150, 64, "Big Bang: 50 / 50", c="red", d=0.2))
# 24.5 wiped each other out
pp = []
for q in range(3):
    a_, ai = posi(24.5, 400 + 120 * q, 500, 0.4)
    b_, bi_ = elle(24.5, 1520 - 120 * q, 500, 0.4)
    pp += a_ + b_ + [sh(24.5, ai, 560 - 120 * q, 0, 0.1, 0.6), sh(24.5, bi_, -560 + 120 * q, 0, 0.1, 0.6)]
bd(24.5, pp, flash(24.5, 960, 500, 0.7, r=180), T(24.5, 960, 820, 60, "should be: nothing left", c="red", d=0.6))
# 25 yet here we are
bd(25, icon(25, "earth_arc", 960, 700, 500, 0.0, c="blue", mv="bob"), icon(25, "sun", 400, 300, 180, 0.2, c="gold", mv="spin"), icon(25, "moon", 1500, 300, 150, 0.3, c="gold", mv="bob"),
   T(25, 960, 300, 64, "yet here we are", c="ink", d=0.3))
# 25.5 made of matter
bd(25.5, icon(25.5, "atom", 600, 480, 300, 0.0, mv="spin"), elle(25.5, 1300, 480, 1.0)[0], T(25.5, 960, 820, 60, "made of matter", c="blue", d=0.3), orbit(25.5, 600, 480, 220, d=0.2, rpm=80, c="blue"))
# 26 every billion pairs
bd(26, BIG(26, 960, 300, "1,000,000,000", c="blue", d=0.0, s=120), bar(26, 600, 800, 160, 300, "red", d=0.2), bar(26, 1160, 800, 160, 300, "blue", d=0.3), T(26, 960, 860, 56, "pairs", c="ink", d=0.3))
# 26.5 one extra survived
p_, pi = elle(26.5, 960, 480, 1.4)
bd(26.5, p_, BIG(26.5, 960, 820, "+1", c="green", d=0.3, s=150), [e for q in range(4) for e in flash(26.5, 450 + 340 * (q % 2) * 3, 300 + 300 * (q // 2), 0.1 * q, r=60)])
# 27 slightly different magnet
bd(27, posi(27, 600, 480, 1.1)[0], elle(27, 1320, 480, 1.1)[0], icon(27, "magnet", 600, 780, 120, 0.2, c="red", mv="wig"), icon(27, "magnet", 1320, 780, 120, 0.3, c="blue", mv="wig"),
   BIG(27, 960, 480, "≠ ?", c="red", d=0.4, s=120))
# 27.5 the clue
bd(27.5, icon(27.5, "magnifier", 800, 480, 320, 0.0, mv="wig"), icon(27.5, "check", 1350, 400, 160, 0.3, c="green"), T(27.5, 1350, 620, 72, "the clue?", c="red", d=0.4), posi(27.5, 800, 480, 0.5)[0])
# 28 this lab measured the electron
bd(28, icon(28, "building", 500, 500, 280, 0.0), elle(28, 1100, 480, 1.0)[0], icon(28, "ruler", 1500, 500, 200, 0.3, mv="wig"), T(28, 960, 820, 56, "the electron's magnet", c="blue", d=0.3))
# 28.5 twelve digits
bd(28.5, BIG(28.5, 960, 420, "2.00231930436", c="blue", d=0.0, s=120), [e for q in range(4) for e in arr(28.5, 500 + 300 * q, 640, 500 + 300 * q, 560, c="red", d=0.2 + 0.1 * q)],
   T(28.5, 960, 760, 64, "about 12 digits", c="red", d=0.5))
# 29 positron can get there
p_, pi = posi(29, 500, 600, 1.0)
bd(29, p_, [sh(29, pi, 300, -200, 0.2, 0.8)], arr(29, 700, 650, 1300, 300, c="green", d=0.2), icon(29, "check", 1450, 300, 180, 0.5, c="green"), T(29, 1300, 700, 56, "positron: next", c="red", d=0.4))
# 29.5 thirty times sharper
bd(29.5, bar(29.5, 500, 800, 160, 40, "muted", d=0.0), bar(29.5, 760, 800, 160, 500, "blue", d=0.2), BIG(29.5, 1400, 420, "30x", c="blue", d=0.4, s=160), T(29.5, 1400, 640, 56, "sharper test", c="ink", d=0.5))
# 30 the lead professor says
bd(30, icon(30, "speaker", 500, 480, 260, 0.0, mv="wig"), sound(30, 640, 480, 1.4, d=0.2), T(30, 1300, 400, 64, "Prof. Gabrielse:", c="blue", d=0.1),
   T(30, 1300, 560, 60, "\"if they differ...\"", c="ink", d=0.4))
# 30.5 biggest discovery in a century
bd(30.5, BIG(30.5, 960, 340, "biggest in 100 years", c="red", d=0.0, s=100), [e for q in range(5) for e in star(30.5, 500 + 230 * q, 600, 0.2 + 0.1 * q, r=40)], icon(30.5, "rocket", 960, 780, 140, 0.4, c="red", mv="wig"))
# 31 fine print
bd(31, T(31, 960, 200, 64, "Friendly fine print", c="red", d=0.0), icon(31, "magnifier", 600, 520, 240, 0.1, mv="wig"), T(31, 1300, 480, 56, "not that precise yet", c="ink", d=0.3), cross(31, 1300, 650, d=0.5))
# 31.5 a cage and a plan
bd(31.5, trap(31.5, 600, 520, 500, 0.0), posi(31.5, 600, 520, 0.5)[0], BIG(31.5, 960, 520, "+", c="ink", d=0.3, s=120), icon(31.5, "map_pin", 1350, 480, 220, 0.4, c="red"), T(31.5, 1350, 700, 56, "a plan", c="ink", d=0.5))
# 32 this isn't fuel
bd(32, icon(32, "rocket", 600, 500, 300, 0.0, c="red", mv="wig"), cross(32, 600, 500, d=0.3), icon(32, "flame", 1300, 500, 220, 0.2, c="gold", mv="wig"), T(32, 960, 820, 60, "not fuel", c="red", d=0.4))
# 32.5 less than a trillionth of a joule
fl = flash(32.5, 600, 480, 0.0, r=40)
bd(32.5, fl, BIG(32.5, 1250, 400, "< 0.000000000001 J", c="blue", d=0.2, s=80), bar(32.5, 1100, 760, 100, 20, "gold", d=0.4), icon(32.5, "battery", 1500, 650, 160, 0.4, mv="wig"))
# 33 sits in its cage
bd(33, trap(33, 960, 520, 760, 0.0), posi(33, 960, 520, 0.9)[0], icon(33, "clock", 1650, 300, 140, 0.2, mv="spin"))
# 33.5 spinning waiting touching nothing
bd(33.5, posi(33.5, 960, 480, 1.2)[0], orbit(33.5, 960, 480, 240, d=0.0, rpm=60, c="gold"), T(33.5, 960, 840, 56, "spinning. waiting. touching nothing.", c="blue", d=0.3))
# 34 loneliest particle
bd(34, posi(34, 960, 520, 0.6, mood="sad")[0], icon(34, "globe", 960, 520, 520, 0.0, c="muted", mv="spin"), T(34, 960, 150, 64, "the loneliest particle", c="ink", d=0.3))
# 34.5 key to why anything exists
ky = uid("ky")
bd(34.5, posi(34.5, 600, 500, 1.3)[0], [O(34.5, 1200, 450, 60, c="ink", fill="gold", idp=ky), R(34.5, 1260, 435, 260, 30, c="ink", fill="gold", idp=ky), pop(34.5, ky, 0.2), rot(34.5, ky, 25, (1300, 450), 0.4, 0.6)],
   T(34.5, 1300, 720, 60, "why anything exists", c="gold", d=0.5))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"E equals m c squared": "E equals M C squared", "8 to 11": "eight to eleven", "0.3": "zero point three", "Northwestern": "North western", "Posi": "Posey"})
