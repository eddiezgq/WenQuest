# webm + 字幕时间 → 剪掉等待段 → 720p mp4（H.264）+ 封面 jpg + 中文字幕 vtt
import json, subprocess, sys
from pathlib import Path
OUT = Path(__file__).parent / "out"
DEST = Path(sys.argv[1])
for name in sys.argv[2:]:
    meta = json.loads((OUT / f"{name}.json").read_text())
    cuts, end = sorted(meta["cuts"]), meta["end"]
    if meta["cues"] and meta["cues"][0]["t"] > 1.5:          # 片头页面还在加载的那几秒剪掉
        cuts = sorted(cuts + [[0.0, meta["cues"][0]["t"] - 0.8]])
    keep, t = [], 0.0
    for a, b in cuts:
        keep.append((t, a)); t = b
    keep.append((t, end))
    keep = [(a, b) for a, b in keep if b - a > 0.2]
    def mapt(x):  # 原时间 → 剪后时间
        acc = 0.0
        for a, b in keep:
            if x < a: return acc
            if x <= b: return acc + x - a
            acc += b - a
        return acc
    sel = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in keep)
    vf = f"select='{sel}',setpts=N/FRAME_RATE/TB,scale=1280:720,fps=25"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUT / f"{name}.webm"), "-vf", vf, "-an", "-c:v", "libx264",
                    "-crf", "28", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(DEST / f"{name}.mp4")], check=True)
    total = sum(b - a for a, b in keep)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(3.0, total / 3):.2f}", "-i", str(DEST / f"{name}.mp4"), "-frames:v", "1",
                    "-q:v", "4", str(DEST / f"{name}.jpg")], check=True)
    cues = meta["cues"]
    def ts(x):
        h, r = divmod(max(0.0, x), 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
    lines = ["WEBVTT", ""]
    for i, c in enumerate(cues):
        a = mapt(c["t"])
        nxt = mapt(cues[i + 1]["t"]) if i + 1 < len(cues) else total
        b = min(nxt, a + (c.get("dur") or 99)) if c.get("dur") else nxt
        b = max(b, a + 1.5)
        lines += [f"{ts(a)} --> {ts(min(b, total))}", c["text"], ""]
    (DEST / f"{name}.vtt").write_text("\n".join(lines), encoding="utf-8")
    print(name, f"{total:.1f}s", (DEST / f"{name}.mp4").stat().st_size // 1024, "KB")
