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
TEMPLATES = ("showcase", "joints", "mechanism", "explode")


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


def build(plan: dict, models: dict, *, title=None, no="", lang="both") -> dict:
    """A scene script from the 3D animator's plan {template, items|item, poses, captions, ...}."""
    tpl = plan.get("template")
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
