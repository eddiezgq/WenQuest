// 实验 7.4 读转矩记录：最大转矩、平均转矩、起动冲击系数和雨流计数（配 7.2–7.4 节）。
// 试验台场景与数字工厂跑合试验台“工况模拟”段同一个模型（sim/engine.torque_record：起动峰值 1.5–1.7 倍额定、稳定运行 0.70–0.80 倍额定、
// 0.5 Hz 的波动 8% 额定加噪声），随机数发生器不同，所以数值与程序 7.2.1、7.4.1 的那一条记录不完全一样。
// 机器人场景用 UR5e 的连杆质量与长度（零件库模型，程序 7.1.1）；自行车场景的踩踏转矩是本书设定的示意模型。
// 雨流计数按 ASTM E1049-85（与 _ch7.rainflow 同一算法）。
function rng7_4(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function gauss7_4(r) { return Math.sqrt(-2 * Math.log(r() + 1e-12)) * Math.cos(2 * Math.PI * r()); }
const ARM7_4 = [[8.393, 0.2125], [2.275, 0.621], [2.6269, 0.817]];   // UR5e：上臂、小臂、腕部（kg, m），负载在 0.917 m
function signal7_4(scene, p) {
  const r = rng7_4(Math.round(p.seed)), dt = 0.1, y = [];
  if (scene === "bench") {
    const tr = p.T0;
    for (let k = 0; k < Math.round(p.n); k++) {
      const peak = tr * (1.5 + 0.2 * r()), mean = tr * (0.70 + 0.10 * r());
      for (let i = 0; i < 250; i++) {
        const t = i * dt; let v;
        if (t < 1) v = peak * t;
        else if (t < 2) v = mean + (peak - mean) * Math.exp(-4 * (t - 1));
        else if (t < 22) v = mean + 0.08 * tr * Math.sin(2 * Math.PI * 0.5 * t) + gauss7_4(r) * 0.03 * tr;
        else if (t < 23) v = mean * (23 - t);
        else v = gauss7_4(r) * 0.005 * tr;
        y.push(v);
      }
    }
    return { dt, y, unit: "N·m" };
  }
  if (scene === "robot") {                       // 码垛：持负载转 60°，停 0.5 s，空手转回，停 0.5 s；肩关节力矩 = 重力矩 + J·θ̈
    const g = 9.81, tm = p.T0 / 10, ta = tm / 3, th0 = -Math.PI / 6, th1 = Math.PI / 6;
    for (let k = 0; k < Math.round(p.n); k++) {
      [[p.load, th0, th1], [0, th1, th0]].forEach(([m, a, b]) => {
        const items = ARM7_4.concat([[m, 0.917]]);
        const M0 = items.reduce((s, [mm, x]) => s + mm * g * x, 0), J = items.reduce((s, [mm, x]) => s + mm * x * x, 0);
        const wm = (b - a) / (tm - ta), al = wm / ta;
        for (let t = 0; t < tm + 0.5; t += dt) {
          let th, acc;
          if (t < ta) { th = a + 0.5 * al * t * t; acc = al; }
          else if (t < tm - ta) { th = a + 0.5 * al * ta * ta + wm * (t - ta); acc = 0; }
          else if (t < tm) { const q = tm - t; th = b - 0.5 * al * q * q; acc = -al; }
          else { th = b; acc = 0; }
          y.push(M0 * Math.cos(th) + J * acc + gauss7_4(r) * 0.5);
        }
      });
    }
    return { dt, y, unit: "N·m" };
  }
  // bike：曲柄转矩，左右脚各踩半圈 T = Tpk·|sin φ|；起步的前 3 s 站起来踩，峰值加大；每段骑 20 s 后停 5 s
  const cad = 80 / 60;                            // 踏频 80 r/min
  for (let k = 0; k < Math.round(p.n); k++) {
    for (let t = 0; t < 25; t += dt) {
      if (t >= 20) { y.push(0); continue; }
      const boost = t < 3 ? 1 + 0.8 * (1 - t / 3) : 1;
      y.push(p.T0 * boost * Math.abs(Math.sin(2 * Math.PI * cad * t)) * (1 + 0.05 * gauss7_4(r)));
    }
  }
  return { dt, y, unit: "N·m" };
}
function rainflow7_4(x) {                         // ASTM E1049-85：返回 [[范围, 次数]]
  const rev = [];
  x.forEach((v) => {
    if (rev.length && v === rev[rev.length - 1]) return;
    if (rev.length >= 2 && (rev[rev.length - 1] - rev[rev.length - 2]) * (v - rev[rev.length - 1]) > 0) rev[rev.length - 1] = v;
    else rev.push(v);
  });
  const st = [], out = [];
  rev.forEach((v) => {
    st.push(v);
    while (st.length >= 3) {
      const X = Math.abs(st[st.length - 1] - st[st.length - 2]), Y = Math.abs(st[st.length - 2] - st[st.length - 3]);
      if (X < Y) break;
      if (st.length === 3) { out.push([Y, 0.5]); st.shift(); }
      else { out.push([Y, 1]); const last = st.pop(); st.pop(); st.pop(); st.push(last); }
    }
  });
  for (let i = 0; i + 1 < st.length; i++) out.push([Math.abs(st[i + 1] - st[i]), 0.5]);
  return out;
}
function analyse7_4(scene, p) {
  const s = signal7_4(scene, p), y = s.y;
  const max = Math.max(...y), mean = y.reduce((a, b) => a + b, 0) / y.length;
  const on = y.filter((v) => v > 0.05 * max);                        // 运行时（去掉停机）
  const sorted = on.slice().sort((a, b) => a - b), med = sorted[Math.floor(sorted.length / 2)] || 1;
  const steady = on.filter((v) => v < 1.3 * med);                    // 稳定段（去掉起动峰）
  let runMean = steady.reduce((a, b) => a + b, 0) / (steady.length || 1);
  if (scene === "robot") runMean = ARM7_4.concat([[p.load, 0.917]]).reduce((a, [mm, x]) => a + mm * 9.81 * x, 0);   // 机器人：手臂水平静止持重的力矩
  const cyc = rainflow7_4(y), n = cyc.reduce((a, c) => a + c[1], 0);
  const eq = Math.pow(cyc.reduce((a, c) => a + c[1] * Math.pow(c[0] / 2, p.m), 0) / n, 1 / p.m);
  const big = cyc.filter((c) => c[0] > 0.5 * max).reduce((a, c) => a + c[1], 0);
  const revs = scene === "bike" ? Math.round(p.n) * 20 * 80 / 60 : 0;           // 自行车：骑行时间里曲柄转过的圈数
  return { s, max, mean, runMean, k: max / runMean, cyc, n, eq, big, revs, maxRange: Math.max(...cyc.map((c) => c[0])) };
}
WQ.lab({
  title: ["实验 7.4 读转矩记录：载荷的大小、冲击与循环", "Lab 7.4 Reading a torque record: magnitude, impact and cycles"],
  goal: ["读一段转矩的时间历程，求最大转矩、平均转矩、起动冲击系数，再用雨流计数把它分解成一个个循环，比较三种机器的载荷有什么不同。",
         "Read a torque–time history, find the maximum and mean torque and the start impact factor, then split it into cycles by rainflow counting, and compare the loads of three machines."],
  scenes: [
    { id: "bench", robot: false, name: ["WQR-105 跑合试验台", "WQR-105 run-in bench"],
      problem: { title: ["工程问题：减速器出厂前的“工况模拟”", "Engineering problem: the duty simulation before a reducer ships"],
                 text: ["每台 WQR-105 出厂前在跑合试验台上模拟带式输送机起动—运行—停机三次，记录输出转矩（数字工厂“生产”页可以看到每台的记录）。设计时该按多大的转矩算？",
                        "Before shipping, every WQR-105 runs three start–run–stop cycles of a belt conveyor on the run-in bench, and the output torque is recorded (each unit's record is on the factory's Production page). Which torque should design use?"] } },
    { id: "robot", robot: true, name: ["码垛机器人的肩关节", "Palletizing robot shoulder"],
      problem: { title: ["工程问题：码垛机器人肩关节的力矩", "Engineering problem: shoulder torque of a palletizing robot"],
                 text: ["UR5e 做码垛：持着箱子把手臂转过 60°，放下，空手转回，周而复始。肩关节的减速器每个工作循环受几次载荷？哪一部分来自重力、哪一部分来自加速？",
                        "A UR5e palletizes: it swings 60° holding a box, puts it down and swings back empty, over and over. How many load cycles does the shoulder reducer see per work cycle, and how much comes from gravity versus acceleration?"] } },
    { id: "bike", name: ["自行车的曲柄", "Bicycle crank"],
      problem: { title: ["生活中的例子：自行车的踩踏", "Everyday example: pedaling a bicycle"],
                 text: ["骑车时曲柄的转矩是左右脚轮流踩出来的，起步时站起来踩更大。中轴每转一圈受几次载荷？",
                        "Crank torque comes from the two feet in turn, and is larger when you stand on the pedals to start. How many load cycles does the bottom bracket see per revolution?"] } },
  ],
  params: [
    { id: "T0", name: ["额定转矩 / 运动时间×10 / 踩踏峰值", "Rated torque / move time ×10 / pedal peak"], min: 5, max: 600, step: 1, value: 350, unit: "", digits: 0 },
    { id: "n", name: ["起停（工作循环）次数", "Number of start–stops (work cycles)"], min: 1, max: 6, step: 1, value: 3, unit: "", digits: 0 },
    { id: "load", name: ["机器人负载", "Robot payload"], min: 0, max: 10, step: 0.5, value: 5, unit: "kg", digits: 1 },
    { id: "m", name: ["当量幅值的指数 m", "Exponent m for the equivalent amplitude"], min: 3, max: 12, step: 1, value: 9, unit: "", digits: 0 },
    { id: "seed", name: ["记录编号（随机数种子）", "Record number (random seed)"], min: 1, max: 99, step: 1, value: 1, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["读取记录", "Read record"], primary: true }, { id: "reset", name: ["清除", "Clear"] }],
  legend: [{ color: "#1d2327", name: ["转矩记录", "torque record"] }, { color: "#d62728", name: ["最大值", "maximum"] }, { color: "#1f77b4", name: ["稳定运行的平均值（机器人：静止持重）", "steady-running mean (robot: static holding)"] }],
  tasks: [
    { id: "bench", text: ["试验台记录（默认参数）：读出最大转矩、平均转矩、稳定运行平均转矩，算起动冲击系数。", "Bench record (defaults): read the maximum, mean and steady-running mean torque and work out the start impact factor."],
      demo: { scene: "bench", set: { T0: 350, n: 3, load: 5, m: 9, seed: 1 }, press: ["start"], wait: 1 } },
    { id: "exp", text: ["把指数 m 从 9 改成 3 再读：当量幅值怎样变？哪一种循环说了算？", "Change m from 9 to 3: how does the equivalent amplitude change, and which cycles dominate?"],
      demo: { scene: "bench", set: { T0: 350, n: 3, load: 5, m: 3, seed: 1 }, press: ["start"], wait: 1 } },
    { id: "robot", robot: true, text: ["码垛机器人，负载 5 kg 和 10 kg 各读一次：每个工作循环有几个大循环？力矩的最大值比静止持重时大多少？", "Palletizing robot with 5 kg and 10 kg: how many large cycles per work cycle, and how much larger is the peak than the static holding torque?"],
      demo: { scene: "robot", set: { T0: 12, n: 3, load: 10, m: 9, seed: 1 }, press: ["start"], wait: 1 } },
    { id: "bike", text: ["自行车，踩踏峰值 60 N·m：中轴每转一圈受几次载荷？起动冲击系数多大？", "Bicycle, pedal peak 60 N·m: how many load cycles per crank revolution, and what is the start impact factor?"],
      demo: { scene: "bike", set: { T0: 60, n: 2, load: 5, m: 9, seed: 1 }, press: ["start"], wait: 1 } },
  ],
  think: ["程序 7.4.1 的雨流计数与本实验同一算法。数字孪生的边缘端把每次起停简化成一个 0 → 峰值 → 0 的循环、把运行波动简化成固定幅值的小循环。和本实验逐点计数的结果比，这样简化在什么情况下会出错？",
          "Program 7.4.1 uses the same rainflow algorithm. The twin's edge device simplifies each start–stop to one 0 → peak → 0 cycle and the running ripple to small cycles of fixed amplitude. Compared with the full count in this lab, when would that simplification go wrong?"],

  reset(api, s) { s.r = null; },
  update(dt, api, s) {
    s.r = analyse7_4(api.scene, api.p);
    if (api.scene === "bench" && Math.round(api.p.m) === 9) api.done("bench");
    if (api.scene === "bench" && Math.round(api.p.m) <= 3) api.done("exp");
    if (api.scene === "robot" && api.p.load >= 10) api.done("robot");
    if (api.scene === "bike") api.done("bike");
    api.stop();
  },
  readouts(api, s) {
    const f = api.fmt, r = s.r;
    if (!r) return [[["状态", "Status"], api.T("按“读取记录”开始", "press Read record")]];
    return [
      [["最大转矩", "Maximum torque"], f(r.max, 1) + " N·m"],
      [["平均转矩（整段记录）", "Mean torque (whole record)"], f(r.mean, 1) + " N·m"],
      [[api.scene === "robot" ? "静止持重（手臂水平）的力矩" : "稳定运行的平均转矩", api.scene === "robot" ? "Static holding torque (arm horizontal)" : "Steady-running mean torque"], f(r.runMean, 1) + " N·m"],
      [[api.scene === "robot" ? "动载系数 = 最大 / 静止持重" : "起动冲击系数 = 最大 / 稳定运行平均", api.scene === "robot" ? "Dynamic factor = max / static holding" : "Start impact factor = max / steady mean"], f(r.k, 2)],
      [["每秒的雨流循环数", "Rainflow cycles per second"], f(r.n / (r.s.y.length * r.s.dt), 2)],
      [["雨流循环总数（半循环算 0.5）", "Rainflow cycles (half cycles count 0.5)"], f(r.n, 1)],
      [["大循环（范围 > 最大值的一半）", "Large cycles (range > half the maximum)"], f(r.big, 1)],
      [["当量幅值（与全部循环同次数）", "Equivalent amplitude (same number of cycles)"], f(r.eq, 1) + " N·m"],
    ].concat(r.revs ? [[["每转的雨流循环数（只算骑行时间）", "Rainflow cycles per crank revolution (riding time only)"], f(r.n / r.revs, 2)]] : []);
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    if (!s.r) { api.label(api.T("按“读取记录”读入一段转矩记录", "Press Read record to load a torque record"), w / 2, h / 2, css("--muted"), 14, "center"); return; }
    const r = s.r, y = r.s.y, dt = r.s.dt;
    const pts = y.map((v, i) => [i * dt, v]);
    const ymax = Math.max(r.max * 1.1, 1);
    const P = api.plot(50, 20, w - 70, h * 0.55, [{ pts, color: css("--ink") },
      { pts: [[0, r.max], [y.length * dt, r.max]], color: "#d62728" }, { pts: [[0, r.runMean], [y.length * dt, r.runMean]], color: "#1f77b4" }],
      { ymin: Math.min(0, ...y), ymax, xlabel: api.T("时间 / s", "time / s"), ylabel: api.T("转矩 / N·m", "torque / N·m") });
    // 雨流直方图：按范围分 10 档
    const bins = 10, top = Math.max(r.maxRange, 1), cnt = new Array(bins).fill(0);
    r.cyc.forEach(([rg, n]) => { cnt[Math.min(bins - 1, Math.floor(rg / top * bins))] += n; });
    const x0 = 50, y0 = h * 0.55 + 55, W = w - 70, H = h - y0 - 30, cm = Math.max(...cnt.map((c) => Math.log10(1 + c)), 1);
    api.rect(x0, y0, W, H, null, css("--grid"));
    cnt.forEach((c, i) => {
      const bh = Math.log10(1 + c) / cm * H;
      api.rect(x0 + i * W / bins + 3, y0 + H - bh, W / bins - 6, bh, i >= bins / 2 ? "#d62728" : "#1f77b4");
      api.label(c ? (Math.round(c * 2) / 2).toString() : "", x0 + (i + 0.5) * W / bins, y0 + H - bh - 4, css("--muted"), 11, "center");
    });
    api.label(api.T("雨流循环的范围（0 到最大范围，分 10 档；纵轴为次数的对数）", "rainflow ranges (0 to the largest, 10 bins; height = log of count)"), x0 + W, y0 + H + 16, css("--muted"), 12, "right");
  },
});
