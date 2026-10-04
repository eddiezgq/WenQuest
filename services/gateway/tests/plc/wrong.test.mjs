// 第 18 轮第 5 步验收：十段常见的错误程序，全部被自动化测试或程序检查拦下；正确的参考程序不被误报为错误。
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const P = require("../../app/production/labkit/plc.js");
const W = require("../../app/production/labkit/plants.js");
const src = readFileSync(new URL("./plants.test.mjs", import.meta.url), "utf8");
const REF = Object.fromEntries(["TRAFFIC", "ELEVATOR", "SORTER", "PRESS"].map((k) => [k, src.match(new RegExp(`const ${k} = \`([\\s\\S]*?)\`;`))[1]]));
const demo = readFileSync(new URL("../../app/production/labkit/demo_plc.js", import.meta.url), "utf8");

// the conveyor of the example lab, as a plant
const conveyor = {
  io: [
    { name: "S1_Start", addr: "%IX0.0", dir: "in", comment: ["启动按钮（常开）", "Start (NO)"] },
    { name: "S2_Stop", addr: "%IX0.1", dir: "in", comment: ["停止按钮（常闭）", "Stop (NC)"] },
    { name: "B2_End", addr: "%IX0.2", dir: "in", comment: ["末端光电", "End sensor"] },
    { name: "M1_Run", addr: "%QX0.0", dir: "out" }, { name: "H1_Jam", addr: "%QX0.1", dir: "out" },
  ],
  reset(s, o) { s.x = 0.1; s.v = 0; s.f = (o && o.faults) || {}; },
  inputs(s) { return { B2_End: s.x >= 0.92 }; },
  step(dt, out, s) { const t = out.M1_Run && !s.f.jam ? 0.25 : 0; s.v += (t - s.v) * Math.min(1, dt / 150); s.x = Math.min(1, s.x + s.v * dt / 1000); },
};
const convTests = [
  { id: "run", steps: [{ set: { S2_Stop: true } }, { wait: 50 }, { set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } }, { until: { B2_End: true }, within: 5000 }, { wait: 30 }, { expect: { M1_Run: false } }] },
  { id: "stop", steps: [{ set: { S2_Stop: true } }, { wait: 50 }, { set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } }, { wait: 500 }, { set: { S2_Stop: false } }, { wait: 30 }, { expect: { M1_Run: false } }, { set: { S2_Stop: true } }, { never: { M1_Run: true }, during: 1000 }] },
  { id: "jam", faults: { jam: true }, steps: [{ set: { S2_Stop: true } }, { wait: 50 }, { set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } }, { until: { H1_Jam: true }, within: 7000 }, { wait: 30 }, { expect: { M1_Run: false } }] },
  { id: "ack", faults: { jam: true }, steps: [{ set: { S2_Stop: true } }, { wait: 50 }, { set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } }, { until: { H1_Jam: true }, within: 7000 },
    { wait: 200 }, { set: { S1_Start: true } }, { until: { H1_Jam: false }, within: 100 }] },
];
const CONV = `PROGRAM Main
  VAR tJam : TON; rStart : R_TRIG; END_VAR
  rStart(CLK := S1_Start);
  IF rStart.Q THEN H1_Jam := FALSE; END_IF;
  M1_Run := (S1_Start OR M1_Run) AND S2_Stop AND NOT B2_End AND NOT H1_Jam;
  tJam(IN := M1_Run, PT := T#6s);
  IF tJam.Q THEN H1_Jam := TRUE; END_IF;
END_PROGRAM`;

const machines = {
  conveyor: { plant: conveyor, tests: convTests },
  traffic: { plant: W.traffic(), tests: [{ id: "safe", steps: [{ never: { hazard: true }, during: 20000 }] }, { id: "go", steps: [{ until: { NS_G: true }, within: 9000 }, { until: { EW_G: true }, within: 9000 }] }] },
  elevator: { plant: W.elevator(), tests: [{ id: "up", steps: [{ wait: 2000 }, { set: { S_C3: true } }, { wait: 100 }, { set: { S_C3: false } }, { until: { floor: 3 }, within: 12000 }, { until: { B_DoorOpen: true }, within: 3000 }, { expect: { hazard: false } }] }] },
  sorter: { plant: W.sorter(), tests: [{ id: "sort", steps: [{ set: { S_Stop: true } }, { wait: 50 }, { set: { S_Start: true } }, { wait: 100 }, { set: { S_Start: false } }, { until: { done: true }, within: 60000 }, { expect: { wrong: 0 } }] }] },
  press: { plant: W.press(), tests: [{ id: "lc", steps: [{ set: { S_LC: true, B_Part: true } }, { wait: 100 }, { set: { S_Hand1: true, S_Hand2: true } }, { wait: 1500 }, { set: { S_LC: false } }, { never: { hazard: true }, during: 500 }] }] },
};
function judge(machine, st) {
  const m = machines[machine];
  const failed = m.tests.filter((t) => !P.runTest({ io: m.plant.io, st, cycle: 10 }, m.plant, t).ok).map((t) => t.id);
  const errors = P.review({ st }, m.plant.io).filter((r) => r.level === "error").map((r) => r.rule);
  return { failed, errors, caught: failed.length > 0 || errors.length > 0 };
}

test("the reference programs pass every test and the review finds no errors", () => {
  for (const [m, st] of [["conveyor", CONV], ["traffic", REF.TRAFFIC], ["elevator", REF.ELEVATOR], ["sorter", REF.SORTER], ["press", REF.PRESS]]) {
    const j = judge(m, st);
    assert.deepEqual(j, { failed: [], errors: [], caught: false }, m);
  }
  // the example lab's ladder program too
  const lad = eval("(" + demo.match(/ladder: (\[[\s\S]*?\n      \]),\n    \},\n    watch/)[1] + ")");
  const errs = P.review({ decls: "VAR tJam : TON; END_VAR", ladder: lad }, conveyor.io).filter((r) => r.level === "error");
  assert.deepEqual(errs, []);
});

const WRONG = [
  ["1 停止按钮当常开用（松开就停不了）", "conveyor", CONV.replace("AND S2_Stop AND", "AND NOT S2_Stop AND")],
  ["2 没有自锁（松开启动按钮就停）", "conveyor", CONV.replace("(S1_Start OR M1_Run)", "S1_Start")],
  ["3 双线圈：报警处又写了一次电机", "conveyor", CONV.replace("IF tJam.Q THEN H1_Jam := TRUE; END_IF;", "IF tJam.Q THEN H1_Jam := TRUE; END_IF;\n  M1_Run := M1_Run AND NOT tJam.Q;\n  M1_Run := M1_Run;")],
  ["4 堵料报警置位后从不复位", "conveyor", CONV.replace("IF rStart.Q THEN H1_Jam := FALSE; END_IF;", "")],
  ["5 用 WHILE 等末端光电", "conveyor", CONV.replace("tJam(IN", "WHILE NOT B2_End AND M1_Run DO tJam(IN := TRUE, PT := T#6s); END_WHILE;\n  tJam(IN")],
  ["6 交通灯两个方向同时绿", "traffic", REF.TRAFFIC.replace("EW_G := step = 3;", "EW_G := step = 3 OR step = 0;")],
  ["7 电梯开着门就走", "elevator", REF.ELEVATOR.replace("K_Up := target > floor AND S_TopLim AND B_DoorClosed;", "K_Up := target > floor AND S_TopLim;").replace("IF B_DoorClosed THEN Y_DoorClose", "IF TRUE THEN Y_DoorClose")],
  ["8 电梯不用上极限开关", "elevator", REF.ELEVATOR.replace("K_Up := target > floor AND S_TopLim AND B_DoorClosed;", "K_Up := target > floor AND B_DoorClosed;").replace("K_Down := target < floor AND S_LowLim AND", "K_Down := target < floor AND")],
  ["9 分拣不跟踪：见到工件就推", "sorter", REF.SORTER.replace("IF kind[s1 MOD 32] = 1 THEN", "IF TRUE THEN")],
  ["10 压装不理光幕", "press", REF.PRESS.replace("Y_PressDown := S_Hand1 AND S_Hand2 AND S_LC;", "Y_PressDown := S_Hand1 AND S_Hand2;").replace("IF NOT (S_Hand1 AND S_Hand2 AND S_LC) OR force > 8.0", "IF NOT (S_Hand1 AND S_Hand2) OR force > 8.0")],
];
for (const [name, machine, st] of WRONG) {
  test("caught: " + name, () => {
    const j = judge(machine, st);
    assert.ok(j.caught, `${name}: not caught ${JSON.stringify(j)}`);
    if (process.env.PLC_SHOW) console.log(name, JSON.stringify(j));
  });
}
