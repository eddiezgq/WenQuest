"""Demo and contact requests from the China website 问渠科技 (第 48 轮).

The form on site/cn/contact/ posts here. Nothing leaves the server: requests are kept in <data_dir>/demo-request.db
(SQLite) and administrators read them on the platform (or download a CSV). Only what the form asks for is stored, plus
the time; the network address is used for rate limiting in memory and is not stored (个人信息保护法: 最小必要).

  POST /api/v1/public/demo-request     no login; validated, rate-limited per network address, a honeypot field
  POST /api/v1/public/demo-request/code   round 96: a 6-digit code to the email of a trial request; a right code
                                       opens the trial at once (orgs.auto_open) unless a limit sends it to the administrator
  GET  /api/v1/admin/demo-request      administrators: the requests (?format=csv to download)

Error details are in Chinese: the page shows them to the visitor as they are.
"""

import csv
import hashlib
import hmac
import io
import re
import secrets
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
            "学习系统", "电子教材开发", "虚拟实验开发", "数字工厂开发", "CAD/CAM/CAE 集成化解决方案", "技术服务", "咨询",
            "问渠 AI 学习平台", "数字工厂教学版与虚拟实验室")           # 最后两项是第 48 轮的旧名称，旧页面提交时仍认
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
    trial: bool = False                              # round 50: the organisation asks for online trial accounts
    seats: int = Field(default=0, ge=0, le=5)
    code: str = Field(default="", max_length=8)      # round 96: the email code of a trial request
    website: str = ""                                # honeypot: people never fill it


class CodeIn(BaseModel):
    email: str = Field(min_length=3, max_length=254)


def register(app, m) -> None:
    state = m.state
    hits: dict[str, deque] = {}

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "demo-request.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists request(id integer primary key, ts integer, org text, name text, phone text,
                     email text, industry text, products text, note text, trial integer default 0, seats integer default 0)""")
        c.execute("create table if not exists vcode(email text, hash text, expires real, tries integer default 0, created real)")
        cols = {r[1] for r in c.execute("pragma table_info(request)")}
        for col in ("trial", "seats"):                 # databases from round 48
            if col not in cols:
                c.execute(f"alter table request add column {col} integer default 0")
        return c

    def ip(req: Request) -> str:
        fwd = req.headers.get("x-forwarded-for", "")
        return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "?"

    def code_hash(email: str, code: str) -> str:
        return hmac.new(state.settings.secret_key.encode(), f"trial|{email}|{code}".encode(), hashlib.sha256).hexdigest()

    def cn() -> bool:
        return state.settings.region.strip().lower() == "cn"

    @app.post("/api/v1/public/demo-request/code")
    async def trial_code(body: CodeIn, req: Request):
        """Round 96: prove the email of a trial request is the applicant's own."""
        email = body.email.strip().lower()
        if not EMAIL_RE.match(email):
            raise EngineError("bad_email", "邮箱格式不对", 400)
        now = time.time()
        q = hits.setdefault("code:" + ip(req), deque())
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= 10:
            raise EngineError("rate_limited", "请求太频繁，请一小时后再试", 429)
        with db() as c:
            last = c.execute("select max(created) from vcode where email=?", (email,)).fetchone()[0]
            if last and now - last < 60:
                raise EngineError("code_too_soon", f"请 {int(60 - (now - last))} 秒后再获取", 429)
            code = f"{secrets.randbelow(10**6):06d}"
            c.execute("insert into vcode(email, hash, expires, created) values(?,?,?,?)", (email, code_hash(email, code), now + 600, now))
            c.execute("delete from vcode where created<?", (now - 86400,))
        q.append(now)
        ok = await state.mailer.send(email, "问渠在线体验：邮箱验证码",
                                     f"你的验证码是：\n\n{code}\n\n10 分钟内有效。如果不是你本人在问渠科技官网申请在线体验，请忽略这封邮件。")
        if not ok:
            raise EngineError("mail_failed", "邮件没有发出去，请稍后再试，或直接打电话给我们", 502)
        return {"sent": True}

    def code_ok(email: str, code: str) -> bool:
        now = time.time()
        with db() as c:
            r = c.execute("select rowid, hash from vcode where email=? and expires>? and tries<5 order by created desc limit 1",
                          (email, now)).fetchone()
            if not r:
                return False
            if not hmac.compare_digest(r["hash"], code_hash(email, code.strip())):
                c.execute("update vcode set tries=tries+1 where rowid=?", (r["rowid"],))
                return False
            c.execute("update vcode set expires=0 where email=?", (email,))
        return True

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
        auto = body.trial and cn() and bool(getattr(m, "orgs_auto_on", lambda: False)())
        if auto:                                       # round 96: a trial is opened at once once the email is proven
            if not email:
                raise EngineError("bad_email", "申请在线体验请填写邮箱，账号会发到这个邮箱", 400)
            if not body.code.strip():
                raise EngineError("code_required", "请先点“获取验证码”，填写邮箱收到的 6 位验证码", 400)
            if not code_ok(email, body.code):
                raise EngineError("code_wrong", "验证码不对或已过期，请重新获取", 400)
        now = time.time()
        q = hits.setdefault(ip(req), deque())
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= IP_HOURLY:
            raise EngineError("rate_limited", "提交太频繁，请稍后再试，或直接打电话联系我们", 429)
        q.append(now)
        products = [p for p in dict.fromkeys(body.products) if p in PRODUCTS]
        with db() as c:
            cur = c.execute("insert into request(ts,org,name,phone,email,industry,products,note,trial,seats) values(?,?,?,?,?,?,?,?,?,?)",
                            (int(now), org[:100], name[:40], phone, email, body.industry.strip()[:60], "、".join(products),
                             body.note.strip()[:2000], 1 if body.trial else 0, (body.seats or 5) if body.trial else 0))
            rid = cur.lastrowid
        if auto:
            why = await m.orgs_auto_open(org[:100], name[:40], phone, email, body.seats or 5, rid, ip(req))
            return {"ok": True, "opened": not why, "manual": why}
        return {"ok": True}

    @app.get("/api/v1/public/site")
    async def site():
        """What the platform shows about the operator (round 48): in China the brand, company and filing numbers for the
        footer, and that AI output is labelled; elsewhere just the region (the US platform looks as before)."""
        st = state.settings
        if st.region.strip().lower() != "cn":
            return {"region": "us"}
        return {"region": "cn", "brand": st.brand or "问渠科技", "company": st.company, "icp": st.icp, "psb": st.psb,
                "ai_reg": st.ai_reg, "ai_model": "DeepSeek", "ai_label": True,
                "signup": bool(getattr(m, "phone_signup_open", lambda: False)()),   # 第 108 轮 D-8：手机号注册
                **getattr(m, "login_methods", dict)()}                              # 第 108 轮：手机号、微信登录

    @app.get("/api/v1/admin/demo-request")
    async def listing(sess: Annotated[Session, Depends(m.current)], format: str = "json"):
        await m.accounts_require_admin(sess)
        with db() as c:
            rows = [dict(r) for r in c.execute("select * from request order by id desc")]
        if format == "csv":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["时间（UTC）", "单位", "姓名", "电话", "邮箱", "行业", "想了解", "需求说明", "申请体验", "账号数"])
            for r in rows:
                w.writerow([time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["ts"])), r["org"], r["name"], r["phone"], r["email"],
                            r["industry"], r["products"], r["note"], "是" if r["trial"] else "", r["seats"] or ""])
            return Response("﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                            headers={"Content-Disposition": "attachment; filename=demo-requests.csv"})
        return {"count": len(rows), "rows": rows[:500]}
