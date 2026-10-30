"""每日科普 2026-10-30（中文）：《凭啥让你一路绿灯？》
新闻：北京的红绿灯“变聪明了”——AI 智能信控，部分路口按实时车流调绿灯时长，主干路有望连续绿灯通行（北京商报；
新浪科技热点小时报 2026-10-30 02 时 第 12 条）。
用到的事实：
- IT之家 / 央视新闻（2026-06-04 海淀 AI 红绿灯）https://www.ithome.com/0/959/654.htm ：3D 轨迹拼接生成“全息路口”；大模型 50 秒内生成约 200 套配时方案；
  拥堵时绿灯自动延长 1～15 秒；传统红绿灯全天固定配时；四道口一带 13 个路口上线后整体车速提升约 21%、拥堵指数下降约 19%；
  全市信号灯联网 8000 处、绿波道路 500 条。
- 新浪科技热点小时报 2026-10-30 02 时 https://k.sina.com.cn/article_7857201856_1d45362c001908sya4.html （第 12 条，北京商报）。
- 常识：绿波的相位差 = 路口间距 ÷ 车速（500 m ÷ 13.9 m/s ≈ 36 s，是算例）；堵车波（刹车波）往车流后方传，没有事故也会“幽灵堵车”
  （2008 年日本名古屋环形跑道实验）。
推测：第 29～31 句“车和路口直接说话”（车路协同）是展望，片中说“也许”。
"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)
from popkit import bubble, car, car_drive, cute_bot  # noqa: E402

S = [
 ("八千个红绿灯，|北京让它们全部联了网。", "Eight thousand traffic lights. | Beijing has networked all of them."),
 ("现在AI开始管红绿灯，|有的路口车速提了两成。", "Now AI is running the lights. | Some junctions got about twenty percent faster."),
 ("今天的烧脑问题：|红绿灯怎么知道你要来？", "Today's brain teaser: | how does a traffic light know you're coming?"),
 ("先说老式红绿灯：|一天二十四小时，一个死节奏。", "First, the old lights: | one fixed rhythm, twenty four hours a day."),
 ("路上一辆车也好，|一百辆车也好，红灯都那么长。", "One car or | a hundred cars, the red lasts just as long."),
 ("就像食堂只开一个窗口，|队排多长都不加人。", "Like a canteen with one window open, | no matter how long the line gets."),
 ("于是有了你最熟悉的场景：|空荡荡的路口，等一个超长的红灯。", "So you get the classic scene: | an empty junction, and a really long red."),
 ("秘密武器一：绿波。|让一串红绿灯按顺序变绿。", "Secret weapon one: the green wave. | A row of lights turns green one after another."),
 ("就像体育场里的人浪，|一个接一个站起来。", "Like a stadium wave, | people standing up one after another."),
 ("你踩着这道波浪的速度开，|就一路都是绿灯。", "Drive at the speed of the wave, | and every light is green."),
 ("算笔账：两个路口相距五百米，|车速每小时五十公里。", "Do the math: two junctions five hundred meters apart, | cars at fifty kilometers an hour."),
 ("五十公里每小时，大约每秒十四米，|五百米要开三十六秒。", "Fifty an hour is about fourteen meters a second, | so five hundred meters takes thirty six seconds."),
 ("所以下一个路口，|要比上一个晚三十六秒变绿。", "So the next light | turns green thirty six seconds later."),
 ("北京已经有|五百条这样的绿波路。", "Beijing already has | five hundred green wave roads."),
 ("反转一：绿波怕堵车。|前面一排队，波浪就断了。", "Twist one: green waves hate traffic jams. | A queue ahead breaks the wave."),
 ("堵车本身也是一种波，|而且是往后传的。", "A traffic jam is a wave too, | and it travels backward."),
 ("前车一脚刹车，|后面一辆接一辆刹。", "One driver taps the brakes, | and the cars behind brake one by one."),
 ("所以有时候前面根本没事故，|你却莫名其妙地堵着。", "That's why sometimes there's no accident at all, | and you're still stuck."),
 ("秘密武器二：给路口装眼睛。|摄像头和雷达，数清每条车道的车。", "Secret weapon two: give the junction eyes. | Cameras and radar count every lane."),
 ("系统把每辆车的轨迹拼起来，|在电脑里造一个全息路口。", "The system stitches every car's path together, | into a digital twin of the junction."),
 ("然后大模型来排班：|五十秒内算出大约两百套方案。", "Then a big AI model makes the schedule: | about two hundred plans in fifty seconds."),
 ("挑出最好的一套，|堵的方向，绿灯多给一到十五秒。", "It picks the best one. | The jammed direction gets one to fifteen extra seconds of green."),
 ("反转二，最反直觉：|绿灯不是越长越好。", "Twist two, the surprising one: | longer green is not always better."),
 ("你这边多绿一秒，|横着那边就多红一秒。", "Every extra second of green for you | is an extra second of red for the cross street."),
 ("路口就像一块蛋糕，|一分钟就这么大，切给谁都是从别人那抢。", "A junction is like a cake. | A minute is a minute, and every slice comes from someone else."),
 ("所以AI真正在做的，|是让整片路网的总等待最少。", "So what the AI really does | is shrink the total waiting across the whole network."),
 ("结果：四道口一带十三个路口，|整体车速提了大约百分之二十一。", "The result: thirteen junctions in one Beijing district, | traffic about twenty one percent faster."),
 ("拥堵指数|降了大约百分之十九。", "And the congestion index | fell about nineteen percent."),
 ("反转三：将来的红绿灯，|也许要和车直接说话。", "Twist three: future traffic lights | may talk to cars directly."),
 ("车说：我十秒后到。|路口说：开每小时四十八公里，正好赶上绿灯。", "The car says: I'll arrive in ten seconds. | The light says: drive forty eight, and you'll catch the green."),
 ("到那时，自动驾驶的车|就是踩着绿波的冲浪手。", "Then self driving cars | become surfers riding the green wave."),
 ("友情提示：这些是官方报道的试点数字，|别的城市、别的时段不一定一样。", "Fine print: these are reported pilot numbers. | Other cities and other hours may differ."),
 ("而且再聪明的灯，|也救不了所有人同时出门的早高峰。", "And no light, however smart, | can save a rush hour when everyone leaves at once."),
 ("红绿灯怎么知道你要来？|它数车、算账，给你留一道波浪。", "So how does the light know you're coming? | It counts, it calculates, and it saves you a wave."),
 ("下次一路绿灯，|别以为是运气好。", "Next time you hit every green, | don't call it luck."),
 ("那是一个AI|在后面替你打节拍。", "That's an AI | keeping the beat for you."),
]
TITLE = {"zh": "凭啥让你一路绿灯？", "en": "How Do Traffic Lights Know You're Coming?"}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += [p] if isinstance(p, dict) else p
    E += star(a, 110, 110, 0.1, r=20) + star(a, 1810, 110, 0.3, r=20)
    B.append(E)


def ic(a, name, x, y, s=160, d=0.0, mv="bob", c="ink"):
    i = uid("ic")
    m = bob(a, i, 8, 1.2) if mv == "bob" else (spin(a, i, (x, y), 40) if mv == "spin" else wig(a, i, (x, y + s / 2), 8, 2.0))
    return [{"t": "icon", "at": a, "id": i, "name": name, "x": x, "y": y, "size": s, "c": c}, pop(a, i, d), m]


def light(a, x, y, k=1.0, d=0.0, on="red", seq=(), mood="happy"):
    """小灯：会眨眼的红绿灯角色。(x, y) = 灯杆底；on = 一开始亮哪盏；seq = [(秒, 颜色)] 依次换灯（旧灯被盖灭）。"""
    i, f = uid("lt"), uid("lf")
    top = y - 520 * k
    E = [R(a, x - 8 * k, y - 250 * k, 16 * k, 250 * k, c="ink", fill="muted", idp=i, sw=3),
         R(a, x - 75 * k, top, 150 * k, 300 * k, c="ink", fill="ink", idp=i, sw=4)]
    ys = {"red": top + 55 * k, "gold": top + 150 * k, "green": top + 245 * k}
    for cy in ys.values():
        E.append(O(a, x, cy, 38 * k, c="muted", fill="muted", idp=i, sw=3))
    mo = (f"M{x + 95 * k},{top + 175 * k} Q{x + 120 * k},{top + 195 * k} {x + 145 * k},{top + 175 * k}" if mood == "happy"
          else f"M{x + 95 * k},{top + 190 * k} Q{x + 120 * k},{top + 170 * k} {x + 145 * k},{top + 190 * k}")
    E += [R(a, x + 80 * k, top + 90 * k, 80 * k, 120 * k, c="ink", fill="paper", idp=f, sw=3),
          O(a, x + 105 * k, top + 135 * k, 8 * k, c="ink", fill="ink", idp=f), O(a, x + 135 * k, top + 135 * k, 8 * k, c="ink", fill="ink", idp=f),
          P(a, mo, c="ink", w=4, idp=f), pop(a, [i, f], d), wig(a, f, (x + 120 * k, top + 210 * k), 6, 1.6), bob(a, i, 3, 0.8)]
    L = uid("on")
    E += [O(a, x, ys[on], 38 * k, c=on, fill=on, idp=L, sw=3), pop(a, L, d + 0.1), pulse(a, L, d + 0.5)]
    prev = on
    for t, col in seq:
        off, L = uid("of"), uid("on")
        E += [O(a, x, ys[prev], 38 * k, c="muted", fill="muted", idp=off, sw=3), pop(a, off, t),
              O(a, x, ys[col], 38 * k, c=col, fill=col, idp=L, sw=3), pop(a, L, t + 0.05)]
        prev = col
    return E


def road(a, y=860, x0=80, x1=1840):
    i = uid("rd")
    E = [P(a, f"M{x0},{y} L{x1},{y}", c="ink", w=6)]
    for q in range(int((x1 - x0) / 160)):
        E.append(R(a, x0 + 160 * q + 40, y + 30, 80, 10, c="muted", fill="muted", idp=i, sw=1))
    E.append(sh(a, i, -160, 0, 0.0, 3.0))
    return E


def kar(a, x, y=860, k=0.7, dx=0, d=0.0, dur=1.2, mood="happy", c=None):
    """小 R 开车：轮子一直转，可选向右开 dx。"""
    i = uid("car")
    E = car(x, y, k, a, idp=i, mood=mood) + car_drive(x, y, k, a, idp=i, rpm=120) + [pop(a, i + "*", d)]
    if dx:
        E.append(sh(a, i + "*", dx, 0, d + 0.2, dur))
    return E


def wave_people(a, x, y, n=9, d=0.0, gap=150):
    """人浪：一排小人依次跳起来。"""
    E = []
    for q in range(n):
        j = uid("pp")
        px = x + gap * q
        E += [O(a, px, y - 150, 30, c="ink", fill="paper", idp=j),
              P(a, f"M{px},{y - 120} L{px},{y - 40} M{px - 40},{y - 150} L{px},{y - 100} L{px + 40},{y - 150} M{px},{y - 40} L{px - 25},{y + 20} M{px},{y - 40} L{px + 25},{y + 20}", c="ink", w=5, idp=j),
              pop(a, j, d + 0.03 * q), sh(a, j, 0, -70, d + 0.4 + 0.12 * q, 0.25), sh(a, j, 0, 0, d + 0.65 + 0.12 * q, 0.25)]
    return E


def cake(a, x, y, r=200, d=0.0, frac=0.5):
    i, sl = uid("ck"), uid("cs")
    import math
    ang = 2 * math.pi * frac
    ex, ey = x + r * math.sin(ang), y - r * math.cos(ang)
    big = 1 if frac > 0.5 else 0
    return [O(a, x, y, r, c="ink", fill="gold", idp=i), pop(a, i, d), spin(a, i, (x, y), 10),
            P(a, f"M{x},{y} L{x},{y - r} A{r},{r} 0 {big},1 {ex},{ey} Z", c="ink", w=5, fill="red", idp=sl), pop(a, sl, d + 0.3),
            sh(a, sl, 60, -40, d + 0.8, 0.5)]


def radar(a, x, y, d=0.0):
    i, b = uid("rr"), uid("rb")
    return [R(a, x - 50, y - 30, 100, 60, c="ink", fill="blue", idp=b), O(a, x, y, 22, c="ink", fill="paper", idp=b), pop(a, b, d), bob(a, b, 5, 1.4),
            P(a, f"M{x + 60},{y - 50} Q{x + 100},{y} {x + 60},{y + 50} M{x + 90},{y - 80} Q{x + 150},{y} {x + 90},{y + 80}", c="green", w=5, idp=i),
            pop(a, i, d + 0.2), pulse(a, i, d + 0.6), wig(a, i, (x, y), 6, 2.5)]


def queue(a, x, y=860, n=4, k=0.45, d=0.0, brake=False):
    E = []
    for q in range(n):
        px = x - 230 * q
        E += kar(a, px, y, k, d=d + 0.08 * q, mood="worried" if brake else "happy")
        if brake:
            j = uid("bl")
            E += [O(a, px - 95 * k * 2.2, y - 60, 16, c="red", fill="red", idp=j), pop(a, j, d + 0.4 + 0.25 * q), pulse(a, j, d + 0.6 + 0.25 * q)]
    return E


# ---------- 画板 ----------
lts = []
for q in range(5):
    lts += light(0, 330 + 330 * q, 800, 0.55, 0.06 * q, on="red", seq=[(1.0 + 0.15 * q, "green")])
bd(0, lts, BIG(0, 960, 200, "8000", c="red", d=0.2, s=150))
net = uid("net")
bd(0.5, light(0.5, 400, 860, 0.9, 0.0), ic(0.5, "globe", 1300, 450, 300, 0.2, mv="spin"),
   [P(0.5, "M560,450 C800,250 1000,250 1150,400", c="blue", w=6, idp=net), pop(0.5, net, 0.3), pulse(0.5, net, 0.8)], T(0.5, 1300, 750, 64, "全部联网", c="blue", d=0.5))
bd(1, cute_bot(450, 840, 1.0, 1, idp="b1"), [pop(1, "b1*", 0.0)], light(1, 1100, 860, 0.9, 0.2, seq=[(0.8, "green")]), BIG(1, 1550, 400, "AI", c="blue", d=0.3, s=160))
bd(1.5, road(1.5), kar(1.5, 300, 860, 0.7, dx=900, d=0.0, dur=1.6), BIG(1.5, 1100, 330, "车速 +20%", c="red", d=0.2, s=130))
bd(2, BIG(2, 1150, 380, "烧脑问题", c="red", d=0.0, s=130), ic(2, "question", 450, 450, 260, 0.2, mv="wig", c="red"), ic(2, "flame", 1700, 650, 140, 0.4, mv="wig", c="red"),
   ic(2, "gear", 1150, 620, 140, 0.5, mv="spin"))
bd(2.5, light(2.5, 600, 860, 1.0, 0.0, mood="o"), ic(2.5, "question", 950, 330, 180, 0.2, mv="wig", c="red"), road(2.5), kar(2.5, 1500, 860, 0.6, d=0.3),
   T(2.5, 1350, 300, 60, "你要来了？", c="blue", d=0.5))
bd(3, light(3, 500, 860, 1.0, 0.0, seq=[(0.7, "green"), (1.4, "gold"), (1.8, "red")]), T(3, 1300, 380, 70, "老式红绿灯", c="ink", d=0.2), ic(3, "clock", 1300, 600, 180, 0.3, mv="spin"))
bd(3.5, ic(3.5, "clock", 500, 450, 260, 0.0, mv="spin"), BIG(3.5, 1200, 380, "24 小时", c="red", d=0.2, s=130), T(3.5, 1200, 560, 64, "一个死节奏", c="blue", d=0.5),
   ic(3.5, "gear", 1650, 650, 140, 0.4, mv="spin"))
bd(4, road(4), light(4, 1500, 860, 0.9, 0.0), kar(4, 600, 860, 0.7, d=0.2), BIG(4, 960, 300, "1 辆", c="blue", d=0.3, s=130))
bd(4.5, road(4.5), light(4.5, 1650, 860, 0.9, 0.0), queue(4.5, 1300, 860, 5, 0.45, d=0.0), BIG(4.5, 800, 300, "100 辆", c="red", d=0.3, s=130), T(4.5, 800, 450, 56, "红灯一样长", c="ink", d=0.6))
win = uid("wn")
ppl = []
for q in range(6):
    j = uid("pp")
    px = 1000 + 140 * q
    ppl += [O(5, px, 560, 30, c="ink", fill="paper", idp=j), P(5, f"M{px},{590} L{px},{700} M{px - 35},{630} L{px + 35},{630}", c="ink", w=5, idp=j), pop(5, j, 0.08 * q), bob(5, j, 6, 1.0 + 0.2 * q)]
bd(5, [R(5, 400, 400, 400, 320, c="ink", fill="paper", idp=win), pop(5, win, 0.0)], ic(5, "flame", 600, 560, 120, 0.2, mv="wig", c="red"), ppl, T(5, 600, 320, 60, "只开一个窗口", c="blue", d=0.3))
bd(5.5, ppl and [], [R(5.5, 300, 400, 300, 320, c="ink", fill="paper", idp="wn55"), pop(5.5, "wn55", 0.0)],
   [x for q in range(8) for x in (O(5.5, 700 + 140 * q, 560, 28, c="ink", fill="paper", idp=f"q55{q}"), pop(5.5, f"q55{q}", 0.06 * q), bob(5.5, f"q55{q}", 6, 1.0 + 0.15 * q))],
   arr(5.5, 1800, 750, 800, 750, c="red", d=0.4), T(5.5, 1200, 330, 60, "不加人", c="red", d=0.5))
bd(6, road(6), light(6, 1300, 860, 1.0, 0.0, mood="o"), kar(6, 500, 860, 0.7, d=0.2, mood="worried"), T(6, 800, 300, 64, "你最熟悉的场景", c="blue", d=0.3))
bd(6.5, road(6.5), light(6.5, 1300, 860, 1.0, 0.0), kar(6.5, 600, 860, 0.7, d=0.0, mood="worried"), ic(6.5, "clock", 950, 330, 180, 0.2, mv="spin"),
   BIG(6.5, 1650, 330, "...", c="red", d=0.4, s=150))
bd(7, BIG(7, 960, 360, "秘密武器一", c="blue", d=0.0, s=120), BIG(7, 960, 560, "绿波", c="green", d=0.3, s=160), star(7, 500, 650, 0.4, r=50), star(7, 1420, 650, 0.5, r=50))
lts = []
for q in range(5):
    lts += light(7.5, 330 + 330 * q, 860, 0.55, 0.0, on="red", seq=[(0.4 + 0.35 * q, "green")])
bd(7.5, lts, T(7.5, 960, 200, 60, "一个接一个变绿", c="green", d=0.2))
bd(8, wave_people(8, 360, 700, 9, 0.0), T(8, 960, 250, 64, "人浪", c="blue", d=0.2))
bd(8.5, wave_people(8.5, 260, 760, 11, 0.0, gap=140), arr(8.5, 400, 380, 1500, 380, c="red", d=0.4), T(8.5, 960, 280, 56, "一个接一个站起来", c="ink", d=0.3))
lts = []
for q in range(4):
    lts += light(9, 450 + 400 * q, 860, 0.5, 0.0, on="red", seq=[(0.3 + 0.4 * q, "green")])
bd(9, road(9), lts, kar(9, 200, 860, 0.5, dx=1300, d=0.1, dur=1.7))
bd(9.5, road(9.5), kar(9.5, 400, 860, 0.7, dx=600, d=0.0, dur=1.5), BIG(9.5, 1100, 350, "一路绿灯", c="green", d=0.3, s=140), check(9.5, 1650, 400, d=0.6))
bd(10, road(10), light(10, 400, 860, 0.6, 0.0, on="green"), light(10, 1500, 860, 0.6, 0.1, on="red"), arr(10, 520, 450, 1380, 450, c="blue", d=0.3),
   BIG(10, 960, 360, "500 米", c="blue", d=0.4, s=120))
bd(10.5, road(10.5), kar(10.5, 500, 860, 0.8, dx=500, d=0.0, dur=1.5), BIG(10.5, 1100, 350, "50 公里/时", c="red", d=0.2, s=120), ic(10.5, "gear", 1650, 600, 140, 0.4, mv="spin"))
bd(11, T(11, 600, 320, 72, "50 公里/时", c="ink", d=0.0), arr(11, 900, 320, 1100, 320, c="red", d=0.2), BIG(11, 1450, 330, "≈14 米/秒", c="red", d=0.3, s=100),
   road(11), kar(11, 400, 860, 0.6, dx=700, d=0.2, dur=1.4))
bd(11.5, T(11.5, 960, 280, 64, "500 ÷ 14", c="blue", d=0.0), BIG(11.5, 960, 470, "≈36 秒", c="red", d=0.3, s=150), ic(11.5, "clock", 400, 500, 200, 0.2, mv="spin"),
   ic(11.5, "ruler", 1550, 500, 150, 0.4, mv="wig"))
bd(12, light(12, 500, 860, 0.8, 0.0, on="green"), light(12, 1400, 860, 0.8, 0.1, on="red"), arr(12, 650, 500, 1250, 500, c="blue", d=0.3),
   T(12, 950, 300, 56, "下一个路口", c="ink", d=0.2))
bd(12.5, light(12.5, 500, 860, 0.8, 0.0, on="green"), light(12.5, 1400, 860, 0.8, 0.0, on="red", seq=[(1.3, "green")]), ic(12.5, "clock", 950, 500, 180, 0.1, mv="spin"),
   BIG(12.5, 950, 280, "晚 36 秒", c="red", d=0.3, s=110))
gw = []
for q in range(5):
    j = uid("gw")
    gw += [P(13, f"M{300 + 280 * q},{750} L{520 + 280 * q},{750}", c="green", w=14, idp=j), pop(13, j, 0.1 * q), pulse(13, j, 0.6 + 0.1 * q)]
bd(13, gw, ic(13, "map_pin", 960, 520, 160, 0.0, mv="bob", c="red"), T(13, 960, 300, 64, "北京已经有", c="ink", d=0.2))
bd(13.5, BIG(13.5, 960, 380, "500 条", c="green", d=0.0, s=160), T(13.5, 960, 560, 64, "绿波路", c="green", d=0.3), road(13.5), kar(13.5, 300, 860, 0.5, dx=1200, d=0.2, dur=1.6))
bd(14, BIG(14, 960, 380, "反转一", c="red", d=0.0, s=150), ic(14, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), ic(14, "question", 1470, 450, 150, 0.4, mv="wig", c="red"))
gw2 = uid("gw")
bd(14.5, road(14.5), queue(14.5, 1500, 860, 5, 0.45, d=0.0, brake=True),
   [P(14.5, "M200,500 L800,500", c="green", w=14, idp=gw2), pop(14.5, gw2, 0.2), sh(14.5, gw2, 0, 200, 1.0, 0.5)], cross(14.5, 950, 500, d=0.9), T(14.5, 500, 400, 56, "波浪断了", c="red", d=0.6))
bd(15, road(15), queue(15, 1600, 860, 6, 0.4, d=0.0), arr(15, 1500, 450, 500, 450, c="red", d=0.3), T(15, 960, 330, 64, "堵车也是一种波", c="ink", d=0.2))
bd(15.5, road(15.5), queue(15.5, 1600, 860, 6, 0.4, d=0.0, brake=True), BIG(15.5, 960, 350, "往后传", c="red", d=0.2, s=130))
bd(16, road(16), kar(16, 1400, 860, 0.7, d=0.0, mood="o"), [O(16, 1100, 800, 22, c="red", fill="red", idp="bk16"), pop(16, "bk16", 0.3), pulse(16, "bk16", 0.6)],
   T(16, 1400, 380, 64, "一脚刹车", c="red", d=0.3), ic(16, "flame", 500, 500, 140, 0.4, mv="wig", c="red"))
bd(16.5, road(16.5), queue(16.5, 1700, 860, 6, 0.4, d=0.0, brake=True), arr(16.5, 1600, 400, 400, 400, c="red", d=0.2), T(16.5, 960, 300, 56, "一辆接一辆", c="ink", d=0.1))
bd(17, road(17), queue(17, 1500, 860, 5, 0.45, d=0.0), cross(17, 1750, 500, d=0.3), T(17, 1600, 330, 56, "没事故", c="blue", d=0.2), ic(17, "question", 500, 450, 160, 0.4, mv="wig", c="red"))
bd(17.5, road(17.5), queue(17.5, 1300, 860, 5, 0.45, d=0.0, brake=True), BIG(17.5, 960, 330, "幽灵堵车", c="red", d=0.3, s=130))
bd(18, BIG(18, 960, 360, "秘密武器二", c="blue", d=0.0, s=120), ic(18, "eye", 960, 600, 200, 0.3, mv="wig"), star(18, 500, 600, 0.4, r=50), star(18, 1420, 600, 0.5, r=50))
bd(18.5, light(18.5, 500, 860, 0.9, 0.0), radar(18.5, 800, 380, 0.2), ic(18.5, "eye", 1100, 380, 150, 0.3, mv="wig"), road(18.5), queue(18.5, 1700, 860, 3, 0.45, d=0.4),
   T(18.5, 1400, 300, 56, "数清每条车道", c="blue", d=0.5))
trk = []
for q in range(4):
    j = uid("tk")
    trk += [P(19, f"M{300},{350 + 120 * q} C{700},{300 + 140 * q} {1100},{450 + 60 * q} {1600},{380 + 110 * q}", c=["blue", "red", "green", "gold"][q], w=6, idp=j),
            {"t": "move", "at": 19, "kind": "grow", "targets": [j], "axis": "x", "pivot": [300, 400], "dur": 0.8, "delay": 0.1 + 0.2 * q}]
bd(19, trk, ic(19, "computer", 960, 830, 140, 0.3, mv="bob"), T(19, 960, 230, 60, "把轨迹拼起来", c="ink", d=0.2))
bd(19.5, ic(19.5, "computer", 960, 520, 360, 0.0, mv="bob"), kar(19.5, 960, 500, 0.35, dx=120, d=0.3, dur=1.0), BIG(19.5, 960, 250, "全息路口", c="blue", d=0.2, s=110),
   ic(19.5, "gear", 1550, 650, 140, 0.4, mv="spin"))
bd(20, cute_bot(500, 840, 1.0, 20, idp="b20"), [pop(20, "b20*", 0.0)], ic(20, "chip", 1250, 450, 220, 0.2, mv="spin"), T(20, 1250, 700, 64, "大模型排班", c="blue", d=0.3))
cards = []
for q in range(8):
    j = uid("cd")
    cards += [R(20.5, 300 + 170 * q, 500, 130, 170, c="ink", fill="paper", idp=j, sw=4), pop(20.5, j, 0.06 * q), bob(20.5, j, 6, 1.0 + 0.15 * q)]
bd(20.5, cards, BIG(20.5, 700, 320, "200 套", c="red", d=0.2, s=120), BIG(20.5, 1350, 320, "50 秒", c="blue", d=0.4, s=120))
bd(21, cards and [], [R(21, 860, 380, 200, 260, c="ink", fill="gold", idp="best21", sw=6), pop(21, "best21", 0.0), pulse(21, "best21", 0.5), bob(21, "best21", 8, 1.2)],
   check(21, 960, 510, d=0.3), cross(21, 450, 510, d=0.4), cross(21, 1470, 510, d=0.5))
bd(21.5, light(21.5, 500, 860, 0.9, 0.0, on="green"), bar(21.5, 1000, 820, 160, 200, "green", 0.2), bar(21.5, 1250, 820, 160, 480, "green", 0.6),
   BIG(21.5, 1450, 280, "+1~15 秒", c="green", d=0.5, s=110))
bd(22, BIG(22, 960, 380, "反转二", c="red", d=0.0, s=150), ic(22, "flame", 450, 450, 150, 0.2, mv="wig", c="red"), ic(22, "question", 1470, 450, 150, 0.4, mv="wig", c="red"))
bd(22.5, light(22.5, 500, 860, 0.9, 0.0, on="green"), T(22.5, 1250, 380, 64, "绿灯越长越好？", c="blue", d=0.2), cross(22.5, 1250, 600, d=0.6))
bd(23, light(23, 500, 860, 0.9, 0.0, on="green"), BIG(23, 960, 350, "+1 秒", c="green", d=0.2, s=120), kar(23, 900, 860, 0.5, dx=300, d=0.2))
bd(23.5, light(23.5, 500, 860, 0.9, 0.0, on="green"), light(23.5, 1400, 860, 0.9, 0.0, on="red", mood="o"), BIG(23.5, 950, 350, "+1 秒", c="red", d=0.3, s=110), T(23.5, 950, 500, 56, "横着那边", c="ink", d=0.4))
bd(24, cake(24, 700, 520, 220, 0.0, 0.5), T(24, 1350, 450, 64, "路口 = 蛋糕", c="blue", d=0.3), ic(24, "clock", 1350, 650, 150, 0.4, mv="spin"))
bd(24.5, cake(24.5, 600, 520, 220, 0.0, 0.65), BIG(24.5, 1300, 380, "1 分钟", c="red", d=0.2, s=120), T(24.5, 1300, 560, 56, "从别人那抢", c="ink", d=0.6))
nw = []
for q in range(3):
    for r_ in range(2):
        nw += light(25, 420 + 540 * q, 520 + 380 * r_, 0.32, 0.05 * (q + r_), on="green" if (q + r_) % 2 else "red")
bd(25, nw, T(25, 960, 160, 56, "AI 真正在做的", c="blue", d=0.2))
bd(25.5, bar(25.5, 500, 820, 200, 500, "red", 0.0), bar(25.5, 1100, 820, 200, 250, "green", 0.4), T(25.5, 600, 260, 52, "总等待", c="red", d=0.1),
   arr(25.5, 750, 450, 1050, 600, c="green", d=0.5), BIG(25.5, 1550, 400, "最少", c="green", d=0.7, s=110))
bd(26, ic(26, "map_pin", 600, 450, 220, 0.0, mv="bob", c="red"), BIG(26, 1250, 380, "13 个路口", c="blue", d=0.2, s=110), T(26, 1250, 550, 56, "四道口一带", c="ink", d=0.4),
   road(26), kar(26, 300, 860, 0.5, dx=1200, d=0.3))
bd(26.5, road(26.5), kar(26.5, 300, 860, 0.7, dx=1000, d=0.0, dur=1.3), BIG(26.5, 960, 350, "车速 +21%", c="green", d=0.2, s=140), star(26.5, 1600, 550, 0.6, r=40))
bd(27, T(27, 960, 320, 70, "拥堵指数", c="ink", d=0.0), road(27), queue(27, 1500, 860, 5, 0.45, d=0.1, brake=True))
bd(27.5, bar(27.5, 700, 820, 220, 450, "red", 0.0), bar(27.5, 1100, 820, 220, 360, "green", 0.4), BIG(27.5, 1500, 350, "−19%", c="green", d=0.6, s=150),
   arr(27.5, 920, 380, 1080, 460, c="green", d=0.5))
bd(28, BIG(28, 960, 380, "反转三", c="red", d=0.0, s=150), light(28, 450, 860, 0.7, 0.2), kar(28, 1450, 860, 0.6, d=0.3))
bd(28.5, light(28.5, 500, 860, 0.9, 0.0), kar(28.5, 1350, 860, 0.8, d=0.1), [P(28.5, "M680,450 C900,300 1100,300 1300,550", c="blue", w=5, idp="lk28"), pop(28.5, "lk28", 0.3),
   {"t": "move", "at": 28.5, "kind": "signal", "targets": ["lk28"], "speed": 260}], T(28.5, 960, 220, 56, "也许：和车直接说话", c="blue", d=0.4))
bd(29, road(29), kar(29, 700, 860, 0.8, d=0.0), [dict(e, id="bb29") for e in bubble(900, 260, 520, 160, 29, "10 秒后到", s=56)] + [pop(29, "bb29", 0.2), bob(29, "bb29", 6, 1.2)], light(29, 1600, 860, 0.7, 0.1), ic(29, "clock", 400, 400, 140, 0.3, mv="spin"))
bd(29.5, road(29.5), light(29.5, 1600, 860, 0.8, 0.0, seq=[(1.4, "green")]), kar(29.5, 400, 860, 0.7, dx=700, d=0.4, dur=1.2),
   BIG(29.5, 800, 300, "48 公里/时", c="green", d=0.2, s=110))
surf = uid("sf")
bd(30, road(30), cute_bot(800, 840, 0.8, 30, idp="b30"), [pop(30, "b30*", 0.0), sh(30, "b30*", 300, 0, 0.5, 1.2)], T(30, 1400, 380, 60, "自动驾驶", c="blue", d=0.3),
   ic(30, "gear", 400, 450, 140, 0.4, mv="spin"))
bd(30.5, [P(30.5, "M100,750 C400,600 600,900 900,750 C1200,600 1400,900 1800,750", c="green", w=12, idp=surf), pop(30.5, surf, 0.0), wig(30.5, surf, (960, 750), 4, 1.0)],
   kar(30.5, 600, 700, 0.6, dx=700, d=0.2, dur=1.6), BIG(30.5, 960, 330, "冲浪手", c="blue", d=0.3, s=130))
bd(31, BIG(31, 960, 380, "友情提示", c="blue", d=0.0, s=130), ic(31, "magnifier", 500, 620, 150, 0.2, mv="wig"), T(31, 1250, 620, 56, "试点数字", c="red", d=0.4))
bd(31.5, ic(31.5, "map_pin", 500, 450, 180, 0.0, mv="bob", c="red"), ic(31.5, "clock", 1400, 450, 180, 0.2, mv="spin"), T(31.5, 960, 700, 60, "别处、别的时段不一定一样", c="ink", d=0.4))
bd(32, light(32, 500, 860, 0.9, 0.0), ic(32, "chip", 1200, 450, 200, 0.2, mv="spin"), T(32, 1250, 700, 56, "再聪明的灯", c="blue", d=0.3))
bd(32.5, road(32.5), queue(32.5, 1800, 860, 7, 0.38, d=0.0, brake=True), BIG(32.5, 960, 330, "早高峰", c="red", d=0.3, s=140))
bd(33, light(33, 500, 860, 1.0, 0.0, mood="o"), ic(33, "question", 1250, 450, 220, 0.2, mv="wig", c="red"), T(33, 1250, 720, 56, "怎么知道你要来？", c="blue", d=0.3))
lts = []
for q in range(4):
    lts += light(33.5, 450 + 400 * q, 860, 0.5, 0.0, on="red", seq=[(0.3 + 0.35 * q, "green")])
bd(33.5, lts, T(33.5, 960, 200, 56, "数车 · 算账 · 留一道波浪", c="green", d=0.3))
bd(34, road(34), kar(34, 400, 860, 0.7, dx=900, d=0.0, dur=1.5), T(34, 960, 330, 64, "下次一路绿灯", c="green", d=0.2))
bd(34.5, BIG(34.5, 960, 380, "不是运气", c="red", d=0.0, s=140), cross(34.5, 960, 600, d=0.3), star(34.5, 450, 600, 0.3, r=50), star(34.5, 1470, 600, 0.5, r=50))
bd(35, cute_bot(600, 840, 1.0, 35, idp="b35"), [pop(35, "b35*", 0.0), wig(35, "b35*", (600, 840), 6, 2.0)], ic(35, "clock", 1250, 450, 200, 0.2, mv="spin"), T(35, 1250, 700, 60, "一个 AI", c="blue", d=0.3))
lts = []
for q in range(4):
    lts += light(35.5, 450 + 400 * q, 860, 0.5, 0.0, on="red", seq=[(0.2 + 0.3 * q, "green")])
bd(35.5, lts, BIG(35.5, 960, 220, "替你打节拍", c="green", d=0.3, s=110))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={})
