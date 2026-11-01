"""Daily science short 2026-11-01 (English): "Trees Have Muscles?"
News: INRAE study, New Phytologist (2026), DOI 10.1111/nph.71238: "Proprioception drives tension wood formation for autotropic
straightening and postural control in trees" (Caulus, Hartmann, Badel, Ploquin, Brunel-Michac, Ruelle, Decourteix, Moulia).
Trending: ScienceDaily "Top Science", Oct 31, 2026 (#1 of that day): "Scientists Discover the Hidden 'Muscles' Trees Use to Straighten Themselves"
Facts used (https://www.sciencedaily.com/releases/2026/10/261030003006.htm):
- Young poplars laid horizontal; stems curved upward over about 10 days.
- Then moved into a horizontal platform rotating on its axis inside a sphere lit evenly from all sides (no steady gravity, no light direction).
- Over the following weeks the curved stems straightened until nearly straight.
- Tension wood on the upper side stopped forming; identical tension wood formed on the opposite side -> like opposing muscle groups.
- 2012 INRAE (Bastien et al., PNAS): plants have proprioception.
- Moulia: "a genuine sensorimotor loop operating in the woody parts of trees"; excess internal tension can affect wood quality.
- Implications: recovery after storms, straighter timber, maybe less cereal lodging.
Our analogies (not from the paper): "close your eyes and touch your nose", biceps/triceps, robot joint encoders, "slowest gym".
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig, waves)
from popkit import cute_tree, cute_bot, stick  # noqa: E402

S = [
 ("树有肌肉。|而且它闭着眼，也知道自己歪了。", "Trees have muscles. | And they know when they are bent, even with their eyes closed."),
 ("把它压弯，|它会自己慢慢挺回来。", "Bend one over, | and it will slowly pull itself back up."),
 ("法国科学家刚刚证明了这件事，|用的是一台会转的机器。", "French scientists just showed it, | using a machine that never stops spinning."),
 ("论文刚登在《新植物学家》上。|对，这本期刊真叫这个名字。", "Their paper just came out in New Phytologist. | Yes, that is a real journal name."),
 ("先来个实验：|把一棵小杨树放倒。", "Start with an experiment: | lay a young poplar tree on its side."),
 ("大约十天，|它的茎就弯着朝上长回来。", "In about ten days, | its stem curves back up toward the sky."),
 ("这不奇怪，|树能感觉重力，也追着光走。", "No surprise there. | Trees feel gravity and chase the light."),
 ("今天的烧脑问题：|要是没有重力方向，也没有光的方向呢？", "Today's brain teaser: | what if there is no gravity direction and no light direction?"),
 ("树还知道|自己是弯的吗？", "Does the tree still know | that it is bent?"),
 ("想想看：树没有眼睛，|也没有我们那样的大脑和神经。", "Think about it: a tree has no eyes, | no brain, no nerves like ours."),
 ("研究团队造了一台机器：|一个慢慢转的平台。", "The team built a machine: | a platform that slowly rotates."),
 ("树横躺在上面，|一直转，一直转。", "The tree lies on it | and turns, and turns, and turns."),
 ("这样重力就没有固定的方向，|从树的角度看，“下面”一直在变。", "So gravity never points one steady way. | For the tree, down keeps changing."),
 ("整个装置罩在一个球里，|四面八方的光一样亮。", "The whole thing sits inside a sphere | lit equally from every side."),
 ("没有上，没有下，|也没有哪边更亮。", "No up, no down, | no bright side."),
 ("说白了：一棵放在烤肉架上转的树，|还装在一个发光的大球里。", "Basically, a tree on a rotisserie, | inside a giant glowing ball."),
 ("结果：接下来几周，|弯的茎慢慢变直了。", "The result: over the next few weeks, | the bent stems slowly straightened out."),
 ("几乎直得像|什么都没发生过。", "Almost as straight | as if nothing ever happened."),
 ("而且不是碰巧。|树的身体里有东西在拉。", "And it was not luck. | Something inside the tree was pulling."),
 ("反转一：树靠的不是重力，|是对自己形状的感觉。", "Twist one: the tree was not using gravity. | It was sensing its own shape."),
 ("这叫本体感觉。|你闭上眼也能摸到鼻子，靠的就是它。", "That sense is called proprioception. | It is how you touch your nose with your eyes closed."),
 ("二零一二年，同一家研究所就证明了：|植物有本体感觉。", "Back in 2012, the same institute showed | that plants have proprioception."),
 ("机器人也有：|每个关节里有个传感器，报告自己弯了多少。", "Robots have it too: | a sensor in every joint reports how far it is bent."),
 ("那树用什么把自己掰直？|答案是一种特别的木头。", "So how does a tree pull itself straight? | With a special kind of wood."),
 ("它叫应拉木，|长在弯的那一边。", "It is called tension wood, | and it grows along one side of the stem."),
 ("应拉木会收缩、往回拉，|就像一块肌肉。", "Tension wood shrinks and pulls, | just like a muscle."),
 ("不像你的肌肉那么快，|它是随着新木头一点点长出来的。", "Not fast, like your muscles. | It builds up as new wood grows."),
 ("树弯着朝上长回来的时候，|应拉木在上面那一侧。", "While the tree curves back up, | the tension wood forms on the upper side."),
 ("反转二，最妙：|机器一转，上面这块肌肉不长了。", "Twist two, the clever one: | once the machine starts, that upper muscle stops growing."),
 ("一模一样的应拉木，|长到了对面去。", "And identical tension wood | starts growing on the opposite side."),
 ("就像你的手臂：|二头肌把它弯起来，三头肌把它伸直。", "It is like your arm: | biceps bend it, triceps straighten it."),
 ("两边的力|慢慢扯平。", "The two pulls | slowly balance out."),
 ("树就这样|把自己掰直了。", "And that is how the tree | pulls itself straight."),
 ("想象一根旗杆，两边各拴一根绳：|拉得刚好，它就站得笔直。", "Picture a flagpole with a rope on each side: | pull both just right, and it stands tall."),
 ("研究主任说，这是树木木头里|一个真正的感觉加运动的回路。", "The research director calls it a genuine sensorimotor loop | in the woody parts of trees."),
 ("感觉到弯，就长肌肉，|再感觉，再调整。", "Feel the bend, grow the muscle, | feel again, adjust again."),
 ("这跟机器人站稳的办法|是同一个思路。", "That is the same idea a robot uses | to keep its balance."),
 ("只不过机器人一秒钟调几百次，|树要调好几个星期。", "Except a robot adjusts hundreds of times a second. | A tree takes weeks."),
 ("同一个回路，|速度天差地别。", "Same loop. | Wildly different speed."),
 ("反转三，跟你有关：|有用。", "Twist three, the useful one: | this matters."),
 ("暴风雨、山体滑坡之后，|树要靠这招重新站直。", "After storms and landslides, | trees need this trick to stand back up."),
 ("挑本体感觉更强的品种，|也许能长出更直、更好的木材。", "Breeding trees with a stronger sense of shape | might give straighter, better wood."),
 ("内部拉力太乱，|木头质量会变差。", "Messy internal tension | can make the wood worse."),
 ("研究者还想到：|也许能让麦子少倒伏。", "The researchers even hope | it could keep wheat from falling over."),
 ("农民管这叫倒伏，|会实打实地减产。", "Farmers call it lodging, | and it costs real harvest."),
 ("友情提示：这是小杨树在实验室里的实验，|大树在野外怎么样，还要再看。", "Fine print: these were young poplars in a lab. | Big trees in the wild still need checking."),
 ("“肌肉”是比喻，|木头不是真的肌肉。", "And muscle is a metaphor. | Wood is not actual muscle."),
 ("论文说这是一个细胞一个细胞控制的，|细节还在研究。", "The paper says it is controlled cell by cell. | The details are still being worked out."),
 ("所以，树闭着眼知道自己歪了吗？|知道，然后它去健身。", "So, does a tree know it is bent with its eyes closed? | Yes. Then it hits the gym."),
 ("世界上最慢的健身房，|一次训练，好几个星期。", "The slowest gym in the world. | One workout takes several weeks."),
]
TITLE = {"zh": "树也有肌肉？", "en": "Trees Have Muscles?"}

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


def tree(a, x, y, k=1.0, d=0.0, lean=0, straighten=None, mood="happy", muscle=None, flex=False):
    """lean: starting angle (deg, + = toward the right); straighten = delay to rotate back to upright."""
    i = uid("tr")
    E = cute_tree(x, y, k, a, idp=i, mood=mood, muscle=muscle) + [pop(a, [i + "_b", i + "_l"] + ([i + "_m"] if muscle else []), d)]
    if lean:
        E.append(rot(a, i + "*", lean, (x, y), 0.0, 0.01))
        if straighten is not None:
            E.append(rot(a, i + "*", 0, (x, y), straighten, 1.6))
    if muscle:
        E.append(pulse(a, i + "_m", d + 0.5))
        if flex:
            E.append({"t": "move", "at": a, "kind": "wiggle", "targets": [i + "_m"], "pivot": [x, y], "amp": 3, "hz": 3})
    return E


def platform(a, x, y, d=0.0, w=700):
    """The rotating platform: a disc seen edge-on with spinning spokes."""
    i, j = uid("pf"), uid("sp")
    E = [R(a, x - w / 2, y, w, 30, c="ink", fill="muted", idp=i), R(a, x - 20, y + 30, 40, 120, c="ink", fill="muted", idp=i), pop(a, i, d)]
    E += [O(a, x, y + 220, 70, c="blue", idp=j, sw=5), P(a, f"M{x - 70},{y + 220} L{x + 70},{y + 220} M{x},{y + 150} L{x},{y + 290}", c="blue", w=5, idp=j),
          pop(a, j, d + 0.1), spin(a, j, (x, y + 220), 50)]
    return E


def sphere(a, x, y, r=420, d=0.0):
    i = uid("sf")
    E = [O(a, x, y, r, c="blue", idp=i, sw=6), pop(a, i, d), pulse(a, i, d + 0.6)]
    for q in range(8):
        import math
        ang = q * math.pi / 4
        j = uid("ry")
        x0, y0 = x + (r + 30) * math.cos(ang), y + (r + 30) * math.sin(ang)
        x1, y1 = x + (r - 60) * math.cos(ang), y + (r - 60) * math.sin(ang)
        E += [{"t": "arrow", "at": a, "id": j, "pts": [[x0, y0], [x1, y1]], "c": "gold", "w": 6}, pop(a, j, d + 0.05 * q), pulse(a, j, d + 0.6 + 0.05 * q)]
    return E


def gravity(a, x, y, d=0.0, spinning=True):
    """A 'down' arrow that keeps turning (gravity direction changing for the tree)."""
    i = uid("gv")
    E = [{"t": "arrow", "at": a, "id": i, "pts": [[x, y - 90], [x, y + 90]], "c": "red", "w": 8}, pop(a, i, d)]
    if spinning:
        E.append(spin(a, i, (x, y), 30))
    return E


def arm(a, x, y, d=0.0, bend=True):
    """A stick arm: upper arm + forearm (rotates at the elbow), biceps (red) and triceps (blue) blobs."""
    u, f, b, t = uid("au"), uid("af"), uid("bi"), uid("tri")
    E = [P(a, f"M{x - 300},{y} L{x},{y}", c="ink", w=14, idp=u), P(a, f"M{x},{y} L{x + 280},{y}", c="ink", w=12, idp=f),
         O(a, x + 300, y, 40, c="ink", fill="paper", idp=f),
         P(a, f"M{x - 240},{y - 14} Q{x - 150},{y - 90} {x - 50},{y - 14} Z", c="red", w=4, fill="red", idp=b),
         P(a, f"M{x - 240},{y + 14} Q{x - 150},{y + 70} {x - 50},{y + 14} Z", c="blue", w=4, fill="blue", idp=t),
         pop(a, [u, f, b, t], d), rot(a, f, -70 if bend else 0, (x, y), d + 0.4, 0.8), pulse(a, b if bend else t, d + 0.5),
         rot(a, f, -10 if bend else -60, (x, y), d + 1.6, 0.8)]
    return E


def wood(a, x, y, d=0.0, side="up"):
    """A trunk cross-section bar with a red tension-wood strip that shrinks (pulls)."""
    i, j = uid("wd"), uid("tw")
    yy = y - 60 if side == "up" else y + 40
    E = [R(a, x - 400, y - 60, 800, 120, c="ink", fill="gold", idp=i), pop(a, i, d),
         R(a, x - 400, yy, 800, 20, c="red", fill="red", idp=j, sw=2), pop(a, j, d + 0.3),
         {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "x", "pivot": [x, yy], "dur": 0.9, "delay": d + 0.6, "from": 1.0, "to": 0.7},
         arr(a, x - 380, yy - 40, x - 200, yy - 40, c="red", d=d + 0.6, w=6), arr(a, x + 380, yy - 40, x + 200, yy - 40, c="red", d=d + 0.6, w=6)]
    return [e for p in E for e in (p if isinstance(p, list) else [p])]


def bot(a, x, y, k=0.8, d=0.0, mood="happy", tilt=0):
    i = uid("rb")
    E = cute_bot(x, y, k, a, idp=i, mood=mood) + [pop(a, i + "_b", d)]
    if tilt:
        E += [rot(a, i + "*", tilt, (x, y), d + 0.3, 0.5), rot(a, i + "*", 0, (x, y), d + 1.0, 0.5)]
    return E


def joint(a, x, y, d=0.0):
    i = uid("jt")
    return [O(a, x, y, 60, c="blue", fill="paper", idp=i), P(a, f"M{x},{y} L{x + 50},{y - 20}", c="red", w=6, idp=i), pop(a, i, d), spin(a, i, (x, y), 30)]


def rain(a, n=6, d=0.0):
    E = []
    for q in range(n):
        j = uid("rn")
        x = 250 + 260 * q
        E += [P(a, f"M{x},{200} L{x - 30},{280}", c="blue", w=5, idp=j), pop(a, j, d + 0.06 * q), sh(a, j, -60, 400, d + 0.1 * q, 1.2)]
    return E


def wheat(a, x, y, d=0.0, fall=False):
    i = uid("wh")
    E = [P(a, f"M{x},{y} L{x},{y - 200} M{x},{y - 200} L{x - 18},{y - 230} M{x},{y - 215} L{x + 18},{y - 245} M{x},{y - 235} L{x - 18},{y - 265}", c="gold", w=6, idp=i),
         pop(a, i, d), wig(a, i, (x, y), 4, 1.5)]
    if fall:
        E.append(rot(a, i, 70, (x, y), d + 0.6, 0.8))
    return E


def clock(a, x, y, s=140, d=0.0):
    return ic(a, "clock", x, y, s, d, mv="spin")


Z = 0
# ---------- boards ----------
bd(0, tree(0, 600, 900, 1.3, 0.0, muscle="right", flex=True), BIG(0, 1350, 330, "MUSCLES", c="red", d=0.3, s=150), arr(0, 1050, 450, 700, 650, c="red", d=0.6))
bd(0.5, tree(0.5, 500, 900, 1.2, 0.0, lean=60, straighten=0.6), ic(0.5, "eye", 1350, 350, 180, 0.2, mv="wig"), cross(0.5, 1350, 350, d=0.5), T(0.5, 1350, 600, 60, "eyes closed", c="ink", d=0.6))
bd(2, ic(2, "flask", 450, 500, 220, 0.0, mv="wig"), BIG(2, 1250, 350, "France", c="blue", d=0.2, s=120), T(2, 1250, 520, 56, "INRAE", c="ink", d=0.4), tree(2, 1250, 950, 0.6, 0.5))
bd(2.5, platform(2.5, 960, 600, 0.0), tree(2.5, 960, 600, 0.6, 0.2, lean=90), BIG(2.5, 960, 250, "never stops", c="red", d=0.4, s=100))
bd(4, tree(4, 700, 900, 1.2, 0.0), arr(4, 1100, 500, 1500, 500, c="ink", d=0.4), T(4, 1300, 350, 64, "young poplar", c="green", d=0.3))
bd(4.5, tree(4.5, 500, 850, 1.0, 0.0, lean=90), P(4.5, "M200,880 L1700,880", c="ink", w=6), T(4.5, 1300, 400, 70, "on its side", c="ink", d=0.4))
bd(5, BIG(5, 1300, 350, "10 days", c="red", d=0.0, s=150), clock(5, 1300, 620, 160, 0.3), tree(5, 500, 880, 1.0, 0.2, lean=90, straighten=0.6, muscle="left", flex=True))
bd(5.5, tree(5.5, 700, 880, 1.1, 0.0, lean=50, straighten=0.3, muscle="left"), ic(5.5, "sun", 1450, 300, 200, 0.2, mv="spin", c="gold"), arr(5.5, 900, 500, 1300, 350, c="gold", d=0.5))
bd(6, tree(6, 600, 880, 1.0, 0.0), gravity(6, 1100, 550, 0.2, spinning=False), T(6, 1100, 750, 56, "gravity", c="red", d=0.3), ic(6, "sun", 1550, 350, 200, 0.4, mv="spin", c="gold"))
bd(6.5, tree(6.5, 600, 880, 1.0, 0.0, lean=-25, straighten=0.5), arr(6.5, 900, 450, 1350, 300, c="gold", d=0.3), ic(6.5, "sun", 1550, 300, 200, 0.2, mv="spin", c="gold"), T(6.5, 1300, 650, 60, "chase the light", c="gold", d=0.6))
bd(7, BIG(7, 1150, 360, "Brain teaser", c="red", d=0.0, s=120), ic(7, "question", 450, 450, 260, 0.2, mv="wig", c="red"), gravity(7, 1000, 700, 0.4), ic(7, "sun", 1450, 700, 140, 0.5, mv="spin", c="gold"))
bd(7.5, gravity(7.5, 500, 500, 0.0), cross(7.5, 500, 500, d=0.4), ic(7.5, "sun", 1000, 500, 180, 0.2, mv="spin", c="muted"), cross(7.5, 1000, 500, d=0.6), ic(7.5, "question", 1500, 500, 200, 0.5, mv="wig", c="red"))
bd(8, tree(8, 700, 900, 1.2, 0.0, lean=40, mood="sad"), ic(8, "question", 1350, 400, 220, 0.3, mv="wig", c="red"), T(8, 1350, 700, 60, "still bent?", c="red", d=0.5))
bd(8.5, tree(8.5, 600, 900, 1.1, 0.0, lean=40), ic(8.5, "question", 1150, 350, 140, 0.2, mv="wig", c="red"), ic(8.5, "question", 1450, 450, 180, 0.4, mv="wig", c="red"), ic(8.5, "question", 1700, 300, 120, 0.6, mv="wig", c="red"))
bd(10, ic(10, "gear", 500, 450, 220, 0.0, mv="spin"), ic(10, "gear", 700, 600, 140, 0.2, mv="spin"), BIG(10, 1300, 400, "a machine", c="blue", d=0.3, s=110), ic(10, "flask", 1300, 650, 140, 0.5, mv="wig"))
bd(10.5, platform(10.5, 960, 550, 0.0), BIG(10.5, 960, 260, "slowly rotates", c="blue", d=0.3, s=100), arr(10.5, 1400, 900, 1550, 750, c="blue", d=0.5))
bd(11, platform(11, 960, 600, 0.0), tree(11, 960, 600, 0.7, 0.2, lean=90), T(11, 960, 280, 64, "turns...", c="ink", d=0.3), ic(11, "clock", 1600, 400, 130, 0.4, mv="spin"))
bd(11.5, platform(11.5, 700, 600, 0.0), tree(11.5, 700, 600, 0.6, 0.1, lean=90), ic(11.5, "gear", 1400, 400, 180, 0.2, mv="spin"), ic(11.5, "gear", 1580, 560, 120, 0.3, mv="spin"), T(11.5, 1450, 780, 56, "and turns", c="ink", d=0.4))
bd(12, gravity(12, 600, 500, 0.0), gravity(12, 1000, 500, 0.15), gravity(12, 1400, 500, 0.3), T(12, 1000, 800, 60, "no steady down", c="red", d=0.5))
bd(12.5, tree(12.5, 600, 900, 1.0, 0.0, lean=90, mood="sad"), gravity(12.5, 1300, 500, 0.2), BIG(12.5, 1300, 800, "down = ?", c="red", d=0.4, s=100))
bd(13, sphere(13, 960, 560, 400, 0.0), tree(13, 960, 700, 0.5, 0.3, lean=90))
bd(13.5, sphere(13.5, 700, 560, 380, 0.0), ic(13.5, "sun", 1500, 400, 170, 0.2, mv="spin", c="gold"), T(13.5, 1500, 650, 56, "equal light", c="gold", d=0.4))
bd(14, cross(14, 500, 450, d=0.0), T(14, 500, 650, 70, "up", c="ink", d=0.1), cross(14, 960, 450, d=0.2), T(14, 960, 650, 70, "down", c="ink", d=0.3), gravity(14, 1450, 500, 0.4))
bd(14.5, ic(14.5, "sun", 600, 500, 220, 0.0, mv="spin", c="gold"), ic(14.5, "sun", 1300, 500, 220, 0.2, mv="spin", c="gold"), T(14.5, 960, 800, 60, "no bright side", c="ink", d=0.4))
bd(16, BIG(16, 1300, 300, "weeks", c="red", d=0.0, s=140), clock(16, 1300, 600, 150, 0.2), tree(16, 500, 900, 1.0, 0.2, lean=45, straighten=0.5))
bd(16.5, tree(16.5, 700, 900, 1.2, 0.0, lean=40, straighten=0.3), check(16.5, 1400, 450, d=0.8), T(16.5, 1400, 650, 64, "straight!", c="green", d=1.0))
bd(17, tree(17, 960, 900, 1.3, 0.0), P(17, "M960,250 L960,900", c="blue", w=3, strokeDash="dashed"), ic(17, "ruler", 1500, 500, 160, 0.3, mv="wig"), check(17, 1500, 750, d=0.5))
bd(17.5, tree(17.5, 700, 900, 1.2, 0.0), T(17.5, 1350, 450, 64, "nothing happened", c="ink", d=0.3), ic(17.5, "question", 1350, 650, 120, 0.5, mv="wig", c="red"))
bd(19, BIG(19, 960, 380, "Twist 1", c="red", d=0.0, s=150), gravity(19, 450, 500, 0.2), cross(19, 450, 500, d=0.5), tree(19, 1500, 850, 0.6, 0.3))
bd(19.5, tree(19.5, 600, 900, 1.2, 0.0, lean=30, straighten=0.5), ic(19.5, "eye", 1350, 400, 160, 0.2, mv="wig"), BIG(19.5, 1350, 650, "its own shape", c="green", d=0.4, s=90))
bd(20, T(20, 960, 300, 70, "proprioception", c="blue", d=0.0), ic(20, "eye", 450, 600, 160, 0.2, mv="wig"), cross(20, 450, 600, d=0.4), ic(20, "signal", 1450, 600, 160, 0.3, mv="bob"))
bd(20.5, O(20.5, 700, 450, 90, c="ink", fill="paper"), P(20.5, "M650,440 L690,440 M710,440 L750,440", c="ink", w=6), P(20.5, "M700,470 L690,500 L705,500", c="ink", w=5),
   arm(20.5, 1250, 600, 0.0), T(20.5, 960, 900, 56, "touch your nose", c="ink", d=0.5))
bd(22, bot(22, 700, 900, 1.2, 0.0), joint(22, 700 + 95 * 1.2 * 0 + 120, 900 - 230 * 1.2, 0.3), T(22, 1350, 400, 60, "joint sensor", c="blue", d=0.4), ic(22, "chip", 1350, 620, 140, 0.5, mv="bob"))
bd(22.5, joint(22.5, 600, 500, 0.0), joint(22.5, 960, 500, 0.15), joint(22.5, 1320, 500, 0.3), BIG(22.5, 960, 780, "bent 30°", c="red", d=0.5, s=100))
bd(23, tree(23, 600, 900, 1.1, 0.0, lean=40, mood="sad"), ic(23, "question", 1300, 400, 200, 0.2, mv="wig", c="red"), arr(23, 1150, 650, 850, 650, c="red", d=0.5))
bd(23.5, wood(23.5, 960, 550, 0.0), T(23.5, 960, 300, 64, "special wood", c="red", d=0.3))
bd(24, BIG(24, 960, 300, "tension wood", c="red", d=0.0, s=110), wood(24, 960, 650, 0.2))
bd(24.5, tree(24.5, 700, 900, 1.2, 0.0, lean=35, muscle="left", flex=True), arr(24.5, 1250, 500, 820, 600, c="red", d=0.4), T(24.5, 1400, 400, 56, "one side", c="red", d=0.3))
bd(25, wood(25, 960, 450, 0.0), arr(25, 300, 800, 700, 800, c="red", d=0.4), arr(25, 1620, 800, 1220, 800, c="red", d=0.4), T(25, 960, 800, 60, "pull", c="red", d=0.6))
bd(25.5, arm(25.5, 900, 550, 0.0), BIG(25.5, 1450, 300, "muscle", c="red", d=0.3, s=110))
bd(27, tree(27, 600, 900, 1.2, 0.0, lean=60, straighten=0.4, muscle="left", flex=True), ic(27, "sun", 1450, 300, 160, 0.2, mv="spin", c="gold"))
bd(27.5, tree(27.5, 600, 900, 1.2, 0.0, lean=70, muscle="left", flex=True), arr(27.5, 1200, 400, 750, 520, c="red", d=0.3), T(27.5, 1400, 300, 60, "upper side", c="red", d=0.4))
bd(28, BIG(28, 960, 380, "Twist 2", c="red", d=0.0, s=150), platform(28, 960, 650, 0.3, w=500), ic(28, "flame", 450, 450, 140, 0.4, mv="wig", c="red"))
bd(28.5, platform(28.5, 960, 600, 0.0), tree(28.5, 960, 600, 0.6, 0.1, lean=90, muscle="left"), cross(28.5, 1350, 400, d=0.5), T(28.5, 1350, 300, 56, "stops", c="red", d=0.6))
bd(29, tree(29, 600, 900, 1.2, 0.0, lean=60, muscle="right", flex=True), arr(29, 1250, 600, 820, 700, c="blue", d=0.3), BIG(29, 1400, 350, "other side!", c="blue", d=0.4, s=100))
bd(29.5, tree(29.5, 550, 900, 1.0, 0.0, muscle="left", flex=True), tree(29.5, 1350, 900, 1.0, 0.2, muscle="right", flex=True), T(29.5, 960, 280, 60, "identical", c="ink", d=0.5), arr(29.5, 800, 500, 1100, 500, c="ink", d=0.4))
bd(30, arm(30, 900, 600, 0.0, bend=True), T(30, 960, 250, 64, "your arm", c="ink", d=0.2))
bd(30.5, arm(30.5, 900, 600, 0.0, bend=False), T(30.5, 600, 300, 56, "biceps: bend", c="red", d=0.3), T(30.5, 1350, 300, 56, "triceps: straighten", c="blue", d=0.5))
bd(31, arr(31, 300, 550, 900, 550, c="red", d=0.0, w=10), arr(31, 1620, 550, 1020, 550, c="blue", d=0.0, w=10), ic(31, "block_force", 960, 550, 160, 0.3, mv="wig"))
bd(31.5, T(31.5, 960, 300, 70, "balance", c="green", d=0.0), check(31.5, 960, 500, d=0.3), arm(31.5, 900, 750, 0.2, bend=False))
bd(32, tree(32, 700, 900, 1.3, 0.0, lean=45, straighten=0.4, muscle="right", flex=True), BIG(32, 1450, 350, "pull!", c="red", d=0.3, s=110))
bd(32.5, tree(32.5, 800, 900, 1.3, 0.0, lean=20, straighten=0.2), check(32.5, 1450, 450, d=0.6), T(32.5, 1450, 650, 64, "straight", c="green", d=0.7))
bd(34, T(34, 960, 260, 60, "sensorimotor loop", c="blue", d=0.0), ic(34, "eye", 600, 550, 150, 0.2, mv="wig"), arr(34, 720, 550, 1200, 550, c="blue", d=0.3), ic(34, "spring", 1350, 550, 150, 0.4, mv="wig"),
   arr(34, 1300, 700, 650, 700, c="red", d=0.6))
bd(34.5, tree(34.5, 960, 900, 1.2, 0.0, muscle="left", flex=True), T(34.5, 960, 260, 60, "in the wood", c="ink", d=0.3), ic(34.5, "signal", 1500, 500, 150, 0.4, mv="bob"))
bd(35, ic(35, "eye", 450, 550, 180, 0.0, mv="wig"), arr(35, 600, 550, 850, 550, c="ink", d=0.2), tree(35, 1100, 850, 0.7, 0.3, muscle="left", flex=True), T(35, 1100, 300, 56, "feel, grow", c="red", d=0.4))
bd(35.5, ic(35.5, "gear", 600, 500, 200, 0.0, mv="spin"), arr(35.5, 800, 500, 1150, 500, c="blue", d=0.2), arr(35.5, 1150, 650, 800, 650, c="blue", d=0.5), ic(35.5, "gear", 1350, 550, 200, 0.3, mv="spin"))
bd(36, bot(36, 700, 900, 1.2, 0.0, tilt=12), T(36, 1350, 400, 64, "same idea", c="blue", d=0.3), tree(36, 1350, 950, 0.5, 0.4))
bd(36.5, bot(36.5, 960, 900, 1.3, 0.0, tilt=-15), arr(36.5, 600, 500, 800, 500, c="red", d=0.6), check(36.5, 1450, 450, d=1.2))
bd(37, bot(37, 500, 900, 1.0, 0.0, tilt=10), BIG(37, 1250, 380, "100s / second", c="red", d=0.3, s=100), ic(37, "clock", 1250, 650, 150, 0.4, mv="spin"))
bd(37.5, tree(37.5, 500, 900, 1.0, 0.0, lean=30, straighten=0.8), BIG(37.5, 1250, 380, "weeks", c="green", d=0.3, s=140), ic(37.5, "clock", 1250, 650, 150, 0.4, mv="spin"))
bd(39, BIG(39, 960, 380, "Twist 3", c="red", d=0.0, s=150), tree(39, 450, 850, 0.6, 0.2), ic(39, "check", 1470, 450, 140, 0.4, mv="bob", c="green"))
bd(39.5, BIG(39.5, 960, 400, "it matters", c="green", d=0.0, s=130), ic(39.5, "gear", 500, 650, 140, 0.2, mv="spin"), ic(39.5, "globe", 1400, 650, 140, 0.3, mv="spin"))
bd(40, rain(40, 6, 0.0), ic(40, "wind", 1500, 350, 180, 0.2, mv="wig"), tree(40, 700, 900, 1.0, 0.3, lean=0, mood="sad"))
bd(40.5, tree(40.5, 700, 900, 1.1, 0.0, lean=70, straighten=0.4), P(40.5, "M200,900 L1700,900", c="ink", w=6), T(40.5, 1350, 400, 60, "stand back up", c="green", d=0.5))
bd(41, tree(41, 500, 900, 0.8, 0.0), tree(41, 900, 900, 0.8, 0.15), tree(41, 1300, 900, 0.8, 0.3), T(41, 900, 230, 56, "stronger sense", c="blue", d=0.4))
bd(41.5, R(41.5, 400, 500, 1100, 100, c="ink", fill="gold"), check(41.5, 1650, 550, d=0.4), BIG(41.5, 960, 300, "straighter wood", c="green", d=0.2, s=100), ic(41.5, "ruler", 960, 750, 140, 0.5, mv="wig"))
bd(42, wood(42, 960, 500, 0.0), cross(42, 960, 780, d=0.6), T(42, 960, 260, 60, "messy tension", c="red", d=0.3))
bd(42.5, R(42.5, 400, 500, 1100, 100, c="ink", fill="gold"), P(42.5, "M600,500 L650,560 L620,600 M1100,500 L1150,600", c="red", w=6), BIG(42.5, 960, 300, "worse wood", c="red", d=0.3, s=100))
bd(43, wheat(43, 600, 850, 0.0), wheat(43, 800, 850, 0.1), wheat(43, 1000, 850, 0.2), T(43, 1400, 400, 60, "wheat?", c="gold", d=0.3))
bd(43.5, wheat(43.5, 600, 850, 0.0, fall=True), wheat(43.5, 800, 850, 0.1, fall=True), wheat(43.5, 1200, 850, 0.2), check(43.5, 1400, 500, d=0.7))
bd(45, BIG(45, 960, 360, "Fine print", c="blue", d=0.0, s=130), tree(45, 500, 850, 0.5, 0.2), ic(45, "flask", 1400, 650, 150, 0.4, mv="wig"))
bd(45.5, tree(45.5, 500, 900, 1.4, 0.0), ic(45.5, "question", 1300, 450, 200, 0.3, mv="wig", c="red"), T(45.5, 1300, 700, 56, "big trees, wild", c="ink", d=0.4))
bd(46, BIG(46, 960, 350, "metaphor", c="blue", d=0.0, s=130), arm(46, 700, 700, 0.2), cross(46, 1400, 650, d=0.6))
bd(46.5, R(46.5, 500, 500, 900, 120, c="ink", fill="gold"), T(46.5, 960, 300, 60, "wood is not muscle", c="ink", d=0.2), ic(46.5, "magnifier", 1500, 600, 150, 0.4, mv="wig"))
bd(48, tree(48, 700, 900, 1.2, 0.0, lean=40, straighten=0.6), ic(48, "question", 1350, 400, 180, 0.2, mv="wig", c="red"), check(48, 1350, 650, d=1.0))
bd(48.5, tree(48.5, 700, 900, 1.3, 0.0, muscle="right", flex=True), bar(48.5, 1200, 850, 80, 250, "red", 0.3), bar(48.5, 1350, 850, 80, 350, "red", 0.5), BIG(48.5, 1350, 300, "gym", c="red", d=0.4, s=120))
bd(49, tree(49, 600, 900, 1.2, 0.0, muscle="left", flex=True), ic(49, "clock", 1300, 450, 180, 0.2, mv="spin"), T(49, 1300, 700, 60, "slowest gym", c="red", d=0.4))
bd(49.5, tree(49.5, 960, 900, 1.3, 0.0, muscle="right", flex=True), BIG(49.5, 960, 260, "1 workout = weeks", c="red", d=0.3, s=90), check(49.5, 1550, 600, d=0.8))

bd(1, tree(1, 600, 900, 1.2, 0.0, lean=70, straighten=0.5), arr(1, 1100, 400, 1100, 700, c="red", d=0.2), T(1, 1400, 400, 64, "bend it", c="red", d=0.2))
bd(1.5, tree(1.5, 700, 900, 1.2, 0.0, lean=50, straighten=0.2, muscle="left", flex=True), BIG(1.5, 1400, 400, "back up", c="green", d=0.3, s=110), check(1.5, 1400, 650, d=0.8))
bd(3, R(3, 760, 300, 400, 520, c="ink", fill="paper"), T(3, 960, 380, 44, "New Phytologist", c="green", d=0.2), tree(3, 960, 760, 0.5, 0.3), ic(3, "magnifier", 1450, 500, 160, 0.4, mv="wig"))
bd(3.5, BIG(3.5, 960, 350, "real name!", c="red", d=0.0, s=120), check(3.5, 960, 600, d=0.3), ic(3.5, "question", 500, 600, 150, 0.2, mv="wig", c="red"), tree(3.5, 1450, 900, 0.6, 0.4))
bd(9, tree(9, 700, 900, 1.2, 0.0), ic(9, "eye", 1350, 450, 180, 0.2, mv="wig"), cross(9, 1350, 450, d=0.5))
bd(9.5, ic(9.5, "signal", 600, 500, 180, 0.0, mv="bob"), cross(9.5, 600, 500, d=0.3), ic(9.5, "chip", 1300, 500, 180, 0.2, mv="bob"), cross(9.5, 1300, 500, d=0.5), tree(9.5, 960, 950, 0.5, 0.4, mood="sad"))
bd(15, platform(15, 960, 600, 0.0), tree(15, 960, 600, 0.6, 0.1, lean=90), ic(15, "flame", 1500, 400, 150, 0.3, mv="wig", c="red"), T(15, 960, 250, 60, "rotisserie", c="red", d=0.4))
bd(15.5, sphere(15.5, 960, 560, 400, 0.0), tree(15.5, 960, 700, 0.5, 0.2, lean=90, mood="sad"), T(15.5, 960, 1000, 50, "glowing ball", c="gold", d=0.5))
bd(18, ic(18, "question", 600, 500, 200, 0.0, mv="wig", c="red"), cross(18, 600, 500, d=0.4), tree(18, 1300, 900, 1.0, 0.2, lean=30, straighten=0.5))
bd(18.5, tree(18.5, 800, 900, 1.3, 0.0, lean=40, straighten=0.4, muscle="left", flex=True), arr(18.5, 1350, 500, 850, 600, c="red", d=0.3), BIG(18.5, 1450, 350, "pulling", c="red", d=0.3, s=110))
bd(21, BIG(21, 960, 330, "2012", c="blue", d=0.0, s=150), ic(21, "flask", 500, 650, 150, 0.2, mv="wig"), ic(21, "clock", 1400, 650, 150, 0.3, mv="spin"))
bd(21.5, tree(21.5, 600, 900, 1.1, 0.0, lean=20, straighten=0.4), ic(21.5, "eye", 1300, 400, 160, 0.2, mv="wig"), check(21.5, 1300, 650, d=0.5))
bd(26, arm(26, 900, 550, 0.0), ic(26, "clock", 1500, 350, 150, 0.2, mv="spin"), cross(26, 1500, 650, d=0.4))
bd(26.5, wood(26.5, 960, 450, 0.0), bar(26.5, 700, 900, 100, 150, "gold", 0.3), bar(26.5, 900, 900, 100, 230, "gold", 0.5), bar(26.5, 1100, 900, 100, 310, "gold", 0.7))
bd(33, P(33, "M960,900 L960,250", c="ink", w=12), arr(33, 960, 300, 500, 850, c="red", d=0.3), arr(33, 960, 300, 1420, 850, c="blue", d=0.5), T(33, 960, 200, 56, "flagpole", c="ink", d=0.2))
bd(33.5, tree(33.5, 960, 900, 1.3, 0.0, lean=-15, straighten=0.4, muscle="left", flex=True), check(33.5, 1500, 450, d=0.8), BIG(33.5, 1500, 650, "tall", c="green", d=0.9, s=110))
bd(38, ic(38, "gear", 600, 500, 200, 0.0, mv="spin"), ic(38, "gear", 1300, 500, 200, 0.2, mv="spin"), T(38, 960, 800, 64, "same loop", c="blue", d=0.3))
bd(38.5, bot(38.5, 500, 900, 0.9, 0.0, tilt=10), T(38.5, 960, 450, 120, "vs", c="ink", d=0.2), tree(38.5, 1400, 900, 0.9, 0.3, lean=20, straighten=0.6))
bd(44, wheat(44, 600, 850, 0.0, fall=True), wheat(44, 800, 850, 0.1, fall=True), wheat(44, 1000, 850, 0.2, fall=True), T(44, 1400, 400, 64, "lodging", c="red", d=0.3))
bd(44.5, bar(44.5, 700, 900, 140, 450, "gold", 0.0), bar(44.5, 1000, 900, 140, 250, "red", 0.3), arr(44.5, 1300, 400, 1300, 750, c="red", d=0.5), BIG(44.5, 1500, 300, "less grain", c="red", d=0.4, s=80))
bd(47, ic(47, "magnifier", 600, 500, 220, 0.0, mv="wig"), ic(47, "molecule", 1300, 500, 200, 0.2, mv="spin"), T(47, 960, 850, 56, "cell by cell", c="blue", d=0.4))
bd(47.5, ic(47.5, "question", 960, 450, 220, 0.0, mv="wig", c="red"), ic(47.5, "flask", 500, 650, 150, 0.2, mv="wig"), ic(47.5, "gear", 1450, 650, 150, 0.3, mv="spin"))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"INRAE": "in ray", "Phytologist": "fie tall a gist"})
