"""烧脑科普（约 8 分钟）《会飞的特斯拉，到底能飞多久？》——Eddie 2026-10-16 09:29：“马斯克会飞的汽车值得深入探讨其黑科技，插入相关视频，
做一个烧脑的科普，8 分钟左右”；09:34：“先做中文，中英字幕”。
事实：TechCrunch、Electrek、CNBC、CNN 2026-10-15/16 报道（得州发布会、倒挂轨道、飞越五辆车、0–60 mph 约 1 秒、10 个冷气喷口、600 升压缩空气、
后部推力约 80 千牛（Electrek）、屏幕上约 4700 公斤下压力、碳纤维缠绕高压气罐、马斯克原话、2028 量产、2017 年起多次推迟、蛇河峡谷）；
1978 年 Brabham BT46B 风扇车；1974 年 Evel Knievel 飞越蛇河峡谷失败。估算（片中都说是估算）：气罐空气量、喷气时间、悬停时间、悬停功率对比、充气电量。
插入的视频：本目录 飞行实验.html（虚拟实验）的录屏 _lab.mp4（发布会画面属于特斯拉，不剪进片子，只给链接）。
    python3 make.py <kokoro 模型目录> [--boards-only] && python3 ../../../tools/whiteboard/wb.py . [--mp4]"""
import json, sys  # noqa: E401
from pathlib import Path
import numpy as np, soundfile as sf  # noqa: E401
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[2] / "services" / "gateway"))
sys.path.insert(0, str(here.parent))
from app.production.whiteboard import ai as wai  # noqa: E402
from app.production.whiteboard.core import missing_chars  # noqa: E402
from app.production.whiteboard.speech import speakable  # noqa: E402
from popkit import bubble, car, car_drive, stick, txt  # noqa: E402

S = [  # (中文讲稿, English subtitle)
 ("昨天，美国得州，一辆白色跑车开上了一条倒挂的轨道。", "Yesterday in Texas, a white sports car drove onto an upside-down track."),
 ("它头朝下开过去，翻个身，稳稳落地。", "It drove across upside down, flipped over, and landed."),
 ("然后，它从五辆车的头顶上，“飞”了过去。", "Then it \"flew\" over the roofs of five cars."),
 ("马斯克说：这就是将来真正上路的那辆车。", "Musk said: this is the actual car that will be on the roads."),
 ("网上吵翻了：这是真飞，还是跳得很有派头？", "The internet split: real flight, or a very stylish jump?"),
 ("今天我们不站队，我们算账。八分钟，把这辆车拆开看看。", "Today we don't take sides. We do the math. Eight minutes to take this car apart."),
 ("先认识一下今天的主角：小 R，一辆有点紧张的跑车。", "Meet today's star: R, a slightly nervous sports car."),
 ("第一个黑科技：倒着开，为什么掉不下来？", "Trick one: driving upside down, why doesn't it fall?"),
 ("答案在车底：几台大风扇，拼命把车底下的空气往外抽。", "The answer is underneath: fans pump the air out from under the car."),
 ("车底的空气变稀了，车顶上的大气还在使劲压。一上一下差出来的这股力，就把车按在路面上。", "Thin air below, the whole atmosphere pressing above: the difference pins the car to the road."),
 ("这招叫“风扇车”，一点也不新。", "It's called a fan car, and it isn't new."),
 ("1978 年，F1 有一辆赛车屁股上装了个大风扇，只比了一场，就赢了。", "In 1978, an F1 car with a giant fan on its back raced once, and won."),
 ("然后就被叫停了。对手说它像个吸尘器，还把石子往后喷。", "Then it was pulled. Rivals called it a vacuum cleaner that sprayed stones behind it."),
 ("关键在这里：机翼要靠速度才有下压力，风扇不用。车停着不动，也能把自己吸住。", "Here's the key: wings need speed to make downforce, fans don't. Even standing still, the car sticks."),
 ("所以，只要吸力比车重还大，天花板就成了地板。", "So once the suction beats the car's weight, the ceiling becomes the floor."),
 ("特斯拉屏幕上显示的吸力，约四千七百公斤，可能是车重的两倍多。", "Tesla's screen showed about 4,700 kg of downforce, maybe more than twice the car's weight."),
 ("连科技媒体都说，这个数字可能有点水分。另一辆风扇车，一吨来重，号称两吨吸力，已经够吓人了。", "Even tech press suspect it's inflated. Another fan car, about a ton, claims two tons, which is already wild."),
 ("第一个黑科技，打分：真本事。", "Trick one gets a score: the real thing."),
 ("第二个黑科技：零到一百公里，只要一秒。", "Trick two: zero to sixty in one second."),
 ("算一下：一秒加到每小时九十六公里，等于每秒提速二十七米，差不多是两点七个重力加速度。", "Do the math: 96 km/h in one second is 27 meters per second, every second. About 2.7 g."),
 ("问题是，车靠轮胎抓着地面往前推。抓得再紧，最多也就一个多 g。", "But a car pushes off the road through its tires, and even great tires top out at one-point-something g."),
 ("怎么办？两招。", "So what now? Two tricks."),
 ("第一招，还是风扇：车被按得越紧，轮胎抓得越牢。", "First, the fans again: the harder the car is pressed down, the better the tires grip."),
 ("第二招更狠：干脆不靠地面。车屁股后面，向后喷气。", "Second, more brutal: don't rely on the road at all. Blow gas out the back."),
 ("这就是火箭的原理：把东西往后扔，自己就往前走。", "That's how a rocket works: throw stuff backward, and you go forward."),
 ("据报道，后面四个喷口加起来，约八万牛顿推力。一辆两吨的车，光靠喷气，就有四个 g。", "Reportedly, the four rear jets make about 80 kilonewtons. For a two-ton car, that alone is 4 g."),
 ("不过，还没有独立测量，这个“一秒”，我们先打个问号。", "No independent measurement yet, so that 'one second' gets a question mark."),
 ("第三个，也是今天的重头戏：它到底能飞多久？", "Trick three, the main event: how long can it actually fly?"),
 ("它喷的不是火，是压缩空气。官方说，车上有六百升压缩空气，供十个喷口用。", "It doesn't burn anything. It blows compressed air: Tesla says 600 liters feed ten jets."),
 ("六百升听起来很多？其实也就三个浴缸。", "600 liters sounds like a lot? It's about three bathtubs."),
 ("压得越狠，装得越多。官方没说压力，我们按常见的高压气罐估一估：大约能装两三百公斤空气。", "Tesla didn't give the pressure. Assuming a typical high-pressure tank, that's roughly 200 to 300 kilograms of air."),
 ("冷空气喷出去，最快也就每秒几百米。要顶出八万牛的推力，每秒得喷掉一百多公斤。", "Cold air jets out at a few hundred meters per second at most. For 80 kN, you burn over 100 kilos every second."),
 ("两三百公斤，每秒一百多公斤。全力喷，一两秒，推力就掉得差不多了。", "Two or three hundred kilos, over a hundred per second: at full blast, the thrust is mostly gone in a second or two."),
 ("那不全力，只是把车托在半空悬停呢？两吨的车，要两万牛推力，每秒吃掉三十多公斤空气。", "What about just hovering? Holding up two tons takes 20 kN, eating over 30 kilos of air a second."),
 ("而且越喷，罐里压力越低，推力越小，最后托不住了。", "And as it empties, pressure and thrust drop, until it can't hold the car."),
 ("不信？我们做了一个虚拟实验，你可以自己调。", "Don't believe us? We built a virtual lab. Try it yourself."),
 ("三百个大气压，悬停三米：五秒左右。", "300 atmospheres, hover at three meters: about five seconds."),
 ("压到七百个大气压：十秒左右。", "Squeeze it to 700: about ten seconds."),
 ("再把车减掉五百公斤：也就十二秒多。", "Then cut 500 kilos off the car: just over twelve."),
 ("所以结论是：它不是“飞”，是一次很贵的“跳”。", "So the verdict: it doesn't fly. It does a very expensive jump."),
 ("再烧一点脑：同样托起两吨，直升机能在天上待一个小时，喷口为什么只能撑几秒？", "A brain-burner: a helicopter holds up two tons for an hour. Why do jets last only seconds?"),
 ("关键是：推力，是“喷出去的空气乘速度”；花掉的力气，却是“空气乘速度的平方”。", "Key: thrust is air times speed, but the energy you spend is air times speed squared."),
 ("少量空气喷得飞快，推力一样，力气却花得多得多；大量空气慢慢往下推，最省力。", "Blasting a little air very fast wastes energy. Gently pushing lots of air is efficient."),
 ("直升机的大旋翼，就是在慢慢推一大片空气。算一下，托起同样两吨，小喷口要的功率，大约是十米旋翼的三十倍。", "A big rotor gently pushes a huge column of air. For the same two tons, small jets need about thirty times the power of a ten-meter rotor."),
 ("所以你看，真正在做飞行汽车的公司，造出来的都长着螺旋桨。", "That's why the companies actually building flying cars all put propellers on them."),
 ("第三个黑科技，打分：物理没错，但它是表演，不是交通工具。", "Trick three gets a score: right physics, but it's a stunt, not transportation."),
 ("好，假设你就坐在里面。", "OK, suppose you're sitting in it."),
 ("起步四个 g，相当于过山车最猛的那一下，还要再猛一点。", "Launching at 4 g is like the wildest moment on a roller coaster, and then some."),
 ("翻跟头的时候头朝下，血往脑袋里冲。科技媒体都在问：要不要穿战斗机飞行员的抗荷服？", "Upside down, blood rushes to your head. Tech press ask: will you need a fighter pilot's g-suit?"),
 ("再看车里：每一个空隙，都塞满了碳纤维缠绕的高压气罐。", "And inside: every spare gap is packed with carbon-fiber-wrapped high-pressure tanks."),
 ("这种罐子又轻又结实，但 SpaceX 几次火箭出事，都和这类罐子有关。", "They're light and strong, but this type of tank has been linked to SpaceX rocket failures."),
 ("还有一道算术题：把六百升充满，最理想也要二十多度电，够这辆车跑一百多公里。", "And a sum: filling those 600 liters takes, ideally, over 20 kWh, enough to drive this car over 100 km."),
 ("马斯克自己说：安全不是主要目标；他们会“争取不害死任何人”。", "Musk himself said safety is not the main goal, and they will 'aspire not to kill anyone'."),
 ("这两句是原话，我们不加评论。", "Those are his words. No comment from us."),
 ("那这辆车，到底是什么？", "So what is this car, really?"),
 ("吸地：真本事，七十年代就有，现在做得更猛。", "The suction: real, around since the seventies, now turned up."),
 ("一秒破百：物理上说得通，等独立测量。", "The one-second sprint: physically plausible, awaiting independent tests."),
 ("飞：几秒钟的表演。很酷，但别指望它带你上班。", "The flying: a few seconds of show. Cool, but it won't fly you to work."),
 ("时间表：说是 2028 年量产。这辆车 2017 年就发布过，之后推迟了一次又一次。", "Timeline: production in 2028. It was first unveiled in 2017 and delayed again and again."),
 ("最后一个彩蛋：马斯克说，也许会开着它飞越蛇河峡谷。", "One last easter egg: Musk said it might jump the Snake River Canyon."),
 ("1974 年，有个特技演员骑着火箭摩托试过。降落伞提前打开，他飘进了峡谷底。", "In 1974 a stuntman tried it on a rocket bike. His parachute opened early, and he drifted into the canyon."),
 ("要是小 R 真飞过去了，我们再做一期。", "If R actually makes it, we'll make another episode."),
 ("友情提示：吸力、一秒破百、六百升是特斯拉的说法；八万牛推力来自媒体报道；能装多少空气、能飞几秒、要多少电，是我们按常见数值做的估算。",
  "Note: the suction, the one-second sprint and 600 liters are Tesla's claims; 80 kN is from press reports; air mass, airtime and energy are our own estimates."),
]
EXTRA = {  # added 2026-10-16 to reach ~8 minutes (keys sit between the original sentences)
 34.1: ("还有一个看不见的敌人：冷。", "There's also an invisible enemy: cold."),
 34.2: ("气体一膨胀就会变冷。你按住喷雾罐不放，罐子会越来越冰手，就是这个道理。", "Expanding gas gets cold. Hold down a spray can and it turns icy. Same thing."),
 34.3: ("罐子一冷，压力掉得更快，喷口还可能结霜。所以真实的飞行时间，只会比我们算的更短。", "A colder tank loses pressure even faster, and nozzles can frost up. So real airtime would be even shorter than our estimate."),
 39.1: ("不过，跳得有派头，也是真功夫。它在空中是怎么翻跟头的？", "Still, a stylish jump takes real skill. How does it flip in mid-air?"),
 39.2: ("秘密是：喷口不对准重心。推力偏一点，就变成让车转动的力，叫力矩。", "The secret: the jets don't point through the center of mass. Off-center thrust turns the car. That's torque."),
 39.3: ("前面喷、后面不喷，车头就抬起来；左边喷、右边不喷，车就打滚。", "Fire the front but not the back, and the nose lifts. Fire the left but not the right, and it rolls."),
 39.4: ("十个喷口一起配合，就能在空中“开”车。火箭回收落地，用的也是这一套。", "Ten jets working together let it steer in the air. Rockets that land themselves use the same trick."),
 51.1: ("还有路边的人：据报道，演示时喷气卷起的碎石沙子，能飞出几十米。", "And bystanders: reportedly, the blast threw gravel and sand tens of meters during the demo."),
 51.2: ("所以这些动作，只能在封闭场地里做。", "So these stunts belong on a closed course."),
}
KEYS = sorted(list(range(len(S))) + list(EXTRA))
ALL = {**{i: v for i, v in enumerate(S)}, **EXTRA}
S = [ALL[k] for k in KEYS]
IDX = {k: i for i, k in enumerate(KEYS)}
SEG = [z for z, _ in S]
SAY = {"1978": "一九七八", "1974": "一九七四", "2028": "二零二八", "2017": "二零一七", "SpaceX": "Space X", "F1": "F 一", "小 R": "小 R", " g": " G"}

# ---------------------------------------------------------------- drawing helpers for this episode
def track_inverted(at):
    return [{"t": "path", "at": at, "c": "ink", "w": 5, "d": "M160,260 L1760,260"},
            {"t": "path", "at": at, "c": "muted", "w": 3, "d": "M160,236 L1760,236"}]

def arrows_down(x0, x1, y, at, c="blue", n=5, length=90, idp=None):
    E = []
    for i in range(n):
        x = x0 + (x1 - x0) * i / max(1, n - 1)
        e = {"t": "arrow", "at": at, "pts": [[x, y], [x, y + length]], "c": c, "w": 3}
        if idp:
            e["id"] = idp
        E.append(e)
    return E

def fan(cx, cy, r, at, idp):
    return [{"t": "ellipse", "at": at, "x": cx - r, "y": cy - r, "w": 2 * r, "h": 2 * r, "c": "ink"},
            {"t": "path", "at": at, "id": idp, "c": "blue", "w": 4,
             "d": f"M{cx},{cy} Q{cx + r * .5},{cy - r * .9} {cx},{cy - r * .9} M{cx},{cy} Q{cx + r * .9},{cy + r * .4} {cx + r * .8},{cy + r * .45} "
                  f"M{cx},{cy} Q{cx - r * .9},{cy + r * .5} {cx - r * .8},{cy + r * .4}"},
            {"t": "move", "at": at, "kind": "spin", "targets": [idp], "pivot": [cx, cy], "rpm": 160}]

def bathtub(x, y, at):
    return [{"t": "path", "at": at, "c": "ink", "w": 4, "d": f"M{x},{y} L{x + 260},{y} Q{x + 250},{y + 120} {x + 200},{y + 120} L{x + 60},{y + 120} Q{x + 10},{y + 120} {x},{y} Z"},
            {"t": "line", "at": at, "pts": [[x + 20, y + 30], [x + 240, y + 30]], "c": "blue", "w": 3}]

def tank(x, y, w, h, at, level, idp=None, c="gold"):
    E = [{"t": "rect", "at": at, "x": x, "y": y, "w": w, "h": h, "c": "ink"},
         {"t": "rect", "at": at, "x": x + 8, "y": y + h - (h - 16) * level - 8, "w": w - 16, "h": (h - 16) * level, "c": c, "fill": c}]
    if idp:
        E[1]["id"] = idp
    return E

def heli(cx, cy, at, idp="heli"):
    return [{"t": "ellipse", "at": at, "id": idp, "x": cx - 110, "y": cy - 60, "w": 220, "h": 120, "c": "ink"},
            {"t": "path", "at": at, "id": idp, "c": "ink", "w": 4, "d": f"M{cx + 110},{cy - 10} L{cx + 300},{cy - 30} L{cx + 320},{cy - 70}"},
            {"t": "line", "at": at, "id": idp, "pts": [[cx, cy - 60], [cx, cy - 100]], "c": "ink", "w": 4},
            {"t": "line", "at": at, "id": idp + "_rotor", "pts": [[cx - 330, cy - 104], [cx + 330, cy - 104]], "c": "blue", "w": 5},
            {"t": "move", "at": at, "kind": "wiggle", "targets": [idp + "_rotor"], "pivot": [cx, cy - 104], "amp": 6, "hz": 6},
            {"t": "path", "at": at, "id": idp, "c": "ink", "w": 3, "d": f"M{cx - 80},{cy + 60} L{cx - 90},{cy + 90} L{cx + 90},{cy + 90} L{cx + 80},{cy + 60}"}]

def score(x, y, at, text, c="green"):
    return [{"t": "rect", "at": at, "x": x - 230, "y": y - 70, "w": 460, "h": 110, "c": c},
            txt(x, y + 6, 48, text, at, c=c)]

B = []
# 0-2 · 倒挂轨道；翻身落地；飞过五辆车
els = track_inverted(0) + car(960, 248, 1.0, 0, idp="r0", mood="o", moves=False)
els[-1:] = els[-1:]
els += [{"t": "move", "at": 0, "kind": "rotate", "targets": ["r0*"], "pivot": [960, 254], "to": 180, "dur": 0.01},
        txt(960, 120, 44, "倒挂的轨道", 0, c="muted"),
        {"t": "move", "at": 0, "kind": "shift", "targets": ["r0*"], "dx": 500, "dy": 0, "dur": 3.0, "delay": 0.8}]
for i in range(5):
    x = 330 + i * 300
    els += [{"t": "rect", "at": 2, "x": x - 110, "y": 880, "w": 220, "h": 70, "c": "muted"},
            {"t": "ellipse", "at": 2, "x": x - 90, "y": 935, "w": 40, "h": 40, "c": "muted"}, {"t": "ellipse", "at": 2, "x": x + 50, "y": 935, "w": 40, "h": 40, "c": "muted"}]
els += [{"t": "path", "at": 2, "c": "red", "w": 4, "d": "M160,860 Q960,380 1780,860"},
        txt(960, 560, 56, "“飞”过五辆车", 2, c="red")]
B.append(els)
# 3-5 · 马斯克说能上路；真飞还是跳？算账
els = bubble(220, 220, 620, 140, 3, "这就是将来真正上路的车。", s=44)
els += stick(330, 760, 1.4, 3)
els += [txt(1360, 330, 60, "真飞？", 4, c="blue"), txt(1360, 450, 60, "还是跳得很有派头？", 4, c="red"),
        txt(1360, 660, 52, "不站队，算账。", 5, c="green"),
        {"t": "rect", "at": 5, "x": 1150, "y": 720, "w": 420, "h": 240, "c": "ink"},
        txt(1360, 800, 40, "F = m a", 5, font="en"), txt(1360, 870, 40, "8 分钟", 5, c="muted")]
B.append(els)
# 6 · 小 R 登场
els = car(960, 700, 1.8, 6, idp="r1", mood="worried")
els += car_drive(960, 700, 1.8, 6, idp="r1")
els += [txt(960, 240, 72, "小 R", 6, c="red"), txt(960, 320, 40, "有点紧张的跑车", 6, c="muted"),
        {"t": "path", "at": 6, "id": "sweat", "c": "blue", "w": 3, "d": "M1330,420 Q1350,460 1330,470 Q1310,460 1330,420"}]
B.append(els)
# 7-10 · 风扇把车底空气抽走；上下压差
els = [txt(960, 170, 60, "黑科技一：倒着开，为什么掉不下来？", 7, c="red")]
els += car(700, 640, 1.6, 8, idp="r2", moves=False)
els += fan(630, 676, 26, 8, "f1") + fan(770, 676, 26, 8, "f2")
els += [{"t": "arrow", "at": 8, "pts": [[700, 700], [700, 840]], "c": "blue", "w": 4}, txt(700, 900, 36, "抽走车底的空气", 8, c="blue")]
els += arrows_down(380, 1020, 300, 9, c="red", n=6, length=110, idp="press")
els += [txt(1480, 380, 48, "上面：整个大气压着", 9, c="red"), txt(1480, 700, 48, "下面：空气变稀", 9, c="blue"),
        txt(1480, 860, 52, "差出来的力 = 下压力", 9, c="green"),
        {"t": "move", "at": 9, "kind": "pulse", "targets": ["press"]}]
B.append(els)
# 11-12 · 1978 吸尘器赛车
els = [txt(560, 200, 56, "1978 · F1 风扇车", 11, c="ink")]
els += car(560, 640, 1.3, 11, idp="f78", moves=False)
els += fan(250, 540, 60, 11, "f3")
els += [txt(560, 820, 40, "只比了一场——赢了", 11, c="green"),
        txt(1400, 300, 56, "然后被叫停", 12, c="red")]
els += bubble(1140, 420, 520, 130, 12, "这是吸尘器！", s=48, c="red")
els += [{"t": "ellipse", "at": 12, "id": "stones", "x": 130 + i * 30, "y": 600 + (i % 3) * 30, "w": 14, "h": 14, "c": "muted", "fill": "muted"} for i in range(5)]
els += [{"t": "move", "at": 12, "kind": "shift", "targets": ["stones"], "dx": -90, "dy": 20, "dur": 0.8}]
B.append(els)
# 13-17 · 机翼要速度，风扇不用；吸力 > 车重；4700 公斤？
els = [txt(500, 220, 48, "机翼：要速度", 13, c="muted"),
       {"t": "path", "at": 13, "c": "muted", "w": 4, "d": "M300,380 Q500,320 700,380 Q500,360 300,380 Z"},
       txt(500, 470, 40, "车停着 → 0", 13, c="muted"),
       txt(1400, 220, 48, "风扇：停着也行", 13, c="green")]
els += fan(1400, 380, 70, 13, "f4")
els += [txt(1400, 520, 40, "车停着 → 照样吸", 13, c="green"),
        txt(960, 680, 60, "吸力 > 车重  →  天花板 = 地板", 14, c="blue"),
        txt(560, 860, 56, "≈ 4700 kg ?", 15, c="red"), txt(560, 930, 32, "（特斯拉屏幕上的数字）", 15, c="muted"),
        txt(1360, 860, 40, "另一辆风扇车：约 1 吨重，号称 2 吨吸力", 16, c="muted"),
        txt(1360, 930, 34, "媒体：4700 可能有水分", 16, c="red")]
B.append(els)
# 17 · 打分
els = car(960, 640, 1.5, 17, idp="r3", mood="happy") + score(960, 300, 17, "黑科技一：真本事", "green")
B.append(els)
# 18-21 · 1 秒破百 = 2.7 g；轮胎只有 1 个多 g
els = [txt(960, 190, 60, "黑科技二：1 秒破百", 18, c="red"),
       txt(560, 400, 52, "0 → 96 km/h，用时 1 秒", 19), txt(560, 500, 52, "= 每秒提速 27 m/s", 19),
       txt(560, 620, 80, "≈ 2.7 g", 19, c="red"),
       {"t": "rect", "at": 20, "x": 1180, "y": 340, "w": 440, "h": 220, "c": "ink"}]
els += [{"t": "line", "at": 20, "pts": [[1200 + 40 * i, 560], [1220 + 40 * i, 520]], "c": "ink", "w": 3} for i in range(10)]
els += [txt(1400, 450, 40, "轮胎抓地", 20), txt(1400, 640, 52, "最多 1 个多 g", 20, c="blue"),
        txt(960, 880, 56, "怎么办？两招。", 21, c="gold")]
B.append(els)
# 22-26 · 风扇按住；向后喷气 = 火箭；8 万牛 = 4 g；打问号
els = car(520, 560, 1.4, 22, idp="r4", moves=False) + arrows_down(330, 710, 240, 22, c="red", n=4, length=110)
els += [txt(520, 820, 40, "第一招：按得越紧，抓得越牢", 22, c="blue")]
els += car(1400, 560, 1.4, 23, idp="r5", jets="back")
els += car_drive(1400, 560, 1.4, 23, idp="r5", rpm=200)
els += [txt(1400, 820, 40, "第二招：干脆向后喷气", 23, c="red"),
        txt(1400, 900, 36, "往后扔东西，自己往前走 = 火箭", 24, c="muted"),
        txt(960, 180, 52, "约 80,000 N ÷ 2,000 kg ≈ 4 g", 25, c="gold"),
        {"t": "icon", "at": 26, "id": "q1", "name": "question", "x": 1780, "y": 300, "size": 180, "c": "red"},
        txt(1600, 300, 34, "还没有独立测量", 26, c="red", align="right"),
        {"t": "move", "at": 26, "kind": "pulse", "targets": ["q1"]}]
B.append(els)
# 27-29 · 能飞多久？600 升 = 三个浴缸
els = [txt(960, 180, 64, "黑科技三：到底能飞多久？", 27, c="red")]
els += car(560, 620, 1.3, 28, idp="r6", jets="down")
els += [txt(560, 820, 40, "喷的是压缩空气，不是火", 28, c="blue"), txt(560, 890, 36, "10 个喷口 · 600 升", 28, c="muted")]
els += bathtub(1100, 380, 29) + bathtub(1400, 380, 29) + bathtub(1250, 560, 29)
els += [txt(1400, 780, 48, "600 升 ≈ 3 个浴缸", 29, c="gold")]
B.append(els)
# 30-32 · 两三百公斤空气；每秒一百多公斤；一两秒
els = tank(260, 300, 200, 480, 30, 1.0, idp="air1")
els += [txt(360, 860, 40, "约 200–300 kg 空气", 30, c="gold"), txt(360, 920, 30, "（按常见高压罐估算）", 30, c="muted"),
        txt(1200, 320, 48, "冷空气喷速：每秒几百米", 31),
        txt(1200, 440, 52, "8 万牛 → 每秒喷掉 100+ kg", 31, c="red"),
        txt(1200, 640, 64, "全力：一两秒", 32, c="red"),
        {"t": "move", "at": 32, "kind": "shift", "targets": ["air1"], "dx": 0, "dy": 440, "dur": 2.0}]
B.append(els)
# 33-34 · 悬停：2 万牛，每秒 30 多公斤；越喷越托不住
els = car(560, 640, 1.3, 33, idp="r7", jets="down")
els += [{"t": "move", "at": 33, "kind": "shift", "targets": ["r7*"], "dx": 0, "dy": -160, "dur": 1.2},
        txt(560, 900, 40, "悬停：托住 2 吨 = 2 万牛", 33, c="blue"),
        txt(1360, 360, 48, "每秒吃掉 30+ kg 空气", 33, c="red")]
els += tank(1240, 460, 160, 380, 34, 0.9, idp="air2")
els += [{"t": "move", "at": 34, "kind": "shift", "targets": ["air2"], "dx": 0, "dy": 300, "dur": 3.0},
        txt(1600, 600, 40, "压力↓ 推力↓", 34, c="red", align="left"),
        {"t": "move", "at": 34, "kind": "shift", "targets": ["r7*"], "dx": 0, "dy": 160, "dur": 1.6, "delay": 2.6}]
B.append(els)
# 35-38 · 虚拟实验录屏
els = [txt(960, 150, 52, "虚拟实验：冷气推进能飞多久？", 35, c="blue"),
       {"t": "media", "at": 35, "src": "video:" + str(here / "_lab.mp4"), "x": 210, "y": 210, "w": 1500, "h": 703, "play": 20},
       txt(960, 1000, 34, "网页版里可以自己调", 35, c="muted")]
B.append(els)
# 39 · 结论：很贵的跳
els = car(960, 640, 1.6, 39, idp="r8", mood="o", jets="down")
els += [{"t": "move", "at": 39, "kind": "shift", "targets": ["r8*"], "dx": 0, "dy": -120, "dur": 0.5},
        {"t": "move", "at": 39, "kind": "shift", "targets": ["r8*"], "dx": 0, "dy": 120, "dur": 0.5, "delay": 1.4},
        txt(960, 260, 72, "不是“飞”，是很贵的“跳”", 39, c="red")]
B.append(els)
# 40-44 · 直升机 vs 喷口：动量与能量；30 倍；螺旋桨
els = heli(480, 420, 40) + car(1440, 520, 1.0, 40, idp="r9", jets="down")
els += [txt(480, 640, 40, "直升机：一小时", 40, c="green"), txt(1440, 640, 40, "喷口：几秒", 40, c="red"),
        txt(960, 780, 46, "推力 = 空气 × 速度", 41, c="blue"),
        txt(960, 860, 46, "力气 = 空气 × 速度²", 41, c="red"),
        txt(960, 960, 38, "少量空气喷得快：费力 · 大量空气推得慢：省力", 42, c="muted")]
B.append(els)
els = [txt(560, 300, 52, "托起同样 2 吨", 43),
       {"t": "rect", "at": 43, "x": 300, "y": 400, "w": 120, "h": 30, "c": "green", "fill": "green"},
       txt(560, 425, 36, "10 米旋翼", 43, c="green", align="left"),
       {"t": "rect", "at": 43, "x": 300, "y": 480, "w": 1200, "h": 30, "c": "red", "fill": "red"},
       txt(300, 570, 36, "小喷口：约 30 倍功率", 43, c="red", align="left"),
       txt(960, 760, 44, "真正的飞行汽车：都长着螺旋桨", 44, c="blue")]
for i, x in enumerate((760, 960, 1160)):
    els += [{"t": "line", "at": 44, "id": f"pr{i}", "pts": [[x - 60, 860], [x + 60, 860]], "c": "blue", "w": 5},
            {"t": "move", "at": 44, "kind": "wiggle", "targets": [f"pr{i}"], "pivot": [x, 860], "amp": 10, "hz": 6}]
B.append(els)
# 45 · 打分
els = car(960, 680, 1.5, 45, idp="r10", mood="worried") + score(960, 300, 45, "黑科技三：物理没错，是表演", "gold")
B.append(els)
# 46-48 · 坐在里面：4 g；头朝下；抗荷服
els = car(560, 620, 1.4, 46, idp="r11", mood="o", moves=False)
els += stick(600, 520, 0.45, 46, idp="driver")
els += [txt(1360, 300, 56, "起步：约 4 g", 47, c="red"), txt(1360, 380, 36, "比过山车最猛的一下还猛", 47, c="muted"),
        {"t": "move", "at": 48, "kind": "rotate", "targets": ["r11*", "driver"], "pivot": [560, 520], "to": 180, "dur": 1.0},
        txt(1360, 600, 48, "头朝下：血往头上冲", 48, c="red"), txt(1360, 690, 40, "要穿抗荷服吗？", 48, c="blue")]
B.append(els)
# 49-51 · 高压气罐；SpaceX；充一次气 20+ 度电
els = car(560, 640, 1.6, 49, idp="r12", moves=False)
els += [{"t": "ellipse", "at": 49, "x": 300 + i * 90, "y": 500, "w": 80, "h": 50, "c": "gold", "fill": "gold"} for i in range(6)]
els += [txt(560, 860, 40, "每个空隙：碳纤维高压气罐", 49, c="gold"),
        txt(1400, 300, 40, "又轻又结实……", 50), txt(1400, 370, 40, "SpaceX 几次出事和它有关", 50, c="red"),
        txt(1400, 560, 44, "充满 600 升：", 51), txt(1400, 650, 60, "20+ 度电", 51, c="gold"),
        txt(1400, 730, 36, "≈ 这辆车跑 100+ km（理想估算）", 51, c="muted")]
B.append(els)
# 52-53 · 原话
els = bubble(260, 300, 1400, 160, 52, "“安全不是主要目标。”", s=56, c="ink")
els += bubble(260, 560, 1400, 160, 52, "“争取不害死任何人。”", s=56, c="ink")
els += [txt(960, 940, 40, "（原话，不加评论）", 53, c="muted")]
B.append(els)
# 54-57 · 到底是什么：三项打分
els = [txt(960, 180, 60, "那这辆车，到底是什么？", 54),
       {"t": "icon", "at": 55, "name": "check", "x": 360, "y": 380, "size": 120, "c": "green"}, txt(460, 400, 44, "吸地：真本事（七十年代就有）", 55, align="left"),
       {"t": "icon", "at": 56, "name": "question", "x": 360, "y": 560, "size": 110, "c": "gold"}, txt(460, 580, 44, "1 秒破百：说得通，等独立测量", 56, align="left"),
       {"t": "line", "at": 57, "pts": [[310, 700], [410, 790]], "c": "red", "w": 6}, {"t": "line", "at": 57, "pts": [[410, 700], [310, 790]], "c": "red", "w": 6},
       txt(460, 760, 44, "飞：几秒钟的表演", 57, align="left"), txt(460, 840, 34, "别指望它带你上班", 57, c="muted", align="left")]
B.append(els)
# 58 · 时间表
els = [{"t": "line", "at": 58, "pts": [[200, 560], [1720, 560]], "c": "ink", "w": 4}]
for i, (y, lab, c) in enumerate(((2017, "发布", "ink"), (2020, "推迟", "red"), (2021, "推迟", "red"), (2023, "推迟", "red"), (2024, "推迟", "red"),
                                 (2026, "再发布", "blue"), (2028, "量产？", "gold"))):
    x = 260 + i * 235
    els += [{"t": "ellipse", "at": 58, "x": x - 12, "y": 548, "w": 24, "h": 24, "c": c, "fill": c},
            txt(x, 520, 34, str(y), 58, c=c, font="en"), txt(x, 630, 34, lab, 58, c=c)]
B.append(els)
# 59-61 · 蛇河峡谷彩蛋
els = [{"t": "path", "at": 59, "c": "ink", "w": 4, "d": "M100,520 L620,520 L720,900 L1200,900 L1300,520 L1820,520"},
       txt(960, 980, 36, "蛇河峡谷", 59, c="muted"),
       txt(960, 200, 44, "马斯克：也许飞越蛇河峡谷", 59, c="blue"),
       txt(400, 380, 40, "1974 · 火箭摩托", 60, c="red"),
       {"t": "path", "at": 60, "id": "chute", "c": "red", "w": 4, "d": "M860,420 Q920,330 980,420 Z M870,420 L920,500 M970,420 L920,500"},
       {"t": "move", "at": 60, "kind": "shift", "targets": ["chute"], "dx": 0, "dy": 360, "dur": 3.0},
       txt(1500, 380, 40, "降落伞提前打开……", 60, c="muted")]
els += car(1560, 508, 0.8, 61, idp="r13", mood="worried")
els += [txt(1560, 300, 40, "小 R：真飞过去，再做一期", 61, c="green")]
B.append(els)
# 62 · 友情提示
els = [txt(960, 200, 56, "友情提示", 62, c="red"),
       txt(300, 360, 40, "特斯拉的说法：吸力、1 秒破百、600 升", 62, align="left"),
       txt(300, 460, 40, "媒体报道：后部推力约 8 万牛", 62, align="left", c="blue"),
       txt(300, 560, 40, "我们的估算：空气多少、飞几秒、要多少电", 62, align="left", c="gold"),
       txt(300, 700, 34, "发布会视频请看特斯拉官方 · 虚拟实验见网页版", 62, align="left", c="muted")]
els += car(1500, 900, 0.7, 62, idp="r14")
B.append(els)
# 34.1-34.3 · 冷：喷雾罐、结霜（插在悬停那张之后）
els = [txt(960, 200, 64, "看不见的敌人：冷", 34.1, c="blue"),
       {"t": "rect", "at": 34.2, "x": 380, "y": 420, "w": 160, "h": 360, "c": "ink"},
       {"t": "rect", "at": 34.2, "x": 420, "y": 370, "w": 80, "h": 50, "c": "ink"},
       {"t": "path", "at": 34.2, "id": "spray", "c": "muted", "w": 3, "d": "M520,380 L700,330 M520,390 L700,390 M520,400 L700,450"},
       {"t": "move", "at": 34.2, "kind": "pulse", "targets": ["spray"]},
       txt(460, 860, 40, "按住不放 → 冰手", 34.2, c="blue")]
for i, (x, y) in enumerate([(1100, 420), (1300, 360), (1500, 460), (1220, 560), (1420, 620)]):
    els += [{"t": "path", "at": 34.3, "id": f"snow{i}", "c": "blue", "w": 3,
             "d": f"M{x - 30},{y} L{x + 30},{y} M{x},{y - 30} L{x},{y + 30} M{x - 21},{y - 21} L{x + 21},{y + 21} M{x - 21},{y + 21} L{x + 21},{y - 21}"},
            {"t": "move", "at": 34.3, "kind": "spin", "targets": [f"snow{i}"], "pivot": [x, y], "rpm": 12}]
els += [txt(1300, 780, 44, "压力掉得更快 · 喷口结霜", 34.3, c="red"), txt(1300, 860, 40, "真实的飞行时间：更短", 34.3, c="red")]
B.insert(B.index(next(b for b in B if any(isinstance(e, dict) and e.get("text") == "压力↓ 推力↓" for e in b))) + 1, els)
# 39.1-39.4 · 翻跟头：喷口不对准重心 = 力矩；火箭回收
els = [txt(960, 180, 56, "它在空中怎么翻跟头？", 39.1, c="blue")]
els += car(620, 560, 1.4, 39.2, idp="rf", moves=False)
els += [{"t": "ellipse", "at": 39.2, "x": 610, "y": 470, "w": 22, "h": 22, "c": "red", "fill": "red"}, txt(650, 450, 32, "重心", 39.2, c="red", align="left"),
        {"t": "arrow", "at": 39.2, "pts": [[870, 720], [870, 560]], "c": "blue", "w": 6}, txt(900, 700, 34, "推力偏一点", 39.2, c="blue", align="left"),
        {"t": "path", "at": 39.2, "c": "gold", "w": 5, "d": "M440,340 Q620,250 800,340"}, {"t": "arrow", "at": 39.2, "pts": [[780, 330], [810, 352]], "c": "gold", "w": 5},
        txt(620, 250, 44, "= 力矩，车就转", 39.2, c="gold"),
        {"t": "move", "at": 39.3, "kind": "rotate", "targets": ["rf*"], "pivot": [620, 480], "to": -25, "dur": 0.8},
        txt(1460, 420, 40, "前喷后不喷：抬头", 39.3), txt(1460, 500, 40, "左喷右不喷：打滚", 39.3),
        {"t": "path", "at": 39.4, "c": "ink", "w": 4, "d": "M1440,860 L1440,620 L1470,580 L1500,620 L1500,860 Z M1430,860 L1400,900 M1510,860 L1540,900"},
        {"t": "path", "at": 39.4, "id": "flame", "c": "red", "w": 3, "d": "M1450,870 L1470,940 L1490,870"},
        {"t": "move", "at": 39.4, "kind": "pulse", "targets": ["flame"]},
        txt(1700, 760, 36, "火箭回收", 39.4, c="muted"), txt(1700, 810, 36, "也是这一套", 39.4, c="muted")]
B.insert(B.index(next(b for b in B if any(isinstance(e, dict) and e.get("text") == "不是“飞”，是很贵的“跳”" for e in b))) + 1, els)
# 51.1-51.2 · 碎石乱飞；封闭场地
els = car(560, 640, 1.3, 51.1, idp="rd", jets="down")
els += [{"t": "ellipse", "at": 51.1, "id": "debris", "x": 860 + 40 * i, "y": 620 + (i % 3) * 25, "w": 14, "h": 14, "c": "muted", "fill": "muted"} for i in range(8)]
els += [{"t": "move", "at": 51.1, "kind": "shift", "targets": ["debris"], "dx": 520, "dy": -60, "dur": 1.6}]
els += stick(1600, 760, 1.0, 51.1, idp="bystander", arms="up")
els += [txt(1300, 300, 44, "碎石沙子：几十米", 51.1, c="red"),
        {"t": "rect", "at": 51.2, "x": 220, "y": 860, "w": 1480, "h": 90, "c": "gold"}, txt(960, 920, 44, "只能在封闭场地里做", 51.2, c="gold")]
B.insert(B.index(next(b for b in B if any(isinstance(e, dict) and e.get("text") == "≈ 这辆车跑 100+ km（理想估算）" for e in b))) + 1, els)
for b in B:            # sentence keys → sentence numbers
    for e in b:
        if isinstance(e, dict):
            e["at"] = IDX[e["at"]]
            if isinstance(e.get("until"), (int, float)):
                e["until"] = IDX[e["until"]]
boards = [{"elements": [e for e in b if e]} for b in B]

bad = missing_chars("".join(e.get("text", "") for b in B for e in b if isinstance(e, dict)))
if bad:
    sys.exit(f"the fonts lack: {bad}")
if "--boards-only" in sys.argv:
    lesson = json.load(open(here / "lesson.json"))
    lesson["boards"] = boards
    json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
    sys.exit(print(len(boards), "boards"))

import sherpa_onnx as so  # noqa: E402
d = sys.argv[1].rstrip("/") + "/"
tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
    model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
    lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=2),
    rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1))
t, parts, segs, sr = 0.4, [], [], 24000
PAUSE = {2: 0.6, 4: 0.4, 5: 0.6, 12: 0.4, 17: 0.7, 21: 0.4, 26: 0.6, 29: 0.4, 32: 0.5, 35: 1.0, 36: 2.4, 37: 2.4, 38: 3.2, 39: 0.8,
         45: 0.7, 53: 0.6, 57: 0.5, 61: 0.6}
for i, (zh, en) in enumerate(S):
    key = KEYS[i]
    spoken = zh
    for a_, b_ in SAY.items():
        spoken = spoken.replace(a_, b_)
    a = tts.generate(speakable(spoken), sid=49, speed=1.04); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.4), np.float32))
    segs.append({"zh": zh, "en": en, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    gap = PAUSE.get(key, 0.3)
    parts += [x, np.zeros(int(sr * gap), np.float32)]; t += len(x) / sr + gap
    print(i, round(t, 1), flush=True)
parts.append(np.zeros(int(sr * 1.5), np.float32)); t += 1.5
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson({"zh": "会飞的特斯拉，到底能飞多久？", "en": "Tesla's flying Roadster: how long can it really fly?"}, segs, boards,
                       audio="配音.wav", duration=round(t, 2))
lesson["pace"], lesson["hand"], lesson["subs"] = 0.55, False, True
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
