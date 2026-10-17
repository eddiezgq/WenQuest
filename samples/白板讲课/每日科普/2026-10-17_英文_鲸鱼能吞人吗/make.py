"""Daily science short 2026-10-17 (English): "Could a whale actually swallow you?"
News: the film "Whalefall" (from Daniel Kraus's 2023 novel) opened in US theaters on Oct 16, 2026: a diver is swallowed by a sperm whale
with about an hour of air left (PopSci; Science Friday segment 2026-10-16; Science News; Slate; CNN 2026-10-15 with Michael Packard).
Facts: only a full-grown bull of 18 m or more could do it, bigger than most whales researchers see (Science News); left-shifted larynx →
wide throat; suction feeding by dropping the hyoid is thought, not observed (Science News); fin whales reach 26 m but "I can barely get
my arm down the throat" (Reidenberg, Science News); giant/colossal squid, colossal up to 14 m with tentacles (Science News); feeding
~3,000 ft deep, dives > 2 km (PopSci, Science News); four-chambered stomach, the first muscular, a leftover from plant-eating land
ancestors ~50 million years ago; "acids and gases"; "To my knowledge, no one has ever been eaten by a sperm whale" (Gero, PopSci);
only the reticulated python is confirmed to swallow people whole (Science News); 2019 Bryde's whale grabbed a photographer and spat
him out (Science News); Michael Packard, humpback, Cape Cod, 2021, "30 to 40 seconds" by his own account (CNN; widely reported).
Said as estimates in the film: an hour of breath-hold for a sperm whale dive; the scuba arithmetic.
Characters: popkit.cute_whale ("Gulp", the polite sperm whale, running gag: "not on the menu"), stick diver. No hand.
    python3 make.py <kokoro model dir> | --fake | --boards-only   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, bubbles, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, waves, wig)
from popkit import cute_whale, jaw_hinge, stick  # noqa: E402

S = [
 ("本周上映的电影《鲸落》：一头抹香鲸，把一个潜水员整个吞了下去。", "A movie out this weekend has a whale swallow a man. Whole."),
 ("他在鲸鱼肚子里，气瓶只剩一小时的空气。", "He's inside its stomach, with one hour of air left."),
 ("今天的问题：鲸鱼，真的能把你吞下去吗？", "So today's question: could a whale actually swallow you?"),
 ("先介绍今天的主角：大口，一头很有礼貌的抹香鲸。", "Meet our star: Gulp, a very polite sperm whale."),
 ("大口说：别担心，你不在菜单上。我们来查一查它说的对不对。", "Gulp says: relax, you're not on the menu. Let's check if Gulp is telling the truth."),
 ("先看最大的鲸鱼。长须鲸能长到二十六米，比两辆公交车还长。", "Start with the giants. A fin whale can grow to 26 meters. Longer than two buses."),
 ("可它的喉咙呢？一位解剖学家说：我的胳膊都很难伸进去。", "But its throat? One anatomist says: I can barely get my arm down there."),
 ("这种鲸靠吞大口海水，用鲸须滤出小虾。它是个大筛子，配了一根吸管那么细的喉咙。", "These whales gulp seawater and strain out tiny krill. A giant sieve with a drinking-straw throat."),
 ("所以长须鲸、蓝鲸：嘴大，喉咙小。吞不下你。", "So fin whales, blue whales: huge mouth, tiny throat. You don't fit."),
 ("反转一：抹香鲸不一样。它是有牙齿的鲸里最大的。", "Twist one: sperm whales are different. They're the biggest whales with teeth."),
 ("它的喉头偏向左边，让出了一条很宽的喉咙。", "Its voice box sits off to the left, leaving a much wider throat."),
 ("它吃的是什么？大王乌贼，大到十几米长。", "And what does it eat? Giant squid. Some over ten meters long."),
 ("科学家猜测，它是把舌骨往下一拉，像吸尘器一样把猎物吸进嘴里。|不过这个动作，谁也没亲眼见过。", "Scientists think it drops a bone in its throat and sucks prey in like a vacuum. | Nobody has actually seen it."),
 ("所以生理上，一头够大的抹香鲸，确实有可能吞下一个人。", "So physically, a big enough sperm whale could, maybe, swallow a person."),
 ("但要多大？至少十八米的成年雄鲸，|比科学家平时见到的大多数都大。", "How big? A full-grown bull of 18 meters or more. | Bigger than most whales scientists ever see."),
 ("反转二：就算它吞得下，它也碰不到你。", "Twist two: even if it could swallow you, it would never meet you."),
 ("潜水员一般在三十米以内。|抹香鲸去九百米深的地方吃饭，能潜到两千米以下。", "Divers stay above about 30 meters. | Sperm whales dine near 900 meters down, and dive past 2,000."),
 ("你在一楼，它在地下三百层的餐厅。|你们根本不在一个楼层。", "You're on the ground floor. Its restaurant is three hundred floors down. | You never share an elevator."),
 ("好，假设电影里那种倒霉事真的发生了。进去以后呢？", "Fine. Say the movie's bad luck really happens. You're in. Now what?"),
 ("抹香鲸的胃有四个格子，|这是五千万年前吃草的陆地祖先留下来的。", "A sperm whale's stomach has four chambers. | A leftover from plant-eating ancestors on land, fifty million years ago."),
 ("第一个格子，肌肉很厚，专门把食物搓碎。像一台洗衣机，只有甩干档。", "The first chamber has thick muscle walls that mash food. A washing machine stuck on spin."),
 ("里面没有空气，只有胃酸和气体。|墙壁又湿又滑，没有一个能抓的地方。", "No air in there. Just acids and gases. | The walls are wet and slimy, with nothing to grab."),
 ("所以电影里的气瓶，是主角唯一的空气来源。", "That's why the scuba tank in the movie is everything. It's the only air you've got."),
 ("一瓶气，在浅水里大约够用一小时。|估算：越害怕，喘得越快，用得越快。", "One tank lasts about an hour in shallow water. | Rough estimate: the more you panic, the faster it goes."),
 ("巧的是：抹香鲸一次下潜，也能憋气一个小时左右。", "Funny thing: a sperm whale can hold its breath for about an hour, too."),
 ("所以你们俩在比谁憋得久。它是专业的，你是业余的。", "So you're in a breath-holding contest. It's a professional. You're an amateur."),
 ("反转三，最反直觉：真正被吞过的人，吞他的根本不是抹香鲸。", "Twist three, the weird one: the people who really got gulped weren't caught by sperm whales."),
 ("二零二一年，美国一个捕龙虾的潜水员，被一头座头鲸含进了嘴里。", "In 2021, a lobster diver off Cape Cod was scooped into a humpback whale's mouth."),
 ("他说，在里面待了三十到四十秒，然后被吐了出来。", "He says he spent thirty to forty seconds inside. Then it spat him out."),
 ("座头鲸是滤食的：嘴巴巨大，喉咙很小。|它不是想吃他，是不小心多吃了一口。", "Humpbacks are filter feeders: huge mouth, small throat. | It wasn't hunting him. It just took a bad bite."),
 ("二零一九年在南非，一头鲸鱼也叼起过一个摄影师，|同样马上吐了。", "In 2019 off South Africa, another whale grabbed a photographer. | Same thing. Spat him right out."),
 ("一位研究抹香鲸的生物学家说：据我所知，从来没有人被抹香鲸吃掉过。", "A sperm whale biologist says: to my knowledge, no one has ever been eaten by a sperm whale."),
 ("而且抹香鲸吃大乌贼，经常是撕成块吃，未必整吞。", "And with big squid, sperm whales often surface with chunks. They may not swallow prey whole at all."),
 ("一个穿着气瓶、脚蹼的人，对它来说，更像是一根卡嗓子的鱼刺。", "A human in a tank and fins? Less like dinner, more like a fishbone stuck in its throat."),
 ("那世界上，真的有动物能把人整个吞下去吗？", "So is there any animal that really can swallow a human whole?"),
 ("有，而且已经确认过：网纹蟒。|在印尼有好几起记录。", "Yes, confirmed: the reticulated python. | There are several documented cases in Indonesia."),
 ("蟒蛇的下巴能左右分开，把嘴撑得比头还大。这才是真正的吞人专家。", "A python's jaw can spread apart, opening wider than its own head. That's the real swallowing expert."),
 ("就这，科学家也说，极其罕见。", "And even that, scientists say, is extremely rare."),
 ("算总账：长须鲸、蓝鲸，喉咙太小；座头鲸，含一下就吐。", "Final score: fin and blue whales, throat too small. Humpbacks, a quick mouthful and out."),
 ("抹香鲸，理论上能吞，但它在深海，你在浅水，它也不感兴趣。", "Sperm whales could in theory. But they're deep, you're shallow, and you're not their type."),
 ("友情提示：电影是虚构的。鲸鱼一般很温和，别去打扰它们就好。", "Friendly fine print: the movie is fiction. Whales are usually gentle. Just don't bother them."),
 ("我们今天的估算：气瓶时间、鲸鱼憋气，都是大概的数。", "Our rough numbers today: the air tank, the breath-hold. Ballpark only."),
 ("大口说得对：你真的不在菜单上。", "Gulp was right. You're really not on the menu."),
 ("不过大口补了一句：大王乌贼，你还是快跑吧。", "Gulp would like to add: giant squid, you should probably start swimming."),
]
TITLE = {"zh": "鲸鱼真的能把人吞下去吗？", "en": "Could a whale actually swallow you?"}


def W(at, cx, cy, k, **kw):
    i = uid("wh")
    return cute_whale(cx, cy, k, at, idp=i, **kw), i


def diver(at, cx, cy, k=1.0, kick=True):
    """Stick diver with a tank; feet at (cx, cy)."""
    i = uid("dv")
    E = stick(cx, cy, k, at, idp=i, arms="up")
    E += [R(at, cx + 18 * k, cy - 190 * k, 30 * k, 90 * k, c="gold", fill="gold", idp=i, sw=3)]
    E += [bob(at, i + "*", 10 * k, 1.4)]
    return E, i


B = []
# 0 swallowed whole
a = 0
els, i = W(a, 1000, 480, 1.25, mood="happy", mouth_open=True)
E = waves(a, 140) + els
dv, j = diver(a, 260, 640, 0.7)
E += dv + [sh(a, j + "*", 400, -40, 0.4, 1.4)] + bubbles(a, 1500, 760, n=4, d=0.2)
E += BIG(a, 960, 900, "GULP.", c="red", d=2.0, s=130)
B.append(E)
# 1 one hour of air
a = 1
E = waves(a, 140)
E += [O(a, 960, 520, 300, c="blue", sw=6)]
dv, j = diver(a, 960, 640, 0.9)
E += dv + [wig(a, j + "*", (960, 560), 6, 1.6)] + bubbles(a, 1000, 380, n=5, d=0.1)
k0 = uid("tk")
E += [R(a, 1460, 260, 140, 420, c="ink"), R(a, 1476, 300, 108, 364, c="green", fill="green", idp=k0),
      {"t": "move", "at": a, "kind": "grow", "targets": [k0], "axis": "y", "from": 1, "to": 0.3, "pivot": [1530, 664], "dur": 2.4, "delay": 0.4}]
E += BIG(a, 1530, 820, "1 hour", c="red", d=0.8, s=100) + T(a, 420, 300, 60, "inside the stomach", c="muted", d=0.3)
B.append(E)
# 2 the question
a = 2
els, i = W(a, 700, 560, 1.1, mood="o")
E = els + [rot(a, i + "_jaw", 18, jaw_hinge(700, 560, 1.1), 0.5, 0.4)]
dv, j = diver(a, 1500, 760, 0.8)
E += dv + [sh(a, j + "*", -120, 0, 0.6, 1.4)]
q = uid("q")
E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 1500, "y": 260, "size": 220, "c": "red"}, pop(a, q, 0.2), pulse(a, q, 1.0)]
E += BIG(a, 960, 920, "Could a whale swallow YOU?", c="ink", d=1.2, s=84)
B.append(E)
# 3 meet Gulp
a = 3
els, i = W(a, 960, 520, 1.6)
E = waves(a, 140) + els + bubbles(a, 380, 820, n=4) + star(a, 1600, 300, 0.6) + star(a, 1720, 420, 0.9)
E += BIG(a, 960, 900, "Gulp", c="blue", d=0.4, s=130) + T(a, 1500, 760, 52, "(very polite)", c="muted", d=1.4)
B.append(E)
# 4 not on the menu
a = 4
els, i = W(a, 640, 560, 1.1)
E = els
m = uid("menu")
E += [R(a, 1260, 200, 480, 600, c="ink", idp=m), pop(a, m, 0.2), wig(a, m, (1500, 200), 3, 0.8)]
E += T(a, 1500, 290, 60, "MENU", c="ink", d=0.3) + T(a, 1500, 400, 48, "giant squid", c="green", d=0.6) + T(a, 1500, 480, 48, "more squid", c="green", d=0.9)
E += T(a, 1500, 580, 48, "fish", c="green", d=1.2) + T(a, 1500, 690, 48, "you", c="red", d=1.6)
E += cross(a, 1500, 675, d=2.0) + bubbles(a, 300, 820, n=3)
B.append(E)
# 5 fin whale 26 m, two buses
a = 5
fw = uid("fw")
E = [P(a, "M180,420 Q300,330 700,340 L1500,370 Q1650,380 1720,420 L1800,360 L1790,470 L1720,440 Q1500,500 700,500 Q260,500 180,420 Z",
       c="ink", w=4, fill="muted", idp=fw), wig(a, fw, (1720, 420), 1.5, 1.0), sh(a, fw, -40, 0, 0.1, 3.0)]
for k in range(2):
    bs = uid("bus")
    E += [R(a, 260 + 640 * k, 640, 600, 170, c="gold", idp=bs), O(a, 380 + 640 * k, 820, 34, c="ink", idp=bs), O(a, 740 + 640 * k, 820, 34, c="ink", idp=bs),
          pop(a, bs, 0.8 + 0.4 * k), bob(a, bs, 4, 2.2)]
E += arr(a, 180, 580, 1800, 580, c="blue", w=5, d=0.4, dur=0.8) + BIG(a, 960, 220, "26 m", c="blue", d=0.3, s=130)
B.append(E)
# 6 arm in the throat
a = 6
E = [P(a, "M300,300 Q960,120 1620,300 L1620,800 Q960,980 300,800 Z", c="ink", w=5)]
th = uid("th")
E += [O(a, 960, 560, 60, c="red", sw=6, idp=th), pulse(a, th, 0.3)]
arm = uid("arm")
E += [P(a, "M1700,380 Q1300,420 1050,520", c="ink", w=14, idp=arm), sh(a, arm, -60, 30, 0.4, 1.0), wig(a, arm, (1700, 380), 3, 3)]
E += T(a, 960, 260, 56, "\"I can barely get my arm down the throat.\"", c="ink", d=0.8) + T(a, 960, 860, 44, "anatomist Joy Reidenberg", c="muted", d=1.6)
E += bubbles(a, 600, 720, n=3, d=0.5)
B.append(E)
# 7 sieve + straw
a = 7
E = []
for k in range(9):
    kr = uid("kr")
    E += [O(a, 220 + 60 * (k % 5), 420 + 60 * (k // 5) + (k % 2) * 20, 12, c="red", fill="red", idp=kr), sh(a, kr, 560, 30, 0.2 + 0.1 * k, 1.4)]
sv = uid("sv")
E += [P(a, " ".join(f"M{820 + 30 * k},300 L{820 + 30 * k},640" for k in range(10)), c="ink", w=4, idp=sv), wig(a, sv, (950, 470), 1.5, 1.2)]
st = uid("straw")
E += [R(a, 1400, 440, 360, 40, c="gold", fill="gold", idp=st), pop(a, st, 1.6), pulse(a, st, 2.2)]
E += T(a, 960, 230, 60, "giant sieve", c="blue", d=0.6) + T(a, 1580, 380, 56, "+ straw throat", c="gold", d=1.8)
E += T(a, 360, 760, 44, "krill", c="red", d=0.2)
B.append(E)
# 8 big mouth, tiny throat → you don't fit
a = 8
E = [P(a, "M200,300 L700,300 L1000,520 L700,740 L200,740", c="ink", w=6)]
dv, j = diver(a, 1500, 760, 0.8)
E += dv + [sh(a, j + "*", -380, 0, 0.3, 1.0), sh(a, j + "*", 380, 0, 1.4, 0.6)]
E += [R(a, 990, 500, 200, 40, c="ink")] + cross(a, 1100, 380, d=1.3)
E += BIG(a, 450, 520, "huge", c="blue", d=0.2, s=90) + T(a, 1100, 620, 48, "tiny", c="red", d=0.6)
E += BIG(a, 960, 900, "You don't fit.", c="red", d=1.8, s=90)
B.append(E)
# 9 sperm whale: biggest with teeth
a = 9
els, i = W(a, 820, 520, 1.4, mouth_open=True)
E = els + star(a, 380, 760, 0.4) + star(a, 1500, 240, 0.7)
tw = uid("tooth")
E += [P(a, "M1500,560 L1560,700 L1620,560 Z", c="ink", w=5, idp=tw), pop(a, tw, 0.8), wig(a, tw, (1560, 630), 8, 2)]
E += BIG(a, 960, 140, "Twist #1", c="red", d=0.0, s=90) + T(a, 1560, 800, 52, "biggest with teeth", c="blue", d=1.2)
B.append(E)
# 10 larynx to the left → wide throat
a = 10
E = [P(a, "M300,260 Q960,120 1620,260 L1620,820 Q960,960 300,820 Z", c="ink", w=5)]
lx = uid("lx")
E += [O(a, 700, 540, 70, c="blue", fill="blue", idp=lx), sh(a, lx, -260, 0, 0.3, 1.0)]
gl = uid("gl")
E += [O(a, 1060, 540, 120, c="red", sw=7, idp=gl), {"t": "move", "at": a, "kind": "grow", "targets": [gl], "axis": "x", "from": 0.4, "to": 1.6, "pivot": [1060, 540], "dur": 1.0, "delay": 0.9}]
E += arr(a, 760, 400, 500, 400, c="blue", d=0.3) + T(a, 440, 360, 44, "voice box", c="blue", d=0.4)
E += T(a, 1060, 760, 56, "wide throat", c="red", d=1.6) + bubbles(a, 1450, 760, n=3)
B.append(E)
# 11 giant squid
a = 11
sq = uid("sq")
E = [P(a, "M1200,300 Q1300,200 1400,300 L1420,560 L1180,560 Z", c="ink", w=5, fill="red", idp=sq)]
for k in range(6):
    tn = uid("tn")
    x = 1200 + 44 * k
    E += [P(a, f"M{x},560 Q{x - 40},700 {x + 10},820 Q{x + 40},900 {x - 20},980", c="red", w=5, idp=tn), wig(a, tn, (x, 560), 10, 1.5 + 0.3 * k)]
E += [bob(a, sq, 12, 0.9)]
els, i = W(a, 520, 540, 0.9, mood="o")
E += els + arr(a, 380, 900, 380, 200, c="blue", w=4, d=0.4, dur=0.8) + BIG(a, 700, 220, "10+ m", c="red", d=0.6, s=110)
B.append(E)
# 12 suction like a vacuum
a = 12
els, i = W(a, 640, 520, 1.2, mouth_open=True)
E = els
for k in range(3):
    sq = uid("sq")
    E += [P(a, f"M{1400 + 120 * k},{460 + 40 * k} Q{1440 + 120 * k},{400 + 40 * k} {1480 + 120 * k},{460 + 40 * k} L{1470 + 120 * k},{560 + 40 * k} L{1410 + 120 * k},{560 + 40 * k} Z",
            c="red", w=4, idp=sq), sh(a, sq, -900 - 100 * k, 60, 0.4 + 0.3 * k, 1.2)]
for k in range(4):
    ln = uid("suck")
    E += [P(a, f"M{1300 + 40 * k},{400 + 60 * k} L{1100 + 40 * k},{500 + 30 * k}", c="blue", w=4, idp=ln), pulse(a, ln, 0.2 * k)]
E += T(a, 1500, 260, 60, "WHOOSH", c="blue", d=0.4) + T(a, 1500, 800, 48, "(scientists' guess)", c="gold", d=1.2)
B.append(E)
# 13 physically possible
a = 13
els, i = W(a, 760, 520, 1.3)
E = els
dv, j = diver(a, 1600, 760, 0.6)
E += dv + [sh(a, j + "*", -40, 0, 0.3, 2.0)] + check(a, 1600, 300, d=1.0) + bubbles(a, 1200, 820, n=3)
E += BIG(a, 960, 920, "possible... maybe", c="gold", d=1.4, s=90)
B.append(E)
# 14 18 m bull
a = 14
els, i = W(a, 960, 460, 1.7)
E = els + arr(a, 400, 760, 1680, 760, c="red", w=5, d=0.3, dur=1.0)
E += BIG(a, 960, 900, "18 m +", c="red", d=0.6, s=130)
for k in range(3):
    sc = uid("sc")
    E += stick(260 + 120 * k, 1000, 0.35, a, idp=sc) + [pop(a, sc, 1.2 + 0.2 * k), bob(a, sc + "*", 6, 2.0)]
B.append(E)
# 15 twist 2: it never meets you
a = 15
E = waves(a, 260)
dv, j = diver(a, 500, 520, 0.7)
E += dv
els, i = W(a, 1300, 820, 0.8, moves=True)
E += els + [sh(a, i + "*", 200, 60, 0.4, 2.0)] + bubbles(a, 900, 900, n=4)
E += BIG(a, 960, 140, "Twist #2", c="red", d=0.0, s=90) + T(a, 960, 520, 60, "never meets you", c="blue", d=1.2)
B.append(E)
# 16 depths: 30 m vs 900 m vs 2000 m
a = 16
E = waves(a, 140) + [P(a, "M300,140 L300,1000", c="muted", w=3)]
dv, j = diver(a, 520, 300, 0.4)
E += dv + T(a, 260, 230, 40, "30 m", c="green", d=0.2, align="right")
els, i = W(a, 1100, 620, 0.55, moves=False)
E += els + [sh(a, i + "*", 0, 120, 0.4, 1.2), wig(a, i + "_t", (1100 + 176, 626), 10, 1.4), bob(a, i + "*", 6, 0.7)]
E += T(a, 260, 640, 40, "900 m", c="blue", d=0.8, align="right") + T(a, 260, 960, 40, "2,000 m+", c="ink", d=1.6, align="right")
E += arr(a, 1500, 160, 1500, 960, c="blue", w=6, d=0.6, dur=1.6) + bubbles(a, 1100, 520, n=3, d=1.0)
B.append(E)
# 17 elevator: floor 1 vs B300
a = 17
E = [R(a, 760, 120, 400, 820, c="ink")]
for k in range(8):
    E += [P(a, f"M760,{220 + 100 * k} L1160,{220 + 100 * k}", c="muted", w=2)]
el = uid("lift")
E += [R(a, 900, 140, 120, 70, c="gold", fill="gold", idp=el), sh(a, el, 0, 720, 0.4, 2.2)]
dv, j = diver(a, 520, 300, 0.5)
E += dv + T(a, 520, 380, 44, "floor 1", c="green", d=0.3)
els, i = W(a, 1520, 860, 0.45)
E += els + T(a, 1520, 1000, 44, "floor B300", c="blue", d=1.2) + star(a, 1700, 700, 1.4)
B.append(E)
# 18 say it happens. Now what?
a = 18
els, i = W(a, 960, 520, 1.4, mood="o", mouth_open=True)
E = els
dv, j = diver(a, 1700, 700, 0.6)
E += dv + [sh(a, j + "*", -1100, -100, 0.3, 1.2)] + bubbles(a, 400, 820, n=4)
E += BIG(a, 960, 920, "Now what?", c="red", d=1.6, s=100)
B.append(E)
# 19 four chambers, 50 million years
a = 19
E = []
for k in range(4):
    ch = uid("ch")
    E += [O(a, 360 + 300 * k, 520, 120 - 10 * k, c=["red", "gold", "green", "blue"][k], sw=6, idp=ch), pop(a, ch, 0.2 + 0.3 * k), pulse(a, ch, 1.6 + 0.2 * k)]
cw = uid("cow")
E += [R(a, 1500, 340, 260, 140, c="ink", idp=cw), O(a, 1500, 360, 40, c="ink", idp=cw), P(a, "M1530,480 L1530,560 M1730,480 L1730,560", c="ink", w=5, idp=cw),
      pop(a, cw, 1.6), bob(a, cw, 6, 1.6)]
E += BIG(a, 700, 230, "4 chambers", c="ink", d=0.0, s=90)
B.append(E)
# 20 washing machine on spin
a = 20
E = [R(a, 660, 220, 600, 640, c="ink", sw=6), O(a, 960, 560, 220, c="ink", sw=6)]
dr = uid("drum")
E += [P(a, "M800,560 Q960,420 1120,560 Q960,700 800,560", c="red", w=6, idp=dr), spin(a, dr, (960, 560), 120)]
for k in range(3):
    s_ = uid("sk")
    E += [O(a, 900 + 60 * k, 540, 18, c="gold", fill="gold", idp=s_), spin(a, s_, (960, 560), 100 + 30 * k)]
mw = uid("mw")
E += [R(a, 680, 240, 560, 600, c="ink", idp=mw, sw=2), wig(a, mw, (960, 860), 2, 6)]
E += T(a, 1500, 400, 56, "thick muscle", c="red", d=0.4) + T(a, 1500, 500, 56, "mashes food", c="red", d=0.8) + BIG(a, 1500, 700, "SPIN", c="blue", d=1.4, s=110)
B.append(E)
# 21 no air, acid, gas, slimy
a = 21
E = [P(a, "M240,240 Q960,80 1680,240 Q1820,560 1680,880 Q960,1000 240,880 Q100,560 240,240 Z", c="red", w=6)]
for k in range(6):
    g = uid("gas")
    E += [O(a, 400 + 220 * k, 820, 26 + 6 * (k % 3), c="green", sw=4, idp=g), sh(a, g, 10, -460, 0.2 + 0.25 * k, 2.4)]
dp = uid("drip")
E += [P(a, "M1200,250 Q1220,320 1200,360 Q1180,320 1200,250", c="blue", w=4, idp=dp), sh(a, dp, 0, 400, 0.6, 1.6)]
E += T(a, 600, 420, 64, "no air", c="red", d=0.2) + T(a, 1000, 560, 64, "acid + gas", c="green", d=1.0) 
B.append(E)
# 22 the tank is everything
a = 22
dv, j = diver(a, 760, 800, 1.3)
E = dv + [wig(a, j + "*", (760, 600), 4, 1.2)] + bubbles(a, 820, 400, n=5, d=0.1)
k0 = uid("tk")
E += [R(a, 1300, 260, 160, 520, c="ink", sw=6), R(a, 1318, 300, 124, 460, c="green", fill="green", idp=k0), pulse(a, k0, 0.6)]
E += BIG(a, 1380, 900, "only air", c="green", d=1.0, s=90)
B.append(E)
# 23 about an hour; panic burns it faster
a = 23
k0 = uid("tk")
E = [R(a, 300, 260, 160, 520, c="ink", sw=6), R(a, 318, 300, 124, 460, c="green", fill="green", idp=k0),
     {"t": "move", "at": a, "kind": "grow", "targets": [k0], "axis": "y", "from": 1, "to": 0.2, "pivot": [380, 760], "dur": 2.8, "delay": 0.4}]
E += BIG(a, 380, 900, "~1 h", c="green", d=0.2, s=100)
B.append(E)
a = 23.5
E = []
hr = uid("heart")
E += [P(a, "M1100,420 Q1040,320 980,420 Q960,500 1100,620 Q1240,500 1220,420 Q1160,320 1100,420 Z", c="red", w=6, fill="red", idp=hr),
      {"t": "move", "at": a, "kind": "pulse", "targets": [hr], "dur": 0.4}, {"t": "move", "at": a, "kind": "wiggle", "targets": [hr], "pivot": [1100, 500], "amp": 6, "hz": 4}]
E += arr(a, 1400, 760, 1700, 360, c="red", w=7, d=1.4, dur=0.8)
E += T(a, 1100, 760, 56, "panic", c="red", d=0.4) + T(a, 1560, 860, 48, "air used up faster", c="red", d=1.2) + T(a, 900, 200, 44, "(rough estimate)", c="gold", d=0.2)
dv, j = diver(a, 460, 820, 1.0)
E += dv + [wig(a, j + "*", (460, 700), 10, 5)] + bubbles(a, 520, 480, n=6, d=0.1, rise=300)
B.append(E)
# 24 sperm whale holds breath an hour too
a = 24
els, i = W(a, 960, 560, 1.4)
E = els
ck = uid("clk")
E += [O(a, 1620, 260, 110, c="ink", sw=6), P(a, "M1620,260 L1620,180", c="red", w=6, idp=ck), spin(a, ck, (1620, 260), 60)]
E += bubbles(a, 500, 820, n=4) + BIG(a, 960, 920, "~1 hour, too", c="blue", d=0.8, s=100)
B.append(E)
# 25 breath contest: pro vs amateur
a = 25
els, i = W(a, 560, 520, 1.0)
E = els
dv, j = diver(a, 1440, 760, 0.9)
E += dv + [wig(a, j + "*", (1440, 600), 8, 3)]
for x, lab, c, d in ((560, "PRO", "blue", 0.6), (1440, "amateur", "red", 1.4)):
    E += T(a, x, 180, 72, lab, c=c, d=d)
md = uid("md")
E += [O(a, 560, 300, 50, c="gold", fill="gold", idp=md), pop(a, md, 1.0), spin(a, md, (560, 300), 40)]
sw = uid("swt")
E += [P(a, "M1560,420 Q1580,460 1560,480 Q1540,460 1560,420", c="blue", w=4, idp=sw), sh(a, sw, 0, 120, 1.6, 1.0)]
B.append(E)
# 26 twist 3
a = 26
els, i = W(a, 600, 560, 1.0, mood="o")
E = els + cross(a, 600, 260, d=1.4)
hb = uid("hb")
E += [P(a, "M1100,560 Q1300,380 1700,480 L1820,420 L1800,560 L1700,560 Q1400,720 1100,560 Z", c="ink", w=5, fill="muted", idp=hb),
      pop(a, hb, 1.8), bob(a, hb, 10, 0.8), wig(a, hb, (1500, 540), 2, 1.0)]
E += BIG(a, 960, 140, "Twist #3", c="red", d=0.0, s=90) + T(a, 1460, 820, 52, "someone else did it", c="ink", d=2.2)
B.append(E)
# 27 2021 Cape Cod humpback
a = 27
hb = uid("hb")
E = waves(a, 300) + [P(a, "M300,640 Q600,380 1300,480 L1500,380 L1480,620 L1300,600 Q800,860 300,640 Z", c="ink", w=5, fill="muted", idp=hb),
                     sh(a, hb, 220, -60, 0.3, 1.4), wig(a, hb, (900, 600), 2, 1.0)]
dv, j = diver(a, 760, 640, 0.5)
E += dv + [sh(a, j + "*", 220, -60, 0.3, 1.4)]
E += BIG(a, 400, 180, "2021", c="gold", d=0.2, s=110) + T(a, 1400, 180, 60, "Cape Cod", c="blue", d=0.8) + T(a, 1400, 860, 48, "lobster diver + humpback", c="muted", d=1.6)
E += bubbles(a, 1600, 800, n=3)
B.append(E)
# 28 30-40 s then spat out
a = 28
hb = uid("hb")
E = [P(a, "M200,600 Q500,340 1100,440 L1300,340 L1280,580 L1100,560 Q700,820 200,600 Z", c="ink", w=5, fill="muted", idp=hb), wig(a, hb, (700, 560), 2, 1.0)]
dv, j = diver(a, 500, 640, 0.5)
E += dv + [sh(a, j + "*", 1100, -200, 1.8, 0.7), rot(a, j + "*", 200, (500, 560), 1.8, 0.7)]
ck = uid("clk")
E += [O(a, 1600, 300, 100, c="ink", sw=6), P(a, "M1600,300 L1600,220", c="red", w=6, idp=ck), spin(a, ck, (1600, 300), 120)]
E += BIG(a, 1600, 520, "30–40 s", c="red", d=0.4, s=96) + BIG(a, 1500, 860, "PTOO!", c="blue", d=1.9, s=110)
B.append(E)
# 29 filter feeder, a bad bite
a = 29
E = [P(a, "M200,300 L800,300 L1000,520 L800,740 L200,740", c="ink", w=6), R(a, 990, 500, 160, 40, c="ink")]
for k in range(8):
    kr = uid("kr")
    E += [O(a, 1500 + 40 * (k % 4), 420 + 60 * (k // 4), 12, c="red", fill="red", idp=kr), sh(a, kr, -1000, 80, 0.2 + 0.12 * k, 1.2)]
dv, j = diver(a, 1600, 860, 0.5)
E += dv
E += T(a, 500, 220, 56, "huge mouth", c="blue", d=0.2) + T(a, 1070, 640, 44, "small throat", c="red", d=0.6)
B.append(E)
# 30 2019 South Africa photographer
a = 30
E = waves(a, 360)
bw = uid("bw")
E += [P(a, "M600,900 Q760,460 920,360 Q1080,460 1240,900", c="ink", w=6, fill="muted", idp=bw), sh(a, bw, 0, -140, 0.3, 0.8), sh(a, bw, 0, 160, 1.6, 0.8)]
cam = uid("cam")
E += [R(a, 860, 200, 120, 80, c="ink", fill="ink", idp=cam), O(a, 920, 240, 26, c="gold", idp=cam), sh(a, cam, 0, -140, 0.3, 0.8), sh(a, cam, 300, -40, 1.6, 0.8), wig(a, cam, (920, 240), 12, 3)]
E += BIG(a, 340, 180, "2019", c="gold", d=0.2, s=110) + T(a, 1520, 180, 56, "South Africa", c="blue", d=0.6) 
B.append(E)
# 31 "no one has ever been eaten by a sperm whale"
a = 31
els, i = W(a, 1400, 600, 0.9)
E = els + T(a, 700, 300, 54, "\"To my knowledge,", c="ink", d=0.2) + T(a, 700, 400, 54, "no one has ever been eaten", c="ink", d=0.8) + T(a, 700, 500, 54, "by a sperm whale.\"", c="ink", d=1.4)
E += T(a, 700, 640, 40, "biologist Shane Gero", c="muted", d=1.8) + check(a, 1400, 280, d=2.2) + bubbles(a, 1700, 860, n=3)
B.append(E)
# 32 chunks, not whole
a = 32
els, i = W(a, 620, 560, 1.1, mouth_open=True)
E = els
for k in range(5):
    ch = uid("chunk")
    E += [R(a, 1150 + 90 * k, 480 + 30 * (k % 2), 60, 50, c="red", fill="red", idp=ch), pop(a, ch, 0.3 + 0.15 * k), sh(a, ch, 40 * k, 200 + 30 * k, 1.2, 1.6)]
E += T(a, 1400, 300, 64, "chunks", c="red", d=0.4) + T(a, 1400, 860, 48, "not always swallowed whole", c="muted", d=1.6)
B.append(E)
# 33 a fishbone in the throat
a = 33
els, i = W(a, 700, 560, 1.2, mood="worried")
E = els + [wig(a, i + "_b", (700, 560), 3, 5)]
fb = uid("fb")
E += [P(a, "M1250,560 L1650,560 M1330,500 L1360,560 L1330,620 M1430,500 L1460,560 L1430,620 M1530,500 L1560,560 L1530,620", c="ink", w=6, idp=fb),
      pop(a, fb, 0.8), rot(a, fb, 30, (1450, 560), 1.2, 0.6)]
E += T(a, 1450, 360, 56, "tank + fins =", c="ink", d=0.4) + BIG(a, 1450, 800, "fishbone", c="red", d=1.4, s=96)
B.append(E)
# 34 any animal that really can?
a = 34
q = uid("q")
E = [{"t": "icon", "at": a, "id": q, "name": "question", "x": 960, "y": 460, "size": 360, "c": "red"}, pop(a, q, 0.1), pulse(a, q, 0.8),
     wig(a, q, (960, 640), 6, 1.5)]
for k in range(4):
    E += star(a, 400 + 370 * k, 860 - 80 * (k % 2), 0.4 + 0.25 * k)
E += BIG(a, 960, 160, "anyone?", c="ink", d=0.4, s=96)
B.append(E)
# 35 reticulated python
a = 35
sn = uid("snake")
E = [P(a, "M200,700 Q400,500 600,700 Q800,900 1000,700 Q1200,500 1400,700 L1520,660 Q1600,640 1640,700 Q1600,760 1520,740 L1400,720",
       c="green", w=14, idp=sn), wig(a, sn, (900, 700), 4, 1.6), sh(a, sn, 120, 0, 0.2, 2.6)]
ey = uid("eye")
E += [O(a, 1580, 680, 10, c="ink", fill="ink", idp=ey), sh(a, ey, 120, 0, 0.2, 2.6), pulse(a, ey, 1.0)]
E += BIG(a, 960, 260, "reticulated python", c="green", d=0.3, s=90) + T(a, 960, 380, 52, "confirmed · Indonesia", c="muted", d=1.2)
E += check(a, 1700, 260, d=1.8)
B.append(E)
# 36 jaw spreads wider than the head
a = 36
E = [O(a, 960, 520, 120, c="green", sw=7)]
up, lo = uid("uj"), uid("lj")
E += [P(a, "M960,420 L1300,360 L1300,400 L1000,470", c="green", w=8, idp=up), rot(a, up, -25, (980, 440), 0.4, 0.8),
      P(a, "M960,620 L1300,680 L1300,640 L1000,570", c="green", w=8, idp=lo), rot(a, lo, 25, (980, 600), 0.4, 0.8)]
E += arr(a, 1400, 520, 1400, 260, c="red", w=5, d=1.2) + arr(a, 1400, 520, 1400, 780, c="red", w=5, d=1.2)
E += T(a, 960, 860, 56, "jaw spreads apart", c="green", d=0.8) + BIG(a, 500, 300, "wider", c="red", d=1.6, s=96) + T(a, 500, 400, 48, "than its head", c="red", d=1.8)
B.append(E)
# 37 extremely rare
a = 37
sn = uid("snake")
E = [P(a, "M300,700 Q500,500 700,700 Q900,900 1100,700 L1200,660 Q1260,650 1290,700 Q1260,750 1200,740 L1100,720", c="green", w=12, idp=sn),
     wig(a, sn, (800, 700), 5, 1.2), bob(a, sn, 8, 0.8)]
for k in range(3):
    E += star(a, 1400 + 120 * k, 400 + 90 * (k % 2), 0.3 + 0.3 * k)
E += BIG(a, 960, 260, "EXTREMELY rare", c="red", d=0.4, s=110)
B.append(E)
# 38 scoreboard 1
a = 38
fw = uid("fw")
E = [P(a, "M160,380 Q300,300 600,310 L800,320 L880,280 L870,380 L800,360 Q600,440 300,430 Q200,420 160,380 Z", c="ink", w=4, fill="muted", idp=fw), wig(a, fw, (520, 370), 2, 1)]
E += T(a, 1200, 380, 60, "fin + blue: throat too small", c="blue", d=0.2) + cross(a, 1780, 360, d=0.8)
hb = uid("hb")
E += [P(a, "M160,700 Q300,600 600,640 L800,600 L790,720 L600,700 Q300,800 160,700 Z", c="ink", w=4, fill="muted", idp=hb), pop(a, hb, 1.4), bob(a, hb, 8, 1.0)]
E += T(a, 1200, 700, 60, "humpback: in, then out", c="gold", d=1.6) + cross(a, 1780, 680, d=2.2)
B.append(E)
# 39 scoreboard 2: sperm whale in theory, but
a = 39
els, i = W(a, 500, 520, 0.9)
E = els + T(a, 1300, 300, 60, "sperm whale: in theory", c="green", d=0.2) + check(a, 1800, 280, d=0.6)
E += T(a, 1300, 480, 52, "but it's deep", c="blue", d=1.2) + T(a, 1300, 580, 52, "you're shallow", c="green", d=1.8) + T(a, 1300, 700, 52, "and not its type", c="red", d=2.4)
E += bubbles(a, 300, 860, n=4, d=0.6)
B.append(E)
# 40 fine print
a = 40
els, i = W(a, 1500, 640, 0.8)
E = T(a, 700, 220, 72, "friendly fine print", c="red", d=0.0) + T(a, 700, 400, 52, "the movie is fiction", c="ink", d=0.6)
E += T(a, 700, 520, 52, "whales: usually gentle", c="green", d=1.6) + T(a, 700, 640, 52, "don't bother them", c="blue", d=2.6) + els
E += star(a, 1700, 300, 1.0) + bubbles(a, 1200, 880, n=3)
B.append(E)
# 41 rough numbers
a = 41
k0 = uid("tk")
E = [R(a, 400, 300, 140, 440, c="ink", sw=6), R(a, 416, 340, 108, 384, c="green", fill="green", idp=k0),
     {"t": "move", "at": a, "kind": "grow", "targets": [k0], "axis": "y", "from": 1, "to": 0.5, "pivot": [470, 724], "dur": 1.4, "delay": 0.3}]
ck = uid("clk")
E += [O(a, 1400, 520, 140, c="ink", sw=6), P(a, "M1400,520 L1400,410", c="red", w=6, idp=ck), spin(a, ck, (1400, 520), 90)]
E += T(a, 470, 840, 52, "air tank", c="green", d=0.2) + T(a, 1400, 760, 52, "breath-hold", c="blue", d=0.8) + BIG(a, 960, 200, "ballpark", c="gold", d=1.4, s=100)
E += bubbles(a, 900, 860, n=3)
B.append(E)
# 42 Gulp was right
a = 42
els, i = W(a, 960, 500, 1.5)
E = els + star(a, 300, 300, 0.4) + star(a, 1650, 260, 0.7) + bubbles(a, 300, 860, n=3) + check(a, 1600, 760, d=1.0)
E += BIG(a, 960, 920, "not on the menu", c="green", d=0.6, s=96)
B.append(E)
# 43 giant squid, start swimming
a = 43
els, i = W(a, 520, 540, 1.0, mouth_open=True)
E = els + [sh(a, i + "*", 300, 0, 0.8, 2.0)]
sq = uid("sq")
E += [P(a, "M1400,400 Q1480,320 1560,400 L1570,560 L1390,560 Z", c="ink", w=5, fill="red", idp=sq), sh(a, sq, 300, -60, 0.4, 1.6)]
for k in range(4):
    tn = uid("tn")
    x = 1400 + 50 * k
    E += [P(a, f"M{x},560 Q{x - 30},660 {x + 10},760", c="red", w=5, idp=tn), wig(a, tn, (x, 560), 14, 3), sh(a, tn, 300, -60, 0.4, 1.6)]
E += BIG(a, 960, 160, "Run, squid!", c="red", d=1.2, s=110) + T(a, 1500, 900, 48, "(swim, actually)", c="muted", d=2.2)
B.append(E)

# ---------------------------------------------------------------- second halves (one sentence, two boards)
# 12.5 nobody has seen it
a = 12.5
sc, j = diver(a, 500, 860, 1.0)
E = sc
bn = uid("bino")
E += [O(a, 860, 420, 60, c="ink", sw=6, idp=bn), O(a, 1000, 420, 60, c="ink", sw=6, idp=bn), pop(a, bn, 0.1), wig(a, bn, (930, 420), 6, 1.2)]
q = uid("q")
E += [{"t": "icon", "at": a, "id": q, "name": "question", "x": 1400, "y": 420, "size": 260, "c": "red"}, pop(a, q, 0.5), pulse(a, q, 1.0)]
E += bubbles(a, 1200, 860, n=4, d=0.1) + BIG(a, 1300, 820, "never seen", c="red", d=0.8, s=96)
B.append(E)
# 14.5 bigger than most ever seen
a = 14.5
E = []
for k in range(4):
    els, i = W(a, 260 + 300 * k, 760, 0.3)
    E += els
els, i = W(a, 1450, 420, 0.75)
E += els + [pop(a, i + "*", 0.3)] + star(a, 1800, 200, 0.8) + star(a, 1100, 220, 1.0)
E += T(a, 700, 960, 48, "most whales", c="muted", d=0.1) + BIG(a, 1450, 860, "rare giant", c="red", d=0.9, s=90)
B.append(E)
# 16.5 dine at 900 m, dive past 2,000 m
a = 16.5
E = [R(a, 220, 140, 80, 800, c="ink", sw=5)]
dp = uid("depth")
E += [R(a, 232, 152, 56, 776, c="blue", fill="blue", idp=dp), {"t": "move", "at": a, "kind": "grow", "targets": [dp], "axis": "y", "from": 0.05, "to": 1, "pivot": [260, 152], "dur": 2.0, "delay": 0.1}]
els, i = W(a, 900, 300, 0.8, moves=False)
E += els + [rot(a, i + "*", -60, (900, 300), 0.1, 0.5), sh(a, i + "*", 200, 520, 0.4, 2.0), wig(a, i + "_t", (900 + 256, 308), 12, 1.6)]
E += BIG(a, 1500, 420, "900 m", c="blue", d=0.4, s=110) + BIG(a, 1500, 680, "2,000 m+", c="ink", d=1.4, s=110) + bubbles(a, 700, 900, n=4)
B.append(E)
# 17.5 you never share an elevator
a = 17.5
E = [R(a, 660, 200, 600, 700, c="ink", sw=6)]
dl, dr_ = uid("door"), uid("door")
E += [R(a, 360, 210, 290, 680, c="muted", fill="muted", idp=dl), R(a, 1270, 210, 290, 680, c="muted", fill="muted", idp=dr_),
      sh(a, dl, 310, 0, 0.3, 1.0), sh(a, dr_, -310, 0, 0.3, 1.0)]
dv, j = diver(a, 900, 860, 0.8)
E += dv
els, i = W(a, 1650, 560, 0.4)
E += els + cross(a, 1650, 300, d=1.2)
B.append(E)
# 19.5 plant-eating ancestors, 50 million years ago
a = 19.5
cw = uid("cow")
E = [R(a, 600, 420, 380, 200, c="ink", idp=cw), O(a, 590, 440, 60, c="ink", idp=cw), P(a, "M640,620 L640,740 M940,620 L940,740", c="ink", w=6, idp=cw),
     bob(a, cw, 6, 1.4)]
for k in range(6):
    gr = uid("grass")
    E += [P(a, f"M{380 + 60 * k},760 L{390 + 60 * k},700 M{400 + 60 * k},760 L{410 + 60 * k},690", c="green", w=5, idp=gr), wig(a, gr, (390 + 60 * k, 760), 10, 2 + 0.2 * k)]
E += [P(a, "M300,760 L1100,760", c="ink", w=5)]
E += arr(a, 1150, 500, 1450, 500, c="ink", w=6, d=0.8)
els, i = W(a, 1620, 520, 0.5)
E += els + BIG(a, 960, 200, "50 million years ago", c="gold", d=0.2, s=80) + T(a, 790, 860, 48, "a plant-eater on land", c="green", d=0.6)
B.append(E)
# 21.5 wet, slimy, nothing to grab
a = 21.5
E = [P(a, "M300,200 Q500,600 300,1000", c="red", w=8), P(a, "M1620,200 Q1420,600 1620,1000", c="red", w=8)]
for k in range(5):
    dp = uid("drip")
    x = 420 + 270 * k
    E += [P(a, f"M{x},220 Q{x + 20},290 {x},330 Q{x - 20},290 {x},220", c="green", w=4, idp=dp), sh(a, dp, 0, 500, 0.1 + 0.3 * k, 1.4)]
dv, j = diver(a, 960, 500, 0.9)
E += dv + [sh(a, j + "*", 0, 360, 0.3, 1.6), wig(a, j + "*", (960, 400), 10, 4)]
E += T(a, 960, 160, 64, "wet · slimy", c="green", d=0.1) + BIG(a, 1300, 600, "nothing to grab", c="red", d=0.8, s=72)
B.append(E)
# 29.5 not hunting, just a bad bite
a = 29.5
hb = uid("hb")
E = [P(a, "M200,600 Q500,340 1100,440 L1300,340 L1280,580 L1100,560 Q700,820 200,600 Z", c="ink", w=5, idp=hb), wig(a, hb, (700, 560), 2, 1.2)]
dv, j = diver(a, 400, 600, 0.5)
E += dv + [sh(a, j + "*", 1250, -140, 0.4, 0.8), rot(a, j + "*", 160, (400, 520), 0.4, 0.8)]
E += cross(a, 700, 260, d=0.2) + T(a, 700, 180, 48, "hunting", c="muted", d=0.1)
E += BIG(a, 1500, 820, "oops!", c="gold", d=1.0, s=110) + bubbles(a, 1500, 500, n=3, d=1.0)
B.append(E)
# 30.5 same thing, spat right out
a = 30.5
E = waves(a, 420)
cam = uid("cam")
E += [R(a, 860, 500, 120, 80, c="ink", fill="ink", idp=cam), O(a, 920, 540, 26, c="gold", idp=cam), sh(a, cam, 600, -300, 0.2, 0.8), wig(a, cam, (920, 540), 12, 3)]
dv, j = diver(a, 900, 760, 0.6)
E += dv + [sh(a, j + "*", 600, -300, 0.3, 0.8)]
E += BIG(a, 700, 220, "PTOO!", c="blue", d=0.5, s=120) + check(a, 1700, 760, d=1.0) + bubbles(a, 600, 860, n=3)
B.append(E)
# 35.5 several documented cases, Indonesia
a = 35.5
E = []
for k in range(3):
    pg = uid("doc")
    x = 400 + 260 * k
    E += [R(a, x, 360, 200, 260, c="ink", idp=pg), P(a, f"M{x + 30},420 L{x + 170},420 M{x + 30},480 L{x + 170},480 M{x + 30},540 L{x + 120},540", c="muted", w=4, idp=pg),
          pop(a, pg, 0.1 + 0.3 * k), rot(a, pg, -6 + 6 * k, (x + 100, 620), 0.4 + 0.3 * k, 0.4)]
isl = uid("isl")
E += [P(a, "M1280,560 Q1360,480 1480,520 Q1560,470 1640,540 Q1700,600 1600,620 Q1460,660 1340,620 Q1260,600 1280,560 Z", c="green", w=5, idp=isl),
      pop(a, isl, 0.6), bob(a, isl, 6, 0.8)]
E += T(a, 1480, 720, 56, "Indonesia", c="green", d=0.8) + BIG(a, 660, 220, "documented", c="ink", d=0.4, s=90)
B.append(E)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en")
