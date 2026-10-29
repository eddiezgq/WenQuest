import json, subprocess, sys
from pathlib import Path
OUT = Path("/home/claude/fc/rec/out"); DEST = Path(sys.argv[1])
for name in sys.argv[2:]:
    t0 = json.loads((OUT / f"{name}.t0.json").read_text())["t0"]
    allc = json.loads((OUT / f"{name}.cues.json").read_text())
    cut = [c["t"] for c in allc if c["text"] in ("__cut_start__", "__cut_end__")]
    cues = [c for c in allc if not c["text"].startswith("__")]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT / f"{name}.raw.mp4")], capture_output=True, text=True).stdout)
    start = max(0.0, cues[0]["t"] - t0 - 1.0)
    end = min(dur, cues[-1]["t"] - t0 + 7.0)
    keep = [(start, end)]
    if len(cut) == 2:                                    # 剪掉等求解的那一段（留 1.5 秒）
        a, b = cut[0] - t0 + 1.5, cut[1] - t0
        keep = [(start, a), (b, end)]
    sel = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in keep)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUT / f"{name}.raw.mp4"), "-vf", f"select='{sel}',setpts=N/FRAME_RATE/TB",
                    "-an", "-c:v", "libx264", "-crf", "28", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(DEST / f"{name}.mp4")], check=True)
    total = sum(b - a for a, b in keep)
    def mapt(x):
        acc = 0.0
        for a, b in keep:
            if x < a: return acc
            if x <= b: return acc + x - a
            acc += b - a
        return acc
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(total * 0.45, total - 1):.2f}", "-i", str(DEST / f"{name}.mp4"), "-frames:v", "1", "-q:v", "4", str(DEST / f"{name}.jpg")], check=True)
    def ts(x):
        m, s = divmod(max(0.0, x), 60)
        return f"00:{int(m):02d}:{s:06.3f}"
    L = ["WEBVTT", ""]
    for i, c in enumerate(cues):
        a = mapt(c["t"] - t0)
        b = mapt(cues[i + 1]["t"] - t0) if i + 1 < len(cues) else total
        L += [f"{ts(a)} --> {ts(max(b, a + 1.5))}", c["text"], ""]
    (DEST / f"{name}.vtt").write_text("\n".join(L), encoding="utf-8")
    print(name, f"{total:.1f}s", (DEST / f"{name}.mp4").stat().st_size // 1024, "KB")
