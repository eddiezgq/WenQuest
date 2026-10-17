# 实施细则 · 第 38 轮：WenQuest Ops 介绍视频

日期：2026-10-17
起因：Eddie：“再出一个视频介绍，说服中小企业老板，10 分钟左右，英文，中英字幕”；“用我的声音”；画面用“课件即画面（推荐）”，配音“英文配音，中英字幕（推荐）”；11:52“把这几页动画放到网页介绍最后，开始做视频介绍”。
状态：**已定（Eddie 12:04：“可以，片尾留我个人邮箱：eddiezgq@gmail.com”），施工中。**

## 一、决定

| 项 | 决定 |
| --- | --- |
| 观众 | 美国和国际中小企业（10–200 人）的老板 |
| 目的 | 说服对方来谈试点：一份连通的记录、AI 只起草、人来决定；从一个问题起步 |
| 长度 | 9–11 分钟，1920×1080，30 帧/秒 |
| 声音 | Eddie 本人声音，英文。工作流“Lecture videos 公开课视频”，`voice=clone`、`engine=cv2`（CosyVoice2，租 GPU，合成完关机） |
| 字幕 | 烧录在画面下方：英文在上、中文在下；另出一份同内容的 `字幕.srt` 备上传 |
| 画面 | 课件即画面：逐页录 1 小时讲座网页（55 页，深蓝底，带可操作的软件复制品和四张未来工厂白板）。配音讲到哪句，页面就点到哪一步 |
| 片头片尾 | 片头 = 讲座封面页；片尾 = 结束页，加试点邀请和联系方式 eddiezgq@gmail.com（讲座网页结束页同步改） |
| 计划中的功能 | 只用已做好的功能页；仓储配送、托管接口这两页（标 Planned）不进视频；未来工厂白板标“Vision” |
| 数字 | 只用网页里虚构演示企业 Harbor Lane Supply 的数字，并在画面上保留“Fictional demo”标记；不说节省多少钱、提高多少百分比这类没有依据的数 |

## 二、讲稿（英文配音 + 中文字幕）

每段对应讲座网页的一页；“→”是讲这句时页面上做的操作。英文约 1,350 词，按每分钟 140 词约 9.5 分钟，加上操作停顿约 10.5 分钟。

| # | 页 | 英文配音 | 中文字幕 | 页面操作 |
| --- | --- | --- | --- | --- |
| 1 | 1 封面 | I'm Eddie Zhang. In the next ten minutes I'll show you how a company of ten to two hundred people can run orders, stock, purchasing and quality from one record, with AI that drafts and people who decide. | 我是 Eddie Zhang。接下来十分钟，我给您看：一家十到两百人的公司，怎样用一份记录管好订单、库存、采购和质量；AI 起草，人来决定。 | 封面逐条出现 |
| 2 | 4 一个周二 | Let's start with a Tuesday. A customer asks about a late order. The facts exist: the order is in the ERP, the shortage is in a spreadsheet, the supplier's delay is in someone's inbox, and the failed inspection is on paper. Nobody can see the chain. So you spend the morning on the phone. | 先说一个周二。客户问一张迟到的订单。事实都在：订单在 ERP 里，缺料在表格里，供应商延期在某个人的邮箱里，检验不合格记在纸上。可没人看得见这条链。于是一上午都在打电话。 | 时间线逐条出现 |
| 3 | 5 散落的记录 | Every record lives in its own tool, owned by one person. We don't ask anyone to type things twice. We connect what you already have. | 每份记录都在各自的工具里，归一个人管。我们不让任何人重复录入，只把您已有的连起来。 | → 点 Connect |
| 4 | 6 审核周与 AI | Two more pains. Audit week, when evidence is hunted down at the last minute. And the new AI tools, which are fast, but nobody can check where their answers came from. | 还有两件头疼事：审核周，证据临时到处找；新的 AI 工具，快是快，可谁也查不了它的答案从哪来。 | 逐条出现 |
| 5 | 7 怎么搭的 | Here is the whole design. At the bottom, ERPNext, a mature open-source ERP, used as is. On top, our operations hub, which reads it, connects it, and checks it. | 整个设计就这样。最底下是 ERPNext，成熟的开源 ERP，原样使用。上面是我们的运营中枢：读它、连它、查它。 | 架构图逐层出现 |
| 6 | 8 AI 起草、人签字 | One rule runs through everything: AI drafts, people sign. Ask the AI for a report and it writes from your records, with citations. Ask it to sign, and it is refused. Every time. | 有一条规则贯穿始终：AI 起草，人签字。让 AI 写报告，它照您的记录写，并注明出处。让它签字？拒绝。每一次都拒绝。 | → 点“AI 起草”→ 点“让 AI 签字” |
| 7 | 11 ERP 是什么 | First, the base. An ERP is your single book of record: one list of items, customers and suppliers, and every transaction posted once. | 先说底座。ERP 是公司唯一的账本：一份物料、客户、供应商清单，每笔业务只记一次。 | → 点“发出货单 DN-0331” |
| 8 | 16 复式记账 | Ship one order and watch: stock goes down, cost of goods goes up, the books stay balanced. Your accountant and your warehouse finally read the same numbers. | 发一张货，您看：库存减少，销货成本增加，账始终平衡。会计和仓库终于看的是同一组数。 | → 依次过账 4、5、6 |
| 9 | 18 库存台账 | Stock is a ledger too. Every movement has a quantity and a value, and you can't ship what you don't have. | 库存也是一本账。每次进出都有数量和金额；没有的货，发不出去。 | → 收货、收货、发货 120 |
| 10 | 22 中枢加了什么 | The ERP records. Our hub connects, measures and explains: events become one graph of the business, metrics with published formulas, anomalies with their causes, and drafts a person confirms. | ERP 负责记录。我们的中枢负责连接、度量、解释：业务变动连成一张图，指标公式公开，异常附带原因，草稿由人确认。 | → 逐个点六个阶段 |
| 11 | 27 早晨看板 | This is the morning dashboard. Every tile is clickable. Late orders, stock-outs, quality holds, receivables, each one opens to the records behind it. | 这是每天早上的看板。每一格都能点：迟到订单、缺货、质量冻结、应收款，点开就是背后的记录。 | → 点“Late orders” |
| 12 | 28 追一张迟单 | Back to Tuesday. Click the late order and follow the chain: the item that's short, the purchase order that's late, the inspection that failed. What used to take a morning takes a minute. | 回到那个周二。点开迟到的订单，顺着链看：缺的物料、迟到的采购单、没通过的检验。过去要一上午，现在一分钟。 | → 点 SO-1042，沿链展开 |
| 13 | 29 草稿 | And the fix comes back as a draft: a purchase order, a note to the customer. Nothing reaches ERPNext until a person clicks confirm. | 解决办法以草稿回来：一张采购单、一封给客户的说明。人不点“确认”，什么也进不了 ERPNext。 | → 点草稿 → 点“确认” |
| 14 | 33 财务看板 | For you, the owner: what you invoiced this week, who owes you, what's overdue and from whom, and what you owe next. | 给老板看的：这周开了多少票，谁欠您钱，谁逾期了，接下来要付多少。 | → 点 Visitor mode |
| 15 | 37 体系健康 | Quality is where most small companies drown. Here, a standard like ISO 9001 or 13485 becomes checks that read your actual records every day. Green means today's records satisfy it. Red names the exact record that doesn't. | 质量是多数小公司最吃力的地方。在这里，ISO 9001、13485 这样的标准变成每天读取实际记录的检查。绿色：今天的记录满足要求；红色：直接指出是哪一条不满足。 | → 点红色格 |
| 16 | 38 不合格到纠正 | A nonconformance follows its workflow. Try to approve your own disposition: refused. Someone else must approve, and the history can only grow. | 不合格品按流程走。想自己批自己的处置？拒绝。必须另一个人批，记录只增不改。 | → 同一人批准被拒 |
| 17 | 39 来料检验 | At receiving, type a reading out of tolerance and it turns red at once. The verdict comes from code, not from the AI. | 来料检验时，输入一个超差读数，立刻变红。判定由程序给出，不由 AI 决定。 | → 输入 3.3 |
| 18 | 44 扫 UDI | For medical devices, scan the label: the device identifier, lot and expiry are read and checked, then traced to every shipment. | 医疗器械扫一下标签：器械标识、批号、有效期读出并校验，再追到每一次发货。 | → 点示例码 |
| 19 | 46 测量文件 | Measuring machines send their files straight in. Each reading lands on the right part and feature, and a person accepts it. | 测量设备的文件直接导入。每个读数落到对应的零件和项目上，由人接收。 | → 改 CSV，看预览 |
| 20 | 51 未来工厂 | And this is where it leads: a factory where warehouse, robots, vision inspection and every gauge feed one hub, | 这就是它通向的地方：仓库、机器人、视觉质检、每一件量具，都汇入同一个中枢， | 白板动画播放（无声） |
| 21 | 54 闭环 | and the loop closes with a person approving at the key step. That's a vision, and every step toward it runs on the same record. | 闭环里，关键一步由人确认。这是愿景；而通往它的每一步，都跑在同一份记录上。 | 白板动画播放（无声） |
| 22 | 10 归您所有 | It's yours to run. The platform runs on a server you control. Your data stays yours. We teach your people, and we offer hosted connections when you need them. | 平台归您自己运行：装在您掌控的服务器上，数据归您。我们教会您的人，需要时提供托管接口服务。 | 逐条出现 |
| 23 | 50 起步 | Don't switch everything at once. Import your data, put one module live, usually incoming inspection or nonconformance, then grow. | 不用一次全换。先导入数据，上线一个模块，通常是来料检验或不合格品，再一步步扩。 | 四步逐个出现 |
| 24 | 55 结束 | One record. AI drafts. People decide. We're inviting a small number of pilot companies. If that Tuesday sounded familiar, let's talk. | 一份记录，AI 起草，人来决定。我们正在邀请少数试点企业。如果那个周二听着耳熟，我们聊聊。 | 联系方式（待给） |

## 三、做法

1. **课件进仓库**：讲座网页（`index.html` + `wb/future-factory-en.html`）复制到 `docs/课程视频/WenQuestOps介绍/课件/`；讲稿写成 `docs/课程视频/WenQuestOps介绍/讲稿.yaml`，每段：`page`（页号）、`say.en`、`say.zh`（只作字幕）、`steps`（每句前的页面操作：`next` 出下一条，`js` 点按钮）。
2. **新增镜头类型 `page`**（`tools/video/script.py`、`make.py`、`labrec.py`）：打开外部网页课件，用 `__deck.go(页, 0)` 翻页，按句子做操作，虚拟时钟逐帧录（同现有实验录屏）；白板页每帧把白板跳到对应时刻（白板自己的声音关掉）。讲稿没有 `book`/`section` 时按“独立视频”处理：不出教材封面、作业页，片头片尾就是课件第一页和最后一页。
3. **字幕**：英文版烧录时英文在上、中文在下（新加 `--subs en+zh`）；`字幕.srt` 一起交付。
4. **配音**：`clone.py lectures` 读同一份讲稿的英文句子；先本地用 Kokoro 占位声音出整片样片，核对节奏和每页操作，再在 GitHub Actions 跑 `voice=clone, engine=cv2, lang=en` 出正式版。
5. **安全**：样音只在工作流里用 `VOICE_KEY` 解密，用完即删；解密后的录音不进仓库、不上传任何公开地方；合成好的配音只在工作流的临时目录和本次运行的产物里。

## 四、施工顺序与验收

| 步 | 内容 | 验收 |
| --- | --- | --- |
| 1 | 课件和讲稿进仓库；`page` 镜头、独立视频、双语字幕 | `services/gateway` 和 `tools/video` 测试通过；本地出一页样片，操作和句子对得上 |
| 2 | Kokoro 占位声音出整片样片 | 9–11 分钟；每页操作都在画面里完成；字幕不出框、不挡操作 |
| 3 | Actions 用 Eddie 的声音出正式版 | 声音是 Eddie 本人；字幕与配音同步；片尾联系方式是 Eddie 给的 |
| 4 | Eddie 看片 | 按意见改讲稿或画面，重出改动的部分 |
| 5 | 帮助文件 | `tools/video/README.md` 加“独立视频（外部网页课件）”一节 |

## 五、施工中的偏差（已按规矩写回）

1. **长度**：第二节的 24 段实际只有约 700 个英文词（约 6 分钟），达不到 9–11 分钟。按同样的内容加了 9 段，取自讲座网页已有的页：ERPNext 模块（13）、批号与补货（20）、指标公式（25）、助手（30）、控制图（40）、追溯与召回（43）、设备收件箱（47）、两张未来工厂白板（52、53）；并给开场加一句“画面是可操作的复制品、企业是虚构的”。共 33 段，约 1,000 词。逐句定稿在 `docs/课程视频/WenQuestOps介绍/讲稿.yaml`。
2. **工作流**：原来运行记录和预览一律推到 main。从本分支运行时会把未合并的代码一起推进 main（并触发上线），所以改成推回运行所在的分支；从 main 运行时不变。
3. **财务看板**不点“访客模式”（那是给访客隐藏金额用的，和老板看账的旁白不符）。

## 六、验收记录（2026-10-17）

| 步 | 结果 |
| --- | --- |
| 1 | 33 段每步操作先用无头浏览器逐页试点，全部通过；本机录 3 段核对 |
| 2 | Kokoro 占位声音整片 7:01；据此加“每步后停 1.2 秒”，录制时隐藏白板播放条，去掉课件里“价格待定”的占位句 |
| 3 | 工作流 run 39051167121（分支 `p38/ops-intro-video`，`voice=clone, engine=cv2, lang=en`）：声音合成成功，成片 **11:15**，1920×1080；字幕英文在上、中文在下；片尾联系方式 eddiezgq@gmail.com。下载页：https://github.com/eddiezgq/WenQuest/releases/tag/lecture-video-39051167121 |
| 4 | Eddie 13:58 看片意见，见第七节 |
| 5 | `tools/video/README.md` 已加“独立视频：外部网页课件”一节 |

## 七、Eddie 看片意见（13:58）与修改

意见：“镜头每次切换都在抖……应该加上漂亮的切换效果，语音有不连贯和不清楚的地方”“为什么不讲 dashboard”“中枢是没有实现吗”。

| 意见 | 原因 | 改法 |
| --- | --- | --- |
| 切换时抖 | 每个镜头开头，课件自带的翻页动画（横移加旋转）又播了一遍 | 录制时关掉课件翻页动画；镜头之间用 0.6 秒转场：同一部分内平滑推移，换部分时经暗场淡入（`make.py` 的 `XFADE`），转场落在镜头开头的静音里，不压配音 |
| 语音不连贯、不清楚 | 不少句子被切成半句分开合成（如 “At incoming inspection,”），语调断开；ERPNext、ISO 编号等读不准；合成本身有随机性 | 讲稿每行改成完整短句；ERPNext、ERP、AI、ISO 9001、13485 写成读法（“[字幕|读法]”）；GPU 上每句合成后用 Whisper 听写核对，听不清的最多重合成 3 次、留最好的一遍，运行日志列出仍不清的句子 |
| 不讲 dashboard | 看板只有一段约 15 秒 | 新增“中枢与看板”一部分：中枢已做好在运行（同步、对象图、指标、追因、草稿、助手）、对象图点击、车间大屏（26 页）、早晨看板逐项讲六个指标再点进去（27 页）、指标公式、追迟单、草稿、助手 |
| 中枢没实现？ | 原片只用一张流程图讲中枢 | 旁白明说“已做好、在运行”，并用对象图和看板演示（wenquest-ops 仓库 `wqops/hub/sync.py`、`ont/`、`drafts.py`、`ai/`、`Dashboard.vue`、`Wall.vue` 均已合并） |

另：测量文件一页（46）去掉，设备收件箱一页已讲同样的事，控制总长。讲稿 33 段。

## 八、第三版（Eddie 15:07：“能不能把语速增加三倍，信息量也增加三倍”）

真提到 3 倍语速（每分钟约 450 词）听不清，克隆声音也会变形。Eddie 选定（15:07 问答）：**语速 1.3 倍、空白全压缩；约 15 分钟，信息量约 3 倍。**

| 项 | 做法 |
| --- | --- |
| 语速 | 讲稿 `pace.speed: 1.3`：克隆声音在 GPU 上按 1.3 倍合成（模型不收 speed 参数时改用 ffmpeg 变速不变调）；Kokoro 样片同样 1.3 倍 |
| 空白 | 镜头开头 0.45 秒、句间 0.12 秒、每步后 0.25 秒、结尾 0.45 秒，转场 0.4 秒（原为 0.6 / 0.38 / 0.9 / 0.9 / 0.6） |
| 信息量 | 讲稿从 33 段约 1,050 词扩到 51 段约 2,300 词，覆盖讲座网页 55 页中的 51 页：加了四条规则、为什么选 ERPNext、订单到收款、采购到付款、报表与月结、计价方法、生产与其他模块、同步演示、销售与采购看板、仓储（标明计划中）、标准变流程、文件由 AI 分类、生产记录、搬家导入、测量文件、给工程师 |
| 用词 | 旁白不说“第几部分”，以免和课件页上的编号对不上 |
