"""每日科普 2026-10-23（中文）：《撕一层膜，赔八千？》
新闻：苹果首款折叠屏 iPhone Duo 国行开售。微博热搜 2026-10-23：#12 苹果折叠屏开售、#14 苹果内屏磨砂膜能徒手撕下、#15 华强北商家说iPhoneDuo毫无技术含量、
#17 撕完苹果内屏磨砂膜再贴回去要花398（weibo-trending-hot-history 存档）；新浪/微博报道：内屏磨砂膜可徒手撕下，撕后变亮面、折痕更明显，
官方重贴 398 元，私自操作伤屏、换内屏近 8000 元（据报道）；《华尔街日报》Joanna Stern 测评机折叠 32,000 多次手感无明显变化（据报道）。
教科书：弯曲时表面应变 ε ≈ t / (2R)（t 厚度，R 弯曲半径）；玻璃一般在约 1% 量级的拉应变就会断（表面缺陷决定，估算口径）；
折叠屏用超薄玻璃（UTG，业内常见约 30 微米），头发约 70 微米；叠层弯曲有中性层（不拉也不压），脆弱层尽量放在中性层附近；
磨砂面漫反射（散光、抗眩光、略发雾），亮面镜面反射，会把表面起伏（折痕）照得更明显。
我们的估算（片中说是估算）：0.5 mm 玻璃弯到 R = 2 mm，ε ≈ 0.5/4 = 12.5%；30 μm 时 ε ≈ 0.03/4 ≈ 0.75%。
推测（片中说是推测）：撕掉一层后叠层厚度变化、中性层挪动，长期可能让内部多受一点力。角色：小折（会对折的手机）。梗：别撕我的铠甲。
    python3 make.py <kokoro 模型目录> | --boards-only | --fake   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("苹果第一台折叠屏刚开卖，|热搜就被一层膜承包了。", "Apple's first foldable just went on sale, | and one thin film took over the trending list."),
 ("有人发现，内屏那层磨砂膜，|用手就能撕下来。", "People found the matte film on the inner screen | peels off by hand."),
 ("撕完想贴回去？官方售后398元。|要是把屏弄坏了，据报道换内屏将近八千。", "Want it back on? 398 yuan at Apple service. | Damage the screen, and a new one reportedly costs nearly 8,000."),
 ("今天的问题：一块玻璃，|凭什么能对折？", "Today's question: how can a sheet of glass | fold in half?"),
 ("认识一下小折。|一台会对折的手机。", "Meet Foldy. | A phone that bends in half."),
 ("普通手机的玻璃，|你敢对折吗？", "Would you dare fold | an ordinary phone's glass?"),
 ("咔嚓。|玻璃很硬，可是一弯就碎。", "Crack. | Glass is hard, but it snaps when bent."),
 ("秘密在一个公式里：|弯的时候，表面拉长的比例，约等于厚度除以两倍的弯曲半径。", "The secret is one formula: | bend something, and its surface stretches by about thickness over twice the bend radius."),
 ("翻译成人话：|越薄，越弯得动。", "In plain words: | the thinner it is, the more it can bend."),
 ("一本书你折不动，|一张纸随便折。", "You can't fold a whole book, | but a single page folds easily."),
 ("我们粗算一下：0.5毫米的普通玻璃，|弯到半径2毫米，表面要拉长大约12%。", "Our rough math: half-millimeter glass | bent to a 2-millimeter radius would stretch about 12 percent."),
 ("可玻璃拉长1%左右，|就碎了。", "But glass breaks | at roughly 1 percent stretch."),
 ("所以折叠屏用的是超薄玻璃，|业内常见大约30微米。", "So foldables use ultra-thin glass, | often around 30 microns."),
 ("比一根头发，|还要薄一半。", "That's half the thickness | of a human hair."),
 ("同样弯到2毫米，|表面只拉长不到1%。", "Bent to the same 2 millimeters, | it stretches less than 1 percent."),
 ("反转一：薄到这个程度，|玻璃就像纸一样软。", "Twist one: that thin, | glass turns floppy like paper."),
 ("可它也很娇气，|怕划，怕戳。", "But it's also delicate. | It hates scratches and pokes."),
 ("所以最上面要盖一层保护层。|你撕的，就是它的铠甲。", "So a protective layer sits on top. | That film you peeled is its armor."),
 ("反转二：屏幕是好多层叠在一起的，|像一块千层蛋糕。", "Twist two: the screen is a stack of layers, | like a layer cake."),
 ("弯的时候，外面被拉，|里面被挤。", "When it bends, the outside stretches | and the inside squeezes."),
 ("中间有一层，不拉也不挤，|叫中性层。", "In between, one layer does neither. | It's called the neutral layer."),
 ("工程师把最怕拉的东西，|尽量藏在中性层附近。", "Engineers tuck the most fragile parts | as close to that layer as they can."),
 ("撕掉一层，整叠的厚度就变了，|中性层也会跟着挪。", "Peel one layer, and the stack changes thickness. | The neutral layer moves too."),
 ("这是我们的推测：|时间长了，里面可能多受一点力。", "That's our guess: | over time, the inside might take a bit more strain."),
 ("反转三，最反直觉：|撕了膜，屏幕反而更亮、更清楚。", "Twist three, the weird one: | peel it off and the screen looks brighter and sharper."),
 ("因为磨砂面像毛玻璃，|把光往四面八方散开。", "Because a matte surface is like frosted glass. | It scatters light in every direction."),
 ("反光不刺眼了，|可画面也蒙上了一点雾。", "Less glare, | but a slight haze over the picture."),
 ("撕掉以后变成亮面，|像镜子一样反光。", "Peel it, and the surface turns glossy, | reflecting like a mirror."),
 ("而镜子会把每一点起伏都照出来，|包括中间那道折痕。", "And a mirror shows every tiny bump, | including the crease down the middle."),
 ("所以那层磨砂膜，|其实也在帮你藏折痕。", "So that matte film | was also hiding the crease."),
 ("有商家说这台手机没技术含量？|光这一层膜，就有这么多讲究。", "A reseller says this phone has no real tech in it? | This one film alone holds all of this."),
 ("据报道，有人把它折了三万两千多次，|手感没什么变化。", "One reported test folded it over 32,000 times, | with no noticeable change."),
 ("友情提示：膜不是不能撕，|但撕了就回不去了。", "Friendly fine print: you can peel it, | but you can't un-peel it."),
 ("想要亮面，先算算账：|398元，对比一块将近八千的屏。", "Want glossy? Do the math first: | 398 yuan, versus a nearly 8,000-yuan screen."),
 ("小折说：|我能对折，但请别撕我的铠甲。", "Foldy says: | I can bend in half, but please don't peel my armor."),
]
TITLE = {"zh": "撕一层膜，赔八千？", "en": "Peel One Film, Pay 8,000?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 970, 0.5, r=16)
    B.append(E)


def foldy(a, x, y, k=1.0, mood="happy", d=None, open_=True):
    """小折：一台会对折的手机，中间一条铰链线，有脸，一直在晃。"""
    i = uid("fd") + "_"
    w, h = (300 * k, 360 * k) if open_ else (150 * k, 360 * k)
    E = [R(a, x - w / 2, y - h / 2, w, h, c="ink", fill="blue", idp=i, sw=6)]
    if open_:
        E.append(P(a, f"M{x},{y - h / 2} L{x},{y + h / 2}", c="muted", w=4, idp=i))
    E += [O(a, x - 45 * k, y - 40 * k, 14 * k, c="ink", fill="ink", idp=i), O(a, x + 45 * k, y - 40 * k, 14 * k, c="ink", fill="ink", idp=i)]
    m = {"happy": f"M{x - 40 * k},{y + 20 * k} Q{x},{y + 60 * k} {x + 40 * k},{y + 20 * k}",
         "o": f"M{x - 15 * k},{y + 40 * k} a15,15 0 1,0 30,0 a15,15 0 1,0 -30,0",
         "sad": f"M{x - 40 * k},{y + 55 * k} Q{x},{y + 20 * k} {x + 40 * k},{y + 55 * k}"}[mood]
    E += [P(a, m, c="ink", w=5, idp=i), bob(a, i, 8 * k, 1.3), wig(a, i, (x, y + h / 2), 4, 1.1)]
    if d is not None:
        E.append(pop(a, i + "*", d))
    return E, i


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def film(a, x, y, w=300, d=0.0, c="gold"):
    """一层膜：一张有点卷边的薄片。"""
    i = uid("fm")
    return [P(a, f"M{x - w / 2},{y} L{x + w / 2},{y} Q{x + w / 2 + 40},{y - 30} {x + w / 2 + 20},{y - 70}", c=c, w=9, idp=i), pop(a, i, d), wig(a, i, (x - w / 2, y), 5, 1.6)], i


def cracks(a, x, y, d=0.0, n=5):
    E = []
    for q in range(n):
        i = uid("cr")
        E += [P(a, f"M{x},{y} l{60 * ((q % 3) - 1) + 20},{-50 + 25 * q} l{30 * ((q % 2) * 2 - 1)},{-40}", c="red", w=6, idp=i), pop(a, i, d + 0.06 * q), wig(a, i, (x, y), 6, 4.0)]
    return E


def bend(a, x, y, r=200, c="blue", w=10, d=0.0):
    """一条被弯成 U 形的薄片。"""
    i = uid("bd")
    return [P(a, f"M{x - r},{y - 250} L{x - r},{y} A{r},{r} 0 0,0 {x + r},{y} L{x + r},{y - 250}", c=c, w=w, idp=i), pop(a, i, d), bob(a, i, 5, 1.0)], i


def rays(a, x, y, n=5, d=0.0, spread=160, c="gold", fan=False):
    E = []
    for q in range(n):
        i = uid("ry")
        if fan:
            ex, ey = x + (q - n // 2) * spread, y - 260 + 40 * abs(q - n // 2)
        else:
            ex, ey = x + 260, y - 260
        E += arr(a, x, y, ex, ey, c=c, w=5, d=d + 0.1 * q)
    return E


def layers(a, x, y, n=6, w=700, d=0.0):
    cols = ["gold", "blue", "green", "red", "muted", "ink"]
    E = []
    for q in range(n):
        i = uid("ly")
        E += [R(a, x - w / 2, y - 40 * q, w, 34, c=cols[q % 6], fill=cols[q % 6], idp=i), pop(a, i, d + 0.08 * q), bob(a, i, 3, 0.8 + 0.1 * q)]
    return E


# 0 苹果第一台折叠屏开卖
f_, fi = foldy(0, 700, 560, 1.4, d=0.0)
bd(0, f_, [e for q in range(4) for e in star(0, 1200 + 150 * q, 400 + 80 * (q % 2), 0.2 + 0.1 * q, r=34)], T(0, 1450, 760, 64, "开卖！", c="red", d=0.3))
# 0.5 热搜被一层膜承包
fm, mi = film(0.5, 960, 560, 600, 0.0)
bd(0.5, fm, [sh(0.5, mi, 0, -120, 0.4, 0.8)], BIG(0.5, 960, 300, "热搜", c="red", d=0.1, s=140), [e for q in range(3) for e in icon(0.5, "phone", 500 + 460 * q, 820, 110, 0.3 + 0.1 * q, mv="wig")])
# 1 磨砂膜
f_, fi = foldy(1, 760, 560, 1.4)
bd(1, f_, film(1, 760, 360, 360, 0.2)[0], T(1, 1350, 420, 64, "内屏磨砂膜", c="gold", d=0.3), icon(1, "magnifier", 1400, 700, 200, 0.4, mv="wig"))
# 1.5 用手就能撕
f_, fi = foldy(1.5, 700, 600, 1.3)
fm, mi = film(1.5, 700, 380, 360, 0.0)
bd(1.5, f_, fm, [rot(1.5, mi, -35, (520, 380), 0.3, 1.0), sh(1.5, mi, 150, -60, 0.6, 0.8)], T(1.5, 1400, 500, 72, "撕——", c="red", d=0.4), cross(1.5, 1400, 760, d=0.8))
# 2 398元
bd(2, BIG(2, 960, 420, "¥398", c="blue", d=0.1, s=180), film(2, 960, 700, 500, 0.3)[0], icon(2, "gear", 400, 760, 150, 0.2, mv="spin"), icon(2, "gear", 1520, 760, 150, 0.4, mv="spin"))
# 2.5 将近八千
f_, fi = foldy(2.5, 500, 560, 1.0, mood="sad")
bd(2.5, f_, cracks(2.5, 500, 560, 0.2), BIG(2.5, 1250, 450, "≈ ¥8000", c="red", d=0.3, s=170), T(2.5, 1250, 650, 48, "换内屏（据报道）", c="muted", d=0.5))
# 3 一块玻璃
gl = uid("gl")
bd(3, [R(3, 560, 400, 800, 30, c="blue", fill="blue", idp=gl), pop(3, gl, 0.0), bob(3, gl, 6, 1.0)], T(3, 960, 300, 64, "一块玻璃", c="ink", d=0.2),
   icon(3, "question", 1550, 650, 200, 0.4, c="red", mv="wig"))
# 3.5 凭什么能对折
b_, bi = bend(3.5, 960, 600, 150, d=0.0)
bd(3.5, b_, [rot(3.5, bi, 8, (960, 750), 0.3, 0.6), rot(3.5, bi, -8, (960, 750), 0.9, 0.6)], BIG(3.5, 1500, 450, "对折？", c="red", d=0.3, s=120), foldy(3.5, 400, 560, 0.6)[0])
# 4 认识小折
f_, fi = foldy(4, 860, 560, 2.0, d=0.0)
bd(4, f_, BIG(4, 1500, 380, "小折", c="blue", d=0.4, s=160), [e for q in range(3) for e in star(4, 1400 + 110 * q, 620, 0.6 + 0.1 * q, r=30)])
# 4.5 会对折
f_, fi = foldy(4.5, 600, 560, 1.4)
bd(4.5, f_, [{"t": "move", "at": 4.5, "kind": "grow", "targets": [fi + "*"], "axis": "x", "from": 1.0, "to": 0.5, "pivot": [600, 560], "dur": 0.6, "delay": 0.3}],
   foldy(4.5, 1350, 560, 1.4, open_=False, d=0.8)[0], arr(4.5, 850, 560, 1150, 560, c="red", d=0.6))
# 5 普通手机的玻璃
ph = icon(5, "phone", 700, 560, 360, 0.0, mv="wig")
bd(5, ph, [rot(5, ph[0]["id"], 10, (700, 740), 0.4, 0.6)], T(5, 1350, 450, 60, "普通手机", c="ink", d=0.2), BIG(5, 1350, 650, "0.5 mm", c="blue", d=0.4, s=100))
# 5.5 你敢对折吗
ph = icon(5.5, "phone", 800, 560, 360, 0.0, mv="wig")
bd(5.5, ph, [rot(5.5, ph[0]["id"], -25, (800, 740), 0.2, 0.8)], icon(5.5, "question", 1400, 500, 220, 0.3, c="red", mv="wig"), T(5.5, 1400, 800, 60, "敢折吗？", c="red", d=0.5))
# 6 咔嚓
gl = uid("gl")
bd(6, [R(6, 560, 500, 800, 30, c="blue", fill="blue", idp=gl), pop(6, gl, 0.0), rot(6, gl, 20, (960, 515), 0.1, 0.3)], cracks(6, 960, 520, 0.2, 7), BIG(6, 960, 300, "咔嚓！", c="red", d=0.2, s=150))
# 6.5 很硬，一弯就碎
E = []
for q in range(6):
    i = uid("sd")
    E += [P(6.5, f"M{900 + 20 * q},{500} l30,20 l-20,30 Z", c="blue", w=5, idp=i), pop(6.5, i, 0.2), sh(6.5, i, 160 * ((q % 3) - 1), 120 + 20 * q, 0.3, 0.8), spin(6.5, i, (915 + 20 * q, 515), 90)]
bd(6.5, E, T(6.5, 500, 300, 60, "硬", c="ink", d=0.1), check(6.5, 650, 300, d=0.2), T(6.5, 1400, 300, 60, "怕弯", c="red", d=0.4), cross(6.5, 1600, 300, d=0.5))
# 7 一个公式
bd(7, BIG(7, 960, 420, "秘密公式", c="blue", d=0.1, s=140), [e for q in range(3) for e in icon(7, "gear", 560 + 400 * q, 720, 150, 0.2 + 0.1 * q, mv="spin")], foldy(7, 1650, 800, 0.4)[0])
# 7.5 ε ≈ t / 2R
b_, bi = bend(7.5, 600, 700, 140, d=0.0)
bd(7.5, b_, BIG(7.5, 1300, 380, "拉长 ≈ 厚度 ÷ 2R", c="red", d=0.2, s=90), arr(7.5, 600, 700, 740, 700, c="green", d=0.4), T(7.5, 680, 900, 48, "R：弯曲半径", c="green", d=0.5),
   icon(7.5, "ruler", 1300, 700, 160, 0.6, mv="wig"))
# 8 翻译成人话
bd(8, foldy(8, 600, 560, 1.4)[0], icon(8, "speaker", 1250, 500, 200, 0.2, mv="wig"), T(8, 1250, 760, 60, "说人话", c="ink", d=0.4))
# 8.5 越薄越弯得动
t1, t2 = uid("th"), uid("tn")
bd(8.5, [R(8.5, 300, 400, 500, 120, c="ink", fill="muted", idp=t1), pop(8.5, t1, 0.0), wig(8.5, t1, (550, 520), 1, 1.0)], cross(8.5, 550, 650, d=0.3),
   bend(8.5, 1350, 560, 160, d=0.2)[0], check(8.5, 1350, 780, d=0.5), BIG(8.5, 960, 920, "越薄越能弯", c="red", d=0.4, s=90))
# 9 一本书折不动
bk = uid("bk")
bd(9, [R(9, 560, 380, 360, 300, c="red", fill="red", idp=bk), pop(9, bk, 0.0), wig(9, bk, (740, 680), 3, 1.5)], cross(9, 740, 530, d=0.4), T(9, 740, 800, 60, "一本书", c="red", d=0.2),
   icon(9, "question", 1350, 500, 180, 0.3, c="muted", mv="wig"))
# 9.5 一张纸随便折
pp = uid("pp")
bd(9.5, [P(9.5, "M700,700 L700,400 L1000,400 L1000,700 Z", c="ink", w=5, idp=pp), pop(9.5, pp, 0.0), rot(9.5, pp, -60, (1000, 550), 0.3, 0.8), rot(9.5, pp, 60, (1000, 550), 1.2, 0.8)],
   T(9.5, 1400, 500, 60, "一张纸", c="green", d=0.2), check(9.5, 1400, 700, d=0.5))
# 10 粗算 0.5 mm
bd(10, T(10, 960, 200, 52, "我们粗算一下", c="muted", d=0.1), BIG(10, 600, 480, "0.5 mm", c="blue", d=0.2, s=120), bend(10, 1350, 650, 130, w=22, d=0.3)[0],
   icon(10, "gear", 600, 760, 130, 0.4, mv="spin"))
# 10.5 R=2mm → 12%
bd(10.5, BIG(10.5, 960, 420, "≈ 12%", c="red", d=0.1, s=180), bar(10.5, 700, 900, 160, 330, "red", d=0.3), T(10.5, 780, 950, 40, "要拉长"), cracks(10.5, 1300, 700, 0.6, 4),
   T(10.5, 960, 200, 52, "弯到半径 2 mm", c="ink", d=0.2))
# 11 玻璃拉长 1%
bd(11, bar(11, 700, 900, 160, 330, "red", d=0.0), T(11, 780, 950, 40, "要拉长 12%"), bar(11, 1100, 900, 160, 30, "blue", d=0.2), T(11, 1180, 950, 40, "玻璃极限 ~1%"),
   arr(11, 1180, 840, 860, 600, c="ink", d=0.4))
# 11.5 就碎了
gl = uid("gl")
bd(11.5, [R(11.5, 560, 500, 800, 30, c="blue", fill="blue", idp=gl), pop(11.5, gl, 0.0), sh(11.5, gl, 0, 300, 0.4, 0.6)], cracks(11.5, 960, 520, 0.1, 7), BIG(11.5, 960, 300, "碎", c="red", d=0.2, s=170))
# 12 超薄玻璃
b_, bi = bend(12, 700, 650, 160, w=5, d=0.0)
bd(12, b_, [rot(12, bi, 10, (700, 810), 0.3, 0.6)], T(12, 1350, 400, 64, "超薄玻璃", c="blue", d=0.2), T(12, 1350, 520, 44, "UTG", c="muted", d=0.3), foldy(12, 1350, 760, 0.5)[0])
# 12.5 30 微米
bd(12.5, BIG(12.5, 960, 420, "≈ 30 μm", c="blue", d=0.1, s=180), icon(12.5, "magnifier", 400, 760, 180, 0.3, mv="wig"), T(12.5, 960, 700, 48, "业内常见", c="muted", d=0.3),
   icon(12.5, "lens", 1520, 760, 160, 0.4, mv="spin"))
# 13 一根头发
hr = uid("hr")
bd(13, [P(13, "M300,500 Q700,420 1000,520 Q1300,620 1650,500", c="ink", w=14, idp=hr), pop(13, hr, 0.0), wig(13, hr, (960, 520), 3, 1.2)], T(13, 960, 380, 56, "头发 ≈ 70 μm", c="ink", d=0.2),
   icon(13, "magnifier", 960, 780, 180, 0.4, mv="wig"))
# 13.5 薄一半
hr, gg = uid("hr"), uid("gg")
bd(13.5, [P(13.5, "M300,420 L1650,420", c="ink", w=28, idp=hr), pop(13.5, hr, 0.0), bob(13.5, hr, 3, 0.9), P(13.5, "M300,620 L1650,620", c="blue", w=12, idp=gg), pop(13.5, gg, 0.3),
          {"t": "move", "at": 13.5, "kind": "grow", "targets": [gg], "axis": "x", "from": 0.05, "to": 1.0, "pivot": [300, 620], "dur": 0.8, "delay": 0.3}],
   T(13.5, 960, 340, 44, "头发", c="ink", d=0.1), T(13.5, 960, 700, 44, "超薄玻璃", c="blue", d=0.4), BIG(13.5, 960, 880, "÷ 2", c="red", d=0.6, s=110))
# 14 同样弯到 2mm
b_, bi = bend(14, 700, 650, 130, w=5, d=0.0)
bd(14, b_, [rot(14, bi, 12, (700, 780), 0.3, 0.6), rot(14, bi, -12, (700, 780), 1.0, 0.6)], T(14, 1350, 450, 60, "同样 R = 2 mm", c="ink", d=0.2), foldy(14, 1350, 760, 0.5)[0])
# 14.5 不到 1%
bd(14.5, BIG(14.5, 960, 400, "< 1%", c="green", d=0.1, s=190), [e for q in range(3) for e in check(14.5, 600 + 360 * q, 760, d=0.3 + 0.15 * q)], bend(14.5, 1650, 800, 60, w=4, d=0.2)[0])
# 15 反转一
bd(15, BIG(15, 960, 160, "反转一", c="red", d=0.1, s=90), bend(15, 700, 700, 160, w=5, d=0.1)[0], T(15, 1350, 500, 60, "薄到这个程度", c="ink", d=0.3), icon(15, "ruler", 1350, 760, 150, 0.4, mv="wig"))
# 15.5 像纸一样软
pp = uid("pp")
bd(15.5, [P(15.5, "M500,500 Q700,350 900,500 Q1100,650 1300,500", c="blue", w=8, idp=pp), pop(15.5, pp, 0.0), wig(15.5, pp, (900, 500), 10, 1.5)],
   T(15.5, 900, 760, 64, "软得像纸", c="blue", d=0.3), foldy(15.5, 1600, 600, 0.5, mood="o")[0])
# 16 娇气
bd(16, foldy(16, 700, 560, 1.4, mood="sad")[0], T(16, 1350, 400, 64, "娇气", c="red", d=0.2), [e for q in range(3) for e in icon(16, "water", 1250 + 120 * q, 650, 70, 0.3 + 0.1 * q, c="blue")])
# 16.5 怕划，怕戳
nl = uid("nl")
f_, fi = foldy(16.5, 800, 560, 1.3, mood="o")
bd(16.5, f_, [P(16.5, "M1300,300 L1100,500", c="ink", w=12, idp=nl), pop(16.5, nl, 0.0), sh(16.5, nl, -150, 120, 0.3, 0.4), sh(16.5, nl, 150, -120, 0.8, 0.4)],
   cracks(16.5, 900, 520, 0.6, 3), T(16.5, 1500, 760, 60, "划、戳", c="red", d=0.4))
# 17 保护层
f_, fi = foldy(17, 800, 600, 1.3)
fm, mi = film(17, 800, 300, 360, 0.0)
bd(17, f_, fm, [sh(17, mi, 0, 60, 0.3, 0.8)], T(17, 1400, 500, 60, "保护层", c="gold", d=0.4), check(17, 1400, 700, d=0.6))
# 17.5 铠甲
sh_ = uid("shd")
bd(17.5, [P(17.5, "M960,300 L1200,380 Q1200,700 960,820 Q720,700 720,380 Z", c="gold", w=8, fill="gold", idp=sh_), pop(17.5, sh_, 0.0), bob(17.5, sh_, 6, 1.0), pulse(17.5, sh_, 0.6)],
   T(17.5, 960, 940, 60, "它的铠甲", c="ink", d=0.3), foldy(17.5, 400, 600, 0.6)[0], foldy(17.5, 1550, 600, 0.6, mood="o")[0])
# 18 反转二 多层
bd(18, BIG(18, 960, 160, "反转二", c="red", d=0.1, s=90), layers(18, 960, 700, 6, 800, 0.2), foldy(18, 1650, 760, 0.4)[0])
# 18.5 千层蛋糕
ck = uid("ck")
bd(18.5, layers(18.5, 760, 700, 6, 600, 0.0), [P(18.5, "M760,430 L760,360", c="red", w=8, idp=ck), pop(18.5, ck, 0.5), wig(18.5, ck, (760, 430), 8, 3.0)],
   T(18.5, 1450, 500, 64, "千层蛋糕", c="gold", d=0.3), icon(18.5, "flame", 760, 330, 60, 0.6, c="red", mv="wig"))
# 19 外面被拉
b_, bi = bend(19, 760, 650, 220, w=40, c="muted", d=0.0)
bd(19, b_, arr(19, 450, 400, 450, 250, c="red", d=0.3), arr(19, 1070, 400, 1070, 250, c="red", d=0.3), T(19, 1450, 400, 64, "外面：拉", c="red", d=0.2), foldy(19, 1550, 760, 0.4)[0])
# 19.5 里面被挤
b_, bi = bend(19.5, 760, 650, 220, w=40, c="muted", d=0.0)
bd(19.5, b_, arr(19.5, 620, 500, 680, 600, c="blue", d=0.2), arr(19.5, 900, 500, 840, 600, c="blue", d=0.3), T(19.5, 1450, 500, 64, "里面：挤", c="blue", d=0.2),
   [pulse(19.5, bi, 0.6)], icon(19.5, "spring", 1450, 760, 150, 0.4, mv="wig"))
# 20 中间一层
bd(20, layers(20, 960, 760, 7, 800, 0.0), arr(20, 1500, 640, 1380, 640, c="green", d=0.5), T(20, 1650, 580, 52, "不拉也不挤", c="green", d=0.6))
# 20.5 中性层
nl_ = uid("nl")
bd(20.5, [P(20.5, "M300,560 L1620,560", c="green", w=14, idp=nl_), pop(20.5, nl_, 0.0), pulse(20.5, nl_, 0.4), wig(20.5, nl_, (960, 560), 1, 1.0)],
   BIG(20.5, 960, 380, "中性层", c="green", d=0.2, s=140), arr(20.5, 960, 860, 960, 600, c="green", d=0.4), foldy(20.5, 400, 820, 0.4)[0])
# 21 工程师
bd(21, icon(21, "gear", 600, 500, 260, 0.0, mv="spin"), icon(21, "ruler", 1000, 500, 200, 0.2, mv="wig"), T(21, 1450, 500, 64, "工程师", c="blue", d=0.3), foldy(21, 960, 860, 0.4)[0])
# 21.5 藏在中性层附近
gp = uid("gp")
bd(21.5, layers(21.5, 960, 760, 7, 800, 0.0), [O(21.5, 1600, 300, 40, c="red", fill="red", idp=gp), pop(21.5, gp, 0.2), sh(21.5, gp, -640, 340, 0.4, 1.0)],
   T(21.5, 1550, 200, 48, "最怕拉的", c="red", d=0.3), check(21.5, 1550, 860, d=1.2))
# 22 撕掉一层
E = layers(22, 960, 760, 6, 800, 0.0)
top = E[-3]["id"]
bd(22, E, [sh(22, top, 250, -250, 0.4, 0.8), rot(22, top, -20, (960, 560), 0.4, 0.8)], T(22, 600, 300, 60, "撕掉一层", c="red", d=0.3))
# 22.5 中性层跟着挪
nl_ = uid("nl")
bd(22.5, layers(22.5, 960, 800, 5, 800, 0.0), [P(22.5, "M500,680 L1420,680", c="green", w=10, idp=nl_), pop(22.5, nl_, 0.2), sh(22.5, nl_, 0, 40, 0.5, 0.8)],
   arr(22.5, 1550, 600, 1550, 720, c="green", d=0.5), T(22.5, 960, 300, 60, "中性层挪了", c="green", d=0.4))
# 23 我们的推测
bd(23, T(23, 960, 300, 72, "推测", c="muted", d=0.1), icon(23, "question", 600, 620, 200, 0.2, c="muted", mv="wig"), foldy(23, 1300, 620, 1.0, mood="o")[0])
# 23.5 多受一点力
f_, fi = foldy(23.5, 760, 560, 1.3, mood="sad")
bd(23.5, f_, [pulse(23.5, fi + "*", 0.4), pulse(23.5, fi + "*", 1.2)], icon(23.5, "clock", 1400, 400, 180, 0.2, mv="spin"), T(23.5, 1400, 700, 56, "多受一点力？", c="red", d=0.4))
# 24 反转三
bd(24, BIG(24, 960, 160, "反转三", c="red", d=0.1, s=90), foldy(24, 960, 600, 1.4, mood="o")[0], icon(24, "question", 1450, 500, 180, 0.3, c="red", mv="wig"))
# 24.5 更亮更清楚
f_, fi = foldy(24.5, 700, 560, 1.4)
bd(24.5, f_, [pulse(24.5, fi + "*", 0.3)], icon(24.5, "sun", 1350, 450, 220, 0.2, c="gold", mv="spin"), T(24.5, 1350, 760, 64, "更亮、更清楚", c="gold", d=0.4))
# 25 毛玻璃
fg = uid("fg")
bd(25, [R(25, 560, 360, 400, 400, c="muted", fill="muted", idp=fg), pop(25, fg, 0.0), wig(25, fg, (760, 760), 2, 1.0)], T(25, 760, 860, 56, "毛玻璃", c="ink", d=0.2),
   icon(25, "lens", 1350, 520, 200, 0.3, mv="spin"), T(25, 1350, 760, 48, "磨砂面", c="ink", d=0.4))
# 25.5 四面八方散开
srf = uid("srf")
bd(25.5, [P(25.5, "M300,800 L1620,800", c="muted", w=12, idp=srf), bob(25.5, srf, 2, 0.6)], arr(25.5, 500, 300, 960, 790, c="gold", d=0.0), rays(25.5, 960, 790, 7, 0.4, 160, fan=True),
   T(25.5, 1500, 300, 60, "四面八方", c="gold", d=0.5))
# 26 反光不刺眼
ey = icon(26, "eye", 700, 520, 240, 0.0, mv="wig")
bd(26, ey, [pulse(26, ey[0]["id"], 0.5)], check(26, 1000, 520, d=0.3), T(26, 1400, 520, 60, "不刺眼", c="green", d=0.3), icon(26, "sun", 1600, 220, 120, 0.2, c="gold", mv="spin"))
# 26.5 蒙一点雾
bd(26.5, foldy(26.5, 800, 560, 1.4)[0], [e for q in range(4) for e in icon(26.5, "cloud", 700 + 80 * q, 450 + 60 * (q % 2), 110, 0.2 + 0.1 * q, c="muted", mv="bob")],
   T(26.5, 1450, 560, 60, "一点雾", c="muted", d=0.4))
# 27 亮面
f_, fi = foldy(27, 700, 560, 1.4)
bd(27, f_, [pulse(27, fi + "*", 0.5)], icon(27, "mirror", 1350, 520, 240, 0.2, mv="wig"), T(27, 1350, 820, 64, "亮面", c="blue", d=0.3))
# 27.5 镜面反射
srf = uid("srf")
bd(27.5, [P(27.5, "M300,800 L1620,800", c="blue", w=12, idp=srf), bob(27.5, srf, 2, 0.6)], arr(27.5, 500, 300, 960, 790, c="gold", d=0.0), arr(27.5, 960, 790, 1420, 300, c="gold", d=0.4),
   T(27.5, 960, 200, 60, "像镜子", c="blue", d=0.3), icon(27.5, "eye", 1550, 260, 120, 0.6, mv="wig"))
# 28 每一点起伏
wv = uid("wv")
bd(28, [P(28, "M300,700 Q500,660 700,700 Q900,740 1100,700 Q1300,660 1500,700 Q1600,720 1620,700", c="blue", w=10, idp=wv), pop(28, wv, 0.0), wig(28, wv, (960, 700), 2, 1.5)],
   arr(28, 600, 300, 800, 690, c="gold", d=0.2), arr(28, 800, 690, 900, 300, c="gold", d=0.4), arr(28, 1200, 300, 1300, 680, c="gold", d=0.5), arr(28, 1300, 680, 1600, 320, c="gold", d=0.7))
# 28.5 中间那道折痕
f_, fi = foldy(28.5, 960, 560, 2.0)
cr_ = uid("crs")
bd(28.5, f_, [P(28.5, "M960,200 L960,920", c="red", w=12, idp=cr_), pop(28.5, cr_, 0.3), pulse(28.5, cr_, 0.8)], T(28.5, 1500, 400, 64, "折痕", c="red", d=0.4), arr(28.5, 1400, 450, 1000, 550, c="red", d=0.5))
# 29 那层磨砂膜
fm, mi = film(29, 960, 560, 700, 0.0)
bd(29, fm, [pulse(29, mi, 0.4)], T(29, 960, 380, 72, "磨砂膜", c="gold", d=0.2), foldy(29, 960, 800, 0.5)[0])
# 29.5 帮你藏折痕
f_, fi = foldy(29.5, 800, 560, 1.6)
fg = uid("fg")
bd(29.5, f_, [R(29.5, 540, 260, 520, 600, c="muted", fill="muted", idp=fg), pop(29.5, fg, 0.3), wig(29.5, fg, (800, 860), 2, 1.0)], T(29.5, 1450, 500, 60, "藏起折痕", c="ink", d=0.4),
   check(29.5, 1450, 700, d=0.6))
# 30 有商家说没技术含量
shp = uid("shp")
bd(30, [P(30, "M400,800 L400,450 L800,450 L800,800 M350,450 L600,300 L850,450", c="ink", w=6, idp=shp), pop(30, shp, 0.0), bob(30, shp, 3, 0.8)],
   T(30, 600, 600, 48, "商家", c="ink", d=0.1), T(30, 1350, 400, 60, "没技术含量？", c="red", d=0.3), icon(30, "question", 1350, 650, 180, 0.4, c="red", mv="wig"))
# 30.5 一层膜这么多讲究
bd(30.5, film(30.5, 960, 300, 600, 0.0)[0], [e for q, n_ in enumerate(["ruler", "lens", "gear", "atom"]) for e in icon(30.5, n_, 450 + 340 * q, 620, 150, 0.2 + 0.12 * q, mv="spin" if n_ == "gear" else "wig")], T(30.5, 960, 880, 60, "讲究多着呢", c="blue", d=0.5))
# 31 折了三万两千次
f_, fi = foldy(31, 700, 560, 1.3)
bd(31, f_, [{"t": "move", "at": 31, "kind": "grow", "targets": [fi + "*"], "axis": "x", "from": 1.0, "to": 0.5, "pivot": [700, 560], "dur": 0.3, "delay": 0.2},
            {"t": "move", "at": 31, "kind": "grow", "targets": [fi + "*"], "axis": "x", "from": 0.5, "to": 1.0, "pivot": [700, 560], "dur": 0.3, "delay": 0.6}],
   BIG(31, 1350, 450, "32,000+", c="red", d=0.2, s=140), T(31, 1350, 620, 44, "（据报道）", c="muted", d=0.4))
# 31.5 手感没变
bd(31.5, foldy(31.5, 800, 560, 1.4)[0], [e for q in range(3) for e in check(31.5, 1300 + 150 * q, 500, d=0.2 + 0.15 * q)], T(31.5, 1450, 700, 56, "手感没变", c="green", d=0.4))
# 32 友情提示 膜能撕
fm, mi = film(32, 960, 560, 500, 0.0)
bd(32, T(32, 960, 200, 60, "友情提示", c="ink", d=0.1), fm, [rot(32, mi, -20, (710, 560), 0.3, 0.8)], check(32, 1450, 560, d=0.5), foldy(32, 450, 800, 0.4)[0])
# 32.5 回不去了
fm, mi = film(32.5, 960, 500, 500, 0.0)
bd(32.5, fm, [sh(32.5, mi, 350, -250, 0.2, 1.0)], arr(32.5, 1300, 700, 700, 700, c="red", d=0.4), cross(32.5, 1000, 700, d=0.7), T(32.5, 960, 880, 60, "回不去了", c="red", d=0.5))
# 33 先算算账
bd(33, icon(33, "gear", 600, 520, 200, 0.0, mv="spin"), T(33, 1200, 520, 72, "算算账", c="blue", d=0.2), foldy(33, 1650, 760, 0.5, mood="o")[0])
# 33.5 398 对 8000
bd(33.5, bar(33.5, 600, 880, 200, 40, "blue", d=0.1), T(33.5, 700, 940, 44, "¥398"), bar(33.5, 1100, 880, 200, 600, "red", d=0.3, dur=1.0), T(33.5, 1200, 940, 44, "≈ ¥8000"),
   T(33.5, 960, 160, 56, "重贴  vs  换屏", c="ink", d=0.2))
# 34 小折说
bd(34, foldy(34, 960, 580, 1.8, d=0.0)[0], [e for q in range(4) for e in star(34, 400 + 370 * q, 880, 0.3 + 0.1 * q, r=34)], T(34, 960, 150, 56, "小折说：", c="ink", d=0.3))
# 34.5 别撕我的铠甲
sh_ = uid("shd")
f_, fi = foldy(34.5, 700, 560, 1.3)
bd(34.5, f_, [P(34.5, "M1350,300 L1550,370 Q1550,650 1350,750 Q1150,650 1150,370 Z", c="gold", w=8, fill="gold", idp=sh_), pop(34.5, sh_, 0.2), bob(34.5, sh_, 6, 1.0), pulse(34.5, sh_, 0.8)],
   BIG(34.5, 960, 940, "别撕我的铠甲", c="red", d=0.4, s=90))

# ---- 加句（插在原第 k 句后面；画板 at 写 100 + j）----
X = [
 (2, "国行起售价15999元，|这层膜成了全网最贵的一张贴纸。", "It starts at 15,999 yuan in China, | and this film became the internet's priciest sticker."),
 (6, "为什么？因为弯的时候，|外侧要被拉长。", "Why? Because when you bend something, | the outside has to stretch."),
 (6, "而玻璃最怕拉：|表面一道看不见的小裂纹，一拉就裂开。", "And glass hates stretching: | one invisible tiny flaw, and it rips open."),
 (14, "一样是玻璃，|薄到一定程度，就从“碎”变成了“弯”。", "Same glass. | Make it thin enough, and 'shatter' becomes 'bend'."),
 (20, "就像对折一本杂志：|封面被拉，封底被挤，中间的书页最轻松。", "Like folding a magazine: | the cover stretches, the back squeezes, the middle pages relax."),
 (23, "按常见折叠屏的结构，最外面那层专门挡划痕。|撕了，下面那层就直接见人了。", "In a typical foldable, the outermost layer takes the scratches. | Peel it, and the layer below faces the world bare."),
 (27, "磨砂是漫反射，|亮面是镜面反射。", "Matte means diffuse reflection. | Glossy means mirror reflection."),
 (29, "这就是为什么，|撕膜以后，很多人说折痕更明显了。", "That's why, | after peeling, many people say the crease got more obvious."),
 (31, "折叠屏最难的从来不是“折”，|而是折几万次以后还能平。", "The hard part of a foldable was never folding. | It's staying flat after tens of thousands of folds."),
]
# 100 15999
f_, fi = foldy(100, 600, 560, 1.3)
bd(100, f_, BIG(100, 1300, 420, "¥15,999", c="blue", d=0.2, s=150), T(100, 1300, 600, 48, "国行起售价", c="muted", d=0.3), [e for q in range(3) for e in star(100, 1150 + 150 * q, 760, 0.4 + 0.1 * q, r=30)])
# 100.5 最贵的贴纸
fm, mi = film(100.5, 800, 560, 500, 0.0)
bd(100.5, fm, [rot(100.5, mi, 10, (800, 560), 0.3, 0.6), sh(100.5, mi, 0, -60, 0.5, 0.6)], T(100.5, 1450, 450, 64, "最贵贴纸", c="red", d=0.3), BIG(100.5, 1450, 650, "?!", c="red", d=0.5, s=120))
# 101 外侧被拉长
b_, bi = bend(101, 760, 650, 200, w=30, c="blue", d=0.0)
bd(101, b_, arr(101, 480, 500, 480, 300, c="red", d=0.3), arr(101, 1040, 500, 1040, 300, c="red", d=0.4), T(101, 1450, 450, 64, "外侧：拉", c="red", d=0.2), icon(101, "question", 1450, 700, 160, 0.4, c="red", mv="wig"))
# 101.5 拉长
gl = uid("gl")
bd(101.5, [R(101.5, 660, 520, 600, 40, c="blue", fill="blue", idp=gl), pop(101.5, gl, 0.0),
           {"t": "move", "at": 101.5, "kind": "grow", "targets": [gl], "axis": "x", "from": 1.0, "to": 1.3, "pivot": [960, 540], "dur": 1.0, "delay": 0.2}],
   arr(101.5, 600, 650, 300, 650, c="red", d=0.3), arr(101.5, 1320, 650, 1620, 650, c="red", d=0.3), T(101.5, 960, 820, 60, "被拉长", c="red", d=0.4))
# 102 玻璃最怕拉
gl = uid("gl")
bd(102, [R(102, 560, 500, 800, 40, c="blue", fill="blue", idp=gl), pop(102, gl, 0.0), bob(102, gl, 4, 1.0)], foldy(102, 960, 820, 0.4, mood="o")[0], T(102, 960, 300, 64, "最怕拉", c="red", d=0.2),
   arr(102, 500, 520, 250, 520, c="red", d=0.3), arr(102, 1420, 520, 1670, 520, c="red", d=0.3))
# 102.5 小裂纹一拉就裂
gl, gr = uid("gl"), uid("gr")
bd(102.5, [R(102.5, 460, 500, 500, 40, c="blue", fill="blue", idp=gl), R(102.5, 960, 500, 500, 40, c="blue", fill="blue", idp=gr), pop(102.5, [gl, gr], 0.0),
           sh(102.5, gl, -200, 0, 0.5, 0.6), sh(102.5, gr, 200, 0, 0.5, 0.6)], cracks(102.5, 960, 520, 0.2, 4), icon(102.5, "magnifier", 960, 780, 160, 0.1, mv="wig"),
   T(102.5, 960, 300, 56, "看不见的小裂纹", c="ink", d=0.2))
# 103 一样是玻璃
gl = uid("gl")
bd(103, [R(103, 400, 450, 400, 60, c="blue", fill="blue", idp=gl), pop(103, gl, 0.0), wig(103, gl, (600, 480), 2, 1.0)], BIG(103, 960, 480, "=", c="ink", d=0.2, s=120),
   bend(103, 1400, 600, 120, w=5, d=0.3)[0], T(103, 960, 850, 60, "一样是玻璃", c="blue", d=0.4))
# 103.5 从碎变成弯
bd(103.5, cracks(103.5, 500, 500, 0.0, 5), T(103.5, 500, 760, 72, "碎", c="red", d=0.1), arr(103.5, 750, 500, 1150, 500, c="ink", d=0.3), bend(103.5, 1400, 640, 120, w=5, d=0.5)[0],
   T(103.5, 1400, 860, 72, "弯", c="green", d=0.6))
# 104 对折杂志
mg = uid("mg")
bd(104, [R(104, 560, 300, 800, 500, c="red", idp=mg), P(104, "M960,300 L960,800", c="muted", w=4, idp=mg), pop(104, mg, 0.0),
         {"t": "move", "at": 104, "kind": "grow", "targets": [mg], "axis": "x", "from": 1.0, "to": 0.5, "pivot": [960, 550], "dur": 0.8, "delay": 0.4}],
   T(104, 960, 900, 60, "对折一本杂志", c="ink", d=0.2), icon(104, "question", 1600, 400, 140, 0.3, c="muted", mv="wig"))
# 104.5 封面拉 封底挤 中间轻松
b1, i1 = bend(104.5, 960, 650, 260, w=10, c="red", d=0.0)
b2, i2 = bend(104.5, 960, 650, 200, w=10, c="green", d=0.2)
b3, i3 = bend(104.5, 960, 650, 140, w=10, c="blue", d=0.4)
bd(104.5, b1, b2, b3, T(104.5, 1450, 300, 48, "封面：拉", c="red", d=0.3), T(104.5, 1450, 420, 48, "中间：轻松", c="green", d=0.5), T(104.5, 1450, 540, 48, "封底：挤", c="blue", d=0.7))
# 105 最外面挡划痕
nl = uid("nl")
bd(105, layers(105, 960, 760, 6, 800, 0.0), [P(105, "M1300,250 L1100,500", c="ink", w=12, idp=nl), pop(105, nl, 0.2), sh(105, nl, -200, 0, 0.5, 0.6)],
   T(105, 600, 300, 56, "最外层：挡划痕", c="gold", d=0.3))
# 105.5 下面那层直接见人
E = layers(105.5, 960, 760, 6, 800, 0.0)
top = E[-3]["id"]
bd(105.5, E, [sh(105.5, top, 300, -300, 0.2, 0.8)], foldy(105.5, 400, 300, 0.5, mood="o")[0], T(105.5, 1300, 300, 56, "直接见人", c="red", d=0.5))
# 106 漫反射
srf = uid("srf")
bd(106, [P(106, "M300,800 L1620,800", c="muted", w=12, idp=srf), bob(106, srf, 2, 0.6)], arr(106, 500, 300, 960, 790, c="gold", d=0.0), rays(106, 960, 790, 5, 0.3, 200, fan=True),
   T(106, 1500, 250, 64, "磨砂：漫反射", c="muted", d=0.3))
# 106.5 镜面反射
srf = uid("srf")
bd(106.5, [P(106.5, "M300,800 L1620,800", c="blue", w=12, idp=srf), bob(106.5, srf, 2, 0.6)], arr(106.5, 500, 300, 960, 790, c="gold", d=0.0), arr(106.5, 960, 790, 1420, 300, c="gold", d=0.3),
   T(106.5, 1500, 200, 64, "亮面：镜面反射", c="blue", d=0.3), icon(106.5, "mirror", 400, 600, 140, 0.4, mv="wig"))
# 107 这就是为什么
bd(107, BIG(107, 960, 400, "所以", c="blue", d=0.1, s=150), foldy(107, 600, 760, 0.6)[0], icon(107, "lens", 1350, 760, 160, 0.3, mv="spin"))
# 107.5 折痕更明显
f_, fi = foldy(107.5, 800, 560, 1.6, mood="sad")
cr_ = uid("crs")
bd(107.5, f_, [P(107.5, "M800,250 L800,870", c="red", w=14, idp=cr_), pop(107.5, cr_, 0.2), pulse(107.5, cr_, 0.6), pulse(107.5, cr_, 1.2)], T(107.5, 1450, 500, 60, "折痕更明显", c="red", d=0.3),
   icon(107.5, "eye", 1450, 720, 150, 0.4, mv="wig"))
# 108 最难的不是折
f_, fi = foldy(108, 700, 560, 1.3)
bd(108, f_, [{"t": "move", "at": 108, "kind": "grow", "targets": [fi + "*"], "axis": "x", "from": 1.0, "to": 0.5, "pivot": [700, 560], "dur": 0.4, "delay": 0.2}],
   T(108, 1350, 450, 64, "折？简单", c="ink", d=0.3), check(108, 1350, 650, d=0.5))
# 108.5 折几万次还能平
fl = uid("fl")
bd(108.5, [P(108.5, "M300,600 L1620,600", c="blue", w=10, idp=fl), pop(108.5, fl, 0.0), wig(108.5, fl, (960, 600), 1, 1.0)], icon(108.5, "ruler", 960, 400, 200, 0.2, mv="wig"),
   BIG(108.5, 960, 820, "几万次，还要平", c="red", d=0.4, s=90))

ORDER = []
for k in range(len(S)):
    ORDER.append(k)
    ORDER += [100 + j for j, x in enumerate(X) if x[0] == k]
S = [S[k] if k < 100 else X[k - 100][1:] for k in ORDER]
NEW = {k: n for n, k in enumerate(ORDER)}
for b in B:
    for e in b:
        e["at"] = NEW[int(e["at"])] + (e["at"] - int(e["at"]))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"0.5毫米": "零点五毫米", "12%": "百分之十二", "1%": "百分之一", "15999元": "一万五千九百九十九元"})
