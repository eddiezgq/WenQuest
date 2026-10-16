"""白板课（第 35 轮第 3 步）：老师的白板课存在网关，后台全自动生成（AI 写讲稿或识别录音 → 配音 → AI 排画板），编辑器改，出 MP4。

一节课一个目录 <root>/<id>/：
  lesson.json   标题、来源、声音、讲稿分段 segments [{t0, t1, zh, en}]、画板 scene（Excalidraw）、动作 moves、状态 job/error、mp4
  narration.wav 配音或老师录音（16 kHz 单声道之外的原始质量）；narration.mp3 网页播放用
  uploads/      老师上传的视频片段（插进画板的框里）；_parts/ 上传中的分片
  白板课.mp4    出的视频

素材（画板里的框）：lab:<教材>/<章.节>、anim:<教材>/<动画名>（平台教材），lesson:<课程项目>/<课>/lab|animation（AI 建课），
upload:<文件名>（老师上传）。网页里用有时效的链接；出 MP4 时整页、整段视频嵌进录制页（录制服务不联网）。
"""
from __future__ import annotations

import asyncio
import base64
import html as _html
import json
import logging
import re
import secrets
import shutil
import subprocess
import time
import wave
from pathlib import Path
from typing import Any, Callable

from .production import voice as V
from .production.whiteboard import ai as wai
from .production.whiteboard import core
from .production.whiteboard import speech

log = logging.getLogger("wenquest.whiteboards")
GAP, HEAD, TAIL = 0.45, 0.8, 1.5          # seconds: between segments, before the first, after the last
CHUNK = 30.0       # seconds of video per recording request: ≤ 900 frames, well inside the recorder's 15 minutes even with a live lab
LABBOX = re.compile(r"<div class='wq-media-box wq-labbox' data-lab='(M?\d+)-(\d+)'>(.*?)</div>", re.S)
ANIMBOX = re.compile(r"<div class='wq-media-box' data-anim='(\w+)' data-hash='(\w+)'>(.*?)</div>", re.S)
VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v"}
AUDIO_EXT = {".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac", ".mp4", ".mov", ".webm", ".m4v", ".amr"}


def now() -> float:
    return round(time.time(), 3)


def label_of(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[【】\[\]]", " ", re.sub(r"<[^>]+>", "", text))).strip()


def silence(seconds: float, rate: int = 24000) -> bytes:
    import io
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\0\0" * int(seconds * rate))
    return b.getvalue()


def ffmpeg(*args: str, timeout: float = 1800) -> None:
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + (r.stderr or "")[-400:])


def bigrams(text: str) -> set[str]:
    t = re.sub(r"\s+", "", text.lower())
    return {t[i:i + 2] for i in range(len(t) - 1)}


class Whiteboards:
    """Storage and background work. `env` gives what the platform has: ai, voice_url, labcheck_url, textbook_dir,
    textbook_media(book) → folder of rendered textbook animations, studio (the AI course builder) — read each time,
    so tests and settings changes take effect."""

    def __init__(self, root: str | Path, env: Callable[[], dict]):
        self.root = Path(root)
        self.env = env
        self.tasks: dict[str, asyncio.Task] = {}
        self.render_lock = asyncio.Lock()
        self._catalog: dict[str, tuple[float, list[dict]]] = {}

    # ------------------------------------------------------------------ storage
    def dir(self, wid: str) -> Path:
        if not re.fullmatch(r"[a-z0-9]{8,24}", wid or ""):
            raise KeyError(wid)
        return self.root / wid

    def load(self, wid: str) -> dict:
        p = self.dir(wid) / "lesson.json"
        if not p.exists():
            raise KeyError(wid)
        L = json.loads(p.read_text(encoding="utf-8"))
        if L.get("job") and wid not in self.tasks:          # the server restarted while it was working
            L["job"], L["error"] = None, "服务器重启，这一步没有做完，请重试"
            if L.get("state") == "making":
                L["state"] = "failed"
            self.save(L)
        return L

    def save(self, L: dict) -> None:
        d = self.dir(L["id"])
        d.mkdir(parents=True, exist_ok=True)
        L["updated"] = now()
        tmp = d / "lesson.json.tmp"
        tmp.write_text(json.dumps(L, ensure_ascii=False), encoding="utf-8")
        tmp.replace(d / "lesson.json")

    def all(self, owner: int) -> list[dict]:
        out = []
        if not self.root.exists():
            return out
        for p in self.root.glob("*/lesson.json"):
            try:
                L = self.load(p.parent.name)
            except (KeyError, ValueError):
                continue
            if L.get("owner") == owner:
                out.append(L)
        return sorted(out, key=lambda x: -x.get("updated", 0))

    def new(self, owner: int, **kw: Any) -> dict:
        wid = secrets.token_hex(6)
        L = {"id": wid, "owner": owner, "created": now(), "title": {"zh": (kw.get("topic") or "白板课")[:40], "en": ""},
             "source": kw.get("source", "topic"), "topic": kw.get("topic", ""), "note": kw.get("note", ""),
             "minutes": kw.get("minutes", 6), "voice": kw.get("voice", "zm_yunjian"), "speed": kw.get("speed", 1.0),
             "course": kw.get("course"), "book": kw.get("book", ""), "segments": [], "duration": 0, "audio": "",
             "scene": None, "moves": [], "state": "making", "job": None, "error": "", "notes": [], "mp4": None}
        self.save(L)
        return L

    def remove(self, wid: str) -> None:
        t = self.tasks.pop(wid, None)
        if t:
            t.cancel()
        shutil.rmtree(self.dir(wid), ignore_errors=True)

    # ------------------------------------------------------------------ background jobs
    def busy(self, wid: str) -> bool:
        t = self.tasks.get(wid)
        return bool(t and not t.done())

    def run(self, L: dict, label: str, fn: Callable[[dict], Any]) -> None:
        wid = L["id"]
        L["job"], L["error"] = {"label": label, "progress": 0, "since": now()}, ""
        self.save(L)

        async def job():
            try:
                cur = self.load(wid)
                await fn(cur)
                cur["job"] = None
                if cur.get("state") == "making":
                    cur["state"] = "ready"
                self.save(cur)
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001 - shown to the teacher
                log.exception("whiteboard %s: %s failed", wid, label)
                try:
                    cur = json.loads((self.dir(wid) / "lesson.json").read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    return
                cur["job"], cur["error"] = None, f"{label}没有成功：{str(e)[:300]}"
                if cur.get("state") == "making":
                    cur["state"] = "failed"
                self.save(cur)
            finally:
                self.tasks.pop(wid, None)

        self.tasks[wid] = asyncio.get_event_loop().create_task(job())

    def step(self, L: dict, label: str, progress: int = 0) -> None:
        L["job"] = {"label": label, "progress": progress, "since": (L.get("job") or {}).get("since", now())}
        self.save(L)

    # ------------------------------------------------------------------ making a lesson
    async def make_from_topic(self, L: dict) -> None:
        env = self.env()
        self.step(L, "AI 正在写讲稿")
        script = await wai.write_script(env["ai"], L["topic"], L.get("note", ""), L.get("minutes", 6), self.course_name(L))
        L["title"], L["segments"] = script["title"], script["segments"]
        self.save(L)
        await self.voice(L)
        await self.lay_out(L)

    async def make_from_recording(self, L: dict, src: Path) -> None:
        self.step(L, "正在识别录音")
        await self.take_recording(L, src)
        self.step(L, "AI 正在校对讲稿")
        fixed = await wai.proofread(self.env()["ai"], L["segments"])
        if not L.get("topic"):
            L["title"] = fixed["title"]
        L["segments"] = fixed["segments"]
        self.save(L)
        await self.lay_out(L)

    async def lay_out(self, L: dict, note: str = "") -> None:
        self.step(L, "AI 正在排画板")
        avail = await asyncio.to_thread(self.catalog_for, L)
        boards, notes = await wai.lay_out(self.env()["ai"], L["title"], L["segments"], note, avail)
        labels = {m["src"]: m["title"] for m in avail}
        for b in boards:
            for e in b["elements"]:
                if e["t"] == "media":
                    e["label"] = labels.get(e.get("src"), "")
        lesson = wai.to_lesson(L["title"], L["segments"], boards, duration=L.get("duration", 0))
        L["scene"], L["moves"] = core.lesson_scene(lesson, prefix=secrets.token_hex(3))
        L["notes"] = notes[:30]
        self.save(L)

    async def redo_board(self, L: dict, frame_id: str, note: str) -> None:
        """AI lays out one board again (the segments drawn on it), the rest stays as the teacher left it."""
        scene = L["scene"]
        els = scene["elements"]
        frames = [e for e in els if e.get("type") == "frame" and not e.get("isDeleted")]
        frame = next((f for f in frames if f["id"] == frame_id), None)
        if not frame:
            raise ValueError("这张画板已经不在了")
        ats = core_ats(els)
        mine = [e for e in els if e.get("frameId") == frame_id and not e.get("isDeleted") and e["id"] in ats]
        if not mine:
            raise ValueError("这张画板上还没有东西")
        lo, hi = min(ats[e["id"]] for e in mine), max(ats[e["id"]] for e in mine)
        sub = L["segments"][lo:hi + 1]
        self.step(L, "AI 正在重排这张画板")
        avail = await asyncio.to_thread(self.catalog_for, L)
        boards, notes = await wai.lay_out(self.env()["ai"], L["title"], sub, note, avail)
        for b in boards:
            for e in b["elements"]:
                e["at"] += lo
                if e["t"] == "media":
                    e["label"] = next((m["title"] for m in avail if m["src"] == e.get("src")), "")
        full = wai.to_lesson(L["title"], L["segments"], boards, duration=L.get("duration", 0))
        new_scene, new_moves = core.lesson_scene(full, prefix=secrets.token_hex(3))
        # the new board(s) go where the old one was; a second new board below it
        fx, fy = frame["x"], frame["y"]
        new_frames = [e for e in new_scene["elements"] if e["type"] == "frame"]
        shift = {f["id"]: (fx - f["x"], fy - f["y"] + k * 1400) for k, f in enumerate(new_frames)}
        for e in new_scene["elements"]:
            dx, dy = shift.get(e["id"] if e["type"] == "frame" else e.get("frameId"), (0, 0))
            e["x"] += dx
            e["y"] += dy
            if e["type"] == "frame" and len(new_frames) == 1:
                e["name"] = frame.get("name") or e.get("name")
        at = els.index(frame)
        keep = [e for e in els if e["id"] != frame_id and e.get("frameId") != frame_id]
        before = [e for e in keep if els.index(e) < at]
        after = [e for e in keep if els.index(e) > at]
        scene["elements"] = before + new_scene["elements"] + after
        L["moves"] = [m for m in L.get("moves") or [] if m.get("frame") != frame_id] + new_moves
        L["notes"] = notes[:30]
        self.save(L)

    # ------------------------------------------------------------------ voice
    def voice_cache(self) -> Path:
        return self.root / "_voice_cache"

    async def speak(self, text: str, voice: str, speed: float) -> tuple[Path, float, bool]:
        """(WAV, seconds, spoken just now) for one segment; every spoken sentence is kept by voice + speed + text."""
        import hashlib
        cache = self.voice_cache()
        cache.mkdir(parents=True, exist_ok=True)
        k = hashlib.sha256(f"{voice}|{speed:.2f}|{text}".encode()).hexdigest()[:32]
        wav, meta = cache / f"{k}.wav", cache / f"{k}.json"
        if wav.exists() and meta.exists():
            return wav, float(json.loads(meta.read_text())["seconds"]), False
        audio, secs = await V.tts(self.env()["voice_url"], text, voice, speed)
        wav.write_bytes(audio)
        with wave.open(str(wav), "rb") as r:
            odd = r.getnchannels() != 1 or r.getsampwidth() != 2 or r.getframerate() != 24000
        if odd:     # one format for joining: 24 kHz, mono, 16 bit
            fixed = cache / f"{k}.fix.wav"
            await asyncio.to_thread(ffmpeg, "-i", str(wav), "-ac", "1", "-ar", "24000", "-sample_fmt", "s16", str(fixed))
            fixed.replace(wav)
        meta.write_text(json.dumps({"seconds": secs}))
        return wav, secs, True

    async def voice(self, L: dict) -> list[int]:
        """AI narration: every segment spoken (sentences already spoken come from the cache), placed one after another.
        Returns the segments that were spoken anew. Without a voice service the lesson runs silent at reading speed."""
        url = self.env().get("voice_url")
        segs = L["segments"]
        parts: list[tuple[Path | None, float]] = []
        fresh: list[int] = []
        for i, s in enumerate(segs):
            self.step(L, "正在配音", round(100 * i / max(1, len(segs))))
            if url:
                wav, secs, new = await self.speak(speech.speakable(s["zh"]), L.get("voice") or "zm_yunjian", float(L.get("speed") or 1.0))
                if new:
                    fresh.append(i)
                parts.append((wav, secs))
            else:
                parts.append((None, round(max(1.2, len(s["zh"]) / 4.2), 2)))
        t = HEAD
        for s, (_, secs) in zip(segs, parts):
            s["t0"], s["t1"] = round(t, 2), round(t + secs, 2)
            t += secs + GAP
        L["duration"] = round(t - GAP + TAIL, 2)
        d = self.dir(L["id"])
        await asyncio.to_thread(self._join_audio, d, parts, L["duration"])
        L["audio"], L["audio_kind"] = "narration.wav", "ai" if url else "silent"
        self.save(L)
        return fresh

    @staticmethod
    def _join_audio(d: Path, parts: list[tuple[Path | None, float]], total: float) -> None:
        rate = 24000
        out = d / "narration.wav"
        with wave.open(str(out), "wb") as o:
            o.setnchannels(1)
            o.setsampwidth(2)
            o.setframerate(rate)
            written = 0
            o.writeframes(b"\0\0" * int(HEAD * rate))
            written += int(HEAD * rate)
            for w, secs in parts:
                if w:
                    with wave.open(str(w), "rb") as r:
                        frames = r.readframes(r.getnframes())
                        o.writeframes(frames)
                        written += len(frames) // 2
                else:
                    o.writeframes(b"\0\0" * int(secs * rate))
                    written += int(secs * rate)
                o.writeframes(b"\0\0" * int(GAP * rate))
                written += int(GAP * rate)
            rest = int(total * rate) - written
            if rest > 0:
                o.writeframes(b"\0\0" * rest)
        (d / "narration.mp3").unlink(missing_ok=True)

    async def take_recording(self, L: dict, src: Path) -> None:
        """The teacher's recording: recognised into segments. The boards (if any) follow the words to the new times."""
        url = self.env().get("voice_url")
        if not url:
            raise RuntimeError("平台的语音服务没有开，不能识别录音")
        d = self.dir(L["id"])
        wav16 = d / "_asr.wav"
        await asyncio.to_thread(ffmpeg, "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(wav16))
        await asyncio.to_thread(ffmpeg, "-i", str(src), "-vn", "-ac", "1", "-ar", "44100", str(d / "narration.wav"))
        rows = await V.asr(url, wav16)
        new = speech.merge_asr(rows)
        if not new:
            raise RuntimeError("录音里没听出说话")
        secs = await asyncio.to_thread(duration_of, d / "narration.wav")
        if L.get("scene") and L.get("segments"):
            mapping = speech.remap(L["segments"], new)
            speech.remap_scene(L["scene"], L.get("moves") or [], mapping)
        L["segments"] = new
        L["duration"] = round(max(secs, new[-1]["t1"]) + TAIL, 2)
        L["audio"], L["audio_kind"] = "narration.wav", "teacher"
        (d / "narration.mp3").unlink(missing_ok=True)
        wav16.unlink(missing_ok=True)
        src.unlink(missing_ok=True)
        self.save(L)

    def web_audio(self, L: dict) -> Path | None:
        """MP3 of the narration for the browser (every browser plays MP3)."""
        d = self.dir(L["id"])
        src, out = d / "narration.wav", d / "narration.mp3"
        if not src.exists():
            return None
        if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
            ffmpeg("-i", str(src), "-vn", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(out))
        return out

    # ------------------------------------------------------------------ media
    def course_name(self, L: dict) -> str:
        c = L.get("course") or {}
        return c.get("title", "") if isinstance(c, dict) else ""

    def textbook_catalog(self) -> list[dict]:
        """Every textbook's virtual labs and rendered animations: [{src, title, kind}]. Chapter pages are large (some are
        tens of MB), so each one is read once and remembered by size and time (in memory and in <root>/_catalog.json)."""
        env = self.env()
        root = Path(env.get("textbook_dir") or "/nonexistent")
        if not root.exists():
            return []
        pages = sorted(p for p in root.glob("*/ch*.html") if re.fullmatch(r"ch(M?\d+)\.html", p.name))
        disk = self.root / "_catalog.json"
        if "files" not in self._catalog:
            try:
                self._catalog["files"] = json.loads(disk.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self._catalog["files"] = {}
        known: dict = self._catalog["files"]
        out, changed, seen = [], False, set()
        for page in pages:
            st = page.stat()
            key, stamp = str(page), f"{st.st_size}:{int(st.st_mtime)}"
            seen.add(key)
            hit = known.get(key)
            if not hit or hit["stamp"] != stamp:
                book = page.parent.name
                text = page.read_text(encoding="utf-8", errors="ignore")
                items = [{"src": f"lab:{book}/{ch}.{k}", "title": label_of(label)[:80], "kind": "虚拟实验", "book": book}
                         for ch, k, label in LABBOX.findall(text)]
                items += [{"src": f"anim:{book}/{name}", "title": label_of(label)[:80], "kind": "动画", "book": book, "hash": h}
                          for name, h, label in ANIMBOX.findall(text)]
                hit = known[key] = {"stamp": stamp, "items": items}
                changed = True
            out += hit["items"]
        for k in [k for k in known if k not in seen]:
            known.pop(k)
            changed = True
        if changed:
            try:
                self.root.mkdir(parents=True, exist_ok=True)
                disk.write_text(json.dumps(known, ensure_ascii=False), encoding="utf-8")
            except OSError:
                pass
        return out

    def course_catalog(self, L: dict) -> list[dict]:
        c = L.get("course") or {}
        studio = self.env().get("studio")
        if not (c.get("pid") and studio):
            return []
        try:
            proj = studio.projects.load(c["pid"])
        except KeyError:
            return []
        if proj.get("owner") != L["owner"]:
            return []
        out = []
        for ch in (proj.get("outline") or {}).get("chapters", []):
            for i, les in enumerate(ch["lessons"], 1):
                title = (les.get("title") or {}).get("zh", "")
                for f in les.get("files") or []:
                    if f["kind"] in ("lab", "animation"):
                        out.append({"src": f"lesson:{c['pid']}/{les['id']}/{f['kind']}", "kind": "虚拟实验" if f["kind"] == "lab" else
                                    ("动画（含数字工厂车间）" if "3D" in f["name"] or "车间" in f["name"] else "动画"),
                                    "title": f"{ch['no']}.{i} {title}"[:80], "lid": les["id"], "name": f["name"]})
        return out

    def uploads(self, L: dict) -> list[dict]:
        d = self.dir(L["id"]) / "uploads"
        return [{"src": f"upload:{p.name}", "title": p.stem[:80], "kind": "上传的视频"} for p in sorted(d.glob("*")) if p.suffix in VIDEO_EXT]

    def book_title(self, book: str) -> str:
        titles = self._catalog.setdefault("titles", {})
        if book not in titles:
            try:
                p = Path(self.env().get("textbook_dir") or "/nonexistent") / book / "web" / "index.json"
                titles[book] = json.loads(p.read_text(encoding="utf-8")).get("title") or book
            except (OSError, ValueError):
                titles[book] = book
        return titles[book]

    def words_of(self, L: dict) -> set[str]:
        return bigrams(" ".join([L.get("topic", ""), L.get("note", "")[:2000], (L.get("title") or {}).get("zh", "")]
                                + [s["zh"] for s in L.get("segments") or []]))

    def catalog(self, L: dict) -> list[dict]:
        """Everything that can go into this lesson's frames (the editor's 插入 list): the teacher's videos, the course's
        labs and animations, then the textbooks' — those closest to this lesson first."""
        books = self.textbook_catalog()
        if L.get("book"):
            books = [m for m in books if m["book"] == L["book"]]
        words = self.words_of(L)
        ranked = sorted(enumerate(books), key=lambda x: (-len(words & bigrams(x[1]["title"])), x[0]))
        course = self.course_name(L)
        return ([dict(m, **{"from": "我上传的"}) for m in self.uploads(L)]
                + [dict(m, **{"from": course or "AI 建课"}) for m in self.course_catalog(L)]
                + [dict(m, **{"from": self.book_title(m["book"])}) for _, m in ranked])

    def catalog_for(self, L: dict, limit: int = 24) -> list[dict]:
        """What the AI may put on the boards: the lesson's course first, then the textbook items closest to the topic."""
        own = self.uploads(L) + self.course_catalog(L)
        c = L.get("course") or {}
        if c.get("lid"):          # a lesson of the AI course builder: its own lab and animation first
            own.sort(key=lambda m: m.get("lid") != c["lid"])
        books = self.textbook_catalog()
        if L.get("book"):
            books = [m for m in books if m["book"] == L["book"]]
        words = self.words_of(L)
        scored = sorted(((len(words & bigrams(m["title"])), n, m) for n, m in enumerate(books)), key=lambda x: (-x[0], x[1]))
        picked = [m for sc, _, m in scored if sc >= 2][:max(0, limit - len(own))]
        return [{"src": m["src"], "title": m["title"], "kind": m["kind"]} for m in (own[:limit] + picked)]

    def media_file(self, L: dict, src: str) -> tuple[str, Path, str] | None:
        """(kind video|page, file, hash) of a media source, or None."""
        env = self.env()
        kind, _, ref = src.partition(":")
        if kind == "lab":
            book, _, no = ref.partition("/")
            ch, _, k = no.partition(".")
            if not (re.fullmatch(r"[a-z0-9_\-]+", book) and re.fullmatch(r"M?\d+", ch) and k.isdigit()):
                return None
            from .textbook_api import chdir
            p = Path(env.get("textbook_dir") or "/nonexistent") / book / "lab" / f"{chdir(ch)}.html"
            return ("page", p, f"lab-{ch}-{k}") if p.exists() else None
        if kind == "anim":
            book, _, name = ref.partition("/")
            m = next((x for x in self.textbook_catalog() if x["src"] == src), None)
            if not m:
                return None
            p = Path(env["textbook_media"](book)) / f"{name}-{m['hash']}.mp4"
            return ("video", p, "") if p.exists() else None
        if kind == "lesson":
            m = next((x for x in self.course_catalog(L) if x["src"] == src), None)
            studio = env.get("studio")
            if not (m and studio):
                return None
            proj = studio.projects.load(src.split(":", 1)[1].split("/")[0])
            _, les = studio.find_lesson(proj, m["lid"])
            p = studio.lesson_dir(proj, les) / m["name"]
            return ("page" if src.endswith("/lab") else "video", p, "") if p.exists() else None
        if kind == "upload":
            p = self.dir(L["id"]) / "uploads" / Path(ref).name
            return ("video", p, "") if p.exists() and p.suffix in VIDEO_EXT else None
        return None

    def resolver(self, L: dict, link: Callable[[str, Path], str] | None) -> Callable[[str], dict | None]:
        """src → what the player needs. link(kind, file) = a signed URL (web page); None = inline everything (MP4)."""
        def resolve(src: str) -> dict | None:
            f = self.media_file(L, src)
            if not f:
                return None
            kind, path, h = f
            if link:
                url = link(kind, path)
                return {"kind": kind, "url": url + (f"#{h}" if h else "")}
            if kind == "page":
                return {"kind": "page", "html": path.read_text(encoding="utf-8"), **({"hash": h} if h else {}), "zoom": 1.0}
            return {"kind": "video", "url": "data:video/mp4;base64," + base64.b64encode(path.read_bytes()).decode()}
        return resolve

    # ------------------------------------------------------------------ compile, page, video
    def compile(self, L: dict, link: Callable[[str, Path], str] | None, scene: dict | None = None,
                segments: list[dict] | None = None) -> dict:
        return core.compile_scene(scene or L["scene"], segments or L["segments"], L.get("duration", 0),
                                  L.get("moves") or [], self.resolver(L, link))

    def page(self, L: dict, link: Callable[[str, Path], str], audio_url: str) -> str:
        data = self.compile(L, link)
        return core.page(data, (L.get("title") or {}).get("zh", "白板课"), audio_url=audio_url)

    async def render_mp4(self, L: dict) -> None:
        """Frame by frame in the lab checker's browser, CHUNK seconds per request; joined and given the narration."""
        url = self.env().get("labcheck_url")
        if not url:
            raise RuntimeError("出视频的录制服务没有开")
        d = self.dir(L["id"])
        work = d / "_render"
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        L["mp4"] = {"state": "running"}
        self.step(L, "排队出视频")
        try:
            await self._render(L, url, d, work)
        except BaseException:
            L["mp4"] = {"state": "failed", "at": now()}
            self.save(L)
            raise

    async def _render(self, L: dict, url: str, d: Path, work: Path) -> None:
        async with self.render_lock:
            data = self.compile(L, None)
            plain = None            # the same lesson with each lab frame as a still card (if a lab page cannot be recorded)
            total = data["total"]
            n = max(1, int((total + CHUNK - 0.001) // CHUNK))
            parts = []
            for k in range(n):
                self.step(L, f"出视频 {round(100 * k / n)}%", round(100 * k / n))
                start, dur = k * CHUNK, min(CHUNK, total - k * CHUNK)
                html_ = core.page(data, "render", render=True, seek_from=start)
                try:
                    video = await record(url, html_, dur)
                except RuntimeError as e:
                    if "not allowed" not in str(e) and "script error" not in str(e):
                        raise
                    plain = plain or still_labs(data)
                    video = await record(url, core.page(plain, "render", render=True, seek_from=start), dur)
                p = work / f"{k:03d}.mp4"
                p.write_bytes(video)
                parts.append(p)
            self.step(L, "出视频：配上声音", 99)
            out = d / "白板课.mp4"
            await asyncio.to_thread(join_video, work, parts, d / "narration.wav", out)
        shutil.rmtree(work, ignore_errors=True)
        L["mp4"] = {"state": "done", "at": now(), "seconds": round(total, 1)}
        self.save(L)


def core_ats(els: list[dict]) -> dict[str, int]:
    """Effective segment of every element (its own wq_at, else the one before it), as the compiler reads it."""
    out, at = {}, 0
    for e in els:
        if e.get("isDeleted") or e.get("type") == "frame":
            continue
        v = (e.get("customData") or {}).get("wq_at")
        if isinstance(v, int):
            at = v
        out[e["id"]] = at
    return out


def duration_of(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, timeout=120)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def still_labs(data: dict) -> dict:
    """A copy of the player data whose lab frames show a card instead of the live page (the recorder has no network)."""
    out = dict(data)
    out["media"] = []
    for m in data.get("media") or []:
        if m["kind"] == "page":
            card = ("<!doctype html><meta charset='utf-8'><body style='margin:0;display:flex;align-items:center;justify-content:center;"
                    "height:100vh;background:#f4f1ea;font:28px sans-serif;color:#1d2329'>▶ 虚拟实验（网页版里可以动手操作）</body>")
            out["media"].append(dict(m, html=card, url=None))
        else:
            out["media"].append(m)
    return out


async def record(url: str, page_html: str, seconds: float) -> bytes:
    import httpx
    try:
        async with httpx.AsyncClient(timeout=1000, trust_env=False) as c:
            r = await c.post(url.rstrip("/") + "/render3d", json={"html": page_html, "duration": round(seconds, 3), "fps": 30,
                                                                  "width": 1280, "height": 720})
    except httpx.HTTPError as e:
        raise RuntimeError(f"录制服务连不上：{type(e).__name__}") from e
    if r.status_code != 200:
        raise RuntimeError(f"录制服务回答 {r.status_code}")
    d = r.json()
    if not d.get("ok"):
        raise RuntimeError(str(d.get("error") or "录制失败")[:500])
    return base64.b64decode(d["video"])


def join_video(work: Path, parts: list[Path], audio: Path, out: Path) -> None:
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    silent = work / "all.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent))
    tmp = out.with_suffix(".part.mp4")
    ffmpeg("-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
           "-shortest", "-movflags", "+faststart", str(tmp))
    tmp.replace(out)


def summary(L: dict, busy: bool) -> dict:
    return {"id": L["id"], "title": L.get("title") or {}, "source": L.get("source"), "state": L.get("state"),
            "job": L.get("job") if busy else None, "error": L.get("error", ""), "duration": L.get("duration", 0),
            "segments": len(L.get("segments") or []), "updated": L.get("updated"), "created": L.get("created"),
            "course": L.get("course"), "mp4": (L.get("mp4") or {}).get("state") == "done"}


def escape(s: str) -> str:
    return _html.escape(s)
