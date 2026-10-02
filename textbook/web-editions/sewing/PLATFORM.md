# 共用设定：问渠缝制电控原型平台 WQ-SC 与零件库（第 19–22、27 章必须一致）

第 19 章定义，第 20–22 章和第 27 章引用。数值都是**示意/算例值**，不写任何具体厂商的型号；需要引用公开标准或资料时只引用你确实知道存在的。

## 1. 平台名与总体
- 名称：**问渠缝制电控原型平台 WQ-SC**（Sewing Control），英文 WenQuest Sewing-Control prototyping platform (WQ-SC)。
- 目标：用同一套“主控 + 模块 + 固件框架 + 测试台”，依照本书第 3–18 章的原理，搭出四种电控原型：**平缝机 WQ-SC/LS、包缝机 WQ-SC/OL、电子花样机 WQ-SC/PS、缩比电脑横机 WQ-SC/FK**；原型通过自动化测试一轮轮迭代，逐步达到工业级。
- 机械部分：平缝机、包缝机原型用**现成的机械机头**（拆掉离合器电机，或用已有直驱机头的机械部分）改装；花样机原型自制 X–Y 平台（零件库里的滚珠丝杠、直线导轨、同步带轮）装一个平缝机头；横机原型是自制的**缩比样机**（如 60 针、单系统、单针床或双针床，针距 E5–E7 级粗针），机械件尽量用零件库的标准件。

## 2. 参考架构（四种机器共用）
层次（自下而上）：
1. **执行与传感层**：主轴伺服电机 + 增量编码器（2500 线，四倍频 10000 计数/转，带 Z 相）；闭环步进电机（送布、X–Y、度目、牵拉）；推拉式电磁铁（剪线、拨线、倒缝、抬压脚、选针器）；气缸 + 电磁阀（压框、压脚、吹气）；霍尔脚踏传感器、光电传感器（布边、断线）、接近开关（原点、限位）、电流与温度检测。
2. **驱动层**：伺服驱动器（速度/转矩模式，经 CAN FD 或 RS-485 接主控）；步进驱动器（脉冲/方向或总线）；电磁铁驱动板（低边 MOSFET、强激磁 + 斩波维持、稳压管续流，第 13 章）；气阀驱动。
3. **实时控制层**：主控板 **WQ-SC 主控**：Cortex-M4F 级 MCU（170 MHz 量级，带编码器接口定时器、高分辨率 PWM、CAN FD），跑 RTOS；角度中断与控制环。横机选针可选一块小 FPGA 做逐针时序（第 17 章 FPGA 实验）。
4. **人机与联网层**：网关模块（Wi-Fi/以太网，跑 MQTT 客户端和网页参数界面），7 英寸触摸屏可选。
5. **数字工厂接口**：设备消息按问渠数字工厂的主题和信封格式上总线：`wq/<工厂>/<区域>/<单元>/<类别>`，类别沿用 status / event / measurement / alert / cmd 等（见仓库 factory/digital/wqbus/topics.py，第 26、27 章）。缝纫机厂示例根主题 `wq/sewing`，服装厂示例 `wq/garment`。

## 3. 固件框架（第 19 章讲，第 20、21 章用）
- 时间基准：**主轴转角**（平缝、包缝、花样机）或**机头位置**（横机），不是时间。编码器计数换算成 0.1° 分辨率的角度；每过一个整角度刻度（或用比较器在指定计数触发）检查**事件表**。
- **事件表**：一行一个动作 `(起始角, 结束角, 动作, 条件)`，例如剪线电磁铁在 205°–330° 通电、拨线在 15°–60°；表在参数里，可以改，不用改代码。
- **状态机**：IDLE → RUN（脚踏调速）→ SLOW（减速到剪线速度）→ TRIM（执行剪线事件）→ POSITION（停到上针位）→ IDLE；任一状态遇到 FAULT（过流、编码器丢失、超时、急停）都进 SAFE（断电磁铁、主轴自由停或制动）。
- 控制环：电流环在驱动器里（≈10–20 kHz），速度环 1–2 kHz，位置环 1 kHz；X–Y 插补周期 1 ms。
- **硬件抽象层 HAL**：每类模块一个接口（`spindle_*`、`stepper_*`、`sol_*`、`io_*`），换模块只改驱动文件；这正是“零件库快速配套”能落地的前提。
- 参数表、故障码、日志都有版本号；固件版本号和参数版本号随每台原型上报到数字工厂。

## 4. 零件库：已有条目与建议新增条目
问渠零件与机器人库（仓库 `library/`）目前分四部分：A 标准件（如 A-BRG-DG 深沟球轴承、A-BSC-SFU 滚珠丝杠、A-LGD-RAIL 直线导轨、A-PUL-HTD 同步带轮、A-CPL-JAW 梅花联轴器、A-SPR-CMP 压缩弹簧、A-KEY-FLAT 平键、A-SCR-SHC 内六角螺钉）；B 机器人整机；C 机构（C-CAM-DISC 盘形凸轮、C-LNK-SLIDER 曲柄滑块、C-LNK-4BAR 四杆、C-BLT-BELT 带传动、C-SCN-LEAD 丝杠、C-GER-TRAIN 齿轮系、C-RED-WQR105 减速器）；D 厂商器件（目前是机器人用的执行器、传感器，如 D-ACT-ROBOTIS-X、D-LDR-SICK-TIM）。每个条目有 entry.yaml（身份、参数定义：每个参数有 key、中英文名、role=perf/dim、单位）和 specs.csv 规格表；有“AI 选型”只从库里挑、答案注明条目编号和规格，库里没有就说没有。

**缝制电控模块目前还不在库里。**本书给出建议编号，一律写“建议编号，计划入库”，不要写成已有：
| 建议编号 | 名称 | 关键参数（key） |
|---|---|---|
| D-MOT-PMSM | 交流永磁同步伺服电机 | rated_power_W, rated_speed_rpm, max_speed_rpm, rated_torque_Nm, peak_torque_Nm, rotor_inertia_kgm2, encoder_ppr |
| D-DRV-SERVO | 伺服驱动器 | supply_V, cont_current_A, peak_current_A, bus (CAN FD / RS-485), modes |
| D-MOT-STEP | 混合式步进电机（含闭环型） | frame (NEMA 17/23/34), holding_torque_Nm, rotor_inertia_kgm2, rated_current_A, closed_loop (bool) |
| D-DRV-STEP | 步进驱动器 | supply_V, current_A, microstep, interface |
| D-SOL-PUSH | 推拉式电磁铁 | stroke_mm, force_at_stroke_N, coil_R_ohm, duty_pct |
| D-DRV-SOL | 电磁铁驱动板 | channels, boost_V, hold_A, clamp_V |
| D-ENC-INC | 增量编码器 | ppr, index (bool), max_rpm, output (TTL/差分) |
| D-SNS-HALL | 霍尔脚踏传感器 | range_mm, output_V |
| D-SNS-PE | 光电传感器（布边/断线） | range_mm, response_ms |
| D-SNS-PROX | 接近开关 | range_mm, type |
| D-CTL-WQSC | WQ-SC 主控板 | cpu, encoder_inputs, pwm_ch, can_fd, di, do, ai |
| D-IO-EXP | CAN FD 扩展 I/O 板 | di, do, ai |
| D-GW-WQSC | 网关模块（MQTT/网页） | net, protocols |
| D-PSU-SMPS | 开关电源 | V_out, P_W |
| D-PNU-CYL / D-PNU-VLV | 气缸 / 电磁阀 | bore_mm, stroke_mm / ports, V |
| D-HMI-PANEL | 触摸屏 | size_in, interface |
机械件优先引用**已有**条目（A-BSC-SFU、A-LGD-RAIL、A-PUL-HTD、C-BLT-BELT、A-CPL-JAW、A-BRG-DG、C-CAM-DISC 等）。

## 5. 快速配套流程（第 19 章讲，第 20–22 章用）
需求表（机种、最高转速、针距、负载惯量、动作清单、I/O、电源）→ 计算（主轴转矩与惯量匹配、加速时间；步进转矩–转速裕量；电磁铁吸合/释放折算转角，第 13 章；电源功率预算；I/O 计数）→ 从零件库按参数筛选 → 自动生成 BOM、接线表（I/O 映射）、固件配置（HAL 驱动选择、事件表初值）→ 上测试台验证 → 迭代。

## 6. 测试（第 22 章讲，第 20、21 章各留一节“验收测试”引用它）
- 测试金字塔：单元测试（固件函数，主机上跑）→ 软件在环 SIL（固件 + 本书虚拟实验同款的机器模型）→ 硬件在环 HIL（真主控板 + 仿真的电机/编码器/电磁铁负载）→ 整机测试台（真机头 + 测功/传感 + 相机看线迹）→ 出厂测试 EOL。
- 统一的测试脚本：Python + pytest，通过网关的 API/MQTT 下发命令、读测量；每个测试用例对应一条需求（需求编号 REQ-…），结果自动写成报告，并按数字工厂格式发到 `.../measurement` 主题，进历史库。
- 关键验收指标（示意，第 20–22 章用同一组）：停针定位误差 ≤ ±1°（主轴角，上针位）；剪线成功率 ≥ 99.5%（1000 次）；回针对齐偏差 ≤ 0.3 mm；电磁铁吸合/释放折算转角 ≤ 20°；最高转速下连续运转 4 h 温升与故障；X–Y 跟随误差 ≤ 0.05 mm，针在布中时位移为 0；横机选针时序误差 ≤ 0.1 针距对应的机头位移。
- 成熟度：原型 P0（能动）→ P1（功能全）→ EVT 工程验证 → DVT 设计验证（EMC、可靠性、环境，第 18 章）→ PVT 小批验证 → 量产。每一级的进入/退出条件用自动测试的通过率和指标衡量。
