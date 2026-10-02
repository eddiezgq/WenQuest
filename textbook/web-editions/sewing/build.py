# -*- coding: utf-8 -*-
"""Assemble the web book (zh at root, en under en/) from chapter fragments in src/<lang>/chNN.html."""
import re, os, json, html, shutil, glob
from book import PARTS, CH, TITLE, part_of, NEW

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out')   # overridden by the command-line argument (CI: textbook/build/sewing/webed)
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
        s = s.replace("'针距'", "'stitch length'").replace("'布面'", "'fabric top'").replace("'布底'", "'fabric bottom'")
        s = s.replace("'第 ' + (cyc + 1) + ' 针'", "'stitch ' + (cyc + 1)")
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
    # images are stored as WebP in the repository
    fr = re.sub(r'((?:src|href)="(?:\.\./)?img/[^"]+)\.png"', r'\1.webp"', fr)
    # side nav from h3 ids
    items = re.findall(r'<h3 id="([^"]+)">(.*?)</h3>', fr, flags=re.S)
    side = ''.join(f'<li><a href="#{i}">{re.sub("<[^>]+>", "", t)}</a></li>' for i, t in items)
    order = sorted(CH)
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
    if zh:
        cover = (f'<section class="cover"><div class="cover-text"><p class="eyebrow">高等学校教材 · 网页版</p><h1>缝纫机<br>设计与制造</h1>'
                 '<p class="lede">从一针线迹到一座服装工厂：机构怎样设计，电控怎样实现，原型机怎样搭起来、测出来、迭代成工业级产品，零件怎样制造，工厂怎样用数字系统组织起来。每一章都配有可以动手的动画、虚拟实验和三维模型。</p>'
                 f'<div class="stats"><div><b>{nready}</b><span>章已可读</span></div><div><b>{len(CH)}</b><span>章计划</span></div><div><b>{len(res)}</b><span>个动画、实验与模型</span></div></div>'
                 '<div class="cta"><a class="btn" href="ch01.html">从第 1 章开始读</a><a class="btn ghost" href="ch19.html">新增：电控原型机</a><a class="btn ghost" href="resources.html">浏览互动资源</a></div></div>'
                 '<figure class="cover-art"><canvas id="seamCanvas" width="560" height="360" aria-label="301 锁式线迹示意动画"></canvas><figcaption>301 锁式线迹：针线（蓝）与底线（橙）在布层中间交织</figcaption></figure></section>')
        tochead = f'<h2>全书目录</h2><p class="muted">八篇三十一章。标 NEW 的是本版新增的章节：第六篇讲怎样依照本书原理搭出平缝机、包缝机、花样机和横机的电控原型并自动化测试，第七篇补充机针、旋梭、机壳、凸轮的制造工艺和数字工厂整体方案。</p>'
        foot = '<p class="foot">本网页版由书稿自动生成，与书稿同步更新。书中数值标“算例值”的为教学算例，标“待核”的待企业资料核对。</p>'
    else:
        cover = (f'<section class="cover"><div class="cover-text"><p class="eyebrow">University textbook · web edition</p><h1>Sewing Machine<br>Design and Manufacturing</h1>'
                 '<p class="lede">From a single stitch to a whole garment factory: how the mechanisms are designed, how the controls work, how a control prototype is built, tested and iterated into an industrial product, how the parts are made, and how a factory is run on digital systems. Every chapter comes with animations, virtual labs and 3D models you can try.</p>'
                 f'<div class="stats"><div><b>{nready}</b><span>chapters ready</span></div><div><b>{len(CH)}</b><span>chapters planned</span></div><div><b>{len(res)}</b><span>animations, labs and models</span></div></div>'
                 '<div class="cta"><a class="btn" href="ch01.html">Start with Chapter 1</a><a class="btn ghost" href="ch19.html">New: control prototypes</a><a class="btn ghost" href="resources.html">Browse resources</a></div></div>'
                 '<figure class="cover-art"><canvas id="seamCanvas" width="560" height="360" aria-label="Animation of lockstitch 301"></canvas><figcaption>Lockstitch 301: needle thread (blue) and bobbin thread (orange) interlace inside the fabric plies</figcaption></figure></section>')
        tochead = '<h2>Contents</h2><p class="muted">Eight parts, thirty-one chapters. Chapters marked NEW were added in this edition: Part VI shows how to build and automatically test control prototypes of a lockstitch machine, an overlocker, a pattern sewer and a flat-knitting machine from the principles in this book; Part VII adds manufacturing processes for needles, hooks, housings and cams, and an integrated digital-factory solution.</p>'
        foot = '<p class="foot">This web edition is generated from the manuscript and updated with it. Figures marked “worked-example value” are teaching values; those marked “to be verified” await checking against manufacturers’ data.</p>'
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
    h = (f'<p class="eyebrow">互动资源</p><h2>动画、虚拟实验与三维模型</h2><p class="muted">共 {len(res)} 个，按章排列。每一个也嵌在对应章节正文里，读到那里就能直接运行。</p>' if zh else
         f'<p class="eyebrow">Interactive resources</p><h2>Animations, virtual labs and 3D models</h2><p class="muted">{len(res)} in all, listed by chapter. Each is also embedded in its chapter, so you can run it where you read about it.</p>')
    out = head(lang, (('互动资源 · ' if zh else 'Interactive resources · ') + TITLE[lang])) + bar(lang, 'res', 'resources.html') + \
        f'<main class="home"><section class="toc">{h}{"".join(secs)}</section></main>' + script(lang) + '</body></html>'
    d = OUT if zh else os.path.join(OUT, 'en')
    open(os.path.join(d, 'resources.html'), 'w').write(out)

def copy_labs(lang):
    d = os.path.join(OUT, 'labs') if lang == 'zh' else os.path.join(OUT, 'en', 'labs')
    os.makedirs(d, exist_ok=True)
    for p in glob.glob(os.path.join(ROOT, 'src', lang, 'labs', '*.html')):
        shutil.copy(p, d)

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
