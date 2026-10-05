// 实验 1.7 第一次在实验台上写程序（配 1.7 节）。三维虚拟上料输送线（第一篇篇首项目），I/O 与 1.1 节相同。
const plant = WQPLANTS.conveyor();
const START = [{ set: { S1_Start: true } }, { wait: 300 }, { set: { S1_Start: false } }];
// 参考程序（任务的示范做法用，自动试做时载入）：第 2 步的自锁 + 第 3 步的末端停
const SOL = { st: `PROGRAM Main
  KM1_Run := (S1_Start OR KM1_Run) AND S2_Stop AND S0_EStop AND F1_Overload AND NOT B2_End;
  H1_Run := KM1_Run;
  H2_Fault := NOT F1_Overload;
END_PROGRAM
` };
const LAMP = { st: `PROGRAM Main
  H1_Run := S1_Start;
  KM1_Run := S1_Start AND S2_Stop AND S0_EStop AND F1_Overload;
  H2_Fault := NOT F1_Overload;
END_PROGRAM
` };
WQ.lab({
  title: ["实验 1.7 第一次在实验台上写程序", "Lab 1.7 Your first program on the bench"],
  goal: ["在实验台上写、下载、运行第一个 PLC 程序：先让按钮点亮一盏灯，再让输送线自锁运行、到末端自动停，用自动测试检验。",
         "Write, download and run your first PLC program: a button lights a lamp, then the conveyor seals in and stops at the end; check it with the tests."],
  view: "plc",
  scenes: [{ id: "line", name: ["上料输送线", "Feed conveyor"],
    problem: { title: ["车间问题：把棒料送到锯床跟前", "Shop-floor problem: bring the bar to the saw"],
               text: ["按一下启动按钮 S1，输送线运转，松开按钮后继续运转；棒料到达末端光电开关 B2 时停下；按停止按钮 S2（常闭）、急停 S0（常闭）或电机过载（热继电器 F1 常闭触点断开）时立即停。",
                      "Press start S1 once and the belt runs on after release; it stops when the bar reaches end sensor B2; stop S2 (NC), the e-stop S0 (NC) or a motor overload (F1 NC contact opens) stop it at once."] } }],
  params: [],
  plc: {
    io: plant.io, lang: "ST", langs: ["ST", "LD"], cycle: 10,
    program: { st: `(* 实验 1.7：第一个程序。第 1 步：按住 S1 时绿灯 H1 亮 *)
PROGRAM Main
  H1_Run := FALSE;   (* 改成 H1_Run := S1_Start; 试试 *)
  KM1_Run := FALSE;
  H2_Fault := FALSE;
END_PROGRAM
` },
    watch: [],
    tests: [
      { id: "lamp", name: ["按住 S1 时 H1 亮，松开就灭", "H1 is on while S1 is held, off when released"],
        steps: [{ set: { S1_Start: true } }, { wait: 50 }, { expect: { H1_Run: true } }, { set: { S1_Start: false } }, { wait: 50 }, { expect: { H1_Run: false } }] },
      { id: "seal", name: ["按一下 S1 电机一直转，按 S2 停", "Press S1 once: the motor keeps running; S2 stops it"],
        steps: [...START, { wait: 1000 }, { expect: { KM1_Run: true } }, { set: { S2_Stop: false } }, { wait: 30 }, { expect: { KM1_Run: false } },
                { set: { S2_Stop: true } }, { never: { KM1_Run: true }, during: 500 }] },
      { id: "end", name: ["料到末端 B2 时电机自动停", "The motor stops when the bar reaches B2"],
        steps: [...START, { until: { B2_End: true }, within: 15000 }, { wait: 30 }, { expect: { KM1_Run: false } }] },
      { id: "safety", name: ["急停、过载时不能运转", "No running with the e-stop pressed or on overload"], faults: { overload: true },
        steps: [...START, { wait: 50 }, { expect: { KM1_Run: false } }] },
      { id: "estop", name: ["运行中按急停立即停，松开后不自行启动", "The e-stop stops the belt at once; releasing it does not restart"],
        steps: [...START, { wait: 1000 }, { expect: { KM1_Run: true } }, { set: { S0_EStop: false } }, { wait: 30 }, { expect: { KM1_Run: false } },
                { set: { S0_EStop: true } }, { never: { KM1_Run: true }, during: 500 }] },
    ],
  },
  plant,
  tasks: [
    { id: "lamp", test: "lamp", text: ["第 1 步：按住 S1 时运行灯 H1 亮、松开就灭（测试通过）。", "Step 1: H1 on while S1 is held (test passes)."], demo: { program: LAMP, tests: true } },
    { id: "seal", test: "seal", text: ["第 2 步：按一下 S1 电机一直转，按 S2 停（自锁，测试通过）。", "Step 2: press S1 once and the motor keeps running; S2 stops it (test passes)."], demo: { program: SOL, tests: true } },
    { id: "end", test: "end", text: ["第 3 步：料到末端 B2 自动停（测试通过）。", "Step 3: stop at the end sensor B2 (test passes)."], demo: { program: SOL, tests: true } },
    { id: "review", review: true, text: ["程序检查没有错误（急停、过载、停止都用到了）。", "The program check finds no errors (stop, e-stop and overload all used)."], demo: { program: SOL, review: true } },
  ],
  think: ["第 2 步的程序里，“OR KM1_Run”起什么作用？把它去掉，按一下 S1 会怎样？", "In step 2, what does 'OR KM1_Run' do? Remove it and press S1 once: what happens?"],
  readouts(api, s) {
    const x = s.parts && s.parts.length ? Math.max(...s.parts.map((p) => p.x)) : 0;
    return [[["棒料位置", "Bar position"], api.fmt(x, 2) + " m"], [["输送速度", "Belt speed"], api.fmt(s.v || 0, 2) + " m/s"],
            [["已送到锯床", "Delivered"], String(s.delivered || 0)]];
  },
});
