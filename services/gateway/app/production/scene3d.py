"""三维动画 (round 4, step 3): scene scripts built from templates, rendered by the browser service (labcheck).

The animator does not write 3D code. It picks a template and fills in THIS lesson's content (which robots, which
poses, captions); the template turns that into a declarative scene script, the gateway puts script, engine
(three.js bundle) and the course's copies of the library models into one self-contained page, and the browser
service steps through it frame by frame and encodes an MP4 (POST /render3d).

Templates:
  showcase   — a family of robots appears one after another, each doing its typical motion (course overview)
  joints     — one robot moves through key poses; the tool point leaves a trace; base and tool frames shown
  mechanism  — a mechanism turns through its motion table (four-bar etc.)
  explode    — an assembly flies apart and back together (bearing, gearbox)
"""
from __future__ import annotations

import base64
import csv
import html
import io
import json
import math
from pathlib import Path

import httpx

ENGINE = Path(__file__).parent / "three" / "wq3d.js"
TEMPLATES = ("showcase", "joints", "mechanism", "explode", "workshop")


class Render3DError(Exception):
    def __init__(self, message: str, stage: str = "render"):
        super().__init__(message)
        self.stage = stage


# --- models ------------------------------------------------------------------------------------------------------

def load_models(assets_dir: Path, ids: list[str]) -> dict:
    """The course's copies: {id: {entry, glb (base64), motion (rows)}}."""
    out = {}
    for eid in dict.fromkeys(ids):
        d = assets_dir / eid
        if not (d / "entry.json").exists():
            continue
        entry = json.loads((d / "entry.json").read_text(encoding="utf-8"))
        glb = next((p for p in sorted(d.glob("*.glb"))), None)
        if not glb:
            continue
        rows = []
        if (d / "motion.csv").exists():
            rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(io.StringIO((d / "motion.csv").read_text()))]
        out[eid] = {"entry": entry, "glb": base64.b64encode(glb.read_bytes()).decode(), "motion": rows}
    return out


# --- templates -----------------------------------------------------------------------------------------------------

def _pair(v, default=("", "")) -> list[str]:
    if isinstance(v, (list, tuple)) and v:
        return [str(v[0] or ""), str((v[1] if len(v) > 1 else "") or v[0] or "")]
    return [str(v or default[0]), str(v or default[1])]


def _demo_tracks(actor: str, entry: dict, t0: float, t1: float) -> tuple[list, list]:
    """Typical motion of a robot from its entry's `demo` ([from, to] per joint): out and back; continuous joints spin."""
    tracks, spins = [], []
    mid = (t0 + t1) / 2
    for j in entry.get("joints") or []:
        rng = (entry.get("demo") or {}).get(j["name"])
        if not rng:
            continue
        if j["type"] == "continuous" and abs(rng[1] - rng[0]) > 6:
            spins.append({"actor": actor, "joint": j["name"], "rate": (rng[1] - rng[0]) / 2, "from": t0, "to": t1})
        else:
            tracks.append({"actor": actor, "joint": j["name"], "keys": [[t0, rng[0]], [mid, rng[1]], [t1 - 0.2, rng[0]]]})
    return tracks, spins


def showcase(items: list[dict], models: dict, *, title=None, no="", lang="both", per=5.0) -> dict:
    """items: [{id, name: [zh, en], line: [zh, en]}] — one after another, each with its name and one line."""
    items = [i for i in items if i["id"] in models][:8]
    actors, tracks, spins, captions, labels, cam = [], [], [], [], [], []
    t = 0.6
    for k, it in enumerate(items):
        aid = f"a{k}"
        entry = models[it["id"]]["entry"]
        t0, t1 = t, t + per
        actors.append({"id": aid, "model": it["id"], "appear": [t0, t1]})
        tr, sp = _demo_tracks(aid, entry, t0 + 0.4, t1 - 0.3)
        tracks += tr
        spins += sp
        labels.append([t0 + 0.3, t1, aid, _pair(it.get("name") or entry["name"].values())])
        if it.get("line"):
            captions.append([t0 + 0.3, t1, _pair(it["line"])])
        az = 30 + (k % 2) * 20
        cam += [[t0, az, 20, 0.72, aid], [t1 - 0.01, az + 25, 24, 0.78, aid]]
        t = t1
    return {"theme": "dark", "lang": lang, "duration": round(t + 0.4, 2), "title": _pair(title) if title else None, "no": no,
            "actors": actors, "tracks": tracks, "spin": spins, "captions": captions, "labels": labels,
            "camera": {"keys": cam or [[0, 35, 22, 0.8, "all"]]}}


def joints(item: str, models: dict, poses: list[dict], *, captions=None, title=None, no="", lang="both", seg=3.0) -> dict:
    """One robot through key poses (joint name → value), holding each briefly; the tool point leaves a trace."""
    entry = models[item]["entry"]
    known = {j["name"] for j in entry.get("joints") or []}
    poses = [{k: float(v) for k, v in (p or {}).items() if k in known} for p in poses][:8] or [entry.get("rest") or {}]
    start = {j["name"]: float((entry.get("rest") or {}).get(j["name"], 0.0)) for j in entry.get("joints") or []}
    keys: dict[str, list] = {n: [[0.0, v]] for n, v in start.items()}
    t, cur = 0.8, dict(start)
    for p in poses:
        cur = {**cur, **p}
        for n, v in cur.items():
            keys[n].append([t + seg, v])
            keys[n].append([t + seg + 0.6, v])
        t += seg + 0.6
    tracks = [{"actor": "r", "joint": n, "keys": k} for n, k in keys.items()]
    caps = [[float(c[0]), float(c[1]), _pair(c[2])] for c in (captions or []) if isinstance(c, (list, tuple)) and len(c) == 3]
    return {"theme": "dark", "lang": lang, "duration": round(t + 0.6, 2), "title": _pair(title) if title else None, "no": no,
            "actors": [{"id": "r", "model": item}], "tracks": tracks,
            "traces": [{"actor": "r", "from": 0.8}] if entry.get("tool") else [],
            "frames": [{"actor": "r", "link": entry.get("root"), "size": 0.15}]
                      + ([{"actor": "r", "link": entry["tool"]["link"], "size": 0.1}] if entry.get("tool") else []),
            "captions": caps, "camera": {"keys": [[0, 40, 20, 0.7, "r"], [t + 0.6, 70, 26, 0.72, "r"]]}}


def mechanism(item: str, models: dict, *, turns=2.0, seconds=10.0, captions=None, title=None, no="", lang="both") -> dict:
    caps = [[float(c[0]), float(c[1]), _pair(c[2])] for c in (captions or []) if isinstance(c, (list, tuple)) and len(c) == 3]
    return {"theme": "dark", "lang": lang, "duration": seconds, "title": _pair(title) if title else None, "no": no,
            "actors": [{"id": "m", "model": item}], "motion": [{"actor": "m", "keys": [[0.5, 0], [seconds - 0.3, 360 * turns]]}],
            "captions": caps, "camera": {"keys": [[0, 0, 70, 0.75, "m"], [seconds, 20, 55, 0.75, "m"]]}}


def explode(item: str, models: dict, *, amount=0.9, captions=None, title=None, no="", lang="both") -> dict:
    caps = [[float(c[0]), float(c[1]), _pair(c[2])] for c in (captions or []) if isinstance(c, (list, tuple)) and len(c) == 3]
    entry = models[item]["entry"]
    tr, sp = _demo_tracks("e", entry, 0.5, 9.5)
    return {"theme": "dark", "lang": lang, "duration": 10.0, "title": _pair(title) if title else None, "no": no,
            "actors": [{"id": "e", "model": item}], "tracks": tr, "spin": sp,
            "explode": [{"actor": "e", "keys": [[1.0, 0], [3.5, amount], [6.5, amount], [9.0, 0]]}],
            "captions": caps, "camera": {"keys": [[0, 30, 35, 0.6, "e"], [10, 80, 30, 0.6, "e"]]}}


def _ts(s: str):
    from datetime import datetime
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _route(a, b, ys, vx):
    """The factory's AGV routing: into the nearest aisle, along it (changing aisle on the cross aisle), into the dock."""
    if abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6:
        return [a]
    ay = min(ys, key=lambda y: abs(y - a[1])) if ys else a[1]
    by = min(ys, key=lambda y: abs(y - b[1])) if ys else b[1]
    pts = [a, (a[0], ay)]
    if ay != by and vx is not None:
        pts += [(vx, ay), (vx, by)]
    pts += [(b[0], by), b]
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    return out


def workshop(data: dict, *, follow: str = "", highlight=None, captions=None, title=None, no="", lang="both",
             seconds: float = 24.0, source: str = "") -> dict:
    """车间: the digital factory's floor in a time window, from its own data — units coloured by their state, AGVs on
    their recorded moves (routed along the aisles as in the factory). data = {layout, agv (rows), event (rows), from, to}."""
    layout = data["layout"]
    t0, t1 = _ts(data["from"]), _ts(data["to"])
    span = max(60.0, (t1 - t0).total_seconds())
    usable = max(6.0, seconds - 1.0)
    T = lambda ts: round(0.5 + (_ts(ts) - t0).total_seconds() / span * usable, 3)  # noqa: E731
    ys = sorted(a["y_m"] for a in layout.get("aisles") or [] if a.get("axis") == "x")
    vx = next((a["x_m"] for a in layout.get("aisles") or [] if a.get("axis") == "y"), None)
    hi = set(highlight or [])
    states: dict[str, list] = {}
    for r in sorted(data.get("event") or [], key=lambda r: r["ts"]):
        if r.get("event") != "state" or not r.get("state"):
            continue
        t = max(0.0, T(r["ts"])) if _ts(r["ts"]) >= t0 else 0.0
        if _ts(r["ts"]) <= t1:
            states.setdefault(r["unit"], []).append([t, r["state"]])
    units = [{"id": u["unit"], "x": u["x_m"], "y": u["y_m"], "w": u["w_m"], "d": u["d_m"], "h": 2.6 if u.get("area") == "warehouse" else 1.6,
              "store": u.get("area") == "warehouse",
              "name": (u["name"].get("en") if lang == "en" else u["name"].get("zh")) or u["unit"],
              "highlight": u["unit"] in hi, "states": states.get(u["unit"], [])} for u in layout.get("units") or []]
    by_agv: dict[str, list] = {}
    for r in sorted(data.get("agv") or [], key=lambda r: r["ts"]):
        by_agv.setdefault(r["unit"], []).append(r)
    agvs = []
    for aid, rows in by_agv.items():
        keys = []
        for a, b in zip(rows, rows[1:] + [None]):
            ta = T(a["ts"])
            keys.append([ta, a["x_m"], a["y_m"], 1 if a.get("load") else 0])
            if b is None:
                break
            path = _route((a["x_m"], a["y_m"]), (b["x_m"], b["y_m"]), ys, vx)
            if len(path) < 2:
                continue
            tb = T(b["ts"])
            lens = [((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5 for p, q in zip(path, path[1:])]
            total = sum(lens) or 1.0
            acc = 0.0
            for q, ln in zip(path[1:-1], lens):
                acc += ln
                keys.append([round(ta + (tb - ta) * acc / total, 3), q[0], q[1], 1 if a.get("load") else 0])
        for name, p in (layout.get("agv_home") or {}).items():
            if name == aid and not keys:
                keys.append([0.0, p["x_m"], p["y_m"], 0])
        agvs.append({"id": aid, "keys": keys})
    for name, p in (layout.get("agv_home") or {}).items():
        if name not in by_agv:
            agvs.append({"id": name, "keys": [[0.0, p["x_m"], p["y_m"], 0]]})
    aisles = []
    fw, fd = layout["floor"]["w_m"], layout["floor"]["d_m"]
    for a in layout.get("aisles") or []:
        if a.get("axis") == "x":
            aisles.append({"x": fw / 2, "y": a["y_m"], "w": fw, "d": a.get("width_m", 2.2)})
        elif a.get("axis") == "y":
            y0, y1 = a.get("from_y_m", 0), a.get("to_y_m", fd)
            aisles.append({"x": a["x_m"], "y": (y0 + y1) / 2, "w": a.get("width_m", 2.2), "d": y1 - y0})
    caps = [[float(c[0]), float(c[1]), _pair(c[2])] for c in (captions or []) if isinstance(c, (list, tuple)) and len(c) == 3]
    target = follow if follow in {u["id"] for u in units} | {a["id"] for a in agvs} else ""
    mid = seconds * 0.5
    cam = [[0, 15, 52, 1.7, "workshop"], [mid - 2, 35, 44, 1.7, "workshop"]]
    cam += [[mid, 30, 35, 1.0, target], [seconds - 3, 55, 32, 1.0, target]] if target else [[seconds, 55, 40, 1.7, "workshop"]]
    if target:
        cam.append([seconds, 30, 48, 1.7, "workshop"])
    sod = t0.hour * 3600 + t0.minute * 60 + t0.second
    return {"theme": "dark", "lang": lang, "duration": round(seconds, 2), "title": _pair(title) if title else None, "no": no,
            "actors": [], "captions": caps, "source": source,
            "workshop": {"floor": {"w": fw, "d": fd}, "aisles": aisles, "units": units, "agvs": agvs, "clock": [sod, span / usable]},
            "camera": {"keys": cam}}


def build(plan: dict, models: dict, *, title=None, no="", lang="both", factory_data: dict | None = None, source: str = "") -> dict:
    """A scene script from the 3D animator's plan {template, items|item, poses, captions, ...}."""
    tpl = plan.get("template")
    if tpl == "workshop":
        if not factory_data:
            raise Render3DError("the digital factory is not connected for this course", "plan")
        return workshop(factory_data, follow=plan.get("follow") or "", highlight=plan.get("highlight"), captions=plan.get("captions"),
                        title=title, no=no, lang=lang, source=source)
    if tpl == "showcase":
        return showcase(plan.get("items") or [], models, title=title, no=no, lang=lang)
    item = plan.get("item") or next(iter(models), "")
    if item not in models:
        raise Render3DError(f"model {item or '(none)'} is not in this course's library copies", "plan")
    if tpl == "joints":
        return joints(item, models, plan.get("poses") or [], captions=plan.get("captions"), title=title, no=no, lang=lang)
    if tpl == "mechanism":
        return mechanism(item, models, captions=plan.get("captions"), title=title, no=no, lang=lang)
    if tpl == "explode":
        return explode(item, models, captions=plan.get("captions"), title=title, no=no, lang=lang)
    raise Render3DError(f"unknown template {tpl!r}", "plan")


def used_models(script: dict) -> list[str]:
    return [a["model"] for a in script.get("actors") or []]


# --- page and render ------------------------------------------------------------------------------------------------

def page(script: dict, models: dict) -> str:
    """One self-contained page: engine, models (base64) and the script. Nothing is loaded from the network."""
    data = {k: models[k] for k in used_models(script) if k in models}
    w, h = script.get("width", 1280), script.get("height", 720)
    js = ENGINE.read_text(encoding="utf-8").replace("</script", "<\\/script")
    payload = json.dumps({"script": script, "models": data}).replace("</", "<\\/")
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(str((script.get('title') or [''])[0]))}</title>
<style>html,body{{margin:0;background:#0f1419;overflow:hidden}}#wrap{{position:relative;width:{w}px;height:{h}px}}
canvas{{display:block;width:{w}px;height:{h}px}}#over{{position:absolute;inset:0}}</style></head>
<body><div id="wrap"><canvas id="c" width="{w}" height="{h}"></canvas><div id="over"></div></div>
<script>{js}</script>
<script>
const DATA = {payload};
WQ3D.player(document.getElementById("c"), document.getElementById("over"), DATA.script, DATA.models)
  .then((p) => {{ window.P = p; window.SEEK = p.seek; window.DURATION = p.duration; window.READY = true; }})
  .catch((e) => {{ window.FAIL = String(e && e.stack || e); }});
</script></body></html>"""


async def render(url: str, page_html: str, duration: float, *, fps: int = 30, timeout: float = 600.0) -> tuple[bytes, bytes, float, list[bytes]]:
    """(video, poster, seconds, key frames) from the browser service."""
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as c:
            r = await c.post(url.rstrip("/") + "/render3d", json={"html": page_html, "duration": duration, "fps": fps})
    except httpx.HTTPError as e:
        raise Render3DError(f"3D renderer unreachable: {type(e).__name__}", "service") from e
    if r.status_code != 200:
        raise Render3DError(f"3D renderer answered {r.status_code}", "service")
    d = r.json()
    if not d.get("ok"):
        raise Render3DError(str(d.get("error") or "3D render failed")[:3000], str(d.get("stage") or "render"))
    return (base64.b64decode(d["video"]), base64.b64decode(d.get("poster") or ""), float(d.get("seconds") or duration),
            [base64.b64decode(f) for f in d.get("frames") or []])


def seconds(script: dict) -> float:
    return float(script.get("duration") or 10.0)


def ease_pose(a: dict, b: dict, f: float) -> dict:
    s = f * f * (3 - 2 * f)
    return {k: a.get(k, 0) + (b.get(k, 0) - a.get(k, 0)) * s for k in set(a) | set(b)}


_ = math  # (kept for templates that compute poses)
