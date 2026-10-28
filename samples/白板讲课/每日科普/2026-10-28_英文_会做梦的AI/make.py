"""Daily science short 2026-10-28 (English): "This AI Dreams Up Worlds. Then It Forgets."
News: Google DeepMind announced Genie 4, a real-time "world model", on Oct 27, 2026 (research preview).
Trending: TechCrunch AI front page Oct 27; covered by MarkTechPost, The AI Insider, Unite.AI (Oct 27-28); newscord lists 10 outlets.
Facts used:
- TechCrunch 2026-10-27 https://techcrunch.com/2026/10/27/googles-genie-4-world-model-adds-audio-more-realistic-worlds-and-real-time-steering/ :
  generates interactive worlds users change while they run; real-time audio (music, ambient noise, dialogue); type prompts mid-simulation
  (weather, camera, add people/objects); keeps a scene consistent for up to two minutes, double Genie 3; research preview for trusted
  testers, rolling out in coming weeks to Google AI Ultra subscribers (Project Genie) and Gemini API / AI Studio early-access partners;
  Gemini breaks robot tasks into steps that Genie 4 simulates; details drift the longer it runs; audio accuracy and legible text unsolved.
- Google DeepMind blog https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation/ : first real-time world model with
  native audio; object permanence can drift in longer runs, after many edits or while navigating; complex physics, text, spatial accuracy,
  long-term consistency are active research; all output carries SynthID watermarks; training environments for robots and agents.
- General: world models of this kind predict the next frame from recent frames and the user's input (autoregressive video generation);
  they learn regularities from video rather than running a physics engine; errors compound over long runs.
Speculation / opinion: "a robot that trusts a bad dream learns bad moves" is said as our worry, not a finding. The cost argument for
memory (more frames to look back at) is a simplified explanation. Analogies: flipbook artist; telephone game. Running gag: "it hopes you
won't check" -> "just like me when I say I remember your name".
    python3 make.py <kokoro model dir> | --boards-only | --fake   then  WB_CRF=17 python3 ../../../../tools/whiteboard/wb.py . --mp4"""
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.path.insert(0, str(here.parents[1]))
from fastkit import (BIG, O, P, R, T, arr, bar, bob, check, cross, main, pop, pulse, rot, sh, spin,  # noqa: E402
                     star, uid, wig)

S = [
 ("谷歌造了一个AI，能凭空“梦”出一个你能走进去的世界。|可你转身太久，这个世界就忘了。", "Google built an AI that dreams up a world you can walk around in. | But turn around too long, and the world forgets."),
 ("它叫Genie 4，|10月27号发布。", "It's called Genie four. | It was announced on October twenty seventh."),
 ("打一句话，它就画出一个世界，|有声音、有天气，还有会搭话的人。", "Type a sentence, and it paints a world, | with sound, weather, and people who talk back."),
 ("每一帧画面和声音，|都打了看不见的水印。", "Every picture and sound it makes | carries an invisible watermark."),
 ("今天的烧脑问题：它不是游戏引擎，|它怎么知道下一秒该是什么样？", "Today's brain-teaser: it's not a game engine, | so how does it know what comes next?"),
 ("先说个秘密：它里面没有地图，|没有墙，也没有物理公式。", "First, a secret: there's no map inside. | No walls. No physics code."),
 ("普通游戏把一切都存着：|树在哪，箱子多重。", "A normal video game stores everything: | where the tree is, how heavy the box is."),
 ("Genie什么都不存，|它只猜下一张画面。", "Genie stores nothing like that. | It just guesses the next picture."),
 ("猜完一张，再猜下一张，|一秒钟猜很多张。", "Then it guesses the next one, | and the next, many times a second."),
 ("就像一个画翻页小人书的画家，|每页都照着前几页画。", "It's like a flip book artist | drawing each page by looking at the last few."),
 ("那它怎么知道球会往下掉？|因为它看过海量的视频。", "So how does it know a ball falls down? | It watched a huge amount of video."),
 ("看多了，往下掉就显得正常，|飘在空中就显得不对劲。", "After enough video, falling looks normal, | and floating looks wrong."),
 ("反转一：|没有人教过它重力。", "Twist one: | nobody taught it gravity."),
 ("它的物理是习惯，不是定律，|就像小娃娃知道杯子会掉，却不知道为什么。", "Its physics is a habit, not a law. | Like a toddler who knows cups fall, but not why."),
 ("反转二，最反直觉：|最难的不是画，是记性。", "Twist two, the weird one: | the hard part isn't drawing. It's memory."),
 ("想让世界保持一致，|它得回头翻已经画过的页。", "To keep the world the same, | it has to look back at pages it already drew."),
 ("多记一秒，每画一页|就要多翻好多页。", "Every extra second it remembers | means more pages to check, for every new page."),
 ("所以记性是按分钟算的，|不是按小时。", "That's why its memory is measured in minutes, | not hours."),
 ("Genie 4能让一个场景保持一致最多两分钟，|大约是Genie 3的两倍。", "Genie four keeps a scene consistent for up to two minutes, | about double Genie three."),
 ("再久一点，细节就会漂：|你身后的树，可能悄悄挪了地方。", "After that, details can drift: | the tree behind you might quietly move."),
 ("这就像传话游戏：|每传一次，就错一点点。", "It's the telephone game: | every copy of a copy gets a little more wrong."),
 ("谷歌自己也说，物体会漂，|尤其是跑得久、改得多的时候。", "Google itself says objects can drift, | especially in long runs and after lots of edits."),
 ("而且你可以边玩边改：|打一句“下雨”，就下雨了。", "And you can edit while you play: | type make it rain, and it rains."),
 ("反转三：|最大的用户，可能是机器人。", "Twist three: | the biggest customer might be robots."),
 ("在真实世界里训练机器人很慢，|摔坏一台还很贵。", "Training a robot in the real world is slow, | and broken robots are expensive."),
 ("在梦里，机器人可以把杯子摔一千次，|一分钱不花。", "In a dream world, a robot can drop a cup | a thousand times for free."),
 ("谷歌试过：Gemini把机器人的任务拆成几步，|Genie 4当场把每一步演出来。", "In one Google test, Gemini split a robot task into steps, | and Genie four acted out each step on the spot."),
 ("上面一个会计划的，|下面一个会做梦的。", "A planner on top, | a dreamer underneath."),
 ("友情提示：现在只是研究预览，|只给受邀测试者用。", "Fine print: it's a research preview, | only for invited testers right now."),
 ("谷歌说，接下来几周|会开放给部分付费用户和开发者。", "Google says that in the coming weeks | it opens to some paid subscribers and developers."),
 ("世界里的文字、声音准不准、复杂的物理，|都还在研究。", "Writing inside the world, accurate sound, and tricky physics | are all still being worked on."),
 ("我们的担心是：机器人要是信了一个错的梦，|可能学会错的动作。", "Our worry, not a finding: a robot that trusts a bad dream | might learn bad moves."),
 ("所以它怎么知道下一秒？|它不知道，它只是猜得非常非常好。", "So how does it know what comes next? | It doesn't. It just guesses really, really well."),
 ("而你转身的时候，|它只盼着你别回头检查。", "And when you turn around, | it's hoping you won't check."),
 ("就像我说“我记得你的名字”的时候，|一样。", "Just like me | when I say I remember your name."),
]
TITLE = {"zh": "会做梦的AI，为什么记不住？", "en": "This AI Dreams Up Worlds. Then It Forgets."}

B = []


def bd(a, *parts):
    E = []
    for p in parts:
        E += p
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


def dreamy(a, x, y, k=1.0, d=0.0, mood="sleepy"):
    """Dreamy, the world model: a puffy cloud with a face and a nightcap; floats, and its z's drift up."""
    i, cp, z = uid("dr"), uid("drc"), uid("drz")
    eyes = {"sleepy": f"M{x - 55 * k},{y} Q{x - 40 * k},{y + 12 * k} {x - 25 * k},{y} M{x + 25 * k},{y} Q{x + 40 * k},{y + 12 * k} {x + 55 * k},{y}",
            "awake": f"M{x - 75 * k},{y + 22 * k} L{x - 58 * k},{y + 22 * k} M{x + 58 * k},{y + 22 * k} L{x + 75 * k},{y + 22 * k}",
            "o": f"M{x - 55 * k},{y} Q{x - 40 * k},{y - 14 * k} {x - 25 * k},{y} M{x + 25 * k},{y} Q{x + 40 * k},{y - 14 * k} {x + 55 * k},{y}"}[mood]
    mouth = f"M{x - 20 * k},{y + 35 * k} Q{x},{y + 50 * k} {x + 20 * k},{y + 35 * k}" if mood != "o" else f"M{x - 10 * k},{y + 40 * k} a10,10 0 1,0 20,0 a10,10 0 1,0 -20,0"
    E = [E_(a, x - 90 * k, y + 20 * k, 160 * k, 120 * k, c="ink", fill="blue", idp=i), E_(a, x + 90 * k, y + 20 * k, 160 * k, 120 * k, c="ink", fill="blue", idp=i),
         E_(a, x, y - 10 * k, 220 * k, 170 * k, c="ink", fill="blue", idp=i),
         P(a, eyes, c="ink", w=5, idp=i), P(a, mouth, c="ink", w=4, idp=i),
         *([O(a, x - 40 * k, y - 5 * k, 11 * k, c="ink", fill="ink", idp=i), O(a, x + 40 * k, y - 5 * k, 11 * k, c="ink", fill="ink", idp=i)] if mood == "awake" else []),
         P(a, f"M{x - 60 * k},{y - 85 * k} L{x + 40 * k},{y - 180 * k} L{x + 60 * k},{y - 80 * k} L{x - 60 * k},{y - 85 * k}", c="ink", w=4, idp=cp),
         O(a, x + 40 * k, y - 185 * k, 14 * k, c="ink", fill="gold", idp=cp),
         pop(a, [i, cp], d), bob(a, i, 9 * k, 0.8), bob(a, cp, 9 * k, 0.8), wig(a, cp, (x, y - 85 * k), 8, 1.4)]
    if mood == "sleepy":
        E += [P(a, f"M{x + 140 * k},{y - 120 * k} L{x + 170 * k},{y - 120 * k} L{x + 140 * k},{y - 90 * k} L{x + 170 * k},{y - 90 * k}", c="ink", w=4, idp=z),
              pop(a, z, d + 0.3), sh(a, z, 40, -60, d + 0.5, 1.6)]
    return E, [i, cp]


def walker(a, x, y, k=1.0, d=0.0, walk=0):
    """A stick explorer whose legs and arms swing; walk = how far it walks."""
    i, lg = uid("wk"), uid("wkl")
    E = [O(a, x, y - 210 * k, 40 * k, c="ink", fill="paper", idp=i),
         P(a, f"M{x},{y - 170 * k} L{x},{y - 30 * k} M{x - 60 * k},{y - 120 * k} L{x},{y - 140 * k} L{x + 60 * k},{y - 110 * k}", c="ink", w=7, idp=i),
         P(a, f"M{x},{y - 30 * k} L{x - 45 * k},{y + 80 * k} M{x},{y - 30 * k} L{x + 45 * k},{y + 80 * k}", c="ink", w=7, idp=lg),
         O(a, x + 12 * k, y - 215 * k, 5 * k, c="ink", fill="ink", idp=i),
         pop(a, [i, lg], d), wig(a, lg, (x, y - 30 * k), 18, 2.4), bob(a, i, 5 * k, 2.4)]
    if walk:
        E.append(sh(a, [i, lg], walk, 0, d + 0.3, 1.6))
    return E, [i, lg]


def tree(a, x, y, k=1.0, d=0.0, c="green"):
    i = uid("tr")
    return [R(a, x - 18 * k, y - 120 * k, 36 * k, 120 * k, c="ink", fill="gold", idp=i), O(a, x, y - 180 * k, 90 * k, c="ink", fill=c, idp=i),
            pop(a, i, d), wig(a, i, (x, y), 3, 0.9)], i


def robot(a, x, y, k=1.0, d=0.0, mood="happy"):
    """A little robot: box head, antenna that spins, arms that wave."""
    i, an, ar = uid("rb"), uid("rba"), uid("rbr")
    m = (f"M{x - 25 * k},{y - 120 * k} Q{x},{y - 100 * k} {x + 25 * k},{y - 120 * k}" if mood == "happy"
         else f"M{x - 25 * k},{y - 105 * k} Q{x},{y - 125 * k} {x + 25 * k},{y - 105 * k}")
    E = [R(a, x - 80 * k, y - 210 * k, 160 * k, 130 * k, c="ink", fill="muted", idp=i), R(a, x - 70 * k, y - 70 * k, 140 * k, 150 * k, c="ink", fill="gold", idp=i),
         O(a, x - 35 * k, y - 160 * k, 14 * k, c="ink", fill="blue", idp=i), O(a, x + 35 * k, y - 160 * k, 14 * k, c="ink", fill="blue", idp=i), P(a, m, c="ink", w=4, idp=i),
         P(a, f"M{x},{y - 210 * k} L{x},{y - 260 * k} M{x - 25 * k},{y - 260 * k} L{x + 25 * k},{y - 260 * k}", c="red", w=5, idp=an),
         P(a, f"M{x - 70 * k},{y - 40 * k} L{x - 140 * k},{y + 20 * k} M{x + 70 * k},{y - 40 * k} L{x + 140 * k},{y - 80 * k}", c="ink", w=7, idp=ar),
         pop(a, [i, an, ar], d), bob(a, i, 6 * k, 1.1), bob(a, an, 6 * k, 1.1), spin(a, an, (x, y - 260 * k), 80), wig(a, ar, (x, y - 40 * k), 12, 1.8)]
    return E, [i, an, ar]


def pages(a, x, y, n=5, d=0.0, w=160, h=200, gap=60, flip=True):
    """A flip book: pages pop in one after another, then slide."""
    E = []
    for q in range(n):
        i = uid("pg")
        E += [R(a, x + gap * q, y - 10 * q, w, h, c="ink", fill="paper", idp=i, sw=4), pop(a, i, d + 0.12 * q)]
        if flip:
            E.append(sh(a, i, 0, -30, d + 0.7 + 0.08 * q, 0.4))
    return E


def ball(a, x, y, d=0.0, drop=350, c="red"):
    i = uid("ba")
    return [O(a, x, y, 40, c="ink", fill=c, idp=i), pop(a, i, d), sh(a, i, 0, drop, d + 0.3, 0.7)]


def cup(a, x, y, d=0.0, drop=300):
    i = uid("cu")
    return [P(a, f"M{x - 50},{y - 60} L{x - 35},{y + 60} L{x + 35},{y + 60} L{x + 50},{y - 60} L{x - 50},{y - 60}", c="ink", w=5, idp=i),
            pop(a, i, d), sh(a, i, 0, drop, d + 0.3, 0.6), rot(a, i, 120, (x, y), d + 0.3, 0.6)]


def rain(a, x0, x1, y, d=0.0, n=8):
    E = []
    for q in range(n):
        i = uid("rn")
        x = x0 + (x1 - x0) * q / (n - 1)
        E += [P(a, f"M{x},{y + 30 * (q % 3)} L{x - 15},{y + 60 + 30 * (q % 3)}", c="blue", w=5, idp=i), pop(a, i, d + 0.05 * q), sh(a, i, -20, 200, d + 0.2 + 0.05 * q, 0.9)]
    return E


def screen(a, x, y, w=420, h=280, d=0.0, c="ink"):
    i = uid("sc")
    return [R(a, x - w / 2, y - h / 2, w, h, c=c, idp=i, sw=6), pop(a, i, d), pulse(a, i, d + 0.6)]


# 0 dreams a world / forgets
dm, did = dreamy(0, 500, 450, 1.1, mood="awake")
t1, tid = tree(0, 1250, 650, 1.1, 0.3)
w1, wid = walker(0, 1550, 650, 0.9, 0.4)
bd(0, dm, t1, w1, arr(0, 760, 420, 1050, 420, c="blue", d=0.2))
t1, tid = tree(0.5, 600, 650, 1.1, 0.0)
w1, wid = walker(0.5, 1100, 650, 1.0, 0.1)
bd(0.5, t1, w1, [sh(0.5, wid, 200, 0, 0.2, 0.8), sh(0.5, tid, 300, 0, 0.9, 0.8)], ic(0.5, "question", 1600, 350, 160, 0.6, mv="wig", c="red"), BIG(0.5, 960, 320, "forgets!", c="red", d=0.8, s=90))
# 1 Genie 4, Oct 27
dm, did = dreamy(1, 650, 450, 1.3)
bd(1, dm, BIG(1, 1350, 400, "Genie 4", c="blue", d=0.3, s=150), T(1, 1350, 560, 56, "Google DeepMind", c="ink", d=0.5))
bd(1.5, BIG(1.5, 960, 380, "Oct 27", c="red", d=0.1, s=160), ic(1.5, "clock", 450, 450, 200, 0.2, mv="spin"), ic(1.5, "computer", 1500, 450, 200, 0.4, mv="bob"), arr(1.5, 600, 650, 1350, 650, c="blue", d=0.5))
# 2 type a sentence -> a world, sound, weather, talk
bx = uid("tb")
dm, did = dreamy(2, 1350, 420, 0.9, mood="awake")
bd(2, [R(2, 250, 380, 520, 110, c="ink", idp=bx, sw=5), pop(2, bx, 0.0)], T(2, 510, 450, 44, "a snowy forest...", c="ink", d=0.2), arr(2, 800, 435, 1080, 435, c="blue", d=0.4), dm)
t1, _ = tree(2.5, 450, 650, 0.9, 0.0)
w1, _ = walker(2.5, 1350, 650, 0.9, 0.2)
bd(2.5, t1, w1, ic(2.5, "speaker", 800, 350, 150, 0.2, mv="wig"), ic(2.5, "cloud", 1000, 250, 160, 0.3, mv="bob"), rain(2.5, 850, 1150, 330, 0.4, 5), T(2.5, 1350, 300, 50, "hi there!", c="blue", d=0.6))
# 3 invisible watermark
bd(3, screen(3, 700, 450, 460, 300, 0.0), ic(3, "speaker", 1300, 450, 180, 0.2, mv="wig"), T(3, 960, 760, 64, "invisible watermark", c="blue", d=0.4), ic(3, "eye", 700, 450, 120, 0.3, mv="wig"))
bd(3.5, BIG(3.5, 960, 380, "SynthID", c="blue", d=0.1, s=140), ic(3.5, "magnifier", 500, 450, 200, 0.2, mv="wig"), check(3.5, 1500, 450, d=0.5), ic(3.5, "chip", 1500, 650, 120, 0.4, mv="spin"))
# 4 brain-teaser: not a game engine
bd(4, ic(4, "gear", 600, 450, 220, 0.0, mv="spin"), cross(4, 600, 450, d=0.4), T(4, 600, 650, 56, "game engine", c="ink", d=0.2), dreamy(4, 1300, 450, 1.0)[0])
bd(4.5, ic(4.5, "question", 960, 380, 280, 0.0, mv="wig", c="red"), BIG(4.5, 960, 720, "what comes next?", c="red", d=0.3, s=90), ic(4.5, "clock", 450, 450, 160, 0.2, mv="spin"), ic(4.5, "clock", 1470, 450, 160, 0.3, mv="spin"))
# 5 no map, no walls, no physics
dm, did = dreamy(5, 960, 450, 1.2, mood="o")
bd(5, dm, ic(5, "map_pin", 350, 400, 160, 0.2, mv="bob"), cross(5, 350, 400, d=0.4), BIG(5, 1550, 400, "secret", c="red", d=0.3, s=100))
wl = uid("wl")
bd(5.5, [R(5.5, 300, 300, 60, 350, c="ink", fill="muted", idp=wl), pop(5.5, wl, 0.0), wig(5.5, wl, (330, 650), 3, 1.0)], cross(5.5, 330, 470, d=0.2),
   T(5.5, 960, 470, 90, "F = ma", c="ink", d=0.3), cross(5.5, 960, 450, d=0.5), ic(5.5, "atom", 1550, 450, 180, 0.4, mv="spin"), cross(5.5, 1550, 450, d=0.7))
# 6 normal games store everything
t1, tid = tree(6, 600, 700, 1.0, 0.0)
bd(6, t1, ic(6, "map_pin", 600, 330, 120, 0.2, mv="bob", c="red"), T(6, 1200, 380, 50, "tree: x=600", c="blue", d=0.3), T(6, 1200, 480, 50, "box: 20 kg", c="blue", d=0.5), ic(6, "computer", 1500, 680, 160, 0.4, mv="bob"))
bxx = uid("bx")
bd(6.5, [R(6.5, 450, 500, 200, 200, c="ink", fill="gold", idp=bxx), pop(6.5, bxx, 0.0), sh(6.5, bxx, 0, 50, 0.4, 0.4)], ic(6.5, "ruler", 1000, 450, 180, 0.2, mv="wig"),
   BIG(6.5, 1450, 450, "stored", c="blue", d=0.3, s=110), check(6.5, 1450, 650, d=0.6))
# 7 Genie stores nothing, guesses next picture
dm, did = dreamy(7, 600, 450, 1.1)
bd(7, dm, BIG(7, 1350, 400, "stores", c="ink", d=0.2, s=100), BIG(7, 1350, 540, "nothing", c="red", d=0.4, s=100), cross(7, 1650, 470, d=0.6))
bd(7.5, screen(7.5, 600, 450, 380, 260, 0.0), arr(7.5, 830, 450, 1080, 450, c="blue", d=0.3), screen(7.5, 1320, 450, 380, 260, 0.4, c="blue"), ic(7.5, "question", 1320, 450, 120, 0.6, mv="wig", c="red"))
# 8 next and next
bd(8, pages(8, 400, 350, 6, 0.0), arr(8, 400, 700, 1300, 700, c="blue", d=0.5, dur=0.9), ic(8, "clock", 1550, 400, 180, 0.3, mv="spin"))
bd(8.5, pages(8.5, 350, 330, 9, 0.0, w=140, h=180, gap=110), BIG(8.5, 960, 750, "many per second", c="red", d=0.5, s=80))
# 9 flip book artist
w1, wid = walker(9, 450, 650, 1.0, 0.0)
bd(9, w1, pages(9, 800, 350, 5, 0.2), ic(9, "magnifier", 1550, 400, 160, 0.4, mv="wig"))
bd(9.5, pages(9.5, 500, 350, 4, 0.0, flip=False), arr(9.5, 1000, 450, 1250, 450, c="blue", d=0.5), screen(9.5, 1450, 450, 260, 220, 0.6, c="blue"), T(9.5, 800, 700, 56, "the last few pages", c="ink", d=0.3))
# 10 ball falls; watched video
bd(10, ball(10, 600, 300, 0.1), ball(10, 900, 300, 0.4, c="blue"), ic(10, "question", 1450, 400, 220, 0.2, mv="wig", c="red"), T(10, 750, 800, 56, "how does it know?", c="ink", d=0.6))
vs = []
for q in range(6):
    vs += screen(10.5, 380 + 230 * q, 350 + 60 * (q % 2), 200, 140, 0.08 * q)
bd(10.5, vs, BIG(10.5, 960, 700, "huge amounts of video", c="blue", d=0.5, s=80))
# 11 falling normal / floating wrong
bd(11, ball(11, 600, 300, 0.0), check(11, 600, 750, d=0.6), T(11, 600, 850, 50, "normal", c="green", d=0.6), ball(11, 1300, 450, 0.2, drop=-120, c="blue"), cross(11, 1300, 650, d=0.8))
bd(11.5, ic(11.5, "eye", 700, 450, 220, 0.0, mv="wig"), BIG(11.5, 1300, 380, "floating?", c="red", d=0.2, s=100), T(11.5, 1300, 550, 60, "looks wrong", c="red", d=0.4), ball(11.5, 1300, 700, 0.5, drop=-40, c="blue"))
# 12 twist one: no gravity lesson
bd(12, BIG(12, 960, 220, "Twist one", c="red", d=0.0, s=120), ic(12, "question", 600, 550, 200, 0.2, mv="wig", c="red"), ic(12, "question", 1320, 550, 200, 0.4, mv="wig", c="red"))
bd(12.5, ic(12.5, "globe", 600, 450, 240, 0.0, mv="spin"), T(12.5, 1250, 380, 80, "gravity", c="blue", d=0.2), cross(12.5, 1250, 380, d=0.5), T(12.5, 1250, 560, 56, "never taught", c="red", d=0.6))
# 13 habit not law; toddler
bd(13, T(13, 600, 400, 90, "habit", c="green", d=0.1), check(13, 600, 550, d=0.3), T(13, 1300, 400, 90, "law", c="ink", d=0.4), cross(13, 1300, 550, d=0.6))
tod = uid("td")
bd(13.5, [O(13.5, 600, 400, 80, c="ink", fill="paper", idp=tod), P(13.5, "M600,480 L600,650 M600,650 L550,750 M600,650 L650,750 M520,540 L680,540", c="ink", w=7, idp=tod),
           O(13.5, 575, 390, 8, c="ink", fill="ink", idp=tod), O(13.5, 625, 390, 8, c="ink", fill="ink", idp=tod), pop(13.5, tod, 0.0), bob(13.5, tod, 6, 1.4)],
   cup(13.5, 900, 450, 0.3), ic(13.5, "question", 1450, 450, 200, 0.6, mv="wig", c="red"), T(13.5, 1450, 700, 56, "but why?", c="red", d=0.8))
# 14 twist two: memory
bd(14, BIG(14, 960, 220, "Twist two", c="red", d=0.0, s=120), check(14, 650, 550, d=0.3), T(14, 650, 700, 60, "drawing", c="green", d=0.3), ic(14, "question", 1300, 550, 200, 0.5, mv="wig", c="red"))
dm, did = dreamy(14.5, 600, 450, 1.1, mood="o")
bd(14.5, dm, BIG(14.5, 1350, 450, "memory", c="red", d=0.3, s=130), ic(14.5, "chip", 1350, 650, 140, 0.5, mv="spin"))
# 15 look back at pages
bd(15, pages(15, 350, 380, 6, 0.0, flip=False), arr(15, 1200, 300, 500, 300, c="red", d=0.6, dur=0.7), dreamy(15, 1550, 500, 0.7, mood="awake")[0])
bd(15.5, pages(15.5, 400, 380, 5, 0.0), ic(15.5, "magnifier", 1300, 450, 220, 0.3, mv="wig"), T(15.5, 1300, 700, 56, "look back", c="blue", d=0.5))
# 16 more seconds -> more pages
bd(16, bar(16, 500, 780, 140, 120, "blue", d=0.0), bar(16, 750, 780, 140, 260, "blue", d=0.2), bar(16, 1000, 780, 140, 450, "red", d=0.4),
   T(16, 1400, 400, 60, "remember more", c="ink", d=0.3), ic(16, "clock", 1450, 600, 150, 0.4, mv="spin"))
bd(16.5, pages(16.5, 300, 350, 10, 0.0, w=120, h=160, gap=120), BIG(16.5, 960, 700, "every single page", c="red", d=0.6, s=80))
# 17 minutes not hours
bd(17, ic(17, "clock", 600, 450, 260, 0.0, mv="spin"), BIG(17, 1300, 380, "minutes", c="green", d=0.2, s=120), check(17, 1300, 560, d=0.4))
bd(17.5, ic(17.5, "clock", 600, 450, 260, 0.0, mv="spin", c="muted"), BIG(17.5, 1300, 380, "hours", c="ink", d=0.2, s=120), cross(17.5, 1300, 560, d=0.4), ic(17.5, "battery", 1600, 700, 120, 0.5, mv="wig"))
# 18 two minutes, double Genie 3
bd(18, BIG(18, 960, 380, "2 min", c="red", d=0.0, s=180), ic(18, "clock", 400, 450, 200, 0.2, mv="spin"), dreamy(18, 1550, 480, 0.6, mood="awake")[0])
bd(18.5, bar(18.5, 600, 780, 180, 220, "muted", d=0.0), bar(18.5, 950, 780, 180, 440, "blue", d=0.4), T(18.5, 690, 850, 50, "Genie 3", c="ink", d=0.1),
   T(18.5, 1040, 850, 50, "Genie 4", c="blue", d=0.5), BIG(18.5, 1450, 400, "x2", c="red", d=0.7, s=130))
# 19 the tree behind you moves
t1, tid = tree(19, 500, 700, 1.0, 0.0)
w1, wid = walker(19, 1100, 700, 1.0, 0.1)
bd(19, t1, w1, T(19, 960, 300, 70, "drift...", c="red", d=0.4), ic(19, "clock", 1550, 400, 150, 0.3, mv="spin"))
t1, tid = tree(19.5, 500, 700, 1.0, 0.0)
w1, wid = walker(19.5, 1200, 700, 1.0, 0.0)
gh = uid("gh")
bd(19.5, t1, w1, [sh(19.5, tid, 350, 0, 0.3, 1.2), O(19.5, 500, 520, 90, c="muted", idp=gh, sw=3), pop(19.5, gh, 0.2)], ic(19.5, "question", 1550, 350, 160, 0.6, mv="wig", c="red"))
# 20 telephone game
ps = []
for q in range(4):
    ps += walker(20, 400 + 370 * q, 680, 0.8, 0.1 * q)[0]
bd(20, ps, arr(20, 450, 300, 1500, 300, c="blue", d=0.3, dur=1.0), T(20, 450, 220, 56, "cat", c="ink", d=0.1), T(20, 1500, 220, 56, "hat?", c="red", d=0.8))
bd(20.5, pages(20.5, 350, 380, 5, 0.0, flip=False), arr(20.5, 400, 700, 1300, 700, c="red", d=0.3, dur=0.9), T(20.5, 1550, 450, 60, "a bit wrong", c="red", d=0.6), ic(20.5, "sine", 1550, 650, 140, 0.5, mv="wig"))
# 21 Google says drift
bd(21, ic(21, "building", 600, 450, 240, 0.0, mv="bob"), ic(21, "speaker", 1000, 420, 160, 0.2, mv="wig"), T(21, 1450, 420, 64, "objects drift", c="red", d=0.4))
bd(21.5, bar(21.5, 500, 780, 150, 150, "blue", d=0.0), bar(21.5, 750, 780, 150, 300, "blue", d=0.2), bar(21.5, 1000, 780, 150, 470, "red", d=0.4),
   T(21.5, 1450, 400, 56, "long runs", c="ink", d=0.3), T(21.5, 1450, 520, 56, "many edits", c="ink", d=0.5), ic(21.5, "clock", 1450, 680, 120, 0.6, mv="spin"))
# 22 make it rain
bx = uid("tb")
bd(22, [R(22, 300, 400, 600, 110, c="ink", idp=bx, sw=5), pop(22, bx, 0.0)], T(22, 600, 470, 50, "make it rain", c="blue", d=0.3), arr(22, 950, 455, 1200, 455, c="blue", d=0.5), ic(22, "cloud", 1450, 450, 220, 0.4, mv="bob"))
w1, wid = walker(22.5, 960, 750, 1.0, 0.0)
bd(22.5, ic(22.5, "cloud", 700, 250, 200, 0.0, mv="bob"), ic(22.5, "cloud", 1200, 250, 200, 0.1, mv="bob"), rain(22.5, 550, 1350, 350, 0.2, 9), w1)
# 23 twist three: robots
bd(23, BIG(23, 960, 220, "Twist three", c="red", d=0.0, s=120), robot(23, 960, 700, 1.0, 0.3)[0])
r1, rid = robot(23.5, 600, 700, 1.1)
bd(23.5, r1, BIG(23.5, 1350, 400, "customer #1?", c="red", d=0.3, s=90), dreamy(23.5, 1350, 650, 0.6)[0])
# 24 real-world training slow, expensive
r1, rid = robot(24, 600, 700, 1.0)
bd(24, r1, ic(24, "clock", 1200, 400, 200, 0.2, mv="spin"), T(24, 1200, 650, 60, "slow", c="ink", d=0.4), [sh(24, rid, 0, 0, 0, 0.1)][:0])
r1, rid = robot(24.5, 600, 650, 1.0, mood="sad")
bd(24.5, r1, [rot(24.5, rid, 80, (600, 730), 0.3, 0.6)], BIG(24.5, 1350, 400, "$$$", c="green", d=0.5, s=150), ic(24.5, "flame", 900, 700, 120, 0.7, mv="wig", c="red"))
# 25 drop a cup 1000 times
dm, did = dreamy(25, 1450, 350, 0.8)
r1, rid = robot(25, 600, 700, 1.0)
bd(25, dm, r1, cup(25, 800, 450, 0.3, 250), T(25, 1450, 650, 56, "in a dream", c="blue", d=0.5))
cs = []
for q in range(6):
    cs += cup(25.5, 400 + 220 * q, 330, 0.1 * q, 300)
bd(25.5, cs, BIG(25.5, 960, 800, "1,000x free", c="green", d=0.6, s=90))
# 26 Gemini splits the task, Genie acts it out
st = []
for q in range(3):
    i = uid("stp")
    st += [R(26, 250 + 330 * q, 380, 280, 120, c="ink", fill="paper", idp=i, sw=4), pop(26, i, 0.2 * q)]
    st += T(26, 390 + 330 * q, 455, 48, f"step {q + 1}", c="blue", d=0.2 * q + 0.1)
bd(26, st, T(26, 640, 280, 60, "Gemini", c="blue", d=0.0), arr(26, 1250, 440, 1450, 440, c="blue", d=0.7), robot(26, 1650, 650, 0.6, 0.8)[0])
r1, rid = robot(26.5, 900, 720, 0.9)
bd(26.5, screen(26.5, 900, 520, 700, 520, 0.0, c="blue"), r1, [sh(26.5, rid, 200, 0, 0.3, 0.8)], cup(26.5, 1200, 420, 0.6, 150), T(26.5, 1550, 300, 56, "Genie 4", c="blue", d=0.4))
# 27 planner on top, dreamer underneath
bd(27, ic(27, "gear", 960, 300, 220, 0.0, mv="spin"), T(27, 1350, 300, 60, "planner", c="blue", d=0.2), arr(27, 960, 430, 960, 560, c="ink", d=0.4))
dm, did = dreamy(27.5, 960, 550, 1.1)
bd(27.5, ic(27.5, "gear", 960, 230, 140, 0.0, mv="spin"), dm, T(27.5, 1450, 550, 60, "dreamer", c="blue", d=0.3), star(27.5, 500, 500, 0.4, r=40))
# 28 research preview, invited testers
bd(28, BIG(28, 960, 200, "Fine print", c="ink", d=0.0, s=100), ic(28, "flask", 600, 550, 220, 0.2, mv="wig"), T(28, 1300, 550, 64, "research preview", c="blue", d=0.4))
ps = []
for q in range(3):
    ps += walker(28.5, 600 + 350 * q, 680, 0.8, 0.1 * q)[0]
bd(28.5, ps, T(28.5, 960, 280, 64, "invited testers only", c="red", d=0.4))
# 29 coming weeks
bd(29, BIG(29, 960, 380, "coming weeks", c="blue", d=0.1, s=120), ic(29, "clock", 450, 450, 180, 0.2, mv="spin"), arr(29, 600, 650, 1350, 650, c="blue", d=0.4), ic(29, "rocket", 1550, 500, 160, 0.5, mv="bob"))
bd(29.5, ic(29.5, "computer", 600, 450, 220, 0.0, mv="bob"), T(29.5, 600, 680, 56, "developers", c="ink", d=0.2), ic(29.5, "phone", 1300, 450, 200, 0.3, mv="wig"), T(29.5, 1300, 680, 56, "paid users", c="ink", d=0.5))
# 30 text, sound, physics: still being worked on
bd(30, T(30, 500, 420, 70, "Hcllo", c="ink", d=0.0), cross(30, 500, 560, d=0.2), ic(30, "speaker", 960, 450, 180, 0.3, mv="wig"), ic(30, "atom", 1450, 450, 180, 0.5, mv="spin"))
bd(30.5, ic(30.5, "flask", 700, 450, 240, 0.0, mv="wig"), ic(30.5, "gear", 1050, 400, 150, 0.2, mv="spin"), T(30.5, 1350, 600, 64, "still in the lab", c="blue", d=0.4))
# 31 our worry: bad dream -> bad moves
r1, rid = robot(31, 700, 700, 1.0)
bd(31, r1, dreamy(31, 1350, 400, 0.8, mood="o")[0], T(31, 1350, 650, 56, "our worry", c="muted", d=0.4))
r1, rid = robot(31.5, 700, 700, 1.0, mood="sad")
bd(31.5, r1, [rot(31.5, rid, -30, (700, 780), 0.3, 0.5)], cup(31.5, 1000, 450, 0.4, 250), cross(31.5, 1450, 450, d=0.6), T(31.5, 1450, 650, 56, "bad moves", c="red", d=0.7))
# 32 it doesn't know, it guesses well
dm, did = dreamy(32, 600, 450, 1.1, mood="o")
bd(32, dm, ic(32, "question", 1350, 400, 240, 0.2, mv="wig", c="red"), T(32, 1350, 680, 60, "what comes next?", c="ink", d=0.4))
dm, did = dreamy(32.5, 600, 450, 1.1, mood="awake")
bd(32.5, dm, BIG(32.5, 1350, 380, "guesses", c="blue", d=0.2, s=110), BIG(32.5, 1350, 540, "really well", c="green", d=0.5, s=90), star(32.5, 1650, 300, 0.6, r=40))
# 33 hoping you won't check
t1, tid = tree(33, 500, 700, 1.0, 0.0)
w1, wid = walker(33, 1100, 700, 1.0, 0.0)
bd(33, t1, w1, [sh(33, wid, 250, 0, 0.3, 0.8)], ic(33, "eye", 1550, 350, 150, 0.4, mv="wig"))
dm, did = dreamy(33.5, 960, 450, 1.2, mood="o")
bd(33.5, dm, T(33.5, 960, 780, 64, "please don't check", c="red", d=0.4), ic(33.5, "question", 400, 400, 140, 0.3, mv="wig", c="red"))
# 34 just like me, your name
dm, did = dreamy(34, 600, 450, 1.1, mood="awake")
w1, wid = walker(34, 1350, 650, 1.0, 0.2)
bd(34, dm, w1, T(34, 1350, 300, 56, "hi, ...?", c="blue", d=0.4))
dm, did = dreamy(34.5, 960, 450, 1.2, mood="sleepy")
bd(34.5, dm, BIG(34.5, 960, 800, "...of course I remember", c="red", d=0.3, s=70), star(34.5, 500, 400, 0.4, r=40), star(34.5, 1420, 400, 0.6, r=40))

INS = [
 (2, "你可以用方向键在里面走来走去，|就像玩普通游戏。", "You can walk around with the arrow keys, | just like a normal game."),
 (3, "它叫SynthID，|好让大家认出这是AI做的。", "It's called SynthID, | so people can tell an AI made it."),
 (8, "手机输入法猜下一个字，|Genie猜的是下一整张画。", "Your phone's keyboard guesses the next word. | Genie guesses the next whole picture."),
 (11, "没有公式，|只有看了一遍又一遍的规律。", "No equations. | Just patterns, seen over and over."),
 (13, "所以水花四溅、积木叠高这种复杂的物理，|最容易露馅。", "So tricky physics, like splashing water or stacking blocks, | is where it slips."),
 (16, "就像每写一个新字，|都要把整本书重读一遍。", "It's like rereading the whole book | every time you write one new word."),
 (20, "真正的游戏引擎从来不忘，|它直接去查那棵树的位置。", "A real game engine never forgets. | It just looks up where the tree is."),
 (25, "它还可以编出少见的场面，|比如一只猫突然钻到机器人脚下。", "It could also invent rare moments, | like a cat darting under the robot's feet."),
 (30, "Genie 3一年多前才出来，|这一行跑得飞快。", "Genie three came out just over a year ago. | This field is moving fast."),
]
# 100 arrow keys
w1, wid = walker(100, 1300, 650, 1.0, 0.0, walk=200)
ks = []
for q, (dx, dy) in enumerate(((0, -1), (-1, 0), (0, 0), (1, 0))):
    i = uid("key")
    ks += [R(100, 450 + dx * 130 - 55, 500 + dy * 130 - 55 + (130 if q else 0) * 0, 110, 110, c="ink", fill="paper", idp=i, sw=4), pop(100, i, 0.1 * q), pulse(100, i, 0.6 + 0.15 * q)]
bd(100, ks, w1, arr(100, 750, 500, 1050, 500, c="blue", d=0.4))
t1, _ = tree(100.5, 500, 700, 1.0, 0.0)
w1, wid = walker(100.5, 900, 700, 1.0, 0.1, walk=400)
bd(100.5, t1, w1, ic(100.5, "map_pin", 1500, 400, 160, 0.3, mv="bob", c="red"), T(100.5, 960, 300, 64, "like a game", c="blue", d=0.5))
# 101 SynthID: tell an AI made it
bd(101, BIG(101, 960, 380, "SynthID", c="blue", d=0.0, s=150), ic(101, "magnifier", 450, 450, 200, 0.2, mv="wig"), ic(101, "chip", 1500, 450, 180, 0.4, mv="spin"))
bd(101.5, screen(101.5, 650, 450, 420, 280, 0.0), T(101.5, 650, 450, 70, "AI", c="red", d=0.3), arr(101.5, 900, 450, 1150, 450, c="ink", d=0.4), ic(101.5, "eye", 1400, 450, 200, 0.5, mv="wig"), check(101.5, 1650, 450, d=0.7))
# 102 phone keyboard -> next picture
bd(102, ic(102, "phone", 500, 450, 280, 0.0, mv="wig"), T(102, 1100, 380, 64, "I am so...", c="ink", d=0.2), T(102, 1100, 500, 64, "happy?", c="blue", d=0.5), arr(102, 1100, 560, 1100, 700, c="blue", d=0.6))
bd(102.5, screen(102.5, 550, 450, 380, 260, 0.0), arr(102.5, 770, 450, 1050, 450, c="blue", d=0.3), screen(102.5, 1350, 450, 380, 260, 0.4, c="blue"), dreamy(102.5, 1350, 450, 0.5, mood="awake")[0])
# 103 no equations, patterns
bd(103, T(103, 700, 450, 90, "E = mc²", c="ink", d=0.0), cross(103, 700, 450, d=0.3), ic(103, "sine", 1350, 450, 240, 0.4, mv="wig", c="blue"))
bd(103.5, ball(103.5, 450, 300, 0.0), ball(103.5, 750, 300, 0.2), ball(103.5, 1050, 300, 0.4), ball(103.5, 1350, 300, 0.6), T(103.5, 900, 800, 60, "over and over", c="blue", d=0.7))
# 104 splashing water, stacking blocks
bk = []
for q in range(4):
    i = uid("blk")
    bk += [R(104, 1250 + 15 * q * (-1) ** q, 700 - 110 * q, 160, 100, c="ink", fill=("gold", "blue", "red", "green")[q], idp=i, sw=4), pop(104, i, 0.15 * q), wig(104, i, (1330, 800), 3, 1.5)]
bd(104, ic(104, "water", 600, 450, 280, 0.0, mv="wig", c="blue"), [e for q in range(3) for e in ball(104, 450 + 150 * q, 350, 0.2 + 0.1 * q, drop=-150, c="blue")], bk)
dm, did = dreamy(104.5, 960, 450, 1.1, mood="o")
bd(104.5, dm, T(104.5, 960, 780, 64, "where it slips", c="red", d=0.4), ic(104.5, "question", 450, 400, 160, 0.3, mv="wig", c="red"), ic(104.5, "water", 1500, 400, 160, 0.5, mv="wig", c="blue"))
# 105 reread the book
bd(105, pages(105, 400, 380, 8, 0.0, w=140, h=200, gap=90), ic(105, "magnifier", 1550, 450, 200, 0.5, mv="wig"))
bd(105.5, T(105.5, 700, 450, 120, "+1 word", c="blue", d=0.0), arr(105.5, 950, 450, 1150, 450, c="ink", d=0.3), BIG(105.5, 1450, 450, "reread all", c="red", d=0.5, s=90), ic(105.5, "clock", 700, 700, 140, 0.4, mv="spin"))
# 106 real engine looks up
t1, tid = tree(106, 500, 700, 1.0, 0.0)
bd(106, t1, ic(106, "gear", 1000, 400, 200, 0.2, mv="spin"), T(106, 1450, 380, 56, "never forgets", c="green", d=0.4), check(106, 1450, 550, d=0.6))
bd(106.5, ic(106.5, "computer", 600, 450, 240, 0.0, mv="bob"), arr(106.5, 800, 450, 1100, 450, c="blue", d=0.3), T(106.5, 1450, 450, 64, "tree: x=600", c="blue", d=0.5), tree(106.5, 1450, 800, 0.6, 0.6)[0])
# 107 invent rare moments: a cat
r1, rid = robot(107, 700, 720, 1.0)
cat = uid("cat")
bd(107, r1, [O(107, 1500, 680, 60, c="ink", fill="gold", idp=cat), P(107, "M1455,630 L1470,580 L1495,625 M1505,625 L1530,580 L1545,630", c="ink", w=5, idp=cat),
             P(107, "M1560,700 Q1640,640 1620,580", c="ink", w=5, idp=cat), pop(107, cat, 0.2), sh(107, cat, -650, 50, 0.5, 0.8)], T(107, 1300, 300, 60, "rare moments", c="blue", d=0.3))
r1, rid = robot(107.5, 900, 720, 1.0, mood="sad")
bd(107.5, r1, [rot(107.5, rid, 15, (900, 800), 0.2, 0.3), rot(107.5, rid, -15, (900, 800), 0.6, 0.3)], ic(107.5, "question", 1400, 350, 160, 0.3, mv="wig", c="red"), T(107.5, 1450, 650, 56, "practice it safely", c="green", d=0.6))
# 108 Genie 3 a year ago, moving fast
bd(108, BIG(108, 700, 400, "Genie 3", c="muted", d=0.0, s=110), arr(108, 950, 400, 1250, 400, c="blue", d=0.3), BIG(108, 1500, 400, "Genie 4", c="blue", d=0.5, s=110), T(108, 1100, 600, 56, "~1 year", c="ink", d=0.4))
bd(108.5, ic(108.5, "rocket", 700, 450, 260, 0.0, mv="bob"), [e for e in ic(108.5, "rocket", 700, 450, 1, 0.0)][:0], arr(108.5, 900, 600, 1500, 300, c="red", d=0.3, dur=0.8), BIG(108.5, 1350, 650, "fast", c="red", d=0.5, s=120))

S2, MAP = [], {}
for k, sent in enumerate(S):
    MAP[k], MAP[k + 0.5] = len(S2), len(S2) + 0.5
    S2.append(sent)
    for q, (after, zh, en) in enumerate(INS):
        if after == k:
            MAP[100 + q], MAP[100 + q + 0.5] = len(S2), len(S2) + 0.5
            S2.append((zh, en))
S = S2
for b in B:
    for e in b:
        e["at"] = MAP[e["at"]]
B.sort(key=lambda b: min(e["at"] for e in b))

assert len(B) == len(S) + sum("|" in zh for zh, _ in S), (len(B), len(S))
if __name__ == "__main__":
    main(here, S, B, TITLE, "en", say={"SynthID": "Synth I D"})
