"""每日科普 2026-10-29（中文）：《闭着眼，怎么知道蚊子在左边？》
新闻：Advanced Bionics（索诺瓦旗下）的新一代人工耳蜗 INTEGRO CI，主打 AI 声音处理和 SoundFinder 声源定位，计划在第九届进博会亮相。
热榜：新浪科技热点小时报 2026-10-29 11 时 第 7 条（“360° 人工耳蜗”）。
事实出处：
- 新浪科技热点小时报 2026-10-29 11时 https://k.sina.com.cn/article_7857201856_1d45362c001908sv7s.html ：INTEGRO CI 能判断声音方向，计划在进博会全球首秀。
- Vermoegenszentrum / AWP 2026-10-14 https://www.vermoegenszentrum.ch/en/stock-exchange-and-markets/news/advanced-bionics-wins-tuv-approval-integro-ci-cochlear-implant ：
  INTEGRO CI 获 TÜV 认证，AI 声音处理、SoundFinder 定位，美国 FDA 尚未批准，欧洲部分市场在售。
- 通用声学/听觉科学（教科书知识）：声速约 340 米/秒；双耳时间差最大约 0.6–0.7 毫秒；人最灵时能分辨约 10 微秒量级的双耳时间差；
  低频主要靠时间差、高频主要靠头影造成的音量差（双工理论）；前后混淆靠耳廓滤波和转头/歪头解决；Jeffress 延迟线模型在仓鸮脑中有证据；
  麦克风阵列用到达时间差估方向。
估算/推测：“绕过脑袋约 20 厘米”是估算；“眨眼一百多毫秒”是常见范围；耳蜗实际效果片中说“要看真实使用数据”，不做评价。
比喻：两人从两头往中间跑着送信（延迟线）。贯穿的梗：蚊子——结尾蚊子早飞了，还叮了右边。
    python3 make.py <kokoro 模型目录> | --boards-only | --fake   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, sound, spin,  # noqa: E402
                     star, uid, wig)
from popkit import cute_bot, cute_fly  # noqa: E402

S = [
 ("闭上眼，一只蚊子在耳边嗡嗡，|你一巴掌就知道往左边拍。", "Eyes closed, a mosquito buzzes by your ear, | and you know to slap left."),
 ("耳朵又没长眼睛，|它怎么知道声音从哪来？", "Your ears have no eyes. | So how do they know where a sound comes from?"),
 ("即将开幕的进博会上，一款人工耳蜗要来首秀，|卖点就是：能找出声音的方向。", "At the upcoming China Import Expo, a cochlear implant debuts, | and its selling point is finding where sound comes from."),
 ("它叫INTEGRO，|据报道用AI来处理声音。", "It's called Integro, | and it reportedly uses AI to process sound."),
 ("今天的烧脑问题：|两只耳朵，怎么算出一个方向？", "Today's brain teaser: | how do two ears work out a direction?"),
 ("先看你的脑袋：两只耳朵，|一左一右，中间隔着一颗头。", "Look at your head: two ears, | one left, one right, a head in between."),
 ("蚊子在左边，声音先到左耳，|再绕过脑袋，才到右耳。", "Mosquito on the left: the sound hits your left ear first, | then wraps around your head to the right."),
 ("声音一秒钟走三百四十米，|绕过脑袋，估算大约二十厘米。", "Sound travels 340 meters a second, | and the trip around your head is roughly 20 centimeters."),
 ("算一下：两只耳朵最多|只差零点六毫秒。", "Do the math: the two ears differ by at most | 0.6 milliseconds."),
 ("眨一下眼要一百多毫秒，|这个差比眨眼短几百倍。", "A blink takes over 100 milliseconds. | This gap is hundreds of times shorter."),
 ("可你的大脑，最灵的时候能分出|大约十微秒的差别！", "Yet at its best your brain can tell apart | about ten microseconds!"),
 ("怎么做到的？想象两个人|从两头往中间跑着送信。", "How? Picture two runners | carrying letters from both ends toward the middle."),
 ("左耳的信先出发，两人就在偏右的地方碰头；|大脑看在哪碰头，就知道方向。", "The left letter leaves first, so they meet right of center. | Where they meet tells the brain the direction."),
 ("这叫“延迟线”模型，|在猫头鹰的脑子里真找到了这样的线路。", "It's called the delay-line model, | and barn owls really have wiring like this."),
 ("反转一：光靠时间差，|遇到高音就犯迷糊。", "Twist one: timing alone | gets confused by high notes."),
 ("高音的波很短，脑袋就像一堵墙，|挡出一片“声音的影子”。", "High notes have short waves, so your head acts like a wall | and casts a sound shadow."),
 ("所以离得远的那只耳朵，|听到的声音更小。", "So the far ear | hears it quieter."),
 ("低音看时间差，高音看音量差，|大脑两样一起用。", "Low notes: timing. High notes: loudness. | The brain uses both."),
 ("反转二，最反直觉：|正前方和正后方，时间差一模一样！", "Twist two, the weird one: | dead ahead and dead behind give the exact same timing!"),
 ("前面和后面的声音，|到两只耳朵一样远。", "A sound in front and one behind | are equally far from both ears."),
 ("这时候靠耳廓，|就是你耳朵上那些弯弯绕绕。", "Now your outer ear takes over, | all those curls and folds."),
 ("声音从不同方向进来，被弯弯绕绕弹一弹，|音色就悄悄变了。", "Sound from each direction bounces off the folds, | and its tone quietly changes."),
 ("大脑从小就记住了：|这种音色，就是在后面。", "Your brain learned long ago: | this tone means behind you."),
 ("还拿不准？你会下意识地|歪一下头。", "Still not sure? You tilt your head | without thinking."),
 ("头一歪，时间差就变了，|答案马上出来。", "Tilt, and the timing changes. | Answer found."),
 ("想帮人找方向的设备，也得用好几个麦克风，|把这笔账再算一遍。", "A device that helps people find direction needs several microphones | to do the same math again."),
 ("机器人也一样：|扫地机、机器狗、智能音箱。", "Robots do it too: | robot vacuums, robot dogs, smart speakers."),
 ("智能音箱上有一圈麦克风，|比的就是谁先听到。", "A smart speaker has a ring of microphones, | comparing who hears it first."),
 ("麦克风隔得越远，|方向算得越准。", "The farther apart the microphones, | the sharper the direction."),
 ("友情提示：听得出方向，|不等于听得清楚。", "Fine print: hearing the direction | is not the same as hearing clearly."),
 ("这款耳蜗好不好用，|还要看真实使用的数据。", "How well this implant works | still depends on real-world data."),
 ("所以两只耳朵怎么算方向？|比时间、比音量、听音色、再歪个头。", "So how do two ears find a direction? | Timing, loudness, tone, and a head tilt."),
 ("一套微秒级的算法，|天天在你头上跑。", "A microsecond-level algorithm | running on your head all day."),
 ("可惜，算出蚊子在左边，|不代表你拍得着。", "Sadly, knowing the mosquito is on the left | doesn't mean you'll hit it."),
 ("它早飞了，|还顺手在右边叮了一口。", "It's long gone, | and it bit your right side on the way out."),
]
TITLE = {"zh": "闭着眼，怎么知道蚊子在左边？", "en": "Eyes Closed, How Do You Know the Mosquito Is on the Left?"}

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


def E_(a, cx, cy, w, h, c="ink", fill=None, idp=None, sw=5):
    e = {"t": "ellipse", "at": a, "x": cx - w / 2, "y": cy - h / 2, "w": w, "h": h, "c": c, "sw": sw}
    if fill:
        e["fill"] = fill
    if idp:
        e["id"] = idp
    return e


def head(a, x, y, k=1.0, d=0.0, mood="happy", eyes="closed"):
    """小耳朵：圆脑袋，两只会扇的大耳朵（左耳 el、右耳 er），闭着眼。"""
    h, el, er = uid("hd"), uid("el"), uid("er")
    ey = (f"M{x - 70 * k},{y - 20 * k} Q{x - 50 * k},{y - 5 * k} {x - 30 * k},{y - 20 * k} M{x + 30 * k},{y - 20 * k} Q{x + 50 * k},{y - 5 * k} {x + 70 * k},{y - 20 * k}"
          if eyes == "closed" else
          f"M{x - 50 * k},{y - 30 * k} m-12,0 a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0 M{x + 50 * k},{y - 30 * k} m-12,0 a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0")
    mo = {"happy": f"M{x - 30 * k},{y + 45 * k} Q{x},{y + 70 * k} {x + 30 * k},{y + 45 * k}",
          "o": f"M{x - 12 * k},{y + 55 * k} a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0",
          "sad": f"M{x - 30 * k},{y + 65 * k} Q{x},{y + 40 * k} {x + 30 * k},{y + 65 * k}"}[mood]
    E = [E_(a, x - 150 * k, y, 60 * k, 110 * k, c="ink", fill="red", idp=el), E_(a, x + 150 * k, y, 60 * k, 110 * k, c="ink", fill="red", idp=er),
         O(a, x, y, 140 * k, c="ink", fill="paper", idp=h), P(a, ey, c="ink", w=5, idp=h), P(a, mo, c="ink", w=5, idp=h),
         E_(a, x - 85 * k, y + 30 * k, 36 * k, 18 * k, c="red", fill="red", idp=h, sw=2), E_(a, x + 85 * k, y + 30 * k, 36 * k, 18 * k, c="red", fill="red", idp=h, sw=2),
         pop(a, [h, el, er], d), bob(a, h, 6 * k, 1.0), wig(a, el, (x - 130 * k, y), 10, 2.2), wig(a, er, (x + 130 * k, y), -10, 2.2)]
    return E, [h, el, er]


def mos(a, x, y, k=0.5, d=0.0, mood="happy", go=None):
    """蚊子（用 cute_fly 画），翅膀嗡嗡扇，飘着；go=(dx, dy) 飞走。"""
    i = uid("ms")
    E = cute_fly(x, y, k, a, idp=i, mood=mood) + [pop(a, i + "*", d)]
    if go:
        E.append(sh(a, i + "*", go[0], go[1], d + 0.5, 0.8))
    return E


def dot(a, x0, y0, x1, y1, c="red", d=0.0, dur=0.8, r=16):
    """一个小点（声音、信）从 (x0,y0) 跑到 (x1,y1)。"""
    i = uid("dt")
    return [O(a, x0, y0, r, c=c, fill=c, idp=i), pop(a, i, d), sh(a, i, x1 - x0, y1 - y0, d + 0.15, dur)]


def mic(a, x, y, d=0.0, c="ink"):
    i = uid("mc")
    return [R(a, x - 18, y - 40, 36, 60, c=c, fill="muted", idp=i, sw=4), P(a, f"M{x - 28},{y} Q{x},{y + 40} {x + 28},{y} M{x},{y + 30} L{x},{y + 55}", c=c, w=4, idp=i),
            pop(a, i, d), pulse(a, i, d + 0.5)]


def runner(a, x, y, k=0.7, d=0.0, go=0, c="blue"):
    """送信的小人：腿摆，手里一封信，往中间跑。"""
    i, lg = uid("rn"), uid("rl")
    s = 1 if go >= 0 else -1
    E = [O(a, x, y - 210 * k, 40 * k, c="ink", fill="paper", idp=i),
         P(a, f"M{x},{y - 170 * k} L{x},{y - 30 * k} M{x},{y - 140 * k} L{x + s * 70 * k},{y - 130 * k}", c="ink", w=7, idp=i),
         R(a, x + s * 70 * k - 25 * k, y - 155 * k, 50 * k, 34 * k, c=c, fill=c, idp=i, sw=3),
         P(a, f"M{x},{y - 30 * k} L{x - 45 * k},{y + 80 * k} M{x},{y - 30 * k} L{x + 45 * k},{y + 80 * k}", c="ink", w=7, idp=lg),
         pop(a, [i, lg], d), wig(a, lg, (x, y - 30 * k), 22, 3.0), bob(a, i, 6 * k, 3.0)]
    if go:
        E.append(sh(a, [i, lg], go, 0, d + 0.3, 1.4))
    return E


def wave_rings(a, x, y, d=0.0, c="blue", n=3):
    """声波一圈圈往外扩（每圈一个 grow）。"""
    E = []
    for q in range(n):
        i = uid("rg")
        r = 60 + 50 * q
        E += [O(a, x, y, r, c=c, idp=i, sw=4), {"t": "move", "at": a, "kind": "grow", "targets": [i], "axis": "x", "pivot": [x, y], "dur": 0.5, "delay": d + 0.2 * q},
              pulse(a, i, d + 0.8 + 0.2 * q)]
    return E


def speaker_ring(a, x, y, d=0.0):
    """智能音箱：圆柱 + 顶上一圈 6 个麦克风点，点依次闪。"""
    i = uid("sp")
    E = [R(a, x - 110, y - 120, 220, 260, c="ink", fill="muted", idp=i, sw=5), E_(a, x, y - 120, 220, 60, c="ink", fill="paper", idp=i), pop(a, i, d), bob(a, i, 5, 0.9)]
    for q in range(6):
        j = uid("mp")
        import math
        px, py = x + 90 * math.cos(q * math.pi / 3), y - 120 + 22 * math.sin(q * math.pi / 3)
        E += [O(a, px, py, 10, c="red", fill="red", idp=j), pop(a, j, d + 0.3 + 0.1 * q), pulse(a, j, d + 1.0 + 0.1 * q)]
    return E


# ---------- 画板 ----------
# 0 闭眼、蚊子在耳边嗡嗡 / 往左拍
h0, hid = head(0, 1060, 470, 1.1)
bd(0, h0, mos(0, 520, 380, 0.6, 0.2), sound(0, 700, 420, 1.0, c="red", d=0.4), BIG(0, 1500, 300, "嗡~", c="red", d=0.6, s=110))
h0, hid = head(0.5, 1100, 470, 1.0)
hand = uid("hn")
bd(0.5, h0, mos(0.5, 500, 400, 0.55, 0.0, go=(-300, -250)),
   [R(0.5, 620, 350, 120, 160, c="ink", fill="gold", idp=hand, sw=5), pop(0.5, hand, 0.1), sh(0.5, hand, -150, 0, 0.5, 0.25), rot(0.5, hand, -25, (680, 510), 0.5, 0.25)],
   BIG(0.5, 1550, 330, "啪！", c="red", d=0.6, s=130), arr(0.5, 1450, 600, 1200, 600, c="red", d=0.3))
# 1 耳朵没长眼睛
h1, hid = head(1, 960, 470, 1.2, mood="o")
bd(1, h1, ic(1, "eye", 560, 300, 150, 0.2, mv="wig"), cross(1, 560, 300, d=0.5), ic(1, "eye", 1360, 300, 150, 0.3, mv="wig"), cross(1, 1360, 300, d=0.6))
h1, hid = head(1.5, 700, 480, 1.0)
bd(1.5, h1, ic(1.5, "question", 1300, 330, 200, 0.1, mv="wig", c="red"), wave_rings(1.5, 1300, 650, 0.3, c="blue"), T(1.5, 1300, 860, 56, "声音从哪来？", c="ink", d=0.5))
# 2 进博会 人工耳蜗首秀 / 卖点 找方向
bd(2, ic(2, "building", 520, 470, 260, 0.0, mv="bob"), BIG(2, 1300, 330, "进博会", c="blue", d=0.2, s=130), ic(2, "speaker", 1100, 600, 150, 0.4, mv="wig"),
   ic(2, "chip", 1500, 600, 150, 0.5, mv="spin"), arr(2, 720, 470, 940, 470, c="blue", d=0.3))
bd(2.5, ic(2.5, "map_pin", 960, 360, 220, 0.0, mv="bob", c="red"), wave_rings(2.5, 960, 470, 0.2, c="blue"), arr(2.5, 400, 700, 800, 520, c="red", d=0.4), arr(2.5, 1520, 700, 1120, 520, c="red", d=0.5),
   T(2.5, 960, 830, 64, "找出声音的方向", c="red", d=0.6))
# 3 INTEGRO / AI 处理声音
bd(3, BIG(3, 960, 330, "INTEGRO", c="blue", d=0.1, s=140), ic(3, "speaker", 520, 620, 160, 0.3, mv="wig"), ic(3, "chip", 960, 620, 160, 0.4, mv="spin"), ic(3, "gear", 1400, 620, 160, 0.5, mv="spin"))
bd(3.5, ic(3.5, "chip", 650, 470, 260, 0.0, mv="spin"), BIG(3.5, 1300, 380, "AI", c="red", d=0.2, s=150), sound(3.5, 850, 470, 1.0, c="blue", d=0.3), T(3.5, 1300, 600, 56, "据报道", c="muted", d=0.5),
   ic(3.5, "gear", 1600, 650, 120, 0.4, mv="spin"))
# 4 烧脑问题 / 两只耳朵 -> 一个方向
bd(4, ic(4, "question", 480, 470, 280, 0.0, mv="wig", c="red"), BIG(4, 1200, 400, "烧脑问题", c="red", d=0.2, s=130), ic(4, "flame", 1700, 420, 130, 0.4, mv="wig", c="red"),
   ic(4, "gear", 1200, 640, 140, 0.5, mv="spin"))
h4, hid = head(4.5, 560, 500, 0.9)
bd(4.5, h4, BIG(4.5, 1000, 400, "2", c="blue", d=0.1, s=150), arr(4.5, 1100, 470, 1350, 470, c="red", d=0.3), ic(4.5, "map_pin", 1500, 450, 200, 0.5, mv="bob", c="red"),
   T(4.5, 1500, 700, 56, "1 个方向", c="red", d=0.6))
# 5 两只耳朵 一左一右 / 隔着一颗头
h5, hid = head(5, 960, 480, 1.4)
bd(5, h5, T(5, 520, 480, 60, "左耳", c="red", d=0.3), T(5, 1400, 480, 60, "右耳", c="red", d=0.4), arr(5, 640, 480, 720, 480, c="red", d=0.3), arr(5, 1280, 480, 1200, 480, c="red", d=0.4))
h5, hid = head(5.5, 960, 480, 1.4)
bd(5.5, h5, arr(5.5, 760, 260, 1160, 260, c="blue", d=0.2), arr(5.5, 1160, 260, 760, 260, c="blue", d=0.4), T(5.5, 960, 200, 56, "隔着一颗头", c="blue", d=0.5))
# 6 声音先到左耳 / 绕到右耳
h6, hid = head(6, 1060, 480, 1.1)
bd(6, h6, mos(6, 380, 420, 0.5, 0.0), sound(6, 520, 450, 1.0, c="red", d=0.2), dot(6, 560, 480, 870, 480, c="red", d=0.4, dur=0.6), BIG(6, 1550, 300, "先到", c="red", d=0.6, s=100))
h6, hid = head(6.5, 1000, 480, 1.1)
arc = uid("ac")
bd(6.5, h6, mos(6.5, 340, 420, 0.45, 0.0), [P(6.5, "M820,480 Q1000,230 1180,480", c="red", w=6, idp=arc), {"t": "move", "at": 6.5, "kind": "grow", "targets": [arc], "axis": "x", "pivot": [820, 480], "dur": 0.8, "delay": 0.2}],
   dot(6.5, 820, 360, 1180, 470, c="red", d=0.4, dur=0.9), BIG(6.5, 1550, 300, "再到", c="blue", d=0.8, s=100))
# 7 340 米每秒 / 约 20 厘米
bd(7, BIG(7, 1150, 380, "340 米/秒", c="red", d=0.1, s=130), sound(7, 400, 470, 1.2, c="blue", d=0.2), dot(7, 450, 650, 1600, 650, c="blue", d=0.3, dur=0.6),
   ic(7, "rocket", 1650, 520, 140, 0.4, mv="bob"))
h7, hid = head(7.5, 700, 500, 1.1)
bd(7.5, h7, ic(7.5, "ruler", 1350, 380, 220, 0.1, mv="wig"), BIG(7.5, 1350, 620, "≈ 20 厘米", c="blue", d=0.4, s=110), T(7.5, 1350, 760, 48, "估算", c="muted", d=0.6))
# 8 算一下 / 0.6 毫秒
bd(8, T(8, 960, 330, 80, "0.2 米 ÷ 340 米/秒", c="ink", d=0.1), ic(8, "clock", 500, 600, 180, 0.3, mv="spin"), arr(8, 700, 600, 1300, 600, c="red", d=0.4), ic(8, "gear", 1450, 600, 150, 0.5, mv="spin"))
bd(8.5, BIG(8.5, 960, 420, "0.6 毫秒", c="red", d=0.0, s=160), ic(8.5, "clock", 420, 450, 200, 0.2, mv="spin"), star(8.5, 1500, 250, 0.4, r=40), star(8.5, 1600, 650, 0.6, r=34))
# 9 眨眼一百多毫秒 / 短几百倍
bd(9, ic(9, "eye", 520, 450, 260, 0.0, mv="wig"), BIG(9, 1250, 400, "100+ 毫秒", c="blue", d=0.2, s=120), bar(9, 1500, 800, 120, 300, "blue", 0.4))
bd(9.5, bar(9.5, 600, 800, 160, 480, "blue", 0.0), bar(9.5, 1150, 800, 160, 6, "red", 0.4), T(9.5, 680, 260, 52, "眨眼", c="blue", d=0.2), T(9.5, 1230, 740, 52, "耳朵差", c="red", d=0.5),
   BIG(9.5, 1550, 400, "几百倍", c="red", d=0.7, s=100))
# 10 大脑最灵 / 十微秒
br = uid("br")
bd(10, [E_(10, 700, 470, 420, 300, c="ink", fill="red", idp=br), P(10, "M560,430 Q620,380 680,440 Q740,500 800,430 M560,520 Q640,470 720,530 Q780,570 840,520", c="ink", w=5, idp=br),
        pop(10, br, 0.0), pulse(10, br, 0.6), wig(10, br, (700, 620), 3, 1.5)], ic(10, "magnifier", 1300, 470, 220, 0.3, mv="wig"), sound(10, 950, 470, 1.0, c="blue", d=0.2))
bd(10.5, BIG(10.5, 960, 420, "10 微秒", c="red", d=0.0, s=170), ic(10.5, "clock", 400, 450, 180, 0.2, mv="spin"), ic(10.5, "flame", 1550, 450, 160, 0.4, mv="wig", c="red"), check(10.5, 960, 650, d=0.6))
# 11 两个人 / 从两头往中间送信
bd(11, runner(11, 500, 650, 0.8, 0.0), runner(11, 1420, 650, 0.8, 0.2, c="red", go=0), P(11, "M300,760 L1620,760", c="ink", w=5), T(11, 960, 300, 64, "两个送信的人", c="ink", d=0.4))
bd(11.5, runner(11.5, 400, 650, 0.8, 0.0, go=400), runner(11.5, 1520, 650, 0.8, 0.0, c="red", go=-400), P(11.5, "M300,760 L1620,760", c="ink", w=5), arr(11.5, 760, 300, 940, 300, c="blue", d=0.3),
   arr(11.5, 1160, 300, 980, 300, c="red", d=0.3))
# 12 左边先出发 偏右碰头 / 在哪碰头 = 方向
bd(12, runner(12, 300, 650, 0.8, 0.0, go=860), runner(12, 1620, 650, 0.8, 0.8, c="red", go=-400), P(12, "M200,760 L1720,760", c="ink", w=5), T(12, 400, 300, 56, "左耳先出发", c="blue", d=0.1),
   ic(12, "map_pin", 1180, 380, 140, 1.2, mv="bob", c="red"))
bd(12.5, P(12.5, "M200,700 L1720,700", c="ink", w=5), ic(12.5, "map_pin", 1180, 560, 160, 0.0, mv="bob", c="red"), T(12.5, 960, 300, 64, "在哪碰头 = 方向", c="red", d=0.3),
   mos(12.5, 360, 520, 0.45, 0.2), arr(12.5, 1180, 760, 1180, 900, c="red", d=0.5), T(12.5, 1440, 860, 48, "偏右 → 声音在左", c="blue", d=0.6))
# 13 延迟线模型 / 猫头鹰
lines_ = []
for q in range(5):
    lines_ += dot(13, 600, 400 + 70 * q, 1320, 400 + 70 * q, c="blue" if q % 2 else "red", d=0.1 * q, dur=1.0, r=12)
bd(13, lines_, P(13, "M600,380 L1320,380 M600,690 L1320,690", c="ink", w=4), BIG(13, 960, 250, "延迟线", c="blue", d=0.2, s=110))
ow = uid("ow")
bd(13.5, [O(13.5, 800, 500, 180, c="ink", fill="gold", idp=ow), O(13.5, 730, 460, 50, c="ink", fill="paper", idp=ow), O(13.5, 870, 460, 50, c="ink", fill="paper", idp=ow),
          O(13.5, 730, 460, 20, c="ink", fill="ink", idp=ow), O(13.5, 870, 460, 20, c="ink", fill="ink", idp=ow), P(13.5, "M780,530 L800,570 L820,530 Z", c="ink", w=4, idp=ow),
          P(13.5, "M660,350 L690,280 L730,340 M940,340 L910,280 L870,350", c="ink", w=5, idp=ow), pop(13.5, ow, 0.0), bob(13.5, ow, 8, 1.0), rot(13.5, ow, 20, (800, 500), 0.6, 0.4)],
   T(13.5, 1400, 400, 64, "猫头鹰", c="blue", d=0.3), check(13.5, 1400, 560, d=0.5), sound(13.5, 1050, 500, 0.8, c="red", d=0.4))
# 14 反转一 / 高音犯迷糊
bd(14, BIG(14, 960, 380, "反转一", c="red", d=0.0, s=150), ic(14, "flame", 500, 450, 160, 0.2, mv="wig", c="red"), ic(14, "flame", 1420, 450, 160, 0.3, mv="wig", c="red"),
   arr(14, 700, 650, 1220, 650, c="red", d=0.4))
h14, hid = head(14.5, 600, 500, 1.0, mood="o")
hw = uid("hw")
bd(14.5, h14, [P(14.5, "M1000,450 " + " ".join(f"Q{1020 + 40 * q},{400 if q % 2 == 0 else 500} {1040 + 40 * q},450" for q in range(14)), c="red", w=5, idp=hw),
               pop(14.5, hw, 0.0), wig(14.5, hw, (1300, 450), 3, 3.0)], T(14.5, 1300, 300, 60, "高音", c="red", d=0.2), ic(14.5, "question", 1300, 680, 150, 0.5, mv="wig", c="red"))
# 15 波很短 脑袋像墙 / 声音的影子
bd(15, P(15, "M200,450 " + " ".join(f"Q{220 + 40 * q},{400 if q % 2 == 0 else 500} {240 + 40 * q},450" for q in range(14)), c="red", w=5),
   head(15, 1250, 480, 1.0)[0], arr(15, 300, 650, 950, 650, c="red", d=0.2), T(15, 600, 300, 56, "波很短", c="red", d=0.3), ic(15, "building", 1650, 480, 140, 0.5, mv="bob"))
shd = uid("sd")
bd(15.5, head(15.5, 800, 480, 1.0)[0], sound(15.5, 400, 480, 1.4, c="red", d=0.0),
   [R(15.5, 1000, 330, 600, 300, c="muted", fill="muted", idp=shd, sw=2), {"t": "move", "at": 15.5, "kind": "grow", "targets": [shd], "axis": "x", "pivot": [1000, 480], "dur": 0.8, "delay": 0.3}],
   T(15.5, 1300, 260, 60, "声音的影子", c="ink", d=0.5), mos(15.5, 250, 300, 0.4, 0.1))
# 16 远的耳朵 / 声音更小
h16, hid = head(16, 960, 480, 1.2)
bd(16, h16, sound(16, 640, 480, 1.3, c="red", d=0.0, dirn=-1), T(16, 420, 700, 56, "近：大声", c="red", d=0.3), T(16, 1500, 700, 56, "远：小声", c="blue", d=0.5), sound(16, 1280, 480, 0.5, c="blue", d=0.4))
bd(16.5, bar(16.5, 650, 800, 180, 420, "red", 0.0), bar(16.5, 1100, 800, 180, 180, "blue", 0.3), T(16.5, 740, 300, 56, "左耳", c="red", d=0.1), T(16.5, 1190, 560, 56, "右耳", c="blue", d=0.4),
   BIG(16.5, 1550, 450, "音量差", c="red", d=0.6, s=90))
# 17 低音时间差 高音音量差 / 两样一起用
bd(17, P(17, "M220,380 Q320,280 420,380 Q520,480 620,380 Q720,280 820,380", c="blue", w=6), ic(17, "clock", 1100, 380, 160, 0.2, mv="spin"), T(17, 1500, 380, 60, "低音 → 时间差", c="blue", d=0.3),
   P(17, "M220,650 " + " ".join(f"Q{235 + 30 * q},{610 if q % 2 == 0 else 690} {250 + 30 * q},650" for q in range(20)), c="red", w=5), ic(17, "speaker", 1100, 650, 160, 0.5, mv="wig"),
   T(17, 1500, 650, 60, "高音 → 音量差", c="red", d=0.6))
br2 = uid("br")
bd(17.5, [E_(17.5, 960, 470, 440, 300, c="ink", fill="red", idp=br2), pop(17.5, br2, 0.0), pulse(17.5, br2, 0.5), wig(17.5, br2, (960, 620), 3, 1.5)],
   ic(17.5, "clock", 450, 470, 170, 0.2, mv="spin"), ic(17.5, "speaker", 1470, 470, 170, 0.3, mv="wig"), arr(17.5, 560, 470, 720, 470, c="blue", d=0.4), arr(17.5, 1360, 470, 1200, 470, c="red", d=0.5))
# 18 反转二 / 前后时间差一样
bd(18, BIG(18, 960, 380, "反转二", c="red", d=0.0, s=150), T(18, 960, 560, 64, "最反直觉", c="blue", d=0.3), ic(18, "flame", 480, 450, 150, 0.2, mv="wig", c="red"), ic(18, "question", 1440, 450, 150, 0.4, mv="wig", c="red"))
h18, hid = head(18.5, 960, 480, 1.0)
bd(18.5, h18, mos(18.5, 960, 220, 0.4, 0.1), mos(18.5, 960, 830, 0.4, 0.3), T(18.5, 1450, 250, 56, "前", c="red", d=0.2), T(18.5, 1450, 800, 56, "后", c="red", d=0.4), BIG(18.5, 1550, 520, "一样！", c="red", d=0.6, s=100))
# 19 前后到两耳一样远
h19, hid = head(19, 960, 520, 1.0)
bd(19, h19, mos(19, 960, 200, 0.35, 0.0), arr(19, 940, 250, 830, 470, c="blue", d=0.2), arr(19, 980, 250, 1090, 470, c="blue", d=0.2), T(19, 1450, 300, 56, "左 = 右", c="blue", d=0.5))
h19, hid = head(19.5, 960, 420, 1.0)
bd(19.5, h19, mos(19.5, 960, 780, 0.35, 0.0), arr(19.5, 940, 730, 830, 480, c="red", d=0.2), arr(19.5, 980, 730, 1090, 480, c="red", d=0.2), T(19.5, 1450, 700, 56, "左 = 右", c="red", d=0.5),
   ic(19.5, "question", 400, 450, 160, 0.6, mv="wig", c="red"))
# 20 耳廓 / 弯弯绕绕
ear = uid("ea")
bd(20, [P(20, "M860,250 Q1150,230 1130,520 Q1110,760 900,780 Q850,700 920,650 Q1030,560 980,420 Q930,330 860,250 M930,330 Q1040,380 1020,520", c="ink", w=8, idp=ear),
        pop(20, ear, 0.0), wig(20, ear, (900, 780), 4, 1.4), pulse(20, ear, 0.8)], T(20, 1500, 400, 70, "耳廓", c="red", d=0.3), arr(20, 1380, 420, 1150, 420, c="red", d=0.4))
squig = uid("sq")
bd(20.5, [P(20.5, "M500,450 Q560,350 620,450 Q680,550 740,450 Q800,350 860,450 Q920,550 980,450 Q1040,350 1100,450 Q1160,550 1220,450 Q1280,350 1340,450", c="blue", w=7, idp=squig),
          pop(20.5, squig, 0.0), wig(20.5, squig, (920, 450), 4, 2.0)], T(20.5, 920, 680, 70, "弯弯绕绕", c="blue", d=0.3), ic(20.5, "magnifier", 1600, 450, 180, 0.4, mv="wig"))
# 21 不同方向进来 弹一弹 / 音色变了
bd(21, [P(21, "M860,250 Q1150,230 1130,520 Q1110,760 900,780 Q850,700 920,650 Q1030,560 980,420 Q930,330 860,250", c="ink", w=7)],
   dot(21, 400, 300, 980, 420, c="red", d=0.0, dur=0.6), dot(21, 400, 700, 980, 600, c="blue", d=0.3, dur=0.6), dot(21, 1600, 300, 1080, 450, c="gold", d=0.6, dur=0.6), sound(21, 1150, 520, 0.8, c="red", d=0.9))
bd(21.5, ic(21.5, "sine", 520, 450, 220, 0.0, mv="wig"), arr(21.5, 720, 450, 1100, 450, c="red", d=0.2),
   P(21.5, "M1200,450 Q1230,350 1260,450 Q1300,560 1330,450 Q1350,400 1380,450 Q1420,520 1460,450 Q1480,380 1520,450", c="red", w=6, idp="tone21"), pop(21.5, "tone21", 0.5), wig(21.5, "tone21", (1360, 450), 4, 2.5),
   T(21.5, 960, 700, 64, "音色变了", c="red", d=0.6))
# 22 大脑从小记住 / 这种音色 = 后面
bd(22, [E_(22, 700, 470, 420, 300, c="ink", fill="red", idp="br22"), pop(22, "br22", 0.0), wig(22, "br22", (700, 620), 3, 1.5)], ic(22, "clock", 1300, 380, 150, 0.2, mv="spin"),
   T(22, 1300, 600, 60, "从小记住", c="blue", d=0.4), check(22, 1600, 600, d=0.6))
bd(22.5, P(22.5, "M300,450 Q330,350 360,450 Q400,560 430,450 Q450,400 480,450 Q520,520 560,450", c="red", w=6), arr(22.5, 650, 450, 1000, 450, c="red", d=0.2),
   head(22.5, 1350, 450, 0.9)[0], mos(22.5, 1350, 820, 0.35, 0.4), T(22.5, 1700, 800, 56, "后面！", c="red", d=0.6))
# 23 拿不准 / 歪一下头
h23, hid = head(23, 960, 480, 1.1, mood="o")
bd(23, h23, ic(23, "question", 1450, 330, 180, 0.2, mv="wig", c="red"), ic(23, "question", 470, 330, 140, 0.4, mv="wig", c="red"), mos(23, 960, 820, 0.3, 0.3))
h23, hid = head(23.5, 960, 480, 1.2)
bd(23.5, h23, [rot(23.5, hid, 20, (960, 620), 0.2, 0.4), rot(23.5, hid, -20, (960, 620), 0.8, 0.4)], T(23.5, 1500, 300, 64, "歪头", c="blue", d=0.3), arr(23.5, 1400, 400, 1250, 450, c="blue", d=0.4))
# 24 时间差变了 / 答案出来
h24, hid = head(24, 760, 480, 1.0)
bd(24, h24, [rot(24, hid, 22, (760, 620), 0.0, 0.4)], dot(24, 1500, 400, 900, 400, c="red", d=0.3, dur=0.6), dot(24, 1500, 560, 640, 560, c="blue", d=0.5, dur=0.9),
   T(24, 1500, 260, 56, "时间差变了", c="red", d=0.4))
h24, hid = head(24.5, 760, 480, 1.0, eyes="open")
bd(24.5, h24, check(24.5, 1300, 420, d=0.1), BIG(24.5, 1400, 650, "后面！", c="red", d=0.3, s=110), mos(24.5, 1650, 330, 0.35, 0.4))
# 25 设备 好几个麦克风 / 再算一遍
bd(25, mic(25, 500, 450, 0.0), mic(25, 800, 450, 0.2), mic(25, 1100, 450, 0.4), ic(25, "chip", 1500, 450, 180, 0.5, mv="spin"), arr(25, 1200, 450, 1380, 450, c="blue", d=0.6))
bd(25.5, ic(25.5, "chip", 600, 450, 240, 0.0, mv="spin"), T(25.5, 1200, 380, 70, "比时间 · 比音量", c="blue", d=0.2), ic(25.5, "gear", 1050, 620, 140, 0.4, mv="spin"), ic(25.5, "gear", 1350, 620, 120, 0.5, mv="spin"))
# 26 机器人也一样 / 扫地机 机器狗 音箱
bd(26, cute_bot(960, 800, 1.2, 26, idp="bot26"), [pop(26, "bot26*", 0.0)], sound(26, 1150, 400, 1.0, c="blue", d=0.3, dirn=1), sound(26, 770, 400, 1.0, c="blue", d=0.4, dirn=-1),
   BIG(26, 1500, 650, "机器人", c="red", d=0.5, s=100))
vac, dog = uid("vc"), uid("dg")
bd(26.5, [E_(26.5, 420, 600, 300, 120, c="ink", fill="muted", idp=vac), O(26.5, 420, 560, 20, c="red", fill="red", idp=vac), pop(26.5, vac, 0.0), sh(26.5, vac, 120, 0, 0.3, 1.0)],
   [R(26.5, 800, 420, 260, 120, c="ink", fill="gold", idp=dog), R(26.5, 1040, 360, 100, 80, c="ink", fill="gold", idp=dog),
    P(26.5, "M830,540 L810,650 M890,540 L900,650 M980,540 L960,650 M1040,540 L1060,650", c="ink", w=8, idp="dgl"), pop(26.5, [dog, "dgl"], 0.2), bob(26.5, dog, 6, 2), wig(26.5, "dgl", (930, 540), 15, 3)],
   speaker_ring(26.5, 1500, 560, 0.4))
# 27 一圈麦克风 / 比谁先听到
bd(27, speaker_ring(27, 760, 520, 0.0), T(27, 1400, 400, 60, "一圈麦克风", c="blue", d=0.3), sound(27, 1100, 420, 1.0, c="red", d=0.5))
bd(27.5, speaker_ring(27.5, 960, 560, 0.0), mos(27.5, 300, 380, 0.4, 0.0), dot(27.5, 400, 420, 860, 440, c="red", d=0.3, dur=0.5), BIG(27.5, 1500, 380, "第一！", c="red", d=0.7, s=100))
# 28 隔得越远 / 越准
bd(28, mic(28, 600, 450, 0.0), mic(28, 1300, 450, 0.1), arr(28, 680, 600, 1220, 600, c="blue", d=0.3), arr(28, 1220, 600, 680, 600, c="blue", d=0.4), T(28, 960, 260, 64, "隔得越远", c="blue", d=0.3))
bd(28.5, ic(28.5, "map_pin", 960, 420, 240, 0.0, mv="bob", c="red"), BIG(28.5, 960, 720, "越准", c="red", d=0.3, s=130), check(28.5, 1450, 450, d=0.5), wave_rings(28.5, 960, 470, 0.2, c="blue"))
# 29 友情提示 / 听得出方向 ≠ 听得清
bd(29, BIG(29, 960, 380, "友情提示", c="blue", d=0.0, s=130), ic(29, "map_pin", 600, 650, 150, 0.2, mv="bob", c="red"), check(29, 1300, 650, d=0.4))
h29, hid = head(29.5, 600, 480, 1.0, mood="o")
bd(29.5, h29, BIG(29.5, 1300, 380, "方向 ≠ 清楚", c="red", d=0.2, s=100), sound(29.5, 1050, 600, 0.8, c="muted", d=0.4), ic(29.5, "question", 1550, 650, 140, 0.5, mv="wig", c="red"))
# 30 效果 / 看真实数据
bd(30, ic(30, "speaker", 600, 450, 200, 0.0, mv="wig"), ic(30, "chip", 1000, 450, 180, 0.2, mv="spin"), ic(30, "question", 1400, 450, 180, 0.4, mv="wig", c="red"))
bd(30.5, bar(30.5, 600, 800, 140, 200, "blue", 0.0), bar(30.5, 800, 800, 140, 320, "blue", 0.2), bar(30.5, 1000, 800, 140, 260, "blue", 0.4), ic(30.5, "magnifier", 1450, 500, 200, 0.5, mv="wig"),
   T(30.5, 960, 260, 64, "真实使用数据", c="ink", d=0.3))
# 31 回到问题 / 四招
h31, hid = head(31, 960, 480, 1.1)
bd(31, h31, ic(31, "question", 1500, 350, 180, 0.1, mv="wig", c="red"), mos(31, 380, 380, 0.4, 0.2))
bd(31.5, ic(31.5, "clock", 400, 420, 170, 0.0, mv="spin"), ic(31.5, "speaker", 780, 420, 170, 0.2, mv="wig"), ic(31.5, "sine", 1160, 420, 170, 0.4, mv="wig"),
   head(31.5, 1540, 450, 0.55)[0],
   T(31.5, 400, 650, 52, "比时间", c="blue", d=0.1), T(31.5, 780, 650, 52, "比音量", c="red", d=0.3), T(31.5, 1160, 650, 52, "听音色", c="blue", d=0.5), T(31.5, 1540, 650, 52, "歪个头", c="red", d=0.7))
# 32 微秒级算法 / 在你头上跑
bd(32, BIG(32, 960, 380, "微秒级", c="red", d=0.0, s=150), ic(32, "gear", 500, 450, 180, 0.2, mv="spin"), ic(32, "gear", 1420, 450, 180, 0.3, mv="spin"), ic(32, "clock", 960, 650, 140, 0.4, mv="spin"))
h32, hid = head(32.5, 960, 520, 1.1)
bd(32.5, h32, ic(32.5, "gear", 960, 250, 140, 0.1, mv="spin"), ic(32.5, "gear", 1090, 230, 100, 0.2, mv="spin"), T(32.5, 1550, 450, 60, "天天在跑", c="blue", d=0.4))
# 33 算出在左边 / 拍不着
h33, hid = head(33, 1100, 480, 1.0)
bd(33, h33, mos(33, 520, 380, 0.5, 0.0), arr(33, 900, 300, 680, 300, c="red", d=0.2), check(33, 520, 650, d=0.4), T(33, 1550, 300, 56, "在左边！", c="red", d=0.3))
hand2 = uid("hn")
bd(33.5, head(33.5, 1100, 480, 1.0, mood="sad")[0], mos(33.5, 520, 380, 0.5, 0.0, go=(-200, -300)),
   [R(33.5, 700, 330, 120, 160, c="ink", fill="gold", idp=hand2, sw=5), pop(33.5, hand2, 0.1), sh(33.5, hand2, -180, 0, 0.6, 0.25)], cross(33.5, 500, 650, d=0.9), T(33.5, 1550, 300, 56, "拍空", c="blue", d=0.8))
# 34 早飞了 / 右边叮一口
bd(34, mos(34, 960, 400, 0.6, 0.0, go=(500, -100)), BIG(34, 600, 650, "早飞了", c="blue", d=0.3, s=110), arr(34, 1100, 300, 1500, 220, c="blue", d=0.4))
h34, hid = head(34.5, 860, 480, 1.0, mood="sad")
bump = uid("bp")
bd(34.5, h34, mos(34.5, 1250, 350, 0.45, 0.0), [O(34.5, 1030, 430, 30, c="red", fill="red", idp=bump), pop(34.5, bump, 0.4), pulse(34.5, bump, 0.8)],
   BIG(34.5, 1550, 650, "叮！", c="red", d=0.5, s=130))

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh", say={"INTEGRO": "因特格罗", "340": "三百四十", "0.6": "零点六"})
