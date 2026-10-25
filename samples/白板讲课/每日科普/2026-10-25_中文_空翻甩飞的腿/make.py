"""每日科普 2026-10-25（中文）：《机器人空翻，腿怎么飞了？》
新闻：10 月 22 日宇树“物理 AI 大会”上，新发布的 H2-X“功夫传奇守护”人形机器人侧空翻落地失稳，一条机械小腿从关节处脱落、
滑到垫子上（新浪科技 2026-10-23 finance.sina.com.cn/tech/discovery/2026-10-23/doc-iniweywn8239244.shtml；
dimsumdaily.hk 2026-10-23：右小腿；截至报道公司未回应）。新浪科技热点小时报 10 月 25 日 09 时第 12 条、互联网热点小时报第 7 条。
参数（据报道，techeblog）：身高约 182 cm、体重约 70 kg、腿部关节扭矩约 360 N·m；宣传片 4 米高台翻下、能踢开车门。
课本物理：腾空后角动量守恒；落地冲击 F = m(g + v²/2d)。我们的估算（片中说是估算）：从 0.5 m 落下 v ≈ 3.1 m/s；
屈膝 30 cm 缓冲 ≈ 2.7 倍体重，腿绷直 5 cm ≈ 11 倍体重（70 kg → 约 770 公斤力）；侧空翻腾空约半秒。
“腿怕掰不怕压”导致脱落是我们的推测；学走路的小孩一小时摔十几次（Adolph 等 2012，约 17 次/小时）。
角色：小翻（会空翻的小机器人，小腿可以甩出去）。梗：“腿：我先走了”。
    python3 make.py <kokoro 模型目录> | --boards-only | --fake   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("一台一米八的机器人空翻落地，|一条腿飞了出去。", "A 1.8-meter robot lands a flip, | and one of its legs flies off."),
 ("腿说：我先走了。|机器人：等等我！", "The leg: I'm out. | The robot: wait for me!"),
 ("这是10月22日，宇树H2-X|在自家发布会上的表演。", "This was Unitree's H2-X on October 22, | live at the company's own launch event."),
 ("今天的问题：机器人那么硬，|腿怎么说掉就掉？", "Today's question: robots are so tough, | so how does a leg just fall off?"),
 ("认识一下小翻，|一个热爱空翻的小机器人。", "Meet Flip, | a little robot who loves flips."),
 ("据报道，H2-X身高大约1米82，|体重大约70公斤。", "Reportedly, the H2-X is about 1.82 meters tall | and weighs about 70 kilos."),
 ("宣传片里，它从4米高台翻下来，|稳稳落地。", "In its promo video, it flips off a 4-meter platform | and sticks the landing."),
 ("可现场这一次，侧空翻转到一半，|姿态乱了。", "But live on stage, halfway through a side flip, | it lost its balance."),
 ("落地没站稳，右边小腿从关节处脱落，|滑到了垫子上。", "It landed badly, and the right lower leg came off at the joint | and slid across the mat."),
 ("第一个道理：一跳起来，|转多少就定了。", "Lesson one: once you leave the ground, | your spin is locked in."),
 ("空中没有东西可以推，|这叫角动量守恒。", "There's nothing to push on in midair. | That's conservation of angular momentum."),
 ("就像花样滑冰：手一收转得快，|手一伸转得慢。", "Like a figure skater: arms in, faster. | Arms out, slower."),
 ("但总的转动，|起跳那一刻就交了卷。", "But the total spin | is handed in at takeoff, like an exam."),
 ("起跳差一点点，|落地就歪一大截。", "A tiny error at takeoff | becomes a big tilt at landing."),
 ("我们估算：侧空翻在空中大约只有半秒，|想纠正，几乎来不及。", "Our estimate: a side flip is airborne for about half a second. | Barely any time to fix it."),
 ("第二个道理：落地那一下，|力有多大？", "Lesson two: how hard | is the landing?"),
 ("我们估算：从半米高落下，|落地速度大约每秒3米。", "Our estimate: falling half a meter, | you hit the ground at about 3 meters a second."),
 ("如果膝盖弯一弯，用30厘米慢慢停，|冲击大约是体重的2.7倍。", "Bend the knees and stop over 30 centimeters: | the force is about 2.7 times body weight."),
 ("如果腿绷直，只用5厘米就停住，|冲击就是体重的11倍！", "Lock the legs and stop in 5 centimeters: | 11 times body weight!"),
 ("70公斤的机器人，|一条腿要扛七百多公斤的力。", "For a 70-kilo robot, | one leg takes the force of over 700 kilos."),
 ("所以人落地都会屈膝，|时间拉长，力就变小。", "That's why we bend our knees: | stretch the time, shrink the force."),
 ("第三个道理，最反直觉：|腿不怕压，怕掰。", "Lesson three, the weirdest: | legs don't mind squeezing. They hate bending."),
 ("就像一根筷子：顺着压很难压断，|横着一掰就断。", "Like a chopstick: push along it, it holds. | Bend it sideways, snap."),
 ("我们推测：姿态一歪，力从侧面来，|整条腿就成了被横掰的筷子。", "Our guess: with the body tilted, the force comes sideways, | and the leg becomes a bent chopstick."),
 ("而最先吃不住的，|往往是关节这种接缝。", "And the first thing to give | is usually a seam, like a joint."),
 ("据报道，它腿部关节扭矩大约360牛米，|能一脚踢开车门。", "Reportedly its leg joints make about 360 newton-meters, | enough to kick in a car door."),
 ("可力气大不等于扛得住：|齿轮、螺栓，都有极限。", "But strong isn't the same as tough: | gears and bolts all have limits."),
 ("工程上还有一招：故意留个保险丝，|先坏便宜的零件，保住贵的。", "Engineers also have a trick: a built-in fuse. | A cheap part breaks first to save the expensive ones."),
 ("这次是故障还是保护设计？|截至报道，宇树还没有回应。", "Was this a failure, or a safety feature? | As of the reports, Unitree hasn't said."),
 ("友情提示：官方原因还没公布，|今天讲的是我们按物理做的推测。", "Friendly fine print: no official cause yet. | Today's story is our physics-based guess."),
 ("机器人摔一跤不丢人，|每一跤，工程师都能学到东西。", "A robot falling isn't shameful. | Every fall teaches the engineers something."),
 ("据研究，学走路的小孩，|一小时能摔十几次。", "Studies find toddlers learning to walk | fall more than ten times an hour."),
 ("所以别笑小翻，|它只是在交学费。", "So don't laugh at Flip. | It's just paying tuition."),
 ("下次再空翻，记得：屈膝、站稳，|腿别先走。", "Next flip, remember: bend, land, stay together. | Legs, don't leave first."),
]

SX = {
 100: ("再烧一点：猫从空中掉下，|却能在半空翻个身。", "Even weirder: a falling cat | can still turn itself over in midair."),
 101: ("它先扭前半身、再扭后半身，|总转动一直是零，照样翻过来。", "It twists its front half, then its back half. | Total spin stays zero, and it still flips over."),
 102: ("机器人也能学这招，|可只有半秒钟，太紧了。", "Robots can learn that trick too, | but half a second is tight."),
 103: ("人跑步时，每一步脚下，|大约是体重的两三倍。", "When you run, each step pushes on the ground | with about two to three times your weight."),
 104: ("体操运动员落地，|膝盖、脚踝、髋部一起当弹簧。", "Gymnasts land with knees, ankles and hips | all working as springs."),
 105: ("机器人腿里，电机就是肌肉，|落地时要像弹簧一样往回收。", "In a robot leg, the motors are the muscles. | On landing they have to give, like springs."),
 106: ("要是这一刻控制没算准，|电机就会硬顶。", "If the control gets that moment wrong, | the motors push back stiff."),
}
ORDER = list(range(0, 15)) + [100, 101, 102] + list(range(15, 21)) + [103, 104] + list(range(21, 27)) + [105, 106] + list(range(27, 34))
TITLE = {"zh": "机器人空翻，腿怎么飞了？", "en": "Why Did the Robot's Leg Fly Off?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 880, 0.5, r=16)
    B.append(E)


def bot(a, x, y, k=1.0, mood="happy", d=None, kick=None, tilt=0, legless=False):
    """小翻：方脑袋小机器人，天线会摇、手会挥；右小腿单独编号（i+'sn'），kick=(dx, dy, 角度, 延时) 让它甩出去。"""
    i = uid("bt") + "_"
    an, ar, sn = i + "an", i + "ar", i + "sn"
    E = [R(a, x - 60 * k, y - 230 * k, 120 * k, 95 * k, c="ink", fill="blue", idp=i),
         O(a, x - 25 * k, y - 190 * k, 11 * k, c="ink", fill="ink", idp=i), O(a, x + 25 * k, y - 190 * k, 11 * k, c="ink", fill="ink", idp=i),
         R(a, x - 50 * k, y - 125 * k, 100 * k, 130 * k, c="ink", fill="muted", idp=i),
         O(a, x, y - 70 * k, 14 * k, c="red", fill="red", idp=i),
         P(a, f"M{x},{y - 230 * k} L{x},{y - 275 * k}", c="ink", w=5, idp=an), O(a, x, y - 285 * k, 10 * k, c="red", fill="red", idp=an),
         P(a, f"M{x - 50 * k},{y - 110 * k} L{x - 110 * k},{y - 40 * k} M{x + 50 * k},{y - 110 * k} L{x + 110 * k},{y - 170 * k}", c="ink", w=8, idp=ar),
         P(a, f"M{x - 25 * k},{y + 5 * k} L{x - 35 * k},{y + 75 * k} L{x - 30 * k},{y + 150 * k} L{x - 60 * k},{y + 150 * k}", c="ink", w=9, idp=i),
         P(a, f"M{x + 25 * k},{y + 5 * k} L{x + 35 * k},{y + 75 * k}", c="ink", w=9, idp=i),
         O(a, x + 35 * k, y + 75 * k, 9 * k, c="red", fill="red", idp=i)]
    if not legless:
        E.append(P(a, f"M{x + 35 * k},{y + 80 * k} L{x + 30 * k},{y + 150 * k} L{x + 60 * k},{y + 150 * k}", c="gold", w=10, idp=sn))
    m = {"happy": f"M{x - 25 * k},{y - 165 * k} Q{x},{y - 145 * k} {x + 25 * k},{y - 165 * k}",
         "o": f"M{x - 10 * k},{y - 160 * k} a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0",
         "sad": f"M{x - 25 * k},{y - 150 * k} Q{x},{y - 170 * k} {x + 25 * k},{y - 150 * k}"}[mood]
    E += [P(a, m, c="ink", w=5, idp=i), wig(a, an, (x, y - 230 * k), 14, 2.0), wig(a, ar, (x, y - 110 * k), 8, 1.6), bob(a, i, 6 * k, 1.3)]
    if not legless:
        E.append(bob(a, sn, 6 * k, 1.3))
    allp = [i, an, ar] + ([] if legless else [sn])
    if tilt:
        E.append(rot(a, allp, tilt, (x, y), 0.3, 0.8))
    if kick and not legless:
        dx, dy, ang, dl = kick
        E += [rot(a, sn, ang, (x + 35 * k, y + 80 * k), dl, 0.9), sh(a, sn, dx, dy, dl, 0.9)]
    if d is not None:
        E.append(pop(a, allp, d))
    return E, i


def icon(a, name, x, y, s, d=0.0, c="ink", mv="bob"):
    i = uid("ic")
    m = bob(a, i, 6, 1.1) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 6, 1.5))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def mat(a, y=860, x0=300, x1=1620):
    i = uid("mt")
    return [R(a, x0, y, x1 - x0, 40, c="ink", fill="ink", idp=i), bob(a, i, 2, 0.5)]


def spinarc(a, x, y, r=170, c="red", d=0.0, rpm=60):
    i = uid("sa")
    return [P(a, f"M{x + r},{y} A{r},{r} 0 1,1 {x},{y - r}", c=c, w=6, idp=i),
            P(a, f"M{x - 20},{y - r - 20} L{x},{y - r} L{x - 20},{y - r + 20}", c=c, w=6, idp=i), pop(a, i, d), spin(a, i, (x, y), rpm)]


def chop(a, x, y, L=420, ang=0, c="gold", d=0.0, idp=None):
    i = idp or uid("cp")
    return [R(a, x - L / 2, y - 14, L, 28, c="ink", fill=c, idp=i), pop(a, i, d), rot(a, i, ang, (x, y), 0, 0.01) if ang else bob(a, i, 3, 0.8)], i


def gear(a, x, y, s=160, d=0.0, rpm=50, c="ink"):
    i = uid("gr")
    return [{"t": "icon", "at": a, "id": i, "name": "gear", "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), spin(a, i, (x, y), rpm)]


def person(a, x, y, k=1.0, c="ink", arms_in=False):
    i = uid("ps")
    ar = i + "ar"
    E = [O(a, x, y - 130 * k, 40 * k, c=c, idp=i), P(a, f"M{x},{y - 90 * k} L{x},{y + 40 * k} M{x},{y + 40 * k} L{x - 40 * k},{y + 130 * k} M{x},{y + 40 * k} L{x + 40 * k},{y + 130 * k}", c=c, w=6, idp=i)]
    if arms_in:
        E.append(P(a, f"M{x - 25 * k},{y - 60 * k} L{x},{y - 40 * k} L{x + 25 * k},{y - 60 * k}", c=c, w=6, idp=ar))
    else:
        E.append(P(a, f"M{x - 110 * k},{y - 60 * k} L{x + 110 * k},{y - 60 * k}", c=c, w=6, idp=ar))
    E += [bob(a, i, 4, 1.0), spin(a, ar, (x, y - 60 * k), 140 if arms_in else 40)]
    return E, i


def fall(a, x, y0, y1, d=0.0, dur=0.6):
    i = uid("bl")
    return [O(a, x, y0, 30, c="ink", fill="red", idp=i), sh(a, i, 0, y1 - y0, d, dur), pulse(a, i, d + dur)]


def spring(a, x, y, h, c="blue", d=0.0):
    i = uid("sp")
    pts = " ".join(f"L{x + (30 if q % 2 else -30)},{y - h * (q + 1) / 9}" for q in range(8))
    return [P(a, f"M{x},{y} {pts} L{x},{y - h}", c=c, w=5, idp=i), {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x, y], "dur": 0.6, "delay": d}, wig(a, i, (x, y), 3, 2.5)]


def bolt(a, x, y, d=0.0):
    i = uid("bo")
    return [P(a, f"M{x - 60},{y} L{x + 60},{y} M{x + 60},{y - 22} L{x + 60},{y + 22} M{x - 40},{y - 14} L{x - 40},{y + 14} M{x - 15},{y - 14} L{x - 15},{y + 14} M{x + 10},{y - 14} L{x + 10},{y + 14}", c="ink", w=7, idp=i),
            pop(a, i, d), wig(a, i, (x, y), 8, 2.4)]


def crack(a, x, y, d=0.0):
    i = uid("ck")
    return [P(a, f"M{x - 30},{y - 50} L{x + 10},{y - 15} L{x - 15},{y + 10} L{x + 25},{y + 50}", c="red", w=7, idp=i), pop(a, i, d), pulse(a, i, d + 0.4)]


# 0 一米八机器人空翻
b_, bi = bot(0, 960, 600, 1.3, kick=(520, 160, 300, 0.8))
bd(0, b_, mat(0), spinarc(0, 960, 420, 300, d=0.0, rpm=90), BIG(0, 400, 300, "1.8米", c="red", d=0.2, s=120))
# 0.5 一条腿飞了出去
b_, bi = bot(0.5, 760, 600, 1.2, mood="o", kick=(700, 120, 540, 0.2))
bd(0.5, b_, mat(0.5), BIG(0.5, 1300, 300, "腿飞了！", c="red", d=0.3, s=130), arr(0.5, 900, 760, 1500, 820, c="red", d=0.2))
# 1 腿：我先走了
b_, bi = bot(1, 600, 620, 1.1, legless=True, mood="o")
li = uid("lg")
bd(1, b_, mat(1), [P(1, "M1300,560 L1290,700 L1340,700", c="gold", w=12, idp=li), O(1, 1300, 470, 30, c="ink", idp=li), sh(1, li, 300, 0, 0.3, 1.6), wig(1, li, (1300, 700), 10, 3)],
   T(1, 1350, 300, 64, "腿：我先走了～", c="gold", d=0.1))
# 1.5 等等我
b_, bi = bot(1.5, 700, 620, 1.1, legless=True, mood="sad")
bd(1.5, b_, [sh(1.5, [bi, bi + "an", bi + "ar"], 300, 0, 0.2, 1.4)], mat(1.5), T(1.5, 700, 230, 70, "等等我！", c="red", d=0.1),
   [e for q in range(3) for e in icon(1.5, "wind", 1250 + 180 * q, 560, 100, 0.2 + 0.1 * q, c="blue", mv="wig")])
# 2 10月22日
bd(2, BIG(2, 960, 260, "10月22日", c="blue", d=0.0, s=120), bot(2, 960, 700, 1.0, d=0.2)[0], icon(2, "clock", 1500, 600, 180, 0.3, mv="spin"),
   icon(2, "map_pin", 420, 600, 140, 0.4, c="red"))
# 2.5 自家发布会
bd(2.5, icon(2.5, "building", 500, 520, 300, 0.0), T(2.5, 1250, 320, 72, "宇树 H2-X", c="blue", d=0.1), icon(2.5, "speaker", 1500, 600, 180, 0.2, mv="wig"),
   bot(2.5, 1050, 720, 0.8, d=0.3)[0], [e for q in range(4) for e in star(2.5, 800 + 160 * q, 160, 0.3 + 0.1 * q)])
# 3 机器人那么硬
bd(3, bot(3, 600, 640, 1.2)[0], icon(3, "gear", 1200, 400, 200, 0.1, mv="spin"), icon(3, "magnet", 1500, 650, 160, 0.3), T(3, 1350, 860, 56, "钢铁 + 电机", c="ink", d=0.4))
# 3.5 腿怎么说掉就掉
b_, bi = bot(3.5, 700, 620, 1.2, mood="o", kick=(160, 120, 60, 0.5))
bd(3.5, b_, icon(3.5, "question", 1350, 450, 300, 0.1, c="red", mv="wig"), T(3.5, 1350, 780, 64, "说掉就掉？", c="red", d=0.4), mat(3.5))
# 4 认识小翻
bd(4, bot(4, 760, 640, 1.6, d=0.0)[0], BIG(4, 1450, 380, "小翻", c="blue", d=0.3, s=150), [e for q in range(3) for e in star(4, 1330 + 120 * q, 600, 0.5 + 0.1 * q, r=30)])
# 4.5 热爱空翻
b_, bi = bot(4.5, 960, 600, 1.0)
bd(4.5, b_, [rot(4.5, [bi, bi + "an", bi + "ar", bi + "sn"], 360, (960, 500), 0.2, 1.2), sh(4.5, [bi, bi + "an", bi + "ar", bi + "sn"], 0, -120, 0.2, 0.6)], mat(4.5),
   spinarc(4.5, 960, 480, 330, c="gold", d=0.1), T(4.5, 1550, 300, 60, "爱空翻！", c="gold", d=0.3))
# 5 1米82
bd(5, bot(5, 700, 640, 1.4)[0], [e for e in arr(5, 1000, 860, 1000, 200, c="red", d=0.2, dur=0.6)], BIG(5, 1400, 420, "1.82米", c="red", d=0.3, s=130), icon(5, "ruler", 1400, 700, 160, 0.4, mv="wig"))
# 5.5 70公斤
bd(5.5, icon(5.5, "block_force", 600, 520, 280, 0.0, mv="bob"), BIG(5.5, 1250, 420, "70公斤", c="blue", d=0.2, s=140), person(5.5, 1500, 720, 0.8)[0], T(5.5, 1250, 860, 52, "跟一个成年人差不多", c="muted", d=0.4))
# 6 4米高台
pi = uid("pf")
b_, bi = bot(6, 500, 330, 0.7)
bd(6, [R(6, 350, 440, 300, 440, c="ink", fill="muted", idp=pi), pop(6, pi, 0.0)], b_, [sh(6, [bi, bi + "an", bi + "ar", bi + "sn"], 700, 400, 0.4, 1.2), rot(6, [bi, bi + "an", bi + "ar", bi + "sn"], 360, (500, 300), 0.4, 1.2)],
   BIG(6, 1350, 250, "4米", c="red", d=0.1, s=140), arr(6, 720, 440, 720, 860, c="red", d=0.2))
# 6.5 稳稳落地
bd(6.5, bot(6.5, 960, 700, 1.2)[0], mat(6.5, 860), check(6.5, 1450, 450, d=0.2), T(6.5, 1450, 620, 64, "稳稳落地", c="green", d=0.3), spring(6.5, 500, 850, 300, d=0.1))
# 7 现场侧空翻
b_, bi = bot(7, 960, 600, 1.0)
bd(7, b_, [rot(7, [bi, bi + "an", bi + "ar", bi + "sn"], 180, (960, 520), 0.2, 1.0)], spinarc(7, 960, 520, 300, c="blue", rpm=90), icon(7, "speaker", 300, 400, 160, 0.1, mv="wig"), mat(7))
# 7.5 姿态乱了
b_, bi = bot(7.5, 960, 560, 1.0, mood="o")
bd(7.5, b_, [rot(7.5, [bi, bi + "an", bi + "ar", bi + "sn"], 145, (960, 480), 0.0, 1.2)], BIG(7.5, 1500, 300, "乱了！", c="red", d=0.3, s=120),
   [e for q in range(3) for e in icon(7.5, "question", 400 + 140 * q, 300 + 60 * q, 100, 0.2 + 0.1 * q, c="red", mv="wig")], mat(7.5))
# 8 落地没站稳
b_, bi = bot(8, 900, 640, 1.0, mood="sad", tilt=-35)
bd(8, b_, mat(8), BIG(8, 1450, 300, "没站稳", c="red", d=0.4, s=110), [e for q in range(3) for e in star(8, 700 + 200 * q, 850, 0.5 + 0.1 * q, c="red", r=30)])
# 8.5 小腿脱落滑到垫子
b_, bi = bot(8.5, 600, 640, 1.0, mood="sad", kick=(800, 60, 90, 0.2))
bd(8.5, b_, mat(8.5), crack(8.5, 640, 720, d=0.1), T(8.5, 1400, 400, 60, "右小腿，关节处脱落", c="red", d=0.3), arr(8.5, 800, 820, 1500, 820, c="gold", d=0.4))
# 9 第一个道理
bd(9, BIG(9, 960, 200, "道理一", c="blue", d=0.0, s=110), bot(9, 960, 700, 1.0, d=0.2)[0], spinarc(9, 960, 520, 300, d=0.3), icon(9, "rocket", 400, 600, 150, 0.4, c="red", mv="wig"))
# 9.5 转多少就定了
b_, bi = bot(9.5, 700, 560, 1.0)
bd(9.5, b_, [sh(9.5, [bi, bi + "an", bi + "ar", bi + "sn"], 0, -150, 0.0, 0.5), rot(9.5, [bi, bi + "an", bi + "ar", bi + "sn"], 360, (700, 460), 0.2, 1.4)],
   icon(9.5, "clock", 1400, 450, 200, 0.2, mv="spin"), BIG(9.5, 1400, 760, "定了", c="red", d=0.4, s=110))
# 10 空中没东西可推
b_, bi = bot(10, 960, 520, 1.0, mood="o")
bd(10, b_, [e for q in range(4) for e in icon(10, "cloud", 400 + 380 * q, 230 + 80 * (q % 2), 120, 0.1 * q, c="muted", mv="bob")], cross(10, 1350, 600, d=0.4), T(10, 960, 860, 56, "空中：没东西可推", c="muted", d=0.3))
# 10.5 角动量守恒
bd(10.5, BIG(10.5, 960, 260, "角动量守恒", c="blue", d=0.0, s=110), spinarc(10.5, 500, 620, 160, d=0.2, rpm=80), spinarc(10.5, 1420, 620, 160, d=0.4, rpm=80),
   T(10.5, 960, 620, 90, "=", c="ink", d=0.5), gear(10.5, 960, 860 - 80, 100, 0.3))
# 11 花滑 手一收转得快
p_, pi2 = person(11, 600, 600, 1.4, arms_in=True)
bd(11, p_, spinarc(11, 600, 480, 220, c="red", rpm=160), T(11, 1300, 400, 70, "手一收：快！", c="red", d=0.2), [e for q in range(3) for e in icon(11, "wind", 1150 + 160 * q, 650, 100, 0.3 + 0.1 * q, c="blue", mv="wig")])
# 11.5 手一伸转得慢
p_, pi2 = person(11.5, 1300, 600, 1.4, arms_in=False)
bd(11.5, p_, spinarc(11.5, 1300, 480, 260, c="blue", rpm=25), T(11.5, 550, 400, 70, "手一伸：慢", c="blue", d=0.2), icon(11.5, "clock", 550, 650, 160, 0.3, mv="spin"))
# 12 总的转动
bd(12, BIG(12, 960, 260, "总转动 = 不变", c="red", d=0.0, s=100), spinarc(12, 600, 620, 150, d=0.2), spinarc(12, 1320, 620, 150, d=0.3),
   bar(12, 820, 820, 80, 200, "blue", d=0.4), bar(12, 1020, 820, 80, 200, "blue", d=0.5))
# 12.5 起跳那一刻交了卷
pa = uid("pp")
bd(12.5, [R(12.5, 400, 300, 360, 460, c="ink", fill="muted", idp=pa), P(12.5, "M450,400 L700,400 M450,480 L700,480 M450,560 L650,560", c="ink", w=4, idp=pa), pop(12.5, pa, 0.0),
          sh(12.5, pa, 600, -60, 0.6, 0.9), rot(12.5, pa, 20, (580, 530), 0.6, 0.9)],
   T(12.5, 1350, 300, 72, "交卷！", c="red", d=0.3), bot(12.5, 1400, 760, 0.7, d=0.2)[0])
# 13 差一点点
bd(13, bot(13, 600, 680, 1.0, tilt=5)[0], BIG(13, 1300, 350, "差 1°", c="blue", d=0.2, s=120), arr(13, 1050, 600, 1500, 560, c="blue", d=0.3), mat(13))
# 13.5 歪一大截
bd(13.5, bot(13.5, 900, 640, 1.1, mood="o", tilt=-40)[0], BIG(13.5, 1450, 350, "歪一大截", c="red", d=0.3, s=110), crack(13.5, 1400, 650, d=0.5), mat(13.5))
# 14 半秒
b_, bi = bot(14, 700, 560, 0.9)
bd(14, b_, [rot(14, [bi, bi + "an", bi + "ar", bi + "sn"], 360, (700, 470), 0.0, 1.0)], BIG(14, 1350, 400, "≈ 0.5 秒", c="red", d=0.2, s=130), icon(14, "clock", 1350, 700, 180, 0.3, mv="spin"))
# 14.5 来不及
bd(14.5, icon(14.5, "chip", 600, 450, 240, 0.0, mv="wig"), bubbles(14.5, 600, 650, 4, 0.2), T(14.5, 1300, 400, 72, "纠正？", c="blue", d=0.1), cross(14.5, 1300, 600, d=0.5),
   T(14.5, 1300, 780, 56, "几乎来不及", c="red", d=0.6))
# 15 第二个道理
bd(15, BIG(15, 960, 200, "道理二", c="blue", d=0.0, s=110), fall(15, 960, 300, 760, d=0.3), mat(15, 800), icon(15, "block_force", 500, 600, 180, 0.2), icon(15, "spring", 1450, 600, 180, 0.4, mv="wig"))
# 15.5 力有多大
bd(15.5, bot(15.5, 700, 650, 1.1)[0], [e for q in range(3) for e in arr(15.5, 1100 + 200 * q, 300, 1100 + 200 * q, 700, c="red", d=0.1 + 0.15 * q)], T(15.5, 1300, 820, 64, "力有多大？", c="red", d=0.4))
# 16 半米高落下
bd(16, bot(16, 700, 380, 0.8, d=0.0)[0], arr(16, 1000, 300, 1000, 780, c="blue", d=0.2), BIG(16, 1350, 500, "0.5米", c="blue", d=0.1, s=120), mat(16, 820))
# 16.5 每秒3米
b_, bi = bot(16.5, 600, 380, 0.8)
bd(16.5, b_, [sh(16.5, [bi, bi + "an", bi + "ar", bi + "sn"], 0, 320, 0.0, 0.6)], BIG(16.5, 1300, 420, "3 米/秒", c="red", d=0.3, s=130), mat(16.5, 820),
   icon(16.5, "car", 1300, 680, 160, 0.4, mv="wig"))
# 17 屈膝 30 厘米
bd(17, person(17, 600, 640, 1.3)[0], spring(17, 1000, 820, 360, d=0.1), BIG(17, 1400, 350, "30 厘米", c="blue", d=0.2, s=110), T(17, 1400, 560, 60, "膝盖弯一弯", c="ink", d=0.3), mat(17, 820))
# 17.5 2.7 倍
bd(17.5, bar(17.5, 500, 820, 140, 120, "muted", d=0.0), bar(17.5, 760, 820, 140, 330, "blue", d=0.3), T(17.5, 570, 660, 50, "体重", c="ink", d=0.1),
   BIG(17.5, 1400, 420, "2.7 倍", c="blue", d=0.4, s=140), icon(17.5, "check", 1400, 700, 140, 0.6, c="green"))
# 18 绷直 5 厘米
bd(18, bot(18, 600, 640, 1.2)[0], icon(18, "ruler", 1050, 560, 200, 0.1, mv="wig"), BIG(18, 1450, 420, "5 厘米", c="red", d=0.2, s=110), T(18, 1450, 600, 60, "腿绷直", c="ink", d=0.3), mat(18, 820))
# 18.5 11 倍
bd(18.5, bar(18.5, 400, 820, 120, 60, "muted", d=0.0), bar(18.5, 600, 820, 120, 160, "blue", d=0.2), bar(18.5, 800, 820, 120, 660, "red", d=0.4),
   BIG(18.5, 1400, 400, "11 倍！", c="red", d=0.5, s=150), crack(18.5, 1400, 680, d=0.7))
# 19 70 公斤
bd(19, bot(19, 600, 640, 1.2)[0], BIG(19, 1300, 380, "70 公斤", c="blue", d=0.1, s=110), arr(19, 1300, 500, 1300, 760, c="blue", d=0.3), mat(19, 820))
# 19.5 七百多公斤
bk = uid("bk")
bd(19.5, [R(19.5, 400, 100, 360, 260, c="ink", fill="red", idp=bk), pop(19.5, bk, 0.0), sh(19.5, bk, 0, 330, 0.2, 0.5)],
   bot(19.5, 580, 860 - 10, 0.6, mood="o")[0], BIG(19.5, 1350, 400, "七百多公斤", c="red", d=0.3, s=110), T(19.5, 1350, 600, 56, "压在一条腿上", c="ink", d=0.5))
# 20 人落地屈膝
bd(20, person(20, 600, 640, 1.3)[0], spring(20, 950, 820, 260, d=0.1), spring(20, 1100, 820, 260, d=0.25), icon(20, "check", 1450, 450, 180, 0.4, c="green"), mat(20, 820))
# 20.5 时间拉长，力变小
bd(20.5, icon(20.5, "clock", 500, 420, 220, 0.0, mv="spin"), arr(20.5, 650, 420, 1000, 420, c="blue", d=0.2), BIG(20.5, 1350, 300, "时间 ↑", c="blue", d=0.1, s=100),
   BIG(20.5, 1350, 600, "力 ↓", c="red", d=0.4, s=120), bar(20.5, 500, 820, 120, 150, "red", d=0.5))
# 21 第三个道理
bd(21, BIG(21, 960, 200, "道理三", c="blue", d=0.0, s=110), T(21, 960, 380, 64, "最反直觉", c="red", d=0.2), bot(21, 960, 780, 0.8, mood="o", d=0.3)[0],
   [e for q in range(3) for e in icon(21, "question", 450 + 250 * q, 600, 110, 0.3 + 0.1 * q, c="red", mv="wig")])
# 21.5 不怕压 怕掰
bd(21.5, arr(21.5, 520, 250, 520, 480, c="blue", d=0.0), T(21.5, 520, 760, 64, "压：不怕", c="blue", d=0.2), check(21.5, 520, 620, d=0.3),
   arr(21.5, 1150, 500, 1350, 500, c="red", d=0.4), T(21.5, 1400, 760, 64, "掰：怕！", c="red", d=0.5), crack(21.5, 1420, 500, d=0.7))
# 22 筷子顺着压
c_, ci = chop(22, 700, 520, 500, ang=90)
bd(22, c_, arr(22, 700, 150, 700, 250, c="blue", d=0.1), [sh(22, ci, 0, 20, 0.4, 0.3)], check(22, 1050, 520, d=0.5), T(22, 1400, 500, 64, "顺着压：难断", c="blue", d=0.3))
# 22.5 横着一掰就断
i1, i2 = uid("ch"), uid("ch")
bd(22.5, [R(22.5, 500, 500, 250, 28, c="ink", fill="gold", idp=i1), R(22.5, 750, 500, 250, 28, c="ink", fill="gold", idp=i2), pop(22.5, [i1, i2], 0.0),
          rot(22.5, i1, -30, (750, 514), 0.4, 0.4), rot(22.5, i2, 30, (750, 514), 0.4, 0.4)], arr(22.5, 750, 300, 750, 470, c="red", d=0.1),
   crack(22.5, 750, 560, d=0.6), BIG(22.5, 1400, 500, "啪！", c="red", d=0.6, s=150))
# 23 姿态一歪 力从侧面来
bd(23, bot(23, 700, 640, 1.1, tilt=-30)[0], arr(23, 1300, 760, 860, 760, c="red", d=0.2), T(23, 1400, 400, 60, "力从侧面来", c="red", d=0.3), mat(23, 820), T(23, 1400, 250, 44, "推测", c="muted", d=0.0))
# 23.5 被横掰的筷子
c_, ci = chop(23.5, 650, 520, 420, ang=90, c="gold")
bd(23.5, c_, [rot(23.5, ci, 120, (650, 700), 0.4, 0.6)], arr(23.5, 400, 400, 600, 400, c="red", d=0.2), T(23.5, 1350, 400, 64, "腿 = 筷子", c="gold", d=0.3), crack(23.5, 650, 650, d=0.7))
# 24 最先吃不住
bd(24, bot(24, 700, 640, 1.2, mood="sad")[0], crack(24, 770, 700, d=0.1), T(24, 1400, 400, 64, "最先吃不住…", c="red", d=0.2), arr(24, 1200, 500, 850, 700, c="red", d=0.3))
# 24.5 关节接缝
bd(24.5, gear(24.5, 700, 480, 260, 0.0, rpm=40), gear(24.5, 900, 640, 160, 0.1, rpm=-60), crack(24.5, 800, 560, d=0.4), BIG(24.5, 1400, 480, "接缝", c="red", d=0.3, s=130))
# 25 360 牛米
bd(25, gear(25, 560, 480, 260, 0.0, rpm=90), BIG(25, 1300, 380, "360 牛米", c="blue", d=0.2, s=120), spinarc(25, 560, 480, 200, c="red", d=0.1), T(25, 1300, 560, 50, "据报道", c="muted", d=0.3))
# 25.5 踢开车门
b_, bi = bot(25.5, 600, 640, 1.1)
car = uid("car")
bd(25.5, b_, [rot(25.5, bi + "sn", -60, (600 + 38, 640 + 88), 0.2, 0.3)], [{"t": "icon", "at": 25.5, "id": car, "name": "car", "x": 1250, "y": 600, "size": 340, "c": "ink"}, pop(25.5, car, 0.0),
   sh(25.5, car, 150, 0, 0.5, 0.4), wig(25.5, car, (1250, 700), 4, 3)], BIG(25.5, 1300, 260, "砰！", c="red", d=0.5, s=120))
# 26 力气大 ≠ 扛得住
bd(26, BIG(26, 960, 260, "力气大 ≠ 扛得住", c="red", d=0.0, s=90), icon(26, "block_force", 550, 600, 220, 0.2, mv="bob"), cross(26, 960, 600, d=0.4), icon(26, "spring", 1350, 600, 200, 0.3, mv="wig"))
# 26.5 齿轮螺栓都有极限
bd(26.5, gear(26.5, 500, 500, 220, 0.0, rpm=60), bolt(26.5, 1000, 500, d=0.2), crack(26.5, 1000, 520, d=0.6), icon(26.5, "thermometer", 1450, 500, 200, 0.3, c="red", mv="wig"),
   T(26.5, 960, 780, 60, "都有极限", c="ink", d=0.5))
# 27 保险丝
fu = uid("fu")
bd(27, [R(27, 600, 440, 700, 120, c="ink", fill="muted", idp=fu), P(27, "M660,500 Q760,440 860,500 Q960,560 1060,500 Q1160,440 1240,500", c="red", w=6, idp=fu), pop(27, fu, 0.0), pulse(27, fu, 0.4)],
   T(27, 950, 300, 70, "保险丝", c="red", d=0.1), icon(27, "flame", 400, 500, 160, 0.3, c="red", mv="wig"), icon(27, "check", 1500, 500, 160, 0.5, c="green"))
# 27.5 先坏便宜的
bd(27.5, bolt(27.5, 500, 450, d=0.0), crack(27.5, 500, 470, d=0.3), T(27.5, 500, 640, 56, "便宜零件：先坏", c="red", d=0.3), gear(27.5, 1300, 450, 240, 0.2, rpm=50),
   T(27.5, 1300, 680, 56, "贵的：保住", c="green", d=0.5), check(27.5, 1300, 820 - 40, d=0.6))
# 28 故障还是保护设计
bd(28, bot(28, 960, 640, 1.0, legless=True)[0], T(28, 450, 380, 72, "故障？", c="red", d=0.1), T(28, 1470, 380, 72, "保护？", c="green", d=0.3),
   icon(28, "question", 960, 220, 140, 0.4, c="ink", mv="wig"), arr(28, 800, 420, 600, 420, c="red", d=0.2), arr(28, 1120, 420, 1320, 420, c="green", d=0.4))
# 28.5 还没回应
bd(28.5, icon(28.5, "phone", 600, 500, 260, 0.0, mv="wig"), sound(28.5, 760, 450, 1.0, d=0.2), T(28.5, 1300, 400, 64, "宇树：", c="blue", d=0.2), T(28.5, 1300, 560, 90, "……", c="muted", d=0.5),
   icon(28.5, "clock", 1300, 760, 120, 0.4, mv="spin"))
# 29 友情提示
bd(29, T(29, 960, 200, 70, "友情提示", c="red", d=0.0), icon(29, "magnifier", 600, 520, 260, 0.1, mv="wig"), BIG(29, 1300, 520, "官方原因：未公布", c="ink", d=0.3, s=64),
   [e for q in range(3) for e in icon(29, "question", 1050 + 200 * q, 720, 90, 0.4 + 0.1 * q, c="red", mv="wig")])
# 29.5 物理推测
bd(29.5, icon(29.5, "atom", 600, 480, 260, 0.0, mv="spin"), BIG(29.5, 1300, 420, "物理推测", c="blue", d=0.2, s=110), icon(29.5, "flask", 1300, 680, 160, 0.4, mv="wig"))
# 30 摔一跤不丢人
bd(30, bot(30, 760, 660, 1.0, mood="happy", tilt=70)[0], mat(30, 820), T(30, 1400, 380, 64, "摔一跤，不丢人", c="blue", d=0.2), [e for q in range(3) for e in star(30, 700 + 150 * q, 380, 0.3 + 0.1 * q, r=28)])
# 30.5 工程师学到东西
bd(30.5, icon(30.5, "computer", 600, 500, 260, 0.0, mv="bob"), arr(30.5, 800, 500, 1100, 500, c="green", d=0.2), icon(30.5, "chip", 1300, 500, 200, 0.3, mv="spin"),
   bar(30.5, 1500, 760, 80, 260, "green", d=0.4), T(30.5, 960, 800, 56, "每一跤都是数据", c="green", d=0.5))
# 31 学走路的小孩
p_, pi2 = person(31, 700, 680, 0.8)
bd(31, p_, [rot(31, [pi2, pi2 + "ar"], 60, (700, 790), 0.4, 0.5)], mat(31, 790, 400, 1100), T(31, 1350, 400, 64, "学走路的小孩", c="blue", d=0.1), icon(31, "dinosaur", 1450, 650, 160, 0.3, mv="wig"))
# 31.5 一小时十几次
bd(31.5, icon(31.5, "clock", 500, 480, 240, 0.0, mv="spin"), BIG(31.5, 1200, 420, "1 小时 ≈ 17 次", c="red", d=0.2, s=100),
   [e for q in range(5) for e in check(31.5, 900 + 140 * q, 650, c="red", d=0.3 + 0.1 * q)], T(31.5, 1200, 800, 44, "Adolph 等 2012", c="muted", d=0.4))
# 32 别笑小翻
bd(32, bot(32, 760, 660, 1.4, mood="sad", legless=True)[0], T(32, 1400, 400, 70, "别笑我…", c="blue", d=0.2), icon(32, "water", 860, 380, 80, 0.4, c="blue"), mat(32, 860))
# 32.5 交学费
coins = []
for q in range(4):
    ci = uid("cn")
    coins += [O(32.5, 1100 + 120 * q, 200, 40, c="ink", fill="gold", idp=ci), pop(32.5, ci, 0.1 * q), sh(32.5, ci, -400 + 40 * q, 450, 0.2 + 0.15 * q, 0.6)]
bd(32.5, coins, bot(32.5, 600, 700, 1.0)[0], BIG(32.5, 1350, 600, "交学费", c="gold", d=0.5, s=120))
# 33 屈膝 站稳
bd(33, bot(33, 700, 650, 1.2)[0], spring(33, 1100, 820, 260, d=0.1), check(33, 1400, 400, d=0.2), T(33, 1450, 560, 60, "屈膝、站稳", c="green", d=0.3), mat(33, 820))
# 33.5 腿别先走
b_, bi = bot(33.5, 960, 600, 1.2)
bd(33.5, b_, [rot(33.5, [bi, bi + "an", bi + "ar", bi + "sn"], 360, (960, 500), 0.0, 1.0)], spinarc(33.5, 960, 480, 330, c="gold", d=0.0),
   BIG(33.5, 960, 150, "腿，别先走！", c="red", d=0.5, s=100), mat(33.5, 820))

# 100 猫从空中掉下
ct = uid("cat")
bd(100, [O(100, 700, 560, 90, c="ink", fill="muted", idp=ct), P(100, "M640,490 L650,430 L690,480 M760,490 L750,430 L710,480", c="ink", w=6, idp=ct),
         O(100, 670, 550, 9, c="ink", fill="ink", idp=ct), O(100, 730, 550, 9, c="ink", fill="ink", idp=ct), pop(100, ct, 0.0), rot(100, ct, 360, (700, 560), 0.3, 0.8), bob(100, ct, 8, 1.2)],
   T(100, 1350, 300, 64, "再烧一点", c="red", d=0.1), mat(100, 860, 400, 1000), icon(100, "question", 1350, 560, 180, 0.3, c="red", mv="wig"))
# 100.5 半空翻个身
ct = uid("cat")
bd(100.5, [O(100.5, 960, 300, 90, c="ink", fill="muted", idp=ct), P(100.5, "M900,230 L910,170 L950,220 M1020,230 L1010,170 L970,220", c="ink", w=6, idp=ct),
           O(100.5, 930, 290, 9, c="ink", fill="ink", idp=ct), O(100.5, 990, 290, 9, c="ink", fill="ink", idp=ct), pop(100.5, ct, 0.0),
           rot(100.5, ct, 360, (960, 300), 0.1, 0.8), sh(100.5, ct, 0, 380, 0.2, 1.0)],
   spinarc(100.5, 960, 450, 260, c="blue", d=0.1), check(100.5, 1500, 700, d=0.8), mat(100.5, 860, 600, 1320))
# 101 先扭前半身、再扭后半身
f1, f2 = uid("cf"), uid("cb")
bd(101, [R(101, 560, 420, 400, 160, c="ink", fill="muted", idp=f1), R(101, 960, 420, 400, 160, c="ink", fill="blue", idp=f2), pop(101, [f1, f2], 0.0),
         rot(101, f1, 90, (760, 500), 0.2, 0.5), rot(101, f2, -40, (1160, 500), 0.2, 0.5), rot(101, f2, 50, (1160, 500), 0.8, 0.5)],
   T(101, 760, 230, 56, "前半身", c="ink", d=0.1), T(101, 1160, 230, 56, "后半身", c="blue", d=0.3), spinarc(101, 760, 500, 230, c="red", d=0.2, rpm=70))
# 101.5 总转动是零
bd(101.5, BIG(101.5, 960, 300, "总转动 = 0", c="blue", d=0.0, s=110), spinarc(101.5, 600, 650, 150, c="red", d=0.2, rpm=80), spinarc(101.5, 1320, 650, 150, c="blue", d=0.3, rpm=-80),
   T(101.5, 960, 650, 80, "+", c="ink", d=0.4), check(101.5, 960, 860 - 60, d=0.6))
# 102 机器人学这招
b_, bi = bot(102, 700, 600, 1.1)
bd(102, b_, [rot(102, bi + "ar", 40, (700, 490), 0.2, 0.5)], icon(102, "chip", 1300, 420, 200, 0.1, mv="spin"), T(102, 1300, 680, 60, "学这招", c="blue", d=0.3), mat(102, 820))
# 102.5 半秒太紧
bd(102.5, icon(102.5, "clock", 600, 480, 280, 0.0, mv="spin"), BIG(102.5, 1300, 400, "0.5 秒", c="red", d=0.2, s=120), T(102.5, 1300, 620, 64, "太紧了！", c="red", d=0.4),
   bot(102.5, 1300, 860 - 20, 0.5, mood="o", d=0.3)[0])
# 103 人跑步
p_, pi2 = person(103, 700, 640, 1.2)
bd(103, p_, [sh(103, [pi2, pi2 + "ar"], 400, 0, 0.0, 1.6)], [e for q in range(3) for e in icon(103, "wind", 400 + 120 * q, 560, 90, 0.1 * q, c="blue", mv="wig")], mat(103, 820),
   T(103, 1400, 300, 64, "跑步每一步", c="ink", d=0.2))
# 103.5 两三倍体重
bd(103.5, bar(103.5, 500, 820, 140, 120, "muted", d=0.0), bar(103.5, 760, 820, 140, 300, "blue", d=0.3), T(103.5, 570, 660, 50, "体重", c="ink", d=0.1),
   BIG(103.5, 1400, 420, "2–3 倍", c="blue", d=0.4, s=130), spring(103.5, 1400, 820, 200, d=0.5))
# 104 体操运动员
p_, pi2 = person(104, 960, 600, 1.0)
bd(104, p_, [rot(104, [pi2, pi2 + "ar"], 360, (960, 560), 0.0, 1.0), sh(104, [pi2, pi2 + "ar"], 0, 120, 0.9, 0.4)], spinarc(104, 960, 500, 280, c="gold", d=0.0, rpm=90),
   T(104, 1500, 300, 60, "体操落地", c="ink", d=0.2), mat(104, 860))
# 104.5 膝盖脚踝髋部当弹簧
bd(104.5, spring(104.5, 600, 820, 300, d=0.0), spring(104.5, 960, 820, 300, d=0.2), spring(104.5, 1320, 820, 300, d=0.4),
   T(104.5, 600, 420, 56, "髋", c="blue", d=0.1), T(104.5, 960, 420, 56, "膝", c="blue", d=0.3), T(104.5, 1320, 420, 56, "踝", c="blue", d=0.5), T(104.5, 960, 250, 64, "三根弹簧", c="ink", d=0.6))
# 105 电机就是肌肉
bd(105, gear(105, 600, 480, 240, 0.0, rpm=70), arr(105, 780, 480, 1100, 480, c="ink", d=0.2), icon(105, "battery", 1350, 480, 200, 0.3, mv="wig"), T(105, 960, 780, 64, "电机 = 肌肉", c="blue", d=0.3))
# 105.5 像弹簧往回收
b_, bi = bot(105.5, 700, 560, 1.0)
bd(105.5, b_, [sh(105.5, [bi, bi + "an", bi + "ar", bi + "sn"], 0, 80, 0.2, 0.4), sh(105.5, [bi, bi + "an", bi + "ar", bi + "sn"], 0, -80, 0.7, 0.4)], spring(105.5, 1300, 820, 300, d=0.2),
   check(105.5, 1550, 400, d=0.6), mat(105.5, 820))
# 106 控制没算准
bd(106, icon(106, "chip", 600, 480, 260, 0.0, mv="wig"), crack(106, 600, 480, d=0.3), T(106, 1300, 400, 64, "没算准？", c="red", d=0.2), icon(106, "question", 1300, 640, 160, 0.4, c="red", mv="wig"))
# 106.5 电机硬顶
bd(106.5, gear(106.5, 600, 480, 260, 0.0, rpm=200), arr(106.5, 800, 480, 1150, 480, c="red", d=0.2), BIG(106.5, 1400, 480, "硬顶！", c="red", d=0.3, s=120), crack(106.5, 1400, 680, d=0.6))

# 按讲稿顺序把画板时间换成句子序号
_POS = {k: n for n, k in enumerate(ORDER)}
for b in B:
    for e in b:
        k = int(e["at"]) if e["at"] < 100 else int(e["at"])
        e["at"] = _POS[k] + (e["at"] - k)
S = [SX[k] if k >= 100 else S[k] for k in ORDER]

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"宇树H2-X": "宇树的新机器人", "H2-X": "这台机器人", "10月22日": "十月二十二日", "1米82": "一米八二", "2.7倍": "二点七倍",
                                       "11倍": "十一倍", "360牛米": "三百六十牛米", "70公斤": "七十公斤", "4米": "四米", "30厘米": "三十厘米", "5厘米": "五厘米", "3米": "三米"})
