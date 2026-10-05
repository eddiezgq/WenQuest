"""Interest registration for the physical sewing-machine kits (第 20 轮 5.2).

The public site has a bilingual page (site/kits.html) where learners and schools say which kit they would want,
at what price band, how many, from where. Nothing is sold: the answers decide whether, and how many, kits to stock.

  POST /api/v1/public/kit-interest     no login; validated, rate-limited per network address, a honeypot field
  GET  /api/v1/admin/kit-interest      administrators: the registrations and a summary (?format=csv to download)

Kept in <data_dir>/kit-interest.db (SQLite). Only what the form asks for is stored, plus time and language;
the network address is used for rate limiting in memory and is not stored.
"""

import csv
import io
import re
import sqlite3
import time
from collections import Counter, deque
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request, Response
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

KITS = ("A", "A+", "B", "C")                       # 机头拆装套件、开窗剖切展示机、整机、控制套件
WHO = ("self", "school", "company", "other")
MACHINES = ("lockstitch", "overlock", "pattern")
BANDS = ("1", "2", "3", "4")                        # price bands as shown on the page, in the visitor's currency
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,24}$")
IP_HOURLY = 8


class InterestIn(BaseModel):
    kits: list[str] = Field(min_length=1, max_length=4)
    machines: list[str] = Field(default_factory=lambda: ["lockstitch"], max_length=3)
    band: str = ""
    currency: str = Field(default="USD", max_length=3)
    who: str
    country: str = Field(min_length=1, max_length=60)
    qty: int = Field(default=1, ge=1, le=500)
    email: str = Field(max_length=254)
    note: str = Field(default="", max_length=1000)
    lang: str = Field(default="zh", max_length=5)
    consent: bool = False
    website: str = ""                                # honeypot: people never fill it


def register(app, m) -> None:
    state = m.state
    hits: dict[str, deque] = {}

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "kit-interest.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists interest(id integer primary key, ts integer, kits text, machines text, band text,
                     currency text, who text, country text, qty integer, email text, note text, lang text)""")
        return c

    def ip(req: Request) -> str:
        fwd = req.headers.get("x-forwarded-for", "")
        return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "?"

    @app.post("/api/v1/public/kit-interest")
    async def submit(body: InterestIn, req: Request):
        if body.website:                               # a bot filled the hidden field: pretend all went well
            return {"ok": True}
        now = time.time()
        q = hits.setdefault(ip(req), deque())
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= IP_HOURLY:
            raise EngineError("rate_limited", "too many registrations from this network; try again later", 429)
        kits = [k for k in dict.fromkeys(body.kits) if k in KITS]
        machines = [k for k in dict.fromkeys(body.machines) if k in MACHINES] or ["lockstitch"]
        email = body.email.strip().lower()
        if not kits:
            raise EngineError("bad_kits", "choose at least one kit", 400)
        if body.who not in WHO:
            raise EngineError("bad_who", "who is it for", 400)
        if body.band and body.band not in BANDS:
            raise EngineError("bad_band", "price band", 400)
        if not EMAIL_RE.match(email):
            raise EngineError("bad_email", "email address", 400)
        if not body.consent:
            raise EngineError("consent_required", "please agree to be contacted about the kits", 400)
        q.append(now)
        with db() as c:
            c.execute("insert into interest(ts,kits,machines,band,currency,who,country,qty,email,note,lang) values(?,?,?,?,?,?,?,?,?,?,?)",
                      (int(now), ",".join(kits), ",".join(machines), body.band, body.currency.upper()[:3], body.who,
                       body.country.strip()[:60], body.qty, email, body.note.strip()[:1000], "en" if body.lang.startswith("en") else "zh"))
        return {"ok": True}

    @app.get("/api/v1/admin/kit-interest")
    async def listing(sess: Annotated[Session, Depends(m.current)], format: str = "json"):
        await m.accounts_require_admin(sess)
        with db() as c:
            rows = [dict(r) for r in c.execute("select * from interest order by ts desc")]
        if format == "csv":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["time", "kits", "machines", "price_band", "currency", "who", "country", "qty", "email", "note", "lang"])
            for r in rows:
                w.writerow([time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["ts"])), r["kits"], r["machines"], r["band"], r["currency"],
                            r["who"], r["country"], r["qty"], r["email"], r["note"], r["lang"]])
            return Response("﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                            headers={"Content-Disposition": "attachment; filename=kit-interest.csv"})
        kits = Counter(k for r in rows for k in r["kits"].split(","))
        units = Counter()
        for r in rows:
            for k in r["kits"].split(","):
                units[k] += r["qty"]
        return {"count": len(rows), "kits": dict(kits), "units": dict(units),
                "who": dict(Counter(r["who"] for r in rows)), "country": dict(Counter(r["country"] for r in rows).most_common(20)),
                "rows": rows[:500]}
