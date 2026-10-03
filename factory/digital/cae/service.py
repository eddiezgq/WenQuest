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
import zipfile

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
        if surf.get("temp") is not None:                  # 第 14 轮：热分析多一段节点温度（旧读法读到 face 为止，不受影响）
            f.write(np.ascontiguousarray(surf["temp"], dtype="<f4").tobytes())


def read_surface(path):
    raw = open(path, "rb").read()
    _, nv, nt = struct.unpack_from("<4sII", raw)
    o = 12
    out = {}
    for name, n, dt in (("positions", nv * 3, "<f4"), ("vm", nv, "<f4"), ("u", nv * 3, "<f4"),
                        ("triangles", nt * 3, "<u4"), ("face_of_triangle", nt, "<u4")):
        out[name] = np.frombuffer(raw, dt, n, o)
        o += 4 * n
    if len(raw) >= o + 4 * nv:
        out["temp"] = np.frombuffer(raw, "<f4", nv, o)
    out["positions"] = out["positions"].reshape(-1, 3)
    out["u"] = out["u"].reshape(-1, 3)
    out["triangles"] = out["triangles"].reshape(-1, 3)
    return out


def _solve_child(step_path, setup, outdir, q):
    try:
        if setup.get("analysis") in ("thermal", "thermo_mech"):
            from cae import thermal as S
        else:
            from cae import solve as S
        stats, surf, _ = S.solve(open(step_path, "rb").read(), setup)
        write_surface(os.path.join(outdir, "surface.bin"), surf)
        q.put((True, stats))
    except Exception as e:  # noqa: BLE001
        q.put((False, str(e) or e.__class__.__name__))


# ------------------------------------------------------------------ 运动与动力分析（第 12 轮）
def model_key(ref):
    src = (ref or {}).get("source")
    if src == "library":
        return str(ref.get("id", "")).replace("/", "")
    if src == "upload":
        return "u-" + str(ref.get("sha", "")).replace("/", "")[:64]
    if src == "mech":
        import json as _j
        return "m-" + hashlib.sha256(_j.dumps([ref.get("id"), ref.get("params") or {}], sort_keys=True).encode()).hexdigest()[:24]
    raise ValueError("模型来源不对")


def load_model_spec(ref):
    """模型引用 → MjSpec"""
    from cae import mbd, mbd_models as MM
    src = ref.get("source")
    if src == "library":
        return mbd.load_spec(path=MM.robot_path(ref.get("id")))
    if src == "upload":
        if ref.get("_main"):                      # 子进程里：主进程已经找好了文件
            return mbd.load_spec(path=ref["_main"])
        meta = _p("mbd", "uploads", model_key(ref)[2:], "meta.json")
        if not os.path.exists(meta):
            raise ValueError("没有这个上传的模型")
        return mbd.load_spec(path=_read_json(meta)["main"])
    if src == "mech":
        from cae import mech_mjcf
        return mbd.load_spec(xml=mech_mjcf.mjcf(ref.get("id"), ref.get("params") or {}))
    raise ValueError("模型来源不对")


def _resolved(ref):
    """交给子进程前把上传模型的文件路径找好（子进程不一定知道数据目录）"""
    if ref.get("source") == "upload":
        meta = _p("mbd", "uploads", model_key(ref)[2:], "meta.json")
        if not os.path.exists(meta):
            raise HTTPException(404, "没有这个上传的模型")
        return dict(ref, _main=_read_json(meta)["main"])
    return ref


def _model_child(ref, outdir, q):
    try:
        from cae import mbd, mbd_models as MM
        model, _ = mbd.build(load_model_spec(ref), {})
        open(os.path.join(outdir, "model.glb"), "wb").write(MM.model_glb(model))
        _write_json(os.path.join(outdir, "info.json"), mbd.info(model))
        q.put((True, None))
    except Exception as e:  # noqa: BLE001
        q.put((False, str(e) or e.__class__.__name__))


def write_series(path, ch):
    names = list(ch)
    head = json.dumps({"names": names, "n": int(len(ch["t"]))}).encode()
    with open(path, "wb") as f:
        f.write(struct.pack("<4sI", b"WQC1", len(head)))
        f.write(head)
        f.write(np.ascontiguousarray(np.stack([ch[n] for n in names], 1), dtype="<f4").tobytes())


def read_series(path):
    raw = open(path, "rb").read()
    _, hl = struct.unpack_from("<4sI", raw)
    head = json.loads(raw[8:8 + hl])
    arr = np.frombuffer(raw, "<f4", offset=8 + hl).reshape(head["n"], len(head["names"]))
    return {n: arr[:, i] for i, n in enumerate(head["names"])}


def write_anim(path, an):
    head = json.dumps({"bodies": an["bodies"], "frames": int(len(an["t"]))}).encode()
    with open(path, "wb") as f:
        f.write(struct.pack("<4sI", b"WQA1", len(head)))
        f.write(head)
        for a in (an["t"], an["pos"], an["quat"]):
            f.write(np.ascontiguousarray(a, dtype="<f4").tobytes())


def _mbd_child(ref, setup, outdir, q):
    try:
        from cae import mbd
        if ref.get("source") == "mech":
            from cae import mech_mjcf
            setup = mech_mjcf.prepare_setup(ref.get("id"), ref.get("params") or {}, setup)
        summ, ch, an = mbd.simulate(load_model_spec(ref), setup)
        write_series(os.path.join(outdir, "series.bin"), ch)
        write_anim(os.path.join(outdir, "anim.bin"), an)
        q.put((True, summ))
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
            if j.get("kind") == "mbd":
                ok, res = _isolated(_mbd_child, (_resolved(j["model"]), j["setup"], _job_path(jid)), TIME_LIMIT_S + 60)
            else:
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
    os.makedirs(_p("mbd", "models"), exist_ok=True)
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
    return {"materials": M.public(), "films": M.FILM}


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


@app.get("/geometry/{sha}/faces")
def geometry_faces(sha: str):
    p = _p("geo", sha.replace("/", ""), "faces.json")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个零件")
    return _read_json(p)


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
    an = setup.get("analysis", "static")
    if an in ("thermal", "thermo_mech"):
        th = setup.get("thermal") or []
        for l in th:
            if l["type"] != "heat_body" and l.get("faces") != "rest" and (not l.get("faces") or not set(l["faces"]) <= faces):
                raise HTTPException(400, "热载荷选的面不对")
        if not any(l["type"] in ("temperature", "convection") for l in th):
            raise HTTPException(400, "至少要有一个固定温度或对流换热的面")
        if an == "thermo_mech" and not any(l["type"] in ("fixed", "cyl_support") for l in loads):
            raise HTTPException(400, "热—结构耦合至少要有一个固定或支承面")
    else:
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


@app.get("/mbd/mechs")
def mbd_mechs():
    from cae import mech_mjcf as MC
    return {"mechs": [{"id": k, "name": MC.NAMES[k], "driver": MC.DRIVER[k], "params": MC.DEFAULTS[k], "labels": MC.LABELS,
                       "fea_members": list(MC.STEP_MEMBERS.get(k, {}))}
                      for k in MC.DEFAULTS]}


@app.get("/mbd/robots")
def mbd_robots():
    from cae import mbd_models as MM
    return {"robots": [{"id": k, "name": v[1], "end_body": v[2]} for k, v in MM.ROBOTS.items()]}


def _model_ready(ref):
    key = model_key(ref)
    d = _p("mbd", "models", key)
    if not os.path.exists(os.path.join(d, "info.json")):
        os.makedirs(d, exist_ok=True)
        ok, err = _isolated(_model_child, (_resolved(ref), d), GEO_LIMIT_S)
        if not ok:
            raise HTTPException(422, "读不了这个模型：{}".format(err))
    return dict(_read_json(os.path.join(d, "info.json")), key=key, ref=ref)


@app.post("/mbd/models/load")
def mbd_model_load(body: dict = Body(...)):
    try:
        model_key(body)
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    return _model_ready(body)


@app.post("/mbd/models/upload")
async def mbd_model_upload(request: Request, name: str = "model.xml"):
    from cae import mbd_models as MM
    data = await request.body()
    if not data:
        raise HTTPException(400, "没有收到文件")
    if len(data) > 100 * 1024 * 1024:
        raise HTTPException(413, "文件超过 100 MB")
    sha = hashlib.sha256(data).hexdigest()
    d = _p("mbd", "uploads", sha)
    if not os.path.exists(os.path.join(d, "meta.json")):
        try:
            main = MM.unpack_upload(data, name, os.path.join(d, "files"))
        except (ValueError, zipfile.BadZipFile) as e:
            raise HTTPException(422, str(e)) from None
        _write_json(os.path.join(d, "meta.json"), {"main": main, "name": name})
    return _model_ready({"source": "upload", "sha": sha})


@app.get("/mbd/models/{key}/model.glb")
def mbd_model_glb(key: str):
    p = _p("mbd", "models", key.replace("/", ""), "model.glb")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个模型")
    return FileResponse(p, media_type="model/gltf-binary")


@app.post("/mbd/jobs")
def mbd_submit(body: dict = Body(...)):
    from cae import mbd
    ref = body.get("model") or {}
    info = _model_ready(ref)
    setup = body.get("setup") or {}
    try:
        dur = float(setup.get("duration_s", 2))
    except (TypeError, ValueError):
        raise HTTPException(400, "仿真时长不对") from None
    if not 0 < dur <= mbd.MAX_DURATION_S:
        raise HTTPException(400, "仿真时长要在 0–{:.0f} 秒之间".format(mbd.MAX_DURATION_S))
    names = {j["name"] for j in info["joints"]}
    bodies = {b["name"] for b in info["bodies"]}
    for d in setup.get("drives") or []:
        if d.get("joint") not in names:
            raise HTTPException(400, "模型里没有关节“{}”".format(d.get("joint")))
    for x in (setup.get("payloads") or []) + (setup.get("forces") or []) + (setup.get("points") or []):
        if x.get("body") not in bodies:
            raise HTTPException(400, "模型里没有构件“{}”".format(x.get("body")))
    jid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    os.makedirs(_job_path(jid))
    j = {"id": jid, "kind": "mbd", "status": "queued", "created": time.time(), "model": ref, "model_key": info["key"],
         "setup": setup, "owner": body.get("owner"), "owner_name": body.get("owner_name"), "factory": body.get("factory"),
         "title": body.get("title") or "", "item": body.get("item")}
    _write_json(_job_path(jid, "job.json"), j)
    _Q.put(jid)
    return _public(j)


def _quat_mat(q):
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def _read_anim(path):
    raw = open(path, "rb").read()
    _, hl = struct.unpack_from("<4sI", raw)
    head = json.loads(raw[8:8 + hl])
    f, nb = head["frames"], len(head["bodies"])
    arr = np.frombuffer(raw, "<f4", offset=8 + hl)
    return head["bodies"], arr[:f], arr[f:f + f * nb * 3].reshape(f, nb, 3), arr[f + f * nb * 3:].reshape(f, nb, 4)


def member_load(jid, member):
    """动力学结果里一根杆件的受力（第 12 轮 D6）：B 端受力的时间序列（构件坐标）、最大时刻"""
    from cae import mech_mjcf as MC
    j = _read_json(_job_path(jid, "job.json"))
    if j.get("kind") != "mbd" or j["status"] != "done":
        raise HTTPException(409, "动力学结果还没出来")
    ref = j["model"]
    if ref.get("source") != "mech":
        raise HTTPException(400, "目前只有零件库的连杆机构能把杆件送去有限元")
    try:
        ch_body = MC.member_force_channel(ref["id"], member)
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    ser = read_series(_job_path(jid, "series.bin"))
    bodies, at, apos, aquat = _read_anim(_job_path(jid, "anim.bin"))
    F = -np.stack([ser["rf.{}.{}".format(ch_body, a)] for a in "xyz"], 1)        # 世界坐标，B 端受力
    bi = bodies.index(member)
    idx = np.clip(np.searchsorted(at, ser["t"]), 0, len(at) - 1)                  # 每个采样时刻的构件姿态（取最近的动画帧）
    Floc = np.stack([_quat_mat(aquat[k, bi]).T @ F[i] for i, k in enumerate(idx)])
    mag = np.linalg.norm(Floc, axis=1)
    k = int(np.argmax(mag))
    return {"job": j, "member": member, "t": ser["t"], "F_local": Floc, "peak_index": k, "peak_t": float(ser["t"][k]),
            "peak_local": Floc[k], "peak_N": float(mag[k]), "duration_s": float(ser["t"][-1] - ser["t"][0])}


@app.post("/mbd/jobs/{jid}/to-fea")
def mbd_to_fea(jid: str, body: dict = Body(...)):
    """把杆件和它受力最大时刻的力交给有限元：返回零件（同 /geometry）和建议的约束、载荷"""
    from cae import mech_mjcf as MC
    member = str(body.get("member") or "")
    ml = member_load(jid.replace("/", ""), member)
    ref = ml["job"]["model"]
    step = MC.member_step(ref["id"], member, ref.get("params") or {})
    sha = hashlib.sha256(step).hexdigest()
    d = _p("geo", sha)
    if not os.path.exists(os.path.join(d, "faces.json")):
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "part.step"), "wb").write(step)
        ok, err = _isolated(_geo_child, (os.path.join(d, "part.step"), d), GEO_LIMIT_S)
        if not ok:
            raise HTTPException(422, "杆件模型生成失败：{}".format(err))
    geo = dict(_read_json(os.path.join(d, "faces.json")), sha=sha)
    holes = sorted([f for f in geo["faces"] if f["kind"] == "cylinder" and f.get("radius_mm") and
                    abs(f["center"][1]) < 1e-3 and abs(f["center"][2]) < 1e-3 and
                    f["radius_mm"] < 0.4 * MC.params(ref["id"], ref.get("params"))["link_width_m"] * 1000],
                   key=lambda f: f["center"][0])
    if len(holes) != 2:
        raise HTTPException(500, "没找到杆件两端的销孔")
    Fv = [round(float(x), 3) for x in ml["peak_local"]]
    name = MC.LABELS.get(member, member)
    return {"geometry": geo, "member": member, "member_name": name, "peak_t": ml["peak_t"], "peak_N": ml["peak_N"],
            "force_local_N": Fv,
            "rows": [{"kind": "fixed", "faces": [holes[0]["id"]]},
                     {"kind": "force", "faces": [holes[1]["id"]], "fx": Fv[0], "fy": Fv[1], "fz": Fv[2]}],
            "title": "{} 的{}（t = {:.3f} s，{:.0f} N）".format(MC.NAMES[ref["id"]], name, ml["peak_t"], ml["peak_N"]),
            "note": "A 端销孔固定、B 端销孔受动力学算出的最大力（构件坐标）；二力杆近似，略去惯性力和自重",
            "source": {"job": ml["job"]["id"], "member": member}}


@app.get("/mbd/jobs/{jid}/motors")
def mbd_motors(jid: str, safety: float = 1.2):
    """电机选型助手：每个转动关节的驱动（给定运动 / 力矩）"""
    from cae import motors as MT
    j = _read_json(_job_path(jid.replace("/", ""), "job.json"))
    if j.get("kind") != "mbd" or j["status"] != "done":
        raise HTTPException(409, "动力学结果还没出来")
    if not 1.0 <= safety <= 3.0:
        raise HTTPException(400, "安全系数要在 1–3 之间")
    ser = read_series(_job_path(j["id"], "series.bin"))
    out = []
    only = None
    if (j.get("model") or {}).get("source") == "mech":            # 机构：只有主动件装电机，从动件上的是工作阻力
        from cae import mech_mjcf as MC
        only = MC.DRIVER.get(j["model"]["id"])
    for d in j["stats"]["drives"]:
        jn = d["joint"]
        if d["kind"] == "coupled" or ("drive." + jn) not in ser or (only and jn != only):
            continue
        if not np.any(np.abs(ser["qd." + jn]) > 0) and not np.any(np.abs(ser["drive." + jn]) > 0):
            continue
        out.append(dict(MT.select(ser["drive." + jn], ser["qd." + jn], ser["qdd." + jn], safety), joint=jn))
    return {"joints": out, "table": MT.table()}


@app.get("/mbd/jobs/{jid}/member-series")
def mbd_member_series(jid: str, member: str, direction: str = ""):
    """疲劳用：杆件 B 端受力在指定方向（构件坐标，默认最大力的方向）上的分量随时间的变化"""
    ml = member_load(jid.replace("/", ""), member)
    u = np.array([float(x) for x in direction.split(",")]) if direction else ml["peak_local"]
    u = u / max(np.linalg.norm(u), 1e-12)
    return {"values": [round(float(x), 4) for x in ml["F_local"] @ u], "duration_s": ml["duration_s"],
            "peak_N": ml["peak_N"], "direction": [float(x) for x in u]}


@app.get("/jobs/{jid}/series.bin")
def job_series(jid: str):
    p = _job_path(jid.replace("/", ""), "series.bin")
    if not os.path.exists(p):
        raise HTTPException(404, "结果还没出来")
    return FileResponse(p, media_type="application/octet-stream")


@app.get("/jobs/{jid}/anim.bin")
def job_anim(jid: str):
    p = _job_path(jid.replace("/", ""), "anim.bin")
    if not os.path.exists(p):
        raise HTTPException(404, "结果还没出来")
    return FileResponse(p, media_type="application/octet-stream")


@app.get("/jobs")
def jobs(factory: str = "", owner: str = "", limit: int = 50, kind: str = ""):
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
        if kind and j.get("kind", "fea") != kind:
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
    if j.get("kind") == "mbd":
        from cae import mbd_report as MR
        ser = read_series(_job_path(j["id"], "series.bin"))
        peaks = []
        for n in ser:
            if n.startswith("rf.") and n.endswith(".abs") and "wq_payload" not in n:
                b = n[3:-4]
                fm, mm = ser[n], ser["rm.{}.abs".format(b)]
                i, k = int(np.argmax(fm)), int(np.argmax(mm))
                peaks.append((b, float(fm[i]), float(ser["t"][i]), float(mm[k]), float(ser["t"][k])))
        data = MR.build(j, peaks, (body.get("images") or [])[:6], body.get("motors"), body.get("ai_text") or j.get("ai_text"))
        name = "动力学报告-{}.docx".format(j.get("item") or jid)
        return Response(data, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        headers={"Content-Disposition": "attachment; filename*=UTF-8''" + urllib.parse.quote(name)})
    from cae import report as R
    imgs = (body.get("images") or [])[:4]
    data = R.build(j, imgs, body.get("ai_text") or j.get("ai_text"))
    name = "有限元报告-{}.docx".format(j.get("item") or jid)
    return Response(data, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": "attachment; filename*=UTF-8''" + urllib.parse.quote(name)})


@app.post("/jobs/{jid}/note")
def note(jid: str, body: dict = Body(...)):
    """记下 AI 解释（报告用）"""
    p = _job_path(jid.replace("/", ""), "job.json")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个任务")
    _update(jid.replace("/", ""), ai_text=str(body.get("ai_text") or "")[:4000])
    return {"ok": True}


@app.post("/jobs/{jid}/fatigue")
def fatigue(jid: str, body: dict = Body(...)):
    """疲劳寿命：body = {ref_load, series, block_seconds, surface, size_factor, kf, haibach, label}。
    返回汇总 + 每个表面点的每块损伤（float32，base64），汇总也记进任务（报告用）"""
    import base64
    from cae import fatigue as FT
    p = _job_path(jid.replace("/", ""), "job.json")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个任务")
    j = _read_json(p)
    if j["status"] != "done":
        raise HTTPException(409, "有限元结果还没出来")
    series = body.get("series") or []
    if len(series) < 2 or len(series) > 200000:
        raise HTTPException(400, "载荷谱至少 2 个点")
    if body.get("surface", "ground") not in FT.SURFACE:
        raise HTTPException(400, "表面状态不对")
    surf = read_surface(_job_path(j["id"], "surface.bin"))
    try:
        D, summ = FT.compute(surf["vm"], float(body.get("ref_load") or 0), series, float(body.get("block_seconds") or 1),
                             M.get(j["setup"]["material_id"]), body.get("surface", "ground"),
                             float(body.get("size_factor") or 0.85), float(body.get("kf") or 1.0), bool(body.get("haibach", True)))
    except ValueError as e:
        raise HTTPException(400, str(e)) from None
    i = summ.pop("hot_index")
    summ["hot_at"] = [round(float(x), 3) for x in surf["positions"][i]]
    summ.update(label=body.get("label") or "", ref_load=body.get("ref_load"), ref_unit=body.get("ref_unit") or "",
                series_peak=float(np.max(np.abs(series))), series_points=len(series))
    _update(j["id"], fatigue=summ)
    return {"summary": summ, "damage_b64": base64.b64encode(np.asarray(D, "<f4").tobytes()).decode()}


@app.get("/geometry/{sha}/step")
def geometry_step(sha: str):
    p = _p("geo", sha.replace("/", ""), "part.step")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个零件")
    return Response(open(p, "rb").read(), media_type="application/step")


# ------------------------------------------------------------------ 数控编程（第 13 轮）
CAM_LIMIT_S = 120


def _cam_geo_child(step_path, outdir, q):
    try:
        from cae import cam_geom as CG
        data = open(step_path, "rb").read()
        out = {}
        for k, fn in (("turn", CG.turn_profile), ("mill", CG.mill_features)):
            try:
                out[k] = fn(data)
            except Exception as e:  # noqa: BLE001 —— 认不出来的写原因，另一种照样给
                out[k] = {"error": str(e) or e.__class__.__name__}
        _write_json(os.path.join(outdir, "cam.json"), out)
        q.put((True, None))
    except Exception as e:  # noqa: BLE001
        q.put((False, str(e) or e.__class__.__name__))


@app.post("/cam/recognize")
def cam_recognize(body: dict = Body(...)):
    """读入过的零件（/geometry）→ 车削轮廓、铣削特征"""
    sha = str(body.get("sha", "")).replace("/", "")
    d = _p("geo", sha)
    if not os.path.exists(os.path.join(d, "part.step")):
        raise HTTPException(400, "请先读入零件")
    if not os.path.exists(os.path.join(d, "cam.json")):
        ok, err = _isolated(_cam_geo_child, (os.path.join(d, "part.step"), d), GEO_LIMIT_S)
        if not ok:
            raise HTTPException(422, "识别不了这个零件：{}".format(err))
    return dict(_read_json(os.path.join(d, "cam.json")), sha=sha)


def _cam_child(spec, outdir, q):
    try:
        from cae import cam_job as J
        progs = J.generate(spec)
        for k, p in enumerate(progs):
            with open(os.path.join(outdir, "{}.nc".format(k)), "w", encoding="utf-8") as f:
                f.write(p.pop("gcode"))
            H = p["sim"].pop("_H", None)
            if H is not None:
                open(os.path.join(outdir, "h{}.bin".format(k)), "wb").write(np.asarray(H, "<f4").tobytes())
                p["sim"]["height"] = True
        q.put((True, {"programs": progs, "compare": spec.get("compare")}))
    except Exception as e:  # noqa: BLE001
        q.put((False, str(e) or e.__class__.__name__))


@app.post("/cam/jobs")
def cam_submit(body: dict = Body(...)):
    """编程单 → 生成程序、仿真、检查（不排队：一般 1–3 秒）"""
    spec = body.get("spec") or {}
    if spec.get("kind") not in ("turn", "slot", "mill25"):
        raise HTTPException(400, "编程单不对")
    if spec.get("machine") not in __import__("cae.cam_post", fromlist=["MACHINES"]).MACHINES:
        raise HTTPException(400, "没有这台机床")
    jid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    os.makedirs(_job_path(jid))
    j = {"id": jid, "kind": "cam", "status": "running", "created": time.time(), "spec": spec,
         "owner": body.get("owner"), "owner_name": body.get("owner_name"), "factory": body.get("factory"),
         "title": body.get("title") or "", "item": spec.get("item")}
    _write_json(_job_path(jid, "job.json"), j)
    ok, res = _isolated(_cam_child, (spec, _job_path(jid)), CAM_LIMIT_S)
    if ok:
        j = _update(jid, status="done", finished=time.time(), programs=res["programs"], compare=res["compare"],
                    stats={"seconds": round(time.time() - j["created"], 1),
                           "errors": sum(c["level"] == "error" for p in res["programs"] for c in p["checks"])})
    else:
        j = _update(jid, status="failed", finished=time.time(), error=res)
    return _public(j)


@app.get("/cam/jobs/{jid}/{k}.nc")
def cam_nc(jid: str, k: int):
    p = _job_path(jid.replace("/", ""), "{}.nc".format(int(k)))
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个程序")
    return Response(open(p, encoding="utf-8").read(), media_type="text/plain; charset=utf-8")


@app.get("/cam/jobs/{jid}/h{k}.bin")
def cam_height(jid: str, k: int):
    p = _job_path(jid.replace("/", ""), "h{}.bin".format(int(k)))
    if not os.path.exists(p):
        raise HTTPException(404, "没有高度图")
    return FileResponse(p, media_type="application/octet-stream")


@app.get("/cam/machines")
def cam_machines():
    from cae.cam_post import MACHINES
    return {"machines": MACHINES}


@app.post("/cam/jobs/{jid}/submission")
def cam_submission(jid: str, body: dict = Body(...)):
    """记下这次编程挂到了哪次工艺规程提交（网页再打开时接着看审批）"""
    p = _job_path(jid.replace("/", ""), "job.json")
    if not os.path.exists(p):
        raise HTTPException(404, "没有这个任务")
    return _public(_update(jid.replace("/", ""), submission=str(body.get("submission") or "")[:40]))
