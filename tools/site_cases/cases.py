"""三个典型应用案例页的内容（中英成对）。

数字全部取自 freecad-ai-parts 仓库 examples/apps/out/<应用>/README.md 与 factory_flow/README.md
（《M13 典型应用全流程演练报告》，2026-10-07，M14 修订）。改数之前先核对那两份文件。
"""

REPO = "https://github.com/eddiezgq/freecad-ai-parts/tree/main/examples/apps/out/"

# 工厂一侧第 12 步（厂情中枢）三个应用是同一次演练，共用
HUB = {
    "t": ("厂情中枢", "Factory command center"),
    "s": "ok",
    "who": ("工厂 · 异常、追因、推演、动作", "Factory · anomaly, root cause, what-if, action"),
    "body": (
        "<p>演练中给一台数控车床注入“主轴过热”停机。4 s 后厂情中枢报出异常和因果链，推演两个方案并给出推荐。</p>"
        '<dl class="kv"><dt>方案 A</dt><dd>不处理，费用 0：在手订单都能按时交</dd><dt>方案 B</dt><dd>维修加急，费用 300：不改善交期</dd>'
        "<dt>推荐</dt><dd>A；演练仍批准 B，验证动作能下到车间</dd></dl>",
        "<p>During the run a CNC lathe was forced to stop (“spindle overheating”). Four seconds later the command center raised an anomaly with its causal chain, simulated two responses and recommended one.</p>"
        '<dl class="kv"><dt>Option A</dt><dd>Do nothing, cost 0: every open order still ships on time</dd><dt>Option B</dt><dd>Rush repair, cost 300: no gain in delivery</dd>'
        "<dt>Recommended</dt><dd>A. The run still approved B to prove the action reaches the shop floor</dd></dl>",
    ),
}

CASES = [
    # ------------------------------------------------------------------ 协作机器人关节
    {
        "slug": "cobot-joint",
        "no": "01",
        "name": ("协作机器人关节", "Collaborative Robot Joint"),
        "title": ("一台协作机器人的肩关节，能不能只用现成零件做出来？",
                  "Can a cobot shoulder joint be built from off-the-shelf parts alone?"),
        "lede": (
            "以 UR5e 一类协作臂为对象：先算出关节要多大力矩，再从零件库里选电机、谐波减速器和驱动器，做强度、疲劳、热分析和拓扑优化，编好数控程序；然后发布到问渠数字工厂，<b>进 ERP、排 MRP、下 MES 工单，车间把它做出来</b>。",
            "Take a UR5e-class arm. Work out the torque each joint needs, pick a motor, harmonic reducer and drive from the parts library, check strength, fatigue and heat, optimize the arm plate and write the CNC programs. Then release it to the WenQuest digital factory, <b>where ERP, MRP and MES take it all the way to finished parts</b>.",
        ),
        "facts": [
            (("肩关节峰值力矩", "Shoulder peak torque"), "92.5", "N·m"),
            (("空心轴安全系数", "Hollow shaft safety factor"), "12.8", ""),
            (("侧板柔度（优化后）", "Plate compliance (optimized)"), "933→154", ""),
            (("车间完工工单", "Work orders completed"), "3", ""),
        ],
        "parts": [
            ("RJ-201", ("RJ-201 空心输出轴", "RJ-201 hollow shaft"),
             ("<b>RJ-201</b> 空心输出轴 · 最大外径 Ø70、长 96 mm · 内孔 Ø30 贯通 · 峰值扭矩下 27.7 MPa",
              "<b>RJ-201</b> hollow output shaft · max Ø70 × 96 mm · Ø30 through bore · 27.7 MPa at peak torque")),
            ("J2-HSG", ("J2-HSG 关节壳体", "J2-HSG housing"),
             ("<b>J2-HSG</b> 关节壳体 · Ø140×90 mm · 外轮廓与 4 个螺纹底孔铣削约 5.7 min",
              "<b>J2-HSG</b> joint housing · Ø140 × 90 mm · contour and 4 tap holes milled in about 5.7 min")),
            ("upper-arm-plate", ("大臂侧板（拓扑优化）", "Arm plate (topology-optimized)"),
             ("<b>大臂侧板</b> · 425 mm · 拓扑优化保留 45% 材料，柔度 933 → 154",
              "<b>Upper-arm plate</b> · 425 mm · 45% of the material kept, compliance 933 → 154")),
        ],
        "release": ("COBOT-J2 第 1 版，带自制件 RJ-201、J2-HSG 和总装工艺", "COBOT-J2 rev 1, with made parts RJ-201, J2-HSG and the assembly routing"),
        "design": [
            {"t": ("动力学", "Dynamics"), "s": "ok", "who": ("设计院 · 多体动力学", "Design · multibody dynamics"),
             "body": (
                 "<p>大臂、小臂水平伸直，满载 5 kg，肩、肘各转 90°、用时 1 s，算出每个关节要多大力矩、多快的转速。</p>"
                 '<div class="bar"><div><span>肩 j2</span><i style="width:100%"></i><span>92.5</span></div><div><span>肘 j3</span><i style="width:45.8%"></i><span>42.4</span></div><div><span>腕 j4</span><i style="width:12.3%"></i><span>11.4</span></div></div><p class="unit">峰值力矩，N·m</p>',
                 "<p>Arm stretched out level with the full 5 kg payload; shoulder and elbow each turn 90° in 1 s. The run gives every joint’s torque and speed.</p>"
                 '<div class="bar"><div><span>Shoulder j2</span><i style="width:100%"></i><span>92.5</span></div><div><span>Elbow j3</span><i style="width:45.8%"></i><span>42.4</span></div><div><span>Wrist j4</span><i style="width:12.3%"></i><span>11.4</span></div></div><p class="unit">Peak torque, N·m</p>'),
             "side": (
                 '<dl class="kv"><dt>肩 j2 均方根</dt><dd>70.0 N·m</dd><dt>最高转速</dt><dd>20.0 rpm</dd><dt>峰值功率</dt><dd>193 W</dd><dt>手算重力矩</dt><dd>Σm·g·r = 92.5 N·m，与仿真一致</dd><dt>腕 j4 手算</dt><dd>11.4 N·m，一致</dd></dl>'
                 '<p class="course"><b>对应：</b>《机器人学》第 23–29 章动力学（编写中）；数字工厂实验 9</p>',
                 '<dl class="kv"><dt>Shoulder RMS</dt><dd>70.0 N·m</dd><dt>Max speed</dt><dd>20.0 rpm</dd><dt>Peak power</dt><dd>193 W</dd><dt>Hand check</dt><dd>Σm·g·r = 92.5 N·m, matches the simulation</dd><dt>Wrist hand check</dt><dd>11.4 N·m, matches</dd></dl>'
                 '<p class="course"><b>Course:</b> <i>Robotics</i> Ch. 23–29, dynamics (in writing); factory lab 9</p>')},
            {"t": ("选型", "Selection"), "s": "hold", "who": ("设计院 · 零件库选型校验", "Design · parts-library selection"),
             "body": (
                 "<p>按连续 70.0 N·m、峰值 92.5 N·m、20 rpm，在零件库里找电机 + 谐波减速器 + 驱动器的组合，逐条校验 C1–C11。</p>"
                 '<div class="tbl"><table><thead><tr><th>部件</th><th>型号</th><th class="r">质量 kg</th></tr></thead><tbody><tr><td>伺服电机</td><td>Yaskawa SGM7J-04A（轴端代码 6）</td><td class="r">1.1</td></tr><tr><td>谐波减速器</td><td>Harmonic Drive CSF-32-100-2UH</td><td class="r">3.2</td></tr><tr><td>驱动器</td><td>Yaskawa SGD7S-2R8A（EtherCAT）</td><td class="r">1.1</td></tr></tbody></table></div>',
                 "<p>With 70.0 N·m continuous, 92.5 N·m peak and 20 rpm, the engine searches the library for a motor + harmonic reducer + drive and checks rules C1–C11 one by one.</p>"
                 '<div class="tbl"><table><thead><tr><th>Part</th><th>Model</th><th class="r">Mass kg</th></tr></thead><tbody><tr><td>Servo motor</td><td>Yaskawa SGM7J-04A (shaft code 6)</td><td class="r">1.1</td></tr><tr><td>Harmonic reducer</td><td>Harmonic Drive CSF-32-100-2UH</td><td class="r">3.2</td></tr><tr><td>Drive</td><td>Yaskawa SGD7S-2R8A (EtherCAT)</td><td class="r">1.1</td></tr></tbody></table></div>'),
             "side": (
                 '<p class="note">待确认：C3 法兰配合缺分度圆直径；C8 惯量比缺减速器输入侧惯量。数据补齐前不判定为“可用”。</p>'
                 '<dl class="kv"><dt>通过</dt><dd>C1、C2、C4–C7、C9、C10</dd><dt>肘 j3</dt><dd>4 个候选，最轻 3.2 kg</dd><dt>腕 j4</dt><dd>14 个候选，最轻 1.88 kg（A5A-6 + CSF-17）</dd><dt>数据来源</dt><dd>厂商手册，AI 两次独立抽取一致</dd></dl>'
                 '<p class="course"><b>对应：</b>特色选修“伺服驱动与运动控制”</p>',
                 '<p class="note">To be confirmed: C3 flange fit lacks the bolt-circle diameter; C8 inertia ratio lacks the reducer’s input-side inertia. The pick is not called “usable” until the data are in.</p>'
                 '<dl class="kv"><dt>Passed</dt><dd>C1, C2, C4–C7, C9, C10</dd><dt>Elbow j3</dt><dd>4 candidates, lightest 3.2 kg</dd><dt>Wrist j4</dt><dd>14 candidates, lightest 1.88 kg (A5A-6 + CSF-17)</dd><dt>Data source</dt><dd>Vendor manuals; two independent AI extractions agree</dd></dl>'
                 '<p class="course"><b>Course:</b> elective “Servo Drives and Motion Control”</p>')},
            {"t": ("布局与 BOM", "Layout & BOM"), "s": "ok", "who": ("设计院 · FreeCAD 无界面布局", "Design · headless FreeCAD layout"),
             "body": (
                 "<p>FreeCAD 按端口把电机、减速器、驱动器摆好，检查干涉。第 1 轮驱动器与电机、减速器有干涉，挪开后第 2 轮通过。</p>"
                 '<dl class="kv"><dt>第 1 轮</dt><dd>干涉：驱动器–减速器 338,818 mm³</dd><dt>第 2 轮</dt><dd>无干涉（驱动器移到 x = 111.5 mm）</dd><dt>外购件</dt><dd>3 种，共 5.4 kg</dd></dl>',
                 "<p>FreeCAD places motor, reducer and drive by their ports and checks for clashes. Round 1 found the drive overlapping the motor and reducer; after moving it, round 2 passed.</p>"
                 '<dl class="kv"><dt>Round 1</dt><dd>Clash: drive–reducer 338,818 mm³</dd><dt>Round 2</dt><dd>No clash (drive moved to x = 111.5 mm)</dd><dt>Bought parts</dt><dd>3 items, 5.4 kg in total</dd></dl>'),
             "side": ("@layout", "@layout")},
            {"t": ("强度 · 疲劳 · 热", "Strength · fatigue · heat"), "s": "ok", "who": ("设计院 · 有限元与热分析", "Design · FEA and thermal"),
             "body": (
                 "<p>空心轴 RJ-201 加峰值扭矩做有限元；用动力学的扭矩记录算疲劳寿命；用平均功率和效率曲线估关节壳体温度。</p>"
                 '<dl class="kv"><dt>最大 Von Mises</dt><dd>27.7 MPa</dd><dt>安全系数</dt><dd>12.8</dd><dt>手算校核</dt><dd>花键段 τ = T·r/Iₚ = 8.0 MPa，等效 13.8 MPa；有限元最大值在台阶附近，含应力集中</dd><dt>疲劳</dt><dd>应力远低于疲劳极限，远超设计寿命</dd></dl>',
                 "<p>FEA on the hollow shaft RJ-201 at peak torque; fatigue life from the torque record of the dynamics run; housing temperature from mean power and the efficiency curve.</p>"
                 '<dl class="kv"><dt>Max von Mises</dt><dd>27.7 MPa</dd><dt>Safety factor</dt><dd>12.8</dd><dt>Hand check</dt><dd>Spline section τ = T·r/Iₚ = 8.0 MPa, equivalent 13.8 MPa; the FE maximum sits at a shoulder, with stress concentration</dd><dt>Fatigue</dt><dd>Far below the fatigue limit; life far beyond the design target</dd></dl>'),
             "side": (
                 '<p class="note">壳体最高 89.7 °C：按连续往复运动估算，偏保守。实际要有停顿，或加散热。</p>'
                 '<dl class="kv"><dt>减速器损耗</dt><dd>约 36.4 W（效率 0.69）</dd><dt>电机损耗</dt><dd>零件库无数据，未计</dd></dl>'
                 '<p class="course"><b>对应：</b>《机械设计》第 33.10 节；数字工厂实验 8、11</p>',
                 '<p class="note">Housing peaks at 89.7 °C, assuming non-stop back-and-forth motion, so this is conservative. Real duty needs pauses or extra cooling.</p>'
                 '<dl class="kv"><dt>Reducer loss</dt><dd>About 36.4 W (efficiency 0.69)</dd><dt>Motor loss</dt><dd>Not in the library, not counted</dd></dl>'
                 '<p class="course"><b>Course:</b> <i>Machine Design</i> §33.10; factory labs 8 and 11</p>')},
            {"t": ("拓扑优化", "Topology optimization"), "s": "ok", "who": ("设计院 · 拓扑优化", "Design · topology optimization"),
             "body": (
                 "<p>大臂侧板按悬臂构形、保留 45% 材料做拓扑优化，再拉伸成 6 mm 板做有限元复核。上方三维模型里可以看到优化后的板。</p>"
                 '<div class="bar"><div><span>优化前柔度</span><i class="ghost" style="width:100%"></i><span>933</span></div><div><span>优化后柔度</span><i style="width:16.5%"></i><span>154</span></div></div>',
                 "<p>The upper-arm plate is optimized as a cantilever keeping 45% of the material, then extruded to a 6 mm plate and re-checked by FEA. The optimized plate is in the 3D viewer above.</p>"
                 '<div class="bar"><div><span>Before</span><i class="ghost" style="width:100%"></i><span>933</span></div><div><span>After</span><i style="width:16.5%"></i><span>154</span></div></div>'),
             "side": (
                 '<dl class="kv"><dt>板面积</dt><dd>29,369 mm²</dd><dt>末端载荷</dt><dd>49 N</dd><dt>最大应力</dt><dd>1.5 MPa</dd><dt>最大位移</dt><dd>0.018 mm</dd></dl>',
                 '<dl class="kv"><dt>Plate area</dt><dd>29,369 mm²</dd><dt>Tip load</dt><dd>49 N</dd><dt>Max stress</dt><dd>1.5 MPa</dd><dt>Max deflection</dt><dd>0.018 mm</dd></dl>')},
            {"t": ("数控编程", "CNC programming"), "s": "ok", "who": ("设计院 · CAM", "Design · CAM"),
             "body": (
                 "<p>RJ-201 两次装夹车外圆，J2-HSG 铣外轮廓、钻 4 个螺纹底孔。程序都过了自动检查。Ø30 内孔另行钻镗，不在本模块。</p>"
                 '<dl class="kv"><dt>RJ-201 车削</dt><dd>2 个程序，约 4.1 min</dd><dt>J2-HSG 铣削</dt><dd>1 个程序，约 5.7 min</dd><dt>机床</dt><dd>示例数控车床、立式加工中心（虚构）</dd></dl>',
                 "<p>RJ-201 is turned in two setups; J2-HSG gets its contour milled and 4 tap holes drilled. All programs passed the automatic check. The Ø30 bore is drilled and bored separately.</p>"
                 '<dl class="kv"><dt>RJ-201 turning</dt><dd>2 programs, about 4.1 min</dd><dt>J2-HSG milling</dt><dd>1 program, about 5.7 min</dd><dt>Machines</dt><dd>Example lathe and machining center (fictional)</dd></dl>'),
             "side": ("@gcode", "@gcode")},
        ],
        "gcode": "%\nO1001 (RJ-201 车削 右端[第一次装夹])\n(毛坯 Ø74×98)\n(T01 外圆粗车刀)\nG21 G18 G40 G97 G99\nG00 X200.0 Z150.0\nT0101\nG50 S3000\nG96 S120 M03\n(车端面[余量 1])\nG00 X78.0 Z2.0 M08\nZ0.0\nG01 X-1.0 F0.3\n(分层粗车[每层 ap=2.5])\nX69.0\nG01 Z-85.9\nX70.0 Z-85.4\nG00 Z2.0\nX64.0\nG01 Z-85.9\n…",
        "factory": [
            {"t": ("转为 ERP 物料", "Into ERP"), "s": "ok", "who": ("工厂 · 厂长确认 → ERPNext", "Factory · plant manager approves → ERPNext"),
             "body": (
                 "<p>工厂收到方案后不自动建账：先出一份“转为生产物料”的提议，厂长确认后，桥接程序在 ERPNext 里建供应商、物料和带工序的 BOM。</p>"
                 '<dl class="kv"><dt>供应商</dt><dd>3 家</dd><dt>物料</dt><dd>7 种</dd><dt>BOM</dt><dd>3 张（含工序）</dd><dt>重复执行</dt><dd>同一版本只保留 1 张 BOM，新版本自动成为默认</dd></dl>',
                 "<p>The factory does not create records on its own. It drafts a “convert to production items” proposal; once the plant manager approves, the bridge creates suppliers, items and routed BOMs in ERPNext.</p>"
                 '<dl class="kv"><dt>Suppliers</dt><dd>3</dd><dt>Items</dt><dd>7</dd><dt>BOMs</dt><dd>3 (with operations)</dd><dt>Re-run</dt><dd>One BOM per revision; a new revision becomes the default</dd></dl>'),
             "side": (
                 '<p class="note">三家供应商都没填采购提前期，系统提示“交期待确认”。</p><p class="course"><b>对应：</b>特色选修“ERP 原理与实践”</p>',
                 '<p class="note">None of the three suppliers has a lead time on file, so the system flags “lead time to be confirmed”.</p><p class="course"><b>Course:</b> elective “ERP Principles and Practice”</p>')},
            {"t": ("工艺规程", "Process plans"), "s": "ok", "who": ("工厂 · 工艺员 → AI 评审 → 技术负责人", "Factory · process engineer → AI review → chief engineer"),
             "body": (
                 "<p>工艺员按方案起草工艺规程，粗基准和装夹来自设计方案。AI 工艺评审提出意见，技术负责人批准为第 1 版。</p>"
                 '<dl class="kv"><dt>RJ-201</dt><dd>6 道工序，粗基准：毛坯 Ø50 外圆</dd><dt>J2-HSG</dt><dd>3 道工序，粗基准：毛坯底面</dd></dl>',
                 "<p>The process engineer drafts the plans; the rough datum and fixturing come from the design. An AI review comments, and the chief engineer approves rev 1.</p>"
                 '<dl class="kv"><dt>RJ-201</dt><dd>6 operations; rough datum: Ø50 stock diameter</dd><dt>J2-HSG</dt><dd>3 operations; rough datum: stock bottom face</dd></dl>'),
             "side": (
                 '<p class="note">AI 评审意见：没有附工艺计算书（工序尺寸、余量、切削用量和工时的计算过程）。</p><p class="course"><b>对应：</b>《机械制造技术》工艺规程设计</p>',
                 '<p class="note">AI review: no process calculation sheet attached (operation sizes, allowances, cutting data and time estimates).</p><p class="course"><b>Course:</b> <i>Manufacturing Technology</i>, process planning</p>')},
            {"t": ("接单与 MRP", "Order & MRP"), "s": "ok", "who": ("工厂 · 计划员", "Factory · planner"),
             "body": (
                 "<p>示例客户订 2 台。MRP 按 BOM 展开，生成工单和请购单。</p>"
                 '<div class="tbl"><table><thead><tr><th>工单</th><th class="r">数量</th><th class="r">工时</th></tr></thead><tbody><tr><td>RJ-201 空心轴</td><td class="r">2</td><td class="r">约 77 min</td></tr><tr><td>J2-HSG 壳体</td><td class="r">2</td><td class="r">约 65 min</td></tr><tr><td>COBOT-J2 总装</td><td class="r">2</td><td class="r">约 115 min</td></tr></tbody></table></div>',
                 "<p>A demo customer orders 2 units. MRP explodes the BOM into work orders and purchase requests.</p>"
                 '<div class="tbl"><table><thead><tr><th>Work order</th><th class="r">Qty</th><th class="r">Time</th></tr></thead><tbody><tr><td>RJ-201 hollow shaft</td><td class="r">2</td><td class="r">≈ 77 min</td></tr><tr><td>J2-HSG housing</td><td class="r">2</td><td class="r">≈ 65 min</td></tr><tr><td>COBOT-J2 assembly</td><td class="r">2</td><td class="r">≈ 115 min</td></tr></tbody></table></div>'),
             "side": (
                 '<dl class="kv"><dt>请购</dt><dd>CSF-32 ×2、SGD7S-2R8A ×2、SGM7J-04A-6 ×2、原材料 RM-45-D50 ×50、RM-6061-B140 ×10</dd><dt>需求日</dt><dd>交期待确认，暂按当天</dd></dl><p class="course"><b>对应：</b>特色选修“生产计划与排程”</p>',
                 '<dl class="kv"><dt>Requests</dt><dd>CSF-32 ×2, SGD7S-2R8A ×2, SGM7J-04A-6 ×2, stock RM-45-D50 ×50, RM-6061-B140 ×10</dd><dt>Need date</dt><dd>Lead time unknown, set to today</dd></dl><p class="course"><b>Course:</b> elective “Production Planning and Scheduling”</p>')},
            {"t": ("采购到货", "Receiving"), "s": "ok", "who": ("工厂 · 仓库", "Factory · warehouse"),
             "body": ("<p>5 种物料到货，ERPNext 生成收货单，入原材料库。</p>", "<p>Five items arrive; ERPNext posts a purchase receipt into raw-material stock.</p>"),
             "side": ('<p class="course"><b>对应：</b>特色选修“仓储管理与智能仓库”“物流与供应链管理”</p>',
                      '<p class="course"><b>Course:</b> electives “Warehousing” and “Logistics and Supply Chain”</p>')},
            {"t": ("MES 车间执行", "MES execution"), "s": "ok", "who": ("工厂 · 车间终端", "Factory · shop-floor terminal"),
             "body": (
                 "<p>两张自制件工单派到 7 台设备，仿真车间加工完工；再下总装工单。车间仿真按 120 倍速运行。</p>"
                 '<dl class="kv"><dt>自制件</dt><dd>MFG-WO-2026-00001、00002，仿真 97 s 完工</dd><dt>总装</dt><dd>MFG-WO-2026-00003，74 s 完工</dd></dl>',
                 "<p>Two work orders for made parts are dispatched to 7 machines and completed in the simulated shop, then the assembly order runs. The shop simulation runs at 120×.</p>"
                 '<dl class="kv"><dt>Made parts</dt><dd>MFG-WO-2026-00001, 00002, done in 97 s simulated</dd><dt>Assembly</dt><dd>MFG-WO-2026-00003, done in 74 s</dd></dl>'),
             "side": ('<p class="course"><b>对应：</b>特色选修“制造执行系统 MES”；数字工厂实验 7</p>',
                      '<p class="course"><b>Course:</b> elective “Manufacturing Execution Systems”; factory lab 7</p>')},
            {**HUB, "side": (
                '<dl class="kv"><dt>工厂复算</dt><dd>RJ-201 有限元 20.2 MPa（设计院 27.7 MPa；网格与固定面不同，量级一致）</dd><dt>ERP 一致性</dt><dd>0 条错误</dd></dl><p class="course"><b>对应：</b>“智能制造与数字孪生”；数字工厂实验 15</p>',
                '<dl class="kv"><dt>Factory re-check</dt><dd>RJ-201 FEA 20.2 MPa (design 27.7 MPa; different mesh and fixed face, same order)</dd><dt>ERP consistency</dt><dd>0 errors</dd></dl><p class="course"><b>Course:</b> “Smart Manufacturing and Digital Twins”; factory lab 15</p>')},
        ],
        "open": [
            (("电机与减速器的法兰能不能对上", "Will the motor and reducer flanges mate?"),
             ("零件库缺分度圆直径、孔数和孔的形式，配合检查 C3 判为“待确认”。其余 C1、C2、C4–C7、C9、C10 通过。",
              "The library lacks bolt-circle diameter, hole count and hole type, so fit check C3 is “to be confirmed”. C1, C2, C4–C7, C9 and C10 pass.")),
            (("惯量比", "Inertia ratio"),
             ("谐波减速器缺输入侧惯量，C8 无法判定。补齐样本数据后可以重算。",
              "The harmonic reducer has no input-side inertia on file, so C8 cannot be judged until the catalogue value is added.")),
            (("减速器还能用多久", "How long will the reducer last?"),
             ("CSF-32 缺额定寿命和额定输入转速，数字孪生算不出剩余寿命。补录规格书后即可计算。",
              "CSF-32 lacks rated life and rated input speed, so the digital twin cannot compute remaining life until the datasheet is added.")),
            (("采购交期", "Purchase lead times"),
             ("三家供应商都没有登记提前期，工厂按“交期待确认”排程，请购单需求日暂按当天。",
              "No supplier has a lead time on file; the factory schedules with “lead time to be confirmed” and dates requests today.")),
            (("壳体温度偏高", "Housing runs hot"),
             ("按连续往复运动估算，壳体最高 89.7 °C。实际工况有停顿，或者要加散热，这是偏保守的结果。",
              "With non-stop motion the housing peaks at 89.7 °C. Real duty has pauses, or needs cooling; the figure is conservative.")),
            (("演练用的假设", "Assumptions in this run"),
             ("满载 5 kg 水平伸直为最不利工况；机械臂各节质量来自外部测量；数控程序用的是示例机床（虚构）；控制柜按 200 V 交流，真实协作臂多用 48 V 直流关节。",
              "Worst case is the arm level with 5 kg; link masses come from external measurements; CNC programs target fictional example machines; the cabinet is 200 V AC, while real cobots mostly use 48 V DC joints.")),
        ],
        "courses": [
            (("机器人学", "Robotics"), ("UR5e 运动学与虚拟实验（已上线）；第 23–29 章动力学、第 32 章传动与减速器、第 36 章电机与驱动（编写中）",
                                        "UR5e kinematics and virtual labs (online); Ch. 23–29 dynamics, Ch. 32 transmissions, Ch. 36 motors and drives (in writing)"), ("部分上线", "Partly online")),
            (("机械设计", "Machine Design"), ("第 33.10 节：协作机器人肩关节空心轴 RJ-201", "§33.10: the cobot shoulder hollow shaft RJ-201"), ("教材已上线", "Online")),
            (("机械制造技术", "Manufacturing Technology"), ("工艺规程、粗基准与装夹、数控车削与铣削", "Process plans, datums and fixturing, CNC turning and milling"), ("教材编写中", "In writing")),
            (("伺服驱动与运动控制", "Servo Drives and Motion Control"), ("电机、减速器、驱动器的选型与校核", "Selecting and checking motor, reducer and drive"), ("特色选修 · 建设中", "Elective · planned")),
            (("ERP 原理与实践 · 制造执行系统 MES", "ERP and MES"), ("物料与 BOM、MRP、请购、工单与报工", "Items and BOMs, MRP, purchasing, work orders"), ("特色选修 · 建设中", "Elective · planned")),
            (("智能制造与数字孪生", "Smart Manufacturing and Digital Twins"), ("厂情中枢：异常、追因、推演与决策", "Command center: anomalies, root cause, what-if, decisions"), ("特色选修 · 建设中", "Elective · planned")),
        ],
        "labs": [("实验 9", "机械臂关节力矩与电机选型", "Lab 9", "Arm joint torque and motor sizing"),
                 ("实验 8", "输出轴强度与疲劳校核", "Lab 8", "Output shaft strength and fatigue"),
                 ("实验 12", "一根轴的数字化设计与两个典型案例", "Lab 12", "Digital design of a shaft"),
                 ("实验 7", "数字工厂闭环（订单 → 车间 → 入库）", "Lab 7", "The factory loop: order → shop → stock")],
        "files": "RJ-201.step、J2-HSG.step、upper-arm-plate.step、O1001.nc、O1002.nc、O5001.nc、bom.csv、candidate-1.urdf",
        "src": "cobot_joint",
        "basis": ('<a href="https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/" target="_blank" rel="noopener">UR5e 数据表</a>、<a href="https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/" target="_blank" rel="noopener">UR 官方 DH 参数表</a>',
                  '<a href="https://www.universal-robots.com/manuals/latest/en/datasheets/ur5e/" target="_blank" rel="noopener">UR5e datasheet</a>, <a href="https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/" target="_blank" rel="noopener">UR DH parameter table</a>'),
    },
    # ------------------------------------------------------------------ SCARA
    {
        "slug": "scara",
        "no": "02",
        "name": ("SCARA 机器人", "SCARA Robot"),
        "title": ("节拍定了 0.4 秒，零件库能不能供得上？", "The cycle time is set at 0.4 s. Can the parts library deliver it?"),
        "lede": (
            "以 600 mm 臂展的 SCARA 为对象（Epson LS6-B 一类）：先按快、慢两种节拍算大臂和小臂的力矩，再到零件库里选型。快节拍<b>找不到能满足的组合</b>，平台如实报告缺什么，改按慢节拍选型，接着做拓扑优化、有限元和数控编程，发布到工厂做出来。",
            "Take a 600 mm SCARA (Epson LS6-B class). Compute arm torques for a fast and a slow cycle, then search the parts library. For the fast cycle <b>no combination in the library works</b>; the platform says exactly what is missing, sizes for the slow cycle instead, then optimizes, checks and machines the arm and releases it to the factory.",
        ),
        "facts": [
            (("快节拍大臂峰值", "Fast-cycle arm peak"), "184", "N·m"),
            (("慢节拍大臂峰值", "Slow-cycle arm peak"), "46.8", "N·m"),
            (("大臂一阶频率", "Arm 1st mode"), "179", "Hz"),
            (("车间完工工单", "Work orders completed"), "3", ""),
        ],
        "parts": [
            ("SC-ARM1", ("SC-ARM1 大臂", "SC-ARM1 inner arm"),
             ("<b>SC-ARM1</b> 大臂 · 325×120×20 mm 铝板 · 拓扑优化保留 50% 材料，柔度 710 → 142",
              "<b>SC-ARM1</b> inner arm · 325 × 120 × 20 mm aluminium · 50% material kept, compliance 710 → 142")),
        ],
        "release": ("SCARA-600 第 1 版，带自制件 SC-ARM1、SC-ARM2", "SCARA-600 rev 1, with made parts SC-ARM1 and SC-ARM2"),
        "design": [
            {"t": ("动力学", "Dynamics"), "s": "ok", "who": ("设计院 · 多体动力学（水平面）", "Design · multibody dynamics (horizontal)"),
             "body": (
                 "<p>大臂 325 mm、小臂 275 mm，末端额定负载 2 kg，两臂各转 90°。快节拍用时 0.3 s，慢节拍 0.6 s。水平面运动，不计重力。</p>"
                 '<div class="bar"><div><span>快 · 大臂</span><i style="width:100%"></i><span>183.7</span></div><div><span>快 · 小臂</span><i style="width:36.9%"></i><span>67.7</span></div><div><span>慢 · 大臂</span><i style="width:25.5%"></i><span>46.8</span></div><div><span>慢 · 小臂</span><i style="width:9.3%"></i><span>17.1</span></div></div><p class="unit">峰值力矩，N·m</p>',
                 "<p>Inner arm 325 mm, outer arm 275 mm, 2 kg rated payload; both arms turn 90°. Fast cycle 0.3 s, slow cycle 0.6 s. Horizontal motion, so gravity does not enter.</p>"
                 '<div class="bar"><div><span>Fast · inner</span><i style="width:100%"></i><span>183.7</span></div><div><span>Fast · outer</span><i style="width:36.9%"></i><span>67.7</span></div><div><span>Slow · inner</span><i style="width:25.5%"></i><span>46.8</span></div><div><span>Slow · outer</span><i style="width:9.3%"></i><span>17.1</span></div></div><p class="unit">Peak torque, N·m</p>'),
             "side": (
                 '<dl class="kv"><dt>快 · 最高转速</dt><dd>83 rpm</dd><dt>慢 · 最高转速</dt><dd>42 rpm</dd><dt>最大等效惯量</dt><dd>1.602 kg·m²</dd><dt>时间减半</dt><dd>力矩约 4 倍：加速度与时间平方成反比</dd></dl>'
                 '<p class="course"><b>对应：</b>《机器人学》动力学（编写中）；数字工厂实验 9</p>',
                 '<dl class="kv"><dt>Fast · max speed</dt><dd>83 rpm</dd><dt>Slow · max speed</dt><dd>42 rpm</dd><dt>Max equivalent inertia</dt><dd>1.602 kg·m²</dd><dt>Half the time</dt><dd>About 4× the torque: acceleration goes as 1/t²</dd></dl>'
                 '<p class="course"><b>Course:</b> <i>Robotics</i> dynamics (in writing); factory lab 9</p>')},
            {"t": ("选型", "Selection"), "s": "hold", "who": ("设计院 · 零件库选型校验", "Design · parts-library selection"),
             "body": (
                 "<p><b>快节拍：零件库供不了。</b>100:1 时电机转速超限；50:1 的谐波减速器库里最大只到 CSF-20，扭矩不够。要做到 0.40 s 节拍，需要补 32 号以上的 50:1 谐波减速器，或换减速方式。</p>"
                 "<p>改按慢节拍选型，大臂、小臂都选出同一组：</p>"
                 '<div class="tbl"><table><thead><tr><th>部件</th><th>型号</th></tr></thead><tbody><tr><td>伺服电机</td><td>Yaskawa SGM7J-02A（轴端代码 6）</td></tr><tr><td>谐波减速器</td><td>Harmonic Drive CSF-25-100-2UH</td></tr><tr><td>驱动器</td><td>Yaskawa SGD7S-1R6A</td></tr></tbody></table></div>',
                 "<p><b>Fast cycle: the library cannot supply it.</b> At 100:1 the motor overspeeds; the largest 50:1 harmonic reducer in the library is CSF-20, which lacks torque. A 0.40 s cycle needs a size-32+ 50:1 harmonic reducer or a different reduction.</p>"
                 "<p>Sized for the slow cycle instead, both arms get the same set:</p>"
                 '<div class="tbl"><table><thead><tr><th>Part</th><th>Model</th></tr></thead><tbody><tr><td>Servo motor</td><td>Yaskawa SGM7J-02A (shaft code 6)</td></tr><tr><td>Harmonic reducer</td><td>Harmonic Drive CSF-25-100-2UH</td></tr><tr><td>Drive</td><td>Yaskawa SGD7S-1R6A</td></tr></tbody></table></div>'),
             "side": (
                 '<p class="note">慢节拍的组合也是“待确认”：缺分度圆直径（C3）、减速比或效率（C4、C5）、过载保护数据（C6）、减速器输入侧惯量（C8）。</p>'
                 '<dl class="kv"><dt>大臂需求</dt><dd>连续 27.0 / 峰值 46.8 N·m，42 rpm</dd><dt>小臂需求</dt><dd>连续 9.6 / 峰值 17.1 N·m，42 rpm</dd></dl>'
                 '<p class="course"><b>对应：</b>特色选修“伺服驱动与运动控制”</p>',
                 '<p class="note">The slow-cycle set is also “to be confirmed”: missing bolt-circle diameter (C3), ratio or efficiency (C4, C5), overload data (C6) and reducer input inertia (C8).</p>'
                 '<dl class="kv"><dt>Inner arm needs</dt><dd>27.0 continuous / 46.8 N·m peak, 42 rpm</dd><dt>Outer arm needs</dt><dd>9.6 continuous / 17.1 N·m peak, 42 rpm</dd></dl>'
                 '<p class="course"><b>Course:</b> elective “Servo Drives and Motion Control”</p>')},
            {"t": ("布局与 BOM", "Layout & BOM"), "s": "ok", "who": ("设计院 · FreeCAD 无界面布局", "Design · headless FreeCAD layout"),
             "body": (
                 "<p>按端口把每个关节的电机、减速器、驱动器摆好并检查干涉，生成两个关节的外购件清单。</p>"
                 '<dl class="kv"><dt>外购件</dt><dd>每个关节 3 种：SGM7J-02A、CSF-25-100-2UH、SGD7S-1R6A</dd><dt>复核</dt><dd>同上一步的待确认项</dd></dl>',
                 "<p>Each joint’s motor, reducer and drive are placed by their ports and checked for clashes; the bought-parts list covers both joints.</p>"
                 '<dl class="kv"><dt>Bought parts</dt><dd>3 per joint: SGM7J-02A, CSF-25-100-2UH, SGD7S-1R6A</dd><dt>Re-check</dt><dd>Same open items as the previous step</dd></dl>'),
             "side": ("@layout", "@layout")},
            {"t": ("拓扑优化 · 有限元", "Topology · FEA"), "s": "ok", "who": ("设计院 · 拓扑优化与模态", "Design · topology and modal"),
             "body": (
                 "<p>大臂按悬臂构形、保留 50% 材料做拓扑优化，做成 20 mm 铝板，再做强度和模态校核。</p>"
                 '<div class="bar"><div><span>优化前柔度</span><i class="ghost" style="width:100%"></i><span>710</span></div><div><span>优化后柔度</span><i style="width:20%"></i><span>142</span></div></div>',
                 "<p>The inner arm is optimized as a cantilever keeping 50% of the material, made as a 20 mm aluminium plate, then checked for stress and vibration modes.</p>"
                 '<div class="bar"><div><span>Before</span><i class="ghost" style="width:100%"></i><span>710</span></div><div><span>After</span><i style="width:20%"></i><span>142</span></div></div>'),
             "side": (
                 '<dl class="kv"><dt>末端载荷</dt><dd>144 N</dd><dt>最大应力</dt><dd>1.6 MPa</dd><dt>末端位移</dt><dd>0.014 mm</dd><dt>一阶固有频率</dt><dd>179 Hz（根部固定，不含小臂与负载的附加质量）</dd></dl>',
                 '<dl class="kv"><dt>Tip load</dt><dd>144 N</dd><dt>Max stress</dt><dd>1.6 MPa</dd><dt>Tip deflection</dt><dd>0.014 mm</dd><dt>1st mode</dt><dd>179 Hz (root fixed, without outer arm and payload mass)</dd></dl>')},
            {"t": ("热 · 流体 · 孪生", "Heat · CFD · twin"), "s": "na", "who": ("设计院", "Design"),
             "body": ("<p>做法与协作机器人关节相同，这里不重复。数字孪生同样缺谐波减速器的额定寿命。</p>",
                      "<p>Same method as the cobot joint, not repeated here. The digital twin again lacks the harmonic reducer’s rated life.</p>"),
             "side": ("", "")},
            {"t": ("数控编程", "CNC programming"), "s": "ok", "who": ("设计院 · CAM", "Design · CAM"),
             "body": (
                 "<p>大臂铣外轮廓、减重型腔和 4 个安装孔，程序过了自动检查。</p>"
                 '<dl class="kv"><dt>SC-ARM1 铣削</dt><dd>1 个程序，约 21.3 min</dd><dt>刀具</dt><dd>Ø10、Ø20 立铣刀，Ø8.5 麻花钻</dd><dt>机床</dt><dd>示例立式加工中心（虚构）</dd></dl>',
                 "<p>The inner arm gets its outline, lightening pockets and 4 mounting holes milled; the program passed the automatic check.</p>"
                 '<dl class="kv"><dt>SC-ARM1 milling</dt><dd>1 program, about 21.3 min</dd><dt>Tools</dt><dd>Ø10 and Ø20 end mills, Ø8.5 drill</dd><dt>Machine</dt><dd>Example machining center (fictional)</dd></dl>'),
             "side": ("@gcode", "@gcode")},
        ],
        "gcode": "%\nO5001 (SC-ARM1 铣削)\n(机床 示例立式加工中心[虚构])\n(T01 立铣刀 Ø10 D10.0)\n(T02 立铣刀 Ø20 D20.0)\n(T03 麻花钻 Ø8.5 D8.5)\nG21 G17 G40 G49 G80 G90 G94\n(铣外轮廓)\nT1 M06\nG54\nS3183 M03\nG00 X170.0 Y-75.0\nG43 Z50.0 H01 M08\n(铣外轮廓：深 20，刀具 Ø10，顺铣，分 4 层)\nG00 Z5.0\nZ0.5\nG01 Z-5.0 F254.7\nY-65.0 F509.3\nX0.0\n…",
        "factory": [
            {"t": ("转为 ERP 物料", "Into ERP"), "s": "ok", "who": ("工厂 · 厂长确认 → ERPNext", "Factory · plant manager approves → ERPNext"),
             "body": ("<p>厂长确认“转为生产物料”的提议后，桥接程序在 ERPNext 里建供应商、物料和带工序的 BOM。</p>"
                      '<dl class="kv"><dt>供应商</dt><dd>3 家</dd><dt>物料</dt><dd>8 种</dd><dt>BOM</dt><dd>3 张（含工序）</dd></dl>',
                      "<p>After the plant manager approves the proposal, the bridge creates suppliers, items and routed BOMs in ERPNext.</p>"
                      '<dl class="kv"><dt>Suppliers</dt><dd>3</dd><dt>Items</dt><dd>8</dd><dt>BOMs</dt><dd>3 (with operations)</dd></dl>'),
             "side": ('<p class="note">三家供应商都没填采购提前期，交期待确认。</p><p class="course"><b>对应：</b>特色选修“ERP 原理与实践”</p>',
                      '<p class="note">No supplier has a lead time on file; lead time to be confirmed.</p><p class="course"><b>Course:</b> elective “ERP Principles and Practice”</p>')},
            {"t": ("工艺规程", "Process plans"), "s": "ok", "who": ("工厂 · 工艺员 → AI 评审 → 技术负责人", "Factory · process engineer → AI review → chief engineer"),
             "body": ("<p>两只臂各 3 道工序，粗基准都是毛坯底面，来自设计方案。技术负责人批准为第 1 版。</p>",
                      "<p>Each arm has 3 operations with the stock bottom face as rough datum, taken from the design. The chief engineer approves rev 1.</p>"),
             "side": ('<p class="note">AI 评审意见：没有附工艺计算书。</p><p class="course"><b>对应：</b>《机械制造技术》工艺规程设计</p>',
                      '<p class="note">AI review: no process calculation sheet attached.</p><p class="course"><b>Course:</b> <i>Manufacturing Technology</i>, process planning</p>')},
            {"t": ("接单与 MRP", "Order & MRP"), "s": "ok", "who": ("工厂 · 计划员", "Factory · planner"),
             "body": ("<p>示例客户订 2 台，MRP 生成工单和请购单。</p>"
                      '<div class="tbl"><table><thead><tr><th>工单</th><th class="r">数量</th><th class="r">工时</th></tr></thead><tbody><tr><td>SC-ARM1 大臂</td><td class="r">2</td><td class="r">约 84 min</td></tr><tr><td>SC-ARM2 小臂</td><td class="r">2</td><td class="r">约 74 min</td></tr><tr><td>SCARA-600 总装</td><td class="r">2</td><td class="r">约 165 min</td></tr></tbody></table></div>',
                      "<p>A demo customer orders 2 units; MRP creates work orders and purchase requests.</p>"
                      '<div class="tbl"><table><thead><tr><th>Work order</th><th class="r">Qty</th><th class="r">Time</th></tr></thead><tbody><tr><td>SC-ARM1 inner arm</td><td class="r">2</td><td class="r">≈ 84 min</td></tr><tr><td>SC-ARM2 outer arm</td><td class="r">2</td><td class="r">≈ 74 min</td></tr><tr><td>SCARA-600 assembly</td><td class="r">2</td><td class="r">≈ 165 min</td></tr></tbody></table></div>'),
             "side": ('<dl class="kv"><dt>请购</dt><dd>CSF-25 ×2、SGD7S-1R6A ×2、SGM7J-02A-6 ×2、原材料 RM-6061-P330 ×10、RM-6061-P380 ×10</dd></dl><p class="course"><b>对应：</b>特色选修“生产计划与排程”</p>',
                      '<dl class="kv"><dt>Requests</dt><dd>CSF-25 ×2, SGD7S-1R6A ×2, SGM7J-02A-6 ×2, stock RM-6061-P330 ×10, RM-6061-P380 ×10</dd></dl><p class="course"><b>Course:</b> elective “Production Planning and Scheduling”</p>')},
            {"t": ("采购到货", "Receiving"), "s": "ok", "who": ("工厂 · 仓库", "Factory · warehouse"),
             "body": ("<p>5 种物料到货，ERPNext 生成收货单，入原材料库。</p>", "<p>Five items arrive; ERPNext posts a purchase receipt into raw-material stock.</p>"),
             "side": ('<p class="course"><b>对应：</b>特色选修“仓储管理与智能仓库”</p>', '<p class="course"><b>Course:</b> elective “Warehousing”</p>')},
            {"t": ("MES 车间执行", "MES execution"), "s": "ok", "who": ("工厂 · 车间终端", "Factory · shop-floor terminal"),
             "body": ("<p>两张自制件工单派到 2 台设备完工，再下总装工单。</p>"
                      '<dl class="kv"><dt>自制件</dt><dd>MFG-WO-2026-00004、00005，仿真 112 s 完工</dd><dt>总装</dt><dd>MFG-WO-2026-00006，99 s 完工</dd></dl>',
                      "<p>Two made-part work orders run on 2 machines, then the assembly order.</p>"
                      '<dl class="kv"><dt>Made parts</dt><dd>MFG-WO-2026-00004, 00005, done in 112 s simulated</dd><dt>Assembly</dt><dd>MFG-WO-2026-00006, done in 99 s</dd></dl>'),
             "side": ('<p class="course"><b>对应：</b>特色选修“制造执行系统 MES”</p>', '<p class="course"><b>Course:</b> elective “Manufacturing Execution Systems”</p>')},
            {**HUB, "side": ('<dl class="kv"><dt>搜索</dt><dd>厂情中枢里能搜到 SCARA-600 的 8 个相关对象</dd></dl><p class="course"><b>对应：</b>“智能制造与数字孪生”；数字工厂实验 15</p>',
                             '<dl class="kv"><dt>Search</dt><dd>The command center finds 8 objects linked to SCARA-600</dd></dl><p class="course"><b>Course:</b> “Smart Manufacturing and Digital Twins”; factory lab 15</p>')},
        ],
        "open": [
            (("0.4 秒节拍要什么零件", "What a 0.4 s cycle would need"),
             ("32 号以上、减速比 50:1 的谐波减速器，或者换一种减速方式。零件库里目前没有。",
              "A size-32 or larger 50:1 harmonic reducer, or a different reduction. The library has neither today.")),
            (("选型数据缺口", "Data gaps in selection"),
             ("分度圆直径、减速比与效率、过载数据、减速器输入侧惯量都缺，C3–C6、C8 判为“待确认”。",
              "Bolt circle, ratio and efficiency, overload data and reducer input inertia are missing, so C3–C6 and C8 are “to be confirmed”.")),
            (("一阶频率偏乐观", "The 179 Hz mode is optimistic"),
             ("179 Hz 没算小臂和负载的附加质量，装上之后会更低。",
              "It leaves out the outer arm and payload mass; the assembled arm will be lower.")),
            (("演练用的假设", "Assumptions in this run"),
             ("产品页只给总臂展 600 mm，大臂 325、小臂 275 mm 是分配假设；两臂质量 3.0、3.5 kg 是估计；快节拍 0.3 s 是按标准循环 0.40 s 粗估的。",
              "The datasheet gives only the 600 mm reach; the 325/275 mm split, arm masses of 3.0 and 3.5 kg, and the 0.3 s fast move estimated from the 0.40 s standard cycle are assumptions.")),
        ],
        "courses": [
            (("机器人学", "Robotics"), ("机械臂运动学（已上线）；动力学各章（编写中）", "Manipulator kinematics (online); dynamics chapters (in writing)"), ("部分上线", "Partly online")),
            (("伺服驱动与运动控制", "Servo Drives and Motion Control"), ("节拍、力矩、转速与减速比的取舍", "Trading cycle time, torque, speed and ratio"), ("特色选修 · 建设中", "Elective · planned")),
            (("机械设计", "Machine Design"), ("轻量化结构、有限元与模态", "Lightweight structures, FEA and modes"), ("部分上线", "Partly online")),
            (("机械制造技术", "Manufacturing Technology"), ("板件铣削、型腔与孔加工", "Plate milling, pockets and holes"), ("教材编写中", "In writing")),
            (("ERP 原理与实践 · 制造执行系统 MES", "ERP and MES"), ("物料与 BOM、MRP、工单与报工", "Items and BOMs, MRP, work orders"), ("特色选修 · 建设中", "Elective · planned")),
        ],
        "labs": [("实验 9", "机械臂关节力矩与电机选型", "Lab 9", "Arm joint torque and motor sizing"),
                 ("实验 10", "输出轴数控车削与键槽铣削编程", "Lab 10", "CNC turning and keyway milling"),
                 ("实验 7", "数字工厂闭环（订单 → 车间 → 入库）", "Lab 7", "The factory loop: order → shop → stock")],
        "files": "SC-ARM1.step、O5001.nc、bom.csv、candidate-1.urdf",
        "src": "scara",
        "basis": ('<a href="https://epson.com/For-Work/Robots/SCARA/Epson-LS6-B-SCARA-Robot---600mm/p/RLS6B602ST9B5" target="_blank" rel="noopener">Epson LS6-B 产品页</a>',
                  '<a href="https://epson.com/For-Work/Robots/SCARA/Epson-LS6-B-SCARA-Robot---600mm/p/RLS6B602ST9B5" target="_blank" rel="noopener">Epson LS6-B product page</a>'),
    },
    # ------------------------------------------------------------------ 直驱平缝机
    {
        "slug": "lockstitch",
        "no": "03",
        "name": ("直驱平缝机", "Direct-Drive Lockstitch"),
        "title": ("每分钟 5000 针，主轴电机该选多大？", "At 5,000 stitches a minute, how big a motor does the main shaft need?"),
        "lede": (
            "以工业直驱平缝机为对象（JUKI DDL-9000C 一类）：电机直接装在主轴上。先算针杆机构在 5000 rpm 下的惯性力矩，分清“峰值”和“一转做功”，选出电机；再校核上轴的强度、疲劳和固有频率，用 OpenFOAM 算控制箱散热器，编好数控程序，<b>选出的 400 W 与实机一致</b>。",
            "Take an industrial direct-drive lockstitch machine (JUKI DDL-9000C class), with the motor right on the main shaft. Compute the needle-bar mechanism’s inertia torque at 5,000 rpm, separate “peak” from “work per revolution”, pick the motor, check the upper shaft for strength, fatigue and resonance, size the control-box heat sink with OpenFOAM and write the CNC programs. <b>The 400 W pick matches the real machine.</b>",
        ),
        "facts": [
            (("惯性力矩峰值", "Peak inertia torque"), "2.82", "N·m"),
            (("选出电机功率", "Motor selected"), "400", "W"),
            (("上轴一阶 / 工作频率", "Shaft 1st mode / running"), "14×", ""),
            (("散热器散热", "Heat sink rejects"), "23", "W"),
        ],
        "parts": [
            ("LS-101", ("LS-101 上轴", "LS-101 upper shaft"),
             ("<b>LS-101</b> 上轴 · Ø16 × 297 mm · 一阶 1185 Hz，是 5000 rpm 工作频率的 14 倍",
              "<b>LS-101</b> upper shaft · Ø16 × 297 mm · 1st mode 1185 Hz, 14× the 5,000 rpm running speed")),
            ("LS-HS", ("LS-HS 控制箱散热器", "LS-HS heat sink"),
             ("<b>LS-HS</b> 控制箱散热器 · 120×80 mm 底板、8 片直翅 · 2 m/s 风速散热 23.2 W",
              "<b>LS-HS</b> control-box heat sink · 120 × 80 mm base, 8 straight fins · 23.2 W at 2 m/s air")),
        ],
        "release": ("LOCKSTITCH-DD 第 1 版，带自制件 LS-101、LS-HS；校验结论“通过”随方案发出", "LOCKSTITCH-DD rev 1, with made parts LS-101 and LS-HS; the selection verdict “pass” travels with it"),
        "design": [
            {"t": ("动力学", "Dynamics"), "s": "ok", "who": ("设计院 · 针杆曲柄滑块机构", "Design · needle-bar slider-crank"),
             "body": (
                 "<p>针杆行程 35 mm（曲柄 17.5 mm、连杆 60 mm），主轴恒速 5000 rpm。往复质量的动能有增有减：惯性力矩峰值很大，一转做的功却约等于零。</p>"
                 '<dl class="kv"><dt>惯性力矩峰值</dt><dd>2.82 N·m</dd><dt>均方根</dt><dd>1.60 N·m</dd><dt>一转平均</dt><dd>−0.060 N·m（约为零）</dd><dt>最大盈亏功</dt><dd>ΔE = 2.23 J；教材近似 2.07 J</dd></dl>',
                 "<p>Needle-bar stroke 35 mm (crank 17.5 mm, rod 60 mm), main shaft at a steady 5,000 rpm. The reciprocating mass gains and loses energy: the inertia torque peaks high, yet the work per revolution is about zero.</p>"
                 '<dl class="kv"><dt>Peak inertia torque</dt><dd>2.82 N·m</dd><dt>RMS</dt><dd>1.60 N·m</dd><dt>Mean per revolution</dt><dd>−0.060 N·m (about zero)</dd><dt>Max energy swing</dt><dd>ΔE = 2.23 J; textbook estimate 2.07 J</dd></dl>'),
             "side": (
                 '<p class="note">针杆质量按杆宽、杆厚取的示意值，不是实物数据。</p>'
                 '<p>旧版（M13）把惯性力矩当成连续扭矩，并把与 400 W 的差距归到“没加平衡块”。M14 改正：平衡块只平衡机座振动，恒速下不改变驱动扭矩。</p>'
                 '<p class="course"><b>对应：</b>缝纫机课（机构各讲）；《机械设计》第 33.11 节</p>',
                 '<p class="note">The needle-bar mass is an illustrative value from bar width and thickness, not measured data.</p>'
                 '<p>The first run (M13) treated inertia torque as continuous torque and blamed the gap to 400 W on a missing counterweight. M14 corrected it: the counterweight only balances frame vibration and does not change drive torque at steady speed.</p>'
                 '<p class="course"><b>Course:</b> sewing-machine course (mechanism lessons); <i>Machine Design</i> §33.11</p>')},
            {"t": ("选型", "Selection"), "s": "ok", "who": ("设计院 · 上下限两种选法", "Design · upper and lower bound"),
             "body": (
                 "<p>引擎逐对校验 28 组电机与驱动器，按两种假设各选一次：</p>"
                 '<div class="tbl"><table><thead><tr><th>假设</th><th>结果</th></tr></thead><tbody><tr><td><b>下限</b>：惯量吸收波动，只付一转平均功</td><td>SGM7J-04A + SGD7S-2R8A，总体通过——<b>400 W，与 JUKI 实机一致</b></td></tr><tr><td><b>上限</b>：速度环很刚，电机吃下全部惯性力矩</td><td>SGM7J-08A 扭矩、转速够，但库里最大的驱动器 2.8 A 带不动（C9 失败）</td></tr></tbody></table></div>',
                 "<p>The engine checks 28 motor–drive pairs under two assumptions:</p>"
                 '<div class="tbl"><table><thead><tr><th>Assumption</th><th>Result</th></tr></thead><tbody><tr><td><b>Lower bound</b>: inertia absorbs the swing; motor supplies only the mean work</td><td>SGM7J-04A + SGD7S-2R8A, overall pass — <b>400 W, same as the JUKI machine</b></td></tr><tr><td><b>Upper bound</b>: stiff speed loop; motor supplies all inertia torque</td><td>SGM7J-08A has the torque and speed, but the largest drive in the library (2.8 A) cannot run it (C9 fails)</td></tr></tbody></table></div>'),
             "side": (
                 '<p class="note">缝制阻力和摩擦零件库与样本都没有，下限没算它们，结论待确认。</p>'
                 '<dl class="kv"><dt>转速不均匀系数</dt><dd>δ = 0.083</dd><dt>降到 0.05（示例值）</dt><dd>再加约 6.5e-5 kg·m² 的手轮</dd><dt>0→5000 rpm 用 0.1 s</dt><dd>转子 0.25 + 机构 0.26 N·m</dd></dl>'
                 '<p class="course"><b>对应：</b>特色选修“伺服驱动与运动控制”</p>',
                 '<p class="note">Sewing resistance and friction are in neither the library nor the brochure; the lower bound leaves them out, so the verdict stays “to be confirmed”.</p>'
                 '<dl class="kv"><dt>Speed fluctuation</dt><dd>δ = 0.083</dd><dt>To reach 0.05 (example)</dt><dd>Add about 6.5e-5 kg·m² handwheel</dd><dt>0→5,000 rpm in 0.1 s</dt><dd>Rotor 0.25 + mechanism 0.26 N·m</dd></dl>'
                 '<p class="course"><b>Course:</b> elective “Servo Drives and Motion Control”</p>')},
            {"t": ("上轴 · 强度与频率", "Shaft · strength & modes"), "s": "ok", "who": ("设计院 · 有限元、疲劳、模态", "Design · FEA, fatigue, modal"),
             "body": (
                 "<p>上轴 LS-101 两个轴承位径向支承、电机端固定，做模态、扭转有限元和疲劳。</p>"
                 '<dl class="kv"><dt>一阶固有频率</dt><dd>1184.7 Hz，工作 83.3 Hz，比值 14.2，远离共振</dd><dt>最大 Von Mises</dt><dd>37.6 MPa，安全系数 9.4</dd><dt>手算</dt><dd>Ø10 段 τ = 16T/πd³ = 14.4 MPa（等效 24.9）</dd><dt>疲劳</dt><dd>5000 rpm 扭矩记录雨流计数：无限寿命</dd></dl>',
                 "<p>Upper shaft LS-101, radially supported at two bearing seats and fixed at the motor end: modes, torsion FEA and fatigue.</p>"
                 '<dl class="kv"><dt>1st mode</dt><dd>1184.7 Hz vs 83.3 Hz running, ratio 14.2, far from resonance</dd><dt>Max von Mises</dt><dd>37.6 MPa, safety factor 9.4</dd><dt>Hand check</dt><dd>Ø10 section τ = 16T/πd³ = 14.4 MPa (equivalent 24.9)</dd><dt>Fatigue</dt><dd>Rainflow on the 5,000 rpm torque record: infinite life</dd></dl>'),
             "side": (
                 '<p class="note">模态没算装在轴上的曲柄、带轮和转子的质量。</p><p class="course"><b>对应：</b>《机械设计》第 33.11 节；数字工厂实验 8、12</p>',
                 '<p class="note">The modal run leaves out crank, pulley and rotor mass mounted on the shaft.</p><p class="course"><b>Course:</b> <i>Machine Design</i> §33.11; factory labs 8 and 12</p>')},
            {"t": ("散热 CFD", "Cooling CFD"), "s": "ok", "who": ("设计院 · OpenFOAM", "Design · OpenFOAM"),
             "body": (
                 "<p>控制箱散热器：铝底板 120×80×6 mm、8 片 30 mm 直翅；风扇风速 2 m/s，空气 35 °C，散热器 60 °C。</p>"
                 '<dl class="kv"><dt>散热量</dt><dd>23.2 W</dd><dt>平均散热系数</dt><dd>13.6 W/(m²·K)</dd></dl>',
                 "<p>Control-box heat sink: 120 × 80 × 6 mm aluminium base, eight 30 mm straight fins; fan air 2 m/s at 35 °C, sink at 60 °C.</p>"
                 '<dl class="kv"><dt>Heat rejected</dt><dd>23.2 W</dd><dt>Mean film coefficient</dt><dd>13.6 W/(m²·K)</dd></dl>'),
             "side": ('<p class="note">驱动器损耗零件库没有数据，23 W 够不够待确认。</p><p class="course"><b>对应：</b>数字工厂实验 14</p>',
                      '<p class="note">Drive losses are not in the library, so whether 23 W is enough is to be confirmed.</p><p class="course"><b>Course:</b> factory lab 14</p>')},
            {"t": ("拓扑优化", "Topology optimization"), "s": "ok", "who": ("设计院 · 拓扑优化", "Design · topology optimization"),
             "body": ("<p>电机支架：左边固定、右下角受力，保留 40% 材料，45 次迭代。</p>"
                      '<div class="bar"><div><span>优化前柔度</span><i class="ghost" style="width:100%"></i><span>403</span></div><div><span>优化后柔度</span><i style="width:12.4%"></i><span>50</span></div></div>',
                      "<p>Motor bracket: fixed on the left, loaded at the lower right, 40% material kept, 45 iterations.</p>"
                      '<div class="bar"><div><span>Before</span><i class="ghost" style="width:100%"></i><span>403</span></div><div><span>After</span><i style="width:12.4%"></i><span>50</span></div></div>'),
             "side": ('<dl class="kv"><dt>板面积</dt><dd>2,124 mm²</dd></dl>', '<dl class="kv"><dt>Plate area</dt><dd>2,124 mm²</dd></dl>')},
            {"t": ("数控编程", "CNC programming"), "s": "ok", "who": ("设计院 · CAM", "Design · CAM"),
             "body": ("<p>上轴用 Ø20 棒料，两次装夹车削，程序过了自动检查。</p>"
                      '<dl class="kv"><dt>LS-101 车削</dt><dd>2 个程序，约 1.5 min</dd><dt>机床</dt><dd>示例数控车床（虚构）</dd></dl>',
                      "<p>The upper shaft is turned from Ø20 bar in two setups; the programs passed the automatic check.</p>"
                      '<dl class="kv"><dt>LS-101 turning</dt><dd>2 programs, about 1.5 min</dd><dt>Machine</dt><dd>Example lathe (fictional)</dd></dl>'),
             "side": ("@gcode", "@gcode")},
        ],
        "gcode": "%\nO1001 (LS-101 车削 右端[第一次装夹])\n(毛坯 Ø20×299)\n(机床 示例数控车床[虚构])\n(T01 外圆粗车刀)\n(T02 外圆精车刀)\nG21 G18 G40 G97 G99\nG00 X200.0 Z150.0\nT0101\nG50 S3000\nG96 S120 M03\n(车端面[余量 1])\nG00 X24.0 Z2.0 M08\nZ0.0\nG01 X-1.0 F0.3\nG00 Z2.0\nX24.0\n(分层粗车[每层 ap=2.5])\nX15.0\n…",
        "factory": [
            {"t": ("转为 ERP 物料", "Into ERP"), "s": "ok", "who": ("工厂 · 厂长确认 → ERPNext", "Factory · plant manager approves → ERPNext"),
             "body": ("<p>厂长确认后，桥接程序在 ERPNext 里建供应商、物料和带工序的 BOM。</p>"
                      '<dl class="kv"><dt>供应商</dt><dd>2 家</dd><dt>物料</dt><dd>6 种</dd><dt>BOM</dt><dd>3 张（含工序）</dd></dl>',
                      "<p>After approval, the bridge creates suppliers, items and routed BOMs in ERPNext.</p>"
                      '<dl class="kv"><dt>Suppliers</dt><dd>2</dd><dt>Items</dt><dd>6</dd><dt>BOMs</dt><dd>3 (with operations)</dd></dl>'),
             "side": ('<p class="note">两家供应商都没填采购提前期，交期待确认。</p><p class="course"><b>对应：</b>特色选修“ERP 原理与实践”</p>',
                      '<p class="note">Neither supplier has a lead time on file; lead time to be confirmed.</p><p class="course"><b>Course:</b> elective “ERP Principles and Practice”</p>')},
            {"t": ("工艺规程", "Process plans"), "s": "ok", "who": ("工厂 · 工艺员 → AI 评审 → 技术负责人", "Factory · process engineer → AI review → chief engineer"),
             "body": ("<p>LS-101 6 道工序，粗基准为毛坯外圆；LS-HS 3 道工序，粗基准为毛坯底面。技术负责人批准为第 1 版。</p>",
                      "<p>LS-101 has 6 operations with the stock diameter as rough datum; LS-HS has 3 with the stock bottom face. The chief engineer approves rev 1.</p>"),
             "side": ('<p class="note">细长轴 L/d ≈ 30，实际要顶尖、跟刀架；仿真不计让刀。</p><p class="course"><b>对应：</b>《机械制造技术》工艺规程设计；缝纫机课“零件制造”</p>',
                      '<p class="note">A slender shaft (L/d ≈ 30) needs centers and a follow rest in practice; the simulation ignores deflection.</p><p class="course"><b>Course:</b> <i>Manufacturing Technology</i>, process planning; sewing-machine course, part manufacturing</p>')},
            {"t": ("接单与 MRP", "Order & MRP"), "s": "ok", "who": ("工厂 · 计划员", "Factory · planner"),
             "body": ("<p>示例客户订 2 台，MRP 生成工单和请购单。</p>"
                      '<div class="tbl"><table><thead><tr><th>工单</th><th class="r">数量</th><th class="r">工时</th></tr></thead><tbody><tr><td>LS-101 上轴</td><td class="r">2</td><td class="r">约 53 min</td></tr><tr><td>LS-HS 散热器</td><td class="r">2</td><td class="r">约 62 min</td></tr><tr><td>LOCKSTITCH-DD 总装</td><td class="r">2</td><td class="r">约 133 min</td></tr></tbody></table></div>',
                      "<p>A demo customer orders 2 units; MRP creates work orders and purchase requests.</p>"
                      '<div class="tbl"><table><thead><tr><th>Work order</th><th class="r">Qty</th><th class="r">Time</th></tr></thead><tbody><tr><td>LS-101 upper shaft</td><td class="r">2</td><td class="r">≈ 53 min</td></tr><tr><td>LS-HS heat sink</td><td class="r">2</td><td class="r">≈ 62 min</td></tr><tr><td>LOCKSTITCH-DD assembly</td><td class="r">2</td><td class="r">≈ 133 min</td></tr></tbody></table></div>'),
             "side": ('<dl class="kv"><dt>请购</dt><dd>SGD7S-2R8A ×2、SGM7J-04A ×2、原材料 RM-6061-B125 ×10</dd></dl><p class="course"><b>对应：</b>特色选修“生产计划与排程”</p>',
                      '<dl class="kv"><dt>Requests</dt><dd>SGD7S-2R8A ×2, SGM7J-04A ×2, stock RM-6061-B125 ×10</dd></dl><p class="course"><b>Course:</b> elective “Production Planning and Scheduling”</p>')},
            {"t": ("采购到货", "Receiving"), "s": "ok", "who": ("工厂 · 仓库", "Factory · warehouse"),
             "body": ("<p>3 种物料到货，ERPNext 生成收货单，入原材料库。</p>", "<p>Three items arrive; ERPNext posts a purchase receipt into raw-material stock.</p>"),
             "side": ('<p class="course"><b>对应：</b>特色选修“仓储管理与智能仓库”</p>', '<p class="course"><b>Course:</b> elective “Warehousing”</p>')},
            {"t": ("MES 车间执行", "MES execution"), "s": "ok", "who": ("工厂 · 车间终端", "Factory · shop-floor terminal"),
             "body": ("<p>两张自制件工单派到 7 台设备完工，再下总装工单。</p>"
                      '<dl class="kv"><dt>自制件</dt><dd>MFG-WO-2026-00007、00008，仿真 52 s 完工</dd><dt>总装</dt><dd>MFG-WO-2026-00009，84 s 完工</dd></dl>',
                      "<p>Two made-part work orders run on 7 machines, then the assembly order.</p>"
                      '<dl class="kv"><dt>Made parts</dt><dd>MFG-WO-2026-00007, 00008, done in 52 s simulated</dd><dt>Assembly</dt><dd>MFG-WO-2026-00009, done in 84 s</dd></dl>'),
             "side": ('<p class="course"><b>对应：</b>特色选修“制造执行系统 MES”</p>', '<p class="course"><b>Course:</b> elective “Manufacturing Execution Systems”</p>')},
            {**HUB, "side": ('<dl class="kv"><dt>工厂复算</dt><dd>LS-101 有限元 34.3 MPa、安全系数 10.3（设计院 37.6 MPa；网格与固定面不同，量级一致）；粗车程序 2 个，检查通过</dd></dl><p class="course"><b>对应：</b>“智能制造与数字孪生”；数字工厂实验 15</p>',
                             '<dl class="kv"><dt>Factory re-check</dt><dd>LS-101 FEA 34.3 MPa, safety factor 10.3 (design 37.6 MPa; different mesh and fixed face, same order); 2 roughing programs pass</dd></dl><p class="course"><b>Course:</b> “Smart Manufacturing and Digital Twins”; factory lab 15</p>')},
        ],
        "open": [
            (("缝制阻力", "Sewing resistance"),
             ("缝制阻力和摩擦零件库与样本都没有。400 W 是不含它们的下限，结论待确认。",
              "Neither the library nor the brochure gives sewing resistance or friction. The 400 W pick is a lower bound without them.")),
            (("刚性速度环要更大的驱动器", "A stiff speed loop needs a bigger drive"),
             ("SGM7J-08A 扭矩、转速都够，但库里最大的驱动器 SGD7S-2R8A 带不动，需要企业补更大驱动器的数据。",
              "SGM7J-08A has the torque and speed, but the largest drive in the library cannot run it; a larger drive’s data must be added.")),
            (("驱动器发热", "Drive heat"),
             ("散热器能散 23 W，但驱动器损耗零件库没有数据，够不够待确认。",
              "The heat sink rejects 23 W, but drive losses are not in the library, so adequacy is unconfirmed.")),
            (("演练用的假设", "Assumptions in this run"),
             ("针杆质量是示意值；起停加速时间 0.05 / 0.1 / 0.2 s 是设计假设；δ = 0.05 只为说明手轮大小，不是标准值；供电按三相 200 V。",
              "Needle-bar mass is illustrative; start-stop times of 0.05/0.1/0.2 s are design assumptions; δ = 0.05 only illustrates handwheel size and is not a standard; supply is 3-phase 200 V.")),
        ],
        "courses": [
            (("缝纫机设计与制造", "Sewing Machine Design and Manufacturing"), ("31 讲：机构、电控、样机与零件制造", "31 lessons: mechanisms, controls, prototypes and part making"), ("已上线", "Online")),
            (("机械设计", "Machine Design"), ("第 33.11 节：平缝机上轴 LS-101", "§33.11: the lockstitch upper shaft LS-101"), ("教材已上线", "Online")),
            (("伺服驱动与运动控制", "Servo Drives and Motion Control"), ("惯性力矩、盈亏功与电机选型", "Inertia torque, energy swing and motor sizing"), ("特色选修 · 建设中", "Elective · planned")),
            (("机械制造技术", "Manufacturing Technology"), ("细长轴车削、散热器加工", "Slender-shaft turning, heat-sink machining"), ("教材编写中", "In writing")),
            (("ERP 原理与实践 · 制造执行系统 MES", "ERP and MES"), ("物料与 BOM、MRP、工单与报工", "Items and BOMs, MRP, work orders"), ("特色选修 · 建设中", "Elective · planned")),
        ],
        "labs": [("实验 8", "输出轴强度与疲劳校核", "Lab 8", "Output shaft strength and fatigue"),
                 ("实验 12", "一根轴的数字化设计与两个典型案例", "Lab 12", "Digital design of a shaft"),
                 ("实验 14", "风扇冷却的流体与传热分析", "Lab 14", "Fan cooling: flow and heat transfer"),
                 ("实验 7", "数字工厂闭环（订单 → 车间 → 入库）", "Lab 7", "The factory loop: order → shop → stock")],
        "files": "LS-101.step、LS-HS.step、O1001.nc、O1002.nc",
        "src": "lockstitch",
        "basis": ('<a href="https://www.sewingmachinesplus.com/media/products/juki/juki-9000c/brochure.pdf" target="_blank" rel="noopener">JUKI DDL-9000C 样本</a>',
                  '<a href="https://www.sewingmachinesplus.com/media/products/juki/juki-9000c/brochure.pdf" target="_blank" rel="noopener">JUKI DDL-9000C brochure</a>'),
    },
]
