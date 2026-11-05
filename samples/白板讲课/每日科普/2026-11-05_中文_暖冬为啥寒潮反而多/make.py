"""每日科普 2026-11-05（中文）：《暖冬为啥寒潮反而多？》
热点：中国气象局 2026-11-03 新闻发布会：最强厄尔尼诺将明显影响我国，今冬气温总体偏高、寒潮频次略偏多（新浪天气热点小时报 2026-11-04 07 时上榜；
  热摸爽 2026-11-05 每日热点摘要第 10 条；澎湃、人民网、21 世纪经济报道、腾讯新闻等转载）。
事实（中国气象局 / 国家气候中心，澎湃 2026-11-04、腾讯新闻“青观气象”2026-11-05）：
- 本次是有监测记录以来最强的厄尔尼诺事件，预计秋末冬初（11—12 月前后）达到峰值；只用约 5 个月达到超强标准，前三次超强事件（1982—83、1997—98、2015—16）用了 8 到 15 个月。
- 今冬全国气温总体偏高，但寒潮频次略偏多、冷暖起伏大，“前冬冷、后冬暖”，12 月和 1 月强降温、强升温频繁；内蒙古东北部和东北地区西部偏低。
- 全国降水总体偏多，南方显著偏多；北方强降雪多发；华东西南部、华中中南部、华南北部、西南东部有阶段性低温雨雪冰冻。
- 热量冬春季逐步传到印度洋、热带北大西洋，影响约持续半年；专家（国家气候中心）说每次背景不同，影响不会简单复制。
教科书常识：El Niño 是西班牙语“小男孩/圣婴”，秘鲁渔民圣诞前后发现海水变暖；平时信风由东向西吹，把暖水堆到西太平洋，
  西太平洋海面比东太平洋高约半米（NOAA）；东太平洋冷水上翻、鱼多；太平洋约占地球表面三分之一；海洋表层几米水的热容量约等于整个大气。
比喻和例子（我们的）：澡盆里的水晃回来；海洋 = 充电宝；“三天零下五度、四天十五度”的一周是打比方。
出处：
- https://www.thepaper.cn/newsDetail_forward_34408369
- https://news.qq.com/rain/a/20261105A06UEU00
- https://k.sina.com.cn/article_7857201856_1d45362c001908tkf8.html
- https://remoshuang.com/daily/2026-11-05
- http://env.people.com.cn/n1/2026/1104/c1010-40827120.html
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, rot, sh, spin,  # noqa: E402
                     star, uid, waves, wig)
from popkit import cute_drop, stick  # noqa: E402

S = [
 ("史上最强的厄尔尼诺，|正在太平洋上“充满电”。", "The strongest El Niño on record | is charging up over the Pacific."),
 ("可气象局说：今冬总体偏暖，|寒潮却略偏多。", "Yet forecasters say this winter will be warmer overall, | with slightly more cold waves."),
 ("又暖又冷？|这预报是不是自相矛盾？", "Warm and cold? | Is the forecast contradicting itself?"),
 ("十一月三日，中国气象局开发布会，|这条冲上了热点榜。", "On November third, the China Meteorological Administration held a briefing, | and it hit the trending lists."),
 ("他们说，这次是有监测记录以来|最强的厄尔尼诺。", "They said this is the strongest El Niño | since records began."),
 ("今天的烧脑问题：|暖冬来了，为啥羽绒服还不能收？", "Today's brain teaser: | if it's a warm winter, why keep the down jacket?"),
 ("先认识主角：一滴热海水，|小尼。", "Meet our hero: a drop of warm sea water, | Little Niño."),
 ("厄尔尼诺是西班牙语，|意思是“小男孩”。", "El Niño is Spanish | for 'the little boy'."),
 ("秘鲁渔民发现，每隔几年，|圣诞前后海水变暖，鱼也少了。", "Peruvian fishermen noticed that every few years, | the sea warmed around Christmas and the fish vanished."),
 ("平时，太平洋上的信风|从东往西吹。", "Normally, the trade winds | blow across the Pacific from east to west."),
 ("信风把表层的热水|一路推到印度尼西亚那边。", "They push the warm surface water | all the way toward Indonesia."),
 ("西边的海面，|比东边高出大约半米。", "So the sea surface in the west | sits about half a meter higher than in the east."),
 ("东边秘鲁那头，|深海冷水翻上来，鱼特别多。", "Off Peru in the east, | cold deep water wells up, and fish thrive."),
 ("反转一：信风一松劲，|热水就“哗”地流回东边。", "Twist one: when the trade winds weaken, | the warm water sloshes back east."),
 ("就像澡盆里的水，|你一松手，水就往回晃。", "Like water in a bathtub: | let go, and it sloshes back."),
 ("于是大半个赤道太平洋|都热了起来。", "So a huge stretch of the equatorial Pacific | heats up."),
 ("太平洋有多大？|占了地球表面的三分之一。", "How big is the Pacific? | About a third of Earth's surface."),
 ("反转二：海水是个超级充电宝。|海面下几米的水，存的热就顶得上整个大气。", "Twist two: the ocean is a giant power bank. | The top few meters hold as much heat as the whole atmosphere."),
 ("今年只用了大约五个月，就冲到超强；|以前要八到十五个月。", "This year it went super strong in about five months. | Before, it took eight to fifteen."),
 ("国家气候中心说，|峰值大概在秋末冬初。", "China's National Climate Center says | it should peak in late autumn or early winter."),
 ("充满了电，就要放电：|热量一点点送进大气。", "Once charged, it discharges: | heat seeps into the air, bit by bit."),
 ("大气的环流一改道，|全球的天气都被搅动。", "When the air currents shift, | weather all over the world gets stirred."),
 ("这股劲能拖大约半年，|一直到明年春天。", "The effect can last about half a year, | into next spring."),
 ("对我们：全国气温总体偏高，|南方的雨雪显著偏多。", "For China: temperatures mostly above normal, | and much more rain and snow in the south."),
 ("反转三，最反直觉：|偏暖，不等于天天暖。", "Twist three, the most counterintuitive: | warmer does not mean warm every day."),
 ("气象局说：寒潮略偏多，|冷暖起伏大，像坐过山车。", "Forecasters say: slightly more cold waves, | big swings, like a roller coaster."),
 ("打个比方：一周里三天零下五度，|四天十五度。", "Picture a week with three days at minus five, | and four days at fifteen."),
 ("平均一算，六度多，挺暖；|可那三天，你冻得直哆嗦。", "Average it out: over six degrees, not bad. | But on those three days, you shiver."),
 ("平均数会骗人，|起伏才是要命的。", "Averages can fool you. | The swings are what bite."),
 ("预报还说“前冬冷、后冬暖”，|十二月、一月忽冷忽热最频繁。", "The forecast also says: colder early, warmer late, | with the wildest swings in December and January."),
 ("北方要防强降温和大雪，|南方要防低温雨雪冰冻。", "The north should watch for cold snaps and heavy snow, | the south for freezing rain and ice."),
 ("内蒙古东北部和东北西部，|还可能比常年偏冷。", "Northeast Inner Mongolia and western Northeast China | may even run colder than usual."),
 ("友情提示：这是季节预测，说的是可能性，|不是说哪一天一定冷。", "Fine print: this is a seasonal forecast, about odds, | not a promise about any single day."),
 ("专家也说：每次厄尔尼诺背景不同，|影响不会简单照抄。", "Experts also say every El Niño is different, | so the effects never simply repeat."),
 ("所以，暖冬为啥寒潮反而多？|因为平均暖了，起伏却更大。", "So why more cold waves in a warm winter? | The average rises, but the swings get bigger."),
 ("秋裤先别收，|小尼的电，才刚开始放。", "Keep your long johns handy. | Little Niño has only just started to discharge."),
]
TITLE = {"zh": "暖冬为啥寒潮反而多？", "en": "A Warm Winter With More Cold Waves?"}

B = []


def bd(a, *parts):
    E = []

    def flat(p):
        if isinstance(p, dict):
            E.append(p)
        else:
            for q in p:
                flat(q)
    flat(parts)
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    B.append(E)


def t(a, x, y, s, text, c="ink", d=0.0):
    return T(a, x, y, s * 1.5, text, c=c, d=d)


def big(a, x, y, text, c="red", d=0.0, s=140):
    return BIG(a, x, y, text, c=c, d=d, s=s)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def man(a, x, y, k=1.4, d=0.0, arms="down"):
    i = uid("mn")
    return stick(x, y, k, a, idp=i, arms=arms) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": 3, "hz": 1.6}]


def shiver(a, x, y, k=1.4, d=0.0):
    i = uid("sv")
    return stick(x, y, k, a, idp=i, arms="down") + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d},
                                                    {"t": "move", "at": a, "kind": "wiggle", "targets": [i + "*"], "pivot": [x, y], "amp": 6, "hz": 6}]


def nino(a, x, y, k=1.0, d=0.0, mood="happy", warm=True):
    i = uid("nn")
    return cute_drop(x, y, k, a, idp=i, mood=mood, warm=warm) + [{"t": "move", "at": a, "kind": "pop", "targets": [i + "*"], "dur": 0.35, "delay": d}]


def sea(a, y=760, d=0.0, c="blue", x0=120, x1=1800, tilt=0):
    """A wavy sea line (optionally tilted: west higher by `tilt` px) that keeps rolling."""
    i = uid("sea")
    pts = " ".join(f"Q{x0 + (x1 - x0) * (q + 0.5) / 8},{y - tilt * (1 - (q + 0.5) / 8) + (24 if q % 2 else -24)} {x0 + (x1 - x0) * (q + 1) / 8},{y - tilt * (1 - (q + 1) / 8)}"
                   for q in range(8))
    return [P(a, f"M{x0},{y - tilt} " + pts, c=c, w=7, idp=i), pop(a, i, d), wig(a, i, ((x0 + x1) / 2, y), 2, 1.2)]


def wind(a, x, y, dx, d=0.0, n=3, dur=1.6):
    """Trade-wind streaks blowing along dx."""
    E = []
    for q in range(n):
        i = uid("wd")
        yy = y + 60 * q
        E += [P(a, f"M{x},{yy} Q{x + dx * 0.15},{yy - 20} {x + dx * 0.3},{yy}", c="muted", w=5, idp=i), pop(a, i, d + 0.1 * q), sh(a, i, dx * 0.7, 0, d + 0.2 + 0.1 * q, dur)]
    return E


def thermo(a, x, y, s=240, d=0.0, c="red"):
    return ic(a, "thermometer", x, y, s, d, mv="wig", c=c)


def coaster(a, x0=200, x1=1720, y=650, amp=220, d=0.0, c="red", n=3):
    """A roller-coaster temperature curve with a little cart riding it."""
    i, j = uid("cs"), uid("ct")
    w = (x1 - x0) / (2 * n)
    dd = f"M{x0},{y}" + "".join(f" Q{x0 + w * (2 * q + 0.5)},{y - amp * 2 if q % 2 == 0 else y + amp * 2} {x0 + w * (2 * q + 1)},{y}"
                                    f" Q{x0 + w * (2 * q + 1.5)},{y + amp * 2 if q % 2 == 0 else y - amp * 2} {x0 + w * (2 * q + 2)},{y}" for q in range(n))
    return [P(a, dd, c=c, w=8, idp=i), pop(a, i, d), O(a, x0, y, 26, c="ink", fill="gold", idp=j), pop(a, j, d + 0.2), sh(a, j, x1 - x0, 0, d + 0.3, 3.0), wig(a, i, ((x0 + x1) / 2, y), 2, 1)]


def pacific(a, d=0.0, tilt=0, warm_x=1400, label=True):
    """Side view of the equatorial Pacific: Indonesia (west, left), Peru (east, right)."""
    E = sea(a, 620, d, tilt=tilt, x0=300, x1=1620)
    i, j = uid("ld"), uid("ld")
    E += [R(a, 120, 560, 180, 300, c="green", fill="green", idp=i), pop(a, i, d), R(a, 1620, 560, 180, 300, c="ink", fill="paper", idp=j), pop(a, j, d + 0.1)]
    if label:
        E += [t(a, 210, 920, 36, "印尼", d=d + 0.1), t(a, 1710, 920, 36, "秘鲁", d=d + 0.2)]
    return E


# ---------- 画板 ----------
bd(0, pacific(0, 0.0, label=False), nino(0, 960, 520, 1.3, 0.1), [ic(0, "flame", 600 + 300 * q, 760, 90, 0.3 + 0.1 * q, mv="wig", c="red") for q in range(3)], big(0, 960, 220, "史上最强", c="red", d=0.4, s=130))
bd(0.5, ic(0.5, "battery", 600, 560, 320, 0.0, mv="wig", c="green"), bar(0.5, 1100, 900, 120, 200, "gold", 0.2), bar(0.5, 1300, 900, 120, 400, "red", 0.4), bar(0.5, 1500, 900, 120, 600, "red", 0.6), nino(0.5, 600, 260, 0.5, 0.3))
bd(1, thermo(1, 500, 560, 300, 0.0), arr(1, 500, 800, 500, 350, c="red", d=0.3), big(1, 1250, 400, "偏暖", c="red", d=0.2, s=170), ic(1, "sun", 1250, 750, 180, 0.4, mv="spin", c="gold"))
bd(1.5, ic(1.5, "wind", 500, 520, 260, 0.0, mv="wig", c="blue"), ic(1.5, "cloud", 1000, 450, 200, 0.2, mv="bob", c="muted"), big(1.5, 1300, 760, "寒潮偏多", c="blue", d=0.3, s=120), thermo(1.5, 1600, 450, 200, 0.4, c="blue"))
bd(2, nino(2, 960, 600, 1.4, 0.0, mood="o"), ic(2, "sun", 450, 450, 200, 0.2, mv="spin", c="gold"), ic(2, "wind", 1470, 450, 200, 0.3, mv="wig", c="blue"), ic(2, "question", 960, 220, 140, 0.4, mv="wig", c="red"))
bd(2.5, ic(2.5, "question", 600, 550, 300, 0.0, mv="wig", c="red"), big(2.5, 1300, 420, "自相矛盾？", c="red", d=0.2, s=120), man(2.5, 1300, 950, 1.2, 0.3, arms="up"))
bd(3, big(3, 960, 250, "11月3日", c="red", d=0.0, s=130), ic(3, "building", 500, 650, 260, 0.1, mv="bob"), ic(3, "speaker", 960, 650, 200, 0.2, mv="wig"), ic(3, "satellite", 1420, 650, 200, 0.3, mv="bob"))
bd(3.5, ic(3.5, "phone", 550, 560, 300, 0.0, mv="wig"), t(3.5, 1250, 380, 70, "热点榜", c="red", d=0.2), bar(3.5, 1050, 900, 110, 200, "gold", 0.2), bar(3.5, 1220, 900, 110, 350, "gold", 0.3), bar(3.5, 1390, 900, 110, 480, "red", 0.4))
bd(4, ic(4, "clock", 500, 560, 260, 0.0, mv="spin"), t(4, 1250, 380, 64, "有监测记录以来", d=0.1), big(4, 1250, 580, "最强", c="red", d=0.3, s=180), star(4, 1650, 750, 0.4, r=50))
bd(4.5, bar(4.5, 450, 950, 150, 300, "gold", 0.0), t(4.5, 525, 1010, 40, "1982", d=0.0), bar(4.5, 750, 950, 150, 380, "gold", 0.15), t(4.5, 825, 1010, 40, "1997", d=0.15),
   bar(4.5, 1050, 950, 150, 360, "gold", 0.3), t(4.5, 1125, 1010, 40, "2015", d=0.3), bar(4.5, 1350, 950, 150, 600, "red", 0.5), t(4.5, 1425, 1010, 40, "今年", c="red", d=0.5), nino(4.5, 1650, 400, 0.6, 0.6))
bd(5, big(5, 1150, 300, "烧脑问题", c="red", d=0.0, s=130), ic(5, "question", 450, 450, 260, 0.2, mv="wig", c="red"), nino(5, 1150, 700, 0.9, 0.3, mood="o"))
bd(5.5, ic(5.5, "sun", 500, 450, 220, 0.0, mv="spin", c="gold"), shiver(5.5, 1000, 950, 1.6, 0.2), R(5.5, 880, 520, 240, 250, c="blue", fill="paper", sw=8), t(5.5, 1450, 500, 64, "羽绒服？", c="blue", d=0.3), ic(5.5, "question", 1450, 750, 140, 0.4, mv="wig", c="red"))
bd(6, nino(6, 960, 560, 2.0, 0.0), t(6, 960, 950, 70, "小尼", c="red", d=0.3), waves(6, 1000, c="blue"))
bd(6.5, nino(6.5, 600, 600, 1.3, 0.0), nino(6.5, 1300, 600, 1.0, 0.2, warm=False, mood="o"), t(6.5, 600, 950, 56, "热海水", c="red", d=0.3), t(6.5, 1300, 950, 56, "冷海水", c="blue", d=0.4))
bd(7, big(7, 1250, 380, "El Niño", c="red", d=0.0, s=150), stick(550, 950, 1.5, 7, idp="boy", arms="up"), pop(7, "boy*", 0.1), wig(7, "boy*", (550, 950), 5, 2), t(7, 1250, 620, 70, "小男孩", d=0.3))
bd(7.5, ic(7.5, "globe", 600, 550, 300, 0.0, mv="spin", c="blue"), t(7.5, 1250, 450, 70, "西班牙语", d=0.2), nino(7.5, 1250, 750, 0.6, 0.3))
bd(8, sea(8, 750, 0.0), [ic(8, "water", 500 + 180 * q, 900, 70, 0.1 * q, mv="bob", c="blue") for q in range(4)], man(8, 1400, 700, 1.2, 0.2), t(8, 1350, 300, 64, "秘鲁渔民", d=0.3), ic(8, "clock", 500, 400, 160, 0.4, mv="spin"))
bd(8.5, sea(8.5, 650, 0.0, c="red"), thermo(8.5, 500, 400, 220, 0.1), big(8.5, 1200, 330, "圣诞前后", c="red", d=0.2, s=110), ic(8.5, "water", 1100, 850, 90, 0.3, mv="bob", c="blue"), cross(8.5, 1100, 850, d=0.6))
bd(9, pacific(9, 0.0), wind(9, 1500, 380, -1100, 0.2), arr(9, 1500, 300, 500, 300, c="ink", d=0.4), t(9, 960, 220, 56, "信风：东 → 西", d=0.3))
bd(9.5, ic(9.5, "wind", 1300, 500, 280, 0.0, mv="wig", c="muted"), arr(9.5, 1100, 500, 500, 500, c="blue", d=0.2), ic(9.5, "globe", 400, 500, 200, 0.3, mv="spin", c="blue"), wind(9.5, 1500, 800, -900, 0.3))
bd(10, pacific(10, 0.0, tilt=60), nino(10, 1300, 500, 0.7, 0.1), sh(10, [], 0, 0, 0, 0.1) if False else [], wind(10, 1500, 350, -1000, 0.2))
bd(10.5, pacific(10.5, 0.0, tilt=90), [nino(10.5, 450 + 130 * q, 480 - 15 * (3 - q), 0.45, 0.2 + 0.1 * q) for q in range(4)], t(10.5, 600, 250, 56, "热水堆到西边", c="red", d=0.4))
bd(11, pacific(11, 0.0, tilt=120), arr(11, 330, 420, 330, 560, c="red", d=0.3), big(11, 1100, 300, "高约半米", c="red", d=0.3, s=120), ic(11, "ruler", 1300, 500, 140, 0.5, mv="wig"))
bd(11.5, R(11.5, 500, 400, 300, 450, c="blue", fill="paper", sw=6), R(11.5, 1100, 550, 300, 300, c="blue", fill="paper", sw=6), sea(11.5, 400, 0.1, x0=500, x1=800), sea(11.5, 550, 0.2, x0=1100, x1=1400),
   t(11.5, 650, 950, 56, "西", d=0.2), t(11.5, 1250, 950, 56, "东", d=0.3), arr(11.5, 950, 470, 950, 560, c="red", d=0.5), nino(11.5, 650, 650, 0.5, 0.4))
bd(12, pacific(12, 0.0, tilt=60), [nino(12, 1450, 950 - 80 * q, 0.35, 0.2 + 0.1 * q, warm=False) for q in range(3)], arr(12, 1350, 950, 1350, 700, c="blue", d=0.4))
bd(12.5, sea(12.5, 450, 0.0), [ic(12.5, "water", 500 + 230 * q, 650 + (q % 2) * 150, 110, 0.1 * q, mv="bob", c="blue") for q in range(5)], t(12.5, 960, 250, 70, "鱼特别多", c="green", d=0.3))
bd(13, big(13, 960, 260, "反转一", c="red", d=0.0, s=140), ic(13, "wind", 500, 650, 220, 0.1, mv="wig", c="muted"), cross(13, 500, 650, d=0.4), nino(13, 1200, 700, 1.0, 0.3), arr(13, 1350, 700, 1650, 700, c="red", d=0.5))
bd(13.5, pacific(13.5, 0.0, tilt=0), [nino(13.5, 500, 480, 0.5, 0.1)], sh(13.5, [], 0, 0, 0, 0.1) if False else [], arr(13.5, 600, 400, 1500, 400, c="red", d=0.2), t(13.5, 1050, 250, 70, "哗——", c="red", d=0.3),
   [ic(13.5, "flame", 900 + 200 * q, 700, 70, 0.4 + 0.1 * q, mv="wig", c="red") for q in range(3)])
bd(14, R(14, 400, 450, 1100, 400, c="ink", fill="paper", sw=8), sea(14, 600, 0.1, x0=420, x1=1480, tilt=80), stick(1650, 950, 1.3, 14, idp="hd", arms="up"), pop(14, "hd*", 0.2), wig(14, "hd*", (1650, 950), 4, 2), t(14, 960, 300, 64, "澡盆", d=0.2))
bd(14.5, R(14.5, 400, 450, 1100, 400, c="ink", fill="paper", sw=8), sea(14.5, 600, 0.0, x0=420, x1=1480, tilt=-80), arr(14.5, 600, 400, 1350, 400, c="blue", d=0.2), t(14.5, 960, 300, 64, "一松手，水往回晃", c="red", d=0.3), nino(14.5, 1300, 750, 0.4, 0.4))
bd(15, pacific(15, 0.0), [O(15, 450 + 180 * q, 680, 40, c="red", fill="red", idp=f"hot{q}") for q in range(7)], [pop(15, f"hot{q}", 0.1 + 0.1 * q) for q in range(7)], [wig(15, f"hot{q}", (450 + 180 * q, 680), 5, 2) for q in range(7)])
bd(15.5, thermo(15.5, 500, 560, 300, 0.0), arr(15.5, 500, 800, 500, 330, c="red", d=0.3), t(15.5, 1250, 400, 70, "大半个赤道太平洋", d=0.2), sea(15.5, 700, 0.3, c="red", x0=900, x1=1700))
bd(16, ic(16, "globe", 700, 560, 380, 0.0, mv="spin", c="blue"), big(16, 1400, 450, "1/3", c="red", d=0.2, s=200), t(16, 1400, 700, 56, "地球表面", d=0.3))
bd(16.5, O(16.5, 960, 560, 330, c="blue", fill="paper", idp="ea16", sw=8), pop(16.5, "ea16", 0.0), P(16.5, "M960,230 A330,330 0 0,1 1250,720 L960,560 Z", c="blue", w=6, idp="pac16"),
   pop(16.5, "pac16", 0.2), rot(16.5, "pac16", 30, (960, 560), 0.4, 1.0), nino(16.5, 1450, 750, 0.6, 0.4), t(16.5, 500, 900, 56, "太平洋", c="blue", d=0.4))
bd(17, big(17, 960, 260, "反转二", c="red", d=0.0, s=140), ic(17, "battery", 600, 650, 300, 0.1, mv="wig", c="green"), nino(17, 1300, 700, 1.0, 0.3), ic(17, "flame", 1300, 400, 90, 0.4, mv="wig", c="red"))
bd(17.5, sea(17.5, 400, 0.0), R(17.5, 300, 420, 500, 150, c="blue", fill="paper", sw=6, idp="lay"), pop(17.5, "lay", 0.2), t(17.5, 550, 640, 50, "海面下几米", c="blue", d=0.2),
   t(17.5, 960, 495, 80, "=", c="red", d=0.4), ic(17.5, "cloud", 1400, 450, 300, 0.4, mv="bob", c="muted"), t(17.5, 1400, 700, 50, "整个大气", d=0.5), bar(17.5, 650, 950, 150, 250, "red", 0.5), bar(17.5, 1350, 950, 150, 250, "gold", 0.6))
bd(18, big(18, 1200, 380, "≈5个月", c="red", d=0.0, s=150), ic(18, "rocket", 500, 600, 300, 0.1, mv="wig"), t(18, 1200, 620, 60, "冲到超强", d=0.3), ic(18, "clock", 1200, 850, 140, 0.4, mv="spin"))
bd(18.5, bar(18.5, 600, 950, 200, 220, "red", 0.0), t(18.5, 700, 1010, 44, "今年 5", c="red", d=0.0), bar(18.5, 1000, 950, 200, 360, "gold", 0.2), t(18.5, 1100, 1010, 44, "以前 8", d=0.2),
   bar(18.5, 1300, 950, 200, 650, "gold", 0.4), t(18.5, 1400, 1010, 44, "以前 15", d=0.4), nino(18.5, 400, 500, 0.6, 0.5))
bd(19, ic(19, "satellite", 500, 560, 280, 0.0, mv="bob"), t(19, 1250, 380, 64, "国家气候中心", c="blue", d=0.2), ic(19, "computer", 1250, 650, 200, 0.3, mv="wig"))
bd(19.5, P(19.5, "M300,850 Q700,820 960,350 Q1220,820 1620,850", c="red", w=10, idp="pk"), pop(19.5, "pk", 0.0), wig(19.5, "pk", (960, 850), 2, 1), nino(19.5, 960, 260, 0.6, 0.3),
   t(19.5, 960, 960, 56, "秋末冬初到顶", c="red", d=0.4), ic(19.5, "cloud", 400, 400, 140, 0.3, mv="bob", c="muted"))
bd(20, ic(20, "battery", 500, 560, 280, 0.0, mv="wig", c="red"), arr(20, 680, 560, 1100, 560, c="red", d=0.2), ic(20, "cloud", 1350, 500, 280, 0.3, mv="bob", c="muted"), t(20, 960, 850, 64, "放电", c="red", d=0.4))
bd(20.5, sea(20.5, 800, 0.0, c="red"), [ic(20.5, "flame", 450 + 250 * q, 650, 80, 0.1 * q, mv="wig", c="red") for q in range(5)],
   [arr(20.5, 450 + 250 * q, 580, 450 + 250 * q, 330, c="red", d=0.4 + 0.08 * q) for q in range(5)], ic(20.5, "cloud", 960, 230, 160, 0.5, mv="bob", c="muted"))
bd(21, ic(21, "globe", 960, 560, 400, 0.0, mv="spin", c="blue"), [ic(21, "wind", x, y, 120, 0.2 + 0.1 * q, mv="wig", c="muted") for q, (x, y) in enumerate([(500, 350), (1420, 350), (500, 800), (1420, 800)])])
bd(21.5, [ic(21.5, n_, 400 + 370 * q, 560, 200, 0.1 * q, mv="wig" if q % 2 else "bob", c=c_) for q, (n_, c_) in enumerate([("cloud", "muted"), ("sun", "gold"), ("water", "blue"), ("wind", "muted")])],
   t(21.5, 960, 850, 64, "全球天气被搅动", c="red", d=0.4))
bd(22, big(22, 1200, 400, "≈半年", c="red", d=0.0, s=160), ic(22, "clock", 500, 560, 280, 0.1, mv="spin"), nino(22, 1200, 750, 0.6, 0.3))
bd(22.5, ic(22.5, "sunrise", 600, 560, 280, 0.0, mv="bob", c="gold"), t(22.5, 1250, 450, 70, "一直到明年春天", d=0.2), ic(22.5, "flame", 1250, 700, 120, 0.3, mv="wig", c="green"))
bd(23, thermo(23, 500, 560, 300, 0.0), big(23, 1250, 400, "总体偏高", c="red", d=0.2, s=120), ic(23, "map_pin", 1250, 720, 140, 0.4, mv="bob", c="red"))
bd(23.5, ic(23.5, "cloud", 600, 450, 300, 0.0, mv="bob", c="muted"), [ic(23.5, "water", 480 + 120 * q, 700 + (q % 2) * 60, 70, 0.1 + 0.08 * q, mv="bob", c="blue") for q in range(3)],
   t(23.5, 1300, 450, 64, "南方雨雪", d=0.2), big(23.5, 1300, 650, "显著偏多", c="blue", d=0.4, s=110))
bd(24, big(24, 960, 260, "反转三", c="red", d=0.0, s=140), thermo(24, 500, 650, 240, 0.1), nino(24, 1350, 700, 1.0, 0.3, mood="o"))
bd(24.5, ic(24.5, "sun", 500, 550, 260, 0.0, mv="spin", c="gold"), t(24.5, 960, 550, 100, "≠", c="red", d=0.3), ic(24.5, "clock", 1400, 550, 260, 0.2, mv="spin"), t(24.5, 960, 850, 64, "偏暖 ≠ 天天暖", c="red", d=0.4))
bd(25, ic(25, "wind", 500, 560, 260, 0.0, mv="wig", c="blue"), big(25, 1250, 400, "寒潮略偏多", c="blue", d=0.2, s=110), shiver(25, 1250, 950, 1.1, 0.3))
bd(25.5, coaster(25.5, 200, 1720, 600, 180, 0.0), t(25.5, 960, 1000, 60, "冷暖起伏大", c="red", d=0.3), man(25.5, 200, 520, 0.6, 0.2, arms="up"))
bd(26, [R(26, 250 + 205 * q, 700, 170, 230, c="blue", fill="paper", sw=6) for q in range(3)], [t(26, 335 + 205 * q, 815, 44, "-5°", c="blue", d=0.1 * q) for q in range(3)],
   [ic(26, "wind", 335 + 205 * q, 560, 90, 0.1 * q, mv="wig", c="blue") for q in range(3)], big(26, 1300, 330, "打个比方", c="ink", d=0.3, s=100))
bd(26.5, [R(26.5, 250 + 205 * q, 700, 170, 230, c="blue" if q < 3 else "red", fill="paper", sw=6) for q in range(7)], [t(26.5, 335 + 205 * q, 815, 44, "-5°" if q < 3 else "15°", c="blue" if q < 3 else "red", d=0.08 * q) for q in range(7)],
   [ic(26.5, "sun", 335 + 205 * q, 560, 90, 0.3 + 0.08 * q, mv="spin", c="gold") for q in range(3, 7)], [ic(26.5, "wind", 335 + 205 * q, 560, 90, 0.0, mv="wig", c="blue") for q in range(3)])
bd(27, big(27, 960, 330, "平均 6°多", c="red", d=0.0, s=130), thermo(27, 500, 750, 200, 0.2), ic(27, "check", 1400, 750, 160, 0.4, mv="bob", c="green"), ic(27, "sun", 960, 700, 140, 0.3, mv="spin", c="gold"))
bd(27.5, shiver(27.5, 600, 950, 1.6, 0.0), shiver(27.5, 1000, 950, 1.3, 0.1), ic(27.5, "wind", 1450, 500, 240, 0.2, mv="wig", c="blue"), t(27.5, 1400, 800, 64, "冻得直哆嗦", c="blue", d=0.3))
bd(28, big(28, 960, 330, "平均数会骗人", c="red", d=0.0, s=110), P(28, "M300,700 L1620,700", c="muted", w=4, idp="avg"), pop(28, "avg", 0.1), coaster(28, 300, 1620, 700, 120, 0.2, c="blue", n=2))
bd(28.5, coaster(28.5, 200, 1720, 600, 230, 0.0, n=4), t(28.5, 960, 1000, 64, "起伏才要命", c="red", d=0.3), shiver(28.5, 1650, 950, 0.8, 0.4))
bd(29, P(29, "M300,500 Q600,900 960,700 Q1300,450 1620,400", c="red", w=9, idp="tr29"), pop(29, "tr29", 0.0), wig(29, "tr29", (960, 650), 2, 1), t(29, 500, 300, 56, "前冬冷", c="blue", d=0.2),
   t(29, 1450, 300, 56, "后冬暖", c="red", d=0.3), ic(29, "wind", 600, 900, 110, 0.4, mv="wig", c="blue"), ic(29, "sun", 1500, 600, 120, 0.5, mv="spin", c="gold"))
bd(29.5, coaster(29.5, 250, 1670, 650, 200, 0.0, n=4), big(29.5, 960, 250, "12月 · 1月", c="red", d=0.3, s=110), ic(29.5, "clock", 1700, 950, 100, 0.4, mv="spin"))
bd(30, ic(30, "wind", 500, 450, 240, 0.0, mv="wig", c="blue"), [ic(30, "cloud", 900 + 250 * q, 400, 160, 0.1 * q, mv="bob", c="muted") for q in range(3)],
   [O(30, 900 + 120 * q, 650 + (q % 3) * 80, 14, c="blue", fill="paper", idp=f"sn{q}") for q in range(7)], [pop(30, f"sn{q}", 0.2 + 0.05 * q) for q in range(7)],
   [sh(30, f"sn{q}", 0, 200, 0.3 + 0.05 * q, 1.5) for q in range(7)], t(30, 500, 750, 56, "北方：大雪", d=0.3))
bd(30.5, ic(30.5, "cloud", 700, 400, 260, 0.0, mv="bob", c="muted"), [ic(30.5, "water", 600 + 100 * q, 620, 60, 0.1 * q, mv="bob", c="blue") for q in range(3)],
   P(30.5, "M400,850 L1100,850", c="blue", w=12, idp="ice"), pop(30.5, "ice", 0.3), wig(30.5, "ice", (750, 850), 2, 4), t(30.5, 1450, 500, 64, "南方：冻雨", c="blue", d=0.3), shiver(30.5, 1450, 950, 0.9, 0.4))
bd(31, ic(31, "map_pin", 600, 500, 260, 0.0, mv="bob", c="blue"), t(31, 1250, 380, 56, "内蒙古东北部", d=0.2), t(31, 1250, 500, 56, "东北西部", d=0.3), thermo(31, 1250, 750, 180, 0.4, c="blue"))
bd(31.5, thermo(31.5, 600, 560, 280, 0.0, c="blue"), arr(31.5, 600, 350, 600, 800, c="blue", d=0.3), big(31.5, 1250, 450, "偏冷", c="blue", d=0.2, s=170), shiver(31.5, 1250, 950, 1.0, 0.4))
bd(32, big(32, 960, 280, "友情提示", c="blue", d=0.0, s=120), t(32, 960, 470, 56, "季节预测：说的是可能性", d=0.2), ic(32, "magnifier", 600, 750, 180, 0.3, mv="wig"), nino(32, 1350, 760, 0.6, 0.4, mood="o"))
bd(32.5, [R(32.5, 400 + 160 * q, 550, 120, 140, c="ink", fill="paper", sw=5) for q in range(7)], [ic(32.5, "question", 460 + 160 * q, 620, 70, 0.1 * q, mv="wig", c="red") for q in range(7)],
   t(32.5, 960, 850, 60, "不是哪一天一定冷", c="red", d=0.4))
bd(33, man(33, 500, 950, 1.4, 0.0), ic(33, "computer", 500, 350, 140, 0.2, mv="wig"), [nino(33, 1000 + 250 * q, 600, 0.5 + 0.1 * q, 0.2 + 0.1 * q) for q in range(3)], t(33, 1250, 900, 56, "每次不一样", d=0.4))
bd(33.5, bar(33.5, 500, 900, 160, 400, "gold", 0.0), bar(33.5, 800, 900, 160, 250, "blue", 0.15), bar(33.5, 1100, 900, 160, 500, "red", 0.3), cross(33.5, 1450, 600, d=0.5), t(33.5, 1450, 850, 56, "不会照抄", c="red", d=0.4))
bd(34, nino(34, 600, 600, 1.2, 0.0, mood="o"), ic(34, "wind", 1250, 450, 200, 0.2, mv="wig", c="blue"), ic(34, "question", 1250, 750, 180, 0.3, mv="wig", c="red"))
bd(34.5, P(34.5, "M200,600 L1720,560", c="red", w=6, idp="avg2"), pop(34.5, "avg2", 0.0), coaster(34.5, 200, 1720, 580, 220, 0.2, c="blue", n=4), t(34.5, 500, 250, 56, "平均暖了", c="red", d=0.3), t(34.5, 1400, 250, 56, "起伏更大", c="blue", d=0.4))
bd(35, man(35, 600, 950, 1.5, 0.0, arms="up"), R(35, 950, 450, 220, 380, c="blue", fill="paper", sw=8, idp="pants"), pop(35, "pants", 0.2), wig(35, "pants", (1060, 450), 6, 2), t(35, 1550, 650, 70, "秋裤先别收", c="blue", d=0.3))
bd(35.5, pacific(35.5, 0.0, label=False), nino(35.5, 960, 480, 1.2, 0.1), ic(35.5, "battery", 1450, 300, 140, 0.3, mv="wig", c="red"), [ic(35.5, "flame", 700 + 260 * q, 760, 80, 0.4 + 0.1 * q, mv="wig", c="red") for q in range(3)])

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"El Niño": "厄尔尼诺", "11月3日": "十一月三日"})
