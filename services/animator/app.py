"""WenQuest animation renderer.

Renders one Manim scene (`class Lesson(Base)`, written by the AI animator) to an MP4 and a poster.
It runs in its own container with no secrets and no internet, one render at a time, and checks the
code before running it: only Manim, the shared wq_anim parts, numpy and math, and no file, system
or introspection access.
"""
from __future__ import annotations

import ast
import asyncio
import base64
import os
import shutil
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

HERE = Path(__file__).parent
TIMEOUT = int(os.environ.get("WQ_RENDER_TIMEOUT", "420"))
MAX_CODE = 40_000

ALLOWED_IMPORTS = {"manim", "wq_anim", "numpy", "math", "random"}
FORBIDDEN_NAMES = {
    "open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "input", "breakpoint", "exit", "quit", "help", "memoryview", "dir", "type", "object", "classmethod",
    "staticmethod", "property", "ImageMobject", "SVGMobject", "Code", "config", "tempconfig", "logger", "console",
    "os", "sys", "subprocess", "shutil", "pathlib", "Path", "io", "builtins", "importlib", "socket", "ctypes",
    "__builtins__", "__loader__", "__spec__", "__file__",
}
FORBIDDEN_ATTRS = {
    "os", "sys", "subprocess", "shutil", "io", "builtins", "importlib", "pathlib", "socket", "ctypes",
    "load", "save", "savez", "savez_compressed", "savetxt", "loadtxt", "genfromtxt", "fromfile", "tofile", "memmap",
    "lib", "ctypeslib", "f2py", "distutils", "testing", "renderer", "file_writer", "add_sound", "save_image",
    "system", "popen", "remove", "unlink", "rmtree", "write_text", "write_bytes", "read_text", "read_bytes",
}


def check(code: str) -> str:
    """'' when the code may run, otherwise the reason (fed back to the animator)."""
    if len(code) > MAX_CODE:
        return f"code too long ({len(code)} characters, limit {MAX_CODE})"
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} (line {e.lineno})"
    has_lesson = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    return f"import of '{a.name}' is not allowed (only manim, wq_anim, numpy, math, random)"
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS or node.level:
                return f"import from '{node.module}' is not allowed (only manim, wq_anim, numpy, math, random)"
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES or node.id.startswith("__"):
                return f"name '{node.id}' is not allowed (line {node.lineno})"
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("_") or node.attr in FORBIDDEN_ATTRS:
                return f"attribute '.{node.attr}' is not allowed (line {node.lineno})"
        elif isinstance(node, (ast.Global, ast.Nonlocal, ast.AsyncFunctionDef, ast.Await)):
            return f"'{type(node).__name__}' is not allowed (line {node.lineno})"
        elif isinstance(node, ast.ClassDef) and node.name == "Lesson":
            has_lesson = True
    if not has_lesson:
        return "the scene must be defined as `class Lesson(Base):` with a construct(self) method"
    return ""


def _tail(text: str, lines: int = 30) -> str:
    """The useful end of Manim's output: the traceback without the progress bars."""
    keep = [ln for ln in text.splitlines() if ln.strip() and "it/s]" not in ln and "Animation" not in ln[:12]]
    return "\n".join(keep[-lines:])[-4000:]


async def _run(cmd: list[str], cwd: Path, timeout: int) -> tuple[int, str]:
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "HOME": str(cwd), "PYTHONPATH": str(HERE),
           "LANG": "C.UTF-8", "MPLCONFIGDIR": str(cwd)}
    p = await asyncio.create_subprocess_exec(*cmd, cwd=cwd, env=env, stdout=asyncio.subprocess.PIPE,
                                             stderr=asyncio.subprocess.STDOUT, start_new_session=True)
    try:
        out, _ = await asyncio.wait_for(p.communicate(), timeout)
    except asyncio.TimeoutError:
        try:
            os.killpg(p.pid, 9)
        except ProcessLookupError:
            pass
        await p.wait()
        return -9, f"render took longer than {timeout} s; make the animation shorter or simpler"
    return p.returncode or 0, out.decode("utf-8", "replace")


async def render(code: str, width: int = 1280, height: int = 720, fps: int = 30) -> dict:
    reason = check(code)
    if reason:
        return {"ok": False, "error": reason, "stage": "check"}
    work = Path(tempfile.mkdtemp(prefix="wqanim-"))
    t0 = time.monotonic()
    try:
        (work / "scene.py").write_text(code, encoding="utf-8")
        rc, log = await _run(["manim", "-r", f"{width},{height}", "--fps", str(fps), "--disable_caching",
                              "--media_dir", str(work / "media"), "-o", "lesson", "--progress_bar", "none",
                              "scene.py", "Lesson"], work, TIMEOUT)
        videos = list((work / "media").rglob("lesson.mp4"))
        if rc != 0 or not videos:
            return {"ok": False, "error": _tail(log) or f"manim exited with {rc}", "stage": "render"}
        video = videos[0]
        rc2, dur = await _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], work, 30)
        seconds = float(dur.strip() or 0) if rc2 == 0 else 0.0
        poster = work / "poster.png"
        await _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0.0, seconds * 0.45):.2f}", "-i", str(video),
                    "-frames:v", "1", str(poster)], work, 60)
        return {"ok": True, "seconds": round(seconds, 1), "render_seconds": round(time.monotonic() - t0, 1),
                "video": base64.b64encode(video.read_bytes()).decode(),
                "poster": base64.b64encode(poster.read_bytes()).decode() if poster.exists() else ""}
    finally:
        shutil.rmtree(work, ignore_errors=True)


class Job(BaseModel):
    code: str
    width: int = 1280
    height: int = 720
    fps: int = 30


app = FastAPI(title="WenQuest animator")
_lock = asyncio.Lock()
_state = {"busy": False, "done": 0, "failed": 0}


@app.get("/health")
async def health():
    return {"ok": True, **_state}


@app.post("/check")
async def check_only(job: Job):
    reason = check(job.code)
    return {"ok": not reason, "error": reason}


@app.post("/render")
async def render_job(job: Job):
    async with _lock:  # one render at a time: the site stays responsive
        _state["busy"] = True
        try:
            out = await render(job.code, min(job.width, 1920), min(job.height, 1080), min(job.fps, 30))
        finally:
            _state["busy"] = False
        _state["done" if out["ok"] else "failed"] += 1
        return out
