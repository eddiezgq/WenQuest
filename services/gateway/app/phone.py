"""China server: sign in with a phone number and a text-message code, and with WeChat (round 108).

Accounts still live in Moodle. Here the gateway keeps which phone number and which WeChat account belong to which
Moodle user; after a right code (or a WeChat sign-in bound to an account) it asks the accounts service for a sign-in
token (local_wenquest_account_signin_token, never for administrators).

  GET  /api/v1/auth/methods          which ways of signing in this server offers (the login page asks)
  POST /api/v1/auth/sms/code         a code for login | register | reset | bind
  POST /api/v1/auth/sms/login        phone + code -> signed in
  POST /api/v1/auth/sms/register     phone + code + name -> a student account (D-8), signed in
  POST /api/v1/auth/sms/reset        phone + code + new password
  GET  /api/v1/auth/wechat/url       the WeChat QR page to send the browser to (signed in: binds instead)
  GET  /api/v1/auth/wechat/callback  WeChat sends the browser back here
  POST /api/v1/auth/wechat/bind      first scan: phone + code binds the WeChat account, then signed in
  GET  /api/v1/me/logins             the signed-in person's phone and whether WeChat is bound
  DELETE /api/v1/me/wechat           unbind WeChat

Accounts without an email get an internal sign-in name <phone>@m.<site domain>; nothing is mailed there.
Limits (D-6): one code a minute and sms_daily a day per phone, IP_HOURLY an hour per network address; a code lives
five minutes and dies after five wrong tries.
"""

import re
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import Depends, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from .accounts import IP_HOURLY, password_problem
from .moodle import EngineError
from .orgs import gen_password
from .session import Session
from .sms import Sms

SMS_TTL = 300
SMS_TRIES = 5
SMS_GAP = 60
WX_TTL = 600
PHONE_RE = re.compile(r"^1[3-9]\d{9}$")
PURPOSES = ("login", "register", "reset", "bind")


def norm_phone(raw: str) -> str:
    """A mainland mobile number, 11 digits; '' when it is not one."""
    p = re.sub(r"[\s\-()]", "", raw or "")
    if p.startswith("+86"):
        p = p[3:]
    elif p.startswith("0086"):
        p = p[4:]
    elif p.startswith("86") and len(p) == 13:
        p = p[2:]
    return p if PHONE_RE.match(p) else ""


def internal_domain(settings) -> str:
    """Accounts without an email sign in as <phone>@m.<site domain>; nothing is ever mailed there."""
    return "m." + (settings.site_domain.strip().lstrip(".").lower() or "wenquest.local")


def split_name(name: str) -> tuple[str, str]:
    """Chinese order: (family, given). Moodle wants both."""
    n = name.strip()
    return (n[0], n[1:]) if len(n) > 1 else (n, n)


class SmsCodeIn(BaseModel):
    phone: str = Field(min_length=5, max_length=20)
    purpose: str = Field(pattern="^(login|register|reset|bind)$")
    lang: str = ""


class SmsLoginIn(BaseModel):
    phone: str = Field(min_length=5, max_length=20)
    code: str = Field(min_length=4, max_length=8)
    lang: str = ""


class SmsRegisterIn(SmsLoginIn):
    name: str = Field(min_length=2, max_length=40)
    agree: bool = False


class SmsResetIn(SmsLoginIn):
    password: str = Field(min_length=1, max_length=100)


class WxBindIn(SmsLoginIn):
    ticket: str = Field(min_length=8, max_length=64)


def register(app, m) -> None:
    state = m.state
    s = lambda: state.settings

    def cn() -> bool:
        return s().region.strip().lower() == "cn"

    def need_cn() -> None:
        if not cn():
            raise EngineError("not_found", "only on the China server", 404)

    def get_sms() -> Sms:
        """Built from the settings on first use (tests change them); keeps its outbox afterwards."""
        cur = getattr(state, "sms", None)
        if cur is None:
            cur = state.sms = Sms(s().sms_access_key_id, s().sms_access_key_secret, s().sms_sign, s().sms_template,
                                  s().sms_endpoint, None)
        return cur

    def internal_email(phone: str) -> str:
        return f"{phone}@{internal_domain(s())}"

    m.internal_email = internal_email

    def db() -> sqlite3.Connection:
        d = Path(s().data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "logins.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.executescript("""
            create table if not exists phone(phone text primary key, userid integer unique, created real);
            create table if not exists wechat(wxid text primary key, userid integer unique, created real);
            create table if not exists code(phone text, purpose text, hash text, expires real, tries integer default 0,
                                            created real, ip text);
            create table if not exists wxstate(k text primary key, kind text, v text, created real);
        """)
        return c

    # ---------------------------------------------------------------- the phone map

    backfilled = {"done": False}

    def backfill() -> None:
        """Accounts opened for organisations before round 108 already have a phone in orgs.db: map them once."""
        if backfilled["done"]:
            return
        backfilled["done"] = True
        f = Path(s().data_dir) / "orgs.db"
        if not f.exists():
            return
        o = sqlite3.connect(str(f))
        try:
            rows = o.execute("select userid, phone from member order by created").fetchall()
        except sqlite3.Error:
            rows = []
        finally:
            o.close()
        with db() as c:
            for uid, ph in rows:
                p = norm_phone(ph or "")
                if p:
                    c.execute("insert or ignore into phone(phone, userid, created) values(?,?,?)", (p, uid, time.time()))

    def user_of(phone: str) -> int:
        backfill()
        with db() as c:
            r = c.execute("select userid from phone where phone=?", (phone,)).fetchone()
        return int(r["userid"]) if r else 0

    def phone_of(uid: int) -> str:
        backfill()
        with db() as c:
            r = c.execute("select phone from phone where userid=?", (uid,)).fetchone()
        return r["phone"] if r else ""

    def map_phone(uid: int, phone: str) -> None:
        """Put (or move) this account's phone. Raise when the number belongs to someone else."""
        other = user_of(phone)
        if other and other != uid:
            raise EngineError("phone_taken", "这个手机号已经绑定了别的账号", 409)
        with db() as c:
            c.execute("delete from phone where userid=?", (uid,))
            c.execute("insert or replace into phone(phone, userid, created) values(?,?,?)", (phone, uid, time.time()))

    m.phone_user = user_of
    m.phone_of = phone_of
    m.phone_map = map_phone

    async def login_name(name: str) -> str:
        """The password form also takes a phone number (round 108)."""
        p = norm_phone(name) if cn() else ""
        uid = user_of(p) if p else 0
        if not uid:
            return name
        u = await m.accounts_find(userid=uid)
        return u["username"] if u else name

    m.login_name = login_name

    # ---------------------------------------------------------------- codes

    def code_hash(phone: str, purpose: str, code: str) -> str:
        import hashlib
        import hmac
        return hmac.new(s().secret_key.encode(), f"sms|{phone}|{purpose}|{code}".encode(), hashlib.sha256).hexdigest()

    def check(phone: str, purpose: str, code: str) -> None:
        import hmac
        now = time.time()
        with db() as c:
            row = c.execute("select rowid, * from code where phone=? and purpose=? and expires>? and tries<? "
                            "order by created desc limit 1", (phone, purpose, now, SMS_TRIES)).fetchone()
            if not row:
                raise EngineError("code_expired", "验证码已失效，请重新获取", 400)
            if not hmac.compare_digest(row["hash"], code_hash(phone, purpose, code.strip())):
                c.execute("update code set tries=tries+1 where rowid=?", (row["rowid"],))
                raise EngineError("code_wrong", "验证码不对", 400)

    def spend(phone: str, purpose: str) -> None:
        with db() as c:
            c.execute("update code set expires=0 where phone=? and purpose=?", (phone, purpose))

    def client_ip(req: Request) -> str:
        fwd = req.headers.get("x-forwarded-for", "")
        return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "?"

    def phone_or_400(raw: str) -> str:
        p = norm_phone(raw)
        if not p:
            raise EngineError("invalid_phone", "请填 11 位手机号", 400)
        return p

    def signup_open() -> bool:
        return cn() and s().public_signup_cn and sms_ready()

    m.phone_signup_open = lambda: signup_open()
    m.login_methods = lambda: {"phone": cn() and sms_ready(), "wechat": wechat_ready()}

    def sms_ready() -> bool:
        return get_sms().configured or s().sms_log_only

    def wechat_ready() -> bool:
        return cn() and bool(s().wechat_web_appid and s().wechat_web_secret)

    @app.get("/api/v1/auth/methods")
    async def methods():
        return {"phone": cn() and sms_ready(), "wechat": wechat_ready(), "signup_phone": signup_open(),
                "signup_email": not cn()}

    @app.post("/api/v1/auth/sms/code")
    async def send_code(body: SmsCodeIn, req: Request):
        need_cn()
        if not sms_ready():
            raise EngineError("sms_unavailable", "短信登录还没有开通", 503)
        phone = phone_or_400(body.phone)
        uid = user_of(phone)
        if body.purpose == "register":
            if not signup_open():
                raise EngineError("signup_closed", "暂未开放注册", 403)
            if uid:
                raise EngineError("phone_taken", "这个手机号已经有账号了，请直接登录", 409)
        elif not uid:
            raise EngineError("phone_unknown", "这个手机号还没有账号" + ("，请先注册" if signup_open() else "，请联系单位管理员开通"), 404)
        now = time.time()
        ip = client_ip(req)
        with db() as c:
            last = c.execute("select max(created) from code where phone=?", (phone,)).fetchone()[0]
            if last and now - last < SMS_GAP:
                raise EngineError("code_too_soon", str(int(SMS_GAP - (now - last))), 429)
            if c.execute("select count(*) from code where phone=? and created>?", (phone, now - 86400)).fetchone()[0] \
                    >= s().sms_daily:
                raise EngineError("code_limit", "这个手机号今天的验证码已达上限，请明天再试", 429)
            if c.execute("select count(*) from code where ip=? and created>?", (ip, now - 3600)).fetchone()[0] >= IP_HOURLY:
                raise EngineError("code_limit", "这个网络请求验证码太频繁，请一小时后再试", 429)
            code = f"{secrets.randbelow(10**6):06d}"
            c.execute("insert into code(phone, purpose, hash, expires, created, ip) values(?,?,?,?,?,?)",
                      (phone, body.purpose, code_hash(phone, body.purpose, code), now + SMS_TTL, now, ip))
            c.execute("delete from code where created<?", (now - 2 * 86400,))
        sms = get_sms()
        sms.http = state.http
        if not await sms.send_code(phone, code):
            raise EngineError("sms_failed", "短信没有发出去，请稍后再试", 502)
        return {"sent": True}

    # ---------------------------------------------------------------- signing in

    async def sign_in_as(resp: Response, uid: int, lang: str) -> dict:
        m.org_gate(uid)
        try:
            r = await m.accounts_svc("local_wenquest_account_signin_token", userid=uid)
        except EngineError as exc:
            if exc.code == "account_suspended":
                raise EngineError("account_suspended", "这个账号已停用", 403) from exc
            if exc.code in ("invalid_input", "engine_error"):
                raise EngineError("phone_login_refused", "这个账号不能用手机号登录，请用密码登录", 403) from exc
            raise
        mtoken = r["token"]
        info = await state.moodle.site_info(mtoken)
        lg = m.lang_of(lang or info.get("lang"))
        token = state.codec.issue(Session(moodle_token=mtoken, user_id=int(info["userid"]), lang=lg))
        m.set_sso_cookie(resp, token)
        return {"token": token, "user": m._user(info, lg, await m.can_create(mtoken)).model_dump()}

    @app.post("/api/v1/auth/sms/login")
    async def sms_login(body: SmsLoginIn, resp: Response):
        need_cn()
        phone = phone_or_400(body.phone)
        check(phone, "login", body.code)
        uid = user_of(phone)
        if not uid:
            raise EngineError("phone_unknown", "这个手机号还没有账号", 404)
        out = await sign_in_as(resp, uid, body.lang)
        spend(phone, "login")
        return out

    @app.post("/api/v1/auth/sms/register")
    async def sms_register(body: SmsRegisterIn, resp: Response):
        need_cn()
        if not signup_open():
            raise EngineError("signup_closed", "暂未开放注册", 403)
        if not body.agree:
            raise EngineError("must_agree", "请先同意用户协议和隐私政策", 400)
        phone = phone_or_400(body.phone)
        check(phone, "register", body.code)
        if user_of(phone):
            raise EngineError("phone_taken", "这个手机号已经有账号了，请直接登录", 409)
        last, first = split_name(body.name)
        u = await m.accounts_svc("local_wenquest_account_create", email=internal_email(phone), password=gen_password(),
                                 firstname=first, lastname=last, lang="zh_cn", teacher=False)
        map_phone(int(u["id"]), phone)
        spend(phone, "register")
        return await sign_in_as(resp, int(u["id"]), body.lang or "zh")

    @app.post("/api/v1/auth/sms/reset")
    async def sms_reset(body: SmsResetIn, resp: Response):
        need_cn()
        phone = phone_or_400(body.phone)
        if bad := password_problem(body.password):
            raise EngineError(bad, "password too weak", 400)
        check(phone, "reset", body.code)
        uid = user_of(phone)
        if not uid:
            raise EngineError("phone_unknown", "这个手机号还没有账号", 404)
        await m.accounts_svc("local_wenquest_account_update", userid=uid, password=body.password)
        spend(phone, "reset")
        u = await m.accounts_find(userid=uid)
        mtoken = await state.moodle.login(u["username"], body.password)
        info = await state.moodle.site_info(mtoken)
        m.org_gate(uid)
        lg = m.lang_of(body.lang or info.get("lang"))
        token = state.codec.issue(Session(moodle_token=mtoken, user_id=uid, lang=lg))
        m.set_sso_cookie(resp, token)
        return {"token": token, "user": m._user(info, lg, await m.can_create(mtoken)).model_dump()}

    # ---------------------------------------------------------------- WeChat (open platform, website application)

    def callback_url() -> str:
        return s().app_url.rstrip("/") + "/api/v1/auth/wechat/callback"

    def remember(kind: str, v: str) -> str:
        k = secrets.token_urlsafe(18)
        now = time.time()
        with db() as c:
            c.execute("delete from wxstate where created<?", (now - WX_TTL,))
            c.execute("insert into wxstate(k, kind, v, created) values(?,?,?,?)", (k, kind, v, now))
        return k

    def recall(kind: str, k: str, keep: bool = False) -> str | None:
        with db() as c:
            r = c.execute("select v, created from wxstate where k=? and kind=?", (k, kind)).fetchone()
            if r and not keep:
                c.execute("delete from wxstate where k=?", (k,))
        return r["v"] if r and r["created"] > time.time() - WX_TTL else None

    def safe_back(back: str) -> str:
        return back if back.startswith("/") and not back.startswith("//") else ""

    @app.get("/api/v1/auth/wechat/url")
    async def wechat_url(req: Request, back: str = ""):
        """The QR page. With a signed-in person's token the scan binds WeChat to that account instead."""
        need_cn()
        if not wechat_ready():
            raise EngineError("wechat_unavailable", "微信登录还没有开通", 503)
        uid = 0
        auth = req.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            sess = state.codec.read(auth.split(" ", 1)[1].strip())
            uid = sess.user_id if sess else 0
        st_ = remember("state", f"{uid}|{safe_back(back)}")
        q = urlencode({"appid": s().wechat_web_appid, "redirect_uri": callback_url(), "response_type": "code",
                       "scope": "snsapi_login", "state": st_})
        return {"url": f"https://open.weixin.qq.com/connect/qrconnect?{q}#wechat_redirect"}

    async def wechat_identity(code: str) -> str:
        """unionid when the open platform gives one (same person across our apps), else openid."""
        try:
            r = await state.http.get("https://api.weixin.qq.com/sns/oauth2/access_token", timeout=15, params={
                "appid": s().wechat_web_appid, "secret": s().wechat_web_secret, "code": code,
                "grant_type": "authorization_code"})
            body = r.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise EngineError("wechat_failed", f"微信接口没有响应：{exc}", 502) from exc
        wx = body.get("unionid") or body.get("openid")
        if not wx:
            raise EngineError("wechat_failed", f"微信登录失败（{body.get('errcode')}）", 502)
        return str(wx)

    def to_app(path: str, **q: str) -> RedirectResponse:
        qs = urlencode({k: v for k, v in q.items() if v})
        return RedirectResponse(s().app_url.rstrip("/") + path + (f"?{qs}" if qs else ""), status_code=302)

    @app.get("/api/v1/auth/wechat/callback")
    async def wechat_callback(code: str = "", state: str = ""):
        need_cn()
        v = recall("state", state) if state else None
        if v is None or not code:
            return to_app("/pages/login/login", wx_error="expired")
        uid_s, back = v.split("|", 1)
        try:
            wx = await wechat_identity(code)
        except EngineError:
            return to_app("/pages/login/login", wx_error="failed")
        with db() as c:
            row = c.execute("select userid from wechat where wxid=?", (wx,)).fetchone()
            if int(uid_s):                                   # binding from the signed-in person's page
                if row and int(row["userid"]) != int(uid_s):
                    return to_app("/pages/courses/courses", wx_error="taken")
                c.execute("delete from wechat where userid=?", (int(uid_s),))
                c.execute("insert or replace into wechat(wxid, userid, created) values(?,?,?)", (wx, int(uid_s), time.time()))
                return to_app("/pages/courses/courses", wx="bound")
        if row:
            resp = to_app("/pages/login/login", back=back)
            try:
                await sign_in_as(resp, int(row["userid"]), "zh")
            except EngineError as exc:
                return to_app("/pages/login/login", wx_error=exc.code)
            return resp
        return to_app("/pages/login/login", wx=remember("ticket", wx), back=back)

    @app.post("/api/v1/auth/wechat/bind")
    async def wechat_bind(body: WxBindIn, resp: Response):
        need_cn()
        phone = phone_or_400(body.phone)
        wx = recall("ticket", body.ticket, keep=True)
        if not wx:
            raise EngineError("wx_ticket_expired", "微信扫码已过期，请重新扫码", 400)
        check(phone, "bind", body.code)
        uid = user_of(phone)
        if not uid:
            raise EngineError("phone_unknown", "这个手机号还没有账号", 404)
        out = await sign_in_as(resp, uid, body.lang)
        with db() as c:
            c.execute("delete from wechat where userid=?", (uid,))
            c.execute("insert or replace into wechat(wxid, userid, created) values(?,?,?)", (wx, uid, time.time()))
        recall("ticket", body.ticket)
        spend(phone, "bind")
        return out

    @app.get("/api/v1/me/logins")
    async def my_logins(sess: Annotated[Session, Depends(m.current)]):
        with db() as c:
            wx = c.execute("select 1 from wechat where userid=?", (sess.user_id,)).fetchone()
        return {"phone": phone_of(sess.user_id), "wechat": bool(wx), "wechat_ready": wechat_ready()}

    @app.delete("/api/v1/me/wechat")
    async def unbind_wechat(sess: Annotated[Session, Depends(m.current)]):
        with db() as c:
            c.execute("delete from wechat where userid=?", (sess.user_id,))
        return {"ok": True}

