"""每日科普 2026-10-20（中文）：《史上最强厄尔尼诺，关你啥事？》
热点：新浪科学热点小时报 2026-10-20 18 时第 3 条“史上最强厄尔尼诺即将登顶”；21 财经 2026-10-20（转红星新闻）
“NASA 卫星直击‘最强厄尔尼诺’：赤道太平洋海水由绿变蓝、叶绿素骤降近八成”(m.21jingji.com/article/20261020/herald/b2d0c6013987c587dd9068414c1886d9.html)：
PACE 卫星；赤道海域叶绿素比一年前降近八成；9 月 21 日尼诺 3.4 区海温距平 3.05℃（国家海洋环境预报中心，经环球时报）；峰值预计 11–12 月；
NOAA：打破 1950 年以来纪录的概率 75%，97% 持续到 2027 年春；WMO：可能是有监测记录以来最强；
哈佛 Kuang：单次破纪录不能证明厄尔尼诺因气候变化变强。新浪 2026-10“厄尔尼诺或达超强级”：国标 GB/T 33666—2017 峰值 ≥2.5℃ 为超强；
国家气候中心预计强至超强、冬季我国大部偏暖、南方冬雨偏多（按概率）。
教科书常识：信风把暖水吹向西太平洋，东太平洋冷水上涌带来营养；信风减弱，暖水东回，上涌被盖住；名字来自秘鲁渔民（圣诞前后出现，“圣婴”）；
1998 年长江大洪水在 1997–98 超强厄尔尼诺之后；2016、2024 年的全球最热纪录都紧跟强厄尔尼诺。浴缸比喻是比喻。
角色：小鳀（一条鳀鱼，贯穿全片的梗：它的饭没了；结尾等拉尼娜把饭送回来）。没有手。
    python3 make.py <kokoro 模型目录> | --fake | --boards-only   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import importlib.util
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, waves, wig)
_sp = importlib.util.spec_from_file_location("en20", here.parent / "2026-10-20_英文_冰箱变烤箱" / "make.py")
en = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(en)          # 借用英文期的小工具：温度计、热浪、水滴、问号、小房子
thermo, waveheat, drops, Q, store = en.thermo, en.waveheat, en.drops, en.Q, en.store

S = [
 ("太平洋上一大片海，|一年之间，从绿色变成了蓝色。", "A huge patch of the Pacific | went from green to blue in one year."),
 ("蓝色不是更干净，|而是饭没了。", "Blue doesn't mean cleaner. | It means the food is gone."),
 ("NASA卫星测到，赤道太平洋的叶绿素，|比一年前少了将近八成。", "A NASA satellite found chlorophyll in the equatorial Pacific | is down nearly 80% from a year ago."),
 ("罪魁祸首：可能是有记录以来最强的厄尔尼诺。|今天的问题：太平洋发烧，关你啥事？", "The culprit: maybe the strongest El Niño on record. | Today's question: the Pacific has a fever, why should you care?"),
 ("认识一下小鳀，一条秘鲁鳀鱼。|今天，它的饭碗要被端了。", "Meet Andy, a Peruvian anchovy. | Today, his dinner is about to vanish."),
 ("平时，赤道上的信风，|一直从东往西吹。", "Normally, the trade winds along the equator | blow from east to west."),
 ("它把太阳晒热的表层海水，|一路推到印尼那边。", "They push the sun-warmed surface water | all the way toward Indonesia."),
 ("就像你对着浴缸一直吹：|热水全堆在了另一头。", "Like blowing across a bathtub nonstop: | the warm water piles up at the far end."),
 ("西边的海面，|因此比东边高出几十厘米。", "So the sea surface in the west | sits tens of centimeters higher than the east."),
 ("东边，南美那一侧，|深处的冷水就往上涌。", "In the east, off South America, | cold deep water wells up to replace it."),
 ("冷水带着营养，养活浮游植物，|浮游植物养活小鳀。", "That cold water carries nutrients that feed plankton, | and plankton feeds Andy."),
 ("反转一：信风一旦变弱，|浴缸里的水就晃回来了。", "Twist one: when the trade winds weaken, | the bathtub water sloshes back."),
 ("暖水向东回流，像一床热被子，|把冷水盖在下面。", "Warm water flows east like a warm blanket, | trapping the cold water below."),
 ("冷水上不来，营养上不来，|海就从绿变蓝。", "No cold water, no nutrients, | and the sea turns from green to blue."),
 ("秘鲁渔民早就发现，这事常在圣诞节前后出现，|所以叫它“圣婴”，厄尔尼诺。", "Peruvian fishers noticed it often came around Christmas, | so they called it El Niño, the Christ child."),
 ("小鳀表示：|这礼物我不要。", "Andy says: | no thanks to that gift."),
 ("反转二：一点点升温，|为什么能搅动全世界？", "Twist two: how can a little warming | shake up the whole world?"),
 ("暖水跑到哪儿，|水汽和大雨就跟到哪儿。", "Wherever the warm water goes, | the moisture and big storms follow."),
 ("大气就像被挪了暖气片的房间，|整屋的空气都跟着重新流动。", "The atmosphere is like a room where someone moved the radiator: | all the air starts flowing differently."),
 ("这次有多强？|9月21日，关键海区比常年高了3.05度。", "How strong is this one? | On September 21, the key ocean region was 3.05 degrees above normal."),
 ("按我国标准，超过2.5度，|就叫超强厄尔尼诺。", "By China's national standard, anything above 2.5 degrees | counts as a super El Niño."),
 ("美国海洋大气局估计，打破纪录的概率|大约75%。", "NOAA puts the chance of breaking the record | at about 75%."),
 ("峰值预计在11月到12月，|很可能拖到明年春天。", "The peak is expected in November or December, | likely lasting into next spring."),
 ("关你啥事？第一：全球会更热。|2016年和2024年两个最热纪录，都紧跟着强厄尔尼诺。", "Why care? First: the whole planet gets hotter. | The record hot years 2016 and 2024 both followed strong El Niños."),
 ("第二：天气会乱。按气象部门的经验，|我国冬天常常偏暖，南方雨偏多。", "Second: weather gets weird. Forecasters' experience says | Chinese winters tend to run warm, with more rain in the south."),
 ("1998年长江大洪水，|就发生在上一次超强厄尔尼诺之后。", "The great 1998 Yangtze flood | came right after an earlier super El Niño."),
 ("反转三：最强，不等于|它是被气候变暖“养大”的。", "Twist three: strongest doesn't automatically mean | climate change made it stronger."),
 ("哈佛的科学家提醒，一次破纪录，|还证明不了这个。", "A Harvard scientist warns one record-breaker | can't prove that on its own."),
 ("可它叠加在一个本来就变暖的地球上，|热浪的起点更高了。", "But it rides on top of an already warmer planet, | so heat waves start from a higher floor."),
 ("友情提示：这些都是概率预报，|不是板上钉钉。", "Friendly fine print: these are probability forecasts, | not certainties."),
 ("厄尔尼诺不等于一定发洪水，|还要看季风、副热带高压这些角色。", "El Niño doesn't guarantee floods. | Monsoons and other weather systems get a say too."),
 ("气象部门每个月都会更新，|跟着官方预报走就好。", "Weather agencies update every month, | so follow the official forecasts."),
 ("等信风重新吹起来，冷水回来，|海又会变绿。", "When the trade winds pick up again and the cold water returns, | the sea turns green again."),
 ("小鳀现在只盼一件事：|它的妹妹拉尼娜，快点回家做饭。", "Andy is waiting for one thing: | his sister La Niña to come home and cook."),
]
TITLE = {"zh": "史上最强厄尔尼诺，关你啥事？", "en": "The Strongest El Niño Ever: Why Care?"}


def fish(a, x, y, k=1.0, c="blue", sad=False, d=None, dirn=1):
    """小鳀：一条胖乎乎的小鱼，尾巴一直摆，身子上下浮。"""
    i, tail = uid("fish"), uid("tail")
    s = dirn
    E = [O(a, x, y, 70 * k, c=c, fill=c, idp=i), O(a, x + s * 35 * k, y - 15 * k, 10 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x + s * 20 * k},{y + 25 * k} Q{x + s * 40 * k},{y + (10 if sad else 40) * k} {x + s * 55 * k},{y + 25 * k}", c="ink", w=4, idp=i),
         P(a, f"M{x - s * 65 * k},{y} L{x - s * 130 * k},{y - 50 * k} L{x - s * 130 * k},{y + 50 * k} Z", c=c, w=4, fill=c, idp=tail),
         wig(a, tail, (x - s * 65 * k, y), 18, 3.0), bob(a, i, 8 * k, 1.2), bob(a, tail, 8 * k, 1.2)]
    if d is not None:
        E += [pop(a, i, d), pop(a, tail, d)]
    return E, i


def plank(a, x, y, n=6, d=0.1, c="green", spread=300):
    """浮游植物：一群小绿点，蹦出来后上下漂。"""
    E = []
    for q in range(n):
        i = uid("pk")
        E += [O(a, x + (q * 97) % spread - spread / 2, y + (q * 53) % 120 - 60, 14, c=c, fill=c, idp=i), pop(a, i, d + 0.08 * q), bob(a, i, 8, 0.8 + 0.1 * (q % 4))]
    return E


def wind(a, x0, x1, y, n=3, d=0.1, c="ink", w=6):
    """信风：几支箭头一支接一支射出，然后一直轻摆。"""
    E = []
    for q in range(n):
        yy = y + 60 * q
        E += arr(a, x0, yy, x1, yy, c=c, w=w, d=d + 0.2 * q, dur=0.5)
        E.append(wig(a, E[-2]["id"], (x0, yy), 1.5, 1.2))
    return E


def ocean(a, y=640, warm_x=None, c="blue"):
    """一截海：波浪线（一直晃）+ 暖水块（可选，从一侧挪过来）。"""
    E = waves(a, y, 160, 1760, c=c) + waves(a, y + 40, 200, 1720, c=c, amp=10)
    return E


def warm(a, x, y, w, h, d=0.2, dx=0, dur=1.2):
    i = uid("wm")
    E = [R(a, x, y, w, h, c="red", fill="red", idp=i), pulse(a, i, d + dur + 0.2, 0.8)]
    E.append(sh(a, i, dx, 0, d, dur) if dx else pop(a, i, d))
    return E, i


def cold(a, x, y, d=0.2, n=3):
    """冷水上涌：几支蓝箭头从下往上。"""
    E = []
    for q in range(n):
        E += arr(a, x + 70 * (q - 1), y, x + 70 * (q - 1), y - 200, c="blue", w=6, d=d + 0.2 * q, dur=0.6)
    return E


def globe(a, x, y, r=200, d=None, c="blue"):
    i, m = uid("gl"), uid("mer")
    E = [O(a, x, y, r, c=c, idp=i), P(a, f"M{x - r},{y} L{x + r},{y}", c=c, w=3, idp=i),
         P(a, f"M{x},{y - r} Q{x + r * 0.6},{y} {x},{y + r} M{x},{y - r} Q{x - r * 0.6},{y} {x},{y + r}", c=c, w=3, idp=m),
         {"t": "move", "at": a, "kind": "wiggle", "targets": [m], "pivot": [x, y], "amp": 8, "hz": 0.6}, bob(a, i, 5, 0.8)]
    if d is not None:
        E.append(pop(a, i, d))
    return E, i


def cloud(a, x, y, k=1.0, d=0.0, rain=True):
    i = uid("cl")
    E = [O(a, x - 60 * k, y, 60 * k, c="muted", fill="muted", idp=i), O(a, x + 10 * k, y - 30 * k, 75 * k, c="muted", fill="muted", idp=i),
         O(a, x + 80 * k, y, 55 * k, c="muted", fill="muted", idp=i), pop(a, i, d), sh(a, i, 60, 0, d + 0.3, 2.0)]
    if rain:
        E += drops(a, x, y + 80 * k, n=3, d=d + 0.3)
    return E


def amb(a, n=2):
    E = star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    if n > 2:
        E += star(a, 1810, 900, 0.5, r=20)
    return E


B = []


def bd(a, *parts, n=2):
    E = []
    for p in parts:
        E += p
    B.append(E + amb(a, n))


def patch(a, x, y, w, h, c, d=0.0, to=None):
    """一块颜色海：可从一种颜色换成另一种（新块从中间长出来盖住）。"""
    i = uid("pt")
    E = [R(a, x, y, w, h, c=c, fill=c, idp=i), bob(a, i, 4, 0.7)]
    if to:
        j = uid("pt")
        E += [R(a, x, y, w, h, c=to, fill=to, idp=j),
              {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "x", "pivot": [x + w / 2, y + h / 2], "dur": 1.0, "delay": d}]
    return E


# 0 绿变蓝
gl, gi = globe(0, 1450, 470, 220)
bd(0, patch(0, 260, 300, 700, 340, "green", d=0.6, to="blue"), gl, arr(0, 1000, 470, 1200, 470, c="ink", d=0.3), T(0, 610, 740, 64, "一年", c="ink", d=0.4),
   waves(0, 860, 200, 1700))
# 0.5 不是更干净
bd(0.5, patch(0.5, 260, 300, 600, 340, "blue"), cross(0.5, 560, 470, d=0.3), T(0.5, 1350, 380, 70, "更干净？", c="blue", d=0.1), BIG(0.5, 1350, 600, "饭没了", c="red", d=0.6, s=130),
   plank(0.5, 560, 470, 6, d=0.0))
# 1 NASA 卫星
sat = uid("sat")
bd(1, [R(1, 860, 200, 200, 120, c="ink", fill="muted", idp=sat), P(1, "M760,260 L860,260 M1060,260 L1160,260", c="blue", w=14, idp=sat), bob(1, sat, 10, 0.8),
       sh(1, sat, 300, 0, 0.1, 2.5)], sound(1, 960, 440, 1.0, d=0.4), T(1, 960, 700, 70, "NASA 卫星", c="ink", d=0.3), waves(1, 860, 200, 1700))
# 1.5 少了八成
bd(1.5, bar(1.5, 500, 820, 260, 500, "green", d=0.1) + bar(1.5, 1150, 820, 260, 100, "green", d=0.5), T(1.5, 630, 900, 56, "去年", c="ink"), T(1.5, 1280, 900, 56, "今年", c="ink"),
   BIG(1.5, 1280, 450, "−80%", c="red", d=0.8, s=140))
# 2 最强
bd(2, BIG(2, 960, 340, "厄尔尼诺", c="red", d=0.1, s=150), thermo(2, 400, 760, 1.0), [e for k in range(3) for e in star(2, 700 + 260 * k, 640, 0.4 + 0.2 * k, r=40)],
   T(2, 1100, 820, 64, "可能有记录以来最强", c="ink", d=0.6))
# 2.5 关你啥事
f, fi = fish(2.5, 700, 520, 1.3)
bd(2.5, f, Q(2.5, 1150, 300), T(2.5, 1350, 760, 80, "关你啥事？", c="red", d=0.4), thermo(2.5, 300, 760, 0.8))
# 3 小鳀
f, fi = fish(3, 900, 520, 2.0, d=0.0)
bd(3, f, BIG(3, 1500, 420, "小鳀", c="gold", d=0.4, s=150), plank(3, 500, 800, 6, d=0.3), n=3)
# 3.5 饭碗被端
f, fi = fish(3.5, 700, 520, 1.5, sad=True)
bwl = uid("bowl")
bd(3.5, f, [P(3.5, "M1100,500 Q1250,680 1400,500 Z", c="ink", w=6, fill="gold", idp=bwl), sh(3.5, bwl, 300, -300, 0.5, 0.8), rot(3.5, bwl, 40, (1250, 560), 0.5, 0.8)],
   T(3.5, 960, 860, 64, "饭碗要没了", c="red", d=0.4))
# 4 信风东往西
bd(4, ocean(4), wind(4, 1600, 400, 300, d=0.1), T(4, 1700, 480, 56, "东", c="ink", d=0.1), T(4, 220, 480, 56, "西", c="ink", d=0.1), T(4, 960, 200, 70, "信风", c="ink", d=0.3))
# 4.5 一直吹
bd(4.5, ocean(4.5), wind(4.5, 1500, 500, 260, n=4, d=0.0, c="muted"), [e for k in range(3) for e in waveheat(4.5, 600 + 400 * k, 560, n=1, d=0.2 * k, c="gold")],
   T(4.5, 960, 860, 56, "从东往西，一直吹", c="ink", d=0.5))
# 5 推暖水
w_, wi = warm(5, 1200, 540, 400, 90, d=0.3, dx=-800, dur=1.6)
bd(5, w_, wind(5, 1600, 600, 300, d=0.0), ocean(5), T(5, 960, 820, 60, "暖水被推走", c="red", d=0.5))
# 5.5 推到印尼
w_, wi = warm(5.5, 260, 520, 500, 120, d=0.1)
isl = uid("isl")
bd(5.5, w_, [P(5.5, "M200,500 Q260,420 320,500 M360,500 Q420,440 480,500", c="green", w=8, idp=isl), pop(5.5, isl, 0.3), bob(5.5, isl, 4, 1.0)],
   ocean(5.5), T(5.5, 400, 360, 64, "印尼", c="ink", d=0.4), arr(5.5, 1400, 400, 800, 400, c="muted", d=0.2))
# 6 浴缸
tub = uid("tub")
bd(6, [P(6, "M400,420 L400,760 Q400,820 460,820 L1460,820 Q1520,820 1520,760 L1520,420", c="ink", w=8, idp=tub), bob(6, tub, 3, 0.6)],
   [e for e in waves(6, 560, 420, 1500, amp=10)], wind(6, 1700, 1300, 380, n=2, d=0.2, c="blue"), T(6, 960, 260, 64, "一直吹浴缸", c="ink", d=0.3))
# 6.5 堆在另一头
tub = uid("tub")
wt = uid("wt")
bd(6.5, [P(6.5, "M400,420 L400,760 Q400,820 460,820 L1460,820 Q1520,820 1520,760 L1520,420", c="ink", w=8, idp=tub),
         P(6.5, "M410,500 Q900,560 1510,640 L1510,800 L410,800 Z", c="red", w=4, fill="red", idp=wt),
         rot(6.5, wt, -3, (960, 800), 0.2, 1.2), wig(6.5, wt, (960, 800), 1.5, 0.9)], wind(6.5, 1700, 1300, 380, n=2, d=0.0, c="blue"),
   T(6.5, 700, 360, 64, "全堆这头", c="red", d=0.5))
# 7 西边高
sea = uid("sea")
bd(7, [P(7, "M200,480 Q960,560 1720,620", c="blue", w=8, idp=sea), wig(7, sea, (960, 560), 1.5, 0.8)], arr(7, 260, 700, 260, 500, c="red", d=0.3),
   T(7, 300, 400, 60, "西：高", c="red", d=0.4), T(7, 1600, 520, 60, "东：低", c="blue", d=0.6), ocean(7, 800))
# 7.5 几十厘米
bd(7.5, BIG(7.5, 960, 420, "几十厘米", c="red", d=0.1, s=140), arr(7.5, 500, 700, 500, 560, c="red", d=0.4), arr(7.5, 1420, 560, 1420, 700, c="blue", d=0.6), ocean(7.5, 780))
# 8 东边冷水上涌
bd(8, ocean(8, 420), cold(8, 1400, 900, d=0.1), T(8, 1400, 300, 64, "南美", c="ink", d=0.2), T(8, 700, 760, 60, "深处的冷水", c="blue", d=0.5),
   [e for e in drops(8, 1400, 640, n=3, d=0.5)])
# 8.5 往上涌
bd(8.5, ocean(8.5, 360), cold(8.5, 960, 900, d=0.0, n=4), cold(8.5, 1400, 900, d=0.4, n=2), BIG(8.5, 500, 640, "上涌", c="blue", d=0.5, s=130))
# 9 营养 → 浮游植物
bd(9, cold(9, 500, 860, d=0.0), plank(9, 1000, 500, 8, d=0.4), arr(9, 650, 500, 820, 500, c="ink", d=0.3), T(9, 500, 400, 60, "营养", c="gold", d=0.2),
   T(9, 1000, 760, 60, "浮游植物", c="green", d=0.6))
# 9.5 养活小鳀
f, fi = fish(9.5, 1300, 520, 1.4)
bd(9.5, plank(9.5, 600, 500, 8, d=0.0), f, arr(9.5, 820, 500, 1100, 500, c="ink", d=0.3), [sh(9.5, fi + "*", -150, 0, 0.6, 0.8)], check(9.5, 1300, 260, d=1.0))
# 10 反转一：信风变弱
E = arr(10, 1500, 300, 1100, 300, c="muted", w=4, d=0.3)
bd(10, BIG(10, 960, 160, "反转一", c="red", d=0.1, s=90), E, [{"t": "move", "at": 10, "kind": "grow", "targets": [E[0]["id"]], "axis": "x", "from": 1.0, "to": 0.3,
                                                                "pivot": [1500, 300], "dur": 0.8, "delay": 1.0}], ocean(10, 640), T(10, 700, 400, 64, "信风变弱", c="ink", d=0.4))
# 10.5 晃回来
tub = uid("tub")
wt = uid("wt")
bd(10.5, [P(10.5, "M400,420 L400,760 Q400,820 460,820 L1460,820 Q1520,820 1520,760 L1520,420", c="ink", w=8, idp=tub),
          P(10.5, "M410,500 Q900,560 1510,640 L1510,800 L410,800 Z", c="red", w=4, fill="red", idp=wt),
          rot(10.5, wt, 6, (960, 800), 0.2, 1.0), wig(10.5, wt, (960, 800), 3, 1.2)], arr(10.5, 600, 360, 1300, 360, c="red", d=0.4), T(10.5, 960, 260, 64, "晃回来！", c="red", d=0.6))
# 11 暖水东回 热被子
w_, wi = warm(11, 300, 560, 600, 100, d=0.1, dx=900, dur=1.4)
bd(11, w_, ocean(11, 700), T(11, 960, 380, 64, "暖水向东", c="red", d=0.3), arr(11, 400, 460, 1500, 460, c="red", d=0.2))
# 11.5 盖住冷水
w_, wi = warm(11.5, 500, 420, 900, 120, d=0.0)
E = []
for q in range(4):
    E += arr(11.5, 600 + 220 * q, 860, 600 + 220 * q, 560, c="blue", w=6, d=0.2 + 0.15 * q, dur=0.5)
bd(11.5, w_, E, cross(11.5, 950, 480, d=0.9), T(11.5, 960, 300, 64, "热被子盖住", c="red", d=0.3))
# 12 营养上不来
bd(12, cold(12, 960, 900, d=0.0), [R(12, 560, 500, 800, 90, c="red", fill="red", idp=uid("lid"))], cross(12, 960, 760, d=0.6), T(12, 960, 360, 64, "营养上不来", c="ink", d=0.3),
   plank(12, 960, 300, 3, d=0.8))
# 12.5 绿变蓝
bd(12.5, patch(12.5, 360, 300, 1200, 380, "green", d=0.3, to="blue"), T(12.5, 960, 820, 70, "绿 → 蓝", c="ink", d=0.4), waves(12.5, 740, 300, 1600))
# 13 秘鲁渔民 圣诞
boat = uid("boat")
tree = uid("tree")
bd(13, [P(13, "M400,600 L900,600 L820,700 L480,700 Z", c="ink", w=6, fill="muted", idp=boat), bob(13, boat, 10, 0.8), rot(13, boat, 4, (650, 650), 0.2, 1.0)],
   [P(13, "M1400,250 L1250,550 L1550,550 Z", c="green", w=6, fill="green", idp=tree), pop(13, tree, 0.4), wig(13, tree, (1400, 550), 3, 1.0)],
   star(13, 1400, 240, 0.6, r=40), ocean(13, 720), T(13, 650, 400, 60, "秘鲁渔民", c="ink", d=0.2))
# 13.5 圣婴
bd(13.5, BIG(13.5, 960, 400, "圣婴", c="gold", d=0.1, s=150), T(13.5, 960, 600, 70, "El Niño", c="red", d=0.4), star(13.5, 600, 300, 0.5, r=40), star(13.5, 1320, 300, 0.7, r=40),
   ocean(13.5, 780))
# 14 小鳀表示
f, fi = fish(14, 960, 520, 1.6, sad=True)
gift = uid("gift")
bd(14, f, [R(14, 1350, 400, 200, 200, c="red", idp=gift), P(14, "M1450,400 L1450,600 M1350,500 L1550,500", c="gold", w=8, idp=gift), pop(14, gift, 0.3), bob(14, gift, 6, 1.2)],
   T(14, 600, 300, 64, "小鳀：", c="ink", d=0.2))
# 14.5 礼物不要
f, fi = fish(14.5, 700, 520, 1.4, sad=True)
gift = uid("gift")
bd(14.5, f, [R(14.5, 1200, 420, 200, 200, c="red", idp=gift), sh(14.5, gift, 500, -200, 0.4, 0.8), rot(14.5, gift, 60, (1300, 520), 0.4, 0.8)],
   T(14.5, 960, 860, 70, "这礼物我不要", c="red", d=0.3), [wig(14.5, fi + "*", (700, 520), 6, 3.0)])
# 15 反转二
bd(15, BIG(15, 960, 160, "反转二", c="red", d=0.1, s=90), thermo(15, 500, 760, 1.0, frm=0.4, to=0.55), globe(15, 1300, 520, 220)[0], Q(15, 860, 380, s=180, d=0.6))
# 15.5 搅动全世界
gl, gi = globe(15.5, 960, 480, 260)
bd(15.5, gl, [spin(15.5, gi, (960, 480), 20)], cloud(15.5, 500, 300, 0.8, d=0.3), cloud(15.5, 1400, 300, 0.8, d=0.6), T(15.5, 960, 860, 64, "搅动全世界", c="red", d=0.6))
# 16 暖水跑到哪儿
w_, wi = warm(16, 400, 640, 400, 90, d=0.1, dx=700, dur=1.4)
bd(16, w_, ocean(16, 760), cloud(16, 600, 340, 0.8, d=0.3, rain=False), T(16, 960, 200, 60, "暖水跑到哪儿…", c="red", d=0.2))
# 16.5 大雨跟到哪儿
bd(16.5, cloud(16.5, 960, 340, 1.3, d=0.0), [e for k in range(4) for e in drops(16.5, 760 + 130 * k, 460, n=2, d=0.2 + 0.15 * k)], ocean(16.5, 780),
   T(16.5, 960, 920, 60, "雨就跟到哪儿", c="blue", d=0.5))
# 17 挪暖气片
rad = uid("rad")
room = uid("room")
bd(17, [R(17, 360, 240, 1200, 600, c="ink", idp=room)],
    [R(17, 420, 620, 200, 160, c="red", fill="red", idp=rad), sh(17, rad, 900, 0, 0.4, 1.2), pulse(17, rad, 1.8)], waveheat(17, 520, 600, d=0.1), T(17, 960, 180, 60, "挪了暖气片", c="ink", d=0.3))
# 17.5 空气重新流动
loop1, loop2 = uid("lp"), uid("lp")
bd(17.5, [O(17.5, 700, 520, 200, c="blue", idp=loop1), spin(17.5, loop1, (700, 520), 50), O(17.5, 1220, 520, 200, c="red", idp=loop2), spin(17.5, loop2, (1220, 520), -50)],
   arr(17.5, 700, 320, 800, 320, c="blue", d=0.2), arr(17.5, 1220, 320, 1120, 320, c="red", d=0.4), T(17.5, 960, 860, 60, "整屋空气重新流动", c="ink", d=0.5))
# 18 有多强
bd(18, thermo(18, 600, 760, 1.2, frm=0.2, to=0.9), Q(18, 1100, 300, d=0.2), T(18, 1250, 700, 70, "有多强？", c="red", d=0.4))
# 18.5 3.05度
bd(18.5, BIG(18.5, 960, 420, "+3.05℃", c="red", d=0.1, s=150), T(18.5, 960, 620, 56, "9月21日 · 关键海区", c="ink", d=0.4), thermo(18.5, 400, 820, 0.8), waveheat(18.5, 1500, 800, d=0.5))
# 19 我国标准
book = uid("bk")
bd(19, [R(19, 500, 280, 340, 440, c="ink", fill="muted", idp=book), pop(19, book, 0.1), rot(19, book, -6, (670, 720), 0.4, 0.6), bob(19, book, 5, 0.9)],
   T(19, 670, 420, 56, "国家标准", c="ink", d=0.2), BIG(19, 1350, 480, "≥ 2.5℃", c="red", d=0.6, s=130))
# 19.5 超强
bd(19.5, BIG(19.5, 960, 420, "超强", c="red", d=0.1, s=150), bar(19.5, 400, 860, 160, 180, "gold", d=0.2), bar(19.5, 700, 860, 160, 260, "gold", d=0.4),
   bar(19.5, 1060, 860, 160, 320, "red", d=0.6), bar(19.5, 1360, 860, 160, 380, "red", d=0.8))
# 20 NOAA
bd(20, globe(20, 600, 500, 200, d=0.0)[0], T(20, 1300, 380, 60, "美国海洋大气局", c="ink", d=0.2), T(20, 1300, 520, 56, "破纪录的概率", c="ink", d=0.5), sound(20, 820, 500, 1.0, d=0.3))
# 20.5 75%
pie = uid("pie")
bd(20.5, [O(20.5, 700, 500, 220, c="ink", idp=uid("pc")), P(20.5, "M700,500 L700,280 A220,220 0 1 1 480,500 Z", c="red", w=4, fill="red", idp=pie),
          pop(20.5, pie, 0.2), spin(20.5, pie, (700, 500), 6)], BIG(20.5, 1350, 500, "75%", c="red", d=0.4, s=150))
# 21 峰值 11-12 月
E = []
for k, m in enumerate(["9", "10", "11", "12", "1", "2"]):
    h = [150, 250, 380, 400, 330, 220][k]
    E += bar(21, 360 + 210 * k, 800, 140, h, "red" if m in ("11", "12") else "gold", d=0.1 + 0.15 * k, dur=0.4) + T(21, 430 + 210 * k, 860, 50, m + "月", c="ink")
bd(21, E, T(21, 960, 220, 64, "峰值：11–12月", c="red", d=0.8))
# 21.5 拖到明年春
flw = uid("flw")
bd(21.5, [P(21.5, "M960,700 L960,480", c="green", w=8, idp=flw), O(21.5, 960, 440, 60, c="gold", fill="gold", idp=flw), pop(21.5, flw, 0.4), wig(21.5, flw, (960, 700), 6, 1.4)],
   T(21.5, 960, 300, 64, "很可能拖到明年春天", c="ink", d=0.2), BIG(21.5, 1450, 560, "97%", c="green", d=0.7, s=110), thermo(21.5, 450, 760, 0.8))
# 22 全球更热
gl, gi = globe(22, 700, 500, 220)
bd(22, gl, waveheat(22, 700, 260, d=0.2), thermo(22, 1200, 760, 1.0), T(22, 1550, 500, 64, "第一：更热", c="red", d=0.4))
# 22.5 2016 2024
E = []
for k, yr in enumerate(["2015", "2016", "2023", "2024"]):
    E += bar(22.5, 400 + 300 * k, 820, 160, [250, 380, 300, 440][k], "red" if yr in ("2016", "2024") else "gold", d=0.1 + 0.2 * k) + T(22.5, 480 + 300 * k, 880, 50, yr, c="ink")
bd(22.5, E, star(22.5, 780, 380, 0.9, r=40), star(22.5, 1380, 320, 1.1, r=40), T(22.5, 960, 200, 56, "最热纪录紧跟强厄尔尼诺", c="red", d=0.6))
# 23 天气会乱
bd(23, cloud(23, 600, 400, 1.0, d=0.1), [e for e in waveheat(23, 1300, 600, d=0.3)], T(23, 960, 820, 64, "第二：天气会乱", c="ink", d=0.4), thermo(23, 1600, 760, 0.7))
# 23.5 暖冬 南方多雨
snowman = uid("snm")
bd(23.5, [O(23.5, 600, 600, 110, c="ink", idp=snowman), O(23.5, 600, 430, 70, c="ink", idp=snowman), sh(23.5, snowman, 0, 80, 0.3, 1.4), wig(23.5, snowman, (600, 710), 4, 1.0)],
   drops(23.5, 600, 300, d=0.5), T(23.5, 600, 820, 56, "冬天偏暖", c="red", d=0.4), cloud(23.5, 1350, 380, 1.0, d=0.3), T(23.5, 1350, 820, 56, "南方雨多", c="blue", d=0.6))
# 24 1998 长江
riv = uid("riv")
bd(24, [P(24, "M200,600 Q600,450 960,600 Q1300,750 1720,600", c="blue", w=14, idp=riv), wig(24, riv, (960, 600), 1.5, 0.8)], BIG(24, 960, 300, "1998", c="ink", d=0.1, s=130),
   cloud(24, 1400, 280, 0.8, d=0.3), T(24, 960, 820, 60, "长江大洪水", c="blue", d=0.4))
# 24.5 上一次超强之后
wl = uid("wl")
bd(24.5, [R(24.5, 300, 640, 1320, 200, c="blue", fill="blue", idp=wl),
          {"t": "move", "at": 24.5, "kind": "grow", "targets": [wl], "axis": "y", "from": 0.3, "to": 1.0, "pivot": [960, 840], "dur": 1.2, "delay": 0.2}],
   store(24.5, 700, 600, 1.0, 0.0), store(24.5, 1200, 600, 1.0, 0.1), T(24.5, 960, 300, 60, "上一次超强厄尔尼诺之后", c="red", d=0.4))
# 25 反转三
bd(25, BIG(25, 960, 160, "反转三", c="red", d=0.1, s=90), BIG(25, 700, 460, "最强", c="red", d=0.3, s=120), T(25, 1300, 460, 80, "≠", c="ink", d=0.6),
   thermo(25, 1600, 760, 0.8), globe(25, 1300, 700, 120, d=0.8)[0])
# 25.5 气候变暖养大？
gl, gi = globe(25.5, 760, 520, 200)
bd(25.5, gl, waveheat(25.5, 760, 280, d=0.2), Q(25.5, 1150, 300, d=0.4), T(25.5, 1350, 760, 60, "被变暖养大？", c="ink", d=0.5))
# 26 哈佛提醒
book = uid("bk")
bd(26, [R(26, 500, 260, 340, 440, c="red", fill="red", idp=book), pop(26, book, 0.1), bob(26, book, 6, 0.9), rot(26, book, 5, (670, 700), 0.4, 0.6)],
   T(26, 670, 480, 64, "哈佛", c="ink", d=0.2), sound(26, 900, 450, 1.0, d=0.4), T(26, 1350, 480, 60, "科学家提醒", c="ink", d=0.5))
# 26.5 一次证明不了
bd(26.5, BIG(26.5, 700, 460, "1 次", c="red", d=0.1, s=130), arr(26.5, 900, 460, 1150, 460, c="ink", d=0.3), cross(26.5, 1400, 460, d=0.7), T(26.5, 960, 760, 60, "证明不了", c="ink", d=0.6))
# 27 叠加在变暖地球
gl, gi = globe(27, 760, 560, 200)
w_, wi = warm(27, 560, 260, 400, 80, d=0.2, dx=0)
bd(27, gl, w_, [sh(27, wi, 0, 40, 0.6, 0.8)], T(27, 1400, 500, 60, "叠加在变暖的地球上", c="red", d=0.4))
# 27.5 起点更高
step1, step2 = uid("stp"), uid("stp")
bd(27.5, [R(27.5, 400, 640, 400, 200, c="gold", fill="gold", idp=step1), pop(27.5, step1, 0.1), R(27.5, 1000, 520, 400, 320, c="red", fill="red", idp=step2), pop(27.5, step2, 0.4)],
   arr(27.5, 600, 600, 1200, 480, c="ink", d=0.6), waveheat(27.5, 1200, 500, d=0.8), T(27.5, 960, 260, 64, "热浪起点更高", c="red", d=0.5))
# 28 概率预报
pie = uid("pie")
bd(28, BIG(28, 960, 200, "友情提示", c="muted", d=0.1, s=80), [O(28, 700, 560, 180, c="ink", idp=pie), spin(28, pie, (700, 560), 30), P(28, "M700,560 L700,380", c="red", w=6, idp=uid("pp"))],
   T(28, 1300, 560, 64, "概率预报", c="ink", d=0.4), cloud(28, 1400, 380, 0.6, d=0.6, rain=False))
# 28.5 不是板上钉钉
nail = uid("nail")
bd(28.5, [P(28.5, "M960,300 L960,620 M880,300 L1040,300", c="ink", w=12, idp=nail), sh(28.5, nail, 0, 60, 0.2, 0.4), rot(28.5, nail, 20, (960, 620), 0.7, 0.5)],
   cross(28.5, 960, 460, d=0.9), T(28.5, 960, 800, 64, "不是板上钉钉", c="red", d=0.5), [R(28.5, 600, 620, 720, 60, c="ink", fill="muted", idp=uid("bd"))])
# 29 不等于一定洪水
bd(29, cloud(29, 700, 380, 1.0, d=0.1), T(29, 1350, 380, 70, "≠ 一定发洪水", c="ink", d=0.4), cross(29, 700, 640, d=0.7), ocean(29, 820))
# 29.5 季风 副高
bd(29.5, wind(29.5, 300, 900, 360, n=2, d=0.1, c="blue"), T(29.5, 600, 560, 56, "季风", c="blue", d=0.2),
   [O(29.5, 1350, 440, 160, c="red", idp=(hi := uid("hi"))), pulse(29.5, hi, 0.6), spin(29.5, hi, (1350, 440), 20)], T(29.5, 1350, 440, 56, "副热带高压", c="red", d=0.5),
   T(29.5, 960, 820, 56, "都有发言权", c="ink", d=0.8))
# 30 每月更新
cal_ = uid("cal")
bd(30, [R(30, 560, 300, 360, 380, c="ink", idp=cal_), R(30, 560, 300, 360, 90, c="red", fill="red", idp=cal_), pop(30, cal_, 0.1), wig(30, cal_, (740, 300), 4, 1.0)],
   [O(30, 1300, 480, 140, c="green", idp=(up := uid("up"))), spin(30, up, (1300, 480), 80)], T(30, 740, 560, 64, "每月", c="ink", d=0.3), T(30, 1300, 720, 56, "更新", c="green", d=0.5))
# 30.5 跟官方预报
bd(30.5, sound(30.5, 600, 460, 1.4, d=0.1), T(30.5, 1100, 460, 70, "跟着官方预报走", c="green", d=0.3), check(30.5, 1100, 640, d=0.7), cloud(30.5, 1550, 300, 0.6, d=0.5, rain=False))
# 31 信风再吹 冷水回来
bd(31, wind(31, 1600, 600, 260, n=3, d=0.1, c="blue"), cold(31, 1300, 900, d=0.5), ocean(31, 560), T(31, 500, 760, 60, "冷水回来", c="blue", d=0.6))
# 31.5 海又变绿
bd(31.5, patch(31.5, 360, 300, 1200, 360, "blue", d=0.3, to="green"), plank(31.5, 960, 470, 8, d=0.6, c="gold"), T(31.5, 960, 800, 70, "海又变绿", c="green", d=0.5))
# 32 小鳀盼
f, fi = fish(32, 760, 520, 1.6)
bd(32, f, [sh(32, fi + "*", 0, -40, 0.4, 0.3), sh(32, fi + "*", 0, 40, 0.7, 0.3)], Q(32, 1200, 300, s=160, d=0.5), T(32, 1350, 720, 60, "只盼一件事", c="ink", d=0.4), n=3)
# 32.5 拉尼娜回家做饭
f, fi = fish(32.5, 600, 540, 1.3)
f2, fi2 = fish(32.5, 1500, 540, 1.3, c="red", dirn=-1, d=0.2)
bd(32.5, f, f2, [sh(32.5, fi2 + "*", -500, 0, 0.3, 1.0)], plank(32.5, 1000, 360, 6, d=0.8), T(32.5, 960, 860, 70, "拉尼娜，快回家做饭", c="red", d=0.6), n=3)

# 上面的画板编号从第 2 句起写成了“句号 − 1”：统一往后挪一句，再补第 0.5、1.5 两张
for b in B:
    for e in b:
        e["at"] = e["at"] + 1 if e["at"] >= 1 else (1 if e["at"] == 0.5 else e["at"])
# 0.5 一年之间绿变蓝
E = []
for q in range(8):
    i = uid("pk")
    E += [O(0.5, 400 + 150 * q, 420 + 40 * (q % 3), 18, c="green", fill="green", idp=i), sh(0.5, i, 0, 500, 0.4 + 0.1 * q, 0.6)]
bd(0.5, E, BIG(0.5, 960, 300, "绿 → 蓝", c="blue", d=0.2, s=140), waves(0.5, 760, 200, 1700), waves(0.5, 820, 240, 1660))
# 1.5 饭没了
f, fi = fish(1.5, 760, 520, 1.6, sad=True)
E = []
for q in range(5):
    i = uid("pk")
    E += [O(1.5, 1200 + 70 * q, 420 + 50 * (q % 2), 16, c="green", fill="green", idp=i), sh(1.5, i, 600, -200, 0.2 + 0.15 * q, 0.7)]
bd(1.5, f, E, BIG(1.5, 1300, 760, "饭没了", c="red", d=0.6, s=120))
B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"NASA": "那萨", "3.05度": "三点零五度", "2.5度": "二点五度", "1998年": "一九九八年", "2016年": "二零一六年",
                                       "2024年": "二零二四年", "9月21日": "九月二十一日", "75%": "百分之七十五"})
