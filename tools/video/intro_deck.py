"""首页视频简介的画面（第 86 轮）：讲稿.yaml 里每个镜头的 slide → 一份网页演示稿（中文 index.zh.html、英文 index.html），
make.py 的 page 镜头逐页录下来（独立视频，和 WenQuest Ops 介绍片同一条路）。

    python3 tools/video/intro_shots.py docs/课程视频/首页简介/17-评价与校情   # 先截真界面
    python3 tools/video/intro_deck.py  docs/课程视频/首页简介/17-评价与校情   # 再出演示稿

镜头写法：
  - id: s02
    kind: page
    page: 2                        # 与镜头顺序一致（程序检查）
    slide:
      layout: shot                 # shot（默认：左边大截图、右边要点）/ cover（封面）/ end（结尾）
      img: eval-stu                # 课件/media/<img>-<语言>.jpg
      kick: [学生端, Student]
      title: [每一步都留下证据, Every step leaves evidence]
      points:                      # 每条一个 “>”（steps 里 {show: …} 显示到第几条）
        - text: [诊断与练习, Diagnosis and practice]
          ring: [3, 20, 60, 10]    # 截图上圈出来的区域（百分比 x, y, 宽, 高），和这一条同时出现
          zoom: [1.35, 30, 25]     # 同时把截图放大到 1.35 倍，对准 (30%, 25%)
画面里的动作都由页面时钟（performance.now）驱动，录屏的虚拟时钟下也是平滑的。
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import yaml

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden;background:#07131f}
body{font-family:"Noto Sans CJK SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",Inter,Arial,sans-serif;color:#eaf1fb}
#stage{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0;overflow:hidden;
  background:radial-gradient(1200px 700px at 85% -10%,#1d3f7a 0%,transparent 60%),radial-gradient(900px 600px at -10% 110%,#0f4a4a 0%,transparent 60%),#07131f}
section.pg{position:absolute;inset:0;display:none}
section.pg.on{display:block}
.brand{position:absolute;left:56px;top:40px;font:600 24px/1 Inter,sans-serif;letter-spacing:.18em;color:#7fb6ff;text-transform:uppercase}
.brand b{color:#f5c344;font-weight:700;letter-spacing:.05em;margin-right:14px}
.kick{position:absolute;left:56px;top:84px;font-size:26px;color:#f5c344;font-weight:600;letter-spacing:.04em}
.title{position:absolute;left:56px;top:122px;width:1800px;font-size:52px;font-weight:800;line-height:1.15;color:#fff}
.win{position:absolute;left:56px;top:212px;width:1280px;height:720px;border-radius:14px;overflow:hidden;background:#fff;
  box-shadow:0 30px 80px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08)}
.win .bar{position:absolute;left:0;top:0;right:0;height:34px;background:#e9edf2;display:flex;align-items:center;gap:8px;padding-left:14px;z-index:3}
.win .bar i{width:12px;height:12px;border-radius:50%;background:#ff5f57}.win .bar i:nth-child(2){background:#febc2e}.win .bar i:nth-child(3){background:#28c840}
.win .bar span{margin-left:18px;font:500 15px/1 Inter,sans-serif;color:#5b6775;background:#fff;border-radius:6px;padding:5px 14px}
.win .vp{position:absolute;left:0;top:34px;right:0;bottom:0;overflow:hidden}
.win .vp .cam{position:absolute;inset:0;transform-origin:0 0}
.win .vp img{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:top left}
.ring{position:absolute;border:5px solid #f5c344;border-radius:12px;box-shadow:0 0 0 9999px rgba(7,19,31,.16),0 0 24px rgba(245,195,68,.8);opacity:0}
.side{position:absolute;left:1384px;top:236px;width:480px}
.side li{list-style:none;position:relative;padding:0 0 0 46px;margin:0 0 30px;font-size:31px;line-height:1.38;color:#dbe7f7;opacity:0}
.side li::before{content:attr(data-n);position:absolute;left:0;top:4px;width:32px;height:32px;border-radius:50%;background:#f5c344;color:#07131f;
  font:700 19px/32px Inter,sans-serif;text-align:center}
.side li b{color:#fff}
.cover .title{top:330px;font-size:78px;width:900px}
.cover .sub{position:absolute;left:56px;top:600px;width:860px;font-size:36px;line-height:1.45;color:#bcd0ea}
.cover .line{position:absolute;left:56px;top:300px;width:120px;height:6px;background:#f5c344;border-radius:3px}
.cover .win{left:1010px;top:200px;width:1000px;height:597px;transform:perspective(1800px) rotateY(-16deg) rotateX(3deg);transform-origin:left center;opacity:.92}
.end .title{top:300px;font-size:84px;width:1700px}
.end .sub{position:absolute;left:56px;top:430px;font-size:40px;color:#bcd0ea}
.end .url{position:absolute;left:56px;top:540px;font:600 44px/1.2 Inter,sans-serif;color:#f5c344}
.end .win{left:1180px;top:260px;width:680px;height:416px;opacity:.85}
.f{opacity:0}
"""

JS = r"""
(() => {
  const pages = [...document.querySelectorAll('section.pg')]
  let cur = 0, frag = 0, t0 = performance.now()
  const frags = (i) => [...pages[i].querySelectorAll('[data-k]')].reduce((m, e) => Math.max(m, +e.dataset.k), 0)
  function go(i, s) { pages.forEach((p, k) => p.classList.toggle('on', k === i)); cur = i; frag = 0; t0 = performance.now()
    pages[i].querySelectorAll('[data-k]').forEach((e) => { e.dataset.t = '' }); while (frag < s) next() }
  function next() { if (frag >= frags(cur)) { if (cur < pages.length - 1) go(cur + 1, 0); return } frag++
    pages[cur].querySelectorAll(`[data-k="${frag}"]`).forEach((e) => { e.dataset.t = performance.now() })
    const z = pages[cur].querySelector(`.cam[data-z${frag}]`); if (z) { z.dataset.from = z.dataset.now || '1,0,0'; z.dataset.to = z.dataset['z' + frag]; z.dataset.zt = performance.now() } }
  const ease = (x) => x < 0 ? 0 : x > 1 ? 1 : x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2
  function tick() {
    const now = performance.now(), p = pages[cur]; if (!p) return
    p.querySelectorAll('[data-k]').forEach((e) => { const t = +e.dataset.t; const a = e.dataset.t ? ease((now - t) / 450) : 0
      e.style.opacity = a; if (e.tagName === 'LI') e.style.transform = `translateX(${(1 - a) * 24}px)` })
    p.querySelectorAll('.cam').forEach((c) => {
      const drift = 1 + 0.035 * Math.min(1, (now - t0) / 14000)          // 缓慢推近，画面不死
      let [s, x, y] = (c.dataset.now || '1,0,0').split(',').map(Number)
      if (c.dataset.to) { const a = ease((now - +c.dataset.zt) / 1200), A = c.dataset.from.split(',').map(Number), B = c.dataset.to.split(',').map(Number)
        ;[s, x, y] = A.map((v, k) => v + (B[k] - v) * a); if (a >= 1) { c.dataset.now = c.dataset.to; delete c.dataset.to } }
      const W = c.clientWidth, H = c.clientHeight, S = s * drift
      // 把 (x%, y%) 放到画面中心，且不露出边
      const tx = Math.min(0, Math.max(W - W * S, W / 2 - W * S * x / 100)), ty = Math.min(0, Math.max(H - H * S, H / 2 - H * S * y / 100))
      c.style.transform = `translate(${s === 1 && !x ? 0 : tx}px,${s === 1 && !y ? 0 : ty}px) scale(${S})`
    })
  }
  setInterval(tick, 16)
  function fit() { const k = Math.min(innerWidth / 1920, innerHeight / 1080); document.getElementById('stage').style.transform = `scale(${k})` }
  addEventListener('resize', fit); fit()
  addEventListener('keydown', (e) => { if (['ArrowRight', ' ', 'PageDown'].includes(e.key)) next(); if (e.key === 'ArrowLeft') go(Math.max(0, cur - 1), 0) })
  const h = +(location.hash.match(/#p(\d+)/) || [])[1]; go(h ? h - 1 : 0, 0)
  window.__deck = { pages: pages.length, go: (i, s) => go(i, s ?? 0), next, fragments: frags,
    notes: (i) => '', state: () => ({ page: cur, frag }) }
})()
"""


def T(v, lang):
    if isinstance(v, list):
        return v[0] if lang == "zh" or len(v) < 2 else v[1]
    return v or ""


def esc(s):
    return html.escape(str(s)).replace("**", "")


def page(shot, lang, n, brand):
    s = shot.get("slide") or {}
    lay = s.get("layout", "shot")
    img = s.get("img")
    url = T(s.get("url", ""), lang)
    parts = [f'<section class="pg {lay}" data-n="{n}">', f'<div class="brand"><b>问渠</b>{esc(brand)}</div>']
    if s.get("kick") and lay == "shot":
        parts.append(f'<div class="kick">{esc(T(s["kick"], lang))}</div>')
    parts.append(f'<div class="title">{esc(T(s.get("title"), lang))}</div>')
    if lay == "cover":
        parts.append('<div class="line"></div>')
    if s.get("sub"):
        parts.append(f'<div class="sub">{esc(T(s["sub"], lang))}</div>')
    if lay == "end" and s.get("link"):
        parts.append(f'<div class="url">{esc(T(s["link"], lang))}</div>')
    pts = s.get("points") or []
    if img:
        zs, rings = [], []
        for k, p in enumerate(pts, 1):
            if p.get("zoom"):
                zs.append(f' data-z{k}="{",".join(str(x) for x in p["zoom"])}"')
            if p.get("ring"):
                x, y, w, h = p["ring"]
                rings.append(f'<div class="ring" data-k="{k}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%"></div>')
        parts.append(f'<div class="win"><div class="bar"><i></i><i></i><i></i><span>{esc(url)}</span></div><div class="vp">'
                     f'<div class="cam"{"".join(zs)}><img src="media/{img}-{lang}.jpg" alt="">{"".join(rings)}</div></div></div>')
    if pts and lay == "shot":
        parts.append('<ul class="side">' + "".join(f'<li data-k="{k}" data-n="{k}">{esc(T(p["text"], lang))}</li>' for k, p in enumerate(pts, 1)) + "</ul>")
    parts.append("</section>")
    return "\n".join(parts)


def build(d: str):
    lec = Path(d)
    spec = yaml.safe_load((lec / "讲稿.yaml").read_text(encoding="utf-8"))
    shots = spec["shots"]
    for i, sh in enumerate(shots, 1):
        if int(sh.get("page", 0)) != i:
            raise SystemExit(f"{sh.get('id')}: page 应为 {i}")
        npts = len((sh.get("slide") or {}).get("points") or [])
        for lang in ("zh", "en"):
            gt = sum(1 for x in (sh.get("say") or {}).get(lang, []) if str(x).startswith(">"))
            if gt != len(sh.get("steps") or []):
                raise SystemExit(f"{sh['id']} {lang}: “>” {gt} 个，steps {len(sh.get('steps') or [])} 个")
        for st in sh.get("steps") or []:
            if "show" in st and npts == 0 and st["show"] not in (0, 1):
                raise SystemExit(f"{sh['id']}: 没有要点，show 只能是 0 或 1")
    out = lec / "课件"
    out.mkdir(exist_ok=True)
    for lang, name in (("zh", "index.zh.html"), ("en", "index.html")):
        brand = T(spec.get("brand", ["WenQuest", "WenQuest"]), lang)
        body = "\n".join(page(sh, lang, i, brand) for i, sh in enumerate(shots, 1))
        title = esc(T(spec["title"], lang))
        doc = (f'<!doctype html><html lang="{"zh-CN" if lang == "zh" else "en"}"><head><meta charset="utf-8">'
               f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{CSS}</style></head>'
               f'<body><div id="stage">{body}</div><script>{JS}</script></body></html>')
        (out / name).write_text(doc, encoding="utf-8")
        missing = [f"media/{(sh.get('slide') or {}).get('img')}-{lang}.jpg" for sh in shots
                   if (sh.get("slide") or {}).get("img") and not (out / "media" / f"{sh['slide']['img']}-{lang}.jpg").exists()]
        if missing:
            raise SystemExit("缺截图：" + "、".join(missing))
        print(out / name)


if __name__ == "__main__":
    build(sys.argv[1])
