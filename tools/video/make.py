"""公开课视频制作（第 22 轮）：讲稿 → 配音 → 逐镜头画面 → 合成（字幕、水印、响度）→ 封面与上传资料。

    python3 tools/video/make.py docs/课程视频/线性代数/14-2 --lang zh --voice kokoro --out /tmp/v
    python3 tools/video/make.py docs/课程视频/线性代数/14-2 --lang both --voice estimate --only problem,lab   # 只渲染部分镜头试看

输出（--out/<语言>/）：lecture.mp4、lecture.srt、cover_youtube.png（1280×720）、cover_bilibili.png（1146×717）、
upload.md（标题、简介含章节时间点、标签）、timeline.json。中间文件在 --out/work/，可反复使用（改一句只重做受影响的镜头）。

环境变量：WQ_MANIM（manim 命令，默认 manim）、WQ_FOOTAGE（数字工厂等录屏素材目录）、WQ_TTS_MODELS（kokoro 模型目录）、
WQ_CLONE_DIR（clone.py 生成的克隆配音目录）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import script as S  # noqa: E402
import voice as V  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FPS = 30
HEAD, PAUSE, TAIL, LEAD = 0.6, 0.38, 0.9, 0.35       # 秒：镜头开头、句间、镜头结尾；画面比配音提前 LEAD 秒变化
FONT_ZH = "Noto Sans CJK SC"
COURSE = {"linalg": ["线性代数", "Linear Algebra"], "sewing": ["缝纫机设计与制造", "Sewing Machine Design and Manufacturing"]}
VOICE_NOTE = {"clone": ["配音：AI 合成（讲者本人声音）", "Voice: AI-generated from the lecturer's own voice"],
              "kokoro": ["配音：AI 合成", "Voice: AI-generated"],
              "estimate": ["无声排版样片", "Silent layout preview"]}


def sh(*a, **k):
    return subprocess.run([str(x) for x in a], check=True, **k)


def dur(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def h(obj) -> str:
    return hashlib.sha1(json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- timing
def timeline(lec, lang, voice):
    """Per shot: lines with wav + start/end (seconds within the shot), step times, total length."""
    out = []
    for s in lec.shots:
        t, lines, steps = HEAD, [], []
        for ln in s.lines[lang]:
            wav, d = voice.say(voice.spoken(ln.spoken))
            if ln.step:
                steps.append(max(0.2, t - LEAD))
            lines.append({"shown": ln.shown, "wav": str(wav), "start": t, "end": t + d})
            t += d + PAUSE
        total = t - PAUSE + TAIL
        if s.kind == "title":
            total = max(total, 5.0)
        if s.kind == "lab":
            for st, at in zip(s.data.get("steps") or [], steps):   # a sweep must finish inside the shot
                total = max(total, at + float(st.get("dur", 0)) + 0.5)
        out.append({"id": s.id, "kind": s.kind, "lines": lines, "steps": steps, "total": round(total, 3)})
    return out


# ---------------------------------------------------------------- pictures
def svg_to_png(svg: Path, png: Path, width=1400):
    """Rasterise a textbook figure (SVG) with Chromium so fonts match the book."""
    if png.exists() and png.stat().st_mtime > svg.stat().st_mtime:
        return png
    html = png.with_suffix(".html")
    html.write_text(f"<html><body style='margin:0;background:#fff'><img id='i' src='{svg.resolve().as_uri()}' style='width:{width // 2}px'></body></html>",
                    encoding="utf-8")
    code = f"""
import asyncio
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(device_scale_factor=2, viewport={{'width': {width}, 'height': 1400}})
        await pg.goto({html.resolve().as_uri()!r}); await pg.wait_for_timeout(300)
        await (await pg.query_selector('#i')).screenshot(path={str(png)!r}); await b.close()
asyncio.run(m())
"""
    sh(sys.executable, "-c", code)
    return png


def figure(lec, name, lang, work: Path) -> str:
    if lec.web:                                   # 网页版教材（第 23 轮）：img/名字.webp，英文版优先 img/en/
        stem = Path(name).stem
        src = lec.web / "img" / "en" / f"{stem}.webp"
        if lang != "en" or not src.exists():
            src = lec.web / "img" / f"{stem}.webp"
        if not src.exists():
            raise S.ScriptError(f"找不到插图 {src}")
        png = work / f"{stem}.{lang}.png"
        if not png.exists():
            sh("ffmpeg", "-y", "-loglevel", "error", "-i", src, png)
        return str(png)
    base = S.TEXTBOOK / "build" / lec.book / "figs"
    svg = (base / "en" / f"{name}.svg") if lang == "en" and (base / "en" / f"{name}.svg").exists() else base / f"{name}.svg"
    if not svg.exists():
        raise S.ScriptError(f"找不到教材图 {svg}（先构建教材：python3 textbook/tools/build.py {lec.book}）")
    return str(svg_to_png(svg, work / f"{name}.{lang}.png"))


def manim(scene_file: Path, scene: str, env: dict, work: Path, quality: str) -> Path:
    exe = os.environ.get("WQ_MANIM", "manim")
    media = work / "media"
    q = {"h": ["-qh", "-r", "1920,1080"], "l": ["-ql"]}[quality]
    r = subprocess.run([exe, *q, "--fps", str(FPS), "--disable_caching", "--media_dir", str(media), "--progress_bar", "none",
                        str(scene_file), scene], env={**os.environ, **env}, cwd=scene_file.parent, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"Manim 渲染失败（{scene_file.name}）：\n{r.stderr[-3000:]}")
    vids = sorted(media.rglob(f"{scene}.mp4"), key=lambda p: p.stat().st_mtime)
    if not vids:
        raise RuntimeError("Manim 没有输出视频")
    return vids[-1]


def fit_length(src: Path, total: float, dst: Path):
    """Exactly `total` seconds at 1920×1080/30 fps: cut, or hold the last frame."""
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf",
       f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0f1419,fps={FPS},"
       f"tpad=stop_mode=clone:stop_duration={total + 1:.2f},format=yuv420p",
       "-t", f"{total:.3f}", "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", dst)


ANIM_PATCH = r'''

# ---- 公开课视频模式（tools/video/make.py 追加）：字幕由视频统一烧录，动画里的字幕改为“等到下一句”的同步点 ----
import json as _json, os as _os
_V = _json.loads(open(_os.environ["WQ_ANIM_SYNC"], encoding="utf-8").read())
_K = [0]

def _pick(pair):
    if isinstance(pair, (list, tuple)):
        return pair[0] if _V["lang"] == "zh" else (pair[1] if len(pair) > 1 and pair[1] else pair[0])
    return pair

def _v_title(self, no, zh_text, en_text=""):
    head = VGroup(zh(no, 26, YELLOW), zh(zh_text if _V["lang"] == "zh" else (en_text or zh_text), 34, WHITE, BOLD)).arrange(RIGHT, buff=0.3)
    fit(head, 11).to_corner(UL, buff=0.4)
    self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.8)
    self._title = head
    return head

def _v_sync(self, fallback):
    k = _K[0]; _K[0] += 1
    marks = _V["marks"]
    target = marks[k] if k < len(marks) else self.renderer.time + (fallback or 0)
    now = self.renderer.time
    if target > now + 1 / 60:
        self.wait(target - now)

def _v_caption(self, zh_text, en_text="", wait=1.5):
    _v_sync(self, wait)
    return VMobject()

def _v_card(self, lines, wait=2.5):
    self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
    body = []
    for i, x in enumerate(lines):
        if isinstance(x, Mobject):
            body.append(x)
        else:
            body.append(zh(_pick(x), 34 if i == 0 else 30, YELLOW if i == 0 else WHITE, BOLD if i == 0 else NORMAL))
    g = fit(VGroup(*body).arrange(DOWN, buff=0.35), 12)
    box = SurroundingRectangle(g, color=YELLOW, buff=0.45, corner_radius=0.15, stroke_width=2)
    self.play(Create(box), LaggedStart(*[Write(m) for m in body], lag_ratio=0.35), run_time=2.2)

Base.title = _v_title
Base.caption = _v_caption
Base.card = _v_card
'''


def deck_stills(lec, lang, work: Path) -> dict:
    """课件里的三维片段（虚拟样机、三维模型）先在三维页上逐帧录好（三维页自己的逐帧推进），课件录屏时按帧换图。"""
    import labrec
    import yaml
    spec = yaml.safe_load((lec.web / "course" / "slides" / f"{lec.data['deck']}.yaml").read_text(encoding="utf-8"))
    out = {}
    for name, c in (spec.get("clips") or {}).items():
        if not c["page"].startswith(("proto-", "model-")):
            continue
        d = work / f"still_{lang}_{name}"
        if not (d / "00000.jpg").exists():
            page = lec.web / "src" / lang / "labs" / f"{c['page']}.html"
            full = ("var s=document.createElement('style');s.textContent='" + (c.get("selector") or "#stage") +
                    "{position:fixed!important;left:0!important;top:0!important;width:100vw!important;height:100vh!important;"
                    "z-index:99999!important;margin:0!important;border-radius:0!important}';document.head.appendChild(s);"
                    "dispatchEvent(new Event('resize'))")
            steps, times = [{"js": full}], [0.0]
            for st in sorted(c.get("steps") or [], key=lambda x: x.get("at", 0)):
                st = {k: v for k, v in st.items() if k != "at"}
                if "press" in st:                 # 舞台盖住了按钮：用脚本点
                    sels = st.pop("press")
                    sels = sels if isinstance(sels, list) else [sels]
                    click = ";".join(f"document.querySelector({json.dumps(x if x[:1] in '#.[' else '#' + x)}).click()" for x in sels)
                    st["js"] = click + (";" + st["js"] if st.get("js") else "")
                steps.append(st)
                times.append(float(st.get("at", 0)) + 0.1)
            loop = float(c.get("loop") or 12)
            mp4 = work / "shots" / f"still_{name}_{lang}.mp4"
            mp4.parent.mkdir(parents=True, exist_ok=True)
            labrec.run(page.resolve().as_uri(), c["page"], steps, times, loop, mp4, standalone=True, viewport=(1280, 720),
                       manual=True, fps=15)
            d.mkdir(parents=True, exist_ok=True)
            sh("ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", "fps=15,scale=1600:-2", "-q:v", "3", "-start_number", "0",
               d / "%05d.jpg")
            if (d / "00001.jpg").exists():   # 第一帧录在三维舞台铺开之前（黑屏），循环时每 12 秒闪一下：用第二帧代替
                shutil.copyfile(d / "00001.jpg", d / "00000.jpg")
        out[name] = (d.resolve().as_uri(), len(list(d.glob("*.jpg"))))
    return out


def render_shot(lec, shot, tl, lang, work: Path, quality: str, voice_backend: str) -> Path:
    spec = {"kind": shot.kind, "lang": lang, "total": tl["total"], "steps": tl["steps"],
            "part": lec.t(shot.data.get("part", ""), lang), "head": lec.t(shot.data.get("head", ""), lang)}
    d = shot.data
    if shot.kind == "title":
        spec.update(course=lec.t(COURSE.get(lec.book, [lec.book, lec.book]), lang), chapter=lec.t(lec.data.get("chapter", ""), lang),
                    title=lec.t(lec.data["title"], lang), no=lecture_no(lec, lang), voice_note=lec.t(VOICE_NOTE[voice_backend], lang))
    elif shot.kind == "slide":
        items = []
        for it in d["items"]:
            it = dict(it)
            if "img" in it:
                it["img"] = figure(lec, it["img"], lang, work)
            if "text" in it:
                it["text"] = lec.t(it["text"], lang)
            items.append(it)
        spec["items"] = items
    elif shot.kind == "code":
        src = (lec.code_dir / f"{d['src']}.py").read_text(encoding="utf-8").splitlines()
        start = next((i for i, l in enumerate(src) if d.get("from") and d["from"] in l), 0)
        body, skip = [], False
        for l in src[start:]:
            if not l.strip() or l.lstrip().startswith("#"):
                continue
            if l.startswith("out("):          # bookout lines only feed the book; the output is shown below instead
                skip = l.count("(") > l.count(")")
                continue
            if skip:
                skip = not l.rstrip().endswith(")")
                continue
            body.append(re.sub(r"\s+#.*$", "", l).rstrip())
        if lang == "en":
            body = [re.sub(r"#.*[一-鿿].*$", "", l).rstrip() for l in body]
            body = [l for l in body if l.strip()]
        spec.update(source="\n".join(body), result=d.get("result", []))
    elif shot.kind == "homework" and lec.web:
        ex = S.assignment(lec, d["items"], lang)
        rows = [[f"{i}", k, txt.replace("`", "")] for i, (k, txt) in ex.items()]
        spec.update(items=rows, head=lec.t(["本讲作业", "Assignment"], lang),
                    foot=lec.t(d.get("foot") or ["另：本讲实验的实验报告。在问渠学习平台提交。",
                                                 "Plus the lab report for this lecture. Submit on WenQuest."], lang))
    elif shot.kind == "homework":
        ex = S.exercises(lec, d["items"])
        ex_en = S.exercises_en(lec, d["items"]) if lang == "en" else {}
        kinds_en = {"计算": "Compute", "证明": "Prove", "编程": "Code", "机器人": "Robotics", "判断": "Decide"}
        rows = []
        for i in d["items"]:
            if lang == "en":
                k, txt = ex_en.get(i, (kinds_en.get(ex[i][0], ex[i][0]), None))
                txt = txt or (d.get("en_text") or {}).get(i) or ex[i][1]
            else:
                k, txt = ex[i]
            rows.append([i, k, txt.replace("`", "")])
        spec.update(items=rows, head=lec.t(["本讲作业", "Exercises"], lang),
                    foot=lec.t(["另：实验 14.2 实验报告。在问渠平台提交，AI 当场反馈。".replace("14.2", lec.section),
                                f"Plus the report for Lab {lec.section}. Submit on WenQuest for instant AI feedback."], lang))
    elif shot.kind == "outro":
        tl_lines = tl["lines"]
        n = len(d["points"])
        spec.update(head=lec.t(["小结", "Summary"], lang), points=[lec.t(p, lang) for p in d["points"]],
                    cta=lec.t(["问渠学习平台 · 免费注册", "learn.wenquestrobotics.com"], lang),
                    cta2=lec.t(["实验 · 程序 · 讲义 · 作业 · AI 反馈", "Labs · programs · notes · exercises · instant AI feedback"], lang),
                    cta_at=max(0.5, tl_lines[n]["start"] - LEAD) if len(tl_lines) > n else tl["total"] - 3)
    key = h([spec, (HERE / "slides.py").read_text(encoding="utf-8"), quality] + ([d, (HERE / "labrec.py").read_text(encoding="utf-8")] if shot.kind in ("lab", "clip", "deck") else []))   # 实验镜头：步骤或录屏程序变了要重录
    out = work / "shots" / f"{shot.id}.{lang}.{key}.mp4"
    if out.exists():
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    if shot.kind in ("title", "slide", "code", "homework", "outro"):
        js = work / f"spec_{shot.id}_{lang}.json"
        js.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        raw = manim(HERE / "slides.py", "Shot", {"WQ_SHOT_SPEC": str(js), "WQ_LAYOUT_LOG": str(work / f"layout_{lang}.log")}, work, quality)
    elif shot.kind == "anim":
        tmp = work / "anim" / f"{d['src']}_{lang}"
        tmp.mkdir(parents=True, exist_ok=True)
        shutil.copy(lec.ch_dir / "anim" / f"{d['src']}.py", tmp / "scene.py")
        base = (ROOT / "services" / "animator" / "wq_anim.py").read_text(encoding="utf-8")
        (tmp / "wq_anim.py").write_text(base + ANIM_PATCH, encoding="utf-8")
        js = tmp / "sync.json"
        js.write_text(json.dumps({"lang": lang, "marks": tl["steps"]}), encoding="utf-8")
        raw = manim(tmp / "scene.py", "Lesson", {"WQ_ANIM_SYNC": str(js)}, tmp, quality)
    elif shot.kind == "deck":
        # 第 25 轮：画面就是网页互动课件（中文版双语、英文版只显示英文），翻到这一页，每个 “>” 出现下一个要点，最后一个 “>” 出现全部
        import labrec
        deck = work / f"deck_{lang}" / "deck.html"
        if not deck.exists():
            sys.path.insert(0, str(lec.web / "course" / "tools"))
            import build_slides
            build_slides.make_deck(lec.data["deck"], deck.parent, lang, extra=lec.data.get("deck_extra"), name="deck.html",
                                   stills=deck_stills(lec, lang, work))
        nxt = "(()=>{const f=document.querySelector('.slide.on .frag:not(.on)');if(f)f.classList.add('on')})()"
        rest = "document.querySelectorAll('.slide.on .frag').forEach(f=>f.classList.add('on'))"
        k = len(tl["steps"])
        steps = [{"js": nxt} for _ in range(max(0, k - 1))] + ([{"js": rest}] if k else [])
        raw = work / "shots" / f"deck_{shot.id}_{lang}.mp4"
        labrec.run(deck.resolve().as_uri() + f"?video=1#{d['slide']}", "deck", steps, tl["steps"], tl["total"], raw,
                   standalone=True, viewport=(1920, 1080), fps=15)
        fit_length(raw, tl["total"], out)
        return out
    elif shot.kind == "lab":
        import labrec
        if lec.web:                               # 网页版教材：实验、动画、三维页各是一个独立网页，直接打开源文件（库按相对路径加载）
            page = lec.web / "src" / lang / "labs" / f"{d['lab']}.html"
            if d.get("book"):                     # 录网页版教材本身（平台“教材”书架上的那本书）：先构建一次
                webed = work / "webed"
                if not (webed / "index.html").exists():
                    sh(sys.executable, lec.web / "build.py", webed, cwd=lec.web, capture_output=True)
                page = webed / ("en" if lang == "en" else "") / f"ch{lec.chapter_no:02d}.html"
            if not page.exists():
                raise S.ScriptError(f"找不到实验页 {page}")
            raw = work / "shots" / f"lab_{shot.id}_{lang}.mp4"
            manual = "manual:on=>" in page.read_text(encoding="utf-8")      # 三维页：逐帧手动推进；网页实验一律 15 帧/秒录，合成时补成 30 帧
            labrec.run(page.resolve().as_uri() + (d.get("query") or ""), d["lab"], d.get("steps") or [], tl["steps"], tl["total"], raw,
                       standalone=True, viewport=tuple(d.get("viewport") or (1280, 720)), manual=manual, fps=15)
            fit_length(raw, tl["total"], out)
            return out
        page = S.TEXTBOOK / "build" / lec.book / "lab" / f"ch{lec.chapter_no:02d}.html"
        if not page.exists():
            raise S.ScriptError(f"找不到实验页 {page}（先构建：python3 textbook/tools/build.py {lec.book} --labs）")
        lab = d["lab"]
        url = page.resolve().as_uri() + f"#lab-{lab}" + ("-en" if lang == "en" else "")
        raw = work / "shots" / f"lab_{shot.id}_{lang}.mp4"
        labrec.run(url, lab, d.get("steps") or [], tl["steps"], tl["total"], raw)
    elif shot.kind == "clip":
        src = Path(os.environ.get("WQ_FOOTAGE", ROOT / "docs" / "课程视频" / "素材")) / d["src"]
        if not src.exists():
            print(f"！ 缺少录屏素材 {src}，用占位画面", file=sys.stderr)
            js = work / f"spec_{shot.id}_{lang}.json"
            js.write_text(json.dumps({**spec, "kind": "slide", "items": [{"text": lec.t(["（数字工厂录屏素材待补：" + d["src"] + "）",
                                                                                          "(digital-factory footage to come: " + d["src"] + ")"], lang)}],
                                      "steps": tl["steps"][:1]}, ensure_ascii=False), encoding="utf-8")
            raw = manim(HERE / "slides.py", "Shot", {"WQ_SHOT_SPEC": str(js)}, work, quality)
        else:
            raw = src
    else:
        raise S.ScriptError(f"unknown kind {shot.kind}")
    fit_length(raw, tl["total"], out)
    return out


def lecture_no(lec, lang):
    if lec.web:
        return f"第 {lec.section} 讲" if lang == "zh" else f"Lecture {lec.section}"
    c, k = lec.section.split(".")
    return f"第 {c} 章 · 第 {k} 讲" if lang == "zh" else f"Chapter {c} · Lecture {k}"


# ---------------------------------------------------------------- subtitles, audio, compose
def pieces(text: str, lang: str, spoken_len: float):
    """Split a long subtitle into screen-sized pieces at punctuation; returns [(text, share)]."""
    limit = 30 if lang == "zh" else 78
    if len(text) <= limit:
        return [(text, 1.0)]
    seps = r"(?<=[，。；：？！,;:?!])\s*" if lang == "zh" else r"(?<=[,;:.?!])\s+"
    parts, cur = [], ""
    for seg in re.split(seps, text):
        if not seg:
            continue
        if cur and len(cur) + len(seg) > limit:
            parts.append(cur)
            cur = seg
        else:
            cur = (cur + ("" if lang == "zh" else " ") + seg).strip() if cur else seg
    if cur:
        parts.append(cur)
    out = []
    for p in parts:            # still too long (no punctuation): hard split
        while len(p) > limit + 6:
            cut = limit if lang == "zh" else p.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            out.append(p[:cut].strip())
            p = p[cut:].strip()
        out.append(p)
    tot = sum(len(x) for x in out) or 1
    return [(x, len(x) / tot) for x in out]


def ts_srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ts_ass(t):
    cs = int(round(t * 100))
    return f"{cs // 360000:d}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def compose(lec, lang, tls, shot_files, out_dir: Path, work: Path, voice_backend: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    # absolute times
    t0, events, chapters, offsets = 0.0, [], [], []
    for s, tl in zip(lec.shots, tls):
        offsets.append(t0)
        part = lec.t(s.data.get("part", ""), lang) if s.data.get("part") else ""
        if s.kind == "title":
            part = lec.t(["开场", "Intro"], lang)
        if s.kind == "homework":
            part = lec.t(["作业", "Homework"], lang)
        if s.kind == "outro":
            part = lec.t(["小结", "Summary"], lang)
        if part and (not chapters or chapters[-1][1] != part):
            chapters.append((t0, part))
        for ln in tl["lines"]:
            a, b = t0 + ln["start"], t0 + ln["end"]
            span = b - a
            x = a
            for txt, share in pieces(ln["shown"], lang, span):
                events.append((x, x + span * share, txt))
                x += span * share
        t0 += tl["total"]
    total = t0
    # audio
    rate = V.RATE
    track = np.zeros(int((total + 0.5) * rate), np.float32)
    for off, tl in zip(offsets, tls):
        for ln in tl["lines"]:
            a = V.wav_read(Path(ln["wav"]))
            i = int((off + ln["start"]) * rate)
            track[i:i + len(a)] += a[: max(0, len(track) - i)]
    aw = work / f"voice_{lang}.wav"
    pcm = (np.clip(track, -1, 1) * 32767).astype("<i2")
    with wave.open(str(aw), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    # subtitles
    srt = out_dir / "lecture.srt"
    srt.write_text("\n".join(f"{i + 1}\n{ts_srt(a)} --> {ts_srt(b - 0.02)}\n{t}\n" for i, (a, b, t) in enumerate(events)), encoding="utf-8")
    size = 50 if lang == "zh" else 44
    ass = work / f"subs_{lang}.ass"
    ass.write_text(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Sub,{FONT_ZH},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,4,0,0,2,260,260,34,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        + "".join(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b - 0.02)},Sub,,0,0,0,,{t}\n" for a, b, t in events), encoding="utf-8")
    # concat pictures
    lst = work / f"concat_{lang}.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in shot_files), encoding="utf-8")
    pic = work / f"picture_{lang}.mp4"
    sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", pic)
    mark = "问渠 WenQuest" if lang == "zh" else "WenQuest"
    fontfile = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    vf = (f"subtitles={ass}:fontsdir=/usr/share/fonts/opentype/noto,"
          f"drawtext=fontfile={fontfile}:text='{mark}':fontcolor=white@0.45:fontsize=26:x=w-tw-36:y=h-th-30")
    mp4 = out_dir / "lecture.mp4"
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", pic, "-i", aw, "-vf", vf,
       "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", mp4)
    tl_out = {"total": total, "chapters": chapters, "shots": [{"id": s.id, "start": o, **tl} for s, o, tl in zip(lec.shots, offsets, tls)]}
    (out_dir / "timeline.json").write_text(json.dumps(tl_out, ensure_ascii=False, indent=1), encoding="utf-8")
    return mp4, chapters, total


def mmss(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}" if t < 3600 else f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}"


def covers_talk(mp4: Path, out_dir: Path):
    """演讲稿（第 44 轮：行业解决方案介绍片）：封面取片头那一页（活的三维样机）的画面"""
    png = out_dir / "cover.png"
    sh("ffmpeg", "-y", "-loglevel", "error", "-ss", "4", "-i", mp4, "-frames:v", "1", png)
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", png, "-vf", "scale=1280:720", out_dir / "cover_youtube.png")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", png, "-vf", "scale=1146:645,pad=1146:717:0:36:color=0x0f1419", out_dir / "cover_bilibili.png")


def upload_text_talk(lec, lang, chapters, total, voice_backend, out_dir):
    d = lec.data
    t = lec.t(d["title"], lang)
    desc = [lec.t(d.get("desc", ["", ""]), lang), "", "章节：" if lang == "zh" else "Chapters:"] + [f"{mmss(a)} {p}" for a, p in chapters] + [
        "", lec.t(VOICE_NOTE[voice_backend], lang) + ("。数字均由问渠缝纫机设计软件的计算核心算出。" if lang == "zh" else ".")]
    tags = list((d.get("tags") or {}).get(lang, []))
    extra = ["分区：知识 → 职业职场", "投稿时勾选“作者声明：使用 AI 合成技术”（配音）"] if lang == "zh" else ["Altered or synthetic content: Yes (AI voice)"]
    md = [f"# {t}", "", "## 标题", t, "", "## 简介", *desc, "", "## 标签", ", ".join(tags), "", "## 设置", *[f"- {x}" for x in extra],
          "", f"<!-- length {mmss(total)} -->"]
    (out_dir / "upload.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out_dir / "upload.json").write_text(json.dumps({"title": t, "description": "\n".join(desc), "tags": tags, "lang": lang},
                                                    ensure_ascii=False, indent=1), encoding="utf-8")


def covers(lec, lang, work, out_dir, quality):
    spec = {"kind": "cover", "lang": lang, "total": 0.05, "steps": [],
            "course": lec.t(COURSE.get(lec.book, [lec.book, lec.book]), lang), "title": lec.t(lec.data["title"], lang),
            "no": lecture_no(lec, lang), "formula": lec.data.get("cover_formula", "")}
    js = work / f"spec_cover_{lang}.json"
    js.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    exe = os.environ.get("WQ_MANIM", "manim")
    media = work / "media_cover"
    sh(exe, "-qh", "-r", "1920,1080", "-s", "--disable_caching", "--media_dir", media, "--progress_bar", "none",
       HERE / "slides.py", "Shot", env={**os.environ, "WQ_SHOT_SPEC": str(js)}, cwd=HERE, capture_output=True)
    png = sorted(media.rglob("*.png"), key=lambda p: p.stat().st_mtime)[-1]
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", png, "-vf", "scale=1280:720", out_dir / "cover_youtube.png")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", png, "-vf", "scale=1146:645,pad=1146:717:0:36:color=0x0f1419", out_dir / "cover_bilibili.png")


UPLOAD = {   # 网页版教材的标题、标签、合集（第 23 轮）
    "sewing": {"zh": {"title": "缝纫机设计与制造 第 {n} 讲｜{t}", "tags": ["缝纫机", "机械设计", "机构", "服装机械", "智能制造", "机器人", "工科", "问渠"],
                      "list": "缝纫机设计与制造（问渠公开课）", "next": "下一讲"},
               "en": {"title": "Sewing Machine Design {n:02d} | {t}", "tags": ["sewing machine", "mechanism design", "mechanical engineering",
                                                                               "garment machinery", "manufacturing", "robotics", "WenQuest"],
                      "list": "Sewing Machine Design and Manufacturing (WenQuest)", "next": "Next"}}}


def _web_courses():
    """第 29 轮：其他网页版教材的课名和上传文字写在各书 course/course.yaml（name、upload）"""
    import yaml
    for p in sorted((ROOT / "textbook" / "web-editions").glob("*/course/course.yaml")):
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        book = cfg.get("book") or p.parents[1].name
        if cfg.get("name"):
            COURSE.setdefault(book, cfg["name"])
        if cfg.get("upload"):
            UPLOAD.setdefault(book, cfg["upload"])


_web_courses()

def upload_text_web(lec, lang, chapters, total, voice_backend, out_dir):
    u = UPLOAD[lec.book][lang]
    title = lec.t(lec.data["title"], lang)
    t = u["title"].format(n=int(lec.section), t=title)
    course = lec.t(COURSE[lec.book], lang)
    if lang == "zh":
        desc = [f"问渠 WenQuest · {course} · 第 {lec.section} 讲",
                "本讲的虚拟实验、三维样机、讲义、作业和整本网页版教材都在问渠学习平台，免费注册即可学习：https://learn.wenquestrobotics.com",
                "", "章节："] + [f"{mmss(a)} {p}" for a, p in chapters] + [
                "", lec.t(VOICE_NOTE[voice_backend], lang) + "。字幕与讲稿一致，数字均由配套程序计算。",
                f"下一讲：{lec.t(lec.data.get('next', ''), lang)}"]
        extra = ["分区：知识 → 校园学习", "投稿时勾选“作者声明：使用 AI 合成技术”（配音）", f"合集：{u['list']}"]
    else:
        desc = [f"WenQuest · {course} · Lecture {lec.section}",
                "The virtual labs, 3D prototype, notes, assignment and the whole web textbook for this lecture are free on WenQuest: https://learn.wenquestrobotics.com",
                "", "Chapters:"] + [f"{mmss(a)} {p}" for a, p in chapters] + [
                "", lec.t(VOICE_NOTE[voice_backend], lang) + ". Every number shown is computed by the companion program.",
                f"Next: {lec.t(lec.data.get('next', ''), lang)}"]
        extra = ["Category: Education", "Altered or synthetic content: Yes (AI voice)", f"Playlist: {u['list']}"]
    tags = u["tags"] + [x for x in (lec.data.get("tags") or {}).get(lang, [])]
    md = [f"# {t}", "", "## " + ("标题" if lang == "zh" else "Title"), t, "", "## " + ("简介" if lang == "zh" else "Description"), *desc,
          "", "## " + ("标签" if lang == "zh" else "Tags"), ", ".join(tags), "", "## " + ("设置" if lang == "zh" else "Settings"), *[f"- {x}" for x in extra],
          "", f"<!-- length {mmss(total)} -->"]
    (out_dir / "upload.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out_dir / "upload.json").write_text(json.dumps({"title": t, "description": "\n".join(desc), "tags": tags, "lang": lang,
                                                     "playlist": u["list"]}, ensure_ascii=False, indent=1), encoding="utf-8")


def upload_text(lec, lang, chapters, total, voice_backend, out_dir):
    if lec.web:
        return upload_text_web(lec, lang, chapters, total, voice_backend, out_dir)
    c, k = lec.section.split(".")
    course = lec.t(COURSE.get(lec.book, [lec.book, lec.book]), lang)
    title = lec.t(lec.data["title"], lang)
    if lang == "zh":
        t = f"{course} {c}.{k}　{title}｜机器人工程师的{course}"
        desc = [f"问渠 WenQuest · {course} · {lec.t(lec.data.get('chapter', ''), lang)}",
                "本讲配套的虚拟实验、程序、讲义和作业（AI 即时反馈）在问渠学习平台，免费注册即可学习：https://learn.wenquestrobotics.com",
                "", "章节："] + [f"{mmss(a)} {p}" for a, p in chapters] + [
                "", lec.t(VOICE_NOTE[voice_backend], lang) + "。字幕与讲稿一致，书中数字均由配套程序计算。",
                f"下一讲：{lec.t(lec.data.get('next', ''), lang)}"]
        tags = ["线性代数", "机器人", "谱定理", "对称矩阵", "特征值", "大学数学", "工科数学", "问渠"]
        extra = ["分区：知识 → 校园学习", "投稿时勾选“作者声明：使用 AI 合成技术”（配音）", "合集：线性代数（问渠公开课）"]
    else:
        t = f"{course} {c}.{k}: {title} | Linear Algebra for Robotics Engineers"
        desc = [f"WenQuest · {course} · {lec.t(lec.data.get('chapter', ''), lang)}",
                "The virtual lab, programs, notes and exercises (with instant AI feedback) for this lecture are free on WenQuest: https://learn.wenquestrobotics.com",
                "", "Chapters:"] + [f"{mmss(a)} {p}" for a, p in chapters] + [
                "", lec.t(VOICE_NOTE[voice_backend], lang) + ". Every number shown is computed by the companion program.",
                f"Next: {lec.t(lec.data.get('next', ''), lang)}"]
        tags = ["linear algebra", "robotics", "spectral theorem", "symmetric matrix", "eigenvalues", "engineering math", "WenQuest"]
        extra = ["Category: Education", "Altered or synthetic content: Yes (AI voice)", "Playlist: Linear Algebra (WenQuest)"]
    md = [f"# {t}", "", "## " + ("标题" if lang == "zh" else "Title"), t, "", "## " + ("简介" if lang == "zh" else "Description"), *desc,
          "", "## " + ("标签" if lang == "zh" else "Tags"), ", ".join(tags), "", "## " + ("设置" if lang == "zh" else "Settings"), *[f"- {x}" for x in extra],
          "", f"<!-- length {mmss(total)} -->"]
    (out_dir / "upload.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out_dir / "upload.json").write_text(json.dumps({"title": t, "description": "\n".join(desc), "tags": tags, "lang": lang},
                                                    ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lecture")
    ap.add_argument("--lang", default="both", choices=["zh", "en", "both"])
    ap.add_argument("--voice", default="estimate", choices=["estimate", "kokoro", "clone"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="", help="只渲染这些镜头（逗号分隔），试看用，不合成")
    ap.add_argument("--quality", default="h", choices=["h", "l"])
    a = ap.parse_args()
    lec = S.load(a.lecture)
    out = Path(a.out)
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    only = set(x for x in a.only.split(",") if x)
    for lang in (["zh", "en"] if a.lang == "both" else [a.lang]):
        voice = V.Voice(a.voice, lang, work / "voice")
        tls = timeline(lec, lang, voice)
        files = []
        for s, tl in zip(lec.shots, tls):
            if only and s.id not in only:
                continue
            f = render_shot(lec, s, tl, lang, work, a.quality, a.voice)
            print(f"{lang} {s.id:14s} {tl['total']:6.1f}s  {f.name}", flush=True)
            files.append(f)
        if only:
            continue
        d = out / lang
        mp4, chapters, total = compose(lec, lang, tls, files, d, work, a.voice)
        if lec.data.get("talk"):
            covers_talk(mp4, d)
            upload_text_talk(lec, lang, chapters, total, a.voice, d)
        else:
            covers(lec, lang, work, d, a.quality)
            upload_text(lec, lang, chapters, total, a.voice, d)
        print(f"{lang}: {mp4}  {mmss(total)}", flush=True)


if __name__ == "__main__":
    main()
