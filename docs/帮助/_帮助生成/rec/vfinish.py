"""带配音的录屏出片（第 90 轮）：webm（网页，vrec.js）或 raw.mp4（FreeCAD，fcrec.sh）+ 字幕时间 → 剪掉等待段 → 720p mp4（H.264 + AAC 配音）+ 封面 jpg + 中文字幕 vtt。
配音把每句的 WAV 放在它的字幕时间上（剪辑后的时间），响度统一到 −16 LUFS。

  python3 vfinish.py <录屏目录> <出片目录> 名字1 名字2 …
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

RATE = 24000


def wav(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    return a


def main():
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    dest.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[3:]:
        meta = json.loads((src / f"{name}.json").read_text(encoding="utf-8"))
        cuts, end = sorted(meta["cuts"]), meta["end"]
        if meta["cues"] and meta["cues"][0]["t"] > 1.5:  # the page loading before the first line
            cuts = sorted(cuts + [[0.0, meta["cues"][0]["t"] - 0.6]])
        keep, t = [], 0.0
        for a, b in cuts:
            keep.append((t, a))
            t = b
        keep.append((t, end))
        keep = [(a, b) for a, b in keep if b - a > 0.2]

        def mapt(x):
            acc = 0.0
            for a, b in keep:
                if x < a:
                    return acc
                if x <= b:
                    return acc + x - a
                acc += b - a
            return acc
        total = sum(b - a for a, b in keep)
        track = np.zeros(int((total + 1) * RATE), np.float32)
        for c in meta["cues"]:
            a = wav(c["wav"])
            i = int(mapt(c["t"]) * RATE)
            track[i:i + len(a)] += a[: max(0, len(track) - i)]
        tmp = dest / f"{name}.voice.wav"
        with wave.open(str(tmp), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes((np.clip(track, -1, 1) * 32767).astype("<i2").tobytes())
        video = src / f"{name}.webm"
        if not video.exists():                           # FreeCAD 录屏（fcrec.sh）是 mp4
            video = src / f"{name}.raw.mp4"
        sel = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in keep)
        vf = f"select='{sel}',setpts=N/FRAME_RATE/TB,scale=1280:720,fps=25"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(tmp), "-vf", vf,
                        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "28",
                        "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-shortest",
                        "-movflags", "+faststart", str(dest / f"{name}.mp4")], check=True)
        tmp.unlink()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(3.0, total / 3):.2f}", "-i", str(dest / f"{name}.mp4"),
                        "-frames:v", "1", "-q:v", "4", str(dest / f"{name}.jpg")], check=True)

        def ts(x):
            h, r = divmod(max(0.0, x), 3600)
            m, s = divmod(r, 60)
            return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
        lines = ["WEBVTT", ""]
        cues = meta["cues"]
        for i, c in enumerate(cues):
            a = mapt(c["t"])
            nxt = mapt(cues[i + 1]["t"]) if i + 1 < len(cues) else total
            b = min(nxt, a + c["dur"] + 0.6)
            lines += [f"{ts(a)} --> {ts(min(max(b, a + 1.2), total))}", c["text"], ""]
        (dest / f"{name}.vtt").write_text("\n".join(lines), encoding="utf-8")
        print(name, f"{total:.1f}s", (dest / f"{name}.mp4").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
