"""问渠白板讲课（第 35 轮）：本机出片与看样。核心在 services/gateway/app/production/whiteboard/（网关也用它）。

    python3 tools/whiteboard/wb.py <课目录>            # 读 <课目录>/lesson.json，写 board.excalidraw、data.json、白板课.html
    python3 tools/whiteboard/wb.py <课目录> --scene    # 从（老师改过的）board.excalidraw 编译
    python3 tools/whiteboard/wb.py <课目录> --mp4      # 另出 白板课.mp4（1920×1080，30 帧/秒）
"""
import base64
import os
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "services" / "gateway"))
from app.production.whiteboard.core import *  # noqa: E402,F401,F403
from app.production.whiteboard.core import compile_lesson, compile_scene, excalidraw, page, W, H  # noqa: E402

HERE = Path(__file__).resolve().parent   # (the star import above brought core's HERE)
HAND = HERE / "assets"   # Eddie's hand photo, kept out of the public repository


REPO = HERE.parent.parent


def local_media(src: str):
    """Media frames for local samples: lab:<书>/<章.节> → the built textbook's lab page; video:<file> → the file inline."""
    kind, _, ref = src.partition(":")
    if kind == "lab":
        book, _, no = ref.partition("/")
        ch = no.split(".")[0]
        p = REPO / "textbook" / "build" / book / "lab" / f"ch{int(ch):02d}.html"
        if p.exists():
            return {"kind": "page", "html": p.read_text(encoding="utf-8"), "hash": "lab-" + no.replace(".", "-"), "zoom": 1.0}
    if kind == "video":
        p = Path(ref)
        if p.exists():
            # the recorder's Chromium cannot decode H.264: use WebM (VP9) clips for frames that must show in the MP4
            mime = "video/webm" if p.suffix == ".webm" else "video/mp4"
            return {"kind": "video", "url": f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()}
    print("media not found:", src)
    return None


def srt(d, segs):
    """One subtitle file for uploading with the video (sites take only one): 字幕.srt, each cue
    the narration line and, when the segments have English, the English line under it."""
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    for old in ("字幕.zh.srt", "字幕.en.srt"):
        (d / old).unlink(missing_ok=True)
    out = []
    for i, s in enumerate(segs, 1):
        end = s["t1"] + 0.35
        if i < len(segs):
            end = min(end, segs[i]["t0"])
        lines = [s.get("text") or s.get("zh") or ""]
        if s.get("en") and s.get("en") != lines[0]:
            lines.append(s["en"])
        out.append(f"{i}\n{ts(s['t0'])} --> {ts(end)}\n" + "\n".join(lines) + "\n\n")
    (d / "字幕.srt").write_text("".join(out), encoding="utf-8")


def build(lesson_dir, mp4=False):
    d = Path(lesson_dir)
    L = json.loads((d / "lesson.json").read_text())
    data, ex = compile_lesson(L, local_media)
    (d / "data.json").write_text(json.dumps(data, ensure_ascii=False))
    (d / "board.excalidraw").write_text(json.dumps(excalidraw(L, ex), ensure_ascii=False))
    audio = d / L["audio"]
    web_audio = d / "_web.mp3"   # MP3: every browser plays it (open-source Chromium has no AAC)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-vn", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(web_audio)], check=True)
    b64 = base64.b64encode(web_audio.read_bytes()).decode()
    pen = L.get("hand", True)          # lesson.json "hand": false → no hand
    (d / "白板课.html").write_text(page(data, L["title"], b64, "audio/mpeg", hand_dir=HAND, pen=pen))
    (d / "_render.html").write_text(page(data, L["title"], render=True, hand_dir=HAND, pen=pen, subs=bool(L.get("subs"))))
    srt(d, L["segments"])
    print(f"{len(L['boards'])} boards, {len(data['items'])} strokes, {data['total']} s → {d / '白板课.html'}")
    if mp4:
        render_mp4(d, data, audio)


def build_scene(lesson_dir, mp4=False):
    """lesson.json (segments, audio) + board.excalidraw (edited) → web page / MP4."""
    d = Path(lesson_dir)
    L = json.loads((d / "lesson.json").read_text())
    scene = json.loads((d / "board.excalidraw").read_text())
    data = compile_scene(scene, L["segments"], L.get("duration", 0))
    (d / "data.json").write_text(json.dumps(data, ensure_ascii=False))
    (d / "_render.html").write_text(page(data, L["title"], render=True, hand_dir=HAND))
    print(f"scene: {len(data['boards'])} boards, {len(data['items'])} strokes, {data['total']} s")
    if mp4:
        render_mp4(d, data, d / L["audio"])
    return data


def render_mp4(d, data, audio, fps=30, start=0.0, end=None, progress=None):
    from playwright.sync_api import sync_playwright
    end = end or data["total"]
    out = d / "白板课.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                           "-ss", str(start), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                           "-crf", os.environ.get("WB_CRF", "21"), "-preset", "medium", "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": W, "height": H})
        p.goto((d / "_render.html").resolve().as_uri())
        n = int((end - start) * fps)
        for i in range(n):
            p.evaluate(f"WB.seek({start + i / fps})")
            p.evaluate("WB.settle()")      # videos in frames show the asked moment
            try:
                ff.stdin.write(p.screenshot(type="jpeg", quality=90))
            except BrokenPipeError:   # -shortest: ffmpeg is done once the narration ends
                break
            if i % 900 == 0:
                print(f"  frame {i}/{n}", flush=True)
            if progress and i % 30 == 0:
                progress(round(100 * i / n))
        b.close()
    try:
        ff.stdin.close()
    except BrokenPipeError:
        pass
    ff.wait()
    print("→", out)


if __name__ == "__main__":
    if "--scene" in sys.argv:
        build_scene(sys.argv[1], "--mp4" in sys.argv)
    else:
        build(sys.argv[1], "--mp4" in sys.argv)
