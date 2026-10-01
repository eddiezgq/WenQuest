# -*- coding: utf-8 -*-
"""零件库构建：按附录 B.10–B.13 输出发布目录。

    python3 tools/build.py --version 2026.10.1 [--only A-BRG-DG A-KEY] [--limit 3] [--jobs 4] [--out build]

输出（--out 下）：
    library/latest.json
    library/<版本>/index.json
    library/<版本>/<条目>/entry.json、<规格>.glb、<规格>.png
    packages/<条目>.zip           # STEP、STL（每个规格）+ entry.json + 许可与署名，发布到 GitHub Releases
    report.json                   # 每个规格成功与否、用时
"""
import argparse
import datetime as dt
import io
import json
import os
import sys
import time
import traceback
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT)]
import wqlib  # noqa: E402

REPO = "https://github.com/eddiezgq/WenQuest"
LIN_TOL_MM = 0.02          # B.5：弦高误差
ANG_TOL = 0.25


def _mesh(shape):
    import numpy as np
    if type(shape).__name__ == "Trimesh":                             # 已经是网格（机器人）
        return (np.asarray(shape.vertices, dtype=float), np.asarray(shape.faces, dtype=int)) if len(shape.faces) else None
    v, t = shape.tessellate(LIN_TOL_MM * 5, ANG_TOL)
    if not t:
        return None
    return np.array([[p.X, p.Y, p.Z] for p in v], dtype=float), np.array(t, dtype=int)


def glb_bytes(nodes, colors=None):
    """[(节点名, 形体)] → glb：根节点 root 把 Z 向上转成 Y 向上；顶点单位米（B.13）。"""
    import numpy as np
    import trimesh
    scene = trimesh.Scene()
    rot = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    scene.graph.update(frame_from=scene.graph.base_frame, frame_to="root", matrix=rot)
    palette = [(176, 184, 190, 255), (140, 150, 158, 255), (200, 170, 90, 255), (90, 100, 110, 255)]
    for i, (name, shape) in enumerate(nodes):
        m = _mesh(shape)
        if m is None:
            continue
        mesh = trimesh.Trimesh(vertices=m[0] / 1000.0, faces=m[1], process=True)
        mesh.visual = trimesh.visual.ColorVisuals(mesh, face_colors=(colors or palette)[i % len(colors or palette)])
        scene.add_geometry(mesh, node_name=name, geom_name=name, parent_node_name="root")
    return scene.export(file_type="glb")


def png_bytes(nodes, size_px=512):
    """缩略图：等轴测视角，按法向明暗着色。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    tris, shades = [], []
    light = np.array([0.4, -0.6, 0.7])
    light /= np.linalg.norm(light)
    for _, shape in nodes:
        m = _mesh(shape)
        if m is None:
            continue
        v, f = m
        t = v[f]
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        tris.append(t)
        shades.append(0.35 + 0.65 * np.abs(n @ light))
    t = np.concatenate(tris)
    s = np.concatenate(shades)
    if len(t) > 40000:                      # 太密的网格抽样画（只影响缩略图）
        idx = np.linspace(0, len(t) - 1, 40000).astype(int)
        t, s = t[idx], s[idx]
    fig = plt.figure(figsize=(size_px / 100, size_px / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    base = np.array([0.55, 0.60, 0.64])
    ax.add_collection3d(Poly3DCollection(t, facecolors=np.clip(base[None, :] * s[:, None] + 0.12, 0, 1), linewidths=0))
    lo, hi = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 1.05
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=24, azim=-58)
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def build_variant(entry_dir, size, out_ver, cad_dir):
    """在子进程里造一个规格，写 glb、png、step、stl；返回报告。"""
    t0 = time.time()
    e = wqlib.load(entry_dir)
    row = next(r for r in wqlib.specs(e) if str(r["size"]) == str(size))
    code = wqlib.file_code(size)
    try:
        from generators import get_builder
        nodes = get_builder(e)(e, row)
        d = Path(out_ver) / e["id"]
        d.mkdir(parents=True, exist_ok=True)
        extra = {}
        if nodes and nodes[0][0] == "__scene__":          # 机器人：连杆分节点的场景 + 关节表
            from generators import b_robot
            part = nodes[0][1]
            (d / (code + ".glb")).write_bytes(b_robot.glb_bytes(part))
            (d / (code + ".png")).write_bytes(png_bytes([("robot", part["world"])]))
            extra["robot"] = part["robot"]
            if part.get("urdf"):                       # 自建机器人：URDF（第 5 轮 P9）
                (d / (code + ".urdf")).write_text(part["urdf"], encoding="utf-8")
                extra["urdf"] = "{}/{}.urdf".format(e["id"], code)
            if part.get("motion"):                     # 并联机构：运动表（R5）
                import csv
                with open(d / "motion.csv", "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f, lineterminator="\n")
                    w.writerow(part["motion"][0])
                    w.writerows(part["motion"][1])
                extra["mechanism"] = part["mechanism"]
            nodes = [(b["name"], None) for b in part["bodies"]]
        else:
            (d / (code + ".glb")).write_bytes(glb_bytes(nodes))
            (d / (code + ".png")).write_bytes(png_bytes(nodes))
        fmts = e["model"].get("formats", [])
        if cad_dir and ("step" in fmts or "stl" in fmts):
            from build123d import Compound, export_step, export_stl
            shape = nodes[0][1] if len(nodes) == 1 else Compound(children=[n[1] for n in nodes])
            cd = Path(cad_dir) / e["id"]
            cd.mkdir(parents=True, exist_ok=True)
            if "step" in fmts:
                export_step(shape, str(cd / (code + ".step")))
            if "stl" in fmts:
                export_stl(shape, str(cd / (code + ".stl")), tolerance=LIN_TOL_MM)
        files = {"glb": "{}/{}.glb".format(e["id"], code), "png": "{}/{}.png".format(e["id"], code)}
        if extra.get("urdf"):
            files["urdf"] = extra.pop("urdf")
        if extra.get("mechanism"):
            files["motion"] = "{}/motion.csv".format(e["id"])
        return dict({"ref": wqlib.ref(e, size), "ok": True, "files": files, "s": round(time.time() - t0, 2),
                     "nodes": [n for n, _ in nodes]}, **extra)
    except Exception as ex:  # noqa: BLE001
        return {"ref": wqlib.ref(e, size), "ok": False, "error": "{}: {}".format(type(ex).__name__, ex)[:300],
                "trace": traceback.format_exc()[-800:], "s": round(time.time() - t0, 2)}


def key_params(e, row):
    keys = [p["key"] for p in e["params"] if p.get("role") == "key"]
    return {k: row[k] for k in keys if row.get(k) not in (None, "")}


def entry_json(e, rows, results, version):
    doc = {k: v for k, v in e.items() if not k.startswith("_")}
    doc.pop("specs", None)
    doc["version"] = version
    src = e.get("source") or {}
    if src.get("origin") == "menagerie":          # 现成机器人：完整 MJCF 与网格在原仓库（固定提交），不另存
        doc["package"] = "{}/tree/{}/{}".format(src["repo"], src["commit"], src.get("path", "").rstrip("/"))
    elif src.get("origin") == "robot_descriptions":   # URDF 机器人：原仓库固定提交里 URDF 所在目录
        doc["package"] = "{}/tree/{}/{}".format(src["repo"], src["commit"], src.get("path", "").rsplit("/", 1)[0])
    elif src.get("origin") == "wenquest" and e["kind"] == "robot":   # 自建机器人：参数化生成程序（URDF、glTF 都在网页包里）
        doc["package"] = "{}/blob/main/library/generators/b_wq.py".format(REPO)
    elif src.get("origin") == "vendor" and e["kind"] == "robot":   # 按 DH 生成的厂商机器人：没有原始模型，指向官方技术参数表
        doc["package"] = (e.get("datasheet") or {}).get("src") or (e.get("vendor") or {}).get("site")
    else:
        doc["package"] = "{}/releases/download/library-v{}/{}.zip".format(REPO, version, e["id"])
    doc["sizes"] = []
    for r in rows:
        res = results.get(wqlib.ref(e, r["size"]))
        if not res or not res["ok"]:
            continue
        doc["sizes"].append({"size": str(r["size"]), "params": {k: v for k, v in r.items() if k != "size" and v not in (None, "")},
                             "files": res["files"]})
    for r in rows:                                 # 机器人：构建时提取的连杆与关节（B.13）
        res = results.get(wqlib.ref(e, r["size"]))
        if res and res.get("robot"):
            doc["robot"] = dict(doc.get("robot") or {}, **res["robot"])
        if res and res.get("mechanism"):
            doc["mechanism"] = res["mechanism"]
    return doc


def size_name(e, size):
    if size == "default":
        return dict(e["name"])
    return {"zh": "{} {}".format(e["name"]["zh"], size), "en": "{} {}".format(e["name"]["en"], size)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=dt.date.today().strftime("%Y.%m") + ".0")
    ap.add_argument("--out", default=str(ROOT / "build"))
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--limit", type=int, default=0, help="每个条目最多造几个规格（本地试跑用）")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--no-cad", action="store_true", help="不出 STEP/STL")
    ap.add_argument("--robot-jobs", type=int, default=2, help="机器人同时生成几个（每个要 1～2 GB 内存）")
    a = ap.parse_args(argv)

    out = Path(a.out)
    ver_dir = out / "library" / a.version
    cad_dir = None if a.no_cad else out / "cad"
    ver_dir.mkdir(parents=True, exist_ok=True)
    released = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ents = wqlib.entries(a.only)
    jobs = []
    for e in ents:
        rows = wqlib.specs(e)
        if a.limit:
            keep = [r for r in rows if str(r["size"]) == str(e.get("default"))]
            rows = keep + [r for r in rows if r not in keep][: max(0, a.limit - len(keep))]
        for r in rows:
            jobs.append((e["_dir"], r["size"], e["kind"] == "robot"))

    results = {}
    t0 = time.time()
    done = 0
    # 标准件按 --jobs 并行；机器人每个要 1～2 GB 内存：每批 --robot-jobs 个，一批一个新进程池（用完释放内存）。
    # 不用 max_tasks_per_child：Python 3.11/3.12 的进程池用它会卡住（gh-115634）
    std = [(d, s) for d, s, r in jobs if not r]
    rob = [(d, s) for d, s, r in jobs if r]
    rj = max(1, min(a.jobs, a.robot_jobs))
    batches = ([(std, a.jobs)] if std else []) + [(rob[i:i + rj], rj) for i in range(0, len(rob), rj)]
    for part, workers in batches:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(build_variant, str(d), s, str(ver_dir), str(cad_dir) if cad_dir else None) for d, s in part]
            for f in as_completed(futs):
                r = f.result()
                results[r["ref"]] = r
                done += 1
                if not r["ok"]:
                    print("  失败 {}：{}".format(r["ref"], r["error"]), flush=True)
                if done % 50 == 0:
                    print("  {}/{}（{:.0f} 秒）".format(done, len(jobs), time.time() - t0), flush=True)

    items = []
    for e in ents:
        rows = [r for r in wqlib.specs(e) if wqlib.ref(e, r["size"]) in results]
        doc = entry_json(e, rows, results, a.version)
        (ver_dir / e["id"]).mkdir(parents=True, exist_ok=True)
        (ver_dir / e["id"] / "entry.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        erp = {}
        for x in (e.get("factory") or {}).get("erp_items") or []:
            erp.setdefault(str(x.get("size", "default")), []).append(x["item_code"])
        for s in doc["sizes"]:
            items.append({"ref": wqlib.ref(e, s["size"]), "id": e["id"], "size": s["size"], "part": e["id"][0],
                          "kind": e["kind"], "category": e["category"], "name": size_name(e, s["size"]),
                          "tags": e.get("tags", []), "standards": [x["code"] for x in e.get("standards") or []],
                          "params": key_params(e, dict(s["params"], size=s["size"])),
                          "license": e["source"]["license"], "erp_items": erp.get(s["size"], []),
                          "files": s["files"], "entry": "{}/entry.json".format(e["id"]),
                          "family": e["name"], "origin": e["source"]["origin"],
                          **({"vendor": e["vendor"]["name"]} if e.get("vendor") else {}),
                          "default": str(s["size"]) == str(e.get("default", "default")),
                          **({"dof": doc["robot"]["dof"]} if doc.get("robot") else {})})
        if cad_dir and e["kind"] != "robot":
            write_package(e, doc, cad_dir, out / "packages")

    collections = []                                # 只收索引的外部零件库（B.6 第 5 条）
    if not a.only:
        import freecad_index
        c = freecad_index.build(ver_dir)
        if c:
            collections.append(c)
            print("FreeCAD-library 索引：{} 个零件，缩略图 {} 张".format(c["count"], c["thumbs"]))
    index = {"schema": 1, "version": a.version, "released": released,
             "count": {"entries": len(ents), "items": len(items)}, "items": items, "collections": collections,
             "categories": {p: {c: {"zh": n[0], "en": n[1]} for c, n in v.items()} for p, v in wqlib.CATEGORY_NAMES.items()}}
    (ver_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    latest = {"schema": 1, "version": a.version, "released": released,
              "index": "library/{}/index.json".format(a.version),
              "release_url": "{}/releases/tag/library-v{}".format(REPO, a.version)}
    (out / "library" / "latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = [r for r in results.values() if not r.get("ok")]
    (out / "report.json").write_text(json.dumps({"version": a.version, "total": len(results), "failed": bad,
                                                  "seconds": round(time.time() - t0)}, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
    print("完成：{} 个条目、{} 个规格，失败 {} 个，用时 {:.0f} 秒".format(len(ents), len(items), len(bad), time.time() - t0))
    return 1 if bad else 0


def write_package(e, doc, cad_dir, pkg_dir):
    pkg_dir.mkdir(parents=True, exist_ok=True)
    src = e["source"]
    lic = "条目 {} · {}\n许可：{}\n署名：{}\n来源：{}\n".format(e["id"], e["name"]["zh"], src["license"], src.get("attribution", ""),
                                                        src.get("repo") or "问渠零件库")
    with zipfile.ZipFile(pkg_dir / (e["id"] + ".zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("entry.json", json.dumps(doc, ensure_ascii=False, indent=1))
        z.writestr("LICENSE-ATTRIBUTION.txt", lic)
        d = Path(cad_dir) / e["id"]
        if d.exists():
            for f in sorted(d.iterdir()):
                z.write(f, f.name)


if __name__ == "__main__":
    sys.exit(main())
