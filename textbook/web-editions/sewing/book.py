# -*- coding: utf-8 -*-
"""Book metadata: parts and chapters (zh / en)."""
TITLE = {"zh": "缝纫机设计与制造", "en": "Sewing Machine Design and Manufacturing"}

PARTS = [
    # (zh numeral, zh name, en name, [chapter numbers])
    ("第一篇", "绪论", "Part I · Introduction", [1, 2]),
    ("第二篇", "平缝机机构", "Part II · Lockstitch Mechanisms", [3, 4, 5, 6, 7, 8]),
    ("第三篇", "包缝、绷缝与链缝", "Part III · Overlock, Coverstitch and Chainstitch", [9, 10]),
    ("第四篇", "特种机与自动单元", "Part IV · Special Machines and Automatic Units", [11, 12]),
    ("第五篇", "电气控制", "Part V · Electrical Control", [13, 14, 15, 16, 17, 18]),
    ("第六篇", "电控原型机开发与自动化测试", "Part VI · Control Prototyping and Automated Testing", [19, 20, 21, 22]),
    ("第七篇", "制造与数字工厂", "Part VII · Manufacturing and the Digital Factory", [23, 24, 25, 26, 27]),
    ("第八篇", "工厂与未来", "Part VIII · Factories and the Future", [28, 29, 30, 31]),
]

# n: (zh title, en title, zh summary, en summary)
CH = {
 1: ("缝制设备与服装产业", "Sewing Equipment and the Apparel Industry", "发展史、设备分类、产业格局、全书路线图", "History, equipment classes, the industry, a roadmap of the book"),
 2: ("线迹的形成", "How a Stitch Is Formed", "整机结构、线迹分类、301 线迹形成、时序", "Machine layout, stitch classes, forming stitch 301, timing"),
 3: ("刺布机构", "The Needle-Bar Mechanism", "曲柄滑块分析、连杆比、惯性力与平衡", "Slider-crank analysis, link ratio, inertia forces and balancing"),
 4: ("挑线机构", "The Thread Take-up Mechanism", "连杆式、凸轮式、旋转式，供线量与耗线量", "Link, cam and rotary take-ups; thread supply and consumption"),
 5: ("钩线机构", "The Hook Mechanism", "全回转与半回转旋梭、摆梭，钩线定时与间隙", "Full and half rotary hooks, oscillating shuttles, loop-catch timing and clearance"),
 6: ("送布机构", "The Feed Mechanism", "下送、差动、针送、上下复合送布，针距调节", "Drop, differential, needle and compound feed; stitch-length adjustment"),
 7: ("线张力与线迹质量", "Thread Tension and Stitch Quality", "夹线器、张力曲线、线迹缺陷", "Tension assemblies, tension curves, stitch defects"),
 8: ("运动协调与整机动力学", "Motion Coordination and Machine Dynamics", "时序设计、振动噪声、润滑", "Timing design, vibration and noise, lubrication"),
 9: ("包缝机", "The Overlock Machine", "500 类线迹、弯针、切刀、差动送布", "Class 500 stitches, loopers, knives, differential feed"),
 10: ("绷缝机与链缝机", "Coverstitch and Chainstitch Machines", "400、600 类线迹与机构", "Class 400 and 600 stitches and their mechanisms"),
 11: ("典型特种机的机构", "Mechanisms of Typical Special Machines", "锁眼、钉扣、套结、花样机、绗缝、刺绣机的机械部分", "Buttonholers, button sewers, bartackers, pattern sewers, quilters and embroidery machines"),
 12: ("自动缝制单元与柔性制衣单元", "Automatic Sewing Units and Flexible Cells", "自动开袋、上袖等单元，吊挂系统，单元布局", "Pocket-welting and sleeve-setting units, hanger systems, cell layout"),
 13: ("控制基础：电机、驱动与传感", "Control Basics: Motors, Drives and Sensors", "伺服、步进、电磁铁与气动，编码器与传感器，控制器与总线", "Servos, steppers, solenoids and pneumatics; encoders and sensors; controllers and buses"),
 14: ("工业平缝机电控", "Control of the Industrial Lockstitch Machine", "主轴定位与调速、剪线拨线倒缝抬压脚时序、电子针距、电子张力", "Spindle positioning and speed, trimming and backtack sequences, electronic feed and tension"),
 15: ("花样机与锁眼、钉扣、套结机控制", "Control of Pattern Sewers, Buttonholers and Bartackers", "X–Y 运动控制、主轴与送料同步、插补与加减速、花样编程", "X–Y motion control, spindle–feed synchronisation, interpolation, pattern programming"),
 16: ("电脑刺绣机控制", "Control of Computerised Embroidery Machines", "多头同步、绷架运动、换色剪线、断线检测、绣花文件", "Multi-head sync, frame motion, colour change and trimming, thread-break detection, design files"),
 17: ("电脑横机（毛衣编织机）控制", "Control of Computerised Flat Knitting Machines", "编织原理、选针、度目、摇床、纱嘴、牵拉，花型编程与全成型", "Knitting principles, needle selection, stitch cams, racking, carriers, take-down, programming and whole-garment"),
 18: ("电控系统的设计、制造与测试", "Designing, Building and Testing the Control Box", "硬件与 PCB、EMC 与热设计、嵌入式软件、生产测试", "Hardware and PCB, EMC and thermal design, embedded software, production test"),
 19: ("电控原型平台与零件库", "The Prototyping Platform and the Parts Library", "一套参考架构做四种机器、电控模块入库、从需求到 BOM 的快速配套、角度驱动的固件框架、硬件在环", "One reference architecture for four machines, control modules in the parts library, from requirements to BOM, angle-driven firmware, hardware-in-the-loop"),
 20: ("平缝机与包缝机电控原型", "Lockstitch and Overlock Control Prototypes", "系统构成、BOM 与接线、固件、逐步调试、两台原型的共用与差异", "System build-up, BOM and wiring, firmware, step-by-step bring-up, what the two prototypes share"),
 21: ("电子花样机与电脑横机电控原型", "Pattern Sewer and Flat-Knitting Control Prototypes", "XY 平台与针–模板同步、缩比横机的机头、选针、度目、纱嘴与牵拉", "X–Y table and needle–clamp sync; a scaled flat-knitting carriage, selection, stitch cams, carriers and take-down"),
 22: ("自动化测试与持续迭代", "Automated Testing and Continuous Iteration", "测试金字塔、通用测试台、测试脚本、持续集成、出厂测试数据回流、从原型到工业级", "Test pyramid, a universal test bench, test scripts, CI, end-of-line data back to the factory, prototype to industrial grade"),
 23: ("缝纫机的设计、制造与检测", "Designing, Building and Testing the Sewing Machine", "关键零件工艺、精度与可靠性、噪声振动试验、标准", "Key-part processes, accuracy and reliability, noise and vibration tests, standards"),
 24: ("机针与旋梭的制造", "Manufacturing Needles and Rotary Hooks", "机针的拉丝、成形、冲孔、热处理与镀层；旋梭的锻造、精加工、渗碳、梭道磨削、研磨、DLC 与选配", "Needle drawing, forming, eye punching, heat treatment and plating; hook forging, machining, carburising, race grinding, lapping, DLC and selective assembly"),
 25: ("机壳与凸轮的制造", "Manufacturing Housings and Cams", "铸造与时效、基准与夹具、一次装夹镗孔、凸轮廓线加工与磨削、廓线误差的影响", "Casting and ageing, datums and fixtures, single-setup boring, cam-profile machining and grinding, effects of profile error"),
 26: ("设备联网与数字孪生", "Connected Machines and Digital Twins", "联网协议、数据采集、MES 对接、远程运维", "Protocols, data acquisition, MES integration, remote service"),
 27: ("数字工厂：缝纫机工厂的整体信息化解决方案", "The Digital Factory: An Integrated IT Solution for a Sewing-Machine Plant", "统一数据总线、ERP–PLM–MES–QMS、零件库与配置、工艺与质量闭环、固件版本、分期实施", "Unified data bus, ERP–PLM–MES–QMS, parts library and configuration, process and quality loops, firmware versions, phased roll-out"),
 28: ("服装生产工艺与缝制车间", "Garment Processes and the Sewing Floor", "工序分析、标准工时、生产线平衡、精益生产", "Operation breakdown, standard minutes, line balancing, lean production"),
 29: ("典型服装工厂", "Typical Garment Factories", "西服、衬衫、T 恤与针织、毛衫、小单快反", "Suits, shirts, T-shirts and knits, sweaters, small-batch quick response"),
 30: ("缝制设备发展趋势", "Trends in Sewing Equipment", "自动化、缝制机器人、数字化、按需生产", "Automation, sewing robots, digitalisation, on-demand production"),
 31: ("人工智能与制衣业", "Artificial Intelligence and Apparel Making", "AI 设计、视觉检测、智能排产、AI 缝纫机、就业与产业转移", "AI design, vision inspection, scheduling, AI sewing machines, jobs and industrial shift"),
}

def part_of(n):
    for p in PARTS:
        if n in p[3]:
            return p
NEW = [19, 20, 21, 22, 24, 25, 27]
