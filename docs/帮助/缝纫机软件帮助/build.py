# -*- coding: utf-8 -*-
"""缝纫机设计软件的网页互动帮助（第 49 轮）：一份源文件，生成两份帮助。

  python3 docs/帮助/缝纫机软件帮助/build.py

生成：
  apps/web/src/static/help/sewing/index.html            网页版帮助（learn.wenquestrobotics.com/static/help/sewing/）
  apps/web/src/static/help/sewing-freecad/index.html    FreeCAD 版帮助的在线一份
  apps/web/src/static/help/media/…                      两份共用的视频、封面、字幕、截图
  services/gateway/app/sewcore/freecad/help/…           FreeCAD 版帮助的离线一份（随工作台安装包，带 FreeCAD 的视频）

源文件：sections/*.md（Markdown + 几种指令，见 README.md）、template.html（版式）、anim.js（动画与小计算器）。
文中的数一律由计算核心算出（{{键}}），不手写；CAE 的真实结果在 data/（tools/ 里的程序重算）。
"""
import html
import json
import math
import re
import shutil
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "services" / "gateway"))
from app.sewcore import cae_setup as CS  # noqa: E402
from app.sewcore import machines as MS  # noqa: E402
from app.sewcore import partlib as PL  # noqa: E402

WEB_OUT = ROOT / "apps/web/src/static/help/sewing"
FC_ONLINE = ROOT / "apps/web/src/static/help/sewing-freecad"
MEDIA_OUT = ROOT / "apps/web/src/static/help/media"
FC_OFFLINE = ROOT / "services/gateway/app/sewcore/freecad/help"
ONLINE = "https://learn.wenquestrobotics.com"

# 两份帮助各自的章节顺序：(文件, 编号)。common/ 两份都有；web/、freecad/ 各自的
EDITIONS = {
    "web": dict(title="缝纫机设计软件 · 网页版帮助", short="网页版帮助", other=("FreeCAD 版帮助", "../sewing-freecad/index.html"),
                files=["web/00-intro", "web/01-start", "web/02-tabs", "common/ai", "common/cae", "common/lib", "web/03-export",
                       "common/kernel", "common/arch", "web/04-account", "common/faq"]),
    "freecad": dict(title="缝纫机设计软件 · FreeCAD 工作台帮助", short="FreeCAD 版帮助", other=("网页版帮助", ONLINE + "/static/help/sewing/index.html"),
                    files=["freecad/00-intro", "freecad/01-install", "freecad/02-use", "freecad/03-console", "common/ai", "common/cae",
                           "common/lib", "common/kernel", "common/arch", "common/faq"]),
}


# ---------- 文中的数（全部由计算核心算） ----------
def numbers():
    v = {}
    for k in MS.ORDER:
        m = MS.get(k)
        R = m.analyze(m.clean({}))
        v[f"checks_{k}"] = len(R["checks"])
        v[f"name_{k}"] = m.NAME[0]
    v["checks_all"] = sum(v[f"checks_{k}"] for k in MS.ORDER)
    from app.sewcore import design as D
    R = D.analyze({})
    v["n0"] = R["params"]["n"]
    v["F_bdc"] = round(R["key"]["F_bdc"])
    v["F_lim"] = R["params"]["F_lim"]
    R6 = D.analyze(D.clean({"n": 6000}))
    v["bad6"] = "、".join(c["name"]["zh"] for c in R6["checks"] if c["state"] == "bad")
    v["n_bad6"] = sum(c["state"] == "bad" for c in R6["checks"])
    v["n_warn6"] = sum(c["state"] == "warn" for c in R6["checks"])
    R6b = D.analyze(D.clean({"n": 6000, "mr": 0.1, "fn": 240}))
    v["ok6b"] = all(c["state"] == "ok" for c in R6b["checks"])
    v["cats"] = len(PL.CATS)
    v["cat_names"] = "、".join(c["zh"] for c in PL.CATS.values())
    from app import sewing_parts as SP
    from app import sewing_cae  # noqa: F401
    v["max_parts"] = SP.MAX_PARTS
    v["extract_daily"] = SP.EXTRACT_DAILY
    from app.config import Settings
    v["ai_daily"] = Settings.model_fields["sewing_ai_daily"].default
    cae = json.loads((HERE / "data/web_cae.json").read_text())
    fc = json.loads((HERE / "data/crank_fea.json").read_text())
    v["fea_vm"] = round(cae["fea"]["vm_max_mpa"], 1)
    v["fea_sf"] = round(cae["fea"]["safety_factor"], 1)
    v["fea_el"] = cae["fea"]["elements"]
    v["fc_vm"] = fc["max"]
    v["fc_el"] = fc["elements"]
    v["fea_diff"] = round(abs(cae["fea"]["vm_max_mpa"] - fc["max"]) / cae["fea"]["vm_max_mpa"] * 100, 1)
    v["fea_force"] = round(fc["force"], 1)
    v["mbd_peak"] = round(cae["mbd"]["torque_peak_mbd"], 2)
    v["mbd_formula"] = round(cae["mbd"]["torque_peak_formula"], 2)
    v["mbd_diff"] = round(cae["mbd"]["diff"] * 100, 1)
    v["motor_pick"] = cae["motor"]["pick"]
    v["motor_peak"] = round(cae["motor"]["peak_nm"], 2)
    v["motor_rms"] = round(cae["motor"]["rms_nm"], 2)
    v["cae_date"] = cae["date"]
    return v


# ---------- 动画用的数据 ----------
def anim_data():
    from app.sewcore import design as D
    p = D.clean({})
    rod = CS.rod_series(p, p["n"], p["mr"])
    w = 2 * math.pi * p["n"] / 60
    lam = p["r"] / p["l"]
    pos, torque = [], []
    for f in range(360):
        a = math.radians(f)
        S = math.sqrt(1 - (lam * math.sin(a)) ** 2)
        pos.append(p["r"] * (1 - math.cos(a)) + p["l"] * (1 - S))        # 针杆自上止点向下的位移 mm
        acc = p["r"] / 1000 * w * w * (math.cos(a) - lam * (math.cos(2 * a) + lam ** 2 * math.sin(a) ** 4) / S ** 3)
        torque.append(p["mr"] * acc * CS._slider_vel(p, f, p["n"]) / w)
    cae = json.loads((HERE / "data/web_cae.json").read_text())
    s = cae["mbd"]["series"] or []
    mj = []
    if s:   # MuJoCo 的结果是最后几转：试 1–3 转一段，取一转重采样到 360 点，按最相关的起点对齐（只平移相位，不改数值）
        def corr(a, b):
            ma, mb = sum(a) / len(a), sum(b) / len(b)
            num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
            return num / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b) or 1)
        best = (-2, None)
        for revs in (1, 2, 3):
            seg = s[: max(2, len(s) // revs)]
            one = [seg[int(i * len(seg) / 360)] for i in range(360)]
            for k in range(0, 360, 2):
                cand = [one[(i + k) % 360] for i in range(360)]
                c = corr(cand, torque)
                if c > best[0]:
                    best = (c, cand)
        mj = best[1]
        print("MuJoCo 与公式的相关系数", round(best[0], 4))
    fc = json.loads((HERE / "data/crank_fea.json").read_text())
    return {"crank": {"r": p["r"], "l": p["l"], "n": p["n"], "mr": p["mr"], "pos": [round(x, 3) for x in pos],
                      "rod": [round(x, 1) for x in rod], "torque": [round(x, 4) for x in torque], "mujoco": [round(x, 4) for x in mj]},
            "fea": {k: fc[k] for k in ("x", "z", "s", "t", "max", "force")},
            "frame": {"fn": p["fn"], "n": p["n"]}}


# ---------- Markdown + 指令 ----------
ATTR = re.compile(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))')


def attrs(s):
    return {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) if m.group(3) is not None else m.group(4) for m in ATTR.finditer(s)}


def directive(name, a, ed, media_prefix):
    e = html.escape
    if name == "anim":
        return f'<div class="anim" data-anim="{e(a["id"])}"></div>'
    if name == "calc":
        return f'<div class="calc" data-calc="{e(a["id"])}"></div>'
    if name == "video":
        v = a["src"]
        cap = a.get("title", "")
        return (f'<figure class="vid"><video controls preload="none" playsinline poster="{media_prefix}{v}.jpg">'
                f'<source src="{media_prefix}{v}.mp4" type="video/mp4"><track kind="subtitles" srclang="zh" label="中文" default src="{media_prefix}{v}.vtt">'
                f'</video><figcaption>▶ {e(cap)}</figcaption></figure>')
    if name == "img":
        return f'<figure class="shot"><img loading="lazy" src="{media_prefix}{e(a["src"])}" alt="{e(a.get("caption", ""))}"><figcaption>{e(a.get("caption", ""))}</figcaption></figure>'
    if name == "try":
        q = [f"machine={a.get('machine', 'lockstitch')}"]
        if a.get("tab"):
            q.append(f"tab={a['tab']}")
        if a.get("p"):
            from urllib.parse import quote
            q.append("p=" + quote(a["p"]))
        url = ("/" if ed == "web" else ONLINE + "/") + "#/pages/sewing/sewing?" + "&".join(q)
        return f'<a class="try" href="{e(url)}" target="_blank" rel="noopener">▶ 试一试：{e(a["label"])}</a>'
    raise ValueError("unknown directive " + name)


DIR = re.compile(r"^::(\w+)\{(.*)\}\s*$", re.M)
ONLY = re.compile(r"^::only\{(\w+)\}\s*\n(.*?)^::end\s*$", re.M | re.S)


def render(md, ed, vals, media_prefix):
    md = ONLY.sub(lambda m: m.group(2) if m.group(1) == ed else "", md)
    md = re.sub(r"\{\{(\w+)\}\}", lambda m: str(vals[m.group(1)]), md)
    blocks = {}

    def keep(m):
        k = f"@@D{len(blocks)}@@"
        blocks[k] = directive(m.group(1), attrs(m.group(2)), ed, media_prefix)
        return "\n" + k + "\n"
    md = DIR.sub(keep, md)
    h = markdown.markdown(md, extensions=["tables", "fenced_code", "attr_list", "md_in_html"])
    for k, v in blocks.items():
        h = h.replace(f"<p>{k}</p>", v).replace(k, v)
    return h


def sections(ed, vals, media_prefix):
    out, nav = [], []
    for i, f in enumerate(EDITIONS[ed]["files"]):
        md = (HERE / "sections" / (f + ".md")).read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n", md, re.S)
        meta = dict(x.split(":", 1) for x in m.group(1).splitlines()) if m else {}
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        body = md[m.end():] if m else md
        sid = meta["id"]
        h = render(body, ed, vals, media_prefix)
        subs = []

        def h3(mm):
            hid = mm.group(1) or f"{sid}-{len(subs) + 1}"
            t = re.sub("<[^>]+>", "", mm.group(2))
            subs.append((hid, t))
            return f'<h3 id="{hid}">{mm.group(2)}</h3>'
        h = re.sub(r'<h3(?: id="([^"]*)")?>(.*?)</h3>', h3, h)
        num = f"{i:02d}"
        out.append(f'<section id="{sid}"><h2><span class="n">{num}</span>{html.escape(meta["title"])}</h2>'
                   f'<p class="lead">{meta.get("lead", "")}</p>{h}</section>')
        nav.append((sid, num, meta["title"], subs))
    return "\n".join(out), nav


def nav_html(nav):
    s = []
    for sid, num, title, subs in nav:
        s.append(f'<a href="#{sid}" data-s="{sid}"><span class="n">{num}</span>{html.escape(title)}</a>')
        for k, t in subs:
            s.append(f'<a class="sub" href="#{k}" data-s="{sid}">{html.escape(t)}</a>')
    return "\n".join(s)


def build(ed, vals, data, out_dir, media_prefix):
    E = EDITIONS[ed]
    body, nav = sections(ed, vals, media_prefix)
    t = (HERE / "template.html").read_text(encoding="utf-8")
    page = (t.replace("{{TITLE}}", E["title"]).replace("{{SHORT}}", E["short"]).replace("{{NAV}}", nav_html(nav))
             .replace("{{BODY}}", body).replace("{{OTHER_NAME}}", E["other"][0]).replace("{{OTHER_URL}}", E["other"][1])
             .replace("{{EDITION}}", ed).replace("{{API}}", "" if ed == "web" else ONLINE)
             .replace("{{DATA}}", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
             .replace("{{ANIM_JS}}", (HERE / "anim.js").read_text(encoding="utf-8")))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    return page


def main():
    vals = numbers()
    data = anim_data()
    data["cats"] = PL.cats_public()
    data["ai"] = {k: vals[k] for k in ("bad6", "n_bad6", "ok6b", "mbd_diff", "checks_lockstitch")}
    data["fatigue"] = json.loads((HERE / "data/web_cae.json").read_text())["fatigue"]
    media = HERE / "media"
    if MEDIA_OUT.exists():
        shutil.rmtree(MEDIA_OUT)
    MEDIA_OUT.mkdir(parents=True)
    for f in media.glob("*"):
        if f.is_file():
            shutil.copy2(f, MEDIA_OUT / f.name)
    build("web", vals, data, WEB_OUT, "../media/")
    build("freecad", vals, data, FC_ONLINE, "../media/")
    # 离线版：只带 FreeCAD 的视频（fc-*）和截图，网页版的视频点了就去在线
    if FC_OFFLINE.exists():
        shutil.rmtree(FC_OFFLINE)
    (FC_OFFLINE / "media").mkdir(parents=True)
    for f in media.glob("*"):
        if f.is_file() and (f.name.startswith("fc-") or f.suffix in (".png", ".webp", ".jpg") and not f.name.startswith("web-")):
            shutil.copy2(f, FC_OFFLINE / "media" / f.name)
    page = build("freecad", vals, data, FC_OFFLINE, "media/")
    # 离线版里网页版的视频改成在线地址
    page = re.sub(r'(src|poster)="media/(web-[^"]+)"', lambda m: f'{m.group(1)}="{ONLINE}/static/help/media/{m.group(2)}"', page)
    (FC_OFFLINE / "index.html").write_text(page, encoding="utf-8")
    print("web", (WEB_OUT / "index.html").stat().st_size // 1024, "KB · freecad", (FC_OFFLINE / "index.html").stat().st_size // 1024, "KB ·",
          len(list(MEDIA_OUT.glob("*"))), "media files")


if __name__ == "__main__":
    main()
