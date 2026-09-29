"""The lesson spec: one lesson to the chapter-1 benchmark, as structured bilingual data (D31).

The lecturer (主讲教授) writes a LessonSpec; the course designer (课程设计师) writes a GuidePlan
(lab guide + lesson plan). Renderers turn them into the lecture page, the slide deck, the lab
guide, the lab report template and the lesson plan — always in the benchmark's layout, so every
lesson looks and works like 大学物理 Chapter 1.

Every piece of student-facing text is a pair [中文, English] (课件中英对照).
The exemplar is lesson 1.1 of the benchmark, translated into this structure; the prompts show it
to the model as the level to match.
"""
from __future__ import annotations

from typing import Any

PAIR = {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 2,
        "description": "[Simplified Chinese, English]"}
PAIRS = {"type": "array", "items": PAIR}
STR = {"type": "string"}


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required if required is not None else list(props)}


def lesson_schema() -> dict:
    return _obj({
        "title": PAIR,
        "goal": PAIR,
        "problem": _obj({"title": PAIR, "text": PAIR, "given": PAIRS, "answer": PAIR}),
        "concept": _obj({"title": PAIR, "points": PAIRS, "formula": PAIR}),
        "notes": {"type": "array", "items": _obj({"heading": PAIR, "zh": STR, "en": STR}),
                  "description": "The lecture notes, 3-6 sections; zh/en are HTML (p, ul, ol, li, strong, em, table; formulas in \\( \\) or \\[ \\])"},
        "example": _obj({"question": PAIR, "steps": PAIRS, "answer": PAIR}),
        "animation": _obj({"title": PAIR, "question": PAIR, "beats": PAIRS},
                          ),
        "lab": _obj({"title": PAIR, "robot_scene": PAIR, "life_scene": PAIR, "params": PAIRS, "tasks": PAIRS}),
        "model": _obj({"assume": PAIR, "solve": PAIR, "check": PAIR, "improve": PAIR}),
        "everyday": _obj({"text": PAIR, "answer": PAIR}),
        "summary": PAIRS,
        "self_check": PAIRS,
    })


ENV = {"type": "array", "items": _obj({"item": PAIR, "range": PAIR})}
TABLES = {"type": "array", "items": _obj({"caption": PAIR, "headers": {"type": "array", "items": STR},
                                          "rows": {"type": "array", "items": {"type": "array", "items": STR}}})}
PROCESS = {"type": "array", "items": _obj({"phase": STR, "minutes": {"type": "integer"}, "content": STR, "activity": STR})}


def guide_plan_schema() -> dict:
    return _obj({
        "guide": _obj({"goal": PAIRS, "theory": PAIRS, "env": ENV, "steps": PAIRS, "tables": TABLES,
                       "cautions": PAIRS, "questions": PAIRS, "problem_question": PAIR}),
        "plan": _obj({"audience": STR, "hours": STR, "method": STR,
                      "objectives": _obj({"knowledge": STR, "ability": STR, "literacy": STR}),
                      "key": STR, "difficult": STR, "process": PROCESS, "board": STR, "homework": STR, "reflection": STR}),
    })


# --- the benchmark lesson 1.1, as the one example the model sees ------------------------------

EXEMPLAR: dict[str, Any] = {
    "title": ["参考系、坐标系与质点", "Reference frames, coordinates and particles"],
    "goal": ["能选定合适的参考系描述运动，并用速度叠加计算运动物体的对地速度", "Choose a suitable frame to describe motion and use velocity addition to find ground velocities"],
    "problem": {
        "title": ["传送带跟踪抓取", "Grasping from a moving conveyor"],
        "text": ["工件在传送带上以 0.50 m/s 运动，机械臂要在运动中抓住它。在哪个参考系里规划抓取最简单？末端对地速度应是多少？",
                 "A part rides the belt at 0.50 m/s and the arm must grab it on the move. In which frame is the grasp easiest to plan, and what must the gripper’s ground velocity be?"],
        "given": [["传送带速度 u = 0.50 m/s", "belt speed u = 0.50 m/s"],
                  ["末端相对传送带竖直下降 0.25 m/s", "gripper descends at 0.25 m/s relative to the belt"],
                  ["下降距离 0.50 m", "descent 0.50 m"]],
        "answer": ["在传送带参考系中规划最简单；末端对地速度 0.56 m/s，向下偏 26.6°", "Plan in the belt frame; the gripper’s ground velocity is 0.56 m/s, 26.6° below horizontal"],
    },
    "concept": {
        "title": ["参考系：运动是相对的", "Reference frames: motion is relative"],
        "points": [["描述运动必须先选定参考系；同一运动在不同参考系中看来不同", "Choose a frame first; one motion looks different in different frames"],
                   ["在参考系上建立坐标系：直角坐标系、自然坐标系", "Set up coordinates: Cartesian or path (natural) coordinates"],
                   ["质点：形状和大小可以忽略时，把物体看成有质量的点", "Particle: ignore size and shape when they do not matter"],
                   ["速度叠加：v(对地) = v(相对) + v(牵连)", "Velocity addition: v(ground) = v(relative) + v(frame)"]],
        "formula": ["描述运动 = 参考系 + 坐标系 + 研究对象（质点）", "Motion = frame + coordinates + object (particle)"],
    },
    "notes": [
        {"heading": ["参考系与坐标系", "Frames and coordinates"],
         "zh": "<p>描述运动必须先选定参考系，同一运动在不同参考系中看来不同。为了定量描述，还要在参考系上建立坐标系，常用直角坐标系和自然坐标系。</p>",
         "en": "<p>To describe motion we first choose a reference frame; one motion looks different from different frames. To make it quantitative we set up coordinates on the frame, usually Cartesian or path coordinates.</p>"},
        {"heading": ["质点：理想模型", "The particle: an idealized model"],
         "zh": "<p>当物体的形状和大小对所研究的问题影响可以忽略时，可以把它看成一个有质量的点，称为质点。地球绕太阳公转时可以看作质点，研究地球自转时则不能。</p>",
         "en": "<p>When an object’s size and shape do not matter for the question, we treat it as a point with mass, a particle. Earth orbiting the Sun can be a particle; Earth spinning on its axis cannot.</p>"},
        {"heading": ["速度叠加", "Velocity addition"],
         "zh": "<p>物体相对运动参考系的速度为 \\(\\vec v'\\)，参考系相对地面的速度为 \\(\\vec u\\)，则对地速度 \\[\\vec v = \\vec v' + \\vec u\\] （伽利略变换，\\(u \\ll c\\)）。</p>",
         "en": "<p>If an object moves at \\(\\vec v'\\) relative to a frame that moves at \\(\\vec u\\) relative to the ground, its ground velocity is \\[\\vec v = \\vec v' + \\vec u\\] (Galilean transformation, \\(u \\ll c\\)).</p>"},
    ],
    "example": {
        "question": ["列车以 12 m/s 匀速行驶，乘客在 1.80 m 高处松手让小球下落。分别在车厢和地面参考系中描述小球的运动。", "A train moves at 12 m/s; a passenger drops a ball from 1.80 m. Describe the motion in the carriage frame and in the ground frame."],
        "steps": [["下落时间 t = √(2h/g) = √(2×1.80/9.8) ≈ 0.61 s，与参考系无关", "Fall time t = √(2h/g) ≈ 0.61 s in both frames"],
                  ["车厢参考系：初速度为零，竖直下落，轨迹是直线", "Carriage frame: starts at rest, falls straight down"],
                  ["地面参考系：水平速度 12 m/s，轨迹是抛物线，水平位移 12 × 0.61 ≈ 7.3 m", "Ground frame: horizontal speed 12 m/s, a parabola, 7.3 m sideways"]],
        "answer": ["同一运动：车厢里看是直线，地面上看是抛物线", "One motion: a line in the carriage, a parabola from the ground"],
    },
    "animation": {
        "title": ["参考系：运动是相对的", "Reference frames: motion is relative"],
        "question": ["车厢里的人和地面上的人，看到的小球轨迹为什么不同？", "Why do the passenger and the person on the ground see different paths?"],
        "beats": [["车厢匀速向右行驶，乘客松手让小球下落", "The carriage moves right at constant speed; a passenger lets go of a ball"],
                  ["同一个小球：车厢里看是直线，地面上看是抛物线", "Same ball: a straight line seen from the carriage, a parabola seen from the ground"],
                  ["所以描述运动，必须先选定参考系", "So to describe motion, first choose a reference frame"],
                  ["研究地球公转时，地球的大小可以忽略……", "For Earth's orbit around the Sun, Earth's size can be ignored..."],
                  ["……把它看成一个有质量的点：质点（理想模型）", "...so treat it as a point with mass: a particle (an idealized model)"]],
    },
    "lab": {
        "title": ["参考系与相对运动", "Reference frames and relative motion"],
        "robot_scene": ["机器人：传送带抓取——传送带带着工件运动，机械臂末端在运动中抓取", "Robot: conveyor grasp — a part rides the belt and the gripper grabs it on the move"],
        "life_scene": ["列车上落球——车厢里和地面上的观察者看同一个小球", "Ball in a train — observers in the carriage and on the ground watch one ball"],
        "params": [["传送带速度 0–1.00 m/s", "belt speed 0–1.00 m/s"], ["列车速度 0–30 m/s", "train speed 0–30 m/s"], ["观察者速度（可反向）", "observer speed (either direction)"]],
        "tasks": [["传送带参考系：末端竖直落到工件上", "Belt frame: gripper comes straight down"],
                  ["地面参考系：读出末端对地速度和方向", "Ground frame: read the gripper’s ground velocity"],
                  ["列车：找一个观察者看到小球向后抛出", "Train: find an observer who sees the ball go backwards"]],
    },
    "model": {
        "assume": ["工件、末端看成质点；传送带匀速；末端相对传送带竖直下降 0.25 m/s", "Part and gripper as particles; belt at constant speed; gripper descends 0.25 m/s relative to the belt"],
        "solve": ["v(对地) = (0.50, −0.25) m/s，大小 0.56 m/s，向下偏 26.6°。若只对地竖直下降，2.0 s 内工件滑过 1.0 m，抓不到",
                  "v(ground) = (0.50, −0.25) m/s: 0.56 m/s, 26.6° below horizontal. Descending straight down relative to the ground, the part slides 1.0 m past in 2.0 s"],
        "check": ["虚拟实验“传送带抓取”：两个参考系中分别观察轨迹、读对地速度", "Lab “conveyor grasp”: compare the path in both frames and read the ground velocity"],
        "improve": ["传送带速度有波动，要用编码器或视觉实时跟踪；抓取前后的加减速也要规划", "Belt speed varies, so track it with an encoder or camera; plan the acceleration before and after the grasp"],
    },
    "everyday": {"text": ["雨天车窗上的雨痕：雨滴下落 7 m/s、车速 20 m/s，雨痕与竖直方向成多大角？", "Rain streaks on a car window: raindrops at 7 m/s, car at 20 m/s — what angle do the streaks make with the vertical?"],
                 "answer": ["约 71°（tanα = 20/7）", "About 71° (tanα = 20/7)"]},
    "summary": [["描述运动 = 参考系 + 坐标系 + 质点", "Motion = frame + coordinates + particle"],
                ["对地速度 = 相对速度 + 牵连速度", "Ground velocity = relative velocity + frame velocity"]],
    "self_check": [["车厢里的人说小球“竖直下落”，地面上的人说它“做平抛运动”，谁对？", "The passenger says the ball falls straight down; the person on the ground says it is a projectile. Who is right?"],
                   ["地球在什么问题里可以看成质点？在什么问题里不能？", "When can Earth be treated as a particle, and when not?"]],
}

# --- normalising model output ------------------------------------------------------------------


def pair(v: Any) -> list[str]:
    """Anything -> [zh, en]. A single string is used for both."""
    if isinstance(v, (list, tuple)):
        items = [str(x or "").strip() for x in v][:2]
        if len(items) == 1:
            items.append(items[0])
        return items if items else ["", ""]
    if isinstance(v, dict):
        return [str(v.get("zh") or "").strip(), str(v.get("en") or "").strip()]
    s = str(v or "").strip()
    return [s, s]


def pairs(v: Any, limit: int = 12) -> list[list[str]]:
    return [pair(x) for x in (v if isinstance(v, list) else [])[:limit] if x]


def normalize_lesson(d: Any) -> dict:
    d = d if isinstance(d, dict) else {}
    g = lambda k: d.get(k) if isinstance(d.get(k), dict) else {}  # noqa: E731
    pr, co, ex, an, lab, mo, ev = g("problem"), g("concept"), g("example"), g("animation"), g("lab"), g("model"), g("everyday")
    notes = []
    for n in d.get("notes") or []:
        if isinstance(n, dict):
            notes.append({"heading": pair(n.get("heading")), "zh": str(n.get("zh") or ""), "en": str(n.get("en") or "")})
    return {
        "title": pair(d.get("title")), "goal": pair(d.get("goal")),
        "problem": {"title": pair(pr.get("title")), "text": pair(pr.get("text")), "given": pairs(pr.get("given"), 6), "answer": pair(pr.get("answer"))},
        "concept": {"title": pair(co.get("title")), "points": pairs(co.get("points"), 6), "formula": pair(co.get("formula"))},
        "notes": notes[:8],
        "example": {"question": pair(ex.get("question")), "steps": pairs(ex.get("steps"), 8), "answer": pair(ex.get("answer"))},
        "animation": {"title": pair(an.get("title")), "question": pair(an.get("question")), "beats": pairs(an.get("beats"), 10)},
        "lab": {"title": pair(lab.get("title")), "robot_scene": pair(lab.get("robot_scene")), "life_scene": pair(lab.get("life_scene")),
                "params": pairs(lab.get("params"), 6), "tasks": pairs(lab.get("tasks"), 5)},
        "model": {k: pair(mo.get(k)) for k in ("assume", "solve", "check", "improve")},
        "everyday": {"text": pair(ev.get("text")), "answer": pair(ev.get("answer"))},
        "summary": pairs(d.get("summary"), 6), "self_check": pairs(d.get("self_check"), 5),
    }


def normalize_guide_plan(d: Any) -> dict:
    d = d if isinstance(d, dict) else {}
    gd = d.get("guide") if isinstance(d.get("guide"), dict) else {}
    pl = d.get("plan") if isinstance(d.get("plan"), dict) else {}
    tables = []
    for t in gd.get("tables") or []:
        if isinstance(t, dict) and t.get("headers"):
            headers = [str(h) for h in t["headers"]][:9]
            rows = [[str(c) for c in (r if isinstance(r, list) else [])][:len(headers)] + [""] * max(0, len(headers) - len(r if isinstance(r, list) else []))
                    for r in (t.get("rows") or [])[:10]]
            tables.append({"caption": pair(t.get("caption")), "headers": headers, "rows": rows})
    env = [{"item": pair(e.get("item")), "range": pair(e.get("range"))} for e in gd.get("env") or [] if isinstance(e, dict)]
    obj = pl.get("objectives") if isinstance(pl.get("objectives"), dict) else {}
    process = [{"phase": str(p.get("phase") or ""), "minutes": int(p.get("minutes") or 0) if str(p.get("minutes") or "0").isdigit() else 0,
                "content": str(p.get("content") or ""), "activity": str(p.get("activity") or "")}
               for p in pl.get("process") or [] if isinstance(p, dict)]
    return {
        "guide": {"goal": pairs(gd.get("goal"), 5), "theory": pairs(gd.get("theory"), 6), "env": env[:8], "steps": pairs(gd.get("steps"), 10),
                  "tables": tables[:4], "cautions": pairs(gd.get("cautions"), 5), "questions": pairs(gd.get("questions"), 5),
                  "problem_question": pair(gd.get("problem_question"))},
        "plan": {"audience": str(pl.get("audience") or ""), "hours": str(pl.get("hours") or ""), "method": str(pl.get("method") or ""),
                 "objectives": {k: str(obj.get(k) or "") for k in ("knowledge", "ability", "literacy")},
                 "key": str(pl.get("key") or ""), "difficult": str(pl.get("difficult") or ""), "process": process[:12],
                 "board": str(pl.get("board") or ""), "homework": str(pl.get("homework") or ""), "reflection": str(pl.get("reflection") or "")},
    }


def check_lesson(s: dict) -> list[str]:
    """What the benchmark requires and a spec is missing (the reviewer gets these too)."""
    problems = []
    need = [("机器人问题的题面", s["problem"]["text"][0]), ("已知条件", s["problem"]["given"]), ("概念要点", s["concept"]["points"]),
            ("讲义正文", s["notes"]), ("动画分镜", s["animation"]["beats"]), ("虚拟实验任务", s["lab"]["tasks"]),
            ("建模五步：建模", s["model"]["assume"][0]), ("建模五步：求解", s["model"]["solve"][0]),
            ("建模五步：检验", s["model"]["check"][0]), ("建模五步：修正", s["model"]["improve"][0]),
            ("生活中的例子", s["everyday"]["text"][0]), ("例题", s["example"]["steps"])]
    for label, value in need:
        if not value:
            problems.append(f"缺少{label}")
    if s["notes"] and not any(n["en"].strip() for n in s["notes"]):
        problems.append("讲义没有英文")
    if len(s["lab"]["tasks"]) < 2:
        problems.append("虚拟实验任务少于 2 个")
    return problems
