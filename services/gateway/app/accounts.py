"""Sign-up, email codes, sign-in across the site, and teacher approval (round 3, step C).

Accounts live in Moodle. The gateway creates and changes them through the plugin's
local_wenquest_account_* functions, using the wqservice account whose token is derived from
WQ_SECRET_KEY (see moodle/setup_wenquest.php). Codes, teacher applications and the AI's
review of them are kept here in a small SQLite file.

Teacher applications: a school email (.edu, .edu.cn, .ac.cn, .ac.uk ...) is approved at once;
anything else is reviewed by the AI (institution, title, email domain, evidence), which asks the
applicant for more evidence by email when needed. The administrator only clicks approve or reject.
"""

import hashlib
import hmac
import io
import json
import logging
import re
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import quote, urlsplit

from fastapi import Depends, File, Request, Response, UploadFile
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

log = logging.getLogger("wenquest.accounts")

COOKIE = "wq_sso"
CODE_TTL = 600            # a code lives 10 minutes
CODE_TRIES = 5            # wrong guesses before a code is void
RESEND_GAP = 60           # one code per email per minute
EMAIL_HOURLY = 5          # codes per email per hour
IP_HOURLY = 20            # codes per network address per hour
DIGEST_GAP = 3600         # at most one summary email to the administrator per hour
MAX_EVIDENCE = 5
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
EVIDENCE_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp",
                  ".pdf": "application/pdf"}
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,24}$")
SCHOOL_RE = re.compile(r"(^|\.)(edu|ac)(\.[a-z]{2})?$")


def is_school_email(email: str) -> bool:
    return bool(SCHOOL_RE.search(email.rsplit("@", 1)[-1].lower()))


def password_problem(pw: str) -> str:
    if len(pw) < 8 or len(pw) > 100:
        return "password_length"
    if not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        return "password_weak"
    return ""


# --- storage ------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS codes (email TEXT, purpose TEXT, hash TEXT, expires REAL, tries INTEGER DEFAULT 0,
                                  created REAL, ip TEXT);
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER UNIQUE, email TEXT, name TEXT, lang TEXT,
    institution TEXT, department TEXT, title TEXT, note TEXT, school INTEGER DEFAULT 0,
    status TEXT, ai TEXT DEFAULT '', evidence TEXT DEFAULT '[]', created REAL, updated REAL,
    submitted REAL DEFAULT 0, reviewed REAL DEFAULT 0, more_requested REAL DEFAULT 0,
    decided REAL DEFAULT 0, decided_by TEXT DEFAULT '', reason TEXT DEFAULT '', digest INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS catalog (courseid INTEGER PRIMARY KEY, mode TEXT, price REAL DEFAULT 0,
                                    currency TEXT DEFAULT 'CNY', blurb TEXT DEFAULT '', updated REAL, updated_by INTEGER);
CREATE TABLE IF NOT EXISTS enrol_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, courseid INTEGER, userid INTEGER,
    name TEXT, email TEXT, note TEXT, status TEXT, created REAL, decided REAL DEFAULT 0, digest INTEGER DEFAULT 0,
    UNIQUE(courseid, userid));
"""


class Store:
    def __init__(self, folder: str):
        self.dir = Path(folder)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.dir / "accounts.db"), check_same_thread=False, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def q(self, sql: str, *args: Any) -> list[dict]:
        return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def one(self, sql: str, *args: Any) -> dict | None:
        r = self.db.execute(sql, args).fetchone()
        return dict(r) if r else None

    def run(self, sql: str, *args: Any) -> int:
        cur = self.db.execute(sql, args)
        return cur.lastrowid or cur.rowcount

    def meta(self, k: str, v: str | None = None) -> str:
        if v is not None:
            self.run("INSERT INTO meta (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v = excluded.v", k, v)
            return v
        r = self.one("SELECT v FROM meta WHERE k = ?", k)
        return r["v"] if r else ""

    def evidence_dir(self, app_id: int) -> Path:
        p = self.dir / "evidence" / str(app_id)
        p.mkdir(parents=True, exist_ok=True)
        return p


def app_row(r: dict) -> dict:
    r = dict(r)
    r["ai"] = json.loads(r["ai"]) if r.get("ai") else None
    r["evidence"] = json.loads(r.get("evidence") or "[]")
    return r


# --- email texts --------------------------------------------------------

def texts(kind: str, lang: str, **kw: Any) -> tuple[str, str]:
    zh = lang != "en"
    name = kw.get("name") or ""
    if kind == "code":
        what = {"register": ("注册", "sign-up"), "reset": ("重设密码", "password reset")}[kw["purpose"]]
        if zh:
            return (f"问渠验证码 {kw['code']}",
                    f"你好！\n\n你正在问渠机器人学院{what[0]}，验证码是：\n\n{kw['code']}\n\n"
                    "10 分钟内有效。如果不是你本人操作，请忽略这封邮件。")
        return (f"WenQuest code {kw['code']}",
                f"Hello,\n\nYour WenQuest {what[1]} code is:\n\n{kw['code']}\n\n"
                "It is valid for 10 minutes. If you did not ask for it, you can ignore this email.")
    if kind == "welcome":
        if zh:
            return ("欢迎加入问渠机器人学院",
                    f"{name}，你好！\n\n你的账号已经开通，用这个邮箱和你设的密码登录：\n{kw['url']}\n\n"
                    "官网、学习平台、虚拟实验室都用这一个账号。祝学习愉快！")
        return ("Welcome to WenQuest",
                f"Hello {name},\n\nYour account is ready. Sign in with this email and your password:\n{kw['url']}\n\n"
                "The same account works on the website, the learning platform and the virtual labs.")
    if kind == "teacher_auto":
        if zh:
            return ("问渠教师账号已开通",
                    f"{name}老师，你好！\n\n你用学校邮箱注册，教师身份已自动开通，现在就可以建课：\n{kw['url']}\n\n"
                    "在“AI 建课”里说出课程要求或上传资料，AI 会帮你把整门课建出来。")
        return ("Your WenQuest teacher account is ready",
                f"Hello {name},\n\nYou signed up with a school email, so your teacher account is active. "
                f"You can build a course now:\n{kw['url']}")
    if kind == "teacher_pending":
        if zh:
            return ("问渠教师申请已收到",
                    f"{name}老师，你好！\n\n我们收到了你的教师申请，审核通常在 1 个工作日内完成，结果会发到这个邮箱。"
                    f"审核期间你可以先用学生身份登录浏览课程：\n{kw['url']}")
        return ("We received your teacher application",
                f"Hello {name},\n\nWe received your application to teach on WenQuest. It is usually reviewed within "
                f"one working day, and we will email you the result. Meanwhile you can sign in as a learner:\n{kw['url']}")
    if kind == "more":
        if zh:
            return ("问渠教师申请：请补充材料",
                    f"{name}老师，你好！\n\n审核你的教师申请时，还需要补充一点材料：\n\n{kw['message']}\n\n"
                    f"请登录后在这里上传（工作证、聘书、学校官网上的教师页面截图都可以）：\n{kw['url']}")
        return ("WenQuest teacher application: more information needed",
                f"Hello {name},\n\nTo finish reviewing your teacher application we need a little more:\n\n{kw['message']}\n\n"
                f"Please sign in and upload it here (staff card, appointment letter or a screenshot of your "
                f"page on your school's website):\n{kw['url']}")
    if kind == "approved":
        if zh:
            return ("问渠教师申请已通过",
                    f"{name}老师，你好！\n\n你的教师申请已经通过，现在就可以建课：\n{kw['url']}\n\n"
                    "在“AI 建课”里说出课程要求或上传资料，AI 会帮你把整门课建出来。")
        return ("Your WenQuest teacher application is approved",
                f"Hello {name},\n\nYour teacher application is approved. You can build a course now:\n{kw['url']}")
    if kind == "rejected":
        if zh:
            return ("问渠教师申请结果",
                    f"{name}，你好！\n\n很抱歉，这次的教师申请没有通过。\n\n{kw['reason']}\n\n"
                    f"你的账号仍然可以学习课程。补齐材料后可以在这里重新申请：\n{kw['url']}")
        return ("Your WenQuest teacher application",
                f"Hello {name},\n\nWe are sorry, your teacher application was not approved this time.\n\n{kw['reason']}\n\n"
                f"You can still learn with your account, and apply again here:\n{kw['url']}")
    if kind == "enrolled":
        if zh:
            return (f"已为你开通课程：{kw['course']}",
                    f"{name}，你好！\n\n管理员已为你开通课程《{kw['course']}》，现在就可以开始学习：\n{kw['url']}")
        return (f"You are enrolled: {kw['course']}",
                f"Hello {name},\n\nYou now have access to {kw['course']}. Start here:\n{kw['url']}")
    raise ValueError(kind)


# --- the AI's review of a teacher application ----------------------------

REVIEWER = """你是“问渠机器人学院”（在线工程教育平台）的教师资格审核助手。有人申请成为平台教师（教师可以建课、发布课程）。
请根据申请信息做预审，给管理员一个建议，最终由管理员一键批准或拒绝。

判断要点：
1. 单位是否真实存在、是不是学校/科研机构/培训机构/企业（凭你的知识判断；不确定就如实说“无法确认”）。
2. 邮箱域名是否和所填单位一致（例如 tsinghua.edu.cn 对清华大学）；公共邮箱（gmail、qq、163 等）本身不是扣分项，但需要证明材料支撑。
3. 院系、职称是否合理（教授、讲师、助教、中小学教师、培训讲师、工程师等都可以）。
4. 证明材料（工作证、聘书、学校网站教师页面截图等）上的姓名、单位是否与申请一致；看不到图片时要说明“需要人工看一眼图片”。
5. 明显的乱填、广告、测试数据，建议拒绝。

建议只能是三种之一：
- approve：信息一致、可信。
- more：可能是真的，但证据不足（例如公共邮箱且没有任何证明材料），需要申请人补充；message_to_applicant 写清楚要补什么（礼貌、具体、2 句以内）。
- reject：明显不可信或乱填；message_to_applicant 写一句礼貌的拒绝理由。
approve 时 message_to_applicant 留空。
reason 用中文一句话（40 字以内）写给管理员。message_to_applicant 用申请人的语言（lang=en 用英文，否则中文）。"""

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendation": {"type": "string", "enum": ["approve", "more", "reject"]},
        "reason": {"type": "string"},
        "checks": {"type": "array", "items": {"type": "object", "properties": {
            "item": {"type": "string"}, "result": {"type": "string", "enum": ["ok", "doubt", "bad", "unknown"]},
            "note": {"type": "string"}}, "required": ["item", "result", "note"]}},
        "message_to_applicant": {"type": "string"},
    },
    "required": ["recommendation", "reason", "checks", "message_to_applicant"],
}


def fake_review(a: dict) -> dict:
    """Offline stand-in for the model: evidence or a school email is enough; otherwise ask for more."""
    if a["school"] or a["evidence"]:
        return {"recommendation": "approve", "reason": "单位与材料一致（离线模拟审核）",
                "checks": [{"item": "证明材料", "result": "ok", "note": f"{len(a['evidence'])} 份"}],
                "message_to_applicant": ""}
    return {"recommendation": "more", "reason": "公共邮箱且没有证明材料（离线模拟审核）",
            "checks": [{"item": "证明材料", "result": "bad", "note": "未上传"}],
            "message_to_applicant": "请上传能证明你教师身份的材料，例如工作证或聘书照片。" if a["lang"] != "en"
            else "Please upload proof that you teach, such as a staff card or appointment letter."}


def evidence_inputs(store: Store, a: dict, sees_images: bool) -> tuple[str, list[tuple[str, bytes]]]:
    """What the model gets from the uploaded evidence: PDF text, and images when it can see them."""
    lines, images = [], []
    folder = store.evidence_dir(a["id"])
    for f in a["evidence"]:
        path = folder / f["file"]
        if not path.exists():
            continue
        if f["mime"] == "application/pdf":
            try:
                from pypdf import PdfReader
                text = " ".join((p.extract_text() or "") for p in PdfReader(str(path)).pages[:3]).strip()
            except Exception:  # noqa: BLE001 - a broken PDF is just "unreadable"
                text = ""
            lines.append(f"- {f['name']}（PDF）：{text[:2500] or '无法读取文字，需人工查看'}")
        elif sees_images and len(images) < 4:
            images.append(("image/jpeg", shrink(path.read_bytes())))
            lines.append(f"- {f['name']}（图片，见附图 {len(images)}）")
        else:
            lines.append(f"- {f['name']}（图片，当前模型看不了图，需要人工看一眼）")
    return ("\n".join(lines) or "（没有上传证明材料）"), images


def shrink(data: bytes) -> bytes:
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    im = im.convert("RGB")
    im.thumbnail((1600, 1600))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=85)
    return out.getvalue()


# --- request bodies -----------------------------------------------------

class CodeIn(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    purpose: str = Field(default="register", pattern="^(register|reset)$")
    lang: str = "zh"


class TeacherInfo(BaseModel):
    institution: str = Field(default="", max_length=200)
    department: str = Field(default="", max_length=200)
    title: str = Field(default="", max_length=100)
    note: str = Field(default="", max_length=1000)


class RegisterIn(TeacherInfo):
    role: str = Field(pattern="^(student|teacher)$")
    email: str = Field(min_length=3, max_length=254)
    code: str = Field(min_length=4, max_length=10)
    password: str = Field(min_length=1, max_length=200)
    lastname: str = Field(min_length=1, max_length=100)
    firstname: str = Field(min_length=1, max_length=100)
    lang: str = "zh"
    agree: bool = False


class ResetIn(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    code: str = Field(min_length=4, max_length=10)
    password: str = Field(min_length=1, max_length=200)


class DecideIn(BaseModel):
    approve: bool
    reason: str = Field(default="", max_length=2000)


class UserChangeIn(BaseModel):
    suspended: bool | None = None
    teacher: bool | None = None


# --- registration -------------------------------------------------------

def register(app, m) -> None:  # noqa: C901 - one place for all account routes
    state = m.state

    def st() -> Store:
        return state.accounts

    def svc_token() -> str:
        return hashlib.sha256(("wq-accounts:" + state.settings.secret_key).encode()).hexdigest()[:32]

    async def svc(fn: str, **params: Any) -> Any:
        try:
            return await state.moodle.call(svc_token(), fn, **params)
        except EngineError as exc:
            if exc.code == "engine_error" and "password" in (exc.message or "").lower():
                raise EngineError("password_weak", exc.message, 400) from exc
            if exc.code in ("session_expired", "engine_misconfigured", "forbidden"):
                log.error("accounts service not available (%s): %s", fn, exc.message)
                raise EngineError("accounts_unavailable", "the accounts service is not set up", 503) from exc
            raise

    async def find(email: str = "", userid: int = 0) -> dict | None:
        r = await svc("local_wenquest_account_find", email=email, userid=userid)
        return r["users"][0] if r.get("found") else None

    def link(path: str) -> str:
        return state.settings.app_url.rstrip("/") + path

    def norm(email: str) -> str:
        e = email.strip().lower()
        if not EMAIL_RE.match(e):
            raise EngineError("invalid_email", "not an email address", 400)
        return e

    def client_ip(req: Request) -> str:
        fwd = req.headers.get("x-forwarded-for", "")
        return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "?"

    def code_hash(email: str, purpose: str, code: str) -> str:
        return hmac.new(state.settings.secret_key.encode(), f"{email}|{purpose}|{code}".encode(), hashlib.sha256).hexdigest()

    def check_code(email: str, purpose: str, code: str) -> None:
        """Raise unless the code is right. It stays usable until use_code(), so a failed step can be retried."""
        now = time.time()
        row = st().one("SELECT rowid, * FROM codes WHERE email = ? AND purpose = ? AND expires > ? AND tries < ? "
                       "ORDER BY created DESC LIMIT 1", email, purpose, now, CODE_TRIES)
        if not row:
            raise EngineError("code_expired", "no valid code; ask for a new one", 400)
        if not hmac.compare_digest(row["hash"], code_hash(email, purpose, code.strip())):
            st().run("UPDATE codes SET tries = tries + 1 WHERE rowid = ?", row["rowid"])
            raise EngineError("code_wrong", "wrong code", 400)

    def use_code(email: str, purpose: str) -> None:
        st().run("UPDATE codes SET expires = 0 WHERE email = ? AND purpose = ?", email, purpose)

    def cookie_domain() -> str | None:
        dom = state.settings.site_domain.strip().lstrip(".").lower()
        host = (urlsplit(state.settings.app_url).hostname or "").lower()
        return dom if dom and (host == dom or host.endswith("." + dom)) else None

    def set_cookie(resp: Response, token: str) -> None:
        resp.set_cookie(COOKIE, token, max_age=state.settings.session_days * 86400, httponly=True,
                        secure=state.settings.app_url.startswith("https://"), samesite="lax",
                        domain=cookie_domain(), path="/")

    m.set_sso_cookie = set_cookie

    async def sign_in(resp: Response, login: str, password: str, lang: str) -> dict:
        mtoken = await state.moodle.login(login, password)
        info = await state.moodle.site_info(mtoken)
        lg = m.lang_of(lang or info.get("lang"))
        token = state.codec.issue(Session(moodle_token=mtoken, user_id=int(info["userid"]), lang=lg))
        set_cookie(resp, token)
        return {"token": token, "user": m._user(info, lg, await m.can_create(mtoken)).model_dump()}

    async def is_admin(sess: Session) -> bool:
        try:
            p = await state.moodle.call(sess.moodle_token, "local_wenquest_get_permissions")
        except EngineError:
            return False
        return bool(p.get("issiteadmin"))

    async def require_admin(sess: Session) -> None:
        if not await is_admin(sess):
            raise EngineError("forbidden", "administrators only", 403)

    async def mail(to: str, kind: str, lang: str, **kw: Any) -> bool:
        subject, text = texts(kind, lang, **kw)
        return await state.mailer.send(to, subject, text)

    def admin_address() -> str:
        return state.settings.admin_email or state.settings.admin_email_fallback

    # --- codes, sign-up, sign-in ---------------------------------------

    @app.post("/api/v1/auth/code")
    async def send_code(body: CodeIn, req: Request):
        email = norm(body.email)
        now = time.time()
        last = st().one("SELECT MAX(created) AS t FROM codes WHERE email = ?", email)
        if last and last["t"] and now - last["t"] < RESEND_GAP:
            raise EngineError("code_too_soon", str(int(RESEND_GAP - (now - last["t"]))), 429)
        if st().one("SELECT COUNT(*) AS n FROM codes WHERE email = ? AND created > ?", email, now - 3600)["n"] >= EMAIL_HOURLY:
            raise EngineError("code_limit", "too many codes for this email; try again in an hour", 429)
        ip = client_ip(req)
        if st().one("SELECT COUNT(*) AS n FROM codes WHERE ip = ? AND created > ?", ip, now - 3600)["n"] >= IP_HOURLY:
            raise EngineError("code_limit", "too many codes from this network; try again in an hour", 429)
        existing = await find(email)
        if body.purpose == "register" and existing:
            raise EngineError("email_taken", "this email already has an account", 409)
        code = f"{secrets.randbelow(10**6):06d}"
        st().run("INSERT INTO codes (email, purpose, hash, expires, created, ip) VALUES (?, ?, ?, ?, ?, ?)",
                 email, body.purpose, code_hash(email, body.purpose, code), now + CODE_TTL, now, ip)
        st().run("DELETE FROM codes WHERE created < ?", now - 86400)
        if body.purpose == "reset" and not existing:
            return {"sent": True}  # do not reveal whether an email has an account
        if not await mail(email, "code", m.lang_of(body.lang), code=code, purpose=body.purpose):
            raise EngineError("mail_failed", "the email could not be sent", 502)
        return {"sent": True}

    @app.post("/api/v1/auth/register")
    async def sign_up(body: RegisterIn, resp: Response):
        email = norm(body.email)
        if not body.agree:
            raise EngineError("must_agree", "accept the terms first", 400)
        if bad := password_problem(body.password):
            raise EngineError(bad, "password too weak", 400)
        teacher = body.role == "teacher"
        if teacher and not body.institution.strip():
            raise EngineError("institution_required", "teachers give their school or organisation", 400)
        check_code(email, "register", body.code)
        lang = m.lang_of(body.lang)
        school = teacher and is_school_email(email)
        u = await svc("local_wenquest_account_create", email=email, password=body.password,
                      firstname=body.firstname.strip(), lastname=body.lastname.strip(),
                      lang="en" if lang == "en" else "zh_cn", teacher=school)
        use_code(email, "register")
        # Chinese order (family name first) for Chinese, "First Last" otherwise.
        last, first = body.lastname.strip(), body.firstname.strip()
        name = f"{last}{first}" if lang == "zh" else f"{first} {last}"
        now = time.time()
        if teacher:
            st().run("INSERT OR REPLACE INTO applications (userid, email, name, lang, institution, department, title, note, "
                     "school, status, created, updated, submitted, decided, decided_by) "
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     u["id"], email, name, lang, body.institution.strip(), body.department.strip(), body.title.strip(),
                     body.note.strip(), 1 if school else 0, "approved" if school else "pending", now, now,
                     0, now if school else 0, "auto" if school else "")
            await mail(email, "teacher_auto" if school else "teacher_pending", lang, name=name, url=link("/pages/courses/courses"))
        else:
            await mail(email, "welcome", lang, name=name, url=link("/pages/login/login"))
        out = await sign_in(resp, email, body.password, lang)
        out["teacher_status"] = ("approved" if school else "pending") if teacher else ""
        return out

    @app.post("/api/v1/auth/reset")
    async def reset(body: ResetIn, resp: Response):
        email = norm(body.email)
        if bad := password_problem(body.password):
            raise EngineError(bad, "password too weak", 400)
        check_code(email, "reset", body.code)
        u = await find(email)
        if not u:
            raise EngineError("code_wrong", "wrong code", 400)
        if u["suspended"]:
            raise EngineError("account_suspended", "this account is suspended", 403)
        await svc("local_wenquest_account_update", userid=u["id"], password=body.password)
        use_code(email, "reset")
        return await sign_in(resp, u["username"], body.password, "en" if u["lang"] == "en" else "zh")

    @app.get("/api/v1/auth/sso")
    async def sso(req: Request, resp: Response, lang: str | None = None):
        """The learning platform signs in with the site-wide cookie (set when signing in anywhere on the site)."""
        tok = req.cookies.get(COOKIE, "")
        sess = state.codec.read(tok) if tok else None
        if not sess:
            raise EngineError("not_logged_in", "no site sign-in", 401)
        info = await state.moodle.site_info(sess.moodle_token)
        return {"token": tok, "user": m._user(info, m.lang_of(lang, sess), await m.can_create(sess.moodle_token)).model_dump()}

    @app.get("/api/v1/auth/whoami")
    async def whoami(req: Request):
        """For the academy website's header: who is signed in (never an error, never the token)."""
        tok = req.cookies.get(COOKIE, "")
        sess = state.codec.read(tok) if tok else None
        if not sess:
            return {"user": None}
        try:
            info = await state.moodle.site_info(sess.moodle_token)
        except EngineError:
            return {"user": None}
        return {"user": {"fullname": info.get("fullname", ""), "teacher": await m.can_create(sess.moodle_token)},
                "app_url": state.settings.app_url}

    @app.post("/api/v1/auth/logout")
    async def logout(resp: Response):
        resp.delete_cookie(COOKIE, domain=cookie_domain(), path="/")
        return {"ok": True}

    # --- the signed-in person's own teacher application ------------------

    def my_app(uid: int) -> dict | None:
        r = st().one("SELECT * FROM applications WHERE userid = ?", uid)
        return app_row(r) if r else None

    def public_app(a: dict | None) -> dict | None:
        if not a:
            return None
        ai = a["ai"] or {}
        return {"status": a["status"], "institution": a["institution"], "department": a["department"],
                "title": a["title"], "evidence": [f["name"] for f in a["evidence"]],
                "more": ai.get("message_to_applicant", "") if a["status"] == "need_more" else "",
                "reason": a["reason"] if a["status"] == "rejected" else "", "created": a["created"]}

    @app.get("/api/v1/me/application")
    async def my_application(sess: Annotated[Session, Depends(m.current)]):
        return {"application": public_app(my_app(sess.user_id)), "teacher": await m.can_create(sess.moodle_token)}

    @app.post("/api/v1/me/application")
    async def apply(body: TeacherInfo, sess: Annotated[Session, Depends(m.current)]):
        """Apply to teach (someone who signed up as a learner, or re-applying after a rejection)."""
        if await m.can_create(sess.moodle_token):
            raise EngineError("already_teacher", "you can already create courses", 409)
        if not body.institution.strip():
            raise EngineError("institution_required", "give your school or organisation", 400)
        u = await find(userid=sess.user_id)
        if not u:
            raise EngineError("not_found", "no such account", 404)
        a = my_app(sess.user_id)
        now = time.time()
        if a and a["status"] in ("pending", "need_more"):
            st().run("UPDATE applications SET institution = ?, department = ?, title = ?, note = ?, updated = ? WHERE id = ?",
                     body.institution.strip(), body.department.strip(), body.title.strip(), body.note.strip(), now, a["id"])
        else:
            st().run("DELETE FROM applications WHERE userid = ?", sess.user_id)
            st().run("INSERT INTO applications (userid, email, name, lang, institution, department, title, note, school, "
                     "status, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)",
                     sess.user_id, u["email"], u["fullname"], sess.lang, body.institution.strip(), body.department.strip(),
                     body.title.strip(), body.note.strip(), 1 if is_school_email(u["email"]) else 0, now, now)
        return {"application": public_app(my_app(sess.user_id))}

    @app.post("/api/v1/me/application/files")
    async def add_evidence(sess: Annotated[Session, Depends(m.current)], file: UploadFile = File(...)):
        a = my_app(sess.user_id)
        if not a or a["status"] not in ("pending", "need_more"):
            raise EngineError("not_found", "no open application", 404)
        if len(a["evidence"]) >= MAX_EVIDENCE:
            raise EngineError("too_many_files", "at most 5 files", 400)
        ext = Path(file.filename or "").suffix.lower()
        if ext not in EVIDENCE_TYPES:
            raise EngineError("file_type", "photos (jpg, png) or PDF only", 415)
        data = await file.read(MAX_EVIDENCE_BYTES + 1)
        if len(data) > MAX_EVIDENCE_BYTES:
            raise EngineError("file_too_large", "at most 10 MB", 413)
        if ext != ".pdf":
            try:
                data = shrink(data)
                ext = ".jpg"
            except Exception as exc:  # noqa: BLE001 - not a readable image
                raise EngineError("file_type", "not a readable image", 415) from exc
        n = len(a["evidence"]) + 1
        stored = f"{n}{ext}"
        (st().evidence_dir(a["id"]) / stored).write_bytes(data)
        a["evidence"].append({"name": (file.filename or stored)[:120], "file": stored, "mime": EVIDENCE_TYPES[ext]})
        st().run("UPDATE applications SET evidence = ?, updated = ? WHERE id = ?", json.dumps(a["evidence"], ensure_ascii=False),
                 time.time(), a["id"])
        return {"application": public_app(my_app(sess.user_id))}

    @app.post("/api/v1/me/application/submit")
    async def submit(sess: Annotated[Session, Depends(m.current)]):
        """The applicant finished (form and evidence): the AI reviews it now."""
        a = my_app(sess.user_id)
        if not a or a["status"] not in ("pending", "need_more"):
            raise EngineError("not_found", "no open application", 404)
        st().run("UPDATE applications SET status = 'pending', submitted = ?, digest = 0 WHERE id = ?", time.time(), a["id"])
        await review(a["id"])
        return {"application": public_app(my_app(sess.user_id))}

    async def review(app_id: int) -> dict | None:
        """The AI's pre-review. It may ask the applicant for more evidence (once); it never decides."""
        r = st().one("SELECT * FROM applications WHERE id = ?", app_id)
        if not r:
            return None
        a = app_row(r)
        if a["status"] not in ("pending", "need_more"):
            return a
        facts, images = evidence_inputs(st(), a, state.ai.sees_images)
        prompt = (f"申请人：{a['name']}\n邮箱：{a['email']}（域名 {a['email'].split('@')[-1]}）\n"
                  f"单位：{a['institution']}\n院系：{a['department'] or '（未填）'}\n职称/职务：{a['title'] or '（未填）'}\n"
                  f"补充说明：{a['note'] or '（无）'}\n申请人语言：{a['lang']}\n"
                  f"之前已请他补充过材料：{'是' if a['more_requested'] else '否'}\n\n证明材料：\n{facts}")
        try:
            if not state.ai.available:
                raise EngineError("ai_unavailable", "", 503)
            ai = await state.ai.json(system=REVIEWER, prompt=prompt, schema=REVIEW_SCHEMA, max_tokens=1500,
                                     images=images, fake=lambda: fake_review(a))
            if ai.get("recommendation") not in ("approve", "more", "reject"):
                raise EngineError("ai_bad_output", "", 502)
        except EngineError as exc:
            log.warning("AI review of application %s failed: %s", app_id, exc.code)
            ai = {"recommendation": "manual", "reason": "AI 暂时无法审核，请人工判断", "checks": [], "message_to_applicant": ""}
        now = time.time()
        status = a["status"]
        if ai["recommendation"] == "more" and not a["more_requested"] and ai.get("message_to_applicant"):
            await mail(a["email"], "more", a["lang"], name=a["name"], message=ai["message_to_applicant"],
                       url=link("/pages/apply/apply"))
            status = "need_more"
            st().run("UPDATE applications SET more_requested = ? WHERE id = ?", now, app_id)
        st().run("UPDATE applications SET ai = ?, reviewed = ?, status = ?, updated = ? WHERE id = ?",
                 json.dumps(ai, ensure_ascii=False), now, status, now, app_id)
        return app_row(st().one("SELECT * FROM applications WHERE id = ?", app_id))

    m.review_application = review

    async def sweep() -> None:
        """Every few minutes: review applications nobody submitted (the page was closed), then tell the
        administrator about new ones (and new course requests) in one email, at most once an hour."""
        now = time.time()
        for a in st().q("SELECT id FROM applications WHERE status = 'pending' AND reviewed = 0 AND created < ?", now - 300):
            await review(a["id"])
        apps = st().q("SELECT * FROM applications WHERE status = 'pending' AND digest = 0 AND reviewed > 0")
        reqs = st().q("SELECT * FROM enrol_requests WHERE status = 'pending' AND digest = 0")
        if not (apps or reqs) or not admin_address():
            return
        if now - float(st().meta("last_digest") or 0) < DIGEST_GAP:
            return
        total = st().one("SELECT COUNT(*) AS n FROM applications WHERE status = 'pending'")["n"]
        lines = [f"有 {total} 份教师申请等你批准" + (f"，{len(reqs)} 个课程报名等你开通" if reqs else "") + "。", ""]
        label = {"approve": "建议批准", "more": "建议补材料", "reject": "建议拒绝", "manual": "需人工判断"}
        for a in apps:
            ai = json.loads(a["ai"] or "{}")
            lines.append(f"· {a['name']}（{a['institution']}{('，' + a['title']) if a['title'] else ''}）"
                         f" — AI {label.get(ai.get('recommendation', 'manual'), '')}：{ai.get('reason', '')}")
        for r in reqs:
            lines.append(f"· 课程报名：{r['name']}（{r['email']}）申请课程 #{r['courseid']}")
        lines += ["", f"去审核：{link('/pages/admin/admin')}"]
        if await state.mailer.send(admin_address(), f"问渠：{total + len(reqs)} 件事等你批准", "\n".join(lines)):
            st().meta("last_digest", str(now))
            for a in apps:
                st().run("UPDATE applications SET digest = 1 WHERE id = ?", a["id"])
            for r in reqs:
                st().run("UPDATE enrol_requests SET digest = 1 WHERE id = ?", r["id"])

    m.accounts_sweep = sweep

    # --- administration ----------------------------------------------------

    def evidence_url(app_id: int, i: int) -> str:
        tok = state.codec.fernet.encrypt(json.dumps({"a": app_id, "i": i}).encode()).decode()
        return f"{state.settings.public_url.rstrip('/')}/api/v1/admin/evidence/{tok}"

    @app.get("/api/v1/admin/summary")
    async def admin_summary(sess: Annotated[Session, Depends(m.current)]):
        if not await is_admin(sess):
            return {"admin": False}
        return {"admin": True,
                "applications": st().one("SELECT COUNT(*) AS n FROM applications WHERE status IN ('pending', 'need_more')")["n"],
                "requests": st().one("SELECT COUNT(*) AS n FROM enrol_requests WHERE status = 'pending'")["n"],
                "mail": state.mailer.configured, "ai": state.ai.provider}

    @app.get("/api/v1/admin/applications")
    async def admin_applications(sess: Annotated[Session, Depends(m.current)], status: str = "open"):
        await require_admin(sess)
        where = {"open": "status IN ('pending', 'need_more')", "done": "status IN ('approved', 'rejected')"}.get(status, "1 = 1")
        out = []
        for r in st().q(f"SELECT * FROM applications WHERE {where} ORDER BY created DESC LIMIT 200"):
            a = app_row(r)
            a["evidence"] = [{"name": f["name"], "mime": f["mime"], "url": evidence_url(a["id"], i)}
                             for i, f in enumerate(a["evidence"])]
            out.append(a)
        return {"applications": out}

    @app.post("/api/v1/admin/applications/{app_id}/decide")
    async def admin_decide(app_id: int, body: DecideIn, sess: Annotated[Session, Depends(m.current)]):
        await require_admin(sess)
        r = st().one("SELECT * FROM applications WHERE id = ?", app_id)
        if not r:
            raise EngineError("not_found", "no such application", 404)
        a = app_row(r)
        if a["status"] in ("approved", "rejected"):
            raise EngineError("already_decided", "already decided", 409)
        reason = body.reason.strip() or ((a["ai"] or {}).get("message_to_applicant") if not body.approve else "") or ""
        if not body.approve and not reason:
            reason = "目前提供的信息还不足以确认教师身份。" if a["lang"] != "en" else \
                "The information given was not enough to confirm that you teach."
        if body.approve:
            await svc("local_wenquest_account_update", userid=a["userid"], teacher=1)
        now = time.time()
        st().run("UPDATE applications SET status = ?, decided = ?, decided_by = ?, reason = ?, updated = ? WHERE id = ?",
                 "approved" if body.approve else "rejected", now, str(sess.user_id), reason, now, app_id)
        if body.approve:
            sent = await mail(a["email"], "approved", a["lang"], name=a["name"], url=link("/pages/studio/studio"))
        else:
            sent = await mail(a["email"], "rejected", a["lang"], name=a["name"], reason=reason, url=link("/pages/apply/apply"))
        return {"ok": True, "mailed": sent}

    @app.post("/api/v1/admin/applications/{app_id}/review")
    async def admin_review(app_id: int, sess: Annotated[Session, Depends(m.current)]):
        await require_admin(sess)
        st().run("UPDATE applications SET status = 'pending' WHERE id = ? AND status = 'need_more'", app_id)
        a = await review(app_id)
        if not a:
            raise EngineError("not_found", "no such application", 404)
        return {"ai": a["ai"], "status": a["status"]}

    @app.get("/api/v1/admin/evidence/{signed}")
    async def admin_evidence(signed: str):
        """An evidence file; the encrypted link (one day) is only given to administrators."""
        try:
            d = json.loads(state.codec.fernet.decrypt(signed.encode(), ttl=m.FILE_TTL))
        except Exception as exc:  # noqa: BLE001 - any bad link
            raise EngineError("link_expired", "link expired", 410) from exc
        r = st().one("SELECT * FROM applications WHERE id = ?", int(d["a"]))
        files = app_row(r)["evidence"] if r else []
        if not (0 <= int(d["i"]) < len(files)):
            raise EngineError("not_found", "no such file", 404)
        f = files[int(d["i"])]
        path = st().evidence_dir(int(d["a"])) / f["file"]
        return Response(path.read_bytes(), media_type=f["mime"], headers={
            "Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; img-src 'self' data:; sandbox",
            "Content-Disposition": f"inline; filename*=UTF-8''{quote(f['name'])}"})

    @app.get("/api/v1/admin/users")
    async def admin_users(sess: Annotated[Session, Depends(m.current)], q: str = "", page: int = 0):
        await require_admin(sess)
        r = await svc("local_wenquest_account_search", query=q[:100], page=max(0, page), perpage=50)
        return {"total": r["total"], "users": r["users"]}

    @app.put("/api/v1/admin/users/{uid}")
    async def admin_user_change(uid: int, body: UserChangeIn, sess: Annotated[Session, Depends(m.current)]):
        await require_admin(sess)
        if uid == sess.user_id:
            raise EngineError("forbidden", "you cannot change your own account here", 403)
        params: dict[str, int] = {}
        if body.suspended is not None:
            params["suspended"] = 1 if body.suspended else 0
        if body.teacher is not None:
            params["teacher"] = 1 if body.teacher else 0
        u = await svc("local_wenquest_account_update", userid=uid, **params)
        if body.teacher:
            now = time.time()
            st().run("UPDATE applications SET status = 'approved', decided = ?, decided_by = ? WHERE userid = ? AND "
                     "status IN ('pending', 'need_more')", now, str(sess.user_id), uid)
        return u

    @app.post("/api/v1/admin/users/{uid}/reset")
    async def admin_user_reset(uid: int, sess: Annotated[Session, Depends(m.current)]):
        """Send the person a password reset code (they finish on the 'forgot password' page)."""
        await require_admin(sess)
        u = await find(userid=uid)
        if not u or not EMAIL_RE.match(u["email"] or ""):
            raise EngineError("not_found", "no email for this account", 404)
        now = time.time()
        code = f"{secrets.randbelow(10**6):06d}"
        email = u["email"].lower()
        st().run("INSERT INTO codes (email, purpose, hash, expires, created, ip) VALUES (?, 'reset', ?, ?, ?, 'admin')",
                 email, code_hash(email, "reset", code), now + 3 * 86400, now)
        lang = "en" if u["lang"] == "en" else "zh"
        subject, text = texts("code", lang, code=code, purpose="reset")
        text = text.replace("10 分钟内有效", "3 天内有效").replace("valid for 10 minutes", "valid for 3 days")
        text += f"\n\n{link('/pages/login/forgot?email=' + quote(email))}"
        return {"mailed": await state.mailer.send(email, subject, text)}

    m.accounts_svc = svc
    m.accounts_find = find
    m.accounts_mail = mail
    m.accounts_link = link
    m.accounts_is_admin = is_admin
    m.accounts_require_admin = require_admin

