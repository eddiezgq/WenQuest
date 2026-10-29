"""China server: online trial accounts are given to organisations, not individuals (round 50).

On a server with WQ_REGION=cn the platform is an online trial for schools and companies. An administrator opens a
trial for an organisation (usually from a demo request on the website), gives it a few accounts, and the trial runs
for a fixed number of days. Individuals cannot sign up there.

  limits (settings): at most cn_max_orgs organisations at a time (expired or stopped ones do not count),
                     cn_org_seats accounts each by default (an administrator may raise it to cn_org_seats_max),
                     cn_trial_days days of trial (an administrator may extend it)
  GET  /api/v1/admin/orgs                          organisations, their accounts, the counts and who expires soon
  POST /api/v1/admin/orgs                          open a trial (optionally from a demo request)
  PUT  /api/v1/admin/orgs/{oid}                    change seats, extend, stop or restart
  POST /api/v1/admin/orgs/{oid}/members            add an account: a Moodle account (may create courses) with a
                                                   generated password that is shown once
  PUT  /api/v1/admin/orgs/{oid}/members/{uid}      stop or restart one account
  POST /api/v1/admin/orgs/{oid}/members/{uid}/password   a new generated password, shown once

The gate: on sign-in and on every request, an account of an organisation whose trial has ended or was stopped is
refused with org_expired. The sweep also suspends such accounts in Moodle (so the classic interface refuses them too)
and restores them when the trial is extended. Accounts that belong to no organisation (the administrators) pass.
Elsewhere (region us) none of this is active and the endpoints answer 404.
"""

import secrets
import sqlite3
import string
import time
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

DAY = 86400
KINDS = ("school", "company", "other")


class OrgIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    kind: str = Field(default="company", pattern="^(school|company|other)$")
    contact: str = Field(default="", max_length=40)
    phone: str = Field(default="", max_length=20)
    email: str = Field(default="", max_length=254)
    seats: int | None = Field(default=None, ge=1, le=100)
    days: int | None = Field(default=None, ge=1, le=3650)
    request_id: int | None = None
    note: str = Field(default="", max_length=500)


class OrgChange(BaseModel):
    seats: int | None = Field(default=None, ge=1, le=100)
    extend_days: int | None = Field(default=None, ge=1, le=3650)
    status: str | None = Field(default=None, pattern="^(active|stopped)$")
    note: str | None = Field(default=None, max_length=500)


class MemberIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    phone: str = Field(min_length=5, max_length=20)
    email: str = Field(min_length=3, max_length=254)


class MemberChange(BaseModel):
    stopped: bool


def gen_password() -> str:
    """12 characters, letters and digits (the platform's rule: at least one of each); no look-alike characters."""
    alpha = "".join(c for c in string.ascii_letters if c not in "lIO")
    digits = "23456789"
    while True:
        pw = "".join(secrets.choice(alpha + digits) for _ in range(12))
        if any(c in digits for c in pw) and any(c in alpha for c in pw):
            return pw


def register(app, m) -> None:
    state = m.state

    def cn() -> bool:
        return state.settings.region.strip().lower() == "cn"

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "orgs.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists org(id integer primary key, name text, kind text, contact text, phone text,
                     email text, seats integer, expires integer, status text, request_id integer, note text, created integer)""")
        c.execute("""create table if not exists member(userid integer primary key, org_id integer, name text, phone text,
                     email text, stopped integer default 0, created integer)""")
        return c

    def need_cn():
        if not cn():
            raise EngineError("not_found", "only on the China server", 404)

    def live(o) -> bool:
        return o["status"] == "active" and o["expires"] > time.time()

    def counts(c) -> dict:
        now = time.time()
        live_n = c.execute("select count(*) from org where status='active' and expires>?", (now,)).fetchone()[0]
        return {"live": live_n, "max": state.settings.cn_max_orgs}

    def org_out(c, o) -> dict:
        mem = [dict(r) for r in c.execute("select * from member where org_id=? order by created", (o["id"],))]
        days = (o["expires"] - time.time()) / DAY
        return {**dict(o), "live": live(o), "days_left": max(0, int(days + 0.999)) if days > 0 else 0,
                "members": mem, "used": len(mem)}

    def get_org(c, oid: int):
        o = c.execute("select * from org where id=?", (oid,)).fetchone()
        if not o:
            raise EngineError("not_found", "no such organisation", 404)
        return o

    # ------------------------------------------------------------------ the gate

    def gate(user_id: int) -> None:
        """Refuse an account whose organisation's trial has ended or was stopped (China server only)."""
        if not cn():
            return
        with db() as c:
            r = c.execute("select m.stopped, o.status, o.expires from member m join org o on o.id=m.org_id where m.userid=?",
                          (user_id,)).fetchone()
        if not r:
            return
        if r["stopped"]:
            raise EngineError("account_stopped", "此账号已停用，请联系问渠科技", 403)
        if r["status"] != "active" or r["expires"] <= time.time():
            raise EngineError("org_expired", "体验已到期，请联系问渠科技续期", 403)

    m.org_gate = gate

    async def sweep() -> None:
        """Keep Moodle's suspension in step with the trials: suspend accounts of ended or stopped trials, restore
        accounts of live ones (except accounts stopped one by one)."""
        if not cn():
            return
        with db() as c:
            rows = [dict(r) for r in c.execute(
                "select m.userid, m.stopped, o.status, o.expires from member m join org o on o.id=m.org_id")]
        now = time.time()
        for r in rows:
            off = bool(r["stopped"]) or r["status"] != "active" or r["expires"] <= now
            try:
                await m.accounts_svc("local_wenquest_account_update", userid=r["userid"], suspended=1 if off else 0)
            except EngineError:
                pass

    m.orgs_sweep = sweep

    # ------------------------------------------------------------------ administration

    @app.get("/api/v1/admin/orgs")
    async def list_orgs(sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        now = time.time()
        with db() as c:
            orgs = [org_out(c, o) for o in c.execute("select * from org order by created desc")]
            cnt = counts(c)
        soon = [o["id"] for o in orgs if o["live"] and o["expires"] - now < 7 * DAY]
        return {**cnt, "default_seats": state.settings.cn_org_seats, "max_seats": state.settings.cn_org_seats_max,
                "trial_days": state.settings.cn_trial_days, "expiring": soon, "orgs": orgs}

    @app.post("/api/v1/admin/orgs")
    async def open_org(body: OrgIn, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        st = state.settings
        seats = body.seats or st.cn_org_seats
        if seats > st.cn_org_seats_max:
            raise EngineError("too_many_seats", f"每家单位最多 {st.cn_org_seats_max} 个账号", 400)
        now = time.time()
        with db() as c:
            if counts(c)["live"] >= st.cn_max_orgs:
                raise EngineError("org_limit", f"体验单位已满 {st.cn_max_orgs} 家，请先停用已到期的单位", 409)
            if c.execute("select 1 from org where name=? and status='active' and expires>?", (body.name.strip(), now)).fetchone():
                raise EngineError("org_exists", "这家单位已在体验中", 409)
            cur = c.execute("insert into org(name,kind,contact,phone,email,seats,expires,status,request_id,note,created) "
                            "values(?,?,?,?,?,?,?,'active',?,?,?)",
                            (body.name.strip(), body.kind, body.contact.strip(), body.phone.strip(), body.email.strip().lower(),
                             seats, int(now + (body.days or st.cn_trial_days) * DAY), body.request_id, body.note.strip(), int(now)))
            return org_out(c, get_org(c, cur.lastrowid))

    @app.put("/api/v1/admin/orgs/{oid}")
    async def change_org(oid: int, body: OrgChange, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        st = state.settings
        now = time.time()
        with db() as c:
            o = get_org(c, oid)
            if body.seats is not None:
                used = c.execute("select count(*) from member where org_id=?", (oid,)).fetchone()[0]
                if body.seats > st.cn_org_seats_max:
                    raise EngineError("too_many_seats", f"每家单位最多 {st.cn_org_seats_max} 个账号", 400)
                if body.seats < used:
                    raise EngineError("seats_below_used", f"这家单位已有 {used} 个账号", 400)
                c.execute("update org set seats=? where id=?", (body.seats, oid))
            reopening = (body.status == "active" or body.extend_days) and not live(o)
            if reopening and counts(c)["live"] >= st.cn_max_orgs:
                raise EngineError("org_limit", f"体验单位已满 {st.cn_max_orgs} 家", 409)
            if body.extend_days:
                c.execute("update org set expires=? where id=?", (int(max(o["expires"], now) + body.extend_days * DAY), oid))
            if body.status:
                c.execute("update org set status=? where id=?", (body.status, oid))
            if body.note is not None:
                c.execute("update org set note=? where id=?", (body.note.strip(), oid))
            out = org_out(c, get_org(c, oid))
        await sweep()
        return out

    @app.post("/api/v1/admin/orgs/{oid}/members")
    async def add_member(oid: int, body: MemberIn, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        email = body.email.strip().lower()
        with db() as c:
            o = get_org(c, oid)
            if not live(o):
                raise EngineError("org_expired", "这家单位的体验已到期或已停用", 409)
            used = c.execute("select count(*) from member where org_id=?", (oid,)).fetchone()[0]
            if used >= o["seats"]:
                raise EngineError("seats_full", f"这家单位的 {o['seats']} 个账号已用完", 409)
        name = body.name.strip()
        last, first = (name[0], name[1:]) if len(name) > 1 else (name, "")
        pw = gen_password()
        u = await m.accounts_svc("local_wenquest_account_create", email=email, password=pw, firstname=first or name,
                                 lastname=last if first else "", lang="zh_cn", teacher=True)
        with db() as c:
            c.execute("insert into member(userid,org_id,name,phone,email,stopped,created) values(?,?,?,?,?,0,?)",
                      (int(u["id"]), oid, name, body.phone.strip(), email, int(time.time())))
        return {"userid": int(u["id"]), "login": email, "password": pw}

    @app.put("/api/v1/admin/orgs/{oid}/members/{uid}")
    async def change_member(oid: int, uid: int, body: MemberChange, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        with db() as c:
            get_org(c, oid)
            if not c.execute("select 1 from member where userid=? and org_id=?", (uid, oid)).fetchone():
                raise EngineError("not_found", "no such account in this organisation", 404)
            c.execute("update member set stopped=? where userid=?", (1 if body.stopped else 0, uid))
        await sweep()
        return {"ok": True}

    @app.post("/api/v1/admin/orgs/{oid}/members/{uid}/password")
    async def new_password(oid: int, uid: int, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        with db() as c:
            r = c.execute("select email from member where userid=? and org_id=?", (uid, oid)).fetchone()
        if not r:
            raise EngineError("not_found", "no such account in this organisation", 404)
        pw = gen_password()
        await m.accounts_svc("local_wenquest_account_update", userid=uid, password=pw)
        return {"login": r["email"], "password": pw}
