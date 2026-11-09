"""上线检查：在线实验报告导出 PDF（第 122 轮）。在网关容器里跑：python -m app.production.pdf_selftest

拿一份真实的实验报告模板（默认《大学物理》实验 1.5）生成 Word，交给在线文档服务（OnlyOffice /converter，带 JWT）
转成 PDF，取回并检查。Word 文件由本脚本在 8001 端口临时提供（同一个 docker 网络里 http://gateway:8001），
不经过正在运行的网关、不登录、不写任何数据。最后一行是 "pdf ok …" 或 "pdf FAIL …"。
"""
import hashlib
import http.server
import json
import re
import sys
import threading
import time
from pathlib import Path

import httpx

from app.config import get_settings
from app.production import webdoc
from app.webdocs_api import jwt_hs256

PORT = 8001


def main(book: str = "physics", lab: str = "1_5") -> int:
    s = get_settings()
    if not (s.docs_url and s.docs_jwt_secret):
        print("pdf FAIL 没有配置 docs_url / docs_jwt_secret")
        return 1
    p = next((Path(s.textbook_dir) / book / sub / f"lab{lab}-report.json" for sub in ("lab", "gpulab")
              if (Path(s.textbook_dir) / book / sub / f"lab{lab}-report.json").exists()), None)
    if not p:
        print(f"pdf FAIL 找不到 {book} 实验 {lab} 的报告模板")
        return 1
    doc = webdoc.blank(json.loads(p.read_text(encoding="utf-8")))
    data = webdoc.to_docx(doc)
    key = "selftest" + hashlib.sha256(data + str(time.time()).encode()).hexdigest()[:24]

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != f"/{key}.docx":
                self.send_response(404); self.end_headers(); return
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    host = re.sub(r"^https?://([^:/]+).*", r"\1", s.internal_url) or "gateway"
    try:
        payload = {"async": False, "filetype": "docx", "outputtype": "pdf", "key": key, "title": f"{key}.docx",
                   "url": f"http://{host}:{PORT}/{key}.docx"}
        payload["token"] = jwt_hs256(payload, s.docs_jwt_secret)
        base = s.docs_url.rstrip("/")
        t0 = time.time()
        r = httpx.post(f"{base}/converter", json=payload, timeout=120,
                       headers={"Accept": "application/json",
                                "Authorization": "Bearer " + jwt_hs256({"payload": payload}, s.docs_jwt_secret)})
        out = r.json() if r.status_code == 200 else {}
        if not out.get("endConvert") or not out.get("fileUrl"):
            print(f"pdf FAIL 转换出错 {r.status_code} {out}")
            return 1
        url = out["fileUrl"]
        if not url.startswith(base + "/"):
            url = base + re.sub(r"^/docs(?=/)", "", re.sub(r"^https?://[^/]+", "", url))
        f = httpx.get(url, timeout=60)
        if f.status_code != 200 or not f.content.startswith(b"%PDF"):
            print(f"pdf FAIL 取不回 PDF {f.status_code}")
            return 1
        import io
        from pypdf import PdfReader
        pdf = PdfReader(io.BytesIO(f.content))
        text = "".join((pg.extract_text() or "") for pg in pdf.pages)
        print(f"word {len(data)} B -> pdf {len(f.content)} B, {len(pdf.pages)} 页, {time.time() - t0:.1f} s")
        if len(pdf.pages) < 2 or "实验目的" not in text:
            print(f"pdf FAIL 内容不对（{len(pdf.pages)} 页，正文里{'有' if '实验目的' in text else '没有'}“实验目的”）")
            return 1
        print(f"pdf ok {book} 实验 {lab.replace('_', '.')}")
        return 0
    finally:
        srv.shutdown()


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
