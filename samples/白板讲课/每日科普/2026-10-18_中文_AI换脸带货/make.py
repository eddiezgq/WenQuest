"""每日科普 2026-10-18（中文）：《吴越被AI换脸，怎么识破？》
新闻：2026-10-18 凌晨约 3 点，演员吴越在微博怒斥有人用 AI 伪造她的脸和声音带货护肤品，要求“如数奉还”骗款；视频台词“这个产品不是他们找我，
是我找他们”，画面下方标了“含AI生成内容”但不显眼；同一视频末尾还出现邓亚萍的“带货”画面；温峥嵘此前也遇到 AI 盗播，说“很难证明我是我”；
据《每日经济新闻》报道约 1280 元即可在直播中实时换脸（新浪新闻 k.sina.com.cn/article_7879776328_1d5abd84806802e4li.html；
新浪科技热点小时报 10-18 17时第 1 条 k.sina.com.cn/article_7857201856_1d45362c001908ri28.html）。
微信视频号回应：账号已永久封禁、内容清空（新浪科技热点小时报 10-18 15时第 8 条 k.sina.com.cn/article_7857201856_1d45362c001908rhq8.html）。
《人工智能生成合成内容标识办法》2025-09-01 起施行。
科学：经典换脸 = 共享编码器把脸压成“表情、角度”的少量数（笔记），再用另一个人的解码器按笔记重画；声音克隆几十秒录音即可学音色（常见说法）。
破绽是“常见情况”，不是万能检测法；“破绽正在被补上”是趋势判断。
角色：小画（AI 画像师，popkit.cute_bot + 画笔），贯穿的梗：“我是我”。没有手。
    python3 make.py <kokoro 模型目录> | --fake | --boards-only   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_bot, stick  # noqa: E402

S = [
 ("凌晨三点，演员吴越发了一条很生气的微博：|视频里那个卖护肤品的“我”，不是我！",
  "3 a.m.: actress Wu Yue posts an angry message. | The 'me' selling skincare in that video is not me!"),
 ("脸是她的，声音也像她的，可全是AI做的。", "Her face, her voice, almost. All made by AI."),
 ("视频里的“她”还说：这个产品不是他们找我，是我找他们。", "The fake her even says: they didn't come to me, I went to them."),
 ("今天的问题：AI是怎么偷走一张脸的？|你又该怎么识破？", "Today's question: how does AI steal a face? | And how do you catch it?"),
 ("再烧一点：连明星本人都很难证明“我是我”，我们普通人看什么？", "Harder one: if even a star can't prove she's herself, what do the rest of us look at?"),
 ("先认识今天的主角：小画，一个AI画像师。", "Meet our star: Doodle, an AI portrait painter."),
 ("小画干活分两步。第一步：看你的脸，只记笔记。", "Doodle works in two steps. Step one: look at a face, and only take notes."),
 ("笔记上没有长相，只有几个数：|嘴角翘多少，头往哪边转，眼睛眨没眨。", "The notes have no looks, just numbers: | how much you smile, which way you turn, whether you blink."),
 ("第二步：拿着这份笔记，照另一个人的样子，重新画一张脸。", "Step two: take those notes and redraw them as somebody else's face."),
 ("这就是换脸：主播在镜头前笑，|小画就画出一个“吴越”在笑。", "That's a face swap. The streamer smiles on camera, | and Doodle paints a 'Wu Yue' smiling."),
 ("打个比方：同一份舞谱，交给两个舞者，跳出来是两个人。", "Think of a dance score: same steps, two dancers, two different people."),
 ("声音也一样。常见的说法是：|几十秒录音，就能学会一个人的音色。", "Voices work the same way. A common claim: | a few dozen seconds of audio is enough to copy one."),
 ("而且据报道，大约一千二百八十元，|就能在直播里实时换脸。", "And reportedly, about 1,280 yuan | buys you a live face swap during a stream."),
 ("反转一：这么便宜，被冒充的就不止吴越。", "Twist one: that cheap, and it's not just Wu Yue."),
 ("同一个视频的结尾，还冒出了邓亚萍在“带货”。", "The same video ends with table tennis legend Deng Yaping 'selling' stuff too."),
 ("演员温峥嵘也遇到过AI盗播，她说：我很难证明我是我。", "Actress Wen Zhengrong hit AI copycats too. She said: it's hard to prove I am me."),
 ("那小画有没有画不好的地方？有，下面是常见破绽。", "So does Doodle ever mess up? Yes. Here are common tells."),
 ("破绽一：让人侧过脸。小画多半是看正脸学的，|转到九十度，脸容易糊。", "Tell one: turn sideways. Doodle mostly learned from front faces. | At ninety degrees, the face can smear."),
 ("破绽二：用手在脸前挡一下。手和脸叠在一起，小画常常画穿帮。", "Tell two: wave a hand in front of the face. Hand plus face often breaks the painting."),
 ("破绽三：看牙齿、眼镜边、耳环。细节越多，越容易出错。", "Tell three: teeth, glasses rims, earrings. More detail, more mistakes."),
 ("破绽四：光从左边来，影子也在左边。|光影对不上，就要多个心眼。", "Tell four: light from the left, shadow also on the left. | If light and shadow disagree, be suspicious."),
 ("破绽五：嘴型和声音，对不齐。", "Tell five: lips and voice out of sync."),
 ("反转二，最反直觉：这些破绽，正在一个一个被补上。", "Twist two, the weird one: these tells are being fixed, one by one."),
 ("AI一年比一年画得好。|靠眼睛找破绽，就像跟魔术师比手快。", "AI paints better every year. | Spotting tells by eye is like out-speeding a magician."),
 ("所以，最靠得住的不是看脸，是看渠道。", "So the safest check isn't the face. It's the channel."),
 ("看账号：有没有官方认证，是不是本人的号。", "Check the account: is it verified, is it really hers?"),
 ("看话术：“今天最后一天”，“只剩最后几单”。|它在催你，你就慢一点。", "Check the pitch: 'last day!', 'only a few left!' | When it rushes you, slow down."),
 ("看付款：叫你私下转账的，一律不信。", "Check the payment: anyone asking for a private transfer, no."),
 ("还有一条规矩：从二零二五年九月一日起，AI生成的内容必须加标识。", "One more rule: since September 1, 2025, China requires AI-made content to be labeled."),
 ("这次的视频下面也写了“含AI生成内容”，|只是字很小，很不显眼。", "This video did say 'contains AI content', | in tiny, easy-to-miss print."),
 ("所以刷视频时，多看一眼角落。", "So when you scroll, glance at the corners."),
 ("后来，涉事账号已被永久封禁，内容清空。", "The account has since been banned for good, its videos wiped."),
 ("友情提示：哪个破绽管用，因视频而异。|今天说的是常见情况，不是万能检测法。", "Friendly fine print: which tells work varies by video. | These are common cases, not a magic detector."),
 ("回到开头：明星怎么证明我是我？", "Back to the start: how does a star prove she's herself?"),
 ("答案是：不用证明脸，要证明渠道。|真吴越，在她自己认证的账号里。", "Answer: don't prove the face, prove the channel. | The real Wu Yue lives on her own verified account."),
 ("小画说：我能画出任何一张脸，|可我登不上你的账号。", "Doodle says: I can paint any face. | I just can't log into your account."),
]
TITLE = {"zh": "吴越被AI换脸，怎么识破？", "en": "Wu Yue was deepfaked. How do you catch it?"}
SAY = {"AI": "A I"}


def face(at, cx, cy, r, mood="happy", c="ink", hair="ink", moves=True, fill=None):
    """A round cute face; '<id>*' moves it, '<id>_m' is the mouth, '<id>_e' the eyes."""
    i = uid("fc")
    E = [O(at, cx, cy, r, c=c, idp=i + "_b", sw=5, fill=fill),
         P(at, f"M{cx - r},{cy - 0.05 * r} Q{cx - 1.05 * r},{cy - 1.35 * r} {cx},{cy - 1.12 * r} Q{cx + 1.05 * r},{cy - 1.35 * r} {cx + r},{cy - 0.05 * r}",
           c=hair, w=8, idp=i + "_h")]
    for s in (-1, 1):
        E.append(O(at, cx + s * 0.35 * r, cy - 0.1 * r, 0.09 * r, c="ink", fill="ink", idp=i + "_e"))
        if mood == "angry":
            E.append(P(at, f"M{cx + s * 0.55 * r},{cy - 0.38 * r} L{cx + s * 0.18 * r},{cy - 0.25 * r}", c="red", w=6, idp=i + "_e"))
    if mood == "happy":
        E.append(P(at, f"M{cx - 0.3 * r},{cy + 0.3 * r} Q{cx},{cy + 0.58 * r} {cx + 0.3 * r},{cy + 0.3 * r}", c="red", w=6, idp=i + "_m"))
    elif mood == "o":
        E.append(O(at, cx, cy + 0.4 * r, 0.13 * r, c="red", idp=i + "_m", sw=5))
    else:
        E.append(P(at, f"M{cx - 0.28 * r},{cy + 0.45 * r} Q{cx},{cy + 0.3 * r} {cx + 0.28 * r},{cy + 0.45 * r}", c="red", w=6, idp=i + "_m"))
    if moves:
        E += [bob(at, i + "*", 0.05 * r, 1.0), {"t": "move", "at": at, "kind": "pulse", "targets": [i + "_e"], "delay": 1.2, "dur": 0.3}]
    return E, i


def painter(at, cx, cy, k=1.0, mood="happy"):
    """小画: cute_bot + a beret + a wiggling brush. '<id>*' moves it."""
    i = uid("xh")
    E = cute_bot(cx, cy, k, at, idp=i, mood=mood)
    E += [P(at, f"M{cx - 80 * k},{cy - 420 * k} Q{cx},{cy - 490 * k} {cx + 85 * k},{cy - 425 * k} Z", c="red", w=4, idp=i + "_hat", fill="red")]
    E += [P(at, f"M{cx + 90 * k},{cy - 170 * k} L{cx + 170 * k},{cy - 300 * k}", c="ink", w=7, idp=i + "_br"),
          O(at, cx + 172 * k, cy - 305 * k, 14 * k, c="blue", fill="blue", idp=i + "_br"),
          wig(at, i + "_br", (cx + 90 * k, cy - 170 * k), 18, 2.2)]
    return E, i


def phone(at, cx, cy, w=380, h=640, d=None):
    i = uid("ph")
    E = [R(at, cx - w / 2, cy - h / 2, w, h, c="ink", idp=i, sw=7), R(at, cx - 40, cy - h / 2 + 18, 80, 14, c="ink", fill="ink", idp=i)]
    if d is not None:
        E.append(pop(at, i, d))
    return E, i


def coins(at, x, y, n=3, d=0.3, dx=0, dy=-200):
    E = []
    for k in range(n):
        c = uid("cn")
        E += [O(at, x + 50 * k, y - 20 * k, 30, c="gold", fill="gold", idp=c), sh(at, c, dx, dy, d + 0.3 * k, 0.9)]
    return E


def note(at, x, y, w, h, lines, d=0.2):
    i = uid("nt")
    E = [R(at, x, y, w, h, c="ink", idp=i, sw=4), pop(at, i, d), wig(at, i, (x + w / 2, y), 2.5, 0.8)]
    for n, (s, c) in enumerate(lines):
        E += T(at, x + w / 2, y + 80 + 70 * n, 46, s, c=c, d=d + 0.4 + 0.35 * n)
    return E


def sparkle(at, pts, d=0.0):
    E = []
    for n, (x, y) in enumerate(pts):
        E += star(at, x, y, d + 0.25 * n)
    return E


B = []
# 0 3 a.m. angry post
a = 0
f, i = face(a, 620, 480, 170, mood="angry")
E = f + [wig(a, i + "_b", (620, 480), 4, 3.0)]
cl = uid("cl")
E += [{"t": "icon", "at": a, "id": cl, "name": "clock", "x": 1450, "y": 330, "size": 260, "c": "ink"}, pop(a, cl, 0.0), wig(a, cl, (1450, 330), 6, 2.0)]
mn = uid("mn")
E += [{"t": "icon", "at": a, "id": mn, "name": "moon", "x": 1720, "y": 200, "size": 150, "c": "gold"}, bob(a, mn, 10, 0.8)]
E += BIG(a, 1450, 620, "3:00", c="red", d=0.2, s=150) + sparkle(a, [(300, 220), (920, 240)], 0.4)
B.append(E)
# 0.5 not me
a = 0.5
ph, p = phone(a, 1300, 470, d=0.0)
f, j = face(a, 1300, 430, 120, mood="happy", hair="gold")
E = ph + f + [wig(a, p, (1300, 790), 2, 1.5)]
f2, i = face(a, 520, 470, 150, mood="angry")
E += f2 + [rot(a, i + "*", -8, (520, 620), 0.3, 0.3)] + cross(a, 1300, 430, d=0.9) + BIG(a, 520, 800, "不是我！", c="red", d=0.5, s=120)
E += arr(a, 720, 470, 1060, 470, d=0.4)
B.append(E)
# 1 face + voice, all AI
a = 1
f, i = face(a, 520, 420, 150, hair="gold")
E = f
spk = uid("spk")
E += [{"t": "icon", "at": a, "id": spk, "name": "speaker", "x": 1000, "y": 420, "size": 200, "c": "blue"}, pop(a, spk, 0.5), pulse(a, spk, 1.0)]
for n in range(3):
    s = uid("sw")
    E += [P(a, f"M{1110 + 40 * n},{350 - 20 * n} Q{1160 + 40 * n},420 {1110 + 40 * n},{490 + 20 * n}", c="blue", w=5, idp=s), wig(a, s, (1110, 420), 4, 2 + n)]
ch = uid("chip")
E += [{"t": "icon", "at": a, "id": ch, "name": "chip", "x": 1550, "y": 420, "size": 260, "c": "red"}, pop(a, ch, 1.0), spin(a, ch, (1550, 420), 30)]
E += BIG(a, 960, 800, "全是 AI", c="red", d=1.2, s=130)
B.append(E)
# 2 the fake line
a = 2
ph, p = phone(a, 560, 470)
f, i = face(a, 560, 420, 120, hair="gold")
E = ph + f + [{"t": "move", "at": a, "kind": "wiggle", "targets": [i + "_m"], "pivot": [560, 470], "amp": 10, "hz": 4}]
bt = uid("bt")
E += [R(a, 470, 640, 180, 70, c="green", fill="green", idp=bt), pulse(a, bt, 0.5), bob(a, bt, 4, 2.0)]
E += T(a, 1300, 330, 60, "“不是他们找我，", c="ink", d=0.3) + T(a, 1300, 450, 60, "是我找他们。”", c="ink", d=1.0)
E += BIG(a, 1300, 680, "假的", c="red", d=1.6, s=130) + coins(a, 1600, 800, 3, 0.4)
B.append(E)
# 3 how does AI steal a face
a = 3
f, i = face(a, 640, 460, 160, hair="gold")
E = f
pr, j = painter(a, 1350, 820, 0.9, mood="happy")
E += pr + [sh(a, i + "*", 380, 0, 0.6, 1.2)]
q = uid("q")
E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 960, "y": 200, "size": 200, "c": "red"}, pop(a, q, 0.2), pulse(a, q, 1.2)]
E += BIG(a, 520, 820, "偷脸？", c="red", d=0.4, s=120)
B.append(E)
# 3.5 how to catch it
a = 3.5
mg = uid("mg")
E = [{"t": "icon", "at": a, "id": mg, "name": "magnifier", "x": 700, "y": 420, "size": 360, "c": "ink"}, pop(a, mg, 0.0),
     sh(a, mg, 500, 0, 0.4, 1.4), rot(a, mg, 15, (700, 420), 1.6, 0.4)]
f, i = face(a, 1300, 420, 140, hair="gold")
E += f + [wig(a, i + "*", (1300, 560), 6, 2.5)] + BIG(a, 960, 800, "怎么识破？", c="blue", d=0.6, s=120) + sparkle(a, [(300, 200), (1700, 200)], 0.2)
B.append(E)
# 4 how to prove I am me
a = 4
f1, i1 = face(a, 600, 440, 140, hair="gold")
f2, i2 = face(a, 1320, 440, 140, hair="gold")
E = f1 + f2 + [sh(a, i1 + "*", 60, 0, 0.3, 0.6), sh(a, i2 + "*", -60, 0, 0.3, 0.6)]
eq = uid("eq")
E += [P(a, "M920,420 L1000,420 M920,460 L1000,460", c="red", w=9, idp=eq), pop(a, eq, 0.8), pulse(a, eq, 1.4)]
E += BIG(a, 960, 220, "我 = 我？", c="ink", d=0.2, s=110) + BIG(a, 960, 780, "怎么证明？", c="red", d=1.4, s=110)
q = uid("q")
E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 1700, "y": 640, "size": 160, "c": "red"}, bob(a, q, 12, 1.4)]
B.append(E)
# 5 meet 小画
a = 5
pr, i = painter(a, 960, 820, 1.4)
E = pr + sparkle(a, [(500, 260), (1450, 260), (1550, 520)], 0.2) + BIG(a, 520, 640, "小画", c="blue", d=0.4, s=140)
E += T(a, 1500, 760, 52, "（AI画像师）", c="muted", d=1.0) + [rot(a, i + "*", 6, (960, 820), 1.2, 0.5)]
B.append(E)
# 6 step one: take notes
a = 6
f, i = face(a, 460, 450, 150)
pr, j = painter(a, 1000, 820, 0.9)
E = f + pr + BIG(a, 460, 160, "第一步", c="blue", d=0.2, s=90)
E += note(a, 1300, 240, 420, 460, [("只记笔记", "ink")], d=0.6) + arr(a, 640, 450, 820, 450, d=0.4)
pn = uid("pn")
E += [P(a, "M1560,640 L1660,520", c="ink", w=8, idp=pn), wig(a, pn, (1560, 640), 15, 3)]
B.append(E)
# 7 notes: no looks, just numbers
a = 7
E = note(a, 1120, 200, 560, 560, [("嘴角 +0.7", "red"), ("头 左转 15°", "blue"), ("眨眼 1", "green"), ("……", "muted")], d=0.1)
f, i = face(a, 520, 460, 160, moves=False)
E += f + [bob(a, i + "*", 8, 1.0), rot(a, i + "*", -15, (520, 460), 0.9, 0.5),
          {"t": "move", "at": a, "kind": "pulse", "targets": [i + "_m"], "delay": 0.5, "dur": 0.5}]
cx_ = uid("nolook")
E += [P(a, "M300,240 L740,700", c="red", w=7, idp=cx_), pop(a, cx_, 2.0)] + arr(a, 760, 460, 1080, 460, c="blue", d=0.2)
B.append(E)
# 7.5 smile / turn / blink, three dials
a = 7.5
E = []
for n, (lab, c) in enumerate([("嘴角", "red"), ("转头", "blue"), ("眨眼", "green")]):
    x = 420 + 540 * n
    dl, nd = uid("dl"), uid("nd")
    E += [O(a, x, 440, 170, c=c, idp=dl, sw=6), pop(a, dl, 0.2 * n),
          P(a, f"M{x},440 L{x},300", c="ink", w=9, idp=nd), rot(a, nd, 60 - 50 * n, (x, 440), 0.4 + 0.4 * n, 0.6), wig(a, nd, (x, 440), 5, 1.5 + n)]
    E += T(a, x, 720, 64, lab, c=c, d=0.2 + 0.3 * n)
E += BIG(a, 960, 860, "几个数", c="ink", d=1.4, s=90)
B.append(E)
# 8 step two: redraw as someone else
a = 8
E = note(a, 240, 260, 380, 400, [("+0.7", "red"), ("15°", "blue"), ("1", "green")], d=0.0)
pr, i = painter(a, 960, 820, 0.9)
E += pr + arr(a, 640, 460, 800, 460, d=0.3) + BIG(a, 960, 160, "第二步", c="blue", d=0.1, s=90)
f, j = face(a, 1500, 450, 150, hair="gold", fill=None)
E += f + [pop(a, j + "_b", 0.9), pop(a, j + "_h", 1.2), pop(a, j + "_m", 1.5)] + sparkle(a, [(1720, 260)], 1.6)
B.append(E)
# 9 the streamer smiles
a = 9
cam = uid("cam")
E = [R(a, 300, 360, 200, 140, c="ink", fill="ink", idp=cam), O(a, 400, 430, 46, c="red", idp=cam), pulse(a, cam, 0.3), wig(a, cam, (400, 430), 3, 1.0)]
f, i = face(a, 900, 440, 150, mood="happy")
E += f + T(a, 900, 720, 56, "主播", c="muted", d=0.2) + [rot(a, i + "*", 10, (900, 600), 0.6, 0.4), rot(a, i + "*", -10, (900, 600), 1.2, 0.4)]
for n in range(3):
    s = uid("rec")
    E += [O(a, 1350 + 60 * n, 260, 16, c="red", fill="red", idp=s), pulse(a, s, 0.3 * n)]
E += BIG(a, 1550, 520, "笑", c="red", d=0.8, s=150)
B.append(E)
# 9.5 小画 paints a "Wu Yue" smiling
a = 9.5
f, i = face(a, 520, 440, 130, mood="happy")
pr, j = painter(a, 960, 820, 0.85)
ph, p = phone(a, 1480, 470, d=0.0)
f2, k = face(a, 1480, 430, 120, hair="gold")
E = f + pr + ph + f2 + [pop(a, k + "*", 0.8)] + arr(a, 680, 440, 820, 440, d=0.2) + arr(a, 1100, 440, 1260, 440, d=0.6)
E += T(a, 1480, 870, 56, "“吴越”", c="red", d=1.1)
B.append(E)
# 10 dance score, two dancers
a = 10
sc = uid("sc")
E = [R(a, 760, 160, 400, 220, c="ink", idp=sc), pop(a, sc, 0.0), wig(a, sc, (960, 160), 2, 0.9)]
for n in range(3):
    E += T(a, 820 + 140 * n, 290, 70, "♪", c="blue", d=0.2 + 0.2 * n)
d1, d2 = uid("dn"), uid("dn")
E += stick(560, 820, 1.4, a, idp=d1, arms="up") + stick(1360, 820, 1.4, a, idp=d2, arms="up")
E += [wig(a, d1, (560, 820), 12, 1.6), wig(a, d2, (1360, 820), 12, 1.6), sh(a, d1, -60, 0, 0.6, 0.8), sh(a, d2, 60, 0, 0.6, 0.8)]
E += arr(a, 860, 400, 640, 520, c="blue", d=0.5) + arr(a, 1060, 400, 1280, 520, c="blue", d=0.7)
E += BIG(a, 960, 700, "一谱两人", c="red", d=1.2, s=90)
B.append(E)
# 11 voice too
a = 11
spk = uid("spk")
E = [{"t": "icon", "at": a, "id": spk, "name": "speaker", "x": 520, "y": 440, "size": 280, "c": "blue"}, pop(a, spk, 0.0), pulse(a, spk, 0.8)]
wv = uid("wv")
E += [P(a, "M780,440 Q840,300 900,440 Q960,580 1020,440 Q1080,300 1140,440 Q1200,580 1260,440 Q1320,300 1380,440", c="blue", w=6, idp=wv),
      wig(a, wv, (1080, 440), 3, 3), sh(a, wv, 60, 0, 0.2, 1.2)]
pr, i = painter(a, 1640, 820, 0.7)
E += pr + BIG(a, 960, 160, "声音也一样", c="ink", d=0.2, s=90)
B.append(E)
# 11.5 dozens of seconds
a = 11.5
cl = uid("cl")
E = [{"t": "icon", "at": a, "id": cl, "name": "clock", "x": 520, "y": 440, "size": 320, "c": "ink"}, pop(a, cl, 0.0)]
hd = uid("hd")
E += [P(a, "M520,440 L520,330", c="red", w=9, idp=hd), spin(a, hd, (520, 440), 90)]
E += BIG(a, 1200, 380, "几十秒", c="red", d=0.3, s=150)
mic = uid("mic")
E += [R(a, 1150, 560, 70, 130, c="ink", idp=mic), P(a, "M1185,690 L1185,760 M1140,760 L1230,760", c="ink", w=6, idp=mic), pop(a, mic, 0.7), bob(a, mic, 8, 1.4)]
E += T(a, 1500, 640, 56, "（常见说法）", c="muted", d=1.0) + sparkle(a, [(1650, 240)], 1.2)
B.append(E)
# 12 reportedly 1280 yuan
a = 12
E = BIG(a, 900, 440, "1280 元", c="red", d=0.1, s=160) + coins(a, 1450, 700, 4, 0.3, dx=0, dy=-220)
E += T(a, 900, 640, 56, "据报道", c="muted", d=0.6)
tg = uid("tg")
E += [P(a, "M300,200 L520,200 L560,260 L520,320 L300,320 Z", c="gold", w=6, idp=tg), pop(a, tg, 0.4), wig(a, tg, (300, 260), 6, 1.6)]
E += bubbles(a, 1700, 860, n=3, d=0.2, c="gold")
B.append(E)
# 12.5 live face swap
a = 12.5
ph, p = phone(a, 960, 470)
f, i = face(a, 960, 420, 120)
f2, j = face(a, 960, 420, 120, hair="gold", moves=False)
E = ph + f + f2 + [pop(a, j + "*", 0.8), sh(a, i + "*", -400, 0, 0.6, 0.6)]
lv = uid("lv")
E += [R(a, 840, 170, 120, 50, c="red", fill="red", idp=lv), pulse(a, lv, 0.2), bob(a, lv, 3, 2)]
E += T(a, 900, 200, 36, "直播", c="white", d=0.2) + BIG(a, 1520, 470, "实时", c="blue", d=1.1, s=130)
E += sparkle(a, [(400, 300), (420, 700)], 0.9)
B.append(E)
# 13 twist one: not just Wu Yue
a = 13
E = BIG(a, 960, 160, "反转一", c="red", d=0.0, s=100)
for n in range(4):
    f, i = face(a, 420 + 360 * n, 500, 110, hair=["gold", "ink", "blue", "red"][n])
    E += f + [pop(a, i + "_b", 0.3 + 0.3 * n)]
E += BIG(a, 960, 800, "不止一个", c="ink", d=1.4, s=100)
B.append(E)
# 14 Deng Yaping at the end
a = 14
ph, p = phone(a, 1300, 470)
f, i = face(a, 1300, 420, 110, hair="ink")
E = ph + f
pd = uid("pd")
E += [O(a, 560, 420, 110, c="red", fill="red", idp=pd), P(a, "M560,530 L560,700", c="ink", w=12, idp=pd), rot(a, pd, 30, (560, 700), 0.3, 0.4),
      rot(a, pd, -20, (560, 700), 0.8, 0.4)]
ball = uid("ball")
E += [O(a, 760, 300, 26, c="gold", fill="gold", idp=ball), sh(a, ball, 300, 120, 0.5, 0.6), bob(a, ball, 14, 2.4)]
E += T(a, 1300, 870, 56, "“带货”", c="red", d=1.0) + T(a, 560, 820, 50, "视频结尾", c="muted", d=0.2)
B.append(E)
# 15 Wen Zhengrong: hard to prove I am me
a = 15
f1, i1 = face(a, 560, 460, 140, mood="o")
f2, i2 = face(a, 1060, 460, 140, mood="happy")
f3, i3 = face(a, 1500, 460, 140, mood="happy")
E = f1 + f2 + f3 + [wig(a, i2 + "*", (1060, 600), 6, 2), wig(a, i3 + "*", (1500, 600), 6, 2.4)]
E += BIG(a, 960, 800, "我是我？", c="red", d=0.8, s=120) + T(a, 1280, 220, 52, "AI 盗播", c="muted", d=0.3)
E += [pulse(a, i1 + "_b", 1.4)]
B.append(E)
# 16 common tells
a = 16
pr, i = painter(a, 600, 820, 1.0, mood="sad")
E = pr + [rot(a, i + "*", -8, (600, 820), 0.4, 0.4)]
blob = uid("blob")
E += [P(a, "M1200,300 Q1400,200 1500,360 Q1620,520 1420,600 Q1240,660 1180,520 Q1100,400 1200,300 Z", c="red", w=6, idp=blob),
      pop(a, blob, 0.6), wig(a, blob, (1350, 450), 6, 1.6)]
E += BIG(a, 1350, 800, "常见破绽", c="red", d=1.0, s=100) + T(a, 1350, 450, 90, "糊", c="red", d=0.9)
B.append(E)
# 17 tell one: turn sideways
a = 17
E = BIG(a, 960, 140, "破绽一：侧脸", c="blue", d=0.0, s=80)
f, i = face(a, 960, 500, 170, hair="gold")
E += f + [rot(a, i + "*", 0, (960, 500), 0, 0.1)]
for s in (-1, 1):
    a_ = uid("ar")
    E += [P(a, f"M{960 + s * 260},380 Q{960 + s * 340},500 {960 + s * 260},620", c="blue", w=6, idp=a_), pop(a, a_, 0.4), wig(a, a_, (960 + s * 300, 500), 6, 1.4)]
E += [{"t": "move", "at": a, "kind": "shift", "targets": [i + "_e"], "dx": 60, "dy": 0, "delay": 1.0, "dur": 0.6}]
B.append(E)
# 17.5 at 90 degrees the face smears
a = 17.5
f, i = face(a, 700, 480, 170, hair="gold")
E = f + [{"t": "move", "at": a, "kind": "wiggle", "targets": [i + "_b"], "pivot": [700, 480], "amp": 14, "hz": 6}]
for n in range(4):
    s = uid("smr")
    E += [P(a, f"M{820 + 30 * n},{360 + 60 * n} L{1000 + 30 * n},{340 + 60 * n}", c="muted", w=10, idp=s), pop(a, s, 0.3 + 0.2 * n), wig(a, s, (900, 480), 5, 3)]
E += BIG(a, 1400, 440, "90°", c="red", d=0.2, s=150) + T(a, 1400, 650, 64, "容易糊", c="red", d=1.0)
B.append(E)
# 18 tell two: hand in front
a = 18
E = BIG(a, 960, 140, "破绽二：手挡脸", c="blue", d=0.0, s=80)
f, i = face(a, 960, 520, 180, hair="gold")
hd = uid("hd")
E += f + [P(a, "M640,800 L700,560 M700,560 L680,470 M700,560 L720,460 M700,560 L760,470 M700,560 L790,500", c="ink", w=12, idp=hd),
          sh(a, hd, 260, -40, 0.4, 0.6), sh(a, hd, -260, 40, 1.2, 0.6)]
gl = uid("gl")
E += [P(a, "M1080,420 L1180,380 L1150,500 L1240,470", c="red", w=7, idp=gl), pop(a, gl, 0.9), wig(a, gl, (1150, 450), 8, 4)]
E += [{"t": "move", "at": a, "kind": "wiggle", "targets": [i + "_b"], "pivot": [960, 520], "amp": 8, "hz": 5}]
B.append(E)
# 19 tell three: teeth, glasses, earrings
a = 19
E = BIG(a, 960, 140, "破绽三：细节", c="blue", d=0.0, s=80)
f, i = face(a, 960, 520, 200, hair="gold")
gs = uid("gs")
E += f + [O(a, 890, 500, 50, c="ink", idp=gs, sw=6), O(a, 1030, 500, 50, c="ink", idp=gs, sw=6), P(a, "M940,500 L980,500", c="ink", w=6, idp=gs),
          pop(a, gs, 0.3), wig(a, gs, (960, 500), 4, 2.5)]
er = uid("er")
E += [O(a, 750, 600, 22, c="gold", fill="gold", idp=er), O(a, 1170, 600, 22, c="gold", fill="gold", idp=er), wig(a, er, (960, 560), 10, 1.8), pop(a, er, 0.8)]
mg = uid("mg")
E += [{"t": "icon", "at": a, "id": mg, "name": "magnifier", "x": 1500, "y": 640, "size": 220, "c": "red"}, pop(a, mg, 1.2), bob(a, mg, 10, 1.4)]
E += T(a, 460, 640, 56, "牙齿", c="red", d=1.4)
B.append(E)
# 20 tell four: light from left, shadow also on left
a = 20
sun = uid("sun")
E = [{"t": "icon", "at": a, "id": sun, "name": "sun", "x": 300, "y": 300, "size": 220, "c": "gold"}, spin(a, sun, (300, 300), 20), pop(a, sun, 0.0)]
for n in range(3):
    r_ = uid("ray")
    E += [P(a, f"M420,{300 + 60 * n} L700,{360 + 60 * n}", c="gold", w=5, idp=r_), pop(a, r_, 0.2 + 0.15 * n), wig(a, r_, (420, 360), 2, 2)]
f, i = face(a, 1000, 480, 170)
sd = uid("sd")
E += f + [P(a, "M830,400 Q790,500 840,600 Q880,500 830,400 Z", c="muted", w=4, idp=sd, fill="muted"), pop(a, sd, 1.0), pulse(a, sd, 1.6)]
E += BIG(a, 1550, 480, "影子？", c="red", d=1.1, s=110) + BIG(a, 960, 140, "破绽四：光影", c="blue", d=0.0, s=80)
B.append(E)
# 20.5 be suspicious
a = 20.5
f, i = face(a, 700, 480, 160, mood="o")
E = f + [rot(a, i + "*", 12, (700, 640), 0.2, 0.4)]
for n in range(3):
    q = uid("q")
    E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 1100 + 220 * n, "y": 340 + 60 * (n % 2), "size": 150, "c": "red"}, pop(a, q, 0.3 + 0.3 * n), bob(a, q, 10, 1.2 + 0.3 * n)]
E += BIG(a, 1320, 780, "多个心眼", c="red", d=1.2, s=110)
B.append(E)
# 21 tell five: lips vs voice
a = 21
f, i = face(a, 640, 480, 180)
E = f + [{"t": "move", "at": a, "kind": "wiggle", "targets": [i + "_m"], "pivot": [640, 560], "amp": 12, "hz": 2}]
wv = uid("wv")
E += [P(a, "M1000,480 Q1060,360 1120,480 Q1180,600 1240,480 Q1300,360 1360,480 Q1420,600 1480,480", c="blue", w=6, idp=wv),
      wig(a, wv, (1240, 480), 4, 5), sh(a, wv, 120, 0, 0.5, 0.8)]
E += BIG(a, 960, 140, "破绽五：对口型", c="blue", d=0.0, s=80) + BIG(a, 1240, 780, "对不齐", c="red", d=1.0, s=110)
B.append(E)
# 22 twist two: tells being fixed
a = 22
E = BIG(a, 960, 140, "反转二", c="red", d=0.0, s=100)
for n in range(5):
    x = 360 + 300 * n
    c_ = uid("cx")
    E += [P(a, f"M{x - 40},420 L{x + 40},500 M{x + 40},420 L{x - 40},500", c="red", w=9, idp=c_), {"t": "move", "at": a, "kind": "pop", "targets": [c_], "dur": 0.3, "delay": 0.1}]
    E += check(a, x, 640, d=0.6 + 0.3 * n)
pr, i = painter(a, 1750, 860, 0.5)
E += pr
B.append(E)
# 23 AI better every year
a = 23
E = []
for n, h in enumerate([160, 260, 380, 520]):
    E += bar(a, 380 + 260 * n, 780, 160, h, c="blue", d=0.2 + 0.3 * n)
    E += T(a, 460 + 260 * n, 840, 44, f"第{n + 1}年", c="muted", d=0.2 + 0.3 * n)
E += arr(a, 380, 640, 1300, 200, c="red", d=1.3, dur=0.6) + BIG(a, 1600, 400, "越画越好", c="red", d=0.6, s=90)
pr, i = painter(a, 1600, 860, 0.5)
E += pr
B.append(E)
# 23.5 like out-speeding a magician
a = 23.5
mg_ = uid("hat")
E = [R(a, 300, 360, 240, 220, c="ink", fill="ink", idp=mg_), R(a, 240, 560, 360, 30, c="ink", fill="ink", idp=mg_), wig(a, mg_, (420, 580), 4, 1.5)]
rb = uid("rab")
E += [O(a, 420, 330, 50, c="ink", idp=rb), P(a, "M400,290 L380,200 M440,290 L460,200", c="ink", w=6, idp=rb), sh(a, rb, 0, -80, 0.4, 0.5), bob(a, rb, 8, 2)]
cd = uid("cd")
E += [R(a, 1150, 320, 140, 200, c="red", idp=cd), spin(a, cd, (1220, 420), 120), pop(a, cd, 0.6)]
f, i = face(a, 1600, 480, 120, mood="o")
E += f + BIG(a, 960, 800, "比手快？", c="red", d=1.0, s=110)
B.append(E)
# 24 the safest check: the channel
a = 24
f, i = face(a, 480, 460, 130, hair="gold")
E = f + cross(a, 480, 460, d=0.4)
pipe = uid("pp")
E += [P(a, "M900,460 L1600,460", c="blue", w=40, idp=pipe), {"t": "move", "at": a, "kind": "grow", "targets": [pipe], "axis": "x", "pivot": [900, 460], "dur": 0.7, "delay": 0.6}]
for n in range(3):
    dt = uid("dt")
    E += [O(a, 920 + 40 * n, 460, 14, c="gold", fill="gold", idp=dt), sh(a, dt, 640, 0, 1.0 + 0.3 * n, 1.2)]
E += BIG(a, 1250, 700, "看渠道", c="blue", d=1.0, s=130) + T(a, 480, 700, 56, "看脸", c="muted", d=0.2)
B.append(E)
# 25 check the account
a = 25
ph, p = phone(a, 700, 470)
f, i = face(a, 700, 360, 80, hair="gold")
E = ph + f + T(a, 700, 520, 44, "@吴越", c="ink", d=0.2)
bd = uid("bd")
E += [O(a, 830, 520, 34, c="blue", fill="blue", idp=bd), pop(a, bd, 0.6), pulse(a, bd, 1.2), wig(a, p, (700, 790), 2, 1.2)]
E += BIG(a, 1350, 380, "看账号", c="blue", d=0.3, s=120) + check(a, 1350, 600, d=1.0) + T(a, 1350, 760, 56, "官方认证", c="ink", d=1.2)
B.append(E)
# 26 check the pitch
a = 26
E = BIG(a, 960, 140, "看话术", c="blue", d=0.0, s=100)
for n, s in enumerate(["今天最后一天！", "只剩最后几单！"]):
    bb = uid("bb")
    E += [R(a, 380 + 620 * n, 300 + 140 * n, 520, 140, c="red", idp=bb), pop(a, bb, 0.3 + 0.5 * n), wig(a, bb, (640 + 620 * n, 370 + 140 * n), 3, 3)]
    E += T(a, 640 + 620 * n, 390 + 140 * n, 54, s, c="red", d=0.4 + 0.5 * n)
cl = uid("cl")
E += [{"t": "icon", "at": a, "id": cl, "name": "clock", "x": 520, "y": 720, "size": 180, "c": "ink"}, wig(a, cl, (520, 720), 10, 4)]
B.append(E)
# 26.5 slow down
a = 26.5
sn = uid("sn")
E = [P(a, "M300,640 Q300,560 380,560 Q460,560 460,640 Z", c="green", w=6, idp=sn, fill="green"), O(a, 380, 590, 40, c="ink", idp=sn),
     sh(a, sn, 300, 0, 0.2, 3.0), bob(a, sn, 4, 1)]
f, i = face(a, 1300, 460, 150)
E += f + BIG(a, 960, 220, "慢一点", c="green", d=0.4, s=130) + [rot(a, i + "*", -8, (1300, 610), 1.0, 0.6)]
sp = uid("sp")
E += [O(a, 1650, 700, 60, c="red", idp=sp), pulse(a, sp, 1.2)]
B.append(E)
# 27 private transfer: no
a = 27
E = BIG(a, 960, 140, "看付款", c="blue", d=0.0, s=100)
E += coins(a, 500, 600, 4, 0.2, dx=600, dy=-100)
sf_ = uid("sf")
E += [R(a, 1300, 380, 260, 240, c="ink", idp=sf_), O(a, 1430, 500, 50, c="ink", idp=sf_), pop(a, sf_, 0.1), wig(a, sf_, (1430, 500), 3, 1.2)]
E += cross(a, 1430, 500, d=1.2) + T(a, 960, 780, 64, "私下转账 = 不信", c="red", d=1.4)
B.append(E)
# 28 labeling rule since 2025-09-01
a = 28
cal = uid("cal")
E = [R(a, 300, 260, 420, 420, c="ink", idp=cal), R(a, 300, 260, 420, 90, c="red", fill="red", idp=cal), pop(a, cal, 0.0), bob(a, cal, 6, 1.0)]
E += T(a, 510, 470, 70, "2025", c="ink", d=0.2) + T(a, 510, 590, 64, "9 月 1 日", c="red", d=0.5)
tg = uid("tg")
E += [P(a, "M1100,360 L1500,360 L1560,440 L1500,520 L1100,520 Z", c="blue", w=7, idp=tg), pop(a, tg, 0.9), wig(a, tg, (1100, 440), 5, 1.4)]
E += T(a, 1320, 455, 70, "AI 标识", c="blue", d=1.1) + sparkle(a, [(1650, 300)], 1.3)
B.append(E)
# 29 the video did say it
a = 29
ph, p = phone(a, 960, 470, w=420, h=680)
f, i = face(a, 960, 400, 130, hair="gold")
E = ph + f + T(a, 960, 760, 30, "含AI生成内容", c="muted", d=0.5)
mg = uid("mg")
E += [{"t": "icon", "at": a, "id": mg, "name": "magnifier", "x": 1400, "y": 700, "size": 200, "c": "red"}, sh(a, mg, -280, 40, 0.8, 0.8), bob(a, mg, 8, 1.6)]
B.append(E)
# 29.5 tiny print
a = 29.5
E = T(a, 600, 380, 26, "含AI生成内容", c="muted", d=0.0)
for n in range(3):
    e_ = uid("ey")
    E += [{"t": "icon", "at": a, "id": e_, "name": "eye", "x": 1150 + 220 * n, "y": 380, "size": 160, "c": "ink"}, pop(a, e_, 0.3 + 0.3 * n), wig(a, e_, (1150 + 220 * n, 380), 6, 2)]
E += BIG(a, 600, 640, "字很小", c="red", d=0.6, s=120) + arr(a, 600, 520, 600, 420, c="red", d=1.0)
B.append(E)
# 30 glance at the corners
a = 30
ph, p = phone(a, 960, 470, w=420, h=680)
E = ph
for (x, y) in [(790, 160), (1130, 160), (790, 780), (1130, 780)]:
    s = uid("crn")
    E += [O(a, x, y, 40, c="red", idp=s, sw=6), pulse(a, s, 0.2 + (x + y) % 3 * 0.3)]
f, i = face(a, 960, 420, 110)
E += f + [{"t": "move", "at": a, "kind": "shift", "targets": [i + "_e"], "dx": 20, "dy": 20, "delay": 0.8, "dur": 0.4}]
E += BIG(a, 1550, 470, "看角落", c="blue", d=0.6, s=110)
B.append(E)
# 31 account banned
a = 31
ph, p = phone(a, 700, 470)
f, i = face(a, 700, 420, 110, hair="gold")
E = ph + f + [rot(a, i + "*", 25, (700, 530), 1.0, 0.5)]
lk = uid("lk")
E += [R(a, 1300, 420, 260, 220, c="ink", fill="ink", idp=lk), P(a, "M1350,420 L1350,330 Q1430,250 1510,330 L1510,420", c="ink", w=12, idp=lk),
      pop(a, lk, 0.2), wig(a, lk, (1430, 420), 5, 2)]
E += BIG(a, 1430, 820, "永久封禁", c="red", d=0.6, s=100) + cross(a, 700, 470, d=0.8)
B.append(E)
# 32 fine print
a = 32
E = BIG(a, 960, 160, "友情提示", c="gold", d=0.0, s=100)
for n in range(3):
    ph_, p_ = phone(a, 500 + 460 * n, 560, w=240, h=400, d=0.2 + 0.3 * n)
    E += ph_ + [bob(a, p_, 6, 1 + 0.3 * n)]
    E += T(a, 500 + 460 * n, 560, 70, ["?", "✓", "?"][n] if n != 1 else "OK", c=["red", "green", "red"][n], d=0.5 + 0.3 * n)
B.append(E)
# 32.5 not a magic detector
a = 32.5
wd = uid("wd")
E = [P(a, "M500,700 L800,300", c="ink", w=14, idp=wd), rot(a, wd, 20, (500, 700), 0.2, 0.5), wig(a, wd, (500, 700), 8, 2)]
E += sparkle(a, [(820, 280), (900, 360)], 0.4) + cross(a, 700, 480, d=1.0)
E += BIG(a, 1350, 380, "不是万能", c="red", d=0.6, s=110) + T(a, 1350, 600, 60, "常见情况", c="ink", d=1.2)
pr, i = painter(a, 1650, 880, 0.45)
E += pr
B.append(E)
# 33 back to the start
a = 33
f1, i1 = face(a, 640, 460, 150, hair="gold")
f2, i2 = face(a, 1280, 460, 150, hair="gold")
E = f1 + f2 + [sh(a, i1 + "*", 40, 0, 0.3, 0.5), sh(a, i2 + "*", -40, 0, 0.3, 0.5)]
E += BIG(a, 960, 160, "我是我？", c="ink", d=0.2, s=110)
q = uid("q")
E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 960, "y": 760, "size": 170, "c": "red"}, pop(a, q, 0.8), pulse(a, q, 1.4)]
B.append(E)
# 34 prove the channel
a = 34
f, i = face(a, 460, 440, 130, hair="gold")
E = f + cross(a, 460, 440, d=0.3) + T(a, 460, 700, 56, "证明脸", c="muted", d=0.2)
pipe = uid("pp")
E += [P(a, "M900,440 L1600,440", c="blue", w=40, idp=pipe), {"t": "move", "at": a, "kind": "grow", "targets": [pipe], "axis": "x", "pivot": [900, 440], "dur": 0.6, "delay": 0.6}]
E += check(a, 1250, 620, d=1.2) + T(a, 1250, 760, 64, "证明渠道", c="blue", d=1.0)
dt = uid("dt")
E += [O(a, 920, 440, 16, c="gold", fill="gold", idp=dt), sh(a, dt, 660, 0, 0.8, 1.2)]
B.append(E)
# 34.5 the real Wu Yue on her verified account
a = 34.5
ph, p = phone(a, 960, 470)
f, i = face(a, 960, 380, 110, hair="gold")
E = ph + f + T(a, 960, 560, 44, "@吴越", c="ink", d=0.2)
bd = uid("bd")
E += [O(a, 1090, 560, 34, c="blue", fill="blue", idp=bd), pop(a, bd, 0.5), pulse(a, bd, 1.0)]
E += sparkle(a, [(600, 260), (1320, 260), (1380, 700)], 0.4) + BIG(a, 1500, 860, "真吴越", c="green", d=0.9, s=90)
B.append(E)
# 35 Doodle: I can paint any face
a = 35
pr, i = painter(a, 560, 840, 1.1)
E = pr
for n in range(3):
    f, j = face(a, 1050 + 280 * n, 420, 100, hair=["gold", "blue", "red"][n])
    E += f + [pop(a, j + "*", 0.2 + 0.3 * n)]
E += BIG(a, 1330, 760, "任何一张脸", c="blue", d=1.0, s=90)
B.append(E)
# 35.5 but can't log in
a = 35.5
pr, i = painter(a, 560, 840, 1.1, mood="sad")
E = pr + [wig(a, i + "*", (560, 840), 5, 3)]
lk = uid("lk")
E += [R(a, 1200, 400, 300, 240, c="ink", idp=lk, sw=8), P(a, "M1260,400 L1260,300 Q1350,210 1440,300 L1440,400", c="ink", w=12, idp=lk), pop(a, lk, 0.2), bob(a, lk, 6, 1)]
E += cross(a, 1350, 520, d=0.8) + BIG(a, 1350, 800, "登不上", c="red", d=1.0, s=120) + sparkle(a, [(1700, 260)], 1.2)
B.append(E)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say=SAY)
