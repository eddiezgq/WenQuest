"""Daily science short 2026-10-18 (English): "Doritos dye made this chicken see-through?"
News: Hacker News front page 2026-10-17 (#9, 242 points, Hacker News Digest zeli.app/digest/2026-10-17): a home experimenter
("Casual Physics Enjoyer", written up by Cook if Ya 2026-10-17) soaked a ~2 mm slice of raw chicken breast in tartrazine (Yellow 5,
the dye in Doritos) for six hours: partly translucent, grid faintly visible, gummy; a water control stayed opaque; ~0.56 M crystallized
on the meat; the paper used 40 C and a shaker; "partial transparency but not to the degree of the paper".
Background: Ou, Hong et al., Science 2024 (Stanford, doi 10.1126/science.adm6869): tartrazine rubbed on living mice made skin
see-through in minutes, organs/vessels visible, reversible by washing, no significant toxicity reported (Forbes 2024-09-12, WaPo).
Physics: scattering at water/lipid-protein boundaries; index matching; strong absorption (blue) raises refractive index at nearby longer
wavelengths (Kramers-Kronig). Indices "about 1.33" and "around 1.45" said as approximate.
Character: Chip, a little photon (running gag: "Chip just wants to get through"). No hand.
    python3 make.py <kokoro model dir> | --fake | --boards-only   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import stick  # noqa: E402

S = [
 ("这块生鸡肉是透明的。|秘密配料？多力多滋薯片里的黄色染料。", "This raw chicken is see-through. | The secret ingredient? Doritos dye."),
 ("这周，一位业余玩家把一片鸡胸肉泡进黄色食用色素。|下面的格子透了出来。", "This week, a home experimenter soaked chicken breast in yellow food dye. | And a grid showed through it."),
 ("今天的问题：一种黄色染料，怎么能让肉变透明？", "Today's question: how can a yellow dye make meat clear?"),
 ("先认识今天的主角：小光，一颗光子，一小包光。", "Meet our narrator: Chip. Chip is a photon, a tiny packet of light."),
 ("小光只有一个心愿：穿过去。", "Chip has one dream in life: to get through."),
 ("先问：鸡肉为什么本来不透明？|它大部分是水，而水是透明的。", "First: why isn't chicken see-through already? | It's mostly water. And water is clear."),
 ("蛋白质和脂肪，单独看也是透明的。|可混在一起，就成了一团雾。", "Proteins and fats are clear on their own, too. | But mix them up, and you get fog."),
 ("小光每次从水跨进脂肪，都会拐一下弯。这叫折射。", "Every time Chip crosses from water into fat, it bends a little. That's refraction."),
 ("一片肉里有数不清的这种边界。|小光像弹珠台里的球，到处乱撞，出不去。", "A slice of meat has countless borders like that. | Chip bounces like a pinball and never gets out straight."),
 ("牛奶是白的，云是白的，都是这个道理：透明的东西混在一起，就会把光散射掉。", "Same reason milk is white, and clouds are white. Clear stuff, mixed up, scatters light."),
 ("办法听起来很简单：让水像脂肪一样弯光。|物理学家管这叫折射率匹配。", "The fix sounds simple: make the water bend light like the fat does. | Physicists call it index matching."),
 ("水的折射率大约一点三三，脂肪和蛋白质更高，大约一点四五。", "Water's refractive index is about 1.33. Fats and proteins are higher, around 1.45."),
 ("把差距抹平，边界就“消失”了，小光一路直穿。", "Close that gap, and the borders vanish. Chip flies straight through."),
 ("反转一：常用的办法是加糖或甘油。染料，听起来是最差的选择。", "Twist one: the usual trick is sugar or glycerol. A dye sounds like the worst possible choice."),
 ("染料会吸光，这明明是透明的反义词。", "A dye absorbs light. That's literally the opposite of see-through."),
 ("怪就怪在：一种东西强烈吸收某种颜色，旁边颜色的光就会被它弯得更厉害。|这是光学里的一条规律，叫克拉默斯-克勒尼希关系。", "Here's the weird part: something that strongly absorbs one color bends nearby colors more. | It's a rule of optics called the Kramers-Kronig relations."),
 ("柠檬黄，也叫黄色五号，专吃蓝光。|于是它让水对红光弯得更厉害。", "Tartrazine, a.k.a. Yellow 5, gobbles up blue light. | So it makes the water bend red light harder."),
 ("水的折射率被推高，靠近脂肪。雾散了，至少在红光下。", "That pushes the water's index up toward the fat's. The fog clears, at least in red light."),
 ("就像一个吵闹的派对，突然大家都说同一种语言，没人再撞来撞去。", "Like a noisy party where suddenly everyone speaks the same language. Nobody bumps into anybody."),
 ("这不是厨房传说。二零二四年，斯坦福团队把它发表在《科学》杂志上。", "This isn't kitchen folklore. In 2024, a Stanford team published it in the journal Science."),
 ("他们把染料涂在活老鼠的肚皮上。|几分钟后，皮肤变透明了。", "They rubbed the dye on the bellies of living mice. | Within minutes, the skin went clear."),
 ("不用开刀，就能看到肚子里的器官和血管。", "They could see organs and blood vessels inside, without a single cut."),
 ("洗掉染料，皮肤又变回不透明。|在老鼠身上，没发现明显的毒性。", "Wash it off, and the skin turns opaque again. | In the mice, they saw no significant toxic effects."),
 ("反转二：家里做的版本，没那么顺利。", "Twist two: the home version did not go nearly as well."),
 ("他用的鸡肉片大约两毫米厚，泡了六个小时。", "The slice was about 2 millimeters thick, soaked for six hours."),
 ("结果：部分半透明，格子隐约可见。口感呢？像橡皮糖。", "Result: partly translucent, the grid faintly visible. And the texture? Gummy."),
 ("对照组泡清水的那片，完全不透明。所以染料确实起了作用。", "The slice soaked in plain water stayed totally opaque. So the dye really did something."),
 ("染料放太多，还会在肉上结成晶体。", "Too much dye, and it crystallized right on the meat."),
 ("实验室用四十度的温水浴加摇床，他家只有一盏台灯。", "The lab used a 40 degree bath and a shaker. The kitchen had a desk lamp."),
 ("用他自己的话说：透明了一部分，没到论文的程度。", "In his own words: partial transparency, but not to the degree of the paper."),
 ("反转三：捏碎薯片没用。要的是纯染料，浓度远远超过任何零食。", "Twist three: crushed chips won't do it. You need pure dye, far stronger than any snack."),
 ("所以，吃多力多滋不会让你隐身。朋友照样看得见你，连同你橙色的手指。", "So no, eating Doritos won't make you invisible. Your friends still see you. Orange fingers and all."),
 ("科学家为什么在乎？不用切开，就能看进活的组织里面。", "Why do scientists care? Seeing inside living tissue, without cutting it open."),
 ("友情提示：它在红光下、薄组织里最好用，还是早期研究。|别在自己身上试，也别吃泡过染料的鸡肉。", "Friendly fine print: it works best in red light and thin tissue, and it's early research. | Don't try it on yourself. And don't eat dye-soaked chicken."),
 ("所以鸡肉变透明，是因为水学会了像脂肪一样弯光。", "So the chicken went clear because the water learned to bend light like fat."),
 ("小光终于穿过去了。|下一站：隐形鸡块？有消息我们告诉你。", "Chip finally gets through. | Next stop: invisible chicken nuggets? We'll keep you posted."),
]
TITLE = {"zh": "薯片染料让鸡肉变透明？", "en": "Doritos dye made this chicken see-through?"}


def chip(at, x, y, k=1.0, mood="happy"):
    """Chip the photon: a gold ball with eyes, smile and four spiky rays (rays spin)."""
    i, r = uid("ph"), uid("rays")
    E = [O(at, x, y, 44 * k, c="gold", fill="gold", idp=i), O(at, x - 15 * k, y - 8 * k, 6 * k, c="ink", fill="ink", idp=i),
         O(at, x + 15 * k, y - 8 * k, 6 * k, c="ink", fill="ink", idp=i),
         P(at, f"M{x - 16 * k},{y + 14 * k} Q{x},{y + 28 * k} {x + 16 * k},{y + 14 * k}" if mood == "happy" else
           f"M{x - 14 * k},{y + 22 * k} Q{x},{y + 10 * k} {x + 14 * k},{y + 22 * k}", c="ink", w=4, idp=i),
         P(at, f"M{x - 80 * k},{y} L{x - 58 * k},{y} M{x + 58 * k},{y} L{x + 80 * k},{y} M{x},{y - 80 * k} L{x},{y - 58 * k} "
               f"M{x},{y + 58 * k} L{x},{y + 80 * k}", c="gold", w=6, idp=r), spin(at, r, (x, y), 50),
         bob(at, i, 8 * k, 1.6)]
    return E, i, r


def slab(at, x, y, w, h, fill="muted", c="ink"):
    """A slice of chicken (rounded blob); returns elements and id."""
    i = uid("sl")
    d = (f"M{x + 40},{y} Q{x + w / 2},{y - 30} {x + w - 40},{y} Q{x + w + 20},{y + h / 2} {x + w - 40},{y + h} "
         f"Q{x + w / 2},{y + h + 30} {x + 40},{y + h} Q{x - 20},{y + h / 2} {x + 40},{y} Z")
    e = P(at, d, c=c, w=5, idp=i)
    if fill:
        e["fill"] = fill
    return [e, wig(at, i, (x + w / 2, y + h / 2), 1.2, 0.7)], i


def grid(at, x, y, w, h, n=5, c="blue"):
    i = uid("gr")
    d = " ".join(f"M{x + w * k / n},{y} L{x + w * k / n},{y + h}" for k in range(n + 1))
    d += " " + " ".join(f"M{x},{y + h * k / n} L{x + w},{y + h * k / n}" for k in range(n + 1))
    return [P(at, d, c=c, w=3, idp=i), pulse(at, i, 0.6, 1.0)], i


def dorito(at, x, y, k=1.0, d=0.0):
    i = uid("dor")
    return [P(at, f"M{x},{y - 70 * k} L{x + 62 * k},{y + 45 * k} L{x - 62 * k},{y + 45 * k} Z", c="gold", w=5, fill="gold", idp=i),
            pop(at, i, d), spin(at, i, (x, y), 30)]


def zig(at, x0, y0, d=0.0, c="gold"):
    """A zigzag scattered light path that pops in, then wiggles."""
    i = uid("zz")
    pts = [(x0, y0), (x0 + 120, y0 - 90), (x0 + 200, y0 + 60), (x0 + 330, y0 - 40), (x0 + 380, y0 + 110), (x0 + 520, y0 + 10)]
    return [P(at, "M" + " L".join(f"{a},{b}" for a, b in pts), c=c, w=5, idp=i), pop(at, i, d), wig(at, i, (x0 + 260, y0), 3, 1.4)]


def blobs(at, x, y, n=6, d=0.2, c="gold"):
    """Little fat droplets that pop in one by one and bob."""
    E = []
    for k in range(n):
        i = uid("fat")
        E += [O(at, x + 90 * (k % 3), y + 90 * (k // 3), 22 + 6 * (k % 2), c=c, idp=i, sw=4), pop(at, i, d + 0.15 * k), bob(at, i, 5, 0.9 + 0.2 * k)]
    return E


def mouse(at, x, y, k=1.0):
    i = uid("ms")
    E = [{"t": "ellipse", "at": at, "id": i, "x": x - 150 * k, "y": y - 80 * k, "w": 300 * k, "h": 160 * k, "c": "ink"},
         O(at, x - 150 * k, y - 70 * k, 40 * k, c="ink", idp=i), O(at, x - 180 * k, y - 20 * k, 7 * k, c="ink", fill="ink", idp=i),
         P(at, f"M{x + 150 * k},{y} Q{x + 260 * k},{y - 60 * k} {x + 300 * k},{y + 30 * k}", c="ink", w=4, idp=i)]
    t = uid("tail")
    E += [P(at, f"M{x + 300 * k},{y + 30 * k} Q{x + 330 * k},{y + 70 * k} {x + 310 * k},{y + 100 * k}", c="ink", w=4, idp=t),
          wig(at, t, (x + 300 * k, y + 30 * k), 14, 2.0), bob(at, i, 5, 1.2)]
    return E, i


def amb(at, n=2):
    """Background life: twinkling stars in corners (they always spin)."""
    E = star(at, 120, 120, 0.1) + star(at, 1800, 980, 0.3)
    if n > 2:
        E += star(at, 1800, 120, 0.5)
    return E


B = []
# 0 see-through chicken
a = 0
g, gi = grid(a, 660, 300, 600, 420)
s, si = slab(a, 640, 290, 640, 440, fill=None, c="gold")
ch, ci, _ = chip(a, 260, 520)
E = g + s + ch + [sh(a, ci + "*", 1400, 0, 0.8, 1.8)] + amb(a) + BIG(a, 960, 900, "SEE-THROUGH", c="red", d=0.4, s=120)
B.append(E)
# 0.5 doritos dye
a = 0.5
E = dorito(a, 600, 520, 2.4) + dorito(a, 1000, 560, 1.6, 0.4) + dorito(a, 1340, 500, 2.0, 0.8) + amb(a)
E += BIG(a, 960, 860, "Doritos dye?!", c="gold", d=0.6, s=120)
B.append(E)
# 1 soaked in yellow dye
a = 1
jar = uid("jar")
lq = uid("lq")
E = [R(a, 760, 300, 400, 520, c="ink", idp=jar), R(a, 772, 420, 376, 388, c="gold", fill="gold", idp=lq),
     {"t": "move", "at": a, "kind": "grow", "targets": [lq], "axis": "y", "from": 0.2, "to": 1, "pivot": [960, 808], "dur": 1.6, "delay": 0.2}]
s, si = slab(a, 400, 120, 300, 160)
E += s + [sh(a, si, 420, 380, 1.0, 1.2)] + amb(a, 3)
ss = stick(1500, 820, 1.0, a, idp="me1", arms="up")
E += ss + [bob(a, "me1*", 10, 1.4)] + T(a, 960, 920, 56, "yellow food dye", c="gold", d=0.4)
B.append(E)
# 1.5 a grid showed through
a = 1.5
g, gi = grid(a, 660, 280, 600, 440, n=6)
s, si = slab(a, 640, 270, 640, 460, fill="muted")
E = g + s + [{"t": "move", "at": a, "kind": "grow", "targets": [si], "axis": "x", "from": 1, "to": 0.15, "pivot": [1280, 500], "dur": 1.6, "delay": 0.5}]
E += amb(a, 3) + check(a, 1550, 500, d=1.6) + T(a, 960, 900, 60, "the grid shows through", c="blue", d=0.8)
B.append(E)
# 2 the question
a = 2
q = uid("q")
E = [{"t": "icon", "at": a, "id": q, "name": "question", "x": 1500, "y": 380, "size": 260, "c": "red"}, pop(a, q, 0.2), pulse(a, q, 1.0)]
E += dorito(a, 420, 420, 1.6, 0.2)
s, si = slab(a, 700, 300, 380, 260)
E += s + [rot(a, si, 8, (890, 430), 0.8, 0.6)] + amb(a)
E += BIG(a, 960, 860, "Yellow dye → clear meat?", c="ink", d=1.0, s=84)
B.append(E)
# 3 meet Chip
a = 3
ch, ci, _ = chip(a, 960, 460, 2.6)
E = ch + amb(a, 3) + [sh(a, ci + "*", 0, -40, 0.4, 0.8)] + star(a, 1500, 300, 0.7) + star(a, 420, 300, 1.0)
E += BIG(a, 960, 860, "Chip", c="gold", d=0.4, s=130) + T(a, 960, 980, 48, "(a photon)", c="muted", d=1.2)
B.append(E)
# 4 one dream: get through
a = 4
wl = uid("wall")
E = [R(a, 1100, 220, 120, 640, c="ink", fill="muted", idp=wl), wig(a, wl, (1160, 860), 1, 0.6)]
ch, ci, _ = chip(a, 600, 540, 1.4, mood="sad")
E += ch + [sh(a, ci + "*", 380, 0, 0.3, 0.6), sh(a, ci + "*", -200, 0, 1.0, 0.5)] + amb(a)
E += T(a, 600, 300, 64, "\"let me through!\"", c="ink", d=0.2) + BIG(a, 1550, 540, "?", c="red", d=1.4, s=150)
B.append(E)
# 5 why not see-through already
a = 5
s, si = slab(a, 600, 260, 720, 460)
E = s + [rot(a, si, -5, (960, 490), 0.4, 0.6)] + amb(a, 3)
ch, ci, _ = chip(a, 300, 490, 1.0)
E += ch + [sh(a, ci + "*", 220, 0, 0.6, 0.8)] + BIG(a, 960, 880, "Why so foggy?", c="ink", d=0.6, s=90)
B.append(E)
# 5.5 mostly water
a = 5.5
cup = uid("cup")
wt = uid("wt")
E = [R(a, 700, 300, 520, 480, c="ink", idp=cup), R(a, 712, 400, 496, 368, c="blue", fill="blue", idp=wt),
     {"t": "move", "at": a, "kind": "grow", "targets": [wt], "axis": "y", "from": 0.1, "to": 1, "pivot": [960, 768], "dur": 1.4, "delay": 0.1},
     wig(a, wt, (960, 400), 1, 1.0)]
E += BIG(a, 1520, 460, "~75%", c="blue", d=0.5, s=120) + T(a, 1520, 580, 50, "water (roughly)", c="muted", d=0.8)
E += amb(a) + check(a, 960, 880, d=1.2)
B.append(E)
# 6 proteins and fats clear on their own
a = 6
E = blobs(a, 360, 360, 6, 0.1) + amb(a)
pr = uid("pr")
E += [P(a, "M1180,380 Q1260,300 1340,380 Q1420,460 1500,380 Q1580,300 1660,380", c="green", w=7, idp=pr), pop(a, pr, 0.6), wig(a, pr, (1420, 380), 6, 1.2)]
E += T(a, 450, 640, 56, "fat", c="gold", d=0.4) + T(a, 1420, 520, 56, "protein", c="green", d=0.8) + check(a, 960, 840, d=1.2)
B.append(E)
# 6.5 mix -> fog
a = 6.5
E = blobs(a, 600, 300, 6, 0.0) + blobs(a, 1000, 360, 6, 0.3, c="green") + amb(a)
fg = uid("fog")
E += [O(a, 960, 470, 380, c="muted", fill="muted", idp=fg), pop(a, fg, 1.0, 0.6), pulse(a, fg, 1.6)]
E += BIG(a, 960, 920, "FOG", c="muted", d=1.2, s=140)
B.append(E)
# 7 refraction
a = 7
fat = uid("fatz")
E = [R(a, 960, 200, 760, 620, c="gold", fill="gold", idp=fat), pulse(a, fat, 0.2)]
E += arr(a, 200, 300, 960, 520, c="ink", d=0.2, dur=0.6) + arr(a, 960, 520, 1500, 860, c="red", d=0.9, dur=0.6)
ch, ci, _ = chip(a, 200, 300, 0.8)
E += ch + [sh(a, ci + "*", 760, 220, 0.3, 0.8), sh(a, ci + "*", 540, 340, 1.1, 0.8)] + amb(a)
E += T(a, 500, 760, 56, "water", c="blue", d=0.1) + T(a, 1340, 280, 56, "fat", c="ink", d=0.3) + BIG(a, 500, 900, "bend!", c="red", d=1.2, s=90)
B.append(E)
# 8 countless borders
a = 8
E = blobs(a, 420, 260, 6, 0.0) + blobs(a, 820, 380, 6, 0.2) + blobs(a, 1220, 260, 6, 0.4) + amb(a)
E += BIG(a, 960, 860, "countless borders", c="ink", d=0.8, s=84)
B.append(E)
# 8.5 pinball
a = 8.5
E = zig(a, 300, 420, 0.1) + zig(a, 820, 520, 0.4, c="red") + amb(a)
ch, ci, _ = chip(a, 300, 420, 0.8, mood="sad")
E += ch + [sh(a, ci + "*", 220, -120, 0.2, 0.4), sh(a, ci + "*", 160, 200, 0.6, 0.4), sh(a, ci + "*", 200, -160, 1.0, 0.4)]
E += BIG(a, 960, 880, "PINBALL", c="red", d=0.5, s=120)
B.append(E)
# 9 milk, clouds
a = 9
gl = uid("milk")
cl = uid("cloud")
E = [R(a, 360, 320, 300, 460, c="ink", fill="muted", idp=gl), pop(a, gl, 0.1), rot(a, gl, -10, (510, 780), 0.6, 0.6),
     P(a, "M1180,520 Q1180,400 1300,420 Q1360,320 1480,380 Q1600,340 1630,460 Q1720,500 1640,580 L1220,580 Q1140,570 1180,520 Z",
       c="ink", w=5, fill="muted", idp=cl), pop(a, cl, 0.6), sh(a, cl, -120, 0, 0.8, 2.0)]
E += T(a, 510, 860, 56, "milk", c="ink", d=0.2) + T(a, 1420, 700, 56, "clouds", c="ink", d=0.7) + amb(a)
E += zig(a, 760, 300, 1.2)
B.append(E)
# 10 make water bend like fat
a = 10
E = []
for k, (c_, x) in enumerate((("blue", 560), ("gold", 1360))):
    bx = uid("bx")
    E += [R(a, x - 200, 300, 400, 400, c=c_, fill=c_, idp=bx), pop(a, bx, 0.2 * k), bob(a, bx, 6, 1.0 + 0.3 * k)]
E += arr(a, 820, 500, 1100, 500, c="red", d=0.6) + T(a, 560, 780, 56, "water", c="blue", d=0.2) + T(a, 1360, 780, 56, "fat", c="ink", d=0.4)
E += amb(a) + BIG(a, 960, 920, "match them", c="ink", d=1.2, s=84)
B.append(E)
# 10.5 index matching
a = 10.5
E = []
for k in range(2):
    bx = uid("bx")
    E += [R(a, 560 + 400 * k, 300, 400, 400, c="gold", fill="gold", idp=bx), sh(a, bx, 100 - 200 * k, 0, 0.3, 1.0)]
E += arr(a, 300, 500, 1650, 500, c="red", d=0.8, dur=0.8) + amb(a, 3) + BIG(a, 960, 860, "INDEX MATCHING", c="red", d=0.6, s=96)
B.append(E)
# 11 1.33 vs 1.45
a = 11
E = bar(a, 520, 820, 220, 400, "blue", d=0.2) + bar(a, 1180, 820, 220, 520, "gold", d=0.8)
E += BIG(a, 630, 300, "1.33", c="blue", d=0.3, s=120) + BIG(a, 1290, 200, "~1.45", c="gold", d=0.9, s=120)
E += T(a, 630, 900, 52, "water", c="blue", d=0.2) + T(a, 1290, 900, 52, "fat, protein", c="ink", d=0.8) + amb(a)
gp = uid("gap")
E += [P(a, "M800,420 L1120,300", c="red", w=6, idp=gp), pop(a, gp, 1.4), pulse(a, gp, 1.8)]
B.append(E)
# 12 close the gap, straight through
a = 12
E = bar(a, 520, 820, 220, 400, "blue", d=0.0) + bar(a, 1180, 820, 220, 520, "gold", d=0.0)
gw = uid("gw")
E += [R(a, 520, 300, 220, 120, c="blue", fill="blue", idp=gw),
      {"t": "move", "at": a, "kind": "grow", "targets": [gw], "axis": "y", "pivot": [630, 420], "dur": 0.8, "delay": 0.3}]
ch, ci, _ = chip(a, 200, 600, 0.9)
E += ch + [sh(a, ci + "*", 1500, 0, 0.9, 1.2)] + arr(a, 200, 680, 1720, 680, c="red", d=1.0, dur=1.0) + amb(a)
E += BIG(a, 960, 140, "straight through!", c="green", d=1.2, s=90)
B.append(E)
# 13 sugar or glycerol
a = 13
E = []
for k in range(5):
    cu = uid("cube")
    E += [R(a, 360 + 90 * k, 300 + 30 * (k % 2), 70, 70, c="ink", fill="muted", idp=cu), pop(a, cu, 0.1 * k), rot(a, cu, 20, (395 + 90 * k, 335), 0.6 + 0.1 * k, 0.4)]
bt = uid("bt")
E += [R(a, 1340, 260, 180, 360, c="ink", fill="blue", idp=bt), pop(a, bt, 0.6), wig(a, bt, (1430, 620), 3, 1.0)]
E += T(a, 600, 480, 56, "sugar", c="ink", d=0.3) + T(a, 1430, 700, 56, "glycerol", c="blue", d=0.7)
E += dorito(a, 960, 820, 1.0, 1.4) + cross(a, 960, 820, d=1.8) + amb(a)
B.append(E)
# 14 dye absorbs light
a = 14
E = dorito(a, 960, 520, 2.4, 0.0)
for k in range(3):
    E += arr(a, 300, 360 + 160 * k, 820, 360 + 160 * k, c="gold", d=0.2 + 0.25 * k, dur=0.5)
E += BIG(a, 1500, 520, "GULP", c="red", d=1.1, s=120) + T(a, 960, 900, 56, "dyes absorb light", c="ink", d=0.4) + amb(a)
B.append(E)
# 15 absorbs one color, bends neighbours more
a = 15
cv = uid("cv")
E = [P(a, "M200,700 L700,700 Q860,700 900,300 Q940,700 1100,700 L1700,700", c="blue", w=7, idp=cv), pop(a, cv, 0.1), wig(a, cv, (900, 700), 1.5, 1.0)]
cv2 = uid("cv2")
E += [P(a, "M200,520 Q700,520 860,420 L940,640 Q1100,560 1700,560", c="red", w=7, idp=cv2), pop(a, cv2, 1.0), wig(a, cv2, (900, 520), 1.5, 1.2)]
E += T(a, 900, 220, 52, "absorbs here", c="blue", d=0.4) + T(a, 1450, 470, 52, "bends more here", c="red", d=1.3) + amb(a)
B.append(E)
# 15.5 Kramers-Kronig
a = 15.5
bk = uid("book")
E = [R(a, 760, 260, 400, 500, c="ink", fill="muted", idp=bk), pop(a, bk, 0.1), rot(a, bk, -8, (960, 760), 0.4, 0.5), bob(a, bk, 6, 1.0)]
E += T(a, 960, 430, 50, "Kramers-", c="ink", d=0.3) + T(a, 960, 510, 50, "Kronig", c="ink", d=0.5)
E += star(a, 600, 300, 0.8) + star(a, 1320, 300, 1.0) + amb(a) + BIG(a, 960, 900, "a real rule of optics", c="blue", d=1.0, s=72)
B.append(E)
# 16 Yellow 5 eats blue light
a = 16
E = dorito(a, 1240, 520, 2.2, 0.0)
for k in range(3):
    E += arr(a, 300, 380 + 140 * k, 1000, 400 + 120 * k, c="blue", d=0.2 + 0.3 * k, dur=0.6)
E += BIG(a, 600, 220, "Yellow 5", c="gold", d=0.2, s=110) + T(a, 1240, 820, 56, "nom nom blue", c="blue", d=1.2) + amb(a)
B.append(E)
# 16.5 water bends red light harder
a = 16.5
cup = uid("cup")
E = [R(a, 760, 320, 400, 440, c="ink", fill="gold", idp=cup), wig(a, cup, (960, 760), 1, 0.8)]
E += arr(a, 200, 400, 760, 520, c="red", d=0.1) + arr(a, 1160, 600, 1500, 900, c="red", d=0.7)
r_ = uid("redbend")
E += [P(a, "M760,520 L1160,600", c="red", w=6, idp=r_), pop(a, r_, 0.4)]
E += BIG(a, 1500, 300, "red bends harder", c="red", d=1.0, s=72) + amb(a)
B.append(E)
# 17 water index up toward fat; fog clears
a = 17
E = bar(a, 520, 820, 220, 400, "blue", d=0.0) + bar(a, 1180, 820, 220, 520, "gold", d=0.0)
gw = uid("gw")
E += [R(a, 520, 300, 220, 120, c="gold", fill="gold", idp=gw),
      {"t": "move", "at": a, "kind": "grow", "targets": [gw], "axis": "y", "pivot": [630, 420], "dur": 1.0, "delay": 0.3}]
fg = uid("fog")
E += [O(a, 1600, 400, 160, c="muted", fill="muted", idp=fg),
      {"t": "move", "at": a, "kind": "grow", "targets": [fg], "axis": "x", "from": 1, "to": 0.05, "pivot": [1600, 400], "dur": 1.2, "delay": 1.0}]
E += T(a, 630, 900, 52, "dyed water", c="gold", d=0.2) + BIG(a, 960, 160, "fog clears", c="green", d=1.4, s=90) + amb(a)
B.append(E)
# 18 noisy party, same language
a = 18
E = []
for k in range(4):
    pid = f"pp{k}_{uid()}"
    E += stick(400 + 360 * k, 800, 0.8, a, idp=pid, arms="up" if k % 2 else "down") + [wig(a, pid + "*", (400 + 360 * k, 800), 6, 1.5 + 0.3 * k)]
E += T(a, 960, 260, 64, "\"hello!\" \"hello!\" \"hello!\"", c="green", d=0.8) + BIG(a, 960, 140, "PARTY", c="red", d=0.2, s=90) + amb(a)
B.append(E)
# 19 Stanford, Science 2024
a = 19
jr = uid("jr")
E = [R(a, 700, 220, 520, 640, c="ink", idp=jr), pop(a, jr, 0.1), bob(a, jr, 6, 1.0), rot(a, jr, 4, (960, 860), 0.6, 0.5)]
E += T(a, 960, 330, 80, "Science", c="red", d=0.3) + BIG(a, 960, 560, "2024", c="ink", d=0.6, s=130) + T(a, 960, 760, 56, "Stanford", c="red", d=0.9)
E += star(a, 1400, 300, 1.0) + amb(a)
B.append(E)
# 20 dye on bellies of living mice
a = 20
ms, mi = mouse(a, 900, 560, 1.6)
E = ms + amb(a)
br = uid("brush")
E += [P(a, "M1400,200 L1200,440", c="gold", w=14, idp=br), sh(a, br, -200, 0, 0.4, 0.6), sh(a, br, 200, 0, 1.0, 0.6)]
E += T(a, 900, 860, 56, "living mice", c="ink", d=0.3)
B.append(E)
# 20.5 minutes -> skin clear
a = 20.5
ms, mi = mouse(a, 900, 520, 1.6)
E = ms + amb(a)
win = uid("win")
E += [O(a, 900, 540, 100, c="red", fill="gold", idp=win), pop(a, win, 0.4), pulse(a, win, 1.0)]
cl = uid("clk")
E += [O(a, 1550, 320, 90, c="ink", idp=cl)]
hd = uid("hd")
E += [P(a, "M1550,320 L1550,250", c="red", w=6, idp=hd), spin(a, hd, (1550, 320), 240)]
E += BIG(a, 900, 880, "minutes", c="red", d=0.6, s=110)
B.append(E)
# 21 organs and vessels, no cut
a = 21
ms, mi = mouse(a, 900, 520, 1.6)
E = ms + amb(a)
gut = uid("gut")
E += [P(a, "M780,520 Q840,460 900,520 Q960,580 1020,520 Q980,590 900,580 Q840,570 780,560", c="red", w=6, idp=gut), pop(a, gut, 0.3), wig(a, gut, (900, 520), 8, 1.2)]
vs = uid("vs")
E += [P(a, "M720,470 L800,440 L860,470 M940,470 L1000,440 L1080,470", c="red", w=3, idp=vs), pop(a, vs, 0.8)]
E += cross(a, 1500, 400, d=1.2) + T(a, 1500, 520, 52, "no scalpel", c="ink", d=1.2) + BIG(a, 900, 880, "organs!", c="red", d=0.6, s=100)
B.append(E)
# 22 wash off -> opaque
a = 22
ms, mi = mouse(a, 900, 520, 1.6)
E = ms + amb(a)
win = uid("win")
E += [O(a, 900, 540, 100, c="ink", fill="muted", idp=win), pop(a, win, 0.6)]
for k in range(4):
    dr = uid("drop")
    E += [O(a, 700 + 120 * k, 160, 18, c="blue", fill="blue", idp=dr), sh(a, dr, 0, 260, 0.1 + 0.2 * k, 0.8)]
E += T(a, 1500, 820, 56, "reversible", c="green", d=1.0)
B.append(E)
# 22.5 no significant toxicity
a = 22.5
ms, mi = mouse(a, 800, 560, 1.4)
E = ms + amb(a) + check(a, 1450, 440, d=0.4)
E += T(a, 1450, 600, 52, "no significant", c="green", d=0.6) + T(a, 1450, 670, 52, "toxic effects", c="green", d=0.8)
E += T(a, 960, 900, 48, "(in mice)", c="muted", d=1.2) + star(a, 1700, 300, 0.9)
B.append(E)
# 23 twist two: home version
a = 23
st = stick(700, 820, 1.2, a, idp="hx1", arms="up")
E = st + [wig(a, "hx1*", (700, 820), 5, 1.4)]
lp = uid("lamp")
E += [P(a, "M1300,820 L1300,500 L1450,380", c="ink", w=7, idp=lp), O(a, 1480, 360, 50, c="gold", fill="gold", idp=lp), pulse(a, lp, 0.5)]
E += BIG(a, 960, 160, "TWIST TWO", c="red", d=0.2, s=100) + T(a, 960, 960, 56, "home version", c="ink", d=0.8) + amb(a)
B.append(E)
# 24 2 mm, six hours
a = 24
s, si = slab(a, 300, 360, 520, 60)
E = s + BIG(a, 560, 600, "2 mm", c="ink", d=0.3, s=120) + amb(a)
cl = uid("clk")
E += [O(a, 1400, 440, 160, c="ink", idp=cl)]
hd = uid("hd")
E += [P(a, "M1400,440 L1400,320", c="red", w=7, idp=hd), spin(a, hd, (1400, 440), 180)]
E += BIG(a, 1400, 740, "6 hours", c="red", d=0.9, s=110)
B.append(E)
# 25 partly translucent, gummy
a = 25
g, gi = grid(a, 600, 300, 520, 400)
s, si = slab(a, 580, 290, 560, 420, fill="muted")
E = g + s + [{"t": "move", "at": a, "kind": "grow", "targets": [si], "axis": "x", "from": 1, "to": 0.55, "pivot": [1140, 500], "dur": 1.2, "delay": 0.3}]
gm = uid("gum")
E += [O(a, 1500, 500, 90, c="red", fill="red", idp=gm), pop(a, gm, 1.2), wig(a, gm, (1500, 500), 10, 3)]
E += T(a, 860, 860, 56, "partly translucent", c="blue", d=0.4) + BIG(a, 1500, 720, "gummy", c="red", d=1.4, s=80) + amb(a)
B.append(E)
# 26 water control opaque
a = 26
s1, i1 = slab(a, 260, 320, 560, 360, fill="ink")
s2, i2 = slab(a, 1100, 320, 560, 360, fill="gold")
E = s1 + s2 + [rot(a, i1, -4, (540, 500), 0.3, 0.5), rot(a, i2, 4, (1380, 500), 0.6, 0.5)]
E += T(a, 540, 800, 56, "plain water", c="ink", d=0.2) + T(a, 1380, 800, 56, "dye", c="gold", d=0.6)
E += cross(a, 540, 500, c="red", d=0.9) + check(a, 1380, 500, c="green", d=1.3) + amb(a)
B.append(E)
# 27 crystals
a = 27
s, si = slab(a, 500, 380, 900, 360)
E = s + amb(a)
for k in range(6):
    E += star(a, 620 + 140 * k, 460 + 80 * (k % 2), 0.3 + 0.18 * k, c="gold", r=30)
E += BIG(a, 960, 220, "too much dye", c="red", d=0.2, s=90) + T(a, 960, 880, 56, "crystals!", c="gold", d=1.2)
B.append(E)
# 28 lab vs kitchen
a = 28
bath = uid("bath")
E = [R(a, 220, 440, 600, 300, c="ink", fill="blue", idp=bath), {"t": "move", "at": a, "kind": "wiggle", "targets": [bath], "pivot": [520, 740], "amp": 4, "hz": 3}]
E += BIG(a, 520, 300, "40°C", c="red", d=0.2, s=110) + T(a, 520, 840, 52, "lab: bath + shaker", c="ink", d=0.4)
lp = uid("lamp")
E += [P(a, "M1400,740 L1400,460 L1540,360", c="ink", w=7, idp=lp), O(a, 1570, 340, 46, c="gold", fill="gold", idp=lp), pop(a, lp, 0.9), pulse(a, lp, 1.4)]
E += T(a, 1450, 840, 52, "kitchen: a desk lamp", c="muted", d=1.0) + amb(a)
B.append(E)
# 29 his own words
a = 29
st = stick(500, 840, 1.1, a, idp="hx2", arms="down")
E = st + [bob(a, "hx2*", 8, 1.2)]
bb = uid("bb")
E += [R(a, 820, 260, 920, 360, c="ink", idp=bb), pop(a, bb, 0.1), wig(a, bb, (1280, 620), 2, 0.8)]
E += T(a, 1280, 380, 52, "\"partial transparency,", c="ink", d=0.3) + T(a, 1280, 480, 52, "not to the degree of the paper\"", c="ink", d=0.8)
E += amb(a) + BIG(a, 1280, 820, "honest!", c="green", d=1.4, s=80)
B.append(E)
# 30 crushed chips won't do it
a = 30
E = dorito(a, 500, 480, 1.6, 0.0)
for k in range(5):
    cr = uid("crumb")
    E += [O(a, 480 + 30 * k, 520, 14, c="gold", fill="gold", idp=cr), sh(a, cr, -120 + 60 * k, 300, 0.5 + 0.08 * k, 0.6)]
E += cross(a, 500, 480, d=1.0)
E += bar(a, 1300, 840, 120, 60, "gold", d=0.6) + bar(a, 1500, 840, 120, 520, "red", d=0.9)
E += T(a, 1360, 920, 44, "snack", c="gold", d=0.6) + T(a, 1560, 920, 44, "lab", c="red", d=0.9) + amb(a)
B.append(E)
# 31 not invisible, orange fingers
a = 31
st = stick(960, 860, 1.4, a, idp="me3", arms="up")
E = st + [wig(a, "me3*", (960, 860), 4, 1.2)]
for x in (820, 1100):
    f = uid("fing")
    E += [O(a, x, 420, 36, c="gold", fill="gold", idp=f), pop(a, f, 1.0), pulse(a, f, 1.4)]
E += dorito(a, 400, 400, 1.0, 0.2) + dorito(a, 1550, 420, 1.0, 0.4) + BIG(a, 960, 160, "still visible", c="red", d=0.6, s=90)
B.append(E)
# 32 seeing inside living tissue
a = 32
eye = uid("eye")
E = [P(a, "M520,520 Q760,320 1000,520 Q760,720 520,520 Z", c="ink", w=6, idp=eye), O(a, 760, 520, 70, c="blue", fill="blue", idp=eye), pop(a, eye, 0.1), pulse(a, eye, 0.9)]
pu = uid("pupil")
E += [O(a, 760, 520, 26, c="ink", fill="ink", idp=pu), sh(a, pu, 30, 0, 0.6, 0.6)]
E += arr(a, 1020, 520, 1380, 520, c="red", d=0.5) + amb(a)
cel = uid("cell")
E += [O(a, 1540, 520, 140, c="green", idp=cel), O(a, 1540, 520, 40, c="green", fill="green", idp=cel), bob(a, cel, 8, 1.0)]
E += T(a, 960, 860, 56, "look inside, no cutting", c="ink", d=0.8)
B.append(E)
# 33 fine print
a = 33
E = []
for k, (lab, c_) in enumerate((("red light", "red"), ("thin tissue", "ink"), ("early research", "blue"))):
    E += T(a, 960, 300 + 170 * k, 64, lab, c=c_, d=0.3 + 0.5 * k)
    E += check(a, 560, 300 + 170 * k, d=0.4 + 0.5 * k)
E += BIG(a, 960, 140, "fine print", c="muted", d=0.0, s=70) + amb(a, 3)
ch, ci, _ = chip(a, 1600, 820, 0.8)
E += ch
B.append(E)
# 33.5 don't try on yourself, don't eat
a = 33.5
s, si = slab(a, 1100, 380, 480, 300, fill="gold")
E = s + cross(a, 1340, 530, d=0.9)
st = stick(500, 860, 1.1, a, idp="me4", arms="down")
E += st + [wig(a, "me4*", (500, 860), 5, 1.6)] + cross(a, 500, 500, d=0.3)
E += BIG(a, 960, 160, "DON'T", c="red", d=0.1, s=110) + amb(a)
B.append(E)
# 34 water learned to bend like fat
a = 34
E = []
for k in range(2):
    bx = uid("bx")
    E += [R(a, 400 + 760 * k, 300, 360, 360, c="gold", fill="gold" if k else "blue", idp=bx), bob(a, bx, 6, 1.0 + 0.4 * k)]
    if not k:
        E += [R(a, 400, 300, 360, 360, c="gold", fill="gold", idp=bx + "y"), pop(a, bx + "y", 0.8, 0.6)]
E += arr(a, 820, 480, 1100, 480, c="red", d=0.4) + T(a, 580, 760, 56, "water", c="blue", d=0.2) + T(a, 1340, 760, 56, "fat", c="ink", d=0.2)
E += BIG(a, 960, 920, "same bend", c="green", d=1.2, s=90) + amb(a)
B.append(E)
# 35 Chip gets through
a = 35
g, gi = grid(a, 660, 300, 600, 420)
s, si = slab(a, 640, 290, 640, 440, fill=None, c="gold")
ch, ci, _ = chip(a, 260, 520, 1.2)
E = g + s + ch + [sh(a, ci + "*", 1400, 0, 0.3, 1.4)] + amb(a, 3) + star(a, 1700, 520, 1.5) + BIG(a, 960, 900, "THROUGH!", c="green", d=1.2, s=120)
B.append(E)
# 35.5 invisible nuggets?
a = 35.5
E = []
for k in range(3):
    ng = uid("ng")
    E += [P(a, f"M{500 + 380 * k},{420} Q{600 + 380 * k},{340} {700 + 380 * k},{420} Q{740 + 380 * k},{540} {640 + 380 * k},{580} "
                f"Q{520 + 380 * k},{580} {500 + 380 * k},{420} Z", c="gold", w=5, idp=ng), pop(a, ng, 0.2 + 0.3 * k), bob(a, ng, 8, 1.0 + 0.3 * k)]
q = uid("q")
E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 1650, "y": 300, "size": 180, "c": "red"}, pop(a, q, 1.0), pulse(a, q, 1.4)]
E += BIG(a, 960, 860, "invisible nuggets?", c="ink", d=0.8, s=90) + amb(a)
B.append(E)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en")
