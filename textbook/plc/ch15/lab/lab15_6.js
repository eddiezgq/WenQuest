// 实验 15.6 三层电梯（配 15.6 节）。三维虚拟电梯；CASE 或顺序功能图任选；四个测试与程序 15.6.1/15.6.2 相同。
const plant = WQPLANTS.elevator();
const call = (k) => [{ set: { ["S_C" + k]: true } }, { wait: 100 }, { set: { ["S_C" + k]: false } }];
// 参考程序（与书中程序 5.6.1 相同），只供自动试做（每个任务的 demo）用；书里已全文印出。
const SOL = { st: String.raw`(* 程序 15.6.1  三层电梯：用 CASE 写的状态机（呼梯登记、关门、运行、平层、开门） *)
TYPE E_Lift : (DOOR_OPEN, CLOSING, MOVING); END_TYPE

PROGRAM Main
  VAR
    state : E_Lift := DOOR_OPEN;
    call : ARRAY[1..3] OF BOOL;   (* 已登记的呼梯 *)
    floor : INT := 1;             (* 最近经过的楼层 *)
    target : INT;                 (* 要去的楼层，0 表示没有 *)
    tClose : TON;                 (* 关门时限：门被挡住就重新开门 *)
    atTarget : BOOL;
  END_VAR

  (* 登记呼梯；记住最近经过的楼层 *)
  IF S_C1 THEN call[1] := TRUE; END_IF;
  IF S_C2 THEN call[2] := TRUE; END_IF;
  IF S_C3 THEN call[3] := TRUE; END_IF;
  IF B_F1 THEN floor := 1; ELSIF B_F2 THEN floor := 2; ELSIF B_F3 THEN floor := 3; END_IF;
  atTarget := (target = 1 AND B_F1) OR (target = 2 AND B_F2) OR (target = 3 AND B_F3);

  CASE state OF
    DOOR_OPEN:                                   (* 停在某层、门开着 *)
      IF B_F1 OR B_F2 OR B_F3 THEN call[floor] := FALSE; END_IF;   (* 本层的呼梯随到随消 *)
      target := 0;
      IF call[1] THEN target := 1; ELSIF call[2] THEN target := 2; ELSIF call[3] THEN target := 3; END_IF;
      IF target <> 0 AND B_DoorOpen THEN state := CLOSING; END_IF;
    CLOSING:
      tClose(IN := TRUE, PT := T#4s);
      IF B_DoorClosed THEN tClose(IN := FALSE); state := MOVING;
      ELSIF tClose.Q THEN tClose(IN := FALSE); state := DOOR_OPEN; END_IF;
    MOVING:
      IF atTarget THEN call[target] := FALSE; state := DOOR_OPEN; END_IF;
  END_CASE;

  K_Up    := state = MOVING AND target > floor AND NOT atTarget AND S_TopLim AND B_DoorClosed;
  K_Down  := state = MOVING AND target < floor AND NOT atTarget AND S_LowLim AND B_DoorClosed AND NOT K_Up;
  Y_DoorOpen  := state = DOOR_OPEN AND NOT B_DoorOpen;
  Y_DoorClose := state = CLOSING AND NOT B_DoorClosed;
  H_C1 := call[1]; H_C2 := call[2]; H_C3 := call[3];
END_PROGRAM
` };
WQ.lab({
  title: ["实验 15.6 三层电梯", "Lab 15.6 A three-storey lift"],
  goal: ["把呼梯“记忆”和状态分开，用 CASE 或顺序功能图写出三层电梯的控制程序，通过四个测试；再注入传感器故障，解释电梯的表现。",
         "Keep the call memory apart from the state, write a three-storey lift program in CASE or SFC, pass four tests, then inject a sensor fault and explain what the lift does."],
  view: "plc",
  scenes: [{ id: "lift", name: ["三层电梯", "Three-storey lift"],
    problem: { title: ["车间问题：厂房里的三层货梯", "Shop-floor problem: a three-storey goods lift"],
               text: ["每层一个呼梯按钮，按下后指示灯亮，电梯到达该层、开门后熄灭。门没关到位绝不运行；门被挡住 4 s 关不上就重新开门。平层传感器只在楼层附近约 ±4 cm 内有信号，上下极限开关是常闭的。",
                      "One call button per floor; its lamp stays lit until the lift arrives and opens. Never move with the door not closed; if the door cannot close within 4 s, reopen. Level sensors are active only within about ±4 cm of a floor; the end limits are NC."] } }],
  params: [],
  plc: {
    io: plant.io, lang: "ST", langs: ["ST", "SFC"], cycle: 10,
    program: {
      st: `(* 实验 15.6：三层电梯（CASE 写法）。呼梯登记已写好，补全转移和输出 *)
TYPE E_Lift : (DOOR_OPEN, CLOSING, MOVING); END_TYPE

PROGRAM Main
  VAR
    state : E_Lift := DOOR_OPEN;
    call : ARRAY[1..3] OF BOOL;   (* 已登记的呼梯 *)
    floor : INT := 1;             (* 最近经过的楼层 *)
    target : INT;                 (* 要去的楼层，0 表示没有 *)
    tClose : TON;
    atTarget : BOOL;
  END_VAR

  IF S_C1 THEN call[1] := TRUE; END_IF;
  IF S_C2 THEN call[2] := TRUE; END_IF;
  IF S_C3 THEN call[3] := TRUE; END_IF;
  IF B_F1 THEN floor := 1; ELSIF B_F2 THEN floor := 2; ELSIF B_F3 THEN floor := 3; END_IF;
  atTarget := (target = 1 AND B_F1) OR (target = 2 AND B_F2) OR (target = 3 AND B_F3);

  CASE state OF
    DOOR_OPEN:
      (* 消除本层呼梯；选目标层；门开到位且有目标就去关门 *)
      ;
    CLOSING:
      (* 关到位去运行；4 s 关不上回到开门 *)
      ;
    MOVING:
      (* 到达目标层：消除呼梯，回到开门 *)
      ;
  END_CASE;

  K_Up := FALSE;          (* 别忘了：门关到位、极限开关 *)
  K_Down := FALSE;
  Y_DoorOpen := FALSE;
  Y_DoorClose := FALSE;
  H_C1 := call[1]; H_C2 := call[2]; H_C3 := call[3];
END_PROGRAM
`,
      sfc: `(* 实验 15.6：三层电梯（顺序功能图写法）。补全步、转移和动作 *)
PROGRAM Main
  VAR
    call : ARRAY[1..3] OF BOOL;
    floor : INT := 1;
    target : INT;
    atTarget : BOOL;
  END_VAR

  IF S_C1 THEN call[1] := TRUE; END_IF;
  IF S_C2 THEN call[2] := TRUE; END_IF;
  IF S_C3 THEN call[3] := TRUE; END_IF;
  IF B_F1 THEN floor := 1; ELSIF B_F2 THEN floor := 2; ELSIF B_F3 THEN floor := 3; END_IF;
  atTarget := (target = 1 AND B_F1) OR (target = 2 AND B_F2) OR (target = 3 AND B_F3);

  INITIAL_STEP Open: Y_DoorOpen(N); END_STEP
  STEP Closing: Y_DoorClose(N); END_STEP
  TRANSITION FROM Open TO Closing := FALSE; END_TRANSITION
  TRANSITION FROM Closing TO Open := Closing.T > T#4s; END_TRANSITION
END_PROGRAM
` },
    watch: ["Main.state", "Main.floor", "Main.target"],
    tests: [
      { id: "up", name: ["1 楼呼 3 楼：到 3 楼、开门、指示灯灭", "Call 3 from floor 1: arrive, open, lamp off"],
        steps: [{ wait: 2000 }, ...call(3), { until: { floor: 3 }, within: 12000 }, { until: { B_DoorOpen: true }, within: 3000 }, { expect: { H_C3: false, hazard: false } }] },
      { id: "down", name: ["3 楼回 2 楼", "From floor 3 back to 2"],
        steps: [{ wait: 2000 }, ...call(3), { until: { B_DoorOpen: true, floor: 3 }, within: 15000 }, ...call(2), { until: { floor: 2, B_DoorOpen: true }, within: 12000 }, { expect: { hazard: false } }] },
      { id: "jam", name: ["门卡住：绝不运行", "Door jammed: never moves"], faults: { doorJam: true },
        steps: [{ wait: 2000 }, ...call(2), { never: { K_Up: true }, during: 9000 }, { expect: { hazard: false } }] },
      { id: "safe", name: ["连续三个呼梯：25 s 内没有危险", "Three calls in a row: no hazard for 25 s"],
        steps: [{ wait: 1500 }, ...call(3), { wait: 300 }, ...call(1), { wait: 300 }, ...call(2), { never: { hazard: true }, during: 25000 }] },
    ],
  },
  plant,
  tasks: [
    { id: "up", test: "up", text: ["1 楼呼 3 楼，平层开门（测试通过）。", "Call 3 from floor 1, level and open the door (test passes)."], demo: { program: SOL, tests: true } },
    { id: "down", test: "down", text: ["3 楼回 2 楼（测试通过）。", "From 3 back to 2 (test passes)."], demo: { program: SOL, tests: true } },
    { id: "jam", test: "jam", text: ["门卡住时绝不运行（测试通过）。", "Never moves with a jammed door (test passes)."], demo: { program: SOL, tests: true } },
    { id: "safe", test: "safe", text: ["连续呼梯无危险动作（测试通过）。", "No hazard with calls in a row (test passes)."], demo: { program: SOL, tests: true } },
    { id: "review", review: true, text: ["程序检查没有错误。", "The program check finds no errors."], demo: { program: SOL, review: true } },
    { id: "f2", text: ["注入“2 楼平层传感器坏”，呼 2 楼，观察电梯怎样运行并解释。", "Inject 'floor-2 sensor dead', call floor 2, observe and explain."], demo: { program: SOL, faults: { f2dead: true }, panel: { S_C2: true }, run: true, wait: 25 } },   // the call stays pressed and the check gets time: no race on a busy machine
  ],
  check(api, s) {   // 2 楼传感器坏、2 楼的呼梯还亮着，轿厢却已经越过 2 楼：学生看到了这个现象
    if (s.f && s.f.f2dead && s.out && s.out.H_C2 && s.z > 4.0) api.done("f2");
  },
  think: ["注入 2 楼传感器故障后，电梯为什么没有冲顶？程序怎样才能发现这个故障？", "With the floor-2 sensor dead, why does the lift not hit the top? How could the program detect the fault?"],
  readouts(api, s) {
    return [[["轿厢高度", "Car height"], api.fmt(s.z || 0, 2) + " m"], [["速度", "Speed"], api.fmt(s.v || 0, 2) + " m/s"]];
  },
});
