"""官网“三维仿真视频”解决方案页（第 38 轮）：site/cases/video3d.html。
样片视频是 video3d.yml 勾选“同时出网页版”后挂在发布页 video3d-samples 的 720p 版，下载到 site/cases/video3d/。"""

SAMPLES = [
    ("hook-loop-machine", ("平缝机一针：从机头到线结", "One stitch: from the machine head to the knot"),
     ("整机转起来 → 去外盖 → 跟着机针钻到针板下 → 旋梭钩住线环、套过梭壳 → 在布中间扣成线结 → 回到整机。连看实物都难懂的一下，讲清楚了。",
      "The whole machine runs → covers off → follow the needle below the plate → the hook catches the loop and carries it round the bobbin case → the threads lock inside the cloth → back to the machine. The step that is hard to see even on a real machine, made clear.")),
    ("lockstitch-one-stitch", ("平缝机怎样缝一针", "How a lockstitch machine makes one stitch"),
     ("剖开机壳，看上轴、针杆、挑线杆、下轴、旋梭怎样配合；慢放约 2000 倍，右侧读数和针尖高度曲线跟着机构实时走。",
      "The casing cut open: main shaft, needle bar, take-up, lower shaft and hook working together, about 2000× slower, with live readouts and the needle-height curve.")),
    ("arm-pick-place", ("六轴机械臂抓取放料", "Six-axis arm pick and place"),
     ("逆运动学算出每个关节角；透视看到关节里的电机和减速器，关节角面板逐帧跟着走。",
      "Every joint angle computed by inverse kinematics; X-ray shows the motors and reducers inside the joints, with the joint panel following frame by frame.")),
    ("lockstitch-cinematic", ("写实版：一针 12 毫秒", "Cinematic: one stitch in 12 ms"),
     ("同一台平缝机，换成写实光照、景深和配音，适合产品展示和宣传。",
      "The same machine with realistic lighting, depth of field and narration, for product showcases and promotion.")),
]

EXTRA_CSS = """
  .v3hero .wrap { grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.25fr); }
  .v3hero video, .v3card video { width: 100%; display: block; border-radius: 6px; background: #000; border: 1px solid var(--night-line); }
  .v3grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 22px; margin-top: 22px; }
  .v3card { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px; }
  .v3card video { border-color: var(--line); }
  .v3card b { display: block; margin-top: 12px; font: 700 18px/1.4 var(--serif-zh); }
  .v3card p { margin: 6px 0 0; color: var(--muted); font-size: 15px; }
  .v3cols { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 22px; }
  .v3cols > div { border-top: 2px solid var(--accent); padding-top: 12px; }
  .v3cols h3 { margin: 0 0 6px; font: 700 18px/1.4 var(--serif-zh); }
  .v3cols p, .v3cols li { color: var(--muted); font-size: 15px; }
  .v3cols ul { margin: 6px 0 0; padding-left: 18px; }
  .v3quote { margin: 0; font: 700 clamp(22px, 2.6vw, 30px)/1.4 var(--serif-zh); }
  .v3who { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 22px; }
  .v3who > div { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 18px; }
  .v3who h3 { margin: 0 0 4px; font: 700 20px/1.4 var(--serif-zh); }
  .v3who .tagl { font: 500 12px/1 var(--mono); letter-spacing: .12em; color: var(--accent-ink); text-transform: uppercase; }
  .v3who ul { margin: 10px 0 14px; padding-left: 18px; color: var(--muted); }
  .v3who .btn.pri { color: var(--night); }
  .v3who .btn.line { border: 1px solid var(--line); color: var(--ink); }
  .sub { color: var(--muted); }
  @media (max-width: 860px) { .v3hero .wrap, .v3grid, .v3cols, .v3who { grid-template-columns: 1fr; } }
"""


def video(slug, autoplay=False):
    a = ' autoplay muted loop playsinline' if autoplay else ' controls playsinline'
    return (f'<video preload="{"auto" if autoplay else "none"}"{a} poster="video3d/{slug}.jpg">'
            f'<source src="video3d/{slug}.mp4" type="video/mp4"></video>')


def page(head, topbar, bi, script):
    cards = "".join(f"""<div class="v3card">{video(slug)}<b>{bi(title)}</b><p>{bi(desc)}</p></div>""" for slug, title, desc in SAMPLES)
    crumb = f'<a href="/#solutions">{bi(("解决方案", "Solutions"))}</a> › {bi(("三维仿真视频", "3D simulation video"))}'
    mail = "mailto:info@wenquestrobotics.com?subject=%E4%B8%89%E7%BB%B4%E4%BB%BF%E7%9C%9F%E8%A7%86%E9%A2%91%E5%BC%80%E9%80%9A%20%2F%203D%20video%20access"
    feats = [
        (("动作是算出来的", "Motion is computed"),
         ("机械臂按逆运动学、整机按虚拟样机的机构计算，读数可信，能写进报告和课件；不是动画师手调的。",
          "Arms follow inverse kinematics and machines their own mechanism model, so the numbers can go into reports and courses. Nothing is hand-keyed.")),
        (("看得见里面", "See inside"),
         ("剖开、透视、慢放、特写、读数面板和曲线，按讲解需要组合；中英标注，可加配音。",
          "Cutaways, X-ray, slow motion, close-ups, readout panels and curves, combined as the explanation needs; bilingual labels and optional narration.")),
        (("一句话，几分钟", "One sentence, minutes"),
         ("说要什么，AI 写场景；先看关键画面（1–2 分钟），再出小样（约 10 分钟）和高清（约 30 分钟）。逐条提意见，AI 改。",
          "Say what you want and the AI writes the scene; key frames in 1–2 minutes, a draft in about 10 minutes and HD in about 30. Give feedback and the AI revises.")),
    ]
    fcols = "".join(f"<div><h3>{bi(h)}</h3><p>{bi(t)}</p></div>" for h, t in feats)
    return f"""{head("三维仿真视频", "3D simulation video", "", False)}<style>{EXTRA_CSS}</style>
{topbar(crumb, False)}
<div class="hero v3hero"><div class="wrap">
  <div>
    <p class="eyebrow">{bi(("解决方案 · 三维仿真视频", "Solutions · 3D simulation video"))}</p>
    <h1>{bi(("一句话，要一段工程级三维仿真视频", "One sentence, one engineering-grade 3D simulation video"))}</h1>
    <p class="lede">{bi(("机构怎么动、零件里面发生了什么、为什么这样设计——用平台已有的模型和算出来的运动，自动出讲解视频。不用装软件，浏览器里用。",
                       "How a mechanism moves, what happens inside, why it is designed that way: explanation videos made automatically from the platform's models and computed motion. Nothing to install; it runs in the browser."))}</p>
    <dl class="facts">
      <div><dt>{bi(("关键画面", "Key frames"))}</dt><dd>1–2<small>{bi(("分钟", "min"))}</small></dd></div>
      <div><dt>{bi(("小样", "Draft"))}</dt><dd>~10<small>{bi(("分钟", "min"))}</small></dd></div>
      <div><dt>{bi(("高清", "HD"))}</dt><dd>1080<small>p</small></dd></div>
      <div><dt>{bi(("标注", "Labels"))}</dt><dd>{bi(("中英", "ZH·EN"))}</dd></div>
    </dl>
  </div>
  <div>{video(SAMPLES[0][0], autoplay=True)}</div>
</div></div>

<section><div class="wrap">
  <h2>{bi(("样片", "Samples"))}</h2>
  <p class="sub">{bi(("全部由平台按场景文件自动渲染，没有手工剪辑。", "All rendered automatically from scene files; no manual editing."))}</p>
  <div class="v3grid">{cards}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <h2>{bi(("能做什么", "What it does"))}</h2>
  <div class="v3cols">{fcols}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <p class="v3quote">{bi(("SolidWorks 负责设计和算，问渠负责讲出来、教出去。", "SolidWorks designs and computes; WenQuest explains and teaches."))}</p>
  <p class="sub" style="max-width:52em">{bi(("我们不和 SolidWorks、ADAMS、RoboDK 等比求解和建模。它们出的是动画本身，讲解字幕、中英标注、读数、配音还要另外做，一段一段手调；我们补的是这一段：不会这些软件的老师、学生、销售也能一句话出片，可以批量出，直接插进课件和白板课。企业的装配可以导出 STEP 交给我们接入。",
                                    "We do not compete with SolidWorks, ADAMS or RoboDK on solving or modelling. They produce the animation itself; captions, bilingual labels, readouts and narration still have to be added by hand, clip by clip. We fill that gap: teachers, students and sales staff who do not use those tools get a video from one sentence, in batches, ready for slides and whiteboard lectures. Company assemblies can be brought in by sending us a STEP export."))}</p>
</div></section>

<section style="padding-top:0"><div class="wrap">
  <h2>{bi(("给谁用、怎样开通", "Who it is for and how to start"))}</h2>
  <div class="v3who">
    <div>
      <span class="tagl">{bi(("学校", "Schools"))}</span>
      <h3>{bi(("老师：课件和讲课视频", "Teachers: slides and lecture videos"))}</h3>
      <ul>
        <li>{bi(("登录学习平台，左侧菜单“三维视频”就能用", "Sign in to the learning platform and open “3D video” in the menu"))}</li>
        <li>{bi(("开课用免费", "Free for courses you teach"))}</li>
        <li>{bi(("出好的视频可插进白板课和网页课件", "Finished videos go straight into whiteboard lectures and web slides"))}</li>
      </ul>
      <a class="btn pri" href="https://learn.wenquestrobotics.com/" target="_blank" rel="noopener">{bi(("去学习平台", "Open the platform"))}</a>
    </div>
    <div>
      <span class="tagl">{bi(("企业", "Companies"))}</span>
      <h3>{bi(("产品展示、投标、操作培训、售后说明", "Showcases, bids, operator training, service guides"))}</h3>
      <ul>
        <li>{bi(("申请开通后，在学习平台里自助出片", "Once enabled, make videos yourself on the platform"))}</li>
        <li>{bi(("按使用时间计费", "Billed by usage time"))}</li>
        <li>{bi(("没有现成模型的产品，可以接入你的 STEP 装配或为你定制机构模型", "No model yet? Bring your STEP assembly, or we build the mechanism model for you"))}</li>
      </ul>
      <a class="btn pri" href="{mail}">{bi(("申请开通", "Request access"))}</a>
    </div>
  </div>
</div></section>
<footer><div class="wrap">{bi(("只在已有模型上做：AI 挑模型、填参数、编动作、定镜头和标注，不凭空生成几何形状。学生账号不能使用。",
                              "Built only on existing models: the AI picks models, fills in parameters, plans motion, camera and labels; it never invents geometry. Not available to student accounts."))}</div></footer>
<script>
{script.split("/*LANG-END*/")[0]}
</script>
</body>
</html>
"""
