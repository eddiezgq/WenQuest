"""Daily science short 2026-10-29 (English): "AI Found 34 Cracks in Math's Biggest Proof"
News: Axiom (San Francisco AI startup) says its AI agents formalized and machine-checked the Classification of Finite Simple Groups
("the enormous theorem") in Lean, announced Oct 27, 2026.
Trending: The Neuron "Everything that happened in AI today" Oct 28, 2026 (story #5); OfficeChai, CryptoBriefing, FourWeekMBA, Unite.AI, zeli.app (Oct 27-28).
Facts used:
- OfficeChai 2026-10-27 https://officechai.com/ai/axiom-enormous-theorem/ : ~15,000 pages, 500+ papers, ~100 mathematicians; Brauer's strategy
  in the 1950s, Gorenstein's roadmap 1972, "done" announced 1983, quasithin gap closed 2004; AI agent swarms, 24 days, ~43.1 million lines of
  Lean; 34 errors serious enough to need repair, most small (typos, mislabeled tables, dropped assumptions); one tied to the Unbalanced Group
  Theorem needed new mathematics, Richard Lyons and Ronald Solomon helped route around it, written up as a new citable result; the list has a few
  infinite families, 16 Lie-type families and 26 sporadic groups; Monster ~8 x 10^53 elements.
- The Neuron 2026-10-28 https://theneuron.ai/digest/everything-that-happened-in-ai-today-wednesday-october-28-2026 : 15,000 pages, 43.1M lines, 24 days.
- CryptoBriefing https://cryptobriefing.com/axiom-ai-formalizes-enormous-theorem-24-days/ (same claims).
- General: atoms in the Earth ~10^50 (so the Monster's size is larger); Lean is a proof assistant whose small kernel checks every step.
Speculation / opinion: "almost nobody has read all of it" is a common remark, said loosely. The robot-safety twist is said "in principle".
The announcement is Axiom's own; outside review is ongoing (said in the fine print). Analogies: picky referee; dominoes. Running gag: the paper
tower ("Stacky") that finally gets a second reader.
    python3 make.py <kokoro model dir> | --boards-only | --fake   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import math
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_bot  # noqa: E402

S = [
 ("一万五千页。|这是一个数学证明，几乎没人把它从头读到尾。", "Fifteen thousand pages. | That's one math proof, and almost nobody has read all of it."),
 ("这周，一家叫Axiom的AI公司说，它的AI把每一行都查了一遍，|只用了24天。", "This week, an AI startup called Axiom says its AI agents checked every line. | In twenty four days."),
 ("还查出了34个真错误，|其中一个得靠全新的数学才补得上。", "And it found thirty four real mistakes. | One of them needed brand new math to fix."),
 ("今天的烧脑问题：|一个大到没人读得完的证明，怎么检查？", "Today's brain teaser: | how do you check a proof too big for any human to read?"),
 ("先说它证明了什么：|有限单群分类定理。", "First, what was being proved? | It's called the classification of finite simple groups."),
 ("“群”就是一套能组合的动作，|比如拧魔方的各种转法。", "A group is just a set of moves you can combine, | like all the ways to twist a puzzle cube."),
 ("单群是积木块，|就像质数能拼出所有的数。", "Simple groups are the building blocks, | the way prime numbers build every other number."),
 ("这个定理说：积木块的完整清单就在这，|一块都不少。", "The theorem says: here is the complete list of blocks. | Nothing is missing."),
 ("清单里有几大无穷家族，|外加26个怪家伙，叫“散在群”。", "The list has a few infinite families, | plus twenty six weird loners called sporadic groups."),
 ("最大的怪家伙叫“魔群”，|大约有8乘10的53次方个元素。", "The biggest loner is called the Monster. | It has about eight times ten to the fifty three elements."),
 ("这比整个地球的原子|还多。", "That's more than the number of atoms | in the entire Earth."),
 ("证完这张清单，用了大约一百位数学家，|五百多篇论文。", "Proving the list took about a hundred mathematicians | and more than five hundred papers."),
 ("五十年代开工，|一九八三年宣布完工。", "It started in the nineteen fifties. | People announced it was done in nineteen eighty three."),
 ("反转一：其实没完工，|有个缺口一直到2004年才补上。", "Twist one: it wasn't done. | One gap stayed open until two thousand and four."),
 ("那一万五千页怎么查？|别信，一步一步查。", "So how do you check fifteen thousand pages? | Stop trusting. Start checking every single step."),
 ("Axiom把证明翻译成一种叫Lean的语言，|Lean是个超级较真的裁判。", "Axiom rewrote the proof in a language called Lean. | Lean is a super picky referee."),
 ("每一步都必须从前面推出来，|不然Lean直接说不行。", "Every step has to follow from the steps before it, | or Lean flat out says no."),
 ("就像多米诺骨牌：|少一块，整条链就停了。", "It's like dominoes: | if one domino is missing, the whole chain stops."),
 ("妙就妙在：|AI负责写，Lean负责查。", "Here's the clever part: | the AI writes, and Lean checks."),
 ("AI会瞎编，|可Lean不吃这一套。", "AI can make things up. | But Lean can't be sweet talked."),
 ("一群AI写了大约四千三百万行，|只用了24天。", "Swarms of AI agents wrote about forty three million lines. | In twenty four days."),
 ("反转二，最意外：|大家信了几十年的证明，有裂缝。", "Twist two, the surprising one: | the proof people trusted for decades had cracks."),
 ("34个错误需要真修，|大多是笔误、表格标错、漏了条件。", "Thirty four errors needed real repair. | Most were typos, mislabeled tables, and missing assumptions."),
 ("但有一个，藏在“非平衡群定理”里，|改个笔误救不回来。", "But one, deep inside a piece called the Unbalanced Group Theorem, | could not be fixed with a quick patch."),
 ("Axiom请来当年的两位作者，莱昂斯和所罗门，|绕过了这个坑。", "Axiom called in two of the original authors, Richard Lyons and Ronald Solomon, | and they found a way around it."),
 ("这个补丁成了一个新结果，|积木清单依然成立。", "That fix is now a new result of its own. | And the list of building blocks still stands."),
 ("反转三：|将来查机器人，可能也靠这个。", "Twist three: | this might be how we check robots, too."),
 ("自动驾驶、手术机器人跑着几百万行代码，|测试不可能试遍所有情况。", "A self driving car or a surgical robot runs millions of lines of code. | Testing can never try every case."),
 ("原理上，像Lean这样的检查器能证明一条规矩永远成立，|比如机械臂永远不撞墙。", "In principle, a checker like Lean can prove a rule always holds, | like this arm never swings into that wall."),
 ("友情提示：这是Axiom自己宣布的，|数学家们还在细看。", "Fine print: this is Axiom's own announcement. | Mathematicians are still going through it."),
 ("而且Lean只查你问的问题，|问题写错了，证出来的也是错的东西。", "And Lean only checks the question you wrote. | Write the question wrong, and you prove the wrong thing."),
 ("所以，没人读得完的证明怎么查？|把每一步切到小得电脑能查。", "So how do you check a proof nobody can read? | Cut every step small enough for a computer to check."),
 ("一万五千页，|变成四千三百万块小骨牌。", "Fifteen thousand pages, | turned into forty three million tiny dominoes."),
 ("数学史上最高的那摞纸，|终于有了第二个读者。", "The tallest stack of paper in math history | finally got a second reader."),
 ("只不过，|不是人。", "It just | wasn't a human."),
]
TITLE = {"zh": "AI查出数学最大证明的34个错", "en": "AI Found 34 Cracks in Math's Biggest Proof"}

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


def E_(a, cx, cy, w, h, c="ink", fill=None, idp=None, sw=5):
    e = {"t": "ellipse", "at": a, "x": cx - w / 2, "y": cy - h / 2, "w": w, "h": h, "c": c, "sw": sw}
    if fill:
        e["fill"] = fill
    if idp:
        e["id"] = idp
    return e


def stacky(a, x, y, k=1.0, d=0.0, n=6, mood="happy"):
    """Stacky, the tower of paper: a wobbling pile of pages with a face; the top page flaps."""
    i, tp = uid("sk"), uid("skt")
    E = []
    for q in range(n):
        E.append(R(a, x - 110 * k + (q % 2) * 12 * k, y - 50 * k * (q + 1), 220 * k, 46 * k, c="ink", fill="paper", idp=i, sw=4))
    top = y - 50 * k * n
    E.append(P(a, f"M{x - 100 * k},{top - 6 * k} L{x + 100 * k},{top - 6 * k} L{x + 80 * k},{top - 40 * k} L{x - 80 * k},{top - 40 * k} Z", c="ink", w=4, idp=tp))
    fy = y - 50 * k * n / 2
    mo = (f"M{x - 25 * k},{fy + 25 * k} Q{x},{fy + 45 * k} {x + 25 * k},{fy + 25 * k}" if mood == "happy"
          else f"M{x - 25 * k},{fy + 40 * k} Q{x},{fy + 20 * k} {x + 25 * k},{fy + 40 * k}" if mood == "sad"
          else f"M{x - 10 * k},{fy + 30 * k} a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0")
    E += [O(a, x - 40 * k, fy - 10 * k, 12 * k, c="ink", fill="ink", idp=i), O(a, x + 40 * k, fy - 10 * k, 12 * k, c="ink", fill="ink", idp=i), P(a, mo, c="ink", w=5, idp=i),
          E_(a, x - 70 * k, fy + 15 * k, 30 * k, 14 * k, c="red", fill="red", idp=i, sw=2), E_(a, x + 70 * k, fy + 15 * k, 30 * k, 14 * k, c="red", fill="red", idp=i, sw=2),
          pop(a, [i, tp], d), wig(a, i, (x, y), 2.5, 1.3), wig(a, tp, (x - 100 * k, top - 6 * k), 12, 2.4), bob(a, tp, 4, 2.4)]
    return E, [i, tp]


def referee(a, x, y, k=1.0, d=0.0, idp=None):
    """Lean the referee: the cute robot with a whistle and a flag that waves."""
    idp = idp or uid("rf")
    fl = uid("fl")
    E = cute_bot(x, y, k, a, idp=idp) + [pop(a, idp + "*", d)]
    E += [P(a, f"M{x + 90 * k},{y - 170 * k} L{x + 90 * k},{y - 330 * k} L{x + 170 * k},{y - 300 * k} L{x + 90 * k},{y - 270 * k}", c="red", w=5, idp=fl),
          pop(a, fl, d + 0.2), wig(a, fl, (x + 90 * k, y - 170 * k), 14, 2.2)]
    return E


def dominoes(a, x, y, n=8, gap=110, d=0.0, missing=None, c="ink"):
    """A row of dominoes that fall one after another (stops at the missing one)."""
    E = []
    for q in range(n):
        if q == missing:
            continue
        i = uid("dm")
        px = x + gap * q
        E += [R(a, px, y - 160, 34, 160, c=c, fill="gold", idp=i, sw=4), pop(a, i, d + 0.04 * q)]
        if missing is None or q < missing:
            E.append(rot(a, i, 60, (px + 34, y), d + 0.5 + 0.12 * q, 0.25))
    return E


def cube(a, x, y, s=240, d=0.0):
    """A Rubik's cube face that twists."""
    i, rw = uid("cb"), uid("cbr")
    cols = ["red", "blue", "gold", "green", "red", "gold", "blue", "green", "red"]
    E = []
    for q in range(9):
        cx, cy = x - s / 2 + (q % 3) * s / 3, y - s / 2 + (q // 3) * s / 3
        E.append(R(a, cx, cy, s / 3, s / 3, c="ink", fill=cols[q], idp=rw if q < 3 else i, sw=4))
    E += [pop(a, [i, rw], d), rot(a, rw, 90, (x, y - s / 3), d + 0.5, 0.5), rot(a, rw, 0, (x, y - s / 3), d + 1.3, 0.5), bob(a, i, 6, 1.0)]
    return E


def blocks(a, x, y, labels, d=0.0, c="blue", w=150):
    E = []
    for q, lb in enumerate(labels):
        i = uid("bk")
        bx = x + (w + 20) * q
        E += [R(a, bx, y, w, w, c="ink", fill=c, idp=i, sw=5), pop(a, i, d + 0.15 * q), bob(a, i, 6, 1.0 + 0.2 * q)]
        if lb:
            E += T(a, bx + w / 2, y + w / 2 + 20, 56, lb, c="ink", d=d + 0.15 * q + 0.1)
    return E


def monster(a, x, y, k=1.0, d=0.0):
    """The Monster: a fuzzy purple-ish blob with horns, one big eye, waving arms."""
    i, ar = uid("mn"), uid("mna")
    E = [E_(a, x, y, 320 * k, 280 * k, c="ink", fill="red", idp=i),
         P(a, f"M{x - 100 * k},{y - 110 * k} L{x - 130 * k},{y - 200 * k} L{x - 60 * k},{y - 130 * k} M{x + 100 * k},{y - 110 * k} L{x + 130 * k},{y - 200 * k} L{x + 60 * k},{y - 130 * k}", c="ink", w=6, idp=i),
         O(a, x, y - 30 * k, 50 * k, c="ink", fill="paper", idp=i), O(a, x, y - 30 * k, 20 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x - 60 * k},{y + 60 * k} Q{x},{y + 100 * k} {x + 60 * k},{y + 60 * k} M{x - 30 * k},{y + 72 * k} L{x - 20 * k},{y + 92 * k} M{x + 30 * k},{y + 72 * k} L{x + 20 * k},{y + 92 * k}", c="ink", w=5, idp=i),
         P(a, f"M{x - 160 * k},{y} L{x - 250 * k},{y - 80 * k} M{x + 160 * k},{y} L{x + 250 * k},{y - 80 * k}", c="ink", w=8, idp=ar),
         pop(a, [i, ar], d), bob(a, i, 10 * k, 1.0), bob(a, ar, 10 * k, 1.0), wig(a, ar, (x, y), 10, 2.0)]
    return E


def crack(a, x, y, d=0.0, k=1.0):
    i = uid("ck")
    return [P(a, f"M{x},{y - 90 * k} L{x - 25 * k},{y - 30 * k} L{x + 20 * k},{y} L{x - 15 * k},{y + 50 * k} L{x + 10 * k},{y + 90 * k}", c="red", w=7, idp=i),
            {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x, y - 90 * k], "dur": 0.5, "delay": d}, pulse(a, i, d + 0.7)]


def paper_rain(a, x0, x1, y, d=0.0, n=6):
    E = []
    for q in range(n):
        i = uid("pr")
        x = x0 + (x1 - x0) * q / max(1, n - 1)
        E += [R(a, x - 40, y, 80, 100, c="ink", fill="paper", idp=i, sw=4), pop(a, i, d + 0.08 * q), sh(a, i, 20 * (q % 2 * 2 - 1), 260, d + 0.3 + 0.08 * q, 1.0),
              rot(a, i, 30 * (q % 2 * 2 - 1), (x, y + 50), d + 0.3 + 0.08 * q, 1.0)]
    return E


def arm(a, x, y, d=0.0, stop=True):
    """A robot arm that swings toward a wall and stops short."""
    i = uid("am")
    E = [R(a, x - 60, y, 120, 50, c="ink", fill="muted", idp=i + "b", sw=5),
         P(a, f"M{x},{y} L{x},{y - 200} L{x + 220},{y - 260}", c="ink", w=14, idp=i), O(a, x + 220, y - 260, 24, c="ink", fill="gold", idp=i),
         pop(a, [i, i + "b"], d), rot(a, i, 25 if stop else 60, (x, y), d + 0.4, 0.6), rot(a, i, 0, (x, y), d + 1.3, 0.5)]
    return E


# ---------- boards ----------
s0, sid = stacky(0, 700, 820, 1.2, 0.0, n=9)
bd(0, s0, BIG(0, 1350, 380, "15,000", c="red", d=0.2, s=150), T(0, 1350, 520, 64, "pages", c="ink", d=0.4), paper_rain(0, 1100, 1650, 600, 0.5, 5))
s0, sid = stacky(0.5, 600, 820, 1.1, 0.0, n=9, mood="o")
bd(0.5, s0, ic(0.5, "eye", 1200, 400, 180, 0.2, mv="wig"), cross(0.5, 1200, 400, d=0.5), T(0.5, 1300, 620, 60, "read it all? nope", c="blue", d=0.6))
bd(1, BIG(1, 960, 330, "Axiom", c="blue", d=0.0, s=140), referee(1, 500, 820, 1.0, 0.2), ic(1, "chip", 1450, 550, 180, 0.3, mv="spin"), ic(1, "magnifier", 1050, 600, 150, 0.4, mv="wig"))
bd(1.5, BIG(1.5, 1100, 430, "24 days", c="red", d=0.0, s=150), ic(1.5, "clock", 450, 450, 220, 0.2, mv="spin"), ic(1.5, "rocket", 1650, 600, 150, 0.4, mv="bob"))
s2, sid = stacky(2, 500, 820, 1.0, 0.0, n=8, mood="o")
bd(2, s2, BIG(2, 1250, 420, "34 mistakes", c="red", d=0.2, s=130), crack(2, 1600, 650, 0.4), crack(2, 900, 650, 0.6))
bd(2.5, BIG(2.5, 960, 320, "1 needed NEW math", c="red", d=0.0, s=100), ic(2.5, "atom", 600, 620, 180, 0.2, mv="spin"), ic(2.5, "gear", 1000, 620, 160, 0.3, mv="spin"),
   ic(2.5, "flask", 1400, 620, 160, 0.4, mv="wig"))
bd(3, BIG(3, 1150, 400, "Brain teaser", c="red", d=0.0, s=120), ic(3, "question", 450, 450, 260, 0.2, mv="wig", c="red"), ic(3, "flame", 1700, 650, 140, 0.4, mv="wig", c="red"),
   ic(3, "gear", 1150, 620, 140, 0.5, mv="spin"))
s3, sid = stacky(3.5, 800, 860, 1.0, 0.0, n=12, mood="o")
bd(3.5, s3, ic(3.5, "magnifier", 1350, 400, 200, 0.2, mv="wig"), ic(3.5, "question", 1550, 650, 150, 0.4, mv="wig", c="red"), T(3.5, 1350, 220, 56, "too big to read", c="blue", d=0.3))
bd(4, ic(4, "question", 960, 450, 260, 0.0, mv="wig", c="red"), stacky(4, 450, 820, 0.8, 0.2, n=7)[0], T(4, 1450, 400, 60, "what is it", c="blue", d=0.3), T(4, 1450, 500, 60, "even about?", c="blue", d=0.4))
bd(4.5, T(4.5, 960, 300, 70, "Classification of", c="ink", d=0.0), BIG(4.5, 960, 460, "Finite Simple Groups", c="blue", d=0.2, s=100), blocks(4.5, 620, 580, ["A", "B", "C", "D"], 0.4, c="gold"))
bd(5, ic(5, "gear", 500, 450, 200, 0.0, mv="spin"), arr(5, 650, 450, 850, 450, c="blue", d=0.2), ic(5, "gear", 1000, 450, 200, 0.3, mv="spin"), T(5, 1450, 400, 64, "moves you", c="ink", d=0.4),
   T(5, 1450, 500, 64, "can combine", c="ink", d=0.5))
bd(5.5, cube(5.5, 700, 480, 300, 0.0), T(5.5, 1350, 400, 64, "twist + twist", c="blue", d=0.3), T(5.5, 1350, 520, 64, "= another twist", c="red", d=0.6), arr(5.5, 900, 480, 1080, 480, c="red", d=0.4))
bd(6, blocks(6, 450, 380, ["2", "3", "5", "7"], 0.0, c="gold"), T(6, 960, 680, 64, "primes", c="blue", d=0.5), ic(6, "atom", 1550, 450, 160, 0.4, mv="spin"))
bd(6.5, blocks(6.5, 300, 450, ["2", "x", "3", "x", "5"], 0.0, c="gold", w=130), arr(6.5, 1150, 520, 1350, 520, c="red", d=0.6), BIG(6.5, 1550, 560, "30", c="red", d=0.8, s=140))
s7, sid = stacky(7, 500, 820, 1.0, 0.0, n=7)
bd(7, s7, ic(7, "check", 1050, 400, 150, 0.2, mv="bob", c="green"), T(7, 1400, 420, 60, "the complete list", c="blue", d=0.3), blocks(7, 950, 560, ["", "", "", ""], 0.4, c="blue", w=110))
bd(7.5, BIG(7.5, 960, 380, "Nothing missing", c="green", d=0.0, s=110), check(7.5, 600, 620, d=0.3), check(7.5, 960, 620, d=0.45), check(7.5, 1320, 620, d=0.6))
inf = uid("inf")
bd(8, [P(8, "M700,450 C600,330 450,330 450,450 C450,570 600,570 700,450 C800,330 950,330 950,450 C950,570 800,570 700,450", c="blue", w=8, idp=inf),
       pop(8, inf, 0.0), spin(8, inf, (700, 450), 20)], T(8, 1350, 400, 64, "infinite families", c="blue", d=0.3), blocks(8, 1100, 520, ["", "", ""], 0.4, c="blue", w=100))
lon = []
for q in range(6):
    j = uid("ln")
    lon += [O(8.5, 450 + 200 * q, 520 + 60 * (q % 2), 50, c="ink", fill="red" if q % 2 else "gold", idp=j), pop(8.5, j, 0.1 * q), bob(8.5, j, 10, 1.0 + 0.3 * q)]
bd(8.5, lon, BIG(8.5, 960, 320, "26 loners", c="red", d=0.2, s=120), T(8.5, 960, 760, 56, "sporadic groups", c="ink", d=0.7))
bd(9, monster(9, 650, 520, 1.1, 0.0), BIG(9, 1350, 420, "the Monster", c="red", d=0.3, s=110))
bd(9.5, monster(9.5, 450, 520, 0.8, 0.0), BIG(9.5, 1200, 450, "8 x 10^53", c="red", d=0.2, s=150), T(9.5, 1200, 620, 56, "elements", c="ink", d=0.5), ic(9.5, "atom", 1700, 650, 120, 0.4, mv="spin"))
bd(10, ic(10, "globe", 700, 470, 300, 0.0, mv="spin"), ic(10, "atom", 1200, 350, 120, 0.2, mv="spin"), ic(10, "atom", 1350, 500, 100, 0.3, mv="spin"), ic(10, "atom", 1200, 650, 110, 0.4, mv="spin"),
   T(10, 1550, 800, 50, "atoms in Earth ~ 10^50", c="blue", d=0.5))
bd(10.5, bar(10.5, 600, 820, 180, 120, "blue", 0.0), bar(10.5, 1100, 820, 180, 520, "red", 0.3), T(10.5, 690, 640, 52, "Earth atoms", c="blue", d=0.1), T(10.5, 1190, 240, 52, "Monster", c="red", d=0.6),
   monster(10.5, 1550, 560, 0.5, 0.5))
people = []
for q in range(7):
    j = uid("pp")
    px = 330 + 210 * q
    people += [O(11, px, 420, 34, c="ink", fill="paper", idp=j), P(11, f"M{px},{454} L{px},{560} M{px - 40},{500} L{px + 40},{500} M{px},{560} L{px - 30},{640} M{px},{560} L{px + 30},{640}", c="ink", w=6, idp=j),
               pop(11, j, 0.07 * q), bob(11, j, 6, 1.2 + 0.2 * q)]
bd(11, people, BIG(11, 960, 260, "~100 mathematicians", c="blue", d=0.3, s=90))
bd(11.5, stacky(11.5, 500, 820, 1.0, 0.0, n=9)[0], BIG(11.5, 1250, 400, "500+ papers", c="red", d=0.2, s=120), paper_rain(11.5, 1000, 1600, 500, 0.4, 6))
bd(12, ic(12, "clock", 450, 450, 220, 0.0, mv="spin"), BIG(12, 1100, 420, "1950s", c="blue", d=0.2, s=150), arr(12, 1350, 450, 1650, 450, c="blue", d=0.4))
bd(12.5, BIG(12.5, 900, 420, "1983: done!", c="green", d=0.0, s=130), ic(12.5, "check", 1550, 430, 180, 0.3, mv="bob", c="green"), star(12.5, 400, 700, 0.4, r=40), star(12.5, 1500, 700, 0.6, r=40))
bd(13, BIG(13, 960, 380, "Twist 1", c="red", d=0.0, s=150), crack(13, 960, 640, 0.3), cross(13, 1450, 640, d=0.5), ic(13, "flame", 450, 600, 140, 0.4, mv="wig", c="red"))
gap = uid("gp")
bd(13.5, [R(13.5, 300, 500, 500, 60, c="ink", fill="gold", idp=gap + "l", sw=4), R(13.5, 1100, 500, 500, 60, c="ink", fill="gold", idp=gap + "r", sw=4), pop(13.5, [gap + "l", gap + "r"], 0.0),
          sh(13.5, gap + "r", -300, 0, 1.0, 0.6)], BIG(13.5, 960, 330, "gap until 2004", c="red", d=0.2, s=100), T(13.5, 960, 720, 52, "21 years later", c="blue", d=0.6))
bd(14, stacky(14, 500, 820, 1.0, 0.0, n=9, mood="o")[0], ic(14, "question", 1200, 450, 220, 0.2, mv="wig", c="red"), T(14, 1350, 700, 60, "15,000 pages?", c="ink", d=0.4))
bd(14.5, cross(14.5, 500, 450, d=0.0), T(14.5, 500, 620, 60, "trust", c="red", d=0.1), check(14.5, 1400, 450, d=0.4), T(14.5, 1400, 620, 60, "check", c="green", d=0.5),
   arr(14.5, 700, 450, 1200, 450, c="blue", d=0.3), dominoes(14.5, 700, 820, 6, 100, 0.6))
bd(15, BIG(15, 1250, 400, "Lean", c="blue", d=0.2, s=160), stacky(15, 450, 820, 0.9, 0.0, n=6)[0], arr(15, 650, 450, 950, 450, c="blue", d=0.4), ic(15, "computer", 1250, 650, 150, 0.5, mv="bob"))
bd(15.5, referee(15.5, 800, 840, 1.2, 0.0), BIG(15.5, 1400, 420, "super picky", c="red", d=0.3, s=100), ic(15.5, "magnifier", 1400, 650, 140, 0.5, mv="wig"))
st16 = []
for q in range(4):
    j = uid("sp")
    st16 += [R(16, 300 + 300 * q, 650 - 110 * q, 260, 80, c="ink", fill="paper", idp=j, sw=4), pop(16, j, 0.15 * q)]
    st16 += T(16, 430 + 300 * q, 705 - 110 * q, 44, f"step {q + 1}", c="blue", d=0.15 * q + 0.05)
bd(16, st16, arr(16, 520, 620, 600, 560, c="red", d=0.3), arr(16, 820, 510, 900, 450, c="red", d=0.5), arr(16, 1120, 400, 1200, 340, c="red", d=0.7), check(16, 1600, 300, d=0.9))
bd(16.5, referee(16.5, 700, 840, 1.1, 0.0), BIG(16.5, 1350, 420, "NO.", c="red", d=0.2, s=170), cross(16.5, 1350, 650, d=0.4))
bd(17, dominoes(17, 400, 700, 10, 120, 0.0), T(17, 960, 300, 70, "dominoes", c="blue", d=0.2))
bd(17.5, dominoes(17.5, 400, 700, 10, 120, 0.0, missing=5), cross(17.5, 1060, 500, d=1.2), T(17.5, 960, 300, 64, "one missing = stop", c="red", d=0.3))
bd(18, BIG(18, 960, 380, "the clever part", c="blue", d=0.0, s=110), ic(18, "flame", 500, 600, 140, 0.2, mv="wig", c="red"), star(18, 1450, 600, 0.3, r=50))
bd(18.5, ic(18.5, "chip", 450, 450, 220, 0.0, mv="spin"), T(18.5, 450, 650, 60, "AI writes", c="blue", d=0.2), arr(18.5, 650, 450, 1050, 450, c="blue", d=0.3),
   referee(18.5, 1350, 780, 0.9, 0.4), T(18.5, 1350, 860, 60, "Lean checks", c="red", d=0.6))
bd(19, ic(19, "chip", 600, 450, 220, 0.0, mv="spin"), T(19, 1200, 400, 64, "2 + 2 = 5, trust me", c="red", d=0.2), ic(19, "question", 1600, 600, 140, 0.4, mv="wig", c="red"))
bd(19.5, referee(19.5, 700, 840, 1.1, 0.0), T(19.5, 1350, 380, 64, "please?", c="blue", d=0.2), cross(19.5, 1350, 560, d=0.4), BIG(19.5, 1350, 760, "NO.", c="red", d=0.6, s=110))
sw = []
for q in range(5):
    sw += ic(20, "chip", 350 + 300 * q, 360, 130, 0.08 * q, mv="spin")
bd(20, sw, BIG(20, 960, 620, "43,000,000 lines", c="red", d=0.4, s=110))
bd(20.5, BIG(20.5, 960, 400, "24 days", c="blue", d=0.0, s=150), ic(20.5, "clock", 450, 450, 200, 0.2, mv="spin"), ic(20.5, "rocket", 1500, 600, 160, 0.4, mv="bob"))
bd(21, BIG(21, 960, 380, "Twist 2", c="red", d=0.0, s=150), ic(21, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), ic(21, "question", 1470, 450, 150, 0.4, mv="wig", c="red"))
bd(21.5, stacky(21.5, 800, 860, 1.1, 0.0, n=9, mood="sad")[0], crack(21.5, 800, 450, 0.3), crack(21.5, 1150, 550, 0.6, 0.8), T(21.5, 1450, 300, 60, "decades of trust", c="blue", d=0.4))
bd(22, BIG(22, 900, 420, "34", c="red", d=0.0, s=170), ic(22, "magnifier", 400, 450, 200, 0.2, mv="wig"), T(22, 1400, 420, 60, "real repairs", c="ink", d=0.3), crack(22, 1400, 650, 0.5, 0.8))
bd(22.5, T(22.5, 500, 380, 60, "typos", c="blue", d=0.0), T(22.5, 960, 380, 60, "wrong tables", c="blue", d=0.2), T(22.5, 1420, 380, 60, "missing IFs", c="blue", d=0.4),
   check(22.5, 500, 560, d=0.2), check(22.5, 960, 560, d=0.4), check(22.5, 1420, 560, d=0.6), ic(22.5, "ruler", 960, 750, 130, 0.5, mv="wig"))
bd(23, BIG(23, 960, 320, "Unbalanced Group Theorem", c="red", d=0.0, s=80), crack(23, 960, 600, 0.3, 1.3), ic(23, "flame", 1400, 600, 150, 0.5, mv="wig", c="red"))
bd(23.5, ic(23.5, "ruler", 600, 450, 200, 0.0, mv="wig"), cross(23.5, 600, 450, d=0.3), crack(23.5, 1200, 480, 0.1, 1.4), T(23.5, 1200, 760, 56, "no quick patch", c="red", d=0.5))
pp2 = []
for q, nm in enumerate(["Lyons", "Solomon"]):
    j = uid("pp")
    px = 650 + 600 * q
    pp2 += [O(24, px, 380, 50, c="ink", fill="paper", idp=j), P(24, f"M{px},{430} L{px},{600} M{px - 60},{500} L{px + 60},{500} M{px},{600} L{px - 40},{720} M{px},{600} L{px + 40},{720}", c="ink", w=7, idp=j),
            pop(24, j, 0.2 * q), bob(24, j, 8, 1.2 + 0.4 * q)]
    pp2 += T(24, px, 820, 60, nm, c="blue", d=0.3 + 0.2 * q)
bd(24, pp2, T(24, 960, 220, 56, "original authors", c="ink", d=0.5))
bd(24.5, crack(24.5, 960, 470, 0.0, 1.2), [P(24.5, "M500,700 Q960,250 1420,700", c="green", w=8, idp="br24"),
                                          {"t": "move", "at": 24.5, "kind": "grow", "targets": ["br24"], "axis": "x", "pivot": [500, 700], "dur": 0.8, "delay": 0.3}],
   T(24.5, 960, 830, 60, "a way around", c="green", d=0.7), dominoes(24.5, 300, 720, 2, 90, 0.1))
bd(25, BIG(25, 960, 400, "new result", c="green", d=0.0, s=130), star(25, 500, 650, 0.2, r=50), star(25, 1420, 650, 0.4, r=50), ic(25, "atom", 960, 650, 150, 0.3, mv="spin"))
bd(25.5, blocks(25.5, 560, 420, ["", "", "", "", ""], 0.0, c="gold", w=130), check(25.5, 960, 700, d=0.6), T(25.5, 960, 300, 60, "the list still stands", c="green", d=0.4))
bd(26, BIG(26, 960, 380, "Twist 3", c="red", d=0.0, s=150), cute_bot(500, 800, 0.9, 26, idp="bot26"), [pop(26, "bot26*", 0.2)], ic(26, "flame", 1450, 600, 140, 0.4, mv="wig", c="red"))
bd(26.5, cute_bot(700, 820, 1.1, 26.5, idp="bot265"), [pop(26.5, "bot265*", 0.0)], referee(26.5, 1300, 820, 1.0, 0.3), ic(26.5, "magnifier", 1000, 350, 140, 0.5, mv="wig"))
car_ = uid("car")
bd(27, [R(27, 300, 480, 400, 130, c="ink", fill="blue", idp=car_), O(27, 380, 630, 40, c="ink", fill="ink", idp=car_), O(27, 620, 630, 40, c="ink", fill="ink", idp=car_),
        pop(27, car_, 0.0), sh(27, car_, 250, 0, 0.3, 1.2)], arm(27, 1450, 700, 0.2), BIG(27, 960, 280, "millions of lines", c="red", d=0.4, s=90))
tc = []
for q in range(6):
    tc += check(27.5, 400 + 170 * q, 450, d=0.1 * q)
bd(27.5, tc, ic(27.5, "question", 1500, 450, 200, 0.6, mv="wig", c="red"), T(27.5, 960, 700, 64, "can't try every case", c="red", d=0.7))
bd(28, referee(28, 600, 820, 1.0, 0.0), T(28, 1300, 400, 64, "rule:", c="blue", d=0.2), T(28, 1300, 520, 64, "ALWAYS holds", c="green", d=0.4), T(28, 960, 220, 48, "in principle", c="muted", d=0.1))
wall = uid("wl")
bd(28.5, arm(28.5, 800, 750, 0.0), [R(28.5, 1250, 250, 60, 520, c="ink", fill="muted", idp=wall), pop(28.5, wall, 0.1), pulse(28.5, wall, 0.9)], check(28.5, 1500, 400, d=1.0),
   T(28.5, 1500, 600, 56, "never hits", c="green", d=1.1))
bd(29, BIG(29, 960, 380, "Fine print", c="blue", d=0.0, s=130), ic(29, "magnifier", 500, 620, 150, 0.2, mv="wig"), T(29, 1250, 620, 56, "Axiom's own claim", c="red", d=0.4))
pp3 = []
for q in range(4):
    j = uid("pp")
    px = 450 + 330 * q
    pp3 += [O(29.5, px, 420, 40, c="ink", fill="paper", idp=j), P(29.5, f"M{px},{460} L{px},{580} M{px - 50},{520} L{px + 50},{520}", c="ink", w=6, idp=j),
            pop(29.5, j, 0.1 * q), bob(29.5, j, 6, 1.0 + 0.3 * q)]
    pp3 += ic(29.5, "magnifier", px + 60, 360, 80, 0.2 + 0.1 * q, mv="wig")
bd(29.5, pp3, T(29.5, 960, 760, 60, "still reviewing", c="blue", d=0.6))
bd(30, referee(30, 600, 820, 1.0, 0.0), T(30, 1300, 400, 60, "checks only", c="ink", d=0.2), T(30, 1300, 520, 60, "what you wrote", c="blue", d=0.4))
bd(30.5, T(30.5, 600, 400, 60, "wrong question", c="red", d=0.0), arr(30.5, 850, 400, 1100, 400, c="red", d=0.2), T(30.5, 1400, 400, 60, "wrong proof", c="red", d=0.4),
   check(30.5, 1400, 600, d=0.6), cross(30.5, 600, 600, d=0.3), ic(30.5, "question", 960, 700, 140, 0.5, mv="wig", c="red"))
bd(31, stacky(31, 500, 860, 1.0, 0.0, n=10, mood="o")[0], ic(31, "question", 1250, 450, 220, 0.2, mv="wig", c="red"))
bd(31.5, stacky(31.5, 400, 820, 0.8, 0.0, n=6)[0], arr(31.5, 600, 500, 850, 500, c="blue", d=0.2), dominoes(31.5, 950, 700, 7, 110, 0.4), ic(31.5, "computer", 1300, 330, 140, 0.3, mv="bob"))
bd(32, BIG(32, 960, 380, "15,000 pages", c="blue", d=0.0, s=130), paper_rain(32, 400, 1500, 500, 0.2, 7))
bd(32.5, dominoes(32.5, 250, 700, 14, 105, 0.0), BIG(32.5, 960, 320, "43 million", c="red", d=0.2, s=120))
s33, sid = stacky(33, 800, 880, 1.0, 0.0, n=12)
bd(33, s33, ic(33, "map_pin", 1350, 300, 160, 0.3, mv="bob", c="red"), T(33, 1400, 500, 56, "tallest stack", c="blue", d=0.4))
bd(33.5, stacky(33.5, 600, 860, 1.0, 0.0, n=9)[0], referee(33.5, 1250, 840, 1.0, 0.2), T(33.5, 1250, 260, 60, "reader #2", c="green", d=0.5))
bd(34, stacky(34, 600, 860, 1.0, 0.0, n=9)[0], ic(34, "chip", 1250, 450, 220, 0.2, mv="spin"), T(34, 1250, 700, 60, "it just...", c="blue", d=0.4))
bd(34.5, BIG(34.5, 960, 400, "wasn't human", c="red", d=0.0, s=130), referee(34.5, 450, 820, 0.8, 0.2), stacky(34.5, 1500, 820, 0.8, 0.3, n=6, mood="happy")[0])

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"Ronald": "Ron Old"})
