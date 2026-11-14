"""第 138 轮 G6.1：网页三维整机“WQ-LS 整机”的数据。

    python3 tools/wqls/g6_web.py <整机目录根> <机壳目录> factory/digital/web/public/wqls

输出目录就是网页所在的目录：数字工厂把它作为公开页面 /wqls/index.html 提供，《缝纫机设计与制造》网页版构建时整个复制到 labs/wqls/。
页面 index.html 是手写的（不由本程序生成）；three.min.js（r128）是 site/cases/three.min.js 的副本，页面只用它。

<整机目录根> 里是 cad/mech.py 按各状态建出来的整机（b_<档位>_<压脚>_<选项>，选项 none / TE / T / E），
每个目录先用 render/web_tess.py 划好网页用的网格（<目录>/web/*.stl）；<机壳目录> 里是 housing_upper.step、housing_lower.step
（同样划好 web/*.stl、web/vol.json）。

输出（页面 index.html 读）：
  machine.json  零件表（物料号、名称、材料、质量、计算书、图纸、爆炸分组）、每个零件在各状态下用哪份网格和哪段运动、面线
  mesh.bin      全部网格：Int16 量化的顶点 + 索引（顶点在折角 > 30° 处已拆开，页面直接算法线）
  frames.bin    运动：每段 180 帧（每 2°）× 3×4 变换，Float32
网格和运动都按内容去重：状态之间没变的零件只存一份。

状态：送布档 s3 / s5 / r5（针距 3、5、倒缝 5）× 压脚 down / hand / knee × 剪线 sew / trim / wipe，选项 T、E 任意组合（8 种变型）。
运动在每个组合下由 g4_mech.py 重算（27 组）；网格在每个（档位、压脚、选项）下取自对应的整机目录。
没有单独建的 T、E 变型（只在 s3、放下时建过）由 none 的零件加上 TE 里的选配件拼成，并在 s3、放下时与真建的比对。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
FEEDS, PRESSES, TRIMS = ("s3", "s5", "r5"), ("down", "hand", "knee"), ("sew", "trim", "wipe")
OPTS = ("none", "T", "E", "TE")
GKEYS = [(f, p, o) for f in FEEDS for p in PRESSES for o in OPTS]          # 网格按（档位、压脚、选项）
FKEYS = [f"{f},{p},{t}" for f in FEEDS for p in PRESSES for t in TRIMS]      # 运动按（档位、压脚、剪线）
DOC = Path(__file__).resolve().parents[2] / "docs" / "设计" / "WQ-LS"
CREASE = np.cos(np.radians(30.0))
RHO_HT250 = 7.2e-6                                   # kg/mm³


def read_stl(p: Path) -> np.ndarray:
    b = p.read_bytes()
    n = struct.unpack_from("<I", b, 80)[0]
    a = np.frombuffer(b, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
    return np.ascontiguousarray(a["v"])               # (n, 3, 3)


def crease_split(tri: np.ndarray):
    """焊接重合顶点，再在折角 > 30° 的地方拆开 → (顶点 (m,3), 三角形索引 (n,3))。"""
    q = np.round(tri.reshape(-1, 3) * 1e3).astype(np.int64)
    _, vid = np.unique(q, axis=0, return_inverse=True)
    vid = vid.reshape(-1, 3)
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    fn = np.cross(e1, e2)
    ln = np.linalg.norm(fn, axis=1)
    keep = ln > 1e-12
    tri, vid, fn = tri[keep], vid[keep], fn[keep] / ln[keep, None]
    corners_v = vid.reshape(-1)
    corners_f = np.repeat(np.arange(len(tri)), 3)
    order = np.argsort(corners_v, kind="stable")
    new_id = np.empty(len(corners_v), np.int64)
    pos = []
    nxt = 0
    cv = corners_v[order]
    starts = np.flatnonzero(np.r_[True, cv[1:] != cv[:-1]])
    ends = np.r_[starts[1:], len(cv)]
    flat = tri.reshape(-1, 3)
    for s, e in zip(starts, ends):
        idx = order[s:e]
        seeds = []                                   # (法线, 新顶点号)
        for c in idx:
            n = fn[corners_f[c]]
            for sn, sid in seeds:
                if n @ sn >= CREASE:
                    new_id[c] = sid
                    break
            else:
                seeds.append((n, nxt))
                new_id[c] = nxt
                pos.append(flat[c])
                nxt += 1
    return np.array(pos, np.float32), new_id.reshape(-1, 3)


class Pack:
    """网格去重打包：Int16 量化顶点 + Uint16/Uint32 索引，每块按 4 字节对齐。"""

    def __init__(self):
        self.buf = bytearray()
        self.meshes = []
        self.by_hash = {}

    def add(self, tri: np.ndarray) -> int:
        h = hashlib.sha1(np.round(tri, 3).tobytes()).hexdigest()
        if h in self.by_hash:
            return self.by_hash[h]
        pos, ix = crease_split(tri)
        lo, hi = pos.min(0), pos.max(0)
        sc = np.maximum(hi - lo, 1e-6) / 65535.0
        qv = (np.round((pos - lo) / sc) - 32768).astype(np.int16)
        it = np.uint16 if len(pos) < 65536 else np.uint32
        ov = len(self.buf)
        self.buf += qv.tobytes()
        self.buf += b"\0" * (-len(self.buf) % 4)
        oi = len(self.buf)
        self.buf += ix.astype(it).tobytes()
        self.buf += b"\0" * (-len(self.buf) % 4)
        self.meshes.append(dict(v=ov, nv=len(pos), i=oi, ni=int(ix.size), i32=int(it == np.uint32),
                                lo=[round(float(x), 4) for x in lo], sc=[float(x) for x in sc]))
        self.by_hash[h] = len(self.meshes) - 1
        return self.by_hash[h]


DOC_CSS = """<style>
:root{--bg:#fbfbfa;--ink:#1d2329;--mut:#5b6670;--line:#d8dde2;--acc:#0b4fae;--hl:#fff3c4}
@media (prefers-color-scheme: dark){:root{--bg:#15181b;--ink:#e6e9ec;--mut:#9aa5ae;--line:#39414a;--acc:#6aa7ff;--hl:#4a3f12}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 system-ui,"Noto Sans CJK SC","PingFang SC",sans-serif}
main{max-width:860px;margin:0 auto;padding:16px 16px 64px}
.note{color:var(--mut);font-size:13px;border-bottom:1px solid var(--line);padding-bottom:8px}
h1{font-size:22px}h2{font-size:18px;margin-top:2em;scroll-margin-top:12px}h3{font-size:16px;scroll-margin-top:12px}
h2:target,h3:target{background:var(--hl);border-radius:4px}
table{border-collapse:collapse;display:block;overflow-x:auto;font-size:13.5px;margin:1em 0}
td,th{border:1px solid var(--line);padding:4px 8px;vertical-align:top}th{background:rgba(127,127,127,.08)}
code{font-size:.9em;background:rgba(127,127,127,.12);padding:0 3px;border-radius:3px}pre{overflow-x:auto}
img{max-width:100%;height:auto}a{color:var(--acc)}blockquote{margin:1em 0;padding:0 12px;border-left:3px solid var(--line);color:var(--mut)}
</style>"""


def links(codes, parts, out: Path):
    """计算书 → doc/<简称>.html（标题加锚点 s1、s2…），图纸 → dwg/<原名>.pdf；零件里换成网址和那一节的标题。"""
    import markdown
    (out / "doc").mkdir(exist_ok=True)
    (out / "dwg").mkdir(exist_ok=True)
    anchors = {}
    for key, rel in codes["docs"].items():
        src = DOC / rel
        h = markdown.markdown(src.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
        heads = []

        def tag(m):
            heads.append(re.sub(r"<[^>]+>", "", m.group(3)).strip())
            return f'<{m.group(1)} id="s{len(heads)}"{m.group(2)}>{m.group(3)}</{m.group(1)}>'
        h = re.sub(r"<(h[1-4])([^>]*)>(.*?)</\1>", tag, h, flags=re.S)

        def img(m):
            p = (src.parent / m.group(1)).resolve()
            if not p.exists():
                return m.group(0)
            dst = out / "doc" / "img" / (hashlib.sha1(str(p).encode()).hexdigest()[:10] + p.suffix)
            dst.parent.mkdir(exist_ok=True)
            shutil.copyfile(p, dst)
            return f'src="img/{dst.name}"'
        h = re.sub(r'src="([^"]+)"', img, h)
        title = heads[0] if heads else rel
        (out / "doc" / f"{key}.html").write_text(
            f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title>{DOC_CSS}</head><body><main><p class="note">WQ-LS 设计文档 · {rel} · 设计计算的原文（中文）'
            f' · Design document (Chinese original)</p>{h}</main></body></html>', encoding="utf-8")
        anchors[key] = heads
    for k, c in parts.items():
        if c.get("doc"):
            key, _, head = c.pop("doc").partition("#")
            hs = anchors[key]
            norm = lambda x: re.sub(r"[`\s]", "", x)       # noqa: E731  标题里的 `代码` 渲染后没有反引号
            i = next((n for n, t in enumerate(hs) if head and norm(t).startswith(norm(head))), None)
            assert i is not None or not head, f"{k}：{codes['docs'][key]} 里找不到“{head}”"
            c["doc"] = dict(u=f"doc/{key}.html" + (f"#s{i + 1}" if i is not None else ""), t=hs[i] if i is not None else hs[0],
                            f=codes["docs"][key])
        if c.get("dwg"):
            lst = []
            for rel in c.pop("dwg"):
                p = DOC / rel
                shutil.copyfile(p, out / "dwg" / p.name)
                lst.append(dict(u=f"dwg/{p.name}", t=p.stem))
            c["dwg"] = lst


def frames_for(feed, press, trim):
    with tempfile.TemporaryDirectory() as t:
        env = dict(os.environ, WQ_FEED=feed, WQ_PRESS=press, WQ_TRIM=trim)
        subprocess.run([sys.executable, str(HERE / "g4_mech.py"), t], env=env, check=True, capture_output=True)
        return json.loads((Path(t) / "frames.json").read_text())["frames"]


def main():
    broot, hdir, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    codes = yaml.safe_load((HERE / "part_codes.yaml").read_text(encoding="utf-8"))
    P = codes["parts"]
    bad = [k for k, v in list(codes["groups"].items()) + [(k, v.get(f)) for k, v in P.items() for f in ("name", "sub") if f in v]
           if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) for x in v))]
    assert not bad, f"part_codes.yaml 里这些中英文名不是两个字符串（YAML 里含“: ”的要加引号）：{bad}"
    builds = {}
    for d in sorted(broot.glob("b_*_*_*")):
        _, f, p, o = d.name.split("_")
        builds[(f, p, o)] = d
    pj = {k: json.loads((d / "parts.json").read_text())["parts"] for k, d in builds.items()}
    base = set(pj[("s3", "down", "none")])
    optT = set(pj[("s3", "down", "T")]) - base
    optE = set(pj[("s3", "down", "E")]) - base
    e_remove = base - set(pj[("s3", "down", "E")])
    print("T:", sorted(optT), "\nE:", sorted(optE), "\nE 去掉:", sorted(e_remove))
    pack = Pack()
    geo = {}                                          # (f, p, o) → {零件: 网格号}
    tri_cache = {}

    def mesh_of(d: Path, k: str) -> int:
        key = (d, k)
        if key not in tri_cache:
            tri_cache[key] = pack.add(read_stl(d / "web" / f"{k}.stl"))
        return tri_cache[key]

    for f in FEEDS:
        for p in PRESSES:
            none, te = builds[(f, p, "none")], builds[(f, p, "TE")]
            for o in OPTS:
                g = {}
                for k in sorted(base):
                    if "E" in o and k in e_remove:
                        continue
                    g[k] = mesh_of(none, k)
                for k in sorted((optT if "T" in o else set()) | (optE if "E" in o else set())):
                    g[k] = mesh_of(te, k)
                geo[(f, p, o)] = g
    # 拼出来的 T、E 变型与真建的比对（s3、放下）
    for o in ("T", "E"):
        real = {k: mesh_of(builds[("s3", "down", o)], k) for k in pj[("s3", "down", o)]}
        diff = {k for k in set(real) | set(geo[("s3", "down", o)]) if real.get(k) != geo[("s3", "down", o)].get(k)}
        assert not diff, f"拼出的 {o} 变型与真建的不一样：{sorted(diff)}"
    # 机壳
    hv = json.loads((hdir / "web" / "vol.json").read_text())
    hmesh = {k: pack.add(read_stl(hdir / "web" / f"{k}.stl")) for k in ("housing_upper", "housing_lower")}
    # 零件表
    allparts = sorted(set().union(*[set(g) for g in geo.values()]))
    miss = [k for k in allparts + list(hmesh) if k not in P]
    assert not miss, f"part_codes.yaml 里没有：{miss}"
    extra = [k for k in P if k not in allparts and k not in hmesh]
    assert not extra, f"part_codes.yaml 里多出来（三维里没有）：{extra}"
    parts = {}
    for k in allparts + list(hmesh):
        c = dict(P[k])
        src = next(pj[b][k] for b in (("s3", "down", "TE"), ("s3", "down", "none")) if k in pj[b]) if k in allparts else None
        c["mass_g"] = round(src["mass_kg"] * 1000, 1) if src else round(hv[k] * RHO_HT250 * 1000, 0)
        c["show"] = src["material"] if src else "shell"
        if k in hmesh:
            c["g"] = hmesh[k]
        else:
            ids = [geo[gk].get(k, -1) for gk in GKEYS]
            c["g"] = ids[0] if len(set(ids)) == 1 else ids    # 一个数：各变型都是这份网格；数组：按 gkeys 的顺序，−1 = 这个变型没有这个零件
        if k in optT:
            c["need"] = "T"
        elif k in optE:
            c["need"] = "E"
        elif k in e_remove:
            c["need"] = "!E"
        parts[k] = c
    # 运动（27 组）
    fbuf = bytearray()
    seq_by_hash = {}
    fr_of = {k: {} for k in parts}
    threads, thread_by_hash, thread_of = [], {}, {}
    nfr = None
    for f in FEEDS:
        for p in PRESSES:
            for t in TRIMS:
                FR = frames_for(f, p, t)
                nfr = len(FR)
                ck = f"{f},{p},{t}"
                for k in parts:
                    if k not in FR[0]["M"]:
                        continue
                    a = np.array([np.array(fr["M"][k], np.float64).reshape(4, 4)[:3, :] for fr in FR], np.float32)
                    if np.allclose(a, np.tile(np.eye(4, dtype=np.float32)[:3], (nfr, 1, 1)), atol=1e-6):
                        continue
                    h = hashlib.sha1(np.round(a, 5).tobytes()).hexdigest()
                    if h not in seq_by_hash:
                        seq_by_hash[h] = len(fbuf) // (nfr * 48)
                        fbuf += a.tobytes()
                    fr_of[k][ck] = seq_by_hash[h]
                th = dict(pts=[[[round(v, 2) for v in q] for q in fr["thread"]] for fr in FR],
                          tip=[round(fr["tip_z"], 2) for fr in FR], eye=[fr["eye"] for fr in FR])
                h = hashlib.sha1(json.dumps(th).encode()).hexdigest()
                if h not in thread_by_hash:
                    thread_by_hash[h] = len(threads)
                    threads.append(th)
                thread_of[ck] = thread_by_hash[h]
    for k, m in fr_of.items():
        if not m:
            continue
        ids = [m.get(fk, -1) for fk in FKEYS]
        parts[k]["f"] = ids[0] if len(set(ids)) == 1 else ids     # 一个数：各状态同一段运动；数组：按 fkeys，−1 = 不动
    links(codes, parts, out)
    meta = dict(version=1, frames=nfr, step_deg=360 // nfr, feeds=FEEDS, presses=PRESSES, trims=TRIMS, opts=OPTS,
                gkeys=[",".join(k) for k in GKEYS], fkeys=FKEYS,
                groups=codes["groups"], assemblies=codes.get("assemblies", {}),
                meshes=pack.meshes, parts=parts, threads=threads, thread_of=[thread_of[k] for k in FKEYS],
                mesh_bytes=len(pack.buf), frame_bytes=len(fbuf))
    by_code = {}
    for k, c in parts.items():
        by_code.setdefault(c["code"], []).append(k)
        if c.get("of"):
            by_code.setdefault(c["of"], []).append(k)
    (out / "codes.json").write_text(json.dumps(by_code, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    (out / "mesh.bin").write_bytes(bytes(pack.buf))
    (out / "frames.bin").write_bytes(bytes(fbuf))
    (out / "machine.json").write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    tris = sum(m["ni"] // 3 for m in pack.meshes)
    print(f"零件 {len(parts)}，网格 {len(pack.meshes)} 份（{tris} 三角形，{len(pack.buf) / 1e6:.2f} MB），"
          f"运动 {len(fbuf) // (nfr * 48)} 段（{len(fbuf) / 1e6:.2f} MB），面线 {len(threads)} 组")


if __name__ == "__main__":
    main()
