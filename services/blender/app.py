"""三维仿真视频渲染容器（第 38 轮第 1 步）。

- POST /stills {"scene": "<scene.yaml 文本>", "times": [秒, ...]} → {"ok": true, "stills": [PNG base64], "seconds": n}
  出几张关键画面（960×540），先看构图和镜头；整段视频不在这里出（租 Lambda 机器，见网关 video3d.py）。
- GET /samples → 样片场景 [{"id", "title": {zh, en}, "duration", "scene"}]
- GET /format → 场景格式说明（tools/blender/场景格式.md，给 AI 写场景时用）
- GET /bundle → 渲染器打包（tar.gz），网关把它传到租来的机器上，配 run.sh 出片
没有密钥、不能上网，一次只出一个。场景是数据（YAML），不执行代码。"""
from __future__ import annotations

import asyncio
import base64
import io
import os
import shutil
import sys
import tarfile
import tempfile
import time
from pathlib import Path

import yaml
from fastapi import FastAPI, Response
from pydantic import BaseModel

HERE = Path(__file__).parent
ROOT = Path(os.environ.get("WQ_BLENDER_ROOT", HERE / "wq"))      # 渲染器与它要读的文件（保持仓库里的相对位置）
RENDER = ROOT / "tools/blender/render.py"
TIMEOUT = int(os.environ.get("WQ_STILL_TIMEOUT", "600"))
MAX_SCENE = 60_000
MAX_STILLS = 8

app = FastAPI(title="WenQuest 3D video stills")
lock = asyncio.Lock()


class StillsIn(BaseModel):
    scene: str
    times: list[float]


@app.get("/health")
def health():
    return {"ok": RENDER.exists()}


@app.get("/samples")
def samples():
    out = []
    for f in sorted((ROOT / "video3d").glob("*/scene.yaml")):
        try:
            s = yaml.safe_load(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        out.append({"id": f.parent.name, "title": s.get("title") or {"zh": f.parent.name, "en": f.parent.name},
                    "duration": s.get("duration"), "scene": f.read_text(encoding="utf-8")})
    return {"samples": out}


@app.get("/format")
def fmt():
    return {"text": (ROOT / "tools/blender/场景格式.md").read_text(encoding="utf-8")}


@app.get("/bundle")
def bundle():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for rel in ("tools/blender", "tools/site_cases/assets/three.min.js", "textbook/web-editions/sewing/src"):
            p = ROOT / rel
            if p.exists():
                t.add(p, arcname=rel, filter=lambda i: None if "__pycache__" in i.name or "/_" in i.name else i)
        # 第 56 轮 gen:sewdesign 要的计算核心：只带 .py（不带 FreeCAD 插件那 3 MB）
        core = ROOT / "services/gateway/app/sewcore"
        for f in sorted(core.glob("*.py")):
            t.add(f, arcname=f"services/gateway/app/sewcore/{f.name}")
    return Response(buf.getvalue(), media_type="application/gzip")


@app.get("/run.sh")
def run_sh():
    return Response((HERE / "run.sh").read_text(encoding="utf-8"), media_type="text/x-shellscript")


@app.post("/stills")
async def stills(body: StillsIn):
    if len(body.scene) > MAX_SCENE:
        return {"ok": False, "error": "scene too long"}
    times = sorted({round(float(t), 1) for t in body.times})[:MAX_STILLS]
    if not times:
        return {"ok": False, "error": "no times"}
    try:
        spec = yaml.safe_load(body.scene)
        assert isinstance(spec, dict)
    except Exception as e:
        return {"ok": False, "error": f"scene is not valid YAML: {e}"}
    async with lock:
        t0 = time.time()
        work = Path(tempfile.mkdtemp(prefix="still_"))
        try:
            (work / "scene.yaml").write_text(body.scene, encoding="utf-8")
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(RENDER), str(work), "--draft", "--still", ",".join(str(t) for t in times),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
            try:
                out, _ = await asyncio.wait_for(proc.communicate(), TIMEOUT)
            except asyncio.TimeoutError:
                proc.kill()
                return {"ok": False, "error": f"timed out after {TIMEOUT} s"}
            log = out.decode("utf-8", "replace")
            files = sorted((work / "_frames").glob("still_*.png"))
            if proc.returncode != 0 or len(files) < len(times):
                lines = [ln for ln in log.splitlines() if not ln.startswith(("Fra:", "Saved:", "Time:")) and ln.strip()]
                return {"ok": False, "error": "\n".join(lines[-12:])[-1500:] or f"exit {proc.returncode}"}
            return {"ok": True, "seconds": round(time.time() - t0, 1),
                    "stills": [base64.b64encode(f.read_bytes()).decode() for f in files]}
        finally:
            shutil.rmtree(work, ignore_errors=True)
