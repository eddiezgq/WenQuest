// 实验 15.3 压装工位的顺序控制（配 15.3 节）。三维虚拟压装工位，I/O 与表 15.1.1 相同；五个测试对应控制要求说明的五条要求。
const plant = WQPLANTS.press();
const LOAD = { set: { B_Part: true, S_LC: true, S_EStop: true } };
const HANDS = { set: { S_Hand1: true, S_Hand2: true } };
const FREE = { set: { S_Hand1: false, S_Hand2: false } };
const RESET = [{ set: { S_Reset: true } }, { wait: 50 }, { set: { S_Reset: false } }];
// 每个测试先拨到“自动”、按一次复位、等就绪灯：15.3 节的程序不用这两个信号，照样通过；加上 15.4–15.5 节的操作方式后也照样能测。
const AUTO = [{ set: { S_Auto: true, S_EStop: true, S_LC: true } }, { wait: 100 }, ...RESET, { until: { H_Ready: true }, within: 6000 }];
const cycle = (...mid) => [...AUTO, LOAD, { wait: 200 }, HANDS, ...mid, { until: { B_PressUp: true, Y_Clamp: false }, within: 8000 }, FREE, { until: { B_Unclamped: true }, within: 2000 }];
// 参考程序（与书中程序 5.5.1 相同），只供自动试做（每个任务的 demo）用；书里已全文印出。
const SOL = { st: String.raw`(* 程序 15.5.1  压装工位：加上异常处理——动作超时、传感器冲突、急停与恢复 *)
TYPE E_Press : (INIT, HOMING, IDLE, CLAMPING, PRESSING, RETURNING, UNCLAMPING, FAULT, ESTOP); END_TYPE

PROGRAM Main
  VAR
    state : E_Press := INIT;
    prev : E_Press := INIT;    (* 上一次扫描的状态：状态一变，计时重新开始 *)
    tState : TON;              (* 本状态已经停留的时间 *)
    maxTime : TIME;            (* 本状态允许停留的最长时间 *)
    faultCode : INT;               (* 故障代码：0 无；1 夹紧超时；2 压装超时；3 回程超时；4 松开超时；5 回原点超时；9 传感器冲突 *)
    clampHold : BOOL;          (* 进入故障或急停时夹具是否夹着：保持原样 *)
    auto, go, jog : BOOL;
    rStep, rReset : R_TRIG;
    tTwoHand : TON;
    force, peak : REAL;
    resOk, resNok : BOOL;
  END_VAR

  force := INT_TO_REAL(AI_Force) * 10.0 / 27648.0;
  tTwoHand(IN := S_Hand1 OR S_Hand2, PT := T#500ms);
  rStep(CLK := S_Step);
  rReset(CLK := S_Reset);
  auto := S_Auto;
  go := auto OR rStep.Q;

  (* 1. 急停与传感器冲突：任何状态下都优先 *)
  IF NOT S_EStop AND state <> ESTOP THEN
    clampHold := Y_Clamp; state := ESTOP;
  ELSIF ((B_Clamped AND B_Unclamped) OR (B_PressUp AND B_PressDown)) AND state <> FAULT AND state <> ESTOP THEN
    clampHold := Y_Clamp; faultCode := 9; state := FAULT;
  END_IF;

  (* 2. 状态时限：自动方式和回原点时才计时（单步时等的是人） *)
  CASE state OF
    CLAMPING, UNCLAMPING: maxTime := T#1s;
    PRESSING: maxTime := T#4s;
    RETURNING: maxTime := T#5s;
    HOMING: maxTime := T#5s;
  ELSE
    maxTime := T#1h;
  END_CASE;
  tState(IN := state = prev AND (auto OR state = HOMING), PT := maxTime);
  prev := state;

  (* 3. 转移 *)
  CASE state OF
    INIT:
      IF rReset.Q THEN state := HOMING; END_IF;
    HOMING:
      IF B_PressUp AND B_Unclamped THEN state := IDLE;
      ELSIF tState.Q THEN clampHold := FALSE; faultCode := 5; state := FAULT; END_IF;
    IDLE:
      IF rReset.Q THEN
        state := HOMING;
      ELSIF B_Part AND B_PressUp AND B_Unclamped AND S_LC
            AND ((auto AND S_Hand1 AND S_Hand2 AND NOT tTwoHand.Q) OR (NOT auto AND rStep.Q)) THEN
        resOk := FALSE; resNok := FALSE; peak := 0.0;
        state := CLAMPING;
      ELSIF NOT auto AND (S_JogClamp OR S_JogDown OR S_JogUp) THEN
        state := INIT;                    (* 点动过：位置不再确定，再启动前要回原点 *)
      END_IF;
    CLAMPING:
      IF go AND B_Clamped THEN state := PRESSING;
      ELSIF tState.Q THEN clampHold := TRUE; faultCode := 1; state := FAULT; END_IF;
    PRESSING:
      peak := MAX(peak, force);
      IF force > 8.0 THEN
        resNok := TRUE; state := RETURNING;
      ELSIF go AND B_PressDown THEN
        resOk := peak >= 4.0 AND peak <= 7.0; resNok := NOT resOk;
        state := RETURNING;
      ELSIF auto AND NOT (S_Hand1 AND S_Hand2 AND S_LC) THEN
        resNok := TRUE; state := RETURNING;
      ELSIF tState.Q THEN clampHold := TRUE; faultCode := 2; state := FAULT; END_IF;
    RETURNING:
      IF go AND B_PressUp THEN state := UNCLAMPING;
      ELSIF tState.Q THEN clampHold := TRUE; faultCode := 3; state := FAULT; END_IF;
    UNCLAMPING:
      IF go AND B_Unclamped THEN state := IDLE;
      ELSIF tState.Q THEN clampHold := FALSE; faultCode := 4; state := FAULT; END_IF;
    FAULT:                                (* 停在原地，等人看清原因、按复位 *)
      IF rReset.Q AND S_EStop AND NOT ((B_Clamped AND B_Unclamped) OR (B_PressUp AND B_PressDown)) THEN
        faultCode := 0; state := HOMING;
      END_IF;
    ESTOP:                                (* 急停松开后也不自己动，按复位才回原点 *)
      IF S_EStop AND rReset.Q THEN state := HOMING; END_IF;
  END_CASE;

  (* 4. 输出 *)
  jog := NOT auto AND (state = IDLE OR state = INIT OR state = FAULT);   (* 故障时允许点动，联锁照样有效 *)
  Y_Clamp     := state = CLAMPING OR state = PRESSING OR state = RETURNING OR (jog AND S_JogClamp)
                 OR ((state = FAULT OR state = ESTOP) AND clampHold);
  Y_PressDown := ((state = PRESSING AND S_Hand1 AND S_Hand2) OR (jog AND S_JogDown AND B_Clamped)) AND S_LC AND S_EStop;
  Y_PressUp   := (state = RETURNING OR (state = HOMING AND NOT B_PressUp) OR (jog AND S_JogUp))
                 AND S_EStop AND NOT Y_PressDown;
  H_OK    := resOk;
  H_NOK   := resNok;
  H_Ready := state = IDLE;
  H_Fault := state = FAULT OR state = ESTOP;
END_PROGRAM
` };
WQ.lab({
  title: ["实验 15.3 压装工位的顺序控制", "Lab 15.3 Sequential control of the press-fit station"],
  goal: ["用状态机设计法写出压装工位的自动循环程序：列状态、写转移、写输出，再用五个测试证明它满足控制要求。",
         "Write the press-fit station's automatic cycle with the state-machine method (states, transitions, outputs) and prove it with five tests."],
  view: "plc",
  scenes: [{ id: "press", name: ["轴承压装工位", "Bearing press-fit station"],
    problem: { title: ["车间问题：把轴承压进减速器盖，压好了亮绿灯", "Shop-floor problem: press the bearing into the cover and light green when it is good"],
               text: ["按 15.1 节的控制要求说明：放上工件，0.5 s 内双手启动，夹紧，压头下行（双手一直按着、光幕无遮挡），压到底按最大压装力 4.0–7.0 kN 判定，回程，松开。",
                      "As specified in Section 15.1: load the part, start with both hands within 0.5 s, clamp, ram down (both hands held, curtain clear), judge by the peak force 4.0–7.0 kN at the bottom, return, unclamp."] } }],
  params: [],
  plc: {
    io: plant.io, lang: "ST", langs: ["ST", "SFC"], cycle: 10,
    program: { st: `(* 实验 15.3：压装工位的状态机。按 15.3.3 节的五步补全 *)
TYPE E_Press : (IDLE, CLAMPING, PRESSING, RETURNING, UNCLAMPING); END_TYPE

PROGRAM Main
  VAR
    state : E_Press := IDLE;
    tTwoHand : TON;
    force, peak : REAL;
    resOk, resNok : BOOL;
  END_VAR

  force := INT_TO_REAL(AI_Force) * 10.0 / 27648.0;
  tTwoHand(IN := S_Hand1 OR S_Hand2, PT := T#500ms);

  (* 1. 转移 *)
  CASE state OF
    IDLE:
      (* 在这里写启动条件 *)
      ;
    CLAMPING:
      ;
    PRESSING:
      ;
    RETURNING:
      ;
    UNCLAMPING:
      ;
  END_CASE;

  (* 2. 输出：每个输出只写一次 *)
  Y_Clamp := FALSE;
  Y_PressDown := FALSE;
  Y_PressUp := FALSE;
  H_OK := resOk;
  H_NOK := resNok;
  H_Ready := state = IDLE AND B_PressUp AND B_Unclamped;
END_PROGRAM
` },
    watch: ["Main.state", "Main.peak"],
    tests: [
      { id: "good", name: ["合格件：压到底、亮绿灯", "Good part: pressed home, green lamp"], steps: [...cycle({ until: { B_PressDown: true }, within: 5000 }), { expect: { H_OK: true, H_NOK: false } }] },
      { id: "loose", name: ["过盈太小：判不合格", "Interference too small: NOK"], faults: { loose: true }, steps: [...cycle(), { expect: { H_OK: false, H_NOK: true } }] },
      { id: "tight", name: ["过盈太大：过载中止、判不合格", "Interference too large: overload, NOK"], faults: { tight: true }, steps: [...cycle(), { expect: { H_NOK: true } }] },
      { id: "curtain", name: ["压装途中挡光：压头立即停下、回程、判不合格", "Curtain broken while pressing: stop at once, return, NOK"],
        steps: [...AUTO, LOAD, { wait: 200 }, HANDS, { wait: 1500 }, { set: { S_LC: false } }, { wait: 20 }, { expect: { Y_PressDown: false, hazard: false } },
                { set: { S_LC: true } }, { until: { B_PressUp: true, Y_Clamp: false }, within: 6000 }, { expect: { H_NOK: true } }] },
      { id: "twohand", name: ["双手按钮相隔 0.8 s：不启动；两手松开再同时按：启动", "Buttons 0.8 s apart: no start; release both, press together: start"],
        steps: [...AUTO, LOAD, { wait: 200 }, { set: { S_Hand1: true } }, { wait: 800 }, { set: { S_Hand2: true } }, { never: { Y_Clamp: true }, during: 1500 },
                FREE, { wait: 300 }, HANDS, { until: { Y_Clamp: true }, within: 300 }] },
      // 以下四个测试检验 15.5、15.7 节的异常处理（工程任务 TS-15-1 用），15.3 节的程序通不过是正常的
      { id: "clamp_timeout", name: ["（15.5 节）夹紧传感器断线：报故障、不下行，复位后回原点", "(15.5) Clamp sensor wire broken: fault, no descent, reset homes"], faults: { clampWire: true },
        steps: [...AUTO, LOAD, { wait: 200 }, HANDS, { until: { H_Fault: true }, within: 1500 }, { never: { Y_PressDown: true }, during: 1000 }, FREE, ...RESET, { until: { H_Ready: true }, within: 3000 }] },
      { id: "estop", name: ["（15.5 节）压装中急停：立即停；松开不动，复位后回原点", "(15.5) E-stop while pressing: stop; no move on release; reset homes"],
        steps: [...AUTO, LOAD, { wait: 200 }, HANDS, { wait: 1500 }, { set: { S_EStop: false } }, { wait: 20 },
                { expect: { Y_PressDown: false, Y_PressUp: false, H_Fault: true, hazard: false } }, { wait: 500 }, { set: { S_EStop: true } },
                { never: { Y_PressUp: true }, during: 1000 }, FREE, ...RESET, { until: { H_Ready: true }, within: 4000 }, { expect: { hazard: false } }] },
      { id: "conflict", name: ["（15.5 节）上位开关粘连：判冲突、停住", "(15.5) Upper switch stuck: conflict, stop"], faults: { upStuck: true },
        steps: [...AUTO, LOAD, { wait: 200 }, HANDS, { until: { H_Fault: true }, within: 5000 }, { expect: { Y_PressDown: false } }, { never: { Y_PressUp: true }, during: 500 }] },
      { id: "power", name: ["（15.7 节）回程中断电 0.5 s：来电后不动", "(15.7) 0.5 s power loss while returning: no move after"],
        steps: [...AUTO, LOAD, { wait: 200 }, HANDS, { until: { B_PressDown: true }, within: 5000 }, { wait: 600 }, { power: 500 },
                { never: { Y_PressUp: true }, during: 2000 }, { expect: { H_Ready: false } }] },
    ],
  },
  plant,
  tasks: [
    { id: "good", test: "good", text: ["合格件压到底亮绿灯（测试“合格件”通过）。", "A good part lights green (test 'good part' passes)."], demo: { program: SOL, tests: true } },
    { id: "nok", test: "loose", text: ["过盈不合适的件判不合格（测试“过盈太小”通过）。", "A bad fit is NOK (test 'too small' passes)."], demo: { program: SOL, tests: true } },
    { id: "curtain", test: "curtain", text: ["挡光时压头立即停下（测试“挡光”通过）。", "The ram stops at once when the curtain is broken (curtain test passes)."], demo: { program: SOL, tests: true } },
    { id: "twohand", test: "twohand", text: ["双手按钮相隔太久不启动（测试“双手”通过）。", "Hand buttons too far apart do not start (two-hand test passes)."], demo: { program: SOL, tests: true } },
    { id: "review", review: true, text: ["程序检查没有错误（没有双线圈，安全输入都用到了）。", "The program check finds no errors (no double coils, all safety inputs used)."], demo: { program: SOL, review: true } },
  ],
  think: ["把下行阀改成纯摩尔型（Y_PressDown := state = PRESSING;），五个测试照样通过。为什么测试抓不到这个隐患？怎样的程序修改会让它变成真的危险？",
          "Make ram down a pure Moore output (Y_PressDown := state = PRESSING;): all five tests still pass. Why can the tests not catch this weakness, and what later change would make it a real hazard?"],
  readouts(api, s) {
    return [[["压装力", "Force"], api.fmt(s.force || 0, 2) + " kN"], [["压头位置", "Ram travel"], api.fmt((s.ram || 0) * 1000, 1) + " mm"],
            [["本件最大力", "Peak force"], api.fmt(s.peak || 0, 2) + " kN"]];
  },
});
