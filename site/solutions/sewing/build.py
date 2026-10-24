#!/usr/bin/env python3
"""官网“缝纫机企业解决方案”页（第 44 轮）：演示稿、讲稿全文、介绍页。

内容只有一份：《缝纫机设计与制造》课程包里的演示稿 textbook/web-editions/sewing/course/slides/sol_enterprise.yaml
（每页的讲稿就是 notes；数字由 course/calc/sol_enterprise.py 用缝纫机设计软件的计算核心算出）。改了它重新跑：

    python3 site/solutions/sewing/build.py

生成 deck.html（演示稿，单文件，S 键讲者窗口）、script.html（讲稿全文，可打印）、index.html（介绍页：短版视频、演示稿、完整版视频）。
视频（video/short.mp4、video/full.mp4 和封面 .jpg）由“公开课视频”工作流做好后压成网页用的 720p 放进 video/，有就显示。
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "textbook" / "web-editions" / "sewing" / "course" / "tools"))
import build_slides as B  # noqa: E402  （设好本书的课程目录，再取公用课件引擎）
import yaml  # noqa: E402

DECK = "sol_enterprise"
e = html.escape


def spec():
    s = yaml.safe_load((B.COURSE / "slides" / f"{DECK}.yaml").read_text(encoding="utf-8"))
    s = B.zh_pairs(s)
    return B.fill(s, B.run_programs(s.get("code") or [])), s


def page_title(sl):
    t = sl.get("title") or sl.get("kicker") or ["", ""]
    return t[0]


def script_html(sp) -> str:
    """讲稿全文：每页一节（页码、标题、要点、讲稿），可打印"""
    secs = []
    for k, sl in enumerate(sp["slides"], 1):
        if sl["layout"] == "section":
            secs.append(f'<h2 class="part">{e(sl["num"])}　{e(sl["title"][0])}</h2>')
            continue
        pts = [p[0] for p in sl.get("points") or sl.get("facts") or []]
        if sl["layout"] == "bignum":
            pts = [f'{n["label"][0]} {n["n"]} 项' for n in sl["nums"]]
        if sl["layout"] == "chain":
            pts = [" → ".join(x[0] for x in sl["steps"])]
        if sl["layout"] == "duo":
            pts = [f'{sl[c]["label"][0]}：{sl[c]["note"][0]}' for c in ("left", "right")]
        ul = "".join(f"<li>{e(p)}</li>" for p in pts)
        note = (sl.get("notes") or ["", ""])[0]
        secs.append(f'<section><div class="no">第 {k} 页</div><h3>{e(page_title(sl))}</h3>'
                    + (f"<ul>{ul}</ul>" if ul else "") + f'<p class="say">{e(note)}</p></section>')
    n = sum(len((s.get("notes") or ["", ""])[0]) for s in sp["slides"])
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>讲稿全文 · 缝纫机企业解决方案 · 问渠</title><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
:root{{--paper:#f4f2ec;--ink:#121c21;--muted:#56656b;--line:#d6d2c6;--accent:#f2b705;--accent-ink:#7a5a00}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--paper:#0f181c;--ink:#e6ecee;--muted:#93a3a9;--line:#2a3a41;--accent-ink:#f2c94c}}}}
body{{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.85 "Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif}}
main{{max-width:820px;margin:0 auto;padding:36px 20px 80px}}
h1{{font:900 30px/1.3 "Noto Serif SC",serif;margin:0 0 6px}}.lede{{color:var(--muted);margin:0 0 28px}}
.bar{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:30px}}.bar a{{color:var(--accent-ink);text-decoration:none;font-weight:600}}
h2.part{{font:700 22px/1.4 "Noto Serif SC",serif;margin:42px 0 8px;padding-top:18px;border-top:2px solid var(--accent)}}
section{{padding:16px 0;border-bottom:1px solid var(--line);break-inside:avoid}}
.no{{font:500 13px/1 ui-monospace,monospace;color:var(--muted)}}h3{{margin:6px 0 6px;font-size:20px}}
ul{{margin:4px 0 8px;padding-left:1.2em;color:var(--muted)}}.say{{margin:6px 0 0}}
@media print{{.bar{{display:none}}body{{background:#fff;color:#000}}}}
</style></head><body><main>
<h1>缝纫机企业解决方案 · 讲稿全文</h1>
<p class="lede">共 {len(sp["slides"])} 页，讲稿约 {n} 字，讲下来十分钟左右。放映时按 S 键打开讲者窗口，看到的是同一份讲稿。数字都由问渠缝纫机设计软件的计算核心算出。</p>
<div class="bar"><a href="deck.html">放映演示稿 →</a><a href="./">回到方案介绍</a><a href="javascript:print()">打印</a></div>
{"".join(secs)}
</main></body></html>"""


def video_block(name, title, note):
    """视频由工作流压好放进 video/（可能比页面晚到）：文件还没有时这块自己隐藏（短版的位置换成演示稿）"""
    return (f'<figure class="vid" data-v="{name}"><video controls preload="metadata" playsinline poster="video/{name}.jpg">'
            f'<source src="video/{name}.mp4" type="video/mp4"><track kind="subtitles" srclang="zh" label="中文字幕" src="video/{name}.vtt"></video>'
            f'<figcaption><b>{e(title)}</b>　{e(note)}</figcaption></figure>')


def index_html(sp) -> str:
    v = B.run_programs(["sol_enterprise"])["sol_enterprise"]
    facts = [("机型", v["machines"], "种"), ("红绿灯校核", v["checks_all"], "项"), ("教材", v["lessons"], "讲"), ("虚拟实验与三维模型", v["labs"], "个")]
    dl = "".join(f"<div><dt>{a}</dt><dd>{b}<small>{c}</small></dd></div>" for a, b, c in facts)
    short = video_block("short", "三分钟版", "先看这个")
    full = video_block("full", "完整版", "十分钟，和演示稿一页一页对应")
    rows = []
    for sl in sp["slides"]:
        if sl["layout"] == "section":
            rows.append(f'<li class="sec">{e(sl["title"][0])}</li>')
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="description" content="问渠缝纫机企业解决方案：五种机型的设计与校核软件、仿真与数控编程、数字工厂、售后数字分身和人才培养，一条线、一套数据。">
<title>缝纫机企业解决方案 · 问渠</title>
<link rel="stylesheet" href="/vendor/fonts/noto-serif-sc.css"><link rel="stylesheet" href="/vendor/fonts/noto-sans-sc.css"><link rel="stylesheet" href="/vendor/fonts/ibm-plex-mono.css">
<style>
:root{{--night:#0a1216;--night-line:#22323a;--night-ink:#e9eef0;--night-muted:#8fa1a8;--paper:#f4f2ec;--surface:#fbfaf6;--ink:#121c21;--muted:#56656b;--line:#d6d2c6;--accent:#f2b705;--accent-ink:#7a5a00;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--paper:#0f181c;--surface:#152127;--ink:#e6ecee;--muted:#93a3a9;--line:#2a3a41;--accent-ink:#f2c94c;color-scheme:dark}}}}
:root[data-theme="dark"]{{--paper:#0f181c;--surface:#152127;--ink:#e6ecee;--muted:#93a3a9;--line:#2a3a41;--accent-ink:#f2c94c;color-scheme:dark}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:400 16px/1.75 "Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif}}
a{{color:inherit}}.wrap{{max-width:1180px;margin:0 auto;padding-inline:16px}}
.top{{background:var(--night);color:var(--night-ink);border-bottom:1px solid var(--night-line)}}.top .wrap{{display:flex;align-items:center;gap:18px;height:60px}}
.brand{{text-decoration:none;font:900 20px/1 "Noto Serif SC",serif;letter-spacing:.04em}}.crumb{{font-size:14px;color:var(--night-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.crumb a{{text-decoration:none}}
.hero{{background:var(--night);color:var(--night-ink)}}.hero .wrap{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:40px;padding-block:52px 48px;align-items:center}}
.eyebrow{{font:500 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.16em;color:var(--accent);margin:0 0 16px}}
h1{{margin:0;font:900 clamp(30px,4.2vw,48px)/1.2 "Noto Serif SC",serif}}.lede{{margin:20px 0 0;color:var(--night-muted);font-size:17px;max-width:32em}}
.facts{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin:28px 0 0;border-top:1px solid var(--night-line)}}.facts div{{padding:14px 10px 0 0}}
.facts dt{{font-size:12px;color:var(--night-muted)}}.facts dd{{margin:4px 0 0;font:600 26px/1.1 "Noto Serif SC",serif}}.facts dd small{{font:400 13px/1 sans-serif;color:var(--night-muted);margin-left:3px}}
.btns{{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}}.btn{{display:inline-block;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:600;border:1px solid var(--night-line)}}
.btn.pri{{background:var(--accent);color:#0a1216;border-color:var(--accent)}}
.vid{{margin:0}}.vid video{{width:100%;aspect-ratio:16/9;background:#000;border-radius:6px;display:block}}.vid figcaption{{font-size:14px;color:var(--night-muted);margin-top:8px}}
section{{padding-block:52px}}h2{{margin:0 0 6px;font:700 clamp(22px,3vw,30px)/1.3 "Noto Serif SC",serif}}.sub{{margin:0 0 24px;color:var(--muted);max-width:46em}}
.deck{{position:relative;width:100%;aspect-ratio:16/9;border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#000}}.deck iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.links{{display:flex;flex-wrap:wrap;gap:18px;margin-top:14px}}.links a{{color:var(--accent-ink);font-weight:600;text-decoration:none}}
.parts{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:0;padding:0;list-style:none}}
.parts li{{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:18px}}.parts b{{display:block;font:700 18px/1.4 "Noto Serif SC",serif;margin-bottom:6px}}.parts span{{color:var(--muted);font-size:15px}}
.cta{{background:var(--night);color:var(--night-ink)}}.cta p{{color:var(--night-muted)}}
@media (max-width:820px){{.hero .wrap{{grid-template-columns:1fr;gap:28px}}.parts{{grid-template-columns:1fr}}.facts{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
</style>
</head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="/">问渠</a><span class="crumb"><a href="/#sol-enterprise">企业解决方案</a> › 缝纫机</span></div></header>
<div class="hero"><div class="wrap">
  <div>
    <p class="eyebrow">企业解决方案 · 缝纫机</p>
    <h1>缝纫机企业解决方案</h1>
    <p class="lede">新机型在设计时就知道行不行：五种机型的设计与校核软件，接上仿真和数控编程；批准的设计直接到车间，卖出的机器在线监测；教材、课程、实验配齐，人才跟得上。一条线、一套数据，浏览器里就能用。</p>
    <dl class="facts">{dl}</dl>
    <div class="btns"><a class="btn pri" href="deck.html" target="_blank" rel="noopener">放映演示稿</a><a class="btn" href="script.html">讲稿全文</a><a class="btn" href="/#contact">预约演示</a></div>
  </div>
  <div id="heroV">{short}</div>
</div></div>
<main>
<section><div class="wrap">
  <h2>演示稿</h2>
  <p class="sub">像幻灯片一样一页一页翻（→ 或空格下一步，F 全屏）；三维样机、花样机、刺绣机这些页面是活的，可以直接拖动、操作。去企业讲的时候按 S 键打开讲者窗口，看着讲稿讲。</p>
  <div class="deck"><iframe src="deck.html" title="缝纫机企业解决方案 · 演示稿" loading="lazy" allow="fullscreen"></iframe></div>
  <div class="links"><a href="deck.html" target="_blank" rel="noopener">新窗口全屏放映 →</a><a href="script.html">讲稿全文（可打印）→</a></div>
</div></section>
<section id="fullV"><div class="wrap"><h2>介绍片</h2><p class="sub">配音：AI 合成（讲者本人声音）。画面就是上面的演示稿，数字由软件的计算核心算出。</p>{full}</div></section>
<section><div class="wrap">
  <h2>方案里有什么</h2>
  <p class="sub">每一块都能单独用，也能连成一条线。</p>
  <ul class="parts">
    <li><b>缝纫机设计软件</b><span>平缝机、包缝机、绷缝机、电子花样机、多头刺绣机；改参数当场红绿灯；出计算书、调机卡、STEP、DXF；也能装进 FreeCAD。</span></li>
    <li><b>仿真与加工</b><span>有限元强度与疲劳、模态、动力学、拓扑减重后复核；伺服选型；零件和花样模板直接出数控程序并试切检查。</span></li>
    <li><b>设计到车间</b><span>发布审批，批准才生效；物料版本、BOM、工单、程序自动更新；报工、质检、追溯。</span></li>
    <li><b>售后数字分身</b><span>卖出的机器联网上报，健康度、剩余寿命，提前安排维护；现场数据反馈设计。</span></li>
    <li><b>人才培养</b><span>教材《缝纫机设计与制造》、网页课件、公开课视频、虚拟实验，真机拆装套件。</span></li>
    <li><b>部署</b><span>浏览器里用，不装软件；计算在自己的服务器上，企业数据不出平台；国内只用已备案的大模型。</span></li>
  </ul>
  <div class="links"><a href="https://learn.wenquestrobotics.com/pages/sewing/sewing">免费试算缝纫机设计软件 →</a><a href="/#sewing-software">软件介绍 →</a></div>
</div></section>
<section class="cta"><div class="wrap"><h2>预约演示</h2><p>我们可以上门或在线演示，用贵厂的机型现场算一遍。</p><div class="btns"><a class="btn pri" href="/#contact">联系我们</a></div></div></section>
</main>
<script>
// 视频还没放上来时：短版的位置换成演示稿，完整版那一节不显示
document.querySelectorAll('figure.vid').forEach(function (f) {{
  var src = f.querySelector('source');
  src.addEventListener('error', function () {{
    if (f.dataset.v === 'short') document.getElementById('heroV').innerHTML = '<div class="deck"><iframe src="deck.html" title="演示稿" loading="lazy" allow="fullscreen"></iframe></div>';
    else document.getElementById('fullV').style.display = 'none';
  }});
}});
</script>
</body>
</html>
"""


def main():
    sp, _ = spec()
    B.make_deck(DECK, HERE, "zh", name="deck.html")
    (HERE / "script.html").write_text(script_html(sp), encoding="utf-8")
    (HERE / "index.html").write_text(index_html(sp), encoding="utf-8")
    print("deck.html", round((HERE / "deck.html").stat().st_size / 1e6, 2), "MB · script.html · index.html")


if __name__ == "__main__":
    main()
