"""Virtual labs (round 3, A3): the lab kit, the chapter lab page, the safety check and the trial run.

The AI lab engineer (实验师) writes one lab per lesson as a call to WQ.lab({...}) — physics and drawing
only. The kit (labkit/kit.js + kit.css, taken from the Chapter 1 benchmark) supplies everything else,
so every lab looks and works the same. A chapter's labs share one page, "第2章 虚拟实验", which follows
the WenQuest lab protocol (#lab-2-1, {type: "wq-lab", lab: "2.1"}).

Before a lab is used it is checked twice: statically here (no network, no navigation, no storage
tricks, size), then in a headless browser by the lab checker service (services/labcheck), which also
runs every task's demo and takes the screenshot used on the slides.
"""
from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path

import httpx

KIT = Path(__file__).parent / "labkit"
MAX_CODE = 60_000
# The lab page may not load or send anything: no network at all, only its own inline code.
CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; "
       "font-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'")

FORBIDDEN = [
    (r"\bfetch\s*\(", "network access (fetch)"), (r"XMLHttpRequest", "network access (XMLHttpRequest)"),
    (r"WebSocket|EventSource|RTCPeerConnection", "network access"), (r"sendBeacon", "network access (sendBeacon)"),
    (r"\bimport\s*\(|\bimport\s+[\w{*]|importScripts", "loading other code (import)"),
    (r"\beval\s*\(|\bnew\s+Function\b|\bFunction\s*\(", "eval / Function"),
    (r"document\.cookie|localStorage|sessionStorage|indexedDB", "storage (the kit saves progress itself)"),
    (r"\blocation\s*(\.\s*(href|assign|replace)|=)|window\.open|\bopen\s*\(", "navigation or pop-ups"),
    (r"\b(parent|top|opener)\s*\.", "reaching the page around the lab"),
    (r"postMessage", "messages (the kit reports progress itself)"),
    (r"document\.write|innerHTML|outerHTML|insertAdjacentHTML", "writing HTML (use the kit's panels and api.readout)"),
    (r"</\s*script|<\s*script|<!--", "script tags"),
    (r"https?://|//[a-z0-9-]+\.[a-z]{2,}/", "web addresses"),
    (r"\bsetInterval\s*\(|\bsetTimeout\s*\(|requestAnimationFrame", "own timers (the kit runs the loop)"),
    (r"\bWQ\s*\.\s*(demo|reset|begin|fail|status|start|speed|show)\b", "kit internals"),
]


def static_problems(code: str) -> list[str]:
    """What is wrong with a lab's code before it is run (fed back to the lab engineer)."""
    out = []
    if not code.strip():
        return ["the code is empty"]
    if len(code) > MAX_CODE:
        out.append(f"the code is too long ({len(code)} characters, at most {MAX_CODE})")
    if len(re.findall(r"\bWQ\s*\.\s*lab\s*\(", code)) != 1:
        out.append("call WQ.lab({...}) exactly once")
    for pattern, what in FORBIDDEN:
        if re.search(pattern, code, re.I if "http" in pattern else 0):
            out.append(f"not allowed: {what}")
    return out


def example_code() -> str:
    """The technique example shown to the lab engineer (placeholder content, nothing of it may be reused)."""
    return (KIT / "technique_lab.js").read_text(encoding="utf-8")


def physics_example() -> str:
    """The physics lab 2.1 (AGV emergency stop): a full working lab, kept for the checker's tests."""
    return (KIT / "demo_lab_2_1.js").read_text(encoding="utf-8")


def _js_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")


def page(labs: list[tuple[str, str]], *, course: list[str], chapter: list[str], lang: str = "zh",
         key: str = "wq-lab") -> str:
    """One lab page with the labs [(lesson number '2.1', code), ...] in order."""
    css = (KIT / "kit.css").read_text(encoding="utf-8")
    kit = (KIT / "kit.js").read_text(encoding="utf-8")
    title = [f"{chapter[0]} 虚拟实验", f"{chapter[1]} · Virtual lab"]
    esc = html.escape
    scripts = []
    for no, code in labs:
        lab_id = no.replace(".", "-")
        scripts.append(f"<script>\nWQ.begin({_js_string(lab_id)});\ntry {{\n{code}\n}} catch (e) {{ WQ.fail({_js_string(lab_id)}, e); }}\n</script>")
    return f"""<!doctype html>
<html lang="{'en' if lang == 'en' else 'zh-CN'}" data-lang="{'en' if lang == 'en' else 'zh'}" data-key="{esc(key)}" data-title="{esc(json.dumps(title, ensure_ascii=False))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{esc(title[0])}</title>
<style>
{css}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <div class="course bi" data-zh="{esc(course[0] + ' · ' + chapter[0])}" data-en="{esc(course[1] + ' · ' + chapter[1])}">{esc(course[0] + ' · ' + chapter[0])}</div>
      <h1 class="bi" data-zh="{esc(title[0])}" data-en="{esc(title[1])}">{esc(title[0])}</h1>
    </div>
    <div class="hright">
      <span class="course" id="progress"></span>
      <button class="lang" id="lang" aria-label="切换语言 / Switch language">EN</button>
    </div>
  </header>
  <nav class="tabs" id="tabs" role="tablist" aria-label="实验 Labs"></nav>
  <div id="labs"></div>
  <footer class="bi" data-zh="问渠 WenQuest 虚拟实验 · 与本章讲义、动画、实验指导书和实验报告模板配套使用。任务进度只保存在这台设备的浏览器里。"
    data-en="WenQuest virtual labs · use with this chapter's notes, animations, lab guides and report templates. Task progress is saved only in this browser.">问渠 WenQuest 虚拟实验</footer>
</div>
<script>
{kit}
</script>
{chr(10).join(scripts)}
<script>WQ.start();</script>
</body>
</html>
"""


class CheckError(Exception):
    def __init__(self, message: str, stage: str = "check"):
        super().__init__(message)
        self.stage = stage


async def trial_run(url: str, page_html: str, lab: str, timeout: float = 120.0) -> dict:
    """Run one lab in the lab checker (headless browser): {ok, problems, tasks, screenshot(bytes)}.
    Raises CheckError(stage="service") when the checker cannot be reached."""
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as c:
            r = await c.post(url.rstrip("/") + "/check", json={"html": page_html, "lab": lab})
    except httpx.HTTPError as e:
        raise CheckError(f"lab checker unreachable: {type(e).__name__}", "service") from e
    if r.status_code != 200:
        raise CheckError(f"lab checker answered {r.status_code}", "service")
    d = r.json()
    shot = base64.b64decode(d["screenshot"]) if d.get("screenshot") else b""
    return {"ok": bool(d.get("ok")), "problems": [str(p) for p in d.get("problems") or []][:30],
            "tasks": d.get("tasks") or {}, "screenshot": shot, "seconds": float(d.get("seconds") or 0)}
