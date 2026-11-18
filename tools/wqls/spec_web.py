"""第 172 轮：WQ-LS 设计说明书网页版。

把 docs/设计/WQ-LS/ 下全部文章（Markdown）和图、视频、工程图、数据文件生成一个静态网站，放在
factory/digital/web/public/wqls/spec/（数字工厂 /wqls/spec/，公开，和网页三维整机同一处）。

  - 左边总目录：关 → 篇 → 节（随滚动高亮）；右边本篇目录；页顶路径、页底上一篇 / 下一篇；全文搜索
  - 文章没引用的图和文件，每关末尾一页“附图与附件”
  - 文章里写的文件名（`G4/挑线机构.json` 这类）能点开；公式转成 MathML
  - 工程图、STEP 和三维整机的 dwg/、step/ 内容相同的，直接用那一份

    python3 tools/wqls/spec_web.py            # 生成
    python3 tools/wqls/spec_web.py --check    # 只核对生成结果是否和原文一致（测试用同一个函数）

改了 docs/设计/WQ-LS/ 里任何文件都要重新生成再提交，factory/digital/tests/test_wqls_spec.py 会核对。
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "设计" / "WQ-LS"
PUB = ROOT / "factory" / "digital" / "web" / "public" / "wqls"
OUT = PUB / "spec"
SCRIPT = Path(__file__).resolve()
sys.path[:0] = [str(Path(__file__).resolve().parent)]
import spec_web_ui as UI  # noqa: E402

# 关的次序与名字；篇的次序（没列的按文件名排在后面）
GROUPS = [
    ("G1", "G1 设计任务书与总体方案", ["设计任务书.md"]),
    ("G2", "G2 动力学、强度与仿真", ["设计计算书.md"]),
    ("G3", "G3 外观与机壳铸件", ["外观与机壳铸件.md"]),
    ("G4", "G4 零件与机构", ["刺布与挑线机构.md", "旋梭组.md", "送布组.md", "压脚与操纵件.md", "剪线与电子针距.md"]),
    ("G5", "G5 机壳工艺", ["机壳铸造工艺.md", "机壳机加工工艺.md"]),
    ("G6", "G6 网页三维整机", ["网页三维整机.md"]),
    ("G7", "G7 工程图与物料清单", []),
    ("G8", "G8 整机补全与虚拟样机", ["G8.0-1_总体布置与刺布机构复查.md", "G8.0-2_刺布机构依据与改动清单.md",
                                "G8.1_虚拟样机验证方案.md", "G8.1_配合表.md"]),
    ("GC", "GC 控制器", ["控制器方案与选型.md", "打样/上电调试步骤书.md"]),
    ("标准", "企业标准", ["Q-WQ-001_缝纫机螺纹与螺钉.md"]),
]
IMG = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
VID = {".mp4", ".webm"}
MAXW = 2000                     # 图宽超过这个就缩小（像素）


def sha1(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()


def manifest_now() -> dict:
    """原文（全部文件）和本脚本的指纹：生成结果里记一份，测试拿它核对"""
    files = {str(p.relative_to(SRC)): sha1(p) for p in sorted(SRC.rglob("*")) if p.is_file()}
    data = {str(p.relative_to(ROOT)): sha1(p) for p in UI.DATA_FILES}
    return dict(script=sha1(SCRIPT), ui=sha1(Path(UI.__file__)), data=data, files=files)


def check() -> list[str]:
    m = OUT / "manifest.json"
    if not m.exists():
        return ["没有 spec/manifest.json：还没生成"]
    old, now = json.loads(m.read_text(encoding="utf-8")), manifest_now()
    bad = []
    if old.get("script") != now["script"] or old.get("ui") != now["ui"]:
        bad.append("spec_web.py / spec_web_ui.py 改过")
    for k in sorted(set(old.get("data", {})) | set(now["data"])):
        if old.get("data", {}).get(k) != now["data"].get(k):
            bad.append(f"{k} 改过（章首数字、首页读它）")
    for k in sorted(set(old["files"]) | set(now["files"])):
        if old["files"].get(k) != now["files"].get(k):
            bad.append(f"docs/设计/WQ-LS/{k} 改过（或新增、删除）")
    return bad


def git_date(p: Path) -> str:
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(p)], cwd=ROOT, capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or "未提交"
    except Exception:
        return ""


def slug_page(rel: str) -> str:
    """docs 相对路径 → 网页文件名（g4-旋梭组.html）"""
    if rel == "README.md":
        return "index.html"
    s = rel[:-3].replace("/", "-")
    return re.sub(r"[\s（）()]+", "_", s) + ".html"


def strip_tags(h: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", h))


def human(n: int) -> str:
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{max(1, round(n / 1e3))} KB"


class Site:
    def __init__(self):
        self.assets: dict[str, str] = {}          # 原文相对路径 → 网址（相对 spec/）
        self.used: set[str] = set()                # 文章引用过的文件
        self.shared = {}                           # 三维整机 dwg/、step/ 里的文件：指纹 → 网址
        for sub in ("dwg", "step"):
            for p in (PUB / sub).glob("*"):
                if p.is_file():
                    self.shared[sha1(p)] = f"../{sub}/{p.name}"
        self.pages = []                            # dict(rel, url, title, group, heads, html, desc, date)

    # ---------- 文件 ----------
    def asset(self, rel: str) -> str:
        if rel in self.assets:
            return self.assets[rel]
        p = SRC / rel
        h = sha1(p)
        if h in self.shared:
            u = self.shared[h]
        else:
            u = "f/" + rel
            dst = OUT / u
            dst.parent.mkdir(parents=True, exist_ok=True)
            if p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                from PIL import Image
                im = Image.open(p)
                if im.width > MAXW:
                    im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
                    im.save(dst, optimize=True)
                else:
                    shutil.copyfile(p, dst)
            else:
                shutil.copyfile(p, dst)
        self.assets[rel] = u
        return u

    def resolve(self, target: str, base: Path) -> str | None:
        """文章里的路径 → docs/设计/WQ-LS 下的相对路径（找不到返回 None）"""
        t = target.strip().split("#")[0].strip()
        if not t or t.startswith(("http:", "https:", "mailto:", "/")) or "*" in t or "<" in t:
            return None
        t = t.removeprefix("docs/设计/WQ-LS/")
        for cand in (base / t, SRC / t):
            try:
                c = cand.resolve()
                r = c.relative_to(SRC.resolve())
            except (ValueError, OSError):
                continue
            if c.is_file():
                return str(r)
        return None

    def link_of(self, rel: str) -> str:
        if rel.endswith(".md"):
            return slug_page(rel)
        self.used.add(rel)
        return self.asset(rel)

    # ---------- 文章 ----------
    def render(self, rel: str, group: str):
        import markdown
        p = SRC / rel
        src = p.read_text(encoding="utf-8")
        maths = []

        def math(m):
            from latex2mathml.converter import convert
            disp = m.group(1) is not None
            tex = m.group(1) if disp else m.group(2)
            maths.append(convert(tex.strip(), display="block" if disp else "inline"))
            return f"\x00M{len(maths) - 1}\x00"
        src = re.sub(r"\$\$(.+?)\$\$|(?<![\w$])\$([^$\n]+?)\$(?![\w$])", math, src, flags=re.S)
        h = markdown.markdown(list_gaps(src), extensions=["tables", "fenced_code", "sane_lists"])
        h = re.sub(r"\x00M(\d+)\x00", lambda m: maths[int(m.group(1))], h)
        h = re.sub(r"<p>(<math[^>]*display=\"block\".*?</math>)</p>", r'<div class="math">\1</div>', h, flags=re.S)

        heads = []
        n = [0]

        def tag(m):
            lvl, inner = int(m.group(1)), m.group(3)
            n[0] += 1
            hid = f"s{n[0]}"
            heads.append(dict(l=lvl, id=hid, t=strip_tags(inner).strip()))
            return f'<h{lvl} id="{hid}"{m.group(2)}>{inner}<a class="hl" href="#{hid}" aria-label="本节链接">#</a></h{lvl}>'
        h = re.sub(r"<h([1-4])([^>]*)>(.*?)</h\1>", tag, h, flags=re.S)

        def src_attr(m):
            r = self.resolve(html.unescape(m.group(2)), p.parent)
            if not r:
                return m.group(0)
            return f'{m.group(1)}="{html.escape(self.link_of(r))}"'
        h = re.sub(r'(src)="([^"]+)"', src_attr, h)

        def href(m):
            raw = html.unescape(m.group(1))
            if raw.startswith(("http:", "https:")):
                return f'href="{m.group(1)}" target="_blank" rel="noopener"'
            r = self.resolve(raw, p.parent)
            if not r:
                return m.group(0)
            frag = "#" + raw.split("#", 1)[1] if "#" in raw else ""
            return f'href="{html.escape(self.link_of(r))}{frag}"'
        h = re.sub(r'href="([^"]+)"', href, h)

        # 行内代码里写的文件名 → 链接（已经在 <a> 里的不动）
        parts = re.split(r"(<a\b.*?</a>|<pre\b.*?</pre>)", h, flags=re.S)
        for i in range(0, len(parts), 2):
            def code(m):
                r = self.resolve(html.unescape(m.group(1)), p.parent)
                if not r:
                    return m.group(0)
                return f'<a class="fl" href="{html.escape(self.link_of(r))}">{m.group(0)}</a>'
            parts[i] = re.sub(r"<code>([^<]{3,160})</code>", code, parts[i])
        h = "".join(parts)
        # 图：点开看原图；表：可横向滚动
        h = re.sub(r'<img ([^>]*?)src="([^"]+)"([^>]*)>', r'<a class="im" href="\2" target="_blank"><img loading="lazy" \1src="\2"\3></a>', h)
        h = h.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
        h = UI.videos(h)                                  # 原文写到的视频：放播放器
        h = UI.insert_labs(rel, h, heads)                 # 动画、虚拟实验、三维模型块
        title = heads[0]["t"] if heads else rel
        self.pages.append(dict(rel=rel, url=slug_page(rel), title=title, group=group, heads=heads, html=h,
                               desc=describe(src), date=git_date(p), src="docs/设计/WQ-LS/" + rel))

    def bom_page(self):
        """G7：物料清单 + 工程图"""
        d = json.loads((SRC / "G7" / "物料清单.json").read_text(encoding="utf-8"))
        V = d["variants"]
        names = list(V)
        rows, order = {}, []
        for vn, v in V.items():
            for ln in v["lines"]:
                c = ln["code"]
                if c not in rows:
                    rows[c] = dict(ln, used=[])
                    order.append(c)
                rows[c]["used"].append(vn)
        body = [f'<h1 id="s1">WQ-LS 工程图与物料清单（G7）<a class="hl" href="#s1">#</a></h1>',
                f'<p>{html.escape(d.get("note", ""))}。原始数据：<a href="{self.link_of("G7/物料清单.json")}"><code>G7/物料清单.json</code></a>。</p>',
                '<h2 id="s2">一、变型与价格<a class="hl" href="#s2">#</a></h2><div class="tbl"><table><thead><tr><th>变型</th><th>自动剪线 T</th><th>电子针距 E</th><th>少油旋梭 D</th><th>物料行数</th><th>示例价（元）</th></tr></thead><tbody>']
        for vn, v in V.items():
            o = v.get("options", {})
            body.append(f"<tr><td>{vn}</td>" + "".join(f"<td>{'✓' if o.get(k) else ''}</td>" for k in "TED")
                        + f"<td>{len(v['lines'])}</td><td>{v.get('price', '')}</td></tr>")
        body.append("</tbody></table></div>")
        body.append(f'<h2 id="s3">二、物料清单（{len(order)} 项，8 种变型合并）<a class="hl" href="#s3">#</a></h2>'
                    '<div class="tbl"><table><thead><tr><th>物料号</th><th>名称</th><th>来源</th><th>数量</th><th>质量 g</th><th>用于变型</th></tr></thead><tbody>')
        kinds = dict(make="自制", buy="外购", std="标准件")
        for c in order:
            r = rows[c]
            used = "全部" if len(r["used"]) == len(names) else "、".join(r["used"])
            body.append(f"<tr><td><code>{html.escape(c)}</code></td><td>{html.escape(str(r.get('name', '')))}</td>"
                        f"<td>{kinds.get(r.get('kind'), r.get('kind', ''))}</td><td>{r.get('qty', '')}</td>"
                        f"<td>{r.get('mass_g', '') if r.get('mass_g') is not None else ''}</td><td>{html.escape(used)}</td></tr>")
        body.append("</tbody></table></div>")
        body.append('<h2 id="s4">三、工程图<a class="hl" href="#s4">#</a></h2><ul class="files">')
        for p in sorted((SRC / "G7" / "工程图").glob("*")):
            rel = str(p.relative_to(SRC))
            body.append(f'<li><a href="{self.link_of(rel)}" target="_blank">{html.escape(p.name)}</a> <span class="mut">{human(p.stat().st_size)}</span></li>')
        body.append("</ul>")
        heads = [dict(l=1, id="s1", t="WQ-LS 工程图与物料清单（G7）"), dict(l=2, id="s2", t="一、变型与价格"),
                 dict(l=2, id="s3", t=f"二、物料清单（{len(order)} 项，8 种变型合并）"), dict(l=2, id="s4", t="三、工程图")]
        self.pages.append(dict(rel="G7/物料清单.json", url="G7-工程图与物料清单.html", title=heads[0]["t"], group="G7", heads=heads,
                               html="".join(body), desc="8 种变型的物料清单和零件工程图", date=git_date(SRC / "G7"),
                               src="docs/设计/WQ-LS/G7/"))

    def attach_page(self, gid: str, gname: str):
        """这一关文件夹里文章没用到的图、视频、文件"""
        g = SRC / gid
        files = [p for p in sorted(g.rglob("*")) if p.is_file() and p.suffix != ".md" and str(p.relative_to(SRC)) not in self.used]
        if not files:
            return
        imgs = [p for p in files if p.suffix.lower() in IMG]
        vids = [p for p in files if p.suffix.lower() in VID]
        rest = [p for p in files if p not in imgs and p not in vids]
        body, heads = [], []
        t = f"{gname} · 附图与附件"
        body.append(f'<h1 id="s1">{html.escape(t)}<a class="hl" href="#s1">#</a></h1>'
                    f'<p class="mut">{gid}/ 文件夹里文章正文没有直接引用的图、视频和文件，原样列出。</p>')
        heads.append(dict(l=1, id="s1", t=t))
        k = 1
        if imgs:
            k += 1
            body.append(f'<h2 id="s{k}">图（{len(imgs)}）<a class="hl" href="#s{k}">#</a></h2><div class="gal">')
            heads.append(dict(l=2, id=f"s{k}", t=f"图（{len(imgs)}）"))
            for p in imgs:
                u = self.asset(str(p.relative_to(SRC)))
                body.append(f'<figure><a class="im" href="{html.escape(u)}" target="_blank"><img loading="lazy" src="{html.escape(u)}" alt="{html.escape(p.stem)}"></a>'
                            f"<figcaption>{html.escape(str(p.relative_to(g)))}</figcaption></figure>")
            body.append("</div>")
        if vids:
            k += 1
            body.append(f'<h2 id="s{k}">视频（{len(vids)}）<a class="hl" href="#s{k}">#</a></h2>')
            heads.append(dict(l=2, id=f"s{k}", t=f"视频（{len(vids)}）"))
            for p in vids:
                u = self.asset(str(p.relative_to(SRC)))
                body.append(f'<figure><video controls preload="metadata" src="{html.escape(u)}"></video><figcaption>{html.escape(p.name)}</figcaption></figure>')
        if rest:
            k += 1
            body.append(f'<h2 id="s{k}">文件（{len(rest)}）<a class="hl" href="#s{k}">#</a></h2><ul class="files">')
            heads.append(dict(l=2, id=f"s{k}", t=f"文件（{len(rest)}）"))
            for p in rest:
                u = self.asset(str(p.relative_to(SRC)))
                tgt = ' target="_blank"' if p.suffix.lower() in {".pdf", ".json", ".txt", ".nc", ".mmd", ".svg"} else " download"
                body.append(f'<li><a href="{html.escape(u)}"{tgt}>{html.escape(str(p.relative_to(g)))}</a> <span class="mut">{human(p.stat().st_size)}</span></li>')
            body.append("</ul>")
        self.pages.append(dict(rel=gid + "/（附件）", url=f"{gid}-附图与附件.html", title=t, group=gid, heads=heads, html="".join(body),
                               desc="、".join(f"{n} {u}" for n, u in ((len(imgs), "张图"), (len(vids), "段视频"), (len(rest), "个文件")) if n), date="", src=f"docs/设计/WQ-LS/{gid}/", attach=True))


def list_gaps(md: str) -> str:
    """GitHub 允许列表紧跟在一段文字后面，Python-Markdown 要空一行，否则整串“- …”并成一段：补上空行（代码块里不动）"""
    out, fence, prev = [], False, ""
    item = re.compile(r"^\s{0,3}([-*+]|\d+[.)])\s")
    for ln in md.split("\n"):
        if ln.lstrip().startswith("```"):
            fence = not fence
        if not fence and item.match(ln) and prev.strip() and not item.match(prev) and not prev.startswith((" ", "\t", "|", "#")):
            out.append("")
        out.append(ln)
        prev = ln
    return "\n".join(out)


def describe(md: str) -> str:
    """一句话说明：“结论”一节的第一段，没有就取正文第一段"""
    m = re.search(r"^##+ [^\n]*结论[^\n]*\n+(.+?)(?:\n\n|\Z)", md, flags=re.M | re.S)
    cands = [m.group(1)] if m else []
    cands += [b for b in re.split(r"\n\s*\n", md) if not b.lstrip().startswith(("#", "|", "!", "```", "<", "*WenQuest", ">", "- ", "1.")) and len(b) > 30]
    cands = [c for c in cands if not c.lstrip().startswith("|")]
    for c in cands:
        t = re.sub(r"[`*]|\[([^\]]*)\]\([^)]*\)|\$[^$]*\$", lambda x: x.group(1) or "", c)
        t = re.sub(r"\s+", " ", t).strip()
        t = re.sub(r"^[-\d.、。，\s]+", "", t)
        if len(t) > 20 and not re.match(r"问渠示例设计", t):
            return t[:90] + ("…" if len(t) > 90 else "")
    return ""


CSS, JS = UI.CSS, UI.JS


def nav_html(site: Site, page: dict) -> str:
    out = []
    for gid, gname, _ in [("", "", [])] + GROUPS:
        ps = [p for p in site.pages if p["group"] == gid]
        if not ps:
            continue
        if gname:
            out.append(f'<div class="g">{html.escape(gname)}</div>')
        for p in ps:
            cur = p is page
            label = p["title"] if gid == "" else short_title(p)
            out.append(f'<a href="{p["url"]}"{" class=cur" if cur else ""}>{html.escape(label)}</a>')
            if cur:
                sub = [h for h in p["heads"] if h["l"] in (2, 3)]
                if sub:
                    out.append("<ul>")
                    open3 = False
                    for h in sub:
                        if h["l"] == 3 and not open3:
                            out.append("<ul>")
                            open3 = True
                        if h["l"] == 2 and open3:
                            out.append("</ul>")
                            open3 = False
                        out.append(f'<li><a href="#{h["id"]}">{html.escape(h["t"])}</a></li>')
                    if open3:
                        out.append("</ul>")
                    out.append("</ul>")
    return "".join(out)


def short_title(p: dict) -> str:
    """侧栏里短一点：去掉“WQ-LS ”“第 4 关 · ”这类前缀"""
    if p.get("attach"):
        return "附图与附件"
    t = p["title"]
    t = re.sub(r"^(WQ-LS\s*(工业直驱平缝机\s*·\s*)?|G\d\.\d\s*WQ-LS\s*)", "", t)
    t = re.sub(r"^(设计计算书\s*·\s*)?第\s*\d\s*关\s*[·：:]\s*", "", t)
    return t or p["title"]


def page_html(site: Site, page: dict, i: int) -> str:
    e = html.escape
    gname = next((g[1] for g in GROUPS if g[0] == page["group"]), "")
    head_end = """<link rel="stylesheet" href="spec.css"></head>\n<body>\n""" + UI.bar_html(page["url"] != "index.html")
    title = e(short_title(page) if page["group"] else "WQ-LS 设计说明书 · 工业直驱平缝机")
    top = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="WQ-LS 工业直驱平缝机设计说明书（问渠示例设计）：整机虚拟样机、十关设计文档、计算书、工程图 · Design documentation with a virtual prototype">
{head_end}"""
    if page["url"] == "index.html":
        body = UI.home_html(site, site.nums, page["html"], GROUPS)
        return top + f"""<div class="home" style="padding:0 16px"><div id="res"></div></div>{body}
<button id="totop" aria-label="回到顶部">↑</button><script src="spec.js"></script></body></html>
"""
    crumb = '<a href="index.html">总览</a>' + (f" › {e(gname)} › {e(short_title(page))}" if page["group"] else "")
    meta = f'原文：<code>{e(page["src"])}</code>' + (f' · 最后修改 {page["date"]}' if page["date"] else "")
    toc = "".join(f'<a class="l{h["l"]}" href="#{h["id"]}">{e(h["t"])}</a>' for h in page["heads"] if h["l"] in (2, 3))
    pv = site.pages[i - 1] if i > 0 else None
    nx = site.pages[i + 1] if i + 1 < len(site.pages) else None
    pn = '<div class="pn">' + (f'<a href="{pv["url"]}"><span>← 上一篇</span>{e(short_title(pv))}</a>' if pv else "<span></span>") \
        + (f'<a class="nx" href="{nx["url"]}"><span>下一篇 →</span>{e(short_title(nx))}</a>' if nx else "") + "</div>"
    first = next((p for p in site.pages if p["group"] == page["group"]), None) is page
    gidx = [g[0] for g in GROUPS].index(page["group"]) + 1 if page["group"] in [g[0] for g in GROUPS] else 0
    gate = UI.head_html(page["group"], gname, site.nums.get(page["group"], []), gidx) if first else ""
    return top + f"""<div class="wrap">
<nav class="side" aria-label="总目录">{nav_html(site, page)}</nav>
<main><div class="crumb">{crumb}</div><div class="meta">{meta}</div>{gate}
<div id="res"></div><article>{page["html"]}</article>{pn}</main>
<aside class="toc" aria-label="本篇目录">{('<b>本篇目录 · ON THIS PAGE</b>' + toc) if toc else ''}</aside>
</div>
<button id="totop" aria-label="回到顶部">↑</button>
<script src="spec.js"></script>
</body></html>
"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    site = Site()
    site.nums = UI.head_numbers()
    site.render("README.md", "")
    site.pages[0]["heads"].append(dict(l=2, id="all", t="全部篇目"))
    site.pages[0]["title"] = "总览"
    listed = {"README.md"}
    for gid, gname, order in GROUPS:
        if gid == "G7":
            site.bom_page()
            listed.add("G7/物料清单.json")
            continue
        mds = [gid + "/" + x for x in order]
        rest = sorted(str(p.relative_to(SRC)) for p in (SRC / gid).rglob("*.md") if str(p.relative_to(SRC)) not in mds)
        for rel in mds + rest:
            site.render(rel, gid)
            listed.add(rel)
    missing = [str(p.relative_to(SRC)) for p in SRC.rglob("*.md") if str(p.relative_to(SRC)) not in listed]
    assert not missing, f"这些文章不在任何一关里：{missing}"
    # 附图与附件放在每关最后
    pages = site.pages
    for gid, gname, _ in GROUPS:
        site.attach_page(gid, gname)
    att = {p["group"]: p for p in pages if p.get("attach")}
    order = []
    for p in [x for x in pages if not x.get("attach")]:
        order.append(p)
    final = [order[0]]
    for gid, _, _ in GROUPS:
        final += [p for p in order if p["group"] == gid]
        if gid in att:
            final.append(att[gid])
    site.pages = final
    for i, p in enumerate(site.pages):
        (OUT / p["url"]).write_text(page_html(site, p, i), encoding="utf-8")
    (OUT / "spec.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT / "spec.js").write_text(JS.strip() + "\n", encoding="utf-8")
    idx = []
    for p in site.pages:
        segs = re.split(r'(<h[1-4] id="(s\d+|all)"[^>]*>.*?</h[1-4]>)', p["html"], flags=re.S)
        hid, title = p["heads"][0]["id"] if p["heads"] else "", p["title"]
        buf = segs[0]
        k = 1
        while True:
            txt = re.sub(r"\s+", " ", strip_tags(buf)).strip()
            if txt or title:
                idx.append(dict(u=p["url"], id=hid, t=title, p=short_title(p) if p["group"] else "总览", x=txt[:4000]))
            if k >= len(segs):
                break
            hid, title = segs[k + 1], re.sub(r"#$", "", strip_tags(segs[k]).strip())
            buf = segs[k + 2] if k + 2 < len(segs) else ""
            k += 3
    (OUT / "search.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest_now(), ensure_ascii=False, indent=0), encoding="utf-8")
    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"{len(site.pages)} 页，{sum(1 for _ in (OUT / 'f').rglob('*') if _.is_file()) if (OUT / 'f').exists() else 0} 个文件，"
          f"共 {human(size)} → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        b = check()
        print("\n".join(b) or "一致")
        sys.exit(1 if b else 0)
    build()
