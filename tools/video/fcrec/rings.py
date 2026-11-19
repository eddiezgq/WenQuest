"""把 clicks.txt 里的点击（时间 x y）画成黄圈叠到录像上：每个圈 0.8 秒，由小变大、渐隐。"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
import os
R = Path(os.environ.get("WQ_REC", "."))
raw, out = sys.argv[1], sys.argv[2]
t0 = float((R / "t0.txt").read_text())
clicks = [l.split() for l in (R / "clicks.txt").read_text().split("\n") if l.strip()] if (R / "clicks.txt").exists() else []
N = 8
for k in range(N):
    s = k / (N - 1); a = 1 - 0.75 * s; rad = 16 + 22 * s
    im = Image.new("RGBA", (100, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([50 - rad, 50 - rad, 50 + rad, 50 + rad], fill=(242, 183, 5, int(60 * a)), outline=(242, 183, 5, int(255 * a)), width=5)
    im.save(R / f"ring{k}.png")
if not clicks:
    subprocess.run(["cp", raw, out], check=True)
inputs = ["-i", raw] + sum([["-i", str(R / f"ring{k}.png")] for k in range(N)], [])
chain, last = [], "0:v"
n = 0
for t, x, y in clicks:
    t = float(t) - t0
    for k in range(N):
        a, b = t + k * 0.1, t + (k + 1) * 0.1
        n += 1
        chain.append(f"[{last}][{k+1}:v]overlay={int(x)-50}:{int(y)-50}:enable='between(t,{a:.2f},{b:.2f})'[v{n}]")
        last = f"v{n}"
clicks and subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", f"[{last}]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], check=True)
print("rings", len(clicks))

# 字幕：subs.txt（时间\t文字）→ 与成片同名的 .vtt；每条显示到下一条开始（最长 6 秒），文字为空表示收起
subs = R / "subs.txt"
if subs.exists():
    rows = [l.split("\t", 1) for l in subs.read_text(encoding="utf-8").splitlines() if l.strip()]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                               capture_output=True, text=True).stdout or 0)

    def ts(x):
        x = max(0.0, x)
        return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}"
    cues = []
    for i, (t, txt) in enumerate(rows):
        a = float(t) - t0
        b = float(rows[i + 1][0]) - t0 if i + 1 < len(rows) else dur
        b = min(b, a + 6.0, dur)
        if txt.strip() and b > a:
            cues.append(f"{ts(a)} --> {ts(b)}\n{txt.strip()}")
    Path(out).with_suffix(".vtt").write_text("WEBVTT\n\n" + "\n\n".join(cues) + "\n", encoding="utf-8")
    print("subs", len(cues))
