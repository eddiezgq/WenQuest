(* 程序 15.3.1  压装工位的状态机：只有自动循环（方式与异常处理在 15.4、15.5 节加上） *)
TYPE E_Press : (IDLE, CLAMPING, PRESSING, RETURNING, UNCLAMPING); END_TYPE

PROGRAM Main
  VAR
    state : E_Press := IDLE;   (* 当前状态 *)
    tTwoHand : TON;            (* 双手按钮须在 0.5 s 内先后按下 *)
    force : REAL;              (* 压装力，kN *)
    peak : REAL;               (* 本件的最大压装力，kN *)
    resOk, resNok : BOOL;      (* 本件结果：合格 / 不合格 *)
  END_VAR

  force := INT_TO_REAL(AI_Force) * 10.0 / 27648.0;
  tTwoHand(IN := S_Hand1 OR S_Hand2, PT := T#500ms);

  (* 1. 转移：每个状态只看“离开这个状态”的条件 *)
  CASE state OF
    IDLE:
      IF B_Part AND B_PressUp AND B_Unclamped AND S_LC AND S_EStop
         AND S_Hand1 AND S_Hand2 AND NOT tTwoHand.Q THEN
        resOk := FALSE; resNok := FALSE; peak := 0.0;
        state := CLAMPING;
      END_IF;
    CLAMPING:
      IF B_Clamped THEN state := PRESSING; END_IF;
    PRESSING:
      peak := MAX(peak, force);
      IF B_PressDown THEN                          (* 压到底：按最大压装力判定 *)
        resOk := peak >= 4.0 AND peak <= 7.0; resNok := NOT resOk;
        state := RETURNING;
      ELSIF force > 8.0 THEN                       (* 过载：中止，判不合格 *)
        resNok := TRUE; state := RETURNING;
      ELSIF NOT (S_Hand1 AND S_Hand2 AND S_LC) THEN (* 松手或挡光：中止 *)
        resNok := TRUE; state := RETURNING;
      END_IF;
    RETURNING:
      IF B_PressUp THEN state := UNCLAMPING; END_IF;
    UNCLAMPING:
      IF B_Unclamped THEN state := IDLE; END_IF;
  END_CASE;

  (* 2. 输出：只由状态决定，每个输出只写一次 *)
  Y_Clamp     := state = CLAMPING OR state = PRESSING OR state = RETURNING;
  Y_PressDown := state = PRESSING AND S_Hand1 AND S_Hand2 AND S_LC;
  Y_PressUp   := state = RETURNING AND NOT Y_PressDown;   (* 软件联锁：两个线圈不同时得电 *)
  H_OK  := resOk;
  H_NOK := resNok;
  H_Ready := state = IDLE AND B_PressUp AND B_Unclamped;
END_PROGRAM
