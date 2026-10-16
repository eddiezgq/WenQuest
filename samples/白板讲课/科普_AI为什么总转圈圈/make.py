"""科普短片（每日热点 + 科普）第 1 期《AI 为什么总“转圈圈”？》（Eddie 22:43–22:47：DeepSeek 宕机，原因、怎么改、像不像当年的电；三分钟）。
事实来源：澎湃新闻 2026-10-15（宕机 8:11–13:04、补偿、专家分析）、The Register 2026-09-03（ChatGPT、Claude、Grok 同日故障，OpenAI 路由读错配置），
电力史（1882 珍珠街电站、1965、2003 北美大停电、冷负荷启动、备用容量、N-1）。固定角色“小卡”（一张显卡）。没有手。
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
from popkit import bubble, stick, txt  # noqa: E402

SEG = [
 "今天早上八点，很多人打开 DeepSeek，看到的是一个转圈圈。",
 "转了五个小时。",
 "别笑。九月三号，ChatGPT、Claude、Grok 同一天出故障。AI 宕机，快成天气预报了。",
 "这些公司有的是钱，有的是天才，为什么还老崩？",
 "先看你问一句话，背后发生了什么：问题被拆成一串小块，送进一台装满显卡的机器，几千亿个参数，一个字一个字往外算。",
 "一台机器一次只能接待这么多人。人多了排队，排不下，就转圈圈。",
 "原因一：算力不够。内测时一个账号最多同时问二十个问题，还搞峰谷价格，白天贵、半夜便宜。",
 "等等，峰谷价格？这个我们见过。一百多年前，电刚进城，也是这样。",
 "1882 年爱迪生建了第一座电站，只管周围几条街。电站一出问题，这几条街就黑。",
 "后来电站连成电网，灯更稳了，新问题也来了：一处出事，能拖垮一大片。",
 "1965 年，北美一个保护开关设得太敏感，跳了一下，连锁反应，三千万人摸黑十几个小时。",
 "2003 年更离谱：一套报警软件有 bug，值班的人没收到警报，五千万人停电。",
 "原因二：牵一发动全身。OpenAI 九月那次，就是路由系统读错了一条配置更新。",
 "原因三，最反直觉：恢复比崩溃还难。大模型重启，要把几百 GB 的参数重新搬进显卡、预热，再一点一点放人进来。",
 "可这时候，所有人都在疯狂点“重试”。",
 "电网管这叫“冷负荷启动”：一来电，全城冰箱空调同时开机，一冲，又跳闸了。",
 "怎么改？电力行业花了一百年，攒了四条老规矩，AI 正好抄作业。",
 "一，留余量：多备几台发电机，算力也要有备用。",
 "二，N 减 1：坏掉任何一个零件，都得照常运转。DeepSeek 说要“消除单点依赖”，就是这条。",
 "三，宁可限电，不要全黑：人太多，先让一部分人排队，别让所有人一起转圈圈。",
 "四，先在一个小区试，再全城推：新版本先放一小部分流量试试，这叫灰度发布。",
 "所以 AI 会不会像电一样，变成谁都离不开、谁也看不见的基础设施？我猜会。",
 "到那一天，AI 停摆就像停电，要上新闻、要追责、要赔钱。",
 "至于今天？DeepSeek 已经赔了，补了你一周的钱。下次它再转圈圈，你可以先去泡杯茶。",
]
SAY = {"DeepSeek": "Deep Seek", "ChatGPT": "Chat G P T", "GB": "G B", "bug": "bug", "1882": "一八八二", "1965": "一九六五", "2003": "二零零三",
       "N 减 1": "N 减一"}


def xiaoka(cx, cy, k, at, idp="ka", mood="happy", sweat=False, moves=True):
    """小卡: a graphics card with a face — the recurring character. Ids <idp>_*; "<idp>*" moves the whole card."""
    def P(d, c="ink", w=3.4, part="_b"):
        return {"t": "path", "at": at, "id": idp + part, "c": c, "w": w, "d": d}
    x0, y0, w, h = cx - 130 * k, cy - 80 * k, 260 * k, 160 * k
    E = [P(f"M{x0 + 18 * k},{y0} L{x0 + w - 18 * k},{y0} Q{x0 + w},{y0} {x0 + w},{y0 + 18 * k} L{x0 + w},{y0 + h - 18 * k} "
           f"Q{x0 + w},{y0 + h} {x0 + w - 18 * k},{y0 + h} L{x0 + 18 * k},{y0 + h} Q{x0},{y0 + h} {x0},{y0 + h - 18 * k} "
           f"L{x0},{y0 + 18 * k} Q{x0},{y0} {x0 + 18 * k},{y0} Z")]
    for fx in (cx - 70 * k, cx + 70 * k):          # two fans (the eyes sit in them)
        E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": fx - 48 * k, "y": cy - 62 * k, "w": 96 * k, "h": 96 * k, "c": "blue"})
        E.append({"t": "ellipse", "at": at, "id": idp + "_b", "x": fx - 13 * k, "y": cy - 30 * k, "w": 26 * k, "h": 30 * k, "c": "ink", "fill": "ink"})
    for i in range(6):                               # gold contacts under the card
        E.append({"t": "rect", "at": at, "id": idp + "_b", "x": x0 + 40 * k + i * 32 * k, "y": y0 + h, "w": 18 * k, "h": 22 * k, "c": "gold", "fill": "gold"})
    mouth = {"happy": f"M{cx - 26 * k},{cy + 40 * k} Q{cx},{cy + 64 * k} {cx + 26 * k},{cy + 40 * k}",
             "tired": f"M{cx - 26 * k},{cy + 56 * k} Q{cx},{cy + 36 * k} {cx + 26 * k},{cy + 56 * k}",
             "o": f"M{cx - 12 * k},{cy + 48 * k} a12,14 0 1,0 24,0 a12,14 0 1,0 -24,0"}[mood]
    E.append(P(mouth, w=3.4))
    if sweat:
        E.append(P(f"M{x0 + w + 10 * k},{y0 + 10 * k} Q{x0 + w + 30 * k},{y0 + 50 * k} {x0 + w + 10 * k},{y0 + 60 * k} "
                   f"Q{x0 + w - 10 * k},{y0 + 50 * k} {x0 + w + 10 * k},{y0 + 10 * k}", c="blue", w=3, part="_sweat"))
    E.append(txt(x0 + w - 36 * k, y0 + 30 * k, 22 * k, "GPU", at, c="muted", font="en", id=idp + "_b"))
    if moves:
        E.append({"t": "move", "at": at, "kind": "bob", "targets": [idp + "*"], "amp": 10 * k, "hz": 1.4})
    return E


def spinner(cx, cy, r, at, idp, c="blue", rpm=50):
    return [{"t": "path", "at": at, "id": idp, "c": c, "w": 7, "d": f"M{cx + r},{cy} A{r},{r} 0 1,1 {cx},{cy - r}"},
            {"t": "move", "at": at, "kind": "spin", "targets": [idp], "pivot": [cx, cy], "rpm": rpm}]


def pylon(x, y, at, idp):
    """A power pylon standing on (x, y)."""
    return [{"t": "path", "at": at, "id": idp, "c": "ink", "w": 3.4,
             "d": f"M{x - 40},{y} L{x},{y - 220} L{x + 40},{y} M{x - 26},{y - 70} L{x + 26},{y - 70} M{x - 14},{y - 140} L{x + 14},{y - 140} "
                  f"M{x - 60},{y - 180} L{x + 60},{y - 180}"}]


def house(x, y, w, at, c="ink", idp=None):
    e = {"t": "path", "at": at, "c": c, "w": 3.4, "d": f"M{x},{y} L{x},{y - w * 0.7} L{x + w / 2},{y - w * 1.15} L{x + w},{y - w * 0.7} L{x + w},{y} Z"}
    if idp:
        e["id"] = idp
    return [e]


def button(x, y, at, text="重试", s=36, c="red"):
    return [{"t": "rect", "at": at, "x": x - 80, "y": y - 36, "w": 160, "h": 64, "c": c}, txt(x, y + 12, s, text, at, c=c)]


B = []
# 0-1 · 8:11，转圈圈；5 小时
els = [{"t": "icon", "at": 0, "name": "phone", "x": 620, "y": 560, "size": 620, "c": "ink"}]
els += spinner(620, 540, 80, 0, "sp0")
els += [txt(620, 240, 44, "8:11", 0, c="muted", font="en"),
        txt(1350, 560, 160, "5 小时", 1, c="red"), txt(1350, 680, 40, "（还在转）", 1, c="muted")]
B.append(els)
# 2 · 九月三号，三家同一天；宕机天气预报
els = []
for i, name in enumerate(("ChatGPT", "Claude", "Grok")):
    x = 420 + i * 420
    els += spinner(x, 420, 70, 2, f"sp1_{i}", c=("blue", "gold", "red")[i])
    els += [txt(x, 560, 44, name, 2, font="en")]
els += [txt(840, 220, 48, "9 月 3 日 · 同一天", 2, c="muted"),
        {"t": "icon", "at": 2, "name": "cloud", "x": 1620, "y": 420, "size": 260, "c": "muted"},
        txt(1620, 640, 40, "AI 天气预报：", 2, c="blue"), txt(1620, 700, 40, "多云转圈圈", 2, c="blue")]
B.append(els)
# 3 · 有钱有天才，为什么还老崩？
els = [txt(400, 360, 110, "¥¥¥", 3, c="gold", font="en"), txt(400, 470, 40, "有钱", 3)]
for i in range(3):
    els += stick(780 + i * 130, 560, 0.8, 3)
els += [txt(910, 640, 40, "有天才", 3),
        {"t": "icon", "at": 3, "id": "q3", "name": "question", "x": 1480, "y": 420, "size": 360, "c": "red"},
        txt(1480, 760, 60, "为什么还老崩？", 3, c="red"), {"t": "move", "at": 3, "kind": "pulse", "targets": ["q3"]}]
B.append(els)
# 4 · 一句话 → 小块 → 显卡机器 → 一个字一个字
els = bubble(120, 260, 300, 110, 4, "你好，请问…", s=40)
els += [{"t": "rect", "at": 4, "x": 500 + i * 56, "y": 300, "w": 44, "h": 44, "c": "blue", "fill": "blue"} for i in range(5)]
els += [txt(610, 400, 32, "拆成小块", 4, c="blue"),
        {"t": "line", "at": 4, "id": "pipe", "pts": [[800, 322], [1000, 322]], "c": "muted", "w": 3},
        {"t": "move", "at": 4, "kind": "signal", "targets": ["pipe"], "speed": 260},
        {"t": "rect", "at": 4, "x": 1010, "y": 180, "w": 420, "h": 560, "c": "ink"}]
els += xiaoka(1220, 330, 0.9, 4, idp="k4")
els += xiaoka(1220, 590, 0.9, 4, idp="k4b")
els += [txt(1220, 800, 36, "几千亿个参数", 4, c="muted")]
for i, ch in enumerate("答案是……"):
    els.append(txt(1520 + i * 60, 480, 52, ch, 4, c="green"))
B.append(els)
# 5 · 一次只能接待这么多人；排不下就转圈圈
els = xiaoka(360, 520, 1.3, 5, idp="k5", mood="tired", sweat=True)
for i in range(7):
    els += stick(700 + i * 150, 760, 0.7, 5)
els += spinner(1780, 520, 60, 5, "sp5")
els += [txt(1100, 880, 40, "人多了排队，排不下 →", 5, c="muted"), txt(1780, 660, 36, "转圈圈", 5, c="blue")]
B.append(els)
# 6 · 原因一：算力不够；20 个；峰谷价格
els = [txt(960, 240, 72, "原因一：算力不够", 6, c="red"),
       txt(520, 470, 110, "20", 6, c="blue", font="en"), txt(520, 560, 38, "每个账号最多同时问", 6),
       {"t": "icon", "at": 6, "name": "sun", "x": 1240, "y": 480, "size": 200, "c": "gold"}, txt(1240, 650, 44, "白天贵", 6, c="red"),
       {"t": "icon", "at": 6, "name": "moon", "x": 1600, "y": 480, "size": 180, "c": "blue"}, txt(1600, 650, 44, "半夜便宜", 6, c="green"),
       txt(1420, 780, 40, "峰谷价格", 6, c="muted")]
B.append(els)
# 7-8 · 峰谷价格？我们见过；1882 爱迪生电站
els = [txt(960, 200, 60, "峰谷价格？这个我们见过……", 7, c="muted")]
els += house(380, 760, 300, 8, idp="plant") + [{"t": "rect", "at": 8, "id": "plant", "x": 600, "y": 380, "w": 50, "h": 180, "c": "ink"},
        {"t": "path", "at": 8, "id": "bolt", "c": "gold", "w": 4, "d": "M520,520 L480,610 L530,610 L490,700"},
        txt(530, 840, 40, "1882 · 第一座电站", 8)]
for i in range(3):
    els += house(1000 + i * 260, 760, 180, 8)
els += [{"t": "line", "at": 8, "id": "wire", "pts": [[680, 400], [1660, 400]], "c": "muted", "w": 3},
        {"t": "move", "at": 8, "kind": "signal", "targets": ["wire"], "speed": 500},
        txt(1350, 840, 40, "只管周围几条街", 8, c="muted"),
        {"t": "line", "at": 8, "pts": [[360, 380], [720, 780]], "c": "red", "w": 6},
        {"t": "line", "at": 8, "pts": [[720, 380], [360, 780]], "c": "red", "w": 6},
        txt(1350, 960, 44, "电站一出事，这几条街就黑", 8, c="red")]
B.append(els)
# 9-10 · 连成电网；1965 一个开关跳了，连锁倒
els = []
for i in range(6):
    els += pylon(260 + i * 280, 780, 9, f"py{i}")
els += [{"t": "line", "at": 9, "pts": [[200, 600], [1720, 600]], "c": "muted", "w": 3},
        txt(960, 220, 56, "电站连成电网", 9, c="blue"),
        {"t": "path", "at": 10, "id": "spark", "c": "red", "w": 5, "d": "M230,540 L270,500 L250,490 L300,440"},
        {"t": "move", "at": 10, "kind": "pulse", "targets": ["spark"]},
        txt(960, 920, 52, "1965 · 3000 万人 · 十几个小时", 10, c="red")]
for i in range(6):
    els.append({"t": "move", "at": 10, "kind": "rotate", "targets": [f"py{i}"], "pivot": [300 + i * 280, 780], "to": 70, "dur": 0.6, "delay": 2.2 + i * 0.45})
B.append(els)
# 11 · 2003 报警软件有 bug，值班的人没收到
els = [{"t": "icon", "at": 11, "name": "computer", "x": 620, "y": 480, "size": 480, "c": "ink"},
       {"t": "ellipse", "at": 11, "x": 580, "y": 430, "w": 80, "h": 60, "c": "red", "fill": "red"},
       {"t": "path", "at": 11, "c": "red", "w": 3, "d": "M590,440 L560,420 M590,480 L560,500 M650,440 L680,420 M650,480 L680,500 M620,430 L600,400 M620,430 L640,400"},
       txt(620, 380, 34, "bug", 11, c="red", font="en")]
els += stick(1240, 800, 1.2, 11, idp="guard")
els += [txt(1360, 470, 60, "z z z", 11, c="blue", font="en"),
        txt(960, 950, 52, "2003 · 警报没响 · 5000 万人停电", 11, c="red")]
B.append(els)
# 12 · 原因二：牵一发动全身；路由读错一条配置
els = [txt(960, 220, 72, "原因二：牵一发动全身", 12, c="red"),
       {"t": "rect", "at": 12, "x": 200, "y": 380, "w": 420, "h": 380, "c": "ink"}]
els += [{"t": "line", "at": 12, "pts": [[240, 440 + 50 * i], [560, 440 + 50 * i]], "c": "red" if i == 3 else "muted", "w": 5 if i == 3 else 2} for i in range(6)]
els += [txt(410, 830, 36, "一条配置改错", 12, c="red"), {"t": "arrow", "at": 12, "pts": [[660, 560], [800, 560]], "c": "red", "w": 4}]
for i in range(5):
    els += xiaoka(980 + i * 190, 560, 0.55, 12, idp=f"d{i}", mood="o", moves=False)
    els.append({"t": "move", "at": 12, "kind": "rotate", "targets": [f"d{i}*"], "pivot": [1060 + i * 190, 610], "to": 80, "dur": 0.5, "delay": 2.5 + i * 0.35})
els += [txt(1360, 860, 36, "OpenAI · 9 月 · 路由读错配置", 12, c="muted")]
B.append(els)
# 13 · 原因三：恢复比崩溃难；几百 GB 搬回显卡
els = [txt(960, 200, 64, "原因三：恢复比崩溃还难", 13, c="red")]
els += xiaoka(1300, 560, 1.4, 13, idp="k13", mood="tired", sweat=True)
for i in range(4):
    els += [{"t": "rect", "at": 13, "id": "box", "x": 260 + i * 120, "y": 480 + (i % 2) * 70, "w": 100, "h": 80, "c": "gold"}]
els += [txt(470, 680, 36, "几百 GB 参数", 13, c="gold"),
        {"t": "arrow", "at": 13, "pts": [[760, 540], [1060, 540]], "c": "ink", "w": 4},
        {"t": "move", "at": 13, "kind": "shift", "targets": ["box"], "dx": 380, "dy": 0, "dur": 3, "delay": 3},
        {"t": "rect", "at": 13, "x": 1060, "y": 820, "w": 480, "h": 50, "c": "ink"},
        {"t": "rect", "at": 13, "x": 1060, "y": 820, "w": 130, "h": 50, "c": "green", "fill": "green"},
        txt(1300, 930, 36, "预热中……一点一点放人", 13, c="muted")]
B.append(els)
# 14-15 · 疯狂点重试；冷负荷启动
els = []
for i, (x, y) in enumerate([(300, 300), (620, 420), (420, 620), (820, 260), (900, 640), (250, 860), (700, 860)]):
    els += button(x, y, 14)

els += [txt(560, 1000, 40, "所有人都在点", 14, c="muted"),
        {"t": "rect", "at": 15, "x": 1180, "y": 300, "w": 220, "h": 420, "c": "ink"},
        {"t": "line", "at": 15, "pts": [[1180, 470], [1400, 470]], "c": "ink", "w": 3},
        {"t": "rect", "at": 15, "x": 1480, "y": 300, "w": 300, "h": 120, "c": "ink"},
        {"t": "line", "at": 15, "pts": [[1500, 390], [1760, 390]], "c": "ink", "w": 3},
        txt(1290, 790, 34, "冰箱", 15, c="muted"), txt(1630, 470, 34, "空调", 15, c="muted"),
        {"t": "path", "at": 15, "id": "boom", "c": "red", "w": 6, "d": "M1560,560 L1500,680 L1580,680 L1520,820"},
        txt(1640, 720, 64, "砰！", 15, c="red", align="left"),
        txt(1480, 950, 48, "冷负荷启动", 15, c="blue"), {"t": "move", "at": 15, "kind": "pulse", "targets": ["boom"]}]
B.append(els)
# 16-18 · 四条老规矩：留余量；N-1
els = [txt(960, 200, 64, "抄作业：电力的四条老规矩", 16, c="green"),
       txt(480, 340, 52, "一 · 留余量", 17, c="blue")]
els += xiaoka(380, 560, 0.8, 17, idp="k17")
els += xiaoka(640, 560, 0.8, 17, idp="k17b", moves=False)
els += [txt(640, 720, 36, "备用", 17, c="muted"),
        txt(1420, 340, 52, "二 · N 减 1", 18, c="blue")]
for i in range(4):
    els += xiaoka(1140 + i * 190, 560, 0.55, 18, idp=f"n{i}", moves=False)
els += [{"t": "line", "at": 18, "pts": [[1250, 500], [1370, 620]], "c": "red", "w": 6}, {"t": "line", "at": 18, "pts": [[1370, 500], [1250, 620]], "c": "red", "w": 6},
        {"t": "icon", "at": 18, "name": "check", "x": 1420, "y": 790, "size": 140, "c": "green"},
        txt(1420, 930, 40, "坏一个，照常运转", 18, c="green")]
B.append(els)
# 19-20 · 宁可限电不要全黑；灰度发布
els = [txt(480, 220, 52, "三 · 宁可限电，不要全黑", 19, c="blue")]
for i in range(5):
    els += stick(200 + i * 120, 640, 0.6, 19)
els += [{"t": "rect", "at": 19, "x": 760, "y": 360, "w": 200, "h": 110, "c": "gold"}, txt(860, 420, 30, "请稍候", 19, c="gold"),
        txt(560, 760, 34, "先排队，不一起转圈圈", 19, c="muted"),
        txt(1440, 220, 52, "四 · 先在小区试", 20, c="blue")]
els += house(1120, 640, 140, 20, c="green")
els += [txt(1190, 700, 32, "5% 流量", 20, c="green"), {"t": "arrow", "at": 20, "pts": [[1300, 560], [1440, 560]], "c": "ink", "w": 4}]
for i in range(4):
    els.append({"t": "icon", "at": 20, "name": "building", "x": 1540 + i * 100, "y": 560, "size": 150, "c": "ink"})
els += [txt(1690, 700, 32, "再全城", 20), txt(1440, 840, 44, "灰度发布", 20, c="green")]
B.append(els)
# 21-22 · AI 会像电一样；停摆像停电
els = [txt(960, 300, 120, "AI ≈ 电", 21, c="blue"),
       txt(960, 440, 40, "谁都离不开，谁也看不见", 21, c="muted"),
       {"t": "rect", "at": 22, "x": 560, "y": 560, "w": 800, "h": 360, "c": "ink"},
       txt(960, 640, 48, "今日头条", 22, c="ink"),
       {"t": "line", "at": 22, "pts": [[600, 670], [1320, 670]], "c": "ink", "w": 2},
       txt(960, 760, 52, "AI 停摆 · 追责 · 赔钱", 22, c="red"),
       txt(960, 860, 32, "（就像停电一样）", 22, c="muted")]
B.append(els)
# 23 · 赔了一周的钱；去泡杯茶
els = xiaoka(760, 560, 1.6, 23, idp="k23")
els += [{"t": "path", "at": 23, "c": "ink", "w": 4, "d": "M1240,620 L1260,800 L1400,800 L1420,620 Z M1420,660 Q1480,680 1420,740"},
        {"t": "path", "at": 23, "id": "steam", "c": "muted", "w": 3, "d": "M1290,600 Q1270,560 1290,520 Q1310,480 1290,440 M1350,600 Q1330,560 1350,520 Q1370,480 1350,440"},
        {"t": "move", "at": 23, "kind": "bob", "targets": ["steam"], "amp": 12, "hz": 0.8},
        txt(960, 240, 52, "已赔：一周的钱", 23, c="green"),
        txt(1330, 920, 44, "先去泡杯茶", 23, c="gold")]
B.append(els)
boards = [{"elements": e} for e in B]

bad = missing_chars("".join(e.get("text", "") for b in B for e in b))
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
PAUSE = {0: 0.9, 1: 0.7, 2: 0.4, 7: 0.4, 11: 0.5, 14: 0.4, 15: 0.5, 22: 0.5}
for i, zh in enumerate(SEG):
    spoken = zh
    for a_, b_ in SAY.items():
        spoken = spoken.replace(a_, b_)
    a = tts.generate(speakable(spoken), sid=49, speed=1.12); sr = a.sample_rate; x = np.array(a.samples, dtype=np.float32)
    if not parts: parts.append(np.zeros(int(sr * 0.4), np.float32))
    segs.append({"zh": zh, "t0": round(t, 2), "t1": round(t + len(x) / sr, 2)})
    gap = PAUSE.get(i, 0.25)
    parts += [x, np.zeros(int(sr * gap), np.float32)]; t += len(x) / sr + gap
parts.append(np.zeros(int(sr * 1.2), np.float32)); t += 1.2
sf.write(here / "配音.wav", np.concatenate(parts), sr)
lesson = wai.to_lesson({"zh": "AI 为什么总“转圈圈”？", "en": "Why does AI keep spinning?"}, segs, boards, audio="配音.wav", duration=round(t, 2))
lesson["pace"], lesson["hand"] = 0.5, False
json.dump(lesson, open(here / "lesson.json", "w"), ensure_ascii=False, indent=1)
print(len(segs), "segments", len(boards), "boards", round(t, 1), "s")
