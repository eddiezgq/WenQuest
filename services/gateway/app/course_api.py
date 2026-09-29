"""Course menus in WenQuest's own UI (round 3, D32 / step B1): announcements, discussions,
online class sessions, people and groups. Registered by main.create_app().

Every call uses the signed-in user's own Moodle token, so Moodle's permissions decide who may do
what; the gateway only reshapes the data for the WenQuest pages.
"""

import html as htmllib
import json
import random
import re
from typing import Annotated, Any

from fastapi import Depends
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

MAX_TEXT = 20000


class PostIn(BaseModel):
    subject: str = Field(default="", max_length=255)
    message: str = Field(min_length=1, max_length=MAX_TEXT)


class ReplyIn(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_TEXT)


class StateIn(BaseModel):
    on: bool


class MeetingIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    provider: str = Field(default="tencent", pattern="^(tencent|zoom|other)$")
    url: str = Field(default="", max_length=1000)
    meetingcode: str = Field(default="", max_length=64)
    passcode: str = Field(default="", max_length=64)
    notes: str = Field(default="", max_length=2000)
    timestart: int = Field(gt=0)
    duration: int = Field(default=90, ge=5, le=600)


class EnrolIn(BaseModel):
    identifiers: list[str] = Field(min_length=1, max_length=500)
    role: str = Field(default="student", pattern="^(student|teacher|editingteacher)$")


class GroupIn(BaseModel):
    name: str = Field(default="", max_length=254)
    members: list[int] | None = Field(default=None, max_length=2000)


class PlanGroup(BaseModel):
    name: str = Field(min_length=1, max_length=254)
    members: list[int] = Field(default_factory=list, max_length=2000)


class PlanIn(BaseModel):
    groups: list[PlanGroup] = Field(min_length=1, max_length=200)
    replace: bool = False


class AiGroupsIn(BaseModel):
    request: str = Field(default="", max_length=1000)


def text_html(s: str) -> str:
    """What the page sends: plain text becomes paragraphs; light HTML from the editor is kept (Moodle cleans it)."""
    s = s.strip()
    if re.search(r"</?(p|br|ul|ol|li|strong|em|b|i|a|h\d|blockquote|table|img)\b", s, re.I):
        return s
    paras = [p for p in re.split(r"\n\s*\n", s) if p.strip()]
    return "".join("<p>" + htmllib.escape(p).replace("\n", "<br>") + "</p>" for p in paras)


def validate_plan(groups: list[dict], students: list[int]) -> list[dict]:
    """Every student in exactly one group: drop unknown and repeated ids, put the missing into the smallest groups."""
    known, seen, out = set(students), set(), []
    for i, g in enumerate(groups):
        members = []
        for uid in g.get("members") or []:
            try:
                uid = int(uid)
            except (TypeError, ValueError):
                continue
            if uid in known and uid not in seen:
                seen.add(uid)
                members.append(uid)
        out.append({"name": str(g.get("name") or f"第{i + 1}组").strip()[:254] or f"第{i + 1}组", "members": members,
                    "note": str(g.get("note") or "")[:300]})
    out = [g for g in out if g["members"] or len(out) == 1] or [{"name": "第1组", "members": [], "note": ""}]
    for uid in students:
        if uid not in seen:
            min(out, key=lambda g: len(g["members"]))["members"].append(uid)
    return out


def balanced_groups(students: list[dict], size: int) -> list[dict]:
    """Offline plan: snake order by grade so each group gets a spread (random when there are no grades)."""
    people = list(students)
    if any(p.get("grade") is not None for p in people):
        people.sort(key=lambda p: -(p.get("grade") or 0))
    else:
        random.Random(len(people)).shuffle(people)
    n = max(1, round(len(people) / max(2, size)))
    groups: list[list[int]] = [[] for _ in range(n)]
    for i, p in enumerate(people):
        row, col = divmod(i, n)
        groups[col if row % 2 == 0 else n - 1 - col].append(p["id"])
    return [{"name": f"第{i + 1}组", "members": g, "note": ""} for i, g in enumerate(groups)]


GROUPING = (
    "You are the teaching assistant of a university course on WenQuest. Split the students into groups as "
    "the teacher asks. Every student must be in exactly one group; use only the ids given. If the teacher "
    "gives no size, use groups of 4 (3-5). Balance groups by grade when grades are given unless the teacher "
    "says otherwise. Group names: 第1组, 第2组 ... unless the teacher asks for names. Give each group a short "
    "note on why it is balanced, and a one-sentence explanation of the whole plan, in Chinese."
)


def register(app, m) -> None:
    current = m.current
    state = m.state

    def avatar(url: str | None, tok: str) -> str | None:
        """Only pictures people uploaded; the default silhouette is drawn by the page (initials)."""
        return m.proxied(url, tok) if url and "/pluginfile.php/" in url else None

    def clean(h: str | None, lg: str, tok: str) -> str:
        return m.content.clean(m.resolve(h, lg), state.settings.moodle_url, m.sign_file(tok))

    async def call(sess: Session, fn: str, lang: str | None = None, **params: Any) -> Any:
        return await state.moodle.call(sess.moodle_token, fn, lang, **params)

    async def is_teacher(sess: Session, courseid: int) -> bool:
        try:
            return await state.moodle.can_edit_course(sess.moodle_token, courseid)
        except EngineError:
            return False

    async def forums(sess: Session, courseid: int, lg: str) -> list[dict]:
        rows = await call(sess, "mod_forum_get_forums_by_courses", lg, courseids=[courseid])
        return [f for f in rows if int(f.get("course", 0)) == courseid]

    def discussion_row(d: dict, lg: str, tok: str) -> dict:
        return {
            "id": d.get("discussion") or d.get("id"),
            "postid": d.get("id"),
            "subject": m.plain(d.get("subject") or d.get("name"), lg),
            "message": clean(d.get("message"), lg, tok),
            "author": d.get("userfullname") or "",
            "avatar": avatar(d.get("userpictureurl"), tok),
            "created": d.get("created") or d.get("timemodified"),
            "modified": d.get("timemodified") or d.get("modified"),
            "replies": d.get("numreplies") or 0,
            "unread": d.get("numunread") or 0,
            "pinned": bool(d.get("pinned")),
            "locked": bool(d.get("locked")),
            "can_reply": bool(d.get("canreply", True)),
            "can_lock": bool(d.get("canlock")),
        }

    async def discussions_of(sess: Session, forumid: int, lg: str, page: int = 0, perpage: int = 50) -> list[dict]:
        data = await call(sess, "mod_forum_get_forum_discussions", lg, forumid=forumid, sortorder=-1, page=page, perpage=perpage)
        return [discussion_row(d, lg, sess.moodle_token) for d in data.get("discussions") or []]

    # --- announcements ---------------------------------------------------------------------------

    @app.get("/api/v1/courses/{courseid}/announcements")
    async def announcements(courseid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        news = next((f for f in await forums(sess, courseid, lg) if f.get("type") == "news"), None)
        if not news:
            return {"forum": None, "items": [], "can_post": False}
        items = await discussions_of(sess, int(news["id"]), lg)
        return {"forum": int(news["id"]), "items": items, "can_post": bool(news.get("cancreatediscussions"))}

    @app.post("/api/v1/courses/{courseid}/announcements")
    async def post_announcement(courseid: int, body: PostIn, sess: Annotated[Session, Depends(current)]):
        news = next((f for f in await forums(sess, courseid, None) if f.get("type") == "news"), None)
        if not news:
            raise EngineError("not_found", "this course has no announcements forum", 404)
        if not body.subject.strip():
            raise EngineError("subject_required", "an announcement needs a title", 400)
        r = await call(sess, "mod_forum_add_discussion", None, forumid=int(news["id"]), subject=body.subject.strip(),
                       message=text_html(body.message))
        return {"id": r.get("discussionid")}

    # --- discussions -----------------------------------------------------------------------------

    @app.get("/api/v1/courses/{courseid}/forums")
    async def course_forums(courseid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        out = []
        for f in await forums(sess, courseid, lg):
            if f.get("type") == "news":
                continue
            out.append({"id": int(f["id"]), "cmid": f.get("cmid"), "name": m.plain(f.get("name"), lg),
                        "intro": clean(f.get("intro"), lg, sess.moodle_token), "type": f.get("type"),
                        "discussions": f.get("numdiscussions"), "unread": f.get("unreadpostscount") or 0,
                        "can_post": bool(f.get("cancreatediscussions"))})
        return {"forums": out}

    @app.get("/api/v1/forums/{forumid}/discussions")
    async def forum_discussions(forumid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None, page: int = 0):
        lg = m.lang_of(lang, sess)
        info = await call(sess, "mod_forum_get_forum_access_information", lg, forumid=forumid)
        items = await discussions_of(sess, forumid, lg, page)
        caps = {k: bool(v) for k, v in (info or {}).items() if k.startswith("can")}
        return {"items": items, "can_post": caps.get("canstartdiscussion", False),
                "can_pin": caps.get("canpindiscussions", False), "page": page}

    @app.post("/api/v1/forums/{forumid}/discussions")
    async def new_discussion(forumid: int, body: PostIn, sess: Annotated[Session, Depends(current)]):
        if not body.subject.strip():
            raise EngineError("subject_required", "a topic needs a title", 400)
        r = await call(sess, "mod_forum_add_discussion", None, forumid=forumid, subject=body.subject.strip(),
                       message=text_html(body.message))
        return {"id": r.get("discussionid")}

    @app.get("/api/v1/discussions/{discussionid}")
    async def discussion(discussionid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        tok = sess.moodle_token
        data = await call(sess, "mod_forum_get_discussion_posts", lg, discussionid=discussionid,
                          sortby="created", sortdirection="ASC")
        posts = []
        for p in data.get("posts") or []:
            a = p.get("author") or {}
            caps = p.get("capabilities") or {}
            posts.append({
                "id": p["id"], "parent": p.get("parentid") or 0, "subject": m.plain(p.get("subject"), lg),
                "message": "" if p.get("isdeleted") else clean(p.get("message"), lg, tok),
                "author": a.get("fullname") or "", "author_id": a.get("id"),
                "avatar": avatar((a.get("urls") or {}).get("profileimage"), tok),
                "time": p.get("timecreated"), "unread": bool(p.get("unread")), "deleted": bool(p.get("isdeleted")),
                "can_reply": bool(caps.get("reply")), "can_edit": bool(caps.get("edit")), "can_delete": bool(caps.get("delete")),
                "attachments": [{"name": f.get("filename"), "url": m.sign_file(tok)(f["fileurl"])}
                                for f in p.get("attachments") or [] if f.get("fileurl")],
            })
        try:
            await call(sess, "mod_forum_view_forum_discussion", None, discussionid=discussionid)
        except EngineError:
            pass  # logging a view never blocks reading
        first = posts[0] if posts else None
        return {"id": discussionid, "forum": data.get("forumid"), "course": data.get("courseid"),
                "subject": first["subject"] if first else "", "posts": posts}

    @app.post("/api/v1/posts/{postid}/reply")
    async def reply(postid: int, body: ReplyIn, sess: Annotated[Session, Depends(current)]):
        parent = await call(sess, "mod_forum_get_discussion_post", None, postid=postid)
        subj = (parent.get("post") or {}).get("replysubject") or "Re"
        r = await call(sess, "mod_forum_add_discussion_post", None, postid=postid, subject=subj, message=text_html(body.message))
        return {"id": r.get("postid")}

    @app.put("/api/v1/posts/{postid}")
    async def edit_post(postid: int, body: PostIn, sess: Annotated[Session, Depends(current)]):
        params: dict[str, Any] = {"postid": postid, "message": text_html(body.message)}
        if body.subject.strip():
            params["subject"] = body.subject.strip()
        await call(sess, "mod_forum_update_discussion_post", None, **params)
        return {"ok": True}

    @app.delete("/api/v1/posts/{postid}")
    async def delete_post(postid: int, sess: Annotated[Session, Depends(current)]):
        await call(sess, "mod_forum_delete_post", None, postid=postid)
        return {"ok": True}

    @app.put("/api/v1/discussions/{discussionid}/pin")
    async def pin(discussionid: int, body: StateIn, sess: Annotated[Session, Depends(current)]):
        await call(sess, "mod_forum_set_pin_state", None, discussionid=discussionid, targetstate=1 if body.on else 0)
        return {"ok": True}

    @app.put("/api/v1/discussions/{discussionid}/lock")
    async def lock(discussionid: int, body: StateIn, sess: Annotated[Session, Depends(current)]):
        d = await call(sess, "mod_forum_get_discussion_posts", None, discussionid=discussionid)
        await call(sess, "mod_forum_set_lock_state", None, forumid=int(d.get("forumid")), discussionid=discussionid,
                   targetstate=0 if body.on else 1)  # Moodle: 0 locks now, a non-zero state unlocks
        return {"ok": True}

    # --- online class sessions ---------------------------------------------------------------------

    @app.get("/api/v1/courses/{courseid}/meetings")
    async def meetings(courseid: int, sess: Annotated[Session, Depends(current)]):
        data = await call(sess, "local_wenquest_get_meetings", None, courseid=courseid)
        return {"meetings": data.get("meetings") or [], "can_manage": bool(data.get("canmanage"))}

    def meeting_params(body: MeetingIn) -> dict:
        url = body.url.strip()
        if url and not re.match(r"^https?://", url):
            url = "https://" + url
        if not url and not body.meetingcode.strip():
            raise EngineError("meeting_link_required", "a join link or a meeting number is required", 400)
        return {"name": body.name.strip(), "provider": body.provider, "url": url, "meetingcode": body.meetingcode.strip(),
                "passcode": body.passcode.strip(), "notes": body.notes.strip(), "timestart": body.timestart,
                "duration": body.duration}

    @app.post("/api/v1/courses/{courseid}/meetings")
    async def add_meeting(courseid: int, body: MeetingIn, sess: Annotated[Session, Depends(current)]):
        return await call(sess, "local_wenquest_save_meeting", None, courseid=courseid, id=0, **meeting_params(body))

    @app.put("/api/v1/courses/{courseid}/meetings/{mid}")
    async def edit_meeting(courseid: int, mid: int, body: MeetingIn, sess: Annotated[Session, Depends(current)]):
        return await call(sess, "local_wenquest_save_meeting", None, courseid=courseid, id=mid, **meeting_params(body))

    @app.delete("/api/v1/courses/{courseid}/meetings/{mid}")
    async def delete_meeting(courseid: int, mid: int, sess: Annotated[Session, Depends(current)]):
        await call(sess, "local_wenquest_delete_meeting", None, courseid=courseid, id=mid)
        return {"ok": True}

    # --- people and groups -----------------------------------------------------------------------

    async def people_data(sess: Session, courseid: int, lg: str) -> dict:
        tok = sess.moodle_token
        users = await call(sess, "core_enrol_get_enrolled_users", lg, courseid=courseid, options=[
            {"name": "userfields", "value": "id,fullname,email,profileimageurl,roles,groups,lastcourseaccess"}])
        members, seen_groups = [], {}
        for u in users:
            for g in u.get("groups") or []:
                seen_groups.setdefault(g["id"], g.get("name") or "")
            roles = [r.get("shortname") for r in u.get("roles") or []]
            role = ("teacher" if {"editingteacher", "manager"} & set(roles) else
                    "assistant" if "teacher" in roles else "student" if "student" in roles or not roles else roles[0])
            members.append({"id": u["id"], "fullname": u.get("fullname") or "", "email": u.get("email") or "",
                            "avatar": avatar(u.get("profileimageurl"), tok), "role": role,
                            "groups": [g["id"] for g in u.get("groups") or []],
                            "lastaccess": u.get("lastcourseaccess") or 0})
        order = {"teacher": 0, "assistant": 1, "student": 2}
        members.sort(key=lambda x: (order.get(x["role"], 3), x["fullname"]))
        try:
            groups = await call(sess, "core_group_get_course_groups", lg, courseid=courseid)
        except EngineError:  # students may not list groups; they see the groups people belong to
            groups = [{"id": gid, "name": name} for gid, name in sorted(seen_groups.items())]
        gl = [{"id": g["id"], "name": m.plain(g.get("name"), lg),
               "members": [u["id"] for u in members if g["id"] in u["groups"]]} for g in groups]
        return {"members": members, "groups": gl}

    @app.get("/api/v1/courses/{courseid}/people")
    async def people(courseid: int, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        lg = m.lang_of(lang, sess)
        data = await people_data(sess, courseid, lg)
        teacher = await is_teacher(sess, courseid)
        if not teacher:  # students see names and groups, not addresses or activity
            for u in data["members"]:
                u["email"] = ""
                u["lastaccess"] = 0
        return {**data, "can_manage": teacher}

    @app.post("/api/v1/courses/{courseid}/people")
    async def enrol(courseid: int, body: EnrolIn, sess: Annotated[Session, Depends(current)]):
        ids = [x.strip() for x in body.identifiers if x.strip()]
        r = await call(sess, "local_wenquest_manage_members", None, courseid=courseid, action="enrol",
                       identifiers=ids, role=body.role)
        return {"added": r.get("added") or [], "already": r.get("already") or [], "notfound": r.get("notfound") or []}

    @app.delete("/api/v1/courses/{courseid}/people/{userid}")
    async def unenrol(courseid: int, userid: int, sess: Annotated[Session, Depends(current)]):
        r = await call(sess, "local_wenquest_manage_members", None, courseid=courseid, action="unenrol", userid=userid)
        if not r.get("removed"):
            raise EngineError("not_removable", "this person was not added by hand and cannot be removed here", 409)
        return {"ok": True}

    async def groups_call(sess: Session, courseid: int, **params: Any) -> dict:
        r = await call(sess, "local_wenquest_manage_groups", None, courseid=courseid, **params)
        return {"groups": r.get("groups") or [], "skipped": r.get("skipped") or []}

    @app.post("/api/v1/courses/{courseid}/groups")
    async def add_group(courseid: int, body: GroupIn, sess: Annotated[Session, Depends(current)]):
        if not body.name.strip():
            raise EngineError("name_required", "a group needs a name", 400)
        return await groups_call(sess, courseid, action="create", name=body.name.strip(), userids=body.members or [])

    @app.put("/api/v1/courses/{courseid}/groups/{gid}")
    async def edit_group(courseid: int, gid: int, body: GroupIn, sess: Annotated[Session, Depends(current)]):
        out: dict = {}
        if body.name.strip():
            out = await groups_call(sess, courseid, action="rename", groupid=gid, name=body.name.strip())
        if body.members is not None:
            out = await groups_call(sess, courseid, action="setmembers", groupid=gid, userids=body.members)
        return out

    @app.delete("/api/v1/courses/{courseid}/groups/{gid}")
    async def delete_group(courseid: int, gid: int, sess: Annotated[Session, Depends(current)]):
        return await groups_call(sess, courseid, action="delete", groupid=gid)

    @app.post("/api/v1/courses/{courseid}/groups/apply")
    async def apply_plan(courseid: int, body: PlanIn, sess: Annotated[Session, Depends(current)]):
        plan = [{"name": g.name, "userids": g.members} for g in body.groups]
        return await groups_call(sess, courseid, action="applyplan", plan=plan, replace=body.replace)

    @app.post("/api/v1/courses/{courseid}/groups/ai")
    async def ai_groups(courseid: int, body: AiGroupsIn, sess: Annotated[Session, Depends(current)], lang: str | None = None):
        """A grouping plan from the teacher's request; nothing changes until the teacher applies it."""
        if not await is_teacher(sess, courseid):
            raise EngineError("forbidden", "only teachers group students", 403)
        lg = m.lang_of(lang, sess)
        data = await people_data(sess, courseid, lg)
        students = [u for u in data["members"] if u["role"] == "student"]
        if len(students) < 2:
            raise EngineError("too_few_students", "at least two students are needed", 400)
        grades: dict[int, float] = {}
        try:
            g = await call(sess, "gradereport_user_get_grade_items", None, courseid=courseid, userid=0)
            for ug in g.get("usergrades") or []:
                total = next((i for i in ug.get("gradeitems") or [] if i.get("itemtype") == "course"), None)
                if total and total.get("graderaw") is not None:
                    grades[int(ug["userid"])] = float(total["graderaw"])
        except EngineError:
            pass
        roster = [{"id": u["id"], "name": u["fullname"], "grade": grades.get(u["id"]),
                   "current_groups": [x["name"] for x in data["groups"] if u["id"] in x["members"]]} for u in students]
        want = re.search(r"(\d+)\s*(人|个人|名|people|students)", body.request)
        size = int(want.group(1)) if want else 4
        schema = {"type": "object", "properties": {
            "explanation": {"type": "string"},
            "groups": {"type": "array", "items": {"type": "object", "properties": {
                "name": {"type": "string"}, "members": {"type": "array", "items": {"type": "integer"}},
                "note": {"type": "string"}}, "required": ["name", "members", "note"], "additionalProperties": False}}},
            "required": ["explanation", "groups"], "additionalProperties": False}
        prompt = (f"Teacher's request: {body.request or '（没有特别要求）'}\n\nStudents ({len(roster)}):\n"
                  + json.dumps(roster, ensure_ascii=False))
        out = await state.ai.json(system=GROUPING, prompt=prompt, schema=schema, max_tokens=6000,
                                  fake=lambda: {"explanation": f"按成绩蛇形排列，每组约 {size} 人，各组水平接近。",
                                                "groups": balanced_groups(roster, size)})
        plan = validate_plan((out or {}).get("groups") or [], [u["id"] for u in students])
        names = {u["id"]: u["fullname"] for u in students}
        for g in plan:
            g["names"] = [names[i] for i in g["members"]]
        return {"explanation": str((out or {}).get("explanation") or "")[:600], "groups": plan,
                "has_grades": bool(grades), "existing": len(data["groups"])}
