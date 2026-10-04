# 贯通项目：从晶体管到芯片 · Capstone: from transistor to chip

为机器人关节设计一块电机控制芯片的数字部分（PWM 发生器 + 正交编码器计数器），四步做完，交出一份可以报名开源共享流片（Tiny Tapeout，SKY130 工艺）的芯片版图。每一步的做法、要求和报告写法见对应的实验指导书。

Design the digital part of a motor-control chip for a robot joint (PWM generator + quadrature encoder counter) in four steps, ending with a layout ready for a shared open-source tapeout (Tiny Tapeout, SKY130). The lab guides give the details for each step.

| 步 Step | 目录 Folder | 你要完成的 What you complete | 检查命令 Check |
|---|---|---|---|
| 一 器件 Device | `step1_device/` | `device_curves.py` 里的 `extract()`：VT、IDSAT、IOFF、亚阈值摆幅 | `wqlab device --script step1_device/device_curves.py --out step1_device/out` |
| 二 单元 Cell | `step2_nand2/` | 原理图网表 `nand2_schematic.spice`；在 `nand2.mag` 里画连线（四个管子已放好） | `wqlab nand2 --check step2_nand2 --schematic step2_nand2/nand2_schematic.spice` |
| 三 模块 Module | `step3_rtl/` | `src/pwm_gen.v`、`src/quad_dec.v`；`test/test_motor.py` 里的五个测试 | `wqlab test step3_rtl` |
| 四 芯片 Chip | `step4_chip/` | 按需要调整 `config.json`（时钟、密度），修正违例，写设计报告 | `wqlab tt step3_rtl --config step4_chip/config.json --out step4_chip/run` |

所有标着“在这里完成 / TODO”的地方由你完成；端口、文件名、结果的键名不要改，自动检查和报告回填按它们取数。

Fill in every place marked “在这里完成 / TODO”. Keep the port names, file names and result keys: the checks and the report read them.

画版图时只保存顶层单元（Magic 菜单 File → Save，或命令 `save nand2`），不要用 `writeall` 把四个管子的单元一起改写。

When drawing the layout, save only the top cell (File → Save, or `save nand2`); do not `writeall` the transistor cells.
