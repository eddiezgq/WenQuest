// A PLC lab (第 18 轮 〔PLC〕〔VP〕〔TST〕): conveyor with start/stop, seal-in and a jam alarm.
// Technique example for PLC labs: io table, starting program, plant model (reset/inputs/step/panel/faults), tests.
WQ.lab({
  title: ["实验 8.1 输送线的启停与自锁", "Lab 8.1 Starting and stopping a conveyor"],
  goal: ["用梯形图或结构化文本写输送线的启停、自锁与堵料报警，先手动试，再跑自动测试。",
         "Write start/stop, seal-in and a jam alarm for a conveyor in ladder or ST; try it by hand, then run the tests."],
  view: "plc",
  scenes: [{ id: "line", name: ["上料输送线", "Feed conveyor"],
    problem: { title: ["车间问题：工件到头了，输送线还在转", "Shop-floor problem: the part is at the end and the belt still runs"],
               text: ["按启动后输送线把工件送到末端光电开关 B2 处停下；按停止（常闭按钮）或急停立即停；电机运行 6 s 还没到末端判为堵料，红灯亮。",
                      "Start runs the belt until the part reaches end sensor B2; Stop (an NC button) or the e-stop stops it at once; if the motor runs 6 s without the part arriving, it is a jam and the red lamp comes on."] } }],
  params: [],
  plc: {
    lang: "LD", cycle: 10, filter: 0,
    io: [
      { name: "S1_Start", addr: "%IX0.0", dir: "in", comment: ["启动按钮（常开）", "Start button (NO)"] },
      { name: "S2_Stop", addr: "%IX0.1", dir: "in", comment: ["停止按钮（常闭）", "Stop button (NC)"] },
      { name: "B2_End", addr: "%IX0.2", dir: "in", comment: ["末端光电开关", "End photo sensor"] },
      { name: "M1_Run", addr: "%QX0.0", dir: "out", comment: ["输送电机接触器 KM1", "Conveyor contactor KM1"] },
      { name: "H1_Jam", addr: "%QX0.1", dir: "out", comment: ["堵料红灯", "Jam lamp (red)"] },
    ],
    program: {
      decls: "VAR\n  tJam : TON;\nEND_VAR",
      ladder: [
        { comment: ["启停与自锁：到末端自动停", "Start/stop with seal-in; stop at the end"],
          cells: [[{ k: "NO", v: "S1_Start" }, { k: "NO", v: "S2_Stop" }, { k: "NC", v: "B2_End" }, { k: "NC", v: "H1_Jam" }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "COIL", v: "M1_Run" }],
                  [{ k: "NO", v: "M1_Run" }, null, null, null, null, null, null, null]],
          links: [[0, 1]] },
        { comment: ["堵料：运行 6 s 没到末端", "Jam: running 6 s without reaching the end"],
          cells: [[{ k: "NO", v: "M1_Run" }, { k: "FB", fb: "TON", inst: "tJam", p: { PT: "T#6s" } }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "SET", v: "H1_Jam" }]],
          links: [] },
        { comment: ["按启动复位报警", "Start resets the alarm"],
          cells: [[{ k: "P", v: "S1_Start" }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "WIRE" }, { k: "RST", v: "H1_Jam" }]],
          links: [] },
      ],
    },
    watch: ["tJam.ET"],
    tests: [
      { id: "run", name: ["按启动，工件送到末端后停", "Start: the part travels to the end and the belt stops"],
        steps: [{ set: { S2_Stop: true } }, { wait: 50 }, { set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } },
                { until: { B2_End: true }, within: 5000 }, { wait: 30 }, { expect: { M1_Run: false, H1_Jam: false } }] },
      { id: "stop", name: ["运行中按停止立即停，松开后不自己再启动", "Stop while running stops at once and does not restart on release"],
        steps: [{ set: { S2_Stop: true } }, { wait: 50 }, { set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } }, { wait: 500 },
                { set: { S2_Stop: false } }, { wait: 30 }, { expect: { M1_Run: false } }, { set: { S2_Stop: true } }, { never: { M1_Run: true }, during: 1000 }] },
      { id: "jam", name: ["堵料 6 s 报警并停机", "A jam raises the alarm after 6 s and stops"], faults: { jam: true },
        steps: [{ set: { S2_Stop: true } }, { wait: 50 }, { set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } },
                { never: { H1_Jam: true }, during: 5500 }, { until: { H1_Jam: true }, within: 1000 }, { wait: 30 }, { expect: { M1_Run: false } }] },
      { id: "wire", name: ["停止按钮断线（常闭断开）时不能启动", "With the stop wire broken (NC open) it cannot start"],
        steps: [{ set: { S2_Stop: false } }, { wait: 50 }, { set: { S1_Start: true } }, { never: { M1_Run: true }, during: 500 }] },
    ],
  },
  plant: {
    panel: [{ name: "S1_Start", kind: "push", label: ["启动 S1", "Start S1"] }, { name: "S2_Stop", kind: "nc-push", label: ["停止 S2", "Stop S2"] }],
    faults: [{ id: "jam", name: ["堵料", "Jam"] }],
    reset(s, o) { s.x = 0.1; s.v = 0; s.faults = (o && o.faults) || {}; },
    inputs(s) { return { B2_End: s.x >= 0.92 }; },
    step(dt, out, s) {
      const target = out.M1_Run && !s.faults.jam ? 0.25 : 0;          // belt speed, m/s
      s.v += (target - s.v) * Math.min(1, dt / 150);                    // the motor needs ~0.15 s to get up to speed
      s.x = Math.min(1.0, s.x + s.v * dt / 1000);
      s.run = out.M1_Run; s.jamLamp = out.H1_Jam;
    },
    read(s, n) { return n === "x" ? s.x : undefined; },
  },
  tasks: [
    { id: "run", test: "run", text: ["测试“按启动，工件送到末端后停”通过。", "Pass the test 'Start: the part travels to the end'."] },
    { id: "stop", test: "stop", text: ["测试“按停止立即停、不自己再启动”通过。", "Pass the test 'Stop stops at once and does not restart'."] },
    { id: "jam", test: "jam", text: ["测试“堵料 6 s 报警”通过。", "Pass the jam test."] },
    { id: "hand", text: ["手动操作：把工件送到末端一次。", "By hand: bring a part to the end once."] },
  ],
  think: ["停止按钮为什么用常闭触点接线？“停止按钮断线”这条测试说明了什么？", "Why is the stop button wired normally closed? What does the 'broken wire' test show?"],
  check(api, s) { if (s.x >= 0.92 && api.running) api.done("hand"); },
  readouts(api, s) {
    return [[["工件位置", "Part position"], api.fmt(s.x, 3) + " m"], [["输送速度", "Belt speed"], api.fmt(s.v, 3) + " m/s"]];
  },
  draw(api, s) {
    const { w, h } = api, io = api.plc.io;
    const y = h * 0.58, x0 = w * 0.08, x1 = w * 0.9, k = (x1 - x0);
    // frame and belt
    api.rect(x0 - 20, y, k + 40, 26, api.css("--soft"), api.css("--ink"), 13);
    const off = ((s.x || 0) * 40 * k) % 24;
    for (let x = x0 - 10 + (off % 24); x < x1 + 10; x += 24) api.line(x, y + 4, x - 6, y + 22, api.css("--muted"), 1.5);
    api.circle(x0 - 7, y + 13, 11, api.css("--panel"), api.css("--ink")); api.circle(x1 + 7, y + 13, 11, api.css("--panel"), api.css("--ink"));
    // motor M1
    api.rect(x0 - 40, y + 30, 46, 34, io.M1_Run ? api.css("--green") : api.css("--panel"), api.css("--ink"), 6);
    api.label("M1", x0 - 17, y + 47, io.M1_Run ? "#fff" : api.css("--ink"), 13, "center");
    // the part
    const px = x0 + k * (s.x || 0);
    api.rect(px - 26, y - 44, 52, 44, api.css("--amber"), api.css("--ink"), 4);
    // end sensor B2 (beam across the belt end)
    const bx = x0 + k * 0.92 - 26;
    api.line(bx, y - 70, bx, y - 4, io.B2_End ? api.css("--red") : api.css("--muted"), 2, [5, 4]);
    api.rect(bx - 8, y - 84, 16, 14, io.B2_End ? api.css("--red") : api.css("--panel"), api.css("--ink"), 3);
    api.label("B2", bx, y - 96, api.css("--ink"), 13, "center");
    // jam lamp H1
    api.circle(w * 0.84, h * 0.16, 16, io.H1_Jam ? api.css("--red") : api.css("--panel"), api.css("--ink"));
    api.label(api.T("H1 堵料", "H1 Jam"), w * 0.84, h * 0.16 + 30, api.css("--ink"), 13, "center");
    if (s.faults && s.faults.jam) api.label(api.T("（故障：堵料）", "(fault: jam)"), px, y - 58, api.css("--red"), 12, "center");
  },
});
