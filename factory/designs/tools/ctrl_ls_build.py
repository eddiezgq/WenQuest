# -*- coding: utf-8 -*-
"""平缝机控制器 CTRL-LS：从设计描述生成 KiCad 原理图和产物（第 159 轮 159d1；PCB 在 159d2 接上）。

    python3 ctrl_ls_build.py              # 原理图（每个功能块一页）、各页 SVG、网表核对、物料清单
    python3 ctrl_ls_build.py --board      # 再加板子：摆放、平面、自动布线（159d2b）
    python3 ctrl_ls_build.py --board --no-route   # 板子不重新布线，沿用仓库里的

要：KiCad 7.0.11 的 kicad-cli。产物写到 ../ctrl-ls/：kicad/（KiCad 工程，可以用 KiCad 打开继续改）、out/（网页和工厂用）。
网表核对：KiCad 从原理图导出网表，逐个网络、逐个引脚和设计描述对照（KiCad 7 的命令行没有电气规则检查，用这个代替：
接错、漏接、多接都会查出来）。示例设计，未经硬件验证，不能直接投产。"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
NAME = "ctrl-ls"
PROJ = os.path.join(ROOT, NAME)
KDIR = os.path.join(PROJ, "kicad")
OUT = os.path.join(PROJ, "out")
TMP = os.path.join(PROJ, ".route")  # 中间文件（不入库）
DATE = "2026-11-12"

import ctrl_ls as D  # noqa: E402
import sch  # noqa: E402
import sexp  # noqa: E402


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("{} 失败：{}{}".format(" ".join(cmd[:4]), r.stdout[-1500:], r.stderr[-1500:]))
    return r


def schematic():
    os.makedirs(KDIR, exist_ok=True)
    shutil.copy(os.path.join(ROOT, "libs", "wq.kicad_sym"), os.path.join(KDIR, "wq.kicad_sym"))
    with open(os.path.join(KDIR, "sym-lib-table"), "w", encoding="utf-8") as f:
        f.write('(sym_lib_table\n  (lib (name "wq")(type "KiCad")(uri "${KIPRJMOD}/wq.kicad_sym")(options "")'
                '(descr "问渠：定制磁性元件、隔离电源等官方库没有的符号"))\n)\n')
    return sch.write(D, KDIR, NAME)


def _norm(path, pats):
    with open(path, encoding="utf-8", errors="replace") as f:
        t = f.read()
    for a, b in pats:
        t = re.sub(a, b, t)
    with open(path, "w", encoding="utf-8") as f:
        f.write(t)


def exports():
    root = os.path.join(KDIR, NAME + ".kicad_sch")
    os.makedirs(TMP, exist_ok=True)
    sdir = os.path.join(OUT, "schematic")
    if os.path.isdir(sdir):
        shutil.rmtree(sdir)
    os.makedirs(sdir)
    run(["kicad-cli", "sch", "export", "svg", "-o", sdir, root])
    for fn in os.listdir(sdir):
        _norm(os.path.join(sdir, fn), [(r"(<title>SVG Image created as [^<]*?) date [^<]*</title>", r"\1 date {}</title>".format(DATE))])
    net = os.path.join(TMP, "sch.net")
    run(["kicad-cli", "sch", "export", "netlist", "-o", net, root])
    return net


def netcheck(net_path):
    """KiCad 导出的网表 ↔ 设计描述，逐网络逐引脚对照"""
    with open(net_path, encoding="utf-8") as f:
        doc = sexp.parse(f.read())
    got = {}
    for n in sexp.find(sexp.first(doc, "nets"), "net"):
        name = sexp.first(n, "name")[1].lstrip("/")
        nodes = {(sexp.first(x, "ref")[1], sexp.first(x, "pin")[1]) for x in sexp.find(n, "node")}
        if name.startswith("unconnected-") or name.startswith("Net-("):
            for node in nodes:
                got.setdefault("（未连接）", set()).add(node)
            continue
        got[name] = nodes
    want = {k: set(v) for k, v in D.nets().items() if k not in D.NC_NETS}
    problems = []
    for name in sorted(set(want) | set(got) - {"（未连接）"}):
        a, b = want.get(name, set()), got.get(name, set())
        if a != b:
            problems.append({"net": name, "missing": sorted(a - b), "extra": sorted(b - a)})
    comps = {sexp.first(c_, "ref")[1] for c_ in sexp.find(sexp.first(doc, "components"), "comp")}
    refs = {p["ref"] for p in D.PARTS}
    return {"nets_design": len(want), "nets_schematic": len([k for k in got if k != "（未连接）"]), "parts_design": len(refs),
            "parts_schematic": len(comps), "missing_parts": sorted(refs - comps), "extra_parts": sorted(comps - refs),
            "problems": problems, "pass": not problems and refs == comps}


def _parts_catalog():
    """器件表 parts.yaml：物料编号 → 型号、厂家、立创编号（阻容等通用件不在表里，物料清单只写数值和封装）"""
    import yaml

    with open(os.path.join(PROJ, "parts.yaml"), encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    return {p["item"]: p for p in doc["parts"] if p.get("item")}


def bom(path):
    cat = _parts_catalog()
    rows = {}
    for p in D.PARTS:
        if not p["item"]:
            continue
        rows.setdefault((p["item"], p["value"], p["fp"].split(":")[1]), []).append(p["ref"])
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["物料编号", "数值", "封装", "数量", "位号", "型号", "厂家", "立创编号", "说明"])
        for (item, val, fp), refs in sorted(rows.items()):
            note = next(p["note"] for p in D.PARTS if p["ref"] == refs[0])
            q = cat.get(item, {})
            w.writerow([item, val, fp, len(refs), " ".join(sorted(refs, key=_refkey)), q.get("mpn", ""), q.get("maker", ""), q.get("lcsc", ""),
                        note])
    return len(rows)


def _refkey(r):
    m = re.match(r"([A-Z]+)(\d+)", r)
    return (m.group(1), int(m.group(2))) if m else (r, 0)


def summary(nc, n_bom, brd=None):
    sheets = sorted(os.listdir(os.path.join(OUT, "schematic")))
    files = {}
    for i, (key, _, _) in enumerate(D.SHEETS):
        files[key] = next((s for s in sheets if s.startswith("{}-{} ".format(NAME, i + 1))), None)
    d = {
        "name": "平缝机控制器 CTRL-LS", "item": "CTRL-LS", "rev": "示例 A", "date": DATE, "stage": "159d1 原理图（PCB 在 159d2）",
        "disclaimer": "示例设计，未经硬件验证，不能直接投产",
        "tool": "KiCad 7.0.11", "board_mm": list(D.X["board_mm"]), "layers": D.X["layers"],
        "sheets": [{"key": k, "name": n, "name_en": e, "svg": files.get(k), "note": D.SHEET_NOTES.get(k, "")} for k, n, e in D.SHEETS],
        "root_svg": next((s for s in sheets if s == NAME + ".svg"), None),
        "parts": [{"ref": p["ref"], "value": p["value"], "fp": p["fp"], "sheet": p["sheet"], "item": p["item"], "note": p["note"],
                   "lib": p["lib"]} for p in D.PARTS],
        "nets": len([n for n in D.nets() if n not in D.NC_NETS]),
        "bom_by_item": D.bom_by_item(), "bom_rows": n_bom,
        "netcheck": {k: nc[k] for k in ("pass", "nets_design", "nets_schematic", "parts_design", "parts_schematic")},
        "pcb_layers": [{"key": k, "name": n, "svg": k + ".svg"} for k, _, n in LAYERS_SVG] if brd else [],
        "drc": {k: brd[0][k] for k in ("errors", "warnings", "unconnected")} if brd else None,
        "safety": [{k: r[k] for k in ("key", "name", "status", "value", "limit", "example")} for r in brd[1]] if brd else None,
        "files": {},
    }
    for root, _, fs in os.walk(OUT):
        for fn in sorted(fs):
            if fn == "design.json" or fn.endswith((".glb", ".step")):    # 三维随 OpenCASCADE 版本略有不同，不记摘要
                continue
            p = os.path.join(root, fn)
            with open(p, "rb") as f:
                d["files"][os.path.relpath(p, OUT)] = hashlib.sha256(f.read()).hexdigest()[:16]
    with open(os.path.join(OUT, "design.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return d


# ------------------------------------------------------------------ 板子（159d2b）
# 隔离面板口所在的角（右下）：内层地平面在这里断开，隔离侧另铺 GND_ISO；两者之间的缝就是隔离带（安全距离检查量它）
ISO_CORNER = (204.0, 118.0)
BARRIER = 6.0          # 隔离带宽度 mm（示例值，规则在 safety.yaml）


def planes(board, nets):
    from wqeda.gen import board as gb
    w, h = D.X["board_mm"]
    ix, iy = ISO_CORNER
    b = BARRIER / 2
    main = [(0.5, 0.5), (w - 0.5, 0.5), (w - 0.5, iy - b), (ix - b, iy - b), (ix - b, h - 0.5), (0.5, h - 0.5)]
    iso = [(ix + b, iy + b), (w - 0.5, iy + b), (w - 0.5, h - 0.5), (ix + b, h - 0.5)]
    for net, pts in (("GND", main), ("GND_ISO", iso)):
        z = gb.add_pour(board, nets[net], "In1.Cu", pts, clearance=0.3)
        z.SetAssignedPriority(0)
        z.SetPadConnection(pcbnew().ZONE_CONNECTION_FULL)
    return [("In1.Cu", main), ("In1.Cu", iso)]


def pcbnew():
    import pcbnew as m
    return m


def board_build(route, jar):
    from wqeda.gen import board as gb
    gb.LOCAL_FPDIRS["wq"] = os.path.join(ROOT, "libs")
    path = os.path.join(KDIR, NAME + ".kicad_pcb")
    title = {"title": D.TITLE, "company": "问渠数字工业园 · 电路板厂（示例设计，未经硬件验证，不能直接投产）", "rev": "示例 A", "date": DATE}
    board, nets = gb.build(D.X, path, title, hole_net="PE")
    planes(board, nets)
    os.makedirs(TMP, exist_ok=True)
    stats = None
    if route:
        keep = tie = gb.tie_keepouts(board)
        stats = gb.autoroute(board, TMP, jar, gb.classes_of(D.X), passes=60, keepouts=keep)
        del tie
    board.BuildConnectivity()
    gb.fill_zones(board)
    pcbnew().SaveBoard(path, board)
    return stats


LAYERS_SVG = [("F_Cu", "F.Cu,Edge.Cuts", "顶层铜"), ("In1_Cu", "In1.Cu,Edge.Cuts", "内层 1（地平面，隔离角另铺 GND_ISO）"),
              ("In2_Cu", "In2.Cu,Edge.Cuts", "内层 2"), ("B_Cu", "B.Cu,Edge.Cuts", "底层铜"),
              ("F_Silk", "F.SilkS,F.Fab,Edge.Cuts", "顶面丝印与装配"), ("B_Silk", "B.SilkS,B.Fab,Edge.Cuts", "底面丝印与装配")]


def board_exports():
    """板子产物：各层 SVG、光绘与钻孔、贴片坐标、三维（STEP → GLB）、工程打包（与关节驱动板 build.py 同一套做法）"""
    import io
    import zipfile

    import build as B

    pcbf = os.path.join(KDIR, NAME + ".kicad_pcb")
    pdir = os.path.join(OUT, "pcb")
    if os.path.isdir(pdir):
        shutil.rmtree(pdir)
    os.makedirs(pdir)
    date_pat = [(r"(<title>SVG Image created as [^<]*?) date [^<]*</title>", r"\1 date {}</title>".format(DATE))]
    for key, layers, _ in LAYERS_SVG:
        run(["kicad-cli", "pcb", "export", "svg", "--exclude-drawing-sheet", "--page-size-mode", "2", "-l", layers,
             "-o", os.path.join(pdir, key + ".svg"), pcbf])
        _norm(os.path.join(pdir, key + ".svg"), date_pat)
    gdir = os.path.join(TMP, "gerber")
    if os.path.isdir(gdir):
        shutil.rmtree(gdir)
    os.makedirs(gdir)
    run(["kicad-cli", "pcb", "export", "gerbers", "--no-x2", "--no-netlist", "-l",
         "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts", "-o", gdir + "/", pcbf])
    run(["kicad-cli", "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--generate-map", "--map-format",
         "gerberx2", "-o", gdir + "/", pcbf])
    for fn in sorted(os.listdir(gdir)):
        _norm(os.path.join(gdir, fn), [(r"(?m)^G04 Created by KiCad.*\n", ""), (r"(?m)^; DRILL file .* date .*\n", ""),
                                       (r"(?m)^;.*[Dd]ate.*\n", ""), (r"(?m)^G04 .*[Dd]ate.*\n", ""), (r"%TF.CreationDate[^%]*%\*?%?\n?", ""),
                                       (r'"CreationDate": "[^"]*"', '"CreationDate": "{}T00:00:00"'.format(DATE))])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for fn in sorted(os.listdir(gdir)):
            zi = zipfile.ZipInfo(fn, date_time=(2026, 11, 12, 0, 0, 0))
            with open(os.path.join(gdir, fn), "rb") as f:
                z.writestr(zi, f.read())
    with open(os.path.join(OUT, "gerber.zip"), "wb") as f:
        f.write(buf.getvalue())
    run(["kicad-cli", "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "-o", os.path.join(OUT, "pos.csv"), pcbf])
    step = os.path.join(OUT, NAME + ".step")
    env = dict(os.environ, KICAD7_3DMODEL_DIR=os.path.join(ROOT, "3dmodels"))
    r = subprocess.run(["kicad-cli", "pcb", "export", "step", "--subst-models", "--force", "-o", step, pcbf], capture_output=True,
                       text=True, env=env)
    if r.returncode == 0 and os.path.exists(step):
        _norm(step, [(r"FILE_NAME\('[^']*','[^']*'", "FILE_NAME('{}.step','{}T00:00:00'".format(NAME, DATE))])
        B.glb(step, os.path.join(OUT, NAME + ".glb"))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for fn in sorted(os.listdir(KDIR)):
            if fn.endswith((".kicad_sch", ".kicad_pcb", ".kicad_pro", ".kicad_sym")) or fn == "sym-lib-table":
                zi = zipfile.ZipInfo(NAME + "/" + fn, date_time=(2026, 11, 12, 0, 0, 0))
                with open(os.path.join(KDIR, fn), "rb") as f:
                    z.writestr(zi, f.read())
    with open(os.path.join(OUT, "kicad-project.zip"), "wb") as f:
        f.write(buf.getvalue())


def board_checks():
    """设计规则检查（KiCad）+ 安全距离（safety.yaml）→ out/drc.json、out/safety.json"""
    import yaml

    import build as B
    from wqeda.checks import safety
    from wqeda.readers import kicad as RK

    B.KDIR, B.NAME, B.PROJ = KDIR, NAME, PROJ
    dr = B.drc()
    with open(os.path.join(OUT, "drc.json"), "w", encoding="utf-8") as f:
        json.dump(dr, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(PROJ, "safety.yaml"), encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    res = safety.run(RK.read(os.path.join(KDIR, NAME + ".kicad_pcb")), rules)
    with open(os.path.join(OUT, "safety.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return dr, res


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--no-route", action="store_true")
    a = ap.parse_args()
    if a.board:
        jar = os.environ.get("FREEROUTING_JAR") or os.path.join(HERE, "freerouting-1.9.0.jar")
        if not a.no_route:
            print("布线：", board_build(True, jar))
            # 导出和检查换一个新进程做：KiCad 的工程设置在同一进程里会沿用布线前读到的旧值（关节驱动板同样做法）
            return subprocess.call([sys.executable, os.path.abspath(__file__), "--board", "--no-route"])
        import build as B
        B.KDIR, B.NAME, B.CLASSES = KDIR, NAME, {c["name"]: (c["track_mm"], c["clearance_mm"], c["nets"]) for c in D.X["net_classes"]}
        B._project_settings()
    schematic()
    net = exports()
    nc = netcheck(net)
    with open(os.path.join(OUT, "netcheck.json"), "w", encoding="utf-8") as f:
        json.dump(nc, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    n_bom = bom(os.path.join(OUT, "bom.csv"))
    brd = None
    if a.board:
        board_exports()
        brd = board_checks()
    s = summary(nc, n_bom, brd)
    print("原理图 {} 页、器件 {}、网络 {}；网表核对 {}（问题 {} 处）；物料清单 {} 行".format(
        len(D.SHEETS), len(D.PARTS), s["nets"], "通过" if nc["pass"] else "不通过", len(nc["problems"]), n_bom))
    if brd:
        print("设计规则检查：错误 {}、警告 {}、未连接 {}；安全距离：{}".format(
            brd[0]["errors"], brd[0]["warnings"], brd[0]["unconnected"],
            "、".join("{} {}（{} mm）".format(r["name"][5:], r["status"], r["value"]) for r in brd[1])))
    return 0 if nc["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
