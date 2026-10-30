"""Daily science short 2026-10-30 (English): "Is 68% of the Universe a Math Mistake?"
News: UC Davis / UCL mathematicians (Blake Temple, C. Alexander, Z. Vogler) argue the standard Lambda-CDM model is unstable and that cosmic
acceleration might come from Einstein's equations without dark energy. Proc. R. Soc. A 482 (2338), doi 10.1098/rspa.2025.0912.
Trending: ScienceDaily "Top Science" Oct 29, 2026 (#5): "Einstein's Equations May Explain the Universe Without Dark Energy".
Facts used:
- ScienceDaily 2026-10-29 https://www.sciencedaily.com/releases/2026/10/261028232719.htm : Friedmann spacetimes unstable to radial perturbations at
  large length scales; Temple: this "appears to rule out" Lambda-CDM as a stable solution; pencil-on-its-tip analogy ("any breath of air and it falls
  away"); unstable solutions are not physical; accelerations away from Friedmann behavior may appear far from the center; theoretical only.
- Sci.News https://www.sci.news/astronomy/dark-energy-alternative-14801.html (same paper; no observational test yet).
- General: accelerating expansion found in 1998 from type Ia supernovae (Nobel Prize 2011); dark energy ~68% of the cosmic energy budget (Planck);
  Einstein's cosmological constant 1917, "biggest blunder" is a reported quote (via Gamow); DESI 2025 results hinted dark energy may evolve.
Speculation: "the universe already fell over" is said as their picture / maybe. The raisin-bread and ball analogies are standard teaching analogies.
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_bot  # noqa: E402

S = [
 ("宇宙的百分之六十八，|可能根本不存在。", "Sixty eight percent of the universe | might not exist."),
 ("说的是暗能量。|这周，几位数学家冲它挥了一拳。", "We're talking about dark energy. | This week, a team of mathematicians took a swing at it."),
 ("新论文说，爱因斯坦自己的方程|也许不用暗能量就能解释宇宙。", "A new paper says Einstein's own equations | might explain the universe without it."),
 ("今天的烧脑问题：|一支立在笔尖上的铅笔，能推倒整个宇宙学吗？", "Today's brain teaser: | can a pencil standing on its tip knock over cosmology?"),
 ("先说谜题：宇宙在膨胀，|就像烤箱里发起来的面包。", "First, the mystery. The universe is expanding, | like bread dough rising in an oven."),
 ("星系是面包里的葡萄干，|彼此越离越远。", "Galaxies are the raisins. | They all drift apart from each other."),
 ("引力本该让膨胀变慢，|就像往上扔的球越飞越慢。", "Gravity should slow that down, | like a ball thrown up slows as it rises."),
 ("可是一九九八年，天文学家看遥远的爆炸恒星，|发现正好相反。", "But in nineteen ninety eight, astronomers watched distant exploding stars | and found the opposite."),
 ("膨胀在加速。|这个发现拿了诺贝尔奖。", "The expansion is speeding up. | That discovery won a Nobel Prize."),
 ("想象你往上扔个球，|它越飞越快。", "Imagine throwing a ball up | and watching it go faster and faster."),
 ("一定有东西在推。|科学家给它起名叫暗能量。", "Something must be pushing. | Scientists named that something dark energy."),
 ("按标准模型，暗能量占宇宙的|大约百分之六十八。", "In the standard model, dark energy is about sixty eight percent | of everything in the cosmos."),
 ("可它到底是什么，|没人知道。", "And nobody knows | what it actually is."),
 ("反转一：这个点子很老了。|爱因斯坦一九一七年就加过类似的一项。", "Twist one: the idea is old. | Einstein added a similar term in nineteen seventeen."),
 ("据说他后来称之为一生最大的错误。|结果它又回来了。", "He reportedly called it his biggest blunder. | Then it came back."),
 ("新论文来自加州大学戴维斯分校和伦敦大学学院，|发表在英国皇家学会的期刊上。", "The new paper comes from UC Davis and University College London, | in a Royal Society journal."),
 ("它瞄准的是宇宙的标准模型，|就是自带暗能量的那个。", "Their target is the standard model of the cosmos, | the one with dark energy built in."),
 ("来看这支铅笔。|你可以让它完美地立在笔尖上。", "Here's the pencil. | You can balance it perfectly on its tip."),
 ("数学上，这是个真解：|所有的力正好抵消。", "Mathematically, that's a real solution. | All the forces cancel."),
 ("可只要一丝风，|它就倒了。", "But one tiny breath of air, | and it falls."),
 ("反转二，最意外：|他们说，我们的宇宙模型就是这支铅笔。", "Twist two, the surprising one: | they say our model of the universe is that pencil."),
 ("他们算出它不稳定：|超大尺度上的小涟漪会长大，而不是消失。", "They found it's unstable. | Tiny ripples on huge scales grow instead of fading."),
 ("论文作者认为，|不稳定的解，大自然不会选。", "The lead author argues | that nature doesn't pick unstable solutions."),
 ("那如果宇宙早就从平衡点滑开了呢？|在他们的图景里，这一滑，看起来就像加速。", "So what if the universe already slid off the balance point? | In their picture, that slide could look like acceleration."),
 ("而且，|根本不需要暗能量。", "And it would need | no dark energy at all."),
 ("反转三：怀疑暗能量的不只这篇论文。|去年，巨型星系巡天DESI暗示，暗能量可能在变。", "Twist three: this paper isn't alone. | Last year, a giant galaxy survey called DESI hinted that dark energy may be changing."),
 ("如果它会变，|它也许从来就不是一个常数。", "If it can change, | maybe it was never a constant to begin with."),
 ("友情提示：目前这还是纯数学，|还没拿望远镜的数据检验过。", "Fine print: so far this is pure math. | Nobody has tested it against telescope data yet."),
 ("很多宇宙学家仍然认为，|暗能量是对观测最好的解释。", "And many cosmologists still think dark energy | is the best explanation for what we see."),
 ("新想法得做出能测量的预言，|这才是下一步。", "A new idea has to predict something we can measure. | That's the next step."),
 ("所以，笔尖上的铅笔能推倒宇宙学吗？|也许能，如果宇宙就是那支铅笔。", "So, can a pencil on its tip knock over cosmology? | Maybe, if the universe is the pencil."),
 ("宇宙的百分之六十八，|押在一个平衡上。", "Sixty eight percent of everything | is riding on a balancing act."),
 ("要么暗能量是真的，|而且怪得要命。", "Either dark energy is real, | and deeply weird."),
 ("要么我们最好的宇宙地图，|一直都立在笔尖上。", "Or our best map of the cosmos | has been standing on its tip all along."),
]
TITLE = {"zh": "宇宙的68%是个数学错误？", "en": "Is 68% of the Universe a Math Mistake?"}

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


def pencil(a, x, y, k=1.0, d=0.0, fall=None, mood="happy", amp=4):
    """Penny the pencil: balanced on its tip at (x, y), wobbling; fall = seconds when it topples."""
    i = uid("pn")
    h = 460 * k
    w = 70 * k
    E = [P(a, f"M{x},{y} L{x - w / 2},{y - 90 * k} L{x + w / 2},{y - 90 * k} Z", c="ink", w=4, fill="gold", idp=i),
         R(a, x - w / 2, y - h, w, h - 90 * k, c="ink", fill="gold", idp=i, sw=4),
         R(a, x - w / 2, y - h - 50 * k, w, 50 * k, c="ink", fill="red", idp=i, sw=4),
         O(a, x - 14 * k, y - h + 110 * k, 7 * k, c="ink", fill="ink", idp=i), O(a, x + 14 * k, y - h + 110 * k, 7 * k, c="ink", fill="ink", idp=i)]
    mo = (f"M{x - 15 * k},{y - h + 140 * k} Q{x},{y - h + 155 * k} {x + 15 * k},{y - h + 140 * k}" if mood == "happy"
          else f"M{x - 8 * k},{y - h + 148 * k} a8,8 0 1,0 {16 * k},0 a8,8 0 1,0 {-16 * k},0")
    E += [P(a, mo, c="ink", w=4, idp=i), pop(a, i, d), wig(a, i, (x, y), amp, 1.4)]
    if fall is not None:
        E.append(rot(a, i, 80, (x, y), fall, 0.6))
    return E


def galaxy(a, x, y, r=60, d=0.0, c="blue", rpm=30):
    i = uid("gx")
    return [P(a, f"M{x},{y} C{x + r},{y - r} {x + r},{y + r} {x},{y + r * 0.6} M{x},{y} C{x - r},{y + r} {x - r},{y - r} {x},{y - r * 0.6}", c=c, w=5, idp=i),
            O(a, x, y, r * 0.18, c=c, fill=c, idp=i), pop(a, i, d), spin(a, i, (x, y), rpm)]


def dough(a, x, y, d=0.0, grow=True, n=6):
    """Raisin bread: a loaf that rises, raisins drift apart."""
    i = uid("dg")
    E = [E_(a, x, y, 520, 300, c="ink", fill="gold", idp=i), pop(a, i, d)]
    if grow:
        E.append({"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x, y + 150], "dur": 1.2, "delay": d + 0.3})
    for q in range(n):
        j = uid("rs")
        rx, ry = x - 160 + 64 * q, y - 40 + 50 * (q % 2)
        E += [O(a, rx, ry, 16, c="ink", fill="ink", idp=j), pop(a, j, d + 0.1), sh(a, j, (rx - x) * 0.6, (ry - y) * 0.6 - 40, d + 0.4, 1.2)]
    return E


def ball(a, x, y, d=0.0, up=-400, faster=False):
    i = uid("bl")
    E = [O(a, x, y, 45, c="ink", fill="red", idp=i), pop(a, i, d), spin(a, i, (x, y), 60)]
    if faster:
        E += [sh(a, i, 0, up * 0.2, d + 0.3, 0.6), sh(a, i, 0, up, d + 0.9, 0.4)]
    else:
        E += [sh(a, i, 0, up, d + 0.3, 1.2)]
    return E


def boom(a, x, y, d=0.0, c="gold", r=90):
    i = uid("bm")
    pts = []
    import math
    for q in range(16):
        rr = r if q % 2 == 0 else r * 0.45
        ang = math.pi * q / 8
        pts.append(f"{x + rr * math.cos(ang):.0f},{y + rr * math.sin(ang):.0f}")
    return [P(a, "M" + " L".join(pts) + " Z", c="red", w=5, fill=c, idp=i), pop(a, i, d), pulse(a, i, d + 0.4), spin(a, i, (x, y), 20)]


def ripple(a, x, y, d=0.0, n=3, grow=True):
    E = []
    for q in range(n):
        j = uid("rp")
        r = 60 + 50 * q
        E += [O(a, x, y, r, c="blue", idp=j, sw=4), pop(a, j, d + 0.15 * q)]
        if grow:
            E.append({"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "x", "pivot": [x, y], "dur": 0.8, "delay": d + 0.4 + 0.15 * q})
        E.append(pulse(a, j, d + 0.9 + 0.1 * q))
    return E


def blob(a, x, y, k=1.0, d=0.0):
    """Dark Energy, a shy purple-black cloud with a question mark face that pushes."""
    i, ar = uid("de"), uid("dea")
    E = [P(a, f"M{x - 150 * k},{y} C{x - 180 * k},{y - 120 * k} {x - 60 * k},{y - 170 * k} {x},{y - 120 * k} C{x + 60 * k},{y - 180 * k} {x + 190 * k},{y - 110 * k} {x + 150 * k},{y} "
               f"C{x + 190 * k},{y + 100 * k} {x - 190 * k},{y + 100 * k} {x - 150 * k},{y} Z", c="ink", w=5, fill="muted", idp=i),
         O(a, x - 45 * k, y - 30 * k, 14 * k, c="ink", fill="ink", idp=i), O(a, x + 45 * k, y - 30 * k, 14 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x - 25 * k},{y + 30 * k} Q{x},{y + 50 * k} {x + 25 * k},{y + 30 * k}", c="ink", w=4, idp=i),
         P(a, f"M{x - 160 * k},{y + 10 * k} L{x - 260 * k},{y + 10 * k} M{x + 160 * k},{y + 10 * k} L{x + 260 * k},{y + 10 * k}", c="ink", w=8, idp=ar),
         pop(a, [i, ar], d), bob(a, i, 10 * k, 1.0), bob(a, ar, 10 * k, 1.0), wig(a, ar, (x, y), 8, 2.2)]
    return E


def pie(a, x, y, r=220, d=0.0):
    """68 / 27 / 5 pie, the dark-energy slice pops out."""
    import math
    E = []
    parts = [(0.68, "muted"), (0.27, "blue"), (0.05, "gold")]
    a0 = 0.0
    for frac, c in parts:
        j = uid("pi")
        a1 = a0 + 2 * math.pi * frac
        x0, y0 = x + r * math.sin(a0), y - r * math.cos(a0)
        x1, y1 = x + r * math.sin(a1), y - r * math.cos(a1)
        E += [P(a, f"M{x},{y} L{x0:.0f},{y0:.0f} A{r},{r} 0 {1 if frac > 0.5 else 0},1 {x1:.0f},{y1:.0f} Z", c="ink", w=4, fill=c, idp=j), pop(a, j, d + 0.1 * len(E) / 2)]
        if c == "muted":
            E.append(sh(a, j, 30, -20, d + 0.8, 0.4))
        a0 = a1
    E.append(spin(a, E[0]["id"], (x, y), 6))
    return E


def people(a, x, y, n=4, gap=260, d=0.0):
    E = []
    for q in range(n):
        j = uid("pp")
        px = x + gap * q
        E += [O(a, px, y, 36, c="ink", fill="paper", idp=j), P(a, f"M{px},{y + 36} L{px},{y + 150} M{px - 45},{y + 80} L{px + 45},{y + 80} M{px},{y + 150} L{px - 30},{y + 240} M{px},{y + 150} L{px + 30},{y + 240}", c="ink", w=6, idp=j),
              pop(a, j, d + 0.08 * q), bob(a, j, 6, 1.0 + 0.25 * q)]
    return E


def sky(a, n=5, d=0.0, y=300):
    E = []
    for q in range(n):
        E += galaxy(a, 250 + 350 * q, y + 80 * (q % 2), 50, d + 0.05 * q, c=["blue", "red", "green", "gold", "blue"][q % 5], rpm=20 + 8 * q)
    return E


# ---------- boards ----------
bd(0, pie(0, 600, 520, 260, 0.0), BIG(0, 1350, 430, "68%", c="red", d=0.2, s=170), T(0, 1350, 600, 56, "of the universe", c="ink", d=0.4))
bd(0.5, blob(0.5, 650, 520, 1.2, 0.0), BIG(0.5, 1350, 450, "doesn't exist?", c="red", d=0.2, s=100), ic(0.5, "question", 1350, 700, 150, 0.4, mv="wig", c="red"))
bd(1, blob(1, 700, 520, 1.1, 0.0), BIG(1, 1400, 450, "dark energy", c="ink", d=0.2, s=110), galaxy(1, 1600, 700, 60, 0.3))
bd(1.5, people(1.5, 400, 400, 3, 230, 0.0), blob(1.5, 1450, 520, 0.9, 0.2), arr(1.5, 1000, 520, 1200, 520, c="red", d=0.4), T(1.5, 700, 270, 60, "mathematicians", c="blue", d=0.3))
bd(2, BIG(2, 960, 300, "Einstein's equations", c="blue", d=0.0, s=100), T(2, 960, 480, 90, "G = 8πT", c="ink", d=0.3), ic(2, "atom", 450, 650, 150, 0.4, mv="spin"),
   galaxy(2, 1450, 650, 70, 0.5))
bd(2.5, blob(2.5, 700, 520, 1.0, 0.0), cross(2.5, 700, 520, d=0.5), T(2.5, 1350, 450, 64, "without it?", c="red", d=0.3), ic(2.5, "question", 1350, 650, 140, 0.4, mv="wig", c="red"))
bd(3, BIG(3, 1150, 400, "Brain teaser", c="red", d=0.0, s=120), ic(3, "question", 450, 450, 260, 0.2, mv="wig", c="red"), ic(3, "flame", 1700, 650, 140, 0.4, mv="wig", c="red"),
   ic(3, "gear", 1150, 620, 140, 0.5, mv="spin"))
bd(3.5, pencil(3.5, 600, 880, 1.0, 0.0, amp=6), galaxy(3.5, 1200, 400, 80, 0.2), galaxy(3.5, 1550, 600, 60, 0.3, c="red"),
   T(3.5, 1350, 800, 56, "knock over cosmology?", c="red", d=0.5))
bd(4, BIG(4, 960, 260, "expanding", c="blue", d=0.0, s=120), arr(4, 900, 520, 500, 520, c="blue", d=0.2), arr(4, 1020, 520, 1420, 520, c="blue", d=0.2), galaxy(4, 960, 520, 70, 0.1),
   ripple(4, 960, 520, 0.4, 3))
bd(4.5, dough(4.5, 960, 600, 0.0), ic(4.5, "flame", 960, 880, 100, 0.3, mv="wig", c="red"), T(4.5, 960, 280, 60, "like rising bread", c="ink", d=0.2))
bd(5, dough(5, 800, 600, 0.0, grow=False, n=7), T(5, 1450, 400, 60, "raisins =", c="ink", d=0.2), T(5, 1450, 500, 60, "galaxies", c="blue", d=0.3), galaxy(5, 1450, 700, 60, 0.4))
gs = []
for q in range(5):
    j = uid("gp")
    gx = 960 + (q - 2) * 120
    gs += galaxy(5.5, gx, 520, 45, 0.05 * q, c=["blue", "red", "green", "gold", "blue"][q])
    gs.append(sh(5.5, gs[-4]["id"], (q - 2) * 250, (q % 2) * 80 - 40, 0.4, 1.4))
bd(5.5, gs, T(5.5, 960, 250, 60, "drifting apart", c="blue", d=0.2), T(5.5, 960, 820, 56, "all of them", c="ink", d=0.8))
bd(6, ic(6, "globe", 500, 550, 260, 0.0, mv="spin"), arr(6, 1300, 380, 1300, 700, c="red", d=0.2), T(6, 1300, 300, 60, "gravity pulls", c="red", d=0.3), galaxy(6, 1650, 500, 60, 0.4))
bd(6.5, ball(6.5, 960, 800, 0.0, up=-450), people(6.5, 600, 600, 1, 0, 0.0), T(6.5, 1400, 400, 60, "slower...", c="blue", d=0.3),
   T(6.5, 1400, 520, 60, "and slower", c="blue", d=0.9))
bd(7, BIG(7, 960, 260, "1998", c="blue", d=0.0, s=150), boom(7, 600, 600, 0.3), boom(7, 1300, 650, 0.6, r=70), ic(7, "magnifier", 1650, 500, 150, 0.4, mv="wig"))
bd(7.5, boom(7.5, 500, 500, 0.0, r=80), arr(7.5, 650, 500, 1050, 500, c="red", d=0.2), BIG(7.5, 1400, 500, "the opposite", c="red", d=0.4, s=100), galaxy(7.5, 960, 750, 60, 0.3))
bd(8, galaxy(8, 960, 520, 70, 0.0), arr(8, 880, 520, 300, 520, c="red", d=0.1, w=10), arr(8, 1040, 520, 1620, 520, c="red", d=0.1, w=10), BIG(8, 960, 280, "speeding up", c="red", d=0.3, s=120),
   ripple(8, 960, 520, 0.4, 3))
bd(8.5, BIG(8.5, 960, 400, "Nobel Prize", c="gold", d=0.0, s=130), star(8.5, 500, 650, 0.2, r=60), star(8.5, 1420, 650, 0.4, r=60), ic(8.5, "check", 960, 650, 150, 0.3, mv="bob", c="green"))
bd(9, people(9, 600, 600, 1, 0, 0.0), ball(9, 960, 800, 0.0, up=-450, faster=True), T(9, 1400, 400, 60, "faster", c="red", d=0.4), T(9, 1400, 520, 70, "and FASTER", c="red", d=0.9))
bd(9.5, ball(9.5, 960, 750, 0.0, up=-550, faster=True), ic(9.5, "question", 500, 450, 200, 0.2, mv="wig", c="red"), ic(9.5, "rocket", 1450, 600, 150, 0.4, mv="bob"))
bd(10, blob(10, 960, 560, 1.1, 0.0), arr(10, 1250, 560, 1650, 560, c="red", d=0.3), arr(10, 670, 560, 270, 560, c="red", d=0.3), T(10, 960, 260, 60, "something pushes", c="ink", d=0.2))
bd(10.5, blob(10.5, 650, 560, 1.0, 0.0), BIG(10.5, 1350, 450, "Dark Energy", c="ink", d=0.2, s=110), T(10.5, 1350, 600, 50, "(name tag)", c="muted", d=0.5), star(10.5, 1650, 700, 0.6, r=40))
bd(11, pie(11, 700, 540, 260, 0.0), T(11, 1350, 400, 60, "standard model", c="blue", d=0.2), ic(11, "atom", 1350, 600, 150, 0.4, mv="spin"))
bd(11.5, pie(11.5, 600, 540, 240, 0.0), BIG(11.5, 1350, 420, "68%", c="red", d=0.2, s=170), T(11.5, 1350, 600, 50, "dark energy", c="ink", d=0.4), T(11.5, 1350, 680, 44, "27% dark matter, 5% us", c="muted", d=0.6))
bd(12, people(12, 450, 400, 4, 330, 0.0), [x for q in range(4) for x in ic(12, "question", 450 + 330 * q, 300, 90, 0.2 + 0.1 * q, mv="wig", c="red")])
bd(12.5, blob(12.5, 960, 520, 1.2, 0.0), BIG(12.5, 960, 250, "???", c="red", d=0.2, s=150), ic(12.5, "magnifier", 1550, 650, 150, 0.4, mv="wig"))
bd(13, BIG(13, 960, 380, "Twist 1", c="red", d=0.0, s=150), ic(13, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), ic(13, "clock", 1470, 450, 150, 0.4, mv="spin"))
bd(13.5, BIG(13.5, 960, 280, "1917", c="blue", d=0.0, s=150), T(13.5, 960, 480, 90, "+ Λ", c="red", d=0.3), people(13.5, 500, 500, 1, 0, 0.2), ic(13.5, "clock", 1450, 550, 160, 0.4, mv="spin"))
bd(14, people(14, 600, 450, 1, 0, 0.0), T(14, 1200, 400, 64, "\"my biggest blunder\"", c="red", d=0.2), cross(14, 1200, 600, d=0.5), T(14, 1200, 760, 44, "(reportedly)", c="muted", d=0.6))
bd(14.5, blob(14.5, 700, 520, 1.0, 0.0), arr(14.5, 1500, 520, 1000, 520, c="green", d=0.2), BIG(14.5, 1450, 330, "it's back", c="green", d=0.4, s=110), ic(14.5, "rocket", 1550, 650, 140, 0.5, mv="bob"))
bd(15, T(15, 650, 380, 70, "UC Davis", c="blue", d=0.0), T(15, 1300, 380, 70, "UCL", c="red", d=0.2), people(15, 650, 500, 1, 0, 0.2), people(15, 1300, 500, 1, 0, 0.3),
   arr(15, 800, 600, 1150, 600, c="ink", d=0.4))
pap = uid("pap")
bd(15.5, [R(15.5, 760, 300, 400, 500, c="ink", fill="paper", idp=pap, sw=5), pop(15.5, pap, 0.0), wig(15.5, pap, (960, 800), 3, 1.2)], T(15.5, 960, 420, 50, "Proc. R. Soc. A", c="blue", d=0.2),
   [P(15.5, f"M820,{500 + 60 * q} L1100,{500 + 60 * q}", c="muted", w=5, idp=f"ln155{q}") for q in range(4)], [pop(15.5, [f"ln155{q}" for q in range(4)], 0.3)],
   star(15.5, 1350, 400, 0.5, r=40), ic(15.5, "check", 500, 500, 140, 0.4, mv="bob", c="green"))
bd(16, ic(16, "map_pin", 960, 300, 140, 0.0, mv="bob", c="red"), pie(16, 600, 620, 200, 0.1), T(16, 1350, 600, 60, "the standard model", c="blue", d=0.3))
bd(16.5, blob(16.5, 600, 560, 0.9, 0.0), T(16.5, 1350, 450, 60, "dark energy", c="ink", d=0.2), T(16.5, 1350, 560, 60, "built in", c="red", d=0.4), galaxy(16.5, 1350, 750, 60, 0.4))
bd(17, pencil(17, 800, 900, 1.2, 0.0, amp=3), BIG(17, 1400, 400, "Penny", c="gold", d=0.3, s=120), T(17, 1400, 560, 56, "the pencil", c="ink", d=0.4))
bd(17.5, pencil(17.5, 960, 900, 1.3, 0.0, amp=1), check(17.5, 1400, 500, d=0.4), T(17.5, 1400, 700, 60, "perfect balance", c="green", d=0.5), star(17.5, 500, 500, 0.3, r=40))
bd(18, pencil(18, 700, 900, 1.2, 0.0, amp=1), arr(18, 450, 500, 650, 500, c="blue", d=0.2), arr(18, 950, 500, 750, 500, c="blue", d=0.2), T(18, 1400, 450, 60, "forces cancel", c="blue", d=0.4),
   check(18, 1400, 620, d=0.6))
bd(18.5, pencil(18.5, 600, 900, 1.1, 0.0, amp=2), BIG(18.5, 1300, 420, "a real solution", c="green", d=0.2, s=90), T(18.5, 1300, 560, 70, "F = 0", c="ink", d=0.4))
wind = uid("wd")
bd(19, pencil(19, 960, 900, 1.2, 0.0, amp=3), [P(19, "M200,450 C350,400 450,500 600,450 M220,550 C370,500 470,600 620,550", c="blue", w=6, idp=wind), pop(19, wind, 0.2),
   sh(19, wind, 200, 0, 0.4, 1.0)], T(19, 1450, 400, 56, "one tiny breath...", c="blue", d=0.3))
bd(19.5, pencil(19.5, 960, 900, 1.2, 0.0, fall=0.2, mood="o"), BIG(19.5, 1400, 330, "falls!", c="red", d=0.3, s=130), star(19.5, 1250, 850, 0.7, r=40))
bd(20, BIG(20, 960, 380, "Twist 2", c="red", d=0.0, s=150), ic(20, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), ic(20, "question", 1470, 450, 150, 0.4, mv="wig", c="red"))
bd(20.5, pencil(20.5, 700, 900, 1.1, 0.0, amp=5, mood="o"), T(20.5, 1350, 380, 64, "our universe model", c="blue", d=0.2), T(20.5, 1350, 500, 64, "= the pencil", c="red", d=0.4),
   galaxy(20.5, 700, 260, 60, 0.3), galaxy(20.5, 1350, 700, 60, 0.5, c="red"))
bd(21, pencil(21, 600, 900, 1.0, 0.0, amp=8, mood="o"), BIG(21, 1300, 420, "unstable", c="red", d=0.2, s=130), ic(21, "flame", 1300, 650, 140, 0.4, mv="wig", c="red"))
bd(21.5, ripple(21.5, 650, 520, 0.0, 4), arr(21.5, 950, 520, 1200, 520, c="red", d=0.6), T(21.5, 1500, 450, 60, "ripples grow", c="red", d=0.7), T(21.5, 1500, 560, 50, "on huge scales", c="ink", d=0.8))
bd(22, people(22, 600, 420, 1, 0, 0.0), T(22, 1200, 400, 60, "lead author", c="blue", d=0.2), T(22, 1200, 520, 60, "Blake Temple", c="ink", d=0.3), ic(22, "atom", 1600, 700, 120, 0.4, mv="spin"))
bd(22.5, pencil(22.5, 600, 900, 1.0, 0.0, amp=6), cross(22.5, 600, 500, d=0.4), ic(22.5, "globe", 1300, 500, 220, 0.2, mv="spin"), T(22.5, 1300, 760, 56, "nature won't pick it", c="red", d=0.5))
hill, hb = uid("hl"), uid("hb")
bd(23, [P(23, "M200,850 Q600,850 960,350 Q1320,850 1720,850", c="ink", w=7, idp=hill), pop(23, hill, 0.0), O(23, 960, 310, 45, c="ink", fill="red", idp=hb), pop(23, hb, 0.2),
        spin(23, hb, (960, 310), 60), sh(23, hb, 450, 480, 0.8, 1.0)], T(23, 960, 200, 56, "what if it already slid off?", c="blue", d=0.3))
bd(23.5, galaxy(23.5, 700, 500, 60, 0.0), arr(23.5, 780, 500, 1300, 500, c="red", d=0.2, w=10), BIG(23.5, 1350, 300, "looks like", c="ink", d=0.3, s=80),
   BIG(23.5, 1350, 700, "acceleration", c="red", d=0.5, s=100), ripple(23.5, 700, 500, 0.4, 2))
bd(24, galaxy(24, 600, 500, 70, 0.0), galaxy(24, 1000, 600, 60, 0.1, c="red"), galaxy(24, 1400, 450, 50, 0.2, c="green"), T(24, 960, 800, 60, "and it would need...", c="ink", d=0.3))
bd(24.5, blob(24.5, 960, 520, 1.1, 0.0), cross(24.5, 960, 520, d=0.3), BIG(24.5, 960, 260, "NO dark energy", c="red", d=0.4, s=110))
bd(25, BIG(25, 960, 380, "Twist 3", c="red", d=0.0, s=150), ic(25, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), T(25, 960, 600, 60, "not alone", c="blue", d=0.4))
bd(25.5, ic(25.5, "magnifier", 450, 500, 220, 0.0, mv="wig"), galaxy(25.5, 900, 450, 50, 0.2), galaxy(25.5, 1150, 600, 45, 0.3, c="red"),
   galaxy(25.5, 1400, 420, 55, 0.4, c="green"), BIG(25.5, 1150, 800, "DESI", c="blue", d=0.5, s=100))
bd(26, blob(26, 650, 520, 1.0, 0.0), arr(26, 950, 520, 1150, 520, c="blue", d=0.3), blob(26, 1400, 520, 0.6, 0.4), T(26, 960, 250, 60, "changing?", c="red", d=0.5))
bd(26.5, T(26.5, 960, 380, 90, "Λ = constant?", c="ink", d=0.0), cross(26.5, 960, 580, d=0.4), ic(26.5, "question", 450, 600, 160, 0.3, mv="wig", c="red"), ic(26.5, "gear", 1450, 600, 160, 0.3, mv="spin"))
bd(27, BIG(27, 960, 380, "Fine print", c="blue", d=0.0, s=130), ic(27, "ruler", 500, 620, 150, 0.2, mv="wig"), T(27, 1250, 620, 60, "pure math", c="red", d=0.4))
bd(27.5, ic(27.5, "magnifier", 600, 500, 260, 0.0, mv="wig"), galaxy(27.5, 600, 500, 40, 0.2), cross(27.5, 1300, 450, d=0.4), T(27.5, 1300, 650, 56, "not tested on data", c="red", d=0.5))
bd(28, people(28, 450, 380, 4, 330, 0.0), [x for q in range(4) for x in check(28, 450 + 330 * q, 260, d=0.2 + 0.1 * q)])
bd(28.5, blob(28.5, 650, 520, 1.0, 0.0), check(28.5, 1300, 420, d=0.3), T(28.5, 1300, 620, 56, "still the best fit", c="green", d=0.4))
bd(29, T(29, 960, 300, 64, "new idea needs", c="ink", d=0.0), BIG(29, 960, 460, "a prediction", c="blue", d=0.2, s=110), ic(29, "ruler", 600, 700, 140, 0.4, mv="wig"), ic(29, "magnifier", 1300, 700, 140, 0.5, mv="wig"))
bd(29.5, BIG(29.5, 960, 380, "next step", c="green", d=0.0, s=130), arr(29.5, 600, 600, 1300, 600, c="green", d=0.3), ic(29.5, "rocket", 1500, 600, 140, 0.5, mv="bob"))
bd(30, pencil(30, 600, 900, 1.0, 0.0, amp=6), ic(30, "question", 1250, 450, 220, 0.2, mv="wig", c="red"), galaxy(30, 1550, 700, 60, 0.4))
bd(30.5, pencil(30.5, 960, 900, 1.2, 0.0, amp=8, mood="o"), galaxy(30.5, 960, 340, 60, 0.2), BIG(30.5, 1450, 450, "maybe.", c="red", d=0.4, s=120), galaxy(30.5, 500, 500, 50, 0.3, c="red"))
bd(31, BIG(31, 960, 300, "68%", c="red", d=0.0, s=160), pencil(31, 960, 920, 0.8, 0.2, amp=8))
bd(31.5, pencil(31.5, 960, 900, 1.1, 0.0, amp=10), pie(31.5, 960, 260, 120, 0.2), T(31.5, 1450, 600, 56, "a balancing act", c="blue", d=0.4))
bd(32, blob(32, 650, 520, 1.1, 0.0), check(32, 1300, 400, d=0.3), T(32, 1300, 600, 60, "real...", c="green", d=0.4))
bd(32.5, blob(32.5, 650, 520, 1.1, 0.0), BIG(32.5, 1300, 450, "and WEIRD", c="red", d=0.2, s=120), star(32.5, 1300, 700, 0.5, r=50))
bd(33, ic(33, "map_pin", 600, 450, 200, 0.0, mv="bob", c="red"), sky(33, 3, 0.2, 650), T(33, 1250, 400, 60, "our best map", c="blue", d=0.3))
bd(33.5, pencil(33.5, 960, 900, 1.3, 0.0, amp=6, fall=1.6, mood="o"), BIG(33.5, 1450, 330, "on its tip", c="red", d=0.3, s=100), galaxy(33.5, 450, 400, 60, 0.4))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"DESI": "Desi", "UC Davis": "U C Davis", "UCL": "U C L"})
