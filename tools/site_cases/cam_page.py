"""官网“凸轮设计与制造”解决方案页（第 39 轮）：site/cases/cam.html。
右边嵌的是线上软件本身（/cam/?embed=1，挑线槽凸轮示例在转），不是截图。"""

APP = "/cam/"

EXTRA_CSS = """
  .camhero .wrap { grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.3fr); align-items: start; }
  .camframe { width: 100%; height: 560px; border: 1px solid var(--night-line); border-radius: 8px; background: var(--paper); display: block; }
  .camcta { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }
  .camcta .btn.pri { color: var(--night); }
  .camcta .btn.line { border: 1px solid var(--night-line); color: var(--night-ink); }
  .camcols { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 22px; }
  .camcols > div { border-top: 2px solid var(--accent); padding-top: 12px; }
  .camcols h3 { margin: 0 0 6px; font: 700 18px/1.4 var(--serif-zh); }
  .camcols p, .camcols li { color: var(--muted); font-size: 15px; }
  .camcols ul { margin: 6px 0 0; padding-left: 18px; }
  .camsteps { width: 100%; border-collapse: collapse; margin-top: 18px; font-size: 15px; }
  .camsteps th, .camsteps td { text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
  .camsteps th { font-weight: 600; color: var(--muted); font-size: 13px; }
  .camsteps .st { white-space: nowrap; font-size: 13px; }
  .camsteps .st.now { color: var(--ok, #2e7d5b); font-weight: 600; }
  .camsteps .st.next { color: var(--muted); }
  .camex { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }
  .camex a { display: block; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px; color: var(--ink); text-decoration: none; }
  .camex a:hover { border-color: var(--accent); }
  .camex b { display: block; font: 700 17px/1.4 var(--serif-zh); }
  .camex span.d { display: block; color: var(--muted); font-size: 14px; margin-top: 4px; }
  .sub { color: var(--muted); }
  @media (max-width: 860px) {
    .camhero .wrap, .camcols, .camex { grid-template-columns: 1fr; }
    .camframe { height: 460px; }
  }
"""

EXAMPLES = [
    ("sewing-takeup-groove", ("缝纫机挑线槽凸轮", "Sewing machine take-up groove cam"),
     ("摆动滚子从动件、形封闭槽凸轮；看槽两侧的根切和滚子换侧。", "Oscillating roller in a closed groove; both flanks checked, and where the roller changes sides.")),
    ("sewing-feed", ("送布抬牙凸轮（反例）", "Feed-lift cam (a failing case)"),
     ("5000 r/min 下弹簧压不住，从动件会跳离：看软件怎样把问题指出来。", "At 5000 r/min the spring cannot hold the follower: see how the check reports it.")),
    ("packaging-plate", ("包装机推料盘形凸轮", "Packaging machine pusher cam"),
     ("偏置直动滚子从动件，带载荷、弹簧和转速，校核全做。", "Offset translating roller follower with load, spring and speed; every check runs.")),
]

STEPS = [
    (("设计与校核", "Design and checks"),
     ("8 种运动规律拼运动程序；盘形凸轮（直动 / 摆动，滚子 / 平底 / 尖顶）和槽凸轮；压力角、根切、曲率、接触应力、高速跳离、驱动力矩；最小基圆；计算书",
      "Motion programs from 8 laws; disk cams (translating or oscillating; roller, flat or knife-edge) and groove cams; pressure angle, undercut, curvature, contact stress, jump speed, drive torque; minimum base radius; calculation sheet"),
     "now"),
    (("加工程序与误差补偿", "Machining programs and error compensation"),
     ("磨床 X–C 程序、铣削程序、DXF；程序仿真；STEP 模型；导入实测廓线，谐波分解、加速度误差、补偿磨削程序",
      "Grinder X–C and milling programs, DXF; program simulation; STEP models; measured profiles in, harmonic breakdown, acceleration error, compensated grinding programs"),
     "next"),
    (("空间凸轮", "Spatial cams"),
     ("圆柱凸轮、弧面分度凸轮：包络齿面、接触与干涉检查、三维模型、四轴程序",
      "Cylindrical and globoidal indexing cams: enveloped flanks, contact and interference checks, 3D models, 4-axis programs"),
     "next"),
    (("FreeCAD 工作台与 AI 起草", "FreeCAD workbench and AI drafts"),
     ("同一个计算内核进 FreeCAD；一句话要求变成运动程序草稿，由代码检查后人确认",
      "The same kernel inside FreeCAD; a one-sentence requirement becomes a draft motion program, checked by code and confirmed by you"),
     "next"),
]


def page(head, topbar, bi, script):
    crumb = f'<a href="/#solutions">{bi(("解决方案", "Solutions"))}</a> › {bi(("凸轮设计与制造", "Cam design and manufacturing"))}'
    mail = "mailto:info@wenquestrobotics.com?subject=%E5%87%B8%E8%BD%AE%E8%BD%AF%E4%BB%B6%E6%BC%94%E7%A4%BA%20%2F%20Cam%20software%20demo"
    feats = [
        (("从运动要求出发", "Start from the motion"),
         ("先定从动件什么时候升、升多少、停多久，再选运动规律；廓线由程序算出来，段与段之间速度、加速度连不连续当场标出。",
          "Say when the follower rises, how far and how long it dwells, then pick the motion laws; the profile is computed, and any jump in velocity or acceleration between segments is marked at once.")),
        (("校核写得进计算书", "Checks that go in the calc sheet"),
         ("合格、不合格、未知三种结论，全部由确定性程序计算；缺数据就是“未知”，不算合格。许用值由你填，软件不编。",
          "Pass, fail or unknown, all computed by deterministic code; missing data means unknown, never a pass. Allowable values come from you; the software does not invent them.")),
        (("高速下跑不跑得住", "Will it hold at speed"),
         ("给转速、质量、弹簧，算出不跳离的最高转速、凸轮上的力和驱动力矩；缝纫机、包装机这类高速凸轮最要紧的一项。",
          "Give speed, mass and spring and it finds the highest speed without jump, the force on the cam and the drive torque: what matters most for sewing and packaging machines.")),
    ]
    fcols = "".join(f"<div><h3>{bi(h)}</h3><p>{bi(t)}</p></div>" for h, t in feats)
    excards = "".join(f'<a href="{APP}?example={eid}" target="_blank" rel="noopener"><b>{bi(t)}</b><span class="d">{bi(d)}</span></a>'
                      for eid, t, d in EXAMPLES)
    rows = "".join(
        f'<tr><td><b>{bi(n)}</b></td><td>{bi(d)}</td><td class="st {s}">{bi(("已上线", "Online") if s == "now" else ("开发中", "In development"))}</td></tr>'
        for n, d, s in STEPS)
    return f"""{head("凸轮设计与制造", "Cam design and manufacturing", "", False)}<style>{EXTRA_CSS}</style>
{topbar(crumb, False)}
<div class="hero camhero"><div class="wrap">
  <div>
    <p class="eyebrow">{bi(("解决方案 · 问渠凸轮", "Solutions · WenQuest Cam"))}</p>
    <h1>{bi(("从运动要求到凸轮廓线，一路校核到计算书", "From motion requirements to the cam profile, checked all the way to the calc sheet"))}</h1>
    <p class="lede">{bi(("问渠凸轮在浏览器里用，不用安装。编运动程序，凸轮当场转给你看；压力角、根切、接触应力、高速跳离逐项给出结论，导出计算书。右边就是软件本身，挑线槽凸轮示例正在转。",
                       "WenQuest Cam runs in the browser; nothing to install. Edit the motion program and watch the cam turn; pressure angle, undercut, contact stress and jump speed each get a verdict, and the calculation sheet exports to PDF. On the right is the software itself, turning the take-up groove cam example."))}</p>
    <div class="camcta">
      <a class="btn pri" href="{APP}" target="_blank" rel="noopener">{bi(("打开软件", "Open the software"))}</a>
      <a class="btn line" href="{mail}">{bi(("预约演示", "Book a demo"))}</a>
    </div>
    <p class="sub" style="margin-top:14px;font-size:14px">{bi(("演示免登录，项目存在你自己的浏览器里，也可以存成文件。", "No sign-in for the demo: projects stay in your own browser, or save them as a file."))}</p>
  </div>
  <div><iframe class="camframe" src="{APP}?example=sewing-takeup-groove&amp;embed=1" title="问渠凸轮 WenQuest Cam" loading="lazy"></iframe></div>
</div></div>

<section><div class="wrap">
  <h2>{bi(("能做什么", "What it does"))}</h2>
  <div class="camcols">{fcols}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <h2>{bi(("打开一个示例", "Open an example"))}</h2>
  <p class="sub">{bi(("示例参数均为虚构，仅作演示。", "Example parameters are fictional, for demonstration only."))}</p>
  <div class="camex">{excards}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <h2>{bi(("现在能用的和接下来的", "Available now and coming next"))}</h2>
  <table class="camsteps"><thead><tr><th>{bi(("部分", "Part"))}</th><th>{bi(("内容", "What it covers"))}</th><th>{bi(("状态", "Status"))}</th></tr></thead><tbody>{rows}</tbody></table>
  <p class="sub" style="margin-top:14px;max-width:52em">{bi(("算法依据 Norton《Cam Design and Manufacturing Handbook》、Chen《Mechanics and Design of Cam Mechanisms》、Angeles 与 López-Cajún《Optimization of Cam Mechanisms》等专著；每个计算模块带标准题，和闭式解对照。",
                                                     "Methods follow Norton's Cam Design and Manufacturing Handbook, Chen's Mechanics and Design of Cam Mechanisms, Angeles and López-Cajún's Optimization of Cam Mechanisms and other monographs; every module carries standard problems checked against closed-form results."))}</p>
</div></section>
<footer><div class="wrap">{bi(("教学版免费；加工程序、误差补偿和 FreeCAD 工作台属于企业版。企业自己的凸轮规范、机床和测量仪可以接进来，按项目报价。",
                              "Free for teaching; machining programs, error compensation and the FreeCAD workbench are in the enterprise edition. Your own cam standards, machines and measuring instruments can be connected, quoted per project."))}</div></footer>
<script>
{script.split("/*LANG-END*/")[0]}
</script>
</body>
</html>
"""
