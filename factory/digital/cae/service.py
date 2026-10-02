# -*- coding: utf-8 -*-
"""计算服务（第 11 轮 F2）：单独的 cae 容器。所有工厂（公共、演示、各班）的枢纽都把任务交到这里排队。

- 同一时间只算 1 个任务；每个任务在单独的子进程里算，超时或内存不够就整个结束掉，不影响服务。
- 只在内部网络可达（不对外开端口），身份由枢纽核对后带过来（owner、factory）。
- 数据放 /data：geo/<sha>/（零件 STEP、面清单、按面分开的模型），jobs/<编号>/（设置、状态、结果）。
"""
import hashlib
import json
import multiprocessing as mp
import os
import queue
import struct
import threading
import time
import urllib.parse
import uuid

import numpy as np
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response

from cae import materials as M

DATA = os.environ.get("WQ_CAE_DATA", "/data")
TIME_LIMIT_S = int(os.environ.get("WQ_CAE_TIME_LIMIT_S", "300"))
GEO_LIMIT_S = 90
MAX_STEP_BYTES = 30 * 1024 * 1024

app = FastAPI(title="WenQuest CAE")
_Q = queue.Queue()
_RUNNING = {"id": None}
_JLOCK = threading.Lock()


def _p(*a):
    return os.path.join(DATA, *a)


def _write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)


def _read_json(path):
    with open(path) as f:
        return json.load(f)


# ------------------------------------------------------------------ 子进程
def _isolated(target, args, timeout):
    """在新进程里跑 target(*args, out_queue)；返回 (ok, 结果或错误文字)"""
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=target, args=(*args, q), daemon=True)
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.kill()
        p.join()
        return False, "超过 {} 秒，已中止：请把网格尺寸调大或简化模型".format(timeout)
    try:
        return q.get(timeout=2)
    except queue.Empty:
        return False, "计算进程异常退出（代码 {}，多半是内存不够）：请把网格尺寸调大".format(p.exitcode)


def _geo_child(step_path, outdir, q):
    try:
        from cae import geometry as G
        faces, glb, solid = G.faces(open(step_path, "rb").read())
        open(os.path.join(outdir, "model.glb"), "wb").write(glb)
        _write_json(os.path.join(outdir, "faces.json"), {"faces": faces, "solid": solid})
        q.put((True, None))
    except Exception as e:  # noqa: BLE001
        q.put((False, str(e) or e.__class__.__name__))


def write_surface(path, surf):
    pos, vm, u = surf["positions"], surf["vm"], surf["u"]
    tri, face = surf["triangles"], surf["face_of_triangle"]
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"WQS1", len(pos), len(tri)))
        for a, dt in ((pos, "<f4"), (vm, "<f4"), (u, "<f4"), (tri, "<u4"), (face, "<u4")):
            f.write(np.ascontiguousarray(a, dtype=dt).tobytes())


def read_surface(path):
    raw = open(path, "rb").read()
    _, nv, nt = struct.unpack_from("<4sII", raw)
    o = 12
    out = {}
    for name, n, dt in (("positions", nv * 3, "<f4"), ("vm", nv, "<f4"), ("u", nv * 3, "<f4"),
                        ("triangles", nt * 3, "<u4"), ("face_of_triangle", nt, "<u4")):
        out[name] = np.frombuffer(raw, dt, n, o)
        o += 4 * n
    out["positions"] = out["positions"].reshape(-1, 3)
    out["u"] = out["u"].reshape(-1, 3)
    out["triangles"] = out["triangles"].reshape(-1, 3)
    return out


def _solve_child(step_path, setup, outdir, q):
    try:
        from cae import solve as S
        stats, surf, _ = S.solve(open(step_path, "rb").read(), setup)
        write_surface(os.path.join(outdir, "surface.bin"), surf)
        q.put((True, stats))
    except Exception as e:  # noqa: BLE001
        q.put((False, str(e) or e.__class__.__name__))


# ------------------------------------------------------------------ 队列
def _job_path(jid, *a):
    return _p("jobs", jid, *a)


def _update(jid, **kw):
    with _JLOCK:
        j = _read_json(_job_path(jid, "job.json"))
        j.update(kw)
        _write_json(_job_path(jid, "job.json"), j)
        return j


def _worker():
    while True:
        jid = _Q.get()
        try:
            j = _read_json(_job_path(jid, "job.json"))
            if j["status"] != "queued":
                continue
            _RUNNING["id"] = jid
            _update(jid, status="running", started=time.time())
            setup = dict(j["setup"])
            setup["material"] = M.get(setup["material_id"])
            ok, res = _isolated(_solve_child, (_p("geo", j["step_sha"], "part.step"), setup, _job_path(jid)), TIME_LIMIT_S + 60)
            if ok:
                _update(jid, status="done", finished=time.time(), stats=res)
            else:
                _update(jid, status="failed", finished=time.time(), error=res)
        except Exception as e:  # noqa: BLE001
            try:
                _update(jid, status="failed", finished=time.time(), error=str(e))
            except Exception:  # noqa: BLE001
                pass
        finally:
            _RUNNING["id"] = None


@app.on_event("startup")
def _start():
    os.makedirs(_p("geo"), exist_ok=True)
    os.makedirs(_p("jobs"), exist_ok=True)
    pending = []
    for jid in os.listdir(_p("jobs")):
        try:
            j = _read_json(_job_path(jid, "job.json"))
        except Exception:  # noqa: BLE001
            continue
        if j["status"] == "running":
            _update(jid, status="failed", error="计算服务重启，任务中断，请重新提交")
        elif j["status"] == "queued":
            pending.append((j["created"], jid))
    for _, jid in sorted(pending):
        _Q.put(jid)
    threading.Thread(target=_worker, daemon=True).start()


def _queued_ids():
    out = []
    for jid in os.listdir(_p("jobs")):
        try:
            j = _read_json(_job_path(jid, "job.json"))
        except Exception:  # noqa: BLE001
            continue
        if j["status"] == "queued":
            out.append((j["created"], jid))
    return [jid for _, jid in sorted(out)]


def _public(j):
    j = dict(j)
    if j["status"] == "queued":
        q = _queued_ids()
        j["position"] = q.index(j["id"]) + 1 if j["id"] in q else None
        j["running_other"] = _RUNNING["id"] is not None
    return j


# ------------------------------------------------------------------ 接口
@app.get("/health")
def health():
    return {"ok": True, "running": _RUNNING["id"], "queued": len(_queued_ids())}


@app.get("/materials")
def materials():
    return {"materials": M.public()}


@app.post("/geometry")
async def geometry(request: Request):
    data = await request.body()
    if not data:
        raise HTTPException(400, "没有收到 STEP 文件")
    if len(data) > MAX_STEP_BYTES:
        raise HTTPException(413, "STEP 文件超过 30 MB，教学版不支持")
    sha = hashlib.sha256(data).hexdigest()
    d = _p("geo", sha)
    if not os.path.exists(os.path.join(d, "faces.json")):
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "part.step"), "wb").write(data)
        ok, err = _isolated(_geo_child, (os.path.join(d, "part.step"), d), GEO_LIMIT_S)
        if not ok:
            raise HTTPException(422, "读不了这个 STEP：{}".format(err))
    return dict(_read_json(os.path.join(d, "faces.json")), sha=sha)


@app.get("/geometry/{sha}/model.glb")
def geometry_glb(sha: str):
    p = _p("geo", sha.replace("/", ""), "model.glb")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个零件")
    return FileResponse(p, media_type="model/gltf-binary")


@app.post("/jobs")
def submit(body: dict = Body(...)):
    sha = str(body.get("step_sha", "")).replace("/", "")
    if not os.path.exists(_p("geo", sha, "faces.json")):
        raise HTTPException(400, "请先读入零件")
    setup = body.get("setup") or {}
    try:
        M.get(setup.get("material_id"))
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    faces = {f["id"] for f in _read_json(_p("geo", sha, "faces.json"))["faces"]}
    loads = setup.get("loads") or []
    for l in loads:
        if not l.get("faces") or not set(l["faces"]) <= faces:
            raise HTTPException(400, "载荷或约束选的面不对")
    if not any(l["type"] in ("fixed", "cyl_support") for l in loads):
        raise HTTPException(400, "至少要有一个固定或支承面")
    if not any(l["type"] not in ("fixed", "cyl_support") for l in loads):
        raise HTTPException(400, "还没有加载荷")
    jid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    os.makedirs(_job_path(jid))
    j = {"id": jid, "status": "queued", "created": time.time(), "step_sha": sha, "setup": setup,
         "owner": body.get("owner"), "owner_name": body.get("owner_name"), "factory": body.get("factory"),
         "title": body.get("title") or "", "item": body.get("item")}
    _write_json(_job_path(jid, "job.json"), j)
    _Q.put(jid)
    return _public(j)


@app.get("/jobs")
def jobs(factory: str = "", owner: str = "", limit: int = 50):
    out = []
    for jid in sorted(os.listdir(_p("jobs")), reverse=True):
        try:
            j = _read_json(_job_path(jid, "job.json"))
        except Exception:  # noqa: BLE001
            continue
        if factory and j.get("factory") != factory:
            continue
        if owner and str(j.get("owner")) != owner:
            continue
        out.append(_public(j))
        if len(out) >= limit:
            break
    return {"jobs": out}


@app.get("/jobs/{jid}")
def job(jid: str):
    p = _job_path(jid.replace("/", ""), "job.json")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个任务")
    return _public(_read_json(p))


@app.get("/jobs/{jid}/surface.bin")
def surface(jid: str):
    p = _job_path(jid.replace("/", ""), "surface.bin")
    if not os.path.exists(p):
        raise HTTPException(404, "结果还没出来")
    return FileResponse(p, media_type="application/octet-stream")


@app.post("/jobs/{jid}/report")
def report(jid: str, body: dict = Body(default={})):
    """Word 报告：images = [{data: dataURL, caption}]（浏览器截的云图），ai_text 可选"""
    p = _job_path(jid.replace("/", ""), "job.json")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个任务")
    j = _read_json(p)
    if j["status"] != "done":
        raise HTTPException(409, "结果还没出来")
    from cae import report as R
    imgs = (body.get("images") or [])[:4]
    data = R.build(j, imgs, body.get("ai_text") or j.get("ai_text"))
    name = "有限元报告-{}.docx".format(j.get("item") or jid)
    return Response(data, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": "attachment; filename*=UTF-8''" + urllib.parse.quote(name)})


@app.get("/geometry/{sha}/step")
def geometry_step(sha: str):
    p = _p("geo", sha.replace("/", ""), "part.step")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个零件")
    return Response(open(p, "rb").read(), media_type="application/step")
