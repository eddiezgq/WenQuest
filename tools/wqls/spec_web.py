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
    return dict(script=sha1(SCRIPT), files=files)


def check() -> list[str]:
    m = OUT / "manifest.json"
    if not m.exists():
        return ["没有 spec/manifest.json：还没生成"]
    old, now = json.loads(m.read_text(encoding="utf-8")), manifest_now()
    bad = []
    if old.get("script") != now["script"]:
        bad.append("spec_web.py 改过")
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


CSS = r"""
:root{--bg:#fbfbfa;--panel:#f3f4f2;--ink:#1d2329;--mut:#5b6670;--line:#dde1e5;--acc:#0b4fae;--acc-bg:#e6eefb;--hl:#fff3c4;--code:rgba(127,127,127,.12)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15181b;--panel:#1b1f23;--ink:#e6e9ec;--mut:#9aa5ae;--line:#323a42;--acc:#7cb2ff;--acc-bg:#1d2b40;--hl:#4a3f12}}
:root[data-theme="dark"]{--bg:#15181b;--panel:#1b1f23;--ink:#e6e9ec;--mut:#9aa5ae;--line:#323a42;--acc:#7cb2ff;--acc-bg:#1d2b40;--hl:#4a3f12}
*{box-sizing:border-box}
html{scroll-padding-top:64px}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 system-ui,-apple-system,"Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
header.top{position:sticky;top:0;z-index:20;height:52px;display:flex;align-items:center;gap:12px;padding:0 16px;background:var(--panel);border-bottom:1px solid var(--line)}
header.top .brand{font-weight:650;color:var(--ink);white-space:nowrap}
header.top .brand small{font-weight:400;color:var(--mut);margin-left:6px}
header.top .sp{flex:1}
header.top a.ext{white-space:nowrap;font-size:14px}
#q{width:min(320px,40vw);height:34px;border:1px solid var(--line);border-radius:8px;padding:0 10px;background:var(--bg);color:var(--ink);font:inherit;font-size:14px}
#menu{display:none;border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:8px;height:34px;padding:0 10px;font:inherit;font-size:14px;cursor:pointer}
.wrap{display:grid;grid-template-columns:290px minmax(0,1fr) 230px}
nav.side{position:sticky;top:52px;height:calc(100vh - 52px);overflow:auto;border-right:1px solid var(--line);padding:12px 8px 40px;font-size:14px;line-height:1.45;background:var(--bg)}
nav.side .g{margin:14px 8px 4px;font-size:12px;font-weight:650;color:var(--mut);letter-spacing:.02em}
nav.side a{display:block;color:var(--ink);padding:4px 8px;border-radius:6px}
nav.side a:hover{background:var(--acc-bg);text-decoration:none}
nav.side a.cur{background:var(--acc-bg);color:var(--acc);font-weight:600}
nav.side ul{list-style:none;margin:2px 0 6px 10px;padding:0 0 0 8px;border-left:1px solid var(--line)}
nav.side ul a{font-size:13px;color:var(--mut);padding:3px 8px}
nav.side ul ul{margin-left:6px}
nav.side ul a.on,aside.toc a.on{color:var(--acc);font-weight:600}
main{min-width:0;padding:20px 32px 80px;max-width:900px}
.crumb{font-size:13px;color:var(--mut);margin-bottom:4px}
.crumb a{color:var(--mut)}
.meta{font-size:12.5px;color:var(--mut);border-bottom:1px solid var(--line);padding-bottom:10px;margin-bottom:8px}
.meta code{font-size:12px}
article h1{font-size:25px;line-height:1.35;margin:.3em 0 .5em}
article h2{font-size:20px;margin:2em 0 .6em;padding-bottom:4px;border-bottom:1px solid var(--line)}
article h3{font-size:17px;margin:1.6em 0 .5em}article h4{font-size:15px;margin:1.3em 0 .4em}
article h1:target,article h2:target,article h3:target,article h4:target{background:var(--hl);border-radius:4px}
.hl{margin-left:6px;color:var(--mut);opacity:0;font-weight:400;font-size:.8em}
h1:hover .hl,h2:hover .hl,h3:hover .hl,h4:hover .hl{opacity:1}
.tbl{overflow-x:auto;margin:1em 0}
table{border-collapse:collapse;font-size:13.5px;line-height:1.5}
td,th{border:1px solid var(--line);padding:5px 9px;vertical-align:top}th{background:var(--panel);text-align:left;white-space:nowrap}
code{font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);padding:1px 4px;border-radius:4px}
pre{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px}pre code{background:none;padding:0}
a.fl code{color:var(--acc)}
img{max-width:100%;height:auto;border-radius:4px}a.im{display:inline-block}
video{max-width:100%;border-radius:6px;background:#000}
blockquote{margin:1em 0;padding:2px 14px;border-left:3px solid var(--line);color:var(--mut)}
.math{overflow-x:auto;margin:1em 0}math{font-size:1.08em}
.mut{color:var(--mut);font-size:13px}
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
figure{margin:0 0 14px}figcaption{font-size:12.5px;color:var(--mut);margin-top:4px;word-break:break-all}
ul.files li{margin:3px 0}
.pn{display:flex;gap:12px;margin-top:48px;border-top:1px solid var(--line);padding-top:16px}
.pn a{flex:1;border:1px solid var(--line);border-radius:10px;padding:10px 14px;color:var(--ink)}
.pn a:hover{border-color:var(--acc);text-decoration:none}
.pn a span{display:block;font-size:12px;color:var(--mut)}.pn a.nx{text-align:right}
aside.toc{position:sticky;top:52px;height:calc(100vh - 52px);overflow:auto;padding:20px 14px 40px 8px;font-size:13px;line-height:1.45}
aside.toc b{display:block;font-size:12px;color:var(--mut);margin-bottom:6px}
aside.toc a{display:block;color:var(--mut);padding:3px 0 3px 10px;border-left:2px solid transparent}
aside.toc a.l3{padding-left:22px;font-size:12.5px}
aside.toc a.on{border-left-color:var(--acc)}
#totop{position:fixed;right:18px;bottom:18px;width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:var(--panel);color:var(--ink);font-size:18px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .2s;z-index:15}
#totop.show{opacity:1;pointer-events:auto}
#res{display:none}
body.searching #res{display:block}body.searching article,body.searching .pn{display:none}
#res .r{display:block;border-bottom:1px solid var(--line);padding:10px 0;color:var(--ink)}
#res .r b{color:var(--acc);font-weight:600}#res .r span{display:block;font-size:13px;color:var(--mut)}
#res mark{background:var(--hl);color:inherit;border-radius:2px}
.groups .grp{margin:18px 0 6px;font-weight:650}
.groups .doc{display:block;border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:8px 0;color:var(--ink)}
.groups .doc:hover{border-color:var(--acc);text-decoration:none}
.groups .doc b{color:var(--acc)}.groups .doc span{display:block;font-size:13px;color:var(--mut);margin-top:2px}
.notice{background:var(--acc-bg);border-radius:10px;padding:10px 14px;font-size:14px;margin:12px 0}
@media (max-width:1280px){.wrap{grid-template-columns:270px minmax(0,1fr)}aside.toc{display:none}}
@media (max-width:860px){
 .wrap{display:block}#menu{display:inline-block}
 nav.side{position:fixed;left:0;top:52px;width:min(320px,86vw);z-index:30;transform:translateX(-105%);transition:transform .2s;box-shadow:0 8px 30px rgba(0,0,0,.25)}
 body.nav nav.side{transform:none}
 main{padding:14px 16px 72px}header.top .brand small,header.top a.ext{display:none}#q{width:auto;flex:1;min-width:0}header.top .sp{display:none}
 article h1{font-size:21px}
}
@media print{header.top,nav.side,aside.toc,.pn,#totop{display:none}.wrap{display:block}main{max-width:none;padding:0}}
"""

JS = r"""
(function(){
var b=document.body,side=document.querySelector('nav.side');
document.getElementById('menu').onclick=function(){b.classList.toggle('nav')};
side.addEventListener('click',function(e){if(e.target.closest('a'))b.classList.remove('nav')});
var cur=side.querySelector('a.cur');if(cur)cur.scrollIntoView({block:'center'});
// 读到哪一节，左右两个目录跟着高亮
var hs=[].slice.call(document.querySelectorAll('article h1[id],article h2[id],article h3[id]'));
var links={};[].forEach.call(document.querySelectorAll('nav.side ul a,aside.toc a'),function(a){var h=a.getAttribute('href').split('#')[1];(links[h]=links[h]||[]).push(a)});
var last=null;
function spy(){var y=window.scrollY+90,id=hs.length?hs[0].id:null;for(var i=0;i<hs.length;i++){if(hs[i].offsetTop<=y)id=hs[i].id;else break}
 if(id===last)return;if(last&&links[last])links[last].forEach(function(a){a.classList.remove('on')});last=id;
 if(id&&links[id])links[id].forEach(function(a){a.classList.add('on');var box=a.closest('nav.side,aside.toc');var r=a.getBoundingClientRect(),rb=box.getBoundingClientRect();if(r.top<rb.top+40||r.bottom>rb.bottom-40)box.scrollTop+=r.top-rb.top-rb.height/2});
 document.getElementById('totop').classList.toggle('show',window.scrollY>600)}
window.addEventListener('scroll',spy,{passive:true});spy();
document.getElementById('totop').onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};
// 全文搜索
var q=document.getElementById('q'),res=document.getElementById('res'),idx=null,t=null;
function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function run(){var s=q.value.trim();if(!s){b.classList.remove('searching');return}
 if(!idx){fetch('search.json').then(function(r){return r.json()}).then(function(d){idx=d;run()});return}
 var ws=s.toLowerCase().split(/\s+/),out=[],n=0;
 idx.forEach(function(e){var x=e.x.toLowerCase(),tt=e.t.toLowerCase();if(!ws.every(function(w){return x.indexOf(w)>=0||tt.indexOf(w)>=0}))return;
  var p=x.indexOf(ws[0]),a=Math.max(0,p-40),snip=(a?'…':'')+e.x.substr(a,140)+'…';
  var hl=esc(snip);ws.forEach(function(w){hl=hl.replace(new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi'),function(m){return'<mark>'+m+'</mark>'})});
  if(n++<200)out.push('<a class="r" href="'+e.u+'#'+e.id+'"><b>'+esc(e.t)+'</b><span>'+esc(e.p)+'</span><span>'+hl+'</span></a>')});
 res.innerHTML='<p class="mut">“'+esc(s)+'”：'+n+' 处'+(n>200?'（只列前 200 处）':'')+'。按 Esc 清除。</p>'+out.join('');b.classList.add('searching');window.scrollTo(0,0)}
q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(run,180)});
q.addEventListener('keydown',function(e){if(e.key==='Escape'){q.value='';run()}});
document.addEventListener('keydown',function(e){if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus()}});
var m=location.search.match(/[?&]q=([^&]+)/);if(m){q.value=decodeURIComponent(m[1]);run()}
})();
"""


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
    gname = next((g[1] for g in GROUPS if g[0] == page["group"]), "")
    crumb = '<a href="index.html">总览</a>' + (f" › {html.escape(gname)} › {html.escape(short_title(page))}" if page["group"] else "")
    meta = f'原文：<code>{html.escape(page["src"])}</code>' + (f' · 最后修改 {page["date"]}' if page["date"] else "")
    toc = "".join(f'<a class="l{h["l"]}" href="#{h["id"]}">{html.escape(h["t"])}</a>' for h in page["heads"] if h["l"] in (2, 3))
    pv = site.pages[i - 1] if i > 0 else None
    nx = site.pages[i + 1] if i + 1 < len(site.pages) else None
    pn = '<div class="pn">' + (f'<a href="{pv["url"]}"><span>← 上一篇</span>{html.escape(short_title(pv))}</a>' if pv else "<span></span>") \
        + (f'<a class="nx" href="{nx["url"]}"><span>下一篇 →</span>{html.escape(short_title(nx))}</a>' if nx else "") + "</div>"
    body = page["html"]
    if page["url"] == "index.html":
        body = overview(site, body)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(short_title(page) if page['group'] else 'WQ-LS 设计说明书')}</title>
<meta name="description" content="WQ-LS 工业直驱平缝机设计说明书（问渠示例设计） · Design documentation (Chinese original)">
<link rel="stylesheet" href="spec.css"></head>
<body>
<header class="top"><button id="menu" aria-label="目录">☰ 目录</button><a class="brand" href="index.html">WQ-LS 设计说明书<small>Design documentation (Chinese original)</small></a>
<span class="sp"></span><input id="q" type="search" placeholder="搜索全文（/）" aria-label="搜索全文"><a class="ext" href="../index.html" target="_blank">三维整机 ↗</a></header>
<div class="wrap">
<nav class="side" aria-label="总目录">{nav_html(site, page)}</nav>
<main><div class="crumb">{crumb}</div><div class="meta">{meta}</div>
<div id="res"></div><article>{body}</article>{pn}</main>
<aside class="toc" aria-label="本篇目录">{('<b>本篇目录</b>' + toc) if toc else ''}</aside>
</div>
<button id="totop" aria-label="回到顶部">↑</button>
<script src="spec.js"></script>
</body></html>
"""


def overview(site: Site, readme: str) -> str:
    # README 里的旧表（只写到 G4）换成按关的全部篇目
    readme = re.sub(r'<div class="tbl"><table>.*?</table></div>', "", readme, count=1, flags=re.S)
    out = [readme, '<div class="notice">问渠示例设计：经计算和三维校核，<b>没有实物试制</b>，所有数值是示例值。左边是总目录，右上角可搜索全文。</div>',
           '<h2 id="all">全部篇目</h2><div class="groups">']
    for gid, gname, _ in GROUPS:
        ps = [p for p in site.pages if p["group"] == gid]
        if not ps:
            continue
        out.append(f'<div class="grp">{html.escape(gname)}</div>')
        for p in ps:
            out.append(f'<a class="doc" href="{p["url"]}"><b>{html.escape(short_title(p))}</b><span>{html.escape(p["desc"])}</span></a>')
    out.append("</div>")
    return "".join(out)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    site = Site()
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
