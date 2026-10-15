"""Microelectronics labs: the Verilog synthesis service for phones (第 17 轮附 3.3).

The Verilog lab page synthesises in the browser (WebAssembly Yosys, ~16 MB) on computers; on phones it sends the
source here and the gateway forwards it to the internal micro-synth service (services/micro-synth), then the page
simulates the returned netlist with DigitalJS as before.

Two ways in:
  POST /api/v1/micro/synth                 — a signed-in user (the WenQuest app);
  GET  /api/v1/micro/synth-link            — a personal, signed link (12 h) to the Verilog lab page served by the
                                             gateway, for a course or textbook to open;
  GET  /api/v1/micro-verilog/{signed}      — that page: the built lab (app/static/micro_verilog.html, copied by
                                             labs/micro/tools/build.js) with its synthesis address set to the next route;
  POST /api/v1/micro-synth/{signed}        — the lab page posts there (same site; no session header inside an iframe).
Limits on top of the service's own (64 KB, 20 s, 2 at a time): 10 syntheses per user per minute.
"""

import json
import time
from pathlib import Path
from collections import defaultdict, deque
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

PER_MINUTE = 10
LINK_TTL = 12 * 3600
MAX_SOURCE = 64 * 1024
PAGE = Path(__file__).resolve().parent / "static" / "micro_verilog.html"


class SynthIn(BaseModel):
    source: str = Field(min_length=1, max_length=MAX_SOURCE)
    top: str | None = Field(default=None, max_length=64)


def register(app, m) -> None:
    current = m.current
    state = m.state
    recent: dict[str, deque] = defaultdict(deque)

    def allow(user: str) -> None:
        now = time.monotonic()
        q = recent[user]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= PER_MINUTE:
            raise EngineError("rate_limited", f"at most {PER_MINUTE} syntheses a minute; wait a little", 429)
        q.append(now)

    async def forward(sess: Session, body: SynthIn) -> dict:
        url = state.settings.microsynth_url
        if not url:
            raise EngineError("unavailable", "server synthesis is not set up on this site; use a computer browser", 503)
        allow(str(sess.user_id))
        try:
            r = await state.http.post(url.rstrip("/") + "/synth", json=body.model_dump(), timeout=state.settings.microsynth_timeout)
        except httpx.HTTPError as e:
            raise EngineError("unavailable", "the synthesis service did not answer", 503) from e
        if r.status_code == 503:
            raise EngineError("busy", "the synthesis service is busy, try again in a minute", 503)
        try:
            return r.json()
        except ValueError as e:
            raise EngineError("unavailable", "the synthesis service gave no answer", 502) from e

    @app.post("/api/v1/micro/synth")
    async def synth(body: SynthIn, sess: Annotated[Session, Depends(current)]):
        return await forward(sess, body)

    def signed_session(signed: str) -> Session:
        try:
            d = json.loads(state.codec.fernet.decrypt(signed.encode(), ttl=LINK_TTL))
        except Exception as e:  # noqa: BLE001
            raise EngineError("link_expired", "link expired; open the lab again", 410) from e
        sess = state.codec.read(d.get("s", "")) if d.get("k") == "synth" else None
        if not sess:
            raise EngineError("link_expired", "link expired; open the lab again", 410)
        return sess

    @app.get("/api/v1/micro/synth-link")
    async def synth_link(sess: Annotated[Session, Depends(current)]):
        tok = state.codec.fernet.encrypt(json.dumps({"s": state.codec.issue(sess), "k": "synth"}).encode()).decode()
        base = (state.settings.public_url or state.settings.app_url).rstrip("/")
        return {"url": f"{base}/api/v1/micro-verilog/{tok}", "synth_url": f"{base}/api/v1/micro-synth/{tok}",
                "expires_in": LINK_TTL, "on": bool(state.settings.microsynth_url)}

    @app.get("/api/v1/micro-verilog/{signed}")
    async def verilog_page(signed: str):
        signed_session(signed)
        if not PAGE.exists():
            raise EngineError("unavailable", "the Verilog lab page is not installed on this site", 503)
        conf = (f"<script>window.WQ_SYNTH_URL = {json.dumps('/api/v1/micro-synth/' + signed)};"
                f"window.WQ_SYNTH_ON = {json.dumps(bool(state.settings.microsynth_url))};"
                # 国内部署（第 34 轮）：仿真器从自己的服务器取，综合走服务器（公共 CDN 在国内太慢）
                + ("window.WQ_ENGINE_BASE = '/vendor/npm/';window.WQ_SYNTH_PREFER = 'server';"
                   if state.settings.region.strip().lower() == "cn" else "")
                + "</script>")
        page = PAGE.read_text(encoding="utf-8").replace("<head>", "<head>" + conf, 1)
        return HTMLResponse(page, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})

    @app.post("/api/v1/micro-synth/{signed}")
    async def synth_signed(signed: str, body: SynthIn):
        return await forward(signed_session(signed), body)
