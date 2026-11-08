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
    email: str = Field(default="", max_length=254)   # 第 108 轮：选填；不填的用手机号登录


class MemberChange(BaseModel):
    stopped: bool | None = None
    owner: bool | None = None        # 第 96 轮：设为 / 取消单位负责人（可在“我的单位”里加人）


class AutoSwitch(BaseModel):
    on: bool


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
        c.execute("create table if not exists setting(k text primary key, v text)")
        # 第 96 轮：自动开通的单位做标记；单位负责人（owner）可以在“我的单位”里自己加人
        if "auto" not in {r[1] for r in c.execute("pragma table_info(org)")}:
            c.execute("alter table org add column auto integer default 0")
        if "owner" not in {r[1] for r in c.execute("pragma table_info(member)")}:
            c.execute("alter table member add column owner integer default 0")
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
        return {**cnt, "auto": auto_on(), "auto_daily": state.settings.cn_auto_daily,
                "default_seats": state.settings.cn_org_seats, "max_seats": state.settings.cn_org_seats_max,
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

    async def create_member(oid: int, name: str, phone_raw: str, email_raw: str = "", owner: bool = False) -> dict:
        """One account in an organisation (administrator, the organisation's owner, or the automatic opening)."""
        from .phone import norm_phone
        phone = norm_phone(phone_raw)
        if not phone:
            raise EngineError("invalid_phone", "请填 11 位手机号（登录要用）", 400)
        if m.phone_user(phone):
            raise EngineError("phone_taken", "这个手机号已经有账号了", 409)
        email = email_raw.strip().lower() or m.internal_email(phone)
        with db() as c:
            o = get_org(c, oid)
            if not live(o):
                raise EngineError("org_expired", "这家单位的体验已到期或已停用", 409)
            used = c.execute("select count(*) from member where org_id=?", (oid,)).fetchone()[0]
            if used >= o["seats"]:
                raise EngineError("seats_full", f"这家单位的 {o['seats']} 个账号已用完", 409)
        name = name.strip()
        last, first = (name[0], name[1:]) if len(name) > 1 else (name, name)
        pw = gen_password()
        u = await m.accounts_svc("local_wenquest_account_create", email=email, password=pw, firstname=first,
                                 lastname=last, lang="zh_cn", teacher=True)
        m.phone_map(int(u["id"]), phone)
        shown = "" if email == m.internal_email(phone) else email
        with db() as c:
            c.execute("insert into member(userid,org_id,name,phone,email,stopped,created,owner) values(?,?,?,?,?,0,?,?)",
                      (int(u["id"]), oid, name, phone, shown, int(time.time()), 1 if owner else 0))
        return {"userid": int(u["id"]), "login": shown or phone, "phone": phone, "password": pw}

    async def set_stopped(oid: int, uid: int, stopped: bool) -> None:
        with db() as c:
            c.execute("update member set stopped=? where userid=? and org_id=?", (1 if stopped else 0, uid, oid))
        await sweep()

    async def fresh_password(oid: int, uid: int) -> dict:
        with db() as c:
            r = c.execute("select email, phone from member where userid=? and org_id=?", (uid, oid)).fetchone()
        if not r:
            raise EngineError("not_found", "no such account in this organisation", 404)
        pw = gen_password()
        await m.accounts_svc("local_wenquest_account_update", userid=uid, password=pw)
        return {"login": r["email"] or r["phone"], "password": pw}

    @app.post("/api/v1/admin/orgs/{oid}/members")
    async def add_member(oid: int, body: MemberIn, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        return await create_member(oid, body.name, body.phone, body.email)

    @app.put("/api/v1/admin/orgs/{oid}/members/{uid}")
    async def change_member(oid: int, uid: int, body: MemberChange, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        with db() as c:
            get_org(c, oid)
            if not c.execute("select 1 from member where userid=? and org_id=?", (uid, oid)).fetchone():
                raise EngineError("not_found", "no such account in this organisation", 404)
            if body.owner is not None:
                c.execute("update member set owner=? where userid=?", (1 if body.owner else 0, uid))
        if body.stopped is not None:
            await set_stopped(oid, uid, body.stopped)
        return {"ok": True}

    @app.post("/api/v1/admin/orgs/{oid}/members/{uid}/password")
    async def new_password(oid: int, uid: int, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        return await fresh_password(oid, uid)

    # ------------------------------------------------------------------ 第 96 轮：自动开通、单位负责人自己管账号

    def auto_on() -> bool:
        with db() as c:
            r = c.execute("select v from setting where k='auto'").fetchone()
        return (r["v"] == "1") if r else bool(state.settings.cn_auto)

    @app.put("/api/v1/admin/orgs-auto")
    async def switch_auto(body: AutoSwitch, sess: Annotated[Session, Depends(m.current)]):
        need_cn()
        await m.accounts_require_admin(sess)
        with db() as c:
            c.execute("insert or replace into setting(k, v) values('auto', ?)", ("1" if body.on else "0",))
        return {"auto": auto_on()}

    m.orgs_auto_on = lambda: cn() and auto_on()
    auto_hits: dict[str, list[float]] = {}

    async def auto_open(org: str, name: str, phone: str, email: str, seats: int, request_id: int, ip: str,
                        erp: bool = False) -> str:
        """Open a trial at once for a verified request (round 96). Returns '' when opened (the account is mailed),
        else why it goes to the administrator instead (the request is kept either way)."""
        from .phone import norm_phone
        st = state.settings
        if not (cn() and auto_on()):
            return "auto_off"
        mobile = norm_phone(phone)
        if not mobile:
            return "not_mobile"
        if m.phone_user(mobile) or await m.accounts_find(email=email):
            return "known_person"
        now = time.time()
        hits = [t for t in auto_hits.get(ip, []) if now - t < 3600]
        with db() as c:
            if c.execute("select 1 from org where name=? or (email<>'' and email=?) or (phone<>'' and phone in (?, ?))",
                         (org.strip(), email, phone, mobile)).fetchone():
                return "known_org"
            if len(hits) >= 2:
                return "ip_hourly"
            if c.execute("select count(*) from org where auto=1 and created>?", (now - DAY,)).fetchone()[0] >= st.cn_auto_daily:
                return "daily"
            if counts(c)["live"] >= st.cn_max_orgs:
                return "org_limit"
            cur = c.execute("insert into org(name,kind,contact,phone,email,seats,expires,status,request_id,note,created,auto) "
                            "values(?,?,?,?,?,?,?,'active',?,?,?,1)",
                            (org.strip(), "school" if any(k in org for k in ("学校", "学院", "大学", "职业")) else "company",
                             name.strip(), mobile, email, max(1, min(seats or st.cn_org_seats, 5)),
                             int(now + st.cn_trial_days * DAY), request_id, "官网申请，自动开通", int(now)))
            oid = cur.lastrowid
        auto_hits[ip] = [*hits, now]
        try:
            a = await create_member(oid, name, mobile, email, owner=True)
        except EngineError:
            with db() as c:                          # could not make the account: leave it to the administrator
                c.execute("delete from org where id=?", (oid,))
            return "account_failed"
        url = st.app_url.rstrip("/") + "/pages/login/login"
        text = (f"{name}，你好：\n\n{org} 的在线体验已开通，体验期 {st.cn_trial_days} 天。\n\n"
                f"登录网址：{url}\n账号：{a['login']}（也可以用手机号 {mobile} 登录）\n初始密码：{a['password']}\n\n"
                f"登录后在左上角头像菜单“我的单位”里可以给同事开账号（共 {max(1, min(seats or st.cn_org_seats, 5))} 个）。\n"
                "请登录后尽快修改密码。有问题直接回复这封邮件或打电话给我们。\n\n问渠科技")
        if erp:                                       # 勾了“问渠质量 ERP”：共用演示企业的体验账号另发一封（ops ADR-0027）
            m.pilots_open_trial(name, email, org)
            text = text.replace("\n\n问渠科技", "\n\n问渠质量 ERP 的体验账号稍后另发一封邮件。\n\n问渠科技")
        await state.mailer.send(email, "问渠在线体验已开通", text)
        return ""

    m.orgs_auto_open = auto_open

    def my_org(uid: int):
        """The organisation this person is the owner of, or 404."""
        if not cn():
            raise EngineError("not_found", "only on the China server", 404)
        with db() as c:
            r = c.execute("select org_id from member where userid=? and owner=1 and stopped=0", (uid,)).fetchone()
            if not r:
                raise EngineError("not_found", "not an organisation's owner", 404)
            return org_out(c, get_org(c, r["org_id"]))

    @app.get("/api/v1/my/org")
    async def my_org_view(sess: Annotated[Session, Depends(m.current)]):
        return my_org(sess.user_id)

    @app.post("/api/v1/my/org/members")
    async def my_org_add(body: MemberIn, sess: Annotated[Session, Depends(m.current)]):
        o = my_org(sess.user_id)
        return await create_member(o["id"], body.name, body.phone, body.email)

    @app.put("/api/v1/my/org/members/{uid}")
    async def my_org_change(uid: int, body: MemberChange, sess: Annotated[Session, Depends(m.current)]):
        o = my_org(sess.user_id)
        if uid == sess.user_id:
            raise EngineError("forbidden", "不能停用自己的账号", 403)
        if not any(x["userid"] == uid for x in o["members"]):
            raise EngineError("not_found", "no such account in this organisation", 404)
        if body.stopped is not None:
            await set_stopped(o["id"], uid, body.stopped)
        return {"ok": True}

    @app.post("/api/v1/my/org/members/{uid}/password")
    async def my_org_password(uid: int, sess: Annotated[Session, Depends(m.current)]):
        o = my_org(sess.user_id)
        if not any(x["userid"] == uid for x in o["members"]):
            raise EngineError("not_found", "no such account in this organisation", 404)
        return await fresh_password(o["id"], uid)
