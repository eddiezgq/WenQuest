"""A course's life after teaching (round 3): take down (下架) / reopen, delete into the recycle bin, restore, delete
for good, and download — a Moodle backup (.mbz) or a zip of the course's own files, chapter by chapter.

Moodle does the work (local_wenquest_course_life, on Moodle's own category recycle bin) with each user's own token;
only a course's teachers and site admins may do any of it. The AI course projects (AI 建课) follow their course:
kept when it is taken down or deleted, reconnected when it is restored, and deleted with it only if asked.

Downloads are made in the background into the data folder (exports/<user>/), announced by email when mail is set
up, and fetched through a signed link valid for a day; files older than three days are cleared.
"""

import asyncio
import html
import json
import re
import secrets
import shutil
import time
import zipfile
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .moodle import EngineError
from .session import Session

LINK_TTL = 24 * 3600
KEEP = 3 * 24 * 3600


class ExportIn(BaseModel):
    kind: str = Field(pattern="^(backup|files)$")


class PurgeIn(BaseModel):
    delete_project: bool = False


def safe(name: str, limit: int = 80) -> str:
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "-", str(name or "")).strip(" .")
    return (name or "untitled")[:limit]


def project_title(p: dict) -> str:
    from .studio import disp
    return disp((p.get("outline") or {}).get("title")) or (p.get("requirements") or {}).get("course_title") or "AI 建课项目"


def register(app, m) -> None:
    state = m.state
    running: dict[str, asyncio.Task] = {}

    async def call(sess: Session, action: str, **kw) -> dict:
        return await state.moodle.call(sess.moodle_token, "local_wenquest_course_life", None, action=action, **kw)

    async def need_teacher(sess: Session, courseid: int) -> None:
        try:
            ok = await state.moodle.can_edit_course(sess.moodle_token, courseid)
        except EngineError:
            ok = False
        if not ok:
            raise EngineError("forbidden", "only the course's teachers may do this", 403)

    def projects_of(courseid: int) -> list[dict]:
        return [p for p in m._studio().projects.all() if int((p.get("course") or {}).get("id") or 0) == courseid]

    # --- take down / reopen ----------------------------------------------------------------------

    async def set_visible(sess: Session, courseid: int, visible: bool) -> dict:
        await need_teacher(sess, courseid)
        await state.moodle.call(sess.moodle_token, "local_wenquest_edit_course", None, courseid=courseid, action="course",
                                visible=1 if visible else 0)
        return {"ok": True, "visible": visible}

    @app.post("/api/v1/courses/{courseid}/takedown")
    async def takedown(courseid: int, sess: Annotated[Session, Depends(m.current)]):
        """下架: students no longer see the course (dashboard, course list, catalogue); their work is kept."""
        return await set_visible(sess, courseid, False)

    @app.post("/api/v1/courses/{courseid}/reopen")
    async def reopen(courseid: int, sess: Annotated[Session, Depends(m.current)]):
        return await set_visible(sess, courseid, True)

    # --- delete / recycle bin --------------------------------------------------------------------

    @app.delete("/api/v1/courses/{courseid}")
    async def delete_course(courseid: int, sess: Annotated[Session, Depends(m.current)]):
        """Into the recycle bin (a full backup is kept); only a course that has been taken down."""
        r = await call(sess, "delete", courseid=courseid)
        st = m._studio()
        for p in projects_of(courseid):
            p["course"]["deleted"] = {"binid": r["binid"], "at": int(time.time())}
            st.say(p, "这门课已经删除，放进了回收站；AI 建课项目保留着。从回收站恢复课程后，这里会自动重新连上。", "system")
            st.projects.save(p)
        return {"ok": True, "binid": r["binid"]}

    @app.get("/api/v1/trash")
    async def trash(sess: Annotated[Session, Depends(m.current)]):
        items = (await call(sess, "list")).get("items") or []
        lg = m.lang_of(None, sess)
        for it in items:
            it["name"] = m.plain(it.pop("fullname", ""), lg)
            it["projects"] = [{"id": p["id"], "title": project_title(p)} for p in projects_of(int(it["oldcourseid"]))
                              if p.get("owner") == sess.user_id]
        return {"items": items}

    @app.post("/api/v1/trash/{binid}/restore")
    async def restore(binid: int, sess: Annotated[Session, Depends(m.current)]):
        """Back as a course that is taken down; its AI course project points at it again."""
        r = await call(sess, "restore", binid=binid)
        new, old = int(r["courseid"]), int(r["oldcourseid"])
        st = m._studio()
        secs = None
        for p in projects_of(old):
            p["course"]["id"] = new
            p["course"].pop("deleted", None)
            if p["course"].get("labs"):
                # Moodle numbered everything anew: find each chapter's lab page again (by chapter and name)
                if secs is None:
                    try:
                        secs = await state.moodle.course_contents(sess.moodle_token, new, None)
                    except EngineError:
                        secs = []
                by_no = {int(s.get("section") or 0): s for s in secs}
                labs = {}
                for chap_id in p["course"]["labs"]:
                    sec = by_no.get(int((p["course"].get("sections") or {}).get(chap_id) or -1))
                    mod = next((x for x in (sec or {}).get("modules") or []
                                if x.get("modname") == "resource" and re.search(r"虚拟实验|virtual lab", x.get("name") or "")), None)
                    if mod:
                        labs[chap_id] = int(mod["id"])
                p["course"]["labs"] = labs
            st.say(p, "课程已从回收站恢复（目前是下架状态，确认没问题后在课程页点“重新开课”），这个项目已重新连上。", "system")
            st.projects.save(p)
        # the catalogue listing follows the course to its new id
        try:
            state.accounts.run("UPDATE catalog SET courseid = ? WHERE courseid = ?", new, old)
        except Exception:
            pass
        return {"ok": True, "courseid": new}

    @app.delete("/api/v1/trash/{binid}")
    async def purge(binid: int, sess: Annotated[Session, Depends(m.current)], delete_project: bool = False):
        """永久删除. The AI course project is kept unless the teacher asks to delete it too."""
        r = await call(sess, "purge", binid=binid)
        st = m._studio()
        removed = []
        for p in projects_of(int(r["oldcourseid"])):
            if delete_project and p.get("owner") == sess.user_id:
                st.projects.remove(p["id"])
                removed.append(p["id"])
            else:
                p["course"] = {"id": 0, "shortname": "", "sections": {}, "attached": [], "purged": int(time.time())}
                for c in (p.get("outline") or {}).get("chapters", []):
                    for les in c["lessons"]:
                        if les.get("status") == "published":
                            les["status"] = "awaiting"   # its course is gone; it can be published into a new one
                            les["cmids"] = []
                st.say(p, "对应的课程已永久删除。项目和写好的课时都还在，可以重新发布成一门新课。", "system")
                st.projects.save(p)
        return {"ok": True, "deleted_projects": removed}

    # --- downloads -------------------------------------------------------------------------------

    def folder(uid: int) -> Path:
        d = Path(state.settings.data_dir) / "exports" / str(int(uid))
        d.mkdir(parents=True, exist_ok=True)
        return d

    def sweep(d: Path) -> None:
        for f in d.iterdir():
            if time.time() - f.stat().st_mtime > KEEP:
                f.unlink(missing_ok=True)

    def sign(uid: int, eid: str) -> str:
        tok = state.codec.fernet.encrypt(json.dumps({"u": uid, "e": eid}).encode()).decode()
        return f"{state.settings.public_url.rstrip('/')}/api/v1/exports/file/{tok}"

    def load(d: Path, eid: str) -> dict:
        return json.loads((d / f"{eid}.json").read_text())

    def save(d: Path, job: dict) -> None:
        tmp = d / f"{job['id']}.tmp"
        tmp.write_text(json.dumps(job, ensure_ascii=False))
        tmp.replace(d / f"{job['id']}.json")

    async def start(sess: Session, kind: str, name: str, *, courseid: int = 0, binid: int = 0) -> dict:
        d = folder(sess.user_id)
        sweep(d)
        eid = secrets.token_hex(8)
        job = {"id": eid, "kind": kind, "name": name, "courseid": courseid, "binid": binid, "status": "running",
               "file": "", "size": 0, "error": "", "created": int(time.time()), "done": 0}
        save(d, job)
        running[eid] = asyncio.create_task(work(sess, d, job))
        return view(sess.user_id, job)

    async def work(sess: Session, d: Path, job: dict) -> None:
        try:
            if job["kind"] == "backup":
                r = await call(sess, "binfile", binid=job["binid"]) if job["binid"] else \
                    await call(sess, "backup", courseid=job["courseid"])
                name = safe(job["name"]) + "-备份.mbz"
                await fetch(sess, r["fileurl"], d / f"{job['id']}.data")
            else:
                name = safe(job["name"]) + "-资料.zip"
                await pack(sess, job["courseid"], d / f"{job['id']}.data")
            job.update(status="done", file=name, size=(d / f"{job['id']}.data").stat().st_size, done=int(time.time()))
        except Exception as e:  # noqa: BLE001 - the teacher sees the reason
            job.update(status="failed", error=(getattr(e, "message", "") or str(e))[:300], done=int(time.time()))
            (d / f"{job['id']}.data").unlink(missing_ok=True)
        save(d, job)
        running.pop(job["id"], None)
        await tell(sess, job)

    async def tell(sess: Session, job: dict) -> None:
        if not state.mailer.configured or job["status"] != "done":
            return
        try:
            u = await state.moodle.call(sess.moodle_token, "core_user_get_users_by_field", None, field="id",
                                        values=[sess.user_id])
            to = (u or [{}])[0].get("email", "")
            if to:
                link = f"{state.settings.app_url.rstrip('/')}/#/pages/trash/trash"
                await state.mailer.send(to, f"问渠：《{job['name']}》可以下载了",
                                        f"你要的{('课程备份包' if job['kind'] == 'backup' else '资料压缩包')}已经打包好了，"
                                        f"请在 24 小时内到问渠“课程 → 回收站与下载”里下载：{link}")
        except Exception:
            pass

    async def fetch(sess: Session, url: str, dest: Path) -> None:
        """Stream a Moodle file to disk (backups can be large)."""
        mo = state.moodle
        if not url.startswith(mo.base + "/"):
            raise EngineError("forbidden", "foreign file url", 403)
        sep = "&" if "?" in url else "?"
        async with mo.http.stream("GET", f"{mo._url(url)}{sep}token={sess.moodle_token}", headers=mo.headers,
                                  timeout=None) as r:
            if r.status_code != 200 or "application/json" in r.headers.get("content-type", ""):
                raise EngineError("engine_error", f"download failed ({r.status_code})", 502)
            with dest.open("wb") as f:
                async for chunk in r.aiter_bytes(1 << 20):
                    f.write(chunk)

    async def pack(sess: Session, courseid: int, dest: Path) -> None:
        """资料压缩包: one folder per chapter with the course's files and pages, plus 课程目录.html."""
        lg = m.lang_of(None, sess)
        c = await state.moodle.course(sess.moodle_token, courseid, None) or {}
        secs = await state.moodle.course_contents(sess.moodle_token, courseid, None)
        tmp = dest.with_suffix(".parts")
        tmp.mkdir(exist_ok=True)
        index = [f"<h1>{html.escape(m.plain(c.get('fullname'), lg))}</h1>"]
        try:
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
                for s in secs:
                    title = m.plain(s.get("name"), lg) or f"#{s.get('section')}"
                    sdir = f"{int(s.get('section') or 0):02d} {safe(title, 60)}"
                    rows = []
                    for mod in s.get("modules") or []:
                        mname = m.plain(mod.get("name"), lg)
                        files = [f for f in mod.get("contents") or [] if f.get("type") == "file" and f.get("fileurl")]
                        if mod.get("modname") == "url":
                            u = next((f.get("fileurl") for f in mod.get("contents") or [] if f.get("type") == "url"), "")
                            rows.append(f'<li>{html.escape(mname)}：<a href="{html.escape(u)}">{html.escape(u)}</a></li>')
                            continue
                        links = []
                        for i, f in enumerate(files[:200]):
                            fname = safe(f.get("filename") or f"file{i}", 120)
                            if mod.get("modname") == "page" and fname == "index.html":
                                fname = safe(mname, 80) + ".html"
                            arc = f"{sdir}/{fname}"
                            if arc in z.namelist():
                                arc = f"{sdir}/{mod['id']}-{fname}"
                            part = tmp / "f"
                            try:
                                await fetch(sess, f["fileurl"], part)
                            except EngineError:
                                continue
                            z.write(part, arc)
                            part.unlink(missing_ok=True)
                            links.append(f'<a href="{html.escape(arc)}">{html.escape(fname)}</a>')
                        if links:
                            rows.append(f"<li>{html.escape(mname)}：{'、'.join(links)}</li>")
                        elif mod.get("modname") not in ("label",):
                            rows.append(f"<li>{html.escape(mname)}（{html.escape(mod.get('modname') or '')}，只能在平台上使用）</li>")
                    if rows:
                        index.append(f"<h2>{html.escape(title)}</h2><ul>{''.join(rows)}</ul>")
                z.writestr("课程目录.html", "<!doctype html><meta charset='utf-8'><title>课程目录</title>"
                           "<style>body{font:15px/1.7 sans-serif;max-width:860px;margin:24px auto;padding:0 16px}</style>"
                           + "".join(index))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def view(uid: int, job: dict) -> dict:
        out = {k: job[k] for k in ("id", "kind", "name", "courseid", "binid", "status", "file", "size", "error", "created")}
        if job["status"] == "running" and job["id"] not in running:
            out.update(status="failed", error="服务重启过，请重新下载")
        out["url"] = sign(uid, job["id"]) if job["status"] == "done" else ""
        return out

    @app.post("/api/v1/courses/{courseid}/exports")
    async def export_course(courseid: int, body: ExportIn, sess: Annotated[Session, Depends(m.current)]):
        await need_teacher(sess, courseid)
        c = await state.moodle.course(sess.moodle_token, courseid, None) or {}
        return await start(sess, body.kind, m.plain(c.get("fullname"), m.lang_of(None, sess)) or f"course-{courseid}",
                           courseid=courseid)

    @app.post("/api/v1/trash/{binid}/exports")
    async def export_bin(binid: int, sess: Annotated[Session, Depends(m.current)]):
        items = (await call(sess, "list")).get("items") or []
        it = next((x for x in items if int(x["binid"]) == binid), None)
        if not it:
            raise EngineError("not_found", "no such item in your recycle bin", 404)
        return await start(sess, "backup", m.plain(it["fullname"], m.lang_of(None, sess)), binid=binid)

    @app.get("/api/v1/exports")
    async def exports(sess: Annotated[Session, Depends(m.current)]):
        d = folder(sess.user_id)
        sweep(d)
        jobs = []
        for f in d.glob("*.json"):
            try:
                jobs.append(view(sess.user_id, json.loads(f.read_text())))
            except (OSError, ValueError):
                continue
        return {"exports": sorted(jobs, key=lambda j: -j["created"])}

    @app.get("/api/v1/exports/file/{signed}")
    async def export_file(signed: str):
        try:
            d = json.loads(state.codec.fernet.decrypt(signed.encode(), ttl=LINK_TTL))
            uid, eid = int(d["u"]), str(d["e"])
        except Exception:
            raise EngineError("link_expired", "download link expired", 410)
        if not re.fullmatch(r"[0-9a-f]{16}", eid):
            raise EngineError("not_found", "no such file", 404)
        folder_ = folder(uid)
        try:
            job = load(folder_, eid)
        except (OSError, ValueError):
            raise EngineError("not_found", "no such file", 404)
        path = folder_ / f"{eid}.data"
        if job["status"] != "done" or not path.exists():
            raise EngineError("not_found", "no such file", 404)
        return FileResponse(path, filename=job["file"], media_type="application/octet-stream",
                            headers={"Cache-Control": "private, no-store"})
