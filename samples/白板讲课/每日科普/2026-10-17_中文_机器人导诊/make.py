"""每日科普 2026-10-17（中文）：《一天被问七百遍，机器人怎么听清你？》
新闻：人形机器人站上三甲医院导诊台，“硅基接待员”日均答复七百问；据报道是智元的半尺寸人形机器人，回答科室指引、就诊流程、医保政策、
院内导航（新浪机器人热点小时报 2026-10-17 18 时第 8 条；新浪科技热点小时报 2026-10-17 17 时第 8 条；上观新闻）。各报道对医院说法不一，片中只说“一家三甲医院”。
科学：声音到两个麦克风的时间差（声速 340 米/秒，相距 5 厘米最多差约 0.15 毫秒）→ 判断方向；麦克风阵列把声音按时间差对齐再相加（波束成形）：
你的声音对得齐、越加越响，四面八方的噪声对不齐；理想情况下 6 个麦克风信噪比提高 6 倍、约 8 分贝（估算）；分贝每加 10，能量乘 10；
听清以后：语音转文字 → 查医院知识库再回答（“开卷考试”），只答指路、流程、医保。
片中说是估算或推测的：大厅噪声六七十分贝、每 40 秒一个问题、“厕所在哪”问得最多（玩笑）、为什么做成人形、这台机器人具体用什么算法（未公开）。
角色：popkit.cute_guide（小导，半人高导诊机器人，贯穿全片的梗：“厕所在哪”）、stick（病人）。没有手。
    python3 make.py <kokoro 模型目录> | --fake | --boards-only   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)
from popkit import bubble, cute_guide, stick  # noqa: E402

S = [
 ("七百个问题。一台机器人，在医院导诊台，一天要回答七百个问题。", "Seven hundred questions. A robot at a hospital help desk answers 700 questions a day."),
 ("我猜，其中三百个是：厕所在哪？", "My guess: three hundred of them are 'where's the bathroom?'"),
 ("据报道，这是一台半人高的人形机器人，|最近站上了一家三甲医院的导诊台。", "Reportedly, it's a half-size humanoid robot, | now staffing the help desk of a top-tier hospital."),
 ("今天的主角：小导。它管指路、管流程、管医保。", "Today's star: Little Guide. Directions, procedures, insurance questions."),
 ("算一下：一天八小时，七百个问题，|大约每四十秒，就有一个人冲它开口。", "Do the math: 700 questions in an eight-hour day | is one every forty seconds or so."),
 ("今天的烧脑问题：医院大厅那么吵，它怎么听清你说的话？", "Today's brain teaser: in a noisy hospital lobby, how does it hear you?"),
 ("先看有多吵。大厅里叫号、脚步、聊天，估计有六七十分贝。", "First, how noisy? Number calls, footsteps, chatter: maybe 60 to 70 decibels."),
 ("而你对它说话，也就六十分贝左右。噪声，和你一样大。", "And you talking to it? About 60 decibels. The noise is as loud as you are."),
 ("分贝每加十，声音的能量就乘十。七十比六十，能量是十倍。", "Every 10 decibels means ten times the energy. 70 versus 60 is ten times as much."),
 ("人是怎么做到的？鸡尾酒会效应：|一屋子人在说话，你还是能听清对面那一个。", "How do people manage? The cocktail party effect: | a room full of talk, and you still follow one voice."),
 ("秘诀之一：两只耳朵。声音从左边来，左耳先听到，右耳晚一点。", "Secret one: two ears. Sound from the left hits the left ear first, the right ear a bit later."),
 ("大脑靠这一点点时间差，就知道声音从哪儿来。", "From that tiny delay, your brain knows where the sound came from."),
 ("小导没有耳朵，它头上有一圈麦克风，叫麦克风阵列。", "Little Guide has no ears. It has a ring of microphones: a microphone array."),
 ("声速每秒三百四十米。|两个麦克风隔五厘米，时间差最多零点一五毫秒。", "Sound travels 340 meters per second. | Mics 5 cm apart hear it at most 0.15 milliseconds apart."),
 ("这么小的差，电脑也量得出来。于是，它知道你站在哪个方向。", "Tiny, but a computer can measure it. So it knows which direction you're standing in."),
 ("反转一：知道方向，还不够。噪声照样往里灌。", "Twist one: knowing the direction isn't enough. The noise still pours in."),
 ("下一招叫波束成形。打个比方：一群人齐步走。", "The next trick is beamforming. Think of a crowd marching in step."),
 ("把每个麦克风的声音，按你的时间差对齐，再加起来。", "Line up every mic's sound by your time delay, then add them together."),
 ("你的声音，步子对齐了，越加越响。", "Your voice is in step, so it adds up and gets louder."),
 ("四面八方的噪声，步子对不齐，加起来有的抵消，涨得慢。", "Noise from everywhere else is out of step. Some cancels out, and it grows more slowly."),
 ("理想情况下，六个麦克风，你的声音比噪声，能提高六倍，|大约八分贝。这是估算。", "Ideally, six mics boost your voice over the noise six times, | about 8 decibels. That's an estimate."),
 ("相当于，在嘈杂的大厅里，给你一个人开了一束看不见的手电筒。", "It's like an invisible flashlight, shining only on you in the noisy hall."),
 ("反转二：听清了，还得听懂。", "Twist two: hearing you isn't the same as understanding you."),
 ("第一步，把声音变成文字：“请问心内科在几楼？”", "Step one: turn sound into text. 'Which floor is cardiology?'"),
 ("第二步，AI 理解你在问什么：找科室。", "Step two: the AI works out what you want: a department."),
 ("第三步最关键：它不凭记忆回答，|而是先去翻医院的资料。", "Step three is the key: it doesn't answer from memory. | It looks it up first."),
 ("这就像开卷考试：书里写着心内科在三楼，它才说三楼。", "Like an open-book exam: the book says third floor, so it says third floor."),
 ("为什么要开卷？|因为大模型闭卷考试，偶尔会一本正经地瞎编。", "Why open-book? | Because a big AI model, taking the test closed-book, sometimes makes things up with a straight face."),
 ("在医院里，编错一个楼层，病人就要多爬三层楼。", "In a hospital, one wrong floor means a patient climbs three extra flights."),
 ("反转三，最反直觉：好的导诊机器人，要知道什么不该答。", "Twist three, the counterintuitive one: a good guide robot knows what not to answer."),
 ("报道里，它管的是指路、流程、医保。看病，还是交给医生。", "In the reports, it handles directions, procedures, insurance. Diagnosis stays with the doctors."),
 ("那为什么要做成人形，而不是一块大屏幕？", "So why make it humanoid, instead of just a big screen?"),
 ("我的推测：人更愿意跟像人的东西说话，|而且它能转身，能抬手给你指方向。", "My guess: people talk more easily to something human-shaped, | and it can turn and point the way."),
 ("半人高也有讲究：老人、坐轮椅的人、小朋友，都能平视它。这也是推测。", "Half height may matter too: seniors, wheelchair users, kids can look it in the eye. Also a guess."),
 ("再回到七百个问题。|人回答七百遍，嗓子哑了，脾气也没了。", "Back to the 700 questions. | A person answering 700 times loses their voice, and their patience."),
 ("小导回答第七百遍，和第一遍一样耐心。", "Little Guide answers the 700th time as patiently as the first."),
 ("这可能才是它最大的本事：不累，不烦。", "That may be its real superpower: it never gets tired or grumpy."),
 ("算总账：听方向，靠时间差。", "Final tally: direction comes from the time delay."),
 ("听清楚，靠波束成形。", "Hearing clearly comes from beamforming."),
 ("答对，靠开卷考试。|不乱答，靠知道自己的边界。", "Getting it right comes from the open book. | Not getting it wrong comes from knowing its limits."),
 ("友情提示：七百问是报道的数字，|分贝和信噪比是我们的估算。", "Friendly fine print: 700 is the reported number. | The decibels and the gain are our estimates."),
 ("这台机器人内部用什么算法，没有公开。我们讲的是通用的原理。", "Its exact algorithms aren't public. We explained the general principles."),
 ("最后，小导想说：厕所在您左手边，直走二十米。", "Finally, Little Guide would like to say: the bathroom is on your left, twenty meters ahead."),
 ("这是今天的第七百零一遍。", "That's the seven hundred and first time today."),
]
TITLE = {"zh": "一天被问七百遍，机器人怎么听清你？", "en": "700 questions a day: how does a robot hear you?"}
SAY = {"AI": "A I", "0.15": "零点一五", "340": "三百四十"}


def G(at, cx, cy, k, **kw):
    i = uid("gd")
    return cute_guide(cx, cy, k, at, idp=i, **kw), i


def person(at, cx, cy, k=1.0, arms="down", walk=False):
    i = uid("pp")
    E = stick(cx, cy, k, at, idp=i, arms=arms) + [bob(at, i + "*", 6 * k, 1.6)]
    return E, i


def desk(at, x=560, y=760, w=800):
    return [R(at, x, y, w, 140, c="ink", sw=5), P(at, f"M{x},{y + 40} L{x + w},{y + 40}", c="muted", w=3)]


def mics(at, cx, cy, r=90, n=6, d=0.0):
    """A ring of microphones (dots) seen from above; each pops in, then they pulse."""
    E = []
    for k in range(n):
        i = uid("mic")
        x, y = cx + r * __import__("math").cos(k * 6.283 / n), cy + r * __import__("math").sin(k * 6.283 / n)
        E += [O(at, x, y, 16, c="blue", fill="blue", idp=i), pop(at, i, d + 0.1 * k), pulse(at, i, d + 0.8 + 0.1 * k)]
    return E


def wave(at, x0, y, n, amp, c="blue", lam=80, d=0.0, idp=None, w=5):
    i = idp or uid("sw")
    pts = " ".join(f"Q{x0 + lam * k + lam / 4},{y - amp * (1 if k % 2 == 0 else -1)} {x0 + lam * k + lam / 2},{y}" for k in range(2 * n))
    pts = f"M{x0},{y} " + " ".join(f"Q{x0 + lam / 2 * k + lam / 4},{y - amp * (1 if k % 2 == 0 else -1)} {x0 + lam / 2 * (k + 1)},{y}" for k in range(2 * n))
    return [P(at, pts, c=c, w=w, idp=i), {"t": "move", "at": at, "kind": "grow", "targets": [i], "axis": "x", "pivot": [x0, y], "dur": 0.8, "delay": d}]


def noise(at, x0, y, n=10, c="muted", d=0.0, w=4):
    i = uid("nz")
    pts = f"M{x0},{y} " + " ".join(f"L{x0 + 30 * (k + 1)},{y + ((k * 53) % 7 - 3) * 14}" for k in range(n))
    return [P(at, pts, c=c, w=w, idp=i), wig(at, i, (x0 + 15 * n, y), 3, 5), pop(at, i, d)]


B = []
# 0 七百个问题
a = 0
els, i = G(a, 960, 900, 1.3)
E = desk(a, 560, 760) + els
for k in range(6):
    q = uid("q")
    x, y = 300 + 270 * k, 220 + 70 * (k % 2)
    E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": x, "y": y, "size": 110, "c": ["red", "blue", "gold"][k % 3]}, pop(a, q, 0.2 + 0.25 * k), bob(a, q, 10, 1.2 + 0.2 * k)]
E += BIG(a, 1560, 600, "700", c="red", d=1.8, s=150) + T(a, 1560, 700, 52, "个问题 / 天", c="red", d=2.2)
B.append(E)
# 1 厕所在哪
a = 1
els, i = G(a, 520, 900, 1.2, sweat=True)
E = els
for k in range(5):
    pp, j = person(a, 1150 + 140 * k, 900, 0.7)
    E += pp + [sh(a, j + "*", -120, 0, 0.2 + 0.25 * k, 0.8)]
E += bubble(1060, 230, 560, 140, a, "厕所在哪？", s=60, c="red")
E += BIG(a, 1340, 520, "× 300", c="red", d=1.0, s=110)
B.append(E)
# 2 半人高人形机器人，三甲医院导诊台
a = 2
els, i = G(a, 700, 900, 1.3)
E = desk(a, 300, 760) + els
pp, j = person(a, 1500, 900, 1.6)
E += pp + arr(a, 1150, 900, 1150, 340, c="blue", w=5, d=0.3) + BIG(a, 1150, 280, "半人高", c="blue", d=0.5, s=80) + star(a, 1700, 300, 0.8)
B.append(E)
a = 2.5
els, i = G(a, 700, 900, 1.2)
E = desk(a, 300, 760) + els
hs = uid("hosp")
E += [R(a, 1300, 260, 420, 460, c="ink", idp=hs), P(a, "M1470,380 L1550,380 M1510,340 L1510,420", c="red", w=10, idp=hs), pop(a, hs, 0.1), wig(a, hs, (1510, 720), 1, 1)]
E += T(a, 1510, 800, 56, "三甲医院 · 导诊台", c="ink", d=0.4) + T(a, 1510, 880, 40, "（据报道）", c="muted", d=0.8)
B.append(E)
# 3 主角小导
a = 3
els, i = G(a, 960, 920, 1.7)
E = els + star(a, 400, 300, 0.3) + star(a, 1520, 280, 0.6)
for k, (lab, c, x, y) in enumerate((("指路", "blue", 400, 720), ("流程", "green", 1520, 560), ("医保", "gold", 1520, 720))):
    E += T(a, x, y, 64, lab, c=c, d=1.0 + 0.4 * k)
E += BIG(a, 400, 520, "小导", c="red", d=0.2, s=100)
B.append(E)
# 4 每 40 秒一个
a = 4
ck = uid("clk")
E = [O(a, 520, 480, 220, c="ink", sw=7), P(a, "M520,480 L520,300", c="red", w=8, idp=ck), spin(a, ck, (520, 480), 90)]
mn = uid("mn")
E += [P(a, "M520,480 L640,480", c="ink", w=8, idp=mn), spin(a, mn, (520, 480), 8)]
for k in range(5):
    pp, j = person(a, 1100 + 150 * k, 900, 0.6)
    E += pp + [pop(a, j, 0.4 + 0.4 * k)]
E += BIG(a, 1400, 360, "8 小时", c="ink", d=0.3, s=110) + T(a, 1400, 480, 56, "700 问", c="red", d=0.9)
B.append(E)
a = 4.5
E = desk(a, 160, 760, 500)
els, i = G(a, 410, 900, 0.9)
E += els
for k in range(5):
    pp, j = person(a, 900 + 200 * k, 900, 0.7)
    E += pp + [sh(a, j + "*", -150, 0, 0.2 + 0.3 * k, 0.6)]
E += BIG(a, 1300, 360, "40 秒", c="red", d=0.3, s=130) + T(a, 1300, 480, 48, "一个人（估算）", c="muted", d=0.8)
B.append(E)
# 5 烧脑问题
a = 5
els, i = G(a, 960, 920, 1.3, sweat=True)
E = els
for k in range(8):
    E += noise(a, 100 + 220 * k, 260 + 60 * (k % 3), n=6, d=0.1 * k)
q = uid("q")
E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 1500, "y": 520, "size": 240, "c": "red"}, pop(a, q, 1.0), pulse(a, q, 1.6)]
E += BIG(a, 520, 560, "怎么听清？", c="ink", d=1.4, s=100)
B.append(E)
# 6 有多吵：六七十分贝
a = 6
E = []
for k in range(5):
    pp, j = person(a, 260 + 180 * k, 900, 0.7, arms="up" if k % 2 else "down")
    E += pp + [wig(a, j + "*", (260 + 180 * k, 900), 3, 2 + k * 0.3)]
spk = uid("spk")
E += [{"t": "icon", "at": a, "id": spk, "name": "speaker", "x": 360, "y": 260, "size": 160, "c": "ink"}, pulse(a, spk, 0.2)]
E += sound(a, 460, 260, 1.0, c="red", d=0.4)
E += BIG(a, 1450, 420, "60–70", c="red", d=0.8, s=150) + T(a, 1450, 560, 60, "分贝（估计）", c="red", d=1.2)
B.append(E)
# 7 你也就 60 分贝
a = 7
pp, j = person(a, 400, 900, 1.2)
E = pp + sound(a, 480, 580, 0.9, c="blue", d=0.2)
E += bar(a, 900, 860, 180, 360, "blue", d=0.4) + bar(a, 1300, 860, 180, 390, "muted", d=0.8)
E += T(a, 990, 920, 48, "你", c="blue", d=0.4) + T(a, 1390, 920, 48, "噪声", c="muted", d=0.8)
E += BIG(a, 1200, 280, "一样大", c="red", d=1.6, s=110)
B.append(E)
# 8 每加 10 分贝能量 ×10
a = 8
E = bar(a, 400, 860, 160, 60, "blue", d=0.2) + bar(a, 900, 860, 160, 600, "red", d=0.8, dur=1.2)
E += T(a, 480, 920, 52, "60 分贝", c="blue", d=0.2) + T(a, 980, 920, 52, "70 分贝", c="red", d=0.8)
E += arr(a, 600, 760, 860, 380, c="ink", w=6, d=1.0) + BIG(a, 1500, 460, "× 10", c="red", d=1.4, s=150) + T(a, 1500, 600, 56, "能量", c="red", d=1.8)
B.append(E)
# 9 鸡尾酒会效应
a = 9
E = []
for k in range(6):
    pp, j = person(a, 200 + 150 * k, 880, 0.6, arms="up" if k % 2 else "down")
    E += pp + [wig(a, j + "*", (200 + 150 * k, 880), 3, 2.4)]
for k in range(3):
    E += noise(a, 150 + 300 * k, 300, n=6, d=0.1 * k)
cg = uid("glass")
E += [P(a, "M1700,560 L1820,560 L1760,660 Z M1760,660 L1760,760 M1720,760 L1800,760", c="gold", w=5, idp=cg), wig(a, cg, (1760, 760), 6, 1.5)]
E += BIG(a, 960, 160, "鸡尾酒会效应", c="ink", d=0.2, s=90)
B.append(E)
a = 9.5
E = []
for k in range(5):
    pp, j = person(a, 200 + 160 * k, 900, 0.7, arms="up" if k % 2 else "down")
    E += pp + [wig(a, j + "*", (200 + 160 * k, 900), 3, 2.6)] + noise(a, 120 + 160 * k, 520 - 40 * (k % 2), n=4, d=0.1 * k)
me, j = person(a, 1550, 900, 1.2)
E += me + wave(a, 1050, 560, 3, 50, c="blue", d=0.3, w=7)
hl = uid("hl")
E += [O(a, 1550, 520, 210, c="gold", sw=6, idp=hl), pop(a, hl, 0.9), pulse(a, hl, 1.4)]
E += T(a, 1550, 220, 60, "只听清这一个", c="blue", d=0.6)
B.append(E)
# 10 两只耳朵
a = 10
E = [O(a, 960, 520, 200, c="ink", sw=7)]
el, er = uid("ear"), uid("ear")
E += [O(a, 750, 520, 40, c="ink", sw=6, idp=el), O(a, 1170, 520, 40, c="ink", sw=6, idp=er), pulse(a, el, 0.8), pulse(a, er, 1.6)]
src = uid("src")
E += [{"t": "icon", "at": a, "id": src, "name": "speaker", "x": 200, "y": 520, "size": 140, "c": "red"}, pulse(a, src, 0.1)]
for k in range(3):
    sw_ = uid("sw")
    E += [P(a, "M300,440 Q340,520 300,600", c="red", w=6, idp=sw_), sh(a, sw_, 900, 0, 0.2 + 0.25 * k, 1.8)]
E += T(a, 750, 830, 52, "左耳：先", c="green", d=0.8) + T(a, 1170, 830, 52, "右耳：晚一点", c="gold", d=1.6)
B.append(E)
# 11 大脑靠时间差
a = 11
br = uid("brain")
E = [P(a, "M760,560 Q700,360 900,320 Q960,240 1060,300 Q1220,300 1200,460 Q1260,600 1100,640 Q960,700 860,640 Q740,640 760,560 Z",
       c="red", w=6, idp=br), pulse(a, br, 0.4), wig(a, br, (980, 480), 2, 1.5)]
E += [P(a, "M860,420 Q960,380 1060,440 M880,520 Q980,480 1100,540", c="red", w=4, idp=br)]
E += arr(a, 400, 480, 720, 480, c="green", d=0.3) + arr(a, 1600, 480, 1250, 480, c="gold", d=0.9)
E += BIG(a, 980, 860, "→ 方向", c="blue", d=1.6, s=100) + T(a, 400, 400, 52, "先", c="green", d=0.3) + T(a, 1600, 400, 52, "后", c="gold", d=0.9)
B.append(E)
# 12 麦克风阵列
a = 12
els, i = G(a, 600, 960, 1.4)
E = els
E += [O(a, 1400, 480, 180, c="ink", sw=5)] + mics(a, 1400, 480, r=140, n=6, d=0.4)
E += arr(a, 760, 300, 1200, 400, c="muted", w=4, d=0.2) + T(a, 1400, 760, 60, "麦克风阵列", c="blue", d=1.2) + T(a, 1400, 840, 44, "（从上往下看）", c="muted", d=1.6)
B.append(E)
# 13 340 米/秒，5 厘米，0.15 毫秒
a = 13
# 13 声速 340 米/秒
E = []
for k in range(4):
    sw_ = uid("sw")
    E += [P(a, f"M{250},{420 + 30 * k} Q{320},{540} {250},{660 - 30 * k}", c="red", w=6, idp=sw_), sh(a, sw_, 1300, 0, 0.1 + 0.25 * k, 1.6)]
spk = uid("spk")
E += [{"t": "icon", "at": a, "id": spk, "name": "speaker", "x": 160, "y": 540, "size": 150, "c": "ink"}, pulse(a, spk, 0.1)]
E += BIG(a, 960, 300, "340 米/秒", c="red", d=0.2, s=130) + T(a, 960, 820, 52, "一秒钟，三个多足球场", c="muted", d=0.9)
B.append(E)
a = 13.5
m1, m2 = uid("mic"), uid("mic")
E = [O(a, 700, 640, 28, c="blue", fill="blue", idp=m1), O(a, 1220, 640, 28, c="blue", fill="blue", idp=m2), pulse(a, m1, 0.9), pulse(a, m2, 1.5)]
for k in range(3):
    sw_ = uid("sw")
    E += [P(a, f"M{300},{380 + 20 * k} Q{360},{440 + 20 * k} {300},{520 + 20 * k}", c="red", w=6, idp=sw_), sh(a, sw_, 1100, 120, 0.2 + 0.2 * k, 2.0)]
E += [{"t": "line", "at": a, "pts": [[700, 740], [1220, 740]], "c": "muted", "w": 3}] + T(a, 960, 800, 48, "5 厘米", c="muted", d=0.6)
E += BIG(a, 1580, 600, "0.15", c="red", d=1.0, s=130) + T(a, 1580, 700, 52, "毫秒", c="red", d=1.8)
B.append(E)
# 14 它知道你在哪个方向
a = 14
E = [O(a, 700, 540, 120, c="ink", sw=5)] + mics(a, 700, 540, r=90, n=6, d=0.0)
pp, j = person(a, 1500, 860, 1.0)
E += pp + [sh(a, j + "*", 0, 0, 0, 0.3)]
dr = uid("dir")
E += [P(a, "M700,540 L1380,600", c="red", w=7, idp=dr), {"t": "move", "at": a, "kind": "grow", "targets": [dr], "axis": "x", "pivot": [700, 540], "dur": 0.8, "delay": 0.8},
      wig(a, dr, (700, 540), 3, 1.2)]
E += sound(a, 1400, 600, 0.8, c="blue", d=0.3, dirn=-1)
E += BIG(a, 960, 200, "你在这边！", c="green", d=1.6, s=96)
B.append(E)
# 15 反转一：噪声照样灌进来
a = 15
els, i = G(a, 960, 940, 1.3, mood="worried")
E = els
for k in range(10):
    nz = uid("nz")
    x, y = (150 if k % 2 else 1770), 220 + 70 * k
    E += [P(a, f"M{x},{y} l30,-20 l30,30 l30,-25 l30,20", c="muted", w=5, idp=nz), sh(a, nz, (700 if k % 2 else -760), 80, 0.1 + 0.15 * k, 1.6)]
E += BIG(a, 960, 160, "反转一", c="red", d=0.0, s=90) + T(a, 960, 280, 56, "噪声照样往里灌", c="ink", d=0.8)
B.append(E)
# 16 波束成形：齐步走
a = 16
E = []
for k in range(6):
    pp, j = person(a, 300 + 140 * k, 900, 0.8, arms="up")
    E += pp + [sh(a, j + "*", 600, 0, 0.3, 2.6)]
E += BIG(a, 960, 220, "波束成形", c="blue", d=0.2, s=110) + T(a, 960, 340, 56, "= 一群人齐步走", c="ink", d=1.0)
for k in range(3):
    E += star(a, 1400 + 140 * k, 520 + 40 * k, 1.2 + 0.2 * k)
B.append(E)
# 17 对齐再相加
a = 17
E = []
for k in range(3):
    i_ = uid("sw")
    y = 300 + 160 * k
    E += wave(a, 300 + 60 * k, y, 3, 40, c="blue", d=0.1 * k, idp=i_) + [sh(a, i_, -60 * k, 0, 1.0, 0.8)]
    E += T(a, 220, y + 16, 44, f"麦{k + 1}", c="muted", d=0.1 * k)
E += arr(a, 1250, 460, 1450, 460, c="ink", w=6, d=1.8) + [{"t": "line", "at": a, "pts": [[300, 800], [1100, 800]], "c": "muted", "w": 2}]
E += T(a, 700, 880, 52, "按时间差对齐", c="blue", d=1.0) + BIG(a, 1650, 470, "＋", c="red", d=2.0, s=150)
B.append(E)
# 18 你的声音越加越响
a = 18
E = wave(a, 200, 300, 3, 30, c="blue", d=0.1) + wave(a, 200, 460, 3, 30, c="blue", d=0.3) + wave(a, 200, 620, 3, 30, c="blue", d=0.5)
E += arr(a, 760, 460, 960, 460, c="ink", w=6, d=0.9)
E += wave(a, 1040, 460, 3, 120, c="blue", d=1.2, w=8)
E += BIG(a, 1300, 820, "越加越响", c="green", d=1.6, s=100)
B.append(E)
# 19 噪声对不齐
a = 19
E = noise(a, 200, 300, n=10, d=0.1) + noise(a, 200, 460, n=10, d=0.3) + noise(a, 200, 620, n=10, d=0.5)
E += arr(a, 560, 460, 860, 460, c="ink", w=6, d=0.9) + noise(a, 1000, 460, n=16, c="muted", d=1.2, w=3)
E += BIG(a, 1300, 820, "涨得慢", c="muted", d=1.6, s=100) + T(a, 1300, 260, 52, "步子对不齐", c="muted", d=0.6)
B.append(E)
# 20 6 个麦克风，×6，约 8 分贝
a = 20
E = [O(a, 420, 480, 150, c="ink", sw=5)] + mics(a, 420, 480, r=110, n=6, d=0.0)
E += bar(a, 900, 860, 150, 100, "muted", d=0.4) + bar(a, 1150, 860, 150, 600, "blue", d=0.9, dur=1.2)
E += T(a, 975, 920, 44, "噪声", c="muted", d=0.4) + T(a, 1225, 920, 44, "你", c="blue", d=0.9)
E += BIG(a, 1600, 400, "× 6", c="red", d=1.4, s=150)
B.append(E)
a = 20.5
E = bar(a, 500, 860, 200, 300, "muted", d=0.1) + bar(a, 800, 860, 200, 300, "blue", d=0.1)
up = uid("up")
E += [R(a, 800, 360, 200, 200, c="blue", fill="blue", idp=up), {"t": "move", "at": a, "kind": "grow", "targets": [up], "axis": "y", "pivot": [900, 560], "dur": 0.8, "delay": 0.4}]
E += arr(a, 1060, 760, 1060, 380, c="red", w=7, d=0.5)
E += T(a, 600, 920, 44, "噪声", c="muted", d=0.1) + T(a, 900, 920, 44, "你", c="blue", d=0.1)
E += BIG(a, 1450, 480, "≈ 8 分贝", c="red", d=0.6, s=110) + T(a, 1450, 620, 52, "这是估算", c="gold", d=1.0)
B.append(E)
# 21 看不见的手电筒
a = 21
els, i = G(a, 380, 940, 1.1)
E = els
bm = uid("beam")
E += [P(a, "M470,520 L1560,330 L1560,770 Z", c="gold", w=4, fill="gold", idp=bm), pop(a, bm, 0.3), wig(a, bm, (470, 520), 2, 0.8)]
pp, j = person(a, 1500, 880, 1.0, arms="up")
E += pp
for k in range(4):
    q, _ = person(a, 800 + 160 * k, 900 + 0 * k, 0.5)
    E += q
E += BIG(a, 1000, 200, "手电筒", c="gold", d=1.2, s=100) + star(a, 1700, 300, 1.6)
B.append(E)
# 22 反转二：听清 ≠ 听懂
a = 22
ear = uid("ear")
E = [P(a, "M500,360 Q640,300 680,460 Q700,600 560,640 Q520,700 560,760", c="ink", w=8, idp=ear), wig(a, ear, (580, 560), 3, 1.6)]
br = uid("brain")
E += [P(a, "M1260,560 Q1200,360 1400,320 Q1460,240 1560,300 Q1720,300 1700,460 Q1760,600 1600,640 Q1460,700 1360,640 Q1240,640 1260,560 Z",
        c="red", w=6, idp=br), pop(a, br, 1.0), pulse(a, br, 1.6)]
E += BIG(a, 960, 520, "≠", c="red", d=0.8, s=200) + T(a, 600, 860, 60, "听清", c="blue", d=0.3) + T(a, 1480, 860, 60, "听懂", c="red", d=1.2)
E += BIG(a, 960, 160, "反转二", c="red", d=0.0, s=90)
B.append(E)
# 23 声音 → 文字
a = 23
E = wave(a, 200, 500, 4, 60, c="blue", d=0.1) + arr(a, 900, 500, 1100, 500, c="ink", w=6, d=0.8)
E += T(a, 1500, 480, 60, "“心内科在几楼？”", c="ink", d=1.2)
for k in range(4):
    dt = uid("dot")
    E += [O(a, 1180 + 40 * k, 600, 10, c="gold", fill="gold", idp=dt), pop(a, dt, 0.9 + 0.1 * k), bob(a, dt, 8, 2 + 0.3 * k)]
E += BIG(a, 960, 200, "第一步：声音变文字", c="blue", d=0.2, s=80)
B.append(E)
# 24 AI 理解：找科室
a = 24
els, i = G(a, 400, 940, 1.1)
E = els
gr = uid("gear")
E += [{"t": "icon", "at": a, "id": gr, "name": "gear", "x": 1000, "y": 480, "size": 240, "c": "blue"}, spin(a, gr, (1000, 480), 40)]
gr2 = uid("gear")
E += [{"t": "icon", "at": a, "id": gr2, "name": "gear", "x": 1170, "y": 340, "size": 150, "c": "gold"}, spin(a, gr2, (1170, 340), -60)]
E += arr(a, 1180, 520, 1420, 520, c="ink", w=6, d=1.0) + BIG(a, 1640, 540, "找科室", c="green", d=1.4, s=90)
E += BIG(a, 960, 180, "第二步：AI 理解", c="blue", d=0.2, s=80)
B.append(E)
# 25 先翻资料
a = 25
br = uid("brain")
E = [P(a, "M660,560 Q600,360 800,320 Q860,240 960,300 Q1120,300 1100,460 Q1160,600 1000,640 Q860,700 760,640 Q640,640 660,560 Z", c="red", w=6, idp=br),
     pulse(a, br, 0.2), wig(a, br, (880, 480), 3, 2)]
for k in range(3):
    qq = uid("q")
    E += [{"t": "icon", "at": a, "id": qq, "name": "question", "x": 760 + 120 * k, "y": 470, "size": 80, "c": "muted"}, pop(a, qq, 0.2 + 0.2 * k), bob(a, qq, 8, 2)]
E += cross(a, 1400, 480, d=0.9) + BIG(a, 1400, 700, "不凭记忆", c="red", d=0.6, s=90) + BIG(a, 960, 160, "第三步，最关键", c="ink", d=0.0, s=80)
B.append(E)
a = 25.5
bk = uid("book")
E = [P(a, "M560,320 L960,360 L1360,320 L1360,780 L960,820 L560,780 Z M960,360 L960,820", c="ink", w=6, idp=bk), pop(a, bk, 0.3), wig(a, bk, (960, 820), 1.5, 1)]
for k in range(3):
    pg = uid("pg")
    E += [P(a, "M960,360 Q1140,300 1340,330 L1340,770 Q1140,740 960,810 Z", c="muted", w=3, idp=pg), rot(a, pg, -175, (960, 580), 0.6 + 0.4 * k, 0.4)]
E += BIG(a, 960, 200, "先翻资料", c="green", d=0.2, s=90) + check(a, 1550, 560, d=1.0)
B.append(E)
# 26 开卷考试：三楼
a = 26
E = [R(a, 300, 300, 600, 500, c="ink", sw=6)]
for k in range(5):
    E += [P(a, f"M340,{380 + 80 * k} L860,{380 + 80 * k}", c="muted", w=3)]
hl = uid("hl")
E += [R(a, 330, 520, 540, 60, c="gold", fill="gold", idp=hl), pop(a, hl, 0.6), pulse(a, hl, 1.2)]
E += T(a, 600, 565, 44, "心内科 · 3 楼", c="ink", d=0.6)
els, i = G(a, 1450, 940, 1.1)
E += els + BIG(a, 1450, 260, "3 楼！", c="green", d=1.6, s=110) + T(a, 600, 230, 56, "开卷考试", c="blue", d=0.2)
B.append(E)
# 27 闭卷会瞎编
a = 27
bk = uid("book")
E = [P(a, "M700,360 L1220,360 L1220,780 L700,780 Z", c="ink", w=7, idp=bk), pop(a, bk, 0.1), wig(a, bk, (960, 780), 2, 1)]
lk = uid("lock")
E += [R(a, 910, 540, 100, 80, c="red", fill="red", idp=lk), P(a, "M930,540 L930,500 Q960,460 990,500 L990,540", c="red", w=7, idp=lk), pop(a, lk, 0.4), pulse(a, lk, 0.9)]
E += BIG(a, 960, 200, "为什么要开卷？", c="ink", d=0.0, s=90) + T(a, 1500, 600, 56, "闭卷？", c="red", d=0.6)
B.append(E)
a = 27.5
els, i = G(a, 500, 940, 1.2)
E = els + [wig(a, i + "_b", (500, 700), 2, 6)]
E += bubble(820, 240, 760, 150, a, "心内科在…十八楼？", s=56, c="red")
for k in range(3):
    E += star(a, 1100 + 200 * k, 560 + 50 * (k % 2), 0.8 + 0.3 * k, c="red")
E += BIG(a, 1200, 820, "一本正经地瞎编", c="red", d=1.4, s=80)
B.append(E)
# 28 多爬三层楼
a = 28
E = [P(a, "M300,900 L300,780 L500,780 L500,660 L700,660 L700,540 L900,540 L900,420 L1100,420", c="ink", w=7)]
pp, j = person(a, 400, 780, 0.6)
E += pp + [sh(a, j + "*", 200, -120, 0.3, 0.5), sh(a, j + "*", 200, -120, 0.9, 0.5), sh(a, j + "*", 200, -120, 1.5, 0.5)]
sw_ = uid("swt")
E += [P(a, "M1000,300 Q1020,340 1000,360 Q980,340 1000,300", c="blue", w=4, idp=sw_), sh(a, sw_, 0, 120, 1.8, 1.0)]
E += BIG(a, 1500, 420, "+3 层", c="red", d=1.2, s=130) + T(a, 1500, 560, 52, "错一个楼层", c="muted", d=0.3)
B.append(E)
# 29 反转三：知道什么不该答
a = 29
els, i = G(a, 960, 940, 1.4)
E = els
st_ = uid("stop")
E += [O(a, 1500, 460, 130, c="red", sw=8, idp=st_), P(a, "M1410,550 L1590,370", c="red", w=10, idp=st_), pop(a, st_, 1.0), pulse(a, st_, 1.6)]
E += BIG(a, 960, 160, "反转三", c="red", d=0.0, s=90) + T(a, 420, 460, 60, "什么不该答", c="ink", d=0.8)
E += star(a, 420, 640, 1.4)
B.append(E)
# 30 指路流程医保 vs 看病交给医生
a = 30
els, i = G(a, 420, 940, 1.1)
E = els
for k, lab in enumerate(("指路", "流程", "医保")):
    E += T(a, 900, 360 + 120 * k, 60, lab, c="green", d=0.2 + 0.3 * k) + check(a, 1060, 340 + 120 * k, d=0.3 + 0.3 * k)
dr, j = person(a, 1600, 860, 1.1)
E += dr + [pop(a, j, 1.4)]
cx_ = uid("crs")
E += [P(a, "M1560,500 L1640,500 M1600,460 L1600,540", c="red", w=9, idp=cx_), pop(a, cx_, 1.6), pulse(a, cx_, 2.0)]
E += T(a, 1600, 300, 60, "看病：医生", c="red", d=1.4)
B.append(E)
# 31 为什么人形，不是大屏幕
a = 31
scr = uid("scr")
E = [R(a, 300, 260, 460, 560, c="ink", sw=7, idp=scr), pop(a, scr, 0.2), wig(a, scr, (530, 820), 1, 1)]
els, i = G(a, 1400, 900, 1.3)
E += els + [pop(a, i + "*", 0.8)]
E += BIG(a, 960, 520, "？", c="red", d=1.2, s=180) + T(a, 530, 900, 52, "大屏幕", c="muted", d=0.2) + T(a, 1400, 160, 52, "人形", c="blue", d=0.8)
B.append(E)
# 32 推测：像人 + 能转身指路
a = 32
els, i = G(a, 600, 940, 1.3)
E = els
pp, j = person(a, 1300, 940, 1.2)
E += pp + bubble(1350, 260, 420, 130, a, "你好呀！", s=56, c="green")
for k in range(3):
    ht = uid("heart")
    x = 900 + 100 * k
    E += [P(a, f"M{x},{420} Q{x - 30},{380} {x - 40},{410} Q{x - 40},{440} {x},{470} Q{x + 40},{440} {x + 40},{410} Q{x + 30},{380} {x},{420} Z", c="red", w=4, fill="red", idp=ht),
          pop(a, ht, 0.3 + 0.25 * k), sh(a, ht, 0, -120, 0.6 + 0.25 * k, 1.2)]
E += BIG(a, 300, 200, "推测", c="gold", d=0.0, s=90) + T(a, 960, 820, 52, "像人，更愿意开口", c="ink", d=0.8)
B.append(E)
a = 32.5
els, i = G(a, 700, 940, 1.3, moves=False)
E = els + [rot(a, i + "*", -12, (700, 940), 0.4, 0.6), wig(a, i + "_arm", (700 + 62 * 1.3, 940 - 260 * 1.3), 18, 2.5), bob(a, i + "_ant", 6, 2)]
E += arr(a, 960, 380, 1500, 380, c="blue", w=7, d=0.8) + T(a, 1550, 330, 56, "那边！", c="blue", d=1.0, align="left")
pp, j = person(a, 1500, 900, 0.9)
E += pp + [sh(a, j + "*", 120, 0, 1.4, 1.0)]
E += T(a, 400, 200, 56, "能转身 · 能指路", c="blue", d=0.0)
B.append(E)
# 33 半人高：平视
a = 33
els, i = G(a, 760, 940, 1.2)
E = els
kd, j = person(a, 1200, 940, 0.75)
E += kd
wc = uid("wc")
E += [O(a, 1560, 880, 60, c="ink", sw=6, idp=wc), spin(a, wc, (1560, 880), 30)]
sp, j2 = person(a, 1560, 820, 0.6)
E += sp
ln = uid("eye")
E += [P(a, "M840,500 L1700,520", c="green", w=4, idp=ln, dash=True), pop(a, ln, 1.0), pulse(a, ln, 1.6)]
E += T(a, 1200, 220, 60, "都能平视", c="green", d=1.2) + T(a, 1200, 300, 44, "（也是推测）", c="gold", d=1.8)
B.append(E)
# 34 人答七百遍：嗓子哑了
a = 34
E = []
for k in range(10):
    q = uid("q")
    E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 300 + 150 * k, "y": 400 + 120 * (k % 3), "size": 110, "c": ["red", "blue", "gold"][k % 3]},
          pop(a, q, 0.05 + 0.1 * k), bob(a, q, 10, 1.3 + 0.1 * k)]
E += BIG(a, 960, 860, "700 个问题", c="red", d=0.6, s=110)
B.append(E)
a = 34.5
pp, j = person(a, 600, 900, 1.3)
E = pp + [wig(a, j + "*", (600, 900), 4, 5)]
for k in range(3):
    st_ = uid("steam")
    E += [P(a, f"M{540 + 60 * k},380 Q{520 + 60 * k},330 {550 + 60 * k},290 Q{580 + 60 * k},250 {550 + 60 * k},210", c="red", w=5, idp=st_), sh(a, st_, 0, -80, 0.3 + 0.3 * k, 1.4)]
E += bar(a, 1200, 860, 140, 500, "red", d=0.2, dur=2.0)
E += T(a, 1270, 920, 44, "烦躁", c="red", d=0.4) + BIG(a, 1600, 500, "700 遍", c="ink", d=0.8, s=100)
B.append(E)
# 35 小导第七百遍一样耐心
a = 35
els, i = G(a, 760, 940, 1.5)
E = els + bubble(1100, 280, 620, 140, a, "您好，请问…", s=56, c="green")
E += BIG(a, 1400, 640, "第 700 遍", c="blue", d=0.8, s=96) + star(a, 1700, 780, 1.2) + star(a, 1150, 800, 1.5)
B.append(E)
# 36 不累，不烦
a = 36
els, i = G(a, 960, 940, 1.6)
E = els + check(a, 520, 420, d=0.6) + check(a, 1400, 420, d=1.2)
E += T(a, 520, 560, 72, "不累", c="green", d=0.6) + T(a, 1400, 560, 72, "不烦", c="green", d=1.2) + star(a, 960, 180, 1.6)
B.append(E)
# 37 总账：时间差
a = 37
E = BIG(a, 960, 160, "算总账", c="ink", d=0.0, s=90)
m1, m2 = uid("mic"), uid("mic")
E += [O(a, 700, 600, 28, c="blue", fill="blue", idp=m1), O(a, 1220, 600, 28, c="blue", fill="blue", idp=m2), pulse(a, m1, 0.5), pulse(a, m2, 1.0)]
for k in range(2):
    sw_ = uid("sw")
    E += [P(a, f"M300,{520 + 20 * k} Q360,{580 + 20 * k} 300,{660 + 20 * k}", c="red", w=6, idp=sw_), sh(a, sw_, 1000, 0, 0.2 + 0.3 * k, 1.4)]
E += T(a, 960, 820, 64, "方向 ← 时间差", c="blue", d=1.0)
B.append(E)
# 38 听清 ← 波束成形
a = 38
els, i = G(a, 380, 940, 1.0)
E = els
bm = uid("beam")
E += [P(a, "M450,600 L1500,420 L1500,800 Z", c="gold", w=4, fill="gold", idp=bm), pop(a, bm, 0.2), wig(a, bm, (450, 600), 2, 0.8)]
pp, j = person(a, 1450, 860, 0.9, arms="up")
E += pp + T(a, 1100, 260, 64, "听清 ← 波束成形", c="gold", d=0.6)
B.append(E)
# 39 答对 ← 开卷；不乱答 ← 边界
a = 39
bk = uid("book")
E = [P(a, "M260,360 L520,390 L780,360 L780,700 L520,730 L260,700 Z M520,390 L520,730", c="ink", w=6, idp=bk), pop(a, bk, 0.2), wig(a, bk, (520, 730), 2, 1)]
E += T(a, 520, 840, 60, "答对 ← 开卷", c="blue", d=0.4)
els, i = G(a, 1300, 940, 1.2)
E += els + check(a, 1600, 400, d=0.8)
B.append(E)
a = 39.5
els, i = G(a, 600, 940, 1.2, mood="worried")
E = els
st_ = uid("stop")
E += [O(a, 1400, 540, 150, c="red", sw=8, idp=st_), P(a, "M1295,645 L1505,435", c="red", w=10, idp=st_), pop(a, st_, 0.2), pulse(a, st_, 0.8)]
E += T(a, 1400, 840, 60, "不乱答 ← 边界", c="red", d=0.4)
B.append(E)
# 40 友情提示 1
a = 40
E = T(a, 960, 200, 80, "友情提示", c="red", d=0.0) + T(a, 960, 400, 60, "700 问：报道的数字", c="ink", d=0.6)
els, i = G(a, 1650, 1000, 0.7)
E += els + star(a, 300, 760, 0.8) + star(a, 520, 860, 1.2)
B.append(E)
a = 40.5
E = bar(a, 500, 860, 160, 300, "blue", d=0.1) + bar(a, 760, 860, 160, 420, "gold", d=0.3)
E += T(a, 580, 920, 44, "分贝", c="blue", d=0.1) + T(a, 840, 920, 44, "信噪比", c="gold", d=0.3)
E += BIG(a, 1400, 480, "估算", c="gold", d=0.5, s=140) + T(a, 1400, 620, 52, "（我们算的）", c="muted", d=0.9) + star(a, 1700, 300, 0.8)
B.append(E)
# 41 友情提示 2
a = 41
gr = uid("gear")
E = [{"t": "icon", "at": a, "id": gr, "name": "gear", "x": 700, "y": 500, "size": 280, "c": "muted"}, spin(a, gr, (700, 500), 30), pop(a, gr, 0.2)]
lk = uid("lock")
E += [R(a, 650, 490, 100, 80, c="red", fill="red", idp=lk), P(a, "M670,490 L670,450 Q700,410 730,450 L730,490", c="red", w=7, idp=lk), pop(a, lk, 0.8), pulse(a, lk, 1.4)]
E += T(a, 1400, 440, 60, "算法：未公开", c="red", d=0.6) + T(a, 1400, 580, 60, "讲的是通用原理", c="blue", d=1.8)
E += star(a, 1700, 760, 2.0)
B.append(E)
# 42 厕所在左手边
a = 42
els, i = G(a, 1300, 940, 1.4, moves=False)
E = els + [wig(a, i + "_arm", (1300 + 62 * 1.4, 940 - 260 * 1.4), 10, 2), bob(a, i + "*", 8, 1.0), pulse(a, i + "_ant", 0.4)]
E += arr(a, 1000, 520, 300, 520, c="green", w=9, d=0.6, dur=0.8)
wc = uid("wc")
E += [R(a, 160, 300, 180, 140, c="blue", sw=6, idp=wc), pop(a, wc, 1.2), bob(a, wc, 8, 1.6)]
E += T(a, 250, 390, 56, "WC", c="blue", d=1.2) + T(a, 640, 460, 52, "直走 20 米", c="green", d=1.4)
B.append(E)
# 43 第七百零一遍
a = 43
els, i = G(a, 760, 940, 1.5)
E = els + BIG(a, 1400, 480, "#701", c="red", d=0.4, s=150) + T(a, 1400, 620, 56, "今天第七百零一遍", c="ink", d=1.0)
for k in range(4):
    E += star(a, 1150 + 170 * k, 820 - 40 * (k % 2), 0.8 + 0.2 * k)
B.append(E)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say=SAY)
