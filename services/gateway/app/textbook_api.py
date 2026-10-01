"""问渠教材阅读（第 7 轮第 3 步）。

The textbooks are built from the repository (textbook/, see textbook/README.md) by CI and copied to the server;
the gateway serves the built pages from WQ_TEXTBOOK_DIR (<dir>/<book>/web/index.json, <id>.html, <id>.mp.html,
<dir>/<book>/chNN.pdf). Decided by Eddie (第 7 轮 Q2): every signed-in user reads; the PDFs are for teachers.
"""

import asyncio
import json
import logging
import re
import time
from pathlib import Path
from typing import Annotated

from cryptography.fernet import InvalidToken
from fastapi import Depends
from fastapi.responses import FileResponse, HTMLResponse

from .moodle import EngineError
from .production import anim
from .session import Session

log = logging.getLogger("wenquest.textbook")

BOOK = re.compile(r"^[a-z][a-z0-9_-]{0,40}$")
SECTION = re.compile(r"^\d{1,3}\.(\d{1,3}|end)$")
PDF_TTL = 3600
MEDIA_TTL = 86400
LABBOX = re.compile(r"<div class='wq-media-box wq-labbox' data-lab='(\d+)-(\d+)'>(.*?)</div>", re.S)
BOX = re.compile(r"<div class='wq-media-box' data-anim='(\w+)' data-hash='(\w+)'>(.*?)</div>", re.S)


def media_dir(m, book: str) -> Path:
    return Path(m.state.settings.data_dir) / "textbook-media" / book


def pending(m) -> list[tuple[str, str, str]]:
    """(book, scene, hash) of every textbook animation whose video has not been made yet (and did not fail today)."""
    root = Path(m.state.settings.textbook_dir)
    out = []
    if not root.is_dir():
        return out
    for d in sorted(root.iterdir()):
        idx = d / "web" / "index.json"
        if not (BOOK.match(d.name) and idx.exists()):
            continue
        for name, h in (json.loads(idx.read_text(encoding="utf-8")).get("anims") or {}).items():
            md = media_dir(m, d.name)
            err = md / f"{name}-{h}.err"
            if (md / f"{name}-{h}.mp4").exists() or (err.exists() and time.time() - err.stat().st_mtime < 86400):
                continue
            if (d / "anim" / f"{name}.py").exists():
                out.append((d.name, name, h))
    return out


async def render_pending(m, limit: int = 0) -> int:
    """Render missing textbook animations one at a time with the animation service; returns how many were made."""
    url = m.state.settings.animator_url
    if not url:
        return 0
    made = 0
    for book, name, h in pending(m):
        code = (Path(m.state.settings.textbook_dir) / book / "anim" / f"{name}.py").read_text(encoding="utf-8")
        md = media_dir(m, book)
        md.mkdir(parents=True, exist_ok=True)
        try:
            video, poster, secs, _ = await anim.render(url, code, 900)
        except anim.RenderError as e:
            if e.stage == "service":              # renderer restarting or busy: try again on the next round
                log.warning("textbook animation %s/%s postponed: %s", book, name, e)
                return made
            (md / f"{name}-{h}.err").write_text(json.dumps({"error": str(e)[:2000], "at": time.time()}), encoding="utf-8")
            log.warning("textbook animation %s/%s failed: %s", book, name, str(e)[:300])
            continue
        (md / f"{name}-{h}.png").write_bytes(poster)
        tmp = md / f"{name}-{h}.mp4.tmp"
        tmp.write_bytes(video)
        tmp.replace(md / f"{name}-{h}.mp4")
        for old in md.glob(f"{name}-*"):          # older versions of this scene
            if h not in old.name:
                old.unlink(missing_ok=True)
        made += 1
        log.info("textbook animation %s/%s rendered (%.1f s)", book, name, secs)
        if limit and made >= limit:
            break
    return made


async def media_loop(m) -> None:
    await asyncio.sleep(20)
    while True:
        try:
            await render_pending(m)
        except Exception:  # noqa: BLE001 - keep the loop alive
            log.exception("textbook animation loop")
        await asyncio.sleep(300)


def register(app, m) -> None:
    def root() -> Path:
        return Path(m.state.settings.textbook_dir)

    def index(book: str) -> dict:
        if not BOOK.match(book):
            raise EngineError("not_found", "no such textbook", 404)
        p = root() / book / "web" / "index.json"
        if not p.exists():
            raise EngineError("not_found", "no such textbook", 404)
        return json.loads(p.read_text(encoding="utf-8"))

    def written(idx: dict) -> list[dict]:
        return [dict(s, chapter=c["no"]) for c in idx["chapters"] for s in c["sections"] if s.get("written")]

    @app.get("/api/v1/textbooks")
    async def textbooks(sess: Annotated[Session, Depends(m.current)]):
        out = []
        if root().is_dir():
            for d in sorted(root().iterdir()):
                if (d / "web" / "index.json").exists() and BOOK.match(d.name):
                    idx = index(d.name)
                    out.append({"book": d.name, "title": idx.get("title", d.name), "chapters": len(idx["chapters"]),
                                "sections": sum(len(c["sections"]) for c in idx["chapters"]), "written": len(written(idx))})
        return {"books": out}

    @app.get("/api/v1/textbooks/{book}")
    async def textbook(book: str, sess: Annotated[Session, Depends(m.current)]):
        idx = index(book)
        teacher = await m.can_create(sess.moodle_token)
        idx["teacher"] = teacher
        idx["pdf"] = [c for c in idx.get("pdf", []) if (root() / book / f"ch{int(c):02d}.pdf").exists()] if teacher else []
        anims = idx.pop("anims", {}) or {}
        idx["anims_ready"] = sum((media_dir(m, book) / f"{n}-{h}.mp4").exists() for n, h in anims.items())
        idx["anims_total"] = len(anims)
        return idx

    def media_link(book: str, name: str, h: str, kind: str) -> str:
        tok = m.state.codec.fernet.encrypt(json.dumps({"b": book, "n": name, "h": h, "k": kind}).encode()).decode()
        return f"{m.state.settings.public_url.rstrip('/')}/api/v1/textbook-media/{tok}"

    def with_media(book: str, html_: str, mp: bool) -> str:
        """Put the rendered animations into the page; a scene not rendered yet keeps its box."""
        def one(mt):
            name, h, label = mt.group(1), mt.group(2), mt.group(3)
            md = media_dir(m, book)
            if not (md / f"{name}-{h}.mp4").exists():
                return mt.group(0).replace(label, label + "（动画制作中）")
            poster = media_link(book, name, h, "png")
            if mp:
                return f"<img class='wq-poster' src='{poster}'/><p class='wq-note'>{label}：请在网页端观看动画</p>"
            return (f"<video class='wq-video' controls preload='none' playsinline poster='{poster}' "
                    f"src='{media_link(book, name, h, 'mp4')}'></video>")
        html_ = BOX.sub(one, html_)

        def lab(mt):
            ch, k, label = mt.group(1), mt.group(2), mt.group(3)
            page = root() / book / "lab" / f"ch{int(ch):02d}.html"
            if not page.exists():
                return mt.group(0)
            if mp:
                return f"<p class='wq-note'>{label}：请在网页端打开虚拟实验</p>"
            tok = m.state.codec.fernet.encrypt(json.dumps({"b": book, "c": int(ch)}).encode()).decode()
            url = f"{m.state.settings.public_url.rstrip('/')}/api/v1/textbook-lab/{tok}#lab-{ch}-{k}"
            return f"<a class='wq-labbtn' href='{url}' target='_blank' rel='noopener'>▶ 打开{label}</a>"
        return LABBOX.sub(lab, html_)

    @app.get("/api/v1/textbook-lab/{signed}")
    async def lab_page(signed: str):
        """A chapter's virtual-lab page (built with the platform's lab kit; it loads nothing from outside)."""
        from .production import labs as labkit
        try:
            d = json.loads(m.state.codec.fernet.decrypt(signed.encode(), ttl=MEDIA_TTL))
        except (InvalidToken, ValueError):
            raise EngineError("link_expired", "link expired", 410)
        if not BOOK.match(d["b"]):
            raise EngineError("not_found", "no such lab", 404)
        p = root() / d["b"] / "lab" / f"ch{int(d['c']):02d}.html"
        if not p.exists():
            raise EngineError("not_found", "no such lab", 404)
        return HTMLResponse(p.read_text(encoding="utf-8"), headers={"Content-Security-Policy": labkit.CSP,
                                                                     "Cache-Control": "private, max-age=3600"})

    @app.get("/api/v1/textbook-media/{signed}")
    async def media(signed: str):
        try:
            d = json.loads(m.state.codec.fernet.decrypt(signed.encode(), ttl=MEDIA_TTL))
        except (InvalidToken, ValueError):
            raise EngineError("link_expired", "link expired", 410)
        if not (BOOK.match(d["b"]) and re.fullmatch(r"\w+", d["n"]) and re.fullmatch(r"\w+", d["h"]) and d["k"] in ("mp4", "png")):
            raise EngineError("not_found", "no such file", 404)
        p = media_dir(m, d["b"]) / f"{d['n']}-{d['h']}.{d['k']}"
        if not p.exists():
            raise EngineError("not_found", "no such file", 404)
        return FileResponse(p, media_type="video/mp4" if d["k"] == "mp4" else "image/png",
                            headers={"Cache-Control": "private, max-age=86400"})

    @app.get("/api/v1/textbooks/{book}/sections/{sid}")
    async def section(book: str, sid: str, sess: Annotated[Session, Depends(m.current)], mp: bool = False):
        idx = index(book)
        if not SECTION.match(sid):
            raise EngineError("not_found", "no such section", 404)
        order = written(idx)
        ids = [s["id"] for s in order]
        if sid not in ids:
            raise EngineError("not_written", "this section has not been written yet", 404)
        p = root() / book / "web" / (f"{sid}.mp.html" if mp else f"{sid}.html")
        if not p.exists():
            p = root() / book / "web" / f"{sid}.html"
        i = ids.index(sid)
        cur = order[i]
        chapter = next(c for c in idx["chapters"] if c["no"] == cur["chapter"])
        return {"id": sid, "title": cur["title"], "chapter": {"no": chapter["no"], "title": chapter["title"]},
                "html": with_media(book, p.read_text(encoding="utf-8"), mp),
                "prev": order[i - 1] if i > 0 else None, "next": order[i + 1] if i + 1 < len(order) else None}

    @app.get("/api/v1/textbooks/{book}/pdf/{chapter}")
    async def pdf_link(book: str, chapter: int, sess: Annotated[Session, Depends(m.current)]):
        """A short-lived download link for a chapter's PDF (teachers only)."""
        index(book)
        if not await m.can_create(sess.moodle_token):
            raise EngineError("forbidden", "the PDF is for teachers", 403)
        if not (root() / book / f"ch{chapter:02d}.pdf").exists():
            raise EngineError("not_found", "no PDF for this chapter", 404)
        tok = m.state.codec.fernet.encrypt(json.dumps({"b": book, "c": chapter, "u": sess.user_id, "t": time.time()}).encode()).decode()
        return {"url": f"{m.state.settings.public_url.rstrip('/')}/api/v1/textbook-pdf/{tok}"}

    @app.get("/api/v1/textbook-pdf/{signed}")
    async def pdf_file(signed: str):
        try:
            d = json.loads(m.state.codec.fernet.decrypt(signed.encode(), ttl=PDF_TTL))
        except (InvalidToken, ValueError):
            raise EngineError("link_expired", "link expired", 410)
        idx = index(d["b"])
        p = root() / d["b"] / f"ch{int(d['c']):02d}.pdf"
        if not p.exists():
            raise EngineError("not_found", "no PDF for this chapter", 404)
        title = next((c["title"] for c in idx["chapters"] if c["no"] == int(d["c"])), "")
        name = f"{idx.get('title', '')}-第{int(d['c'])}章-{title}.pdf"
        return FileResponse(p, media_type="application/pdf", filename=name)
