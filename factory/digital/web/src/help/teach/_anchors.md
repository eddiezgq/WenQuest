# 教学版帮助：“带我去做”要的页面标记（给合并施工用）

> 第 30 轮 H-3。教学版各章的 `goto` 块用到下面这些引导（tour）。每一步高亮一个带 `data-help="名字"` 的元素。
> 合并时：① 把下表的 `data-help` 加到对应 .vue 文件；② 把第三节的引导并进 `web/src/help/tours.json`；
> ③ **本文件和 `_videos.md` 用完请移出 `help/teach/`**（例如放到 `docs/实施细则/附件/`）：`help/index.js` 用
> `import.meta.glob('./*/*.md')` 把这个目录里所有 .md 都当章节，`tests/test_help.py` 也要求文件名是 `NN-名字.md`，
> 留在这里会多出两“章”并让测试失败。

## 一、注意

- `tests/test_help.py` 只在**页面文件本身**（`pages/X.vue`）或 `App.vue` 里找 `data-help="…"` 字符串，不看组件。
  所以标记在组件里的元素（教师控制台、推演与建议、生产与成本），要把 `data-help` 写在**页面里使用这个组件的标签上**
  （例如 `<TeacherConsole data-help="dir-console" />`）。这几个组件都是单根元素，属性会落到根元素上。
- `v-for` 里的元素加标记，引导会高亮第一个（`querySelector` 取第一个）。
- 引导支持 `query`（例如 `{"path": "/maint", "query": {"tab": "pm"}}`），用来打开某个标签页。
- 名字沿用那边（freecad-ai-parts）已有的，同一个元素同一个名字。

## 二、要加的标记

### 沿用那边的名字（元素在这边也有，只差属性）

| 页面文件 | 元素 | data-help |
| --- | --- | --- |
| `App.vue` | 左栏“资源 → 帮助”的 `router-link` | `nav-help` |
| `pages/Home.vue` | `section.card.brief`（AI 今日简报） | `home-brief` |
| `pages/Home.vue` | `section.kpis`（关键指标） | `home-kpis` |
| `pages/Home.vue` | `section.card.shop`（车间实况） | `home-shop` |
| `pages/Home.vue` | `section.card.orders`（订单与交期） | `home-orders` |
| `pages/Home.vue` | `section aria-label="质量"` | `home-quality` |
| `pages/Planner.vue` | `section.card.neworder`（新建订单） | `planner-neworder` |
| `pages/Planner.vue` | “客户”的 `div.field` | `planner-customer` |
| `pages/Planner.vue` | “产品”的 `div.field` | `planner-item` |
| `pages/Planner.vue` | “数量（台）”的 `div.field` | `planner-qty` |
| `pages/Planner.vue` | “算料”按钮 | `planner-calc` |
| `pages/Planner.vue` | `section.card.side`（提议） | `planner-proposals` |
| `pages/Planner.vue` | 工单 `section.card` | `planner-wos` |
| `pages/Operator.vue` | 工位 `div.tabs` | `op-units` |
| `pages/Operator.vue` | `div.now`（正在做的） | `op-now` |
| `pages/Operator.vue` | `h3` 派到本工位的工序 | `op-jobs` |
| `pages/Quality.vue` | `section.card.grow`（控制图） | `q-chart` |
| `pages/Quality.vue` | “质量异常单（8D）”的 `div.card-head` | `q-8d` |
| `pages/Quality.vue` | “问题情景（老师）”的 `div.card-head` | `q-problems` |
| `pages/ProcessPlan.vue` | “参照工艺规程”的 `div.card-head` | `pp-reference` |
| `pages/ProcessPlan.vue` | “上传工艺规程”的 `div.card-head` | `pp-upload` |
| `pages/Factory3D.vue` | `div.host`（三维画面） | `3d-scene` |
| `pages/Factory3D.vue` | `div.legend` | `3d-legend` |
| `pages/OntOps.vue` | 顶上 `span.tabs`（全厂态势 / 异常处理 / …） | `ont-tabs` |
| `pages/OntOps.vue` | 异常处理左栏 `section.card.list` | `ont-list` |
| `pages/OntOps.vue` | 中栏 `<ChainGraph …>` 标签上 | `ont-chain` |
| `pages/OntOps.vue` | 右栏 `section.card.right` | `ont-actions` |

那边的 `mgr-teacher`（Manager.vue 的教师控制台）这边没有 Manager 页，改用下面的 `dir-console`。
那边的 `cad-list`、`cad-production`、`acct-*`、`ai-model` 是企业功能，教学版不用。

### 新加的

| 页面文件 | 元素 | data-help |
| --- | --- | --- |
| `pages/Engineer.vue` | “在线设计 · 输出轴 SH-301”所在的 `section.card` | `eng-design` |
| `pages/Engineer.vue` | “发布新版本 / 提交审批”按钮 | `eng-publish` |
| `pages/Engineer.vue` | “设计版本”卡片 | `eng-versions` |
| `pages/Engineer.vue` | “进阶：用桌面 CAD 发布（选做）”卡片 | `eng-cad` |
| `pages/OntOps.vue` | 全厂态势的 `div.timebar`（时间栏） | `ont-timebar` |
| `pages/OntOps.vue` | 第一个 `div.maprow`（价值链那一排卡片；v-for 取第一个） | `ont-cards` |
| `pages/OntOps.vue` | `<OptionsPanel …>` 标签上（推演与建议） | `ont-options` |
| `pages/OntActions.vue` | 顶上 `span.tabs`（待我批准 / 我发起的 / 全部） | `act-boxes` |
| `pages/OntActions.vue` | 说明谁能批的那段 `p.small.muted` | `act-rules` |
| `pages/OntActions.vue` | 动作列表：`section.card.act`（v-for 取第一个；或给列表包一层 `div`） | `act-list` |
| `pages/CustomerService.vue` | `section.kpis` | `svc-kpis` |
| `pages/CustomerService.vue` | 顶上 `span.tabs` | `svc-tabs` |
| `pages/CustomerService.vue` | “登记投诉”卡片（`v-if="cp.can_edit"` 那个 `div.card`） | `svc-complaint` |
| `pages/Supply.vue` | `section.kpis` | `sup-kpis` |
| `pages/Supply.vue` | 顶上 `span.tabs` | `sup-tabs` |
| `pages/Supply.vue` | “到货与检验”标签里的批次表 `div.card` | `sup-inspect` |
| `pages/Finance.vue` | `section.kpis` | `fin-kpis` |
| `pages/Finance.vue` | 顶上 `span.tabs` | `fin-tabs` |
| `pages/Finance.vue` | “经营目标”标签的第一个 `div.card`（指标树） | `fin-objectives` |
| `pages/Finance.vue` | `<ProductionCost …>` 标签上（生产与成本） | `fin-production` |
| `pages/Maint.vue` | `section.kpis` | `maint-kpis` |
| `pages/Maint.vue` | 顶上 `span.tabs` | `maint-tabs` |
| `pages/Maint.vue` | 设备台账表所在的 `div.card` | `maint-assets` |
| `pages/Maint.vue` | “保养”标签里的保养单表（`table.tbl.card`） | `maint-pm` |
| `pages/Maint.vue` | “老师：车间可靠性”那一行（只给老师，教学版引导暂不用，留给以后老师版引导） | `maint-reliability` |
| `pages/People.vue` | `section.kpis` | `people-kpis` |
| `pages/People.vue` | 顶上 `span.tabs` | `people-tabs` |
| `pages/People.vue` | “排班”标签的 `div.card`（排班表） | `people-roster` |
| `pages/Ehs.vue` | `section.kpis` | `ehs-kpis` |
| `pages/Ehs.vue` | 顶上 `span.tabs` | `ehs-tabs` |
| `pages/Ehs.vue` | “随手拍”卡片 `div.card` | `ehs-report` |
| `pages/Energy.vue` | `section.kpis` | `energy-kpis` |
| `pages/Energy.vue` | “车间总表”卡片 `div.card` | `energy-curve` |
| `pages/Energy.vue` | “每台设备的电量（度）”卡片 `div.card` | `energy-units` |
| `pages/Labs.vue` | `div.grid`（实验卡片） | `labs-grid` |
| `pages/Lab15.vue`（建议 Lab16–Lab23 同样加，名字相同） | 顶上 `span.r`（指导书 · 报告模板） | `lab-links` |
| `pages/Lab15.vue`（同上） | `div.card.sum`（得分条、比对模式状态） | `lab-sum` |
| `pages/Lab15.vue`（同上） | 任务 `section.card.task`（v-for 取第一个） | `lab-task` |
| `pages/Director.vue` | `section.card.dbar`（倍速、开始、下一幕、快进、自动演示、复盘） | `dir-bar` |
| `pages/Director.vue` | `ol.timeline`（八幕） | `dir-timeline` |
| `pages/Director.vue` | `<TeacherConsole />` 标签上 | `dir-console` |

## 三、引导（并进 tours.json）

沿用那边、内容不变：`home-tour`、`open-3d`、`planner-release`、`operator-start`、`quality-chart`、`process-plan`、`ont-anomaly`。

那边有、这边要改的：

- `planner-order`：第二步文字“客户来自 ERPNext（企业工厂是工厂清单里登记的客户）”可以保留；演示厂产品只有 WQR-105，不用改。
- `teacher-console`：路径改为 `/director`，标记改为 `dir-console`（见下）。

教学版不用的：`cad-to-production`、`accounts`、`ai-model`（企业版有就留着）。

新加的（JSON 可以直接并进去）：

```json
{
  "teacher-console": {
    "title": "教师控制台",
    "path": "/director",
    "steps": [
      { "help": "dir-console", "text": "教师控制台在情景导演页最下面：仿真倍速、注入一次故障、车间班次、重置实验 7 情景。勾“同时清空学生得分”才清分。" }
    ]
  },
  "engineer-design": {
    "title": "在线设计并发布新版本",
    "path": "/work/engineer",
    "steps": [
      { "help": "eng-design", "text": "在线设计：改输出轴的轴段直径与长度、倒角、圆角、键槽，右边三维模型马上跟着变，下面是校核结果。" },
      { "help": "eng-publish", "text": "填改动说明，点“发布新版本”。校核没通过时按钮是灰的，看红字。生产模式这里是“提交审批”。" },
      { "help": "eng-versions", "text": "发布后这里多一个版本：STEP、零件图、键槽 G 代码，ERPNext 里的设计版本加一。" },
      { "help": "eng-cad", "text": "想用真 CAD：下载“我的 CAD 宏包”，在 FreeCAD 1.1 或 SolidWorks 里执行发布宏，效果相同。" }
    ]
  },
  "ont-situation": {
    "title": "看全厂态势",
    "path": "/ont",
    "steps": [
      { "help": "ont-tabs", "text": "厂情中枢的各个地方：全厂态势、异常处理、推演工作台、动作收件箱、全貌地图、规则目录、日报周报、AI 运行记录。" },
      { "help": "ont-timebar", "text": "时间栏：可以回看过去 7 天的任一时刻；回看时点“从这里推演”，试“如果当时那样做”。" },
      { "help": "ont-cards", "text": "每个领域一块卡片：关键指标、近 7 天小折线、开着的异常数（红严重、黄警告、蓝提示）。点卡片只看这个领域的异常。" }
    ]
  },
  "ont-options": {
    "title": "比较处理方案",
    "path": "/ont",
    "query": { "view": "anomalies" },
    "steps": [
      { "help": "ont-list", "text": "先在左边选一个异常。" },
      { "help": "ont-chain", "text": "中间是因果链：原因在上，影响在下。点一条边看依据。" },
      { "help": "ont-options", "text": "推演与建议：每个方案的预计交期、多花的钱。第一个标“建议”。比对模式下，提交自己的选择之前不显示建议。看好了点“采纳，生成动作”。" }
    ]
  },
  "ont-inbox": {
    "title": "动作收件箱",
    "path": "/ont/actions",
    "steps": [
      { "help": "act-boxes", "text": "待我批准、我发起的、全部。" },
      { "help": "act-rules", "text": "谁能批：花钱的动作要厂长批；不能批自己发起的。" },
      { "help": "act-list", "text": "每个动作有试运行结果（和“不处理”对比）。“批准并执行”以后，执行器发给车间、改班次表或在 ERPNext 建单据；情况变了先“用最新快照重新试运行”。" }
    ]
  },
  "service-tour": {
    "title": "登记一条投诉",
    "path": "/service",
    "query": { "tab": "complaints" },
    "steps": [
      { "help": "svc-kpis", "text": "上方五个数：满意度、开着的投诉、待上门的服务、保修成本、漏斗金额。" },
      { "help": "svc-tabs", "text": "五个标签：销售漏斗、投诉、服务与排班、回访与满意度、客户 360。" },
      { "help": "svc-complaint", "text": "填设备序列号（会带出客户）、现象、严重度，点“登记”，同时在 ERPNext 开投诉单。20 秒内厂情中枢开异常。要用“售后”角色。" }
    ]
  },
  "supply-inspect": {
    "title": "检验一批来料",
    "path": "/supply",
    "query": { "tab": "inspect" },
    "steps": [
      { "help": "sup-kpis", "text": "上方：在途、到货待检、不合格待处理、准时率 / 合格率、供应商模拟器。" },
      { "help": "sup-tabs", "text": "四个标签：采购单与在途、到货与检验、批次、供应商。" },
      { "help": "sup-inspect", "text": "到货待检的批次点“检验”，看抽样数据，逐件对照上下限，判合格或不合格。任何一件、任何一项超差，整批不合格。" }
    ]
  },
  "finance-tour": {
    "title": "看经营与财务",
    "path": "/finance",
    "steps": [
      { "help": "fin-kpis", "text": "上方五个数：毛利率、应收与逾期、应收周转天数、现金、本月预算已用。" },
      { "help": "fin-tabs", "text": "经营目标、订单毛利、应收应付、预算、生产与成本。" },
      { "help": "fin-objectives", "text": "经营目标的指标树：每个目标挂一个指标，数取自各领域的态势卡。绿达标、黄差一点、红偏离。" }
    ]
  },
  "finance-production": {
    "title": "看生产与成本",
    "path": "/finance",
    "query": { "tab": "production" },
    "steps": [
      { "help": "fin-tabs", "text": "原来的“经营与成本”页，现在是“经营与财务”的“生产与成本”标签。" },
      { "help": "fin-production", "text": "各设备今日 OEE、本月交付、工单成本分解：差异来自调整、换刀、超时。" }
    ]
  },
  "maint-tour": {
    "title": "看设备台账",
    "path": "/maint",
    "steps": [
      { "help": "maint-kpis", "text": "上方：保养逾期的设备、开着的维修单、近 7 天故障停机、平均故障间隔、点检异常待处理。" },
      { "help": "maint-tabs", "text": "四个标签：设备台账、保养、点检、维修与备件。" },
      { "help": "maint-assets", "text": "每台设备：自上次保养运行了多少小时、保养周期、未来一段运行时间内坏的概率、预期损失。点“详情”看失效率曲线。" }
    ]
  },
  "maint-pm": {
    "title": "保养单与验收解锁",
    "path": "/maint",
    "query": { "tab": "pm" },
    "steps": [
      { "help": "maint-tabs", "text": "保养在厂情中枢里排：保养逾期、故障风险高的异常，采纳“现在保养”或“下班后保养”，厂长批准后生成保养单。" },
      { "help": "maint-pm", "text": "到时间设备挂牌上锁停下。维修工做完点“保养完成”，另一个人点“验收解锁”，设备恢复。" }
    ]
  },
  "people-tour": {
    "title": "看排班",
    "path": "/people",
    "steps": [
      { "help": "people-kpis", "text": "上方：这一班出勤率、排班缺口、单点依赖的设备、本周加班、车间“要有人”开没开。" },
      { "help": "people-tabs", "text": "组织与员工、技能矩阵、排班、出勤与加班。" },
      { "help": "people-roster", "text": "每一格是这一班谁开这台设备。红：没人能开；黄：学徒带着开。点格子可以换人，生成调班动作。" }
    ]
  },
  "ehs-tour": {
    "title": "报一条隐患",
    "path": "/ehs",
    "steps": [
      { "help": "ehs-kpis", "text": "上方：开着的隐患（重大、逾期）、整改按期率、挂牌上锁的设备、培训到期、未遂。" },
      { "help": "ehs-tabs", "text": "隐患、作业许可、事故与未遂、培训与资质、化学品与废弃物。" },
      { "help": "ehs-report", "text": "随手拍：选设备、种类、等级，写一句话，拍照，提交。谁都能报。重大隐患在厂情中枢报“重大隐患未关闭”。" }
    ]
  },
  "energy-tour": {
    "title": "找空转最多的设备",
    "path": "/energy",
    "steps": [
      { "help": "energy-kpis", "text": "上方：用电、电费、峰时占比、空转电量、碳排放、需量。" },
      { "help": "energy-curve", "text": "车间总表：每 15 分钟的平均功率，红峰、黄平、蓝谷；虚线是合同需量。" },
      { "help": "energy-units", "text": "每台设备的电量条，灰色是空转。灰色多的设备，可以考虑自动待机。" }
    ]
  },
  "labs-tour": {
    "title": "打开实验与任务",
    "path": "/labs",
    "steps": [
      { "help": "labs-grid", "text": "实验 7、15–23 每个一张卡片：领域、学时、任务数、自动评的得分和报告分、做到第几个任务。点卡片进实验页，“指导书”直接下载。" }
    ]
  },
  "lab-page": {
    "title": "看一个实验页",
    "path": "/lab15",
    "steps": [
      { "help": "lab-links", "text": "先下载指导书和报告模板。" },
      { "help": "lab-sum", "text": "你的得分；黄色标签表示还在比对模式：提交选择之前，指挥台和 AI 不显示建议。" },
      { "help": "lab-task", "text": "任务一个一个做：读说明和提示，填表提交，马上给分和反馈。" }
    ]
  },
  "director-tour": {
    "title": "情景导演",
    "path": "/director",
    "steps": [
      { "help": "dir-bar", "text": "选倍速、要不要自动收尾，点“开始两周情景”；之后点“下一幕”。还有快进到订单做完、自动演示、复盘。" },
      { "help": "dir-timeline", "text": "八幕的时间线：每一幕的旁白、讲解要点、去看的页面、谁处理；厂情中枢报出异常后打勾。" },
      { "help": "dir-console", "text": "页面最下面是教师控制台：倍速、注入故障、车间班次、重置实验 7 情景。" }
    ]
  }
}
```

## 四、各章用到的引导

| 章 | 引导 |
| --- | --- |
| 01-start | open-3d |
| 02-dashboard | home-tour |
| 03-design-to-factory | engineer-design、process-plan |
| 04-planning | planner-order、planner-release |
| 05-workshop | operator-start、open-3d |
| 06-quality | quality-chart |
| 07-insight | ont-situation、ont-anomaly、ont-options、ont-inbox |
| 08-service | service-tour |
| 09-supply | supply-inspect |
| 10-finance | finance-tour、finance-production |
| 11-maint | maint-tour、maint-pm |
| 12-people | people-tour |
| 13-ehs | ehs-tour |
| 14-energy | energy-tour |
| 15-labs | labs-tour、lab-page |
| 16-director | director-tour、teacher-console |
| 17-course | labs-tour |
| 18-faq | — |
