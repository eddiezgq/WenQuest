"""生成国内版官网“问渠科技”（第 48 轮）：site/cn/。

    python3 tools/site_cn/build.py            # 部署用：公司名、备案号等写成 Caddy 模板，由服务器 .env 在访问时填入
    python3 tools/site_cn/build.py --preview  # 本地预览：这些位置显示【占位】（输出到 site/cn-preview/，不进仓库）

文字依据 docs/方案/国内版官网文字稿.md（Eddie 审过的版本以文字稿为准，改文字先改文字稿再改这里）。
只在 WQ_REGION=cn 的服务器上由 Caddy 提供（deploy/site-handle/cn.caddy）；美国版 site/ 其余文件不受影响。
截图在 assets/，来源见 assets/README.md。
"""
import html
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIEW = "--preview" in sys.argv
OUT = ROOT / "site" / ("cn-preview" if PREVIEW else "cn")
VER = "50a"                                   # 改了 cn.css、cn.js 就改这里，浏览器取新文件

# ---------------------------------------------------------------- 由服务器 .env 填入的信息（Caddy templates）

def env(key, ph):
    """部署时：Caddy 模板，取环境变量，没填就显示【占位】；预览时直接显示【占位】。"""
    if PREVIEW:
        return f"【{ph}】"
    return '{{with env "' + key + '"}}{{.}}{{else}}【' + ph + '】{{end}}'


def env_opt(key, ph, fmt):
    """可选项（备案号）：填了才显示，fmt 里的 {v} 换成值。预览时用【占位】显示。"""
    if PREVIEW:
        return fmt.format(v=f"【{ph}】", digits="0")
    return '{{with env "' + key + '"}}' + fmt.format(v="{{.}}", digits='{{regexFind "[0-9]+" .}}') + "{{end}}"


COMPANY = env("WQ_COMPANY", "公司全称")
PHONE = env("WQ_CONTACT_PHONE", "电话")
EMAIL = env("WQ_CONTACT_EMAIL", "邮箱")
ADDRESS = env("WQ_ADDRESS", "地址")
AI_REG = env("WQ_AI_REG", "生成式AI登记编号")
LEARN = "#" if PREVIEW else 'https://learn.{{env "SITE_DOMAIN"}}'

# ---------------------------------------------------------------- 页面框架

LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="#1c9c8f"/>'
        '<path d="M5 11c4 0 6-3 11-3s7 3 11 3" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>'
        '<path d="M5 21c4 0 6 3 11 3s7-3 11-3" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>'
        '<circle cx="9" cy="16" r="1.8" fill="#e8a50b"/><circle cx="16" cy="16" r="1.8" fill="#fff"/><circle cx="23" cy="16" r="1.8" fill="#fff"/></svg>')

ENTERPRISE = [
    ("/solutions/qms-erp/", "问渠质量 ERP", "旗舰 · 以质量体系为核心的 AI ERP"),
    ("/solutions/platform/", "问渠数字工厂集成平台", "旗舰 · CAD/CAM/CAE/MES/MRP/ERP 一体"),
    ("/solutions/sewing/", "缝纫机设计与制造软件", "成熟产品"),
    ("/solutions/cam/", "凸轮设计与制造软件", "成熟产品"),
    ("/solutions/custom/", "制造业专用软件定制", "按企业需求定制"),
]
EDUCATION = [
    ("/education/platform/", "学习系统：问渠 AI 学习平台", "AI 原生的在线学习平台"),
    ("/education/#dev", "电子教材、虚拟实验、数字工厂开发", "按单位需求开发"),
    ("/education/#trial", "在线体验", "按单位申请，审核后开通"),
]


def nav(cur):
    def a(href, text):
        c = ' aria-current="page"' if cur == href else ""
        return f'<a href="{href}"{c}>{text}</a>'

    def dd(label, items):
        links = "".join(f'<a href="{h}">{t}<small>{s}</small></a>' for h, t, s in items)
        return f'<div class="dd"><button type="button" aria-expanded="false">{label}</button><div class="menu">{links}</div></div>'

    return ("<nav class=\"main\" aria-label=\"主菜单\">" + dd("企业服务", ENTERPRISE) + a("/services/", "技术服务")
            + dd("教育服务", EDUCATION) + a("/consulting/", "咨询") + a("/cases/", "案例") + a("/about/", "关于我们")
            + '<a class="cta-m" href="/contact/">预约演示</a></nav>')


def footer():
    icp = env_opt("WQ_ICP", "ICP备案号", '<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{v}</a>')
    psb = env_opt("WQ_PSB", "公安备案号",
                  '<a href="https://beian.mps.gov.cn/#/query/webSearch?code={digits}" target="_blank" rel="noopener">{v}</a>')
    return f"""<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <p class="brandline">问渠科技</p>
        <p>{COMPANY}</p>
        <p>地址：{ADDRESS}</p>
        <p>电话：{PHONE}</p>
        <p>邮箱：{EMAIL}</p>
      </div>
      <div><h3>企业服务</h3><ul>{''.join(f'<li><a href="{h}">{t}</a></li>' for h, t, _ in ENTERPRISE)}</ul></div>
      <div><h3>服务</h3><ul><li><a href="/services/">技术服务</a></li><li><a href="/education/">教育服务</a></li>
        <li><a href="/education/platform/">问渠 AI 学习平台</a></li><li><a href="/consulting/">咨询</a></li><li><a href="/cases/">案例</a></li></ul></div>
      <div><h3>关于</h3><ul><li><a href="/about/">关于我们</a></li><li><a href="/contact/">预约演示 / 联系我们</a></li>
        <li><a href="/privacy/">隐私政策</a></li><li><a href="/terms/">用户协议</a></li><li><a href="/ai/">AI 服务说明</a></li>
        <li><a href="/report/">投诉与举报</a></li></ul></div>
    </div>
    <p class="ai">本站和产品中的 AI 功能调用已备案的境内大模型（DeepSeek），AI 生成的内容均标注“AI 生成”，经人工审核后才生效。生成式人工智能服务登记编号：{AI_REG}</p>
    <div class="base">
      <span>© 2026 {COMPANY}</span>
      {icp}
      {psb}
    </div>
  </div>
</footer>"""


def page(path, title, desc, body, cur=None):
    """path 是网址（如 /solutions/qms-erp/），写成 <OUT>/solutions/qms-erp/index.html。"""
    full = "问渠科技" if path == "/" else f"{title} · 问渠科技"
    doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="/assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="/vendor/fonts/noto-serif-sc.css"><link rel="stylesheet" href="/vendor/fonts/noto-sans-sc.css"><link rel="stylesheet" href="/vendor/fonts/ibm-plex-mono.css">
<link rel="stylesheet" href="/assets/cn.css?v={VER}">
</head>
<body>
<a class="skip" href="#main">跳到正文</a>
<header class="top"><div class="wrap">
  <a class="brand" href="/">{LOGO}<b>问渠科技</b></a>
  {nav(cur or path)}
  <a class="cta-top" href="/contact/">预约演示</a>
  <button class="burger" type="button" aria-expanded="false" aria-label="菜单">菜单</button>
</div></header>
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/cn.js?v={VER}" defer></script>
</body>
</html>
"""
    out = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def hero(eyebrow, h1, lead, crumbs=None, btns=None):
    cr = f'<p class="crumbs"><a href="/">首页</a> / {crumbs}</p>' if crumbs else ""
    bt = ""
    if btns:
        bt = '<div class="btns">' + "".join(
            f'<a class="btn{" solid" if i == 0 else ""}" href="{h}">{t}</a>' for i, (t, h) in enumerate(btns)) + "</div>"
    return f'<section class="hero sub"><div class="wrap">{cr}<p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p>{bt}</div></section>'


def part(no, h2, lead, inner, cls=""):
    ld = f"<p>{lead}</p>" if lead else ""
    nn = f'<span class="no">{no}</span>' if no else ""
    head = f'<div class="head">{nn}<h2>{h2}</h2>{ld}</div>' if h2 else ""
    return f'<section class="part {cls}"><div class="wrap">{head}{inner}</div></section>'


def ai_table(rows):
    tr = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return f'<div class="tbl"><table class="t ai"><thead><tr><th>AI 做</th><th>人做</th></tr></thead><tbody>{tr}</tbody></table></div>'


def shot(src, cap, alt=None):
    return (f'<figure class="shot"><img src="/assets/{src}" alt="{html.escape(alt or cap)}" loading="lazy" decoding="async">'
            f'<figcaption>{cap}</figcaption></figure>')


def ul(items):
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def steps(items, n=None):
    li = "".join(f"<li><b>{t}</b><span>{d}</span></li>" for t, d in items)
    return f'<ol class="steps" style="--n:{n or len(items)}">{li}</ol>'


def cta(h="看一看你的工厂能怎样用。", p="留下单位和联系方式，我们约时间演示。", btn="预约演示"):
    return (f'<section class="cta"><div class="wrap"><div><h2>{h}</h2><p>{p}</p></div>'
            f'<a class="btn solid" href="/contact/">{btn} →</a></div></section>')


DEMO_NOTE = "截图来自产品的演示环境，演示企业、人名和数据均为虚构。"
DEPLOY_STEPS = [
    ("调研", "看你的产品、流程、表单和现有系统，列出要用的模块。"),
    ("配置", "按你的规则配好流程、表单、编码和权限，导入现有数据。"),
    ("上线", "先选一条产品线或一个车间试运行，再推广。"),
    ("持续完善", "你提意见，AI 起草改动，你确认后生效；每次改动有记录、可撤回。"),
]

# ================================================================ 首页

def home():
    flag_qms = f"""<article class="flag">
  <div class="shot"><img src="/assets/qms-health.jpg" alt="问渠质量 ERP：质量体系按记录每日自查" loading="lazy"></div>
  <div class="txt"><span class="tag">旗舰一</span><h3>问渠质量 ERP</h3>
  <p>以质量体系为核心的 AI ERP。标准变成流程和检查，体系每天按记录自查；文件、不合格、来料检验、追溯召回，和接单、物料、排产、采购、财务在同一套数据里。</p>
  {ul(["AI 把共享盘里的文件分类，检查整个文件库，起草新文件，人审批", "不合格与纠正、来料检验、控制图、帕累托、鱼骨图与 5 Why、过程 FMEA", "生产记录逐步签字，出了问题一键追溯到批次、设备和人"])}
  <a class="more" href="/solutions/qms-erp/">了解问渠质量 ERP →</a></div></article>"""
    flag_plat = f"""<article class="flag">
  <div class="shot"><img src="/assets/platform-12steps.jpg" alt="问渠数字工厂集成平台：从需求到车间完工 12 步" loading="lazy"></div>
  <div class="txt"><span class="tag">旗舰二</span><h3>问渠数字工厂集成平台</h3>
  <p>CAD、CAM、CAE、MES、MRP、ERP 信息集成化平台：改一次设计，下游自动跟着变，车间只拿到批准过的版本。</p>
  {ul(["设计 → 审批 → 物料版本与 BOM → MRP → 排产与车间执行 → 数控程序 → 质量 → 厂情中枢", "接你已有的 CAD（SolidWorks、FreeCAD，或任何能导出 STEP 的软件）", "选哪几个模块就集成哪几个，也可以整套上"])}
  <a class="more" href="/solutions/platform/">了解集成平台 →</a></div></article>"""
    products = f"""<div class="cards" style="--n:2">
  <article class="card"><div class="shot"><img src="/assets/sewing-video.jpg" alt="缝纫机设计与制造软件" loading="lazy"></div>
    <span class="tag">成熟产品</span><h3 style="margin-top:12px">缝纫机设计与制造软件</h3>
    <p>平缝机、包缝机、绷缝机、电子花样机、多头刺绣机的设计、校核与出图。改参数，当场看三维样机、运动时序和红绿灯校核；一键出设计计算书、三维模型（STEP）、零件轮廓（DXF）、调机卡。网页直接用，也能装进 FreeCAD。</p>
    <a class="more" href="/solutions/sewing/">了解 →</a></article>
  <article class="card"><div class="shot"><img src="/assets/cam-ui.jpg" alt="凸轮设计与制造软件界面" loading="lazy"></div>
    <span class="tag">成熟产品</span><h3 style="margin-top:12px">凸轮设计与制造软件</h3>
    <p>从运动要求到凸轮廓线，再到加工误差与补偿：挑线、送布等凸轮机构的运动与受力，廓线误差在高速下引起的加速度误差，磨削补偿能修掉哪些误差。</p>
    <a class="more" href="/solutions/cam/">了解 →</a></article>
</div>"""
    custom = f"""<div class="split"><div><h3>你的行业，你的软件</h3>
<p>你的行业有没有现成软件解决不了的设计、计算或工艺问题？我们按你的需求定制专用软件，缝纫机和凸轮两款软件就是这样做出来的。</p>
<ol class="plain">{"".join(f"<li><b>{a}</b>：{b}</li>" for a, b in [("需求调研", "讲清现在怎么算、怎么画、怎么检"), ("AI 起草", "计算核心和界面，工程师逐条核对"), ("试用迭代", "用你自己的老产品核对结果"), ("交付", "网页版或 FreeCAD 工作台，可接入集成平台")])}</ol>
<p style="margin-top:22px"><a class="btn" href="/solutions/custom/">定制怎么做 →</a></p></div>
{shot("case-lockstitch.jpg", "缝纫机设计软件做出的直驱平缝机案例：每分钟 5000 针，主轴电机该选多大")}</div>"""
    cases = """<div class="cards casecards" style="--n:4">
  <a class="card" href="/cases/#cobot" style="text-decoration:none"><div class="shot"><img src="/assets/case-cobot-joint.jpg" alt="" loading="lazy"></div><h3>协作机器人关节</h3><p>从选型、强度到数控程序，再进 ERP、排 MRP、下 MES 工单。</p></a>
  <a class="card" href="/cases/#scara" style="text-decoration:none"><div class="shot"><img src="/assets/case-scara.jpg" alt="" loading="lazy"></div><h3>SCARA 机器人</h3><p>节拍定了 0.4 秒，零件库能不能供得上：缺什么，平台照实说。</p></a>
  <a class="card" href="/cases/#lockstitch" style="text-decoration:none"><div class="shot"><img src="/assets/case-lockstitch.jpg" alt="" loading="lazy"></div><h3>直驱平缝机</h3><p>每分钟 5000 针，主轴电机该选多大，上轴强度与共振怎么校核。</p></a>
  <a class="card" href="/cases/#thread" style="text-decoration:none"><div class="shot"><img src="/assets/case-digital-thread.jpg" alt="" loading="lazy"></div><h3>数字主线追溯</h3><p>客户一个电话，追到车间那片砂轮，再找出同样隐患的设备。</p></a>
</div><p class="note">案例使用虚构的演示企业和数据。</p>"""
    three = """<div class="cards">
  <article class="card"><h3>技术服务</h3><p>工程仿真（有限元强度、疲劳、温度场、流体、多体动力学）、设计优化、数控编程、工业设计。</p><a class="more" href="/services/">了解 →</a></article>
  <article class="card"><h3>教育服务</h3><p>学习系统（问渠 AI 学习平台）、电子教材开发、虚拟实验开发、数字工厂开发、CAD/CAM/CAE 集成化解决方案；学校和企业可按单位申请在线体验。</p><a class="more" href="/education/">了解 →</a></article>
  <article class="card"><h3>咨询</h3><p>数字化转型与智能制造诊断，ERP / MES 选型与实施规划，工业软件方案咨询。</p><a class="more" href="/consulting/">了解 →</a></article>
</div>"""
    body = f"""<section class="hero"><canvas id="thread" aria-hidden="true"></canvas><div class="wrap">
  <p class="eyebrow">问渠科技 · AI 原生的制造业软件</p>
  <h1><span class="nw">按你的工厂来配，</span><span class="nw"><em>模块自由组合</em>，</span><span class="nw">快速上线、越用越合身。</span></h1>
  <p class="lead">我们用 AI 重新构造制造企业的软件，不是在老系统上加一个聊天框：整理文件、起草流程、每天自查、追查原因、生成程序，这些原来要人一点点做的事交给 AI，人只做判断和审批。</p>
  <div class="btns"><a class="btn solid" href="/contact/">预约演示 →</a><a class="btn" href="#flagships">看两个旗舰产品</a></div>
  <p class="motto">问渠那得清如许，为有源头活水来。</p>
</div>
<div class="wrap" style="position:relative;z-index:2"><div class="pillars">
  <div><span class="no">01</span><h3>AI 原生</h3><p>每项功能都写清“AI 做什么、人做什么”。AI 起草，人批准才生效，全程留痕。</p></div>
  <div><span class="no">02</span><h3>自由组合</h3><p>质量、ERP、MRP、MES、CAD、CAM、CAE、厂情中枢，每个模块都能单独用，也能任意组合，经同一条数据总线连在一起，并对接你已有的系统。</p></div>
  <div><span class="no">03</span><h3>个性化部署</h3><p>按你的产品、流程、表单和标准配置，不让企业去适应软件。上线后按你的反馈持续完善：AI 起草改动，你确认后生效。</p></div>
</div></div></section>
<div id="flagships"></div>
{part("旗舰产品", "两个旗舰：质量为核心的 AI ERP，和一条数字主线", "两者可以单独上，也可以合在一起：质量 ERP 管体系和经营，集成平台把设计、工艺和车间接进来。", f'<div class="flagships">{flag_qms}{flag_plat}</div><p class="note">{DEMO_NOTE}</p>')}
{part("成熟产品", "两款已经可以交付的行业软件", "网页直接用，也能装进 FreeCAD；计算核心相同，结果一致；设计结果可以提交到集成平台审批。", products, "alt")}
{part("定制", "制造业专用软件定制", None, custom)}
{part("部署", "部署怎么走", "可以只上一个模块，先解决一个问题，再逐步扩展。", steps(DEPLOY_STEPS), "dark")}
{part("案例", "典型案例", "从需求到车间完工，每一步做了什么、得出什么数、产出了什么，都在平台里留着。", cases, "alt")}
{part("服务", "技术服务、教育服务和咨询", None, three)}
{cta()}"""
    page("/", "问渠科技", "问渠科技：AI 原生的制造业软件——以质量体系为核心的 AI ERP、CAD/CAM/CAE/MES/MRP/ERP 数字工厂集成平台、缝纫机与凸轮设计软件、制造业专用软件定制，以及技术服务、教育服务和咨询。", body)


# ================================================================ 旗舰一：问渠质量 ERP

def qms():
    feats = """<div class="cards">
  <article class="card"><h3>文件库与文件控制</h3><p>上传共享盘，AI 归类；整个文件库做一次检查，旧台账变成记录。只有一个生效版本，变更要签字，相关人员读过并确认。</p></article>
  <article class="card"><h3>不合格与纠正预防</h3><p>从发现、隔离、处置到纠正预防（CAPA），每一步谁做、谁批，职责分离，系统强制执行。</p></article>
  <article class="card"><h3>来料检验与控制图</h3><p>来料检验按抽样方案由程序判定；控制图直接来自已签字的检验记录，过程偏移自动提示并可一键开不合格报告。</p></article>
  <article class="card"><h3>质量工具</h3><p>帕累托图、鱼骨图与 5 Why（AI 建议、你来定）、按你自己评分尺度的过程 FMEA，并与流程图关联。</p></article>
  <article class="card"><h3>生产记录与追溯</h3><p>每一步签字、每个量具检查有效期；扫一下标签记录就打开；从供应商批次到每一位客户，几秒钟追完。</p></article>
  <article class="card"><h3>同一套数据的 ERP</h3><p>接单、发货、采购、收货、库存（批次、序列号、再订货点）、生产、开票与应收应付、财务分录，全在同一套记录里。</p></article>
</div>"""
    gallery = f"""<div class="split"><div><h3>体系每天按记录自查</h3><p>每一条标准条款都对应流程、控制措施和检查。系统每天对照真实记录检查一遍：达标、未达标、未知，一目了然，审核前不用临时补材料。</p>
{ul(["可按 ISO 9001、ISO 13485 等标准配置条款", "未达标项直接点进去看是哪条记录、谁负责"])}</div>{shot("qms-health.jpg", "质量体系健康度：按条款对照记录每日自查（演示数据）")}</div>
<div class="split rev"><div><h3>上传共享盘，AI 来归类</h3><p>多年的文件散在共享盘里：程序、作业指导书、台账、证书。上传以后 AI 判断每份是什么、属于哪个过程，并引用原文给出依据，你确认后才入库。</p></div>{shot("qms-docs.jpg", "AI 判断文件类型与所属过程，引用原文，人确认（演示数据）")}</div>
<div class="split"><div><h3>原因分析：AI 建议，你来定</h3><p>不合格发生后，AI 读相关记录，在鱼骨图上给出可能原因并标明依据；结论由你下，纠正措施由你批。</p></div>{shot("qms-rca.jpg", "鱼骨图与 5 Why：AI 建议原因，人下结论（演示数据）")}</div>
<div class="split rev"><div><h3>从批次到客户，几秒钟</h3><p>供应商发来警告：某批来料有问题。从来料批次向下追到用了它的生产记录，再追到发给了哪几家客户，一张图看完，召回范围清清楚楚。</p></div>{shot("qms-trace.jpg", "向下追溯：来料批次 → 生产记录 → 客户（演示数据）")}</div>"""
    more = f"""<div class="gallery">{shot("qms-capa.jpg", "不合格品报告：隔离、处置、纠正预防，职责分离")}{shot("qms-spc.jpg", "控制图：来自已签字的检验记录，过程偏移自动提示")}
{shot("qms-anomaly.jpg", "异常：迟交订单点一下，沿关联记录追到原因")}{shot("qms-wall.jpg", "车间大屏：整家公司的运营情况实时显示")}</div><p class="note">{DEMO_NOTE}</p>"""
    body = f"""{hero("旗舰产品一", "问渠质量 ERP：以质量体系为核心的 AI ERP", "质量不是 ERP 里的一个角落，而是整套系统的骨架：标准写成流程和检查，每一张单据都按体系走，体系每天按记录自己检查自己。", "企业服务 / 问渠质量 ERP", [("预约演示", "/contact/"), ("和集成平台怎么组合", "/solutions/platform/#combine")])}
{part("一", "AI 做什么、人做什么", "AI 只起草和建议；凡是会生效的东西，都要人批准，系统记下谁、在什么时候、批准了哪一版。", ai_table([
        ("把共享盘里的文件分类，找出缺的、过期的、互相矛盾的", "决定保留、修订还是作废"),
        ("按标准条款起草程序文件、作业指导书、表单", "审批，批准后才受控生效"),
        ("每天按生产、检验、培训记录自查体系，列出偏差", "指派责任人、确认关闭"),
        ("起草不合格的原因分析（鱼骨图、5 Why）和纠正措施", "判断、批准、验证效果"),
        ("出了问题，沿记录追到批次、设备、人员，并找出同样隐患的产品", "决定是否召回、怎样通知客户"),
        ("回答“这个月为什么迟交这么多”这类问题，引用你自己的记录", "据此决策"),
    ]))}
{part("二", "看几个画面", None, gallery, "alt")}
{part("三", "功能", None, feats)}
{part("四", "更多画面", None, more, "alt")}
{part("五", "适合谁、怎么上", "要过质量体系审核、客户审核的中小制造企业；文件多、记录散、追溯靠翻纸的工厂。可以只上质量部分，再逐步接 ERP 和集成平台的其他模块。", steps(DEPLOY_STEPS))}
{cta()}"""
    page("/solutions/qms-erp/", "问渠质量 ERP", "问渠质量 ERP：以质量体系为核心的 AI ERP，AI 归类与起草文件、每日按记录自查体系、不合格与纠正预防、来料检验、控制图、追溯召回，与 ERP 同一套数据。", body, "/solutions/qms-erp/")


# ================================================================ 旗舰二：集成平台

MODULES = [
    ("CAD 接入与设计发布", "接企业已有的 CAD：SolidWorks 宏、FreeCAD 工作台一键提交，任何 CAD 导出 STEP 即可发布；网页三维看图、差异着色、点处批注，批准才生效；网页设计台做参数化零件。", "对比两版设计，列出改动和受影响的下游"),
    ("CAM 数控编程", "浏览器里排编程单，生成 FANUC 风格 G 代码，仿真检查后挂到工艺规程，随工单派到车间终端；机床参数按企业设备配置。", "起草程序，标出风险工步"),
    ("CAE 仿真与优化", "不用装软件：有限元强度、疲劳寿命、温度场与热应力，流体（OpenFOAM），多体动力学（MuJoCo），设计优化与拓扑优化，结果送回设计。", "按工况起草仿真设置，读结果写报告"),
    ("ERP / MRP", "基于开源 ERPNext：物料、BOM、工艺规程、MRP、销售与采购、财务一套数据。", "起草采购和排产建议"),
    ("MES 车间执行", "车间终端报工、质检、设备维护、人员排班；能源与环境、安全环保。", "发现异常，起草处理单"),
    ("厂情中枢", "把全厂数据连成一张关系网：订单、物料、设备、人员、质量；异常带因果链，每日态势卡；数字孪生：卖出的每台产品在线监测、预测维护。", "写每日态势，追查根源"),
    ("参数配置器", "销售填参数，出三维、图纸、报价并草拟订单。", "按客户需求推荐配置"),
    ("质量体系", "即问渠质量 ERP 的质量部分，可单独作为集成平台的一个模块。", "归类与起草文件、每日自查、原因分析"),
]


def platform():
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in MODULES)
    table = f'<div class="tbl"><table class="t"><thead><tr><th>模块</th><th>能做什么</th><th>AI 做什么</th></tr></thead><tbody>{rows}</tbody></table></div>'
    thread = f"""<div class="split"><div><h3>一条数字主线</h3>
<p>CAD → 审批 → ERP（物料版本 / BOM）→ MRP → 排产与车间执行（MES）→ CAM 程序 → 质量 → 厂情中枢。</p>
<p>设计院改了一个零件，批准以后，物料版本、BOM、工单上的数控程序自动更新，车间终端只拿到批准过的版本；全程留痕，谁改的、谁批的、影响到哪些工单，随时查得到。</p></div>
{shot("platform-12steps.jpg", "从需求到车间完工 12 步：设计院 6 步、数字工厂 6 步，绿色是通过，黄色是待确认")}</div>
<div class="split rev"><div><h3>出了问题，追得到根源</h3><p>厂情中枢把订单、物料、设备、人员和质量连成一张关系网。客户来电投诉，从这台设备追到输出轴、追到那片砂轮，再向前找出同一片砂轮加工过、装到别家客户设备上的零件。</p></div>
{shot("case-digital-thread.jpg", "数字主线追溯：投诉 → 输出轴 → 砂轮 → 同批零件 → 其他客户（演示数据）")}</div>"""
    combine = """<div class="cards">
  <article class="card"><h3>只要质量 + ERP</h3><p>先把体系和单据管起来：文件、不合格、检验、追溯，和接单、采购、库存、财务一套数据。</p></article>
  <article class="card"><h3>CAD + 审批 + ERP</h3><p>设计改动走审批，批准后自动更新物料版本和 BOM，采购和生产用的永远是最新批准的版本。</p></article>
  <article class="card"><h3>整套</h3><p>从设计、仿真、编程到车间执行、质量和售后，一条线；卖出的产品还能在线监测、预测维护。</p></article>
</div><p class="note">选哪几个就集成哪几个，并可对接你已有的系统（经统一的数据总线和接口）。</p>"""
    body = f"""{hero("旗舰产品二", "问渠数字工厂集成平台：CAD、CAM、CAE、MES、MRP、ERP 信息集成化", "一条数字主线把设计、工艺、加工、经营和车间连起来：改一次设计，下游自动跟着变，车间只拿到批准过的版本。", "企业服务 / 数字工厂集成平台", [("预约演示", "/contact/"), ("看案例", "/cases/")])}
{part("一", "设计、工艺、经营、车间，一条线", None, thread)}
{part("二", "各模块：每个都能单独用", "下表最后一列是 AI 在这个模块里做的事；它起草的东西都要人批准。", table, "alt")}
<div id="combine"></div>
{part("三", "怎样组合", None, combine)}
{part("四", "部署怎么走", None, steps(DEPLOY_STEPS), "dark")}
{cta()}"""
    page("/solutions/platform/", "问渠数字工厂集成平台", "问渠数字工厂集成平台：CAD、CAM、CAE、MES、MRP、ERP 信息集成化，模块自由组合，设计改动经审批自动传到 BOM、工单和车间。", body, "/solutions/platform/")


# ================================================================ 成熟产品

def sewing():
    body = f"""{hero("成熟产品", "缝纫机设计与制造软件", "平缝机、包缝机、绷缝机、电子花样机、多头刺绣机的设计、校核与出图：改参数，当场看三维样机和红绿灯校核，一键出计算书、模型和图纸。", "企业服务 / 缝纫机设计与制造软件", [("预约演示", "/contact/")])}
{part("一", "改参数，当场看结果", None, f'''<div class="split"><div>
{ul(["机型：平缝机、包缝机、绷缝机、电子花样机、多头刺绣机（横机随后上线）",
     "三维样机、运动时序和红绿灯校核：惯性力、钩线、挑线、送布、张力、共振、尺寸链",
     "一键出设计计算书、三维模型（STEP）、零件轮廓（DXF）、调机卡",
     "绷缝机出耗线量与线团计划；花样机出每针转速表、伺服选型和模板数控程序",
     "网页直接用，也能装进 FreeCAD：同一份计算核心，结果一致；可提交到集成平台审批",
     "可按企业的机型和标准定制"])}
<p><video controls preload="none" poster="/assets/sewing-video.jpg" style="width:100%;border-radius:10px;border:1px solid var(--line)"><source src="/solutions/sewing/video/short.mp4" type="video/mp4"></video></p>
<p class="note">介绍视频（约 3 分钟）。</p></div>
{shot("case-lockstitch.jpg", "直驱平缝机：每分钟 5000 针，主轴电机该选多大")}</div>''')}
{part("二", "交付物", None, '<ul class="chips"><li>设计计算书</li><li>三维模型 STEP</li><li>零件轮廓 DXF</li><li>调机卡</li><li>耗线量与线团计划</li><li>每针转速表</li><li>伺服选型</li><li>模板数控程序</li></ul>', "alt")}
{cta("把你的机型放进来试一试。", "我们用你的一款现有机型演示计算和出图。")}"""
    page("/solutions/sewing/", "缝纫机设计与制造软件", "缝纫机设计与制造软件：平缝机、包缝机、绷缝机、电子花样机、多头刺绣机的设计、校核与出图，网页与 FreeCAD 两用。", body, "/solutions/sewing/")


def cam():
    body = f"""{hero("成熟产品", "凸轮设计与制造软件", "从运动要求到凸轮廓线，再到加工误差与补偿：一路校核到计算书。浏览器里直接用，不用安装。", "企业服务 / 凸轮设计与制造软件", [("在线试用", "/cam/"), ("预约演示", "/contact/")])}
{part("一", "从运动要求到能加工的廓线", None, f'''<div class="split"><div>
{ul(["运动规律：等速、等加速等减速、简谐、摆线、修正梯形、修正正弦、3-4-5、4-5-6-7 等",
     "盘形凸轮与槽凸轮，直动 / 摆动从动件，滚子 / 平底 / 尖顶",
     "校核：刚性冲击、柔性冲击、压力角、根切、曲率半径、高速不跳离、接触应力、轴峰值力矩；缺数据的项标“未知”，不算合格",
     "挑线、送布等凸轮机构的运动与受力；廓线误差在高速下引起的加速度误差",
     "磨削补偿：算出能修掉哪些误差；弧面凸轮精确实体",
     "计算书导出 PDF；项目存在你自己的浏览器里或存成文件"])}</div>
{shot("cam-ui.jpg", "凸轮设计软件：运动程序、三维廓线、校核与曲线")}</div>''')}
{cta("带一个你的凸轮来。", "我们按你的运动要求现场出廓线和校核。")}"""
    page("/solutions/cam/", "凸轮设计与制造软件", "凸轮设计与制造软件：运动规律、廓线、校核、加工误差与磨削补偿，浏览器里直接用。", body, "/solutions/cam/")


def custom():
    body = f"""{hero("按企业需求定制", "制造业专用软件定制：你的行业，你的软件", "很多制造企业的核心诀窍在设计计算和工艺里，市面上的通用软件管不到。我们按你的需求定制专用软件。", "企业服务 / 制造业专用软件定制", [("谈谈你的需求", "/contact/")])}
{part("一", "怎么做", None, steps([
        ("需求调研", "工程师讲清楚现在怎么算、怎么画、怎么检；收集你的图纸、计算表、标准。"),
        ("AI 起草", "AI 起草计算核心和界面，我们的工程师核对每一个公式。"),
        ("试用", "你的工程师在网页上试用，用你自己的老产品核对结果。"),
        ("迭代", "按意见改，每一版有记录。"),
        ("交付", "网页版或 FreeCAD 工作台；可接入集成平台，设计结果直接走审批、进 ERP。"),
    ]))}
{part("二", "样板：两款已经交付的软件", "缝纫机设计与制造软件（五种机型）、凸轮设计与制造软件，都是按这个流程做出来的。", f'<div class="gallery">{shot("sewing-video.jpg", "缝纫机设计与制造软件")}{shot("cam-ui.jpg", "凸轮设计与制造软件")}</div>', "alt")}
{part("三", "部署与数据", None, "<p>软件和数据部署在你选定的国内服务器或你自己的机房；源代码与计算依据随交付文档提供（按合同约定）。</p>")}
{cta("说说你想算什么、画什么。", "一页纸的需求也行，我们先回一份可行性和做法。", "谈谈你的需求")}"""
    page("/solutions/custom/", "制造业专用软件定制", "制造业专用软件定制：需求调研、AI 起草、试用、迭代、交付，可接入集成平台。", body, "/solutions/custom/")


# ================================================================ 技术服务、教育、咨询

def services():
    inner = """<div class="cards">
  <article class="card"><h3>工程仿真</h3><p>有限元强度、疲劳寿命、温度场与热应力、流体分析、多体动力学；出仿真报告。</p></article>
  <article class="card"><h3>设计优化</h3><p>参数优化、拓扑优化，结果送回设计。</p></article>
  <article class="card"><h3>数控编程与工艺</h3><p>编程单、G 代码、仿真检查、工艺规程。</p></article>
  <article class="card"><h3>工业设计</h3><p>产品结构与外观设计、三维建模与出图。</p></article>
  <article class="card"><div class="shot"><img src="/assets/video3d-arm.jpg" alt="三维仿真视频画面" loading="lazy"></div><h3>三维仿真视频与讲解视频</h3><p>为产品说明、客户演示、员工上手制作三维动画和白板讲解视频（标注“AI 生成”）。</p></article>
  <article class="card"><h3>系统集成与数据服务</h3><p>与企业已有系统对接，数据迁移与清洗，在国内服务器上托管与备份。</p></article>
</div>"""
    body = f"""{hero("技术服务", "智能制造技术服务", "仿真、优化、编程、设计：用我们自己的平台和工具，替你把活干完，交付报告和文件。", "技术服务", [("咨询", "/contact/")])}
{part(None, "服务内容", None, inner)}
{cta("有一个具体的零件或问题？", "发来图纸或说明，我们回一份做法和报价。", "联系我们")}"""
    page("/services/", "技术服务", "问渠科技技术服务：工程仿真、设计优化、数控编程与工艺、工业设计、三维仿真视频、系统集成与数据服务。", body, "/services/")


EDU_SERVICES = [
    ("dev-lms", "学习系统", "问渠 AI 学习平台：AI 建课、AI 助教、AI 批改建议、网页互动课件，网页与微信小程序一套。",
     ["按单位部署（国内服务器或单位自己的机房）", "与单位已有的账号、课程对接", "老师和单位审核后才发布，全程留痕"], "/education/platform/"),
    ("dev-book", "电子教材开发", "按专业和课程标准编写电子教材：每章配程序、动画和实验，书里的数字由程序算出、逐条核对。",
     ["网页版、PDF 与课程包（课件、作业、测验）", "中英对照可选", "现有样书可看简介、目录、样章"], None),
    ("dev-lab", "虚拟实验开发", "物理仿真在浏览器里运行：机器人、力学、电路、PLC、Verilog 芯片设计等。",
     ["每个实验配指导书和报告模板", "任务自动判定，AI 助教讲原因不代做", "可嵌进课件当场操作"], None),
    ("dev-factory", "数字工厂开发", "按真实企业数据运转的教学或企业数字工厂：设计、工艺、计划、采购、质检、设备等岗位都在里面。",
     ["每班或每个部门一座自己的工厂", "基于开源 ERPNext，数据与业务真实", "可接集成平台与数字孪生"], "/solutions/platform/"),
    ("dev-cax", "CAD、CAM、CAE 集成化解决方案", "接企业或学校已有的 CAD，数控编程与仿真在浏览器里完成，结果走审批、进 ERP。",
     ["SolidWorks、FreeCAD，或任何能导出 STEP 的软件", "有限元、疲劳、温度场、流体、多体动力学", "缝纫机、凸轮等行业软件可按需求定制"], "/solutions/platform/"),
]


def education():
    cards = ""
    for aid, h, p, pts, link in EDU_SERVICES:
        more = f'<a class="more" href="{link}">了解 →</a>' if link else ""
        cards += f'<article class="card" id="{aid}"><h3>{h}</h3><p>{p}</p>{ul(pts)}{more}</article>'
    dev = f'<div class="cards">{cards}</div>'
    trial = f"""<div class="split"><div>
<h3>先在线体验，再谈合同</h3>
<p>学校和企业可以先在我们的服务器上在线体验：学习系统（AI 建课、AI 助教、互动课件、虚拟实验）、缝纫机与凸轮设计软件、演示数字工厂。</p>
{ul(["按单位申请：由单位联系人在“预约演示”里勾选“申请在线体验账号”", "审核后为单位开通若干体验账号，体验期 90 天，可以申请延长", "名额有限，按申请先后开通；不接受个人申请", "正式使用时按合同为单位单独部署"])}
<p><a class="btn solid" href="/contact/">申请在线体验 →</a></p></div>
{shot("edu-slides.jpg", "在线体验：网页互动课件，动画和实验在页里当场操作")}</div>"""
    body = f"""{hero("教育服务", "教育服务：学习系统与教学资源开发", "为学校和企业开发学习系统、电子教材、虚拟实验、数字工厂和 CAD、CAM、CAE 集成化解决方案；国内服务器上提供按单位开通的在线体验。", "教育服务", [("申请在线体验", "/contact/"), ("学习系统", "/education/platform/")])}
<div id="dev"></div>
{part("一", "我们为你开发什么", "每一项都按单位的需求做，交付后归单位使用；可以单独做，也可以合在一起。", dev)}
<div id="trial"></div>
{part("二", "在线体验", None, trial, "alt")}
{part("三", "边界", None, '<p class="note" style="margin-top:0">本公司提供教学软件开发、数字内容制作和教育咨询，不从事需要审批的教育培训活动；只与单位签约、不面向个人，不颁发证书。电子教材全文只给合同单位在平台内使用。</p>')}
{cta("想看一门课是怎样建出来的？", "申请在线体验，或预约我们用你的资料现场演示。", "申请在线体验")}"""
    page("/education/", "教育服务", "问渠科技教育服务：学习系统、电子教材开发、虚拟实验开发、数字工厂开发、CAD/CAM/CAE 集成化解决方案；按单位开通在线体验。", body, "/education/")


def edu_platform():
    feats = ul([
        "网页互动课件取代 PPT：像 PPT 一样翻页，动画、虚拟实验、三维模型嵌在页里当场操作",
        "网页与微信小程序一套；直播课可用腾讯会议",
        "与数字工厂教学版、虚拟实验室打通：课里直接进工厂做岗位实验",
        "企业版：把作业指导书、质量文件、设备手册变成员工上手课程；与问渠质量 ERP 的“培训确认”连通，学完、考过才算培训到位",
        "数据存于境内，按单位隔离；AI 调用已备案的境内大模型，生成内容标注“AI 生成”",
    ])
    body = f"""{hero("教育服务 · 学习平台", "问渠 AI 学习平台：AI 原生的在线学习平台", "AI 建课、AI 助教、AI 批改建议，老师和单位来把关。", "教育服务 / 问渠 AI 学习平台", [("预约演示", "/contact/")])}
{part("一", "AI 做什么、人做什么", None, ai_table([
        ("老师交来一堆杂乱的资料（讲义、PPT、视频、习题），或只说一句要求，AI 整理分类，建出完整的一门课：教学大纲、每节内容、网页互动课件、作业、测验、考试", "老师审核修改；课程委员会（单位指定的人）批准后才发布"),
        ("对话中随时改课：“第三章加一个实验”“这节讲浅一点”", "每次改动可撤回，留痕"),
        ("AI 助教回答学生的问题：只依据课程资料，注明出处；作业和实验只引导思路，不代做", "老师查看问答记录，纠正"),
        ("读学生的实验曲线和作业，起草评分建议", "老师复核后才生效"),
        ("为课件生成动画、讲解视频、虚拟实验（标注“AI 生成”）", "老师选用"),
    ]))}
{part("二", "特点", None, f'<div class="split"><div>{feats}</div>{shot("edu-slides.jpg", "网页互动课件：每页的动画和实验当场操作")}</div>', "alt")}
{part("三", "谁在用", "高校和职业院校用它开课、做实训；企业用它做员工上手和技术交流。平台作为软件按单位签约提供，不面向个人；国内服务器上可按单位申请在线体验（90 天）。", "", "")}
{cta("用你自己的一门课试一试。", "按单位申请在线体验，或交来资料，我们现场建一门课给你看。", "申请在线体验")}"""
    page("/education/platform/", "问渠 AI 学习平台", "问渠 AI 学习平台：AI 原生的在线学习平台，AI 建课、AI 助教、AI 批改建议，老师和单位把关；企业版与质量 ERP 培训确认连通。", body, "/education/platform/")


def consulting():
    body = f"""{hero("咨询", "数字化转型与智能制造咨询", "先看清楚现状，再决定上什么、先上什么。选型建议不限于我们自己的产品。", "咨询", [("预约咨询", "/contact/")])}
{part(None, "四步", None, steps([
        ("诊断", "现场看流程和数据，交《数字化现状诊断报告》。"),
        ("规划", "定目标和优先次序，交《数字化与智能制造规划》（分期、模块、投入估算）。"),
        ("选型", "ERP / MES / 质量系统 / 工业软件选型，交选型对比与建议。"),
        ("实施陪跑", "上线过程中的方案把关与问题处理。"),
    ]))}
{cta("先聊一次。", "说说你的工厂现在最头疼的一件事。", "预约咨询")}"""
    page("/consulting/", "咨询", "问渠科技咨询：数字化现状诊断、智能制造规划、ERP/MES/质量系统选型、实施陪跑。", body, "/consulting/")


def cases():
    items = [
        ("cobot", "case-cobot-joint.jpg", "一台协作机器人的肩关节，能不能只用现成零件做出来？",
         "以 UR5e 一类协作臂为对象：先算出关节要多大力矩，再从零件库里选电机、谐波减速器和驱动器，做强度、疲劳、热分析和拓扑优化，编好数控程序；然后发布到数字工厂，进 ERP、排 MRP、下 MES 工单，车间把它做出来。"),
        ("scara", "case-scara.jpg", "节拍定了 0.4 秒，零件库能不能供得上？",
         "以 600 mm 臂展的 SCARA 为对象：先按快、慢两种节拍算大臂和小臂的力矩，再到零件库里选型。快节拍找不到能满足的组合，平台照实报告缺什么，改按慢节拍选型，接着做拓扑优化、有限元和数控编程，发布到工厂做出来。"),
        ("lockstitch", "case-lockstitch.jpg", "每分钟 5000 针，主轴电机该选多大？",
         "以工业直驱平缝机为对象：电机直接装在主轴上。先算针杆机构在 5000 rpm 下的惯性力矩，分清“峰值”和“一转做功”，选出电机；再校核上轴的强度、疲劳和共振，用流体分析算控制箱散热器，编好数控程序。"),
        ("thread", "case-digital-thread.jpg", "客户一个电话，追到车间里的那片砂轮",
         "客户来电：减速器有异响、振动变大。厂情中枢沿着数据往回追：这台减速器装的哪根输出轴、在哪台磨床上用哪片砂轮磨的；再往前追：同一片砂轮还磨了哪些轴、装进了哪些客户的设备。然后按数字孪生的健康度排出风险，起草服务方案，人批准后派工。"),
    ]
    inner = ""
    for i, (aid, img, h, p) in enumerate(items):
        rev = " rev" if i % 2 else ""
        inner += f'<div class="split{rev}" id="{aid}"><div><h3>{h}</h3><p>{p}</p></div>{shot(img, h)}</div>'
    body = f"""{hero("案例", "典型案例：从需求到车间完工", "每一步做了什么、得出什么数、产出了什么，都在平台里留着；缺数据的地方，平台照实停下，不靠估。", "案例", [("预约演示", "/contact/")])}
{part(None, "四个案例", "案例使用虚构的演示企业和数据。", inner)}
{cta()}"""
    page("/cases/", "典型案例", "问渠科技典型案例：协作机器人关节、SCARA 机器人、直驱平缝机、数字主线追溯。", body, "/cases/")


def about():
    body = f"""{hero("关于我们", "问渠科技", "问渠那得清如许，为有源头活水来。", "关于我们")}
{part(None, "我们是谁", None, f'''<div class="doc">
<p>{COMPANY}，从事人工智能应用软件与工业软件的开发、信息系统集成和技术服务。我们相信，AI 能让每一家中小制造企业用上为自己量身定做的软件。</p>
<h2>创办人</h2>
<p>张国庆，曾任大学教授、院长和校长。</p>
<h2>我们怎么做事</h2>
{ul(["AI 起草，人来决定：会生效的东西都要人批准，全程留痕。", "每一个数字都能追到来源。", "不夸大：计划中的功能明确写“计划中”。", "数据存在境内，客户的数据只用于为客户服务。"])}
<h2>联系</h2>
<p>电话：{PHONE}<br>邮箱：{EMAIL}<br>地址：{ADDRESS}</p>
</div>''')}
{cta()}"""
    page("/about/", "关于我们", "关于问渠科技：人工智能应用软件与工业软件的开发、信息系统集成和技术服务。", body, "/about/")


PRODUCTS = ["问渠质量 ERP", "问渠数字工厂集成平台", "缝纫机设计与制造软件", "凸轮设计与制造软件", "制造业专用软件定制",
            "学习系统", "电子教材开发", "虚拟实验开发", "数字工厂开发", "CAD/CAM/CAE 集成化解决方案", "技术服务", "咨询"]


def contact():
    boxes = "".join(f'<label><input type="checkbox" name="products" value="{p}"> {p}</label>' for p in PRODUCTS)
    form = f"""<form class="demo" id="demo-form" novalidate>
  <label>单位名称 *<input type="text" name="org" required maxlength="100" autocomplete="organization"></label>
  <label>姓名 *<input type="text" name="name" required maxlength="40" autocomplete="name"></label>
  <label>手机 *<input type="tel" name="phone" required maxlength="20" autocomplete="tel" inputmode="tel"></label>
  <label>邮箱<input type="email" name="email" maxlength="254" autocomplete="email"></label>
  <label class="full">所在行业<input type="text" name="industry" maxlength="60" placeholder="如：缝制机械、减速器、电子装配、职业院校"></label>
  <fieldset><legend>想了解的产品或服务</legend>{boxes}</fieldset>
  <fieldset class="trial"><legend>在线体验</legend>
    <label><input type="checkbox" name="trial" value="1"> 申请在线体验账号（按单位开通，体验期 90 天）</label>
    <label>需要几个账号 <select name="seats"><option>1</option><option>2</option><option>3</option><option>4</option><option selected>5</option></select></label>
  </fieldset>
  <label class="full">需求说明<textarea name="note" maxlength="2000" placeholder="说说你的工厂或学校现在最想解决的一件事"></textarea></label>
  <label class="hp" aria-hidden="true">网站<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
  <label class="agree full"><input type="checkbox" name="consent" required> <span>我已阅读并同意<a href="/privacy/" target="_blank">《隐私政策》</a>，同意问渠科技为安排演示和联系我使用以上信息。</span></label>
  <div class="full"><button class="btn solid" type="submit">提交</button></div>
  <p class="msg" role="status" aria-live="polite"></p>
</form>
<p class="note">信息只存于境内服务器，仅用于联系你，不提供给第三方。也可以直接联系：电话 {PHONE}，邮箱 {EMAIL}。</p>"""
    body = f"""{hero("预约演示", "预约演示 / 联系我们", "留下单位和联系方式，我们会在 2 个工作日内联系你，约时间演示。", "预约演示")}
{part(None, "填写信息", None, form)}"""
    page("/contact/", "预约演示", "预约问渠科技的产品演示或咨询。", body, "/contact/")


# ================================================================ 法律页

def privacy():
    body = f"""{hero("隐私政策", "隐私政策", "我们怎样处理你的个人信息。", "隐私政策")}
{part(None, "", None, f'''<div class="doc">
<p class="meta">更新日期：2026 年 10 月 27 日　生效日期：2026 年 10 月 27 日</p>
<p>{COMPANY}（以下称“我们”）依照《中华人民共和国个人信息保护法》《中华人民共和国网络安全法》《中华人民共和国数据安全法》等法律法规处理个人信息。本政策适用于本网站，以及我们向单位客户提供的软件和服务中由我们处理个人信息的情形；在单位客户自行部署和管理的系统中，单位客户是个人信息处理者，我们按其委托处理。</p>
<h2>一、个人信息处理者与联系方式</h2>
<p>个人信息处理者：{COMPANY}<br>地址：{ADDRESS}<br>个人信息保护事务联系方式：{EMAIL}，{PHONE}</p>
<h2>二、我们收集哪些信息、为什么</h2>
<h3>1. 预约演示与联系</h3>
<p>单位名称、姓名、手机号、邮箱（选填）、所在行业、想了解的产品、需求说明。目的：联系你、安排演示和提供报价。你主动填写并勾选同意后才提交。</p>
<h3>2. 产品账号</h3>
<p>在我们的产品中注册账号时，需要手机号（用于实名注册、登录和找回账号，依照《网络安全法》要求提供真实身份信息）和姓名；单位客户为其人员开通账号的，由单位提供。目的：提供服务、身份验证和安全保障。</p>
<h3>3. 使用记录</h3>
<p>登录记录、操作日志、审批与签字记录（含时间、操作人、版本）。目的：提供服务、记录追溯（这是质量体系和审批功能本身的要求）、安全审计。网络日志按法律要求留存不少于六个月。</p>
<h3>4. 你提交给 AI 功能的内容</h3>
<p>你在 AI 功能中输入或上传的文字、文件。目的：完成你要求的起草、归类、回答等任务。</p>
<p>我们不收集与上述目的无关的信息，不收集精确位置、通讯录等。</p>
<h2>三、存储地点与期限</h2>
<p>个人信息存储于中华人民共和国境内的服务器，不向境外提供。预约演示信息自提交起保存两年后删除，或在你要求时删除；账号信息在账号注销后 15 个工作日内删除或匿名化；法律法规要求保存更久的（如网络日志、合同约定的质量记录），依法保存。</p>
<h2>四、AI 功能</h2>
<p>AI 功能调用已备案的境内大模型服务。你提交的内容仅用于完成本次任务，我们不将其用于训练第三方模型。AI 生成的内容标注“AI 生成”，经人工审核后才在系统中生效。</p>
<h2>五、委托处理、共享、转让与公开披露</h2>
<p>我们不出售个人信息。仅在以下情形与他人共享：为向你发送短信验证码，委托境内短信服务商处理手机号；依法律法规或有权机关的要求。委托处理时，我们与受托方约定处理目的、方式和保护措施，并监督其履行。未经你单独同意，我们不向其他个人信息处理者提供你的个人信息，不公开披露。</p>
<h2>六、你的权利</h2>
<p>你有权查阅、复制、更正、补充、删除你的个人信息，有权撤回同意、注销账号，有权要求我们解释处理规则。请通过 {EMAIL} 联系我们，我们在验证身份后 15 个工作日内答复。</p>
<h2>七、安全措施</h2>
<p>传输全程加密（HTTPS）；按单位隔离数据；最小权限访问；操作留痕；定期备份。发生个人信息安全事件时，我们会按法律要求告知你并向主管部门报告。</p>
<h2>八、未成年人</h2>
<p>我们的网站和产品面向成年人和机构用户，不面向不满十四周岁的未成年人。如发现误收集了不满十四周岁未成年人的个人信息，我们会尽快删除。</p>
<h2>九、Cookie</h2>
<p>我们只使用维持登录和保障安全所必需的 Cookie，不使用广告或跨站跟踪 Cookie。</p>
<h2>十、本政策的更新</h2>
<p>本政策更新时，我们会在本页公布新版本并注明更新日期；重大变更会以显著方式提示。</p>
</div>''')}"""
    page("/privacy/", "隐私政策", "问渠科技隐私政策。", body, "/privacy/")


def terms():
    body = f"""{hero("用户协议", "用户协议", "使用本网站和我们的产品前，请阅读本协议。", "用户协议")}
{part(None, "", None, f'''<div class="doc">
<p class="meta">更新日期：2026 年 10 月 27 日</p>
<h2>一、协议双方与适用范围</h2>
<p>本协议是你与 {COMPANY}（以下称“我们”）之间关于使用本网站及我们提供的软件和服务的约定。单位客户与我们另行签订合同的，以合同为准；合同未约定的，适用本协议。</p>
<h2>二、服务内容</h2>
<p>我们提供人工智能应用软件与工业软件、信息系统集成、技术服务、教学软件与课程资源、教育咨询和技术咨询。具体功能、期限和费用以合同为准。网站上的产品介绍和演示画面使用虚构的演示企业和数据。</p>
<h2>三、账号</h2>
<p>注册账号需提供真实的手机号等身份信息。你应妥善保管账号和密码，对账号下的行为负责；发现被盗用请及时联系我们。</p>
<h2>四、使用规范</h2>
<p>你不得利用本网站和我们的产品制作、复制、发布、传播法律法规禁止的信息；不得侵犯他人知识产权或其他合法权益；不得攻击、破坏系统，不得以自动化方式大量抓取数据，不得绕过安全措施。违反的，我们有权停止服务并依法处理。</p>
<h2>五、AI 生成的内容</h2>
<p>AI 功能生成的文字、图片、音视频标注“AI 生成”，仅供参考和起草之用，可能存在错误。凡涉及设计、质量、财务、教学评分等决定，以有权限的人员审核批准为准。你不得删除或篡改 AI 生成内容的标识。</p>
<h2>六、知识产权</h2>
<p>本网站和我们的软件、教材、动画、课件、计算方法的知识产权归我们或相应权利人所有。你上传的资料和在服务中产生的业务数据归你或你所在的单位所有，我们只为向你提供服务而使用。</p>
<h2>七、个人信息</h2>
<p>我们按<a href="/privacy/">《隐私政策》</a>处理个人信息。</p>
<h2>八、责任限制</h2>
<p>我们尽力保证服务稳定、计算正确，但因不可抗力、第三方原因或你未按说明使用造成的损失，我们在法律允许的范围内不承担责任。合同另有约定的，从其约定。</p>
<h2>九、协议的变更与终止</h2>
<p>我们可能更新本协议，并在本页公布；你继续使用即视为接受。你可以随时停止使用并注销账号。</p>
<h2>十、法律适用与争议解决</h2>
<p>本协议适用中华人民共和国法律。因本协议发生的争议，双方协商解决；协商不成的，提交我们住所地有管辖权的人民法院诉讼解决。</p>
<h2>十一、联系方式</h2>
<p>{EMAIL}，{PHONE}，{ADDRESS}</p>
</div>''')}"""
    page("/terms/", "用户协议", "问渠科技用户协议。", body, "/terms/")


def ai_notice():
    body = f"""{hero("AI 服务说明", "AI 服务说明", "我们的产品怎样使用人工智能。", "AI 服务说明")}
{part(None, "", None, f'''<div class="doc">
<h2>一、使用哪个模型</h2>
<p>本网站和我们产品中的 AI 功能调用已备案的境内大模型（DeepSeek）。生成式人工智能服务登记编号：{AI_REG}。</p>
<h2>二、AI 做什么、不做什么</h2>
<p>AI 只起草和建议：文件、程序、方案、课程、评分建议，都要有权限的人审批后才生效；系统记录谁批准、何时批准、批准的是哪一版。AI 不替人签字，不自动下达生产、采购、发布等决定。</p>
<h2>三、内容标识</h2>
<p>依照《人工智能生成合成内容标识办法》，AI 生成的文字、图片、音频、视频在产品界面中显示“AI 生成”标识；导出的文件中保留标识。</p>
<h2>四、数据</h2>
<p>你提交给 AI 功能的内容存于境内，仅用于完成你的任务，不用于训练第三方模型。详见<a href="/privacy/">《隐私政策》</a>。</p>
<h2>五、投诉与举报</h2>
<p>对 AI 生成的内容有疑问或发现违法违规内容，请见<a href="/report/">投诉与举报</a>。</p>
</div>''')}"""
    page("/ai/", "AI 服务说明", "问渠科技 AI 服务说明：调用已备案模型、AI 起草人审批、生成内容标识。", body, "/ai/")


def report():
    body = f"""{hero("投诉与举报", "投诉与举报", "发现违法违规内容、侵权内容，或对我们的服务有投诉，请告诉我们。", "投诉与举报")}
{part(None, "", None, f'''<div class="doc">
<p>邮箱：{EMAIL}<br>电话：{PHONE}<br>地址：{ADDRESS}</p>
<p>请写明：涉及的网址或页面、内容说明、你的联系方式；涉及侵权的，请附权属证明。我们收到后会及时处理，并在 15 个工作日内答复。</p>
<p>你也可以向有关部门举报：中央网信办（国家互联网信息办公室）违法和不良信息举报中心，网址 www.12377.cn，电话 12377。</p>
</div>''')}"""
    page("/report/", "投诉与举报", "问渠科技投诉与举报渠道。", body, "/report/")


# ================================================================ 生成

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for p in (HERE / "assets").glob("*.jpg"):
        shutil.copy2(p, OUT / "assets" / p.name)
    shutil.copy2(HERE / "cn.css", OUT / "assets" / "cn.css")
    shutil.copy2(HERE / "cn.js", OUT / "assets" / "cn.js")
    (OUT / "assets" / "logo.svg").write_text(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'), encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    page("/404/", "页面不存在", "页面不存在。", hero("404", "这一页不存在", "可能是网址打错了，或者页面已经移走。", None, [("回首页", "/"), ("预约演示", "/contact/")]))
    (OUT / "404" / "index.html").rename(OUT / "404.html")
    (OUT / "404").rmdir()
    for f in (home, qms, platform, sewing, cam, custom, services, education, edu_platform, consulting, cases, about, contact,
              privacy, terms, ai_notice, report):
        f()
    n = len(list(OUT.rglob("index.html")))
    print(f"site/{OUT.name}: {n} 个页面")


if __name__ == "__main__":
    main()
