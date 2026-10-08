"""减速器厂专题案例（中英成对）。

数字取自教学工厂的一次演练记录 runs/digital-thread_2026-10-08.txt
（脚本 runs/digital_thread_run.py：在 factory/digital 目录下、有本地 PostgreSQL 时运行；
与实验 16 同一套引擎：注入批次投诉 → 追溯 → 三个服务方案）。改数之前先重跑核对。
"""

STORIES = [
    {
        "slug": "digital-thread",
        "no": "04",
        "name": ("一台报警，追到砂轮", "From one complaint to one grinding wheel"),
        "title": ("客户一个电话，追到车间里的那片砂轮，再找出还有谁家的设备有同样的隐患",
                  "One customer call, traced back to one grinding wheel, then forward to every machine that shares the risk"),
        "lede": (
            "北方矿业来电：2 号主运皮带上的减速器有异响、振动变大。厂情中枢沿着数据往回追：这台减速器装的哪根输出轴、在哪台磨床上用哪片砂轮磨的；再往前追：同一片砂轮还磨了哪些轴、装进了哪些客户的设备。然后<b>按数字孪生的健康度排出风险，给出三个服务方案，算好人、天数和费用</b>，人批准后派工。",
            "Northern Mining calls: the gearbox on belt line 2 is noisy and vibrating more. The command center walks the data back — which output shaft is in this gearbox, which grinder and which wheel ground it — then forward: what else that wheel ground, and whose machines those shafts went into. It <b>ranks the risk with the digital twins, prices three service options in engineers, days and dollars</b>, and dispatches once a person approves.",
        ),
        "facts": [
            (("追溯链", "Trace chain"), "6", ("环", "links")),
            (("同批另外装在", "Same batch also in"), "2", ("台设备", "units")),
            (("推荐方案费用", "Recommended option"), "$973", ("", "")),
            (("推荐方案漏掉高风险", "High-risk units missed"), "0", ("台", "")),
        ],
        "chain": [
            {"k": ("投诉", "Complaint"), "v": "WQR105-H2404-01", "sub": ("北方矿业 · 2 号主运皮带", "Northern Mining · belt line 2"), "tone": "alarm",
             "d": ("客户来电：减速器异响，振动比以前大。投诉登记后，规则 C1 在下一个检测周期开出异常。数字孪生：健康度绿，但最先到期的中间轴轴承 B（6206-2RS）寿命已用 73.7%。",
                   "Phone complaint: noise and more vibration. Rule C1 opens an anomaly on the next detection cycle. Digital twin: health green, but the first-due bearing (intermediate shaft B, 6206-2RS) has used 73.7% of its life."),
             "how": "规则 C1（客户投诉）/ rule C1"},
            {"k": ("输出轴", "Output shaft"), "v": "SH301-H2404-01", "sub": ("出厂档案", "Build record"), "tone": "",
             "d": ("从现场设备找到它的出厂总成，再找到装在里面的输出轴。依据是数字孪生的出厂数据。",
                   "From the field unit to its shipped assembly, then to the output shaft installed in it, using the twin’s build record."),
             "how": "PartSerial.became → PartSerial.installed_in"},
            {"k": ("砂轮", "Grinding wheel"), "v": "grd-01/S1", "sub": ("GRD-01 外圆磨床", "GRD-01 cylindrical grinder"), "tone": "cause",
             "d": ("这根轴的磨外圆工序记下了用的是哪片砂轮：grd-01/S1，加工时砂轮剩余寿命 62%。轴承位尺寸由这一刀决定。",
                   "The grinding operation recorded which wheel it used: grd-01/S1, with 62% wheel life left at the time. This pass sets the bearing seat size."),
             "how": "PartSerial.processed（加工记录 / machining record）"},
            {"k": ("同一片砂轮磨出", "Same wheel also ground"), "v": "SH301-H2406-09 · SH301-H2408-05", "sub": ("另外 2 根输出轴", "2 more output shafts"), "tone": "",
             "d": ("反过来查：同一片砂轮还磨了两根输出轴。如果问题出在砂轮（修整不及时、磨损），这两根轴的轴承位也可能偏。",
                   "Searching the other way: the same wheel ground two more shafts. If the wheel is the cause (late dressing, wear), their bearing seats may be off too."),
             "how": "PartSerial.processed（props.tool = grd-01/S1）"},
            {"k": ("装在", "Installed in"), "v": "WQR105-H2408-05", "sub": ("东港码头 · 散货输送线", "East Port · bulk conveyor"), "tone": "risk",
             "d": ("健康度黄：换油已过期；最先到期的轴承寿命已用 51.4%。按规则（健康度红 / 黄，或轴承寿命用过 50%）判为<b>高风险</b>。",
                   "Health yellow: oil change overdue; first-due bearing at 51.4% of life. By the rule (health red or yellow, or a bearing past 50%) it is <b>high risk</b>."),
             "how": "PartSerial.installed_in → FieldUnit.customer"},
            {"k": ("装在", "Installed in"), "v": "WQR105-H2406-09", "sub": ("鲜丰食品 · 包装线", "Fresh Foods · packaging line"), "tone": "",
             "d": ("健康度绿，没有报警，最先到期的轴承寿命只用了 3.5%。在排查范围里，但不是高风险。",
                   "Health green, no alarms, first-due bearing at only 3.5% of life. In the check scope, but not high risk."),
             "how": "PartSerial.installed_in → FieldUnit.customer"},
        ],
        "options": [
            {"key": "A", "label": ("只修出问题的", "Repair the reported unit only"), "units": 1, "eng": ("赵岩", "Zhao Yan"), "days": 2, "pd": "0.5", "cost": "$493", "cust": 1, "miss": ("1 台（WQR105-H2408-05）", "1 (WQR105-H2408-05)"), "rec": False},
            {"key": "B", "label": ("修 + 高风险上门点检", "Repair + inspect high-risk units"), "units": 2, "eng": ("赵岩、周海", "Zhao Yan, Zhou Hai"), "days": 2, "pd": "1.0", "cost": "$973", "cust": 2, "miss": ("0", "0"), "rec": True},
            {"key": "C", "label": ("整批排查", "Inspect the whole batch"), "units": 3, "eng": ("赵岩、周海、林青", "Zhao Yan, Zhou Hai, Lin Qing"), "days": 2, "pd": "1.5", "cost": "$1,453", "cust": 3, "miss": ("0", "0"), "rec": False},
        ],
        "options_note": (
            "三台都已过保修期，费用全部向客户收取；备件都是 2 套 6206-2RS 轴承（BRG-6206）。工程师按区域排班：北部赵岩、东部周海、南部林青，同区域每人每天最多 2 单。中枢推荐 B：比 C 少通知一家客户、少花 $480，又不漏掉高风险的那台。",
            "All three units are out of warranty, so customers are billed; each option uses 2 sets of 6206-2RS bearings (BRG-6206). Engineers are scheduled by region — Zhao Yan north, Zhou Hai east, Lin Qing south — at most 2 jobs per person per day. The command center recommends B: one fewer customer to notify and $480 less than C, without missing the high-risk unit.",
        ),
        "after": [
            (("起草动作", "Draft actions"), ("采纳 B，AI 起草三个动作：服务派工、备件出库、给东港码头的预防性服务通知。", "Adopting B, the AI drafts three actions: service dispatch, spare-parts issue and a preventive-service notice to East Port.")),
            (("人来批准", "A person approves"), ("派工和出库要花钱，只有厂长能批；客户通知由另一位售后或老师批，不能批自己发起的。", "Dispatch and parts cost money, so only the plant manager can approve; the notice needs another service person or the teacher — never its author.")),
            (("落到 ERPNext", "Into ERPNext"), ("批准后 ERPNext 里有服务单（写明工程师和上门日）和备件出库单；工程师日历多了单子。", "After approval ERPNext holds the service issues (engineer and visit date) and the stock entry; the engineers’ calendars fill in.")),
            (("回访", "Follow-up"), ("工程师按日子上门换轴承，孪生健康度回到绿；第二天客户回访打分，响应慢、拖期、修完又坏都会扣分。", "Engineers replace the bearings on schedule and the twin returns to green; the next day the customer scores the service, losing points for slow response, delay or a repeat failure.")),
        ],
        "everyday": ("生活里的同一件事：汽车厂发现某批刹车片有问题，按车架号查出用了这批零件的车，给车主寄召回通知。",
                     "The everyday version: a carmaker finds a bad batch of brake pads, looks up every VIN that got them, and mails recall notices."),
        "open": [
            (("只看同一片砂轮够吗", "Is one wheel the right batch?"),
             ("批次还可以按同一张工单、同一炉热处理、同一批轴承来划。范围划窄会漏，划宽会多花钱、多惊动客户。",
              "Batches can also be cut by work order, heat-treat lot or bearing lot. Too narrow misses units; too wide costs more and alarms more customers.")),
            (("这笔钱算谁的", "Whose budget pays?"),
             ("保修内由工厂出钱。该算售后、质量还是生产？怎样从源头少花这笔钱，比如把砂轮修整间隔从 30 件改为 20 件？",
              "In warranty the factory pays. Should it land on service, quality or production? How do you cut it at the source — say, dressing the wheel every 20 parts instead of 30?")),
            (("演练是教学情景", "This run is a teaching scenario"),
             ("客户、设备和砂轮批次都是教学工厂的情景数据，现场时钟 1 分钟 = 1 天。追溯和方案的算法与线上一致。",
              "Customers, units and wheel batches are scenario data in the teaching factory, with a field clock of 1 minute = 1 day. The tracing and option logic are the same code that runs live.")),
        ],
        "courses": [
            (("质量管理与 SPC", "Quality Management and SPC"), ("批次追溯、不合格品处理、CAPA", "Batch traceability, nonconformance, CAPA"), ("特色选修 · 建设中", "Elective · planned")),
            (("设备管理与预测性维护", "Equipment Management and Predictive Maintenance"), ("数字孪生、轴承寿命、维护时机", "Digital twins, bearing life, maintenance timing"), ("特色选修 · 建设中", "Elective · planned")),
            (("智能制造与数字孪生", "Smart Manufacturing and Digital Twins"), ("工厂本体、异常、追因、推演与动作", "Factory ontology, anomalies, root cause, what-if and actions"), ("特色选修 · 建设中", "Elective · planned")),
            (("工业数据与 AI 代理", "Industrial Data and AI Agents"), ("AI 代理怎样调工具、引依据、只起草不擅自执行", "How the AI agent calls tools, cites evidence and only drafts"), ("特色选修 · 建设中", "Elective · planned")),
            (("机械制造技术", "Manufacturing Technology"), ("磨削、砂轮修整与加工误差", "Grinding, wheel dressing and machining error"), ("教材编写中", "In writing")),
        ],
        "labs": [("实验 16", "客户投诉的追溯、召回与服务决策", "Lab 16", "Complaint traceability, recall and service decisions"),
                 ("实验 15", "车间异常的追因、推演与决策", "Lab 15", "Shop-floor anomalies: root cause, what-if, decision"),
                 ("实验 13", "减速器数字孪生与预测性维护", "Lab 13", "Gearbox digital twin and predictive maintenance")],
        "basis": ("问渠数字工厂教学模式演练（2026-10-08），引擎与实验 16 相同；记录见仓库 tools/site_cases/runs/。",
                  "WenQuest digital factory, teaching-mode run (2026-10-08), same engine as Lab 16; record in tools/site_cases/runs/ in the repository."),
    },
]
