"""《会飞的特斯拉，到底能飞多久？》第二版（约 8 分钟，快节奏）——Eddie 2026-10-16 11:07：“视频不够清晰，动画太少，节奏太慢，我喜欢节奏快，信息量大”；
11:31 看过快节奏样段后：“好，继续”，并要字幕中英合一（一个 字幕.srt）。
标准同《每日科普说明》三：pace 0.2、ink 1.7、pan 0.45、语速 1.22、句间 0.12 秒；一句一个数字或结论；每 2～3 秒有东西动或蹦出来。
事实（同第一版，出处见第一版 make.py 说明）：得州发布会、倒挂轨道、飞越五辆车、0–60 mph 约 1 秒、10 个冷气喷口、600 升压缩空气、后部推力约 80 千牛
（Electrek）、屏幕上约 4700 公斤下压力、碳纤维缠绕高压气罐、马斯克原话、2028 量产、2017 年起多次推迟、蛇河峡谷；1978 年 Brabham BT46B；
1974 年 Evel Knievel。估算（片中说是估算）：大气压 ≈ 每平方米 10 吨；车底 8 平方米、低 5% ≈ 4 吨；气罐空气量；喷气、悬停时间；
悬停功率（喷口 F·v/2 ≈ 6.5 MW，十米旋翼理想 ≈ 0.2 MW，每秒约一吨空气）；充气电量（等温压缩 200 kg 到 300 bar ≈ 27 度）。
虚拟实验：飞行实验.html，rec_lab.py 高清录成 _lab.webm。
    python3 rec_lab.py && python3 make.py <kokoro 模型目录> [--boards-only] && WB_CRF=17 python3 ../../../tools/whiteboard/wb.py . --mp4"""
import json, sys  # noqa: E401
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[2] / "services" / "gateway"))
sys.path.insert(0, str(here.parent))
from app.production.whiteboard import ai as wai  # noqa: E402
from app.production.whiteboard.core import missing_chars  # noqa: E402
from app.production.whiteboard.speech import speakable  # noqa: E402
from popkit import car, car_drive, stick, txt  # noqa: E402

S = [  # (中文讲稿, English)
 # 0 开场
 ("这周，美国得州。一辆特斯拉跑车，头朝下，开过了一条倒挂的轨道。", "This week in Texas, a Tesla sports car drove upside down along an inverted track."),
 ("翻个身，落地，再从五辆车的头顶上，一跳而过。", "It flipped, landed, and then jumped clean over five cars."),
 ("马斯克说：这就是将来量产的那辆车，二零二八年。", "Musk says this is the actual production car, coming in 2028."),
 ("三个黑科技：吸在天花板上、一秒破百、会飞。今天不站队，我们一个一个算账。", "Three tricks: sticking to the ceiling, 0 to 60 in a second, and flying. No sides today. We do the math."),
 ("今天的主角：小 R，一辆有点紧张的跑车。", "Today's star: R, a slightly nervous sports car."),
 # 5 黑科技一：吸地
 ("黑科技一：倒着开，车重两吨，为什么掉不下来？", "Trick one: upside down, two tons of car. Why doesn't it fall?"),
 ("车底藏着几台风扇，拼命把车底的空气往外抽，车底气压变低。", "Fans hidden underneath pump air out from under the car, so the pressure there drops."),
 ("而头顶上，是整个大气层：每平方米，压着十吨。", "Above it sits the whole atmosphere: ten tons on every square meter."),
 ("车底大约八平方米，只要比外面低百分之五，就多出四吨的力，把车按住。", "The floor is about eight square meters. Just five percent lower pressure gives four tons pressing the car on."),
 ("四吨按着两吨的车：倒过来，也掉不下去。", "Four tons holding a two-ton car: even upside down, it stays put."),
 ("特斯拉屏幕上写的更猛：四千七百公斤，车重的两倍多。", "Tesla's screen claimed even more: 4,700 kg, over twice the car's weight."),
 ("科技媒体说，这个数可能有水分。不过我们算的四吨，已经够用。", "Tech press suspect that's inflated. But our four tons is already enough."),
 ("这招一点不新：一九七八年，F1 赛车 BT46B，屁股上装了个大风扇。", "And it isn't new: in 1978 the F1 car BT46B had a giant fan on its back."),
 ("只比了一场，赢了。然后就被叫停：对手说它是吸尘器，还往后喷石子。", "It raced once and won. Then it was pulled: rivals called it a vacuum cleaner that sprayed stones."),
 ("风扇最狠的地方：机翼要靠速度才有下压力，风扇停着就有。", "Here's the killer feature: wings need speed for downforce. Fans work standing still."),
 ("机翼的下压力跟速度的平方走：速度减半，只剩四分之一。", "Wing downforce goes with speed squared: half the speed, a quarter of the force."),
 ("黑科技一，打分：真本事。", "Trick one gets a score: the real thing."),
 # 17 黑科技二：一秒破百
 ("黑科技二：零到六十英里，也就是九十六公里，一秒。", "Trick two: 0 to 60 miles an hour, that's 96 km/h, in one second."),
 ("一秒钟加到每秒二十七米：加速度，二点七个 g。", "Reaching 27 meters per second in one second: that's 2.7 g."),
 ("可车是靠轮胎抓地往前推的。最好的轮胎，也就一点几个 g。", "But a car pushes through its tires, and the best tires manage only 1-point-something g."),
 ("第一招：风扇把车压紧。压得越紧，轮胎抓得越牢。", "Fix one: the fans press the car down. The harder the press, the better the grip."),
 ("第二招更狠：干脆不靠地面，车尾向后喷气，就像火箭。", "Fix two, more brutal: forget the road. Blast gas out the back, like a rocket."),
 ("据报道，后面四个喷口，推力约八万牛。", "Reportedly, the four rear jets make about 80,000 newtons."),
 ("八万牛除以两吨，每秒提速四十米：四个 g。光靠喷气就够了。", "80,000 newtons over two tons is 40 meters per second squared: 4 g. The jets alone are enough."),
 ("不过，还没有独立测量。这个“一秒”，先打个问号。", "No independent test yet, though. That 'one second' gets a question mark."),
 # 25 黑科技三：能飞多久（快节奏样段）
 ("黑科技三，重头戏：它到底能飞多久？官方只给了两个数：十个喷口，六百升压缩空气。", "Trick three, the main event: how long can it fly? Tesla gave two numbers: ten jets, 600 liters of compressed air."),
 ("六百升，就是三个浴缸。压到三百个大气压，大约装两百公斤空气；压到七百，也就三百多公斤。", "600 liters is three bathtubs. At 300 atmospheres that's about 200 kg of air; at 700, just over 300."),
 ("冷空气喷出去，每秒最多六七百米。推力八万牛，除一下：每秒要喷掉一百三十公斤。", "Cold air leaves at 600 to 700 meters per second at most. 80 kN divided by that: 130 kg every second."),
 ("两百公斤，每秒一百三，一秒半见底。而且压力一掉，推力跟着掉。", "200 kg at 130 per second: empty in a second and a half. And as pressure drops, so does thrust."),
 ("只悬停呢？两吨的车要两万牛，每秒三十多公斤：五到十秒，就得落地。", "Just hovering? Two tons needs 20 kN, over 30 kg a second: down again in five to ten seconds."),
 ("不信？我们做了一个虚拟实验，你可以自己调。", "Don't believe us? We built a virtual lab. Try it yourself."),
 ("三百个大气压，悬停三米：五秒左右。", "300 atmospheres, hover at three meters: about five seconds."),
 ("压到七百个大气压：十秒左右。", "Squeeze it to 700: about ten seconds."),
 ("再把车减掉五百公斤：也就十二秒多。", "Then cut 500 kg off the car: just over twelve."),
 ("还有隐藏减益：气体一膨胀就降温，罐子越喷越冷，压力掉得更快，喷口还会结霜。", "Hidden penalty: expanding gas cools, the tank gets colder, pressure falls faster, and nozzles frost."),
 ("结论：这不是飞，是用两百公斤空气，换来的一次很贵的跳。", "Verdict: it doesn't fly. It trades 200 kg of air for one very expensive jump."),
 # 36 翻跟头
 ("不过，跳得有派头，也是真功夫：它在空中怎么翻跟头？", "Still, a stylish jump takes skill. How does it flip in mid-air?"),
 ("秘密是：喷口不对准重心。推力偏一点，就变成让车转动的力，叫力矩。", "The secret: the jets don't point through the center of mass. Off-center thrust turns the car. That's torque."),
 ("前面喷、后面不喷，车头抬起来；左边喷、右边不喷，车就打滚。", "Fire the front but not the back, and the nose lifts. Fire the left but not the right, and it rolls."),
 ("十个喷口一起配合，就能在空中“开”车。火箭回收落地，用的也是这一招。", "Ten jets together let it steer in the air. Rockets that land themselves use the same trick."),
 # 40 烧脑：喷口 vs 旋翼
 ("再烧一点脑：同样托起两吨，直升机能在天上待一个小时，喷口为什么只能撑几秒？", "A brain-burner: a helicopter holds up two tons for an hour. Why do jets last only seconds?"),
 ("推力，是每秒喷出的空气乘速度；花的力气，却是空气乘速度的平方，再除以二。", "Thrust is air per second times speed. But the energy you spend is air times speed squared, over two."),
 ("速度翻一倍，推力翻一倍，力气翻四倍。所以想省力：多推空气，推得慢一点。", "Double the speed: double the thrust, four times the energy. So to save energy, push more air, more slowly."),
 ("喷口：每秒三十公斤空气，六百多米每秒，功率六千多千瓦。", "Jets: 30 kg of air a second at over 600 m/s. That's over 6,000 kilowatts."),
 ("十米的旋翼：每秒推一吨空气，只要二十米每秒，约两百千瓦。", "A ten-meter rotor: a ton of air a second at just 20 m/s. About 200 kilowatts."),
 ("差了三十倍。所以真正在做飞行汽车的公司，造出来的都长着螺旋桨。", "Thirty times apart. That's why companies building real flying cars all use propellers."),
 ("黑科技三，打分：物理没错，但它是表演，不是交通工具。", "Trick three gets a score: right physics, but a stunt, not transportation."),
 # 47 坐在里面
 ("好，假设你就坐在里面。起步四个 g，跟过山车最猛的那一下差不多。", "Now imagine you're inside. Launching at 4 g is like the wildest moment on a roller coaster."),
 ("翻跟头时头朝下，血往脑袋里冲。科技媒体都在问：要不要穿战斗机飞行员的抗荷服？", "Upside down, blood rushes to your head. Tech press ask: will you need a fighter pilot's g-suit?"),
 ("车里每个空隙，都塞满了碳纤维缠绕的高压气罐，压力是轮胎的上百倍。", "Every gap inside is packed with carbon-fiber-wrapped tanks, at over a hundred times tire pressure."),
 ("这种罐子又轻又结实，但 SpaceX 几次火箭出事，都和这类罐子有关。", "They're light and strong, but this type of tank has been linked to SpaceX rocket failures."),
 ("还有路边的人：据报道，演示时喷气卷起的碎石沙子，能飞出几十米。", "And bystanders: reportedly the blast threw gravel and sand tens of meters during the demo."),
 ("再算一笔账：把气罐充满，最理想也要二十多度电，够这辆车跑一百多公里。", "One more sum: filling the tanks takes, ideally, over 20 kWh. That would drive this car over 100 km."),
 ("马斯克自己说：安全不是主要目标；他们会“争取不害死任何人”。", "Musk himself said safety is not the main goal, and they will 'aspire not to kill anyone'."),
 ("这是原话，我们不加评论。", "Those are his words. No comment from us."),
 # 55 打分表
 ("好，打分表。", "OK, the scorecard."),
 ("吸地：真本事，一九七八年就有，现在做得更猛。", "Suction: real, around since 1978, now turned up."),
 ("一秒破百：物理上说得通，等独立测量。", "One-second sprint: physically plausible, awaiting independent tests."),
 ("飞：几秒钟的表演。很酷，但别指望它带你上班。", "Flying: a few seconds of show. Cool, but it won't fly you to work."),
 ("时间表：二零一七年就发布过，推迟了一次又一次，现在说二零二八年量产。", "Timeline: first unveiled in 2017, delayed again and again, now promised for 2028."),
 ("最后一个彩蛋：马斯克说，也许会开着它飞越蛇河峡谷。", "One last easter egg: Musk said it might jump the Snake River Canyon."),
 ("一九七四年，有个特技演员骑着火箭摩托试过：降落伞提前打开，他飘进了峡谷底。", "In 1974 a stuntman tried it on a rocket bike. His parachute opened early and he drifted into the canyon."),
 ("要是小 R 真飞过去了，我们再做一期。", "If R actually makes it, we'll make another episode."),
 ("友情提示：吸力、一秒破百、六百升是特斯拉的说法；八万牛来自媒体报道；空气量、飞行时间、功率和电量，是我们按常见数值做的估算。",
  "Note: the suction, the one-second sprint and 600 liters are Tesla's claims; 80 kN is from press reports; air mass, airtime, power and energy are our estimates."),
]
EXTRA = {  # 2026-10-16 加密到 8 分钟：插在原句之间（键是小数），估算都在片中说明
 1.1: ("先算个小账：五辆车排起来大约二十五米。斜着起跳，每秒十六米就够，相当于时速五十多公里。", "Quick math: five cars in a row are about 25 meters. Launch at an angle and 16 m/s is enough, about 56 km/h."),
 1.2: ("在空中只待两秒多。这一跳难的不是距离，是落地别把车摔坏。", "That's just over two seconds in the air. The hard part isn't the distance. It's landing without wrecking the car."),
 2.1: ("其实这辆车二零一七年就发布过，当时承诺：一点九秒破百，续航一千公里。", "This car was first unveiled in 2017, promising 0 to 60 in 1.9 seconds and 1,000 km of range."),
 2.2: ("二零一八年马斯克又说，要给它加个 SpaceX 套件：车身一圈小喷口。今天，喷口真的来了。", "In 2018 Musk promised a SpaceX package: small thrusters around the body. Today, the thrusters showed up."),
 9.1: ("反过来说：风扇一停，四吨变零。倒挂开车的时候，风扇比轮子还要命。", "Flip side: if the fans stop, four tons becomes zero. Upside down, the fans matter more than the wheels."),
 13.1: ("后来，F1 干脆禁了风扇车，一禁就是四十多年。", "F1 later banned fan cars outright, and the ban has lasted over forty years."),
 15.1: ("所以风扇车在弯道最占便宜：车速一慢，机翼没劲了，风扇照样吸。", "So fan cars shine in corners: when speed drops, wings go weak, but fans keep sucking."),
 18.1: ("这一秒，只跑了十三米多，差不多三辆车那么长。", "In that one second it covers just over 13 meters, about three car lengths."),
 18.2: ("对比一下：现在最快的量产电车，零到六十英里大约一点七秒；F1 赛车两秒半左右。", "For comparison: the fastest production EV does 0 to 60 in about 1.7 seconds; an F1 car in about 2.5."),
 23.1: ("但喷气只够喷一两秒，所以它是专门给起步那一下准备的。", "But the jets only last a second or two, so they're made for that one launch."),
 29.1: ("那为什么不喷火？火箭燃料喷速每秒三千米，是冷空气的五倍：同样的推力，只要五分之一的料。", "Why not use fire? Rocket exhaust leaves at 3,000 m/s, five times faster than cold air: same thrust, a fifth of the propellant."),
 29.2: ("可车上烧火箭燃料，路边的人就不是被石子砸，是被烤了。所以只能喷冷气。", "But burn rocket fuel on a car, and bystanders don't get pelted with gravel. They get roasted. So: cold air."),
 29.3: ("冷气推进其实很常见：卫星在太空里调姿态，喷的就是冷气。", "Cold-gas thrusters are actually common: satellites use them to adjust their attitude in space."),
 33.1: ("注意：车减掉四分之一，时间只多了两秒多。瓶颈是罐子，不是车重。", "Notice: cut a quarter of the weight and you gain only two seconds. The bottleneck is the tank, not the car."),
 37.1: ("力矩等于推力乘距离：假如偏一米，八万牛就是八万牛米，翻一辆车绰绰有余。", "Torque is thrust times distance: off by one meter, 80,000 newtons makes 80,000 newton-meters. Plenty to flip a car."),
 45.1: ("无人机为什么都是大桨慢转？同一个道理：桨越大，越省电。", "Why do drones use big, slow propellers? Same reason: the bigger the blade, the less power."),
 47.1: ("四个 g 的时候，你七十公斤的身体，压在座椅上有两百八十公斤。", "At 4 g, your 70 kg body presses into the seat like 280 kg."),
 52.1: ("按家里的电价，一跳也就十几块钱。真正贵的，是那些罐子和风险。", "At household electricity prices, one jump costs a couple of dollars. The expensive part is the tanks and the risk."),
 59.1: ("对一下账：一点九秒变成了一秒，交车从二零二零年变成了二零二八年。", "Check the books: 1.9 seconds became 1, and delivery went from 2020 to 2028."),
 62.1: ("下期见。小 R，别紧张，你今天表现不错。", "See you next time. Relax, R. You did great today."),
}
KEYS = sorted(list(range(len(S))) + list(EXTRA))
ALL = {**dict(enumerate(S)), **EXTRA}
S = [ALL[k] for k in KEYS]
IDX = {k: i for i, k in enumerate(KEYS)}
SAY = {"2018": "二零一八", "2020": "二零二零", "1978": "一九七八", "1974": "一九七四", "2028": "二零二八", "2017": "二零一七", "SpaceX": "Space X", "F1": "F 一", "BT46B": "B T 四十六 B",
       " g": " G", "小 R": "小 R"}

# ---------------------------------------------------------------- helpers
N = [0]


def uid(p="e"):
    N[0] += 1
    return f"{p}{N[0]}z"


def pop(at, ids, delay=0.0, dur=0.35):
    return {"t": "move", "at": at, "kind": "pop", "targets": ids if isinstance(ids, list) else [ids], "dur": dur, "delay": delay}


def T(at, x, y, s, text, c="ink", d=None, **kw):
    """Text; d = when (seconds into the sentence) it pops in. None = just drawn."""
    i = uid("t")
    font = "en" if all(ord(ch) < 128 for ch in text) and any(ch.isalpha() for ch in text) else "zh"
    E = [txt(x, y, s, text, at, c=c, id=i, font=kw.pop("font", font), **kw)]
    if d is not None:
        E.append(pop(at, i, d))
    return E


def BIG(at, x, y, text, c="red", d=0.0, s=140):
    return T(at, x, y, s, text, c=c, d=d)


def P(at, d, c="ink", w=4, idp=None, **kw):
    e = {"t": "path", "at": at, "c": c, "w": w, "d": d, **kw}
    if idp:
        e["id"] = idp
    return e


def R(at, x, y, w, h, c="ink", fill=None, idp=None, sw=5):
    e = {"t": "rect", "at": at, "x": x, "y": y, "w": w, "h": h, "c": c, "sw": sw}
    if fill:
        e["fill"] = fill
    if idp:
        e["id"] = idp
    return e


def bar(at, x, base, w, h, c, d=0.0, dur=0.8):
    """A filled bar growing up from base."""
    i = uid("b")
    return [R(at, x, base - h, w, h, c=c, fill=c, idp=i),
            {"t": "move", "at": at, "kind": "grow", "targets": [i], "axis": "y", "pivot": [x + w / 2, base], "dur": dur, "delay": d}]


def arr(at, x0, y0, x1, y1, c="red", w=6, d=0.0, dur=0.5):
    """An arrow shooting out from its tail."""
    i = uid("a")
    ax = "y" if abs(x1 - x0) < abs(y1 - y0) else "x"
    return [{"t": "arrow", "at": at, "id": i, "pts": [[x0, y0], [x1, y1]], "c": c, "w": w},
            {"t": "move", "at": at, "kind": "grow", "targets": [i], "axis": ax, "pivot": [x0, y0], "dur": dur, "delay": d}]


def sh(at, ids, dx, dy, d, dur):
    return {"t": "move", "at": at, "kind": "shift", "targets": ids if isinstance(ids, list) else [ids], "dx": dx, "dy": dy, "delay": d, "dur": dur}


def rot(at, ids, to, pivot, d, dur):
    return {"t": "move", "at": at, "kind": "rotate", "targets": ids if isinstance(ids, list) else [ids], "to": to, "pivot": pivot, "delay": d, "dur": dur}


def spin(at, i, pivot, rpm=160):
    return {"t": "move", "at": at, "kind": "spin", "targets": [i], "pivot": pivot, "rpm": rpm}


def pulse(at, i, d=0.0, dur=0.6):
    return {"t": "move", "at": at, "kind": "pulse", "targets": [i], "delay": d, "dur": dur}


def fan(at, cx, cy, r):
    i = uid("fan")
    return [{"t": "ellipse", "at": at, "x": cx - r, "y": cy - r, "w": 2 * r, "h": 2 * r, "c": "ink", "sw": 5},
            P(at, f"M{cx},{cy} Q{cx + r * .5},{cy - r * .9} {cx},{cy - r * .9} M{cx},{cy} Q{cx + r * .9},{cy + r * .4} {cx + r * .8},{cy + r * .45} "
                  f"M{cx},{cy} Q{cx - r * .9},{cy + r * .5} {cx - r * .8},{cy + r * .4}", c="blue", w=5, idp=i),
            spin(at, i, [cx, cy])]


def puffs(at, x, y, dx, dy, n=6, c="blue", d=0.3, dur=2.0, r=26):
    """A row of air puffs flying off by (dx, dy)."""
    i = uid("pf")
    E = [{"t": "ellipse", "at": at, "id": i, "x": x + k * 34 * (1 if dx >= 0 else -1) * (abs(dx) > abs(dy)),
          "y": y + k * 34 * (abs(dy) >= abs(dx)) * (1 if dy >= 0 else -1) + (k % 2) * 14 * (abs(dx) > abs(dy)),
          "w": r, "h": r, "c": c, "fill": c} for k in range(n)]
    return E + [sh(at, i, dx, dy, d, dur)]


def stamp(at, x, y, text, c="green", d=0.6):
    i = uid("st")
    return [{"t": "ellipse", "at": at, "id": i, "x": x - 190, "y": y - 110, "w": 380, "h": 190, "c": c, "sw": 7},
            txt(x, y + 22, 72, text, at, c=c, id=i), pop(at, i, d, 0.45)]


def check(at, x, y, c="green", d=0.0):
    i = uid("ck")
    return [P(at, f"M{x - 40},{y} L{x - 8},{y + 34} L{x + 48},{y - 40}", c=c, w=9, idp=i), pop(at, i, d)]


def cross(at, x, y, c="red", d=0.0):
    i = uid("cx")
    return [P(at, f"M{x - 36},{y - 36} L{x + 36},{y + 36} M{x + 36},{y - 36} L{x - 36},{y + 36}", c=c, w=9, idp=i), pop(at, i, d)]


def tank(at, x, y, w, h, frac, c="gold", drain=None, d=1.0, dur=1.5):
    """A tank; the fill drains to `drain` (fraction) if given."""
    i = uid("tk")
    pad = 16
    fh = (h - 2 * pad) * frac
    E = [R(at, x, y, w, h), R(at, x + pad, y + h - pad - fh, w - 2 * pad, fh, c=c, fill=c, idp=i, sw=3)]
    if drain is not None:
        E.append({"t": "move", "at": at, "kind": "grow", "targets": [i], "axis": "y", "from": 1, "to": drain,
                  "pivot": [x + w / 2, y + h - pad], "dur": dur, "delay": d})
    return E


def cars_row(at, x0, y, n, w=150, h=80, c="muted"):
    E = []
    for k in range(n):
        x = x0 + k * (w + 20)
        E.append(P(at, f"M{x},{y} L{x},{y - h * .55} L{x + w * .25},{y - h} L{x + w * .75},{y - h} L{x + w},{y - h * .55} L{x + w},{y} Z", c=c, w=4))
    return E


def road(at, y, x0=120, x1=1800, c="ink"):
    return [{"t": "line", "at": at, "pts": [[x0, y], [x1, y]], "c": c, "w": 5}]


def axes(at, x0, y0, x1, y1, xl="", yl=""):
    E = [{"t": "line", "at": at, "pts": [[x0, y0], [x1, y0]], "c": "ink", "w": 4}, {"t": "line", "at": at, "pts": [[x0, y0], [x0, y1]], "c": "ink", "w": 4}]
    if xl:
        E += T(at, x1 - 60, y0 + 70, 44, xl, c="muted")
    if yl:
        E += T(at, x0 + 20, y1 - 30, 44, yl, c="muted", align="left")
    return E


def curve(at, d, c="red", w=7, pivot=(0, 0), delay=0.5, dur=1.4):
    i = uid("cv")
    return [P(at, d, c=c, w=w, idp=i), {"t": "move", "at": at, "kind": "grow", "targets": [i], "axis": "x", "pivot": list(pivot), "dur": dur, "delay": delay}]


def R_(at, cx, cy, k, mood="happy", jets=None, moves=True):
    """小 R with a fresh id; returns (elements, id)."""
    i = uid("car")
    return car(cx, cy, k, at, idp=i, mood=mood, jets=jets, moves=moves), i


# ---------------------------------------------------------------- boards (one per sentence: fast cuts)
B = []
a = 0
# 0 倒挂轨道：车翻过来贴着天花板开
E = [P(a, "M120,250 L1800,250", w=7), P(a, "M120,222 L1800,222", c="muted", w=3)]
els, i = R_(a, 420, 250, 1.6, mood="o", moves=False)
E += els + car_drive(420, 250, 1.6, a, idp=i, rpm=-240)
E += [rot(a, i + "*", 180, [420, 330], 0.2, 0.01), sh(a, i + "*", 1000, 0, 0.9, 3.2)]
E += arr(a, 960, 520, 960, 760, c="blue", d=2.2) + T(a, 1080, 680, 56, "重力", c="blue", d=2.2, align="left")
E += BIG(a, 960, 920, "倒着开！", c="red", d=3.4, s=110)
B.append(E)
a = 1
# 1 飞越五辆车
E = road(a, 860) + cars_row(a, 620, 860, 5)
els, i = R_(a, 330, 860, 1.0, jets="down", moves=False)
E += els + [sh(a, i + "*", 650, -360, 0.6, 1.2), sh(a, i + "*", 650, 360, 1.8, 1.2)]
E += BIG(a, 1060, 330, "× 5", c="red", d=2.6, s=130)
B.append(E)
a = 1.1
# 1.1 五辆车 25 m，抛物线，16 m/s
E = road(a, 860) + cars_row(a, 520, 860, 5)
E += [{"t": "line", "at": a, "pts": [[520, 920], [1370, 920]], "c": "muted", "w": 3}] + T(a, 945, 990, 48, "≈ 25 m", c="muted")
E += curve(a, "M400,860 Q945,140 1490,860", c="blue", w=6, pivot=(400, 860), delay=0.6, dur=1.6)
E += BIG(a, 945, 300, "16 m/s", c="red", d=2.6, s=120) + T(a, 945, 410, 52, "≈ 56 km/h", c="red", d=3.2)
B.append(E)
a = 1.2
# 1.2 空中 2 秒多；落地别摔
els, i = R_(a, 960, 440, 1.8, mood="o", moves=False)
E = els + road(a, 860, 300, 1620) + [sh(a, i + "*", 0, 420, 1.8, 0.4)]
E += BIG(a, 400, 300, "2.3 s", c="blue", d=0.2, s=120) + T(a, 400, 400, 48, "在空中", c="blue", d=0.4)
for k, (x, y) in enumerate(((780, 800), (1140, 800), (960, 760))):
    j = uid("star")
    E += [P(a, f"M{x - 30},{y} L{x + 30},{y} M{x},{y - 30} L{x},{y + 30} M{x - 20},{y - 20} L{x + 20},{y + 20} M{x - 20},{y + 20} L{x + 20},{y - 20}", c="gold", w=5, idp=j),
          pop(a, j, 2.3 + 0.15 * k)]
E += T(a, 1500, 300, 60, "难的是落地", c="red", d=2.8)
B.append(E)
a = 2
# 2 2028 量产
els, i = R_(a, 600, 800, 2.2)
E = els + car_drive(600, 800, 2.2, a, idp=i) + road(a, 800, 120, 1100)
E += T(a, 1450, 330, 64, "马斯克：", c="muted", d=0.2) + T(a, 1450, 440, 60, "就是这辆，上路", d=0.8)
E += BIG(a, 1450, 700, "2028", c="red", d=2.2, s=170) + T(a, 1450, 820, 52, "量产", c="red", d=2.6)
B.append(E)
a = 2.1
# 2.1 2017 发布：1.9 秒、1000 km
E = BIG(a, 420, 360, "2017", c="gold", d=0.0, s=150) + T(a, 420, 480, 56, "第一次发布", c="muted", d=0.4)
E += BIG(a, 1300, 360, "1.9 s", c="ink", d=1.6, s=120) + T(a, 1300, 460, 48, "零到六十英里", c="muted", d=1.8)
E += BIG(a, 1300, 700, "1,000 km", c="green", d=3.0, s=120) + T(a, 1300, 800, 48, "续航", c="muted", d=3.2)
B.append(E)
a = 2.2
# 2.2 2018 SpaceX 套件：一圈小喷口
els, i = R_(a, 960, 700, 2.4, moves=False)
E = els + BIG(a, 400, 260, "2018", c="gold", d=0.0, s=110) + T(a, 1300, 260, 64, "SpaceX 套件", c="blue", d=0.6, font="zh")
for k in range(10):
    import math
    ang = math.pi * (0.05 + 0.9 * k / 9)
    x, y = 960 - 560 * math.cos(ang), 640 - 300 * math.sin(ang) * 0.9 + 120
    j = uid("thr")
    E += [{"t": "ellipse", "at": a, "id": j, "x": x - 18, "y": y - 18, "w": 36, "h": 36, "c": "blue", "fill": "blue"}, pop(a, j, 1.4 + 0.18 * k)]
E += T(a, 960, 940, 60, "今天：真的来了", c="red", d=4.2)
B.append(E)
a = 3
# 3 三个黑科技 + 算账
E = []
for k, (lab, c) in enumerate((("吸在天花板上", "blue"), ("一秒破百", "gold"), ("会飞", "red"))):
    x = 360 + k * 600
    i = uid("n")
    E += [{"t": "ellipse", "at": a, "id": i, "x": x - 90, "y": 230, "w": 180, "h": 180, "c": c, "sw": 7},
          txt(x, 355, 110, str(k + 1), a, c=c, font="en", id=i), pop(a, i, 0.3 + 0.9 * k)]
    E += T(a, x, 520, 60, lab, c=c, d=0.5 + 0.9 * k)
E += BIG(a, 960, 820, "不站队，算账", c="ink", d=4.0, s=100)
B.append(E)
a = 4
# 4 小 R，紧张
els, i = R_(a, 760, 760, 2.6, mood="worried")
E = els + road(a, 760, 160, 1400)
E += [{"t": "move", "at": a, "kind": "wiggle", "targets": [i + "_b"], "pivot": [760, 700], "amp": 2, "hz": 9}]
E += T(a, 1500, 400, 120, "小 R", c="red", d=0.6) + T(a, 1500, 520, 52, "有点紧张", c="muted", d=1.4)
for k, (x, y) in enumerate(((1160, 430), (1210, 360), (1250, 450))):
    j = uid("sw")
    E += [P(a, f"M{x},{y} Q{x - 14},{y + 26} {x},{y + 34} Q{x + 14},{y + 26} {x},{y} Z", c="blue", w=4, idp=j), pop(a, j, 1.6 + 0.3 * k)]
B.append(E)
a = 5
# 5 为什么掉不下来：倒挂车 + 2 吨重力
E = [P(a, "M260,260 L1660,260", w=7)]
els, i = R_(a, 960, 260, 1.8, mood="worried", moves=False)
E += els + [rot(a, i + "*", 180, [960, 350], 0.0, 0.01)]
E += arr(a, 960, 520, 960, 800, c="red", w=9, d=1.0) + BIG(a, 1160, 720, "2 吨", c="red", d=1.4, s=100)
E += BIG(a, 960, 980, "为什么掉不下来？", c="ink", d=2.4, s=72)
B.append(E)
a = 6
# 6 风扇抽气，车底变稀
els, i = R_(a, 900, 560, 2.4, moves=False)
E = els + road(a, 560, 200, 1600)
E += fan(a, 700, 640, 60) + fan(a, 1100, 640, 60)
E += puffs(a, 640, 760, -480, 160, n=5, d=0.6, dur=2.2) + puffs(a, 1160, 760, 480, 160, n=5, d=0.6, dur=2.2)
E += T(a, 900, 900, 60, "车底：空气变稀 → 气压低", c="blue", d=2.4)
B.append(E)
a = 7
# 7 大气层：每平方米 10 吨
E = [R(a, 760, 640, 400, 300, c="ink")]
E += [T(a, 960, 810, 52, "1 平方米", c="muted")[0]]
for k in range(7):
    E += arr(a, 700 + k * 87, 220, 700 + k * 87, 600, c="blue", w=6, d=0.2 + 0.12 * k)
E += BIG(a, 1520, 470, "10 吨", c="red", d=1.8, s=150) + T(a, 1520, 590, 52, "大气每平方米压着", c="muted", d=2.2)
B.append(E)
a = 8
# 8 车底低 5% × 8 平方米 = 4 吨
els, i = R_(a, 760, 640, 2.2, moves=False)
E = els + road(a, 640, 160, 1360)
for k in range(6):
    E += arr(a, 420 + k * 136, 260, 420 + k * 136, 360, c="blue", w=6, d=0.1 * k)
for k in range(6):
    E += arr(a, 420 + k * 136, 760, 420 + k * 136, 700, c="blue", w=3, d=0.6 + 0.1 * k)
E += T(a, 1600, 300, 56, "车底 8 m²", d=1.2) + T(a, 1600, 400, 56, "低 5%", c="blue", d=2.0)
E += BIG(a, 1600, 620, "= 4 吨", c="red", d=3.2, s=130)
B.append(E)
a = 9
# 9 天平：4 吨 vs 2 吨
E = [P(a, "M560,860 L1360,860", w=6)]
E += bar(a, 620, 860, 220, 520, "blue", d=0.3) + T(a, 730, 940, 60, "吸力 4 吨", c="blue", d=0.3)
E += bar(a, 1080, 860, 220, 260, "red", d=1.1) + T(a, 1190, 940, 60, "车重 2 吨", c="red", d=1.1)
E += check(a, 1560, 500, d=2.4) + T(a, 1560, 640, 56, "掉不下去", c="green", d=2.6)
B.append(E)
a = 9.1
# 9.1 风扇一停：4 吨变 0，车掉下来
E = [P(a, "M260,240 L1660,240", w=7)]
els, i = R_(a, 760, 240, 1.6, mood="worried", moves=False)
E += els + [rot(a, i + "*", 180, [760, 320], 0.0, 0.01), sh(a, i + "*", 0, 560, 2.2, 0.6)]
E += fan(a, 1360, 520, 80) + cross(a, 1360, 520, d=1.0)
E += BIG(a, 1360, 760, "4 吨 → 0", c="red", d=1.4, s=100) + road(a, 980, 300, 1220)
B.append(E)
a = 10
# 10 屏幕 4700 kg
E = [R(a, 460, 260, 1000, 520, c="ink", sw=6), R(a, 500, 300, 920, 440, c="muted", sw=2)]
E += BIG(a, 960, 560, "4,700 kg", c="red", d=0.4, s=150) + T(a, 960, 680, 52, "下压力（特斯拉屏幕）", c="muted", d=0.8)
E += T(a, 960, 900, 64, "≈ 车重 × 2.3", c="gold", d=2.4)
B.append(E)
a = 11
# 11 可能有水分；4 吨够用
E = T(a, 600, 380, 110, "4,700 kg", c="muted", d=0.0)
i = uid("q")
E += [P(a, "M420,330 L780,420", c="red", w=7, idp=i), pop(a, i, 0.8)] + T(a, 600, 520, 56, "可能有水分", c="red", d=1.0)
E += BIG(a, 1340, 400, "4 吨", c="blue", d=2.4, s=140) + check(a, 1340, 600, d=3.0) + T(a, 1340, 730, 56, "已经够用", c="green", d=3.2)
B.append(E)
a = 12
# 12 1978 BT46B 风扇赛车
E = BIG(a, 400, 300, "1978", c="gold", d=0.2, s=150) + T(a, 400, 420, 64, "F1 · BT46B", d=0.8)
E += [P(a, "M820,760 L860,680 L1180,660 L1300,600 L1480,640 L1560,700 L1580,760 Z", w=6)]
E += [{"t": "ellipse", "at": a, "x": 880, "y": 700, "w": 120, "h": 120, "c": "ink", "sw": 6},
      {"t": "ellipse", "at": a, "x": 1400, "y": 700, "w": 120, "h": 120, "c": "ink", "sw": 6}]
E += fan(a, 760, 650, 85) + T(a, 760, 520, 56, "大风扇", c="blue", d=1.6)
B.append(E)
a = 13
# 13 一场就赢，被叫停：吸尘器、喷石子
E = T(a, 360, 300, 72, "比赛 1 场", d=0.2) + T(a, 360, 420, 72, "赢 1 场", c="green", d=0.9)
E += stamp(a, 360, 640, "叫停", c="red", d=1.8)
E += [P(a, "M1100,760 L1100,560 Q1100,500 1160,500 L1400,500 Q1460,500 1460,560 L1460,760 Z", w=6),
      P(a, "M1280,500 L1280,380 L1520,380", w=6)]
E += fan(a, 1280, 650, 90)
for k in range(5):
    j = uid("stone")
    E += [{"t": "ellipse", "at": a, "id": j, "x": 1060 - k * 10, "y": 700 + (k % 3) * 25, "w": 22, "h": 18, "c": "ink", "fill": "ink"},
          sh(a, j, -420 - k * 60, -60 + k * 30, 2.4 + 0.15 * k, 0.9)]
E += T(a, 1280, 900, 56, "“吸尘器”", c="muted", d=2.0)
B.append(E)
a = 13.1
# 13.1 F1 禁风扇车 40 多年
E = fan(a, 560, 520, 150) + [{"t": "ellipse", "at": a, "x": 380, "y": 340, "w": 360, "h": 360, "c": "red", "sw": 9},
                             P(a, "M430,390 L690,650", c="red", w=9)]
E += BIG(a, 1300, 420, "禁！", c="red", d=0.6, s=150) + BIG(a, 1300, 680, "40+ 年", c="ink", d=1.8, s=120)
B.append(E)
a = 14
# 14 机翼要速度，风扇停着就有
E = T(a, 500, 260, 64, "机翼", c="blue", d=0.2) + T(a, 1420, 260, 64, "风扇", c="red", d=1.4)
E += [P(a, "M300,480 Q500,400 720,470 Q500,450 300,480 Z", c="blue", w=6)]
E += arr(a, 510, 520, 510, 640, c="blue", w=7, d=0.6) + T(a, 500, 760, 52, "要速度", c="blue", d=0.8)
E += fan(a, 1420, 480, 90) + arr(a, 1420, 600, 1420, 760, c="red", w=9, d=1.8) + T(a, 1420, 860, 52, "停着就有", c="red", d=2.2)
B.append(E)
a = 15
# 15 下压力 ∝ v²：速度减半剩 1/4
E = axes(a, 420, 860, 1500, 260, "速度", "下压力")
E += curve(a, "M420,860 Q900,840 1400,320", c="blue", pivot=(420, 860), delay=0.2)
E += curve(a, "M420,560 L1400,560", c="red", w=6, pivot=(420, 560), delay=0.8, dur=1.0) + T(a, 1600, 575, 52, "风扇", c="red", d=1.6)
E += T(a, 1600, 330, 52, "机翼", c="blue", d=1.2)
E += [{"t": "ellipse", "at": a, "x": 896, "y": 745, "w": 28, "h": 28, "c": "gold", "fill": "gold"},
      {"t": "ellipse", "at": a, "x": 1386, "y": 306, "w": 28, "h": 28, "c": "gold", "fill": "gold"}]
E += BIG(a, 900, 200, "速度 ÷ 2 → 力 ÷ 4", c="gold", d=2.6, s=72)
B.append(E)
a = 15.1
# 15.1 弯道：慢下来，风扇照样吸
E = [P(a, "M200,900 Q300,300 960,300 Q1620,300 1720,900", w=7), P(a, "M380,900 Q470,470 960,470 Q1450,470 1540,900", w=7)]
els, i = R_(a, 960, 410, 0.7)
E += els + T(a, 960, 640, 60, "弯道：车速慢", c="ink", d=0.6)
E += T(a, 600, 800, 52, "机翼：没劲", c="blue", d=1.8) + cross(a, 600, 900, c="blue", d=2.0)
E += T(a, 1320, 800, 52, "风扇：照样吸", c="red", d=2.8) + check(a, 1320, 900, c="red", d=3.0)
B.append(E)
a = 16
# 16 打分：真本事
E = T(a, 600, 400, 80, "黑科技一：吸地", d=0.0) + stamp(a, 1320, 420, "真本事", c="green", d=0.6)
els, i = R_(a, 960, 900, 1.3)
E += els + road(a, 900, 500, 1420)
B.append(E)
a = 17
# 17 0–60 mph = 96 km/h，1 秒
els, i = R_(a, 340, 820, 1.4, moves=False)
E = els + road(a, 820) + car_drive(340, 820, 1.4, a, idp=i, rpm=400) + [sh(a, i + "*", 1180, 0, 1.2, 1.0)]
E += BIG(a, 960, 330, "0 → 96 km/h", c="ink", d=0.3, s=110) + BIG(a, 960, 520, "1 秒", c="red", d=1.8, s=150)
B.append(E)
a = 18
# 18 27 m/s 每秒 → 2.7 g
E = T(a, 560, 360, 72, "每秒 + 27 m/s", d=0.2)
E += T(a, 560, 520, 72, "÷ 9.8", c="muted", d=1.4)
E += BIG(a, 1360, 520, "2.7 g", c="red", d=2.4, s=170)
E += arr(a, 820, 450, 1120, 450, c="ink", w=6, d=2.0)
B.append(E)
a = 18.1
# 18.1 一秒只跑 13 米：三辆车长
E = road(a, 760) + cars_row(a, 540, 760, 3, w=260, h=110)
E += arr(a, 540, 860, 1400, 860, c="red", w=7, d=0.4, dur=1.0) + BIG(a, 970, 400, "13.4 m", c="red", d=1.4, s=130)
E += T(a, 970, 960, 52, "≈ 3 辆车长", c="muted", d=2.4)
B.append(E)
a = 18.2
# 18.2 对比：小 R 1 s，最快量产电车 1.7 s，F1 ≈ 2.5 s（横条）
E = []
for k, (lab, secs, c) in enumerate((("小 R（官方）", 1.0, "red"), ("最快量产电车", 1.7, "gold"), ("F1 赛车", 2.5, "blue"))):
    y = 320 + k * 220
    j = uid("hb")
    E += T(a, 400, y + 70, 52, lab, c=c, d=0.3 + 1.2 * k)
    E += [R(a, 640, y, 440 * secs, 100, c=c, fill=c, idp=j, sw=3),
          {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "x", "pivot": [640, y + 50], "dur": 0.7, "delay": 0.3 + 1.2 * k}]
    E += T(a, 700 + 440 * secs, y + 70, 56, f"{secs:g} s", c=c, d=0.6 + 1.2 * k, align="left")
B.append(E)
a = 19
# 19 轮胎极限 1.x g vs 2.7 g
E = [P(a, "M500,860 L1420,860", w=6)]
E += bar(a, 600, 860, 240, 260, "blue", d=0.3) + T(a, 720, 940, 56, "轮胎极限 ≈ 1.x g", c="blue", d=0.3)
E += bar(a, 1080, 860, 240, 560, "red", d=1.2) + T(a, 1200, 940, 56, "需要 2.7 g", c="red", d=1.2)
E += BIG(a, 960, 220, "不够！", c="red", d=2.6, s=100)
B.append(E)
a = 20
# 20 第一招：压紧 → 抓地更牢
els, i = R_(a, 760, 760, 2.2, moves=False)
E = els + road(a, 760)
E += arr(a, 760, 260, 760, 520, c="blue", w=12, d=0.3) + T(a, 900, 360, 56, "风扇压紧", c="blue", d=0.3, align="left")
E += arr(a, 760, 820, 1360, 820, c="red", w=10, d=1.6, dur=0.9) + T(a, 1460, 830, 56, "抓得更牢", c="red", d=2.0, align="left")
B.append(E)
a = 21
# 21 第二招：车尾喷气，像火箭
els, i = R_(a, 900, 760, 2.2, jets="back", moves=False)
E = els + road(a, 760) + [sh(a, i + "*", 500, 0, 1.6, 1.2)]
E += puffs(a, 420, 670, -380, 0, n=6, d=0.3, dur=1.6)
E += T(a, 960, 300, 80, "向后扔空气 → 自己向前", c="red", d=0.8)
E += [P(a, "M1600,560 L1640,440 L1680,560 Z M1625,560 L1625,600 L1655,600 L1655,560", c="gold", w=5)]
B.append(E)
a = 22
# 22 后部四个喷口 80,000 N
E = [P(a, "M380,700 L380,420 L560,420 L560,700 Z", w=6)]
for k in range(4):
    E += puffs(a, 600, 450 + k * 70, 420, 0, n=4, d=0.2 + 0.15 * k, dur=1.4, r=22)
E += T(a, 470, 790, 52, "4 个后喷口", c="muted")
E += BIG(a, 1500, 560, "80,000 N", c="red", d=1.6, s=130) + T(a, 1500, 680, 48, "据报道", c="muted", d=2.0)
B.append(E)
a = 23
# 23 80000 ÷ 2000 = 40 → 4 g
E = T(a, 960, 300, 80, "80,000 N ÷ 2,000 kg", d=0.2)
E += T(a, 960, 450, 80, "= 40 m/s²", c="gold", d=1.8)
E += BIG(a, 960, 700, "4 g", c="red", d=3.0, s=200)
B.append(E)
a = 23.1
# 23.1 只够喷一两秒：专为起步
E = tank(a, 300, 260, 220, 600, 1.0, drain=0.05, d=0.4, dur=1.4)
E += BIG(a, 1100, 420, "1–2 s", c="red", d=1.0, s=150) + T(a, 1100, 600, 60, "只够起步那一下", c="ink", d=2.2)
B.append(E)
a = 24
# 24 一秒？打问号
E = BIG(a, 760, 600, "1 秒", c="ink", d=0.0, s=170)
i = uid("qm")
E += [txt(1200, 640, 300, "?", a, c="red", font="en", id=i), pop(a, i, 1.4, 0.5), pulse(a, i, 2.2)]
E += T(a, 960, 900, 56, "还没有独立测量", c="muted", d=1.0)
B.append(E)
a = 25
# 25 能飞多久？10 喷口 + 600 L（同快节奏样段）
E = T(a, 960, 190, 84, "到底能飞多久？", c="red", d=0.0)
E += car(560, 640, 2.0, a, idp="flyR", jets="down")
E += BIG(a, 1440, 430, "10", c="blue", d=1.2, s=150) + T(a, 1440, 520, 52, "个喷口", c="blue")
E += BIG(a, 1440, 760, "600 L", c="gold", d=2.6, s=150) + T(a, 1440, 850, 52, "压缩空气", c="gold")
B.append(E)
a = 26
# 26 三个浴缸；300 bar ≈ 200 kg；700 bar ≈ 300+ kg
E = []
for k, x in enumerate((240, 520, 800)):
    j = uid("tub")
    E += [P(a, f"M{x},300 L{x + 240},300 Q{x + 230},420 {x + 185},420 L{x + 55},420 Q{x + 10},420 {x},300 Z", w=5, idp=j), pop(a, j, 0.3 * k)]
E += T(a, 640, 520, 56, "600 L ≈ 3 个浴缸", c="gold")
E += [R(a, 1180, 260, 140, 600)] + bar(a, 1195, 845, 110, 285, "gold", d=2.0, dur=1.0)
E += T(a, 1250, 940, 52, "300 bar") + T(a, 1250, 1010, 44, "≈ 200 kg", c="gold")
E += [R(a, 1520, 260, 140, 600)] + bar(a, 1535, 845, 110, 545, "red", d=4.2, dur=1.0)
E += T(a, 1590, 940, 52, "700 bar") + T(a, 1590, 1010, 44, "≈ 300+ kg", c="red")
B.append(E)
a = 27
# 27 F = ṁ·v → 130 kg/s
E = T(a, 960, 260, 76, "推力 = 每秒喷出的空气 × 喷速", d=0.0)
E += T(a, 560, 470, 52, "喷速 v ≈ 600–700 m/s", c="blue") + T(a, 1360, 470, 52, "推力 F ≈ 80,000 N", c="red")
E += BIG(a, 960, 720, "≈ 130 kg/s", c="red", d=3.0, s=140) + T(a, 960, 830, 48, "每秒喷掉的空气", c="muted")
E += puffs(a, 300, 900, 1300, 0, n=6, d=1.0, dur=3.5, r=30)
B.append(E)
a = 28
# 28 一秒半见底；推力跟着掉
E = tank(a, 260, 220, 220, 640, 1.0, drain=0.02, d=1.2, dur=1.5) + T(a, 370, 940, 48, "200 kg", c="gold")
E += axes(a, 700, 860, 1780, 260, "时间", "推力")
E += curve(a, "M700,300 C820,320 900,700 1100,820 C1300,850 1600,855 1780,856", c="red", w=7, pivot=(700, 560), delay=1.2, dur=1.5)
E += BIG(a, 1240, 380, "1.5 秒见底", c="red", d=2.8, s=72)
B.append(E)
a = 29
# 29 悬停：2 万牛，30 kg/s，5–10 秒
E = car(620, 820, 1.7, a, idp="hovR", jets="down")
E += [sh(a, "hovR*", 0, -330, 0.4, 1.2), sh(a, "hovR*", 0, 330, 6.0, 1.2)]
E += T(a, 1400, 300, 64, "托住 2 吨 = 20,000 N", c="blue")
E += T(a, 1400, 470, 64, "每秒 30+ kg", c="red", d=1.6) + BIG(a, 1400, 720, "5–10 s", c="red", d=3.2, s=150)
B.append(E)
a = 29.1
# 29.1 喷火？3000 m/s vs 600 m/s；料 ÷ 5
E = T(a, 300, 360, 56, "冷空气", c="blue", d=0.2) + arr(a, 460, 340, 760, 340, c="blue", w=9, d=0.4) + T(a, 900, 360, 52, "600 m/s", c="blue", d=0.6)
E += T(a, 300, 580, 56, "火箭燃料", c="red", d=1.6) + arr(a, 460, 560, 1640, 560, c="red", w=9, d=1.8, dur=0.9) + T(a, 1750, 580, 52, "3,000", c="red", d=2.4)
E += BIG(a, 960, 860, "同样推力：料 ÷ 5", c="green", d=3.6, s=96)
B.append(E)
a = 29.2
# 29.2 路人被烤 → 只能喷冷气
E = stick(1300, 820, 1.6, a, idp=uid("bys"))
for k in range(5):
    j = uid("fl")
    x = 380 + k * 110
    E += [P(a, f"M{x},820 Q{x - 50},700 {x},560 Q{x + 50},700 {x},820 Z", c="red", w=5, idp=j), pop(a, j, 0.3 + 0.15 * k),
          {"t": "move", "at": a, "kind": "wiggle", "targets": [j], "pivot": [x, 820], "amp": 6, "hz": 5}]
E += BIG(a, 1300, 300, "被烤了", c="red", d=1.6, s=110) + T(a, 600, 960, 60, "所以：只能喷冷气", c="blue", d=3.2)
B.append(E)
a = 29.3
# 29.3 卫星喷冷气调姿态
j = uid("sat")
E = [R(a, 820, 440, 280, 200, idp=j), R(a, 420, 500, 360, 80, c="blue", idp=j, sw=4), R(a, 1140, 500, 360, 80, c="blue", idp=j, sw=4),
     rot(a, j, 25, [960, 540], 2.2, 1.6)]
E += puffs(a, 1110, 450, 300, -120, n=4, d=1.6, dur=1.2, r=22)
E += T(a, 960, 860, 60, "卫星调姿态：喷冷气", c="blue", d=0.4)
B.append(E)
a = 30
# 30–33 虚拟实验（同一张画板，右边一列数字依次蹦出）
E = [{"t": "media", "at": a, "src": "video:" + str(here / "_lab.webm"), "x": 60, "y": 260, "w": 1440, "h": 675, "play": 23}]
E += T(a, 780, 190, 64, "虚拟实验：自己调", c="blue", d=0.0)
E += BIG(31, 1720, 420, "≈ 5 s", c="gold", d=0.8, s=90) + T(31, 1720, 490, 40, "300 bar", c="muted", d=0.8)
E += BIG(32, 1720, 640, "≈ 10 s", c="red", d=0.8, s=90) + T(32, 1720, 710, 40, "700 bar", c="muted", d=0.8)
E += BIG(33, 1720, 860, "≈ 12 s", c="red", d=0.8, s=90) + T(33, 1720, 930, 40, "−500 kg", c="muted", d=0.8)
B.append(E)
a = 33.1
# 33.1 车重 −25%，时间 +2 s；瓶颈是罐子
E = T(a, 500, 320, 64, "车重 −25%", c="ink", d=0.2) + T(a, 500, 460, 64, "时间 +2 s", c="gold", d=1.2)
E += tank(a, 1240, 220, 260, 640, 0.9) + BIG(a, 1370, 960, "瓶颈：罐子", c="red", d=2.6, s=72)
j = uid("ring")
E += [{"t": "ellipse", "at": a, "id": j, "x": 1170, "y": 170, "w": 400, "h": 740, "c": "red", "sw": 7}, pop(a, j, 2.4), pulse(a, j, 3.0)]
B.append(E)
a = 34
# 34 降温、结霜
E = T(a, 960, 200, 80, "隐藏减益：冷", c="blue", d=0.0)
E += [R(a, 300, 320, 60, 520)] + [{"t": "ellipse", "at": a, "x": 270, "y": 820, "w": 120, "h": 120, "c": "ink", "sw": 5}]
j = uid("merc")
E += [R(a, 315, 340, 30, 500, c="red", fill="red", idp=j, sw=3),
      {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "from": 1, "to": 0.25, "pivot": [330, 840], "dur": 3.0, "delay": 0.6}]
E += T(a, 520, 600, 52, "越喷越冷", c="blue", align="left")
for k, (x, y) in enumerate([(1100, 420), (1360, 360), (1600, 470), (1250, 620), (1500, 700)]):
    j = uid("sn")
    E += [P(a, f"M{x - 40},{y} L{x + 40},{y} M{x},{y - 40} L{x},{y + 40} M{x - 28},{y - 28} L{x + 28},{y + 28} M{x - 28},{y + 28} L{x + 28},{y - 28}", c="blue", w=5, idp=j),
          pop(a, j, 2.0 + 0.4 * k), spin(a, j, [x, y], 20)]
E += T(a, 1360, 880, 56, "压力掉得更快 · 喷口结霜", c="red")
B.append(E)
a = 35
# 35 结论：很贵的跳
E = car(960, 880, 2.0, a, idp="jmpR", mood="o", jets="down")
E += [sh(a, "jmpR*", 0, -300, 0.3, 0.5), sh(a, "jmpR*", 0, 300, 1.3, 0.5)]
E += BIG(a, 960, 220, "不是飞，是很贵的跳", c="red", d=1.8, s=96) + T(a, 960, 360, 52, "200 kg 空气 → 1 次跳", c="gold")
B.append(E)
a = 36
# 36 空中翻跟头？
els, i = R_(a, 960, 780, 2.0, jets="down", moves=False)
E = els + [rot(a, i + "*", 360, [960, 700], 0.5, 2.2)]
E += BIG(a, 960, 220, "怎么翻跟头？", c="ink", d=1.6, s=96)
B.append(E)
a = 37
# 37 力矩：推力偏离重心
els, i = R_(a, 900, 760, 2.0, moves=False)
E = els
E += [{"t": "ellipse", "at": a, "x": 875, "y": 645, "w": 50, "h": 50, "c": "gold", "fill": "gold"}] + T(a, 760, 600, 44, "重心", c="gold", d=0.2)
E += arr(a, 1160, 1000, 1160, 800, c="red", w=12, d=0.8) + T(a, 1280, 980, 52, "推力偏一点", c="red", d=0.9, align="left")
E += [rot(a, i + "*", -20, [900, 670], 2.0, 1.4)]
E += BIG(a, 960, 220, "力矩 = 推力 × 偏离", c="red", d=3.0, s=84)
B.append(E)
a = 37.1
# 37.1 力矩 = 推力 × 距离；偏 1 m → 80,000 N·m
E = T(a, 960, 300, 84, "力矩 = 推力 × 距离", c="red", d=0.0)
E += T(a, 960, 500, 60, "假如偏 1 m", c="muted", d=1.6)
E += BIG(a, 960, 720, "80,000 N·m", c="red", d=2.6, s=130)
els, i = R_(a, 1620, 900, 0.8, mood="o", moves=False)
E += els + [rot(a, i + "*", 360, [1620, 860], 3.4, 1.0)]
B.append(E)
a = 38
# 38 前喷抬头；左喷打滚
els, i = R_(a, 520, 640, 1.3, moves=False)
E = els + arr(a, 680, 820, 680, 680, c="red", w=10, d=0.2) + [rot(a, i + "*", -30, [520, 590], 0.8, 1.2)]
E += T(a, 520, 330, 60, "前喷 → 抬头", c="red", d=0.4)
j = uid("roll")   # car seen from behind: a box with two wheels, rolling
E += [P(a, "M1240,640 L1240,520 L1300,460 L1540,460 L1600,520 L1600,640 Z", w=6, idp=j),
      {"t": "rect", "at": a, "id": j, "x": 1250, "y": 640, "w": 60, "h": 70, "c": "ink", "fill": "ink"},
      {"t": "rect", "at": a, "id": j, "x": 1530, "y": 640, "w": 60, "h": 70, "c": "ink", "fill": "ink"}]
E += arr(a, 1280, 860, 1280, 730, c="blue", w=10, d=2.6) + [rot(a, j, 90, [1420, 580], 3.2, 1.6)]
E += T(a, 1420, 330, 60, "左喷 → 打滚", c="blue", d=2.8)
B.append(E)
a = 39
# 39 十个喷口配合；火箭回收
els, i = R_(a, 560, 660, 1.6, jets="down")
E = els
E += T(a, 560, 300, 60, "10 个喷口配合", c="blue", d=0.2)
j = uid("rk")
E += [P(a, "M1420,260 L1470,180 L1520,260 L1520,700 L1420,700 Z M1420,640 L1370,720 L1420,700 M1520,640 L1570,720 L1520,700", w=6, idp=j),
      P(a, "M1440,720 L1470,820 L1500,720", c="red", w=5, idp=j), sh(a, j, 0, 140, 1.8, 2.4)]
E += road(a, 960, 1260, 1680) + T(a, 1470, 1030, 52, "火箭回收：同一招", c="red", d=2.4)
B.append(E)
a = 40
# 40 直升机一小时 vs 喷口几秒
j = uid("heli")
E = [P(a, "M300,560 Q300,460 420,460 L620,460 Q700,460 700,560 Q700,640 600,640 L420,640 Q300,640 300,560 Z M700,540 L940,520 L960,480 M560,460 L560,400", w=6)]
E += [P(a, "M300,400 L820,400", c="blue", w=7, idp=j), {"t": "move", "at": a, "kind": "wiggle", "targets": [j], "pivot": [560, 400], "amp": 8, "hz": 6}]
E += BIG(a, 520, 860, "1 小时", c="green", d=0.8, s=110)
E += car(1420, 600, 1.4, a, idp="hvR2", jets="down") + BIG(a, 1420, 860, "几秒", c="red", d=2.0, s=110)
E += BIG(a, 960, 220, "为什么？", c="ink", d=3.2, s=96)
B.append(E)
a = 41
# 41 推力 = ṁv；力气 = ṁv²/2
E = T(a, 960, 330, 84, "推力 = 每秒空气 × v", c="blue", d=0.2)
i = uid("v2")
E += [txt(960, 600, 84, "力气 = 每秒空气 × v² ÷ 2", a, c="red", id=i), pop(a, i, 2.4), pulse(a, i, 4.4, 0.8)]
E += BIG(a, 1560, 470, "v²！", c="gold", d=4.2, s=110)
E += T(a, 960, 860, 52, "v = 喷出去的速度", c="muted", d=1.2)
B.append(E)
a = 42
# 42 速度 ×2：推力 ×2，力气 ×4 → 多推空气、推慢点
E = [P(a, "M360,800 L1340,800", w=6)]
E += bar(a, 420, 800, 180, 160, "blue", d=0.3) + bar(a, 640, 800, 180, 320, "blue", d=0.8) + T(a, 620, 880, 52, "推力 ×2", c="blue", d=0.8)
E += bar(a, 880, 800, 180, 80, "red", d=1.4) + bar(a, 1100, 800, 180, 320, "red", d=1.9) + T(a, 1080, 880, 52, "力气 ×4", c="red", d=1.9)
E += T(a, 1600, 420, 64, "省力秘诀：", c="ink", d=3.2) + BIG(a, 1600, 580, "多推空气", c="green", d=3.6, s=80) + BIG(a, 1600, 720, "推慢一点", c="green", d=4.2, s=80)
B.append(E)
a = 43
# 43 喷口：30 kg/s × 600+ m/s → 6000+ kW
E = car(520, 560, 1.6, a, idp="jtR", jets="down")
E += puffs(a, 400, 720, 0, 300, n=3, d=0.2, dur=0.8, r=30) + puffs(a, 640, 720, 0, 300, n=3, d=0.2, dur=0.8, r=30)
E += T(a, 1300, 300, 64, "每秒 30 kg", c="blue", d=0.4) + T(a, 1300, 430, 64, "× 600+ m/s", c="blue", d=1.4)
E += BIG(a, 1300, 680, "6,000+ kW", c="red", d=2.8, s=140)
B.append(E)
a = 44
# 44 十米旋翼：1 吨/秒 × 20 m/s → 200 kW
j = uid("rot")
E = [P(a, "M180,360 L940,360", c="blue", w=8, idp=j), spin(a, j, [560, 360], 90),
     P(a, "M560,360 L560,470 M440,470 Q440,560 560,560 Q680,560 680,470 Z", w=6)]
E += T(a, 560, 290, 48, "10 m", c="muted")
for k in range(6):
    E += arr(a, 260 + k * 120, 600, 260 + k * 120, 860, c="blue", w=5, d=0.2 + 0.1 * k, dur=0.9)
E += T(a, 1400, 300, 64, "每秒 1 吨空气", c="blue", d=0.6) + T(a, 1400, 430, 64, "× 20 m/s", c="blue", d=1.6)
E += BIG(a, 1400, 680, "≈ 200 kW", c="green", d=2.8, s=140)
B.append(E)
a = 45
# 45 差 30 倍；飞行汽车都长螺旋桨
E = [P(a, "M300,820 L900,820", w=6)]
E += bar(a, 380, 820, 180, 600, "red", d=0.2) + T(a, 470, 900, 48, "喷口", c="red", d=0.2)
E += bar(a, 640, 820, 180, 20, "green", d=0.6) + T(a, 730, 900, 48, "旋翼", c="green", d=0.6)
E += BIG(a, 600, 160, "× 30", c="red", d=1.2, s=120)
g = uid("drone")
E += [P(a, "M1240,600 L1640,600 L1600,680 L1280,680 Z M1260,600 L1260,520 M1620,600 L1620,520", w=6, idp=g + "_b"),
      P(a, "M1170,520 L1350,520 M1530,520 L1710,520", c="blue", w=7, idp=g + "_r"),
      {"t": "move", "at": a, "kind": "wiggle", "targets": [g + "_r"], "pivot": [1440, 520], "amp": 6, "hz": 7}, sh(a, g + "*", 0, -120, 2.8, 1.4)]
E += T(a, 1440, 820, 56, "真正的飞行汽车：螺旋桨", c="green", d=3.0)
B.append(E)
a = 45.1
# 45.1 无人机大桨慢转：桨越大越省电
j1, j2 = uid("bp"), uid("sp")
E = [P(a, "M260,560 L860,560", c="blue", w=8, idp=j1), spin(a, j1, [560, 560], 40), {"t": "ellipse", "at": a, "x": 535, "y": 535, "w": 50, "h": 50, "c": "ink", "fill": "ink"}]
E += [P(a, "M1300,560 L1540,560", c="red", w=8, idp=j2), spin(a, j2, [1420, 560], 400), {"t": "ellipse", "at": a, "x": 1400, "y": 540, "w": 40, "h": 40, "c": "ink", "fill": "ink"}]
E += T(a, 560, 760, 56, "大桨慢转", c="green", d=0.6) + T(a, 1420, 760, 56, "小桨猛转", c="red", d=1.4)
E += BIG(a, 960, 940, "桨越大，越省电", c="green", d=2.6, s=80)
B.append(E)
a = 46
# 46 打分：表演，不是交通工具
E = T(a, 640, 360, 72, "黑科技三：飞", d=0.0) + T(a, 640, 500, 56, "物理没错", c="green", d=0.6) + check(a, 900, 490, d=0.8)
E += stamp(a, 1380, 460, "表演", c="red", d=1.8) + T(a, 1380, 700, 52, "不是交通工具", c="red", d=2.4)
B.append(E)
a = 47
# 47 坐在里面：4 g ≈ 过山车
E = stick(560, 640, 1.6, a, idp=uid("man"))
E += arr(a, 820, 520, 380, 520, c="red", w=12, d=0.6) + BIG(a, 860, 300, "4 g", c="red", d=1.0, s=130)
j = uid("rc")
E += [P(a, "M1100,860 Q1250,300 1400,700 Q1500,920 1620,500 Q1700,300 1800,600", c="blue", w=6, idp=j)]
E += [{"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "x", "pivot": [1100, 860], "dur": 1.6, "delay": 2.0}]
E += T(a, 1450, 1000, 52, "≈ 过山车最猛那一下", c="blue", d=2.6)
B.append(E)
a = 47.1
# 47.1 70 kg × 4 = 280 kg
E = stick(560, 760, 1.6, a, idp=uid("sit")) + [P(a, "M400,780 L720,780 L720,860 L400,860 Z", w=6)]
E += arr(a, 560, 380, 560, 520, c="red", w=10, d=0.4)
E += T(a, 1300, 360, 72, "70 kg × 4", c="ink", d=0.4) + BIG(a, 1300, 600, "= 280 kg", c="red", d=1.8, s=140)
B.append(E)
a = 48
# 48 头朝下；抗荷服？
j = uid("hd")
E = stick(560, 560, 1.6, a, idp=j) + [rot(a, j + "*", 180, [560, 520], 0.3, 0.8)]
for k in range(4):
    E += arr(a, 500 + k * 40, 380, 500 + k * 40, 700, c="red", w=5, d=1.2 + 0.15 * k)
E += T(a, 760, 860, 52, "血往脑袋冲", c="red", d=1.6, align="left")
E += [P(a, "M1300,300 L1500,300 L1560,420 L1540,800 L1260,800 L1240,420 Z", c="green", w=6)]
E += BIG(a, 1400, 940, "抗荷服？", c="green", d=3.0, s=80)
B.append(E)
a = 49
# 49 碳纤维气罐塞满车：轮胎的上百倍
E = [P(a, "M260,700 L260,560 L520,540 L700,420 L1180,420 L1420,540 L1660,560 L1680,700 Z", w=6)]
for k, (x, y) in enumerate(((420, 600), (620, 600), (820, 520), (1020, 520), (1220, 600), (1420, 620))):
    j = uid("cyl")
    E += [{"t": "ellipse", "at": a, "id": j, "x": x - 70, "y": y - 32, "w": 140, "h": 64, "c": "gold", "fill": "gold"}, pop(a, j, 0.3 + 0.25 * k)]
E += T(a, 960, 300, 60, "碳纤维缠绕高压气罐", c="gold", d=0.2)
E += BIG(a, 960, 880, "气压 > 轮胎 × 100", c="red", d=2.6, s=90)
B.append(E)
a = 50
# 50 又轻又结实；SpaceX 事故
j = uid("cy2")
E = [{"t": "ellipse", "at": a, "id": j, "x": 360, "y": 420, "w": 400, "h": 180, "c": "gold", "fill": "gold"}]
E += T(a, 560, 720, 56, "轻 · 结实", c="green", d=0.4) + check(a, 800, 700, d=0.6)
E += [P(a, "M1340,820 L1340,380 L1400,280 L1460,380 L1460,820 Z", w=6)]
k = uid("boom")
E += [P(a, "M1400,500 L1440,420 L1460,500 L1540,460 L1490,540 L1560,580 L1470,590 L1490,670 L1420,610 L1360,680 L1370,600 L1290,580 L1360,540 L1300,460 L1380,490 Z",
        c="red", w=6, idp=k), pop(a, k, 2.2, 0.5), pulse(a, k, 2.8)]
E += T(a, 1400, 940, 52, "SpaceX 几次事故与它有关", c="red", d=2.6, font="zh")
B.append(E)
a = 51
# 51 碎石飞出几十米
els, i = R_(a, 560, 740, 1.6, jets="down", moves=False)
E = els + road(a, 740, 120, 1800)
for k in range(8):
    j = uid("gr")
    E += [{"t": "ellipse", "at": a, "id": j, "x": 680 + (k % 3) * 12, "y": 730 - (k % 4) * 10, "w": 20, "h": 16, "c": "ink", "fill": "ink"},
          sh(a, j, 300 + k * 110, -40 - (k % 3) * 60, 0.4 + 0.12 * k, 1.0)]
E += BIG(a, 1400, 420, "几十米", c="red", d=1.8, s=110) + T(a, 1400, 540, 48, "据报道", c="muted", d=2.2)
E += stick(1700, 720, 0.9, a, idp=uid("by"))
B.append(E)
a = 52
# 52 充满气罐 20+ 度电 = 跑 100+ 公里
E = tank(a, 300, 300, 240, 520, 0.05)
j = uid("fill")
E += [R(a, 316, 384, 208, 420, c="gold", fill="gold", idp=j, sw=3),
      {"t": "move", "at": a, "kind": "grow", "targets": [j], "axis": "y", "pivot": [420, 804], "dur": 1.6, "delay": 0.3}]
E += BIG(a, 1000, 480, "20+ 度电", c="gold", d=1.4, s=110)
E += arr(a, 1000, 580, 1000, 700, c="ink", d=2.4)
els, i = R_(a, 1300, 900, 1.0, moves=False)
E += els + road(a, 900, 900, 1800) + car_drive(1300, 900, 1.0, a, idp=i) + [sh(a, i + "*", 360, 0, 3.0, 2.0)]
E += BIG(a, 1550, 780, "100+ km", c="green", d=3.2, s=90)
B.append(E)
a = 52.1
# 52.1 一跳十几块钱；贵的是罐子和风险
E = []
for k in range(5):
    j = uid("coin")
    E += [{"t": "ellipse", "at": a, "id": j, "x": 300 + k * 30, "y": 760 - k * 70, "w": 220, "h": 70, "c": "gold", "fill": "gold"}, pop(a, j, 0.2 + 0.2 * k)]
E += BIG(a, 1200, 400, "一跳 ≈ 十几块", c="gold", d=0.8, s=96)
E += T(a, 1200, 640, 64, "贵的是：罐子 + 风险", c="red", d=2.8)
B.append(E)
a = 53
# 53 马斯克原话
E = T(a, 960, 240, 56, "马斯克原话：", c="muted", d=0.0)
E += T(a, 960, 450, 80, "“安全不是主要目标”", c="red", d=0.6)
E += T(a, 960, 680, 80, "“争取不害死任何人”", c="red", d=3.2)
B.append(E)
a = 54
# 54 不加评论
els, i = R_(a, 960, 760, 2.4, mood="o")
E = els + road(a, 760, 500, 1420) + BIG(a, 960, 300, "不加评论", c="ink", d=0.4, s=110)
B.append(E)
a = 55
# 55–58 打分表（同一张画板，一行一行蹦出）
E = BIG(a, 960, 170, "打分表", c="ink", d=0.0, s=96)
rows = [(56, "吸地", "真本事 · 1978 年就有", "green", True), (57, "一秒破百", "说得通 · 等独立测量", "gold", None), (58, "飞", "几秒钟的表演", "red", False)]
for r, (at, k1, k2, c, ok) in enumerate(rows):
    y = 380 + r * 200
    E += T(at, 420, y, 72, k1, c=c, d=0.1) + T(at, 1100, y, 60, k2, c=c, d=0.6)
    E += (check(at, 1700, y - 20, d=1.0) if ok else cross(at, 1700, y - 20, d=1.0) if ok is False
          else T(at, 1700, y + 10, 100, "?", c="gold", d=1.0, font="en"))
B.append(E)
a = 59
# 59 时间表 2017 → 2028
E = [P(a, "M160,560 L1760,560", w=6)]
for k, (y, lab, c) in enumerate(((2017, "发布", "ink"), (2020, "推迟", "red"), (2021, "推迟", "red"), (2023, "推迟", "red"),
                                 (2024, "推迟", "red"), (2028, "量产？", "gold"))):
    x = 260 + k * 280
    j = uid("tl")
    E += [{"t": "ellipse", "at": a, "id": j, "x": x - 22, "y": 538, "w": 44, "h": 44, "c": c, "fill": c}, pop(a, j, 0.3 + 0.55 * k),
          txt(x, 470, 48, str(y), a, c=c, font="en", id=j), txt(x, 660, 48, lab, a, c=c, id=j)]
B.append(E)
a = 59.1
# 59.1 1.9 s → 1 s；2020 → 2028
E = T(a, 520, 400, 100, "1.9 s", c="muted", d=0.2) + arr(a, 760, 380, 1120, 380, c="ink", w=7, d=0.8) + BIG(a, 1380, 410, "1 s", c="red", d=1.2, s=110)
E += T(a, 520, 700, 100, "2020", c="muted", d=2.2) + arr(a, 760, 680, 1120, 680, c="ink", w=7, d=2.8) + BIG(a, 1380, 710, "2028", c="red", d=3.2, s=110)
E += T(a, 520, 260, 44, "承诺", c="muted", d=0.2) + T(a, 1380, 260, 44, "现在", c="muted", d=1.2)
B.append(E)
a = 60
# 60 蛇河峡谷
E = [P(a, "M120,520 L700,520 L760,960 M1220,960 L1280,520 L1800,520", w=7), P(a, "M760,960 L1220,960", c="blue", w=5)]
els, i = R_(a, 420, 520, 1.0, jets="down", moves=False)
E += els + [sh(a, i + "*", 520, -260, 0.8, 1.2), sh(a, i + "*", 520, 260, 2.0, 1.2)]
E += T(a, 990, 230, 72, "蛇河峡谷", c="blue", d=0.4) + BIG(a, 990, 380, "飞过去？", c="red", d=2.8, s=90)
B.append(E)
a = 61
# 61 1974 火箭摩托，降落伞提前打开
E = [P(a, "M120,520 L700,520 L760,960 M1220,960 L1280,520 L1800,520", w=7)]
E += BIG(a, 300, 300, "1974", c="gold", d=0.2, s=120)
j = uid("chute")
E += [P(a, "M860,300 Q990,180 1120,300 Z M860,300 L990,440 M1120,300 L990,440 M990,300 L990,440", c="red", w=6, idp=j),
      {"t": "ellipse", "at": a, "id": j, "x": 960, "y": 430, "w": 60, "h": 40, "c": "ink", "fill": "ink"},
      pop(a, j, 1.6), sh(a, j, 0, 440, 2.4, 2.4), {"t": "move", "at": a, "kind": "wiggle", "targets": [j], "pivot": [990, 300], "amp": 6, "hz": 1.5}]
E += T(a, 1500, 300, 56, "降落伞提前打开", c="red", d=1.8)
B.append(E)
a = 62
# 62 真飞过去，再做一期
els, i = R_(a, 960, 760, 2.4)
E = els + road(a, 760, 500, 1420) + car_drive(960, 760, 2.4, a, idp=i, rpm=60)
E += BIG(a, 960, 300, "再做一期！", c="red", d=0.8, s=110)
B.append(E)
a = 62.1
# 62.1 下期见
els, i = R_(a, 760, 760, 2.4)
E = els + road(a, 760, 300, 1220) + car_drive(760, 760, 2.4, a, idp=i, rpm=80)
E += BIG(a, 1500, 420, "下期见", c="blue", d=0.4, s=120) + T(a, 1500, 560, 56, "小 R：表现不错", c="green", d=2.0)
B.append(E)
a = 63
# 63 友情提示
E = T(a, 960, 190, 72, "友情提示", c="ink", d=0.0)
E += T(a, 960, 380, 52, "特斯拉的说法：吸力 · 一秒破百 · 600 升", c="blue", d=0.8)
E += T(a, 960, 520, 52, "媒体报道：80,000 N", c="gold", d=4.0)
E += T(a, 960, 660, 52, "我们的估算：空气量 · 飞行时间 · 功率 · 电量", c="red", d=6.0)
B.append(E)

assert len(S) == 84, len(S)
for b in B:
    for e in b:
        e["at"] = IDX[e["at"]]
boards = [{"elements": b} for b in B]

def fit(boards, segs):
    """Squeeze each delayed move into the time its board is on screen (speech is fast; a move after the cut is never seen)."""
    for b in boards:
        last = max(e["at"] for e in b["elements"])
        for e in b["elements"]:
            if e["t"] != "move" or e.get("delay") is None:
                continue
            avail = segs[last]["t1"] - segs[e["at"]]["t0"] - 0.5
            need = e["delay"] + e.get("dur", 1.0)
            if need > avail > 0:
                k = avail / need
                e["delay"] = round(e["delay"] * k, 2)
                e["dur"] = round(max(0.25, e.get("dur", 1.0) * k), 2)
    return boards


if __name__ == "__main__":
    bad = missing_chars("".join(e.get("text", "") for b in B for e in b))
    if bad:
        sys.exit(f"the fonts lack: {bad}")
    if "--boards-only" in sys.argv:
        lesson = json.load(open(here / "lesson.json"))
        lesson["boards"] = fit(boards, lesson["segments"])
        json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
        sys.exit(print(len(boards), "boards"))
    import numpy as np, soundfile as sf, sherpa_onnx as so  # noqa: E401
    d = sys.argv[1].rstrip("/") + "/"
    tts = so.OfflineTts(so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(kokoro=so.OfflineTtsKokoroModelConfig(
        model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
        lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"), num_threads=4),
        rule_fsts=d + "date-zh.fst," + d + "number-zh.fst," + d + "phone-zh.fst", max_num_sentences=1))
    t, parts, segs, sr = 0.3, [], [], 24000
    for zh, en in S:
        say = zh
        for k, v in SAY.items():
            say = say.replace(k, v)
        import hashlib
        cache = here / "_tts" / (hashlib.md5(say.encode()).hexdigest()[:16] + ".wav")   # 改一句只重配这一句
        if cache.exists():
            x, sr = sf.read(cache, dtype="float32")
        else:
            a = tts.generate(speakable(say), sid=49, speed=1.22)
            sr = a.sample_rate
            x = np.array(a.samples, dtype=np.float32)
            cache.parent.mkdir(exist_ok=True)
            sf.write(cache, x, sr)
        if not parts:
            parts.append(np.zeros(int(sr * 0.3), np.float32))
        segs.append({"zh": zh, "en": en, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
        parts += [x, np.zeros(int(sr * 0.12), np.float32)]
        t += len(x) / sr + 0.12
    parts.append(np.zeros(int(sr * 1.0), np.float32))
    t += 1.0
    sf.write(here / "配音.wav", np.concatenate(parts), sr)
    lesson = wai.to_lesson({"zh": "会飞的特斯拉，到底能飞多久？", "en": "The flying Tesla: how long can it really fly?"}, segs, fit(boards, segs),
                           audio="配音.wav", duration=round(t, 2))
    lesson.update(pace=0.2, hand=False, subs=True, ink=1.7, pan=0.45)
    json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
    print(len(segs), "segments", round(t, 1), "s")
