"""每日科普 2026-10-19（中文）：《为什么吃得“差”反而更胖？》
热点：微博热搜 2026-10-19 第 11 位“原来吃得差才会胖”（热度约 3314.9 万，remoshuang.com/weibo 实时榜转录）；
新浪微博话题页 sina.cn/weibo/detail/5355758217855310.html（“牛肉鸡蛋不是元凶，蛋糕奶茶才是”）。
科学依据：Hall et al., Cell Metabolism 2019（美国国立卫生研究院 NIH，nih.gov/news-events/nih-research-matters/eating-highly-processed-foods-linked-weight-gain）：
20 名健康成人住院 28 天，超加工 / 少加工饮食各两周；端上的热量、糖、纤维、脂肪、碳水相同，随便吃；超加工期每天多吃约 500 大卡，
两周平均胖约 0.9 公斤（2 磅），少加工期瘦了差不多同样多；超加工期吃得更快；两种饭被评为同样好吃；
少加工期饱腹激素 PYY 升高、饥饿激素 ghrelin 下降（论文报告）。
估算 / 推测（片中照此说）：“差不多两碗米饭”（一碗约 230 大卡，估算）；“蛋糕和青菜热量可能差十倍”（每百克约 350 对 30 大卡，估算）；
“液体热量大脑容易漏算”说成“不少研究认为”。比喻：饱了的信号 = 外卖小哥送纸条。角色：小胃（贯穿：“我不是不饱，我只是消息慢”）。无手。
    python3 make.py <kokoro 模型目录> | --fake | --boards-only   然后  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("同样一桌饭，同样的热量，|有人一天多吃了五百大卡。", "Same meals, same calories on the plate, | and people ate 500 extra calories a day."),
 ("今天的微博热搜：原来吃得差才会胖。|热度三千三百万。", "Today on Weibo's hot list: 'eating badly is what makes you fat.' | 33 million in heat."),
 ("说法是：牛肉鸡蛋不是元凶，|蛋糕奶茶才是。", "The claim: beef and eggs aren't the culprits. | Cake and milk tea are."),
 ("今天的问题：一样多的热量，|为什么吃得“差”就会胖？", "Today's question: with the same calories, | why does eating 'badly' make you fatter?"),
 ("先认识小胃。|它每天只问一句话：吃饱了吗？", "Meet Tummy. | It asks one thing all day: am I full yet?"),
 ("二零一九年，美国国立卫生研究院做了一个实验。|二十个人，住进医院，整整四个星期。", "In 2019, the US National Institutes of Health ran an experiment. | Twenty people lived in a hospital for four weeks."),
 ("两周吃超加工食品，|两周吃少加工的天然食物。", "Two weeks of ultra-processed food, | two weeks of minimally processed food."),
 ("关键是：两种饭端上来的热量、糖、脂肪、纤维，|全都一样。", "The key: both diets served the same calories, sugar, fat and fiber. | Exactly matched."),
 ("想吃多少吃多少，没人逼。", "Eat as much as you like. Nobody's forcing anyone."),
 ("结果：超加工那两周，每人每天多吃了大约五百大卡。|差不多两碗米饭。", "Result: on ultra-processed food, people ate about 500 calories more per day. | Roughly two bowls of rice."),
 ("两周下来，平均胖了将近一公斤。|换成天然食物，又瘦了差不多那么多。", "In two weeks they gained almost a kilo on average. | On the natural diet, they lost about the same."),
 ("反转一：大家给两种饭打分，一样好吃。|不是因为更香，才多吃。", "Twist one: people rated both diets equally tasty. | It wasn't about flavor."),
 ("那多出来的五百大卡，|到底是从哪来的？", "So where did those extra 500 calories | come from?"),
 ("线索一：吃得更快。|超加工食品又软又好嚼，几口就下去了。", "Clue one: people ate faster. | Soft, easy-to-chew food goes down in a few bites."),
 ("而“吃饱了”的信号，从肠子传到大脑，|要花上一段时间。", "And the 'I'm full' signal takes time | to travel from the gut to the brain."),
 ("就像外卖小哥送一张“够了”的纸条。|你吃得太快，纸条还没到，饭已经光了。", "It's like a courier delivering a note that says 'enough.' | Eat too fast, and the plate is empty before the note arrives."),
 ("线索二：热量密度。|同样一口，超加工食品塞进去的热量更多。", "Clue two: energy density. | Each bite of processed food packs in more calories."),
 ("一块蛋糕和一盘青菜，个头差不多，|热量估计能差十倍。", "A slice of cake and a plate of greens look about the same size, | but the calories can differ roughly tenfold."),
 ("而胃觉得饱，很大一部分是靠被撑开。|它不太会数热量。", "And a stomach feels full largely by being stretched. | It's bad at counting calories."),
 ("反转二：吃天然食物的那两周，|让人饱的激素升高了，让人饿的激素降了。", "Twist two: on the natural diet, | a fullness hormone went up and a hunger hormone went down."),
 ("也就是说，吃天然食物，|身体自己会踩刹车。", "In other words, on real food, | the body hits its own brakes."),
 ("反转三：“吃得差”说的不是吃得少，也不是穷，|而是食物被加工得太“省事”了。", "Twist three: 'eating badly' isn't about eating little, or being poor. | It's food processed to be too effortless."),
 ("工厂把嚼、剥、消化的活儿，|提前帮你干完了。", "The factory has already done the chewing, peeling and breaking down | for you."),
 ("对你的牙是省事了，|对你的腰可就不省事了。", "Easy on your teeth. | Not so easy on your waistline."),
 ("奶茶为什么喝了不觉得饱？|不少研究认为，喝下去的热量，大脑最容易漏算。", "Why doesn't milk tea fill you up? | Many studies suggest the brain undercounts calories you drink."),
 ("那牛肉鸡蛋呢？蛋白质让人饱得更久，|同样的热量，更难吃过头。", "And beef and eggs? Protein keeps you full longer, | so the same calories are harder to overeat."),
 ("所以热搜那句话，大方向是对的：|胖不胖，不只看吃多少，还看吃的是什么。", "So the hot take is roughly right: | it's not only how much you eat, but what kind."),
 ("但别把它理解成“蛋糕有毒”。|热量还是热量。", "But it doesn't mean cake is poison. | A calorie is still a calorie."),
 ("只不过超加工食品，|让人特别容易多吃。", "Ultra-processed food just makes it | really easy to eat more."),
 ("友情提示：这只是一项二十个人、四周的小实验，|结论还要更多研究，每个人也不一样。", "Friendly fine print: this was a small study, 20 people, four weeks. | More research is needed, and everyone's different."),
 ("身体有问题，听医生的，|别听热搜的，也别听一块白板的。", "For health questions, listen to your doctor, | not a hot list, and not a whiteboard."),
 ("最后送一个小建议：吃慢一点，|让“够了”的纸条，追上你的筷子。", "One last tip: eat a little slower, | so the 'enough' note can catch up with your chopsticks."),
 ("小胃说：我不是不饱，|我只是消息慢。", "Tummy says: I'm not never full. | My messages are just slow."),
]
TITLE = {"zh": "为什么吃得“差”反而更胖？", "en": "Why does eating 'badly' make you fatter?"}


def tummy(a, x, y, k=1.0, mood="happy", sweat=False):
    """小胃：一只 J 形的胃，圆眼睛、会笑，左右晃，头上的食道管一直抖。"""
    i, tube = uid("wei"), uid("tube")
    d = (f"M{x - 40 * k},{y - 150 * k} Q{x - 60 * k},{y - 40 * k} {x - 130 * k},{y + 10 * k} Q{x - 190 * k},{y + 140 * k} {x - 40 * k},{y + 150 * k} "
         f"Q{x + 150 * k},{y + 150 * k} {x + 170 * k},{y - 10 * k} Q{x + 180 * k},{y - 140 * k} {x + 60 * k},{y - 120 * k} "
         f"Q{x + 20 * k},{y - 110 * k} {x + 20 * k},{y - 150 * k}")
    E = [P(a, d, c="red", w=6, idp=i, fill="red"),
         O(a, x - 40 * k, y + 10 * k, 16 * k, c="ink", fill="ink", idp=i), O(a, x + 50 * k, y + 10 * k, 16 * k, c="ink", fill="ink", idp=i),
         P(a, f"M{x - 30 * k},{y + 60 * k} Q{x + 5 * k},{y + (95 if mood == 'happy' else 40) * k} {x + 40 * k},{y + 60 * k}", c="ink", w=5, idp=i),
         P(a, f"M{x - 10 * k},{y - 150 * k} Q{x - 20 * k},{y - 230 * k} {x + 10 * k},{y - 300 * k}", c="red", w=7, idp=tube),
         bob(a, i, 8 * k, 1.2), bob(a, tube, 8 * k, 1.2), wig(a, tube, (x, y - 150 * k), 6, 1.8), wig(a, i, (x, y + 150 * k), 3, 0.9)]
    if sweat:
        s = uid("sw")
        E += [O(a, x + 150 * k, y - 120 * k, 14 * k, c="blue", fill="blue", idp=s), sh(a, s, 0, 60 * k, 0.3, 1.2)]
    return E, i


def person(a, x, y, k=1.0, c="ink", d=None, hz=1.2):
    i = uid("pp")
    E = [O(a, x, y - 70 * k, 18 * k, c=c, fill=c, idp=i),
         P(a, f"M{x},{y - 52 * k} L{x},{y - 18 * k} M{x - 20 * k},{y} L{x},{y - 18 * k} L{x + 20 * k},{y} M{x - 22 * k},{y - 42 * k} L{x + 22 * k},{y - 42 * k}",
           c=c, w=4, idp=i), bob(a, i, 4 * k, hz)]
    if d is not None:
        E.append(pop(a, i, d))
    return E


def crowd(a, x, y, cols, rows, gap=60, k=0.8, d=0.2, step=0.06, c="ink"):
    E, n = [], 0
    for r in range(rows):
        for q in range(cols):
            E += person(a, x + q * gap + (r % 2) * gap / 2, y + r * gap * 1.1, k, c=c, d=d + step * n, hz=0.9 + 0.1 * (n % 5))
            n += 1
    return E


def cake(a, x, y, k=1.0, d=0.0):
    i, fl = uid("cake"), uid("fl")
    E = [R(a, x - 110 * k, y - 60 * k, 220 * k, 120 * k, c="gold", fill="gold", idp=i), R(a, x - 110 * k, y - 80 * k, 220 * k, 30 * k, c="red", fill="red", idp=i),
         P(a, f"M{x},{y - 80 * k} L{x},{y - 130 * k}", c="ink", w=4, idp=i), O(a, x, y - 145 * k, 12 * k, c="red", fill="gold", idp=fl),
         pop(a, i, d), wig(a, fl, (x, y - 130 * k), 10, 3.0), bob(a, i, 4, 1.0)]
    return E


def tea(a, x, y, k=1.0, d=0.0):
    i, st = uid("tea"), uid("straw")
    E = [P(a, f"M{x - 70 * k},{y - 120 * k} L{x - 50 * k},{y + 120 * k} L{x + 50 * k},{y + 120 * k} L{x + 70 * k},{y - 120 * k} Z", c="ink", w=5, fill="gold", idp=i),
         P(a, f"M{x + 10 * k},{y - 120 * k} L{x + 40 * k},{y - 220 * k}", c="red", w=7, idp=st), pop(a, i, d), pop(a, st, d + 0.2), wig(a, st, (x + 10 * k, y - 120 * k), 8, 1.6)]
    for q in range(3):
        b = uid("pearl")
        E += [O(a, x - 25 * k + 25 * k * q, y + 90 * k, 12 * k, c="ink", fill="ink", idp=b), bob(a, b, 6, 1.4 + 0.3 * q)]
    return E


def egg(a, x, y, k=1.0, d=0.0):
    i = uid("egg")
    return [{"t": "ellipse", "at": a, "id": i, "x": x - 60 * k, "y": y - 80 * k, "w": 120 * k, "h": 160 * k, "c": "ink"}, pop(a, i, d), rot(a, i, 12, (x, y + 80 * k), d + 0.4, 0.5), bob(a, i, 5, 1.1)]


def steak(a, x, y, k=1.0, d=0.0):
    i = uid("stk")
    return [P(a, f"M{x - 120 * k},{y} Q{x - 100 * k},{y - 90 * k} {x + 20 * k},{y - 70 * k} Q{x + 140 * k},{y - 60 * k} {x + 120 * k},{y + 30 * k} "
                 f"Q{x + 80 * k},{y + 90 * k} {x - 40 * k},{y + 70 * k} Q{x - 130 * k},{y + 60 * k} {x - 120 * k},{y} Z", c="red", w=5, fill="red", idp=i),
            pop(a, i, d), wig(a, i, (x, y), 3, 1.0)]


def greens(a, x, y, k=1.0, d=0.0):
    E = []
    for q in range(5):
        i = uid("leaf")
        E += [P(a, f"M{x - 100 * k + 50 * k * q},{y + 40 * k} Q{x - 130 * k + 50 * k * q},{y - 60 * k} {x - 90 * k + 50 * k * q},{y - 100 * k} "
                   f"Q{x - 60 * k + 50 * k * q},{y - 40 * k} {x - 100 * k + 50 * k * q},{y + 40 * k}", c="green", w=5, fill="green", idp=i),
              pop(a, i, d + 0.1 * q), wig(a, i, (x - 100 * k + 50 * k * q, y + 40 * k), 6, 1.2 + 0.2 * q)]
    return E


def bowl(a, x, y, k=1.0, d=0.0):
    i = uid("bowl")
    return [P(a, f"M{x - 110 * k},{y} Q{x},{y + 150 * k} {x + 110 * k},{y} Z", c="ink", w=5, idp=i),
            P(a, f"M{x - 100 * k},{y} Q{x - 50 * k},{y - 70 * k} {x},{y - 60 * k} Q{x + 60 * k},{y - 80 * k} {x + 100 * k},{y}", c="muted", w=4, fill="muted", idp=i),
            pop(a, i, d), bob(a, i, 5, 1.0)]


def courier(a, x0, y0, x1, y1, d=0.0, dur=1.6):
    """外卖小哥：一张纸条（小方块）沿着肠—脑的线慢慢跑。"""
    line, n = uid("nerve"), uid("note")
    return [P(a, f"M{x0},{y0} Q{(x0 + x1) / 2},{min(y0, y1) - 120} {x1},{y1}", c="muted", w=5, idp=line),
            {"t": "move", "at": a, "kind": "signal", "targets": [line], "dur": 1.2},
            R(a, x0 - 30, y0 - 22, 60, 44, c="gold", fill="gold", idp=n), sh(a, n, x1 - x0, y1 - y0, d, dur), wig(a, n, (x0, y0), 8, 2.5)]


def brain(a, x, y, k=1.0):
    i = uid("brain")
    E = [P(a, f"M{x - 110 * k},{y + 40 * k} Q{x - 150 * k},{y - 60 * k} {x - 60 * k},{y - 90 * k} Q{x},{y - 140 * k} {x + 60 * k},{y - 90 * k} "
              f"Q{x + 150 * k},{y - 60 * k} {x + 110 * k},{y + 40 * k} Q{x},{y + 90 * k} {x - 110 * k},{y + 40 * k} Z", c="blue", w=6, idp=i),
         P(a, f"M{x - 60 * k},{y - 30 * k} Q{x - 20 * k},{y + 10 * k} {x},{y - 40 * k} Q{x + 30 * k},{y + 10 * k} {x + 60 * k},{y - 30 * k}", c="blue", w=4, idp=i),
         pulse(a, i, 0.6, 1.0), bob(a, i, 5, 0.9)]
    return E


def scale(a, x, y, d=0.0, tilt=10):
    i, bm = uid("scl"), uid("beam")
    return [P(a, f"M{x},{y} L{x},{y - 220} M{x - 80},{y} L{x + 80},{y}", c="ink", w=6, idp=i),
            P(a, f"M{x - 220},{y - 220} L{x + 220},{y - 220} M{x - 220},{y - 220} L{x - 260},{y - 140} L{x - 180},{y - 140} Z M{x + 220},{y - 220} L{x + 180},{y - 140} L{x + 260},{y - 140} Z",
              c="ink", w=5, idp=bm), rot(a, bm, tilt, (x, y - 220), d, 0.8), wig(a, bm, (x, y - 220), 1.5, 0.8)]


def hosp(a, x, y, d=0.0):
    i, cr = uid("hos"), uid("cr")
    return [R(a, x - 220, y - 200, 440, 400, c="ink", idp=i), P(a, f"M{x - 220},{y - 200} L{x},{y - 320} L{x + 220},{y - 200}", c="ink", w=5, idp=i),
            P(a, f"M{x - 50},{y - 60} L{x + 50},{y - 60} M{x},{y - 110} L{x},{y - 10}", c="red", w=12, idp=cr), pop(a, i, d), pulse(a, cr, d + 0.4, 0.8), bob(a, cr, 6, 1.4)]


def amb(a, n=2):
    E = star(a, 110, 110, 0.1, r=20) + star(a, 1810, 990, 0.3, r=20)
    if n > 2:
        E += star(a, 1810, 110, 0.5, r=20)
    return E


B = []


def bd(a, *parts, n=2):
    E = []
    for p in parts:
        E += p
    B.append(E + amb(a, n))


# 0 same meals
bd(0, bowl(0, 500, 520, 1.3, 0.1), bowl(0, 1400, 520, 1.3, 0.3), T(0, 960, 520, 90, "=", c="ink", d=0.4), T(0, 500, 300, 56, "同样的热量", c="ink", d=0.6),
   crowd(0, 760, 760, 6, 1, gap=80, k=1.0, d=0.5))
# 0.5 +500 kcal
t, ti = tummy(0.5, 600, 560, 1.2, sweat=True)
bd(0.5, t, BIG(0.5, 1300, 480, "+500", c="red", d=0.2, s=150), T(0.5, 1300, 640, 64, "大卡 / 天", c="ink", d=0.4), cake(0.5, 1300, 860, 0.7, 0.8))
# 1 weibo hot search
E = []
for k in range(5):
    i = uid("row")
    E += [R(1, 460, 240 + 110 * k, 1000, 80, c="red" if k == 2 else "muted", fill="red" if k == 2 else None, idp=i), pop(1, i, 0.1 + 0.12 * k)]
bd(1, E, [sh(1, E[4]["id"], 0, -110, 0.9, 0.5)], T(1, 960, 380 + 110 * 0 - 110, 50, "微博热搜", c="ink", d=0.0), T(1, 960, 480, 50, "原来吃得差才会胖", c="ink", d=0.6))
# 1.5 33 million
bd(1.5, BIG(1.5, 960, 420, "3300万", c="red", d=0.1, s=150), crowd(1.5, 300, 680, 16, 2, gap=90, k=0.8, d=0.2, step=0.02), T(1.5, 960, 960, 52, "热度", c="muted", d=0.4))
# 2 beef & eggs not culprits
bd(2, steak(2, 600, 480, 1.4, 0.1), egg(2, 1250, 480, 1.4, 0.3), check(2, 600, 760, d=0.8), check(2, 1250, 760, d=1.0), T(2, 960, 960, 56, "不是元凶", c="green", d=0.6))
# 2.5 cake & milk tea
bd(2.5, cake(2.5, 600, 560, 1.6, 0.0), tea(2.5, 1300, 540, 1.4, 0.3), cross(2.5, 600, 820, d=0.8), cross(2.5, 1300, 820, d=1.0))
# 3 question
q = uid("q")
bd(3, bowl(3, 600, 520, 1.3, 0.0), bowl(3, 1300, 520, 1.3, 0.2), T(3, 960, 520, 90, "=", c="ink", d=0.3),
   [{"t": "icon", "at": 3, "id": q, "name": "question", "x": 860, "y": 650, "size": 200, "c": "red"}, pop(3, q, 0.6), wig(3, q, (960, 750), 8, 1.4)])
# 3.5 why fatter
t, ti = tummy(3.5, 960, 560, 1.4)
bd(3.5, t, [{"t": "move", "at": 3.5, "kind": "grow", "targets": [ti], "axis": "x", "from": 1, "to": 1.3, "pivot": [960, 560], "dur": 1.0, "delay": 0.4}],
   BIG(3.5, 960, 960, "为什么会胖？", c="red", d=0.3, s=100))
# 4 meet Tummy
t, ti = tummy(4, 960, 560, 1.8)
bd(4, t, [pop(4, ti, 0.0)], BIG(4, 1550, 460, "小胃", c="red", d=0.4, s=140), star(4, 500, 360, 0.6, r=40), n=3)
# 4.5 am I full?
t, ti = tummy(4.5, 700, 600, 1.3)
q = uid("q")
bd(4.5, t, T(4.5, 1300, 420, 80, "吃饱了吗？", c="ink", d=0.2),
   [{"t": "icon", "at": 4.5, "id": q, "name": "question", "x": 1250, "y": 560, "size": 200, "c": "red"}, pop(4.5, q, 0.6), pulse(4.5, q, 1.0)])
# 5 NIH 2019
bd(5, hosp(5, 760, 560, 0.1), BIG(5, 1400, 440, "2019", c="ink", d=0.3, s=130), T(5, 1400, 620, 56, "美国国立卫生研究院", c="blue", d=0.6))
# 5.5 20 people 4 weeks
E = []
for k in range(4):
    i = uid("wk")
    E += [R(5.5, 1080 + 190 * k, 320, 150, 150, c="blue", idp=i), pop(5.5, i, 0.4 + 0.2 * k), bob(5.5, i, 4, 1.0 + 0.2 * k)]
bd(5.5, crowd(5.5, 250, 350, 5, 4, gap=120, k=1.0, d=0.0, step=0.03), E, BIG(5.5, 620, 900, "20 人", c="ink", d=0.3, s=100), BIG(5.5, 1380, 640, "4 周", c="blue", d=0.9, s=110))
# 6 ultra-processed
bd(6, cake(6, 500, 560, 1.2, 0.0), tea(6, 900, 540, 1.1, 0.2), bowl(6, 1300, 560, 1.0, 0.4), T(6, 960, 860, 70, "两周 超加工", c="red", d=0.4))
# 6.5 minimally processed
bd(6.5, greens(6.5, 520, 540, 1.4, 0.0), egg(6.5, 960, 520, 1.1, 0.3), steak(6.5, 1400, 540, 1.0, 0.5), T(6.5, 960, 860, 70, "两周 少加工", c="green", d=0.4))
# 7 same calories sugar fat fiber
bd(7, scale(7, 960, 760, 0.6, tilt=0), cake(7, 680, 500, 0.8, 0.1), greens(7, 1240, 520, 0.9, 0.2),
   T(7, 960, 900, 52, "热量 糖 脂肪 纤维", c="ink", d=0.3))
# 7.5 exactly matched
bd(7.5, BIG(7.5, 960, 420, "全都一样", c="blue", d=0.1, s=130), check(7.5, 600, 700, d=0.4), check(7.5, 960, 700, d=0.6), check(7.5, 1320, 700, d=0.8))
# 8 eat as much as you like
t, ti = tummy(8, 1300, 600, 1.2)
bd(8, t, bowl(8, 500, 420, 0.8, 0.1), bowl(8, 700, 600, 0.8, 0.3), bowl(8, 500, 780, 0.8, 0.5), T(8, 960, 960, 64, "随便吃", c="green", d=0.4))
# 9 +500 per day
E = bar(9, 600, 820, 240, 380, "green", d=0.1) + bar(9, 1100, 820, 240, 560, "red", d=0.4)
bd(9, E, T(9, 720, 900, 52, "少加工", c="ink"), T(9, 1220, 900, 52, "超加工", c="ink"), BIG(9, 1550, 340, "+500", c="red", d=0.9, s=120))
# 9.5 two bowls of rice
bd(9.5, bowl(9.5, 650, 560, 1.6, 0.0), bowl(9.5, 1250, 560, 1.6, 0.3), BIG(9.5, 960, 900, "≈ 两碗米饭", c="ink", d=0.6, s=100), n=3)
# 10 gained almost a kilo
bd(10, scale(10, 960, 820, 0.4, tilt=-12), BIG(10, 960, 300, "+0.9 公斤", c="red", d=0.2, s=120), crowd(10, 640, 520, 1, 1, k=2.0, d=0.1), cake(10, 1300, 560, 0.8, 0.5))
# 10.5 lost about the same
bd(10.5, scale(10.5, 960, 820, 0.4, tilt=12), BIG(10.5, 960, 300, "−0.9 公斤", c="green", d=0.2, s=120), greens(10.5, 640, 560, 0.9, 0.3), egg(10.5, 1300, 540, 0.9, 0.5))
# 11 twist one: equally tasty
E = []
for k in range(2):
    for s_ in range(5):
        E += star(11, 340 + 140 * s_ + 760 * k, 640, 0.3 + 0.08 * s_ + 0.3 * k, r=34)
bd(11, BIG(11, 960, 220, "反转一", c="red", d=0.0, s=90), cake(11, 620, 440, 0.9, 0.1), greens(11, 1380, 440, 0.9, 0.3), E)
# 11.5 not about flavor
bd(11.5, T(11.5, 960, 400, 90, "不是因为更香", c="ink", d=0.1), cross(11.5, 960, 640, d=0.6), crowd(11.5, 500, 860, 10, 1, gap=100, k=0.8, d=0.3))
# 12 where from?
t, ti = tummy(12, 700, 600, 1.3)
bd(12, t, BIG(12, 1350, 480, "+500", c="red", d=0.1, s=130), arr(12, 1150, 480, 900, 560, c="red", d=0.5))
# 12.5 come from
q = uid("q")
bd(12.5, [{"t": "icon", "at": 12.5, "id": q, "name": "question", "x": 820, "y": 300, "size": 300, "c": "red"}, pop(12.5, q, 0.0), wig(12.5, q, (970, 450), 8, 1.6)],
   crowd(12.5, 500, 820, 10, 1, gap=100, k=0.9, d=0.2), T(12.5, 960, 1000, 56, "从哪来？", c="ink", d=0.4), n=3)
# 13 clue one: faster
cl = uid("clock")
hd = uid("hand")
bd(13, [O(13, 700, 520, 220, c="ink", idp=cl), P(13, "M700,520 L700,340", c="red", w=8, idp=hd), spin(13, hd, (700, 520), 240), pulse(13, cl, 0.4, 0.8)],
   T(13, 1350, 300, 70, "线索一", c="red", d=0.0), BIG(13, 1350, 560, "吃得更快", c="ink", d=0.3, s=110))
# 13.5 soft, a few bites
E = []
for k in range(4):
    b = uid("bite")
    E += [O(13.5, 500, 500, 40, c="gold", fill="gold", idp=b), sh(13.5, b, 900, 0, 0.1 + 0.3 * k, 0.4)]
t, ti = tummy(13.5, 1450, 600, 1.0)
bd(13.5, E, t, T(13.5, 700, 800, 64, "又软又好嚼", c="ink", d=0.3))
# 14 full signal gut -> brain
t, ti = tummy(14, 500, 680, 0.9)
bd(14, t, brain(14, 1450, 340, 1.2), courier(14, 620, 560, 1300, 360, d=0.3, dur=2.0), T(14, 1000, 900, 60, "“吃饱了”的信号", c="gold", d=0.4))
# 14.5 takes time
cl = uid("clock")
hd = uid("hand")
bd(14.5, [O(14.5, 960, 480, 200, c="ink", idp=cl), P(14.5, "M960,480 L1080,400", c="blue", w=8, idp=hd), spin(14.5, hd, (960, 480), 60)],
   BIG(14.5, 960, 860, "要花时间", c="blue", d=0.3, s=110), crowd(14.5, 300, 860, 2, 1, gap=100, k=0.8, d=0.5))
# 15 courier note "enough"
mot = uid("moto")
w1, w2 = uid("w"), uid("w")
bd(15, [R(15, 300, 520, 260, 120, c="blue", fill="blue", idp=mot), O(15, 340, 660, 40, c="ink", idp=w1), O(15, 520, 660, 40, c="ink", idp=w2),
        sh(15, [mot, w1, w2], 600, 0, 0.3, 2.0), spin(15, w1, (340, 660), 200), spin(15, w2, (520, 660), 200)],
   T(15, 960, 300, 80, "“够了”", c="gold", d=0.3), brain(15, 1550, 560, 1.0))
# 15.5 plate empty before note arrives
bd(15.5, bowl(15.5, 600, 520, 1.5, 0.0),
   courier(15.5, 900, 700, 1600, 400, d=0.2, dur=2.2), BIG(15.5, 600, 860, "光了！", c="red", d=0.6, s=110))
# 16 clue two energy density
bd(16, T(16, 960, 220, 70, "线索二", c="red", d=0.0), BIG(16, 960, 420, "热量密度", c="ink", d=0.2, s=120),
   bar(16, 600, 860, 200, 160, "green", d=0.5) + bar(16, 1120, 860, 200, 360, "red", d=0.8))
# 16.5 each bite packs more
E = []
for k in range(5):
    b = uid("cal")
    E += [O(16.5, 1300 + 60 * (k % 3), 380 + 60 * (k // 3), 24, c="red", fill="red", idp=b), pop(16.5, b, 0.1 + 0.15 * k), bob(16.5, b, 5, 1.0 + 0.2 * k)]
bd(16.5, cake(16.5, 600, 560, 1.4, 0.0), E, T(16.5, 1350, 760, 60, "一口更多热量", c="red", d=0.4))
# 17 cake vs greens same size
bd(17, cake(17, 560, 560, 1.4, 0.0), greens(17, 1360, 560, 1.4, 0.2), T(17, 960, 560, 90, "≈", c="ink", d=0.4), T(17, 960, 860, 60, "个头差不多", c="ink", d=0.5))
# 17.5 tenfold
E = bar(17.5, 640, 860, 220, 560, "red", d=0.1) + bar(17.5, 1160, 860, 220, 56, "green", d=0.4)
bd(17.5, E, BIG(17.5, 960, 260, "×10", c="red", d=0.7, s=140), T(17.5, 750, 940, 50, "蛋糕", c="ink"), T(17.5, 1270, 940, 50, "青菜", c="ink"))
# 18 stomach feels full by stretch
t, ti = tummy(18, 960, 560, 1.4)
bd(18, t, [{"t": "move", "at": 18, "kind": "grow", "targets": [ti], "axis": "both", "from": 0.8, "to": 1.25, "pivot": [960, 560], "dur": 1.6, "delay": 0.2}],
   arr(18, 600, 560, 720, 560, c="blue", d=0.5), arr(18, 1320, 560, 1200, 560, c="blue", d=0.5), T(18, 960, 960, 60, "撑开 = 饱", c="blue", d=0.6))
# 18.5 bad at counting calories
t, ti = tummy(18.5, 700, 600, 1.2, mood="sad", sweat=True)
bd(18.5, t, T(18.5, 1350, 420, 80, "1, 2, ...?", c="ink", d=0.2), cross(18.5, 1350, 640, d=0.7), T(18.5, 1350, 840, 56, "不会数热量", c="red", d=0.5))
# 19 twist two hormones
bd(19, BIG(19, 960, 200, "反转二", c="red", d=0.0, s=90), greens(19, 960, 520, 1.4, 0.2), crowd(19, 600, 820, 8, 1, gap=100, k=0.8, d=0.4))
# 19.5 full hormone up, hunger down
E = bar(19.5, 500, 820, 200, 460, "green", d=0.1) + bar(19.5, 1200, 820, 200, 160, "red", d=0.4)
bd(19.5, E, arr(19.5, 800, 760, 800, 380, c="green", d=0.6), arr(19.5, 1500, 380, 1500, 760, c="red", d=0.8),
   T(19.5, 600, 900, 52, "饱的激素", c="green"), T(19.5, 1300, 900, 52, "饿的激素", c="red"))
# 20 body brakes
t, ti = tummy(20, 700, 600, 1.2)
bd(20, t, T(20, 1350, 420, 70, "吃天然食物", c="green", d=0.2), greens(20, 1350, 640, 0.9, 0.4))
# 20.5 hits brakes
br = uid("brake")
bd(20.5, [O(20.5, 960, 480, 200, c="red", fill="red", idp=br), pop(20.5, br, 0.1), pulse(20.5, br, 0.6, 0.8), spin(20.5, br, (960, 480), 30)],
   BIG(20.5, 960, 480, "停", c="ink", d=0.3, s=150), T(20.5, 960, 860, 64, "身体自己踩刹车", c="ink", d=0.5))
# 21 twist three: not little, not poor
bd(21, BIG(21, 960, 200, "反转三", c="red", d=0.0, s=90), T(21, 560, 480, 70, "吃得少", c="ink", d=0.2), T(21, 1360, 480, 70, "穷", c="ink", d=0.4),
   cross(21, 560, 640, d=0.6), cross(21, 1360, 640, d=0.8))
# 21.5 too effortless
gear = uid("gear")
bd(21.5, [O(21.5, 600, 520, 160, c="ink", idp=gear), P(21.5, "M600,340 L600,700 M420,520 L780,520 M470,390 L730,650 M730,390 L470,650", c="ink", w=8, idp=gear),
          spin(21.5, gear, (600, 520), 60)], BIG(21.5, 1300, 480, "太“省事”", c="red", d=0.4, s=110), cake(21.5, 1300, 760, 0.8, 0.6))
# 22 factory does chewing
fac = uid("fac")
sm = uid("smoke")
bd(22, [R(22, 400, 400, 520, 360, c="ink", idp=fac), R(22, 760, 260, 80, 140, c="ink", idp=fac), O(22, 800, 220, 40, c="muted", fill="muted", idp=sm),
        sh(22, sm, 30, -140, 0.2, 1.6), pop(22, fac, 0.0)], T(22, 1350, 360, 64, "嚼", c="ink", d=0.3), T(22, 1350, 500, 64, "剥", c="ink", d=0.5),
   T(22, 1350, 640, 64, "消化", c="ink", d=0.7))
# 22.5 done for you
E = []
for k in range(4):
    b = uid("pk")
    E += [R(22.5, 300, 560, 90, 90, c="gold", fill="gold", idp=b), sh(22.5, b, 1100, 0, 0.1 + 0.35 * k, 1.0)]
t, ti = tummy(22.5, 1600, 620, 0.9)
bd(22.5, E, t, [P(22.5, "M200,660 L1450,660", c="ink", w=5)], T(22.5, 800, 380, 64, "提前帮你干完", c="ink", d=0.3))
# 23 easy on teeth
th = uid("tooth")
bd(23, [P(23, "M760,360 Q960,280 1160,360 L1120,640 L1040,560 L960,640 L880,560 L800,640 Z", c="ink", w=6, idp=th), pop(23, th, 0.0), bob(23, th, 8, 1.4),
        wig(23, th, (960, 640), 5, 2.0)], check(23, 1400, 460, d=0.6), T(23, 960, 860, 64, "牙：省事了", c="green", d=0.4))
# 23.5 not on waist
belt = uid("belt")
bd(23.5, [R(23.5, 560, 460, 800, 120, c="ink", fill="muted", idp=belt), {"t": "move", "at": 23.5, "kind": "grow", "targets": [belt], "axis": "x", "from": 1, "to": 1.25,
                                                                     "pivot": [960, 520], "dur": 1.0, "delay": 0.3}, wig(23.5, belt, (960, 520), 2, 1.2)],
   cross(23.5, 960, 760, d=0.8), T(23.5, 960, 300, 64, "腰：不省事", c="red", d=0.2))
# 24 milk tea not filling
t, ti = tummy(24, 1350, 600, 1.1, mood="sad")
bd(24, tea(24, 600, 560, 1.6, 0.0), t, T(24, 1350, 300, 60, "还饿？", c="red", d=0.6))
# 24.5 brain undercounts liquid calories
bd(24.5, brain(24.5, 700, 500, 1.4), T(24.5, 1350, 420, 64, "喝下去的热量", c="gold", d=0.2), cross(24.5, 1350, 600, d=0.6),
   T(24.5, 1350, 780, 52, "容易漏算（不少研究认为）", c="muted", d=0.8))
# 25 beef & eggs: protein keeps you full
bd(25, steak(25, 560, 500, 1.3, 0.0), egg(25, 1000, 500, 1.2, 0.2), T(25, 1450, 500, 70, "蛋白质", c="red", d=0.4), crowd(25, 600, 820, 8, 1, gap=100, k=0.8, d=0.5))
# 25.5 harder to overeat
t, ti = tummy(25.5, 700, 600, 1.3)
bd(25.5, t, check(25.5, 1350, 400, d=0.3), T(25.5, 1350, 620, 64, "饱得更久", c="green", d=0.5), egg(25.5, 1350, 840, 0.6, 0.7))
# 26 roughly right
bd(26, check(26, 960, 420, d=0.1), T(26, 960, 700, 80, "大方向是对的", c="green", d=0.3), crowd(26, 360, 880, 12, 1, gap=100, k=0.8, d=0.4))
# 26.5 how much AND what kind
bd(26.5, BIG(26.5, 560, 420, "吃多少", c="ink", d=0.1, s=100), BIG(26.5, 960, 420, "+", c="ink", d=0.3, s=100), BIG(26.5, 1360, 420, "吃什么", c="red", d=0.5, s=100),
   cake(26.5, 560, 760, 0.8, 0.6), greens(26.5, 1360, 760, 0.8, 0.8))
# 27 cake isn't poison
bd(27, cake(27, 960, 520, 1.8, 0.0), T(27, 960, 860, 64, "蛋糕有毒？", c="ink", d=0.3), cross(27, 1350, 400, d=0.7))
# 27.5 calorie is a calorie
bd(27.5, scale(27.5, 960, 800, 0.3, tilt=0), BIG(27.5, 960, 260, "热量还是热量", c="ink", d=0.1, s=100), cake(27.5, 720, 520, 0.6, 0.4), greens(27.5, 1200, 520, 0.6, 0.6))
# 28 ultra-processed
bd(28, cake(28, 500, 560, 1.1, 0.0), tea(28, 960, 540, 1.1, 0.2), bowl(28, 1420, 560, 1.0, 0.4), T(28, 960, 880, 64, "超加工食品", c="red", d=0.3))
# 28.5 easy to eat more
t, ti = tummy(28.5, 960, 560, 1.3, sweat=True)
bd(28.5, t, [{"t": "move", "at": 28.5, "kind": "grow", "targets": [ti], "axis": "both", "from": 1, "to": 1.2, "pivot": [960, 560], "dur": 1.2, "delay": 0.2}],
   BIG(28.5, 960, 960, "特别容易多吃", c="red", d=0.4, s=90))
# 29 fine print small study
bd(29, BIG(29, 960, 200, "友情提示", c="muted", d=0.0, s=80), crowd(29, 500, 480, 10, 2, gap=100, k=0.9, d=0.1, step=0.03), T(29, 960, 800, 64, "20 人 · 4 周", c="ink", d=0.6))
# 29.5 more research, everyone different
E = []
for k, c in enumerate(["ink", "blue", "red", "green", "gold"]):
    E += person(29.5, 500 + 230 * k, 620, 1.2 + 0.25 * (k % 3), c=c, d=0.1 + 0.15 * k)
bd(29.5, E, T(29.5, 960, 860, 64, "每个人不一样", c="ink", d=0.6))
# 30 listen to doctor
bd(30, hosp(30, 700, 560, 0.0), check(30, 1300, 480, d=0.5), T(30, 1300, 700, 64, "听医生的", c="green", d=0.3))
# 30.5 not hot list not whiteboard
wb = uid("wb")
bd(30.5, [R(30.5, 1100, 300, 500, 340, c="ink", idp=wb), pop(30.5, wb, 0.4), rot(30.5, wb, -5, (1350, 640), 0.7, 0.5)], T(30.5, 560, 440, 70, "热搜", c="red", d=0.1),
   cross(30.5, 560, 620, d=0.3), cross(30.5, 1350, 470, d=0.9), T(30.5, 1350, 760, 52, "也别听白板", c="ink", d=0.8))
# 31 eat slower
cl = uid("clock")
hd = uid("hand")
bd(31, [O(31, 640, 520, 200, c="ink", idp=cl), P(31, "M640,520 L740,400", c="green", w=8, idp=hd), spin(31, hd, (640, 520), 20)],
   BIG(31, 1300, 520, "吃慢一点", c="green", d=0.3, s=110), bowl(31, 1300, 800, 0.8, 0.5))
# 31.5 note catches up with chopsticks
cs = uid("chop")
bd(31.5, courier(31.5, 400, 700, 1200, 420, d=0.1, dur=1.6),
   [P(31.5, "M1300,300 L1600,600 M1340,280 L1640,580", c="ink", w=8, idp=cs), wig(31.5, cs, (1600, 600), 6, 2.0)], T(31.5, 960, 920, 60, "纸条追上筷子", c="gold", d=0.5))
# 32 Tummy says
t, ti = tummy(32, 960, 600, 1.6)
bd(32, t, T(32, 960, 200, 70, "我不是不饱", c="ink", d=0.2), n=3)
# 32.5 just slow messages
t, ti = tummy(32.5, 600, 620, 1.2)
bd(32.5, t, courier(32.5, 760, 520, 1500, 340, d=0.1, dur=2.0), BIG(32.5, 1200, 860, "消息慢", c="red", d=0.5, s=110), brain(32.5, 1600, 300, 0.8), n=3)

B.sort(key=lambda b: min(e["at"] for e in b))
assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "zh")
