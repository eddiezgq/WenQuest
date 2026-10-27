"""每日科普 2026-10-27（中文）：《手机凭啥知道你在摇它？》
热点：新浪科技热点小时报 2026-10-27 10 时第 11 条“苹果出手整治摇一摇跳转广告！iOS 27.2 可禁止运动传感器权限：国行专属”。
事实出处：
- 凤凰网科技/IT之家 2026-09-23 https://tech.ifeng.com/c/8weNnsGS71y ：iOS 27.2 Beta 2，设置-隐私与安全-运动与健身，
  “Restrict Motion Data”，选中的 App 读不到加速度计、陀螺仪，个别 App 可能闪退；只在 App Store 登录中国大陆账号时出现；苹果未说明用途。
- 快科技/差评 2026-09-25 https://news.mydrivers.com/1/1153/1153888.htm ：仍是测试版；App Store 审核指南 4.10 不许拿陀螺仪等内置硬件功能变现；
  2023 年工信部点名摇一摇灵敏度过高；小米、华为、vivo、OPPO 早有传感器权限开关。
- 凤凰网 https://tech.ifeng.com/c/8UgSVK4KpA5 ：T/TAF 078.7—2022（电信终端产业协会，2022 年 11 月，团体标准、自愿采用）：
  加速度 ≥ 15 m/s²、转动角度 ≥ 35°、或操作时间 ≥ 3 秒。
- 课本知识：MEMS 加速度计（硅质量块 + 硅弹簧 + 梳齿电容）、MEMS 陀螺仪（振动质量块 + 科里奥利力）、静止时读到重力 9.8 m/s²；
  机器人、无人机、平衡车用同类惯性测量单元（IMU）保持平衡，一秒读几百到上千次（典型值）。
比喻：公交车起步人往后仰 = 质量块的惯性；转椅……不用。角色：小机（会动的手机）。梗：“怪惯性”。
推测/估算：“走路一颠、坐车一晃都可能被当成摇”是按门槛调低时的推理，片中说“可能”。
    python3 make.py <kokoro 模型目录> | --boards-only | --fake   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bob, bubbles, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("你只是把手机拿起来，|屏幕就跳进了购物App。", "You just pick up your phone, | and it jumps into a shopping app."),
 ("罪魁祸首：|摇一摇广告。", "The culprit: | shake-to-open ads."),
 ("这回苹果出手了：|iOS 27.2测试版里，多了一个国行专属开关。", "Now Apple steps in: | a China-only switch in the iOS 27.2 beta."),
 ("在运动与健身里，|可以不让某个App读运动传感器。", "Under Motion & Fitness, | you can block an app from the motion sensors."),
 ("今天的烧脑问题：|手机凭什么知道你在摇它？", "Today's brain-teaser: | how does a phone know you shook it?"),
 ("手机里藏着一杆比芝麻还小的弹簧秤，|叫加速度计。", "Inside hides a spring scale smaller than a sesame seed: | the accelerometer."),
 ("一小块硅做的质量块，|挂在几根细细的硅弹簧上。", "A tiny block of silicon | hangs on thin silicon springs."),
 ("手机往右一冲，|质量块因为惯性，往左一躲。", "The phone jerks right; | inertia makes the block lag to the left."),
 ("就像公交车一起步，|你会往后一仰。", "Like when a bus pulls away | and you lean back."),
 ("质量块旁边有一排梳子一样的电极，|它一躲，缝隙就变了。", "Comb-shaped electrodes sit beside it. | When it moves, the gaps change."),
 ("缝隙一变，电容就变，|芯片就算出：加速了多少。", "Gaps change, capacitance changes, | and the chip computes the acceleration."),
 ("反转一：|你一动不动，它也有读数。", "Twist one: | even sitting still, it reads something."),
 ("读多少？每秒平方9.8米，|那是地球在拽它。", "9.8 meters per second squared: | that's Earth pulling on it."),
 ("所以手机知道哪边是下，|你一横过来，屏幕就跟着转。", "So the phone knows which way is down, | and the screen turns when you do."),
 ("可光有加速度，|分不清你是在摇，还是在转。", "But acceleration alone | can't tell a shake from a turn."),
 ("所以还有第二个小家伙：|陀螺仪。", "So there's a second little guy: | the gyroscope."),
 ("里面的小质量块一直来回振动，|手机一转，它就被往旁边推一把。", "Its tiny block vibrates back and forth nonstop. | Turn the phone, and it gets pushed sideways."),
 ("这一推叫科里奥利力，|推得越狠，说明转得越快。", "That push is the Coriolis force. | The harder the push, the faster the turn."),
 ("那多大才算“摇”？|2022年，一个行业标准给了数。", "So how hard counts as a shake? | A 2022 industry standard set numbers."),
 ("加速度至少每秒平方15米，|转过至少35度，或者摇满3秒。", "At least 15 meters per second squared, | at least 35 degrees of turn, or 3 seconds of shaking."),
 ("15，大约是一点五倍重力，|正常拿手机，碰不到。", "15 is about one and a half g. | Normal handling shouldn't reach it."),
 ("反转二：|这只是团体标准，自愿执行，不强制。", "Twist two: | it's a voluntary standard. Nothing forces it."),
 ("2023年，工信部就点过名：|有的摇一摇，灵敏得过头。", "In 2023, China's tech ministry called out | shake prompts that were far too sensitive."),
 ("门槛一调低，走路一颠、|坐车一晃，都可能被当成“摇”。", "Set the bar too low, and a step | or a bumpy ride might count as a shake."),
 ("而且苹果的审核规则本来就不许|拿陀螺仪这类硬件功能来变现。", "And Apple's own rules already forbid | making money off hardware like the gyroscope."),
 ("反转三，最妙的一个：|这套传感器，正是机器人的平衡感。", "Twist three, the best one: | these sensors are a robot's sense of balance."),
 ("人形机器人、无人机、平衡车，|都靠它知道自己歪没歪。", "Humanoid robots, drones, self-balancing scooters | all use them to know if they're tilting."),
 ("一秒读几百上千次，|一歪就马上掰回来。", "Hundreds to thousands of readings a second, | correcting every wobble."),
 ("你的手机里，|住着一个机器人的小脑。", "Inside your phone | lives a robot's sense of balance."),
 ("友情提示：这个开关还在测试版里，|叫什么、放哪儿，正式版都可能变。", "Friendly fine print: this switch is still in beta. | Its name and place may change."),
 ("关掉以后，|个别App可能会闪退。", "Block an app, | and it may crash."),
 ("安卓的小米、华为、vivo、OPPO，|早就有类似的权限开关。", "Android makers like Xiaomi, Huawei, vivo and OPPO | already have similar switches."),
 ("手机知道你在摇，|是因为里面有一杆会晃的小秤。", "Your phone knows you shook it | because a tiny scale inside wobbled."),
 ("下次再被摇进广告，|别怪手，怪惯性。", "So next time an ad ambushes you, | don't blame your hand. Blame inertia."),
]
TITLE = {"zh": "手机凭啥知道你在摇它？", "en": "How Does Your Phone Know You Shook It?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20) + star(a, 1810, 820, 0.5, r=16)
    B.append(E)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def xiaoji(a, x, y, k=1.0, d=0.0, mood="happy", shake=False, c="blue"):
    """小机：一部会动的手机，圆角机身、屏幕上一张脸；平时上下晃，shake=True 时左右猛摇。"""
    i = uid("xj")
    w, h = 150 * k, 260 * k
    m = {"happy": f"M{x - 30 * k},{y + 30 * k} Q{x},{y + 60 * k} {x + 30 * k},{y + 30 * k}",
         "o": f"M{x - 12 * k},{y + 40 * k} a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0",
         "sad": f"M{x - 30 * k},{y + 55 * k} Q{x},{y + 25 * k} {x + 30 * k},{y + 55 * k}"}[mood]
    E = [R(a, x - w / 2, y - h / 2, w, h, c="ink", fill=c, idp=i),
         R(a, x - w / 2 + 14 * k, y - h / 2 + 24 * k, w - 28 * k, h - 60 * k, c="ink", fill="paper", idp=i, sw=3),
         O(a, x - 28 * k, y - 20 * k, 10 * k, c="ink", fill="ink", idp=i), O(a, x + 28 * k, y - 20 * k, 10 * k, c="ink", fill="ink", idp=i),
         P(a, m, c="ink", w=5, idp=i), O(a, x, y + h / 2 - 18 * k, 8 * k, c="ink", idp=i, sw=3), pop(a, i, d)]
    E.append(wig(a, i, (x, y + h / 2), 14 if shake else 3, 4.0 if shake else 1.0))
    E.append(bob(a, i, 6 * k, 1.3))
    return E, i


def adbox(a, x, y, d=0.0, s=1.0):
    """红色广告弹窗，蹦出来后一直抖。"""
    i = uid("ad")
    E = [R(a, x - 150 * s, y - 90 * s, 300 * s, 180 * s, c="red", fill="paper", idp=i, sw=7), pop(a, i, d), wig(a, i, (x, y), 4, 3.0)]
    E += T(a, x, y + 20 * s, int(70 * s), "广告", c="red", d=d + 0.1)
    return E


def mass(a, x, y, d=0.0, dx=0, dt=0.3, comb=False):
    """加速度计：方框外壳、中间质量块、左右锯齿弹簧；dx≠0 时质量块在 dt 秒挪 dx。"""
    f, mb, sl, sr = uid("fr"), uid("mb"), uid("spl"), uid("spr")
    zz = lambda x0, x1: f"M{x0},{y} " + " ".join(f"L{x0 + (x1 - x0) * (q + .5) / 8},{y + (24 if q % 2 else -24)}" for q in range(8)) + f" L{x1},{y}"
    E = [R(a, x - 360, y - 160, 720, 320, c="ink", idp=f, sw=6), pop(a, f, d),
         R(a, x - 90, y - 90, 180, 180, c="ink", fill="blue", idp=mb), pop(a, mb, d + 0.15),
         P(a, zz(x - 360, x - 90), c="ink", w=5, idp=sl), P(a, zz(x + 90, x + 360), c="ink", w=5, idp=sr), pop(a, [sl, sr], d + 0.2),
         wig(a, sl, (x - 360, y), 1.5, 3.0), wig(a, sr, (x + 360, y), 1.5, 3.0), bob(a, mb, 4, 3.0)]
    if dx:
        E.append(sh(a, mb, dx, 0, dt, 0.4))
    if comb:
        for q in range(4):
            cb = uid("cb")
            E += [P(a, f"M{x - 70 + 45 * q},{y + 90} L{x - 70 + 45 * q},{y + 150}", c="red", w=5, idp=cb), pop(a, cb, d + 0.3 + 0.08 * q), wig(a, cb, (x - 70 + 45 * q, y + 150), 2, 2)]
    return E


def tilt(a, x, y, d=0.0, ang=25):
    """一根杆一歪一回正（平衡）。"""
    i = uid("tl")
    return [P(a, f"M{x},{y} L{x},{y - 240} M{x - 60},{y} L{x + 60},{y}", c="ink", w=7, idp=i), pop(a, i, d),
            rot(a, i, ang, (x, y), d + 0.3, 0.5), rot(a, i, 0, (x, y), d + 1.0, 0.5), wig(a, i, (x, y), 4, 1.5)]


def gyro_(a, x, y, d=0.0):
    i = uid("gy")
    return [O(a, x, y, 140, c="ink", fill="gold", idp=i), P(a, f"M{x - 140},{y} L{x + 140},{y} M{x},{y - 140} L{x},{y + 140}", c="ink", w=5, idp=i), pop(a, i, d), spin(a, i, (x, y), 90)]


# 0 拿起手机
p, pid = xiaoji(0, 700, 500, 1.3)
bd(0, p, [sh(0, pid, 0, -120, 0.2, 0.5)], arr(0, 1000, 420, 1200, 420, c="red", d=0.6), adbox(0, 1450, 420, 0.8), ic(0, "question", 300, 300, 120, 0.3, mv="wig", c="red"))
p, pid = xiaoji(0.5, 600, 480, 1.3, mood="o")
bd(0.5, p, [e for q in range(3) for e in ic(0.5, "map_pin", 1100 + 220 * q, 380 + 80 * (q % 2), 120, 0.15 * q, mv="bob", c="red")], BIG(0.5, 1320, 720, "购物App", c="red", d=0.4, s=110))
# 1 罪魁祸首
p, pid = xiaoji(1, 520, 480, 1.2, shake=True)
bd(1, p, ic(1, "magnifier", 1050, 420, 220, 0.1, mv="wig"), BIG(1, 1450, 300, "罪魁祸首", c="ink", d=0.3, s=110))
p, pid = xiaoji(1.5, 500, 480, 1.2, shake=True, mood="o")
bd(1.5, p, adbox(1.5, 1100, 380, 0.1), adbox(1.5, 1500, 600, 0.3, 0.8), BIG(1.5, 1150, 760, "摇一摇", c="red", d=0.2, s=150))
# 2 苹果出手
p, pid = xiaoji(2, 520, 500, 1.2)
bd(2, p, ic(2, "block_force", 1100, 420, 220, 0.2, mv="wig", c="red"), adbox(2, 1500, 400, 0.0, 0.8), cross(2, 1500, 400, d=0.6), cross(2, 1500, 400, d=0.75))
sw = uid("sw")
bd(2.5, [R(2.5, 760, 360, 400, 180, c="ink", fill="paper", idp=sw, sw=6), pop(2.5, sw, 0.0)],
   [O(2.5, 860, 450, 70, c="ink", fill="green", idp=(kn := uid("kn"))), pop(2.5, kn, 0.1), sh(2.5, kn, 200, 0, 0.5, 0.4), pulse(2.5, kn, 1.0)],
   BIG(2.5, 960, 700, "iOS 27.2 测试版", c="blue", d=0.3, s=100), ic(2.5, "phone", 350, 450, 200, 0.2, mv="wig"), ic(2.5, "map_pin", 1550, 450, 160, 0.4, c="red"), T(2.5, 1550, 620, 56, "国行专属", c="red", d=0.6))
# 3 运动与健身
bd(3, ic(3, "gear", 500, 420, 200, 0.0, mv="spin"), arr(3, 650, 420, 850, 420, d=0.3), T(3, 1150, 380, 64, "隐私与安全", c="ink", d=0.3), arr(3, 1150, 450, 1150, 560, d=0.5), T(3, 1150, 640, 64, "运动与健身", c="blue", d=0.7), ic(3, "phone", 1650, 480, 160, 0.4, mv="wig"))
bd(3.5, mass(3.5, 700, 480), cross(3.5, 700, 480, d=0.5), ic(3.5, "signal", 1300, 380, 160, 0.2, mv="wig", c="red"), cross(3.5, 1300, 380, d=0.6), T(3.5, 1350, 650, 60, "读不到运动传感器", c="red", d=0.4))
# 4 烧脑问题
p, pid = xiaoji(4, 960, 500, 1.4, shake=True)
bd(4, p, ic(4, "question", 500, 400, 200, 0.2, mv="wig", c="red"), ic(4, "question", 1420, 400, 200, 0.4, mv="wig", c="red"), BIG(4, 960, 160, "烧脑问题", c="ink", d=0.1, s=90))
p, pid = xiaoji(4.5, 500, 500, 1.3, shake=True, mood="o")
bd(4.5, p, BIG(4.5, 1250, 420, "它怎么知道", c="ink", d=0.1, s=110), BIG(4.5, 1250, 600, "你在摇？", c="red", d=0.4, s=130), ic(4.5, "eye", 1700, 250, 120, 0.3, mv="wig"))
# 5 弹簧秤
ss = uid("ss")
bd(5, [O(5, 500, 450, 16, c="ink", fill="gold", idp=ss), pop(5, ss, 0.1), pulse(5, ss, 0.6)], T(5, 500, 560, 56, "芝麻", c="ink", d=0.3),
   ic(5, "spring", 1100, 420, 260, 0.2, mv="bob"), ic(5, "magnifier", 800, 450, 160, 0.4, mv="wig"), BIG(5, 1500, 420, "< 1 mm", c="red", d=0.6, s=110))
bd(5.5, mass(5.5, 800, 450), BIG(5.5, 1500, 700, "加速度计", c="blue", d=0.4, s=110), ic(5.5, "chip", 1550, 300, 150, 0.2, mv="spin"))
# 6 质量块 + 弹簧
bd(6, mass(6, 960, 450), T(6, 960, 230, 60, "硅质量块", c="blue", d=0.4), arr(6, 960, 260, 960, 340, c="blue", d=0.5))
bd(6.5, mass(6.5, 960, 450), T(6.5, 680, 680, 56, "硅弹簧", c="ink", d=0.3), T(6.5, 1240, 680, 56, "硅弹簧", c="ink", d=0.5), arr(6.5, 680, 640, 720, 500, c="red", d=0.4), arr(6.5, 1240, 640, 1200, 500, c="red", d=0.6))
# 7 手机冲 / 质量块躲
p, pid = xiaoji(7, 400, 480, 1.0)
bd(7, p, [sh(7, pid, 300, 0, 0.3, 0.4)], arr(7, 800, 480, 1300, 480, c="red", d=0.3, dur=0.4), BIG(7, 1500, 480, "→", c="red", d=0.4, s=150), ic(7, "wind", 1550, 250, 140, 0.5, mv="wig"))
bd(7.5, mass(7.5, 960, 450, dx=-120, dt=0.3), arr(7.5, 860, 700, 600, 700, c="red", d=0.4), BIG(7.5, 960, 200, "惯性", c="red", d=0.5, s=110))
# 8 公交车
bus = uid("bus")
bd(8, [R(8, 300, 330, 700, 300, c="ink", fill="gold", idp=bus), pop(8, bus, 0.0), sh(8, bus, 300, 0, 0.4, 1.0)],
   ic(8, "wheel", 450, 650, 120, 0.1, mv="spin"), ic(8, "wheel", 850, 650, 120, 0.1, mv="spin"), arr(8, 1100, 480, 1500, 480, c="red", d=0.3))
st = uid("st")
bd(8.5, [P(8.5, "M900,300 L900,600 L840,750 M900,600 L960,750 M900,380 L800,470 M900,380 L1000,470", c="ink", w=8, idp=st), O(8.5, 900, 240, 60, c="ink", fill="paper", idp=st),
         pop(8.5, st, 0.0), rot(8.5, st, -22, (900, 700), 0.3, 0.4), rot(8.5, st, 0, (900, 700), 1.1, 0.5)],
   arr(8.5, 1300, 450, 1650, 450, c="red", d=0.2), T(8.5, 1450, 380, 56, "车往前", c="red", d=0.2), arr(8.5, 600, 450, 300, 450, c="blue", d=0.4), T(8.5, 450, 380, 56, "你往后", c="blue", d=0.4))
# 9 梳齿电极
bd(9, mass(9, 960, 400, comb=True), T(9, 960, 680, 60, "梳齿电极", c="red", d=0.6), ic(9, "magnifier", 1550, 650, 140, 0.3, mv="wig"))
bd(9.5, mass(9.5, 960, 400, dx=-60, dt=0.2, comb=True), arr(9.5, 400, 700, 600, 600, d=0.4), T(9.5, 400, 760, 56, "缝隙变了", c="red", d=0.5))
# 10 电容
bd(10, mass(10, 700, 420, dx=-50, dt=0.2, comb=True), ic(10, "battery", 1400, 300, 160, 0.3, mv="wig"), BIG(10, 1400, 560, "电容变了", c="blue", d=0.5, s=100))
bd(10.5, ic(10.5, "chip", 600, 450, 240, 0.0, mv="spin"), arr(10.5, 780, 450, 1000, 450, d=0.2), BIG(10.5, 1350, 450, "a = ?", c="red", d=0.4, s=150), ic(10.5, "sine", 1350, 700, 160, 0.6, mv="wig", c="blue"))
# 11 反转一
p, pid = xiaoji(11, 960, 520, 1.3)
bd(11, p, BIG(11, 960, 180, "反转一", c="red", d=0.0, s=120), ic(11, "question", 1450, 500, 160, 0.3, mv="wig", c="red"), ic(11, "clock", 450, 500, 160, 0.4, mv="spin"))
p, pid = xiaoji(11.5, 500, 500, 1.2)
bd(11.5, p, mass(11.5, 1250, 450), [sh(11.5, [], 0, 0, 0, 0.1)][:0], BIG(11.5, 1250, 750, "读数 ≠ 0", c="red", d=0.5, s=100))
# 12 9.8
bd(12, BIG(12, 960, 420, "9.8", c="red", d=0.1, s=220), T(12, 960, 620, 60, "米 / 秒²", c="ink", d=0.3), ic(12, "spring", 450, 450, 200, 0.2, mv="bob"), arr(12, 1450, 300, 1450, 600, c="blue", d=0.5))
bd(12.5, ic(12.5, "globe", 960, 650, 300, 0.0, mv="spin"), mass(12.5, 960, 230)[:0], arr(12.5, 960, 200, 960, 450, c="red", d=0.3), ic(12.5, "phone", 960, 160, 110, 0.1, mv="wig"), T(12.5, 1450, 450, 64, "地球在拽", c="red", d=0.6))
# 13 哪边是下 / 屏幕转
p, pid = xiaoji(13, 700, 480, 1.2)
bd(13, p, arr(13, 1000, 300, 1000, 700, c="red", d=0.3), T(13, 1200, 500, 70, "下", c="red", d=0.5), ic(13, "compass" if False else "map_pin", 1500, 450, 150, 0.4, mv="bob", c="blue"))
p, pid = xiaoji(13.5, 960, 480, 1.3)
bd(13.5, p, [rot(13.5, pid, 90, (960, 480), 0.3, 0.6)], arr(13.5, 1300, 300, 1450, 500, c="blue", d=0.5), ic(13.5, "gear", 450, 450, 140, 0.2, mv="spin"))
# 14 摇 vs 转
p, pid = xiaoji(14, 550, 480, 1.1, shake=True)
p2, pid2 = xiaoji(14, 1350, 480, 1.1, c="gold")
bd(14, p, p2, [spin(14, pid2, (1350, 480), 30)], T(14, 550, 800, 60, "摇？", c="red", d=0.3), T(14, 1350, 800, 60, "转？", c="blue", d=0.5))
bd(14.5, mass(14.5, 960, 420), ic(14.5, "question", 960, 720, 160, 0.4, mv="wig", c="red"), T(14.5, 1550, 720, 56, "分不清", c="red", d=0.6))
# 15 陀螺仪
bd(15, ic(15, "chip", 960, 450, 260, 0.0, mv="spin"), T(15, 960, 720, 60, "第二个小家伙", c="ink", d=0.4), ic(15, "eye", 500, 450, 120, 0.3, mv="wig"))
gy = uid("gy")
bd(15.5, [O(15.5, 960, 450, 160, c="ink", fill="gold", idp=gy), P(15.5, "M800,450 L1120,450 M960,290 L960,610", c="ink", w=5, idp=gy), pop(15.5, gy, 0.0), spin(15.5, gy, (960, 450), 90)],
   BIG(15.5, 1450, 450, "陀螺仪", c="blue", d=0.3, s=120), ic(15.5, "phone", 450, 450, 180, 0.4, mv="wig"))
# 16 振动 / 被推
vb = uid("vb")
bd(16, [R(16, 880, 380, 160, 160, c="ink", fill="blue", idp=vb), pop(16, vb, 0.0), wig(16, vb, (960, 600), 12, 5.0)], arr(16, 700, 460, 860, 460, c="ink", d=0.2), arr(16, 1220, 460, 1060, 460, c="ink", d=0.2),
   T(16, 960, 700, 60, "一直来回振动", c="blue", d=0.4), ic(16, "sine", 1550, 460, 150, 0.4, mv="wig", c="red"))
vb = uid("vb")
bd(16.5, [R(16.5, 880, 380, 160, 160, c="ink", fill="blue", idp=vb), pop(16.5, vb, 0.0), wig(16.5, vb, (960, 600), 12, 5.0), sh(16.5, vb, 0, -120, 0.5, 0.4)],
   ic(16.5, "gear", 500, 460, 180, 0.1, mv="spin"), arr(16.5, 1200, 460, 1200, 250, c="red", d=0.5), T(16.5, 1450, 250, 60, "被推一把", c="red", d=0.7))
# 17 科里奥利力
bd(17, BIG(17, 960, 300, "科里奥利力", c="red", d=0.1, s=120), ic(17, "globe", 500, 600, 200, 0.2, mv="spin"), arr(17, 900, 600, 1300, 500, c="blue", d=0.4), ic(17, "wind", 1450, 600, 160, 0.5, mv="wig"))
bd(17.5, [e for q in range(3) for e in __import__("fastkit").bar(17.5, 650 + 250 * q, 750, 120, 120 + 160 * q, "blue", d=0.2 * q)], T(17.5, 900, 830, 56, "推力 ↑ = 转速 ↑", c="ink", d=0.6), ic(17.5, "gear", 1550, 400, 200, 0.1, mv="spin"))
# 18 多大算摇
p, pid = xiaoji(18, 600, 480, 1.2, shake=True)
bd(18, p, ic(18, "ruler", 1200, 450, 220, 0.2, mv="wig"), ic(18, "question", 1600, 450, 150, 0.4, mv="bob", c="red"))
bd(18.5, BIG(18.5, 960, 320, "2022", c="blue", d=0.1, s=160), T(18.5, 960, 520, 64, "行业标准", c="ink", d=0.3), ic(18.5, "flask", 500, 600, 150, 0.2, mv="wig"), ic(18.5, "check", 1450, 600, 150, 0.5, mv="bob", c="green"))
# 19 15 / 35° / 3 s
bd(19, BIG(19, 960, 380, "≥ 15", c="red", d=0.1, s=200), T(19, 960, 560, 60, "米 / 秒²", c="ink", d=0.3), mass(19, 960, 760)[:0], ic(19, "spring", 450, 450, 200, 0.2, mv="bob"), ic(19, "thermometer", 1500, 450, 200, 0.4, mv="wig", c="red"))
p, pid = xiaoji(19.5, 450, 480, 1.0)
bd(19.5, p, [rot(19.5, pid, 35, (450, 610), 0.2, 0.5)], BIG(19.5, 950, 420, "≥ 35°", c="blue", d=0.3, s=130), BIG(19.5, 1500, 420, "≥ 3 秒", c="red", d=0.6, s=130), ic(19.5, "clock", 1500, 680, 140, 0.6, mv="spin"))
# 20 1.5 g
fk = __import__("fastkit")
bd(20, fk.bar(20, 600, 750, 180, 300, "blue", d=0.1), fk.bar(20, 900, 750, 180, 450, "red", d=0.4), T(20, 690, 820, 56, "1 倍重力", c="blue", d=0.2), T(20, 990, 820, 56, "1.5 倍", c="red", d=0.5), ic(20, "globe", 1500, 450, 200, 0.2, mv="spin"))
p, pid = xiaoji(20.5, 700, 480, 1.2)
bd(20.5, p, check(20.5, 1200, 450, d=0.3), T(20.5, 1350, 650, 60, "正常拿，碰不到", c="green", d=0.5), ic(20.5, "map_pin", 1600, 300, 120, 0.2))
# 21 反转二：自愿
bd(21, BIG(21, 960, 200, "反转二", c="red", d=0.0, s=120), ic(21, "ruler", 600, 550, 220, 0.2, mv="wig"), ic(21, "question", 1300, 550, 200, 0.4, mv="wig", c="red"))
bd(21.5, BIG(21.5, 960, 380, "团体标准", c="blue", d=0.1, s=130), T(21.5, 960, 580, 70, "自愿 ≠ 强制", c="red", d=0.4), ic(21.5, "block_force", 400, 500, 180, 0.3, mv="wig"), cross(21.5, 1550, 500, d=0.6))
# 22 工信部点名
bd(22, BIG(22, 960, 300, "2023", c="blue", d=0.1, s=150), ic(22, "magnifier", 500, 550, 200, 0.2, mv="wig"), ic(22, "building", 1450, 550, 220, 0.4, mv="bob"))
p, pid = xiaoji(22.5, 960, 480, 1.3, shake=True, mood="o")
bd(22.5, p, ic(22.5, "thermometer", 500, 450, 200, 0.2, mv="wig", c="red"), T(22.5, 1450, 450, 70, "太灵敏", c="red", d=0.4), arr(22.5, 1450, 520, 1450, 700, c="red", d=0.6))
# 23 走路/坐车
wk = uid("wk")
bd(23, [P(23, "M600,300 L600,560 L540,720 M600,560 L660,720 M600,380 L520,480 M600,380 L680,480", c="ink", w=8, idp=wk), O(23, 600, 240, 55, c="ink", fill="paper", idp=wk), pop(23, wk, 0.0), sh(23, wk, 500, 0, 0.2, 1.2), bob(23, wk, 20, 2.5)],
   ic(23, "phone", 1500, 350, 120, 0.4, mv="wig"), BIG(23, 1500, 600, "一颠", c="red", d=0.6, s=110))
bd(23.5, ic(23.5, "car", 700, 480, 300, 0.0, mv="wig"), adbox(23.5, 1350, 420, 0.4), T(23.5, 1350, 680, 56, "可能被当成“摇”", c="red", d=0.6))
# 24 苹果规则
bd(24, ic(24, "check", 600, 450, 200, 0.1, mv="bob", c="green"), T(24, 1100, 380, 64, "审核规则 4.10", c="ink", d=0.3), ic(24, "magnifier", 1550, 450, 180, 0.3, mv="wig"))
gy = uid("gy")
bd(24.5, [O(24.5, 600, 450, 130, c="ink", fill="gold", idp=gy), P(24.5, "M470,450 L730,450 M600,320 L600,580", c="ink", w=5, idp=gy), pop(24.5, gy, 0.0), spin(24.5, gy, (600, 450), 90)],
   arr(24.5, 780, 450, 1000, 450, d=0.2), BIG(24.5, 1250, 450, "¥", c="gold", d=0.3, s=180), cross(24.5, 1250, 450, d=0.6), ic(24.5, "block_force", 1600, 450, 150, 0.5, mv="wig", c="red"))
# 25 反转三：机器人平衡感
bd(25, BIG(25, 960, 200, "反转三", c="red", d=0.0, s=120), ic(25, "robot_arm", 600, 550, 240, 0.2, mv="wig"), ic(25, "question", 1350, 550, 200, 0.4, mv="wig", c="red"))
rb = uid("rb")
bd(25.5, [R(25.5, 860, 280, 200, 220, c="ink", fill="blue", idp=rb), O(25.5, 920, 360, 14, c="ink", fill="ink", idp=rb), O(25.5, 1000, 360, 14, c="ink", fill="ink", idp=rb),
          P(25.5, "M900,500 L880,720 M1020,500 L1040,720", c="ink", w=8, idp=rb), pop(25.5, rb, 0.0), wig(25.5, rb, (960, 720), 6, 1.2)],
   ic(25.5, "chip", 960, 420, 70, 0.3, mv="spin", c="red"), T(25.5, 1450, 450, 70, "平衡感", c="red", d=0.4), tilt(25.5, 450, 700, 0.2))
# 26 机器人、无人机、平衡车
bd(26, ic(26, "robot_arm", 400, 450, 220, 0.0, mv="wig"), ic(26, "rocket", 960, 450, 200, 0.2, mv="bob"), ic(26, "wheel", 1520, 450, 200, 0.4, mv="spin"))
bd(26.5, tilt(26.5, 700, 700, 0.1, 30), tilt(26.5, 1250, 700, 0.4, -30), T(26.5, 960, 200, 64, "歪没歪？", c="red", d=0.3))
# 27 几百上千次
bd(27, BIG(27, 960, 380, "100s–1000s", c="red", d=0.1, s=150), T(27, 960, 560, 60, "次 / 秒", c="ink", d=0.3), ic(27, "clock", 450, 450, 180, 0.2, mv="spin"), ic(27, "sine", 1500, 600, 180, 0.4, mv="wig", c="blue"))
bd(27.5, tilt(27.5, 960, 750, 0.0, 25), arr(27.5, 1200, 400, 1050, 400, c="green", d=0.6), check(27.5, 1450, 400, d=1.0), ic(27.5, "gear", 500, 400, 160, 0.2, mv="spin"))
# 28 机器人的小脑
p, pid = xiaoji(28, 700, 480, 1.4)
bd(28, p, ic(28, "magnifier", 1200, 450, 220, 0.2, mv="wig"), ic(28, "chip", 1550, 450, 140, 0.4, mv="spin"))
p, pid = xiaoji(28.5, 600, 480, 1.4)
bd(28.5, p, ic(28.5, "robot_arm", 1200, 450, 200, 0.2, mv="wig"), BIG(28.5, 1300, 720, "机器人的小脑", c="blue", d=0.4, s=90), ic(28.5, "check", 1600, 300, 120, 0.5, mv="bob", c="green"))
# 29 友情提示
bd(29, BIG(29, 960, 200, "友情提示", c="ink", d=0.0, s=100), ic(29, "flask", 600, 550, 220, 0.2, mv="wig"), T(29, 1250, 550, 70, "还是测试版", c="red", d=0.4), ic(29, "clock", 1650, 550, 140, 0.4, mv="spin"))
bd(29.5, ic(29.5, "question", 600, 450, 200, 0.1, mv="wig", c="red"), ic(29.5, "gear", 1000, 450, 180, 0.3, mv="spin"), T(29.5, 1400, 450, 64, "名字、位置会变", c="ink", d=0.4))
# 30 闪退
p, pid = xiaoji(30, 700, 480, 1.2)
bd(30, p, mass(30, 1300, 450)[:0], ic(30, "block_force", 1300, 450, 200, 0.2, mv="wig", c="red"), arr(30, 900, 450, 1150, 450, d=0.3))
p, pid = xiaoji(30.5, 960, 480, 1.3, mood="sad")
bd(30.5, p, [rot(30.5, pid, 90, (960, 610), 0.3, 0.4)], T(30.5, 1450, 400, 70, "闪退", c="red", d=0.5), star(30.5, 1300, 300, 0.4, c="red", r=40))
# 31 安卓
bd(31, [e for q in range(4) for e in ic(31, "phone", 450 + 340 * q, 450, 200, 0.12 * q, mv="wig", c=["blue", "red", "green", "gold"][q])], T(31, 960, 720, 64, "安卓早就有", c="ink", d=0.6))
sw = uid("sw")
bd(31.5, [R(31.5, 760, 360, 400, 180, c="ink", fill="paper", idp=sw, sw=6), pop(31.5, sw, 0.0)],
   [O(31.5, 860, 450, 70, c="ink", fill="green", idp=(kn := uid("kn"))), pop(31.5, kn, 0.1), sh(31.5, kn, 200, 0, 0.4, 0.4), pulse(31.5, kn, 0.9)],
   T(31.5, 960, 680, 64, "传感器权限开关", c="blue", d=0.3), ic(31.5, "gear", 450, 450, 160, 0.2, mv="spin"), ic(31.5, "check", 1500, 450, 160, 0.5, mv="bob", c="green"))
# 32 会晃的小秤
p, pid = xiaoji(32, 500, 480, 1.2, shake=True)
bd(32, p, mass(32, 1250, 450), T(32, 1250, 720, 60, "它知道", c="blue", d=0.5))
bd(32.5, mass(32.5, 960, 450, dx=-100, dt=0.2), [sh(32.5, [], 0, 0, 0, 0.1)][:0], BIG(32.5, 960, 750, "会晃的小秤", c="red", d=0.4, s=100))
# 33 别怪手，怪惯性
p, pid = xiaoji(33, 600, 480, 1.2, shake=True, mood="o")
bd(33, p, adbox(33, 1300, 420, 0.2), ic(33, "question", 1650, 650, 120, 0.4, mv="wig", c="red"))
p, pid = xiaoji(33.5, 500, 480, 1.2)
bd(33.5, p, cross(33.5, 1000, 300, d=0.2), T(33.5, 1000, 420, 56, "手", c="ink", d=0.2), BIG(33.5, 1350, 600, "怪惯性！", c="red", d=0.5, s=130), mass(33.5, 1350, 300)[:0])

INS = [
 (1, "而且常常是你根本没想摇，|它就跳了。", "And often you never meant to shake it. | It jumps anyway."),
 (4, "答案藏在一个你天天都在用的物理定律里：|惯性。", "The answer hides in a law of physics you use every day: | inertia."),
 (10, "没有齿轮，没有线圈，|全是在硅片上刻出来的。", "No gears, no coils. | It's all carved into a silicon chip."),
 (13, "计步也靠它：|你每走一步，质量块就晃一下。", "Your step counter uses it too: | every step jiggles the block."),
 (17, "加速度计管往哪冲，陀螺仪管怎么转，|两个一起，手机就知道自己在干嘛。", "The accelerometer feels pushes, the gyroscope feels turns. | Together, the phone knows what it's doing."),
 (20, "粗略估算，|差不多是使劲甩一下手腕。", "As a rough estimate, | that's about a hard flick of the wrist."),
 (24, "所以这个开关，|等于拔掉了广告的“耳朵”。", "So this switch | basically unplugs the ad's ears."),
 (28, "没有它，机器人站不住，|无人机也飞不稳。", "Without it, robots can't stand, | and drones can't fly steady."),
]
p, pid = xiaoji(100, 600, 480, 1.2, mood="o")
bd(100, p, ic(100, "question", 1250, 400, 200, 0.2, mv="wig", c="red"), cross(100, 1250, 650, d=0.4), T(100, 1250, 780, 56, "没想摇", c="ink", d=0.4))
p, pid = xiaoji(100.5, 600, 480, 1.2, mood="sad")
bd(100.5, p, adbox(100.5, 1250, 420, 0.2), adbox(100.5, 1550, 650, 0.5, 0.7))
bd(101, ic(101, "flask", 500, 450, 200, 0.0, mv="wig"), ic(101, "magnifier", 960, 450, 200, 0.2, mv="wig"), ic(101, "atom", 1420, 450, 200, 0.4, mv="spin", c="blue"))
bd(101.5, BIG(101.5, 960, 420, "惯性", c="red", d=0.1, s=200), ic(101.5, "car", 450, 650, 200, 0.3, mv="wig"), ic(101.5, "rocket", 1500, 650, 180, 0.4, mv="bob"))
bd(102, ic(102, "gear", 600, 450, 200, 0.0, mv="spin"), cross(102, 600, 450, d=0.3), ic(102, "magnet", 1300, 450, 200, 0.2, mv="wig"), cross(102, 1300, 450, d=0.5))
bd(102.5, ic(102.5, "chip", 960, 450, 280, 0.0, mv="spin", c="blue"), T(102.5, 960, 720, 60, "刻在硅片上", c="blue", d=0.3), ic(102.5, "lens", 1500, 450, 160, 0.4, mv="wig"))
wk = uid("wk")
bd(103, [P(103, "M600,300 L600,560 L540,720 M600,560 L660,720 M600,380 L520,480 M600,380 L680,480", c="ink", w=8, idp=wk), O(103, 600, 240, 55, c="ink", fill="paper", idp=wk), pop(103, wk, 0.0), sh(103, wk, 400, 0, 0.2, 1.2), bob(103, wk, 20, 2.5)],
    BIG(103, 1450, 400, "1, 2, 3...", c="blue", d=0.4, s=110))
bd(103.5, mass(103.5, 960, 420, dx=-40, dt=0.2), [e for q in range(3) for e in ic(103.5, "map_pin", 600 + 360 * q, 760, 90, 0.3 + 0.15 * q, c="blue")])
bd(104, mass(104, 600, 420), gyro_(104, 1350, 420))
p, pid = xiaoji(104.5, 960, 480, 1.3)
bd(104.5, p, ic(104.5, "check", 1450, 450, 160, 0.4, mv="bob", c="green"), ic(104.5, "gear", 450, 450, 160, 0.2, mv="spin"))
bd(105, ic(105, "ruler", 600, 450, 200, 0.0, mv="wig"), BIG(105, 1250, 450, "估算", c="red", d=0.3, s=130))
arm = uid("arm")
bd(105.5, [P(105.5, "M700,700 L900,450 L1100,400", c="ink", w=12, idp=arm), O(105.5, 1130, 395, 40, c="ink", fill="paper", idp=arm), pop(105.5, arm, 0.0), rot(105.5, arm, -35, (700, 700), 0.3, 0.3), rot(105.5, arm, 0, (700, 700), 0.7, 0.3)],
    ic(105.5, "wind", 1450, 350, 160, 0.4, mv="wig"), BIG(105.5, 1450, 650, "≈ 1.5 g", c="red", d=0.5, s=100))
sw = uid("sw")
bd(106, [R(106, 760, 360, 400, 180, c="ink", fill="paper", idp=sw, sw=6), pop(106, sw, 0.0)],
    [O(106, 1060, 450, 70, c="ink", fill="green", idp=(kn := uid("kn"))), pop(106, kn, 0.1), sh(106, kn, -200, 0, 0.4, 0.4), pulse(106, kn, 0.9)], ic(106, "phone", 400, 450, 200, 0.2, mv="wig"), ic(106, "check", 1500, 450, 160, 0.5, mv="bob", c="green"))
bd(106.5, adbox(106.5, 800, 420, 0.0), ic(106.5, "speaker", 1300, 420, 180, 0.2, mv="wig", c="red"), cross(106.5, 1300, 420, d=0.5), T(106.5, 1050, 700, 64, "拔掉“耳朵”", c="red", d=0.4))
bd(107, tilt(107, 700, 750, 0.0, 60), cross(107, 1300, 450, d=0.5), ic(107, "robot_arm", 1300, 450, 180, 0.2, mv="wig"))
bd(107.5, ic(107.5, "rocket", 960, 450, 240, 0.0, mv="wig"), [rot(107.5, [], 0, (0, 0), 0, 0.1)][:0], ic(107.5, "wind", 500, 450, 180, 0.2, mv="wig"), ic(107.5, "question", 1450, 450, 160, 0.4, mv="wig", c="red"))

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
    main(here, S, B, TITLE, "zh", say={"iOS 27.2": "i O S 二十七点二", "App": "A P P", "vivo": "维沃", "OPPO": "欧珀", "2022年": "二零二二年", "2023年": "二零二三年",
                                       "每秒平方9.8米": "九点八米每二次方秒", "每秒平方15米": "十五米每二次方秒"})
