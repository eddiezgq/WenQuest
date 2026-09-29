"""Course catalogue with free and paid courses (round 3, step C3).

Teachers choose per course: not listed / listed and free / listed and paid (a price). Anyone,
signed in or not, sees the catalogue. Joining a free course is immediate; for a paid course the
learner asks to join and the administrator opens it with one click (online payment comes later).
Settings live in the accounts store (accounts.db); enrolment goes through the accounts service.
"""

import time
from typing import Annotated

from fastapi import Depends, Header
from pydantic import BaseModel, Field

from .moodle import EngineError
from .multilang import plain
from .session import Session


class ListingIn(BaseModel):
    mode: str = Field(pattern="^(private|free|paid)$")
    price: float = Field(default=0, ge=0, le=1000000)
    currency: str = Field(default="CNY", pattern="^(CNY|USD)$")
    blurb: str = Field(default="", max_length=2000)


class JoinIn(BaseModel):
    note: str = Field(default="", max_length=1000)


class RequestDecisionIn(BaseModel):
    approve: bool


def register(app, m) -> None:
    state = m.state

    def st():
        return state.accounts

    def listing(cid: int) -> dict:
        r = st().one("SELECT * FROM catalog WHERE courseid = ?", cid)
        return {"mode": r["mode"], "price": r["price"], "currency": r["currency"], "blurb": r["blurb"]} if r else \
            {"mode": "private", "price": 0, "currency": "CNY", "blurb": ""}

    async def maybe_session(authorization: Annotated[str | None, Header()] = None) -> Session | None:
        if not authorization or not authorization.lower().startswith("bearer "):
            return None
        return state.codec.read(authorization.split(" ", 1)[1].strip())

    async def cards(ids: list[int], uid: int, lang: str) -> list[dict]:
        if not ids:
            return []
        r = await m.accounts_svc("local_wenquest_account_courses", courseids=ids, userid=uid)
        out = []
        for c in r["courses"]:
            if not c["visible"]:
                continue
            ls = listing(c["id"])
            req = st().one("SELECT status FROM enrol_requests WHERE courseid = ? AND userid = ?", c["id"], uid) if uid else None
            out.append({
                "id": c["id"], "name": plain(c["fullname"], lang),
                "summary": plain(c["summary"], lang)[:400], "teachers": c["teachers"],
                "chapters": c["sections"], "students": c["students"], "mode": ls["mode"], "price": ls["price"],
                "currency": ls["currency"], "blurb": ls["blurb"], "enrolled": c["enrolled"],
                "requested": bool(req and req["status"] == "pending"),
            })
        return out

    @app.get("/api/v1/catalog")
    async def catalog(sess: Annotated[Session | None, Depends(maybe_session)], lang: str | None = None):
        ids = [r["courseid"] for r in st().q("SELECT courseid FROM catalog WHERE mode IN ('free', 'paid') ORDER BY updated DESC")]
        return {"courses": await cards(ids, sess.user_id if sess else 0, m.lang_of(lang, sess)), "signed_in": bool(sess)}

    @app.get("/api/v1/courses/{cid}/listing")
    async def get_listing(cid: int, sess: Annotated[Session, Depends(m.current)]):
        if not await state.moodle.can_edit_course(sess.moodle_token, cid):
            raise EngineError("forbidden", "teachers only", 403)
        return listing(cid)

    @app.put("/api/v1/courses/{cid}/listing")
    async def set_listing(cid: int, body: ListingIn, sess: Annotated[Session, Depends(m.current)]):
        if not await state.moodle.can_edit_course(sess.moodle_token, cid):
            raise EngineError("forbidden", "teachers only", 403)
        if body.mode == "paid" and body.price <= 0:
            raise EngineError("price_required", "a paid course needs a price", 400)
        st().run("INSERT INTO catalog (courseid, mode, price, currency, blurb, updated, updated_by) VALUES (?, ?, ?, ?, ?, ?, ?) "
                 "ON CONFLICT(courseid) DO UPDATE SET mode = excluded.mode, price = excluded.price, currency = excluded.currency, "
                 "blurb = excluded.blurb, updated = excluded.updated, updated_by = excluded.updated_by",
                 cid, body.mode, round(body.price, 2) if body.mode == "paid" else 0, body.currency, body.blurb.strip(),
                 time.time(), sess.user_id)
        return listing(cid)

    @app.post("/api/v1/catalog/{cid}/join")
    async def join(cid: int, body: JoinIn, sess: Annotated[Session, Depends(m.current)]):
        ls = listing(cid)
        if ls["mode"] == "private":
            raise EngineError("not_found", "this course is not open for joining", 404)
        if ls["mode"] == "free":
            r = await m.accounts_svc("local_wenquest_account_enrol", userid=sess.user_id, courseid=cid)
            return {"status": "enrolled", "already": r["status"] == "already"}
        u = await m.accounts_find(userid=sess.user_id)
        st().run("INSERT INTO enrol_requests (courseid, userid, name, email, note, status, created) VALUES (?, ?, ?, ?, ?, 'pending', ?) "
                 "ON CONFLICT(courseid, userid) DO UPDATE SET status = 'pending', note = excluded.note, created = excluded.created, "
                 "digest = 0 WHERE enrol_requests.status <> 'approved'",
                 cid, sess.user_id, u["fullname"] if u else "", u["email"] if u else "", body.note.strip(), time.time())
        return {"status": "requested"}

    @app.get("/api/v1/admin/requests")
    async def admin_requests(sess: Annotated[Session, Depends(m.current)], status: str = "pending"):
        await m.accounts_require_admin(sess)
        rows = st().q("SELECT * FROM enrol_requests WHERE status = ? ORDER BY created DESC LIMIT 200",
                      status if status in ("pending", "approved", "rejected") else "pending")
        names = {c["id"]: c for c in (await m.accounts_svc("local_wenquest_account_courses",
                                                           courseids=sorted({r["courseid"] for r in rows}))).get("courses", [])} if rows else {}
        for r in rows:
            c = names.get(r["courseid"])
            r["course"] = plain(c["fullname"], m.lang_of(None, sess)) if c else f"#{r['courseid']}"
            ls = listing(r["courseid"])
            r["price"], r["currency"] = ls["price"], ls["currency"]
        return {"requests": rows}

    @app.post("/api/v1/admin/requests/{rid}/decide")
    async def admin_request_decide(rid: int, body: RequestDecisionIn, sess: Annotated[Session, Depends(m.current)]):
        await m.accounts_require_admin(sess)
        r = st().one("SELECT * FROM enrol_requests WHERE id = ?", rid)
        if not r:
            raise EngineError("not_found", "no such request", 404)
        if r["status"] != "pending":
            raise EngineError("already_decided", "already decided", 409)
        mailed = False
        if body.approve:
            await m.accounts_svc("local_wenquest_account_enrol", userid=r["userid"], courseid=r["courseid"])
            u = await m.accounts_find(userid=r["userid"])
            c = (await m.accounts_svc("local_wenquest_account_courses", courseids=[r["courseid"]]))["courses"]
            if u and c:
                lang = "en" if u["lang"] == "en" else "zh"
                mailed = await m.accounts_mail(u["email"], "enrolled", lang, name=u["fullname"],
                                               course=plain(c[0]["fullname"], lang),
                                               url=m.accounts_link(f"/pages/course/course?id={r['courseid']}"))
        st().run("UPDATE enrol_requests SET status = ?, decided = ? WHERE id = ?",
                 "approved" if body.approve else "rejected", time.time(), rid)
        return {"ok": True, "mailed": mailed}
