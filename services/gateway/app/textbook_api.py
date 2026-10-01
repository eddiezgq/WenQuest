"""问渠教材阅读（第 7 轮第 3 步）。

The textbooks are built from the repository (textbook/, see textbook/README.md) by CI and copied to the server;
the gateway serves the built pages from WQ_TEXTBOOK_DIR (<dir>/<book>/web/index.json, <id>.html, <id>.mp.html,
<dir>/<book>/chNN.pdf). Decided by Eddie (第 7 轮 Q2): every signed-in user reads; the PDFs are for teachers.
"""

import json
import re
import time
from pathlib import Path
from typing import Annotated

from cryptography.fernet import InvalidToken
from fastapi import Depends
from fastapi.responses import FileResponse

from .moodle import EngineError
from .session import Session

BOOK = re.compile(r"^[a-z][a-z0-9_-]{0,40}$")
SECTION = re.compile(r"^\d{1,3}\.\d{1,3}$")
PDF_TTL = 3600


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
        return idx

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
                "html": p.read_text(encoding="utf-8"),
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
