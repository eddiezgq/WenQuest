"""问渠客服的知识库（第 87 轮）：把面向用户的帮助文件、首页清单、国内版官网文字稿切成段落，写成
services/gateway/app/assist_kb.json（网关启动时读入、建检索索引）；同时把帮助文件生成公开网页
site/help/<编号>.html（美国站），客服回答里的出处链接指向这些页面。
国内站：只用不含国内版官网禁用词（tools/site_cn/check_cn.py 的 BANNED）的段落（cn: true），出处不带链接——
国内版官网只提供 site/cn/ 里的页面，帮助网页暂不上国内站。

    python3 tools/assistant/build_kb.py

资料改了就重跑一次（推送前），客服就跟着改。部署、运维、开发类的帮助文件不进知识库（EXCLUDE）。
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

import sys

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[2]
HELP = ROOT / "docs" / "帮助"
OUT = ROOT / "services" / "gateway" / "app" / "assist_kb.json"
EXCLUDE = {"GPU平台接入说明", "国内服务器加模块（质量ERP等）", "官网典型应用案例页", "官网首页", "数字工厂上线与维护", "数字工厂课程接口",
           "本地测试环境", "视频课制作与发布", "解决方案介绍片"}
ROUND = re.compile(r"[（(]\s*(?:第\s*\d+\s*轮[^）)]*|\d{4}-\d{2}-\d{2}\s*起)[）)]")
MAX = 900
# 给管理员、运维、开发看的小节不进客服（来问的是访客和用户；2026-11-06 “管理员能打开 ERP 吗”被这些小节顶走）
STAFF = re.compile(r"给维护|运维|技术备注|给开发|开发者|数据格式|接口说明|一次性设置|排查|日志|密钥|\.env|部署与|上线与维护|源文件")
sys.path.insert(0, str(ROOT / "tools" / "site_cn"))
from check_cn import BANNED  # noqa: E402


def cn_ok(t: str) -> bool:
    return not any(b in t for b in BANNED)


def cn_text(t: str) -> str:
    """国内站用的写法：域名换成国内的；“第一步、第一次”这类序数写成数字（“第一”是广告法禁用词）"""
    t = t.replace("wenquestrobotics.com", "wenquestech.online")
    return t.replace("第一", "第 1 ")


def add_cn(c: dict) -> dict:
    alt = {k: cn_text(c.get(k, "")) for k in ("text", "title", "section")}
    c["cn"] = cn_ok(" ".join(alt.values()))
    if c["cn"]:
        for k, v in alt.items():
            if v != c.get(k, ""):
                c[k + "_cn"] = v
    return c


def slug(name: str) -> str:
    return "h" + hashlib.sha1(name.encode()).hexdigest()[:8]


def clean_title(t: str) -> str:
    return ROUND.sub("", t).strip()


def chunks_of(md: str):
    """按二、三级标题切段；太长的段再按空行切；每段带上所在小节的标题"""
    title, sec, buf = "", "", []
    for line in md.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            if buf:
                yield sec, "\n".join(buf).strip()
                buf = []
            if len(m.group(1)) == 1 and not title:
                title = m.group(2)
            sec = clean_title(m.group(2))
            continue
        buf.append(line)
        if sum(len(x) for x in buf) > MAX and line.strip() == "":
            yield sec, "\n".join(buf).strip()
            buf = []
    if buf:
        yield sec, "\n".join(buf).strip()


JUNK = [re.compile(p) for p in (r"(?:-{3,}\s*)+", r"第\s*\d+\s*轮起?[^：:。；]*[：:]?", r"[（(]\s*\d{4}-\d{2}-\d{2}[^）)]*[）)]",
                                  r"\S*(?:docs|tools|services|apps|textbook|factory)/[\w./\-]+\S*", r"python3?\s+\S+\.py[^。；]*")]


def tidy(t: str) -> str:
    """给客服用的文字：去掉表格分隔线、轮次备注、文件路径和命令（访客看不懂也用不上）"""
    for j in JUNK:
        t = j.sub(" ", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def plain(md: str) -> str:
    t = re.sub(r"```.*?```", " ", md, flags=re.S)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[`*_>#|]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


PAGE = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 问渠帮助</title><style>
:root{{--ink:#121c21;--muted:#56656b;--line:#d6d2c6;--paper:#fbfaf6;--accent:#2563eb;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root{{--ink:#e6ecee;--muted:#93a3a9;--line:#2a3a41;--paper:#0f181c;--accent:#7aa7ff;color-scheme:dark}}}}
body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.75 "Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:24px 16px 64px}} a{{color:var(--accent)}} h1{{font:700 26px/1.3 serif}} h2{{margin-top:28px}}
table{{border-collapse:collapse;width:100%;font-size:14.5px;display:block;overflow-x:auto}} th,td{{border:1px solid var(--line);padding:6px 8px;text-align:left}}
code,pre{{background:color-mix(in srgb,var(--ink) 7%,transparent);border-radius:4px;padding:1px 4px}} pre{{padding:10px;overflow-x:auto}}
.top{{font-size:14px;color:var(--muted)}}
</style></head><body><main><p class="top"><a href="{home}">← {brand}</a> · <a href="index.html">帮助目录</a></p>
{body}</main><script src="/assist.js" defer></script></body></html>"""


def main():
    kb, pages = [], []
    for f in sorted(HELP.glob("*.md")):
        if f.stem in EXCLUDE:
            continue
        md = f.read_text(encoding="utf-8")
        first = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), f.stem)
        title = clean_title(first)
        sid = slug(f.stem)
        pages.append((sid, title, md))
        for i, (sec, text) in enumerate(chunks_of(md)):
            t = tidy(plain(text))
            if len(t) < 30 or STAFF.search(sec or ""):
                continue
            kb.append(add_cn({"id": f"{sid}-{i}", "doc": f.stem, "title": title, "section": sec if sec != title else "",
                       "text": t[:1600], "url": f"/help/{sid}.html", "lang": "zh"}))
    cat = yaml.safe_load((ROOT / "tools" / "site_home" / "catalog.yaml").read_text(encoding="utf-8"))
    for g in cat["groups"]:
        for it in g["items"]:
            url = it["url"] if it["url"].startswith("http") else it["url"]
            kb.append({"id": "cat-" + slug(it["zh"]), "doc": "首页清单", "title": f"{it['zh']}（{g['zh']}）", "section": "",
                       "text": f"{it['zh']} / {it['en']}：{it['dz']}。{it['de']}。" + ("需要登录。" if it.get("login") else "不用登录，直接打开。")
                               + f" 入口：{url}", "url": url, "lang": "zh+en", "cn": False})
    cn = ROOT / "docs" / "方案" / "国内版官网文字稿.md"
    if cn.exists():
        for i, (sec, text) in enumerate(chunks_of(cn.read_text(encoding="utf-8"))):
            t = tidy(plain(re.sub(r"〔[^〕]*〕", "", text)))
            if len(t) >= 30:
                kb.append(add_cn({"id": f"cn-{i}", "doc": "问渠科技官网", "title": "问渠科技", "section": sec, "text": t[:1600],
                           "url": "/about/", "lang": "zh", "us": False}))
    faq = yaml.safe_load((Path(__file__).with_name("faq.yaml")).read_text(encoding="utf-8"))
    for f in faq:
        sites = f.get("sites") or ["cn", "us"]
        kb.append({"id": "faq-" + f["id"], "doc": "常见问题", "title": f["q"]["zh"][0], "section": "", "faq": True,
                   "q": f["q"], "a": f["a"], "link": f.get("link") or {}, "text": f["a"]["zh"],
                   "url": (f.get("link") or {}).get("us"), "lang": "zh+en", "cn": "cn" in sites, "us": "us" in sites})
    OUT.write_text(json.dumps({"chunks": kb}, ensure_ascii=False), encoding="utf-8")
    # 公开的帮助网页：美国站 site/help/，国内站 site/cn/help/
    for base, home, brand in ((ROOT / "site" / "help", "/", "问渠 WenQuest"),):
        base.mkdir(parents=True, exist_ok=True)
        for sid, title, md in pages:
            body = markdown.markdown(ROUND.sub("", md), extensions=["tables", "fenced_code"])
            (base / f"{sid}.html").write_text(PAGE.format(title=html.escape(title), body=body, home=home, brand=brand), encoding="utf-8")
        idx = "<h1>帮助目录</h1><ul>" + "".join(f'<li><a href="{sid}.html">{html.escape(t)}</a></li>' for sid, t, _ in sorted(pages, key=lambda x: x[1])) + "</ul>"
        (base / "index.html").write_text(PAGE.format(title="帮助目录", body=idx, home=home, brand=brand), encoding="utf-8")
    print(f"知识库 {len(kb)} 段，帮助网页 {len(pages)} 篇 → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
