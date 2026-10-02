# -*- coding: utf-8 -*-
"""Generates the HTML block diagrams of chapter 20 (zh + en) and renders them with fig.js.
Run from /home/claude/sm:  python3 figsrc/ch20_figs_html.py"""
import os, subprocess
ROOT = '/home/claude/sm'
HEAD = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">\n<style>%s</style>\n'
CSS = """
.layer{display:grid;grid-template-columns:150px 1fr;gap:12px;align-items:stretch;margin-bottom:6px}
.lname{font-size:13px;font-weight:700;color:#5a6570;display:flex;align-items:center;border-right:3px solid #d8dde1;padding-right:8px}
.row{display:grid;gap:10px}
.box b{font-size:14.5px}.box span{font-size:12px}
.id{font-family:"JetBrains Mono","DejaVu Sans Mono",monospace;font-size:11.5px;color:#14797f;display:block;margin-top:2px}
.link{display:flex;justify-content:space-around;font-size:12px;color:#5a6570;margin:2px 0 6px 162px}
.link i{font-style:normal;background:#eef1f2;border-radius:10px;padding:1px 9px}
.arrow{font-size:22px;color:#5a6570;display:flex;align-items:center;justify-content:center}
.st{border-radius:22px}
.small{font-size:12px;color:#5a6570}
.tag{display:inline-block;font-size:11px;border-radius:8px;padding:0 6px;background:#fcefe8;color:#c4531d;margin-left:4px}
.tag.n{background:#e6f3f3;color:#0f6e74}
"""
def write(name, lang, body, w=1100):
    path = f'{ROOT}/figsrc/ch20_{name}.{lang}.html'
    open(path, 'w').write(HEAD % CSS + f'<div class="fig" style="--w:{w}px">\n' + body + '\n</div>\n')
    out = f'{ROOT}/img/fig_c20_{name}.png' if lang == 'zh' else f'{ROOT}/img/en/fig_c20_{name}.png'
    subprocess.run(['node', f'{ROOT}/fig.js', path, out], check=True, cwd=ROOT)

def box(cls, title, sub='', ids=''):
    return f'<div class="box {cls}"><b>{title}</b>' + (f'<span>{sub}</span>' if sub else '') + (f'<span class="id">{ids}</span>' if ids else '') + '</div>'
def layer(name, cols, boxes):
    return f'<div class="layer"><div class="lname">{name}</div><div class="row" style="grid-template-columns:{cols}">' + ''.join(boxes) + '</div></div>'
def link(items):
    return '<div class="link">' + ''.join(f'<i>{x}</i>' for x in items) + '</div>'

# ---------------- Fig 20-1: LS architecture ----------------
T = {
'zh': dict(t='图 20-1 的内容：平缝机原型 WQ-SC/LS 的系统构成', title='平缝机原型 WQ-SC/LS 的系统构成',
  sub='示意。五层参考架构（第 19 章）落到一台平缝机上；编号为建议编号（计划入库），A/C 类为零件库已有条目',
  L=['人机与联网','实时控制','驱动与电源','执行与传感','机械（改装）'],
  b=[('网关模块','MQTT 客户端、网页参数界面','D-GW-WQSC'),('触摸屏（可选）','参数、事件表、故障码','D-HMI-PANEL'),('问渠数字工厂','wq/sewing/…/status · event · measurement',''),
     ('WQ-SC 主控板','Cortex-M4F 级 MCU + RTOS：状态机、事件表、脚踏、日志','D-CTL-WQSC'),
     ('伺服驱动器','电流环 + 速度环；位置环可在主控','D-DRV-SERVO'),('电磁铁驱动板（6 路）','24 V 强激磁 10 ms + 1 A 斩波维持，48 V 稳压管续流','D-DRV-SOL'),('开关电源 24 V','电磁铁、传感器、主控','D-PSU-SMPS'),('急停与安全回路','双触点急停、机头翻倒开关','D-SNS-PROX'),
     ('主轴伺服电机 + 编码器','2500 线，四倍频 10000 计数/转，Z 相','D-MOT-PMSM · D-ENC-INC'),('5 个推拉式电磁铁','剪线 · 拨线 · 倒缝 · 抬压脚 · 松线','D-SOL-PUSH ×5'),('脚踏霍尔传感器','0.5–4.5 V','D-SNS-HALL'),
     ('直驱：梅花联轴器','电机与主轴同轴','A-CPL-JAW'),('或带传动 1:1','同步带轮 + 带','A-PUL-HTD · C-BLT-BELT'),('复位弹簧、螺钉','电磁铁连杆复位、支架','A-SPR-CMP · A-SCR-SHC')],
  k=[['以太网 / Wi-Fi','CAN FD（参数、日志）'],['CAN FD：速度指令、状态','SPI/IO：6 路通断 + 电流回读','AI：脚踏','DI：急停、翻倒'],['U V W 动力线','A/B/Z 差分（驱动器 1:1 转发）','线圈 24 V'],['机械连接']]),
'en': dict(title='System build-up of the lockstitch prototype WQ-SC/LS',
  sub='Illustrative. The five-layer reference architecture applied to one lockstitch machine; D-… are proposed IDs (planned for the library), A/C are existing library entries',
  L=['HMI & network','Real-time control','Drives & power','Actuators & sensors','Mechanics (retrofit)'],
  b=[('Gateway module','MQTT client, web parameter page','D-GW-WQSC'),('Touch panel (optional)','parameters, event table, fault codes','D-HMI-PANEL'),('WenQuest Digital Factory','wq/sewing/…/status · event · measurement',''),
     ('WQ-SC main controller','Cortex-M4F-class MCU + RTOS: state machine, event table, pedal, log','D-CTL-WQSC'),
     ('Servo drive','current + velocity loops; position loop may run on the controller','D-DRV-SERVO'),('Solenoid driver (6 ch)','24 V boost 10 ms + 1 A chopped hold, 48 V Zener clamp','D-DRV-SOL'),('24 V power supply','solenoids, sensors, controller','D-PSU-SMPS'),('E-stop & safety chain','two-contact E-stop, head-tilt switch','D-SNS-PROX'),
     ('Spindle servo motor + encoder','2500 lines, ×4 = 10 000 counts/rev, index','D-MOT-PMSM · D-ENC-INC'),('5 push-pull solenoids','trim · wipe · backtack · foot lift · tension release','D-SOL-PUSH ×5'),('Pedal Hall sensor','0.5–4.5 V','D-SNS-HALL'),
     ('Direct drive: jaw coupling','motor coaxial with spindle','A-CPL-JAW'),('or 1:1 belt drive','timing pulleys + belt','A-PUL-HTD · C-BLT-BELT'),('Return springs, screws','solenoid linkage return, brackets','A-SPR-CMP · A-SCR-SHC')],
  k=[['Ethernet / Wi-Fi','CAN FD (parameters, log)'],['CAN FD: speed command, status','SPI/IO: 6 on/off + current read-back','AI: pedal','DI: E-stop, head tilt'],['U V W power','A/B/Z differential (repeated 1:1 by drive)','coil 24 V'],['mechanical']])}
for lang, d in T.items():
    b = d['b']; cl = ['t fill-t', 'p', 'k fill-k', 'k fill-k fill-y', 'b', 'o', 'y', 'o fill-o', 'b fill-b', 'o', 'g', 'k', 'k', 'k']
    body = f'<p class="title">{d["title"]}</p><p class="sub">{d["sub"]}</p>'
    body += layer(d['L'][0], '1fr 1fr 1.3fr', [box('t', *b[0]), box('t', *b[1]), box('k fill-k', *b[2])])
    body += link(d['k'][0])
    body += layer(d['L'][1], '1fr', [box('k fill-y', *b[3])])
    body += link(d['k'][1])
    body += layer(d['L'][2], '1fr 1.3fr 1fr 1fr', [box('b', *b[4]), box('o', *b[5]), box('y', *b[6]), box('o fill-o', *b[7])])
    body += link(d['k'][2])
    body += layer(d['L'][3], '1.2fr 1.2fr 1fr', [box('b fill-b', *b[8]), box('o fill-o', *b[9]), box('g fill-g', *b[10])])
    body += link(d['k'][3])
    body += layer(d['L'][4], '1fr 1fr 1fr', [box('k', *b[11]), box('k', *b[12]), box('k', *b[13])])
    write('lsarch', lang, body, 1150)

# ---------------- Fig 20-2: retrofit / mounting ----------------
M = {
'zh': dict(title='把机械平缝机头改成电控样机：拆什么、装什么、装在哪里', sub='示意（侧视，非比例）。圆圈编号对应表 20-1 的 BOM 行；虚线为拆下的部件',
  lab=['① 伺服电机 + 编码器（直驱，手轮装在电机后端）','② 剪线电磁铁：底板下、旋梭旁，经连杆摆动动刀','③ 拨线电磁铁：机臂前端，拨线杆扫过针下','④ 倒缝电磁铁：机臂内，拉针距调节器的倒缝杠杆','⑤ 抬压脚电磁铁：底板下，推膝控抬压脚杠杆','⑥ 松线电磁铁：机臂上，顶开夹线器松线顶杆','⑦ 机头翻倒开关（接近开关）','⑧ 脚踏霍尔传感器（台下）'],
  rm='拆下：离合器电机、V 带与带罩、机械定位器（若有）', alt='或：电机装在台下，1:1 同步带传动（编码器 Z 相与主轴每转对齐）',
  w=dict(arm='机臂', bed='底板', nb='针杆', hw='手轮', tab='台板', hook='旋梭', motor='离合器电机（拆）', belt='V 带（拆）')),
'en': dict(title='Retrofitting a mechanical lockstitch head: what comes off, what goes on, and where', sub='Illustrative side view, not to scale. Circled numbers match the BOM rows of Table 20-1; dashed parts are removed',
  lab=['① Servo motor + encoder (direct drive; handwheel on the motor\'s rear end)','② Trimmer solenoid: under the bed beside the hook, swings the moving knife via a link','③ Wiper solenoid: front of the arm, wiper sweeps under the needle','④ Backtack solenoid: inside the arm, pulls the reverse lever of the stitch regulator','⑤ Foot-lift solenoid: under the bed, pushes the knee-lift lever','⑥ Tension-release solenoid: on the arm, pushes the release pin of the tension assembly','⑦ Head-tilt switch (proximity switch)','⑧ Pedal Hall sensor (under the table)'],
  rm='Removed: clutch motor, V-belt and guard, mechanical positioner (if any)', alt='Or: motor under the table with a 1:1 timing belt (encoder index stays aligned with each spindle revolution)',
  w=dict(arm='arm', bed='bed', nb='needle bar', hw='handwheel', tab='table', hook='hook', motor='clutch motor (removed)', belt='V-belt (removed)'))}
SVG = """<svg width="640" height="430" viewBox="0 0 640 430">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#5a6570"/></marker></defs>
<rect x="40" y="250" width="470" height="40" rx="6" fill="#e9eef2" stroke="#7d8a96" stroke-width="2"/>
<path d="M450 250 L450 110 L150 110 L150 175 L90 175 L90 90 Q90 60 120 60 L470 60 Q500 60 500 90 L500 250 Z" fill="#e9eef2" stroke="#7d8a96" stroke-width="2"/>
<text x="290" y="88" font-size="14" text-anchor="middle" fill="#5a6570">{arm}</text>
<text x="300" y="276" font-size="14" text-anchor="middle" fill="#5a6570">{bed}</text>
<rect x="113" y="150" width="10" height="70" fill="#5a6570"/><line x1="118" y1="220" x2="118" y2="246" stroke="#1b2430" stroke-width="2"/><rect x="100" y="240" width="40" height="8" rx="2" fill="#7d8a96"/><text x="160" y="200" font-size="13" fill="#5a6570">{nb}</text>
<line x1="20" y1="296" x2="600" y2="296" stroke="#1b2430" stroke-width="3"/><text x="420" y="314" font-size="13" text-anchor="middle" fill="#5a6570">{tab}</text>
<circle cx="118" cy="272" r="14" fill="#fff" stroke="#7d8a96" stroke-width="2"/><text x="118" y="318" font-size="12" text-anchor="middle" fill="#5a6570">{hook}</text>
<rect x="500" y="110" width="60" height="70" rx="6" fill="#e9f0fc" stroke="#2a6fdb" stroke-width="2.5"/><circle cx="578" cy="145" r="30" fill="none" stroke="#1b2430" stroke-width="3"/>
<text x="590" y="104" font-size="12" text-anchor="middle" fill="#5a6570">{hw}</text>
<rect x="470" y="345" width="160" height="55" rx="6" fill="none" stroke="#9aa4ae" stroke-width="2" stroke-dasharray="6 5"/><text x="550" y="377" font-size="12" text-anchor="middle" fill="#9aa4ae">{motor}</text>
<line x1="578" y1="175" x2="560" y2="345" stroke="#9aa4ae" stroke-width="2" stroke-dasharray="6 5"/><text x="500" y="330" font-size="12" fill="#9aa4ae">{belt}</text>
<g font-size="15" font-weight="700" text-anchor="middle">
<circle cx="530" cy="96" r="13" fill="#2a6fdb"/><text x="530" y="101" fill="#fff">1</text>
<rect x="160" y="290" width="46" height="22" rx="4" fill="#fcefe8" stroke="#e0662f" stroke-width="2"/><circle cx="183" cy="335" r="13" fill="#e0662f"/><text x="183" y="340" fill="#fff">2</text>
<rect x="60" y="184" width="26" height="22" rx="4" fill="#fcefe8" stroke="#e0662f" stroke-width="2"/><circle cx="40" cy="196" r="13" fill="#e0662f"/><text x="40" y="201" fill="#fff">3</text>
<rect x="300" y="116" width="46" height="22" rx="4" fill="#fcefe8" stroke="#e0662f" stroke-width="2"/><circle cx="323" cy="160" r="13" fill="#e0662f"/><text x="323" y="165" fill="#fff">4</text>
<rect x="230" y="290" width="46" height="22" rx="4" fill="#fcefe8" stroke="#e0662f" stroke-width="2"/><circle cx="253" cy="335" r="13" fill="#e0662f"/><text x="253" y="340" fill="#fff">5</text>
<rect x="150" y="36" width="40" height="22" rx="4" fill="#fcefe8" stroke="#e0662f" stroke-width="2"/><circle cx="210" cy="30" r="13" fill="#e0662f"/><text x="210" y="35" fill="#fff">6</text>
<rect x="470" y="252" width="26" height="14" rx="3" fill="#eaf6ee" stroke="#2e9e5b" stroke-width="2"/><circle cx="484" cy="232" r="13" fill="#2e9e5b"/><text x="484" y="237" fill="#fff">7</text>
<rect x="60" y="390" width="70" height="16" rx="4" fill="#eaf6ee" stroke="#2e9e5b" stroke-width="2"/><circle cx="150" cy="398" r="13" fill="#2e9e5b"/><text x="150" y="403" fill="#fff">8</text>
</g></svg>"""
for lang, d in M.items():
    svg = SVG.format(**d['w'])
    items = ''.join(f'<li style="margin:4px 0">{x}</li>' for x in d['lab'])
    body = f'<p class="title">{d["title"]}</p><p class="sub">{d["sub"]}</p><div style="display:grid;grid-template-columns:640px 1fr;gap:22px;align-items:start">{svg}<div><ul style="list-style:none;padding:0;margin:0;font-size:13.5px">{items}</ul><div class="box k fill-k" style="margin-top:14px;text-align:left"><span style="color:#1b2430">{d["rm"]}</span></div><div class="box b fill-b" style="margin-top:8px;text-align:left"><span style="color:#1b2430">{d["alt"]}</span></div></div></div>'
    write('mount', lang, body, 1180)

# ---------------- Fig 20-3: firmware ----------------
F = {
'zh': dict(title='平缝机原型的固件：状态机、角度中断里的事件表、HAL', sub='示意。时间基准是主轴转角；事件表在参数里，改表不改代码',
  st=[('IDLE','压脚落下，等脚踏'),('RUN','脚踏调速；起缝回针、慢起针'),('SLOW','减速到剪线转速'),('TRIM','剪线事件表生效'),('POSITION','位置环停到上针位'),('IDLE','拨线 → 抬压脚')],
  safe=('SAFE','任一状态：过流、编码器丢失、超时、急停 → 断全部电磁铁，主轴自由停或制动'),
  tr=['前掌踩下','后跟踩到底','到剪线转速','到切入角 25°','停稳标志'],
  lay=[('角度中断 10 kHz','读编码器计数 → ψ（0.1°）；扫描事件表，跨过起/止角就开/关对应通道；回针针数计数','o'),
       ('控制任务 1 kHz','状态机、速度曲线（慢起针、加减速限幅）、位置环（K<sub>p</sub> = 200 s⁻¹）、超时','b'),
       ('后台任务','脚踏滤波、参数表与版本号、故障码、日志、网关通信（MQTT）','t'),
       ('HAL','spindle_* · sol_* · io_* · enc_*；换模块只换驱动文件','k')]),
'en': dict(title='Firmware of the lockstitch prototype: state machine, event table in the angle interrupt, HAL', sub='Illustrative. The time base is spindle angle; the event table lives in the parameters, so changing it needs no code change',
  st=[('IDLE','foot down, wait for pedal'),('RUN','pedal speed; start backtack, soft start'),('SLOW','decelerate to trim speed'),('TRIM','trim event table active'),('POSITION','position loop to needle-up'),('IDLE','wipe → lift foot')],
  safe=('SAFE','from any state: over-current, encoder lost, time-out, E-stop → all solenoids off, spindle coasts or brakes'),
  tr=['toe down','heel fully back','at trim speed','at engage angle 25°','stopped flag'],
  lay=[('Angle interrupt 10 kHz','read encoder count → ψ (0.1°); scan event table, switch a channel when its on/off angle is crossed; count backtack stitches','o'),
       ('Control task 1 kHz','state machine, speed profile (soft start, accel limits), position loop (K<sub>p</sub> = 200 s⁻¹), time-outs','b'),
       ('Background','pedal filter, parameter table and version, fault codes, log, gateway (MQTT)','t'),
       ('HAL','spindle_* · sol_* · io_* · enc_*; swap a module by swapping its driver file','k')])}
for lang, d in F.items():
    sts = []
    for i, (a, b) in enumerate(d['st']):
        sts.append(f'<div class="box st {"y fill-y" if a=="TRIM" else "b fill-b" if a in ("RUN","SLOW","POSITION") else "k fill-k"}"><b>{a}</b><span>{b}</span></div>')
        if i < 5: sts.append(f'<div class="arrow" style="flex-direction:column"><span style="font-size:11px;color:#5a6570;line-height:1.1;text-align:center">{d["tr"][i]}</span>→</div>')
    body = f'<p class="title">{d["title"]}</p><p class="sub">{d["sub"]}</p>'
    body += '<div style="display:grid;grid-template-columns:1fr 70px 1fr 70px 1fr 70px 1fr 70px 1fr 70px 1fr;gap:4px;align-items:center">' + ''.join(sts) + '</div>'
    body += f'<div class="box o fill-o" style="margin:12px 0 18px;display:flex;gap:14px;align-items:center;text-align:left"><b style="display:inline">{d["safe"][0]}</b><span style="display:inline">{d["safe"][1]}</span></div>'
    for (a, b, c) in d['lay']:
        body += f'<div class="box {c}" style="display:grid;grid-template-columns:200px 1fr;text-align:left;margin-bottom:8px;align-items:center"><b>{a}</b><span style="color:#1b2430;font-size:13px">{b}</span></div>'
    write('fw', lang, body, 1250)

# ---------------- Fig 20-7: overlock prototype ----------------
O = {
'zh': dict(title='包缝机原型 WQ-SC/OL：同一块主控，换掉的是执行器、传感器和事件表', sub='示意。灰色为与平缝机原型完全相同的模块；橙色为改动或新增',
  same='相同：WQ-SC 主控、HAL、伺服驱动器、电磁铁驱动板、24 V 电源、网关、脚踏、急停回路、测试脚本框架',
  b=[('主轴伺服 + 同步带 1:1.25','电机 5600 r/min → 主轴 7000 r/min；8000 计数/主轴转','D-MOT-PMSM · A-PUL-HTD · C-BLT-BELT'),('主轴上针位传感器','手轮处霍尔/接近开关，核对跳齿','D-SNS-PROX'),
     ('布边光电传感器','针前 25 mm，响应 ≤ 1 ms','D-SNS-PE'),('链线切刀气缸 + 吸风阀','停车后切链、吸走线头','D-PNU-CYL · D-PNU-VLV ×2'),('差动比步进电机（可选）','丝杠推差动滑块，D = 0.7–2.0','D-MOT-STEP · D-DRV-STEP · C-SCN-LEAD')],
  st=[('WAIT','无布'),('RUN','布到即起（去抖 2 针）'),('TAIL','布走后再缝 N₁ + N₂ 针'),('STOP','提前 N_b 针开始减速，停上针位'),('CUT','切链 60 ms + 吸风 300 ms')],
  tr=['布遮住传感器','布离开传感器','剩余针数 ≤ N_b','停稳'],
  nb='N₁ = 传感器到针的距离 / 针距；N₂ = 链线长度 / 针距；N_b = 从当前转速减速到停所需的转数（按惯量算，随转速平方变化）'),
'en': dict(title='Overlock prototype WQ-SC/OL: same controller; actuators, sensors and event table change', sub='Illustrative. Grey: modules identical to the lockstitch prototype; orange: changed or added',
  same='Same: WQ-SC controller, HAL, servo drive, solenoid driver, 24 V supply, gateway, pedal, E-stop chain, test-script framework',
  b=[('Spindle servo + 1:1.25 timing belt','motor 5600 r/min → spindle 7000 r/min; 8000 counts per spindle rev','D-MOT-PMSM · A-PUL-HTD · C-BLT-BELT'),('Spindle needle-up sensor','Hall/proximity at the handwheel, checks tooth jump','D-SNS-PROX'),
     ('Fabric-edge photo sensor','25 mm ahead of the needle, response ≤ 1 ms','D-SNS-PE'),('Chain-cutter cylinder + suction valve','cut the chain after stop, suck away the tail','D-PNU-CYL · D-PNU-VLV ×2'),('Differential stepper (optional)','lead screw moves the differential slider, D = 0.7–2.0','D-MOT-STEP · D-DRV-STEP · C-SCN-LEAD')],
  st=[('WAIT','no fabric'),('RUN','start when fabric arrives (debounce 2 stitches)'),('TAIL','after fabric leaves, sew N₁ + N₂ more'),('STOP','start braking N_b stitches early, stop needle-up'),('CUT','cut chain 60 ms + suction 300 ms')],
  tr=['fabric covers sensor','fabric leaves sensor','stitches left ≤ N_b','stopped'],
  nb='N₁ = sensor-to-needle distance / stitch length; N₂ = chain length / stitch length; N_b = revolutions needed to brake from the present speed (from inertia; grows with speed squared)')}
for lang, d in O.items():
    b = d['b']
    body = f'<p class="title">{d["title"]}</p><p class="sub">{d["sub"]}</p>'
    body += f'<div class="box k fill-k" style="margin-bottom:12px">{d["same"]}</div>'
    body += '<div class="row" style="grid-template-columns:repeat(5,1fr);display:grid;gap:10px">' + ''.join(box('o fill-o' if i != 1 else 'o', *x) for i, x in enumerate(b)) + '</div>'
    sts = []
    for i, (a, c) in enumerate(d['st']):
        sts.append(f'<div class="box st {"y fill-y" if a in ("TAIL","CUT") else "b fill-b"}"><b>{a}</b><span>{c}</span></div>')
        if i < 4: sts.append(f'<div class="arrow" style="flex-direction:column"><span style="font-size:11px;color:#5a6570;line-height:1.1;text-align:center">{d["tr"][i]}</span>→</div>')
    body += '<div style="display:grid;grid-template-columns:1fr 84px 1fr 84px 1fr 84px 1fr 84px 1fr;gap:4px;align-items:center;margin-top:20px">' + ''.join(sts) + '</div>'
    body += f'<p class="note">{d["nb"]}</p>'
    write('ol', lang, body, 1250)
