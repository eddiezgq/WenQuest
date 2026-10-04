(* 程序 15.4.1  压装工位：自动、手动（点动）、单步与回原点 *)
TYPE E_Press : (INIT, HOMING, IDLE, CLAMPING, PRESSING, RETURNING, UNCLAMPING); END_TYPE

PROGRAM Main
  VAR
    state : E_Press := INIT;   (* 上电时位置未知 *)
    auto : BOOL;               (* 自动方式（方式开关在“自动”） *)
    go : BOOL;                 (* 本次扫描允许转移：自动方式下总允许，手动方式下按一次“单步”允许一次 *)
    jog : BOOL;                (* 允许点动：手动方式且停在原点 *)
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

  CASE state OF
    INIT:                                 (* 等操作员按复位，绝不自己动 *)
      IF rReset.Q AND S_EStop THEN state := HOMING; END_IF;
    HOMING:                               (* 回原点：压头回上位、夹具松开 *)
      IF B_PressUp AND B_Unclamped THEN state := IDLE; END_IF;
    IDLE:
      IF rReset.Q THEN
        state := HOMING;
      ELSIF B_Part AND B_PressUp AND B_Unclamped AND S_LC AND S_EStop
            AND ((auto AND S_Hand1 AND S_Hand2 AND NOT tTwoHand.Q) OR (NOT auto AND rStep.Q)) THEN
        resOk := FALSE; resNok := FALSE; peak := 0.0;
        state := CLAMPING;
      ELSIF NOT auto AND (S_JogClamp OR S_JogDown OR S_JogUp) THEN
        state := INIT;                    (* 点动过：位置不再确定，再启动前要回原点 *)
      END_IF;
    CLAMPING:
      IF go AND B_Clamped THEN state := PRESSING; END_IF;
    PRESSING:
      peak := MAX(peak, force);
      IF force > 8.0 THEN                           (* 过载：任何方式下都立即回程 *)
        resNok := TRUE; state := RETURNING;
      ELSIF go AND B_PressDown THEN
        resOk := peak >= 4.0 AND peak <= 7.0; resNok := NOT resOk;
        state := RETURNING;
      ELSIF auto AND NOT (S_Hand1 AND S_Hand2 AND S_LC) THEN
        resNok := TRUE; state := RETURNING;         (* 自动方式松手或挡光：中止；单步时只是停住 *)
      END_IF;
    RETURNING:
      IF go AND B_PressUp THEN state := UNCLAMPING; END_IF;
    UNCLAMPING:
      IF go AND B_Unclamped THEN state := IDLE; END_IF;
  END_CASE;

  jog := NOT auto AND (state = IDLE OR state = INIT);

  Y_Clamp     := state = CLAMPING OR state = PRESSING OR state = RETURNING OR (jog AND S_JogClamp);
  Y_PressDown := ((state = PRESSING AND S_Hand1 AND S_Hand2) OR (jog AND S_JogDown AND B_Clamped)) AND S_LC AND S_EStop;
  Y_PressUp   := (state = RETURNING OR (state = HOMING AND NOT B_PressUp) OR (jog AND S_JogUp))
                 AND S_EStop AND NOT Y_PressDown;
  H_OK  := resOk;
  H_NOK := resNok;
  H_Ready := state = IDLE;
END_PROGRAM
