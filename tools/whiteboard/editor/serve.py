"""白板课编辑器样板服务（第 35 轮第 2 步）：本机打开一节白板课来编辑、预览、换录音、出视频。
接进平台后这些接口由网关提供（路径相同），这个文件只用于看样和本机制作。

    python3 tools/whiteboard/editor/serve.py <课目录> [--port 8765]      然后浏览器打开 http://127.0.0.1:8765/

语音识别用本机的 SenseVoice 模型（目录由环境变量 WB_MODELS 指定，里面有 sense-voice 模型和 silero_vad.onnx；
平台上用语音服务 services/voice 的 /asr）。"""
import difflib
import json
import os
import subprocess
import sys
import threading
import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import wb  # noqa: E402

LESSON = Path(sys.argv[1]).resolve()
PORT = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
MODELS = Path(os.environ.get("WB_MODELS", "/models"))
app = FastAPI()
JOBS = {}


def load():
    return json.loads((LESSON / "lesson.json").read_text())


@app.get("/api/lesson")
def lesson():
    L = load()
    scene = json.loads((LESSON / "board.excalidraw").read_text())
    return {"title": L["title"], "segments": L["segments"], "audio": "api/file/" + preview_audio(L["audio"]), "scene": scene}


def preview_audio(name):
    """MP3 copy of the recording for the browser (every browser plays MP3; open-source Chromium has no AAC)."""
    src, out = LESSON / name, LESSON / "_preview.mp3"
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(out)], check=True)
    return out.name


@app.post("/api/save")
async def save(req: Request):
    body = await req.json()
    L = load()
    L["title"], L["segments"] = body.get("title", L["title"]), body["segments"]
    (LESSON / "lesson.json").write_text(json.dumps(L, ensure_ascii=False, indent=1))
    (LESSON / "board.excalidraw").write_text(json.dumps(body["scene"], ensure_ascii=False))
    return {"ok": True}


@app.post("/api/compile")
async def compile_(req: Request):
    body = await req.json()
    return wb.compile_scene(body["scene"], body["segments"], load().get("duration", 0))


@app.get("/api/file/{name}")
def file(name: str):
    p = (LESSON / name).resolve()
    if p.parent != LESSON or not p.is_file():
        raise HTTPException(404)
    return FileResponse(p)


# ---- new recording: speech recognition → segments; the boards keep their drawings, matched to the new words
_asr = None


def asr(wav):
    global _asr
    import numpy as np
    import sherpa_onnx as so
    import soundfile as sf
    if _asr is None:
        m = next(MODELS.glob("sherpa-onnx-sense-voice-*"))
        rec = so.OfflineRecognizer.from_sense_voice(model=str(m / "model.int8.onnx"), tokens=str(m / "tokens.txt"), use_itn=True, language="auto")
        _asr = rec
    cfg = so.VadModelConfig()
    cfg.silero_vad.model = str(MODELS / "silero_vad.onnx")
    cfg.silero_vad.min_silence_duration = 0.45
    cfg.silero_vad.max_speech_duration = 15
    cfg.sample_rate = 16000
    vad = so.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)
    a, _ = sf.read(wav, dtype="float32")
    out = []

    def drain():
        while not vad.empty():
            seg = vad.front
            s = _asr.create_stream()
            s.accept_waveform(16000, seg.samples)
            _asr.decode_stream(s)
            t0 = seg.start / 16000
            out.append({"t0": round(t0, 2), "t1": round(t0 + len(seg.samples) / 16000, 2), "zh": s.result.text.strip()})
            vad.pop()
    for i in range(0, len(a), 512):
        vad.accept_waveform(a[i:i + 512])
        drain()
    vad.flush()
    drain()
    # join pieces that belong to one sentence (short pause, still short)
    merged = []
    for s in out:
        if not s["zh"]:
            continue
        if merged and s["t0"] - merged[-1]["t1"] < 0.5 and len(merged[-1]["zh"]) + len(s["zh"]) < 28 and not merged[-1]["zh"].endswith(("。", "？", "！")):
            merged[-1]["t1"] = s["t1"]
            merged[-1]["zh"] += "，" + s["zh"] if not merged[-1]["zh"].endswith(("，", "、")) else s["zh"]
        else:
            merged.append(dict(s))
    return merged, len(a) / 16000


def remap(old, new):
    """old segment index → new segment index, by matching the words (re-recordings rarely split sentences the same way)."""
    a = "".join(s["zh"] for s in old)
    b = "".join(s["zh"] for s in new)
    a_start, pos = [], 0
    for s in old:
        a_start.append(pos)
        pos += len(s["zh"])
    b_owner = []
    for i, s in enumerate(new):
        b_owner += [i] * len(s["zh"])
    cmap = {}
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            cmap[blk.a + k] = blk.b + k
    out = []
    for i, st in enumerate(a_start):
        end = a_start[i + 1] if i + 1 < len(a_start) else len(a)
        hits = [cmap[c] for c in range(st, end) if c in cmap]
        if hits and b_owner:
            out.append(b_owner[min(hits[0], len(b_owner) - 1)])
        else:   # no matching words: same relative position
            out.append(round(i * (len(new) - 1) / max(1, len(old) - 1)))
    return out


@app.post("/api/audio")
async def audio(file: UploadFile = File(...)):
    ext = Path(file.filename or "a.m4a").suffix.lower() or ".m4a"
    name = "录音" + ext
    raw = LESSON / ("_upload" + ext)
    raw.write_bytes(await file.read())
    wav = LESSON / "_asr.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    new, seconds = asr(str(wav))
    if not new:
        raise HTTPException(422, "录音里没听出说话")
    L = load()
    scene = json.loads((LESSON / "board.excalidraw").read_text())
    m = remap(L["segments"], new)
    at = 0
    for e in scene["elements"]:
        if e.get("type") == "frame" or e.get("isDeleted"):
            continue
        cd = e.get("customData") or {}
        if isinstance(cd.get("wq_at"), int):
            at = cd["wq_at"]
        cd["wq_at"] = m[min(at, len(m) - 1)]
        e["customData"] = cd
    raw.rename(LESSON / name)
    L.update(segments=new, audio=name, duration=round(seconds + 1.5, 2))
    (LESSON / "lesson.json").write_text(json.dumps(L, ensure_ascii=False, indent=1))
    (LESSON / "board.excalidraw").write_text(json.dumps(scene, ensure_ascii=False))
    return {"segments": new, "scene": scene, "audio": "api/file/" + preview_audio(name)}


# ---- MP4 (the platform queues this on the server; here a thread)
@app.post("/api/render")
async def render(req: Request):
    body = await req.json()
    L = load()
    data = wb.compile_scene(body["scene"], body["segments"], L.get("duration", 0))
    job = uuid.uuid4().hex[:8]
    JOBS[job] = {"state": "running", "progress": 0}
    (LESSON / "_render.html").write_text(wb.page(data, L["title"], render=True))

    def run():
        try:
            wb.render_mp4(LESSON, data, LESSON / L["audio"], progress=lambda p: JOBS[job].update(progress=p))
            JOBS[job] = {"state": "done", "url": "api/file/白板课.mp4"}
        except Exception as e:  # noqa: BLE001
            JOBS[job] = {"state": "failed", "error": str(e)[:300]}
    threading.Thread(target=run, daemon=True).start()
    return {"job": job}


@app.get("/api/render/{job}")
def render_state(job: str):
    return JOBS.get(job) or JSONResponse({"state": "failed", "error": "no such job"}, 404)


app.mount("/", StaticFiles(directory=HERE / "dist", html=True), name="editor")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
