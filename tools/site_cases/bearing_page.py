"""官网“轴承设计与制造”解决方案页（第 64 轮第 2 步）：site/cases/bearing.html。
右边嵌的是线上软件本身（/bearing/?embed=1，角接触球轴承示例），不是截图。"""

APP = "/bearing/"

EXTRA_CSS = """
  .brhero .wrap { grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.3fr); align-items: start; }
  .brframe { width: 100%; height: 560px; border: 1px solid var(--night-line); border-radius: 8px; background: var(--paper); display: block; }
  .brcta { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }
  .brcta .btn.pri { color: var(--night); }
  .brcta .btn.line { border: 1px solid var(--night-line); color: var(--night-ink); }
  .brcols { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 22px; }
  .brcols > div { border-top: 2px solid var(--accent); padding-top: 12px; }
  .brcols h3 { margin: 0 0 6px; font: 700 18px/1.4 var(--serif-zh); }
  .brcols p, .brcols li { color: var(--muted); font-size: 15px; }
  .brcols ul { margin: 6px 0 0; padding-left: 18px; }
  .brsteps { width: 100%; border-collapse: collapse; margin-top: 18px; font-size: 15px; }
  .brsteps th, .brsteps td { text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
  .brsteps th { font-weight: 600; color: var(--muted); font-size: 13px; }
  .brsteps .st { white-space: nowrap; font-size: 13px; }
  .brsteps .st.now { color: var(--ok, #2e7d5b); font-weight: 600; }
  .brsteps .st.next { color: var(--muted); }
  .brex { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
  .brex a { display: block; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px; color: var(--ink); text-decoration: none; }
  .brex a:hover { border-color: var(--accent); }
  .brex b { display: block; font: 700 17px/1.4 var(--serif-zh); }
  .brex span.d { display: block; color: var(--muted); font-size: 14px; margin-top: 4px; }
  .sub { color: var(--muted); }
  @media (max-width: 860px) {
    .brhero .wrap, .brcols, .brex { grid-template-columns: 1fr; }
    .brframe { height: 460px; }
  }
"""

EXAMPLES = [
    ("demo-deep-groove", ("减速器输入轴深沟球轴承", "Deep groove ball bearing on a gearbox input shaft"),
     ("径向力加少量轴向力；轴过盈配合、内外圈温差后的工作游隙。", "Radial with a little axial force; operating clearance after the shaft fit and ring temperatures.")),
    ("demo-angular", ("主轴角接触球轴承", "Angular contact ball bearing on a spindle"),
     ("轴向力为主的联合载荷，8000 r/min 的油膜和故障频率。", "Mostly axial combined load; film and fault frequencies at 8000 r/min.")),
]

STEPS = [
    (("设计与校核（深沟球、角接触球）", "Design and checks (deep groove and angular contact ball bearings)"),
     ("钢球与沟道几何；静力学载荷分布（每个钢球的载荷和接触角）；赫兹接触应力与接触椭圆；接触椭圆是否越过挡肩；初始 → 装配 → 温差的游隙链；油膜厚度与 λ；故障特征频率；剖面图与计算书",
      "Ball and groove geometry; static load distribution (load and contact angle of every ball); Hertz contact stress and the contact ellipse; whether the ellipse runs over the shoulder; the clearance chain from initial to mounted to operating; film thickness and λ; fault frequencies; section drawing and calculation report"),
     "now"),
    (("典型应用场景", "Typical applications"),
     ("减速器齿轮轴、电机转子、机床主轴、汽车轮毂、机器人关节、凸轮轴：由设备参数算出轴承上的力，多工况载荷谱，一圈内变化的力；静强度与疲劳分开判",
      "Gearbox shafts, motor rotors, machine tool spindles, wheel hubs, robot joints, camshafts: the bearing loads worked out from the machine data, load spectra, forces that change round the turn; static strength and fatigue judged separately"),
     "now"),
    (("额定载荷与寿命", "Load ratings and life"),
     ("按 GB/T 6391、GB/T 4662 与 ISO 16281 计算；标准正文购买并录入前，结果显示“未知”",
      "Following GB/T 6391, GB/T 4662 and ISO 16281; until the purchased standard texts are entered, these show “unknown”"),
     "next"),
    (("圆柱滚子轴承", "Cylindrical roller bearings"),
     ("切片法算沿滚子长度的接触应力；滚子凸度（圆弧、直线加圆弧、实测点表）；内外圈倾斜；两端是否受载",
      "Contact stress along the roller by slices; roller crown (arc, flat with arcs, measured points); ring misalignment; whether the roller ends take load"),
     "now"),
    (("圆锥滚子轴承（单列）", "Tapered roller bearings (one row)"),
     ("滚子的受力平衡（外圈、内圈、挡边）、沿滚子长度的接触应力、挡边力与挡边接触应力",
      "Roller equilibrium (cup, cone, rib), contact stress along the roller, rib force and rib contact stress"),
     "now"),
    (("圆锥滚子轴承：成对与预紧", "Tapered roller bearings: pairs and preload"),
     ("背对背、面对面成对，或轴两端各一个；按安装时调的轴向游隙（或预紧力）算两列各分担多少、预紧是否够、刚度，画调整量曲线；不用目录的 Y 值",
      "Back to back, face to face, or one at each end of the shaft; from the end play (or preload) set at mounting: what each row carries, whether the preload holds, stiffness, and an end play sweep; no catalogue Y factors"),
     "now"),
    (("角接触球轴承：高速与成对预紧", "Angular contact ball bearings: speed and paired preload"),
     ("离心力下内外圈接触角分开；背对背、面对面、串联成对安装与预紧，两列受力、预紧是否够、轴向与径向刚度",
      "Inner and outer contact angles split by centrifugal force; back-to-back, face-to-face and tandem pairs with preload: the load on each row, whether the preload holds, axial and radial stiffness"),
     "now"),
    (("合套选配", "Selective assembly"),
     ("按实测的内外圈沟径和钢球分组逐件配对：配成套数最多、游隙靠近目标；与分组配套对照，列出配不上的件和原因",
      "Measured raceway diameters and ball groups matched piece by piece: the most sets, clearances nearest the target; compared with size classes, with the leftovers and why"),
     "now"),
    (("检测与 SPC", "Inspection and SPC"),
     ("沟道圆度与波纹度的谐波分析；均值–极差、均值–标准差、单值–移动极差控制图，Nelson 八条判异，Cp、Cpk、Pp、Ppk",
      "Harmonic analysis of raceway roundness and waviness; mean–range, mean–s and individuals charts, Nelson's eight tests, Cp, Cpk, Pp, Ppk"),
     "now"),
    (("零件图与三维", "Part drawings and 3D"),
     ("内圈、外圈、滚动体截面图与 DXF，整套与单件 STEP（由程序直接写出，经 OpenCASCADE 核对体积）",
      "Sections of the rings and rolling elements with DXF, STEP of the bearing and of each part (written directly, volumes checked with OpenCASCADE)"),
     "now"),
    (("工艺路线与工序卡", "Process routes and operation sheets"),
     ("内外圈工序链（车削、热处理、磨削、超精……可增删）；按成品尺寸和企业自己的留量倒推每道工序尺寸，算最小与最大留量（含上道公差、热处理波动与变形），可打印的工序卡；软件不给默认值",
      "Ring operation chains (turning, heat treatment, grinding, superfinishing… edit freely); each operation size worked back from the finished part with your own allowances, smallest and largest stock (with the preceding tolerance, heat-treatment scatter and distortion), printable operation sheets; no default values"),
     "now"),
    (("FreeCAD 工作台", "FreeCAD workbench"),
     ("在 FreeCAD 1.1 里填参数（与网页版同样的字段、通用的项目文件）、校核（同一个内核，结果逐项相同）、建精确实体与整套装配、查干涉、出零件工作图和每道磨削工序的工序简图",
      "In FreeCAD 1.1: the same fields and project files as the web app, the same checks (one kernel, identical results), exact solids and the assembled bearing, an interference check, working drawings and a sketch for every grinding operation"),
     "now"),
    (("云端项目与 AI 起草", "Cloud projects and AI drafts"),
     ("开通的企业把设计项目和工艺模板存到云端，同单位共用、留 20 版、不互相覆盖；AI 用一句话起草应用场景、解释校核结果、起草设计说明，数字逐个由代码核对，人点“采用”才进项目",
      "Activated companies keep design projects and process templates in the cloud, shared, 20 versions kept, no overwriting; AI drafts the application from one sentence, explains the checks and drafts the design description, every number checked by code, adopted only by a person"),
     "now"),
]


def page(head, topbar, bi, script):
    crumb = f'<a href="/#solutions">{bi(("解决方案", "Solutions"))}</a> › {bi(("轴承设计与制造", "Bearing design and manufacturing"))}'
    mail = "mailto:info@wenquestrobotics.com?subject=%E8%BD%B4%E6%89%BF%E8%BD%AF%E4%BB%B6%E6%BC%94%E7%A4%BA%20%2F%20Bearing%20software%20demo"
    feats = [
        (("从载荷到每个钢球", "From the loads to every ball"),
         ("径向力、轴向力和力矩一起作用时，按内外圈的相对位移解出每个钢球的载荷和工作接触角；深沟球轴承按装配和温差后的工作游隙计算。",
          "With radial force, axial force and moment acting together, the relative displacement of the rings gives each ball’s load and operating contact angle; deep groove bearings are worked at the operating clearance after fitting and temperature.")),
        (("接触与润滑", "Contact and lubrication"),
         ("赫兹点接触用椭圆积分精确求解，给出最大接触应力和接触椭圆；检查椭圆是否越过挡肩；按 Hamrock–Dowson 公式算最小油膜厚度和 λ。",
          "Hertz point contact solved exactly with elliptic integrals gives the peak contact stress and the contact ellipse; the ellipse is checked against the shoulder; Hamrock–Dowson gives the minimum film thickness and λ.")),
        (("缺数据就说“未知”", "Missing data says “unknown”"),
         ("许用应力、最小壁厚等限值由企业按自己的标准填写；没有限值或缺数据的项显示“未知”，不会判为合格。额定载荷和寿命等国家标准正文录入后再算。",
          "Limits such as allowed stress and smallest wall come from your own standards; a check without its limit or data shows “unknown”, never a pass. Load ratings and life wait for the national standard texts to be entered.")),
    ]
    fcols = "".join(f"<div><h3>{bi(h)}</h3><p>{bi(t)}</p></div>" for h, t in feats)
    excards = "".join(f'<a href="{APP}?example={eid}" target="_blank" rel="noopener"><b>{bi(t)}</b><span class="d">{bi(d)}</span></a>'
                      for eid, t, d in EXAMPLES)
    rows = "".join(
        f'<tr><td><b>{bi(n)}</b></td><td>{bi(d)}</td><td class="st {s}">{bi(("已上线", "Online") if s == "now" else ("接下来", "Coming next"))}</td></tr>'
        for n, d, s in STEPS)
    return f"""{head("轴承设计与制造", "Bearing design and manufacturing", "", False)}<style>{EXTRA_CSS}</style>
{topbar(crumb, False)}
<div class="hero brhero"><div class="wrap">
  <div>
    <p class="eyebrow">{bi(("解决方案 · 问渠轴承", "Solutions · WenQuest Bearing"))}</p>
    <h1>{bi(("每个钢球受多大力，一眼看清", "See the load on every ball"))}</h1>
    <p class="lede">{bi(("给轴承厂的设计校核软件。问渠轴承在浏览器里用，不用安装。填尺寸、钢球、沟道和载荷，当场算出每个钢球的载荷、接触应力、接触椭圆、工作游隙、油膜和故障频率，逐项给出结论，导出计算书。右边就是软件本身。",
                       "Design checks for bearing makers. WenQuest Bearing runs in the browser; nothing to install. Enter the sizes, balls, grooves and loads, and it works out the load on every ball, contact stress, contact ellipse, operating clearance, oil film and fault frequencies, gives each a verdict and exports the calculation report. On the right is the software itself."))}</p>
    <div class="brcta">
      <a class="btn pri" href="{APP}" target="_blank" rel="noopener">{bi(("打开软件", "Open the software"))}</a>
      <a class="btn line" href="{mail}">{bi(("预约演示", "Book a demo"))}</a>
    </div>
    <p class="sub" style="margin-top:14px;font-size:14px">{bi(("演示免登录，项目存在你自己的浏览器里，也可以存成文件。", "No sign-in for the demo: projects stay in your own browser, or save them as a file."))}</p>
  </div>
  <div><iframe class="brframe" src="{APP}?example=demo-angular&amp;embed=1" title="问渠轴承 WenQuest Bearing" loading="lazy"></iframe></div>
</div></div>

<section><div class="wrap">
  <h2>{bi(("能做什么", "What it does"))}</h2>
  <div class="brcols">{fcols}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <h2>{bi(("打开一个示例", "Open an example"))}</h2>
  <p class="sub">{bi(("示例尺寸和参数均为虚构，不是任何厂家或标准中的型号。", "Example sizes and data are fictional: not any maker’s or any standard’s bearing."))}</p>
  <div class="brex">{excards}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <h2>{bi(("现在能用的和接下来的", "Available now and coming next"))}</h2>
  <table class="brsteps"><thead><tr><th>{bi(("部分", "Part"))}</th><th>{bi(("内容", "What it covers"))}</th><th>{bi(("状态", "Status"))}</th></tr></thead><tbody>{rows}</tbody></table>
  <p class="sub" style="margin-top:14px;max-width:52em">{bi(("算法依据 Harris 与 Kotzalas《Rolling Bearing Analysis》、Johnson《Contact Mechanics》、Hamrock 与 Dowson《Ball Bearing Lubrication》；每个计算模块带标准题，和闭式解或公开公式对照。",
                                                     "Methods follow Harris and Kotzalas, Rolling Bearing Analysis; Johnson, Contact Mechanics; Hamrock and Dowson, Ball Bearing Lubrication; every module carries standard problems checked against closed forms or published formulas."))}</p>
</div></section>
<footer><div class="wrap">{bi(("教学版免费；制造、FreeCAD 工作台和企业自己的标准接入属于企业版，按项目报价。",
                              "Free for teaching; manufacturing, the FreeCAD workbench and connecting your own standards are in the enterprise edition, quoted per project."))}</div></footer>
<script>
{script.split("/*LANG-END*/")[0]}
</script>
</body>
</html>
"""
