# Fig 1-4 roadmap (8 parts) and Fig 17-6 pattern chart, zh + en
import subprocess
T={
'zh':dict(title='全书路线图：一针 → 一台机器 → 一类机器 → 控制 → 原型与测试 → 制造 → 一座工厂 → 未来',
 sub='八篇三十一章；箭头表示后面的篇章用到前面的内容；带 NEW 的是本版新增',
 parts=[('一','绪论','第 1–2 章','线迹怎样形成<br>四个动作与时序','#7aa6e8',''),
        ('二','平缝机机构','第 3–8 章','刺布、挑线、钩线<br>送布、张力、动力学','#2a6fdb',''),
        ('三','包缝、绷缝与链缝','第 9–10 章','弯针、切刀<br>差动送布','#3d8fd1',''),
        ('四','特种机与自动单元','第 11–12 章','锁眼、钉扣、套结<br>自动单元、吊挂','#14797f',''),
        ('五','电气控制','第 13–18 章','伺服与传感、平缝机电控<br>花样机、刺绣机、横机<br>电控箱设计与测试','#e0662f',''),
        ('六','电控原型机与自动化测试','第 19–22 章','平台与零件库、快速配套<br>平缝·包缝·花样机·横机原型<br>自动化测试与持续迭代','#c4531d','NEW'),
        ('七','制造与数字工厂','第 23–27 章','设计制造检测<br>机针·旋梭·机壳·凸轮工艺<br>联网、数字工厂整体方案','#b7791f','NEW'),
        ('八','工厂与未来','第 28–31 章','工序与产线、典型工厂<br>趋势、人工智能','#8a5cc7','')],
 every='每章都有',items=['引子：车间里的一个真问题','结构图与三维模型','建模、推导与算例','动画或虚拟实验','设计要点、现场要点','习题与参考答案'],
 note='第六篇是“动手篇”：用零件库模块搭原型，用自动化测试迭代到工业级'),
'en':dict(title='Roadmap: a stitch → a machine → a family → control → prototypes & tests → manufacturing → a factory → the future',
 sub='Eight parts, thirty-one chapters; arrows show later parts building on earlier ones; NEW marks parts added in this edition',
 parts=[('I','Introduction','Ch. 1–2','How a stitch forms<br>four motions and timing','#7aa6e8',''),
        ('II','Lockstitch mechanisms','Ch. 3–8','Needle bar, take-up, hook<br>feed, tension, dynamics','#2a6fdb',''),
        ('III','Overlock, cover & chain','Ch. 9–10','Loopers, knives<br>differential feed','#3d8fd1',''),
        ('IV','Special machines & units','Ch. 11–12','Buttonholing, buttons, bartacks<br>automatic units, hangers','#14797f',''),
        ('V','Electrical control','Ch. 13–18','Servos and sensors, lockstitch control<br>pattern, embroidery, knitting<br>control-box design and test','#e0662f',''),
        ('VI','Control prototypes & testing','Ch. 19–22','Platform and parts library<br>lockstitch · overlock · pattern · knit<br>automated tests, iteration','#c4531d','NEW'),
        ('VII','Manufacturing & digital factory','Ch. 23–27','Design, build, test<br>needles · hooks · housings · cams<br>connectivity, digital factory','#b7791f','NEW'),
        ('VIII','Factories & the future','Ch. 28–31','Operations and lines, factories<br>trends, AI','#8a5cc7','')],
 every='Every chapter has',items=['An opening problem from the shop floor','Structure drawings and 3D models','Modelling, derivation, worked examples','Animations or virtual labs','Design notes and shop-floor notes','Exercises with answers'],
 note='Part VI is the hands-on part: build prototypes from library modules and iterate them to industrial grade with automated tests')}
def card(p,x,y):
    n,name,ch,body,col,new=p
    badge=f'<span style="font:600 11px monospace;color:#fff;background:#1b2430;border-radius:4px;padding:1px 5px;margin-left:6px">{new}</span>' if new else ''
    return f'''<div style="position:absolute;left:{x}px;top:{y}px;width:250px;height:178px;border:2px solid {col};border-radius:10px;background:#fff;overflow:hidden">
<div style="background:{col};color:#fff;font-weight:700;padding:8px 12px;font-size:15px">{n}&nbsp; {name}{badge}</div>
<div style="padding:8px 12px;font-size:13px;line-height:1.6"><div style="color:{col};font-weight:700">{ch}</div>{body}</div></div>'''
for lang,t in T.items():
    pos=[(20,0),(300,0),(580,0),(860,0),(20,250),(300,250),(580,250),(860,250)]
    cards=''.join(card(p,x,y) for p,(x,y) in zip(t['parts'],pos))
    arrows=''
    def ar(x1,y1,x2,y2): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5a6570" stroke-width="2" marker-end="url(#a)"/>'
    for i in range(3): arrows+=ar(270+280*i,89,298+280*i,89)
    for i in range(3): arrows+=ar(270+280*i,339,298+280*i,339)
    arrows+=f'<path d="M985 178 L985 214 L145 214 L145 248" fill="none" stroke="#5a6570" stroke-width="2" marker-end="url(#a)"/>'
    items=''.join(f'<li>{x}</li>' for x in t['items'])
    html=f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">
<div class="fig" style="--w:1420px"><p class="title">{t['title']}</p><p class="sub">{t['sub']}</p>
<div style="display:flex;gap:24px"><div style="position:relative;width:1120px;height:440px">
<svg width="1120" height="440" style="position:absolute;left:0;top:0"><defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5a6570"/></marker></defs>{arrows}</svg>{cards}</div>
<div class="box" style="width:230px;text-align:left;padding:14px 16px;align-self:flex-start"><b>{t['every']}</b><ul style="padding-left:18px;margin:8px 0;font-size:13px;line-height:1.9">{items}</ul><p style="font-size:12.5px;color:#c4531d;margin:6px 0 0">{t['note']}</p></div></div></div>'''
    open(f'road.{lang}.html','w').write(html)
    out='../img/fig_1_road2.png' if lang=='zh' else '../img/en/fig_1_road2.png'
    subprocess.run(['node','../fig.js',f'road.{lang}.html',out],check=True)

# Fig 17-6
motif=['000000000000','000001100000','000011110000','000111111000','000011110000','000001100000','000000000000','000000000000']
# row index 1..8 bottom to top; we want row 4 = 000001100000 per text table
motif=['000000000000','000000000000','000011110000','000001100000','000011110000','000111111000','000011110000','000001100000']
T2={'zh':dict(title='意匠图与编译出的选针数据（12 针 × 8 行示例）',sub='左：意匠图，白色格 = 纱嘴 1（底色），橙色格 = 纱嘴 2（花色），从下往上织。右：编译结果，每个意匠行拆成两个横列，每个横列只选用该色线圈的针（1 = 编织）',
 h=['横列','方向','纱嘴','前床选针（针 1→12）'],c1='1 底色',c2='2 花色',note='第 4 行（加框）对应正文表中的 4a、4b。其余组织参数（后床、度目、摇床、速度）编译时从参数表引用。示例值。',rowl='行',needle='针'),
 'en':dict(title='Pattern chart and the compiled selection data (12 needles × 8 rows, example)',sub='Left: pattern chart; white = carrier 1 (ground), orange = carrier 2 (motif), knitted bottom to top. Right: the compiled result; each chart row becomes two courses, and each course selects only the needles that knit its colour (1 = knit)',
 h=['Course','Dir.','Carrier','Front-bed selection (needle 1→12)'],c1='1 ground',c2='2 motif',note='Row 4 (boxed) corresponds to courses 4a and 4b in the table in the text. Other parameters (back bed, stitch cam, racking, speed) are taken from the parameter table at compile time. Example values.',rowl='Row',needle='Needle')}
for lang,t in T2.items():
    cs=30
    grid=''
    for r in range(8,0,-1):
        row=motif[r-1]
        cells=''.join(f'<td style="width:{cs}px;height:{cs}px;border:1px solid #c9cfd4;background:{"#f08c58" if b=="1" else "#fff"}"></td>' for b in row)
        grid+=f'<tr><th style="border:none;font-weight:400;color:#5a6570;padding:0 8px;{"outline:2px solid #1b2430" if r==4 else ""}">{r}</th>{cells}</tr>'
    grid+='<tr><th style="border:none"></th>'+''.join(f'<td style="border:none;text-align:center;color:#5a6570;font-size:11px;padding:2px 0">{i}</td>' for i in range(1,13))+'</tr>'
    rows=''
    for r in range(1,9):
        m=motif[r-1]; base=''.join('0' if b=='1' else '1' for b in m)
        hl='background:#fff6d6;' if r==4 else ''
        rows+=f'<tr style="{hl}"><td>{r}a</td><td>→</td><td>{t["c1"]}</td><td class="mono">{base}</td></tr>'
        if '1' in m: rows+=f'<tr style="{hl}"><td>{r}b</td><td>←</td><td style="color:#c4531d">{t["c2"]}</td><td class="mono" style="color:#c4531d">{m}</td></tr>'
        else: rows+=f'<tr style="{hl}color:#9aa4ae"><td>{r}b</td><td>—</td><td>—</td><td class="mono">{"—" if lang=="zh" else "—"}</td></tr>'
    html=f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">
<div class="fig" style="--w:1060px"><p class="title">{t['title']}</p><p class="sub">{t['sub']}</p>
<div style="display:flex;gap:36px;align-items:flex-start"><table style="border-collapse:collapse">{grid}</table>
<table style="font-size:13px"><thead><tr>{''.join(f'<th>{h}</th>' for h in t['h'])}</tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">{t['note']}</p></div>'''
    open(f'k176.{lang}.html','w').write(html)
    out='../img/w_b834f1c3.png' if lang=='zh' else '../img/en/w_b834f1c3.png'
    subprocess.run(['node','../fig.js',f'k176.{lang}.html',out],check=True)
