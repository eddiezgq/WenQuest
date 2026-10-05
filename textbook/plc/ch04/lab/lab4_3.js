// 实验 4.3 扫描周期可视化：程序越长，扫描越慢，快的工件就数漏了（配 4.3、4.7 节）。
// 计件输送线：工件长 40 mm、间距 100 mm，带速 0.5 / 2 / 5 m/s 时工件挡光 80 / 20 / 8 ms。实验台的扫描时间按程序实际执行的语句数算：
// 固定开销 0.5 ms + 每条语句 1 µs（FOR 循环每转一圈约 2 条），自由循环；扫描时间超过 150 ms，看门狗让 PLC 停机。
const plant = WQPLANTS.counter();
const SM = { base: 0.5, perStep: 1 };
const prog = (n, hsc) => `PROGRAM Main
  VAR
    cnt : CTU;             (* 对 B1_Part 的上升沿计数 *)
    n : DINT := ${n};       (* 其余程序：用一个循环代替，改 n 就改了程序的长度 *)
    i : DINT;
    work : DINT;${hsc ? `
    base : DINT;           (* 清零时记下高速计数器的读数 *)
    countHsc : DINT;      (* 用高速计数器数的件数 *)` : ""}
  END_VAR
  cnt(CU := B1_Part, R := S1_Reset, PV := 30000);
${hsc ? `  IF S1_Reset THEN
    base := HSC1_CV;
  END_IF;
  countHsc := HSC1_CV - base;
` : ""}  FOR i := 1 TO n DO
    work := work + 1;
  END_FOR;
  H1_Count := B1_Part;
END_PROGRAM
`;
const P = (n, hsc) => ({ st: prog(n, hsc) });
const val = (api, n) => { try { return api.plc.rt ? api.plc.rt.watchAny(n) : undefined; } catch (e) { return undefined; } };
WQ.lab({
  title: ["实验 4.3 扫描周期可视化：找出漏计的临界点", "Lab 4.3 Seeing the scan: where counting starts to miss"],
  goal: ["在计件输送线上改变程序的长度和带速，看扫描时间怎样变、计数从哪里开始漏；让看门狗动作一次；最后改用高速计数器，在长程序、高带速下也一个不漏。",
         "On the counting conveyor, change the program's length and the belt speed; watch the scan time and find where counting starts to miss; trip the watchdog once; finally switch to the high-speed counter, which misses nothing even with a long program at high speed."],
  view: "plc",
  scenes: [{ id: "count", name: ["计件输送线", "Counting conveyor"],
    problem: { title: ["车间问题：提速以后，产量报表少了四分之一", "Shop-floor problem: after a speed-up, the count is a quarter short"],
               text: ["装配线的计件输送线从 2 m/s 提到 5 m/s，同时程序里加了一大段统计功能。此后，PLC 报的件数比下游装箱数少了约四分之一。光电开关 B1 每来一个工件挡一次光，程序用计数器数 B1 的上升沿。",
                      "The counting conveyor was sped up from 2 to 5 m/s, and a large statistics block was added to the program. Since then the PLC's count is about a quarter below the packing count. Photo sensor B1 is blocked once per part; the program counts B1's rising edges."] } }],
  params: [],
  plc: {
    io: plant.io, lang: "ST", langs: ["ST"], cycle: 1, scanModel: SM, cycleMode: "free", watchdog: 150, budget: 10000000,
    program: { st: prog(1000, false) },
    watch: ["Main.cnt.CV", "Main.n"],
    tests: [
      { id: "reset", name: ["按 S1 清零：计数回到 0", "S1 resets the count to 0"], steps: [{ wait: 1000 }, { set: { S1_Reset: true } }, { wait: 50 }, { expect: { "cnt.CV": 0 } }, { set: { S1_Reset: false } }] },
    ],
  },
  plant,
  tasks: [
    { id: "ok5", text: ["第 1 步：起始程序 n = 1000。打开“带速 5 m/s”，运行，看状态栏的扫描时间；计数与实际件数相同（数满 50 件）。", "Step 1: the starting program has n = 1000. Switch on 5 m/s and run; read the scan time in the status bar; the count equals the parts (50 parts)."],
      demo: { program: P(1000, false), panel: { VeryFast: true }, run: true, wait: 8 } },
    { id: "miss", text: ["第 2 步：把 n 逐步加大（2000、3000……），每次下载后按 S1 清零再数，找出开始漏计的 n 和扫描时间（漏 3 件以上）。", "Step 2: raise n step by step (2000, 3000, …); after each download press S1 and count again; find the n and scan time where parts start to be missed (3 or more)."],
      demo: { program: P(5000, false), panel: { VeryFast: true }, run: true, wait: 8 } },
    { id: "ok2", text: ["第 3 步：n = 5000（扫描约 10.5 ms），改回“带速 2 m/s”（关掉 5 m/s），按 S1 清零，又一个不漏了（数满 30 件）。为什么？", "Step 3: with n = 5000 (scan about 10.5 ms), switch back to 2 m/s (5 m/s off), press S1: nothing is missed again (30 parts). Why?"],
      demo: { program: P(5000, false), panel: { Fast: true, VeryFast: false }, run: true, wait: 10 } },
    { id: "wd", text: ["第 4 步：把 n 改成 100000，下载运行：扫描时间超过 150 ms，看门狗让 PLC 停机。读出状态栏的提示。", "Step 4: set n = 100000, download and run: the scan exceeds 150 ms and the watchdog stops the PLC. Read the message in the status bar."],
      demo: { program: P(100000, false), run: true, wait: 4 } },
    { id: "hsc", text: ["第 5 步：n 回到 5000，带速 5 m/s。加上读高速计数器 HSC1_CV 的几行（程序 4.7.1），按 S1 清零：countHsc 一个不漏（数满 50 件），cnt 照样漏。", "Step 5: n back to 5000, 5 m/s. Add the lines that read the high-speed counter HSC1_CV (Program 4.7.1); press S1: countHsc misses nothing (50 parts) while cnt still does."],
      demo: { program: P(5000, true), panel: { VeryFast: true }, run: true, wait: 8 } },
  ],
  check(api, s) {
    const rt = api.plc.rt;
    if (!rt) return;
    if (rt.error && rt.error.code === "watchdog" && /扫描时间/.test(rt.error.message)) api.done("wd");   // the time watchdog, not the step budget
    const cnt = val(api, "cnt.CV"), hsc = val(api, "countHsc");
    if (typeof cnt !== "number") return;
    const lost = s.since - cnt;
    if (s.fast2 && s.since >= 50 && lost <= 1) api.done("ok5");
    if (s.fast2 && s.since >= 30 && lost >= 3) api.done("miss");
    if (!s.fast2 && s.fast && rt.maxScan > 8 && s.since >= 30 && lost <= 1) api.done("ok2");
    if (s.fast2 && typeof hsc === "number" && rt.maxScan > 8 && s.since >= 50 && Math.abs(s.since - hsc) <= 1) api.done("hsc");
  },
  think: ["带速 5 m/s 时工件挡光 8 ms、两件之间的空档 12 ms。扫描时间多长以内一定不漏？为什么扫描时间远大于 20 ms 时，数到的件数有时又会多起来一点？",
          "At 5 m/s a part blocks the beam for 8 ms and the gap is 12 ms. Up to what scan time is nothing ever missed? Why, with scans far above 20 ms, does the count sometimes go up a little again?"],
  readouts(api, s) {
    const rt = api.plc.rt;
    const cnt = val(api, "cnt.CV"), hsc = val(api, "countHsc");
    const r = [[["带速", "Belt speed"], api.fmt(plant.read(s, "speed") || 0, 1) + " m/s"], [["工件挡光", "Beam blocked"], api.fmt(plant.read(s, "pulseMs") || 0, 0) + " ms"],
               [["扫描时间", "Scan time"], rt && rt.scans ? api.fmt(rt.lastScan, 1) + " ms" : "—"], [["实际件数（清零后）", "Parts since reset"], String(s.since || 0)],
               [["计数器 cnt", "Counter cnt"], typeof cnt === "number" ? String(cnt) : "—"]];
    if (typeof hsc === "number") r.push([["高速计数 countHsc", "HSC count"], String(hsc)]);
    return r;
  },
});
