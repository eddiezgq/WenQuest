"""Demo and contact requests from the China website 问渠科技 (第 48 轮).

The form on site/cn/contact/ posts here. Nothing leaves the server: requests are kept in <data_dir>/demo-request.db
(SQLite) and administrators read them on the platform (or download a CSV). Only what the form asks for is stored, plus
the time; the network address is used for rate limiting in memory and is not stored (个人信息保护法: 最小必要).

  POST /api/v1/public/demo-request     no login; validated, rate-limited per network address, a honeypot field
  GET  /api/v1/admin/demo-request      administrators: the requests (?format=csv to download)

Error details are in Chinese: the page shows them to the visitor as they are.
"""

import csv
import io
import re
import sqlite3
import time
from collections import deque
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request, Response
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

PRODUCTS = ("问渠质量 ERP", "问渠数字工厂集成平台", "缝纫机设计与制造软件", "凸轮设计与制造软件", "制造业专用软件定制",
            "技术服务", "问渠 AI 学习平台", "数字工厂教学版与虚拟实验室", "咨询")
PHONE_RE = re.compile(r"^(?:\+?86[- ]?)?(?:1[3-9]\d{9}|0\d{2,3}-?\d{7,8}(?:-\d{1,6})?)$")
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,24}$")
IP_HOURLY = 6


class DemoIn(BaseModel):
    org: str = Field(default="", max_length=100)
    name: str = Field(default="", max_length=40)
    phone: str = Field(default="", max_length=20)
    email: str = Field(default="", max_length=254)
    industry: str = Field(default="", max_length=60)
    products: list[str] = Field(default_factory=list, max_length=len(PRODUCTS))
    note: str = Field(default="", max_length=2000)
    consent: bool = False
    website: str = ""                                # honeypot: people never fill it


def register(app, m) -> None:
    state = m.state
    hits: dict[str, deque] = {}

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "demo-request.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists request(id integer primary key, ts integer, org text, name text, phone text,
                     email text, industry text, products text, note text)""")
        return c

    def ip(req: Request) -> str:
        fwd = req.headers.get("x-forwarded-for", "")
        return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "?"

    @app.post("/api/v1/public/demo-request")
    async def submit(body: DemoIn, req: Request):
        if body.website:                               # a bot filled the hidden field: pretend all went well
            return {"ok": True}
        org, name = body.org.strip(), body.name.strip()
        phone = re.sub(r"\s+", "", body.phone)
        email = body.email.strip().lower()
        if not org:
            raise EngineError("bad_org", "请填写单位名称", 400)
        if not name:
            raise EngineError("bad_name", "请填写姓名", 400)
        if not PHONE_RE.match(phone):
            raise EngineError("bad_phone", "请填写正确的手机号或带区号的座机号", 400)
        if email and not EMAIL_RE.match(email):
            raise EngineError("bad_email", "邮箱格式不对", 400)
        if not body.consent:
            raise EngineError("consent_required", "请先阅读并同意《隐私政策》", 400)
        now = time.time()
        q = hits.setdefault(ip(req), deque())
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= IP_HOURLY:
            raise EngineError("rate_limited", "提交太频繁，请稍后再试，或直接打电话联系我们", 429)
        q.append(now)
        products = [p for p in dict.fromkeys(body.products) if p in PRODUCTS]
        with db() as c:
            c.execute("insert into request(ts,org,name,phone,email,industry,products,note) values(?,?,?,?,?,?,?,?)",
                      (int(now), org[:100], name[:40], phone, email, body.industry.strip()[:60], "、".join(products),
                       body.note.strip()[:2000]))
        return {"ok": True}

    @app.get("/api/v1/public/site")
    async def site():
        """What the platform shows about the operator (round 48): in China the brand, company and filing numbers for the
        footer, and that AI output is labelled; elsewhere just the region (the US platform looks as before)."""
        st = state.settings
        if st.region.strip().lower() != "cn":
            return {"region": "us"}
        return {"region": "cn", "brand": st.brand or "问渠科技", "company": st.company, "icp": st.icp, "psb": st.psb,
                "ai_reg": st.ai_reg, "ai_model": "DeepSeek", "ai_label": True}

    @app.get("/api/v1/admin/demo-request")
    async def listing(sess: Annotated[Session, Depends(m.current)], format: str = "json"):
        await m.accounts_require_admin(sess)
        with db() as c:
            rows = [dict(r) for r in c.execute("select * from request order by id desc")]
        if format == "csv":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["时间（UTC）", "单位", "姓名", "电话", "邮箱", "行业", "想了解", "需求说明"])
            for r in rows:
                w.writerow([time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["ts"])), r["org"], r["name"], r["phone"], r["email"],
                            r["industry"], r["products"], r["note"]])
            return Response("﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                            headers={"Content-Disposition": "attachment; filename=demo-requests.csv"})
        return {"count": len(rows), "rows": rows[:500]}
