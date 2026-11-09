"""首页视频的网页版 PPT（第 127 轮）：讲道理的镜头用网页直接画（矢量，任何放大都清楚），不用截图。

    python3 tools/video/intro_ppt.py docs/课程视频/首页简介/18-电子与芯片

读 <讲稿目录>/课件/ppt.html（只写各页的 <section class="pg">，样式见 ../样页/样页.html），套上统一的样式和翻页程序，
写出 课件/index.zh.html（中文为主、英文小字）和 课件/index.html（英文版）。make.py 的 page 镜头逐页录（1920×1080）。

页里的写法：
  <section class="pg">…</section>          一页；顺序就是 page 页号
  data-k="1"                                第 1 个 “>” 出现（steps 里 {show: …} 显示到第几个；data-k 从 1 起）
  data-d="600"                              同一步里再晚 600 毫秒出现（一句话里依次出现几样东西）
  data-a="draw"                             SVG 线条“画出来”（默认是淡入并上移一点）；data-a="pop" 放大出现
  class="sub"                               中文版里的英文小字（英文版不显示）
  data-en="…"                               英文版里把这段文字换成英文（标题、卡片名、图上的字）
  class="zh-only" / class="en-only"         只在中文版 / 英文版出现
  class="flow"                              SVG 箭头上的虚线一直往前走（数据在流动）
画面里的动作都由页面时钟（performance.now）驱动，录屏的虚拟时钟下也是平滑的。
"""
from __future__ import annotations

import sys
from pathlib import Path

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden;background:#07131f}
body{font-family:"Noto Sans CJK SC","Source Han Sans SC","PingFang SC",Inter,Arial,sans-serif;color:#eaf1fb}
#stage{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0;overflow:hidden;
  background:radial-gradient(1200px 700px at 85% -10%,#1d3f7a 0%,transparent 60%),radial-gradient(900px 600px at -10% 110%,#0f4a4a 0%,transparent 60%),#07131f}
section.pg{position:absolute;inset:0;display:none}
section.pg.on{display:block}
.brand{position:absolute;left:56px;top:40px;font:600 24px/1 Inter,"Noto Sans CJK SC",sans-serif;letter-spacing:.18em;color:#7fb6ff}
.brand b{color:#f5c344;letter-spacing:.05em;margin-right:14px}
.kick{position:absolute;left:56px;top:84px;font-size:26px;color:#f5c344;font-weight:600}
.title{position:absolute;left:56px;top:122px;width:1800px;font-size:56px;font-weight:800;line-height:1.2;color:#fff}
.sub{font:500 34px/1.3 Inter,"Noto Sans CJK SC",sans-serif;color:#8fb3dd;display:block;margin-top:6px}
svg text{font-family:"Noto Sans CJK SC",Inter,sans-serif}
.code{position:absolute;border-radius:16px;background:#0b1d30;border:1px solid #23415f;padding:26px 28px;
  font:500 21px/1.6 "JetBrains Mono","DejaVu Sans Mono",monospace;color:#cfe2ff;white-space:pre;overflow:hidden}
.code .k{color:#f5c344}.code .c{color:#6f8db0}.code .n{color:#7fe0c0}
.cap{position:absolute;font-size:30px;font-weight:700;color:#fff}.cap .sub{font-size:21px;margin-top:4px}
.tag{position:absolute;left:56px;bottom:118px;font-size:30px;color:#bcd0ea}.tag b{color:#f5c344}
.card{position:absolute;border-radius:22px;background:linear-gradient(#14304f,#0c2038);border:2px solid #2f5d8a}
.card.hot{border:3px solid #f5c344}
.big{position:absolute;font-size:84px;font-weight:800;color:#fff;line-height:1.15}
.url{position:absolute;font:600 46px/1.2 Inter,"Noto Sans CJK SC",sans-serif;color:#f5c344}
html[lang=en] .sub,html[lang=en] .zh-only{display:none!important}
html[lang=zh-CN] .en-only{display:none!important}
html[lang=en] .title{font-family:Inter,"Noto Sans CJK SC",sans-serif}
"""

JS = r"""
(() => {
  const en = document.documentElement.lang === 'en'
  if (en) document.querySelectorAll('[data-en]').forEach((e) => { e.textContent = e.dataset.en })
  const pages = [...document.querySelectorAll('section.pg')]
  let cur = 0, frag = 0
  const frags = (i) => [...pages[i].querySelectorAll('[data-k]')].reduce((m, e) => Math.max(m, +e.dataset.k), 0)
  const prep = (p) => p.querySelectorAll('[data-a="draw"]').forEach((e) => {
    if (e.dataset.len) return
    const L = e.getTotalLength ? e.getTotalLength() : 1000
    e.dataset.len = L; e.style.strokeDasharray = L + ' ' + L
  })
  function go(i, s) { pages.forEach((p, k) => p.classList.toggle('on', k === i)); cur = i; frag = 0; prep(pages[i])
    pages[i].querySelectorAll('[data-k]').forEach((e) => { e.dataset.t = '' }); while (frag < s) next() }
  function next() { if (frag >= frags(cur)) { if (cur < pages.length - 1) go(cur + 1, 0); return } frag++
    const now = performance.now()
    pages[cur].querySelectorAll(`[data-k="${frag}"]`).forEach((e) => { e.dataset.t = now + (+e.dataset.d || 0) }) }
  const ease = (x) => x < 0 ? 0 : x > 1 ? 1 : 1 - Math.pow(1 - x, 3)
  function tick() {
    const now = performance.now(), p = pages[cur]; if (!p) return
    p.querySelectorAll('[data-k]').forEach((e) => {
      const a = e.dataset.t ? ease((now - +e.dataset.t) / 600) : 0, kind = e.dataset.a
      if (kind === 'draw') { e.style.strokeDashoffset = (+e.dataset.len) * (1 - ease((now - +e.dataset.t) / 900) * (e.dataset.t ? 1 : 0)); e.style.opacity = e.dataset.t && now >= +e.dataset.t ? 1 : 0; return }
      e.style.opacity = a
      // 用 CSS 的 translate / scale 属性（不碰 transform）：SVG 分组自己的 transform 属性不被覆盖
      if (e instanceof SVGElement) { e.style.transformBox = 'fill-box'; e.style.transformOrigin = 'center' }
      if (kind === 'pop') e.style.scale = 0.85 + 0.15 * a; else e.style.translate = `0 ${(1 - a) * 18}px`
    })
    p.querySelectorAll('.flow').forEach((e) => { e.style.strokeDashoffset = -((now / 40) % 1000) })
  }
  setInterval(tick, 16)
  function fit() { const k = Math.min(innerWidth / 1920, innerHeight / 1080); document.getElementById('stage').style.transform = `scale(${k})` }
  addEventListener('resize', fit); fit()
  addEventListener('keydown', (e) => { if (['ArrowRight', ' ', 'PageDown'].includes(e.key)) next(); if (e.key === 'ArrowLeft') go(Math.max(0, cur - 1), 0) })
  const h = +(location.hash.match(/#p(\d+)/) || [])[1]; go(h ? h - 1 : 0, 0)
  window.__deck = { pages: pages.length, go: (i, s) => go(i, s ?? 0), next, fragments: frags, notes: () => '', state: () => ({ page: cur, frag }) }
})()
"""


def build(d: str):
    lec = Path(d)
    src = (lec / "课件" / "ppt.html").read_text(encoding="utf-8")
    title = lec.name
    for lang, name in (("zh-CN", "index.zh.html"), ("en", "index.html")):
        doc = (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
               f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{CSS}</style></head>'
               f'<body><div id="stage">{src}</div><script>{JS}</script></body></html>')
        (lec / "课件" / name).write_text(doc, encoding="utf-8")
        print(lec / "课件" / name)


if __name__ == "__main__":
    build(sys.argv[1])
