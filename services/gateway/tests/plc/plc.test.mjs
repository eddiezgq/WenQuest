// Tests of the PLC engine (labkit/plc.js): run with  node --test services/gateway/tests/plc/
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const P = require("../../app/production/labkit/plc.js");

const IO = [
  { name: "start", addr: "%IX0.0", dir: "in" }, { name: "stop", addr: "%IX0.1", dir: "in" },
  { name: "fwd", addr: "%IX0.2", dir: "in" }, { name: "rev", addr: "%IX0.3", dir: "in" },
  { name: "motor", addr: "%QX0.0", dir: "out" }, { name: "kmF", addr: "%QX0.1", dir: "out" }, { name: "kmR", addr: "%QX0.2", dir: "out" },
  { name: "lamp", addr: "%QX0.3", dir: "out" }, { name: "count", addr: "%QW2", dir: "out", type: "INT" },
];

function rt(st, extra = {}) { return new P.Runtime(Object.assign({ io: IO, st, cycle: 10 }, extra)); }
function press(r, name, v, scans = 1) { r.setInput(name, v); for (let k = 0; k < scans; k++) r.scan(); }

test("seal-in: start latches, stop (normally closed button wired as NC) breaks", () => {
  const r = rt(`PROGRAM Main
    motor := (start OR motor) AND stop;   (* stop is a normally closed button: TRUE when not pressed *)
  END_PROGRAM`);
  press(r, "stop", true);
  assert.equal(r.output("motor"), false);
  press(r, "start", true); press(r, "start", false);
  assert.equal(r.output("motor"), true);
  press(r, "stop", false);
  assert.equal(r.output("motor"), false);
  press(r, "stop", true);
  assert.equal(r.output("motor"), false, "no restart after the stop button is released");
});

test("forward/reverse with interlock: both contactors never on together", () => {
  const r = rt(`PROGRAM Main
    kmF := (fwd OR kmF) AND stop AND NOT kmR;
    kmR := (rev OR kmR) AND stop AND NOT kmF;
  END_PROGRAM`);
  press(r, "stop", true);
  press(r, "fwd", true); press(r, "fwd", false);
  press(r, "rev", true, 3);
  assert.equal(r.output("kmF"), true); assert.equal(r.output("kmR"), false);
});

test("TON: Q after PT measured in scans; ET grows by the cycle", () => {
  const r = rt(`PROGRAM Main
    VAR t1 : TON; END_VAR
    t1(IN := start, PT := T#100ms);
    lamp := t1.Q;
  END_PROGRAM`);
  r.setInput("start", true);
  let n = 0;
  while (!r.output("lamp") && n < 100) { r.scan(); n++; }
  // the timer starts in the first scan (now = 0) and is done when now - t0 >= 100 ms: the 11th scan
  assert.equal(n, 11);
  assert.equal(r.watch("Main.t1.ET"), 100);
  press(r, "start", false);
  assert.equal(r.output("lamp"), false);
  assert.equal(r.watch("Main.t1.ET"), 0);
});

test("TOF and TP", () => {
  const r = rt(`PROGRAM Main
    VAR off : TOF; p : TP; END_VAR
    off(IN := start, PT := T#50ms); lamp := off.Q;
    p(IN := fwd, PT := T#30ms); motor := p.Q;
  END_PROGRAM`);
  press(r, "start", true); press(r, "start", false);
  assert.equal(r.output("lamp"), true);
  for (let k = 0; k < 5; k++) r.scan();
  assert.equal(r.output("lamp"), false);
  press(r, "fwd", true);
  assert.equal(r.output("motor"), true);
  press(r, "fwd", false, 2);
  assert.equal(r.output("motor"), true, "TP keeps its pulse when IN falls");
  for (let k = 0; k < 3; k++) r.scan();
  assert.equal(r.output("motor"), false);
});

test("CTU counts rising edges only; INT overflow wraps like a 16-bit PLC", () => {
  const r = rt(`PROGRAM Main
    VAR c : CTU; n : INT := 32766; END_VAR
    c(CU := start, R := stop, PV := 3);
    lamp := c.Q;
    count := c.CV;
    n := n + 1;
  END_PROGRAM`);
  for (let k = 0; k < 3; k++) { press(r, "start", true, 2); press(r, "start", false); }
  assert.equal(r.output("count"), 3); assert.equal(r.output("lamp"), true);
  assert.ok(r.watch("Main.n") < 0, "32767 + 1 becomes negative in an INT");
  assert.equal(r.watch("Main.n"), -32768 + (r.scans - 2));
});

test("CASE state machine with an enumeration (traffic light)", () => {
  const r = rt(`TYPE E_Light : (RED, GREEN, YELLOW); END_TYPE
  PROGRAM Main
    VAR state : E_Light; t : TON; END_VAR
    CASE state OF
      RED:    t(IN := TRUE, PT := T#30ms); IF t.Q THEN t(IN := FALSE); state := GREEN; END_IF;
      GREEN:  t(IN := TRUE, PT := T#20ms); IF t.Q THEN t(IN := FALSE); state := YELLOW; END_IF;
      YELLOW: t(IN := TRUE, PT := T#10ms); IF t.Q THEN t(IN := FALSE); state := E_Light#RED; END_IF;
    END_CASE;
    lamp := state = GREEN;
  END_PROGRAM`);
  const seen = [];
  for (let k = 0; k < 15; k++) { r.scan(); seen.push(r.watch("Main.state")); }
  assert.deepEqual(seen.slice(0, 9), [0, 0, 0, 1, 1, 1, 2, 2, 0]);
});

test("FOR over an array of structures, function and user FB", () => {
  const r = rt(`TYPE ST_Part : STRUCT ok : BOOL; weight : REAL; END_STRUCT; END_TYPE
  FUNCTION FC_Scale : REAL
    VAR_INPUT raw : INT; lo, hi : REAL; END_VAR
    FC_Scale := lo + (hi - lo) * INT_TO_REAL(raw) / 27648.0;
  END_FUNCTION
  FUNCTION_BLOCK FB_Avg
    VAR_INPUT x : REAL; END_VAR
    VAR_OUTPUT y : REAL; END_VAR
    VAR buf : ARRAY[1..4] OF REAL; i : INT := 1; k : INT; s : REAL; END_VAR
    buf[i] := x; i := i MOD 4 + 1;
    s := 0.0;
    FOR k := 1 TO 4 DO s := s + buf[k]; END_FOR;
    y := s / 4.0;
  END_FUNCTION_BLOCK
  PROGRAM Main
    VAR parts : ARRAY[0..2] OF ST_Part := [(ok := TRUE, weight := 1.5), (ok := FALSE, weight := 2.0), (ok := TRUE, weight := 3.0)];
        i, good : INT; total, level : REAL; avg : FB_Avg; END_VAR
    good := 0; total := 0.0;
    FOR i := 0 TO 2 DO
      IF parts[i].ok THEN good := good + 1; total := total + parts[i].weight; END_IF;
    END_FOR;
    level := FC_Scale(raw := 13824, lo := 0.0, hi := 2.0);
    avg(x := level);
    count := good;
  END_PROGRAM`);
  r.scan();
  assert.equal(r.output("count"), 2);
  assert.equal(r.watch("Main.total"), Math.fround(4.5));
  assert.equal(r.watch("Main.level"), Math.fround(1.0));
  for (let k = 0; k < 4; k++) r.scan();
  assert.ok(Math.abs(r.watch("Main.avg.y") - 1.0) < 1e-6);
});

test("watchdog: an endless WHILE stops the PLC and switches the outputs off", () => {
  const r = rt(`PROGRAM Main
    VAR x : INT; END_VAR
    lamp := TRUE;
    WHILE start DO x := x + 1; END_WHILE;
  END_PROGRAM`, { budget: 5000 });
  r.scan();
  assert.equal(r.output("lamp"), true);
  press(r, "start", true);
  assert.ok(r.error && r.error.code === "watchdog", "watchdog trips");
  assert.match(r.error.message, /看门狗/);
  assert.equal(r.output("lamp"), false);
});

test("double coil: the last write wins (Chapter 4.6)", () => {
  const r = rt(`PROGRAM Main
    lamp := start;
    lamp := fwd;
  END_PROGRAM`);
  press(r, "start", true);
  assert.equal(r.output("lamp"), false);
});

test("input image: the program sees the inputs as they were at the start of the scan", () => {
  const r = rt(`PROGRAM Main
    VAR a, b : BOOL; END_VAR
    a := start; b := start;
    lamp := a = b;
  END_PROGRAM`);
  press(r, "start", true);
  assert.equal(r.output("lamp"), true);
});

test("input filter: a 5 ms glitch does not pass a 20 ms filter", () => {
  const r = rt(`PROGRAM Main lamp := start; END_PROGRAM`, { filter: 20, cycle: 5 });
  press(r, "start", true); press(r, "start", false, 3);
  assert.equal(r.output("lamp"), false);
  press(r, "start", true, 6);
  assert.equal(r.output("lamp"), true);
});

test("syntax and semantic errors give the line and a bilingual message", () => {
  assert.throws(() => P.compile(`PROGRAM Main\n VAR a : BOOL; END_VAR\n a := b;\nEND_PROGRAM`, { io: [] }),
    (e) => e.line === 3 && /没有声明/.test(e.message) && /not declared/.test(e.message));
  assert.throws(() => P.compile(`PROGRAM Main\n IF a THEN\nEND_PROGRAM`, { io: [] }), (e) => e.code === "syntax");
  assert.throws(() => P.compile(`PROGRAM Main VAR t : TON; END_VAR lamp := t(IN := TRUE); END_PROGRAM`, { io: IO }), /功能块/);
});

test("time literals and formatting", () => {
  assert.equal(P.parseTime("1m30s"), 90000);
  assert.equal(P.parseTime("1.5s"), 1500);
  assert.equal(P.fmtTime(90500), "T#1m30s500ms");
});

// ---------------- ladder
const C = (k, v) => ({ k, v });
test("ladder: seal-in with a parallel branch, stop as NC contact of a NO-wired button", () => {
  const rungs = [{
    comment: ["启停与自锁", "Start/stop with seal-in"],
    cells: [
      [C("NO", "start"), C("NC", "stopPb"), C("COIL", "motor")],
      [C("NO", "motor"), null, null],
    ],
    links: [[0, 1]],
  }];
  const io = IO.concat([{ name: "stopPb", addr: "%IX0.5", dir: "in" }]);
  const r = new P.Runtime({ io, decls: "", ladder: rungs, cycle: 10 });
  r.setInput("start", true); r.scan(); r.setInput("start", false); r.scan();
  assert.equal(r.output("motor"), true);
  r.setInput("stopPb", true); r.scan();
  assert.equal(r.output("motor"), false);
  r.setInput("stopPb", false); r.scan();
  assert.equal(r.output("motor"), false);
  const st = P.ladderToSt(rungs);
  assert.match(st, /motor := \(start OR motor\) AND NOT stopPb;/);
});

test("ladder: TON box and a counter, edge contact", () => {
  const rungs = [
    { cells: [[C("NO", "start"), { k: "FB", fb: "TON", inst: "t1", p: { PT: "T#50ms" } }, C("COIL", "lamp")]] },
    { cells: [[C("P", "fwd"), { k: "FB", fb: "CTU", inst: "c1", p: { R: "rev", PV: "2" } }, C("COIL", "motor")]] },
    { cells: [[C("WIRE"), { k: "ASSIGN", v: "count", x: "c1.CV" }]] },
  ];
  const r = new P.Runtime({ io: IO, decls: "VAR t1 : TON; c1 : CTU; END_VAR", ladder: rungs, cycle: 10 });
  r.setInput("start", true);
  for (let k = 0; k < 5; k++) r.scan();
  assert.equal(r.output("lamp"), false);
  r.scan();
  assert.equal(r.output("lamp"), true);
  for (let k = 0; k < 2; k++) { r.setInput("fwd", true); r.scan(); r.scan(); r.setInput("fwd", false); r.scan(); }
  assert.equal(r.output("count"), 2); assert.equal(r.output("motor"), true);
});

// ---------------- tests against a plant (〔TST〕)
const conveyorPlant = {
  // a conveyor: the motor moves a box 0 → 1 m at 0.5 m/s; the end sensor sees it at x ≥ 0.95
  reset(s, o) { s.x = 0; s.jam = !!(o.faults || {}).jam; },
  inputs(s) { return { fwd: s.x >= 0.95 }; },
  step(dt, out, s) { if (out.motor && !s.jam) s.x = Math.min(1, s.x + 0.5 * dt / 1000); },
  read(s, n) { return n === "x" ? s.x : undefined; },
};
const conveyorSt = `PROGRAM Main
  VAR jamT : TON; END_VAR
  motor := (start OR motor) AND NOT fwd AND NOT lamp;
  jamT(IN := motor, PT := T#3s);
  IF jamT.Q THEN lamp := TRUE; END_IF;   (* jam alarm *)
END_PROGRAM`;
test("runTest: the box reaches the end, and a jam raises the alarm", () => {
  const ok = P.runTest({ io: IO, st: conveyorSt, cycle: 10 }, conveyorPlant, {
    id: "run", steps: [{ set: { start: true } }, { wait: 50 }, { set: { start: false } },
      { until: { fwd: true }, within: 2500 }, { expect: { motor: false, lamp: false } }],
  });
  assert.equal(ok.ok, true, JSON.stringify(ok.failures));
  const jam = P.runTest({ io: IO, st: conveyorSt, cycle: 10 }, conveyorPlant, {
    id: "jam", faults: { jam: true }, steps: [{ set: { start: true } }, { wait: 50 }, { set: { start: false } },
      { until: { lamp: true }, within: 3500 }, { wait: 10 }, { expect: { motor: false } }],   // one scan later (the alarm is set after the motor rung)
  });
  assert.equal(jam.ok, true, JSON.stringify(jam.failures));
  const bad = P.runTest({ io: IO, st: conveyorSt, cycle: 10 }, conveyorPlant, {
    id: "wrong", steps: [{ set: { start: true } }, { until: { fwd: true }, within: 500 }],
  });
  assert.equal(bad.ok, false);
  assert.match(bad.failures[0].msg, /没有等到/);
});

test("PLCopen XML export is well formed and carries the POUs, types and I/O", () => {
  const src = `TYPE E_Light : (RED, GREEN); END_TYPE
FUNCTION_BLOCK FB_X
  VAR_INPUT a : BOOL; END_VAR
  VAR_OUTPUT q : BOOL; END_VAR
  q := NOT a;
END_FUNCTION_BLOCK
PROGRAM Main
  VAR x : FB_X; s : E_Light; t : TIME := T#2s; END_VAR
  x(a := start);
  lamp := x.q;
END_PROGRAM`;
  const xml = P.exportXml(src, { io: IO, name: "test", date: new Date("2026-10-03T00:00:00Z") });
  assert.match(xml, /<pou name="Main" pouType="program">/);
  assert.match(xml, /<pou name="FB_X" pouType="functionBlock">/);
  assert.match(xml, /address="%IX0.0"/);
  assert.match(xml, /<!\[CDATA\[  x\(a := start\);\n  lamp := x.q;\]\]>/);
  writeFileSync(process.env.PLC_XML_OUT || "/dev/null", xml);
});

// ---------------- SFC (Chapter 12)
const SFC_IO = [
  { name: "start", addr: "%IX0.0", dir: "in" }, { name: "up", addr: "%IX0.1", dir: "in" }, { name: "down", addr: "%IX0.2", dir: "in" },
  { name: "left", addr: "%IX0.3", dir: "in" }, { name: "right", addr: "%IX0.4", dir: "in" },
  { name: "lift", addr: "%QX0.0", dir: "out" }, { name: "lower", addr: "%QX0.1", dir: "out" }, { name: "moveR", addr: "%QX0.2", dir: "out" },
  { name: "grip", addr: "%QX0.3", dir: "out" }, { name: "lamp", addr: "%QX0.4", dir: "out" }, { name: "count", addr: "%QW2", dir: "out", type: "INT" },
];
test("SFC: sequence with S/R, P, D and L qualifiers, step flags and times, and a parallel branch", () => {
  const r = new P.Runtime({ io: SFC_IO, cycle: 10, st: `PROGRAM Main
    VAR n : INT; END_VAR
    INITIAL_STEP S0: END_STEP
    STEP S1: lower(N); grip(S); END_STEP
    STEP S2: lift(N); Count(P); END_STEP
    STEP S3: moveR(N); lamp(L, T#50ms); END_STEP
    STEP S4: grip(R); END_STEP
    STEP S5a: lamp(D, T#30ms); END_STEP
    STEP S5b: END_STEP
    STEP S6: END_STEP
    ACTION Count: n := n + 1; count := n; END_ACTION
    TRANSITION FROM S0 TO S1 := start; END_TRANSITION
    TRANSITION FROM S1 TO S2 := down; END_TRANSITION
    TRANSITION FROM S2 TO S3 := up; END_TRANSITION
    TRANSITION FROM S3 TO S4 := right; END_TRANSITION
    TRANSITION FROM S4 TO (S5a, S5b) := TRUE; END_TRANSITION
    TRANSITION FROM S5b TO S6 := S5b.T >= T#20ms; END_TRANSITION
    TRANSITION FROM (S5a, S6) TO S0 := S5a.T >= T#100ms; END_TRANSITION
  END_PROGRAM` });
  const step = (n = 1) => { for (let k = 0; k < n; k++) r.scan(); };
  step(2);
  assert.equal(r.watch("Main.S0.X"), true);
  r.setInput("start", true); step(2);
  assert.equal(r.output("lower"), true); assert.equal(r.output("grip"), true);
  r.setInput("start", false); r.setInput("down", true); step(2);
  assert.equal(r.output("lower"), false); assert.equal(r.output("lift"), true);
  step(5);
  assert.equal(r.output("count"), 1, "P action runs once");
  r.setInput("down", false); r.setInput("up", true); step(2);
  assert.equal(r.output("moveR"), true); assert.equal(r.output("lamp"), true, "L: on at first");
  step(6);
  assert.equal(r.output("lamp"), false, "L: off after 50 ms");
  assert.equal(r.output("grip"), true, "S keeps grip on");
  r.setInput("right", true); step(2);
  assert.equal(r.output("grip"), false, "R in S4");
  step(1);
  assert.equal(r.watch("Main.S5a.X"), true); assert.equal(r.watch("Main.S5b.X"), true);
  assert.equal(r.output("lamp"), false);
  step(4);
  assert.equal(r.output("lamp"), true, "D: on after 30 ms");
  assert.equal(r.watch("Main.S6.X"), true);
  step(12);
  assert.equal(r.watch("Main.S0.X"), true, "both branches joined back to S0");
  assert.equal(r.watch("Main.S5a.X"), false);
});
test("SFC errors: no initial step, unknown step, unknown action; a variable may still be called step", () => {
  assert.throws(() => P.compile(`PROGRAM Main STEP S1: END_STEP END_PROGRAM`, { io: [] }), /INITIAL_STEP/);
  assert.throws(() => P.compile(`PROGRAM Main INITIAL_STEP S0: END_STEP TRANSITION FROM S0 TO S9 := TRUE; END_TRANSITION END_PROGRAM`, { io: [] }), /S9/);
  assert.throws(() => P.compile(`PROGRAM Main INITIAL_STEP S0: foo(N); END_STEP END_PROGRAM`, { io: [] }), /foo/);
  P.compile(`PROGRAM Main VAR step : INT; END_VAR step := step + 1; END_PROGRAM`, { io: [] });
});
