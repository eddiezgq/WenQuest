// 实验 2.3 继电器电路仿真：电动机正反转（配 2.3 节）。三维虚拟正反转电动机：接触器有吸合时间（20 ms）、释放时间（12 ms）
// 和主触点电弧（0–10 ms），辅助触点与主触点机械联动；两个接触器的主触点同时导通就是 L1、L3 相间短路，断路器 Q1 跳闸。
// 梯形图的一级就是电路图里的一条电流通路（2.5 节）；扫描周期取 1 ms，近似继电器电路里各支路同时动作。
const plant = WQPLANTS.reversing();
const F = [{ set: { S1_Fwd: true } }, { wait: 300 }, { set: { S1_Fwd: false } }];
const R = [{ set: { S3_Rev: true } }, { wait: 300 }, { set: { S3_Rev: false } }];
const STOP = [{ set: { S2_Stop: false } }, { wait: 300 }, { set: { S2_Stop: true } }];
const C = (k, v) => ({ k, v });
// 起始程序：正转一级已经画好（还没有互锁），反转一级由学生画
const START = [
  { comment: ["正转：S1 启动，KM1 辅助触点自锁，S2 停止，F1 过载", "Forward: S1 starts, KM1 seals in, S2 stops, F1 overload"],
    cells: [[C("NO", "S1_Fwd"), C("NO", "S2_Stop"), C("NO", "F1_Overload"), C("WIRE"), C("WIRE"), C("COIL", "KM1_Fwd")],
            [C("NO", "KM1_Aux"), null, null, null, null, null]],
    links: [[0, 1]] },
  { comment: ["反转：照正转画（S3、KM2）", "Reverse: draw it like the forward rung (S3, KM2)"],
    cells: [[null, null, null, null, null, null], [null, null, null, null, null, null]], links: [] },
];
// 参考程序（任务的示范做法用，自动试做时载入）：程序 2.3.1（双重互锁）；NONE：拆掉全部互锁
const SOL = { st: `PROGRAM Main
  KM1_Fwd := (S1_Fwd OR KM1_Aux) AND NOT S3_Rev AND NOT KM2_Aux AND S2_Stop AND F1_Overload;
  KM2_Rev := (S3_Rev OR KM2_Aux) AND NOT S1_Fwd AND NOT KM1_Aux AND S2_Stop AND F1_Overload;
END_PROGRAM
` };
const NONE = { st: `PROGRAM Main
  KM1_Fwd := (S1_Fwd OR KM1_Aux) AND S2_Stop AND F1_Overload;
  KM2_Rev := (S3_Rev OR KM2_Aux) AND S2_Stop AND F1_Overload;
END_PROGRAM
` };
WQ.lab({
  title: ["实验 2.3 继电器电路仿真：电动机正反转", "Lab 2.3 Relay circuit simulation: a reversing motor"],
  goal: ["把正反转控制电路画成梯形图，在虚拟电动机上运行；先不加互锁，看两个接触器同时吸合的后果，再加上按钮互锁和接触器互锁，用测试证明它在换向、两个按钮同时按、主触点熔焊时都不会短路。",
         "Draw the reversing control circuit as a ladder diagram and run it on the virtual motor; first without interlocks, to see what happens when both contactors close, then with button and contactor interlocks, proving with tests that reversing, pressing both buttons and a welded contact never short-circuit the supply."],
  view: "plc",
  scenes: [{ id: "motor", name: ["正反转电动机", "Reversing motor"],
    problem: { title: ["车间问题：输送线要能退料", "Shop-floor problem: the conveyor must run backwards"],
               text: ["上料输送线卡料时要能反转退料。按 S1 正转、按 S3 反转、按 S2 停止；热继电器 F1 动作时停。两个接触器无论怎样操作都不许同时吸合。",
                      "When the feed conveyor jams it must run backwards. S1 forward, S3 reverse, S2 stop; F1 stops it on overload. Whatever the operator does, the two contactors must never close together."] } }],
  params: [],
  plc: {
    io: plant.io, lang: "LD", langs: ["LD", "ST"], cycle: 1,
    program: { decls: "", ladder: START },
    watch: [],
    tests: [
      { id: "fwd", name: ["按 S1 正转并自锁", "S1: forward, sealed in"], steps: [...F, { wait: 3000 }, { expect: { KM1_Closed: true, KM2_Closed: false } }] },
      { id: "stop", name: ["按 S2 停，松开后不再自己启动", "S2 stops; no restart after release"],
        steps: [...F, { wait: 3000 }, { set: { S2_Stop: false } }, { wait: 40 }, { expect: { KM1_Closed: false } }, { set: { S2_Stop: true } }, { never: { KM1_Fwd: true }, during: 1000 }] },
      { id: "rev", name: ["停下后按 S3 反转", "S3 after a stop: reverse"], steps: [...F, { wait: 3000 }, ...STOP, { wait: 3000 }, ...R, { wait: 3000 }, { expect: { KM2_Closed: true, short: false } }] },
      { id: "direct", name: ["正转时直接按 S3：换向，不短路", "S3 while running forward: reverses, no short"],
        steps: [...F, { wait: 3000 }, ...R, { wait: 3000 }, { expect: { KM2_Closed: true, KM1_Closed: false, short: false } }] },
      { id: "both", name: ["S1、S3 同时按：都不吸合", "S1 and S3 together: neither closes"],
        steps: [{ set: { S1_Fwd: true, S3_Rev: true } }, { wait: 500 }, { set: { S1_Fwd: false, S3_Rev: false } }, { wait: 500 }, { expect: { KM1_Closed: false, KM2_Closed: false, short: false } }] },
      { id: "weld", name: ["KM1 主触点熔焊后按 S3：不短路", "KM1 welded, S3 pressed: no short"], faults: { weld1: true },   // KM1 welds on its second closing
        steps: [...F, { wait: 2000 }, ...STOP, { wait: 2000 }, ...R, { wait: 2000 }, { expect: { KM2_Closed: true } },
                ...STOP, { wait: 2000 }, ...F, { wait: 2000 }, ...R, { wait: 2000 }, { expect: { KM1_Closed: true, KM2_Closed: false, short: false } }] },
      { id: "overload", name: ["负载卡住：热继电器动作，电动机停", "Load jammed: F1 trips, the motor stops"], faults: { heavy: true },
        steps: [...F, { until: { tripped: true }, within: 20000 }, { wait: 40 }, { expect: { KM1_Closed: false } }] },
    ],
  },
  plant,
  tasks: [
    { id: "fwd", test: "fwd", text: ["第 1 步：运行起始程序，按 S1 正转、按 S2 停（测试“按 S1 正转”通过）。", "Step 1: run the starting program; S1 forward, S2 stop (test passes)."], demo: { program: SOL, tests: true } },
    { id: "rev", test: "rev", text: ["第 2 步：画出反转一级，停下后按 S3 能反转（测试通过）。", "Step 2: draw the reverse rung; S3 after a stop reverses (test passes)."], demo: { program: SOL, tests: true } },
    { id: "short", text: ["第 3 步：不加互锁，正转时按 S3（或同时按 S1、S3），看断路器 Q1 跳闸；按“重新合上断路器 Q1”恢复。", "Step 3: without interlocks, press S3 while running forward (or S1 and S3 together) and watch Q1 trip; close Q1 again."],
      demo: { program: NONE, panel: { S1_Fwd: true, S3_Rev: true }, run: true, wait: 4 } },   // both held (no release: a busy machine may not have scanned yet)
    { id: "interlock", test: "direct", text: ["第 4 步：加上按钮互锁和接触器互锁，正转时直接按 S3 能换向而不短路（测试通过）。", "Step 4: add button and contactor interlocks; S3 while running forward reverses without a short (test passes)."], demo: { program: SOL, tests: true } },
    { id: "weld", test: "weld", text: ["第 5 步：注入“KM1 主触点熔焊”（第二次吸合时粘住），正转、停、再正转以后按 S3，也不短路（测试通过）。", "Step 5: inject “KM1 welds” (it sticks on the second closing); forward, stop, forward again, then S3: no short (test passes)."], demo: { program: SOL, tests: true } },
    { id: "review", review: true, text: ["程序检查没有错误。", "The program check finds no errors."], demo: { program: SOL, review: true } },
  ],
  check(api, s) {   // 不加互锁时 Q1 跳过闸：学生看到了相间短路
    if (s.shorts > 0) api.done("short");
  },
  think: ["只有按钮互锁、没有接触器互锁时，正转中直接按 S3 有时短路、有时不短路。为什么？什么情况下一定短路？",
          "With the button interlock alone, pressing S3 while running forward sometimes shorts and sometimes does not. Why? When does it always short?"],
  readouts(api, s) {
    const m = s.m || { w: 0, I: 0 };
    return [[["转速", "Speed"], api.fmt(m.w * 1500, 0) + " r/min"], [["电流", "Current"], api.fmt(m.I * 1.9, 1) + " A"],
            [["断路器 Q1", "Breaker Q1"], s.blown ? "跳闸 / tripped" : "合 / closed"], [["热继电器 F1", "Overload F1"], m.tripped ? "动作 / tripped" : "正常 / ok"]];
  },
});
