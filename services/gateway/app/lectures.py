"""讲解视频 in the AI course builder (round 4, step 5): the part of the orchestrator that makes lecture videos.

  B. make_lecture   — after a lesson's slides are laid out: the lecturer writes what to say on each slide
                      (Chinese + English), the voice service speaks it, the slides become the picture.
  A. take_recording — the teacher's own recording: recognised into Chinese subtitles, proofread and translated by
                      the AI, spoken in English into the same times.
  edit_lecture      — the teacher changes a line (narration, subtitle or translation); only changed sentences are
                      spoken again (every spoken sentence is cached by voice + speed + text).

Mixed into studio.Studio; uses its projects, ai, lesson_dir, needs_you and friends.
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import team
from .production import lecture as L
from .production import voice as V

log = logging.getLogger("wenquest.lecture")
DEFAULT_VOICES = {"zh": "zf_xiaobei", "en": "af_heart"}
SAMPLE = {"zh": "同学们好，欢迎来到机器人学。这一节我们看看，一台六轴机械臂是怎样把末端送到目标位置的。",
          "en": "Hello everyone, and welcome to robotics. In this lesson we will see how a six-axis arm moves its tool to a target."}
MAX_SPEED = 1.35


def _now() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")


def fake_narration(slides: list[dict]) -> dict:
    out = []
    for i, s in enumerate(slides, 1):
        words = " ".join(s["text"].split())[:24] or "本页"
        out.append({"n": i, "zh": f"第{i}页。我们来看：{words}。想一想它和机器人问题有什么关系。",
                    "en": f"Slide {i}. Let us look at this page and think about how it connects to the robot problem."})
    return {"slides": out}


def fake_subtitles(lines: list[dict]) -> dict:
    return {"lines": [{"n": x["n"], "zh": x["text"] + "。", "en": f"Line {x['n']} of the lecture."} for x in lines]}


class LectureMixin:
    # --- voices ----------------------------------------------------------------------------------------------------
    def voices_of(self, proj: dict) -> dict:
        return {**DEFAULT_VOICES, **(proj.get("voices") or {})}

    @staticmethod
    def lecture_langs(proj: dict) -> list[str]:
        lang = proj["outline"].get("languages")
        return ["zh"] if lang == "zh" else ["en"] if lang == "en" else ["zh", "en"]

    def lecture_dir(self, proj: dict, les: dict) -> Path:
        return self.lesson_dir(proj, les) / "lecture"

    def voice_cache(self, proj: dict) -> Path:
        return self.projects.root / proj["id"] / "voice_cache"

    async def speak(self, proj: dict | None, text: str, voice: str, speed: float = 1.0, cache: Path | None = None) -> tuple[Path, float]:
        """One sentence spoken by the voice service, cached by voice + speed + text."""
        cache = cache or self.voice_cache(proj)
        cache.mkdir(parents=True, exist_ok=True)
        k = L.key(voice, f"{speed:.2f}", text)
        wav, meta = cache / f"{k}.wav", cache / f"{k}.json"
        if wav.exists() and meta.exists():
            return wav, float(json.loads(meta.read_text())["seconds"])
        audio, secs = await V.tts(self.voice_url, text, voice, speed)
        wav.write_bytes(audio)
        meta.write_text(json.dumps({"seconds": secs, "text": text[:200]}))
        return wav, secs

    async def voice_sample(self, cache: Path, voice: str, lang: str) -> Path:
        wav, _ = await self.speak(None, SAMPLE["zh" if lang == "zh" else "en"], voice, 1.0, cache)
        return wav

    # --- files list --------------------------------------------------------------------------------------------------
    def lecture_file(self, proj: dict, les: dict, no: str) -> dict | None:
        lec, d = les.get("lecture") or {}, self.lecture_dir(proj, les)
        langs = [x for x in lec.get("langs") or [] if (d / f"{x}.mp4").exists()]
        if not langs:
            return None
        title = (les.get("spec_title") or [""])[0] or (les.get("title") or {}).get("zh", "")
        return {"name": f"{no} 讲解视频 {title}"[:80].strip() + ".mp4", "kind": "lecture", "teacher_only": False,
                "seconds": lec.get("seconds", 0), "langs": langs, "source": lec.get("source", "ai")}

    def set_lecture_file(self, proj: dict, les: dict, no: str) -> None:
        files = [f for f in les.get("files") or [] if f["kind"] != "lecture"]
        entry = self.lecture_file(proj, les, no)
        if entry:
            at = next((i for i, f in enumerate(files) if f["kind"] == "animation"), -1) + 1
            files.insert(at, entry)
        les["files"] = files

    def _lecture_failed(self, proj: dict, les: dict, why: str) -> None:
        les.setdefault("checks", {})["lecture"] = {"ok": False, "note": why[:300]}
        self.needs_you(les, "lecture", why)
        self.projects.save(proj)

    def lecture_check(self, les: dict) -> dict:
        lec = les.get("lecture") or {}
        c = (les.get("checks") or {}).get("lecture")
        if c and not c.get("ok"):
            return c
        if not lec.get("seconds"):
            return {"ok": False, "note": "还没有讲解视频"}
        m, s = divmod(int(lec["seconds"]), 60)
        who = "你的讲课录像" if lec.get("source") == "teacher" else "AI 讲解"
        langs = "、".join({"zh": "中文", "en": "英文"}[x] for x in lec.get("langs") or [])
        return {"ok": True, "note": f"{who}，{m} 分 {s:02d} 秒；{langs}配音和字幕"}

    # --- B. AI narration -----------------------------------------------------------------------------------------------
    async def make_lecture(self, proj: dict, chapter: dict, les: dict, spec: dict, no: str) -> dict | None:
        """The lesson's lecture video from its slides. A teacher's recording, when there is one, is kept."""
        from . import slides as slidemod
        if not self.voice_url:
            return None
        lec = les.get("lecture") or {}
        if lec.get("source") == "teacher" and (self.lecture_dir(proj, les) / "zh.mp4").exists():
            self.set_lecture_file(proj, les, no)
            return lec
        self.clear_attention(les, "lecture")
        les.setdefault("checks", {}).pop("lecture", None)
        d = self.lesson_dir(proj, les)
        deck = next((d / f["name"] for f in les.get("files") or [] if f["kind"] == "slides" and (d / f["name"]).exists()), None)
        if not deck:
            return None
        out = self.lecture_dir(proj, les)
        out.mkdir(parents=True, exist_ok=True)
        try:
            proj["busy"] = {"label": f"正在准备讲解视频的画面：{no}", "since": _now()}
            self.projects.save(proj)
            manifest = await asyncio.to_thread(slidemod.convert, deck.read_bytes(), out / "slides")
            slides = manifest["slides"]
            script = await self.narration(proj, chapter, les, spec, no, slides)
            return await self.build_ai_lecture(proj, les, no, script)
        except (V.VoiceError, L.LectureError, OSError, RuntimeError) as e:
            log.warning("lecture %s failed: %s", no, e)
            self._lecture_failed(proj, les, f"讲解视频没有做成（{str(e)[:160]}）。稍后点“重做讲解视频”。")
            return None

    async def narration(self, proj: dict, chapter: dict, les: dict, spec: dict, no: str, slides: list[dict]) -> dict:
        """What to say on every slide. Narration the teacher edited is kept for slides whose text did not change."""
        path = self.lecture_dir(proj, les) / "script.json"
        old = json.loads(path.read_text()) if path.exists() else {}
        kept = {s["text"]: s for s in old.get("slides") or [] if s.get("edited")} if old.get("source") == "ai" else {}
        same = old.get("source") == "ai" and [s["text"] for s in old.get("slides") or []] == [s["text"] for s in slides]
        if same:
            return {"source": "ai", "slides": [{**s} for s in old["slides"]]}
        proj["busy"] = {"label": f"主讲教授正在写讲稿：{no}", "since": _now()}
        self.projects.save(proj)
        course, _, _ = self.pairs_for(proj, chapter)
        spec_json = json.dumps({k: spec.get(k) for k in ("title", "goal", "problem", "concept", "animation", "lab", "model", "summary")},
                               ensure_ascii=False)[:12000]
        problem, rows = "", []
        for _ in range(2):
            data = await self.ai.json(system=team.NARRATOR, prompt=team.narration_prompt(no, f"{course[0]} / {course[1]}", spec_json, slides, problem),
                                      schema=team.narration_schema(), max_tokens=9000, fake=lambda: fake_narration(slides))
            rows = [r for r in (data or {}).get("slides") or [] if isinstance(r, dict)]
            by_n = {int(r.get("n") or 0): r for r in rows}
            missing = [i for i in range(1, len(slides) + 1) if not str((by_n.get(i) or {}).get("zh") or "").strip()]
            if not missing:
                break
            problem = f"slides {missing[:10]} have no narration; write all {len(slides)}."
        by_n = {int(r.get("n") or 0): r for r in rows}
        out = []
        for i, s in enumerate(slides, 1):
            if s["text"] in kept:
                out.append({**kept[s["text"]]})
                continue
            r = by_n.get(i) or {}
            zh = str(r.get("zh") or "").strip() or f"请看这一页。{s['text'][:60]}"
            en = str(r.get("en") or "").strip() or "Please look at this slide."
            out.append({"text": s["text"], "zh": zh[:900], "en": en[:1500], "edited": False})
        return {"source": "ai", "slides": out}

    async def build_ai_lecture(self, proj: dict, les: dict, no: str, script: dict) -> dict:
        out = self.lecture_dir(proj, les)
        manifest = json.loads((out / "slides" / "manifest.json").read_text())
        langs, voices = self.lecture_langs(proj), self.voices_of(proj)
        total = sum(len(L.sentences(s[lang], lang)) for s in script["slides"] for lang in langs)
        done, t0 = 0, time.time()
        slides = []
        for s, m in zip(script["slides"], manifest["slides"]):
            audio = {}
            for lang in langs:
                audio[lang] = []
                for text in L.sentences(s[lang], lang):
                    wav, secs = await self.speak(proj, text, voices[lang])
                    audio[lang].append({"wav": wav, "seconds": secs, "text": text})
                    done += 1
                    if done % 5 == 0 or done == total:
                        proj["busy"] = {"label": f"正在合成讲解配音：{no}（{done}/{total} 句）", "since": _now()}
                        self.projects.save(proj)
            v = (m.get("videos") or [None])[0]
            clip = out / "slides" / v["src"] if v and (out / "slides" / v["src"]).exists() else None
            slides.append({"image": out / "slides" / m["image"], "clip": clip,
                           "box": {k: v[k] for k in ("x", "y", "w", "h")} if clip else None,
                           "clip_seconds": L.probe_seconds(clip) if clip else 0.0, "audio": audio})
        proj["busy"] = {"label": f"正在合成讲解视频：{no}", "since": _now()}
        self.projects.save(proj)
        result = await asyncio.to_thread(L.assemble, slides, langs, out, self.voice_cache(proj) / "segments")
        script.update({"langs": langs, "voices": {k: voices[k] for k in langs}, "seconds": result["seconds"],
                       "timeline": result["slides"], "cues": result["cues"]})
        (out / "script.json").write_text(json.dumps(script, ensure_ascii=False))
        les["lecture"] = {"source": "ai", "seconds": result["seconds"], "langs": langs, "voices": script["voices"],
                          "made": _now(), "took": round(time.time() - t0)}
        les.setdefault("checks", {})["lecture"] = self.lecture_check(les)
        self.clear_attention(les, "lecture")
        self.set_lecture_file(proj, les, no)
        return les["lecture"]

    # --- A. the teacher's recording --------------------------------------------------------------------------------------
    async def take_recording(self, proj: dict, lid: str, src: Path) -> None:
        """老师亲讲: the recording becomes the lecture video; Chinese subtitles by speech recognition (proofread by the
        AI), English subtitles by the AI, English voice spoken into the same times."""
        chapter, les = self.find_lesson(proj, lid)
        no = self.lesson_no(proj, chapter, les)
        out = self.lecture_dir(proj, les)
        work = out.with_name("lecture.new")
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        self.clear_attention(les, "lecture")
        try:
            proj["busy"] = {"label": f"正在转换你的讲课录像：{no}", "since": _now()}
            self.projects.save(proj)
            seconds = await asyncio.to_thread(L.transcode, src, work / "zh.mp4", work / "audio16k.wav")
            proj["busy"] = {"label": f"正在识别讲课录音：{no}", "since": _now()}
            self.projects.save(proj)
            segs = await V.asr(self.voice_url, work / "audio16k.wav")
            (work / "audio16k.wav").unlink(missing_ok=True)
            if not segs:
                raise L.LectureError("录像里没有识别到讲话声音")
            course, _, _ = self.pairs_for(proj, chapter)
            lines = await self.subtitles(proj, no, course, segs, les)
            script = {"source": "teacher", "seconds": seconds, "lines": lines}
            (work / "script.json").write_text(json.dumps(script, ensure_ascii=False))
            shutil.rmtree(out, ignore_errors=True)
            work.rename(out)
            await self.build_teacher_lecture(proj, les, no)
        except (V.VoiceError, L.LectureError, OSError, RuntimeError) as e:
            shutil.rmtree(work, ignore_errors=True)
            log.warning("recording %s failed: %s", no, e)
            self._lecture_failed(proj, les, f"讲课录像没有处理成（{str(e)[:160]}）。可以重新上传。")
            self.say(proj, f"《{no}》的讲课录像没有处理成：{str(e)[:160]}。可以重新上传。", "lead", "lesson")
            return
        finally:
            src.unlink(missing_ok=True)
        m, s = divmod(int(les["lecture"]["seconds"]), 60)
        self.say(proj, f"《{no}》的讲课录像处理好了（{m} 分 {s:02d} 秒）：中文字幕来自语音识别，英文字幕和英文配音由 AI 生成。"
                       "请在这一课的“讲解视频”里逐句看一遍，改好后自动重新配音。", "lead", "lesson")

    async def subtitles(self, proj: dict, no: str, course: list[str], segs: list[dict], les: dict) -> list[dict]:
        rows = [{"n": i, "text": s["text"], "start": s["start"], "end": s["end"]} for i, s in enumerate(segs, 1)]
        out = []
        for k in range(0, len(rows), 40):
            batch = rows[k:k + 40]
            proj["busy"] = {"label": f"正在校对字幕并翻译成英文：{no}（{min(k + 40, len(rows))}/{len(rows)} 句）", "since": _now()}
            self.projects.save(proj)
            data = await self.ai.json(system=team.SUBTITLER,
                                      prompt=team.subtitle_prompt(f"{course[0]} / {course[1]}", f"{no} {(les.get('title') or {}).get('zh', '')}", batch),
                                      schema=team.subtitle_schema(), max_tokens=8000, fake=lambda b=batch: fake_subtitles(b))
            by_n = {int(r.get("n") or 0): r for r in (data or {}).get("lines") or [] if isinstance(r, dict)}
            for x in batch:
                r = by_n.get(x["n"]) or {}
                out.append({"start": x["start"], "end": x["end"], "raw": x["text"],
                            "zh": str(r.get("zh") or x["text"]).strip()[:300], "en": str(r.get("en") or "").strip()[:500]})
        return out

    async def build_teacher_lecture(self, proj: dict, les: dict, no: str) -> dict:
        """Chinese: the recording itself. English: every line spoken, fitted into its time (sped up to 1.35x at most)."""
        out = self.lecture_dir(proj, les)
        script = json.loads((out / "script.json").read_text())
        lines, seconds = script["lines"], float(script["seconds"])
        langs = ["zh"] + (["en"] if proj["outline"].get("languages") != "zh" else [])
        voice = self.voices_of(proj)["en"]
        zh_cues = [{"start": x["start"], "end": x["end"], "text": x["zh"]} for x in lines if x["zh"]]
        (out / "zh.vtt").write_text(L.vtt(zh_cues), encoding="utf-8")
        if "en" in langs:
            spoken, total = [], len(lines)
            for i, x in enumerate(lines):
                if not x["en"]:
                    continue
                nxt = next((y["start"] for y in lines[i + 1:] if y["en"]), seconds)
                slot = max(0.8, nxt - x["start"] - 0.1)
                wav, secs = await self.speak(proj, x["en"], voice, 1.0)
                if secs > slot * 1.05:
                    wav, secs = await self.speak(proj, x["en"], voice, round(min(MAX_SPEED, secs / slot + 0.02), 2))
                spoken.append({"start": x["start"], "end": x["end"], "wav": wav, "seconds": secs, "text": x["en"]})
                if (i + 1) % 5 == 0:
                    proj["busy"] = {"label": f"正在合成英文配音：{no}（{i + 1}/{total} 句）", "since": _now()}
                    self.projects.save(proj)
            proj["busy"] = {"label": f"正在合成英文版讲解视频：{no}", "since": _now()}
            self.projects.save(proj)

            def english():
                cues = L.dub(spoken, seconds, out / "en.wav")
                L.mux(out / "zh.mp4", out / "en.wav", out / "en.mp4")
                (out / "en.wav").unlink(missing_ok=True)
                (out / "en.vtt").write_text(L.vtt(cues), encoding="utf-8")
                return cues
            en_cues = await asyncio.to_thread(english)
        else:
            en_cues = []
        if not (out / "poster.jpg").exists():
            await asyncio.to_thread(L.ff, "-ss", str(min(3.0, seconds / 2)), "-i", str(out / "zh.mp4"), "-frames:v", "1", "-q:v", "4",
                                    str(out / "poster.jpg"))
        script.update({"langs": langs, "voices": {"en": voice} if "en" in langs else {}, "cues": {"zh": zh_cues, "en": en_cues}})
        (out / "script.json").write_text(json.dumps(script, ensure_ascii=False))
        les["lecture"] = {"source": "teacher", "seconds": seconds, "langs": langs, "voices": script["voices"], "made": _now()}
        les.setdefault("checks", {})["lecture"] = self.lecture_check(les)
        self.clear_attention(les, "lecture")
        self.set_lecture_file(proj, les, no)
        les["checklist"] = self.checklist(proj, les, *self._media_of(proj, les))
        return les["lecture"]

    def _media_of(self, proj: dict, les: dict) -> tuple:
        d = self.lesson_dir(proj, les)
        video = next(({"video": d / f["name"], "poster": None} for f in les.get("files") or [] if f["kind"] == "animation"), None)
        lab = {"code": d / "lab.js", "image": d / "lab.png" if (d / "lab.png").exists() else None} if (d / "lab.js").exists() else None
        return video, lab

    # --- edits -------------------------------------------------------------------------------------------------------------
    def lecture_view(self, proj: dict, les: dict) -> dict:
        path = self.lecture_dir(proj, les) / "script.json"
        if not path.exists():
            return {"source": "", "rows": []}
        sc = json.loads(path.read_text())
        if sc.get("source") == "teacher":
            rows = [{"n": i, "start": x["start"], "end": x["end"], "zh": x["zh"], "en": x["en"], "raw": x.get("raw", "")}
                    for i, x in enumerate(sc["lines"])]
        else:
            tl = sc.get("timeline") or []
            rows = [{"n": i, "start": (tl[i]["start"] if i < len(tl) else 0), "zh": s["zh"], "en": s["en"], "edited": s.get("edited", False)}
                    for i, s in enumerate(sc.get("slides") or [])]
        return {"source": sc.get("source", "ai"), "seconds": sc.get("seconds", 0), "langs": sc.get("langs", []),
                "voices": sc.get("voices", {}), "rows": rows}

    async def edit_lecture(self, proj: dict, lid: str, rows: list[dict]) -> None:
        """Apply the teacher's changed lines, then speak and assemble again (unchanged sentences come from the cache)."""
        chapter, les = self.find_lesson(proj, lid)
        no = self.lesson_no(proj, chapter, les)
        out = self.lecture_dir(proj, les)
        sc = json.loads((out / "script.json").read_text())
        items = sc["lines"] if sc.get("source") == "teacher" else sc["slides"]
        for r in rows:
            i = int(r.get("n", -1))
            if 0 <= i < len(items):
                for k in ("zh", "en"):
                    if isinstance(r.get(k), str) and r[k].strip() and r[k].strip() != items[i][k]:
                        items[i][k] = r[k].strip()[:1500]
                        items[i]["edited"] = True
        (out / "script.json").write_text(json.dumps(sc, ensure_ascii=False))
        try:
            if sc.get("source") == "teacher":
                await self.build_teacher_lecture(proj, les, no)
            else:
                await self.build_ai_lecture(proj, les, no, sc)
                les["checklist"] = self.checklist(proj, les, *self._media_of(proj, les))
        except (V.VoiceError, L.LectureError, OSError) as e:
            self._lecture_failed(proj, les, f"改过的讲解视频没有合成成（{str(e)[:160]}）。稍后再试。")
            return
        self.say(proj, f"《{no}》的讲解视频按你改的内容重新配好音了。", "lead", "lesson")

    async def redo_lecture(self, proj: dict, lid: str) -> None:
        """重做讲解视频 (AI): narration is written again, except the slides the teacher edited."""
        chapter, les = self.find_lesson(proj, lid)
        no = self.lesson_no(proj, chapter, les)
        d = self.lesson_dir(proj, les)
        spec = json.loads((d / "spec.json").read_text())["lesson"]
        if (les.get("lecture") or {}).get("source") == "teacher":
            les["lecture"] = {}
        script = self.lecture_dir(proj, les) / "script.json"
        if script.exists():
            sc = json.loads(script.read_text())
            if sc.get("source") == "ai" and not any(s.get("edited") for s in sc.get("slides") or []):
                script.unlink()   # write it afresh
            elif sc.get("source") == "teacher":
                shutil.rmtree(self.lecture_dir(proj, les), ignore_errors=True)
        lec = await self.make_lecture(proj, chapter, les, spec, no)
        les["checklist"] = self.checklist(proj, les, *self._media_of(proj, les))
        self.say(proj, f"《{no}》的讲解视频{'重做好了' if lec else '还是没做成，请看清单'}。", "lead", "lesson")
