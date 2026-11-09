"""问渠质量 ERP 试点企业（第 97 轮，wenquest-ops ADR-0025）：管理员发邀请，企业凭链接自己注册，服务器自动开通。

网关不碰 Docker。开通经一个文件夹交接（服务器 /opt/wenquest/pilot-queue，挂进网关是 /pilot-queue，WQ_PILOT_QUEUE）：
  网关写 req-<编号>.json（企业名、联系人、邮箱、语言）→ 服务器上 deploy 用户的 pilot-runner.sh（wenquest-ops，每分钟）
  跑 tenant.sh new，写 state-<编号>.json（installing / active / failed）和 res-<编号>.json（老板的初始密码，600）；
  网关每 20 秒看一次：res 到了就把账号发到老板邮箱、删掉 res 文件。runner 每次还写 host.json（可用内存），
  管理页和开通前的检查都看它。停用 / 恢复写 cmd-<编号>.json。

  GET  /api/v1/admin/pilots                    名额、内存、邀请、各家状态
  POST /api/v1/admin/pilots/invite             {email, company?, lang?} 发邀请邮件（7 天有效、只能用一次）
  POST /api/v1/admin/pilots/{id}/stop|start    停用（记录保留）/ 恢复
  GET  /api/v1/public/pilot/{token}            邀请是否有效（邮箱只显示一部分）
  POST /api/v1/public/pilot/{token}/code       发 6 位验证码到受邀邮箱
  POST /api/v1/public/pilot/{token}/apply      {company, id, contact, code} 提交，排队开通
  GET  /api/v1/public/pilot/{token}/status     开通进度（不含密码）
  GET  /api/v1/caddy/ask?domain=               Caddy 按需办证书前来问：是已开通的试点企业就放行，别的转问数字工厂
"""

import asyncio
import json
import os
import re
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Response
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

DAY = 86400
INVITE_DAYS = 7
ID_RE = re.compile(r"^[a-z][a-z0-9-]{2,19}$")
# 部署直接装的演示企业（不经开通流程）：证书照办，试点企业不能用这些编号
QMS_DEMOS = {"sewing"}
RESERVED = {"demo", "www", "api", "admin", "erp", "mail", "qms", "test", "staging"} | QMS_DEMOS
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,24}$")
MIN_FREE_MB = 1536
RUNNER_STALE = 600                    # 10 分钟没有心跳：开通程序没在跑


class InviteIn(BaseModel):
    email: str = Field(max_length=254)
    company: str = Field(default="", max_length=100)
    lang: str = Field(default="", max_length=5)


class ApplyIn(BaseModel):
    company: str = Field(min_length=2, max_length=100)
    id: str = Field(min_length=3, max_length=20)
    contact: str = Field(min_length=1, max_length=40)
    code: str = Field(min_length=6, max_length=6)


def mask(email: str) -> str:
    name, _, dom = email.partition("@")
    return (name[:2] + "***@" + dom) if dom else email


def register(app, m) -> None:
    state = m.state

    def cn() -> bool:
        return state.settings.region.strip().lower() == "cn"

    def zh(lang: str = "") -> bool:
        # 第 129 轮：美国站的邀请、注册页、邮件、开出来的企业一律英文（原来跟着管理员界面语言，开出了中文的）
        return cn() and (lang or "zh").startswith("zh")

    def queue() -> Path:
        return Path(os.environ.get("WQ_PILOT_QUEUE", "/pilot-queue"))

    def most() -> int:
        # 国内 3 家；美国服务器还跑着数字工厂，内存只够 2 家（11-06 换装后实测可用约 3 GB）
        return int(os.environ.get("WQ_PILOT_MAX", "") or (3 if cn() else 2))

    def db() -> sqlite3.Connection:
        d = Path(state.settings.data_dir)
        d.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(d / "pilots.db"), isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("""create table if not exists invite(token text primary key, email text, company text, lang text,
                     created integer, expires integer, used integer default 0, code text, code_exp integer default 0,
                     code_sent integer default 0, tries integer default 0)""")
        c.execute("""create table if not exists tenant(id text primary key, company text, contact text, email text, lang text,
                     status text, error text, token text, created integer, ready integer)""")
        # ops ADR-0027：官网申请里勾了“问渠质量 ERP”的，在共用演示企业里开一个体验账号（每晚还原）
        c.execute("""create table if not exists trial(id text primary key, name text, email text, org text, status text,
                     error text, created integer)""")
        return c

    def domain(kind: str, tid: str) -> str:
        return f"{tid}.{kind}.{state.settings.site_domain}"

    def host() -> dict:
        try:
            h = json.loads((queue() / "host.json").read_text(encoding="utf-8"))
            h["fresh"] = time.time() - float(h.get("ts", 0)) < RUNNER_STALE
            return h
        except (OSError, ValueError):
            return {"fresh": False}

    def taken(c) -> int:
        return c.execute("select count(*) from tenant where status in ('queued','installing','active','stopped')").fetchone()[0]

    def tenant_out(t) -> dict:
        d = dict(t)
        d.pop("token", None)
        d["url"] = f"https://{domain('qms', t['id'])}" if t["status"] == "active" else None
        return d

    def write(name: str, data: dict) -> None:
        q = queue()
        q.mkdir(parents=True, exist_ok=True)
        tmp = q / f".{name}.tmp"
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(q / name)

    def link(token: str, lang: str) -> str:
        base = (state.settings.public_url or f"https://{state.settings.site_domain}").rstrip("/")
        if base.startswith("https://learn."):
            base = "https://" + base[len("https://learn."):]
        return f"{base}/pilot/?t={token}" + ("" if zh(lang) else "&lang=en")

    async def mail(to: str, subject: str, text: str) -> None:
        await state.mailer.send(to, subject, text)

    # ------------------------------------------------------------------ administration

    @app.get("/api/v1/admin/pilots")
    async def list_pilots(sess: Annotated[Session, Depends(m.current)]):
        await m.accounts_require_admin(sess)
        now = time.time()
        with db() as c:
            inv = [{k: r[k] for k in ("email", "company", "lang", "created", "expires", "used")} | {"live": not r["used"] and r["expires"] > now}
                   for r in c.execute("select * from invite order by created desc limit 50")]
            ts = [tenant_out(t) for t in c.execute("select * from tenant order by created desc")]
            used = taken(c)
        h = host()
        return {"max": most(), "used": used, "host": {"fresh": h["fresh"], "mem_free_mb": h.get("mem_free_mb"), "ts": h.get("ts")},
                "min_free_mb": MIN_FREE_MB, "invites": inv, "tenants": ts}

    @app.post("/api/v1/admin/pilots/invite")
    async def invite(body: InviteIn, sess: Annotated[Session, Depends(m.current)]):
        await m.accounts_require_admin(sess)
        email = body.email.strip().lower()
        if not EMAIL_RE.match(email):
            raise EngineError("bad_email", "邮箱格式不对" if cn() else "Not a valid email address", 400)
        lang = (body.lang if body.lang in ("zh", "en") else "zh") if cn() else "en"
        with db() as c:
            if taken(c) >= most():
                raise EngineError("pilot_full", f"试点企业已满 {most()} 家（WQ_PILOT_MAX）", 409)
            token = secrets.token_urlsafe(18)
            now = int(time.time())
            c.execute("insert into invite(token,email,company,lang,created,expires) values(?,?,?,?,?,?)",
                      (token, email, body.company.strip(), lang, now, now + INVITE_DAYS * DAY))
        url = link(token, lang)
        if zh(lang):
            await mail(email, "邀请：开通问渠质量 ERP 试点（免费 3 个月）",
                       f"您好！\n\n问渠科技邀请{body.company.strip() or '贵单位'}免费试用问渠质量 ERP 3 个月：每家单位一套独立的系统，"
                       f"数据存于境内云服务器、单独隔离。\n\n请在 {INVITE_DAYS} 天内打开下面的链接，填写单位名称和联系人，"
                       f"用这个邮箱收验证码确认，系统会自动开通，并把账号发到这个邮箱：\n{url}\n\n这个链接只能用一次。\n\n问渠科技")
        else:
            await mail(email, "Invitation: a free 3-month pilot of WenQuest Ops",
                       f"Hello,\n\nWenQuest invites {body.company.strip() or 'your company'} to try WenQuest Ops, our quality-centred AI ERP, "
                       f"free for 3 months - your own separate installation.\n\nWithin {INVITE_DAYS} days, open the link below, enter your "
                       f"company and name, and confirm with the code we email you. It is set up automatically and the sign-in "
                       f"is sent to this address:\n{url}\n\nThe link works once.\n\nWenQuest")
        return {"ok": True, "email": email, "link": url, "expires": now + INVITE_DAYS * DAY}

    @app.post("/api/v1/admin/pilots/{tid}/{action}")
    async def stop_start(tid: str, action: str, sess: Annotated[Session, Depends(m.current)]):
        await m.accounts_require_admin(sess)
        if action not in ("stop", "start"):
            raise EngineError("not_found", "no such action", 404)
        with db() as c:
            t = c.execute("select * from tenant where id=?", (tid,)).fetchone()
            if not t or t["status"] not in ("active", "stopped"):
                raise EngineError("not_found", "没有这家试点企业，或还没开通好", 404)
            write(f"cmd-{tid}.json", {"id": tid, "cmd": action, "ts": int(time.time())})
            c.execute("update tenant set status=? where id=?", ("stopped" if action == "stop" else "active", tid))
            return tenant_out(c.execute("select * from tenant where id=?", (tid,)).fetchone())

    # ------------------------------------------------------------------ the invited company

    def get_invite(c, token: str):
        r = c.execute("select * from invite where token=?", (token,)).fetchone()
        if not r or r["expires"] < time.time():
            raise EngineError("invite_invalid", "邀请链接无效或已过期，请联系问渠科技重新发送" if cn() else
                              "This invitation link is not valid or has expired", 404)
        return r

    @app.get("/api/v1/public/pilot/{token}")
    async def invite_info(token: str):
        with db() as c:
            r = get_invite(c, token)
            t = c.execute("select * from tenant where token=?", (token,)).fetchone()
        return {"email": mask(r["email"]), "company": r["company"], "lang": "zh" if zh(r["lang"]) else "en", "used": bool(r["used"]),
                "status": t["status"] if t else None, "domain": f"<编号>.qms.{state.settings.site_domain}"}

    @app.post("/api/v1/public/pilot/{token}/code")
    async def send_code(token: str):
        now = int(time.time())
        with db() as c:
            r = get_invite(c, token)
            if r["used"]:
                raise EngineError("invite_used", "这个邀请已经用过了" if zh(r["lang"]) else "This invitation was used already", 409)
            if now - r["code_sent"] < 60:
                raise EngineError("too_fast", "验证码刚发过，请一分钟后再试" if zh(r["lang"]) else "Please wait a minute", 429)
            code = f"{secrets.randbelow(10 ** 6):06d}"
            c.execute("update invite set code=?, code_exp=?, code_sent=?, tries=0 where token=?", (code, now + 900, now, token))
        if zh(r["lang"]):
            await mail(r["email"], f"问渠质量 ERP 试点验证码：{code}", f"您的验证码是 {code}，15 分钟内有效。不是您本人操作请忽略。")
        else:
            await mail(r["email"], f"WenQuest Ops pilot code: {code}", f"Your code is {code}. It is valid for 15 minutes.")
        return {"ok": True, "email": mask(r["email"])}

    @app.post("/api/v1/public/pilot/{token}/apply")
    async def apply(token: str, body: ApplyIn):
        tid = body.id.strip().lower()
        with db() as c:
            r = get_invite(c, token)
            en = not zh(r["lang"])
            if r["used"]:
                raise EngineError("invite_used", "This invitation was used already" if en else "这个邀请已经用过了", 409)
            if r["tries"] >= 5:
                raise EngineError("too_many_tries", "Too many wrong codes; ask for a new one" if en else "验证码错太多次，请重新获取", 429)
            if not r["code"] or r["code_exp"] < time.time() or not secrets.compare_digest(r["code"], body.code.strip()):
                c.execute("update invite set tries=tries+1 where token=?", (token,))
                raise EngineError("bad_code", "Wrong or expired code" if en else "验证码不对或已过期", 400)
            if not ID_RE.match(tid) or tid.endswith("-") or tid in RESERVED:
                raise EngineError("bad_id", "The short name: 3-20 lower-case letters, digits or -, starting with a letter" if en else
                                  "简称（网址里用）：3–20 位小写字母、数字或 -，以字母开头", 400)
            if c.execute("select 1 from tenant where id=?", (tid,)).fetchone():
                raise EngineError("id_taken", "This short name is taken; choose another" if en else "这个简称已被使用，请换一个", 409)
            if taken(c) >= most():
                raise EngineError("pilot_full", "All pilot places are taken; we will contact you" if en else
                                  "试点名额已满，我们会尽快联系您", 409)
            h = host()
            if not h["fresh"] or (h.get("mem_free_mb") or 0) < MIN_FREE_MB:
                raise EngineError("server_busy", "We cannot set it up right now; we have been told and will contact you" if en else
                                  "服务器暂时不能开通，已通知管理员，我们会尽快联系您", 503)
            now = int(time.time())
            c.execute("insert into tenant(id,company,contact,email,lang,status,token,created) values(?,?,?,?,?,'queued',?,?)",
                      (tid, body.company.strip(), body.contact.strip(), r["email"], "zh" if zh(r["lang"]) else "en", token, now))
            c.execute("update invite set used=1, code=null where token=?", (token,))
            write(f"req-{tid}.json", {"id": tid, "name": body.company.strip(), "contact": body.contact.strip(),
                                      "email": r["email"], "lang": "zh" if zh(r["lang"]) else "en", "ts": now})
        return {"ok": True, "id": tid, "status": "queued", "minutes": 15}

    @app.get("/api/v1/public/pilot/{token}/status")
    async def status(token: str):
        with db() as c:
            get_invite(c, token)
            t = c.execute("select * from tenant where token=?", (token,)).fetchone()
        if not t:
            return {"status": None}
        return {"status": t["status"], "url": f"https://{domain('qms', t['id'])}" if t["status"] == "active" else None}

    # ------------------------------------------------------------------ certificates

    @app.get("/api/v1/caddy/ask")
    async def caddy_ask(domain: str = ""):
        d = domain.lower().strip(".")
        site = state.settings.site_domain.lower()
        parts = d.split(".")
        if site and d.endswith("." + site) and len(parts) == len(site.split(".")) + 2 and parts[1] in ("qms", "qms-erp"):
            # 演示企业（第 109 轮 26f 的蓝湾缝纫机械，sewing.qms）由部署直接装、不经开通流程，不在 tenant 表里：
            # 按名单放行（第 124 轮补：原来漏了，证书办不下来，网址打不开）
            if parts[0] in QMS_DEMOS:
                return Response(status_code=200)
            with db() as c:
                ok = c.execute("select 1 from tenant where id=? and status in ('active','stopped')", (parts[0],)).fetchone()
            return Response(status_code=200 if ok else 404)
        try:                                           # 班级工厂 <编号>.factory / <编号>.erp 照旧问数字工厂（第 10 轮）
            r = await state.http.get(os.environ.get("WQ_FACTORY_ASK", "http://wqf-hub:8100/api/caddy/ask"),
                                     params={"domain": d}, timeout=5)
            return Response(status_code=200 if r.status_code == 200 else 404)
        except Exception:                              # noqa: BLE001  问不到就不办证书
            return Response(status_code=404)

    # ------------------------------------------------------------------ results from the server

    async def collect() -> None:
        q = queue()
        if not q.is_dir():
            return
        for f in sorted(q.glob("state-*.json")):
            try:
                s = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            tid = s.get("id", "")
            with db() as c:
                t = c.execute("select * from tenant where id=?", (tid,)).fetchone()
                if not t:
                    continue
                if s.get("status") == "installing" and t["status"] == "queued":
                    c.execute("update tenant set status='installing' where id=?", (tid,))
                elif s.get("status") == "failed" and t["status"] in ("queued", "installing"):
                    c.execute("update tenant set status='failed', error=? where id=?", (str(s.get("error", ""))[:500], tid))
                    admin = state.settings.admin_email or state.settings.admin_email_fallback
                    if admin:
                        await mail(admin, f"试点企业 {tid} 开通失败", f"{t['company']}（{t['email']}）开通失败：\n{s.get('error', '')}\n"
                                   "服务器上看 /opt/wenquest/pilot-queue 和 /opt/wenquest/qms-tenants/" + tid)
        for f in sorted(q.glob("res-trial-*.json")):
            await trial_done(f)
        for f in sorted(q.glob("res-*.json")):
            if f.name.startswith("res-trial-"):
                continue
            try:
                res = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            tid = res.get("id", "")
            with db() as c:
                t = c.execute("select * from tenant where id=?", (tid,)).fetchone()
            if not t:
                continue
            if zh(t["lang"]):
                text = (f"{t['contact']}您好！\n\n{t['company']}的问渠质量 ERP 已开通，免费试用 3 个月。\n\n"
                        f"工作台：{res.get('url')}\nERPNext：{res.get('erp_url')}（从工作台菜单“ERPNext ↗”直接进，不用再登录）\n"
                        f"账号：{res.get('email')}\n初始密码：{res.get('password')}\n\n请登录后在“我的账户”（点右上角自己的名字）改密码，"
                        "再到“人员”页添加同事。使用中遇到问题，回复这封邮件即可。\n\n问渠科技")
                subj = "问渠质量 ERP 已开通：您的账号"
            else:
                text = (f"Hello {t['contact']},\n\nWenQuest Ops for {t['company']} is ready - free for 3 months.\n\n"
                        f"Workspace: {res.get('url')}\nERPNext: {res.get('erp_url')} (open it from the workspace menu, no second sign-in)\n"
                        f"Email: {res.get('email')}\nFirst password: {res.get('password')}\n\nPlease change the password under My account, "
                        "then add your colleagues on the People page. Just reply to this email with any problem.\n\nWenQuest")
                subj = "WenQuest Ops is ready: your sign-in"
            await mail(t["email"], subj, text)
            f.unlink(missing_ok=True)                  # 密码只在这封邮件里
            with db() as c:
                c.execute("update tenant set status='active', ready=?, error=null where id=?", (int(time.time()), tid))

    # ------------------------------------------------------------------ 质量 ERP 共用演示企业的体验账号（ops ADR-0027）

    def open_trial(name: str, email: str, org: str) -> str:
        tid = "t" + secrets.token_hex(6)
        with db() as c:
            c.execute("insert into trial(id,name,email,org,status,created) values(?,?,?,?, 'queued', ?)",
                      (tid, name, email.lower(), org, int(time.time())))
        write(f"trial-{tid}.json", {"id": tid, "name": name, "email": email.lower()})
        return tid

    async def trial_done(f: Path) -> None:
        try:
            res = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        with db() as c:
            t = c.execute("select * from trial where id=?", (res.get("id", ""),)).fetchone()
        if t and res.get("error"):
            admin = state.settings.admin_email or state.settings.admin_email_fallback
            if admin:
                await mail(admin, "质量 ERP 体验账号没开成", f"{t['org']} {t['name']}（{t['email']}）：{res['error']}")
            with db() as c:
                c.execute("update trial set status='failed', error=? where id=?", (str(res["error"])[:500], t["id"]))
        elif t:
            # 第 109 轮 26f：缝纫机演示企业也装好了的，同一个账号、同一个初始密码也开在那里
            sew = (f"\n另一家演示企业：蓝湾缝纫机械（缝纫机厂，看产品数据管理 PLM：零件、BOM、型号配置、设计变更）\n"
                   f"工作台：{res['sewing_url']}（同一个账号和初始密码，两边各自改密码）\n") if res.get("sewing_url") else ""
            await mail(t["email"], "问渠质量 ERP 体验账号",
                       f"{t['name']}，你好：\n\n问渠质量 ERP 的体验账号已开通，可以用到 {res.get('expires')}。\n\n"
                       f"工作台：{res.get('url')}\n账号：{res.get('email')}\n初始密码：{res.get('password')}\n{sew}\n"
                       "请注意：这是供大家体验的共用演示企业（海港五金供应" + ("、蓝湾缝纫机械" if sew else "") +
                       "，数据是虚构的），别人也在用，每晚还原成演示数据。"
                       "请不要录入真实的企业数据。\n\n想用自己的数据试（独立的一套、数据保留、免费 3 个月），直接回复这封邮件，"
                       "我们为你开通独立的试点企业。\n\n问渠科技")
            with db() as c:
                c.execute("update trial set status='active', error=null where id=?", (t["id"],))
        f.unlink(missing_ok=True)                      # 密码只在这封邮件里

    m.pilots_open_trial = open_trial

    async def loop() -> None:
        while True:
            try:
                await collect()
            except Exception:                          # 下一轮再试
                pass
            await asyncio.sleep(20)

    m.pilots_collect = collect
    m.pilots_loop = loop
