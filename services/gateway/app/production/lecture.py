"""讲解视频 (round 4, step 5): one lecture video per lesson, with a Chinese and an English voice track and subtitles.

Two sources, one result:
  B. AI 讲解: the lecturer writes what to say on every slide (Chinese and English); the voice service speaks it
     sentence by sentence; the slides (and the animation on its slide) are laid on a timeline that fits the longer
     language, so both voice tracks share one picture track.
  A. 老师亲讲: the teacher's recording is the picture and the Chinese voice; speech recognition gives the Chinese
     subtitles with their times, the AI translates them, and the English voice is spoken into the same times.

What comes out (in the lesson's `lecture/` folder): zh.mp4 and en.mp4 (same picture, different voice), zh.vtt and
en.vtt, poster.jpg and script.json. The player switches voice by switching file at the same moment.
Everything here is blocking (ffmpeg, numpy); callers run it in a thread.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

W, H, FPS = 1280, 720, 30
RATE = 24000          # voice service output
HEAD, PAUSE, TAIL = 0.5, 0.3, 0.9     # seconds: before the first sentence, between sentences, after the last
MAX_BYTES = 190 * 1024 * 1024        # one file must fit Moodle's upload limit (200 MB)
ZH_MAX, EN_MAX = 40, 110             # subtitle line lengths (characters)


class LectureError(Exception):
    pass


# --- text ---------------------------------------------------------------------------------------------------------

def speakable(text: str) -> str:
    """What the voice can read: no markup, formula signs spelled out simply, spaces normalised."""
    t = str(text or "")
    t = re.sub(r"\\\(|\\\)|\\\[|\\\]|\$", "", t)
    t = re.sub(r"\\([a-zA-Z]+)", r"\1", t)          # \theta -> theta
    t = re.sub(r"[*_#`^{}|<>\[\]]", " ", t)
    t = t.replace("→", "，").replace("≈", "约等于" if re.search(r"[一-鿿]", t) else " about ")
    return " ".join(t.split())


def _chunks(s: str, limit: int, soft: str) -> list[str]:
    if len(s) <= limit:
        return [s]
    parts = [p for p in re.split(f"(?<=[{soft}])", s) if p]
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > limit:
            out.append(cur)
            cur = ""
        while len(p) > limit * 1.5:            # no soft break at all: cut
            out.append(p[:limit])
            p = p[limit:]
        cur += p
    if cur:
        out.append(cur)
    return [x.strip() for x in out if x.strip()]


def sentences(text: str, lang: str) -> list[str]:
    """Split narration into subtitle-sized sentences, each spoken separately."""
    t = speakable(text)
    if not t:
        return []
    if lang == "zh":
        parts = [p.strip() for p in re.split(r"(?<=[。！？；!?;])", t) if p.strip()]
        return [c for p in parts for c in _chunks(p, ZH_MAX, "，,、：:")]
    parts = [p.strip() for p in re.split(r"(?<=[.!?;])\s+", t) if p.strip()]
    return [c for p in parts for c in _chunks(p, EN_MAX, ",:")]


def key(*parts) -> str:
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode()).hexdigest()[:20]


# --- audio --------------------------------------------------------------------------------------------------------

def read_wav(data: bytes) -> np.ndarray:
    with wave.open(io.BytesIO(data)) as w:
        rate, ch = w.getframerate(), w.getnchannels()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    if rate != RATE:
        n = int(len(a) * RATE / rate)
        a = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
    return a


def write_wav(path: Path, a: np.ndarray, rate: int = RATE) -> None:
    pcm = (np.clip(a, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


def place(track: np.ndarray, clip: np.ndarray, at: float) -> None:
    i = int(round(at * RATE))
    n = min(len(clip), len(track) - i)
    if n > 0:
        track[i:i + n] += clip[:n]


# --- subtitles ----------------------------------------------------------------------------------------------------

def _ts(t: float) -> str:
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def vtt(cues: list[dict]) -> str:
    out = ["WEBVTT", ""]
    for i, c in enumerate(cues, 1):
        out += [str(i), f"{_ts(c['start'])} --> {_ts(c['end'])}", c["text"].replace("\n", " "), ""]
    return "\n".join(out)


def parse_vtt(text: str) -> list[dict]:
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r", "")):
        m = re.search(r"(\d+):(\d{2}):(\d{2}\.\d+)\s*-->\s*(\d+):(\d{2}):(\d{2}\.\d+)\s*\n(.+)", block, re.S)
        if m:
            a = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
            b = int(m[4]) * 3600 + int(m[5]) * 60 + float(m[6])
            cues.append({"start": a, "end": b, "text": m[7].strip()})
    return cues


# --- video --------------------------------------------------------------------------------------------------------

def ff(*args: str, timeout: float = 1800) -> None:
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise LectureError("ffmpeg: " + (r.stderr or "")[-600:])


def probe_seconds(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, timeout=60)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


X264 = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-g", str(FPS * 4), "-video_track_timescale", "15360"]
FIT = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1"


def segment(image: Path, seconds: float, out: Path, clip: Path | None = None, box: dict | None = None) -> None:
    """One slide held for `seconds`; the animation (if any) plays in its box on the slide."""
    if clip and box:
        cw = max(2, int(box["w"] * W) // 2 * 2)
        chh = max(2, int(box["h"] * H) // 2 * 2)
        x, y = int(box["x"] * W), int(box["y"] * H)
        ff("-loop", "1", "-framerate", str(FPS), "-i", str(image), "-i", str(clip), "-filter_complex",
           f"[0:v]{FIT}[bg];[1:v]scale={cw}:{chh},fps={FPS},setsar=1[c];[bg][c]overlay={x}:{y}:eof_action=repeat,format=yuv420p[v]",
           "-map", "[v]", "-t", f"{seconds:.3f}", "-an", *X264, str(out))
    else:
        ff("-loop", "1", "-framerate", str(FPS), "-i", str(image), "-vf", f"{FIT},format=yuv420p",
           "-t", f"{seconds:.3f}", "-an", *X264, str(out))


def concat(parts: list[Path], out: Path, work: Path) -> None:
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out))


def mux(video: Path, audio: Path, out: Path, *, reencode: bool = False) -> None:
    v = ["-c:v", "copy"] if not reencode else X264
    ff("-i", str(video), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", *v, "-c:a", "aac", "-b:a", "96k",
       "-ac", "1", "-shortest", "-movflags", "+faststart", str(out))


# --- B. AI narration ----------------------------------------------------------------------------------------------

def timeline(slides: list[dict], langs: list[str]) -> list[dict]:
    """Start and length of every slide so that each language's sentences fit; sentence times per language."""
    t0, out = 0.0, []
    for s in slides:
        need = [3.0]
        times = {}
        for lang in langs:
            t, rows = HEAD, []
            for line in s["audio"].get(lang) or []:
                rows.append((t, t + line["seconds"]))
                t += line["seconds"] + PAUSE
            times[lang] = rows
            need.append((t - PAUSE if rows else t) + TAIL)
        if s.get("clip_seconds"):
            need.append(s["clip_seconds"] + 0.6)
        d = math.ceil(max(need) * FPS) / FPS
        out.append({"start": t0, "seconds": d, "times": times})
        t0 += d
    return out


def assemble(slides: list[dict], langs: list[str], out_dir: Path, cache: Path) -> dict:
    """slides: [{image, clip, box, clip_seconds, audio: {lang: [{wav (Path), seconds, text}]}}] ->
    zh.mp4 / en.mp4, zh.vtt / en.vtt, poster.jpg in out_dir; returns {seconds, cues: {lang: [...]}, slides: [...]}"""
    out_dir.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    work = out_dir / "work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    try:
        tl = timeline(slides, langs)
        total = tl[-1]["start"] + tl[-1]["seconds"] if tl else 0.0
        segs = []
        for s, t in zip(slides, tl):
            k = key(hashlib.sha1(Path(s["image"]).read_bytes()).hexdigest(), f"{t['seconds']:.3f}",
                    hashlib.sha1(Path(s["clip"]).read_bytes()).hexdigest() if s.get("clip") else "", json.dumps(s.get("box")))
            seg = cache / f"seg-{k}.mp4"
            if not seg.exists():
                tmp = cache / f"seg-{k}.tmp.mp4"
                segment(Path(s["image"]), t["seconds"], tmp, Path(s["clip"]) if s.get("clip") else None, s.get("box"))
                tmp.rename(seg)
            segs.append(seg)
        picture = work / "picture.mp4"
        concat(segs, picture, work)
        cues = {}
        for lang in langs:
            track = np.zeros(int(math.ceil(total * RATE)) + RATE, dtype=np.float32)
            cues[lang] = []
            for s, t in zip(slides, tl):
                for line, (a, b) in zip(s["audio"].get(lang) or [], t["times"][lang]):
                    place(track, read_wav(Path(line["wav"]).read_bytes()), t["start"] + a)
                    cues[lang].append({"start": round(t["start"] + a, 2), "end": round(t["start"] + b + 0.2, 2), "text": line["text"]})
            write_wav(work / f"{lang}.wav", track[: int(total * RATE)])
            mux(picture, work / f"{lang}.wav", out_dir / f"{lang}.mp4")
            (out_dir / f"{lang}.vtt").write_text(vtt(cues[lang]), encoding="utf-8")
        ff("-i", str(slides[0]["image"]), "-vf", FIT, "-frames:v", "1", "-q:v", "4", str(out_dir / "poster.jpg"))
        return {"seconds": round(total, 2), "cues": cues,
                "slides": [{"start": round(t["start"], 2), "seconds": t["seconds"]} for t in tl]}
    finally:
        shutil.rmtree(work, ignore_errors=True)


# --- A. the teacher's recording -----------------------------------------------------------------------------------

def transcode(src: Path, out: Path, audio16k: Path) -> float:
    """The recording as a web video (1280x720 at most, H.264 + AAC, under the upload limit) and a 16 kHz mono WAV
    for recognition. Returns the length in seconds."""
    secs = probe_seconds(src)
    if secs <= 0:
        raise LectureError("这个文件读不出视频长度，可能不是视频文件")
    scale = "scale='min(1280,iw)':-2:force_original_aspect_ratio=decrease,scale=trunc(iw/2)*2:trunc(ih/2)*2"
    ff("-i", str(src), "-vf", scale, "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p",
       "-r", str(FPS), "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-movflags", "+faststart", str(out), timeout=7200)
    if out.stat().st_size > MAX_BYTES:       # too big for one file: fit a bitrate to the limit
        kbps = max(250, int(MAX_BYTES * 8 / 1000 / secs) - 110)
        tmp = out.with_suffix(".small.mp4")
        ff("-i", str(src), "-vf", scale, "-c:v", "libx264", "-preset", "veryfast", "-b:v", f"{kbps}k",
           "-maxrate", f"{kbps}k", "-bufsize", f"{kbps * 2}k", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-movflags", "+faststart", str(tmp), timeout=7200)
        tmp.replace(out)
    ff("-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(audio16k), timeout=3600)
    return probe_seconds(out) or secs


def dub(lines: list[dict], seconds: float, out_wav: Path) -> list[dict]:
    """English voice laid on the recording's times. lines: [{start, end, wav, seconds, text}] in order.
    A line starts at its own time, or right after the previous one if that is still speaking; the caller already
    sped up lines that do not fit. Returns the cues with the times actually used."""
    track = np.zeros(int(math.ceil(seconds * RATE)) + RATE * 5, dtype=np.float32)
    cues, free = [], 0.0
    for line in lines:
        at = max(line["start"], free)
        clip = read_wav(Path(line["wav"]).read_bytes())
        place(track, clip, at)
        free = at + len(clip) / RATE + 0.12
        cues.append({"start": round(at, 2), "end": round(max(free, line["end"]), 2), "text": line["text"]})
    write_wav(out_wav, track[: int(seconds * RATE)])
    return cues
