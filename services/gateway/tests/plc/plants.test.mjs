// The virtual machines (labkit/plants.js) with reference programs: a correct program passes, a typical wrong one is caught.
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const P = require("../../app/production/labkit/plc.js");
const W = require("../../app/production/labkit/plants.js");

const ok = (r) => assert.equal(r.ok, true, JSON.stringify(r.failures));
const run = (plant, st, t) => P.runTest({ io: plant.io, st, cycle: 10 }, plant, t);

// ------------------------------------------------ traffic light
const TRAFFIC = `PROGRAM Main
  VAR step : INT; t : TON; flash : TON; blink : BOOL; END_VAR
  IF S_Night THEN
    flash(IN := NOT flash.Q, PT := T#500ms);
    IF flash.Q THEN blink := NOT blink; END_IF;
    NS_R := FALSE; NS_G := FALSE; EW_R := FALSE; EW_G := FALSE; NS_Y := blink; EW_Y := blink; P_Wait := FALSE;
    step := 0;
  ELSE
    CASE step OF
      0: t(IN := TRUE, PT := T#5s);    (* NS green *)
      1: t(IN := TRUE, PT := T#2s);    (* NS yellow *)
      2: t(IN := TRUE, PT := T#1s);    (* all red *)
      3: t(IN := TRUE, PT := T#5s);    (* EW green *)
      4: t(IN := TRUE, PT := T#2s);    (* EW yellow *)
      5: t(IN := TRUE, PT := T#1s);    (* all red *)
    END_CASE;
    IF t.Q THEN t(IN := FALSE); step := (step + 1) MOD 6; END_IF;
    NS_G := step = 0; NS_Y := step = 1; NS_R := step >= 2;
    EW_G := step = 3; EW_Y := step = 4; EW_R := step <= 2 OR step = 5;
    P_Wait := S_Ped;
  END_IF;
END_PROGRAM`;
test("traffic light: a full cycle without conflict; night mode flashes yellow only", () => {
  const plant = W.traffic();
  ok(run(plant, TRAFFIC, { id: "cycle", steps: [{ until: { EW_G: true }, within: 9000 }, { until: { NS_G: true }, within: 9000 }, { never: { hazard: true }, during: 30000 }] }));
  ok(run(plant, TRAFFIC, { id: "night", steps: [{ set: { S_Night: true } }, { until: { NS_Y: true }, within: 1500 }, { never: { NS_G: true }, during: 5000 }, { never: { EW_G: true }, during: 5000 }] }));
  const bad = TRAFFIC.replace("EW_G := step = 3;", "EW_G := step = 3 OR step = 0;");
  const r = run(plant, bad, { id: "cycle", steps: [{ never: { hazard: true }, during: 20000 }] });
  assert.equal(r.ok, false);
});

// ------------------------------------------------ elevator
const ELEVATOR = `PROGRAM Main
  VAR call : ARRAY[1..3] OF BOOL; floor : INT := 1; target : INT; tDoor : TON; state : INT; END_VAR
  IF S_C1 THEN call[1] := TRUE; END_IF; IF S_C2 THEN call[2] := TRUE; END_IF; IF S_C3 THEN call[3] := TRUE; END_IF;
  IF B_F1 THEN floor := 1; ELSIF B_F2 THEN floor := 2; ELSIF B_F3 THEN floor := 3; END_IF;
  CASE state OF
    0: (* idle, door open *)
       Y_DoorOpen := NOT B_DoorOpen; Y_DoorClose := FALSE; K_Up := FALSE; K_Down := FALSE;
       call[floor] := call[floor] AND NOT (B_F1 OR B_F2 OR B_F3);
       target := 0;
       IF call[1] THEN target := 1; ELSIF call[2] THEN target := 2; ELSIF call[3] THEN target := 3; END_IF;
       IF target <> 0 AND B_DoorOpen THEN state := 1; END_IF;
    1: (* close the door *)
       Y_DoorOpen := FALSE; Y_DoorClose := TRUE;
       tDoor(IN := TRUE, PT := T#4s);
       IF B_DoorClosed THEN Y_DoorClose := FALSE; tDoor(IN := FALSE); state := 2;
       ELSIF tDoor.Q THEN tDoor(IN := FALSE); state := 0; END_IF;     (* door blocked: open again *)
    2: (* travel *)
       K_Up := target > floor AND S_TopLim AND B_DoorClosed;
       K_Down := target < floor AND S_LowLim AND B_DoorClosed AND NOT K_Up;
       IF (target = 1 AND B_F1) OR (target = 2 AND B_F2) OR (target = 3 AND B_F3) THEN
         K_Up := FALSE; K_Down := FALSE; call[target] := FALSE; state := 0;
       END_IF;
  END_CASE;
  H_C1 := call[1]; H_C2 := call[2]; H_C3 := call[3];
END_PROGRAM`;
test("elevator: a call from floor 3 brings the car up, levels, opens; a dead floor sensor is caught by the limit", () => {
  const plant = W.elevator();
  ok(run(plant, ELEVATOR, { id: "up", steps: [{ wait: 2000 }, { set: { S_C3: true } }, { wait: 100 }, { set: { S_C3: false } },
    { until: { floor: 3 }, within: 12000 }, { until: { B_DoorOpen: true }, within: 3000 }, { expect: { H_C3: false, hazard: false } }] }));
  ok(run(plant, ELEVATOR, { id: "down", steps: [{ wait: 2000 }, { set: { S_C3: true } }, { wait: 100 }, { set: { S_C3: false } }, { until: { B_DoorOpen: true, floor: 3 }, within: 15000 },
    { set: { S_C2: true } }, { wait: 100 }, { set: { S_C2: false } }, { until: { floor: 2, B_DoorOpen: true }, within: 12000 }, { expect: { hazard: false } }] }));
  // the floor-2 sensor is dead: the car passes floor 2 and the top limit keeps it from overtravelling
  const dead = run(plant, ELEVATOR, { id: "dead", faults: { f2dead: true }, steps: [{ wait: 2000 }, { set: { S_C2: true } }, { wait: 100 }, { set: { S_C2: false } }, { wait: 12000 }] });
  assert.equal(dead.ok, true);
  // a program without the door interlock moves with the door open: hazard
  const bad = ELEVATOR.replace("K_Up := target > floor AND S_TopLim AND B_DoorClosed;", "K_Up := target > floor AND S_TopLim;").replace("IF B_DoorClosed THEN Y_DoorClose", "IF TRUE THEN Y_DoorClose");
  const r = run(plant, bad, { id: "door", steps: [{ wait: 2000 }, { set: { S_C3: true } }, { wait: 100 }, { set: { S_C3: false } }, { never: { hazard: true }, during: 8000 }] });
  assert.equal(r.ok, false);
});

// ------------------------------------------------ sorter
const SORTER = `PROGRAM Main
  VAR kind : ARRAY[0..31] OF INT; gone : ARRAY[0..31] OF BOOL; nIn, s1, s2, s3 : INT;
      rIn, r1, r2, r3 : R_TRIG; run : BOOL; k : INT; push1, push2, push3 : TP; END_VAR
  run := (S_Start OR run) AND S_Stop;
  M_Belt := run; H_Run := run;
  rIn(CLK := B_Insp);
  IF rIn.Q THEN   (* 1 metal, 2 red, 3 blue, 9 reject (tall) *)
    IF B_Tall THEN k := 9; ELSIF B_Metal THEN k := 1; ELSIF B_Red THEN k := 2; ELSE k := 3; END_IF;
    kind[nIn MOD 32] := k; gone[nIn MOD 32] := FALSE; nIn := nIn + 1;
  END_IF;
  r1(CLK := B_P1);
  IF r1.Q AND s1 < nIn THEN
    IF kind[s1 MOD 32] = 1 THEN gone[s1 MOD 32] := TRUE; push1(IN := TRUE, PT := T#400ms); END_IF;
    s1 := s1 + 1;
  END_IF;
  r2(CLK := B_P2);
  IF r2.Q THEN
    WHILE s2 < nIn AND gone[s2 MOD 32] AND s2 < s1 DO s2 := s2 + 1; END_WHILE;
    IF s2 < nIn THEN IF kind[s2 MOD 32] = 2 THEN gone[s2 MOD 32] := TRUE; push2(IN := TRUE, PT := T#400ms); END_IF; s2 := s2 + 1; END_IF;
  END_IF;
  r3(CLK := B_P3);
  IF r3.Q THEN
    WHILE s3 < nIn AND gone[s3 MOD 32] AND s3 < s2 DO s3 := s3 + 1; END_WHILE;
    IF s3 < nIn THEN IF kind[s3 MOD 32] = 3 THEN gone[s3 MOD 32] := TRUE; push3(IN := TRUE, PT := T#400ms); END_IF; s3 := s3 + 1; END_IF;
  END_IF;
  push1(IN := FALSE); push2(IN := FALSE); push3(IN := FALSE);
  Y1 := push1.Q; Y2 := push2.Q; Y3 := push3.Q;
END_PROGRAM`;
test("sorter: eight parts end up in the right bins with a FIFO tracking program; a stuck pusher is visible", () => {
  const plant = W.sorter();
  const t = { id: "sort", steps: [{ set: { S_Stop: true } }, { wait: 50 }, { set: { S_Start: true } }, { wait: 100 }, { set: { S_Start: false } },
    { until: { done: true }, within: 60000 }, { expect: { wrong: 0, bin1: 2, bin2: 3, bin3: 2, rejects: 1 } }] };
  ok(run(plant, SORTER, t));
  const stuck = run(plant, SORTER, Object.assign({}, t, { faults: { y2stuck: true } }));
  assert.equal(stuck.ok, false);
  assert.match(stuck.failures.map((f) => f.msg).join(" "), /wrong/);
  // without tracking (push when the sensor sees "red" at the pusher… it can't): pushing every part at P1 is wrong
  const naive = SORTER.replace("IF kind[s1 MOD 32] = 1 THEN", "IF TRUE THEN");
  assert.equal(run(plant, naive, t).ok, false);
});

// ------------------------------------------------ press-fit station
const PRESS = `PROGRAM Main
  VAR state : INT; tHands : TON; force : REAL; peak : REAL; END_VAR
  force := INT_TO_REAL(AI_Force) * 10.0 / 27648.0;
  IF NOT S_EStop THEN state := 9; END_IF;
  CASE state OF
    0: Y_Clamp := FALSE; Y_PressDown := FALSE; Y_PressUp := NOT B_PressUp;
       tHands(IN := S_Hand1 OR S_Hand2, PT := T#500ms);
       IF B_Part AND S_Hand1 AND S_Hand2 AND NOT tHands.Q AND S_LC AND B_PressUp THEN H_OK := FALSE; H_NOK := FALSE; peak := 0.0; state := 1; END_IF;
    1: Y_Clamp := TRUE;
       IF B_Clamped THEN state := 2; END_IF;
    2: Y_PressUp := FALSE; Y_PressDown := S_Hand1 AND S_Hand2 AND S_LC;
       IF force > peak THEN peak := force; END_IF;
       IF NOT (S_Hand1 AND S_Hand2 AND S_LC) OR force > 8.0 THEN Y_PressDown := FALSE; state := 3;
       ELSIF B_PressDown THEN
         H_OK := peak >= 4.0 AND peak <= 7.0; H_NOK := NOT H_OK; Y_PressDown := FALSE; state := 3;
       END_IF;
    3: Y_PressDown := FALSE; Y_PressUp := TRUE;
       IF B_PressUp THEN Y_PressUp := FALSE; Y_Clamp := FALSE; IF NOT (H_OK OR H_NOK) THEN H_NOK := TRUE; END_IF; state := 0; END_IF;
    9: (* emergency stop: the ram stops where it is; reset after the e-stop is released *)
       Y_PressDown := FALSE; Y_PressUp := FALSE;
       IF S_EStop AND S_Reset THEN state := 3; END_IF;
  END_CASE;
END_PROGRAM`;
const cycle = (extra = []) => ({ steps: [{ set: { S_LC: true, B_Part: true } }, { wait: 100 }, { set: { S_Hand1: true, S_Hand2: true } },
  ...extra, { until: { B_PressUp: true, Y_Clamp: false }, within: 8000 }] });
test("press-fit: good, tight and loose parts; the light curtain stops the ram", () => {
  const plant = W.press();
  ok(run(plant, PRESS, Object.assign({ id: "good" }, cycle([{ until: { B_PressDown: true }, within: 5000 }]))));
  const g = run(plant, PRESS, Object.assign({ id: "good2" }, cycle([{ until: { B_PressDown: true }, within: 5000 }, { wait: 50 }, { expect: { H_OK: true, H_NOK: false } }])));
  ok(g);
  const tight = run(plant, PRESS, Object.assign({ id: "tight", faults: { tight: true } }, cycle([{ wait: 4000 }, { expect: { H_OK: false } }])));
  ok(tight);
  const loose = run(plant, PRESS, Object.assign({ id: "loose", faults: { loose: true } }, cycle([{ until: { B_PressDown: true }, within: 5000 }, { wait: 50 }, { expect: { H_NOK: true } }])));
  ok(loose);
  // the curtain is broken half-way: the ram must not keep going down, no hazard
  ok(run(plant, PRESS, Object.assign({ id: "lc" }, cycle([{ wait: 1500 }, { set: { S_LC: false } }, { wait: 30 }, { expect: { Y_PressDown: false, hazard: false } }, { set: { S_LC: true } }]))));
  // a program that ignores the curtain is caught
  const bad = PRESS.replace("Y_PressDown := S_Hand1 AND S_Hand2 AND S_LC;", "Y_PressDown := TRUE;").replace("IF NOT (S_Hand1 AND S_Hand2 AND S_LC) OR force > 8.0", "IF force > 8.0");
  const r = run(plant, bad, Object.assign({ id: "lc" }, cycle([{ wait: 1500 }, { set: { S_LC: false } }, { never: { hazard: true }, during: 500 }])));
  assert.equal(r.ok, false);
});

test("press-fit panel: a latching e-stop and one button holding both hand buttons (usable with a mouse)", () => {
  const pr = W.press();
  const est = pr.panel.find((p) => p.name === "S_EStop");
  assert.equal(est.kind, "estop");
  const both = pr.panel.find((p) => p.names);
  assert.deepEqual(both.names, ["S_Hand1", "S_Hand2"]);
  const io = new Set(pr.io.map((x) => x.name));
  for (const p of pr.panel) for (const n of p.names || [p.name]) assert.ok(io.has(n), n);
});

// ------------------------------------------------ feed conveyor (Part I project)
test("feed conveyor: a bar travels to the end and the belt stops; stop, e-stop, overload, jam; operator actions reach the machine", () => {
  const fs = require("node:fs");
  const st = fs.readFileSync(new URL("../../../../textbook/plc/ch01/code/p1_1_1.st", import.meta.url), "utf8");
  const cv = W.conveyor();
  const start = [{ set: { S1_Start: true } }, { wait: 100 }, { set: { S1_Start: false } }];
  ok(run(cv, st, { id: "run", steps: [...start, { until: { B2_End: true }, within: 15000 }, { wait: 50 }, { expect: { KM1_Run: false, H2_Fault: false, atEnd: true } },
    { set: { TakePart: true } }, { wait: 50 }, { set: { TakePart: false, PutPart: true } }, { wait: 50 }, { set: { PutPart: false } }, { wait: 20 },
    { expect: { delivered: 1, B1_Entry: true } }, ...start, { until: { B2_End: true }, within: 15000 }] }));
  ok(run(cv, st, { id: "stop", steps: [...start, { wait: 2000 }, { set: { S2_Stop: false } }, { wait: 20 }, { expect: { KM1_Run: false } },
    { set: { S2_Stop: true } }, { never: { KM1_Run: true }, during: 1000 }] }));
  ok(run(cv, st, { id: "estop", steps: [...start, { wait: 2000 }, { set: { S0_EStop: false } }, { wait: 20 }, { expect: { KM1_Run: false, hazard: false } }] }));
  ok(run(cv, st, { id: "jam", faults: { jam: true }, steps: [...start, { never: { H2_Fault: true }, during: 19000 }, { until: { H2_Fault: true }, within: 2000 },
    { wait: 20 }, { expect: { KM1_Run: false } }, ...start, { wait: 50 }, { expect: { H2_Fault: false, KM1_Run: true } }] }));   // start resets the alarm and runs again
  ok(run(cv, st, { id: "overload", faults: { overload: true }, steps: [...start, { wait: 50 }, { expect: { KM1_Run: false, H2_Fault: true } }] }));
  // a program without the end sensor runs the bar into the end stop forever
  const naive = st.replace(" AND NOT B2_End AND NOT jammed;", " AND NOT jammed;");
  assert.equal(run(cv, naive, { id: "run", steps: [...start, { until: { B2_End: true }, within: 15000 }, { wait: 50 }, { expect: { KM1_Run: false } }] }).ok, false);
  assert.ok(!P.review({ st }, cv.io).some((x) => x.level === "error"));
});
