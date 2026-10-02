# -*- coding: utf-8 -*-
"""第 24 章结构图/流程图：生成 figsrc/ch24_<name>.zh.html / .en.html，再用 fig.js 渲染。
运行：python3 figsrc/ch24_htmlfigs.py && （脚本末尾打印渲染命令）"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">\n<style>{css}</style>\n'
ARROW = '<svg width="26" height="20" viewBox="0 0 26 20"><path d="M2 10H20" stroke="#5a6570" stroke-width="2"/><path d="M16 4L23 10L16 16" fill="none" stroke="#5a6570" stroke-width="2"/></svg>'
DOWN = '<svg width="20" height="22" viewBox="0 0 20 22"><path d="M10 2V16" stroke="#5a6570" stroke-width="2"/><path d="M4 12L10 19L16 12" fill="none" stroke="#5a6570" stroke-width="2"/></svg>'

FLOWCSS = """
.flow{display:grid;grid-template-columns:repeat(7,auto);align-items:center;justify-content:start;gap:8px 4px}
.flow .box{width:205px;min-height:96px;text-align:left;padding:8px 10px}
.flow .box b{font-size:14.5px}.flow .box span{font-size:12px;line-height:1.45}
.box span.n,.n{display:inline-block;width:20px;height:20px;border-radius:50%;background:#1b2430;color:#fff;font-size:12px;text-align:center;line-height:20px;margin-right:6px;font-weight:700}
.turn{grid-column:1/-1;display:flex;justify-content:flex-end;padding-right:96px;height:22px}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px;font-size:12.5px;color:#5a6570}
.legend i{display:inline-block;width:14px;height:14px;border:2px solid;border-radius:4px;vertical-align:-2px;margin-right:5px}
.ctq{margin-top:14px;font-size:12.5px}
.ctq td{padding:4px 10px}
.lane{display:flex;align-items:center;gap:4px;margin-bottom:10px}
.lane .tag{width:86px;font-weight:700;font-size:14px}
"""


def flow_rows(steps, per_row=4):
    """蛇形排列：奇数行从左到右，偶数行从右到左，行尾用向下箭头接到下一行。"""
    LEFT = '<div style="transform:scaleX(-1)">' + ARROW + '</div>'
    rows = [steps[i:i + per_row] for i in range(0, len(steps), per_row)]
    out = []
    k = 0
    for r, row in enumerate(rows):
        cells = []
        for j, (cls, t, note) in enumerate(row):
            k += 1
            cells.append(f'<div class="box {cls}"><b><span class="n">{k}</span>{t}</b><span>{note}</span></div>')
        seq = []
        for j, c in enumerate(cells):
            if j:
                seq.append('<div>' + (ARROW if r % 2 == 0 else LEFT) + '</div>')
            seq.append(c)
        if r % 2:
            seq = seq[::-1]
        out += seq
        if r < len(rows) - 1:
            side = 'flex-end;padding-right:96px' if r % 2 == 0 else 'flex-start;padding-left:96px'
            out.append(f'<div class="turn" style="justify-content:{side}">' + DOWN + '</div>')
    return '<div class="flow">' + ''.join(out) + '</div>'


# ------------------------------------------------------------------ 图 24-x 机针工艺流程
NEEDLE = {
 'zh': dict(title='机针的制造工艺流程', sub='示意：12 道主要工序；不同厂家的顺序和合并方式可以不同，数值以企业工艺文件为准',
  steps=[('k fill-k', '线材进厂', '高碳钢丝，直径约等于针柄直径；查直径、表面、脱碳层'),
         ('b fill-b', '校直与定长切断', '矫直轮校直，切成针坯；坯长 = 针长 + 余量'),
         ('b fill-b', '针身减径', '旋锻或无心磨把针身减细、做出锥形过渡；针柄倒角'),
         ('b fill-b', '冲长槽、短槽与凹口', '模具冷压成形；槽深、凹口位置决定梭尖间隙'),
         ('o fill-o', '压扁与冲针孔', '先两侧压出针孔区，再冲穿；最易出毛刺的关键工序'),
         ('o fill-o', '磨针尖', '成形砂轮磨出尖头、圆头或切割刃；控制烧伤'),
         ('y fill-y', '淬火', '保护气氛加热后油淬；针身获得高硬度'),
         ('y fill-y', '回火', '降低脆性，在硬度与韧性之间取平衡'),
         ('b fill-b', '校直', '热处理后变形，逐支校直到直度要求'),
         ('p fill-p', '滚光 / 电解抛光', '去毛刺，使针孔、长槽、针尖圆滑光洁'),
         ('p fill-p', '镀层', '镀镍、镀铬，或钛氮化物等耐磨涂层'),
         ('g fill-g', '检测与包装', '自动光学检测全检外形，抽检硬度、直度；装盒')],
  legend=[('#1b2430', '原材料'), ('#2a6fdb', '成形与校直'), ('#e0662f', '针孔与针尖（关键）'), ('#c48a17', '热处理'), ('#8a5cc7', '表面处理'), ('#2e9e5b', '检测')],
  ctq_h=('关键质量特性', '主要在哪几道工序形成'),
  ctq=[('直度', '③ 减径、⑦ 淬火变形、⑨ 校直'), ('针孔光洁、无毛刺', '⑤ 冲针孔、⑩ 抛光、⑪ 镀层'), ('针尖形状', '⑥ 磨针尖、⑩ 抛光（不可磨圆过度）'),
       ('凹口位置与深度', '④ 冲凹口（影响梭尖间隙，第 5、23 章）'), ('硬度与韧性', '⑦ 淬火、⑧ 回火')]),
 'en': dict(title='Manufacturing process for sewing-machine needles', sub='Illustrative: 12 main operations; sequence and grouping vary between makers; values come from the plant\'s process sheets',
  steps=[('k fill-k', 'Incoming wire', 'High-carbon steel wire, about shank diameter; check diameter, surface, decarburisation'),
         ('b fill-b', 'Straighten and cut off', 'Roller straightening, cut into blanks; blank = needle length + allowance'),
         ('b fill-b', 'Blade reducing', 'Rotary swaging or centreless grinding thins the blade and forms the taper; shank chamfer'),
         ('b fill-b', 'Press long groove, short groove and scarf', 'Cold pressing in dies; groove depth and scarf position set the hook clearance'),
         ('o fill-o', 'Flatten and punch the eye', 'Eye area pressed from both sides, then punched through; the burr-prone key step'),
         ('o fill-o', 'Point grinding', 'Form wheel grinds a sharp, ball or cutting point; avoid grinding burn'),
         ('y fill-y', 'Quenching', 'Heated in protective atmosphere, oil-quenched; blade becomes hard'),
         ('y fill-y', 'Tempering', 'Reduces brittleness; balances hardness against toughness'),
         ('b fill-b', 'Straightening', 'Heat treatment distorts; each needle is straightened to spec'),
         ('p fill-p', 'Tumbling / electropolishing', 'Removes burrs; eye, groove and point become smooth'),
         ('p fill-p', 'Plating / coating', 'Nickel or chrome plating, or wear-resistant coatings such as titanium nitride'),
         ('g fill-g', 'Inspection and packing', 'Automatic optical inspection of every needle; sampled hardness and straightness; boxing')],
  legend=[('#1b2430', 'Raw material'), ('#2a6fdb', 'Forming and straightening'), ('#e0662f', 'Eye and point (critical)'), ('#c48a17', 'Heat treatment'), ('#8a5cc7', 'Surface finishing'), ('#2e9e5b', 'Inspection')],
  ctq_h=('Critical characteristic', 'Formed mainly in operations'),
  ctq=[('Straightness', '③ blade reducing, ⑦ quench distortion, ⑨ straightening'), ('Smooth, burr-free eye', '⑤ eye punching, ⑩ polishing, ⑪ plating'), ('Point shape', '⑥ point grinding, ⑩ polishing (must not over-round)'),
       ('Scarf position and depth', '④ scarf pressing (affects hook clearance, Chapters 5 and 23)'), ('Hardness and toughness', '⑦ quenching, ⑧ tempering')]),
}


def needleflow(L):
    leg = ''.join(f'<span><i style="border-color:{c}"></i>{t}</span>' for c, t in L['legend'])
    ctq = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in L['ctq'])
    return (HEAD.format(css=FLOWCSS) + f'<div class="fig" style="--w:1010px"><p class="title">{L["title"]}</p><p class="sub">{L["sub"]}</p>'
            + flow_rows(L['steps']) + f'<div class="legend">{leg}</div>'
            + f'<table class="ctq"><thead><tr><th>{L["ctq_h"][0]}</th><th>{L["ctq_h"][1]}</th></tr></thead><tbody>{ctq}</tbody></table></div>')


# ------------------------------------------------------------------ 旋梭工艺流程（两条线汇合）
HOOK = {
 'zh': dict(title='旋梭的制造工艺流程', sub='示意：旋梭体与梭床两条线分别加工，在选配站汇合；材料与热处理为常见做法的示意，以企业图纸为准',
  body='旋梭体', basket='梭床', asm='组件',
  b=[('k fill-k', '锻坯或棒料', '合金钢锻坯（示意）；查硬度、折叠'), ('b fill-b', '车削', '内外圆、端面、梭道粗形；留磨量'),
     ('b fill-b', '多轴铣削', '梭尖、梭尖背面与梭道轮廓；一次装夹'), ('y fill-y', '渗碳淬火', '或整体淬火；表面高硬度、心部有韧性'),
     ('o fill-o', '梭道精磨', '梭道直径与圆度；按尺寸分组'), ('o fill-o', '梭尖研磨抛光', '刃口圆滑、无毛刺；手工或机器')],
  k=[('k fill-k', '棒料', '轴承钢等（示意）'), ('b fill-b', '车削', '中心柱、外缘导轨粗形'), ('b fill-b', '铣削', '定位凹槽、线道'),
     ('y fill-y', '整体淬火', '或渗碳淬火'), ('o fill-o', '导轨精磨', '导轨外径；按尺寸分组'), ('p fill-p', '表面处理', 'DLC 等（可选）')],
  a=[('g fill-g', '测量分组与选配', '同组旋梭体与梭床配对'), ('g fill-g', '装配', '压板、螺钉；转动灵活'),
     ('g fill-g', '跑合与噪声检测', '规定转速下运转，测噪声、温升'), ('g fill-g', '出厂检验', '间隙、外观、梭尖；记录批号')]),
 'en': dict(title='Manufacturing process for rotary hooks', sub='Illustrative: hook body and basket are made on two lines and meet at the fitting station; materials and heat treatment are typical practice, the drawing governs',
  body='Hook body', basket='Basket', asm='Assembly',
  b=[('k fill-k', 'Forging or bar', 'Alloy-steel forging (illustrative); check hardness, laps'), ('b fill-b', 'Turning', 'Bores, faces, rough race; leave grinding stock'),
     ('b fill-b', 'Multi-axis milling', 'Hook point, its back and the race contour in one setup'), ('y fill-y', 'Carburising', 'or through hardening; hard case, tough core'),
     ('o fill-o', 'Race grinding', 'Race diameter and roundness; graded by size'), ('o fill-o', 'Point lapping', 'Edge rounded and burr-free; by hand or machine')],
  k=[('k fill-k', 'Bar stock', 'Bearing steel etc. (illustrative)'), ('b fill-b', 'Turning', 'Centre post, rough rib'), ('b fill-b', 'Milling', 'Positioning notch, thread path'),
     ('y fill-y', 'Through hardening', 'or carburising'), ('o fill-o', 'Rib grinding', 'Rib outside diameter; graded by size'), ('p fill-p', 'Surface treatment', 'DLC etc. (optional)')],
  a=[('g fill-g', 'Grade and match', 'Hook body and basket of the same group'), ('g fill-g', 'Assembly', 'Gib, screws; free rotation'),
     ('g fill-g', 'Running-in and noise test', 'Run at set speed; measure noise and temperature rise'), ('g fill-g', 'Final inspection', 'Clearance, appearance, point; record lot')]),
}
HOOKCSS = FLOWCSS + """
.lane .box{width:132px;min-height:92px;text-align:left;padding:7px 8px}
.lane .box b{font-size:13.5px}.lane .box span{font-size:11.5px;line-height:1.4}
.merge{display:flex;align-items:center;gap:4px;margin-top:4px}
.bracket{width:86px}
"""


def hookflow(L):
    def lane(tag, steps, last_arrow=True):
        cells = []
        for i, (cls, t, n) in enumerate(steps):
            if i:
                cells.append(ARROW)
            cells.append(f'<div class="box {cls}"><b>{t}</b><span>{n}</span></div>')
        return f'<div class="lane"><div class="tag">{tag}</div>' + ''.join(cells) + '</div>'
    merge_svg = ('<svg width="1000" height="40" viewBox="0 0 1000 40" style="display:block;margin:-4px 0 2px">'
                 '<path d="M970 0V14H180V34" fill="none" stroke="#5a6570" stroke-width="2"/>'
                 '<path d="M174 28L180 37L186 28" fill="none" stroke="#5a6570" stroke-width="2"/></svg>')
    a_cells = []
    for i, (cls, t, n) in enumerate(L['a']):
        if i:
            a_cells.append(ARROW)
        a_cells.append(f'<div class="box {cls}" style="width:190px;min-height:70px;text-align:left"><b>{t}</b><span>{n}</span></div>')
    return (HEAD.format(css=HOOKCSS) + f'<div class="fig" style="--w:1060px"><p class="title">{L["title"]}</p><p class="sub">{L["sub"]}</p>'
            + lane(L['body'], L['b']) + lane(L['basket'], L['k']) + merge_svg
            + f'<div class="lane"><div class="tag">{L["asm"]}</div>' + ''.join(a_cells) + '</div></div>')


# ------------------------------------------------------------------ 针号与针尖形状
POINTS = {
 'zh': dict(title='针号、针身刚度与针尖形状', sub='左：针身截面按比例画出，刚度（抗弯、抗失稳）按 d⁴ 相对 Nm 90 计算；右：几种常见针尖的侧视与正视（示意）',
  nm='针号', d='直径', st='相对刚度',
  pts=[('尖头', '普通梭织物，刺穿纤维'), ('轻圆头', '细密针织物，推开纱线'), ('中圆头', '粗针织、弹性织物'), ('切割尖', '皮革，刃口切开')],
  side='侧视', front='针尖正视'),
 'en': dict(title='Needle size, blade stiffness and point shapes', sub='Left: blade cross-sections to scale; stiffness (bending and buckling) scales as d⁴, relative to Nm 90. Right: side and end views of common points (illustrative)',
  nm='Size', d='Diameter', st='Relative stiffness',
  pts=[('Sharp point', 'woven fabrics; pierces fibres'), ('Light ball point', 'fine knits; pushes yarns aside'), ('Medium ball point', 'coarse knits, elastic fabrics'), ('Cutting point', 'leather; the edge cuts')],
  side='side', front='end view'),
}


def points(L):
    sizes = [60, 70, 80, 90, 110, 130]
    sc = 70  # px per mm
    cells = []
    for nm in sizes:
        d = nm / 100
        r = d * sc / 2
        cells.append(f'<g transform="translate({{x}},0)"><circle cx="0" cy="70" r="{r:.1f}" fill="#e9f0fc" stroke="#2a5fb8" stroke-width="2"/>'
                     f'<text x="0" y="140" text-anchor="middle" font-size="14" font-weight="700">Nm {nm}</text>'
                     f'<text x="0" y="158" text-anchor="middle" font-size="12" fill="#5a6570">{d:.2f} mm</text>'
                     f'<text x="0" y="176" text-anchor="middle" font-size="12" fill="#c4531d">{(d/0.9)**4:.2f}×</text></g>')
    left = ''.join(c.replace('{x}', str(40 + i * 92)) for i, c in enumerate(cells))
    left = (f'<svg width="530" height="200" viewBox="0 0 530 200">{left}'
            f'<text x="0" y="196" font-size="11.5" fill="#5a6570">{L["d"]} / <tspan fill="#c4531d">{L["st"]}</tspan></text></svg>')
    # point shapes: side view of the last 6 mm, and end view
    shapes = []
    tips = [
        'M0 -9 L60 -9 L100 0 L60 9 L0 9 Z',                                   # sharp
        'M0 -9 L60 -9 Q96 -3 98 0 Q96 3 60 9 L0 9 Z',                         # light ball
        'M0 -9 L58 -9 Q92 -6 94 0 Q92 6 58 9 L0 9 Z',                         # medium ball
        'M0 -9 L60 -9 L100 -1 L100 1 L60 9 L0 9 Z',                           # cutting (wedge)
    ]
    ends = [
        '<circle cx="0" cy="0" r="12" fill="#fff" stroke="#1b2430" stroke-width="1.6"/><circle cx="0" cy="0" r="1.6" fill="#1b2430"/>',
        '<circle cx="0" cy="0" r="12" fill="#fff" stroke="#1b2430" stroke-width="1.6"/><circle cx="0" cy="0" r="3.2" fill="#1b2430"/>',
        '<circle cx="0" cy="0" r="12" fill="#fff" stroke="#1b2430" stroke-width="1.6"/><circle cx="0" cy="0" r="5.5" fill="#1b2430"/>',
        '<circle cx="0" cy="0" r="12" fill="#fff" stroke="#1b2430" stroke-width="1.6"/><path d="M-9 0H9" stroke="#1b2430" stroke-width="3"/>',
    ]
    for i, ((name, use), tip, end) in enumerate(zip(L['pts'], tips, ends)):
        y = 30 + i * 46
        shapes.append(f'<g transform="translate(10,{y})"><path d="{tip}" fill="#e6e9ec" stroke="#1b2430" stroke-width="1.6"/></g>'
                      f'<g transform="translate(150,{y})">{end}</g>'
                      f'<text x="180" y="{y-3}" font-size="14" font-weight="700">{name}</text>'
                      f'<text x="180" y="{y+14}" font-size="12" fill="#5a6570">{use}</text>')
    right = (f'<svg width="450" height="200" viewBox="0 0 450 200"><text x="10" y="12" font-size="11.5" fill="#5a6570">{L["side"]}</text>'
             f'<text x="150" y="12" font-size="11.5" fill="#5a6570" text-anchor="middle">{L["front"]}</text>' + ''.join(shapes) + '</svg>')
    return (HEAD.format(css='') + f'<div class="fig" style="--w:1000px"><p class="title">{L["title"]}</p><p class="sub">{L["sub"]}</p>'
            f'<div style="display:flex;gap:30px;align-items:flex-start">{left}{right}</div></div>')


# ------------------------------------------------------------------ 针孔的冲制
EYE = {
 'zh': dict(title='针孔怎样冲出来：工序与缺陷', sub='示意：沿针孔中心的横截面（垂直于针身轴线）；尺寸放大、不按比例',
  st=[('① 减径后的针身', '圆截面，直径 d'), ('② 冲长槽与短槽', '两侧压出槽，针孔区局部变薄'), ('③ 冲穿针孔', '冲头穿过，孔边留下毛刺'), ('④ 抛光后', '孔边倒圆，线从孔里滑过不受刮')],
  bad='常见缺陷', bads=['孔边毛刺、锐边：割线、起毛、断线', '孔偏：孔不在针身中心，一侧壁太薄易断', '孔壁粗糙：线与孔摩擦发热、线迹不匀', '冲头磨损：毛刺逐渐变大，孔宽漂移'],
  burr='毛刺', thread='线'),
 'en': dict(title='How the eye is made: steps and defects', sub='Illustrative: cross-section through the eye centre, perpendicular to the blade axis; enlarged, not to scale',
  st=[('① Reduced blade', 'round section, diameter d'), ('② Grooves pressed', 'eye zone thinned'), ('③ Eye punched', 'punch leaves a burr'), ('④ After polishing', 'edges rounded, thread slides')],
  bad='Common defects', bads=['Burrs and sharp edges: cut, fuzzed or broken thread', 'Eye off-centre: one wall too thin, needle breaks', 'Rough eye wall: friction heat, uneven stitches', 'Punch wear: burrs grow, eye width drifts'],
  burr='burr', thread='thread'),
}


def eye(L):
    W = 230
    g = []
    # 1 round
    g.append('<circle cx="0" cy="0" r="60" fill="#e6e9ec" stroke="#1b2430" stroke-width="2"/>')
    # 2 grooves: circle with two notches top/bottom (grooves on both sides)
    g2 = ('<path d="M-60 0 A60 60 0 0 1 -22 -56 L-22 -36 Q0 -28 22 -36 L22 -56 A60 60 0 0 1 60 0 A60 60 0 0 1 22 56 L22 40 Q0 32 -22 40 L-22 56 A60 60 0 0 1 -60 0 Z" fill="#e6e9ec" stroke="#1b2430" stroke-width="2"/>')
    g.append(g2)
    # 3 punched: hole through middle (walls left/right) with burrs
    g3 = ('<path d="M-60 0 A60 60 0 0 1 -22 -56 L-22 -36 L-18 -34 L-18 34 L-22 40 L-22 56 A60 60 0 0 1 -60 0 Z" fill="#e6e9ec" stroke="#1b2430" stroke-width="2"/>'
          '<path d="M60 0 A60 60 0 0 0 22 -56 L22 -36 L18 -34 L18 34 L22 40 L22 56 A60 60 0 0 0 60 0 Z" fill="#e6e9ec" stroke="#1b2430" stroke-width="2"/>'
          '<path d="M-18 34 L-12 46 L-20 40 Z M18 34 L12 46 L20 40 Z" fill="#c0392b" stroke="#c0392b" stroke-width="1.5"/>'
          f'<text x="0" y="68" text-anchor="middle" font-size="12" fill="#c0392b">{L["burr"]}</text>')
    g.append(g3)
    g4 = ('<path d="M-60 0 A60 60 0 0 1 -22 -56 L-22 -40 Q-14 -36 -14 -26 L-14 26 Q-14 36 -22 42 L-22 56 A60 60 0 0 1 -60 0 Z" fill="#e6e9ec" stroke="#1b2430" stroke-width="2"/>'
          '<path d="M60 0 A60 60 0 0 0 22 -56 L22 -40 Q14 -36 14 -26 L14 26 Q14 36 22 42 L22 56 A60 60 0 0 0 60 0 Z" fill="#e6e9ec" stroke="#1b2430" stroke-width="2"/>'
          '<circle cx="0" cy="0" r="8" fill="#2a5fb8"/>'
          f'<text x="0" y="-64" text-anchor="middle" font-size="12" fill="#2a5fb8">{L["thread"]}</text><path d="M0 -60 V-10" stroke="#2a5fb8" stroke-width="1" stroke-dasharray="3 3"/>')
    g.append(g4)
    svg = []
    for i, (gg, (t, s)) in enumerate(zip(g, L['st'])):
        x = 115 + i * W
        svg.append(f'<g transform="translate({x},95)">{gg}</g><text x="{x}" y="196" text-anchor="middle" font-size="14" font-weight="700">{t}</text>'
                   f'<text x="{x}" y="215" text-anchor="middle" font-size="12" fill="#5a6570">{s}</text>')
        if i:
            svg.append(f'<g transform="translate({x-W/2-13},86)">' + ARROW.replace('<svg ', '<svg x="0" y="0" ') + '</g>')
    bads = ''.join(f'<li>{b}</li>' for b in L['bads'])
    return (HEAD.format(css='ul{margin:6px 0 0 18px;padding:0;font-size:13px;columns:2;column-gap:40px}') +
            f'<div class="fig" style="--w:1000px"><p class="title">{L["title"]}</p><p class="sub">{L["sub"]}</p>'
            f'<svg width="940" height="225" viewBox="0 0 940 225">{"".join(svg)}</svg>'
            f'<div class="box o fill-o" style="text-align:left;margin-top:8px"><b>{L["bad"]}</b><ul>{bads}</ul></div></div>')


# ------------------------------------------------------------------ 梭道与梭床的配合、分组选配原理
RACE = {
 'zh': dict(title='梭道与梭床导轨的配合和分组选配', sub='示意：左为旋梭体与梭床的局部截面（间隙放大）；右为分 3 组选配的原理，数值为算例值',
  hb='旋梭体', bk='梭床', race='梭道（直径 D）', rib='导轨（外径 d）', gap='直径间隙 c = D − d',
  req='要求 10–30 μm（示意）', axis='旋梭轴线',
  rt='两零件各按 ±15 μm 加工（σ = 5 μm），测量后各分 3 组', gD='梭道 D 的偏差', gd='导轨 d 的偏差',
  g=['1 组', '2 组', '3 组'], rule='只在同组之间配对：c = 20 + x − y，组宽 10 μm → |x − y| < 10 μm → c 在 10–30 μm 之内',
  note='代价：两种零件的分布必须“长得一样”，否则各组件数不等，多出来的成为剩余不配套件'),
 'en': dict(title='Race-to-rib fit and grouped selective assembly', sub='Illustrative: left, a partial section of hook body and basket (clearance exaggerated); right, the principle of 3-group selective fitting with worked-example values',
  hb='Hook body', bk='Basket', race='Race (diameter D)', rib='Rib (outside diameter d)', gap='Diametral clearance c = D − d',
  req='required 10–30 μm (illustrative)', axis='hook axis',
  rt='Both parts made to ±15 μm (σ = 5 μm); measured, 3 groups each', gD='race deviation x', gd='rib deviation y',
  g=['Group 1', 'Group 2', 'Group 3'], rule='Pair only within a group: c = 20 + x − y; group width 10 μm → |x − y| < 10 μm → c within 10–30 μm',
  note='The price: both parts must have the same distribution, or the groups hold unequal counts and the surplus is left unmatched'),
}


def race(L):
    import math
    left = (
        '<svg width="475" height="300" viewBox="0 0 475 300">'
        # hook body section: L-shaped with race groove
        '<path d="M20 40 H330 V110 H300 V90 H250 V150 H300 V130 H330 V200 H20 Z" fill="#e9f0fc" stroke="#2a5fb8" stroke-width="2"/>'
        # basket with rib inside groove
        '<path d="M20 228 H240 V160 H258 V96 H292 V160 H310 V250 H20 Z" fill="#fcefe8" stroke="#e0662f" stroke-width="2"/>'
        '<path d="M20 275 H410" stroke="#5a6570" stroke-dasharray="8 5" stroke-width="1.4"/>'
        f'<text x="24" y="292" font-size="12" fill="#5a6570">{L["axis"]}</text>'
        f'<text x="40" y="70" font-size="15" font-weight="700" fill="#2a5fb8">{L["hb"]}</text>'
        f'<text x="40" y="244" font-size="15" font-weight="700" fill="#c4531d">{L["bk"]}</text>'
        # gap callouts
        '<path d="M292 100 L345 70" stroke="#1b2430" stroke-width="1.2"/>'
        f'<text x="336" y="66" font-size="12.5">{L["race"]}</text>'
        '<path d="M298 238 L318 256" stroke="#1b2430" stroke-width="1.2"/>'
        f'<text x="320" y="266" font-size="12.5">{L["rib"]}</text>'
        f'<text x="20" y="22" font-size="13" font-weight="700" fill="#c0392b">{L["gap"]}</text>'
        f'<text x="236" y="22" font-size="12" fill="#5a6570">{L["req"]}</text>'
        '<path d="M300 92 V96" stroke="#c0392b" stroke-width="3"/>'
        '</svg>')

    def bell(x0, y0, w, h, col, flip=False):
        pts = []
        for i in range(61):
            u = -3 + i * 0.1
            yy = math.exp(-u * u / 2)
            pts.append(f'{x0 + (u + 3) / 6 * w:.1f},{y0 + (yy * h if flip else -yy * h):.1f}')
        return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2.2"/>'
    x0, w = 25, 410
    parts = [f'<text x="0" y="16" font-size="12.5" font-weight="700">{L["rt"]}</text>']
    parts.append(bell(x0, 110, w, 70, '#2a5fb8'))
    parts.append(f'<text x="{x0+6}" y="56" font-size="12" fill="#2a5fb8">{L["gD"]}</text>')
    parts.append(bell(x0, 130, w, 70, '#e0662f', flip=True))
    parts.append(f'<text x="{x0+6}" y="196" font-size="12" fill="#c4531d">{L["gd"]}</text>')
    for j in range(4):
        xx = x0 + j / 3 * w
        parts.append(f'<path d="M{xx:.1f} 34 V206" stroke="#5a6570" stroke-dasharray="4 4"/>')
        parts.append(f'<text x="{xx:.1f}" y="222" text-anchor="middle" font-size="11.5" fill="#5a6570">{-15 + 10 * j:+d} μm</text>')
    for j in range(3):
        xx = x0 + (j + 0.5) / 3 * w
        parts.append(f'<text x="{xx:.1f}" y="124" text-anchor="middle" font-size="12.5" font-weight="700">{L["g"][j]}</text>')
        parts.append(f'<path d="M{xx:.1f} 98 V108 M{xx:.1f} 128 V138" stroke="#1e8449" stroke-width="2"/>')
    right = f'<svg width="470" height="232" viewBox="0 0 470 232">{"".join(parts)}</svg>'
    return (HEAD.format(css='') + f'<div class="fig" style="--w:1000px"><p class="title">{L["title"]}</p><p class="sub">{L["sub"]}</p>'
            f'<div style="display:flex;gap:20px;align-items:flex-start">{left}<div>{right}'
            f'<div class="box g fill-g" style="text-align:left;margin-top:8px;width:470px"><b>{L["rule"]}</b><span>{L["note"]}</span></div></div></div></div>')


# ------------------------------------------------------------------ 数字工厂：工艺、检验与数据闭环
DIG = {
 'zh': dict(title='把机针、旋梭的工艺与检验放进数字工厂', sub='示意：主数据按问渠数字工厂 data.py 的写法；测量值按 quality.measurement 信封上总线，进历史库后算控制图、Cpk 与选配统计',
  a=('主数据（data.py 写法）', '物料、BOM、工作中心、工艺路线、检验计划'),
  b=('ERP / MES', '工单按工艺路线派到工作中心；检验工序设“质检门”'),
  c=('车间工位', 'NDL-EYE 冲孔机旁的视觉测孔宽<br>HK-GRD 梭道磨床的在线量仪<br>HK-MATCH 选配站的气动量仪'),
  d=('统一数据总线', '<span class="mono2">wq/sewing/quality/&lt;单元&gt;/measurement</span><span class="mono2">wq/sewing/machining/&lt;单元&gt;/event</span>'),
  e=('历史库', '每条测量带批号、工序、量具、时间'),
  f=('SPC 与看板', '均值–极差控制图、Cpk、各组件数与剩余件'),
  g=('AI 工厂助手', '控制图报警 → 提醒（附证据）：换冲头、修整砂轮、调整梭床磨削目标'),
  loop='改进措施回到工艺路线和检验计划（新版本）'),
 'en': dict(title='Putting needle and hook processes and inspection into the digital factory', sub='Illustrative: master data written as in the WenQuest Digital Factory data.py; measurements travel on the bus in the quality.measurement envelope and the historian feeds control charts, Cpk and fitting statistics',
  a=('Master data (data.py style)', 'Items, BOMs, work centres, routings, inspection plans'),
  b=('ERP / MES', 'Work orders dispatched along the routing; inspection operations act as quality gates'),
  c=('Shop-floor stations', 'NDL-EYE: vision gauge for eye width<br>HK-GRD: in-process gauge on the race grinder<br>HK-MATCH: air gauges at the fitting station'),
  d=('Unified data bus', '<span class="mono2">wq/sewing/quality/&lt;unit&gt;/measurement</span><span class="mono2">wq/sewing/machining/&lt;unit&gt;/event</span>'),
  e=('Historian', 'every measurement carries lot, operation, gauge and time'),
  f=('SPC and dashboard', 'X̄–R charts, Cpk, group counts and leftovers'),
  g=('AI factory assistant', 'chart alarm → alert with evidence: change punch, dress wheel, re-target basket grinding'),
  loop='Corrective actions go back into routings and inspection plans (new revision)'),
}


def digital(L):
    def bx(cls, t, w=210):
        return f'<div class="box {cls}" style="width:{w}px;text-align:left"><b>{t[0]}</b><span>{t[1]}</span></div>'
    row1 = bx('k fill-k', L['a'], 185) + ARROW + bx('b fill-b', L['b'], 190) + ARROW + bx('o fill-o', L['c'], 255) + ARROW + bx('t fill-t', L['d'], 300)
    row2 = bx('p fill-p', L['g'], 300) + '<div style="transform:scaleX(-1)">' + ARROW + '</div>' + bx('g fill-g', L['f'], 250) + '<div style="transform:scaleX(-1)">' + ARROW + '</div>' + bx('t fill-t', L['e'], 300)
    css = '.mono2{font-family:"DejaVu Sans Mono",monospace;font-size:11.5px!important;white-space:nowrap;color:#0f6e74!important}.r{display:flex;align-items:center;gap:6px}.r2{justify-content:flex-end}.dn{display:flex;justify-content:flex-end;padding-right:105px;margin:4px 0}'
    loop = ('<svg width="1040" height="44" viewBox="0 0 1040 44" style="display:block"><path d="M150 0 V30 H105 V8" fill="none" stroke="#7444b4" stroke-width="2" stroke-dasharray="6 4"/>'
            '<path d="M99 14 L105 5 L111 14" fill="none" stroke="#7444b4" stroke-width="2"/>'
            f'<text x="170" y="30" font-size="12.5" fill="#7444b4">{L["loop"]}</text></svg>')
    # loop drawn from AI box (left of row2) back up to master data (row1 left) – place as a note row under row2
    return (HEAD.format(css=css) + f'<div class="fig" style="--w:1080px"><p class="title">{L["title"]}</p><p class="sub">{L["sub"]}</p>'
            f'<div class="r">{row1}</div><div class="dn">{DOWN}</div><div class="r r2">{row2}</div>'
            f'<div class="note" style="color:#7444b4">↺ {L["loop"]}</div></div>')


FIGS = {'needleflow': (needleflow, NEEDLE), 'hookflow': (hookflow, HOOK), 'points': (points, POINTS),
        'eye': (eye, EYE), 'racefit': (race, RACE), 'digital': (digital, DIG)}

if __name__ == '__main__':
    for name, (fn, D) in FIGS.items():
        for lang in ('zh', 'en'):
            p = os.path.join(HERE, f'ch24_{name}.{lang}.html')
            open(p, 'w').write(fn(D[lang]))
            out = f'img/{"en/" if lang == "en" else ""}fig_c24_{name}.png'
            print(f'node fig.js figsrc/ch24_{name}.{lang}.html {out}')
