# -*- coding: utf-8 -*-
"""第 25 章结构图/流程图：生成 figsrc/ch25_*.zh.html / .en.html，再用 node fig.js 渲染。"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
HEAD = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">'
def T(zh, en): return {'zh': zh, 'en': en}

# ------------------------------------------------------------------ 图 25-1 机壳与关键孔系
def housing(L):
    t = {k: v[L] for k, v in dict(
        title=T('机壳：所有孔的相对位置都由它决定', 'The housing fixes the relative position of every bore'),
        sub=T('工业平缝机机壳正视示意（不按比例）；孔位要求为示意值，以企业图纸为准', 'Front view of an industrial lockstitch housing (schematic, not to scale); tolerances are illustrative'),
        arm=T('机臂', 'arm'), col=T('立柱', 'column'), bed=T('底板', 'bed'), head=T('机头', 'head'),
        a=T('a 上轴孔（3 处）', 'a main-shaft bores (3)'), b=T('b 下轴孔（3 处）', 'b hook-shaft bores (3)'),
        c=T('c 针杆孔（上下 2 处）', 'c needle-bar bores (2)'), d=T('d 压脚杆孔', 'd presser-bar bores'),
        hook=T('旋梭', 'hook'), belt=T('同步带', 'timing belt'), hw=T('手轮', 'handwheel'),
        dA=T('A 底面', 'A bottom face'), dC=T('C 右端面', 'C right end face'),
        k1=T('关键孔系（示意）', 'Key bores (illustrative)'),
        r1=T('a 三处同轴度 ⌀0.01 mm；对 A 平行度 0.02/300', 'a coaxiality ⌀0.01 mm; parallel to A 0.02/300'),
        r2=T('b 三处同轴度 ⌀0.01 mm；与 a 的中心距 ±0.02', 'b coaxiality ⌀0.01 mm; centre distance to a ±0.02'),
        r3=T('c 两孔同轴度 ⌀0.008；对 a 垂直度 0.01', 'c coaxiality ⌀0.008; perpendicular to a 0.01'),
        r4=T('c 轴线到 b 轴线（旋梭）的位置度 ⌀0.03', 'c axis to b axis (hook) position ⌀0.03'),
        r5=T('基准：A 底面、B 后侧面（图上看不见）、C 右端面', 'Datums: A bottom, B rear face (hidden), C right end'),
        k2=T('铸件结构要点', 'Casting design points'),
        s1=T('① 壁厚尽量均匀（示意 6–8 mm），厚处减薄或掏空', '① keep walls even (illustrative 6–8 mm); core out thick spots'),
        s2=T('② 加强筋提高机臂和立柱的弯曲刚度（第 23.6 节）', '② ribs stiffen arm and column (Section 23.6)'),
        s3=T('③ 内外转角做圆角，避免缩孔和裂纹', '③ fillet every corner against shrinkage and cracks'),
        s4=T('④ 清砂工艺孔，加工后用堵头封住', '④ core-removal holes, plugged after machining'),
        s5=T('⑤ 拔模斜度 1°–3°（砂型），压铸更小', '⑤ draft 1°–3° (sand), less for die casting'),
        s6=T('⑥ 油路孔与油池：铸出或钻出，要能清洗', '⑥ oil passages and sump: cast or drilled, must be cleanable'),
    ).items()}
    svg = f'''<svg viewBox="0 0 660 420" width="660" height="420" style="display:block">
<defs><pattern id="h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#9aa4ae" stroke-width="1"/></pattern></defs>
<path d="M60 40 H610 V320 H640 V372 H20 V320 H520 V122 H180 V238 H60 Z" fill="#f3f5f6" stroke="#1b2430" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M520 122 Q520 112 530 112" fill="none" stroke="#c48a17" stroke-width="2"/>
<g stroke="#9aa4ae" stroke-width="2" stroke-dasharray="4 3"><line x1="290" y1="92" x2="290" y2="120"/><line x1="380" y1="92" x2="380" y2="120"/><line x1="470" y1="92" x2="470" y2="120"/></g>
<line x1="40" y1="82" x2="650" y2="82" stroke="#5a6570" stroke-dasharray="10 4 2 4" stroke-width="1.2"/>
<line x1="60" y1="345" x2="650" y2="345" stroke="#5a6570" stroke-dasharray="10 4 2 4" stroke-width="1.2"/>
<line x1="105" y1="25" x2="105" y2="335" stroke="#5a6570" stroke-dasharray="10 4 2 4" stroke-width="1.2"/>
<line x1="150" y1="30" x2="150" y2="300" stroke="#5a6570" stroke-dasharray="10 4 2 4" stroke-width="1"/>
<g fill="#e9f0fc" stroke="#2a6fdb" stroke-width="2">
<rect x="174" y="70" width="12" height="24"/><rect x="514" y="70" width="12" height="24"/><rect x="604" y="70" width="12" height="24"/>
<rect x="144" y="333" width="12" height="24"/><rect x="330" y="333" width="12" height="24"/><rect x="604" y="333" width="12" height="24"/>
</g>
<g fill="#fcefe8" stroke="#e0662f" stroke-width="2"><rect x="93" y="34" width="24" height="12"/><rect x="93" y="226" width="24" height="12"/></g>
<g fill="#f2ecfa" stroke="#8a5cc7" stroke-width="2"><rect x="140" y="34" width="20" height="12"/><rect x="140" y="226" width="20" height="12"/></g>
<line x1="105" y1="238" x2="105" y2="312" stroke="#1b2430" stroke-width="2.5"/>
<circle cx="105" cy="345" r="15" fill="#fbf4e3" stroke="#c48a17" stroke-width="2"/>
<circle cx="565" cy="82" r="13" fill="none" stroke="#14797f" stroke-width="2"/><circle cx="565" cy="345" r="13" fill="none" stroke="#14797f" stroke-width="2"/>
<line x1="552" y1="82" x2="552" y2="345" stroke="#14797f" stroke-width="1.6" stroke-dasharray="5 3"/><line x1="578" y1="82" x2="578" y2="345" stroke="#14797f" stroke-width="1.6" stroke-dasharray="5 3"/>
<rect x="640" y="58" width="12" height="48" rx="3" fill="#fff" stroke="#5a6570" stroke-width="1.5"/>
<text x="335" y="105" font-size="15" font-weight="700" fill="#1b2430" text-anchor="middle">{t['arm']}</text>
<text x="470" y="250" font-size="15" font-weight="700" fill="#1b2430" text-anchor="end">{t['col']}</text>
<text x="420" y="366" font-size="15" font-weight="700" fill="#1b2430">{t['bed']}</text>
<text x="66" y="150" font-size="15" font-weight="700" fill="#1b2430">{t['head']}</text>
<text x="300" y="63" font-size="13" fill="#2a5fb8" font-weight="700">{t['a']}</text>
<text x="190" y="318" font-size="13" fill="#2a5fb8" font-weight="700">{t['b']}</text>
<text x="190" y="205" font-size="13" fill="#c4531d" font-weight="700">{t['c']}</text>
<text x="190" y="222" font-size="13" fill="#7444b4" font-weight="700">{t['d']}</text>
<line x1="186" y1="200" x2="118" y2="232" stroke="#c4531d" stroke-width="1"/>
<text x="105" y="398" font-size="12.5" fill="#a8740c" text-anchor="middle">{t['hook']}</text>
<text x="585" y="270" font-size="12.5" fill="#0f6e74" text-anchor="middle" transform="rotate(-90 585 270)">{t['belt']}</text>
<text x="656" y="30" font-size="12" fill="#5a6570" text-anchor="end">{t['hw']}</text>
<polygon points="240,372 232,386 248,386" fill="#1b2430"/><text x="254" y="388" font-size="13" font-weight="700" fill="#1b2430">{t['dA']}</text>
<polygon points="642,346 656,338 656,354" fill="#1b2430"/><text x="656" y="392" font-size="13" font-weight="700" fill="#1b2430" text-anchor="end">{t['dC']}</text>
<g font-size="14" font-weight="700" fill="#c4531d"><text x="245" y="48">①</text><text x="384" y="118">②</text><text x="516" y="140">③</text><text x="484" y="332">④</text><text x="40" y="360">⑥</text></g>
<circle cx="490" cy="345" r="5" fill="#fff" stroke="#1b2430" stroke-width="1.5"/>
<circle cx="40" cy="335" r="3" fill="#c48a17"/>
</svg>'''
    lst1 = ''.join(f'<li>{t[k]}</li>' for k in ('r1', 'r2', 'r3', 'r4', 'r5'))
    lst2 = ''.join(f'<li>{t[k]}</li>' for k in ('s1', 's2', 's3', 's4', 's5', 's6'))
    ul = 'style="margin:6px 0 0;padding-left:16px;text-align:left;font-size:13px;line-height:1.55"'
    return f'''{HEAD}<div class="fig" style="--w:1120px"><p class="title">{t['title']}</p><p class="sub">{t['sub']}</p>
<div style="display:grid;grid-template-columns:660px 1fr;gap:18px;align-items:start">{svg}
<div style="display:flex;flex-direction:column;gap:12px"><div class="box b fill-b"><b>{t['k1']}</b><ul {ul}>{lst1}</ul></div>
<div class="box o fill-o"><b>{t['k2']}</b><ul {ul}>{lst2}</ul></div></div></div></div>'''

# ------------------------------------------------------------------ 图 25-2 两种毛坯路线与缺陷
def casting(L):
    def row(title, cls, steps, defects):
        cells = []
        for i, (b, s) in enumerate(steps):
            cells.append(f'<div class="box {cls}"><b>{b}</b><span>{s}</span></div>')
            if i < len(steps) - 1: cells.append('<div style="align-self:center;text-align:center;color:#5a6570;font-size:20px">→</div>')
        cols = ' '.join(['1fr'] + ['22px', '1fr'] * (len(steps) - 1))
        dc = []
        for i, d in enumerate(defects):
            dc.append(f'<div style="font-size:12px;color:#c0392b;text-align:center;line-height:1.35">{d}</div>')
            if i < len(defects) - 1: dc.append('<div></div>')
        return (f'<p style="font-weight:700;margin:14px 0 8px">{title}</p><div style="display:grid;grid-template-columns:{cols};gap:6px 0">{"".join(cells)}{"".join(dc)}</div>')
    zh = L == 'zh'
    sand = row(T('灰铸铁砂型铸造（中小批量、要求吸振的机壳）', 'Grey-iron sand casting (small/medium batches, vibration-damping housings)')[L], 'b fill-b', [
        (T('模样与芯盒', 'Pattern & core box')[L], T('含收缩率、拔模斜度、加工余量', 'shrinkage, draft, machining stock')[L]),
        (T('造型制芯', 'Moulding & coring')[L], T('湿型砂或树脂砂；内腔用砂芯', 'green or resin sand; cores for cavities')[L]),
        (T('熔炼浇注', 'Melting & pouring')[L], T('冲天炉或中频炉；控温度和成分', 'cupola or induction; control temp. & chemistry')[L]),
        (T('冷却落砂', 'Cooling & shake-out')[L], T('在型内缓冷，开箱过早易变形', 'cool in mould; early shake-out distorts')[L]),
        (T('清理', 'Fettling')[L], T('去浇冒口、抛丸、清砂芯', 'remove gates/risers, shot blast, decore')[L]),
        (T('时效', 'Ageing')[L], T('人工时效（去应力退火）', 'thermal stress relief')[L]),
        (T('检验', 'Inspection')[L], T('外观、硬度、尺寸，抽检 X 射线', 'visual, hardness, dims; sample X-ray')[L])],
        [T('尺寸错、变形', 'wrong size, distortion')[L], T('夹砂、砂眼、错型', 'sand inclusion, mismatch')[L], T('气孔、冷隔、浇不足', 'gas holes, cold shuts, misruns')[L],
         T('缩孔、缩松、裂纹', 'shrinkage, cracks')[L], T('残留砂芯', 'retained core sand')[L], T('不做：孔位慢慢漂移', 'skip it: bores drift later')[L], T('漏检的内部缺陷', 'missed internal defects')[L]])
    die = row(T('铝合金压铸（大批量、轻量化的家用机和部分工业机部件）', 'Aluminium die casting (high volume, lightweight household machines and some industrial parts)')[L], 'g fill-g', [
        (T('压铸模', 'Die')[L], T('钢模，费用高、寿命长', 'steel die: costly, long life')[L]),
        (T('熔化保温', 'Melt & hold')[L], T('除气、精炼', 'degas, refine')[L]),
        (T('高压压射', 'High-pressure shot')[L], T('几十毫秒充满型腔', 'fills in tens of ms')[L]),
        (T('开模顶出', 'Open & eject')[L], T('件出模即接近成形', 'near-net shape')[L]),
        (T('切边去浇口', 'Trim')[L], T('切边模、去毛刺', 'trim die, deburr')[L]),
        (T('（可选）热处理', '(Optional) heat treat')[L], T('视合金和要求而定', 'depends on alloy')[L]),
        (T('检验', 'Inspection')[L], T('X 射线、渗漏试验', 'X-ray, leak test')[L])],
        [T('模具磨损、粘模', 'die wear, soldering')[L], T('氧化夹杂', 'oxide inclusions')[L], T('卷气形成气孔', 'entrapped-air porosity')[L], T('顶出变形', 'ejection distortion')[L],
         T('毛刺残留', 'residual flash')[L], T('气孔受热鼓泡', 'blisters from porosity')[L], T('加工后露出的气孔', 'porosity opened by machining')[L]])
    return (f'{HEAD}<div class="fig" style="--w:1240px"><p class="title">{T("机壳毛坯的两条路线：每一步都可能留下缺陷", "Two routes to a housing blank, and the defects each step can leave")[L]}</p>'
            f'<p class="sub">{T("红字：该工序容易产生的典型缺陷（示意）", "Red: typical defects introduced at that step (illustrative)")[L]}</p>{sand}{die}</div>')

# ------------------------------------------------------------------ 图 25-4 定位、卧加与镗孔
def hmc(L):
    t = {k: v[L] for k, v in dict(
        title=T('3-2-1 定位、卧式加工中心一次装夹、一次镗通', '3-2-1 location, one HMC set-up, one boring pass'),
        sub=T('示意；精度数值为算例值', 'Schematic; accuracy figures are worked-example values'),
        a=T('a　3-2-1 定位', 'a   3-2-1 location'), b=T('b　回转工作台：一次装夹加工四个面', 'b   Rotary table: four faces in one set-up'), c=T('c　两种镗孔方法', 'c   Two ways to bore'),
        p3=T('底面 A：3 个支承（限 3 个自由度）', 'face A: 3 supports (3 DOF)'), p2=T('后侧面 B：2 个定位点（限 2 个）', 'face B: 2 locators (2 DOF)'), p1=T('端面 C：1 个定位点（限 1 个）', 'face C: 1 stop (1 DOF)'),
        cl=T('夹紧力压向定位点，不能把工件压变形', 'clamp toward the locators, without distorting the part'),
        tb=T('B 轴回转台', 'B-axis table'), sp=T('主轴', 'spindle'), fx=T('夹具', 'fixture'),
        c1=T('一根镗杆从一端进给、穿过两孔（必要时用导向套）', 'one bar fed from one side through both bores (guide bush if needed)'),
        c1v=T('同轴度取决于镗杆的直线进给：算例 ≈ 0.003–0.005 mm', 'coaxiality set by straight feed: ≈ 0.003–0.005 mm'),
        c2=T('先镗一端，回转台转 180° 再镗另一端', 'bore one end, index table 180°, bore the other'),
        c2v=T('还要加上回转中心找正误差 × 2 和分度误差 × 距离', 'adds 2 × table-centre error + indexing error × distance'),
        c2w=T('算例 ≈ 0.01–0.015 mm', 'worked example ≈ 0.01–0.015 mm'),
    ).items()}
    svga = f'''<svg viewBox="0 0 340 280" width="340" height="280">
<polygon points="40,150 210,150 270,105 100,105" fill="#e9f0fc" stroke="#2a6fdb" stroke-width="2"/>
<polygon points="40,150 210,150 210,200 40,200" fill="#f3f5f6" stroke="#1b2430" stroke-width="2"/>
<polygon points="210,150 270,105 270,155 210,200" fill="#eaf6ee" stroke="#2e9e5b" stroke-width="2"/>
<polygon points="40,150 100,105 100,155 40,200" fill="none" stroke="#9aa4ae" stroke-dasharray="4 3"/>
<g fill="#c0392b"><circle cx="70" cy="214" r="5"/><circle cx="190" cy="214" r="5"/><circle cx="130" cy="232" r="5"/></g>
<g stroke="#c0392b" stroke-width="1.5"><line x1="70" y1="200" x2="70" y2="209"/><line x1="190" y1="200" x2="190" y2="209"/></g>
<g fill="#e0662f"><circle cx="135" cy="92" r="5"/><circle cx="235" cy="92" r="5"/></g>
<circle cx="288" cy="140" r="5" fill="#8a5cc7"/>
<text x="10" y="272" font-size="12" fill="#c0392b">{t['p3']}</text>
<text x="335" y="70" font-size="12" text-anchor="end" fill="#c4531d">{t['p2']}</text>
<text x="338" y="250" font-size="12" fill="#7444b4" text-anchor="end">{t['p1']}</text><line x1="288" y1="146" x2="300" y2="236" stroke="#8a5cc7" stroke-width="1"/>
<line x1="125" y1="36" x2="125" y2="118" stroke="#1b2430" stroke-width="2"/><polygon points="125,124 119,112 131,112" fill="#1b2430"/>
<text x="10" y="22" font-size="12" fill="#1b2430">{t['cl']}</text>
<text x="100" y="236" font-size="13" font-weight="700" fill="#c0392b">A</text><text x="181" y="97" font-size="13" font-weight="700" fill="#c4531d">B</text><text x="242" y="160" font-size="13" font-weight="700" fill="#1f8a4c">C</text>
</svg>'''
    svgb = f'''<svg viewBox="0 0 300 260" width="300" height="260">
<circle cx="150" cy="140" r="95" fill="#f3f5f6" stroke="#1b2430" stroke-width="2"/>
<rect x="95" y="95" width="110" height="90" fill="#fbf4e3" stroke="#c48a17" stroke-width="2"/>
<rect x="110" y="110" width="80" height="60" fill="#e9f0fc" stroke="#2a6fdb" stroke-width="2"/>
<path d="M 60 70 A 105 105 0 0 1 120 38" fill="none" stroke="#e0662f" stroke-width="2.5"/><polygon points="122,34 110,34 116,44" fill="#e0662f"/>
<rect x="250" y="128" width="46" height="24" fill="#fcefe8" stroke="#e0662f" stroke-width="2"/><line x1="250" y1="140" x2="210" y2="140" stroke="#1b2430" stroke-width="3"/>
<text x="273" y="170" font-size="12" text-anchor="middle" fill="#c4531d">{t['sp']}</text>
<text x="150" y="252" font-size="12.5" text-anchor="middle" fill="#1b2430">{t['tb']}</text>
<text x="150" y="91" font-size="11.5" text-anchor="middle" fill="#a8740c">{t['fx']}</text>
<text x="40" y="60" font-size="12" fill="#c4531d">B</text>
<g font-size="11" fill="#5a6570" text-anchor="middle"><text x="150" y="145">0°</text><text x="216" y="114">90°</text></g>
</svg>'''
    svgc = f'''<svg viewBox="0 0 380 280" width="380" height="280">
<g fill="#f3f5f6" stroke="#1b2430" stroke-width="2"><rect x="70" y="30" width="34" height="70"/><rect x="290" y="30" width="34" height="70"/></g>
<g fill="#fff" stroke="#2a6fdb" stroke-width="2"><rect x="70" y="53" width="34" height="24"/><rect x="290" y="53" width="34" height="24"/></g>
<line x1="10" y1="65" x2="350" y2="65" stroke="#e0662f" stroke-width="5"/><polygon points="350,57 366,65 350,73" fill="#e0662f"/>
<rect x="335" y="52" width="14" height="26" fill="#fbf4e3" stroke="#c48a17" stroke-width="1.5"/>
<g fill="#f3f5f6" stroke="#1b2430" stroke-width="2"><rect x="70" y="150" width="34" height="70"/><rect x="290" y="150" width="34" height="70"/></g>
<g fill="#fff" stroke="#2a6fdb" stroke-width="2"><rect x="70" y="173" width="34" height="24"/><rect x="290" y="176" width="34" height="24"/></g>
<line x1="10" y1="185" x2="118" y2="185" stroke="#e0662f" stroke-width="5"/><line x1="276" y1="188" x2="372" y2="188" stroke="#8a5cc7" stroke-width="5"/>
<path d="M 180 215 A 26 26 0 1 1 214 215" fill="none" stroke="#8a5cc7" stroke-width="2"/><polygon points="214,210 220,222 208,220" fill="#8a5cc7"/><text x="197" y="200" font-size="11" text-anchor="middle" fill="#7444b4">180°</text>
<text x="190" y="18" font-size="12" text-anchor="middle" fill="#1b2430">{t['c1']}</text>
<text x="190" y="120" font-size="12" text-anchor="middle" fill="#1f8a4c" font-weight="700">{t['c1v']}</text>
<text x="190" y="140" font-size="12" text-anchor="middle" fill="#1b2430">{t['c2']}</text>
<text x="190" y="252" font-size="12" text-anchor="middle" fill="#c0392b" font-weight="700">{t['c2v']}</text><text x="190" y="270" font-size="12" text-anchor="middle" fill="#c0392b" font-weight="700">{t['c2w']}</text>
</svg>'''
    cap = 'style="font-weight:700;font-size:14px;margin:0 0 6px"'
    return (f'{HEAD}<div class="fig" style="--w:1110px"><p class="title">{t["title"]}</p><p class="sub">{t["sub"]}</p>'
            f'<div style="display:grid;grid-template-columns:340px 300px 380px;gap:30px">'
            f'<div><p {cap}>{t["a"]}</p>{svga}</div><div><p {cap}>{t["b"]}</p>{svgb}</div><div><p {cap}>{t["c"]}</p>{svgc}</div></div></div>')

# ------------------------------------------------------------------ 图 25-5 凸轮工艺流程
def camflow(L):
    st = [
        ('k', T('下料', 'Cut blank')[L], T('棒料或锻坯：20CrMnTi（渗碳）/ 45、40Cr（感应淬火）', 'bar or forging: carburising or induction-hardening steel')[L], T('材料牌号、炉号', 'grade, heat no.')[L]),
        ('b', T('车削', 'Turning')[L], T('内孔、端面、外圆，留磨量', 'bore, faces, OD; leave grinding stock')[L], T('孔径、端面跳动', 'bore, face runout')[L]),
        ('b', T('铣廓线 / 线切割', 'Mill or wire-cut profile')[L], T('数控铣（留 0.2–0.3 mm），沟槽凸轮铣槽；小批可线切割', 'CNC mill (0.2–0.3 mm stock), groove cams; wire EDM for small lots')[L], T('廓线余量均匀', 'even stock')[L]),
        ('o', T('热处理', 'Heat treatment')[L], T('渗碳淬火 + 低温回火，或廓线感应淬火', 'carburise + temper, or induction-harden the profile')[L], T('硬度、硬化层深、变形', 'hardness, case depth, distortion')[L]),
        ('t', T('磨孔与端面', 'Grind bore & faces')[L], T('建立凸轮磨削的基准', 'creates the datum for cam grinding')[L], T('孔径、端面垂直度', 'bore, squareness')[L]),
        ('p', T('数控凸轮磨削', 'CNC cam grinding')[L], T('C 轴转凸轮、X 轴进退砂轮；粗磨—精磨—光磨', 'C turns cam, X moves wheel; rough–finish–spark-out')[L], T('升程、表面粗糙度、烧伤', 'lift, roughness, burn')[L]),
        ('g', T('廓线测量', 'Profile measurement')[L], T('凸轮测量仪或三坐标：每 0.5°–1° 测一点', 'cam gauge or CMM: a point every 0.5°–1°')[L], T('升程误差曲线、谐波', 'lift-error curve, harmonics')[L]),
        ('k', T('清洗防锈', 'Clean & protect')[L], T('入库或装配', 'to stores or assembly')[L], T('清洁度', 'cleanliness')[L]),
    ]
    cells = []
    for i, (c, b, s, q) in enumerate(st):
        cells.append(f'<div class="box {c} fill-{c if c!="k" else "k"}"><b>{b}</b><span>{s}</span><small style="margin-top:6px;color:#1b2430">✓ {q}</small></div>')
        if i in (0, 1, 2, 4, 5, 6): cells.append('<div style="align-self:center;text-align:center;color:#5a6570;font-size:20px">→</div>')
        if i == 3: pass
    row1 = cells[:7]; row2 = cells[7:]
    g = 'display:grid;grid-template-columns:1fr 24px 1fr 24px 1fr 24px 1fr;gap:0;align-items:stretch'
    fb = T('补偿回路：测得的升程误差 → 谐波分解 → 改写 C–X 磨削轨迹（反向叠加）→ 再磨一次。低阶误差改得掉，高阶（振纹）只能靠工艺消除',
           'Compensation loop: measured lift error → harmonic analysis → rewrite the C–X path (subtract the error) → regrind. Low orders can be corrected; high orders (chatter) must be removed by the process')[L]
    return (f'{HEAD}<div class="fig" style="--w:1180px"><p class="title">{T("凸轮的工艺流程：热处理以后靠磨削定形状", "Cam process route: after heat treatment, grinding sets the shape")[L]}</p>'
            f'<p class="sub">{T("✓ 为该工序的主要检验项目；余量等数值为示意", "✓ main inspection item at that step; stock values illustrative")[L]}</p>'
            f'<div style="{g}">{"".join(row1)}</div><div style="text-align:right;margin:4px 12% 4px 0;font-size:20px;color:#5a6570">↓</div>'
            f'<div style="{g}">{"".join(row2[::-1]) if False else ""}{"".join(reversed_row(row2))}</div>'
            f'<div class="box y fill-y" style="margin-top:14px;text-align:left"><b>↺ {fb}</b></div></div>')

def reversed_row(row2):
    # row2: [box4, ->, box5, ->, box6, ->, box7, box8]  显示为 清洗 ← 测量 ← 磨 ← 磨孔 ← 热处理（从右到左）
    boxes = [x for x in row2 if 'class="box' in x]
    out = []
    for i, b in enumerate(reversed(boxes)):
        out.append(b)
        if i < len(boxes) - 1: out.append('<div style="align-self:center;text-align:center;color:#5a6570;font-size:20px">←</div>')
    return out

FIGS = {'housing': housing, 'casting': casting, 'hmc': hmc, 'camflow': camflow}
if __name__ == '__main__':
    for name, fn in FIGS.items():
        for L in ('zh', 'en'):
            p = os.path.join(HERE, f'ch25_{name}.{L}.html'); open(p, 'w').write(fn(L))
            out = os.path.join(ROOT, 'img', f'fig_25_{name}.png') if L == 'zh' else os.path.join(ROOT, 'img', 'en', f'fig_25_{name}.png')
            subprocess.run(['node', os.path.join(ROOT, 'fig.js'), p, out], cwd=ROOT, check=True)
