"""Publish a course pack (第 16 轮): a course built from a web-edition textbook, published without the studio.

CI renders <textbook_dir>/<book>/course/manifest.json and its files (textbook/web-editions/<book>/course/tools/
build_course.py). An administrator presses “发布” on the admin page: the gateway creates the course the first time,
publishes every lesson of the chosen batches that is not published yet (in order, activity by activity, so a retry
after a failure continues where it stopped), adds the exams, and lists the course in the catalogue as free.
Progress lives in <data_dir>/course-packs/<book>.json.
"""

import asyncio
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends
from pydantic import BaseModel, Field

from . import course_builder as cb
from .moodle import EngineError
from .session import Session


class PublishIn(BaseModel):
    batch: int = Field(ge=1, le=20)


def ml(p: list[str] | None, is_html: bool = False) -> str:
    """A [zh, en] pair -> Moodle multilang text (one language as is; the same text twice stays plain)."""
    zh, en = (p or ["", ""])[:2]
    if zh.strip() == en.strip():
        return zh.strip()
    return cb.ml(cb.Text(zh=zh, en=en), "both", is_html)


def register(app, m) -> None:
    state = m.state
    running: dict[str, asyncio.Task] = {}

    def packs_dir() -> Path:
        return Path(state.settings.textbook_dir)

    def manifest_path(book: str) -> Path:
        return packs_dir() / book / "course" / "manifest.json"

    def state_path(book: str) -> Path:
        d = Path(state.settings.data_dir) / "course-packs"
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{book}.json"

    def load_manifest(book: str) -> dict:
        p = manifest_path(book)
        if "/" in book or ".." in book or not p.is_file():
            raise EngineError("not_found", "no such course pack", 404)
        return json.loads(p.read_text(encoding="utf-8"))

    def load_state(book: str) -> dict:
        p = state_path(book)
        st = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        st.setdefault("courseid", 0)
        st.setdefault("lessons", {})
        st.setdefault("exams", {})
        st.setdefault("status", "idle")
        st.setdefault("error", "")
        st.setdefault("progress", {"done": 0, "total": 0, "current": ""})
        return st

    def save_state(book: str, st: dict) -> None:
        st["updated"] = int(time.time())
        p = state_path(book)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
        tmp.replace(p)

    def lesson_done(st: dict, les: dict) -> bool:
        x = st["lessons"].get(str(les["no"]))
        return bool(x) and x.get("done", 0) >= len(les["activities"])

    def view(book: str, man: dict, st: dict, lang: str) -> dict:
        i = 0 if lang == "zh" else 1
        by_no = {x["no"]: x for x in man["lessons"]}
        batches = []
        for b in man["batches"]:
            done = sum(1 for n in b["lessons"] if n in by_no and lesson_done(st, by_no[n]))
            exams_done = sum(1 for e in b["exams"] if st["exams"].get(e))
            batches.append({"no": b["no"], "name": b["name"][i], "lessons": len(b["lessons"]), "published": done,
                            "exams": len(b["exams"]), "exams_published": exams_done,
                            "done": done == len(b["lessons"]) and exams_done == len(b["exams"])})
        status = "running" if book in running and not running[book].done() else st["status"]
        if status == "running" and book not in running:
            status = "failed"   # the gateway restarted mid-way: press again to continue
        return {"book": book, "title": man["course"]["fullname"][i], "version": man.get("version", ""),
                "courseid": st["courseid"], "status": status, "error": st["error"], "progress": st["progress"],
                "batches": batches, "updated": st.get("updated", 0), "stale": len(stale(book, man, st)), "skipped": st.get("skipped", 0)}

    async def call(sess: Session, fn: str, **kw: Any) -> dict:
        return await state.moodle.call(sess.moodle_token, fn, None, **kw)

    async def upload_files(sess: Session, base: Path, rels: list[str]) -> int:
        draft = 0
        for rel in rels:
            p = (base / rel).resolve()
            if not p.is_relative_to(base.resolve()) or not p.is_file():
                raise EngineError("pack_file_missing", rel, 500)
            draft = await state.moodle.upload(sess.moodle_token, p.name, p.read_bytes(), draft)
        return draft

    async def activity(sess: Session, base: Path, a: dict) -> dict:
        t = a["type"]
        out: dict[str, Any] = {"type": t, "name": ml(a["name"])[:250], "visible": int(a.get("visible", 1))}
        if t == "page":
            out["content"] = ml(a["content"], True)
            if a.get("files"):
                out["draftitemid"] = await upload_files(sess, base, a["files"])
        elif t == "resource":
            out["draftitemid"] = await upload_files(sess, base, [a["file"]])
        elif t in ("assign", "forum"):
            out["intro"] = ml(a.get("intro"), True)
            if t == "assign":
                out["grade"] = a.get("grade", 100)
        else:
            raise EngineError("pack_invalid", f"activity type {t}", 500)
        return out

    def quiz_payload(q: dict, courseid: int, section: int) -> dict:
        qs = []
        for x in q["questions"]:
            qs.append({"type": x["type"], "text": ml(x["text"], True), "feedback": ml(x["feedback"], True),
                       "mark": x.get("mark", 1), "correct": bool(x.get("correct", True)),
                       "answers": [{"text": ml(a["text"], True) if x["type"] in ("single", "multiple") else a["text"][0],
                                    "fraction": a.get("fraction", 0), "feedback": "", "tolerance": a.get("tolerance", 0)}
                                   for a in x.get("answers") or []]})
        return {"courseid": courseid, "cmid": 0, "section": section, "name": ml(q["name"])[:250], "intro": ml(q.get("intro"), True),
                "timeopen": 0, "timeclose": 0, "timelimit": q.get("timelimit", 0), "attempts": q.get("attempts", 1),
                "grade": q.get("grade", 100), "showanswers": q.get("showanswers", "immediately"),
                "visible": int(q.get("visible", 1)), "questions": qs}

    async def create_course(sess: Session, base: Path, man: dict, st: dict, book: str) -> None:
        c = man["course"]
        acts = [await activity(sess, base, a) for a in c["info"]["activities"]]
        res = await call(sess, "local_wenquest_create_course", fullname=ml(c["fullname"]), shortname=c["shortname"],
                         summary=ml(c["summary"], True),
                         sections=[{"name": ml(c["info"]["name"]), "summary": "", "activities": acts}])
        st["courseid"] = int(res["courseid"])
        st["shortname"] = res.get("shortname", "")
        save_state(book, st)
        state.accounts.run(
            "INSERT INTO catalog (courseid, mode, price, currency, blurb, updated, updated_by) VALUES (?, 'free', 0, 'CNY', ?, ?, ?) "
            "ON CONFLICT(courseid) DO UPDATE SET mode = 'free', blurb = excluded.blurb, updated = excluded.updated, "
            "updated_by = excluded.updated_by", st["courseid"], c.get("blurb", ""), time.time(), sess.user_id)

    async def publish_activities(sess: Session, base: Path, st: dict, book: str, key: str, courseid: int, section: int,
                                 sectionname: str, summary: str, acts: list[dict]) -> None:
        """Publish acts[done:] into the section, saving progress after each step. Quizzes go through their own call;
        the other activities in runs, so their order in the section is the order in the manifest."""
        rec = st["lessons"].setdefault(key, {"done": 0, "cmids": []})
        named = rec["done"] > 0
        i = rec["done"]
        while i < len(acts):
            a = acts[i]
            st["progress"]["current"] = ml(a["name"])
            if a["type"] == "quiz":
                if not named:
                    await call(sess, "local_wenquest_add_activities", courseid=courseid, section=section, sectionname=sectionname,
                               sectionsummary=summary, activities=[])
                    named = True
                r = await call(sess, "local_wenquest_create_quiz", **quiz_payload(a, courseid, section))
                rec["cmids"].append(int(r.get("cmid", 0)))
                i += 1
            else:
                j = i
                group = []
                while j < len(acts) and acts[j]["type"] != "quiz" and len(group) < 6:
                    group.append(await activity(sess, base, acts[j]))
                    j += 1
                r = await call(sess, "local_wenquest_add_activities", courseid=courseid, section=section,
                               sectionname="" if named else sectionname, sectionsummary="" if named else summary, activities=group)
                named = True
                cmids = [int(x) for x in r.get("cmids") or []]
                rec["cmids"] += cmids
                for a2, cmid in zip(acts[i:j], cmids):
                    if a2["type"] == "resource" and cmid:
                        st.setdefault("files", {})[str(cmid)] = file_hash(base, a2["file"])
                for a2, cmid in zip(acts[i:j], cmids):
                    if a2["type"] == "assign" and cmid:
                        try:
                            await call(sess, "local_wenquest_edit_course", courseid=courseid, action="content", cmid=cmid,
                                       allowtext=1, allowfiles=1, maxfiles=10)
                        except EngineError:
                            pass   # the defaults still accept submissions
                i = j
            rec["done"] = i
            rec["at"] = int(time.time())
            save_state(book, st)

    def file_hash(base: Path, rel: str) -> str:
        p = (base / rel).resolve()
        return hashlib.sha1(p.read_bytes()).hexdigest() if p.is_file() else ""

    def stale(book: str, man: dict, st: dict) -> list[tuple[str, int, dict]]:
        """Published file activities whose file in the current pack differs from what was uploaded (第 24 轮：
        课件由 PPT 换成网页互动课件，以后改了课件、实验页也走这里)。Matched by position: a lesson's cmids are recorded
        in the order of its activities. Older records without a hash count as changed once."""
        base = manifest_path(book).parent
        known = st.get("files", {})
        out = []
        for les in man["lessons"]:
            rec = st["lessons"].get(str(les["no"]))
            if not rec or not lesson_done(st, les):
                continue
            for a, cmid in zip(les["activities"], rec.get("cmids") or []):
                if a["type"] == "resource" and cmid and known.get(str(cmid)) != file_hash(base, a["file"]):
                    out.append((str(les["no"]), int(cmid), a))
        return out

    def norm(t: str) -> str:
        """A Moodle activity name as plain text: multilang spans keep the Chinese one, tags and spaces dropped."""
        m_ = re.search(r'<span[^>]*lang="zh[^"]*"[^>]*>(.*?)</span>', t or "", re.S)
        t = m_.group(1) if m_ else (t or "")
        return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", t))

    def stem(t: str) -> str:
        return re.split(r"[（(]", t, 1)[0]

    def match(a: dict, cmid: int, names: dict[int, str], sec: list[tuple[int, str]], res: list[dict]) -> int:
        """The live file activity for manifest activity a: same name, else the one name before the bracket."""
        want = {norm(a["name"][0]), norm(a["name"][1]), norm(ml(a["name"]))}
        if names.get(cmid) in want:
            return cmid
        hit = [i for i, n in sec if n in want]
        if len(hit) == 1:
            return hit[0]
        st_ = stem(norm(a["name"][0]))
        if sum(stem(norm(x["name"][0])) == st_ for x in res) == 1:
            hit = [i for i, n in sec if stem(n) == st_]
            if len(hit) == 1:
                return hit[0]
        return 0

    async def refresh_work(sess: Session, book: str) -> None:
        man = load_manifest(book)
        st = load_state(book)
        base = manifest_path(book).parent
        try:
            todo = stale(book, man, st)
            st["progress"] = {"done": 0, "total": len(todo), "current": ""}
            save_state(book, st)
            # The recorded cmids follow the manifest's activity order at publishing time; if the pack gained or lost
            # activities since then, a position points at the wrong activity. So each file is matched to the live
            # course by name within its section (the recorded cmid is used only when its name agrees), and a file
            # that cannot be matched is left alone and counted instead of stopping the whole update.
            live: dict[int, list[tuple[int, str]]] = {}
            names: dict[int, str] = {}
            try:
                for sec in await state.moodle.call(sess.moodle_token, "core_course_get_contents", None, courseid=st["courseid"]) or []:
                    for mo in sec.get("modules") or []:
                        if mo.get("modname") == "resource":
                            nm = norm(mo.get("name", ""))
                            live.setdefault(int(sec.get("section", -1)), []).append((int(mo["id"]), nm))
                            names[int(mo["id"])] = nm
            except Exception:  # noqa: BLE001 - without the listing, trust the record
                live = {}
            lessons = {str(x["no"]): x for x in man["lessons"]}
            skipped = 0
            for no, cmid, a in todo:
                st["progress"]["current"] = ml(a["name"])
                try:
                    if live:
                        les = lessons[no]
                        found = match(a, cmid, names, live.get(int(les["section"]), []),
                                      [x for x in les["activities"] if x["type"] == "resource"])
                        if not found:
                            skipped += 1
                            continue
                        if found != cmid:
                            st["lessons"][no]["cmids"][les["activities"].index(a)] = cmid = found
                    draft = await upload_files(sess, base, [a["file"]])
                    await call(sess, "local_wenquest_edit_course", courseid=st["courseid"], action="replacefile", cmid=cmid, draftitemid=draft)
                    await call(sess, "local_wenquest_edit_course", courseid=st["courseid"], action="module", cmid=cmid, name=ml(a["name"])[:250])
                    st.setdefault("files", {})[str(cmid)] = file_hash(base, a["file"])
                    names[cmid] = norm(ml(a["name"]))
                    st["progress"]["done"] += 1
                except EngineError:
                    skipped += 1
                save_state(book, st)
            st["skipped"] = skipped
            st.update(status="done", error="")
            st["progress"]["current"] = ""
        except Exception as exc:  # noqa: BLE001 - the administrator sees the reason and presses again
            st.update(status="failed", error=(getattr(exc, "message", "") or str(exc))[:400])
        save_state(book, st)

    async def work(sess: Session, book: str, batch: int) -> None:
        man = load_manifest(book)
        st = load_state(book)
        base = manifest_path(book).parent
        try:
            chosen = [b for b in man["batches"] if b["no"] <= batch]
            nos = {n for b in chosen for n in b["lessons"]}
            lessons = [x for x in man["lessons"] if x["no"] in nos and not lesson_done(st, x)]
            exams = [e for e in man["exams"] if any(e["id"] in b["exams"] for b in chosen) and not st["exams"].get(e["id"])]
            st["progress"] = {"done": 0, "total": len(lessons) + len(exams), "current": ""}
            save_state(book, st)
            if not st["courseid"]:
                await create_course(sess, base, man, st, book)
            cid = st["courseid"]
            for les in lessons:
                await publish_activities(sess, base, st, book, str(les["no"]), cid, les["section"], ml(les["name"]),
                                         ml(les["summary"], True), les["activities"])
                st["progress"]["done"] += 1
                save_state(book, st)
            for e in exams:
                sec = man["exam_section"]
                key = f"exam-{e['id']}"
                await publish_activities(sess, base, st, book, key, cid, sec["section"], ml(sec["name"]), "", [e])
                st["exams"][e["id"]] = st["lessons"][key]["cmids"][-1]
                st["progress"]["done"] += 1
                save_state(book, st)
            st.update(status="done", error="")
            st["progress"]["current"] = ""
        except Exception as exc:  # noqa: BLE001 - the administrator sees the reason and presses again
            st.update(status="failed", error=(getattr(exc, "message", "") or str(exc))[:400])
        save_state(book, st)

    @app.get("/api/v1/admin/course-packs")
    async def list_packs(sess: Annotated[Session, Depends(m.current)], lang: str | None = None):
        await m.accounts_require_admin(sess)
        lg = m.lang_of(lang, sess)
        out = []
        root = packs_dir()
        for p in sorted(root.glob("*/course/manifest.json")) if root.is_dir() else []:
            book = p.parent.parent.name
            try:
                out.append(view(book, load_manifest(book), load_state(book), lg))
            except (ValueError, KeyError):
                continue
        return {"packs": out}

    @app.post("/api/v1/admin/course-packs/{book}/refresh")
    async def refresh(book: str, sess: Annotated[Session, Depends(m.current)], lang: str | None = None):
        """Replace the files of already published lessons that changed in the pack (same activity, new file and name)."""
        await m.accounts_require_admin(sess)
        man = load_manifest(book)
        if book in running and not running[book].done():
            raise EngineError("busy", "already publishing", 409)
        st = load_state(book)
        st.update(status="running", error="")
        save_state(book, st)
        running[book] = asyncio.create_task(refresh_work(sess, book))
        await asyncio.sleep(0)
        return view(book, man, load_state(book), m.lang_of(lang, sess))

    @app.post("/api/v1/admin/course-packs/{book}/publish")
    async def publish(book: str, body: PublishIn, sess: Annotated[Session, Depends(m.current)], lang: str | None = None):
        await m.accounts_require_admin(sess)
        man = load_manifest(book)
        if not any(b["no"] == body.batch for b in man["batches"]):
            raise EngineError("not_found", "no such batch", 404)
        if book in running and not running[book].done():
            raise EngineError("busy", "already publishing", 409)
        st = load_state(book)
        st.update(status="running", error="")
        save_state(book, st)
        running[book] = asyncio.create_task(work(sess, book, body.batch))
        await asyncio.sleep(0)
        return view(book, man, load_state(book), m.lang_of(lang, sess))
