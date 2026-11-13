"""问渠贴片（第 112 轮 P5）：工厂端新产品导入的接口。网址 <主域名>/eda/factory/。

  GET  /api/factory/factories        能选的工艺能力表（演示工厂，虚构）
  POST /api/factory/check            上传资料包（光绘 zip 或多个文件 + 物料清单 + 坐标）→ 检查结果、数量统计、板图
  POST /api/factory/issues           检查结果 → AI 起草工程问题单（经网关；只交检查结果，不交文件）
  POST /api/factory/issues/render    人改过的问题单 → 校验 → YAML 和 Markdown（下载用）

客户的文件只在这一次检查里用：写进临时文件夹，算完就删，不存、不进仓库、不用来训练。
服务器只在日志里记一行：时间、文件个数、各种结论的条数，不记文件名和内容。判定都由 wqeda 的确定性代码做。"""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import tempfile
import time
import warnings
import zipfile

import httpx
from fastapi import HTTPException, Request
from starlette.datastructures import UploadFile

from wqeda import factory as F
from wqeda import issues as I
from wqeda.ai import issues as AI
from wqeda.readers import gerber as G
from wqeda.schema import capability

MAX_TOTAL = 40 * 1024 * 1024  # 上传合计上限
MAX_FILES = 40
MAX_UNZIPPED = 120 * 1024 * 1024


def _err(code, en, zh):
    return HTTPException(code, {"en": en, "zh": zh})


def factories(folder):
    out = {}
    for p in sorted(glob.glob(os.path.join(folder, "*.yaml")), key=lambda q: os.path.splitext(os.path.basename(q))[0]):
        try:
            doc = capability.load(p)
        except ValueError:
            continue
        out[os.path.splitext(os.path.basename(p))[0]] = doc
    return out


def _safe_name(name):
    base = os.path.basename(name or "")
    if not base or base.startswith(".") or not re.fullmatch(r"[\w\-. ()\[\]+,]+", base):
        raise _err(400, "file names may only use letters, digits and - _ . ( ) [ ] + ,",
                   "文件名只能用字母、数字和 - _ . ( ) [ ] + ,")
    return base


def _unzip(path, dest):
    """只解出一层文件，不跟随目录、不解链接；解压后合计大小有上限"""
    total = 0
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            name = os.path.basename(info.filename)
            if not name or name.startswith("."):
                continue
            total += info.file_size
            if total > MAX_UNZIPPED:
                raise _err(413, "the zip is too large when unpacked", "压缩包解开后太大")
            with z.open(info) as src, open(os.path.join(dest, _safe_name(name)), "wb") as out:
                shutil.copyfileobj(src, out)


class _Local:
    """演示资料包：仓库里的文件，当成上传的文件用"""

    def __init__(self, path):
        self.path = str(path)
        self.filename = os.path.basename(self.path)

    async def read(self):
        with open(self.path, "rb") as f:
            return f.read()


def _json_field(form, key):
    v = form.get(key)
    if not v:
        return None
    try:
        d = json.loads(v)
    except ValueError as e:
        raise _err(400, "{} is not JSON".format(key), "{} 不是 JSON".format(key)) from e
    if not isinstance(d, dict) or not all(isinstance(a, str) and isinstance(b, str) for a, b in d.items()):
        raise _err(400, "{} must map names to names".format(key), "{} 应是“名字 → 名字”".format(key))
    return d


def bom_rows(board):
    """第 158 轮：物料清单按“物料编号、数值、封装”合并成行，回给上传的人做“到外部库查”的链接。
    只回显，不存；不参与任何判定。"""
    rows = {}
    for r in getattr(board, "bom", None) or []:
        k = (r.item or "", r.value or "", r.package or "")
        q = r.qty if r.qty is not None else len(r.refs)
        rows[k] = rows.get(k, 0) + (q or 0)
    return [{"item": i, "value": v, "package": p, "qty": q} for (i, v, p), q in sorted(rows.items())]


def register(app, *, factory_dir, gateway, headers_of, gw_errors, client, demo=None):
    """demo = {名字: {gerber, bom, cpl}}：资料包的路径。"1" 是演示资料包（第 112 轮，故意带错，标明）；
    "ctrl-ls" 是平缝机控制器 CTRL-LS 生成的真文件（第 159 轮 159d3），检查结果照实显示。
    只给一组 {gerber, bom, cpl} 时当作 "1"。"""
    caps = factories(factory_dir)
    packs = {"1": demo} if demo and "gerber" in demo else dict(demo or {})

    @app.get("/api/factory/factories")
    def list_factories():
        return {"factories": [{"key": k, "factory": v.get("factory"), "fictional": bool(v.get("fictional")),
                               "pcb": v.get("pcb") or {}} for k, v in caps.items()],
                "layers": G.LAYER_NAMES}

    @app.post("/api/factory/check")
    async def check(request: Request):
        form = await request.form()
        key = str(form.get("factory") or "")
        if key not in caps:
            raise _err(400, "choose a factory capability table", "请选一家工厂的工艺能力表")
        uploads = [v for k, v in form.multi_items() if k == "gerber" and isinstance(v, UploadFile)]
        bom_up, cpl_up = form.get("bom"), form.get("cpl")
        pack = packs.get(str(form.get("demo") or ""))
        if pack:
            uploads = [_Local(pack["gerber"])]
            bom_up, cpl_up = _Local(pack["bom"]), _Local(pack["cpl"])
        if not uploads:
            raise _err(400, "upload the Gerber and drill files (a zip or several files)",
                       "请上传光绘和钻孔文件（一个 zip 或多个文件）")
        if len(uploads) > MAX_FILES:
            raise _err(400, "too many files", "文件太多")
        tmp = tempfile.mkdtemp(prefix="wq-pcba-")
        t0 = time.time()
        try:
            gdir = os.path.join(tmp, "gerber")
            os.makedirs(gdir)
            total = 0
            for up in uploads:
                data = await up.read()
                total += len(data)
                if total > MAX_TOTAL:
                    raise _err(413, "upload too large (40 MB at most)", "上传太大（合计不超过 40 MB）")
                name = _safe_name(up.filename)
                p = os.path.join(gdir, name)
                with open(p, "wb") as f:
                    f.write(data)
                if name.lower().endswith(".zip"):
                    try:
                        _unzip(p, gdir)
                    except zipfile.BadZipFile as e:
                        raise _err(400, "the zip file is damaged", "zip 文件坏了") from e
                    os.remove(p)
            side = {}
            for k, up in (("bom", bom_up), ("cpl", cpl_up)):
                if isinstance(up, (UploadFile, _Local)) and up.filename:
                    data = await up.read()
                    total += len(data)
                    if total > MAX_TOTAL:
                        raise _err(413, "upload too large (40 MB at most)", "上传太大（合计不超过 40 MB）")
                    if not up.filename.lower().endswith((".csv", ".txt")):
                        raise _err(400, "BOM and placement files must be CSV (save Excel as CSV)",
                                   "物料清单和坐标要 CSV（Excel 请另存为 CSV）")
                    p = os.path.join(tmp, k + ".csv")
                    with open(p, "wb") as f:
                        f.write(data)
                    side[k] = p
            layers = _json_field(form, "layers")
            maps = {k: _json_field(form, k + "_map") for k in ("bom", "cpl")}
            heads = {k: G.headers(p) for k, p in side.items()}
            guessed = {k: G.guess_map(heads[k], k)[0] for k in side}
            try:
                out = F.check_package(gdir, caps[key], side.get("bom"), side.get("cpl"), layers, maps["bom"] or None,
                                      maps["cpl"] or None)
            except Exception as e:  # noqa: BLE001 —— gerbonara 认不出时抛的异常种类不一（甚至 UnboundLocalError）
                files = sorted(os.listdir(gdir))
                raise HTTPException(422, {"en": "could not tell which file is which layer; assign the layers",
                                          "zh": "认不出哪个文件是哪一层，请手动指定", "files": files,
                                          "layers": G.LAYER_NAMES, "error": str(e)[:200]}) from e
            st = out["board"].stack
            svg = {}
            for s in ("top", "bottom"):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        svg[s] = str(st.to_pretty_svg(side=s))
                except Exception:  # noqa: BLE001 —— 板图画不出来不影响检查结果
                    svg[s] = ""
            counts = {}
            for r in out["results"]:
                counts[r["status"]] = counts.get(r["status"], 0) + 1
            print(json.dumps({"event": "pcba_check", "ts": round(t0), "files": len(os.listdir(gdir)) + len(side),
                              "factory": key, "counts": counts, "ms": int((time.time() - t0) * 1000)}), flush=True)
            return {"factory": caps[key].get("factory"), "fictional": bool(caps[key].get("fictional")),
                    "results": out["results"], "quantity": out["quantity"], "notes": out["notes"],
                    "bom": bom_rows(out.get("board")),
                    "layers": out["layers"], "headers": heads, "guessed": guessed,
                    "maps": {k: maps[k] or guessed.get(k) for k in side}, "svg": svg, "counts": counts}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @app.post("/api/factory/issues")
    async def draft_issues(request: Request):
        j = await request.json()
        results = j.get("results") if isinstance(j, dict) else None
        if not isinstance(results, list) or not results or len(results) > 80:
            raise _err(400, "send the check results", "请先检查资料包")
        h = headers_of(request)
        if not h:
            en, zh = gw_errors[401]
            raise _err(401, en, zh)
        fac = str(j.get("factory") or "")[:120]
        lang = "en" if j.get("lang") == "en" else "zh"

        def model(open_results, factory, lang_):
            try:
                with client() as c:
                    r = c.post(gateway + "/api/v1/eda/ai/issues", headers=h,
                               json={"results": open_results, "factory": factory, "lang": lang_})
            except httpx.HTTPError as e:
                raise _err(502, "the AI service did not answer", "AI 服务没有响应") from e
            if r.status_code in gw_errors:
                en, zh = gw_errors[r.status_code]
                raise _err(r.status_code, en, zh)
            if r.status_code != 200:
                raise _err(502, "the AI service failed", "AI 服务出错")
            d = r.json()
            return d.get("draft"), d.get("run")

        out = AI.run(results, model, fac, str(j.get("package") or "")[:120], lang)
        doc = out["issues"]
        return {"issues": doc, "rejected": out["rejected"], "run": out["run"], "yaml": I.to_yaml(doc),
                "markdown": I.to_markdown(doc)}

    @app.post("/api/factory/issues/render")
    async def render(request: Request):
        j = await request.json()
        doc = j.get("issues") if isinstance(j, dict) else None
        if not isinstance(doc, dict):
            raise _err(400, "send the issue list", "请发问题单")
        probs = I.validate(doc)
        if probs:
            raise _err(400, "; ".join(probs), "；".join(probs))
        return {"yaml": I.to_yaml(doc), "markdown": I.to_markdown(doc)}
