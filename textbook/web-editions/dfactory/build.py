# -*- coding: utf-8 -*-
"""《数字工厂实训》网页版（第 29 轮，由《缝纫机设计与制造》的 build.py 改来）：zh 在根目录，en 在 en/。"""
import re, os, json, html, shutil, glob
from book import PARTS, CH, TITLE, SUBTITLE, part_of, NEW

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out')   # overridden by the command-line argument (CI: textbook/build/dfactory/webed)
STYLE = open(os.path.join(ROOT, 'style.html')).read()
SCRIPT = open(os.path.join(ROOT, 'script.html')).read()
SCRIPT_IX = open(os.path.join(ROOT, 'script_index.html')).read()

EXTRA_CSS = """<style>
.lang a{color:var(--muted);text-decoration:none}.lang a:hover{color:var(--ink)}.lang b{font-weight:600}
.math{overflow-x:auto;overflow-y:hidden;margin:.6em 0 1.2em;padding:6px 0;font-size:1.08em}
.math math{font-size:1.08em}
pre code{white-space:pre}
.fig svg{display:block;width:100%;height:auto}
.tbl caption{caption-side:top;text-align:left;font-size:.86rem;color:var(--muted);padding-bottom:6px}
.callout{margin:1.6em 0;border-left:3px solid var(--bobbin);background:var(--bobbin-soft);padding:10px 16px;border-radius:0 8px 8px 0;font-size:.95rem}
.callout p:last-child{margin-bottom:0}
.refs{font-size:.88rem;line-height:1.6}.refs li{margin:.3em 0}
.new-badge{font-family:var(--f-mono);font-size:.68rem;letter-spacing:.08em;color:var(--bobbin);border:1px solid currentColor;border-radius:4px;padding:0 5px;margin-left:6px;vertical-align:2px}
</style>"""

T = {
 'zh': dict(toc='目录', res='互动资源', side='本章目录', ch=lambda n: f'第 {n} 章', run='在本页运行', collapse='收起',
            prev='← ', next=' →', theme='切换深浅色', lang_html='zh-CN'),
 'en': dict(toc='Contents', res='Interactive resources', side='In this chapter', ch=lambda n: f'Chapter {n}', run='Run on this page',
            collapse='Collapse', prev='← ', next=' →', theme='Toggle light/dark', lang_html='en'),
}

def head(lang, title):
    font = '' if lang == 'zh' else ''
    return (f'<!doctype html><html lang="{T[lang]["lang_html"]}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<title>{html.escape(title)}</title>{STYLE}{EXTRA_CSS}</head><body>')

def bar(lang, here, page):
    t = T[lang]
    pre = '' if lang == 'zh' else ''
    if lang == 'zh':
        sw = f'<span class="lang"><b>中文</b> · <a href="en/{page}" hreflang="en">English</a></span>'
    else:
        sw = f'<span class="lang"><a href="../{page}" hreflang="zh-CN">中文</a> · <b>English</b></span>'
    cur = lambda k: ' aria-current="page"' if here == k else ''
    return (f'<header class="bar"><a class="brand" href="index.html"><span class="stitch-mark" aria-hidden="true"></span>{TITLE[lang]}</a>'
            f'<nav class="barnav"><a href="index.html#toc"{cur("toc")}>{t["toc"]}</a><a href="resources.html"{cur("res")}>{t["res"]}</a>'
            f'{sw}<button type="button" class="theme" aria-label="{t["theme"]}">◐</button></nav></header>')

def fix_math(s):
    def rep(m):
        tex = html.unescape(m.group(1)).strip()
        return '<div class="math">\\[' + html.escape(tex, quote=False) + '\\]</div>'
    return re.sub(r'<pre><code class="language-math">(.*?)</code></pre>', rep, s, flags=re.S)

def script(lang, index=False):
    s = SCRIPT_IX if index else SCRIPT
    s = s.replace("lb.querySelector('img').src = a.getAttribute('href');", "var im = a.querySelector('img'); lb.querySelector('img').src = im ? im.src : a.getAttribute('href');")
    s = s.replace("katex.render(tex, el, { displayMode: true, throwOnError: false })",
                  "katex.render(tex, el, { displayMode: true, throwOnError: false, output: 'mathml' })")
    if lang == 'en':
        s = s.replace("'收起'", "'Collapse'").replace("'在本页运行'", "'Run on this page'")
        for a, b in (("'订单'", "'Orders'"), ("'物料'", "'Materials'"), ("'设备'", "'Machines'"), ("'人员'", "'People'"),
                     ("'质量'", "'Quality'"), ("'安全'", "'Safety'"), ("'能源'", "'Energy'"), ("'现金'", "'Cash'"),
                     ("'厂情中枢'", "'Factory hub'"), ("'异常：'", "'Exception: '")):
            s = s.replace(a, b)
    return '<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>' + s

def eyebrow(lang, n):
    p = part_of(n)
    return f'{p[0]} · {p[1]}' if lang == 'zh' else p[2]

def chap_title(lang, n):
    return CH[n][0] if lang == 'zh' else CH[n][1]

def build_chapter(lang, n):
    src = os.path.join(ROOT, 'src', lang, f'ch{n:02d}.html')
    if not os.path.exists(src):
        return False
    fr = open(src).read()
    fr = fix_math(fr)
    # normalise eyebrow + h1 from metadata
    fr = re.sub(r'<p class="eyebrow">.*?</p>', f'<p class="eyebrow">{eyebrow(lang, n)}</p>', fr, count=1, flags=re.S)
    fr = re.sub(r'<h1>.*?</h1>', f'<h1><span class="chno">{T[lang]["ch"](n)}</span>{chap_title(lang, n)}</h1>', fr, count=1, flags=re.S)
    if lang == 'en':
        fr = fr.replace('src="img/', 'src="../img/').replace('href="img/', 'href="../img/')
        # English figures where they exist (img/en/<name>), else the original
        fr = re.sub(r'(src|href)="\.\./img/([^"/]+)\.png"', lambda m: f'{m.group(1)}="../img/en/{m.group(2)}.png"' if os.path.exists(os.path.join(ROOT, 'img', 'en', m.group(2) + '.webp')) else m.group(0), fr)
    # 本章的网页互动课件（第 24 轮）：标题下放一个“放映课件”按钮
    if os.path.exists(os.path.join(ROOT, 'course', 'slides', f'ch{n:02d}.yaml')):
        href = ('' if lang == 'zh' else '../') + f'slides/ch{n:02d}.html'
        btn = (f'<p class="deck-link"><a class="chip" href="{href}" target="_blank" rel="noopener"><b>{"课件" if lang == "zh" else "Slides"}</b>'
               f'{"放映本讲网页课件（动画和实验在页里可操作）" if lang == "zh" else "Present the interactive web slides of this lecture"} ↗</a></p>')
        fr = re.sub(r'(</h1>)', r'\1' + btn.replace('\\', '\\\\'), fr, count=1)
    # images are stored as WebP in the repository
    fr = re.sub(r'((?:src|href)="(?:\.\./)?img/[^"]+)\.png"', r'\1.webp"', fr)
    # side nav from h3 ids
    items = re.findall(r'<h3 id="([^"]+)">(.*?)</h3>', fr, flags=re.S)
    side = ''.join(f'<li><a href="#{i}">{re.sub("<[^>]+>", "", t)}</a></li>' for i, t in items)
    order = [m for m in sorted(CH) if os.path.exists(os.path.join(ROOT, 'src', lang, f'ch{m:02d}.html'))]   # 只链到写好了的章
    k = order.index(n)
    prv = f'<a href="ch{order[k-1]:02d}.html">{T[lang]["prev"]}{T[lang]["ch"](order[k-1])} {chap_title(lang, order[k-1])}</a>' if k > 0 else '<span></span>'
    nxt = f'<a href="ch{order[k+1]:02d}.html">{T[lang]["ch"](order[k+1])} {chap_title(lang, order[k+1])}{T[lang]["next"]}</a>' if k + 1 < len(order) else '<span></span>'
    page = f'ch{n:02d}.html'
    title = f'{T[lang]["ch"](n)} {chap_title(lang, n)} · {TITLE[lang]}'
    out = (head(lang, title) + bar(lang, '', page) +
           f'<div class="layout"><aside class="side"><details open><summary>{T[lang]["side"]}</summary><ol>{side}</ol></details></aside>'
           f'<main class="chapter">{fr}<nav class="pager">{prv}{nxt}</nav></main></div>'
           '<div class="lightbox" hidden><img alt=""></div>' + script(lang) + '</body></html>')
    d = OUT if lang == 'zh' else os.path.join(OUT, 'en')
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, page), 'w').write(out)
    return True

def toc(lang):
    zh = lang == 'zh'
    parts = []
    for p in PARTS:
        lis = []
        for n in p[3]:
            ready = os.path.exists(os.path.join(ROOT, 'src', lang, f'ch{n:02d}.html'))
            new = ' <span class="new-badge">NEW</span>' if n in NEW else ''
            st = ('可读' if zh else 'Ready') if ready else ('编写中' if zh else 'Draft')
            t = CH[n][0] if zh else CH[n][1]
            d = CH[n][2] if zh else CH[n][3]
            if ready:
                lis.append(f'<li class="ready"><a href="ch{n:02d}.html"><span class="n">{n}</span><span class="t">{t}{new}</span><span class="d">{d}</span><span class="st">{st}</span></a></li>')
            else:
                lis.append(f'<li><div><span class="n">{n}</span><span class="t">{t}</span><span class="d">{d}</span><span class="st">{st}</span></div></li>')
        label = p[0] if zh else p[2].split(' · ')[0]
        name = p[1] if zh else p[2].split(' · ')[1]
        parts.append(f'<section class="part"><h3><span>{label}</span>{name}</h3><ol>{"".join(lis)}</ol></section>')
    return ''.join(parts)

def count_ready(lang):
    return sum(os.path.exists(os.path.join(ROOT, 'src', lang, f'ch{n:02d}.html')) for n in CH)

def resources(lang):
    return json.load(open(os.path.join(ROOT, f'res_{lang}.json')))

def build_index(lang):
    zh = lang == 'zh'
    res = resources(lang)
    nready = count_ready(lang)
    first = min(n for n in CH if os.path.exists(os.path.join(ROOT, 'src', lang, f'ch{n:02d}.html')))
    if zh:
        cover = (f'<section class="cover"><div class="cover-text"><p class="eyebrow">特色实践课教材 · 网页版 · {SUBTITLE["zh"]}</p><h1>数字工厂<br>实训</h1>'
                 '<p class="lede">一座真在跑的减速器厂：订单、物料、设备、人员、质量、安全、能源和钱连在一起。每一章从厂里出的一件事讲起——停机、保养逾期、客户拖款——学会发现异常、追到原因、算出几种处理方案的代价，再在问渠数字工厂里亲手做一次决定。</p>'
                 f'<div class="stats"><div><b>{nready}</b><span>章已可读</span></div><div><b>{len(CH)}</b><span>章计划</span></div><div><b>{len(res)}</b><span>个动画与虚拟实验</span></div></div>'
                 f'<div class="cta"><a class="btn" href="ch{first:02d}.html">从第 {first} 章开始读</a><a class="btn ghost" href="resources.html">浏览互动资源</a></div></div>'
                 '<figure class="cover-art"><canvas id="factoryCanvas" width="560" height="360" aria-label="厂情中枢示意动画"></canvas><figcaption>八个领域的数据汇到厂情中枢；哪里出了异常，中枢沿因果链追过去</figcaption></figure></section>')
        tochead = '<h2>全书目录</h2><p class="muted">四篇十二章，一章对应课程的一讲（4 学时：1 学时概念与建模，3 学时在数字工厂里做实验）。标“可读”的章节已经写完，其余在编写中。</p>'
        foot = '<p class="foot">本网页版由书稿自动生成，与书稿同步更新。书中的工厂数据取自问渠数字工厂的教学情景，标“示意值”的为教学设定。</p>'
    else:
        cover = (f'<section class="cover"><div class="cover-text"><p class="eyebrow">Practicum textbook · web edition · {SUBTITLE["en"]}</p><h1>Digital Factory<br>Practicum</h1>'
                 '<p class="lede">A gearbox plant that really runs: orders, materials, machines, people, quality, safety, energy and money are all connected. Every chapter starts from something that happens in the plant (a breakdown, an overdue service, a customer who will not pay) and shows how to spot the exception, trace its cause, price the options and then make the decision yourself in the WenQuest digital factory.</p>'
                 f'<div class="stats"><div><b>{nready}</b><span>chapters ready</span></div><div><b>{len(CH)}</b><span>chapters planned</span></div><div><b>{len(res)}</b><span>animations and labs</span></div></div>'
                 f'<div class="cta"><a class="btn" href="ch{first:02d}.html">Start with Chapter {first}</a><a class="btn ghost" href="resources.html">Browse resources</a></div></div>'
                 '<figure class="cover-art"><canvas id="factoryCanvas" width="560" height="360" aria-label="Animation of the factory hub"></canvas><figcaption>Data from eight domains flows into the factory hub; when something goes wrong, the hub follows the causal chain back</figcaption></figure></section>')
        tochead = '<h2>Contents</h2><p class="muted">Four parts, twelve chapters, one per lecture (4 hours each: one hour of concepts and modelling, three hours of lab work in the digital factory). Chapters marked Ready are complete; the rest are being written.</p>'
        foot = '<p class="foot">This web edition is generated from the manuscript and updated with it. Plant data come from the teaching scenarios of the WenQuest digital factory; values marked “illustrative” are teaching settings.</p>'
    out = (head(lang, TITLE[lang]) + bar(lang, 'toc', 'index.html') + '<main class="home">' + cover +
           f'<section id="toc" class="toc">{tochead}{toc(lang)}{foot}</section></main>' + script(lang, index=True) + '</body></html>')
    d = OUT if zh else os.path.join(OUT, 'en')
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(out)

def build_resources(lang):
    zh = lang == 'zh'
    res = resources(lang)
    by = {}
    for r in res:
        by.setdefault(r['ch'], []).append(r)
    secs = []
    for n in sorted(by):
        lis = ''.join(f'<li><a href="{r["href"]}" target="_blank" rel="noopener"><span class="lab-kind">{r["kind"]}</span><b>{r["title"]}</b><span>{r["desc"]}</span></a></li>' for r in by[n])
        secs.append(f'<section class="res-ch"><h3><a href="ch{n:02d}.html">{T[lang]["ch"](n)} {chap_title(lang, n)}</a></h3><ul class="res-grid">{lis}</ul></section>')
    h = (f'<p class="eyebrow">互动资源</p><h2>动画与虚拟实验</h2><p class="muted">共 {len(res)} 个，按章排列。每一个也嵌在对应章节正文里，读到那里就能直接运行。</p>' if zh else
         f'<p class="eyebrow">Interactive resources</p><h2>Animations and virtual labs</h2><p class="muted">{len(res)} in all, listed by chapter. Each is also embedded in its chapter, so you can run it where you read about it.</p>')
    out = head(lang, (('互动资源 · ' if zh else 'Interactive resources · ') + TITLE[lang])) + bar(lang, 'res', 'resources.html') + \
        f'<main class="home"><section class="toc">{h}{"".join(secs)}</section></main>' + script(lang) + '</body></html>'
    d = OUT if zh else os.path.join(OUT, 'en')
    open(os.path.join(d, 'resources.html'), 'w').write(out)

def copy_labs(lang):
    d = os.path.join(OUT, 'labs') if lang == 'zh' else os.path.join(OUT, 'en', 'labs')
    os.makedirs(d, exist_ok=True)
    try:
        from inline import inline   # 本书若有共用库（src/lib/），构建时内联
    except ImportError:
        inline = lambda h: h
    for p in glob.glob(os.path.join(ROOT, 'src', lang, 'labs', '*.html')):
        with open(p, encoding='utf-8') as f:
            html = inline(f.read())
        with open(os.path.join(d, os.path.basename(p)), 'w', encoding='utf-8') as f:
            f.write(html)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        OUT = os.path.abspath(sys.argv[1])
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for lang in ('zh', 'en'):
        built = [n for n in sorted(CH) if build_chapter(lang, n)]
        print(lang, 'chapters:', built)
        if os.path.exists(os.path.join(ROOT, f'res_{lang}.json')):
            build_index(lang); build_resources(lang)
        copy_labs(lang)
    # 网页互动课件（第 24 轮）
    sys.path.insert(0, os.path.join(ROOT, 'course', 'tools'))
    import build_slides
    from pathlib import Path
    for y in sorted(glob.glob(os.path.join(ROOT, 'course', 'slides', 'ch*.yaml'))):
        lid = os.path.splitext(os.path.basename(y))[0]
        deck = build_slides.make_deck(lid, Path(OUT) / 'slides' / '_tmp')
        shutil.move(str(deck), os.path.join(OUT, 'slides', f'{lid}.html'))
    shutil.rmtree(os.path.join(OUT, 'slides', '_tmp'), ignore_errors=True)
    # new images
    for p in glob.glob(os.path.join(ROOT, 'img', '**', '*.webp'), recursive=True):
        rel = os.path.relpath(p, ROOT)
        os.makedirs(os.path.dirname(os.path.join(OUT, rel)), exist_ok=True)
        shutil.copy(p, os.path.join(OUT, rel))
    # what the learning platform's bookshelf reads (第 15 轮)
    json.dump({'title': TITLE['zh'], 'title_en': TITLE['en'], 'chapters': len(CH),
               'labs': len(resources('zh')), 'parts': len(PARTS)},
              open(os.path.join(OUT, 'book.json'), 'w'), ensure_ascii=False)
    print('built', OUT)
