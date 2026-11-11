"""把零件的二进制 STL 打包成一个 meshes.json（每个零件的三角形顶点，Float32 小端、base64），给发布到网页用（网页托管不收 .stl）。

    python3 tools/wqls/render/stl2json.py <零件目录>      → <零件目录>/meshes.json
"""
import base64
import json
import struct
import sys
from pathlib import Path

d = Path(sys.argv[1])
out = {}
for f in sorted(d.glob("*.stl")):
    b = f.read_bytes()
    n = struct.unpack_from("<I", b, 80)[0]
    pos = bytearray()
    for i in range(n):
        o = 84 + 50 * i + 12
        pos += b[o:o + 36]
    out[f.stem] = base64.b64encode(bytes(pos)).decode()
(d / "meshes.json").write_text(json.dumps(out))
print(len(out), "meshes", (d / "meshes.json").stat().st_size // 1024, "KB")
