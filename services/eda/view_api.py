"""网页审图（第 113 轮 P6）的接口。网址 <主域名>/eda/view/。

  GET /api/view/designs                  能看的设计（驱动板 A、B，24 V 示例用 A 的板子）
  GET /api/view/file/{key}/{name}        设计的 KiCad 文件（原理图、板子、工程文件；只给登记过的文件夹）
  GET /api/view/report/{key}             这块板子报告里没通过的项：检查项、结论、位号、位置（KiCad 坐标，y 向下）
  GET /api/kicad-plugin.zip              KiCad 9 插件（插件文件 + 检查引擎 + 器件数据 + 示例工厂），现场打包

打开自己电脑上的 KiCad 文件不经过这里：页面在浏览器里读文件、交给 KiCanvas，不上传。"""

from __future__ import annotations

import json
import os
import re

from fastapi import HTTPException
from fastapi.responses import FileResponse, Response

from wqeda.factory import refs_of

KICAD_EXT = (".kicad_sch", ".kicad_pcb", ".kicad_pro")


def designs(repo):
    """登记的设计：键 → (标题, KiCad 文件夹, 报告 json)"""
    f = repo / "factory" / "designs"
    return {
        "A": ("关节伺服驱动板 A 版（示例设计）", f / "drv-joint" / "kicad", f / "drv-joint" / "report" / "report.json"),
        "B": ("关节伺服驱动板 B 版（示例设计，带抱闸）", f / "drv-joint-b" / "kicad",
              f / "drv-joint-b" / "report" / "report.json"),
        "24V": ("24 V 示例（规格改 24 V，用 A 版的板子）", f / "drv-joint" / "kicad",
                repo / "eda" / "examples" / "drv-joint-24v" / "report" / "report.json"),
    }


def issues(report):
    """报告 → 没通过的项（工艺、布局约束、热）。位置换成 KiCad 坐标（板子模型 y 向上，KiCad y 向下）"""
    out = []
    for sec, rows in (("process", report.get("process") or []), ("layout", report.get("layout") or [])):
        for r in rows:
            if r.get("status") == "pass":
                continue
            pts = [[a[0], -a[1]] for a in r.get("at") or []
                   if isinstance(a, list) and len(a) >= 2 and all(isinstance(v, (int, float)) for v in a[:2])]
            out.append({"key": r.get("key"), "name": r.get("name"), "status": r.get("status"), "section": sec,
                        "value": r.get("value"), "limit": r.get("limit"), "unit": r.get("unit") or "",
                        "detail": r.get("detail") or "", "why": r.get("why") or "", "refs": refs_of(r),
                        "points": pts[:50]})
    th = report.get("thermal") or {}
    for r in th.get("rows") or []:
        if r.get("model") == "mosfet" and r.get("status") != "pass":
            out.append({"key": "TH-" + r["ref"], "name": "结温 {}".format(r["ref"]), "status": r["status"],
                        "section": "thermal", "value": r.get("tj_c"), "limit": r.get("tj_max_c"), "unit": "℃",
                        "detail": "；".join(r.get("notes") or []), "why": "", "refs": [r["ref"]], "points": []})
    rank = {"fail": 0, "unknown": 1, "pending": 2}
    out.sort(key=lambda x: rank.get(x["status"], 3))
    return out


def register(app, repo):
    reg = designs(repo)

    @app.get("/api/kicad-plugin.zip")
    def plugin_zip():
        import importlib.util

        spec = importlib.util.spec_from_file_location("wq_pack", repo / "eda" / "kicad-plugin" / "pack.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return Response(mod.build(), media_type="application/zip",
                        headers={"Content-Disposition": 'attachment; filename="wenquest-eda-kicad-plugin.zip"'})

    @app.get("/api/view/designs")
    def list_designs():
        out = []
        for k, (title, folder, rep) in reg.items():
            if not folder.is_dir():
                continue
            files = sorted(p for p in os.listdir(folder) if p.endswith(KICAD_EXT))
            count = None
            if rep.exists():
                count = json.loads(rep.read_text(encoding="utf-8")).get("count")
            out.append({"key": k, "title": title, "files": files, "count": count})
        return {"designs": out}

    @app.get("/api/view/file/{key}/{name}")
    def file(key: str, name: str):
        if key not in reg or not re.fullmatch(r"[\w\-.]+", name) or not name.endswith(KICAD_EXT):
            raise HTTPException(404, {"en": "no such file", "zh": "没有这个文件"})
        p = reg[key][1] / name
        if not p.is_file():
            raise HTTPException(404, {"en": "no such file", "zh": "没有这个文件"})
        return FileResponse(p, media_type="text/plain; charset=utf-8")

    @app.get("/api/view/report/{key}")
    def report(key: str):
        if key not in reg or not reg[key][2].exists():
            raise HTTPException(404, {"en": "no report", "zh": "没有报告"})
        rep = json.loads(reg[key][2].read_text(encoding="utf-8"))
        return {"title": reg[key][0], "count": rep.get("count"), "status": rep.get("status"),
                "factory": rep.get("factory"), "issues": issues(rep)}
