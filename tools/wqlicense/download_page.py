"""第 175 轮：问渠软件下载中心（测试版）。美国版 site/download/index.html（本程序写），国内版 site/cn/download/index.html
（tools/site_cn/build.py 调 render("cn") 写）。中英两种文字都在页里，右上角切换。

版本、大小、校验码在浏览器里读 /download/versions.json（tools/wqlicense/pack.py 写）；“领取一年测试授权”先用全站登录的
cookie 换令牌（/api/v1/auth/sso），再调 /api/v1/license/beta。
国内版：不出现境外服务名、不放外链（问渠 CAD 国内下载地址开通前显示“准备中”）；AI 只写国内可用的模型。

    python3 tools/wqlicense/download_page.py          # 写美国版
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def T(zh: str, en: str) -> str:
    return f'<span data-zh>{zh}</span><span data-en>{en}</span>'


CSS = """
:root{--paper:#f4f2ec;--ink:#121c21;--muted:#56656b;--line:#d6d2c6;--accent:#f2b705;--card:#fffdf7;--ok:#2e7d4f}
@media (prefers-color-scheme:dark){:root{--paper:#0f181c;--ink:#e6ecee;--muted:#93a3a9;--line:#2a3a41;--card:#152126;--ok:#5cc28a}}
*{box-sizing:border-box}[hidden]{display:none!important}
body{margin:0;background:var(--paper);color:var(--ink);font:400 16px/1.75 "IBM Plex Sans","Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif}
main{max-width:1040px;margin:0 auto;padding:24px 16px 72px}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.top a{color:var(--muted);text-decoration:none;font-size:14px}
button,.btn{font:inherit;font-size:14px;background:none;color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:6px 14px;cursor:pointer;text-decoration:none;display:inline-block}
.btn.pri,button.pri{background:var(--accent);border-color:var(--accent);color:#121c21;font-weight:600}
h1{font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:32px;line-height:1.3;margin:26px 0 6px}
h2{font-size:21px;margin:40px 0 10px}h3{font-size:17px;margin:22px 0 6px}
.lead{color:var(--muted);max-width:760px}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:22px 0}
.steps div{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}.steps b{display:block;font-size:13px;color:var(--muted)}
.lic{background:var(--card);border:2px solid var(--accent);border-radius:16px;padding:16px 18px;margin:18px 0}
.lic code{display:block;word-break:break-all;background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:12.5px;margin:8px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;display:flex;flex-direction:column;gap:6px}
.card h3{margin:0}.card .meta{font-size:13px;color:var(--muted)}.card .sha{font-size:11px;color:var(--muted);word-break:break-all}
.card .row{display:flex;gap:8px;flex-wrap:wrap;margin-top:auto;padding-top:8px}
.tag{font-size:12px;border-radius:999px;padding:1px 9px;background:var(--paper);border:1px solid var(--line);color:var(--muted)}
.tut{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:6px 20px 14px;margin:14px 0}
ol li{margin:4px 0}kbd{font-family:ui-monospace,Menlo,monospace;font-size:13px;background:var(--paper);border:1px solid var(--line);border-radius:5px;padding:0 5px}
.note{font-size:14px;color:var(--muted)}
html:not([lang="en"]) [data-en],html[lang="en"] [data-zh]{display:none!important}
"""


def tutorials(region: str) -> str:
    cn = region == "cn"
    ai_key = (T("AI 功能在国内用 DeepSeek：在 Windows 设置环境变量 <kbd>DEEPSEEK_API_KEY</kbd>（自己的密钥，不要发给别人）。",
                "In China the AI features use DeepSeek: set the environment variable <kbd>DEEPSEEK_API_KEY</kbd> to your own key.")
              if cn else
              T("AI 功能要一个模型密钥：在美国设 <kbd>ANTHROPIC_API_KEY</kbd>，在国内设 <kbd>DEEPSEEK_API_KEY</kbd>（软件按地区自动切换）。",
                "AI features need a model key: <kbd>ANTHROPIC_API_KEY</kbd> in the US, <kbd>DEEPSEEK_API_KEY</kbd> in China (switched automatically by region)."))
    return f"""
<h2 id="tut-cad">{T("安装教程 · 问渠 CAD、问渠有限元、问渠多体动力学（Windows）", "Install guide · WenQuest CAD, FEA, MBD (Windows)")}</h2>
<div class="tut">
<h3>{T("电脑要求", "Requirements")}</h3>
<p>{T("Windows 10 / 11（64 位）；内存 8 GB 以上（16 GB 更好）；硬盘留 8 GB；首次打开 AI 功能要联网。",
      "Windows 10 / 11 (64-bit); 8 GB RAM or more (16 GB better); 8 GB free disk; internet for the AI features.")}</p>
<h3>{T("安装", "Install")}</h3>
<ol>
<li>{T("下载 <b>WenQuestCAD-…-Setup.exe</b>（约 1.4 GB）。可以用页面上的校验码核对文件是否完整。", "Download <b>WenQuestCAD-…-Setup.exe</b> (about 1.4 GB); you can check it against the SHA-256 shown.")}</li>
<li>{T("双击运行。测试版没有买代码签名证书，Windows 多半会拦一下——照下面“<a href=\"#unblock\">Windows 不让装怎么办</a>”一步步做，几分钟就能装上。",
      "Run it. The beta has no code-signing certificate, so Windows will probably stop it once — follow “<a href=\"#unblock\">Windows won't let me install</a>” below; it takes a few minutes.")}</li>
<li>{T("选语言 → 同意使用说明与许可 → 选安装位置（默认即可）→ 安装，约 3–5 分钟。", "Pick a language → accept the terms → choose a folder (the default is fine) → Install, about 3–5 minutes.")}</li>
<li>{T("装完桌面上有<b>问渠 CAD</b>，双击打开；窗口标题是 “WenQuest CAD 1.1.4”。", "A <b>WenQuest CAD</b> shortcut appears on the desktop; the window title reads “WenQuest CAD 1.1.4”.")}</li>
</ol>
<h3 id="unblock">{T("Windows 不让装怎么办（按你看到的提示找）", "Windows won't let me install (find the message you see)")}</h3>
<ol>
<li><b>{T("浏览器下载完就提示“通常不会下载此文件 / 可能有害”", "The browser says the file “isn't commonly downloaded / might be harmful”")}</b><br>
{T("Edge：在下载列表里这个文件右边点 <b>…</b> → <b>保留</b> → 再点 <b>显示详细信息</b> → <b>仍然保留</b>。Chrome：点 <b>保留</b>。",
   "Edge: in the downloads list click <b>…</b> next to the file → <b>Keep</b> → <b>Show more</b> → <b>Keep anyway</b>. Chrome: click <b>Keep</b>.")}</li>
<li><b>{T("双击后蓝色框“Windows 已保护你的电脑”", "Blue box “Windows protected your PC”")}</b><br>
{T("先点框里的小字 <b>更多信息</b>，下面才会出现 <b>仍要运行</b> 按钮，点它。", "Click the small <b>More info</b> link first; a <b>Run anyway</b> button appears — click it.")}</li>
<li><b>{T("框里只有“不运行 / 确定”，没有“仍要运行”", "Only “Don't run / OK”, no “Run anyway”")}</b><br>
{T("在下载文件夹里<b>右键</b>安装包 → <b>属性</b> → “常规”页最下面勾上 <b>解除锁定</b> → <b>确定</b>，再双击。",
   "In the downloads folder <b>right-click</b> the installer → <b>Properties</b> → at the bottom of the General tab tick <b>Unblock</b> → <b>OK</b>, then double-click again.")}</li>
<li><b>{T("提示“智能应用控制已阻止此应用”，或者双击没有任何反应", "“Smart App Control blocked this app”, or nothing happens")}</b><br>
{T("这是 Windows 11 的“智能应用控制”，它只放行有签名的软件。打开 <b>Windows 安全中心</b> → <b>应用和浏览器控制</b> → <b>智能应用控制设置</b> → 选 <b>关闭</b>，再装。注意：在不少 Windows 11 版本上，关掉后不能自己再打开（要重装系统才能恢复）；介意的话先别关，等有签名的正式版。",
   "This is Windows 11 Smart App Control, which only allows signed software. Open <b>Windows Security</b> → <b>App &amp; browser control</b> → <b>Smart App Control settings</b> → <b>Off</b>, then install. Note: on many Windows 11 versions it cannot be turned back on without reinstalling Windows; if that matters to you, wait for the signed release.")}</li>
<li><b>{T("杀毒软件报毒，或者安装包不见了", "The antivirus flags it, or the installer disappears")}</b><br>
{T("Windows 自带的：<b>Windows 安全中心</b> → <b>病毒和威胁防护</b> → <b>保护历史记录</b> → 点这条记录 → <b>操作</b> → <b>还原</b>（或“允许”）。别的杀毒软件在它的“隔离区 / 信任区”里恢复并信任。可以先用页面上的 SHA-256 核对文件没被改过（PowerShell：<kbd>Get-FileHash 文件名</kbd>）。",
   "Windows Defender: <b>Windows Security</b> → <b>Virus &amp; threat protection</b> → <b>Protection history</b> → open the entry → <b>Actions</b> → <b>Restore</b> (or Allow). Other antivirus: restore it from quarantine and trust it. You can first check the file against the SHA-256 on this page (PowerShell: <kbd>Get-FileHash file</kbd>).")}</li>
<li><b>{T("公司或学校的电脑", "Company or school computer")}</b><br>{T("这类电脑常常不准装没签名的软件，请找管理员。", "These often block unsigned software; ask your administrator.")}</li>
</ol>
<p class="note">{T("问渠有限元、问渠多体动力学的安装包也一样，照上面做。", "The same applies to the WenQuest FEA and WenQuest MBD installers.")}</p>
<h3>{T("输入授权码", "Enter the licence code")}</h3>
<ol>
<li>{T("在本页“领取一年测试授权”里复制授权码。", "Copy your code from “Get a one-year beta licence” on this page.")}</li>
<li>{T("装好后首次启动时会弹窗要授权码（问渠的工作台：<b>AI Parts</b>、<b>问渠</b>、<b>问渠缝纫机</b>），粘贴进去点确定；以后不再问，到期前 30 天提醒续期。",
      "The first time you start it after installing, a box asks for the code (for the WenQuest workbenches <b>AI Parts</b>, <b>WenQuest</b>, <b>WenQuest Sewing</b>); paste and OK. It is not asked again; you are reminded 30 days before it ends.")}</li>
<li>{ai_key}</li>
</ol>
<h3>{T("更新与卸载", "Update and uninstall")}</h3>
<p>{T("软件联网时会在报告视图里提示有新版本；到本页下载新的安装包，直接装在原来的位置上（授权码不用重输）。卸载：Windows 设置 → 应用 → 问渠 CAD → 卸载；授权码留在 %APPDATA%\\WenQuest\\license.txt，可以手动删。",
      "When online the software notes a new version in the report view; download the new installer here and install over the old one (no need to re-enter the code). Uninstall in Windows Settings → Apps → WenQuest CAD; the code stays in %APPDATA%\\WenQuest\\license.txt.")}</p>
</div>

<h2 id="tut-wb">{T("安装教程 · FreeCAD 工作台（缝纫机、轴承、凸轮）", "Install guide · FreeCAD workbenches (Sewing, Bearing, Cam)")}</h2>
<div class="tut">
<ol>
<li>{T("装好问渠 CAD（自带这些工作台的运行环境），或装官方 FreeCAD 1.1（Windows、macOS、Linux 都行）。",
      "Install WenQuest CAD, or the official FreeCAD 1.1 (Windows, macOS or Linux).")}</li>
<li>{T("下载工作台的 zip，解压。", "Download the workbench zip and unzip it.")}</li>
<li>{T("在 FreeCAD 里打开 Python 控制台（菜单 视图 → 面板 → Python 控制台），输入 <kbd>App.getUserAppDataDir()</kbd> 回车，显示的就是你的用户数据文件夹。",
      "In FreeCAD open the Python console (View → Panels → Python console), type <kbd>App.getUserAppDataDir()</kbd> and press Enter: that is your user data folder.")}</li>
<li>{T("把 zip 里的 <b>Mod</b> 文件夹里的东西复制到这个文件夹下的 <b>Mod</b>（没有就新建；FreeCAD 1.1 里通常是 …\\FreeCAD\\v1-1\\Mod）。",
      "Copy the contents of the zip’s <b>Mod</b> folder into <b>Mod</b> under that folder (create it if missing; in FreeCAD 1.1 it is usually …/FreeCAD/v1-1/Mod).")}</li>
<li>{T("重启 FreeCAD，在工作台列表里选它；首次会要授权码，同上。", "Restart FreeCAD and pick the workbench; the first time it asks for the licence code as above.")}</li>
</ol>
<p class="note">{T("工作台里的问渠程序是编译过的（不含源代码），要用 FreeCAD 1.1 自带的 Python 3.11。", "WenQuest code inside is compiled (no source) and needs FreeCAD 1.1’s Python 3.11.")}</p>
</div>

<h2 id="faq">{T("常见问题", "FAQ")}</h2>
<div class="tut">
<p><b>{T("测试授权收费吗？", "Is the beta licence free?")}</b> {T("不收费。注册用户每人一个，一年有效，到期可以续。", "Yes: one per registered user, valid one year, renewable.")}</p>
<p><b>{T("换电脑了怎么办？", "New computer?")}</b> {T("在本页再点一次“领取”，会显示同一个授权码，粘贴到新电脑即可。", "Click “Get” again here: it shows the same code; paste it on the new computer.")}</p>
<p><b>{T("问渠 CAD 和 FreeCAD 什么关系？", "WenQuest CAD and FreeCAD?")}</b> {T("问渠 CAD 基于开源的 FreeCAD 1.1.4，带上我们在《FreeCAD 内核解密、验证与修正》里验证过的 27 处修正和问渠的 AI 工作台。按 FreeCAD、OpenCASCADE 的开源许可（LGPL），这些修正的源代码随安装包说明提供。",
   "WenQuest CAD is based on the open-source FreeCAD 1.1.4 with 27 fixes verified in our FreeCAD kernel book and the WenQuest AI workbench. Under FreeCAD’s and OpenCASCADE’s LGPL, the source of these fixes is provided as stated in the installer.")}</p>
</div>
"""


def render(region: str = "us", footer: str = "", head: str = "") -> str:
    """footer/head：国内版传入 build.py 的页脚（备案号等）和它的样式表"""
    cn = region == "cn"
    home = "/"
    learn = 'https://learn.{{env "SITE_DOMAIN"}}' if cn else "https://learn.wenquestrobotics.com"   # 国内页走 Caddy 模板，和国内官网其他页一样
    course_btn = (f'<a class="btn" href="{learn}/static/help/wqcad/">培训课程</a>' if cn else
                  f'<a class="btn" data-zh href="{learn}/static/help/wqcad/">培训课程</a><a class="btn" data-en href="{learn}/static/help/wqcad/en/">Training course</a>')
    cad_note = ""
    online = lambda path: f"{learn}{path}"
    return f"""<!doctype html>
<html lang="{'zh-CN' if cn else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="{'/assets/logo.svg' if cn else '/favicon.svg'}" type="image/svg+xml">
<title>{'问渠软件下载（测试版）' if cn else 'Downloads (beta) — WenQuest'}</title>
{head}<style>{CSS}</style>
</head>
<body>
<main>
<div class="top"><a href="{home}">← {T("问渠科技" if cn else "问渠", "WenQuest")}</a><span><span data-wq-auth></span> <button id="lang" type="button">EN</button></span></div>
<h1>{T("问渠软件下载（测试版）", "WenQuest software downloads (beta)")}</h1>
<p class="lead">{T("问渠的桌面软件和 FreeCAD 工作台都可以下载安装。现在是测试版：注册用户免费领一年授权，期间随时更新到新版本。网页版软件（问渠电子、数字工厂、缝纫机网页版等）不用下载，登录学习平台就能用。",
 "WenQuest desktop software and FreeCAD workbenches can be downloaded and installed. This is a beta: registered users get a free one-year licence and can update to new versions at any time. The web apps (WenQuest Electronics, the digital factory, the web sewing-machine designer…) need no download; sign in to the learning platform.")}</p>

<div class="steps">
<div><b>1</b>{T("注册或登录问渠账号", "Sign up or sign in")}</div>
<div><b>2</b>{T("领取一年测试授权（下面）", "Get a one-year beta licence (below)")}</div>
<div><b>3</b>{T("下载、照教程安装", "Download and install with the guide")}</div>
<div><b>4</b>{T("首次打开时粘贴授权码", "Paste the code the first time you open it")}</div>
</div>

<div class="lic" id="lic">
<b>{T("一年测试授权", "One-year beta licence")}</b>
<p id="licMsg" class="note">{T("登录后点按钮领取；问渠所有可下载的软件共用这一个授权码。", "Sign in, then click the button; one code works for all WenQuest downloads.")}</p>
<code id="licCode" hidden></code>
<div class="row" style="display:flex;gap:8px;flex-wrap:wrap"><button class="pri" id="licGet" type="button">{T("领取一年测试授权", "Get a one-year beta licence")}</button><button id="licCopy" type="button" hidden>{T("复制", "Copy")}</button></div>
</div>

<h2>{T("下载", "Downloads")}</h2>
<div class="cards">
<div class="card" data-key="wqcad"><h3>{T("问渠 CAD", "WenQuest CAD")} <span class="tag">Windows 10/11 64 位</span></h3>
<p>{T("基于 FreeCAD 1.1.4 + 27 处内核修正 + 问渠 AI 工作台（AI 选零件、企业零件库、AI 设计零件）。一个安装包，装完就能用，不用装别的。",
      "FreeCAD 1.1.4 + 27 kernel fixes + the WenQuest AI workbench (AI part selection, enterprise parts library, AI part design). One installer, nothing else to install.")}</p>
<div class="meta" data-meta>{T("安装包准备中", "Installer being built")} {cad_note}</div><div class="sha" data-sha></div>
<div class="row"><a class="btn pri" data-dl hidden>{T("下载", "Download")}</a><a class="btn" href="#tut-cad">{T("安装教程", "Install guide")}</a>{course_btn}</div></div>
<div class="card" data-key="sewing-freecad"><h3>{T("问渠缝纫机", "WenQuest Sewing")} <span class="tag">{T("FreeCAD 工作台", "FreeCAD workbench")}</span></h3>
<p>{T("平缝、包缝、绷缝、花样、刺绣、横机的机构设计与校核，出三维零件、计算书；和网页版同一份计算核心。", "Mechanism design and checks for lockstitch, overlock, coverstitch, pattern, embroidery and flat-knitting machines; 3-D parts and reports; same core as the web app.")}</p>
<div class="meta" data-meta></div><div class="sha" data-sha></div>
<div class="row"><a class="btn pri" data-dl hidden>{T("下载", "Download")}</a><a class="btn" href="#tut-wb">{T("安装教程", "Install guide")}</a></div></div>
<div class="card" data-key="bearing-freecad"><h3>{T("问渠轴承", "WenQuest Bearing")} <span class="tag">{T("FreeCAD 工作台", "FreeCAD workbench")}</span></h3>
<p>{T("各类滚动轴承的设计校核、合套选配与尺寸链、零件图与三维、工艺。", "Rolling-bearing design checks, matching and tolerance chains, drawings and 3-D, process.")}</p>
<div class="meta" data-meta></div><div class="sha" data-sha></div>
<div class="row"><a class="btn pri" data-dl hidden>{T("下载", "Download")}</a><a class="btn" href="#tut-wb">{T("安装教程", "Install guide")}</a></div></div>
<div class="card" data-key="cam-freecad"><h3>{T("问渠凸轮", "WenQuest Cam")} <span class="tag">{T("FreeCAD 工作台", "FreeCAD workbench")}</span></h3>
<p>{T("盘形、圆柱凸轮设计校核，加工程序，测量与补偿，凸轮系统。", "Disc and cylindrical cam design and checks, machining programs, measurement and compensation, cam systems.")}</p>
<div class="meta" data-meta></div><div class="sha" data-sha></div>
<div class="row"><a class="btn pri" data-dl hidden>{T("下载", "Download")}</a><a class="btn" href="#tut-wb">{T("安装教程", "Install guide")}</a></div></div>
<div class="card" data-key="wqfea"><h3>{T("问渠有限元", "WenQuest FEA")} <span class="tag">Windows 10/11 64 位</span></h3>
<p>{T("零件静力分析：建算例、Gmsh 划网格、CalculiX 求解，自动做网格收敛、反力平衡、奇异点三项核查，通过了才给安全系数；带验证手册和入门例子。免费版不用授权码；出报告、AI 一句话起草等专业版功能暂不开放。",
      "Static analysis of parts: set up the case, Gmsh mesh, CalculiX solve, then automatic checks (mesh convergence, reaction balance, singularities) before a safety factor is given; verification manual and examples included. The free edition needs no licence code; Pro features (reports, AI drafting) are not open yet.")}</p>
<div class="meta" data-meta>{T("安装包准备中", "Installer being built")}</div><div class="sha" data-sha></div>
<div class="row"><a class="btn pri" data-dl hidden>{T("下载", "Download")}</a><a class="btn" href="#tut-cad">{T("安装教程", "Install guide")}</a></div></div>
<div class="card" data-key="wqmbd"><h3>{T("问渠多体动力学", "WenQuest MBD")} <span class="tag">Windows 10/11 64 位</span></h3>
<p>{T("机构运动学与动力学：直接读装配体的零件和关节，给驱动，算驱动力矩、运动副受力、速度加速度，先核查约束残差、自由度、能量再给结果。免费版不用授权码；专业版功能暂不开放。",
      "Kinematics and dynamics of mechanisms: reads the assembly's parts and joints, add drives, get drive torques, joint forces, velocities and accelerations, with checks (constraint residual, degrees of freedom, energy) before results. The free edition needs no licence code; Pro features are not open yet.")}</p>
<div class="meta" data-meta>{T("安装包准备中", "Installer being built")}</div><div class="sha" data-sha></div>
<div class="row"><a class="btn pri" data-dl hidden>{T("下载", "Download")}</a><a class="btn" href="#tut-cad">{T("安装教程", "Install guide")}</a></div></div>
<div class="card"><h3>{T("白板课", "Whiteboard lessons")} <span class="tag">{T("在线使用", "Online")}</span></h3>
<p>{T("输入题目或上传录音，AI 画出会动的白板讲解，出网页和视频；老师在平台上编辑、发给学生。不用下载，登录学习平台就能用。",
      "Type a topic or upload a recording and AI draws an animated whiteboard explanation, as a web page and a video; teachers edit and share it on the platform. Nothing to download; sign in to the learning platform.")}</p>
<div class="row"><a class="btn pri" href="{online('/pages/whiteboard/whiteboard')}">{T("打开", "Open")}</a></div></div>
<div class="card"><h3>{T("三维仿真视频", "3-D simulation videos")} <span class="tag">{T("在线使用", "Online")}</span></h3>
<p>{T("机构、零件、工作场景的三维讲解视频，在平台上做、在平台上看。不用下载，登录学习平台就能用。",
      "3-D explainer videos of mechanisms, parts and work scenes, made and watched on the platform. Nothing to download; sign in to the learning platform.")}</p>
<div class="row"><a class="btn pri" href="{online('/pages/video3d/video3d')}">{T("打开", "Open")}</a></div></div>
</div>
<p class="note">{T("问渠轴承和问渠凸轮装在同一个“问渠”工作台里，两个都装时后装的覆盖先装的，功能都在。", "Bearing and Cam share one “WenQuest” workbench; installing both is fine.")}</p>
{tutorials(region)}
</main>
{footer}
<script>
(() => {{
  const root = document.documentElement, btn = document.getElementById("lang");
  let l = null; try {{ l = localStorage.getItem("wq-site-lang2"); }} catch (e) {{}}
  l = l || ({str(cn).lower()} || location.hostname.endsWith("wenquestech.online") ? "zh" : "en");
  const set = (x) => {{ l = x; root.lang = x === "en" ? "en" : "zh-CN"; btn.textContent = x === "en" ? "中文" : "EN"; try {{ localStorage.setItem("wq-site-lang2", x); }} catch (e) {{}} }};
  set(l); btn.onclick = () => set(l === "en" ? "zh" : "en");
  const CN = {str(cn).lower()};
  const mb = (n) => (n / 1048576).toFixed(n > 104857600 ? 0 : 1) + " MB";
  fetch("/download/versions.json", {{ cache: "no-store" }}).then((r) => r.ok ? r.json() : {{}}).then((v) => {{
    document.querySelectorAll(".card[data-key]").forEach((c) => {{
      const it = v[c.dataset.key]; if (!it) return;
      if (CN && /^https?:/.test(it.url) && !it.url_cn) return;
      const url = CN && it.url_cn ? it.url_cn : (/^https?:/.test(it.url) ? it.url : "/download/" + it.url);
      const a = c.querySelector("[data-dl]"); a.href = url; a.hidden = false;
      c.querySelector("[data-meta]").innerHTML = (l === "en" ? "Version " : "版本 ") + it.version + " · " + it.date + " · " + mb(it.size);
      c.querySelector("[data-sha]").textContent = "SHA-256 " + it.sha256;
    }});
  }}).catch(() => {{}});
  const msg = document.getElementById("licMsg"), code = document.getElementById("licCode"), cp = document.getElementById("licCopy");
  const say = (zh, en) => {{ msg.innerHTML = "<span data-zh>" + zh + "</span><span data-en>" + en + "</span>"; }};
  document.getElementById("licGet").onclick = async () => {{
    try {{
      const s = await fetch("/api/v1/auth/sso", {{ credentials: "same-origin" }});
      if (!s.ok) {{ say("请先登录（右上角“登录”，没有账号就“注册”），登录后回到本页再点。", "Please sign in first (top right; sign up if you have no account), then come back and click again."); return; }}
      const tok = (await s.json()).token;
      const r = await fetch("/api/v1/license/beta", {{ method: "POST", headers: {{ Authorization: "Bearer " + tok }} }});
      if (!r.ok) throw new Error(r.status);
      const d = await r.json();
      code.textContent = d.token; code.hidden = false; cp.hidden = false;
      const day = new Date(d.exp * 1000).toISOString().slice(0, 10);
      say("你的授权码（有效到 " + day + "）：复制后在软件首次打开时粘贴。", "Your licence code (valid until " + day + "): copy it and paste it the first time you open the software.");
    }} catch (e) {{ say("没领到（" + e.message + "），请稍后再试。", "Could not get a code (" + e.message + "); please try again later."); }}
  }};
  cp.onclick = () => {{ navigator.clipboard && navigator.clipboard.writeText(code.textContent); cp.textContent = l === "en" ? "Copied" : "已复制"; }};
}})();
</script>
<script src="/auth.js" defer></script>
<script src="{'/assets/assist.js' if cn else '/assist.js'}" defer></script>
</body>
</html>
"""


def main():
    out = ROOT / "site" / "download" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render("us"), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
