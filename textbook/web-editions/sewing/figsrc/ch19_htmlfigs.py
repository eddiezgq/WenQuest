# -*- coding: utf-8 -*-
"""第 19 章框图（中英两版）：写出 figsrc/ch19_<name>.zh.html / .en.html，再用 fig.js 渲染到 img/ 与 img/en/。
python3 figsrc/ch19_htmlfigs.py"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
HEAD = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">'
CSS = """<style>
.box span.chip,.chip{display:inline-block;color:#1b2430;border:1.5px solid #9aa4ae;border-radius:6px;background:#fff;padding:2px 7px;margin:2px 3px;font-size:12.5px;white-space:nowrap}
.chip.g{border-color:#2e9e5b}.chip.b{border-color:#2a6fdb}.chip.o{border-color:#e0662f}.chip.p{border-color:#8a5cc7}.chip.t{border-color:#14797f}.chip.y{border-color:#c48a17}
.lay{display:grid;grid-template-columns:150px 1fr;gap:8px;align-items:stretch;margin-bottom:8px}
.lab{display:flex;flex-direction:column;justify-content:center;border-radius:8px;padding:6px 10px;font-size:13px}
.lab b{font-size:14px}
.mono{font-family:"DejaVu Sans Mono",monospace;font-size:12px}
.arrow{font-size:22px;color:#5a6570;text-align:center;align-self:center}
.small{font-size:12px;color:#5a6570}
ul.t{margin:4px 0 0;padding-left:16px;text-align:left;font-size:12.5px;color:#1b2430}
ul.t li{margin:1px 0}
.gantt{display:grid;grid-template-columns:190px repeat(12,minmax(0,1fr));gap:3px 2px;font-size:12.5px;align-items:center}
.gantt .h{font-size:11.5px;color:#5a6570;text-align:center}
.bar{height:18px;border-radius:4px}
.ms{font-size:12px;font-weight:700;text-align:center;white-space:nowrap}
</style>"""

def fig(w, body):
    return HEAD+CSS+f'<div class="fig" style="--w:{w}px">'+body+'</div>'

# ------------------------------------------------------------ 1. 搭—测—改与三个月
def iterate(L):
    zh = L == "zh"
    t = dict(
        title="一个学生小组的三个月：搭—测—改" if zh else "Three months for a student team: build – test – change",
        sub="示意。左：每一轮迭代都从需求出发、留下数据；右：12 周计划（第 20–22 章逐项展开）" if zh else
            "Illustrative. Left: every iteration starts from the requirements and leaves data behind; right: a 12-week plan (detailed in Chapters 20–22)",
        build=("搭", "按 BOM 与接线表装；<br>固件配置、事件表初值") if zh else ("Build", "assemble from BOM and I/O map;<br>firmware config, event-table values"),
        test=("测", "单元 → SIL → HIL → 测试台；<br>脚本自动跑，结果按 REQ 编号") if zh else ("Test", "unit → SIL → HIL → bench;<br>scripts run unattended, results per REQ"),
        change=("改", "先改参数，再换模块，<br>最后才改机械") if zh else ("Change", "parameters first, then modules,<br>mechanics last"),
        core=("需求表 REQ-…", "测试报告", "固件 / 参数版本") if zh else ("Requirements REQ-…", "test reports", "firmware / parameter versions"),
        rows=[("需求表与快速配套", 1, 2, "#2a6fdb"), ("模块到货、装机与接线", 2, 4, "#2e9e5b"), ("固件框架 + SIL", 2, 5, "#8a5cc7"),
              ("功能补全 + HIL", 6, 9, "#8a5cc7"), ("测试台：自动测试与迭代", 8, 12, "#e0662f"), ("演示与报告", 12, 12, "#c48a17")] if zh else
             [("Requirements & configuration", 1, 2, "#2a6fdb"), ("Modules in, assembly, wiring", 2, 4, "#2e9e5b"), ("Firmware framework + SIL", 2, 5, "#8a5cc7"),
              ("Complete functions + HIL", 6, 9, "#8a5cc7"), ("Bench: automated tests, iterate", 8, 12, "#e0662f"), ("Demo and report", 12, 12, "#c48a17")],
        ms=[("P0 能动", 6), ("P1 功能全", 9), ("验收", 12)] if zh else [("P0 runs", 6), ("P1 complete", 9), ("Sign-off", 12)],
        wk="周次" if zh else "Week", note="注：P0、P1 的退出条件见 19.8 节；实验室原型到此为止，EVT 以后的工作见图 19-8。" if zh else
            "Note: exit criteria for P0 and P1 are in Section 19.8; a lab prototype stops here, the work from EVT on is in Fig. 19-8.")
    svg = f"""<svg viewBox="0 0 360 330" width="360" height="330">
<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5a6570"/></marker></defs>
<circle cx="180" cy="172" r="112" fill="none" stroke="#c9d0d6" stroke-width="2"/>
<path d="M262,95 A112,112 0 0,1 270,240" fill="none" stroke="#5a6570" stroke-width="2.4" marker-end="url(#ah)"/>
<path d="M235,270 A112,112 0 0,1 120,268" fill="none" stroke="#5a6570" stroke-width="2.4" marker-end="url(#ah)"/>
<path d="M78,225 A112,112 0 0,1 105,85" fill="none" stroke="#5a6570" stroke-width="2.4" marker-end="url(#ah)"/>
<text x="180" y="160" text-anchor="middle" font-size="13" fill="#1b2430">{t['core'][0]}</text>
<text x="180" y="180" text-anchor="middle" font-size="13" fill="#1b2430">{t['core'][1]}</text>
<text x="180" y="200" text-anchor="middle" font-size="13" fill="#1b2430">{t['core'][2]}</text>
</svg>"""
    def box(cls, xy, k):
        x, y = xy
        return f'<div class="box {cls} fill-{cls}" style="position:absolute;left:{x}px;top:{y}px;width:200px;padding:6px 8px"><b>{t[k][0]}</b><span>{t[k][1]}</span></div>'
    left = f'<div style="position:relative;width:420px;height:400px">{svg}{box("b",(80,0),"build")}{box("o",(220,262),"test")}{box("p",(-10,262),"change")}</div>'
    g = f'<div class="gantt"><div class="small">{t["wk"]}</div>'+"".join(f'<div class="h">{i}</div>' for i in range(1, 13))
    for nm, a, b, c in t["rows"]:
        g += f'<div>{nm}</div>'+"".join('<div></div>' for _ in range(1, a))+f'<div class="bar" style="grid-column:span {b-a+1};background:{c};opacity:.85"></div>'+"".join('<div></div>' for _ in range(b+1, 13))
    g += '<div class="small">'+("里程碑" if zh else "Milestones")+'</div>'
    cells = {w: n for n, w in t["ms"]}
    g += "".join(f'<div class="ms">{("◆<br>"+cells[i]) if i in cells else ""}</div>' for i in range(1, 13))
    g += '</div>'
    body = f'<p class="title">{t["title"]}</p><p class="sub">{t["sub"]}</p><div style="display:grid;grid-template-columns:420px 1fr;gap:26px;align-items:center">{left}<div>{g}</div></div><p class="note">{t["note"]}</p>'
    return fig(1080, body)

# ------------------------------------------------------------ 2. 参考架构
def platform(L):
    zh = L == "zh"
    if zh:
        title, sub = "WQ-SC 参考架构：一套平台，四种机器", "示意。括号内为零件库的建议编号（计划入库）或已有条目；箭头旁是层间接口"
        layers = [
         ("5 数字工厂接口", "fill-k", [("主题 wq/&lt;工厂&gt;/&lt;区域&gt;/&lt;单元&gt;/&lt;类别&gt;", "k"), ("status / event / measurement / alert / cmd", "k"), ("固件与参数版本上报", "k")]),
         ("4 人机与联网", "fill-t", [("网关模块 (D-GW-WQSC)：MQTT、网页参数", "t"), ("7 英寸触摸屏 (D-HMI-PANEL，可选)", "t")]),
         ("3 实时控制", "fill-p", [("WQ-SC 主控 (D-CTL-WQSC)：Cortex-M4F、RTOS", "p"), ("编码器接口定时器 → 角度 0.1°", "p"), ("事件表 · 状态机 · HAL", "p"), ("扩展 I/O (D-IO-EXP)", "p"), ("横机：小 FPGA 逐针选针", "p")]),
         ("2 驱动", "fill-b", [("伺服驱动器 (D-DRV-SERVO)", "b"), ("步进驱动器 (D-DRV-STEP)", "b"), ("电磁铁驱动板 (D-DRV-SOL)", "b"), ("气阀驱动", "b"), ("开关电源 (D-PSU-SMPS)", "b")]),
         ("1 执行与传感", "fill-g", [("主轴伺服电机 + 2500 线编码器 (D-MOT-PMSM)", "g"), ("闭环步进 (D-MOT-STEP)", "g"), ("推拉式电磁铁 (D-SOL-PUSH)", "g"), ("气缸、电磁阀 (D-PNU-CYL/VLV)", "g"),
                           ("霍尔脚踏 (D-SNS-HALL)", "g"), ("光电 (D-SNS-PE)", "g"), ("接近开关 (D-SNS-PROX)", "g"), ("增量编码器 (D-ENC-INC)", "g")]),
         ("0 机械", "fill-y", [("现成机头（平缝、包缝）", "y"), ("滚珠丝杠 A-BSC-SFU", "y"), ("直线导轨 A-LGD-RAIL", "y"), ("同步带轮 A-PUL-HTD", "y"), ("联轴器 A-CPL-JAW", "y"), ("凸轮 C-CAM-DISC", "y")])]
        ifs = ["MQTT / 信封 JSON", "CAN FD / 以太网", "CAN FD · 脉冲/方向 · DO · 编码器 A/B/Z", "三相电流 · 线圈电流 · 气路", "轴、带、丝杠"]
        mach = [("平缝机 WQ-SC/LS", "主轴转角；剪线、拨线、倒缝、抬压脚"), ("包缝机 WQ-SC/OL", "主轴转角；链线切刀、抬压脚、吸线头"), ("电子花样机 WQ-SC/PS", "主轴转角；X–Y 电子凸轮、压框"), ("缩比横机 WQ-SC/FK", "机头位置；选针、度目、纱嘴、牵拉")]
        mh, tb = "四种原型", "时间基准"
    else:
        title, sub = "WQ-SC reference architecture: one platform, four machines", "Illustrative. Proposed library IDs (planned for the library) or existing entries in brackets; interfaces between layers on the left"
        layers = [
         ("5 Digital-factory interface", "fill-k", [("topic wq/&lt;plant&gt;/&lt;area&gt;/&lt;unit&gt;/&lt;category&gt;", "k"), ("status / event / measurement / alert / cmd", "k"), ("firmware and parameter versions reported", "k")]),
         ("4 HMI and network", "fill-t", [("Gateway (D-GW-WQSC): MQTT, web parameters", "t"), ("7-inch touch panel (D-HMI-PANEL, optional)", "t")]),
         ("3 Real-time control", "fill-p", [("WQ-SC controller (D-CTL-WQSC): Cortex-M4F, RTOS", "p"), ("encoder timer → angle in 0.1°", "p"), ("event table · state machine · HAL", "p"), ("I/O expansion (D-IO-EXP)", "p"), ("knitting: small FPGA per-needle selection", "p")]),
         ("2 Drives", "fill-b", [("Servo drive (D-DRV-SERVO)", "b"), ("Stepper drive (D-DRV-STEP)", "b"), ("Solenoid driver (D-DRV-SOL)", "b"), ("Valve drivers", "b"), ("SMPS (D-PSU-SMPS)", "b")]),
         ("1 Actuators and sensors", "fill-g", [("Spindle servo + 2500-line encoder (D-MOT-PMSM)", "g"), ("Closed-loop stepper (D-MOT-STEP)", "g"), ("Push-pull solenoid (D-SOL-PUSH)", "g"), ("Cylinders, valves (D-PNU-CYL/VLV)", "g"),
                           ("Hall pedal (D-SNS-HALL)", "g"), ("Photoelectric (D-SNS-PE)", "g"), ("Proximity (D-SNS-PROX)", "g"), ("Incremental encoder (D-ENC-INC)", "g")]),
         ("0 Mechanics", "fill-y", [("Bought-in heads (lockstitch, overlock)", "y"), ("Ball screw A-BSC-SFU", "y"), ("Linear guide A-LGD-RAIL", "y"), ("Timing pulley A-PUL-HTD", "y"), ("Coupling A-CPL-JAW", "y"), ("Cam C-CAM-DISC", "y")])]
        ifs = ["MQTT / envelope JSON", "CAN FD / Ethernet", "CAN FD · step/dir · DO · encoder A/B/Z", "phase current · coil current · air", "shafts, belts, screws"]
        mach = [("Lockstitch WQ-SC/LS", "spindle angle; trim, wipe, backtack, foot lift"), ("Overlock WQ-SC/OL", "spindle angle; chain cutter, foot lift, suction"), ("Pattern sewer WQ-SC/PS", "spindle angle; X–Y electronic cam, clamps"), ("Scaled flat knitter WQ-SC/FK", "carriage position; selection, stitch cams, carriers, take-down")]
        mh, tb = "Four prototypes", "time base"
    rows = ""
    for i, (nm, fill, chips) in enumerate(layers):
        cls = fill.split("-")[1]
        rows += f'<div class="lay"><div class="lab {fill} box {cls}" style="text-align:left"><b>{nm}</b></div><div class="box {cls}" style="text-align:left;padding:6px 8px">'+"".join(f'<span class="chip {c}">{x}</span>' for x, c in chips)+'</div></div>'
        if i < len(ifs):
            rows += f'<div style="margin:-4px 0 4px 150px;font-size:11.5px;color:#5a6570">⇅ {ifs[i]}</div>'
    right = f'<div><p style="margin:0 0 6px;font-weight:700">{mh}</p>'+"".join(f'<div class="box k" style="text-align:left;margin-bottom:8px"><b>{a}</b><span>{tb}：{b}</span></div>' if zh else f'<div class="box k" style="text-align:left;margin-bottom:8px"><b>{a}</b><span>{tb}: {b}</span></div>' for a, b in mach)+'</div>'
    body = f'<p class="title">{title}</p><p class="sub">{sub}</p><div style="display:grid;grid-template-columns:1fr 250px;gap:18px;align-items:start"><div>{rows}</div>{right}</div>'
    return fig(1180, body)

# ------------------------------------------------------------ 3. 快速配套流程
def matching(L):
    zh = L == "zh"
    if zh:
        title, sub = "快速配套：从需求表到 BOM、接线表和固件配置", "示意。实线是一次配套，虚线是迭代：测试结果回到需求表或判据"
        st = [("b", "① 需求表", ["机种、最高转速、加速时间", "负载惯量、动作清单", "X–Y 行程与速度、针数", "I/O、电源、联网"]),
              ("p", "② 计算", ["主轴转矩、惯量比、制动能量", "步进转矩–转速裕量", "电磁铁 6·n·t 折算转角", "电源预算、I/O 计数"]),
              ("g", "③ 从零件库筛选", ["按 perf 参数比判据", "每类挑最便宜的合格规格", "机械件引用已有条目", "库里没有：如实说没有"]),
              ("o", "④ 自动生成", ["BOM：编号/规格、数量、单价", "接线表：端口 ↔ 器件", "固件配置：HAL 驱动、事件表初值", "需求 ↔ 测试用例 REQ-…"]),
              ("y", "⑤ 上测试台", ["SIL、HIL、整机测试台", "pytest 脚本、报告", "结果发到 measurement 主题"])]
        lib = ("零件库条目", "entry.yaml：编号、名称、参数定义（key、中英文名、role、单位）、出处；specs.csv：一行一个规格")
        ai = ("AI 选型助手的规矩", "只从库里挑；答案写成“编号/规格”并列出依据的那一行参数和出处；库里没有就说没有，不编造；编号逐个核对")
        back = "迭代：改需求、改判据或换模块，重新配套"
    else:
        title, sub = "Rapid configuration: from requirements to BOM, I/O map and firmware configuration", "Illustrative. Solid arrows: one pass; dashed: iteration — test results go back to the requirements or the criteria"
        st = [("b", "① Requirements", ["machine type, top speed, accel time", "load inertia, list of actions", "X–Y travel and speed, needle count", "I/O, power, network"]),
              ("p", "② Calculation", ["spindle torque, inertia ratio, braking energy", "stepper torque–speed margin", "solenoid angle 6·n·t", "power budget, I/O count"]),
              ("g", "③ Filter the library", ["compare perf parameters with criteria", "cheapest passing size in each class", "mechanical parts: existing entries", "nothing suitable: say so"]),
              ("o", "④ Generate", ["BOM: ID/size, quantity, unit price", "I/O map: port ↔ device", "firmware config: HAL drivers, event table", "requirement ↔ test case REQ-…"]),
              ("y", "⑤ On the bench", ["SIL, HIL, machine test bench", "pytest scripts, reports", "results to the measurement topic"])]
        lib = ("Library entry", "entry.yaml: ID, name, parameter definitions (key, zh/en names, role, unit), sources; specs.csv: one row per size")
        ai = ("Rules of the AI selection assistant", "pick only from the library; write answers as “ID/size” with the row of parameters and the source; if nothing fits, say so and invent nothing; every ID is checked")
        back = "Iterate: change requirements, criteria or modules, and configure again"
    boxes = ""
    for i, (c, h, items) in enumerate(st):
        boxes += f'<div class="box {c} fill-{c}" style="text-align:left"><b>{h}</b><ul class="t">'+"".join(f"<li>{x}</li>" for x in items)+'</ul></div>'
        if i < len(st)-1:
            boxes += '<div class="arrow">→</div>'
    svg = f'''<svg viewBox="0 0 1120 46" width="1120" height="46" style="display:block;margin-top:6px"><defs><marker id="a2" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#c4531d"/></marker></defs>
<path d="M1050,2 L1050,30 L90,30 L90,6" fill="none" stroke="#c4531d" stroke-width="2" stroke-dasharray="7,5" marker-end="url(#a2)"/>
<text x="570" y="24" text-anchor="middle" font-size="13" fill="#c4531d">{back}</text></svg>'''
    under = f'''<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:8px">
<div class="box g" style="text-align:left"><b>{lib[0]}</b><span>{lib[1]}</span></div>
<div class="box k fill-k" style="text-align:left"><b>{ai[0]}</b><span>{ai[1]}</span></div></div>'''
    body = f'<p class="title">{title}</p><p class="sub">{sub}</p><div style="display:grid;grid-template-columns:1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr;gap:4px;align-items:stretch">{boxes}</div>{svg}{under}'
    return fig(1180, body)

# ------------------------------------------------------------ 4. 状态机
def states(L):
    zh = L == "zh"
    S = dict(IDLE=(150, 100), RUN=(390, 100), SLOW=(630, 100), TRIM=(870, 100), POSITION=(870, 260), SAFE=(510, 350))
    if zh:
        title, sub = "平缝机原型的状态机（示意）", "实线：正常的工作周期；红色虚线：任一状态检测到故障都进入 SAFE"
        desc = dict(IDLE="停在上针位，压脚抬起", RUN="脚踏调速，事件表逐针执行", SLOW="减速到剪线转速 300 r/min", TRIM="剪线那一针：剪线、拨线", POSITION="位置环停到 70°", SAFE="断电磁铁，主轴自由停或制动")
        tr = ["前掌踩下：|落压脚、起缝回针", "后跟踩下|（剪线）", "n ≤ 320 r/min|且过 180°", "第 1 转 25°：|切入位置环", "±0.5° 内保持 5 ms：拨线完、抬压脚"]
        flt = "FAULT：过流、编码器丢失、超时、急停、机头翻起"
        rst = "故障清除且脚踏回中位"
    else:
        title, sub = "State machine of the lockstitch prototype (illustrative)", "Solid: the normal cycle; red dashed: a fault detected in any state leads to SAFE"
        desc = dict(IDLE="needle up, foot raised", RUN="pedal sets speed; table runs", SLOW="slow down to 300 r/min", TRIM="trim stitch: trim, wipe", POSITION="position loop to 70°", SAFE="solenoids off, spindle stops")
        tr = ["pedal forward:|foot down, start backtack", "heel back|(trim)", "n ≤ 320 r/min|and past 180°", "rev 1 at 25°:|position loop on", "within ±0.5° for 5 ms: wipe done, foot up"]
        flt = "FAULT: over-current, encoder lost, time-out, E-stop, head tilted"
        rst = "fault cleared and pedal neutral"
    W, H = 190, 64
    col = dict(IDLE="#2a6fdb", RUN="#2e9e5b", SLOW="#c48a17", TRIM="#e0662f", POSITION="#8a5cc7", SAFE="#c0392b")
    fill = dict(IDLE="#e9f0fc", RUN="#eaf6ee", SLOW="#fbf4e3", TRIM="#fcefe8", POSITION="#f2ecfa", SAFE="#fdecea")
    svg = '<svg viewBox="0 0 1000 430" width="1000" height="430"><defs><marker id="m" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1b2430"/></marker><marker id="mr" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker><marker id="mg" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5a6570"/></marker></defs>'
    def text(x, y, s, anchor="middle", c="#1b2430", size=12.5):
        parts = s.split("|")
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{c}" stroke="#faf9f5" stroke-width="4" paint-order="stroke">' + "".join(f'<tspan x="{x}" dy="{0 if i == 0 else 15}">{p}</tspan>' for i, p in enumerate(parts)) + '</text>'
    for k, (x, y) in S.items():
        svg += f'<rect x="{x-W/2}" y="{y-H/2}" width="{W}" height="{H}" rx="10" fill="{fill[k]}" stroke="{col[k]}" stroke-width="2"/>'
        svg += text(x, y-6, k, c=col[k], size=16).replace('<text ', '<text font-weight="700" ')
        svg += text(x, y+16, desc[k], size=12)
    line = lambda x1, y1, x2, y2, c="#1b2430", mk="m", dash="", w=2: f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" {dash} marker-end="url(#{mk})"/>'
    order = ["IDLE", "RUN", "SLOW", "TRIM"]
    for i in range(3):
        a, b = S[order[i]], S[order[i+1]]
        svg += line(a[0]+W/2, a[1], b[0]-W/2-1, b[1])
        svg += text((a[0]+b[0])/2, 30, tr[i])
    svg += line(870, 100+H/2, 870, 260-H/2-1) + text(880, 175, tr[3], "start")
    svg += f'<path d="M{870-W/2},260 L30,260 L30,100 L{150-W/2-1},100" fill="none" stroke="#1b2430" stroke-width="2" marker-end="url(#m)"/>' + text(470, 252, tr[4])
    d = 'stroke-dasharray="6,4"'
    for (sx, sy), (ex, ey) in [((190, 132), (450, 318)), ((390, 132), (480, 318)), ((630, 132), (540, 318)), ((820, 132), (570, 318)), ((870-W/2, 278), (605, 340))]:
        svg += line(sx, sy, ex, ey, "#c0392b", "mr", d, 1.6)
    svg += text(510, 402, flt, c="#c0392b")
    svg += f'<path d="M{510-W/2},360 L150,360 L150,{100+H/2+1}" fill="none" stroke="#5a6570" stroke-width="1.6" stroke-dasharray="3,3" marker-end="url(#mg)"/>' + text(270, 378, rst, c="#5a6570")
    svg += '</svg>'
    body = f'<p class="title">{title}</p><p class="sub">{sub}</p>{svg}'
    return fig(1060, body)

# ------------------------------------------------------------ 5. SIL / HIL / 测试台
def hil(L):
    zh = L == "zh"
    if zh:
        title, sub = "先在电脑上“缝”：软件在环、硬件在环与整机测试台", "示意。三者跑同一套 pytest 测试用例，只换“被测对象”和“对象模型”"
        cols = [("p", "软件在环 SIL", "电脑上", ["固件（工艺层、状态机、事件表）编译成电脑程序", "HAL 换成仿真驱动", "机器模型：本书虚拟实验同款（伺服 13-1、电磁铁 13-2、剪线 14-1、花样 15、横机 17）", "按 50 µs 步长推进，比实时快几十倍"],
                 ["查：逻辑、时序表、参数边界", "每次提交自动跑（持续集成）"]),
                ("b", "硬件在环 HIL", "真主控板 + 仿真台", ["真 WQ-SC 主控板、真固件", "编码器仿真：按模型角度输出 A/B/Z，5000 r/min 时每秒 83 万个计数", "电磁铁负载：真线圈或 R–L 假负载，测电流波形", "伺服：CAN FD 上的驱动器模型；故障注入：断编码器、过流、欠压"],
                 ["查：中断时序、驱动、故障处理", "夜间批量跑几千个周期"]),
                ("o", "整机测试台", "真机头", ["真机头、真伺服、真电磁铁", "转矩/转速传感器，主轴编码器记录", "相机拍线迹，计数剪线成败", "环境：电压 ±10%、温度"],
                 ["查：机械与电控的配合、寿命", "验收指标：停针 ±1°、剪线 99.5%"])]
        pc = "测试电脑：pytest 脚本 → 网关 API/MQTT → 结果写报告并发到 …/measurement（第 22 章）"
    else:
        title, sub = "Sewing on the computer first: software-in-the-loop, hardware-in-the-loop and the machine bench", "Illustrative. All three run the same pytest cases; only the unit under test and the plant model change"
        cols = [("p", "Software-in-the-loop (SIL)", "on a PC", ["firmware (process layer, state machine, event table) built as a PC program", "HAL replaced by simulated drivers", "plant: the models of this book’s labs (servo 13-1, solenoid 13-2, trimming 14-1, pattern Ch. 15, knitting Ch. 17)", "50 µs steps, tens of times faster than real time"],
                 ["finds: logic, timing tables, parameter limits", "runs on every commit (CI)"]),
                ("b", "Hardware-in-the-loop (HIL)", "real board + simulator", ["real WQ-SC controller, real firmware", "encoder emulator: A/B/Z from the model angle, 833 000 counts/s at 5000 r/min", "solenoid load: real coil or R–L dummy, current recorded", "servo: drive model on CAN FD; fault injection: encoder loss, over-current, under-voltage"],
                 ["finds: interrupt timing, drivers, fault handling", "thousands of cycles overnight"]),
                ("o", "Machine test bench", "real head", ["real head, servo and solenoids", "torque/speed transducer, spindle encoder log", "camera on the seam, trim success counted", "environment: supply ±10 %, temperature"],
                 ["finds: mechanics–control interplay, endurance", "acceptance: needle stop ±1°, trimming 99.5 %"])]
        pc = "Test PC: pytest scripts → gateway API/MQTT → report, results published to …/measurement (Chapter 22)"
    out = ""
    for c, h, s, items, finds in cols:
        out += f'<div class="box {c}" style="text-align:left"><b>{h}</b><span>{s}</span><ul class="t">'+"".join(f"<li>{x}</li>" for x in items)+f'</ul><div class="box {c} fill-{c}" style="margin-top:8px;text-align:left;padding:5px 8px"><ul class="t" style="margin:0">'+"".join(f"<li>{x}</li>" for x in finds)+'</ul></div></div>'
    arrow = '<div style="text-align:center;font-size:12.5px;color:#5a6570;margin:6px 0">'+("越往右越真实、越慢、越贵 →" if zh else "more realistic, slower and costlier to the right →")+'</div>'
    body = f'<p class="title">{title}</p><p class="sub">{sub}</p><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px">{out}</div>{arrow}<div class="box k fill-k">{pc}</div>'
    return fig(1120, body)

# ------------------------------------------------------------ 6. 成熟度
def gates(L):
    zh = L == "zh"
    if zh:
        title, sub = "从原型到工业级：P0 → P1 → EVT → DVT → PVT → 量产", "示意。每一级的退出条件都写成自动测试的通过率和指标；数量、比例为示意值"
        st = [("g", "P0 能动", "1 台", "现成机头 + 模块", ["主轴调速、停针", "事件表驱动电磁铁", "SIL 全部通过"], "停针 ≤ ±3°；HIL 冒烟测试通过"),
              ("g", "P1 功能全", "1–2 台", "模块化原型", ["全部动作、联网上报", "需求 100% 有用例", "测试台自动跑"], "用例通过 ≥ 95%；停针 ≤ ±1°；剪线 1000 次 ≥ 99.5%"),
              ("b", "EVT 工程验证", "3–5 台", "集成电控板、机箱", ["模块合成一块板", "热、电源、初测 EMC", "4 h 满速运转"], "全部 REQ 用例通过；温升合格（第 18 章）"),
              ("p", "DVT 设计验证", "10–20 台", "设计冻结", ["EMC、安全、环境试验", "可靠性与寿命", "认证送样"], "标准试验通过；寿命试验无关键故障"),
              ("o", "PVT 小批验证", "50–200 台", "量产工装", ["产线装配、EOL 测试", "老化（第 18 章）", "数据回流数字工厂"], "EOL 一次通过率 ≥ 98%；返修原因已闭环"),
              ("y", "量产", "—", "", ["EOL 数据 → 历史库", "固件与参数版本受控", "现场数据回到需求表"], "")]
        lab = ("数量", "形态", "退出条件")
    else:
        title, sub = "From prototype to industrial grade: P0 → P1 → EVT → DVT → PVT → mass production", "Illustrative. Every exit criterion is a pass rate of automated tests or a measured indicator; quantities are illustrative"
        st = [("g", "P0 runs", "1 unit", "bought-in head + modules", ["spindle speed, needle stop", "event table drives solenoids", "all SIL tests pass"], "stop ≤ ±3°; HIL smoke tests pass"),
              ("g", "P1 complete", "1–2 units", "modular prototype", ["all actions, network reporting", "every requirement has a test", "bench runs unattended"], "≥ 95 % cases pass; stop ≤ ±1°; trimming ≥ 99.5 % of 1000"),
              ("b", "EVT engineering", "3–5 units", "integrated board and box", ["modules merged into one board", "thermal, supply, EMC pre-scan", "4 h at top speed"], "all REQ cases pass; temperature rise OK (Ch. 18)"),
              ("p", "DVT design", "10–20 units", "design frozen", ["EMC, safety, environment", "reliability and life", "certification samples"], "standard tests passed; no critical failure in life test"),
              ("o", "PVT production", "50–200 units", "production tooling", ["line assembly, EOL test", "burn-in (Ch. 18)", "data back to the digital factory"], "EOL first-pass yield ≥ 98 %; repair causes closed"),
              ("y", "Mass production", "—", "", ["EOL data → historian", "firmware and parameter versions controlled", "field data back to requirements"], "")]
        lab = ("Quantity", "Form", "Exit criteria")
    out = ""
    for i, (c, h, q, f, items, ex) in enumerate(st):
        out += f'<div class="box {c} fill-{c}" style="text-align:left;display:flex;flex-direction:column"><b>{h}</b><span>{lab[0]}{"：" if zh else ": "}{q}</span>' + (f'<span>{lab[1]}{"：" if zh else ": "}{f}</span>' if f else '') + '<ul class="t">'+"".join(f"<li>{x}</li>" for x in items)+'</ul>' + (f'<div style="margin-top:auto;padding-top:6px;border-top:1px dashed #9aa4ae;font-size:12px"><b style="font-size:12.5px;display:inline;color:#1b2430">{lab[2]}{"：" if zh else ": "}</b>{ex}</div>' if ex else '') + '</div>'
        if i < len(st)-1:
            out += '<div class="arrow">→</div>'
    brace = ('<div style="display:grid;grid-template-columns:2fr 4fr;gap:12px;margin-top:8px;font-size:12.5px;color:#5a6570;text-align:center">'
             + ('<div style="border-top:2px solid #2e9e5b;padding-top:4px">实验室原型（第 19–22 章）</div><div style="border-top:2px solid #2a6fdb;padding-top:4px">工业化：补 EMC、热、成本、认证与生产测试（第 18、22、27 章）</div>' if zh else
                '<div style="border-top:2px solid #2e9e5b;padding-top:4px">lab prototype (Chapters 19–22)</div><div style="border-top:2px solid #2a6fdb;padding-top:4px">industrialisation: EMC, thermal, cost, certification, production test (Chapters 18, 22, 27)</div>') + '</div>')
    body = f'<p class="title">{title}</p><p class="sub">{sub}</p><div style="display:grid;grid-template-columns:1fr 18px 1fr 18px 1fr 18px 1fr 18px 1fr 18px 1fr;gap:3px;align-items:stretch">{out}</div>{brace}'
    return fig(1200, body)

FIGS = dict(iterate=iterate, platform=platform, matching=matching, states=states, hil=hil, gates=gates)

if __name__ == "__main__":
    import sys
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        for L in ("zh", "en"):
            src = os.path.join(HERE, f"ch19_{n}.{L}.html")
            open(src, "w", encoding="utf-8").write(FIGS[n](L))
            out = os.path.join(ROOT, "img", f"fig_19_{n}.png") if L == "zh" else os.path.join(ROOT, "img", "en", f"fig_19_{n}.png")
            subprocess.run(["node", os.path.join(ROOT, "fig.js"), src, out], check=True, cwd=ROOT)
