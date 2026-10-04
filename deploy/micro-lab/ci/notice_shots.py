"""把远程桌面截图缩成小图，以运行注释（notice）写出，便于在拿不到构建产物的环境里查看。
每张图压到 3 段以内（每段 ≤ 3900 字符），一步最多 9 条注释。
用法：python notice_shots.py <截图目录>"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

CHUNK = 3900
for png in sorted(Path(sys.argv[1]).glob("*.png"))[:3]:
    im = Image.open(png).convert("RGB")
    for width, q in ((480, 40), (400, 30), (320, 25), (240, 20)):
        buf = io.BytesIO()
        im.resize((width, round(im.height * width / im.width))).save(buf, "JPEG", quality=q, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        if len(b64) <= 3 * CHUNK:
            break
    parts = [b64[i:i + CHUNK] for i in range(0, len(b64), CHUNK)][:3]
    for i, p in enumerate(parts):
        print(f"::notice title=截图 {png.stem} {i + 1}/{len(parts)}::{p}")
