"""第 172b 轮：WQ-LS 设计说明书的版面（和《缝纫机设计与制造》网页版同一套样子）、每关章首、互动块。

spec_web.py 负责读原文、生成页面；这里是“长什么样”：样式、脚本、章首的大数字（从设计数据读，不手写）、
插在原文里的动画 / 虚拟实验 / 三维模型块。
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "设计" / "WQ-LS"
PUB = ROOT / "factory" / "digital" / "web" / "public" / "wqls"
SIMSEW = ROOT / "factory" / "designs" / "ctrl-ls" / "fw" / "out" / "sim_sew.json"
DATA_FILES = [PUB / "proto.json", PUB / "machine.json", SIMSEW]      # 章首数字读的数据：一致性测试也核对它们

GROUP_EN = {"": "Overview", "G1": "Design brief and general scheme", "G2": "Dynamics, strength and simulation", "G3": "Styling and housing casting",
            "G4": "Parts and mechanisms", "G5": "Housing process", "G6": "Web 3-D machine", "G7": "Drawings and bill of materials",
            "G8": "Completion and virtual prototype", "GC": "Controller", "标准": "Company standard"}
ONE = {   # 每关一句话（中、英）
    "G1": ("定下这台机器要做成什么样：5000 r/min 直驱平缝机的指标、四大机构的方案、时序和总体布置。",
           "What the machine must be: targets for a 5000 r/min direct-drive lockstitch, the four mechanisms, timing and layout."),
    "G2": ("一转之内每个零件的惯性力和缝纫阻力叠成主轴力矩，算平衡、上轴强度与疲劳、轴承寿命、电机与惯量，并用 MuJoCo 复核。",
           "Inertia of every part and sewing resistance add up to the shaft torque over one turn: balance, shaft strength and fatigue, bearings, motor and inertia, cross-checked with MuJoCo."),
    "G3": ("三个外观方案里定了 B，机壳做成上下两件 HT250 铸件，用模态和壁厚复算把关。",
           "Option B of three stylings; the housing is two HT250 castings, checked by modal analysis and wall thickness."),
    "G4": ("刺布挑线、旋梭、送布、压脚和操纵件、剪线和电子针距，每一个零件都是 FreeCAD 实体，每组一转一检干涉。",
           "Needle and take-up, hook, feed, presser and controls, trimmer and electronic stitch: every part a FreeCAD solid, every group checked for interference over a turn."),
    "G5": ("机壳从铸造到机加工：凝固仿真、工艺卡、夹具、数控程序和三坐标检测计划。",
           "The housing from casting to machining: solidification, process sheets, fixtures, NC programs and CMM plan."),
    "G6": ("整台机器搬上网页：所有零件、每 2° 的运动、8 种变型，点零件看物料号和图纸。",
           "The whole machine in the browser: every part, motion every 2°, 8 variants; click a part for item number and drawing."),
    "G7": ("8 种变型的物料清单和零件工程图，由设计直接生成。", "Bills of materials for the 8 variants and detail drawings, generated from the design."),
    "G8": ("把整机补全，再做虚拟样机验证：三维、装配、运动学、动力学、有限元疲劳、样机验证、工程图。",
           "Complete the machine, then verify it as a virtual prototype: 3-D, assembly, kinematics, dynamics, FEA and fatigue, prototype checks, drawings."),
    "GC": ("主轴伺服控制器：方案与选型、伺服仿真、示例固件在 Renode 里接整机负载跑工作周期，打样调试步骤。",
           "The main-shaft servo controller: architecture, servo simulation, example firmware running the work cycle against the machine load in Renode, bring-up steps."),
    "标准": ("缝纫机用螺纹与螺钉的企业标准，零件库条目由它生成。", "Company standard for sewing-machine threads and screws; library entries are generated from it."),
}

# 互动块：kind（动画 / 虚拟实验 / 三维模型）、标题、说明、网址（相对 spec/）
LABS = {
    "proto": ("虚拟样机", "Virtual prototype", "WQ-LS 整机虚拟样机", "WQ-LS virtual prototype",
              "真设计的全部零件在转：布料被一针针送走、布面出线迹；脚踏工作周期是控制器固件在 Renode 里跑出来的；仪表盘显示转速、力矩、电流、惯性力和挑线余量。",
              "Every part of the real design in motion: fabric fed stitch by stitch with the seam forming; the pedal cycle is the controller firmware run in Renode; gauges show speed, torque, current, inertia and take-up margin.",
              "../index.html?proto=1&lang=zh"),
    "proto_man": ("虚拟实验", "Virtual lab", "转速与驱动力矩", "Speed and drive torque",
                  "拖脚踏定转速：一转的驱动力矩曲线（G2 dyn.py：惯性部分随转速平方变）、电机电流、针杆和挑线杆惯性力当场变。",
                  "Set the speed with the pedal: the drive torque over one turn (G2 dyn.py, inertia scales with speed squared), motor current and inertia forces update live.",
                  "../index.html?proto=manual&lang=zh"),
    "timing": ("动画", "Animation", "整机时序图（和三维同步）", "Timing diagram (synced with 3-D)",
               "拖时序图上的竖线，三维整机转到同一个角度：针、挑线、旋梭、送布一转里各在做什么。",
               "Drag the line on the diagram and the 3-D machine turns to the same angle: what needle, take-up, hook and feed do in one turn.",
               "../timing.html?lang=zh"),
    "takeup": ("虚拟实验", "Virtual lab", "挑线四连杆虚拟实验", "Take-up linkage lab",
               "拖曲柄看挑线杆和线眼轨迹；拖滑块改杆长、支点，衬里、棉布、轻牛仔三种布厚的供线、耗线和判据当场重算；可切换 G4 原机构对比。",
               "Turn the crank to see the lever and eye path; drag sliders to change lengths and pivot, and supply, demand and criteria for three fabrics are recomputed; switch to the G4 original to compare.",
               "../takeup.html?lang=zh"),
    "asm": ("动画", "Animation", "机头 19 步装配", "19-step head assembly",
            "零件按总装顺序沿真实装入路线一个个装进机壳；每一步都用三维逐 2 mm 查过不碰。",
            "Parts go into the housing one by one along their real insertion paths, in assembly order; each step was checked for clearance every 2 mm in 3-D.",
            "../index.html?asm=1&lang=zh"),
    "m3d": ("三维模型", "3-D model", "整机三维", "The complete machine in 3-D",
            "转、爆炸、剖开，点零件看物料号、材料、质量、图纸和计算书那一节。", "Turn, explode and section it; click a part for item number, material, mass, drawing and calculation.",
            "../index.html?lang=zh"),
    "spin": ("三维模型", "3-D model", "整机外观", "Exterior", "外观方案 B、HT250 机壳，整机慢慢转。", "Styling B, HT250 housing, slowly turning.",
             "../index.html?embed=1&view=whole&spin=1&lang=zh"),
    "v_needle": ("三维模型", "3-D model", "刺布与挑线机构", "Needle and take-up mechanism", "只亮刺布挑线这一组，其余半透明，主轴在转。",
                 "Only the needle and take-up group lit, the rest see-through, shaft turning.", "../index.html?embed=1&view=face&focus=needle&lang=zh"),
    "v_hook": ("三维模型", "3-D model", "旋梭组", "Hook group", "下轴、1 : 2 齿轮、旋梭轴、旋梭；梭尖在 206° 从针后掠过钩住线环。",
               "Lower shaft, 1 : 2 gears, hook shaft, hook; the point passes behind the needle at 206° and catches the loop.", "../index.html?embed=1&view=hook&focus=hook&lang=zh"),
    "v_feed": ("三维模型", "3-D model", "送布组", "Feed group", "送布偏心、调节器、摆轴、牙架和抬牙；送布牙走椭圆轨迹。",
               "Feed eccentric, regulator, rock shafts, dog carrier and lift; the dog traces its ellipse.", "../index.html?embed=1&view=feed&focus=feed&lang=zh"),
    "v_press": ("三维模型", "3-D model", "压脚与操纵件", "Presser and controls", "压脚、手抬和膝抬、松线、针距旋钮和倒缝扳手。",
                "Presser foot, hand and knee lift, tension release, stitch dial and reverse lever.", "../index.html?embed=1&view=press&focus=press&lang=zh"),
    "v_trim": ("三维模型", "3-D model", "自动剪线", "Thread trimmer", "剪线凸轮带动动刀；看“剪线那一转”。",
               "The trim cam drives the moving knife; see the trimming turn.", "../index.html?embed=1&view=trim&focus=optT&opt=T&lang=zh"),
}
# 插在原文哪一节标题后面（标题里含这段字；找不到就报错，原文改了标题要跟着改这里）
INSERTS = {
    "G1/设计任务书.md": [("五、G1 校核结果", "timing")],
    "G4/刺布与挑线机构.md": [("结论", "v_needle"), ("二、新挑线四连杆怎么定的", "takeup")],
    "G4/旋梭组.md": [("一、位置怎么定的", "v_hook")],
    "G4/送布组.md": [("一、", "v_feed")],
    "G4/压脚与操纵件.md": [("一、", "v_press")],
    "G4/剪线与电子针距.md": [("一、", "v_trim")],
    "G8/G8.1_虚拟样机验证方案.md": [("第二步 装配", "asm"), ("第三步 运动学", "timing"), ("第三步 运动学", "takeup")],
}
HEAD_LAB = {"G1": "timing", "G2": "proto_man", "G3": "spin", "G4": "v_needle", "G6": "m3d", "G8": "asm", "GC": "proto"}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def head_numbers() -> dict:
    """每关章首的大数字：全部从设计结果文件读"""
    import sys
    sys.path[:0] = [str(Path(__file__).parent)]
    import spec as S
    proto, mach, sim = _j(PUB / "proto.json"), _j(PUB / "machine.json"), _j(SIMSEW)
    g1, g2 = _j(SRC / "G1" / "校核.json"), _j(SRC / "G2" / "结果.json")
    itf, kin = _j(SRC / "G8" / "G8.1_运动干涉.json"), _j(SRC / "G8" / "G8.1_运动学.json")
    bom = _j(SRC / "G7" / "物料清单.json")["variants"]
    rows = g1["rows"].values()
    n_ok = sum(all(v == "ok" for v in r["states"].values()) for r in rows)
    fat = min(v["S"] for v in g2["shaft"]["两支承"]["fatigue"].values())
    nparts = len(mach["parts"])
    codes = {ln["code"] for v in bom.values() for ln in v["lines"]}
    prices = [v["price"] for v in bom.values()]
    tk = proto["takeup"]["python"]["new"]
    tk_ok = sum(1 for f in proto["takeup"]["fabrics"] if tk[f]["margin"] >= 1 and tk[f]["neg"] <= 1)
    cyc = next(s for s in sim["scenarios"] if s["id"] == "cycle")["series"]
    n = lambda zh, en, v, u="": dict(zh=zh, en=en, v=v, u=u)  # noqa: E731
    return {
        "G1": [n("额定转速", "Rated speed", f"{S.SEW['n']:,}".replace(",", " "), "r/min"), n("最大针距", "Max stitch", f"{max(S.STITCH_RANGE):g}", "mm"),
               n("G1 校核", "G1 checks", f"{n_ok}/{len(g1['rows'])}", "合格 pass"), n("钩线角", "Hook catch", f"{kin['catch']['angle']:.1f}", "°")],
        "G2": [n("驱动力矩峰值", "Peak drive torque", f"{g2['torque']['T_max']:.2f}", "N·m"), n("平均缝纫功率", "Mean sewing power", f"{g2['torque']['P_mean']:.0f}", "W"),
               n("MuJoCo 对照最大差", "MuJoCo max difference", f"{g2['mujoco']['max_diff']:.3f}", "N·m"), n("上轴疲劳安全系数", "Shaft fatigue safety", f"{fat:.1f}", "≥ 1.5")],
        "G3": [n("外观方案", "Styling options", f"{len(list((SRC / 'G3').glob('方案*_前视.png')))}", "选 B chose B"), n("机壳材料", "Housing material", "HT250", ""),
               n("机壳铸件", "Housing castings", "2", "上下件 upper/lower")],
        "G4": [n("零件", "Parts", f"{nparts}", "FreeCAD"), n("挑线量", "Take-up stroke", f"{tk['cotton']['Smax']:.1f}", "mm"),
               n("梭尖间隙", "Hook point gap", f"{kin['catch']['point_gap']:.2f}", "mm"), n("最大惯性力", "Peak inertia force", f"{kin['peaks'][0]['F_inertia_max']:.0f}", "N")],
        "G5": [n("数控程序", "NC programs", f"{len(list((SRC / 'G5' / '数控程序').glob('*.nc')))}", ""), n("工程图", "Drawings", f"{len(list((SRC / 'G5' / '工程图').glob('*.pdf')))}", "PDF"),
               n("工艺卡", "Process sheets", f"{len(list((SRC / 'G5').glob('工艺卡_*.pdf')))}", "")],
        "G6": [n("零件", "Parts", f"{nparts}", ""), n("运动", "Motion sets", f"{len(mach['fkeys'])}", "组 sets"), n("变型", "Variants", "8", "T · E · D")],
        "G7": [n("物料", "Items", f"{len(codes)}", "项 items"), n("变型", "Variants", f"{len(bom)}", ""), n("示例价", "Example price", f"{min(prices)}–{max(prices)}", "元 CNY")],
        "G8": [n("干涉检查", "Interference pairs", f"{len(itf['pairs'])}", "对 pairs"), n("装配", "Assembly", f"{len(proto['assembly'])}", "步全通 steps clear"),
               n("挑线三种布厚", "Take-up, 3 fabrics", f"{tk_ok}/3", "合格 pass"), n("运动学", "Kinematics", "✓" if kin["all_ok"] else "✗", "全部合格 all pass")],
        "GC": [n("固件仿真场景", "Firmware scenarios", f"{sum(1 for s in sim['scenarios'] if s['passed'])}/{len(sim['scenarios'])}", "通过 pass"),
               n("固件大小", "Firmware size", f"{sim['firmware']['flash']:,}".replace(",", " "), "B"), n("相电流峰值", "Peak phase current", f"{max(abs(x) for x in cyc['ipk']):.2f}", "A ≤ 7.5")],
    }


def lab_html(key: str, auto: bool = False, tall: bool = False) -> str:
    kz, ke, tz, te, dz, de, src = LABS[key]
    e = html.escape
    return (f'<section class="lab{" tall" if tall else ""}" data-src="{e(src)}"{" data-auto" if auto else ""}>'
            f'<div class="lab-head"><span class="lab-kind">{e(kz)} · {e(ke)}</span><h4>{e(tz)}<small>{e(te)}</small></h4></div>'
            f'<p>{e(dz)}<br><span class="en">{e(de)}</span></p><div class="lab-frame"></div>'
            f'<div class="lab-actions"><button type="button" class="run">▶ 在本页运行 · Run here</button><button type="button" class="fs">⛶ 全屏 · Full screen</button>'
            f'<a class="open" href="{e(src)}" target="_blank" rel="noopener">新窗口打开 ↗</a></div></section>')


def insert_labs(rel: str, h: str, heads: list) -> str:
    for needle, key in reversed(INSERTS.get(rel, [])):          # 倒着插：同一节后面多个块时顺序和表里一样
        hd = next((x for x in heads if x["l"] in (2, 3) and needle in x["t"]), None)
        assert hd, f"{rel} 里找不到标题“{needle}”（spec_web_ui.INSERTS）"
        m = re.search(rf'<h[23] id="{hd["id"]}"[^>]*>.*?</h[23]>', h, flags=re.S)
        h = h[:m.end()] + lab_html(key) + h[m.end():]
    return h


def videos(h: str) -> str:
    """原文写到的 .mp4：在那一段（段落、列表、表格）后面放播放器"""
    done = set()
    for m in list(re.finditer(r'href="([^"]+\.mp4)"', h)):
        u = m.group(1)
        if u in done:
            continue
        done.add(u)
        pos = h.find(u)
        ends = [(h.find(t, pos), t) for t in ("</p>", "</ul>", "</ol>", "</table></div>") if h.find(t, pos) >= 0]
        if not ends:
            continue
        at, tag = min(ends)
        cap = html.escape(Path(html.unescape(u)).stem)
        fig = f'<figure class="vid"><video src="{u}" controls muted loop playsinline preload="metadata"></video><figcaption>▶ {cap}</figcaption></figure>'
        h = h[:at + len(tag)] + fig + h[at + len(tag):]
    return h


def head_html(gid: str, gname: str, nums: list, gidx: int) -> str:
    e = html.escape
    zh1, en1 = ONE.get(gid, ("", ""))
    cards = "".join(f'<div class="num"><b>{e(str(x["v"]))}</b><i>{e(x["u"])}</i><span>{e(x["zh"])}<br><em>{e(x["en"])}</em></span></div>' for x in nums)
    lab = lab_html(HEAD_LAB[gid], auto=True, tall=True) if gid in HEAD_LAB else ""
    title = re.sub(r"^\S+\s+", "", gname) if gid != "标准" else gname
    return (f'<header class="gate"><p class="eyebrow">{"第 " + str(gidx) + " 关 · GATE " + str(gidx) if gid not in ("GC", "标准") else ("控制器 · CONTROLLER" if gid == "GC" else "标准 · STANDARD")}</p>'
            f'<span class="chno">{e(gid)}</span><h1 class="gt">{e(title)}<small>{e(GROUP_EN.get(gid, ""))}</small></h1>'
            f'<p class="one">{e(zh1)}<br><span class="en">{e(en1)}</span></p>'
            f'{f"<div class=nums>{cards}</div>" if cards else ""}{lab}<div class="seam"></div></header>')


CSS = r"""
[hidden]{display:none!important}
:root{--paper:#f5f6f3;--sheet:#fff;--ink:#1b2430;--muted:#5a6570;--rule:#d8dde1;--soft:#eceff0;--needle:#2a5fb8;--bobbin:#c4531d;--needle-soft:#e6eefb;--bobbin-soft:#fbece4;--hl:#fff3c4;--code:rgba(127,127,127,.12);
 --shadow:0 1px 2px rgba(20,30,40,.06),0 6px 24px rgba(20,30,40,.06);
 --f-display:"Noto Serif SC","Source Han Serif SC","Songti SC","STSong",serif;--f-body:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;--f-mono:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#11161b;--sheet:#182029;--ink:#e2e7ec;--muted:#9aa6b2;--rule:#2b3540;--soft:#1e2730;--needle:#7fa9f2;--bobbin:#f08c58;--needle-soft:#1c2a40;--bobbin-soft:#33221a;--hl:#4a3f12;--shadow:none;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#11161b;--sheet:#182029;--ink:#e2e7ec;--muted:#9aa6b2;--rule:#2b3540;--soft:#1e2730;--needle:#7fa9f2;--bobbin:#f08c58;--needle-soft:#1c2a40;--bobbin-soft:#33221a;--hl:#4a3f12;--shadow:none;color-scheme:dark}
*{box-sizing:border-box}
html{scroll-padding-top:72px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--f-body);font-size:16px;line-height:1.8;-webkit-text-size-adjust:100%}
a{color:var(--needle);text-underline-offset:3px}
.en{color:var(--muted);font-size:.9em}
.bar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px 16px;padding:10px max(16px,3vw);background:color-mix(in srgb,var(--paper) 90%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--rule)}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--f-display);font-weight:700;font-size:1.02rem;color:var(--ink);text-decoration:none;letter-spacing:.04em;white-space:nowrap}
.brand small{font-family:var(--f-body);font-weight:400;color:var(--muted);font-size:.78rem;letter-spacing:0}
.stitch-mark{display:inline-block;width:28px;height:8px;background:repeating-linear-gradient(90deg,var(--needle) 0 6px,transparent 6px 9px) top/100% 2px no-repeat,repeating-linear-gradient(90deg,transparent 0 3px,var(--bobbin) 3px 9px) bottom/100% 2px no-repeat}
.bar .sp{flex:1}
.bar nav{display:flex;gap:14px;font-size:.88rem;white-space:nowrap}.bar nav a{color:var(--muted);text-decoration:none}.bar nav a:hover{color:var(--ink)}
#q{width:min(260px,30vw);height:32px;border:1px solid var(--rule);border-radius:999px;padding:0 12px;background:var(--sheet);color:var(--ink);font:inherit;font-size:.86rem}
.theme,#menu{font:inherit;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:999px;height:32px;min-width:32px;cursor:pointer;font-size:.86rem}
#menu{display:none;padding:0 12px;white-space:nowrap}
.wrap{display:grid;grid-template-columns:270px minmax(0,1fr) 220px;gap:clamp(16px,3vw,40px);max-width:1440px;margin:0 auto;padding:0 16px}
nav.side{position:sticky;top:57px;height:calc(100vh - 57px);overflow:auto;padding:18px 0 40px;font-size:.86rem;line-height:1.45}
nav.side .g{margin:16px 0 4px;font-family:var(--f-mono);font-size:.72rem;letter-spacing:.12em;color:var(--muted);font-weight:600}
nav.side .g:first-child{margin-top:0}
nav.side a{display:block;color:var(--ink);text-decoration:none;padding:4px 10px;border-left:2px solid transparent;margin-left:-2px}
nav.side a:hover{color:var(--needle)}
nav.side a.cur{border-left-color:var(--needle);color:var(--needle);font-weight:600;background:var(--needle-soft);border-radius:0 6px 6px 0}
nav.side ul{list-style:none;margin:2px 0 8px 10px;padding:0;border-left:1px solid var(--rule)}
nav.side ul a{font-size:.8rem;color:var(--muted);padding:3px 10px}
nav.side ul ul{margin-left:8px}
nav.side ul a.on,aside.toc a.on{color:var(--needle);font-weight:600}
main{min-width:0;padding:22px 0 90px;max-width:900px}
.crumb{font-size:.8rem;color:var(--muted)}.crumb a{color:var(--muted)}
.meta{font-size:.76rem;color:var(--muted);margin:2px 0 14px}.meta code{font-size:.74rem}
.gate .eyebrow{font-family:var(--f-mono);font-size:.74rem;letter-spacing:.14em;color:var(--muted);margin:10px 0 4px}
.chno{display:block;font-family:var(--f-mono);font-weight:600;font-size:.9rem;letter-spacing:.1em;color:var(--bobbin);margin-bottom:4px}
h1.gt{font-family:var(--f-display);font-weight:900;font-size:clamp(1.9rem,4vw,2.6rem);line-height:1.25;margin:0}
h1.gt small{display:block;font-family:var(--f-body);font-weight:400;font-size:.95rem;color:var(--muted);margin-top:4px}
.gate .one{font-size:1.05rem;margin:12px 0 16px}
.nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:0 0 18px}
.num{background:var(--sheet);border:1px solid var(--rule);border-radius:12px;padding:12px 14px;box-shadow:var(--shadow);position:relative;overflow:hidden}
.num:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--needle)}.num:nth-child(2n):before{background:var(--bobbin)}
.num b{font-family:var(--f-mono);font-size:1.7rem;line-height:1.1;display:block;color:var(--ink)}
.num i{font-style:normal;font-size:.76rem;color:var(--muted)}
.num span{display:block;font-size:.82rem;margin-top:4px;line-height:1.35}.num em{font-style:normal;color:var(--muted);font-size:.74rem}
.seam{height:10px;margin:22px 0 26px;background:repeating-linear-gradient(90deg,var(--needle) 0 14px,transparent 14px 20px) 0 1px/100% 2px no-repeat,repeating-linear-gradient(90deg,transparent 0 11px,var(--bobbin) 11px 23px,transparent 23px 20px) 0 7px/100% 2px no-repeat}
article h1{font-family:var(--f-display);font-weight:900;font-size:clamp(1.6rem,3.2vw,2.1rem);line-height:1.3;margin:.2em 0 .6em}
article h2{font-family:var(--f-display);font-weight:700;font-size:1.4rem;line-height:1.4;margin:2.2em 0 .6em}
article h3{font-family:var(--f-display);font-weight:700;font-size:1.15rem;margin:1.8em 0 .5em}article h4{font-size:1rem;margin:1.4em 0 .4em}
article h1:target,article h2:target,article h3:target,article h4:target{background:var(--hl);border-radius:4px}
.hl{margin-left:6px;color:var(--muted);opacity:0;font-weight:400;font-size:.75em;text-decoration:none}
h1:hover .hl,h2:hover .hl,h3:hover .hl,h4:hover .hl{opacity:1}
.tbl{overflow-x:auto;margin:1.2em 0;background:var(--sheet);border:1px solid var(--rule);border-radius:10px}
table{border-collapse:collapse;font-size:.86rem;line-height:1.5;width:100%}
td,th{border-bottom:1px solid var(--rule);padding:7px 10px;vertical-align:top;text-align:left}th{background:var(--soft);font-weight:600;white-space:nowrap}tr:last-child td{border-bottom:0}
code{font:.82em/1.5 var(--f-mono);background:var(--code);padding:1px 4px;border-radius:4px}
pre{overflow-x:auto;background:var(--sheet);border:1px solid var(--rule);border-radius:10px;padding:12px 14px}pre code{background:none;padding:0}
a.fl code{color:var(--needle)}
img{max-width:100%;height:auto;border-radius:8px}a.im{display:inline-block;margin:.4em 0}
blockquote{margin:1em 0;padding:4px 16px;border-left:3px solid var(--bobbin);background:var(--bobbin-soft);border-radius:0 8px 8px 0}
.math{overflow-x:auto;margin:1em 0}math{font-size:1.08em}
.mut{color:var(--muted);font-size:.86rem}
.lab{margin:1.6em 0 1.8em;background:var(--sheet);border:1px solid var(--rule);border-radius:12px;padding:14px 18px;box-shadow:var(--shadow)}
.lab-head{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.lab-kind{font-family:var(--f-mono);font-size:.7rem;letter-spacing:.08em;color:#fff;background:var(--bobbin);border-radius:999px;padding:1px 10px}
.lab h4{font-family:var(--f-display);font-size:1.1rem;margin:0}.lab h4 small{font-family:var(--f-body);font-weight:400;color:var(--muted);font-size:.8rem;margin-left:8px}
.lab p{font-size:.9rem;margin:6px 0 8px}
.lab-frame iframe{width:100%;height:min(620px,78vh);border:0;border-radius:10px;background:#dfe3e7;display:block}
.lab.tall .lab-frame iframe{height:min(720px,82vh)}
.lab-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.lab-actions button,.lab-actions a{font:inherit;font-size:.82rem;border:1px solid var(--rule);background:var(--soft);color:var(--ink);border-radius:999px;padding:4px 12px;cursor:pointer;text-decoration:none}
.lab-actions .run{background:var(--needle);border-color:var(--needle);color:#fff}
.lab.on .run{display:none}
figure.vid{margin:1.2em 0;background:#000;border-radius:12px;overflow:hidden}figure.vid video{display:block;width:100%;max-height:70vh}
figure.vid figcaption{background:var(--sheet);color:var(--muted);font-size:.8rem;padding:6px 12px;border:1px solid var(--rule);border-top:0;border-radius:0 0 12px 12px}
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
figure{margin:0 0 14px}figcaption{font-size:.8rem;color:var(--muted);margin-top:4px;word-break:break-all}
ul.files li{margin:3px 0}
.pn{display:flex;gap:12px;margin-top:56px}
.pn a{flex:1;border:1px solid var(--rule);border-radius:12px;padding:12px 16px;color:var(--ink);text-decoration:none;background:var(--sheet)}
.pn a:hover{border-color:var(--needle)}
.pn a span{display:block;font-size:.76rem;color:var(--muted)}.pn a.nx{text-align:right}
aside.toc{position:sticky;top:57px;height:calc(100vh - 57px);overflow:auto;padding:22px 0 40px;font-size:.8rem;line-height:1.45}
aside.toc b{display:block;font-family:var(--f-mono);font-size:.7rem;letter-spacing:.12em;color:var(--muted);margin-bottom:6px}
aside.toc a{display:block;color:var(--muted);padding:3px 0 3px 10px;border-left:2px solid var(--rule);text-decoration:none}
aside.toc a.l3{padding-left:22px;font-size:.76rem}
aside.toc a.on{border-left-color:var(--needle)}
#totop{position:fixed;right:18px;bottom:18px;width:42px;height:42px;border-radius:50%;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);font-size:18px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .2s;z-index:15;box-shadow:var(--shadow)}
#totop.show{opacity:1;pointer-events:auto}
#res{display:none}
body.searching #res{display:block}body.searching article,body.searching .pn,body.searching .gate{display:none}
#res .r{display:block;border-bottom:1px solid var(--rule);padding:10px 0;color:var(--ink);text-decoration:none}
#res .r b{color:var(--needle);font-weight:600}#res .r span{display:block;font-size:.84rem;color:var(--muted)}
#res mark{background:var(--hl);color:inherit;border-radius:2px}
/* 首页 */
.hero{position:relative;margin:0 calc(50% - 50vw);background:#0f141a}
.hero iframe{display:block;width:100%;height:min(86vh,860px);border:0}
.hero .cap{position:absolute;left:max(16px,4vw);bottom:22px;pointer-events:none;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.45)}
.hero .cap b{display:block;font-family:var(--f-display);font-size:clamp(1.6rem,4vw,2.8rem);line-height:1.2}
.hero .cap span{font-size:.95rem;opacity:.9}
.home{max-width:1180px;margin:0 auto;padding:28px 16px 80px}
.home .nums{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px;margin:12px 0 30px}
.card{display:flex;flex-direction:column;background:var(--sheet);border:1px solid var(--rule);border-radius:14px;overflow:hidden;color:var(--ink);text-decoration:none;box-shadow:var(--shadow);transition:transform .15s,border-color .15s}
.card:hover{transform:translateY(-3px);border-color:var(--needle)}
.card .pv{aspect-ratio:16/9;background:var(--soft);overflow:hidden}.card .pv img,.card .pv video{width:100%;height:100%;object-fit:cover;display:block;border-radius:0}
.card .tx{padding:12px 14px}.card .tx i{font-style:normal;font-family:var(--f-mono);font-size:.74rem;color:var(--bobbin);letter-spacing:.08em}
.card .tx b{display:block;font-family:var(--f-display);font-size:1.08rem;margin:2px 0}.card .tx span{display:block;font-size:.82rem;color:var(--muted);line-height:1.5}
.notice{background:var(--needle-soft);border-radius:12px;padding:12px 16px;font-size:.92rem;margin:14px 0}
h2.sec{font-family:var(--f-display);font-size:1.5rem;margin:34px 0 4px}
@media (max-width:1280px){.wrap{grid-template-columns:250px minmax(0,1fr)}aside.toc{display:none}}
@media (max-width:900px){
 .wrap{display:block}#menu{display:inline-block}.bar nav{display:none}
 nav.side{position:fixed;left:0;top:53px;width:min(320px,86vw);height:calc(100vh - 53px);z-index:30;background:var(--paper);padding:14px 12px;transform:translateX(-105%);transition:transform .2s;box-shadow:0 8px 30px rgba(0,0,0,.25)}
 body.nav nav.side{transform:none}
 main{padding:14px 0 72px}.brand small{display:none}#q{width:auto;flex:1;min-width:0}.bar .sp{display:none}
 .lab-frame iframe,.lab.tall .lab-frame iframe{height:70vh}
}
@media print{.bar,nav.side,aside.toc,.pn,#totop,.lab-actions{display:none}.wrap{display:block}main{max-width:none;padding:0}}
"""

JS = r"""
(function(){
var b=document.body,side=document.querySelector('nav.side');
var mb=document.getElementById('menu');if(mb)mb.onclick=function(){b.classList.toggle('nav')};
if(side){side.addEventListener('click',function(e){if(e.target.closest('a'))b.classList.remove('nav')});var cur=side.querySelector('a.cur');if(cur)cur.scrollIntoView({block:'center'});}
// 深浅色
var th=document.getElementById('theme');function setT(v){if(v)document.documentElement.setAttribute('data-theme',v);else document.documentElement.removeAttribute('data-theme');}
try{setT(localStorage.getItem('wq-spec-theme'))}catch(e){}
if(th)th.onclick=function(){var d=document.documentElement.getAttribute('data-theme'),dark=d?d==='dark':matchMedia('(prefers-color-scheme: dark)').matches,v=dark?'light':'dark';setT(v);try{localStorage.setItem('wq-spec-theme',v)}catch(e){}};
// 互动块：点“在本页运行”才载入（章首和首页的自动载入，滚到附近再载）
function run(s){if(s.classList.contains('on'))return;s.classList.add('on');var f=document.createElement('iframe');f.src=s.dataset.src;f.loading='lazy';f.allow='fullscreen';f.title=(s.querySelector('h4')||{}).textContent||'';s.querySelector('.lab-frame').appendChild(f);}
document.querySelectorAll('section.lab').forEach(function(s){s.querySelector('.run').onclick=function(){run(s)};
 s.querySelector('.fs').onclick=function(){run(s);var f=s.querySelector('iframe');(f.requestFullscreen||f.webkitRequestFullscreen||function(){}).call(f)};});
var auto=[].slice.call(document.querySelectorAll('section.lab[data-auto], .hero[data-src]'));
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){io.unobserve(e.target);if(e.target.classList.contains('hero')){var f=e.target.querySelector('iframe');if(!f.src)f.src=e.target.dataset.src;}else run(e.target);}})},{rootMargin:'200px'});auto.forEach(function(s){io.observe(s)});}
else auto.forEach(function(s){if(s.classList.contains('hero'))s.querySelector('iframe').src=s.dataset.src;else run(s)});
// 读到哪一节，左右目录跟着高亮
var hs=[].slice.call(document.querySelectorAll('article h1[id],article h2[id],article h3[id]'));
var links={};[].forEach.call(document.querySelectorAll('nav.side ul a,aside.toc a'),function(a){var h=a.getAttribute('href').split('#')[1];(links[h]=links[h]||[]).push(a)});
var last=null,tt=document.getElementById('totop');
function spy(){var y=window.scrollY+100,id=hs.length?hs[0].id:null;for(var i=0;i<hs.length;i++){if(hs[i].getBoundingClientRect().top+window.scrollY<=y)id=hs[i].id;else break}
 if(tt)tt.classList.toggle('show',window.scrollY>600);
 if(id===last)return;if(last&&links[last])links[last].forEach(function(a){a.classList.remove('on')});last=id;
 if(id&&links[id])links[id].forEach(function(a){a.classList.add('on');var box=a.closest('nav.side,aside.toc');if(!box)return;var r=a.getBoundingClientRect(),rb=box.getBoundingClientRect();if(r.top<rb.top+40||r.bottom>rb.bottom-40)box.scrollTop+=r.top-rb.top-rb.height/2});}
window.addEventListener('scroll',spy,{passive:true});spy();
if(tt)tt.onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};
// 全文搜索
var q=document.getElementById('q'),res=document.getElementById('res'),idx=null,t=null;if(!q)return;
function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function go(){var s=q.value.trim();if(!s){b.classList.remove('searching');return}
 if(!res){location.href='index.html?q='+encodeURIComponent(s);return}
 if(!idx){fetch('search.json').then(function(r){return r.json()}).then(function(d){idx=d;go()});return}
 var ws=s.toLowerCase().split(/\s+/),out=[],n=0;
 idx.forEach(function(e){var x=e.x.toLowerCase(),tl=e.t.toLowerCase();if(!ws.every(function(w){return x.indexOf(w)>=0||tl.indexOf(w)>=0}))return;
  var p=x.indexOf(ws[0]),a=Math.max(0,p-40),snip=(a?'…':'')+e.x.substr(a,140)+'…';
  var hl=esc(snip);ws.forEach(function(w){hl=hl.replace(new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi'),function(m){return'<mark>'+m+'</mark>'})});
  if(n++<200)out.push('<a class="r" href="'+e.u+'#'+e.id+'"><b>'+esc(e.t)+'</b><span>'+esc(e.p)+'</span><span>'+hl+'</span></a>')});
 res.innerHTML='<p class="mut">“'+esc(s)+'”：'+n+' 处'+(n>200?'（只列前 200 处）':'')+'。按 Esc 清除。</p>'+out.join('');b.classList.add('searching');window.scrollTo(0,0)}
q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(go,180)});
q.addEventListener('keydown',function(e){if(e.key==='Escape'){q.value='';go()}if(e.key==='Enter')go()});
document.addEventListener('keydown',function(e){if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus()}});
var m=location.search.match(/[?&]q=([^&]+)/);if(m){q.value=decodeURIComponent(m[1]);go()}
})();
"""


def bar_html(menu: bool = True) -> str:
    return ('<header class="bar">' + ('<button id="menu" aria-label="目录">☰ 目录</button>' if menu else '') +
            '<a class="brand" href="index.html"><span class="stitch-mark"></span>WQ-LS 设计说明书<small>Design documentation</small></a>'
            '<nav><a href="index.html">总览</a><a href="../index.html?proto=1&lang=zh" target="_blank">虚拟样机 ↗</a><a href="../index.html?lang=zh" target="_blank">三维整机 ↗</a></nav>'
            '<span class="sp"></span><input id="q" type="search" placeholder="搜索全文（/）" aria-label="搜索全文">'
            '<button class="theme" id="theme" aria-label="深浅色">◐</button></header>')


def home_html(site, nums_all: dict, readme: str, groups) -> str:
    """首页：整机虚拟样机做大图，下面大数字、十关卡片、README"""
    e = html.escape
    proto = _j(PUB / "proto.json")
    mach = _j(PUB / "machine.json")
    big = [dict(zh="额定转速", en="Rated speed", v="5 000", u="r/min"), dict(zh="零件（FreeCAD 实体）", en="Parts (FreeCAD solids)", v=str(len(mach["parts"])), u=""),
           dict(zh="变型", en="Variants", v="8", u="T · E · D"), dict(zh="挑线量", en="Take-up stroke", v=f"{proto['takeup']['python']['new']['cotton']['Smax']:.1f}", u="mm"),
           dict(zh="设计关", en="Design gates", v=str(len([g for g in groups if g[0] not in ('标准',)])), u="G1–G8 · GC"),
           dict(zh="装配", en="Assembly", v=str(len(proto["assembly"])), u="步 steps")]
    cards = "".join(f'<div class="num"><b>{e(x["v"])}</b><i>{e(x["u"])}</i><span>{e(x["zh"])}<br><em>{e(x["en"])}</em></span></div>' for x in big)
    PREVIEW = {"G1": "G1/机构运动简图.png", "G7": "G6/爆炸.png", "G8": "G8/G8.1_整机爆炸.png", "GC": "GC/控制器框图.png", "标准": "G8/G8.1_挑线供线.png"}
    pv = {}
    for gid, _, _ in groups:
        d = SRC / gid
        vids = sorted(d.glob("*.mp4")) if d.exists() else []
        imgs = sorted(d.glob("*.png")) if d.exists() else []
        pv[gid] = SRC / PREVIEW[gid] if gid in PREVIEW else (vids[0] if vids else (imgs[0] if imgs else None))
    out = []
    for gid, gname, _ in groups:
        ps = [p for p in site.pages if p["group"] == gid and not p.get("attach")]
        if not ps:
            continue
        f = pv.get(gid)
        media = ""
        if f is not None:
            u = site.asset(str(f.relative_to(SRC)))
            media = (f'<video src="{e(u)}" muted loop playsinline autoplay preload="metadata"></video>' if f.suffix == ".mp4"
                     else f'<img loading="lazy" src="{e(u)}" alt="">')
        one = ONE.get(gid, ("", ""))
        out.append(f'<a class="card" href="{ps[0]["url"]}"><div class="pv">{media}</div><div class="tx"><i>{e(gid)}</i><b>{e(re.sub(r"^\S+\s+", "", gname) if gid != "标准" else gname)}</b>'
                   f'<span>{e(one[0])}</span><span class="en">{e(GROUP_EN.get(gid, ""))} · {len(ps)} 篇</span></div></a>')
    readme = re.sub(r'<div class="tbl"><table>.*?</table></div>', "", readme, count=1, flags=re.S)
    readme = re.sub(r"<h1[^>]*>.*?</h1>", "", readme, count=1, flags=re.S)
    return (f'<div class="hero" data-src="../index.html?proto=1&pv=iso&lang=zh"><iframe title="WQ-LS 整机虚拟样机" allow="fullscreen"></iframe>'
            f'</div><div class="home"><p class="eyebrow" style="font-family:var(--f-mono);letter-spacing:.14em;color:var(--muted);font-size:.74rem;margin:0">WQ-LS · 问渠示例设计 · WENQUEST EXAMPLE DESIGN</p>'
            f'<h1 class="gt">工业直驱平缝机设计说明书<small>Direct-drive industrial lockstitch machine — design documentation</small></h1>'
            f'<p class="one" style="font-size:1.05rem">上面是这台机器的整机虚拟样机：真设计的全部零件在转、在缝，脚踏和仪表盘都来自设计计算和控制器固件仿真。'
            f'<br><span class="en">Above: the virtual prototype — every part of the real design sewing; pedal and gauges come from the design calculations and the controller firmware simulation.</span></p>'
            f'<div class="nums">{cards}</div><div class="notice">示例设计：经计算、三维和仿真校核，<b>没有实物试制</b>，所有数值是示例值。'
            f'<span class="en">Example design, checked by calculation, 3-D and simulation; no physical prototype built.</span></div>'
            f'<h2 class="sec" id="all">十关 · The gates</h2><div class="cards">{"".join(out)}</div>'
            f'<h2 class="sec">说明 · About</h2><article>{readme}</article></div>')
