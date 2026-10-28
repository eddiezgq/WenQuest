"""每日科普 2026-10-28（中文）：《老干妈的AI，怎么挑出坏辣椒？》
热点：老干妈用 AI 视觉质检挑辣椒、“600 人变 48 人”的说法上了热搜（新浪科技热点小时报 2026-10-28 09 时第 5 条；
21 经济网 / 澎湃 10-14 “老干妈悄悄玩AI，552个拣椒工去哪儿了”；10-26 公司回应“AI裁员传闻不实”）。
用到的事实：
- 21经济网 2026-10-14 https://www.21jingji.com/article/20261014/herald/9ab72544d3fecb6299b33ae1fa7daff0.html
  （转自中国商报，综合界面、蓝鲸、澎湃）：首席质量官李鑫在 2026 贵州省质量发展大会披露 AI 视觉质检全车间上线；
  高速工业相机每 0.3 秒扫描一次传送带，识别霉变、黑斑辣椒，用气流自动剔除；上线前“超过 600 名”拣椒工，保留 48 人做最后把关；
  552 是 600−48 推算的，不是公司公布的；关键工序不良率降到 0.02%。
- 什么值得买 https://post.smzdm.com/p/a5rxgpe8/ ：靠颜色、斑点等外观特征判断；0.02% 不是食品安全抽检合格率。
- 搜狐 2026-10-26 https://sohu.com/a/1093044321_121607705 ：公司称“相关AI裁员传闻为不实信息”；人事称“从来都没用过这么多拣椒工人”。
- 常识：数码照片的每个像素是红、绿、蓝三个数；色选机用喷气阀剔除（大米、豆子、茶叶色选是成熟工业）；
  部分分拣机用近红外等人眼看不见的光（这一句说的是“有的分拣机”，不是说老干妈）。
推测/假设：“传送带每秒一米”是假设的例子，片中说“假如”；AI 可能误判的两种情况是一般原理，不是老干妈的数据。
比喻：老师傅带徒弟（看一万颗）。贯穿的梗：“一口气”。
    python3 make.py <kokoro 模型目录> | --boards-only | --fake   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("据报道，老干妈挑辣椒的工人，|从六百多人变成了四十八人。", "Reportedly, Laoganma's chili sorters | went from over six hundred to forty-eight."),
 ("顶替他们的，是传送带上方的高速相机，|每零点三秒扫一遍。", "Replacing them: high-speed cameras over the belt, | scanning every 0.3 seconds."),
 ("公司回应：裁员传闻不实，|而且从来没用过这么多拣椒工。", "The company says the layoff rumor is false, | and it never had that many sorters."),
 ("人数之争我们先放一边，|今天只问一个烧脑问题：", "Let's leave the head count aside | and ask one brain-teaser:"),
 ("一台机器，从没吃过辣椒，|凭什么一眼看出哪颗是坏的？", "A machine that has never tasted a chili — | how does it spot a bad one at a glance?"),
 ("第一步，先说个秘密：|在相机眼里，根本没有辣椒。", "First, a secret: | to a camera, there is no chili."),
 ("只有几百万个小格子，叫像素，|每一格，就是三个数：红、绿、蓝。", "Only millions of tiny squares called pixels, | each just three numbers: red, green, blue."),
 ("好辣椒的格子，红的数很大，|绿和蓝都很小。", "Good chili pixels: big red, | small green and blue."),
 ("霉斑、黑斑呢？|三个数都很小，黑乎乎一片。", "Mold and black spots? | All three numbers small. Dark."),
 ("有的分拣机还看人眼看不见的光，|有些毛病在那种光下更显眼。", "Some sorters even see light our eyes can't, | where some flaws stand out more."),
 ("最笨的办法：数一数黑格子，|超过一定数量，就判它坏。", "The dumbest method: count dark pixels; | too many, and it's bad."),
 ("反转一：|这招很快就翻车。", "Twist one: | that trick breaks fast."),
 ("辣椒的影子是黑的，蒂把也是深色的，|一颗好椒也会被冤枉。", "Shadows are dark. Stems are dark. | A perfectly good chili gets framed."),
 ("所以现在用AI：|给它看成千上万张标好的照片。", "So now we use AI: | show it thousands of labeled photos."),
 ("这张好，那张坏，|它自己琢磨出霉斑长什么样。", "This one good, that one bad, | and it works out what mold looks like."),
 ("就像老师傅带徒弟：|不讲规则，只让你看一万颗。", "Like a master training an apprentice: | no rules, just look at ten thousand."),
 ("徒弟看多了就有了手感，|AI的手感，就是一大堆调好的数字。", "Look long enough and you get a feel. | An AI's feel is a pile of tuned numbers."),
 ("反转二，最反直觉：|看出来不难，难的是追上它。", "Twist two, the weird one: | spotting is easy. Catching is hard."),
 ("传送带一直在跑，|等算完，那颗辣椒已经往前走了。", "The belt never stops. | By the time the math is done, the chili has moved."),
 ("所以机器要算准：它现在在哪，|几分之一秒后会到哪。", "So the machine works out where it is now, | and where it'll be a split second later."),
 ("到了那一点，一个小喷嘴，|噗，吹一口气。", "At that spot, a tiny nozzle | goes pfft: one puff of air."),
 ("坏辣椒被吹飞，掉进废料槽，|好辣椒继续往前走。", "The bad chili flies into the reject bin; | the good ones roll on."),
 ("据报道，从看见到吹走，|也就零点三秒左右。", "Reportedly, from spotted to blown away | takes about 0.3 seconds."),
 ("吹早了吹到邻居，吹晚了吹个空，|这是一道物理题。", "Too early hits the neighbor, too late hits air. | It's a physics problem."),
 ("假如传送带每秒走一米，|晚百分之一秒，就偏一厘米。", "If the belt moves one meter a second, | a hundredth of a second late is a centimeter off."),
 ("反转三：|机器看得见，不等于看得懂。", "Twist three: | seeing isn't understanding."),
 ("颜色怪、其实没坏的，|它可能吹掉。", "Odd color but perfectly fine? | It might blow it away."),
 ("坏在里面、外面看不出的，|它可能放过。", "Rotten inside, clean outside? | It might let it pass."),
 ("所以还留着四十八位老师傅，|守最后一道关。", "That's why forty-eight experienced workers remain | on the final check."),
 ("据报道，关键工序的不良率，|降到了万分之二。", "Reportedly, the defect rate at the key step | fell to 0.02 percent."),
 ("友情提示：这是公司说的数字，|不是食品安全抽检结果。", "Fine print: that's the company's figure, | not a food safety test result."),
 ("人数怎么变的，各方说法不一，|我们只讲机器怎么看。", "Accounts of the head count differ; | we only explain how the machine sees."),
 ("同样的办法，早就用在挑米、挑豆、挑茶叶，|也帮机器人分拣快递。", "The same trick sorts rice, beans and tea, | and helps robots sort parcels."),
 ("所以答案是：机器不懂辣，|它只认得三个数，和一口气。", "So the answer: the machine knows nothing about spice. | Just three numbers, and one puff of air."),
 ("下次你吃到一瓶没有坏椒的辣酱，|记得谢谢那一口气。", "Next time your chili sauce has no bad chili, | thank that puff of air."),
]
TITLE = {"zh": "老干妈的AI，怎么挑出坏辣椒？", "en": "How Does an AI Spot a Bad Chili?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
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


def chili(a, x, y, k=1.0, d=0.0, mood="happy", bad=False):
    """小辣椒：红色长身子、绿蒂把、会眨眼的脸；坏辣椒身上有黑斑、愁眉苦脸。身子上下飘，蒂把一直晃。"""
    i, st = uid("ch"), uid("chs")
    if bad:
        mood = "sad"
    m = {"happy": f"M{x - 30 * k},{y + 8 * k} Q{x - 5 * k},{y + 28 * k} {x + 20 * k},{y + 8 * k}",
         "o": f"M{x - 15 * k},{y + 14 * k} a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0",
         "sad": f"M{x - 30 * k},{y + 24 * k} Q{x - 5 * k},{y + 6 * k} {x + 20 * k},{y + 24 * k}"}[mood]
    E = [E_(a, x, y, 260 * k, 100 * k, c="ink", fill="red", idp=i),
         E_(a, x + 115 * k, y + 18 * k, 70 * k, 50 * k, c="ink", fill="red", idp=i, sw=4),
         O(a, x - 40 * k, y - 14 * k, 8 * k, c="ink", fill="ink", idp=i), O(a, x + 10 * k, y - 14 * k, 8 * k, c="ink", fill="ink", idp=i),
         P(a, m, c="ink", w=4, idp=i),
         P(a, f"M{x - 125 * k},{y - 5 * k} Q{x - 160 * k},{y - 30 * k} {x - 175 * k},{y - 75 * k}", c="green", w=9, idp=st)]
    if bad:
        E += [O(a, x + 50 * k, y - 10 * k, 16 * k, c="ink", fill="ink", idp=i), O(a, x + 85 * k, y + 20 * k, 11 * k, c="ink", fill="ink", idp=i),
              O(a, x - 70 * k, y + 25 * k, 10 * k, c="ink", fill="ink", idp=i)]
    E += [pop(a, [i, st], d), bob(a, i, 7 * k, 1.1), bob(a, st, 7 * k, 1.1), wig(a, st, (x - 125 * k, y - 5 * k), 10, 2.2)]
    return E, [i, st]


def cam(a, x, y, k=1.0, d=0.0, beam=True):
    """小相机“阿眼”：蓝色机身、大镜头，镜头里的光圈一直转，往下打一道扫描光。"""
    i, ln, bm = uid("cm"), uid("cml"), uid("cmb")
    E = [R(a, x - 110 * k, y - 70 * k, 220 * k, 140 * k, c="ink", fill="blue", idp=i),
         R(a, x - 40 * k, y - 100 * k, 80 * k, 30 * k, c="ink", fill="paper", idp=i, sw=4),
         O(a, x, y, 52 * k, c="ink", fill="paper", idp=i),
         P(a, f"M{x - 36 * k},{y} L{x + 36 * k},{y} M{x},{y - 36 * k} L{x},{y + 36 * k} M{x - 22 * k},{y - 22 * k} L{x + 22 * k},{y + 22 * k}", c="ink", w=4, idp=ln),
         pop(a, [i, ln], d), bob(a, i, 6 * k, 1.0), bob(a, ln, 6 * k, 1.0), spin(a, ln, (x, y), 50)]
    if beam:
        E += [P(a, f"M{x - 40 * k},{y + 80 * k} L{x - 140 * k},{y + 300 * k} M{x + 40 * k},{y + 80 * k} L{x + 140 * k},{y + 300 * k}", c="gold", w=5, idp=bm),
              pop(a, bm, d + 0.2), wig(a, bm, (x, y + 80 * k), 6, 1.6)]
    return E, [i, ln]


def belt(a, y=760, d=0.0, x0=150, x1=1770):
    """传送带：上下两条带，四个滚轮一直转，带上的小箭头往前走。"""
    rl = uid("bl")
    E = [P(a, f"M{x0},{y} L{x1},{y} M{x0},{y + 70} L{x1},{y + 70}", c="ink", w=6, idp=rl), pop(a, rl, d)]
    for q in range(4):
        r = uid("rl")
        cx = x0 + 60 + (x1 - x0 - 120) * q / 3
        E += [O(a, cx, y + 35, 30, c="ink", fill="muted", idp=r, sw=4), P(a, f"M{cx - 28},{y + 35} L{cx + 28},{y + 35}", c="ink", w=4, idp=r),
              pop(a, r, d + 0.05 * q), spin(a, r, (cx, y + 35), 90)]
    ch = uid("bc")
    E += [P(a, " ".join(f"M{x0 + 120 + 300 * q},{y + 20} L{x0 + 150 + 300 * q},{y + 35} L{x0 + 120 + 300 * q},{y + 50}" for q in range(5)), c="muted", w=4, idp=ch),
          sh(a, ch, 160, 0, d + 0.1, 2.2)]
    return E


def puff(a, x, y, d=0.0, dirn=-1):
    """喷嘴吹气：喷嘴 + 三道气流依次射出。dirn=-1 往上吹。"""
    nz = uid("nz")
    E = [R(a, x - 30, y, 60, 90, c="ink", fill="muted", idp=nz), pop(a, nz, d)]
    for q in range(3):
        g = uid("gas")
        E += [P(a, f"M{x - 30 + 30 * q},{y - 10} Q{x - 45 + 30 * q},{y - 60} {x - 30 + 30 * q},{y - 110}", c="blue", w=5, idp=g),
              pop(a, g, d + 0.25 + 0.1 * q), sh(a, g, 0, dirn * 80, d + 0.35 + 0.1 * q, 0.6)]
    return E


def pix(a, x0, y0, cols, rows, sz, colors, d=0.0, stag=0.04):
    """像素格子：一格一格蹦出来。colors(c, r) -> 颜色名。"""
    E = []
    for r in range(rows):
        for c in range(cols):
            i = uid("px")
            E += [R(a, x0 + c * sz, y0 + r * sz, sz - 6, sz - 6, c="ink", fill=colors(c, r), idp=i, sw=3), pop(a, i, d + stag * (r * cols + c))]
    return E


def person(a, x, y, k=1.0, d=0.0, cap=False, c="ink"):
    """老师傅/徒弟：火柴人，手臂一直摆；cap=True 戴白帽子（老师傅）。"""
    i, ar = uid("ps"), uid("psa")
    E = [O(a, x, y - 170 * k, 45 * k, c=c, fill="paper", idp=i),
         P(a, f"M{x},{y - 125 * k} L{x},{y + 20 * k} M{x},{y + 20 * k} L{x - 50 * k},{y + 130 * k} M{x},{y + 20 * k} L{x + 50 * k},{y + 130 * k}", c=c, w=7, idp=i),
         P(a, f"M{x - 80 * k},{y - 30 * k} L{x},{y - 90 * k} L{x + 80 * k},{y - 30 * k}", c=c, w=7, idp=ar),
         O(a, x - 15 * k, y - 175 * k, 5 * k, c=c, fill=c, idp=i), O(a, x + 15 * k, y - 175 * k, 5 * k, c=c, fill=c, idp=i)]
    if cap:
        E.append(R(a, x - 45 * k, y - 240 * k, 90 * k, 40 * k, c="ink", fill="paper", idp=i, sw=4))
    E += [pop(a, [i, ar], d), bob(a, i, 5 * k, 1.0), wig(a, ar, (x, y - 90 * k), 14, 1.6), bob(a, ar, 5 * k, 1.0)]
    return E, [i, ar]


def bin_(a, x, y, d=0.0):
    i = uid("bin")
    return [R(a, x - 90, y, 180, 160, c="ink", fill="muted", idp=i), P(a, f"M{x - 110},{y} L{x + 110},{y}", c="ink", w=8, idp=i), pop(a, i, d), wig(a, i, (x, y + 160), 2, 1.2)]


RGB = lambda c, r: ("red", "green", "blue")[c % 3]  # noqa: E731
GOOD = lambda c, r: "red"  # noqa: E731
BADP = lambda c, r: "ink" if (c + r) % 3 == 0 else "red"  # noqa: E731

# 0 600 -> 48
ps = []
for q in range(8):
    ps += person(0, 300 + 190 * q, 560, 0.55, 0.05 * q)[0]
bd(0, ps, BIG(0, 960, 820, "600+", c="red", d=0.4, s=130))
p1, pid = person(0.5, 1300, 560, 0.8, 0.0)
bd(0.5, bar(0.5, 400, 800, 160, 500, "muted", d=0.0), bar(0.5, 700, 800, 160, 40, "red", d=0.4), T(0.5, 480, 860, 50, "600+", c="ink", d=0.1),
   T(0.5, 780, 860, 50, "48", c="red", d=0.5), p1, BIG(0.5, 1550, 350, "48", c="red", d=0.6, s=150))
# 1 cameras every 0.3 s
c1, cid = cam(1, 960, 300, 1.0)
c2, _ = cam(1, 450, 300, 0.7, 0.2)
c3, _ = cam(1, 1470, 300, 0.7, 0.3)
bd(1, c1, c2, c3, belt(1, 700, 0.1))
c1, cid = cam(1.5, 600, 350, 1.1)
bd(1.5, c1, ic(1.5, "clock", 1350, 380, 220, 0.1, mv="spin"), BIG(1.5, 1350, 700, "0.3 秒", c="red", d=0.4, s=140), [pulse(1.5, cid[0], 0.8)])
# 2 company response
bd(2, ic(2, "building", 500, 450, 260, 0.0, mv="bob"), ic(2, "speaker", 950, 420, 180, 0.2, mv="wig"), cross(2, 1450, 420, d=0.4), T(2, 1450, 600, 64, "传闻不实", c="red", d=0.5))
ps = []
for q in range(5):
    ps += person(2.5, 450 + 250 * q, 560, 0.6, 0.06 * q)[0]
bd(2.5, ps, ic(2.5, "question", 960, 250, 150, 0.4, mv="wig", c="red"), T(2.5, 960, 830, 60, "说法不一", c="ink", d=0.5))
# 3 set aside / brain-teaser
bd(3, ic(3, "building", 500, 450, 220, 0.0), [sh(3, [], 0, 0, 0, 0.1)][:0], arr(3, 750, 450, 1150, 450, c="muted", d=0.2), T(3, 1450, 450, 70, "先放一边", c="muted", d=0.4), cross(3, 500, 450, c="muted", d=0.6))
bd(3.5, ic(3.5, "question", 960, 400, 300, 0.0, mv="wig", c="red"), BIG(3.5, 960, 750, "烧脑问题", c="red", d=0.3, s=110), ic(3.5, "gear", 450, 400, 160, 0.2, mv="spin"), ic(3.5, "gear", 1470, 400, 160, 0.4, mv="spin"))
# 4 machine never tasted
c1, cid = cam(4, 600, 400, 1.1, beam=False)
ch, chid = chili(4, 1350, 450, 1.1)
bd(4, c1, ch, ic(4, "flame", 1350, 250, 120, 0.4, mv="wig", c="red"), cross(4, 900, 300, d=0.6))
g1, _ = chili(4.5, 550, 450, 0.9)
b1, bid = chili(4.5, 1350, 450, 0.9, bad=True)
bd(4.5, g1, b1, check(4.5, 550, 650, d=0.4), cross(4.5, 1350, 650, d=0.6), ic(4.5, "eye", 960, 300, 150, 0.2, mv="wig"))
# 5 no chili
c1, cid = cam(5, 960, 350, 1.2)
bd(5, c1, BIG(5, 400, 400, "秘密", c="red", d=0.3, s=120), ic(5, "magnifier", 1550, 400, 200, 0.4, mv="wig"))
ch, chid = chili(5.5, 600, 500, 1.0)
bd(5.5, ch, arr(5.5, 850, 500, 1100, 500, c="ink", d=0.2), pix(5.5, 1200, 320, 4, 4, 90, GOOD, d=0.4), [sh(5.5, chid, -80, 0, 0.9, 0.6)])
# 6 pixels, three numbers
bd(6, pix(6, 360, 260, 8, 5, 110, BADP, d=0.0, stag=0.03), BIG(6, 1500, 450, "几百万格", c="red", d=0.8, s=90))
bd(6.5, pix(6.5, 400, 300, 3, 1, 200, RGB, d=0.0, stag=0.25), T(6.5, 500, 600, 70, "红", c="red", d=0.1), T(6.5, 700, 600, 70, "绿", c="green", d=0.35),
   T(6.5, 900, 600, 70, "蓝", c="blue", d=0.6), BIG(6.5, 1400, 420, "3 个数", c="ink", d=0.8, s=120), ic(6.5, "computer", 1400, 700, 140, 0.9, mv="bob"))
# 7 good chili: big red
ch, chid = chili(7, 500, 450, 1.0)
bd(7, ch, bar(7, 1000, 780, 140, 450, "red", d=0.2), bar(7, 1200, 780, 140, 80, "green", d=0.4), bar(7, 1400, 780, 140, 60, "blue", d=0.6))
bd(7.5, pix(7.5, 400, 300, 5, 3, 120, GOOD, d=0.0), check(7.5, 1350, 450, d=0.5), T(7.5, 1350, 650, 64, "红大 绿蓝小", c="red", d=0.4), ic(7.5, "eye", 1550, 300, 120, 0.3, mv="wig"))
# 8 mold: all small
b1, bid = chili(8, 600, 450, 1.3, bad=True)
bd(8, b1, ic(8, "magnifier", 1300, 400, 220, 0.2, mv="wig"), T(8, 1350, 700, 64, "霉斑？黑斑？", c="ink", d=0.4))
bd(8.5, bar(8.5, 500, 780, 140, 50, "red", d=0.0), bar(8.5, 700, 780, 140, 40, "green", d=0.2), bar(8.5, 900, 780, 140, 40, "blue", d=0.4),
   pix(8.5, 1250, 300, 3, 3, 110, lambda c, r: "ink", d=0.3), T(8.5, 1400, 760, 60, "黑乎乎", c="ink", d=0.8))
# 9 invisible light
c1, cid = cam(9, 600, 300, 1.0)
bd(9, c1, ic(9, "eye", 1300, 400, 200, 0.2, mv="wig"), cross(9, 1300, 400, d=0.4), ic(9, "sun", 1550, 650, 140, 0.5, mv="spin", c="gold"))
b1, bid = chili(9.5, 960, 500, 1.2, bad=True)
bd(9.5, b1, ic(9.5, "laser", 400, 350, 180, 0.0, mv="wig", c="red"), arr(9.5, 500, 380, 750, 450, c="red", d=0.3), T(9.5, 1450, 300, 60, "看不见的光", c="blue", d=0.4), [pulse(9.5, bid[0], 0.8)])
# 10 count dark pixels
bd(10, pix(10, 400, 300, 6, 4, 100, BADP, d=0.0, stag=0.03), BIG(10, 1400, 380, "数黑格", c="ink", d=0.5, s=110), ic(10, "ruler", 1400, 650, 160, 0.6, mv="wig"))
bd(10.5, bar(10.5, 600, 780, 160, 450, "ink", d=0.0), [P(10.5, "M450,500 L950,500", c="red", w=6)], T(10.5, 1050, 500, 50, "门槛", c="red", d=0.3),
   cross(10.5, 1400, 450, d=0.6), T(10.5, 1400, 650, 64, "判坏", c="red", d=0.7))
# 11 twist one
bd(11, BIG(11, 960, 220, "反转一", c="red", d=0.0, s=120), ic(11, "question", 600, 550, 200, 0.2, mv="wig", c="red"), ic(11, "question", 1320, 550, 200, 0.4, mv="wig", c="red"))
ch, chid = chili(11.5, 960, 450, 1.2, mood="o")
bd(11.5, ch, [rot(11.5, chid, 25, (960, 450), 0.2, 0.4), rot(11.5, chid, -25, (960, 450), 0.7, 0.4)], BIG(11.5, 960, 750, "翻车", c="red", d=0.3, s=120))
# 12 shadows, stems: framed
ch, chid = chili(12, 900, 420, 1.1)
sd = uid("sd")
bd(12, ch, [E_(12, 950, 530, 300, 40, c="ink", fill="ink", idp=sd), pop(12, sd, 0.3), sh(12, sd, 60, 0, 0.6, 1.0)], ic(12, "sun", 300, 250, 150, 0.1, mv="spin", c="gold"),
   T(12, 1450, 300, 60, "影子", c="ink", d=0.4), arr(12, 1350, 330, 1150, 500, c="red", d=0.5))
ch, chid = chili(12.5, 800, 450, 1.1, mood="sad")
bd(12.5, ch, cross(12.5, 800, 450, d=0.3), BIG(12.5, 1400, 400, "冤枉！", c="red", d=0.4, s=110), ic(12.5, "question", 1400, 650, 140, 0.6, mv="wig", c="red"))
# 13 AI: thousands of labeled photos
ph = []
for q in range(6):
    i = uid("ph")
    ph += [R(13, 300 + 230 * q, 330 + 30 * (q % 2), 190, 150, c="ink", fill="paper", idp=i), pop(13, i, 0.08 * q), sh(13, i, 0, 30, 0.6 + 0.05 * q, 0.4)]
bd(13, ph, BIG(13, 960, 700, "AI", c="blue", d=0.3, s=150))
pp = []
for q in range(4):
    i = uid("ph")
    pp += [R(13.5, 250 + 260 * q, 350, 200, 160, c="ink", fill="paper", idp=i), pop(13.5, i, 0.1 * q), sh(13.5, i, 400, 0, 0.8 + 0.1 * q, 0.6)]
bd(13.5, pp, ic(13.5, "computer", 1500, 430, 240, 0.2, mv="bob"), T(13.5, 960, 720, 64, "成千上万张", c="ink", d=0.5))
# 14 this good, that bad
g1, _ = chili(14, 500, 400, 0.8)
b1, _ = chili(14, 1400, 400, 0.8, bad=True)
bd(14, g1, b1, check(14, 500, 600, d=0.3), cross(14, 1400, 600, d=0.5), T(14, 500, 720, 56, "好", c="green", d=0.3), T(14, 1400, 720, 56, "坏", c="red", d=0.5))
bd(14.5, ic(14.5, "computer", 700, 450, 260, 0.0, mv="bob"), ic(14.5, "gear", 700, 250, 120, 0.2, mv="spin"), arr(14.5, 900, 450, 1150, 450, c="ink", d=0.3),
   chili(14.5, 1450, 450, 0.8, bad=True)[0], T(14.5, 1450, 650, 56, "霉斑长这样", c="red", d=0.6))
# 15 master & apprentice
m1, mid = person(15, 600, 560, 1.0, 0.0, cap=True)
m2, _ = person(15, 1300, 600, 0.8, 0.2)
bd(15, m1, m2, T(15, 600, 840, 56, "老师傅", c="ink", d=0.2), T(15, 1300, 840, 56, "徒弟", c="ink", d=0.4))
cs = []
for q in range(5):
    cs += chili(15.5, 350 + 300 * q, 350 + 60 * (q % 2), 0.45, 0.1 * q, bad=(q == 3))[0]
bd(15.5, cs, BIG(15.5, 960, 700, "看一万颗", c="red", d=0.6, s=110))
# 16 feel = tuned numbers
m2, mid = person(16, 600, 600, 1.0, 0.0)
bd(16, m2, ic(16, "check", 1300, 400, 200, 0.3, mv="bob", c="green"), T(16, 1300, 650, 64, "手感", c="ink", d=0.4), star(16, 800, 300, 0.5, r=40))
dd = []
for q in range(3):
    dd += BIG(16.5, 500 + 450 * q, 350, ("0.73", "-1.2", "4.05")[q], c="blue", d=0.1 + 0.2 * q, s=110)
bd(16.5, dd, ic(16.5, "gear", 700, 650, 160, 0.3, mv="spin"), ic(16.5, "gear", 1200, 650, 160, 0.4, mv="spin"), T(16.5, 960, 830, 56, "一大堆调好的数", c="ink", d=0.6))
# 17 twist two
bd(17, BIG(17, 960, 220, "反转二", c="red", d=0.0, s=120), check(17, 650, 550, d=0.3), T(17, 650, 700, 64, "看出来", c="green", d=0.3), ic(17, "question", 1300, 550, 200, 0.5, mv="wig", c="red"))
ch, chid = chili(17.5, 500, 450, 0.9)
bd(17.5, ch, [sh(17.5, chid, 900, 0, 0.3, 1.3)], belt(17.5, 650, 0.0), BIG(17.5, 960, 300, "追上它", c="red", d=0.4, s=110))
# 18 belt keeps running
ch, chid = chili(18, 400, 560, 0.7)
c1, _ = cam(18, 400, 250, 0.7, beam=True)
bd(18, c1, ch, [sh(18, chid, 700, 0, 0.2, 1.6)], belt(18, 680, 0.0))
c1, cid = cam(18.5, 500, 250, 0.7)
ch, chid = chili(18.5, 600, 560, 0.7, mood="o")
bd(18.5, c1, ch, [sh(18.5, chid, 800, 0, 0.1, 1.2)], belt(18.5, 680, 0.0), ic(18.5, "clock", 1500, 300, 150, 0.2, mv="spin"))
# 19 where now, where later
ch, chid = chili(19, 450, 450, 0.8)
gh = uid("gh")
bd(19, ch, [E_(19, 1350, 450, 260, 100, c="red", idp=gh, sw=4), pop(19, gh, 0.4), pulse(19, gh, 0.9)], arr(19, 650, 450, 1150, 450, c="blue", d=0.2, dur=0.8),
   T(19, 450, 650, 56, "现在", c="ink", d=0.1), T(19, 1350, 650, 56, "过一会儿", c="blue", d=0.5))
bd(19.5, BIG(19.5, 960, 350, "几分之一秒", c="red", d=0.1, s=110), ic(19.5, "clock", 450, 600, 180, 0.2, mv="spin"), ic(19.5, "ruler", 1450, 600, 180, 0.4, mv="wig"), arr(19.5, 650, 650, 1250, 650, c="blue", d=0.5))
# 20 nozzle puff
bd(20, puff(20, 960, 600, 0.1), belt(20, 720, 0.0), T(20, 960, 300, 70, "小喷嘴", c="ink", d=0.2), ic(20, "wind", 1450, 400, 180, 0.3, mv="wig", c="blue"))
b1, bid = chili(20.5, 960, 560, 0.7, bad=True)
bd(20.5, b1, puff(20.5, 960, 640, 0.1), [sh(20.5, bid, 200, -350, 0.5, 0.6), rot(20.5, bid, 200, (960, 560), 0.5, 0.7)], BIG(20.5, 500, 300, "噗！", c="blue", d=0.4, s=150))
# 21 bad flies into bin, good roll on
b1, bid = chili(21, 700, 300, 0.7, bad=True)
bd(21, b1, [sh(21, bid, 500, 400, 0.2, 0.8)], bin_(21, 1300, 600, 0.0), T(21, 1300, 850, 56, "废料槽", c="muted", d=0.3))
g1, gid = chili(21.5, 400, 560, 0.6)
g2, gid2 = chili(21.5, 800, 560, 0.6)
bd(21.5, g1, g2, [sh(21.5, gid + gid2, 700, 0, 0.1, 1.6)], belt(21.5, 660, 0.0), check(21.5, 1500, 350, d=0.5))
# 22 0.3 s
c1, cid = cam(22, 500, 280, 0.8)
bd(22, c1, puff(22, 1300, 600, 0.4), arr(22, 650, 600, 1200, 600, c="red", d=0.2, dur=0.8), belt(22, 720, 0.0))
bd(22.5, BIG(22.5, 960, 420, "≈0.3 秒", c="red", d=0.0, s=160), ic(22.5, "clock", 400, 450, 200, 0.2, mv="spin"), ic(22.5, "wind", 1550, 450, 180, 0.4, mv="wig", c="blue"), T(22.5, 960, 650, 56, "据报道", c="muted", d=0.5))
# 23 too early / late
g1, gid = chili(23, 700, 500, 0.7)
b1, bid = chili(23, 1150, 500, 0.7, bad=True)
bd(23, g1, b1, puff(23, 700, 600, 0.2), [sh(23, gid, 0, -150, 0.6, 0.5)], T(23, 350, 300, 60, "吹早了", c="red", d=0.4), cross(23, 350, 420, d=0.8))
bd(23.5, BIG(23.5, 960, 300, "物理题", c="blue", d=0.1, s=130), ic(23.5, "atom", 500, 600, 180, 0.2, mv="spin"), ic(23.5, "ruler", 960, 650, 180, 0.3, mv="wig"), ic(23.5, "clock", 1420, 600, 180, 0.4, mv="spin"))
# 24 1 m/s, 1/100 s, 1 cm
bd(24, belt(24, 700, 0.0), BIG(24, 960, 350, "1 米/秒", c="blue", d=0.2, s=130), T(24, 960, 520, 56, "（假如）", c="muted", d=0.4), arr(24, 400, 620, 1500, 620, c="blue", d=0.3, dur=1.0))
bd(24.5, BIG(24.5, 600, 400, "0.01 秒", c="red", d=0.0, s=110), arr(24.5, 900, 400, 1100, 400, c="ink", d=0.3), BIG(24.5, 1450, 400, "1 厘米", c="red", d=0.5, s=110),
   ic(24.5, "ruler", 1450, 650, 180, 0.6, mv="wig"), ic(24.5, "clock", 600, 650, 150, 0.2, mv="spin"))
# 25 twist three
bd(25, BIG(25, 960, 220, "反转三", c="red", d=0.0, s=120), ic(25, "eye", 650, 550, 220, 0.2, mv="wig"), ic(25, "question", 1300, 550, 200, 0.4, mv="wig", c="red"))
c1, cid = cam(25.5, 700, 400, 1.1, beam=False)
bd(25.5, c1, T(25.5, 1350, 350, 64, "看得见", c="green", d=0.2), check(25.5, 1650, 350, d=0.3), T(25.5, 1350, 550, 64, "看得懂？", c="red", d=0.5), cross(25.5, 1650, 550, d=0.7))
# 26 odd colour but fine
ch, chid = chili(26, 800, 450, 1.1)
bd(26, ch, ic(26, "sun", 1350, 300, 140, 0.2, mv="spin", c="gold"), T(26, 1400, 600, 60, "颜色怪", c="gold", d=0.4), check(26, 1400, 750, d=0.6))
ch, chid = chili(26.5, 700, 560, 0.8, mood="o")
bd(26.5, ch, puff(26.5, 700, 650, 0.0), [sh(26.5, chid, 500, -350, 0.4, 0.6)], BIG(26.5, 1400, 300, "误吹", c="red", d=0.6, s=110))
# 27 rotten inside
ch, chid = chili(27, 800, 450, 1.2)
cr = uid("cr")
bd(27, ch, [O(27, 820, 455, 30, c="ink", fill="ink", idp=cr), pop(27, cr, 0.4), pulse(27, cr, 0.8)], T(27, 1450, 400, 64, "坏在里面", c="red", d=0.3), ic(27, "magnifier", 1450, 650, 150, 0.5, mv="wig"))
g1, gid = chili(27.5, 400, 560, 0.7)
bd(27.5, g1, [sh(27.5, gid, 900, 0, 0.1, 1.5)], belt(27.5, 680, 0.0), T(27.5, 1300, 300, 64, "放过", c="red", d=0.5), cam(27.5, 960, 270, 0.6, 0.0)[0])
# 28 48 masters
ps = []
for q in range(4):
    ps += person(28, 450 + 340 * q, 560, 0.7, 0.08 * q, cap=True)[0]
bd(28, ps, BIG(28, 960, 850, "48", c="red", d=0.4, s=110))
m1, mid = person(28.5, 600, 560, 1.0, cap=True)
bd(28.5, m1, ic(28.5, "eye", 1050, 400, 160, 0.2, mv="wig"), T(28.5, 1450, 450, 64, "最后一道关", c="blue", d=0.4), check(28.5, 1450, 650, d=0.6))
# 29 defect rate 0.02%
bd(29, ic(29, "building", 450, 450, 200, 0.0, mv="bob"), BIG(29, 1150, 420, "万分之二", c="red", d=0.2, s=140), T(29, 1150, 600, 60, "0.02%", c="ink", d=0.4))
dots = []
for q in range(20):
    i = uid("dt")
    dots += [O(29.5, 450 + 110 * (q % 10), 350 + 140 * (q // 10), 30, c="ink", fill=("ink" if q == 13 else "red"), idp=i, sw=3), pop(29.5, i, 0.03 * q)]
bd(29.5, dots, T(29.5, 960, 720, 56, "一万颗里约两颗", c="ink", d=0.6), [pulse(29.5, dots[2 * 13]["id"], 0.9)])
# 30 fine print
bd(30, BIG(30, 960, 200, "友情提示", c="ink", d=0.0, s=100), ic(30, "building", 600, 550, 200, 0.2), ic(30, "speaker", 1000, 520, 140, 0.3, mv="wig"), T(30, 1450, 550, 60, "公司的数字", c="blue", d=0.5))
bd(30.5, ic(30.5, "flask", 700, 450, 220, 0.0, mv="wig"), cross(30.5, 700, 450, d=0.4), T(30.5, 1300, 450, 60, "不是抽检结果", c="red", d=0.3), ic(30.5, "magnifier", 1300, 650, 140, 0.5, mv="wig"))
# 31 accounts differ; we explain the machine
ps = []
for q in range(3):
    ps += person(31, 500 + 450 * q, 560, 0.7, 0.1 * q)[0]
bd(31, ps, ic(31, "question", 725, 300, 120, 0.4, mv="wig", c="red"), ic(31, "question", 1175, 300, 120, 0.5, mv="wig", c="red"))
c1, cid = cam(31.5, 700, 350, 1.1)
bd(31.5, c1, ic(31.5, "eye", 1350, 400, 220, 0.2, mv="wig"), T(31.5, 1350, 650, 60, "机器怎么看", c="blue", d=0.4))
# 32 rice, beans, tea, parcels
gr = []
for q in range(12):
    i = uid("rc")
    gr += [E_(32, 350 + 110 * (q % 6), 350 + 100 * (q // 6), 60, 34, c="ink", fill=("gold" if q != 7 else "ink"), idp=i, sw=3), pop(32, i, 0.04 * q)]
bd(32, gr, T(32, 650, 650, 60, "米 豆 茶叶", c="ink", d=0.5), puff(32, 1400, 500, 0.6), ic(32, "water", 1400, 300, 100, 0.3, mv="bob", c="blue"))
bx = uid("bx")
bd(32.5, ic(32.5, "robot_arm", 600, 450, 260, 0.0, mv="wig"), [R(32.5, 1100, 400, 200, 150, c="ink", fill="gold", idp=bx), pop(32.5, bx, 0.2), sh(32.5, bx, 300, 0, 0.6, 0.8)],
   belt(32.5, 640, 0.1), T(32.5, 1300, 300, 60, "分拣快递", c="ink", d=0.4))
# 33 three numbers and a puff
ch, chid = chili(33, 600, 450, 1.0)
bd(33, ch, ic(33, "flame", 600, 260, 120, 0.2, mv="wig", c="red"), cross(33, 850, 260, d=0.4), T(33, 1350, 450, 70, "不懂辣", c="red", d=0.4))
bd(33.5, pix(33.5, 450, 330, 3, 1, 180, RGB, d=0.0, stag=0.2), BIG(33.5, 1150, 420, "+", c="ink", d=0.5, s=120), puff(33.5, 1450, 520, 0.6), T(33.5, 960, 750, 64, "三个数 + 一口气", c="blue", d=0.7))
# 34 thank the puff
jar = uid("jar")
g1, gid = chili(34, 1350, 450, 0.8)
bd(34, [R(34, 450, 300, 300, 400, c="ink", fill="red", idp=jar), R(34, 430, 260, 340, 60, c="ink", fill="gold", idp=jar), pop(34, jar, 0.0), wig(34, jar, (600, 700), 3, 1.2)],
   g1, check(34, 1350, 650, d=0.5), T(34, 600, 800, 56, "辣酱", c="ink", d=0.3))
bd(34.5, puff(34.5, 700, 550, 0.0), BIG(34.5, 1300, 400, "谢谢", c="red", d=0.4, s=150), T(34.5, 1300, 600, 64, "那一口气", c="blue", d=0.6), ic(34.5, "wind", 700, 300, 160, 0.3, mv="wig", c="blue"))

INS = [
 (1, "据报道，挑出来的坏辣椒，|是被一股气流直接吹走的。", "Reportedly, the bad chilies | are simply blown away by a jet of air."),
 (6, "你的手机屏幕也是这么拼出来的，|凑近看，全是红绿蓝的小点。", "Your phone screen works the same way: | up close, it's all red, green and blue dots."),
 (13, "这叫监督学习：|人先把答案标好，它照着学。", "That's called supervised learning: | people label the answers, and it learns from them."),
 (18, "这就像接球：|你不是追着球跑，是先猜它落在哪。", "It's like catching a ball: | you don't chase it, you guess where it will land."),
 (20, "色选机的喷气阀，开关只要几毫秒，|比眨一下眼快几十倍。", "A sorter's air valve opens in a few milliseconds, | dozens of times faster than a blink."),
 (32, "机器人学里，这叫感知、决策、执行：|看见、算好、出手。", "In robotics it's called sense, think, act: | see it, work it out, make the move."),
]
# 100 气流吹走
b1, bid = chili(100, 700, 450, 1.0, bad=True)
bd(100, b1, [sh(100, bid, 0, -300, 0.4, 0.6)], puff(100, 700, 560, 0.1), ic(100, "wind", 1350, 400, 220, 0.2, mv="wig", c="blue"))
bd(100.5, puff(100.5, 600, 600, 0.0), bin_(100.5, 1300, 500, 0.2), arr(100.5, 700, 450, 1150, 450, c="blue", d=0.4), BIG(100.5, 960, 280, "一股气", c="blue", d=0.5, s=110))
# 101 屏幕 = 红绿蓝小点
bd(101, ic(101, "phone", 600, 450, 300, 0.0, mv="wig"), ic(101, "magnifier", 1000, 450, 200, 0.2, mv="wig"), arr(101, 1150, 450, 1300, 450, c="ink", d=0.4))
dts = []
for q in range(15):
    i = uid("rgb")
    dts += [O(101.5, 500 + 130 * (q % 5) + 40 * (q // 5 % 2), 330 + 120 * (q // 5), 40, c="ink", fill=("red", "green", "blue")[q % 3], idp=i, sw=3), pop(101.5, i, 0.04 * q), pulse(101.5, i, 0.8 + 0.03 * q)]
bd(101.5, dts, T(101.5, 1450, 450, 64, "红 绿 蓝", c="ink", d=0.6))
# 102 监督学习
bd(102, BIG(102, 960, 350, "监督学习", c="blue", d=0.0, s=120), ic(102, "computer", 500, 650, 160, 0.2, mv="bob"), ic(102, "check", 960, 650, 140, 0.4, mv="bob", c="green"), ic(102, "eye", 1420, 650, 140, 0.5, mv="wig"))
p1, pid = person(102.5, 500, 600, 0.9, 0.0)
bd(102.5, p1, pix(102.5, 800, 380, 3, 2, 120, BADP, d=0.2), T(102.5, 1550, 400, 60, "标好答案", c="red", d=0.5), check(102.5, 1550, 600, d=0.7))
# 103 接球
ba = uid("ball")
p1, pid = person(103, 1400, 600, 0.9, 0.0)
bd(103, p1, [O(103, 400, 300, 45, c="ink", fill="red", idp=ba), pop(103, ba, 0.0), sh(103, ba, 900, 200, 0.3, 1.2), spin(103, ba, (400, 300), 60)],
   [P(103, "M400,300 Q900,80 1300,500", c="blue", w=4, idp=uid("tr"))], T(103, 800, 750, 60, "先猜落点", c="blue", d=0.5))
gx = uid("gx")
ch, chid = chili(103.5, 450, 560, 0.7)
bd(103.5, ch, [sh(103.5, chid, 800, 0, 0.2, 1.2), E_(103.5, 1300, 560, 220, 90, c="red", idp=gx, sw=4), pop(103.5, gx, 0.1), pulse(103.5, gx, 0.7)], belt(103.5, 680, 0.0))
# 104 几毫秒
bd(104, puff(104, 600, 550, 0.0), puff(104, 800, 550, 0.2), BIG(104, 1350, 400, "几毫秒", c="red", d=0.3, s=130), ic(104, "clock", 1350, 650, 150, 0.4, mv="spin"))
ey = uid("ey")
bd(104.5, ic(104.5, "eye", 600, 450, 260, 0.0, mv="wig"), [P(104.5, "M480,450 Q600,520 720,450", c="ink", w=8, idp=ey), pop(104.5, ey, 0.3), pulse(104.5, ey, 0.6)],
   T(104.5, 1350, 380, 70, "快几十倍", c="red", d=0.4), ic(104.5, "wind", 1350, 600, 160, 0.5, mv="wig", c="blue"))
# 105 感知 决策 执行
bd(105, ic(105, "eye", 450, 420, 180, 0.0, mv="wig"), ic(105, "chip", 960, 420, 180, 0.3, mv="spin"), ic(105, "robot_arm", 1470, 420, 180, 0.6, mv="wig"),
   arr(105, 580, 420, 830, 420, c="ink", d=0.2), arr(105, 1090, 420, 1340, 420, c="ink", d=0.5))
bd(105.5, T(105.5, 450, 450, 80, "看见", c="blue", d=0.0), T(105.5, 960, 450, 80, "算好", c="gold", d=0.3), T(105.5, 1470, 450, 80, "出手", c="red", d=0.6),
   cam(105.5, 450, 700, 0.5, 0.1, beam=False)[0], ic(105.5, "gear", 960, 700, 120, 0.4, mv="spin"), puff(105.5, 1470, 650, 0.7))

S2, MAP = [], {}
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
    main(here, S, B, TITLE, "zh", say={"AI": "A I", "0.3": "零点三", "0.02": "零点零二"})
